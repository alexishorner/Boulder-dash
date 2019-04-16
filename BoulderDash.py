"""
Module principal du jeu.
C'est ici que le jeu se lance.
"""
import pygame
from Controleur import *
import time

pygame.init()

if __name__ == "__main__":
    niveau = Niveau("""
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
                    """)

    carte = Carte(niveau)
    carte.dessiner()
    pygame.display.update()

    continuer = True
    while continuer:
        for evenement in pygame.event.get():
            if evenement.type == QUIT:
                continuer = False
