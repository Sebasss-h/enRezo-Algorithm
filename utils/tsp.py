### Performe le TSP sur la graph entre les batiments avec la densité comme poids

import networkx as nx

def tsp(G) :
    tsp = nx.approximation.traveling_salesman_problem
    reseau = tsp(G, weight='weight', cycle=True, method=nx.approximation.greedy_tsp)
    return reseau