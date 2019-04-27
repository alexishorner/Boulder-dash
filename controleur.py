"""
Module gerant la logique du jeu.
"""
from modele import *
import time
import math
# import ctypes

# ctypes.windll.user32.SetProcessDPIAware()
# vraie_resolution = (ctypes.windll.user32.GetSystemMetrics(0),ctypes.windll.user32.GetSystemMetrics(1))
# info = pygame.display.Info()
# vraie_resolution = (info.current_w, info.current_h)


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
        self.ecran = pygame.display.set_mode((ECRAN.LARGEUR, ECRAN.HAUTEUR), RESIZABLE)  # TODO : permettre le mode plein ecran
        self.arriere_plan = pygame.Surface((ECRAN.LARGEUR, ECRAN.HAUTEUR))
        self.arriere_plan.fill((0, 0, 0))
        self.carte = Carte(Niveau.niveau(1))
        self.personnage = self.carte.personnage

        pygame.key.set_repeat(1, 1)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.minuteur = Minuteur(0.2, 0.01)
        self.mouvement_en_cours = None

    @property
    def mouvement_detecte(self):
        """
        Determine si un mouvement a ete detecte.

        :return: booleen indiquant si un mouvement a ete detecte
        """
        return self.mouvement_en_cours is not None

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
            self.effectuer_mouvement()
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
                    self.mouvement_en_cours = ORIENTATIONS.HAUT
                elif derniere_touche_pressee in TOUCHES.BAS:
                    self.mouvement_en_cours = ORIENTATIONS.BAS
                elif derniere_touche_pressee in TOUCHES.GAUCHE:
                    self.mouvement_en_cours = ORIENTATIONS.GAUCHE
                elif derniere_touche_pressee in TOUCHES.DROITE:
                    self.mouvement_en_cours = ORIENTATIONS.DROITE

    def effectuer_mouvement(self):
        """
        Fait bouger les differents blocs.

        :return: "None"
        """
        if self.mouvement_detecte:  # Si un mouvement doit etre effectue
            self.personnage.bouger(self.mouvement_en_cours)  # On fait avancer le personnage
            self.personnage.etait_en_mouvement = True  # FIXME: Personnage peut pousser cailloux dans vide
            self.mouvement_en_cours = None
        else:
            self.personnage.etait_en_mouvement = False
            self.personnage.caillou_pousse = None

        for x in range(self.carte.nombre_cases_largeur - 1, -1, -1):
            for y in range(self.carte.nombre_cases_hauteur - 1, -1, -1):
                rect = rectangle_a(x, y)
                blocs = self.carte.cases[rect]
                if len(blocs) == 1:
                    pass
                elif len(blocs) == 2:
                    pass
                else:
                    raise RuntimeError("Il n'est pas cense y avoir plus de deux blocs a la meme position.")

        # blocs_a_traiter = self.carte.blocs
        # continuer = True
        # while continuer:
        #     continuer = False
        #     for bloc in blocs_a_traiter:
        #         bloc.actualiser(self.carte.cases)  # On gere les collisions entre les blocs
        #         if bloc.a_deja_bouge:
        #             blocs_a_traiter.remove(bloc)
        #             continuer = True

        for bloc in self.carte.blocs:
            bloc.terminer_cycle()
