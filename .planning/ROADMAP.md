# Roadmap: Ketu v1.1 Flexibility & Houses

## Overview

Ketu v1.1 evolves the library from a pure astronomical engine into an astronomical-astrological framework. Building on the stable v1.0 foundation (250 tests, 91% coverage, PyPI-published), this milestone delivers three orthogonal capabilities: a verified Lilith calculation, configurable aspect sets (5 majors by default with opt-in harmonics), and an extensible houses module starting with Placidus and Koch. Five phases (8 through 12) ship the work, with phases 8/9/10 fully parallelizable, phase 11 integrating CLI on top of phases 9+10, and phase 12 closing with a v1.1.0 PyPI release.

## Milestones

- ✅ **v1.0 Production Stability** — Phases 1-7 (shipped 2026-02-12, archived to `.planning/milestones/v1.0-ROADMAP.md`)
- 🚧 **v1.1 Flexibility & Houses** — Phases 8-12 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (8, 9, 10, 11, 12): Planned milestone work
- Decimal phases (e.g. 9.1): Reserved for urgent insertions (none yet)

**Execution Order & Parallelization:**
- Phases 8, 9, 10 are mutually independent (disjoint modules) — can execute in parallel
- Phase 11 hard-blocks on Phases 9 AND 10 (CLI surfaces the new aspect + houses APIs)
- Phase 12 is last (depends on all prior phases)

- [x] **Phase 8: Lilith Verification & Fix** — Document Lilith definition, audit formula vs Swiss Ephemeris, fix if needed (completed 2026-05-06)
- [x] **Phase 9: Configurable Aspects** — 5-major default with `CLASSICAL`/`TRADITIONAL`/`EXTENDED` presets; append-only `core.aspects` (completed 2026-05-07)
- [ ] **Phase 10: Houses Module** — Placidus + Koch with extensible registry, polar fallback, LST precision audit
- [ ] **Phase 11: CLI Refactor & Integration** — argparse subcommands, `--harmonics SPEC`, `ketu houses` subcommand, introspection flags
- [ ] **Phase 12: Release Preparation v1.1.0** — Version bump, CHANGELOG, UPGRADING.md, GitHub release, PyPI publish

## Cross-Cutting Constraints

These apply to every phase below (not just one) and originate from research/SUMMARY.md:

- `core.aspects` array remains length 14 and append-only (Kala uses positional indexing)
- No new runtime dependencies — pure NumPy contract preserved (`pysweph` is test-only, AGPL-safe)
- All new code must pass mypy strict, numpydoc-style docstrings, interrogate ≥95%
- All new calculations vectorized over date arrays (no Python loops in hot paths)
- DateTime inputs always UTC
- Cache keys include configuration hashes (aspect set, house system) — no stale results after config change
- Coverage gate: ≥90% project, ≥85% per module, target 95% on new modules

## Phase Details

### Phase 8: Lilith Verification & Fix

**Goal**: Lilith longitude is provably correct against Swiss Ephemeris over 1900-2050, with the formula's definition documented before any code change.

**Depends on**: Nothing (parallelizable with Phases 9 and 10)

**Parallelizable with**: Phase 9, Phase 10

**Requirements**: LIL-01, LIL-02, LIL-03, LIL-04, LIL-05

**Success Criteria** (what must be TRUE):
  1. `LILITH_DEFINITION.md` exists and documents Mean Apogee, tropical longitude convention, and Chapront-Touz/Francou source citation BEFORE any formula code changes
  2. User runs the test harness and sees `pysweph SE_MEAN_APOG` cross-check pass on 5+ dates spanning 1900, 1950, 2000, 2025, 2050 within an explicit tolerance documented in the test
  3. If empirical error >0.01°, user sees the corrected formula land with regression tests pinning new values; if error ≤0.01°, definition document closes the loop without code change
  4. User installs `ketu[test]` and `pysweph>=2.10.3.6` is present as a test-only dependency (NOT pulled into the runtime wheel)
  5. CHANGELOG and UPGRADING.md document any Lilith value changes with explicit magnitude (e.g. "Lilith differs by X° vs v1.0 on 2025-01-01")

**Plans:** 5 plans (4 if Plan 03 harness passes — Plan 04 is conditional)

Plans:

