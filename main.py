### Calculate the optimal heat network in a given zone

from utils.import_db import import_db
from utils.split_db import split_db
from utils.projection_route import projection_route
from utils.create_graph import create_graph
from utils.tree import tree
from utils.tracer_reseau import tracer_reseau
from utils.export_reseau import export_reseau

def main() :

    # 1 - On importe nos base de données
    print("On importe nos base de données")
    bats_db, routes_db = import_db()

    # 2 - On découpe nos base de données par zone d'interets
    print("On découpe nos base de données")
    id_zone_liste, bats_liste, routes_liste = split_db(bats_db, routes_db)

    reseaux_finaux = []

    # On trace les réseaux pour chaque zone d'interets

    N = len(bats_liste)
    for i in range(N) :

        print(f"----- Calcul du réseau {i+1}/{N} -----")

        id_zone = id_zone_liste[i]
        bats = bats_liste[i]
        routes = routes_liste[i]

        print(f'Nombre de batiments : {bats.shape[0]}')

        # 3 - Projection des batiments sur les routes
        bats, routes = projection_route(bats, routes)

        # 4 - Création du graph
        G  = create_graph(bats, routes)

        # 5 - TSP
        reseau= tree(G)

        # 6 - Tracer le réseau
        reseau_final = tracer_reseau(reseau, routes, id_zone)

        reseaux_finaux.append(reseau_final)

    # 7 - Export
    print("Export")
    export_reseau(reseaux_finaux)

if __name__ == '__main__':
    main()
