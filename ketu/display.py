"""
Library formatters for Ketu astronomical output.

Provides ``print_positions`` and ``print_aspects`` — pure-stdout
formatted dumps used by the CLI (``ketu.cli.aspects_cmd``) and
documentation examples. The legacy interactive ``main()`` prompt was
removed in Phase 11; the argparse-based CLI lives in ``ketu.cli``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .core import signs
from .core import aspects as _CORE_ASPECTS
from .calculations import (
    body_name,
    body_sign,
    positions,
    is_retrograde,
    dd_to_dms,
    long,
    distance,
)
from .aspects import calculate_aspects
from .aspects.calculator import _normalize_dynamic_specs
from .aspects.harmonics import DynamicAspectSpec

if TYPE_CHECKING:
    from .aspects.presets import AspectSetSpec


def print_positions(jdate: float) -> None:
    """
    Print formatted positions of all bodies for a given date.

    Parameters
    ----------
    jdate : float
        Julian Date.
    """
    print("\n")
    print("------------- Bodies Positions -------------")
    for index, pos in np.ndenumerate(positions(jdate)):
        sign, degs, mins, secs = body_sign(pos)
        retro = ", R" if is_retrograde(jdate, *index) else ""
        print(f"{body_name(*index):10}: " f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


def _resolve_dynamic_name(
    jdate: float,
    body1: int,
    body2: int,
    dyn: np.ndarray,
) -> str:
    """
    Resolve the synthetic name for a dynamic-aspect row (``i_asp == -2``).

    Recomputes the actual angular separation between *body1* and *body2* at
    *jdate*, then finds the dynamic spec row whose angle is closest to that
    separation.  This mirrors the name-resolution logic in
    :func:`ketu.aspects.calculator.calculate_aspects` but works from the
    display side where only the body IDs and Julian Date are available.

    Parameters
    ----------
    jdate : float
        Julian Date.
    body1 : int
        First body ID (0-13).
    body2 : int
        Second body ID (0-13).
    dyn : np.ndarray
        Normalised dynamic specs array (as returned by
        :func:`~ketu.aspects.calculator._normalize_dynamic_specs`).  Must be
        non-None and non-empty.

    Returns
    -------
    str
        Synthetic name decoded from ``dyn['name']``, e.g. ``'H7-1'``.
    """
    dist = distance(long(jdate, body1), long(jdate, body2))
    dyn_angles = dyn["angle"].astype(float)
    idx = int(np.argmin(np.abs(dyn_angles - dist)))
    raw_name = dyn["name"][idx]
    return raw_name.decode() if isinstance(raw_name, bytes) else str(raw_name)


def print_aspects(
    jdate: float,
    aspects: "AspectSetSpec" = None,
    dynamic_specs: DynamicAspectSpec = None,
) -> None:
    """
    Print formatted aspects between all bodies for a given date.

    Parameters
    ----------
    jdate : float
        Julian Date.
    aspects : AspectSetSpec, default None
        Aspect set to compute. Forwarded verbatim to
        :func:`ketu.aspects.calculate_aspects`. ``None`` resolves to the
        CLASSICAL preset (5 majors). Accepts a preset name, a list of
        aspect names or indices, or a length-14 boolean mask.
    dynamic_specs : DynamicAspectSpec, default None
        Optional dynamic aspect specs as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`.  When
        provided, rows with ``i_asp == -2`` are resolved to their synthetic
        ``H{h}-{k}`` names via :func:`_resolve_dynamic_name` instead of the
        erroneous ``_CORE_ASPECTS['name'][-2]`` lookup (which would return
        ``b'Quadrinovile'``).  ``None`` keeps the classical static-only path.

    Notes
    -----
    The format string (``"{degs:>2}º{mins:>2}'{secs:>2}\"")``) uses
    ``º`` (U+00BA, MASCULINE ORDINAL INDICATOR), NOT the DEGREE SIGN
    character at codepoint U+00B0. v1.0 used U+00BA and CLI-03
    (Plan 11-06) pins the output byte-for-byte against the v1.0
    fixture; do not "correct" the character.
    """
    # Normalise dynamic_specs once — reuse the same helper as calculator.py (DRY).
    dyn = _normalize_dynamic_specs(dynamic_specs)

    print("\n")
    print("------------- Bodies Aspects -------------")
    for aspect in calculate_aspects(jdate, aspects=aspects, dynamic_specs=dynamic_specs):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
        if i_asp == -2 and dyn is not None:
            # Dynamic row — resolve synthetic name by recovering the actual
            # angular separation and matching against dynamic spec angles.
            # The _CORE_ASPECTS['name'][-2] lookup would return b'Quadrinovile'
            # (the 13th entry in the 14-row table), which is WRONG for dynamic rows.
            aspect_name = _resolve_dynamic_name(jdate, int(body1), int(body2), dyn)
        else:
            aspect_name_bytes = _CORE_ASPECTS['name'][i_asp]
            aspect_name = aspect_name_bytes.decode() if isinstance(aspect_name_bytes, bytes) else str(aspect_name_bytes)
        print(
            f"{body_name(body1):7} - {body_name(body2):12}: "
            f"{aspect_name:12} "
            f"{degs:>2}º{mins:>2}'{secs:>2}\""
        )


__all__ = [
    "print_positions",
    "print_aspects",
]
