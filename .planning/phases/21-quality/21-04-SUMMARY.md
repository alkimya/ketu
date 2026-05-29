---
phase: 21-quality
plan: "04"
subsystem: testing
tags: [coverage, pytest, pyproject, ci, github-actions, quality-gate]

requires:
  - phase: 21-quality/21-01
    provides: "62 gap tests closing all non-orbital-guard gaps; 4 dead-code branches documented for exclude_lines"
  - phase: 21-quality/21-02
    provides: "9 arcsin div/0 guards in orbital.py + coordinates.py; div/0 regression tests"
  - phase: 21-quality/21-03
    provides: "52 runnable doctests across public API; doctest gate wired in Makefile + CI"

provides:
  - "fail_under = 100 in pyproject.toml [tool.coverage.report] — project coverage gate is 100%"
  - "CI 3.13 'Check coverage threshold' step uses --cov-fail-under=100"
  - "5 exclude_lines entries for runtime-unreachable branches (no pragmas added)"
  - "9 new tests in TestAspectsCalculatorMissingPaths covering aspects/calculator.py and calculations.py gaps"
  - "pytest --cov-fail-under=100 PASSES: 1346 tests, TOTAL 100%, zero pragmas"

affects: [22-ephemeris-refactor, 26-release-1-3-0]

tech-stack:
  added: []
  patterns:
    - "exclude_lines for TYPE_CHECKING guard — standard coverage.py idiom, preserves zero-pragma policy"
    - "exclude_lines for post-modulo < 0 defensive branches — proven dead code after Python modulo"
    - "Single-body slice trick to force empty-result path in vectorized aspect functions"
    - "In-orb JD selection for find_aspect_timing loop-body coverage (lines 429/442)"

key-files:
  created:
    - ".planning/phases/21-quality/21-04-SUMMARY.md"
  modified:
    - "pyproject.toml — fail_under 70→100; 5 new exclude_lines entries"
    - ".github/workflows/tests.yml — coverage threshold step: 70→100"
    - "tests/test_coverage_improvements.py — TestAspectsCalculatorMissingPaths (9 tests, Rule 3 deviation)"

key-decisions:
  - "5 exclude_lines entries added (not pragmas): TYPE_CHECKING (display.py:27), if angle < 0: (orbital.py:226), if gst < 0: (time.py:368), if avg_speed == 0: (planets.py:447), return \\(jd_left \\+ jd_right\\) / 2 (planets.py:362) — all proven dead code"
  - "9 new gap tests written (Rule 3 auto-fix) to cover aspects/calculator.py and calculations.py:382 — lines not in original RESEARCH inventory, present but untested in baseline"
  - "Zero pragmas added: zero-pragma policy maintained throughout Phase 21"
  - "omit list unchanged: ketu/__main__.py and ketu/lunar_calendar.py remain excluded as documented"

patterns-established:
  - "exclude_lines pattern for TYPE_CHECKING: standard coverage.py practice, preserves zero-pragma discipline"
  - "In-orb date selection for aspect timing test: choose JD where separation < orb to exercise loop-body lines"

duration: 11min
completed: "2026-05-29"
---

# Phase 21 Plan 04: Coverage Gate Flip Summary

**fail_under 70→100 in pyproject.toml, 5 dead-code branches excluded via exclude_lines (no pragmas), CI gate flipped to 100%, and 9 gap tests added — QAL-10 fully delivered with 1346 tests at 100% coverage.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-05-29T17:05:20Z
- **Completed:** 2026-05-29T17:16:35Z
- **Tasks:** 2 (+ 1 Rule-3 deviation fix folded into Task 1)
- **Files modified:** 3

## Accomplishments

- `pyproject.toml`: `fail_under` lifted from 70 to 100; 5 `exclude_lines` entries for runtime-unreachable defensive branches (no `# pragma: no cover` anywhere)
- `.github/workflows/tests.yml`: CI "Check coverage threshold" step (3.13 only) changed from `--cov-fail-under=70` to `--cov-fail-under=100`
- Rule-3 deviation: 9 new tests in `TestAspectsCalculatorMissingPaths` covering `aspects/calculator.py` lines 74, 249, 380, 410-450, 497-502, 507 and `calculations.py:382` — all lines missing from the original RESEARCH inventory but required for the 100% gate
- Final result: `pytest --cov-fail-under=100` PASSES (1346 passed, 2 skipped, TOTAL 100%)

## Task Commits

1. **Task 1: Exclude TYPE_CHECKING + lift fail_under to 100** — `e7b7bbb` (chore)
   *Includes Rule-3 deviation: 9 gap tests for aspects/calculator.py and calculations.py*
