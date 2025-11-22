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

__version__ = "0.3.0"
__author__ = "Loc Cosnier"
__license__ = "MIT"

# Import from modular structure
from ketu.core import bodies, aspects, signs
from ketu.calculations import (
    # Time conversion
    local_to_utc,
    utc_to_julian,
    julian_to_utc,

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
    calculate_aspects_vectorized,
    calculate_aspects_batch,
    find_aspect_timing,
    find_aspects_between_dates,

    # Utility functions
    decimal_degrees_to_dms,
    dd_to_dms,
    distance,
    get_orb,
    body_properties,
)
from ketu.display import print_positions, print_aspects, main

# Advanced aspect window calculations
from ketu.aspect_windows import (
    AspectMoment,
    AspectWindow,
    find_aspect_window,
    find_aspects_timeline,
)

# Transit calculations
from ketu.transits import (
    TransitMoment,
    TransitWindow,
    NatalPosition,
    TransitAspect,
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
)

# iCalendar export (requires: pip install icalendar)
try:
    from ketu.icalendar_export import (
        export_lunations_to_ical,
        export_transits_to_ical,
        export_aspects_to_ical,
    )
    _ICALENDAR_AVAILABLE = True
except ImportError:
    _ICALENDAR_AVAILABLE = False

# Chart visualization (requires: pip install matplotlib)
try:
    from ketu.chart import draw_zodiacal_chart
    _CHART_AVAILABLE = True
except ImportError:
    _CHART_AVAILABLE = False

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
    "julian_to_utc",

    # Body information
    "body_name",
    "body_id",
    "body_properties",

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
    "calculate_aspects_vectorized",
    "calculate_aspects_batch",
    "find_aspect_timing",
    "find_aspects_between_dates",

    # Utility functions
    "decimal_degrees_to_dms",
    "dd_to_dms",
    "distance",
    "get_orb",

    # Display functions
    "print_positions",
    "print_aspects",

    # Main entry point
    "main",

    # Advanced aspect windows
    "AspectMoment",
    "AspectWindow",
    "find_aspect_window",
    "find_aspects_timeline",

    # Transits
    "TransitMoment",
    "TransitWindow",
    "NatalPosition",
    "TransitAspect",
    "find_transits_to_position",
    "get_natal_positions",
    "compare_dates_transits",
]

# Add iCalendar exports if available
if _ICALENDAR_AVAILABLE:
    __all__.extend([
        "export_lunations_to_ical",
        "export_transits_to_ical",
        "export_aspects_to_ical",
    ])

# Add chart visualization if available
if _CHART_AVAILABLE:
    __all__.extend([
        "draw_zodiacal_chart",
    ])
