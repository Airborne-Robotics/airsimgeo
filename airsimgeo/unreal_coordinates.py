import math
import numpy as np
from pyproj import Proj
from haversine import haversine, inverse_haversine


def get_bearing(lat1, long1, lat2, long2):
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    brng = np.arctan2(x,y)
    brng = np.degrees(brng)

    return brng

def lonlatToProj(lon, lat, z, inverse=False):
        proj_coords = proj(lon, lat, inverse=inverse)
        return proj_coords + (z,)

def projToAirSim(x, y, z):
    x_airsim = x - origin_proj[0]
    y_airsim = y - origin_proj[1]
    z_airsim = -z + origin_proj[2]
    return (x_airsim, -y_airsim, z_airsim)

def lonlatToAirSim(lon, lat, z):
    return projToAirSim(*lonlatToProj(lon, lat, z))



if __name__ == "__main__":
    SRID = "EPSG:27700"
    ORIGIN = (50.8292029862927, -0.23565952723679637, 1005)
    DEST = (50.82874470527534, -0.2540887625824003, 1105)
    
    heading = get_bearing(*ORIGIN[0:2], *DEST[0:2])
    heading = heading + 92.67

    if heading > 360:
        heading = heading - 360

    distance = haversine(ORIGIN[0:2], DEST[0:2])

    corr_coords = inverse_haversine(ORIGIN[0:2], distance = distance, direction = math.radians(heading))
    corr_coords = (*corr_coords, DEST[2])
    print("=" * 75)
    print(f"Corrected coordinates: {corr_coords}")
    print("=" * 75)

    proj = Proj(init= SRID)
    origin_proj = proj(*ORIGIN[0:2]) + (ORIGIN[2],)

    unreal_coords = lonlatToAirSim(*corr_coords)
    
    print()
    print(f"Unreal Engine Coordinates: {unreal_coords}")