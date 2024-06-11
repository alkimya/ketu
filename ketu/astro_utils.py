"""
Ketu is a python library to generate time series and calendars based on
planetary aspects
"""

from datetime import datetime, timedelta
from functools import lru_cache
from itertools import combinations as combs
from zoneinfo import ZoneInfo

import numpy as np

from numpy.lib.recfunctions import append_fields
from numpy.typing import ArrayLike

from astro_data import *
from timea import timea

utc = ZoneInfo("UTC")


# ------------------------- Utilities to work with angles and datetimes ---------------------------


@np.vectorize
def sign(long: float | np.ndarray) -> np.ndarray:
    """
    Returns the body position in sign, degrees, minutes and seconds from the given longitude.

    Args:
        long (float | numpy.ndarray): The longitude value(s) to be converted.

    Returns:
        numpy.ndarray: A structured array with fields 'sign', 'degs', 'mins', and 'secs'
                       containing the sign, degrees, minutes, and seconds of the body position.
    """
    degs, mins, secs = degrees_to_dms(long)
    sign, degs = divmod(degs, 30)
    datatype = np.dtype([("sign", "i4"), ("degs", "i4"), ("mins", "i4"), ("secs", "i4")])
    return np.array((sign, degs, mins, secs), dtype=datatype)


@np.vectorize
def degrees_to_dms(degrees: float | np.ndarray) -> tuple[int, int, int] | np.ndarray:
    """
    Convert degrees to degrees, minutes, seconds.

    Args:
        degrees (float | numpy.ndarray): A scalar value or an array of decimal degrees.

    Returns:
        tuple[int, int, int] | numpy.ndarray: A tuple of (degrees, minutes, seconds) for a scalar input,
                                               or an array of tuples for an array input.
    """
    degrees = np.asarray(degrees)
    mins, secs = divmod(degrees * 3600, 60)
    degs, mins = divmod(mins, 60)
    return degs.astype(int), mins.astype(int), secs.astype(int)


@np.vectorize
def dms_to_degrees(dms: np.ndarray) -> np.ndarray:
    """
    Convert degrees, minutes, seconds to decimal degrees.

    Args:
        dms (np.ndarray): An array of degrees, minutes, and seconds.

    Returns:
        np.ndarray: The decimal degree representation of the input.
    """

    return sum(value / (60**i) for i, value in enumerate(dms))


@np.vectorize
def norm(angle: np.ndarray) -> np.ndarray:
    """Normalize the angular distance of two bodies between 0 - 360 degrees.

    Args:
        angle (np.ndarray): The angular distance to be normalized.

    Returns:
        np.ndarray: The normalized angular distance between 0 and 360 degrees.
    """

    return angle % 360


@np.vectorize
def znorm(angle: np.ndarray) -> np.ndarray:
    """
    Return the normalized angle of two bodies between -180 and 180 degrees.

    Args:
        angle (np.ndarray): The angle to be normalized.

    Returns:
        np.ndarray: The normalized angle between -180 and 180 degrees.
    """

    angle = norm(angle)

    return angle if angle < 180 else angle - 360


@np.vectorize
def distance(angle: np.ndarray) -> np.ndarray:
    """
    Return the angular distance between two angles, normalized to be less than 180 degrees.

    Args:
        angle (np.ndarray): The input angles.

    Returns:
        np.ndarray: The angular distance between the input angles, normalized to be less than 180 degrees.
    """

    return abs(znorm(angle))


@np.vectorize
def local_to_utc(dtime: np.ndarray) -> np.ndarray:
    """Convert a local datetime to UTC datetime.

    Args:
        dtime (np.ndarray): A numpy array of local datetime objects.

    Returns:
        np.ndarray: A numpy array of UTC datetime objects.
    """
    """Convert local time to  UTC time"""

    if dtime.tzinfo is None:
        dtime = dtime.replace(tzinfo=ZoneInfo("UTC"))

    return dtime - dtime.utcoffset()


@np.vectorize
def utc_to_julian(dtime: np.ndarray) -> np.ndarray:
    """Convert a UTC datetime to a Julian date.

    This function takes a NumPy array of UTC datetime objects and returns a NumPy array of the corresponding Julian dates. It first converts any naive or local datetime objects to aware UTC datetime objects, then calculates the Julian date based on the time delta from January 1, 1 at noon.

    Args:
        dtime (np.ndarray): A NumPy array of UTC datetime objects.

    Returns:
        np.ndarray: A NumPy array of the corresponding Julian dates.
    """

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


@np.vectorize
def julian_to_utc(julian_date: np.ndarray) -> np.ndarray:
    """Convert a Julian date to a UTC datetime.

    Args:
        julian_date (np.ndarray): An array of Julian dates to be converted.

    Returns:
        np.ndarray: An array of corresponding UTC datetime objects.
    """

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


@np.vectorize
def utc_to_local(utc_dtime: np.ndarray, zoneinfos: np.ndarray = None) -> np.ndarray:
    """
    Convert UTC datetime to given timezones.

    Args:
        utc_dtime (np.ndarray): An array of UTC datetime objects to be converted.
        zoneinfos (np.ndarray, optional): An array of `ZoneInfo` objects representing the target timezones. If not provided, defaults to the UTC timezone.

    Returns:
        np.ndarray: An array of datetime objects in the given timezones.
    """

    if zoneinfos is None:
        zoneinfos = np.array([ZoneInfo("UTC")])
    local_dtimes = np.empty(zoneinfos.shape, dtype=object)
    for i, zoneinfo in enumerate(zoneinfos):
        local_dtimes[i] = utc_dtime.astimezone(zoneinfo)

    return local_dtimes


