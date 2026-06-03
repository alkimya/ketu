---
gsd_state_version: 1.0
milestone: v1.4
milestone_name: Dynamic Harmonics & Chiron Range
status: complete
last_updated: "2026-06-03T17:30:00Z"
last_activity: 2026-06-03
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 15
  completed_plans: 15
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — after v1.4 milestone)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Planning next milestone (v1.5). MILESTONE v1.4 (Dynamic Harmonics & Chiron Range) SHIPPED & ARCHIVED — `ketu==1.4.0` live on PyPI. Run `/gsd:new-milestone` to scope v1.5. v1.0–v1.4 archived to `.planning/milestones/`.

## Current Position

Phase: — (between milestones)
Status: MILESTONE v1.4 COMPLETE & ARCHIVED — `ketu==1.4.0` live on PyPI (OIDC, `publish.yml` SUCCESS); GitHub release v1.4.0 (sdist+wheel); tag `v1.4.0` (`3f3f9b4`, annotated `ca9e24c`) + `origin/main` pushed; post-publish fresh-venv smoke 4/4 PASS. All 5 phases (28-32), 15/15 plans. Roadmap + requirements archived; PROJECT.md evolved; MILESTONES.md entry written.
Last activity: 2026-06-03 — `/gsd:complete-milestone v1.4` (archive + collapse roadmap + evolve PROJECT.md)

Progress: [██████████████] 100% — v1.4 SHIPPED & ARCHIVED

## Next Step

**Start the next milestone** — `/gsd:new-milestone` (questioning → research → requirements → roadmap). Phase numbering continues at **33** (v1.4 ended at Phase 32). A fresh `.planning/REQUIREMENTS.md` is created by that flow.

Candidate seeds carried forward (not yet scoped):

- CLI surface for arbitrary harmonics `--harmonics h7` (ASP-F1) — return-type + CLI byte-stability work
- Formalize the synthetic off-table aspect naming scheme `H7k1` as a documented API contract (ASP-F2)
- `find_aspect_timing` orb-derivation design debt (ASP-F3)
- Lunar declination (montant/descendant biodynamique, true δ) — deferred; `is_ascending` (latitude β) suffices at daily resolution
- See `.planning/BACKLOG.md` for the full backlog.

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table; per-milestone detail in `.planning/milestones/v1.4-ROADMAP.md`. No open decisions carried into v1.5.

### Blockers/Concerns

None — all v1.4 blockers resolved at milestone close (Phase 30 perihelion accuracy spike PASSED, `.npz` regenerated, build environment confirmed).

### Pending Todos

None at milestone close. See `.planning/BACKLOG.md`.

## Performance Metrics

**Velocity totals (shipped milestones):**

- v1.0: 16 plans / 7 phases (decimal Phase 2.1 inserted)
- v1.1: 27 plans / 5 phases (~3h active)
- v1.2: 35 plans / 8 phases (~20 days elapsed)
- v1.3: 30 plans / 8 phases (21-27 + 26.1) (2026-05-29 → 2026-06-01)
- v1.4: 15 plans / 5 phases (28-32) (2026-06-02 → 2026-06-03)

## Session Continuity

Last session: 2026-06-03 — `/gsd:complete-milestone v1.4`. Archived roadmap + requirements to `.planning/milestones/v1.4-*`; collapsed v1.4 in ROADMAP.md; evolved PROJECT.md (Current State → v1.4, requirements → Validated, Key Decisions + Context updated); wrote MILESTONES.md entries for v1.4 + v1.3; deleted `.planning/REQUIREMENTS.md` (fresh for v1.5). Tag `v1.4.0` already on PyPI (no duplicate `v1.4` tag created — semantic tag reused).
Stopped at: Milestone v1.4 archived. Ready for `/gsd:new-milestone`.
Resume file: None — milestone complete.
