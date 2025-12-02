"""Astronomical and astrological calculations for Ketu.

This module contains position, velocity, and time conversion calculations for planetary bodies.
For aspect calculations, see the aspects module.
"""

from functools import lru_cache
from typing import Tuple

import numpy as np

# Import core data structures
from .core import bodies, aspects, signs

# Import ephemeris calculation functions
from .ephemeris.time import utc_to_julian, julian_to_utc, local_to_utc
from .ephemeris.planets import (
    calc_planet_position,
    get_planet_name,
    body_properties as _body_properties_uncached,
)


# ========== Utility Functions ==========

def dd_to_dms(deg: float) -> np.ndarray:
    """Convert decimal degrees to degrees, minutes, seconds.

    Args:
        deg: Decimal degrees

    Returns:
        Array of [degrees, minutes, seconds] as integers
    """
    mins, secs = divmod(deg * 3600, 60)
    degs, mins = divmod(mins, 60)
    return np.array((degs, mins, secs), dtype="i4")


# Alias for backward compatibility
decimal_degrees_to_dms = dd_to_dms


def distance(pos1: float, pos2: float) -> float:
    """Calculate angular distance between two positions (vectorized).

    Works with scalars or arrays via NumPy broadcasting.
    Always returns the shortest angular distance (0-180 degrees).

    Args:
        pos1: First position in degrees
        pos2: Second position in degrees

    Returns:
        Shortest angular distance in degrees
    """
    angle = np.abs(pos2 - pos1)
    return np.where(angle <= 180, angle, 360 - angle)


# ========== Body Position Functions ==========

@lru_cache(maxsize=1024)
def body_properties(jdate: float, body: int) -> np.ndarray:
    """Cached wrapper for body_properties to maintain API compatibility.

    Uses LRU cache (maxsize=1024) for optimal performance with repeated calculations.
    Benchmark shows 6.7x speedup vs no cache, and better performance than unbounded cache.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Array of [lon, lat, dist, lon_speed, lat_speed, dist_speed]
    """
    return _body_properties_uncached(jdate, body)


def body_name(body: int) -> str:
    """Get the name of an astronomical body.

    Args:
        body: Body ID (0-12)

    Returns:
        Body name as string
    """
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
    """Get the ID of an astronomical body by name.

    Args:
        b_name: Body name (e.g., "Sun", "Moon", "Mars")

    Returns:
        Body ID (0-12)
    """
    return bodies["id"][np.where(bodies["name"] == b_name.encode())][0]


def long(jdate: float, body: int) -> float:
    """Get ecliptic longitude of a body.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Longitude in degrees (0-360)
    """
    return body_properties(jdate, body)[0]


def lat(jdate: float, body: int) -> float:
    """Get ecliptic latitude of a body.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Latitude in degrees
    """
    return body_properties(jdate, body)[1]


def dist_au(jdate: float, body: int) -> float:
    """Get distance of a body from Earth.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Distance in Astronomical Units (AU)
    """
    return body_properties(jdate, body)[2]


def vlong(jdate: float, body: int) -> float:
    """Get longitude velocity of a body.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Longitude speed in degrees/day
    """
    return body_properties(jdate, body)[3]


def vlat(jdate: float, body: int) -> float:
    """Get latitude velocity of a body.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Latitude speed in degrees/day
    """
    return body_properties(jdate, body)[4]


def vdist_au(jdate: float, body: int) -> float:
    """Get distance velocity of a body.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        Distance speed in AU/day
    """
    return body_properties(jdate, body)[5]


def is_retrograde(jdate: float, body: int) -> bool:
    """Check if a body is in retrograde motion.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        True if retrograde (negative longitude velocity)
    """
    return bool(vlong(jdate, body) < 0)


def is_ascending(jdate: float, body: int) -> bool:
    """Check if a body's latitude is rising.

    Args:
        jdate: Julian Date
        body: Body ID (0-12)

    Returns:
        True if latitude is increasing
    """
    return bool(vlat(jdate, body) > 0)


def body_sign(b_long: float) -> Tuple[int, int, int, int]:
    """Convert longitude to zodiac sign position.

    Args:
        b_long: Ecliptic longitude in degrees

    Returns:
        Tuple of (sign_index, degrees, minutes, seconds)
    """
    dms = dd_to_dms(b_long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return sign, degs, mins, secs


def positions(jdate: float, l_bodies=bodies) -> np.ndarray:
    """Get ecliptic longitudes of all bodies.

    Args:
        jdate: Julian Date
        l_bodies: Bodies array (default: all bodies)

    Returns:
        Array of longitudes in degrees
    """
    bodies_id = l_bodies["id"]
    return np.array([long(jdate, body) for body in bodies_id])


__all__ = [
    # Utility functions
    "dd_to_dms",
    "decimal_degrees_to_dms",
    "distance",

    # Body functions
    "body_properties",
    "body_name",
    "body_id",
    "long",
    "lat",
    "dist_au",
    "vlong",
    "vlat",
    "vdist_au",
    "is_retrograde",
    "is_ascending",
    "body_sign",
    "positions",

    # Time functions (re-exported from ephemeris)
    "utc_to_julian",
    "julian_to_utc",
    "local_to_utc",
]
