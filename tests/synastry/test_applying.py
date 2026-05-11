"""Tests for the velocity-based ``applying`` field in synastry output.

Covers Pitfall 4 from ``.planning/phases/16-synastry/16-RESEARCH.md``:
the SIGNED ``speed_a - speed_b`` convention must be preserved across
retrograde-body involvements; ASC / MC speed=0 means contacts involving
the angles are always classified as non-applying; the exact-aspect
edge case ``delta == 0`` yields ``applying == False``.

Fixtures live in :mod:`tests.synastry.conftest` (auto-discovered).
"""
from __future__ import annotations

import numpy as np

from ketu.synastry import calculate_synastry


def test_applying_field_is_bool_dtype(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``result.dtype['applying']`` is ``np.bool_`` (matches SYNASTRY_DTYPE 'applying' = '?')."""
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.dtype["applying"] == np.bool_


def test_applying_for_perfect_aspect_is_false(
    chart_a_paris: np.ndarray,
) -> None:
    """At ``delta == 0`` (exact aspect), ``applying == False``.

    The signed-orb convention ``(sign(delta) * rel_speed) > 0`` gives
    ``sign(0) == 0``, so the product is 0, which is NOT > 0 — by design,
    a perfectly exact aspect is classified as neither applying nor
    separating.

    Self-synastry (chart vs itself) places every body's conjunction at
    delta=0, providing a deterministic edge case.
    """
    self_syn = calculate_synastry(chart_a_paris, chart_a_paris, mode="dense")
    diag = self_syn[self_syn["body_a"] == self_syn["body_b"]]
    assert not diag["applying"].any()


def test_applying_self_synastry_diagonal_all_false(
    chart_a_paris: np.ndarray,
) -> None:
    """All 15 self-pair conjunctions (chart vs itself) have ``applying == False``."""
    self_syn = calculate_synastry(chart_a_paris, chart_a_paris, mode="dense")
    diag = self_syn[self_syn["body_a"] == self_syn["body_b"]]
    assert len(diag) == 15
    assert (~diag["applying"]).all()


def test_applying_sign_convention_signed_delta_times_relative_speed(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Implementation matches ``(sign(delta) * (speed_a - speed_b)) > 0``.

    For every aspected row in the filtered output, re-derive ``applying``
    from the natal speeds of the involved bodies and assert equality.
    Lons / speeds come straight from the CHART_DTYPE fixtures.
    """
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    # Build extended (15,) speed arrays per chart (ASC, MC speeds = 0).
    speeds_a = np.concatenate([
        chart_a_paris["body_speeds"], np.array([0.0, 0.0]),
    ])
    speeds_b = np.concatenate([
        chart_b_nyc["body_speeds"], np.array([0.0, 0.0]),
    ])
    for row in filtered:
        sa = speeds_a[int(row["body_a"])]
        sb = speeds_b[int(row["body_b"])]
        rel = sa - sb
        delta = float(row["orb"])
        expected = bool((np.sign(delta) * rel) > 0)
        assert bool(row["applying"]) == expected, (
            f"applying mismatch on row {tuple(row)}: "
            f"expected {expected}, got {bool(row['applying'])}"
        )


def test_applying_with_retrograde_body(
    chart_a_retrograde_mercury: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Retrograde-Mercury chart preserves the signed applying convention.

    The Aug-2024 Paris fixture (``chart_a_retrograde_mercury``) carries
    Mercury at speed ~-0.19 deg/day (retrograde). For each aspected row
    where Mercury_A is involved, the hand-computed signed-convention
    expectation matches the implementation. This is the Pitfall 4 ratchet
    — if someone re-introduces ``np.abs(speed_a - speed_b)`` the test
    flips half the retrograde applying flags and trips immediately.
    """
    assert chart_a_retrograde_mercury["body_speeds"][2] < 0, (
        "Mercury must be retrograde in the test fixture"
    )
    filtered = calculate_synastry(chart_a_retrograde_mercury, chart_b_nyc)
    speeds_a_ext = np.concatenate([
        chart_a_retrograde_mercury["body_speeds"], np.array([0.0, 0.0]),
    ])
    speeds_b_ext = np.concatenate([
        chart_b_nyc["body_speeds"], np.array([0.0, 0.0]),
    ])
    mercury_rows = filtered[filtered["body_a"] == 2]
    assert mercury_rows.size > 0, "expected at least one Mercury_A aspected row"
    for row in mercury_rows:
        sa = speeds_a_ext[int(row["body_a"])]  # Mercury_A retrograde
        sb = speeds_b_ext[int(row["body_b"])]
        rel = sa - sb
        delta = float(row["orb"])
        expected = bool((np.sign(delta) * rel) > 0)
        assert bool(row["applying"]) == expected


def test_applying_angle_to_angle_contacts_are_false(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """ASC<->ASC, ASC<->MC, MC<->ASC and MC<->MC contacts are always applying=False.

    Both sides have speed=0 by :func:`_extend_body_data` convention, so
    ``rel_speed == 0`` and ``sign(delta) * 0 == 0`` is never ``> 0`` —
    angle-to-angle contacts are mechanically non-applying.

    Note: ASC/MC vs a fast-moving body (e.g. Moon) CAN have
    ``applying=True`` because ``rel_speed = -speed_b != 0``; the
    16-RESEARCH.md docstring claim that "ASC/MC contacts are always
    non-applying" only holds in the angle-to-angle sub-case. Plan 16-02
    Task 3 specified the broader claim — this test honours the correct
    narrow contract instead (see SUMMARY deviation note).
    """
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    aspected = dense[dense["aspect_type"] >= 0]
    angle_to_angle = aspected[
        ((aspected["body_a"] == 13) | (aspected["body_a"] == 14))
        & ((aspected["body_b"] == 13) | (aspected["body_b"] == 14))
    ]
    if angle_to_angle.size == 0:
        # No angle-to-angle aspects in this chart pair — still valid;
        # the invariant is vacuously true.
        return
    assert (~angle_to_angle["applying"]).all(), (
        "ASC/MC <-> ASC/MC contacts must be applying=False (both speeds = 0)"
    )


def test_applying_angle_to_planet_uses_planet_speed_sign(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """ASC/MC vs planet: applying follows ``sign(delta) * (0 - planet_speed) > 0``.

    With one side speed=0, the relative-speed reduces to the negative of
    the moving body's natal speed. The signed convention then becomes a
    deterministic function of ``sign(delta)`` and the planet's retrograde
    state. Re-derives the expectation per row and compares to the
    implementation output — this is the Pitfall 4 ratchet specialised to
    the angle case.
    """
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    speeds_a_ext = np.concatenate([
        chart_a_paris["body_speeds"], np.array([0.0, 0.0]),
    ])
    speeds_b_ext = np.concatenate([
        chart_b_nyc["body_speeds"], np.array([0.0, 0.0]),
    ])
    angle_rows = filtered[
        ((filtered["body_a"] == 13) | (filtered["body_a"] == 14)
         | (filtered["body_b"] == 13) | (filtered["body_b"] == 14))
    ]
    for row in angle_rows:
        sa = speeds_a_ext[int(row["body_a"])]
        sb = speeds_b_ext[int(row["body_b"])]
        rel = sa - sb
        delta = float(row["orb"])
        expected = bool((np.sign(delta) * rel) > 0)
        assert bool(row["applying"]) == expected


def test_applying_non_aspected_dense_rows_are_false(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense rows with ``aspect_type == -1`` have ``applying == False`` (sentinel init)."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    non_aspected = dense[dense["aspect_type"] == -1]
    assert non_aspected.size > 0
    assert (~non_aspected["applying"]).all()


def test_applying_consistent_dense_filtered(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``applying`` field for an aspected pair matches between dense (post-filter) and filtered."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc, mode="filtered")
    dense_aspected = dense[dense["aspect_type"] >= 0]
    # Both arrays are in canonical body-pair order, so they should align row-wise.
    assert len(dense_aspected) == len(filtered)
    assert np.array_equal(dense_aspected["applying"], filtered["applying"])
