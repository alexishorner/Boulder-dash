from Blocs import *

LARGEUR = 500
HAUTEUR = 500
ecran = display.set_mode((LARGEUR, HAUTEUR))


def enlever_extremite(chaine, gauche=True, caracteres_a_enlever=("\n", " ")):
    if gauche:
        debut = 0
        increment = 1
    else:
        debut = len(chaine)-1
        increment = -1

    i = debut
    while 0 <= i < len(chaine):
        if chaine[i] not in caracteres_a_enlever:
            break
        i += increment

    if gauche:
        return chaine[i+1:]
    return chaine[:i]


def enlever_extremites(chaine, caracteres_a_enlever=("\n", " ")):
    temp = enlever_extremite(chaine, gauche=True, caracteres_a_enlever=caracteres_a_enlever)
    return enlever_extremite(temp, gauche=False, caracteres_a_enlever=caracteres_a_enlever)


class Niveau:
    def __init__(self, ascii, numero=None):
        self.numero = numero
        self.ascii = ascii


class Carte:
    ASCII_VERS_BLOC = {"O": Caillou,     # Ressemble a un caillou
                       "#": Mur,         # Ressemble a une barriere -> mur
                       "P": Personnage,  # "P" comme "Personnage"
                       "[": Entree,      # Forme rectangulaire comme une porte. Crochet ouvrant -> entree
                       "]": Sortie,      # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,       # Ressemble aux points dans Packman et est centre, contrairement au point "."
                       "$": Diamant}     # Dollar fait penser a argent -> diamant

    def __init__(self, niveau):
        if niveau.__class__ == Niveau:
            niveau_ascii = niveau.ascii
        elif niveau.__class__ == str:
            niveau_ascii = niveau
        else:
            raise TypeError("Erreur, le niveau doit etre de type \"Niveau\" ou \"str\"")

        niveau_ascii = enlever_extremites(niveau_ascii)
        self.blocs = sprite.Group()
        for y, ligne_ascii in enumerate(niveau_ascii.split("\n")):
            for x, bloc_ascii in enumerate(ligne_ascii):
                self.blocs.add(self.ASCII_VERS_BLOC[bloc_ascii]())

    def dessiner(self):
        self.blocs.draw(ecran)
