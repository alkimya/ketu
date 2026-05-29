---
phase: 24-chiron
plan: 05
subsystem: ephemeris, charts, cycles, cache, testing
tags: [chiron, integration, smoke-tests, docstrings, coverage, doctest, mypy, numpydoc]

# Dependency graph
requires:
  - phase: 24-chiron/24-03
    provides: "Chiron wired at all 6 insertion points; CHART_DTYPE (14,)/(14,14); 1361 tests green"

provides:
  - "tests/ephemeris/test_chiron_integration.py: 4 CHIR-05 smoke tests (chart/aspect/cycle/positions)"
  - "ketu/cache/ephemeris_cache.py: stale-cache body-count guard (ensure_month validates shape[1])"
  - "Docstring count fixes: (13,)→(14,) in 5 modules (charts, composite, returns)"
  - "All quality gates green at 14 bodies: 1373 tests, 100% coverage, 56 doctests, mypy clean"

affects:
  - "26 (Release 1.3.0): CHIR-01..05 all satisfied; UPGRADING note can reference these smoke tests)"
  - "Kala downstream: cache stale-file recompute is transparent (users with old ~/.ketu unaffected)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Stale-cache body-count guard in ensure_month: load .npy → validate shape[1]==BODY_COUNT → recompute+overwrite if mismatch"
    - "Integration smoke tests in tests/ephemeris/ — exercise full subsystem (chart/aspect/cycle) with one body as entry point"

key-files:
  created:
    - tests/ephemeris/test_chiron_integration.py
  modified:
    - ketu/cache/ephemeris_cache.py
    - ketu/__init__.py
    - ketu/charts/__init__.py
    - ketu/charts/api.py
    - ketu/composite/api.py
    - ketu/returns/solar.py
    - ketu/returns/lunar.py
    - tests/test_cache_coverage.py

key-decisions:
  - "Cache stale-file recompute transparent: users with old ~/.ketu/ephemeris_cache/*.npy get silent upgrade — no manual cache-clear needed"
  - "chiron.py modifications (jd_end param) left to plan 24-04 commit — coordination boundary respected"
  - "Docstring shape examples updated in-scope: (13,)→(14,) in charts/__init__, charts/api, composite/api, returns/solar, returns/lunar"
  - "Version stays 1.3.0 (per Phase 24 decision): public API additive; only internal positional contract breaks"

patterns-established:
  - "Integration smoke tests: 4-test pattern (chart shape, aspect_matrix shape, cycle series, all_positions) for verifying a new body end-to-end"

# Metrics
duration: 22min
completed: 2026-05-29
---

# Phase 24 Plan 05: Integration Smoke Tests + Quality Gates Summary

**CHIR-05 satisfied: 4 integration smoke tests prove Chiron flows through compute_chart/aspect_matrix/generate_cycle_series/calculate_all_positions with no special-casing; all quality gates green at 14 bodies (1373 tests, 100% coverage, 56 doctests, mypy strict clean)**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-05-29T22:05:00Z
- **Completed:** 2026-05-29T22:27:00Z
- **Tasks:** 2/2
- **Files created:** 1
- **Files modified:** 7

## Accomplishments

- `tests/ephemeris/test_chiron_integration.py` (4 tests) — CHIR-05 smoke test suite:
  - `test_compute_chart_includes_chiron`: body_lons.shape==(14,), Chiron lon finite/in[0,360), matches calc_planet_position(jd,13), within 0.01° of J2000 oracle
  - `test_aspect_matrix_covers_chiron`: shape==(14,14), diagonal==-1, Chiron row has ≥1 off-diagonal non-sentinel, symmetry D-17
  - `test_cycle_series_with_chiron`: generate_cycle_series("Sun","Chiron",...) returns CYCLE_DTYPE with body2_id==13, finite angular_separation/cycle_progress
  - `test_calculate_all_positions_has_14`: 14-entry dict, "Chiron" key at index 13, finite lon, consistent with calc_planet_position
- `ketu/cache/ephemeris_cache.py` stale-cache guard: load .npy → validate shape[1]==BODY_COUNT; recompute+overwrite if mismatch (transparent upgrade from 13-body to 14-body cache files)
- Docstring updates: 5 module docstrings/examples fixed (charts/__init__, charts/api, composite/api, returns/solar, returns/lunar) — 7 individual (13,) → (14,) / (13,13) → (14,14) / 78→91 body-pair fixes
- `ketu/__init__.py` Body IDs updated to include `13=Chiron (Centaur, v1.3 D-08)`
- Quality gate run: 1373 passed / 2 skipped / 0 failed / 100% coverage / 56 doctests / mypy strict 68 files clean / interrogate 99.7% / numpydoc lint clean

## CHIR Requirements Status

| Req | Description | Status |
|-----|-------------|--------|
| CHIR-01 | Generator + ketu/data/chiron_coeffs.npz | Satisfied (plan 24-01) |
| CHIR-02 | Chiron evaluator ketu/ephemeris/chiron.py | Satisfied (plan 24-02) |
| CHIR-03 | D-08 breaking change 13→14 | Satisfied (plan 24-03) |
| CHIR-04 | Accuracy regression vs oracle (plan 24-04) | Satisfied (plan 24-04) |
| CHIR-05 | Participates with no special-casing | **Satisfied (this plan)** |

## Task Commits

1. **Task 1: CHIR-05 integration smoke tests + cache stale-file fix** — `30f8a80` (feat)
2. **Task 2: Docstring touch-ups + quality gates verified** — `b47dab1` (feat)

## Files Created/Modified

