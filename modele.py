# coding: utf-8
"""
Module stockant les donnees du jeu.
"""
from blocs import *
import json
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
    """
    Fonction permettant de nettoyer une liste de blocs et de la trier par ordre croissant de position z.

    :param blocs: liste de blocs à trier
    :return: nouvelle liste contenant les blocs par ordre croissant de coordonnée z
    """
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
        """
        Propriété permettant de gérer l'accès aux blocs de la case.

        :return: liste de blocs se trouvant sur la case
        """
        return self._blocs

    @blocs.setter
    def blocs(self, nouveaux):
        try:
            blocs = list(nouveaux)
        except TypeError:  # Si "blocs" n'est pas itérable
            blocs = [nouveaux]
        self._blocs = trier(blocs)  # On ordonne les blocs pour pouvoir les dessiner en respectant leur coordonnée z

    @property
    def rect(self):
        """
        Propriété permettant de gérer l'accès au rectangle décrivant les dimensions et la position de la case.

        :return: instance de "pygame.Rect" décrivant les dimensions et la position de la case.
        """
        return self._rect

    @rect.setter
    def rect(self, nouveau):
        rect = pygame.Rect(nouveau)  # On crée une copie du nouveau rectangle

        # On change le rectangle de chaque case
        for bloc in self.blocs:
            if bloc is not None:
                bloc.rect = rect
        self._rect = rect

    def ajouter(self, bloc):
        """
        Méthode permettant d'ajouter un bloc à la case.

        :param bloc: bloc à ajouter
        :return: "None"
        """
        self._blocs.append(bloc)
        self._blocs = trier(self._blocs)  # On trie les blocs à nouveau par ordre de position z

    def enlever(self, bloc):
        """
        Méthode permettant de retirer un bloc de la case.

        :param bloc: bloc à enlever
        :return: "None"
        """
        self._blocs.remove(bloc)
        if len(self._blocs) == 0:
            self._blocs = [None]


