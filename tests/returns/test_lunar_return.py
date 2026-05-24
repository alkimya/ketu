"""LRET-01..03 + LRET-05 surface suite for ``lunar_return``.

End-to-end tests of the public API. Wrap-around helper-level tests
live in tests/returns/test_solve_return.py (Plan 18-01); oracle
fixtures live in tests/returns/test_returns_oracle.py (Plan 18-04).
This file pins:

- Dtype contract.
- Resolved-JD Moon residual < 1 arc-second (LRET-03).
- FIRST-return->= target_jd contract (LRET-01) -- parametrised over
  multiple ``target_jd`` offsets from a known return; ratchet that
  no resolved JD is < ``target_jd``.
- Day-after-target_jd case (LRET-04 contract; full Astro.com oracle
  in Plan 18-04).
- Relocation contract (LRET-05).
- ``natal_lat/lon`` irrelevance (LRET-05 ratchet).
- Polar relocation does NOT raise.
- ``system=`` pass-through.
- ``target_jd`` type contract (float; not str).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import CHART_DTYPE
from ketu.ephemeris.planets import calc_planet_position
from ketu.returns import lunar_return
from ketu.returns._solve import (
    _TOL_DAYS,
    _TOL_DEG,
    _TROPICAL_MONTH_D,
    _signed_residual_deg,
)


class TestLunarReturnDtype:
    """LRET-01 dtype binding."""

    def test_returns_chart_dtype(self, natal_diana: dict[str, float]) -> None:
        """Output is a scalar CHART_DTYPE (0-d ndarray).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            target_jd=2451545.0,  # 2000-01-01T12:00 UT
        )
        assert chart.dtype == CHART_DTYPE
        assert chart.shape == ()


class TestLunarReturnResidual:
    """LRET-03: resolved-JD Moon longitude is within 1 arc-second of natal."""

    @pytest.mark.parametrize(
        "target_jd",
        [
            2440000.0,  # 1968-05-23
            2450000.0,  # 1995-10-09
            2455000.0,  # 2009-06-19
            2460000.0,  # 2023-02-25
        ],
    )
    def test_residual_under_one_arcsecond(
        self, natal_diana: dict[str, float], target_jd: float
    ) -> None:
        """Multiple target JDs: resolved Moon is within 1 arcsec of natal.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        target_jd : float
            Parametrised earliest-acceptable return JD.
        """
        natal_moon = float(calc_planet_position(natal_diana["jd"], 1)[0])
        chart = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], target_jd
        )
        jd_return = float(chart["jd"])
        moon_at_return = float(calc_planet_position(jd_return, 1)[0])
        residual = abs(float(_signed_residual_deg(np.asarray(moon_at_return), natal_moon)))
        assert residual < _TOL_DEG, (
            f"target_jd={target_jd}: residual={residual} deg exceeds {_TOL_DEG} deg"
        )


class TestLunarReturnFirstReturnContract:
    """LRET-01 binding: resolved JD is the FIRST return >= ``target_jd``."""

    @pytest.mark.parametrize(
        "target_jd",
        [2440000.0, 2450000.0, 2455000.0, 2460000.0],
    )
    def test_resolved_jd_is_at_or_after_target(
        self, natal_diana: dict[str, float], target_jd: float
    ) -> None:
        """``jd_return >= target_jd - tol_days``.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        target_jd : float
            Parametrised earliest-acceptable return JD.
        """
        chart = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], target_jd
        )
        jd_return = float(chart["jd"])
        assert jd_return >= target_jd - _TOL_DAYS, (
            f"target_jd={target_jd}: jd_return={jd_return} < target_jd "
            f"(violates LRET-01)"
        )

    @pytest.mark.parametrize(
        "target_jd",
        [2440000.0, 2450000.0, 2455000.0, 2460000.0],
    )
    def test_resolved_jd_is_within_one_period_of_target(
        self, natal_diana: dict[str, float], target_jd: float
    ) -> None:
        """Resolved JD is within one tropical month of target_jd.

        Pins the FIRST return contract -- if resolution accidentally
        jumped to the SECOND return, this test catches it.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        target_jd : float
            Parametrised earliest-acceptable return JD.
        """
        chart = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], target_jd
        )
        jd_return = float(chart["jd"])
        time_since_target = jd_return - target_jd
        assert time_since_target < _TROPICAL_MONTH_D + 0.1, (
            f"target_jd={target_jd}: jd_return is {time_since_target:.3f} d "
            f"past target -- this is the SECOND return, not the first "
            f"(violates LRET-01)"
        )


