# Roadmap: Ketu

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- ✅ **v1.1 Flexibility & Houses** — Phases 8-12 (shipped 2026-05-08, archived to `.planning/milestones/v1.1-ROADMAP.md`)
- 📋 **v1.2 Astrologie relationnelle et prédictive** — Phases 13-20 (planning frontier; non-breaking minor strict)

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

### 📋 v1.2 Astrologie relationnelle et prédictive (Phases 13-20)

- [x] **Phase 13: Doc Gates & CI Foundation** — Wire `interrogate ≥95%` and `numpydoc validate` early so they apply to every v1.2 module *(2026-05-08)*
- [x] **Phase 14: Chart Abstraction Foundation** — `ketu/charts/` subpackage with `CHART_DTYPE`, `compute_chart`, `is_day_chart` — keystone upstream of SYN/COMP/RET *(2026-05-09)*
- [x] **Phase 15: Additional House Systems** — Whole Sign, Equal, Regiomontanus via existing `SYSTEMS` registry; Swiss Ephemeris validation *(2026-05-09)*
- [x] **Phase 16: Synastry** — `calculate_synastry(chart_a, chart_b)` with `SYNASTRY_DTYPE`, dense + filtered output modes, dedicated synastry orbs *(2026-05-11)*
- [x] **Phase 17: Composite Chart (Midpoint)** — `calculate_composite(chart_a, chart_b)` with circular midpoint helper and composite-derived houses *(2026-05-24)*
- [ ] **Phase 18: Solar + Lunar Returns (Standard + Relocated)** — `solar_return(...)` + `lunar_return(...)` sharing a pure-NumPy `_solve_return` helper handling 360°→0° wrap; <1 arcsecond convergence on both
- [ ] **Phase 19: Arabic Parts Framework + 8 Parts** — `ketu/parts/` registry, sect-aware `calculate_part`, 7 Hermetic Lots + Marriage, `--list-parts` CLI
- [ ] **Phase 20: Release Preparation v1.2.0** — Workflow refresh (Node 24), `fr/CHANGELOG.md` decision, PyPI publish via OIDC

## Cross-Cutting Constraints (v1.2)

These apply to every v1.2 phase:

- **Non-breaking minor strict** — All new APIs are additive; no default change on existing APIs; no exports removed (v1.1 burned the BREAKING quota).
- **Pure-NumPy contract** — No new runtime dependencies. `pysweph` remains test-only (AGPL non-contamination); no scipy.
- **Python 3.10+** — CI matrix unchanged (3.10–3.13).
- **Vectorizable** — All new calculations batchable over `jd` arrays; no Python loops in hot paths.
- **UTC-only** — Timezone conversion is the caller's responsibility (reaffirmed in synastry / return docstrings where the error would be common).
- **Coverage gates** — ≥90% project, ≥85% per module, ≥95% on new modules (`ketu/charts/`, `ketu/parts/`, new house systems).
- **Doc gates** — From Phase 13 onward, every public function passes `numpydoc validate` and contributes to `interrogate ≥95%`.
- **Mypy `--strict`** clean across the package.

## Phase Details

### Phase 13: Doc Gates & CI Foundation

**Goal**: CI enforces docstring quality and coverage on every commit so the gates apply to all subsequent v1.2 work.

**Depends on**: Nothing (parallelizable with Phase 14 only after the gates land)

**Requirements**: OPS-01, OPS-02

**Success Criteria** (what must be TRUE):

1. `interrogate` is installed in `[project.optional-dependencies].test` and a CI step fails the build if docstring coverage drops below 95%.
2. `numpydoc validate` runs in CI on `ketu/` public modules; warnings surface in the build log (gate flips to blocking at end of milestone).
3. The aspirational `interrogate ≥95%` and `numpydoc validate` references in CHANGELOG / README are now backed by real CI status — no aspirational references left.
4. Re-running the gates on the v1.1 codebase produces a clean baseline (any pre-existing gaps fixed in this phase, not deferred).

**Plans:** 5 plans

Plans:
- [ ] 13-01-PLAN.md — Add `dev` extras group + `[tool.interrogate]` config; fix the 4 `_ra_formula_cusp_*` docstrings (interrogate green locally)
- [ ] 13-02-PLAN.md — Wire `interrogate` as BLOCKING CI step in `tests.yml`; add `make doc-gates` Makefile target
- [ ] 13-03-PLAN.md — Add `[tool.numpydoc_validation]` config; fix all numpydoc gaps in 9 source files (numpydoc clean locally)
- [ ] 13-04-PLAN.md — Wire `numpydoc lint` as WARNING-only CI step in `tests.yml` with Phase 20 flip-target YAML comment
- [ ] 13-05-PLAN.md — Positive-add of "Documentation Quality Gates" section in README + `## [Unreleased]` `### Added` entry in CHANGELOG citing OPS-01/OPS-02

