"""Ketu - Library for astronomical calculations and astrological aspects

Ketu is a Python library to compute positions of astronomical bodies (Sun, Moon,
planets and mean Node aka Rahu) and calculate astrological aspects based on their
positions.

Example:
    >>> from datetime import datetime
    >>> from zoneinfo import ZoneInfo
    >>> from ketu import utc_to_julian, print_positions, print_aspects
    >>>
    >>> # Define a datetime
    >>> dtime = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
    >>> jday = utc_to_julian(dtime)
    >>>
    >>> # Print positions and aspects
    >>> print_positions(jday)
    >>> print_aspects(jday)
"""

__version__ = "0.2.0"
__author__ = "Loc Cosnier"
__license__ = "MIT"

from ketu.ketu import (
    # Data structures
    bodies,
    aspects,
    signs,

    # Time conversion
    local_to_utc,
    utc_to_julian,

    # Body information
    body_name,
    body_id,

    # Position calculations
    long,
    lat,
    dist_au,
    vlong,
    vlat,
    vdist_au,
    positions,

    # Analysis functions
    is_retrograde,
    is_ascending,
    body_sign,

    # Aspect calculations
    get_aspect,
    calculate_aspects,

    # Utility functions
    decimal_degrees_to_dms,
    distance,
    get_orb,

    # Display functions
    print_positions,
    print_aspects,

    # Main entry point
    main,
)

__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__license__",

    # Data structures
    "bodies",
    "aspects",
    "signs",

    # Time conversion
    "local_to_utc",
    "utc_to_julian",

    # Body information
    "body_name",
    "body_id",

    # Position calculations
    "long",
    "lat",
    "dist_au",
    "vlong",
    "vlat",
    "vdist_au",
    "positions",

    # Analysis functions
    "is_retrograde",
    "is_ascending",
    "body_sign",

    # Aspect calculations
    "get_aspect",
    "calculate_aspects",

    # Utility functions
    "decimal_degrees_to_dms",
    "distance",
    "get_orb",

    # Display functions
    "print_positions",
    "print_aspects",

    # Main entry point
    "main",
]
