"""Dispatcher for `ketu houses ...` subcommand.

Calls :func:`ketu.calculate_houses` (Phase 10 deliverable) — registry
dispatch, no inline if/elif. Formats the 12 cusps + ASC + MC for stdout.
The resolved-config header (CLI-06) is wired by Plan 11-04 (which adds
the `emit_resolved_config` call at the top of this dispatcher); Plan
11-03 lays down the rest of the dispatcher first.
"""
from __future__ import annotations

import argparse

import numpy as np

from ketu import calculate_houses
from ketu.calculations import dd_to_dms
from ketu.core import signs

from ._dates import parse_iso_utc
from .formatters import emit_resolved_config


def _format_cusp(cusp_deg: float) -> str:
    """Format a cusp longitude as ``'SIGN  DD°MM'SS"'`` for stdout.

    Parameters
    ----------
    cusp_deg : float
        Ecliptic longitude in degrees, 0-360.

    Returns
    -------
    str
        Sign-padded position string, e.g. ``"Aries           15°30'00\""``.
    """
    sign_index = int(cusp_deg // 30) % 12
    in_sign = cusp_deg - 30.0 * sign_index
    dms = dd_to_dms(in_sign)
    degs, mins, secs = int(dms[0]), int(dms[1]), int(dms[2])
    return f"{signs[sign_index]:15} {degs:>2}°{mins:>2}'{secs:>2}\""


def cmd_houses(args: argparse.Namespace) -> int:
    """Compute and print the 12 house cusps + ASC + MC.

    Parameters
    ----------
    args : argparse.Namespace
        Required attributes: ``date``, ``lat``, ``lon``, ``system``,
        ``polar_fallback``.

    Returns
    -------
    int
        Process exit code: 0 on success, non-zero handled by caller.
    """
    # Resolved-config header to STDERR (CLI-06; BLOCKER 2 fix — every
    # CLI invocation echoes the resolved config, including `houses`).
    emit_resolved_config(mask=None, preset_name=None, house_system=args.system)
    jd = parse_iso_utc(args.date)
    # Public API; registry dispatch happens inside calculate_houses.
    rec = calculate_houses(
        jd=jd,
        lat=args.lat,
        lon=args.lon,
        system=args.system,
        polar_fallback=args.polar_fallback,
    )
    cusps = np.asarray(rec["cusps"]).reshape(-1)
    if cusps.size != 12:
        raise SystemExit(
            f"error: calculate_houses returned {cusps.size} cusps, expected 12 "
            f"(this is a Ketu bug; please report)"
        )
    print()
    print("------------- House Cusps -------------")
    for i, cusp in enumerate(cusps, start=1):
        print(f"House {i:>2}: {_format_cusp(float(cusp))} ({float(cusp):8.4f}°)")
    asc = float(rec["asc"])
    mc = float(rec["mc"])
    print()
    print(f"ASC: {_format_cusp(asc)} ({asc:8.4f}°)")
    print(f"MC : {_format_cusp(mc)} ({mc:8.4f}°)")
    return 0
