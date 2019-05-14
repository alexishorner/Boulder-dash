"""
Module gerant la logique du jeu.
"""
from modele import *
import time
import math
import random


def modulo(num, div):
    """
    Fonction permettant de calculer le reste de la division de deux nombres sans avoir d'erreur due a l'arrondi des ordinateurs.

    Cette fonction donne le meme resultat que l'operateur "%" pour les nombres entiers, mais donne des resultats
    correspondants a la definition de modulo pour tous les nombres, y compris les nombres a virgule et les nombres negatifs.

    Exemple :
    7.5 % 0.05 donne 0.04999999999999992 (incorrect), alors que modulo(7.5, 0.05) donne 0.0 (correct)

    Verification:
    7.5 = 150.0 * 0.05 + 0.0

    Le desavantage de cette fonction est qu'elle perd un peu de precision pour parer aux erreurs d'arrondi.

    :param num: numerateur
    :param div: diviseur
    :return: reste de la division de "num" par "div"
    """
    a = float(num)  # Assure que la division sera flottante
    b = float(div)
    facteur = int(1e14)  # Facteur de precision
    return (a / b - int(math.ceil(a / b * facteur) / facteur)) * b


def vecteur(directions):
    try:
        len(directions)  # On verifie si "directions" est iterable
        directions_ = directions
    except TypeError:
        directions_ = [directions]  # S'il n'y a qu'une seule direction on la transforme en liste
    v = array([0, 0])  # On commence avec un vecteur nul
    for direction in directions_:  # On ajoute le vecteur correspondant a chaque direction
        if direction == ORIENTATIONS.DROITE:
            v += array([1, 0])
        elif direction == ORIENTATIONS.GAUCHE:
            v += array([-1, 0])
        elif direction == ORIENTATIONS.HAUT:
            v += array([0, -1])
        elif direction == ORIENTATIONS.BAS:
            v += array([0, 1])
        else:
            raise ValueError("La direction est invalide")
    v *= DIMENSIONS.LARGEUR_CASE  # On multiplie par la largeur d'une case pour avoir la bonne norme
    return v


class Action(object):
    def __init__(self, fonction=None, *args, **kwargs):
        self.reinitialiser()
        if fonction is not None:
            self.fonction = fonction
        self.args = args
        self.kwargs = kwargs

    def effectuer(self):
        return self.fonction(*self.args, **self.kwargs)

    def reinitialiser(self):
        self.fonction = lambda *_: None
        self.args = tuple()
        self.kwargs = dict()


class GestionnaireTouches(object):  # On herite d'"object" pour avoir une classe de nouveau style.
    """
    Classe permettant de gerer les evenements de pression des touches.

    Dans pygame, si nous voulons savoir les touches pressees il faut appeler "pygame.key.get_pressed()", cette methode
    renvoie une liste de booleens indiquant pour chaque touche possible si elle est pressee. Pour ordonner les touches
    pressees dans l'ordre de pressage il est plus simple de conserver une liste des indexes des touches pressees, ce qui
    est a l'origine des differentes conversions presentes dans les methode de cette classe.
    """
    def __init__(self, touches_pressees_booleens=None):
        if touches_pressees_booleens is None:
            touches_pressees_indexes = []
        else:
            touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)
        self.indexes_ordonnes = touches_pressees_indexes  # indexes des touches dans leur ordre de pressage

    def actualiser_touches(self, touches_pressees_booleens):
        """
        Ajoute les nouvelles touches pressees et enleve les touches non pressees.

        :param touches_pressees_booleens: liste de booleens indiquant pour chaque touche si elle est pressee
        :return: "None"
        """
        ajoutees, enlevees = self.changements_touches(touches_pressees_booleens)  # Regarde les touches nouvellement
                                                                        # pressees et les touches n'etant plus pressees
        for touche in enlevees:
            self.indexes_ordonnes.remove(touche)
        self.indexes_ordonnes.extend(ajoutees)  # Ajoute a la fin de la liste les touches nouvellement pressees

    def changements_touches(self, touches_pressees_booleens):
        """
        Detecte les changement dans les touches pressees par rapport a l'etat d'avant.

        :param touches_pressees_booleens: touches pressees dans l'etat actuel
        :return: instances de "list", l'une contenant les touches ajoutees, l'autre les touches enlevees
        """
        touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)    # Recupere l'index des
                                                                                            # touches pressees
        ajoutees = [touche for touche in touches_pressees_indexes if touche not in self.indexes_ordonnes]
        enlevees = [touche for touche in self.indexes_ordonnes if touche not in touches_pressees_indexes]
        return ajoutees, enlevees

    def derniere_touche(self):
        """
        Retourne la derniere touche pressee.

        :return: derniere touche pressee
        """
        if len(self.indexes_ordonnes) > 0:
            return self.indexes_ordonnes[-1]
        else:
            return None

    @staticmethod
    def booleens_vers_indexes(booleens):
        """
        Retourne les indexes des touches pressees a partir d'une liste de booleens.

        :param booleens: liste de booleens determinant pour chaque touche si elle est pressee
        :return: liste contenant l'index de chaque touche pressee
        """
        return [index for index, booleen in enumerate(booleens) if booleen]

    @staticmethod
    def indexes_vers_booleens(indexes):
        """
        Retourne une liste de booleens determinant pour chaque touche si elle est pressee a partir de l'index de chaque
        touche pressee.

        :param indexes: liste contenant l'index de chaque touche pressee
        :return: liste de booleens determinant pour chaque touche si elle est pressee
        """
        booleens = [False] * GestionnaireTouches.nombre_de_touches()
        for index in indexes:
            booleens[index] = True
        return booleens

    @staticmethod
    def nombre_de_touches():
        """
        Retourne le nombre total de touches.

        :return: nombre total de touches
        """
        return len(pygame.key.get_pressed())


