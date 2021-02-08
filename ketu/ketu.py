"""Ketu is a python library to generate time series and calendars based on
planetary aspects"""

from datetime import datetime
from functools import lru_cache
from itertools import combinations as combs
from zoneinfo import ZoneInfo

import numpy as np
import swisseph as swe

# Structured array of astronomical bodies: Sun, Moon, Mercury, Venus, Mars,
# Jupiter, Saturn, Uranus, Neptune, Pluto and mean Node aka Rahu,
# their id's and their orb of influence.
# Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050)
bodies = np.array([('Sun', 0, 12), ('Moon', 1, 12), ('Mercury', 2, 8),
                   ('Venus', 3, 8), ('Mars', 4, 10), ('Jupiter', 5, 10),
                   ('Saturn', 6, 10), ('Uranus', 7, 6), ('Neptune', 8, 6),
                   ('Pluto', 9, 4), ('Rahu', 10, 0)],
                  dtype=[('name', 'S12'), ('id', 'i4'), ('orb', 'f4')])

# Structured array of major aspects (harmonics 2 and 3) and their coefficient
# for calculation of the orb
aspects = np.array([('Conjunction', 0, 1), ('Sextile', 60, 1/3),
                    ('Square', 90, 1/2), ('Trine', 120, 2/3),
                    ('Opposition', 180, 1)],
                   dtype=[('name', 'S12'), ('value', 'f4'), ('coef', 'f4')])

# List of signs for body position
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def dd_to_dms(deg):
    """Return degrees, minutes, seconds from degrees decimal"""
    mins, secs = divmod(deg * 3600, 60)
    degs, mins = divmod(mins, 60)
    return np.array((degs, mins, secs), dtype='i4')


def distance(pos1, pos2):
    """Return the angular distance from two bodies positions"""
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


def get_orb(body1, body2, asp):
    """Calculate the orb for two bodies and aspect"""
    orbs, coef = bodies['orb'], aspects['coef']
    return (orbs[body1] + orbs[body2])/2 * coef[asp]


# --------- interface functions with pyswisseph ---------

def local_to_utc(dtime):
    """Convert local time to  UTC time"""
    return dtime - dtime.utcoffset()


def utc_to_julian(dtime):
    """Convert UTC time to Julian date"""
    if dtime.tzinfo is not None:
        utc = local_to_utc(dtime)
    else:
        utc = dtime
    year, month, day = utc.year, utc.month, utc.day
    hour, minute, second = utc.hour, utc.minute, utc.second
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def body_name(body):
    """Return the body name"""
    if swe.get_planet_name(body) == 'mean Node':
        return 'Rahu'
    return swe.get_planet_name(body)


@lru_cache()
def body_properties(jdate, body):
    """
    Return the body properties (longitude, latitude, distance to Earth in AU,
    longitude speed, latitude speed, distance speed) as a Numpy array
    """
    return np.array(swe.calc_ut(jdate, body)[0])

# --------------------------------------------------------


def body_id(b_name):
    """Return the body id"""
    return bodies['id'][np.where(bodies['name'] == b_name.encode())]


def body_long(jdate, body):
    """Return the body longitude"""
    return body_properties(jdate, body)[0]


def body_lat(jdate, body):
    """Return the body latitude"""
    return body_properties(jdate, body)[1]


def body_distance(jdate, body):
    """Return distance of the body to Earth in AU"""
    return body_properties(jdate, body)[2]


def body_vlong(jdate, body):
    """Return the body longitude speed"""
    return body_properties(jdate, body)[3]


def body_vlat(jdate, body):
    """Return the body latitude speed"""
    return body_properties(jdate, body)[4]


def body_vdistance(jdate, body):
    """Return the distance speed of the body"""
    return body_properties(jdate, body)[5]


def is_retrograde(jdate, body):
    """Return True if a body is retrograde"""
    return body_vlong(jdate, body) < 0


def is_ascending(jdate, body):
    """Return True if a body latitude is rising"""
    return body_vlat(jdate, body) > 0


def body_sign(long):
    """Return the body position in sign, degrees, minutes and seconds"""
    dms = dd_to_dms(long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return np.array((sign, degs, mins, secs))


def positions(jdate, l_bodies=bodies):
    """Return an array of bodies longitude"""
    bodies_id = l_bodies['id']
    return np.array([body_long(jdate, body) for body in bodies_id])


def get_aspect(jdate, body1, body2):
    """
    Return the aspect and orb between two bodies for a certain date
    Return None if there's no aspect
    """
    if body1 > body2:
        body1, body2 = body2, body1
    dist = distance(body_long(jdate, body1),
                    body_long(jdate, body2))
    for i_asp, aspect in enumerate(aspects['value']):
        orb = get_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif aspect - orb <= dist <= aspect + orb:
            return body1, body2, i_asp, aspect - dist
    return None


def get_aspects(jdate, l_bodies=bodies):
    """
    Return a structured array of aspects and orb
    Return None if there's no aspect
    """
    bodies_id = l_bodies['id']
    return np.array([get_aspect(jdate, *comb) for comb in combs(bodies_id, 2)
                     if get_aspect(jdate, *comb) is not None],
                    dtype=[('body1', 'i4'), ('body2', 'i4'),
                           ('i_asp', 'i4'), ('orb', 'f4')])


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print('\n')
    print('------------- Bodies Positions -------------')
    for index, pos in np.ndenumerate(positions(jdate)):
        sign, degs, mins, secs = body_sign(pos)
        retro = ', R' if is_retrograde(jdate, *index) else ''
        print(f"{body_name(*index):10}: "
              f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print('\n')
    print('------------- Bodies Aspects -------------')
    for aspect in get_aspects(jdate):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
        print(f"{body_name(body1):7} - {body_name(body2):8}: "
              f"{aspects['name'][i_asp].decode():12} "
              f"{degs:>2}º{mins:>2}'{secs:>2}\"")


def main():
    """Entry point of the programm"""
    year, month, day = map(int, input(
        "Give a date with iso format, ex: 2020-12-21\n").split("-"))
    hour, minute = map(int, input(
        "Give a time (hour, minute), with iso format, ex: 19:20\n").split(":"))
    tzinfo = input("Give the Time Zone, ex: 'Europe/Paris' for France\n")
    zoneinfo = ZoneInfo(tzinfo)
    dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
    jday = utc_to_julian(dtime)
    print_positions(jday)
    print_aspects(jday)


if __name__ == '__main__':
    main()
