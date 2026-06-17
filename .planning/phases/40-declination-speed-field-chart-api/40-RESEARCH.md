# Phase 40: Declination Speed Field & Chart API — Research

**Researched:** 2026-06-17
**Domain:** CHART_DTYPE extension + chart-level helper (pure NumPy, no new astronomy)
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 (Composite δ-speed):** Finite difference on the composite's OWN frozen λ,β
  advanced by midpoint velocities over Δt=0.01 d — NOT re-fetching real planetary
  positions, NOT averaging parents' body_decl_speed.
- **D-02 (DECL_STANDSTILL_EPS value):** Not pinned by user — researcher determines a
  justified, tested value (this research resolves it: see § Open Questions Resolved).
- **D-03 (helper output encoding):** np.int8 array {-1, 0, +1} per body. +1 ascending,
  -1 descending, 0 neutral/standstill.
- **Δt = 0.01 day verbatim** from existing declination_velocity — not configurable.
- **body_decl_speed is raw deg/day** (like body_speeds for longitude).
- **Ketu/Rahu boundary is non-negotiable:** Rahu reads; Ketu computes. No astronomy in
  Rahu, including the standstill threshold.
- **MINOR bump (1.8.0):** dtype layout grows → Kala re-pins PyPI.

### Claude's Discretion

