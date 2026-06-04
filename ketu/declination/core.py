"""
Core types for the declination aspects subpackage.

Defines :data:`DECLA_ASPECT_DTYPE`, the structured-array layout for ONE
declination aspect record between two bodies (parallel or contra-parallel),
:data:`DECLA_COEF` and :data:`MIN_DECL_ORB` constants, and the frozen
precomputed 14x14 orb matrix :data:`_ORB_MAT`.

Notes
-----
Why a structured array?
~~~~~~~~~~~~~~~~~~~~~~~

The ``ketu/declination`` subpackage publishes :data:`DECLA_ASPECT_DTYPE` as a
NumPy structured dtype for the same reasons that govern :data:`ketu.synastry.SYNASTRY_DTYPE`
and :data:`ketu.charts.CHART_DTYPE`: ML-interop, batchability, and self-describing
rows. Every row carries its own ``(body1, body2, kind, gap, orb)`` so downstream
consumers never need to re-join with the parent chart.

Why 5 fields?
~~~~~~~~~~~~~

The declination aspect contract needs exactly the identity pair ``(body1, body2)``,
the kind discriminant ``kind`` (``"P"`` or ``"CP"``), the signed separation ``gap``
(``|δ₁ − δ₂|`` for parallels, ``|δ₁ + δ₂|`` for contra-parallels), and the
derived orb limit ``orb`` used for the detection. Five fields give a self-describing
row without bloat; no longitude or symbol field is needed on the δ axis.

Orb formula
~~~~~~~~~~~

Per-pair orb = ``max((orb_b1 + orb_b2) / 2 × DECLA_COEF, MIN_DECL_ORB)``.

:data:`DECLA_COEF` ``= 1/12`` applies the same relative tightening as the aspect
coefficient convention used across Ketu, scaled to the declination axis.
:data:`MIN_DECL_ORB` ``= 0.5°`` is a floor that keeps bodies with nominal orb 0
(Rahu, Ketu, Lilith — and Pluto/Chiron whose formula result is below the floor)
detectable.
"""
from __future__ import annotations

import numpy as np

from ketu.core import bodies as _BODIES

#: Declination orb coefficient applied to the per-body natal orb.
#:
#: Parallel and contra-parallel aspects on the δ axis are tighter than
#: longitudinal aspects. The factor ``1/12`` yields ``1.0°`` for Sun/Moon
#: (natal orb 12°) and ``0.5°`` (floor) for bodies with natal orb 0.
DECLA_COEF: float = 1.0 / 12.0

#: Minimum orb floor for declination aspect detection, in degrees.
#:
#: Bodies with nominal natal orb 0 (Rahu, Ketu, Lilith) would otherwise have
#: a computed orb of 0, making detection impossible. The floor of ``0.5°``
#: keeps those bodies detectable for tight declination aspects.
MIN_DECL_ORB: float = 0.5

#: Structured dtype for ONE declination aspect record.
#:
#: Fields (5 total):
#:     - ``body1`` (i1): index into :data:`ketu.core.bodies` [0..13], always ``body1 < body2``.
#:     - ``body2`` (i1): index into :data:`ketu.core.bodies` [0..13].
#:     - ``kind``  (U2): ``"P"`` (parallel — same non-zero sign) or ``"CP"`` (contra-parallel —
#:           opposite non-zero signs).
#:     - ``gap``   (f8): angular separation on the δ axis, in degrees.
#:           ``|δ₁ − δ₂|`` for parallels; ``|δ₁ + δ₂|`` for contra-parallels.
#:     - ``orb``   (f8): derived orb limit applied for this pair, in degrees.
#:           ``max((orb_b1 + orb_b2) / 2 × DECLA_COEF, MIN_DECL_ORB)``.
#:
#: Body axis order follows :data:`ketu.core.bodies`::
#:
#:     0=Sun, 1=Moon, 2=Mercury, 3=Venus, 4=Mars, 5=Jupiter, 6=Saturn,
#:     7=Uranus, 8=Neptune, 9=Pluto, 10=Rahu, 11=Ketu, 12=Lilith, 13=Chiron.
#:
#: Empty-result contract::
#:
#:     np.empty(0, dtype=DECLA_ASPECT_DTYPE)  # never None, never a tuple
DECLA_ASPECT_DTYPE: np.dtype = np.dtype([
    ("body1", "i1"),   # core.bodies index 0-13, body1 < body2
    ("body2", "i1"),
    ("kind",  "U2"),   # "P" (parallel) or "CP" (contra-parallel)
    ("gap",   "f8"),   # |d1-d2| for P, |d1+d2| for CP, degrees
    ("orb",   "f8"),   # derived orb limit used for this pair, degrees
])


def _build_orb_matrix() -> np.ndarray:
    """Build and freeze the 14x14 per-pair orb limit matrix.

    Computes ``max((orb_b1 + orb_b2) / 2 × DECLA_COEF, MIN_DECL_ORB)`` for
    every ordered pair of the 14 canonical bodies using :func:`numpy.add.outer`,
    then makes the result read-only.

    Returns
    -------
    np.ndarray
        Shape ``(14, 14)``, dtype ``float64``, read-only. Entry ``[i, j]`` is
        the orb limit (in degrees) for the body pair ``(i, j)``.
    """
    orbs = _BODIES["orb"].astype(np.float64)            # (14,), cast f4->f8
    mat = np.maximum(np.add.outer(orbs, orbs) / 2.0 * DECLA_COEF, MIN_DECL_ORB)
    mat.flags.writeable = False                          # freeze
    return mat


#: Frozen 14x14 per-pair orb limit matrix, dtype float64.
#:
#: Pre-computed at module load time from :data:`ketu.core.bodies` orbs.
#: ``_ORB_MAT[i, j]`` is the orb limit in degrees for body pair ``(i, j)``.
#: Read-only (``flags.writeable = False``).
_ORB_MAT: np.ndarray = _build_orb_matrix()              # (14,14) f8, module-level constant


__all__ = [
    "DECLA_ASPECT_DTYPE",
    "DECLA_COEF",
    "MIN_DECL_ORB",
    "_ORB_MAT",
]
