"""
Module stockant les donnees du jeu.
"""
from blocs import *
import itertools
from numpy import array


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


def rectangle_a(x, y, largeur):
    pos_x, pos_y = x * largeur, y * largeur
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
        self._blocs = trier(blocs)

    @blocs.deleter
    def blocs(self):
        raise AttributeError("L'attribut ne peut pas etre supprime.")

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
                       "[": Entree,             # Forme rectangulaire comme une porte. Crochet ouvrant -> entree
                       "]": Sortie,             # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,              # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant,            # Dollar fait penser a argent -> diamant
                       "~": lambda *foo: None}  # Vague -> fluide -> air -> vide

    def __init__(self, ascii, numero=None):
        self.numero = numero  # Numero du niveau
        self.ascii = ascii  # Representation du niveau avec des caracteres ascii

    @property
    def ascii(self):
        return self._ascii

    @ascii.setter
    def ascii(self, valeur):
        # On enleve tous les espaces, ainsi que les retours a la ligne se trouvant au debut ou a la fin
        self._ascii = enlever_extremites(valeur).replace(" ", "")

    @property
    def nombre_cases_largeur(self):
        return len(self.ascii.split("\n")[0])

    @property
    def nombre_cases_hauteur(self):
        return len(self.ascii.split("\n"))

    @property
    def largeur_case(self):
        largeur_max_case = RESOLUTION[0] / self.nombre_cases_largeur
        hauteur_max_case = RESOLUTION[1] / self.nombre_cases_hauteur
        return min(largeur_max_case, hauteur_max_case)

    def vers_cases(self):
        """
        Prend en entree un niveau et cree un groupe de cases ayant chacun le type et la position dictee par le niveau.

        :return: groupe de cases initialises avec la bonne position et le bon type
        """
        lignes_ascii = self.ascii.split("\n")
        cases = dict()
        for y, ligne_ascii in enumerate(lignes_ascii):
            if len(ligne_ascii) != self.nombre_cases_largeur:  # On teste si chaque ligne fait la meme longueur
                raise ValueError("Le niveau a ete defini incorrectement.")

            for x, bloc_ascii in enumerate(ligne_ascii):
                rect = rectangle_a(x, y, self.largeur_case)
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
        self.blocs_tries = []
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
        self.largeur_case = valeur.largeur_case
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
        self.actualiser_blocs()
        self.rectangle = self.rectangle_carte(self.cases)
        self.nombre_cases_largeur = self.rectangle.width / self.largeur_case
        self.nombre_cases_hauteur = self.rectangle.height / self.largeur_case

    @cases.deleter
    def cases(self):
        raise AttributeError("La propriete ne peut pas etre supprimee.")

    def x_min(self):
        largeur_jeu = self.largeur_case * self.nombre_cases_largeur
        x_min_f = (RESOLUTION[0] - largeur_jeu) / 2.0
        return int(round(x_min_f))

    def y_min(self):
        hauteur_jeu = self.largeur_case * self.nombre_cases_hauteur
        y_min_exact = (RESOLUTION[1] - hauteur_jeu) / 2.0
        return int(round(y_min_exact))

    def index_vers_coordonnees(self, x, y):
        return self.x_min() + x * self.largeur_case, self.y_min() + y * self.largeur_case

    def coordonnees_vers_index(self, x, y):
        return (x - self.x_min()) / self.largeur_case, (y - self.y_min()) / self.largeur_case

    def actualiser_blocs(self):
        blocs = []
        for case in self.cases.itervalues():
            blocs.extend(case.blocs)
        while None in blocs:
            blocs.remove(None)
        self.blocs_tries = trier(blocs)
        self.blocs_uniques = self.trouver_blocs_uniques(self.blocs_tries)
        self.nombre_diamants = self.compter_diamants(self.blocs_tries)
        self.cailloux = self.trouver_cailloux(self.blocs_tries)

    def bouger(self, bloc, rect):
        if rect != bloc.rect:
            self.cases[bloc.rect_hashable].enlever(bloc)
            self.cases[Rectangle(rect)].ajouter(bloc)
            bloc.rect.x, bloc.rect.y = rect.x, rect.y
            bloc.a_deja_bouge = True

    def supprimer(self, bloc):
        self.cases[bloc.rect_hashable].enlever(bloc)
        self.actualiser_blocs()

    def supprimer_morts(self):
        for bloc in self.blocs_tries:
            if bloc.est_mort:
                if isinstance(bloc, Personnage):
                    print("mort")
                    while 1:
                        for evenement in pygame.event.get():
                            if evenement.type == QUIT:
                                quit()
                            if evenement.type == KEYDOWN:
                                if evenement.key == K_q:
                                    quit()
                self.supprimer(bloc)

    @staticmethod
    def rectangle_carte(cases):
        x_min = y_min = x_max = y_max = None
        cles = cases.keys()
        if cles:
            xs = [cle.x for cle in cles]
            x_min = min(xs)
            x_max = max(xs)

            ys = [cle.y for cle in cles]
            y_min = min(ys)
            y_max = max(ys)
        return Rectangle(x_min, y_min, x_max - x_min, y_max - y_min)

    def blocs_a(self, x, y):
        rect = rectangle_a(x, y, self.largeur_case)
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
        rect = rectangle_a(x, y, self.largeur_case)
        return self.cases[rect]

    def rect_carte_vers_rect_ecran(self, rect):
        rect_ = rect.copy()
        rect_.x = self.x_min() + rect.x
        rect_.y = self.y_min() + rect.y
        return rect_

    def dessiner(self, ecran):
        """
        Affiche les blocs sur l'ecran.

        :param ecran: Ecran sur lequel dessiner les blocs.
        :return: "None"
        """
        for bloc in self.blocs_tries:          # Puisque les blocs sont tries par position z, les blocs les plus en
            ecran.blit(bloc.image, self.rect_carte_vers_rect_ecran(bloc.rect))  # avant sont dessines en dernier
