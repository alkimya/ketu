"""Orbital elements and calculations for planetary positions.

This module contains the orbital elements data and functions to calculate
planetary positions using Kepler's laws and perturbation theory.
"""

import numpy as np
from typing import Tuple, Union


# Orbital elements for planets (J2000.0 epoch)
# Format: name, N, i, w, a, e, M, N_dot, i_dot, w_dot, e_dot, M_dot
# Where:
#   N = longitude of ascending node (degrees)
#   i = inclination (degrees)
#   w = argument of perihelion (degrees)
#   a = semi-major axis (AU)
#   e = eccentricity
#   M = mean anomaly at epoch (degrees)
#   *_dot = rate of change per day

ORBITAL_ELEMENTS = np.array(
    [
        # Sun (Earth's orbit) - JPL J2000.0 values (L0=100.46435, w=102.94719, M0=L0-w=357.51716)
        ("Sun", 0.0, 0.0, 102.9404, 1.000000, 0.016709, 357.5172, 0.0, 0.0, 4.70935e-5, -1.151e-9, 0.9856002585),
        # Moon - Meeus values (Ω=125.04452, M'=134.9633964)
        (
            "Moon",
            125.04452,
            5.1454,
            318.0634,
            0.002569,
            0.0549,
            134.9634,
            -0.0529538083,
            0.0,
            0.1643573223,
            0.0,
            13.0649929509,
        ),
        # Planets - JPL J2000.0 with high-precision rates
        (
            "Mercury",
            48.33076593,
            7.00497902,
            29.12703035,
            0.3870992700,
            0.2056359300,
            174.79252722,
            -3.431644353183e-06,
            -1.628334017796e-07,
            7.825262149213e-06,
            5.218343600274e-10,
            4.092334391098e+00,
        ),
        (
            "Venus",
            76.67984255,
            3.39467605,
            54.92262463,
            0.7233356600,
            0.0067767200,
            50.37663232,
            -7.602852292950e-06,
            -2.159890485969e-08,
            7.676316769336e-06,
            -1.124435318275e-09,
            1.602130395729e+00,
        ),
        (
            "Mars",
            49.55953891,
            1.84969142,
            286.50069504,
            1.5237103400,
            0.0933941000,
            19.37304145,
            -8.010223956194e-06,
            -2.226231348392e-07,
            2.017753073238e-05,
            2.157973990418e-09,
            0.524020760414e+00,
        ),
        (
            "Jupiter",
            100.47390909,
            1.30439695,
            274.25457074,
            5.2028870000,
            0.0483862400,
            19.66796068,
            5.604135797399e-06,
            -5.029815195072e-08,
            2.145275838467e-07,
            -3.628473648186e-09,
            8.308100208268e-02,
        ),
        (
            "Saturn",
            113.66242448,
            2.48599187,
            338.93645383,
            9.5366759400,
            0.0538617900,
            317.35536592,
            -7.903571252567e-06,
            5.300725530459e-08,
            -3.567261327858e-06,
            -1.396057494867e-08,
            3.348152208542e-02,
        ),
        (
            "Uranus",
            74.01692503,
            0.77263783,
            96.93735127,
            19.1891646400,
            0.0472574400,
            142.28382821,
            1.161009993155e-06,
            -6.651307323751e-08,
            1.001086707734e-05,
            -1.203832991102e-09,
            1.172002669514e-02,
        ),
        (
            "Neptune",
            131.78422574,
            1.77004347,
            273.18053653,
            30.0699227600,
            0.0085904800,
            259.91526801,
            -1.392646132786e-07,
            9.684325804244e-09,
            -8.687967145791e-06,
            1.397672826831e-09,
            5.989921092129e-03,
        ),
        # Pluto - JPL J2000.0 values (L=238.92881, w_bar=224.06676, M=L-w_bar=14.86205)
        ("Pluto", 110.30347, 17.14175, 113.76329, 39.48168677, 0.24880766, 14.86205, 0.0, 0.0, 0.0, 0.0, 0.003964),
        # Lunar nodes
        ("Rahu", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0529538083),  # Mean node
        ("NorthNode", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.0529538083),  # True node
        # Lilith (Mean lunar apogee)
        ("Lilith", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1114040803),
    ],
    dtype=[
        ("name", "U12"),
        ("N", "f8"),
        ("i", "f8"),
        ("w", "f8"),
        ("a", "f8"),
        ("e", "f8"),
        ("M", "f8"),
        ("N_dot", "f8"),
        ("i_dot", "f8"),
        ("w_dot", "f8"),
        ("e_dot", "f8"),
        ("M_dot", "f8"),
    ],
)


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees range."""
    angle = angle % 360.0
    if angle < 0:
        angle += 360.0
    return angle


def solve_kepler_equation(M: float, e: float, tolerance: float = 1e-8) -> float:
    """Solve Kepler's equation for eccentric anomaly.

    Args:
        M: Mean anomaly in radians
        e: Eccentricity
        tolerance: Convergence tolerance

    Returns:
        Eccentric anomaly in radians
    """
    # Initial guess
    E = M + e * np.sin(M) * (1.0 + e * np.cos(M))

    # Newton-Raphson iteration
    for _ in range(50):  # Maximum iterations
        dE = (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        E -= dE

        if abs(dE) < tolerance:
            break

    return E


def orbital_elements_at_date(body_id: int, jd: float) -> dict:
    """Calculate orbital elements for a body at a given Julian Date.

    Args:
        body_id: Index of body in ORBITAL_ELEMENTS array
        jd: Julian Date

    Returns:
        Dictionary with updated orbital elements
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
    """Compute heliocentric position from orbital elements.

    Args:
        elem: Dictionary of orbital elements

    Returns:
        Tuple of (x, y, z, lon, lat, r) where:
        - x, y, z are rectangular coordinates in AU
        - lon, lat are spherical coordinates in degrees
        - r is distance in AU
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
    lat = np.rad2deg(np.arcsin(z / r))

    return x, y, z, lon, lat, r


def apply_perturbations(body_id: int, jd: float, x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Apply perturbation corrections to planetary positions.

    Args:
        body_id: Body index
        jd: Julian Date
        x, y, z: Unperturbed rectangular coordinates

    Returns:
        Perturbed coordinates (x, y, z)
    """
    # For now, only apply major perturbations to outer planets
    # This is a simplified version - full implementation would include
    # more terms from perturbation theory

    d = jd - 2451545.0

    if ORBITAL_ELEMENTS[body_id]["name"] == "Jupiter":
        # Saturn perturbations on Jupiter
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)

        # Longitude perturbations (in degrees)
        dL = (
            -0.332 * np.sin(2 * M_jup - 5 * M_sat - np.deg2rad(67.6))
            - 0.056 * np.sin(2 * M_jup - 2 * M_sat + np.deg2rad(21))
            + 0.042 * np.sin(3 * M_jup - 5 * M_sat + np.deg2rad(21))
            - 0.036 * np.sin(M_jup - 2 * M_sat)
            + 0.022 * np.cos(M_jup - M_sat)
            + 0.023 * np.sin(2 * M_jup - 3 * M_sat + np.deg2rad(52))
            - 0.016 * np.sin(M_jup - 5 * M_sat - np.deg2rad(69))
        )

        # Apply correction to longitude
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / r)

        lon += np.deg2rad(dL)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    elif ORBITAL_ELEMENTS[body_id]["name"] == "Saturn":
        # Jupiter perturbations on Saturn
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)

        # Longitude perturbations
        dL = (
            0.812 * np.sin(2 * M_jup - 5 * M_sat - np.deg2rad(67.6))
            - 0.229 * np.cos(2 * M_jup - 4 * M_sat - np.deg2rad(2))
            + 0.119 * np.sin(M_jup - 2 * M_sat - np.deg2rad(3))
            + 0.046 * np.sin(2 * M_jup - 6 * M_sat - np.deg2rad(69))
            + 0.014 * np.sin(M_jup - 3 * M_sat + np.deg2rad(32))
        )

        # Latitude perturbations
        dB = -0.020 * np.cos(2 * M_jup - 4 * M_sat - np.deg2rad(2)) + 0.018 * np.sin(
            2 * M_jup - 6 * M_sat - np.deg2rad(49)
        )

        # Apply corrections
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / r)

        lon += np.deg2rad(dL)
        lat += np.deg2rad(dB)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    elif ORBITAL_ELEMENTS[body_id]["name"] == "Uranus":
        # Jupiter and Saturn perturbations on Uranus
        M_jup = np.deg2rad(19.8950 + 0.0830853001 * d)
        M_sat = np.deg2rad(316.9670 + 0.0334442282 * d)
        M_ura = np.deg2rad(142.5905 + 0.011725806 * d)

        # Longitude perturbations
        dL = (
            0.040 * np.sin(M_sat - 2 * M_ura + np.deg2rad(6))
            + 0.035 * np.sin(M_sat - 3 * M_ura + np.deg2rad(33))
            - 0.015 * np.sin(M_jup - M_ura + np.deg2rad(20))
        )

        # Apply correction
        r = np.sqrt(x**2 + y**2 + z**2)
        lon = np.arctan2(y, x)
        lat = np.arcsin(z / r)

        lon += np.deg2rad(dL)

        # Convert back to rectangular
        x = r * np.cos(lon) * np.cos(lat)
        y = r * np.sin(lon) * np.cos(lat)
        z = r * np.sin(lat)

    return x, y, z


