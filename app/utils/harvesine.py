import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # rayon de la Terre en km
    # conversion en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # différences
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    # formule de Haversine
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c
