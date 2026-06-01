"""Tests for the dense aspect matrix wired by plan 14-03.

The dense ``(14, 14)`` aspect block of :data:`ketu.charts.CHART_DTYPE` is
populated by ``_build_aspect_matrix`` (private helper inside
``ketu.charts.api``). This module exhaustively covers:

- default ``aspects=None`` ratchet (D-07: ``TRADITIONAL`` is the package
  default — the 7 half-circle aspects, harmonics 1/2/3/6; re-pointed from
  CLASSICAL by Phase 26 plan 02),
- symmetry of ``aspect_matrix`` and ``aspect_orbs`` (D-17),
- diagonal sentinels ``-1`` / ``NaN`` (D-06, RESEARCH §Pitfall 6),
- consistency vs :func:`ketu.aspects.calculator.calculate_aspects_vectorized`
  standalone (D-16: wrapper correctness, not aspect math correctness),
- ``AspectSetSpec`` pass-through filtering (D-10),
- caller-mask pattern equivalence between the two sentinels,
- scalar-jd traversal of ``np.ndindex(())`` (RESEARCH Assumption A1),
- vectorised vs per-element-loop equivalence,
- 3 hand-validated charts with rich aspect content (RESEARCH §6:
  J2000_Paris, 1900_NewYork, Sagan_NYC_1934).

The aspect math itself is exercised in ``tests/test_aspect_calculator.py``
and earlier; here we focus on the wrapping done by ``compute_chart`` and
the dense-matrix layout contract.
"""
from __future__ import annotations

import itertools
from typing import Any

import numpy as np
import pytest

from ketu.aspects.calculator import calculate_aspects_vectorized
from ketu.charts import compute_chart

# Canonical aspect indices into ``ketu.core.aspects``.
# 0=Conjunction, 4=Sextile, 7=Square, 9=Trine, 13=Opposition are part of the
# curated CLASSICAL set (5 majors). See ``ketu/aspects/presets.py`` for the
# full table. The PACKAGE DEFAULT is now TRADITIONAL (7 half-circle aspects).
_I_CONJUNCTION: int = 0
_I_TRINE: int = 9
_CLASSICAL_INDICES: set[int] = {0, 4, 7, 9, 13}  # curated 5-aspect set (opt-in)

# Tolerance on orb cross-checks: the wrapper passes records through
# verbatim, so identity is expected modulo float32 narrowing inside
# ``aspect_orbs`` (calculate_aspects_vectorized emits f4 already).
_ORB_TOL_DEG: float = 1e-5

# Hand-validated reference points (RESEARCH §6 / Open Question 3).
# ``Sagan_NYC_1934`` is recomputed from ``swe.julday`` to avoid a stale
# JD literal in the plan; ~0.005 d drift in the plan's number is below
# any aspect-detection threshold but recomputing keeps the fixture
# self-explanatory.
_HAND_VALIDATED_CHARTS: list[dict[str, Any]] = [
    {
        "label": "J2000_Paris",
        "jd": 2451545.0,
        "lat": 48.8566,
        "lon": 2.3522,
    },
    {
        "label": "1900_NewYork",
        "jd": 2415020.5,
        "lat": 40.7128,
        "lon": -74.0060,
    },
    {
        "label": "Sagan_NYC_1934",
        "jd": 2427750.711806,
        "lat": 40.6943,
        "lon": -73.9249,
    },
]


# ---------------------------------------------------------------------------
# Default aspect set (D-07)
# ---------------------------------------------------------------------------


def test_aspect_matrix_default_aspects_is_traditional() -> None:
    """D-07 ratchet: ``aspects=None`` resolves to TRADITIONAL (7 half-circle).

    Re-pointed from CLASSICAL by Phase 26 plan 02. The package default is now
    the 7 half-circle aspects (harmonics 1/2/3/6 — TRADITIONAL), not the
    curated 5-major CLASSICAL set.
    """
    chart_default = compute_chart(2451545.0, 48.86, 2.35)
    chart_explicit = compute_chart(2451545.0, 48.86, 2.35, aspects="traditional")

    assert np.array_equal(
        chart_default["aspect_matrix"], chart_explicit["aspect_matrix"]
    ), "aspects=None must equal aspects='traditional' (D-07)"
    assert np.array_equal(
        chart_default["aspect_orbs"], chart_explicit["aspect_orbs"], equal_nan=True
    ), "aspects=None must equal aspects='traditional' (orbs, D-07)"


