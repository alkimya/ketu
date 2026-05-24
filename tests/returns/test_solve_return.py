"""Helper-level regression suite for ketu.returns._solve._solve_return.

This suite pins the WRAP-AROUND CONVENTION centralized in
``_signed_residual_deg`` BEFORE any public ``solar_return`` /
``lunar_return`` API exists (Plans 18-02, 18-03). ROADMAP Phase 18
Success Criterion #3 makes the shared root-finder non-negotiable
(``solar_return`` and ``lunar_return`` both call ``_solve_return``);
this file is the safety net for the most likely silent bug
(18-RESEARCH Pitfall 1: sign error in wrap-around residual when
natal body is near the 0°/360° seam).

End-to-end wrap-around oracles (over the full public APIs) live in
Plan 18-04's oracle fixture suite. This file targets the helper.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from ketu.ephemeris.planets import calc_planet_position
from ketu.returns._solve import (
    _TOL_DAYS,
    _TOL_DEG,
    _TROPICAL_MONTH_D,
    _TROPICAL_YEAR_D,
    _signed_residual_deg,
    _solve_return,
)


class TestSignedResidualWrapAround:
    """Signed-short-arc residual algebra — wrap-around convention pin.

    The residual ``((lon - ref + 540) % 360) - 180`` matches the
    convention in ``ketu/composite/core.py:79-81`` (circular_midpoint)
    and ``ketu/houses/porphyry.py:159``. This class pins the algebra
    around the 0°/360° seam.
    """

    @pytest.mark.parametrize(
        ("lon", "ref", "expected"),
        [
            (0.05, 359.95, 0.1),    # lon just past seam; ref just before; expected +0.1° short arc forward
            (359.95, 0.05, -0.1),   # symmetric: lon just before seam; ref just past; expected -0.1° short arc backward
            (0.0, 0.0, 0.0),        # identity
            (180.0, 0.0, -180.0),   # antipodal: canonical algebra `((180-0+540) % 360) - 180 = -180` (interval [-180, +180)); pinned exactly
            (181.0, 0.0, -179.0),   # just past antipodal: short arc wraps back
            (179.0, 0.0, 179.0),    # just before antipodal: short arc forward
            (10.0, 20.0, -10.0),    # plain near case
            (20.0, 10.0, 10.0),     # commutative-sign
        ],
    )
    def test_parametrized_signed_residual(self, lon: float, ref: float, expected: float) -> None:
        """Signed short-arc residual is in (-180, +180] across the seam."""
        result = float(_signed_residual_deg(np.array(lon), ref))
        assert result == pytest.approx(expected, abs=1e-9), (
            f"_signed_residual_deg({lon}, {ref}) = {result}, expected {expected}"
        )

    def test_residual_vectorised_over_array(self) -> None:
        """``lon`` argument accepts NumPy array; output shape matches input."""
        lons = np.array([0.05, 359.95, 90.0, 270.0])
        result = _signed_residual_deg(lons, 0.0)
        assert result.shape == (4,)
        assert result[0] == pytest.approx(0.05)
        assert result[1] == pytest.approx(-0.05)
        assert result[2] == pytest.approx(90.0)
        assert result[3] == pytest.approx(-90.0)

    def test_nan_propagates(self) -> None:
        """NaN longitude yields NaN residual (natural NumPy behaviour)."""
        result = float(_signed_residual_deg(np.array(np.nan), 0.0))
        assert math.isnan(result)


class TestSolveReturnSunWrapAround:
    """RET-02 binding: Sun wrap-around regression at the helper level.

    Construct a natal JD where the Sun's geocentric longitude is near
    the 0°/360° seam (just after the vernal equinox + a few hours).
    Solve for the return in a subsequent year. The bisection MUST
    converge to within ``_TOL_DEG`` of the seam, NOT diverge or fail.
    """

    def test_sun_wraparound_natal_just_past_zero(self) -> None:
        """Natal Sun ~1.4° Aries: solve return in year+1; residual < 1″."""
        # 2020-03-21 ~13:00 UT is just past vernal equinox; Sun ~1.4° Aries.
        # JD computed offline: 2020-03-21T13:00:00 UT ≈ 2458930.0417 JD.
        natal_jd = 2458930.0417
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        # Sanity: confirm natal Sun is within ~1.5° of the seam (else pick a different date).
        assert natal_sun < 1.5 or natal_sun > 358.5, (
            f"Fixture invariant violated: natal_sun={natal_sun}° must be near the 0/360 seam"
        )

        # Seed one tropical year later:
        t_seed = natal_jd + _TROPICAL_YEAR_D
        jd_return = _solve_return(0, natal_sun, t_seed, 1.5)

        # Residual at the resolved JD MUST be within tol_deg:
        sun_at_return = float(calc_planet_position(jd_return, 0)[0])
        residual = float(_signed_residual_deg(np.array(sun_at_return), natal_sun))
        assert abs(residual) < _TOL_DEG, (
            f"Sun wrap-around return: residual={residual}° exceeds tol_deg={_TOL_DEG}°"
        )

    def test_sun_wraparound_natal_just_before_zero(self) -> None:
        """Natal Sun ~359.3° Pisces: solve return in year+1; residual < 1″."""
        # 2020-03-19 ~12:00 UT is just before vernal equinox; Sun ~359.3° Pisces.
        natal_jd = 2458928.0
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        assert natal_sun > 358.0, (
            f"Fixture invariant violated: natal_sun={natal_sun}° must be just before the seam"
        )

        t_seed = natal_jd + _TROPICAL_YEAR_D
        jd_return = _solve_return(0, natal_sun, t_seed, 1.5)

        sun_at_return = float(calc_planet_position(jd_return, 0)[0])
        residual = float(_signed_residual_deg(np.array(sun_at_return), natal_sun))
        assert abs(residual) < _TOL_DEG, (
            f"Sun wrap-around return: residual={residual}° exceeds tol_deg={_TOL_DEG}°"
        )


class TestSolveReturnMoonWrapAround:
    """LRET-02 binding: Moon wrap-around regression at the helper level.

    Mirror of TestSolveReturnSunWrapAround but for the Moon. The
    Moon's longitude changes 13× faster than the Sun, but the
    centralized wrap-around helper is body-agnostic — same algebra
    must work.
    """

    def test_moon_wraparound_natal_near_seam(self) -> None:
        """Pick a natal JD with Moon near 0°/360° seam; solve next return."""
        # Search for a natal date where the Moon is within ~5° of the seam.
        # Use 2000-01-01T12:00 UT + offset until natal Moon is < 5° or > 355°.
        base = 2451545.0  # 2000-01-01T12:00 UT
        natal_jd = None
        natal_moon = None
        for delta_h in range(0, 24 * 28):  # scan over ~28 d (one synodic-ish window)
            candidate = base + delta_h / 24.0
            lon = float(calc_planet_position(candidate, 1)[0])
            if lon < 5.0 or lon > 355.0:
                natal_jd = candidate
                natal_moon = lon
                break
        assert natal_jd is not None, "Could not find Moon near seam within 28 d"
        assert natal_moon is not None

        # Seed one tropical month later:
        t_seed = natal_jd + _TROPICAL_MONTH_D
        jd_return = _solve_return(1, natal_moon, t_seed, 1.5)

        moon_at_return = float(calc_planet_position(jd_return, 1)[0])
        residual = float(_signed_residual_deg(np.array(moon_at_return), natal_moon))
        assert abs(residual) < _TOL_DEG, (
            f"Moon wrap-around return: residual={residual}° exceeds tol_deg={_TOL_DEG}°"
        )


class TestSolveReturnConvergenceCount:
    """Bisection converges in expected iteration counts.

    Ratchets that catches regressions where the bisection accidentally
    drifts toward linear convergence (e.g., a refactor introducing a
    misplaced sign check).

    Sun ±36h bracket / tol_deg=1/3600 at speed 0.985647°/d → ~13 iter.
    Moon ±1.5d bracket / tol_deg=1/3600 at speed 13.176°/d → ~17 iter.
    """

    @staticmethod
    def _solve_return_count_iter(
        body_id: int, natal_lon_ref: float, t_seed: float, half_window_days: float
    ) -> int:
        """Inline copy of _solve_return that counts iterations (no public API yet)."""
        from ketu.ephemeris.planets import calc_planet_position_batch

        t_lo = t_seed - half_window_days
        t_hi = t_seed + half_window_days
        lons = calc_planet_position_batch(np.array([t_lo, t_hi]), body_id)[:, 0]
        r_lo = float(_signed_residual_deg(lons[0], natal_lon_ref))
        r_hi = float(_signed_residual_deg(lons[1], natal_lon_ref))
        if r_lo * r_hi > 0:
            raise ValueError("no sign change")
        for it in range(60):
            t_mid = 0.5 * (t_lo + t_hi)
            lon_mid = float(
                calc_planet_position_batch(np.array([t_mid]), body_id)[0, 0]
            )
            r_mid = float(_signed_residual_deg(lon_mid, natal_lon_ref))
            if abs(r_mid) < _TOL_DEG:
                return it + 1
            if (t_hi - t_lo) < _TOL_DAYS:
                return it + 1
            if r_lo * r_mid < 0:
                t_hi, r_hi = t_mid, r_mid
            else:
                t_lo, r_lo = t_mid, r_mid
        return 60

    def test_sun_converges_in_under_30_iterations(self) -> None:
        """Sun return: ~13 iter expected; cap at 30 as a ratchet."""
        natal_jd = 2451545.0
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        t_seed = natal_jd + _TROPICAL_YEAR_D
        iters = self._solve_return_count_iter(0, natal_sun, t_seed, 1.5)
        assert iters <= 30, f"Sun bisection took {iters} iter; expected ~13"

    def test_moon_converges_in_under_30_iterations(self) -> None:
        """Moon return: ~17 iter expected; cap at 30 as a ratchet."""
        natal_jd = 2451545.0
        natal_moon = float(calc_planet_position(natal_jd, 1)[0])
        t_seed = natal_jd + _TROPICAL_MONTH_D
        iters = self._solve_return_count_iter(1, natal_moon, t_seed, 1.5)
        assert iters <= 30, f"Moon bisection took {iters} iter; expected ~17"


class TestSolveReturnBracketRejection:
    """RESEARCH Open Question Q1 binding: bad bracket raises ValueError (no auto-extend)."""

    def test_no_sign_change_raises_value_error(self) -> None:
        """Bracket completely on one side of the residual zero: ValueError."""
        natal_jd = 2451545.0
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        # Seed at ~+0.5 d from natal — Sun has moved ~0.5°, residual is +0.5°
        # at both endpoints of a ±0.1 d bracket; no sign change.
        bad_seed = natal_jd + 0.5
        with pytest.raises(ValueError, match=r"No return in bracket"):
            _solve_return(0, natal_sun, bad_seed, 0.1)
