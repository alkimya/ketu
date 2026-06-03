"""Tests for ketu.aspects.harmonics — dynamic harmonic generator.

Gives 100% coverage of ``ketu/aspects/harmonics.py`` and guards:
- ASP-04: public generator for any integer h.
- ASP-05: unified 360° convention (fold, mirror-dedup, no 0°/360°, blank symbol).
- ASP-08: frozen core.aspects table untouched; _VALID_HARMONICS never consulted.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from ketu.aspects.harmonics import (
    HARMONIC_DTYPE,
    DynamicAspectSpec,
    _fold_to_0_180,
    generate_harmonic_aspects,
)


# ---------------------------------------------------------------------------
# Dtype tests
# ---------------------------------------------------------------------------


class TestHarmonicDtype:
    """HARMONIC_DTYPE must mirror core.aspects dtype exactly."""

    def test_dtype_field_names(self) -> None:
        """Dtype field names match core.aspects 5-field layout."""
        assert HARMONIC_DTYPE.names == ("name", "angle", "coef", "harmonic", "symbol")

    def test_dtype_field_types(self) -> None:
        """Dtype field types match core.aspects (S16/f4/f4/i4/U4)."""
        assert HARMONIC_DTYPE["name"].kind == "S"
        assert HARMONIC_DTYPE["name"].itemsize == 16
        assert HARMONIC_DTYPE["angle"].kind == "f"
        assert HARMONIC_DTYPE["angle"].itemsize == 4
        assert HARMONIC_DTYPE["coef"].kind == "f"
        assert HARMONIC_DTYPE["coef"].itemsize == 4
        assert HARMONIC_DTYPE["harmonic"].kind == "i"
        assert HARMONIC_DTYPE["harmonic"].itemsize == 4
        assert HARMONIC_DTYPE["symbol"].kind == "U"
        # U4 → 4 chars × 4 bytes/char = 16 bytes on many platforms; verify kind only
        assert HARMONIC_DTYPE["symbol"].kind == "U"

    def test_dtype_matches_core_aspects(self) -> None:
        """HARMONIC_DTYPE is byte-identical to ketu.core.aspects.dtype."""
        from ketu.core import aspects as core_aspects

        assert HARMONIC_DTYPE == core_aspects.dtype


# ---------------------------------------------------------------------------
# Type alias smoke-test
# ---------------------------------------------------------------------------


class TestDynamicAspectSpec:
    """DynamicAspectSpec is importable and is a type alias (not a class)."""

    def test_type_alias_importable(self) -> None:
        assert DynamicAspectSpec is not None

    def test_accepts_none_annotation(self) -> None:
        """None is a valid value for DynamicAspectSpec-typed parameter."""
        value: DynamicAspectSpec = None
        assert value is None

    def test_accepts_single_array(self) -> None:
        specs = generate_harmonic_aspects(7)
        value: DynamicAspectSpec = specs
        assert value is not None

    def test_accepts_list_of_arrays(self) -> None:
        specs = generate_harmonic_aspects(7)
        value: DynamicAspectSpec = [specs, specs]
        assert len(value) == 2


# ---------------------------------------------------------------------------
# _fold_to_0_180 tests
# ---------------------------------------------------------------------------


class TestFoldTo0180:
    """Unit tests for the _fold_to_0_180 helper — gives 100% coverage."""

    def test_already_in_range(self) -> None:
        assert _fold_to_0_180(51.43) == pytest.approx(51.43)

    def test_mirror_folds_to_same_value(self) -> None:
        """308.57 is the mirror of 51.43 (both are k*360/7 and (7-k)*360/7)."""
        assert _fold_to_0_180(308.57) == pytest.approx(51.43, abs=1e-8)

    def test_360_folds_to_0(self) -> None:
        assert _fold_to_0_180(360.0) == pytest.approx(0.0, abs=1e-9)

    def test_180_stays_180(self) -> None:
        assert _fold_to_0_180(180.0) == pytest.approx(180.0)

    def test_270_folds_to_90(self) -> None:
        assert _fold_to_0_180(270.0) == pytest.approx(90.0)

    def test_0_stays_0(self) -> None:
        assert _fold_to_0_180(0.0) == pytest.approx(0.0)

    def test_negative_angle(self) -> None:
        # -90 % 360 = 270, fold(270) = 90
        assert _fold_to_0_180(-90.0) == pytest.approx(90.0)

    def test_large_angle(self) -> None:
        # 540 % 360 = 180
        assert _fold_to_0_180(540.0) == pytest.approx(180.0)

    def test_exactly_half_circle_boundary(self) -> None:
        """180.0 is the boundary — should return 180.0 (not fold further)."""
        result = _fold_to_0_180(180.0)
        assert result == pytest.approx(180.0)
        assert result <= 180.0


# ---------------------------------------------------------------------------
# generate_harmonic_aspects — shape and dtype
# ---------------------------------------------------------------------------


class TestGenerateH7ShapeAndDtype:
    """Task spec: 3 rows; dtype == HARMONIC_DTYPE; field names match."""

    def test_row_count(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert len(specs) == 3

    def test_dtype_equals_harmonic_dtype(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert specs.dtype == HARMONIC_DTYPE

    def test_field_names_match(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert specs.dtype.names == ("name", "angle", "coef", "harmonic", "symbol")

    def test_is_structured_ndarray(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert isinstance(specs, np.ndarray)


# ---------------------------------------------------------------------------
# generate_harmonic_aspects — values
# ---------------------------------------------------------------------------


class TestGenerateH7Values:
    """Task spec: angles, coefs, names, harmonic column, symbols for h=7."""

    def test_names(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert specs["name"].tolist() == [b"H7-1", b"H7-2", b"H7-3"]

    def test_angles(self) -> None:
        specs = generate_harmonic_aspects(7)
        expected = [1 * 360.0 / 7, 2 * 360.0 / 7, 3 * 360.0 / 7]
        assert np.allclose(
            [float(a) for a in specs["angle"]], expected, atol=1e-3
        )

    def test_angle_rounded_values(self) -> None:
        """Spot-check rounded angles (same as doctest)."""
        specs = generate_harmonic_aspects(7)
        angles = [round(float(a), 2) for a in specs["angle"]]
        assert angles == [51.43, 102.86, 154.29]

    def test_coefs(self) -> None:
        specs = generate_harmonic_aspects(7)
        expected = [1 / 7, 2 / 7, 3 / 7]
        assert np.allclose(
            [float(c) for c in specs["coef"]], expected, atol=1e-6
        )

    def test_harmonic_column_all_h(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert all(int(v) == 7 for v in specs["harmonic"])

    def test_symbol_all_blank(self) -> None:
        specs = generate_harmonic_aspects(7)
        assert specs["symbol"].tolist() == ["", "", ""]


# ---------------------------------------------------------------------------
# Even harmonics — never emit 0° or 360°; last row is 180°
# ---------------------------------------------------------------------------


class TestEvenHEmits180NeverO360:
    """Task spec: even h must not emit 0.0 or 360.0; last row must be 180°."""

    @pytest.mark.parametrize("h", [2, 4, 6, 8])
    def test_no_angle_0(self, h: int) -> None:
        specs = generate_harmonic_aspects(h)
        assert not any(float(a) == 0.0 for a in specs["angle"])

    @pytest.mark.parametrize("h", [2, 4, 6, 8])
    def test_no_angle_360(self, h: int) -> None:
        specs = generate_harmonic_aspects(h)
        assert not any(float(a) == 360.0 for a in specs["angle"])

    @pytest.mark.parametrize("h", [2, 4, 6, 8])
    def test_last_row_is_180(self, h: int) -> None:
        specs = generate_harmonic_aspects(h)
        assert float(specs["angle"][-1]) == pytest.approx(180.0, abs=1e-4)

    def test_k_half_gives_180_for_even_h(self) -> None:
        """k = h//2 for even h: k*360/h = 180, fold(180) = 180."""
        for h in (2, 4, 6, 8, 12):
            specs = generate_harmonic_aspects(h)
            assert float(specs["angle"][-1]) == pytest.approx(180.0, abs=1e-4)


