"""Planetary cycle calculations for time series analysis.

This module provides continuous cycle state calculations aligned to timestamps,
designed for correlation analysis with price data.

Unlike the aspects module (which finds discrete events), this module calculates
the instantaneous state of planetary cycles at any given moment.

Key concepts:
- Angular separation: Current distance between two bodies (0-360°)
- Cycle progress: Normalized position in cycle (0.0-1.0)
- Cycle phase: Waxing (0→180°) or waning (180→360°)
- Aspect proximity: Distance to nearest major aspect

Usage:
    from datetime import datetime, timedelta
    from ketu.cycles import generate_cycle_series, CycleState

    # Generate cycle data aligned to timestamps
    timestamps = [datetime(2025, 1, 1) + timedelta(hours=i) for i in range(8760)]
    cycles = generate_cycle_series(
        body1="Sun",
        body2="Mars",
        timestamps=timestamps,
    )

    # Returns numpy structured array with cycle state at each timestamp
"""

from ketu.cycles.calculator import (
    generate_cycle_series,
    generate_multi_cycle_series,
    CycleState,
    CYCLE_DTYPE,
    MAJOR_ASPECTS,
    DEFAULT_PAIRS,
)

__all__ = [
    "generate_cycle_series",
    "generate_multi_cycle_series",
    "CycleState",
    "CYCLE_DTYPE",
    "MAJOR_ASPECTS",
    "DEFAULT_PAIRS",
]
