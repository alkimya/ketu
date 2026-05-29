"""
Body position getters — scalar and vectorized.

Provides:
    get_body_position, get_moon_position, get_lunar_nodes,
    get_lilith_position, get_body_position_vectorized,
    get_moon_position_vectorized

All function bodies are lifted verbatim from orbital.py. Imports resolve
exclusively to the leaf modules (_elements, _kepler, _mechanics,
_perturbations) — nothing is imported from orbital.py to avoid circular
dependencies.
"""

import numpy as np
from typing import Tuple

from ._elements import (
    ORBITAL_ELEMENTS,
    _LILITH_MEAN_EPOCH_DEG,
    _LILITH_MEAN_RATE_DEG_PER_DAY,
    _LILITH_PERTURB_AMP_DEG,
    _LILITH_PERTURB_RATE_DEG_PER_DAY,
    _LILITH_PERTURB_PHASE_DEG,
)
from ._kepler import normalize_angle, solve_kepler_equation
from ._mechanics import orbital_elements_at_date, compute_position
from ._perturbations import apply_perturbations


def get_body_position(body_id: int, jd: float) -> Tuple[float, float, float, float, float, float]:
    """
    Get heliocentric position of a body at given Julian Date.

    Parameters
    ----------
    body_id : int
        Index of body in ORBITAL_ELEMENTS.
    jd : float
        Julian Date.

    Returns
    -------
    tuple of (float, float, float, float, float, float)
        Tuple of (x, y, z, lon, lat, r) in AU and degrees.
    """
    # Get orbital elements at date
    elem = orbital_elements_at_date(body_id, jd)

    # Compute basic position
    x, y, z, lon, lat, r = compute_position(elem)

    # Apply perturbations for major planets
    if body_id in [4, 5, 6, 7]:  # Jupiter through Neptune
        x, y, z = apply_perturbations(body_id, jd, x, y, z)
        # Recalculate spherical coordinates
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.rad2deg(np.arctan2(y, x))
        lon = normalize_angle(lon)
        r_safe = max(r, 1e-10)  # floor r to avoid div/0 (QAL-11)
        lat = np.rad2deg(np.arcsin(z / r_safe))

    return x, y, z, lon, lat, r


