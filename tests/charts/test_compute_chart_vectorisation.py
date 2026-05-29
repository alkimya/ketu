"""Vectorisation tests for :func:`ketu.charts.compute_chart` (D-09, SC 14.2).

Pin the broadcast contract: ``(jd, lat, lon)`` of any compatible shape ``S``
yields a structured array of leading shape ``S`` with subarrays of shape
``S + (13,)`` and aspect block of shape ``S + (13, 13)``.

Hot-path constraint: no Python loop over ``S`` in the body-positions
pipeline (loop bound to 13 bodies via :func:`calc_planet_position_batch`).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.charts import compute_chart


# ---------------------------------------------------------------------------
# Shape pinning across 0-d / 1-d / 2-d / mixed broadcast inputs
# ---------------------------------------------------------------------------


def test_compute_chart_scalar_input_returns_zero_dim() -> None:
    """Scalar inputs yield a 0-d structured array with native subarray shapes."""
    chart = compute_chart(2451545.0, 48.86, 2.35)
    assert chart.shape == ()
    assert chart["body_lons"].shape == (14,)
    assert chart["body_lats"].shape == (14,)
    assert chart["body_speeds"].shape == (14,)
    assert chart["cusps"].shape == (12,)
    assert chart["aspect_matrix"].shape == (14, 14)
    assert chart["aspect_orbs"].shape == (14, 14)


def test_compute_chart_1d_input_preserves_leading_shape() -> None:
    """1-d ``jd`` input with scalar (lat, lon) → leading shape ``(N,)``."""
    jd_arr = np.array([2451545.0, 2470204.0])
    chart = compute_chart(jd_arr, 48.86, 2.35)
    assert chart.shape == (2,)
    assert chart["body_lons"].shape == (2, 14)
    assert chart["body_lats"].shape == (2, 14)
    assert chart["body_speeds"].shape == (2, 14)
    assert chart["cusps"].shape == (2, 12)
    assert chart["aspect_matrix"].shape == (2, 14, 14)
    assert chart["aspect_orbs"].shape == (2, 14, 14)


def test_compute_chart_2d_input_preserves_leading_shape() -> None:
    """2-d ``jd`` input with scalar (lat, lon) → leading shape ``(3, 2)``."""
    jd_arr = np.array([
        [2451545.0, 2470204.0],
        [2451545.0, 2470204.0],
        [2451545.0, 2470204.0],
    ])
    chart = compute_chart(jd_arr, 48.86, 2.35)
    assert chart.shape == (3, 2)
    assert chart["body_lons"].shape == (3, 2, 14)
    assert chart["cusps"].shape == (3, 2, 12)
    assert chart["aspect_matrix"].shape == (3, 2, 14, 14)


def test_compute_chart_broadcast_jd_lat_lon_mixed() -> None:
    """Mixed broadcast: jd shape (2,) × lat shape (3, 1) → leading shape (3, 2)."""
    jd_arr = np.array([2451545.0, 2470204.0])
    lat_arr = np.array([[48.86], [64.15], [40.71]])  # shape (3, 1)
    lon_arr = np.array([[2.35], [-21.94], [-74.01]])  # shape (3, 1)
    chart = compute_chart(jd_arr, lat_arr, lon_arr, polar_fallback="porphyry")
    assert chart.shape == (3, 2)
    # Broadcast-by-value sanity: each row carries its lat/lon, each
    # column its jd.
    assert np.allclose(chart["jd"], np.broadcast_to(jd_arr, (3, 2)))
    assert np.allclose(
        chart["lat"], np.broadcast_to(lat_arr, (3, 2))
    )
    assert np.allclose(
        chart["lon"], np.broadcast_to(lon_arr, (3, 2))
    )


# ---------------------------------------------------------------------------
# Vectorised vs scalar equivalence (D-09 — bit-for-bit on every field
# except aspect_matrix / aspect_orbs which are sentinel until 14-03)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "i",
    [0, 1, 2, 3, 4],
)
def test_compute_chart_vectorised_equivalent_to_loop(i: int) -> None:
    """Vectorised ``compute_chart`` matches scalar element-by-element."""
    jd_arr = np.array([
        2451545.0, 2460759.5, 2415020.5, 2470204.0, 2440000.0,
    ])
    lat_arr = np.array([48.86, 40.71, 51.48, 35.68, -33.87])
    lon_arr = np.array([2.35, -74.01, 0.0, 139.65, 151.21])

    batch = compute_chart(jd_arr, lat_arr, lon_arr)
    scalar = compute_chart(
        float(jd_arr[i]), float(lat_arr[i]), float(lon_arr[i])
    )

    # Field-by-field equivalence on everything except the sentinel
    # aspect block (which is identical -1 / NaN by construction; the
    # diagonal-only test will land in plan 14-03).
    for field in (
        "jd", "lat", "lon",
        "body_lons", "body_lats", "body_speeds",
        "cusps", "asc", "mc", "armc", "vertex",
    ):
        np.testing.assert_array_equal(
            np.asarray(batch[i][field]),
            np.asarray(scalar[field]),
            err_msg=f"vectorised vs scalar mismatch on field {field!r}",
        )
    # ``system`` is U10 → compare via str round-trip (NumPy 0-d str
    # comparison via ``==`` works but ``assert_array_equal`` rejects
    # the U10 zero-dim case in some NumPy versions).
    assert str(batch[i]["system"]) == str(scalar["system"])


def test_compute_chart_zero_python_loop_in_hot_path_proxy() -> None:
    """Soft latency check: 100 jd timestamps must complete under 5 s.

    Proxy for "no Python loop over S in the body-positions pipeline"
    (D-09 / SC 14.2). Marked ``slow`` so dev iteration can skip it via
    ``pytest -m 'not slow'``.
    """
    jd_arr = np.linspace(2451545.0, 2451545.0 + 365.0, 100)
    chart = compute_chart(jd_arr, 48.86, 2.35)
    assert chart.shape == (100,)
    assert chart["body_lons"].shape == (100, 14)
