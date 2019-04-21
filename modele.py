"""
Module stockant les donnees du jeu.
"""
from blocs import *


def _enlever_extremite(chaine, extremite=ORIENTATION.GAUCHE, caracteres_a_enlever=("\n", " ")):
    """
    Enleve des caracteres se trouvant a une extremite d'une chaine de caracteres.

    Exemple :
    extremite == ORIENTATION.DROITE
    caracteres_a_enlever == ("\n", "_")
    chaine == "_\n__\n_\nCeci_est\n_une_chaine\n_d'exemple__\n\n____\n"
              ^--gauche-^------------milieu--------------^---droite--^

    retour == "_\n__\n_\nCeci_est\n_une_chaine\n_d'exemple"


    Cette fonction n'est pas utile en soit, mais permet de simplifier la fonction
    "enlever_extremites(chaine, caracteres_a_enlever)".

    Le tiret bas "_" au debut du nom de la fonction ci-presente indique qu'elle est destinee a un usage interne
    uniquement (cela empeche par exemple son importation avec un "from modele import *") et sert a empecher la confusion
    de cette fonction avec "enlever_extremites(chaine, caracteres_a_enlever)", dont le nom est tres proche.

    :param chaine: chaine de caracteres a traiter
    :param extremite: determine si il faut enlever les caracteres a l'extremite gauche ou droite de la chaine
    :param caracteres_a_enlever: iterable contenant les caracteres devant etre enleves
    :return: chaine de caracteres apres avoir enleve les caracteres specifies a l'extremite demandee
    """
    if extremite == ORIENTATION.GAUCHE:
        debut = 0  # On commence a gauche (i.e. au caractere 0) de la chaine de caracteres
        increment = 1  # On lit de gauche a droite
    else:
        debut = len(chaine)-1  # On commence a droite (i.e. au dernier caractere) de la chaine de caracteres
        increment = -1  # On lit de droite a gauche

    i = debut
    while 0 <= i < len(chaine):
        if chaine[i] not in caracteres_a_enlever:  # regarde jusqu'ou les caracteres doivent etre enleves
            break
        i += increment

    if extremite == ORIENTATION.GAUCHE:
        return chaine[i:]  # renvoie la chaine de caracteres depuis le caractere i jusqu'a la fin
    return chaine[:i+1]  # renvoie la chaine de caracteres depuis le debut jusqu'au caractere i


def enlever_extremites(chaine, caracteres_a_enlever=("\n", " ")):
    """
    Enleve certains caracteres a chacune des extremites d'une chaine de caracteres.

    :param chaine: chaine de caracteres a traiter
    :param caracteres_a_enlever: iterable contenant les caracteres devant etre enleves
    :return: chaine de caracteres apres avoir enleve les caracteres specifies a chacune des extremites.
    """
    variable_temporaire = _enlever_extremite(chaine, ORIENTATION.GAUCHE, caracteres_a_enlever)  # enleve l'extremite gauche
    return _enlever_extremite(variable_temporaire, ORIENTATION.DROITE, caracteres_a_enlever)  # enleve l'extremite droite


class Niveau:
    """
    Classe permettant de representer un niveau.
    Un niveau est un schema decrivant la position initiale de blocs de types divers.

    Cette classe utilise une chaine de caractere pour stocker le niveau et offre la possibilite de specifier le numero
    du niveau.
    """
    ASCII_VERS_BLOC = {"O": Caillou,     # Ressemble a un caillou
                       "#": Mur,         # Ressemble a une barriere -> mur
                       "P": Personnage,  # "P" comme "Personnage"
                       "[": Entree,      # Forme rectangulaire comme une porte. Crochet ouvrant -> entree
                       "]": Sortie,      # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,       # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant}     # Dollar fait penser a argent -> diamant

    def __init__(self, ascii, numero=None):
        self.numero = numero  # Numero du niveau
        self.ascii = ascii  # Representation du niveau avec des caracteres ascii

    def vers_blocs(self):
        """
        Prend en entree un niveau et cree un groupe de blocs ayant chacun le type et la position dictee par le niveau.

        :param niveau: niveau a interpreter
        :return: groupe de blocs initialises avec la bonne position et le bon type
        """
        niveau_ascii = self.ascii
        niveau_ascii = enlever_extremites(niveau_ascii).replace(" ", "")    # On enleve tous les espaces, ainsi que les
                                                                            # retours a la ligne se trouvant au debut ou
                                                                            # a la fin
        blocs = pygame.sprite.Group()
        for y, ligne_ascii in enumerate(niveau_ascii.split("\n")):
            for x, bloc_ascii in enumerate(ligne_ascii):
                bloc = self.ASCII_VERS_BLOC[bloc_ascii](x, y)   # On convertit chaque caractere en bloc et leur attribue
                                                                # une position initiale
                blocs.add(bloc)
        return blocs

    @classmethod
    def niveau(cls, numero):
        """
        Retourne le niveau ayant le numero "numero".

        :param numero: numero du niveau
        :return: niveau correspondant au numero specifie
        """
        return cls(NIVEAUX[numero-1], numero)


class Carte:
    """
    Classe permettant de representer une carte, c'est-a-dire l'ensemble des blocs presents sur l'ecran.
    """
    def __init__(self, niveau):
        self.blocs = niveau.vers_blocs()
        self.personnage = self.trouver_personnage(self.blocs)
        if self.personnage is None:  # On oblige la presence d'un personnage, car on ne peut pas jouer sans
            raise LookupError("Pas de personnage trouve.")

    @staticmethod
    def trouver_personnage(blocs):
        """
        Cherche dans une liste de blocs la premiere occurrence d'un bloc de type "Personnage".

        :param blocs: Blocs dans lesquels chercher
        :return: Premiere occurrence d'un bloc de type "Personnage"
        """
        for bloc in blocs:
            if bloc.__class__ == Personnage:
                personnage = bloc
                return personnage

    def dessiner(self, ecran):
        """
        Affiche les blocs sur l'ecran.

        :param ecran: Ecran sur lequel dessiner les blocs.
        :return: "None"
        """
        self.blocs.remove(self.personnage)
        self.blocs.draw(ecran)  # Dessine les blocs autres que le personnage en premier
        self.blocs.add(self.personnage)
        ecran.blit(self.personnage.image, self.personnage.rect)  # Dessine le personnage en dernier pour qu'il soit au premier plan
