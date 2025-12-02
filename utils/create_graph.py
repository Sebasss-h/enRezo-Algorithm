### Creer le graph simplifié des densité

import geopandas as gpd
import networkx as nx

def create_graph(bats, routes) :

    routes[["start","end"]] = routes.apply(lambda x: give_ends(x), axis=1, result_type="expand")
    routes["length"] = routes.geometry.length

    G = create_G(routes)

    bats["projection_route_coords"] = bats.projection_route.apply(lambda x: give_coords_point(x, G))

    G_list = get_components(G)

    return G_list, bats

def give_ends(row):
    """A function to return a list of comma separated strings of rounded start and end coordinates,
    Example: ['623373.0,6903082.0', '623386.0,6902378.0']"""
    line_coords = list(row.geometry.coords) #Create a list of all line coordinates
    start = ','.join([str(round(x,0)) for x in line_coords[0]]) #A string, like '623373.0,6903082.0'
    end = ','.join([str(round(x,0)) for x in line_coords[-1]])
    return [start, end]

def give_coords_point(point, G) :
    point = ','.join([str(round(x,0)) for x in point.coords[0]])
    point_proj = nearest_node(G, point)
    return point_proj

def create_G(routes) :
    G = nx.Graph()
    _ = routes.apply(lambda x: G.add_edge(x.start, x.end, length=x.length), axis=1)
    return G

def nearest_node(G, point_str):
    # Convertir la chaîne 'x,y' en tuple float
    x, y = map(float, point_str.split(','))
    
    # Convertir les nœuds existants
    nodes = [tuple(map(float, n.split(','))) for n in G.nodes]
    
    # Trouver le plus proche
    dists = [((nx - x)**2 + (ny - y)**2) for nx, ny in nodes]
    return list(G.nodes)[dists.index(min(dists))]

def get_components(G, k = 300) :

    components_nodes = nx.connected_components(G)

    components = [G.subgraph(x) for x in components_nodes]

    return components