# ---------------------------------------------------------------------------
# Mirror deduplication — row count == h // 2
# ---------------------------------------------------------------------------


class TestMirrorDedupRowCount:
    """Task spec: row count must equal h // 2 for several h values."""

    @pytest.mark.parametrize("h,expected", [(2, 1), (4, 2), (5, 2), (7, 3), (12, 6)])
    def test_row_count(self, h: int, expected: int) -> None:
        specs = generate_harmonic_aspects(h)
        assert len(specs) == expected

    @pytest.mark.parametrize("h", range(2, 17))
    def test_row_count_formula(self, h: int) -> None:
        """For all h in [2..16], row count must be h // 2."""
        assert len(generate_harmonic_aspects(h)) == h // 2


# ---------------------------------------------------------------------------
# Invalid h — raises ValueError / TypeError
# ---------------------------------------------------------------------------


class TestInvalidHRaises:
    """Task spec: (1,0,-3,65,128) → ValueError; (True, 2.5, '7') → ValueError/TypeError."""

    @pytest.mark.parametrize("bad", [1, 0, -3, 65, 128])
    def test_out_of_range_raises_value_error(self, bad: int) -> None:
        with pytest.raises(ValueError) as exc_info:
            generate_harmonic_aspects(bad)
        assert len(str(exc_info.value)) > 0

    def test_bool_raises_value_error(self) -> None:
        """True is a bool (subclass of int) — must raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_harmonic_aspects(True)  # type: ignore[arg-type]
        assert "bool" in str(exc_info.value).lower()

    def test_false_raises_value_error(self) -> None:
        """False is a bool (subclass of int) — must raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_harmonic_aspects(False)  # type: ignore[arg-type]
        assert "bool" in str(exc_info.value).lower()

    def test_float_raises_value_error(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            generate_harmonic_aspects(2.5)  # type: ignore[arg-type]
        assert len(str(exc_info.value)) > 0

    def test_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            generate_harmonic_aspects("7")  # type: ignore[arg-type]
        assert len(str(exc_info.value)) > 0

    @pytest.mark.parametrize("bad", [1, 0, -3, 65, 128, True, 2.5, "7"])
    def test_never_raises_index_error(self, bad: object) -> None:
        """An IndexError must NEVER be raised — always ValueError."""
        try:
            generate_harmonic_aspects(bad)  # type: ignore[arg-type]
        except IndexError:
            pytest.fail(f"generate_harmonic_aspects({bad!r}) raised IndexError")
        except (ValueError, TypeError):
            pass  # expected

    @pytest.mark.parametrize("bad", [1, 0, -3, 65, 128, True, 2.5, "7"])
    def test_never_silent_empty_array(self, bad: object) -> None:
        """Must NEVER silently return an empty array — always raise."""
        try:
            result = generate_harmonic_aspects(bad)  # type: ignore[arg-type]
            pytest.fail(
                f"generate_harmonic_aspects({bad!r}) returned {result!r} instead of raising"
            )
        except (ValueError, TypeError):
            pass  # expected


# ---------------------------------------------------------------------------
# Frozen table invariant — ASP-08
# ---------------------------------------------------------------------------


class TestFrozenTableUnchanged:
    """generate_harmonic_aspects must never mutate ketu.core.aspects."""

    def test_table_bytes_identical_before_after(self) -> None:
        """Table bytes are unchanged before and after calling the generator."""
        from ketu.core import aspects

        before = aspects.tobytes()
        generate_harmonic_aspects(7)
        after = aspects.tobytes()
        assert before == after

    def test_v1_sha256_fingerprint(self) -> None:
        """ASP-08: V1 sha256 fingerprint (name+angle+coef) stays byte-identical."""
        from ketu.core import aspects

        EXPECTED_V1 = (
            "c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359"
        )
        h = hashlib.sha256()
        h.update(aspects["name"].tobytes())
        h.update(aspects["angle"].tobytes())
        h.update(aspects["coef"].tobytes())
        assert h.hexdigest() == EXPECTED_V1, (
            f"core.aspects V1 fingerprint changed: got {h.hexdigest()!r}; "
            "the frozen table must not be mutated"
        )

    def test_v1_fingerprint_after_calling_generator(self) -> None:
        """V1 fingerprint holds even AFTER calling the generator."""
        from ketu.core import aspects

        EXPECTED_V1 = (
            "c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359"
        )
        # Call generator for several harmonics
        for h_val in (7, 11, 17, 64):
            generate_harmonic_aspects(h_val)

        h = hashlib.sha256()
        h.update(aspects["name"].tobytes())
        h.update(aspects["angle"].tobytes())
        h.update(aspects["coef"].tobytes())
        assert h.hexdigest() == EXPECTED_V1


# ---------------------------------------------------------------------------
# _VALID_HARMONICS not consulted on the dynamic path — ASP-08
# ---------------------------------------------------------------------------


class TestValidHarmonicsNotConsulted:
    """Generator must succeed for h=7 even though 7 is NOT in _VALID_HARMONICS."""

    def test_7_not_in_valid_harmonics(self) -> None:
        from ketu.aspects.presets import _VALID_HARMONICS

        assert 7 not in _VALID_HARMONICS, (
            "Precondition: 7 must NOT be in _VALID_HARMONICS "
            "for this test to prove the dynamic path is independent"
        )

    def test_generate_h7_succeeds(self) -> None:
        """H7 must work on the dynamic path regardless of _VALID_HARMONICS."""
        specs = generate_harmonic_aspects(7)
        assert len(specs) == 3

    def test_generate_h11_not_in_valid_harmonics(self) -> None:
        from ketu.aspects.presets import _VALID_HARMONICS

        assert 11 not in _VALID_HARMONICS

    def test_generate_h11_succeeds(self) -> None:
        specs = generate_harmonic_aspects(11)
        assert len(specs) == 5  # h//2 = 5

    def test_generate_h17_not_in_valid_harmonics(self) -> None:
        from ketu.aspects.presets import _VALID_HARMONICS

        assert 17 not in _VALID_HARMONICS

    def test_generate_h17_succeeds(self) -> None:
        specs = generate_harmonic_aspects(17)
        assert len(specs) == 8  # h//2 = 8


# ---------------------------------------------------------------------------
# Public export surface
# ---------------------------------------------------------------------------


class TestPublicExports:
    """generate_harmonic_aspects and friends are exported from ketu.aspects."""

    def test_generate_from_ketu_aspects(self) -> None:
        from ketu.aspects import generate_harmonic_aspects as ga

        specs = ga(7)
        assert len(specs) == 3

    def test_harmonic_dtype_from_ketu_aspects(self) -> None:
        from ketu.aspects import HARMONIC_DTYPE as hd

        assert hd.names == ("name", "angle", "coef", "harmonic", "symbol")

    def test_dynamic_aspect_spec_from_ketu_aspects(self) -> None:
        from ketu.aspects import DynamicAspectSpec as das

        assert das is not None
