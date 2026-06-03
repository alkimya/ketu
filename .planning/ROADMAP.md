# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)
- ✅ **v1.4 Dynamic Harmonics & Chiron Range** — Phases 28-32 (shipped 2026-06-03; `ketu==1.4.0` on PyPI via OIDC — on-the-fly `generate_harmonic_aspects(h)` generator wired through the full detection chain with the frozen `core.aspects` table + preset fingerprints byte-identical, Chiron orb 0°→4° (Pluto parity), Chiron range widened to 1900–2100 (`.npz` regenerated, max|Δλ|=0.001214°), docs recentred on the 180°-division default (en+fr); archived to `.planning/milestones/v1.4-ROADMAP.md`)

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

## Progress

**Execution Order:** Phases 28 and 29 are independent (either first). Phase 30 depends on 29. Phase 31 depends on 28 + 29 + 30. Phase 32 depends on 31.

| Phase                                             | Milestone | Plans Complete | Status     | Completed  |
| ------------------------------------------------- | --------- | -------------- | ---------- | ---------- |
| 1-7 (collapsed)                                   | v1.0      | 16/16          | ✓ Complete | 2026-02-12 |
| 8. Lilith Verification & Fix                      | v1.1      | 5/5            | ✓ Complete | 2026-05-06 |
| 9. Configurable Aspects                           | v1.1      | 6/6            | ✓ Complete | 2026-05-07 |
| 10. Houses Module                                 | v1.1      | 6/6            | ✓ Complete | 2026-05-07 |
| 11. CLI Refactor & Integration                    | v1.1      | 6/6            | ✓ Complete | 2026-05-07 |
| 12. Release Preparation v1.1.0                    | v1.1      | 4/4            | ✓ Complete | 2026-05-08 |
| 13. Doc Gates & CI Foundation                     | v1.2      | 5/5            | ✓ Complete | 2026-05-08 |
| 14. Chart Abstraction Foundation                  | v1.2      | 5/5            | ✓ Complete | 2026-05-09 |
| 15. Additional House Systems                      | v1.2      | 4/4            | ✓ Complete | 2026-05-09 |
| 16. Synastry                                      | v1.2      | 5/5            | ✓ Complete | 2026-05-11 |
| 17. Composite Chart (Midpoint)                    | v1.2      | 4/4            | ✓ Complete | 2026-05-24 |
| 18. Solar + Lunar Returns (Std + Reloc)           | v1.2      | 5/5            | ✓ Complete | 2026-05-28 |
| 19. Arabic Parts Framework + 3 Parts              | v1.2      | 3/3            | ✓ Complete | 2026-05-28 |
| 20. Release Preparation v1.2.0                    | v1.2      | 4/4            | ✓ Complete | 2026-05-28 |
| 21. Quality                                       | v1.3      | 4/4            | ✓ Complete | 2026-05-29 |
| 22. Ephemeris Refactor                            | v1.3      | 3/3            | ✓ Complete | 2026-05-29 |
| 23. Spike Chiron                                  | v1.3      | 2/2            | ✓ Complete | 2026-05-29 |
| 24. Chiron                                        | v1.3      | 5/5            | ✓ Complete | 2026-05-29 |
| 25. Documentation                                 | v1.3      | 3/3            | ✓ Complete | 2026-05-30 |
| 26. Aspects Data-Driven                           | v1.3      | 3/3            | ✓ Complete | 2026-06-01 |
| 26.1 French Doc Translation (INSERTED)            | v1.3      | 8/8            | ✓ Complete | 2026-06-01 |
| 27. Release 1.3.0                                 | v1.3      | 2/2            | ✓ Complete | 2026-06-01 |
| **28. Dynamic Harmonic Generator + Detection**    | **v1.4**  | **3/3**        | ✓ Complete | 2026-06-03 |
| **29. Chiron Orb 4°**                             | **v1.4**  | **1/1**        | ✓ Complete | 2026-06-03 |
| **30. Chiron Range 1900–2100**                    | **v1.4**  | **2/2**        | ✓ Complete | 2026-06-03 |
| **31. Documentation (en + fr)**                   | **v1.4**  | **7/7**        | ✓ Complete | 2026-06-03 |
| **32. Release v1.4.0**                            | **v1.4**  | **2/2**        | ✓ Complete | 2026-06-03 |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*Roadmap last updated: 2026-06-03 — MILESTONE v1.4 Dynamic Harmonics & Chiron Range COMPLETE & ARCHIVED. All 5 phases (28-32), 15/15 plans, `ketu==1.4.0` live on PyPI (tag `v1.4.0` + origin/main pushed). Milestone collapsed; full details in `.planning/milestones/v1.4-ROADMAP.md` + MILESTONES.md. Next: `/gsd:new-milestone` to scope v1.5.*
