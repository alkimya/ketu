"""Ketu is a python library to generate time series and calendars based on
planetary aspects"""

from datetime import datetime
from functools import lru_cache
from itertools import (
    combinations as combs,
    combinations_with_replacement as rcombs,
)
from zoneinfo import ZoneInfo

from numpy import array, fromiter, ndenumerate, where

import swisseph as swe


# Structured array of astronomical bodies: Sun, Moon, Mercury, Venus, Mars,
# Jupiter, Saturn, Uranus, Neptune, Pluto, mean Node aka Rahu, mean Apogee aka
# Lilith, their Swiss Ephemeris id's, their orb of influence
# (Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050))
# and their average speed in degrees per day
bodies = array(
    [
        ('Sun', 0, 12, 0.986),
        ('Moon', 1, 12, 13.176),
        ('Mercury', 2, 8, 1.383),
        ('Venus', 3, 8, 1.2),
        ('Mars', 4, 10, 0.524),
        ('Jupiter', 5, 10, 0.083),
        ('Saturn', 6, 10, 0.034),
        ('Uranus', 7, 6, 0.012),
        ('Neptune', 8, 6, 0.007),
        ('Pluto', 9, 4, 0.004),
        ('Rahu', 10, 0, -0.013),
        ('Lilith', 12, 0, 0.113),
    ],
    dtype=[('name', 'S12'), ('swe_id', 'i4'), ('orb', 'f8'), ('avg_s', 'f8')],
    ndmin=1,
)

# Structured array of major aspects (harmonics 2 and 3): Conjunction, Sextile,
# Square, Trine and Opposition, their value and their coefficient for
# the calculation of the orb
maspects = array(
    [
        ('Conjunction', 0, 1),
        ('Sextile', 60, 1 / 3),
        ('Square', 90, 1 / 2),
        ('Trine', 120, 2 / 3),
        ('Opposition', 180, 1),
    ],
    dtype=[('name', 'S12'), ('angle', 'f8'), ('coef', 'f8')],
)

# List of signs for body position
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def body_name(swe_id):
    """Return the body name"""
    match swe.get_planet_name(swe_id):
        case 'mean Node':
            return 'Rahu'
        case 'mean Apogee':
            return 'Lilith'
        case _:
            return swe.get_planet_name(swe_id)


def body_index(swe_id):
    """Return the index of the body in bodies with a swe_id"""
    return where(bodies['swe_id'] == swe_id)[0][0]


def body_orb(swe_id):
    """Return the body orb of influence of b_id"""
    return bodies[body_index(swe_id)]['orb']


