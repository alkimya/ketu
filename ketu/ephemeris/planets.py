"""
High-level planetary calculation functions.

This module provides the main interface for calculating planetary positions,
replacing the pyswisseph dependency with numpy-based calculations.
"""

import numpy as np
from typing import Callable, Dict, NamedTuple, Optional
from functools import lru_cache

from .time import utc_to_julian, terrestrial_to_universal
from .orbital import (
    ORBITAL_ELEMENTS,
    _LILITH_MEAN_RATE_DEG_PER_DAY,
    get_body_position,
    get_moon_position,
    get_lunar_nodes,
    get_lilith_position,
    get_body_position_vectorized,
    get_moon_position_vectorized,
)
from .coordinates import (
    heliocentric_to_geocentric,
    ecliptic_to_equatorial,
    rectangular_to_spherical,
    spherical_to_rectangular,
    mean_obliquity,
    true_obliquity,
    aberration_correction,
)


# Map body names to indices in ORBITAL_ELEMENTS
BODY_INDICES = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    "Rahu": 10,
    "Ketu": 11,
    "Lilith": 12,
}

# Swiss Ephemeris compatible IDs
SWE_IDS = {
    0: "Sun",
    1: "Moon",
    2: "Mercury",
    3: "Venus",
    4: "Mars",
    5: "Jupiter",
    6: "Saturn",
    7: "Uranus",
    8: "Neptune",
    9: "Pluto",
    10: "Rahu",      # Mean North Node
    11: "Ketu",      # Mean South Node (opposite of Rahu)
    12: "Lilith",    # Mean Apogee (Black Moon)
}


# ---------------------------------------------------------------------------
# Per-body strategy container
# ---------------------------------------------------------------------------

class _BodyCalc(NamedTuple):
    """Per-body calculation strategy: scalar + vectorized paths."""

    scalar: Callable[[float], tuple]
    """Scalar function: (jd: float) -> (lon, lat, dist, lon_speed, lat_speed, dist_speed)
    Returns the 6-tuple BEFORE aberration correction."""

    vectorized: Callable[[np.ndarray], tuple]
    """Vectorized function: (jd_array: np.ndarray) -> (lon, lat, dist, lon_speed, lat_speed, dist_speed)
    Returns 6 np.ndarrays BEFORE aberration correction (except _make_planet_vec which applies
    aberration internally for byte-stability with the old batch path)."""


# ---------------------------------------------------------------------------
# Scalar strategy functions (one per body kind)
# ---------------------------------------------------------------------------