- `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_integration.py` — 4 CHIR-05 smoke tests (chart/aspect/cycle/positions)
- `/home/loc/workspace/ketu/ketu/cache/ephemeris_cache.py` — stale-cache body-count guard in ensure_month
- `/home/loc/workspace/ketu/ketu/__init__.py` — Body IDs docstring: added 13=Chiron
- `/home/loc/workspace/ketu/ketu/charts/__init__.py` — example (2,13)/(2,13,13)→(2,14)/(2,14,14); Notes updated
- `/home/loc/workspace/ketu/ketu/charts/api.py` — 7 stale docstring fixes: (13,13)→(14,14), 78→91 upper-triangle, loop bound, shape examples, Notes
- `/home/loc/workspace/ketu/ketu/composite/api.py` — doctest (13,)→(14,)
- `/home/loc/workspace/ketu/ketu/returns/solar.py` — doctest (13,)→(14,)
- `/home/loc/workspace/ketu/ketu/returns/lunar.py` — doctest (13,)→(14,)
- `/home/loc/workspace/ketu/tests/test_cache_coverage.py` — TestStaleCacheBodyCountMismatch covering lines 158-159

## Decisions Made

- Cache stale-file recompute is silent and transparent — users with old `~/.ketu/ephemeris_cache/` files (shape (days,13,6)) will have them regenerated on first access, no user action required.
- chiron.py modifications observed in working tree (jd_end param) were left to plan 24-04's commit scope.
- Version stays 1.3.0 per Phase 24 decision: public API additive.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] EphemerisCache IndexError on body_id=13 with stale .npy files**
- **Found during:** Task 1 (test_cycle_series_with_chiron writing)
- **Issue:** `generate_cycle_series("Sun","Chiron",...)` raised `IndexError: index 13 is out of bounds for axis 1 with size 13` when `~/.ketu/ephemeris_cache/` contained old files built pre-Chiron (shape `(days, 13, 6)`). `ensure_month` loaded them without validating body count.
- **Fix:** Added shape validation in `ensure_month` disk-load branch: if `data.shape[1] != BODY_COUNT`, recompute month and overwrite disk file.
- **Files modified:** `ketu/cache/ephemeris_cache.py`, `tests/test_cache_coverage.py`
- **Verification:** `test_stale_cache_body_count_triggers_recompute` PASSED; `test_cycle_series_with_chiron` PASSED
- **Committed in:** `30f8a80` (Task 1)

**2. [Rule 1 - Bug] 5 stale doctest examples (13,) / (13,13) in charts/composite/returns docstrings**
- **Found during:** Task 2 (make doctest gate)
- **Issue:** `make doctest` reported 5 failures: ketu/charts/__init__.py, ketu/charts/api.py, ketu/composite/api.py, ketu/returns/lunar.py, ketu/returns/solar.py — all had `(13,)` or `(13, 13)` shape examples. These were not updated in plan 24-03.
- **Fix:** Updated all 5 files with correct `(14,)` / `(14, 14)` shapes and 7 associated text fixes (78→91 body-pair, Notes body count).
- **Files modified:** 5 source files listed above.
- **Verification:** `make doctest` → 56 passed, 1 skipped, 0 failed.
- **Committed in:** `b47dab1` (Task 2)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs/stale counts missed by 24-03)
**Impact on plan:** Both corrections required for correctness. No scope creep.

## Issues Encountered

None beyond the two auto-fixed deviations.

## Quality Gates Summary

| Gate | Command | Result |
|------|---------|--------|
| pytest full suite | `pytest tests/ -q` | 1373 passed, 2 skipped, 0 failed |
| Coverage 100% | `pytest --cov=ketu --cov-report=term-missing` | 100.00% (fail_under=100) |
| Doctests | `make doctest` | 56 passed, 1 skipped, 0 failed |
| mypy strict | `python -m mypy ketu/ --strict` | Success: no issues in 68 files |
| interrogate | `python -m interrogate ketu/` | 99.7% (minimum 95%) |
| numpydoc lint | `python -m numpydoc lint ...` | Clean (no output) |

## Note for Phase 26 UPGRADING

The `test_chiron_integration.py::test_cycle_series_with_chiron` test confirms that the cache's `ensure_month` stale-file guard is in place. Any Kala consumer or end-user with a `~/.ketu/ephemeris_cache/` directory populated before v1.3 will have their cache transparently upgraded on first access — no manual step needed. The UPGRADING note in Phase 26 should document:

1. **Breaking positional-array contract**: `body_lons`, `body_lats`, `body_speeds` now have shape `(..., 14)` — Kala must update any hardcoded `13` index to `14` and any `body_id=12` guard to `body_id=13` for Lilith.
2. **Cache transparency**: Old cache files auto-recompute — first call after upgrade takes a few seconds per month.
3. **SYNASTRY_BODY_COUNT**: 15→16 (ASC=14, MC=15).

## Self-Check: PASSED

### Files created check

- `tests/ephemeris/test_chiron_integration.py` — FOUND
- `tests/test_cache_coverage.py` (modified) — FOUND

### Commits check

- `30f8a80` — Task 1 (feat(24-05): CHIR-05 integration smoke tests + cache stale-file fix)
- `b47dab1` — Task 2 (feat(24-05): docstring/version touch-ups + all quality gates green at 14 bodies)

### Suite check

- 1373 passed, 2 skipped, 0 failed, 100% coverage
- No swisseph import in ketu/
- CHIR-05 satisfied: all 4 smoke tests green

---
*Phase: 24-chiron*
*Completed: 2026-05-29*
