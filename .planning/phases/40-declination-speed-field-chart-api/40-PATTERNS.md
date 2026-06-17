# Phase 40: Declination Speed Field & Chart API — Pattern Map

**Mapped:** 2026-06-17
**Files analyzed:** 7 modified + new test additions
**Analogs found:** 7 / 7 (all have exact or role-match analogs in the live codebase)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `ketu/charts/core.py` | model/dtype | CRUD | `ketu/charts/core.py` lines 95-111 (body_decl addition) | exact |
| `ketu/charts/api.py` (compute_chart) | service | transform | `ketu/charts/api.py` lines 379-394 (body_decl block) | exact |
| `ketu/charts/api.py` (helper) | utility | transform | `ketu/charts/api.py` lines 406-553 (is_day_chart) | exact |
| `ketu/calculations.py` | utility/config | — | `ketu/calculations.py` lines 495-555 (declination_velocity / is_ascending_declination) | exact |
| `ketu/composite/api.py` | service | transform | `ketu/composite/api.py` lines 252-266 (body_decl composite derivation) | exact |
| `ketu/synastry/api.py` | service | transform | (no change — verify only) | exact |
| `tests/charts/test_dtype.py` | test | — | `tests/charts/test_dtype.py` lines 56-153 (body_decl ratchet entries) | exact |

---

## Pattern Assignments

### `ketu/charts/core.py` — add `body_decl_speed` field to CHART_DTYPE

**Analog:** `ketu/charts/core.py` lines 95-111 — the v1.5 `body_decl` addition

**Current CHART_DTYPE definition** (lines 95-111 — the block to extend):
```python
CHART_DTYPE: np.dtype = np.dtype([
    ("jd",            "f8"),
    ("lat",           "f8"),
    ("lon",           "f8"),
    ("system",        "U10"),
    ("body_lons",     "f8", (14,)),
    ("body_lats",     "f8", (14,)),
    ("body_speeds",   "f8", (14,)),
    ("body_decl",     "f8", (14,)),
    ("cusps",         "f8", (12,)),
    ("asc",           "f8"),
    ("mc",            "f8"),
    ("armc",          "f8"),
    ("vertex",        "f8"),
    ("aspect_matrix", "i1", (14, 14)),
    ("aspect_orbs",   "f4", (14, 14)),
])
```

**Pattern to mirror:** Insert `("body_decl_speed", "f8", (14,))` immediately after
`("body_decl", "f8", (14,))` at line 103. Same tuple shape, same dtype code `"f8"`,
same body axis `(14,)`. The comment header at lines 90-94 documents the additive
pattern and the Kala positional-offset impact — extend it to mention v1.8
`body_decl_speed`.

**Target layout after change** (field 8 is new, 15 → 16 fields total):
```python
CHART_DTYPE: np.dtype = np.dtype([
    ("jd",              "f8"),
    ("lat",             "f8"),
    ("lon",             "f8"),
    ("system",          "U10"),
    ("body_lons",       "f8", (14,)),
    ("body_lats",       "f8", (14,)),
    ("body_speeds",     "f8", (14,)),
    ("body_decl",       "f8", (14,)),
    ("body_decl_speed", "f8", (14,)),   # NEW — v1.8: dδ/dt in deg/day
    ("cusps",           "f8", (12,)),
    ("asc",             "f8"),
    ("mc",              "f8"),
    ("armc",            "f8"),
    ("vertex",          "f8"),
    ("aspect_matrix",   "i1", (14, 14)),
    ("aspect_orbs",     "f4", (14, 14)),
])
```

---

### `ketu/charts/api.py` — populate `body_decl_speed` in `compute_chart`

**Analog:** `ketu/charts/api.py` lines 379-394 — the `body_decl` derivation block
(the verbatim template to extend for the +Δt pass)

**Analog code** (lines 379-394):
```python
    # DECL-07: Equatorial declination δ per body, derived from the
    # already-fetched ecliptic (body_lons, body_lats) + instantaneous ε(jd).
    # No S-loop, no re-fetch — vectorised over S + (14,) in one pass.
    # true_obliquity is typed jd: float -> float but works on arrays at runtime;
    # np.asarray + float cast keeps mypy --strict clean without modifying the
    # function's own hint.
    eps_b: np.ndarray = np.asarray(
        true_obliquity(float(jd_b) if jd_b.ndim == 0 else jd_b)  # type: ignore[arg-type]
    )
    # eps_b[..., None] adds a trailing axis: 0-d -> (1,), (S,) -> (S,1),
    # broadcasting correctly against body_lons / body_lats shape S+(14,).
    eps_bc = eps_b[..., np.newaxis]
    x_ecl, y_ecl, z_ecl = spherical_to_rectangular(body_lons, body_lats, 1.0)
    x_eq, y_eq, z_eq = ecliptic_to_equatorial(x_ecl, y_ecl, z_ecl, eps_bc)
    _, decl, _ = rectangular_to_spherical(x_eq, y_eq, z_eq)
    out["body_decl"] = decl
```

