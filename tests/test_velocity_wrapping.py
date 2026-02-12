"""Regression tests for Moon velocity wrapping at 360/0 boundary.

BUG: When Moon longitude crosses 360->0, finite difference returns
-36000 deg/day instead of +14 deg/day.

Verified date: 2024-01-16 05:00 UTC (Moon at 359.87 deg).
"""
import numpy as np
import pytest
from datetime import datetime, timezone
from ketu.calculations import long_velocity, utc_to_julian
from ketu.ephemeris.planets import calc_planet_position, calc_planet_position_batch

# Moon body ID
MOON = 1


class TestMoonVelocityWrapping:
    """Regression tests for BUG-03: Moon velocity wrapping."""

    def test_scalar_moon_velocity_at_boundary(self):
        """Scalar calc_planet_position returns sane Moon velocity at 360/0 crossing."""
        # 2024-01-16 05:00 UTC - Moon near 360 deg boundary
        dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)

        result = calc_planet_position(jd, MOON)
        lon_speed = result[3]  # index 3 = lon_speed

        # Moon velocity is ~11-15 deg/day (prograde), never -36000
        assert 10 <= abs(lon_speed) <= 16, (
            f"Moon velocity at 360 deg crossing: {lon_speed} deg/day. "
            f"Expected ~14 deg/day. Wrapping bug if large negative."
        )
        assert lon_speed > 0, (
            f"Moon velocity should be positive (prograde): got {lon_speed}"
        )

    def test_vectorized_moon_velocity_at_boundary(self):
        """Vectorized calc_planet_position_batch returns sane Moon velocity at 360/0 crossing."""
        dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)

        jd_array = np.array([jd])
        results = calc_planet_position_batch(jd_array, MOON)
        lon_speed = results[0, 3]  # first row, index 3 = lon_speed

        assert 10 <= abs(lon_speed) <= 16, (
            f"Vectorized Moon velocity at 360 deg crossing: {lon_speed} deg/day. "
            f"Expected ~14 deg/day. Wrapping bug if large negative."
        )
        assert lon_speed > 0, (
            f"Vectorized Moon velocity should be positive (prograde): got {lon_speed}"
        )

    def test_scalar_and_vectorized_agree(self):
        """Scalar and vectorized Moon velocity must agree at boundary."""
        dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)

        scalar_result = calc_planet_position(jd, MOON)
        batch_result = calc_planet_position_batch(np.array([jd]), MOON)

        np.testing.assert_allclose(
            scalar_result[3], batch_result[0, 3],
            atol=1e-6,
            err_msg="Scalar and vectorized Moon velocity must agree at 360/0 boundary"
        )

    def test_long_velocity_api_at_boundary(self):
        """High-level long_velocity() API returns correct Moon velocity at boundary."""
        dt = datetime(2024, 1, 16, 5, 0, 0, tzinfo=timezone.utc)
        jd = utc_to_julian(dt)

        moon_vel = long_velocity(jd, MOON)

        assert 10 <= moon_vel <= 16, (
            f"long_velocity(Moon) at 360 deg crossing: {moon_vel} deg/day. "
            f"Expected ~14 deg/day."
        )
