---
phase: 18-solar-lunar-returns
plan: 01
subsystem: returns
tags: [returns, bisection, root-finding, wrap-around, numpy, foundation]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE + compute_chart (consumed by Plans 18-02/03)
  - phase: 17-composite-chart-midpoint-variant
    provides: wrap-around convention precedent (circular_midpoint) + subpackage layout precedent
provides:
  - "ketu.returns subpackage skeleton (`__init__.py` with LOUD public-API contract; `__all__` empty pending 18-02/03)"
  - "ketu.returns._solve._solve_return — pure-NumPy bisection root-finder (~30 LOC)"
  - "ketu.returns._solve._signed_residual_deg — canonical Ketu wrap-around algebra ((x-ref+540) % 360) - 180"
  - "Module constants _TOL_DEG, _TOL_DAYS, _TROPICAL_YEAR_D, _TROPICAL_MONTH_D"
  - "tests/returns/test_solve_return.py — 16 helper-level ratchets (wrap-around Sun+Moon, convergence count, bracket rejection)"
  - "tests/returns/test_returns_coverage_gate.py — sentinel marker test"
  - "returns_coverage_gate pytest marker registered alphabetically in pyproject.toml"
  - "ketu.returns in [tool.setuptools].packages"
  - "make returns-coverage Makefile target (two-step pattern)"