class Niveau(object):
    """
    Classe permettant de representer un niveau.
    Un niveau est un schema decrivant la position initiale de blocs de types divers.

    Cette classe utilise une chaine de caractere pour stocker le niveau et offre la possibilite de specifier le numero
    du niveau.
    """
    ASCII_VERS_BLOC = {"O": Caillou,            # Caractère ressemble a un caillou
                       "#": Mur,                # Ressemble a une barrière -> mur
                       "P": Personnage,         # "P" comme "Personnage"
                       "]": Sortie,             # Forme rectangulaire comme une porte. Crochet fermant -> sortie
                       "*": Terre,              # Ressemble aux points dans Packman et est centré verticalement, contrairement au point "."
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
        self.numero = numero  # Numéro du niveau
        self.nombre_cases_largeur = 0
        self.nombre_cases_hauteur = 0
        self.ascii = ascii  # Representation du niveau avec des caracteres ascii
        self.nombre_diamants_pour_sortir = 4
        self.temps_maximal = 120

    @property
    def ascii(self):
        """
        Propriété permettant de gérer l'accès à la représentation du niveau en caractères ascii.

        :return: représentation du niveau en caractères ascii
        """
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
        """
        Retourne une nouvelle instance de la classe "Niveau" créée à partir de la carte passée en argument.

        :param carte: instance de "Carte" à convertir en niveau
        :return: Instance de "Niveau" créée à partir de "carte"
        """
        colonne_ascii = ["~",] * carte.nombre_cases_hauteur
        blocs_ascii = []
        for i in range(carte.nombre_cases_largeur):
            blocs_ascii.append(list(colonne_ascii))
        for y in range(carte.nombre_cases_hauteur):
            for x in range(carte.nombre_cases_largeur):
                blocs = carte.blocs_a(x, y)
                if len(blocs) > 1:
                    bloc = None
                    for bloc_ in blocs:
                        if isinstance(bloc_, Personnage):
                            bloc = bloc_
                else:
                    bloc = blocs[0]
                if bloc is not None:
                    caractere = cls.BLOC_VERS_ASCII[bloc.__class__]
                    blocs_ascii[x][y] = caractere

        ascii = ""
        for y in range(carte.nombre_cases_hauteur):
            for x in range(carte.nombre_cases_largeur):
                ascii += blocs_ascii[x][y]
            ascii += "\n"
        niveau = cls(ascii)
        niveau.nombre_diamants_pour_sortir = carte.nombre_diamants_pour_sortir
        niveau.temps_maximal = carte.temps_maximal
        return niveau

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
        with open(chemin, "r") as f:
            try:
                niveau_json = json.loads(f.read())
            except ValueError:
                return None
            ascii = niveau_json["ascii"]
            nombre_diamants_pour_sortir = niveau_json["nombre diamants pour sortir"]
            temps_maximal = niveau_json["temps maximal"]
            niveau = cls(ascii)
            niveau.nombre_diamants_pour_sortir = nombre_diamants_pour_sortir
            niveau.temps_maximal = temps_maximal
            return niveau

    def sauvegarder(self, chemin):
        """
        Sauvegarde un niveau personnalise.

        :param chemin: chemin où enregistrer le fichier
        """
        niveau_json = json.dumps({"ascii": self.ascii, "nombre diamants pour sortir": self.nombre_diamants_pour_sortir,
                                  "temps maximal": self.temps_maximal})
        with open(chemin, "w") as f:
            f.write(niveau_json)

    @classmethod
    def vide(cls, largeur, hauteur):
        """
        Crée un niveau de la taille spécifiée ayant une simple bordure de murs et de la terre au milieu.

        :param largeur: nombre de cases du niveau à créer dans la largeur
        :param hauteur: nombre de cases du niveau à créer dans la hauteur
        :return: Instance de "Niveau" de la taille spécifiée en argument
        """
        ascii = ""
        for y in range(hauteur):
            ligne = ""
            for x in range(largeur):
                if x in (0, largeur - 1) or y in (0, hauteur - 1):
                    ligne += cls.BLOC_VERS_ASCII[Mur]
                else:
                    ligne += cls.BLOC_VERS_ASCII[Terre]
            ascii += ligne
            if y < hauteur - 1:
                ascii += "\n"

        return cls(ascii)


# On précharge tous les niveaux prédéfinis pour éviter de devoir le faire à chaque partie
NIVEAUX = [Niveau.charger("niveaux/predefinis/niveau_{0}.json".format(i)) for i in range(1, 7)]


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
        self.nombre_diamants_max = 0
        self._tuple_cases = tuple()
        self._rect = rect
        self.niveau = niveau

    @property
    def temps_maximal(self):
        """
        Propriété permettant d'associer le temps maximal du niveau à celui de la carte.

        :return: temps maximal pour terminer le niveau
        """
        return self.niveau.temps_maximal

    @temps_maximal.setter
    def temps_maximal(self, nouveau):
        self.niveau.temps_maximal = nouveau

    @property
    def nombre_diamants_pour_sortir(self):
        """
        Propriété permettant d'associer le nombre de diamants pour sortir du niveau à celui de la carte.

        :return: nombre de diamants requis pour sortir
        """
        return self.niveau.nombre_diamants_pour_sortir

    @nombre_diamants_pour_sortir.setter
    def nombre_diamants_pour_sortir(self, nouveau):
        self.niveau.nombre_diamants_pour_sortir = nouveau

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
        """
        Propriété permettant de gérer l'accès au tuple stockant toutes les cases. Note : "tuple_cases" n'est présent
        que par commodité, il permet d'itérer sur les cases rapidement au lieu de devoir itérer sur l'attribut "cases"
        qui est un dictionnaire.

        :return: tuple contenant toutes les cases de la carte
        """
        return self._tuple_cases

    @property
    def cases(self):
        """
        Propriete permettant d'acceder aux cases.

        :return: dictionnaire contenant toutes les cases avec leur rectangle comme clé
        """
        return self._cases

    @cases.setter
    def cases(self, valeur):
        if not isinstance(valeur, dict):
            raise ValueError("Les cases doivent etre un dictionnaire.")
        self._cases = valeur
        self._tuple_cases = tuple(valeur.itervalues())
        self.actualiser_blocs()
        self.nombre_diamants_max = self.nombre_diamants

    @property
    def rect(self):
        """
        Propriété permettant de gérer l'accès au rectangle de la carte. Les éléments de la cartes sont redimensionnés
        à chaque fois que la propriété est modifiée.

        :return:
        """
        return self._rect

    @rect.setter
    def rect(self, nouveau):
        self._rect = nouveau
        self.actualiser_rects_cases()  # Modifie les rectangles des cases par rapport au nouveau rectangle de la carte.

    @property
    def nombre_cases_largeur(self):
        """
        Propriété permettant d'associer le nombre de cases du niveau dans la largeur à celui de la carte.

        :return: nombre de cases dans la largeur
        """
        return self.niveau.nombre_cases_largeur

    @nombre_cases_largeur.setter
    def nombre_cases_largeur(self, nouveau):
        self.niveau.nombre_cases_largeur = nouveau

    @property
    def nombre_cases_hauteur(self):
        """
        Propriété permettant d'associer le nombre de cases du niveau dans la hauteur à celui de la carte.

        :return: nombre de cases dans la hauteur
        """
        return self.niveau.nombre_cases_hauteur

    @nombre_cases_hauteur.setter
    def nombre_cases_hauteur(self, nouveau):
        self.niveau.nombre_cases_hauteur = nouveau

    @property
    def largeur_case(self):
        """
        Propriété permettant de faire comme si la largeur des cases était un attribut

        :return: largeur des cases de la carte en pixels
        """
        return self.rect.width / self.nombre_cases_largeur

    @property
    def hauteur_case(self):
        """
        Propriété permettant de faire comme si la hauteur des cases était un attribut

        :return: hauteur des cases de la carte en pixels
        """
        return self.rect.height / self.nombre_cases_hauteur

    def index_vers_coordonnees(self, x, y):
        """
        Méthode permettant de convertir la place d'un objet sur la carte vers des coordonnées sur la fenêtre

        :param x: Index x sur la carte
        :param y: Index y sur la carte
        :return: Coordonnées de l'objet sur la fenêtre
        """
        return self.rect.x + x * self.largeur_case, self.rect.y + y * self.hauteur_case

    def coordonnees_vers_index(self, x, y):
        """
        Méthode permettant de convertir la position d'un objet sur la fenêtre en index sur la carte.

        :param x: Coordonnées x sur la fenêtre
        :param y: Coordonnées y sur la fenêtre
        :return: Tuple contenant l'index x et y calculés à partir de la position sur la fenêtre.
        """
        return (x - self.rect.x) / self.largeur_case, (y - self.rect.y) / self.hauteur_case

    def actualiser_rects_cases(self):
        """
        Modifie la taille de chaque case de la carte et remplace les clés du dictionnaire "self.cases" par les
        nouveaux rectangles des cases.

        :return: "None"
        """
        largeur, hauteur = self.largeur_case, self.hauteur_case
        cases = dict()
        for case in self.tuple_cases:
            rect = Rectangle(case.rect)  # On modifie une copie du rectangle pour que la case soit au courant du changement
            rect.x, rect.y = self.index_vers_coordonnees(*case.index)
            rect.width, rect.height = largeur, hauteur
            case.rect = rect  # La case sait qu'on change de rectangle
            cases.update({rect: case})
        self.cases = cases

    def sur_changement_niveau(self):
        """
        Actualise la carte après un changement de niveau.

        :return: "None"
        """
        # On crée les cases par rapport au niveau
        lignes_ascii = self.niveau.ascii.split("\n")
        cases = dict()
        for index_y, ligne_ascii in enumerate(lignes_ascii):
            for index_x, bloc_ascii in enumerate(ligne_ascii):
                x, y = self.index_vers_coordonnees(index_x, index_y)

                # On crée un rectangle hashable pour l'utiliser comme clé de dictionnaire
                rect = Rectangle(x, y, self.largeur_case, self.hauteur_case)
                case = Case(rect, (index_x, index_y))

                # On convertit chaque caractère en bloc et leur attribue une position initiale
                bloc = self.niveau.ASCII_VERS_BLOC[bloc_ascii](rect)
                case.ajouter(bloc)
                cases.update({rect: case})  # On ajoute la case à "cases"
        self.cases = cases

    def actualiser_blocs(self):
        """
        Méthode permettant d'actualiser les différents attributs relatifs aux blocs.

        :return: "None"
        """
        blocs = []
        for case in self.tuple_cases:
            blocs.extend(case.blocs)
        while None in blocs:
            blocs.remove(None)
        self.blocs_tries = trier(blocs)  # On trie les blocs par coordonnée z pour faciliter l'affichage
        self.blocs_uniques = self.trouver_blocs_uniques(self.blocs_tries)
        self.personnage = self.blocs_uniques[Personnage]
        self.sortie = self.blocs_uniques[Sortie]
        self.nombre_diamants = self.compter_diamants(self.blocs_tries)
        self.cailloux = self.trouver_cailloux(self.blocs_tries)

    def bouger(self, bloc, rect):
        """
        Méthode permettant de bouger un certain bloc vers la case ayant le rectangle "rect"

        :param bloc: bloc à bouger
        :param rect: rectangle indiquant vers quel endroit le bloc doit être bougé
        :return: "None"
        """
        if rect != bloc.rect:  # Si on bouge réellement le bloc
            self.cases[bloc.rect_hashable].enlever(bloc)  # On enlève le bloc de son ancienne case
            self.cases[Rectangle(rect)].ajouter(bloc)  # On ajoute le bloc dans sa nouvelle case
            bloc.rect.x, bloc.rect.y = rect.x, rect.y  # On modifie la position du bloc

    def supprimer(self, bloc):
        """
        Méthode permettant de supprimer un bloc de la carte.

        :param bloc: bloc à supprimer
        :return: "None"
        """
        self.cases[bloc.rect_hashable].enlever(bloc)
        self.actualiser_blocs()

    def changer_taille(self, largeur=None, hauteur=None):
        """
        Méthode permettant de changer la taille en nombre de cases de la carte

        :param largeur: nombre de cases dans la largeur
        :param hauteur: nombre de cases dans la hauteur
        :return: "None"
        """
        largeur_ = largeur
        hauteur_ = hauteur

        if largeur is None and hauteur is None:
            return

        # Si aucune largeur n'est spécifiée, on ne change pas le nombre de cases dans la largeur
        if largeur is None:
            largeur_ = self.nombre_cases_largeur

        # Si aucune hauteur n'est spécifiée, on ne change pas le nombre de cases dans la hauteur
        if hauteur is None:
            hauteur_ = self.nombre_cases_hauteur

        self.niveau = Niveau.vide(largeur_, hauteur_)

    def supprimer_morts(self):
        """
        Méthode permettant de supprimer tous les blocs morts.

        :return: "None"
        """
        for bloc in self.blocs_tries:
            if bloc.est_mort:
                # On ne supprime pas le personnage, car on veut pouvoir tester s'il est mort depuis l'extérieur de la
                # classe
                if not isinstance(bloc, Personnage):
                    self.supprimer(bloc)

    def blocs_a(self, x, y, index=True):
        """
        Méthode retournant les blocs se trouvant à une certaine position.

        :param x: position x où chercher les blocs
        :param y:  position y où chercher les blocs
        :param index: booléen indiquant si x et y sont des indexes sur la carte ou des coordonnées sur la fenêtre
        :return: tuple contenant les blocs à la position spécifiée
        """
        return self.case_a(x, y, index).blocs

    def rect_a(self, x, y, index=True):
        """
        Méthode retournant le rectangle de la case se trouvant à une certaine position.

        :param x: position x où se trouve le rectangle
        :param y:  position y où se trouve le rectangle
        :param index: booléen indiquant si x et y sont des indexes sur la carte ou des coordonnées sur la fenêtre
        :return: instance de "Rectangle" ayant la position et les dimensions de la case se trouvant à la position
        spécifiée
        """
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
        """
        Active la sortie si le personnage a ramassé assez de diamants.

        :return: "None"
        """
        if self.personnage is not None:
            if self.personnage.diamants_ramasses >= self.nombre_diamants_pour_sortir:
                self.sortie.activer()

    def valider(self):
        """
        Vérifie si la carte est prête pour le jeu.

        :return: liste des erreurs s'étant produites
        """
        erreurs = []
        if self.personnage is None:
            erreurs.append(ERREURS.PERSONNAGE_MANQUANT)
        if self.sortie is None:
            erreurs.append(ERREURS.PORTE_MANQUANTE)
        if self.nombre_diamants < self.nombre_diamants_pour_sortir:
            erreurs.append(ERREURS.DIAMANTS_INSUFFISANTS)
        return erreurs