# ---------------------------------------------------------------------------
# Symmetry (D-17)
# ---------------------------------------------------------------------------


def test_aspect_matrix_symmetric() -> None:
    """D-17 ratchet: ``aspect_matrix[i, j] == aspect_matrix[j, i]`` for all i, j."""
    chart = compute_chart(2451545.0, 48.86, 2.35)
    m = chart["aspect_matrix"]
    assert np.array_equal(m, m.T), "aspect_matrix must be symmetric (D-17)"


def test_aspect_orbs_symmetric_with_nan_handling() -> None:
    """D-17 ratchet (orbs): symmetry with NaN-safe equality."""
    chart = compute_chart(2451545.0, 48.86, 2.35)
    o = chart["aspect_orbs"]
    assert np.array_equal(o, o.T, equal_nan=True), (
        "aspect_orbs must be symmetric (D-17, NaN-safe)"
    )


# ---------------------------------------------------------------------------
# Diagonal sentinels (D-06, RESEARCH §Pitfall 6)
# ---------------------------------------------------------------------------


def test_aspect_matrix_diagonal_sentinels() -> None:
    """D-06 / Pitfall 6: diagonal stays at ``-1`` (matrix) and ``NaN`` (orbs)."""
    chart = compute_chart(2451545.0, 48.86, 2.35)
    m = chart["aspect_matrix"]
    o = chart["aspect_orbs"]
    for i in range(14):
        assert int(m[i, i]) == -1, (
            f"aspect_matrix[{i}, {i}] expected -1 (sentinel); got {int(m[i, i])}"
        )
        assert np.isnan(o[i, i]), (
            f"aspect_orbs[{i}, {i}] expected NaN (sentinel); got {float(o[i, i])}"
        )


# ---------------------------------------------------------------------------
# Consistency vs calculate_aspects_vectorized standalone (D-16)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _HAND_VALIDATED_CHARTS,
    ids=[c["label"] for c in _HAND_VALIDATED_CHARTS],
)
def test_aspect_matrix_consistent_with_calculate_aspects_vectorized_standalone(
    fixture: dict[str, Any],
) -> None:
    """D-16 wrapping correctness: each record from the standalone calculator
    appears at its expected ``(i, j)`` cell, and every populated upper-triangle
    cell corresponds to exactly one standalone record. Bidirectional round-trip.
    """
    jd, lat, lon = fixture["jd"], fixture["lat"], fixture["lon"]
    chart = compute_chart(jd, lat, lon, aspects="classical")
    records = calculate_aspects_vectorized(jd, aspects="classical")

    m = chart["aspect_matrix"]
    o = chart["aspect_orbs"]

    # Forward: every standalone record lives at its (b1, b2) cell.
    for rec in records:
        b1 = int(rec["body1"])
        b2 = int(rec["body2"])
        i_asp = int(rec["i_asp"])
        orb = float(rec["orb"])
        assert int(m[b1, b2]) == i_asp, (
            f"{fixture['label']}: matrix[{b1}, {b2}] expected {i_asp}; "
            f"got {int(m[b1, b2])}"
        )
        assert abs(float(o[b1, b2]) - orb) < _ORB_TOL_DEG, (
            f"{fixture['label']}: orbs[{b1}, {b2}] expected {orb:.6f}; "
            f"got {float(o[b1, b2]):.6f}"
        )

    # Reverse: every populated upper-triangle cell maps back to a record.
    record_pairs = {(int(r["body1"]), int(r["body2"])) for r in records}
    for i, j in itertools.combinations(range(14), 2):
        if int(m[i, j]) >= 0:
            assert (i, j) in record_pairs, (
                f"{fixture['label']}: matrix[{i}, {j}] is populated "
                f"({int(m[i, j])}) but no standalone record matches"
            )


# ---------------------------------------------------------------------------
# AspectSetSpec pass-through (D-10)
# ---------------------------------------------------------------------------


