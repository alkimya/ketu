"""HOUSES_DTYPE structural tests — field names, shapes, subarray semantics.

Pure structural assertions. No swisseph dependency, no oracle access — these
tests run without any optional deps installed.
"""
from __future__ import annotations

import numpy as np

from ketu.houses import HOUSES_DTYPE, HighLatitudeError


def test_dtype_field_names_match_spec() -> None:
    """HOU-05: dtype has the 9 declared fields in declared order."""
    expected = ("jd", "lat", "lon", "system", "cusps", "asc", "mc", "armc", "vertex")
    assert HOUSES_DTYPE.names == expected, (
        f"HOUSES_DTYPE field names drifted: {HOUSES_DTYPE.names}"
    )


def test_dtype_cusps_is_subarray_of_length_12() -> None:
    """cusps is a (12,) subarray field — central HOU-05 invariant."""
    fields = HOUSES_DTYPE.fields
    assert fields is not None
    cusps_dtype = fields["cusps"][0]
    # Subarray fields expose .shape on the field dtype (NumPy 1.20+ semantics)
    assert cusps_dtype.shape == (12,), (
        f"cusps subarray shape drifted: {cusps_dtype.shape}"
    )


def test_dtype_supports_vectorized_construction() -> None:
    """Outer shape (N,) -> cusps field accessible as (N, 12)."""
    arr = np.zeros(3, dtype=HOUSES_DTYPE)
    assert arr["cusps"].shape == (3, 12)
    # Assignment round-trip
    arr["cusps"][0] = np.arange(12, dtype=np.float64)
    assert arr["cusps"][0, 5] == 5.0


def test_dtype_string_field_capacity() -> None:
    """system field is U16 — fits all v1.2 system names including 'regiomontanus' (13 chars)."""
    for name in (
        "placidus", "koch", "porphyry",
        "whole_sign", "equal", "regiomontanus",
    ):
        arr = np.zeros(1, dtype=HOUSES_DTYPE)
        arr["system"][0] = name
        assert arr["system"][0] == name, (
            f"system field truncated {name!r} to {arr['system'][0]!r}; "
            "did the U16 bump regress?"
        )


def test_dtype_scalar_zero_dim_construction() -> None:
    """0-d HOUSES_DTYPE element exposes cusps as a length-12 array."""
    elem = np.zeros((), dtype=HOUSES_DTYPE)
    assert elem["cusps"].shape == (12,)
    elem["asc"] = 26.77
    assert elem["asc"] == 26.77


def test_high_latitude_error_is_value_error_subclass() -> None:
    """HighLatitudeError carries lat/system/polar_lat and subclasses ValueError."""
    e = HighLatitudeError(75.0, "placidus", 66.5616)
    assert isinstance(e, ValueError)
    assert e.lat == 75.0
    assert e.system == "placidus"
    assert e.polar_lat == 66.5616
    msg = str(e)
    assert "75.0000" in msg
    assert "placidus" in msg
    assert "porphyry" in msg  # Hint to caller about polar_fallback option