- [ ] 08-01-lilith-definition-PLAN.md — Write `docs/LILITH_DEFINITION.md` (formula, frame, Chapront citation, tolerance derivation, history placeholder) BEFORE any code is touched (LIL-01)
- [ ] 08-02-test-only-dependency-PLAN.md — Add `pysweph>=2.10.3.6` to `[project.optional-dependencies].test`; verify two-venv runtime isolation (AGPL non-contamination) (LIL-04)
- [ ] 08-03-cross-check-harness-PLAN.md — `tests/test_lilith_cross_check.py` parametrized over 5 dates spanning 1900-2050; record empirical max |delta|; gate Plan 04 branch (LIL-02)
- [ ] 08-04-conditional-formula-fix-PLAN.md — Branched: NO-OP if max|delta| ≤ 0.01° / FORMULA-CORRECTION updates all THREE plumbing sites (orbital.py:591/146, planets.py:153/458) + regression baselines (LIL-03)
- [ ] 08-05-release-notes-PLAN.md — Update CHANGELOG.md and UPGRADING.md with explicit magnitude (zero allowed) and per-date table on FORMULA-CORRECTION branch (LIL-05)

### Phase 9: Configurable Aspects

**Goal**: User can select an aspect set (5 majors default, 7 traditional, 14 extended) via Python API or named preset, with `core.aspects` remaining length-14 append-only and Kala's positional indexing preserved.

**Depends on**: Nothing (parallelizable with Phases 8 and 10)

**Parallelizable with**: Phase 8, Phase 10

**Requirements**: ASP-01, ASP-02, ASP-03, ASP-04, ASP-05, ASP-06, ASP-07, ASP-08

**Success Criteria** (what must be TRUE):
  1. User imports `core.aspects` and sees length 14 with the same row order as v1.0; an invariant test fails on any reorder, deletion, or shape change
  2. User imports `from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED` and the three constants resolve to 5, 7, and 14 aspects respectively
  3. User calls `calculate_aspects(...)` (and `_vectorized`, `_batch` variants) with `aspects=CLASSICAL` and the result contains zero non-classical aspects (integration test)
  4. User calls any aspect API with `aspects=None` and gets `CLASSICAL` (5 majors) — the default change is explicit and observable; downstream consumers like Kala must opt into `EXTENDED`
  5. User runs `pytest -k benchmark` and `calculate_aspects_batch()` shows ≤5% regression vs the v1.0 baseline (filter mask resolved once at API entry, not in hot loops); LRU caches include `aspect_set` hash so config changes never return stale results

**Plans**: 6 plans (Plan 09-04 split into 09-04a + 09-04b per checker Blocker 3)

Plans:

