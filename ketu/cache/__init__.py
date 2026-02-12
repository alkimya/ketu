"""Ephemeris cache module for fast planetary position lookups.

Ketu uses a coherent two-layer caching strategy, where each layer serves
a distinct, non-overlapping use case:

**Layer 1: LRU Cache (Single-Point Lookups)**
    - Location: @lru_cache decorator on calc_planet_position() in ephemeris/planets.py
    - Type: In-memory memoization
    - Access Pattern: Repeated single-point queries (e.g., interactive calculations)
    - Performance: ~0.01ms hit latency, thread-safe, auto-managed
    - Use Case: Individual date calculations, aspect finding, transit detection
    - Automatic: No user action needed - decorator handles all caching

**Layer 2: EphemerisCache (Batch Operations)**
    - Location: This module (cache/ephemeris_cache.py)
    - Type: Disk-backed monthly pre-computation
    - Access Pattern: Large time-series arrays (e.g., cycle generation, resonance fields)
    - Performance: ~10x faster than looping calc_planet_position() for arrays
    - Use Case: Timeline generation, multi-body batch calculations, ML training data
    - Explicit: User creates instance and calls ensure_range() before batch workflows

**Why Two Layers?**
    They optimize fundamentally different access patterns:
    - LRU: Fast repeated lookups of same dates (hit rate matters)
    - EphemerisCache: Fast batch generation of new dates (vectorization matters)

    Merging them would degrade performance for one pattern or the other.
    Together they form one coherent caching strategy with clear boundaries.

**Example Usage:**
    from ketu.cache import EphemerisCache

    cache = EphemerisCache()
    cache.ensure_range(2025, 1, 2025, 12)  # Pre-compute 2025

    # Fast batch lookup with interpolation
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