class TestLunarReturnDayAfterTarget:
    """LRET-04 pre-oracle ratchet: target_jd ~1h before return.

    Strategy: pick a natal Moon longitude, find a known return,
    then re-target 1h before it. The resolved JD should land ~1h
    later, on the same return (which may fall on the next calendar
    day). Full Astro.com cross-check in Plan 18-04 oracle fixtures;
    this is the architectural pin.
    """

    def test_target_one_hour_before_return_resolves_on_next_day(
        self, natal_diana: dict[str, float]
    ) -> None:
        """target_jd = (known return JD) - 1h => resolved JD is ~1h past target.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        # First, find a known return JD by calling lunar_return with a
        # target ~14 d before:
        first_pass = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            target_jd=2450000.0,
        )
        known_return_jd = float(first_pass["jd"])

        # Now set target_jd = known_return_jd - 1/24 (one hour before):
        target_one_hour_before = known_return_jd - 1.0 / 24.0
        second_pass = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            target_jd=target_one_hour_before,
        )
        resolved = float(second_pass["jd"])

        # The resolved JD must be >= target (LRET-01) AND ~= known_return_jd
        # (the SAME return). Tolerance is the bisection's residual-driven
        # floor for Moon (~66 ms = 7.6e-7 d) times a generous 100x safety
        # margin = ~7.6e-5 d (~6.5 s) -- well below the "different return"
        # threshold of ~27 d.
        assert resolved >= target_one_hour_before - _TOL_DAYS
        assert abs(resolved - known_return_jd) < 1e-4, (
            f"resolved JD shifted unexpectedly: {resolved} vs known "
            f"{known_return_jd}"
        )
        # And it should be ~1h after target_jd:
        time_past_target_hours = (resolved - target_one_hour_before) * 24.0
        assert 0.5 < time_past_target_hours < 1.5, (
            f"time_past_target = {time_past_target_hours} h; expected ~1h"
        )


class TestLunarReturnRelocation:
    """LRET-05: relocation contract."""

    def test_return_lat_lon_none_defaults_to_natal(
        self, natal_diana: dict[str, float]
    ) -> None:
        """``return_lat/lon=None`` reuses ``natal_lat/lon``.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart_default = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 2451545.0
        )
        chart_explicit = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            2451545.0,
            return_lat=natal_diana["lat"],
            return_lon=natal_diana["lon"],
        )
        assert float(chart_default["jd"]) == float(chart_explicit["jd"])
        assert float(chart_default["lat"]) == float(chart_explicit["lat"])
        assert float(chart_default["lon"]) == float(chart_explicit["lon"])

    def test_relocation_changes_houses_not_bodies(
        self, natal_diana: dict[str, float]
    ) -> None:
        """Relocation: same JD + same body_lons, different cusps.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart_natal = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 2451545.0
        )
        chart_reloc = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            2451545.0,
            return_lat=40.7128,
            return_lon=-74.0060,
        )
        assert float(chart_natal["jd"]) == float(chart_reloc["jd"])
        np.testing.assert_array_almost_equal(
            chart_natal["body_lons"], chart_reloc["body_lons"]
        )
        assert not np.allclose(chart_natal["cusps"], chart_reloc["cusps"])


class TestLunarReturnNatalLocationIrrelevance:
    """LRET-05 ratchet: ``natal_lat/lon`` does NOT affect resolved JD."""

    def test_natal_lat_does_not_affect_jd(self, natal_diana: dict[str, float]) -> None:
        """Different natal_lat values -> identical resolved JD.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart_a = lunar_return(natal_diana["jd"], 0.0, 0.0, 2451545.0)
        chart_b = lunar_return(natal_diana["jd"], 89.0, 0.0, 2451545.0)
        assert abs(float(chart_a["jd"]) - float(chart_b["jd"])) < 1e-7


class TestLunarReturnPolarRelocation:
    """Polar relocation does not raise (hard-wired ``polar_fallback='porphyry'``)."""

    def test_tromso_relocation_does_not_raise(
        self, natal_diana: dict[str, float]
    ) -> None:
        """Polar return_lat does not raise; cusps non-NaN.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            2451545.0,
            return_lat=69.65,
            return_lon=18.96,
            system="placidus",
        )
        assert chart.dtype == CHART_DTYPE
        assert not np.any(np.isnan(chart["cusps"]))


class TestLunarReturnSystemKwarg:
    """``system=`` pass-through; unknown raises ValueError."""

    def test_default_placidus(self, natal_diana: dict[str, float]) -> None:
        """Default ``system='placidus'`` stored in chart.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart = lunar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 2451545.0
        )
        assert str(chart["system"]) == "placidus"

    def test_whole_sign_pass_through(self, natal_diana: dict[str, float]) -> None:
        """``system='whole_sign'`` passed through to compute_chart.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            2451545.0,
            system="whole_sign",
        )
        assert str(chart["system"]) == "whole_sign"

    def test_unknown_system_raises(self, natal_diana: dict[str, float]) -> None:
        """Unknown ``system`` propagates ValueError from calculate_houses.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        with pytest.raises(ValueError):
            lunar_return(
                natal_diana["jd"],
                natal_diana["lat"],
                natal_diana["lon"],
                2451545.0,
                system="bogus_system",
            )


class TestLunarReturnTargetJdTypeGuard:
    """``target_jd`` must be float-like (int accepted; str rejected)."""

    def test_string_target_jd_raises(self, natal_diana: dict[str, float]) -> None:
        """String ``target_jd`` raises ValueError with helpful message.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        with pytest.raises(ValueError, match=r"target_jd must be a float"):
            lunar_return(
                natal_diana["jd"],
                natal_diana["lat"],
                natal_diana["lon"],
                target_jd="2010-01-01",  # type: ignore[arg-type]
            )

    def test_int_target_jd_accepted(self, natal_diana: dict[str, float]) -> None:
        """``int`` Julian Date is accepted (promoted via ``float()``).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Princess Diana natal triple (session-scoped fixture).
        """
        chart = lunar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            target_jd=2451545,  # int, not float
        )
        assert chart.dtype == CHART_DTYPE
