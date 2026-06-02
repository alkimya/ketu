# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- ✅ **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (shipped 2026-05-28; `ketu==1.2.0` on PyPI, archived to `.planning/milestones/v1.2-ROADMAP.md`)
- ✅ **v1.3 Chiron & Engine Hardening** — Phases 21-27 (+ inserted 26.1) (shipped 2026-06-01; `ketu==1.3.0` on PyPI — Chiron embedded as 14th body, engine hardened to 100% coverage, data-driven aspect engine, full French docs; archived to `.planning/milestones/v1.3-ROADMAP.md`)

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

### 🚧 v1.4 Dynamic Harmonics & Chiron Range (Phases 28-32) — IN PROGRESS

**Milestone Goal:** Make aspect harmonics open-ended — any integer harmonic (H17, etc.) usable as a first-class aspect across the whole detection chain via an on-the-fly generator, without disturbing the frozen `core.aspects` table or its preset fingerprints — then widen Chiron's validity range to 1900–2100, correct its orb to 4° (Pluto parity), recentre the documentation on the 180°-division default (H1/H2/H3/H6), and ship `ketu==1.4.0`.

**Axis order (BINDING):** Phase 28 (dynamic harmonics + detection integration) and Phase 29 (Chiron orb 4°) are fully independent — either order is valid. Phase 30 (Chiron range) MUST follow Phase 29 (avoids double CLI-fixture churn). Phase 31 (documentation) MUST follow all feature phases (28 + 29 + 30). Phase 32 (release) MUST follow Phase 31.

**Cross-cutting constraints (v1.4):**

- **Pure-NumPy runtime is NON-NEGOTIABLE.** Dynamic harmonic generation is plain NumPy angle arithmetic; Chiron `.npz` regeneration stays offline pyswisseph-build-only. No scipy, no new runtime deps.
- **Frozen `core.aspects` table and sha256 fingerprints PRESERVED.** Dynamic path is parallel and additive — never mutates the 14-row table.
- **`_VALID_HARMONICS` must NOT gate the dynamic path.** The dynamic generator must never call `aspects_for_harmonics` internally.
- **Vectorizable** — all new calculations batchable over date arrays; no Python loops in hot paths.
- **100% coverage + numpydoc BLOCKING** — new public function `generate_harmonic_aspects` needs full numpydoc docstrings + examples; CI gates hold.
- **CRITICAL (release):** Push `origin/main` AND the tag — RTD follows main, PyPI follows tag; pushing only the tag freezes the docs (learned v1.3 release).

#### Phase 28: Dynamic Harmonic Generator + Detection Integration

**Goal**: A user can generate first-class aspects for any integer harmonic `h` on the fly and have them detected through the full aspect chain — `calculate_aspects`, vectorized, batch, cycles, synastry — without touching the frozen `core.aspects` table or its preset sha256 fingerprints.
**Depends on**: Nothing (first v1.4 phase; fully additive, no shared files with Phase 29)
**Requirements**: ASP-04, ASP-05, ASP-06, ASP-07, ASP-08, ASP-09
**Success Criteria** (what must be TRUE):

  1. A user can call `generate_harmonic_aspects(h)` for any integer `h` (e.g. 7, 11, 17) and receive a structured-array of `(angle, coef)` specs using the unified 360° convention — angles `fold_to_0_180(k·360/h)` for `k=1..h//2`, coefficient `k/h`, mirror pairs deduplicated, 0°/360° never emitted, unnamed high harmonics carry a blank symbol.
  2. A user can pass those specs to `calculate_aspects` (scalar, vectorized, batch) and have dynamic aspects detected with correct per-pair orbs derived from `core.bodies['orb']` × dynamic coefficient; the output rows are indistinguishable in type from static-table detections (same dtype, `i_asp = -2` sentinel for dynamic rows, no IndexError).
  3. Dynamic aspects flow through cycles and synastry: cycle series generated with dynamic specs include dynamic aspect detections; synastry called with `dynamic_specs` returns dynamic rows in `SYNASTRY_DTYPE` with orb derived from `core.bodies['orb']` × dynamic coefficient.
  4. `find_aspect_timing` and `find_aspects_between_dates` accept dynamic angles without raising `IndexError`; off-table angles resolve via a synthetic name, not a crash.
  5. The `core.aspects` table sha256 fingerprints (V1 `c5bd177...`, V13 `3258530...`) are unchanged; `test_aspects_byte_fingerprint` passes; `_VALID_HARMONICS` is never consulted on the dynamic path.

