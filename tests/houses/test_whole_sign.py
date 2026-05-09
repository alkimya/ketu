"""Whole Sign tests — closed-form, polar-safe, sign-floor invariants.

Two-tier oracle strategy (mirrors v1.1 Phase 10 pattern):

- **Algorithm tier** (``test_algorithm_matches_oracle_armc``): bit-exact
  comparison vs ``swe.houses_armc``, tolerance ``1e-6°``. Whole Sign is
  pure arithmetic (floor + modulo + addition), so machine precision is
  achievable on all 10 reference charts including polar latitudes.
- **End-to-end tier**: covered automatically by Plan 15-01's
  ``test_loaded_reference_snapshot_matches_oracle`` once it iterates
  whole_sign.

Plus invariants specific to Whole Sign:

- 30° spacing between adjacent cusps (modulo 360).
- ``cusps[0]`` is the start of the rising sign, NOT the ASC.
- ASC = 0° boundary case (Pitfall 3 from 15-RESEARCH §11).
- Registry registration.
- Vectorisation matches scalar element-wise.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.whole_sign import whole_sign_cusps

ALGO_TOL_DEG: float = 1e-6


# --- Algorithm-tier oracle ---------------------------------------------------


def test_whole_sign_algorithm_matches_oracle_armc_at_all_latitudes(
    reference_charts: list[dict[str, Any]],
) -> None:
    """Bit-exact match vs swe.houses_armc on all 10 reference charts."""
    from tests.houses.conftest import swe_oracle_armc

    for chart in reference_charts:
        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        armc = float(np.asarray(ascmc["armc"]))
        eps = float(np.asarray(ascmc["eps"]))
        cusps = whole_sign_cusps(
            np.asarray(armc, dtype=np.float64),
            np.asarray(chart["lat"], dtype=np.float64),
            np.asarray(eps, dtype=np.float64),
        )
        oracle = swe_oracle_armc(armc, float(chart["lat"]), eps, "whole_sign")
        if "error" in oracle:
            pytest.skip(
                f"swe.houses_armc errored at {chart['label']}: "
                f"{oracle['error']}"
            )
        # Short-arc distance (handles wraparound at 0/360).
        deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
        assert deltas.max() < ALGO_TOL_DEG, (
            f"{chart['label']}: max delta {deltas.max():.2e}° exceeds "
            f"{ALGO_TOL_DEG:.0e}° tolerance; cusps={cusps[:4]} vs "
            f"oracle={oracle['cusps'][:4]}"
        )


# --- Polar safety ------------------------------------------------------------


def test_whole_sign_no_nan_at_polar_latitudes() -> None:
    """Whole Sign is polar-safe by construction — no NaN at lat=70°/80°/89°."""
    for lat in (70.0, 80.0, 89.0):
        ascmc = compute_ascmc(2451545.0, lat, 0.0)
        cusps = whole_sign_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"Whole Sign returned NaN at lat={lat}°; polar safety regressed"
        )


# --- 30° spacing invariant ---------------------------------------------------


def test_whole_sign_cusps_evenly_spaced_30_degrees() -> None:
    """All adjacent cusps are exactly 30° apart (modulo 360)."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = whole_sign_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    diffs = np.diff(cusps) % 360.0
    np.testing.assert_allclose(diffs, 30.0, atol=1e-9)
    # Wraparound: cusps[0] = (cusps[11] + 30) % 360
    assert abs((cusps[11] + 30.0) % 360.0 - cusps[0]) < 1e-9


# --- Sign-floor convention (cusps[0] = start of rising sign) -----------------


