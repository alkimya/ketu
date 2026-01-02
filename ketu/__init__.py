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

__version__ = "0.4.0"
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

    # Utility functions
    decimal_degrees_to_dms,
    dd_to_dms,
    distance,
    body_properties,
)

# Aspect calculations (moved to aspects module)
from ketu.aspects import (
    get_aspect,
    calculate_aspects,
    calculate_aspects_vectorized,
    calculate_aspects_batch,
    find_aspect_timing,
    find_aspects_between_dates,
    get_orb,
)

from ketu.lunar_calendar import (
    LunarCycle,
    LunarCalendar,
    generate_lunar_calendar,
    print_lunar_calendar,
)

from ketu.display import print_positions, print_aspects, main

# Advanced aspect calculations (from aspects package)
from ketu.aspects import (
    # Aspect windows (precise timing)
    AspectMoment,
    AspectWindow,
    find_aspect_window,
    find_aspects_timeline,

    # Aspect timelines (ML-ready)
    AspectEvent,
    AspectTimeline,
    generate_aspect_timeline,

    # Transits
    TransitMoment,
    TransitWindow,
    NatalPosition,
    TransitAspect,
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
)

# Export module (optional dependencies)
try:
    from ketu.export import (
        draw_zodiacal_chart,
        export_lunations_to_ical,
        export_transits_to_ical,
        export_aspects_to_ical,
    )
    _EXPORT_AVAILABLE = True
except ImportError:
    _EXPORT_AVAILABLE = False

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
    "get_orb",

    # Utility functions
    "decimal_degrees_to_dms",
    "dd_to_dms",
    "distance",

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

    # Lunar calendar
    "LunarCycle",
    "LunarCalendar",
    "generate_lunar_calendar",
    "print_lunar_calendar",

    # Transits
    "TransitMoment",
    "TransitWindow",
    "NatalPosition",
    "TransitAspect",
    "find_transits_to_position",
    "get_natal_positions",
    "compare_dates_transits",

    # Aspect timelines (ML/research)
    "AspectEvent",
    "AspectTimeline",
    "generate_aspect_timeline",

    # Complex number representation (ML/research)
    "ZodiacPoint",
    "CycleRatio",
    "Aspect",
    "ASPECTS",
    "circular_mean",
    "circular_std",
    "phase_locking_value",
    "degrees_to_complex",
    "cycle_ratio_vectorized",
    "to_ml_features_vectorized",
]

# Complex number representation for cycles
from ketu.complex import (
    ZodiacPoint,
    CycleRatio,
    Aspect,
    ASPECTS,
    circular_mean,
    circular_std,
    phase_locking_value,
    degrees_to_complex,
    cycle_ratio_vectorized,
    to_ml_features_vectorized,
)

# Add export functions if available
if _EXPORT_AVAILABLE:
    __all__.extend([
        "draw_zodiacal_chart",
        "export_lunations_to_ical",
        "export_transits_to_ical",
        "export_aspects_to_ical",
    ])
