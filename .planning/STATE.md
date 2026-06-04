---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: Declination Aspects
status: ready_to_plan
last_updated: "2026-06-04T14:09:17Z"
last_activity: 2026-06-04
progress:
  total_phases: 2
  completed_phases: 0
  total_plans: 2
  completed_plans: 1
  percent: 50
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-04 — v1.6 roadmap created)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 36 — Declination Aspects Core (DECLA-01..04)

## Current Position

Phase: 36 of 37 (Declination Aspects Core)
Plan: 2 of 2 (36-02 batch function)
Status: In progress — Plan 36-01 complete
Last activity: 2026-06-04 — Plan 36-01 executed: ketu/declination sub-package (DECLA_ASPECT_DTYPE + find_declination_aspects), 19 tests, 100% coverage

Progress: █████░░░░░ 50%

## Next Step

Execute Plan 36-02 — batch declination_aspect_masks function.

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table. Relevant for v1.6:

- `CHART_DTYPE` is UNCHANGED (companion function, not a dtype field) — no ratchet break.
- Frozen 14-row `core.aspects` table + V1/V13 sha256 fingerprints stay byte-identical — DECLA aspects live in a SEPARATE `DECLA_ASPECT_DTYPE`.
- Orb formula: `max((orb_b1+orb_b2)/2 * (1/12), 0.5)` — `DECLA_COEF=1/12` yields exactly 1.0° for Sun/Moon; `MIN_DECL_ORB=0.5°` floor keeps Rahu/Ketu/Lilith (orb=0) detectable.
- Detection is vectorizable batch (`(S,14)→(S,91)` upper-triangle) — no Python loop in the hot path.
- Research pitfalls are REQUIRED test cases: sign conflation (+15°/−15° is CP, not P), orb inflation (7° Sun/Moon gap not parallel), zero-sign trap (both at δ=0 → no aspect), MIN_DECL_ORB floor (Rahu/Lilith gap 0.1° → detected).
- User go/no-go relecture-validation REQUIRED before any irreversible publish (tag, PyPI, GitHub release) — hard gate in Phase 37.
- Plan 36-01: find_declination_aspects returns ONE unified DECLA_ASPECT_DTYPE array (P+CP by kind field), sorted by (body1,body2), empty = np.empty(0) never None/tuple — no orbs.py (formula merged into core.py).
- Plan 36-01: `_ORB_MAT` frozen 14x14 at module load; `ketu.__all__` and `CHART_DTYPE` byte-identical — additive sub-package only.

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

Last session: 2026-06-04 — Plan 36-01 executed: ketu/declination sub-package created, 19 tests green, all quality gates pass.
Stopped at: Completed 36-01-PLAN.md — Plan 36-02 (batch function) is next.
Resume file: None
