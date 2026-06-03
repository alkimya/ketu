---
phase: 33-lunar-declination
plan: 01
subsystem: ephemeris
tags: [declination, equatorial-coordinates, coordinates-chain, meeus, oob, numpy, vectorized]

# Dependency graph
requires:
  - phase: 32-release-v14
    provides: clean v1.4 base (1539 tests, 100% coverage, mypy strict clean)
  - phase: 21-quality
    provides: coverage gate fail_under=100, doctest gate

provides:
  - declination(jdate, body) — scalar + vectorized δ via coordinates chain (DECL-01, DECL-02)
  - declination_velocity(jdate, body) — dδ/dt forward FD step=0.01 (DECL-04)
  - is_ascending_declination(jdate, body) — True iff dδ/dt > 0, distinct from β-based is_ascending (DECL-05)
  - is_out_of_bounds(jdate, body) — True iff |δ| > true_obliquity(jd) (DECL-06)
  - DECL-03 equivalence regression (declination() == explicit chain == Meeus 13.4, max|Δ| < 1e-9)
  - All four in __all__; is_ascending (β) unchanged

affects:
  - 33-02 (chart wiring: body_decl in CHART_DTYPE depends on these functions)
  - 33-03 (composite wiring)
  - 33-04 (docs for the new public surface)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Vectorized declination: scalar path uses cached long/lat; array path uses calc_planet_position_batch (loop-free)"
    - "Forward FD step=0.01 for declination velocity (no wraparound, δ bounded)"
    - "instantaneous ε = true_obliquity(jd) for OOB threshold (not mean_obliquity)"
    - "DECL-03 equivalence regression guards chain integrity against Meeus 13.4"

key-files:
  created:
    - tests/test_declination.py
  modified:
    - ketu/calculations.py
    - tests/test_coordinates_coverage.py

key-decisions:
  - "Scalar path uses cached long/lat; array path uses calc_planet_position_batch — long/lat do NOT broadcast over jdate arrays (unhashable type)"
  - "true_obliquity (instantaneous ε) used for OOB threshold, not mean_obliquity — per STATE.md lock"
  - "Forward FD step=0.01 mirrors package-wide lat_velocity idiom; no wraparound needed (δ bounded in [−90,+90])"
  - "is_ascending_declination proved distinct from β-based is_ascending at 2025-03-07 (major standstill)"

patterns-established:
  - "All four functions added to __all__; nothing added to ketu/__init__.py (submodule-import convention)"
  - "Docstrings use numpydoc style with runnable >>> examples verified against make doctest"

# Metrics
duration: 6min
completed: 2026-06-03
---

# Phase 33 Plan 01: Declination Foundation Summary

**Four equatorial-declination helpers (scalar + vectorized δ, dδ/dt, montant/descendant, OOB) added to ketu.calculations via the coordinates chain — proven equivalent to Meeus 13.4 to 7e-15, fully tested (1575 tests, 100% coverage)**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-03T19:34:51Z
- **Completed:** 2026-06-03T19:41:13Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Implemented `declination`, `declination_velocity`, `is_ascending_declination`, `is_out_of_bounds` in `ketu/calculations.py` with numpydoc docstrings and runnable `>>>` examples
- Vectorized `declination()` without a Python loop: scalar path via cached `long`/`lat`, array path via `calc_planet_position_batch`
- Added DECL-03 equivalence regression to `tests/test_coordinates_coverage.py`: `declination()` ≡ explicit chain ≡ Meeus 13.4 (max|Δ| < 1e-9, 50 dates, Moon + Sun)
- Created `tests/test_declination.py` with 32 tests covering DECL-01/02/04/05/06, all 14 bodies, OOB true/false, β-vs-δ independence proof at 2025-03-07

## Task Commits

1. **Task 1: Add four declination functions to calculations.py** — `6183bad` (feat)
2. **Task 2: DECL-03 equivalence regression** — `ad11073` (test)
3. **Task 3: Unit + vectorization tests** — `60da1f9` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `ketu/calculations.py` — Added 5 imports + 4 functions (160 lines) + 4 names in `__all__`; `is_ascending` byte-for-byte unchanged
- `tests/test_declination.py` — 302 lines, 32 tests covering DECL-01/02/04/05/06 + all-14-bodies
- `tests/test_coordinates_coverage.py` — Added `TestDeclinationEquivalenceDECL03` (87 lines, 6 tests)

## Decisions Made

- **Scalar/array dispatch**: `long`/`lat` reject array `jdate` (lru_cache + unhashable). Solution: `np.ndim(jdate) == 0` dispatches scalar to `long`/`lat`, array to `calc_planet_position_batch`. Both paths are loop-free.
- **OOB via `true_obliquity`**: Per STATE.md lock. `mean_obliquity` is NOT used (nutation component non-zero, confirmed by test).
- **FD step = 0.01**: Mirrors `lat_velocity` FD idiom. No wraparound needed — δ ∈ [−90,+90] is bounded and continuous.
- **β-vs-δ divergence confirmed**: At 2025-03-07 (JD=2460742.0), Moon near declination peak (δ≈+28.66°), `is_ascending_declination=True` (vel=+0.30°/day) while `is_ascending=False` (β descending). This date is hardcoded in the test.

## Deviations from Plan

None — plan executed exactly as written. The scalar/array dispatch strategy was the only discovery: `long`/`lat` reject array `jdate` due to `lru_cache` (the plan anticipated this with the `calc_planet_position_batch` fallback).

## Issues Encountered

None. All gates green on first run: `make test` (1575 tests, 100% coverage), `make doctest` (64 passed), `make doc-gates` (99.7%), `make mypy` (success).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `declination()`, `declination_velocity()`, `is_ascending_declination()`, `is_out_of_bounds()` are importable from `ketu.calculations` and ready for Phase 33 Plan 02 (body_decl in CHART_DTYPE)
- No blockers. The OOB major-standstill window (2025, Moon δ up to 28.7°) is well-exercised

---
*Phase: 33-lunar-declination*
*Completed: 2026-06-03*
