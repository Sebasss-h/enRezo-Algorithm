### Performe le TSP sur la graph entre les batiments avec la densité comme poids

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

        reseaux.append(sorted(T.edges(data=True)))

    return reseaux