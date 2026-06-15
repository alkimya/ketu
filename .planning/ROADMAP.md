# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)
- ✅ **v1.4 Dynamic Harmonics & Chiron Range** — Phases 28-32 (shipped 2026-06-03; `ketu==1.4.0` on PyPI via OIDC — on-the-fly `generate_harmonic_aspects(h)` generator wired through the full detection chain with the frozen `core.aspects` table + preset fingerprints byte-identical, Chiron orb 0°→4° (Pluto parity), Chiron range widened to 1900–2100 (`.npz` regenerated, max|Δλ|=0.001214°), docs recentred on the 180°-division default (en+fr); archived to `.planning/milestones/v1.4-ROADMAP.md`)
- ✅ **v1.5 Lunar Declination & Harmonics Debt** — Phases 33-35 (shipped 2026-06-04; `ketu==1.5.0` on PyPI via OIDC — additive minor: equatorial declination δ as a first-class vectorizable quantity (`declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds` + `body_decl` in `CHART_DTYPE`), dynamic-harmonics debt paydown (ASP-F2 `H{h}-{k}` naming contract, ASP-F3 `find_aspect_timing` `dyn_coef` orb derivation, ASP-F1 CLI `--harmonics h7`). No breaking changes; `is_ascending` (β) and the frozen `core.aspects` table stay byte-identical. Archived to `.planning/milestones/v1.5-ROADMAP.md`.)
- ✅ **v1.6 Declination Aspects** — Phases 36-37 (shipped 2026-06-04; `ketu==1.6.0` on PyPI via OIDC — additive `ketu.declination` subpackage: parallel + contra-parallel detection on the δ axis (`find_declination_aspects` scalar + `declination_aspect_masks` batch + `DECLA_ASPECT_DTYPE`), body-derived δ orbs (`DECLA_COEF=1/12`, `MIN_DECL_ORB=0.5°`), docs en + fr. No breaking changes; `CHART_DTYPE` byte-identical, `core.aspects` unchanged. Archived to `.planning/milestones/v1.6-ROADMAP.md`.)
- [ ] **v1.7 Fictitious-Point Orbs** — Phases 38-39 (in progress — orb 0°→2° on Rahu/Ketu/Lilith, targeted Rahu↔Ketu Opposition filter, synastry oracle rewrite + full regression sweep, docs en+fr, `ketu==1.7.0` on PyPI)

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

### v1.7 Fictitious-Point Orbs (Phases 38-39) — IN PROGRESS

- [ ] **Phase 38: Fictitious-Point Orbs Engine** — Single-source orb 0°→2° edit in `core.bodies`, Rahu↔Ketu Opposition filter in the aspect engine, full test-suite regression sweep + synastry oracle rewrite
- [ ] **Phase 39: Documentation + Release v1.7.0** — Docs en+fr (new orb, filter rationale, MINOR-not-patch Kala note), version bump, CHANGELOG/UPGRADING, human go/no-go gate, PyPI OIDC publish, post-publish smoke

## Phase Details

### Phase 38: Fictitious-Point Orbs Engine

**Goal**: Rahu, Ketu, and Lilith participate in aspect detection with a 2° orb, the tautological Rahu↔Ketu Opposition is suppressed, and the full test suite is green against the new oracles
**Depends on**: Nothing (first phase of v1.7; builds on shipped v1.6 base)
**Requirements**: ORB-01, ORB-02, ORB-03
**Success Criteria** (what must be TRUE):

  1. A call to `get_orb` for Rahu, Ketu, or Lilith returns 2.0°; a point↔planet pair (e.g. Rahu↔Sun) returns 7.0°; a point↔point pair (e.g. Rahu↔Lilith) returns 2.0°
  2. The aspect engine never emits a `(Rahu, Ketu)` + `Opposition` detection regardless of the separation; every other aspect involving Rahu or Ketu (e.g. Rahu conjunction, Rahu↔Sun opposition, Ketu↔Lilith conjunction) is detected normally
  3. `tests/synastry/test_orbs.py` and `tests/synastry/test_modes_idempotent.py` pass with oracles rewritten to the new 2° point orb; no oracle update is silent — every changed detection is deliberately pinned
  4. All ~40 test files that reference Rahu, Ketu, or Lilith are green; `pytest tests/` reports 0 failures, 100% coverage maintained, mypy `--strict` clean
**Plans**: 2 plans

Plans:
- [ ] 38-01-PLAN.md — ORB-01 single-source orb 0→2 edit + ORB-02 shared `_is_tautological_node_opposition` helper wired into all natal/scalar emit paths + helper unit & per-path integration tests (Wave 1)
- [ ] 38-02-PLAN.md — ORB-03 synastry oracle rewrite (D-06/D-07) + full ~31-file regression sweep, final gates green (Wave 2, depends on 38-01)

### Phase 39: Documentation + Release v1.7.0

**Goal**: The 2° fictitious-point orb change and its rationale are documented in English and French, and `ketu==1.7.0` is live on PyPI with a human-approved go/no-go
**Depends on**: Phase 38
**Requirements**: ORB-04, REL-01
**Success Criteria** (what must be TRUE):

  1. The English and French docs explain the new 2° orb for Rahu/Ketu/Lilith, the Rahu↔Ketu Opposition filter and its rationale (tautological fixed angle), and the MINOR-not-patch reasoning (aspect results change for Kala); FR `.po` translated and `.mo` recompiled with no English fallback
  2. The `[1.7.0]` CHANGELOG entry (EN + FR) is dated, lists the orb change and the Opposition filter; UPGRADING covers the v1.6→v1.7 migration note for Kala consumers
  3. Version is bumped to `1.7.0` in all source-of-truth files; the human go/no-go relecture-validation gate is honoured before any irreversible action (tag, push, publish)
  4. `ketu==1.7.0` is live on PyPI via OIDC trusted publishing; a post-publish fresh-venv smoke FROM PyPI confirms: at least one Rahu or Lilith aspect is detected, the Rahu↔Ketu Opposition is absent from results, and `pyswisseph` is not importable at runtime
**Plans**: TBD

## Progress

**Execution Order:** v1.7 phases execute 38 → 39.

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
| **38. Fictitious-Point Orbs Engine**              | **v1.7**  | **0/2**        | Planned     | -          |
| **39. Documentation + Release v1.7.0**            | **v1.7**  | **0/TBD**      | Not started | -          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*v1.5 phase details archived to `.planning/milestones/v1.5-ROADMAP.md`*
*v1.6 phase details archived to `.planning/milestones/v1.6-ROADMAP.md`*
*Roadmap last updated: 2026-06-15 — v1.7 Fictitious-Point Orbs STARTED. Phases 38-39 defined. ORB-01..04 + REL-01 mapped. Next: `/gsd-plan-phase 38`.*
