"""This modules is in pre-version"""

from itertools import combinations

import numpy as np
import swisseph as swe

body_orbs = np.array([12, 12, 8, 8, 8, 10, 10, 6, 6, 4])

aspects = np.array([0, 30, 60, 90, 120, 150, 180])

aspects_coeff = np.array([1, 1 / 6, 1 / 3, 1 / 2, 2 / 3, 5 / 6, 1])

aspects_name = ['Conjunction', 'Semisextile', 'Sextile',
                'Square', 'Trine', 'Quincunx', 'Opposition']

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

swe.set_ephe_path(path='/home/loc/workspace/ketu/ephe')


def local_to_utc(year, month, day, hour, minute, second, offset):
    return swe.utc_time_zone(year, month, day, hour, minute, second, offset)


def utc_to_julian(year, month, day, hour, minute, second):
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def dd_to_dms(dd):
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return tuple(map(int, (degrees, minutes, seconds)))


def distance(pos1, pos2):
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


def get_orb(body1, body2, aspect):
    return ((body_orbs[body1] + body_orbs[body2]) / 2) * aspects_coeff[aspect]


# Data Structure for the list of orbs, by couple of bodies and aspect
# We first use a dictionnary, with a frozenset of couple of bodies as key,
# and a numpy array of the orbs, indexed by aspect as value
# We build the dictionnary by comprehension
aspect_dict = {
    frozenset(comb): np.array([get_orb(*comb, n) for n in range(len(aspects))])
    for comb in combinations([i for i in range(len(body_orbs))], 2)}


def body_name(body):
    return swe.get_planet_name(body)


def body_position(jdate, body):
    return swe.calc_ut(jdate, body)[0][0]


def body_speed(jdate, body):
    return swe.calc_ut(jdate, body)[0][3]


def is_retrograde(jdate, body):
    return body_speed(jdate, body) < 0


def body_sign(jdate, body):
    position = body_position(jdate, body)
    dms = dd_to_dms(position)
    sign, degrees = divmod(dms[0], 30)
    return sign, degrees, dms[1], dms[2]


def get_aspect(jdate, body1, body2):
    dist = distance(body_position(jdate, body1),
                    body_position(jdate, body2))
    dist = round(dist, 2)
    for i, n in enumerate(aspect_dict[frozenset([body1, body2])]):
        orb = round(get_orb(body1, body2, i), 2)
        if i == 0 and dist <= n:
            return aspects[i], dist
        elif aspects[i] - orb <= dist <= aspects[i] + orb:
            return aspects[i], abs(aspects[i] - dist)
    return None, dist


def print_positions(jdate):
    print('\n')
    print('-------- Bodies Positions --------')
    for i in range(len(body_orbs)):
        sign, d, m, s = body_sign(jdate, i)
        retro = 'R' if is_retrograde(jdate, i) else ''
        print(body_name(i) + ': ' + signs[sign] + ', ' + str(d) +
              'º' + str(m) + "'" + str(s) + '", ' + retro)


def print_aspects(jdate):
    print('\n')
    print('-------- Bodies Aspects ---------')
    for key in aspect_dict.keys():
        aspect = get_aspect(jdate, *key)
        if aspect[0] is not None and aspect[0] != 30 and aspect[0] != 150:
            body1, body2 = key
            d, m, s = dd_to_dms(aspect[1])
            print(body_name(body1) + '-' + body_name(body2) + ': ' +
                  aspects_name[np.where(aspects == aspect[0])[
                      0].item()] + ', orb = ' + str(d) +
                  'º' + str(m) + "'" + str(s) + '", ')


if __name__ == '__main__':
    year, month, day = map(int, input(
        'Give a date with iso format, ex: 2020-12-21\n').split('-'))
    hour, minute = map(int, input(
        'Give a time (hour, minute), with iso format, ex: 15:10\n').split(':'))
    tz = int(input('Give the offset with UTC, ex: 1 for France\n'))
    jday = utc_to_julian(*local_to_utc(year, month, day, hour, minute, 0, tz))
    print_positions(jday)
    print_aspects(jday)
