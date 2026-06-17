"""RET-01..03 + RET-05 surface suite for ``solar_return``.

End-to-end tests of the public API. Wrap-around helper-level tests
live in ``tests/returns/test_solve_return.py`` (Plan 18-01); oracle
fixtures live in ``tests/returns/test_returns_oracle.py`` (Plan 18-04).
This file pins:

- Dtype contract (output is :data:`ketu.charts.CHART_DTYPE`).
- Resolved-JD Sun residual < 1 arc-second (RET-03 binding).
- Relocation contract (None defaults; non-None overrides) (RET-05).
- ``natal_lat/lon`` does NOT affect resolved JD (RET-05 ratchet).
- Polar relocation does NOT raise (hard-wired
  ``polar_fallback='porphyry'``).
- Feb 29 natal in non-leap target year resolves normally.
- ``system=`` pass-through.
- ``target_year`` type contract (int only).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import CHART_DTYPE
from ketu.ephemeris.planets import calc_planet_position
from ketu.returns import solar_return
from ketu.returns._solve import _TOL_DEG, _signed_residual_deg


class TestSolarReturnDtype:
    """RET-01 dtype binding."""

    def test_returns_chart_dtype(self, natal_diana: dict[str, float]) -> None:
        """Output is a scalar CHART_DTYPE (0-d ndarray).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990
        )
        assert chart.dtype == CHART_DTYPE
        assert chart.shape == ()  # scalar


class TestSolarReturnResidual:
    """RET-03: resolved-JD Sun longitude is within 1 arc-second of natal."""

    @pytest.mark.parametrize("target_year", [1980, 1990, 2000, 2010])
    def test_residual_under_one_arcsecond(
        self, natal_diana: dict[str, float], target_year: int
    ) -> None:
        """Multiple target years: resolved Sun is within 1 arc-second of natal.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        target_year : int
            Target year for the solar return (parametrized).
        """
        natal_sun = float(calc_planet_position(natal_diana["jd"], 0)[0])
        chart = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], target_year
        )
        jd_return = float(chart["jd"])
        sun_at_return = float(calc_planet_position(jd_return, 0)[0])
        residual = abs(float(_signed_residual_deg(np.array(sun_at_return), natal_sun)))
        assert residual < _TOL_DEG, (
            f"target_year={target_year}: residual={residual} deg exceeds {_TOL_DEG} deg"
        )


class TestSolarReturnRelocation:
    """RET-05: relocation contract."""

    def test_return_lat_lon_none_defaults_to_natal(
        self, natal_diana: dict[str, float]
    ) -> None:
        """``return_lat=None``/``return_lon=None`` reuses natal location.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart_default = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990
        )
        chart_explicit = solar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            1990,
            return_lat=natal_diana["lat"],
            return_lon=natal_diana["lon"],
        )
        # Identical outputs (same JD, same houses):
        assert float(chart_default["jd"]) == float(chart_explicit["jd"])
        assert float(chart_default["lat"]) == float(chart_explicit["lat"])
        assert float(chart_default["lon"]) == float(chart_explicit["lon"])
        np.testing.assert_array_almost_equal(
            chart_default["cusps"], chart_explicit["cusps"]
        )

    def test_relocation_changes_houses_not_bodies(
        self, natal_diana: dict[str, float]
    ) -> None:
        """Non-None ``return_lat/lon``: bodies identical (geocentric), houses differ.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart_natal = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990
        )
        chart_reloc = solar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            1990,
            return_lat=40.7128,  # NYC
            return_lon=-74.0060,
        )
        # Same JD (the resolution is location-independent):
        assert float(chart_natal["jd"]) == float(chart_reloc["jd"])
        # Bodies are geocentric → identical:
        np.testing.assert_array_almost_equal(
            chart_natal["body_lons"], chart_reloc["body_lons"]
        )
        # Houses differ because lat/lon differ:
        assert not np.allclose(chart_natal["cusps"], chart_reloc["cusps"])
        assert float(chart_natal["asc"]) != float(chart_reloc["asc"])


class TestSolarReturnNatalLocationIrrelevance:
    """RET-05 ratchet: ``natal_lat/lon`` does NOT affect resolved JD.

    Sun's geocentric longitude is location-independent. Two
    ``solar_return`` calls with identical ``natal_jd`` + ``target_year``
    but different ``natal_lat/lon`` MUST produce the same resolved JD.
    """

    def test_natal_lat_does_not_affect_jd(self, natal_diana: dict[str, float]) -> None:
        """Same natal_jd + target_year + different natal_lat → identical JD.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon; only ``jd`` is used).
        """
        chart_a = solar_return(natal_diana["jd"], 0.0, 0.0, 1990)
        chart_b = solar_return(natal_diana["jd"], 89.0, 0.0, 1990)
        # JD must be identical (Sun longitude is geocentric):
        assert abs(float(chart_a["jd"]) - float(chart_b["jd"])) < 1e-7, (
            f"natal_lat affected resolved JD: "
            f"chart_a.jd={float(chart_a['jd'])}, chart_b.jd={float(chart_b['jd'])}"
        )


