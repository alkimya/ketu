# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)
- ✅ **v1.4 Dynamic Harmonics & Chiron Range** — Phases 28-32 (shipped 2026-06-03; `ketu==1.4.0` on PyPI via OIDC — on-the-fly `generate_harmonic_aspects(h)` generator wired through the full detection chain with the frozen `core.aspects` table + preset fingerprints byte-identical, Chiron orb 0°→4° (Pluto parity), Chiron range widened to 1900–2100 (`.npz` regenerated, max|Δλ|=0.001214°), docs recentred on the 180°-division default (en+fr); archived to `.planning/milestones/v1.4-ROADMAP.md`)
- 🚧 **v1.5 Lunar Declination & Harmonics Debt** — Phases 33-35 (ROADMAP CREATED 2026-06-03; targets `ketu==1.5.0`, additive minor — equatorial declination δ as a first-class vectorizable quantity (`declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds` + `body_decl` in `CHART_DTYPE`), dynamic-harmonics debt paydown (ASP-F2 `H{h}-{k}` naming contract, ASP-F3 `find_aspect_timing` orb derivation, ASP-F1 CLI `--harmonics h7`), release. No breaking changes; `is_ascending` (β) and the frozen `core.aspects` table stay UNCHANGED.)

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

### 🚧 v1.5 Lunar Declination & Harmonics Debt (Phases 33-35) — ACTIVE

- [x] **Phase 33: Lunar Declination δ** (4/4 plans) — completed 2026-06-03 — equatorial declination δ as a first-class vectorizable quantity, montant/descendant trajectory, OOB, and `body_decl` in `CHART_DTYPE`
- [x] **Phase 34: Harmonics Debt (ASP-F1/F2/F3)** (4/4 plans) — completed 2026-06-03 — `H{h}-{k}` naming contract pinned as public API (TestNamingContractF2), `find_aspect_timing` gains `dyn_coef` orb derivation, CLI `--harmonics h7` via `HarmonicsSelection` NamedTuple (Quadrinovile bug fixed); `core.aspects` V1/V13 fingerprints byte-identical
- [ ] **Phase 35: Release v1.5.0** — quality gates + version/CHANGELOG/UPGRADING + PyPI publish via OIDC (user-checkpoint-gated)

#### Phase 33: Lunar Declination δ

**Goal**: A user can compute any body's equatorial declination δ (scalar and vectorized over date arrays), its rate of change, the Moon's biodynamic montant/descendant trajectory, and out-of-bounds state — and every computed chart (and the relational/predictive charts that inherit from it) carries declination in a new `body_decl` field, with the feature documented en + fr. All additive: `is_ascending` (ecliptic latitude β) stays byte-for-byte UNCHANGED.
**Depends on**: Nothing (first v1.5 phase; fully additive; reuses the existing `coordinates.py` chain). Independent of Phase 34.
**Requirements**: DECL-01, DECL-02, DECL-03, DECL-04, DECL-05, DECL-06, DECL-07, DECL-08, DECL-09
**Success Criteria** (what must be TRUE):
  1. A user can call `declination(jdate, body)` and get δ in degrees (north +, south −, in [−90, +90]) for any of the 14 bodies, with the same call working element-wise over a NumPy `jdate` array (no Python loop in the hot path), and a regression test pins it to machine-precision agreement with the existing `ecliptic_to_equatorial` → `rectangular_to_spherical` chain. (DECL-01, DECL-02, DECL-03)
  2. A user can call `declination_velocity(jdate, body)` for dδ/dt in °/day (forward finite difference, step mirroring `lat_velocity`, no longitude-style wraparound), and `is_ascending_declination(jdate, body)` returns True exactly when dδ/dt > 0 (montante) — a function distinct from and parallel to the unchanged β-based `is_ascending`. (DECL-04, DECL-05)
  3. A user can call `is_out_of_bounds(jdate, body)` and get True exactly when |δ| > ε using the instantaneous obliquity ε(jd) via `true_obliquity` as the threshold. (DECL-06)
  4. Every chart returned by `compute_chart` (and inherited by synastry / composite / returns) carries a `body_decl` field (14 bodies, f8, additive, mirroring `body_lats`) populated with each body's declination — no recomputation needed downstream — and a `CHART_DTYPE` layout ratchet test guards the additive field change (analogue of the 13→14 body-count ratchet). (DECL-07, DECL-08)
  5. The declination feature is documented en + fr — the four public functions plus the aspect-centric montant/descendant framing (draconic month ~27.21 d, OOB nodal cycle) and the explicit β-vs-δ distinction. (DECL-09)