def _sun_scalar(jd: float) -> tuple:
    """Scalar geocentric Sun position (Earth-negation method)."""
    x_earth, y_earth, z_earth, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd)
    x_sun, y_sun, z_sun = -x_earth, -y_earth, -z_earth
    lon, lat, dist = rectangular_to_spherical(x_sun, y_sun, z_sun)

    jd_delta = 0.01
    x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd + jd_delta)
    x_sun2, y_sun2, z_sun2 = -x_earth2, -y_earth2, -z_earth2
    lon2, lat2, dist2 = rectangular_to_spherical(x_sun2, y_sun2, z_sun2)

    lon_speed = (lon2 - lon) / jd_delta
    lat_speed = (lat2 - lat) / jd_delta
    dist_speed = (dist2 - dist) / jd_delta

    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _moon_scalar(jd: float) -> tuple:
    """Scalar geocentric Moon position."""
    lon, lat, dist = get_moon_position(jd)

    jd_delta = 0.01
    lon2, lat2, dist2 = get_moon_position(jd + jd_delta)

    lon_diff = lon2 - lon
    if lon_diff > 180:
        lon_diff -= 360
    elif lon_diff < -180:
        lon_diff += 360
    lon_speed = lon_diff / jd_delta
    lat_speed = (lat2 - lat) / jd_delta
    dist_speed = (dist2 - dist) / jd_delta

    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _rahu_scalar(jd: float) -> tuple:
    """Scalar geocentric Rahu (Mean North Node) position."""
    mean_node, _ = get_lunar_nodes(jd)
    lon = mean_node
    lat = 0.0
    dist = 0.0
    lon_speed = -0.0529538083
    lat_speed = 0.0
    dist_speed = 0.0
    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _ketu_scalar(jd: float) -> tuple:
    """Scalar geocentric Ketu (Mean South Node) position."""
    mean_node, _ = get_lunar_nodes(jd)
    lon = (mean_node + 180.0) % 360.0
    lat = 0.0
    dist = 0.0
    lon_speed = -0.0529538083
    lat_speed = 0.0
    dist_speed = 0.0
    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _lilith_scalar(jd: float) -> tuple:
    """Scalar geocentric Lilith (Mean Apogee) position."""
    lon = get_lilith_position(jd)
    lat = 0.0
    dist = 0.0
    lon_speed = _LILITH_MEAN_RATE_DEG_PER_DAY
    lat_speed = 0.0
    dist_speed = 0.0
    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _make_planet_scalar(body_idx: int) -> Callable:
    """Factory returning a scalar strategy for a regular (heliocentric) planet.

    Uses closure over *body_idx* (factory parameter, not a loop variable) to
    ensure each returned function captures its own distinct index.
    """
    def _scalar(jd: float, _bidx: int = body_idx) -> tuple:
        x_earth, y_earth, z_earth, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd)
        x_planet, y_planet, z_planet, _, _, _ = get_body_position(_bidx, jd)
        x_geo, y_geo, z_geo = heliocentric_to_geocentric(
            x_planet, y_planet, z_planet, x_earth, y_earth, z_earth
        )
        lon, lat, dist = rectangular_to_spherical(x_geo, y_geo, z_geo)

        jd_delta = 0.01
        x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd + jd_delta)
        x_planet2, y_planet2, z_planet2, _, _, _ = get_body_position(_bidx, jd + jd_delta)
        x_geo2, y_geo2, z_geo2 = heliocentric_to_geocentric(
            x_planet2, y_planet2, z_planet2, x_earth2, y_earth2, z_earth2
        )
        lon2, lat2, dist2 = rectangular_to_spherical(x_geo2, y_geo2, z_geo2)

        lon_speed = (lon2 - lon) / jd_delta
        lat_speed = (lat2 - lat) / jd_delta
        dist_speed = (dist2 - dist) / jd_delta

        return lon, lat, dist, lon_speed, lat_speed, dist_speed

    return _scalar


# ---------------------------------------------------------------------------
# Vectorized strategy functions
# ---------------------------------------------------------------------------

def _sun_vec(jd_array: np.ndarray) -> tuple:
    """Vectorized geocentric Sun position."""
    x_earth, y_earth, z_earth, _, _, _ = get_body_position_vectorized(BODY_INDICES["Sun"], jd_array)
    x_sun, y_sun, z_sun = -x_earth, -y_earth, -z_earth
    lon, lat, dist = rectangular_to_spherical(x_sun, y_sun, z_sun)

    jd_delta = 0.01
    x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position_vectorized(
        BODY_INDICES["Sun"], jd_array + jd_delta
    )
    x_sun2, y_sun2, z_sun2 = -x_earth2, -y_earth2, -z_earth2
    lon2, lat2, dist2 = rectangular_to_spherical(x_sun2, y_sun2, z_sun2)

    lon_speed = (lon2 - lon) / jd_delta
    lat_speed = (lat2 - lat) / jd_delta
    dist_speed = (dist2 - dist) / jd_delta

    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _moon_vec(jd_array: np.ndarray) -> tuple:
    """Vectorized geocentric Moon position."""
    lon, lat, dist = get_moon_position_vectorized(jd_array)

    jd_delta = 0.01
    lon2, lat2, dist2 = get_moon_position_vectorized(jd_array + jd_delta)

    lon_diff = lon2 - lon
    lon_diff = np.where(lon_diff > 180, lon_diff - 360, lon_diff)
    lon_diff = np.where(lon_diff < -180, lon_diff + 360, lon_diff)
    lon_speed = lon_diff / jd_delta
    lat_speed = (lat2 - lat) / jd_delta
    dist_speed = (dist2 - dist) / jd_delta

    return lon, lat, dist, lon_speed, lat_speed, dist_speed


