### Performe le TSP sur la graph entre les batiments avec la densité comme poids
from utils.trim_leaves import trim_leaves

import networkx as nx

def tree(G_list, bats, trim):

    terminals = bats["projection_route_coords"].tolist()

    reseaux = []

    for G in G_list:

        sub_terminals = [t for t in terminals if t in G.nodes]
        sub_terminals = list(dict.fromkeys(sub_terminals)) # On enleve les doublons

        if len(sub_terminals) == 0:
            reseaux.append(["empty"])
            continue
        elif len(sub_terminals) == 1:
            reseaux.append(("alone", sub_terminals[0]))
            continue

        T = nx.algorithms.approximation.steiner_tree(
                G, sub_terminals, weight='length', method='kou'
            )

        if trim :
            T_trimmed = trim_leaves(T, bats, terminals)
        else :
            T_trimmed = T

        if T_trimmed == [] :
            reseaux.append(["empty"])
        else :
            reseaux.append(sorted(T_trimmed.edges(data=True)))

    return reseaux