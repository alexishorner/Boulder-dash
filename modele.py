"""
Module stockant les donnees du jeu.
"""
from blocs import *
import itertools
from numpy import matrix
from os import listdir
from os.path import isfile, join


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


def trier(blocs):
    if len(blocs) == 0:
        return [None]

    blocs_ = blocs
    while None in blocs_ and len(blocs_) > 1:
        blocs_.remove(None)  # On enleve les occurences inutiles de "None"
    if None not in blocs_:
        blocs_ = sorted(blocs_, key=lambda bloc: bloc.z)  # On trie les blocs par position z croissante
    return blocs_


class Case(object):
    """
    Classe permettant de stocker des blocs partageant la meme position.
    """
    def __init__(self, rect, index, blocs=tuple()):
        self.blocs = blocs
        self.index = Coordonnees(index[0], index[1])
        self.rect = Rectangle(rect)

    @property
    def blocs(self):
        return self._blocs

    @blocs.setter
    def blocs(self, nouveaux):
        try:
            blocs = list(nouveaux)
        except TypeError:
            blocs = [nouveaux]
        self._blocs = trier(blocs)

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, nouveau):
        rect = pygame.Rect(nouveau)
        for bloc in self.blocs:
            if bloc is not None:
                bloc.rect = rect
        self._rect = rect

    def ajouter(self, bloc):
        self._blocs.append(bloc)
        self._blocs = trier(self._blocs)

    def enlever(self, bloc):
        self._blocs.remove(bloc)
        self._blocs = trier(self._blocs)


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
                       "]": Sortie,             # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,              # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant,            # Dollar fait penser a argent -> diamant
                       "~": lambda *foo: None}  # Vague -> fluide -> air -> vide

    BLOC_VERS_ASCII = {Caillou: "O",
                       Mur: "#",
                       Personnage: "P",
                       Sortie: "]",
                       Terre: "*",
                       Diamant: "$",
                       None: "~"}

    def __init__(self, ascii, numero=None):
        self.numero = numero  # Numero du niveau
        self.nombre_cases_largeur = 0
        self.nombre_cases_hauteur = 0
        self.ascii = ascii  # Representation du niveau avec des caracteres ascii

    @property
    def ascii(self):
        return self._ascii

    @ascii.setter
    def ascii(self, valeur):
        # On enleve tous les espaces, ainsi que les retours a la ligne se trouvant au debut ou a la fin
        ascii = enlever_extremites(valeur).replace(" ", "")
        lignes = ascii.split("\n")
        longueur_premiere_ligne = len(lignes[0])
        for ligne in lignes:
            if len(ligne) != longueur_premiere_ligne:  # On teste si chaque ligne fait la meme longueur
                raise ValueError("Le niveau a ete defini incorrectement.")
        self.nombre_cases_hauteur = len(lignes)
        self.nombre_cases_largeur = longueur_premiere_ligne
        self._ascii = ascii

    @classmethod
    def depuis_carte(cls, carte):
        colonne_ascii = ["~",] * carte.nombre_cases_hauteur
        blocs_ascii = []
        for i in range(carte.nombre_cases_largeur):
            blocs_ascii.append(list(colonne_ascii))
        for y in range(carte.nombre_cases_hauteur):
            for x in range(carte.nombre_cases_largeur):
                blocs = carte.blocs_a(x, y)
                if len(blocs) != 1:
                    raise RuntimeError("Pour convertir une carte vers un niveau il ne faut pas plus d'un bloc par case.")
                else:
                    bloc = blocs[0]
                    if bloc is not None:
                        caractere = cls.BLOC_VERS_ASCII[bloc.__class__]
                        blocs_ascii[x][y] = caractere

        niveau = ""
        for y in range(carte.nombre_cases_hauteur):
            for x in range(carte.nombre_cases_largeur):
                niveau += blocs_ascii[x][y]
            niveau += "\n"
        return cls(niveau)

    @classmethod
    def niveau(cls, numero):
        """
        Retourne le niveau ayant le numero "numero".

        :param numero: numero du niveau
        :return: niveau correspondant au numero specifie
        """
        niveau = NIVEAUX[numero-1]
        niveau.numero = numero
        return niveau

    @classmethod
    def charger(cls, chemin):
        """
        Charge un niveau
        """
        f = open(chemin, "r")
        ascii = "".join(f.readlines())
        niveau = cls(ascii)
        return niveau

    def sauvegarder(self, chemin):
        """
        Sauvegarde un niveau personnalise.
        """
        nomchemin = chemin
        f = open(nomchemin, "w")
        f.writelines(self.ascii)
        f.close()

    @classmethod
    def vide(cls, largeur, hauteur):
        ascii = ""
        for y in range(hauteur):
            ligne = ""
            for x in range(largeur):
                if x in (0, largeur - 1) or y in (0, hauteur - 1):
                    ligne += cls.BLOC_VERS_ASCII[Mur]
                else:
                    ligne += cls.BLOC_VERS_ASCII[None]
            ascii += ligne
        return cls(ascii)


