from dataclasses import dataclass
from datetime import datetime
from numpy import arange, array, dtype, empty, float64, fromiter, ndenumerate, vectorize, meshgrid, zeros

import swisseph as swe
from ketu import bodies, aspects, utf_8, utc_to_julian, julian_to_utc, calc_orb


def vectorized_calc(jdate, swe_ids):

    results = empty((len(swe_ids), 4))
    for idx, id in ndenumerate(swe_ids):
        results[idx] = swe.calc_ut(jdate, id)[0][:4]

    return results

PROPS_DTYPE = dtype([
    ("swe_id", "i4"), 
    ("lon", "f8"),
    ("lat", "f8"),
    ("vlon", "f8"), 
    ("vlat", "f8")  
])

class Singleton:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@dataclass
class ArrayWrapper:
    _data = array

    @property
    def data(self):
        # Code to return the internal array data
        return self._data

    def get(self, field):
        # Code to return a specific field from the internal array data
        return self.data[field]

    def dtype(self):
        return self.data.dtype

@dataclass
class BodiesWrapper(Singleton, ArrayWrapper):


    data = bodies
    
    def name(self):
        return utf_8(self.data['name'])
    
    @classmethod
    def swe_id(self):
        return self.data['swe_id']
    
    def orb(self):
        return self.data['orb']

    def speed(self):
        return self.data['speed']


@dataclass    
class AspectsWrapper(Singleton, ArrayWrapper):

    data = aspects

    def name(self):
        return utf_8(self.data['name'])

    def angle(self):
        return self.data['angle']

    def coef(self):
        return self.data['coef']


@dataclass
class BodiesProperties:
    

    jdate: float
    properties: array

    def build_properties(self):
        swe_ids = BodiesWrapper.swe_id()
        props = vectorized_calc(self.jdate, swe_ids)
        ids, lons, lats, vlons, vlats = swe_ids, props[:,0], props[:,1], props[:,2], props[:,3]
        self.properties = array(list(zip(ids, lons, lats, vlons, vlats)), dtype=PROPS_DTYPE)

    def __post_init__(self):
        self.build_properties()



if __name__ == '__main__':
    bodies_wrapper = BodiesWrapper()
    print(bodies_wrapper.name())
    print(bodies_wrapper.swe_id())
    print(bodies_wrapper.orb())
    print(bodies_wrapper.speed())

    aspects_wrapper = AspectsWrapper()
    print(aspects_wrapper.name())
    print(aspects_wrapper.angle())
    print(aspects_wrapper.coef())

    utc = datetime.now()
    print(utc)
    julian_date = utc_to_julian(utc)
    print(julian_date)
    bprops = BodiesProperties(jdate=julian_date , properties=None)
    print(bprops.properties)
    print(julian_to_utc(bprops.jdate))

    # # Get all body index pairs
    # body_pairs = array(meshgrid(arange(len(bodies)), arange(len(bodies)))).T.reshape(-1,2)

    # print(body_pairs)

    # for p in body_pairs:
    #     print(bodies[p[0]], bodies[p[1]])

    # # Calculate orbs for each pair and aspect 
    # orbs = array([calc_orb(p[0], p[1], a) 
    #              for p in body_pairs 
    #              for a in range(len(aspects))])

    # # Reshape into 3D array
    # orb_table = orbs.reshape(len(bodies), len(bodies), len(aspects))

    # print(orb_table)

    # # Get swe_ids and aspect angles
    # swe_ids = bodies['swe_id']
    # angles = aspects['angle']

    # # Create empty labeled 3D array
    # orb_table = zeros((len(swe_ids), len(swe_ids), len(angles)), 
    #                     dtype=float, 
    #                 )

    # # Fill table values
    # for i, id1 in enumerate(swe_ids):
    #     for j, id2 in enumerate(swe_ids):
    #         for k, angle in enumerate(angles):
    #             orb_table[i,j,k] = calc_orb(id1, id2, angle)
        
    # # Access labels  
    # print(orb_table['body1']) # swe_id of body 1
    # print(orb_table['body2']) # swe_id of body 2
    # print(orb_table['angle']) # aspect angle