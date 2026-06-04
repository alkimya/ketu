"""DECLA_ASPECT_DTYPE structural tests — field names, dtypes, itemsize, ratchets.

Pure structural assertions on the locked DECLA_ASPECT_DTYPE contract.
No chart computation, no I/O. These tests pin the contract so that any
reorder, addition, or dtype-width drift goes red here.
"""
from __future__ import annotations

import numpy as np

import ketu.declination
from ketu.declination import DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB


# ---------------------------------------------------------------------------
# DECLA-01/02/03 — public imports resolve
# ---------------------------------------------------------------------------

def test_public_imports_resolve() -> None:
    """DECLA-01: ``from ketu.declination import …`` exposes the dtype + constant surface."""
    assert isinstance(DECLA_ASPECT_DTYPE, np.dtype), (
        f"DECLA_ASPECT_DTYPE is not a np.dtype: {type(DECLA_ASPECT_DTYPE)!r}"
    )
    assert DECLA_COEF == 1.0 / 12.0, (
        f"DECLA_COEF is not 1/12: {DECLA_COEF!r}"
    )
    assert MIN_DECL_ORB == 0.5, (
        f"MIN_DECL_ORB is not 0.5: {MIN_DECL_ORB!r}"
    )


# ---------------------------------------------------------------------------
# Dtype shape + field name ratchets
# ---------------------------------------------------------------------------

def test_dtype_field_count_five() -> None:
    """DECLA_ASPECT_DTYPE has exactly 5 fields."""
    assert len(DECLA_ASPECT_DTYPE.names) == 5, (
        f"DECLA_ASPECT_DTYPE field count drifted: {len(DECLA_ASPECT_DTYPE.names)}"
    )


def test_dtype_field_names_canonical_order() -> None:
    """DECLA_ASPECT_DTYPE field names in the FROZEN canonical order.

    Any reorder breaks downstream consumers that index positionally.
    """
    expected = ("body1", "body2", "kind", "gap", "orb")
    assert DECLA_ASPECT_DTYPE.names == expected, (
        f"DECLA_ASPECT_DTYPE field order drifted: {DECLA_ASPECT_DTYPE.names}"
    )


# ---------------------------------------------------------------------------
# Per-field dtype ratchets
# ---------------------------------------------------------------------------

def test_dtype_body1_dtype_int8() -> None:
    """body1 is i1 (axis range [0..13] fits within [-128, 127])."""
    fields = DECLA_ASPECT_DTYPE.fields
    assert fields is not None
    assert fields["body1"][0] == np.dtype("i1")


def test_dtype_body2_dtype_int8() -> None:
    """body2 is i1 (axis range [0..13] fits within [-128, 127])."""
    fields = DECLA_ASPECT_DTYPE.fields
    assert fields is not None
    assert fields["body2"][0] == np.dtype("i1")


def test_dtype_kind_dtype_unicode2() -> None:
    """kind is U2 — holds 'P' (1 char) and 'CP' (2 chars)."""
    fields = DECLA_ASPECT_DTYPE.fields
    assert fields is not None
    assert fields["kind"][0] == np.dtype("U2")


def test_dtype_gap_dtype_float64() -> None:
    """gap is f8 — full precision for declination separation in degrees."""
    fields = DECLA_ASPECT_DTYPE.fields
    assert fields is not None
    assert fields["gap"][0] == np.dtype("f8")


def test_dtype_orb_dtype_float64() -> None:
    """orb is f8 — full precision for derived orb limit in degrees."""
    fields = DECLA_ASPECT_DTYPE.fields
    assert fields is not None
    assert fields["orb"][0] == np.dtype("f8")


def test_dtype_itemsize_pinned() -> None:
    """Itemsize sums to 1+1+8+8+8 = 26 bytes (U2 = 2 UCS-4 codepoints = 8 bytes).

    NumPy stores Unicode as UCS-4: U2 = 2×4 = 8 bytes. Total: 1+1+8+8+8 = 26.
    Pins struct layout for platform consistency.
    """
    expected = 1 + 1 + 8 + 8 + 8  # 26
    assert DECLA_ASPECT_DTYPE.itemsize == expected, (
        f"DECLA_ASPECT_DTYPE itemsize drifted: {DECLA_ASPECT_DTYPE.itemsize} (want {expected})"
    )


def test_can_allocate_empty_array() -> None:
    """Positive sanity: ``np.empty(0, dtype=DECLA_ASPECT_DTYPE)`` shape == (0,)."""
    arr = np.empty(0, dtype=DECLA_ASPECT_DTYPE)
    assert arr.shape == (0,)
    assert arr.dtype == DECLA_ASPECT_DTYPE


# ---------------------------------------------------------------------------
# Module docstring ratchet
# ---------------------------------------------------------------------------

def test_declination_module_docstring_present() -> None:
    """ketu.declination has a module docstring describing the public surface."""
    doc = ketu.declination.__doc__
    assert doc is not None, "ketu.declination has no module docstring"
    assert "find_declination_aspects" in doc, (
        "ketu.declination docstring missing mention of find_declination_aspects"
    )
