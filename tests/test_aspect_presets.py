"""Unit tests for ketu.aspects.presets — preset constants and resolver.

Coverage:
- Three preset constants (CLASSICAL, TRADITIONAL, EXTENDED): shape, dtype,
  population sums, frozen-mutation guard, structural relationships.
- Resolver happy paths: None default, str preset (case-insensitive), Sequence
  of names, Sequence of indices, np.ndarray bool passthrough, np.ndarray int
  indices.
- Resolver error paths: unknown preset, unknown name, out-of-range index,
  wrong-length boolean mask, invalid item types.
- Custom default behavior.

Phase 9 plan 09-02. Targets ASP-02 (presets exposed), ASP-04 foundation
(default = CLASSICAL via resolver), ASP-05 foundation (single-call resolver
returns mask).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, List

import numpy as np
import pytest

from ketu.aspects import (
    calculate_aspects,
    calculate_aspects_batch,
    calculate_aspects_vectorized,
    find_aspects_between_dates,
)
from ketu.aspects.presets import (
    CLASSICAL,
    EXTENDED,
    TRADITIONAL,
    resolve_aspect_set,
)
from ketu.calculations import utc_to_julian
from ketu.core import aspects as _CORE_ASPECTS

# ---------------------------------------------------------------------------
# Integration test constants — canonical 0-13 i_asp index sets per preset
# ---------------------------------------------------------------------------

CLASSICAL_INDICES = {0, 4, 7, 9, 13}  # 5 majors
TRADITIONAL_INDICES = {0, 1, 4, 7, 9, 11, 13}  # 7
NON_CLASSICAL_INDICES = set(range(14)) - CLASSICAL_INDICES
NON_TRADITIONAL_INDICES = set(range(14)) - TRADITIONAL_INDICES

# CLASSICAL aspect names (find_aspects_between_dates returns aspect_name str,
# not an i_asp index)
CLASSICAL_NAMES = {"Conjunction", "Sextile", "Square", "Trine", "Opposition"}

# ---------------------------------------------------------------------------
# Constants tests
# ---------------------------------------------------------------------------


def test_classical_mask_shape_and_sum() -> None:
    """CLASSICAL has shape (14,), bool dtype, and 5 True entries at expected indices."""
    assert CLASSICAL.shape == (14,)
    assert CLASSICAL.dtype == np.bool_
    assert CLASSICAL.sum() == 5
    expected_indices = [0, 4, 7, 9, 13]
    for i in expected_indices:
        assert CLASSICAL[i], f"CLASSICAL[{i}] should be True"
    # All other positions must be False
    for i in range(14):
        if i not in expected_indices:
            assert not CLASSICAL[i], f"CLASSICAL[{i}] should be False"


def test_traditional_mask_shape_and_sum() -> None:
    """TRADITIONAL has shape (14,), bool dtype, and 7 True entries at expected indices."""
    assert TRADITIONAL.shape == (14,)
    assert TRADITIONAL.dtype == np.bool_
    assert TRADITIONAL.sum() == 7
    expected_indices = [0, 1, 4, 7, 9, 11, 13]
    for i in expected_indices:
        assert TRADITIONAL[i], f"TRADITIONAL[{i}] should be True"
    for i in range(14):
        if i not in expected_indices:
            assert not TRADITIONAL[i], f"TRADITIONAL[{i}] should be False"


def test_extended_mask_shape_and_sum() -> None:
    """EXTENDED has shape (14,), bool dtype, and all 14 entries True."""
    assert EXTENDED.shape == (14,)
    assert EXTENDED.dtype == np.bool_
    assert EXTENDED.sum() == 14
    assert EXTENDED.all()


def test_classical_is_frozen() -> None:
    """Mutating CLASSICAL raises ValueError (writeable=False)."""
    with pytest.raises(ValueError):
        CLASSICAL[0] = False


def test_traditional_is_frozen() -> None:
    """Mutating TRADITIONAL raises ValueError (writeable=False)."""
    with pytest.raises(ValueError):
        TRADITIONAL[0] = False


def test_extended_is_frozen() -> None:
    """Mutating EXTENDED raises ValueError (writeable=False)."""
    with pytest.raises(ValueError):
        EXTENDED[0] = False


def test_classical_subset_of_traditional() -> None:
    """CLASSICAL is a strict subset of TRADITIONAL (every CLASSICAL bit is in TRADITIONAL)."""
    # CLASSICAL & TRADITIONAL == CLASSICAL means every True in CLASSICAL is True in TRADITIONAL
    assert np.array_equal(CLASSICAL & TRADITIONAL, CLASSICAL)
    # And TRADITIONAL is strictly larger
    assert TRADITIONAL.sum() > CLASSICAL.sum()


def test_traditional_subset_of_extended() -> None:
    """TRADITIONAL is a strict subset of EXTENDED."""
    assert np.array_equal(TRADITIONAL & EXTENDED, TRADITIONAL)
    assert EXTENDED.sum() > TRADITIONAL.sum()


# ---------------------------------------------------------------------------
# Resolver — happy paths
# ---------------------------------------------------------------------------


def test_resolve_none_returns_classical() -> None:
    """resolve_aspect_set(None) returns CLASSICAL (default behavior, ASP-04)."""
    result = resolve_aspect_set(None)
    np.testing.assert_array_equal(result, CLASSICAL)


def test_resolve_classical_string_lowercase() -> None:
    """resolve_aspect_set('classical') returns CLASSICAL."""
    result = resolve_aspect_set("classical")
    np.testing.assert_array_equal(result, CLASSICAL)


@pytest.mark.parametrize("name", ["Classical", "CLASSICAL", "classIcal", "ClAsSiCaL"])
def test_resolve_classical_string_mixed_case(name: str) -> None:
    """Preset name lookup is case-insensitive."""
    result = resolve_aspect_set(name)
    np.testing.assert_array_equal(result, CLASSICAL)


def test_resolve_traditional_string() -> None:
    """resolve_aspect_set('traditional') returns TRADITIONAL."""
    result = resolve_aspect_set("traditional")
    np.testing.assert_array_equal(result, TRADITIONAL)


def test_resolve_extended_string() -> None:
    """resolve_aspect_set('extended') returns EXTENDED (legacy v1.0 default)."""
    result = resolve_aspect_set("extended")
    np.testing.assert_array_equal(result, EXTENDED)


@pytest.mark.parametrize(
    "names,expected_indices",
    [
        (["Conjunction"], [0]),
        (["Trine", "Square"], [7, 9]),
        (
            ["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
            [0, 4, 7, 9, 13],
        ),
        (["Semi-sextile", "Quincunx"], [1, 11]),
    ],
)
def test_resolve_name_list_parametrized(
    names: List[str], expected_indices: List[int]
) -> None:
    """A Sequence[str] of aspect names resolves to a mask with those indices set."""
    expected = np.zeros(14, dtype=np.bool_)
    expected[expected_indices] = True
    result = resolve_aspect_set(names)
    np.testing.assert_array_equal(result, expected)


def test_resolve_index_list_yields_classical() -> None:
    """[0, 4, 7, 9, 13] (list of int) resolves to CLASSICAL mask."""
    result = resolve_aspect_set([0, 4, 7, 9, 13])
    np.testing.assert_array_equal(result, CLASSICAL)


def test_resolve_index_tuple_yields_classical() -> None:
    """(0, 4, 7, 9, 13) (tuple of int) resolves to CLASSICAL mask."""
    result = resolve_aspect_set((0, 4, 7, 9, 13))
    np.testing.assert_array_equal(result, CLASSICAL)


def test_resolve_bool_mask_passthrough() -> None:
    """A length-14 bool ndarray is returned unchanged (passthrough)."""
    mask = np.zeros(14, dtype=np.bool_)
    mask[0] = True
    mask[7] = True
    result = resolve_aspect_set(mask)
    np.testing.assert_array_equal(result, mask)


def test_resolve_bool_mask_passthrough_full() -> None:
    """A full-True length-14 bool ndarray returns equivalent of EXTENDED."""
    mask = np.ones(14, dtype=np.bool_)
    result = resolve_aspect_set(mask)
    np.testing.assert_array_equal(result, mask)
    assert result.sum() == 14


def test_resolve_int_ndarray_indices() -> None:
    """np.ndarray of int indices resolves to a mask with those positions True."""
    indices = np.array([0, 13], dtype=np.intp)
    result = resolve_aspect_set(indices)
    expected = np.zeros(14, dtype=np.bool_)
    expected[0] = True
    expected[13] = True
    np.testing.assert_array_equal(result, expected)


def test_resolve_int_ndarray_yields_classical() -> None:
    """np.ndarray of CLASSICAL indices resolves to CLASSICAL mask."""
    indices = np.array([0, 4, 7, 9, 13], dtype=np.intp)
    result = resolve_aspect_set(indices)
    np.testing.assert_array_equal(result, CLASSICAL)


def test_resolve_mixed_str_and_int_sequence() -> None:
    """A Sequence with mixed str and int items is resolved per-item."""
    spec = ["Conjunction", 7, "Trine", 13]  # 0, 7, 9, 13
    expected = np.zeros(14, dtype=np.bool_)
    expected[[0, 7, 9, 13]] = True
    result = resolve_aspect_set(spec)
    np.testing.assert_array_equal(result, expected)


# ---------------------------------------------------------------------------
# Resolver — error paths
# ---------------------------------------------------------------------------


def test_resolve_unknown_preset_raises_with_valid_options() -> None:
    """Unknown preset name raises ValueError listing all three valid presets."""
    with pytest.raises(ValueError, match="unknown aspect preset"):
        resolve_aspect_set("unknown_preset")
    # Confirm the message includes the valid names
    try:
        resolve_aspect_set("nope")
    except ValueError as e:
        msg = str(e)
        assert "classical" in msg
        assert "traditional" in msg
        assert "extended" in msg


def test_resolve_unknown_aspect_name_raises() -> None:
    """Unknown aspect name in a list raises ValueError with informative message."""
    with pytest.raises(ValueError, match="unknown aspect name"):
        resolve_aspect_set(["NotARealAspect"])


def test_resolve_unknown_name_lists_valid_options() -> None:
    """When an aspect name is unknown, the error lists all 14 decoded names."""
    try:
        resolve_aspect_set(["FakeAspect"])
    except ValueError as e:
        msg = str(e)
        # All 14 canonical aspect names must appear in the message
        for canonical in _CORE_ASPECTS["name"]:
            assert canonical.decode() in msg, (
                f"missing {canonical.decode()!r} in error msg"
            )


@pytest.mark.parametrize("bad_index", [14, 15, 100, -1, -10])
def test_resolve_out_of_range_index_raises(bad_index: int) -> None:
    """Indices outside [0, 14) raise ValueError with 'out of range'."""
    with pytest.raises(ValueError, match="out of range"):
        resolve_aspect_set([bad_index])


@pytest.mark.parametrize("bad_index", [14, 100, -1])
def test_resolve_out_of_range_index_in_ndarray_raises(bad_index: int) -> None:
    """Out-of-range indices in an int np.ndarray raise ValueError."""
    arr = np.array([0, bad_index], dtype=np.intp)
    with pytest.raises(ValueError, match="out of range"):
        resolve_aspect_set(arr)


def test_resolve_multidim_int_ndarray_raises() -> None:
    """A 2-D int ndarray raises ValueError mentioning '1-D'."""
    arr = np.array([[0, 4], [7, 13]], dtype=np.intp)
    with pytest.raises(ValueError, match="1-D"):
        resolve_aspect_set(arr)


@pytest.mark.parametrize("bad_length", [13, 15, 0, 1, 28])
def test_resolve_wrong_length_bool_mask_raises(bad_length: int) -> None:
    """Boolean ndarray with shape != (14,) raises ValueError mentioning shape."""
    bad_mask = np.zeros(bad_length, dtype=np.bool_)
    with pytest.raises(ValueError, match="shape"):
        resolve_aspect_set(bad_mask)


@pytest.mark.parametrize("bad_item", [1.5, None, object(), 3.14, b"bytes"])
def test_resolve_invalid_item_type_raises(bad_item: Any) -> None:
    """Sequence items that are not str or int raise ValueError 'invalid aspect spec item'."""
    with pytest.raises(ValueError, match="invalid aspect spec item"):
        resolve_aspect_set([bad_item])


def test_resolve_bool_in_sequence_rejected() -> None:
    """Bool items in a Sequence are rejected (not treated as int) to prevent silent bugs."""
    # Without this guard, [True, False, ...] would resolve to indices [1, 0, ...],
    # which is almost certainly a user mistake.
    with pytest.raises(ValueError, match="invalid aspect spec item"):
        resolve_aspect_set([True, False])


# ---------------------------------------------------------------------------
# Custom default behavior
# ---------------------------------------------------------------------------


def test_resolve_with_custom_default_extended() -> None:
    """resolve_aspect_set(None, default=EXTENDED) returns EXTENDED."""
    result = resolve_aspect_set(None, default=EXTENDED)
    np.testing.assert_array_equal(result, EXTENDED)


def test_resolve_with_custom_default_traditional() -> None:
    """resolve_aspect_set(None, default=TRADITIONAL) returns TRADITIONAL."""
    result = resolve_aspect_set(None, default=TRADITIONAL)
    np.testing.assert_array_equal(result, TRADITIONAL)


def test_resolve_with_default_unused_when_spec_provided() -> None:
    """Custom default is ignored when spec is non-None."""
    # Pass default=EXTENDED but ask for "classical" — must return CLASSICAL
    result = resolve_aspect_set("classical", default=EXTENDED)
    np.testing.assert_array_equal(result, CLASSICAL)


# ---------------------------------------------------------------------------
# Output mask invariants
# ---------------------------------------------------------------------------


def test_resolved_mask_is_length_14() -> None:
    """Every resolver path returns a length-14 mask."""
    for spec in [
        None,
        "classical",
        "traditional",
        "extended",
        ["Conjunction"],
        [0, 4],
        np.array([True] * 14, dtype=np.bool_),
        np.array([0, 7], dtype=np.intp),
    ]:
        result = resolve_aspect_set(spec)
        assert result.shape == (14,), f"shape mismatch for spec {spec!r}"
        assert result.dtype == np.bool_, f"dtype mismatch for spec {spec!r}"


def test_resolved_preset_masks_are_frozen() -> None:
    """Returned preset masks remain frozen (cannot be mutated)."""
    result = resolve_aspect_set("classical")
    with pytest.raises(ValueError):
        result[0] = False


def test_resolved_indices_mask_is_frozen() -> None:
    """Mask returned from index-list resolution is frozen."""
    result = resolve_aspect_set([0, 7])
    with pytest.raises(ValueError):
        result[0] = False


# ---------------------------------------------------------------------------
# ASP-07 Integration tests — public aspect APIs honor the preset
# ---------------------------------------------------------------------------


class TestAspectPresetsIntegration:
    """ASP-07: integration tests verify CLASSICAL/TRADITIONAL/EXTENDED defaults
    propagate correctly through all public aspect APIs (calculator family +
    find_aspects_between_dates) and never leak non-set aspects into results."""

    def setup_method(self) -> None:
        self.jd = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.jd_array = np.array(
            [
                utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i))
                for i in range(7)
            ]
        )
        # Wide-enough window for find_aspects_between_dates to find SOME aspects
        # (Sun-Moon hits every major aspect at least once per lunar cycle).
        self.jd_window_start = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
        self.jd_window_end = utc_to_julian(datetime(2025, 1, 30, tzinfo=timezone.utc))

    def test_calculate_aspects_classical_no_leak(self) -> None:
        """ASP-07: calculate_aspects(jd, aspects=CLASSICAL) returns no row with non-classical i_asp."""
        result = calculate_aspects(self.jd, aspects=CLASSICAL)
        leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
        assert not leaked, f"CLASSICAL preset leaked non-classical i_asp: {leaked}"

    def test_calculate_aspects_vectorized_classical_no_leak(self) -> None:
        """ASP-07: calculate_aspects_vectorized(jd, aspects=CLASSICAL) returns no non-classical i_asp."""
        result = calculate_aspects_vectorized(self.jd, aspects=CLASSICAL)
        leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
        assert not leaked, f"CLASSICAL preset leaked non-classical i_asp: {leaked}"

    def test_calculate_aspects_batch_classical_no_leak(self) -> None:
        """ASP-07: calculate_aspects_batch(jd_array, aspects=CLASSICAL) returns no non-classical i_asp on any date."""
        results_per_date = calculate_aspects_batch(self.jd_array, aspects=CLASSICAL)
        all_leaked: set[int] = set()
        for result in results_per_date:
            if len(result):
                leaked = set(int(x) for x in result["i_asp"]) & NON_CLASSICAL_INDICES
                if leaked:
                    all_leaked |= leaked
        assert not all_leaked, f"CLASSICAL leaked non-classical i_asp across batch: {all_leaked}"

    def test_find_aspects_between_dates_classical_no_leak(self) -> None:
        """ASP-07 / Blocker-1: find_aspects_between_dates(..., aspects=CLASSICAL) returns no
        row whose aspect_name is outside the 5-major set."""
        rows = find_aspects_between_dates(
            self.jd_window_start,
            self.jd_window_end,
            body1=0,
            body2=1,  # Sun-Moon — frequent aspects
            aspects=CLASSICAL,
        )
        # Each row is (jd, b1, b2, aspect_name, aspect_angle)
        names = {row[3] for row in rows}
        leaked = names - CLASSICAL_NAMES
        assert not leaked, f"find_aspects_between_dates with CLASSICAL leaked: {leaked}"

    def test_find_aspects_between_dates_default_equals_classical(self) -> None:
        """ASP-04 / Blocker-1: find_aspects_between_dates with no aspects= kwarg behaves
        identically to aspects=CLASSICAL."""
        r_default = find_aspects_between_dates(
            self.jd_window_start, self.jd_window_end, body1=0, body2=1
        )
        r_classical = find_aspects_between_dates(
            self.jd_window_start,
            self.jd_window_end,
            body1=0,
            body2=1,
            aspects=CLASSICAL,
        )
        assert r_default == r_classical, (
            "find_aspects_between_dates default diverges from explicit aspects=CLASSICAL"
        )

    def test_find_aspects_between_dates_extended_superset(self) -> None:
        """ASP-07 / Blocker-1: aspects=EXTENDED returns a SUPERSET of CLASSICAL rows
        (every CLASSICAL row also appears in EXTENDED — find_aspects_between_dates does
        NOT use first-match-wins; it iterates each angle independently)."""
        r_classical = find_aspects_between_dates(
            self.jd_window_start,
            self.jd_window_end,
            body1=0,
            body2=1,
            aspects=CLASSICAL,
        )
        r_extended = find_aspects_between_dates(
            self.jd_window_start,
            self.jd_window_end,
            body1=0,
            body2=1,
            aspects=EXTENDED,
        )
        # Every CLASSICAL row must appear in EXTENDED:
        cl_set = set(r_classical)
        ext_set = set(r_extended)
        missing = cl_set - ext_set
        assert not missing, (
            f"EXTENDED missing CLASSICAL rows that should appear: {missing}"
        )
        # Sanity: EXTENDED should have at least as many rows as CLASSICAL
        assert len(r_extended) >= len(r_classical), (
            f"EXTENDED ({len(r_extended)}) should have >= CLASSICAL ({len(r_classical)}) rows"
        )

    def test_default_equals_classical(self) -> None:
        """ASP-04: aspects=None default behaves identically to aspects=CLASSICAL on calculate_aspects."""
        r_default = calculate_aspects(self.jd)
        r_classical = calculate_aspects(self.jd, aspects=CLASSICAL)

        # Sort by (body1, body2, i_asp, orb) tuple for stable comparison
        def keyed(arr: Any) -> list[tuple[int, int, int, float]]:
            return sorted(
                (int(r["body1"]), int(r["body2"]), int(r["i_asp"]), float(r["orb"]))
                for r in arr
            )

        assert keyed(r_default) == keyed(r_classical), (
            "default (aspects=None) result diverges from explicit aspects=CLASSICAL"
        )

    def test_traditional_no_leak(self) -> None:
        """ASP-07: TRADITIONAL preset returns no row outside {0,1,4,7,9,11,13}."""
        result = calculate_aspects_vectorized(self.jd, aspects=TRADITIONAL)
        leaked = set(int(x) for x in result["i_asp"]) & NON_TRADITIONAL_INDICES
        assert not leaked, f"TRADITIONAL preset leaked: {leaked}"

    def test_classical_results_use_canonical_iasp(self) -> None:
        """ASP-05/Pitfall 1: i_asp emitted under CLASSICAL is the canonical 0-13 index,
        NOT a position 0..4 within the filtered subset. Verifies Kala contract."""
        result = calculate_aspects_vectorized(self.jd, aspects=CLASSICAL)
        if len(result):
            # All emitted i_asp must be in CLASSICAL_INDICES (subset of {0,4,7,9,13}).
            # If renumbered to subset positions, we'd see {0,1,2,3,4} instead.
            emitted = set(int(x) for x in result["i_asp"])
            assert emitted <= CLASSICAL_INDICES, (
                f"i_asp not canonical — got {emitted}, "
                f"expected subset of {CLASSICAL_INDICES} (0,4,7,9,13). "
                f"Renumbering bug per RESEARCH.md Pitfall 1."
            )