### Phase 14: Chart Abstraction Foundation

**Goal**: Users compute a fully-resolved natal chart in a single vectorizable call, returning a NumPy structured array that is ML-interop friendly and reusable by synastry / composite / solar return.

**Depends on**: Phase 13 (doc gates apply to new module)

**Requirements**: CHART-01, CHART-02, CHART-03, CHART-04, CHART-05

**Success Criteria** (what must be TRUE):

1. `from ketu.charts import compute_chart, CHART_DTYPE, is_day_chart` resolves cleanly; `compute_chart(jd, lat, lon, system="placidus", aspects="classical")` returns a `CHART_DTYPE` array containing body positions, ASC/MC/ARMC/Vertex, cusps, and aspects in one call.
2. `compute_chart` accepts both scalar and array `jd` inputs and returns a vectorized `CHART_DTYPE` of the corresponding shape (no Python loop in the hot path).
3. `is_day_chart(jd, lat, lon)` returns `True` when the Sun is at or above the ASC (sunrise inclusive), is vectorizable over arrays, and is consistent with the Sun longitude / ASC pair stored in the same `CHART_DTYPE`.
4. Coverage on `ketu/charts/` is ≥95% (mirrors v1.1 houses gate); `numpydoc validate` clean.
5. `CHART_DTYPE` is named, frozen, and shape-documented in the module docstring, alongside a "Why structured array" section pointing to the ML-interop rationale.

**Plans**: TBD

### Phase 15: Additional House Systems

**Goal**: Users select Whole Sign, Equal, or Regiomontanus through the existing `SYSTEMS` registry — proving the v1.1 extensibility claim — with each system validated against Swiss Ephemeris.

**Depends on**: Phase 13 (doc gates); independent of Phase 14

**Parallelizable with**: Phase 14

**Requirements**: HOU2-01, HOU2-02, HOU2-03, HOU2-04, HOU2-05

**Success Criteria** (what must be TRUE):

1. `calculate_houses(jd, lat, lon, system="whole_sign")`, `system="equal"`, and `system="regiomontanus"` each return a valid `HOUSES_DTYPE` array; Whole Sign and Equal are polar-safe (no NaN at lat=80°).
2. `ketu houses --list-house-systems` (and the API equivalent) lists exactly six systems: `placidus, koch, porphyry, whole_sign, equal, regiomontanus`.
3. Each new system passes the existing 10-reference-charts oracle suite vs Swiss Ephemeris (max ASC delta documented in test output, same gate as v1.1).
4. `ketu houses --date 2025-06-21T12:00:00Z --lat 48.85 --lon 2.35 --system whole_sign` prints 12 cusps from the CLI without any additional code path beyond the existing dispatch.

**Plans**: TBD

### Phase 16: Synastry

**Goal**: Users compute aspects between two natal charts in a single call, with both dense (matrix) and filtered (orbed list) output modes and synastry-tightened orbs distinct from natal orbs.

**Depends on**: Phase 14 (CHART_DTYPE); independent of Phases 15, 17, 18, 19

**Requirements**: SYN-01, SYN-02, SYN-03, SYN-04, SYN-05

**Success Criteria** (what must be TRUE):

1. `calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry")` returns a `SYNASTRY_DTYPE` array where each row records `(body_a, body_b, aspect_type, orb, applying)` with chart-of-origin preserved on every body.
2. The caller selects dense mode (full N×M matrix of body pairs) or filtered mode (only rows whose orb is within the configured tolerance) via an explicit parameter; both modes share the same `SYNASTRY_DTYPE` schema.
3. The default `orbs="synastry"` set uses tighter orbs (3–5° on majors) than natal `"classical"` (8–10°); the orb convention is documented in the docstring with a citation.
4. Three reference synastry pairs (hand-validated against Astro.com or Solar Fire) are pinned as oracle tests; max orb delta is reported in the test output.
5. Coverage on the synastry module is ≥95%; UTC-only contract restated loudly in the API docstring (the most common user error in relational charts).

**Plans:** 5 plans

Plans:
- [ ] 16-01-PLAN.md — Foundation: `ketu/synastry/` skeleton + frozen `SYNASTRY_DTYPE` (8 fields) + `orbs.py` (formula + `_PRESETS_BY_NAME` + `resolve_orb_set` + ASC_MC default 8°) + structural/formula tests
- [ ] 16-02-PLAN.md — Compute API: `calculate_synastry()` cross-product (15×15 = 225 pairs incl. self-pairs) + dense/filtered modes + velocity-based `applying` field + unit + idempotency tests
- [ ] 16-03-PLAN.md — Oracle tests: 3 hand-validated couples (Curie, Diana/Charles, Lennon/Ono) JSON fixtures + `test_oracle.py` with max-orb-delta reporter
- [ ] 16-04-PLAN.md — CLI sub-command: `ketu synastry --date-a/--lat-a/--lon-a/--date-b/...` + `--mode` + `--system` + `--json` + `--list-orbs` introspection + tests
- [ ] 16-05-PLAN.md — Phase close-out: `make synastry-coverage` (≥95% gate) + `synastry_coverage_gate` marker + See Also cross-refs + CHANGELOG `[Unreleased]` entry + 5-criteria smoke

