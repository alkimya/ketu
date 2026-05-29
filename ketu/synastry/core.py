"""
Core types for the synastry subpackage.

Defines :data:`SYNASTRY_DTYPE`, the structured-array layout for ONE inter-chart
aspect record between two natal charts, and :data:`SYNASTRY_BODY_COUNT`, the
size of the synastry body axis (14 canonical bodies + ASC + MC = 16).

Notes
-----

Why a structured array?
~~~~~~~~~~~~~~~~~~~~~~~

The ``ketu/synastry`` subpackage publishes :data:`SYNASTRY_DTYPE` as a NumPy
structured dtype rather than a Python ``@dataclass``, a flat
``dict[str, np.ndarray]``, or a 2-D ``(16, 16)`` axis-style matrix. The
reasoning mirrors the Phase 14 precedent locked in
``ketu/charts/core.py`` (D-01, D-08) and the v1.0 ``CYCLE_DTYPE``
precedent:

1. **ML-interop, NumPy-first.** Kala (the downstream ML consumer) indexes
   inter-chart aspects positionally — ``rec["body_a"]``, ``rec["body_b"]``,
   ``rec["orb"]``. The body axis order is FROZEN by the same D-08 contract
   that pins ``CHART_DTYPE``; synastry indices 0..12 reuse
   ``ketu.core.bodies`` and indices 13..14 stand for ASC and MC.
2. **Batchability.** A single ``np.empty(N, dtype=SYNASTRY_DTYPE)``
   allocation carries N inter-chart aspect rows as one contiguous buffer.
   ``np.concatenate``-friendly and ``mmap``-friendly out of the box.
3. **Self-describing.** Every row carries its own ``(body_a, body_b,
   lon_a, lon_b, aspect_type, orb, applying, orb_limit)``. Downstream
   consumers never need to look up the parent charts to filter or rank
   aspects.
4. **Record-style, not axis-style (D-rec).** A ``(16, 16)`` matrix layout
   was rejected: the dense mode (all 256 pairs) and the filtered mode
   (orbed pairs only) must share ONE schema so that downstream code
   doesn't branch on shape. A record-style structured array gives both
   modes the same dtype — dense fills the 256 rows with ``aspect_type
   = -1`` and ``orb = NaN`` sentinels; filtered ships only the orbed
   rows. The 2-D axis style would force a different schema per mode.

Why 8 fields, not 5 or 12?
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ROADMAP success criterion #1 mandates 5 fields (``body_a, body_b,
aspect_type, orb, applying``). We extend to 8 to make rows
**auto-sufficient** — a downstream consumer (a Kala feature pipeline, a
JSON dump, a UI table) needs the longitudes ``lon_a`` and ``lon_b`` to
render the aspect glyph at the correct degree, and the ``orb_limit``
that was applied to decide the row was orbed. Without those 3 metadata
fields, every consumer would have to re-join with the parent
``CHART_DTYPE`` records, defeating the self-describing benefit (point 3
above). Going beyond 8 (e.g. a 12-field schema with `applying_speed`,
`exactness_score`, `cycle_phase`) hits diminishing returns and bloats
memory for ML batch use; those derived quantities are cheap to compute
on the fly. 8 fields is the locked floor for v1.2.
"""
from __future__ import annotations

import numpy as np

#: Number of bodies in the synastry body axis.
#:
#: 14 canonical (per :data:`ketu.charts.core.CHART_DTYPE`, body order per
#: D-08 ratchet v1.3 — Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
#: Uranus, Neptune, Pluto, Rahu, Ketu, Lilith, Chiron) + ASC + MC = 16.
#: Extended to 16 by the v1.3 D-08 ratchet (Chiron added as body 13;
#: ASC shifts to index 14, MC to index 15).
SYNASTRY_BODY_COUNT: int = 16

#: Structured dtype for ONE synastry aspect record.
#:
#: Fields (8 total, ordered as identity -> values -> metadata):
#:     - ``body_a`` (i1): chart-A body index, [0..15].
#:           0..13 = :data:`ketu.core.bodies` order; 14 = ASC, 15 = MC.
#:     - ``body_b`` (i1): chart-B body index, [0..15]. Same axis as ``body_a``.
#:     - ``lon_a`` (f8): chart-A body ecliptic longitude, degrees in [0, 360).
#:     - ``lon_b`` (f8): chart-B body ecliptic longitude, degrees in [0, 360).
#:     - ``aspect_type`` (i1): canonical aspect index [0..13] per
#:           :data:`ketu.core.aspects`, OR ``-1`` for "no aspect" (dense-mode
#:           sentinel). The ``i1`` range [-128, 127] holds the sentinel safely.
#:     - ``orb`` (f4): signed orb in degrees, ``aspect_angle - distance``;
#:           ``NaN`` when ``aspect_type == -1``. Inherits the sign convention
#:           from :func:`ketu.aspects.calculator.calculate_aspects_vectorized`
#:           (Phase 14 D-06 sentinel pattern).
#:     - ``applying`` (?): ``True`` when the aspect is applying under the
#:           static-natal-speed convention, ``False`` when separating.
#:           Always ``False`` when ``aspect_type == -1``.
#:     - ``orb_limit`` (f4): tolerance threshold applied (post-factor synastry
#:           orb, in degrees); ``NaN`` when ``aspect_type == -1``.
#:
#: Caller mask one-liner::
#:
#:     mask = recs["aspect_type"] >= 0  # or
#:     mask = ~np.isnan(recs["orb"])
#:
#: Body axis order (the 16-body axis) follows :data:`ketu.core.bodies`
#: extended with ASC and MC::
#:
#:     0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
#:     7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu, 11=Ketu, 12=Lilith,
#:     13=Chiron, 14=ASC, 15=MC.
#:
#: D-08 (v1.3) moved the canonical body axis 13->14 (Chiron added as body
#: 13), widening this synastry axis 15->16. The prior 13-body freeze is
#: intentionally broken (Kala adapts to Ketu).
SYNASTRY_DTYPE: np.dtype = np.dtype([
    ("body_a",      "i1"),
    ("body_b",      "i1"),
    ("lon_a",       "f8"),
    ("lon_b",       "f8"),
    ("aspect_type", "i1"),
    ("orb",         "f4"),
    ("applying",    "?"),
    ("orb_limit",   "f4"),
])


__all__ = [
    "SYNASTRY_BODY_COUNT",
    "SYNASTRY_DTYPE",
]
