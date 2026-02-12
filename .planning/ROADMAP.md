# Roadmap: Ketu 1.0

## Overview

Ketu 1.0 consolidates a working astronomical calculation library from v0.4.0 to production stability. This is not feature development but surgical refinement: fix known bugs, remove anti-features (chart/icalendar exports), eliminate hidden dependencies, harden tests, integrate complex math, and document the stable API. Seven phases move from API cleanup through release, ensuring every v1 requirement ships with correctness guarantees and 70% test coverage.

## Phases

- [x] **Phase 1: API Surface Cleanup** - Define public API, remove export modules
- [x] **Phase 2: Correctness Fixes** - Fix cache and aspect bugs before 1.0
- [x] **Phase 2.1: Fix Moon velocity and rename vlong API** (INSERTED)
- [ ] **Phase 3: Dependency Cleanup** - Remove hidden Pandas dependency
- [ ] **Phase 4: Test Coverage Hardening** - Achieve 70% coverage with module targets
- [ ] **Phase 5: Complex Math Integration** - Unify complex representation into cycle engine
- [ ] **Phase 6: Documentation & Type Checking** - Finalize docs and type hints
- [ ] **Phase 7: Release Preparation** - PyPI publish and GitHub release

## Phase Details

### Phase 1: API Surface Cleanup
**Goal**: Ketu has a clean, explicit public API with removed anti-features
**Depends on**: Nothing (first phase)
**Requirements**: REM-01, REM-02, REM-04
**Success Criteria** (what must be TRUE):
  1. User imports from `ketu` fail for chart and icalendar modules with clear error messages
  2. `ketu.__all__` explicitly lists every public function and type
  3. User installs fresh wheel in clean venv without matplotlib/icalendar dependencies
  4. UPGRADING.md provides migration examples for removed export modules
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Delete export modules, rewrite __init__.py, clean pyproject.toml, update test imports
- [x] 01-02-PLAN.md — Write UPGRADING.md migration guide, verify cleanup

### Phase 2: Correctness Fixes
**Goal**: All known CONCERNS.md bugs are resolved with regression tests
**Depends on**: Phase 1
**Requirements**: BUG-01, BUG-02
**Success Criteria** (what must be TRUE):
  1. User sets `use_cache=False` and cache is verifiably disabled (operator precedence fixed)
  2. User runs `calculate_aspects_vectorized()` across 100 dates and gets consistent aspect count every time
  3. Each bug fix has a regression test that fails on v0.4.0 and passes on v1.0
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Fix cache operator precedence (BUG-01) with regression test
- [x] 02-02-PLAN.md — Fix aspect vectorization non-determinism (BUG-02) with regression test

### Phase 02.1: Fix Moon velocity and rename vlong API (INSERTED)

**Goal:** Moon velocity is correct at 360/0 boundary and velocity functions have explicit, unambiguous names
**Depends on:** Phase 2
**Plans:** 2 plans

Plans:
- [x] 02.1-01-PLAN.md — Fix Moon velocity wrapping bug (TDD: regression test + fix)
- [x] 02.1-02-PLAN.md — Rename vlong/vlat/vdist_au to explicit velocity names

### Phase 3: Dependency Cleanup
**Goal**: Ketu is pure NumPy (no hidden Pandas dependency)
**Depends on**: Phase 2
**Requirements**: REM-03
**Success Criteria** (what must be TRUE):
  1. User calls `generate_aspect_timeline()` and receives NumPy structured array (not DataFrame)
  2. User installs ketu in fresh venv and Pandas is not installed as transitive dependency
  3. All aspect timeline tests pass with NumPy structured arrays instead of DataFrames
**Plans:** 1 plan

Plans:
- [ ] 03-01-PLAN.md — Remove to_pandas() from AspectTimeline, refactor resonance.py to NumPy, update docs and UPGRADING.md

### Phase 4: Test Coverage Hardening
**Goal**: 70% overall coverage with critical modules above 85%
**Depends on**: Phase 3
**Requirements**: TST-01, TST-02, TST-03, TST-04, QAL-02
**Success Criteria** (what must be TRUE):
  1. Coverage report shows overall 70% with cycles >85%, cache >85%, aspects >85%
  2. Tests run successfully on Python 3.10, 3.11, 3.12, 3.13 in CI
  3. All angle comparisons use `numpy.testing.assert_allclose` with documented tolerance (1e-6)
  4. Pytest recognizes `slow` marker without warnings
  5. Edge case tests exist for 0deg/360deg angle boundaries
**Plans**: TBD

Plans:
- [ ] 04-01: TBD

### Phase 5: Complex Math Integration
**Goal**: Cycle engine uses complex numbers internally, degrees externally
**Depends on**: Phase 4
**Requirements**: CPX-01, CPX-02, CPX-03, QAL-01
**Success Criteria** (what must be TRUE):
  1. User calls cycle functions and receives degree outputs while engine uses complex math internally
  2. `ResonanceField._get_trace()` uses vectorized batch calculations (no Python loops)
  3. Single coherent caching strategy exists (not LRU + EphemerisCache in parallel)
  4. Error messages across all modules follow consistent format with context
**Plans**: TBD

Plans:
- [ ] 05-01: TBD

### Phase 6: Documentation & Type Checking
**Goal**: 1.0 API is fully documented with enforced type hints
**Depends on**: Phase 5
**Requirements**: DOC-01, DOC-02
**Success Criteria** (what must be TRUE):
  1. User reads documentation and finds no references to chart, icalendar, matplotlib, or removed functions
  2. CHANGELOG.md has detailed BREAKING CHANGES section explaining 0.4.0 to 1.0.0 migration
  3. All public functions have NumPy-style docstrings with working examples
  4. Mypy runs in strict mode without errors in CI
  5. Numerical precision guarantees are documented (1e-6 degrees for typical use)
**Plans**: TBD

Plans:
- [ ] 06-01: TBD

### Phase 7: Release Preparation
**Goal**: Ketu 1.0.0 is published to PyPI with GitHub release
**Depends on**: Phase 6
**Requirements**: DOC-03, DOC-04, DOC-05, DOC-06
**Success Criteria** (what must be TRUE):
  1. Version is 1.0.0 in pyproject.toml, `ketu/__init__.py`, and all docs
  2. PyPI classifiers show "Development Status :: 5 - Production/Stable"
  3. GitHub release v1.0.0 exists with changelog and download links
  4. User installs `pip install ketu==1.0.0` from PyPI and all tests pass
  5. Wheel and sdist both install cleanly in fresh venv without removed modules
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. API Surface Cleanup | 2/2 | ✓ Complete | 2026-02-12 |
| 2. Correctness Fixes | 2/2 | ✓ Complete | 2026-02-12 |
| 2.1 Fix Moon velocity & vlong | 2/2 | ✓ Complete | 2026-02-12 |
| 3. Dependency Cleanup | 0/1 | Not started | - |
| 4. Test Coverage Hardening | 0/TBD | Not started | - |
| 5. Complex Math Integration | 0/TBD | Not started | - |
| 6. Documentation & Type Checking | 0/TBD | Not started | - |
| 7. Release Preparation | 0/TBD | Not started | - |

---
*Roadmap created: 2026-02-12*
*Last updated: 2026-02-12 — Phase 3 planned*
