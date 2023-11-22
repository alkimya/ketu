"""Module to test the app with some parameters"""

from datetime import datetime
from zoneinfo import ZoneInfo

from numpy import fromiter
import swisseph as swe

from ketu import (
    utc_to_julian, utc_to_julian2, bodies, bodies_name, aspects, get_bodies, properties, print_aspects, print_positions, dms_to_dd,
    get_aspect_orb, julian_to_local, find_easpect, find_easpect2, get_aspects, get_chart, get_angle, get_angles,
    gen_aspects, get_aspect
)
from timea import timea

zoneinfo = ZoneInfo('Europe/Paris')
gday = datetime.now()
jday = utc_to_julian(gday)
jday2 = utc_to_julian2(gday)
lemans = 48.0042, 0.1970, 100
swe.set_topo(*lemans)


@timea
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


def main():
    """Main function"""
    print_array(bodies)
    print_array(maspects)
    chart = get_chart(jday)
    print_array(chart.swe_id)
    print_array(get_angles(chart))
    aspects = get_aspects(chart)
    print_array(aspects)
    print_positions(jday)
    print_aspects(jday)
    print("\n")
    print(f"Initial datetime : \n{gday:}")
    print(f"Datetime for next aspect Sun-Moon recursive: \n{julian_to_utc(find_easpect(get_aspect(chart, 0, 1)), zoneinfo)}")
#   print(f"Datetime for moon rise : \n{julian_to_utc(swe.rise_trans(jday, 1, 1, *lemans)[1][0], zoneinfo)}")
    print(f"Datetime for next aspect Sun-Moon iterative: \n{julian_to_utc(find_easpect2(get_aspect(chart, 0, 1)), zoneinfo)}")
#  print(f"Datetime for moon rise : \n{julian_to_utc(swe.rise_trans(jday, 1, 1, *lemans)[1][0], zoneinfo)}")


if __name__ == "__main__":
    #main()
    print(bodies_name(get_bodies([1, 10, 12])))
    print(jday)
    print(jday2)
