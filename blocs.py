"""
Module gerant les differentes sortes de blocs pouvant etre affiches a l'ecran
"""
# TODO :
#   - tomber
#   - collisions
#   - pousser pierres
#   - porte
#   - animations
#   - son
#   - menu
#   - score
#   - temps limite
#   - niveaux predefinis
#   - editeur de niveaux
#   - generateur de niveaux automatique
#   - mechants


from constantes import *
from numpy import array


class Coordonees(list):
    def __init__(self, x, y):
        list.__init__(self, [x, y])

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, valeur):
        self[0] = valeur

    @x.deleter
    def x(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, valeur):
        self[1] = valeur

    @y.deleter
    def y(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    def __mul__(self, autre):
        return Coordonees(self.x * autre, self.y * autre)

    def __div__(self, autre):
        return Coordonees(self.x / autre, self.y / autre)

class Rectangle(pygame.Rect):
    """
    Classe gerant les rectangles
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
        pygame.Rect.__init__(self, *(args + tuple(arguments)))

    def __hash__(self):
        """
        Permet de donner une identification unique a chaque rectangle
        :return: hash
        """
        argument = (self.x, self.y, self.z=0 self.width, self.height, self.class)   #TODO: implementer z
        return hash(argument)

class Bloc(pygame.sprite.Sprite, object):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 75

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mere
        image = IMAGES[self.__class__.__name__]
        self.image = pygame.transform.scale(image, (self.TAILLE, self.TAILLE))
        self.rect = self.image.get_rect()
        self.rect.x = x*self.TAILLE
        self.rect.y = y*self.TAILLE
        self.ancien_rect = self.rect
        self.nombre_actions_cycle = 0
        self.orientation = ORIENTATION.DROITE
        
    @property
    def a_deja_bouge(self):
        return bool(self.nombre_actions_cycle)

    def actualiser(self, groupe):
        pass
    # TODO : gerer les autres actions (comme tomber)

    def terminer_cycle(self):
        self.nombre_actions_cycle = 0

    @property
    def index(self):
        return Coordonees(self.rect.x, self.rect.y) / self.TAILLE

    @index.setter
    def index(self, *valeur):
        index = Coordonees(*valeur)
        self.rect.x, self.rect.y = index * self.TAILLE

    @index.deleter
    def index(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    @staticmethod
    def homotetie(rectangle, facteur):
        """
        Renvoie une copie d'un rectangle avec des dimensions multipliees par un certain facteur. Conserve la position du
        centre du rectangle.

        :param rectangle: rectangle a agrandir
        :param facteur: nombre par lequel les cotes du rectangle sont multiplies
        :return:
        """
        rect = rectangle.copy()  # Cree une copie du rectangle de base pour eviter de modifier ses dimensions
        centre_x = rect.centerx  # Enregistre la position du centre
        centre_y = rect.centery
        rect.width *= facteur  # Multiplie les cotes par le facteur
        rect.height *= facteur
        depl_x = rect.centerx - centre_x  # Calcule de combien le centre a ete deplace
        depl_y = rect.centery - centre_y
        rect.x -= depl_x  # Deplace le rectangle pour remettre le centre a sa position initiale
        rect.y -= depl_y
        return rect

    # def blocs_adjacents(self, groupe):
    #     """
    #     Renvoie un groupe contenant les blocs adjacents a "self".
    #
    #     :param groupe: groupe de blocs a tester pour voir s'ils sont adjacents a "self"
    #     :return: groupe de blocs adjacents a "self"
    #     """
    #     rect = self.homotetie(self.rect, 3)
    #     adjacents = []
    #     groupe_ = groupe
    #     if self in groupe_:
    #         groupe_.remove(self)
    #     for bloc in groupe_:
    #         if rect.collidepoint(bloc.rect.center):
    #             adjacents.append(bloc)
    #     return adjacents

    def blocs_collisiones(self, groupe):
        """
        Renvoie les blocs collisiones par le bloc.

        :param groupe: groupe de blocs contre lequel verifier les collisions
        :return: blocs collisiones
        """
        blocs = pygame.sprite.spritecollide(self, groupe, dokill=False)
        if self in blocs:
            blocs.remove(self)
        return blocs

    def collision(self, groupe):
        return False

    @classmethod
    def vecteur(cls, direction):
        if direction == ORIENTATION.DROITE:
            vecteur = array([1, 0])
        elif direction == ORIENTATION.GAUCHE:
            vecteur = array([-1, 0])
        elif direction == ORIENTATION.HAUT:
            vecteur = array([0, -1])
        elif direction == ORIENTATION.BAS:
            vecteur = array([0, 1])
        else:
            raise ValueError("La direction est invalide")
        vecteur *= cls.TAILLE
        return vecteur

    def bouger(self, direction, groupe):
        """
            Fait bouger le personnage dans la direction "direction".

            :param direction: direction dans laquelle avancer
            :return: "None"
            """
        if not self.a_deja_bouge:
            self.orientation = direction
            self.ancien_rect = self.rect  # Enregistre la position precedente du personnage pour pouvoir revenir en arriere
            self.rect = self.rect.move(*self.vecteur(direction))  # L'asterisque permet de passer un tuple a la place de plusieurs arguments
            est_revenu = self.collision(groupe)
            a_bouge = not est_revenu
            if a_bouge:
                self.nombre_actions_cycle += 1
        else:
            a_bouge = False
        return a_bouge

    def revenir(self):
        """
        Annule le dernier mouvement du personnage.

        :return: "None"
        """
        self.rect = self.ancien_rect

    def tuer(self):
        """
        Methode appelee lorsque le bloc se fait tuer.

        :return: "None"
        """
        self.kill()  # TODO : ajouter une animation pour chaque type de bloc


class Personnage(Bloc):
    """
    Classe permettant de representer un personnage.
    """

    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self.est_mort = False
        self.orientation = ORIENTATION.DROITE
        self.etait_en_mouvement = False
        self.diamants_ramasses = 0
        self.terre_creusee = 0

    def collision(self, groupe):
        """
        Methode gerant les collisions entre le personnage et les autres blocs.

        :param groupe: groupe de blocs potentiellement collisionnes
        :return: "None"
        """
        est_revenu = False
        blocs = self.blocs_collisiones(groupe)  # cherches les blocs qui sont en collision avec le personnage
        for bloc in blocs:
            type_de_bloc = bloc.__class__
            if type_de_bloc == Caillou:
                succes = self.pousser_caillou(bloc, groupe)
                if not succes:
                    self.revenir()
                    est_revenu = True
            elif type_de_bloc == Terre:
                self.creuser_terre(bloc)
            elif type_de_bloc == Mur:
                self.revenir()
                est_revenu = True
            elif type_de_bloc == Diamant:
                self.ramasser_diamant(bloc)
            elif type_de_bloc == Porte:
                if not bloc.est_activee:
                    self.revenir()
                    est_revenu = True
        return est_revenu



    def creuser_terre(self, terre):
        terre.tuer()
        self.terre_creusee += 1

    def ramasser_diamant(self, diamant):
        diamant.tuer()
        self.diamants_ramasses += 1

    def pousser_caillou(self, caillou, groupe):
        succes = caillou.etre_pousse(self.orientation, groupe)
        return succes

    def bouger(self, direction, groupe):
        return Bloc.bouger(self, direction, groupe)

    def tuer(self):
        self.est_mort = True
        print("mort")


class Terre(Bloc):
    """
    Classe permettant de representer de la terre.
    """


class BlocTombant(Bloc):
    """
    Classe permettant de gerer les blocs qui tombent (caillou et diamant)
    """
    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self.tombe = False

    def actualiser(self, groupe):
        Bloc.actualiser(self, groupe)
        self.tomber(groupe)

    def revenir(self):
        Bloc.revenir(self)

    def collision(self, groupe):
        blocs = self.blocs_collisiones(groupe)  # cherches les blocs qui sont en collision avec le caillou
        if len(blocs) != 0:
            for bloc in blocs:
                type_de_bloc = bloc.__class__
                if type_de_bloc in (Caillou, Diamant, Entree, Sortie):
                    pass
                elif type_de_bloc == Personnage:
                    if self.tombe:
                        bloc.tuer()
            self.revenir()
            est_revenu = True
        else:
            est_revenu = False
        return est_revenu

    def tomber(self, groupe):
        tombe = self.bouger(ORIENTATION.BAS, groupe)
        self.tombe = tombe
        return tombe


class Caillou(BlocTombant):
    """
    Classe permettant de representer un caillou.
    """

    def __init__(self, x, y):
        BlocTombant.__init__(self, x, y)

    def bouger(self, direction, groupe):
        return Bloc.bouger(self, direction, groupe)

    def etre_pousse(self, direction, groupe):
        """
        gere le mouvement du caillou lorsqu'il est pousse
        :param groupe: groupe de blocs contre lequel tester les collisions
        :param direction: direction dans laquelle le caillou est pousse (=vecteur direction personnage)
        :return: "None"
        """
        if direction in (ORIENTATION.GAUCHE, ORIENTATION.DROITE):
            if self.tomber(groupe):
                return True
            return self.bouger(direction, groupe)
        return False


class Diamant(BlocTombant):
    """
    Classe permettant de representer un diamant.
    """
    def __init__(self, x, y):
        BlocTombant.__init__(self, x, y)


class Mur(Bloc):
    """
    Classe permetant de representer un bout de mur.
    """


class Porte(Bloc):
    """
    Classe permettant de representer une porte de maniere generique.
    """
    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self._est_activee = False

    @property
    def est_activee(self):
        """
        Propriete permettant de savoir si la porte est activee.

        :return: booleen indiquant si la porte est activee
        """
        return self._est_activee

    @est_activee.setter
    def est_activee(self, activee):
        activation = not self._est_activee and activee
        desactivation = self._est_activee and not activee
        self._est_activee = activee
        if activation:
            pass
        elif desactivation:
            pass
        # TODO : ajouter animation de changement d'etat

    def activer(self):
        """
        Methode de convenance permettant d'activer la porte.

        :return: "None"
        """
        self.est_activee = True

    def desactiver(self):
        """
        Methode de convenance permettant de desactiver la porte.

        :return: "None"
        """
        self.est_activee = False


class Entree(Porte):
    """
    Classe permettant de representer une porte d'entree.
    """
    def __init__(self, x, y):
        Porte.__init__(self, x, y)
        self.est_activee = True


class Sortie(Porte):
    """
    Classe permettant de representer une porte de sortie.
    """
    def __init__(self, x, y):
        Porte.__init__(self, x, y)
        self.est_activee = False
