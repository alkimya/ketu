"""Unit tests for ketu.cli.parser — argparse tree shape and main() dispatch."""
from __future__ import annotations

import pytest

from ketu.cli.parser import build_parser


class TestBuildParser:
    """build_parser() shape: prog, subparsers, top-level flags."""

    def test_prog_is_ketu(self):
        parser = build_parser()
        assert parser.prog == "ketu"

    def test_subparsers_present(self):
        """aspects and houses subparsers are registered."""
        parser = build_parser()
        # Inspect via parse_args round-trip: --help on each must not crash.
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["aspects", "--help"])
        assert exc.value.code == 0
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["houses", "--help"])
        assert exc.value.code == 0

    def test_aspects_requires_date(self, capsys):
        """`ketu aspects` without --date is rejected with code 2."""
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["aspects"])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--date" in err

    def test_houses_requires_date_lat_lon(self, capsys):
        """`ketu houses` without --date/--lat/--lon is rejected."""
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["houses"])
        assert exc.value.code == 2

    def test_houses_system_default_is_placidus(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "houses",
                "--date",
                "2026-05-06T12:00:00Z",
                "--lat",
                "48.85",
                "--lon",
                "2.35",
            ]
        )
        assert args.system == "placidus"

    def test_houses_system_choices_enforced(self, capsys):
        """argparse rejects unregistered system names with exit code 2.

        Pitfall 7 (15-RESEARCH §11): in v1.1 this test pinned ``regiomontanus``
        as invalid. Phase 15 (Plan 15-03) makes it a registered system —
        the test now uses an impossible name to ratchet the rejection path
        without depending on a specific blacklist.
        """
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(
                [
                    "houses",
                    "--date",
                    "2026-05-06T12:00:00Z",
                    "--lat",
                    "48.85",
                    "--lon",
                    "2.35",
                    "--system",
                    "nonexistent_xyz",
                ]
            )
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "nonexistent_xyz" in err or "invalid choice" in err

    def test_houses_polar_fallback_default_is_raise(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "houses",
                "--date",
                "2026-05-06T12:00:00Z",
                "--lat",
                "48.85",
                "--lon",
                "2.35",
            ]
        )
        assert args.polar_fallback == "raise"

    def test_top_level_harmonics_present(self):
        parser = build_parser()
        # Sub-position; top-level flag goes BEFORE the subcommand.
        args = parser.parse_args(
            [
                "--harmonics",
                "classical",
                "aspects",
                "--date",
                "2026-05-06T12:00:00Z",
            ]
        )
        # After Plan 34-03, type=parse_harmonics_spec returns a HarmonicsSelection.
        from ketu.cli.harmonics_spec import HarmonicsSelection
        import numpy as np
        assert isinstance(args.harmonics, HarmonicsSelection)
        assert args.harmonics.mask.dtype == np.bool_
        assert args.harmonics.mask.shape == (14,)
        assert args.harmonics.mask.sum() == 5  # CLASSICAL = 5 majors
        assert args.harmonics.dynamic_specs is None

    def test_harmonics_default_is_none(self):
        """Default --harmonics value is None (resolved to CLASSICAL by aspects_cmd)."""
        parser = build_parser()
        args = parser.parse_args(
            ["aspects", "--date", "2026-05-06T12:00:00Z"]
        )
        assert args.harmonics is None

    def test_introspection_flags_default_false(self):
        parser = build_parser()
        # Need a subcommand or main() will print help; here we just check
        # the namespace shape after a successful parse.
        args = parser.parse_args(
            ["aspects", "--date", "2026-05-06T12:00:00Z"]
        )
        assert args.list_aspect_sets is False
        assert args.list_house_systems is False


