### Export le reseau en shapefile et en png

from utils.diametre import get_diametre

import pandas as pd
import os

def export_reseau(reseaux, crs, diametre_table):

    if not os.path.exists("result"):
        os.makedirs("result")

    # Reseau Linestring : 1 géometrie par reseau avec densité, demande totale, longueur totale
    reseaux_linestring = [r[0] for r in reseaux]
    reseaux_linestring_gdf = pd.concat(reseaux_linestring, ignore_index=True)
    reseaux_linestring_gdf = reseaux_linestring_gdf.set_crs(crs)
    reseaux_linestring_gdf.to_file('result/reseaux.gpkg', driver='GPKG', layer='reseaux')

    # Reseau GDF : 1 géometrie par troncon de route pour avoir les différents diametre
    reseaux_gdf = [r[1] for r in reseaux]
    reseaux_gdf_gdf = pd.concat(reseaux_gdf, ignore_index=True)
    reseaux_gdf_gdf = get_diametre(reseaux_gdf_gdf, diametre_table)
    reseaux_gdf_gdf = reseaux_gdf_gdf.set_crs(crs)
    reseaux_gdf_gdf.to_file('result/troncon.gpkg', driver='GPKG', layer='troncon')