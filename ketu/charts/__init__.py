"""Chart abstraction subpackage — fully-resolved natal charts in one call.

Public API surface (CHART-01 of the v1.2 milestone):

- :func:`compute_chart` — Compute a fully-resolved natal chart (positions,
  ASC/MC/ARMC/Vertex, cusps, intra-chart aspects) in one vectorisable call.
- :func:`is_day_chart` — Sect helper. ``True`` when the Sun is at or
  above the horizon (sunrise inclusive); polar-safe via internal
  Porphyry fallback.
- :data:`CHART_DTYPE` — Structured-array layout for chart results.

See Also
--------
ketu.houses.calculate_houses : House cusps used internally by
    :func:`compute_chart`.
ketu.aspects.calculate_aspects_vectorized : Aspect engine projected into
    ``aspect_matrix``.
ketu.synastry.calculate_synastry : Inter-chart aspect computation
    consuming two CHART_DTYPE records (Phase 16).
ketu.composite.calculate_composite : Derive a midpoint composite
    chart from two CHART_DTYPE records (Phase 17).

Notes
-----
``ketu.charts`` is composition only — it does not introduce new
astronomical math. The ``CHART_DTYPE`` body axis ``(13,)`` is FROZEN
per decision D-08 (Kala positional contract); adding Chiron is a
v1.3 BREAKING change. The ``polar_fallback`` parameter on
:func:`compute_chart` is a pass-through to
:func:`ketu.houses.calculate_houses` per decision D-11.

Examples
--------
>>> from ketu.charts import compute_chart, is_day_chart, CHART_DTYPE
>>> import numpy as np
>>> jd = np.array([2451545.0, 2470204.0])
>>> lat = np.array([48.86, 64.15])
>>> lon = np.array([2.35, -21.94])
>>> chart = compute_chart(jd, lat, lon, polar_fallback="porphyry")  # doctest: +SKIP
>>> chart.shape, chart["body_lons"].shape, chart["aspect_matrix"].shape  # doctest: +SKIP
((2,), (2, 13), (2, 13, 13))
"""
from __future__ import annotations

from .api import compute_chart, is_day_chart
from .core import CHART_DTYPE

__all__ = [
    "CHART_DTYPE",
    "compute_chart",
    "is_day_chart",
]
