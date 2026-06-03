"""
Dynamic harmonic aspect generator.

Provides :func:`generate_harmonic_aspects` which emits aspect specs for **any**
integer harmonic ``h`` using the locked unified 360° convention.  The output
dtype is byte-for-byte identical to :data:`ketu.core.aspects`, making it a
drop-in source for every consumer that iterates over ``core.aspects``.

This module is **entirely independent** of :mod:`ketu.aspects.presets`.  It
does not import or call ``aspects_for_harmonics``, ``resolve_aspect_set``, or
``_VALID_HARMONICS`` (those APIs would reject ``h=7/11/17`` with
:exc:`ValueError`).  The frozen 14-row table is never mutated.

Notes
-----
Public symbols:

- :data:`HARMONIC_DTYPE` — dtype mirroring ``core.aspects``.
- :data:`DynamicAspectSpec` — type alias for the ``dynamic_specs=`` parameter
  threaded through all consumers (Plans 02/03).
- :func:`_fold_to_0_180` — maps any angle into the closed [0°, 180°] range.
- :func:`generate_harmonic_aspects` — public generator for harmonic ``h``.

Requirements satisfied: ASP-04 (public generator for any integer ``h``),
ASP-05 (unified 360° convention — fold, mirror-dedup, no 0°/360°, blank symbol),
ASP-08 (frozen ``core.aspects`` table untouched; ``_VALID_HARMONICS`` never
consulted on the dynamic path).
"""
from __future__ import annotations

from typing import List, Optional, Union

import numpy as np
import numpy.typing as npt

# ---------------------------------------------------------------------------
# Drop-in dtype — MUST exactly mirror ketu/core.py:113
# ---------------------------------------------------------------------------

#: Structured array dtype for dynamic aspect specs.
#:
#: Identical to ``ketu.core.aspects.dtype`` so any consumer of the frozen
#: table can also accept generator output without dtype conversion.
HARMONIC_DTYPE = np.dtype(
    [
        ("name", "S16"),
        ("angle", "f4"),
        ("coef", "f4"),
        ("harmonic", "i4"),
        ("symbol", "U4"),
    ]
)

# ---------------------------------------------------------------------------
# Type alias for the dynamic_specs parameter (Plans 02/03)
# ---------------------------------------------------------------------------

#: Type alias for the ``dynamic_specs=`` parameter accepted by all consumers
#: (:func:`~ketu.aspects.calculator.calculate_aspects`,
#: :func:`~ketu.aspects.calculator.find_aspects_between_dates`,
#: :func:`~ketu.aspects.calculator.calculate_synastry`, etc.).
#:
#: Accepts a **single** structured array (as returned by
#: :func:`generate_harmonic_aspects`) **or** a ``list`` of such arrays
#: (consumers concatenate them with ``np.concatenate``).  ``None`` disables
#: dynamic detection.
DynamicAspectSpec = Optional[Union[npt.NDArray[np.void], List[npt.NDArray[np.void]]]]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fold_to_0_180(angle_deg: float) -> float:
    """
    Fold any angle into the closed range [0°, 180°].

    Implements the locked 360° convention: ``min(a % 360, 360 - a % 360)``.
    Both 0° and 180° are valid outputs (they correspond to the conjunction and
    opposition poles of the half-circle).  The full-circle mirror pair
    ``(k·360/h, (h-k)·360/h)`` folds to the same value, which is how
    :func:`generate_harmonic_aspects` achieves mirror deduplication.

    Parameters
    ----------
    angle_deg : float
        Input angle in degrees.  Any real value is accepted; the modulo
        operation normalises it to ``[0°, 360°)`` first.

    Returns
    -------
    float
        Angle in ``[0°, 180°]``.

    Examples
    --------
    >>> _fold_to_0_180(51.43)
    51.43
    >>> round(_fold_to_0_180(308.57), 10)  # mirror of 51.43
    51.43
    >>> round(_fold_to_0_180(360.0), 6)
    0.0
    >>> _fold_to_0_180(180.0)
    180.0
    >>> _fold_to_0_180(270.0)
    90.0
    """
    a = angle_deg % 360.0
    return a if a <= 180.0 else 360.0 - a


# ---------------------------------------------------------------------------
# Public generator
# ---------------------------------------------------------------------------


