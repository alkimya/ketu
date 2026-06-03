---
phase: 33-lunar-declination
plan: 03
subsystem: composite
tags: [declination, body-decl, composite, returns, zero-fill-trap, coordinates-chain, numpy, equatorial]

# Dependency graph
requires:
  - phase: 33-lunar-declination
    plan: 02
    provides: body_decl field in CHART_DTYPE (f8, (14,)) + compute_chart population via coordinates chain

provides:
  - calculate_composite explicitly assigns out["body_decl"] derived from composite λ,β via coordinates chain (DECL-07 downstream)
  - Composite zero-fill trap (Pitfall 4) closed with anti-regression test
  - TestCompositeDeclination: 4 tests — shape, non-zero off-equator, valid range, chain self-consistency (< 1e-9°)
  - TestLunarReturnBodyDecl: 3 tests — dtype ratchet, populated non-zero, matches declination() array path at 0.0
  - Returns body_decl inheritance proven by test (not just assumed)
  - Synastry confirmed no-op (non-CHART grid dtype, no body_decl expected)

affects:
  - 33-04 (docs: composite body_decl field visible in numpydoc)
  - 35-release-v15 (body_decl fully wired across chart, composite, returns)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Composite body_decl: derive via coordinates chain on composite λ,β (NOT midpoint of parents' δ) — Open Question 1 resolved to option (a)"
    - "Anti-regression pattern: assert np.any(np.abs(decl) > 0.01) catches the silent zero-fill trap from np.zeros((), CHART_DTYPE)"
    - "Self-consistency test: re-derive δ inline from composite body_lons/body_lats, assert max diff < 1e-9°"
    - "Returns inheritance proof: compare body_decl to declination(np.array([jd]), body_int) — 0.0 diff confirms same evaluator (calc_planet_position_batch)"

key-files:
  created: []
  modified:
    - ketu/composite/api.py
    - tests/composite/test_calculate_composite.py
    - tests/returns/test_lunar_return.py

key-decisions:
  - "Composite body_decl derived via coordinates chain on the composite's own body_lons/body_lats (NOT midpoint of parents' declinations) — Open Question 1 option (a); parallel to how body_lats is midpoint of ecliptic latitudes, body_decl uses the full ecliptic->equatorial chain"
  - "Returns body_decl comparison uses the ARRAY path of declination() (same evaluator: calc_planet_position_batch) — produces 0.0 absolute difference; scalar path would differ by up to 0.025°"

patterns-established:
  - "Pitfall 4 anti-regression: np.zeros((), CHART_DTYPE) silently initializes all body_decl to 0.0 — any downstream consumer that allocates and copies fields by name must explicitly assign body_decl"

# Metrics
duration: 4min
completed: 2026-06-03
---

# Phase 33 Plan 03: Composite body_decl propagation + Returns inheritance proof Summary

**calculate_composite explicitly assigns out["body_decl"] via coordinates chain on composite λ,β; Pitfall 4 (silent zero-fill) closed with anti-regression test; Returns inheritance from compute_chart proven at 0.0 difference against declination() array path**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-03T19:55:12Z
- **Completed:** 2026-06-03T19:59:27Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added `out["body_decl"] = _decl` in `calculate_composite` — derived from composite `body_lons`/`body_lats` already assigned, via `true_obliquity(float(out["jd"]))` + spherical/rectangular coordinates chain; closes Pitfall 4 (silent zero-fill from `np.zeros((), CHART_DTYPE)`)
- Added `TestCompositeDeclination` class (4 tests): shape (14,), non-zero off-equator, valid range [-90, +90]°, chain self-consistency to < 1e-9° (max diff = 0.0 — same code path used in api and test)
- Added `TestLunarReturnBodyDecl` class (3 tests): dtype ratchet (`body_decl` in `CHART_DTYPE`), non-zero populated (proves inheritance via `compute_chart`, not assumption), matches `declination()` array path at 0.0 (same evaluator: `calc_planet_position_batch`)

## Task Commits

1. **Task 1: Populate out["body_decl"] in calculate_composite via coordinates chain** — `6b5af52` (feat)
2. **Task 2: Composite DECL-07 tests — body_decl non-zero + chain self-consistency** — `af70f4d` (test)
3. **Task 3: Returns DECL-07 inheritance tests — body_decl carried by lunar_return** — `fb80084` (test)

**Plan metadata:** (this commit)

## Files Created/Modified

- `ketu/composite/api.py` — Added 5 imports from `ketu.ephemeris.coordinates`; added 9-line `body_decl` derivation block after `body_speeds` assignment (with explanatory comment resolving Open Question 1)
- `tests/composite/test_calculate_composite.py` — Added 4 coordinate-chain imports; added `TestCompositeDeclination` class (4 tests, DECL-07 composite coverage)
- `tests/returns/test_lunar_return.py` — Added `from ketu.calculations import declination`; added `TestLunarReturnBodyDecl` class (3 tests, DECL-07 returns inheritance proof)

## Decisions Made

- **Composite body_decl derivation**: option (a) — derive via the full coordinates chain on the composite's own `body_lons`/`body_lats`, NOT midpoint of parents' declinations. This is physically more correct (δ of the composite midpoint chart) and numerically consistent with the chain used in `compute_chart`. Open Question 1 from research resolved.
- **Returns comparison reference**: array path of `declination()` (integer body id, `np.array([jd])`) gives 0.0 absolute difference vs `body_decl` in the chart — same evaluator (`calc_planet_position_batch`). Scalar path would differ by up to ~0.025° (documented in Plan 02 deviation).

## Deviations from Plan

None — plan executed exactly as written. The coordinates-chain derivation, anti-regression test structure, and return comparison strategy all matched the plan's specification.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- DECL-07 fully closed: chart (Plan 02), composite (this plan), returns (this plan); Synastry confirmed no-op
- 1584 tests, 100% coverage, `mypy --strict` clean
- Ready for Plan 33-04 (documentation: body_decl field visible in numpydoc, composite api.py docstring update)

---

## Self-Check: PASSED

- `ketu/composite/api.py` — FOUND
- `tests/composite/test_calculate_composite.py` — FOUND
- `tests/returns/test_lunar_return.py` — FOUND
- Commit `6b5af52` — FOUND
- Commit `af70f4d` — FOUND
- Commit `fb80084` — FOUND

---
*Phase: 33-lunar-declination*
*Completed: 2026-06-03*
