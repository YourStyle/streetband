from math import radians, cos, sin, asin, sqrt, ceil

from aiogram import types

from streetband.app.show_on_map import show
from streetband.database import database as db, cache

R = 6378.1


def calc_distance(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return ceil(km)


def choose_shortest(location: types.Location):
    distances = []
    musicians = cache.jget("musicians")

    if musicians is None:
        db.get_musicians()
        musicians = cache.jget("musicians")

    for musician in musicians:
        artist_id = musician["musician_id"]
        artist_name = musician["musician_name"]
        artist_location = musician["current_location"]
        if artist_location is not None:
            distances.append((artist_name,
                              calc_distance(location.latitude, location.longitude,
                                            artist_location["lat"], artist_location["lon"]),
                              artist_id
                              ))
        else:
            # если будет мало артистов, иначе будет пустое сообщение
            arctic = {"lat": -79.474655, "lon": 29.507431}
            distances.append((artist_name,
                              calc_distance(location.latitude, location.longitude,
                                            arctic["lat"], arctic["lon"]),
                              artist_id
                              ))
    # show(**artist_location)
    return sorted(distances, key=lambda x: x[1])[:5]
