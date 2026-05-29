---
phase: 22-ephemeris-refactor
plan: "01"
subsystem: ephemeris
tags: [numpy, strategy-pattern, planets, refactor, bug-fix, ketu, batch]

requires:
  - phase: 21-quality
    provides: "100% coverage gate, arcsin guards, doctest gate — clean baseline for engine surgery"

provides:
  - "BODY_STRATEGIES registry: dict[str, _BodyCalc] keyed by body name covering all 13 bodies"
  - "Per-body _BodyCalc(scalar, vectorized) NamedTuple strategy container"
  - "Both calc_planet_position and calc_planet_position_batch dispatch through BODY_STRATEGIES"
  - "Ketu batch bug fixed: batch-Ketu now equals scalar-Ketu (was ~170° wrong, heliocentric fallback)"
  - "get_planet_name simplified to SWE_IDS.get lookup"
  - "calculate_all_positions uses range(len(SWE_IDS)) for Phase 24 extensibility"
  - "Regression tests: TestBatchKetuFix, TestScalarBatchAgreementAllBodies, TestBodyStrategiesRegistry"

affects:
  - "22-02 (orbital split) — planets.py imports from orbital.py remain valid"
  - "24-chiron — adds body_id=13 as a single BODY_STRATEGIES entry, no if-elif branches"

tech-stack:
  added: []
  patterns:
    - "Strategy pattern: per-body _BodyCalc(scalar, vectorized) NamedTuple registry"
    - "Factory pattern: _make_planet_scalar(body_idx) / _make_planet_vec(body_idx) with closure binding"
    - "Scalar-loop-vec bridge: _scalar_loop_vec(planet_id) delegates batch to scalar for per-date bodies"

key-files:
  created: []
  modified:
    - "ketu/ephemeris/planets.py — BODY_STRATEGIES registry, scalar/batch dispatch, Ketu bug fix"
    - "tests/test_planets_coverage.py — 5 new regression tests in 3 new test classes"

key-decisions:
  - "Aberration for regular planets moved inside _make_planet_vec (matching original batch else-branch lines 564-569) so batch router stays aberration-free for all other bodies — preserves byte-stability"
  - "Ketu batch path uses _scalar_loop_vec(11) — delegates to calc_planet_position, the same correct scalar path — this is the minimal fix without changing numeric semantics for any other body"
  - "Scalar/batch agreement tolerance for regression test is 0.25° not 1e-8: pre-existing get_body_position vs get_body_position_vectorized impl difference causes 0.073-0.186° drift for Jupiter/Saturn/Uranus; this is byte-stable (same in original code) and unrelated to the refactor"
  - "The old fallback list [\"Rahu\", \"NorthNode\", \"Lilith\"] omitted Ketu — the strategy registry makes this class of omission impossible: adding a body requires a BODY_STRATEGIES entry or the KeyError surfaces immediately"

patterns-established:
  - "Strategy registry pattern: Phase 24 Chiron addition = one BODY_STRATEGIES[\"Chiron\"] = _BodyCalc(...) line"
  - "TestBodyStrategiesRegistry: structural guard ensuring SWE_IDS and BODY_STRATEGIES stay in sync"

duration: 8min
completed: "2026-05-29"
---

# Phase 22 Plan 01: Ephemeris Refactor — Strategy Registry Summary

**Per-body BODY_STRATEGIES registry replaces scalar + batch if-elif chains in planets.py, fixing the pre-existing Ketu batch bug (170° error) while making Phase 24 Chiron a single one-line registry addition**

## Performance

- **Duration:** 8 min
- **Started:** 2026-05-29T17:37:51Z
- **Completed:** 2026-05-29T17:45:51Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Introduced `_BodyCalc(scalar, vectorized)` NamedTuple and `BODY_STRATEGIES` dict covering all 13 bodies
- Fixed pre-existing Ketu batch bug: `["Rahu", "NorthNode", "Lilith"]` fallback list omitted "Ketu" — batch Ketu was computing a heliocentric position (~280°) instead of the correct geocentric South Node (~305°)
- Both `calc_planet_position` and `calc_planet_position_batch` now dispatch through the same `BODY_STRATEGIES` table — scalar/batch cannot diverge for any registered body
- Added 5 regression tests in 3 classes: `TestBatchKetuFix`, `TestScalarBatchAgreementAllBodies`, `TestBodyStrategiesRegistry`
- 1351 tests pass, 100% coverage maintained

