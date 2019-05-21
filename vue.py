# coding: utf-8
"""
Fichier contenant du code gerant l'affichage.
"""
from coeur import *


class Label(object):
    def __init__(self, position_centre=(0, 0), texte="", taille=24, police=POLICES.PRESS_START_K, couleur=(255, 255, 255, 230)):
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
        return self._taille

    @taille.setter
    def taille(self, nouveau):
        self._taille = nouveau
        self.rendu()

    @property
    def texte(self):
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
        self.rendu()

    @property
    def police(self):
        return self._police

    @police.setter
    def police(self, nouvelle):
        self._police = nouvelle
        self.rendu()

    @property
    def couleur(self):
        return self._couleur

    @couleur.setter
    def couleur(self, nouvelle):
        self._couleur = nouvelle
        self.rendu()

    @property
    def rect(self):
        return self._rect

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, nouvelle):
        self._image = nouvelle
        self._texte = None
        self.rendu()

    def rendu(self):
        if self._texte is not None and self._image is None:
            self._image, rect = self.police.render(self._texte, self._couleur, size=self.taille)
        elif self._image is not None and self._texte is None:
            rect = self._image.rect
        else:
            raise AttributeError("Exactement un des deux attributs \"texte\" et \"image\" doit valoir \"None\".")
        if self._rect is None:
            self._rect = rect
        else:
            self._rect.size = rect.size


class Bouton(Label):
    def __init__(self, position_centre, action_sur_clic=Action(), image=None, texte="", taille=40,
                 police=POLICES.ARCADECLASSIC):
        super(Bouton, self).__init__(position_centre, texte, taille, police)
        if image is not None:
            self.image = image
        self.action_sur_clic = action_sur_clic

    def selectionner(self):
        self.texte = "- " + self.texte

    def deselectionner(self):
        self.texte = self.texte.replace("- ", "")

    def cliquer(self):
        return self.action_sur_clic.effectuer()


