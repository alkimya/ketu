"""Porphyry tests — closed-form trisection invariants and polar correctness."""
from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from ketu.houses.ascmc import compute_ascmc
from ketu.houses.porphyry import (
    POLAR_EPS_TOL,
    is_polar,
    polar_circle,
    porphyry_cusps,
)


def test_porphyry_works_at_extreme_polar_lat() -> None:
    """Porphyry at lat=89° must NOT NaN — it is the polar fallback."""
    ascmc = compute_ascmc(2451545.0, 89.0, 0.0)
    cusps = porphyry_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(89.0),
        np.asarray(ascmc["eps"]),
    )
    assert not np.isnan(cusps).any(), (
        f"Porphyry must work at lat=89°; got cusps={cusps}"
    )


def test_porphyry_works_at_polar_lats_70_80() -> None:
    """Porphyry at lat 70°, 80° remains finite (the polar fallback)."""
    for lat in (70.0, 80.0):
        ascmc = compute_ascmc(2451545.0, lat, 0.0)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"Porphyry NaN at lat={lat}°; the polar-fallback path requires "
            "finite cusps at all latitudes"
        )


def test_porphyry_trisection_invariant_upper_arc() -> None:
    """Cusps 11, 12 evenly trisect the (MC, ASC) short arc."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = porphyry_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    # Cusp ordering: [asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]
    mc, asc = float(cusps[9]), float(cusps[0])
    c11, c12 = float(cusps[10]), float(cusps[11])
    upper_arc = (asc - mc) % 360.0
    assert abs(((c11 - mc) % 360.0) - upper_arc / 3.0) < 1e-9
    assert abs(((c12 - mc) % 360.0) - 2.0 * upper_arc / 3.0) < 1e-9


def test_porphyry_trisection_invariant_lower_arc() -> None:
    """Cusps 2, 3 evenly trisect the (ASC, IC) short arc."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = porphyry_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    ic, asc = float(cusps[3]), float(cusps[0])
    c2, c3 = float(cusps[1]), float(cusps[2])
    lower_arc = (ic - asc) % 360.0
    assert abs(((c2 - asc) % 360.0) - lower_arc / 3.0) < 1e-9
    assert abs(((c3 - asc) % 360.0) - 2.0 * lower_arc / 3.0) < 1e-9


def test_porphyry_cusps_5_6_8_9_are_opposites_of_11_12_2_3() -> None:
    """Cusps 5/6/8/9 = (cusps 11/12/2/3 + 180) mod 360."""
    ascmc = compute_ascmc(2451545.0, 48.8566, 2.3522)
    cusps = porphyry_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(48.8566),
        np.asarray(ascmc["eps"]),
    )
    pairs = [(4, 10), (5, 11), (7, 1), (8, 2)]
    for derived_idx, source_idx in pairs:
        expected = (cusps[source_idx] + 180.0) % 360.0
        delta = abs(((cusps[derived_idx] - expected + 180.0) % 360.0) - 180.0)
        assert delta < 1e-9, (
            f"cusp {derived_idx + 1} not the opposite of cusp {source_idx + 1}"
        )


def test_porphyry_algorithm_matches_oracle_armc_at_all_latitudes(
    reference_charts: list[dict[str, Any]],
) -> None:
    """Bit-exact match vs swe_oracle_armc on all reference charts.

    Porphyry's closed-form mirrors swisseph's ``swehouse.c`` case ``'O'``
    including the polar ASC swap (when ``acmc < 0`` ASC is reflected by
    180°). Once we feed the same (ARMC, lat, eps), we expect machine
    precision.
    """
    from tests.houses.conftest import swe_oracle_armc

    for chart in reference_charts:
        ascmc = compute_ascmc(
            float(chart["jd"]),
            float(chart["lat"]),
            float(chart["lon"]),
        )
        armc = float(ascmc["armc"])
        eps = float(ascmc["eps"])
        lat = float(chart["lat"])

        cusps = porphyry_cusps(
            np.asarray(armc),
            np.asarray(lat),
            np.asarray(eps),
        )
        oracle = swe_oracle_armc(armc, lat, eps, "porphyry")
        assert "polar" not in oracle, (
            f"{chart['label']}: oracle returned polar error: "
            f"{oracle.get('error')}"
        )
        deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
        assert deltas.max() < 1e-6, (
            f"{chart['label']}: Porphyry algorithm drift {deltas.max() * 3600:.6f}\""
        )


def test_polar_circle_at_j2000_is_in_expected_range() -> None:
    """``polar_circle = 90 - ε(jd)``; at J2000 ε ≈ 23.44° → polar ≈ 66.56°."""
    pc = float(polar_circle(2451545.0))
    assert 66.4 < pc < 66.7, (
        f"polar_circle at J2000 = {pc}; expected ~66.56 (90 - ε_mean)"
    )


def test_is_polar_at_boundary() -> None:
    """``lat`` just above polar circle → True; just below → False."""
    pc = float(polar_circle(2451545.0))
    assert is_polar(pc + 0.1, 2451545.0) is True
    assert is_polar(pc - 0.1, 2451545.0) is False
    # Negative lats: same magnitude rule
    assert is_polar(-(pc + 0.1), 2451545.0) is True
    assert is_polar(-(pc - 0.1), 2451545.0) is False


def test_is_polar_vectorized() -> None:
    """``is_polar`` over an ndarray of latitudes returns bool ndarray."""
    lats = np.array([0.0, 45.0, 67.0, 80.0, -67.0])
    result = is_polar(lats, 2451545.0)
    assert isinstance(result, np.ndarray)
    assert result.tolist() == [False, False, True, True, True]


def test_polar_eps_tol_documented() -> None:
    """``POLAR_EPS_TOL == 1e-9`` per research §Open Question 4."""
    assert POLAR_EPS_TOL == 1e-9


def test_porphyry_registered_in_systems() -> None:
    """``@register('porphyry')`` populates the SYSTEMS registry."""
    from ketu.houses.registry import SYSTEMS, get_system
    assert "porphyry" in SYSTEMS
    assert get_system("porphyry") is porphyry_cusps
    assert get_system("PORPHYRY") is porphyry_cusps  # case-insensitive


def test_porphyry_vectorized_matches_scalar_per_element() -> None:
    """Batched arrays produce per-element-equal results."""
    jds = np.array([2451545.0, 2470204.0, 2415020.5])
    lats = np.array([48.8566, 64.1466, 40.7128])
    lons = np.array([2.3522, -21.9426, -74.0060])
    ascmc_b = compute_ascmc(jds, lats, lons)
    cusps_b = porphyry_cusps(ascmc_b["armc"], lats, ascmc_b["eps"])

    for i in range(3):
        ai = compute_ascmc(float(jds[i]), float(lats[i]), float(lons[i]))
        ci = porphyry_cusps(
            np.asarray(ai["armc"]),
            np.asarray(float(lats[i])),
            np.asarray(ai["eps"]),
        )
        np.testing.assert_allclose(cusps_b[i], ci, atol=1e-9, rtol=0)
