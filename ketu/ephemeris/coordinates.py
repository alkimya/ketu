"""Coordinate transformation functions for astronomical calculations.

This module provides functions to transform between different coordinate
systems used in astronomy: rectangular/spherical, ecliptic/equatorial, etc.
"""

import numpy as np
from typing import Tuple


def spherical_to_rectangular(lon: float, lat: float, r: float) -> Tuple[float, float, float]:
    """Convert spherical coordinates to rectangular coordinates.

    Args:
        lon: Longitude in degrees
        lat: Latitude in degrees
        r: Distance

    Returns:
        Tuple of (x, y, z) in same units as r
    """
    lon_rad = np.deg2rad(lon)
    lat_rad = np.deg2rad(lat)

    x = r * np.cos(lon_rad) * np.cos(lat_rad)
    y = r * np.sin(lon_rad) * np.cos(lat_rad)
    z = r * np.sin(lat_rad)

    return x, y, z


def rectangular_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Convert rectangular coordinates to spherical coordinates.

    Args:
        x, y, z: Rectangular coordinates

    Returns:
        Tuple of (lon, lat, r) where angles are in degrees
    """
    r = np.sqrt(x**2 + y**2 + z**2)

    if r == 0:
        return 0.0, 0.0, 0.0

    lon = np.rad2deg(np.arctan2(y, x))
    lat = np.rad2deg(np.arcsin(z / r))

    # Normalize longitude to 0-360
    if lon < 0:
        lon += 360.0

    return lon, lat, r


def ecliptic_to_equatorial(x: float, y: float, z: float, obliquity: float) -> Tuple[float, float, float]:
    """Convert ecliptic coordinates to equatorial coordinates.

    Args:
        x, y, z: Ecliptic rectangular coordinates
        obliquity: Obliquity of ecliptic in degrees

    Returns:
        Tuple of (x_eq, y_eq, z_eq) equatorial rectangular coordinates
    """
    obl_rad = np.deg2rad(obliquity)
    cos_obl = np.cos(obl_rad)
    sin_obl = np.sin(obl_rad)

    x_eq = x
    y_eq = y * cos_obl - z * sin_obl
    z_eq = y * sin_obl + z * cos_obl

    return x_eq, y_eq, z_eq


def equatorial_to_ecliptic(x: float, y: float, z: float, obliquity: float) -> Tuple[float, float, float]:
    """Convert equatorial coordinates to ecliptic coordinates.

    Args:
        x, y, z: Equatorial rectangular coordinates
        obliquity: Obliquity of ecliptic in degrees

    Returns:
        Tuple of (x_ecl, y_ecl, z_ecl) ecliptic rectangular coordinates
    """
    obl_rad = np.deg2rad(obliquity)
    cos_obl = np.cos(obl_rad)
    sin_obl = np.sin(obl_rad)

    x_ecl = x
    y_ecl = y * cos_obl + z * sin_obl
    z_ecl = -y * sin_obl + z * cos_obl

    return x_ecl, y_ecl, z_ecl


def heliocentric_to_geocentric(
    x_planet: float, y_planet: float, z_planet: float, x_earth: float, y_earth: float, z_earth: float
) -> Tuple[float, float, float]:
    """Convert heliocentric coordinates to geocentric coordinates.

    Args:
        x_planet, y_planet, z_planet: Heliocentric coordinates of planet
        x_earth, y_earth, z_earth: Heliocentric coordinates of Earth

    Returns:
        Tuple of (x_geo, y_geo, z_geo) geocentric coordinates
    """
    x_geo = x_planet - x_earth
    y_geo = y_planet - y_earth
    z_geo = z_planet - z_earth

    return x_geo, y_geo, z_geo


def geocentric_to_topocentric(
    lon: float, lat: float, dist: float, observer_lat: float, observer_lon: float, lst: float, height: float = 0.0
) -> Tuple[float, float, float]:
    """Convert geocentric coordinates to topocentric coordinates.

    Args:
        lon: Geocentric longitude in degrees
        lat: Geocentric latitude in degrees
        dist: Distance in AU
        observer_lat: Observer's latitude in degrees
        observer_lon: Observer's longitude in degrees
        lst: Local sidereal time in degrees
        height: Observer's height above sea level in meters

    Returns:
        Tuple of (az, alt, dist) where:
        - az: Azimuth in degrees (0 = North, 90 = East)
        - alt: Altitude in degrees above horizon
        - dist: Topocentric distance in AU
    """
    # Earth's equatorial radius in AU
    earth_radius_au = 4.26352e-5

    # Observer's position
    obs_lat_rad = np.deg2rad(observer_lat)

    # Parallax factors
    rho_cos = np.cos(obs_lat_rad) + height / 6378140.0 * np.cos(obs_lat_rad)
    rho_sin = np.sin(obs_lat_rad) + height / 6378140.0 * np.sin(obs_lat_rad)

    # Convert to rectangular equatorial
    x, y, z = spherical_to_rectangular(lon, lat, dist)

    # Hour angle
    ha = lst - lon
    ha_rad = np.deg2rad(ha)

    # Topocentric rectangular coordinates
    dx = -earth_radius_au * rho_cos * np.cos(ha_rad)
    dy = -earth_radius_au * rho_cos * np.sin(ha_rad)
    dz = -earth_radius_au * rho_sin

    x_topo = x + dx
    y_topo = y + dy
    z_topo = z + dz

    # Convert to horizontal coordinates
    lat_rad = np.deg2rad(lat)

    # Rotate to horizon system
    x_hor = -x_topo * np.sin(ha_rad) + y_topo * np.cos(ha_rad)
    y_hor = (
        -x_topo * np.cos(ha_rad) * np.sin(obs_lat_rad)
        - y_topo * np.sin(ha_rad) * np.sin(obs_lat_rad)
        + z_topo * np.cos(obs_lat_rad)
    )
    z_hor = (
        x_topo * np.cos(ha_rad) * np.cos(obs_lat_rad)
        + y_topo * np.sin(ha_rad) * np.cos(obs_lat_rad)
        + z_topo * np.sin(obs_lat_rad)
    )

    # Convert to azimuth and altitude
    az = np.rad2deg(np.arctan2(x_hor, y_hor))
    alt = np.rad2deg(np.arcsin(z_hor / np.sqrt(x_hor**2 + y_hor**2 + z_hor**2)))

    # Normalize azimuth to 0-360
    if az < 0:
        az += 360.0

    # Topocentric distance
    dist_topo = np.sqrt(x_topo**2 + y_topo**2 + z_topo**2)

    return az, alt, dist_topo


def mean_obliquity(jd: float) -> float:
    """Calculate mean obliquity of the ecliptic.

    Args:
        jd: Julian Date

    Returns:
        Mean obliquity in degrees
    """
    # Centuries since J2000.0
    T = (jd - 2451545.0) / 36525.0

    # IAU 2006 formula
    obliquity = (
        23.0
        + 26.0 / 60.0
        + 21.448 / 3600.0
        - 46.8150 / 3600.0 * T
        - 0.00059 / 3600.0 * T**2
        + 0.001813 / 3600.0 * T**3
    )

    return obliquity


def nutation(jd: float) -> Tuple[float, float]:
    """Calculate nutation in longitude and obliquity.

    Args:
        jd: Julian Date

    Returns:
        Tuple of (nut_lon, nut_obl) in degrees
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Mean elongation of Moon from Sun
    D = np.deg2rad(297.85036 + 445267.111480 * d / 36525.0)

    # Sun's mean anomaly
    M = np.deg2rad(357.52772 + 35999.050340 * d / 36525.0)

    # Moon's mean anomaly
    Mm = np.deg2rad(134.96298 + 477198.867398 * d / 36525.0)

    # Moon's argument of latitude
    F = np.deg2rad(93.27191 + 483202.017538 * d / 36525.0)

    # Longitude of ascending node
    omega = np.deg2rad(125.04452 - 1934.136261 * d / 36525.0)

    # Nutation in longitude (arcseconds)
    nut_lon_as = (
        -17.20 * np.sin(omega)
        - 1.32 * np.sin(2 * F - 2 * D + 2 * omega)
        - 0.23 * np.sin(2 * F + 2 * omega)
        + 0.21 * np.sin(2 * omega)
    )

    # Nutation in obliquity (arcseconds)
    nut_obl_as = (
        9.20 * np.cos(omega)
        + 0.57 * np.cos(2 * F - 2 * D + 2 * omega)
        + 0.10 * np.cos(2 * F + 2 * omega)
        - 0.09 * np.cos(2 * omega)
    )

    # Convert to degrees
    nut_lon = nut_lon_as / 3600.0
    nut_obl = nut_obl_as / 3600.0

    return nut_lon, nut_obl


