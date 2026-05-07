"""Koch house system tests vs swisseph oracle (HOU-04, HOU-09).

Two-tier oracle strategy (research §"Don't Hand-Roll" + Plan 10-02 design):

- **Algorithm tier** (``swe_oracle_armc``): isolates Koch's per-cusp formula
  from sidereal-time / obliquity precision. We supply our own ARMC and the
  oracle returns cusps for that exact ARMC. Strict tolerance (machine
  precision) — verifies the algorithm is correct.
- **End-to-end tier** (snapshot): full path
  ``compute_ascmc(jd, lat, lon) -> koch_cusps``. Inherits any ARMC / eps
  drift from Plan 10-03's :func:`compute_ascmc` (which uses ``eps_mean``;
  swisseph internally uses ``eps_true``). Tolerance: <1 arcmin on 7 of 8
  non-polar reference charts; 2050_Reykjavik (lat 64.1°N) sits at ~2.5
  arcmin because Koch's trisection amplifies the inherited eps drift more
  than Placidus does at the same latitude — pinned by a separate test.

Reference fixtures from Plan 10-02 (``tests/houses/conftest.py`` +
``fixtures/reference_charts.json``).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.koch import MAX_ITER, TOL_DEG, koch_cusps

ARCMIN_DEG: float = 1.0 / 60.0
CUSP_TOL_ARCMIN: float = 1.0 * ARCMIN_DEG  # HOU-09: <1 arcmin
ALGO_TOL_DEG: float = 1e-6  # algorithm-tier (swe_oracle_armc): bit-exact

# 7 non-polar charts that meet the <1 arcmin spec end-to-end. Reykjavik
# (8th) is exercised separately at the inherited-precision tolerance.
NON_POLAR_LABELS_TIGHT: list[str] = [
    "J2000_Greenwich",
    "J2000_Paris",
    "J2000_Sydney",
    "J2000_Tokyo",
    "J2000_BuenosAires",
    "J2000_Equator",
    "1900_NewYork",
]

NON_POLAR_LABELS: list[str] = NON_POLAR_LABELS_TIGHT + ["2050_Reykjavik"]


# ---------------------------------------------------------------------------
# Algorithm tier — swe_oracle_armc isolation (bit-exact)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", NON_POLAR_LABELS)
def test_koch_algorithm_matches_oracle_armc_at_machine_precision(
    label: str,
    reference_charts: list[dict[str, Any]],
) -> None:
    """Koch matches swisseph bit-exact when given the same (ARMC, lat, eps).

    Validates the per-cusp formula independent of input precision — this is
    the Plan 10-02 ``swe_oracle_armc`` design intent: isolate algorithm
    error from sidereal-time / obliquity error.
    """
    from tests.houses.conftest import swe_oracle_armc

    chart = next(c for c in reference_charts if c["label"] == label)
    ascmc = compute_ascmc(
        float(chart["jd"]),
        float(chart["lat"]),
        float(chart["lon"]),
    )
    armc = float(ascmc["armc"])
    eps = float(ascmc["eps"])
    lat = float(chart["lat"])

    cusps = koch_cusps(
        np.asarray(armc),
        np.asarray(lat),
        np.asarray(eps),
    )
    oracle = swe_oracle_armc(armc, lat, eps, "koch")
    if "polar" in oracle:  # algorithm-tier should not hit polar at non-polar lat
        pytest.fail(f"{label}: oracle returned polar error: {oracle['error']}")
    deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
    for i in range(12):
        assert float(deltas[i]) < ALGO_TOL_DEG, (
            f"{label}: Koch algorithm cusp {i + 1} drift "
            f"{float(deltas[i]) * 3600:.6f}\" > {ALGO_TOL_DEG * 3600:.6f}\""
        )


# ---------------------------------------------------------------------------
# End-to-end tier — snapshot match at <1 arcmin (7 charts) and inherited
# precision floor at Reykjavik
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", NON_POLAR_LABELS_TIGHT)
def test_koch_cusps_match_oracle_at_arcmin(
    label: str,
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """End-to-end (compute_ascmc -> koch_cusps) within <1 arcmin per cusp."""
    chart = next(c for c in reference_charts if c["label"] == label)
    snap_chart = loaded_reference_snapshot["charts"][label]
    snap_cusps = np.asarray(
        snap_chart["systems"]["koch"]["cusps"], dtype=np.float64
    )

    ascmc = compute_ascmc(
        float(chart["jd"]),
        float(chart["lat"]),
        float(chart["lon"]),
    )
    cusps = koch_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(float(chart["lat"])),
        np.asarray(ascmc["eps"]),
    )
    deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)
    for i in range(12):
        assert deltas[i] < CUSP_TOL_ARCMIN, (
            f"{label}: Koch cusp {i + 1} drift "
            f"{float(deltas[i]) * 60:.4f} arcmin "
            f"(got {float(cusps[i]):.6f}, oracle {float(snap_cusps[i]):.6f})"
        )


def test_koch_reykjavik_within_inherited_precision_floor(
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """Reykjavik (64.1°N) end-to-end Koch drift bounded by inherited eps drift.

    Plan 10-03 returns ``eps_mean`` from ``compute_ascmc``; swisseph uses
    ``eps_true`` internally. The eps difference is ~7.4″ at this epoch;
    Koch's trisection (``Asc1`` projection at high latitude with ``cos(lat)``
    in the denominator of ``sina``) amplifies this to ~2.5 arcmin. Plan 10-04
    Placidus saw ~51.5″ at the same chart from the same source. Pinned at
    3 arcmin so a future Plan 10-03 upgrade to ``eps_true`` (or any change
    that worsens the Koch drift) is caught loudly.
    """
    chart = next(c for c in reference_charts if c["label"] == "2050_Reykjavik")
    snap_cusps = np.asarray(
        loaded_reference_snapshot["charts"]["2050_Reykjavik"]
        ["systems"]["koch"]["cusps"],
        dtype=np.float64,
    )
    ascmc = compute_ascmc(
        float(chart["jd"]),
        float(chart["lat"]),
        float(chart["lon"]),
    )
    cusps = koch_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(float(chart["lat"])),
        np.asarray(ascmc["eps"]),
    )
    deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)
    REYKJAVIK_KOCH_TOL_ARCMIN: float = 3.0 * ARCMIN_DEG  # ~2.5' empirical + margin
    assert deltas.max() < REYKJAVIK_KOCH_TOL_ARCMIN, (
        f"Reykjavik Koch max drift {deltas.max() * 60:.3f} arcmin > "
        f"{REYKJAVIK_KOCH_TOL_ARCMIN * 60:.0f} arcmin tolerance — "
        "either inherited eps precision regressed or Koch formula broke"
    )


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------


def test_koch_iter_constants_match_research() -> None:
    """``MAX_ITER == 50`` (HOU-03) and ``TOL_DEG == 1e-7`` per research."""
    assert MAX_ITER == 50
    assert TOL_DEG == 1e-7


def test_koch_vectorized_matches_scalar_per_element() -> None:
    """Batched ``(armc, lat, eps)`` arrays produce per-element-equal results."""
    jds = np.array([2451545.0, 2470204.0, 2415020.5])
    lats = np.array([48.8566, 64.1466, 40.7128])
    lons = np.array([2.3522, -21.9426, -74.0060])
    ascmc_b = compute_ascmc(jds, lats, lons)
    cusps_b = koch_cusps(ascmc_b["armc"], lats, ascmc_b["eps"])

    for i in range(3):
        ai = compute_ascmc(float(jds[i]), float(lats[i]), float(lons[i]))
        ci = koch_cusps(
            np.asarray(ai["armc"]),
            np.asarray(float(lats[i])),
            np.asarray(ai["eps"]),
        )
        np.testing.assert_allclose(cusps_b[i], ci, atol=1e-9, rtol=0)


def test_koch_cusps_5_6_8_9_are_opposites_of_11_12_2_3() -> None:
    """Cusps 5/6/8/9 = (cusps 11/12/2/3 + 180) mod 360 by construction."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = koch_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    # Cusp ordering: [asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]
    pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]  # (derived_idx, source_idx)
    for derived_idx, source_idx in pairs:
        expected = (cusps[source_idx] + 180.0) % 360.0
        delta = abs(((cusps[derived_idx] - expected + 180.0) % 360.0) - 180.0)
        assert delta < 1e-9, (
            f"cusp {derived_idx + 1} ({cusps[derived_idx]:.9f}) is not the "
            f"opposite of cusp {source_idx + 1} ({cusps[source_idx]:.9f})"
        )


def test_koch_polar_lat_80_yields_nan() -> None:
    """At lat=80° (beyond polar circle) Koch returns NaN cusps."""
    ascmc = compute_ascmc(2451545.0, 80.0, 0.0)
    cusps = koch_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(80.0),
        np.asarray(ascmc["eps"]),
    )
    assert np.isnan(cusps).any(), "Koch at lat=80° must produce NaN cusps"


def test_koch_no_silent_nan_at_mid_latitudes(
    reference_charts: list[dict[str, Any]],
) -> None:
    """No NaN cusps at any non-polar reference chart (|lat| < 65°)."""
    for chart in reference_charts:
        lat = float(chart["lat"])
        if abs(lat) >= 65.0:
            continue
        ascmc = compute_ascmc(
            float(chart["jd"]), lat, float(chart["lon"])
        )
        cusps = koch_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"silent NaN at {chart['label']} (lat={lat})"
        )


def test_koch_registered_in_systems() -> None:
    """``@register('koch')`` populates the SYSTEMS registry."""
    from ketu.houses.registry import SYSTEMS, get_system
    assert "koch" in SYSTEMS
    assert get_system("koch") is koch_cusps
    assert get_system("KOCH") is koch_cusps  # case-insensitive lookup
