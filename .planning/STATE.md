---
gsd_state_version: 1.0
milestone: v1.8.0
milestone_name: "**Goal**: The `body_decl_speed` field, the 0.01 d FD step, `DECL_STANDSTILL_EPS`, the chart-level helper, and the Ketu/Rahu boundary are fully documented in English and French, the version is bumped to 1.8.0, and `ketu==1.8.0` is live on PyPI"
status: Awaiting next milestone
stopped_at: Completed 41-03-PLAN.md — ketu==1.8.0 live on PyPI
last_updated: "2026-06-19T11:07:49.259Z"
last_activity: 2026-06-19 — Milestone v1.8 completed and archived
progress:
  total_phases: 2
  completed_phases: 2
  total_plans: 6
  completed_plans: 6
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-17 — milestone v1.8 started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 41 — documentation-release-v1-8-0

## Current Position

Phase: Milestone v1.8 complete
Plan: —
Status: Awaiting next milestone
Last activity: 2026-06-19 — Milestone v1.8 completed and archived

## Next Step

`/gsd-complete-milestone` — archive v1.8, update PROJECT.md, clean up .planning/

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table.

Key constraints for this milestone:

- Δt = 0.01 day reused verbatim from `declination_velocity` — not configurable, no new API surface
- Composite `body_decl_speed` derived from the composite chart, never midpoint of parents
- `DECL_STANDSTILL_EPS` defined IN Ketu as a public contract (Rahu invents no threshold)
- MINOR bump (1.8.0) — dtype layout grows; UPGRADING v1.7→v1.8 must give Kala explicit re-pin guidance
- Human go/no-go before irreversible PyPI publish

### Blockers/Concerns

None. v1.7 shipped on a green base (1668 tests, 100% coverage, mypy `--strict` clean).

### Pending Todos

None.

## Deferred Items

| Category | Item | Status |
|----------|------|--------|
| verification_gap | Phase 17 (Composite Chart, v1.2) — Astro.com manual cross-check | human_needed |

Note: Non-blocker. Out of v1.8 scope.

## Performance Metrics

**Velocity (shipped milestones):**

| Milestone | Phases | Plans | Active time |
|-----------|--------|-------|-------------|
| v1.0      | 7      | 16    | —           |
| v1.1      | 5      | 27    | ~3h         |
| v1.2      | 8      | 35    | ~20d elapsed|
| v1.3      | 8+1    | 30    | ~3d         |
| v1.4      | 5      | 15    | ~1d         |
| v1.5      | 3      | 9     | ~1d         |
| v1.6      | 2      | 5     | <1d         |
| v1.7      | 2      | 5     | ~3h         |

*Updated after each plan completion*

## Session Continuity

Last session: 2026-06-19T10:38:26.339Z
Stopped at: Completed 41-03-PLAN.md — ketu==1.8.0 live on PyPI
Resume file: None

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
