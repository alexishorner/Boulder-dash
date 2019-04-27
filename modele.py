"""
Module stockant les donnees du jeu.
"""
from blocs import *
import itertools


def _enlever_extremite(chaine, extremite=ORIENTATIONS.GAUCHE, caracteres_a_enlever=("\n", " ")):
    """
    Enleve des caracteres se trouvant a une extremite d'une chaine de caracteres.

    Exemple :
    extremite == ORIENTATIONS.DROITE
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
    if extremite == ORIENTATIONS.GAUCHE:
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

    if extremite == ORIENTATIONS.GAUCHE:
        return chaine[i:]  # renvoie la chaine de caracteres depuis le caractere i jusqu'a la fin
    return chaine[:i+1]  # renvoie la chaine de caracteres depuis le debut jusqu'au caractere i


def enlever_extremites(chaine, caracteres_a_enlever=("\n", " ")):
    """
    Enleve certains caracteres a chacune des extremites d'une chaine de caracteres.

    :param chaine: chaine de caracteres a traiter
    :param caracteres_a_enlever: iterable contenant les caracteres devant etre enleves
    :return: chaine de caracteres apres avoir enleve les caracteres specifies a chacune des extremites.
    """
    variable_temporaire = _enlever_extremite(chaine, ORIENTATIONS.GAUCHE, caracteres_a_enlever)  # enleve l'extremite gauche
    return _enlever_extremite(variable_temporaire, ORIENTATIONS.DROITE, caracteres_a_enlever)  # enleve l'extremite droite


def dimensions(liste):
    return max(array(liste).shape)


def aplatir(liste):
    dim = dimensions(liste)
    aplatie = liste
    for i in range(dim - 1):
        aplatie = itertools.chain.from_iterable(aplatie)
    return list(aplatie)


def index_vers_coordonnees(x, y):
    x_min, y_min = DIMENSIONS.X_MIN, DIMENSIONS.Y_MIN
    largeur = DIMENSIONS.LARGEUR_CASE
    return x_min + x * largeur, y_min + y * largeur


def coordonnees_vers_index(x, y):
    x_min, y_min = DIMENSIONS.X_MIN, DIMENSIONS.Y_MIN
    largeur = DIMENSIONS.LARGEUR_CASE
    return (x - x_min) / largeur, (y - y_min) / largeur


def rectangle_a(x, y):
    pos_x, pos_y = index_vers_coordonnees(x, y)
    largeur = DIMENSIONS.LARGEUR_CASE
    return Rectangle(pos_x, pos_y, largeur, largeur)


class Case(object):
    """
    Classe permettant de stocker des blocs partageant la meme position.
    """
    def __init__(self, rect, blocs=tuple()):
        self.rect = Rectangle(rect)
        self.blocs = list(blocs)

    @property
    def blocs(self):
        return self._blocs

    @blocs.setter
    def blocs(self, nouveaux):
        blocs = list(nouveaux)
        self._blocs = self.trier(blocs)

    @blocs.deleter
    def blocs(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

    def ajouter(self, bloc):
        self._blocs.append(bloc)
        self._blocs = self.trier(self._blocs)

    @staticmethod
    def trier(blocs):
        if len(blocs) == 0:
            return [None]

        blocs_ = blocs
        while None in blocs_ and len(blocs_) > 1:
            blocs_.remove(None)  # On enleve les occurences inutiles de "None"
        if None not in blocs_:
            blocs_ = sorted(blocs_, key=lambda bloc: bloc.z)  # On trie les blocs par position z
        return blocs_


class Niveau(object):
    """
    Classe permettant de representer un niveau.
    Un niveau est un schema decrivant la position initiale de blocs de types divers.

    Cette classe utilise une chaine de caractere pour stocker le niveau et offre la possibilite de specifier le numero
    du niveau.
    """
    ASCII_VERS_BLOC = {"O": Caillou,            # Ressemble a un caillou
                       "#": Mur,                # Ressemble a une barriere -> mur
                       "P": Personnage,         # "P" comme "Personnage"
                       "[": Entree,             # Forme rectangulaire comme une porte. Crochet ouvrant -> entree
                       "]": Sortie,             # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,              # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant,            # Dollar fait penser a argent -> diamant
                       "~": lambda *foo: None}  # Vague -> fluide -> air -> vide

    def __init__(self, ascii, numero=None):
        self.numero = numero  # Numero du niveau
        self.ascii = ascii  # Representation du niveau avec des caracteres ascii

    def vers_cases(self):
        """
        Prend en entree un niveau et cree un groupe de cases ayant chacun le type et la position dictee par le niveau.

        :return: groupe de cases initialises avec la bonne position et le bon type
        """
        niveau_ascii = self.ascii
        niveau_ascii = enlever_extremites(niveau_ascii).replace(" ", "")    # On enleve tous les espaces, ainsi que les
                                                                            # retours a la ligne se trouvant au debut ou
                                                                            # a la fin
        lignes_ascii = niveau_ascii.split("\n")
        longueur_ligne = len(lignes_ascii[0])
        cases = dict()
        for y, ligne_ascii in enumerate(lignes_ascii):
            if len(ligne_ascii) != longueur_ligne:  # On teste si chaque ligne fait la meme longueur
                raise ValueError("Le niveau a ete defini incorrectement.")

            for x, bloc_ascii in enumerate(ligne_ascii):
                rect = rectangle_a(x, y)
                case = Case(rect)
                bloc = self.ASCII_VERS_BLOC[bloc_ascii](rect)  # On convertit chaque caractere en bloc et leur attribue
                                                               # une position initiale
                case.ajouter(bloc)
                cases.update({rect: case})
        return cases

    @classmethod
    def niveau(cls, numero):
        """
        Retourne le niveau ayant le numero "numero".

        :param numero: numero du niveau
        :return: niveau correspondant au numero specifie
        """
        return cls(NIVEAUX[numero-1], numero)


class Carte(object):
    """
    Classe permettant de representer une carte, c'est-a-dire l'ensemble des blocs presents sur l'ecran.
    """
    def __init__(self, niveau):
        self.blocs = []
        self.blocs_uniques = dict()
        self.cailloux = dict()
        self.nombre_diamants = 0
        self.niveau = niveau
        self.personnage = self.blocs_uniques[Personnage]
        self.sortie = self.blocs_uniques[Sortie]
        if self.personnage is None:  # On oblige la presence d'un personnage, car on ne peut pas jouer sans
            raise LookupError("Pas de personnage trouve.")

    @property
    def niveau(self):
        """
        Propriete permettant d'acceder au niveau.

        :return: niveau
        """
        return self._niveau

    @niveau.setter
    def niveau(self, valeur):
        self._niveau = valeur
        self.cases = valeur.vers_cases()

    @niveau.deleter
    def niveau(self):
        raise AttributeError("La propriete ne peut pas etre supprimee.")

    @property
    def cases(self):
        """
        Propriete permettant d'acceder aux cases.

        :return: cases
        """
        return self._cases

    @cases.setter
    def cases(self, valeur):
        if not isinstance(valeur, dict):
            raise ValueError("Les cases doivent etre un dictionnaire.")
        self._cases = valeur
        blocs = []
        for case in valeur.itervalues():
            blocs.extend(case.blocs)
        while None in blocs:
            blocs.remove(None)
        self.rectangle = self.rectangle_carte(self.cases)
        self.nombre_cases_largeur = self.rectangle.width / DIMENSIONS.LARGEUR_CASE
        self.nombre_cases_hauteur = self.rectangle.height / DIMENSIONS.LARGEUR_CASE
        self.blocs = blocs
        self.blocs_uniques = self.trouver_blocs_uniques(self.blocs)
        self.nombre_diamants = self.compter_diamants(self.blocs)
        self.cailloux = self.trouver_cailloux(self.blocs)

    @cases.deleter
    def cases(self):
        raise AttributeError("La propriete ne peut pas etre supprimee.")

    @staticmethod
    def rectangle_carte(cases):
        x_min = y_min = x_max = y_max = None
        for cle in cases.keys():
            if x_min is None:
                x_min = x_max = cle.x
                y_min = y_max = cle.y
            else:
                if cle.x < x_min:
                    x_min = cle.x
                if cle.x > x_max:
                    x_max = cle.x
                if cle.y < y_min:
                    y_min = cle.y
                if cle.y > y_max:
                    y_max = cle.y
        return Rectangle(x_min, y_min, x_max - x_min, y_max - y_min)

    def blocs_a(self, x, y):
        rect = rectangle_a(x, y)
        return self.cases[rect].blocs

    @staticmethod
    def trouver_blocs_uniques(blocs):
        """
        Cherche dans une liste de blocs la premiere occurrence d'un bloc de type "Personnage".

        :param blocs: Blocs dans lesquels chercher
        :return: Premiere occurrence d'un bloc de type "Personnage"
        """
        blocs_uniques = {Personnage: None, Entree: None, Sortie: None}
        for bloc in blocs:
            if bloc.__class__ in blocs_uniques.keys():
                blocs_uniques[bloc.__class__] = bloc
        return blocs_uniques

    @staticmethod
    def trouver_cailloux(blocs):
        """
        cherche dans une liste de bloc tous les blocs de type "Caillou"
        :param blocs: Blocs dans lesquels chercher
        :return: liste des cailloux du jeu
        """
        blocs_cailloux = []
        for bloc in blocs:
            type_de_bloc = bloc.__class__
            if type_de_bloc == Caillou:
                blocs_cailloux.append(bloc)
        return blocs_cailloux

    @staticmethod
    def compter_diamants(blocs):
        """
        Compte le nombre de diamants dans un ensemble de blocs.

        :param blocs: blocs dans lesquels chercher les diamants
        :return: nombre de diamants
        """
        nombre = 0
        for bloc in blocs:
            if bloc.__class__ == Diamant:
                nombre += 1
        return nombre

    def case_a(self, x, y):
        """
        Permet d'acceder a la case situee a la position (x, y).
        :param x: coordonnee x de la case
        :param y: coordonne y de la case
        :return: instance de "Case" se situant a la position (x, y)
        """
        rect = rectangle_a(x, y)
        return self.cases[rect]

    def blocs_adjacents(self, bloc):
        adjacents = []
        index_x, index_y = coordonnees_vers_index(bloc.rect.x, bloc.rect.y)
        for i in range(-1, 1):
            for j in range(-1, 1):
                x = index_x + i
                y = index_y + j
                if x < len(self.cases) and y < len(self.cases[x]):
                    adjacents.append(self.cases[x][y])
        return aplatir(adjacents)

    def dessiner(self, ecran):
        """
        Affiche les blocs sur l'ecran.

        :param ecran: Ecran sur lequel dessiner les blocs.
        :return: "None"
        """
        for bloc in self.blocs:
            if bloc is not self.personnage:
                ecran.blit(bloc.image, bloc.rect)  # Dessine les blocs autres que le personnage en premier
        self.blocs.append(self.personnage)
        ecran.blit(self.personnage.image, self.personnage.rect)  # Dessine le personnage en dernier pour qu'il soit au premier plan
