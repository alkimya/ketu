---
phase: 10-houses-module
plan: 04
subsystem: houses
tags: [placidus, numpy, vectorization, mask-iteration, registry, swisseph-oracle]

# Dependency graph
requires:
  - phase: 10-houses-module/10-01
    provides: apparent-GST sidereal_time + tightened tolerance fences in tests/houses/test_lst_obliquity_precision.py
  - phase: 10-houses-module/10-02
    provides: tests/houses/conftest.py reference_charts + loaded_reference_snapshot fixtures + fixtures/reference_charts.json
  - phase: 10-houses-module/10-03
    provides: SYSTEMS registry + @register decorator + compute_ascmc + ascensional_difference helper
provides:
  - "Placidus implementation: vectorized mask-based fixed-point iteration over (armc, lat, eps) arrays"
  - "@register('placidus') in ketu.houses.SYSTEMS — calculate_houses dispatch (Plan 10-06) requires no edits"
  - "Per-cusp formula dispatch dict (cusps 11/12/2/3) with cusps 5/6/8/9 as 180-deg opposites and 1/4/7/10 closed-form ASC/IC/DESC/MC"
  - "NaN propagation contract: polar boundary or non-convergence => cusp = NaN, surfacing failure for HighLatitudeError routing in Plan 10-06"
  - "MAX_ITER=50 (HOU-03) and TOL_DEG=1e-7 (research §Don't Hand-Roll) constants pinned by invariant tests"
affects: [10-05-koch-porphyry-polar, 10-06-integration-stub-removal, 11-cli-refactor]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mask-based vectorized fixed-point iteration: ``active = ~converged & ~np.isnan(RA)`` updates only un-converged elements; converged ones frozen so they don't pollute others"
    - "Modular convergence metric: ``abs(((RA_new - RA + 180) % 360) - 180)`` handles 0-deg/360-deg wrap (Pitfall 3)"
    - "Polar-boundary NaN propagation: ascensional_difference returns NaN where ``|tan(lat)*tan(decl)| >= 1``; NaN flows through iteration into output cusps as the failure signal"
    - "Per-cusp formula dispatch via dict[int, callable] (no if-elif ladder, anti-pattern 1)"

key-files:
  created:
    - "ketu/houses/placidus.py (362 lines, 100% coverage)"
    - "tests/houses/test_placidus.py (249 lines, 17 tests)"
  modified: []

key-decisions:
  - "Plan reference RA->lambda formula was incorrect; canonical ecliptic-resident transformation is atan2(sin(RA), cos(RA)*cos(eps)) with cos(eps) in the denominator (NOT numerator). Fix verified: 8/8 non-polar charts <1 arcmin oracle agreement (worst 51.5 arcsec at 2050_Reykjavik)"
  - "_iterate_cusp_ra returns (ra, converged) tuple — caller currently discards converged mask but contract preserved for Plan 10-06's polar-fallback routing"
  - "Inline ASC/MC re-derivation from (armc, lat, eps) rather than calling compute_ascmc(jd, lat, lon) — registry signature is (armc, lat, eps), and the closed-form arctan2 evaluation costs ~10 us; redundant compute_armc call would cost more and require jd which we don't have"

patterns-established:
  - "Pattern: Mask-based fixed-point iteration with NaN-as-failure-signal — converged early elements frozen, polar boundary NaNs propagate, MAX_ITER cap turns silent non-convergence into explicit NaN"
  - "Pattern: RA->lambda for ecliptic-resident points uses atan2(sin(RA), cos(RA)*cos(eps)) [NOT atan2(sin(RA)*cos(eps), cos(RA))]; cross-checked vs swisseph oracle and matches ketu.houses._ecliptic.ra_to_lambda exactly"
  - "Pattern: Per-cusp formula table as dict[int, Callable] for data-driven dispatch — Koch (Plan 10-05) will use the same structure"

# Metrics
duration: 5m 57s
completed: 2026-05-07
---

# Phase 10 Plan 04: Placidus Implementation Summary

