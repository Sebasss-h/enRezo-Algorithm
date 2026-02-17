### Importe les bases de données

import pandas as pd
import geopandas as gpd

def import_db() :
    bats = import_bats()
    routes = import_routes()
    diametre_table = import_diametre_table()
    return bats, routes, routes.crs, diametre_table

def import_bats() :
    bats = gpd.read_file("data/donnee_source/donnee_source/d44_batiment_zone.gpkg")
    bats = bats[["id_zone", "id_source", "besoin_chaud_2025", "geometry"]]
    #bats = bats[~bats["id_zone"].isin(['44123c25000032'])]
    #bats = bats[bats["id_zone"].isin(["44123c25000257"])]
    return bats

def import_routes() :
    routes = gpd.read_file("data/donnee_source/donnee_source/troncon_de_route.gpkg")
    routes = routes[["geometry"]]
    return routes

def import_diametre_table() :
    diametre_table = pd.read_excel('ressources/diametres.xlsx')
    return diametre_table