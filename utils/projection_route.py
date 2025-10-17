### Projette les batiments sur la route la plus proche

import geopandas as gpd
import shapely

def projection_route(bats, routes) :
    bats["projection_route"] = bats.geometry.apply(lambda x : find_proj_route(x, routes))
    routes = routes.explode()
    return bats, routes

def find_proj_route(poly, routes) :
    ### return the projection of the polygon on the nearest line
    ### and the id of this line
    ### and split routes at the projection point
    lines = routes.copy()
    lines["line"] = lines.geometry.apply(lambda r : shapely.shortest_line(poly, r))
    lines["length"] = lines["line"].apply(shapely.length)
    min_id = lines["length"].idxmin()

    route = routes.iloc[min_id].geometry
    proj = shapely.Point(lines["line"][min_id].coords[-1])
    route = shapely.ops.snap(route, proj, tolerance=0.0001)
    split_route = shapely.ops.split(route, proj)
    routes.loc[min_id, "geometry"] = split_route
    routes.explode('geometry')

    return proj