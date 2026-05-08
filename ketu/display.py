"""Library formatters for Ketu astronomical output.

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
)
from .aspects import calculate_aspects

if TYPE_CHECKING:
    from .aspects.presets import AspectSetSpec


def print_positions(jdate: float) -> None:
    """Print formatted positions of all bodies for a given date.

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


def print_aspects(
    jdate: float,
    aspects: "AspectSetSpec" = None,
) -> None:
    """Print formatted aspects between all bodies for a given date.

    Parameters
    ----------
    jdate : float
        Julian Date.
    aspects : AspectSetSpec, default None
        Aspect set to compute. Forwarded verbatim to
        :func:`ketu.aspects.calculate_aspects`. ``None`` resolves to the
        CLASSICAL preset (5 majors). Accepts a preset name, a list of
        aspect names or indices, or a length-14 boolean mask.

    Notes
    -----
    The format string (``"{degs:>2}º{mins:>2}'{secs:>2}\\""``) uses
    ``º`` (U+00BA, MASCULINE ORDINAL INDICATOR), NOT the DEGREE SIGN
    character at codepoint U+00B0. v1.0 used U+00BA and CLI-03
    (Plan 11-06) pins the output byte-for-byte against the v1.0
    fixture; do not "correct" the character.
    """
    print("\n")
    print("------------- Bodies Aspects -------------")
    for aspect in calculate_aspects(jdate, aspects=aspects):
        body1, body2, i_asp, orb = aspect
        degs, mins, secs = dd_to_dms(orb)
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
