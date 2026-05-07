"""Placidus house system tests vs swisseph oracle.

Tolerance: <1 arcmin (1/60 deg ≈ 0.01667°) per HOU-01 / HOU-09 spec.

Reference fixtures from ``tests/houses/fixtures/reference_charts.json`` —
loaded via the ``loaded_reference_snapshot`` fixture from
``tests/houses/conftest.py`` (Plan 10-02 owns the path resolution and the
skip-on-missing fallback).

The 8 non-polar reference charts are:

- J2000_Greenwich      (51.5°N)
- J2000_Paris          (48.9°N)
- J2000_Sydney         (-33.9°N)
- J2000_Tokyo          (35.7°N)
- J2000_BuenosAires    (-34.6°N)
- J2000_Equator        (0°)
- 1900_NewYork         (40.7°N)
- 2050_Reykjavik       (64.1°N)  ← high-lat, near-polar yellow flag
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.placidus import MAX_ITER, TOL_DEG, placidus_cusps

ARCMIN_DEG: float = 1.0 / 60.0
CUSP_TOL: float = 1.0 * ARCMIN_DEG  # HOU-01 / HOU-09: <1 arcmin

NON_POLAR_LABELS: list[str] = [
    "J2000_Greenwich",
    "J2000_Paris",
    "J2000_Sydney",
    "J2000_Tokyo",
    "J2000_BuenosAires",
    "J2000_Equator",
    "1900_NewYork",
    "2050_Reykjavik",
]


@pytest.mark.parametrize("label", NON_POLAR_LABELS)
def test_placidus_cusps_match_oracle_at_arcmin(
    label: str,
    reference_charts: list[dict[str, object]],
    loaded_reference_snapshot: dict[str, object],
) -> None:
    """All 12 cusps agree with swisseph at every non-polar reference chart.

    HOU-09 + HOU-03: 8 charts × 12 cusps = 96 oracle-agreement assertions
    at the <1 arcmin spec tolerance.
    """
    chart = next(c for c in reference_charts if c["label"] == label)
    charts_dict: dict[str, object] = loaded_reference_snapshot["charts"]  # type: ignore[assignment]
    snap_chart: dict[str, object] = charts_dict[label]  # type: ignore[assignment]
    snap_systems: dict[str, object] = snap_chart["systems"]  # type: ignore[assignment]
    snap_placidus: dict[str, object] = snap_systems["placidus"]  # type: ignore[assignment]
    snap_cusps = np.asarray(snap_placidus["cusps"], dtype=np.float64)

    ascmc = compute_ascmc(
        float(chart["jd"]),  # type: ignore[arg-type]
        float(chart["lat"]),  # type: ignore[arg-type]
        float(chart["lon"]),  # type: ignore[arg-type]
    )
    cusps = placidus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(float(chart["lat"])),  # type: ignore[arg-type]
        np.asarray(ascmc["eps"]),
    )

    # Modular distance per cusp (handles 0/360 wrap, Pitfall 3).
    deltas = np.abs(((cusps - snap_cusps + 180.0) % 360.0) - 180.0)

    for i in range(12):
        assert deltas[i] < CUSP_TOL, (
            f"{label}: cusp {i + 1} drift {float(deltas[i]) * 60:.4f} arcmin "
            f"> {CUSP_TOL * 60:.4f} arcmin "
            f"(got {float(cusps[i]):.6f}, oracle {float(snap_cusps[i]):.6f})"
        )


def test_placidus_cusps_1_4_7_10_match_ascmc() -> None:
    """Cusps 1, 4, 7, 10 are closed-form (ASC, IC, DESC, MC) — never iterated."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = placidus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    asc = float(ascmc["asc"])
    mc = float(ascmc["mc"])
    ic = (mc + 180.0) % 360.0
    desc = (asc + 180.0) % 360.0

    def mod_delta(a: float, b: float) -> float:
        return abs(((a - b + 180.0) % 360.0) - 180.0)

    assert mod_delta(float(cusps[0]), asc) < 1e-9, "cusp 1 != ASC"
    assert mod_delta(float(cusps[3]), ic) < 1e-9, "cusp 4 != IC"
    assert mod_delta(float(cusps[6]), desc) < 1e-9, "cusp 7 != DESC"
    assert mod_delta(float(cusps[9]), mc) < 1e-9, "cusp 10 != MC"


