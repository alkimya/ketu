"""Module to test the app with some parameters"""

from datetime import datetime
from functools import wraps
from time import time
from zoneinfo import ZoneInfo

from numpy import ndarray
import swisseph as swe

from ketu import (
    utc_to_julian, bodies, maspects, body_properties, get_aspect, print_aspects, dms_to_dd,
    get_aspect_orb, julian_to_utc, find_easpect, get_aspects
)


zoneinfo = ZoneInfo('Europe/Paris')
gday = datetime(2022, 6, 14, 8, 0, 0, tzinfo=zoneinfo)
jday = utc_to_julian(gday)
lemans = 48.0042, 0.1970, 100
canar = 36.9263, -3.4277, 1014
swe.set_topo(*canar)


def timing(func):
    """Decorator to profile a function"""
    @wraps(func)
    def wrap(*args, **kw):
        start = time()
        result = func(*args, **kw)
        end = time()
        print(f"{func.__name__} took: {end-start}:2.4f sec\n")
        return result
    return wrap


@timing
def print_array(array):
    """Print the characteristics of an array"""
    print(f"array : {array}")
    print(f"type : {type(array)}")
    print(f"ndim : {array.ndim}")
    print(f"shape : {array.shape}")
    print(f"size : {array.size}")
    print(f"dtype : {array.dtype}")
    print(f"itemsize : {array.itemsize}")
    print(f"nbytes : {array.nbytes}\n")
    print(f"{array.strides}")


def main():
    """Main function"""
    props = body_properties
    print_array(bodies)
    print_array(maspects)
    print_array(props(jday, 12))
    print_array(get_aspect(jday, 0, 1))
    print(get_aspect(find_easpect(get_aspect(jday, 0, 1)), 0, 1))
    print_array(get_aspects(jday))
    print_aspects(jday)
    print(get_aspect_orb(get_aspect(jday, 0, 1)))
    print_aspects(find_easpect(get_aspect(jday, 0, 1)))
    print(f"Initial datetime : \n{gday:}")
    print(f"Datetime for full moon : \n{julian_to_utc(find_easpect(get_aspect(jday, 0, 1)), zoneinfo)}")
    print(f"Datetime for moon rise : \n{julian_to_utc(swe.rise_trans(jday, 1, 1, *canar)[1][0], zoneinfo)}")


if __name__ == "__main__":
    main()
