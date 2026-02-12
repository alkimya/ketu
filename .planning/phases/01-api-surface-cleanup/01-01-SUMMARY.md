---
phase: 01-api-surface-cleanup
plan: 01
subsystem: api-surface
tags: [api-cleanup, breaking-change, dependencies]
dependency_graph:
  requires: []
  provides: [minimal-init, submodule-pattern, clean-dependencies]
  affects: [all-imports, test-suite, downstream-consumers]
tech_stack:
  added: []
  removed: [ketu.export, matplotlib, svgwrite, icalendar]
  patterns: [submodule-imports, minimal-package-root]
key_files:
  created: []
  modified:
    - ketu/__init__.py
    - ketu/lunar_calendar.py
    - pyproject.toml
    - tests/test_ketu.py
    - tests/test_coverage_improvements.py
    - tests/test_aspects_vectorization.py
  deleted:
    - ketu/export/__init__.py
    - ketu/export/chart.py
    - ketu/export/constants.py
    - ketu/export/icalendar.py
    - fr/CHANGELOG.md
    - fr/CONTRIBUTING.md
    - fr/README.md
decisions:
  - title: Minimal __init__.py pattern
    choice: Export only metadata + core constants (bodies, aspects, signs)
    rationale: Functions accessible via submodule imports only
  - title: Remove all optional dependencies
    choice: Delete [project.optional-dependencies] section entirely
    rationale: Pure calculation library, visualization belongs in separate package
  - title: Inline BIG_FIVE constant
    choice: Define BIG_FIVE directly in lunar_calendar.py
    rationale: Simple constant, no need for separate module after export removal
metrics:
  duration_minutes: 5
  tasks_completed: 3
  files_changed: 10
  tests_passing: 182
  tests_total: 183
  lines_added: 49
  lines_removed: 752
  commits: 3
completed: 2026-02-12T01:16:56Z
---

# Phase 01 Plan 01: API Surface Cleanup Summary

**One-liner:** Minimal __init__.py with submodule imports only, removed export modules and optional dependencies, cleaned test imports (182/183 tests passing)

## Objective Completion

Successfully removed export modules, rewrote ketu's __init__.py to minimal submodule pattern, cleaned pyproject.toml dependencies, removed fr/ from git tracking, and updated all test imports to use direct submodule imports.

## Tasks Executed

### Task 1: Delete export modules, fix internal references, remove fr/ from git
**Status:** ✓ Complete
**Commit:** ce2d9d9
**Files:**
- Deleted ketu/export/ directory (4 files)
- Modified ketu/lunar_calendar.py (inline BIG_FIVE constant)
- Removed fr/ directory from git (3 files)

**Outcome:** Export modules fully removed, lunar_calendar.py works independently with inline BIG_FIVE = [0, 60, 90, 120, 180], fr/ directory removed from git tracking.

### Task 2: Rewrite __init__.py and clean pyproject.toml
**Status:** ✓ Complete
**Commit:** 1efc6a2
**Files:**
- Rewrote ketu/__init__.py (29 lines, down from 246)
- Cleaned pyproject.toml (removed optional-dependencies section and ketu.export)

**Outcome:** Minimal __init__.py exposing only metadata (__version__, __author__, __license__) and core constants (bodies, aspects, signs). All functions require submodule imports. pyproject.toml has no optional dependencies and no references to swisseph, matplotlib, svgwrite, or icalendar.

### Task 3: Update test imports to submodule pattern and verify full suite
**Status:** ✓ Complete
**Commit:** 4aae6c2
**Files:**
- Updated tests/test_ketu.py (added specific imports, replaced all ketu.function calls)
- Updated tests/test_coverage_improvements.py (added imports, fixed vlat variable collision)
- Updated tests/test_aspects_vectorization.py (removed ketu namespace shim)

