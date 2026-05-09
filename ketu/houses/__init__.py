"""House system calculations.

Public API surface (HOU-02 + HOU-05 + HOU-07 of v1.1 milestone):

- :func:`calculate_houses` — Compute house cusps for one or many charts;
  dispatches via :data:`SYSTEMS`, handles ``polar_fallback``.
- :func:`house_of` — Map a planetary longitude to its 1..12 house index.
- :data:`HOUSES_DTYPE` — Structured array layout for house results.
- :class:`HighLatitudeError` — Raised at polar latitudes (default behavior).
- :data:`SYSTEMS` — Dict of registered house-system implementations.

Examples
--------
>>> from ketu.houses import calculate_houses, house_of, HOUSES_DTYPE
>>> from ketu.houses import SYSTEMS, HighLatitudeError

See Also
--------
ketu.houses.registry.register : Decorator to add new systems.
ketu.houses.ascmc.compute_ascmc : Closed-form ASC/MC/ARMC/Vertex.

Notes
-----
The submodule imports below (``placidus``, ``koch``, ``porphyry``) trigger
the ``@register`` decorator at module load time, populating :data:`SYSTEMS`.
Without these imports, ``calculate_houses(system="placidus")`` would raise
``ValueError("unknown house system 'placidus'")`` because no module would
have loaded the decorators. Common-pitfall trap for registry patterns —
keep these imports even if "unused" by IDE inspection.
"""
from __future__ import annotations

from .api import calculate_houses, house_of
from .core import HOUSES_DTYPE, HighLatitudeError
from .registry import SYSTEMS, get_system, register

# Trigger registration of built-in systems by importing the modules.
# Each module's @register decorator runs on import. DO NOT remove —
# without these imports, SYSTEMS is empty at import time and every
# calculate_houses call would fail.
from . import placidus  # noqa: F401  registers 'placidus' in SYSTEMS
from . import koch       # noqa: F401  registers 'koch' in SYSTEMS
from . import porphyry   # noqa: F401  registers 'porphyry' in SYSTEMS
from . import whole_sign  # noqa: F401  registers 'whole_sign' in SYSTEMS
from . import equal       # noqa: F401  registers 'equal' in SYSTEMS

__all__ = [
    "HOUSES_DTYPE",
    "HighLatitudeError",
    "SYSTEMS",
    "calculate_houses",
    "get_system",
    "house_of",
    "register",
]
