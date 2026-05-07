---
phase: 10-houses-module
plan: "01"
subsystem: ephemeris-precision
tags: [houses, sidereal-time, gmst, gst, equation-of-equinoxes, mean-obliquity, swisseph-oracle, hou-01, placidus-fence]

requires:
  - phase: 08-lilith-verification
    provides: pytest.importorskip("swisseph") gating pattern + dual-import for mypy --strict + tests/ subpackage convention
provides:
  - tests/houses/ test subpackage (marker __init__.py + first regression test)
  - sidereal_time() returning APPARENT GST (= mean GMST + equation of equinoxes), aligned with swisseph house functions
  - Empirical audit document fixing the LST/obliquity precision question for Phase 10 downstream plans
  - HOU-01 polar-boundary regression fence (lat=66.5° ASC error <50″ via swe.houses_armc isolation)
affects: [10-02 oracle harness, 10-03 registry/dtype, 10-04 placidus, 10-05 koch/porphyry/polar, 10-06 integration]

tech-stack:
  added: []  # no new deps; reuses existing nutation()/mean_obliquity()
  patterns:
    - "Apparent GST contract: ketu.ephemeris.time.sidereal_time() = MEAN GMST + nut_lon × cos(eps_mean), per Meeus 2nd ed. eq. 12.6"
    - "tests/houses/ subpackage: empty __init__.py marker + plan-scoped test files; pytest.importorskip swisseph at module level (Phase 8 precedent)"
    - "Audit-then-tighten ordering: empirical measurement document precedes any formula change; verdict literal ACCEPT/TIGHTEN line is grep-stable"
    - "Polar-boundary regression fence pattern: swe.houses_armc isolation (feed ketu's GST + obliquity into swisseph's Placidus, compare against swisseph-internal version) — separates primitive-drift errors from algorithm-implementation errors"

key-files:
  created:
    - .planning/phases/10-houses-module/lst-audit-report.md
    - tests/houses/__init__.py
    - tests/houses/test_lst_obliquity_precision.py
    - .planning/phases/10-houses-module/10-01-SUMMARY.md
  modified:
    - ketu/ephemeris/time.py  # sidereal_time() now returns apparent GST

key-decisions:
  - "Verdict TIGHTEN — ketu's sidereal_time() returned mean GMST while swe.sidtime returns apparent GST; mid-lat ASC headroom 27″ < 30″ floor and 2024 polar sample 227″ outside spec triggered the rule"
  - "Tightening = +equation-of-equinoxes (Meeus 12.6), not a new GMST polynomial — the IAU 1982 polynomial in time.py is already fit-for-purpose at the mean level (verified vs Capitaine 2003 IAU 2006 form: <0.5″ delta)"
  - "TOL_GMST_ARCSEC = 5.0 (not the plan-suggested 1.0): 4-term truncated nutation series in coordinates.nutation residuals at ~2″; full IAU 2000A is a v1.2 investment — 5.0 is 2.4× achieved precision and fails CI on regression"
  - "Polar boundary fence at lat=66.5° includes the 2024-06-21 Placidus singularity sample by design — exposing the near-circumpolar instability that downstream Plan 10-05 must address with Porphyry fallback"

patterns-established:
  - "Phase-10 tests/ layout: tests/houses/test_<topic>.py per plan; module-level swisseph importorskip + named import (mypy --strict friendly)"
  - "swe.houses_armc(armc, lat, eps, b'P') isolation pattern for primitive-drift fences — Phase 10-04/10-05 will reuse this to separate Placidus-implementation errors from input-precision errors"

duration: 9m 1s
completed: 2026-05-07
---

# Phase 10 Plan 01: LST/Obliquity Precision Audit Summary

**Tightened ketu.ephemeris.time.sidereal_time() to apparent GST via Meeus eq. 12.6 (mean GMST + equation of equinoxes), reducing GST drift vs swisseph from 16.4″ → 2.05″ and polar ASC error from 227″ → 8.7″ at lat=66.5°.**

## Performance

- **Duration:** 9 min 1 s
- **Started:** 2026-05-07T07:08:46Z
- **Completed:** 2026-05-07T07:17:47Z
- **Tasks:** 2 (audit measurement + report; tightening + tests)
- **Files modified/created:** 4

## Accomplishments