class InterfaceGraphique:
    def __init__(self, ecran):
        self.ecran = ecran
        self._mode = None
        self.passer_en_fenetre()
        self.arriere_plan = pygame.Surface(RESOLUTION)
        self.arriere_plan.fill((0, 0, 0))
        self.marge = int(self.ecran.get_width() * 0.02)
        pygame.key.set_repeat(1, 1)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.labels_menu = []
        self.boutons_menu = []
        self.distance_labels = 100
        self.label_erreur = Label(couleur=(226, 22, 22))
        self.label_vies = Label()
        self.label_temps = Label()
        self.ajuster_position_labels()

    def rect(self, decalage=None):
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

    def rect_carte(self, niveau, decalage=None):
        rect = self.rect(decalage)
        nombre_cases_largeur = niveau.nombre_cases_largeur
        nombre_cases_hauteur = niveau.nombre_cases_hauteur
        cote_case = int(round(min(rect.width / float(nombre_cases_largeur), rect.height / float(nombre_cases_hauteur))))
        largeur = cote_case * nombre_cases_largeur
        hauteur = cote_case * nombre_cases_hauteur
        x = rect.x + int(round((rect.width - largeur) / 2.0))
        y = rect.y + int(round((rect.height - hauteur) / 2.0))
        return pygame.Rect(x, y, largeur, hauteur)

    @staticmethod
    def appliquer_translation(translation, x=None, y=None, rect=None):
        if rect is not None:
            retour = rect.copy()
            retour.x, retour.y = translation(rect.x, rect.y)
        elif None not in (x, y):
            retour = translation(x, y)
        else:
            raise TypeError("Les arguments de la methode ne peuvent pas tous etre None.")
        return retour

    def quitter(self):
        """
        Quitte le jeu apres confirmation de l'utilisateur.

        :return: "None"
        """
        pygame.quit()
        sys.exit(0)  # TODO : ajouter confirmation

    def passer_en_plein_ecran(self):
        if not self._mode == FULLSCREEN:
            resolution = self.ecran.get_size()
            self.ecran = pygame.display.set_mode(resolution, FULLSCREEN)
            self._mode = FULLSCREEN

    def passer_en_fenetre(self):
        if not self._mode == RESIZABLE:
            resolution = self.ecran.get_size()
            self.ecran = pygame.display.set_mode(resolution, RESIZABLE)
            self._mode = RESIZABLE

    def gerer_evenements(self, evenements):
        self.gestionnaire_touches.actualiser_touches(pygame.key.get_pressed())
        for evenement in evenements:
            if evenement.type == QUIT:
                self.quitter()
            if evenement.type == VIDEORESIZE:  # FIXME : pygame ne signale pas de changement de taille
                print(evenement.size)
                print(self.ecran.get_size())
                self.ecran = pygame.display.set_mode(evenement.size)
                print(self.ecran.get_size())
            if evenement.type == KEYUP:
                if evenement.key == K_m:
                    return EVENEMENTS.MENU
                if evenement.key == K_q:
                    self.quitter()
                elif evenement.key == K_ESCAPE:
                    mods = pygame.key.get_mods()

                    # On regarde si la touche Maj est pressee et qu'aucun autre modificateur ne l'est, on utilise pour
                    # ce faire des operateurs bit a bit
                    if not mods & (KMOD_ALT | KMOD_CTRL):
                        if mods & KMOD_SHIFT:
                            self.passer_en_plein_ecran()
                        else:
                            self.passer_en_fenetre()
                elif evenement.key == K_F12:
                    return EVENEMENTS.EDITEUR
            return None

    def objet_survole(self, pos, *objets):
        if len(objets) == 0:
                raise RuntimeError("Nombre d'arguments insuffisant.")
        for objet in objets:
            if objet.rect.collidepoint(pos):
                return objet
        return None

    def selectionner(self, bloc):
        pass

    def menu(self):
        labels = self.labels_menu
        boutons = self.boutons_menu
        for bouton in boutons:
            bouton.deselectionner()
        menu = labels + boutons
        bouton_selectionne = boutons[0]
        bouton_selectionne.selectionner()
        numero_bouton = 0
        minuteur = Minuteur(0.15, 0.005)
        while 1:
            minuteur.passage()
            while minuteur.tics_restants() > 1:
                evenements = pygame.event.get()
                retour = self.gerer_evenements(evenements)
                if retour is not None:
                    return retour
                for evenement in evenements:
                    if evenement.type == KEYUP:
                        if evenement.key == K_RETURN:
                            return bouton_selectionne.cliquer()
                if minuteur.tics_restants() > 1:
                    minuteur.attendre_un_tic()

            touche_pressee = self.gestionnaire_touches.derniere_touche()

            if touche_pressee in (K_UP, K_DOWN):
                if touche_pressee == K_UP:
                    numero_bouton -= 1
                elif touche_pressee == K_DOWN:
                    numero_bouton += 1
                numero_bouton %= len(boutons)
                bouton_selectionne.deselectionner()
                bouton_selectionne = boutons[numero_bouton]
                bouton_selectionne.selectionner()

            self.afficher(None, *menu)
            minuteur.attendre_fin()

    @staticmethod
    def message_erreur(erreurs):
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
        self.label_erreur.texte = ""

    def ajuster_position_labels(self):
        rect = self.rect()
        pos = (rect.centerx, rect.bottom + 5)
        self.label_erreur.rect.centerx, self.label_erreur.rect.top = pos
        self.label_vies.rect.left, self.label_vies.rect.bottom = rect.left, rect.top - 5
        labels = [self.label_vies, self.label_temps]
        for i, label in enumerate(labels):
            if i > 0:
                label_precedent = labels[i - 1]
                label.rect.left, label.rect.top = label_precedent.rect.right + self.distance_labels, label_precedent.rect.top

    def afficher_erreur(self, erreurs):
        message = self.message_erreur(erreurs)
        self.label_erreur.texte = message

    def afficher(self, carte=None, *autres_objets):
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan

        # On dessine les blocs par ordre de position z
        if carte is not None:
            for bloc in carte.blocs_tries:
                if bloc is not None:
                    self.ecran.blit(bloc.image, bloc.rect)

        if self.label_erreur.texte != "":
            rect = self.rect()
            self.label_erreur.centre = (rect.centerx, rect.bottom + int(round(self.marge / 2.0)))

        self.ajuster_position_labels()
        labels = (self.label_erreur, self.label_vies, self.label_temps)
        for objet in (autres_objets + labels):
            self.ecran.blit(objet.image, objet.rect)
        pygame.display.flip()  # Actualise l'ecran