**Pattern for body_decl_speed:** After `out["body_decl"] = decl` (line 394), add a
second pass at `jd_b + 0.01`. The already-computed `decl` is δ₀ (reused). Only δ₁ is
new. Mirror the `eps_b` + `eps_bc` guard pattern exactly for `jd_b + 0.01`:

```python
    # body_decl_speed: forward FD at Δt=0.01d, vectorised over S+(14,).
    # Mirrors declination_velocity(jdate, body) scalar (calculations.py:495-524)
    # but vectorised: one call covers all 14 bodies over the full leading shape S.
    # Numerical agreement with the scalar: Δ=0 (verified empirically, DSPD-02).
    _Dt = 0.01
    _jd_b1 = jd_b + _Dt
    _lons1, _lats1, _ = _vectorised_body_properties(_jd_b1)
    _eps_b1: np.ndarray = np.asarray(
        true_obliquity(float(_jd_b1) if _jd_b1.ndim == 0 else _jd_b1)  # type: ignore[arg-type]
    )
    _eps_bc1 = _eps_b1[..., np.newaxis]
    _x1, _y1, _z1 = spherical_to_rectangular(_lons1, _lats1, 1.0)
    _xe1, _ye1, _ze1 = ecliptic_to_equatorial(_x1, _y1, _z1, _eps_bc1)
    _, _decl1, _ = rectangular_to_spherical(_xe1, _ye1, _ze1)
    out["body_decl_speed"] = (_decl1 - decl) / _Dt
```

**Key points:**
- `decl` (already in scope from the body_decl block) is reused as δ₀ — no second
  evaluation of the coordinate chain at `jd_b`. Only `jd_b + 0.01` is new.
- The `jd_b.ndim == 0` guard on `true_obliquity` is mandatory — mirror it exactly
  (Pitfall 2 in RESEARCH.md).
- `_vectorised_body_properties` is already defined and in scope at line 62 of api.py.
- No new imports needed in `charts/api.py` for this change (all coordinate chain
  functions already imported at lines 40-45).

---

### `ketu/charts/api.py` — add `is_ascending_declination_chart` helper

**Analog:** `ketu/charts/api.py` lines 406-553 — `is_day_chart` (the chart-level helper
pattern: reads CHART_DTYPE fields, returns a vectorised NumPy result)

**is_day_chart signature + docstring structure to mirror** (lines 406-434):
```python
def is_day_chart(
    jd: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
) -> np.ndarray:
    """
    Return True when the Sun is at or above the horizon (sunrise inclusive).
    ...
    Parameters
    ----------
    jd : float or np.ndarray
        ...
    Returns
    -------
    np.ndarray of bool
        Boolean array with shape ``np.broadcast_shapes(jd, lat, lon)``.
    ...
    """
```

**Pattern for `is_ascending_declination_chart`:** Single-argument function taking a
`CHART_DTYPE` structured array. Returns `np.int8` array of shape `S + (14,)`.
Add `from ketu.calculations import DECL_STANDSTILL_EPS` at the top of the import block
in `charts/api.py` (one-way dependency charts → calculations; no cycle per AST analysis
in RESEARCH.md Resolution 1).