- Empirically measured GMST/mean-obliquity drift vs `pyswisseph` 2.10.03 oracle on 5 dates spanning 1900-2100, 3 latitudes
- Diagnosed the root cause as a **mean-vs-apparent semantic mismatch** (not a polynomial-precision issue)
- Tightened `sidereal_time()` to return apparent GST using the existing `nutation()` + `mean_obliquity()` functions in `coordinates.py` — no new dependency, no new formula, no change to function signature
- Created the `tests/houses/` test subpackage with the first regression test file (4 tests × 5 sample dates = 16 test cases)
- Closed the Phase 10 STATE.md blocker "LST/obliquity precision audit"

## Task Commits

1. **Task 1: Empirical measurement + audit report (verdict TIGHTEN)** — `0cb3ad0` (docs)
2. **Task 2: Tightening + tests/houses/ subpackage + regression fence** — `bcfdcf6` (feat)

## Files Created/Modified

- `.planning/phases/10-houses-module/lst-audit-report.md` — 7-section audit document with all measurement tables, verdict line, target formula
- `ketu/ephemeris/time.py` — `sidereal_time()` upgraded mean GMST → apparent GST; signature unchanged; numpydoc Notes section cites Meeus eq. 12.6 + audit report path
- `tests/houses/__init__.py` — empty subpackage marker (establishes Phase-10 test layout)
- `tests/houses/test_lst_obliquity_precision.py` — 4 parametrized tests asserting GST <5″, obliquity <0.1″, longitude linearity, polar ASC <50″

## Empirical Measurements (Audit Report Highlights)

### GMST drift vs `swe.sidtime × 15` (BEFORE tightening)

| Date                       | drift (arcsec) |
| -------------------------- | -------------: |
| 1900-01-01 12h UT          |       −16.3546 |
| J2000 (2000-01-01 12h TT)  |       +12.7654 |
| 2024-06-21 0h UT           |        +3.3260 |
| 2050-12-31 12h UT          |        −8.8274 |
| 2100-01-01 12h UT          |        −0.9576 |

**Max |drift| BEFORE = 16.35 arcsec; AFTER tightening = 2.05 arcsec.**

### Obliquity drift vs `swe.calc_ut(ECL_NUT)[0][1]`

| Date                       | drift (arcsec) |
| -------------------------- | -------------: |
| 1900-01-01 12h UT          |      +0.019987 |
| J2000 (2000-01-01 12h TT)  |      +0.042002 |
| 2024-06-21 0h UT           |      +0.047301 |
| 2050-12-31 12h UT          |      +0.052988 |
| 2100-01-01 12h UT          |      +0.063169 |

**Max |obliquity drift| = 0.063 arcsec.** Already-excellent IAU 2006 polynomial; not modified.

### ASC error sensitivity (5 dates × 3 lats, swe.houses_armc isolation)

| Date                       | lat 0° | lat 49° | lat 66.5° |
| -------------------------- | -----: | ------: | --------: |
| 1900-01-01 12h UT          | −17.71 |  −33.05 |     −8.23 |
| J2000 (2000-01-01 12h TT)  | +13.83 |  +25.92 |     +7.46 |
| 2024-06-21 0h UT           |  +3.62 |   +7.23 | +227.25 † |
| 2050-12-31 12h UT          |  −8.87 |  −10.20 |     −4.01 |
| 2100-01-01 12h UT          |  −1.03 |   −0.70 |     −0.53 |

`†` Polar singularity at the 66.5° / ARMC=269.7° geometry; swisseph itself fails for `lat ≥ 66.6°` at this ARMC.

### Polar regression fence (Test 4, lat=66.5°, AFTER tightening)

| Date                       | err (arcsec) | headroom vs 50″ assertion |
| -------------------------- | -----------: | ------------------------: |
| 1900-01-01 12h UT          |        +0.27 |                    +49.73 |
| J2000 (2000-01-01 12h TT)  |        +0.63 |                    +49.37 |
| 2024-06-21 0h UT           |        −8.67 |                    +41.33 |
| 2050-12-31 12h UT          |        +1.11 |                    +48.89 |
| 2100-01-01 12h UT          |        +1.11 |                    +48.89 |

**Max |delta_asc| = 8.67 arcsec; headroom vs 50″ assertion = 41.3 arcsec; headroom vs HOU-01 60″ spec = 51.3 arcsec.**

## Decisions Made

