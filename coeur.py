"""
Module definissant des classes utilisees dans l'ensemble du programme.
"""
from constantes import *
import time
import math
from numpy import matrix


def modulo(num, div):
    """
    Fonction permettant de calculer le reste de la division de deux nombres sans avoir d'erreur due a l'arrondi des ordinateurs.

    Cette fonction donne le meme resultat que l'operateur "%" pour les nombres entiers, mais donne des resultats
    correspondants a la definition de modulo pour tous les nombres, y compris les nombres a virgule et les nombres negatifs.

    Exemple :
    7.5 % 0.05 donne 0.04999999999999992 (incorrect), alors que modulo(7.5, 0.05) donne 0.0 (correct)

    Verification:
    7.5 = 150.0 * 0.05 + 0.0

    Le desavantage de cette fonction est qu'elle perd un peu de precision pour parer aux erreurs d'arrondi.

    :param num: numerateur
    :param div: diviseur
    :return: reste de la division de "num" par "div"
    """
    a = float(num)  # Assure que la division sera flottante
    b = float(div)
    facteur = int(1e14)  # Facteur de precision
    return (a / b - int(math.ceil(a / b * facteur) / facteur)) * b


def vecteur(directions, e_x, e_y):
    try:
        len(directions)  # On verifie si "directions" est iterable
        directions_ = directions
    except TypeError:
        directions_ = [directions]  # S'il n'y a qu'une seule direction on la transforme en liste
    v = matrix([[0],
               [0]])  # On commence avec un vecteur nul
    for direction in directions_:  # On ajoute le vecteur correspondant a chaque direction
        if direction == ORIENTATIONS.DROITE:
            v += matrix([[1],
                         [0]])
        elif direction == ORIENTATIONS.GAUCHE:
            v += matrix([[-1],
                         [0]])
        elif direction == ORIENTATIONS.HAUT:
            v += matrix([[0],
                         [-1]])
        elif direction == ORIENTATIONS.BAS:
            v += matrix([[0],
                         [1]])
        else:
            raise ValueError("La direction est invalide")
    matrice = matrix([[e_x, 0],
                     [0, e_y]])
    v = matrice * v  # On multiplie chaque composante du vecteur pour passer dans la base {(e_x, 0), (0, e_y)}
    return v


class Action(object):
    def __init__(self, fonction=None, *args, **kwargs):
        self.reinitialiser()
        if fonction is not None:
            self.fonction = fonction
        self.args = args
        self.kwargs = kwargs

    def effectuer(self):
        return self.fonction(*self.args, **self.kwargs)

    def reinitialiser(self):
        self.fonction = lambda *_: None
        self.args = tuple()
        self.kwargs = dict()


class Coordonnees(list):
    def __init__(self, x, y):
        super(Coordonnees, self).__init__([x, y])

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, valeur):
        self[0] = valeur

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, valeur):
        self[1] = valeur

    def __mul__(self, autre):
        return Coordonnees(self.x * autre, self.y * autre)

    def __div__(self, autre):
        return Coordonnees(self.x / autre, self.y / autre)


class Rectangle(pygame.Rect):
    """
    Classe permettant d'avoir des rectangles pouvant etre utilises comme cle de dictionnaire.
    """
    def __init__(self, *args, **kwargs):
        arguments = []
        if len(kwargs) != 0:
            if "left" in kwargs.keys():
                arguments.append(kwargs["left"])
            if "top" in kwargs.keys():
                arguments.append(kwargs["top"])
            if "width" in kwargs.keys():
                arguments.append(kwargs["width"])
            if "height" in kwargs.keys():
                arguments.append(kwargs["height"])
        super(Rectangle, self).__init__(*(args + tuple(arguments)))

    def __eq__(self, autre):
        return (self.x == autre.x and self.y == autre.y and self.width == autre.width and
                self.height == autre.height)

    def __hash__(self):
        """
        Permet de donner une identification unique a chaque rectangle
        :return: hash
        """
        arguments = (self.x, self.y, self.width, self.height)
        return hash(arguments)

    @staticmethod
    def rectangle_defaut(x, y):
        largeur = 50
        return Rectangle(x, y, largeur, largeur)


