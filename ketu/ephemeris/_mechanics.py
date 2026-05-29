"""
Orbital mechanics — element propagation and heliocentric position computation.

Imports data from _elements and math utilities from _kepler. Does NOT import
from orbital.py (would create a circular dependency).
"""

import numpy as np
from typing import Tuple

from ._elements import ORBITAL_ELEMENTS
from ._kepler import normalize_angle, solve_kepler_equation


def orbital_elements_at_date(body_id: int, jd: float) -> dict:
    """
    Calculate orbital elements for a body at a given Julian Date.

    Parameters
    ----------
    body_id : int
        Index of body in ORBITAL_ELEMENTS array.
    jd : float
        Julian Date.

    Returns
    -------
    dict
        Dictionary with updated orbital elements.
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Get base elements
    elem = ORBITAL_ELEMENTS[body_id]

    # Calculate elements at date
    N = normalize_angle(elem["N"] + elem["N_dot"] * d)
    i = elem["i"] + elem["i_dot"] * d
    w = normalize_angle(elem["w"] + elem["w_dot"] * d)
    a = elem["a"]  # Semi-major axis doesn't change
    e = elem["e"] + elem["e_dot"] * d
    M = normalize_angle(elem["M"] + elem["M_dot"] * d)

    return {"N": N, "i": i, "w": w, "a": a, "e": e, "M": M, "name": elem["name"]}


def compute_position(elem: dict) -> Tuple[float, float, float, float, float, float]:
    """
    Compute heliocentric position from orbital elements.

    Parameters
    ----------
    elem : dict
        Dictionary of orbital elements.

    Returns
    -------
    tuple of (float, float, float, float, float, float)
        Tuple of (x, y, z, lon, lat, r) where
        x, y, z are rectangular coordinates in AU,
        lon, lat are spherical coordinates in degrees,
        r is distance in AU.
    """
    # Convert to radians
    N_rad = np.deg2rad(elem["N"])
    i_rad = np.deg2rad(elem["i"])
    w_rad = np.deg2rad(elem["w"])
    M_rad = np.deg2rad(elem["M"])

    # Solve Kepler's equation
    E = solve_kepler_equation(M_rad, elem["e"])

    # True anomaly
    x_prime = elem["a"] * (np.cos(E) - elem["e"])
    y_prime = elem["a"] * np.sqrt(1 - elem["e"] ** 2) * np.sin(E)

    r = np.sqrt(x_prime**2 + y_prime**2)
    v = np.arctan2(y_prime, x_prime)

    # Heliocentric coordinates
    cos_N = np.cos(N_rad)
    sin_N = np.sin(N_rad)
    cos_i = np.cos(i_rad)
    sin_i = np.sin(i_rad)
    cos_vw = np.cos(v + w_rad)
    sin_vw = np.sin(v + w_rad)

    x = r * (cos_N * cos_vw - sin_N * sin_vw * cos_i)
    y = r * (sin_N * cos_vw + cos_N * sin_vw * cos_i)
    z = r * sin_vw * sin_i

    # Spherical coordinates
    lon = np.rad2deg(np.arctan2(y, x))
    lon = normalize_angle(lon)
    r_safe = max(r, 1e-10)  # floor r to avoid div/0 (QAL-11)
    lat = np.rad2deg(np.arcsin(z / r_safe))

    return x, y, z, lon, lat, r
