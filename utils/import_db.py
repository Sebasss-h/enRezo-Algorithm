### Importe les bases de données

import pandas as pd
import geopandas as gpd

def import_db(path) :
    bats = import_bats(path)
    routes = import_routes(path)
    diametre_table = import_diametre_table()
    return bats, routes, routes.crs, diametre_table

def import_bats(path) :
    bats = gpd.read_file(f"{path}/batiment_zone.gpkg")
    bats = bats[["id_zone", "id_source", "besoin_chaud_2025", "geometry"]]
    return bats

def import_routes(path) :
    routes = gpd.read_file(f"{path}/route.gpkg")
    routes = routes[["geometry"]]
    return routes

def import_diametre_table() :
    diametre_table = pd.read_excel('ressources/diametres.xlsx', sheet_name='Final')
    return diametre_table