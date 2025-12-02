### Performe le TSP sur la graph entre les batiments avec la densité comme poids

import networkx as nx

def tree(G_list, bats) :

    terminals = bats["projection_route_coords"].to_list()

    reseaux = []

    for G in G_list :
        mst = nx.algorithms.approximation.steiner_tree
        T = mst(G, terminals, weight='length', method='kou')

        reseau = sorted(T.edges(data=True))
        reseaux.append(reseau)

    return reseaux