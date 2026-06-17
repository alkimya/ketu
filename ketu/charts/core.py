"""
Core types for the charts subpackage.

Defines :data:`CHART_DTYPE`, the structured-array layout for a fully-resolved
natal chart (positions + ASC/MC/ARMC/Vertex + cusps + aspects). The dtype is
the contractual heart of Phase 14: every downstream consumer (synastry,
composite, solar return, Arabic Parts) reads charts via this layout.

Notes
-----

Why a structured array?
~~~~~~~~~~~~~~~~~~~~~~~

The ``ketu/charts`` subpackage publishes :data:`CHART_DTYPE` as a NumPy
structured dtype rather than a Python ``@dataclass`` or a flat
``dict[str, np.ndarray]``. Four reasons drove the choice (Phase 14
Option A, locked in PROJECT.md and CONTEXT.md D-01):

1. **ML-interop, NumPy-first.** The downstream ML consumer indexes each
   chart positionally — ``chart["body_lons"][i]`` for body ``i`` of the
   canonical 13-body axis. The axis order is FROZEN by D-08 so that
   adapters never need to rebuild mappings.
2. **Batchability.** A single ``np.empty(S, dtype=CHART_DTYPE)`` allocation
   carries S charts as one contiguous buffer. Compared to S Python
   dataclass instances, allocation is roughly two orders of magnitude
   faster and the result is natively ``np.save`` / ``np.load``-friendly,
   ``np.concatenate``-friendly, and ``mmap``-friendly.
3. **Self-describing.** Every chart carries its own ``(jd, lat, lon,
   system)`` (D-04). Synastry (Phase 16), composite (Phase 17), solar
   return (Phase 18), and Parts (Phase 19) consume charts without
   transporting their context separately, eliminating a class of
   "lost context" bugs.
4. **Inline houses, not nested (D-03).** The houses portion of the chart
   is inlined as scalar / short-subarray fields (``cusps``, ``asc``,
   ``mc``, ``armc``, ``vertex``) rather than nested as a
   ``("houses", HOUSES_DTYPE)`` field. The nesting would add an
   indirection level for zero ML-interop benefit; values are scalars or
   length-12 subarrays already.

The same NumPy-first reasoning applies inside Ketu (CYCLE_DTYPE,
HOUSES_DTYPE) — CHART_DTYPE follows the established precedent.
"""
from __future__ import annotations

import numpy as np

#: Structured dtype for a fully-resolved natal chart.
#:
#: Fields (16 total, ordered as metadata -> bodies -> houses -> aspects):
#:     - ``jd`` (f8): Julian Date, UT.
#:     - ``lat`` (f8): Geographic latitude, degrees.
#:     - ``lon`` (f8): Geographic longitude (east-positive), degrees.
#:     - ``system`` (U10): House system requested (e.g. "placidus").
#:     - ``body_lons`` (f8, (14,)): Ecliptic longitudes per body, degrees [0, 360).
#:     - ``body_lats`` (f8, (14,)): Ecliptic latitudes per body, degrees.
#:     - ``body_speeds`` (f8, (14,)): Longitude speeds per body, deg/day.
#:           Negative => retrograde.
#:     - ``body_decl`` (f8, (14,)): Equatorial declination δ per body, degrees,
#:           in [−90, +90]. North positive, south negative. Computed from each
#:           body's ecliptic (λ, β) via the coordinates chain using instantaneous
#:           obliquity ε(jd) (true_obliquity).
#:     - ``body_decl_speed`` (f8, (14,)): Equatorial declination velocity dδ/dt
#:           per body, in deg/day. Positive = northward (montant), negative =
#:           southward (descendant). Computed via forward finite difference at
#:           Δt=0.01 day (package-wide FD idiom). Use the sign for montant /
#:           descendant sense; compare |value| against
#:           :data:`ketu.calculations.DECL_STANDSTILL_EPS` for neutral
#:           classification. Added additively by v1.8 (DSPD-01, DSPD-04).
#:     - ``cusps`` (f8, (12,)): 12 house cusps, degrees [0, 360).
#:     - ``asc`` (f8): Ascendant, degrees [0, 360).
#:     - ``mc`` (f8): Medium Coeli, degrees [0, 360).
#:     - ``armc`` (f8): Right Ascension of MC, degrees [0, 360).
#:     - ``vertex`` (f8): Vertex, degrees [0, 360).
#:     - ``aspect_matrix`` (i1, (14, 14)): canonical aspect index in
#:           ``[0, 13]``; ``-1`` means "no aspect"; symmetric
#:           (``matrix[i, j] == matrix[j, i]``); diagonal == ``-1``
#:           (a body has no aspect with itself).
#:     - ``aspect_orbs`` (f4, (14, 14)): **signed** orb in degrees;
#:           ``aspect_angle - distance`` (positive when ``distance <
#:           aspect_angle``, negative when ``distance > aspect_angle``);
#:           ``NaN`` means "no orb" (matches ``aspect_matrix == -1``);
#:           symmetric; diagonal == ``NaN``. Inherits the sign convention
#:           from :func:`ketu.aspects.calculator.calculate_aspects_vectorized`.
#:           For absolute-orb filters use ``np.abs(chart["aspect_orbs"])``.
#:
#: Caller mask one-liner:
#:     ``mask = chart["aspect_matrix"] >= 0``  # or
#:     ``~np.isnan(chart["aspect_orbs"])``
#:
#: Body axis order (the (14,) axis) follows :data:`ketu.core.bodies`:
#:     0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
#:     7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu, 11=Ketu, 12=Lilith,
#:     13=Chiron.
#:
#: Axis extended to 14 by the v1.3 D-08 ratchet (Chiron added). This is
#: a breaking change for downstream consumers indexing by position.
#: The ``body_decl`` field was appended additively by v1.5 (lunar
#: declination). The ``body_decl_speed`` field was appended additively by
#: v1.8 (dδ/dt, deg/day; DSPD-01, DSPD-04). The body COUNT stays 14;
#: each addition is a dtype-version bump (new field), not an axis change.
#: Downstream positional-offset / ``.view()`` consumers must adapt after
#: each dtype bump — documented, not fixed here.
CHART_DTYPE: np.dtype = np.dtype([
    ("jd",              "f8"),
    ("lat",             "f8"),
    ("lon",             "f8"),
    ("system",          "U10"),
    ("body_lons",       "f8", (14,)),
    ("body_lats",       "f8", (14,)),
    ("body_speeds",     "f8", (14,)),
    ("body_decl",       "f8", (14,)),
    ("body_decl_speed", "f8", (14,)),   # v1.8: dδ/dt in deg/day (DSPD-01)
    ("cusps",           "f8", (12,)),
    ("asc",             "f8"),
    ("mc",              "f8"),
    ("armc",            "f8"),
    ("vertex",          "f8"),
    ("aspect_matrix",   "i1", (14, 14)),
    ("aspect_orbs",     "f4", (14, 14)),
])
