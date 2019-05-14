"""
Module contenant toutes les constantes. Si des variables ne doivent pas etre importees avec le module, il faut commencer
leur nom par un tiret bas ("_").
"""
import pygame
from pygame.locals import *
from enum import IntEnum, unique
import os
import sys

# On regarde si le jeu tourne sur Windows Vista ou une version de Windows plus recente
if os.name == "nt" and sys.getwindowsversion()[0] >= 6:
    import ctypes
    # On desactive l'etirement de l'ecran pour empecher des bugs d'affichage
    ctypes.windll.user32.SetProcessDPIAware()

pygame.init()  # obligatoire pour utiliser une grande partie de pygame
_info = pygame.display.Info()
RESOLUTION = _info.current_w, _info.current_h
ECRAN = pygame.display.set_mode(RESOLUTION, FULLSCREEN)  # obligatoire pour pouvoir charger des images
_chemin = os.path.dirname(__file__)  # on recupere le chemin du module ci-present
os.chdir(_chemin)  # on change de repertoire pour pouvoir utiliser des chemins relatifs


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

for classe, _chemin in IMAGES.iteritems():
    IMAGES[classe] = charger(CHEMIN_IMAGES + _chemin)  # on charge les images

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

    @staticmethod
    def opposee(oritentation):
        if oritentation == ORIENTATIONS.GAUCHE:
            return ORIENTATIONS.DROITE
        elif oritentation == ORIENTATIONS.DROITE:
            return ORIENTATIONS.GAUCHE
        elif oritentation == ORIENTATIONS.HAUT:
            return ORIENTATIONS.BAS
        elif oritentation == ORIENTATIONS.BAS:
            return ORIENTATIONS.BAS
        return None

    @staticmethod
    def sont_opposees(orientation_1, orientation_2):
        return orientation_1 == ORIENTATIONS.opposee(orientation_2)

class DIMENSIONS:
    X_MIN = 0
    Y_MIN = 0
    LARGEUR_CASE = 75


class TOUCHES:
    MOUVEMENT = (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d)
    HAUT = (K_UP, K_w)
    BAS = (K_DOWN, K_s)
    GAUCHE = (K_LEFT, K_a)
    DROITE = (K_RIGHT, K_d)


NIVEAUX = ("""
            ############
            #OOOOOOOOOO#
            #OOOOOOOO$$#
            #$$$O~O~$$~#
            #OO~O~$]~~~#
            #**********#
            #~~~~~~~~~P#
            #~~~~~~~~~~#
            #~~~[~~~~~~#
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
