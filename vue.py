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

    def rect_carte_vers_rect_ecran(self, carte, rect):
        rect_ = rect.copy()
        rect_.x = self.x_min(carte) + rect.x
        rect_.y = self.y_min(carte) + rect.y
        return rect_

    def passer_en_plein_ecran(self):
        resolution = self.ecran.get_size()
        self.ecran = pygame.display.set_mode(resolution, FULLSCREEN)

    def passer_en_fenetre(self):
        resolution = self.ecran.get_size()
        self.ecran = pygame.display.set_mode(resolution, RESIZABLE)

    def afficher(self, carte):
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan

        # On dessine les blocs par ordre de position z
        for bloc in carte.blocs_tries:
            self.ecran.blit(bloc.image, self.rect_carte_vers_rect_ecran(carte, bloc.rect))
        pygame.display.flip()  # Actualise l'ecran
