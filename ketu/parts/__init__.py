"""Arabic Parts (Hermetic Lots) — extensible registry + sect-aware dispatch.

Public API (PARTS-01..07 of the v1.2 milestone):

- :data:`PARTS` — dict of registered :class:`PartSpec` entries (analogue
  of :data:`ketu.houses.SYSTEMS`).
- :func:`calculate_part` ``(part_name, chart)`` — sect-aware longitude for
  one part.
- :func:`calculate_all_parts` ``(chart, parts=None)`` — dict of all (or
  filtered) parts.
- :func:`register` / :func:`get_part` — registry plumbing; a v1.3 Lot is
  one :func:`register` call, no API change.

Sect is determined per-call via :func:`ketu.charts.api.is_day_chart`
(D-12: never cached in :data:`ketu.charts.CHART_DTYPE`).
Formula signature: ``(asc_lon, sun_lon, moon_lon, venus_lon) -> longitude in [0, 360)``.

See Also
--------
ketu.parts.registry.register : Add a new Lot without touching dispatch.
ketu.charts.api.is_day_chart : Sect helper this module dispatches on.
"""
from __future__ import annotations

from .api import calculate_all_parts, calculate_part
from .registry import PARTS, PartSpec, get_part, register

# Built-in parts. Registered at import time (mirror houses/__init__.py
# trigger-import pattern).
# DO NOT remove — without these calls, PARTS is empty and
# calculate_part('fortune', ...) raises
# ValueError("unknown part 'fortune'") (RESEARCH Pitfall 2).

# Fortune — sect-aware. day: ASC + Moon - Sun / night: ASC + Sun - Moon.
register(
    "fortune",
    day_formula=lambda asc, sun, moon, venus: (asc + moon - sun) % 360.0,
    night_formula=lambda asc, sun, moon, venus: (asc + sun - moon) % 360.0,
    description="day: ASC+Moon-Sun / night: ASC+Sun-Moon (sect-aware)",
)

# Spirit — sect-aware, mirror of Fortune. day: ASC + Sun - Moon / night: ASC + Moon - Sun.
register(
    "spirit",
    day_formula=lambda asc, sun, moon, venus: (asc + sun - moon) % 360.0,
    night_formula=lambda asc, sun, moon, venus: (asc + moon - sun) % 360.0,
    description="day: ASC+Sun-Moon / night: ASC+Moon-Sun (sect-aware, mirror of Fortune)",
)

# Marriage — FIXED (no sect inversion). ASC + Descendant - Venus = ASC + (ASC+180) - Venus
#   = (2*ASC + 180 - Venus) % 360. night_formula IS day_formula (identity), NOT a sect_aware flag.
_marriage_formula = lambda asc, sun, moon, venus: (2.0 * asc + 180.0 - venus) % 360.0  # noqa: E731
register(
    "marriage",
    day_formula=_marriage_formula,
    night_formula=_marriage_formula,
    description="ASC+DESC-Venus = ASC+(ASC+180)-Venus (fixed - no sect inversion)",
)

__all__ = [
    "PARTS",
    "PartSpec",
    "calculate_all_parts",
    "calculate_part",
    "get_part",
    "register",
]
