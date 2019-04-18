"""
Module stockant les donnees du jeu.
"""

from blocs import *


def enlever_extremite(chaine, extremite_gauche=True, caracteres_a_enlever=("\n", " ")):
    """
    Enleve des caracteres se trouvant a une extremite d'une chaine de caracteres.

    Exemple :
    extremite_gauche = False
    caracteres_a_enlever == ("\n", "_")
    chaine == "_\n__\n_\nCeci_est\n_une_chaine\n_d'exemple__\n\n____\n"
              |gauche    |            milieu             |      droite|
              ^----------------chaine de caracteres-------------------^

    retour == "_\n__\n_\nCeci_est\n_une_chaine\n_d'exemple"

    :param chaine: chaine de caracteres a traiter
    :param extremite_gauche: determine si il faut enlever les caracteres a l'extremite gauche ou droite de la chaine
    :param caracteres_a_enlever: iterable contenant les caracteres devant etre enleves
    :return: chaine de caracteres apres avoir enleve les caracteres specifies a l'extremite demandee
    """
    if extremite_gauche:
        debut = 0  # On commence a gauche (i.e. au caractere 0) de la chaine de caracteres
        increment = 1  # On lit de gauche a droite
    else:
        debut = len(chaine)-1  # On commence a droite (i.e. au dernier caractere) de la chaine de caracteres
        increment = -1  # On lit de droite a gauche

    i = debut
    while 0 <= i < len(chaine):
        if chaine[i] not in caracteres_a_enlever:
            break
        i += increment

    if extremite_gauche:
        return chaine[i:]
    return chaine[:i+1]


def enlever_extremites(chaine, caracteres_a_enlever=("\n", " ")):
    temp = enlever_extremite(chaine, extremite_gauche=True, caracteres_a_enlever=caracteres_a_enlever)
    return enlever_extremite(temp, extremite_gauche=False, caracteres_a_enlever=caracteres_a_enlever)


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
                       "*": Terre,       # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant}     # Dollar fait penser a argent -> diamant

    def __init__(self, niveau):
        self.blocs = self.niveau_vers_blocs(niveau)
        self.personnage = self.trouver_personnage(self.blocs)
        if self.personnage is None:
            raise LookupError("Pas de personnage trouve.")

    @staticmethod
    def trouver_personnage(blocs):
        for bloc in blocs:
            if bloc.__class__ == Personnage:
                personnage = bloc
                return personnage

    @classmethod
    def niveau_vers_blocs(cls, niveau):
        """
        Prend en entree un niveau et cree un groupe de blocs ayant chacun le type et la position dictee par le niveau.

        :param niveau: niveau a interpreter
        :return: groupe de blocs initialises avec la bonne position et le bon type
        """
        if niveau.__class__ == Niveau:
            niveau_ascii = niveau.ascii
        elif niveau.__class__ == str:
            niveau_ascii = niveau
        else:
            raise TypeError("Erreur, le niveau doit etre de type \"Niveau\" ou \"str\"")

        niveau_ascii = enlever_extremites(niveau_ascii).replace(" ", "")
        blocs = sprite.Group()
        for y, ligne_ascii in enumerate(niveau_ascii.split("\n")):
            for x, bloc_ascii in enumerate(ligne_ascii):
                bloc = cls.ASCII_VERS_BLOC[bloc_ascii](x, y)
                blocs.add(bloc)
        return blocs

    def dessiner(self, ecran):
        self.blocs.remove(self.personnage)
        self.blocs.draw(ecran)  # Dessine les blocs autres que le personnage en premier
        self.blocs.add(self.personnage)  # TODO: Tout dessiner en meme temps, le personnage n'a pas besoin d'etre au premier plan
        ecran.blit(self.personnage.image, self.personnage.rect)  # Dessine le personnage en dernier pour qu'il soit au premier plan


class Constantes:
    LARGEUR_ECRAN = 1920
    HAUTEUR_ECRAN = 1080
    NIVEAUX = (Niveau("""
                        ############
                        #***O***O*$#
                        #***OOP**[##
                        #$$$#******#
                        #OOOO*$]***#
                        #**********#
                        #**********#
                        #**********#
                        #**********#
                        #**********#
                        ############
                                    """, 1),)
