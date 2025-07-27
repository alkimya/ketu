"""High-level planetary calculation functions.

This module provides the main interface for calculating planetary positions,
replacing the pyswisseph dependency with numpy-based calculations.
"""

import numpy as np
from typing import Tuple, Dict, Optional
from functools import lru_cache

from .time import utc_to_julian, terrestrial_to_universal
from .orbital import ORBITAL_ELEMENTS, get_body_position, get_moon_position, get_lunar_nodes, get_lilith_position
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
    "NorthNode": 11,
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
    10: "Rahu",
    11: "NorthNode",
    12: "Lilith",
}


@lru_cache(maxsize=128)
def calc_planet_position(jd: float, planet_id: int, flags: int = 0) -> np.ndarray:
    """Calculate planet position compatible with pyswisseph interface.

    Args:
        jd: Julian Date
        planet_id: Planet ID (0-12)
        flags: Calculation flags (for compatibility, not fully implemented)

    Returns:
        Array of [longitude, latitude, distance, lon_speed, lat_speed, dist_speed]
    """
    planet_name = SWE_IDS.get(planet_id)
    if planet_name is None:
        raise ValueError(f"Unknown planet ID: {planet_id}")

    # Special handling for different bodies
    if planet_name == "Sun":
        # Earth's heliocentric position gives us Sun's geocentric position
        x_earth, y_earth, z_earth, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd)
        # Reverse for geocentric Sun
        x_sun, y_sun, z_sun = -x_earth, -y_earth, -z_earth
        lon, lat, dist = rectangular_to_spherical(x_sun, y_sun, z_sun)

        # Calculate speeds (simplified)
        jd_delta = 0.01  # Small time step
        x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd + jd_delta)
        x_sun2, y_sun2, z_sun2 = -x_earth2, -y_earth2, -z_earth2
        lon2, lat2, dist2 = rectangular_to_spherical(x_sun2, y_sun2, z_sun2)

        lon_speed = (lon2 - lon) / jd_delta
        lat_speed = (lat2 - lat) / jd_delta
        dist_speed = (dist2 - dist) / jd_delta

    elif planet_name == "Moon":
        lon, lat, dist = get_moon_position(jd)

        # Calculate speeds
        jd_delta = 0.01
        lon2, lat2, dist2 = get_moon_position(jd + jd_delta)

        lon_speed = (lon2 - lon) / jd_delta
        lat_speed = (lat2 - lat) / jd_delta
        dist_speed = (dist2 - dist) / jd_delta

    elif planet_name == "Rahu":
        mean_node, _ = get_lunar_nodes(jd)
        lon = mean_node
        lat = 0.0
        dist = 0.0  # Nodes don't have physical distance

        # Node regression speed
        lon_speed = -0.0529538083  # degrees per day
        lat_speed = 0.0
        dist_speed = 0.0

    elif planet_name == "NorthNode":
        _, true_node = get_lunar_nodes(jd)
        lon = true_node
        lat = 0.0
        dist = 0.0

        # True node speed varies, approximate
        jd_delta = 0.01
        _, true_node2 = get_lunar_nodes(jd + jd_delta)
        lon_speed = (true_node2 - true_node) / jd_delta
        lat_speed = 0.0
        dist_speed = 0.0

    elif planet_name == "Lilith":
        lon = get_lilith_position(jd)
        lat = 0.0
        dist = 0.0  # Mean apogee doesn't have physical distance

        # Lilith progression speed
        lon_speed = 0.1114040803  # degrees per day
        lat_speed = 0.0
        dist_speed = 0.0

    else:
        # Regular planets
        body_idx = BODY_INDICES[planet_name]

        # Get Earth's position for geocentric calculation
        x_earth, y_earth, z_earth, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd)

        # Get planet's heliocentric position
        x_planet, y_planet, z_planet, _, _, _ = get_body_position(body_idx, jd)

        # Convert to geocentric
        x_geo, y_geo, z_geo = heliocentric_to_geocentric(x_planet, y_planet, z_planet, x_earth, y_earth, z_earth)

        # Convert to spherical
        lon, lat, dist = rectangular_to_spherical(x_geo, y_geo, z_geo)

        # Calculate speeds
        jd_delta = 0.01
        x_earth2, y_earth2, z_earth2, _, _, _ = get_body_position(BODY_INDICES["Sun"], jd + jd_delta)
        x_planet2, y_planet2, z_planet2, _, _, _ = get_body_position(body_idx, jd + jd_delta)
        x_geo2, y_geo2, z_geo2 = heliocentric_to_geocentric(
            x_planet2, y_planet2, z_planet2, x_earth2, y_earth2, z_earth2
        )
        lon2, lat2, dist2 = rectangular_to_spherical(x_geo2, y_geo2, z_geo2)

        lon_speed = (lon2 - lon) / jd_delta
        lat_speed = (lat2 - lat) / jd_delta
        dist_speed = (dist2 - dist) / jd_delta

    # Apply aberration correction for light-time
    if planet_id >= 2:  # Not for Sun or Moon
        dlon, dlat = aberration_correction(lon, lat, jd)
        lon += dlon
        lat += dlat

    return np.array([lon, lat, dist, lon_speed, lat_speed, dist_speed])


