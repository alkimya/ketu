"""Behavioural tests for :func:`ketu.charts.is_day_chart`.

Pins the v1.2 sect helper contract (Plan 14-04):

- Return type: ``np.ndarray`` of ``bool``, broadcast over ``(jd, lat, lon)``.
- Sect convention (D-13): sunrise-inclusive — Sun in houses 7..12 = day,
  Sun in houses 1..6 = night. The strict ``Sun == ASC`` equality has
  measure zero on real data; convention is pinned by synthetic +/-0.01 deg
  deltas around the ASC.
- Geometric definition (D-14): ``house_of(sun_lon, cusps) >= 7``.
- Polar safety (D-15): never raises :class:`HighLatitudeError` thanks to
  the internal ``polar_fallback="porphyry"`` always-on substitution.
- Vectorisation: scalar (0-d), 1-d, 2-d, mixed broadcast (D-09).
- Cross-API consistency with :data:`CHART_DTYPE` produced by
  :func:`compute_chart` for non-polar latitudes.
"""
from __future__ import annotations

import sys

import numpy as np
import pytest

from ketu.charts import compute_chart, is_day_chart
from ketu.houses import calculate_houses, house_of


# ---------------------------------------------------------------------------
# 1. Return type contract
# ---------------------------------------------------------------------------

def test_is_day_chart_returns_bool_array() -> None:
    """Scalar input returns a 0-d ``np.bool_`` ndarray (not a Python bool)."""
    result = is_day_chart(2451545.0, 48.86, 2.35)
    assert isinstance(result, np.ndarray), (
        f"is_day_chart must return np.ndarray, got {type(result)!r}"
    )
    assert result.dtype == np.bool_, (
        f"is_day_chart dtype drifted: {result.dtype!r}"
    )
    assert result.shape == (), (
        f"scalar input must yield 0-d output; got shape {result.shape!r}"
    )


# ---------------------------------------------------------------------------
# 2. Hand-validated scalar cases — Paris J2000 noon / midnight
# ---------------------------------------------------------------------------

def test_is_day_chart_paris_j2000_noon_is_day() -> None:
    """J2000 (2000-01-01 12:00 UT) at Paris: Sun near MC -> day chart."""
    # 48.8566 N, 2.3522 E, JD 2451545.0 = J2000 epoch (noon UT).
    assert bool(is_day_chart(2451545.0, 48.8566, 2.3522)), (
        "J2000 Paris noon UT must be a day chart (Sun near MC)"
    )


def test_is_day_chart_paris_j2000_midnight_is_night() -> None:
    """J2000 minus 12h at Paris: Sun near IC -> night chart."""
    jd_midnight = 2451545.0 - 0.5  # 2000-01-01 00:00 UT
    assert not bool(is_day_chart(jd_midnight, 48.8566, 2.3522)), (
        "J2000 Paris midnight UT must be a night chart (Sun near IC)"
    )


# ---------------------------------------------------------------------------
# 3. Vectorisation: 1-d, broadcast, 2-d
# ---------------------------------------------------------------------------

def test_is_day_chart_vectorised_over_jd() -> None:
    """1-d jd array preserves leading shape and dtype."""
    # midnight, noon, next-midnight at Paris.
    jd_arr = np.array([2451544.5, 2451545.0, 2451545.5])
    result = is_day_chart(jd_arr, 48.8566, 2.3522)
    assert result.shape == (3,), f"1-d shape drifted: {result.shape}"
    assert result.dtype == np.bool_, f"dtype drifted: {result.dtype!r}"
    # midnight = night, noon = day, next-midnight = night.
    assert not bool(result[0])
    assert bool(result[1])
    assert not bool(result[2])


def test_is_day_chart_vectorised_broadcast_shapes() -> None:
    """Mixed broadcast: jd shape (3,) x lat/lon shape (2,1) -> (2,3)."""
    jd_arr = np.array([2451544.5, 2451545.0, 2451545.5])  # shape (3,)
    lat_arr = np.array([[48.8566], [-33.87]])              # shape (2, 1)
    lon_arr = np.array([[2.3522], [151.21]])               # shape (2, 1)
    result = is_day_chart(jd_arr, lat_arr, lon_arr)
    assert result.shape == (2, 3), (
        f"broadcast shape drifted: {result.shape}"
    )
    assert result.dtype == np.bool_


