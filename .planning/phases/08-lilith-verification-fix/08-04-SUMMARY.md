---
phase: 08-lilith-verification-fix
plan: 04
subsystem: ephemeris
tags: [lilith, mean-apogee, swiss-ephemeris, formula-correction, perturbation, single-source-of-truth, regression-baseline]

# Dependency graph
requires:
  - phase: 08-lilith-verification-fix
    provides: 08-01 LILITH_DEFINITION.md (formula, frame, tolerance contract)
  - phase: 08-lilith-verification-fix
    provides: 08-02 [project.optional-dependencies].test = ["pysweph>=2.10.3.6"]
  - phase: 08-lilith-verification-fix
    provides: 08-03 cross-check harness empirical verdict (MAX |delta| = 179.94 deg, branch FORMULA-CORRECTION)
provides:
  - "Corrected get_lilith_position formula -- 4 plumbing sites updated, single source of truth in orbital.py"
  - "Empirical post-fix MAX |delta| = 0.002693 deg on 5 plan dates (3.7x under tolerance)"
  - "Empirical post-fix MAX |delta| = 0.007815 deg over 55K daily samples 1900-2050 (1.3x under tolerance)"
  - "REGRESSION_TOLERANCE_DEG = 0.005 -- 1.85x post-fit max with safety margin"
  - "v1.1 Lilith private constants: _LILITH_MEAN_EPOCH_DEG, _LILITH_MEAN_RATE_DEG_PER_DAY, _LILITH_PERTURB_AMP_DEG, _LILITH_PERTURB_RATE_DEG_PER_DAY, _LILITH_PERTURB_PHASE_DEG"
affects:
  - 08-05-release-notes

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single source of truth for duplicated physical constants: define once at module scope with leading-underscore name, import everywhere else"
    - "Sinusoidal perturbation correction inside an analytical mean-element formula (linear secular term + one sin() term, joint NLS-fitted)"
    - "Regression-baseline test layer at tighter-than-user tolerance: same swe.calc_ut reference, same dates, smaller TOLERANCE -- pins the agreement margin without hardcoding Ketu output"

key-files:
  created:
    - ".planning/phases/08-lilith-verification-fix/08-04-SUMMARY.md"
  modified:
    - "ketu/ephemeris/orbital.py (+86 / -11; +5 module-level constants, get_lilith_position rewritten, ORBITAL_ELEMENTS row uses named rate)"
    - "ketu/ephemeris/planets.py (+4 / -2; imports named rate, lon_speed and avg_speeds[12] use named rate)"
    - "tests/test_lilith_cross_check.py (+45; REGRESSION_TOLERANCE_DEG = 0.005, test_lilith_regression_baseline parametrized over same 5 dates)"
    - "docs/LILITH_DEFINITION.md (+88 / -34; Formula section rewritten with v1.1 form, History section records old vs new constants)"

key-decisions:
  - "Plan 04 = FORMULA-CORRECTION branch executed (per Plan 03 SUMMARY contract: empirical MAX |delta| = 179.936579 deg >> 0.01 deg tolerance)"
  - "Pure linear correction insufficient: residual after epoch+rate fit is ~0.12 deg with sinusoidal shape (period ~1095 days), 12x tolerance. Plan 04 added one sin() perturbation term to meet tolerance"
  - "Single source of truth pattern: 5 v1.1 constants defined once at module scope in orbital.py with leading-underscore (private) names; 4 plumbing sites import or reference them. Future edits touch one declaration"
  - "REGRESSION_TOLERANCE_DEG = 0.005 (about 1.85x post-fit max of 0.002693) -- pins agreement margin without creating Ketu-tests-Ketu loop"
  - "round(rate, 6) at avg_speeds[12]: keeps the 6-decimal column convention in planets.py while inheriting the source-of-truth value"

patterns-established:
  - "Mean-element formula = linear secular term + small set of sin() perturbations: when a pure linear fit cannot meet a 0.01 deg tolerance vs. an external reference, add the dominant FFT-identified perturbation; document the period and phase reference"
  - "Joint NLS for analytical-formula calibration: refine all parameters (rate, epoch, amplitude, perturbation rate, perturbation phase) jointly via Nelder-Mead after a linear+1-sinusoid initialization; documented residual budget over both the test dates and the dense fitting window"

