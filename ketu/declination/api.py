"""
Public compute surface for the declination aspects subpackage.

Provides two functions:

- :func:`find_declination_aspects` — scalar detector taking a ``(14,)``
  signed-declination array (``chart["body_decl"]`` from
  :data:`ketu.charts.CHART_DTYPE`) and returning a structured array of
  :data:`DECLA_ASPECT_DTYPE` rows.
- :func:`declination_aspect_masks` — vectorized batch detector taking a
  ``(S, 14)`` array (or ``(14,)`` for a single chart) and returning a
  :class:`DeclinationAspectMasks` NamedTuple of parallel/contra bool masks
  and gap arrays, all ``(S, 91)`` shaped, built via pure broadcasting on the
  precomputed 14x14 orb matrix from :mod:`ketu.declination.core`.

Design notes
------------
- **Fully vectorized internally**: both functions use :func:`numpy.triu_indices`
  to enumerate all 91 upper-triangle body pairs without a Python loop over bodies.
- **Single unified return (scalar)**: parallels (``kind="P"``) and
  contra-parallels (``kind="CP"``) are mixed in one array, distinguished by the
  ``kind`` field.
- **Empty-result contract (scalar)**: returns ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)``
  when no aspects are found — never ``None``, never a ``(parallels, contras)``
  tuple.
- **Upper-triangle only**: ``body1 < body2`` always (by construction from
  :func:`numpy.triu_indices` with ``k=1``).
- **Output order (scalar)**: rows sorted ascending by ``(body1, body2)`` pair
  index, regardless of P/CP interleaving.
- **Batch broadcasting**: :func:`declination_aspect_masks` uses
  ``_ORB_MAT[idx_i, idx_j]`` fancy-indexing once (not rebuilt) then broadcasts
  ``(S, 91)`` arrays against the ``(91,)`` orb vector — no Python body loop.

See Also
--------
ketu.charts.compute_chart : Computes the CHART_DTYPE record whose
    ``body_decl`` field is the input to both functions.
ketu.declination.core.DECLA_ASPECT_DTYPE : Output dtype contract (scalar path).
ketu.declination.core._ORB_MAT : Pre-computed per-pair orb limits.
"""
from __future__ import annotations

from typing import NamedTuple

import numpy as np

from .core import DECLA_ASPECT_DTYPE, _ORB_MAT


class DeclinationAspectMasks(NamedTuple):
    """Vectorized declination-aspect detection result over S charts.

    Fields are aligned on the 91 upper-triangle body pairs from
    ``np.triu_indices(14, k=1)`` (pair p maps to bodies ``idx_i[p]`` <
    ``idx_j[p]``).

    Attributes
    ----------
    parallel : np.ndarray
        Shape ``(S, 91)``, dtype ``bool``. True where same non-zero sign and
        ``|δ₁ − δ₂| <= orb``.
    contra : np.ndarray
        Shape ``(S, 91)``, dtype ``bool``. True where opposite non-zero signs
        and ``|δ₁ + δ₂| <= orb``.
    gap : np.ndarray
        Shape ``(S, 91)``, dtype ``float64``. Per-pair minimum of
        ``|δ₁ − δ₂|`` and ``|δ₁ + δ₂|`` (the tighter separation).
    idx_i : np.ndarray
        Shape ``(91,)``, dtype ``intp``. First body index of each pair (from
        ``np.triu_indices(14, k=1)[0]``). Always ``idx_i[p] < idx_j[p]``.
    idx_j : np.ndarray
        Shape ``(91,)``, dtype ``intp``. Second body index of each pair (from
        ``np.triu_indices(14, k=1)[1]``).
    orb_pairs : np.ndarray
        Shape ``(91,)``, dtype ``float64``. Per-pair orb limit extracted from
        ``_ORB_MAT[idx_i, idx_j]``.
    """

    parallel: np.ndarray    # (S, 91) bool — same non-zero sign & |d1-d2| <= orb
    contra: np.ndarray      # (S, 91) bool — opposite non-zero signs & |d1+d2| <= orb
    gap: np.ndarray         # (S, 91) f8 — min(|d1-d2|, |d1+d2|) per pair
    idx_i: np.ndarray       # (91,) int — first body index of each pair
    idx_j: np.ndarray       # (91,) int — second body index of each pair
    orb_pairs: np.ndarray   # (91,) f8 — per-pair orb limit (_ORB_MAT[idx_i, idx_j])


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


