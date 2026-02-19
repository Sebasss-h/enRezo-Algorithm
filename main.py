### Calculate optimal heat network for given opportunity zone and its characteristics

from utils.import_db import import_db
from utils.split_db import split_db
from utils.projection_route import projection_route
from utils.creer_graph import creer_graph
from utils.tree import tree
from utils.tracer_reseau import tracer_reseau
from utils.calcul_perf import calcul_perf
from utils.export_reseau import export_reseau
from utils.merge_reseaux import merge_reseaux_cluster, merge_reseaux_combine
from utils.trim_leaves import trim_leaves
from utils.diametre import get_demande_totale

import argparse
from multiprocessing import Pool
import time
import csv

### Argument Parser for global variable ###

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbeux', help='Booleen pour afficher les informations textuels')
parser.add_argument('-t', '--trim', help='Booleen pour le trim des feuilles')
parser.add_argument('-m', '--merge', help='Booleen pour le merge des zones opportunite')
args = parser.parse_args()

if args.verbeux :
    verbeux = True
else : verbeux = False

if args.trim :
    trim = True
else : trim = False

if args.merge :
    merge = True
else : merge = False


### Definition des fonctions ###

def worker_calcul(id_zone, bats, routes) :
    # Premier worker pour le calcul en parallele : de la projection des batiments à l'arbre complet sur chaque zone

    if verbeux :
        print(f"----- Calcul du réseau {id_zone} : {bats.shape[0]} batiments -----")

    # 3.1 - Projection des batiments sur les routes
    td = time.time()
    bats, routes = projection_route(bats, routes)
    d1 = time.time() - td

    # 3.2 - Création des graph sur plusieurs clusters
    td = time.time()
    G_list, bats  = creer_graph(bats, routes)
    d2 = time.time() - td

    # 3.3 - Steiner
    td = time.time()
    reseaux = tree(G_list, bats)
    d3 = time.time() - td

    # 3.4 - Regrouper les graphs des clusters
    td = time.time()
    reseau = merge_reseaux_cluster(reseaux, routes)
    d4 = time.time() - td

    # On stock les temps de calcul
    with open('time.csv', 'a', newline='') as time_csv :
        spamwriter = csv.writer(time_csv, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([id_zone, 'calcul', bats.shape[0], d1, d2, d3, d4, 0, 0, 0])

    return (id_zone, reseau, bats, routes)

def worker_trace(id_zone, reseau, bats, routes) :
    # Deuxieme worker pour le calcul en parallele : du trim au calcul des performances

    if verbeux :
        print(f"----- Tracé du réseau {id_zone} : {bats.shape[0]} batiments -----")

    crs = routes.crs

    # 5.1 - On optimise le reseau en enlevant les feuilles qui baissent la densité
    td = time.time()
    if trim :
        reseau_trimmed = trim_leaves(reseau, bats)
    else :
        reseau_trimmed = reseau
    d5 = time.time() - td

    # 5.2 - On calcul la demande passant dans chaque canalisations
    td = time.time()
    reseau_demande_totale = get_demande_totale(reseau_trimmed)
    d6 = time.time() - td
    
    # 5.3 - Tracer le réseau
    td = time.time()
    reseau_linestring, reseau_gdf = tracer_reseau(reseau_demande_totale, routes, bats, id_zone, crs)
    d7 = time.time() - td

    # 5.4 - Calcul des performances
    reseau_linestring_perf = calcul_perf(reseau_linestring, bats)

    # On stock les temps de calcul
    with open('time.csv', 'a', newline='') as time_csv :
        spamwriter = csv.writer(time_csv, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([id_zone, 'trace', bats.shape[0], 0, 0, 0, 0, d5, d6, d7])

    return (reseau_linestring_perf, reseau_gdf)

def main() :

    t_total_debut = time.time()

    # 1 - On importe nos base de données
    print("On importe nos base de données")
    bats_db, routes_db, crs, diametre_table = import_db()

    # 2 - On découpe nos base de données par zone d'interets
    print("On découpe nos base de données")
    data_liste_calcul = split_db(bats_db, routes_db)

    # On initialise la base de donnée de temps
    with open('time.csv', 'w', newline='') as time_csv :
        spamwriter = csv.writer(time_csv, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['ID', 'Type', 'NbBats', 'Proj', 'Graph', 'Tree', 'Trace', 'Meta'])

    # 3 - On calcul les réseaux pour chaque zone d'interets avec du multiprocessing
    print("On calcul nos réseaux")
    with Pool(processes = 8) as pool :
        list_reseaux = pool.starmap(worker_calcul, data_liste_calcul)
    
    # 4 - Regrouper les reseaux pour lequels on augmente la densité
    if merge :
        print("On combine nos zones d'intérets")
        reseaux_merged = merge_reseaux_combine(list_reseaux, routes_db, min_density=1.5, max_length=500)
    else :
        reseaux_merged = list_reseaux
    
    # 5 - On trace les réseaux pour chaque zone d'interets avec du multiprocessing
    print("On trace nos réseaux")
    with Pool(processes = 8) as pool :
        reseaux_finaux = pool.starmap(worker_trace, reseaux_merged)
    
    # 6 - Export
    print("Export")
    export_reseau(reseaux_finaux, crs, diametre_table)

    t_total = time.time() - t_total_debut
    print(f'Temps de calcul : {t_total}')

if __name__ == '__main__':
    main()
