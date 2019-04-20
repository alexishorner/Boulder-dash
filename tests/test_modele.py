"""
Module de test pour le module "modele"
"""
import tests
import modele


def test_enlever_extremites():
    assert(modele.enlever_extremites("    \nabcd \nefg hi  \n  ") == "abcd \nefg hi")
    assert(modele.enlever_extremites("sbdufgidu5661 549d86gsd4654\n4d7") == "sbdufgidu5661 549d86gsd4654\n4d7")


def test_vers_blocs():
    niveau = modele.Niveau("""
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
    nombre_de_blocs_par_sorte = dict.fromkeys(modele.Niveau.ASCII_VERS_BLOC.values(), 0)
    for c in niveau.ascii:
        for cle, sorte in modele.Niveau.ASCII_VERS_BLOC.iteritems():
            if c == cle:
                nombre_de_blocs_par_sorte[sorte] += 1

    blocs = niveau.vers_blocs()

    nombre_de_blocs_par_sorte_2 = dict.fromkeys(modele.Niveau.ASCII_VERS_BLOC.values(), 0)
    for bloc in blocs:
        for cle, sorte in modele.Niveau.ASCII_VERS_BLOC.iteritems():
            if bloc.__class__ == sorte:
                nombre_de_blocs_par_sorte_2[sorte] += 1

    assert(nombre_de_blocs_par_sorte == nombre_de_blocs_par_sorte_2)


if __name__ == "__main__":
    tests.init()
    tests = (test_enlever_extremites, test_vers_blocs)  # On cree un tuple avec toutes les fonctions de test
    for test in tests:
        print("")
        chaine = " du test \"{0}\"".format(test.__name__)  # On recupere le nom de chaque fonction de test
        print("Debut{0}...".format(chaine))  # Equivalent a "Debut du test \"" + nom_du_test + "\"..."
        test()  # On effectue le test
        print("Fin{0}".format(chaine))  # Equivalent a "Fin du test \"" + nom_du_test + "\""
