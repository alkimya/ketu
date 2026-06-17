# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)
- ✅ **v1.4 Dynamic Harmonics & Chiron Range** — Phases 28-32 (shipped 2026-06-03; `ketu==1.4.0` on PyPI via OIDC — on-the-fly `generate_harmonic_aspects(h)` generator wired through the full detection chain with the frozen `core.aspects` table + preset fingerprints byte-identical, Chiron orb 0°→4° (Pluto parity), Chiron range widened to 1900–2100 (`.npz` regenerated, max|Δλ|=0.001214°), docs recentred on the 180°-division default (en+fr); archived to `.planning/milestones/v1.4-ROADMAP.md`)
- ✅ **v1.5 Lunar Declination & Harmonics Debt** — Phases 33-35 (shipped 2026-06-04; `ketu==1.5.0` on PyPI via OIDC — additive minor: equatorial declination δ as a first-class vectorizable quantity (`declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds` + `body_decl` in `CHART_DTYPE`), dynamic-harmonics debt paydown (ASP-F2 `H{h}-{k}` naming contract, ASP-F3 `find_aspect_timing` `dyn_coef` orb derivation, ASP-F1 CLI `--harmonics h7`). No breaking changes; `is_ascending` (β) and the frozen `core.aspects` table stay byte-identical. Archived to `.planning/milestones/v1.5-ROADMAP.md`.)
- ✅ **v1.6 Declination Aspects** — Phases 36-37 (shipped 2026-06-04; `ketu==1.6.0` on PyPI via OIDC — additive `ketu.declination` subpackage: parallel + contra-parallel detection on the δ axis (`find_declination_aspects` scalar + `declination_aspect_masks` batch + `DECLA_ASPECT_DTYPE`), body-derived δ orbs (`DECLA_COEF=1/12`, `MIN_DECL_ORB=0.5°`), docs en + fr. No breaking changes; `CHART_DTYPE` byte-identical, `core.aspects` unchanged. Archived to `.planning/milestones/v1.6-ROADMAP.md`.)
- ✅ **v1.7 Fictitious-Point Orbs** — Phases 38-39 (shipped 2026-06-15; `ketu==1.7.0` on PyPI via OIDC — orb 0°→2° on Rahu/Ketu/Lilith so the three fictitious points enter aspect detection, surgical Rahu↔Ketu Opposition filter (tautological 180°), synastry oracle rewrite + full regression sweep, MINOR-not-patch for Kala, docs en+fr. Archived to `.planning/milestones/v1.7-ROADMAP.md`.)
- 🚧 **v1.8 Declination Speed** — Phases 40-41 (in progress — Phase 40 planned: 3 plans, 3 waves; expose dδ/dt as `body_decl_speed` in `CHART_DTYPE`, `DECL_STANDSTILL_EPS` public constant, chart-level helper, docs en+fr, release 1.8.0)

## Phases

<details>
<summary>✅ v1.0 Production Stability (Phases 1-7) — SHIPPED 2026-02-12</summary>

- [x] Phase 1: API Surface Cleanup
- [x] Phase 2: Correctness Fixes
- [x] Phase 2.1: Fix Moon velocity and rename vlong API (INSERTED)
- [x] Phase 3: Dependency Cleanup
- [x] Phase 4: Test Coverage Hardening
- [x] Phase 5: Complex Math Integration
- [x] Phase 6: Documentation & Type Checking
- [x] Phase 7: Release Preparation

Full details archived to `.planning/milestones/v1.0-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.1 Flexibility & Houses (Phases 8-12) — SHIPPED 2026-05-08</summary>

- [x] Phase 8: Lilith Verification & Fix (5/5 plans) — completed 2026-05-06
- [x] Phase 9: Configurable Aspects (6/6 plans) — completed 2026-05-07
- [x] Phase 10: Houses Module (6/6 plans) — completed 2026-05-07
- [x] Phase 11: CLI Refactor & Integration (6/6 plans) — completed 2026-05-07
- [x] Phase 12: Release Preparation v1.1.0 (4/4 plans) — completed 2026-05-08

Full details archived to `.planning/milestones/v1.1-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.2 Astrologie relationnelle et prédictive (Phases 13-20) — SHIPPED 2026-05-28</summary>

- [x] Phase 13: Doc Gates & CI Foundation (5/5 plans) — completed 2026-05-08
- [x] Phase 14: Chart Abstraction Foundation (5/5 plans) — completed 2026-05-09
- [x] Phase 15: Additional House Systems (4/4 plans) — completed 2026-05-09
- [x] Phase 16: Synastry (5/5 plans) — completed 2026-05-11
- [x] Phase 17: Composite Chart (Midpoint) (4/4 plans) — completed 2026-05-24
- [x] Phase 18: Solar + Lunar Returns (Std + Reloc) (5/5 plans) — completed 2026-05-28
- [x] Phase 19: Arabic Parts Framework + 3 Parts (3/3 plans) — completed 2026-05-28
- [x] Phase 20: Release Preparation v1.2.0 (4/4 plans) — completed 2026-05-28