**Plans**: 4 plans

Plans:

- [x] 33-01-PLAN.md — Core declination functions (declination / declination_velocity / is_ascending_declination / is_out_of_bounds) + unit & Meeus-equivalence tests (DECL-01..06) [Wave 1]
- [x] 33-02-PLAN.md — body_decl in CHART_DTYPE + compute_chart wiring + dtype ratchet (DECL-07 chart half, DECL-08) [Wave 2]
- [x] 33-03-PLAN.md — Downstream propagation: composite explicit populate (zero-fill trap) + returns inheritance test + synastry no-op (DECL-07 downstream) [Wave 3]
- [x] 33-04-PLAN.md — Docs en + fr: 4 functions, montant/descendant + β-vs-δ + OOB framing, changelog, FR .po translated & recompiled (DECL-09) [Wave 4]

**Details:**
Declination is computed via the direct Meeus eq. 13.4 formula (`sin δ = sin β·cos ε + cos β·sin ε·sin λ`), guarded by a regression test asserting equality with the existing rectangular `coordinates.py` chain (verified Δ = 0 to machine precision). δ-velocity mirrors the existing `lat_velocity` forward-finite-difference idiom (step 0.01 d) — no wraparound correction since δ ∈ [−90, +90] is bounded and monotone through zero. The montant/descendant helper `is_ascending_declination` is the equatorial analogue of `is_ascending` and must NOT collide with it (β and δ are distinct quantities, do not flip on the same days). OOB uses the instantaneous obliquity ε(jd) (`true_obliquity`), physically correct and free. `body_decl` is added as `("body_decl", "f8", (14,))` parallel to `body_lats`, a deliberate dtype-version bump with a ratchet test mirroring the prior `test_dtype.py` pattern; downstream positional-contract impact (Kala) documented. This is the largest new-surface v1.5 phase. See `.planning/research/DECLINATION.md`.

#### Phase 34: Harmonics Debt (ASP-F1/F2/F3)

