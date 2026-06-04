---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: Declination Aspects
status: ready_to_plan
last_updated: "2026-06-04T12:00:00Z"
last_activity: 2026-06-04
progress:
  total_phases: 2
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-04 — v1.6 roadmap created)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 36 — Declination Aspects Core (DECLA-01..04)

## Current Position

Phase: 36 of 37 (Declination Aspects Core)
Plan: — (not yet planned)
Status: Ready to plan
Last activity: 2026-06-04 — Roadmap created; 2 phases (36-37), 5 requirements mapped (100% coverage)

Progress: ░░░░░░░░░░ 0%

## Next Step

`/gsd:plan-phase 36` — plan the declination aspects core implementation.

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table. Relevant for v1.6:

- `CHART_DTYPE` is UNCHANGED (companion function, not a dtype field) — no ratchet break.
- Frozen 14-row `core.aspects` table + V1/V13 sha256 fingerprints stay byte-identical — DECLA aspects live in a SEPARATE `DECLA_ASPECT_DTYPE`.
- Orb formula: `max((orb_b1+orb_b2)/2 * (1/12), 0.5)` — `DECLA_COEF=1/12` yields exactly 1.0° for Sun/Moon; `MIN_DECL_ORB=0.5°` floor keeps Rahu/Ketu/Lilith (orb=0) detectable.
- Detection is vectorizable batch (`(S,14)→(S,91)` upper-triangle) — no Python loop in the hot path.
- Research pitfalls are REQUIRED test cases: sign conflation (+15°/−15° is CP, not P), orb inflation (7° Sun/Moon gap not parallel), zero-sign trap (both at δ=0 → no aspect), MIN_DECL_ORB floor (Rahu/Lilith gap 0.1° → detected).
- User go/no-go relecture-validation REQUIRED before any irreversible publish (tag, PyPI, GitHub release) — hard gate in Phase 37.

### Blockers/Concerns

None. v1.6 builds additively on the green v1.5 base (1627 tests, 100% coverage, mypy `--strict` clean).

### Pending Todos

None.

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

*Updated after each plan completion*

## Session Continuity

Last session: 2026-06-04 — Roadmap v1.6 created (2 phases, DECLA-01..05 mapped, STATE + REQUIREMENTS traceability updated).
Stopped at: Roadmap creation complete — ready to plan Phase 36.
Resume file: None
