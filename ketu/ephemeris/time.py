"""Time conversion functions for astronomical calculations.

This module provides functions to convert between different time systems
used in astronomical calculations, replacing pyswisseph time functions.
"""

import numpy as np
from datetime import datetime, timezone
from typing import Union, Tuple


def utc_to_julian(dtime: datetime) -> float:
    """Convert UTC datetime to Julian Date.

    Args:
        dtime: datetime object (timezone-aware or naive assumed UTC)

    Returns:
        Julian Date as float

    Notes:
        Julian Date is the number of days since January 1, 4713 BCE noon.
        This implementation follows the standard astronomical convention.
    """
    # Ensure we have UTC time
    if dtime.tzinfo is not None:
        # Convert to UTC if timezone-aware
        utc = dtime.astimezone(timezone.utc)
    else:
        # Assume naive datetime is UTC
        utc = dtime

    year, month, day = utc.year, utc.month, utc.day
    hour, minute, second = utc.hour, utc.minute, utc.second

    # Calculate fractional day
    day_fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0

    # Algorithm for Gregorian calendar
    if month <= 2:
        year -= 1
        month += 12

    A = np.floor(year / 100)
    B = 2 - A + np.floor(A / 4)

    if year < 1582 or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15):
        # Julian calendar
        B = 0

    JD = np.floor(365.25 * (year + 4716)) + np.floor(30.6001 * (month + 1)) + day + B - 1524.5 + day_fraction

    return float(JD)


def julian_to_utc(jd: float) -> datetime:
    """Convert Julian Date to UTC datetime.

    Args:
        jd: Julian Date

    Returns:
        UTC datetime object
    """
    jd = jd + 0.5
    Z = int(jd)
    F = jd - Z

    if Z < 2299161:
        # Julian calendar
        A = Z
    else:
        # Gregorian calendar
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F

    if E < 14:
        month = E - 1
    else:
        month = E - 13

    if month > 2:
        year = C - 4716
    else:
        year = C - 4715

    # Extract time from fractional day
    day_int = int(day)
    day_frac = day - day_int

    hours_frac = day_frac * 24
    hours = int(hours_frac)

    mins_frac = (hours_frac - hours) * 60
    mins = int(mins_frac)

    secs = (mins_frac - mins) * 60
    secs = int(secs)

    return datetime(year, month, day_int, hours, mins, secs, tzinfo=timezone.utc)


def delta_t(year: float) -> float:
    """Calculate Delta T (TT - UT1) for a given year.

    Args:
        year: Year as float (can include fractional year)

    Returns:
        Delta T in seconds

    Notes:
        Uses polynomial expressions from Espenak & Meeus (2006)
        for historical values and extrapolation for future dates.
    """
    if year < -500:
        u = (year - 1820) / 100
        return -20 + 32 * u**2
    elif year < 500:
        u = year / 100
        return (
            10583.6
            - 1014.41 * u
            + 33.78311 * u**2
            - 5.952053 * u**3
            - 0.1798452 * u**4
            + 0.022174192 * u**5
            + 0.0090316521 * u**6
        )
    elif year < 1600:
        u = (year - 1000) / 100
        return (
            1574.2
            - 556.01 * u
            + 71.23472 * u**2
            + 0.319781 * u**3
            - 0.8503463 * u**4
            - 0.005050998 * u**5
            + 0.0083572073 * u**6
        )
    elif year < 1700:
        t = year - 1600
        return 120 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129
    elif year < 1800:
        t = year - 1700
        return 8.83 + 0.1603 * t - 0.0059285 * t**2 + 0.00013336 * t**3 - t**4 / 1174000
    elif year < 1860:
        t = year - 1800
        return (
            13.72
            - 0.332447 * t
            + 0.0068612 * t**2
            + 0.0041116 * t**3
            - 0.00037436 * t**4
            + 0.0000121272 * t**5
            - 0.0000001699 * t**6
            + 0.000000000875 * t**7
        )
    elif year < 1900:
        t = year - 1860
        return 7.62 + 0.5737 * t - 0.251754 * t**2 + 0.01680668 * t**3 - 0.0004473624 * t**4 + t**5 / 233174
    elif year < 1920:
        t = year - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    elif year < 1941:
        t = year - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    elif year < 1961:
        t = year - 1950
        return 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    elif year < 1986:
        t = year - 1975
        return 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    elif year < 2005:
        t = year - 2000
        return 63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3 + 0.000651814 * t**4 + 0.00002373599 * t**5
    elif year < 2050:
        t = year - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    elif year < 2150:
        # Extrapolation
        return -20 + 32 * ((year - 1820) / 100) ** 2 - 0.5628 * (2150 - year)
    else:
        # Far future extrapolation
        u = (year - 1820) / 100
        return -20 + 32 * u**2


