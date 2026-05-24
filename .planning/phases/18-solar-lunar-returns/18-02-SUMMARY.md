---
phase: 18-solar-lunar-returns
plan: 02
subsystem: returns
tags: [returns, solar-return, public-api, bisection, relocation, numpy, chart-dtype]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE + compute_chart(jd, lat, lon, system, polar_fallback) (consumed at assembly step 5)
  - phase: 15-additional-house-systems
    provides: whole_sign + equal + regiomontanus systems (pass-through via system= kwarg)
  - phase: 18-solar-lunar-returns/18-01
    provides: _solve_return + _signed_residual_deg + _TROPICAL_YEAR_D constant (consumed at root-finding step 3)
provides:
  - "ketu.returns.solar.solar_return public function (RET-01 signature verbatim; ~30 LOC algorithmic body + numpydoc docstring)"
  - "ketu.returns re-exports solar_return; __all__ extended to ['solar_return']"
  - "tests/returns/conftest.py with 6 session-scoped natal fixtures (Diana, Charles, Marie/Pierre Curie, Lennon, Ono) — canonical JDs/lat/lon mirroring synastry+composite fixtures for cross-package parity"
  - "tests/returns/test_solar_return.py with 16 RET-01..03+RET-05 surface tests across 7 classes (dtype, residual, relocation, natal-irrelevance ratchet, polar safety, Feb 29 natal, system pass-through, target_year type guard)"
