"""
Orbital elements and calculations for planetary positions.

This module is the **public re-export hub** for the ephemeris orbital
sub-package. Implementation lives in focused private modules:

- ``_elements.py``      — ORBITAL_ELEMENTS structured array + Lilith constants
- ``_kepler.py``        — normalize_angle, solve_kepler_equation
- ``_mechanics.py``     — orbital_elements_at_date, compute_position
- ``_perturbations.py`` — apply_perturbations (Jupiter/Saturn/Uranus branches)
- ``_body_getters.py``  — scalar and vectorized body position getters

Every ``from ketu.ephemeris.orbital import X`` that worked before the split
continues to work byte-identically after it.
"""

# Re-export data so ``from ketu.ephemeris.orbital import ORBITAL_ELEMENTS``
# and the five ``_LILITH_*`` imports keep working.
from ._elements import (  # noqa: F401
    ORBITAL_ELEMENTS,
    _LILITH_MEAN_EPOCH_DEG,
    _LILITH_MEAN_RATE_DEG_PER_DAY,
    _LILITH_PERTURB_AMP_DEG,
    _LILITH_PERTURB_RATE_DEG_PER_DAY,
    _LILITH_PERTURB_PHASE_DEG,
)

# Re-export pure-compute utilities
from ._kepler import normalize_angle, solve_kepler_equation  # noqa: F401

# Re-export orbital mechanics
from ._mechanics import orbital_elements_at_date, compute_position  # noqa: F401

# Re-export perturbation corrections
from ._perturbations import apply_perturbations  # noqa: F401

# Re-export body position getters (scalar + vectorized)
from ._body_getters import (  # noqa: F401
    get_body_position,
    get_moon_position,
    get_lunar_nodes,
    get_lilith_position,
    get_body_position_vectorized,
    get_moon_position_vectorized,
)

__all__ = [
    # Data
    "ORBITAL_ELEMENTS",
    "_LILITH_MEAN_EPOCH_DEG",
    "_LILITH_MEAN_RATE_DEG_PER_DAY",
    "_LILITH_PERTURB_AMP_DEG",
    "_LILITH_PERTURB_RATE_DEG_PER_DAY",
    "_LILITH_PERTURB_PHASE_DEG",
    # Utilities
    "normalize_angle",
    "solve_kepler_equation",
    # Mechanics
    "orbital_elements_at_date",
    "compute_position",
    # Perturbations
    "apply_perturbations",
    # Body getters
    "get_body_position",
    "get_moon_position",
    "get_lunar_nodes",
    "get_lilith_position",
    "get_body_position_vectorized",
    "get_moon_position_vectorized",
]
