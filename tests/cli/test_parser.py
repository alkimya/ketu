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
        # After Plan 11-02, type=parse_harmonics_spec returns a length-14 mask.
        import numpy as np
        assert isinstance(args.harmonics, np.ndarray)
        assert args.harmonics.dtype == np.bool_
        assert args.harmonics.shape == (14,)
        assert args.harmonics.sum() == 5  # CLASSICAL = 5 majors

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
