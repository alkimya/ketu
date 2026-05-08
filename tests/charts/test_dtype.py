"""CHART_DTYPE structural tests — field names, shapes, sentinels, ratchets.

Pure structural assertions. No swisseph dependency, no oracle access — these
tests run without any optional deps installed and pin the CHART_DTYPE
contract for plans 14-02..05 to consume safely.

The ``compute_chart`` stub guard was removed by plan 14-02 when the function
was wired (positions + houses + sentinel aspect block); the ``is_day_chart``
stub guard was removed by plan 14-04 when the sect helper was wired (sunrise
inclusive D-13, polar-safe via internal Porphyry fallback D-15). Behavioural
tests for these public functions live in dedicated test files.
"""
from __future__ import annotations

import inspect
import sys

import numpy as np
import pytest

import ketu.charts
import ketu.charts.api
import ketu.charts.core
from ketu.charts import CHART_DTYPE, compute_chart, is_day_chart


# ---------------------------------------------------------------------------
# CHART-01 — public imports resolve
# ---------------------------------------------------------------------------

def test_public_imports_resolve() -> None:
    """CHART-01: ``from ketu.charts import …`` exposes the locked surface."""
    assert isinstance(CHART_DTYPE, np.dtype), (
        f"CHART_DTYPE is not a np.dtype: {type(CHART_DTYPE)!r}"
    )
    assert callable(compute_chart), "compute_chart is not callable"
    assert callable(is_day_chart), "is_day_chart is not callable"


# ---------------------------------------------------------------------------
# CHART-02 — dtype shape, field names, subarray semantics, sentinels
# ---------------------------------------------------------------------------

def test_dtype_has_expected_field_names() -> None:
    """CHART-02: 14 fields in canonical order (metadata -> bodies -> houses -> aspects)."""
    expected = (
        "jd", "lat", "lon", "system",
        "body_lons", "body_lats", "body_speeds",
        "cusps", "asc", "mc", "armc", "vertex",
        "aspect_matrix", "aspect_orbs",
    )
    assert CHART_DTYPE.names == expected, (
        f"CHART_DTYPE field names drifted: {CHART_DTYPE.names}"
    )


@pytest.mark.parametrize(
    ("name", "expected_shape"),
    [
        ("body_lons",     (13,)),
        ("body_lats",     (13,)),
        ("body_speeds",   (13,)),
        ("cusps",         (12,)),
        ("aspect_matrix", (13, 13)),
        ("aspect_orbs",   (13, 13)),
    ],
)
def test_dtype_subarray_shapes(name: str, expected_shape: tuple) -> None:
    """CHART-02: subarray fields carry their pinned axis shapes."""
    fields = CHART_DTYPE.fields
    assert fields is not None
    assert fields[name][0].shape == expected_shape, (
        f"{name} subarray shape drifted: {fields[name][0].shape}"
    )


@pytest.mark.parametrize(
    ("name", "expected_kind", "expected_itemsize"),
    [
        # f8 scalar fields
        ("jd",          "f", 8),
        ("lat",         "f", 8),
        ("lon",         "f", 8),
        ("asc",         "f", 8),
        ("mc",          "f", 8),
        ("armc",        "f", 8),
        ("vertex",      "f", 8),
        # f8 subarray fields (kind/itemsize on the BASE dtype)
        ("body_lons",   "f", 8),
        ("body_lats",   "f", 8),
        ("body_speeds", "f", 8),
        ("cusps",       "f", 8),
        # U10
        ("system",        "U", 40),  # U10 -> 10 codepoints * 4 bytes UCS-4
        # i1 / f4 aspect block
        ("aspect_matrix", "i", 1),
        ("aspect_orbs",   "f", 4),
    ],
)
def test_dtype_scalar_field_kinds(
    name: str, expected_kind: str, expected_itemsize: int,
) -> None:
    """CHART-02: each field has the pinned kind and itemsize."""
    fields = CHART_DTYPE.fields
    assert fields is not None
    field_dtype = fields[name][0]
    base = field_dtype.base  # base dtype for both scalar and subarray fields
    assert base.kind == expected_kind, (
        f"{name} kind drifted: {base.kind!r} (want {expected_kind!r})"
    )
    assert base.itemsize == expected_itemsize, (
        f"{name} itemsize drifted: {base.itemsize} (want {expected_itemsize})"
    )


def test_dtype_supports_vectorized_construction() -> None:
    """Outer shape (N,) yields the expected per-field broadcast shapes."""
    arr = np.zeros(5, dtype=CHART_DTYPE)
    assert arr.shape == (5,)
    assert arr["body_lons"].shape == (5, 13)
    assert arr["body_lats"].shape == (5, 13)
    assert arr["body_speeds"].shape == (5, 13)
    assert arr["cusps"].shape == (5, 12)
    assert arr["aspect_matrix"].shape == (5, 13, 13)
    assert arr["aspect_orbs"].shape == (5, 13, 13)
    # Round-trip a scalar assignment for sanity.
    arr["asc"][2] = 123.456
    assert arr["asc"][2] == pytest.approx(123.456)


