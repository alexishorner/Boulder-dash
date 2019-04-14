from Blocs import *

LARGEUR = 500
HAUTEUR = 500
ecran = display.set_mode((LARGEUR, HAUTEUR))


class Niveau:
    def __init__(self, numero=None):
        self.numero = numero


    def dessiner(self):
        self.blocs.draw(ecran)


class Carte:
    def __init__(self, niveau):