def test_is_day_chart_2d_input() -> None:
    """2-d jd input preserves the 2-d leading shape."""
    jd_arr = np.linspace(2451545.0, 2451545.0 + 30.0, 12).reshape(3, 4)
    result = is_day_chart(jd_arr, 48.8566, 2.3522)
    assert result.shape == (3, 4), f"2-d shape drifted: {result.shape}"
    assert result.dtype == np.bool_


# ---------------------------------------------------------------------------
# 4. Polar safety (D-15)
# ---------------------------------------------------------------------------

def test_is_day_chart_polar_safety_raises_nothing_at_lat_80() -> None:
    """D-15 ratchet: lat=80 must NOT raise HighLatitudeError; bool answer required."""
    # No pytest.raises — the assertion is that no exception escapes the call.
    result = is_day_chart(2451545.0, 80.0, 0.0)
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.bool_
    # Must be a proper bool, not NaN/uninitialised.
    assert result.item() in (True, False), (
        f"polar lat=80 should yield a clean bool; got {result!r}"
    )


@pytest.mark.parametrize("lat", [70.0, 75.0, 80.0, 85.0])
@pytest.mark.parametrize(
    "jd",
    [
        2451545.0,        # 2000-01-01 noon UT (winter NH)
        2451545.0 + 92,   # ~vernal equinox 2000
        2451545.0 + 183,  # ~summer solstice 2000
        2451545.0 + 274,  # ~autumnal equinox 2000
    ],
)
def test_is_day_chart_polar_safety_arctic_circle_returns_bool(
    lat: float, jd: float,
) -> None:
    """Across arctic latitudes & seasons, output is always a clean bool."""
    result = is_day_chart(jd, lat, 0.0)
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.bool_
    assert result.item() in (True, False)


# ---------------------------------------------------------------------------
# 5. Cross-API consistency vs CHART_DTYPE produced by compute_chart
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("label", "jd", "lat", "lon"),
    [
        ("Paris J2000 noon",   2451545.0,   48.8566,   2.3522),
        ("Sydney J2000 noon",  2451545.0,  -33.8688, 151.2093),
        ("New York J2000 noon", 2451545.0,  40.7128, -74.0060),
        ("Tokyo J2000 noon",   2451545.0,   35.6762, 139.6503),
        ("Reykjavik J2000 noon (sub-polar)", 2451545.0, 64.1466, -21.9426),
    ],
)
def test_is_day_chart_consistency_with_compute_chart_asc_and_sun_lon(
    label: str, jd: float, lat: float, lon: float,
) -> None:
    """``is_day_chart`` agrees with ``house_of(chart["body_lons"][0], chart["cusps"]) >= 7``.

    Sub-polar latitudes only (``polar_fallback="raise"`` is the default for
    ``compute_chart`` per D-11). Polar consistency is tested separately via
    explicit ``polar_fallback="porphyry"`` to mirror ``is_day_chart``'s
    internal choice (D-15).
    """
    del label  # only used for pytest IDs
    chart = compute_chart(jd, lat, lon)  # D-11 default: polar_fallback="raise"
    sun_lon = chart["body_lons"][0]      # body_id=0 = Sun (D-08, D-01)
    expected_house = house_of(sun_lon, chart["cusps"])
    expected = bool(int(expected_house) >= 7)
    actual = bool(is_day_chart(jd, lat, lon))
    assert actual == expected, (
        f"is_day_chart disagrees with house_of(chart['body_lons'][0], "
        f"chart['cusps']) >= 7 at {label}: actual={actual}, "
        f"expected={expected}, sun_house={int(expected_house)}"
    )


def test_is_day_chart_consistency_polar_via_explicit_porphyry() -> None:
    """At polar latitudes, ``is_day_chart`` matches ``compute_chart(polar_fallback="porphyry")``.

    This pins the D-15 internal-Porphyry choice: callers who supply the
    same fallback explicitly to ``compute_chart`` get the same sect
    answer as ``is_day_chart``.
    """
    jd, lat, lon = 2451545.0, 80.0, 0.0
    chart = compute_chart(jd, lat, lon, polar_fallback="porphyry")
    sun_lon = chart["body_lons"][0]
    expected = bool(int(house_of(sun_lon, chart["cusps"])) >= 7)
    actual = bool(is_day_chart(jd, lat, lon))
    assert actual == expected, (
        f"is_day_chart at polar lat=80 disagrees with "
        f"compute_chart(polar_fallback='porphyry'): "
        f"actual={actual}, expected={expected}"
    )