### Phase 17: Composite Chart (Midpoint Variant)

**Goal**: Users derive a midpoint composite chart from two natal charts as a single `CHART_DTYPE`, with circular-midpoint arithmetic verified on the wraparound case.

**Depends on**: Phase 14 (CHART_DTYPE); independent of Phases 15, 16, 18, 19

**Requirements**: COMP-01, COMP-02, COMP-03, COMP-04

**Success Criteria** (what must be TRUE):

1. `calculate_composite(chart_a, chart_b, system="placidus")` returns a `CHART_DTYPE` whose body longitudes are circular midpoints of the two natals, and whose houses are computed from the composite ASC and MC (not recomputed independently).
2. `circular_midpoint(lon_a, lon_b)` is vectorizable, modulo-360°, and `circular_midpoint(359.0, 1.0) == 0.0` (NOT 180.0) is pinned as a regression test.
3. Two reference composite pairs (hand-validated against Astro.com) are pinned as oracle tests with documented max longitude delta.
4. Davison composite is explicitly out of scope and labeled as deferred-to-v1.3 in the module docstring (no aspirational reference).

**Plans:** 4 plans

Plans:
- [ ] 17-01-PLAN.md — Foundation: `ketu/composite/` skeleton + `circular_midpoint` helper (vectorisable; `mid(359°, 1°) == 0.0` pinned regression) + module docstring with Davison-deferred-to-v1.3 Notes block (no aspirational reference)
- [ ] 17-02-PLAN.md — Compute API: `calculate_composite(chart_a, chart_b, system="placidus") -> CHART_DTYPE` with Approach A (inlined Porphyry trisection on composite ASC + composite MC; NO `calculate_houses` call) + inline aspect-matching loop on composite body_lons + COMP-01/COMP-03 ratchets (swap-symmetric, polar-safe, no-`compute_chart` grep ratchet)
- [ ] 17-03-PLAN.md — Oracle tests: 3 hand-validated composite fixtures (Curie bodies-only, Diana/Charles + Lennon/Ono with ASC/MC) at `tolerance_deg=0.0001` self-consistency; `test_oracle.py` with max-|delta| reporter; Astro.com cross-check deferred to Plan 17-04 (bot-blocked per 17-RESEARCH)
- [ ] 17-04-PLAN.md — Phase close-out: `make composite-coverage` (≥95% gate) + `composite_coverage_gate` pytest marker + sentinel test + See Also cross-refs (charts <-> composite <-> synastry) + CHANGELOG `[Unreleased]` entry citing COMP-01..04 + REQUIREMENTS status flips + 4-criteria smoke + Astro.com manual cross-check follow-up note

### Phase 18: Solar + Lunar Returns (Standard + Relocated)

**Goal**: Users compute the solar return chart for any natal birth and any target year **and** the lunar return chart for any natal birth and any target date (≥27.32-day periodicity), optionally relocating either return chart to a different lat/lon, with arc-second convergence on both resolved return times — Solar and Lunar share a single pure-NumPy `_solve_return` core.

**Depends on**: Phase 14 (CHART_DTYPE); independent of Phases 15, 16, 17, 19

**Requirements**: RET-01, RET-02, RET-03, RET-04, RET-05, LRET-01, LRET-02, LRET-03, LRET-04, LRET-05

**Success Criteria** (what must be TRUE):

1. `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus")` returns a `CHART_DTYPE` for the resolved Sun-return moment; passing `return_lat`/`return_lon` produces a relocated chart, `None` (default) uses the natal lat/lon (standard return).
2. `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system="placidus")` returns a `CHART_DTYPE` for the **first Moon-return moment ≥ `target_jd`** (Moon sidereal period ≈ 27.32 d); same relocation contract as `solar_return`. Note the API asymmetry: solar takes `target_year` (calendar-anchored), lunar takes `target_jd` (instant-anchored) — documented loudly in both docstrings.
3. The pure-NumPy root-finder on `body_longitude(t) − natal_body_longitude` is factored into a single internal helper `_solve_return(body, natal_jd, natal_lon_ref, t0, t_window, ...)`; **`solar_return` and `lunar_return` both call it**, parametrised only by body identity and the search window. Wrap-around 360°→0° is handled centrally (pre-unwrap or atan2-style residuals), pinned by wrap-around regression tests on both Sun and Moon.
4. Both returns converge to <1 arc-second of the target body longitude (pro-tools convention), reported per-return as the test verdict.
5. Three reference solar returns and three reference lunar returns (each set including one wrap-around case, hand-validated against Astro.com) are pinned as oracle tests with documented arc-second deltas. The lunar oracle set also includes one case where the return falls on the calendar day *after* `target_jd` to lock the "first return ≥ target" contract.
6. Both docstrings distinguish loudly between `natal_lat/lon` (used for the natal body longitude reference) and `return_lat/lon` (used for return-chart houses) — common-error prevention shared with RET-05/LRET-05.

