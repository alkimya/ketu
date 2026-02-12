# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-12)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Phase 4 complete — ready for Phase 5

## Current Position

Phase: 4 of 7 (Test Coverage Hardening) — COMPLETE
Plan: 2/2 (all plans complete)
Status: Phase 4 complete — 91.48% coverage, all critical modules >85%, CI re-enabled
Last activity: 2026-02-12 — Phase 4 execution complete

Progress: [██████░░░░] ~57% (Phases 1, 2, 2.1, 3, 4 complete — 9 plans total)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: 3.8 minutes
- Total execution time: 0.57 hours

**By Phase:**

| Phase   | Plans | Total  | Avg/Plan |
|---------|-------|--------|----------|
| 01      | 2     | 8 min  | 4 min    |
| 02      | 2     | 7 min  | 3.5 min  |
| 02.1    | 2     | 9 min  | 4.5 min  |
| 03      | 1     | 6 min  | 6 min    |
| 04      | 2     | 7 min  | 3.5 min  |

**Recent Trend:**
- Last 5 plans: 02.1-02 (7 min), 03-01 (6 min), 04-01 (3 min), 04-02 (4 min)
- Trend: Fast execution for test-focused plans, stable velocity

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

### Roadmap Evolution

- Phase 2.1 inserted after Phase 2: Fix Moon velocity and rename vlong API (URGENT)

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-12 (phase 4 execution)
Stopped at: Phase 4 complete, ready for Phase 5
Resume file: None

**Phase 1 Complete:** API Surface Cleanup finished (2 plans completed, UPGRADING.md created, human verified)
**Phase 2 Complete:** Correctness Fixes finished (2 bugs fixed, regression tests added, 192 tests pass)
**Phase 2.1 Complete:** Moon velocity and vlong API fixes finished (2 plans completed, 196 tests pass, breaking API changes documented)
**Phase 3 Complete:** Dependency cleanup finished (pandas removed, pure NumPy library, 196 tests pass)
**Phase 4 Complete:** Test coverage hardened (91.48% overall, cache 89%, cycles 96%, 241 tests pass, CI re-enabled)

---
*State initialized: 2026-02-12*
*Last updated: 2026-02-12*
