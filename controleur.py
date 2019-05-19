"""
Module gerant la logique du jeu.
"""
from modele import *
from vue import *
import random


class GestionnaireTouches(object):  # On herite d'"object" pour avoir une classe de nouveau style.
    """
    Classe permettant de gerer les evenements de pression des touches.

    Contrairement a "pygame.key.get_pressed()", elle permet de savoir dans quel ordre les differentes touches ont ete
    pressees.

    La methode "pygame.key.get_pressed()" renvoie une liste de booleens indiquant pour chaque touche possible si elle
    est pressee. Pour ordonner les touches pressees dans l'ordre de pressage il est plus simple de conserver une liste
    des indexes des touches pressees, ce qui est a l'origine des differentes conversions presentes dans les methode de
    cette classe.
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


class Jeu(object):
    """
    Classe gerant l'ensemble du jeu.
    """
    TEMPS_MAX = 120
    VIES_MAX = 3

    def __init__(self):
        pygame.init()
        self.interface = InterfaceGraphique(ECRAN)
        self.niveau = Niveau.niveau(1)

        pygame.key.set_repeat(1, 1)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.minuteur = Minuteur(0.15, 0.01)

        self.doit_recommencer_partie = False
        self.doit_recommencer_niveau = False
        self.vies = self.VIES_MAX
        self.carte = None
        self.mode = MODE.JEU
        self.recommencer_partie()

    @property
    def personnage(self):
        return self.carte.personnage

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

    def menu(self):
        retour = self.interface.menu()
        ret = raw_input("\t\tMenu\n\t1. recommencer partie\n\t2.quitter\n\t3.editeur niveaux.\n>>>")  # TODO : vraie interface
        ret = int(ret)
        if ret == 1:
            self.doit_recommencer_partie = True
        elif ret == 2:
            self.quitter()
        elif ret == 3:
            self.editeur_niveau()

    def recommencer_niveau(self):
        rect = self.interface.rect_carte(self.niveau)
        self.carte = Carte(rect, self.niveau)
        self.minuteur.reinitialiser()
        self.doit_recommencer_niveau = False
        print("vies restantes : {0}".format(self.vies))

    def recommencer_partie(self, niveau=None):
        if niveau is not None:
            self.niveau = niveau
        self.vies = self.VIES_MAX
        self.recommencer_niveau()
        self.doit_recommencer_partie = False

    def sur_perdu(self):
        ret = raw_input("recommencer? ")
        if ret.lower() == "o":
            self.recommencer_partie()
        else:
            self.menu()

    def verifier_perdu(self):
        if self.personnage.est_mort or self.minuteur.temps_ecoule() > self.TEMPS_MAX:
            self.vies -= 1
            if self.vies <= 0:
                self.sur_perdu()
            else:
                self.doit_recommencer_niveau = True

    def niveau_suivant(self):
        i = self.niveau.numero
        if i is not None:
            if i < len(NIVEAUX):
                self.niveau = Niveau.niveau(i + 1)
                self.doit_recommencer_partie = True
                return True
        return False

    def felicitations(self):
        print("Felicitations, vous avez termine tous les niveaux.")  # TODO : remplacer par texte dans pygame

    def gagne(self):
        if not self.niveau_suivant():
            self.felicitations()

    def boucle(self):
        """
        Fait fonctionner le jeu jusqu'a la fermeture du programme.

        :return: "None"
        """
        self.interface.afficher(self.carte)
        self.minuteur.reinitialiser()
        while 1:
            self.minuteur.passage()
            debut = time.time()
            while self.minuteur.tics_restants() > 1:    # Verifie les evenements a intervalles regulier pour eviter de
                                                        # rater des evenements
                self.gerer_evenements()

                if self.minuteur.tics_restants() > 1:  # S'il reste de quoi attendre un tic
                    self.minuteur.attendre_un_tic()
            self.effectuer_mouvements()

            self.verifier_perdu()
            self.carte.activer_sortie()

            if self.doit_recommencer_niveau:
                self.recommencer_niveau()
            if self.doit_recommencer_partie:
                self.recommencer_partie()
            else:
                self.minuteur.attendre_fin()

            self.interface.afficher(self.carte)

            print(time.time() - debut)

    def carte_vide(self, largeur, hauteur):
        derniere_ligne = "#" * largeur
        premiere_ligne = derniere_ligne + "\n"
        ligne_millieu = "#" + "~" * (largeur - 2) + "#\n"
        niveau_ascii = premiere_ligne + ligne_millieu * (hauteur - 2) + derniere_ligne
        niveau = Niveau(niveau_ascii)
        decalage = None
        if self.mode == MODE.EDITEUR:
            decalage = (self.carte.largeur_case + self.interface.marge, 0)
        rect = self.interface.rect_carte(niveau, decalage)
        return Carte(rect, niveau)

    def blocs_selectionnables(self, x, y, largeur, hauteur):
        blocs_selectionnables = [Terre, Mur, Caillou, Diamant, Personnage, Sortie]
        for i, bloc in enumerate(blocs_selectionnables):
            rect = pygame.Rect(x, y + i * hauteur, largeur, hauteur)
            blocs_selectionnables[i] = bloc(rect)
        return blocs_selectionnables

    def objet_survole(self, pos, *objets):
        return self.interface.objet_survole(pos, *objets)

    def selectionner(self, bloc):
        self.interface.selectionner(bloc)

    def editeur_niveau(self):
        self.mode = MODE.EDITEUR
        carte = self.carte_vide(34, 20)
        x = 0
        y = 0
        # Les blocs selectionnables sont les blocs sur lesquels on peut cliquer pour choisir le type de blocs a ajouter
        # sur la carte
        blocs_selectionnables = self.blocs_selectionnables(x, y, carte.largeur_case, carte.hauteur_case)
        bloc_selectionne = blocs_selectionnables[0]
        position_souris = pygame.mouse.get_pos()
        bloc_pointeur = bloc_selectionne.__class__(pygame.Rect(position_souris, bloc_selectionne.rect.size))
        clic_gauche = clic_droit = False
        case = self.objet_survole(position_souris, *carte.tuple_cases)
        del x, y

        # Affichage premiere image
        if case is not None and not clic_droit:  # Si la souris survole la carte et qu'il n'y a pas de clic droit
            bloc_pointeur.rect = case.rect
            # On affiche la carte et le bloc sous le pointeur
            self.interface.afficher(carte, bloc_pointeur)
        else:
            self.interface.afficher(carte)

        minuteur = Minuteur(1/60.0, 0.005)
        while self.mode == MODE.EDITEUR:
            minuteur.passage()
            while minuteur.tics_restants() > 1:
                evenements = pygame.event.get()
                self.gerer_evenements_fenetre(evenements)
                for evenement in evenements:
                    if evenement.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                        boutons_presses = pygame.mouse.get_pressed()
                        clic_gauche = boutons_presses[CLIC.GAUCHE] and not boutons_presses[CLIC.DROIT]
                        clic_droit = boutons_presses[CLIC.DROIT] and not boutons_presses[CLIC.GAUCHE]

                        position_souris = pygame.mouse.get_pos()
                        # On regarde quelle case est survolee par la souris
                        case = self.objet_survole(position_souris, *carte.tuple_cases)
                        if clic_gauche or clic_droit:
                            if clic_gauche:
                                if case is None:  # Pas de case cliquee sur la carte
                                    # On regarde si un bloc selectionnable a ete clique
                                    bloc_clique = self.objet_survole(position_souris, *blocs_selectionnables)
                                    if bloc_clique is not None:  # Si bloc clique
                                        bloc_selectionne = bloc_clique
                                        # On change le bloc affiche sous le pointeur de la souris
                                        taille_bloc = bloc_selectionne.rect.size
                                        rect = pygame.Rect(position_souris, taille_bloc)
                                        creer_bloc = bloc_selectionne.__class__
                                        bloc_pointeur = creer_bloc(rect)
                                else:  # Si une case de la carte a ete cliquee
                                    # Si le nouveau bloc est d'un autre type que l'ancien ou que la case contient
                                    # plusieurs blocs
                                    if bloc_selectionne.__class__ != case.blocs[0].__class__ or len(case.blocs) != 1:
                                        rect = case.rect
                                        creer_bloc = bloc_selectionne.__class__
                                        case.blocs = [creer_bloc(rect)]  # On construit un bloc du bon type
                            elif clic_droit:
                                if case is not None:  # Si une case de la carte a recu un clic droit
                                    case.blocs = [None]  # On supprime les blocs de la case
                            carte.actualiser_blocs()
                        if minuteur.tics_restants() > 1:
                            minuteur.attendre_un_tic()
            objets_a_afficher = list(blocs_selectionnables)
            if case is not None and not clic_droit:  # Si la souris survole la carte et qu'il n'y a pas de clic droit
                bloc_pointeur.rect = case.rect
                objets_a_afficher.append(bloc_pointeur)
            self.interface.afficher(carte, *objets_a_afficher)
            minuteur.attendre_fin()
        self.niveau = Niveau.depuis_carte(carte)
        self.doit_recommencer_partie = True

    def gerer_evenements_fenetre(self, evenements):
        for evenement in evenements:
            if evenement.type == QUIT:
                self.quitter()
            if evenement.type == KEYUP:
                if evenement.key == K_q:
                    self.quitter()
                elif evenement.key == K_m:
                    self.menu()
                elif evenement.key == K_ESCAPE:
                    mods = pygame.key.get_mods()

                    # On regarde si la touche Maj est pressee et qu'aucun autre modificateur ne l'est, on utilise pour
                    # ce faire des operateurs bit a bit
                    if not mods & (KMOD_ALT | KMOD_CTRL):
                        if mods & KMOD_SHIFT:
                            self.interface.passer_en_plein_ecran()
                        else:
                            self.interface.passer_en_fenetre()
                elif evenement.key == K_F12:
                    if self.mode == MODE.JEU:
                        self.editeur_niveau()
                    else:
                        self.mode = MODE.JEU

    def gerer_evenements(self):
        """
        Regarde les evenements et effectue les actions associees a chacun d'entre eux.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        self.gerer_evenements_fenetre(pygame.event.get())
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
        for case in self.carte.tuple_cases:
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
        v = vecteur(directions, self.carte.largeur_case, self.carte.hauteur_case)
        rect = bloc.rect_hashable.move(v)
        try:
            blocs_collisionnes = self.carte.cases[rect].blocs
        except KeyError:  # bloc pas dans la carte
            blocs_collisionnes = [False]
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
        elif isinstance(bloc_collisionne, Sortie):
            if bloc_collisionne.est_activee:
                reussite = True
                if isinstance(bloc_collisionne, Sortie):
                    self.gagne()
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
                    bloc_collisionne.a_tue = True
                    SONS.TUER.play()
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

            if bloc_collisionne is not False:  # Si le bloc n'est pas hors de la carte
                if bloc_collisionne is None:
                    reussite = True
                else:
                    if isinstance(bloc, Personnage):
                        reussite = self._collision_personnage(bloc, bloc_collisionne, direction, essai)
                        bloc.a_collisione = True
                    elif isinstance(bloc, BlocTombant):
                        reussite = self._collision_bloc_tombant(bloc, bloc_collisionne, direction)
                        bloc.a_collisione = True
                if not essai:
                    if reussite:
                        nouveau_rect = bloc.rect.move(vecteur(direction, self.carte.largeur_case, self.carte.hauteur_case))
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
            if isinstance(bloc_collisionne, (BlocTombant, Mur, Sortie)):
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
                    blocs = self.carte.case_a(x, y).blocs
                    for bloc in blocs:
                        if isinstance(bloc, BlocTombant):
                            essai = True
                            if bloc.tombe or bloc.coups_avant_tomber == 0:
                                essai = False
                            faire_tomber(bloc, essai)

        # self.bouger_personnage()

        self.terminer_mouvements()  # TODO: regler l'ordre de resolution des mouvements
