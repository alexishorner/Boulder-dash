"""
Module gerant la logique du jeu.
"""

import pygame
from pygame.locals import *
from modele import *
import time

def main():
    pygame.init()
    ecran = pygame.display.set_mode((Constantes.LARGEUR_ECRAN, Constantes.HAUTEUR_ECRAN), RESIZABLE)
    arriere_plan = pygame.Surface((Constantes.LARGEUR_ECRAN, Constantes.HAUTEUR_ECRAN))
    arriere_plan.fill((0, 0, 0))

    carte = Carte(Constantes.NIVEAUX[0])

    pygame.key.set_repeat(0, 500)

    continuer = True
    while continuer:
        ecran.blit(arriere_plan, (0, 0))
        carte.dessiner(ecran)
        pygame.display.flip()
        for evenement in pygame.event.get():
            if evenement.type == QUIT:
                continuer = False
            elif evenement.type == KEYDOWN:
                touches_pressees = pygame.key.get_pressed()
                if touches_pressees[K_UP] or touches_pressees[K_w]:
                    carte.personnage.avancer(Orientation.HAUT)
                elif touches_pressees[K_DOWN] or touches_pressees[K_s]:
                    carte.personnage.avancer(Orientation.BAS)
                elif touches_pressees[K_LEFT] or touches_pressees[K_a]:
                    carte.personnage.avancer(Orientation.GAUCHE)
                elif touches_pressees[K_RIGHT] or touches_pressees[K_d]:
                    carte.personnage.avancer(Orientation.DROITE)


