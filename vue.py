"""
Fichier contenant du code gerant l'affichage.
"""
from constantes import *


class InterfaceGraphique:
    def __init__(self, ecran):
        self.ecran = ecran
        self.arriere_plan = pygame.Surface(RESOLUTION)
        self.arriere_plan.fill((0, 0, 0))

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
        return cls.x_min(carte) + x * carte.largeur_case, cls.y_min(carte) + y * carte.largeur_case

    @classmethod
    def coordonnees_vers_index(cls, carte, x, y):
        return (x - cls.x_min(carte)) / carte.largeur_case, (y - cls.y_min(carte)) / carte.largeur_case

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

    @classmethod
    def coords_carte_vers_ecran(cls, carte, x=None, y=None, rect=None):
        translation = lambda x, y: (cls.x_min(carte) + x, cls.y_min(carte) + y)
        return cls.appliquer_translation(translation, x, y, rect)

    @classmethod
    def coords_ecran_vers_carte(cls, carte, x=None, y=None, rect=None):
        translation = lambda x, y: (x - cls.x_min(carte), y - cls.y_min(carte))
        return cls.appliquer_translation(translation, x, y, rect)

    def passer_en_plein_ecran(self):
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
                    self.ecran.blit(bloc.image, self.coords_carte_vers_ecran(carte, rect=bloc.rect))
        for objet in autres_objets:
            self.ecran.blit(objet.image, objet.rect)
        pygame.display.flip()  # Actualise l'ecran
