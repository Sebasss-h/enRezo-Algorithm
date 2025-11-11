### Calculate the optimal heat network in a given zone

from utils.import_db import import_db
from utils.split_db import split_db
from utils.projection_route import projection_route
from utils.create_graph import create_graph
from utils.tsp import tsp
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
    for i in range(len(bats_liste)) :

        print(f"Calcul du réseau {i}")

        bats = bats_liste[i]
        routes = routes_liste[i]

        # 3 - Projection des batiments sur les routes
        bats, routes = projection_route(bats, routes)

        # 4 - Création du graph
        G, path_dict = create_graph(bats, routes)

        # 5 - TSP
        reseau = tsp(G)

        # 6 - Tracer le réseau
        reseau_final = tracer_reseau(reseau, path_dict, routes)

        reseaux_finaux.append(reseau_final)

    # 7 - Export
    print("Export")
    export_reseau(id_zone_liste, reseaux_finaux)

if __name__ == '__main__':
    main()