def body_sign(long):
    """Return the body position in sign, degrees, minutes and seconds from longitude"""
    dms = dd_to_dms(long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return array((sign, degs, mins, secs))


def maspect_name(asp):
    """Return the aspect name"""
    return maspects[asp]['name']


def maspect_angle(asp):
    """Return the aspect angle"""
    return maspects[asp]['name']


def maspect_coef(asp):
    """Return the coefficient of the aspect for the calcul of orb"""
    return maspects[asp]['coef']


def maspect_index(angle):
    """Return the index of the aspect with a certain angle"""
    return where(maspects['angle'] == angle)[0][0]


def dd_to_dms(dd):
    """Return degrees, minutes, seconds from degrees decimal"""
    mins, secs = map(int, divmod(dd * 3600, 60))
    degs, mins = map(int, divmod(mins, 60))
    return degs, mins, secs


def dms_to_dd(dms):
    """Return degrees decimal from degrees, minutes, seconds"""
    return dms[0] + dms[1] / 60 + dms[2] / 3600


def norm(angle):
    """Normalize the angular distance of two bodies between 0 - 360"""
    return angle % 360


def znorm(angle):
    """Return the normalized angle of two bodies between -180 and 180"""
    angle = norm(angle)
    return angle if angle < 180 else angle - 360


def distance(angle):
    """Return the angular distance from two bodies positions < 180"""
    return abs(znorm(angle))


def calc_orb(body1, body2, asp):
    """Calculate the orb for two bodies and aspect"""
    return (body_orb(body1) + body_orb(body2)) / 2 * maspect_coef(asp)


# --------- interface functions with pyswisseph ---------


def local_to_utc(dtime, zoneinfo=ZoneInfo('UTC')):
    """Convert local time to  UTC time"""
    year, month, day = dtime.year, dtime.month, dtime.day
    hour, minute = dtime.hour, dtime.minute
    return datetime(year, month, day, hour, minute, tzinfo=zoneinfo)


def utc_to_julian(dtime):
    """Convert UTC time to Julian date"""
    utc = local_to_utc(dtime)
    year, month, day = utc.year, utc.month, utc.day
    hour, minute, second = utc.hour, utc.minute, utc.second
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def julian_to_utc(julian, zoneinfo):
    """Convert Julian date to UTC time"""
    year, month, day, hour, minute, second = map(int, swe.jdut1_to_utc(julian+13, 0))
    return datetime(year, month, day, hour, minute, second, tzinfo=ZoneInfo('UTC')).astimezone(zoneinfo)


@lru_cache()
def body_properties(jdate, swe_id):
    """
    Return the body properties (longitude, latitude, distance to Earth in AU,
    longitude speed, latitude speed, distance speed) as a Numpy array

    Return : array(['swe_id', 'lon', 'lat', 'vlon', 'vlat'])
    """
    return array(
        (
            swe_id,
            swe.calc_ut(jdate, swe_id)[0][0],
            swe.calc_ut(jdate, swe_id)[0][1],
            swe.calc_ut(jdate, swe_id)[0][3],
            swe.calc_ut(jdate, swe_id)[0][4],
        ),
        dtype=[('swe_id', 'i4'), ('lon', 'f8'), ('lat', 'f8'), ('vlon', 'f8'), ('vlat', 'f8')],
        ndmin=1,)


# --------------------------------------------------------


def get_swe_id(props):
    """Return the body id"""
    return props['swe_id']


def lon(props):
    """Return the body longitude"""
    return props['lon']


def lat(props):
    """Return the body latitude"""
    return props['lat']


def vlon(props):
    """Return the body longitude speed"""
    return props['vlon']


def vlat(props):
    """Return the body latitude speed"""
    return props['vlat']


def is_retrograd(props):
    """Return True if a body is retrograd"""
    return vlon(props) < 0


def is_ascending(props):
    """Return True if a body latitude is rising"""
    return vlat(props) > 0


def is_waxing(angle):
    """Return True if a body is waxing"""
    angle = znorm(angle)
    return angle > 0


def positions(jdate, l_bodies=bodies):
    """Return an array of bodies longitude"""
    bodies_id = l_bodies['swe_id']
    return array([lon(body_properties(jdate, body)) for body in bodies_id])


def get_aspect(jdate, body1, body2):
    """
    Return the aspect and orb between two bodies for a certain date
    Return the angle between the two bodies if there's no aspect
    """
    if bodies[body_index(body1)]['avg_s'] > bodies[body_index(body2)]['avg_s']:
        body1, body2 = body2, body1
    props1, props2 = (body_properties(jdate, body) for body in [body1, body2])
    lon1, lon2 = lon(props1), lon(props2)
    angle = lon2 - lon1
    angle = distance(angle)
    for i_asp, aspect in enumerate(maspects['angle']):
        orbite = calc_orb(body1, body2, i_asp)
        if aspect - orbite <= angle <= aspect + orbite:
            return array(
                (jdate, props1, props2, i_asp),
                dtype=[('jdate', 'f8'), ('props1', 'O'), ('props2', 'O'), ('i_asp', 'i4')],
                ndmin=1,)
    return None


def is_applicative(aspect):
    """ "dev mode"""
    lon1, lon2, i_asp = lon(aspect['props1'][0]), lon(aspect['props2'][0]), aspect['i_asp']
    wax = is_waxing(lon2 - lon1)
    asp = maspects['angle'][i_asp]
    is_r = is_retrograd(aspect['props2'][0])
    if i_asp == 0 and ((not wax and not is_r) or (wax and is_r)):
        return True
    if i_asp == 4 and (((wax and not is_r) or (not wax and is_r))):
        return True
    if distance(lon2 - lon1) - asp > 0 and not is_r:
        return True
    if distance(lon2 - lon1) - asp < 0 and is_r:
        return True
    return False


def get_aspect_orb(aspect):
    """dev mode"""
    lon1, lon2, i_asp = lon(aspect['props1'][0]), lon(
        aspect['props2'][0]), aspect['i_asp']
    orb = distance(lon2 - lon1) - maspects['angle'][i_asp]
    return abs(orb)


def get_aspects(jdate, l_bodies=bodies):
    """
    Return a structured array of aspects and orb
    """
    bodies_id = l_bodies['swe_id']
    aspects = fromiter([get_aspect(jdate, *comb) for comb in combs(bodies_id, 2) if get_aspect(jdate, *comb)],
                       dtype=[('jdate', 'f8'), ('props1', 'O'), ('props2', 'O'), ('i_asp', 'i4')])
    return aspects


def find_easpect(aspect):
    """dev mode"""
    jdate = aspect['jdate']
    # i_asp = aspect["i_asp"]
    props1 = aspect['props1']
    orb = get_aspect_orb(aspect)[0]
    app = is_applicative(aspect)
    props1, props2 = aspect['props1'], aspect['props2']
    body1, body2 = get_swe_id(props1[0]), get_swe_id(props2[0])
    vlon1, vlon2 = vlon(props1[0]), vlon(props2[0])
    if orb > dms_to_dd([0, 0, 1]):
        delta = orb / (vlon2 - vlon1)
        jdate = jdate + delta if app else jdate - delta
        return find_easpect(get_aspect(*jdate, *body1, *body2))
    return jdate[0]


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print("\n")
    print("-------------- Bodies Positions --------------")
    positions(jdate)
    for index, pos in ndenumerate(positions(jdate)):
        sign, degs, mins, secs = body_sign(pos)
        props = body_properties(jdate, bodies[index[0]]['swe_id'])
        retro = ' Retrograd' if is_retrograd(props) else ''
        print(
            f"{body_name(bodies[index[0]]['swe_id']):10}: "
            f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}"
        )


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print("\n")
    print("------------- Bodies Aspects -------------")
    for aspect in get_aspects(jdate):
        props1, props2, i_asp, orb, app = (
            aspect['props1'],
            aspect['props2'],
            aspect['i_asp'],
            get_aspect_orb(aspect),
            is_applicative(aspect),
        )
        degs, mins, secs = dd_to_dms(orb)
        app = 'Applicative' if app else 'Separative'
        b_name, b_id = body_name, get_swe_id
        name1, name2 = b_name(b_id(props1[0])), b_name(b_id(props2[0]))
        print(
            f"{name2:7} - {name1:8}: "
            f"{maspects['name'][i_asp].decode():12} "
            f"{degs:>3}º{mins:>3}'{secs:>3}\" "
            f"{app:>12} "
        )


def main():
    """Entry point of the programm"""
    # year, month, day = map(
    #     int, input("Give a date with iso format, ex: 2020-12-21\n")
    # .split("-")
    # )
    # hour, minute = map(
    #     int,
    #     input(
    #         "Give a time (hour, minute), with iso format, ex: 19:20\n"
    #     ).split(":"),
    # )
    # tzinfo = (
    #    input("Give the Time Zone, ex: 'Europe/Paris' for France\n")
    #    or "Europe/Paris"
    # )

    zoneinfo = ZoneInfo('Europe/Paris')
    year, month, day, hour, minute = 1975, 6, 6, 15, 10
    dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
    jdate = utc_to_julian(dtime)
    print(jdate)
    print_positions(jdate)
    print_aspects(jdate)


if __name__ == "__main__":
    # print(t_aspects)
    main()