def test_dtype_scalar_zero_dim_construction() -> None:
    """0-d CHART_DTYPE element exposes its subarrays at native shape."""
    elem = np.zeros((), dtype=CHART_DTYPE)
    assert elem["body_lons"].shape == (13,)
    assert elem["body_lats"].shape == (13,)
    assert elem["body_speeds"].shape == (13,)
    assert elem["cusps"].shape == (12,)
    assert elem["aspect_matrix"].shape == (13, 13)
    assert elem["aspect_orbs"].shape == (13, 13)


def test_dtype_string_field_capacity() -> None:
    """``system`` is U10: fits 'placidus', 'porphyry', 'whole_sign'; truncates beyond 10 chars."""
    # Standard names fit cleanly.
    for name in ("placidus", "koch", "porphyry", "whole_sign"):
        arr = np.zeros(1, dtype=CHART_DTYPE)
        arr["system"][0] = name
        assert arr["system"][0] == name, (
            f"U10 should accept {name!r} round-trip"
        )
    # Names longer than 10 codepoints are truncated to 10 (NumPy U10 semantics).
    arr = np.zeros(1, dtype=CHART_DTYPE)
    arr["system"][0] = "regiomontanus"  # 13 codepoints > 10
    assert arr["system"][0] == "regiomonta", (
        f"U10 truncation drifted: {arr['system'][0]!r}"
    )


def test_dtype_aspect_matrix_accepts_negative_one_sentinel() -> None:
    """D-06 ratchet: aspect_matrix is i1 and round-trips ``-1`` (no aspect)."""
    arr = np.zeros(3, dtype=CHART_DTYPE)
    sentinel = np.full((3, 13, 13), -1, dtype=np.int8)
    arr["aspect_matrix"] = sentinel
    assert (arr["aspect_matrix"] == -1).all(), (
        "aspect_matrix sentinel -1 round-trip failed"
    )
    # Canonical aspect indices 0..13 must also round-trip.
    arr["aspect_matrix"][0, 0, 1] = 13  # opposition index
    assert arr["aspect_matrix"][0, 0, 1] == 13


def test_dtype_aspect_orbs_accepts_nan_sentinel() -> None:
    """D-06 ratchet: aspect_orbs is f4 and round-trips ``NaN`` (no orb)."""
    arr = np.zeros(3, dtype=CHART_DTYPE)
    sentinel = np.full((3, 13, 13), np.nan, dtype=np.float32)
    arr["aspect_orbs"] = sentinel
    assert np.isnan(arr["aspect_orbs"]).all(), (
        "aspect_orbs sentinel NaN round-trip failed"
    )


# ---------------------------------------------------------------------------
# Module-level ratchets
# ---------------------------------------------------------------------------

def test_dtype_module_docstring_mentions_why_structured_array() -> None:
    """Success criterion 14.5: core.py docstring carries the 'Why a structured array' rationale."""
    doc = ketu.charts.core.__doc__
    assert doc is not None, "ketu.charts.core has no module docstring"
    assert "Why a structured array" in doc, (
        "ketu.charts.core docstring missing the 'Why a structured array' "
        "section required by success criterion 14.5"
    )


def test_dtype_no_dataclass_chart_in_core() -> None:
    """Anti-pattern ratchet (PATTERNS § 8.1): no ``Chart`` dataclass in core.py."""
    assert not hasattr(ketu.charts.core, "Chart"), (
        "ketu.charts.core should NOT define a `Chart` dataclass — Option A "
        "ships dtype-only (CYCLE_DTYPE/CycleState double source-of-truth "
        "is the anti-pattern we are not propagating)."
    )
    # No user-defined classes in core.py at all (BaseException subclasses
    # excepted — currently there are none, but the ratchet allows for a
    # future HighLatitudeError re-export if we ever change our mind).
    user_classes = [
        (name, obj)
        for name, obj in inspect.getmembers(ketu.charts.core, inspect.isclass)
        if obj.__module__ == "ketu.charts.core"
        and not (isinstance(obj, type) and issubclass(obj, BaseException))
    ]
    assert not user_classes, (
        f"ketu.charts.core should be dtype-only; found user classes: "
        f"{[name for name, _ in user_classes]}"
    )


def test_no_runtime_swisseph_import() -> None:
    """AGPL boundary ratchet: ``import ketu.charts`` must not pull swisseph in."""
    # Re-import for symmetry with the houses test (already imported at
    # module top, but the assertion is on names exposed by ketu.charts.*).
    import ketu.charts  # noqa: F401
    import ketu.charts.api  # noqa: F401
    import ketu.charts.core  # noqa: F401
    for mod_name, mod in list(sys.modules.items()):
        if mod_name.startswith("ketu.charts") and mod is not None:
            names = [
                n for n in dir(mod)
                if n.startswith("swe_") or n == "swisseph" or n == "swe"
            ]
            assert not names, (
                f"{mod_name} unexpectedly exposes swisseph-related "
                f"names: {names}"
            )


