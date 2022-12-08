from haversine import haversine, Unit, inverse_haversine
import math


def convertCoords(lat1,lon1,lat2,lon2): #lat1 & lon1 are original destination
    heading = calcBearing(lat1,lon1,lat2,lon2)
    dist = haversine((lat1, lon1), (lat2,lon2), unit=Unit.METERS)
    heading = heading + 90
    if heading > 360:
            heading = heading - 360
    coords = inverse_haversine((lat1,lon1), dist, -heading, unit=Unit.METERS)
    return(coords[0],coords[1])

def calcBearing(lat,lon,lat2,lon2):

        teta1 = math.radians(lat)
        teta2 = math.radians(lat2)
        delta2 = math.radians(lon2-lon)

        y = math.sin(delta2) * math.cos(teta2)
        x = math.cos(teta1)*math.sin(teta2) - math.sin(teta1)*math.cos(teta2)*math.cos(delta2)
        brng = math.atan2(y,x)
        brng = math.degrees(brng)
        return brng