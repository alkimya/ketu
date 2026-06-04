---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Lunar Declination & Harmonics Debt
status: in-progress
last_updated: "2026-06-03T21:00:00Z"
last_activity: 2026-06-03
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 8
  completed_plans: 8
  percent: 67
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03 — v1.5 milestone started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** v1.5 roadmap created — 3 phases (33-35), 21/21 v1.5 requirements mapped. Ready to plan Phase 33 (Lunar Declination δ). Scope: declination δ (scalar + vectorized + montant/descendant + OOB + `body_decl` in `CHART_DTYPE`) + harmonics debt (ASP-F2 naming contract, ASP-F3 timing orb, ASP-F1 CLI `--harmonics h7`) + release v1.5.0. Additive minor, no breaking changes.

## Current Position

Phase: 35 — Release v1.5.0 (in progress — Plan 01 done)
Plan: Plan 01 of Phase 35 complete; Plans 02-03 remain.
Status: Plan 35-01 complete. REL-01+REL-02 satisfied: version bumped to 1.5.0 in all three source-of-truth files (pyproject.toml + ketu/__init__.py + docs/source/conf.py); changelogs date-stamped (Unreleased -> 2026-06-04, content untouched); French [1.5.0] section authored in fr/CHANGELOG.md; UPGRADING.md v1.4->v1.5 section added; README Roadmap updated. 1626 tests, 100% coverage.
Last activity: 2026-06-04 — Plan 35-01 executed (3 tasks, commits f917271/634a176/3295af0).

Progress: Phase 34 complete (4/4 plans done). Phase 35 next.

## Next Step

**`/gsd:execute-phase 35`** — Phase 35 Plan 02: quality gates (mypy --strict full confirmation). Then Plan 03: PyPI via OIDC (tag + main both pushed), post-publish smoke.

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
- [Phase 34-01]: Detection channel is static-first — 120° always Trine (i_asp=9), never H3-1 (i_asp=-2)
- [Phase 34-01]: Cross-file MyST anchor reference uses {ref} role, not path-based concepts.md#anchor (path form triggers myst.xref_missing)
- [Phase 34-02]: Explicit orb wins silently when both orb= and dyn_coef= given — no ValueError raised (HARM-05 locked, overrides brief §4-C)
- [Phase 34-02]: dyn_coef orb formula mirrors calculate_aspects:215-216 exactly — single canonical formula across the library
- [Phase 34-03]: _resolve_dynamic_name recomputes angular separation from jdate+body IDs to identify matched dyn row (result dtype stores dyn_angle-dist, not dyn_angle itself)
- [Phase 34-03]: assert isinstance(dyn, np.ndarray) at _harmonic_label call site narrows DynamicAspectSpec union for mypy (hN token always produces single array)
- [Phase 34-04]: Fixture audited against 5 criteria before pinning — H7-k names, no Quadrinovile, septile angles, timing block identical to v1.1, U+00BA degree symbol
- [Phase 34-04]: Tight-grammar boundary: h<N> alone supported in v1.5; h7,h11 and traditional,h7 mixing deferred to HARMF-01, documented and rejected with argparse error

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
- v1.5: TBD / 3 phases (33-35) — roadmap created 2026-06-03; Plan 33-01 done (6 min, 3 tasks, 3 files); Plan 33-02 done (7 min, 3 tasks, 3 files); Plan 33-03 done (4 min, 3 tasks, 3 files); Plan 33-04 done (7 min, 2 tasks, 9 files) — Phase 33 COMPLETE; Plan 34-01 done (15 min, 3 tasks, 8 files) — HARM-01/02/03 satisfied; Plan 34-02 done (12 min, 3 tasks, 5 files) — HARM-04/05 satisfied; Plan 34-03 done (11 min, 3 tasks, 8 files) — HARM-06/07 satisfied; Plan 34-04 done (8 min, 3 tasks, 8 files) — HARM-08/09 satisfied — Phase 34 COMPLETE; Plan 35-01 done (4 min, 3 tasks, 8 files) — REL-01/02 satisfied (version bump + changelogs + UPGRADING + README)

## Session Continuity

Last session: 2026-06-04 — Plan 01 of Phase 35 executed. REL-01/02 satisfied: version bumped to 1.5.0 in all 3 source-of-truth files, changelogs date-stamped (2026-06-04), French [1.5.0] section authored, UPGRADING v1.4->v1.5 added, README Roadmap updated. 1626 tests, 100% coverage. Commits: f917271 (chore), 634a176 (docs), 3295af0 (docs).
Stopped at: Phase 35 Plan 01 complete.
Resume file: None — proceed with Phase 35 Plan 02 (quality gates).
