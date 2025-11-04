"""Ketu - Refactored version using numpy-based ephemeris.

This is a refactored version of ketu that removes the pyswisseph dependency
and uses our own numpy-based planetary calculations.
"""

from datetime import datetime
from functools import lru_cache
from itertools import combinations as combs
from typing import Tuple, Optional, List
from zoneinfo import ZoneInfo

import numpy as np

# Import our new ephemeris modules
from .ephemeris.time import utc_to_julian, julian_to_utc, local_to_utc
from .ephemeris.planets import (
    calc_planet_position,
    get_planet_name,
    body_properties,
    find_exact_aspect,
    find_all_aspects,
)


# Structured array of astronomical bodies with same format as original
bodies = np.array(
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
        ("North Node", 11, 0, -0.013),
        ("Lilith", 12, 0, 0.113),
    ],
    dtype=[("name", "S12"), ("id", "i4"), ("orb", "f4"), ("speed", "f4")],
)

# Structured array of major aspects
aspects = np.array(
    [
        ("Conjunction", 0, 1),
        ("Semi-sextile", 30, 1 / 6),
        ("Sextile", 60, 1 / 3),
        ("Square", 90, 1 / 2),
        ("Trine", 120, 2 / 3),
        ("Quincunx", 150, 5 / 6),
        ("Opposition", 180, 1),
    ],
    dtype=[("name", "S12"), ("value", "f4"), ("coef", "f4")],
)

# List of signs
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


def dd_to_dms(deg: float) -> np.ndarray:
    """Return degrees, minutes, seconds from degrees decimal"""
    mins, secs = divmod(deg * 3600, 60)
    degs, mins = divmod(mins, 60)
    return np.array((degs, mins, secs), dtype="i4")


def distance(pos1: float, pos2: float) -> float:
    """Return the angular distance from two bodies positions"""
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


def get_orb(body1: int, body2: int, asp: int) -> float:
    """Calculate the orb for two bodies and aspect"""
    orbs, coef = bodies["orb"], aspects["coef"]
    return (orbs[body1] + orbs[body2]) / 2 * coef[asp]


# --------- Updated interface functions ---------


def body_name(body: int) -> str:
    """Return the body name"""
    name = get_planet_name(body)
    # Convert to match original format
    if name == "mean Node":
        return "Rahu"
    elif name == "true Node":
        return "North Node"
    elif name == "mean Apogee":
        return "Lilith"
    return name


def body_id(b_name: str) -> int:
    """Return the body id"""
    return bodies["id"][np.where(bodies["name"] == b_name.encode())][0]


def long(jdate: float, body: int) -> float:
    """Return the body longitude"""
    return body_properties(jdate, body)[0]


def lat(jdate: float, body: int) -> float:
    """Return the body latitude"""
    return body_properties(jdate, body)[1]


def dist_au(jdate: float, body: int) -> float:
    """Return distance of the body to Earth in AU"""
    return body_properties(jdate, body)[2]


def vlong(jdate: float, body: int) -> float:
    """Return the body longitude speed"""
    return body_properties(jdate, body)[3]


def vlat(jdate: float, body: int) -> float:
    """Return the body latitude speed"""
    return body_properties(jdate, body)[4]


def vdist_au(jdate: float, body: int) -> float:
    """Return the distance speed of the body"""
    return body_properties(jdate, body)[5]


def is_retrograde(jdate: float, body: int) -> bool:
    """Return True if a body is retrograde"""
    return vlong(jdate, body) < 0


def is_ascending(jdate: float, body: int) -> bool:
    """Return True if a body latitude is rising"""
    return vlat(jdate, body) > 0