**Plans**: TBD

#### Phase 29: Chiron Orb 4°

**Goal**: Chiron's natal orb is 4° (Pluto parity) — a single-source constant change that propagates automatically to all aspect detection, synastry, cycles, and the CLI — with test artifacts updated to reflect the new value.
**Depends on**: Nothing (fully independent of Phase 28; either may execute first)
**Requirements**: CHIR-06, CHIR-07, CHIR-08
**Success Criteria** (what must be TRUE):

  1. `core.bodies['orb']` for Chiron is 4°; calling `get_orb` (or inspecting `core.bodies` directly) returns 4° for Chiron — the same as Pluto.
  2. The byte-stable CLI fixture `tests/cli/fixtures/v1_1_reference_output.txt` is regenerated and manually audited: every new or changed Chiron aspect line is confirmed correct via `git diff` inspection before committing (not blindly accepted).
  3. Synastry test files (`test_modes_idempotent.py`, `test_orbs.py`) no longer group Chiron with the zero-orb points (Rahu/Ketu/Lilith); a new explicit test pins Chiron orb = 4° in synastry (`_BODY_ORBS_16` entry for Chiron is 4°).

**Plans**: TBD

#### Phase 30: Chiron Range 1900–2100

**Goal**: Chiron's embedded Chebyshev coefficients span 1900–2100, validated to < 0.01° against Swiss Ephemeris (including the ~1895–1896 perihelion region near the lower bound), so callers with early-20th-century dates receive accurate Chiron positions without a runtime error.
**Depends on**: Phase 29 (orb constant must be final before `.npz` regeneration to avoid double CLI-fixture churn)
**Requirements**: CHIR-09, CHIR-10, CHIR-11
**Success Criteria** (what must be TRUE):

  1. A blocking spike is run BEFORE the `.npz` is committed: `tools/gen_chiron_coeffs.py` is executed over 1900–2100 and `max|Δλ|` vs Swiss Ephemeris is measured and recorded — including segments covering the ~1895–1896 perihelion — passing the < 0.01° gate; if the locked Phase 23 parameters (seg=32d, degree=10) fail the gate on the early wings, the degree is raised (e.g. 10→12) or parameters adjusted, and the decision is recorded before committing.
  2. `ketu/data/chiron_coeffs.npz` is regenerated with `jd_start`/`jd_end` reflecting the 1900–2100 range; the embedded `actual_len` for the partial first/last segments is correct (the Phase 24 last-segment fix preserved); runtime evaluation stays 100% pure NumPy (no `pyswisseph` import in `ketu/ephemeris/chiron.py`).
  3. Regression tests are re-pinned to span 1900–2100: at minimum one new reference longitude pre-1950 (e.g. 1920 or 1930) and one post-2050 (e.g. 2080) are pinned, and `test_chiron_regression.py` passes the < 0.01° gate on the full new range.

**Plans**: TBD

#### Phase 31: Documentation (en + fr)

