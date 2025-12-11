### Calculate the optimal heat network in a given zone

from utils.import_db import import_db
from utils.split_db import split_db
from utils.projection_route import projection_route
from utils.create_graph import create_graph
from utils.tree import tree
from utils.tracer_reseau import tracer_reseau
from utils.export_reseau import export_reseau
from utils.calcul_perf import calcul_perf
from multiprocessing import Pool
import time
import csv

def worker_reseau(id_zone, bats, routes) :

    print(f"----- Calcul du réseau {id_zone} : {bats.shape[0]} batiments -----")

    # 3.1 - Projection des batiments sur les routes
    t_debut = time.time()
    bats, routes = projection_route(bats, routes)
    d_1 = time.time() - t_debut

    # 3.2 - Création du graph
    t_debut = time.time()
    G_list, bats  = create_graph(bats, routes)
    d_2 = time.time() - t_debut

    # 3.3 - MST
    t_debut = time.time()
    reseaux = tree(G_list, bats)
    d_3 = time.time() - t_debut

    # 3.4 - Tracer le réseau
    t_debut = time.time()
    reseau_final = tracer_reseau(reseaux, routes, bats, id_zone)
    d_4 = time.time() - t_debut

    # 3.5

    # 3.6 - Calcul des performances
    reseau_final_perf = calcul_perf(reseau_final, bats)

    #print(f'{id_zone}, {bats.shape[0]} batiments : proj={d_1}, graph={d_2}, tree={d_3}, trace={d_4}')
    with open('time.csv', 'a', newline='') as time_csv :
        spamwriter = csv.writer(time_csv, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([id_zone,bats.shape[0],d_1, d_2, d_3, d_4])

    return reseau_final_perf

def main() :

    # 1 - On importe nos base de données
    print("On importe nos base de données")
    bats_db, routes_db, crs = import_db()

    # 2 - On découpe nos base de données par zone d'interets
    print("On découpe nos base de données")
    data_liste = split_db(bats_db, routes_db)

    # 3 - On trace les réseaux pour chaque zone d'interets avec du multiprocessing
    print("On trace nos réseaux")
    with open('time.csv', 'w', newline='') as time_csv :
        spamwriter = csv.writer(time_csv, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['ID', 'NbBats', 'Proj', 'Graph', 'Tree', 'Trace'])
    
    with Pool(processes = 8) as pool :
        reseaux_finaux = pool.starmap(worker_reseau, data_liste)

    # Export
    print("Export")
    export_reseau(reseaux_finaux, crs)

if __name__ == '__main__':
    main()
