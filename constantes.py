"""
Module contenant toutes les constantes. Si des variables ne doivent pas etre importees avec le module, il faut commencer
leur nom par un tiret bas ("_").
"""
import pygame
from pygame.locals import *
from enum import IntEnum, unique
import os

pygame.init()
pygame.display.set_mode((0, 0))
chemin = os.path.dirname(__file__)
os.chdir(chemin)


def charger(image):
    return pygame.image.load(image).convert_alpha()


CHEMIN_IMAGES = "img/"
IMAGES = {"Bloc": "mono-unknown.png", "Personnage": "personnage.png",
          "Diamant": "diamant.jpg", "Terre": "terre.PNG", "Mur": "mur.png", "Caillou": "caillou.jpg"}

for classe, chemin in IMAGES.iteritems():
    IMAGES[classe] = charger(CHEMIN_IMAGES + chemin)

image_porte = charger(CHEMIN_IMAGES + "porte.png")
IMAGES.update({"Porte": image_porte, "Entree": image_porte, "Sortie": image_porte})


@unique
class ORIENTATION(IntEnum):
    """
    Classe permettant de definir des orientations comme des nombres entiers.
    """
    GAUCHE, DROITE, HAUT, BAS = range(4)


class ECRAN:
    LARGEUR = 1920  # TODO : adapter resolution a chaque ecran
    HAUTEUR = 1080


class TOUCHES:
    MOUVEMENT = (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d)
    HAUT = (K_UP, K_w)
    BAS = (K_DOWN, K_s)
    GAUCHE = (K_LEFT, K_a)
    DROITE = (K_RIGHT, K_d)


NIVEAUX = ("""
            ############
            #***O***O*$#
            #***OOP**[##
            #$$$#******#
            #OOOO*$]***#
            #**********#
            #**********#
            #**********#
            #**********#
            #**********#
            ############
            """,)