def get_moon_position(jd: float) -> Tuple[float, float, float]:
    """
    Calculate geocentric position of the Moon.

    Parameters
    ----------
    jd : float
        Julian Date.

    Returns
    -------
    tuple of (float, float, float)
        Tuple of (lon, lat, dist) where
        lon is geocentric longitude in degrees,
        lat is geocentric latitude in degrees,
        dist is distance from Earth in AU.
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Moon's mean elements (Meeus values)
    N = normalize_angle(125.04452 - 0.0529538083 * d)  # Long. ascending node (Ω)
    i = 5.1454  # Inclination
    w = normalize_angle(318.0634 + 0.1643573223 * d)  # Arg. of perigee
    a = 60.2666  # Mean distance (Earth radii)
    e = 0.054900  # Eccentricity
    M = normalize_angle(134.9634 + 13.0649929509 * d)  # Mean anomaly (M')

    # Convert to radians
    N_rad = np.deg2rad(N)
    w_rad = np.deg2rad(w)
    M_rad = np.deg2rad(M)

    # Solve Kepler's equation
    E = solve_kepler_equation(M_rad, e)

    # True anomaly and distance
    x_prime = a * (np.cos(E) - e)
    y_prime = a * np.sqrt(1 - e**2) * np.sin(E)

    r = np.sqrt(x_prime**2 + y_prime**2)
    v = np.arctan2(y_prime, x_prime)

    # Moon's position in space
    xeclip = r * (np.cos(N_rad) * np.cos(v + w_rad) - np.sin(N_rad) * np.sin(v + w_rad) * np.cos(np.deg2rad(i)))
    yeclip = r * (np.sin(N_rad) * np.cos(v + w_rad) + np.cos(N_rad) * np.sin(v + w_rad) * np.cos(np.deg2rad(i)))
    zeclip = r * np.sin(v + w_rad) * np.sin(np.deg2rad(i))

    # Convert to spherical coordinates
    lon = np.rad2deg(np.arctan2(yeclip, xeclip))
    r_safe = max(r, 1e-10)  # floor r to avoid div/0 (QAL-11)
    lat = np.rad2deg(np.arcsin(zeclip / r_safe))

    # Add perturbations
    # Longitude
    Ms = np.deg2rad(normalize_angle(357.5172 + 0.9856002585 * d))  # Sun's mean anomaly (corrected)
    Mm = M_rad  # Moon's mean anomaly
    D = np.deg2rad(normalize_angle(lon - (100.46 + 0.9856474 * d)))  # Moon's elongation
    F = np.deg2rad(normalize_angle(lon - N))  # Argument of latitude

    # Main perturbations in longitude
    dlon = (
        -1.274 * np.sin(Mm - 2 * D)  # Evection
        + 0.658 * np.sin(2 * D)  # Variation
        - 0.186 * np.sin(Mm)  # Yearly equation
        - 0.059 * np.sin(2 * Mm - 2 * D)
        - 0.057 * np.sin(Mm - 2 * D + Ms)
        + 0.053 * np.sin(Mm + 2 * D)
        + 0.046 * np.sin(2 * D - Ms)
        + 0.041 * np.sin(Mm - Ms)
        - 0.035 * np.sin(D)  # Parallactic equation
        - 0.031 * np.sin(Mm + Ms)
        - 0.015 * np.sin(2 * F - 2 * D)
        + 0.011 * np.sin(Mm - 4 * D)
    )

    # Main perturbations in latitude
    dlat = (
        -0.173 * np.sin(F - 2 * D)
        - 0.055 * np.sin(Mm - F - 2 * D)
        - 0.046 * np.sin(Mm + F - 2 * D)
        + 0.033 * np.sin(F + 2 * D)
        + 0.017 * np.sin(2 * Mm + F)
    )

    # Main perturbation in distance
    dr = -0.58 * np.cos(Mm - 2 * D) - 0.46 * np.cos(2 * D)

    lon = normalize_angle(lon + dlon)
    lat = lat + dlat
    dist = r + dr

    # Convert distance to AU (1 Earth radius = 4.26352e-5 AU)
    dist_au = dist * 4.26352e-5

    return lon, lat, dist_au


def get_lunar_nodes(jd: float) -> Tuple[float, float]:
    """
    Calculate positions of lunar nodes.

    Parameters
    ----------
    jd : float
        Julian Date.

    Returns
    -------
    tuple of (float, float)
        Tuple of (mean_node, true_node) in degrees.
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Mean node (Rahu)
    mean_node = normalize_angle(125.1228 - 0.0529538083 * d)

    # True node corrections
    # Moon's mean anomaly
    M = np.deg2rad(normalize_angle(115.3654 + 13.0649929509 * d))
    # Sun's mean anomaly
    Ms = np.deg2rad(normalize_angle(356.0470 + 0.9856002585 * d))

    # Nutation in longitude
    nutlon = -0.0048 * np.sin(2 * np.deg2rad(mean_node)) - 0.0024 * np.sin(2 * M) - 0.0017 * np.sin(Ms)

    true_node = normalize_angle(mean_node + np.rad2deg(nutlon))

    return mean_node, true_node


