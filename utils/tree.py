### Performe le TSP sur la graph entre les batiments avec la densité comme poids

from utils.trim_leaves import trim_leaves

import networkx as nx

def tree(G_list, bats):

    terminals = bats["projection_route_coords"].tolist()

    reseaux = []

    for G in G_list:

        sub_terminals = [t for t in terminals if t in G.nodes]

        if len(sub_terminals) <= 1:
            continue

        T = nx.algorithms.approximation.steiner_tree(
                G, sub_terminals, weight='length', method='kou'
            )
        
        T_trimed = trim_leaves(T, bats, terminals)

        reseaux.append(sorted(T_trimed.edges(data=True)))
    return reseaux