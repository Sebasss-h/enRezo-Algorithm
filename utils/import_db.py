### Importe les bases de données

import geopandas as gpd


def import_db() :
    bats = import_bats()
    routes = import_routes()
    return bats, routes

def import_bats() :
    bats = gpd.read_file("data/donnee_source/donnee_source/d44_batiment_zone.gpkg")
    bats = bats[["id_zone", "id_source", "besoin_chaud_2025", "geometry"]]
    bats = bats[bats.id_zone != '44123c25000032']
    return bats

def import_routes() :
    routes = gpd.read_file("data/donnee_source/donnee_source/troncon_de_route.gpkg")
    routes = routes[["geometry"]]
    return routes