class Minuteur(object):  # Ici le fait d'avoir une classe de nouveau style a une vraie utilite, puisque cela permet d'utiliser des proprietes
    """
    Classe permettant de simuler un minuteur. Le minuteur se remet a zero a intervalles fixes dont la duree est
    determinee par "self._periode". La remise a zero est une illusion externe qui n'a jamais rellement lieu en interne ;
    au lieu de cela le temps ecoule est reduit modulo "self._periode".
    """
    def __init__(self, periode, tic):
        """
        Constructeur de la classe "Minuteur".

        :param periode: duree entre chaque remise a zero du minuteur
        :param tic: plus petite unite de temps du minuteur
        """
        self._periode = periode
        self.tic = tic
        self.debut = time.time()
        self.numero_periode = None

    @property
    def periode(self):
        return self._periode

    @periode.setter
    def periode(self, nouvelle):
        self._periode = nouvelle
        self.reinitialiser()

    @periode.deleter
    def periode(self):
        raise AttributeError("La classe \"{0}\" ne peut pas fonctionner "
                             "sans l'attribut \"_periode\"".format(self.__class__.__name__))

    def temps_ecoule(self):
        """
        Retourne le temps ecoule depuis la derniere reinitialisation du minuteur.

        :return: temps ecoule
        """
        return time.time() - self.debut

    def temps_ecoule_periode_actuelle(self):
        """
        Retourne le temps ecoule depuis la derniere fin de periode.

        :return: nombre representant le temps ecoule depuis la derniere fin de periode
        """
        ecoule = self.temps_ecoule()
        return modulo(ecoule, self.periode)

    def reinitialiser(self):
        """
        Remet le minuteur a zero.

        :return: "None"
        """
        self.debut = time.time()
        self.numero_periode = None

    def passage(self):
        """
        Methode appelee a chaque fin de boucle des evenements pour indiquer au minuteur qu'il peut commencer une
        nouvelle periode.

        :return: "None"
        """
        est_premier_tour = self.numero_periode is None
        if est_premier_tour or self.numero_periode != self.nombre_periodes_ecoulees():
            self.numero_periode = self.nombre_periodes_ecoulees()   # On actualise le numero de la periode en fonction
                                                                    # du temps ecoule
        else:  # Si la periode n'est tout juste pas finie (a cause de l'imprecision de la fonction "time.sleep")
            self.numero_periode += 1  # On augmente quand meme le numero de la periode, car elle est censee etre finie

    def nombre_periodes_ecoulees(self):
        """
        Determine le nombre de fois qu'une periode s'est ecoulee.

        :return: numero de la periode actuelle
        """
        return int(self.temps_ecoule() / self.periode)

    def attendre_un_tic(self):
        """
        Attends le temps d'un tic.

        :return: "None"
        """
        time.sleep(self.tic)

    def attendre_fin(self):
        """
        Attend jusqu'a la fin de la periode specifiee, "None" attend jusqu'a la fin de la periode actuelle.

        :return: "None"
        """
        nombre_periodes_ecoulees = self.nombre_periodes_ecoulees()  # On stocke le nombre de periode ecoulees, car il
                                                                    # varie en fonction du temps
        if self.numero_periode is None:  # Si on est au premier tour apres la reinitialisation
            ecart = 0
        elif self.numero_periode >= nombre_periodes_ecoulees:   # Dans l'eventualite ou le numero de la periode est
                                                                # superieur au nombre de periodes ecoulees (peut arriver
                                                                # si la methode "self.passage" appelee deux fois de
                                                                # suite sans attendre)
            ecart = self.numero_periode - nombre_periodes_ecoulees
        else:
            return
        temps = ecart * self.periode + (self.periode - self.temps_ecoule_periode_actuelle())
        time.sleep(temps)  # On attend la fin de la periode numero "self.numero_periode"

    def tics_restants(self):
        """
        Retourne le nombre de tics restants avant la fin de la periode.

        :return: nombre de tics restant avant la fin de la periode
        """
        if self.numero_periode is None:
            ecart = 0
        else:
            ecart = self.numero_periode - self.nombre_periodes_ecoulees()
        if ecart >= 0:
            return (ecart * self.periode + self.periode - self.temps_ecoule_periode_actuelle()) / self.tic
        else:
            return 0


