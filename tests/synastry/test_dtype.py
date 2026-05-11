"""SYNASTRY_DTYPE structural tests — field names, dtypes, sentinels, ratchets.

Pure structural assertions on the locked SYNASTRY_DTYPE contract. No chart
computation, no I/O. These tests pin the contract for Plans 16-02..05 to
consume safely; any reorder, addition, or dtype-width drift goes red here.
"""
from __future__ import annotations

import numpy as np

import ketu.synastry
import ketu.synastry.core
from ketu.synastry import SYNASTRY_BODY_COUNT, SYNASTRY_DTYPE


# ---------------------------------------------------------------------------
# SYN-01 — public imports resolve
# ---------------------------------------------------------------------------

def test_public_imports_resolve() -> None:
    """SYN-01: ``from ketu.synastry import …`` exposes the dtype + body-count surface."""
    assert isinstance(SYNASTRY_DTYPE, np.dtype), (
        f"SYNASTRY_DTYPE is not a np.dtype: {type(SYNASTRY_DTYPE)!r}"
    )
    assert isinstance(SYNASTRY_BODY_COUNT, int), (
        f"SYNASTRY_BODY_COUNT is not int: {type(SYNASTRY_BODY_COUNT)!r}"
    )


# ---------------------------------------------------------------------------
# Dtype shape + field name ratchets
# ---------------------------------------------------------------------------

def test_dtype_field_count_eight() -> None:
    """SYNASTRY_DTYPE has exactly 8 fields (Plan 16-01 locked floor)."""
    assert len(SYNASTRY_DTYPE.names) == 8, (
        f"SYNASTRY_DTYPE field count drifted: {len(SYNASTRY_DTYPE.names)}"
    )


def test_dtype_field_names_canonical_order() -> None:
    """SYNASTRY_DTYPE field names in the FROZEN canonical order.

    Any reorder breaks Kala consumers that index positionally; this is the
    contractual heart of Plan 16-01.
    """
    expected = (
        "body_a", "body_b",
        "lon_a", "lon_b",
        "aspect_type", "orb",
        "applying", "orb_limit",
    )
    assert SYNASTRY_DTYPE.names == expected, (
        f"SYNASTRY_DTYPE field order drifted: {SYNASTRY_DTYPE.names}"
    )


# ---------------------------------------------------------------------------
# Per-field dtype ratchets
# ---------------------------------------------------------------------------

def test_dtype_body_a_dtype_int8() -> None:
    """body_a is i1 (axis range [0..14] fits within [-128, 127])."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["body_a"][0] == np.dtype("i1")


def test_dtype_body_b_dtype_int8() -> None:
    """body_b is i1 (axis range [0..14] fits within [-128, 127])."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["body_b"][0] == np.dtype("i1")


def test_dtype_lon_a_dtype_float64() -> None:
    """lon_a is f8 (full precision for [0, 360) longitudes, matching CHART_DTYPE.body_lons)."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["lon_a"][0] == np.dtype("f8")


def test_dtype_lon_b_dtype_float64() -> None:
    """lon_b is f8 (full precision for [0, 360) longitudes, matching CHART_DTYPE.body_lons)."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["lon_b"][0] == np.dtype("f8")


def test_dtype_aspect_type_dtype_int8() -> None:
    """aspect_type is i1 — sentinel ``-1`` must fit; i1 range [-128, 127] OK."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["aspect_type"][0] == np.dtype("i1")


def test_dtype_orb_dtype_float32() -> None:
    """orb is f4 — memory budget halved vs f8; matches CHART_DTYPE.aspect_orbs."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["orb"][0] == np.dtype("f4")