def get_lilith_position(jd: float) -> float:
    """
    Calculate position of Black Moon Lilith (mean lunar apogee).

    Returns the geocentric ecliptic longitude (mean ecliptic of date,
    tropical, mean motion) of the Moon's Mean Apogee, in degrees in
    [0, 360). This corresponds exactly to Swiss Ephemeris's
    ``SE_MEAN_APOG`` (body index 12) within 0.01 deg over 1900-2050.

    The formula is a linear secular term plus a single sinusoidal
    perturbation, with constants fitted in v1.1 (Phase 8) by joint
    nonlinear least squares against ``swe.calc_ut(jd, swe.MEAN_APOG)``
    over 1900-2050 (daily sampling, 55K points). Empirical max |delta|
    versus ``swe.MEAN_APOG`` is 0.0078 deg over the dense window and
    0.0027 deg on the five Plan 03 cross-check dates -- well below the
    0.01 deg tolerance documented in ``docs/LILITH_DEFINITION.md``
    Section 7.

    Parameters
    ----------
    jd : float
        Julian Date in UT (matches ``swe.calc_ut`` convention).

    Returns
    -------
    float
        Longitude in degrees in [0, 360).

    Notes
    -----
    Reference documents:

    - ``docs/LILITH_DEFINITION.md`` — Frame, formula, tolerance, history.
    - ``tests/test_lilith_cross_check.py`` — Regression harness vs. Swiss
      Ephemeris ``SE_MEAN_APOG``.
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Mean longitude of lunar apogee = secular linear term + dominant
    # 1095-day perturbation (~0.116 deg amplitude, period ~3 sidereal
    # years). Constants are module-level singletons; see header.
    lilith = normalize_angle(
        _LILITH_MEAN_EPOCH_DEG
        + _LILITH_MEAN_RATE_DEG_PER_DAY * d
        + _LILITH_PERTURB_AMP_DEG
        * np.sin(np.deg2rad(_LILITH_PERTURB_RATE_DEG_PER_DAY * d + _LILITH_PERTURB_PHASE_DEG))
    )

    return float(lilith)


def get_body_position_vectorized(body_id: int, jd_array: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Get heliocentric position of a body for multiple Julian Dates (vectorized).

    This function efficiently computes positions for time series by vectorizing
    the orbital calculations across multiple dates.

    Parameters
    ----------
    body_id : int
        Index of body in ORBITAL_ELEMENTS.
    jd_array : np.ndarray
        Array of Julian Dates.

    Returns
    -------
    tuple of (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)
        Tuple of arrays (x, y, z, lon, lat, r) in AU and degrees.
    """
    # Days since J2000.0 (vectorized)
    d = jd_array - 2451545.0

    # Get base elements
    elem = ORBITAL_ELEMENTS[body_id]

    # Calculate elements at dates (vectorized)
    N = (elem["N"] + elem["N_dot"] * d) % 360.0
    i = elem["i"] + elem["i_dot"] * d
    w = (elem["w"] + elem["w_dot"] * d) % 360.0
    a = elem["a"]
    e = elem["e"] + elem["e_dot"] * d
    M = (elem["M"] + elem["M_dot"] * d) % 360.0

    # Convert to radians (vectorized)
    N_rad = np.deg2rad(N)
    i_rad = np.deg2rad(i)
    w_rad = np.deg2rad(w)
    M_rad = np.deg2rad(M)

    # Solve Kepler's equation (vectorized)
    E = solve_kepler_equation(M_rad, e)

    # True anomaly (vectorized)
    x_prime = a * (np.cos(E) - e)
    y_prime = a * np.sqrt(1 - e**2) * np.sin(E)

    r = np.sqrt(x_prime**2 + y_prime**2)
    v = np.arctan2(y_prime, x_prime)

    # Heliocentric coordinates (vectorized)
    cos_N = np.cos(N_rad)
    sin_N = np.sin(N_rad)
    cos_i = np.cos(i_rad)
    sin_i = np.sin(i_rad)
    cos_vw = np.cos(v + w_rad)
    sin_vw = np.sin(v + w_rad)

    x = r * (cos_N * cos_vw - sin_N * sin_vw * cos_i)
    y = r * (sin_N * cos_vw + cos_N * sin_vw * cos_i)
    z = r * sin_vw * sin_i

    # Spherical coordinates (vectorized)
    lon = np.rad2deg(np.arctan2(y, x))
    lon = lon % 360.0
    lat = np.rad2deg(np.arcsin(z / np.maximum(r, 1e-10)))  # floor r to avoid div/0 (QAL-11)

    return x, y, z, lon, lat, r


