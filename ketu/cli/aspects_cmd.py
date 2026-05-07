"""Dispatcher for `ketu aspects ...` subcommand.

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

import numpy as np

from ketu.aspects import find_aspects_between_dates
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
    """Best-effort human label for the resolved-config header.

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


def cmd_aspects(args: argparse.Namespace) -> int:
    """Compute and print body positions + aspects for a date.

    Parameters
    ----------
    args : argparse.Namespace
        Required: ``date``. Optional (top-level): ``harmonics`` — a
        length-14 ``np.bool_`` mask or None (None resolves to CLASSICAL
        via :func:`ketu.aspects.presets.resolve_aspect_set`).

    Returns
    -------
    int
        Exit code (0 on success).
    """
    # Resolve --harmonics: None → CLASSICAL (Phase 9 default).
    if args.harmonics is None:
        mask = resolve_aspect_set(None)
        preset_label = "classical"
    else:
        mask = args.harmonics  # already a length-14 np.bool_ mask
        preset_label = _preset_label_for_mask(mask)

    # Resolved-config header to STDERR (CLI-06; preserves CLI-03 stdout).
    emit_resolved_config(mask, preset_label, house_system=None)

    jd = parse_iso_utc(args.date)

    # Positions block — library helper (unchanged in Plan 11-04).
    print_positions(jd)

    # Aspects block — library helper extended in Plan 11-04 to accept aspects=.
    # SINGLE SOURCE OF TRUTH for the v1.0 'º' format string (BLOCKER 1 fix).
    print_aspects(jd, aspects=mask)

    # Aspect Timing Example — ALWAYS emitted (research §Open Question 2).
    # Reproduces v1.0 main()'s trailing Sun-Moon timing demo verbatim.
    print()
    print("------------- Aspect Timing Example -------------")
    sun_id = body_id("Sun")
    moon_id = body_id("Moon")
    aspects_found = find_aspects_between_dates(jd - 15, jd + 15, sun_id, moon_id)
    for entry in aspects_found[:3]:
        exact_jd, b1, b2, asp_name, _asp_val = entry
        exact_dt = julian_to_utc(float(exact_jd))
        print(f"{body_name(int(b1))} {asp_name} {body_name(int(b2))} at {exact_dt}")

    return 0