def declination_aspect_masks(body_decl: np.ndarray) -> DeclinationAspectMasks:
    """Detect parallels and contra-parallels across S charts via pure broadcasting.

    Accepts either a single ``(14,)`` chart or a batch ``(S, 14)`` array and
    returns a :class:`DeclinationAspectMasks` NamedTuple whose ``parallel``
    and ``contra`` masks have shape ``(S, 91)`` — one column per upper-triangle
    body pair from ``np.triu_indices(14, k=1)``.

    The hot path uses only NumPy broadcasting (no Python loop over the 14
    bodies or 91 pairs): ``_ORB_MAT[idx_i, idx_j]`` is fancy-indexed once to
    produce a ``(91,)`` orb vector, then broadcast against the ``(S, 91)``
    gap arrays.

    Parameters
    ----------
    body_decl : np.ndarray
        Shape ``(S, 14)`` or ``(14,)``, dtype ``float64`` (or compatible).
        Signed declinations in degrees for the 14 canonical bodies in
        :data:`ketu.core.bodies` order. A ``(14,)`` input is promoted to
        ``(1, 14)`` via :func:`numpy.atleast_2d`.

    Returns
    -------
    DeclinationAspectMasks
        NamedTuple with six fields:

        - ``parallel``: ``(S, 91)`` bool mask — pair is a parallel aspect.
        - ``contra``: ``(S, 91)`` bool mask — pair is a contra-parallel aspect.
        - ``gap``: ``(S, 91)`` float64 — ``min(|δ₁−δ₂|, |δ₁+δ₂|)`` per pair.
        - ``idx_i``: ``(91,)`` intp — first body index of each pair.
        - ``idx_j``: ``(91,)`` intp — second body index of each pair.
        - ``orb_pairs``: ``(91,)`` float64 — ``_ORB_MAT[idx_i, idx_j]``.

    Notes
    -----
    Use :func:`find_declination_aspects` when you need the structured-array
    row format (body names + kind + gap + orb) for a single chart. Use
    :func:`declination_aspect_masks` when you need fast per-pair bool masks
    over multiple charts (e.g. time-series scanning or ML pipelines).

    The pairs encoded in ``idx_i`` / ``idx_j`` are identical to
    ``np.triu_indices(14, k=1)`` and are the same for every call (they only
    depend on the fixed body count of 14).

    Examples
    --------
    >>> import numpy as np
    >>> from ketu.declination import declination_aspect_masks
    >>> d = np.zeros((3, 14))
    >>> r = declination_aspect_masks(d)
    >>> r.parallel.shape
    (3, 91)
    >>> r.contra.shape
    (3, 91)
    >>> r.idx_i.shape
    (91,)
    >>> # Single (14,) chart is accepted and promoted to (1, 91) masks:
    >>> declination_aspect_masks(np.zeros(14)).parallel.shape
    (1, 91)
    """
    idx_i, idx_j = np.triu_indices(14, k=1)               # (91,) each
    orb_pairs = _ORB_MAT[idx_i, idx_j]                    # (91,) f8
    d = np.atleast_2d(body_decl)                           # (S, 14) — accept (14,) too
    d1 = d[:, idx_i]                                       # (S, 91)
    d2 = d[:, idx_j]                                       # (S, 91)
    gap_p  = np.abs(d1 - d2)
    gap_cp = np.abs(d1 + d2)
    s1 = np.sign(d1)
    s2 = np.sign(d2)
    parallel = (s1 == s2) & (s1 != 0) & (gap_p  <= orb_pairs)
    contra   = (s1 != s2) & (s1 != 0) & (s2 != 0) & (gap_cp <= orb_pairs)
    gap = np.minimum(gap_p, gap_cp)
    return DeclinationAspectMasks(parallel, contra, gap, idx_i, idx_j, orb_pairs)


__all__ = [
    "DeclinationAspectMasks",
    "declination_aspect_masks",
    "find_declination_aspects",
]