def generate_harmonic_aspects(h: int) -> npt.NDArray[np.void]:
    """
    Generate aspect specs for integer harmonic *h*.

    Returns a structured array with :data:`HARMONIC_DTYPE` (identical to
    ``ketu.core.aspects.dtype``) containing one row per unique folded angle
    ``fold_to_0_180(k·360/h)`` for ``k = 1 … h//2``.

    Parameters
    ----------
    h : int
        Harmonic number.  Must satisfy ``2 <= h <= 64``.  ``bool`` values are
        rejected explicitly (``bool`` is a subclass of ``int`` in Python).
        ``h = 1`` is excluded because it would produce 0 rows (``1 // 2 = 0``),
        which is degenerate.  ``h > 64`` is excluded because the resulting orbs
        (``coef = k/h`` with small ``k``) are impractically small for typical
        planetary orb tables.

    Returns
    -------
    np.ndarray
        Structured array with dtype :data:`HARMONIC_DTYPE` and shape
        ``(h // 2,)``.

    Raises
    ------
    ValueError
        If ``h`` is a ``bool``, not an ``int``, or outside ``[2, 64]``.

    Notes
    -----
    Convention (locked, 360° unified):

    - Angle  : ``fold_to_0_180(k · 360 / h)`` — values in ``(0°, 180°]``.
    - Coef   : ``k / h`` — used as the orb-scaling factor by consumers.
    - Name   : ``b'H{h}-{k}'`` (byte string, field width S16).
    - Harmonic: ``h`` (the input integer).
    - Symbol : ``''`` (blank U4 — same convention as the 7 minor aspects in
      the frozen table).

    Guarantees:

    - ``0°`` and ``360°`` are **never** emitted (``k`` starts at 1 and stops
      before ``k = h``, so the conjunction/full-circle poles are excluded).
    - Mirror pairs **deduplicated**: only ``k = 1 … h//2``; the fold maps
      ``k·360/h`` and ``(h-k)·360/h`` to the same angle, so we emit it once.
    - Deterministic row ordering by ``k``.
    - The frozen ``core.aspects`` table is **never imported or mutated**.
    - ``_VALID_HARMONICS`` / ``aspects_for_harmonics`` are **never** called;
      this function accepts any valid ``h`` including 7, 11, 17, etc.

    Examples
    --------
    >>> specs = generate_harmonic_aspects(7)
    >>> len(specs)
    3
    >>> specs['name'].tolist()
    [b'H7-1', b'H7-2', b'H7-3']
    >>> [round(float(a), 2) for a in specs['angle']]
    [51.43, 102.86, 154.29]
    >>> [round(float(c), 4) for c in specs['coef']]
    [0.1429, 0.2857, 0.4286]
    >>> specs['symbol'].tolist()
    ['', '', '']
    """
    # --- Validate h (mirror presets.py lines 165-168 pattern) ---------------
    # bool is a subclass of int; reject explicitly to avoid silently accepting
    # True (1) or False (0) as harmonic numbers.
    if isinstance(h, bool):
        raise ValueError(
            f"invalid harmonic {h!r}: bool is not accepted as an int "
            "(pass an explicit integer, e.g. generate_harmonic_aspects(2))"
        )
    if not isinstance(h, (int, np.integer)):
        raise ValueError(
            f"invalid harmonic {h!r}: expected int, got {type(h).__name__}"
        )
    h = int(h)
    if not (2 <= h <= 64):
        raise ValueError(
            f"harmonic {h} out of range: must satisfy 2 <= h <= 64 "
            "(h=1 produces no rows; h>64 yields impractically small orbs)"
        )

    # --- Build rows ----------------------------------------------------------
    rows: list[tuple[bytes, float, float, int, str]] = []
    for k in range(1, h // 2 + 1):
        angle = _fold_to_0_180(k * 360.0 / h)
        coef = k / h
        name = f"H{h}-{k}".encode()  # S16 stores bytes
        rows.append((name, angle, coef, h, ""))

    return np.array(rows, dtype=HARMONIC_DTYPE)


__all__ = [
    "generate_harmonic_aspects",
    "HARMONIC_DTYPE",
    "DynamicAspectSpec",
    "_fold_to_0_180",
]
