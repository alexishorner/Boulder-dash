# coding: utf-8
"""
Fichier contenant du code gerant l'affichage.
"""
from coeur import *


class Label(object):
    """
    Classe permettant d'afficher du texte ou une image sur la fenêtre.
    """
    def __init__(self, position_centre=(0, 0), texte="", taille=24, police=POLICES.PRESS_START_K,
                 couleur=(255, 255, 255, 230)):
        self._taille = taille
        self._police = police
        self._image = None
        self._rect = None
        self._texte = ""
        self._couleur = couleur
        self.texte = texte
        self.centre = position_centre

    @property
    def centre(self):
        """
        Propriété permettant de gérer l'accès à la position du centre du label.

        :return: instance de "Coordonnees" indiquant les coordonnées du centre
        """
        return Coordonnees(*self.rect.center)

    @centre.setter
    def centre(self, nouvelle):
        try:
            x, y = nouvelle.x, nouvelle.y
        except AttributeError:
            x, y = nouvelle[0], nouvelle[1]
        self._rect.center = (x, y)

    @property
    def haut_gauche(self):
        """
        Propriété permettant de gérer l'accès  à la position du coin supérieur gauche du label.

        :return: instance de "Coordonnees" indiquant les coordonnées du coin supérieur gauche
        """
        return Coordonnees(*self._rect.topleft)

    @haut_gauche.setter
    def haut_gauche(self, nouveau):
        try:
            x, y = nouveau.x, nouveau.y
        except AttributeError:
            x, y = nouveau[0], nouveau[1]
        self._rect.topleft = (x, y)

    @property
    def taille(self):
        """
        Propriété permettant de gérer l'accès à la taille de la police du label. Si la taille de la police est modifiée,
        le rendu du label est effectué à nouveau.

        :return: nombre indiquant la taille de la police
        """
        return self._taille

    @taille.setter
    def taille(self, nouveau):
        self._taille = nouveau
        self.rendu()  # On refait le rendu pour rendre les changements visibles

    @property
    def texte(self):
        """
        Propriété permettant de gérer l'accès au texte du label. Si le texte est modifié, le rendu du label est effectué
        à nouveau.

        :return: texte affiché dans le label
        """
        texte = self._texte
        if self.police == POLICES.ARCADECLASSIC:
            texte = texte.replace("   ", " ")
        return texte

    @texte.setter
    def texte(self, nouveau):
        texte = nouveau
        if self.police == POLICES.ARCADECLASSIC:
            texte = nouveau.replace(" ", "   ")
        self._texte = texte
        self._image = None
        self.rendu()  # On refait le rendu pour rendre les changements visibles

    @property
    def police(self):
        """
        Propriété permettant de gérer l'accès à la police du texte du label. Si la police est modifiées, le rendu du
        label est effectué à nouveau.

        :return: police utilisée par le label
        """
        return self._police

    @police.setter
    def police(self, nouvelle):
        self._police = nouvelle
        self.rendu()  # On refait le rendu pour rendre les changements visibles

    @property
    def couleur(self):
        """
        Propriété permettant de gérer l'accès à la couleur du texte du label. Si la couleur du texte est modifiée, le
        rendu du label est effectué à nouveau.

        :return: couleur du texte du label
        """
        return self._couleur

    @couleur.setter
    def couleur(self, nouvelle):
        self._couleur = nouvelle
        self.rendu()

    @property
    def rect(self):
        """
        Propriété permettant de gérer l'accès au rectangle du label.

        Aucun mutateur n'est définit pour éviter la modification complète du rectangle. Il peut néanmoins toujours être
        changé par la modification de ses attributs, mais cela est déconseillé pour les attributs autres que "center",
        "centerx", "centery", "size", "width" et "height".

        :return: rectangle du label
        """
        return self._rect

    @property
    def image(self):
        """
        Propriété permettant de gérer l'accès à l'image (texte rendu ou image classique) du label.

        Aucun mutateur n'est définit pour éviter la modification de l'image depuis l'extérieur de la classe.

        :return: image du label
        """
        return self._image

    @image.setter
    def image(self, nouvelle):
        self._image = nouvelle
        self._texte = None
        self.rendu()  # On refait le rendu pour rendre les changements visibles

    def rendu(self):
        """
        Effectue le rendu du texte du label et enregistre l'image rendu dans l'attribut "_image".

        :return: "None"
        """
        if self._texte is not None and self._image is None:  # Si le texte a une valeur, mais pas l'image
            self._image, rect = self.police.render(self._texte, self._couleur, size=self.taille)
        elif self._image is not None and self._texte is None:  # Si l'image a une valeur, mais pas le texte
            rect = self._image.rect
        else:
            # On ne peut pas afficher du texte et une image dans le même label
            raise AttributeError("Exactement un des deux attributs \"texte\" et \"image\" doit valoir \"None\".")

        if self._rect is None:
            self._rect = rect
        else:
            # On change la taille tout en gardant le centre à la même position
            centre = self.rect.center
            self._rect.size = rect.size
            self._rect.center = centre