Concrete implementation pattern (from RESEARCH.md Implementation Anchors):
```python
def is_ascending_declination_chart(chart: np.ndarray) -> np.ndarray:
    """
    Classify each body's declination direction as ascending, descending, or neutral.

    Chart-level companion to the scalar :func:`ketu.calculations.is_ascending_declination`.
    Reads the ``body_decl_speed`` field of a :data:`CHART_DTYPE` structured array
    and classifies each body using :data:`ketu.calculations.DECL_STANDSTILL_EPS`.

    Parameters
    ----------
    chart : np.ndarray
        Structured array of :data:`CHART_DTYPE`, leading shape ``S`` (any broadcast
        shape — 0-d for scalar, (N,) for vectorised).

    Returns
    -------
    np.ndarray
        Integer array of dtype ``int8``, shape ``S + (14,)``.
        ``+1`` — ascending (dδ/dt > DECL_STANDSTILL_EPS, northward).
        ``-1`` — descending (dδ/dt < −DECL_STANDSTILL_EPS, southward).
        ``0``  — neutral / standstill (|dδ/dt| ≤ DECL_STANDSTILL_EPS).

    See Also
    --------
    ketu.calculations.is_ascending_declination : Scalar bool variant (jd, body).
    ketu.calculations.DECL_STANDSTILL_EPS : Standstill threshold constant.
    """
    speeds = np.asarray(chart["body_decl_speed"], dtype=np.float64)
    return np.where(
        speeds > DECL_STANDSTILL_EPS, np.int8(1),
        np.where(speeds < -DECL_STANDSTILL_EPS, np.int8(-1), np.int8(0))
    ).astype(np.int8)
```

**Export:** Add `is_ascending_declination_chart` to `ketu/charts/__init__.py` `__all__`
alongside `compute_chart` and `is_day_chart`.

**Current `ketu/charts/__init__.py` pattern** (lines 48-55 — extend this):
```python
from .api import compute_chart, is_day_chart
from .core import CHART_DTYPE

__all__ = [
    "CHART_DTYPE",
    "compute_chart",
    "is_day_chart",
]
```

---

### `ketu/calculations.py` — add `DECL_STANDSTILL_EPS` constant

**Analog:** `ketu/calculations.py` lines 495-555 — `declination_velocity` and
`is_ascending_declination` (the natural neighborhood for this constant)

**Scalar functions already present** (lines 495-555):
```python
def declination_velocity(jdate: float, body: int) -> float:
    """...deg/day. Positive = northward, negative = southward..."""
    return (declination(jdate + 0.01, body) - declination(jdate, body)) / 0.01


def is_ascending_declination(jdate: float, body: int) -> bool:
    """...True when dδ/dt > 0 (montante)..."""
    return bool(declination_velocity(jdate, body) > 0)
```

**Pattern:** Add the constant immediately before `declination_velocity` (line 495)
or between the two scalar functions. Use a `#:` docstring for numpydoc compliance
(same style as other documented constants in the codebase):

```python
#: Standstill threshold for equatorial declination velocity (deg/day).
#:
#: ``|dδ/dt| ≤ DECL_STANDSTILL_EPS`` classifies a body as at a declination
#: standstill (δ turning point — "montant" status undefined). Determined
#: empirically against the live ketu 1.7.0 ephemeris:
#:
#: - Sun at exact solstice:       ~0.000020 deg/day → correctly neutral
#: - Moon at exact δ-standstill:  ~0.000041 deg/day → correctly neutral
#: - Jupiter typical in motion:    0.005    deg/day → correctly ascending/descending
#: - Jupiter at own δ-node:       ~0.000081 deg/day → correctly neutral
#: - Uranus typical in motion:     0.003    deg/day → correctly ascending/descending
#:
#: Value 0.001 deg/day is well above the FD truncation floor (~0.000002 deg/day
#: for outer planets) and below any real in-motion reading for all 14 bodies.
DECL_STANDSTILL_EPS: float = 0.001
```

**Export:** Add `"DECL_STANDSTILL_EPS"` to `__all__` at line 656 (currently the list
begins there). The existing pattern in `__all__` (lines 656-687):

```python
__all__ = [
    # Utility functions
    "dd_to_dms",
    ...
    "declination",
    "declination_velocity",
    "is_ascending_declination",
    "is_out_of_bounds",
    ...
]
```

Add `"DECL_STANDSTILL_EPS"` in the body functions section, near `"declination_velocity"`.

---

### `ketu/composite/api.py` — derive `body_decl_speed` from composite frozen fields

**Analog:** `ketu/composite/api.py` lines 248-266 — the `body_speeds` midpoint +
`body_decl` derivation (the exact v1.5 precedent this extends)

**Analog code** (lines 248-266 — the block to extend after):
```python
    out["body_speeds"] = (
        np.asarray(chart_a["body_speeds"], dtype=np.float64)
        + np.asarray(chart_b["body_speeds"], dtype=np.float64)
    ) / 2.0
    # Derive body_decl from the composite λ,β that were just assigned — the
    # self-consistent derivation (δ of the composite midpoint chart, NOT a
    # midpoint of the parents' declinations).
    _eps = true_obliquity(float(out["jd"]))  # scalar ε for composite jd
    _x, _y, _z = spherical_to_rectangular(
        np.asarray(out["body_lons"], dtype=np.float64),
        np.asarray(out["body_lats"], dtype=np.float64),
        1.0,
    )
    _xe, _ye, _ze = ecliptic_to_equatorial(_x, _y, _z, _eps)
    _, _decl, _ = rectangular_to_spherical(_xe, _ye, _ze)
    out["body_decl"] = _decl  # shape (14,) — δ ∈ [−90, +90]°, north positive
```

