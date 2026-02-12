# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-12)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Phase 2.1 complete — ready for Phase 3

## Current Position

Phase: 03 of 7 (Dependency Cleanup)
Plan: 1/? (plan 01 complete)
Status: Phase 03-01 complete — Pandas dependency removed, pure NumPy library
Last activity: 2026-02-12 — Phase 03-01 execution complete

Progress: [█████░░░░░] ~50% (Phase 1: 2 plans, Phase 2: 2 plans, Phase 2.1: 2 plans, Phase 03: 1/? plans complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: 4.3 minutes
- Total execution time: 0.50 hours

**By Phase:**

| Phase   | Plans | Total  | Avg/Plan |
|---------|-------|--------|----------|
| 01      | 2     | 8 min  | 4 min    |
| 02      | 2     | 7 min  | 3.5 min  |
| 02.1    | 2     | 9 min  | 4.5 min  |
| 03      | 1     | 6 min  | 6 min    |

**Recent Trend:**
- Last 5 plans: 02-02 (4 min), 02.1-01 (2 min), 02.1-02 (7 min), 03-01 (6 min)
- Trend: Stable execution speed, dependency cleanup efficient

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

*Updated after each plan completion*
| Phase 03 P01 | 370 | 2 tasks | 8 files |

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
- [Phase 03-01]: Remove to_pandas entirely (no deprecation) — Heading to 1.0.0, clean break justified; Ketu's contract is NumPy-only
- [Phase 03-01]: Keep duck-typing for pandas DatetimeIndex — Zero-cost interop, no pandas dependency required

### Roadmap Evolution

- Phase 2.1 inserted after Phase 2: Fix Moon velocity and rename vlong API (URGENT)

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-12 (phase 03 execution)
Stopped at: Phase 03-01 complete — Pandas dependency removed
Resume file: None

**Phase 1 Complete:** API Surface Cleanup finished (2 plans completed, UPGRADING.md created, human verified)
**Phase 2 Complete:** Correctness Fixes finished (2 bugs fixed, regression tests added, 192 tests pass)
**Phase 2.1 Complete:** Moon velocity and vlong API fixes finished (2 plans completed, 196 tests pass, breaking API changes documented)
**Phase 3 In Progress:** Dependency cleanup (1 plan completed — pandas removed, pure NumPy library)

---
*State initialized: 2026-02-12*
*Last updated: 2026-02-12*