def terrestrial_to_universal(jd_tt: float) -> float:
    """Convert Terrestrial Time (TT) to Universal Time (UT).

    Args:
        jd_tt: Julian Date in Terrestrial Time

    Returns:
        Julian Date in Universal Time
    """
    # Extract year from Julian Date for Delta T calculation
    # Approximate conversion
    year = (jd_tt - 2451545.0) / 365.25 + 2000.0

    # Delta T in days
    delta_t_days = delta_t(year) / 86400.0

    return jd_tt - delta_t_days


def universal_to_terrestrial(jd_ut: float) -> float:
    """Convert Universal Time (UT) to Terrestrial Time (TT).

    Args:
        jd_ut: Julian Date in Universal Time

    Returns:
        Julian Date in Terrestrial Time
    """
    # Extract year from Julian Date for Delta T calculation
    year = (jd_ut - 2451545.0) / 365.25 + 2000.0

    # Delta T in days
    delta_t_days = delta_t(year) / 86400.0

    return jd_ut + delta_t_days


def equation_of_time(jd: float) -> float:
    """Calculate the equation of time for a given Julian Date.

    Args:
        jd: Julian Date

    Returns:
        Equation of time in minutes

    Notes:
        The equation of time is the difference between apparent solar time
        and mean solar time. Positive values indicate the sun is ahead of
        mean time.
    """
    # Days since J2000.0
    n = jd - 2451545.0

    # Mean longitude of the Sun
    L = np.deg2rad(280.460 + 0.9856474 * n)
    L = L % (2 * np.pi)

    # Mean anomaly of the Sun
    g = np.deg2rad(357.528 + 0.9856003 * n)
    g = g % (2 * np.pi)

    # Obliquity of the ecliptic
    eps = np.deg2rad(23.439 - 0.0000004 * n)

    # Equation of time in radians
    E = L - 0.0057183 - np.arctan2(np.tan(L), np.cos(eps))

    # Add periodic terms
    E = E + 0.00478 * np.sin(2 * g) - 0.0000151 * np.sin(4 * g)

    # Convert to minutes
    E_minutes = np.rad2deg(E) * 4  # 4 minutes per degree

    return float(E_minutes)


def sidereal_time(jd: float, longitude: float = 0.0) -> float:
    """Calculate Greenwich Mean Sidereal Time (GMST) or Local Sidereal Time.

    Args:
        jd: Julian Date in UT
        longitude: Observer's longitude in degrees (east positive).
                  If 0, returns GMST.

    Returns:
        Sidereal time in degrees (0-360)
    """
    # Days and centuries since J2000.0
    d = jd - 2451545.0
    T = d / 36525.0

    # GMST at 0h UT
    gmst = 280.46061837 + 360.98564736629 * d + 0.000387933 * T**2 - T**3 / 38710000.0

    # Normalize to 0-360 degrees
    gmst = gmst % 360.0
    if gmst < 0:
        gmst += 360.0

    # Add longitude for local sidereal time
    lst = (gmst + longitude) % 360.0

    return lst


def local_to_utc(dtime: datetime) -> datetime:
    """Convert local time to UTC time.

    Args:
        dtime: datetime object (timezone-aware or naive)

    Returns:
        UTC datetime object

    Notes:
        If datetime is naive, it's returned as-is with UTC timezone.
        If datetime is timezone-aware, it's converted to UTC.
    """
    if dtime.tzinfo is not None:
        return dtime.astimezone(timezone.utc)
    else:
        # Assume naive datetime is already UTC
        return dtime.replace(tzinfo=timezone.utc)