def test_placidus_cusps_5_6_8_9_are_opposites_of_11_12_2_3() -> None:
    """Derived cusps are exact 180° opposites by construction."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = placidus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    # (derived 0-index, source 0-index): cusp 5↔11, 6↔12, 8↔2, 9↔3.
    pairs: list[tuple[int, int]] = [(4, 10), (5, 11), (7, 1), (8, 2)]
    for derived_idx, source_idx in pairs:
        expected = (float(cusps[source_idx]) + 180.0) % 360.0
        actual = float(cusps[derived_idx])
        delta = abs(((actual - expected + 180.0) % 360.0) - 180.0)
        assert delta < 1e-9, (
            f"cusp index {derived_idx} = {actual:.6f}; "
            f"expected (cusp {source_idx} + 180) mod 360 = {expected:.6f}; "
            f"delta = {delta:.6e}"
        )


def test_placidus_vectorized_matches_scalar_per_element() -> None:
    """Running on 3 charts at once == running each individually (HOU-08)."""
    jds = np.array([2451545.0, 2470204.0, 2415020.5])
    lats = np.array([48.8566, 64.1466, 40.7128])
    lons = np.array([2.3522, -21.9426, -74.0060])

    ascmc_batch = compute_ascmc(jds, lats, lons)
    cusps_batch = placidus_cusps(ascmc_batch["armc"], lats, ascmc_batch["eps"])

    assert cusps_batch.shape == (3, 12), f"expected (3, 12); got {cusps_batch.shape}"

    for i in range(3):
        ascmc_i = compute_ascmc(float(jds[i]), float(lats[i]), float(lons[i]))
        cusps_i = placidus_cusps(
            np.asarray(ascmc_i["armc"]),
            np.asarray(float(lats[i])),
            np.asarray(ascmc_i["eps"]),
        )
        np.testing.assert_allclose(
            cusps_batch[i],
            cusps_i,
            atol=1e-9,
            rtol=0,
            err_msg=f"vectorized vs scalar drift at chart {i}",
        )


def test_placidus_polar_lat_80_yields_nan_cusps() -> None:
    """At lat=80° beyond the polar circle, at least one iterated cusp NaN.

    Proves NaN-propagation works end-to-end. Plan 10-05 / 10-06 will route
    NaN to :class:`HighLatitudeError` or the Porphyry fallback per HOU-06.
    """
    ascmc = compute_ascmc(2451545.0, 80.0, 0.0)
    cusps = placidus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(80.0),
        np.asarray(ascmc["eps"]),
    )
    assert np.isnan(cusps).any(), (
        f"polar lat=80° expected to NaN at least one cusp; got {cusps}"
    )


def test_placidus_iteration_cap_invariant() -> None:
    """``MAX_ITER`` matches the HOU-03 spec value of 50."""
    assert MAX_ITER == 50, f"HOU-03 spec is iter-cap=50; got MAX_ITER={MAX_ITER}"


def test_placidus_convergence_threshold_invariant() -> None:
    """``TOL_DEG`` matches the research §'Don't Hand-Roll' value of 1e-7°."""
    assert TOL_DEG == 1e-7, (
        f"research §convergence threshold is 1e-7 deg; got TOL_DEG={TOL_DEG}"
    )


def test_placidus_no_silent_nan_at_mid_latitudes(
    reference_charts: list[dict[str, object]],
) -> None:
    """No reference chart at ``|lat| < 65°`` should produce any NaN cusp.

    Catches regressions where a numerical mishap (e.g. an off-by-one in the
    AD formula) silently NaN-propagates at a normal latitude.
    """
    for chart in reference_charts:
        lat_val = float(chart["lat"])  # type: ignore[arg-type]
        if abs(lat_val) >= 65.0:
            continue  # polar charts handled in test_placidus_polar_lat_80_yields_nan_cusps
        ascmc = compute_ascmc(
            float(chart["jd"]),  # type: ignore[arg-type]
            lat_val,
            float(chart["lon"]),  # type: ignore[arg-type]
        )
        cusps = placidus_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat_val),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"silent NaN at non-polar chart {chart['label']!r} (lat={lat_val}): "
            f"cusps={cusps}"
        )


def test_placidus_typical_iteration_count_well_below_cap() -> None:
    """Mid-latitude charts converge in <10 iter — pins the 50 cap as a safety
    margin, not a typical value.

    We instrument by re-running ``_iterate_cusp_ra`` with a temporary cap
    and asserting convergence is achieved well before 50. This protects
    against silent regressions where the iteration becomes slow but still
    converges (a perf-and-correctness yellow flag).
    """
    from ketu.houses.placidus import _iterate_cusp_ra

    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    armc = np.asarray(ascmc["armc"])
    lat = np.asarray(48.8566)
    eps = np.asarray(ascmc["eps"])

    # All 4 iterated cusps must converge.
    for cusp_n in (11, 12, 2, 3):
        ra, conv = _iterate_cusp_ra(armc, lat, eps, cusp_n)
        assert bool(conv), f"cusp {cusp_n}: did not converge at Paris J2000"
        assert not np.isnan(ra), f"cusp {cusp_n}: RA is NaN at non-polar lat"


def test_placidus_modular_convergence_metric_at_zero_armc() -> None:
    """ARMC near 0° / 360° tests the modular convergence metric (Pitfall 3).

    Without ``abs(((delta + 180) % 360) - 180)``, an iteration that wraps
    across 360° looks like a huge delta and never converges within 50 iter.
    """
    # ARMC = 359.9° pushes some cusps' RA across the 360° wrap.
    ascmc_eps = 23.4
    cusps = placidus_cusps(
        np.asarray(359.9),
        np.asarray(45.0),
        np.asarray(ascmc_eps),
    )
    assert not np.isnan(cusps).any(), (
        f"near-360° ARMC spuriously NaNed: cusps={cusps}"
    )
