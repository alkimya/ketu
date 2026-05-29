"""
Unit tests for ketu.ephemeris.chiron — pure-NumPy Chiron evaluator.

Covers:
  - Loader shapes and metadata
  - Scalar 6-tuple output
  - Vec/scalar consistency (including aberration branch)
  - Out-of-range JD clamp (both directions)
  - AGPL ratchet: no swisseph import in chiron.py
"""

from __future__ import annotations

import importlib
import inspect
from unittest.mock import patch

import numpy as np
import pytest

from ketu.ephemeris.chiron import (
    _chiron_scalar,
    _chiron_vec,
    _eval_chiron_qty,
    _load_chiron_data,
)
from ketu.ephemeris.coordinates import aberration_correction

# J2000.0 — reference JD used throughout the spike and 24-01
_J2000 = 2451545.0


# ---------------------------------------------------------------------------
# Test 1 — loader shapes and metadata
# ---------------------------------------------------------------------------


def test_load_chiron_data_shapes() -> None:
    """_load_chiron_data returns dict with expected shapes and scalar values.

    Notes
    -----
    Confirms .npz wiring: 1142 segments, degree 10 (11 coefficients per seg),
    seg_len = 32.0 days, and the three coefficient arrays have shape (1142, 11).
    """
    data = _load_chiron_data()

    assert "lon_coeffs" in data
    assert "lat_coeffs" in data
    assert "dist_coeffs" in data
    assert "seg_starts" in data
    assert "seg_len" in data
    assert "degree" in data

    assert data["lon_coeffs"].shape == (1142, 11)
    assert data["lat_coeffs"].shape == (1142, 11)
    assert data["dist_coeffs"].shape == (1142, 11)
    assert data["seg_starts"].shape == (1142,)

    assert float(data["seg_len"]) == 32.0
    assert int(data["degree"]) == 10


# ---------------------------------------------------------------------------
# Test 2 — scalar output: 6 finite floats, range checks
# ---------------------------------------------------------------------------


def test_chiron_scalar_returns_6tuple() -> None:
    """_chiron_scalar(J2000) returns 6 finite floats with correct physical ranges.

    Notes
    -----
    - lon in [0, 360)
    - dist > 0 (geocentric distance in AU; Chiron ~8-19 AU)
    - lon_speed ≥ 0 for most of Chiron's orbit (slow prograde or retrograde)
    """
    result = _chiron_scalar(_J2000)

    assert len(result) == 6, "Should return a 6-element tuple"

    lon, lat, dist, lon_speed, lat_speed, dist_speed = result

    # All must be finite (no NaN/Inf)
    for i, v in enumerate(result):
        assert np.isfinite(v), f"Component {i} is not finite: {v}"

    # Longitude in [0, 360)
    assert 0.0 <= lon < 360.0, f"lon={lon} not in [0, 360)"

    # Distance must be positive (Chiron orbits between ~8 and ~19 AU)
    assert dist > 0.0, f"dist={dist} not positive"

    # Speed magnitude reasonable (Chiron ≈ 0.019°/day mean, retrograde possible)
    assert abs(lon_speed) < 1.0, f"lon_speed={lon_speed} seems unreasonable (> 1°/day)"


# ---------------------------------------------------------------------------
# Test 2b — dlon wrap correction branches
# ---------------------------------------------------------------------------


