"""
Module gerant les differentes sortes de blocs pouvant etre affiches a l'ecran
"""
# TODO :
#   - animations
#   - afficher score, temps, vies
#   - recommencer niveau sans crer nouveau personnage
#   - son
#   - menu
#   - score
#   - niveaux predefinis
#   - editeur de niveaux :
#       - ajouter/enlever lignes/colonnes
#       - sauvegarder niveaux dans fichier
#   Facultatif :
#       - ameliorer ajouts blocs par glissement (intersection segment/rectangles)
#       - generateur de niveaux automatique
#       - mechants


from coeur import *


class Bloc(pygame.sprite.Sprite):  # Pas besoin d'heriter d'"object", car "pygame.sprite.Sprite" est une classe de nouveau style
    """
    Classe de base pour tous les blocs.
    """
    PEUT_SE_DEPLACER = False

    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mere
        image = IMAGES[self.__class__.__name__]
        self.image = pygame.transform.scale(image, (rect.width, rect.height))
        self.rect = self.image.get_rect()
        self.rect.x = rect.x
        self.rect.y = rect.y
        self.z = 0
        self.a_deja_bouge = not self.PEUT_SE_DEPLACER  # Les blocs ne pouvant pas se deplacer ont deja un mouvement traite
        self.orientation = ORIENTATIONS.DROITE
        self.est_mort = False
        self.doit_bouger = False

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

    def actualiser(self):
        pass
    # TODO : gerer les autres actions (comme tomber)

    def terminer_cycle(self):
        self.a_deja_bouge = not self.PEUT_SE_DEPLACER  # Les blocs ne pouvant pas se deplacer ont deja un mouvement traite

    def bouger(self, direction):
        """
            Fait bouger le personnage dans la direction "direction".

            :param direction: direction dans laquelle avancer
            :return: "None"
            """
        self.orientation = direction

    def tuer(self):
        """
        Methode appelee lorsque le bloc se fait tuer.

        :return: "None"
        """
        self.est_mort = True  # TODO : ajouter une animation pour chaque type de bloc


class Personnage(Bloc):
    """
    Classe permettant de representer un personnage.
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

        # self.soncreuser = pygame.mixer.Sound()
        # self.sontcaillou = pygame.mixer.Sound()
        # self.sonbouger = pygame.mixer.Sound()e
    def creuser_terre(self, terre):
        terre.tuer()
        SONS.CREUSER_TERRE.play()
        self.terre_creusee += 1

    def ramasser_diamant(self, diamant):
        diamant.tuer()
        SONS.RAMASSER_DIAMANT.play()
        diamant.ramasse = True
        self.diamants_ramasses += 1

    def pousser(self, caillou, direction):
        caillou.etre_pousse()
        SONS.POUSSER_CAILLOU.play()
        self.bouger(direction)

    def bouger(self, direction):
        super(Personnage, self).bouger(direction)
        SONS.BOUGER.play()

    def tuer(self):
        super(Personnage, self).tuer()
        SONS.TUER.play()

class Terre(Bloc):
    """
    Classe permettant de representer de la terre.
    """


class BlocTombant(Bloc):
    """
    Classe permettant de gerer les blocs qui tombent (caillou et diamant)
    """
    PEUT_SE_DEPLACER = True
    INERTIE = 1


    def __init__(self, rect):
        super(BlocTombant, self).__init__(rect)
        self.tombe = False
        self.est_tombe = False
        self.pouvait_tomber = False
        self.coups_avant_tomber = self.INERTIE
        self.a_tue = False

    def tomber(self):
        if self.coups_avant_tomber > 0:
            self.coups_avant_tomber -= 1
        else:
            self.est_tombe = True
        self.pouvait_tomber = True

    def terminer_cycle(self):
        super(BlocTombant, self).terminer_cycle()
        self.tombe = self.est_tombe
        if not self.pouvait_tomber:
            self.coups_avant_tomber = self.INERTIE
        self.est_tombe = self.pouvait_tomber = False


class Caillou(BlocTombant):
    """
    Classe permettant de representer un caillou.
    """
    def __init__(self, rect):
        super(Caillou, self).__init__(rect)
        self.coups_avant_etre_pousse = self.INERTIE
        self.est_pousse = False
        self.a_collisionne = False


    def bouger(self, direction):
        super(Caillou, self).bouger(direction)

    def tomber(self):
        super(Caillou, self).tomber()
        if (not self.est_tombe and not self.a_tue)  or self.a_collisionne:
            SONS.CAILLOU_TOMBE.play()

    def etre_pousse(self):
        self.est_pousse = True
        if self.coups_avant_etre_pousse > 0:
            self.coups_avant_etre_pousse -= 1

    def terminer_cycle(self):
        super(Caillou, self).terminer_cycle()
        if not self.est_pousse:
            self.coups_avant_etre_pousse = self.INERTIE
        self.est_pousse = False


class Diamant(BlocTombant):
    """
    Classe permettant de representer un diamant.
    """
    def __init__(self, rect):
        super(Diamant, self).__init__(rect)
        self.ramasse = False
    def tomber(self):
        super(Diamant, self).tomber()
        if self.ramasse == False: #comme ca on a pas le bruit du diamant qui tombe lorsqu'on le ramasse
            SONS.DIAMANT_TOMBE1.play()


class Mur(Bloc):
    """
    Classe permetant de representer un bout de mur.
    """


class Sortie(Bloc):
    """
    Classe permettant de representer une porte de maniere generique.
    """
    def __init__(self, rect):
        super(Sortie, self).__init__(rect)
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

class Explosion:
    """
    Classe permettant de representer une explosion
    """