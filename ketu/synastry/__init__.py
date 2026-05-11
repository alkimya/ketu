"""Synastry subpackage — inter-chart aspect calculations between two natal charts.

Public API surface (SYN-01..02 of the v1.2 milestone — Plans 16-01 + 16-02):

- :func:`calculate_synastry` — Compute inter-chart aspects between two
  :data:`ketu.charts.CHART_DTYPE` scalar records. Returns a structured
  array of :data:`SYNASTRY_DTYPE` rows; supports ``mode="filtered"``
  (default, only aspected pairs) and ``mode="dense"`` (all 225 ordered
  pairs with ``-1`` / ``NaN`` sentinels for non-aspected ones).
- :data:`SYNASTRY_DTYPE` — Structured-array layout for ONE inter-chart aspect
  record (8 fields, frozen contract).
- :data:`SYNASTRY_BODY_COUNT` — Frozen integer ``15`` (13 canonical + ASC + MC).
- :data:`SYNASTRY_FACTOR` — Multiplicative factor (``0.5``) applied to the
  natal orb formula for synastry.
- :data:`ASC_MC_NATAL_ORB_DEG` — Natal orb width (``8.0``) assigned to ASC/MC
  in synastry (not present in :data:`ketu.core.bodies`).
- :func:`resolve_orb_set` — Preset resolver for the ``orbs=`` parameter.
- :data:`OrbSetSpec` — Type alias for the ``resolve_orb_set`` input.

See Also
--------
ketu.charts.compute_chart : Computes the per-partner :data:`ketu.charts.CHART_DTYPE`
    records consumed by synastry (Phase 14 foundation).
ketu.aspects.calculate_aspects_vectorized : Intra-chart aspect engine that
    inspires the synastry orb formula and signed-orb convention.

Notes
-----
**UTC-only contract** — all timestamps consumed by synastry flow through
:func:`ketu.charts.compute_chart`, which enforces Julian-Date UT. Pass naive
local times at your peril; the package will not silently convert. This is
the same loud invariant as the rest of Ketu.

The body axis (15 bodies) is FROZEN by D-08 (Kala positional contract);
adding bodies (e.g. Vertex) is a v1.3 BREAKING change.
"""
from __future__ import annotations

from .api import calculate_synastry
from .core import SYNASTRY_BODY_COUNT, SYNASTRY_DTYPE
from .orbs import (
    ASC_MC_NATAL_ORB_DEG,
    OrbSetSpec,
    SYNASTRY_FACTOR,
    resolve_orb_set,
)

__all__ = [
    "ASC_MC_NATAL_ORB_DEG",
    "OrbSetSpec",
    "SYNASTRY_BODY_COUNT",
    "SYNASTRY_DTYPE",
    "SYNASTRY_FACTOR",
    "calculate_synastry",
    "resolve_orb_set",
]
