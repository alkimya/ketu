---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Lunar Declination & Harmonics Debt
status: in-progress
last_updated: "2026-06-03T19:41:13Z"
last_activity: 2026-06-03
progress:
  total_phases: 3
  completed_phases: 0
  total_plans: 0
  completed_plans: 1
  percent: 5
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — v1.5 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** v1.5 roadmap created — 3 phases (33-35), 21/21 v1.5 requirements mapped. Ready to plan Phase 33 (Lunar Declination δ). Scope: declination δ (scalar + vectorized + montant/descendant + OOB + `body_decl` in `CHART_DTYPE`) + harmonics debt (ASP-F2 naming contract, ASP-F3 timing orb, ASP-F1 CLI `--harmonics h7`) + release v1.5.0. Additive minor, no breaking changes.

## Current Position

Phase: 33 — Lunar Declination δ (in progress — Plan 01 complete)
Plan: 02 (next)
Status: Plan 01 complete. Four declination functions added to ketu.calculations: `declination` (scalar + vectorized), `declination_velocity` (FD step=0.01), `is_ascending_declination` (dδ/dt > 0), `is_out_of_bounds` (|δ| > true_obliquity). DECL-03 equivalence regression pins machine-precision agreement with Meeus 13.4. 1575 tests, 100% coverage, all gates green.
Last activity: 2026-06-03 — Plan 01 executed (33-01-SUMMARY.md, commits 6183bad/ad11073/60da1f9).

Progress: In progress (Plan 01/N done in Phase 33)

## Next Step

**`/gsd:execute-phase 33 --plan 02`** — execute Plan 02 of Phase 33 (body_decl in CHART_DTYPE + ratchet test). Plan 01 foundation functions are ready as dependencies.

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
- Scalar/array dispatch in `declination()`: `long`/`lat` reject array jdate (lru_cache, unhashable); scalar path uses `long`/`lat`, array path uses `calc_planet_position_batch` (loop-free).
- β-vs-δ independence confirmed: 2025-03-07 (JD=2460742.0) is the anchor date where `is_ascending_declination=True` (vel=+0.30°/day) and `is_ascending=False` (β descending).

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
- v1.5: TBD / 3 phases (33-35) — roadmap created 2026-06-03; Plan 33-01 done (6 min, 3 tasks, 3 files)

## Session Continuity

Last session: 2026-06-03 — Plan 01 of Phase 33 executed. Four declination functions added to ketu.calculations. 1575 tests, 100% coverage, all gates green. Commits: 6183bad (feat), ad11073 (test), 60da1f9 (test).
Stopped at: Phase 33 Plan 01 complete.
Resume file: None — proceed with `/gsd:execute-phase 33 --plan 02`.
