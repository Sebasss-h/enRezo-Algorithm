# Combine les reseauux : soit de cluster différents dans une même zone, ou de deux zones différentes

from utils.creer_graph import give_ends

import shapely as shp
import numpy as np
import geopandas as gpd
import networkx as nx

def merge_reseaux_cluster(reseaux, routes) :
    # Combine les réseaux des différents clusters

    while len(reseaux) != 1 :

        T_1 = reseaux.pop(0)

        n1_f = None
        n2_f = None
        i2_f = None
        T_2_f = None
        min_length = np.inf
        
        for i2 in range(len(reseaux)) :

            T_2 = reseaux[i2]

            n1, n2, length = get_closest_nodes(T_1, T_2)

            if length < min_length :
                n1_f = n1
                n2_f = n2
                i2_f = i2
                T_2_f = T_2
                min_length = length
            
        route = get_route(n1_f, n2_f, routes, min_length)

        new_T = nx.compose(nx.compose(T_1, T_2_f), route)

        reseaux = [j for i, j in enumerate(reseaux) if i != i2_f]

        reseaux.append(new_T)

    return reseaux[0]

def merge_reseaux_combine(reseaux, routes, min_density = 1.5, max_length = 500, iteration = 3000) :
    # Combine les réseaux des différentes zone si la desnité resultante est superieur au seuil

    for _ in range(iteration) :

        nb_reseaux = len(reseaux)

        i1 = np.random.randint(0, nb_reseaux)
        i2 = np.random.randint(0, nb_reseaux)

        if i1 != i2 :

            id_zone_1, T_1, bats_1, routes_1 = reseaux[i1]
            id_zone_2, T_2, bats_2, routes_2 = reseaux[i2]

            n1, n2, length = get_closest_nodes(T_1, T_2)
            if length > max_length :
                continue
            
            route = get_route(n1, n2, routes, length)

            new_density = get_new_density(T_1, T_2, route)
            if new_density > min_density :
                                
                new_id_zone = id_zone_1
                new_T = nx.compose(nx.compose(T_1, T_2), route)
                new_bats = gpd.concat([bats_1, bats_2])
                new_routes = gpd.concat([routes_1, routes_2])

                reseaux = [j for i, j in enumerate(reseaux) if i not in [i1, i2]]

                reseaux.append((new_id_zone, new_T, new_bats, new_routes))

    return reseaux

def get_closest_nodes(T_1, T_2) :
    # Retourne le couple de noeuds donnant la distance la plus petite entre les deux graphs

    n1 = ''
    n2 = ''
    min_length = np.inf

    for n_i in T_1.nodes() :
        for n_j in T_2.nodes() :

                x_i, y_i = map(float, n_i.split(','))
                x_j, y_j = map(float, n_j.split(','))

                length = np.sqrt(((x_i - x_j)**2 + (y_i - y_j)**2))

                if length < min_length :
                    n1 = n_i
                    n2 = n_j
                    min_length = length

    return n1, n2, min_length

def get_route(n1, n2, routes, straight_length) :
    # Retourne la route la plus courte entre les deux sommets

    # Clip routes
    k = 50

    x1, y1 = map(float, n1.split(','))
    x2, y2 = map(float, n2.split(','))

    x = [x1, x2]
    y = [y1, y2]

    minx = min(x) - k
    miny = min(y) - k
    maxx = max(x) + k
    maxy = max(y) + k

    boundary = shp.Polygon([[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]])

    routes_clip = gpd.clip(routes, boundary, keep_geom_type=True).explode()

    # Generer le graph
    G_routes = nx.Graph()
    routes_clip[["start","end"]] = routes_clip.apply(lambda x: give_ends(x), axis=1, result_type="expand")
    routes_clip["length"] = routes_clip.geometry.length
    _ = routes_clip.apply(lambda x: G_routes.add_edge(x.start, x.end, length=x.length), axis=1)

    # Calcul du plus court chemin
    straight = False
    try :
        route_edges = nx.astar_path(G_routes, n1, n2)
    except :
        straight = True

    # Convertir en Graph
    route = nx.Graph()
    if straight :
        route.add_edge(n1, n2, length=straight_length, straight=True)
    else :
        for i in range(len(route_edges)-1) :
            p1, p2 = route_edges[i], route_edges[i+1] 
            length = G_routes[p1][p2]["length"]
            route.add_edge(p1, p2, length=length, straight=False)
    
    for n in route.nodes() :
        route.nodes[n]["demande"] = 0

    return route

def get_new_density(T_1, T_2, route) :
    # Calcul la densite su nouveau reseau qui contient les deux zones

    demande_1 = sum(a['length'] for _,_,a in T_1.edges(data=True))
    demande_2 = sum(a['length'] for _,_,a in T_2.edges(data=True))
    new_besoin_chaleur = demande_1 + demande_2

    length_1 = sum(a['length'] for _,_,a in T_1.edges(data=True))
    length_2 = sum(a['length'] for _,_,a in T_2.edges(data=True))
    length_route = sum(a['length'] for _,_,a in route.edges(data=True))
    new_length = length_1 + length_2 + length_route

    new_density = new_besoin_chaleur / new_length
    return new_density