def calc_orb(body1, body2, asp):
    """Calculate the orb for two bodies and aspect"""
    # Get body objects
    b1 = bodies_data.data[bodies_data.data["swe_id"] == body1]
    b2 = bodies_data.data[bodies_data.data["swe_id"] == body2]

    # Get orb values
    orb1 = b1["orb"][0]
    orb2 = b2["orb"][0]

    # Get aspect coefficient
    coef = aspects_data.get(asp)["coef"]

    # Calculate combined orb
    comb_orb = (orb1 + orb2) / 2 * coef

    return comb_orb


def is_retrograd(props: np.ndarray) -> np.ndarray:
    """Return True if a body is retrograd"""
    return props["vlon"] < 0


def is_ascending(props: np.ndarray) -> np.ndarray:
    """Return True if a body latitude is ascending"""
    return props["vlat"] > 0


def is_waxing(angle: np.ndarray) -> np.ndarray:
    """Return True if a body is waxing"""
    angle = znorm(angle)
    return angle >= 0 and angle < 180


def get_angle(jdate, body1, body2):
    """
    Return angles between body1 et body2
    """
    props = planets_props(jdate)
    prop1 = props[props["swe_id"] == body1]
    prop2 = props[props["swe_id"] == body2]
    lon1, lon2 = prop1["lon"][0], prop2["lon"][0]
    vlon1, vlon2 = prop1["vlon"][0], prop2["vlon"][0]
    angle = znorm(lon1 - lon2)
    datatype = np.dtype(
        [
            ("jdate", "f8"),
            ("body1", "i4"),
            ("body2", "i4"),
            ("lon1", "f8"),
            ("lon2", "f8"),
            ("vlon1", "f8"),
            ("vlon2", "f8"),
            ("angle", "f8"),
        ]
    )
    return np.array((jdate, body1, body2, lon1, lon2, vlon1, vlon2, angle), dtype=datatype)


def get_angles(jdate):
    """
    Return angles between all bodies
    """
    props = planets_props(jdate)
    return [get_angle(jdate, body1, body2) for body1, body2 in combs(props["swe_id"], 2)]


def get_aspect(jdate, body1, body2):
    """
    Return the aspect and orb between two bodies for a jdate
    Return the angle between the two bodies if there's no aspect
    """
    if bodies_data.speed(body1) < bodies_data.speed(body2):
        body1, body2 = body2, body1
    angle = get_angle(jdate, body1, body2)
    dist = distance(angle["angle"])
    for i_asp, asp in enumerate(aspects_data.angle()):
        orb = calc_orb(body1, body2, i_asp)
        if i_asp == 0 and dist <= orb:
            return body1, body2, i_asp, dist
        elif asp - orb <= dist <= asp + orb:
            return body1, body2, i_asp, asp - dist
    return None


def get_aspects(jdate):
    """
    Return a structured array of aspects and orb
    Return None if there's no aspect
    """
    bodies_id = bodies_data.swe_id()
    aspects_data = [get_aspect(jdate, body1, body2) for body1, body2 in combs(bodies_id, 2)]
    aspects_data = [aspect for aspect in aspects_data if aspect is not None]
    return np.array(
        aspects_data,
        dtype=[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")],
    )


@timea
def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print("\n")
    print("-------------- Bodies Positions --------------")
    chart = planets_props(jdate)
    for props in chart:
        swe_id, lon = props["swe_id"], props["lon"]
        bsign = sign(lon)
        sign_name, degs, mins, secs = signs[bsign["sign"]], bsign["degs"], bsign["mins"], bsign["secs"]
        retro = " Retrograde" if is_retrograd(props) else ""
        print(f"{bodies_data.name(swe_id):10}: {sign_name:15}{degs:>2}°{mins:>2}'{secs:>2}\"{retro}")


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print("\n")
    print("------------- Bodies Aspects -------------")
    aspects = get_aspects(jdate)
    for aspect in aspects:
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = degrees_to_dms(orb)
        print(
            f"{bodies_data.name(body1)[0]:7} - {bodies_data.name(body2)[0]:8}: "
            f"{aspects_data.name(i_asp):12} "
            f"{degs:>2}°{mins:>2}'{secs:>2}\""
        )


def main():
    """Entry point of the program"""
    year, month, day = map(int, input("Give a date with iso format, ex: 2020-12-21\n").split("-"))
    hour, minute = map(int, input("Give a time (hour, minute), with iso format, ex: 19:20\n").split(":"))
    tzinfo = input("Give the Time Zone, ex: 'Europe/Paris' for France\n") or "Europe/Paris"
    zoneinfo = ZoneInfo(tzinfo)
    dtime = datetime(year, month, day, hour, minute, tzinfo=zoneinfo)
    jday = utc_to_julian(dtime)
    print_positions(jday)
    print_aspects(jday)


if __name__ == "__main__":
    main()
