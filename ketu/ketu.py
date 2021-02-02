"""Ketu is a python library to generate time series and calendars based on
planetary aspects"""

from itertools import combinations_with_replacement as combs
from functools import lru_cache
import numpy as np
import swisseph as swe


# Orbs of influence by body: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
# Uranus, Neptune, Pluto and mean Node aka Rahu
# Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050)
body_orbs = np.array([12, 12, 8, 8, 8, 10, 10, 6, 6, 4, 0])

# List of major aspects (harmonics 2 and 3)
aspects = np.array([0, 60, 90, 120, 180])
# And their coefficient for calculation of the orb
aspects_coeff = np.array([1, 1/3, 1/2, 2/3, 1])
# Corresponding names of the aspects
aspects_name = ['Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition']

# List of signs for body position
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


# TODO: Refactor with datetime and timezone object
def local_to_utc(year, month, day, hour, minute, second, offset):
    """Return UTC time from local time"""
    return swe.utc_time_zone(year, month, day, hour, minute, second, offset)


# TODO: Refactor with datetime object
def utc_to_julian(year, month, day, hour, minute, second):
    """Return Julian date from UTC time"""
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def dd_to_dms(dd):
    """Return degrees, minutes, seconds from decimal longitude"""
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return tuple(map(int, (degrees, minutes, seconds)))


def distance(pos1, pos2):
    """Return the angular distance from two bodies positions"""
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


def get_orb(body1, body2, aspect):
    """Calculate the orb for two bodies and aspect"""
    return ((body_orbs[body1] + body_orbs[body2]) / 2) * aspects_coeff[aspect]


# Data Structure for the list of orbs, by couple of bodies and aspect
# We first use a dictionnary, with a frozenset of couple of bodies as key,
# and a numpy array of the orbs, indexed by aspect as value
# We build the dictionnary by comprehension and use it to filter the aspects
aspect_dict = {
    frozenset(comb): np.array([get_orb(*comb, n) for n in range(len(aspects))])
    for comb in combs(list(range(len(body_orbs))), 2)
}


# --------- interface functions with pyswisseph ---------

def body_name(body):
    """Return the body name"""
    if swe.get_planet_name(body) == 'mean Node':
        return 'Rahu'
    return swe.get_planet_name(body)


@lru_cache()
def body_properties(jdate, body):
    """Return the body properties as a tuple"""
    return swe.calc_ut(jdate, body)[0]


def body_longitude(jdate, body):
    """Return the body longitude"""
    return body_properties(jdate, body)[0]


def body_speed(jdate, body):
    """Return the body longitude speed"""
    return body_properties(jdate, body)[3]


# --------------------------------------------------------


def is_retrograde(jdate, body):
    """Return True if a body is retrograde"""
    return body_speed(jdate, body) < 0


def body_sign(jdate, body):
    """Return the body position in sign"""
    position = body_longitude(jdate, body)
    dms = dd_to_dms(position)
    sign, degrees = divmod(dms[0], 30)
    return sign, degrees, dms[1], dms[2]


def get_aspect(jdate, body1, body2):
    """
    Return the aspect and orb between two bodies for a certain date
    Return None and distance between the two bodies if there's no aspect
    """
    dist = distance(body_longitude(jdate, body1),
                    body_longitude(jdate, body2))
    dist = round(dist, 2)
    for i, n in enumerate(aspect_dict[frozenset([body1, body2])]):
        orb = round(get_orb(body1, body2, i), 2)
        if i == 0 and dist <= n:
            return aspects[i], dist
        elif aspects[i] - orb <= dist <= aspects[i] + orb:
            return aspects[i], abs(aspects[i] - dist)
    return None, dist


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print('\n')
    print('------------- Bodies Positions -------------')
    for i in range(len(body_orbs)):
        sign, d, m, s = body_sign(jdate, i)
        retro = ', R' if is_retrograde(jdate, i) else ''
        print(f"{body_name(i):10}: {signs[sign]:12}{d}º{m}'{s}\"{retro}")


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print('\n')
    print('------------- Bodies Aspects -------------')
    for key in aspect_dict.keys():
        if len(key) == 2:
            aspect = get_aspect(jdate, *key)
            if aspect[0] is not None:
                body1, body2 = key
                d, m, s = dd_to_dms(aspect[1])
                index = np.where(aspects == aspect[0])[0].item()
                print(f"{body_name(body1):7} - {body_name(body2):10}: "
                      f"{aspects_name[index]:12} {d}º{m}'{s}\"")


def main():
    """Entry point of the programm"""
    year, month, day = map(int, input(
        'Give a date with iso format, ex: 2020-12-21\n').split('-'))
    hour, minute = map(int, input(
        'Give a time (hour, minute), with iso format, ex: 15:10\n').split(':'))
    tz = float(input('Give the offset with UTC, ex: 1 for France\n'))
    jday = utc_to_julian(*local_to_utc(year, month, day, hour, minute, 0, tz))
    print_positions(jday)
    print_aspects(jday)


if __name__ == '__main__':
    main()
