### Transforme l'arbre sous forme de graph en un objet shapely geometrique

import geopandas as gpd
import shapely as shp

def tracer_reseau(reseau, routes, bats, id_zone, crs) :

    reseau_linestring, reseau_gdf = creer_reseaux_linestring(reseau, routes, id_zone, crs)

    if reseau_linestring.empty :
        reseau_linestring, reseau_gdf = reseau_batiments_sans_route(bats.copy(), id_zone, crs)
    
    return reseau_linestring, reseau_gdf


def creer_reseaux_linestring(reseau, routes, id_zone, crs) :
    # Retourne un linestring (ou point pour les batiments seuls) du reseau
    
    if len(reseau.nodes()) == 0 :
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()
    elif len(reseau.nodes()) == 1 :
        x, y = map(float, sorted(reseau.nodes())[0].split(','))
        return gpd.GeoDataFrame([{'geometry':shp.Point(x, y), 'id_zone':id_zone, 'demande_total':0}], crs=crs), gpd.GeoDataFrame([{'geometry':shp.Point(x, y), 'id_zone':id_zone, 'demande_total':0}], crs=crs)

    liste_troncon = []

    for edge in sorted(reseau.edges(data=True)):
        p1 = edge[0]
        p2 = edge[1]

        demande_total = edge[2]["demande_total"]

        geometry = NotImplemented
        if edge[2]["straight"] :
            x1, y1 = map(float, p1.split(','))
            x2, y2 = map(float, p2.split(','))
            geometry = shp.LineString([(x1, y1), (x2, y2)])
        else :
            route = routes[((routes["start"] == p1) & (routes["end"] == p2)) | ((routes["start"] == p2) & (routes["end"] == p1))]
            if not route.empty :
                geometry = route.geometry.values[0]
        
        if geometry is not None :
            liste_troncon.append({'geometry':geometry,
                                  'id_zone':id_zone,
                                  'demande_total':demande_total})
        
    if liste_troncon :

        reseau_multilinestring = shp.MultiLineString([troncon["geometry"] for troncon in liste_troncon])
        reseau_linestring = gpd.GeoDataFrame(geometry=gpd.GeoSeries(reseau_multilinestring), crs=crs)
        reseau_linestring['id_zone'] = id_zone 

        reseau_gdf = gpd.GeoDataFrame(liste_troncon)
        reseau_gdf.set_crs(crs, inplace=True)

        return reseau_linestring, reseau_gdf
    else :
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()

def reseau_batiments_sans_route(bats, id_zone, crs) :
    # Relie les batiments qui ne sont pas reliable par une route via une ligne droite

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
        
        shortest_line = lines_between_bats.iloc[closest_id]

        bats = bats.drop(index=closest_id).reset_index(drop=True)
        demande_total = bats.besoin_chaud_2025
        bats_geometries = bats.geometry

        lines.append({"geometry":shortest_line,
                      "id_zone":id_zone,
                      "demande_total":demande_total})

    if lines :

        reseau_bats_multilinestring = shp.MultiLineString(lines)
        reseau_bats_linestring = gpd.GeoDataFrame(geometry=gpd.GeoSeries(reseau_bats_multilinestring), crs=crs)
        reseau_bats_linestring['id_zone'] = id_zone

        reseau_bats_gdf = gpd.GeoDataFrame(lines)
        reseau_bats_gdf.set_crs(crs, inplace=True)
        
        return reseau_bats_linestring, reseau_bats_gdf
    
    else :
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()