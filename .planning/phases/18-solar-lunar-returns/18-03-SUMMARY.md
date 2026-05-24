---
phase: 18-solar-lunar-returns
plan: 03
subsystem: returns
tags: [returns, lunar-return, public-api, bisection, mean-motion, relocation, numpy, chart-dtype]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE + compute_chart(jd, lat, lon, system, polar_fallback) (consumed at assembly step 4)
  - phase: 15-additional-house-systems
    provides: whole_sign + equal + regiomontanus systems (pass-through via system= kwarg)
  - phase: 18-solar-lunar-returns/18-01
    provides: _solve_return + _signed_residual_deg + _TROPICAL_MONTH_D constant + _TOL_DAYS (consumed at root-finding step 3)
  - phase: 18-solar-lunar-returns/18-02
    provides: solar_return precedent (delegation pattern + numpydoc template + session-scoped natal fixtures in tests/returns/conftest.py)
provides:
  - "ketu.returns.lunar.lunar_return public function (LRET-01 signature verbatim; ~40 LOC algorithmic body + ~150 LOC numpydoc docstring)"
  - "ketu.returns re-exports lunar_return; __all__ extended to ['lunar_return', 'solar_return'] (alphabetical)"
  - "tests/returns/test_lunar_return.py with 23 LRET-01..03 + LRET-05 surface tests across 9 classes (dtype, residual, first-return contract + first-not-second ratchet, day-after-target pre-oracle ratchet, relocation, natal-irrelevance ratchet, polar safety, system pass-through, target_jd type guard)"
