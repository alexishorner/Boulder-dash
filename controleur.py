"""
Module gerant la logique du jeu.
"""

import pygame
from pygame.locals import *
from modele import *
import time
import math


def modulo(num, div):
    """
    Fonction permettant de calculer le reste de la division de deux nombres sans avoir d'erreur due a l'arrondi des ordinateurs.

    Cette fonction donne le meme resultat que l'operateur "%" pour les nombres entiers, mais donne des resultats
    correspondants a la definition de modulo pour tous les nombres, y compris les nombres a virgule et les nombres negatifs.

    Exemple :
    7.5 % 0.05 donne 0.04999999999999992 (incorrect), alors que modulo(7.5, 0.05) donne 0.0 (correct)

    Verification:
    7.5 = 150.0 * 0.05 + 0.0

    Le desavantage de cette fonction est qu'elle pert un peu de precision pour parer aux erreurs d'arrondi.

    :param num: numerateur
    :param div: diviseur
    :return: reste de la division de "num" par "div"
    """
    a = float(num)
    b = float(div)
    facteur = int(1e14)
    return (a / b - int(math.ceil(a / b * facteur) / facteur)) * b


class GestionnaireTouches:
    """
    Classe permettant de gerer les evenements de pression des touches.
    """
    def __init__(self, touches_pressees_booleens=None):
        if touches_pressees_booleens is None:
            touches_pressees_indexes = []
        else:
            touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)
        self.indexes_ordonnes = touches_pressees_indexes

    def actualiser_touches(self, touches_pressees_booleens):
        """
        Ajoute les nouvelles touches pressees et enleve les touches non pressees.

        :param touches_pressees_booleens: liste de booleens indiquant pour chaque touche si elle est pressee
        :return: "None"
        """
        ajoutees, enlevees = self.changements_touches(touches_pressees_booleens)
        for touche in enlevees:
            self.indexes_ordonnes.remove(touche)
        self.indexes_ordonnes.extend(ajoutees)

    def changements_touches(self, touches_pressees_booleens):
        """
        Detecte les changement dans les touches pressees par rapport a l'etat d'avant.

        :param touches_pressees_booleens: touches pressees dans l'etat actuel
        :return: instances de "list", l'une contenant les touches ajoutees, l'autre les touches enlevees
        """
        touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)
        ajoutees = [touche for touche in touches_pressees_indexes if touche not in self.indexes_ordonnes]
        enlevees = [touche for touche in self.indexes_ordonnes if touche not in touches_pressees_indexes]
        return ajoutees, enlevees

    def derniere_touche(self):
        """
        Retourne la derniere touche pressee.

        :return: derniere touche pressee
        """
        if len(self.indexes_ordonnes) > 0:
            return self.indexes_ordonnes[-1]
        else:
            return None

    @staticmethod
    def booleens_vers_indexes(booleens):
        """
        Retourne les indexes des touches pressees a partir d'une liste de booleens.

        :param booleens: liste de booleens determinant pour chaque touche si elle est pressee
        :return: liste contenant l'index de chaque touche pressee
        """
        return [index for index, booleen in enumerate(booleens) if booleen]

    @staticmethod
    def indexes_vers_booleens(indexes):
        """
        Retourne une liste de booleens determinant pour chaque touche si elle est pressee a partir de l'index de chaque
        touche pressee.

        :param indexes: liste contenant l'index de chaque touche pressee
        :return: liste de booleens determinant pour chaque touche si elle est pressee
        """
        booleens = [False]*GestionnaireTouches.nombre_de_touches()
        for index in indexes:
            booleens[index] = True
        return booleens

    @staticmethod
    def nombre_de_touches():
        """
        Retourne le nombre total de touches.

        :return: nombre total de touches
        """
        return len(pygame.key.get_pressed())