# Metrics
duration: 10m 1s
completed: 2026-05-06
---

# Phase 8 Plan 4: Conditional Formula Fix (FORMULA-CORRECTION branch) Summary

**Plan 03's empirical verdict was MAX |delta| = 179.936579 deg, branch FORMULA-CORRECTION. Plan 04 executed that branch: replaced the v1.0 perigee-not-apogee constants with a v1.1 fit (linear secular term + one sinusoidal perturbation, joint NLS over 55K daily samples 1900-2050). All four duplicated rate-constant call sites now reference a single private source of truth in `ketu/ephemeris/orbital.py`. Post-fix MAX |delta| = 0.002693 deg on the 5 cross-check dates and 0.007815 deg over the dense 55K-sample window -- both below the 0.01 deg tolerance. Harness: 10 passed (5 user-tolerance + 5 regression-tolerance at 0.005 deg). Existing test suite: 420 passed (was 410 + 5 newly-green user-tolerance + 5 new regression-tolerance), no regressions. Mypy --strict: clean. `docs/LILITH_DEFINITION.md` Formula and History sections rewritten.**

## Branch Selected

**Plan 04: FORMULA-CORRECTION**

Parsed from `08-03-SUMMARY.md`:

```text
MAX |delta| = 179.936579 deg
Plan 04: FORMULA-CORRECTION
```

Internally consistent: 179.94 >> 0.01 -> FORMULA-CORRECTION (not NO-OP). Per-date table, error-shape diagnosis (constant ~180 deg offset, secondary residual ~0.11 deg), and suspected root cause (epoch off by 180 deg + secondary frame/rate term) were all extracted as expected.

## v1.0 -> v1.1 Constants

| Constant | v1.0 (legacy) | v1.1 (fitted) | Notes |
| --- | --- | --- | --- |
| Epoch (mean longitude at J2000.0) | `83.3532 deg` | `263.3521188770 deg` | v1.0 was the perigee; corrected by adding 180 deg + small rate-of-day offset |
| Rate (mean motion) | `0.1114040803 deg/day` | `0.1114036699 deg/day` | Tiny correction (~4e-7 deg/day) -- not the source of the user-visible error |
| Perturbation amplitude | (none) | `0.1156754590 deg` | New term -- absorbs the residual ~0.12 deg sinusoid |
| Perturbation rate | (none) | `0.3287143373 deg/day` | Period ~1095.25 days (~3 sidereal years) |
| Perturbation phase at J2000.0 | (none) | `96.6084061482 deg` | |

The v1.1 formula:

```text
lilith_lon = (E + R*d + A*sin(omega*d + phi)) mod 360 deg
where d = JD_UT - 2451545.0
```

## Linear-Regression Residuals

The naive 5-point fit (using only the plan dates) was not used directly: with 5 sparse samples and a 0.1114 deg/day rate, np.unwrap cannot recover the integer cycle counts (each adjacent sample is hundreds of degrees apart). I instead unwrapped using a known-approximate rate as reference, ran a coarse linear fit (max |residual| = 0.124 deg), identified the dominant ~1095-day perturbation via FFT on a dense daily sample over 1900-2050, then refined all five parameters jointly via Nelder-Mead (xatol=1e-12, fatol=1e-12).

### Per-date residuals at the v1.1 fit

| Date | Ketu (v1.1) | swe.MEAN_APOG | delta |
| --- | ---: | ---: | ---: |
| 1900-06-15T12:00:00+00:00 | 172.874758 | 172.875666 | -0.000908 |
| 1950-03-21T18:30:00+00:00 |  37.629502 |  37.630263 | -0.000761 |
| 2000-01-01T12:00:00+00:00 | 263.467026 | 263.464333 | +0.002693 |
| 2025-09-23T06:00:00+00:00 | 230.090328 | 230.090289 | +0.000039 |
| 2050-12-21T00:00:00+00:00 | 177.413557 | 177.412343 | +0.001213 |

**5-date MAX |delta| = 0.002693 deg** (3.7x under the 0.01 deg tolerance).

### Dense window (1900-2050, daily, 55K samples)

| Statistic | Value |
| --- | ---: |
| MAX |residual| | 0.007815 deg |
| MEAN |residual| | 0.003190 deg |
| STD residual | 0.003747 deg |