# ---------------------------------------------------------------------------
# 6. Sunrise-inclusive convention (D-13) pinned synthetically
# ---------------------------------------------------------------------------

def test_is_day_chart_sunrise_inclusive_pragmatic_convention() -> None:
    """Pin D-13 sunrise-inclusive convention via +/-0.01 deg synthetic deltas.

    This test pins the sunrise-inclusive convention pragmatically. Strict
    equality ``Sun == ASC`` has measure zero in real data; we validate
    +/-0.01 deg behaviour instead, which is what production callers
    actually encounter.

    Setup: take a real chart's cusps, then probe ``house_of`` directly
    with synthetic Sun longitudes at ``asc - 0.01`` deg (just above the
    horizon, in house 12 going eastward) and ``asc + 0.01`` deg (just
    below the horizon, in house 1). This isolates the convention from
    any ephemeris noise.
    """
    # Use Paris J2000 noon — a non-polar fixture from the consistency suite.
    jd, lat, lon = 2451545.0, 48.8566, 2.3522
    houses = calculate_houses(jd, lat, lon, polar_fallback="porphyry")
    asc = float(houses["asc"])
    cusps = houses["cusps"]

    # Sun just *above* the horizon (going eastward toward the MC), in
    # house 12 by the "cusps[i] BEGINS house i+1" convention; >= 7 = day.
    sun_just_above = (asc - 0.01) % 360.0
    house_above = int(house_of(np.float64(sun_just_above), cusps))
    assert house_above == 12, (
        f"Sun at asc-0.01 deg should map to house 12 (above-horizon side); "
        f"got {house_above}"
    )
    # By the >= 7 rule this is a day chart.
    assert house_above >= 7, "house 12 must be classified as day"

    # Sun just *below* the horizon (just past the ASC going eastward),
    # in house 1; < 7 = night.
    sun_just_below = (asc + 0.01) % 360.0
    house_below = int(house_of(np.float64(sun_just_below), cusps))
    assert house_below == 1, (
        f"Sun at asc+0.01 deg should map to house 1 (below-horizon side); "
        f"got {house_below}"
    )
    assert house_below < 7, "house 1 must be classified as night"


# ---------------------------------------------------------------------------
# 7. Geographic sanity — southern hemisphere
# ---------------------------------------------------------------------------

def test_is_day_chart_southern_hemisphere() -> None:
    """Sydney J2000 noon UTC = ~22h local time -> night chart.

    Sanity check that the helper honours east-positive longitude (Sydney
    is at lon = +151.21 deg) and respects Earth's rotation: at J2000 noon
    UTC, Sydney has the Sun below its horizon.
    """
    assert not bool(is_day_chart(2451545.0, -33.8688, 151.2093)), (
        "Sydney at J2000 12:00 UT (~22h local) must be a night chart"
    )


# ---------------------------------------------------------------------------
# 8. AGPL boundary ratchet (mirror tests/charts/test_compute_chart.py)
# ---------------------------------------------------------------------------

def test_no_runtime_swisseph_import_via_is_day_chart() -> None:
    """AGPL boundary: calling ``is_day_chart`` must not pull swisseph in.

    Mirrors the per-package ratchet from ``test_dtype.py`` and the
    ``compute_chart`` integration suite. Plan 14-04 wires no new runtime
    dep; this test catches any future regression where a contributor
    might accidentally import :mod:`swisseph` from inside
    ``ketu/charts/``.
    """
    # Trigger a real call so that any lazy imports would resolve.
    _ = is_day_chart(2451545.0, 48.86, 2.35)
    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("ketu.charts") and mod is not None:
            names = [
                n for n in dir(mod)
                if n.startswith("swe_") or n == "swisseph" or n == "swe"
            ]
            assert not names, (
                f"{mod_name} unexpectedly exposes swisseph-related "
                f"names: {names}"
            )