**Plans**: TBD

### Phase 19: Arabic Parts Framework + 8 Parts

**Goal**: Users compute any of the 7 Hermetic Lots plus Part of Marriage by name from any chart, with sect-aware day/night formula selection and an extensible registry analogous to `SYSTEMS`.

**Depends on**: Phase 14 (`is_day_chart`, `CHART_DTYPE`); independent of Phases 15, 16, 17, 18

**Requirements**: PARTS-01, PARTS-02, PARTS-03, PARTS-04, PARTS-05, PARTS-06, PARTS-07, PARTS-08

**Success Criteria** (what must be TRUE):

1. `from ketu.parts import PARTS, calculate_part, calculate_all_parts` resolves; `PARTS` registry is iterable and lists exactly 8 parts: Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis, Marriage.
2. `calculate_part("fortune", chart)` reads `is_day_chart` from the chart, applies the day formula (`ASC + Moon − Sun`) or night formula (`ASC + Sun − Moon`) accordingly, and returns the longitude in [0°, 360°).
3. `calculate_all_parts(chart)` returns a `dict[str, float]` mapping every registered part name to its longitude; passing `parts=[...]` filters the result.
4. `ketu --list-parts` (CLI flag, mirroring `--list-house-systems`) prints all 8 part names plus a short formula summary line each.
5. Coverage on `ketu/parts/` is ≥95%; each part has a hand-derived oracle test value pinned at the documented day/night sect.

**Plans**: TBD

### Phase 20: Release Preparation v1.2.0

**Goal**: Ketu 1.2.0 is published to PyPI as a clean non-breaking minor with up-to-date workflows, an explicit `fr/CHANGELOG.md` decision logged, and migration recipes for additive APIs.

**Depends on**: Phases 13, 14, 15, 16, 17, 18, 19 (all v1.2 features must land first)

**Parallelizable with**: — (sequential, last phase)

**Requirements**: OPS-03, OPS-04, OPS-05

**Success Criteria** (what must be TRUE):

1. CI workflows run on Node.js 24 — `actions/checkout@v5+`, `actions/setup-python@v6+`, `actions/upload-artifact@v5+`; zero Node 20 deprecation warnings on a fresh PR run.
2. The `fr/CHANGELOG.md` decision is final and visible in the repo: either the file exists (synthesized from the English CHANGELOG, not double-maintained) or every aspirational reference to it is removed from headers / READMEs.
3. Version bumped to 1.2.0 in `pyproject.toml` and `ketu/__init__.py`; `importlib.metadata.version("ketu") == ketu.__version__ == "1.2.0"`.
4. CHANGELOG `[1.2.0] - YYYY-MM-DD` entry summarizes additive APIs (CHART, SYN, COMP, RET, PARTS, three new house systems, doc gates, workflow refresh) with no BREAKING heading; UPGRADING.md migration recipes are additive-only.
5. `ketu==1.2.0` published on PyPI via OIDC trusted publishing; GitHub release v1.2.0 attaches sdist + wheel; fresh-venv `pip install ketu==1.2.0` smoke-imports cleanly.

**Plans**: TBD

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
| 18. Solar + Lunar Returns (Std + Reloc)| v1.2      | 0/?            | Not started   | —          |
| 19. Arabic Parts Framework + 8 Parts   | v1.2      | 0/?            | Not started   | —          |
| 20. Release Preparation v1.2.0         | v1.2      | 0/?            | Not started   | —          |

---

*v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`*
*v1.1 phase details archived to `.planning/milestones/v1.1-ROADMAP.md`*
*Roadmap last updated: 2026-05-24 — Phase 17 complete (4/4 plans, COMP-01..04 satisfied, 1177 tests, `calculate_composite` + `circular_midpoint` + inline Porphyry trisection, coverage 100% sur `ketu/composite/`). Astro.com manual cross-check on 3 oracle fixtures deferred to pre-Phase-20 follow-up (anti-bot constraint, per synastry Plan 16-05 precedent). Phase 18 scope extended same day to bundle Solar + Lunar Returns behind a shared `_solve_return` helper (LRET-01..05 added; root-finder factorisation locked in success criteria #3).*