def _make_planet_vec(body_idx: int) -> Callable:
    """Factory returning a vectorized strategy for a regular (heliocentric) planet.

    Aberration is applied INSIDE this function (matching the original batch
    else-branch at lines 564-569) so the batch router stays aberration-free
    for these bodies, preserving byte-stability.
    """
    def _vec(jd_array: np.ndarray, _bidx: int = body_idx) -> tuple:
        x_earth, y_earth, z_earth, _, _, _ = get_body_position_vectorized(
            BODY_INDICES["Sun"], jd_array
        )
        x_planet, y_planet, z_planet, _, _, _ = get_body_position_vectorized(_bidx, jd_array)
        x_geo, y_geo, z_geo = heliocentric_to_geocentric(
            x_planet, y_planet, z_planet, x_earth, y_earth, z_earth
        )
        lon, lat, dist = rectangular_to_spherical(x_geo, y_geo, z_geo)

        jd_delta = 0.01
        x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position_vectorized(
            BODY_INDICES["Sun"], jd_array + jd_delta
        )
        x_planet2, y_planet2, z_planet2, _, _, _ = get_body_position_vectorized(
            _bidx, jd_array + jd_delta
        )
        x_geo2, y_geo2, z_geo2 = heliocentric_to_geocentric(
            x_planet2, y_planet2, z_planet2, x_earth2, y_earth2, z_earth2
        )
        lon2, lat2, dist2 = rectangular_to_spherical(x_geo2, y_geo2, z_geo2)

        lon_speed = (lon2 - lon) / jd_delta
        lat_speed = (lat2 - lat) / jd_delta
        dist_speed = (dist2 - dist) / jd_delta

        # Aberration is applied here for regular planets (matches old batch else-branch
        # lines 564-569: only for planet_id >= 2 which is always true for these bodies).
        n = len(jd_array)
        for i in range(n):
            dlon, dlat = aberration_correction(lon[i], lat[i], jd_array[i])
            lon[i] += dlon  # type: ignore[index]
            lat[i] += dlat  # type: ignore[index]

        return lon, lat, dist, lon_speed, lat_speed, dist_speed

    return _vec


def _scalar_loop_vec(planet_id: int) -> Callable:
    """Factory returning a vectorized function that loops over the scalar path.

    Used for per-date bodies (Rahu, Ketu, Lilith) whose batch implementation
    in the original code was already a scalar loop.  By routing through
    calc_planet_position, aberration is already applied inside (planet_id >= 2
    for Lilith; nodes/Ketu return the 6-tuple directly from their scalar fns
    without aberration since planet_id < 2 is false but the router applies it).

    This is also what FIXES the batch-Ketu bug: previously the fallback list
    ["Rahu", "NorthNode", "Lilith"] omitted "Ketu", so Ketu fell through to the
    heliocentric else-branch.  Now Ketu explicitly uses this scalar-loop path.
    """
    def _vec(jd_array: np.ndarray, _pid: int = planet_id) -> tuple:
        n = len(jd_array)
        out = np.zeros((n, 6))
        for i, jd in enumerate(jd_array):
            out[i] = calc_planet_position(float(jd), _pid)
        return (
            out[:, 0], out[:, 1], out[:, 2],
            out[:, 3], out[:, 4], out[:, 5],
        )

    return _vec


# ---------------------------------------------------------------------------
# Per-body strategy registry
# ---------------------------------------------------------------------------

BODY_STRATEGIES: dict[str, _BodyCalc] = {
    "Sun":     _BodyCalc(_sun_scalar,  _sun_vec),
    "Moon":    _BodyCalc(_moon_scalar, _moon_vec),
    "Rahu":    _BodyCalc(_rahu_scalar,  _scalar_loop_vec(10)),
    "Ketu":    _BodyCalc(_ketu_scalar,  _scalar_loop_vec(11)),
    "Lilith":  _BodyCalc(_lilith_scalar, _scalar_loop_vec(12)),
    "Mercury": _BodyCalc(_make_planet_scalar(BODY_INDICES["Mercury"]), _make_planet_vec(BODY_INDICES["Mercury"])),
    "Venus":   _BodyCalc(_make_planet_scalar(BODY_INDICES["Venus"]),   _make_planet_vec(BODY_INDICES["Venus"])),
    "Mars":    _BodyCalc(_make_planet_scalar(BODY_INDICES["Mars"]),    _make_planet_vec(BODY_INDICES["Mars"])),
    "Jupiter": _BodyCalc(_make_planet_scalar(BODY_INDICES["Jupiter"]), _make_planet_vec(BODY_INDICES["Jupiter"])),
    "Saturn":  _BodyCalc(_make_planet_scalar(BODY_INDICES["Saturn"]),  _make_planet_vec(BODY_INDICES["Saturn"])),
    "Uranus":  _BodyCalc(_make_planet_scalar(BODY_INDICES["Uranus"]),  _make_planet_vec(BODY_INDICES["Uranus"])),
    "Neptune": _BodyCalc(_make_planet_scalar(BODY_INDICES["Neptune"]), _make_planet_vec(BODY_INDICES["Neptune"])),
    "Pluto":   _BodyCalc(_make_planet_scalar(BODY_INDICES["Pluto"]),   _make_planet_vec(BODY_INDICES["Pluto"])),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=128)