- [x] 09-01-baseline-capture-PLAN.md — Capture v1.0 timing baseline for `calculate_aspects_batch()` (BEFORE any code change) into `baseline-v1.0.json`; benchmark script ships with `--aspect-set` flag (default extended) wired from day 1; ASP-08 reference point
- [x] 09-02-presets-module-PLAN.md — Create `ketu/aspects/presets.py` with `CLASSICAL`/`TRADITIONAL`/`EXTENDED` frozen masks + `resolve_aspect_set` resolver; re-export from subpackage `__init__` (ASP-02, ASP-04, ASP-05, ASP-06)
- [x] 09-03-invariant-test-PLAN.md — Strengthen `tests/test_ketu.py` invariant: length 14, dtype.names, per-row name/angle/coef, sha256 byte fingerprint (ASP-01)
- [x] 09-04a-calculator-refactor-PLAN.md — Thread `aspects=` through `calculate_aspects/_vectorized/_batch` AND `find_aspects_between_dates`; refactor hot loops to emit canonical `i_asp` from `selected_indices[k]`; rename module-level `aspects` import to `_CORE_ASPECTS` (ASP-03, ASP-04, ASP-05, ASP-07 calculator-side)
- [x] 09-04b-default-migration-PLAN.md — Migrate 4 hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` lists in `windows.py`/`timelines.py`/`transits.py` to derive from `CLASSICAL` preset; parallel with 09-04a in Wave 2 (ASP-04, ASP-07 windows/timelines/transits-side)
- [x] 09-05-integration-and-benchmark-PLAN.md — Integration test (CLASSICAL leak = zero across all 4 public aspect APIs incl. `find_aspects_between_dates`) + benchmark comparison vs `baseline-v1.0.json` with HARD PASS/FAIL ≤5% gate (ASP-07, ASP-08)

### Phase 10: Houses Module

**Goal**: User can compute Placidus or Koch house cusps over batched `(jd, lat, lon)` inputs with polar safety, returning a structured `HOUSES_DTYPE` array and a `house_of(planet_lon, cusps)` helper.

**Depends on**: Nothing (parallelizable with Phases 8 and 9)

**Parallelizable with**: Phase 8, Phase 9

**Requirements**: HOU-01, HOU-02, HOU-03, HOU-04, HOU-05, HOU-06, HOU-07, HOU-08, HOU-09, HOU-10

**Success Criteria** (what must be TRUE):
  1. User calls `calculate_houses(jd, lat, lon, system="placidus")` (or `"koch"`) and receives a `HOUSES_DTYPE` structured array with 12 cusps + ASC + MC + ARMC + Vertex; vectorized inputs return arrays with leading shape preserved
  2. User computes a chart at any latitude in (-66.56°, +66.56°) and the Ascendant matches Astro.com / Swiss Ephemeris within <1 arcmin (LST/obliquity precision audit completed BEFORE algorithm implementation, per HOU-01)
  3. User passes lat ≥ 66.56° (e.g. 70°, 80°) and either receives `HighLatitudeError` (default) or, with `polar_fallback="porphyry"`, gets a Porphyry-derived cusp set — never silent NaN
  4. User adds a new house system by registering it in `houses/registry.py` (`SYSTEMS = {"placidus": ..., "koch": ..., "myhouse": ...}`) without touching dispatch code; the broken `calculate_house_cusps` stub in `ephemeris/planets.py` is gone
  5. User runs `pytest tests/houses/` and sees ≥95% module coverage with ≥10 reference fixtures vs Astro.com/Swiss Ephemeris (including polar latitudes 70°/80° and Placidus iteration cap at 50 with explicit non-convergence handling); `house_of(planet_lon, cusps)` returns a 1-12 integer for any longitude

**Plans**: 6 plans (4 waves — Plan 01 unblocks all; Plans 02+03 parallel; Plans 04+05 parallel; Plan 06 closes)

Plans:

- [ ] 10-01-lst-precision-audit-PLAN.md — Audit GMST/obliquity precision vs swisseph; tighten sidereal_time to IAU 2006 if needed; close state.md HOU-01 blocker (HOU-01)
- [ ] 10-02-oracle-harness-and-fixtures-PLAN.md — Build tests/houses/conftest.py with swe_oracle helpers + ≥10 reference charts (incl. polar 70°/80°) snapshotted to fixtures/reference_charts.json (HOU-09 partial)
- [ ] 10-03-registry-dtype-ascmc-PLAN.md — Create ketu/houses/ subpackage scaffold: HOUSES_DTYPE, HighLatitudeError, SYSTEMS registry pattern, vectorized closed-form ASC/MC/ARMC/Vertex (HOU-02, HOU-05)
- [ ] 10-04-placidus-implementation-PLAN.md — Vectorized Placidus with mask-based iteration, MAX_ITER=50, NaN propagation at polar; oracle agreement <1 arcmin on 8 charts × 12 cusps (HOU-03, HOU-08)
- [ ] 10-05-koch-porphyry-polar-PLAN.md — Koch (oblique-ascension trisection) + Porphyry (closed-form polar fallback) + is_polar/polar_circle helpers using time-varying 90°-ε(jd) (HOU-04, HOU-06)
- [ ] 10-06-integration-stub-removal-PLAN.md — Real calculate_houses (SYSTEMS dispatch + polar_fallback) + house_of vectorized + REMOVE calculate_house_cusps stub from ephemeris/planets.py + ≥95% coverage gate (HOU-07, HOU-10)

### Phase 11: CLI Refactor & Integration

**Goal**: User invokes `ketu` via argparse subcommands, opts into harmonics through `--harmonics SPEC`, computes houses through `ketu houses ...`, and sees the resolved configuration echoed in output — backward compat preserved via `--harmonics all`.

**Depends on**: Phase 9 AND Phase 10 (needs both new APIs to surface them)

**Parallelizable with**: — (sequential after 9+10)

**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06

**Success Criteria** (what must be TRUE):
  1. User runs `ketu --help` and sees argparse subcommands (no interactive `input()` prompt anywhere); each subcommand has its own `--help`
  2. User runs `ketu --harmonics classical` (or `traditional`, `extended`, `all`, or explicit list `9,10,11`) and the aspect output matches the requested set; bare integer `--harmonics 12` is rejected with a clear error pointing to named presets
  3. User runs `ketu --harmonics all ...` against a v1.0-captured reference output and the result is byte-identical (legacy escape hatch regression-tested in CI)
  4. User runs `ketu houses --date 2026-05-06T12:00:00Z --lat 48.85 --lon 2.35 --system placidus` and receives the same house cusps the Python API returns for the same inputs
  5. User runs `ketu --list-aspect-sets` and `ketu --list-house-systems` and sees the available options with descriptions; every CLI invocation echoes a resolved-config header (e.g. `# Aspect set: classical [0°, 60°, 90°, 120°, 180°]` and the chosen house system if applicable)