def test_chiron_scalar_dlon_wrap_corrections() -> None:
    """Both 360°-wrap correction branches in _chiron_scalar are reachable.

    Notes
    -----
    In natural 1950-2050 data, Chiron moves at most ~0.019°/day, so the
    ``if dlon > 180`` or ``if dlon < -180`` branches are only triggered when
    the raw longitude straddles 0°/360° within a 0.01-day window.

    ``dlon > 180`` (line 162): lon ≈ 0° and lon1 ≈ 360° (retrograde crossing).
    ``dlon < -180`` (line 164): lon ≈ 360° and lon1 ≈ 0° (prograde crossing).

    We use ``_eval_chiron_qty`` mock calls to produce synthetic values that
    exercise both branches without depending on specific calendar events.
    """
    import ketu.ephemeris.chiron as _chiron_mod

    # Branch 1: dlon > 180  — lon=359.9°, lon1=0.1° → dlon = 0.1-359.9 = -359.8 (< -180)
    #                          BUT after % 360: lon=359.9, lon1=0.1; dlon=0.1-359.9=-359.8 → += 360 → 0.2
    # Actually the correction fires when dlon < -180 here.
    # Let us instead construct the > 180 case:
    #   lon ≈ 0.001, lon1 = raw_next % 360 ≈ 359.999  → dlon = 359.999 - 0.001 = 359.998 > 180
    # This matches the natural crossing found at JD≈2458387.5.

    call_count = [0]
    # 6 calls per _chiron_scalar invocation (3 quantities × 2 JDs)
    # Order: lon@jd, lat@jd, dist@jd, lon@jd+delta, lat@jd+delta, dist@jd+delta

    def _mock_eval(jd: float, coeffs: np.ndarray,
                   seg_starts: np.ndarray, seg_len: float,
                   jd_end: float) -> float:
        call_count[0] += 1
        idx = call_count[0]
        # 1st call: lon at jd — near 0°
        # 4th call: lon at jd+delta — near 360° (raw, before % 360)
        if idx == 1:
            return 0.001          # lon = 0.001 % 360 = 0.001
        if idx == 4:
            return 359.999        # lon1 = 359.999 % 360 = 359.999; dlon=359.998>180 → -=360 → -0.002
        return 10.0               # lat/dist — arbitrary finite value

    with patch.object(_chiron_mod, "_eval_chiron_qty", side_effect=_mock_eval):
        result = _chiron_scalar(2451545.0)

    assert len(result) == 6
    lon, _lat, _dist, lon_speed, _ls, _ds = result
    # lon_speed should be negative (retrograde) after the wrap correction
    assert lon_speed < 0.0, f"Expected negative speed for retrograde crossing, got {lon_speed}"

    # Branch 2: dlon < -180  — lon≈359.999°, lon1≈0.001° → raw dlon = 0.001-359.999 = -359.998 < -180
    call_count[0] = 0

    def _mock_eval_prograde(jd: float, coeffs: np.ndarray,
                             seg_starts: np.ndarray, seg_len: float,
                             jd_end: float) -> float:
        call_count[0] += 1
        idx = call_count[0]
        if idx == 1:
            return 359.999        # lon = 359.999 % 360 = 359.999
        if idx == 4:
            return 360.001        # lon1 = 360.001 % 360 = 0.001; dlon=-359.998<-180 → +=360 → 0.002
        return 10.0

    with patch.object(_chiron_mod, "_eval_chiron_qty", side_effect=_mock_eval_prograde):
        result2 = _chiron_scalar(2451545.0)

    assert len(result2) == 6
    _lon2, _lat2, _dist2, lon_speed2, _ls2, _ds2 = result2
    # lon_speed should be positive (prograde) after the wrap correction
    assert lon_speed2 > 0.0, f"Expected positive speed for prograde crossing, got {lon_speed2}"


# ---------------------------------------------------------------------------
# Test 3 — vec/scalar consistency (exercises aberration branch)
# ---------------------------------------------------------------------------


def test_chiron_vec_matches_scalar() -> None:
    """_chiron_vec output matches aberration-applied _chiron_scalar values.

    Notes
    -----
    _chiron_vec applies aberration internally (like _make_planet_vec).  This
    test builds the expected values by calling _chiron_scalar and manually
    applying aberration, then asserts np.allclose against _chiron_vec.

    This exercises the aberration loop (the per-element dlon/dlat correction)
    inside _chiron_vec.
    """
    jds = np.array([_J2000, _J2000 + 365.25, _J2000 - 365.25])

    # Build expected: scalar + aberration
    expected = np.zeros((len(jds), 6))
    for i, jd in enumerate(jds):
        r = _chiron_scalar(float(jd))
        lon, lat = r[0], r[1]
        dlon, dlat = aberration_correction(lon, lat, float(jd))
        expected[i, 0] = lon + dlon
        expected[i, 1] = lat + dlat
        expected[i, 2] = r[2]
        expected[i, 3] = r[3]
        expected[i, 4] = r[4]
        expected[i, 5] = r[5]

    lons, lats, dists, lspeeds, bspeeds, dspeeds = _chiron_vec(jds)

    assert np.allclose(lons, expected[:, 0], atol=1e-12), "lon mismatch after aberration"
    assert np.allclose(lats, expected[:, 1], atol=1e-12), "lat mismatch after aberration"
    assert np.allclose(dists, expected[:, 2], atol=1e-12), "dist mismatch"
    assert np.allclose(lspeeds, expected[:, 3], atol=1e-12), "lon_speed mismatch"
    assert np.allclose(bspeeds, expected[:, 4], atol=1e-12), "lat_speed mismatch"
    assert np.allclose(dspeeds, expected[:, 5], atol=1e-12), "dist_speed mismatch"