class GestionnaireTouches(object):  # On herite d'"object" pour avoir une classe de nouveau style.
    """
    Classe permettant de gerer les evenements de pression des touches.

    Contrairement a "pygame.key.get_pressed()", elle permet de savoir dans quel ordre les differentes touches ont ete
    pressees.

    La methode "pygame.key.get_pressed()" renvoie une liste de booleens indiquant pour chaque touche possible si elle
    est pressee. Pour ordonner les touches pressees dans l'ordre de pressage il est plus simple de conserver une liste
    des indexes des touches pressees, ce qui est a l'origine des differentes conversions presentes dans les methode de
    cette classe.
    """
    def __init__(self, touches_pressees_booleens=None):
        if touches_pressees_booleens is None:
            touches_pressees_indexes = []
        else:
            touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)
        self.indexes_ordonnes = touches_pressees_indexes  # indexes des touches dans leur ordre de pressage

    def actualiser_touches(self, touches_pressees_booleens):
        """
        Ajoute les nouvelles touches pressees et enleve les touches non pressees.

        :param touches_pressees_booleens: liste de booleens indiquant pour chaque touche si elle est pressee
        :return: "None"
        """
        ajoutees, enlevees = self.changements_touches(touches_pressees_booleens)  # Regarde les touches nouvellement
                                                                        # pressees et les touches n'etant plus pressees
        for touche in enlevees:
            self.indexes_ordonnes.remove(touche)
        self.indexes_ordonnes.extend(ajoutees)  # Ajoute a la fin de la liste les touches nouvellement pressees

    def changements_touches(self, touches_pressees_booleens):
        """
        Detecte les changement dans les touches pressees par rapport a l'etat d'avant.

        :param touches_pressees_booleens: touches pressees dans l'etat actuel
        :return: instances de "list", l'une contenant les touches ajoutees, l'autre les touches enlevees
        """
        touches_pressees_indexes = self.booleens_vers_indexes(touches_pressees_booleens)    # Recupere l'index des
                                                                                            # touches pressees
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
        booleens = [False] * GestionnaireTouches.nombre_de_touches()
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


class Minuteur(object):  # Ici le fait d'avoir une classe de nouveau style a une vraie utilite, puisque cela permet d'utiliser des proprietes
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
        self.numero_periode = None

    @property
    def periode(self):
        return self._periode

    @periode.setter
    def periode(self, nouvelle):
        self._periode = nouvelle
        self.reinitialiser()

    def temps_ecoule(self):
        """
        Retourne le temps ecoule depuis la derniere reinitialisation du minuteur.

        :return: temps ecoule
        """
        return time.time() - self.debut

    def temps_ecoule_periode_actuelle(self):
        """
        Retourne le temps ecoule depuis la derniere fin de periode.

        :return: nombre representant le temps ecoule depuis la derniere fin de periode
        """
        ecoule = self.temps_ecoule()
        return modulo(ecoule, self.periode)

    def reinitialiser(self):
        """
        Remet le minuteur a zero.

        :return: "None"
        """
        self.debut = time.time()
        self.numero_periode = None

    def passage(self):
        """
        Methode appelee a chaque fin de boucle des evenements pour indiquer au minuteur qu'il peut commencer une
        nouvelle periode.

        :return: "None"
        """
        est_premier_tour = self.numero_periode is None
        if est_premier_tour or self.numero_periode != self.nombre_periodes_ecoulees():
            self.numero_periode = self.nombre_periodes_ecoulees()   # On actualise le numero de la periode en fonction
                                                                    # du temps ecoule
        else:  # Si la periode n'est tout juste pas finie (a cause de l'imprecision de la fonction "time.sleep")
            self.numero_periode += 1  # On augmente quand meme le numero de la periode, car elle est censee etre finie

    def nombre_periodes_ecoulees(self):
        """
        Determine le nombre de fois qu'une periode s'est ecoulee.

        :return: numero de la periode actuelle
        """
        return int(self.temps_ecoule() / self.periode)

    def attendre_un_tic(self):
        """
        Attends le temps d'un tic.

        :return: "None"
        """
        time.sleep(self.tic)

    def attendre_fin(self):
        """
        Attend jusqu'a la fin de la periode specifiee, "None" attend jusqu'a la fin de la periode actuelle.

        :return: "None"
        """
        if self.temps_restant() > 0:
            time.sleep(self.temps_restant())  # On attend la fin de la periode numero "self.numero_periode"

    def temps_restant(self):
        nombre_periodes_ecoulees = self.nombre_periodes_ecoulees()

        # Dans l'eventualite ou le numero de la periode est superieur au nombre de periodes ecoulees (peut arriver si la
        # methode "self.passage" appelee deux fois de suite sans attendre)
        if self.numero_periode is None:  # TODO : ameliorer commentaire
            ecart = 0
        else:
            ecart = self.numero_periode - nombre_periodes_ecoulees
        if ecart >= 0:
            return ecart * self.periode + (self.periode - self.temps_ecoule_periode_actuelle())
        else:
            return 0

    def tics_restants(self):
        """
        Retourne le nombre de tics restants avant la fin de la periode.

        :return: nombre de tics restant avant la fin de la periode
        """
        return self.temps_restant() / self.tic