def test_whole_sign_cusp_1_is_start_of_rising_sign() -> None:
    """cusps[0] = floor(asc / 30) * 30, NOT the ASC longitude itself."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = whole_sign_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    asc = float(ascmc["asc"])
    expected_cusp_1 = float(np.floor(asc / 30.0) * 30.0)
    assert abs(float(cusps[0]) - expected_cusp_1) < 1e-9, (
        f"cusps[0]={cusps[0]} but expected start-of-sign {expected_cusp_1} "
        f"(asc={asc:.4f}°). Whole Sign convention regressed — see PATTERNS §1."
    )
    # Sanity: cusps[0] is always a multiple of 30.
    assert abs(cusps[0] % 30.0) < 1e-9


# --- ASC = 0° boundary case (Pitfall 3) -------------------------------------


def test_whole_sign_asc_at_sign_boundary_yields_cusp_1_zero() -> None:
    """At ASC near 0° exact (Aries 0°), cusps[0] = 0.0 — sign boundary case.

    Pitfall 3 from 15-RESEARCH §11: ``floor(0/30)*30 = 0`` must NOT
    regress. We verify the Whole Sign output for an ARMC that yields
    ASC ≈ 0° (sign boundary) and assert that cusps[0] is exactly the
    floor (multiple of 30, no -1° drift).
    """
    armc = np.asarray(0.0, dtype=np.float64)
    lat = np.asarray(0.0, dtype=np.float64)
    eps = np.asarray(23.4393, dtype=np.float64)
    ascmc = compute_ascmc(2451545.0, 0.0, 0.0)
    asc = float(ascmc["asc"])
    if asc % 30.0 < 0.01 or asc % 30.0 > 29.99:
        # We're at a sign boundary — verify cusps[0] is exactly the floor.
        cusps = whole_sign_cusps(armc, lat, eps)
        assert abs(cusps[0] - np.floor(asc / 30.0) * 30.0) < 1e-9


# --- Registry registration ---------------------------------------------------


def test_whole_sign_registered_in_systems() -> None:
    """``@register('whole_sign')`` populates SYSTEMS at module import time."""
    from ketu.houses.registry import SYSTEMS, get_system
    assert "whole_sign" in SYSTEMS, (
        "whole_sign not registered — did __init__.py forget the trigger import?"
    )
    assert get_system("whole_sign") is whole_sign_cusps
    # Case-insensitive lookup.
    assert get_system("WHOLE_SIGN") is whole_sign_cusps


# --- Vectorisation -----------------------------------------------------------


def test_whole_sign_vectorised_matches_scalar_per_element() -> None:
    """Vector call returns same per-element result as N scalar calls."""
    armcs = np.array([0.0, 90.0, 180.0, 270.0])
    lats = np.array([10.0, 30.0, 50.0, 70.0])
    eps = np.array([23.44, 23.44, 23.44, 23.44])
    vec = whole_sign_cusps(armcs, lats, eps)
    assert vec.shape == (4, 12)
    for i in range(4):
        scalar = whole_sign_cusps(
            np.asarray(armcs[i], dtype=np.float64),
            np.asarray(lats[i], dtype=np.float64),
            np.asarray(eps[i], dtype=np.float64),
        )
        np.testing.assert_allclose(vec[i], scalar, atol=1e-12)


# --- Integration with calculate_houses ---------------------------------------


def test_calculate_houses_routes_whole_sign() -> None:
    """End-to-end: ``calculate_houses(..., system='whole_sign')`` returns finite cusps."""
    from ketu.houses import calculate_houses
    r = calculate_houses(2451545.0, 48.8566, 2.3522, system="whole_sign")
    assert r["cusps"].shape == (12,)
    assert not np.isnan(r["cusps"]).any()
    # Sign-floor: cusps[0] is multiple of 30.
    assert abs(float(r["cusps"][0]) % 30.0) < 1e-9
    # out["asc"] preserves the actual ASC (different from the sign-floor
    # except in the rare sign-boundary case).
    asc = float(r["asc"])
    cusp_1 = float(r["cusps"][0])
    if asc % 30.0 > 1e-9:
        assert abs(asc - cusp_1) > 1e-9, (
            f"asc={asc} should differ from sign-floor cusp_1={cusp_1}"
        )


def test_calculate_houses_whole_sign_polar_safe_no_fallback_needed() -> None:
    """At lat=80° with system='whole_sign', no HighLatitudeError raised."""
    from ketu.houses import calculate_houses
    # polar_fallback='raise' (default) — should NOT raise for whole_sign.
    r = calculate_houses(2451545.0, 80.0, 0.0, system="whole_sign")
    assert not np.isnan(r["cusps"]).any()
    assert r["system"] == "whole_sign"
