---
phase: 18-solar-lunar-returns
plan: 05
subsystem: ketu.returns
tags: [returns, solar-return, lunar-return, close-out, coverage-gate, changelog, requirements]
dependency_graph:
  requires: ["18-01", "18-02", "18-03", "18-04"]
  provides: ["RET-06 coverage gate verified", "cross-module See Also graph closed", "CHANGELOG additive surface", "Phase 18 closure"]
  affects: ["ketu.charts", "ketu.composite", "ketu.synastry", "ketu.returns"]
tech_stack:
  added: []
  patterns: ["two-step coverage gate", "importable-Python-path See Also", "additive-only CHANGELOG", "self-consistency oracle PRIMARY + TEST-ONLY pyswisseph cross-check"]
key_files:
  created:
    - tests/returns/test_returns_coverage_paths.py
    - .planning/phases/18-solar-lunar-returns/18-05-SUMMARY.md
  modified:
    - ketu/charts/__init__.py
    - ketu/composite/__init__.py
    - ketu/synastry/__init__.py
    - CHANGELOG.md
    - .planning/REQUIREMENTS.md
decisions:
  - "5 coverage-gap branches (_solve.py 231/238, lunar.py 250-252/265) closed via 1 new test file (real degenerate-tolerance calls for the helper floors; monkeypatched _solve_return for the physically-unreachable lunar cycle-search branches). ketu/returns/ 94% -> 100%."
  - "pyswisseph cross-check framed in CHANGELOG as TEST-ONLY external validation; self-consistency oracle at 0.0001 deg is the PRIMARY gate. No runtime dependency added; ketu/ stays pure NumPy."
  - "RET-06 added as Plan 18-05 close-out convention addition (mirror of COMP-05/SYN-05/CHART-05/HOU-09); not in original RET-01..05 spec."
metrics:
  duration: "~54m"
  tasks: 3
  files: 6
  tests_added: 5
  completed: 2026-05-28
---

# Phase 18 Plan 05: Solar + Lunar Returns Close-Out Summary

**Completed:** 2026-05-28
**Plans executed:** 18-01 (foundation + `_solve_return` helper + wrap-around suite + `returns_coverage_gate` marker + `make returns-coverage` target), 18-02 (`solar_return`), 18-03 (`lunar_return`), 18-04 (6 oracle fixtures + TEST-ONLY pyswisseph cross-check + Astro-Seek probe + Astro.com deferred), 18-05 (close-out — this plan)

One-liner: Phase 18 close-out — ratcheted the `make returns-coverage` gate to 100% on `ketu/returns/`, closed the four-way cross-module See Also graph (charts ↔ composite ↔ synastry ↔ returns), advertised the additive `ketu.returns` surface in CHANGELOG, flipped 11 requirement entries to Done, and proved all 6 ROADMAP Phase 18 success criteria end-to-end.

## Files Modified (Close-Out)

- `tests/returns/test_returns_coverage_paths.py` (NEW, 5 tests) — closes the `_solve.py` + `lunar.py` error/edge branches to satisfy the ≥95% gate.
- `ketu/charts/__init__.py` — back-reference See Also to `ketu.returns.solar_return` + `ketu.returns.lunar_return`.
- `ketu/composite/__init__.py` — back-reference See Also to `ketu.returns.solar_return` + `ketu.returns.lunar_return`.
- `ketu/synastry/__init__.py` — back-reference See Also to `ketu.returns.solar_return` + `ketu.returns.lunar_return`.
- `CHANGELOG.md` — `## [Unreleased] ### Added` extended with 10 returns bullets (additive only).
- `.planning/REQUIREMENTS.md` — RET-01..05 + LRET-01..05 statuses → Done; new RET-06 entry + status row.

## Coverage Gate Result

`make returns-coverage`: **PASS** — `ketu/returns/` at **100%** (gate ≥95%; exit 0).

Coverage by file (after adding `test_returns_coverage_paths.py`):

```
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
ketu/returns/__init__.py       4      0   100%
ketu/returns/_solve.py        29      0   100%
ketu/returns/lunar.py         32      0   100%
ketu/returns/solar.py         17      0   100%
--------------------------------------------------------
TOTAL                         82      0   100%
```

Before the new test file the gate failed at 94% (5 lines missing: `_solve.py` 231 `tol_days` floor + 238 `max_iter` runaway guard; `lunar.py` 250-252 cycle-fallback `except ValueError: continue` + 265 no-return `ValueError`). These are defense-in-depth branches that the surface/oracle suites never reach with real monotonic Sun/Moon ephemerides, so they were pinned with degenerate-tolerance real calls (helper floors) and monkeypatched `_solve_return` (lunar cycle-search control flow).

## Cross-Module See Also Graph

