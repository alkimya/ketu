"""Regiomontanus tests — closed-form, two-tier oracle, polar NaN propagation.

Two-tier oracle strategy (mirrors Koch v1.1 pattern):

- **Algorithm tier** (``test_regiomontanus_algorithm_matches_oracle_armc``):
  bit-exact comparison vs ``swe.houses_armc``, tolerance ``1e-6°``. Not
  eps-sensitive at the algorithm level (pole heights cancel the eps
  drift between mean and true obliquity).
- **End-to-end tier** (``test_regiomontanus_cusps_match_oracle_at_arcmin``):
  via ``swe_oracle`` snapshot (which calls ``swe.houses_ex`` with full
  sidereal time machinery), tolerance ``1.0/60.0°`` (1 arcmin) on 7 tight
  non-polar charts. Reykjavik (lat=64.1°N) gets a relaxed tolerance
  pinned empirically (see
  ``test_regiomontanus_reykjavik_drift_measured_and_pinned``).

Plus invariants and polar contract:

- 4 non-trivial cusps (11/12/2/3) via ``_asc1`` with pole heights
  ``fh1 = atan(tan(lat)/2)`` and ``fh2 = atan(tan(lat)·cos(30°))``.
- Cusps 5/6/8/9 are 180° opposites of 11/12/2/3.
- Cusps 1/4/7/10 = ASC/IC/DESC/MC.
- ``|lat| ≥ 90° − eps`` → NaN propagation (Koch-style, NOT swap).
- Registry registration.
- Vectorisation matches scalar.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.regiomontanus import regiomontanus_cusps

ARCMIN_DEG: float = 1.0 / 60.0
CUSP_TOL_ARCMIN: float = 1.0 * ARCMIN_DEG
ALGO_TOL_DEG: float = 1e-6

#: Reykjavik (lat=64.15°N) sits inside the high-latitude band where
#: eps_mean vs eps_true drift in the snapshot oracle propagates through
#: the pole-height formulas. The 15-RESEARCH §14.3 estimate was 2-5
#: arcmin; the empirical measurement on 2026-05-09 yielded a max drift
#: of **0.8581 arcmin** (well below the initial 5' cap and below 1' too).
#: Pinned at 1.0 arcmin per Plan 15-03 Task 5 decision-tree (< 1 arcmin
#: case): "Regio est plus précis que prévu", margin ~0.14' against
#: future drift via the 1.0' bound. If a future regen of the snapshot
#: pushes the drift above 1', tighten or relax with a fresh measurement
#: rather than blanket-relax this constant.
#:
#: Measurement reproduction:
#:     pytest tests/houses/test_regiomontanus.py::test_regiomontanus_reykjavik_drift_measured_and_pinned -s
REYKJAVIK_REGIO_TOL_ARCMIN: float = 1.0 * ARCMIN_DEG  # measured 0.86' on 2026-05-09

#: Charts that should match the oracle within the standard 1-arcmin
#: tolerance (excludes Reykjavik, polar, and equator-degenerate cases).
NON_POLAR_LABELS_TIGHT: tuple[str, ...] = (
    "J2000_Greenwich",
    "J2000_Paris",
    "J2000_Sydney",
    "J2000_Tokyo",
    "J2000_BuenosAires",
    "J2000_Equator",
    "1900_NewYork",
)

NON_POLAR_LABELS: tuple[str, ...] = NON_POLAR_LABELS_TIGHT + ("2050_Reykjavik",)


# --- Algorithm-tier oracle (bit-exact 1e-6°) ---------------------------------


def test_regiomontanus_algorithm_matches_oracle_armc(
    reference_charts: list[dict[str, Any]],
) -> None:
    """Algorithm tier: bit-exact match vs swe.houses_armc on non-polar charts.

    1e-6° tolerance — the algorithm is not eps-sensitive at this tier
    because both Ketu and swisseph use the same eps input. End-to-end
    drift (Reykjavik) appears in the snapshot tier, not here.
    """
    from tests.houses.conftest import swe_oracle_armc

    for chart in reference_charts:
        if chart["label"] not in NON_POLAR_LABELS:
            continue
        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        armc = float(np.asarray(ascmc["armc"]))
        eps = float(np.asarray(ascmc["eps"]))
        cusps = regiomontanus_cusps(
            np.asarray(armc, dtype=np.float64),
            np.asarray(chart["lat"], dtype=np.float64),
            np.asarray(eps, dtype=np.float64),
        )
        oracle = swe_oracle_armc(armc, float(chart["lat"]), eps, "regiomontanus")
        if "error" in oracle:
            pytest.skip(f"oracle errored at {chart['label']}: {oracle['error']}")
        deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
        assert deltas.max() < ALGO_TOL_DEG, (
            f"{chart['label']}: max delta {deltas.max():.2e}° exceeds "
            f"{ALGO_TOL_DEG:.0e}° tolerance; cusps[:4]={cusps[:4]} vs "
            f"oracle={oracle['cusps'][:4]}"
        )


# --- End-to-end snapshot tier (1 arcmin) -------------------------------------


@pytest.mark.parametrize("label", NON_POLAR_LABELS_TIGHT)
def test_regiomontanus_cusps_match_oracle_at_arcmin(
    label: str,
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """End-to-end: snapshot match within 1 arcmin on tight non-polar charts."""
    chart = next(c for c in reference_charts if c["label"] == label)
    ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"], dtype=np.float64),
        np.asarray(chart["lat"], dtype=np.float64),
        np.asarray(ascmc["eps"], dtype=np.float64),
    )
    snap = loaded_reference_snapshot["charts"][label]["systems"]["regiomontanus"]
    if "error" in snap:
        pytest.skip(f"{label}: snapshot has polar error")
    oracle_cusps = np.asarray(snap["cusps"], dtype=np.float64)
    deltas = np.abs(((cusps - oracle_cusps + 180.0) % 360.0) - 180.0)
    assert deltas.max() < CUSP_TOL_ARCMIN, (
        f"{label}: max delta {deltas.max() * 60:.4f}' exceeds 1 arcmin; "
        f"cusps[:4]={cusps[:4]} vs oracle={oracle_cusps[:4]}"
    )


# --- Reykjavik tolerance — MEASURED EMPIRICALLY then pinned -----------------


def test_regiomontanus_reykjavik_drift_measured_and_pinned(
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """Reykjavik (lat=64.15°N) drift must stay within the pinned tolerance.

    Measurement procedure (Task 5 of plan 15-03):
        1. Run this test with REYKJAVIK_REGIO_TOL_ARCMIN = 5.0 (initial).
        2. Inspect the printed delta_max.
        3. Update the constant to (delta_max + 0.5) arcmin (margin).
        4. If delta_max > 5 arcmin, BUG, NOT a tolerance to relax (see
           Pitfall 4: pole-height substitution error). Investigate
           BEFORE pinning.
    """
    chart = next(c for c in reference_charts if c["label"] == "2050_Reykjavik")
    ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"], dtype=np.float64),
        np.asarray(chart["lat"], dtype=np.float64),
        np.asarray(ascmc["eps"], dtype=np.float64),
    )
    snap = loaded_reference_snapshot["charts"]["2050_Reykjavik"]["systems"]["regiomontanus"]
    oracle_cusps = np.asarray(snap["cusps"], dtype=np.float64)
    deltas = np.abs(((cusps - oracle_cusps + 180.0) % 360.0) - 180.0)
    delta_max = float(deltas.max())
    print(f"\nReykjavik Regiomontanus drift: max={delta_max * 60:.4f}'")
    assert delta_max < REYKJAVIK_REGIO_TOL_ARCMIN, (
        f"Reykjavik drift {delta_max * 60:.4f}' exceeds pinned tolerance "
        f"{REYKJAVIK_REGIO_TOL_ARCMIN * 60:.4f}'. If delta < 5', this is "
        "likely an eps_mean vs eps_true drift; measure and tighten "
        "REYKJAVIK_REGIO_TOL_ARCMIN. If delta >= 5', suspect Pitfall 4 "
        "(pole-height substitution error in regiomontanus.py)."
    )


# --- Polar contract (NaN propagation) ---------------------------------------


def test_regiomontanus_yields_nan_above_polar_circle() -> None:
    """Above the polar circle (|lat| >= 90° - eps), Regiomontanus NaN-propagates."""
    from ketu.houses.porphyry import polar_circle
    jd = 2451545.0
    pc = float(polar_circle(jd))
    lat = pc + 1.0  # 1° beyond polar circle
    ascmc = compute_ascmc(jd, lat, 0.0)
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"], dtype=np.float64),
        np.asarray(lat, dtype=np.float64),
        np.asarray(ascmc["eps"], dtype=np.float64),
    )
    assert np.isnan(cusps).any(), (
        f"Regiomontanus 1° beyond polar circle (lat={lat}°) must NaN at "
        "least one cusp; calculate_houses uses np.isnan to route via "
        "polar_fallback per HOU-06 (D-02 in 15-CONTEXT.md)."
    )


def test_regiomontanus_polar_lat_80_yields_all_nan() -> None:
    """At lat=80° (well beyond polar), Regiomontanus returns all-NaN."""
    jd = 2451545.0
    ascmc = compute_ascmc(jd, 80.0, 0.0)
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"], dtype=np.float64),
        np.asarray(80.0, dtype=np.float64),
        np.asarray(ascmc["eps"], dtype=np.float64),
    )
    assert np.isnan(cusps).all(), (
        "At lat=80° all 12 cusps must be NaN (the entire polar mask applies)"
    )


def test_regiomontanus_no_silent_nan_at_mid_latitudes(
    reference_charts: list[dict[str, Any]],
) -> None:
    """At non-polar latitudes, regiomontanus_cusps NEVER returns NaN.

    Regression catcher: if a sign error or domain error introduces NaN
    at a normal latitude, this test fails fast.
    """
    for chart in reference_charts:
        if chart["label"] not in NON_POLAR_LABELS:
            continue
        ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
        cusps = regiomontanus_cusps(
            np.asarray(ascmc["armc"], dtype=np.float64),
            np.asarray(chart["lat"], dtype=np.float64),
            np.asarray(ascmc["eps"], dtype=np.float64),
        )
        assert not np.isnan(cusps).any(), (
            f"{chart['label']}: regiomontanus produced NaN at non-polar "
            f"latitude {chart['lat']}° - Pitfall 4 (pole-height) suspected."
        )


# --- Cusp symmetry (5/6/8/9 = 11/12/2/3 + 180°) -----------------------------


def test_regiomontanus_cusps_5_6_8_9_are_opposites_of_11_12_2_3() -> None:
    """Cusps 5,6,8,9 are 180° opposites of 11,12,2,3 by construction."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"], dtype=np.float64),
        np.asarray(48.8566, dtype=np.float64),
        np.asarray(ascmc["eps"], dtype=np.float64),
    )
    # Index map: cusp_5 = idx 4, cusp_11 = idx 10 ; cusp_6 = idx 5, cusp_12 = idx 11 ;
    # cusp_8 = idx 7, cusp_2 = idx 1 ; cusp_9 = idx 8, cusp_3 = idx 2.
    pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]
    for left, right in pairs:
        diff = ((cusps[left] - cusps[right]) % 360.0)
        assert abs(diff - 180.0) < 1e-9, (
            f"cusps[{left}]={cusps[left]} should be 180° from "
            f"cusps[{right}]={cusps[right]}; got delta {diff}°"
        )


