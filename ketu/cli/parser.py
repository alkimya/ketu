"""Argparse tree builder + main() dispatch for ketu CLI.

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
import sys
from typing import Sequence

from .harmonics_spec import parse_harmonics_spec
from .houses_cmd import cmd_houses

# Stub dispatchers — real implementations land in Plan 11-04 (aspects +
# introspection). Plan 11-03 wired the real ``cmd_houses``; the houses
# stub is gone. For now the remaining stubs print a "not yet implemented"
# notice and return 0; tests pinning the dispatch shape continue to assert
# on the Plan-N marker as breadcrumbs.


def _stub_aspects(args: argparse.Namespace) -> int:
    """Stub dispatcher for the ``aspects`` subcommand (replaced in Plan 11-04)."""
    print(
        "ketu aspects: not yet implemented (wired in Plan 11-04)",
        file=sys.stderr,
    )
    return 0


def _stub_list_aspect_sets() -> None:
    """Stub for ``--list-aspect-sets`` introspection (replaced in Plan 11-04)."""
    print("(--list-aspect-sets: wired in Plan 11-04)", file=sys.stderr)


def _stub_list_house_systems() -> None:
    """Stub for ``--list-house-systems`` introspection (replaced in Plan 11-04)."""
    print("(--list-house-systems: wired in Plan 11-04)", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argparse tree.

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
        help=(
            "List available house systems (placidus, koch, porphyry) and exit."
        ),
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
        metavar="{aspects,houses}",
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
    p_aspects.set_defaults(func=_stub_aspects)

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
        choices=["placidus", "koch", "porphyry"],
        default="placidus",
        help="House system (default: placidus).",
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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point.

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

    # Introspection short-circuits.
    if args.list_aspect_sets:
        _stub_list_aspect_sets()
        return 0
    if args.list_house_systems:
        _stub_list_house_systems()
        return 0

    # No subcommand → print help and return 0.
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0

    return int(func(args) or 0)
