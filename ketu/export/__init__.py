"""Export module for Ketu.

This module provides various export functionalities including:
- Chart visualization (requires matplotlib)
- iCalendar export (requires icalendar library)
"""

# Chart visualization (optional dependency: matplotlib)
try:
    from .chart import draw_zodiacal_chart, PLANETS_DEFAULT, BIG_FIVE
    _CHART_AVAILABLE = True
except ImportError:
    _CHART_AVAILABLE = False

# iCalendar export (optional dependency: icalendar)
try:
    from .icalendar import (
        export_lunations_to_ical,
        export_transits_to_ical,
        export_aspects_to_ical,
    )
    _ICALENDAR_AVAILABLE = True
except ImportError:
    _ICALENDAR_AVAILABLE = False

__all__ = []

# Add chart exports if available
if _CHART_AVAILABLE:
    __all__.extend([
        "draw_zodiacal_chart",
        "PLANETS_DEFAULT",
        "BIG_FIVE",
    ])

# Add iCalendar exports if available
if _ICALENDAR_AVAILABLE:
    __all__.extend([
        "export_lunations_to_ical",
        "export_transits_to_ical",
        "export_aspects_to_ical",
    ])
