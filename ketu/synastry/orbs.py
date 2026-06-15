"""
Orb formula, factor presets, and resolver for synastry calculations.

Implements the synastry orb-resolution surface for :mod:`ketu.synastry`:

- :data:`SYNASTRY_FACTOR` — Astrodienst-cited multiplicative factor (``0.5``).
- :data:`ASC_MC_NATAL_ORB_DEG` — Mid-tier natal-orb width (``8.0``) for ASC/MC.
- :data:`_BODY_ORBS_16` — Frozen 16-entry orb table (14 canonical + ASC + MC).
- :class:`OrbSetSpec` — Type alias for the resolver input (``None | str``).
- :func:`synastry_orb_limit` — Scalar orb computation for one body-pair + aspect.
- :data:`_PRESET_BY_NAME` — Internal preset registry (``synastry``, ``classical``).
- :func:`resolve_orb_set` — Public preset resolver (mirrors
  :func:`ketu.aspects.presets.resolve_aspect_set`).

Notes
-----
**Single source of truth.** The natal orb formula
``(orb_a + orb_b) / 2 * coef`` is the AUTHORITATIVE source — defined in
:func:`ketu.aspects.calculator.get_orb` (at line 50). Synastry tightening
is a multiplicative transformation OF that formula, NOT a parallel
hardcoded orb table. This avoids two-source-of-truth drift if the natal
orbs in :data:`ketu.core.bodies` are ever revised.

**v1.2 ships ONE preset** (``synastry``); ``classical`` accepts the natal
formula unchanged for expert comparison views (CONTEXT.md gives
discretion). v1.3 may add ``liz_greene`` per-aspect coefficients via
in-place dict extension.
"""
from __future__ import annotations

from typing import Union

import numpy as np

from ketu.core import aspects as _ASPECTS, bodies as _BODIES


#: Multiplicative factor applied to the natal orb formula for synastry.
#:
#: Cited from Astrodienst (astro.com) FAQ "Partner horoscopes": "for drawing
#: aspects in a synastry chart, half the orb of the natal chart is used."
#: This is the single multiplicative source-of-truth for synastry tightening;
#: no parallel hardcoded orb table is maintained (per
#: ``.planning/phases/16-synastry/16-CONTEXT.md`` locked decision).
SYNASTRY_FACTOR: float = 0.5


#: Natal orb width assigned to ASC and MC for synastry, in degrees.
#:
#: ASC and MC are not present in :data:`ketu.core.bodies` (which lists only the
#: 13 ephemeris bodies); they live in :data:`ketu.charts.core.CHART_DTYPE` as
#: scalar ``asc`` / ``mc`` fields. We assign a mid-tier natal-orb default of
#: ``8.0`` here — matching the convention for Mercury / Mars / Uranus / Neptune
#: in :data:`ketu.core.bodies`. Halved by :data:`SYNASTRY_FACTOR` this yields
#: a 4.0 degree orb on ASC-planet conjunctions, matching astro.com practice.
ASC_MC_NATAL_ORB_DEG: float = 8.0


def _build_body_orbs_16() -> np.ndarray:
    """
    Build the frozen 16-entry orb table (14 canonical + ASC + MC).

    Returns
    -------
    np.ndarray
        Shape ``(16,)``, dtype ``np.float32``, ``writeable=False``.
        Entries 0..13 mirror :data:`ketu.core.bodies` ``["orb"]``;
        entries 14..15 are :data:`ASC_MC_NATAL_ORB_DEG`.
    """
    arr: np.ndarray = np.concatenate([
        _BODIES["orb"].astype(np.float32),                       # 14 canonical (incl. Chiron)
        np.array([ASC_MC_NATAL_ORB_DEG] * 2, dtype=np.float32),  # ASC(14), MC(15)
    ])  # shape (16,)
    arr.flags.writeable = False  # Frozen — accidental mutation raises ValueError
    return arr


#: Extended body-orb table for synastry — frozen 16-entry ``np.float32`` array.
#:
#: Indices 0..13 reuse :data:`ketu.core.bodies` natal orbs (incl. Chiron at 13);
#: indices 14..15 hold :data:`ASC_MC_NATAL_ORB_DEG` for ASC and MC. Computed once
#: at import time and pinned (``flags.writeable = False``) to ratchet against
#: accidental mutation by downstream callers. The ``float32`` dtype matches
#: :data:`ketu.core.bodies` ``["orb"]`` to avoid silent f8 upcasts inside the
#: per-pair vectorized code path.
_BODY_ORBS_16: np.ndarray = _build_body_orbs_16()

# Backward-compatible alias — removed in v1.3 cleanup; use _BODY_ORBS_16.
_BODY_ORBS_15 = _BODY_ORBS_16


#: Type alias for the :func:`resolve_orb_set` input parameter.
#:
#: MVP scope (v1.2) is **name-only string preset** per
#: ``.planning/phases/16-synastry/16-RESEARCH.md`` Open Question Q2. We
#: deliberately do NOT accept ``dict`` / ``callable`` / ``Sequence`` in v1.2 —
#: the surface mirrors :data:`ketu.aspects.presets.AspectSetSpec` in shape but
#: stays strictly narrower until a real use case demands extension.
OrbSetSpec = Union[None, str]