def test_dtype_applying_dtype_bool() -> None:
    """applying is bool (np.bool_)."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["applying"][0] == np.dtype("?")


def test_dtype_orb_limit_dtype_float32() -> None:
    """orb_limit is f4 — matches orb width."""
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    assert fields["orb_limit"][0] == np.dtype("f4")


# ---------------------------------------------------------------------------
# Body-count + itemsize + anti-pattern ratchets
# ---------------------------------------------------------------------------

def test_synastry_body_count_frozen_at_fifteen() -> None:
    """SYNASTRY_BODY_COUNT == 15 — ratchet against accidental Vertex addition pre-v1.3."""
    assert SYNASTRY_BODY_COUNT == 15, (
        f"SYNASTRY_BODY_COUNT drifted: {SYNASTRY_BODY_COUNT}. "
        "Adding bodies (Vertex etc.) is a v1.3 BREAKING change."
    )


def test_dtype_itemsize_pinned() -> None:
    """Itemsize sums to 1+1+8+8+1+4+1+4 = 28 bytes; pins struct padding."""
    # Sum of declared field sizes (struct padding could in theory inflate this
    # on some platforms; numpy structured arrays typically don't pad). Pinning
    # here will catch surprises if numpy ever changes alignment rules.
    expected = 1 + 1 + 8 + 8 + 1 + 4 + 1 + 4  # 28
    assert SYNASTRY_DTYPE.itemsize == expected, (
        f"SYNASTRY_DTYPE itemsize drifted: {SYNASTRY_DTYPE.itemsize} (want {expected})"
    )


def test_can_allocate_empty_array_with_dtype() -> None:
    """Positive sanity: ``np.empty(225, dtype=SYNASTRY_DTYPE)`` shape == (225,)."""
    # 225 = 15 * 15 — full dense mode allocation size.
    arr = np.empty(225, dtype=SYNASTRY_DTYPE)
    assert arr.shape == (225,)
    assert arr.dtype == SYNASTRY_DTYPE


def test_anti_axis_style_no_two_d_subarray() -> None:
    """Anti-axis-style ratchet: no field carries a 2-D subshape.

    Record-style is the locked convention (CONTEXT.md D-rec); a hypothetical
    (15, 15) matrix layout was rejected so that dense + filtered modes share
    one schema. This ratchet ensures the choice survives drift.
    """
    fields = SYNASTRY_DTYPE.fields
    assert fields is not None
    for name in SYNASTRY_DTYPE.names:
        field_dtype = fields[name][0]
        assert field_dtype.shape in ((), ), (
            f"Field {name!r} has a non-scalar shape {field_dtype.shape!r}; "
            "SYNASTRY_DTYPE must stay record-style (no subarray fields)."
        )


def test_dtype_aspect_type_accepts_negative_one_sentinel() -> None:
    """D-06 ratchet: aspect_type round-trips ``-1`` (no aspect, dense-mode sentinel)."""
    arr = np.zeros(3, dtype=SYNASTRY_DTYPE)
    arr["aspect_type"] = np.array([-1, 0, 13], dtype=np.int8)
    assert arr["aspect_type"][0] == -1
    assert arr["aspect_type"][1] == 0
    assert arr["aspect_type"][2] == 13


def test_dtype_orb_accepts_nan_sentinel() -> None:
    """D-06 ratchet: orb round-trips ``NaN`` (no orb, paired with aspect_type=-1)."""
    arr = np.zeros(2, dtype=SYNASTRY_DTYPE)
    arr["orb"] = np.array([np.nan, 1.5], dtype=np.float32)
    assert np.isnan(arr["orb"][0])
    assert arr["orb"][1] == np.float32(1.5)


# ---------------------------------------------------------------------------
# Module docstring ratchets (Phase 13 doc convention)
# ---------------------------------------------------------------------------

def test_core_module_docstring_mentions_why_structured_array() -> None:
    """Plan 16-01 success criterion: core.py docstring carries the 'Why a structured array' rationale."""
    doc = ketu.synastry.core.__doc__
    assert doc is not None, "ketu.synastry.core has no module docstring"
    assert "Why a structured array" in doc, (
        "ketu.synastry.core docstring missing 'Why a structured array' section"
    )
    assert "Why 8 fields" in doc, (
        "ketu.synastry.core docstring missing 'Why 8 fields' rationale "
        "(auto-sufficiency justification for the extra 3 metadata fields)"
    )
