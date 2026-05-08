---
phase: 14-chart-abstraction-foundation
plan: 04
subsystem: charts
tags: [numpy, sect, is-day-chart, hellenistic, polar-safe, porphyry-fallback, sunrise-inclusive, vectorisation, mypy-strict, numpydoc, interrogate]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    plan: 01
    provides: CHART_DTYPE frozen layout, is_day_chart stub signature/docstring
  - phase: 10-houses-module
    provides: calculate_houses (broadcast, polar_fallback contract), house_of (1..12 house mapping with cusps[i] BEGINS house i+1 convention)
  - phase: 04-ephemeris-batch
    provides: calc_planet_position_batch (vectorised on jd, body_id=0 = Sun longitude in column 0)
provides:
  - is_day_chart wired (sunrise-inclusive sect helper, polar-safe via internal Porphyry fallback)
  - tests/charts/test_is_day_chart.py (12 unique tests, 32 PASSED entries via parametrization)
affects: [14-05-doc-gates-and-coverage, 19-arabic-parts]

# Tech tracking
tech-stack:
  added: []  # No new runtime deps; pure NumPy on existing primitives
  patterns:
    - "is_day_chart composes calculate_houses(polar_fallback='porphyry') + calc_planet_position_batch(jd, 0) + house_of (no new astronomical math)"
    - "Internal polar_fallback='porphyry' is always-on regardless of caller (D-15) — distinct from compute_chart's pass-through behaviour (D-11)"
    - "np.asarray(sun_house >= 7) wraps the bool comparison so scalar inputs return a 0-d np.ndarray rather than a bare np.bool_ scalar — uniform return contract"
    - "Sunrise-inclusive convention pinned via synthetic +/-0.01 deg deltas around the ASC, not strict equality (measure-zero in real data)"
    - "house_of body_id=0 = Sun mirrors _vectorised_body_properties from plan 14-02: single source-of-truth for the canonical (13,) body axis"

key-files:
  created:
    - tests/charts/test_is_day_chart.py
    - .planning/phases/14-chart-abstraction-foundation/14-04-SUMMARY.md
  modified:
    - ketu/charts/api.py
    - tests/charts/test_dtype.py

key-decisions:
  - "Followed plan exactly — sunrise-inclusive convention via 'return sun_house >= 7' (no np.isclose branch on Sun==ASC equality, per Open Question 1 pragmatic recommendation)"
  - "Internal polar_fallback hardcoded to 'porphyry' regardless of any caller setting (D-15) — is_day_chart is the canonical sect entry point and must always return a bool answer"
  - "Cast removed from is_day_chart return: np.asarray(...) is sufficient for mypy --strict (cast was redundant and flagged as redundant-cast)"
  - "Cross-API consistency test split into two: 5-city sub-polar parametrization (default polar_fallback='raise') + dedicated polar test (explicit polar_fallback='porphyry') — pins the D-15 internal-Porphyry choice contractually"
  - "Sunrise-inclusive convention pinned by direct house_of injection at asc-0.01 (house 12 = day) and asc+0.01 (house 1 = night) rather than ephemeris root-finding (more stable, faster, isolates the convention from astronomical noise)"

patterns-established:
  - "Plan-04 sect contract: is_day_chart returns np.ndarray of bool with shape == np.broadcast_shapes(jd, lat, lon); scalar input -> 0-d ndarray (not np.bool_ scalar)"
  - "Internal-fallback-different-from-pass-through pattern: compute_chart honours D-11 caller-driven polar_fallback; is_day_chart honours D-15 always-on internal polar_fallback. Documented loudly in both docstrings."
  - "Pragmatic equality convention pattern: when strict equality has measure zero on real data, validate the convention via synthetic +/-eps deltas rather than introducing np.isclose branches in the hot path"

requirements-completed: [CHART-04]

# Metrics
duration: ~6 min
completed: 2026-05-08
---

# Phase 14 Plan 4: is_day_chart sect helper (polar-safe) Summary

**`is_day_chart` wired as the canonical sunrise-inclusive sect entry point — broadcast `(jd, lat, lon)`, internal Porphyry fallback for polar safety (D-15), Sun-via-`calc_planet_position_batch` + `house_of >= 7` composition (D-14), no declination math.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-08T22:47:40Z (after worktree base correction to 051d716)
- **Completed:** 2026-05-08T22:53:47Z
- **Tasks:** 3 (1 implementation + 1 stub cleanup + 1 dedicated test file)
- **Files created:** 2 (1 test file + 1 SUMMARY)
- **Files modified:** 2 (`ketu/charts/api.py`, `tests/charts/test_dtype.py`)

## Accomplishments