# --- Constants invariant -----------------------------------------------------


def test_regiomontanus_constants_unchanged() -> None:
    """API parity constants (MAX_ITER, TOL_DEG) preserved as in Koch."""
    from ketu.houses.regiomontanus import MAX_ITER, TOL_DEG
    assert MAX_ITER == 50
    assert TOL_DEG == 1e-7


# --- Vectorisation -----------------------------------------------------------


def test_regiomontanus_vectorised_matches_scalar_per_element() -> None:
    """Vector call returns same per-element result as N scalar calls."""
    armcs = np.array([0.0, 90.0, 180.0, 270.0])
    lats = np.array([10.0, 30.0, 40.0, 50.0])  # all non-polar
    eps = np.array([23.44, 23.44, 23.44, 23.44])
    vec = regiomontanus_cusps(armcs, lats, eps)
    assert vec.shape == (4, 12)
    for i in range(4):
        scalar = regiomontanus_cusps(
            np.asarray(armcs[i], dtype=np.float64),
            np.asarray(lats[i], dtype=np.float64),
            np.asarray(eps[i], dtype=np.float64),
        )
        np.testing.assert_allclose(vec[i], scalar, atol=1e-10)


# --- Registry registration ---------------------------------------------------


def test_regiomontanus_registered_in_systems() -> None:
    """``@register('regiomontanus')`` populates SYSTEMS at module import time."""
    from ketu.houses.registry import SYSTEMS, get_system
    assert "regiomontanus" in SYSTEMS, (
        "regiomontanus not registered - did __init__.py forget the trigger import?"
    )
    assert get_system("regiomontanus") is regiomontanus_cusps
    assert get_system("REGIOMONTANUS") is regiomontanus_cusps
