# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)
- ✅ **v1.4 Dynamic Harmonics & Chiron Range** — Phases 28-32 (shipped 2026-06-03; `ketu==1.4.0` on PyPI via OIDC — on-the-fly `generate_harmonic_aspects(h)` generator wired through the full detection chain with the frozen `core.aspects` table + preset fingerprints byte-identical, Chiron orb 0°→4° (Pluto parity), Chiron range widened to 1900–2100 (`.npz` regenerated, max|Δλ|=0.001214°), docs recentred on the 180°-division default (en+fr); archived to `.planning/milestones/v1.4-ROADMAP.md`)
- ✅ **v1.5 Lunar Declination & Harmonics Debt** — Phases 33-35 (shipped 2026-06-04; `ketu==1.5.0` on PyPI via OIDC — additive minor: equatorial declination δ as a first-class vectorizable quantity (`declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds` + `body_decl` in `CHART_DTYPE`), dynamic-harmonics debt paydown (ASP-F2 `H{h}-{k}` naming contract, ASP-F3 `find_aspect_timing` `dyn_coef` orb derivation, ASP-F1 CLI `--harmonics h7`). No breaking changes; `is_ascending` (β) and the frozen `core.aspects` table stay byte-identical. Archived to `.planning/milestones/v1.5-ROADMAP.md`.)
- 🚧 **v1.6 Declination Aspects** — Phases 36-37 (in progress — parallel + contra-parallel detection on the δ axis, body-derived δ orbs (Ketu-style), `find_declination_aspects` companion function + `DECLA_ASPECT_DTYPE`, docs en + fr, release `ketu==1.6.0`)

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

### 🚧 v1.6 Declination Aspects (In Progress)

**Milestone Goal:** Add `find_declination_aspects` as a pure-NumPy companion function consuming `CHART_DTYPE["body_decl"]` (already shipped in v1.5), detecting parallels (δ₁≈δ₂, same hemisphere) and contra-parallels (δ₁≈−δ₂, opposite hemisphere) with body-derived orbs (`DECLA_COEF=1/12`, `MIN_DECL_ORB=0.5°`). Additive: `CHART_DTYPE` unchanged, the frozen 14-row `core.aspects` table + V1/V13 sha256 fingerprints byte-identical. The final lightweight Ketu engine milestone before the Rahu UI project.

#### Phase 36: Declination Aspects Core

**Goal:** Users can detect parallel and contra-parallel aspects between all 14 bodies in a natal chart using a dedicated, vectorizable companion function.
**Depends on:** v1.5 (uses `body_decl` from `CHART_DTYPE`, `core.bodies['orb']`)
**Requirements:** DECLA-01, DECLA-02, DECLA-03, DECLA-04
**Success Criteria** (what must be TRUE):
  1. `find_declination_aspects(chart["body_decl"])` returns a `DECLA_ASPECT_DTYPE` structured array where every row is either `kind="P"` (parallel: same non-zero sign, `|δ₁−δ₂| ≤ orb`) or `kind="CP"` (contra-parallel: opposite non-zero signs, `|δ₁+δ₂| ≤ orb`), with `body1` < `body2` (upper-triangle, no duplicates).
  2. The orb for each pair is exactly `max((core.bodies['orb'][b1] + core.bodies['orb'][b2]) / 2 * (1/12), 0.5)` — Sun/Moon yields 1.0°, Rahu/Lilith yields 0.5° (floor applied), verified by a test.
  3. The four pitfall cases from the research brief are guarded by explicit tests: `+15°/−15°` is CP not P (sign conflation guard); a 7° Sun/Moon gap is not a parallel (orb inflation guard); both bodies at δ=0° yield zero aspects (zero-sign trap guard); Rahu/Lilith at gap 0.1° yields one parallel (MIN_DECL_ORB floor guard).
  4. A vectorized batch path accepts `body_decl` of shape `(S, 14)` and returns parallel/contra masks of shape `(S, 91)` using the precomputed 14×14 orb matrix — no Python loop over bodies in the hot path; tested with a multi-chart array.
  5. `CHART_DTYPE` is byte-identical to its v1.5 layout (ratchet test passes); the frozen 14-row `core.aspects` table and V1/V13 sha256 fingerprints are unmodified; 100% coverage maintained (fail_under=100, zero pragma); mypy `--strict` clean.
**Plans:** TBD

Plans:
- [ ] 36-01: `DECLA_ASPECT_DTYPE`, `DECLA_COEF`, `MIN_DECL_ORB` constants + `find_declination_aspects` scalar implementation (P/CP detection with all pitfall guards)
- [ ] 36-02: Vectorized batch path (`(S,14)→(S,91)`) + full test suite (orb formula, pitfall cases, batch path, ratchet guards)

#### Phase 37: Documentation + Release v1.6.0

**Goal:** Users can read the full parallel/contra-parallel documentation in English and French, and `ketu==1.6.0` is live on PyPI after a human go/no-go gate.
**Depends on:** Phase 36
**Requirements:** DECLA-05
**Success Criteria** (what must be TRUE):
  1. The English and French documentation covers all five DECLA-05 items: the signed-δ parallel/contra-parallel definitions (same-hemisphere rule), the body-derived orb formula with the worked Sun/Moon example (1.0°), the biodynamic framing (parallel ≈ conjunction / contra-parallel ≈ opposition on the δ axis), the explicit "parallel ≠ longitude conjunction" distinction, and the `//` / `#` symbol conventions with `P` / `CP` text abbreviations.
  2. A human go/no-go relecture-validation checkpoint is passed by the user before any irreversible publish action (tag, PyPI push, GitHub release).
  3. Version is bumped to `1.6.0` in all three source-of-truth files (`pyproject.toml`, `ketu/__init__.py`, `docs/source/conf.py`); a dated `[1.6.0]` CHANGELOG entry exists in the EN root file and the RTD docs copy (byte-identical content); a fresh French `[1.6.0]` CHANGELOG section exists; an UPGRADING v1.5→v1.6 guide is present.
  4. `ketu==1.6.0` is published on PyPI via OIDC (`publish.yml`); both `origin/main` and the tag `v1.6.0` are pushed (RTD follows main, PyPI follows tag); a GitHub release with sdist + wheel is attached.
  5. A post-publish fresh-venv smoke test FROM PyPI passes: `find_declination_aspects` correctly detects at least one parallel, no `pyswisseph` at runtime (`find_spec('swisseph') is None`).
**Plans:** TBD

Plans:
- [ ] 37-01: Sphinx docs en + fr (parallel/contra-parallel definitions, orb formula, biodynamic framing, symbol conventions, OOB interaction note); FR `.po` translated + `.mo` recompiled
- [ ] 37-02: Release v1.6.0 (version bump, CHANGELOG en+fr, UPGRADING, README; human go/no-go checkpoint; tag + origin/main push; OIDC publish; GitHub release; post-publish smoke)

## Progress

**Execution Order:** v1.6 phases execute 36 → 37.

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
| **36. Declination Aspects Core**                  | **v1.6**  | **0/TBD**      | Not started | -          |
| **37. Documentation + Release v1.6.0**            | **v1.6**  | **0/TBD**      | Not started | -          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*v1.5 phase details archived to `.planning/milestones/v1.5-ROADMAP.md`*
*Roadmap last updated: 2026-06-04 — v1.6 Declination Aspects roadmap created. 2 phases (36-37), 5 requirements mapped (DECLA-01..05, 100% coverage). Phase 36 = detection core (DECLA-01..04); Phase 37 = docs + release (DECLA-05). Next: `/gsd:plan-phase 36`.*
