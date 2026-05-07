"""``house_of`` tests — assigns planet longitude to 1-indexed house (HOU-07).

Covers scalar input, vectorisation over ``planet_lon``, vectorisation
over ``cusps``, exact-cusp boundary semantics, 360° wrap, and modular
input normalisation.

HOU-09 coverage gate command (separate from this file's tests):

    pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.houses import calculate_houses, house_of


@pytest.fixture
def paris_j2000_cusps() -> np.ndarray:
    """Placidus cusps for J2000.0 at Paris (48.86°N, 2.35°E)."""
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
    return np.asarray(r["cusps"])


def test_house_of_returns_int_in_range_1_to_12(paris_j2000_cusps: np.ndarray) -> None:
    """Every 30°-step longitude maps to a valid 1..12 house number."""
    for lon in [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0,
                210.0, 240.0, 270.0, 300.0, 330.0]:
        h = int(house_of(lon, paris_j2000_cusps))
        assert 1 <= h <= 12, f"longitude {lon}° → house {h}; out of range"


def test_house_of_planet_at_cusp_is_in_that_house(paris_j2000_cusps: np.ndarray) -> None:
    """A planet at exactly the i-th cusp lives in house i+1 (not i).

    Convention: ``cusps[i]`` BEGINS house ``i+1`` (eastward direction).
    So a planet at ``cusps[0]`` is in house 1; at ``cusps[5]`` is in
    house 6.
    """
    for i in range(12):
        cusp_value = float(paris_j2000_cusps[i])
        h = int(house_of(cusp_value, paris_j2000_cusps))
        assert h == i + 1, (
            f"planet at cusps[{i}]={cusp_value}° expected house {i+1}, got {h}"
        )


def test_house_of_vectorized_over_planet_lons(paris_j2000_cusps: np.ndarray) -> None:
    """house_of broadcasts an (N,) ``planet_lon`` array against (12,) cusps."""
    lons = np.array([0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0])
    houses = house_of(lons, paris_j2000_cusps)
    assert houses.shape == (8,)
    assert houses.dtype == np.int32
    assert all(1 <= int(h) <= 12 for h in houses)


def test_house_of_vectorized_over_cusps_arrays() -> None:
    """When cusps has shape ``(N, 12)``, house_of broadcasts to ``(N,)``."""
    # Two charts: Paris J2000 and 2050 Reykjavik.
    r = calculate_houses(
        np.array([2451545.0, 2470204.0]),
        np.array([48.8566, 64.1466]),
        np.array([2.3522, -21.9426]),
        system="placidus",
    )
    cusps_2 = np.asarray(r["cusps"])  # shape (2, 12)
    # Same planet longitude (45°) against both charts simultaneously
    # via broadcast: planet_lon shape (2,) matches cusps leading shape.
    planet_lons = np.array([45.0, 45.0])
    houses = house_of(planet_lons, cusps_2)
    assert houses.shape == (2,)
    for h in houses:
        assert 1 <= int(h) <= 12


def test_house_of_handles_360_wrap() -> None:
    """0.01° vs 359.99° land in same or adjacent houses (mod-12 wrap).

    Depending on which side of cusp 1 (the ASC) the 0° meridian falls,
    they may share a house or be in cusp-1 and cusp-12. They cannot be
    farther than that.
    """
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
    h_low = int(house_of(0.01, r["cusps"]))
    h_high = int(house_of(359.99, r["cusps"]))
    # Either same house, or adjacent in mod-12 sense: |Δ| ∈ {0, 1, 11}.
    delta = abs(h_low - h_high)
    assert delta in (0, 1, 11), (
        f"0.01° → {h_low}, 359.99° → {h_high}; expected same or adjacent"
    )


def test_house_of_modular_input_normalization() -> None:
    """planet_lon is normalised mod 360 internally (no caller pre-clamp)."""
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
    h_45 = int(house_of(45.0, r["cusps"]))
    h_405 = int(house_of(405.0, r["cusps"]))     # 405 % 360 = 45
    h_neg = int(house_of(-315.0, r["cusps"]))    # -315 % 360 = 45
    assert h_45 == h_405 == h_neg


def test_house_of_returns_int32_dtype(paris_j2000_cusps: np.ndarray) -> None:
    """Result dtype contract: int32 (consistent ML-friendly interop type)."""
    h_scalar = house_of(45.0, paris_j2000_cusps)
    assert h_scalar.dtype == np.int32

    h_vec = house_of(np.array([0.0, 90.0, 180.0]), paris_j2000_cusps)
    assert h_vec.dtype == np.int32