def get_planet_name(planet_id: int) -> str:
    """Get planet name from ID (Swiss Ephemeris compatible).

    Args:
        planet_id: Planet ID (0-12)

    Returns:
        Planet name string
    """
    names = {
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
        10: "mean Node",  # Swiss Ephemeris convention
        11: "true Node",
        12: "mean Apogee",  # Lilith
    }
    return names.get(planet_id, f"Unknown({planet_id})")


def calculate_all_positions(jd: float) -> Dict[str, np.ndarray]:
    """Calculate positions for all bodies.

    Args:
        jd: Julian Date

    Returns:
        Dictionary mapping body names to position arrays
    """
    positions = {}

    for planet_id in range(13):  # 0-12
        try:
            pos = calc_planet_position(jd, planet_id)
            name = SWE_IDS[planet_id]
            positions[name] = pos
        except Exception as e:
            print(f"Error calculating position for {planet_id}: {e}")

    return positions


def body_properties(jd: float, body_id: int) -> np.ndarray:
    """Get body properties compatible with ketu interface.

    Args:
        jd: Julian Date
        body_id: Body ID (0-12)

    Returns:
        Array of [longitude, latitude, distance, lon_speed, lat_speed, dist_speed]
    """
    return calc_planet_position(jd, body_id)


def calculate_house_cusps(jd: float, lat: float, lon: float, house_system: str = "P") -> Tuple[np.ndarray, np.ndarray]:
    """Calculate house cusps (simplified implementation).

    Args:
        jd: Julian Date
        lat: Geographic latitude
        lon: Geographic longitude
        house_system: House system code (P=Placidus, K=Koch, etc.)

    Returns:
        Tuple of (cusps, ascmc) arrays
    """
    # This is a simplified implementation
    # Full implementation would require complex house calculations

    from .time import sidereal_time

    # Local sidereal time
    lst = sidereal_time(jd, lon)

    # Simple equal house system as placeholder
    cusps = np.zeros(12)
    ascendant = lst  # Simplified

    for i in range(12):
        cusps[i] = (ascendant + i * 30) % 360

    # ascmc array: ASC, MC, ARMC, Vertex, etc.
    mc = (lst + 90) % 360  # Simplified
    ascmc = np.array([ascendant, mc, lst, 0, 0, 0])

    return cusps, ascmc


def find_exact_aspect(
    jd_start: float, jd_end: float, body1_id: int, body2_id: int, aspect_angle: float, orb: float = 1.0
) -> Optional[float]:
    """Find exact aspect between two bodies within time range.

    Args:
        jd_start: Start Julian Date
        jd_end: End Julian Date
        body1_id: First body ID
        body2_id: Second body ID
        aspect_angle: Aspect angle in degrees (0, 60, 90, 120, 180)
        orb: Orb tolerance in degrees

    Returns:
        Julian Date of exact aspect or None if not found
    """
    # Binary search for exact aspect
    max_iterations = 50
    tolerance = 0.001  # 0.001 days = ~1.5 minutes

    def get_angle_diff(jd):
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
    """Find all aspects between two bodies in time range.

    Args:
        jd_start: Start Julian Date
        jd_end: End Julian Date
        body1_id: First body ID
        body2_id: Second body ID
        aspects: List of aspect angles to check (default: major aspects)

    Returns:
        List of tuples (jd, aspect_angle)
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
    """Calculate speed ratio compared to average speed.

    Args:
        jd: Julian Date
        body_id: Body ID

    Returns:
        Speed ratio (1.0 = average speed)
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
        12: 0.111404,  # Lilith
    }

    avg_speed = avg_speeds.get(body_id, 1.0)

    if avg_speed == 0:
        return 1.0

    return current_speed / avg_speed
