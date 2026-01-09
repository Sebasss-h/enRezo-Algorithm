### Enleve les feuilles qui diminuent la densité

import networkx as nx

def trim_leaves(G, bats, terminals) :
    leaves = get_leaves(G, terminals)
    for leaf in leaves :
        parents = get_parents(G, leaf)
        G = lower_density(G, bats, parents)
    return G

def get_leaves(G, terminals) :
    # Retourne les noeuds de degree 1
    leaves = [n for n in G.nodes() if G.degree(n) == 1 if n in terminals]
    return leaves

def get_parents(G, leaf) :
    parents = [leaf]
    parent = list(G.neighbors(leaf))[0]
    while G.degree(parent) == 2 :
        parents.append(parent)
        parent = [n for n in G.neighbors(parent) if (n not in parents)][0]
    return parents

def lower_density(G, bats, parents):
    G2 = G.copy()

    length_total = sum(a['length'] for _,_,a in G2.edges(data=True))
    heat_total = bats.besoin_chaud_2025.sum()
    if length_total == 0 :
        density_total = 0
    else :
        density_total = heat_total/length_total
    
    for parent in parents :
        G2.remove_node(parent)
    
    length_new = sum(a['length'] for _,_,a in G2.edges(data=True))
    heat_new = heat_total - bats[bats["projection_route_coords"].isin(parents)].besoin_chaud_2025.sum()
    if length_new == 0 :
        density_new = 0
    else :
        density_new = heat_new/length_new
    
    if density_new > density_total :
        return G2
    else :
        return G