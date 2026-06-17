"""
Astronomical and astrological calculations for Ketu.

This module contains position, velocity, and time conversion calculations for planetary bodies.
For aspect calculations, see the aspects module.
"""

from functools import lru_cache
from typing import Tuple, Union

import numpy as np

# Import core data structures
from .core import bodies, aspects, signs

# Import ephemeris calculation functions
from .ephemeris.time import utc_to_julian, coerce_to_jd, julian_to_utc, local_to_utc
from .ephemeris.planets import (
    calc_planet_position,
    calc_planet_position_batch,
    get_planet_name,
    body_properties as _body_properties_uncached,
)
from .ephemeris.coordinates import (
    spherical_to_rectangular,
    ecliptic_to_equatorial,
    rectangular_to_spherical,
    true_obliquity,
)


# ========== Utility Functions ==========

def dd_to_dms(deg: float) -> np.ndarray:
    """
    Convert decimal degrees to degrees, minutes, seconds.

    Parameters
    ----------
    deg : float
        Decimal degrees (any value, positive or negative).

    Returns
    -------
    numpy.ndarray
        Array of [degrees, minutes, seconds] as integers (int32).

    Examples
    --------
    >>> from ketu.calculations import dd_to_dms
    >>> dd_to_dms(45.5)
    array([45, 30,  0], dtype=int32)
    >>> dd_to_dms(123.456)
    array([123,  27,  21], dtype=int32)
    """
    mins, secs = divmod(deg * 3600, 60)
    degs, mins = divmod(mins, 60)
    return np.array((degs, mins, secs), dtype="i4")


# Alias for backward compatibility
decimal_degrees_to_dms = dd_to_dms


