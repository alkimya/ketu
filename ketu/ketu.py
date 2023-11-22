"""
Ketu is a python library to generate time series and calendars based on
planetary aspects
"""

from datetime import datetime, timedelta
from functools import lru_cache
from itertools import combinations as combs
from zoneinfo import ZoneInfo

from numpy import (
    argwhere,
    all,
    asarray,
    dtype,
    fromiter,
    isin,
    logical_and,
    array,
    ndenumerate,
    nonzero,
    recarray,
    sort,
    unique,
    vectorize,
    where
)

from numpy.lib.recfunctions import append_fields
from numpy.typing import ArrayLike

import swisseph as swe

# Vectorized lambda function to decode elements of an array or list using UTF-8
utf_8 = vectorize(lambda x: x.decode('UTF-8'))

utc = ZoneInfo('UTC')


# Structured array of astronomical bodies: Sun, Moon, Mercury, Venus, Mars,
# Jupiter, Saturn, Uranus, Neptune, Pluto, mean Node aka Rahu, mean Apogee aka
# Lilith, their Swiss Ephemeris id's, their orb of influence
# (Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050))
# and their average speed in degrees per day
bodies = array(
    [
        ("Sun", 0, 12, 0.986),
        ("Moon", 1, 12, 13.176),
        ("Mercury", 2, 8, 1.383),
        ("Venus", 3, 8, 1.2),
        ("Mars", 4, 10, 0.524),
        ("Jupiter", 5, 10, 0.083),
        ("Saturn", 6, 10, 0.034),
        ("Uranus", 7, 6, 0.012),
        ("Neptune", 8, 6, 0.007),
        ("Pluto", 9, 4, 0.004),
        ("Rahu", 10, 0, -0.013),
        ("Lilith", 12, 0, 0.113),
    ],
    dtype=[("name", "S12"), ("swe_id", "i4"), ("orb", "f8"), ("speed", "f8")],
)

# Structured array of major aspects (harmonics 2 and 3): Conjunction, 
# Semi-sextile, Sextile, Square, Trine, Quincunx and Opposition, 
# their value and their coefficient for the calculation of the orb
aspects = array(
    [
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1/6),
        ("Sextile", 60, 1/3),
        ("Square", 90, 1/2),
        ("Trine", 120, 2/3),
        ("Quincunx", 150, 5/6),
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S12"), ("angle", "f8"), ("coef", "f8")],
)


# List of signs for body position
signs = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


# ------------------------- Utilities to work with angles and datetimes ---------------------------

@vectorize
def sign(long):
    """Return the body position in sign, degrees, minutes and seconds from longitude"""

    degs, mins, secs = dd_to_dms(long)
    sign, degs = divmod(degs, 30)
    datatype = dtype([("sign", "i4"), ("degs", "i4"), ("mins", "i4"), ("secs", "i4")])

    return array((sign, degs, mins, secs), dtype=datatype)


@vectorize
def dd_to_dms(dd):
    """Return degrees, minutes, seconds from degrees decimal"""

    mins, secs = divmod(int(dd * 3600), 60)
    degs, mins = divmod(mins, 60)

    return degs, mins, secs


@vectorize
def dms_to_dd(dms):
    """Return degrees decimal from degrees, minutes, seconds"""

    return sum(value / (60 ** i) for i, value in enumerate(dms))


@vectorize
def norm(angle):
    """Normalize the angular distance of two bodies between 0 - 360"""

    return angle % 360


@vectorize
def znorm(angle):
    """Return the normalized angle of two bodies between -180 and 180"""

    angle = norm(angle)

    return angle if angle < 180 else angle - 360


@vectorize
def distance(angle):
    """Return the angular distance from two bodies positions < 180"""

    return abs(znorm(angle))


@vectorize
def local_to_utc(dtime):
    """Convert local time to  UTC time"""

    if dtime.tzinfo is None:
        dtime = dtime.replace(tzinfo=ZoneInfo('UTC'))
    
    return dtime - dtime.utcoffset()


@vectorize
def utc_to_julian(dtime):
    """Convert a UTC datetime to a Julian date"""

    # Convert naive datetime or local datetime to aware UTC datetime
    utc_dtime = local_to_utc(dtime)

    # Reference datetime and Julian date at noon on January 1, 1
    day_one = datetime(1, 1, 1, 12, 0, 0, tzinfo=utc)
    julian_day_one = 1721426

    time_delta = utc_dtime - day_one    
    julian_date = julian_day_one + time_delta.days

    # Add fractional part of the day
    seconds_in_day = 86400.0
    fractional_day = time_delta.seconds / seconds_in_day
    julian_date += fractional_day

    return julian_date


