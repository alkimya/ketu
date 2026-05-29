---
phase: 22-ephemeris-refactor
plan: 02
subsystem: ephemeris
tags: [numpy, orbital-mechanics, refactor, module-decomposition, byte-stable]

# Dependency graph
requires:
  - phase: 21-quality
    provides: 100% coverage gate (fail_under=100) — must stay green after split

provides:
  - "_elements.py: ORBITAL_ELEMENTS + five _LILITH_* constants (single source of truth, no circular imports)"
  - "_kepler.py: normalize_angle + solve_kepler_equation (pure compute leaf)"
  - "_mechanics.py: orbital_elements_at_date + compute_position (imports _elements/_kepler)"
  - "_perturbations.py: apply_perturbations (Jupiter/Saturn/Uranus if-elif unchanged)"
  - "_body_getters.py: six scalar+vectorized body position getters (imports leaf modules)"
  - "orbital.py: 70-LOC re-export hub — all prior public names importable byte-identically"

affects:
  - 22-01 (planets.py strategy — imports from orbital.py re-export hub unchanged)
  - 24-chiron (clean seams for Chiron: add row to _elements.py + getter to _body_getters.py)
  - 25-documentation
  - 26-release-1-3-0

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hub/spoke module decomposition: orbital.py is the public re-export hub; _*.py are private implementation modules"
    - "Zero-circular-import discipline: dependency direction _elements ← {_mechanics, _perturbations, _body_getters} ← orbital.py; sub-modules NEVER import from orbital.py"
    - "noqa: F401 on hub re-exports to silence unused-import linters while preserving public surface"

key-files:
  created:
    - ketu/ephemeris/_elements.py
    - ketu/ephemeris/_kepler.py
    - ketu/ephemeris/_mechanics.py
    - ketu/ephemeris/_perturbations.py
    - ketu/ephemeris/_body_getters.py
  modified:
    - ketu/ephemeris/orbital.py

key-decisions:
  - "ORBITAL_ELEMENTS and all five _LILITH_* constants extracted to _elements.py (not kept in orbital.py) — eliminates any risk of circular imports when sub-modules need the data"
  - "apply_perturbations if-elif left unchanged in _perturbations.py — strategy-ification deferred to Phase 24 (Chiron perturbations will likely be Chebyshev-based anyway)"
  - "All function bodies moved verbatim — pure structural split, zero algorithm changes, byte-stable"
  - "orbital.py retained as 70-LOC re-export hub with __all__ matching prior public surface exactly"

patterns-established:
  - "Phase 24 Chiron insertion points: add row to _elements.py ORBITAL_ELEMENTS + getter to _body_getters.py — two files, clean seams"

# Metrics
duration: 8min
completed: 2026-05-29
---

# Phase 22 Plan 02: Orbital Split Summary

**859-LOC orbital.py decomposed into five focused private sub-modules (_elements, _kepler, _mechanics, _perturbations, _body_getters) with a 70-LOC re-export hub; 1346 tests green, 100% coverage maintained, byte-stable**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-29T17:37:53Z
- **Completed:** 2026-05-29T17:45:07Z
- **Tasks:** 3
- **Files modified:** 6 (5 created, 1 rewritten)

## Accomplishments

- Split 859-LOC orbital.py into five focused modules each under 500 LOC (orbital.py: 70, _body_getters.py: 415, _elements.py: 209, _kepler.py: 69, _mechanics.py: 99, _perturbations.py: 131)
- Zero circular imports: strict dependency direction _elements ← leaf modules ← orbital.py hub; sub-modules never import from orbital.py
- All historical `from ketu.ephemeris.orbital import X` names resolve byte-identically; `__init__.py` untouched
- 1346 tests pass, 100% coverage maintained including all five new `_*.py` modules at 100%
- test_vectorization.py canary (scalar vs vectorized < 1e-10) and test_lilith_cross_check.py (< 0.005°) both green — zero float drift

## Task Commits

1. **Task 1: Extract _elements, _kepler, _mechanics, _perturbations** - `8ab233b` (feat) — committed by sibling agent 22-03 which ran concurrently
2. **Task 2: Extract _body_getters.py and convert orbital.py to re-export hub** - `29f58a6` (feat)
3. **Task 3: Full-suite byte-stability + coverage verification** — no code changes needed; verified by `29f58a6` (docstring already updated in Task 2)

## Files Created/Modified

- `/home/loc/workspace/ketu/ketu/ephemeris/_elements.py` — ORBITAL_ELEMENTS structured array + five `_LILITH_*` constants (single source of truth, 209 LOC)
- `/home/loc/workspace/ketu/ketu/ephemeris/_kepler.py` — `normalize_angle` + `solve_kepler_equation` (69 LOC, no ketu imports)
- `/home/loc/workspace/ketu/ketu/ephemeris/_mechanics.py` — `orbital_elements_at_date` + `compute_position` (99 LOC, imports _elements/_kepler)
- `/home/loc/workspace/ketu/ketu/ephemeris/_perturbations.py` — `apply_perturbations` verbatim with Jupiter/Saturn/Uranus if-elif (131 LOC)
- `/home/loc/workspace/ketu/ketu/ephemeris/_body_getters.py` — six scalar + vectorized body position getters (415 LOC, imports from leaf modules only)
- `/home/loc/workspace/ketu/ketu/ephemeris/orbital.py` — rewritten as 70-LOC re-export hub with `__all__` matching prior public surface

## Decisions Made

- `_elements.py` as the sole data layer (not keeping data in orbital.py): eliminates all circular-import risk. `orbital.py` re-exports from `_elements.py`, so the public surface is unchanged.
- `apply_perturbations` moved verbatim, if-elif untouched: Phase 24 Chiron perturbations will likely use Chebyshev (Phase 23 spike decides), so strategy-ifying `_perturbations.py` now would be premature optimization.
- Docstring updated in orbital.py to identify it as a re-export hub — the only non-mechanical edit.

## Deviations from Plan

None — plan executed exactly as written.

**Note on parallel execution:** Task 1 files (`_elements.py`, `_kepler.py`, `_mechanics.py`, `_perturbations.py`) were written by this agent but committed by the sibling 22-03 agent in commit `8ab233b`, which ran concurrently. This is an artifact of wave-parallel execution sharing the working tree. The content is correct and verified.

## Issues Encountered

- Parallel execution: sibling agent 22-03 committed `_elements.py` / `_kepler.py` / `_mechanics.py` / `_perturbations.py` before this agent could commit them. The files were already committed with correct content when this agent attempted to commit them. Task 2 committed cleanly.

## Next Phase Readiness

- Phase 22 plan 02 (REF-02) complete
- Clean seams for Phase 24 Chiron: `_elements.py` ORBITAL_ELEMENTS gets a Chiron row, `_body_getters.py` gets a `get_chiron_position` getter — two files, no monolith to navigate
- `ketu/ephemeris/planets.py` and `ketu/ephemeris/__init__.py` untouched (confirmed by git diff)

---
*Phase: 22-ephemeris-refactor*
*Completed: 2026-05-29*
