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
| 38. Fictitious-Point Orbs Engine                  | v1.7      | 2/2            | ✓ Complete  | 2026-06-15 |
| 39. Documentation + Release v1.7.0                | v1.7      | 3/3            | ✓ Complete  | 2026-06-15 |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*v1.5 phase details archived to `.planning/milestones/v1.5-ROADMAP.md`*
*v1.6 phase details archived to `.planning/milestones/v1.6-ROADMAP.md`*
*v1.7 phase details archived to `.planning/milestones/v1.7-ROADMAP.md`*
*Roadmap last updated: 2026-06-16 — v1.7 Fictitious-Point Orbs milestone archived (Phases 38-39, `ketu==1.7.0` shipped). Next: `/gsd-new-milestone`.*
