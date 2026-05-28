---
phase: 19-arabic-parts-framework
plan: "03"
subsystem: testing
tags: [arabic-parts, coverage-gate, oracle, pytest, makefile]

# Dependency graph
requires:
  - phase: 19-arabic-parts-framework plan 01
    provides: ketu.parts subpackage (PARTS registry, calculate_part, calculate_all_parts, register, get_part)
  - phase: 19-arabic-parts-framework plan 02
    provides: --list-parts CLI flag + cmd_list_parts() in ketu/cli/introspection.py
provides:
  - tests/parts/ suite (5 files, 31 tests): registry + CLI + oracle + coverage gate
  - 6 pinned hand-derived oracle values (Fortune day+night, Spirit day+night, Marriage day+night)
  - parts_coverage_gate pytest marker registered in pyproject.toml
  - make parts-coverage Makefile target (two-step pattern, 100% on ketu/parts/)
  - ketu.parts added to [tool.setuptools].packages in pyproject.toml
affects: [phase-19, phase-20]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Self-consistency oracle: derive expected from same formula as implementation, pin to 1e-9"
    - "Two-step coverage gate pattern: pytest --fail-under=0 then coverage report --include --fail-under=95"
    - "Coverage sentinel test with named pytest marker (no conftest.py)"

key-files:
  created:
    - tests/parts/__init__.py
    - tests/parts/test_parts_registry.py
    - tests/parts/test_parts_cli.py
    - tests/parts/test_parts_coverage_gate.py
    - tests/parts/test_parts_oracle.py
  modified:
    - pyproject.toml
    - Makefile

key-decisions:
  - "calculate_all_parts default (parts=None) branch + explicit filter tested separately in TestCalculateAllParts — pushed api.py from 88% to 100%"
  - "Fortune != Spirit mirror-guard tests on BOTH charts (day+night) catch copy-paste formula swap more thoroughly than day-only"
  - "Sect premise asserted at module-level (import-time) in test_parts_oracle.py so a fixture regression surfaces as collection error, not buried test failure"

patterns-established:
  - "Pattern: oracle sect asserted at module level (fail-fast on fixture regression)"
  - "Pattern: calculate_all_parts coverage via TestCalculateAllParts class (default + filter branches)"

# Metrics
duration: ~5min
completed: "2026-05-28"
---

# Phase 19 Plan 03: Arabic Parts Framework — Test Suite + Coverage Gate Summary

**31 tests across 5 files pin 6 hand-derived oracle values for Fortune/Spirit/Marriage (day+night) at 1e-9 tolerance, registry round-trip + extensibility, CLI --list-parts output, and push ketu/parts/ to 100% coverage via two-step make parts-coverage gate.**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-28T19:36:48Z
- **Completed:** 2026-05-28T19:41:57Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- 6 oracle values pinned: Fortune day + night, Spirit day + night, Marriage day + night; each asserted to `< 1e-9` against hand-derived expected; sect of both fixtures asserted at module level; Fortune != Spirit mirror-guard on both charts
- Registry round-trip tests: exactly-3 constraint, case-insensitive lookup, ValueError on unknown (message lists available parts), extensibility (register 4th lot + use without dispatch change + cleanup), Marriage callable identity (PARTS-07)
- CLI test: `--list-parts` exits 0, all 3 names in stdout, "fixed" note present; `cmd_list_parts()` direct call variant
- `parts_coverage_gate` marker registered in `pyproject.toml` (alphabetically between `houses` and `returns`); no `PytestUnknownMarkWarning` under `-W error`
- `make parts-coverage` target added (Makefile + `.PHONY`); two-step pattern mirroring `returns-coverage` (RET-06); exits 0 with ketu/parts/* at **100%** (gate: >=95%)
- `ketu.parts` added to `[tool.setuptools].packages` in `pyproject.toml`
- Full suite: **1284 PASS + 2 SKIP** (unchanged from baseline 1253 + 31 new tests)

## Task Commits

1. **Task 1: Registry + CLI + coverage-gate sentinel tests** - `05222be` (test)
2. **Task 2: Oracle tests — 6 hand-derived pinned values** - `0d68ff4` (test)
3. **Task 3: Register marker + Makefile target + run gate** - `612680b` (chore)

## Files Created/Modified

- `tests/parts/__init__.py` — empty package marker
- `tests/parts/test_parts_registry.py` — registry behaviour + extensibility (13 tests)
- `tests/parts/test_parts_cli.py` — `--list-parts` output assertions (9 tests)
- `tests/parts/test_parts_coverage_gate.py` — `parts_coverage_gate` marker sentinel (1 test)
- `tests/parts/test_parts_oracle.py` — 6 oracle values + sect premise + mirror guard (8 tests)
- `pyproject.toml` — `parts_coverage_gate` marker added; `ketu.parts` added to packages list
- `Makefile` — `parts-coverage` target + `.PHONY` entry

## Decisions Made

- `calculate_all_parts` default (parts=None) branch covered by `TestCalculateAllParts` class added to `test_parts_registry.py` — pushed `api.py` from 88% (2 missing lines) to 100%; gate was already passing at 95% but 100% is cleaner
- Fortune != Spirit mirror-guard placed in its own `TestFortuneAndSpiritAreMirrors` class and run on BOTH charts (day + night) — more thorough than day-only as specified in plan
- Sect premise asserted at module level (import time) in `test_parts_oracle.py` — a fixture sect regression surfaces as a collection error, not a buried test failure

## Deviations from Plan

**1. [Rule 2 - Missing Critical] Added TestCalculateAllParts class to test_parts_registry.py**

- **Found during:** Task 3 (running make parts-coverage)
- **Issue:** `ketu/parts/api.py` lines 146-147 (`calculate_all_parts` body — `parts is not None` branch + dict comprehension) were not exercised by Task 1/2 tests. Plan specified adding targeted tests if any line was missed.
- **Fix:** Added `TestCalculateAllParts` class with 4 tests (default all-3, explicit single, explicit two, all-values-in-range) to `test_parts_registry.py`; pushed api.py to 100%
- **Files modified:** `tests/parts/test_parts_registry.py`
- **Committed in:** `612680b` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing coverage for calculate_all_parts branch)
**Impact on plan:** Fully aligned with plan intent ("add a targeted test to reach >=95%"). Gate was already passing at 95%; 100% is the better outcome.

## Issues Encountered

None — all three verify commands passed on the first run.

## Next Phase Readiness

- Phase 19 (Arabic Parts Framework) is **complete**: all 5 ROADMAP success criteria verifiable end-to-end (criteria 1-4 from Plans 01/02, criterion 5 here)
- PARTS-01..08 all satisfied
- Ready for Phase 20 (Release Preparation v1.2.0)

---
*Phase: 19-arabic-parts-framework*
*Completed: 2026-05-28*
