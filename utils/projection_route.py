### Projette les batiments sur la route la plus proche

import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import LineString, Point

def projection_route(bats, routes):
    """
    Projette tous les bâtiments sur leur route la plus proche et met à jour le GeoDataFrame routes.
    """
    new_routes = routes.copy()

    projections = []
    for geom in bats.geometry:
        proj, new_routes = find_proj_route(geom, new_routes)
        projections.append(proj)

    bats["projection_route"] = projections

    # Exploser les MultiLineString si nécessaire (déjà fait dans find_proj_route)
    new_routes = new_routes.explode(ignore_index=True)

    return bats, new_routes

def find_proj_route(poly, routes):
    """
    Projette un bâtiment sur la route la plus proche, découpe la route au point projeté,
    et met à jour le GeoDataFrame routes en explosant les morceaux si nécessaire.
    """
    lines = routes.copy()
    lines["line"] = lines.geometry.apply(lambda r: shapely.shortest_line(poly, r))
    lines["length"] = lines["line"].apply(shapely.length)
    min_id = lines["length"].idxmin()

    # Route à découper
    route = routes.loc[min_id, "geometry"]

    # Si route est MultiLineString, prendre le premier segment
    if route.geom_type == "MultiLineString":
        route = LineString(route.geoms[0])

    # Point de projection
    proj = Point(lines.loc[min_id, "line"].coords[-1])
    proj = shapely.ops.snap(proj, route, tolerance=0.0001)

    # Split de la route au point projeté
    split_route = shapely.ops.split(route, proj)

    # Remplacer la ligne originale par tous les morceaux du split
    split_lines = [geom for geom in split_route.geoms if geom.geom_type == "LineString"]

    # Supprimer la route originale
    routes = routes.drop(index=min_id)

    # Ajouter les nouveaux morceaux au GeoDataFrame
    new_rows = gpd.GeoDataFrame(geometry=split_lines, crs=routes.crs)
    routes = pd.concat([routes, new_rows], ignore_index=True)

    return proj, routes