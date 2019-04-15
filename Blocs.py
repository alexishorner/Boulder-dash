from pygame import sprite, image, display

DOSSIER_IMAGES = "img/"


class Bloc(sprite.Sprite):
    """
    Classe de base pour tous les blocs.
    """
    TAILLE = 10
    NOM_IMAGE = "mono-unknown.png"

    def __init__(self, ecran):
        sprite.Sprite.__init__(self)  # On appelle le constructeur de la classe mere
        self.image = image.load(self.chemin_image()).convert_alpha()
        self.ecran = ecran
        self.rect = self.image.get_rect()

    def update(self):
        pass

    @classmethod
    def chemin_image(cls):
        return DOSSIER_IMAGES + cls.NOM_IMAGE

    def blocs_collisiones(self, groupe):
        blocs = sprite.spritecollide(self, groupe, dokill=False)
        if self in blocs:
            blocs.remove(self)
        return blocs

    def collision(self, groupe):
        pass

    def bouger(self):
        pass

    def tuer(self):
        pass


class Personnage(Bloc):
    NOM_IMAGE = "personnage.png"

    def collision(self, groupe):
        blocs = self.blocs_collisiones(groupe)
        for bloc in blocs:
            type_de_bloc = bloc.__class__
            if type_de_bloc == Caillou:
                if bloc.tombe:
                    self.tuer()
            elif type_de_bloc == Terre:
                self.creuser_terre(bloc)
            elif type_de_bloc == Mur:
                self.revenir()

    def creuser_terre(self, terre):
        pass

    def revenir(self):
        """
        Annule le dernier mouvement du personnage.

        :return: "None"
        """
        pass


class Caillou(Bloc):
    NOM_IMAGE = "caillou.jpg"

    def __init__(self, ecran):
        Bloc.__init__(self, ecran)
        self.tombe = False


class Terre(Bloc):
    NOM_IMAGE = "terre.PNG"

class Diamant(Bloc):
    NOM_IMAGE = "diamant.jpg"


class Mur(Bloc):
    NOM_IMAGE = "mur.png"


class Porte(Bloc):
    NOM_IMAGE = "porte.png"


class Entree(Porte):
    pass


class Sortie(Porte):
    pass
