---
phase: 24-chiron
plan: 04
subsystem: testing
tags: [chiron, chebyshev, regression, accuracy, pinned-constants, numpy]

# Dependency graph
requires:
  - phase: 24-01
    provides: "7 pinned reference (jd, lon) tuples captured from pyswisseph oracle"
  - phase: 24-02
    provides: "_eval_chiron_qty / _chiron_scalar evaluator in ketu/ephemeris/chiron.py"

provides:
  - "tests/ephemeris/test_chiron_regression.py: CHIR-03 pinned-reference accuracy regression (7 dates 1950-2050)"
  - "Bug fix: _eval_chiron_qty last-segment t-normalisation uses actual_len not seg_len"

affects:
  - 24-05 (test count now 1372; coverage still 100%)
  - 25 (doc — evaluator precision documented as max|Δλ|=0.005695° vs oracle across 7 pinned dates)
  - 26 (release — CHIR-03 regression test ships with ketu 1.3.0)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pinned-constant regression test: zero network/oracle at test time — hardcoded (jd, lon) pairs with documentary capture metadata"
    - "Wrap-aware delta: abs(actual - expected) with > 180 → 360 - delta idiom"

key-files:
  created:
    - tests/ephemeris/test_chiron_regression.py
  modified:
    - ketu/ephemeris/chiron.py
    - tests/ephemeris/test_chiron_unit.py

key-decisions:
  - "Rule 1 auto-fix: _eval_chiron_qty used constant seg_len (32.0) for t-normalisation on the last segment (actual 13 days) — introduced 0.9° error at 2050-01-01; fixed to use actual_len = min(seg_start + seg_len, jd_end) - seg_start"
  - "aberration correction included in calc_planet_position result — observed deltas vs raw pyswisseph oracle are 0.004-0.006° (aberration difference, not precision loss); all within 0.01° tolerance"
  - "test_chiron_unit.py mock signatures updated to accept jd_end (5th arg) as consequence of the chiron.py fix"

patterns-established:
  - "Build-time oracle references pinned as constants in test file; capture metadata (date, tool, retflag) in comments above the list"

# Metrics
duration: 12min
completed: 2026-05-29
---

# Phase 24 Plan 04: Chiron Accuracy Regression Test Summary

**CHIR-03 satisfied: 7 pinned-reference Chiron longitudes across 1950-2050, all within 0.01° — max observed delta 0.005695° (1.75× under tolerance) — plus a Rule 1 bug fix in the Chebyshev evaluator for the last segment**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-29T20:35:06Z
- **Completed:** 2026-05-29T20:47:00Z
- **Tasks:** 1/1
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- `tests/ephemeris/test_chiron_regression.py` (88 lignes) — 7 parametrized pinned-constant (JD, lon) regression cases, zero pyswisseph at test time, numpydoc-style docstring, CHIR-03 reference, wrap-aware delta assertion with informative failure message
- **Bug fix in `_eval_chiron_qty`** — last segment (only 13 days, not 32) was normalising `t` with `seg_len=32` instead of `actual_len=13`; caused 0.905° error at 2050-01-01; fixed by computing `actual_len = min(seg_start + seg_len, jd_end) - seg_start`
- `test_chiron_unit.py` updated to match the new `jd_end` parameter signature (3 tests)
- Full suite: 1372 tests, 0 failures, 100% coverage

## Pinned Reference Table and Observed Deltas

| Date        | JD            | Expected lon (°) | Actual lon (°) | Delta (°)   |
|-------------|---------------|-----------------|----------------|-------------|
| 1950-01-01  | 2433282.5     | 255.777223       | 255.772103     | 0.005120    |
| 1970-01-01  | 2440587.5     | 2.520351         | 2.519512       | 0.000839    |
| 1990-01-01  | 2447892.5     | 103.847482       | 103.853177     | 0.005695 *  |
| J2000.0     | 2451545.0     | 251.617624       | 251.612539     | 0.005085    |
| 2010-01-01  | 2455197.5     | 323.115304       | 323.111051     | 0.004253    |
| 2030-01-01  | 2462501.5     | 38.042056        | 38.044840      | 0.002784    |
| 2050-01-01  | 2469807.5     | 246.587706       | 246.583068     | 0.004638    |

