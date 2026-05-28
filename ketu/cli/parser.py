"""
Argparse tree builder + main() dispatch for ketu CLI.

Subcommand pattern uses ``set_defaults(func=...)`` per subparser so
``main()`` dispatches via ``args.func(args)`` rather than an
if-elif ladder. Top-level introspection flags (``--list-aspect-sets``,
``--list-house-systems``) short-circuit before subcommand dispatch, which
is why ``add_subparsers`` uses ``required=False``.

Plan 11-01 lays the skeleton; Plans 11-02..11-04 wire the real type
validator, subcommand dispatchers, formatters, and introspection.
"""
from __future__ import annotations

import argparse
from typing import Sequence

from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS

from .aspects_cmd import cmd_aspects
from .harmonics_spec import parse_harmonics_spec
from .houses_cmd import cmd_houses
from .introspection import (
    cmd_list_aspect_sets,
    cmd_list_house_systems,
    cmd_list_orbs,
    cmd_list_parts,
)
from .synastry_cmd import cmd_synastry


def build_parser() -> argparse.ArgumentParser:
    """
    Construct the top-level argparse tree.

    Returns
    -------
    argparse.ArgumentParser
        Top-level parser with ``aspects`` and ``houses`` subparsers, plus
        top-level flags ``--harmonics``, ``--list-aspect-sets``, and
        ``--list-house-systems``. Subcommands use
        ``set_defaults(func=...)``; the dispatchers are stubs in Plan
        11-01 and replaced in subsequent plans.
    """
    parser = argparse.ArgumentParser(
        prog="ketu",
        description=(
            "Ketu — astronomical body positions, planetary aspects, and "
            "house cusps. Pure-NumPy library; no external runtime deps."
        ),
    )

    # Top-level introspection flags. These short-circuit in main() before
    # subcommand dispatch.
    parser.add_argument(
        "--list-aspect-sets",
        action="store_true",
        help=(
            "List available aspect set presets (classical, traditional, "
            "extended, all) and exit."
        ),
    )
    parser.add_argument(
        "--list-house-systems",
        action="store_true",
        help="List all registered house systems and exit.",
    )
    parser.add_argument(
        "--list-orbs",
        action="store_true",
        help=(
            "List available synastry orb presets (synastry, classical) with "
            "the formula derivation and exit."
        ),
    )
    parser.add_argument(
        "--list-parts",
        action="store_true",
        help="List all registered Arabic Parts (Fortune, Spirit, Marriage) and exit.",
    )

    # Top-level --harmonics SPEC. Plan 11-02 wires type=parse_harmonics_spec
    # which returns a length-14 np.bool_ mask. Default=None means "use the
    # CLASSICAL preset" (resolved by aspects_cmd in Plan 11-04).
    parser.add_argument(
        "--harmonics",
        type=parse_harmonics_spec,
        default=None,
        metavar="SPEC",
        help=(
            "Aspect set selector. Named preset ('classical' [default], "
            "'traditional', 'extended', 'all' alias for 'extended'), or "
            "comma-separated indices into core.aspects (e.g. '0,4,7,9,13' "
            "= classical). Bare integers (e.g. '12') are rejected — use "
            "named presets or comma-separated lists."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=False,  # introspection flags work without a subcommand
        title="subcommands",
        metavar="{aspects,houses,synastry}",
    )

    # `ketu aspects --date ISO`
    p_aspects = subparsers.add_parser(
        "aspects",
        help="Compute body positions and aspects for a date/time (UTC).",
        description=(
            "Compute body positions and planetary aspects. Uses --harmonics "
            "from the top-level parser to filter the aspect set."
        ),
    )
    p_aspects.add_argument(
        "--date",
        required=True,
        metavar="ISO",
        help="UTC date-time, ISO 8601 (e.g. 2026-05-06T12:00:00Z).",
    )
    p_aspects.set_defaults(func=cmd_aspects)

    # `ketu houses --date ISO --lat F --lon F --system NAME`
    p_houses = subparsers.add_parser(
        "houses",
        help="Compute house cusps for a date/time/location.",
        description=(
            "Compute the 12 house cusps using a registered house system. "
            "At polar latitudes, --polar-fallback porphyry substitutes "
            "Porphyry cusps for offending elements; --polar-fallback raise "
            "(default) raises HighLatitudeError."
        ),
    )
    p_houses.add_argument(
        "--date",
        required=True,
        metavar="ISO",
        help="UTC date-time, ISO 8601 (e.g. 2026-05-06T12:00:00Z).",
    )
    p_houses.add_argument(
        "--lat",
        required=True,
        type=float,
        metavar="DEG",
        help="Geographic latitude in degrees (positive North).",
    )
    p_houses.add_argument(
        "--lon",
        required=True,
        type=float,
        metavar="DEG",
        help="Geographic longitude in degrees (positive East).",
    )
    p_houses.add_argument(
        "--system",
        choices=sorted(_HOUSE_SYSTEMS.keys()),
        default="placidus",
        help=(
            "House system (default: placidus). Available: "
            f"{', '.join(sorted(_HOUSE_SYSTEMS.keys()))}. "
            "Use --list-house-systems for descriptions."
        ),
    )
    p_houses.add_argument(
        "--polar-fallback",
        choices=["raise", "porphyry"],
        default="raise",
        help=(
            "Behavior at polar latitudes: 'raise' (default) raises "
            "HighLatitudeError; 'porphyry' substitutes Porphyry cusps for "
            "offending elements."
        ),
    )
    p_houses.set_defaults(func=cmd_houses)

    # `ketu synastry --date-a ISO --lat-a F --lon-a F --date-b ISO --lat-b F --lon-b F`
    p_synastry = subparsers.add_parser(
        "synastry",
        help="Compute synastry (cross-chart aspects) between two natal charts.",
        description=(
            "Compute aspects between two natal charts. Cross-product "
            "enumeration (15x15 = 225 ordered pairs including ASC/MC and "
            "self-pairs); synastry-tightened orbs (factor 0.5 vs natal). "
            "Defaults: aspects=classical (5 majors), orbs=synastry "
            "(factor 0.5), mode=filtered (only aspected pairs)."
        ),
    )
    # Chart A.
    p_synastry.add_argument(
        "--date-a",
        required=True,
        metavar="ISO",
        help="Chart A UTC date-time, ISO 8601 (e.g. 1940-10-09T18:30:00Z).",
    )
    p_synastry.add_argument(
        "--lat-a",
        required=True,
        type=float,
        metavar="DEG",
        help="Chart A geographic latitude in degrees (positive North).",
    )
    p_synastry.add_argument(
        "--lon-a",
        required=True,
        type=float,
        metavar="DEG",
        help="Chart A geographic longitude in degrees (positive East).",
    )
    # Chart B.
    p_synastry.add_argument(
        "--date-b",
        required=True,
        metavar="ISO",
        help="Chart B UTC date-time, ISO 8601.",
    )
    p_synastry.add_argument(
        "--lat-b",
        required=True,
        type=float,
        metavar="DEG",
        help="Chart B geographic latitude in degrees (positive North).",
    )
    p_synastry.add_argument(
        "--lon-b",
        required=True,
        type=float,
        metavar="DEG",
        help="Chart B geographic longitude in degrees (positive East).",
    )
    # Mode + system + polar fallback + json.
    p_synastry.add_argument(
        "--mode",
        choices=["filtered", "dense"],
        default="filtered",
        help=(
            "Output mode: 'filtered' (default; only aspected pairs) or "
            "'dense' (all 225 cross-pairs with -1/NaN sentinels for "
            "non-aspected)."
        ),
    )
    p_synastry.add_argument(
        "--system",
        choices=sorted(_HOUSE_SYSTEMS.keys()),
        default="placidus",
        help=(
            "House system used to compute ASC/MC for both charts "
            "(default: placidus). Available: "
            f"{', '.join(sorted(_HOUSE_SYSTEMS.keys()))}. "
            "Use --list-house-systems for descriptions."
        ),
    )
    p_synastry.add_argument(
        "--polar-fallback",
        choices=["raise", "porphyry"],
        default="raise",
        help=(
            "Behavior at polar latitudes: 'raise' (default) raises "
            "HighLatitudeError; 'porphyry' substitutes Porphyry cusps for "
            "offending elements."
        ),
    )
    p_synastry.add_argument(
        "--json",
        action="store_true",
        help=(
            "Emit result as JSON list-of-dicts to stdout (default: "
            "aligned ASCII table)."
        ),
    )
    p_synastry.set_defaults(func=cmd_synastry)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    CLI entry point.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument vector. Defaults to ``sys.argv[1:]`` when None — argparse
        convention. Tests inject explicit lists.

    Returns
    -------
    int
        Process exit code (0 = success). argparse errors raise SystemExit
        directly with code 2 before this returns.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Introspection short-circuits. NOTE: this ladder is FIRST-WINS — when
    # multiple --list-* flags are passed simultaneously, only the one
    # encountered first in this order is executed (Pitfall 8 from
    # 16-RESEARCH.md). Order is intentional, NOT alphabetical, and pinned
    # by `test_list_flags_collision_first_wins` in tests/cli/test_parser.py.
    if args.list_aspect_sets:
        cmd_list_aspect_sets()
        return 0
    if args.list_house_systems:
        cmd_list_house_systems()
        return 0
    if args.list_orbs:
        cmd_list_orbs()
        return 0
    if args.list_parts:
        cmd_list_parts()
        return 0

    # No subcommand → print help and return 0.
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0

    return int(func(args) or 0)
