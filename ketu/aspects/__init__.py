"""Aspect calculations and analysis module.

This module provides comprehensive tools for calculating and analyzing
planetary aspects, including:

- Core aspect calculations (orbs, aspect detection)
- Aspect windows (entry/exit times, exact moments)
- Aspect timelines (ML-ready time series data)
- Transit calculations (transits to natal positions)
- Aspect set presets and resolver (Phase 9)

Submodules:
- core: Low-level aspect calculations
- calculator: High-level aspect finding functions
- windows: Aspect window detection with precise timing
- timelines: ML-ready aspect timeline generation
- transits: Transit calculations to natal positions
- presets: CLASSICAL/TRADITIONAL/EXTENDED masks + resolve_aspect_set
"""

# Aspect calculator (high-level API)
from ketu.aspects.calculator import (
    get_aspect,
    calculate_aspects,
    calculate_aspects_vectorized,
    calculate_aspects_batch,
    find_aspect_timing,
    find_aspects_between_dates,
    get_orb,
)

# Aspect windows (precise timing)
from ketu.aspects.windows import (
    AspectMoment,
    AspectWindow,
    find_aspect_window,
    find_aspects_timeline,
)

# Aspect timelines (ML-ready)
from ketu.aspects.timelines import (
    AspectEvent,
    AspectTimeline,
    generate_aspect_timeline,
)

# Transits
from ketu.aspects.transits import (
    TransitMoment,
    TransitWindow,
    NatalPosition,
    TransitAspect,
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
)

# Aspect set presets and resolver (Phase 9 / Phase 26)
from ketu.aspects.presets import (
    CLASSICAL,
    TRADITIONAL,
    EXTENDED,
    AspectSetSpec,
    aspects_for_harmonics,
    resolve_aspect_set,
)

# Dynamic harmonic generator (Phase 28)
from ketu.aspects.harmonics import (
    generate_harmonic_aspects,
    HARMONIC_DTYPE,
    DynamicAspectSpec,
)

__all__ = [
    # Calculator (high-level API)
    "get_aspect",
    "calculate_aspects",
    "calculate_aspects_vectorized",
    "calculate_aspects_batch",
    "find_aspect_timing",
    "find_aspects_between_dates",
    "get_orb",

    # Windows
    "AspectMoment",
    "AspectWindow",
    "find_aspect_window",
    "find_aspects_timeline",

    # Timelines (ML-ready)
    "AspectEvent",
    "AspectTimeline",
    "generate_aspect_timeline",

    # Transits
    "TransitMoment",
    "TransitWindow",
    "NatalPosition",
    "TransitAspect",
    "find_transits_to_position",
    "get_natal_positions",
    "compare_dates_transits",

    # Presets (Phase 9 / Phase 26 — configurable aspects)
    "CLASSICAL",
    "TRADITIONAL",
    "EXTENDED",
    "AspectSetSpec",
    "aspects_for_harmonics",
    "resolve_aspect_set",

    # Dynamic harmonic generator (Phase 28)
    "generate_harmonic_aspects",
    "HARMONIC_DTYPE",
    "DynamicAspectSpec",
]