NIVEAUX = [Niveau.charger("niveaux/niveau{0}".format(i)) for i in range(1, 5)]


class Carte(object):
    """
    Classe permettant de representer une carte, c'est-a-dire l'ensemble des blocs presents sur l'ecran.
    """
    def __init__(self, rect, niveau):
        self.blocs_tries = []
        self.blocs_uniques = dict()
        self.personnage = None
        self.sortie = None
        self.cailloux = dict()
        self.nombre_diamants = 0
        self.nombre_diamants_pour_sortir = 4
        self.nombre_cases_hauteur = 0
        self.nombre_cases_largeur = 0
        self._tuple_cases = tuple()
        self._rect = rect
        self.niveau = niveau

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
        self.sur_changement_niveau()

    @property
    def tuple_cases(self):
        return self._tuple_cases

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
        self._tuple_cases = tuple(valeur.itervalues())
        self.actualiser_blocs()  # FIXME : attention on n'actualise pas le nombre de cases dans la largeur et la hauteur

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, nouveau):
        self._rect = nouveau
        self.actualiser_rects_cases()

    @property
    def largeur_case(self):
        return self.rect.width / self.nombre_cases_largeur

    @property
    def hauteur_case(self):
        return self.rect.height / self.nombre_cases_hauteur

    def index_vers_coordonnees(self, x, y):
        return self.rect.x + x * self.largeur_case, self.rect.y + y * self.hauteur_case

    def coordonnees_vers_index(self, x, y):
        return (x - self.rect.x) / self.largeur_case, (y - self.rect.y) / self.hauteur_case

    def actualiser_rects_cases(self):
        cases = dict()
        for case in self.tuple_cases:
            rect = Rectangle(case.rect)  # On modifie une copie du rectangle pour que la case soit au courant du changement
            rect.x, rect.y = self.index_vers_coordonnees(*case.index)
            rect.width, rect.height = self.largeur_case, self.hauteur_case
            case.rect = rect  # La case sait qu'on change de rectangle
            cases.update({rect: case})
        self.cases = cases

    def sur_changement_niveau(self):
        """
        Actualise la carte apres un changement de niveau.

        :return: "None"
        """
        self.nombre_cases_hauteur = self.niveau.nombre_cases_hauteur
        self.nombre_cases_largeur = self.niveau.nombre_cases_largeur
        lignes_ascii = self.niveau.ascii.split("\n")
        cases = dict()
        for index_y, ligne_ascii in enumerate(lignes_ascii):
            for index_x, bloc_ascii in enumerate(ligne_ascii):
                x, y = self.index_vers_coordonnees(index_x, index_y)
                rect = Rectangle(x, y, self.largeur_case, self.hauteur_case)
                case = Case(rect, (index_x, index_y))

                # On convertit chaque caractere en bloc et leur attribue une position initiale
                bloc = self.niveau.ASCII_VERS_BLOC[bloc_ascii](rect)
                case.ajouter(bloc)
                cases.update({rect: case})
        self.cases = cases

    def actualiser_blocs(self):
        blocs = []
        for case in self.tuple_cases:
            blocs.extend(case.blocs)
        while None in blocs:
            blocs.remove(None)
        self.blocs_tries = trier(blocs)
        self.blocs_uniques = self.trouver_blocs_uniques(self.blocs_tries)
        self.personnage = self.blocs_uniques[Personnage]
        self.sortie = self.blocs_uniques[Sortie]
        self.nombre_diamants = self.compter_diamants(self.blocs_tries)
        self.cailloux = self.trouver_cailloux(self.blocs_tries)

    def bouger(self, bloc, rect):
        if rect != bloc.rect:
            self.cases[bloc.rect_hashable].enlever(bloc)
            self.cases[Rectangle(rect)].ajouter(bloc)
            bloc.rect.x, bloc.rect.y = rect.x, rect.y

    def supprimer(self, bloc):
        self.cases[bloc.rect_hashable].enlever(bloc)
        self.actualiser_blocs()

    def changer_taille(self, largeur=None, hauteur=None):
        cases = dict()
        largeur_ = largeur
        hauteur_ = hauteur
        if largeur is None:
            largeur_ = self.nombre_cases_largeur
        if hauteur is None:
            hauteur_ = hauteur
        self.nombre_cases_largeur = largeur_
        self.nombre_cases_hauteur = hauteur_
        for x in range(largeur_):
            for y in range(hauteur_):
                index = (x, y)
                rect = self.rect_a(x, y)
                blocs = None
                if x in (0, largeur_ - 1) or y in (0, hauteur_ - 1):
                    blocs = (Mur(rect),)
                case = Case(rect, index, blocs)
                cases.update({rect: case})
        self.cases = cases

    def ajouter_ligne(self, y):
        cases = self.cases.copy()
        for x in range(self.nombre_cases_largeur):
            index = (x, y)
            rect = self.rect_a(*index)
            blocs = (Mur(rect),)
            case = Case(rect, index, blocs)
            cases.update({rect: case})
        self.cases = cases

    def ajouter_colonne(self, x):
        cases = self.cases.copy()
        for y in range(self.nombre_cases_hauteur):
            index = (x, y)
            rect = self.rect_a(*index)
            blocs = (Mur(rect),)
            case = Case(rect, index, blocs)
            cases.update({rect: case})
        self.cases = cases

    def supprimer_morts(self):
        for bloc in self.blocs_tries:
            if bloc.est_mort:
                if not isinstance(bloc, Personnage):
                    self.supprimer(bloc)

    def blocs_a(self, x, y, index=True):
        return self.case_a(x, y, index).blocs

    def rect_a(self, x, y, index=True):
        if index:
            x_, y_ = self.index_vers_coordonnees(x, y)
        else:
            x_, y_ = x, y
        return Rectangle(x_, y_, self.largeur_case, self.hauteur_case)

    def case_a(self, x, y, index=True):
        """
        Permet d'acceder a la case situee a la position (x, y).

        :param x: coordonnee x de la case
        :param y: coordonne y de la case
        :param index: booleen specifiant si "x" et "y" representent l'index ou les coordonnees de la case
        :return: instance de "Case" se situant a la position (x, y)
        """
        rect = self.rect_a(x, y, index)
        return self.cases[rect]

    @staticmethod
    def trouver_blocs_uniques(blocs):
        """
        Cherche dans une liste de blocs la premiere occurrence d'un bloc de type "Personnage".

        :param blocs: Blocs dans lesquels chercher
        :return: Premiere occurrence d'un bloc de type "Personnage"
        """
        blocs_uniques = {Personnage: None, Sortie: None}
        for bloc in blocs:
            if bloc.__class__ in blocs_uniques.keys():
                blocs_uniques[bloc.__class__] = bloc
        return blocs_uniques

    @staticmethod
    def trouver_cailloux(blocs):
        """
        Cherche dans une liste de bloc tous les blocs de type "Caillou"

        :param blocs: Blocs dans lesquels chercher
        :return: liste des cailloux du jeu
        """
        blocs_cailloux = []
        for bloc in blocs:
            if isinstance(bloc, Caillou):
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
            if isinstance(bloc, Diamant):
                nombre += 1
        return nombre

    def activer_sortie(self):
        if self.personnage is not None:
            if self.personnage.diamants_ramasses >= self.nombre_diamants_pour_sortir:
                self.sortie.activer()

    def valider(self):
        erreurs = []
        if self.personnage is None:
            erreurs.append(ERREURS.PERSONNAGE_MANQUANT)
        if self.sortie is None:
            erreurs.append(ERREURS.PORTE_MANQUANTE)
        if self.nombre_diamants < self.nombre_diamants_pour_sortir:
            erreurs.append(ERREURS.DIAMANTS_INSUFFISANTS)
        return erreurs
