### Calcul le diametre de chaue troncon de route pour un reseau

import networkx as nx

def get_diametre(reseau, diametre_table) :
    reseau['diametre'] = reseau['demande_total'].apply(lambda x : diametre_from_demande(x, diametre_table))
    return reseau

def diametre_from_demande(x, diametre_table) :
    if x < diametre_table['E (MWh)'].max() :
        diametres = diametre_table[diametre_table['E (MWh)'] > x]
        diametre = diametres[diametres['E (MWh)'] == diametres['E (MWh)'].min()]['Diamètre Nominal (DN)'].values[0]
    else :
        diametre = diametre_table.loc[diametre_table['E (MWh)'].idxmax()]['Diamètre Nominal (DN)']
    return diametre

def get_demande_totale(T):
    source = get_source(T)

    T_directed = nx.bfs_tree(T, source)

    for n in T_directed.nodes():
        d_locale = T.nodes[n].get("demande", 0)
        T_directed.nodes[n]["demande_locale"] = d_locale
        T_directed.nodes[n]["demande_totale"] = d_locale

    for u, v in T_directed.edges():
        if T.has_edge(u, v):
            data = T.edges[u, v]
        else:
            data = T.edges[v, u]
        T_directed.edges[u, v].update(data)

    ordre_remontee = list(nx.dfs_postorder_nodes(T_directed, source))

    for node in ordre_remontee:
        if node == source:
            continue
        
        try:
            parent = list(T_directed.predecessors(node))[0]
            
            demande_accumulee_noeud = T_directed.nodes[node]["demande_totale"]
            
            T_directed.nodes[parent]["demande_totale"] += demande_accumulee_noeud
            
            T_directed.edges[parent, node]["demande_total"] = demande_accumulee_noeud
            
        except IndexError:
            pass

    return T_directed

def get_source(T):
    nodes = list(T.nodes)
    if not nodes: return None
    source = max(nodes, key=lambda n: T.nodes[n].get("demande", 0))
    return source