def test_aspect_matrix_handles_aspect_subset() -> None:
    """D-10 ratchet: a list-spec subset filters out unselected aspects.

    Conjunction (i_asp=0) and Trine (i_asp=9) are kept; Square (i_asp=7)
    and Opposition (i_asp=13) must NOT appear.
    """
    chart = compute_chart(
        2427750.711806, 40.6943, -73.9249,
        aspects=["Conjunction", "Trine"],
    )
    m = chart["aspect_matrix"]
    populated = m[m >= 0]
    populated_values = set(int(v) for v in populated)

    assert len(populated_values) > 0, (
        "Sagan chart has classical aspects, so a {Conjunction, Trine} "
        "subset must yield at least one populated cell"
    )
    assert populated_values <= {_I_CONJUNCTION, _I_TRINE}, (
        f"populated cells must be in {{0, 9}}; got {populated_values}"
    )
    # Verify Square (7) and Opposition (13) are filtered out — relies on
    # the same set-of-int derivation above to dodge the NumPy ``sum()``
    # reduction (which is what triggers the ``_NoValueType`` bug under
    # ``coverage.py + swisseph + numpy lazy reload``; see
    # tests/houses/conftest.py:32-43 for the rationale).
    assert 7 not in populated_values, (
        "Square (i_asp=7) leaked through aspect filter"
    )
    assert 13 not in populated_values, (
        "Opposition (i_asp=13) leaked through aspect filter"
    )


# ---------------------------------------------------------------------------
# Caller mask equivalence (Pitfall 6)
# ---------------------------------------------------------------------------


def test_aspect_matrix_caller_mask_pattern() -> None:
    """Pitfall 6: the two sentinel masks are equivalent.

    ``chart["aspect_matrix"] >= 0`` and ``~np.isnan(chart["aspect_orbs"])``
    must select the exact same cells; a divergence would mean a row was
    written into one matrix but not the other.
    """
    chart = compute_chart(2451545.0, 48.86, 2.35)
    mask_matrix = chart["aspect_matrix"] >= 0
    mask_orbs = ~np.isnan(chart["aspect_orbs"])
    assert np.array_equal(mask_matrix, mask_orbs), (
        "sentinel masks (matrix >= 0) and (~isnan(orbs)) must coincide"
    )


# ---------------------------------------------------------------------------
# Scalar-jd via np.ndindex(()) (RESEARCH Assumption A1)
# ---------------------------------------------------------------------------


def test_aspect_matrix_scalar_jd_via_ndindex_empty_tuple() -> None:
    """A1 ratchet: scalar-jd traverses ``np.ndindex(())`` once (no shape inflation)."""
    # Standalone smoke check pinning the underlying numpy contract.
    assert list(np.ndindex(())) == [()], (
        "np.ndindex(()) must yield exactly [()] — Assumption A1 in RESEARCH"
    )

    chart = compute_chart(2451545.0, 48.86, 2.35)
    # Scalar inputs yield 0-d structured array; aspect_matrix is (14, 14),
    # NOT (1, 14, 14) — that would mean we accidentally promoted to a
    # leading shape of size 1.
    assert chart["aspect_matrix"].shape == (14, 14)
    assert chart["aspect_matrix"].dtype == np.int8
    assert chart["aspect_orbs"].shape == (14, 14)
    assert chart["aspect_orbs"].dtype == np.float32


# ---------------------------------------------------------------------------
# Vectorised vs per-element-loop equivalence
# ---------------------------------------------------------------------------


def test_aspect_matrix_vectorised_consistent_with_per_element_loop() -> None:
    """Batch ``compute_chart`` matches scalar ``compute_chart`` per element.

    Iterates over 5 timestamps spanning ~150 years. Each batch element
    must equal the scalar call at the same ``(jd, lat, lon)``.
    """
    jds = np.array(
        [2415020.5, 2427750.711806, 2451545.0, 2459580.5, 2470204.0],
        dtype=np.float64,
    )
    lats = np.array([40.7128, 40.6943, 48.8566, 51.5074, 64.15], dtype=np.float64)
    lons = np.array([-74.0060, -73.9249, 2.3522, -0.1278, -21.94], dtype=np.float64)

    # Polar fallback Porphyry needed for the Reykjavik (lat=64.15) row at
    # 2050-01-01.5; otherwise calculate_houses raises HighLatitudeError.
    chart_batch = compute_chart(jds, lats, lons, polar_fallback="porphyry")
    assert chart_batch.shape == (5,)
    assert chart_batch["aspect_matrix"].shape == (5, 14, 14)

    for i in range(5):
        chart_scalar = compute_chart(
            float(jds[i]), float(lats[i]), float(lons[i]),
            polar_fallback="porphyry",
        )
        assert np.array_equal(
            chart_batch[i]["aspect_matrix"], chart_scalar["aspect_matrix"]
        ), f"row {i}: aspect_matrix differs between batch and scalar calls"
        assert np.array_equal(
            chart_batch[i]["aspect_orbs"],
            chart_scalar["aspect_orbs"],
            equal_nan=True,
        ), f"row {i}: aspect_orbs differs between batch and scalar calls"


