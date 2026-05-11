"""Synastry subpackage — inter-chart aspect calculations between two natal charts.

Public API surface (SYN-01 of the v1.2 milestone — Plan 16-01 foundation):

- :data:`SYNASTRY_DTYPE` — Structured-array layout for ONE inter-chart aspect
  record (8 fields, frozen contract).
- :data:`SYNASTRY_BODY_COUNT` — Frozen integer ``15`` (13 canonical + ASC + MC).
- :data:`SYNASTRY_FACTOR` — Multiplicative factor (``0.5``) applied to the
  natal orb formula for synastry.
- :data:`ASC_MC_NATAL_ORB_DEG` — Natal orb width (``8.0``) assigned to ASC/MC
  in synastry (not present in :data:`ketu.core.bodies`).
- :func:`resolve_orb_set` — Preset resolver for the ``orbs=`` parameter.
- :data:`OrbSetSpec` — Type alias for the ``resolve_orb_set`` input.

The compute entry point ``calculate_synastry`` is intentionally NOT exported
in Plan 16-01 — Plan 16-02 owns the compute logic and will re-export it from
this module. The data + orb-resolution surface is frozen FIRST so that
Plan 16-02 (compute), Plan 16-03 (oracle), and Plan 16-04 (CLI) consume a
stable contract.

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
    "resolve_orb_set",
]
