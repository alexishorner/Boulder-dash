"""
Fichier contenant du code gerant l'affichage.
"""
from coeur import *


class Label(object):
    def __init__(self, position_centre, texte="", taille=16, police=POLICES.ARCADECLASSIC):
        self._position = position_centre
        self._taille = taille
        self._texte = texte
        self._police = police
        self._image = None
        self._rect = None
        self.rendu()

    @property
    def position_centre(self):
        return Coordonnees(*self.rect.center)

    @position_centre.setter
    def position_centre(self, nouvelle):
        try:
            x, y = nouvelle.x, nouvelle.y
        except AttributeError:
            x, y = nouvelle[0], nouvelle[1]
        self._rect.center = (x, y)

    @property
    def taille(self):
        return self._taille

    @taille.setter
    def taille(self, nouveau):
        self._taille = nouveau
        self.rendu()

    @property
    def texte(self):
        return self._texte

    @texte.setter
    def texte(self, nouveau):
        self._texte = nouveau
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

    def rendu(self, couleur=(255, 255, 255, 230)):
        if self._texte is not None and self._image is None:
            self._image, rect = self.police.render(self.texte, couleur, size=self.taille)
            self._rect.size = (rect.width, rect.height)
        elif self._image is not None and self._texte is None:
            self._rect.size = self._image.rect.size
        else:
            raise AttributeError("Exactement un des deux attributs \"texte\" et \"image\" doit valoir \"None\".")


class Bouton(Label):
    def __init__(self, position_centre, image=None, texte="", taille=16, police=POLICES.ARCADECLASSIC):
        super(Bouton, self).__init__(position_centre, texte, taille, police)
        if image is not None:
            self.image = image
        self.action_sur_clic = Action()

    def cliquer(self):
        self.action_sur_clic.effectuer()


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
        exit()  # TODO : ajouter confirmation

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
            if evenement.type == VIDEORESIZE:
                print(self.ecran.get_size())
                self.ecran = pygame.display.set_mode(evenement.size)
                print(self.ecran.get_size())
            if evenement.type == KEYUP:
                if evenement.key == K_m:
                    return MODES.MENU
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
                    return MODES.EDITEUR
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
        rect = self.rect()
        h = rect.height
        labels = [Label((rect.centerx, 0.3*h), "Menu", 18)]
        boutons = [Label((rect.centerx, labels[0].position_centre.x + 0.02*h), "Reprendre"),
                   Label((rect.centerx, 0), "Recommencer"), Label((rect.centerx, 0), "Nouvelle partie"),
                   Label((rect.centerx, 0),"Charger niveau"), Label((rect.centerx, 0), "Creer niveau")]
        for i, bouton in enumerate(boutons):
            if i > 0:
                y_prec = boutons[i - 1].position_centre.y
                bouton.position_centre = (bouton.position_centre.x, y_prec + 0.015*h)
        elements_affichables = labels + boutons
        bouton_selectionne = boutons[0]
        minuteur = Minuteur(1/60.0, 0.005)
        while 1:
            minuteur.passage()
            while minuteur.tics_restants() > 1:
                self.gerer_evenements(pygame.event.get())
                if minuteur.tics_restants() > 1:
                    minuteur.attendre_un_tic()

            self.afficher(None, elements_affichables)
            minuteur.attendre_fin()

    def afficher(self, carte=None, *autres_objets):
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan

        # On dessine les blocs par ordre de position z
        if carte is not None:
            for bloc in carte.blocs_tries:
                if bloc is not None:
                    self.ecran.blit(bloc.image, bloc.rect)
        for objet in autres_objets:
            self.ecran.blit(objet.image, objet.rect)
        pygame.display.flip()  # Actualise l'ecran
