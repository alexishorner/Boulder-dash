"""
Module de test pour le module "blocs"
"""
import tests
from blocs import *


def test_adjacents():
    nombre_de_blocs_cote = 5
    milieu = int(nombre_de_blocs_cote**2 / 2.0)
    blocs = []
    for x in range(nombre_de_blocs_cote):
        for y in range(nombre_de_blocs_cote):
            bloc = Bloc(x, y)
            blocs.append(bloc)
    bloc_milieu = blocs[milieu]
    blocs_adjacents = bloc_milieu.blocs_adjacents(blocs)
    print(len(blocs_adjacents))
    assert(len(blocs_adjacents) == 8)


if __name__ == "__main__":
    tests.init()
    tests = (test_adjacents,)  # On cree un tuple avec toutes les fonctions de test
    for test in tests:
        print("")
        chaine = " du test \"{0}\"".format(test.__name__)  # On recupere le nom de chaque fonction de test
        print("Debut{0}...".format(chaine))  # Equivalent a "Debut du test \"" + nom_du_test + "\"..."
        test()  # On effectue le test
        print("Fin{0}".format(chaine))  # Equivalent a "Fin du test \"" + nom_du_test + "\""
