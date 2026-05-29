"""CHIR-03 — Chiron accuracy regression: pinned Swiss-Ephemeris reference longitudes.

Seven (JD, expected_longitude) pairs are hardcoded from a one-time capture with
``tools/gen_chiron_coeffs.py --dump-refs`` (oracle: pyswisseph + seas_18.se1,
retflag=260, Moshier fallback, captured 2026-05-29).  No pyswisseph import at
test time; the values are frozen constants.

The tolerance ``TOLERANCE_DEG = 0.01°`` is 11.6× looser than the measured
``max|Δλ| = 0.000861°`` from the Phase 23 spike — more than sufficient headroom
while still guarding against regression.

The 7 dates are spaced ~10-20 years apart across Chiron's ~50.7 yr orbital
period (1950-01-01 through 2050-01-01), covering the full embedded .npz range.

References
----------
CHIR-03 : accuracy-regression requirement (Phase 24 plan 04)
Phase 23 spike : Chebyshev seg=32d, degree=10, max|Δλ|=0.000861° confirmed
"""
from __future__ import annotations

import pytest

from ketu.ephemeris.planets import calc_planet_position

# ---------------------------------------------------------------------------
# Pinned Swiss-Ephemeris reference longitudes for Chiron (body_id=13)
#
# Capture metadata
# ----------------
# - Command   : python tools/gen_chiron_coeffs.py --dump-refs
# - Date      : 2026-05-29
# - Oracle    : pyswisseph + seas_18.se1 (path: kerykeion/sweph/)
# - retflag   : 260  (Moshier fallback; diff vs SWIEPH ≤ 0.000067° — negligible)
# - Tolerance : TOLERANCE_DEG = 0.01° (11.6× looser than measured 0.000861°)
#
# Each tuple is (julian_date, chiron_longitude_degrees) where the longitude
# is ecliptic longitude in degrees [0, 360).
# ---------------------------------------------------------------------------

_CHIRON_REFS: list[tuple[float, float]] = [
    (2433282.5, 255.777223),  # 1950-01-01  retflag=260
    (2440587.5,   2.520351),  # 1970-01-01  retflag=260
    (2447892.5, 103.847482),  # 1990-01-01  retflag=260
    (2451545.0, 251.617624),  # J2000.0     retflag=260
    (2455197.5, 323.115304),  # 2010-01-01  retflag=260
    (2462501.5,  38.042056),  # 2030-01-01  retflag=260
    (2469807.5, 246.587706),  # 2050-01-01  retflag=260
]

#: Tolerance in degrees; spike-validated max|Δλ|=0.000861°, 11.6× under this.
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
        Julian Date for the reference point (one of 7 spanning 1950-2050).
    expected_lon : float
        Chiron longitude captured from pyswisseph oracle (degrees, [0, 360)).

    Notes
    -----
    No pyswisseph or seas_18.se1 is accessed at test time — reference values
    are hardcoded constants.  The lru_cache on ``calc_planet_position`` is
    harmless here: all inputs are distinct JDs and the cache only accelerates
    repeated identical calls.

    CHIR-03 requirement: 7 pinned dates across 1950-2050, all within 0.01°.
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