**Goal**: The three dynamic-harmonics debts left open by v1.4 are paid down — the synthetic off-table aspect naming scheme `H{h}-{k}` is a documented, pinned public API contract; `find_aspect_timing` can derive its dynamic orb itself from a coefficient instead of the caller passing it raw; and a user can request an arbitrary harmonic on the CLI via `--harmonics h7` — all while the frozen 14-row `core.aspects` table and its V1/V13 sha256 preset fingerprints stay byte-identical.
**Depends on**: Nothing (independent of Phase 33; relies only on the v1.4 dynamic-harmonics engine already shipped). Internal order F2 → F3 → F1 (the CLI surface depends on the naming contract being stable).
**Requirements**: HARM-01, HARM-02, HARM-03, HARM-04, HARM-05, HARM-06, HARM-07, HARM-08, HARM-09
**Success Criteria** (what must be TRUE):
  1. The `H{h}-{k}` naming scheme (k = 1..h//2, byte string in an S16 field, ascending k, always `H{h}-{k}` with no traditional-name substitution by the generator) is a documented public API contract, and a pinning test asserts `generate_harmonic_aspects(h)['name']` exactly for representative harmonics including boundaries (h=2 opposition-only; even h folding the last row to exactly 180°; h up to 64). (HARM-01, HARM-02)
  2. The documentation distinguishes the two channels clearly: the GENERATOR always emits `H{h}-{k}`, while the DETECTION layer prefers the canonical table name on angle collision (120° → Trine, not `H3-1`). (HARM-03)
  3. `find_aspect_timing` accepts a new `dyn_coef: Optional[float] = None` parameter and derives the orb itself as `(bodies['orb'][b1] + bodies['orb'][b2]) / 2 * dyn_coef`; the static path (`orb=None` → `get_orb` table lookup) and the explicit `orb=<float>` escape hatch both stay backward-compatible and byte-identical, with the precedence when both `orb` and `dyn_coef` are given defined and tested. (HARM-04, HARM-05)
  4. A user can run `--harmonics h7` (h-prefixed, case-insensitive, disambiguated from the rejected bare integer and from preset/index syntax) and get the harmonic's h//2 aspects via `dynamic_specs=`; `parse_harmonics_spec` returns a typed shape (mask + dynamic_specs, e.g. a `NamedTuple`) clean under mypy `--strict`. The grammar is Tight — `h7` alone or the existing comma index list; `traditional,h7` and `h7,h11` are explicitly deferred. (HARM-06, HARM-07)
  5. The existing v1.1 CLI byte-stability fixture stays UNCHANGED (verified, not re-pinned); a NEW byte-stability fixture for `--harmonics h7` is freshly generated and manually audited; the resolved-config stderr header labels the arbitrary-harmonic selection clearly; and the `--harmonics h7` CLI surface (syntax, semantics, the Tight-grammar boundary) is documented en + fr. (HARM-08, HARM-09)
**Plans**: 4 plans in 3 waves (F2 → F3 → F1; Wave 2 = F3 ∥ F1-engine, Wave 3 = F1-fixture+docs)

Plans:

- [ ] 34-01-naming-contract-f2-PLAN.md — F2 (HARM-01..03): pin the `H{h}-{k}` naming contract (TestNamingContractF2), promote it to the generator docstring, document the GENERATOR-vs-DETECTION two-channel distinction + traditional-name table (en + fr). No code change.
- [ ] 34-02-find-aspect-timing-f3-PLAN.md — F3 (HARM-04..05): add `dyn_coef` to `find_aspect_timing` (explicit-orb-first 3-branch, silent precedence), TestFindAspectTimingF3, docs en + fr.
- [ ] 34-03-cli-h7-engine-f1-PLAN.md — F1 engine (HARM-06..07): `HarmonicsSelection` NamedTuple + `^h(\d+)$` branch, `print_aspects` dynamic_specs (Quadrinovile bug fix), `cmd_aspects`/`emit_resolved_config`/parser wiring, all broken assertions updated + TestHarmonicTokenF1 + h7 integration.
- [ ] 34-04-h7-byte-stability-docs-f1-PLAN.md — F1 fixture+docs (HARM-08..09): generate + manually audit + pin the `--harmonics h7` byte-stability fixture (ketu ritual), TestHarmonicsH7ByteStable sibling class (v1.1 fixture UNCHANGED), `--harmonics h7` CLI docs en + fr.

**Details:**
Internal implementation order is F2 → F3 → F1: HARM-01..03 (naming contract) first because the CLI surface (F1) depends on the naming contract being stable; then HARM-04..05 (`find_aspect_timing` orb derivation); then HARM-06..09 (CLI `--harmonics h7`). The `H{h}-{k}` contract is frozen across v1.5+ minor/patch releases (the `(h, k) → name/angle/coef` mapping never changes; adding new `h` support never alters existing rows). `find_aspect_timing` gets `dyn_coef: Optional[float] = None` (Option (a) from research — `Optional[float]` is clean under `--strict`, no `np.void` single-row typing); explicit `orb` is checked first, so the escape hatch short-circuits regardless of `dyn_coef`; precedence when both given is defined and tested. CLI grammar is Tight (`h7` via `^h(\d+)$` applied after the preset + comma branches, before the bare-int trap; range validation left to `generate_harmonic_aspects`); `parse_harmonics_spec` returns a `HarmonicsSelection` NamedTuple `(mask, dynamic_specs)` reusing the existing `DynamicAspectSpec` type. The v1.1 fixture must stay byte-identical (wrapper change is internal); a new `--harmonics h7` fixture is generated and manually audited per the ketu ritual. `core.aspects` V1/V13 sha256 fingerprints stay byte-identical throughout. See `.planning/research/HARMONICS_DEBT.md`.

#### Phase 35: Release v1.5.0

**Goal**: `ketu==1.5.0` is published to PyPI via OIDC with a GitHub release — all quality gates green, the version bumped in all source-of-truth files, CHANGELOG + UPGRADING documenting the additive declination + arbitrary-harmonic surface, and a fresh-venv smoke FROM PyPI confirming the v1.5 surface works with no `pyswisseph` at runtime. Gated by a user checkpoint: the user reviews the whole milestone before tag/publish.
**Depends on**: Phases 33 + 34 (full v1.5 API surface final). LAST phase. **User-checkpoint-gated** — do not chain into publish without the user's go-ahead.
**Requirements**: REL-01, REL-02, REL-03
**Success Criteria** (what must be TRUE):
  1. All quality gates are green — 100% coverage (`fail_under=100`, zero pragma), mypy `--strict` clean, numpydoc + interrogate gates pass, full test suite passes. (REL-01)
  2. The version is bumped to 1.5.0 (`pyproject.toml` + `ketu/__init__.py`); a dated `[1.5.0]` CHANGELOG documents Added (declination δ + montant/descendant + OOB + `body_decl`; arbitrary-harmonic CLI `h7`) and Changed (none breaking); `fr/CHANGELOG.md` is synced; UPGRADING v1.4→v1.5 + README "What's New" updated. (REL-02)
  3. `ketu==1.5.0` is shipped to PyPI via OIDC trusted publishing; tag `v1.5.0` AND `origin/main` are BOTH pushed (RTD follows main, PyPI follows tag); a GitHub release carries the sdist + wheel. (REL-03)
  4. A post-publish fresh-venv smoke FROM PyPI asserts the v1.5 surface: declination, montant/descendant, OOB, `--harmonics h7`, and no `pyswisseph` at runtime. (REL-03)
**Plans**: TBD (refined during plan-phase)

Plans:

- [ ] 35-01: TBD (plan-phase derives the wave breakdown)

**Details:**
LAST phase, user-checkpoint-gated before tag/publish (the user reviews the whole milestone himself first — do not enchaîner into publish without his feu vert). RTD follows `origin/main`, PyPI follows the tag → push BOTH the tag `v1.5.0` and `origin/main`. Post-publish smoke runs FROM PyPI in a fresh venv and asserts all four v1.5 surface points plus `importlib.util.find_spec('swisseph') is None`. Mirror the v1.4 release shape (OIDC `publish.yml`, GitHub release with sdist + wheel).

## Progress

**Execution Order:** Within v1.5, Phases 33 and 34 are independent (either order). Phase 35 depends on 33 + 34 and is LAST (user-checkpoint-gated before publish). (Prior milestones: see archived roadmaps.)

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
| **33. Lunar Declination δ**                       | **v1.5**  | **4/4**        | ✓ Complete  | 2026-06-03 |
| **34. Harmonics Debt (ASP-F1/F2/F3)**             | **v1.5**  | **4/4**        | ✓ Complete  | 2026-06-03 |
| **35. Release v1.5.0**                            | **v1.5**  | **0/TBD**      | Not started | -          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*v1.4 phase details archived to `.planning/milestones/v1.4-ROADMAP.md`*
*Roadmap last updated: 2026-06-03 — Phase 34 (Harmonics Debt) COMPLETE (4/4 plans, verifier passed 5/5 must-haves; HARM-01..09 shipped — `H{h}-{k}` naming contract pinned as public API (TestNamingContractF2 + frozen docstring), GENERATOR-vs-DETECTION two-channel docs, `find_aspect_timing` `dyn_coef` orb derivation (explicit-orb-wins precedence), CLI `--harmonics h7` via `HarmonicsSelection` NamedTuple with Tight grammar (Quadrinovile display bug fixed), new h7 byte-stability fixture + v1.1 fixture unchanged, docs en + fr; `core.aspects` V1/V13 sha256 fingerprints byte-identical, core.py untouched; 1623 tests / 100% coverage / mypy --strict clean). Phases 33 + 34 done → only Phase 35 (Release v1.5.0) remains, LAST + user-checkpoint-gated. Next: `/gsd:plan-phase 35`.*
