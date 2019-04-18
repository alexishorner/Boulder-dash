"""
Module gerant la logique du jeu.
"""

import pygame
from pygame.locals import *
from modele import *
import time


class Jeu:
    """
    Classe gerant l'ensemble du jeu.
    """
    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((Constantes.LARGEUR_ECRAN, Constantes.HAUTEUR_ECRAN), RESIZABLE)
        self.arriere_plan = pygame.Surface((Constantes.LARGEUR_ECRAN, Constantes.HAUTEUR_ECRAN))
        self.arriere_plan.fill((0, 0, 0))
        self.carte = Carte(Constantes.NIVEAUX[0])
        self.continuer = False
        pygame.key.set_repeat(1, 500)

    def commencer(self):
        """
        Commence le jeu et continue jusqu'a l'arret du programme

        :return: "None"
        """
        self.continuer = True
        while self.continuer:
            self.actualiser_ecran()
            self.gerer_evenements()

    def actualiser_ecran(self):
        """
        Actualise l'ecran.

        :return: "None"
        """
        self.ecran.blit(self.arriere_plan, (0, 0))  # Dessine l'arriere plan
        self.carte.dessiner(self.ecran)  # Dessine les blocs
        pygame.display.flip()  # Actualise l'ecran

    def gerer_evenements(self):
        """
        Regarde les evenements et effectue les actions associees a chacun d'entre eux.

        :return: "None"
        """
        for evenement in pygame.event.get():
            if evenement.type == QUIT:
                self.continuer = False
            elif evenement.type == KEYDOWN:
                self.sur_touche_pressee()

    def sur_touche_pressee(self):
        """
        S'occuppe des evenements correspondants a l'appui sur une touche.

        :return: "None"
        """
        touches_pressees = pygame.key.get_pressed()
        if touches_pressees[K_UP] or touches_pressees[K_w]:
            self.carte.personnage.avancer(Orientation.HAUT)
        elif touches_pressees[K_DOWN] or touches_pressees[K_s]:
            self.carte.personnage.avancer(Orientation.BAS)
        elif touches_pressees[K_LEFT] or touches_pressees[K_a]:
            self.carte.personnage.avancer(Orientation.GAUCHE)
        elif touches_pressees[K_RIGHT] or touches_pressees[K_d]:
            self.carte.personnage.avancer(Orientation.DROITE)

