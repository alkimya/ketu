"""
Dispatcher for `ketu aspects ...` subcommand.

Calls :func:`ketu.display.print_positions` and
:func:`ketu.display.print_aspects` (the latter extended in Plan 11-04 to
accept an optional ``aspects=`` mask kwarg, forwarded to
:func:`ketu.aspects.calculate_aspects`). ``display.py`` is the SINGLE
SOURCE OF TRUTH for the v1.0 stdout format strings — including the
``º`` (U+00BA, MASCULINE ORDINAL INDICATOR) degree character that
CLI-03 (Plan 11-06) byte-pins. This dispatcher therefore does NOT
hand-roll any format strings; it just calls the library helpers.

Open Question 2 resolution (research §Open Questions): the trailing
"Aspect Timing Example" Sun-Moon block is ALWAYS emitted regardless of
``--harmonics`` value. v1.0 emitted it for all aspect sets (it's a
fixed Sun-Moon timing demo, not aspect-set-dependent). Always emitting
preserves the byte-identical contract for ``--harmonics all`` AND
gives non-`all` users the same demo block (no surprising behaviour
change from v1.0).
"""
from __future__ import annotations

import argparse
from typing import Optional, Tuple

import numpy as np
import numpy.typing as npt

from ketu.aspects import find_aspects_between_dates
from ketu.aspects.harmonics import DynamicAspectSpec
from ketu.aspects.presets import resolve_aspect_set
from ketu.calculations import (
    body_id,
    body_name,
    julian_to_utc,
)
from ketu.display import print_positions, print_aspects

from ._dates import parse_iso_utc
from .formatters import emit_resolved_config


def _preset_label_for_mask(mask: np.ndarray) -> str:
    """
    Best-effort human label for the resolved-config header.

    After ``type=parse_harmonics_spec`` runs, the original spec string is
    no longer available — we have only the length-14 mask. Map back to
    the canonical preset name when the mask matches a preset
    bit-for-bit; otherwise return ``"custom"``.

    Note: a comma-separated list ``--harmonics 0,4,7,9,13`` produces the
    SAME mask as ``--harmonics classical``, so the header will say
    ``classical`` for that input. That is intentional — the resolved
    behaviour IS classical; the header reports the resolved set.
    """
    classical = resolve_aspect_set("classical")
    traditional = resolve_aspect_set("traditional")
    extended = resolve_aspect_set("extended")
    if np.array_equal(mask, classical):
        return "classical"
    if np.array_equal(mask, traditional):
        return "traditional"
    if np.array_equal(mask, extended):
        # 'extended' and 'all' produce the same mask; report the
        # canonical name (the alias is documented in --help).
        return "extended"
    return "custom"


def _harmonic_label(dyn: npt.NDArray[np.void]) -> Tuple[str, str]:
    """
    Derive the harmonic token and detail string from a dynamic specs array.

    Used to build the ``# Aspect set: h{N} (...)`` resolved-config header
    when ``--harmonics h<N>`` is supplied.

    Parameters
    ----------
    dyn : np.ndarray
        Dynamic aspect specs structured array as returned by
        :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`.

    Returns
    -------
    tuple[str, str]
        ``(label, detail)`` where *label* is ``"h{N}"`` (e.g. ``"h7"``) and
        *detail* is the human detail string, e.g.
        ``"3 aspects: H7-1 51°, H7-2 103°, H7-3 154°"``.
    """
    h = int(dyn["harmonic"][0])
    label = f"h{h}"
    parts = []
    for row in dyn:
        name = row["name"].decode() if isinstance(row["name"], bytes) else str(row["name"])
        angle = int(round(float(row["angle"])))
        parts.append(f"{name} {angle}°")
    detail = f"{len(dyn)} aspects: " + ", ".join(parts)
    return label, detail


def cmd_aspects(args: argparse.Namespace) -> int:
    """
    Compute and print body positions + aspects for a date.

    Parameters
    ----------
    args : argparse.Namespace
        Required: ``date``. Optional (top-level): ``harmonics`` — a
        :class:`~ketu.cli.harmonics_spec.HarmonicsSelection` NamedTuple or
        None.  ``None`` resolves to CLASSICAL via
        :func:`ketu.aspects.presets.resolve_aspect_set`.

    Returns
    -------
    int
        Exit code (0 on success).
    """
    # Resolve --harmonics: None → classical (5 aspects, v1.0/v1.1 byte-stable
    # contract). NOTE: the LIBRARY default (resolve_aspect_set(None)) is now
    # the 7 half-circle set (TRADITIONAL). The CLI bare default stays pinned
    # to "classical" intentionally so the CLI byte-stable contract is
    # preserved across v1.0/v1.1/v1.2 — use resolve_aspect_set("classical")
    # explicitly here instead of resolve_aspect_set(None).
    dyn: Optional[DynamicAspectSpec]
    dynamic_label: Optional[str]
    if args.harmonics is None:
        mask = resolve_aspect_set("classical")
        dyn = None
        preset_label = "classical"
        dynamic_label = None
    else:
        mask = args.harmonics.mask
        dyn = args.harmonics.dynamic_specs
        if dyn is None:
            preset_label = _preset_label_for_mask(mask)
            dynamic_label = None
        else:
            # dyn is a single structured array from generate_harmonic_aspects;
            # isinstance narrows from DynamicAspectSpec union to NDArray[np.void].
            assert isinstance(dyn, np.ndarray)
            preset_label, dynamic_label = _harmonic_label(dyn)

    # Resolved-config header to STDERR (CLI-06; preserves CLI-03 stdout).
    emit_resolved_config(mask, preset_label, house_system=None, dynamic_label=dynamic_label)

    jd = parse_iso_utc(args.date)

    # Positions block — library helper (unchanged in Plan 11-04).
    print_positions(jd)

    # Aspects block — library helper extended in Plan 11-04 to accept aspects=.
    # SINGLE SOURCE OF TRUTH for the v1.0 'º' format string (BLOCKER 1 fix).
    print_aspects(jd, aspects=mask, dynamic_specs=dyn)

    # Aspect Timing Example — ALWAYS emitted (research §Open Question 2).
    # Reproduces v1.0 main()'s trailing Sun-Moon timing demo verbatim.
    # NOTE: pinned to "classical" (5 majors) explicitly so the output is
    # byte-identical regardless of the --harmonics flag (the library default
    # shifted to TRADITIONAL/7 in Phase 26 plan 02, but this demo block must
    # stay byte-stable per test_v1_1_reference_byte_stable.py).
    print()
    print("------------- Aspect Timing Example -------------")
    sun_id = body_id("Sun")
    moon_id = body_id("Moon")
    aspects_found = find_aspects_between_dates(
        jd - 15, jd + 15, sun_id, moon_id, aspects="classical"
    )
    for entry in aspects_found[:3]:
        exact_jd, b1, b2, asp_name, _asp_val = entry
        exact_dt = julian_to_utc(float(exact_jd))
        print(f"{body_name(int(b1))} {asp_name} {body_name(int(b2))} at {exact_dt}")

    return 0
