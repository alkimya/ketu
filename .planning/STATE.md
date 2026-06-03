---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Lunar Declination & Harmonics Debt
status: roadmap-created
last_updated: "2026-06-03T19:00:00Z"
last_activity: 2026-06-03
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — v1.5 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** v1.5 roadmap created — 3 phases (33-35), 21/21 v1.5 requirements mapped. Ready to plan Phase 33 (Lunar Declination δ). Scope: declination δ (scalar + vectorized + montant/descendant + OOB + `body_decl` in `CHART_DTYPE`) + harmonics debt (ASP-F2 naming contract, ASP-F3 timing orb, ASP-F1 CLI `--harmonics h7`) + release v1.5.0. Additive minor, no breaking changes.

## Current Position

Phase: 33 — Lunar Declination δ (not started; roadmap created, ready to plan)
Plan: —
Status: Roadmap created. 3 phases mapped (33 Declination, 34 Harmonics Debt, 35 Release). Phases 33 and 34 are independent (either order); Phase 35 (release) is LAST and user-checkpoint-gated before tag/publish. All 21 v1.5 requirements mapped to exactly one phase, zero unmapped. Locked decisions baked into the roadmap: `is_ascending_declination` name; OOB via instantaneous ε(jd) (`true_obliquity`); Tight CLI grammar (`h7` alone, no `h7,h11`/`traditional,h7`); harmonics debt internal order F2 → F3 → F1; δ reuses `coordinates.py` chain (Meeus 13.4 equivalence pinned). `is_ascending` (β) and `core.aspects` frozen table + V1/V13 fingerprints stay UNCHANGED.
Last activity: 2026-06-03 — Roadmap created (`/gsd:new-project` roadmapper); ROADMAP.md (v1.5 phases appended), STATE.md, REQUIREMENTS.md traceability all written.

Progress: Not started (0/3 phases)

## Next Step

**`/gsd:plan-phase 33`** — decompose Phase 33 (Lunar Declination δ) into executable plans. This is the largest new-surface phase (9 requirements: scalar + vectorized δ, δ-velocity, montant/descendant, OOB, `body_decl` in `CHART_DTYPE` + ratchet, docs en + fr). Phase 34 (Harmonics Debt) is independent and can be planned in either order; Phase 35 (Release) is last and user-checkpoint-gated.

**Phase map (v1.5):**

- **Phase 33 — Lunar Declination δ** (DECL-01..09): `declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds`, `body_decl` in `CHART_DTYPE` + ratchet test, docs en + fr. Reuses `coordinates.py` chain (Meeus 13.4); δ-velocity mirrors `lat_velocity`; OOB via instantaneous ε(jd). Independent of Phase 34.
- **Phase 34 — Harmonics Debt (ASP-F1/F2/F3)** (HARM-01..09): `H{h}-{k}` naming contract (pinned), `find_aspect_timing` `dyn_coef=` orb derivation, CLI `--harmonics h7` (Tight grammar), byte-stability + docs en + fr. Internal order F2 → F3 → F1. Independent of Phase 33.
- **Phase 35 — Release v1.5.0** (REL-01..03): quality gates, version bump + CHANGELOG/UPGRADING, PyPI via OIDC (tag + main both pushed), post-publish smoke. LAST + user-checkpoint-gated.

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table. v1.5 decisions locked at roadmap creation (do not re-open):

- Declination montant/descendant helper name = `is_ascending_declination` (parallel to the unchanged β-based `is_ascending`).
- OOB threshold = instantaneous obliquity ε(jd) via `true_obliquity` (physically correct, free).
- CLI grammar = Tight (`h7` alone + existing index list; NO `h7,h11` / `traditional,h7` mixing — deferred to HARMF-01).
- Harmonics debt = ONE grouped phase, implementation order F2 → F3 → F1 (CLI surface depends on the naming contract being stable).
- Declination computation REUSES the existing `coordinates.py` chain (`ecliptic_to_equatorial` → `rectangular_to_spherical`, numerically equivalent to Meeus 13.4); δ-velocity mirrors the `lat_velocity` finite-difference idiom.
- `find_aspect_timing` gets `dyn_coef: Optional[float] = None` (Option (a) — clean under mypy `--strict`); explicit `orb` wins / precedence defined + tested.

### Blockers/Concerns

None. v1.5 is fully additive on a green v1.4 base (1539 tests, 100% coverage, mypy `--strict` clean). The only dtype change (`body_decl` in `CHART_DTYPE`) is guarded by a ratchet test and flagged to Kala.

### Pending Todos

None. See `.planning/research/DECLINATION.md` and `.planning/research/HARMONICS_DEBT.md` for the implementation briefs the planner should consume.

## Performance Metrics

**Velocity totals (shipped milestones):**

- v1.0: 16 plans / 7 phases (decimal Phase 2.1 inserted)
- v1.1: 27 plans / 5 phases (~3h active)
- v1.2: 35 plans / 8 phases (~20 days elapsed)
- v1.3: 30 plans / 8 phases (21-27 + 26.1) (2026-05-29 → 2026-06-01)
- v1.4: 15 plans / 5 phases (28-32) (2026-06-02 → 2026-06-03)
- v1.5: TBD / 3 phases (33-35) — roadmap created 2026-06-03

## Session Continuity

Last session: 2026-06-03 — Roadmap created for v1.5 (Lunar Declination & Harmonics Debt). 3 phases (33-35) appended to ROADMAP.md preserving the collapsed v1.0–v1.4 history; 21/21 v1.5 requirements mapped (9 DECL → Phase 33, 9 HARM → Phase 34, 3 REL → Phase 35); REQUIREMENTS.md traceability table filled; STATE.md updated to roadmap-created / ready-to-plan-Phase-33.
Stopped at: Roadmap created. Ready for `/gsd:plan-phase 33`.
Resume file: None — proceed with `/gsd:plan-phase 33` (or `34`; they are independent).
