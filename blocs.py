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


# class Coordonnees(list):
#     def __init__(self, x, y):
#         super(Coordonnees, self).__init__([x, y])
#
#     @property
#     def x(self):
#         return self[0]
#
#     @x.setter
#     def x(self, valeur):
#         self[0] = valeur
#
#     @x.deleter
#     def x(self):
#         raise AttributeError("L'attribut ne peut pas etre supprime.")
#
#     @property
#     def y(self):
#         return self[1]
#
#     @y.setter
#     def y(self, valeur):
#         self[1] = valeur
#
#     @y.deleter
#     def y(self):
#         raise AttributeError("L'attribut ne peut pas etre supprime.")
#
#     def __mul__(self, autre):
#         return Coordonnees(self.x * autre, self.y * autre)
#
#     def __div__(self, autre):
#         return Coordonnees(self.x / autre, self.y / autre)


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


class Bloc(pygame.sprite.Sprite, object):
    """
    Classe de base pour tous les blocs.
    """
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mere
        image = IMAGES[self.__class__.__name__]
        self.image = pygame.transform.scale(image, (rect.width, rect.height))
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.ancien_rect = self.rect.copy()
        self.z = 0
        self.nombre_actions_cycle = 0
        self.orientation = ORIENTATIONS.DROITE

    @property
    def rect_hashable(self):
        """
        Permet d'utiliser le rectangle comme cle de dictionnaire.

        :return: Copie de self.rect, mais hashable.
        """
        return Rectangle(self.rect)

    @rect_hashable.setter
    def rect_hashable(self, nouveau):
        raise AttributeError("Le rectangle hashable n'est pas modifiable, utiliser l'attribut \"rect\" a la place.")

    @rect_hashable.deleter
    def rect_hashable(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")
        
    @property
    def a_deja_bouge(self):
        return bool(self.nombre_actions_cycle)

    def actualiser(self):
        pass
    # TODO : gerer les autres actions (comme tomber)

    def terminer_cycle(self):
        self.nombre_actions_cycle = 0

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
        if direction == ORIENTATIONS.DROITE:
            vecteur = array([1, 0])
        elif direction == ORIENTATIONS.GAUCHE:
            vecteur = array([-1, 0])
        elif direction == ORIENTATIONS.HAUT:
            vecteur = array([0, -1])
        elif direction == ORIENTATIONS.BAS:
            vecteur = array([0, 1])
        else:
            raise ValueError("La direction est invalide")
        vecteur *= DIMENSIONS.LARGEUR_CASE
        return vecteur

    def bouger(self, direction):
        """
            Fait bouger le personnage dans la direction "direction".

            :param direction: direction dans laquelle avancer
            :return: "None"
            """
        if not self.a_deja_bouge:
            self.orientation = direction
            self.ancien_rect = self.rect  # Enregistre la position precedente du personnage pour pouvoir revenir en arriere
            self.rect.move_ip(*self.vecteur(direction))  # L'asterisque permet de passer un tuple a la place de plusieurs arguments
            self.nombre_actions_cycle += 1
            a_bouge = True
        else:
            a_bouge = False
        return a_bouge

    def revenir(self):
        """
        Annule le dernier mouvement du personnage.

        :return: "None"
        """
        self.rect.x, self.rect.y = self.ancien_rect.x, self.ancien_rect.y

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

    def __init__(self, rect):
        super(Personnage, self).__init__(rect)
        self.est_mort = False
        self.orientation = ORIENTATIONS.DROITE
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

    def bouger(self, direction):
        return Bloc.bouger(self, direction)

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
    def __init__(self, rect):
        super(BlocTombant, self).__init__(rect)
        self.tombe = False

    def actualiser(self):
        Bloc.actualiser(self)
        self.tomber()

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

    def tomber(self):
        tombe = self.bouger(ORIENTATIONS.BAS)
        self.tombe = tombe
        return tombe


class Caillou(BlocTombant):
    """
    Classe permettant de representer un caillou.
    """

    def __init__(self, rect):
        BlocTombant.__init__(self, rect)

    def bouger(self, direction):
        return Bloc.bouger(self, direction)

    def etre_pousse(self, direction, groupe):
        """
        gere le mouvement du caillou lorsqu'il est pousse
        :param groupe: groupe de blocs contre lequel tester les collisions
        :param direction: direction dans laquelle le caillou est pousse (=vecteur direction personnage)
        :return: "None"
        """
        if direction in (ORIENTATIONS.GAUCHE, ORIENTATIONS.DROITE):
            if self.tomber():
                return True
            return self.bouger(direction)
        return False


class Diamant(BlocTombant):
    """
    Classe permettant de representer un diamant.
    """
    def __init__(self, rect):
        BlocTombant.__init__(self, rect)


class Mur(Bloc):
    """
    Classe permetant de representer un bout de mur.
    """


class Porte(Bloc):
    """
    Classe permettant de representer une porte de maniere generique.
    """
    def __init__(self, rect):
        super(Porte, self).__init__(rect)
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
    def __init__(self, rect):
        super(Entree, self).__init__(rect)
        self.est_activee = True


class Sortie(Porte):
    """
    Classe permettant de representer une porte de sortie.
    """
    def __init__(self, rect):
        super(Sortie, self).__init__(rect)
        self.est_activee = False