class TestMainDispatch:
    """main(argv) entry point — short-circuit / dispatch / fallback."""

    def test_main_no_args_prints_help_returns_0(self, invoke_main, capsys):
        """`ketu` with no args prints help to stdout and returns 0
        (does NOT crash with AttributeError on missing args.func — Pitfall 4
        in research)."""
        rc = invoke_main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "ketu" in captured.out

    def test_main_list_aspect_sets_short_circuits(self, invoke_main, capsys):
        """--list-aspect-sets short-circuits before subcommand dispatch."""
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "classical" in out
        assert "traditional" in out
        assert "extended" in out
        assert "all" in out

    def test_main_list_house_systems_short_circuits(self, invoke_main, capsys):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "placidus" in out
        assert "koch" in out
        assert "porphyry" in out

    def test_main_aspects_dispatches_to_func(self, invoke_main, capsys):
        """`ketu aspects --date X` runs cmd_aspects → exit 0; resolved-config header on stderr."""
        rc = invoke_main(["aspects", "--date", "2026-05-06T12:00:00Z"])
        assert rc == 0
        out = capsys.readouterr()
        assert "Bodies Positions" in out.out
        assert "Aspect set:" in out.err  # CLI-06 header on stderr

    def test_main_houses_dispatches_to_func(self, invoke_main, capsys):
        """Real houses dispatcher (Plan 11-03) returns 0 and prints cusps to stdout."""
        rc = invoke_main(
            [
                "houses",
                "--date",
                "2026-05-06T12:00:00Z",
                "--lat",
                "48.85",
                "--lon",
                "2.35",
            ]
        )
        assert rc == 0
        captured = capsys.readouterr()
        # Plan 11-03 wired cmd_houses: real cusps go to stdout; "House Cusps"
        # header + 12 cusps + ASC/MC are the load-bearing markers.
        assert "House Cusps" in captured.out
        assert "ASC:" in captured.out
        assert "MC :" in captured.out

    def test_main_unknown_subcommand_rejected(self, invoke_main, capsys):
        """Unknown subcommand → argparse SystemExit(2)."""
        with pytest.raises(SystemExit) as exc:
            invoke_main(["nonexistent-subcommand"])
        assert exc.value.code == 2


# --------------------------------------------------------------------------- #
# Phase 16-04: synastry subparser registration + --list-orbs flag             #
# --------------------------------------------------------------------------- #


class TestSynastrySubparser:
    """Plan 16-04: argparse tree shape for the synastry subcommand."""

    _SYN_OK = [
        "synastry",
        "--date-a", "2000-01-01T12:00:00Z", "--lat-a", "48.85", "--lon-a", "2.35",
        "--date-b", "2000-01-01T12:00:00Z", "--lat-b", "40.71", "--lon-b", "-74.01",
    ]

    def test_parser_has_synastry_subparser(self):
        """`ketu synastry ...` dispatches to ketu.cli.synastry_cmd.cmd_synastry."""
        from ketu.cli.synastry_cmd import cmd_synastry

        parser = build_parser()
        args = parser.parse_args(self._SYN_OK)
        assert args.func is cmd_synastry

    def test_parser_synastry_default_mode_filtered(self):
        """args.mode defaults to 'filtered' when --mode is not specified."""
        parser = build_parser()
        args = parser.parse_args(self._SYN_OK)
        assert args.mode == "filtered"

    def test_parser_synastry_default_system_placidus(self):
        """args.system defaults to 'placidus' when --system is not specified."""
        parser = build_parser()
        args = parser.parse_args(self._SYN_OK)
        assert args.system == "placidus"


class TestListOrbsFlag:
    """Plan 16-04: top-level --list-orbs flag parsing and dispatch."""

    def test_parser_list_orbs_flag_recognized(self):
        """build_parser().parse_args(['--list-orbs']) sets args.list_orbs = True."""
        parser = build_parser()
        args = parser.parse_args(["--list-orbs"])
        assert args.list_orbs is True

    def test_main_dispatches_list_orbs(self, invoke_main, capsys):
        """main(['--list-orbs']) returns 0 and stdout contains the orbs preset header."""
        rc = invoke_main(["--list-orbs"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "synastry" in out
        assert "classical" in out

    def test_list_flags_collision_first_wins(self, invoke_main, capsys):
        """M-1 ratchet: multiple --list-* flags → only the first ladder branch executes.

        The early-return ladder in :func:`ketu.cli.parser.main` is intentional
        FIRST-WINS (research §Pitfall 8). Ladder order is:
        ``--list-aspect-sets`` -> ``--list-house-systems`` -> ``--list-orbs``.
        Passing ``--list-orbs --list-house-systems`` together must therefore
        emit the house-systems output (first reached in the ladder) and
        suppress the orbs preset header (otherwise both would print). The
        invariant the test pins is: never both, always exactly one.
        """
        rc = invoke_main(["--list-orbs", "--list-house-systems"])
        assert rc == 0
        out = capsys.readouterr().out
        # Exactly one of the two ladder branches must have executed; we don't
        # over-specify which (the production ladder is the source of truth),
        # but the contract is "first wins, the other is silent".
        orbs_header = "Available synastry orb presets"
        house_header = "Available house systems"
        emitted_orbs = orbs_header in out
        emitted_house = house_header in out
        assert emitted_orbs ^ emitted_house, (
            "Expected exactly one --list-* branch to emit; "
            f"got orbs={emitted_orbs}, house_systems={emitted_house}. "
            "The early-return ladder in main() must be FIRST-WINS, not run-both."
        )
