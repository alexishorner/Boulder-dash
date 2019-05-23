# coding: utf-8
"""
Module gerant les differentes sortes de blocs pouvant etre affiches a l'ecran
"""
# TODO :
#   Facultatif :
#       - ameliorer ajouts blocs par glissement (intersection segment/rectangles)
#       - generateur de niveaux automatique
#       - animations
#       - mechants


from coeur import *


class Bloc(pygame.sprite.Sprite):  # Pas d'héritage d'"object", "pygame.sprite.Sprite" est une classe de nouveau style
    """
    Classe de base pour tous les blocs.
    """
    PEUT_SE_DEPLACER = False  # Variable de classe indiquant si les instances d'une certaine classe sont bougeables

    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mère
        image = IMAGES[self.__class__.__name__]
        self.image = pygame.transform.scale(image, rect.size)
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.z = 0  # La coordonnée z définit quel bloc apparaît devant sur l'écran en cas de superposition de blocs.
        self.a_deja_bouge = not self.PEUT_SE_DEPLACER
        self.orientation = ORIENTATIONS.DROITE
        self.est_mort = False
        self.doit_bouger = False

    @property
    def taille(self):
        """
        Propriété permettant de gérer la taille du rectangle et de l'image du bloc en même temps.

        :return: Taille du rectangle du bloc.
        """
        return self.rect.size

    @taille.setter
    def taille(self, nouvelle):
        self.rect.size = nouvelle
        self.image = pygame.transform.scale(self.image, nouvelle)

    @property
    def rect_hashable(self):
        """
        Permet d'utiliser le rectangle comme cle de dictionnaire.

        :return: Copie de self.rect, mais hashable.
        """
        return Rectangle(self.rect)

    def terminer_cycle(self):
        """
        Méthode appelée à chaque fin de boucle de jeu.

        :return: "None"
        """
        self.a_deja_bouge = not self.PEUT_SE_DEPLACER  # On considère que les blocs ne pouvant pas se déplacer on déjà bougé

    def bouger(self, direction):
        """
            Fait bouger le personnage dans la direction "direction".

            :param direction: direction dans laquelle avancer
            :return: "None"
            """
        self.orientation = direction
        self.a_deja_bouge = True

    def tuer(self):
        """
        Methode appelee lorsque le bloc se fait tuer.

        :return: "None"
        """
        self.est_mort = True  # TODO : ajouter une animation pour chaque type de bloc


class Personnage(Bloc):
    """
    Classe permettant de représenter un personnage.
    """
    PEUT_SE_DEPLACER = True

    def __init__(self, rect):
        super(Personnage, self).__init__(rect)
        self.mouvement_en_cours = None
        self.orientation = ORIENTATIONS.DROITE
        self.etait_en_mouvement = False
        self.diamants_ramasses = 0
        self.terre_creusee = 0
        self.caillou_pousse = None
        self.z = 1

    def creuser_terre(self, terre):
        """
        Méthode appelée lorsque le personnage creuse de la terre. Elle permet de jouer un son et de compter la quantité
        de terre creusée.

        :param terre: Instance de "Terre" représentant le bloc de terre à creuser
        :return: "None"
        """
        terre.tuer()
        SONS.CREUSER_TERRE.play()
        self.terre_creusee += 1

    def ramasser_diamant(self, diamant):
        """
        Méthode appelée lorsque le personnage ramasse un diamant.

        :param diamant: Instance de "Diamant" représentant le diamant à ramasser.
        :return:
        """
        diamant.tuer()
        SONS.RAMASSER_DIAMANT.play()
        diamant.ramasse = True
        self.diamants_ramasses += 1

    def pousser(self, caillou, direction):
        """
        Méthode appelée lorsque le personnage pousse un caillou.

        :param caillou: Instance de "Caillou" représentant le caillou à pousser
        :param direction: Valeur de l'énumération "ORIENTATIONS" indiquant le sens et la direction dans lesquels le
        caillou doit être poussé.
        :return: "None"
        """
        caillou.etre_pousse()
        SONS.POUSSER_CAILLOU.play()
        self.bouger(direction)

    def bouger(self, direction):
        """
        Méthode appelée lorsque le personnage bouge.

        :param direction: Valeur de l'énumération "ORIENTATIONS" indiquant le sens et la direction dans lesquels le
        personnage doit bouger.
        :return:
        """
        super(Personnage, self).bouger(direction)
        SONS.BOUGER.play()

    def tuer(self):
        """
        Réimplémentation de la méthode "tuer" de la classe "Bloc".

        Elle joue un son indiquant la mort du personnage.

        :return: "None"
        """
        super(Personnage, self).tuer()
        SONS.TUER.play()