**Vectorized Placidus house system with mask-based fixed-point iteration on right ascension; <1 arcmin oracle agreement on all 8 non-polar reference charts; NaN propagation at polar boundary for downstream HighLatitudeError routing.**

## Performance

- **Duration:** 5m 57s
- **Started:** 2026-05-07T07:37:23Z
- **Completed:** 2026-05-07T07:43:20Z
- **Tasks:** 2
- **Files created:** 2 (1 source + 1 test)

## Accomplishments

- `placidus_cusps(armc, lat, eps) -> ndarray` registered into `SYSTEMS` via `@register("placidus")` — `calculate_houses` dispatch in Plan 10-06 needs zero changes.
- 8 non-polar reference charts × 12 cusps = **96 oracle-agreement assertions** pass at <1 arcmin tolerance (HOU-09).
- Mask-based vectorized iteration (HOU-08) — single Python loop iterates max-50 times *total*, not 50× per element; the per-date-Python-loop antipattern is forbidden.
- Polar boundary at lat=80° produces NaN cusps for houses 2, 3, 5, 6, 8, 9, 11, 12 (the iterated cusps and their opposites) — closed-form cusps 1, 4, 7, 10 remain finite, surfacing the failure mode Plan 10-05/10-06 will route to `HighLatitudeError` or Porphyry fallback.
- Iteration cap (50) is comfortable: max iter used across **8 charts × 4 iterated cusps = 32 cases** is **35** — typical convergence in <10 iter at most charts, and the cap absorbs the slow-but-converging case (J2000_Equator with declination near 0).
- 555 tests pass overall (538 pre-existing + 17 new); 100% coverage on `placidus.py`; mypy --strict clean.

## Task Commits

1. **Task 1: Implement vectorized Placidus algorithm with mask-based iteration** — `6299ad5` (feat)
2. **Task 2: Write Placidus oracle-agreement and invariant tests** — `418fa25` (test)

## Files Created

- `ketu/houses/placidus.py` (362 lines) — `placidus_cusps` (registered), `_iterate_cusp_ra` (mask-based fixed point), `_ra_to_lambda_placidus` (canonical ecliptic-resident projection), per-cusp formula dispatch dict, MAX_ITER/TOL_DEG constants.
- `tests/houses/test_placidus.py` (249 lines, 17 tests) — 8 parametrized oracle-agreement cases + 9 invariant/correctness cases.

## Per-Chart, Per-Cusp Drift Table (arcsec vs swisseph oracle)

| Chart                | Max delta | cusp 1 | cusp 2 | cusp 3 | cusp 4 | cusp 5 | cusp 6 | cusp 7 | cusp 8 | cusp 9 | cusp 10 | cusp 11 | cusp 12 |
|----------------------|----------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|--------:|--------:|--------:|
| J2000_Greenwich      | **8.11"** | 8.11   | 7.74   | 3.47   | 0.51   | 4.18   | 5.96   | 8.11   | 7.74   | 3.47   | 0.51    | 4.18    | 5.96    |
| J2000_Paris          | **7.44"** | 7.44   | 6.83   | 3.02   | 0.60   | 3.81   | 4.70   | 7.44   | 6.83   | 3.02   | 0.60    | 3.81    | 4.70    |
| J2000_Sydney         | **4.11"** | 4.07   | 1.54   | 2.34   | 0.60   | 1.83   | 4.11   | 4.07   | 1.54   | 2.34   | 0.60    | 1.83    | 4.11    |
| J2000_Tokyo          | **1.23"** | 0.55   | 0.10   | 0.24   | 0.94   | 1.23   | 0.97   | 0.55   | 0.10   | 0.24   | 0.94    | 1.23    | 0.97    |
| J2000_BuenosAires    | **1.91"** | 1.09   | 0.03   | 0.10   | 1.15   | 1.91   | 1.71   | 1.09   | 0.03   | 0.10   | 1.15    | 1.91    | 1.71    |
| J2000_Equator        | **1.33"** | 0.37   | 1.15   | 0.64   | 0.51   | 1.33   | 0.96   | 0.37   | 1.15   | 0.64   | 0.51    | 1.33    | 0.96    |
| 1900_NewYork         | **1.09"** | 0.75   | 0.00   | 0.25   | 0.17   | 0.90   | 1.09   | 0.75   | 0.00   | 0.25   | 0.17    | 0.90    | 1.09    |
| 2050_Reykjavik       | **51.49"**| 51.49  | 25.32  | 11.50  | 0.86   | 8.62   | 10.53  | 51.49  | 25.32  | 11.50  | 0.86    | 8.62    | 10.53   |

