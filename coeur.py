"""
Module definissant des classes utilisees dans l'ensemble du programme.
"""
from constantes import *


class Action(object):
    def __init__(self, fonction=None, *args, **kwargs):
        self.reinitialiser()
        if fonction is not None:
            self.fonction = fonction
        self.args = args
        self.kwargs = kwargs

    def effectuer(self):
        return self.fonction(*self.args, **self.kwargs)

    def reinitialiser(self):
        self.fonction = lambda *_: None
        self.args = tuple()
        self.kwargs = dict()


class Coordonnees(list):
    def __init__(self, x, y):
        super(Coordonnees, self).__init__([x, y])

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, valeur):
        self[0] = valeur

    @x.deleter
    def x(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, valeur):
        self[1] = valeur

    @y.deleter
    def y(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    def __mul__(self, autre):
        return Coordonnees(self.x * autre, self.y * autre)

    def __div__(self, autre):
        return Coordonnees(self.x / autre, self.y / autre)


class Rectangle(pygame.Rect):
    """
    Classe permettant d'avoir des rectangles pouvant etre utilises comme cle de dictionnaire.
    """
    def __init__(self, *args, **kwargs):
        arguments = []
        if len(kwargs) != 0:
            if "left" in kwargs.keys():
                arguments.append(kwargs["left"])
            if "top" in kwargs.keys():
                arguments.append(kwargs["top"])
            if "width" in kwargs.keys():
                arguments.append(kwargs["width"])
            if "height" in kwargs.keys():
                arguments.append(kwargs["height"])
        super(Rectangle, self).__init__(*(args + tuple(arguments)))

    def __eq__(self, autre):
        return (self.x == autre.x and self.y == autre.y and self.width == autre.width and
                self.height == autre.height)

    def __hash__(self):
        """
        Permet de donner une identification unique a chaque rectangle
        :return: hash
        """
        arguments = (self.x, self.y, self.width, self.height)
        return hash(arguments)

    @staticmethod
    def rectangle_defaut(x, y):
        largeur = 50
        return Rectangle(x, y, largeur, largeur)