def body_sign(b_long: float) -> Tuple[int, int, int, int]:
    """Return the body position in sign, degrees, minutes and seconds"""
    dms = dd_to_dms(b_long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return sign, degs, mins, secs


def positions(jdate: float, l_bodies=bodies) -> np.ndarray:
    """Return an array of bodies longitude"""
    bodies_id = l_bodies["id"]
    return np.array([long(jdate, body) for body in bodies_id])


def get_aspect(jdate: float, body1: int, body2: int) -> Optional[Tuple]:
    """
    Return the aspect and orb between two bodies for a certain date
    Return None if there's no aspect
    """
    if body1 > body2:
        body1, body2 = body2, body1
    dist = distance(long(jdate, body1), long(jdate, body2))
    for i_asp, aspect in enumerate(aspects["value"]):
        orb = get_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif aspect - orb <= dist <= aspect + orb:
            return body1, body2, i_asp, aspect - dist
    return None


def calculate_aspects(jdate: float, l_bodies=bodies) -> np.ndarray:
    """
    Return a structured array of aspects and orb
    Return None if there's no aspect
    """
    bodies_id = l_bodies["id"]
    aspects_data = [get_aspect(jdate, *comb) for comb in combs(bodies_id, 2)]
    aspects_data = [aspect for aspect in aspects_data if aspect is not None]
    return np.array(
        aspects_data,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


# New functions for TODO features
def find_aspect_timing(jdate: float, body1: int, body2: int, aspect_value: float) -> Tuple[float, float, float]:
    """Find beginning, exact, and end times for an aspect.

    Args:
        jdate: Reference Julian Date
        body1: First body ID
        body2: Second body ID
        aspect_value: Aspect angle in degrees

    Returns:
        Tuple of (begin_jd, exact_jd, end_jd)
    """
    # Get the aspect index
    asp_idx = np.where(aspects["value"] == aspect_value)[0]
    if len(asp_idx) == 0:
        raise ValueError(f"Unknown aspect value: {aspect_value}")
    asp_idx = asp_idx[0]

    # Calculate orb
    orb = get_orb(body1, body2, asp_idx)

    # Search backward for beginning
    jd_begin = jdate
    step = -0.25  # Quarter day steps
    for _ in range(400):  # Max 100 days backward
        pos1 = long(jd_begin, body1)
        pos2 = long(jd_begin, body2)
        dist = distance(pos1, pos2)

        if abs(dist - aspect_value) > orb:
            jd_begin -= step
            break
        jd_begin += step

    # Search forward for end
    jd_end = jdate
    step = 0.25
    for _ in range(400):  # Max 100 days forward
        pos1 = long(jd_end, body1)
        pos2 = long(jd_end, body2)
        dist = distance(pos1, pos2)

        if abs(dist - aspect_value) > orb:
            jd_end -= step
            break
        jd_end += step

    # Find exact aspect
    exact_jd = find_exact_aspect(jd_begin, jd_end, body1, body2, aspect_value, orb)

    if exact_jd is None:
        exact_jd = jdate  # Fallback to reference date

    return jd_begin, exact_jd, jd_end


def find_aspects_between_dates(
    jdate_start: float, jdate_end: float, body1: Optional[int] = None, body2: Optional[int] = None
) -> List[Tuple]:
    """Find all aspects between two dates.

    Args:
        jdate_start: Start Julian Date
        jdate_end: End Julian Date
        body1: First body ID (optional, if None check all)
        body2: Second body ID (optional, if None check all)

    Returns:
        List of tuples (jdate, body1, body2, aspect_type, aspect_value)
    """
    results = []

    # Determine which body pairs to check
    if body1 is not None and body2 is not None:
        pairs = [(body1, body2)]
    elif body1 is not None:
        pairs = [(body1, b) for b in bodies["id"] if b != body1]
    elif body2 is not None:
        pairs = [(b, body2) for b in bodies["id"] if b != body2]
    else:
        pairs = list(combs(bodies["id"], 2))

    # Check each pair
    for b1, b2 in pairs:
        if b1 > b2:
            b1, b2 = b2, b1

        # Find all aspects for this pair
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(aspects["value"]))

        for exact_jd, aspect_angle in aspect_list:
            # Find aspect type
            asp_idx = np.where(aspects["value"] == aspect_angle)[0][0]
            aspect_name = aspects["name"][asp_idx].decode()

            results.append((exact_jd, b1, b2, aspect_name, aspect_angle))

    return sorted(results, key=lambda x: x[0])


def print_positions(jdate: float):
    """Function to format and print positions of the bodies for a date"""
    print("\n")
    print("------------- Bodies Positions -------------")
    for index, pos in np.ndenumerate(positions(jdate)):
        sign, degs, mins, secs = body_sign(pos)
        retro = ", R" if is_retrograde(jdate, *index) else ""
        print(f"{body_name(*index):10}: " f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


def print_aspects(jdate: float):
    """Function to format and print aspects between the bodies for a date"""
    print("\n")
    print("------------- Bodies Aspects -------------")
    for aspect in calculate_aspects(jdate):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
        print(
            f"{body_name(body1):7} - {body_name(body2):12}: "
            f"{aspects['name'][i_asp].decode():12} "
            f"{degs:>2}º{mins:>2}'{secs:>2}\""
        )


def main():
    """Entry point of the program"""
    try:
        year, month, day = map(int, input("Give a date with ISO format, ex: 2020-12-21\n").split("-"))
        hour, minute = map(int, input("Give a time (hour, minute), with ISO format, ex: 19:20\n").split(":"))
        tzinfo = input("Give the Time Zone, ex: 'Europe/Paris' for France: ") or "Europe/Paris"
        zoneinfo = ZoneInfo(tzinfo)
        dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
        jday = utc_to_julian(dtime)
        print_positions(jday)
        print_aspects(jday)

        # Demo of new features
        print("\n------------- Aspect Timing Example -------------")
        # Example: Find timing for Sun-Moon conjunction
        sun_id = body_id("Sun")
        moon_id = body_id("Moon")

        aspects_found = find_aspects_between_dates(jday - 15, jday + 15, sun_id, moon_id)
        for asp in aspects_found[:3]:  # Show first 3
            exact_jd, b1, b2, asp_name, asp_val = asp
            exact_dt = julian_to_utc(exact_jd)
            print(f"{body_name(b1)} {asp_name} {body_name(b2)} at {exact_dt}")

    except ValueError as e:
        print(f"Error : {e}")
        print("Please enter a valid date and time with ISO format")


if __name__ == "__main__":
    main()
