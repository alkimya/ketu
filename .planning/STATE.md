# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-12)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Phase 4 complete — ready for Phase 5

## Current Position

Phase: 7 of 7 (Release Preparation) — IN PROGRESS
Plan: 1/3 (Plan 01 complete)
Status: Version 1.0.0 metadata finalized, trusted publishing workflow configured
Last activity: 2026-02-12 — Phase 7-01 execution (complete)

Progress: [██████████] ~90% (Phases 1, 2, 2.1, 3, 4, 5, 6 complete; Phase 7: 1/3 — 14 plans total)

## Performance Metrics

**Velocity:**
- Total plans completed: 14
- Average duration: 4.4 minutes
- Total execution time: 1.04 hours

**By Phase:**

| Phase   | Plans | Total  | Avg/Plan |
|---------|-------|--------|----------|
| 01      | 2     | 8 min  | 4 min    |
| 02      | 2     | 7 min  | 3.5 min  |
| 02.1    | 2     | 9 min  | 4.5 min  |
| 03      | 1     | 6 min  | 6 min    |
| 04      | 2     | 7 min  | 3.5 min  |
| 05      | 2     | 13 min | 6.5 min  |
| 06      | 3     | 57 min | 19 min   |
| 07      | 1     | 4 min  | 4 min    |

**Recent Trend:**
- Last 5 plans: 04-02 (4 min), 05-01 (6 min), 05-02 (7 min), 06-03 (12 min), 07-01 (4 min)
- Trend: Fast execution for metadata updates, stable velocity for documentation work

**Execution Log:**

| Plan          | Duration (sec) | Tasks | Files | Date       |
|---------------|----------------|-------|-------|------------|
| Phase 01 P01  | 306            | 3     | 10    | 2026-02-12 |
| Phase 01 P02  | 180            | 2     | 1     | 2026-02-12 |
| Phase 02 P01  | 180            | 2     | 4     | 2026-02-12 |
| Phase 02 P02  | 253            | 2     | 1     | 2026-02-12 |
| Phase 02.1 P01| 104            | 2     | 2     | 2026-02-12 |
| Phase 02.1 P02| 424            | 2     | 13    | 2026-02-12 |
| Phase 03 P01  | 370            | 2     | 8     | 2026-02-12 |
| Phase 04 P01  | 170            | 2     | 2     | 2026-02-12 |

| Phase 04 P02  | 238            | 2     | 2     | 2026-02-12 |
| Phase 05 P01  | 378            | 2     | 5     | 2026-02-12 |
| Phase 05 P02  | 439            | 2     | 11    | 2026-02-12 |
| Phase 06 P02  | 2700           | 2     | 10    | 2026-02-12 |
| Phase 06 P03  | 720            | 2     | 8     | 2026-02-12 |
| Phase 07 P01  | 232            | 3     | 5     | 2026-02-12 |

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Remove all export modules — Pure calculation library, exports belong in future GUI layer
- Complex math internal, degrees external — Complex numbers better for computation, degrees better for humans
- Fix all CONCERNS.md bugs — Clean slate for 1.0, no known bugs at release
- Remove Pandas dependency — Keep NumPy-only contract, use structured arrays instead
- Breaking API changes OK — Major version bump justifies cleanup

**From Plan 01-01:**
- Minimal __init__.py pattern — Export only metadata + core constants (bodies, aspects, signs), functions via submodule imports only
- Remove all optional dependencies — Delete [project.optional-dependencies] entirely, pure calculation library
- Inline BIG_FIVE constant — Define directly in lunar_calendar.py after export removal

**From Plan 01-02:**
- No Kala-specific references in UPGRADING.md — Generic migration guide for external PyPI users
- Pandas migration guide structure — Use pandas 3.0 migration guide as template for breaking releases
- Professional tone for PyPI release — Concise but professional documentation for external developers

**From Plan 02-01:**
- Fixed cache operator precedence bug — Parentheses required around hasattr() OR expression
- Test file already created for BUG-02 — Plan 02-02 test file was included in plan 02-01 commit

**From Plan 02-02:**
- Use enumerate pattern to fix orb_values indexing — Matches batch version pattern at line 219
- Add matched_pairs set to prevent duplicate aspects — Match loop behavior: first aspect found for each pair wins
- Root cause was pair duplication, not just indexing — Vectorized version found multiple aspects per pair

**From Plan 02.1-01:**
- Use ±180 wrapping for longitude differences — Standard practice for angular differences to handle 360/0 boundary crossings
- Apply wrapping only to Moon (not Sun) — Sun moves ~1 deg/day, can never wrap in 0.01 day delta; Moon moves ~14 deg/day
- Separate scalar and vectorized fixes — Scalar uses if-elif, vectorized uses np.where for performance

