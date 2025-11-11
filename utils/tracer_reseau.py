### Trace le réseau de chaleur à partir du resultat du tsp

import pandas as pd

def tracer_reseau(reseau, routes, id_zone) :
    reseau_total = creer_reseau_total(reseau)
    reseau_linestring = creer_reseau_linestring(reseau_total, routes)
    reseau_linestring['id_zone'] = id_zone
    return reseau_linestring

def creer_reseau_total(reseau) :
    reseau_total = []

    for edge in reseau :
        lines = edge[2]['path']
        reseau_total += lines
    
    return reseau_total

def creer_reseau_linestring(reseau_total, routes) :
    reseau_linestring = []

    for i in range(len(reseau_total)-1) :
        p1 = reseau_total[i]
        p2 = reseau_total[i+1]

        route = routes[((routes["start"] == p1) & (routes["end"] == p2)) | ((routes["start"] == p2) & (routes["end"] == p1))]
        if not route.empty :
            reseau_linestring.append(route)
        
        reseau_linestring_gdf = pd.concat(reseau_linestring, ignore_index=True)
    
    return reseau_linestring_gdf