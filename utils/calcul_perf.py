### Calcul les performance (length, density) du reseau

def calcul_perf(reseau, bats) :

    if reseau.empty :
        return reseau
    
    reseau = calcul_length(reseau)
    reseau = calcul_density(reseau, bats)
    return reseau

def calcul_length(reseau) :
    reseau['length'] = reseau.length
    return reseau

def calcul_density(reseau, bats) :
    length = reseau.length.values[0]
    besoin_chaleur = bats.besoin_chaud_2025.sum()
    reseau['besoin_chaleur'] = besoin_chaleur
    if length == 0 :
        reseau['densite'] = 0
    else :
        reseau['densite'] = besoin_chaleur / length
    return reseau