**Spec gate (HOU-09):** all max deltas <60" (1 arcmin). **Worst case:** 51.5" at 2050_Reykjavik (lat 64.1°N). This mirrors exactly the worst-case ASC drift Plan 10-03 already documented for that high-latitude chart — it's an input-precision artefact propagating through the closed-form ASC into the iterated cusps, NOT an iteration bug. Other 7 charts are <10" worst-case.

**Symmetry observation:** cusps 1↔7, 2↔8, 3↔9, 4↔10, 5↔11, 6↔12 have identical delta values — confirming the 180-deg-opposite construction (5/6/8/9 derived from 11/12/2/3) preserves error from the iterated cusps without amplification.

## Polar Handling

Polar lat=80° at J2000 (`armc=99.61°`, `eps=23.44°`):

- Houses 1, 4, 7, 10 finite (closed-form ASC/IC/DESC/MC do not iterate).
- Houses 2, 3, 5, 6, 8, 9, 11, 12 = **NaN** (iteration hits `|tan(80°) · tan(decl)| ≥ 1` polar boundary in `ascensional_difference`, NaN propagates).
- ASC ≈ 172.36°, MC ≈ 99.61°, DESC ≈ 352.36°, IC ≈ 279.61°.

This is the contract Plan 10-06 expects: NaN signals "Placidus fails here", caller routes to `HighLatitudeError` (with helpful "polar_fallback='porphyry'" hint) or to the Porphyry fallback Plan 10-05 will register.

## Vectorized vs Scalar Parity

Running 3 charts (Paris J2000, Reykjavik 2050, NewYork 1900) as a batch vs each individually:

- **Max delta: 0.00e+00°** (exact bit-equality, as expected for a deterministic vectorized op).

Confirms HOU-08 — the mask-based loop produces results indistinguishable from per-element scalar iteration.

## Iteration Count Sanity

Across 8 charts × 4 iterated cusps = 32 cases:

- **Max iter used: 35** (well below the 50 cap).
- Typical: <10 iter for mid-latitudes; J2000_Equator's near-zero declinations slow convergence to ~30-35 iter on cusps 11/12/2/3.

The 50 cap is therefore a real safety margin (not a typical value); inflating it to "make hard cases work" hides bugs — we lock the value in `test_placidus_iteration_cap_invariant`.

## SYSTEMS Dict at End of Plan

```python
>>> from ketu.houses.registry import SYSTEMS
>>> sorted(SYSTEMS.keys())
['placidus']    # Plan 10-05 will add 'koch' and 'porphyry'
```

