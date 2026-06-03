"""CHIR-03 — Chiron accuracy regression: pinned Swiss-Ephemeris reference longitudes.

Nine (JD, expected_longitude) pairs are hardcoded from a one-time capture with
``tools/gen_chiron_coeffs.py --dump-refs`` (oracle: pyswisseph + seas_18.se1,
retflag=260, Moshier fallback, original 7 captured 2026-05-29, wing refs added
2026-06-03 for Phase 30-02).  No pyswisseph import at test time; the values are
frozen constants.

The tolerance ``TOLERANCE_DEG = 0.01°`` is 8.2× looser than the measured
``max|Δλ| = 0.001214°`` from the Phase 30-01 spike over 1900-2100 — more than
sufficient headroom while still guarding against regression.

The 9 dates span 1920-01-01 through 2080-01-01, covering the full embedded .npz
range (1900-01-01 through 2100-01-01): 7 core dates across the original 1950-2050
period plus 1920-01-01 (pre-1950 wing) and 2080-01-01 (post-2050 wing).

References
----------
CHIR-03 : accuracy-regression requirement (Phase 24 plan 04)
Phase 23 spike : Chebyshev seg=32d, degree=10, max|Δλ|=0.000861° (1950-2050)
Phase 30-01 spike : same params, max|Δλ|=0.001214° confirmed over 1900-2100
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.ephemeris.chiron import _load_chiron_data
from ketu.ephemeris.planets import calc_planet_position

# ---------------------------------------------------------------------------
# Pinned Swiss-Ephemeris reference longitudes for Chiron (body_id=13)
#
# Capture metadata
# ----------------
# - Command   : python tools/gen_chiron_coeffs.py --dump-refs
# - Dates     : 2026-05-29 (original 7); 2026-06-03 (wing refs 1920 + 2080)
# - Oracle    : pyswisseph + seas_18.se1 (path: kerykeion/sweph/)
# - retflag   : 260  (Moshier fallback; diff vs SWIEPH ≤ 0.000067° — negligible)
# - Tolerance : TOLERANCE_DEG = 0.01° (8.2× looser than measured 0.001214°)
#
# Each tuple is (julian_date, chiron_longitude_degrees) where the longitude
# is ecliptic longitude in degrees [0, 360).
# ---------------------------------------------------------------------------

_CHIRON_REFS: list[tuple[float, float]] = [
    (2422324.5,   2.609080),  # 1920-01-01  retflag=260  (pre-1950 wing)
    (2433282.5, 255.777223),  # 1950-01-01  retflag=260
    (2440587.5,   2.520351),  # 1970-01-01  retflag=260
    (2447892.5, 103.847482),  # 1990-01-01  retflag=260
    (2451545.0, 251.617624),  # J2000.0     retflag=260
    (2455197.5, 323.115304),  # 2010-01-01  retflag=260
    (2462501.5,  38.042056),  # 2030-01-01  retflag=260
    (2469807.5, 246.587706),  # 2050-01-01  retflag=260
    (2480764.5,  36.885249),  # 2080-01-01  retflag=260  (post-2050 wing)
]

#: Tolerance in degrees; spike-validated max|Δλ|=0.001214°, 8.2× under this.
TOLERANCE_DEG: float = 0.01


@pytest.mark.parametrize("jd, expected_lon", _CHIRON_REFS)
def test_chiron_longitude_within_tolerance(jd: float, expected_lon: float) -> None:
    """Chiron longitude from Chebyshev evaluator agrees with pyswisseph oracle within 0.01°.

    Calls :func:`ketu.ephemeris.planets.calc_planet_position` with ``planet_id=13``
    (Chiron, per ``BODY_INDICES``), retrieves the ecliptic longitude from index 0 of
    the returned array, and asserts the wrap-aware angular delta is strictly below
    ``TOLERANCE_DEG``.

    Parameters
    ----------
    jd : float
        Julian Date for the reference point (one of 9 spanning 1920-2080).
    expected_lon : float
        Chiron longitude captured from pyswisseph oracle (degrees, [0, 360)).

    Notes
    -----
    No pyswisseph or seas_18.se1 is accessed at test time — reference values
    are hardcoded constants.  The lru_cache on ``calc_planet_position`` is
    harmless here: all inputs are distinct JDs and the cache only accelerates
    repeated identical calls.

    CHIR-03 requirement: 9 pinned dates across 1920-2080, all within 0.01°.
    """
    pos = calc_planet_position(jd, 13)
    actual_lon = float(pos[0])

    delta = abs(actual_lon - expected_lon)
    if delta > 180.0:
        delta = 360.0 - delta

    assert delta < TOLERANCE_DEG, (
        f"Chiron longitude mismatch at JD={jd}: "
        f"expected={expected_lon:.6f}°, actual={actual_lon:.6f}°, "
        f"delta={delta:.6f}° >= tolerance={TOLERANCE_DEG}°"
    )


# ---------------------------------------------------------------------------
# Bounds + just-outside clamp tests (lock the 1900-2100 range contract)
# ---------------------------------------------------------------------------


def test_bounds_at_jd_start() -> None:
    """Chiron evaluator returns a finite longitude exactly at jd_start (1900-01-01).

    Notes
    -----
    jd_start = 2415020.5 is the lower bound of the embedded .npz.  The evaluator
    must return a valid, finite longitude with no exception and no NaN.  No
    pyswisseph access at test time.
    """
    data = _load_chiron_data()
    jd_start = float(data["jd_start"])

    from ketu.ephemeris.chiron import _eval_chiron_qty
    val = _eval_chiron_qty(
        jd_start,
        data["lon_coeffs"],
        data["seg_starts"],
        float(data["seg_len"]),
        float(data["jd_end"]),
    )
    lon = val % 360.0
    assert np.isfinite(lon), f"Expected finite longitude at jd_start, got {lon}"
    assert 0.0 <= lon < 360.0, f"lon={lon} not in [0, 360)"


def test_bounds_just_before_jd_start() -> None:
    """Chiron evaluator silently clamps JD just before jd_start — no exception.

    Notes
    -----
    A JD one day before jd_start (2415019.5) is out of range.  The silent-clamp
    contract requires a finite result (not a ValueError or NaN).
    """
    data = _load_chiron_data()
    jd_before = float(data["jd_start"]) - 1.0

    from ketu.ephemeris.chiron import _chiron_scalar
    result = _chiron_scalar(jd_before)
    assert len(result) == 6
    for v in result:
        assert np.isfinite(v), f"Expected finite value for clamped JD, got {v}"


def test_bounds_at_jd_end() -> None:
    """Chiron evaluator returns a finite longitude just inside jd_end (2100-01-01).

    Notes
    -----
    jd_end = 2488069.5 marks the end of the last segment.  A JD one day before
    jd_end is inside the last (possibly truncated) segment and must evaluate
    without error.
    """
    data = _load_chiron_data()
    jd_inside = float(data["jd_end"]) - 1.0

    from ketu.ephemeris.chiron import _eval_chiron_qty
    val = _eval_chiron_qty(
        jd_inside,
        data["lon_coeffs"],
        data["seg_starts"],
        float(data["seg_len"]),
        float(data["jd_end"]),
    )
    lon = val % 360.0
    assert np.isfinite(lon), f"Expected finite longitude just inside jd_end, got {lon}"
    assert 0.0 <= lon < 360.0, f"lon={lon} not in [0, 360)"


def test_bounds_just_after_jd_end() -> None:
    """Chiron evaluator silently clamps JD just after jd_end — no exception.

    Notes
    -----
    A JD one day after jd_end (2488070.5) is out of range.  The silent-clamp
    contract requires a finite result (not a ValueError or NaN).
    """
    data = _load_chiron_data()
    jd_after = float(data["jd_end"]) + 1.0

    from ketu.ephemeris.chiron import _chiron_scalar
    result = _chiron_scalar(jd_after)
    assert len(result) == 6
    for v in result:
        assert np.isfinite(v), f"Expected finite value for clamped JD, got {v}"
