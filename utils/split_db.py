### Split the big geodb for batiments and roads into a list of geodb for each zone of interest

import geopandas as gpd
import shapely as shp

def split_db(bats_db, routes_db) :
    ### return list of (bats, routes) for every zone

    id_zone_liste = bats_db.id_zone.unique()

    # liste des données sous la forme [...., (id_zone, bats, routes), ....]
    data_liste = []

    for id_zone in id_zone_liste :
        
        bats = bats_db.where(bats_db.id_zone == id_zone).dropna()

        bats_boundary = get_boundaries(bats)
        routes = gpd.clip(routes_db, bats_boundary, keep_geom_type=True)

        routes = routes.explode(ignore_index=True)

        data_liste.append((id_zone, bats, routes))

    return data_liste

def get_boundaries(gdf) :

    boundaries = gdf.geometry.bounds

    minx = boundaries.minx.min() - 200
    miny = boundaries.miny.min() - 200
    maxx = boundaries.maxx.max() + 200
    maxy = boundaries.maxy.max() + 200

    boundary = shp.Polygon([[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]])

    return boundary