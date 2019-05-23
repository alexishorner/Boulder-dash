# coding: utf-8
"""
Module contenant toutes les constantes. Si des variables ne doivent pas etre importees avec le module, il faut commencer
leur nom par un tiret bas ("_").
"""
import pygame
from pygame import freetype
from pygame.locals import *
from enum import IntEnum, unique
import os
import sys

pygame.mixer.init(22050, -16, 2, 64)

# On regarde si le jeu tourne sur Windows Vista ou une version de Windows plus recente
if os.name == "nt" and sys.getwindowsversion()[0] >= 6:
    import ctypes
    # On desactive l'etirement de l'ecran pour empecher des bugs d'affichage
    ctypes.windll.user32.SetProcessDPIAware()

pygame.init()  # obligatoire pour utiliser une grande partie de pygame
_info = pygame.display.Info()
RESOLUTION = _info.current_w, _info.current_h
ECRAN = pygame.display.set_mode((1600, 900))  # obligatoire pour pouvoir charger des images
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
          "Diamant": "diamant.png", "Terre": "terre.PNG", "Mur": "mur.png",
          "Caillou": "caillou.png", "Sortie": "porte.png", "Explosion": "explosion.png", "Portefin": "porte_fin.png"}

for _classe, _chemin in IMAGES.iteritems():
    IMAGES[_classe] = charger(CHEMIN_IMAGES + _chemin)  # on charge les images


class SONS:
    """
    Classe utilisée comme espace de noms pour stocker les différents sons du jeu.
    """
    CAILLOU_TOMBE = pygame.mixer.Sound("sounds/box_push.ogg")
    POUSSER_CAILLOU = pygame.mixer.Sound("sounds/boulder.ogg")
    RAMASSER_DIAMANT = pygame.mixer.Sound("sounds/collectdiamond.ogg")
    BOUGER = pygame.mixer.Sound("sounds/walk_empty.ogg")
    CREUSER_TERRE = pygame.mixer.Sound("sounds/walk_dirt.ogg")
    FINI = pygame.mixer.Sound("sounds/finished.ogg")
    TUER = pygame.mixer.Sound("sounds/explosion.ogg")
    PERDU = pygame.mixer.Sound("sounds/game_over.ogg")
    APPARAITRE = pygame.mixer.Sound("sounds/crack.ogg")
    DIAMANT_TOMBE1 = pygame.mixer.Sound("sounds/diamond1.ogg")
    VIE_BONUS = pygame.mixer.Sound(("sounds/bonus_life.ogg"))
    TIMEOUT = pygame.mixer.Sound(("sounds/timeout1.ogg"))


@unique
class ORIENTATIONS(IntEnum):
    """
    Classe permettant d'énumérer et de manipuler des orientations.
    """
    GAUCHE, DROITE, HAUT, BAS = range(4)

    @staticmethod
    def opposee(orientation):
        """
        Méthode statique renvoyant l'orientation opposée d'une certaine orientation.

        :param orientation: Instance de "ORIENTATIONS" décrivant l'orientation dont on veut calculer l'opposée.
        :return: Instance d'"ORIENTATIONS" opposée à "orientation".
        """
        if orientation == ORIENTATIONS.GAUCHE:
            return ORIENTATIONS.DROITE
        elif orientation == ORIENTATIONS.DROITE:
            return ORIENTATIONS.GAUCHE
        elif orientation == ORIENTATIONS.HAUT:
            return ORIENTATIONS.BAS
        elif orientation == ORIENTATIONS.BAS:
            return ORIENTATIONS.BAS
        return None

    @staticmethod
    def sont_opposees(orientation_1, orientation_2):
        """
        Méthode statique permettant de déterminer si deux directions sont opposées.

        :param orientation_1: première orientation à comparer
        :param orientation_2: deuxième orientation à comparer
        :return: Booléen indiquant si les deux orientations sont opposées.
        """
        return orientation_1 == ORIENTATIONS.opposee(orientation_2)


class TOUCHES:
    """
    Classe utilisée comme espace de noms regroupant des touches par utilité.
    """
    MOUVEMENT = (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d)
    HAUT = (K_UP, K_w)
    BAS = (K_DOWN, K_s)
    GAUCHE = (K_LEFT, K_a)
    DROITE = (K_RIGHT, K_d)


@unique
class CLIC(IntEnum):
    """
    Énumération décrivant les boutons de la souris.
    """
    GAUCHE = 0
    DROIT = 2


@unique
class MODES(IntEnum):
    """
    Énumération décrivant ce qui est affiché à l'écran.
    """
    JEU, EDITEUR, MENU = range(3)


@unique
class ERREURS(IntEnum):
    """
    Énumération décrivant différentes erreurs.
    """
    PERSONNAGE_MANQUANT, PORTE_MANQUANTE, DIAMANTS_INSUFFISANTS = range(3)


class POLICES:
    """
    Classe utilisée comme espace de noms pour stocker des polices.
    """
    ARCADECLASSIC = freetype.Font("polices/arcadeclassic/ARCADECLASSIC.TTF")
    PRESS_START_K = freetype.Font("polices/press_start/prstartk.ttf")


@unique
class EVENEMENTS(IntEnum):
    """
    Énumération décrivant les différents évènements pouvant arriver.
    """
    JEU, EDITEUR, MENU, REPRENDRE, RECOMMENCER, NOUVELLE_PARTIE, CHARGER_NIVEAU, CREER_NIVEAU = range(8)


NIVEAUX = [None]*5  # On donne une valeur à cette constante dans "modele.py"