def synastry_orb_limit(
    b1: int, b2: int, asp: int, factor: float = SYNASTRY_FACTOR,
) -> float:
    """
    Compute the synastry orb tolerance for a body-pair + aspect.

    Reuses the natal formula ``(orb_a + orb_b) / 2 * coef`` (from
    :func:`ketu.aspects.calculator.get_orb` at line 50) and tightens by
    ``factor``. Returned as a pure-Python ``float`` to avoid silent
    ``np.float32`` / ``np.float64`` confusion at the caller boundary.

    Parameters
    ----------
    b1 : int
        First body index in the 16-body synastry axis (0..15).
    b2 : int
        Second body index in the 16-body synastry axis (0..15).
    asp : int
        Canonical aspect index (0..13) per :data:`ketu.core.aspects`.
    factor : float, optional
        Multiplicative tightening factor. Defaults to :data:`SYNASTRY_FACTOR`
        (``0.5``).

    Returns
    -------
    float
        Orb tolerance in degrees (always non-negative; distance from exact
        aspect angle). As of v1.7 the fictitious points Rahu, Ketu, and Lilith
        carry a 2 deg natal orb (previously 0) in :data:`ketu.core.bodies`, so
        point-point pairs yield a non-zero tolerance.

    See Also
    --------
    ketu.aspects.calculator.get_orb : Natal-orb formula
        (``factor=1.0`` equivalent).
    ketu.synastry.orbs.resolve_orb_set : Preset name -> factor resolver.
    ketu.synastry.calculate_synastry : Public entry point that uses this
        formula in vectorised form.

    Examples
    --------
    >>> from ketu.synastry.orbs import synastry_orb_limit
    >>> synastry_orb_limit(0, 1, 0)   # Sun-Moon conjunction: (12+12)/2 * 1 * 0.5
    6.0
    >>> synastry_orb_limit(10, 10, 0)  # Rahu-Rahu conjunction: (2+2)/2 * 1 * 0.5
    1.0
    """
    return float(
        (_BODY_ORBS_16[b1] + _BODY_ORBS_16[b2]) / 2.0
        * float(_ASPECTS["coef"][asp])
        * factor
    )


# Internal preset name registry. Mirrors the singular ``_PRESET_BY_NAME``
# naming convention from ``ketu/aspects/presets.py:91`` — do NOT pluralise.
# v1.2 ships ONE preset (``synastry``); ``classical`` accepts the natal
# formula unchanged for expert comparison views. v1.3 may add
# ``liz_greene`` per-aspect coefficients via in-place dict extension.
_PRESET_BY_NAME: dict[str, float] = {
    "synastry":  SYNASTRY_FACTOR,  # 0.5 — tightened (astro.com convention)
    "classical": 1.0,              # 1.0 — natal orbs unchanged (expert view)
}


def resolve_orb_set(spec: OrbSetSpec) -> float:
    """
    Resolve the ``orbs=`` parameter to a multiplicative factor.

    Single-call resolver: the public ``calculate_synastry`` API (Plan 16-02)
    invokes this exactly once at entry and passes the resulting scalar
    factor down to the hot loop. The factor is multiplied against the natal
    orb formula ``(orb_a + orb_b) / 2 * coef`` to obtain the synastry orb
    tolerance per pair.

    Parameters
    ----------
    spec : None or str
        - ``None`` or ``"synastry"`` -> :data:`SYNASTRY_FACTOR` (``0.5``).
        - ``"classical"`` -> ``1.0`` (use natal orbs unchanged; expert view).
        - String lookup is case-insensitive (lowercased before comparison).

    Returns
    -------
    float
        Multiplicative factor applied to the natal orb formula.

    Raises
    ------
    ValueError
        If ``spec`` is an unknown preset name, or a non-string non-``None``
        type. The error message enumerates the valid preset names so the
        caller can correct the spec without reading source code.

    See Also
    --------
    ketu.aspects.presets.resolve_aspect_set : Sibling resolver for
        ``aspects=`` specs.
    ketu.synastry.orbs.synastry_orb_limit : Scalar orb computation using
        the resolved factor.
    ketu.synastry.calculate_synastry : Public entry point invoking this
        resolver once at entry.

    Examples
    --------
    >>> from ketu.synastry.orbs import resolve_orb_set
    >>> resolve_orb_set(None)
    0.5
    >>> resolve_orb_set("synastry")
    0.5
    >>> resolve_orb_set("classical")
    1.0
    >>> resolve_orb_set("SYNASTRY")  # case-insensitive
    0.5
    """
    if spec is None:
        return _PRESET_BY_NAME["synastry"]
    if isinstance(spec, str):
        key = spec.lower()
        if key in _PRESET_BY_NAME:
            return _PRESET_BY_NAME[key]
        valid = ", ".join(sorted(_PRESET_BY_NAME))
        raise ValueError(
            f"unknown orb preset: {spec!r}. Valid presets: {valid}"
        )
    raise ValueError(
        f"unsupported orbs= type: {type(spec).__name__} "
        f"(expected None or str)"
    )


__all__ = [
    "ASC_MC_NATAL_ORB_DEG",
    "OrbSetSpec",
    "SYNASTRY_FACTOR",
    "resolve_orb_set",
    "synastry_orb_limit",
]