affects: [18-03, 18-04, 18-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Public return-API: read natal body lon at signature boundary → seed JD from period constant → delegate to _solve_return → assemble via compute_chart with hard-wired polar_fallback='porphyry'"
    - "5-step solar_return body: type guard → read natal Sun lon → seed JD → bisect → relocation defaulting → compute_chart assembly"
    - "Session-scoped natal dict fixtures (jd/lat/lon triples) — distinct from synastry/composite's CHART_DTYPE-shaped fixtures because returns consume raw natal triples, not the natal CHART_DTYPE itself"

key-files:
  created:
    - ketu/returns/solar.py
    - tests/returns/conftest.py
    - tests/returns/test_solar_return.py
  modified:
    - ketu/returns/__init__.py

key-decisions:
  - "Plan 18-02: solar_return delegates Sun root-finding to _solve_return(body_id=0, natal_lon_ref=natal_sun_lon, t_seed=natal_jd + (target_year - natal_year) * _TROPICAL_YEAR_D, half_window_days=1.5) — NO inline bisection in solar.py (ROADMAP Phase 18 Success Criterion #3 binding, non-negotiable factorisation lock per LRET-02)."
  - "Plan 18-02: polar_fallback='porphyry' HARD-WIRED in the internal compute_chart call (no public kwarg) — extreme return_lat (Tromso 69.65 N) does NOT raise HighLatitudeError. RESEARCH Open Question Q5 lock honoured."
  - "Plan 18-02: target_year MUST be int or np.integer; runtime guard raises ValueError on float/str with helpful message ('Pass an int year (e.g., 2010), not a JD or a string'). Catches the common 'passed a JD instead of a year' footgun where 1980.5 would silently succeed otherwise."
  - "Plan 18-02: natal_lat/lon NEVER affects the resolved JD — Sun geocentric longitude is location-independent. Pinned at the test level by TestSolarReturnNatalLocationIrrelevance::test_natal_lat_does_not_affect_jd (different natal_lat values, identical resolved JD to within 1e-7 d)."
  - "Plan 18-02: Relocation contract (RET-05) — return_lat=None defaults to natal_lat; non-None override produces a relocated chart. Pinned at the test level by TestSolarReturnRelocation (both None-defaulting and NYC-relocation variants)."
  - "Plan 18-02: Session-scoped natal fixtures (dict-shaped jd/lat/lon triples) duplicated from synastry/composite oracle JSONs — 6 personas, identical UTC JDs (Diana 2437482.281250, Charles 2432870.384722, Marie Curie 2403277.941667, Pierre Curie 2400179.993750, Lennon 2429912.270833, Ono 2427121.979167). Cross-package parity preserved without cross-conftest pytest_plugins import."
  - "Plan 18-02: Feb 29 natal in non-leap target year resolves normally (TestSolarReturnFeb29Natal::test_feb_29_natal_non_leap_target) — the seed is a tropical-year offset (natal_jd + N * 365.24219), NOT calendar-anchored. The return falls in late Feb / early March of the target year; no calendar special-casing needed in code."
  - "Plan 18-02: system= validation deferred to compute_chart / calculate_houses (raises ValueError on unknown). No duplicate validation in solar_return — accept-and-pass-through. Pinned by TestSolarReturnSystemKwarg::test_unknown_system_raises with system='bogus_system'."

patterns-established:
  - "Public return-API skeleton (solar_return is the template Plan 18-03's lunar_return follows): scalar input → natal-body-lon read at signature boundary → seed from period constant → _solve_return delegation → relocation defaulting → compute_chart with polar_fallback='porphyry' hard-wired"
  - "Session-scoped dict fixtures (jd/lat/lon triples) for raw-natal API consumers — distinct shape from synastry/composite's CHART_DTYPE-shaped fixtures, but identical natal-data identity for cross-package consistency"

# Metrics
duration: ~14min
completed: 2026-05-24
---

# Phase 18 Plan 02: solar_return Public API Summary

**Solar return public API landed (RET-01..03 + RET-05) — `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system='placidus') -> CHART_DTYPE` resolves the Sun-return instant within 1 arc-second via the shared `_solve_return` helper (NO inline bisection in `solar.py`), assembles the chart at the resolved instant with `polar_fallback='porphyry'` hard-wired (Tromso-safe), and pins the relocation contract + natal-lat-irrelevance ratchet + Feb 29 leap-year edge case + system pass-through across 16 surface tests.**

## Performance

- **Duration:** ~14min (≈861 s)
- **Started:** 2026-05-24T15:10:43Z
- **Completed:** 2026-05-24T15:25:04Z
- **Tasks:** 2
- **Files modified:** 4 (3 created + 1 modified)

## Accomplishments

- `solar_return` public function implemented at `ketu/returns/solar.py` (199 LOC including ~135-line numpydoc docstring; algorithmic body ~30 LOC).
- Sun root-finding **delegates to `_solve_return(body_id=0, natal_lon_ref, t_seed, half_window_days=1.5)`** — ROADMAP Phase 18 Success Criterion #3 architecturally satisfied. Grep ratchet `grep -E "bisect|while|for.*range.*60" ketu/returns/solar.py` finds only docstring mentions of the delegated helper, no algorithmic bisection in this module.
- `compute_chart(jd_return, return_lat or natal_lat, return_lon or natal_lon, system=system, polar_fallback='porphyry')` assembles the output CHART_DTYPE — Tromso-safe by construction (Porphyry fallback engages silently if Placidus would have raised at extreme latitudes).
- `ketu/returns/__init__.py` extended: `from .solar import solar_return` + `__all__ = ['solar_return']`. The 5 LOUD module-level guard clauses from Plan 18-01 (API asymmetry, UTC-only, natal_lat/lon vs return_lat/lon, polar relocation safety, aberration cancellation) apply to `solar_return` verbatim and are now in-force.
- `tests/returns/conftest.py` created with 6 session-scoped natal fixtures (Diana, Charles, Marie Curie, Pierre Curie, John Lennon, Yoko Ono) using canonical JDs/lat/lon from `tests/synastry/fixtures/oracle_*.json` and `tests/composite/fixtures/oracle_*.json` — single source of truth for natal-data identity across the three pair-chart subpackages.
- `tests/returns/test_solar_return.py` created with **16 tests across 7 classes** pinning RET-01..03 + RET-05:
  - `TestSolarReturnDtype::test_returns_chart_dtype` — RET-01 dtype binding (scalar CHART_DTYPE).
  - `TestSolarReturnResidual::test_residual_under_one_arcsecond[1980/1990/2000/2010]` — RET-03 binding (residual < 1 arc-second across 4 parametrized target years).
  - `TestSolarReturnRelocation::test_return_lat_lon_none_defaults_to_natal` + `test_relocation_changes_houses_not_bodies` — RET-05 relocation contract (both None-defaulting and NYC-relocation variants).
  - `TestSolarReturnNatalLocationIrrelevance::test_natal_lat_does_not_affect_jd` — RET-05 ratchet (different `natal_lat` → identical resolved JD; pins the docstring claim that natal_lat is signature-symmetric only).
  - `TestSolarReturnPolarRelocation::test_tromso_relocation_does_not_raise` — polar safety (return_lat=69.65 with system='placidus' does NOT raise; Porphyry cusps non-NaN).
  - `TestSolarReturnFeb29Natal::test_feb_29_natal_non_leap_target` — leap-year edge case (1980-02-29 natal + target_year=2001 resolves to residual < 1 arc-second).
  - `TestSolarReturnSystemKwarg::test_default_placidus` + `test_whole_sign_pass_through` + `test_unknown_system_raises` — system pass-through (placidus default, whole_sign accepted, bogus raises).
  - `TestSolarReturnTargetYearTypeGuard::test_float_target_year_raises` + `test_string_target_year_raises` + `test_numpy_int_accepted` — type contract (float/str raise ValueError with `target_year must be an integer` message; np.int64 accepted).
- **Project suite green: 1210 PASS + 2 SKIPPED** (1194 baseline + 16 new); no regression.
- **`make returns-coverage` GREEN at 96%** (≥95% gate binding from Plan 18-01). Breakdown: `ketu/returns/__init__.py` 100%, `ketu/returns/_solve.py` 93% (lines 231+238 = `max_iter` exhaustion fallback + `tol_days` early-return, both exercised only at extreme edges), `ketu/returns/solar.py` 100%.
- Doc gates green: `numpydoc lint ketu/returns/solar.py` clean; `interrogate ketu/returns/solar.py` 100%.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement ketu/returns/solar.py with solar_return public API + extend __init__.py** — `514ecbf` (feat)
2. **Task 2: tests/returns/conftest.py with 6 session-scoped natal fixtures + tests/returns/test_solar_return.py RET-01..03+RET-05 surface tests** — `3537821` (test)

## Files Created/Modified

- `ketu/returns/solar.py` (created, 199 LOC) — `solar_return` public function. Reads natal Sun longitude via `calc_planet_position(natal_jd, 0)[0]`; seeds bisection at `natal_jd + (target_year - natal_year) * _TROPICAL_YEAR_D`; calls `_solve_return(0, natal_sun_lon, t_seed, 1.5)`; assembles output via `compute_chart(jd_return, return_lat or natal_lat, return_lon or natal_lon, system=system, polar_fallback='porphyry')`. Full numpydoc docstring with Parameters, Returns, Raises, Notes (5 sections — natal_lat/lon vs return_lat/lon, API asymmetry vs lunar_return, UTC-only contract, polar safety, aberration convention, Feb 29 leap-year edge), See Also, Examples sections.
- `ketu/returns/__init__.py` (modified) — added `from ketu.returns.solar import solar_return` import; extended `__all__ = ['solar_return']` (lunar_return appends in Plan 18-03). Module docstring unchanged (Plan 18-01's 5 guard clauses already cover both functions).
- `tests/returns/conftest.py` (created, 113 LOC) — 6 session-scoped natal fixtures returning `dict[str, float]` triples (`jd`, `lat`, `lon`). Canonical JDs verified via `utc_to_julian(datetime.fromisoformat(iso))`: Diana 2437482.281250, Charles 2432870.384722, Marie Curie 2403277.941667, Pierre Curie 2400179.993750 (1859-05-15T11:51 UT per synastry oracle), Lennon 2429912.270833, Ono 2427121.979167 (1933-02-18T11:30 UT = 20:30 JST per synastry oracle). Each fixture's docstring cites the source oracle fixture (Plan 16-03 / 17-03 lineage).
- `tests/returns/test_solar_return.py` (created, 308 LOC) — 16 tests across 7 test classes, full numpydoc-compliant docstrings on every method (Parameters section for fixture injection, summary line for behaviour pinned). All tests PASS on first execution.

## Decisions Made

See `key-decisions` in frontmatter. Eight locked decisions; all aligned with the plan's `must_haves` / `truths` block and the precedents from Plan 18-01 (delegation contract), Plans 17-03/16-03 (oracle fixture cross-package parity), Phase 14 (CHART_DTYPE consumer contract), and Phase 15 (system= passthrough). No new decisions outside the plan's locked scope.

## Deviations from Plan

**None — plan executed exactly as written.**

One micro-correction during fixture authoring (NOT a deviation, just a verification catch): the planner's illustrative example for Yoko Ono showed `jd: 2426980.979167` paired with `"1933-02-18 20:30 UT"`. The plan explicitly stated the executor MUST cross-reference `tests/composite/conftest.py` (and by extension the synastry oracle JSON) for canonical values. The synastry oracle records Ono's natal as `1933-02-18T11:30:00Z` (= 20:30 JST in pre-1948 Tokyo), giving `jd=2427121.979167`. The executor used the canonical synastry value as instructed (`utc_to_julian(datetime.fromisoformat('1933-02-18T11:30:00+00:00')) = 2427121.979167`). This is exactly the cross-reference behaviour the plan mandates ("the executor MUST verify against `tests/composite/conftest.py` and copy the canonical values to ensure cross-subpackage consistency"); not a deviation, just an instance of the planner's safety-net working as designed. Same logic applied to Pierre Curie's `11:51 UT` (synastry oracle) vs the illustrative `12:00 UT`; canonical value used (`jd=2400179.99375`).

---

**Total deviations:** 0. Plan executed exactly as written.

## Issues Encountered

None. All three verify commands in Task 1 + the pytest run in Task 2 + `make returns-coverage` all PASSED on the first attempt. No project regression. Coverage gate 96% (above 95% binding floor from Plan 18-01).

Recurring minor process issue (Phase 17 leftover, NOT in v1.2 scope): `venv/bin/pytest` shebang is broken; workaround `python -m pytest` after `source venv/bin/activate` (consistent across Plans 17-01..04 and 18-01..02).

A benign `RuntimeWarning: invalid value encountered in divide` from `ketu/ephemeris/orbital.py:733` (line `lat = np.rad2deg(np.arcsin(z / r))`) surfaces during the smoke test when computing the natal Sun position at the J2000 epoch; this is pre-existing v1.0 behaviour (visible across the project's test suite), NOT introduced by Plan 18-02, and does not affect correctness (the resulting `lat` value is unused — `solar_return` only reads `body[0] = lon`). Out of scope for this plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 18-03 (`lunar_return` public API) ready to execute next.** Plan 18-02 establishes the template `lunar_return` follows verbatim (with body_id=1, `_TROPICAL_MONTH_D=27.321582` seed period, `half_window_days=1.5` matching Sun's bracket, and the additional "first return ≥ `target_jd`" contract via a seed loop). The shared `_solve_return` helper is already battle-tested for both bodies (Plan 18-01 pinned Sun+Moon wrap-around regressions; Plan 18-02 now exercises the Sun path end-to-end via 16 surface tests).
- **Subpackage coverage gate at 96% on disk.** Plan 18-03 should lift it to ~98-100% once `lunar_return` lands; the two residual misses in `_solve.py` (lines 231=`tol_days` early-return, 238=`max_iter` exhaustion fallback) will likely be hit by Plan 18-04 oracle edge cases (lunar return near a calendar-day-boundary `target_jd`).
- **ROADMAP Phase 18 Success Criteria status post-18-02:**
  - SC#1 (solar_return + lunar_return public APIs): **half-satisfied** — `solar_return` shipped; `lunar_return` lands in Plan 18-03.
  - SC#2 (wrap-around tests both Sun AND Moon): satisfied at helper level by Plan 18-01; will be re-pinned at public-API level for Sun in Plan 18-04 (and for Moon in Plans 18-03+18-04).
  - SC#3 (shared `_solve_return` factorisation non-negotiable): **architecturally satisfied** by Plan 18-01; **operationally satisfied for Sun by Plan 18-02** (grep ratchet on `ketu/returns/solar.py` confirms no inline bisection). Same ratchet will apply to `ketu/returns/lunar.py` in Plan 18-03.
  - SC#4 (3 solar + 3 lunar oracle fixtures): solar set landing in Plan 18-04.
  - SC#5 (relocation contract documented LOUDLY): **satisfied for solar** — `solar_return` Notes section distinguishes natal_lat/lon vs return_lat/lon LOUDLY; pinned by `TestSolarReturnNatalLocationIrrelevance` ratchet. Same docstring pattern will apply to `lunar_return` in Plan 18-03.
  - SC#6 (API asymmetry target_year vs target_jd documented LOUDLY): **half-satisfied** — `solar_return` Notes section documents the asymmetry; mirror in `lunar_return` Notes lands in Plan 18-03.
- **No blockers.** Plan 18-03 (`lunar_return` public API, LRET-01..03/05 + first-return-≥-target_jd contract) ready to execute next.

## Self-Check: PASSED

- File `ketu/returns/solar.py`: FOUND (199 LOC)
- File `ketu/returns/__init__.py`: FOUND (modified — added solar_return import + __all__)
- File `tests/returns/conftest.py`: FOUND (113 LOC, 6 fixtures)
- File `tests/returns/test_solar_return.py`: FOUND (308 LOC, 16 tests across 7 classes)
- Commit `514ecbf` (Task 1 — feat: solar_return public API): FOUND
- Commit `3537821` (Task 2 — test: RET-01..03+RET-05 surface tests + natal fixtures): FOUND
- Test suite at 1210 PASS + 2 SKIPPED: VERIFIED (full `pytest tests/ -x` green)
- Coverage gate `make returns-coverage` ≥95%: VERIFIED (96% measured)
- Grep ratchet (no inline bisection in solar.py): VERIFIED (only docstring mentions of the delegated `_solve_return`)
- numpydoc lint clean on `ketu/returns/solar.py`: VERIFIED
- interrogate 100% on `ketu/returns/solar.py`: VERIFIED

---
*Phase: 18-solar-lunar-returns*
*Completed: 2026-05-24*
