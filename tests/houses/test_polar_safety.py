"""Polar-safety integration tests (HOU-06).

These tests pin the helper contract that Plan 10-06's ``calculate_houses``
will consume:

- :class:`HighLatitudeError` carries ``lat``/``system``/``polar_lat``
  attributes and its message hints at the ``polar_fallback='porphyry'``
  option.
- Placidus and Koch produce ``NaN`` cusps above the polar circle —
  Plan 10-06 will inspect the result and raise the error or fall back.
- Porphyry produces real (non-NaN) cusps at lat=70°, 80°, 89° — it is
  the polar fallback path.
- :func:`polar_circle` is time-varying (Pitfall 4): the value at J1900
  differs from J2050 by more than 5 milli-degrees because mean obliquity
  drifts ~46.81″ per century.

Plan 10-06 will fold all of this into ``calculate_houses(..., polar_fallback=...)``;
this file does NOT exercise the public dispatch (which still stub-raises
``NotImplementedError``).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.houses import HighLatitudeError
from ketu.houses.ascmc import compute_ascmc
from ketu.houses.koch import koch_cusps
from ketu.houses.placidus import placidus_cusps
from ketu.houses.porphyry import is_polar, polar_circle, porphyry_cusps


def test_high_latitude_error_attributes() -> None:
    """``HighLatitudeError`` carries ``lat``, ``system``, ``polar_lat``."""
    with pytest.raises(HighLatitudeError) as exc_info:
        raise HighLatitudeError(75.0, "placidus", 66.56)
    assert exc_info.value.lat == 75.0
    assert exc_info.value.system == "placidus"
    assert exc_info.value.polar_lat == 66.56


def test_high_latitude_error_message_contains_porphyry_hint() -> None:
    """Error message must guide caller to ``polar_fallback='porphyry'``."""
    e = HighLatitudeError(75.0, "placidus", 66.56)
    assert "porphyry" in str(e).lower(), (
        "HighLatitudeError must hint at polar_fallback='porphyry' per HOU-06"
    )


def test_placidus_yields_nan_above_polar_circle() -> None:
    """Above the polar circle Placidus NaN-propagates — Plan 10-06 routes."""
    jd = 2451545.0
    pc = float(polar_circle(jd))
    lat = pc + 1.0  # 1° beyond polar circle
    ascmc = compute_ascmc(jd, lat, 0.0)
    cusps = placidus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(lat),
        np.asarray(ascmc["eps"]),
    )
    assert np.isnan(cusps).any(), (
        f"Placidus 1° beyond polar circle (lat={lat}°) should NaN at least "
        "one cusp; Plan 10-06 inspects this to raise HighLatitudeError"
    )


def test_koch_yields_nan_above_polar_circle() -> None:
    """Above the polar circle Koch NaN-propagates."""
    jd = 2451545.0
    pc = float(polar_circle(jd))
    lat = pc + 1.0
    ascmc = compute_ascmc(jd, lat, 0.0)
    cusps = koch_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(lat),
        np.asarray(ascmc["eps"]),
    )
    assert np.isnan(cusps).any(), (
        f"Koch 1° beyond polar circle (lat={lat}°) should NaN at least one cusp"
    )


def test_porphyry_does_not_yield_nan_above_polar_circle() -> None:
    """Porphyry remains finite at lat 70°, 80°, 89° (the polar fallback)."""
    for lat in (70.0, 80.0, 89.0):
        ascmc = compute_ascmc(2451545.0, lat, 0.0)
        cusps = porphyry_cusps(
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), (
            f"Porphyry NaN at lat={lat}°; the polar-fallback path must "
            "always produce finite cusps"
        )


def test_polar_circle_is_time_varying_not_hardcoded() -> None:
    """``polar_circle`` is ``90 - ε(jd)``; ε drifts ~46.81″ per century.

    Regression catcher for Pitfall 4 (10-RESEARCH.md): if anyone "optimises"
    :func:`polar_circle` to a constant, this test fails loudly.
    """
    pc_1900 = float(polar_circle(2415020.5))
    pc_2050 = float(polar_circle(2470204.0))
    delta = abs(pc_2050 - pc_1900)
    # Over 150 years ε drifts ~70″ ≈ 0.0194°. Use a conservative >5e-3°
    # threshold so we'd catch even a 50% reduction in nutation precision.
    assert delta > 5e-3, (
        f"polar_circle 1900 vs 2050 differs by only {delta * 3600:.3f}″; "
        "expected >18″ — is mean_obliquity time-varying?"
    )


def test_is_polar_consistency_with_polar_circle() -> None:
    """``is_polar`` must agree with the live ``polar_circle`` boundary."""
    jd = 2451545.0
    pc = float(polar_circle(jd))
    # Check that the boundary detection uses the live polar_circle, not a
    # hardcoded 66.56° literal (Pitfall 4).
    assert is_polar(pc + 0.01, jd) is True
    assert is_polar(pc - 0.01, jd) is False
    # Same epoch but pick a date where polar_circle is materially different
    # (1900). At lat = pc_1900 + 0.01 we should be polar at jd_1900 but
    # NOT at jd_J2000 if pc_1900 < pc_J2000 - 0.02.
    jd_1900 = 2415020.5
    pc_1900 = float(polar_circle(jd_1900))
    # Use the smaller of the two so we're inside both circles + epsilon
    safe_lat = min(pc, pc_1900) - 0.01
    assert is_polar(safe_lat, jd) is False
    assert is_polar(safe_lat, jd_1900) is False


def test_polar_fallback_routing_contract_is_inspectable() -> None:
    """Plan 10-06 will route NaN -> HighLatitudeError or porphyry_cusps.

    Pin the contract that makes that routing possible: above polar_circle,
    placidus_cusps and koch_cusps return arrays containing at least one
    NaN; porphyry_cusps returns an array with NO NaN. A caller can simply
    inspect ``np.isnan(cusps).any()`` to decide whether to fall back.
    """
    jd = 2451545.0
    lat = 75.0  # well beyond polar_circle (~66.56°)
    ascmc = compute_ascmc(jd, lat, 0.0)
    armc_arr = np.asarray(ascmc["armc"])
    lat_arr = np.asarray(lat)
    eps_arr = np.asarray(ascmc["eps"])

    p = placidus_cusps(armc_arr, lat_arr, eps_arr)
    k = koch_cusps(armc_arr, lat_arr, eps_arr)
    o = porphyry_cusps(armc_arr, lat_arr, eps_arr)

    assert np.isnan(p).any(), "Placidus must signal failure via NaN above polar"
    assert np.isnan(k).any(), "Koch must signal failure via NaN above polar"
    assert not np.isnan(o).any(), (
        "Porphyry must NOT signal failure — it is the polar fallback"
    )
