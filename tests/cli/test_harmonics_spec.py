"""Unit tests for ketu.cli.harmonics_spec.parse_harmonics_spec."""
from __future__ import annotations

import argparse

import numpy as np
import pytest

from ketu.cli.harmonics_spec import parse_harmonics_spec


class TestPresetNames:
    """Named presets: classical, traditional, extended, all (case-insensitive)."""

    def test_classical_returns_5_aspect_mask(self):
        mask = parse_harmonics_spec("classical")
        assert isinstance(mask, np.ndarray)
        assert mask.dtype == np.bool_
        assert mask.shape == (14,)
        assert mask.sum() == 5
        # Conjunction (0), Sextile (4), Square (7), Trine (9), Opposition (13)
        assert list(np.where(mask)[0]) == [0, 4, 7, 9, 13]

    def test_traditional_returns_7_aspect_mask(self):
        mask = parse_harmonics_spec("traditional")
        assert mask.sum() == 7
        # CLASSICAL + Semi-sextile (1) + Quincunx (11)
        assert list(np.where(mask)[0]) == [0, 1, 4, 7, 9, 11, 13]

    def test_extended_returns_14_aspect_mask(self):
        mask = parse_harmonics_spec("extended")
        assert mask.sum() == 14
        assert mask.all()

    def test_all_aliases_extended(self):
        """'all' is an alias for 'extended' (CLI-02 + ROADMAP backward compat)."""
        mask_all = parse_harmonics_spec("all")
        mask_extended = parse_harmonics_spec("extended")
        assert np.array_equal(mask_all, mask_extended)

    def test_preset_names_case_insensitive(self):
        for variant in ["CLASSICAL", "Classical", "cLaSsIcAl"]:
            mask = parse_harmonics_spec(variant)
            assert mask.sum() == 5

    def test_preset_names_strip_whitespace(self):
        mask = parse_harmonics_spec("  classical  ")
        assert mask.sum() == 5


class TestCommaSeparatedIndices:
    """Explicit aspect-index lists."""

    def test_classical_indices_match_preset(self):
        mask = parse_harmonics_spec("0,4,7,9,13")
        preset = parse_harmonics_spec("classical")
        assert np.array_equal(mask, preset)

    def test_single_index_with_comma_accepted(self):
        """'9,' (Trine only) is unambiguous — a list of one — and is accepted."""
        mask = parse_harmonics_spec("9,")
        assert mask.sum() == 1
        assert mask[9]

    def test_indices_with_whitespace(self):
        mask = parse_harmonics_spec(" 0 , 4 , 7 , 9 , 13 ")
        assert mask.sum() == 5

    def test_out_of_range_index_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("0,99")
        assert "0,99" in str(exc.value) or "99" in str(exc.value)

    def test_non_integer_in_list_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("0,foo,7")
        assert "0,foo,7" in str(exc.value)


class TestBareIntegerRejection:
    """REQUIREMENTS.md line 101 + research Pitfall 5: bare integer must reject."""

    def test_bare_integer_12_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("12")
        msg = str(exc.value)
        assert "bare integer" in msg
        assert "named preset" in msg or "preset" in msg

    def test_bare_integer_0_rejected(self):
        """Even '0' (which would be a valid index in a list) rejects when bare."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("0")

    def test_bare_integer_9_rejected(self):
        """Even '9' (Trine) rejects when bare — must use '9,' or 'classical'."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("9")


class TestInvalidInputs:
    """Empty / whitespace / unrecognized."""

    def test_empty_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("   ")

    def test_unrecognized_word_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("foobar")
        assert "foobar" in str(exc.value)


class TestArgparseIntegration:
    """End-to-end: parser.parse_args(['--harmonics', '12', ...]) → SystemExit(2)."""

    def test_argparse_renders_bare_integer_error_cleanly(self, capsys):
        """Bare-integer rejection surfaces via argparse's standard error path."""
        from ketu.cli.parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([
                "--harmonics", "12",
                "aspects", "--date", "2026-05-06T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--harmonics" in err
        assert "bare integer" in err

    def test_argparse_classical_returns_5_aspect_mask(self):
        from ketu.cli.parser import build_parser
        parser = build_parser()
        args = parser.parse_args([
            "--harmonics", "classical",
            "aspects", "--date", "2026-05-06T12:00:00Z",
        ])
        assert args.harmonics.sum() == 5

    def test_argparse_default_is_none(self):
        """Without --harmonics, args.harmonics is None (resolved to CLASSICAL by aspects_cmd in 11-04)."""
        from ketu.cli.parser import build_parser
        parser = build_parser()
        args = parser.parse_args(["aspects", "--date", "2026-05-06T12:00:00Z"])
        assert args.harmonics is None

    def test_argparse_renders_unrecognized_error(self, capsys):
        from ketu.cli.parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([
                "--harmonics", "foobar",
                "aspects", "--date", "2026-05-06T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "foobar" in err
