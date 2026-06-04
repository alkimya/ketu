"""Declination aspects subpackage — parallel and contra-parallel detection.

Public API surface (DECLA-01..03 of the v1.6 milestone — Plan 36-01):

- :func:`find_declination_aspects` — Detect parallels and contra-parallels
  between 14 bodies on the declination axis. Takes a ``(14,)`` signed-degree
  array (``chart["body_decl"]``) and returns a structured array of
  :data:`DECLA_ASPECT_DTYPE` rows. Returns ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)``
  when no aspects are detected — never ``None``, never a tuple.
- :data:`DECLA_ASPECT_DTYPE` — Structured-array layout for ONE declination
  aspect record (5 fields, frozen contract): ``body1``, ``body2``, ``kind``,
  ``gap``, ``orb``.
- :data:`DECLA_COEF` — Orb scaling coefficient ``1/12`` applied to the per-body
  natal orb on the declination axis.
- :data:`MIN_DECL_ORB` — Minimum orb floor ``0.5°`` for declination aspect
  detection (keeps bodies with natal orb 0 detectable).

Notes
-----
**Sub-module exposure only.** :func:`find_declination_aspects` is accessible via
``ketu.declination.find_declination_aspects`` but is NOT re-exported from the
top-level ``ketu`` package (``ketu.__all__`` is unchanged — additive-only design).

**CHART_DTYPE unchanged.** This subpackage is a purely additive companion to the
v1.5 declination infrastructure. :data:`ketu.charts.CHART_DTYPE` is not modified;
the ``body_decl`` field (shape ``(14,)``) shipped in v1.5 is the sole input.

**Body axis (14 bodies).** Indices 0..13 from :data:`ketu.core.bodies`::

    0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
    7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu, 11=Ketu, 12=Lilith, 13=Chiron.

See Also
--------
ketu.charts.compute_chart : Computes CHART_DTYPE (source of ``body_decl``).
ketu.calculations.declination : Per-body declination scalar computation.
"""
from __future__ import annotations

from .api import find_declination_aspects
from .core import DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB

__all__ = [
    "DECLA_ASPECT_DTYPE",
    "DECLA_COEF",
    "MIN_DECL_ORB",
    "find_declination_aspects",
]