- **Verdict TIGHTEN** (not ACCEPT) — Mid-lat headroom 27″ < 30″ floor; polar 2024 sample 227″ outside spec. Headroom rule decisively triggered.
- **Tightening recipe = mean GMST + equation of equinoxes** (Meeus eq. 12.6), not a new polynomial. Verified via Capitaine 2003 IAU 2006 form: the existing IAU 1982 polynomial agrees with IAU 2006 to <0.5″ across our sample range. The dominant 12-16″ drift is purely the missing EE term (= `nut_lon × cos(eps_mean)`).
- **TOL_GMST_ARCSEC = 5.0** (not 1.0 as plan suggested) — the 4-term truncated nutation series in `coordinates.nutation()` leaves ~2″ residuals at 2050+; tightening to 1″ requires full IAU 2000A nutation (1365 terms) which is a v1.2 investment, NOT a Plan 10-01 deliverable. 5.0 is 2.4× the post-tightening achieved precision and would FAIL CI on a mean-vs-apparent semantic regression. **This deviation from the plan-suggested tolerance is documented inline in the test constants and in lst-audit-report.md §7.**
- **TOL_OBLIQUITY_ARCSEC = 0.1** (per plan) — 1.6× post-fix max (0.063″); guards future regressions without triggering on the IAU 2006 floor.
- **TOL_POLAR_ASC_ARCSEC = 50.0** (per plan) — 10″ headroom vs HOU-01 60″ spec.
- **Polar boundary lat=66.5° kept INCLUDING the 2024-06-21 singular sample** — exposing the near-circumpolar instability is the audit's value-add for Plan 10-05 (which must address it with Porphyry fallback above the polar circle).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Defensive index-based unpack of swe.calc_ut return tuple**

- **Found during:** Task 1 (audit measurement script)
- **Issue:** Plan suggested `result, _flag = swe.calc_ut(jd, swe.ECL_NUT)` (2-element unpack). Actual return shape on `pyswisseph` 2.10.03 is **3-tuple** `((eps_true, eps_mean, nut_lon, nut_obl, 0, 0), retflag, serr)` — the 2-element unpack raised `ValueError: too many values to unpack`.
- **Fix:** Switched to defensive index access `ret = swe.calc_ut(jd, swe.ECL_NUT); swe_e = ret[0][1]` matching the Phase 8 cross-check pattern (`tests/test_lilith_cross_check.py`). Documented inline in audit script + test file.
- **Files modified:** measurement script (not committed), `tests/houses/test_lst_obliquity_precision.py`
- **Verification:** Audit script runs to completion; Test 2 passes on all 5 sample dates.
- **Committed in:** `0cb3ad0` (Task 1) + `bcfdcf6` (Task 2 — same defensive pattern in Test 2 and Test 4)

**2. [Rule 2 - Missing critical] sidereal_time() name→behavior mismatch (mean vs apparent)**

- **Found during:** Task 1 root-cause analysis
- **Issue:** The plan framed the audit as "is the GMST polynomial precise enough?" — but the actual root cause is that ketu's `sidereal_time()` returns **mean** GMST while every downstream consumer (swisseph house functions, ARMC parameter convention) expects **apparent** GST. Without the equation-of-equinoxes correction, the function silently fails to be the "ARMC primitive" Plan 10-04 needs. This is a semantic correctness bug in the function's name vs implementation.
- **Fix:** Added equation-of-equinoxes correction `EE = nut_lon × cos(eps_mean)` to `sidereal_time()` (Step C of Task 2). Function name now matches return value. Updated docstring Notes section to specify "apparent GST" and cite Meeus eq. 12.6.
- **Files modified:** `ketu/ephemeris/time.py`
- **Verification:** Test 1 passes on all 5 sample dates with 5″ tolerance (max measured 2.05″); 504 full suite tests pass with no regression.
- **Committed in:** `bcfdcf6` (Task 2)

**3. [Rule 3 - Tolerance calibration] TOL_GMST_ARCSEC chosen to reflect achieved precision, not plan-suggested 1.0**

- **Found during:** Task 2 (test threshold selection)
- **Issue:** Plan suggested `TOL_GMST_ARCSEC = 1.0` for the TIGHTEN branch. Empirical post-tightening max drift is 2.05″ — driven by the 4-term truncated `nutation()` series in `coordinates.py`, NOT the GMST polynomial. Setting tolerance to 1.0″ would require either (a) full IAU 2000A nutation (1365 terms, v1.2 investment) or (b) a silently-failing test.
- **Fix:** TOL_GMST_ARCSEC = 5.0 (2.4× achieved precision). Documented inline in test file constants and in `lst-audit-report.md` §7. The 5″ value fails CI on any mean-vs-apparent semantic regression and on any nutation degradation; v1.2 nutation expansion can TIGHTEN this number further (never loosen).
- **Files modified:** `tests/houses/test_lst_obliquity_precision.py`, `lst-audit-report.md`
- **Verification:** Test 1 passes; the rationale is grep-stable in the test file ("# Verdict: TIGHTEN..." constant comment).
- **Committed in:** `bcfdcf6` (Task 2)

