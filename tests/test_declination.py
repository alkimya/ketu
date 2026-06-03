"""Unit and vectorization tests for ketu.calculations declination functions.

Covers DECL-01 (scalar), DECL-02 (vectorized), DECL-04 (velocity),
DECL-05 (montant/descendant + β-vs-δ distinction), DECL-06 (OOB).
All 14 bodies (including Chiron id=13) are exercised for DECL-01.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose
from datetime import datetime, timezone

from ketu.calculations import (
    declination,
    declination_velocity,
    is_ascending_declination,
    is_ascending,
    is_out_of_bounds,
    utc_to_julian,
)
from ketu.ephemeris.coordinates import true_obliquity

# ---------------------------------------------------------------------------
# Reference Julian Dates (all verified against the coordinate chain)
# ---------------------------------------------------------------------------

# 2025-01-15 12:00 UTC — Moon decl=+19.8956°, vel=-4.6051°/day (descending δ)
JD_DESC = utc_to_julian(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc))

# 2025-03-07 00:00 TT — Moon decl=+28.6641°, vel=+0.3049°/day (ascending δ)
# AND beta-ascending is False here → proves is_ascending ≠ is_ascending_declination
JD_ASC = 2460742.0

# 2025-01-01 00:00 TT — Moon decl=-25.8853°, OOB (|δ| > ε ≈ 23.44°)
JD_OOB = 2460676.5

# 2025-06-15 12:00 UTC — Moon decl=-19.72°, in-bounds (|δ| < ε)
JD_INBOUNDS = utc_to_julian(datetime(2025, 6, 15, 12, 0, tzinfo=timezone.utc))


# ---------------------------------------------------------------------------
# DECL-01 — scalar declination
# ---------------------------------------------------------------------------


class TestDeclinationScalar:
    """DECL-01: declination(jdate, body) scalar path."""

    def test_returns_float(self):
        """Should return a Python/NumPy float for scalar jdate."""
        result = declination(JD_DESC, 1)
        assert isinstance(result, (float, np.floating))

    def test_moon_in_valid_range(self):
        """Moon declination must lie within [−90, +90]."""
        d = declination(JD_DESC, 1)
        assert -90.0 <= d <= 90.0

    def test_moon_known_value(self):
        """Moon at 2025-01-15: δ ≈ +19.8956° (north, agrees with coordinates chain)."""
        d = declination(JD_DESC, 1)
        assert_allclose(d, 19.8956, atol=1e-3)

    def test_sun_near_solstice_sign(self):
        """Sun in January has positive (north) declination near −23° (winter solstice past).

        More precisely the Sun has negative (south) declination in January in the Northern
        hemisphere perspective.  At JD_DESC (2025-01-15) the Sun δ ≈ −21°.
        """
        d = declination(JD_DESC, 0)
        assert -90.0 <= d <= 90.0
        # In January the Sun is south of the equator
        assert d < 0.0

    def test_north_positive_south_negative_convention(self):
        """At JD_ASC the Moon δ is ~28.66°, confirming north = positive."""
        d = declination(JD_ASC, 1)
        assert d > 0.0

    def test_all_14_bodies_finite_and_in_range(self):
        """DECL-01 extended: all 14 bodies return finite δ in [−90, +90]."""
        for body_id in range(14):
            d = declination(JD_DESC, body_id)
            assert np.isfinite(d), f"body {body_id}: not finite"
            assert -90.0 <= d <= 90.0, f"body {body_id}: {d} out of [−90,+90]"


# ---------------------------------------------------------------------------
# DECL-02 — vectorized declination
# ---------------------------------------------------------------------------


class TestDeclinationVectorized:
    """DECL-02: declination(jdate_array, body) array path."""

    def test_returns_ndarray_for_array_input(self):
        """Array jdate must return a numpy.ndarray, not a scalar."""
        jd_arr = np.array([JD_DESC, JD_DESC + 1.0, JD_DESC + 7.0])
        result = declination(jd_arr, 1)
        assert isinstance(result, np.ndarray)

    def test_shape_preserved(self):
        """Output shape must equal the input array shape."""
        jd_arr = np.array([JD_DESC, JD_DESC + 1.0, JD_DESC + 7.0, JD_DESC + 14.0])
        result = declination(jd_arr, 1)
        assert result.shape == jd_arr.shape

    def test_array_matches_per_element_scalar(self):
        """Array result must be element-wise equal to individual scalar calls."""
        jd_arr = np.array([JD_DESC, JD_DESC + 1.0, JD_DESC + 7.0])
        result_arr = declination(jd_arr, 1)
        for i, jd in enumerate(jd_arr):
            result_scalar = declination(float(jd), 1)
            assert_allclose(result_arr[i], result_scalar, atol=1e-12,
                            err_msg=f"Mismatch at index {i}")

    def test_all_values_in_valid_range(self):
        """All elements of the array result must lie in [−90, +90]."""
        jd_arr = np.linspace(JD_DESC, JD_DESC + 27.0, 20)
        result = declination(jd_arr, 1)
        assert np.all(result >= -90.0) and np.all(result <= 90.0)

    def test_all_values_finite(self):
        """All elements of the array result must be finite."""
        jd_arr = np.linspace(JD_DESC, JD_DESC + 27.0, 20)
        result = declination(jd_arr, 1)
        assert np.all(np.isfinite(result))


# ---------------------------------------------------------------------------
# DECL-04 — declination_velocity
# ---------------------------------------------------------------------------


class TestDeclinationVelocity:
    """DECL-04: declination_velocity(jdate, body)."""

    def test_returns_float(self):
        """Should return a float for scalar input."""
        vel = declination_velocity(JD_DESC, 1)
        assert isinstance(vel, (float, np.floating))

    def test_finite(self):
        """Velocity must be finite."""
        vel = declination_velocity(JD_DESC, 1)
        assert np.isfinite(vel)

    def test_matches_manual_forward_fd(self):
        """declination_velocity IS the forward FD — assert exact equality."""
        step = 0.01
        manual = (declination(JD_DESC + step, 1) - declination(JD_DESC, 1)) / step
        vel = declination_velocity(JD_DESC, 1)
        assert vel == manual, f"FD mismatch: {vel} vs {manual}"

    def test_known_value_descending(self):
        """At 2025-01-15, Moon decl velocity ≈ −4.6051°/day (descending)."""
        vel = declination_velocity(JD_DESC, 1)
        assert_allclose(vel, -4.6051, atol=1e-3)

    def test_known_value_ascending(self):
        """At JD_ASC, Moon decl velocity is positive (ascending)."""
        vel = declination_velocity(JD_ASC, 1)
        assert vel > 0.0

    def test_no_wraparound_artifact(self):
        """Velocity must be small/smooth near δ→0 crossings.

        At a zero-crossing, δ passes through 0 continuously — there should be
        no ±360-style wraparound artifact. Find a zero-crossing in the scan
        window and assert |vel| < 20°/day (far below the 360°/day artifact level).
        """
        # Scan 30 days, find where δ changes sign (zero crossing)
        jd_arr = np.linspace(JD_DESC, JD_DESC + 30.0, 300)
        decl_arr = declination(jd_arr, 1)
        sign_changes = np.where(np.diff(np.sign(decl_arr)))[0]
        assert len(sign_changes) > 0, "No sign change found in 30-day window"
        crossing_jd = jd_arr[sign_changes[0]]
        vel_at_crossing = declination_velocity(crossing_jd, 1)
        # Wraparound would produce |vel| ~ 360; real velocity << 20°/day for Moon
        assert abs(vel_at_crossing) < 20.0, (
            f"Possible wraparound: vel={vel_at_crossing:.2f} at crossing jd={crossing_jd:.2f}"
        )

    def test_velocity_all_14_bodies_finite(self):
        """Velocity must be finite for all 14 bodies."""
        for body_id in range(14):
            vel = declination_velocity(JD_DESC, body_id)
            assert np.isfinite(vel), f"body {body_id}: velocity not finite"


# ---------------------------------------------------------------------------
# DECL-05 — is_ascending_declination + β-vs-δ distinction
# ---------------------------------------------------------------------------


class TestIsAscendingDeclination:
    """DECL-05: is_ascending_declination(jdate, body)."""

    def test_returns_bool(self):
        """Should return a Python bool."""
        result = is_ascending_declination(JD_DESC, 1)
        assert isinstance(result, bool)

    def test_false_when_velocity_negative(self):
        """False when dδ/dt < 0 (descending at JD_DESC)."""
        assert not is_ascending_declination(JD_DESC, 1)
        # Cross-check with velocity
        assert declination_velocity(JD_DESC, 1) < 0

    def test_true_when_velocity_positive(self):
        """True when dδ/dt > 0 (ascending at JD_ASC)."""
        assert is_ascending_declination(JD_ASC, 1)
        # Cross-check with velocity
        assert declination_velocity(JD_ASC, 1) > 0

    def test_matches_velocity_sign(self):
        """is_ascending_declination must be True iff dδ/dt > 0."""
        for jd in [JD_DESC, JD_ASC, JD_OOB, JD_INBOUNDS]:
            vel = declination_velocity(jd, 1)
            expected = bool(vel > 0)
            actual = is_ascending_declination(jd, 1)
            assert actual == expected, (
                f"jd={jd}: is_ascending_decl={actual}, but vel={vel:.4f} → expected={expected}"
            )

    def test_distinct_from_beta_is_ascending_at_jd_asc(self):
        """At JD_ASC: is_ascending_declination(Moon) = True but is_ascending(Moon) = False.

        Proves the two quantities are INDEPENDENT — they can disagree on the same date.
        (is_ascending measures dβ/dt; is_ascending_declination measures dδ/dt.)
        """
        decl_asc = is_ascending_declination(JD_ASC, 1)
        beta_asc = is_ascending(JD_ASC, 1)
        assert decl_asc is True, f"Expected is_ascending_declination=True at JD_ASC, got {decl_asc}"
        assert beta_asc is False, f"Expected is_ascending=False at JD_ASC, got {beta_asc}"
        assert decl_asc != beta_asc, "Pitfall-1 guard: the two ascending flags must disagree here"

    def test_all_14_bodies_returns_bool(self):
        """is_ascending_declination must return bool for all 14 bodies."""
        for body_id in range(14):
            result = is_ascending_declination(JD_DESC, body_id)
            assert isinstance(result, bool), f"body {body_id}: expected bool, got {type(result)}"


# ---------------------------------------------------------------------------
# DECL-06 — is_out_of_bounds
# ---------------------------------------------------------------------------


class TestIsOutOfBounds:
    """DECL-06: is_out_of_bounds(jdate, body)."""

    def test_returns_bool(self):
        """Should return a Python bool."""
        result = is_out_of_bounds(JD_DESC, 1)
        assert isinstance(result, bool)

    def test_false_when_inbounds(self):
        """Moon at JD_DESC: |δ| ≈ 19.9° < ε ≈ 23.44° → False."""
        assert not is_out_of_bounds(JD_DESC, 1)

    def test_false_when_inbounds_june(self):
        """Moon at JD_INBOUNDS (June): |δ| ≈ 19.7° < ε → False."""
        assert not is_out_of_bounds(JD_INBOUNDS, 1)

    def test_true_when_oob(self):
        """Moon at JD_OOB: |δ| ≈ 25.9° > ε ≈ 23.44° → True (major standstill 2025)."""
        assert is_out_of_bounds(JD_OOB, 1)

    def test_true_at_jd_asc(self):
        """Moon at JD_ASC: |δ| ≈ 28.66° > ε → True."""
        assert is_out_of_bounds(JD_ASC, 1)

    def test_matches_true_obliquity_threshold(self):
        """is_out_of_bounds must equal |δ| > true_obliquity(jd), not mean_obliquity."""
        for jd in [JD_DESC, JD_OOB, JD_INBOUNDS, JD_ASC]:
            d = declination(jd, 1)
            eps = true_obliquity(jd)
            expected = bool(abs(d) > eps)
            actual = is_out_of_bounds(jd, 1)
            assert actual == expected, (
                f"jd={jd}: is_oob={actual}, |δ|={abs(d):.4f}, ε={eps:.4f} → expected={expected}"
            )

    def test_sun_never_oob(self):
        """The Sun's declination is bounded by the obliquity by definition; OOB = False."""
        # The Sun's maximum δ ≈ ε at solstice — may equal but not exceed
        # Scan 1 year: Sun should never be OOB
        jd_arr = np.linspace(JD_DESC, JD_DESC + 365.0, 50)
        for jd in jd_arr:
            d = float(declination(float(jd), 0))
            eps = true_obliquity(float(jd))
            # Sun |δ| ≤ ε by the geometry of the ecliptic; allow tiny FP tolerance
            assert abs(d) <= eps + 1e-6, (
                f"Sun OOB at jd={jd:.1f}: |δ|={abs(d):.4f} > ε={eps:.4f}"
            )

    def test_all_14_bodies_returns_bool(self):
        """is_out_of_bounds must return bool for all 14 bodies."""
        for body_id in range(14):
            result = is_out_of_bounds(JD_DESC, body_id)
            assert isinstance(result, bool), f"body {body_id}: expected bool, got {type(result)}"
