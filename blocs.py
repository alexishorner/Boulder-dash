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


class Bloc(pygame.sprite.Sprite):
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

    def actualiser(self, groupe):
        pass
    # TODO : gerer les autres actions (comme tomber)

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

    def blocs_adjacents(self, groupe):
        """
        Renvoie un groupe contenant les blocs adjacents a "self".

        :param groupe: groupe de blocs a tester pour voir s'ils sont adjacents a "self"
        :return: groupe de blocs adjacents a "self"
        """
        rect = self.homotetie(self.rect, 3)
        adjacents = []
        groupe_ = groupe
        if self in groupe_:
            groupe_.remove(self)
        for bloc in groupe_:
            if rect.collidepoint(bloc.rect.center):
                adjacents.append(bloc)
        return adjacents

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
        pass

    def bouger(self, direction, groupe):
        """
            Fait bouger le personnage dans la direction "direction".

            :param direction: direction dans laquelle avancer
            :return: "None"
            """
        self.orientation = direction
        if direction == ORIENTATION.DROITE:
            vecteur = array([1, 0])
        elif direction == ORIENTATION.GAUCHE:
            vecteur = array([-1, 0])
        elif direction == ORIENTATION.HAUT:
            vecteur = array([0, -1])
        elif direction == ORIENTATION.BAS:
            vecteur = array([0, 1])
        else:
            raise ValueError("L'orientation est invalide")
        vecteur *= self.TAILLE
        self.ancien_rect = self.rect  # Enregistre la position precedente du personnage pour pouvoir revenir en arriere
        self.rect = self.rect.move(*vecteur)  # L'asterisque permet de passer un tuple a la place de plusieurs arguments
        self.collision(groupe)

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
        self.orientation = ORIENTATION.DROITE
        self.ancien_rect = self.rect
        self.etait_en_mouvement = False
        self.diamants_ramasses = 0
        self.terre_creusee = 0

    def collision(self, groupe):
        """
        Methode gerant les collisions entre le personnage et les autres blocs.

        :param groupe: groupe de blocs potentiellement collisionnes
        :return: "None"
        """
        blocs = self.blocs_collisiones(groupe)  # cherches les blocs qui sont en collision avec le personnage
        for bloc in blocs:
            type_de_bloc = bloc.__class__
            if type_de_bloc == Caillou:
                if bloc.tombe:
                    self.tuer()
                else:
                    self.pousser_caillou(bloc)
            elif type_de_bloc == Terre:
                self.creuser_terre(bloc)
            elif type_de_bloc == Mur:
                self.revenir()
            elif type_de_bloc == Diamant:
                self.ramasser_diamant(bloc)

    def creuser_terre(self, terre):
        terre.tuer()
        self.terre_creusee += 1

    def ramasser_diamant(self, diamant):
        diamant.tuer()
        self.diamants_ramasses += 1

    def pousser_caillou(self, caillou, direction):
        self.revenir()
        caillou.etre_pousse(self, caillou, direction)
        caillou.collision()


    def bouger(self, direction, groupe):
        Bloc.bouger(self, direction, groupe)

    def revenir(self):
        pass


class Terre(Bloc):
    """
    Classe permettant de representer de la terre.
    """

# TODO : creer une classe englobant les caracteristiques communes a la classe "Caillou" et "Diamant", comme tomber
class Caillou(Bloc):
    """
    Classe permettant de representer un caillou.
    """

    def __init__(self, x, y):
        Bloc.__init__(self, x, y)
        self.tombe = False

    def bouger(self, direction):
       pass

    def etre_pousse(self, direction):
        """
        gere le mouvement du caillou lorsqu'il est pousse
        :param direction: direction dans laquelle le caillou est pousse (=vecteur direction personnage)
        :return: "None"
        """
        self.move(direction)

    def collision(self, groupe):
        """
        Methode gerant les collisions entre un caillou et les autres blocs.

        :param groupe: groupe de blocs potentiellement collisionnes
        :return: "None"
        """
        blocs = self.blocs_collisiones(groupe)  # cherche les blocs qui sont en collision avec le personnage
        if blocs == []:
            pass
        else:
            self.revenir()

    def actualiser(self, groupe):
        pass


class Diamant(Bloc):
    """
    Classe permettant de representer un diamant.
    """


class Mur(Bloc):
    """
    Classe permetant de representer un bout de mur.
    """


class Porte(Bloc):
    """
    Classe permettant de representer une porte de maniere generique.
    """


class Entree(Porte):
    """
    Classe permettant de representer une porte d'entree.
    """


class Sortie(Porte):
    """
    Classe permettant de representer une porte de sortie.
    """
