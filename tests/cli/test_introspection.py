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
        """HOU2-04: --list-house-systems retourne 6 systèmes triés alphabétiquement."""
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
        out = capsys.readouterr().out
        # All 6 v1.2 systems must appear.
        for name in ("placidus", "koch", "porphyry",
                     "whole_sign", "equal", "regiomontanus"):
            assert name in out, f"system {name!r} missing from --list-house-systems output"

    def test_systems_listed_in_alphabetical_order(self, invoke_main, capsys):
        """D-03 verrouillé: ordre alphabétique déterministe via sorted(SYSTEMS.keys())."""
        invoke_main(["--list-house-systems"])
        out = capsys.readouterr().out
        # Find the line index of each system name; they should be in
        # alphabetical order: equal, koch, placidus, porphyry, regiomontanus, whole_sign.
        expected_order = ["equal", "koch", "placidus", "porphyry", "regiomontanus", "whole_sign"]
        positions = []
        for name in expected_order:
            # Match the formatted line "  NAME ... : ..." (variable padding for long names).
            idx = out.find(f"  {name} ")
            if idx < 0:
                # Long names like 'regiomontanus' may not have a trailing space before ':'
                idx = out.find(f"  {name}")
            assert idx >= 0, f"system {name!r} not found in CLI output"
            positions.append(idx)
        # Verify monotonically increasing.
        assert positions == sorted(positions), (
            f"systems not in alphabetical order; positions: {positions}"
        )

    def test_every_registered_system_has_description(self, invoke_main, capsys):
        """PATTERNS §14.5: no system shall fall through to the
        '(no description available)' default — _SYSTEM_DESCRIPTIONS must
        cover every entry in SYSTEMS."""
        invoke_main(["--list-house-systems"])
        out = capsys.readouterr().out
        assert "(no description available)" not in out, (
            "Some registered system lacks a _SYSTEM_DESCRIPTIONS entry; "
            "extend ketu/cli/introspection.py:_SYSTEM_DESCRIPTIONS."
        )

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

    def test_list_orbs_no_subcommand(self, invoke_main):
        """--list-orbs short-circuits without requiring a subcommand."""
        rc = invoke_main(["--list-orbs"])
        assert rc == 0


class TestListOrbs:
    """Phase 16-04: --list-orbs prints synastry orb presets + formula."""

    def test_cmd_list_orbs_runs_without_error(self, capsys):
        """Calling cmd_list_orbs() directly produces non-empty stdout."""
        from ketu.cli.introspection import cmd_list_orbs

        cmd_list_orbs()
        out = capsys.readouterr().out
        assert out.strip() != ""

    def test_cmd_list_orbs_lists_both_presets(self, capsys):
        """Captured stdout contains both 'synastry' and 'classical' preset names."""
        from ketu.cli.introspection import cmd_list_orbs

        cmd_list_orbs()
        out = capsys.readouterr().out
        assert "synastry" in out
        assert "classical" in out

    def test_cmd_list_orbs_includes_formula_derivation(self, capsys):
        """Captured stdout contains the canonical formula derivation."""
        from ketu.cli.introspection import cmd_list_orbs

        cmd_list_orbs()
        out = capsys.readouterr().out
        assert "(orb[b1] + orb[b2]) / 2 * coef[asp] * factor" in out

    def test_cmd_list_orbs_cites_asc_mc_default(self, capsys):
        """Captured stdout mentions the 8° ASC/MC default natal orb."""
        from ketu.cli.introspection import cmd_list_orbs

        cmd_list_orbs()
        out = capsys.readouterr().out
        # The exact float repr can be '8.0' or '8.0°' depending on format.
        assert "8.0" in out

    def test_cmd_list_orbs_examples_block(self, capsys):
        """Captured stdout contains at least one Sun-Moon example line."""
        from ketu.cli.introspection import cmd_list_orbs

        cmd_list_orbs()
        out = capsys.readouterr().out
        # Conjunction Sun↔Moon example uses the unicode arrow ↔.
        assert "Sun" in out and "Moon" in out and "6.0" in out