affects: [18-02, 18-03, 18-04, 18-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Subpackage with private `_solve.py` helper module (extension of synastry/composite layout)"
    - "Underscored private module + leading-underscore module constants (signals 'private but importable for testability')"
    - "Bisection on signed-short-arc residual with dual stopping criterion (tol_deg + tol_days)"
    - "Bracket-without-sign-change raises ValueError (no auto-extension; caller must extend at public-API level)"

key-files:
  created:
    - ketu/returns/__init__.py
    - ketu/returns/_solve.py
    - tests/returns/__init__.py
    - tests/returns/test_solve_return.py
    - tests/returns/test_returns_coverage_gate.py
  modified:
    - pyproject.toml
    - Makefile

key-decisions:
  - "Plan 18-01: _signed_residual_deg interval is `[-180, +180)` (right-open) — canonical algebra `((x-ref+540) % 360) - 180` returns -180 for antipodal lon=180, ref=0; corrected from plan's stated `(-180, +180]`. Algebra is correct and matches `ketu/composite/core.py:79-81`; semantically `-180` = `+180` (true antipode) for bisection purposes and convergence is unaffected."
  - "Plan 18-01: Bisection chosen over Brent/Newton/secant — pure-NumPy contract (no scipy), curvature indifference (Moon's parallactic peaks), existing precedent (find_exact_aspect, refine_exact_moment). ~30 µs per return — negligible budget."
  - "Plan 18-01: Bracket-without-sign-change raises ValueError (Open Question Q1 lock; no auto-extension). Auto-extension would mask seed-selection bugs in solar_return / lunar_return; caller must fix the seed."
  - "Plan 18-01: tol_deg=1/3600 (1″ residual) + tol_days=1e-7 (~8.6 ms FP-noise floor) dual stopping criterion. Residual fires first by ~10× margin (Sun: 12 iter; Moon: 16 iter measured at 2000-01-01 natal)."
  - "Plan 18-01: returns_coverage_gate marker registered alphabetically between houses_coverage_gate and synastry_coverage_gate in pyproject.toml — RET-06 label for cross-module symmetry (SYN-05 / COMP-05 / CHART-05 / HOU-09)."
  - "Plan 18-01: make returns-coverage uses two-step pattern (pytest tests/returns/ + coverage report --include='ketu/returns/*' --fail-under=95) verbatim mirror of composite-coverage — dodges NumPy _NoValueType reload bug from sub-package source narrowing."

patterns-established:
  - "Pure-NumPy bisection helper at <subpackage>/_solve.py with leading-underscore constants exposed for testability"
  - "Signed-short-arc residual ((x - ref + 540) % 360) - 180 as the canonical Ketu wrap-around convention (composite + houses + returns now all use it)"

# Metrics
duration: ~7min
completed: 2026-05-24
---

# Phase 18 Plan 01: Returns Subpackage Foundation + Shared Bisection Helper Summary

**ketu.returns subpackage skeleton + pure-NumPy `_solve_return` bisection (~30 LOC) + signed-short-arc residual `((x-ref+540) % 360) - 180` + wrap-around regression suite for Sun AND Moon + returns_coverage_gate marker + `make returns-coverage` Makefile target — architectural heart of Phase 18 in place, both Plans 18-02 (solar_return) and 18-03 (lunar_return) will call this single helper per ROADMAP Success Criterion #3**

## Performance

- **Duration:** ~7min
- **Started:** 2026-05-24T14:45:18Z
- **Completed:** 2026-05-24T14:52:46Z
- **Tasks:** 3
- **Files modified:** 7 (5 created + 2 modified)

## Accomplishments
- `ketu/returns/` subpackage created with full module docstring (LOUD guard clauses on API asymmetry, UTC-only, natal_lat/lon vs return_lat/lon, polar relocation safety, aberration convention cancellation).
- `_solve_return` pure-NumPy bisection helper landed at `ketu/returns/_solve.py` (≤30 iter convergence for Sun AND Moon at ±1.5d bracket; ValueError on no-sign-change bracket; module constants exposed for Plans 18-02/03 reuse).
- `_signed_residual_deg` centralizes the wrap-around algebra at `ketu/returns/_solve.py` matching `ketu/composite/core.py:79-81` and `ketu/houses/porphyry.py:159` verbatim.
- Wrap-around regression suite (Sun NEAR-seam + Moon NEAR-seam) pinned BEFORE any public `solar_return` / `lunar_return` API exists — RESEARCH Pitfall 1 (sign error in wrap-around residual near 0°/360°) prevented architecturally.
- Bisection convergence count ratchets pin Sun ≤30 iter (measured 12) and Moon ≤30 iter (measured 16) — catches accidental drift toward linear convergence.
- Bracket-without-sign-change raises `ValueError` (Open Question Q1 lock; no auto-extension).
- `returns_coverage_gate` pytest marker registered alphabetically in `pyproject.toml`; sentinel test `tests/returns/test_returns_coverage_gate.py` ratchets marker recognition + module import.
- `make returns-coverage` Makefile target wired (two-step pattern mirror of `composite-coverage`); gate non-binding in this plan (no solar/lunar yet) but shape correct.
- Suite projet : **1194 passed + 2 skipped** (1177 baseline + 17 new); doc gates clean (numpydoc lint clean, interrogate 100% on `ketu/returns/`).

## Task Commits

Each task was committed atomically:

1. **Task 1: ketu/returns/_solve.py with _solve_return + _signed_residual_deg + constants** — `ca16a36` (feat)
2. **Task 2: ketu/returns/__init__.py docstring + pyproject.toml package/marker + Makefile target** — `7f4fd57` (feat)
3. **Task 3: wrap-around + convergence + bracket-rejection + sentinel marker tests** — `d6970d1` (test)

## Files Created/Modified

- `ketu/returns/__init__.py` (created) — Subpackage init with LOUD module docstring (API asymmetry, UTC-only, natal_lat/lon vs return_lat/lon, polar relocation safety, aberration cancellation); `__all__` empty pending 18-02/03.
- `ketu/returns/_solve.py` (created) — Private bisection helper module hosting `_solve_return`, `_signed_residual_deg`, and module constants `_TOL_DEG`, `_TOL_DAYS`, `_TROPICAL_YEAR_D`, `_TROPICAL_MONTH_D`.
- `tests/returns/__init__.py` (created) — Empty package marker for pytest discovery.
- `tests/returns/test_solve_return.py` (created) — 16 helper-level ratchets across 5 test classes (parametrized residual algebra, Sun wrap-around RET-02 binding, Moon wrap-around LRET-02 binding, convergence count ratchets, bracket rejection ValueError).
- `tests/returns/test_returns_coverage_gate.py` (created) — Sentinel marker test (mirror of `tests/composite/test_composite_coverage_gate.py`).
- `pyproject.toml` (modified) — `ketu.returns` appended to `[tool.setuptools].packages`; `returns_coverage_gate: RET-06 ...` marker registered alphabetically between `houses_coverage_gate` and `synastry_coverage_gate`.
- `Makefile` (modified) — `returns-coverage` two-step target added (mirror of `composite-coverage`); `.PHONY` extended.

## Decisions Made

See `key-decisions` in frontmatter. Six locked decisions; all aligned with Phase 17 / Phase 16 precedents (subpackage layout, marker registration, two-step Makefile pattern). One algebra clarification (interval `[-180, +180)` not `(-180, +180]`) corrected from plan instructions — documented as Rule 1 deviation below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — Bug] Antipodal residual interval correction**