class Terre(Bloc):
    """
    Classe permettant de représenter de la terre.
    """


class BlocTombant(Bloc):
    """
    Classe permettant de gérer les blocs qui tombent (caillou et diamant)
    """
    PEUT_SE_DEPLACER = True
    INERTIE = 1  # Nombre de tours de retard sur les mouvements

    def __init__(self, rect):
        super(BlocTombant, self).__init__(rect)
        self.tombe = False
        self.est_tombe = False
        self.pouvait_tomber = False
        self.coups_avant_tomber = self.INERTIE
        self.a_tue = False

    def tomber(self):
        """
        Méthode appelée lorsque le bloc tombe.

        :return: "None"
        """
        if self.coups_avant_tomber > 0:
            self.coups_avant_tomber -= 1
        else:
            self.est_tombe = True
        self.pouvait_tomber = True

    def terminer_cycle(self):
        """
        Réimplémentation de la méthode "terminer_cycle" de la classe "Bloc".
        :return:
        """
        super(BlocTombant, self).terminer_cycle()
        self.tombe = self.est_tombe  # Si le bloc est tombé à ce tour, il peut tuer le personnage aux prochains tours.
        if not self.pouvait_tomber:  # Si le bloc avait des bloc l'empêchant de bouger
            self.coups_avant_tomber = self.INERTIE
        self.est_tombe = self.pouvait_tomber = False


class Caillou(BlocTombant):
    """
    Classe permettant de représenter un caillou.
    """
    def __init__(self, rect):
        super(Caillou, self).__init__(rect)
        self.coups_avant_etre_pousse = self.INERTIE
        self.est_pousse = False

    def tomber(self):
        super(Caillou, self).tomber()
        if self.tombe and not self.est_tombe and not self.a_tue:
            SONS.CAILLOU_TOMBE.play()

    def etre_pousse(self):
        self.est_pousse = True
        if self.coups_avant_etre_pousse > 0:
            self.coups_avant_etre_pousse -= 1
        else:
            SONS.POUSSER_CAILLOU.play()

    def taper_objet(self):
        """
        Méthode appelée lorsque le caillou tape un objet en tombant.

        :return: "None"
        """
        SONS.CAILLOU_TOMBE.play()

    def terminer_cycle(self):
        """
        Réimplémentation de la méthode "terminer_cycle" de la classe "BlocTombant".

        :return: "None"
        """
        super(Caillou, self).terminer_cycle()
        if not self.est_pousse:
            self.coups_avant_etre_pousse = self.INERTIE
        self.est_pousse = False


class Diamant(BlocTombant):
    """
    Classe permettant de représenter un diamant.
    """
    def __init__(self, rect):
        super(Diamant, self).__init__(rect)
        self.ramasse = False

    def tomber(self):
        """
        Réimplémentation de la méthode "tomber" de la classe "BlocTombant"

        :return: "None"
        """
        super(Diamant, self).tomber()
        if not self.ramasse and (not self.est_tombe and not self.a_tue) : #comme ca on a pas le bruit du diamant qui tombe lorsqu'on le ramasse
            SONS.DIAMANT_TOMBE1.play()

    def taper_objet(self):
        """
        Méthode appelée lorsque le diamant tape un objet en tombant.

        :return: "None"
        """
        SONS.DIAMANT_TOMBE1.play()


class Mur(Bloc):
    """
    Classe permettant de représenter un bout de mur.
    """


class Sortie(Bloc):
    """
    Classe permettant de représenter une porte de sortie
    """
    def __init__(self, rect):
        super(Sortie, self).__init__(rect)
        self._est_activee = False

    @property
    def est_activee(self):
        """
        Propriété permettant de savoir si la porte est activée.

        :return: booléen indiquant si la porte est activée
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
        Méthode de convenance permettant d'activer la porte.

        :return: "None"
        """
        self.est_activee = True

    def desactiver(self):
        """
        Méthode de convenance permettant de désactiver la porte.

        :return: "None"
        """
        self.est_activee = False


class Explosion(Bloc):
    """
    Classe permettant de représenter une explosion
    """
