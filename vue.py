"""
Fichier contenant du code gerant l'affichage.
"""
from constantes import *


class InterfaceGraphique:
    def __init__(self, ecran):
        self.ecran = ecran
        self._mode = None
        self.arriere_plan = pygame.Surface(RESOLUTION)
        self.arriere_plan.fill((0, 0, 0))
        self.marge = int(RESOLUTION[0] * 0.01)
        self.rect = pygame.Rect(self.marge, self.marge, RESOLUTION[0] - 2 * self.marge, RESOLUTION[1] - 2 * self.marge)

    def rect_carte(self, niveau):
        nombre_cases_largeur = niveau.nombre_cases_largeur
        nombre_cases_hauteur = niveau.nombre_cases_hauteur
        cote_case = int(round(min(self.rect.width / float(nombre_cases_largeur), self.rect.height / float(nombre_cases_hauteur))))
        largeur = cote_case * nombre_cases_largeur
        hauteur = cote_case * nombre_cases_hauteur
        x = self.rect.x + int(round((self.rect.width - largeur) / 2.0))
        y = self.rect.y + int(round((self.rect.height - hauteur) / 2.0))
        return pygame.Rect(x, y, largeur, hauteur)


    @staticmethod
    def x_min(carte):
        largeur_jeu = carte.rectangle.width
        x_min_exact = (RESOLUTION[0] - largeur_jeu) / 2.0
        return int(round(x_min_exact))

    @staticmethod
    def y_min(carte):
        hauteur_jeu = carte.rectangle.height
        y_min_exact = (RESOLUTION[1] - hauteur_jeu) / 2.0
        return int(round(y_min_exact))

    @classmethod
    def index_vers_coordonnees(cls, carte, x, y):
        return cls.x_min(carte) + x * carte.largeur_case, cls.y_min(carte) + y * carte.hauteur_case

    @classmethod
    def coordonnees_vers_index(cls, carte, x, y):
        return (x - cls.x_min(carte)) / carte.largeur_case, (y - cls.y_min(carte)) / carte.hauteur_case

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
        if not
        resolution = self.ecran.get_size()
        self.ecran = pygame.display.set_mode(resolution, FULLSCREEN)

    def passer_en_fenetre(self):
        resolution = self.ecran.get_size()
        self.ecran = pygame.display.set_mode(resolution, RESIZABLE)

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
