### Split the big geodb for batiments and roads into a list of geodb for each zone of interest

import geopandas as gpd
import shapely as shp

def split_db(bats_db, routes_db) :
    ### return list of (bats, routes) for every zone

    id_zone_liste = bats_db.id_zone.unique()
    bats_liste = []
    routes_liste = []
    for id_zone in id_zone_liste :
        
        bats = bats_db.where(bats_db.id_zone == id_zone).dropna()
        bats_liste.append(bats)

        bats_boundary = get_boundaries(bats)
        route = gpd.clip(routes_db, bats_boundary, keep_geom_type=True)

        route = route.explode(ignore_index=True)

        routes_liste.append(route)

    return id_zone_liste, bats_liste, routes_liste

def get_boundaries(gdf) :

    boundaries = gdf.geometry.bounds

    minx = boundaries.minx.min() - 100
    miny = boundaries.miny.min() - 100
    maxx = boundaries.maxx.max() + 100
    maxy = boundaries.maxy.max() + 100

    boundary = shp.Polygon([[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]])

    return boundary