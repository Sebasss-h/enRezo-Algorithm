### Creer le graph simplifié des densité

import geopandas as gpd
import networkx as nx
import numpy as np
from sklearn.cluster import AgglomerativeClustering

def creer_graph(bats, routes) :

    routes[["start","end"]] = routes.apply(lambda x: give_ends(x), axis=1, result_type="expand")
    routes["length"] = routes.geometry.length

    G = create_G(routes)

    bats["projection_route_coords"] = bats.apply(lambda x: give_coords_point(x.projection_route, x.besoin_chaud_2025, G), axis = 1)
    
    G_list = get_components(G)

    return G_list, bats

def give_ends(row):
    # Retourne les sommets correspondants aux extremités de la route
    line_coords = list(row.geometry.coords) #Creer une liste des toute les coordonnées
    start = ','.join([str(round(x,0)) for x in line_coords[0]])
    end = ','.join([str(round(x,0)) for x in line_coords[-1]])
    return [start, end]

def give_coords_point(point, demande, G) :
    point = ','.join([str(round(x,0)) for x in point.coords[0]])
    point_proj = nearest_node(G, point)
    G.nodes[point_proj]["demande"] = demande
    return point_proj

def create_G(routes) :
    G = nx.Graph()
    _ = routes.apply(lambda x: G.add_edge(x.start, x.end, length=x.length, straight=False), axis=1)
    for n in G.nodes():
        G.nodes[n]["demande"] = 0
    return G

def nearest_node(G, point_str):
    # Convertir la chaîne 'x,y' en tuple float
    x, y = map(float, point_str.split(','))
    
    # Convertir les nœuds existants
    nodes = [tuple(map(float, n.split(','))) for n in G.nodes]
    
    # Trouver le plus proche
    dists = [((nx - x)**2 + (ny - y)**2) for nx, ny in nodes]
    return list(G.nodes)[dists.index(min(dists))]

def get_components(G, k_max=500):
    all_clusters = []

    # On trie les composants par taille pour traiter les gros en premier
    components = sorted(nx.connected_components(G), key=len, reverse=True)

    for comp in components:
        comp_list = list(comp)

        if len(comp_list) <= k_max:
            all_clusters.append(G.subgraph(comp_list).copy())
            continue

        # Si trop grand, on découpe
        sub_graphs = split_graph(G, comp_list, k_max)
        all_clusters.extend(sub_graphs)

    return all_clusters

def split_graph(G, nodes_subset, k_max):
    # Découpe un sous-graphe en utilisant la contrainte de connectivité.
    # Cela évite d'avoir des clusters 'bizarres' qui suivent la géométrie mais pas les routes.

    sub_G = G.subgraph(nodes_subset).copy()
    
    # On récupère les coordonnées pour le clustering
    # Note : L'ordre des nodes dans sub_G.nodes() est arbitraire, il faut figer l'ordre
    ordered_nodes = list(sub_G.nodes)
    coords = np.array([list(map(float, n.split(","))) for n in ordered_nodes])
        
    # Matrice de connectivité pour forcer le cluster à suivre les routes
    adjacency = nx.adjacency_matrix(sub_G)
    
    n_sub = int(np.ceil(len(ordered_nodes) / k_max))
    
    # Ward minimise la variance, connectivity force le respect du réseau
    model = AgglomerativeClustering(n_clusters=n_sub, linkage='ward', connectivity=adjacency)
    
    try:
        labels = model.fit_predict(coords)
    except UserWarning:
        # Fallback si la connectivité est trop fragmentée (rare si connected_components est fait avant)
        model = AgglomerativeClustering(n_clusters=n_sub)
        labels = model.fit_predict(coords)

    final_subgraphs = []
    
    # Reconstruction des sous-graphes
    for lab in set(labels):
        cluster_nodes = [ordered_nodes[i] for i in range(len(labels)) if labels[i] == lab]
        
        # IMPORTANT : Après un cut géométrique, on vérifie si on n'a pas créé de nouvelles îles
        # (Un cluster peut être coupé en deux morceaux non reliés par le cut)
        sg = sub_G.subgraph(cluster_nodes).copy()
        for comp in nx.connected_components(sg):
            final_subgraphs.append(sub_G.subgraph(comp).copy())
            
    return final_subgraphs