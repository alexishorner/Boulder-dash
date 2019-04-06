import pygame.image
from pygame.sprite import Sprite

DOSSIER_IMAGES = "img/"

class Bloc(Sprite):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 10
    NOM_IMAGE = "mono-unknown.png"

    def __init__(self):
        Sprite.__init__(self)  # On appele le constructeur de la classe mere
        self.image = pygame.image.load(self.chemin_image())

    @classmethod
    def chemin_image(cls):
        return DOSSIER_IMAGES + cls.NOM_IMAGE

    def collision(self):
        pass

    def bouger(self):
        pass

    def tuer(self):
        pass
