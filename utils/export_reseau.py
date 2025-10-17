### Export le reseau en shapefile et en png

import matplotlib.pyplot as plt

def export_reseau(bats, reseau) :
    f, ax = plt.subplots()
    bats.plot(ax=ax, color="green")
    for route in reseau:
        route.to_crs(bats.crs).plot(ax=ax, color="purple")

    f.savefig("result.png")