@vectorize
def julian_to_utc(julian_date):
    """Convert a Julian date to a UTC datetime"""

    # Reference datetime and Julian date at noon on January 1, 1
    day_one = datetime(1, 1, 1, 12, 0, 0, tzinfo=utc)
    julian_day_one = 1721426

    # Calculate difference in days
    day_diff = julian_date - julian_day_one
    
    # Create datetime from day difference
    utc_datetime = day_one + timedelta(days=int(day_diff))

    # Get fractional day in seconds  
    seconds = int((julian_date % 1) * 86400)

    # Breakdown seconds
    hours, minutes = divmod(seconds, 3600)
    minutes, seconds = divmod(minutes, 60)

    utc_datetime += timedelta(hours=hours, minutes=minutes, seconds=seconds)

    return utc_datetime



@vectorize
def utc_to_local(utc_dtime, zoneinfo=utc):
    """Convert UTC datetime to given timezone """

    local_dtime = utc_dtime.astimezone(zoneinfo)

    return local_dtime


def calc_orb(body1, body2, asp):
    """Calculate the orb for two bodies and aspect"""

    # Get body objects
    b1 = bodies[body1]
    b2 = bodies[body2]
    
    # Get orb values
    orb1 = b1['orb']
    orb2 = b2['orb']
    
    # Get aspect coefficient 
    coef = aspects['coef'][asp]
    
    # Calculate combined orb
    comb_orb = (orb1 + orb2) / 2 * coef

    return comb_orb

    
# def is_retrograd(props):
#     """Return True if a body is retrograd"""

#     return props['vlon'] < 0


# def is_ascending(props):
#     """Return True if a body latitude is rising"""

#     return props['vlat'] > 0


# def is_waxing(angle):
#     """Return True if a body is waxing"""

#     angle = znorm(angle)
    
#     return angle > 0


# def get_angle(chart, body1, body2):
#     """
#     Return angles between body1 et body2
#     """
#     if bodies['speed'][get_bodies(body1)] < bodies['speed'][get_bodies(body2)]:
#         body1, body2 = body2, body1
#     jdate = unique(chart['jdate'])
#     prop1 = chart[nonzero(chart['swe_id'] == body1)]
#     prop2 = chart[nonzero(chart['swe_id'] == body2)]
#     lon1, lon2 = prop1['lon'], prop2['lon']
#     vlon1, vlon2 = prop1['vlon'], prop2['vlon']
#     angle = znorm(lon1 - lon2)
#     datatype = dtype(
#         [
#             ("jdate", "f8"),
#             ("body1", "i4"),
#             ("body2", "i4"),
#             ("lon1", "f8"),
#             ("lon2", "f8"),
#             ("vlon1", "f8"),
#             ("vlon2", "f8"),
#             ("angle", "f8"),
#         ]
#     )
#     return array((*jdate, body1, body2, *lon1, *lon2, *vlon1, *vlon2, *angle), dtype=datatype,)


# def get_angles(chart):
#     """
#     Return angles between all bodies
#     """
#     bodies_id = chart['swe_id']
#     datatype = dtype(
#         [
#             ("jdate", "f8"),
#             ("body1", "i4"),
#             ("body2", "i4"),
#             ("lon1", "f8"),
#             ("lon2", "f8"),
#             ("vlon1", "f8"),
#             ("vlon2", "f8"),
#             ("angle", "f8"),
#         ]
#     )
#     return fromiter(
#         [get_angle(chart, *comb) for comb in combs(bodies_id, 2)],
#         dtype=datatype,
#     ).view(recarray)


# def gen_aspects(chart):
#     """
#     dev mode
#     """
#     c_angles = get_angles(chart)

#     for c_angle in c_angles:
#         angle = c_angle['angle']
#         body1, body2 = c_angle['body1'], c_angle['body2']
#         dist = distance(angle)

#         for i_asp, aspect in ndenumerate(aspects['angle']):
#             orbite = calc_orb(body1, body2, *i_asp)

#             if aspect - orbite <= dist <= aspect + orbite:
#                 score = -(bodies_orb(body1) + bodies_orb(body2)) * aspects['coef'][i_asp]
#                 yield append_fields(c_angle, ["score", "i_asp"], [score, *i_asp])


# def get_aspects(chart):
#     """
#     dev mode
#     """
#     datatype = dtype(
#         [
#             ("jdate", "f8"),
#             ("body1", "i4"),
#             ("body2", "i4"),
#             ("lon1", "f8"),
#             ("lon2", "f8"),
#             ("vlon1", "f8"),
#             ("vlon2", "f8"),
#             ("angle", "f8"),
#             ("score", "f8"),
#             ("i_asp", "i4"),
#         ]
#     )
#     return sort(fromiter(gen_aspects(chart), dtype=datatype).view(recarray), order="score",)


# def get_aspect(chart, body1, body2):
#     """
#     Return the aspect and orb between two bodies for a jdate
#     Return the angle between the two bodies if there's no aspect
#     """
#     if get_bodies['speed'][index(body1)] < get_bodies['speed'][index(body2)]:
#         body1, body2 = body2, body1
#     aspects = get_aspects(chart)
#     aspect = aspects[nonzero(logical_and(aspects['body1'] == body1, aspects['body2'] == body2))]
#     return aspect[0] if aspect else None
#     #matching_aspects = [aspect for aspect in aspects if aspect.body1 == body1 and aspect.body2 == body2]
#     #return matching_aspects[0] if matching_aspects else None