(Note: koch.py and porphyry.py exist on disk as untracked files from Plan 10-05's parallel-wave execution but are NOT imported by `ketu/houses/__init__.py` yet, so their `@register` calls have not executed at the time this plan completed.)

## Decisions Made

- **Inline ASC/MC re-derivation**: `placidus_cusps(armc, lat, eps)` re-derives ASC/MC from its inputs rather than calling `compute_ascmc(jd, lat, lon)` — the registry signature is `(armc, lat, eps)`, the closed-form arctan2 cost is ~10 µs, and calling `compute_ascmc` would require a JD we don't have.
- **`_iterate_cusp_ra` returns `(ra, converged)` tuple**: caller currently discards the `converged` mask, but the contract is preserved for Plan 10-06's polar-fallback routing — letting the caller distinguish "iteration timed out" from "polar boundary" if needed.
- **Single-arg `arctan` for declination**: declination is in `[-π/2, +π/2]` by definition (Pitfall 2 applies to RA / longitude — angles spanning the full circle — not to declination). Documented inline so future readers don't "fix" it to `arctan2`.
- **Mid-latitude-only no-NaN test**: `test_placidus_no_silent_nan_at_mid_latitudes` skips charts at `|lat| ≥ 65°` because Plan 10-02's reference set includes polar lat=70°/80° entries. Polar NaN is a feature, not a bug.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan reference `_ra_to_lambda` formula was incorrect**

- **Found during:** Task 1 (Implement vectorized Placidus algorithm)
- **Issue:** The plan reference text (lines 250-286 of `10-04-placidus-implementation-PLAN.md`) included a long-winded derivation arriving at `λ = atan2(sin(RA) * cos(eps), cos(RA))` — i.e., `cos(eps)` in the **numerator**. Empirically tested at J2000_Paris this produced cusp 11 = 307.14° vs oracle 302.52° (delta ≈ 4.6°, ~277 arcmin — well over the <1 arcmin spec). The plan's own derivation acknowledged the ambiguity ("Wait — that's the inverse of MC...", "BUT: for Placidus specifically..."), and arrived at the wrong simplification. The correct closed-form for an ecliptic-resident point (β = 0) is `λ = atan2(sin(RA), cos(RA) * cos(ε))` — `cos(eps)` in the **denominator**. This matches `ketu.houses._ecliptic.ra_to_lambda` exactly.
- **Fix:** Replaced the formula and updated the docstring to point out the correct identity and the fact that the plan reference text was wrong (preserved as a footnote: "this is **not** the Placidus-MC closed form — that one is identical, but applied to ARMC rather than to the per-cusp iterated RA").
- **Files modified:** `ketu/houses/placidus.py` (in-task fix; not a separate commit).
- **Verification:** All 8 non-polar reference charts × 12 cusps now agree with swisseph oracle <1 arcmin. Cross-validated against `_ecliptic.ra_to_lambda` (the registry helper), against the standard Meeus identity, and against pyswisseph oracle.
- **Committed in:** `6299ad5` (Task 1 commit).

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug fix in plan reference text)
**Impact on plan:** Critical correctness fix — the un-fixed formula would have produced ~277 arcmin oracle drift, ~17000× over spec. No scope creep; the fix is a one-line re-arrangement of `arctan2` arguments.

## Issues Encountered

- mypy --strict initially flagged `Unused "type: ignore[index]" comment` on the `dict[str, object]` access pattern in test fixtures — fixed by replacing `# type: ignore[index,assignment]` with `# type: ignore[assignment]` (the snapshot dict is `dict[str, Any]` from `json.load`, so indexing is valid; only the `dict[str, object]` annotation needed the assignment ignore).

## User Setup Required

None — pure-NumPy implementation; no new runtime dependencies; pyswisseph remains test-only.

## Next Phase Readiness

- **Plan 10-05 (`koch-porphyry-polar`):** unblocked. Same registry infrastructure consumed, plus the same Plan 10-02 fixtures and Plan 10-03 helpers. Koch will use the same per-cusp dispatch-dict pattern; Porphyry is closed-form (no iteration); polar fallback wires NaN-Placidus to Porphyry.
- **Plan 10-06 (`integration-stub-removal`):** unblocked once Plan 10-05 lands. `placidus_cusps` is in `SYSTEMS["placidus"]` and follows the documented signature; `calculate_houses` will dispatch via `get_system(name)` and inspect the output for NaN cusps to route to `HighLatitudeError` or polar fallback per HOU-06.
- **No outstanding blockers from this plan.**

## Self-Check: PASSED

- `ketu/houses/placidus.py` — FOUND
- `tests/houses/test_placidus.py` — FOUND
- `.planning/phases/10-houses-module/10-04-SUMMARY.md` — FOUND
- Commit `6299ad5` (Task 1) — FOUND on `gsd/v1.1-milestone`
- Commit `418fa25` (Task 2) — FOUND on `gsd/v1.1-milestone`

---
*Phase: 10-houses-module*
*Completed: 2026-05-07*
