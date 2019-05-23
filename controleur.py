# coding: utf-8
"""
Module gerant la logique du jeu.
"""
from modele import *
from vue import *
import random
from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfilename
from tkSimpleDialog import askinteger
Tk().withdraw()  # On empêche Tk de créer une interface complète


class Jeu(object):
    """
    Classe gerant l'ensemble du jeu.
    """
    VIES_INITIALES = 3

    def __init__(self):
        pygame.init()
        self.interface = InterfaceGraphique(ECRAN)
        self.definir_menu()
        self.niveau = Niveau.niveau(1)
        self.minuteur = Minuteur(0.15, 0.01)

        self.doit_recommencer_niveau = False
        self.doit_recommencer_partie = False
        self.doit_commencer_niveau = False
        self._vies = 0
        self.vies = self.VIES_INITIALES
        self.score_debut_niveau = 0
        self._score = 0
        self.carte = None
        self.carte_editeur = None
        self._ancien_mode = None
        self._mode = MODES.JEU
        self.bouton_dimensions = Bouton((0, 0))
        self.nouvelle_partie()

    @property
    def personnage(self):
        """
        Propriété permettant d'accéder plus facilement au personnage.

        :return: instance de la classe "Personnage" représentant le personnage sur la carte
        """
        return self.carte.personnage

    @property
    def mouvement_detecte(self):
        """
        Determine si un mouvement a ete detecte.

        :return: booleen indiquant si un mouvement a ete detecte
        """
        return self.personnage.mouvement_en_cours is not None

    @property
    def ancien_mode(self):
        """
        Propriété permettant d'acceder à la valeur du mode précédent.
        Le mode décrit quel type de contenu est affiché à l'écran.

        :return: Nombre représentant le mode précédent
        """
        return self._ancien_mode

    @property
    def mode(self):
        """
        Propriété permettant de gérer l'accès au mode, le mode est une valeur de l'énumération "MODES" et sert à décrire
        le type de contenu affiché.

        :return: valeur de l'énumération "MODES" décrivant le mode actuel
        """
        return self._mode

    @mode.setter
    def mode(self, nouveau):
        self._ancien_mode = self._mode
        self._mode = nouveau

    @property
    def vies(self):
        """
        Propriété gérant l'accès au nombre de vies restantes.

        :return: nombre de vies restantes
        """
        return self._vies

    @vies.setter
    def vies(self, nouvelles):
        self._vies = nouvelles
        self.interface.label_vies.texte = u"♥: {0}".format(nouvelles)

    @property
    def score(self):
        """
        Propriété gérant l'accès au score.

        :return: score
        """
        return self._score

    @score.setter
    def score(self, nouveau):
        self._score = nouveau
        self.interface.label_score.texte = "SCORE: {0}".format(nouveau)

    @property
    def temps_restant(self):
        """
        Propriété permettant de savoir le temps restant pour finir le niveau.

        :return: temps restant
        """
        return self.carte.temps_maximal - self.minuteur.temps_ecoule()

    def actualiser_temps(self):
        """
        Fonction permettant de changer la valeur du label affichant le temps restant.

        :return: "None"
        """
        temps = self.temps_restant
        secondes = int(temps)
        if secondes < 10: secondes = "0{0}".format(secondes)
        self.interface.label_temps.texte = "{0}".format(secondes)

    def comptabiliser_score(self):
        """
        comptabilise le score en fonction des diamants
        """
        return self.personnage.diamants_ramasses * 10

    def actualiser_score(self, score):
        """
        Calcule le score.
        """
        nombre_vies_ajoutees = self.score // 500
        self.score = score
        ajout_score_depuis_derniere_vie = self.score - nombre_vies_ajoutees * 500
        vies_a_ajouter = ajout_score_depuis_derniere_vie // 500
        if vies_a_ajouter > 0:
            self.gagner_vies(vies_a_ajouter)

    def gagner_vies(self, vies):
        """
        Ajoute une vie.
        """
        SONS.VIE_BONUS.play()
        self.vies += vies

    def ajouter_temps_score(self):
        """
        Ajoute le temps au score à la fin du niveau

        :return: "None"
        """
        self.actualiser_score(self.score + int(self.temps_restant))

    def afficher_nbdiamants(self):
        """
        Change la valeur du label affichant le nombre total de diamant, le nombre de diamants minimum pour finir le
        niveau et le nombre de diamants ramassés.

        :return: "None"
        """
        nombre_diamants = self.carte.nombre_diamants_max
        nombre_diamants_pour_sortir = self.carte.nombre_diamants_pour_sortir
        diamants_ramasses = self.personnage.diamants_ramasses
        texte = "{0}${1} {2}".format(nombre_diamants, nombre_diamants_pour_sortir, diamants_ramasses)
        self.interface.label_diamants.texte = texte

    def reprendre(self):
        """
        Méthode permettant de revenir au mode précédent après avoir été dans le menu.

        :return: "None"
        """
        self.mode = self.ancien_mode  # TODO pause

    def charger_niveau(self):
        """
        Méthode chargeant un niveau après avoir demandé à l'utilisateur le niveau à charger.

        :return: "None"
        """
        # demande à l'utilisateur un fichier à ouvrir
        nom_fichier = askopenfilename(title="Selectionner un fichier", initialdir="niveaux/personnalises/",
                                      filetypes=[("fichiers JSON", "*.json")])
        if nom_fichier:
            niveau = Niveau.charger(nom_fichier)
            erreurs = Carte(self.carte.rect, niveau).valider()
            if len(erreurs) > 0:
                self.gerer_erreurs(erreurs)
            else:
                self.niveau = niveau
                self.doit_recommencer_partie = True

    def charger_dans_editeur(self):
        """
        Méthode permettant de charger le niveau actuel dans l'éditeur pour pouvoir l'éditer.

        :return: "None"
        """
        if self.ancien_mode == MODES.JEU:
            self.editeur_niveau(self.carte)

    def sauvegarder(self, carte):
        """
        Méthode demandant à l'utilisateur un fichier où sauvegarder le niveau créé dans l'éditeur.

        :param carte: carte de l'éditeur à convertir en niveau et à sauvegarder
        :return: "None"
        """
        erreurs = carte.valider()  # On vérifie si la carte peut être utilisée comme niveau
        if len(erreurs) > 0:
            self.gerer_erreurs(erreurs)
        else:
            nom_fichier = asksaveasfilename(title="Selectionner un fichier", initialdir="niveaux/personnalises/",
                                            filetypes=[("fichiers JSON","*.json")])
            if nom_fichier:
                niveau = Niveau.depuis_carte(carte)
                niveau.sauvegarder(nom_fichier)

    def redimensionner_carte(self, carte):
        """
        Méthode demandant à l'utilisateur les dimensions qu'il désire pour la carte et change la taille de celle-ci.

        :param carte: carte à redimensionner
        :return: "None"
        """
        largeur = askinteger("Largeur", "Entrez la largeur de la carte", minvalue=3, maxvalue=100)
        hauteur = askinteger("Hauteur", "Entrez la hauteur de la carte", minvalue=3, maxvalue=100)
        largeur_ = largeur
        hauteur_ = hauteur
        if largeur is None and hauteur is None:
            return
        if largeur is None:
            largeur_ = carte.nombre_cases_largeur
        if hauteur_ is None:
            hauteur_ = carte.nombre_cases_hauteur
        texte = "{0}:{1}".format(carte.nombre_cases_hauteur, carte.nombre_cases_hauteur)
        self.bouton_dimensions.texte = texte
        decalage = (self.carte.largeur_case + self.interface.marge, 0)
        carte.rect = self.interface.rect_carte(largeur_, hauteur_, decalage)
        carte.changer_taille(largeur_, hauteur_)

    def definir_menu(self):
        """
        Méthode créant tous les éléments du menu.

        :return: "None"
        """
        rect = self.interface.rect()
        h = rect.height
        labels = [Label((rect.centerx, 0.25*h), "Menu", 80)]
        boutons = [Bouton((rect.centerx, labels[0].centre.y + 0.15 * h), Action(self.reprendre),
                          texte="Reprendre"),
                   Bouton((rect.centerx, 0), Action(self.recommencer_niveau), texte="Se suicider"),
                   Bouton((rect.centerx, 0), Action(self.recommencer_partie), texte="Recommencer partie"),
                   Bouton((rect.centerx, 0), Action(self.nouvelle_partie), texte="Nouvelle partie"),
                   Bouton((rect.centerx, 0), Action(self.charger_niveau), texte="Charger niveau"),
                   Bouton((rect.centerx, 0), Action(self.charger_dans_editeur), texte="Modifier dans l'editeur"),
                   Bouton((rect.centerx, 0), Action(self.editeur_niveau), texte="Creer niveau"),
                   Bouton((rect.centerx, 0), Action(self.interface.quitter), texte="Quitter")]
        for i, bouton in enumerate(boutons):
            if i > 0:
                y_prec = boutons[i - 1].centre.y
                bouton.centre = (bouton.centre.x, y_prec + 0.05 * h)
        self.interface.labels_menu = labels
        self.interface.boutons_menu = boutons

    def menu(self):
        """
        Méthode ouvrant le menu et gérant le retour de celui-ci.

        :return: "None"
        """
        self.mode = MODES.MENU
        retour = self.interface.menu()
        self.gerer_retour_interface(retour)

    def commencer_niveau(self):
        """
        Méthode permettant de réinitialiser différentes valeurs avant le commencement d'un niveau. Cette méthode ne
        modifie pas le nombre de vies.

        :return: "None"
        """
        self.mode = MODES.JEU
        self.interface.supprimer_erreurs()
        rect = self.interface.rect_carte(self.niveau.nombre_cases_largeur, self.niveau.nombre_cases_hauteur)
        self.carte = Carte(rect, self.niveau)
        self.minuteur.reinitialiser()
        self.actualiser_score(self.score_debut_niveau)
        self.doit_commencer_niveau = False

    def recommencer_niveau(self):
        """
        Recommence le niveau en enlevant une vie au personnage.

        :return: "None"
        """
        if self.vies > 0:
            self.vies -= 1
        if self.vies <= 0:
            self.sur_perdu()
        else:
            self.commencer_niveau()
        self.doit_recommencer_niveau = False

    def recommencer_partie(self, aller_au_niveau_1=False):
        """
        Méthode permettant de recommencer une partie.

        :param aller_au_niveau_1: booléen déterinant s'il faut revenir au premier niveau ou non.
        :return: "None"
        """
        if self.niveau.numero is not None or aller_au_niveau_1:
            self.niveau = Niveau.niveau(1)
        self.vies = self.VIES_INITIALES
        self.commencer_niveau()
        self.score_debut_niveau = 0
        self.actualiser_score(0)
        self.doit_recommencer_partie = False

    def nouvelle_partie(self):
        """
        Méthode permettant de commencer une nouvelle partie en commençant au premier niveau.

        :return: "None"
        """
        self.recommencer_partie(aller_au_niveau_1=True)

    def sur_perdu(self):
        """
        Méthode appelée lorsque le joueur a perdu.

        :return: "None"
        """
        self.menu()

    def verifier_perdu_niveau(self):
        """
        Méthode vérifiant si le joueur a perdu et gérant les actions à effectuer dans le cas échéant.

        :return: "None"
        """
        if self.personnage.est_mort or self.temps_restant < 0:
            if self.temps_restant<0:
                SONS.TIMEOUT.play()
            self.interface.afficher_jeu(self.carte)
            time.sleep(0.5)
            self.doit_recommencer_niveau = True

    def niveau_suivant(self):
        """
        Méthode permettant de passer au niveau prédéfinit suivant.

        :return: "None"
        """
        i = self.niveau.numero
        if i is not None:
            if i < len(NIVEAUX):
                self.niveau = Niveau.niveau(i + 1)
                self.score_debut_niveau = self.score
                self.doit_commencer_niveau = True
                return True
        return False

    def gagne(self):
        """
        Méthode appelée lorsque le joueur a gagné.

        :return: "None"
        """
        self.ajouter_temps_score()
        SONS.FINI.play()
        self.interface.afficher_jeu(self.carte)
        time.sleep(5)
        if not self.niveau_suivant():
            self.menu()

    def boucle(self):
        """
        Méthode faisant fonctionner le jeu jusqu'a la fermeture du programme.

        :return: "None"
        """
        self.interface.afficher_jeu(self.carte)
        self.minuteur.reinitialiser()
        while 1:
            self.minuteur.passage()
            while self.minuteur.tics_restants() > 1:    # Verifie les evenements a intervalles regulier pour eviter de
                                                        # rater des evenements
                self.gerer_evenements()

                if self.minuteur.tics_restants() > 1:  # S'il reste de quoi attendre un tic
                    self.minuteur.attendre_un_tic()
            self.effectuer_mouvements()

            self.verifier_perdu_niveau()
            self.carte.activer_sortie()

            if self.doit_commencer_niveau:
                self.commencer_niveau()
            if self.doit_recommencer_niveau:
                self.recommencer_niveau()
            if self.doit_recommencer_partie:
                self.recommencer_partie()
            else:
                self.minuteur.attendre_fin()

            self.actualiser_temps()
            self.afficher_nbdiamants()
            self.interface.afficher_jeu(self.carte)

    def carte_vide(self, largeur, hauteur):
        """
        Méthode permettant de créer une carte ne contenant que de la terre et une bordure de mur.

        :param largeur: nombre de cases dans la largeur de la carte
        :param hauteur: nombre de cases dans la longueur de la carte
        :return: instance de "Carte" ayant les dimensions voulues
        """
        niveau = Niveau.vide(largeur, hauteur)
        decalage = None
        if self.mode == MODES.EDITEUR:
            decalage = (self.carte.largeur_case + self.interface.marge, 0)
        rect = self.interface.rect_carte(niveau.nombre_cases_largeur, niveau.nombre_cases_hauteur, decalage)
        return Carte(rect, niveau)

    def blocs_selectionnables(self, x, y, largeur, hauteur):
        """
        Méthode créant les blocs pouvant être sélectionnés dans l'éditeur de niveau.

        :param x: position x du premier bloc
        :param y: position y du premier bloc
        :param largeur: largeur des blocs
        :param hauteur: hauteur des blocs
        :return: liste des blocs sélectionnables
        """
        blocs_selectionnables = [Terre, Mur, Caillou, Diamant, Personnage, Sortie]
        for i, bloc in enumerate(blocs_selectionnables):
            rect = pygame.Rect(x, y + i * hauteur, largeur, hauteur)
            blocs_selectionnables[i] = bloc(rect)
        return blocs_selectionnables

    def boutons_editeur(self, carte):
        """
        Méthode créant les boutons à utiliser dans l'éditeur.

        Le bouton des dimensions est un attribut, car sa valeur peut être modifiée à plusieurs endroits de la classe.

        :param carte:
        :return:
        """
        texte_dimensions = "{0}:{1}".format(carte.nombre_cases_hauteur, carte.nombre_cases_hauteur)
        self.bouton_dimensions = Bouton((0, 0), texte=texte_dimensions, taille=20)
        action_dimensions = Action(self.redimensionner_carte, carte)
        self.bouton_dimensions.action_sur_clic = action_dimensions

        texte_diamants = "Diamants requis: {0}".format(carte.nombre_diamants_pour_sortir)
        bouton_diamants = Bouton((0, 0), texte=texte_diamants, taille=20)
        action_diamants = Action(self.changer_nombre_diamants_pour_sortir, carte, bouton_diamants)
        bouton_diamants.action_sur_clic = action_diamants

        texte_temps = "Temps limite: {0}".format(carte.temps_maximal)
        bouton_temps = Bouton((0, 0), texte=texte_temps, taille=20)
        action_temps = Action(self.changer_temps_maximal, carte, bouton_temps)
        bouton_temps.action_sur_clic = action_temps

        boutons = [bouton_diamants, bouton_temps]

        rect_interface = self.interface.rect()
        dernier_bouton = boutons[-1]
        dernier_bouton.rect.bottomright = rect_interface.topright
        dernier_bouton.rect.bottom -= 5
        inverses = list(reversed(boutons))
        for i, bouton in enumerate(inverses):
            if i > 0:
                bouton.rect.bottomright = inverses[i - 1].rect.bottomleft
                bouton.rect.x -= 80

        return boutons

    def objet_survole(self, pos, *objets):
        """
        Regarde si le curseur se trouve au dessus d'objets affichés et retourne le premier objet survolé

        :param pos: position du curseur
        :param objets: objets à tester pour voir s'ils sont survolés
        :return: objet survolé ou "None" si aucun objet n'est survolé
        """
        return self.interface.objet_survole(pos, *objets)

    def selectionner(self, bloc):
        self.interface.selectionner(bloc)

    @staticmethod
    def changer_nombre_diamants_pour_sortir(carte, bouton):
        diamants_pour_sortir = askinteger("Nombre de diamants requis pour sortir", "Entrez la nouvelle valeur",
                                          minvalue=4, maxvalue=100)
        if diamants_pour_sortir is not None:
            carte.nombre_diamants_pour_sortir = diamants_pour_sortir
            bouton.texte = "Diamants requis: {0}".format(diamants_pour_sortir)

    @staticmethod
    def changer_temps_maximal(carte, bouton):
        temps_maximal = askinteger("Nombre de diamants requis pour sortir", "Entrez la nouvelle valeur",
                                          minvalue=1, maxvalue=3600)
        if temps_maximal is not None:
            carte.temps_maximal = temps_maximal
            bouton.texte = "Temps limite: {0}".format(temps_maximal)

    def editeur_niveau(self, carte_chargee=None):
        self.mode = MODES.EDITEUR
        if carte_chargee is None:
            carte = self.carte_vide(34, 20)
        else:
            carte = carte_chargee
        self.carte_editeur = carte
        # Les blocs selectionnables sont les blocs sur lesquels on peut cliquer pour choisir le type de blocs a ajouter
        # sur la carte
        blocs_selectionnables = self.blocs_selectionnables(0, 0, carte.largeur_case, carte.hauteur_case)
        bloc_selectionne = blocs_selectionnables[0]

        boutons = self.boutons_editeur(carte)

        position_souris = pygame.mouse.get_pos()
        bloc_pointeur = bloc_selectionne.__class__(pygame.Rect(position_souris, bloc_selectionne.rect.size))
        clic_gauche = clic_droit = False
        case = self.objet_survole(position_souris, *carte.tuple_cases)

        # Affichage première image
        if case is not None and not clic_droit:  # Si la souris survole la carte et qu'il n'y a pas de clic droit
            bloc_pointeur.rect = case.rect
            # On affiche la carte et le bloc sous le pointeur
            self.interface.afficher_carte(carte, bloc_pointeur)
        else:
            self.interface.afficher_carte(carte)

        minuteur = Minuteur(1/60.0, 0.01)
        while self.mode == MODES.EDITEUR:
            minuteur.passage()
            while minuteur.tics_restants() > 1:
                evenements = pygame.event.get()
                self.gerer_evenements_interface(evenements)
                for evenement in evenements:
                    if evenement.type == KEYDOWN:
                        if evenement.key == K_s and evenement.mod & KMOD_CTRL:
                            self.sauvegarder(carte)
                        if evenement.key == K_F1:
                            self.redimensionner_carte(carte)
                            taille_bloc = (carte.largeur_case, carte.hauteur_case)
                            blocs = self.blocs_selectionnables(0, 0, *taille_bloc)
                            for i, bloc in enumerate(blocs_selectionnables):
                                bloc.rect, bloc.image = blocs[i].rect, blocs[i].image
                            bloc_pointeur.taille = taille_bloc
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
                                    else:
                                        bouton_clique = self.objet_survole(position_souris, *boutons)
                                        if bouton_clique is not None:
                                            bouton_clique.cliquer()
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
            objets_a_afficher = blocs_selectionnables + boutons
            if case is not None and not clic_droit:  # Si la souris survole la carte et qu'il n'y a pas de clic droit
                bloc_pointeur.rect = case.rect
                objets_a_afficher.append(bloc_pointeur)
            objets_a_afficher.extend(boutons)
            self.interface.afficher_carte(carte, *objets_a_afficher)
            minuteur.attendre_fin()

    def gerer_erreurs(self, erreurs):
        self.interface.changer_erreur(erreurs)

    def gerer_evenements_interface(self, evenements):
        retour = self.interface.gerer_evenements(evenements)
        self.gerer_retour_interface(retour)

    def gerer_retour_interface(self, retour):
        if retour == EVENEMENTS.MENU:
            if self.mode == MODES.MENU:
                self.reprendre()
            else:
                self.menu()
        elif retour == EVENEMENTS.EDITEUR:
            if self.mode != MODES.EDITEUR:
                self.editeur_niveau()
            else:
                erreurs_niveau = self.carte_editeur.valider()
                if len(erreurs_niveau) > 0:
                    self.gerer_erreurs(erreurs_niveau)
                else:
                    self.interface.supprimer_erreurs()
                    self.niveau = Niveau.depuis_carte(self.carte_editeur)
                    self.vies = self.VIES_INITIALES
                    self.doit_commencer_niveau = True
                    self.mode = MODES.JEU

    def gerer_evenements(self):
        """
        Regarde les evenements et effectue les actions associees a chacun d'entre eux.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        self.gerer_evenements_interface(pygame.event.get())
        self.gerer_mouvement()  # Pas besoin de verifier un KEYDOWN grace au gestionnaire de touches
                                # KEYDOWN n'est parfois pas present alors qu'il devrait

    def gerer_mouvement(self):
        """
        S'occuppe des evenements correspondants a l'appui sur une touche.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        # On regarde si plus de la moitie de la periode est ecoulee (sert a ameliorer l'experience utilisateur)
        moitie_periode_est_depassee = self.minuteur.temps_ecoule_periode_actuelle() > self.minuteur.periode * 3.0 / 4.

        if not self.personnage.etait_en_mouvement or moitie_periode_est_depassee:   # Si le personnage est deja en train
                                                                                    # de bouger ou que plus de la moitie
                                                                                    # de la periode est ecoulee
            derniere_touche_pressee = self.interface.gestionnaire_touches.derniere_touche()
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
            doit_actualiser = False
            blocs = None
            if len(case.blocs) == 2:
                for bloc in case.blocs:
                    if isinstance(bloc, BlocTombant):
                        if self.personnage in case.blocs:
                            self.personnage.tuer()
                            blocs = [Explosion(case.rect)]
                            x = case.index.x
                            y = case.index.y
                            for i in range(-1, 2):
                                for j in range(-1, 2):
                                    x_ = x + i
                                    y_ = y + j
                                    if (0 <= x_ < self.carte.nombre_cases_largeur and
                                        0 <= y_ < self.carte.nombre_cases_hauteur):
                                        case_ = self.carte.case_a(x_, y_)
                                        case_.blocs = Explosion(case_.rect)
                            doit_actualiser = True
                            SONS.TUER.play()
                        else:
                            raise RuntimeError("Seul le personnage peut etre sur la meme case qu'un autre bloc.")
            if blocs is not None:
                case.blocs = blocs
                doit_actualiser = True

            if doit_actualiser:
                personnage = self.personnage
                sortie = self.carte.sortie
                self.carte.actualiser_blocs()
                self.carte.personnage = personnage
                self.carte.sortie = sortie

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
                self.actualiser_score(self.score + 10)
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
                    self.pos = self.personnage.get_rect()
                    self.personnage.tuer()
                    bloc_collisionne.a_tue = True
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
                    elif isinstance(bloc, BlocTombant):
                        reussite = self._collision_bloc_tombant(bloc, bloc_collisionne, direction)
                if not essai:
                    if reussite:
                        nouveau_rect = bloc.rect.move(vecteur(direction, self.carte.largeur_case, self.carte.hauteur_case))
                        self.carte.bouger(bloc, nouveau_rect)
                        bloc.bouger(direction)
                        bloc.a_deja_bouge = True
        return reussite, bloc_collisionne  # Le bloc collisionne n'est juste que si reussite == False

    def faire_tomber_droit(self, bloc, essai=False):
        reussite = self.faire_bouger(bloc, ORIENTATIONS.BAS, essai)[0]
        if reussite:
            bloc.tomber()
        else:
            if not essai:
                bloc.taper_objet()
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
            self.personnage.etait_en_mouvement = False
            self.personnage.caillou_pousse = None

    def effectuer_mouvements(self):
        """
        Fait bouger les differents blocs.

        :return: "None"
        """
        # On fait bouger le personnage
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

        self.terminer_mouvements()