# ---------------------------------------------------------------------------
# Hand-validated charts (RESEARCH §6, Open Question 3)
# ---------------------------------------------------------------------------


def test_aspect_matrix_hand_validated_chart_J2000_Paris() -> None:
    """Hand-validated chart #1: J2000 noon at Paris.

    Cross-validation vs ``calculate_aspects_vectorized`` is exercised by
    :func:`test_aspect_matrix_consistent_with_calculate_aspects_vectorized_standalone`
    above; here we add a structural spot-check that at least one Sun
    aspect is populated (the Sun is involved in classical aspects on
    nearly every chart given its 12 deg conjunction orb), AND that
    Sun-Mercury are flagged as Conjunction — a geometric inevitability
    since Mercury is always within 28 deg of the Sun and the
    Conjunction orb in CLASSICAL spans 12 deg.
    """
    chart = compute_chart(2451545.0, 48.8566, 2.3522, aspects="classical")
    m = chart["aspect_matrix"]
    o = chart["aspect_orbs"]

    # Sun-Mercury (body 0 and body 2) are necessarily within Conjunction orb.
    assert int(m[0, 2]) == _I_CONJUNCTION, (
        f"J2000_Paris Sun-Mercury aspect expected Conjunction (0); "
        f"got {int(m[0, 2])}"
    )
    assert not np.isnan(o[0, 2]), "Sun-Mercury orb must not be NaN"
    # Symmetric mirror sanity:
    assert int(m[2, 0]) == int(m[0, 2])
    assert float(o[2, 0]) == float(o[0, 2])


def test_aspect_matrix_hand_validated_chart_1900_NewYork() -> None:
    """Hand-validated chart #2: 1900-01-01 midnight UT at New York.

    Spot-check on the Mercury-Pluto-Rahu cluster around 250 deg in 1900:
    Mercury (body 2) and Rahu (body 10) are nearly conjunct (sub-degree
    orb), giving an unambiguous Conjunction cell. Validates the matrix
    is non-trivially populated AND the diagonal stays at sentinel.
    """
    chart = compute_chart(2415020.5, 40.7128, -74.0060, aspects="classical")
    m = chart["aspect_matrix"]
    # Diagonal sanity:
    for i in range(14):
        assert int(m[i, i]) == -1
    # Mercury-Rahu (body 2 / body 10) Conjunction sanity (orb ~0.04 deg):
    assert int(m[2, 10]) == _I_CONJUNCTION, (
        f"1900_NewYork Mercury-Rahu expected Conjunction (0); got {int(m[2, 10])}"
    )
    # Symmetric mirror:
    assert int(m[10, 2]) == int(m[2, 10])


def test_aspect_matrix_hand_validated_chart_Sagan_NYC_1934() -> None:
    """Hand-validated chart #3: Carl Sagan, 1934-11-09 05:05 UT in NYC.

    Sagan's chart features a triple Jupiter-Saturn-Uranus configuration
    in Aries/Taurus/Aquarius giving rich classical aspects. Verifies
    the matrix is non-trivially populated AND the ``calculate_aspects_vectorized``
    standalone count matches the populated upper-triangle count (round-trip).
    """
    jd, lat, lon = 2427750.711806, 40.6943, -73.9249
    chart = compute_chart(jd, lat, lon, aspects="classical")
    records = calculate_aspects_vectorized(jd, aspects="classical")

    m = chart["aspect_matrix"]
    populated_pairs = sum(
        1 for i, j in itertools.combinations(range(14), 2) if int(m[i, j]) >= 0
    )

    # Sagan chart is rich — at least 10 classical aspects expected
    # (defensive lower bound; current ephemeris yields ~19).
    assert populated_pairs >= 10, (
        f"Sagan chart expected >=10 classical aspects; got {populated_pairs}"
    )
    # Round-trip: standalone record count == upper-triangle populated cells.
    assert populated_pairs == len(records), (
        f"Sagan chart: matrix has {populated_pairs} populated upper-triangle "
        f"cells; standalone calculator yields {len(records)} records"
    )
