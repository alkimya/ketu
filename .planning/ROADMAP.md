# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)

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

## Progress

| Phase                                  | Milestone | Plans Complete | Status        | Completed  |
| -------------------------------------- | --------- | -------------- | ------------- | ---------- |
| 1-7 (collapsed)                        | v1.0      | 16/16          | ✓ Complete    | 2026-02-12 |
| 8. Lilith Verification & Fix           | v1.1      | 5/5            | ✓ Complete    | 2026-05-06 |
| 9. Configurable Aspects                | v1.1      | 6/6            | ✓ Complete    | 2026-05-07 |
| 10. Houses Module                      | v1.1      | 6/6            | ✓ Complete    | 2026-05-07 |
| 11. CLI Refactor & Integration         | v1.1      | 6/6            | ✓ Complete    | 2026-05-07 |
| 12. Release Preparation v1.1.0         | v1.1      | 4/4            | ✓ Complete    | 2026-05-08 |
| 13. Doc Gates & CI Foundation          | v1.2      | 5/5            | ✓ Complete    | 2026-05-08 |
| 14. Chart Abstraction Foundation       | v1.2      | 5/5            | ✓ Complete    | 2026-05-09 |
| 15. Additional House Systems           | v1.2      | 4/4            | ✓ Complete    | 2026-05-09 |
| 16. Synastry                           | v1.2      | 5/5            | ✓ Complete    | 2026-05-11 |
| 17. Composite Chart (Midpoint)         | v1.2      | 4/4            | ✓ Complete    | 2026-05-24 |
| 18. Solar + Lunar Returns (Std + Reloc)| v1.2      | 5/5            | ✓ Complete    | 2026-05-28 |
| 19. Arabic Parts Framework + 3 Parts   | v1.2      | 3/3            | ✓ Complete    | 2026-05-28 |
| 20. Release Preparation v1.2.0         | v1.2      | 4/4            | ✓ Complete    | 2026-05-28 |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*Roadmap last updated: 2026-05-29 — v1.2 milestone COMPLETE and archived (8 phases, 35 plans, all 37 requirements satisfied; `ketu==1.2.0` on PyPI). Next: `/gsd:new-milestone` for v1.3.*

*Roadmap previous update: 2026-05-28 — Phase 19 complete (3/3 plans, PARTS-01..08 satisfied, 1284 tests + 2 skipped, `ketu/parts/` extensible registry + sect-aware `calculate_part` (Fortune/Spirit) + fixed Marriage + `--list-parts` CLI, coverage 100% on `ketu/parts/`, verifier PASSED 5/5; 5 remaining Hermetic Lots deferred to v1.3). Only Phase 20 (Release Prep v1.2.0) remains.*

*Roadmap previous update: 2026-05-28 — Phase 18 complete (5/5 plans, RET-01..06 + LRET-01..05 satisfied, 1253 tests, `solar_return` + `lunar_return` sharing a single pure-NumPy `_solve_return` bisection helper, coverage 100% sur `ketu/returns/`). Self-consistency oracle at 0.0001° is the PRIMARY gate; pyswisseph cross-check is TEST-ONLY (per-body tolerance relaxed with measured ephemeris-theory deltas — Ketu TRUE Sun + truncated-Meeus lunar vs Swiss Ephemeris Moshier ELP). Ketu runtime stays pure NumPy. Test-extra package typo `pysweph` → `pyswisseph` fixed. Astro.com manual cross-check on 6 resolved instants deferred to pre-Phase-20 follow-up (anti-bot; pyswisseph CI substitute strictly stronger than Phase 17).*
