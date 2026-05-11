"""Tests for :func:`ketu.synastry.calculate_synastry` — Phase 16 Plan 02.

Covers: public API surface, mode dispatch, cross-product enumeration with
self-pairs included, orb tightening, CHART_DTYPE consumption, sentinel
convention, filtered row order, dtype precision (Pitfall 6 ratchet),
polar input ratchet.

Fixtures live in :mod:`tests.synastry.conftest` (auto-discovered by pytest).
"""
from __future__ import annotations

import numpy as np
import pytest

from ketu.core import aspects as _ASPECTS
from ketu.synastry import (
    SYNASTRY_BODY_COUNT,
    SYNASTRY_DTYPE,
    SYNASTRY_FACTOR,
    calculate_synastry,
)
from ketu.synastry.orbs import _BODY_ORBS_15, synastry_orb_limit


# ---------------------------------------------------------------------------
# A. Public API surface
# ---------------------------------------------------------------------------

def test_calculate_synastry_signature_accepts_default_args(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Calling with only (chart_a, chart_b) works using default kwargs."""
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.ndim == 1


def test_calculate_synastry_returns_synastry_dtype(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Result dtype is exactly SYNASTRY_DTYPE."""
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.dtype == SYNASTRY_DTYPE


def test_calculate_synastry_filtered_default_mode(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Default mode (no ``mode=`` kw) is equivalent to ``mode='filtered'``."""
    default = calculate_synastry(chart_a_paris, chart_b_nyc)
    explicit = calculate_synastry(chart_a_paris, chart_b_nyc, mode="filtered")
    assert len(default) == len(explicit)


# ---------------------------------------------------------------------------
# B. Mode dispatch
# ---------------------------------------------------------------------------

def test_dense_mode_shape_is_225(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense mode always returns exactly 225 rows (15 x 15 ordered pairs)."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    assert dense.shape == (225,)


def test_filtered_mode_returns_only_aspected_rows(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Filtered mode emits only rows with ``aspect_type >= 0``."""
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc, mode="filtered")
    assert (filtered["aspect_type"] >= 0).all()


def test_filtered_count_le_dense_count(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Filtered row count is bounded above by dense row count (225)."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc, mode="filtered")
    assert len(filtered) <= len(dense)


def test_invalid_mode_raises_value_error(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Unknown ``mode`` raises ValueError naming the valid presets."""
    with pytest.raises(ValueError) as excinfo:
        calculate_synastry(chart_a_paris, chart_b_nyc, mode="matrix")
    msg = str(excinfo.value)
    assert "dense" in msg and "filtered" in msg


# ---------------------------------------------------------------------------
# C. Cross-product enumeration / self-pairs (locked CONTEXT.md decision)
# ---------------------------------------------------------------------------

def test_dense_includes_self_pairs_sun_sun(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense output contains a row with ``body_a == 0 == body_b`` (Sun_A<->Sun_B).

    If this test fails, the implementation reverted to ``triu_indices`` —
    self-pairs are non-negotiable per CONTEXT.md locked decision (Sun_A<->Sun_B
    is the canonical synastry ego-compatibility aspect).
    """
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    sun_sun = dense[(dense["body_a"] == 0) & (dense["body_b"] == 0)]
    assert sun_sun.size == 1


def test_dense_includes_self_pairs_moon_moon(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense output contains a row with ``(body_a, body_b) == (1, 1)`` (Moon_A<->Moon_B)."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    moon_moon = dense[(dense["body_a"] == 1) & (dense["body_b"] == 1)]
    assert moon_moon.size == 1


def test_dense_distinguishes_ordered_pairs(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Row ``(Sun_A, Mars_B)`` is distinct from ``(Mars_A, Sun_B)``."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    sun_a_mars_b = dense[(dense["body_a"] == 0) & (dense["body_b"] == 4)]
    mars_a_sun_b = dense[(dense["body_a"] == 4) & (dense["body_b"] == 0)]
    assert sun_a_mars_b.size == 1
    assert mars_a_sun_b.size == 1
    # ``lon_a``/``lon_b`` differ because chart-of-origin swaps.
    assert sun_a_mars_b["lon_a"][0] != mars_a_sun_b["lon_a"][0]
    assert sun_a_mars_b["lon_b"][0] != mars_a_sun_b["lon_b"][0]


def test_dense_includes_asc_mc_contacts(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense output covers ASC_A (body_a=13) and MC_A (body_a=14) rows; total = 225."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    assert dense.shape == (225,)
    assert (dense["body_a"] == 13).sum() == 15  # ASC_A x 15 chart-B bodies
    assert (dense["body_a"] == 14).sum() == 15  # MC_A  x 15 chart-B bodies


# ---------------------------------------------------------------------------
# D. Orb tightening (synastry vs classical)
# ---------------------------------------------------------------------------

def test_default_orbs_synastry_factor_05(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Default ``orbs='synastry'`` applies factor 0.5 to the natal formula.

    For the chart pair, every ``orb_limit`` in the result equals one half
    of the corresponding natal-orb value (``synastry_orb_limit(.., factor=1.0)``).
    """
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    for row in filtered:
        b1 = int(row["body_a"])
        b2 = int(row["body_b"])
        asp = int(row["aspect_type"])
        natal_limit = synastry_orb_limit(b1, b2, asp, factor=1.0)
        # The recorded orb_limit equals natal_limit * SYNASTRY_FACTOR
        # within float32 precision (write-time f4 cast).
        expected = np.float32(natal_limit * SYNASTRY_FACTOR)
        assert np.isclose(row["orb_limit"], expected, atol=1e-5)


def test_orbs_classical_uses_full_natal(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``orbs='classical'`` (factor 1.0) yields >= as many aspects as default (factor 0.5)."""
    default = calculate_synastry(chart_a_paris, chart_b_nyc)
    classical = calculate_synastry(
        chart_a_paris, chart_b_nyc, orbs="classical",
    )
    # Wider orbs => at least as many in-orb pairs.
    assert len(classical) >= len(default)


def test_orbs_unknown_string_raises(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Unknown ``orbs=`` preset raises ValueError (propagated from resolver)."""
    with pytest.raises(ValueError):
        calculate_synastry(chart_a_paris, chart_b_nyc, orbs="random")


def test_aspects_classical_5_aspect_types_only(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``aspects='classical'`` (default) emits only the 5 majors (0/4/7/9/13)."""
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    found_types = set(filtered["aspect_type"].tolist())
    classical_majors = {0, 4, 7, 9, 13}
    assert found_types <= classical_majors


# ---------------------------------------------------------------------------
# E. CHART_DTYPE consumption
# ---------------------------------------------------------------------------

def test_consumes_chart_dtype_scalar(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Inputs are 0-d CHART_DTYPE scalars; output is a 1-D structured array."""
    assert chart_a_paris.ndim == 0
    assert chart_b_nyc.ndim == 0
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.ndim == 1


def test_chart_lons_propagate_correctly(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``lon_a`` for any row where ``body_a == 0`` matches ``chart_a['body_lons'][0]`` (Sun_A)."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    sun_rows = dense[dense["body_a"] == 0]
    expected_sun_lon = float(chart_a_paris["body_lons"][0])
    assert np.all(sun_rows["lon_a"] == expected_sun_lon)


def test_chart_asc_propagates_to_body_13(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``lon_a`` for rows where ``body_a == 13`` equals ``chart_a['asc']``."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    asc_rows = dense[dense["body_a"] == 13]
    expected_asc = float(chart_a_paris["asc"])
    assert np.all(asc_rows["lon_a"] == expected_asc)


def test_chart_mc_propagates_to_body_14(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``lon_a`` for rows where ``body_a == 14`` equals ``chart_a['mc']``."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    mc_rows = dense[dense["body_a"] == 14]
    expected_mc = float(chart_a_paris["mc"])
    assert np.all(mc_rows["lon_a"] == expected_mc)


# ---------------------------------------------------------------------------
# F. Sentinel convention (Phase 14 D-06 mirror)
# ---------------------------------------------------------------------------

def test_dense_non_aspected_rows_have_aspect_type_minus_one(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Dense rows where the orb test fails carry ``aspect_type == -1`` sentinel."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    non_aspected = dense[dense["aspect_type"] == -1]
    # At least one non-aspected pair exists for any realistic chart pair.
    assert non_aspected.size > 0
    assert (non_aspected["aspect_type"] == -1).all()


def test_dense_non_aspected_rows_have_orb_nan(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Non-aspected dense rows have ``orb == NaN`` sentinel."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    non_aspected = dense[dense["aspect_type"] == -1]
    assert np.isnan(non_aspected["orb"]).all()


def test_dense_non_aspected_rows_have_orb_limit_nan(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Non-aspected dense rows have ``orb_limit == NaN`` sentinel."""
    dense = calculate_synastry(chart_a_paris, chart_b_nyc, mode="dense")
    non_aspected = dense[dense["aspect_type"] == -1]
    assert np.isnan(non_aspected["orb_limit"]).all()


def test_filtered_rows_never_have_negative_aspect_type(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Filtered rows are guaranteed ``aspect_type >= 0``."""
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert (filtered["aspect_type"] >= 0).all()


# ---------------------------------------------------------------------------
# G. Filtered row order (canonical body-pair order, NOT |orb|)
# ---------------------------------------------------------------------------

def test_filtered_canonical_body_pair_order(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Filtered rows are sorted by ``(body_a * 15 + body_b)`` ascending."""
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    linearised = (
        filtered["body_a"].astype(np.int32) * SYNASTRY_BODY_COUNT
        + filtered["body_b"].astype(np.int32)
    )
    assert np.all(np.diff(linearised) >= 0)


def test_filtered_NOT_orb_ascending(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """Filtered rows are NOT pre-sorted by ``|orb|`` (regression guard).

    Documented rationale: keeping canonical body-pair order is predictable
    for ML / oracle tests. Callers wanting |orb|-ascending should sort
    explicitly with ``result[np.argsort(np.abs(result['orb']))]``. This
    test is a ratchet against well-intentioned future "helpful"
    reorderings.
    """
    filtered = calculate_synastry(chart_a_paris, chart_b_nyc)
    if len(filtered) < 2:
        pytest.skip("not enough rows to test ordering")
    orbs_abs = np.abs(filtered["orb"])
    # Demonstrate that at least one adjacent pair is out of |orb|-ascending order.
    diffs = np.diff(orbs_abs)
    # If the result happened to be perfectly |orb|-ascending purely by accident,
    # the test still permits it (skip) — but for the Paris<->NYC pair the
    # canonical order is verifiably different from |orb| order.
    assert not np.all(diffs >= 0), (
        "filtered rows are |orb|-ascending — implementation may have "
        "introduced a hidden sort, breaking the canonical body-pair order"
    )


# ---------------------------------------------------------------------------
# H. Dtype precision (Pitfall 6 STRENGTHENED ratchet)
# ---------------------------------------------------------------------------

def test_orb_field_is_float32(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``result.dtype['orb']`` is float32 (matches SYNASTRY_DTYPE)."""
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.dtype["orb"] == np.float32


def test_orb_limit_field_is_float32(
    chart_a_paris: np.ndarray, chart_b_nyc: np.ndarray,
) -> None:
    """``result.dtype['orb_limit']`` is float32 (matches SYNASTRY_DTYPE)."""
    result = calculate_synastry(chart_a_paris, chart_b_nyc)
    assert result.dtype["orb_limit"] == np.float32


def test_synastry_orb_limit_f4_bit_exact_all_225_pairs() -> None:
    """``synastry_orb_limit`` returns f4 bit-exact across all 225 cross-pairs (conjunction).

    Proves NO silent f8 upcast in the intermediate computation
    ``(_BODY_ORBS_15[b1] + _BODY_ORBS_15[b2]) / 2.0 * coef * SYNASTRY_FACTOR``.
    Loops over the full 15x15 axis with ``asp=0`` (conjunction, coef=1.0).
    """
    coef = float(_ASPECTS["coef"][0])
    factor = SYNASTRY_FACTOR
    for b1 in range(SYNASTRY_BODY_COUNT):
        for b2 in range(SYNASTRY_BODY_COUNT):
            expected_f4 = np.float32(
                (_BODY_ORBS_15[b1] + _BODY_ORBS_15[b2]) / 2.0
                * np.float32(coef) * np.float32(factor)
            )
            actual = synastry_orb_limit(b1, b2, 0)
            assert float(expected_f4) == actual, (
                f"f4 bit-exact mismatch at (b1={b1}, b2={b2}): "
                f"expected {float(expected_f4)!r}, actual {actual!r}"
            )


# ---------------------------------------------------------------------------
# I. Polar input ratchet (Reykjavik fixture built with polar_fallback='porphyry')
# ---------------------------------------------------------------------------

def test_calculate_synastry_with_polar_chart(
    chart_a_paris: np.ndarray, chart_b_reykjavik: np.ndarray,
) -> None:
    """Synastry against a polar chart (lat 64.15) returns finite ASC/MC contacts.

    The polar_fallback contract lives in the fixture (``polar_fallback='porphyry'``);
    this test asserts synastry output is well-formed, not the chart-computation
    machinery.
    """
    result = calculate_synastry(chart_a_paris, chart_b_reykjavik)
    assert result.size > 0
    dense = calculate_synastry(chart_a_paris, chart_b_reykjavik, mode="dense")
    # ASC/MC longitudes (body_b in {13, 14}) must be finite.
    polar_angle_rows = dense[(dense["body_b"] == 13) | (dense["body_b"] == 14)]
    assert np.isfinite(polar_angle_rows["lon_b"]).all()
