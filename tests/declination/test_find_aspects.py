"""Behavioral tests for find_declination_aspects: pitfalls, oracle, orb formula.

Covers:
- The 4 required pitfall tests (sign conflation, orb inflation, zero-sign trap,
  MIN_DECL_ORB floor) sourced verbatim from RESEARCH.md.
- The JD 2451717.0 (2000-06-21) 10-aspect oracle (5 P + 5 CP) with exact pairs.
- The orb formula values for representative body pairs.
- Negative regression seed (Seed 2, JD 2460676.5) confirming no false positive.
- Empty-result type guard.
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.calculations import declination
from ketu.declination import DECLA_ASPECT_DTYPE, find_declination_aspects
from ketu.declination.core import _ORB_MAT


# ---------------------------------------------------------------------------
# Pitfall 1: Sign conflation — +15/−15 is CP not P
# ---------------------------------------------------------------------------

def test_pitfall_sign_conflation() -> None:
    """Sun +15 / Moon -15 must be a contra-parallel, NOT a parallel.

    The naive absolute-value distance ``|15| - |-15| = 0`` would falsely
    indicate a perfect parallel. The correct metric for parallel is
    ``|d1 - d2| = |15 - (-15)| = 30 > orb``. The correct metric for
    contra-parallel is ``|d1 + d2| = |15 + (-15)| = 0 <= orb``.
    """
    d = np.zeros(14)
    d[0] = +15.0   # Sun body 0
    d[1] = -15.0   # Moon body 1
    result = find_declination_aspects(d)
    mask_p  = result["kind"] == "P"
    mask_cp = result["kind"] == "CP"
    p_sun_moon = result[(result["body1"] == 0) & (result["body2"] == 1) & mask_p]
    cp_sun_moon = result[(result["body1"] == 0) & (result["body2"] == 1) & mask_cp]
    assert len(p_sun_moon) == 0, "Sun +15 / Moon -15 must NOT be a parallel"
    assert len(cp_sun_moon) == 1, "Sun +15 / Moon -15 MUST be a contra-parallel"
    assert cp_sun_moon[0]["gap"] < 0.001


# ---------------------------------------------------------------------------
# Pitfall 2: Orb inflation — 7° Sun/Moon gap not parallel
# ---------------------------------------------------------------------------

def test_pitfall_orb_inflation() -> None:
    """7° Sun/Moon gap must NOT be detected as a parallel (orb is 1.0°, not 12°).

    A naive implementation that used the full natal orb of 12° would
    falsely flag this 7° gap. The DECLA_COEF=1/12 tightening reduces the
    Sun/Moon orb to exactly 1.0°.
    """
    d = np.zeros(14)
    d[0] = +15.0   # Sun
    d[1] = +22.0   # Moon — gap = 7° > 1.0° orb
    result = find_declination_aspects(d)
    p_sun_moon = result[
        (result["body1"] == 0) & (result["body2"] == 1) & (result["kind"] == "P")
    ]
    assert len(p_sun_moon) == 0, "7° gap must NOT be a parallel (orb is 1.0° not 12°)"


# ---------------------------------------------------------------------------
# Pitfall 3: Zero-sign trap — δ=0 → no aspect
# ---------------------------------------------------------------------------

def test_pitfall_zero_sign_trap() -> None:
    """All-zero declinations must produce no aspects; near-zero opposite signs are CP not P.

    ``sign(0) == 0``, so bodies at exactly δ=0 match neither the parallel
    condition (same non-zero sign) nor the contra-parallel condition (opposite
    non-zero signs). The sub-case with ±0.01° confirms that very small opposite
    declinations ARE contra-parallels (within the 0.5° floor) but NOT parallels.
    """
    # All-zero case
    d = np.zeros(14)
    result = find_declination_aspects(d)
    assert len(result) == 0, "All-zero declinations must produce no aspects"

    # Near-zero opposite sign sub-case
    d2 = np.zeros(14)
    d2[0] = +0.01   # Sun just north
    d2[1] = -0.01   # Moon just south
    result2 = find_declination_aspects(d2)
    p = result2[result2["kind"] == "P"]
    cp = result2[result2["kind"] == "CP"]
    assert len(p) == 0, "Near-zero opposite signs must NOT be parallel"
    # gap = 0.02° < MIN_DECL_ORB 0.5° → IS a contra-parallel
    assert len(cp) >= 1, "Near-zero opposite signs MUST be contra-parallel (within 0.5° floor)"


# ---------------------------------------------------------------------------
# Pitfall 4: MIN_DECL_ORB floor — Rahu/Lilith gap 0.1° → parallel
# ---------------------------------------------------------------------------

def test_pitfall_min_orb_floor() -> None:
    """Rahu/Lilith gap 0.1° must be detected via the MIN_DECL_ORB=0.5° floor.

    Without the floor, ``orb = max(0 * 1/12, 0) = 0.0°`` → no detection.
    With the floor, ``orb = max(0, 0.5) = 0.5°`` → detects the 0.1° gap.
    Rahu is body 10 (orb=0) and Lilith is body 12 (orb=0).
    """
    d = np.zeros(14)
    d[10] = +12.5   # Rahu (orb=0)
    d[12] = +12.4   # Lilith (orb=0) — gap = 0.1°, both orb=0
    result = find_declination_aspects(d)
    p_rahu_lilith = result[
        (result["body1"] == 10) & (result["body2"] == 12) & (result["kind"] == "P")
    ]
    assert len(p_rahu_lilith) == 1, (
        "Rahu/Lilith parallel (gap 0.1°) must be detected via MIN_DECL_ORB floor"
    )


# ---------------------------------------------------------------------------
# Orb formula values
# ---------------------------------------------------------------------------

def test_orb_formula_values() -> None:
    """Per-pair orb limits match the formula max((orb_b1+orb_b2)/2*1/12, 0.5).

    Verified pairs (from RESEARCH.md §Orb Formula Verification):
      - (0,1) Sun/Moon:     max((12+12)/2 × 1/12, 0.5) = 1.0000°
      - (0,3) Sun/Venus:    max((12+10)/2 × 1/12, 0.5) = 0.9167°
      - (3,4) Venus/Mars:   max((10+8)/2  × 1/12, 0.5) = 0.7500°
      - (10,12) Rahu/Lilith: max((0+0)/2  × 1/12, 0.5) = 0.5000° (floor)
      - (9,13) Pluto/Chiron: max((4+4)/2  × 1/12, 0.5) = 0.5000° (floor; 0.333<floor)
    """
    assert _ORB_MAT[0, 1] == pytest.approx(1.0)
    assert _ORB_MAT[0, 3] == pytest.approx(0.9167, abs=1e-4)
    assert _ORB_MAT[3, 4] == pytest.approx(0.75)
    assert _ORB_MAT[10, 12] == pytest.approx(0.5)
    assert _ORB_MAT[9, 13] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# JD 2451717.0 oracle — 10 aspects (5 P + 5 CP)
# ---------------------------------------------------------------------------

def test_solstice_oracle(body_decl_solstice: np.ndarray) -> None:
    """JD 2451717.0 (2000-06-21) oracle: exactly 10 rows (5 P + 5 CP) with exact pairs.

    Expected parallel pairs (from RESEARCH.md Seed 1):
        (0,3) Sun/Venus, (0,4) Sun/Mars, (1,13) Moon/Chiron,
        (2,10) Mercury/Rahu, (3,4) Venus/Mars

    Expected contra-parallel pairs:
        (1,6) Moon/Saturn, (2,11) Mercury/Ketu, (5,8) Jupiter/Neptune,
        (6,13) Saturn/Chiron, (10,11) Rahu/Ketu
    """
    result = find_declination_aspects(body_decl_solstice)

    # Total row count
    assert len(result) == 10, (
        f"Expected 10 aspects at JD 2451717.0, got {len(result)}"
    )

    # P/CP split
    n_p  = int(np.sum(result["kind"] == "P"))
    n_cp = int(np.sum(result["kind"] == "CP"))
    assert n_p  == 5, f"Expected 5 parallels, got {n_p}"
    assert n_cp == 5, f"Expected 5 contra-parallels, got {n_cp}"

    # Exact pair+kind set
    expected_pairs = {
        (0, 3, "P"),   # Sun/Venus parallel
        (0, 4, "P"),   # Sun/Mars parallel
        (1, 13, "P"),  # Moon/Chiron parallel
        (2, 10, "P"),  # Mercury/Rahu parallel
        (3, 4, "P"),   # Venus/Mars parallel
        (1, 6, "CP"),  # Moon/Saturn contra-parallel
        (2, 11, "CP"), # Mercury/Ketu contra-parallel
        (5, 8, "CP"),  # Jupiter/Neptune contra-parallel
        (6, 13, "CP"), # Saturn/Chiron contra-parallel
        (10, 11, "CP"), # Rahu/Ketu contra-parallel
    }
    actual_pairs = {
        (int(row["body1"]), int(row["body2"]), str(row["kind"]))
        for row in result
    }
    assert actual_pairs == expected_pairs, (
        f"Pair+kind set mismatch:\n  expected={expected_pairs}\n  actual={actual_pairs}"
    )

    # Each row: gap <= orb
    for row in result:
        assert row["gap"] <= row["orb"], (
            f"Row {row} has gap > orb — detection logic error"
        )

    # Spot-check 3 gaps (abs=2e-3 tolerance per RESEARCH.md)
    moon_chiron = result[(result["body1"] == 1) & (result["body2"] == 13) & (result["kind"] == "P")]
    assert moon_chiron[0]["gap"] == pytest.approx(0.0333, abs=2e-3), (
        f"Moon/Chiron P gap mismatch: {moon_chiron[0]['gap']}"
    )

    rahu_ketu = result[(result["body1"] == 10) & (result["body2"] == 11) & (result["kind"] == "CP")]
    assert rahu_ketu[0]["gap"] == pytest.approx(0.0019, abs=2e-3), (
        f"Rahu/Ketu CP gap mismatch: {rahu_ketu[0]['gap']}"
    )

    sun_venus = result[(result["body1"] == 0) & (result["body2"] == 3) & (result["kind"] == "P")]
    assert sun_venus[0]["gap"] == pytest.approx(0.4542, abs=2e-3), (
        f"Sun/Venus P gap mismatch: {sun_venus[0]['gap']}"
    )

    # body1 < body2 always
    assert np.all(result["body1"] < result["body2"]), "body1 < body2 invariant violated"

    # Sorted ascending by (body1, body2)
    sort_keys = result["body1"].astype(np.int32) * 14 + result["body2"].astype(np.int32)
    assert np.all(sort_keys[:-1] <= sort_keys[1:]), "Result not sorted by (body1, body2)"


# ---------------------------------------------------------------------------
# Negative regression: Seed 2 — Sun/Moon NOT parallel at JD 2460676.5
# ---------------------------------------------------------------------------

def test_negative_seed_sun_moon_not_parallel() -> None:
    """At JD 2460676.5 (2025-01-01), Sun/Moon gap ~2.887° > orb 1.0° — NOT parallel.

    Confirms the detector does not falsely trigger on large same-side gaps.
    Moon δ ≈ -25.885°, Sun δ ≈ -22.998°; gap ≈ 2.887° > 1.0° orb.
    """
    jd_oob = 2460676.5
    body_decl = np.array([declination(jd_oob, i) for i in range(14)])
    result = find_declination_aspects(body_decl)
    sun_moon_p = result[
        (result["body1"] == 0) & (result["body2"] == 1) & (result["kind"] == "P")
    ]
    assert len(sun_moon_p) == 0, (
        f"Sun/Moon falsely detected as parallel at JD 2460676.5 "
        f"(gap {abs(body_decl[0] - body_decl[1]):.4f}° should exceed orb 1.0°)"
    )


# ---------------------------------------------------------------------------
# Empty-result type guard
# ---------------------------------------------------------------------------

def test_empty_result_is_array_not_none(body_decl_zeros: np.ndarray) -> None:
    """find_declination_aspects(zeros) returns an ndarray with DECLA_ASPECT_DTYPE, len 0.

    Guards against None / tuple return conventions. The contract is
    ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)`` — always an ndarray.
    """
    result = find_declination_aspects(body_decl_zeros)
    assert isinstance(result, np.ndarray), (
        f"Expected np.ndarray, got {type(result)!r}"
    )
    assert result.dtype == DECLA_ASPECT_DTYPE, (
        f"Expected DECLA_ASPECT_DTYPE, got {result.dtype!r}"
    )
    assert len(result) == 0, f"Expected empty result, got {len(result)} rows"