def get_moon_position_vectorized(jd_array: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate geocentric position of the Moon for multiple dates (vectorized).

    Parameters
    ----------
    jd_array : np.ndarray
        Array of Julian Dates.

    Returns
    -------
    tuple of (np.ndarray, np.ndarray, np.ndarray)
        Tuple of arrays (lon, lat, dist) where
        lon is geocentric longitude in degrees,
        lat is geocentric latitude in degrees,
        dist is distance from Earth in AU.
    """
    # Days since J2000.0 (vectorized)
    d = jd_array - 2451545.0

    # Moon's mean elements (vectorized)
    N = (125.04452 - 0.0529538083 * d) % 360.0
    i = 5.1454
    w = (318.0634 + 0.1643573223 * d) % 360.0
    a = 60.2666
    e = 0.054900
    M = (134.9634 + 13.0649929509 * d) % 360.0

    # Convert to radians
    N_rad = np.deg2rad(N)
    w_rad = np.deg2rad(w)
    M_rad = np.deg2rad(M)

    # Solve Kepler's equation (vectorized)
    E = solve_kepler_equation(M_rad, e)

    # True anomaly and distance (vectorized)
    x_prime = a * (np.cos(E) - e)
    y_prime = a * np.sqrt(1 - e**2) * np.sin(E)

    r = np.sqrt(x_prime**2 + y_prime**2)
    v = np.arctan2(y_prime, x_prime)

    # Moon's position in space (vectorized)
    cos_i = np.cos(np.deg2rad(i))
    sin_i = np.sin(np.deg2rad(i))

    xeclip = r * (np.cos(N_rad) * np.cos(v + w_rad) - np.sin(N_rad) * np.sin(v + w_rad) * cos_i)
    yeclip = r * (np.sin(N_rad) * np.cos(v + w_rad) + np.cos(N_rad) * np.sin(v + w_rad) * cos_i)
    zeclip = r * np.sin(v + w_rad) * sin_i

    # Convert to spherical coordinates (vectorized)
    lon = np.rad2deg(np.arctan2(yeclip, xeclip))
    lat = np.rad2deg(np.arcsin(zeclip / np.maximum(r, 1e-10)))  # floor r to avoid div/0 (QAL-11)

    # Add perturbations (vectorized)
    Ms = np.deg2rad((357.5172 + 0.9856002585 * d) % 360.0)
    Mm = M_rad
    D = np.deg2rad((lon - (100.46 + 0.9856474 * d)) % 360.0)
    F = np.deg2rad((lon - N) % 360.0)

    # Main perturbations in longitude (vectorized)
    dlon = (
        -1.274 * np.sin(Mm - 2 * D)
        + 0.658 * np.sin(2 * D)
        - 0.186 * np.sin(Mm)
        - 0.059 * np.sin(2 * Mm - 2 * D)
        - 0.057 * np.sin(Mm - 2 * D + Ms)
        + 0.053 * np.sin(Mm + 2 * D)
        + 0.046 * np.sin(2 * D - Ms)
        + 0.041 * np.sin(Mm - Ms)
        - 0.035 * np.sin(D)
        - 0.031 * np.sin(Mm + Ms)
        - 0.015 * np.sin(2 * F - 2 * D)
        + 0.011 * np.sin(Mm - 4 * D)
    )

    # Main perturbations in latitude (vectorized)
    dlat = (
        -0.173 * np.sin(F - 2 * D)
        - 0.055 * np.sin(Mm - F - 2 * D)
        - 0.046 * np.sin(Mm + F - 2 * D)
        + 0.033 * np.sin(F + 2 * D)
        + 0.017 * np.sin(2 * Mm + F)
    )

    # Main perturbation in distance (vectorized)
    dr = -0.58 * np.cos(Mm - 2 * D) - 0.46 * np.cos(2 * D)

    lon = (lon + dlon) % 360.0
    lat = lat + dlat
    dist = r + dr

    # Convert distance to AU
    dist_au = dist * 4.26352e-5

    return lon, lat, dist_au