**Pattern for `body_decl_speed`:** After `out["body_decl"] = _decl` (line 266), add the
FD block per CONTEXT.md D-01 and RESEARCH.md Resolution 2.

The pattern has two parts:
1. Compute `body_lat_speeds` (dβ/dt midpoints) — NOT stored in CHART_DTYPE, used only
   for the FD advance. Symmetric to how `body_speeds` (dλ/dt midpoint) is built.
2. FD on composite's frozen (λ, β) advanced by midpoint velocities.

**New import needed** in `composite/api.py` (line 73 area): add
`from ketu.ephemeris.planets import calc_planet_position_batch`.

Current imports (lines 68-85):
```python
from __future__ import annotations

import numpy as np

from ketu.aspects.presets import resolve_aspect_set
from ketu.calculations import distance
from ketu.charts import CHART_DTYPE
from ketu.core import aspects as _ASPECTS, bodies as _BODIES
from ketu.ephemeris.coordinates import (
    ecliptic_to_equatorial,
    rectangular_to_spherical,
    spherical_to_rectangular,
    true_obliquity,
)
from ketu.houses.registry import get_system

from .core import circular_midpoint
```

**Block to add after `out["body_decl"] = _decl`** (full pattern from RESEARCH.md
Resolution 2):
```python
    # body_decl_speed: FD on composite's OWN frozen (λ, β) advanced by midpoint
    # velocities over Δt=0.01d. NOT a midpoint of parents' body_decl_speed (DSPD-03).
    # NOT re-fetching real positions at jd_composite (no canonical jd — D-01).
    # dβ/dt midpoints are needed (Moon contribution 2.6× larger than dλ/dt); derived
    # from calc_planet_position_batch col 4 at each parent natal jd.
    _jd_a_flat = np.array([float(chart_a["jd"])])
    _jd_b_flat = np.array([float(chart_b["jd"])])
    _body_lat_speeds = np.empty((_BODY_COUNT,), dtype=np.float64)
    for _bid in range(_BODY_COUNT):
        _lat_spd_a = calc_planet_position_batch(_jd_a_flat, _bid)[0, 4]
        _lat_spd_b = calc_planet_position_batch(_jd_b_flat, _bid)[0, 4]
        _body_lat_speeds[_bid] = (_lat_spd_a + _lat_spd_b) / 2.0
    # Advance composite frozen (λ, β) by midpoint velocity rates over Δt:
    _Dt = 0.01
    _lons_adv = np.asarray(out["body_lons"], dtype=np.float64) + np.asarray(out["body_speeds"], dtype=np.float64) * _Dt
    _lats_adv = np.asarray(out["body_lats"], dtype=np.float64) + _body_lat_speeds * _Dt
    _eps_adv = true_obliquity(float(out["jd"]) + _Dt)
    _x1, _y1, _z1 = spherical_to_rectangular(_lons_adv, _lats_adv, 1.0)
    _xe1, _ye1, _ze1 = ecliptic_to_equatorial(_x1, _y1, _z1, _eps_adv)
    _, _decl_adv, _ = rectangular_to_spherical(_xe1, _ye1, _ze1)
    out["body_decl_speed"] = (_decl_adv - np.asarray(_decl, dtype=np.float64)) / _Dt
```

---

### `ketu/synastry/api.py` — verify inheritance only (no code change)

**Verification check:** Read `ketu/synastry/api.py` lines 64-105
(`_extend_body_data`). Confirm it reads only `body_lons` / `body_speeds` from
CHART_DTYPE inputs — `body_decl_speed` is not consumed, so adding it to CHART_DTYPE
changes nothing in synastry logic. No source edit needed.

**Test anchor:** Add an assertion in `tests/synastry/` that a synastry call where both
input charts were produced by `compute_chart` results in those charts having
`body_decl_speed` finite and non-zero (the inputs carry it; synastry output
`SYNASTRY_DTYPE` does not have this field — that is correct by design).

---

### `tests/charts/test_dtype.py` — re-pin ratchet (5 locations)

