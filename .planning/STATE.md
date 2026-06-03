---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Lunar Declination & Harmonics Debt
status: in-progress
last_updated: "2026-06-03T20:09:47Z"
last_activity: 2026-06-03
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 0
  completed_plans: 4
  percent: 33
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — v1.5 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** v1.5 roadmap created — 3 phases (33-35), 21/21 v1.5 requirements mapped. Ready to plan Phase 33 (Lunar Declination δ). Scope: declination δ (scalar + vectorized + montant/descendant + OOB + `body_decl` in `CHART_DTYPE`) + harmonics debt (ASP-F2 naming contract, ASP-F3 timing orb, ASP-F1 CLI `--harmonics h7`) + release v1.5.0. Additive minor, no breaking changes.

## Current Position

Phase: 33 — Lunar Declination δ (COMPLETE — all 4 plans done)
Plan: Phase 33 complete; Phase 34 next
Status: Plan 04 complete. DECL-09 satisfied: 4 declination functions + β-vs-δ/montant/OOB documented in api.md+concepts.md+changelog.md; FR api.po/concepts.po/changelog.po fully translated, .mo recompiled, html-fr renders "déclinaison". Phase 33 fully delivered.
Last activity: 2026-06-03 — Plan 04 executed (33-04-SUMMARY.md, commits 9b4b6e6/38ceb61).

Progress: Phase 33 complete (4/4 plans done)

## Next Step

**`/gsd:plan-phase 34`** (if not already planned) or **`/gsd:execute-phase 34 --plan 01`** — Phase 34 Harmonics Debt (ASP-F2 → ASP-F3 → ASP-F1). Plans already exist at `.planning/phases/34-harmonics-debt/`.

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
- CHART_DTYPE body_decl consistency boundary: body_decl matches declination() ARRAY path (both use calc_planet_position_batch); scalar declination() uses calc_planet_position (up to 0.025° diff on outer planets). Chart is internally self-consistent.
- eps_b[..., np.newaxis] broadcast pattern for ε over the (14,) body axis — works for 0-d (scalar jd) and (S,) (array jd) cases.
- [Phase 33]: Composite body_decl derived via coordinates chain on composite λ,β (NOT midpoint of parents' δ) — Open Question 1 resolved option (a)
- [Phase 33]: Equatorial Declination section uses MyST anchor for cross-references between api.md sections

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
- v1.5: TBD / 3 phases (33-35) — roadmap created 2026-06-03; Plan 33-01 done (6 min, 3 tasks, 3 files); Plan 33-02 done (7 min, 3 tasks, 3 files); Plan 33-03 done (4 min, 3 tasks, 3 files); Plan 33-04 done (7 min, 2 tasks, 9 files) — Phase 33 COMPLETE

## Session Continuity

Last session: 2026-06-03 — Plan 04 of Phase 33 executed. DECL-09 docs en+fr complete: api.md (4 functions + Equatorial Declination section), concepts.md (β-vs-δ, montant/descendant, OOB), changelog.md (v1.5 entry). FR .po fully translated + .mo recompiled. Both builds clean. Commits: 9b4b6e6 (docs EN), 38ceb61 (docs FR).
Stopped at: Phase 33 Plan 04 complete. Phase 33 FULLY DONE.
Resume file: None — proceed with Phase 34 (Harmonics Debt).
