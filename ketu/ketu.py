"""Ketu is a python library to generate time series and calendars based on
planetary aspects"""

from datetime import datetime
from functools import lru_cache
from itertools import (
    combinations as combs,
    combinations_with_replacement as rcombs,
)
from zoneinfo import ZoneInfo

from numpy import argsort, dtype, fromiter, hstack, logical_and, ndenumerate, recarray, sort, unique, where
from numpy.core.records import array, fromrecords
from numpy.lib.recfunctions import append_fields
from numpy.ma import MaskedArray as ma


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
    return where(bodies.swe_id == swe_id)


def body_orb(swe_id):
    """Return the body orb of influence of b_id"""
    return bodies[body_index(swe_id)].orb


def body_sign(long):
    """Return the body position in sign, degrees, minutes and seconds from longitude"""
    dms = dd_to_dms(long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    datatype = dtype([('sign', 'i4'), ('degs', 'i4'), ('mins', 'i4'), ('secs', 'i4')])
    return array((sign, degs, mins, secs), dtype=datatype)


def maspect_index(aspect):
    """Return the index of the aspect with a certain aspect in maspect.value"""
    return where(maspects['angle'] == aspect)[0][0]


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
    angle = where(angle < 180, angle, angle - 360)
    return angle


def distance(angle):
    """Return the angular distance from two bodies positions < 180"""
    return abs(znorm(angle))


def calc_orb(body1, body2, asp):
    """Calculate the orb for two bodies and aspect"""
    return (body_orb(body1) + body_orb(body2)) / 2 * maspects.coef[asp]


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
def properties(jdate, swe_id):
    """
    Return the body properties (longitude, latitude, distance to Earth in AU,
    longitude speed, latitude speed, distance speed) as a Numpy array

    Return : array(['jdate', 'swe_id', 'lon', 'lat', 'vlon', 'vlat'])
    """
    datatype = dtype([('jdate', 'f8'), ('swe_id', 'i4'), ('lon', 'f8'), ('lat', 'f8'), ('vlon', 'f8'), ('vlat', 'f8')])
    return array(
        (
            jdate,
            swe_id,
            swe.calc_ut(jdate, swe_id)[0][0],
            swe.calc_ut(jdate, swe_id)[0][1],
            swe.calc_ut(jdate, swe_id)[0][3],
            swe.calc_ut(jdate, swe_id)[0][4],
        ),
        dtype=datatype)


# --------------------------------------------------------


def is_retrograd(props):
    """Return True if a body is retrograd"""
    return props.vlon < 0


def is_ascending(props):
    """Return True if a body latitude is rising"""
    return props.vlat > 0


def is_waxing(angle):
    """Return True if a body is waxing"""
    angle = znorm(angle)
    return angle > 0


def get_chart(jdate, l_bodies=bodies):
    """
    Return the properties of a list of bodies
    """
    swe_id = l_bodies.swe_id
    datatype = dtype([('jdate', 'f8'), ('swe_id', 'i4'), ('lon', 'f8'), ('lat', 'f8'), ('vlon', 'f8'), ('vlat', 'f8')])
    chart = fromiter([properties(jdate, body_id) for body_id in swe_id], dtype=datatype).view(recarray)
    return chart


def get_angle(chart, body1, body2):
    """
    Return angles between body1 et body2
    """
    if bodies.avg_s[body_index(body1)] < bodies.avg_s[body_index(body2)]:
        body1, body2 = body2, body1
    jdate = unique(chart.jdate)
    prop1 = chart[where(chart.swe_id == body1)]
    prop2 = chart[where(chart.swe_id == body2)]
    lon1, lon2 = prop1.lon, prop2.lon
    vlon1, vlon2 = prop1.vlon, prop2.vlon
    angle = znorm(lon1 - lon2)
    datatype = dtype([('jdate', 'f8'), ('body1', 'i4'), ('body2', 'i4'), ('lon1', 'f8'), ('lon2', 'f8'), 
                    ('vlon1', 'f8'), ('vlon2', 'f8'), ('angle', 'f8')])
    c_angle = array((*jdate, body1, body2, *lon1, *lon2, *vlon1, *vlon2, *angle), dtype=datatype)
    return c_angle


def get_angles(chart):
    """
    Return angles between all bodies
    """
    bodies_id = chart.swe_id
    datatype = dtype([('jdate', 'f8'), ('body1', 'i4'), ('body2', 'i4'), ('lon1', 'f8'), ('lon2', 'f8'), 
                    ('vlon1', 'f8'), ('vlon2', 'f8'), ('angle', 'f8')])
    c_angles = fromiter([get_angle(chart, *comb) for comb in combs(bodies_id, 2)],dtype=datatype).view(recarray)
    return c_angles


def gen_aspects(chart):
    """
    dev mode
    """
    c_angles = get_angles(chart)
    for c_angle in c_angles:
        angle = c_angle.angle
        body1, body2 = c_angle.body1, c_angle.body2
        dist = distance(angle)
        for i_asp, aspect in ndenumerate(maspects.angle):
            score = - (body_orb(body1) + body_orb(body2)) * maspects.coef[i_asp]
            orbite = calc_orb(body1, body2, *i_asp)
            if aspect - orbite <= dist <= aspect + orbite:
                yield append_fields(c_angle, ['score', 'i_asp'], [score, *i_asp])


def get_aspects(chart):
    """
    dev mode
    """
    datatype = dtype([('jdate', 'f8'), ('body1', 'i4'), ('body2', 'i4'), ('lon1', 'f8'), ('lon2', 'f8'), 
                    ('vlon1', 'f8'), ('vlon2', 'f8'), ('angle', 'f8'), ('score', 'f8'), ('i_asp', 'i4')])
    aspects = sort(fromiter(gen_aspects(chart), dtype=datatype).view(recarray), order='score')
    return aspects


def get_aspect(chart, body1, body2):
    """
    Return the aspect and orb between two bodies for a jdate
    Return the angle between the two bodies if there's no aspect
    """
    if bodies.avg_s[body_index(body1)] < bodies.avg_s[body_index(body2)]:
        body1, body2 = body2, body1
    aspects = get_aspects(chart)
    aspect = aspects[where(logical_and(aspects.body1 == body1, aspects.body2 == body2))]
    return aspect[0] if aspect else None


def get_aspect_orb(aspect):
    """dev mode"""
    lon1, lon2 = aspect.lon1, aspect.lon2
    i_asp = aspect.i_asp
    orb = distance(lon2 - lon1) - maspects.angle[i_asp]
    return abs(orb)


def is_applicative(aspect):
    """dev mode"""
    jdate = aspect.jdate
    body1 = aspect.body1
    props1 = properties(jdate, body1)
    lon1, lon2 = aspect.lon1, aspect.lon2
    i_asp = aspect.i_asp
    wax = is_waxing(lon1 - lon2)
    asp = maspects.angle[i_asp]
    is_r = is_retrograd(props1)
    angle = distance(lon1 - lon2) - asp
    if i_asp == 0 and ((not wax and not is_r) or (wax and is_r)):
        return True
    if i_asp == 4 and (((wax and not is_r) or (not wax and is_r))):
        return True
    if angle > 0 and not is_r:
        return True
    if angle < 0 and is_r:
        return True
    return False


def find_easpect(aspect):
    """dev mode"""
    jdate = aspect.jdate
    body1, body2 = aspect.body1, aspect.body2
    # i_asp = aspect["i_asp"]
    orb = get_aspect_orb(aspect)
    app = is_applicative(aspect)
    vlon1, vlon2 = aspect.vlon1, aspect.vlon2
    if orb > dms_to_dd([0, 0, 1]):
        delta = orb / (vlon1 - vlon2)
        jdate = jdate + delta if app else jdate - delta
        return find_easpect(get_aspect(get_chart(jdate), body1, body2))
    return jdate


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print("\n")
    print("-------------- Bodies Positions --------------")
    chart = get_chart(jdate)
    for index, props in ndenumerate(chart):
        swe_id, lon = props.swe_id, props.lon
        bsign = body_sign(lon)
        sign, degs, mins, secs = bsign.sign, bsign.degs, bsign.mins, bsign.secs
        retro = ' Retrograd' if is_retrograd(props) else ''
        print(
            f"{body_name(swe_id):10}: "
            f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}"
        )


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print("\n")
    print("------------- Bodies Aspects -------------")
    chart = get_chart(jdate)
    for aspect in get_aspects(chart):
        body1, body2, i_asp = aspect.body1, aspect.body2, aspect.i_asp
        orb = get_aspect_orb(aspect)
        app = is_applicative(aspect)
        degs, mins, secs = dd_to_dms(orb)
        app = 'Applicative' if app else 'Separative'
        name1, name2 = body_name(body1), body_name(body2)
        print(
            f"{name1:7} - {name2:8}: "
            f"{maspects[i_asp].name.decode():12} "
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
    year, month, day, hour, minute = 2022, 7, 13, 19, 34
    dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
    jdate = utc_to_julian(dtime)
    print_positions(jdate)
    print_aspects(jdate)


if __name__ == "__main__":
    main()
