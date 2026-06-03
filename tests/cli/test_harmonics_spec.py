"""Unit tests for ketu.cli.harmonics_spec.parse_harmonics_spec."""
from __future__ import annotations

import argparse

import numpy as np
import pytest

from ketu.cli.harmonics_spec import HarmonicsSelection, parse_harmonics_spec


class TestPresetNames:
    """Named presets: classical, traditional, extended, all (case-insensitive)."""

    def test_classical_returns_5_aspect_mask(self):
        sel = parse_harmonics_spec("classical")
        assert isinstance(sel, HarmonicsSelection)
        assert sel.dynamic_specs is None
        mask = sel.mask
        assert isinstance(mask, np.ndarray)
        assert mask.dtype == np.bool_
        assert mask.shape == (14,)
        assert mask.sum() == 5
        # Conjunction (0), Sextile (4), Square (7), Trine (9), Opposition (13)
        assert list(np.where(mask)[0]) == [0, 4, 7, 9, 13]

    def test_traditional_returns_7_aspect_mask(self):
        sel = parse_harmonics_spec("traditional")
        assert sel.dynamic_specs is None
        assert sel.mask.sum() == 7
        # CLASSICAL + Semi-sextile (1) + Quincunx (11)
        assert list(np.where(sel.mask)[0]) == [0, 1, 4, 7, 9, 11, 13]

    def test_extended_returns_14_aspect_mask(self):
        sel = parse_harmonics_spec("extended")
        assert sel.dynamic_specs is None
        assert sel.mask.sum() == 14
        assert sel.mask.all()

    def test_all_aliases_extended(self):
        """'all' is an alias for 'extended' (CLI-02 + ROADMAP backward compat)."""
        sel_all = parse_harmonics_spec("all")
        sel_extended = parse_harmonics_spec("extended")
        assert np.array_equal(sel_all.mask, sel_extended.mask)
        assert sel_all.dynamic_specs is None
        assert sel_extended.dynamic_specs is None

    def test_preset_names_case_insensitive(self):
        for variant in ["CLASSICAL", "Classical", "cLaSsIcAl"]:
            sel = parse_harmonics_spec(variant)
            assert sel.mask.sum() == 5
            assert sel.dynamic_specs is None

    def test_preset_names_strip_whitespace(self):
        sel = parse_harmonics_spec("  classical  ")
        assert sel.mask.sum() == 5
        assert sel.dynamic_specs is None


class TestCommaSeparatedIndices:
    """Explicit aspect-index lists."""

    def test_classical_indices_match_preset(self):
        sel = parse_harmonics_spec("0,4,7,9,13")
        preset = parse_harmonics_spec("classical")
        assert np.array_equal(sel.mask, preset.mask)
        assert sel.dynamic_specs is None
        assert preset.dynamic_specs is None

    def test_single_index_with_comma_accepted(self):
        """'9,' (Trine only) is unambiguous — a list of one — and is accepted."""
        sel = parse_harmonics_spec("9,")
        assert sel.dynamic_specs is None
        assert sel.mask.sum() == 1
        assert sel.mask[9]

    def test_indices_with_whitespace(self):
        sel = parse_harmonics_spec(" 0 , 4 , 7 , 9 , 13 ")
        assert sel.dynamic_specs is None
        assert sel.mask.sum() == 5

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

    def test_comma_only_empty_list_rejected(self):
        """',' → all parts empty → empty harmonics list → ArgumentTypeError (line 140 coverage)."""
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec(",")
        assert "empty" in str(exc.value).lower() or "," in str(exc.value)

    def test_preset_defensive_valueerror_wrapped(self, monkeypatch):
        """Defensive: if resolve_aspect_set raises ValueError for a preset, wrap as ArgumentTypeError."""
        import ketu.cli.harmonics_spec as hs_mod
        import ketu.aspects.presets as presets_mod

        original = presets_mod.resolve_aspect_set

        def patched_resolve(spec):
            if spec == "classical":
                raise ValueError("injected error")
            return original(spec)

        monkeypatch.setattr(hs_mod, "resolve_aspect_set", patched_resolve)
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("classical")
        assert "injected error" in str(exc.value)


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
        assert isinstance(args.harmonics, HarmonicsSelection)
        assert args.harmonics.mask.sum() == 5
        assert args.harmonics.dynamic_specs is None

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


class TestHarmonicTokenF1:
    """HARM-06/07: ^h(\\d+)$ branch; HarmonicsSelection; Tight grammar."""

    def test_h7_accepted_returns_named_tuple(self):
        """h7 returns a HarmonicsSelection NamedTuple."""
        result = parse_harmonics_spec("h7")
        assert isinstance(result, HarmonicsSelection)

    def test_h7_mask_is_all_false(self):
        """h7 mask is length-14 all-False."""
        result = parse_harmonics_spec("h7")
        assert len(result.mask) == 14
        assert result.mask.sum() == 0

    def test_h7_dynamic_specs_has_3_rows(self):
        """h7 → 3 dynamic specs (H7-1/2/3, k=1..3=h//2)."""
        result = parse_harmonics_spec("h7")
        assert len(result.dynamic_specs) == 3

    def test_h7_dynamic_specs_names(self):
        """h7 dynamic spec names are [b'H7-1', b'H7-2', b'H7-3']."""
        result = parse_harmonics_spec("h7")
        assert result.dynamic_specs["name"].tolist() == [b"H7-1", b"H7-2", b"H7-3"]

    def test_H7_uppercase_accepted(self):
        """H7 (uppercase) is accepted (case-insensitive via .lower())."""
        result = parse_harmonics_spec("H7")
        assert isinstance(result, HarmonicsSelection)
        assert len(result.dynamic_specs) == 3

    def test_h2_accepted_1_row(self):
        """h2 → 1 row (k=1, h//2=1), lower boundary."""
        result = parse_harmonics_spec("h2")
        assert isinstance(result, HarmonicsSelection)
        assert len(result.dynamic_specs) == 1

    def test_h64_accepted_32_rows(self):
        """h64 → 32 rows (k=1..32=h//2), upper boundary."""
        result = parse_harmonics_spec("h64")
        assert isinstance(result, HarmonicsSelection)
        assert len(result.dynamic_specs) == 32

    def test_h1_rejected(self):
        """h1 → ArgumentTypeError (degenerate: 1//2=0 rows, range check in generator)."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("h1")

    def test_h65_rejected(self):
        """h65 → ArgumentTypeError (out of range: > 64)."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("h65")

    def test_h0_rejected(self):
        """h0 → ArgumentTypeError (out of range: < 2)."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("h0")

    def test_h7_comma_h11_rejected(self):
        """h7,h11 → ArgumentTypeError (Tight grammar: mixing deferred, comma branch parses int('h7') → fail)."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("h7,h11")

    def test_traditional_comma_h7_rejected(self):
        """traditional,h7 → ArgumentTypeError (Tight grammar: preset+h mixing deferred)."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("traditional,h7")

    def test_argparse_h7_end_to_end(self):
        """parse_args(['--harmonics', 'h7', 'aspects', '--date', ...]) → HarmonicsSelection with 3 specs."""
        from ketu.cli.parser import build_parser
        parser = build_parser()
        args = parser.parse_args([
            "--harmonics", "h7",
            "aspects", "--date", "2026-05-06T12:00:00Z",
        ])
        assert isinstance(args.harmonics, HarmonicsSelection)
        assert args.harmonics.mask.sum() == 0
        assert len(args.harmonics.dynamic_specs) == 3