def distance(pos1: Union[float, np.ndarray], pos2: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate angular distance between two positions (vectorized).

    Works with scalars or arrays via NumPy broadcasting.
    Always returns the shortest angular distance (0-180 degrees).

    Parameters
    ----------
    pos1 : float or numpy.ndarray
        First position in degrees (scalar or array).
    pos2 : float or numpy.ndarray
        Second position in degrees (scalar or array).

    Returns
    -------
    float or numpy.ndarray
        Shortest angular distance in degrees (scalar or array).

    Notes
    -----
    Precision: ±1e-6° (0.0036 arcseconds) for angular separation.

    Examples
    --------
    >>> from ketu.calculations import distance
    >>> float(distance(10, 50))
    40.0
    >>> float(distance(350, 10))  # Wraps correctly at 0/360 boundary
    20.0
    >>> distance(np.array([0., 90., 180.]), 45.)
    array([ 45.,  45., 135.])
    """
    angle = np.abs(pos2 - pos1)
    return np.where(angle <= 180, angle, 360 - angle)  # type: ignore[return-value]


# ========== Body Position Functions ==========

@lru_cache(maxsize=1024)
def body_properties(jdate: float, body: int) -> np.ndarray:
    """
    Cached wrapper for body_properties to maintain API compatibility.

    Uses LRU cache (maxsize=1024) for optimal performance with repeated calculations.
    Benchmark shows 6.7x speedup vs no cache, and better performance than unbounded cache.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12): 0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars,
        5=Jupiter, 6=Saturn, 7=Uranus, 8=Neptune, 9=Pluto,
        10=Rahu, 11=Ketu, 12=Lilith.

    Returns
    -------
    numpy.ndarray
        Array of [longitude, latitude, distance, lon_speed, lat_speed, dist_speed]:

        - longitude: degrees (0-360).
        - latitude: degrees.
        - distance: AU (or 0 for calculated points like Rahu/Lilith).
        - lon_speed: degrees/day.
        - lat_speed: degrees/day.
        - dist_speed: AU/day.

    Notes
    -----
    Precision: ±0.1° for inner planets, ±0.5° for outer planets, ±0.01° for Moon.

    Examples
    --------
    >>> from ketu.calculations import body_properties, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> props = body_properties(jd, 0)  # Sun
    >>> lon, lat, dist, lon_v, lat_v, dist_v = props
    >>> print(f"Sun longitude: {lon:.2f}°")
    Sun longitude: 295.59°
    """
    return _body_properties_uncached(jdate, body)


def body_name(body: int) -> str:
    """
    Get the name of an astronomical body.

    Parameters
    ----------
    body : int
        Body ID (0-12).

    Returns
    -------
    str
        Body name (e.g., 'Sun', 'Moon', 'Mars', 'Rahu', 'Lilith').

    Examples
    --------
    >>> from ketu.calculations import body_name
    >>> body_name(0)
    'Sun'
    >>> body_name(1)
    'Moon'
    >>> body_name(10)
    'Rahu'
    """
    return get_planet_name(body)


def body_id(b_name: str) -> int:
    """
    Get the ID of an astronomical body by name.

    Parameters
    ----------
    b_name : str
        Body name (e.g., "Sun", "Moon", "Mars").

    Returns
    -------
    int
        Body ID (0-12).

    Raises
    ------
    IndexError
        If body name is not found.

    Examples
    --------
    >>> from ketu.calculations import body_id
    >>> int(body_id("Sun"))
    0
    >>> int(body_id("Jupiter"))
    5
    >>> int(body_id("Rahu"))
    10
    """
    return bodies["id"][np.where(bodies["name"] == b_name.encode())][0]


def long(jdate: float, body: int) -> float:
    """
    Get ecliptic longitude of a body.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Ecliptic longitude in degrees (0-360).

    Notes
    -----
    Precision: ±0.1° for inner planets (Mercury, Venus, Mars),
    ±0.5° for outer planets (Jupiter-Pluto), ±0.01° for Moon.

    Examples
    --------
    >>> from ketu.calculations import long, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> sun_lon = long(jd, 0)
    >>> print(f"Sun: {sun_lon:.2f}°")
    Sun: 295.59°
    """
    return body_properties(jdate, body)[0]


def lat(jdate: float, body: int) -> float:
    """
    Get ecliptic latitude of a body.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Ecliptic latitude in degrees.

    Examples
    --------
    >>> from ketu.calculations import lat, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> moon_lat = lat(jd, 1)
    >>> print(f"Moon latitude: {moon_lat:.2f}°")
    Moon latitude: 3.56°
    """
    return body_properties(jdate, body)[1]


def dist_au(jdate: float, body: int) -> float:
    """
    Get distance of a body from Earth.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Distance in Astronomical Units (AU). Returns 0 for calculated
        points (Rahu, Ketu, Lilith) which have no physical distance.

    Examples
    --------
    >>> from ketu.calculations import dist_au, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> sun_dist = dist_au(jd, 0)
    >>> print(f"Sun distance: {sun_dist:.6f} AU")
    Sun distance: 0.983667 AU
    """
    return body_properties(jdate, body)[2]


def long_velocity(jdate: float, body: int) -> float:
    """
    Get longitude velocity of a body.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Longitude speed in degrees/day. Negative values indicate
        retrograde motion.

    Examples
    --------
    >>> from ketu.calculations import long_velocity, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> sun_vel = long_velocity(jd, 0)
    >>> print(f"Sun velocity: {sun_vel:.3f}°/day")
    Sun velocity: 1.019°/day
    """
    return body_properties(jdate, body)[3]


def lat_velocity(jdate: float, body: int) -> float:
    """
    Get latitude velocity of a body.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Latitude speed in degrees/day.

    Examples
    --------
    >>> from ketu.calculations import lat_velocity, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> moon_lat_vel = lat_velocity(jd, 1)
    >>> print(f"Moon lat velocity: {moon_lat_vel:.3f}°/day")
    Moon lat velocity: -0.804°/day
    """
    return body_properties(jdate, body)[4]


def dist_velocity_au(jdate: float, body: int) -> float:
    """
    Get distance velocity of a body.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    float
        Distance speed in AU/day.

    Examples
    --------
    >>> from ketu.calculations import dist_velocity_au, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> sun_dist_vel = dist_velocity_au(jd, 0)
    >>> print(f"Sun dist velocity: {sun_dist_vel:.6f} AU/day")
    Sun dist velocity: 0.000061 AU/day
    """
    return body_properties(jdate, body)[5]


def is_retrograde(jdate: float, body: int) -> bool:
    """
    Check if a body is in retrograde motion.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    bool
        True if retrograde (negative longitude velocity), False otherwise.

    Examples
    --------
    >>> from ketu.calculations import is_retrograde, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 3, 15, 12, 0, tzinfo=timezone.utc))
    >>> mercury_retro = is_retrograde(jd, 2)  # Check Mercury
    >>> print(f"Mercury retrograde: {mercury_retro}")
    Mercury retrograde: True
    """
    return bool(long_velocity(jdate, body) < 0)


def is_ascending(jdate: float, body: int) -> bool:
    """
    Check if a body's latitude is rising.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-12).

    Returns
    -------
    bool
        True if latitude is increasing (positive latitude velocity), False otherwise.

    Examples
    --------
    >>> from ketu.calculations import is_ascending, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> moon_ascending = is_ascending(jd, 1)
    >>> print(f"Moon ascending: {moon_ascending}")
    Moon ascending: False
    """
    return bool(lat_velocity(jdate, body) > 0)


def declination(jdate: Union[float, np.ndarray], body: int) -> Union[float, np.ndarray]:
    """
    Get equatorial declination (δ) of a body.

    Computed via the ecliptic-to-equatorial coordinate chain:
    ``spherical_to_rectangular(λ, β, 1) → ecliptic_to_equatorial(ε) →
    rectangular_to_spherical``, taking element [1] (equatorial latitude = δ).
    This is numerically equivalent to Meeus eq. 13.4 to machine precision.

    Scalar input uses the cached ``long``/``lat`` functions. Array input is
    vectorized loop-free via ``calc_planet_position_batch``.

    Parameters
    ----------
    jdate : float or numpy.ndarray
        Julian Date (Terrestrial Time). Scalar or 1-D array.
    body : int
        Body ID (0-13): 0=Sun, 1=Moon, 2=Mercury, …, 13=Chiron.

    Returns
    -------
    float or numpy.ndarray
        Declination in degrees (north positive, south negative). Range [−90, +90].
        Same type/shape as *jdate*.

    Examples
    --------
    >>> from ketu.calculations import declination, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> print(f"Moon declination: {declination(jd, 1):.4f}°")
    Moon declination: 19.8956°
    """
    if np.ndim(jdate) == 0:
        # Scalar path — use cached long/lat for consistency with the module
        lam = long(float(jdate), body)
        bet = lat(float(jdate), body)
        x, y, z = spherical_to_rectangular(lam, bet, 1.0)
        eps = true_obliquity(float(jdate))
        xe, ye, ze = ecliptic_to_equatorial(x, y, z, eps)
        _, decl, _ = rectangular_to_spherical(xe, ye, ze)
        return decl
    else:
        # Array path — loop-free via batch calculator
        jdate = np.asarray(jdate, dtype=float)
        batch = calc_planet_position_batch(jdate, body)
        lam = batch[:, 0]
        bet = batch[:, 1]
        x, y, z = spherical_to_rectangular(lam, bet, 1.0)
        eps = true_obliquity(jdate)
        xe, ye, ze = ecliptic_to_equatorial(x, y, z, eps)
        _, decl, _ = rectangular_to_spherical(xe, ye, ze)
        return decl


#: Standstill threshold for equatorial declination velocity (deg/day).
#:
#: ``|dδ/dt| ≤ DECL_STANDSTILL_EPS`` classifies a body as at a declination
#: standstill (δ turning point — "montant" status undefined). Determined
#: empirically against the live ketu 1.7.0 ephemeris:
#:
#: - Sun at exact solstice:       ~0.000020 deg/day → correctly neutral
#: - Moon at exact δ-standstill:  ~0.000041 deg/day → correctly neutral
#: - Jupiter typical in motion:    0.005    deg/day → correctly ascending/descending
#: - Jupiter at own δ-node:       ~0.000081 deg/day → correctly neutral
#: - Uranus typical in motion:     0.003    deg/day → correctly ascending/descending
#:
#: Value 0.001 deg/day is well above the FD truncation floor (~0.000002 deg/day
#: for outer planets) and below any real in-motion reading for all 14 bodies.
DECL_STANDSTILL_EPS: float = 0.001


def declination_velocity(jdate: float, body: int) -> float:
    """
    Get rate of change of equatorial declination (dδ/dt) for a body.

    Computed via forward finite difference with step 0.01 day, mirroring
    the package-wide FD idiom used for latitude velocity. No wraparound
    correction is applied — δ is bounded in [−90, +90] and varies
    monotonically through zero.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-13): 0=Sun, 1=Moon, 2=Mercury, …, 13=Chiron.

    Returns
    -------
    float
        Declination speed in degrees/day. Positive = northward, negative = southward.

    Examples
    --------
    >>> from ketu.calculations import declination_velocity, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> print(f"Moon decl velocity: {declination_velocity(jd, 1):.4f}°/day")
    Moon decl velocity: -4.6051°/day
    """
    return (declination(jdate + 0.01, body) - declination(jdate, body)) / 0.01


def is_ascending_declination(jdate: float, body: int) -> bool:
    """
    Check if a body's equatorial declination is rising (northward).

    True when dδ/dt > 0 (montante). This is a distinct physical quantity
    from the ecliptic-latitude-based ``is_ascending`` (β-rise) — the two
    can disagree for the same body on the same date.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-13): 0=Sun, 1=Moon, 2=Mercury, …, 13=Chiron.

    Returns
    -------
    bool
        True if declination is increasing (moving northward), False otherwise.

    Examples
    --------
    >>> from ketu.calculations import is_ascending_declination, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> print(f"Moon declination ascending: {is_ascending_declination(jd, 1)}")
    Moon declination ascending: False
    """
    return bool(declination_velocity(jdate, body) > 0)


def is_out_of_bounds(jdate: float, body: int) -> bool:
    """
    Check if a body's declination exceeds the instantaneous obliquity (OOB).

    Out-of-bounds occurs when |δ| > ε(jd), where ε is the true (instantaneous)
    obliquity of the ecliptic. The Moon can exceed this during major lunar
    standstill periods (e.g. around 2025, with |δ| up to ~28.7°).

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    body : int
        Body ID (0-13): 0=Sun, 1=Moon, 2=Mercury, …, 13=Chiron.

    Returns
    -------
    bool
        True if |δ| > true_obliquity(jdate), False otherwise.

    Examples
    --------
    >>> from ketu.calculations import is_out_of_bounds, utc_to_julian
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> print(f"Moon out of bounds: {is_out_of_bounds(jd, 1)}")
    Moon out of bounds: False
    """
    return bool(abs(declination(jdate, body)) > true_obliquity(jdate))


def body_sign(b_long: float) -> Tuple[int, int, int, int]:
    """
    Convert longitude to zodiac sign position.

    Parameters
    ----------
    b_long : float
        Ecliptic longitude in degrees (0-360).

    Returns
    -------
    tuple of int
        (sign_index, degrees, minutes, seconds) where:

        - sign_index: 0-11 (0=Aries, 1=Taurus, ..., 11=Pisces).
        - degrees: 0-29 (position within sign).
        - minutes: 0-59.
        - seconds: 0-59.

    Examples
    --------
    >>> from ketu.calculations import body_sign
    >>> tuple(int(x) for x in body_sign(45.5))  # 15° Taurus 30' 0"
    (1, 15, 30, 0)
    >>> tuple(int(x) for x in body_sign(120.0))  # 0° Leo 0' 0"
    (4, 0, 0, 0)
    >>> tuple(int(x) for x in body_sign(294.82))  # ~24° Capricorn 49' 12"
    (9, 24, 49, 12)
    """
    dms = dd_to_dms(b_long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return sign, degs, mins, secs


def positions(jdate: float, l_bodies: np.ndarray = bodies) -> np.ndarray:
    """
    Get ecliptic longitudes of all bodies.

    Parameters
    ----------
    jdate : float
        Julian Date (Terrestrial Time).
    l_bodies : numpy.ndarray, optional
        Bodies array with 'id' field (default: all 13 bodies from ketu.core).

    Returns
    -------
    numpy.ndarray
        Array of longitudes in degrees (0-360), one per body.

    Examples
    --------
    >>> from ketu.calculations import positions, utc_to_julian
    >>> from ketu.core import bodies
    >>> from datetime import datetime, timezone
    >>> jd = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))
    >>> all_positions = positions(jd)
    >>> print(f"Sun: {all_positions[0]:.2f}°")
    Sun: 295.59°
    >>> print(f"Moon: {all_positions[1]:.2f}°")
    Moon: 134.46°
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
    "long_velocity",
    "lat_velocity",
    "dist_velocity_au",
    "is_retrograde",
    "is_ascending",
    "declination",
    "DECL_STANDSTILL_EPS",
    "declination_velocity",
    "is_ascending_declination",
    "is_out_of_bounds",
    "body_sign",
    "positions",

    # Time functions (re-exported from ephemeris)
    "utc_to_julian",
    "coerce_to_jd",
    "julian_to_utc",
    "local_to_utc",
]
