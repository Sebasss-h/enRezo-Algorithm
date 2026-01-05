### Calculate perfromance (legnth, density) of the given heat network

def calcul_perf(reseau, bats) :

    if len(reseau.index) == 0 :
        return reseau
    
    reseau = calcul_length(reseau)
    reseau = calcul_density(reseau, bats)
    return reseau

def calcul_length(reseau) :
    reseau['length'] = reseau.length
    return reseau

def calcul_density(reseau, bats) :
    length = reseau.length
    besoin_chaleur = bats.besoin_chaud_2025.sum()
    reseau['besoin_chaleur'] = besoin_chaleur
    if length == 0 :
        reseau['densite'] = 0
    else :
        reseau['densite'] = besoin_chaleur / length
    return reseau