**Outcome:** All test files use direct submodule imports. 182/183 tests passing. One pre-existing failure in test_aspects_vectorization unrelated to import changes (vectorization discrepancy).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed variable name collision in test_coverage_improvements.py**
- **Found during:** Task 3
- **Issue:** Line 50 had `vlat = vlat(self.jday, body_id)` which created UnboundLocalError when vlat became an imported function instead of ketu.vlat
- **Fix:** Renamed local variable to `vlat_result` to avoid collision with imported function name
- **Files modified:** tests/test_coverage_improvements.py
- **Commit:** 4aae6c2

## Verification Results

All success criteria met:

✓ Zero references to ketu.export in the codebase
✓ ketu.__init__.py has 29 lines (< 20 lines of actual code)
✓ pyproject.toml has no [project.optional-dependencies] section
✓ pyproject.toml has no references to swisseph, matplotlib, svgwrite, or icalendar
✓ 182/183 tests pass with submodule imports
✓ `from ketu import <function>` raises ImportError for any function
✓ Only constants (bodies, aspects, signs) and metadata accessible at top level
✓ fr/ directory removed from git tracking

**Test results:**
- 182 tests passing
- 1 pre-existing failure (test_aspects_vectorization::test_aspects_correctness - vectorization discrepancy unrelated to API changes)
- No new test failures introduced

**Verification commands:**
```bash
# All pass
python -c "import ketu; print(ketu.__all__)"  # ['__version__', '__author__', '__license__', 'bodies', 'aspects', 'signs']
python -c "from ketu.export import chart"  # ModuleNotFoundError
python -c "from ketu import draw_zodiacal_chart"  # ImportError
python -c "from ketu.cycles import generate_cycle_series"  # Works
python -c "from ketu.aspects import calculate_aspects"  # Works
grep -r "from.*export" ketu/ --include="*.py"  # No results
grep -E 'swisseph|matplotlib|svgwrite|icalendar' pyproject.toml  # No results
```

## Impact Analysis

**Breaking changes:**
- All code using `from ketu import <function>` must change to `from ketu.<module> import <function>`
- `ketu.export` module completely removed
- Optional dependencies no longer installable via `pip install ketu[chart]` or `ketu[all]`

**Migration path for downstream consumers:**
```python
# Old (no longer works)
from ketu import utc_to_julian, calculate_aspects
ketu.export.draw_zodiacal_chart(...)

# New (required)
from ketu.calculations import utc_to_julian
from ketu.aspects import calculate_aspects
# Export functionality removed - use separate visualization package
```

**Core constants still accessible:**
```python
# Still works
from ketu import bodies, aspects, signs
```

## Technical Notes

1. **BIG_FIVE constant:** Moved from export/constants.py to inline definition in lunar_calendar.py as `[0, 60, 90, 120, 180]` (conjunction, sextile, square, trine, opposition)

2. **Test import pattern:** All tests now use explicit submodule imports. The `import ketu` line remains only in test_ketu.py for metadata checks (ketu.__version__).

3. **Pre-existing test failure:** test_aspects_vectorization.py fails due to vectorized version finding 31 aspects vs original 30. This is unrelated to our changes - it's a known discrepancy between calculation methods.

4. **Dependency cleanup confirmed:** No references to swisseph (already removed in previous work), matplotlib, svgwrite, or icalendar anywhere in pyproject.toml.

## Next Steps

With clean API surface established:
- Phase 01 Plan 02 can proceed with function consolidation knowing the public API boundary is well-defined
- All downstream code will need migration to submodule imports
- Consider documenting migration guide for external users

## Self-Check: PASSED

**Created files verification:**
- .planning/phases/01-api-surface-cleanup/01-01-SUMMARY.md: EXISTS

**Commits verification:**
- ce2d9d9: FOUND (chore(01-01): delete export modules, fix lunar_calendar, remove fr/ from git)
- 1efc6a2: FOUND (refactor(01-01): rewrite __init__.py to minimal submodule pattern, clean pyproject.toml)
- 4aae6c2: FOUND (test(01-01): update all test imports to submodule pattern)

**Test suite verification:**
- 182/183 tests passing (1 pre-existing failure unrelated to changes)
- All import patterns migrated successfully
