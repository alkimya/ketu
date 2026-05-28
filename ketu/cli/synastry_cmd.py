"""
Dispatcher for ``ketu synastry ...`` subcommand.

Computes synastry between two natal charts and emits either an aligned
ASCII table (default) or a JSON list-of-dicts (``--json`` opt-in). Mirrors
the :mod:`ketu.cli.houses_cmd` pattern: registry dispatch via
:func:`ketu.charts.compute_chart` + :func:`ketu.synastry.calculate_synastry`;
resolved-config STDERR header via :func:`ketu.cli.formatters.emit_resolved_config`.

Notes
-----
**Body axis (15 entries).** Indices 0..12 follow :data:`ketu.core.bodies`
(Sun=0, ..., Lilith=12); index 13 is ASC, index 14 is MC. The labels
emitted in stdout (both table and JSON) follow that order.

**STDERR diagnostics.** In addition to the standard Ketu resolved-config
header (`# Ketu v1.1.0` + `# House system: <name>`), this command appends
two synastry-specific lines:

- ``# Synastry mode: <filtered|dense>`` — echoes the resolved mode.
- ``# Orbs: synastry (factor 0.5 — astro.com convention)`` — pins the
  orb preset citation per ROADMAP success criterion #3.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import numpy as np

from ketu.charts import compute_chart
from ketu.core import aspects as _CORE_ASPECTS, bodies as _CORE_BODIES
from ketu.synastry import calculate_synastry

from ._dates import parse_iso_utc
from .formatters import emit_resolved_config


# Body axis labels: 0..12 from core.bodies, 13 = ASC, 14 = MC.
_BODY_LABELS_15: list[str] = [
    name.decode() if isinstance(name, bytes) else str(name)
    for name in _CORE_BODIES["name"]
] + ["ASC", "MC"]


def _body_label(idx: int) -> str:
    """
    Map a 15-body synastry axis index to a human-readable label.

    Parameters
    ----------
    idx : int
        Synastry axis index in the range ``[0, 14]``. Indices 0..12 map
        to :data:`ketu.core.bodies` names; 13 -> ``"ASC"``; 14 -> ``"MC"``.

    Returns
    -------
    str
        Human-readable body label.

    Raises
    ------
    ValueError
        If ``idx`` is outside ``[0, 14]``.
    """
    if 0 <= idx < len(_BODY_LABELS_15):
        return _BODY_LABELS_15[idx]
    raise ValueError(f"invalid body index {idx}")


def _row_to_jsonable(row: np.void) -> dict[str, Any]:
    """
    Convert one :data:`ketu.synastry.SYNASTRY_DTYPE` row to a JSON-friendly dict.

    Sentinel values (``aspect_type == -1`` / ``NaN`` orb / ``NaN`` orb_limit)
    are serialised as ``None`` per JSON convention; the body indices are
    emitted as ``int`` alongside their human-readable labels.

    Parameters
    ----------
    row : np.void
        One scalar record of :data:`ketu.synastry.SYNASTRY_DTYPE`.

    Returns
    -------
    dict
        Dictionary with the 8 :data:`ketu.synastry.SYNASTRY_DTYPE` field
        names plus three label fields (``body_a_name``, ``body_b_name``,
        ``aspect_name``). ``aspect_name`` is ``None`` when the row carries
        the ``aspect_type == -1`` sentinel.
    """
    aspect_type = int(row["aspect_type"])
    return {
        "body_a": int(row["body_a"]),
        "body_b": int(row["body_b"]),
        "body_a_name": _body_label(int(row["body_a"])),
        "body_b_name": _body_label(int(row["body_b"])),
        "lon_a": float(row["lon_a"]),
        "lon_b": float(row["lon_b"]),
        "aspect_type": aspect_type,
        "aspect_name": (
            _CORE_ASPECTS["name"][aspect_type].decode()
            if aspect_type >= 0 else None
        ),
        "orb": (None if np.isnan(row["orb"]) else float(row["orb"])),
        "applying": bool(row["applying"]),
        "orb_limit": (
            None if np.isnan(row["orb_limit"]) else float(row["orb_limit"])
        ),
    }


def cmd_synastry(args: argparse.Namespace) -> int:
    """
    Compute synastry between two charts and emit table or JSON.

    Workflow: emits the resolved-config STDERR header (CLI-06); parses
    both ISO date strings to Julian Dates; computes both charts via
    :func:`ketu.charts.compute_chart`; runs
    :func:`ketu.synastry.calculate_synastry`; renders either an aligned
    ASCII table (default) or a JSON list-of-dicts (``--json``).

    Parameters
    ----------
    args : argparse.Namespace
        Required attributes: ``date_a``, ``lat_a``, ``lon_a``, ``date_b``,
        ``lat_b``, ``lon_b``, ``mode``, ``system``, ``polar_fallback``,
        ``json``.

    Returns
    -------
    int
        Process exit code (``0`` on success). Argparse argument-validation
        errors raise ``SystemExit(2)`` upstream and never reach here.
    """
    # Resolved-config header to STDERR (CLI-06).
    emit_resolved_config(mask=None, preset_name=None, house_system=args.system)
    print(f"# Synastry mode: {args.mode}", file=sys.stderr)
    print(
        "# Orbs: synastry (factor 0.5 — astro.com convention)",
        file=sys.stderr,
    )

    jd_a = parse_iso_utc(args.date_a)
    jd_b = parse_iso_utc(args.date_b)
    chart_a = compute_chart(
        jd_a, args.lat_a, args.lon_a,
        system=args.system, polar_fallback=args.polar_fallback,
    )
    chart_b = compute_chart(
        jd_b, args.lat_b, args.lon_b,
        system=args.system, polar_fallback=args.polar_fallback,
    )
    result = calculate_synastry(chart_a, chart_b, mode=args.mode)

    if args.json:
        out = [_row_to_jsonable(row) for row in result]
        print(json.dumps(out, indent=2))
        return 0

    # Aligned ASCII table.
    print()
    aspected = (
        result[result["aspect_type"] >= 0] if args.mode == "dense" else result
    )
    print(
        f"------- Synastry ({args.mode} mode, {len(aspected)} aspects) -------"
    )
    if len(aspected) == 0:
        print("(no aspects within synastry orbs)")
        return 0
    print(
        f"{'Body A':<10} {'Body B':<10} {'Aspect':<14} "
        f"{'Orb':>9} {'Limit':>7} {'Apply':>6}"
    )
    for row in aspected:
        name_a = _body_label(int(row["body_a"]))
        name_b = _body_label(int(row["body_b"]))
        asp_name = _CORE_ASPECTS["name"][int(row["aspect_type"])].decode()
        print(
            f"{name_a:<10} {name_b:<10} {asp_name:<14} "
            f"{float(row['orb']):>+9.3f} {float(row['orb_limit']):>7.3f} "
            f"{('Y' if bool(row['applying']) else 'N'):>6}"
        )
    return 0
