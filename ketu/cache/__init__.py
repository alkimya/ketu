"""Ephemeris cache module for fast planetary position lookups.

This module provides a caching layer that pre-computes daily planetary
positions, enabling O(1) lookups with linear interpolation for intra-day times.

Typical speedup: 100x+ for repeated queries within cached date ranges.

Example usage:
    from ketu.cache import EphemerisCache

    cache = EphemerisCache()
    cache.ensure_range(2025, 1, 2025, 12)  # Pre-compute 2025

    # Fast lookup with interpolation
    positions = cache.get_positions(datetime(2025, 6, 15, 14, 30))
"""

from .ephemeris_cache import (
    EphemerisCache,
    BODY_COUNT,
    POSITION_FIELDS,
    get_default_cache,
)

__all__ = [
    "EphemerisCache",
    "BODY_COUNT",
    "POSITION_FIELDS",
    "get_default_cache",
]