Full details archived to `.planning/milestones/v1.2-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.3 Chiron & Engine Hardening (Phases 21-27, + inserted 26.1) — SHIPPED 2026-06-01</summary>

- [x] Phase 21: Quality (4/4 plans) — completed 2026-05-29
- [x] Phase 22: Ephemeris Refactor (3/3 plans) — completed 2026-05-29
- [x] Phase 23: Spike Chiron (2/2 plans) — completed 2026-05-29
- [x] Phase 24: Chiron (5/5 plans) — completed 2026-05-29
- [x] Phase 25: Documentation (3/3 plans) — completed 2026-05-30
- [x] Phase 26: Aspects Data-Driven (3/3 plans) — completed 2026-06-01
- [x] Phase 26.1: French Documentation Translation (INSERTED) (8/8 plans) — completed 2026-06-01
- [x] Phase 27: Release 1.3.0 (2/2 plans) — completed 2026-06-01

Full details archived to `.planning/milestones/v1.3-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.4 Dynamic Harmonics & Chiron Range (Phases 28-32) — SHIPPED 2026-06-03</summary>

- [x] Phase 28: Dynamic Harmonic Generator + Detection (3/3 plans) — completed 2026-06-03
- [x] Phase 29: Chiron Orb 4° (1/1 plan) — completed 2026-06-03
- [x] Phase 30: Chiron Range 1900–2100 (2/2 plans) — completed 2026-06-03
- [x] Phase 31: Documentation (en + fr) (7/7 plans) — completed 2026-06-03
- [x] Phase 32: Release v1.4.0 (2/2 plans) — completed 2026-06-03