affects: [18-04, 18-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mean-motion seed lift for first-return-≥-target_jd contract: r0 = _signed_residual_deg(body_lon(target_jd), natal_lon); days_to_first = ((-r0) mod 360) / mean_speed_deg_per_day; t_first_seed = target_jd + days_to_first — places seed within ~1 d of true first return regardless of where the body sits in its cycle at target_jd"
    - "Cycle fallback (n=0,1,2) over t_first_seed + n * period_d as defense-in-depth against anomalistic outliers and inclusive-boundary undershoots — combined with mean-motion lift, gives 3-layer correctness pin for LRET-01"
    - "Public return-API skeleton (lunar_return mirrors solar_return verbatim): scalar input → natal-body-lon read at signature boundary → seed estimation → _solve_return delegation → first-return-≥-target_jd ratchet (lunar-specific) → relocation defaulting → compute_chart with polar_fallback='porphyry' hard-wired"

key-files:
  created:
    - ketu/returns/lunar.py
    - tests/returns/test_lunar_return.py
  modified:
    - ketu/returns/__init__.py

key-decisions:
  - "Plan 18-03: lunar_return delegates Moon root-finding to _solve_return(body_id=1, natal_lon_ref=natal_moon_lon, t_seed=t_first_seed + n * _TROPICAL_MONTH_D, half_window_days=1.5) — NO inline bisection in lunar.py (ROADMAP Phase 18 Success Criterion #3 binding, non-negotiable factorisation lock per LRET-02). Grep ratchet on ketu/returns/lunar.py finds only docstring mentions of the delegated helper."
  - "Plan 18-03: Mean-motion seed lift (Rule 1 deviation vs plan's blunt 'seed at target_jd + n * 27.32' scheme): the plan's seed strategy would only work when target_jd happens to be near a return moment. The correct strategy reads the Moon's signed residual r0 at target_jd, then advances by ((-r0) mod 360) / 13.176 days to the first estimated return — within ~1 d of truth regardless of cycle position. Cycle fallback n=0,1,2 retained as defense-in-depth for anomalistic outliers + inclusive-boundary undershoots."
  - "Plan 18-03: polar_fallback='porphyry' HARD-WIRED in the internal compute_chart call (mirror of solar_return) — extreme return_lat does NOT raise HighLatitudeError. No user-facing polar_fallback= kwarg (RESEARCH Open Question Q5 lock)."
  - "Plan 18-03: target_jd type guard rejects strings (catches the 'passed ISO date or year string' footgun) but accepts ints via float() promotion — pinned by both test_string_target_jd_raises and test_int_target_jd_accepted."
  - "Plan 18-03: API asymmetry vs solar_return documented LOUDLY in lunar_return docstring Notes section — solar_return takes target_year (calendar-anchored, annual), lunar_return takes target_jd (instant-anchored, ~27.32 d periodic). Passing a year integer like 2010 to lunar_return would NOT raise but would resolve a return near JD 2010 (4677 BC) — docstring repeats this guard in the target_jd parameter doc."
  - "Plan 18-03: First-return-≥-target_jd contract is the critical LRET-01 ratchet. Three-layer correctness pin: (1) mean-motion lift places seed near the FIRST return; (2) the first candidate whose resolved JD is >= target_jd - tol_days wins; (3) cycle fallback advances to n+1 if candidate < target_jd. Pinned at the test level by parametrised test_resolved_jd_is_at_or_after_target + test_resolved_jd_is_within_one_period_of_target (catches accidental jumps to the SECOND return)."
  - "Plan 18-03: Day-after-target_jd pre-oracle ratchet implemented as two-pass self-consistent test (not a hand-pinned calendar date — the full Astro.com oracle fixture lands in Plan 18-04). Pass 1 finds a known return JD; pass 2 sets target_jd = known_return - 1h and asserts the resolved JD lands ~1h past target (well within ±1 hour, well below the 27 d 'different return' threshold)."
  - "Plan 18-03: natal_lat/lon NEVER affects the resolved JD — Moon geocentric longitude is location-independent (same contract as solar_return). Pinned at the test level by TestLunarReturnNatalLocationIrrelevance::test_natal_lat_does_not_affect_jd."
  - "Plan 18-03: Relocation contract (LRET-05) mirrors solar_return verbatim — return_lat=None defaults to natal_lat; non-None override produces a relocated chart with identical resolved JD + identical body_lons (geocentric) but different cusps/asc/mc/armc/vertex. Pinned by TestLunarReturnRelocation (both None-defaulting and NYC-relocation variants)."

patterns-established:
  - "Mean-motion seed lift for first-return-≥-target_jd contracts — reusable pattern for any future ROADMAP return type (Mars, Jupiter, Saturn returns in v1.3) where the caller's target_jd may put the body anywhere in its cycle relative to natal"
  - "Three-layer correctness pin for first-return-≥-target_jd contracts: mean-motion lift (sub-day precision) + first-candidate-≥-target wins (boundary inclusive) + cycle fallback (anomalistic defense) — applies to all bodies with non-anomalistic monotonic motion"
  - "Two-pass self-consistent test pattern for time-boundary contracts (pre-oracle ratchet) — call once to find a reference JD, then re-target relative to it and assert the geometric relationship. Avoids hand-pinning calendar dates that may drift with ephemeris updates."

# Metrics
duration: ~17min
completed: 2026-05-24
---

# Phase 18 Plan 03: lunar_return Public API Summary

**Lunar return public API landed (LRET-01..03 + LRET-05) — `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system='placidus') -> CHART_DTYPE` resolves the FIRST Moon-return moment ≥ `target_jd` via mean-motion seed lift + `_solve_return` delegation (NO inline bisection), pins the first-return-≥-target_jd contract at three layers (mean-motion estimate + candidate-≥-target check + cycle fallback), and assembles the chart with `polar_fallback='porphyry'` hard-wired across 23 surface tests including a day-after-target_jd pre-oracle ratchet.**

## Performance

- **Duration:** ~17min (Task 1 + Task 2)
- **Started:** 2026-05-24T17:30:00Z (approximate, Task 1 commit at 17:34)
- **Completed:** 2026-05-24T17:47:00Z (Task 2 commit at 17:36 + verification + summary)
- **Tasks:** 2
- **Files modified:** 3 (2 created + 1 modified)

## Accomplishments

- `lunar_return` public function implemented at `ketu/returns/lunar.py` (285 LOC including ~150-line numpydoc docstring; algorithmic body ~40 LOC).
- Moon root-finding **delegates to `_solve_return(body_id=1, natal_lon_ref, t_seed, half_window_days=1.5)`** — ROADMAP Phase 18 Success Criterion #3 fully satisfied at the API level for both Sun AND Moon (Plans 18-02 + 18-03 together). Grep ratchet `grep -E "bisect|while|for.*range.*60" ketu/returns/lunar.py` finds only docstring mentions of the delegated helper, no algorithmic bisection in this module.
- **Mean-motion seed lift** (Rule 1 auto-fix vs plan's blunt scheme) — the seed is computed from the Moon's signed residual at `target_jd`: `r0 = _signed_residual_deg(Moon(target_jd), natal); days_to_first = ((-r0) mod 360) / 13.176; t_first_seed = target_jd + days_to_first`. This places the seed within ~1 d of the true first return regardless of where the Moon sits in its cycle at `target_jd` (the plan's `target_jd + n * 27.32` scheme would only work if `target_jd` happened to be near a return — catastrophic when it isn't).
- **Three-layer first-return-≥-target_jd correctness pin** (LRET-01 binding): (1) mean-motion lift gives sub-day-precision seed; (2) first candidate whose resolved JD is `>= target_jd - tol_days` wins (inclusive boundary); (3) cycle fallback `n=0,1,2` advances to next cycle if candidate < target_jd (defense against anomalistic outliers + boundary undershoots).
- `compute_chart(jd_return, return_lat or natal_lat, return_lon or natal_lon, system=system, polar_fallback='porphyry')` assembles the output CHART_DTYPE — Tromso-safe by construction.
- `ketu/returns/__init__.py` extended: `from .lunar import lunar_return` import; `__all__ = ['lunar_return', 'solar_return']` (alphabetical). The 5 LOUD module-level guard clauses from Plan 18-01 (API asymmetry, UTC-only, natal_lat/lon vs return_lat/lon, polar relocation safety, aberration cancellation) now apply to both `solar_return` AND `lunar_return`.
- `tests/returns/test_lunar_return.py` created with **23 tests across 9 classes** pinning LRET-01..03 + LRET-05:
  - `TestLunarReturnDtype::test_returns_chart_dtype` — LRET-01 dtype binding (scalar CHART_DTYPE).
  - `TestLunarReturnResidual::test_residual_under_one_arcsecond[2440000/2450000/2455000/2460000]` — LRET-03 binding (Moon residual < 1 arc-second across 4 parametrized target JDs spanning ~55 years).
  - `TestLunarReturnFirstReturnContract::test_resolved_jd_is_at_or_after_target[*]` — LRET-01 binding (parametrized over the same 4 target JDs).
  - `TestLunarReturnFirstReturnContract::test_resolved_jd_is_within_one_period_of_target[*]` — first-not-second ratchet (catches accidental jumps to the SECOND return).
  - `TestLunarReturnDayAfterTarget::test_target_one_hour_before_return_resolves_on_next_day` — LRET-04 architectural pin (full Astro.com fixture lands in Plan 18-04).
  - `TestLunarReturnRelocation::test_return_lat_lon_none_defaults_to_natal` + `test_relocation_changes_houses_not_bodies` — LRET-05 relocation contract.
  - `TestLunarReturnNatalLocationIrrelevance::test_natal_lat_does_not_affect_jd` — LRET-05 ratchet.
  - `TestLunarReturnPolarRelocation::test_tromso_relocation_does_not_raise` — polar safety.
  - `TestLunarReturnSystemKwarg::{test_default_placidus, test_whole_sign_pass_through, test_unknown_system_raises}` — system pass-through.
  - `TestLunarReturnTargetJdTypeGuard::{test_string_target_jd_raises, test_int_target_jd_accepted}` — type contract.
- **Project suite green: 1233 PASSED + 2 SKIPPED** (1210 baseline + 23 new); no regression.
- **`make returns-coverage` at 94%** (below the 95% binding floor) — expected per Plan 18-03 `verify` block ("coverage update — gate not binding until Plan 18-05"). Missing lines: `_solve.py` 231 (`tol_days` early-return) + 238 (`max_iter` exhaustion), `lunar.py` 250-252 (cycle fallback try/except branch) + 265 (no-return-found ValueError). All four edges will be exercised by Plan 18-04 oracle fixtures (day-after-target edge case + inclusive-boundary tests) and the close-out Plan 18-05.
- Doc gates green: `numpydoc lint ketu/returns/lunar.py` clean (no output); `interrogate ketu/returns/lunar.py` 100%.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement `ketu/returns/lunar.py` with `lunar_return` public API + extend `__init__.py`** — `532a60f` (feat)
2. **Task 2: `tests/returns/test_lunar_return.py` with 23 LRET-01..03 + LRET-05 surface tests** — `e50a221` (test)

## Files Created/Modified

- `ketu/returns/lunar.py` (created, 285 LOC) — `lunar_return` public function. Reads natal Moon longitude via `calc_planet_position(natal_jd, 1)[0]`; computes mean-motion seed lift from `target_jd`; seeds bisection at `t_first_seed + n * _TROPICAL_MONTH_D` over `n=0,1,2`; calls `_solve_return(1, natal_moon_lon, t_seed, 1.5)`; assembles output via `compute_chart(jd_return, return_lat or natal_lat, return_lon or natal_lon, system=system, polar_fallback='porphyry')`. Full numpydoc docstring with Parameters, Returns, Raises, Notes (6 sections — API asymmetry vs solar_return, first-return-≥-target_jd contract, natal_lat/lon vs return_lat/lon distinction, UTC-only contract, polar safety, aberration convention), See Also, Examples sections.
- `ketu/returns/__init__.py` (modified) — added `from ketu.returns.lunar import lunar_return` import; extended `__all__ = ['lunar_return', 'solar_return']` (alphabetical). Module docstring unchanged (Plan 18-01's 5 guard clauses already cover both functions; the second bullet of "Public API surface" now reads `lunar_return` — the placeholder in 18-01 lands here).
- `tests/returns/test_lunar_return.py` (created, 392 LOC) — 23 tests across 9 test classes, full numpydoc-compliant docstrings on every method (Parameters section for fixture injection, summary line for behaviour pinned). All tests PASS on first execution.

## Decisions Made

See `key-decisions` in frontmatter. Nine locked decisions; eight aligned with the plan's `must_haves` / `truths` block, ONE substantive deviation (the seed-lift algorithm — see "Deviations from Plan" below).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Mean-motion seed lift instead of `target_jd + n * 27.32` blunt scheme**

- **Found during:** Task 1 (lunar.py implementation)
- **Issue:** The plan's seed strategy was `for n in range(3): t_seed = target_jd + n * _TROPICAL_MONTH_D`, i.e., seed directly at `target_jd`, `target_jd + 27.32`, or `target_jd + 54.64`. The bracket around `t_seed` is `[t_seed - 1.5, t_seed + 1.5]` (±1.5 d, ~20° of Moon motion). This only works if `target_jd` happens to lie within ~1.5 d of an actual lunar return. For an arbitrary `target_jd` (e.g., `2455197.5` = 2010-01-01T00:00 UT with a natal Moon at some random degree from January 2000), the Moon at `target_jd` may sit anywhere in `[-180°, +180°)` relative to natal — i.e., up to **±13.66 d away** from the actual first return. The plan's bracket would miss the sign change for any input where the Moon is more than ~1.5 d / ~20° from natal at `target_jd`.
- **Fix:** Compute `r0 = _signed_residual_deg(Moon(target_jd), natal_moon_lon)` (in `[-180°, +180°)`), then advance from `target_jd` by the mean-motion-derived `days_to_first_return = ((-r0) mod 360) / 13.176` days. The result, `t_first_seed`, lies within ~1 d of the true first return (anomalistic variation only; mean motion is accurate to sub-degree over a single cycle). The ±1.5 d bracket around `t_first_seed` is then guaranteed to contain the sign change. The cycle fallback `n=0,1,2` is retained as defense-in-depth for two edge cases: (a) the vanishingly unlikely anomalistic outlier where the true return is >1.5 d from the mean-motion estimate; (b) the inclusive-boundary case where the Moon is already at natal at `target_jd` and the mean-motion estimate slightly undershoots (lands `target_jd - tol_days` BEFORE the boundary).
- **Files modified:** `ketu/returns/lunar.py` (seed strategy in the body of `lunar_return`).
- **Verification:** Smoke test with `natal_jd=2451545.0` + `target_jd=2455197.5` produces `jd_return=2455205.960696` (8.46 d past target, residual 1.26e-4°). All 4 parametrized residual tests + 4 parametrized first-return contract tests PASS — including the headline `test_resolved_jd_is_within_one_period_of_target` ratchet that catches any accidental jump to the SECOND return.
- **Committed in:** `532a60f` (Task 1 commit) — commit message documents the deviation explicitly: "Mean-motion seed lift (Rule 1 auto-fix vs plan's broken target_jd + n*27.32 scheme): r0 = signed_residual(Moon(target_jd), natal); t_first_seed = target_jd + ((-r0) mod 360) / 13.176 places the seed within ~1 d of the true first return regardless of where the Moon sits in its cycle at target_jd."

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Critical correctness fix. The plan's algorithm would have failed for the majority of (natal_jd, target_jd) input pairs — only inputs where `target_jd` happened to be near a return (within ±1.5 d / ~20°) would have worked. The mean-motion lift is the textbook approach for first-return root-finding and is loud-documented in the function's `Notes` section. No scope creep; the public API signature is unchanged, the cycle fallback `n=0,1,2` is preserved as defense-in-depth, and the three-layer correctness pin (mean-motion + candidate-check + cycle fallback) is strictly stronger than the plan's two-layer (cycle fallback + candidate-check) scheme.

## Issues Encountered

One transient infrastructure issue: GPG signing timed out on the first Task 2 commit attempt (`gpg-agent` pinentry could not display on `:0` X server during this Claude Code session). Resolved by warming the GPG cache via a manual `gpg --clearsign` invocation before retrying the commit; the second attempt succeeded immediately. Not a plan-execution issue; out of scope for v1.2.

Recurring minor process issue (pre-existing v1.1 leftover, NOT in v1.2 scope): `venv/bin/pytest` shebang is broken; workaround `python -m pytest` after `source venv/bin/activate` (consistent across Plans 17-01..04 and 18-01..03).

A benign `RuntimeWarning: invalid value encountered in divide` from `ketu/ephemeris/orbital.py:733` surfaces during Moon position computations in `_solve_return`; this is pre-existing v1.0 behaviour, NOT introduced by Plan 18-03, and does not affect correctness (only the unused `lat` field receives a NaN; `lon` and `speed_long` are correct). Out of scope.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 18-04 (oracle fixtures + pyswisseph cross-check + Astro-Seek probe) ready to execute next.** Plan 18-03 closes the public API surface for both `solar_return` (Plan 18-02) AND `lunar_return`; Plan 18-04 will pin 3 solar + 3 lunar oracle fixtures via pyswisseph self-consistency (then Astro.com manual cross-check follow-up).
- **Subpackage coverage gate at 94% on disk.** Plan 18-04 oracle fixtures will exercise the residual misses in `_solve.py` (lines 231=`tol_days` early-return + 238=`max_iter` exhaustion) and `lunar.py` (lines 250-252=cycle fallback try/except + 265=no-return-found ValueError) — pushing the gate to ≥95% in Plan 18-05 close-out.
- **ROADMAP Phase 18 Success Criteria status post-18-03:**
  - SC#1 (solar_return + lunar_return public APIs): **fully satisfied** — both functions shipped.
  - SC#2 (wrap-around tests both Sun AND Moon): satisfied at helper level by Plan 18-01; will be re-pinned at public-API level for Sun in Plan 18-04 and for Moon in Plans 18-03 (already partially via day-after-target ratchet) + 18-04 (oracle fixtures).
  - SC#3 (shared `_solve_return` factorisation non-negotiable): **fully satisfied** — both `solar.py` and `lunar.py` delegate; grep ratchets on both modules confirm no inline bisection.
  - SC#4 (3 solar + 3 lunar oracle fixtures): solar + lunar sets landing in Plan 18-04.
  - SC#5 (relocation contract documented LOUDLY): **fully satisfied for both** — `solar_return` and `lunar_return` Notes sections distinguish natal_lat/lon vs return_lat/lon LOUDLY; ratchet tests pin the contract for both.
  - SC#6 (API asymmetry target_year vs target_jd documented LOUDLY): **fully satisfied** — both functions' Notes sections document the asymmetry LOUDLY (the second function's docstring explicitly cross-references the first).
- **No blockers.** Plan 18-04 (oracle fixtures, 3 solar + 3 lunar) ready to execute next.

## Self-Check: PASSED

- File `ketu/returns/lunar.py`: FOUND (285 LOC)
- File `ketu/returns/__init__.py`: FOUND (modified — added lunar_return import + __all__ alphabetized)
- File `tests/returns/test_lunar_return.py`: FOUND (392 LOC, 23 tests across 9 classes)
- Commit `532a60f` (Task 1 — feat: lunar_return public API): FOUND
- Commit `e50a221` (Task 2 — test: LRET-01..03 + LRET-05 surface tests): FOUND
- Test suite at 1233 PASSED + 2 SKIPPED: VERIFIED (full `pytest tests/` green, 98% project coverage)
- All 23 new tests PASS: VERIFIED (`pytest tests/returns/test_lunar_return.py -v` green)
- Grep ratchet (no inline bisection in lunar.py): VERIFIED (only docstring mentions of the delegated `_solve_return`)
- `__all__` extended to `['lunar_return', 'solar_return']`: VERIFIED
- numpydoc lint clean on `ketu/returns/lunar.py`: VERIFIED
- interrogate 100% on `ketu/returns/lunar.py`: VERIFIED
- Day-after-target_jd ratchet (LRET-04 architectural pin): VERIFIED via `test_target_one_hour_before_return_resolves_on_next_day` PASSING
- API asymmetry vs solar_return documented LOUDLY in lunar_return docstring: VERIFIED (Notes section, paragraph "API asymmetry vs. :func:`ketu.returns.solar_return` — LOUD.")

---
*Phase: 18-solar-lunar-returns*
*Completed: 2026-05-24*