def calc_planet_position(jd: float, planet_id: int, flags: int = 0) -> np.ndarray:
    """
    Calculate planet position compatible with pyswisseph interface.

    Parameters
    ----------
    jd : float
        Julian Date.
    planet_id : int
        Planet ID (0-12).
    flags : int, optional
        Calculation flags (for compatibility, not fully implemented).

    Returns
    -------
    np.ndarray
        Array of [longitude, latitude, distance, lon_speed, lat_speed, dist_speed].
    """
    planet_name = SWE_IDS.get(planet_id)
    if planet_name is None:
        raise ValueError(f"unknown planet ID: {planet_id}. Valid range: 0-12")

    lon, lat, dist, lon_speed, lat_speed, dist_speed = BODY_STRATEGIES[planet_name].scalar(jd)

    # Apply aberration correction for light-time
    if planet_id >= 2:  # Not for Sun or Moon
        dlon, dlat = aberration_correction(lon, lat, jd)
        lon += dlon
        lat += dlat

    return np.array([lon, lat, dist, lon_speed, lat_speed, dist_speed])


def get_planet_name(planet_id: int) -> str:
    """
    Get planet name from ID (Swiss Ephemeris compatible).

    Parameters
    ----------
    planet_id : int
        Planet ID (0-12).

    Returns
    -------
    str
        Planet name string.
    """
    return SWE_IDS.get(planet_id, f"Unknown({planet_id})")


def calculate_all_positions(jd: float) -> Dict[str, np.ndarray]:
    """
    Calculate positions for all bodies.

    Parameters
    ----------
    jd : float
        Julian Date.

    Returns
    -------
    dict of {str: np.ndarray}
        Dictionary mapping body names to position arrays.
    """
    positions = {}

    for planet_id in range(len(SWE_IDS)):
        try:
            pos = calc_planet_position(jd, planet_id)
            name = SWE_IDS[planet_id]
            positions[name] = pos
        except Exception as e:
            print(f"Error calculating position for {planet_id}: {e}")

    return positions


def body_properties(jd: float, body_id: int) -> np.ndarray:
    """
    Get body properties compatible with ketu interface.

    Parameters
    ----------
    jd : float
        Julian Date.
    body_id : int
        Body ID (0-12).

    Returns
    -------
    np.ndarray
        Array of [longitude, latitude, distance, lon_speed, lat_speed, dist_speed].
    """
    return calc_planet_position(jd, body_id)


def find_exact_aspect(
    jd_start: float, jd_end: float, body1_id: int, body2_id: int, aspect_angle: float, orb: float = 1.0
) -> Optional[float]:
    """
    Find exact aspect between two bodies within time range.

    Parameters
    ----------
    jd_start : float
        Start Julian Date.
    jd_end : float
        End Julian Date.
    body1_id : int
        First body ID.
    body2_id : int
        Second body ID.
    aspect_angle : float
        Aspect angle in degrees (0, 60, 90, 120, 180).
    orb : float, optional
        Orb tolerance in degrees.

    Returns
    -------
    float or None
        Julian Date of exact aspect or None if not found.
    """
    # Binary search for exact aspect
    max_iterations = 50
    tolerance = 0.001  # 0.001 days = ~1.5 minutes

    def get_angle_diff(jd):
        """
        Compute signed angular difference from target aspect angle.

        Parameters
        ----------
        jd : float
            Julian Date at which to evaluate the angular difference.

        Returns
        -------
        float
            Difference between the angular separation of body1/body2 and
            ``aspect_angle`` in degrees.
        """
        pos1 = calc_planet_position(jd, body1_id)
        pos2 = calc_planet_position(jd, body2_id)

        angle = abs(pos2[0] - pos1[0])
        if angle > 180:
            angle = 360 - angle

        return angle - aspect_angle

    # Check if aspect exists in range
    diff_start = get_angle_diff(jd_start)
    diff_end = get_angle_diff(jd_end)

    if abs(diff_start) > orb and abs(diff_end) > orb:
        return None  # No aspect in range

    if diff_start * diff_end > 0:
        return None  # Same sign, no crossing

    # Binary search
    jd_left = jd_start
    jd_right = jd_end

    for _ in range(max_iterations):
        jd_mid = (jd_left + jd_right) / 2
        diff_mid = get_angle_diff(jd_mid)

        if abs(diff_mid) < 0.01:  # Close enough
            return jd_mid

        if abs(jd_right - jd_left) < tolerance:
            return jd_mid

        if diff_mid * diff_start < 0:
            jd_right = jd_mid
        else:
            jd_left = jd_mid
            diff_start = diff_mid

    return (jd_left + jd_right) / 2


