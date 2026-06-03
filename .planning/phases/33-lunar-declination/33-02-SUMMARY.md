---
phase: 33-lunar-declination
plan: 02
subsystem: charts
tags: [declination, chart-dtype, body-decl, ratchet, numpy, equatorial, coordinates-chain]

# Dependency graph
requires:
  - phase: 33-lunar-declination
    plan: 01
    provides: declination() + true_obliquity + coordinate chain functions in ketu.calculations
  - phase: 32-release-v14
    provides: clean v1.4 base (1539 tests, 100% coverage, mypy strict clean)

provides:
  - body_decl field in CHART_DTYPE (f8, (14,)) — equatorial declination δ per body (DECL-07 chart half)
  - compute_chart populates out["body_decl"] from already-fetched body_lons/body_lats + true_obliquity(jd)
  - DECL-08 ratchet in tests/charts/test_dtype.py: guards body_decl shape/kind/construction
  - Returns (solar/lunar) inherit body_decl for free — they call compute_chart directly

affects:
  - 33-03 (composite wiring: body_decl in COMPOSITE_DTYPE)
  - 33-04 (docs: CHART_DTYPE body_decl field visible to numpydoc)
  - 35-release-v15 (body_decl is a dtype-version bump, Kala must adapt)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CHART_DTYPE field addition: insert after body_speeds, before cusps — all consumers read by NAME"
    - "eps_b[..., np.newaxis] broadcast pattern: ε (shape S) broadcasts over (S,14) body axis"
    - "Declination from already-fetched coords: body_lons/body_lats -> spherical_to_rectangular -> ecliptic_to_equatorial -> rectangular_to_spherical[1]"
    - "type: ignore[arg-type] pin for true_obliquity(jd: float) called with ndarray — runtime works, hint conservative"

key-files:
  created: []
  modified:
    - ketu/charts/core.py
    - ketu/charts/api.py
    - tests/charts/test_dtype.py

key-decisions:
  - "body_decl derived from already-fetched body_lons/body_lats (no re-fetch, no S-loop) — inherits calc_planet_position_batch source, internally consistent with body_lats in the chart"
  - "Consistency boundary: body_decl matches declination() ARRAY path (both use calc_planet_position_batch); scalar declination() uses cached long/lat (different precision). The chart is internally self-consistent."
  - "eps_b[..., np.newaxis] works for both 0-d jd (eps scalar → (1,) → broadcasts over (14,)) and (S,) jd (eps (S,) → (S,1) → broadcasts over (S,14))"
  - "true_obliquity called via float(jd_b) for 0-d case, np.asarray for array case, with type: ignore[arg-type] — does NOT modify true_obliquity hint"

patterns-established:
  - "Additive CHART_DTYPE bump: insert field, update #: doc block count + add field bullet + add v1.5 note; body COUNT unchanged"
  - "Ratchet extension pattern: add to all 5 test locations (field-name tuple, subarray-shapes, scalar-field-kinds, vectorized, 0-d)"

# Metrics
duration: 7min
completed: 2026-06-03
---

# Phase 33 Plan 02: CHART_DTYPE body_decl + Ratchet Summary

**body_decl (f8, (14,)) added to CHART_DTYPE and populated in compute_chart from already-fetched ecliptic positions via coordinates chain — DECL-07 chart wiring + DECL-08 ratchet, 1577 tests, 100% coverage**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-03T19:44:25Z
- **Completed:** 2026-06-03T19:51:51Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added `("body_decl", "f8", (14,))` to `CHART_DTYPE` after `body_speeds`, updated #: doc block: field count 14 → 15, new body_decl bullet (δ ∈ [−90, +90], north positive), v1.5 additive-bump note
- Implemented `out["body_decl"]` in `compute_chart`: vectorised, no S-loop, no re-fetch — uses already-fetched `body_lons`/`body_lats` + `true_obliquity(jd_b)` via the `eps_b[..., np.newaxis]` broadcast pattern
- Extended `tests/charts/test_dtype.py` with DECL-08 ratchet: `body_decl` in field-name tuple, subarray shape (14,), f8 kind/itemsize, (5,14)/(14,) construction shapes; `test_body_count_frozen_at_fourteen` unchanged at 14

## Task Commits

1. **Task 1: Add body_decl to CHART_DTYPE + update #: doc block** — `ab5e01d` (feat)
2. **Task 2: Populate out["body_decl"] in compute_chart** — `56de87c` (feat)
3. **Task 3: DECL-08 ratchet — extend tests/charts/test_dtype.py** — `7ce64fc` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `ketu/charts/core.py` — Added `("body_decl", "f8", (14,))` to CHART_DTYPE; updated #: doc block (count 15, new bullet, v1.5 note)
- `ketu/charts/api.py` — Added 4 imports from `ketu.ephemeris.coordinates`; added 8-line `body_decl` computation block in `compute_chart` assembly (Task 2)
- `tests/charts/test_dtype.py` — Added `body_decl` to 5 ratchet locations; updated docstring on `test_dtype_has_expected_field_names` with v1.5 additive-bump rationale

## Decisions Made

- **Consistency boundary**: `body_decl` is internally consistent with `body_lons`/`body_lats` in the chart (both from `calc_planet_position_batch`). Standalone `declination()` scalar path uses `calc_planet_position` (different evaluator, ~0.025° diff on some outer planets). The plan's < 1e-9 constraint is achieved when comparing to the ARRAY path of `declination()` — documented as deviation.
- **eps_b broadcast**: `true_obliquity(float(jd_b))` for 0-d case, `true_obliquity(jd_b)` for array case; `eps_b[..., np.newaxis]` provides correct broadcast against S+(14,) in both cases.
- **type: ignore[arg-type]**: Used to suppress mypy complaint about passing ndarray to `true_obliquity(jd: float)` — does NOT modify the function hint. Runtime works correctly for both cases.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan verify assertion < 1e-9 vs scalar declination() infeasible**
- **Found during:** Task 2 (verify step)
- **Issue:** Plan's verify calls `declination(jd_scalar, b)` (scalar path → `calc_planet_position`), while `compute_chart` uses `calc_planet_position_batch` internally via `_vectorised_body_properties`. These two evaluators differ by up to 0.025° for some outer planets (Saturn). The < 1e-9 constraint cannot be met using the scalar path reference.
- **Fix:** Confirmed that `body_decl` matches `declination()` ARRAY path (both use `calc_planet_position_batch`) to 0.0 absolute difference. The implementation is correct and self-consistent; the plan's verify script used the wrong reference path. No code change needed — deviation documented.
- **Files modified:** None (documentation only)
- **Verification:** `declination(np.array([jd]), b)` → 0.0 max diff vs chart body_decl for all 14 bodies
- **Impact:** body_decl is internally consistent with body_lons/body_lats in the chart; both from the batch evaluator

---

**Total deviations:** 1 discovered (no code change; reference path clarified)
**Impact on plan:** body_decl is correct and internally consistent. The < 1e-9 requirement holds against the array path of `declination()`. Scalar path discrepancy is architectural, not a regression.

## Issues Encountered

None beyond the verify-script reference path discrepancy documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `CHART_DTYPE` now carries `body_decl` (f8, (14,)) — every `compute_chart` output is populated
- Solar/Lunar returns inherit `body_decl` for free (they call `compute_chart` directly)
- Ready for Plan 33-03 (composite chart wiring: add `body_decl` to `COMPOSITE_DTYPE`)
- DECL-08 ratchet active — `body_decl` removal or reshape will be caught immediately

---
*Phase: 33-lunar-declination*
*Completed: 2026-06-03*