class Bouton(Label):
    """
    Classe permettant de définir des boutons cliquables.
    """
    def __init__(self, position_centre, action_sur_clic=Action(), image=None, texte="", taille=40,
                 police=POLICES.ARCADECLASSIC):
        super(Bouton, self).__init__(position_centre, texte, taille, police)
        if image is not None:
            self.image = image
        self.action_sur_clic = action_sur_clic  # permet d'associer une action au clic du bouton

    def selectionner(self):
        """
        Méthode permettant de montrer que le bouton est sélectionné.

        :return: "None"
        """
        if self.texte is not None:
            self.texte = "- " + self.texte

    def deselectionner(self):
        """
        Méthode permettant d'arrêter de montrer que le bouton est sélectionné.

        :return: "None"
        """
        self.texte = self.texte.replace("- ", "", 1)

    def cliquer(self):
        """
        Méthode à appeler si le bouton a été cliqué.

        :return: retour de l'action associée au clic du bouton
        """
        return self.action_sur_clic.effectuer()


class InterfaceGraphique:
    """
    Classe permettant d'afficher des objets sur la fenêtre.
    """
    def __init__(self, ecran):
        self.ecran = ecran
        self.arriere_plan = pygame.Surface(self.ecran.get_size())
        self.arriere_plan.fill((0, 0, 0))
        self.marge = int(self.ecran.get_width() * 0.02)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.labels_menu = []
        self.boutons_menu = []
        self.distance_labels = 100
        self.label_erreur = Label(couleur=(226, 22, 22))
        self.label_vies = Label()
        self.label_temps = Label()
        self.label_score = Label()
        self.label_diamants = Label()
        self.ajuster_position_labels()

    def rect(self, decalage=None):
        """
        Calcule le rectangle dessinable de l'interface en prenant en compte la marge.

        :param decalage: position désirée de l'angle supérieur gauche du rectangle
        :return:
        """
        if decalage is None:
            x_0 = y_0 = self.marge
        else:
            x_0 = decalage[0]
            y_0 = decalage[1]
            if x_0 < self.marge:
                x_0 = self.marge
            if y_0 < self.marge:
                y_0 = self.marge
        largeur = self.ecran.get_width() - x_0 - self.marge
        hauteur = self.ecran.get_height() - y_0 - self.marge

        return pygame.Rect(x_0, y_0, largeur, hauteur)

    def rect_carte(self, nombre_cases_largeur, nombre_cases_hauteur, decalage=None):
        """
        Calcule le rectangle que la carte doit avoir en fonction de ses dimensions.

        :param nombre_cases_largeur: nombre de cases dans la hauteur de la carte
        :param nombre_cases_hauteur: nombre de cases dans la largeur de la carte
        :param decalage: position désirée de l'angle supérieur gauche du rectangle
        :return: rectangle que la carte doit avoir
        """
        rect = self.rect(decalage)

        largeur_case_max = rect.width / float(nombre_cases_largeur)
        hauteur_case_max = rect.height / float(nombre_cases_hauteur)
        cote_case = min(largeur_case_max, hauteur_case_max)
        cote_case = int(round(cote_case))

        largeur = cote_case * nombre_cases_largeur
        hauteur = cote_case * nombre_cases_hauteur

        rect_carte = pygame.Rect(0, 0, largeur, hauteur)
        rect_carte.center = rect.center
        return rect_carte

    def quitter(self):
        """
        Quitte le jeu après confirmation de l'utilisateur.

        :return: "None"
        """
        pygame.quit()
        sys.exit(0)  # TODO : ajouter confirmation

    def gerer_evenements(self, evenements):
        """
        S'occuppe des évènements de touches et de quitter.

        :param evenements: évènements à gérer
        :return: valeur de l'énumération "EVENEMENTS" indiquant quel type d'évènement a été détecté sans pouvoir être
        traité
        """
        self.gestionnaire_touches.actualiser_touches(pygame.key.get_pressed())
        for evenement in evenements:
            if evenement.type == QUIT:
                self.quitter()
            if evenement.type == KEYUP:
                if evenement.key == K_m:
                    return EVENEMENTS.MENU
                if evenement.key == K_q:
                    self.quitter()
                elif evenement.key == K_ESCAPE:
                    return EVENEMENTS.MENU
                elif evenement.key == K_F12:
                    return EVENEMENTS.EDITEUR
            return None

    @staticmethod
    def objet_survole(pos, *objets):
        """
        Indique le premier objet dont le rectangle collisionne le point pos.

        Cela sert à détecter si le curseur de la souris se trouve au dessus d'un objet.

        :param pos: point contre lequel tester les collisions
        :param objets:
        :return:
        """
        if len(objets) == 0:
                raise RuntimeError("Nombre d'arguments insuffisant.")
        for objet in objets:
            if objet.rect.collidepoint(pos):
                return objet
        return None

    def selectionner(self, bloc):
        pass

    def menu(self):
        """
        Affiche le menu.

        :return: valeur de l'énumération "EVENEMENTS" indiquant les évènements détectés mais non traités
        """
        labels = self.labels_menu
        boutons = self.boutons_menu
        for bouton in boutons:
            bouton.deselectionner()
        menu = labels + boutons
        bouton_selectionne = boutons[0]
        bouton_selectionne.selectionner()
        numero_bouton = 0
        touche_pressee = None
        minuteur = Minuteur(0.15, 0.01)
        while 1:
            minuteur.passage()
            etait_pressee = touche_pressee is not None
            touche_pressee = None
            while minuteur.tics_restants() > 1:
                evenements = pygame.event.get()
                retour = self.gerer_evenements(evenements)
                if retour is not None:
                    return retour
                for evenement in evenements:
                    if evenement.type == KEYUP:
                        if evenement.key == K_RETURN:
                            return bouton_selectionne.cliquer()
                if touche_pressee is None:
                    if not etait_pressee or minuteur.temps_ecoule_periode_actuelle() > minuteur.periode * 3.0 / 4.0:
                        touche_pressee = self.gestionnaire_touches.derniere_touche()
                if minuteur.tics_restants() > 1:
                    minuteur.attendre_un_tic()

            if touche_pressee in TOUCHES.HAUT or touche_pressee in TOUCHES.BAS:
                if touche_pressee in TOUCHES.HAUT:
                    numero_bouton -= 1
                elif touche_pressee in TOUCHES.BAS:
                    numero_bouton += 1
                numero_bouton %= len(boutons)
                bouton_selectionne.deselectionner()
                bouton_selectionne = boutons[numero_bouton]
                bouton_selectionne.selectionner()

            self.afficher(*menu)
            minuteur.attendre_fin()

    @staticmethod
    def message_erreur(erreurs):
        """
        Crée un message d'erreur en fonction d'une liste d'erreurs.

        Cette fonction ne prend en compte que l'erreur la plus importante de la liste et ignore les autres.

        :param erreurs: liste d'erreurs s'étant produites
        :return: chaîne de caractères représentant le message d'erreur
        """
        message_erreur = ""
        erreurs_ = erreurs
        try:
            list(erreurs)
        except TypeError:
            erreurs_ = [erreurs]
        if len(erreurs_) > 0:
            if ERREURS.PERSONNAGE_MANQUANT in erreurs_:
                message_erreur = "Personnage manquant"
            elif ERREURS.PORTE_MANQUANTE in erreurs_:
                message_erreur = "Porte manquante"
            elif ERREURS.DIAMANTS_INSUFFISANTS:
                message_erreur = "Nombre de diamants insuffisants"
            else:
                raise RuntimeError("L'erreur spécifiée est invalide")
        return message_erreur

    def supprimer_erreurs(self):
        """
        Efface les erreurs affichées.

        :return: "None"
        """
        self.label_erreur.texte = ""

    def ajuster_position_labels(self):
        """
        Donne une position a chaque label.

        :return: "None"
        """
        rect = self.rect()

        # Erreur en bas au centre
        self.label_erreur.rect.centerx, self.label_erreur.rect.top = (rect.centerx, rect.bottom + 5)

        # Vies en haut à gauche
        self.label_vies.rect.left, self.label_vies.rect.bottom = rect.left, rect.top - 5

        # Labels du haut placés à la suite
        labels = [self.label_vies, self.label_temps, self.label_score, self.label_diamants]
        for i, label in enumerate(labels):
            if i > 0:
                label_precedent = labels[i - 1]
                label.rect.topleft = label_precedent.rect.right + self.distance_labels, label_precedent.rect.top

    def changer_erreur(self, erreurs):
        """
        Méthode modifiant l'erreur affichée en fonction des erreurs s'étant produites.

        :param erreurs:
        :return:
        """
        message = self.message_erreur(erreurs)
        self.label_erreur.texte = message

    def afficher(self, *objets):
        """
        Affiche des objets à l'écran. Chaque objet doit posséder un attribut "image" et "rect".

        :param objets: objets à afficher
        :return: "None"
        """
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan
        for objet in objets:
            self.ecran.blit(objet.image, objet.rect)
        pygame.display.flip()  # Actualise l'ecran

    def afficher_carte(self, carte, *autres_objets):
        """
        Méthode permettant d'afficher la carte seule sur l'écran

        :param carte: carte à afficher
        :param autres_objets: objets supplémentaires à afficher
        :return: "None"
        """
        labels = (self.label_erreur,)
        blocs = tuple(carte.blocs_tries)
        self.afficher(*(blocs + autres_objets + labels))

    def afficher_jeu(self, carte, *autres_objets):
        """
        Méthode permettant d'afficher le jeu.

        :param carte: carte à afficher
        :param autres_objets: objets supplémentaires à afficher
        :return: "None"
        """
        self.ajuster_position_labels()
        labels = (self.label_erreur, self.label_vies, self.label_temps, self.label_score, self.label_diamants)
        blocs = tuple(carte.blocs_tries)
        self.afficher(*(blocs + autres_objets + labels))
