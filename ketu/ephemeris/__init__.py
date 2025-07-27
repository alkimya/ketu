"""Ephemeris package for astronomical calculations.

This package provides numpy-based implementations of planetary position
calculations, replacing the pyswisseph dependency.
"""

from .time import (
    utc_to_julian,
    julian_to_utc,
    local_to_utc,
    delta_t,
    terrestrial_to_universal,
    universal_to_terrestrial,
    equation_of_time,
    sidereal_time,
)

from .orbital import (
    ORBITAL_ELEMENTS,
    normalize_angle,
    solve_kepler_equation,
    orbital_elements_at_date,
    compute_position,
    apply_perturbations,
    get_body_position,
    get_moon_position,
    get_lunar_nodes,
    get_lilith_position,
)

from .coordinates import (
    spherical_to_rectangular,
    rectangular_to_spherical,
    ecliptic_to_equatorial,
    equatorial_to_ecliptic,
    heliocentric_to_geocentric,
    geocentric_to_topocentric,
    mean_obliquity,
    true_obliquity,
    nutation,
    aberration_correction,
)

from .planets import (
    calc_planet_position,
    get_planet_name,
    body_properties,
    calculate_all_positions,
    calculate_house_cusps,
    find_exact_aspect,
    find_all_aspects,
    calculate_speed_ratio,
)

__all__ = [
    # Time functions
    "utc_to_julian",
    "julian_to_utc",
    "local_to_utc",
    "delta_t",
    "terrestrial_to_universal",
    "universal_to_terrestrial",
    "equation_of_time",
    "sidereal_time",
    # Orbital functions
    "ORBITAL_ELEMENTS",
    "normalize_angle",
    "solve_kepler_equation",
    "orbital_elements_at_date",
    "compute_position",
    "apply_perturbations",
    "get_body_position",
    "get_moon_position",
    "get_lunar_nodes",
    "get_lilith_position",
    # Coordinate functions
    "spherical_to_rectangular",
    "rectangular_to_spherical",
    "ecliptic_to_equatorial",
    "equatorial_to_ecliptic",
    "heliocentric_to_geocentric",
    "geocentric_to_topocentric",
    "mean_obliquity",
    "true_obliquity",
    "nutation",
    "aberration_correction",
    # Planet functions
    "calc_planet_position",
    "get_planet_name",
    "body_properties",
    "calculate_all_positions",
    "calculate_house_cusps",
    "find_exact_aspect",
    "find_all_aspects",
    "calculate_speed_ratio",
]