All below the 0.01 deg tolerance. The MAX |residual| occurs near the boundaries of the fitting window (1900 and 2050) where the dense-sample uniform error budget is tightest. The plan dates (chosen mid-month, mid-day, well inside the window) are an order of magnitude better than the dense-window worst case -- the 5-date residual is a much tighter snapshot.

## Code Sites Updated (Diff Summary)

### `ketu/ephemeris/orbital.py` (+86, -11)

1. **Module header (new):** added 5 module-level private constants
   `_LILITH_MEAN_EPOCH_DEG`, `_LILITH_MEAN_RATE_DEG_PER_DAY`,
   `_LILITH_PERTURB_AMP_DEG`, `_LILITH_PERTURB_RATE_DEG_PER_DAY`,
   `_LILITH_PERTURB_PHASE_DEG`. Comprehensive docstring documenting v1.0
   legacy values, fit method, residual budget, and call sites.

2. **`ORBITAL_ELEMENTS` Lilith row (formerly line 146):** the M_dot column
   now references `_LILITH_MEAN_RATE_DEG_PER_DAY` (named constant) instead
   of the literal `0.1114040803`.

3. **`get_lilith_position` (formerly the `83.3532 + 0.1114040803 * d`
   block):** rewritten to use the new constants plus the sin()
   perturbation. New numpy-style docstring documents the v1.1 fit method
   and tolerance, with a See Also pointer to `LILITH_DEFINITION.md` and
   the harness.

### `ketu/ephemeris/planets.py` (+4, -2)

1. **Import (line 12):** added `_LILITH_MEAN_RATE_DEG_PER_DAY` to the
   import from `.orbital`.

2. **`calc_planet_position` Lilith branch (formerly line 153):**
   `lon_speed = 0.1114040803` -> `lon_speed = _LILITH_MEAN_RATE_DEG_PER_DAY`.
   Comment notes that perturbation contributes <1e-3 deg/day, out of scope
   for the speed-ratio heuristic.

3. **`avg_speeds[12]` (formerly line 458):** `0.111404` -> `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)`. Six-decimal precision preserved (consistent with neighboring `avg_speeds` entries like `0.524167` for Mars), value sourced from the named constant.

### `tests/test_lilith_cross_check.py` (+45)

Added a new section after `test_lilith_matches_swiss_ephemeris`:

- `REGRESSION_TOLERANCE_DEG = 0.005` constant with motivation comment
  (post-fit max of 0.002693 deg + ~85% safety margin).
- `test_lilith_regression_baseline(dt)` parametrized over the same 5
  `CROSS_CHECK_DATES`, computes `swe.calc_ut(jd, swe.MEAN_APOG)` reference
  at test time (NOT hardcoded), asserts `|delta| < REGRESSION_TOLERANCE_DEG`.
- Plan 03's import-pattern preserved exactly: `pytest.importorskip("swisseph")` runtime gate without binding, separate `import swisseph as swe` for mypy --strict, no `swe = pytest.importorskip(...)` rebinding introduced.

### `docs/LILITH_DEFINITION.md` (+88, -34)

- **Formula section:** rewritten with the v1.1 5-parameter form, full-precision constants documented in algebraic form. Subsection "Where the rate constant appears in the codebase" updated to reflect that rate is now a single private named constant in `orbital.py` instead of 4 duplicated literals; lists the 4 consumer sites.
- **History section:** removed the `[TO BE FILLED BY PLAN 04]` placeholder. Records: pre-fix MAX |delta|, primary signature (perigee/apogee 180 deg flip), secondary perturbation (~0.11 deg, ~1095-day period), epoch/rate/perturbation old vs new, the 4 code sites updated, post-fix MAX |delta| both at the 5 dates and over 55K daily samples, pointer to `UPGRADING.md` (Plan 05).

## Post-Fix Harness Run

```text
$ pytest tests/test_lilith_cross_check.py -v
collected 10 items

tests/test_lilith_cross_check.py::test_lilith_matches_swiss_ephemeris[1900-06-15T12:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_matches_swiss_ephemeris[1950-03-21T18:30:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_matches_swiss_ephemeris[2000-01-01T12:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_matches_swiss_ephemeris[2025-09-23T06:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_matches_swiss_ephemeris[2050-12-21T00:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_regression_baseline[1900-06-15T12:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_regression_baseline[1950-03-21T18:30:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_regression_baseline[2000-01-01T12:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_regression_baseline[2025-09-23T06:00:00+00:00] PASSED
tests/test_lilith_cross_check.py::test_lilith_regression_baseline[2050-12-21T00:00:00+00:00] PASSED

10 passed in 0.37s
```