**From Plan 02.1-02:**
- Remove old names entirely (no deprecation) — Heading to 1.0.0, clean break justified; old "v" prefix was ambiguous
- Use full _velocity suffix instead of _vel — Maximally explicit naming prevents confusion; "long_velocity" is unambiguous

**From Plan 03-01:**
- Remove to_pandas entirely (no deprecation) — Heading to 1.0.0, clean break justified; Ketu's contract is NumPy-only
- Keep duck-typing for pandas DatetimeIndex — Zero-cost interop, no pandas dependency required

**From Plan 04-01:**
- Use pytest tmp_path fixture for all cache file I/O isolation — Prevents pollution of ~/.ketu cache, ensures test isolation
- Set fail_under=70 as minimum coverage threshold — Allows gradual improvement without blocking CI
- Exclude removed/irrelevant modules from coverage calculation — Deleted code shouldn't count against metrics
- Allow distance=0 for Rahu/Lilith — Calculated points (lunar nodes), not physical bodies, so distance=0 is correct
**From Plan 04-02:**
- Use pytest tmp_path fixture for cache tests — Standard pytest pattern for temporary file testing
- Test pandas DatetimeIndex with skip if unavailable — Optional pandas compatibility without hard dependency

**From Plan 05-01:**
- Vectorized _get_trace() eliminates Python loop using calc_planet_position_batch (CPX-02) — 10-100x faster for resonance field calculations
- Two-layer caching is coherent by design: LRU for single-point, EphemerisCache for batch (CPX-03) — Complementary non-overlapping use cases documented in cache/__init__.py
- Coordinate functions support arrays via existing NumPy ufuncs — Type hints updated, no implementation changes needed
- [Phase 05-02]: Case-insensitive error message tests to handle auto-formatter capitalization
- [Phase 05-02]: Document received value and valid options in all ValueError messages

**From Plan 06-02 (Partial):**
- Prioritize user-facing API modules for numpydoc conversion first (calculations, complex, core, cycles)
- Add precision guarantees to __init__.py (±1e-6° angular, ±0.1° inner planets, ±0.5° outer)
- Document best accuracy range 1800-2200 CE
- Scope underestimation: 96 public functions = ~80 minutes work, not ~30 minutes

**From Plan 06-03:**

- Use pyproject.toml overrides instead of inline # type: ignore — Centralized configuration cleaner than 20+ inline comments
- Disable misc errors for structured array modules only — NumPy structured arrays generate expected misc errors, override selective
- Target Python 3.11 for mypy configuration — Middle ground ensures compatibility across 3.10-3.13 range

**From Plan 07-01:**

- Removed MIT License classifier to avoid PEP 639 conflict — Modern setuptools rejects both license field AND classifier, kept field only
- Use trusted publishing (OIDC) instead of API tokens — More secure, no secrets in GitHub Actions, requires one-time PyPI setup
- Added automated version sync test — Prevents pyproject.toml vs __init__.py desynchronization before release

### Roadmap Evolution

- Phase 2.1 inserted after Phase 2: Fix Moon velocity and rename vlong API (URGENT)

### Pending Todos

None yet.

### Blockers/Concerns

None. Phase 7 plan 01 complete, ready for release validation.

## Session Continuity

Last session: 2026-02-12 (phase 7-01 execution)
Stopped at: Completed 07-01-PLAN.md — Version 1.0.0 metadata finalized, trusted publishing configured
Resume file: None

**Phase 1 Complete:** API Surface Cleanup finished (2 plans completed, UPGRADING.md created, human verified)
**Phase 2 Complete:** Correctness Fixes finished (2 bugs fixed, regression tests added, 192 tests pass)
**Phase 2.1 Complete:** Moon velocity and vlong API fixes finished (2 plans completed, 196 tests pass, breaking API changes documented)
**Phase 3 Complete:** Dependency cleanup finished (pandas removed, pure NumPy library, 196 tests pass)
**Phase 4 Complete:** Test coverage hardened (91.48% overall, cache 89%, cycles 96%, 241 tests pass, CI re-enabled)
**Phase 5 Complete:** Complex math integration (vectorized resonance, dual-cache docs, error standardization, CPX-01 verified, 250 tests pass)
**Phase 6 Complete:** Documentation & Type Checking (numpydoc 48 functions, mypy strict mode, PEP 561 marker, CI enforced, 250 tests pass)
**Phase 7 In Progress:** Release Preparation (1/3 plans complete — version 1.0.0 metadata finalized, trusted publishing configured, 410 tests pass)

---
*State initialized: 2026-02-12*
*Last updated: 2026-02-12*