class Minuteur:
    """
    Classe permettant de simuler un minuteur. Le minuteur se remet a zero a intervalles fixes dont la duree est
    determinee par "self._periode". La remise a zero est une illusion externe qui n'a jamais rellement lieu en interne ;
    au lieu de cela le temps ecoule est reduit modulo "self._periode".
    """
    def __init__(self, periode, tic):
        """
        Constructeur de la classe "Minuteur".

        :param periode: duree entre chaque remise a zero du minuteur
        :param tic: plus petite unite de temps du minuteur
        """
        self._periode = periode
        self.tic = tic
        self.debut = time.time()

    def temps_ecoule(self):
        """
        Retourne le temps ecoule depuis la derniere fin de periode.

        :return: nombre representant le temps ecoule depuis la derniere fin de periode
        """
        ecoule = time.time() - self.debut
        return modulo(ecoule, self._periode)

    def reinitialiser(self):
        """
        Remet le minuteur a zero.

        :return: "None"
        """
        self.debut = time.time()

    def numero_periode_actuelle(self):
        """
        Determine le numero de la periode actuelle, i.e. le nombre de fois que la periode s'est ecoulee moins 1.

        :return: numero de la periode actuelle
        """
        return int(self.temps_ecoule() / self._periode)

    def attendre_fin(self, numero_periode=None):
        """
        Attend jusqu'a la fin de la periode specifiee, par defaut la periode actuelle.

        :return: "None"
        """
        numero_periode_actuelle = self.numero_periode_actuelle()
        if numero_periode is None:
            ecart = 0
        elif numero_periode >= numero_periode_actuelle:
            ecart = numero_periode_actuelle - numero_periode
        else:
            return
        temps = ecart * self._periode + (self._periode - self.temps_ecoule())
        time.sleep(temps)

    def tics_restants(self):
        """
        Retourne le nombre de tics restants avant la fin de la periode.

        :return: nombre de tics restant avant la fin de la periode
        """
        return (self._periode - self.temps_ecoule()) / self.tic


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
        pygame.key.set_repeat(1, 1)
        self.gestionnaire_touches = GestionnaireTouches(pygame.key.get_pressed())
        self.minuteur = Minuteur(0.5, 0.05)
        self.temps_entre_coups = 0.5
        self.periode_actualisation = 0.05

    def commencer(self):
        """
        Commence le jeu et continue jusqu'a l'arret du programme

        :return: "None"
        """
        self.actualiser_ecran()
        self.minuteur.reinitialiser()
        self.continuer = True
        while self.continuer:
            deja_traite = False
            debut = time.time()
            while self.minuteur.tics_restants() > 1:  # FIXME : quand la fenetre est bougee le code est mis en pause
                if not deja_traite:
                    deja_traite = self.gerer_evenements()
                    if deja_traite:
                        self.actualiser_ecran()
                if self.minuteur.tics_restants() > 1:
                    time.sleep(0.05)
            if self.minuteur.tics_restants() > 0:
                self.minuteur.attendre_fin()

            print(time.time() - debut)

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

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        for evenement in pygame.event.get():
            if evenement.type == QUIT:
                self.continuer = False
            elif evenement.type == KEYDOWN:
                return self.sur_touche_pressee()

    def sur_touche_pressee(self):
        """
        S'occuppe des evenements correspondants a l'appui sur une touche.

        :return: Booleen informant si une touche a provoque une action dans le jeu
        """
        self.gestionnaire_touches.actualiser_touches(pygame.key.get_pressed())
        derniere_touche_pressee = self.gestionnaire_touches.derniere_touche()
        if derniere_touche_pressee in (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d):
            if derniere_touche_pressee == K_UP or derniere_touche_pressee == K_w:
                self.carte.personnage.avancer(Orientation.HAUT)
            elif derniere_touche_pressee == K_DOWN or derniere_touche_pressee == K_s:
                self.carte.personnage.avancer(Orientation.BAS)
            elif derniere_touche_pressee == K_LEFT or derniere_touche_pressee == K_a:
                self.carte.personnage.avancer(Orientation.GAUCHE)
            elif derniere_touche_pressee == K_RIGHT or derniere_touche_pressee == K_d:
                self.carte.personnage.avancer(Orientation.DROITE)
            return True
        else:
            return False