## Existing Test Suite (No Regression)

```text
$ pytest tests/ -q
======================= 420 passed, 39 warnings in 9.15s =======================
Total coverage: 98.24%
```

420 = 410 (pre-Phase-8 baseline) + 5 (Plan 03 user-tolerance harness, now PASSING with v1.1 fix) + 5 (Plan 04 regression-baseline harness, NEW). Zero regressions.

The `tests/test_planets_coverage.py::test_lilith` speed-ratio test at lines 478-482 doesn't hardcode `0.111404`; it asserts `0.9 < abs(ratio) < 1.1`, which the new value `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)` (`0.111404`) trivially satisfies (ratio ~ 1.0).

## REGRESSION_TOLERANCE_DEG Choice

```python
REGRESSION_TOLERANCE_DEG = 0.005
```

Justification:

- Post-fit MAX |delta| over the 5 plan dates is `0.002693 deg`.
- Doubled (with safety margin), this is `~0.0054 deg`.
- Round down to `0.005 deg` for memorability and to give 1.85x slack.
- This is half of the user-facing `0.01 deg` tolerance, providing a clear "regression detected" signal: any future edit that widens delta past `0.005 deg` would be flagged before reaching the user-facing failure boundary.

The constant is a *test-only* threshold (lives in `tests/`); production users are still bound by `TOLERANCE_DEG = 0.01` in the canonical contract.

## Pointer to Plan 05

The CHANGELOG and UPGRADING templates from Plan 05 should embed:

- **Magnitude string:** "Mean Black Moon Lilith corrected: max longitude error reduced from 179.94 deg to under 0.01 deg over 1900-2050."
- **Concrete numerical examples (one per plan date):**

  | Date | v1.0 longitude | v1.1 longitude | Delta v1.0 -> v1.1 |
  | --- | ---: | ---: | ---: |
  | 1900-06-15T12:00:00+00:00 | 352.812244 | 172.874758 | -179.94 |
  | 1950-03-21T18:30:00+00:00 | 217.722980 |  37.629502 | -180.09 |
  | 2000-01-01T12:00:00+00:00 |  83.353200 | 263.467026 | +180.11 |
  | 2025-09-23T06:00:00+00:00 |  50.189492 | 230.090328 | +179.90 |
  | 2050-12-21T00:00:00+00:00 | 357.307261 | 177.413557 | -179.89 |

  (v1.0 column = legacy `83.3532 + 0.1114040803 * d` mod 360, taken from Plan 03 SUMMARY's Per-date deltas table; v1.1 column = the post-fix prediction from this plan.)

- **Migration note:** "Any chart, transit window, or aspect timeline computed against Lilith with v1.0 needs recomputation. Other body positions are unchanged. Cycles, harmonics, houses, and aspect calculations involving non-Lilith bodies are unaffected."

- **Backward-compat assessment:** breaking change for ANY consumer using Lilith positions; no compat shim provided -- v1.0's output was empirically wrong by 180 deg, not a calibration choice.

## Task Commits

Each task committed atomically:

1. **Task 1 (parse branch decision):** no files modified -- branch decision is recorded in this SUMMARY's "Branch Selected" section.
2. **Task 2 (fix formula across 4 sites):** `39e3a71` -- `fix(08-04): correct Lilith mean apogee formula across 4 plumbing sites`.
3. **Task 3 (regression-baseline harness):** `8af6085` -- `test(08-04): add regression-baseline harness pinning v1.1 Lilith fit`.
4. **Task 4 (LILITH_DEFINITION.md update):** `2bce430` -- `docs(08-04): update LILITH_DEFINITION.md Formula and History for v1.1 fix`.

Plan metadata commit (final, captures this SUMMARY + STATE update): added at end of plan execution.

## Decisions Made

- **Single source of truth for the rate constant:** all 4 plumbing sites now reference `_LILITH_MEAN_RATE_DEG_PER_DAY` declared once in `orbital.py`. Future fixes touch one declaration; sites 2-4 inherit. This eliminates the v1.0 drift risk that motivated Plan 01's "rate appears in 4 sites" cross-reference.

- **Pure linear correction is insufficient; need one trig term:** the residual after a perfect linear fit is `~0.124 deg`, 12x tolerance, with a sinusoidal signature at period ~1095 days. The plan's research §Pitfall 1 explicitly enumerated "frame/precession terms or ELP truncation" as candidates for a secondary residual. A single sin() perturbation term, jointly fitted with the secular constants, drops the residual to `0.0078 deg` (max over 55K samples) and `0.0027 deg` (max over the 5 cross-check dates) -- both under tolerance. This is consistent with how Chapront-style mean-element formulae in Meeus / Bureau des Longitudes ELP-2000 work: a base polynomial plus periodic perturbation series.

- **Joint NLS over 1900-2050 daily samples (55K points):** rather than fitting only on the 5 plan dates (which would over-fit to those 5), I fit on dense daily samples covering the full requirement window. The plan dates are an inside-the-window subset where the residual is actually tighter than the dense-window MAX -- so the 5-date pass is a *byproduct* of the wider fit, not a target.

- **`REGRESSION_TOLERANCE_DEG = 0.005`:** half of the user-facing tolerance, ~1.85x post-fit max. Wide enough to absorb floating-point noise and minor reference-implementation drift across pysweph versions; tight enough to catch any unintended edit to the v1.1 constants before the user-facing 0.01 deg threshold breaks.

- **`avg_speeds[12]` keeps 6-decimal precision via `round(...)`:** the surrounding `avg_speeds` dict uses 6-decimal values throughout (`0.524167` Mars, `0.083056` Jupiter, etc.); maintaining that convention while still inheriting from the source-of-truth named constant requires `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)`. Six-decimal precision is sufficient for the speed-ratio heuristic (which only needs ~10% accuracy).

## Deviations from Plan

### Auto-fixed issues / Rule 1 (Bug fix)

**1. [Rule 1 - Bug fix] Plan's three single-strategy branches (epoch-only, rate-only, polyfit) are insufficient -- need one trig perturbation term.**

- **Found during:** Task 2, after computing the linear fit of `swe.MEAN_APOG` over 1900-2050 daily samples.
- **Issue:** The plan's Task 2 enumerates three mutually exclusive correction strategies based on the error-shape diagnosis (constant offset / proportional / monotonic-with-intercept). Plan 03's diagnosis was "constant ~180 deg offset" + "secondary 0.11 deg residual." Applying any of the three pure-linear strategies yields max |delta| = `0.124 deg` over the dense window -- 12x the tolerance. Investigation showed the residual has a single dominant sinusoidal component at period ~1095 days (~3 sidereal years), amplitude ~0.116 deg.
- **Fix:** Augmented the formula with one sin() perturbation term: `lilith = E + R*d + A*sin(omega*d + phi)`. All five parameters fitted jointly via Nelder-Mead (xatol=1e-12, fatol=1e-12) starting from a linear+1-sinusoid initialization. This is consistent with the plan's "If both corrections are applied and max |delta| drops below 0.01 deg on all 5 dates, Plan 04 SUCCESS" goal -- the plan explicitly anticipated a multi-step correction.
- **Files modified:** `ketu/ephemeris/orbital.py` (added perturbation constants and the sin() term in `get_lilith_position`).
- **Commit:** `39e3a71`.
- **Plan-design impact:** zero. The plan's verify scripts use *structural* greps (named constants exist, ORBITAL_ELEMENTS row references them, planets.py imports them) and *numerical* assertions (constants differ from legacy, harness passes, mypy passes). All structural greps pass; all numerical assertions pass. The plan's frontmatter `must_haves` is satisfied at every bullet.
- **Pitfall identified:** the plan's three named branches assumed a single linear correction would suffice. In practice the secondary residual identified by Plan 03 (0.111 deg after the +180 deg correction) was sinusoidal, not a constant offset or rate error. Future Phase 8-style verification plans should account for "linear + N trig perturbations" as a fourth correction strategy when the secondary residual exceeds tolerance.

### Auto-fixed issues / Rule 2 (Missing critical functionality)

None -- no missing functionality was discovered.

### Auto-fixed issues / Rule 3 (Blocking issues)

None -- no environmental blockers (venv was healthy, swisseph importable, etc.).

### Authentication gates

None -- this plan was fully local (no network, no auth-gated tools).

**Total deviations:** 1 (Rule 1 fix, no architectural change, no plan-design impact, all `must_haves` satisfied).

## Issues Encountered

- **Sparse-sample np.unwrap fails:** the plan's Task 2 example code used `np.unwrap(np.deg2rad(lons))` on the 5 plan dates directly. With apogee mean motion of `0.1114 deg/day` and 50-year gaps between samples, each adjacent pair differs by ~2000 deg (5.5 full revolutions); `np.unwrap` cannot recover the integer cycle counts from 5 sparse points. Worked around by unwrapping using the legacy rate as a reference (multiplying `lons` mod 360 by appropriate `n_revs` to bring them close to the predicted continuous trajectory). The dense fitting path uses 30-day or 1-day sampling, where standard `np.unwrap` works correctly.

- **No environmental issues:** venv was healthy; `pip install -e .[test]` already done from Plan 02; pysweph 2.10.3.6 importable; mypy clean from prior phase.

## User Setup Required

None for this plan. Phase 8 ships with no new runtime dependencies; Lilith calculations work with the standard `pip install ketu` install. The harness still requires `pip install -e .[test]` to pull pysweph (already documented in `docs/LILITH_DEFINITION.md` and Plan 02's SUMMARY).

## Next Phase Readiness

**Ready for Plan 05 (`08-05-release-notes`):**

- All four code sites (orbital.py x 2, planets.py x 2) atomically updated and verified.
- Harness passes 10/10 (5 user-tolerance + 5 regression-baseline).
- Existing test suite green: 420 passed, no regressions.
- `docs/LILITH_DEFINITION.md` Formula and History sections rewritten; placeholder removed.
- Plan 05's CHANGELOG/UPGRADING templates can embed the magnitude string and the 5-row v1.0 -> v1.1 numerical-change table from this SUMMARY's "Pointer to Plan 05" section.
- Phase 8 success criterion #3 ("formula corrected if needed, with cross-check pinning the new values") is met.

## Self-Check

Verifying claims against disk:

- File created: `.planning/phases/08-lilith-verification-fix/08-04-SUMMARY.md` -- this file (verified by os.path.exists at write time).
- Files modified:
  - `ketu/ephemeris/orbital.py` -- contains `_LILITH_MEAN_EPOCH_DEG: float = 263.3521188770`, `_LILITH_MEAN_RATE_DEG_PER_DAY: float = 0.1114036699`, named constants referenced in formula and ORBITAL_ELEMENTS row.
  - `ketu/ephemeris/planets.py` -- imports `_LILITH_MEAN_RATE_DEG_PER_DAY` from `.orbital`; `lon_speed` and `avg_speeds[12]` reference it.
  - `tests/test_lilith_cross_check.py` -- contains `REGRESSION_TOLERANCE_DEG = 0.005` and `test_lilith_regression_baseline`.
  - `docs/LILITH_DEFINITION.md` -- placeholder removed; Formula has `263.3521188770`/`0.1114036699`/`0.1156754590`/`0.3287143373`/`96.6084061482`; History records v1.1 corrected with old vs new and 4 code sites.
- Commits:
  - `39e3a71` -- `fix(08-04): correct Lilith mean apogee formula across 4 plumbing sites` (post-Task-2).
  - `8af6085` -- `test(08-04): add regression-baseline harness pinning v1.1 Lilith fit` (post-Task-3).
  - `2bce430` -- `docs(08-04): update LILITH_DEFINITION.md Formula and History for v1.1 fix` (post-Task-4).
- Numerical claims:
  - `pytest tests/test_lilith_cross_check.py -v` -> 10 passed.
  - `pytest tests/ -q` -> 420 passed, 0 failed.
  - `mypy --strict ketu/ tests/test_lilith_cross_check.py` -> Success: no issues found in 23 source files.
  - 5-date max |delta| post-fix: `0.002693 deg` (computed in fit script).
  - Dense-window max |residual| post-fix: `0.007815 deg` (computed in fit script).

## Self-Check: PASSED

All claims in this summary verified against disk and against tool output captured during execution.

---

*Phase: 08-lilith-verification-fix*
*Plan: 04*
*Branch: FORMULA-CORRECTION*
*Completed: 2026-05-06*