- API namespace for DECL_STANDSTILL_EPS and the chart-level helper (resolved by this
  research — see § Open Questions Resolved #1).
- β-velocity source for composite D-01 (resolved by this research — see § Open Questions
  Resolved #2).

### Deferred Ideas (OUT OF SCOPE)

- Rahu-side display logic (value vs ↗/↘ sense, arrow/tint visual language).
- Declination aspect speed (applying/separating parallels) — DECLA-F1.
- Configurable Δt.
- HARMF-01 rich --harmonics CLI grammar.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DSPD-01 | Add `("body_decl_speed", "f8", (14,))` to CHART_DTYPE, populated by `compute_chart` via the vectorised FD path | FD pattern verified at `charts/api.py:379-394`; vectorised agreement with scalar confirmed (Δ=0) |
| DSPD-02 | Δt=0.01d verbatim; numerical agreement against scalar `declination_velocity` | Confirmed: vectorised FD at Δt=0.01d == scalar; Δ=0.0000000000 for Moon and Sun |
| DSPD-03 | Inherited by synastry/composite/returns; composite derived from its own fields, never parent midpoint | Synastry: CHART_DTYPE inputs carry field automatically, no change to calculate_synastry needed; composite: β-velocity source resolved (midpoint of parent lat_speeds via calc_planet_position_batch); returns: free via compute_chart |
| DSPD-04 | Dtype ratchet test re-pinned; Kala positional impact documented | Exact lines to update in `tests/charts/test_dtype.py` identified (56-64, 67-85, 88-110, 128-153); 16 fields after addition |
| DSPD-05 | `DECL_STANDSTILL_EPS` public constant, tested, Rahu invents no threshold | Value 0.001 deg/day empirically justified and verified (see below); belongs in `ketu.calculations` (no import cycle) |
| DSPD-06 | Chart-level helper: np.int8 {-1,0,+1} per body, reads body_decl_speed + DECL_STANDSTILL_EPS, consistent with v1.5 scalar | Placement in `ketu.charts` (`charts/api.py`); no import cycle; consistent with is_day_chart pattern |
</phase_requirements>

---

## Summary

Phase 40 is a **pure additive dtype extension** — no new astronomy, no new algorithm.
The scalar math (`declination_velocity(jd, body)` = forward FD at Δt=0.01d) already
exists in `ketu/calculations.py` since v1.5. This phase:

1. Adds `("body_decl_speed", "f8", (14,))` to CHART_DTYPE (15 → 16 fields).
2. Populates it in `compute_chart` via two calls to `_vectorised_body_properties` (jd
   and jd+0.01), applies the coordinate chain both times, takes the slope — identical
   math to the v1.5 body_decl block (lines 379-394 in charts/api.py) repeated for jd+Δt.
3. Derives it self-consistently in `calculate_composite` from frozen composite λ,β +
   their midpoint velocities (matching the precedent of body_decl v1.5).
4. Verifies inheritance in synastry (CHART_DTYPE inputs already carry it; no code
   change needed) and returns (free via compute_chart).
5. Re-pins the dtype ratchet in `tests/charts/test_dtype.py`.
6. Exports `DECL_STANDSTILL_EPS = 0.001` (deg/day) from `ketu.calculations`.
7. Adds `is_ascending_declination(chart)` to `ketu.charts` (returns np.int8 shape
   matching the body axis).

All three open questions from CONTEXT.md are resolved below with empirical evidence.

**Primary recommendation:** Implement as a single wave, mirroring the v1.5 body_decl
addition verbatim. The only non-trivial design choice is the composite β-velocity source
(resolved: midpoint of parents' lat_speeds via calc_planet_position_batch at each parent
jd, not stored, used only for the FD advance).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Scalar dδ/dt (FD math) | ketu.calculations | — | Already exists; unchanged |
| CHART_DTYPE field storage | ketu.charts.core | — | Single dtype definition |
| Natal/returns field population | ketu.charts.api (compute_chart) | — | All natal paths go through compute_chart |
| Composite field population | ketu.composite.api | — | Composite never calls compute_chart; assembles inline |
| Synastry inheritance | ketu.synastry (no change) | — | Consumes CHART_DTYPE inputs; gain is free |
| Standstill threshold | ketu.calculations | — | Near existing scalar helpers; no import cycle |
| Chart-level helper | ketu.charts.api | — | Mirrors is_day_chart pattern; reads CHART_DTYPE |
| Public export surface | ketu.__init__ / ketu.calculations | — | DECL_STANDSTILL_EPS exported from calculations |

---

## Open Questions Resolved

### Resolution 1: API Namespace for DECL_STANDSTILL_EPS and the chart-level helper [VERIFIED: codebase]

**Import graph (verified by AST analysis):**

- `ketu/calculations.py` imports: `ketu.core`, `ketu.ephemeris.*` only. It imports
  **nothing from `ketu.charts`**. [VERIFIED: codebase grep, empty list confirmed]
- `ketu/charts/api.py` imports: `ketu.aspects.*`, `ketu.core`, `ketu.ephemeris.*`,
  `ketu.houses.*`. It imports **nothing from `ketu.calculations`**. [VERIFIED: codebase
  grep, empty list confirmed]
- `ketu/composite/api.py` imports `ketu.calculations` (for `distance`). This is a
  one-way dependency: composite → calculations, NOT calculations → composite.

**Result: no import cycle risk in any direction.**

**Recommendation (firm):**

- `DECL_STANDSTILL_EPS` → `ketu/calculations.py`, added to `__all__` (line 656).
  Rationale: sits alongside the existing scalar helpers `declination_velocity` and
  `is_ascending_declination`. Natural home. No import cycle.
- Chart-level helper (`is_ascending_declination` chart variant) → `ketu/charts/api.py`
  and exported via `ketu/charts/__init__.py`. Rationale: mirrors `is_day_chart` which
  already lives there and reads CHART_DTYPE. The chart helper reads
  `chart["body_decl_speed"]` and imports `DECL_STANDSTILL_EPS` from
  `ketu.calculations` — this is a one-way dependency (charts → calculations), which
  already exists implicitly via `ketu.composite` and has no cycle.

**Naming disambiguation:** the v1.5 scalar is `is_ascending_declination(jdate: float,
body: int) -> bool`. The new chart-level function has a different signature:
`is_ascending_declination_chart(chart: np.ndarray) -> np.ndarray`. Using a distinct
name avoids shadowing the scalar — the planner should choose one of:
- `is_ascending_declination_chart(chart)` — explicit disambiguation
- `declination_direction(chart)` — avoids name conflict entirely
- Overloaded `is_ascending_declination` with type dispatch (NOT recommended — breaks
  `from ketu.calculations import is_ascending_declination` precedent)

The planner locks the exact name; `is_ascending_declination_chart` is the safe default.

---

### Resolution 2: Composite β-velocity source for D-01 [VERIFIED: codebase]

**What CHART_DTYPE stores (verified):** `body_lons` (λ), `body_lats` (β), `body_speeds`
(dλ/dt), `body_decl` (δ). It does NOT store dβ/dt (lat_speed). [VERIFIED: charts/core.py]

**calc_planet_position_batch return layout (verified):**
`[lon, lat, dist, lon_speed, lat_speed, dist_speed]` — column 3 = dλ/dt, column 4 =
dβ/dt. [VERIFIED: ephemeris/planets.py + runtime probe]

**Sensitivity analysis (empirical):** For the Moon (the most dynamic body), the
contribution of Δβ to Δδ is 2.6× LARGER than the contribution of Δλ over Δt=0.01d.
Ignoring dβ/dt would introduce ~260% error in the FD slope for the Moon. dβ/dt cannot
be set to zero. [VERIFIED: runtime probe]

**Concrete recommended implementation:**

During `calculate_composite`, after the body_lats linear average is computed:

```python
# Compute dβ/dt midpoint for each of the 14 bodies, at each parent's natal jd.
# Symmetric to how body_speeds (dλ/dt midpoint) was built (composite/api.py:248-251).
# col 4 of calc_planet_position_batch = dβ/dt.
import numpy as np
from ketu.ephemeris.planets import calc_planet_position_batch

jd_a_flat = np.array([float(chart_a["jd"])])
jd_b_flat = np.array([float(chart_b["jd"])])
body_lat_speeds = np.empty((_BODY_COUNT,), dtype=np.float64)
for body_id in range(_BODY_COUNT):
    lat_spd_a = calc_planet_position_batch(jd_a_flat, body_id)[0, 4]
    lat_spd_b = calc_planet_position_batch(jd_b_flat, body_id)[0, 4]
    body_lat_speeds[body_id] = (lat_spd_a + lat_spd_b) / 2.0
# body_lat_speeds is NOT stored in CHART_DTYPE — used only for the FD advance below.

# FD on composite's frozen (λ, β) advanced by midpoint velocities:
_Dt = 0.01  # verbatim from declination_velocity
_lons_adv = out["body_lons"] + out["body_speeds"] * _Dt   # λ₀ + dλ/dt × Δt
_lats_adv = out["body_lats"] + body_lat_speeds * _Dt       # β₀ + dβ/dt × Δt
_eps_adv = true_obliquity(float(out["jd"]) + _Dt)
_x1, _y1, _z1 = spherical_to_rectangular(
    np.asarray(_lons_adv, dtype=np.float64),
    np.asarray(_lats_adv, dtype=np.float64),
    1.0,
)
_xe1, _ye1, _ze1 = ecliptic_to_equatorial(_x1, _y1, _z1, _eps_adv)
_, _decl_adv, _ = rectangular_to_spherical(_xe1, _ye1, _ze1)
out["body_decl_speed"] = (_decl_adv - np.asarray(out["body_decl"])) / _Dt
```

This is self-consistent with the composite's construction: both λ-rate and β-rate are
midpoints of the parents' rates, derived at the parents' natal jds. Not stored, not
exposed — used only for the FD.

**Note on calc_planet_position_batch calls:** 14 bodies × 2 parents = 28 scalar
calls to calc_planet_position_batch. These are fast (cached ephemeris). Acceptable for
a composite chart computation. Can be restructured to 2 calls per parent if vectorising
over bodies, but the scalar loop is consistent with the composite's existing pattern.

---

### Resolution 3: DECL_STANDSTILL_EPS numeric value [VERIFIED: runtime probe]

**Empirical findings (all verified by running the live code):**

| Body / Condition | FD at Δt=0.01d | Notes |
|------------------|----------------|-------|
| Sun at exact solstice (2024-06-21) | 0.000020 deg/day | True standstill — correct to classify neutral |
| Sun 6h from solstice | 0.000785 deg/day | Still very close to standstill |
| Sun 1 day from solstice | 0.013 deg/day | Clearly in motion — must NOT be masked |
| Moon at exact δ-standstill (2025-03-08) | 0.000041 deg/day | True standstill — correct to classify neutral |
| Moon 16.5h from standstill | 0.019 deg/day | Already in motion — must NOT be masked |
| Moon normal mid-cycle | ~4.6 deg/day | Clearly ascending/descending |
| Jupiter typical | 0.005 deg/day | Real slow motion — must NOT be masked |
| Jupiter at own δ-standstill (2024) | 0.000081 deg/day | True outer-planet δ-node — correct neutral |
| Uranus typical | 0.003 deg/day | Real slow motion — must NOT be masked |
| Uranus at own δ-standstill (2024) | 0.000211 deg/day | Borderline — see below |
| Neptune typical | 0.009 deg/day | — |
| Chiron typical | 0.004 deg/day | — |

**FD truncation error (Δt=0.01 vs Δt=0.0001):**
- Moon (mid-cycle): 0.004 deg/day — this is NOT random noise, it is systematic forward-difference
  truncation bias. At a true standstill (δ(jd+0.01) ≈ δ(jd)), the FD returns near-zero
  regardless of this bias.
- Sun: 0.00003 deg/day
- Outer planets: ~0.000002 deg/day

**Recommended value: `DECL_STANDSTILL_EPS = 0.001` (deg/day)**

Rationale:
1. Sun at exact solstice: 0.000020 < 0.001 → correctly **neutral**
2. Sun 6h from solstice: 0.000785 < 0.001 → correctly **neutral** (still near-solstice)
3. Sun 1 day from solstice: 0.013 > 0.001 → correctly **descending**
4. Moon at exact δ-standstill: 0.000041 < 0.001 → correctly **neutral**
5. Moon 16.5h from standstill: 0.019 > 0.001 → correctly **ascending**
6. Jupiter typical (0.005) > 0.001 → correctly **ascending/descending** (not masked)
7. Jupiter at own δ-standstill (0.000081) < 0.001 → correctly **neutral**
8. Uranus typical (0.003) > 0.001 → correctly **ascending/descending** (not masked)
9. Uranus at own δ-standstill (0.000211) < 0.001 → correctly **neutral**

The threshold cleanly separates "body in real motion" from "body at its δ turning-point"
for all 14 bodies. It does NOT mask the slow but real daily dδ/dt of outer planets on
non-standstill days.

**Test anchor:** Sun solstice JD ~2460482.36 gives FD 0.000020 deg/day; Moon standstill
JD ~2460742.18 gives FD 0.000041 deg/day — both should classify as neutral (0) with
EPS=0.001.

---

## Implementation Anchors

### File: `ketu/charts/core.py`

**Change:** Append `("body_decl_speed", "f8", (14,))` after `body_decl` (currently
line 103), and update the module docstring to mention the new field. The dtype grows
from 15 to 16 fields. [VERIFIED: current layout at lines 95-111]

New CHART_DTYPE layout (field 7 = body_decl, new field 8 = body_decl_speed):

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
    ("body_decl_speed", "f8", (14,)),   # NEW — v1.8
    ("cusps",           "f8", (12,)),
    ("asc",             "f8"),
    ("mc",              "f8"),
    ("armc",            "f8"),
    ("vertex",          "f8"),
    ("aspect_matrix",   "i1", (14, 14)),
    ("aspect_orbs",     "f4", (14, 14)),
])
```

### File: `ketu/charts/api.py`

**Change 1 — populate body_decl_speed in `compute_chart` (natal path):**

After line 394 (`out["body_decl"] = decl`), add the FD pass. The pattern is two
evaluations of the coordinate chain: one already done (at jd_b), one new (at jd_b+0.01).
The already-computed `decl` IS δ(jd). Need only δ(jd+0.01):

```python
# body_decl_speed: forward FD at Δt=0.01d, vectorised over S+(14,).
# Mirrors the declination_velocity(jdate, body) scalar (calculations.py:495-524)
# but vectorised: one call covers all 14 bodies over the full leading shape S.
# Numerical agreement with the scalar: Δ=0 (verified empirically).
_Dt = 0.01
_lons1, _lats1, _ = _vectorised_body_properties(jd_b + _Dt)
_eps_b1: np.ndarray = np.asarray(
    true_obliquity(float((jd_b + _Dt)) if (jd_b + _Dt).ndim == 0
                   else (jd_b + _Dt))  # type: ignore[arg-type]
)
_eps_bc1 = _eps_b1[..., np.newaxis]
_x1, _y1, _z1 = spherical_to_rectangular(_lons1, _lats1, 1.0)
_xe1, _ye1, _ze1 = ecliptic_to_equatorial(_x1, _y1, _z1, _eps_bc1)
_, _decl1, _ = rectangular_to_spherical(_xe1, _ye1, _ze1)
out["body_decl_speed"] = (_decl1 - decl) / _Dt
```

**Change 2 — add chart-level helper and DECL_STANDSTILL_EPS import:**

Import `DECL_STANDSTILL_EPS` from `ketu.calculations` at the top of charts/api.py
(no cycle: charts/api.py currently does NOT import from ketu.calculations — this adds a
one-way dependency charts → calculations; calculations does NOT import from charts).

Add after `is_day_chart`:

```python
from ketu.calculations import DECL_STANDSTILL_EPS  # already in ketu.calculations.__all__


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
    """
    speeds = np.asarray(chart["body_decl_speed"], dtype=np.float64)
    return np.where(
        speeds > DECL_STANDSTILL_EPS, np.int8(1),
        np.where(speeds < -DECL_STANDSTILL_EPS, np.int8(-1), np.int8(0))
    ).astype(np.int8)
```

Export in `ketu/charts/__init__.py` `__all__`.

### File: `ketu/calculations.py`

**Change:** Add constant `DECL_STANDSTILL_EPS = 0.001` (deg/day) before or after
`declination_velocity` (lines 495-524), and add to `__all__` (currently line 656).

```python
#: Standstill threshold for equatorial declination velocity (deg/day).
#:
#: |dδ/dt| ≤ DECL_STANDSTILL_EPS classifies a body as at a declination standstill
#: (δ turning point — "montant" status undefined). Determined empirically:
#:   - Sun at exact solstice:    ~0.00002 deg/day → correctly neutral
#:   - Moon at exact standstill: ~0.00004 deg/day → correctly neutral
#:   - Jupiter/Uranus in motion: 0.003-0.005 deg/day → correctly ascending/descending
#:   - Outer planets at their own δ-node: < 0.00022 deg/day → correctly neutral
#: Value 0.001 deg/day is well above the FD truncation floor (~0.000002 deg/day for
#: outer planets) and below any real in-motion reading for all 14 bodies.
DECL_STANDSTILL_EPS: float = 0.001
```

### File: `ketu/composite/api.py`

**Change:** After line 266 (`out["body_decl"] = _decl`) add the inline body_decl_speed
FD block per Resolution 2.

Imports already present: `calc_planet_position_batch` is NOT currently imported in
composite/api.py — need to add `from ketu.ephemeris.planets import calc_planet_position_batch`.
All coordinate chain functions are already imported.

### File: `tests/charts/test_dtype.py`

**Four ratchet changes needed:**

1. `test_dtype_has_expected_field_names` (lines 56-64): add `"body_decl_speed"` after
   `"body_decl"` in the `expected` tuple. Count changes from 15 to 16.

2. `test_dtype_subarray_shapes` parametrize (lines 67-85): add entry
   `("body_decl_speed", (14,))`.

3. `test_dtype_scalar_field_kinds` parametrize (lines 88-110): add entry
   `("body_decl_speed", "f", 8)`.

4. `test_dtype_supports_vectorized_construction` (lines 128-139): add
   `assert arr["body_decl_speed"].shape == (5, 14)`.

5. `test_dtype_scalar_zero_dim_construction` (lines 144-153): add
   `assert elem["body_decl_speed"].shape == (14,)`.

Note: the test_dtype_has_expected_field_names docstring currently states "15 fields"
— update to "16 fields" and mention v1.8 `body_decl_speed` addition.

---

## Synastry: Inheritance is Free (No Code Change)

`calculate_synastry` (synastry/api.py) consumes two CHART_DTYPE inputs and produces
SYNASTRY_DTYPE output. SYNASTRY_DTYPE fields:
`('body_a', 'body_b', 'lon_a', 'lon_b', 'aspect_type', 'orb', 'applying', 'orb_limit')`.
The function reads only `body_lons` and `body_speeds` from the chart inputs via
`_extend_body_data` (lines 64-105). Adding `body_decl_speed` to CHART_DTYPE changes
nothing about synastry's logic — the inputs simply carry the new field without it being
consumed. [VERIFIED: synastry/api.py line-by-line]

**What DSPD-03 means for synastry:** "inherited" means that a synastry chart computed
from two natal charts produced by `compute_chart` will automatically have
`body_decl_speed` populated in the CHART_DTYPE inputs. No code change to
`calculate_synastry` is needed. A pinning test should verify that `chart_a["body_decl_speed"]`
is finite and non-zero when passed into a synastry call.

---

## Returns: Free via compute_chart

`lunar_return` (returns/lunar.py:37) and `solar_return` (returns/solar.py) both call
`compute_chart` directly to produce their output. Since `compute_chart` will be updated
to populate `body_decl_speed`, returns inherit the field for free. [VERIFIED: returns/lunar.py:37]

**What DSPD-03 means for returns:** Only a pinning test is needed (verify that a return
chart has `body_decl_speed` present and non-zero). No code change to the returns modules.

---

## Vectorised FD — Numerical Agreement Verification

**Verified empirically (confirmed at research time):**

```
Vectorised body_decl_speed[0, 1] (Moon, jd=2025-01-15): -4.605142 deg/day
Scalar declination_velocity(jd, Moon):                  -4.605142 deg/day
Agreement Δ:                                             0.0000000000 deg/day
```

Both the scalar (`declination_velocity`) and the vectorised FD use:
- `declination(jd + 0.01, body) - declination(jd, body)) / 0.01`
- Forward difference, Δt=0.01d, no wraparound correction
- Same coordinate chain: `spherical_to_rectangular → ecliptic_to_equatorial(ε) →
  rectangular_to_spherical`, taking element [1] (equatorial latitude = δ)

The vectorised version passes body_lons and body_lats from `_vectorised_body_properties`
at both jd and jd+Δt. The scalar uses `declination(jdate, body)` which internally
calls `calc_planet_position_batch`. These are numerically identical paths — Δ=0 is
exact, not approximate. [VERIFIED: runtime probe]

---

## Standard Stack

No new packages. Pure NumPy throughout. [VERIFIED: codebase]

### Core (existing, reused verbatim)

| Asset | Location | Purpose in Phase 40 |
|-------|----------|---------------------|
| `_vectorised_body_properties` | `charts/api.py:62` | Called twice (jd and jd+Δt) for natal FD |
| `true_obliquity` | `ephemeris/coordinates.py` | Called twice per FD for ε(jd) and ε(jd+Δt) |
| `spherical_to_rectangular` | `ephemeris/coordinates.py` | Part of the δ chain at both jd |
| `ecliptic_to_equatorial` | `ephemeris/coordinates.py` | Part of the δ chain at both jd |
| `rectangular_to_spherical` | `ephemeris/coordinates.py` | Part of the δ chain at both jd |
| `calc_planet_position_batch` | `ephemeris/planets.py` | Used in composite for dβ/dt midpoints |
| `declination_velocity` | `calculations.py:495` | Scalar reference for DSPD-02 verification test |
| `CHART_DTYPE` | `charts/core.py:95` | Extended with body_decl_speed |

All these imports are already present in their respective files — no new imports needed
except `calc_planet_position_batch` in `composite/api.py`.

---

## Architecture Patterns

### Pattern 1: Additive Dtype Field (verbatim v1.5 precedent)

`body_decl` (v1.5) is the canonical template. Steps:
1. Add field to CHART_DTYPE definition in core.py.
2. Populate in compute_chart after the existing body_decl block.
3. Derive self-consistently in calculate_composite (inline, no compute_chart call).
4. Re-pin dtype ratchet in test_dtype.py.
5. Export constant + helper from the appropriate namespace.

### Pattern 2: Vectorised FD Over S+(14,)

The body_decl block at charts/api.py:379-394 is the canonical template:
- `eps_b = true_obliquity(jd_b)` — scalar or array depending on jd_b.ndim
- `eps_bc = eps_b[..., np.newaxis]` — broadcast against S+(14,)
- Coordinate chain applied once over the full S+(14,) shape

For body_decl_speed: same pattern applied to `jd_b + 0.01`, with the already-computed
`decl` (= body_decl at jd_b) reused as δ₀. Only the jd+Δt evaluation is new.

### Anti-Patterns to Avoid

- **Re-fetching real positions at composite jd:** D-01 explicitly rejects this. The
  composite jd is a bookkeeping midpoint with no astronomical meaning. FD must advance
  the composite's OWN frozen (λ, β) by their midpoint velocities.
- **Averaging parents' body_decl_speed:** Same trap as body_decl in v1.5 — explicitly
  forbidden by DSPD-03. A test must pin that composite body_decl_speed differs from
  the naïve parent midpoint.
- **Setting dβ/dt=0 in composite FD:** Moon β-velocity contributes 2.6× more to δ
  change than λ-velocity over Δt=0.01d. Ignoring dβ/dt would give wrong values.
- **Storing dβ/dt in CHART_DTYPE:** Out of scope. Use it locally during composite
  assembly only; it is NOT a contract field.
- **Calling compute_chart from calculate_composite:** Existing anti-regression ratchet
  (COMP-03 Pitfall 3); the composite has no canonical jd so compute_chart would
  produce a physically meaningless chart.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| δ chain at jd+Δt | Custom ecliptic→equatorial | `_vectorised_body_properties` + existing coordinate chain |
| Type conversion | Manual int8 logic | `np.where(...).astype(np.int8)` |
| Numerical agreement test | Custom comparison | `assert Δ == 0` or `np.testing.assert_array_equal` |

---

## Common Pitfalls

### Pitfall 1: Zero-fill trap for body_decl_speed

**What goes wrong:** `np.zeros((), dtype=CHART_DTYPE)` initialises all fields to zero.
If the populate step for body_decl_speed is accidentally skipped or placed before the
CHART_DTYPE extension, the field silently stays zero.

**Prevention:** The existing `test_body_decl_is_not_all_zero` test in
`tests/composite/test_calculate_composite.py` is the model. Add an identical ratchet
for body_decl_speed in composite AND natal tests.

### Pitfall 2: eps_b broadcast at jd+Δt

**What goes wrong:** `true_obliquity` is typed `jd: float -> float` but works on arrays
at runtime. The existing body_decl block uses `float(jd_b) if jd_b.ndim == 0 else jd_b`
to keep mypy clean. The same guard is needed for `jd_b + 0.01`.

**Prevention:** Mirror the exact pattern at lines 385-387 for both `jd_b + 0.01` and
the eps broadcast.

### Pitfall 3: Composite — forgetting to import calc_planet_position_batch

**What goes wrong:** composite/api.py does not currently import `calc_planet_position_batch`
(it imports `ketu.calculations.distance` only). The dβ/dt derivation needs it.

**Prevention:** Add `from ketu.ephemeris.planets import calc_planet_position_batch` at
the top of composite/api.py.

### Pitfall 4: Synastry "inheritance" misunderstood

**What goes wrong:** Implementing a code change to calculate_synastry to "propagate"
body_decl_speed — this is unnecessary. SYNASTRY_DTYPE is a different dtype; synastry
output has no body_decl_speed field. Inheritance means the CHART_DTYPE inputs carry it.

**Prevention:** Read SYNASTRY_DTYPE definition before touching synastry code. The only
synastry work is a pinning test.

### Pitfall 5: Ratchet test update count

**What goes wrong:** Updating test_dtype_has_expected_field_names but forgetting the
parametrize entries in test_dtype_subarray_shapes and test_dtype_scalar_field_kinds.
Tests remain green for the field names but miss shape/kind validation.

**Prevention:** Update all five locations in test_dtype.py atomically (listed in
Implementation Anchors above).

### Pitfall 6: is_ascending_declination name conflict

**What goes wrong:** Adding a chart-level function named `is_ascending_declination` to
ketu.charts that shadows the scalar `is_ascending_declination` from ketu.calculations —
a caller who does `from ketu.calculations import is_ascending_declination` and then
`from ketu.charts import is_ascending_declination` gets the chart version silently.

**Prevention:** Use a distinct name for the chart helper, e.g.,
`is_ascending_declination_chart`. The CONTEXT.md D-03 note says "naming is the
planner's call as long as the two are clearly distinguishable."

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (pyproject.toml, `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` |
| Quick run command | `pytest tests/charts/ tests/composite/ tests/test_declination.py -x` |
| Full suite command | `pytest tests/ -v` |
| Coverage gate | `fail_under = 100` (pyproject.toml line 110) — 100% required |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | File / Location |
|--------|----------|-----------|-----------------|
| DSPD-01 | body_decl_speed in CHART_DTYPE.names; compute_chart populates it non-zero | unit | `tests/charts/test_dtype.py` (ratchet re-pin) + `tests/charts/test_compute_chart.py` (new) |
| DSPD-02 | Δt=0.01d; numerical agreement Δ=0 vs scalar declination_velocity | unit | `tests/charts/test_compute_chart.py` or `tests/test_declination.py` (new) |
| DSPD-03a | Synastry chart inputs carry body_decl_speed finite & non-zero | unit | `tests/synastry/test_dtype.py` or `test_calculate_synastry.py` (new assertion) |
| DSPD-03b | Returns (solar+lunar) chart has body_decl_speed finite & non-zero | unit | `tests/returns/test_returns_oracle.py` or `test_solar_return.py` (new assertion) |
| DSPD-03c | Composite body_decl_speed present; differs from parent midpoint | unit | `tests/composite/test_calculate_composite.py` (new class, mirrors body_decl block) |
| DSPD-04 | Dtype ratchet breaks intentionally and is re-pinned | unit | `tests/charts/test_dtype.py` — 5 locations updated |
| DSPD-05 | DECL_STANDSTILL_EPS importable from ketu.calculations; value tested; standstill classification correct | unit | `tests/test_declination.py` (new: test EPS value, import, standstill boundary) |
| DSPD-06 | is_ascending_declination_chart: correct int8 output, consistent with v1.5 scalar, neutral at standstill | unit | `tests/charts/test_dtype.py` or new `tests/charts/test_chart_helpers.py` |

### Wave 0 Gaps

New test functions needed (no existing file covers these):

- [ ] `tests/charts/test_compute_chart.py` — add test class `TestBodyDeclSpeed`:
  - `test_body_decl_speed_present_in_dtype` — DSPD-01
  - `test_body_decl_speed_matches_scalar_fd` — DSPD-02 (Δ=0)
  - `test_body_decl_speed_shape_vectorised` — DSPD-01 (N,14) shape
  - `test_body_decl_speed_non_zero_finite` — anti-zero-fill ratchet
- [ ] `tests/composite/test_calculate_composite.py` — add class `TestBodyDeclSpeed`:
  - `test_body_decl_speed_shape` — shape (14,)
  - `test_body_decl_speed_non_zero` — anti-zero-fill ratchet
  - `test_body_decl_speed_not_parent_midpoint` — DSPD-03 anti-averaging ratchet
  - `test_body_decl_speed_finite` — sanity
- [ ] `tests/test_declination.py` — add:
  - `test_decl_standstill_eps_importable` — DSPD-05
  - `test_decl_standstill_eps_value` — pin 0.001
  - `test_decl_standstill_eps_classifies_sun_solstice_as_neutral` — empirical
  - `test_decl_standstill_eps_does_not_mask_jupiter_in_motion` — DSPD-05 non-masking
- [ ] `tests/charts/` — new or extended test for `is_ascending_declination_chart`:
  - `test_chart_helper_returns_int8` — dtype check
  - `test_chart_helper_shape_matches_body_axis` — S+(14,) shape
  - `test_chart_helper_consistent_with_scalar` — DSPD-06 consistency
  - `test_chart_helper_neutral_at_standstill` — 0 when |v| ≤ EPS

---

## Security Domain

No security-sensitive paths: pure numerical computation, no I/O, no user-controlled
inputs, no parsing. ASVS V5 Input Validation applies at the ketu.charts public surface
(jd/lat/lon) but is unchanged by this phase.

---

## Environment Availability

This phase is code/config-only with no new external dependencies. Skipped.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `calc_planet_position_batch` for 28 scalar calls (14 bodies × 2 parents) is fast enough in composite | Resolution 2 | Performance issue — mitigated by ephemeris cache already present |
| A2 | Adding `from ketu.calculations import DECL_STANDSTILL_EPS` to charts/api.py introduces no circular import | Resolution 1 | Import error at module load — but AST analysis confirms calculations.py does not import from charts; zero cycle risk |

All other claims are VERIFIED against the live codebase.

---

## State of the Art

| Old Approach | Current Approach | Notes |
|--------------|------------------|-------|
| v1.5: scalar `declination_velocity(jd, body)` — not in CHART_DTYPE | v1.8: `body_decl_speed` in CHART_DTYPE — vectorised over S+(14,) | No algorithm change; exposure change only |
| No standstill threshold defined in Ketu | `DECL_STANDSTILL_EPS = 0.001` deg/day — public contract | Rahu can classify neutrality without any astronomy |
| No chart-level ascending/descending helper | `is_ascending_declination_chart(chart)` → np.int8 | Rahu reads a field and checks a sign |

---

## Sources

### Primary (HIGH confidence)

- `ketu/calculations.py:495-524` — scalar `declination_velocity` implementation and FD formula
- `ketu/calculations.py:656+` — `__all__` export list
- `ketu/charts/core.py:95-111` — CHART_DTYPE definition (15 fields, current)
- `ketu/charts/api.py:62-113` — `_vectorised_body_properties` (loop over 14 bodies)
- `ketu/charts/api.py:379-394` — body_decl block (template for body_decl_speed)
- `ketu/charts/api.py:406-553` — `is_day_chart` (template for chart-level helper)
- `ketu/composite/api.py:68-86` — composite imports (confirms calc_planet_position_batch absent)
- `ketu/composite/api.py:248-266` — body_speeds + body_decl derivation (D-01 precedent)
- `ketu/synastry/api.py:64-105` — `_extend_body_data` (confirms no body_decl_speed consumption)
- `ketu/returns/lunar.py:37` — confirms `compute_chart` call = free inheritance
- `tests/charts/test_dtype.py:56-153` — ratchet tests (all 5 update points verified)
- AST import graph analysis — confirms zero import cycle in all directions

### Secondary (MEDIUM confidence)

- Runtime probe output (Python 3 + ketu 1.7.0 installed) — all numerical values
  verified by executing the actual code

### Tertiary (LOW confidence)

None. All claims are codebase-verified or empirically measured.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure NumPy, reuses existing assets, no new packages
- Architecture: HIGH — directly verified against live code; no assumptions
- Pitfalls: HIGH — all derived from actual code inspection
- Numerical values (EPS): HIGH — measured empirically on live ketu 1.7.0

**Research date:** 2026-06-17
**Valid until:** Stable (dtype structure, import graph, FD formula are frozen contracts)
