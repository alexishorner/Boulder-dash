from pygame import sprite, image

DOSSIER_IMAGES = "img/"


class Bloc(sprite.Sprite):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 10
    NOM_IMAGE = "mono-unknown.png"

    def __init__(self, ecran):
        sprite.Sprite.__init__(self)  # On appele le constructeur de la classe mere
        self.image = image.load(self.chemin_image()).convert_alpha()
        self.ecran = ecran
        self.rect = self.image.get_rect()

    @classmethod
    def chemin_image(cls):
        return DOSSIER_IMAGES + cls.NOM_IMAGE

    def collision(self, groupe):
        pass

    def bouger(self):
        pass

    def tuer(self):
        pass


class Personnage(Bloc):
    NOM_IMAGE = "personnage.png"

    def collision(self, groupe):
        pass

class Caillou(Bloc):
    NOM_IMAGE = "caillou.jpg"


class Terre(Bloc):
    NOM_IMAGE = "terre.PNG"


class Mur(Bloc):
    NOM_IMAGE = "mur.png"