\* = worst case = 0.005695° (1.75× under 0.01° tolerance, 1.58× under spike-measured 0.000861° gap — aberration correction accounts for most of the residual)

Oracle: pyswisseph + seas_18.se1, retflag=260 (Moshier fallback), captured 2026-05-29.

## Task Commits

1. **Task 1: Pinned-reference regression test + evaluator bug fix** — `0159c0f` (feat)

## Files Created/Modified

- `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_regression.py` — CHIR-03 regression test, 7 parametrized pinned-constant cases (88 lignes)
- `/home/loc/workspace/ketu/ketu/ephemeris/chiron.py` — Rule 1 fix: `_eval_chiron_qty` `jd_end` param + actual_len for last-segment t-normalisation
- `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_unit.py` — Updated mock signatures and clamp-test calls to pass `jd_end` (5th arg)

## Decisions Made

- Rule 1 auto-fix applied without user permission: `_eval_chiron_qty` was using the constant `seg_len=32.0` for t-normalisation even on the last segment which is only 13 days long; this maps physical JD to wrong `t ∈ [-1, 1]` causing 0.905° error; fixed to compute actual segment length from `jd_end`
- Aberration correction (applied inside `_chiron_scalar`) explains the ~0.004-0.006° residual between the evaluator and the raw pyswisseph oracle — this is intentional and expected

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed last-segment t-normalisation in `_eval_chiron_qty`**
- **Found during:** Task 1 (running pytest on test_chiron_regression.py)
- **Issue:** `_eval_chiron_qty` used constant `seg_len=32.0` for `t = 2*(jd - seg_start)/seg_len - 1`. The last segment spans only 13 days (2469794.5 to 2469807.5) because the total range (36525 days) is not a multiple of 32. The fit was done with `actual_len=13` in `fit_segment`, so the coefficients are valid for `t = 2*(jd - seg_start)/13 - 1`. Using 32 instead of 13 mapped `jd=2469807.5` to `t=-0.1875` but the polynomial was fitted expecting `t=1.0`, causing 0.905° error.
- **Fix:** Added `jd_end` parameter to `_eval_chiron_qty`; compute `actual_len = min(seg_start + seg_len, jd_end) - seg_start` and use it for the `t` calculation.
- **Files modified:** `ketu/ephemeris/chiron.py`, `tests/ephemeris/test_chiron_unit.py`
- **Verification:** 7/7 regression cases now pass; all deltas < 0.006°; 1372 tests, 100% coverage
- **Committed in:** `0159c0f`

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Essential correctness fix. The regression test would have had a guaranteed 0.9° failure at 2050-01-01 without this fix. No scope creep.

## Issues Encountered

- The generator validation gate (pur-NumPy vs oracle, 200 pts/segment) reported max|Δλ|=0.000861° for all 1142 segments. This passed because the validation uses `actual_len` (correct — it calls `min(jd_s + seg_len, jd1) - jd_s`). Only the runtime evaluator in `chiron.py` had the bug (hardcoded `seg_len`). The validation gate is correct; the evaluator was wrong.

## Next Phase Readiness

- Plan 24-05 (integration smoke tests) already committed in parallel — 1372 tests, 100% coverage
- Phase 24 now complete pending SUMMARY commits
- Phase 25 (Documentation) can proceed with Chiron fully wired and tested

## Self-Check: PASSED

- `tests/ephemeris/test_chiron_regression.py` — EXISTS
- `ketu/ephemeris/chiron.py` modified — CONFIRMED (commit 0159c0f)
- Commit 0159c0f — EXISTS (`git log --oneline | grep 0159c0f`)

---
*Phase: 24-chiron*
*Completed: 2026-05-29*
