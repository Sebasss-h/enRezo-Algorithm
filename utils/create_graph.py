### Creer le graph simplifié des densité

import geopandas as gpd
import networkx as nx

def create_graph(bats, routes) :

    bats["projection_route_coords"] = bats.projection_route.apply(lambda x: give_coords_point(x))

    routes[["start","end"]] = routes.apply(lambda x: give_ends(x), axis=1, result_type="expand")
    routes["length"] = routes.geometry.length

    G_total = create_G_total(routes)

    G_final, path_dict = create_G_final(bats, G_total)

    return G_final, path_dict

def give_ends(row):
    """A function to return a list of comma separated strings of rounded start and end coordinates,
    Example: ['623373.0,6903082.0', '623386.0,6902378.0']"""
    line_coords = list(row.geometry.coords) #Create a list of all line coordinates
    start = ','.join([str(round(x,0)) for x in line_coords[0]]) #A string, like '623373.0,6903082.0'
    end = ','.join([str(round(x,0)) for x in line_coords[-1]])
    return [start, end]

def give_coords_point(point) :
    point = ','.join([str(round(x,0)) for x in point.coords[0]])
    return point

def create_G_total(routes) :
    G_total = nx.Graph()
    _ = routes.apply(lambda x: G_total.add_edge(x.start, x.end, length=x.length), axis=1)
    return G_total

def create_G_final(bats, G_total) :
    G_final = nx.DiGraph()
    path_dict = {}

    for i, target in bats.iterrows() :
        proj_t = target.projection_route_coords
        conso_t = target.besoin_chaud_2025

        for j, source in bats.iterrows() :
            if j != i:
                proj_s = source.projection_route_coords
            
                path = nx.astar_path(G_total, proj_s, proj_t, weight="length")
                length = nx.astar_path_length(G_total, proj_s, proj_t, weight="length")

                G_final.add_edge(proj_s, proj_t, weight = conso_t/length, path = path)

                path_dict[(proj_s,proj_t)] = path
    
    return G_final, path_dict