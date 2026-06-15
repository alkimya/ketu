---
gsd_state_version: 1.0
milestone: v1.7
milestone_name: Fictitious-Point Orbs
status: executing
stopped_at: Phase 38 context gathered
last_updated: "2026-06-15T21:20:22.913Z"
last_activity: 2026-06-15 -- Phase 39 execution started
progress:
  total_phases: 2
  completed_phases: 1
  total_plans: 5
  completed_plans: 2
  percent: 40
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-15 — v1.7 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 39 — documentation-release-v1-7-0

## Current Position

Phase: 39 (documentation-release-v1-7-0) — EXECUTING
Plan: 1 of 3
Status: Executing Phase 39
Last activity: 2026-06-15 -- Phase 39 execution started

```text
Progress: [░░░░░░░░░░░░░░░░░░░░] 0% (0/2 phases, 0/0 plans)
```

## Next Step

Run `/gsd-plan-phase 38` to plan Phase 38: Fictitious-Point Orbs Engine (ORB-01, ORB-02, ORB-03).

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table. Relevant context for v1.7:

- Orb change is a single-source edit in `core.bodies` rows 10/11/12 (Rahu/Ketu/Lilith `orb` field). All consumers (`get_orb`, `synastry_orb_limit`, cycles, composite, CLI) inherit data-driven — no per-consumer edits.
- Rahu↔Ketu Opposition filter targets BOTH conditions simultaneously: `(body1, body2) == (Rahu, Ketu)` AND `aspect == Opposition`. Rahu and Ketu stay fully active for ALL other aspects and ALL other pairs.
- Synastry is IN SCOPE: orb=0 oracles in `tests/synastry/test_orbs.py` and `tests/synastry/test_modes_idempotent.py` must be rewritten; ~40 test files reference the points and need a regression sweep. New/changed detections are pinned deliberately, never silently accepted.
- This is MINOR 1.7.0 (not patch 1.6.1) because aspect results change for consumers — Kala must treat the upgrade as deliberate.
- User go/no-go relecture-validation REQUIRED before any irreversible action (tag, PyPI, GitHub release) — hard gate in Phase 39.
- Declination MIN_DECL_ORB floor (0.5°) already kept Rahu/Ketu/Lilith detectable in the δ axis even at orb=0; the new 2° longitude orb is separate and independent of the δ path.

### Blockers/Concerns

None. v1.7 builds on the green v1.6 base (1654 tests, 100% coverage, mypy `--strict` clean).

### Pending Todos

None.

## Deferred Items

Items acknowledged and deferred at milestone close on 2026-06-04 (v1.6):

| Category | Item | Status |
|----------|------|--------|
| verification_gap | Phase 17 (Composite Chart, v1.2) — 17-VERIFICATION.md | human_needed |

Note: Phase 17 belongs to the already-shipped v1.2 milestone. The open flag is the documented-deferred Astro.com manual cross-check (a bot-blocked UI task, ~30 min). It is NOT a blocker. Out of v1.7 scope.

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

*Updated after each plan completion*

## Session Continuity

Last session: 2026-06-15T18:00:00.823Z
Stopped at: Phase 38 context gathered
Resume file: .planning/phases/38-fictitious-point-orbs-engine/38-CONTEXT.md

## Operator Next Steps

- Run `/gsd-plan-phase 38` to plan the engine phase (ORB-01/02/03)
