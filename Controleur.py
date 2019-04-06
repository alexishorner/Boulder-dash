from pygame.sprite import Sprite

class Bloc(Sprite):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 10
    IMAGE = None

    def __init__(self):
        Sprite.__init__(self)  # On appele le constructeur de la classe mere
        if self.IMAGE is not None:
            

    def collision(self):
        pass

    def bouger(self):
        pass

    def tuer(self):
        pass
