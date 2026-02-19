### Approxime l'arbre couvrant minimum sur la graph entre les batiments

import networkx as nx

def tree(G_list, bats):

    terminals = bats["projection_route_coords"].tolist()

    reseaux = []

    for G in G_list:

        sub_terminals = [t for t in terminals if t in G.nodes]
        sub_terminals = list(dict.fromkeys(sub_terminals)) # On enleve les doublons

        if len(sub_terminals) == 0:
            continue
        elif len(sub_terminals) == 1:
            reseaux.append(G.subgraph(sub_terminals))
            continue

        T = nx.algorithms.approximation.steiner_tree(
                G, sub_terminals, weight='length', method='kou'
            )
        
        if nx.is_empty(T) :
            continue
        else :
            G = copy_graph(T)
            reseaux.append(G)

    return reseaux

def copy_graph(G):
    
    new_G = nx.Graph()
    
    # 1. Copie des noeuds (sans fonctions)
    for n, attr in G.nodes(data=True):
        safe_attr = {k: v for k, v in attr.items() if not callable(v)}
        new_G.add_node(n, **safe_attr)
        
    # 2. Copie des arêtes (sans fonctions)
    for u, v, attr in G.edges(data=True):
        safe_attr = {k: v for k, v in attr.items() if not callable(v)}
        new_G.add_edge(u, v, **safe_attr)
    
    return new_G