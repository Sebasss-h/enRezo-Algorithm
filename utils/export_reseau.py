### Export le reseau en shapefile et en png

import pandas as pd
import geopandas as gpd

def export_reseau(reseaux, crs):

    reseaux_gdf = pd.concat(reseaux, ignore_index=True)

    reseaux_gdf = reseaux_gdf.set_crs(crs)

    reseaux_gdf.to_file('reseaux.gpkg', driver='GPKG', layer='reseaux')