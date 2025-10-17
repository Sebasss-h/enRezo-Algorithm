### Calculate the optimal heat network in a given zone

from utils.import_db import import_db
from utils.projection_route import projection_route
from utils.create_graph import create_graph
from utils.tsp import tsp
from utils.tracer_reseau import tracer_reseau
from utils.export_reseau import export_reseau

def main() :
    
    # 1 - On importe nos base de données
    print("1 - On importe nos base de données")
    bats, routes = import_db()

    # 2 - Projection des batiments sur les routes
    print("2 - Projection des batiments sur les routes")
    bats, routes = projection_route(bats, routes)

    # 3 - Création du graph
    print("3 - Création du graph")
    G, path_dict = create_graph(bats, routes)

    # 4 - TSP
    print("4 - TSP")
    reseau = tsp(G)

    # 5 - Tracer le réseau
    print("5 - Tracer le réseau")
    reseau_final = tracer_reseau(reseau, path_dict, routes)

    # 6 - Export
    print("6 - Export")
    export_reseau(bats, reseau_final)

if __name__ == '__main__':
    main()
