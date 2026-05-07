"""Tests for the resolved-config header (CLI-06) — STDERR-only contract."""
from __future__ import annotations


class TestResolvedConfigHeaderOnStderr:
    """Header emitted to stderr; stdout is untouched (research §Pattern 4)."""

    def test_aspects_header_on_stderr(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        captured = capsys.readouterr()
        # Header on stderr.
        assert "# Aspect set:" in captured.err
        assert "# Ketu v1.1.0" in captured.err
        # Header NOT on stdout (CLI-03 byte-identical contract).
        assert "# Aspect set:" not in captured.out
        assert "# Ketu v1.1.0" not in captured.out

    def test_classical_label_in_header(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        assert "Aspect set: classical" in err

    def test_extended_label_when_all(self, invoke_main, capsys):
        """`--harmonics all` → header label is 'extended' (canonical name)."""
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        err = capsys.readouterr().err
        assert "Aspect set: extended" in err

    def test_header_lists_aspect_count_and_angles(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        # Classical → 5 aspects.
        assert "5 aspects" in err
        # Some recognizable angle present.
        assert "0°" in err and "180°" in err


class TestHousesResolvedConfigHeader:
    """BLOCKER 2 fix: `ketu houses ...` ALSO emits the resolved-config header on stderr (CLI-06)."""

    def test_houses_emits_house_system_header_on_stderr(self, invoke_main, capsys):
        rc = invoke_main([
            "houses",
            "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "placidus",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "# House system: placidus" in captured.err, (
            f"CLI-06 regression: `ketu houses ... --system placidus` did not emit "
            f"'# House system: placidus' on stderr; got stderr={captured.err!r}"
        )
        # Header must NOT pollute stdout.
        assert "# House system:" not in captured.out

    def test_houses_emits_ketu_version_header_on_stderr(self, invoke_main, capsys):
        invoke_main([
            "houses",
            "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "placidus",
        ])
        err = capsys.readouterr().err
        assert "# Ketu v1.1.0" in err

    def test_houses_header_reflects_chosen_system(self, invoke_main, capsys):
        """Different --system values → different header lines."""
        invoke_main([
            "houses",
            "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "koch",
        ])
        err = capsys.readouterr().err
        assert "# House system: koch" in err

        invoke_main([
            "houses",
            "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "porphyry",
        ])
        err2 = capsys.readouterr().err
        assert "# House system: porphyry" in err2

    def test_houses_does_NOT_emit_aspect_set_header(self, invoke_main, capsys):
        """`houses` is not aspect-related; mask=None and preset_name=None → no 'Aspect set:' line."""
        invoke_main([
            "houses",
            "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "placidus",
        ])
        err = capsys.readouterr().err
        assert "# Aspect set:" not in err


class TestStdoutPristineUnderHarmonicsAll:
    """CLI-03 spirit-check: under --harmonics all, no '# ...' meta-line is on stdout."""

    def test_no_hash_lines_in_stdout(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        for line in out.splitlines():
            # The only `#`-prefixed line allowed on stdout would be a v1.0
            # output line, but v1.0 doesn't emit any. Anything starting
            # with '# ' is a leak from the resolved-config header.
            assert not line.startswith("# "), (
                f"Resolved-config header leaked to stdout: {line!r}"
            )