- `is_day_chart(jd, lat, lon)` body wired in `ketu/charts/api.py`: broadcast `(jd, lat, lon)` mirroring `compute_chart`, `calculate_houses(...)` with `polar_fallback="porphyry"` always-on (D-15 internal-fallback contract), `calc_planet_position_batch(jd_b.ravel(), 0)[:, 0]` for the Sun longitude, `house_of(sun_lon, cusps) >= 7` for the day/night decision, `np.asarray(...)` wrap to keep the public `np.ndarray` return contract uniform across scalar and vectorised call sites.
- Docstring rewritten to ship the final v1.2 contract: D-13 sunrise-inclusive convention loudly called out (with the measure-zero rationale for the pragmatic `>= 7` formulation), D-15 polar-safety paragraph distinguishing `is_day_chart`'s always-on internal Porphyry from `compute_chart`'s D-11 caller-driven pass-through, D-14 geometric definition (houses 7..12 = above-horizon hemisphere), D-12 standalone-helper rationale (not stored in CHART_DTYPE to avoid double source-of-truth drift).
- Doctest examples replaced with executable `bool(is_day_chart(...))` calls (no `# doctest: +SKIP`) — Paris J2000 noon = day, midnight = night, vectorised midnight+noon, polar Tromsø safety. All examples are now real assertions, not skipped.
- `tests/charts/test_is_day_chart.py` ships 32 PASSED entries covering 12 unique test functions: return type contract (0-d ndarray bool), Paris J2000 noon/midnight hand-validated cases, 1-d vectorisation over jd, mixed broadcast `(3,) x (2,1) -> (2,3)`, 2-d input shape preservation, polar safety at lat=80 (no raise) + parametrized arctic sweep (4 lats × 4 jds across the year, 16 cases), cross-API consistency vs `compute_chart` (5 cities) + dedicated polar consistency via explicit Porphyry, sunrise-inclusive pragmatic ±0.01° pinning, Sydney southern hemisphere sanity, AGPL no-runtime-swisseph ratchet.
- `tests/charts/test_dtype.py` cleaned up: `test_is_day_chart_raises_not_implemented_until_plan_14_04` removed; module docstring updated to reflect the plan-14-04 transition; the `is_day_chart` import is preserved (still consumed by `test_public_imports_resolve`).
- All gates pass: `pytest tests/charts/` 106/106, `pytest tests/` 830/830 (vs 799 baseline + 31 new — zero regression), `mypy --strict ketu/charts/` clean (3 source files), `interrogate ketu/` 100.0% (224/224, ≥95% gate), `numpydoc lint ketu/charts/api.py` clean, AGPL boundary smoke OK, polar sanity (`is_day_chart(2451545.0, 80.0, 0.0) -> True`), vectorisation sanity (`is_day_chart(np.array([midnight, noon]), 48.86, 2.35) -> [False, True]`).

## Task Commits

Tasks 1–3 committed as a single atomic `feat` per the plan's prescribed atomic-commit-message section:

1. **Tasks 1–3: Implement is_day_chart sect helper (polar-safe)** — `1c0b7d7` (feat)

## Files Created/Modified

- `ketu/charts/api.py` — `is_day_chart` body wired (broadcast + internal-Porphyry houses + Sun longitude + `house_of >= 7`); docstring expanded with the full D-12/13/14/15 contract; `house_of` import added at the top of the module. Stub `NotImplementedError` removed. mypy --strict clean (no `cast` needed; `np.asarray` returns `np.ndarray` natively).
- `tests/charts/test_is_day_chart.py` — Created. 12 unique test functions (32 PASSED entries via parametrization) pinning the v1.2 sect contract.
- `tests/charts/test_dtype.py` — Modified. `test_is_day_chart_raises_not_implemented_until_plan_14_04` stub guard removed; module docstring updated to reflect the plan-14-04 transition.
- `.planning/phases/14-chart-abstraction-foundation/14-04-SUMMARY.md` — This file.

## Decisions Made

Followed the plan exactly with three small in-scope adjustments documented as Rule-3 tweaks:

1. **`np.asarray` wrap on the return value (not in the plan).** During first pytest run the polar-safety tests asserted `isinstance(result, np.ndarray)` per the plan's Test #1 spec, but NumPy returns a `np.bool_` scalar (with `.shape == ()` and `.dtype == np.bool_`) for fully-scalar `house_of(...) >= 7`. Wrapping the comparison in `np.asarray(...)` upgrades the scalar case to a 0-d `np.ndarray` and keeps the public `np.ndarray` return contract uniform across scalar and vectorised call sites. This is a Rule-2 fix (correctness: the plan's docstring promises `np.ndarray`; the `np.bool_` scalar would have broken downstream callers that introspect `.shape` / `.dtype` on the assumption they're dealing with an ndarray).
2. **`cast` removed from the return line.** The original plan snippet showed `return cast(np.ndarray, sun_house >= 7)` to silence mypy. After the `np.asarray` wrap, mypy --strict flags the cast as `redundant-cast` because `np.asarray` already returns `np.ndarray`. Removed `cast(np.ndarray, ...)` — `np.asarray(sun_house >= 7)` is mypy-clean on its own. The `cast` import is still used by `compute_chart` line 241 so the import stays.
3. **Cross-API consistency test split into two.** The plan's Test #9 prescribed "5 charts variés (incl. polaire)" but explicitly noted that `compute_chart`'s default `polar_fallback="raise"` would block the polar case. Implemented as two tests: (a) parametrized over 5 sub-polar cities (Paris, Sydney, NYC, Tokyo, Reykjavík) with `compute_chart`'s default; (b) dedicated polar test at lat=80 with explicit `polar_fallback="porphyry"` to mirror `is_day_chart`'s internal D-15 choice. This pins the cross-API consistency contract more crisply and exposes the D-15 design choice to test-time scrutiny.

