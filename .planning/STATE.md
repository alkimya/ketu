---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Lunar Declination & Harmonics Debt
status: defining-requirements
last_updated: "2026-06-03T18:00:00Z"
last_activity: 2026-06-03
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — v1.5 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Defining v1.5 requirements (Lunar Declination & Harmonics Debt). Scope locked via `/gsd:new-milestone` questioning: declination δ (scalar + biodynamic montant/descendant + `body_decl` in CHART_DTYPE) + harmonics debt (ASP-F1/F2/F3) + release v1.5.0. Research pass in flight, then requirements → roadmap (phases continue at 33). v1.0–v1.4 archived to `.planning/milestones/`.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements — v1.5 scope locked (δ lunar declination additive + montant/descendant biodynamic + `body_decl` in CHART_DTYPE; ASP-F1 CLI `--harmonics h7`; ASP-F2 `H{h}-{k}` naming contract; ASP-F3 `find_aspect_timing` orb derivation; release 1.5.0). Declination aspects (parallels/contra-parallels) out of scope (named future candidate). `is_ascending` (β) stays unchanged. Targeted domain research selected (biodynamic declination conventions). User reviews the whole milestone before tag/publish — checkpoint before Release phase.
Last activity: 2026-06-03 — Milestone v1.5 started (`/gsd:new-milestone`); PROJECT.md + STATE.md updated

Progress: Not started

## Next Step

**Research → requirements → roadmap.** Targeted research on biodynamic lunar declination conventions (montant/descendant, sign of δ vs velocity, OOB, sidereal mounting/descending vs declination) is in flight, then `REQUIREMENTS.md` with REQ-IDs, then roadmap. Phase numbering continues at **33** (v1.4 ended at Phase 32).

**Scope reference (decided in questioning):**

- Declination δ: `declination(jdate, body)` scalar + vectorizable; biodynamic montant/descendant via velocity of δ; `body_decl` added to CHART_DTYPE; `is_ascending` (β) UNCHANGED — additive, non-breaking
- ASP-F1: CLI `--harmonics h7` (h-prefixed, disambiguated from rejected bare-int) wired to `dynamic_specs=` + byte-stability
- ASP-F2: `H{h}-{k}` synthetic naming formalized as a documented + pinned public API contract
- ASP-F3: `find_aspect_timing` derives orb from a dynamic spec instead of receiving it raw
- Declination aspects (parallels/contra-parallels) — OUT of scope (future candidate)
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