Bidirectional discoverability complete (all entries use importable Python paths per the Phase 13 BLOCKER lesson — numpydoc's See Also parser crashes on slash-style file paths):

| From | To |
|------|-----|
| `ketu.returns` (module + `solar_return` + `lunar_return`) | `ketu.charts.compute_chart`, `ketu.composite.calculate_composite`, `ketu.synastry.calculate_synastry`, `ketu.returns._solve._solve_return` |
| `ketu.charts` | `ketu.returns.solar_return`, `ketu.returns.lunar_return` |
| `ketu.composite` | `ketu.returns.solar_return`, `ketu.returns.lunar_return` |
| `ketu.synastry` | `ketu.returns.solar_return`, `ketu.returns.lunar_return` |

`python -m numpydoc lint ketu/returns/__init__.py ketu/returns/solar.py ketu/returns/lunar.py ketu/returns/_solve.py ketu/charts/__init__.py ketu/composite/__init__.py ketu/synastry/__init__.py` — clean (exit 0).

## CHANGELOG Bullets Added

10 additive bullets under `## [Unreleased] ### Added` citing RET-01..06 + LRET-01..05 (16 requirement citations total across the block). No `Changed` / `Deprecated` / `Removed` sections touched (the `[Unreleased]` `### Changed` block remains the single pre-existing HOUSES_DTYPE entry — v1.2 non-breaking minor strict). The pyswisseph cross-check is framed as a TEST-ONLY optional dependency; the self-consistency oracle at `tolerance_deg=0.0001` is the PRIMARY gate. **No runtime dependency added; `ketu/` stays pure NumPy.**

## REQUIREMENTS Status Flips

| Req | Phase | Before | After |
|-----|-------|--------|-------|
| RET-01 | Phase 18 | Pending | Done |
| RET-02 | Phase 18 | Pending | Done |
| RET-03 | Phase 18 | Pending | Done |
| RET-04 | Phase 18 | Pending | Done |
| RET-05 | Phase 18 | Pending | Done |
| LRET-01 | Phase 18 | Pending | Done |
| LRET-02 | Phase 18 | Pending | Done |
| LRET-03 | Phase 18 | Pending | Done |
| LRET-04 | Phase 18 | Pending | Done |
| LRET-05 | Phase 18 | Pending | Done |
| RET-06 (NEW) | Phase 18 | — | Done |

Both the bulleted checkbox list (11 `[x]`) and the status table (11 `Done` rows) are consistent.

## 6 ROADMAP Success Criteria Smoke Output

```
########## SC#1 ##########
SC#1 std dtype: True
SC#1 std lat == natal_lat (48.85)? True
SC#1 rel lat == return_lat (40.71)? True
SC#1 std and rel have same jd (resolution is location-independent)? True
SC#1 SOLAR API + RELOCATION CONTRACT PASS

########## SC#2 ##########
SC#2 dtype: True
SC#2 jd_return >= target_jd: True
SC#2 jd_return - target_jd: 8.4607 d (< 27.5 d for first return)
SC#2 LUNAR API + FIRST-RETURN CONTRACT + API ASYMMETRY DOCUMENTED PASS

########## SC#3 ##########
SC#3 SHARED _solve_return FACTORISATION PASS -- no inline bisection in solar.py or lunar.py

########## SC#4 ##########
SC#4 Sun residual: 1.15e-04 deg (must be < 1/3600 = 2.78e-04 deg)
SC#4 Moon residual: 2.68e-04 deg (must be < 1/3600 = 2.78e-04 deg)
SC#4 ARC-SECOND CONVERGENCE PASS (both Sun and Moon)

########## SC#5 ##########
tests/returns/test_returns_oracle.py::test_self_consistency[oracle_solar_aries_seam_1970] PASSED
tests/returns/test_returns_oracle.py::test_self_consistency[oracle_solar_curie_1900] PASSED
tests/returns/test_returns_oracle.py::test_self_consistency[oracle_solar_diana_1980] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_lunar_curie_day_after] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_lunar_diana_2000] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_lunar_pisces_seam_1990] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_solar_aries_seam_1970] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_solar_curie_1900] PASSED
tests/returns/test_returns_oracle.py::test_pyswisseph_cross_check[oracle_solar_diana_1980] PASSED
tests/returns/test_returns_oracle.py::test_day_after_target_calendar_pin PASSED
tests/returns/test_returns_oracle.py::test_wrap_around_natal_near_seam[oracle_solar_aries_seam_1970.json] PASSED
tests/returns/test_returns_oracle.py::test_wrap_around_natal_near_seam[oracle_lunar_pisces_seam_1990.json] PASSED
======================== 15 passed, 6 warnings in 0.28s ========================

########## SC#6 ##########
SC#6 solar_return: LOUD distinction documented PASS
SC#6 lunar_return: LOUD distinction documented PASS
```

Verdict per criterion:
- **SC#1** (RET-01): `solar_return` returns CHART_DTYPE; standard vs relocated honoured; resolved JD location-independent. PASS.
- **SC#2** (LRET-01 + LRET-05): `lunar_return` returns CHART_DTYPE; FIRST return ≥ `target_jd` (8.46 d past target, < one period); API asymmetry documented. PASS.
- **SC#3**: shared `_solve_return` factorisation — neither `solar.py` nor `lunar.py` has an inline bisection loop. PASS.
- **SC#4** (RET-03 + LRET-03): arc-second convergence — Sun residual 1.15e-04 deg, Moon residual 2.68e-04 deg, both < 1″ = 2.78e-04 deg. PASS.
- **SC#5** (RET-04 + LRET-04): 6 oracle fixtures pass self-consistency + TEST-ONLY pyswisseph cross-check, plus day-after-target calendar pin and 2 wrap-around seam pins (15 oracle tests). PASS.
- **SC#6** (RET-05 + LRET-05): LOUD `natal_lat/lon` vs `return_lat/lon` distinction in both docstrings. PASS.

## Astro.com Manual Cross-Check — DEFERRED

Per 18-RESEARCH.md §"Astro.com Oracle Strategy" and the Phase 16-05 +
Phase 17-04 precedents, the Astro.com manual cross-check is deferred:
Astro.com is bot-blocked from automated retrieval (re-confirmed
during this research session — same constraint hit by Phases 16 and
17). Astro.com's free solar/lunar return calculator computes the
return moment to sub-second precision and reports the resolved JD in
UTC; manual capture is straightforward but cannot be automated in CI.

**Secondary reference (per Astro-Seek probe above):** Astro-Seek's
solar return calculator at
https://horoscopes.astro-seek.com/solar-return-chart **is accessible**
(no bot-block) and uses Swiss Ephemeris under the hood — equivalent
accuracy to Astro.com for cross-check purposes. A developer may use
either Astro.com (authoritative) or Astro-Seek (browser-accessible,
faster for batch entry) for the manual cross-check.

A developer should manually generate the 6 returns on Astro.com (or
Astro-Seek), record the resolved JDs, and update each fixture's
`cross_check_astro_com` block:

- `performed: true`
- `date_performed: YYYY-MM-DD`
- `delta_max_arcsec: <observed max delta on resolved JD>`
- `astro_com_settings: "Extended chart selection → method → 'Solar Return' (default)"`
- `notes: "Sun longitude in return chart differs by ~20 arcsec (Astro.com uses APPARENT, Ketu uses TRUE); resolved JD agrees to <1 sec"`

**Expected systematic offsets** (18-RESEARCH Pitfall 4):

- Sun longitude in return chart: ~20 arcsec (aberration convention difference; CANCELS in resolved JD).
- Moon longitude in return chart: sub-arcsec (Moon aberration is negligible).
- Resolved JD: sub-second agreement (same-convention-both-sides math).

**Estimated time:** 30–45 min for 6 fixtures (one-time; not a Phase 18
blocker — pyswisseph cross-check at the per-body `cross_check_tolerance_deg`
is the CI-runnable substitute, strictly stronger than Phase 17
which had only Astro.com deferred).

**Recommended developer workflow:**

1. Open https://horoscopes.astro-seek.com/solar-return-chart in a browser.
2. For each fixture (`tests/returns/fixtures/oracle_*.json`):
   - Enter natal date / time / place from the fixture's `natal` block.
   - Enter `target_year` (solar) or compute the calendar date of `target_jd` (lunar).
   - Submit; capture the resolved date/time UTC from the result page.
   - Convert to JD (e.g., via `ketu.ephemeris.time.utc_to_julian`).
   - Compute `delta_arcsec = abs(astro_seek_jd - fixture_jd) * body_speed_deg_per_day * 3600`.
3. Update `cross_check_astro_com.performed=true` + `delta_max_arcsec` + `date_performed`.
4. Record the observed delta. NOTE the expected disagreement bands: Astro.com
   uses Swiss Ephemeris's full Moshier/SE theory, which Ketu's analytic
   ephemeris diverges from by up to ~0.016 deg (Sun) and ~0.6 deg (Moon) —
   the SAME ephemeris-theory gap the pyswisseph cross-check measures (see
   18-04-NOTES.md "pyswisseph convention alignment + cross-check tolerance").
   The manual Astro.com cross-check is informational only; the CI gate is the
   pyswisseph cross-check at the per-body `cross_check_tolerance_deg`
   (solar 0.01 deg, lunar 0.75 deg) plus the self-consistency oracle at
   0.0001 deg.

## Test Counts

- New tests in this plan: 5 (`tests/returns/test_returns_coverage_paths.py`).
- Returns subpackage suite total: 76 PASS (`make returns-coverage`).
  - `test_solve_return.py`: 16 (helper-level wrap-around + convergence + bracket rejection + NaN/vectorisation)
  - `test_solar_return.py`: 16 (RET-01..03 + RET-05 surface)
  - `test_lunar_return.py`: 23 (LRET-01..03 + LRET-05 surface incl. first-return + day-after)
  - `test_returns_oracle.py`: 15 (6 self-consistency at 0.0001 deg + 6 pyswisseph cross-check + 1 day-after calendar pin + 2 wrap-around seam pins)
  - `test_returns_coverage_gate.py`: 1 (marker sentinel)
  - `test_returns_coverage_paths.py`: 5 (NEW — error/edge branch coverage)
- Project total: **1253 passed + 2 skipped** (was 1248 + 2 before this plan; +5).

## Doc-Gate Status

- `python -m numpydoc lint` on `ketu/returns/` + the three back-referencing `__init__.py`: clean (exit 0).
- `python -m interrogate ketu/`: 100% (258/258, minimum 95%).

## Deviations from Plan

**1. [Rule 1 - Blocking issue] Coverage gate was at 94% (below the ≥95% binding floor) at plan start.**
- **Found during:** Task 1 Step A (`make returns-coverage` exited 2).
- **Issue:** 5 defense-in-depth branches uncovered by the surface/oracle suites (`_solve.py` 231/238, `lunar.py` 250-252/265). Plan 18-03 SUMMARY had predicted Plan 18-04 oracle fixtures would push coverage > 95%, but the day-after/inclusive-boundary fixtures did not exercise the lunar cycle-fallback `except` / no-return `ValueError` (physically unreachable with a real monotonic Moon) nor the `_solve.py` tolerance floors (the residual threshold always fires first in practice).
- **Fix:** Added `tests/returns/test_returns_coverage_paths.py` (5 tests) per the plan's Step A guidance — degenerate-tolerance real calls for the `_solve.py` floors, monkeypatched `_solve_return` for the lunar control-flow branches. Coverage 94% → 100%.
- **Files modified:** `tests/returns/test_returns_coverage_paths.py` (new).
- **Commit:** `347022c`.

No other deviations — Tasks 1 (Steps B-E), 2, and 3 executed exactly as written. The `solar.py` See Also references `compute_chart` + `_solve_return` (no `lunar_return` back-ref, as it was authored in 18-02 before `lunar.py` existed); this matches the plan's "should reference" wording and is numpydoc-lint-clean, so it was left as-is.

## Note on Advisory Hooks

- A `git commit` pre-commit hook surfaced an **advisory** planning-drift warning about Phase 16 (SYN-01..05 still `Pending` in REQUIREMENTS vs a VERIFICATION.md). This is UNRELATED to Phase 18 and the warning is advisory ("commit will proceed"); not acted upon per the close-out scope.
- IDE markdownlint warnings (MD024 duplicate `### Added`/`### Changed` headings, MD050 strong-style, MD060 table alignment) on `CHANGELOG.md` / `.planning/REQUIREMENTS.md` are pre-existing cosmetic issues consistent with surrounding content; they are not part of the project's code doc gates (numpydoc + interrogate) and were not introduced by this plan.

## Phase 18 Closure

**Ready for `/gsd:verify-phase 18`.** Phase 18 is ready for /gsd:verify-phase 18.

All 6 ROADMAP success criteria satisfied end-to-end; 11 requirement entries Done (RET-01..06 + LRET-01..05); coverage gate 100% on `ketu/returns/` (≥95% floor); cross-module discoverability complete (charts ↔ composite ↔ synastry ↔ returns, importable paths only); CHANGELOG additive surface advertised; Astro.com manual cross-check captured as deferred follow-up with the TEST-ONLY pyswisseph CI substitute strictly stronger than the Phase 17 precedent. No runtime dependency added — `ketu/` remains pure NumPy.

Pour `/gsd:verify-phase 18` : la couverture pyswisseph cross-check est CI-runnable et donne la validation cross-tool que les Phases 16 et 17 n'avaient pas. Elle reste strictement TEST-ONLY (`[project.optional-dependencies].test`) — aucune dépendance runtime ajoutée, contrat pur-NumPy préservé. La cross-check Astro.com manuelle reste un follow-up développeur de 30-45 min sans bloquer la clôture de la phase.

## Self-Check: PASSED

All created/modified files verified on disk; all 4 per-task commits verified in git history:
- `347022c` test(18-05): close ketu.returns coverage gaps
- `74c37a9` docs(18-05): complete See Also cross-references
- `64d5daf` docs(18-05): CHANGELOG + REQUIREMENTS RET-01..06 + LRET-01..05 Done
- `3c9990a` docs(18-05): Phase 18 close-out (6-criteria smoke + Astro.com deferred + SUMMARY)
