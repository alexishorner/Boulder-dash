"""
Module de test pour le module "modele"
"""
import modele


def test_enlever_extremites():
    assert(modele.enlever_extremites("    \nabcd \nefg hi  \n  ") == "abcd \nefg hi")
    assert(modele.enlever_extremites("sbdufgidu5661 549d86gsd4654\n4d7") == "sbdufgidu5661 549d86gsd4654\n4d7")


def test_vers_cases():
    niveau = modele.Niveau("""
                    ############~
                    #***O***O*$#~
                    #***OOP**~##~
                    #$$$#******#~
                    #OOOO*$]***#~
                    #**********#~
                    #**********#~
                    #**********#~
                    #**********#~
                    #**********#~
                    ############~
                    """)
    nombre_de_blocs_par_sorte = dict.fromkeys(modele.Niveau.ASCII_VERS_BLOC.values(), 0)
    for c in niveau.ascii:
        for cle, sorte in modele.Niveau.ASCII_VERS_BLOC.iteritems():
            if c == cle:
                nombre_de_blocs_par_sorte[sorte] += 1

    cases = niveau.vers_cases()

    nombre_de_blocs_par_sorte_2 = dict.fromkeys(modele.Niveau.ASCII_VERS_BLOC.values(), 0)
    for case in cases.itervalues():
        for bloc in case.blocs:
            for sorte in nombre_de_blocs_par_sorte_2.keys():
                rect = modele.pygame.Rect()
                if bloc is None and sorte(rect) is None:  # "sorte(rect)" cree un objet de sorte "sorte"
                    nombre_de_blocs_par_sorte_2[sorte] += 1
                elif bloc.__class__ == sorte:
                    nombre_de_blocs_par_sorte_2[sorte] += 1

    assert(nombre_de_blocs_par_sorte == nombre_de_blocs_par_sorte_2)


def test_blocs_a():
    niveau = modele.Niveau("""
                    ############~
                    #***O***O*$#~
                    #***OOP**~##~
                    #$$$#******#~
                    #OOOO*$]***#~
                    #**********#~
                    #**********#~
                    #**********#~
                    #**********#~
                    #**********#~
                    ############~
                    """)
    carte = modele.Carte(niveau)
    assert(isinstance(carte.blocs_a(0, 0)[0], modele.Mur))
    assert(isinstance(carte.blocs_a(6, 2)[0], modele.Personnage))
    assert(isinstance(carte.blocs_a(6, 4)[0], modele.Diamant))
    assert(isinstance(carte.blocs_a(7, 4)[0], modele.Sortie))
    assert(carte.blocs_a(12, 10)[0] is None)


if __name__ == "__main__":
    tests = (test_enlever_extremites, test_vers_cases, test_blocs_a)  # On cree un tuple avec toutes les fonctions de test
    for test in tests:
        print("")
        chaine = " du test \"{0}\"".format(test.__name__)  # On recupere le nom de chaque fonction de test
        print("Debut{0}...".format(chaine))  # Equivalent a "Debut du test \"" + nom_du_test + "\"..."
        test()  # On effectue le test
        print("Fin{0}".format(chaine))  # Equivalent a "Fin du test \"" + nom_du_test + "\""