# def get_aspect_orb(aspect):
#     """dev mode"""
#     lon1, lon2 = aspect['lon1'], aspect['lon2']
#     i_asp = aspect['i_asp']
#     orb = distance(lon2 - lon1) - aspects['angle'][i_asp]
#     return abs(orb)


# def is_applicative(aspect):
#     """dev mode"""
#     jdate = aspect['jdate']
#     body1 = aspect['body1']
#     props1 = properties(jdate, body1)
#     lon1, lon2 = aspect['lon1'], aspect['lon2']
#     i_asp = aspect['i_asp']
#     wax = is_waxing(lon1 - lon2)
#     asp = aspects['angle'][i_asp]
#     is_r = is_retrograd(props1)
#     angle = distance(lon1 - lon2) - asp
#     if not i_asp and ((not wax and not is_r) or (wax and is_r)):
#         return True
#     if i_asp == 4 and (((wax and not is_r) or (not wax and is_r))):
#         return True
#     return True if angle > 0 and not is_r else bool(angle < 0 and is_r)


# def find_easpect(aspect):
#     """
#     Find the exact date and time of an astrological aspect between two celestial bodies.

#     Args:
#         aspect (Aspect): An object representing the astrological aspect.

#     Returns:
#         float: The Julian date representing the exact date and time of the aspect.
#     """
#     jdate = aspect['jdate']
#     body1, body2 = aspect['body1'], aspect['body2']
#     # i_asp = aspect["i_asp"]
#     orb = get_aspect_orb(aspect)
#     app = is_applicative(aspect)
#     vlon1, vlon2 = aspect['vlon1'], aspect['vlon2']
#     if orb > dms_to_dd([0, 0, 1]):
#         delta = orb / (vlon1 - vlon2)
#         jdate = jdate + delta if app else jdate - delta
#         return find_easpect(get_aspect(get_chart(jdate), body1, body2))
#     return jdate


# def find_easpect2(aspect):
#     jdate = aspect['jdate']
#     body1, body2 = aspect['body1'], aspect['body2']
#     vlon1, vlon2 = aspect['vlon1'], aspect['vlon2']
#     orb = get_aspect_orb(aspect)
#     app = is_applicative(aspect)
 
#     while orb > THRESHOLD:
#         delta = orb / (vlon1 - vlon2)
#         jdate = jdate + delta if app else jdate - delta
#         aspect = get_aspect(get_chart(jdate), body1, body2)
#         orb = get_aspect_orb(aspect)
#     return jdate


# def print_positions(jdate):
#     """Function to format and print positions of the bodies for a date"""
#     print("\n")
#     print("-------------- Bodies Positions --------------")
#     chart = get_chart(jdate)
#     for props in ndenumerate(chart):
#         swe_id, lon = props[1]['swe_id'], props[1]['lon']
#         bsign = sign(lon)
#         sign, degs, mins, secs = bsign['sign'], bsign['degs'], bsign['mins'], bsign['secs']
#         retro = " Retrograd" if is_retrograd(props[1]) else ""
#         print(f"{bodies_name(swe_id):10}: " f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


# def print_aspects(jdate):
#     """Function to format and print aspects between the bodies for a date"""
#     print("\n")
#     print("------------- Bodies Aspects -------------")
#     chart = get_chart(jdate)
#     for aspect in get_aspects(chart):
#         body1, body2, i_asp = aspect['body1'], aspect['body2'], aspect['i_asp']
#         orb = get_aspect_orb(aspect)
#         app = is_applicative(aspect)
#         degs, mins, secs = dd_to_dms(orb)
#         app = "Applicative" if app else "Separative"
#         name1, name2 = bodies_name(body1), bodies_name(body2)
#         print(
#             f"{name1:7} - {name2:8}: "
#             f"{aspects[i_asp].name.decode():12} "
#             f"{degs:>3}º{mins:>3}'{secs:>3}\" "
#             f"{app:>12} "
#         )


# def main():
#     """Entry point of the programm"""
#     year, month, day = map(int, input("Give a date with iso format, ex: 2020-12-21\n").split("-"),)
#     hour, minute = map(
#         int,
#         input("Give a time (hour, minute), with iso format, ex: 19:20\n").split(":"),
#     )
#     tzinfo = input("Give the Time Zone, ex: 'Europe/Paris' for France\n") or "Europe/Paris"

#     zoneinfo = ZoneInfo(tzinfo)
#     # year, month, day, hour, minute = 2022, 7, 13, 19, 34
#     dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
#     jdate = utc_to_julian(dtime)
#     print_positions(jdate)
#     print_aspects(jdate)


# if __name__ == "__main__":
#     main()