None of these adjustments alter the contract surface, the file count, or the verification gates. The plan's `done criteria` checklist is met one-for-one.

## Deviations from Plan

**Plan executed exactly as written.** Three minor in-task adjustments listed above as Decisions. No architectural changes; no new files beyond what the plan specified; no auth gates encountered.

The plan's Test #11 (`test_is_day_chart_no_runtime_swisseph_import`) is shipped as `test_no_runtime_swisseph_import_via_is_day_chart` and explicitly triggers a real `is_day_chart(...)` call before checking `sys.modules` — this catches lazy imports that wouldn't fire on bare `import ketu.charts`. Stronger than a pure import-time check, aligned with the plan's intent.

## Issues Encountered

- **Pre-existing `RuntimeWarning` in `ketu/ephemeris/orbital.py:733`** (`invalid value encountered in divide` inside `np.arcsin(z / r)`) — same warning logged in plan 14-02. Surfaces during `is_day_chart` calls for some `(jd, lat)` combinations. Out-of-scope per the SCOPE BOUNDARY rule (not caused by this plan's changes; carry-over from before plan 14-01). Logged here for the verifier; no action taken in plan 14-04.
- **Coverage gate noise on partial run** (carry-over from 14-01/02) — `pytest tests/charts/` without `--no-cov` still hits the project-wide `--cov=ketu --cov-fail-under` config. Standard mitigation: use `--no-cov` for partial runs, full `pytest tests/` for the suite gate. Both green here. Not a blocker.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 14-05 ready** — doc gates already green at this checkpoint (interrogate 100%, numpydoc lint clean, mypy --strict clean). Plan 14-05's role is the Makefile target + `make charts-coverage` validation, not docstring rewrites. The `is_day_chart` docstring is final and contractually frozen.
- **Plan 14-03 (aspect_matrix) and Plan 14-04 (this plan) are independent.** Plan 14-03 lands the aspect-matrix dense block in `compute_chart`; it does not interact with `is_day_chart`. Both can ship in any order in the same wave.
- **Phase 19 (Arabic Parts) ready** — `is_day_chart(jd, lat, lon)` is the canonical sect entry point. Phase 19 callers can rely on:
  - Bool answer at every latitude (no `HighLatitudeError` thanks to D-15 internal Porphyry).
  - Sunrise-inclusive convention (D-13) — synthetic ±0.01° pinned tests guarantee the sect rule for the corner cases real ephemeris data will surface.
  - Vectorisation across `(jd, lat, lon)` of any compatible broadcast shape — Phase 19 batches over Solar Returns / relocated charts / synastry transits get a single-call sect resolution.
- No blockers. No carry-over technical debt from this plan.

## TDD Gate Compliance

This plan does not declare `type: tdd` in its frontmatter; the GREEN-then-VERIFY pattern was used (tests written alongside the implementation in a single atomic commit, per the plan's prescribed atomic-commit-message section). RED gate not required.

## Self-Check: PASSED

Files verified to exist:

- FOUND: ketu/charts/api.py (modified)
- FOUND: tests/charts/test_is_day_chart.py
- FOUND: tests/charts/test_dtype.py (modified)
- FOUND: .planning/phases/14-chart-abstraction-foundation/14-04-SUMMARY.md

Commits verified to exist:

- FOUND: 1c0b7d7 (feat(14-04): implement is_day_chart sect helper (polar-safe))

Verification gates re-confirmed:

- pytest tests/charts/test_is_day_chart.py → 32 passed
- pytest tests/charts/ → 106 passed (75 baseline + 31 new = 106; 32 new in test_is_day_chart minus 1 stub removed in test_dtype = +31)
- pytest tests/ (full suite) → 830 passed (vs 799 baseline + 31 = 830; zero regression)
- mypy --strict ketu/charts/ → Success: no issues found in 3 source files
- interrogate ketu/ → 100.0% (PASSED, minimum 95.0%)
- numpydoc lint ketu/charts/api.py → clean
- AGPL boundary smoke → AGPL OK (no swisseph in sys.modules after `import ketu.charts`)
- Polar sanity → `is_day_chart(2451545.0, 80.0, 0.0) -> True` (no raise, clean bool)
- Vectorisation sanity → `is_day_chart(np.array([2451544.5, 2451545.0]), 48.86, 2.35) -> [False, True]`

---
*Phase: 14-chart-abstraction-foundation*
*Plan: 04-is-day-chart-helper*
*Completed: 2026-05-08*
