### Trace le réseau de chaleur à partir du resultat du tsp

import pandas as pd
import geopandas as gpd
import shapely as shp

def tracer_reseau(reseaux, routes, id_zone) :
    reseaux_linestring = creer_reseaux_linestring(reseaux, routes, id_zone)
    reseau_linestring = concat_reseaux_linestring(reseaux_linestring, id_zone)
    return reseau_linestring


def creer_reseaux_linestring(reseaux, routes, id_zone) :
    
    reseaux_linestring_gdf = []

    for reseau in reseaux :

        reseau_linestring = []

        for edge in reseau :
            p1 = edge[0]
            p2 = edge[1]

            route = routes[((routes["start"] == p1) & (routes["end"] == p2)) | ((routes["start"] == p2) & (routes["end"] == p1))]
            if not route.empty :
                reseau_linestring.append(route.geometry.values[0])
        
        if reseau_linestring != [] :
            reseau_multilinestring = shp.MultiLineString(reseau_linestring)
            reseau_linestring = gpd.GeoDataFrame(geometry=gpd.GeoSeries(reseau_multilinestring))
            reseau_linestring['id_zone'] = id_zone
            reseaux_linestring_gdf.append(reseau_linestring)

    if reseaux_linestring_gdf != [] :
        reseaux_linestring_gdf = pd.concat(reseaux_linestring_gdf, ignore_index=True)
    else :
        reseaux_linestring_gdf = gpd.GeoDataFrame()
    
    return reseaux_linestring_gdf

def concat_reseaux_linestring(reseaux_linestring, id_zone):

    if len(reseaux_linestring.index) == 0 :
        return gpd.GeoDataFrame()

    reseau_linestring = reseaux_linestring

    nb_comp = reseaux_linestring.shape[0]
    reseau_linestring_geometries = reseaux_linestring.geometry
    reseau_linestring_geometry = reseau_linestring_geometries.pop(0)

    for _ in range(nb_comp - 1):
        lines_between_reseaux = reseau_linestring_geometries.shortest_line(reseau_linestring_geometry)

        lines_between_reseaux = lines_between_reseaux.reset_index(drop=True)
        length_between_reseaux = lines_between_reseaux.geometry.length.reset_index(drop=True)

        closest_id = length_between_reseaux.idxmax()

        if closest_id not in lines_between_reseaux.index:
            closest_id = 0

        closest_line = shp.MultiLineString([lines_between_reseaux.loc[closest_id]])

        closest_reseau = reseau_linestring.loc[closest_id, 'geometry']
        reseau_linestring = reseau_linestring.drop(index=closest_id).reset_index(drop=True)
        reseau_linestring_geometries = reseau_linestring.geometry

        reseau_linestring_geometry = shp.unary_union(
            gpd.GeoSeries([reseau_linestring_geometry, closest_line, closest_reseau])
        )

    reseau_linestring = gpd.GeoDataFrame(geometry=gpd.GeoSeries(reseau_linestring_geometry))
    reseau_linestring['id_zone'] = id_zone

    return reseau_linestring