**Plans**: TBD

### Phase 12: Release Preparation v1.1.0

**Goal**: Ketu 1.1.0 is published to PyPI with a GitHub release, breaking-behavior changes documented, and a working migration guide for v1.0 users.

**Depends on**: Phase 8, Phase 9, Phase 10, Phase 11

**Parallelizable with**: — (sequential, last phase)

**Requirements**: REL-01, REL-02, REL-03, REL-04

**Success Criteria** (what must be TRUE):
  1. User checks `pyproject.toml` and `ketu/__init__.py` and sees version `1.1.0`; the version sync test passes in CI
  2. User reads CHANGELOG.md and finds a "BREAKING / Numerical Behavior Changes" section listing: CLI default change (5 majors), Lilith correction (with magnitude if any), new houses module
  3. User reads UPGRADING.md v1.0 → v1.1 section and finds explicit migration recipes for script users (CLI), Kala adapter (request `EXTENDED` for legacy 14), and any Lilith consumers
  4. User runs `pip install ketu==1.1.0` from PyPI in a fresh venv and the test suite passes (250+ tests, mypy strict, numpydoc, interrogate ≥95%); the GitHub release v1.1.0 is published with notes pointing to CHANGELOG and UPGRADING

**Plans**: TBD

## Coverage Validation

**v1.1 requirements: 33 total — all mapped, no orphans**

| Requirement | Phase |
|-------------|-------|
| LIL-01, LIL-02, LIL-03, LIL-04, LIL-05 | Phase 8 |
| ASP-01, ASP-02, ASP-03, ASP-04, ASP-05, ASP-06, ASP-07, ASP-08 | Phase 9 |
| HOU-01, HOU-02, HOU-03, HOU-04, HOU-05, HOU-06, HOU-07, HOU-08, HOU-09, HOU-10 | Phase 10 |
| CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06 | Phase 11 |
| REL-01, REL-02, REL-03, REL-04 | Phase 12 |

**Coverage:** 33/33 requirements mapped ✓ (no orphans, no duplicates)

## Progress

**Execution Order:** 8 → (8, 9, 10 parallel) → 11 → 12

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-7 (collapsed) | v1.0 | 16/16 | ✓ Complete | 2026-02-12 |
| 8. Lilith Verification & Fix | v1.1 | 5/5 | ✓ Complete | 2026-05-06 |
| 9. Configurable Aspects | v1.1 | 6/6 | ✓ Complete | 2026-05-07 |
| 10. Houses Module | v1.1 | 0/6 | Plans created | - |
| 11. CLI Refactor & Integration | v1.1 | 0/TBD | Not started | - |
| 12. Release Preparation v1.1.0 | v1.1 | 0/TBD | Not started | - |

v1.0 phase details archived to `.planning/milestones/v1.0-ROADMAP.md`.

---
*Roadmap v1.1 created: 2026-05-06*
*Phase 8 plans created: 2026-05-06*
*Phase 8 executed: 2026-05-06 (FORMULA-CORRECTION branch — Lilith formula fixed at 4 sites, max |delta| 0.002693° vs Swiss Ephemeris)*
*Phase 9 executed: 2026-05-07 (6 plans, 3 waves — CLASSICAL default, presets module, ASP-08 PASS at -10.10% max regression on EXTENDED, 488 tests green)*
*v1.0 roadmap archived to .planning/milestones/v1.0-ROADMAP.md*
*Phase 10 plans created: 2026-05-07 (6 plans, 4 waves — Plan 01 unblocks all; Plans 02/03 parallel Wave 2; Plans 04/05 parallel Wave 3; Plan 06 closes Wave 4)*
