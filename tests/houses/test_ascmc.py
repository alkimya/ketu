"""ASC/MC/ARMC/Vertex closed-form tests vs swisseph oracle.

Tolerance: <1 arcmin (1/60 deg ~= 0.01667 deg) per HOU-01 spec for ASC/MC/ARMC.
Vertex tolerance widened to 5 arcmin per Open Question 3 (advisory until
proven tight at all latitudes).

Tests using the snapshot fixture skip cleanly if swisseph is not installed —
the conftest.py at :mod:`tests.houses.conftest` does the
``pytest.importorskip("swisseph")`` gate.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_armc, compute_ascmc

ARCMIN_DEG: float = 1.0 / 60.0  # 0.01667 deg
ASC_MC_TOL: float = 1.0 * ARCMIN_DEG     # HOU-01 spec
VERTEX_TOL: float = 5.0 * ARCMIN_DEG     # Advisory (Open Question 3)

# Charts in reference_charts that have closed-form ASC/MC/ARMC/Vertex
# (i.e. non-polar — Placidus/Koch raise at lat=70/80, Porphyry remains
# finite but ASC/MC are system-independent so we exclude polar to avoid
# snapshot polar-fallback semantics). 8 entries.
NON_POLAR_LABELS = [
    "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
    "J2000_Tokyo", "J2000_BuenosAires", "J2000_Equator",
    "1900_NewYork", "2050_Reykjavik",
]

# Subset for advisory Vertex check (skip equator: tan(co-lat) ~= tan(90) → inf)
VERTEX_LABELS = [
    "J2000_Greenwich", "J2000_Paris", "J2000_Sydney",
    "1900_NewYork", "2050_Reykjavik",
]


def _circular_delta(a: float, b: float) -> float:
    """Modular distance on the circle, in degrees (Pitfall 3)."""
    return float(abs(((a - b + 180.0) % 360.0) - 180.0))


@pytest.mark.parametrize("label", NON_POLAR_LABELS)
def test_ascmc_matches_swisseph_within_arcmin(
    label: str,
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """All non-polar reference charts agree with swisseph oracle to <1 arcmin on ASC/MC/ARMC."""
    chart = next(c for c in reference_charts if c["label"] == label)
    snap = loaded_reference_snapshot["charts"][label]["systems"]["placidus"]

    # ASC and MC are system-independent (the hour-angle / meridian intersection
    # of the ecliptic) — any system in the snapshot has the same ASC/MC.
    result = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])

    asc_delta = _circular_delta(float(result["asc"]), snap["asc"])
    mc_delta = _circular_delta(float(result["mc"]), snap["mc"])
    armc_delta = _circular_delta(float(result["armc"]), snap["armc"])

    assert asc_delta < ASC_MC_TOL, (
        f"{label}: ASC drift {asc_delta * 60:.3f} arcmin "
        f"> {ASC_MC_TOL * 60:.0f} arcmin"
    )
    assert mc_delta < ASC_MC_TOL, (
        f"{label}: MC drift {mc_delta * 60:.3f} arcmin "
        f"> {ASC_MC_TOL * 60:.0f} arcmin"
    )
    assert armc_delta < ASC_MC_TOL, (
        f"{label}: ARMC drift {armc_delta * 60:.3f} arcmin "
        f"> {ASC_MC_TOL * 60:.0f} arcmin"
    )


@pytest.mark.parametrize("label", VERTEX_LABELS)
def test_vertex_matches_swisseph_within_5_arcmin(
    label: str,
    reference_charts: list[dict[str, Any]],
    loaded_reference_snapshot: dict[str, Any],
) -> None:
    """Vertex agreement is advisory per Open Question 3 — log actual delta."""
    chart = next(c for c in reference_charts if c["label"] == label)
    snap = loaded_reference_snapshot["charts"][label]["systems"]["placidus"]
    result = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
    vtx_delta = _circular_delta(float(result["vertex"]), snap["vertex"])
    assert vtx_delta < VERTEX_TOL, (
        f"{label}: Vertex drift {vtx_delta * 60:.3f} arcmin "
        f"> {VERTEX_TOL * 60:.0f} arcmin "
        "(may indicate co-latitude formula needs sign correction; see "
        "10-RESEARCH.md Open Question 3)"
    )


def test_compute_ascmc_vectorized_preserves_leading_shape() -> None:
    """ndarray inputs return ndarray outputs of broadcast shape (3,)."""
    jds = np.array([2451545.0, 2470204.0, 2415020.5])
    lats = np.array([48.8566, 64.1466, 40.7128])
    lons = np.array([2.3522, -21.9426, -74.0060])
    result = compute_ascmc(jds, lats, lons)
    for key in ("asc", "mc", "armc", "vertex", "eps"):
        assert result[key].shape == (3,), f"{key} lost leading shape"


def test_compute_ascmc_scalar_returns_zero_d_arrays() -> None:
    """Scalar inputs return 0-d ndarrays (consistent broadcast behavior)."""
    result = compute_ascmc(2451545.0, 48.8566, 2.3522)
    for key in ("asc", "mc", "armc", "vertex", "eps"):
        assert result[key].shape == (), f"{key} not 0-d, got shape {result[key].shape}"


def test_compute_armc_equals_sidereal_time_plus_longitude() -> None:
    """ARMC identity: armc(jd, lon) == (sidereal_time(jd, 0) + lon) mod 360 (Pitfall 5)."""
    from ketu.ephemeris.time import sidereal_time
    jd = 2451545.0
    lon = 45.0
    armc = compute_armc(jd, lon)
    expected = (sidereal_time(jd, 0.0) + lon) % 360.0
    assert abs(float(armc) - expected) < 1e-9, (
        "compute_armc must equal sidereal_time(jd, 0) + lon; if you changed "
        "the formula, check Pitfall 5 in 10-RESEARCH.md"
    )


def test_paris_j2000_asc_in_research_sanity_band() -> None:
    """Empirical sanity: at J2000, lat=48.8566, lon=2.3522, ASC ~= 26.77 deg."""
    result = compute_ascmc(2451545.0, 48.8566, 2.3522)
    asc = float(result["asc"])
    assert 25.0 <= asc <= 28.0, (
        f"Paris J2000 ASC {asc:.4f} outside sanity band [25, 28]; "
        "formula or units regression suspected"
    )