**Goal**: The Sphinx docs (en + fr) accurately reflect the v1.4 API surface — concepts.md recentred on the 180°-division default, stale default-aspect claims corrected, the dynamic-harmonics generator and Chiron updates documented — with zero English fallback in touched French gettext catalogs, and a clean build at the 1-warning baseline.
**Depends on**: Phases 28 + 29 + 30 (API surface and all constant values must be final)
**Requirements**: DOC-14, DOC-15, DOC-16, DOC-17
**Success Criteria** (what must be TRUE):

  1. `concepts.md` aspect tables show CLASSICAL (5) and TRADITIONAL (7) only, with default vs opt-in marked; EXTENDED (H5/H9/H10) is removed from the tables but framed as "available in code" — no example on any page references a removed-from-table aspect as if it were in the table; the 180°-division default (H1/H2/H3/H6) is the framing baseline.
  2. `migration.md` and `relational_charts.md` contain no claim that the default aspect set is EXTENDED or "classical (5)"; the current v1.3+ TRADITIONAL (7) default is the only stated default; no remaining doc/source file contains a stale `EXTENDED.*default` or `classical.*default` string for the library default.
  3. `generate_harmonic_aspects(h)` is documented in the API and/or concepts pages with a runnable example, the accepted ~2× smaller full-circle orb note, Chiron 1900–2100 range, and Chiron orb 4°; no reference to Kala appears anywhere in the Ketu docs.
  4. Every French gettext catalog whose source strings changed (due to any of the above edits) is re-extracted, translated (zero new English-fallback `msgstr`), and recompiled to `.mo`; `make html` (en) and `make html-fr` build clean at the established 1-warning baseline (no new warnings introduced).

**Plans**: TBD

#### Phase 32: Release v1.4.0

**Goal**: `ketu==1.4.0` is published to PyPI via OIDC with a GitHub release, the version is bumped in all source-of-truth files, CHANGELOG documents all changes, and a fresh-venv smoke confirms the dynamic generator, Chiron 4° orb, and 1900–2100 range work correctly with no `pyswisseph` at runtime.
**Depends on**: Phase 31
**Requirements**: REL-12, REL-13
**Success Criteria** (what must be TRUE):

  1. Version is 1.4.0 in both `pyproject.toml` and `ketu/__init__.py`; CHANGELOG `[1.4.0]` lists Added (dynamic harmonics generator, Chiron 1900–2100 range) and Changed (Chiron orb 0°→4°, documentation recentring); `fr/CHANGELOG.md` is synced with the same entries in French.
  2. `ketu==1.4.0` is live on PyPI via OIDC trusted publishing with a GitHub release attaching sdist + wheel; both `origin/main` AND the tag `v1.4.0` are pushed (RTD follows main, PyPI follows tag).
  3. A fresh-venv `pip install ketu==1.4.0` smoke confirms: `generate_harmonic_aspects(7)` returns the correct H7 angles; `core.bodies['orb']` for Chiron is 4°; `calc_planet_position(jd_1920, 13)` returns a finite Chiron longitude (1900–2100 range); `importlib.util.find_spec('swisseph')` is `None` (no pyswisseph at runtime).

**Plans**: TBD

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
| **28. Dynamic Harmonic Generator + Detection**    | **v1.4**  | **0/TBD**      | ⬜ Pending  | —          |
| **29. Chiron Orb 4°**                             | **v1.4**  | **0/TBD**      | ⬜ Pending  | —          |
| **30. Chiron Range 1900–2100**                    | **v1.4**  | **0/TBD**      | ⬜ Pending  | —          |
| **31. Documentation (en + fr)**                   | **v1.4**  | **0/TBD**      | ⬜ Pending  | —          |
| **32. Release v1.4.0**                            | **v1.4**  | **0/TBD**      | ⬜ Pending  | —          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*v1.2 phase details archived to `.planning/milestones/v1.2-ROADMAP.md`*
*v1.3 phase details archived to `.planning/milestones/v1.3-ROADMAP.md`*
*Roadmap last updated: 2026-06-02 — v1.4 (Dynamic Harmonics & Chiron Range) roadmapped: 5 phases (28-32), all 18 v1.4 requirements mapped (ASP/CHIR/DOC/REL), 100% coverage. Axis order BINDING: Phase 28 (dynamic harmonics) and Phase 29 (Chiron orb) are independent; Phase 30 (Chiron range) follows Phase 29; Phase 31 (docs) follows all feature phases; Phase 32 (release) follows Phase 31.*
