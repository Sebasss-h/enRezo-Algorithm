### Trace le réseau de chaleur à partir du resultat du tsp

def tracer_reseau(reseau, path_dict, routes) :
    reseau_total = creer_reseau_total(reseau, path_dict)
    reseau_linestring = creer_reseau_linestring(reseau_total, routes)
    return reseau_linestring

def creer_reseau_total(reseau, path_dict) :
    reseau_total = []

    for i in range(len(reseau)-1) :
        source = reseau[i]
        target = reseau[i+1]

        lines = path_dict[(source, target)]
        reseau_total += lines
    
    return reseau_total

def creer_reseau_linestring(reseau_total, routes) :
    reseau_linestring = []

    for i in range(len(reseau_total)-1) :
        start = reseau_total[i]
        end = reseau_total[i+1]

        route = routes[(routes["start"] == start) & (routes["end"] == end)]
        if not route.empty :
            reseau_linestring.append(route)
    
    return reseau_linestring