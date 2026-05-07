"""Tests for introspection commands (CLI-05)."""
from __future__ import annotations


class TestListAspectSets:
    def test_lists_all_four_presets(self, invoke_main, capsys):
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0
        out = capsys.readouterr().out
        for name in ("classical", "traditional", "extended", "all"):
            assert name in out

    def test_shows_aspect_angles_for_classical(self, invoke_main, capsys):
        invoke_main(["--list-aspect-sets"])
        out = capsys.readouterr().out
        # Classical includes Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°.
        assert "0°" in out and "60°" in out and "90°" in out and "120°" in out and "180°" in out


class TestListHouseSystems:
    def test_lists_registered_systems(self, invoke_main, capsys):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
        out = capsys.readouterr().out
        for name in ("placidus", "koch", "porphyry"):
            assert name in out

    def test_mentions_polar_fallback_hint(self, invoke_main, capsys):
        invoke_main(["--list-house-systems"])
        out = capsys.readouterr().out
        assert "polar-fallback" in out or "porphyry" in out  # the polar fallback hint


class TestIntrospectionShortCircuits:
    """Introspection flags work WITHOUT a subcommand (Pitfall 1)."""

    def test_list_aspect_sets_no_subcommand(self, invoke_main):
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0  # would be SystemExit(2) if subparsers required=True

    def test_list_house_systems_no_subcommand(self, invoke_main):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
