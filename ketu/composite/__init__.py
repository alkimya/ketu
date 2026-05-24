"""Composite chart subpackage — midpoint composite from two natal charts.

Public API surface (COMP-01..04 of the v1.2 milestone):

- :func:`circular_midpoint` — Short-arc midpoint on the unit circle,
  modulo 360°. Vectorised. ``circular_midpoint(359.0, 1.0) == 0.0``
  (NOT 180.0). Phase 17 Plan 01.
- :func:`calculate_composite` — Derive a midpoint composite chart from
  two :data:`ketu.charts.CHART_DTYPE` scalar records. Returns a scalar
  :data:`ketu.charts.CHART_DTYPE` whose body longitudes, ASC, MC,
  ARMC, and Vertex are circular midpoints of the two natals, and
  whose house cusps are derived from the composite ASC and MC via
  Porphyry-style trisection (NOT recomputed from any partner's
  geographic context). Phase 17 Plan 02.

See Also
--------
ketu.charts.compute_chart : Build the per-partner CHART_DTYPE inputs.
ketu.synastry.calculate_synastry : Inter-chart aspect computation
    (the complementary pair-chart operation on the same CHART_DTYPE
    pair).

Notes
-----
**Midpoint method only.** Phase 17 implements the pure midpoint
composite — every CHART_DTYPE field is a circular midpoint of the two
natals; house cusps are derived geometrically from composite ASC +
composite MC via Porphyry-style trisection. The 'reference place
method' documented by Astrodienst, which back-computes the composite
ASC and houses from a chosen reference latitude, is NOT implemented;
users requiring that convention should compute it externally from the
composite ARMC stored in the output.

**Davison composite is NOT in scope.** Davison composites — built at
the temporal midpoint (mid-Julian-Date) and spatial midpoint
(geographic great-circle midpoint) of two births, then computed as a
fresh natal — are deferred to v1.3 (tracked in REQUIREMENTS §"Deferred
to v1.3"). The midpoint method implemented here is algebraically
distinct from Davison and the two conventions are not interchangeable.
No function in this subpackage produces Davison composites; no
``davison=`` kwarg exists on :func:`calculate_composite`.

**Composite (jd, lat, lon) are bookkeeping, NOT a moment-and-place.**
The ``jd``, ``lat``, and ``lon`` fields on the composite CHART_DTYPE
output are stored as linear (jd, lat) and circular (lon) midpoints of
the two natals for round-trip consistency. They have NO astronomical
interpretation as "the moment-and-place of the composite" — that
interpretation requires Davison, which is out of scope.

**UTC-only contract — LOUD.** Both ``chart_a`` and ``chart_b`` MUST
have been computed with UTC Julian Dates. Time-zone conversion is the
caller's responsibility; mixing local-time charts will produce
incorrect midpoints with no error signal.
"""
from __future__ import annotations

from .api import calculate_composite
from .core import circular_midpoint

__all__ = ["calculate_composite", "circular_midpoint"]
