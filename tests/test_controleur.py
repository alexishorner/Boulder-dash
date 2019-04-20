"""
Module de test du module "controleur"
"""
import tests
from controleur import *


def test_modulo():
    assert(abs(modulo(97.05, 0.1) - 0.05) < 1e-13)
    assert(abs(modulo(7.499999, 0.5) - 0.499999) < 1e-13)
    assert(abs(modulo(7.500001, 0.5) - 0.000001) < 1e-13)
    assert(abs(modulo(8.0, 0.000049) - 0.000015) < 1e-13)


def test_booleens_vers_indexes():
    booleens = [False] * GestionnaireTouches.nombre_de_touches()
    booleens[K_LEFT] = True
    booleens[K_UP] = True
    booleens[K_w] = True
    assert(set(GestionnaireTouches.booleens_vers_indexes(booleens)) == {K_LEFT, K_UP, K_w})


def test_indexes_vers_booleens():
    indexes = (K_LEFT, K_UP, K_w)
    booleens_attendus = [False] * GestionnaireTouches.nombre_de_touches()
    booleens_attendus[K_LEFT] = True
    booleens_attendus[K_UP] = True
    booleens_attendus[K_w] = True
    assert(GestionnaireTouches.indexes_vers_booleens(indexes) == booleens_attendus)


def test_changement_touches():
    anciens_booleens = GestionnaireTouches.indexes_vers_booleens((K_RIGHT, K_LEFT, K_UP))
    gestionnaire = GestionnaireTouches(anciens_booleens)
    nouveaux_booleens = gestionnaire.indexes_vers_booleens((K_LEFT, K_DOWN, K_w))
    ajoutees, enlevees = gestionnaire.changements_touches(nouveaux_booleens)
    assert((set(ajoutees), set(enlevees)) == ({K_DOWN, K_w}, {K_RIGHT, K_UP}))


def test_actualiser_touches():
    anciens_booleens = GestionnaireTouches.indexes_vers_booleens((K_RIGHT, K_LEFT, K_UP))
    gestionnaire = GestionnaireTouches(anciens_booleens)
    nouveaux_booleens = gestionnaire.indexes_vers_booleens((K_LEFT, K_DOWN, K_w))
    gestionnaire.actualiser_touches(nouveaux_booleens)
    assert(set(gestionnaire.indexes_ordonnes) == {K_LEFT, K_DOWN, K_w})

if __name__ == "__main__":
    tests.init()
    tests = (test_modulo, test_booleens_vers_indexes, test_indexes_vers_booleens, test_changement_touches,
             test_actualiser_touches)  # On cree un tuple avec toutes les fonctions de test
    for test in tests:
        print("")
        chaine = " du test \"{0}\"".format(test.__name__)  # On recupere le nom de chaque fonction de test
        print("Debut{0}...".format(chaine))  # Equivalent a "Debut du test \"" + nom_du_test + "\"..."
        test()  # On effectue le test
        print("Fin{0}".format(chaine))  # Equivalent a "Fin du test \"" + nom_du_test + "\""

    print("\nTous les test ont ete accomplis avec succes.")
