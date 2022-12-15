"""
Script to convert the real world coordinates to corresponding Unreal Engine coordinates
"""

import math
import warnings
import numpy as np
from typing import Tuple
from pyproj import Proj
from vincenty import vincenty
from haversine import inverse_haversine

warnings.filterwarnings("ignore", category = FutureWarning)

#----------------------------------------------------------
ORIGIN = (50.69294576306597, -0.2596393704456905, 10)
DESTINATION = (50.70133366,	-0.2047640619, 50)
PLAYER_START = (0.0, 0.0, 4972.0)
#----------------------------------------------------------



def get_bearing(lat1: float, long1: float, lat2: float, long2: float) -> float:
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
            math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.cos(math.radians(dLon))
    brng = np.arctan2(x,y)
    brng = np.degrees(brng)

    return brng


class RealToUnreal(object):
    def __init__(self, srid: str, origin: Tuple, **kwargs):
        super(RealToUnreal, self).__init__(**kwargs)

        self.srid = srid
        self.origin = origin
        self.proj = Proj(init = srid)
        self.origin_proj = self.proj(*self.origin[0:2]) + (self.origin[2],)

    def lonlatToProj(self, lon: float, lat: float, z: float, inverse: bool=False) -> Tuple:
        proj_coords = self.proj(lon, lat, inverse=inverse)
        return proj_coords + (z,)

    def projToAirSim(self, x: float, y: float, z: float) -> Tuple:
        x_airsim = x - self.origin_proj[0]
        y_airsim = y - self.origin_proj[1]
        z_airsim = -z + self.origin_proj[2]
        return (x_airsim, -y_airsim, z_airsim)

    def lonlatToAirSim(self, lon: float, lat: float, z: float) -> Tuple:
        return self.projToAirSim(*self.lonlatToProj(lon, lat, z))

    def getUnrealCoords(self, gps = None, proj = None) -> Tuple:
        coords = None

        if gps is not None:
            coords = self.lonlatToAirSim(*gps)
        elif proj is not None:
            coords = self.projToAirSim(*proj)

        if coords:
            return (coords[0]*100, coords[1]*100, coords[2])
        else:
            print('Please pass in GPS (lon,lat,z), or projected coordinates (x,y,z)!')
            return

        



if __name__ == "__main__":
    SRID = "EPSG:27700"

    heading = get_bearing(*ORIGIN[0:2], *DESTINATION[0:2])
    print("Heading: ", heading, "°")

    if heading > 360:
        heading = heading - 360

    # The map on Mission Planner is offset by a little more than 90 degrees
    # This is accounted for below. Value found through experimentation.
    heading = heading + 91.3

    # Checks if the vector lies between two given vectors, all having the same origin.
    angle_diff = (-1 * heading + 180 + 360) % 360 - 180
    
    # It was found through more experimentation that the scaling of the world
    # while importing from Blender to Unreal is a little off.
    # Moreover, both X and Y axes are scaled differently. 
    
    # To account for this, arcs similar to the "X" shape was created.
    # Different scaling is applied for the (left and right), and (top and bottom) of the arcs.
    if (angle_diff >= 45 and angle_diff <= 135) or (angle_diff <= -45 and angle_diff >= -135):
        heading = heading + 0.05
        distance_from_coords = vincenty(ORIGIN[0:2], DESTINATION[0:2]) * 0.9965
        print("Distance: ", distance_from_coords, "km")
    else:
        distance_from_coords = vincenty(ORIGIN[0:2], DESTINATION[0:2])
        print("Distance: ", distance_from_coords, "km")

    corrected_coords = inverse_haversine(ORIGIN[0:2], 
                                         distance = distance_from_coords,
                                         direction = math.radians(heading))

    print("=" * 80)
    print("Corrected real-world coordinates: ", corrected_coords)
    print("=" * 80)

    real2unreal = RealToUnreal(srid = SRID, origin = (ORIGIN[1], ORIGIN[0], ORIGIN[2]))
    
    unreal_coords = real2unreal.getUnrealCoords(gps = (corrected_coords[1], 
                                                       corrected_coords[0], 
                                                       DESTINATION[2]))

    print("\nPlayer Start location:    ", PLAYER_START)
    print("Offset from Player Start: ", unreal_coords, "\n")

    print("=" * 80)
    print("Unreal Engine Coordinates: ", (PLAYER_START[0]+unreal_coords[0], 
                                          PLAYER_START[1]+unreal_coords[1], 
                                          PLAYER_START[2]+unreal_coords[2]))
    print("=" * 80)