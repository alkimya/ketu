"""
Tests for find_aspect_timing dyn_coef= parameter (ASP-F3, HARM-04/05).

Dedicated test file so it does not collide with Plan 01's edits to
tests/test_dynamic_harmonics.py.

HARM-04: find_aspect_timing derives orb from dyn_coef via
         (bodies['orb'][b1] + bodies['orb'][b2]) / 2 * dyn_coef
         — identical formula to calculate_aspects lines 215-216.

HARM-05: static path + explicit-orb escape hatch backward-compatible and
         byte-identical; precedence (explicit orb wins silently when both
         given) defined and tested; off-table-no-args still raises ValueError.
"""

import pytest

from ketu.aspects.calculator import find_aspect_timing
from ketu.core import bodies

# Reference date: J2000.0
JD = 2451545.0

# H7-1 angle (septile) — off-table, so static path raises ValueError.
H7_1_ANGLE = 51.4286


class TestFindAspectTimingF3:
    """Test the dyn_coef= orb-derivation extension (HARM-04 + HARM-05)."""

    def test_dyn_coef_derives_orb_internally(self) -> None:
        """
        Calling with dyn_coef= must NOT raise — it derives the orb internally.

        Covers the new ``dyn_coef is not None`` branch (HARM-04).
        """
        result = find_aspect_timing(JD, 0, 1, H7_1_ANGLE, dyn_coef=1 / 7)
        assert isinstance(result, tuple)
        assert len(result) == 3
        jd_begin, exact_jd, jd_end = result
        assert isinstance(jd_begin, float)
        assert isinstance(exact_jd, float)
        assert isinstance(jd_end, float)

    def test_dyn_coef_orb_matches_calculate_aspects_formula(self) -> None:
        """
        Orb derived via dyn_coef must equal the orb from the same formula.

        Computes expected_orb = (orb_b1 + orb_b2) / 2 * coef and asserts that
        find_aspect_timing(dyn_coef=) gives the same result as
        find_aspect_timing(orb=expected_orb).  Proves the derived orb is
        byte-identical to the explicit one (HARM-04 cross-check).
        """
        coef = 1 / 7
        expected_orb = (
            float(bodies["orb"][0]) + float(bodies["orb"][1])
        ) / 2 * coef

        result_dyn = find_aspect_timing(JD, 0, 1, H7_1_ANGLE, dyn_coef=coef)
        result_explicit = find_aspect_timing(JD, 0, 1, H7_1_ANGLE, orb=expected_orb)
        assert result_dyn == result_explicit

    def test_static_path_unchanged(self) -> None:
        """
        The static path (no orb, no dyn_coef) must be byte-identical with or
        without dyn_coef=None spelled out (HARM-05 backward compatibility).
        """
        result_default = find_aspect_timing(JD, 0, 1, 120.0)
        result_explicit_none = find_aspect_timing(JD, 0, 1, 120.0, dyn_coef=None)
        assert result_default == result_explicit_none

    def test_explicit_orb_wins_over_dyn_coef(self) -> None:
        """
        When both orb= and dyn_coef= are given, explicit orb wins silently.

        Uses explicit_orb=3.0 and coef=1/7 (which would derive ~1.71°, a
        different value).  Asserts that the two-argument call returns the same
        result as the orb-only call — proving orb wins without raising
        (HARM-05 locked precedence: NOT ValueError, silent win).
        """
        explicit_orb = 3.0
        coef = 1 / 7
        # Sanity: derived orb ≠ explicit (otherwise the test would be vacuous)
        derived_orb = (
            float(bodies["orb"][0]) + float(bodies["orb"][1])
        ) / 2 * coef
        assert abs(derived_orb - explicit_orb) > 0.01, (
            "derived and explicit orbs must differ for this test to be meaningful"
        )

        result_orb_only = find_aspect_timing(JD, 0, 1, H7_1_ANGLE, orb=explicit_orb)
        result_both = find_aspect_timing(
            JD, 0, 1, H7_1_ANGLE, orb=explicit_orb, dyn_coef=coef
        )
        assert result_orb_only == result_both

    def test_off_table_no_orb_no_dyn_coef_raises(self) -> None:
        """
        Off-table angle with neither orb nor dyn_coef must raise ValueError.

        Proves the static-path ValueError is preserved after the 3-branch
        refactor (HARM-05).
        """
        with pytest.raises(ValueError, match="unknown aspect value"):
            find_aspect_timing(JD, 0, 1, H7_1_ANGLE)
