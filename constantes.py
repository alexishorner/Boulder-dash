"""
Module contenant toutes les constantes. Si des variables ne doivent pas etre importees avec le module, il faut commencer
leur nom par un tiret bas ("_").
"""
import pygame
from pygame.locals import *
from enum import IntEnum, unique
import os

pygame.init()  # obligatoire pour utiliser une grande partie de pygame
pygame.display.set_mode((0, 0))  # obligatoire pour pouvoir charger des images
chemin = os.path.dirname(__file__)  # on recupere le chemin du module ci-present
os.chdir(chemin)  # on change de repertoire pour pouvoir utiliser des chemins relatifs


def charger(image):
    """
    Charge une image.

    :param image: chemin de l'image a charger
    :return: image chargee
    """
    return pygame.image.load(image).convert_alpha()


CHEMIN_IMAGES = "img/"
IMAGES = {"Bloc": "mono-unknown.png", "Personnage": "personnage.png",
          "Diamant": "diamant.jpg", "Terre": "terre.PNG", "Mur": "mur.png", "Caillou": "caillou.jpg"}

for classe, chemin in IMAGES.iteritems():
    IMAGES[classe] = charger(CHEMIN_IMAGES + chemin)  # on charge les images

image_porte = charger(CHEMIN_IMAGES + "porte.png")  # on s'occupe de la porte separement pour ne pas la charger trois
                                                    # fois au lieu d'une
IMAGES.update({"Porte": image_porte, "Entree": image_porte, "Sortie": image_porte})     # on ajoute l'image de porte aux
                                                                                        # autres images


@unique
class ORIENTATIONS(IntEnum):
    """
    Classe permettant de definir des orientations comme des nombres entiers.
    """
    GAUCHE, DROITE, HAUT, BAS = range(4)


class DIMENSIONS:
    X_MIN = 0
    Y_MIN = 0
    LARGEUR_CASE = 75


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
            #OOOOOOOOOO#
            #OOOOOOOO[##
            #$$$#~O~~~~#
            #OO~O~$]~~~#
            #**********#
            #~~~~~~~~~P#
            #~~~~~~~~~~#
            #~~~~~~~~~~#
            #~~~~~~****#
            ############
            """,
            """
            ############
            #***O***O*$#
            #***OOP**[##
            #$$$#******#
            #OO*O*$]***#
            #**********#
            #**********#
            #**********#
            #**********#
            #**********#
            ############
            """)