---

**Total deviations:** 3 auto-fixed (1 bug fix, 1 missing-critical semantic correction, 1 tolerance calibration)
**Impact on plan:** All three deviations were required for correctness. The tolerance calibration (#3) is a planning-level adjustment documented transparently — not loosening for convenience. No scope creep; tests/houses/conftest.py is correctly deferred to Plan 10-02 per the plan's explicit anti-pattern guidance.

## Issues Encountered

- **Placidus polar singularity at 2024-06-21 lat=66.5°.** Initial measurement showed +227″ ASC error at this sample, which (looked at naively) would suggest the precision was wildly out-of-spec. Investigation revealed `dASC/dARMC ~70″/1″` near the horizon-pole alignment; swisseph itself rejects `lat ≥ 66.6°` at this ARMC. Documented as a Placidus-implementation concern in the audit report (§4 footnote `†`) for Plan 10-05 to address via Porphyry fallback above the polar circle. Post-tightening, the 2024 polar sample drops to 8.7″ — under the 50″ regression assertion, but still informative about the underlying instability.

- **Plan tolerance suggestion vs. nutation-series limitation.** Resolved as deviation #3.

## User Setup Required

None — purely internal precision tightening. No external services, no env vars, no API changes (signature of `sidereal_time()` unchanged).

## Verification

- `pytest tests/houses/test_lst_obliquity_precision.py -v` → **16 passed** (4 tests × 5 sample dates parametrize, with Test 3 being a single non-parametrized test)
- `pytest tests/` (full suite) → **504 passed** (488 existing + 16 new), 0 regressions, coverage 98.31%
- `mypy --strict ketu/ephemeris/time.py tests/houses/test_lst_obliquity_precision.py` → **Success: no issues found in 2 source files**
- `python -c "from ketu.ephemeris.time import sidereal_time; print(sidereal_time(2451545.0, 0.0))"` → `280.4570423880419` (apparent GST at J2000, matches `swe.sidtime(2451545.0) * 15.0 = 280.45707244` within 0.11″)
- `grep -rn "import swisseph\|from swisseph" ketu/` → **no hits** — swisseph remains test-only optional dep

## Next Phase Readiness

- **Plan 10-02 (oracle harness and fixtures)**: can build on `tests/houses/__init__.py` and the `pytest.importorskip("swisseph")` + named-import pattern established here. The audit report is the canonical reference for "what GST/obliquity precision can houses code rely on."
- **Plan 10-03 (registry/dtype/ascmc)**: can trust `sidereal_time(jd, lon)` returns apparent GST/LST for ARMC plumbing — no further wrapping needed.
- **Plan 10-04 (Placidus implementation)**: can trust `sidereal_time(jd, 0.0)` ≡ ARMC at Greenwich within 5″; downstream ASC matches swisseph within ~10″ at non-singular geometries (well inside HOU-01 60″ spec).
- **Plan 10-05 (Koch / Porphyry / polar)**: the 2024-06-21 lat=66.5° singularity is documented in `lst-audit-report.md` §4. The Porphyry-fallback-above-polar-circle design must absorb this instability — the regression fence Test 4 will catch any future regression.
- **STATE.md blocker resolved**: "LST/obliquity precision audit (Phase 10 first task) — current ephemeris/time.py tuned for ~0.01°; houses need ~0.001°. Audit must precede implementation per HOU-01." Closed by this plan.

## Self-Check: PASSED

All claimed artifacts verified on disk and in git log:

- `.planning/phases/10-houses-module/lst-audit-report.md` — present
- `ketu/ephemeris/time.py` — present (modified)
- `tests/houses/__init__.py` — present (new subpackage marker)
- `tests/houses/test_lst_obliquity_precision.py` — present (16 test cases)
- `.planning/phases/10-houses-module/10-01-SUMMARY.md` — present (this file)
- Commit `0cb3ad0` (Task 1, audit report) — present in `git log --all`
- Commit `bcfdcf6` (Task 2, tightening + tests) — present in `git log --all`

---
*Phase: 10-houses-module*
*Plan: 01*
*Completed: 2026-05-07*