Full details archived to `.planning/milestones/v1.4-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.5 Lunar Declination & Harmonics Debt (Phases 33-35) — SHIPPED 2026-06-04</summary>

- [x] Phase 33: Lunar Declination δ (4/4 plans) — completed 2026-06-03
- [x] Phase 34: Harmonics Debt (ASP-F1/F2/F3) (4/4 plans) — completed 2026-06-03
- [x] Phase 35: Release v1.5.0 (2/2 plans) — completed 2026-06-04

Full details archived to `.planning/milestones/v1.5-ROADMAP.md`.

</details>

<details>
<summary>✅ v1.6 Declination Aspects (Phases 36-37) — SHIPPED 2026-06-04</summary>

Full detail archived to `.planning/milestones/v1.6-ROADMAP.md`. Additive `ketu.declination` subpackage detecting parallels/contra-parallels on the δ axis; `CHART_DTYPE` byte-identical, `core.aspects` unchanged. Shipped `ketu==1.6.0` to PyPI via OIDC.

- [x] Phase 36: Declination Aspects Core (2/2 plans) — completed 2026-06-04 — DECLA-01..04
- [x] Phase 37: Documentation + Release v1.6.0 (3/3 plans) — completed 2026-06-04 — DECLA-05

</details>

<details>
<summary>✅ v1.7 Fictitious-Point Orbs (Phases 38-39) — SHIPPED 2026-06-15</summary>

Full detail archived to `.planning/milestones/v1.7-ROADMAP.md`. Orb 0°→2° on Rahu/Ketu/Lilith so the three fictitious points enter aspect detection; surgical Rahu↔Ketu Opposition filter (tautological 180°); synastry oracle rewrite + full regression sweep. MINOR-not-patch because aspect results change for Kala. Shipped `ketu==1.7.0` to PyPI via OIDC.

- [x] Phase 38: Fictitious-Point Orbs Engine (2/2 plans) — completed 2026-06-15 — ORB-01/02/03
- [x] Phase 39: Documentation + Release v1.7.0 (3/3 plans) — completed 2026-06-15 — ORB-04/REL-01

</details>

### 🚧 v1.8 Declination Speed (In Progress)

**Milestone Goal:** Expose dδ/dt as `body_decl_speed` in `CHART_DTYPE` — the gap that blocks the Rahu UI from showing montant/descendant in declination without computing astronomy in the front-end. The calculation already exists since v1.5 (`declination_velocity`); this milestone exposes the field, defines the `DECL_STANDSTILL_EPS` public contract, and ships the chart-level helper.

- [ ] **Phase 40: Declination Speed Field & Chart API** — Add `body_decl_speed` to `CHART_DTYPE`, populate via `compute_chart`, inherit by synastry/composite/returns, re-pin dtype ratchet, define `DECL_STANDSTILL_EPS`, expose chart-level helper
- [ ] **Phase 41: Documentation + Release v1.8.0** — Docs en+fr for the field, step, threshold, and helper; MINOR bump + UPGRADING Kala re-pin guidance; human go/no-go; PyPI publish

## Phase Details

### Phase 40: Declination Speed Field & Chart API

**Goal**: `CHART_DTYPE` carries `body_decl_speed` (dδ/dt, deg/day) for all 14 bodies, inherited across the full chart family, with a public standstill threshold and a chart-level ascending-declination helper that Rahu can consume without computing any astronomy
**Depends on**: Phase 39 (v1.7 shipped green base)
**Requirements**: DSPD-01, DSPD-02, DSPD-03, DSPD-04, DSPD-05, DSPD-06
**Success Criteria** (what must be TRUE):

  1. `np.dtype(CHART_DTYPE).names` includes `body_decl_speed`; a chart computed by `compute_chart` has the field populated with non-zero finite float64 values (verified against `declination_velocity(jd, body)` scalar — Δ = 0 or documented FD tolerance)
  2. `compute_chart` over an array `jd` produces a `body_decl_speed` array with the correct shape `(N, 14)`, using Δt = 0.01 day verbatim (no new parameter, no new API surface)
  3. Synastry, composite, and returns all inherit `body_decl_speed`; composite speed is computed from the composite chart directly (a test pins that it differs from the naïve parent-midpoint value)
  4. The dtype ratchet test is updated and passes: the old layout fingerprint is replaced by the new one (the break is intentional and documented with Kala positional-access impact)
  5. `DECL_STANDSTILL_EPS` is importable from `ketu.calculations` (or the appropriate public namespace), its value is tested, and `|dδ/dt| ≤ DECL_STANDSTILL_EPS` classifies a body as in standstill
  6. A chart-level `is_ascending_declination(chart)` helper returns ascending / descending / neutral (standstill) per body using the `body_decl_speed` field and `DECL_STANDSTILL_EPS`; its output is consistent with the existing v1.5 scalar for matching inputs; 100% coverage maintained

**Plans**: 3 plans, 3 waves

- [x] 40-01-PLAN.md — Foundation: append `body_decl_speed` to `CHART_DTYPE`, define `DECL_STANDSTILL_EPS = 0.001`, re-pin the dtype ratchet (Wave 1) — DSPD-01/04/05
- [ ] 40-02-PLAN.md — Natal: populate `body_decl_speed` in `compute_chart` (vectorised FD, Δ=0 vs scalar) + `is_ascending_declination_chart` helper + returns inheritance (Wave 2) — DSPD-01/02/03/06
- [ ] 40-03-PLAN.md — Composite: derive `body_decl_speed` from the composite's own frozen λ,β (D-01, anti-averaging ratchet) + synastry inheritance pinning (Wave 3 — depends on 40-02 so parent charts carry the field) — DSPD-03

### Phase 41: Documentation + Release v1.8.0

**Goal**: The `body_decl_speed` field, the 0.01 d FD step, `DECL_STANDSTILL_EPS`, the chart-level helper, and the Ketu/Rahu boundary are fully documented in English and French, the version is bumped to 1.8.0, and `ketu==1.8.0` is live on PyPI
**Depends on**: Phase 40
**Requirements**: DSPD-07, REL-01
**Success Criteria** (what must be TRUE):

  1. `docs/source/api.md` and `docs/source/concepts.md` (en + fr) document `body_decl_speed`, `DECL_STANDSTILL_EPS`, the chart-level `is_ascending_declination` helper, the 0.01 d step rationale, and the explicit statement that Rahu computes no threshold of its own; FR `.mo` files recompiled (no English fallback in the French build)
  2. `CHANGELOG.md` has a dated `[1.8.0]` entry (EN + FR) documenting the new field and the MINOR-not-patch rationale; `UPGRADING.md` gives explicit Kala re-pin guidance (dtype layout grows, positional/`.view()` users must adapt)
  3. `ketu==1.8.0` is live on PyPI via OIDC trusted publishing (push main + tag); the human go/no-go relecture-validation gate is honoured before the irreversible publish
  4. Post-publish fresh-venv smoke FROM PyPI confirms: `body_decl_speed` present in `CHART_DTYPE`, field populated with non-trivial values for a test chart, `DECL_STANDSTILL_EPS` importable, no `pyswisseph` at runtime

**Plans**: TBD

## Progress

**Execution Order:** v1.8 phases execute 40 → 41.

| Phase                                             | Milestone | Plans Complete | Status      | Completed  |
| ------------------------------------------------- | --------- | -------------- | ----------- | ---------- |
| 1-7 (collapsed)                                   | v1.0      | 16/16          | ✓ Complete  | 2026-02-12 |
| 8. Lilith Verification & Fix                      | v1.1      | 5/5            | ✓ Complete  | 2026-05-06 |
| 9. Configurable Aspects                           | v1.1      | 6/6            | ✓ Complete  | 2026-05-07 |
| 10. Houses Module                                 | v1.1      | 6/6            | ✓ Complete  | 2026-05-07 |
| 11. CLI Refactor & Integration                    | v1.1      | 6/6            | ✓ Complete  | 2026-05-07 |
| 12. Release Preparation v1.1.0                    | v1.1      | 4/4            | ✓ Complete  | 2026-05-08 |
| 13. Doc Gates & CI Foundation                     | v1.2      | 5/5            | ✓ Complete  | 2026-05-08 |
| 14. Chart Abstraction Foundation                  | v1.2      | 5/5            | ✓ Complete  | 2026-05-09 |
| 15. Additional House Systems                      | v1.2      | 4/4            | ✓ Complete  | 2026-05-09 |
| 16. Synastry                                      | v1.2      | 5/5            | ✓ Complete  | 2026-05-11 |
| 17. Composite Chart (Midpoint)                    | v1.2      | 4/4            | ✓ Complete  | 2026-05-24 |
| 18. Solar + Lunar Returns (Std + Reloc)           | v1.2      | 5/5            | ✓ Complete  | 2026-05-28 |
| 19. Arabic Parts Framework + 3 Parts              | v1.2      | 3/3            | ✓ Complete  | 2026-05-28 |
| 20. Release Preparation v1.2.0                    | v1.2      | 4/4            | ✓ Complete  | 2026-05-28 |
| 21. Quality                                       | v1.3      | 4/4            | ✓ Complete  | 2026-05-29 |
| 22. Ephemeris Refactor                            | v1.3      | 3/3            | ✓ Complete  | 2026-05-29 |
| 23. Spike Chiron                                  | v1.3      | 2/2            | ✓ Complete  | 2026-05-29 |
| 24. Chiron                                        | v1.3      | 5/5            | ✓ Complete  | 2026-05-29 |
| 25. Documentation                                 | v1.3      | 3/3            | ✓ Complete  | 2026-05-30 |
| 26. Aspects Data-Driven                           | v1.3      | 3/3            | ✓ Complete  | 2026-06-01 |
| 26.1 French Doc Translation (INSERTED)            | v1.3      | 8/8            | ✓ Complete  | 2026-06-01 |
| 27. Release 1.3.0                                 | v1.3      | 2/2            | ✓ Complete  | 2026-06-01 |
| 28. Dynamic Harmonic Generator + Detection        | v1.4      | 3/3            | ✓ Complete  | 2026-06-03 |
| 29. Chiron Orb 4°                                 | v1.4      | 1/1            | ✓ Complete  | 2026-06-03 |
| 30. Chiron Range 1900–2100                        | v1.4      | 2/2            | ✓ Complete  | 2026-06-03 |
| 31. Documentation (en + fr)                       | v1.4      | 7/7            | ✓ Complete  | 2026-06-03 |
| 32. Release v1.4.0                                | v1.4      | 2/2            | ✓ Complete  | 2026-06-03 |
| 33. Lunar Declination δ                           | v1.5      | 4/4            | ✓ Complete  | 2026-06-03 |
| 34. Harmonics Debt (ASP-F1/F2/F3)                | v1.5      | 4/4            | ✓ Complete  | 2026-06-03 |
| 35. Release v1.5.0                                | v1.5      | 2/2            | ✓ Complete  | 2026-06-04 |
| 36. Declination Aspects Core                      | v1.6      | 2/2            | ✓ Complete  | 2026-06-04 |
| 37. Documentation + Release v1.6.0               | v1.6      | 3/3            | ✓ Complete  | 2026-06-04 |
| 38. Fictitious-Point Orbs Engine                  | v1.7      | 2/2            | ✓ Complete  | 2026-06-15 |
| 39. Documentation + Release v1.7.0                | v1.7      | 3/3            | ✓ Complete  | 2026-06-15 |
| 40. Declination Speed Field & Chart API           | v1.8      | 1/3 | In Progress|  |
| 41. Documentation + Release v1.8.0               | v1.8      | 0/TBD          | Not started | -          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*v1.5 phase details archived to `.planning/milestones/v1.5-ROADMAP.md`*
*v1.6 phase details archived to `.planning/milestones/v1.6-ROADMAP.md`*
*v1.7 phase details archived to `.planning/milestones/v1.7-ROADMAP.md`*
*Roadmap last updated: 2026-06-17 — Phase 40 planned (3 plans, 2 waves).*
