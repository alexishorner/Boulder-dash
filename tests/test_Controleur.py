"""
Module de test pour le module "Controleur"
"""

import Controleur
import os

path = os.path.dirname(Controleur.__file__)  # On recupere le chemin du module a tester
os.chdir(path)  # On change de repertoire pour pouvoir utiliser des chemins relatifs


def test_enlever_extremites():
    assert(Controleur.enlever_extremites("    \nabcd \nefg hi  \n  ") == "abcd \nefg hi")
    assert(Controleur.enlever_extremites("sbdufgidu5661 549d86gsd4654\n4d7") == "sbdufgidu5661 549d86gsd4654\n4d7")


def test_niveau_vers_blocs():
    niveau = Controleur.Niveau("""
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
    nombre_de_blocs_par_sorte = dict.fromkeys(Controleur.Carte.ASCII_VERS_BLOC.values(), 0)
    for c in niveau.ascii:
        for cle, sorte in Controleur.Carte.ASCII_VERS_BLOC.iteritems():
            if c == cle:
                nombre_de_blocs_par_sorte[sorte] += 1

    blocs = Controleur.Carte.niveau_vers_blocs(niveau)

    nombre_de_blocs_par_sorte_2 = dict.fromkeys(Controleur.Carte.ASCII_VERS_BLOC.values(), 0)
    for bloc in blocs:
        for cle, sorte in Controleur.Carte.ASCII_VERS_BLOC.iteritems():
            if bloc.__class__ == sorte:
                nombre_de_blocs_par_sorte_2[sorte] += 1

    print(nombre_de_blocs_par_sorte)
    assert(nombre_de_blocs_par_sorte == nombre_de_blocs_par_sorte_2)


if __name__ == "__main__":
    tests = (test_enlever_extremites, test_niveau_vers_blocs)  # On cree un tuple avec toutes les fonctions de test
    for test in tests:
        chaine = " du test \"{0}\"".format(test.__name__)  # On recupere le nom de chaque fonction de test
        print("Debut{0}...".format(chaine))  # Equivalent a "Debut du test \"" + nom_du_test + "\"..."
        test()  # On effectue le test
        print("Fin{0}".format(chaine))  # Equivalent a "Fin du test \"" + nom_du_test + "\""
        print("")
