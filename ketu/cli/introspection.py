"""Introspection commands — CLI-05.

Human-readable indented list to STDOUT. JSON output deferred to v1.2
(research §Open Question 4).
"""
from __future__ import annotations

import numpy as np

from ketu.aspects.presets import resolve_aspect_set
from ketu.core import aspects as _CORE_ASPECTS
from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS


_PRESET_DESCRIPTIONS = {
    "classical": "5 majors (Conjunction, Sextile, Square, Trine, Opposition) — v1.1 default",
    "traditional": "7 aspects (CLASSICAL + Semi-sextile + Quincunx)",
    "extended": "14 aspects (all rows of core.aspects, including harmonics 5/9/10)",
    "all": "alias for 'extended' — v1.0 14-aspect output (CLI-03 byte-identical escape hatch)",
}

_SYSTEM_DESCRIPTIONS = {
    "placidus": "Time-based; iterative trisection of the diurnal/nocturnal arcs (v1.1)",
    "koch": "Birthplace-based; closed-form trisection of the oblique-ascension arc (v1.1)",
    "porphyry": "Space-based; equal trisection of the ARMC quadrants — works at all latitudes (v1.1, also the polar fallback)",
    "whole_sign": "Sign-based; cusp 1 = start of rising sign, then 30° spacing — oldest historical system; polar-safe (v1.2)",
    "equal": "Equal-house; cusp 1 = ASC, then 30° spacing — note cusp 10 ≠ astronomical MC; polar-safe (v1.2)",
    "regiomontanus": "Space-based; equal 30° divisions of celestial equator projected through prime vertical; NaN at polar (v1.2)",
}


def cmd_list_aspect_sets() -> None:
    """Print available aspect-set presets with descriptions to stdout."""
    print("Available aspect sets (use with --harmonics SPEC):")
    print()
    for name in ("classical", "traditional", "extended", "all"):
        # Resolve the mask so we can show the actual angles.
        mask = resolve_aspect_set("extended" if name == "all" else name)
        names = [n.decode() if isinstance(n, bytes) else str(n)
                 for n in _CORE_ASPECTS["name"][mask]]
        angles = [int(a) for a in _CORE_ASPECTS["angle"][mask]]
        angle_str = ", ".join(f"{n} {a}°" for n, a in zip(names, angles))
        desc = _PRESET_DESCRIPTIONS.get(name, "")
        print(f"  {name:12} : {desc}")
        print(f"  {'':12}   ({len(names)} aspects: {angle_str})")
        print()
    print("You may also pass an explicit comma-separated list of aspect indices,")
    print("e.g. --harmonics 0,4,7,9,13 (= classical).")


def cmd_list_house_systems() -> None:
    """Print available house systems with descriptions to stdout."""
    print("Available house systems (use with --system NAME on `ketu houses`):")
    print()
    for name in sorted(_HOUSE_SYSTEMS.keys()):
        desc = _SYSTEM_DESCRIPTIONS.get(name, "(no description available)")
        print(f"  {name:10} : {desc}")
    print()
    print("At polar latitudes, use --polar-fallback porphyry to substitute Porphyry")
    print("cusps for offending elements (default: --polar-fallback raise).")
