### Performe le TSP sur la graph entre les batiments avec la densité comme poids

import networkx as nx

def tree(G) :
    mst = nx.minimum_spanning_tree
    T = mst(G, weight='weight', algorithm='kruskal')
    reseau = sorted(T.edges(data=True))
    return reseau