- **Found during:** Task 3 (running `test_solve_return.py`)
- **Issue:** Plan asserted `_signed_residual_deg(180.0, 0.0)` returns `+180.0` ("max edge of (-180, +180]"). The canonical Ketu wrap-around algebra `((180 - 0 + 540) % 360) - 180 = (720 % 360) - 180 = 0 - 180 = -180` returns `-180.0`. The interval is `[-180, +180)` (right-open), not `(-180, +180]` (right-closed). The pin in `tests/returns/test_solve_return.py::TestSignedResidualWrapAround::test_parametrized_signed_residual[180.0-0.0-180.0]` failed with `AssertionError: expected 180.0, got -180.0`.
- **Fix:** Updated test expectation to `-180.0` (matches canonical algebra). Updated `_solve.py` docstring intervals from `(-180, +180]` to `[-180, +180)` for internal consistency. Added clarifying note in the `_signed_residual_deg` Notes section: "The antipodal case `lon - ref == 180` collapses to `-180` under `((180 + 540) % 360) - 180 = -180` (the interval is right-open)."
- **Files modified:** `ketu/returns/_solve.py`, `tests/returns/test_solve_return.py`
- **Verification:** All 16 helper-level tests now PASS; Sun and Moon end-to-end wrap-around regressions PASS (convergence is unaffected — bisection runs across the sign change of the residual, and `-180` semantically equals `+180` for antipodal angles).
- **Committed in:** `d6970d1` (Task 3 commit; docstring correction also bundled).

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug in plan's test expectation, not in code).
**Impact on plan:** Pure docstring/expectation correction. Algebra unchanged; the canonical wrap-around algebra `((x-ref+540) % 360) - 180` matches `ketu/composite/core.py:79-81` verbatim. No scope creep. The antipodal pin remains exact.

## Issues Encountered

None. The three `verify` blocks all passed on the first run (modulo the antipodal-interval Rule 1 fix). Suite green at 1194 PASS + 2 SKIPPED after Task 3 ; no project regression.

Recurring minor process issue (Phase 17 leftover, NOT in v1.2 scope): `venv/bin/pytest` shebang is broken; workaround `python -m pytest` after `source venv/bin/activate` (consistent across Plans 17-01..04 and now 18-01).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **`_solve_return` is the architectural foundation for Plans 18-02 (solar_return) and 18-03 (lunar_return).** Both will import via `from ketu.returns._solve import _solve_return, _signed_residual_deg, _TROPICAL_YEAR_D, _TROPICAL_MONTH_D` and call `_solve_return(body_id, natal_lon_ref, t_seed, half_window_days)` after computing `natal_lon_ref` from `calc_planet_position(natal_jd, body_id)[0]`.
- **Wrap-around safety net is in place** for both Sun (RET-02) and Moon (LRET-02) at the helper level. Plans 18-02 / 18-03 inherit this safety net automatically; their oracle tests (Plan 18-04) only need to pin end-to-end public-API behavior, NOT re-prove the helper.
- **Coverage gate `returns_coverage_gate`** is registered and shape-tested via `make returns-coverage`. The gate is non-binding in this plan (`ketu/returns/_solve.py` 93% measured at module level, mostly due to the `tol_days` early-return path; full coverage of the helper will be exercised by Plan 18-02/03 oracles and validated in Plan 18-05 close-out).
- **No blockers.** Plan 18-02 (solar_return public API) ready to execute next.

## Self-Check: PASSED

- File `ketu/returns/_solve.py`: FOUND
- File `ketu/returns/__init__.py`: FOUND
- File `tests/returns/__init__.py`: FOUND
- File `tests/returns/test_solve_return.py`: FOUND
- File `tests/returns/test_returns_coverage_gate.py`: FOUND
- File `pyproject.toml`: FOUND (modified)
- File `Makefile`: FOUND (modified)
- Commit `ca16a36` (Task 1 — feat: _solve module): FOUND
- Commit `7f4fd57` (Task 2 — feat: subpackage + marker + Makefile): FOUND
- Commit `d6970d1` (Task 3 — test: regression suite + sentinel): FOUND

---
*Phase: 18-solar-lunar-returns*
*Completed: 2026-05-24*
