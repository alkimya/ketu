"""
Public compute surface for the declination aspects subpackage.

Provides :func:`find_declination_aspects` — the scalar detector that takes
a ``(14,)`` signed-declination array (``chart["body_decl"]`` from
:data:`ketu.charts.CHART_DTYPE`) and returns a structured array of
:data:`DECLA_ASPECT_DTYPE` rows, one row per detected parallel or
contra-parallel aspect.

Design notes
------------
- **Fully vectorized internally**: uses :func:`numpy.triu_indices` to enumerate
  all 91 upper-triangle body pairs without a Python loop over bodies.
- **Single unified return**: parallels (``kind="P"``) and contra-parallels
  (``kind="CP"``) are mixed in one array, distinguished by the ``kind`` field.
- **Empty-result contract**: returns ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)``
  when no aspects are found — never ``None``, never a ``(parallels, contras)``
  tuple.
- **Upper-triangle only**: ``body1 < body2`` always (by construction from
  :func:`numpy.triu_indices` with ``k=1``).
- **Output order**: rows sorted ascending by ``(body1, body2)`` pair index,
  regardless of P/CP interleaving.

See Also
--------
ketu.charts.compute_chart : Computes the CHART_DTYPE record whose
    ``body_decl`` field is the input to :func:`find_declination_aspects`.
ketu.declination.core.DECLA_ASPECT_DTYPE : Output dtype contract.
ketu.declination.core._ORB_MAT : Pre-computed per-pair orb limits.
"""
from __future__ import annotations

import numpy as np

from .core import DECLA_ASPECT_DTYPE, _ORB_MAT


def find_declination_aspects(body_decl: np.ndarray) -> np.ndarray:
    """Detect parallels and contra-parallels between 14 bodies on the δ axis.

    A **parallel** (``kind="P"``) occurs when two bodies have the same non-zero
    declination sign and their declinations are within the per-pair orb limit:
    ``sign(δ₁) == sign(δ₂) != 0`` and ``|δ₁ − δ₂| <= orb``.

    A **contra-parallel** (``kind="CP"``) occurs when two bodies have opposite
    non-zero signs and their absolute values sum within the per-pair orb limit:
    ``sign(δ₁) != sign(δ₂)``, both non-zero, and ``|δ₁ + δ₂| <= orb``.

    Bodies at exactly ``δ = 0`` participate in neither aspect type (zero-sign
    trap guard: ``sign(0) == 0``).

    Parameters
    ----------
    body_decl : np.ndarray
        Shape ``(14,)``, dtype ``float64`` (or compatible). Signed declinations
        in degrees for the 14 canonical bodies in :data:`ketu.core.bodies`
        order: ``[Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus,
        Neptune, Pluto, Rahu, Ketu, Lilith, Chiron]``. Typically sourced from
        ``chart["body_decl"]`` of a :data:`ketu.charts.CHART_DTYPE` scalar record.

    Returns
    -------
    np.ndarray
        Shape ``(K,)``, dtype :data:`ketu.declination.DECLA_ASPECT_DTYPE`.
        Each row is one detected aspect with fields ``body1``, ``body2``,
        ``kind``, ``gap``, ``orb``. Rows are sorted ascending by
        ``(body1, body2)`` pair index. ``body1 < body2`` always.
        Returns ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)`` when no aspects
        are detected — never ``None``, never a ``(parallels, contras)`` tuple.

    Notes
    -----
    The per-pair orb limit is pre-computed in :data:`ketu.declination.core._ORB_MAT`
    as ``max((orb_b1 + orb_b2) / 2 × DECLA_COEF, MIN_DECL_ORB)``. Sun/Moon
    yields ``1.0°``; Rahu/Lilith (both natal orb 0) hits the ``0.5°`` floor.

    The function enumerates all 91 upper-triangle pairs (14×13/2) via
    :func:`numpy.triu_indices` with ``k=1``, so ``body1 < body2`` is guaranteed
    by construction. No Python loop over bodies is used internally.

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.declination import find_declination_aspects
    >>> d = np.zeros(14)
    >>> d[0] = +15.0   # Sun north
    >>> d[1] = -15.0   # Moon south — contra-parallel
    >>> result = find_declination_aspects(d)
    >>> result["kind"][0]
    'CP'
    >>> d2 = np.zeros(14)
    >>> find_declination_aspects(d2).shape
    (0,)
    """
    idx_i, idx_j = np.triu_indices(14, k=1)              # (91,) each
    d1 = body_decl[idx_i]                                 # (91,)
    d2 = body_decl[idx_j]                                 # (91,)
    orb_pairs = _ORB_MAT[idx_i, idx_j]                    # (91,)
    gap_p  = np.abs(d1 - d2)
    gap_cp = np.abs(d1 + d2)
    s1 = np.sign(d1)
    s2 = np.sign(d2)
    mask_p  = (s1 == s2) & (s1 != 0) & (gap_p  <= orb_pairs)
    mask_cp = (s1 != s2) & (s1 != 0) & (s2 != 0) & (gap_cp <= orb_pairs)

    n_p  = int(np.sum(mask_p))
    n_cp = int(np.sum(mask_cp))
    total = n_p + n_cp

    if total == 0:
        return np.empty(0, dtype=DECLA_ASPECT_DTYPE)

    result = np.empty(total, dtype=DECLA_ASPECT_DTYPE)

    # Fill parallel rows
    result["body1"][:n_p] = idx_i[mask_p].astype(np.int8)
    result["body2"][:n_p] = idx_j[mask_p].astype(np.int8)
    result["kind"][:n_p]  = "P"
    result["gap"][:n_p]   = gap_p[mask_p]
    result["orb"][:n_p]   = orb_pairs[mask_p]

    # Fill contra-parallel rows
    result["body1"][n_p:] = idx_i[mask_cp].astype(np.int8)
    result["body2"][n_p:] = idx_j[mask_cp].astype(np.int8)
    result["kind"][n_p:]  = "CP"
    result["gap"][n_p:]   = gap_cp[mask_cp]
    result["orb"][n_p:]   = orb_pairs[mask_cp]

    # Sort ascending by (body1, body2) so output order is canonical
    sort_key = result["body1"].astype(np.int32) * 14 + result["body2"].astype(np.int32)
    order = np.argsort(sort_key, kind="stable")
    return result[order]


__all__ = [
    "find_declination_aspects",
]
