"""
Integration smoke tests for CHIR-05: Chiron participates in the full
chart / aspect / cycle machinery with no special-casing.

Covers:
  - compute_chart includes Chiron at index 13 in body_lons/body_lats/body_speeds
  - aspect_matrix has shape (14, 14) with Chiron row/column active
  - generate_cycle_series works with a Sun-Chiron pair (CYCLE_DTYPE result)
  - calculate_all_positions returns 14 bodies, Chiron at dict key "Chiron"

These tests are behaviour-focused: they assert that Chiron flows through
each subsystem identically to any other body (no special-casing).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from ketu.charts import compute_chart
from ketu.cycles import generate_cycle_series, CYCLE_DTYPE
from ketu.ephemeris.planets import calc_planet_position, calculate_all_positions

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

#: J2000.0 — standard reference epoch used throughout the Chiron phase.
_J2000 = 2451545.0

#: Chiron body index in the 14-body axis (CHIR-03 / D-08 ratchet).
_CHIRON_IDX = 13

#: Expected lon for Chiron at J2000.0 (from oracle; tolerance 0.01° per spike).
_CHIRON_J2000_LON = 251.617624  # oracle pyswisseph retflag=260 reference

#: Tolerance: spike-validated max|Δλ|=0.000861° → use 0.01° budget.
_TOL_DEG = 0.01


# ---------------------------------------------------------------------------
# Test 1 — compute_chart includes Chiron at index 13
# ---------------------------------------------------------------------------


def test_compute_chart_includes_chiron() -> None:
    """compute_chart body_lons has 14 bodies; Chiron at index 13 is valid.

    Notes
    -----
    Asserts:
    - ``body_lons.shape[-1] == 14`` (D-08 ratchet: 14-body axis).
    - ``body_lats.shape[-1] == 14`` and ``body_speeds.shape[-1] == 14``.
    - Chiron longitude at index 13 is finite and in ``[0, 360)``.
    - Chiron longitude matches ``calc_planet_position(jd, 13)[0]`` within
      the spike-validated 0.01° budget.
    - Chiron longitude is within 0.01° of the J2000 oracle reference.
    """
    chart = compute_chart(_J2000, 48.86, 2.35)

    # Shape assertions — 14-body axis (D-08)
    assert chart["body_lons"].shape == (14,), (
        f"Expected body_lons.shape == (14,), got {chart['body_lons'].shape}"
    )
    assert chart["body_lats"].shape == (14,)
    assert chart["body_speeds"].shape == (14,)

    # Chiron index 13: finite and in [0, 360)
    chiron_lon = float(chart["body_lons"][_CHIRON_IDX])
    assert np.isfinite(chiron_lon), f"Chiron lon is not finite: {chiron_lon}"
    assert 0.0 <= chiron_lon < 360.0, (
        f"Chiron lon out of [0, 360): {chiron_lon}"
    )

    # Consistency: matches calc_planet_position(jd, 13) within fp64 round-off
    pos13 = calc_planet_position(_J2000, _CHIRON_IDX)
    assert abs(chiron_lon - pos13[0]) < 1e-9, (
        f"body_lons[13]={chiron_lon} disagrees with calc_planet_position(jd,13)={pos13[0]}"
    )

    # Accuracy: within 0.01° of the oracle reference
    assert abs(chiron_lon - _CHIRON_J2000_LON) < _TOL_DEG, (
        f"Chiron J2000 lon {chiron_lon:.6f}° deviates from oracle "
        f"{_CHIRON_J2000_LON:.6f}° by {abs(chiron_lon - _CHIRON_J2000_LON):.6f}°"
    )


# ---------------------------------------------------------------------------
# Test 2 — aspect_matrix shape (14, 14) with Chiron row active
# ---------------------------------------------------------------------------


def test_aspect_matrix_covers_chiron() -> None:
    """aspect_matrix has shape (14, 14); Chiron row/column participates.

    Notes
    -----
    Asserts:
    - ``aspect_matrix.shape == (14, 14)`` — (D-08 ratchet).
    - ``aspect_orbs.shape == (14, 14)``.
    - Diagonal stays at sentinel ``-1`` (D-06: a body has no aspect with itself).
    - Chiron row at index 13 is populated (at least one cell != ``-1``),
      proving Chiron participates without special-casing.
    - Symmetry: ``matrix[i, j] == matrix[j, i]`` for Chiron column (D-17).
    """
    chart = compute_chart(_J2000, 48.86, 2.35)
    asp = chart["aspect_matrix"]
    orbs = chart["aspect_orbs"]

    # Shape: 14×14
    assert asp.shape == (14, 14), f"aspect_matrix.shape={asp.shape}, expected (14, 14)"
    assert orbs.shape == (14, 14), f"aspect_orbs.shape={orbs.shape}, expected (14, 14)"

    # Diagonal sentinel: -1 for aspect_matrix (D-06)
    diag_asp = np.diag(asp)
    assert np.all(diag_asp == -1), (
        f"Diagonal of aspect_matrix contains non-sentinel values: {diag_asp}"
    )

    # Diagonal NaN for aspect_orbs (D-06)
    diag_orbs = np.diag(orbs)
    assert np.all(np.isnan(diag_orbs)), (
        f"Diagonal of aspect_orbs contains non-NaN values: {diag_orbs}"
    )

    # Chiron row (index 13): at least one off-diagonal cell != -1
    chiron_row = asp[_CHIRON_IDX, :]
    off_diag_mask = np.ones(14, dtype=bool)
    off_diag_mask[_CHIRON_IDX] = False  # exclude diagonal
    assert np.any(chiron_row[off_diag_mask] != -1), (
        "Chiron row is all -1 (no aspects computed for Chiron at J2000)"
    )

    # Symmetry: matrix[13, j] == matrix[j, 13] (D-17)
    assert np.array_equal(asp[_CHIRON_IDX, :], asp[:, _CHIRON_IDX]), (
        "aspect_matrix is not symmetric for Chiron row/column (D-17 violation)"
    )
    # Symmetry for orbs (NaN == NaN via array_equal is ok here, we want structural equality)
    orb_row = orbs[_CHIRON_IDX, :]
    orb_col = orbs[:, _CHIRON_IDX]
    # Compare non-NaN entries
    non_nan_row = ~np.isnan(orb_row)
    non_nan_col = ~np.isnan(orb_col)
    assert np.array_equal(non_nan_row, non_nan_col), (
        "aspect_orbs NaN structure not symmetric for Chiron"
    )
    if np.any(non_nan_row):
        np.testing.assert_allclose(
            orb_row[non_nan_row], orb_col[non_nan_row], atol=1e-5,
            err_msg="aspect_orbs values not symmetric for Chiron (D-17)",
        )


# ---------------------------------------------------------------------------
# Test 3 — generate_cycle_series with Sun-Chiron pair
# ---------------------------------------------------------------------------


def test_cycle_series_with_chiron() -> None:
    """generate_cycle_series('Sun', 'Chiron', timestamps) returns valid CYCLE_DTYPE array.

    Notes
    -----
    Asserts:
    - Return dtype == ``CYCLE_DTYPE``.
    - ``body2_id == 13`` (Chiron ID in the 14-body table).
    - ``angular_separation`` is finite and in ``[0, 360]``.
    - ``cycle_progress`` is finite and in ``[0, 1]``.
    - No special-casing: Chiron is resolved by name, same code path as any body.
    """
    # 30 daily timestamps starting 2025-01-01
    timestamps = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(30)]
    cycles = generate_cycle_series("Sun", "Chiron", timestamps)

    # Return type and shape
    assert cycles.dtype == CYCLE_DTYPE, (
        f"generate_cycle_series returned dtype={cycles.dtype}, expected CYCLE_DTYPE"
    )
    assert cycles.shape == (30,), f"Expected shape (30,), got {cycles.shape}"

    # Body IDs: Sun=0, Chiron=13
    assert int(cycles["body1_id"][0]) == 0, (
        f"body1_id={cycles['body1_id'][0]}, expected 0 (Sun)"
    )
    assert int(cycles["body2_id"][0]) == _CHIRON_IDX, (
        f"body2_id={cycles['body2_id'][0]}, expected 13 (Chiron)"
    )

    # angular_separation: finite and in [0, 360]
    sep = cycles["angular_separation"]
    assert np.all(np.isfinite(sep)), "angular_separation contains non-finite values"
    assert np.all((sep >= 0.0) & (sep <= 360.0)), (
        f"angular_separation out of [0,360]: min={sep.min():.3f}, max={sep.max():.3f}"
    )

    # cycle_progress: finite and in [0, 1]
    prog = cycles["cycle_progress"]
    assert np.all(np.isfinite(prog)), "cycle_progress contains non-finite values"
    assert np.all((prog >= 0.0) & (prog <= 1.0)), (
        f"cycle_progress out of [0,1]: min={prog.min():.4f}, max={prog.max():.4f}"
    )


# ---------------------------------------------------------------------------
# Test 4 — calculate_all_positions has 14 bodies with Chiron at key "Chiron"
# ---------------------------------------------------------------------------


def test_calculate_all_positions_has_14() -> None:
    """calculate_all_positions(jd) returns 14-body dict with Chiron at key 'Chiron'.

    Notes
    -----
    Asserts:
    - Returned dict has exactly 14 entries (one per canonical body).
    - ``'Chiron'`` is present as a key.
    - ``'Chiron'`` is the 14th entry (index 13 in insertion order).
    - Chiron position array has shape ``(6,)`` with finite lon in ``[0, 360)``.
    """
    positions = calculate_all_positions(_J2000)

    # 14 bodies
    assert len(positions) == 14, (
        f"calculate_all_positions returned {len(positions)} bodies, expected 14"
    )

    # Chiron present
    assert "Chiron" in positions, "Chiron not found in calculate_all_positions output"

    # Chiron is the 14th key (index 13 in insertion order = body_id 13)
    keys = list(positions.keys())
    assert keys[_CHIRON_IDX] == "Chiron", (
        f"Key at index 13 is '{keys[_CHIRON_IDX]}', expected 'Chiron'"
    )

    # Chiron position: shape (6,), finite lon in [0, 360)
    chiron_pos = positions["Chiron"]
    assert chiron_pos.shape == (6,), (
        f"Chiron position shape={chiron_pos.shape}, expected (6,)"
    )
    chiron_lon = float(chiron_pos[0])
    assert np.isfinite(chiron_lon), f"Chiron lon is not finite: {chiron_lon}"
    assert 0.0 <= chiron_lon < 360.0, f"Chiron lon out of [0,360): {chiron_lon}"

    # Agrees with calc_planet_position(jd, 13)
    pos13 = calc_planet_position(_J2000, _CHIRON_IDX)
    assert abs(chiron_lon - pos13[0]) < 1e-9, (
        f"calculate_all_positions['Chiron'] lon={chiron_lon} disagrees with "
        f"calc_planet_position(jd,13) lon={pos13[0]}"
    )
