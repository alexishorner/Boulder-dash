import boulder_dash
import os
import pygame

def init():
    path = os.path.dirname(boulder_dash.__file__)  # On recupere le chemin du module a tester
    os.chdir(path)  # On change de repertoire pour pouvoir utiliser des chemins relatifs
    pygame.init()
    pygame.display.set_mode((0, 0))
