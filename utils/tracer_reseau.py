### Trace le réseau de chaleur à partir du resultat du tsp

import pandas as pd
import geopandas as gpd
import shapely as shp

def tracer_reseau(reseaux, routes, bats, id_zone) :

    reseaux_linestring = creer_reseaux_linestring(reseaux, routes, id_zone)
    reseau_linestring = concat_reseaux_linestring(reseaux_linestring, id_zone)

    if len(reseaux_linestring.index) == 0 :
        reseau_linestring = reseau_batiments_sans_route(bats.copy(), id_zone)
    else :
        reseau_linestring = rattacher_orphelins(reseau_linestring, bats, id_zone)
    
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

        closest_id = length_between_reseaux.idxmin()

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

def reseau_batiments_sans_route(bats, id_zone) :

    nb_bats = bats.shape[0]
    bats_geometries =  bats.geometry
    bats = bats.reset_index(drop=True)
    bats_geometry = bats.geometry.iloc[0]
    bats = bats.drop(index=0).reset_index(drop=True)
    bats_geometries = bats.geometry

    lines = []

    for _ in range(nb_bats- 1):
        lines_between_bats = bats_geometries.shortest_line(bats_geometry)

        lines_between_bats = lines_between_bats.reset_index(drop=True)
        length_between_bats = lines_between_bats.geometry.length.reset_index(drop=True)

        closest_id = length_between_bats.idxmin()

        if closest_id not in lines_between_bats.index:
            closest_id = 0
        
        lines.append(lines_between_bats.loc[closest_id])

        bats = bats.drop(index=closest_id).reset_index(drop=True)
        bats_geometries = bats.geometry

    reseau_bats_linestring = shp.MultiLineString(lines)

    reseau_bats = gpd.GeoDataFrame(geometry=gpd.GeoSeries(reseau_bats_linestring))
    reseau_bats['id_zone'] = id_zone

    return reseau_bats

def rattacher_orphelins(reseau_gdf, bats, id_zone):
    if reseau_gdf.empty or bats.empty:
        return reseau_gdf

    reseau_union = reseau_gdf.geometry.unary_union
    
    lignes_raccord = []

    for idx, bat in bats.iterrows():
        point_acces = bat["projection_route"]
        
        if reseau_union.distance(point_acces) > 0.1:
            
            ligne = shp.shortest_line(point_acces, reseau_union)
            lignes_raccord.append(ligne)

    if lignes_raccord:
        raccords_gdf = gpd.GeoDataFrame(geometry=lignes_raccord, crs=reseau_gdf.crs)
        raccords_gdf['id_zone'] = id_zone
        
        reseau_final = pd.concat([reseau_gdf, raccords_gdf], ignore_index=True)
        return reseau_final
    
    return reseau_gdf