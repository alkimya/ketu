"""Tests for chart-level helpers in :mod:`ketu.charts.api`.

DSPD-06: ``is_ascending_declination_chart(chart) -> np.ndarray``
    - dtype is int8
    - scalar chart () -> shape (14,); vectorised (N,) -> shape (N, 14)
    - output is consistent with the v1.5 scalar ``is_ascending_declination``
    - neutral (0) when |body_decl_speed| <= DECL_STANDSTILL_EPS
    - all three int8 branches exercised for 100% branch coverage
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.calculations import DECL_STANDSTILL_EPS, declination_velocity
from ketu.charts import CHART_DTYPE, compute_chart


# ---------------------------------------------------------------------------
# Import gate
# ---------------------------------------------------------------------------


def test_is_ascending_declination_chart_importable() -> None:
    """``from ketu.charts import is_ascending_declination_chart`` must succeed."""
    from ketu.charts import is_ascending_declination_chart  # noqa: F401


# ---------------------------------------------------------------------------
# DSPD-06: dtype and shape contract
# ---------------------------------------------------------------------------


class TestIsAscendingDeclChartDtypeAndShape:
    """DSPD-06: int8 dtype + shape S+(14,) for scalar and vectorised charts."""

    # Known JD (2025-01-15T12:00Z)
    _JD = 2460690.0
    _LAT = 48.8566
    _LON = 2.3522

    def test_dtype_is_int8(self) -> None:
        """Output dtype must be int8 (D-03 classification contract).

        Parameters
        ----------
        None
        """
        from ketu.charts import is_ascending_declination_chart

        chart = compute_chart(self._JD, self._LAT, self._LON)
        result = is_ascending_declination_chart(chart)
        assert result.dtype == np.int8, (
            f"Expected dtype int8; got {result.dtype}"
        )

    def test_scalar_chart_gives_shape_14(self) -> None:
        """Scalar (0-d) chart input → output shape (14,).

        Parameters
        ----------
        None
        """
        from ketu.charts import is_ascending_declination_chart

        chart = compute_chart(self._JD, self._LAT, self._LON)
        assert chart.shape == (), "fixture must be scalar (0-d)"
        result = is_ascending_declination_chart(chart)
        assert result.shape == (14,), (
            f"Expected shape (14,) for scalar chart; got {result.shape}"
        )

    def test_vectorised_chart_gives_shape_n_14(self) -> None:
        """Vectorised (N,) chart input → output shape (N, 14).

        Parameters
        ----------
        None
        """
        from ketu.charts import is_ascending_declination_chart

        n = 5
        jd_arr = np.linspace(self._JD, self._JD + 10, n)
        lat_arr = np.full(n, self._LAT)
        lon_arr = np.full(n, self._LON)
        chart = compute_chart(jd_arr, lat_arr, lon_arr)
        assert chart.shape == (n,), "fixture must be vectorised (N,)"
        result = is_ascending_declination_chart(chart)
        assert result.shape == (n, 14), (
            f"Expected shape ({n}, 14) for vectorised chart; got {result.shape}"
        )


# ---------------------------------------------------------------------------
# DSPD-06: consistency with v1.5 scalar is_ascending_declination
# ---------------------------------------------------------------------------


class TestIsAscendingDeclChartConsistency:
    """DSPD-06: chart helper is consistent with the v1.5 scalar.

    For a body moving faster than DECL_STANDSTILL_EPS:
    - is_ascending_declination_chart(chart)[body] == +1 iff is_ascending_declination(jd, body)
    - is_ascending_declination_chart(chart)[body] == -1 iff not is_ascending_declination(jd, body)
    """

    # Known JD (2025-01-15T12:00Z): Moon is fast-moving at this date.
    _JD = 2460690.0
    _LAT = 48.8566
    _LON = 2.3522
    _MOON = 1  # body_id

    def test_ascending_body_gives_plus1(self) -> None:
        """A body ascending faster than EPS gives +1 in chart helper.

        Parameters
        ----------
        None
        """
        from ketu.calculations import is_ascending_declination
        from ketu.charts import is_ascending_declination_chart

        # Find a JD where Moon decl speed > EPS (ascending).
        # Scan a short window to find a clearly ascending Moon.
        for delta in range(0, 30):
            jd = self._JD + delta
            speed = declination_velocity(jd, self._MOON)
            if speed > DECL_STANDSTILL_EPS:
                chart = compute_chart(jd, self._LAT, self._LON)
                result = is_ascending_declination_chart(chart)
                scalar = is_ascending_declination(jd, self._MOON)
                assert scalar is True, f"scalar should be True at jd={jd}"
                assert result[self._MOON] == np.int8(1), (
                    f"Expected +1 for ascending Moon at jd={jd}; "
                    f"got {result[self._MOON]}"
                )
                return
        pytest.skip("No ascending Moon found in 30-day window — unlikely")  # pragma: no cover

    def test_descending_body_gives_minus1(self) -> None:
        """A body descending faster than EPS gives -1 in chart helper.

        Parameters
        ----------
        None
        """
        from ketu.calculations import is_ascending_declination
        from ketu.charts import is_ascending_declination_chart

        # Find a JD where Moon decl speed < -EPS (descending).
        for delta in range(0, 30):
            jd = self._JD + delta
            speed = declination_velocity(jd, self._MOON)
            if speed < -DECL_STANDSTILL_EPS:
                chart = compute_chart(jd, self._LAT, self._LON)
                result = is_ascending_declination_chart(chart)
                scalar = is_ascending_declination(jd, self._MOON)
                assert scalar is False, f"scalar should be False at jd={jd}"
                assert result[self._MOON] == np.int8(-1), (
                    f"Expected -1 for descending Moon at jd={jd}; "
                    f"got {result[self._MOON]}"
                )
                return
        pytest.skip("No descending Moon found in 30-day window — unlikely")  # pragma: no cover


# ---------------------------------------------------------------------------
# DSPD-06: neutral / standstill branch (all three int8 branches for 100% cov)
# ---------------------------------------------------------------------------


class TestIsAscendingDeclChartNeutral:
    """DSPD-06: neutral branch (|speed| <= EPS) classifies as 0.

    This test exercises the third int8 branch explicitly by injecting a
    synthetic CHART_DTYPE array with body_decl_speed set to a value inside
    the standstill band (EPS * 0.5), ensuring the ``np.where`` else-branch
    is covered for 100% branch coverage.
    """

    def test_speed_below_eps_gives_zero(self) -> None:
        """body_decl_speed = EPS * 0.5 → classification 0 (neutral).

        Parameters
        ----------
        None
        """
        from ketu.charts import is_ascending_declination_chart

        # Build a synthetic scalar CHART_DTYPE with all body_decl_speed set
        # to a value in the standstill band.
        synthetic = np.zeros((), dtype=CHART_DTYPE)
        standstill_speed = DECL_STANDSTILL_EPS * 0.5  # within neutral band
        synthetic["body_decl_speed"] = standstill_speed

        result = is_ascending_declination_chart(synthetic)
        assert result.dtype == np.int8
        assert np.all(result == np.int8(0)), (
            f"Expected all-zero for standstill speed {standstill_speed}; "
            f"got {result}"
        )

    def test_all_three_branches_explicit(self) -> None:
        """All three int8 branches (+1 / -1 / 0) are exercised in one call.

        Parameters
        ----------
        None
        """
        from ketu.charts import is_ascending_declination_chart

        # Build a synthetic (3,) CHART_DTYPE: ascending, descending, neutral.
        batch = np.zeros((3,), dtype=CHART_DTYPE)
        ascending_speed = DECL_STANDSTILL_EPS * 10.0   # > EPS → +1
        descending_speed = -DECL_STANDSTILL_EPS * 10.0  # < -EPS → -1
        neutral_speed = DECL_STANDSTILL_EPS * 0.5       # within band → 0
        batch[0]["body_decl_speed"] = ascending_speed
        batch[1]["body_decl_speed"] = descending_speed
        batch[2]["body_decl_speed"] = neutral_speed

        result = is_ascending_declination_chart(batch)
        assert result.shape == (3, 14)
        assert result.dtype == np.int8

        # All bodies in row 0 are ascending (speed > EPS for all 14).
        assert np.all(result[0] == np.int8(1)), f"row 0 should be +1: {result[0]}"
        # All bodies in row 1 are descending.
        assert np.all(result[1] == np.int8(-1)), f"row 1 should be -1: {result[1]}"
        # All bodies in row 2 are neutral.
        assert np.all(result[2] == np.int8(0)), f"row 2 should be 0: {result[2]}"
