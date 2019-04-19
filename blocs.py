"""
Module gerant les differentes sortes de blocs pouvant etre affiches a l'ecran
"""

from pygame import sprite, image, transform, error
from numpy import array
from enum import IntEnum, unique

DOSSIER_IMAGES = "img/"


@unique
class Orientation(IntEnum):
    GAUCHE, DROITE, HAUT, BAS = range(4)


class Bloc(sprite.Sprite):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 75
    NOM_IMAGE = "mono-unknown.png"

    def __init__(self, x, y):
        sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mere
        self.image = image.load(self.chemin_image()).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x*self.TAILLE
        self.rect.y = y*self.TAILLE
        self.image = transform.scale(self.image, (self.TAILLE, self.TAILLE))

    def update(self):
        pass

    @classmethod
    def chemin_image(cls):
        return DOSSIER_IMAGES + cls.NOM_IMAGE

    def blocs_collisiones(self, groupe):
        blocs = sprite.spritecollide(self, groupe, dokill=False)
        if self in blocs:
            blocs.remove(self)
        return blocs

    def collision(self, groupe):
        pass

    def bouger(self):
        pass

    def tuer(self):
        pass


class Personnage(Bloc):
    NOM_IMAGE = "personnage.png"

    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self.orientation = Orientation.DROITE
        self.ancien_rect = self.rect

    def collision(self, groupe):
        blocs = self.blocs_collisiones(groupe)
        for bloc in blocs:
            type_de_bloc = bloc.__class__
            if type_de_bloc == Caillou:
                if bloc.tombe:
                    self.tuer()
            elif type_de_bloc == Terre:
                self.creuser_terre(bloc)
            elif type_de_bloc == Mur:
                self.revenir()

    def creuser_terre(self, terre):
        pass

    def avancer(self, direction):
        """
        Fait avancer le personnage dans la direction "direction".

        :param direction: direction dans laquelle avancer
        :return: "None"
        """
        self.orientation = direction
        if direction == Orientation.DROITE:
            vecteur = array([1, 0])
        elif direction == Orientation.GAUCHE:
            vecteur = array([-1, 0])
        elif direction == Orientation.HAUT:
            vecteur = array([0, -1])
        elif direction == Orientation.BAS:
            vecteur = array([0, 1])
        else:
            raise ValueError("L'orientation est invalide")
        vecteur *= self.TAILLE
        self.ancien_rect = self.rect  # Enregistre la position precedente du personnage pour pouvoir revenir en arriere
        self.rect = self.rect.move(*vecteur)  # L'asterisque permet de passer un tuple a la place de plusieurs arguments

    def revenir(self):
        """
        Annule le dernier mouvement du personnage.

        :return: "None"
        """
        self.rect = self.ancien_rect


class Caillou(Bloc):
    NOM_IMAGE = "caillou.jpg"

    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self.tombe = False


class Terre(Bloc):
    NOM_IMAGE = "terre.PNG"


class Diamant(Bloc):
    NOM_IMAGE = "diamant.jpg"


class Mur(Bloc):
    NOM_IMAGE = "mur.png"


class Porte(Bloc):
    NOM_IMAGE = "porte.png"


class Entree(Porte):
    pass


class Sortie(Porte):
    pass
