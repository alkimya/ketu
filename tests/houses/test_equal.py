"""Equal (ASC-anchored) house tests — closed-form, polar-safe, 30°-spacing invariants.

Two-tier oracle strategy:

- **Algorithm tier**: bit-exact match vs ``swe.houses_armc`` (tolerance 1e-6°).
- **End-to-end tier**: covered by Plan 15-01's snapshot ratchet.

Plus the Equal-specific divergence tests:

- ``cusps[0] == asc`` (consistent with Placidus/Koch/Porphyry).
- ``cusps[9] == (asc + 270) mod 360`` ≠ astronomical MC (HOU2-02 contract).
- 30° spacing.
- Registry, vectorisation.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.equal import equal_cusps

ALGO_TOL_DEG: float = 1e-6


def test_equal_algorithm_matches_oracle_armc_at_all_latitudes(
    reference_charts: list[dict[str, Any]],
) -> None:
    """Bit-exact match vs swe.houses_armc on all 10 reference charts."""
    from tests.houses.conftest import swe_oracle_armc

    for chart in reference_charts:
        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        armc = float(np.asarray(ascmc["armc"]))
        eps = float(np.asarray(ascmc["eps"]))
        cusps = equal_cusps(
            np.asarray(armc, dtype=np.float64),
            np.asarray(chart["lat"], dtype=np.float64),
            np.asarray(eps, dtype=np.float64),
        )
        oracle = swe_oracle_armc(armc, float(chart["lat"]), eps, "equal")
        if "error" in oracle:
            pytest.skip(
                f"swe.houses_armc errored at {chart['label']}: "
                f"{oracle['error']}"
            )
        deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
        assert deltas.max() < ALGO_TOL_DEG, (
            f"{chart['label']}: max delta {deltas.max():.2e}° exceeds "
            f"{ALGO_TOL_DEG:.0e}° tolerance"
        )


def test_equal_no_nan_at_polar_latitudes() -> None:
    """Equal is polar-safe by construction — no NaN at lat=70°/80°/89°."""
    for lat in (70.0, 80.0, 89.0):
        ascmc = compute_ascmc(2451545.0, lat, 0.0)
        cusps = equal_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"Equal returned NaN at lat={lat}°; polar safety regressed"
        )


def test_equal_cusps_evenly_spaced_30_degrees() -> None:
    """All adjacent cusps are exactly 30° apart (modulo 360)."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = equal_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    diffs = np.diff(cusps) % 360.0
    np.testing.assert_allclose(diffs, 30.0, atol=1e-9)


def test_equal_cusp_1_equals_ascendant() -> None:
    """cusps[0] == asc (consistent with Placidus/Koch/Porphyry convention).

    Paris J2000 is non-polar (lat=48.86° well below polar circle), so
    no swisseph swap occurs. We ratchet the actual short-arc equality
    cusps[0] == asc, not a noop modulo identity.
    """
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = equal_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    asc = float(ascmc["asc"])
    # Short-arc comparison: distance modulo 360°, accepting up to 1e-6°
    # tolerance. ``((x - asc + 180) % 360) - 180`` maps any wrap into
    # [-180°, +180°].
    short_arc = ((float(cusps[0]) - asc + 180.0) % 360.0) - 180.0
    assert abs(short_arc) < 1e-6, (
        f"cusps[0]={cusps[0]:.9f} should equal asc={asc:.9f} "
        f"(short_arc={short_arc:.9f}°)"
    )
    # Plus, cusps[0] differs from cusps[9] by exactly 90° going short-arc
    # (cusps[9] is asc+270, so the short distance from cusps[0] to
    # cusps[9] eastward is 270°; westward is 90°).
    diff = (float(cusps[0]) - float(cusps[9]) + 360.0) % 360.0
    assert abs(diff - 90.0) < 1e-9, (
        f"cusps[0] - cusps[9] should be 90° (mod 360), got {diff}°"
    )


def test_equal_cusp_10_is_asc_plus_270_not_astronomical_mc() -> None:
    """cusps[9] = (asc + 270) mod 360, which generally ≠ astronomical MC.

    HOU2-02 contract (PATTERNS §14.2): Equal is ASC-anchored, NOT
    MC-anchored. At Paris J2000, ASC ≈ 26.77° and MC ≈ 281.78° — the
    Equal cusp 10 = 296.77°, divergent from the astro MC by ~15°.
    """
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = equal_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    asc = float(ascmc["asc"])
    mc = float(ascmc["mc"])
    expected_equal_cusp_10 = (asc + 270.0) % 360.0
    assert abs(float(cusps[9]) - expected_equal_cusp_10) < 1e-9, (
        f"cusps[9]={cusps[9]} but expected (asc+270)%360={expected_equal_cusp_10}"
    )
    # Sanity: at Paris J2000 the divergence vs astronomical MC is > 1°.
    delta_to_astro_mc = abs(((float(cusps[9]) - mc + 180.0) % 360.0) - 180.0)
    assert delta_to_astro_mc > 1.0, (
        f"Equal cusp 10 ({cusps[9]:.4f}°) should diverge from astro MC "
        f"({mc:.4f}°) by > 1° at Paris J2000; got {delta_to_astro_mc:.4f}°. "
        "Did the implementation accidentally use MC instead of (asc+270)?"
    )


def test_equal_registered_in_systems() -> None:
    """``@register('equal')`` populates SYSTEMS at module import time."""
    from ketu.houses.registry import SYSTEMS, get_system
    assert "equal" in SYSTEMS
    assert get_system("equal") is equal_cusps
    assert get_system("EQUAL") is equal_cusps


def test_equal_vectorised_matches_scalar_per_element() -> None:
    """Vector call returns same per-element result as N scalar calls."""
    armcs = np.array([0.0, 90.0, 180.0, 270.0])
    lats = np.array([10.0, 30.0, 50.0, 70.0])
    eps = np.array([23.44, 23.44, 23.44, 23.44])
    vec = equal_cusps(armcs, lats, eps)
    assert vec.shape == (4, 12)
    for i in range(4):
        scalar = equal_cusps(
            np.asarray(armcs[i], dtype=np.float64),
            np.asarray(lats[i], dtype=np.float64),
            np.asarray(eps[i], dtype=np.float64),
        )
        np.testing.assert_allclose(vec[i], scalar, atol=1e-12)


def test_calculate_houses_routes_equal() -> None:
    """End-to-end: ``calculate_houses(..., system='equal')`` returns finite cusps."""
    from ketu.houses import calculate_houses
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="equal")
    assert r["cusps"].shape == (12,)
    assert not np.isnan(r["cusps"]).any()
    # cusps[9] = (asc + 270) % 360 — verify the ASC-anchored convention.
    asc = float(r["asc"])
    expected = (asc + 270.0) % 360.0
    # Allow modest delta because the ASC stored may differ from the
    # post-swap ASC used internally by equal_cusps. Tolerance 1e-6° is
    # appropriate for non-polar charts (Paris is well within polar
    # circle).
    assert abs(float(r["cusps"][9]) - expected) < 1e-6


def test_calculate_houses_equal_polar_safe_no_fallback_needed() -> None:
    """At lat=80° with system='equal', no HighLatitudeError raised."""
    from ketu.houses import calculate_houses
    r = calculate_houses(2451545.0, 80.0, 0.0, system="equal")
    assert not np.isnan(r["cusps"]).any()
    assert r["system"] == "equal"