**Analog:** All 5 locations are the current `body_decl` entries — mirror exactly with
`body_decl_speed`.

**Location 1 — `test_dtype_has_expected_field_names` (lines 56-64):**

Current `expected` tuple:
```python
    expected = (
        "jd", "lat", "lon", "system",
        "body_lons", "body_lats", "body_speeds", "body_decl",
        "cusps", "asc", "mc", "armc", "vertex",
        "aspect_matrix", "aspect_orbs",
    )
```
Add `"body_decl_speed"` after `"body_decl"`:
```python
    expected = (
        "jd", "lat", "lon", "system",
        "body_lons", "body_lats", "body_speeds", "body_decl", "body_decl_speed",
        "cusps", "asc", "mc", "armc", "vertex",
        "aspect_matrix", "aspect_orbs",
    )
```
Also update the docstring count from "15 fields" to "16 fields" and mention v1.8.

**Location 2 — `test_dtype_subarray_shapes` parametrize (lines 67-85):**

Current entries include `("body_decl", (14,))`. Add:
```python
        ("body_decl_speed", (14,)),
```

**Location 3 — `test_dtype_scalar_field_kinds` parametrize (lines 88-110):**

Current entries include `("body_decl", "f", 8)`. Add:
```python
        ("body_decl_speed", "f", 8),
```

**Location 4 — `test_dtype_supports_vectorized_construction` (lines 128-139):**

Current assertions include `assert arr["body_decl"].shape == (5, 14)`. Add:
```python
    assert arr["body_decl_speed"].shape == (5, 14)
```

**Location 5 — `test_dtype_scalar_zero_dim_construction` (lines 144-153):**

Current assertions include `assert elem["body_decl"].shape == (14,)`. Add:
```python
    assert elem["body_decl_speed"].shape == (14,)
```

---

## New Test Files / Test Additions

### `tests/charts/test_compute_chart.py` — add class `TestBodyDeclSpeed`

**Analog:** Existing `test_body_decl_is_not_all_zero` pattern in
`tests/composite/test_calculate_composite.py` (anti-zero-fill ratchet).

Tests to add:
- `test_body_decl_speed_present_in_dtype` — `"body_decl_speed" in CHART_DTYPE.names`
- `test_body_decl_speed_non_zero_finite` — compute_chart on a known JD; check
  `np.all(np.isfinite(...))` and `not np.all(result["body_decl_speed"] == 0)`
- `test_body_decl_speed_matches_scalar_fd` — compare
  `result["body_decl_speed"][body_idx]` against
  `declination_velocity(jd, body_idx)` — expect exact agreement (Δ=0)
- `test_body_decl_speed_shape_vectorised` — vectorised chart `(N,)` produces
  `body_decl_speed.shape == (N, 14)`

### `tests/composite/test_calculate_composite.py` — add class `TestBodyDeclSpeed`

**Analog:** The existing `body_decl` test block in the same file.

Tests to add:
- `test_body_decl_speed_shape` — `composite["body_decl_speed"].shape == (14,)`
- `test_body_decl_speed_non_zero` — anti-zero-fill ratchet
- `test_body_decl_speed_finite` — `np.all(np.isfinite(composite["body_decl_speed"]))`
- `test_body_decl_speed_not_parent_midpoint` — compute
  `midpoint = (chart_a["body_decl_speed"] + chart_b["body_decl_speed"]) / 2.0`;
  assert `not np.allclose(composite["body_decl_speed"], midpoint)` (DSPD-03 ratchet)

### `tests/test_declination.py` — add DECL_STANDSTILL_EPS tests

**Analog:** Existing import/value tests for scalar functions in the same file.

Tests to add:
- `test_decl_standstill_eps_importable` —
  `from ketu.calculations import DECL_STANDSTILL_EPS; assert DECL_STANDSTILL_EPS`
- `test_decl_standstill_eps_value` — `assert DECL_STANDSTILL_EPS == 0.001`
- `test_decl_standstill_eps_classifies_sun_solstice_as_neutral` — use JD ~2460482.36
  (Sun exact solstice 2024-06-21); FD at 0.000020 < 0.001 → neutral (0)
- `test_decl_standstill_eps_does_not_mask_jupiter_in_motion` — use Jupiter mid-cycle
  JD (typical |dδ/dt| ~0.005 > 0.001) → not neutral

### `tests/charts/test_chart_helpers.py` (new) or extend `test_compute_chart.py`

**Analog:** Pattern of `is_day_chart` tests.