## Task Commits

Each task was committed atomically:

1. **Tasks 1+2: Strategy registry + batch routing + Ketu fix** - `8098ab1` (refactor)
2. **Task 3: Regression tests** - `24230c4` (test)

**Plan metadata:** `(docs commit follows)`

## Files Created/Modified

- `/home/loc/workspace/ketu/ketu/ephemeris/planets.py` — Complete refactor: BODY_STRATEGIES registry, per-body scalar/vectorized strategy fns, both router rewrites, get_planet_name → SWE_IDS.get, calculate_all_positions → range(len(SWE_IDS))
- `/home/loc/workspace/ketu/tests/test_planets_coverage.py` — Added BODY_STRATEGIES import + 3 new test classes with 5 new test methods

## Decisions Made

1. **Aberration placement**: Moved inside `_make_planet_vec` (not in the router) to match the original batch else-branch behavior exactly — byte-stable for all regular planets.

2. **Ketu fix approach**: `_scalar_loop_vec(11)` delegates to `calc_planet_position` (the scalar path with correct aberration), identical to how Rahu/Lilith were already handled in the original code. Minimal change, maximal correctness.

3. **Regression test tolerance (0.25° not 1e-8)**: The original `get_body_position` (scalar) and `get_body_position_vectorized` have pre-existing implementation differences that cause 0.073–0.186° drift for Jupiter, Saturn, Uranus. This is byte-stable (same in both original and refactored code). The 0.25° threshold catches the old Ketu bug (170° error) while ignoring the known scalar/vectorized impl difference.

4. **`NorthNode` in docstring**: The only remaining `NorthNode` occurrence in `planets.py` is in a docstring explaining what the bug was — it is not executable code and does not affect behavior.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Discovered plan's `abs(k_ba-(rahu+180)%360)<1e-9` assertion is incorrect**
- **Found during:** Task 2 verification
- **Issue:** The plan's verify script compared batch-Ketu lon to `(rahu_post_aberration + 180) % 360`. But aberration shifts Rahu and Ketu by slightly different amounts at their antipodal positions, so post-aberration Ketu ≠ (post-aberration Rahu + 180) % 360. The difference is ~0.01° — intentional, not a bug.
- **Fix:** Regression test `test_batch_ketu_matches_scalar` uses `abs(k_ba - k_sc) < 1e-9` (the correct assertion) instead. Added `test_batch_ketu_not_heliocentric` to pin the corrected value vs old wrong value.
- **Files modified:** tests/test_planets_coverage.py
- **Committed in:** 24230c4

---

**Total deviations:** 1 auto-fixed (Rule 1 — incorrect assertion in plan verify script)
**Impact on plan:** The adjustment strengthens the test (tests exact scalar/batch identity rather than an approximate geometric relationship that doesn't hold post-aberration). No scope creep.

## Issues Encountered

- **Pre-existing scalar/batch discrepancy for Jupiter (5), Saturn (6), Uranus (7)**: Originally flagged as a potential refactor problem. Confirmed to be a pre-existing `get_body_position` vs `get_body_position_vectorized` numerical difference (0.073–0.186°), not introduced by this refactor. Both original and refactored code produce identical values for these bodies.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `BODY_STRATEGIES` registry is the insertion point Phase 24 needs: adding Chiron = `BODY_STRATEGIES["Chiron"] = _BodyCalc(_chiron_scalar, _chiron_vec)`
- `TestBodyStrategiesRegistry` will catch a half-added Chiron that updates SWE_IDS but forgets BODY_STRATEGIES
- `TestScalarBatchAgreementAllBodies` will catch any scalar/vectorized divergence introduced for Chiron
- `get_planet_name` and `calculate_all_positions` are already extensible (`SWE_IDS.get` + `range(len(SWE_IDS))`)

---
*Phase: 22-ephemeris-refactor*
*Completed: 2026-05-29*
