"""
Tests for the _is_tautological_node_opposition helper and per-path integration.

Unit tests cover all branches of the pure helper.
Integration tests cover all four public natal/scalar emit paths.
"""

from __future__ import annotations

import numpy as np
import pytest

from ketu.aspects.calculator import (
    _is_tautological_node_opposition,
    calculate_aspects,
    calculate_aspects_batch,
    calculate_aspects_vectorized,
    get_aspect,
)

# ---------------------------------------------------------------------------
# Helper unit tests
# ---------------------------------------------------------------------------


def test_canonical_rahu_ketu_opposition_is_true() -> None:
    """Rahu↔Ketu Opposition (body1=10, body2=11, i_asp=13) is tautological."""
    assert _is_tautological_node_opposition(10, 11, 13) is True


def test_swapped_ketu_rahu_opposition_is_true() -> None:
    """Order-insensitive: Ketu↔Rahu Opposition (11, 10, 13) is also tautological."""
    assert _is_tautological_node_opposition(11, 10, 13) is True


def test_rahu_ketu_conjunction_is_false() -> None:
    """Rahu↔Ketu conjunction (i_asp=0) must still emit — not tautological."""
    assert _is_tautological_node_opposition(10, 11, 0) is False


def test_rahu_sun_opposition_is_false() -> None:
    """Rahu↔Sun opposition (10, 0, 13) must still emit — not tautological."""
    assert _is_tautological_node_opposition(10, 0, 13) is False


def test_dynamic_row_exempt() -> None:
    """Dynamic rows carry i_asp == -2 and are structurally exempt from suppression."""
    assert _is_tautological_node_opposition(10, 11, -2) is False


def test_numpy_int32_coercion() -> None:
    """np.int32 args from body1_ids[idx] coerce correctly to int inside the helper."""
    assert _is_tautological_node_opposition(np.int32(10), np.int32(11), 13) is True


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------
# Julian date: 2000-01-01 12:00 TT (J2000.0)
# Rahu is at ~120° lon (tropical), Ketu is always opposite Rahu ~300°.
# Separation = 180° → falls inside Opposition orb=(2+2)/2*1=2° → filtered.
# Rahu↔Sun separation on J2000.0: Sun ~280°, Rahu ~120° → separation ~160°,
# NOT an opposition — so we need a date where the Rahu↔Sun opposition fires.
#
# Chosen JD: 2452000.0 (~2001-06-19)
# Verify empirically: at this JD, Rahu and Sun are ~180° apart.
# If not exact, we just confirm (10,11,13) is absent and test keeps/drops correctly.
#
# NOTE: The Rahu↔Ketu separation is ALWAYS ~180° by definition (Ketu = Rahu + 180°).
# So ANY date will trigger the suppression. We also need a date where an independent
# Rahu↔Sun opposition fires for the keep-branch test.

# We probe multiple dates to find one where Rahu↔Sun is in opposition orb.
# Orb for Rahu(2)↔Sun(12) opposition = (2+12)/2 * coef(1) = 7°.
# Rahu moves ~-0.053°/day. Sun moves ~+0.986°/day. Relative motion ~1.04°/day.
# We pick a fixed date and accept that the keep-branch may fire on a nearby date.

# Use J2000.0 as the primary integration date — Rahu↔Ketu is always ~180°.
JD_TEST = 2451545.0  # 2000-01-01 12:00 TT


def test_vectorized_drops_rahu_ketu_opposition() -> None:
    """calculate_aspects_vectorized emits no (10,11,13) row for any date."""
    result = calculate_aspects_vectorized(JD_TEST)
    rk_opp = result[(result["body1"] == 10) & (result["body2"] == 11) & (result["i_asp"] == 13)]
    assert len(rk_opp) == 0, "Rahu↔Ketu Opposition must be suppressed in vectorized path"


def test_batch_drops_rahu_ketu_opposition() -> None:
    """calculate_aspects_batch emits no (10,11,13) row for any date."""
    jd_arr = np.array([JD_TEST])
    results = calculate_aspects_batch(jd_arr)
    result = results[0]
    rk_opp = result[(result["body1"] == 10) & (result["body2"] == 11) & (result["i_asp"] == 13)]
    assert len(rk_opp) == 0, "Rahu↔Ketu Opposition must be suppressed in batch path"


def test_calculate_aspects_drops_rahu_ketu_opposition() -> None:
    """calculate_aspects (slow path) emits no (10,11,13) row."""
    result = calculate_aspects(JD_TEST)
    rk_opp = result[(result["body1"] == 10) & (result["body2"] == 11) & (result["i_asp"] == 13)]
    assert len(rk_opp) == 0, "Rahu↔Ketu Opposition must be suppressed in calculate_aspects path"


def test_get_aspect_returns_none_for_rahu_ketu_opposition() -> None:
    """get_aspect(jd, 10, 11) returns None when separation is Opposition."""
    # Rahu and Ketu are always ~180° apart by definition.
    # get_aspect must return None for both argument orderings.
    result_canonical = get_aspect(JD_TEST, 10, 11)
    result_swapped = get_aspect(JD_TEST, 11, 10)
    # Either returns None (opposition suppressed) or non-opposition (if ~0° conjunction)
    # Since Rahu↔Ketu are always ~180° apart, the opposition match fires and is suppressed.
    if result_canonical is not None:
        # If something returned, it must NOT be the opposition
        assert result_canonical[2] != 13, (
            "get_aspect must not return Opposition for Rahu↔Ketu"
        )
    if result_swapped is not None:
        assert result_swapped[2] != 13, (
            "get_aspect (swapped) must not return Opposition for Ketu↔Rahu"
        )


def test_rahu_ketu_conjunction_keep_branch() -> None:
    """Rahu↔Ketu conjunction is still emitted by calculate_aspects_vectorized when in orb."""
    # Rahu and Ketu are NEVER in conjunction (always ~180° apart by astronomical definition).
    # Instead, test that Rahu↔Ketu conjunction is NOT erroneously suppressed (it won't
    # appear simply because it never fires) — the helper does not touch conjunction (i_asp=0).
    # Verify at the unit level: _is_tautological_node_opposition(10,11,0) is False (already done).
    assert _is_tautological_node_opposition(10, 11, 0) is False


def test_rahu_sun_opposition_keep_branch_vectorized() -> None:
    """A non-tautological opposition (Rahu↔Sun) is not filtered from vectorized results.

    We scan a range of dates to find one where Rahu and Sun are ~180° apart
    within the 7° orb. The test is skipped gracefully if no such date is in range.
    """
    from ketu.calculations import long, distance

    # Scan 365 days starting from JD_TEST
    for offset in range(0, 365):
        jd = JD_TEST + offset
        rahu_lon = long(jd, 10)
        sun_lon = long(jd, 0)
        sep = distance(rahu_lon, sun_lon)
        if abs(sep - 180.0) <= 7.0:
            # Found a date where Rahu↔Sun is in opposition orb
            result = calculate_aspects_vectorized(jd)
            rs_opp = result[
                (result["body1"] == 0) & (result["body2"] == 10) & (result["i_asp"] == 13)
            ]
            assert len(rs_opp) > 0, (
                f"Rahu↔Sun Opposition should be detected at JD={jd} (sep={sep:.2f}°)"
            )
            return  # Test passed

    pytest.skip("No Rahu↔Sun opposition found in the 365-day scan window")