2. **Task 2: Flip CI coverage gate to 100** — `98892ef` (chore)

## Files Created/Modified

- `pyproject.toml` — `fail_under = 100`; 5 `exclude_lines` entries for dead-code branches
- `.github/workflows/tests.yml` — coverage threshold step: `--cov-fail-under=70` → `--cov-fail-under=100`
- `tests/test_coverage_improvements.py` — `TestAspectsCalculatorMissingPaths` class (9 tests)

## Decisions Made

- **exclude_lines over pragmas for 5 dead branches**: `if TYPE_CHECKING:` (display.py:27), `if angle < 0:` (orbital.py:226), `if gst < 0:` (time.py:368), `if avg_speed == 0:` (planets.py:447), `return \(jd_left \+ jd_right\) / 2` (planets.py:362). All proven unreachable in normal Python execution. Config-level exclusion preserves the zero-pragma policy established in Phase 21.
- **Zero pragmas maintained**: grep confirms no `# pragma: no cover` in `ketu/` source — policy intact.
- **omit list untouched**: `ketu/__main__.py` and `ketu/lunar_calendar.py` remain excluded as per CONTEXT decision.
- **per-subpackage 95% Makefile gates kept as-is**: project 100% dominates them de facto; no Makefile rewrites.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 39 lines still uncovered after exclude_lines applied**
- **Found during:** Task 1 verification (first --cov-fail-under=100 run)
- **Issue:** The baseline coverage report had shown 98.63% with 44 missing lines. After the 5 exclude_lines entries covered the documented dead-code branches, the remaining 39 lines (38 in `aspects/calculator.py` + 1 in `calculations.py`) became visible. These lines were NOT in the original RESEARCH inventory and were not assigned to any prior plan. They blocked the 100% gate.
- **Root cause:** `aspects/calculator.py` functions `get_aspect()` (body-swap line), `calculate_aspects_vectorized()` (empty-result path), `calculate_aspects_batch()` (empty per-date path), `find_aspect_timing()` (full function, 0 prior tests), `find_aspects_between_dates()` (body1/body2 filter branches); `calculations.py:382` `dist_velocity_au()` (0 prior tests).
- **Fix:** 9 new tests in `TestAspectsCalculatorMissingPaths`:
  - `test_get_aspect_body1_gt_body2_swap` — passes body1=1, body2=0 to trigger swap
  - `test_calculate_aspects_vectorized_no_aspects` — single-body slice (no pairs → empty path)
  - `test_calculate_aspects_batch_empty_date_path` — single-body slice (empty per-date)
  - `test_find_aspect_timing_known_new_moon` — JD=2451550.0 (Sun-Moon ~2.95°, in-orb) covers backward/forward loop bodies (lines 429, 442)
  - `test_find_aspect_timing_invalid_aspect_raises` — aspect_value=999.0 → ValueError
  - `test_find_aspects_between_dates_body1_filter` — body1=0, body2=None
  - `test_find_aspects_between_dates_body2_filter` — body1=None, body2=1
  - `test_find_aspects_between_dates_all_pairs` — body1=None, body2=None
  - `test_dist_velocity_au_returns_float` — direct call to `dist_velocity_au(JD, 0)`
- **Files modified:** `tests/test_coverage_improvements.py`
- **Verification:** All 9 tests pass; `pytest --cov-fail-under=100` reaches TOTAL 100%
- **Committed in:** `e7b7bbb` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3 — blocking)
**Impact on plan:** Essential for gate to pass. No scope creep — all tests cover existing uncovered paths in shipped code; no source changes.

## Issues Encountered

- `test_find_aspect_timing_known_new_moon` initially used J2000.0 (JD=2451545.0) as reference. At that date Sun-Moon separation was outside conjunction orb → the backward/forward loops exited immediately, never executing lines 429/442 (`jd_begin += step` / `jd_end += step`). Fixed by switching to JD=2451550.0 where Sun-Moon separation is ~2.95° (inside conjunction orb) — the loops now iterate several steps before exiting.

## Next Phase Readiness

- Phase 21 (Quality) fully complete: QAL-10 (coverage 100%), QAL-11 (div/0 guards), QAL-12 (52 doctests + doctest gate) all delivered
- Phase 22 (Ephemeris Refactor) can proceed on clean baseline: 1346 tests, 100% coverage, all gates green
- Zero technical debt from Phase 21

---
*Phase: 21-quality*
*Completed: 2026-05-29*