class Jeu(object):
    """
    Classe gerant l'ensemble du jeu.
    """
    def __init__(self):
        pygame.init()
        self.ecran = ECRAN
        self.arriere_plan = pygame.Surface(RESOLUTION)
        self.arriere_plan.fill((0, 0, 0))
        self.carte = Carte(Niveau.niveau(1))
        self.personnage = self.carte.personnage

        pygame.key.set_repeat(1, 1)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.minuteur = Minuteur(0.15, 0.01)

    @property
    def mouvement_detecte(self):
        """
        Determine si un mouvement a ete detecte.

        :return: booleen indiquant si un mouvement a ete detecte
        """
        return self.personnage.mouvement_en_cours is not None

    @mouvement_detecte.setter
    def mouvement_detecte(self, nouveau):
        raise AttributeError("La propriete ne peut pas etre modifiee.")

    @mouvement_detecte.deleter
    def mouvement_detecte(self):
        raise AttributeError("La propriete ne peut pas etre supprimee.")

    def quitter(self):
        """
        Quitte le jeu apres confirmation de l'utilisateur.

        :return: "None"
        """
        exit()  # TODO : ajouter confirmation

    def commencer(self):
        """
        Commence le jeu et continue jusqu'a l'arret du programme

        :return: "None"
        """
        self.actualiser_ecran()
        self.minuteur.reinitialiser()
        while 1:  # FIXME : quand la fenetre est bougee le code est mis en pause
            self.minuteur.passage()
            debut = time.time()
            while self.minuteur.tics_restants() > 1:    # Verifie les evenements a intervalles regulier pour eviter de
                                                        # rater des evenements
                self.gerer_evenements()  # Gere les evenements autres que les mouvements

                if self.minuteur.tics_restants() > 1:  # S'il reste de quoi attendre un tic
                    self.minuteur.attendre_un_tic()
            self.effectuer_mouvements()
            if self.carte.nombre_diamants == self.personnage.diamants_ramasses:
                self.carte.sortie.activer()
            self.actualiser_ecran()

            if self.minuteur.tics_restants() > 0:  # Si la periode n'est pas finie
                self.minuteur.attendre_fin()

            print(time.time() - debut)

    def actualiser_ecran(self):
        """
        Actualise l'ecran.

        :return: "None"
        """
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan
        self.carte.dessiner(self.ecran)  # Dessine les blocs
        pygame.display.flip()  # Actualise l'ecran

    def gerer_evenements(self):
        """
        Regarde les evenements et effectue les actions associees a chacun d'entre eux.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        for evenement in pygame.event.get():
            if evenement.type == QUIT:
                self.quitter()
        self.gerer_mouvement()  # Pas besoin de verifier un KEYDOWN grace au gestionnaire de touches
                                # KEYDOWN n'est parfois pas present alors qu'il devrait

    def gerer_mouvement(self):
        """
        S'occuppe des evenements correspondants a l'appui sur une touche.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        self.gestionnaire_touches.actualiser_touches(pygame.key.get_pressed())

        # On regarde si plus de la moitie de la periode est ecoulee (sert a ameliorer l'experience utilisateur)
        moitie_periode_est_depassee = self.minuteur.temps_ecoule_periode_actuelle() > self.minuteur.periode / 2.0

        if not self.personnage.etait_en_mouvement or moitie_periode_est_depassee:   # Si le personnage est deja en train
                                                                                    # de bouger ou que plus de la moitie
                                                                                    # de la periode est ecoulee
            derniere_touche_pressee = self.gestionnaire_touches.derniere_touche()
            if derniere_touche_pressee in TOUCHES.MOUVEMENT:  # Si on presse une touche de mouvement

                # On regarde quelle touche est pressee et on stocke le mouvement en consequence
                if derniere_touche_pressee in TOUCHES.HAUT:
                    self.personnage.mouvement_en_cours = ORIENTATIONS.HAUT
                elif derniere_touche_pressee in TOUCHES.BAS:
                    self.personnage.mouvement_en_cours = ORIENTATIONS.BAS
                elif derniere_touche_pressee in TOUCHES.GAUCHE:
                    self.personnage.mouvement_en_cours = ORIENTATIONS.GAUCHE
                elif derniere_touche_pressee in TOUCHES.DROITE:
                    self.personnage.mouvement_en_cours = ORIENTATIONS.DROITE

    def gerer_collisions(self):
        for case in self.carte.cases.itervalues():
            if len(case.blocs) == 2:
                for bloc in case.blocs:
                    if isinstance(bloc, BlocTombant):
                        if self.personnage in case.blocs:
                            self.personnage.tuer()
                        else:
                            raise RuntimeError("Seul le personnage peut etre sur la meme case qu'un autre bloc.")

    def terminer_mouvements(self):
        self.carte.supprimer_morts()
        self.gerer_collisions()
        self.carte.supprimer_morts()  # On supprime les morts lors de la collision
        for bloc in self.carte.blocs_tries:
            bloc.terminer_cycle()

    def bloc_collisionne(self, bloc, directions=tuple()):
        v = vecteur(directions)
        rect = bloc.rect_hashable.move(v)
        blocs_collisionnes = self.carte.cases[rect].blocs
        if len(blocs_collisionnes) == 1:
            bloc_collisionne = blocs_collisionnes[0]
        else:  # len == 2
            bloc_collisionne = None
            for b in blocs_collisionnes:
                if b is not self.personnage:  # On renvoie que la porte et pas le personnage, car la porte protege le personnage
                    bloc_collisionne = b  # Porte
        return bloc_collisionne

    def _collision_personnage_caillou(self, personnage, caillou, direction, essai=False):
        reussite = False
        actions = []
        if direction in (ORIENTATIONS.GAUCHE, ORIENTATIONS.DROITE):
            if caillou.coups_avant_etre_pousse == 0:
                reussite = self.faire_tomber_droit(caillou)
                if reussite:
                    actions.append(Action(personnage.bouger, direction))
                else:
                    reussite = self.faire_bouger(caillou, direction, essai)[0]  # On pousse le caillou
                    actions.append(Action(personnage.pousser, caillou, direction))
            elif self.peut_bouger(caillou, direction):
                actions.append(Action(personnage.pousser, caillou, direction))
            else:
                actions.append(Action(personnage.bouger, direction))
        return reussite, actions

    def _collision_personnage_diamant(self, personnage, diamant, direction, essai=False):
        reussite = False
        actions = []
        if direction in (ORIENTATIONS.GAUCHE, ORIENTATIONS.DROITE) or not diamant.tombe:
            if not essai:
                actions.append(Action(personnage.ramasser_diamant, diamant))
            reussite = True
        return reussite, actions

    def _collision_personnage(self, personnage, bloc_collisionne, direction, essai=False):  # ATTENTION: methode faite pour etre utilisee dans "faire_bouger" uniquement
        actions = []
        reussite = False
        if isinstance(bloc_collisionne, Caillou):
            reussite, actions = self._collision_personnage_caillou(personnage, bloc_collisionne, direction, essai)
        elif isinstance(bloc_collisionne, Diamant):
            reussite, actions = self._collision_personnage_diamant(personnage, bloc_collisionne, direction, essai)
        elif isinstance(bloc_collisionne, Terre):
            actions.append(Action(personnage.creuser_terre, bloc_collisionne))
            reussite = True
        elif isinstance(bloc_collisionne, Porte):
            reussite = True
        if not essai:
            for action in actions:
                action.effectuer()
        return reussite

    def _collision_bloc_tombant(self, bloc, bloc_collisionne, direction):  # ATTENTION: methode faite pour etre utilisee dans "faire_bouger" uniquement
        reussite = False
        if isinstance(bloc_collisionne, Personnage):
            if bloc.tombe and direction == ORIENTATIONS.BAS:
                reussite = True
                if ORIENTATIONS.sont_opposees(direction, self.personnage.mouvement_en_cours):
                    self.personnage.tuer()
        return reussite

    def peut_bouger(self, bloc, direction):
        reussite = self.faire_bouger(bloc, direction, essai=True)[0]
        return reussite

    def faire_bouger(self, bloc, direction, essai=False):
        if bloc.a_deja_bouge:
            return False, None
        reussite = False
        bloc_collisionne = None
        if bloc.PEUT_SE_DEPLACER:
            bloc_collisionne = self.bloc_collisionne(bloc, direction)

            if bloc_collisionne is None:
                reussite = True
            else:
                if isinstance(bloc, Personnage):
                    reussite = self._collision_personnage(bloc, bloc_collisionne, direction, essai)
                elif isinstance(bloc, BlocTombant):
                    reussite = self._collision_bloc_tombant(bloc, bloc_collisionne, direction)
            if not essai:
                if reussite:
                    nouveau_rect = bloc.rect.move(vecteur(direction))
                    self.carte.bouger(bloc, nouveau_rect)
                    bloc.a_deja_bouge = True
        return reussite, bloc_collisionne  # Le bloc collisionne n'est juste que si reussite == False

    def faire_tomber_droit(self, bloc, essai=False):
        reussite = self.faire_bouger(bloc, ORIENTATIONS.BAS, essai)[0]
        if reussite:
            bloc.tomber()
        return reussite

    def faire_tomber_cotes(self, bloc, essai=False):
        reussite = False
        if not bloc.a_deja_bouge:
            bloc_collisionne = self.bloc_collisionne(bloc, ORIENTATIONS.BAS)
            if isinstance(bloc_collisionne, (BlocTombant, Mur, Porte)):
                    directions = [ORIENTATIONS.GAUCHE, ORIENTATIONS.DROITE]
                    while len(directions) > 0 and not reussite:
                        direction = random.choice(directions)
                        directions.remove(direction)
                        bloc_diagonale = self.bloc_collisionne(bloc, (direction, ORIENTATIONS.BAS))
                        if bloc_diagonale is None:
                            reussite = self.faire_bouger(bloc, direction, essai)[0]
            if reussite:
                bloc.tomber()
        return reussite

    def bouger_personnage(self):
        if self.mouvement_detecte:
            self.faire_bouger(self.personnage, self.personnage.mouvement_en_cours)
            self.personnage.etait_en_mouvement = True
            self.personnage.mouvement_en_cours = None
        else:
            self.personnage.a_deja_bouge = True

    def effectuer_mouvements(self):
        """
        Fait bouger les differents blocs.

        :return: "None"
        """
        # On fait bouger le personnage
        if self.personnage.mouvement_en_cours == ORIENTATIONS.DROITE:
            pass
        if self.mouvement_detecte:  # Si un mouvement doit etre effectue
            pass
            # self.faire_bouger(self.personnage, self.personnage.mouvement_en_cours)  # On fait avancer le personnage
            # self.personnage.etait_en_mouvement = True
            # self.personnage.mouvement_en_cours = None
        else:
            self.personnage.etait_en_mouvement = False
            self.personnage.caillou_pousse = None

        if self.personnage.etait_en_mouvement:
            pass

        self.bouger_personnage()

        # On fait d'abord tomber les blocs tout droit et ensuite de cote
        methodes_tomber = (self.faire_tomber_droit, self.faire_tomber_cotes)
        for faire_tomber in methodes_tomber:
            for y in range(self.carte.nombre_cases_hauteur - 1, -1, -1):
                for x in range(self.carte.nombre_cases_largeur - 1, -1, -1):  # On parcourt les blocs de droite a gauche et de bas en haut
                    rect = rectangle_a(x, y)
                    blocs = self.carte.cases[rect].blocs
                    for bloc in blocs:
                        if isinstance(bloc, BlocTombant):
                            essai = True
                            if bloc.tombe or bloc.coups_avant_tomber == 0:
                                essai = False
                            faire_tomber(bloc, essai)

        # self.bouger_personnage()

        self.terminer_mouvements()  # TODO: regler l'ordre de resolution des mouvements
