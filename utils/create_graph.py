### Creer le graph simplifié des densité

import geopandas as gpd
import networkx as nx

def create_graph(bats, routes) :

    routes[["start","end"]] = routes.apply(lambda x: give_ends(x), axis=1, result_type="expand")
    routes["length"] = routes.geometry.length

    G_total = create_G_total(routes)

    bats["projection_route_coords"] = bats.projection_route.apply(lambda x: give_coords_point(x, G_total))

    G_final = create_G_final(bats, G_total)

    return G_final

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

def create_G_total(routes) :
    G_total = nx.Graph()
    _ = routes.apply(lambda x: G_total.add_edge(x.start, x.end, length=x.length), axis=1)
    return G_total

def nearest_node(G, point_str):
    # Convertir la chaîne 'x,y' en tuple float
    x, y = map(float, point_str.split(','))
    
    # Convertir les nœuds existants
    nodes = [tuple(map(float, n.split(','))) for n in G.nodes]
    
    # Trouver le plus proche
    dists = [((nx - x)**2 + (ny - y)**2) for nx, ny in nodes]
    return list(G.nodes)[dists.index(min(dists))]

def create_G_final(bats, G_total) :
    G_final = nx.Graph()

    for i, target in bats.iterrows() :
        proj_t = target.projection_route_coords

        for j, source in bats.iterrows() :
            if j != i:
                proj_s = source.projection_route_coords

                path = nx.astar_path(G_total, proj_s, proj_t, weight="length")
                length = nx.astar_path_length(G_total, proj_s, proj_t, weight="length")

                G_final.add_edge(proj_s, proj_t, weight = length, path=path)
    
    return G_final