"""
Fichier contenant du code gerant l'affichage.
"""
from coeur import *


class InterfaceGraphique:
    def __init__(self, ecran):
        self.ecran = ecran
        self._mode = None
        self.passer_en_fenetre()
        self.arriere_plan = pygame.Surface(RESOLUTION)
        self.arriere_plan.fill((0, 0, 0))
        self.marge = int(self.ecran.get_width() * 0.02)

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
