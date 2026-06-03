"""End-to-end tests for `ketu aspects ...` subcommand."""
from __future__ import annotations

import pytest


class TestAspectsCmdDefaultClassical:
    """Without --harmonics, CLASSICAL (5 majors) is the default (Phase 9)."""

    def test_default_classical_runs(self, invoke_main, capsys):
        rc = invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Bodies Positions" in out
        assert "Bodies Aspects" in out

    def test_default_classical_header_on_stderr(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        assert "Aspect set: classical" in err


class TestAspectsCmdHarmonicsAll:
    """--harmonics all matches v1.0 14-aspect output structure."""

    def test_all_runs_and_header_says_extended(self, invoke_main, capsys):
        """'all' aliases 'extended' — header label resolves to 'extended'."""
        rc = invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Bodies Aspects" in captured.out
        # 'all' → mask of 14 Trues → label = 'extended' (canonical name).
        assert "Aspect set: extended" in captured.err


class TestAspectsCmdTimingExampleAlwaysEmitted:
    """Research Open Question 2 resolution: trailing 'Aspect Timing Example' ALWAYS emitted."""

    def test_timing_example_present_under_classical(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out

    def test_timing_example_present_under_all(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out

    def test_timing_example_present_under_traditional(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "traditional",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out


class TestAspectsCmdCustomMask:
    """--harmonics <custom-list> → header label 'custom' (covers _preset_label_for_mask)."""

    def test_custom_mask_header_says_custom(self, invoke_main, capsys):
        """Indices not matching any preset → label 'custom' in header."""
        invoke_main([
            "--harmonics", "0,4",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        err = capsys.readouterr().err
        assert "Aspect set: custom" in err


class TestAspectsCmdHarmonicsList:
    """--harmonics 0,4,7,9,13 == classical."""

    def test_explicit_classical_indices_match_named_classical(self, invoke_main, capsys):
        rc1 = invoke_main([
            "--harmonics", "0,4,7,9,13",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out1 = capsys.readouterr().out
        rc2 = invoke_main([
            "--harmonics", "classical",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out2 = capsys.readouterr().out
        assert rc1 == 0 and rc2 == 0
        # Aspect content (everything between "Bodies Aspects" and "Aspect Timing Example")
        # should match — same mask → same aspects.

        def aspects_block(s: str) -> str:
            i = s.find("Bodies Aspects")
            j = s.find("Aspect Timing Example", i)
            return s[i:j] if (i >= 0 and j >= 0) else s
        assert aspects_block(out1) == aspects_block(out2)


class TestAspectsCmdRejectsBareInteger:
    """CLI-02 / Pitfall 9: --harmonics 12 → SystemExit(2) on stderr."""

    def test_bare_int_rejected_via_cli(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "--harmonics", "12",
                "aspects", "--date", "2000-01-01T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "bare integer" in err
        assert "named preset" in err


class TestAspectsCmdUsesDegreeCharFromDisplay:
    """BLOCKER 1 fix verification: aspects output uses the v1.0 'º' (U+00BA), not '°'."""

    def test_aspects_output_uses_u00ba_degree_char(self, invoke_main, capsys):
        """Sanity check that the aspects loop renders 'º' (U+00BA), not '°' (U+00B0).

        Plan 11-06 will pin this byte-for-byte against the v1.0 fixture; this
        test gives an earlier, more diagnostic signal if `display.print_aspects`
        ever drifts.
        """
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        out = capsys.readouterr().out
        i = out.find("Bodies Aspects")
        j = out.find("Aspect Timing Example", i)
        aspects_block = out[i:j] if (i >= 0 and j >= 0) else out
        # Must contain U+00BA (the v1.0 character).
        assert "º" in aspects_block, (
            "BLOCKER 1 regression: aspects block missing U+00BA 'º' "
            "(MASCULINE ORDINAL INDICATOR); v1.0 used this character. "
            "Did someone replace it with U+00B0 '°' (DEGREE SIGN)?"
        )
        # Must NOT contain U+00B0 in the aspects block specifically.
        # (It's allowed elsewhere on stdout if some other future feature uses it,
        # but the aspects block must match v1.0 exactly.)
        assert "°" not in aspects_block, (
            "BLOCKER 1 regression: aspects block contains U+00B0 '°' "
            "(DEGREE SIGN); v1.0 used U+00BA 'º' (MASCULINE ORDINAL INDICATOR)."
        )


class TestAspectsCmdHarmonicsH7:
    """HARM-06/07: --harmonics h7 end-to-end (F1 debt, Plan 34-03)."""

    def test_h7_runs_and_shows_synthetic_names(self, invoke_main, capsys):
        """--harmonics h7 runs (rc=0); stdout has H7-k names; no Quadrinovile."""
        rc = invoke_main([
            "--harmonics", "h7",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "H7-" in out
        assert "Quadrinovile" not in out

    def test_h7_header_says_h7(self, invoke_main, capsys):
        """Stderr header contains '# Aspect set: h7'."""
        invoke_main([
            "--harmonics", "h7",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        err = capsys.readouterr().err
        assert "# Aspect set: h7" in err

    def test_h7_timing_example_still_classical(self, invoke_main, capsys):
        """The always-on classical-pinned 'Aspect Timing Example' block is still emitted."""
        invoke_main([
            "--harmonics", "h7",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out
