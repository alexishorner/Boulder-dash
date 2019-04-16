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
        return chaine[i:]
    return chaine[:i+1]


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
                       "*": Terre,       # Ressemble aux points dans Packman et est centre verticalement, contrairement au point "."
                       "$": Diamant}     # Dollar fait penser a argent -> diamant

    def __init__(self, niveau):
        self.blocs = self.niveau_vers_blocs(niveau)

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

    def dessiner(self):
        self.blocs.draw(ecran)


def test_enlever_extremites():
    assert(enlever_extremites("    \nabcd \nefg hi  \n  ") == "abcd \nefg hi")
    assert(enlever_extremites("diuuhcbsbdufgidu5661 549d86gsd4654\n4d7") == "diuuhcbsbdufgidu5661 549d86gsd4654\n4d7")

def test_niveau_vers_blocs():
    niveau = Niveau("""
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
                    """)
    nombre_de_blocs_par_sorte = dict.fromkeys(Carte.ASCII_VERS_BLOC.values(), 0)
    for c in niveau.ascii:
        for cle, sorte in Carte.ASCII_VERS_BLOC.iteritems():
            if c == cle:
                nombre_de_blocs_par_sorte[sorte] += 1

    blocs = Carte.niveau_vers_blocs(niveau)

    nombre_de_blocs_par_sorte_2 = dict.fromkeys(Carte.ASCII_VERS_BLOC.values(), 0)
    for bloc in blocs:
        for cle, sorte in Carte.ASCII_VERS_BLOC.iteritems():
            if bloc.__class__ == sorte:
                nombre_de_blocs_par_sorte_2[sorte] += 1

    print(nombre_de_blocs_par_sorte)
    assert(nombre_de_blocs_par_sorte == nombre_de_blocs_par_sorte_2)


if __name__ == "__main__":
    tests = (test_enlever_extremites, test_niveau_vers_blocs)
    for test in tests:
        chaine = " du test \"{0}\"".format(test.__name__)
        print("Debut{0}".format(chaine))
        test()
        print("Fin{0}".format(chaine))
        print("")