Tests to add for `is_ascending_declination_chart`:
- `test_chart_helper_returns_int8` — `result.dtype == np.int8`
- `test_chart_helper_shape_matches_body_axis` — scalar chart `()` → shape `(14,)`;
  vectorised chart `(N,)` → shape `(N, 14)`
- `test_chart_helper_consistent_with_scalar` — for a known JD/body, compare
  `is_ascending_declination_chart(chart)[body_idx] > 0` against
  `is_ascending_declination(jd, body_idx)`
- `test_chart_helper_neutral_at_standstill` — inject a chart with
  `body_decl_speed` set to `DECL_STANDSTILL_EPS * 0.5`; assert result is `0`

---

## Shared Patterns

### Additive Dtype Field Pattern

**Source:** `ketu/charts/core.py` lines 90-111 (`body_decl` comment block + dtype
definition)

**Apply to:** `ketu/charts/core.py` (field addition) and all dtype ratchet tests

The comment header documents the Kala positional-offset impact. Copy the rationale
verbatim and extend it to mention v1.8 `body_decl_speed`.

### Forward Finite Difference Idiom (Δt = 0.01 d)

**Source:** `ketu/calculations.py` lines 524
```python
return (declination(jdate + 0.01, body) - declination(jdate, body)) / 0.01
```

**Apply to:** `ketu/charts/api.py` (vectorised FD), `ketu/composite/api.py` (FD on
frozen composite fields). The Δt=0.01 is the package-wide idiom — do not change it.

### true_obliquity ndim Guard

**Source:** `ketu/charts/api.py` lines 385-387
```python
    eps_b: np.ndarray = np.asarray(
        true_obliquity(float(jd_b) if jd_b.ndim == 0 else jd_b)  # type: ignore[arg-type]
    )
```

**Apply to:** The `jd_b + 0.01` evaluation in `compute_chart` must use the same guard
(Pitfall 2 in RESEARCH.md). Mirror exactly for `_jd_b1 = jd_b + _Dt`.

### eps Broadcast Pattern

**Source:** `ketu/charts/api.py` lines 390
```python
    eps_bc = eps_b[..., np.newaxis]
```

**Apply to:** The `_eps_bc1 = _eps_b1[..., np.newaxis]` step in the body_decl_speed
FD block. Required for correct broadcasting against `S + (14,)` body arrays.

### coordinate chain (δ derivation)

**Source:** `ketu/charts/api.py` lines 391-394
```python
    x_ecl, y_ecl, z_ecl = spherical_to_rectangular(body_lons, body_lats, 1.0)
    x_eq, y_eq, z_eq = ecliptic_to_equatorial(x_ecl, y_ecl, z_ecl, eps_bc)
    _, decl, _ = rectangular_to_spherical(x_eq, y_eq, z_eq)
```

**Apply to:** Both the `jd + 0.01` pass in `compute_chart` and the FD advance in
`composite/api.py`. All three coordinate chain functions are already imported in both
files.

### Anti-Zero-Fill Ratchet Pattern

**Source:** `tests/composite/test_calculate_composite.py` — the existing
`test_body_decl_is_not_all_zero` test (check `not np.all(... == 0)`)

**Apply to:** Every new `body_decl_speed` test class (natal, composite, returns).
The `np.zeros((), dtype=CHART_DTYPE)` initialiser silently fills unset fields with zero.

### numpydoc Docstring Style

**Source:** `ketu/charts/api.py` lines 406-505 (`is_day_chart` — full Parameters /
Returns / See Also / Notes / Examples structure)

**Apply to:** `is_ascending_declination_chart`. Must pass the `interrogate >= 95%` and
`numpydoc validate` gates. Minimum sections: short summary, Parameters, Returns, See
Also (linking to the scalar variant).

---

## No Analog Found

None. All files have exact analogs in the live codebase.

---

## Metadata

**Analog search scope:** `ketu/charts/`, `ketu/composite/`, `ketu/calculations.py`,
`ketu/synastry/`, `tests/charts/`, `tests/composite/`, `tests/test_declination.py`

**Files scanned (Read tool):**
- `ketu/charts/core.py` lines 90-111
- `ketu/charts/api.py` lines 1-553
- `ketu/charts/__init__.py` lines 1-55
- `ketu/calculations.py` lines 490-555, 650-687
- `ketu/composite/api.py` lines 60-90, 240-290
- `tests/charts/test_dtype.py` lines 50-160

**Pattern extraction date:** 2026-06-17