def true_obliquity(jd: float) -> float:
    """Calculate true obliquity of the ecliptic.

    Args:
        jd: Julian Date

    Returns:
        True obliquity in degrees
    """
    mean_obl = mean_obliquity(jd)
    _, nut_obl = nutation(jd)

    return mean_obl + nut_obl


def aberration_correction(lon: float, lat: float, jd: float) -> Tuple[float, float]:
    """Apply stellar aberration correction.

    Args:
        lon: Longitude in degrees
        lat: Latitude in degrees
        jd: Julian Date

    Returns:
        Tuple of (dlon, dlat) corrections in degrees
    """
    # Days since J2000.0
    d = jd - 2451545.0

    # Earth's orbital eccentricity
    e = 0.016709 - 1.151e-9 * d

    # Sun's mean longitude
    L = np.deg2rad(280.460 + 0.9856474 * d)

    # Aberration constant (arcseconds)
    k = 20.49552

    # Corrections
    lon_rad = np.deg2rad(lon)
    lat_rad = np.deg2rad(lat)

    dlon_as = -k * np.cos(L - lon_rad) / np.cos(lat_rad) + k * e * np.cos(
        np.deg2rad(102.93735 + 0.71953 * d) - lon_rad
    ) / np.cos(lat_rad)

    dlat_as = -k * np.sin(lat_rad) * (np.sin(L - lon_rad) - e * np.sin(np.deg2rad(102.93735 + 0.71953 * d) - lon_rad))

    # Convert to degrees
    dlon = dlon_as / 3600.0
    dlat = dlat_as / 3600.0

    return dlon, dlat
