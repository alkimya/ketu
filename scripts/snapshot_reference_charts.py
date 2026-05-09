#!/usr/bin/env python3
"""Regenerate ``tests/houses/fixtures/reference_charts.json``.

Iterates the 10 reference charts × 6 registered house systems
(placidus, koch, porphyry, whole_sign, equal, regiomontanus) and writes
the snapshot consumed by
``test_oracle_smoke.py::test_loaded_reference_snapshot_matches_oracle``.

The snapshot pinned in git serves as an environmental ratchet: if a
swisseph version bump or ephemeris-file change drifts oracle output by
more than ``1e-9°``, the test fails — pointing the operator here to
re-run this script intentionally.

Usage
-----
``python scripts/snapshot_reference_charts.py``                  # regenerate in place
``python scripts/snapshot_reference_charts.py --check``           # validate without writing

Idempotency
-----------
Running this script twice in a row produces byte-identical JSON
(deterministic swisseph + sorted dict keys + canonical float repr).

License note
------------
Imports ``swisseph`` (AGPL test-only dep). This script lives under
``scripts/`` (not ``ketu/``) deliberately — the production package
remains swisseph-free.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# pyswisseph is a test-only AGPL dep; this regen script is part of the
# test infrastructure even though it sits under scripts/.
import swisseph as swe  # type: ignore[import-not-found]


# ---------------------------------------------------------------------------
# Fixtures (mirrors tests/houses/conftest.py:reference_charts)
# ---------------------------------------------------------------------------

REFERENCE_CHARTS: list[dict[str, Any]] = [
    {"label": "J2000_Greenwich",   "jd": 2451545.0, "lat": 51.4779, "lon": 0.0},
    {"label": "J2000_Paris",       "jd": 2451545.0, "lat": 48.8566, "lon": 2.3522},
    {"label": "J2000_Sydney",      "jd": 2451545.0, "lat": -33.8688, "lon": 151.2093},
    {"label": "J2000_Tokyo",       "jd": 2451545.0, "lat": 35.6762, "lon": 139.6503},
    {"label": "J2000_BuenosAires", "jd": 2451545.0, "lat": -34.6037, "lon": -58.3816},
    {"label": "J2000_Equator",     "jd": 2451545.0, "lat": 0.0, "lon": 0.0},
    {"label": "1900_NewYork",      "jd": 2415020.5, "lat": 40.7128, "lon": -74.0060},
    {"label": "2050_Reykjavik",    "jd": 2470204.0, "lat": 64.1466, "lon": -21.9426},
    {"label": "J2000_Lat70_North", "jd": 2451545.0, "lat": 70.0, "lon": 0.0},
    {"label": "J2000_Lat80_North", "jd": 2451545.0, "lat": 80.0, "lon": 0.0},
]

# All 6 v1.2 systems. Iterate ALL of them on every regen — Pitfall 6
# from 15-RESEARCH §11 (don't accidentally drop placidus/koch/porphyry).
SYSTEM_BYTES: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyry": b"O",
    "whole_sign": b"W",
    "equal": b"E",
    "regiomontanus": b"R",
}

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "houses"
    / "fixtures"
    / "reference_charts.json"
)
SNAPSHOT_VERSION = "v1.2-phase15-snapshot"


# ---------------------------------------------------------------------------
# Snapshot computation
# ---------------------------------------------------------------------------


def compute_snapshot() -> dict[str, Any]:
    """Build the full snapshot dict for all charts × all systems.

    Returns
    -------
    dict
        Top-level structure ``{"version": str, "charts": {label: block}}``.
        Each ``block`` has ``"meta"`` (label/jd/lat/lon) and ``"systems"``
        (mapping system-name → cusps/asc/mc/armc/vertex, or ``{"error":
        msg, "polar": True}`` on swisseph polar failure).
    """
    out: dict[str, Any] = {"version": SNAPSHOT_VERSION, "charts": {}}
    for chart in REFERENCE_CHARTS:
        block: dict[str, Any] = {
            "meta": {
                "label": chart["label"],
                "jd": chart["jd"],
                "lat": chart["lat"],
                "lon": chart["lon"],
            },
            "systems": {},
        }
        for sys_name, code in SYSTEM_BYTES.items():
            try:
                cusps_t, ascmc_t = swe.houses_ex(
                    chart["jd"], chart["lat"], chart["lon"], code
                )
                block["systems"][sys_name] = {
                    "cusps": [float(c) for c in cusps_t[1:13]],
                    "asc": float(ascmc_t[0]),
                    "mc": float(ascmc_t[1]),
                    "armc": float(ascmc_t[2]),
                    "vertex": float(ascmc_t[3]),
                }
            except swe.Error as exc:
                # Polar boundary (Placidus/Koch/Regiomontanus at lat>=70°)
                block["systems"][sys_name] = {
                    "error": str(exc),
                    "polar": True,
                }
        out["charts"][chart["label"]] = block
    return out


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def write_snapshot(payload: dict[str, Any], path: Path) -> None:
    """Write the snapshot to ``path`` with deterministic formatting.

    Parameters
    ----------
    payload : dict
        Snapshot dict produced by :func:`compute_snapshot`.
    path : pathlib.Path
        Destination JSON file. Parent directories are created if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def check_snapshot(payload: dict[str, Any], path: Path) -> bool:
    """Return ``True`` if the on-disk snapshot matches ``payload`` byte-for-byte.

    Parameters
    ----------
    payload : dict
        Snapshot dict produced by :func:`compute_snapshot`.
    path : pathlib.Path
        On-disk JSON file to compare against.

    Returns
    -------
    bool
        ``True`` if the on-disk file is byte-identical to the rendered
        ``payload`` (deterministic JSON formatting); ``False`` if the
        file is missing or differs.
    """
    if not path.exists():
        return False
    expected = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    actual = path.read_text(encoding="utf-8")
    return expected == actual


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Run the snapshot regen / verification CLI.

    Parameters
    ----------
    argv : list of str, optional
        Argument vector (defaults to ``sys.argv[1:]``).

    Returns
    -------
    int
        Process exit code: ``0`` on success, ``1`` on snapshot drift
        when ``--check`` was requested.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare snapshot to disk, exit non-zero if drift; do not write.",
    )
    args = parser.parse_args(argv)

    payload = compute_snapshot()

    if args.check:
        ok = check_snapshot(payload, OUTPUT_PATH)
        if not ok:
            print(
                f"Snapshot drift detected at {OUTPUT_PATH}. "
                "Re-run without --check to regenerate.",
                file=sys.stderr,
            )
            return 1
        print(f"Snapshot {OUTPUT_PATH} matches live oracle output.")
        return 0

    write_snapshot(payload, OUTPUT_PATH)
    print(
        f"Wrote snapshot to {OUTPUT_PATH} "
        f"({len(payload['charts'])} charts × {len(SYSTEM_BYTES)} systems)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