def get_body_position(body_id: int, jd: float) -> Tuple[float, float, float, float, float, float]:
    """Get heliocentric position of a body at given Julian Date.

    Args:
        body_id: Index of body in ORBITAL_ELEMENTS
        jd: Julian Date

    Returns:
        Tuple of (x, y, z, lon, lat, r) in AU and degrees
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
        lat = np.rad2deg(np.arcsin(z / r))

    return x, y, z, lon, lat, r


def get_moon_position(jd: float) -> Tuple[float, float, float]:
    """Calculate geocentric position of the Moon.

    Args:
        jd: Julian Date

    Returns:
        Tuple of (lon, lat, dist) where:
        - lon: Geocentric longitude in degrees
        - lat: Geocentric latitude in degrees
        - dist: Distance from Earth in Earth radii
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
    lat = np.rad2deg(np.arcsin(zeclip / r))

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
    """Calculate positions of lunar nodes.

    Args:
        jd: Julian Date

    Returns:
        Tuple of (mean_node, true_node) in degrees
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
    """Calculate position of Black Moon Lilith (mean lunar apogee).

    Args:
        jd: Julian Date

    Returns:
        Longitude in degrees
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Mean longitude of lunar apogee
    lilith = normalize_angle(83.3532 + 0.1114040803 * d)

    return lilith
