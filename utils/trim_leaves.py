### Enleve les feuilles qui baissent la densité

import networkx as nx

def trim_leaves(G, bats, terminals) :
    leaves = get_leaves(G, terminals)
    for leaf in leaves :
        parents = get_parents(G, leaf)
        if lower_density(G, parents, bats) :
            G = remove_parents(G, parents)
    return G

def get_leaves(G, terminals) :
    # Retourne tous les neouds de degré 1
    leaves = [x for x in G.nodes() if G.degree(x)==1]
    bats_leaves = [l for l in leaves if l in terminals]
    return bats_leaves

def get_parents(G, leaf) :
    # Retourne les parents de degré 2, on remonte la chaine
    parent = list(G.neighbors(leaf))[0]
    parents = [leaf]
    while G.degree(parent) == 2 :
        parents.append(parent)
        parent = [n for n in G.neighbors(parent) if (n not in parents)][0]
    return parents

def lower_density(G, parents, bats) :
    # Verifie si enlever cette "feuille" diminue la densité globale
    G_new = G.copy()
    length_total = sum(a['length'] for _,_,a in G_new.edges(data=True))
    heat_total = bats.besoin_chaud_2025.sum()
    if length_total == 0 :
        density_total = 0
    else :
        density_total = heat_total/length_total

    for parent in parents :
        G_new.remove_node(parent)
    length_new = sum(a['length'] for _,_,a in G_new.edges(data=True))
    heat_new = heat_total - bats[bats["projection_route_coords"].isin(parents)].besoin_chaud_2025.sum()
    if length_new == 0 :
        density_new = 0
    else :
        density_new = heat_new/length_new

    if density_new >= density_total :
        return True
    else :
        return False

def remove_parents(G, parents) :
    G = nx.Graph(G)
    for parent in parents :
        G.remove_node(parent)
    return G