class TestSolarReturnPolarRelocation:
    """Polar relocation does not raise (hard-wired ``polar_fallback='porphyry'``)."""

    def test_tromso_relocation_does_not_raise(
        self, natal_diana: dict[str, float]
    ) -> None:
        """Relocate to Tromso (lat=69.65 deg, above Arctic Circle for Placidus).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        # Must NOT raise HighLatitudeError:
        chart = solar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            1990,
            return_lat=69.65,
            return_lon=18.96,
            system="placidus",
        )
        assert chart.dtype == CHART_DTYPE
        # Cusps populated (Porphyry fallback engaged):
        assert not np.any(np.isnan(chart["cusps"]))


class TestSolarReturnFeb29Natal:
    """Feb 29 natal in non-leap target year resolves normally.

    The seed is a tropical-year offset (NOT calendar-anchored), so the
    return falls in late Feb / early March of the target year.
    """

    def test_feb_29_natal_non_leap_target(self) -> None:
        """1980-02-29T12:00 UT natal; target_year=2001 (non-leap)."""
        # 1980-02-29T12:00 UT JD ≈ 2444299.0
        natal_jd = 2444299.0
        natal_sun = float(calc_planet_position(natal_jd, 0)[0])
        chart = solar_return(natal_jd, 0.0, 0.0, 2001)
        sun_at_return = float(calc_planet_position(float(chart["jd"]), 0)[0])
        residual = abs(float(_signed_residual_deg(np.array(sun_at_return), natal_sun)))
        assert residual < _TOL_DEG, (
            f"Feb 29 natal / non-leap target: residual={residual} deg exceeds {_TOL_DEG} deg"
        )


class TestSolarReturnSystemKwarg:
    """``system=`` pass-through; unknown raises ValueError."""

    def test_default_placidus(self, natal_diana: dict[str, float]) -> None:
        """Default ``system='placidus'`` is stored in the output dtype.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990
        )
        assert str(chart["system"]) == "placidus"

    def test_whole_sign_pass_through(self, natal_diana: dict[str, float]) -> None:
        """``system='whole_sign'`` is stored verbatim in the output dtype.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart = solar_return(
            natal_diana["jd"],
            natal_diana["lat"],
            natal_diana["lon"],
            1990,
            system="whole_sign",
        )
        assert str(chart["system"]) == "whole_sign"

    def test_unknown_system_raises(self, natal_diana: dict[str, float]) -> None:
        """Unknown ``system=`` raises ValueError via ``calculate_houses``.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        with pytest.raises(ValueError):
            solar_return(
                natal_diana["jd"],
                natal_diana["lat"],
                natal_diana["lon"],
                1990,
                system="bogus_system",
            )


# ---------------------------------------------------------------------------
# DSPD-03: returns inherit body_decl_speed for free via compute_chart
# ---------------------------------------------------------------------------


class TestSolarReturnBodyDeclSpeedInherited:
    """DSPD-03: solar_return chart carries finite non-zero body_decl_speed.

    body_decl_speed is populated by compute_chart, which solar_return calls
    internally. No extra wiring is needed — the field is inherited for free.
    This test pins the inheritance contract so that any future refactor that
    accidentally bypasses compute_chart is caught.
    """

    def test_body_decl_speed_finite_and_non_zero(
        self, natal_diana: dict[str, float]
    ) -> None:
        """solar_return body_decl_speed is finite and not all-zero (DSPD-03).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990
        )
        speeds = np.asarray(chart["body_decl_speed"], dtype=np.float64)
        assert np.all(np.isfinite(speeds)), (
            f"solar_return body_decl_speed has non-finite values: {speeds}"
        )
        assert not np.all(speeds == 0.0), (
            "solar_return body_decl_speed is all-zero — inheritance broken (DSPD-03)"
        )


class TestSolarReturnTargetYearTypeGuard:
    """``target_year`` MUST be int; float raises ValueError."""

    def test_float_target_year_raises(self, natal_diana: dict[str, float]) -> None:
        """Float ``target_year`` raises ValueError with a helpful message.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        with pytest.raises(ValueError, match=r"target_year must be an integer"):
            solar_return(
                natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], 1990.5
            )

    def test_string_target_year_raises(self, natal_diana: dict[str, float]) -> None:
        """String ``target_year`` raises ValueError with a helpful message.

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        with pytest.raises(ValueError, match=r"target_year must be an integer"):
            solar_return(
                natal_diana["jd"],
                natal_diana["lat"],
                natal_diana["lon"],
                "1990",  # type: ignore[arg-type]
            )

    def test_numpy_int_accepted(self, natal_diana: dict[str, float]) -> None:
        """``np.int64(1990)`` is acceptable (passes ``np.integer`` isinstance).

        Parameters
        ----------
        natal_diana : dict[str, float]
            Session-scoped natal fixture (jd/lat/lon).
        """
        chart = solar_return(
            natal_diana["jd"], natal_diana["lat"], natal_diana["lon"], np.int64(1990)
        )
        assert chart.dtype == CHART_DTYPE