# ---------------------------------------------------------------------------
# Test 4 — clamp below range (si clamped to 0)
# ---------------------------------------------------------------------------


def test_clamp_below_range() -> None:
    """_eval_chiron_qty with JD before 1950 clamps si to 0 — must not raise.

    Notes
    -----
    Covers the ``max(0, ...)`` branch in _eval_chiron_qty.  A JD far before
    the first segment start forces ``si < 0`` which is clamped to 0.
    """
    data = _load_chiron_data()
    seg_starts: np.ndarray = data["seg_starts"]
    seg_len = float(data["seg_len"])

    # JD well before 1950 (1000 days before first segment)
    jd_early = float(seg_starts[0]) - 1000.0

    # Should not raise, should return a finite float
    val = _eval_chiron_qty(
        jd_early, data["lon_coeffs"], seg_starts, seg_len, float(data["jd_end"])
    )
    assert np.isfinite(val), f"Expected finite value, got {val}"

    # Also verify via _chiron_scalar (exercises full clamp path)
    result = _chiron_scalar(jd_early)
    assert len(result) == 6
    for v in result:
        assert np.isfinite(v), f"Expected finite value for out-of-range JD, got {v}"


# ---------------------------------------------------------------------------
# Test 5 — clamp above range (si clamped to len-1)
# ---------------------------------------------------------------------------


def test_clamp_above_range() -> None:
    """_eval_chiron_qty with JD after 2050 clamps si to n_segs-1 — must not raise.

    Notes
    -----
    Covers the ``min(si, len(seg_starts)-1)`` branch in _eval_chiron_qty.
    A JD far past the last segment forces ``si >= n_segs`` which is clamped
    to the last valid index.
    """
    data = _load_chiron_data()
    seg_starts: np.ndarray = data["seg_starts"]
    seg_len = float(data["seg_len"])

    # JD well after 2050 (1000 days after last segment + its length)
    jd_late = float(seg_starts[-1]) + seg_len + 1000.0

    # Should not raise, should return a finite float
    val = _eval_chiron_qty(
        jd_late, data["lon_coeffs"], seg_starts, seg_len, float(data["jd_end"])
    )
    assert np.isfinite(val), f"Expected finite value, got {val}"

    # Also verify via _chiron_scalar
    result = _chiron_scalar(jd_late)
    assert len(result) == 6
    for v in result:
        assert np.isfinite(v), f"Expected finite value for out-of-range JD, got {v}"


# ---------------------------------------------------------------------------
# Test 6 — AGPL ratchet: no swisseph import in chiron.py
# ---------------------------------------------------------------------------


def test_no_swisseph_import() -> None:
    """chiron.py must not have any swisseph import statement — AGPL ratchet.

    Notes
    -----
    Reinforces the project-level ``test_no_runtime_swisseph_import`` for this
    specific new module.  Only checks import-statement lines (those starting
    with ``import`` or ``from``) to avoid false positives from docstrings that
    mention ``pyswisseph`` as a documentation reference.
    """
    import ketu.ephemeris.chiron as chiron_mod

    source = inspect.getsource(chiron_mod)
    import_lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    for line in import_lines:
        assert "swisseph" not in line, (
            f"chiron.py import line contains swisseph — AGPL ratchet violated: {line!r}"
        )