def find_all_aspects(jd_start: float, jd_end: float, body1_id: int, body2_id: int, aspects: list = []) -> list:
    """
    Find all aspects between two bodies in time range.

    Parameters
    ----------
    jd_start : float
        Start Julian Date.
    jd_end : float
        End Julian Date.
    body1_id : int
        First body ID.
    body2_id : int
        Second body ID.
    aspects : list, optional
        List of aspect angles to check (default: major aspects).

    Returns
    -------
    list of tuple
        List of tuples (jd, aspect_angle).
    """
    if aspects == []:
        aspects = [0, 30, 60, 90, 120, 150, 180]  # Major aspects

    results = []

    # Step through time looking for aspects
    step = 0.5  # Half day steps
    jd = jd_start

    while jd < jd_end:
        jd_next = min(jd + step, jd_end)

        for aspect in aspects:
            exact_jd = find_exact_aspect(jd, jd_next, body1_id, body2_id, aspect)
            if exact_jd is not None:
                results.append((exact_jd, aspect))

        jd = jd_next

    return sorted(results, key=lambda x: x[0])


def calculate_speed_ratio(jd: float, body_id: int) -> float:
    """
    Calculate speed ratio compared to average speed.

    Parameters
    ----------
    jd : float
        Julian Date.
    body_id : int
        Body ID.

    Returns
    -------
    float
        Speed ratio (1.0 = average speed).
    """
    pos = calc_planet_position(jd, body_id)
    current_speed = pos[3]  # Longitude speed

    # Average speeds for bodies (degrees per day)
    avg_speeds = {
        0: 0.985647,  # Sun
        1: 13.176389,  # Moon
        2: 1.383333,  # Mercury
        3: 1.2,  # Venus
        4: 0.524167,  # Mars
        5: 0.083056,  # Jupiter
        6: 0.033611,  # Saturn
        7: 0.011667,  # Uranus
        8: 0.006944,  # Neptune
        9: 0.004167,  # Pluto
        10: -0.052954,  # Mean Node
        11: -0.052954,  # True Node
        12: round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6),  # Lilith (matches orbital.py rate)
    }

    avg_speed = avg_speeds.get(body_id, 1.0)

    if avg_speed == 0:
        return 1.0

    return current_speed / avg_speed


def calc_planet_position_batch(jd_array: np.ndarray, planet_id: int, flags: int = 0) -> np.ndarray:
    """
    Calculate planet positions for multiple Julian Dates (vectorized/batch).

    This function is optimized for calculating time series by vectorizing
    calculations across multiple dates.

    Parameters
    ----------
    jd_array : np.ndarray
        Array of Julian Dates.
    planet_id : int
        Planet ID (0-12).
    flags : int, optional
        Calculation flags (for compatibility).

    Returns
    -------
    np.ndarray
        2D array of shape (n_dates, 6) containing
        [longitude, latitude, distance, lon_speed, lat_speed, dist_speed]
        for each Julian Date.
    """
    planet_name = SWE_IDS.get(planet_id)
    if planet_name is None:
        raise ValueError(f"unknown planet ID: {planet_id}. Valid range: 0-12")

    n_dates = len(jd_array)
    results = np.zeros((n_dates, 6))

    lon, lat, dist, lon_speed, lat_speed, dist_speed = BODY_STRATEGIES[planet_name].vectorized(jd_array)

    results[:, 0] = lon
    results[:, 1] = lat
    results[:, 2] = dist
    results[:, 3] = lon_speed
    results[:, 4] = lat_speed
    results[:, 5] = dist_speed

    return results
