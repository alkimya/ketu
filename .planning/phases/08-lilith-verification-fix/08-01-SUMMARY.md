---
phase: 08-lilith-verification-fix
plan: 01
subsystem: docs
tags: [lilith, mean-apogee, swiss-ephemeris, ELP-2000, chapront, AGPL, definition]

# Dependency graph
requires: []
provides:
  - "docs/LILITH_DEFINITION.md as authoritative reference for Ketu's Mean Apogee Lilith"
  - "Verbatim formula citation: 83.3532 + 0.1114040803 * d (orbital.py:591)"
  - "Named correspondence: Ketu body 12 == SE_MEAN_APOG (Swiss Ephemeris constant 12)"
  - "Tolerance contract for Plan 03 harness: 0.01 deg (36 arcsec, ~129 min drift)"
  - "AGPL test-only-dependency commitment for Plan 02 (pysweph never in runtime wheel)"
  - "History placeholder for Plan 04 verification result"
affects:
  - 08-02-test-only-dependency
  - 08-03-cross-check-harness
  - 08-04-conditional-formula-fix
  - 08-05-release-notes

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Investigation-first ordering: definition document precedes any code change"
    - "Named-quantity contract: Ketu body index aligned to Swiss Ephemeris constant"
    - "Tolerance derivation pattern: rate constant * time-equivalent (not round-number convention)"

key-files:
  created:
    - "docs/LILITH_DEFINITION.md"
  modified: []

key-decisions:
  - "Frame stated explicitly as tropical, ecliptic of date, geocentric, mean (input JD-UT)"
  - "Tolerance 0.01 deg justified arithmetically (~129 min mean apogee drift), one order of magnitude tighter than printed-ephemeris precision"
  - "True/Osculating Apogee (SE_OSCU_APOG) explicitly deferred to v2 per LIL2-01"
  - "All three rate-constant sites (orbital.py:591, orbital.py:146, planets.py:153) cross-referenced so Plan 04 cannot miss any"
  - "AGPL non-contamination commitment recorded in the definition, to be verified empirically by Plan 02's two-venv test"

patterns-established:
  - "Pattern 1: Definition-document-first phase ordering for any change to numerical output of a published library"
  - "Pattern 2: Cross-reference all duplicated constants in the definition so future fixes are atomic"
  - "Pattern 3: ASCII-only docs (no Unicode degree sign, no math glyphs) for plain-viewer compatibility"

# Metrics
duration: 2min
completed: 2026-05-06
---

# Phase 8 Plan 1: Lilith Definition Summary

**Authoritative `docs/LILITH_DEFINITION.md` written from scratch -- 209 lines, 9 named sections, verbatim formula `83.3532 + 0.1114040803 * d` cited against `SE_MEAN_APOG`, ELP-2000 / Chapront source named, 0.01 deg tolerance derived arithmetically, History section seeded with Plan 04 placeholder. Zero code touched.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-06T17:22:42Z
- **Completed:** 2026-05-06T17:24:24Z
- **Tasks:** 1
- **Files modified:** 1 (created)

## Accomplishments

- Created `docs/LILITH_DEFINITION.md` (209 lines, well above the 70-line minimum) -- the contract that the Plan 03 harness will test against and that Plan 04's potential formula change will update.
- All 9 plan-mandated sections present and ordered as specified: Title, What Ketu Computes, Formula, Reference Frame, Source, Cross-Check, Tolerance Justification, AGPL & Test-Only Dependency Note, History.
- Formula quoted verbatim from `ketu/ephemeris/orbital.py:591` (`83.3532 + 0.1114040803 * d`), with explicit cross-references to the three other call sites where the rate constant is duplicated (`orbital.py:146`, `planets.py:153`, `planets.py:458`) -- so a Plan 04 fix cannot accidentally miss any.
- Source attribution names Chapront-Touze, Chapront, and Francou explicitly, and identifies Moshier's reduction of ELP-2000-85 as Swiss Ephemeris's path -- not the pre-research vague "ELP-2000" placeholder.
- Tolerance section derives `0.01 deg` arithmetically: `0.01 / 0.111404 deg/day ~= 0.0898 days ~= 2.15 hours ~= 129 minutes` of mean apogee drift, then compares to printed ephemeris precision (0.1 deg), sign-boundary scale (30 deg), and Ketu aspect orbs (1-8 deg). Reviewer-defensible against "why 0.01?" pushback.
- AGPL note records the test-only commitment that Plan 02 will encode in `pyproject.toml` and verify in two fresh venvs.
- History closes with a literal `[TO BE FILLED BY PLAN 04 -- ...]` placeholder so Plan 04 can do a single search-and-replace.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write LILITH_DEFINITION.md skeleton with formula, frame, source citation, tolerance, history placeholder** - `596da4c` (docs)

## Files Created/Modified

- `docs/LILITH_DEFINITION.md` (created) -- 209 lines, ASCII-only, 9 named sections; authoritative reference for `ketu.ephemeris.orbital.get_lilith_position`. Contains verbatim formula, tropical/ecliptic-of-date/geocentric/mean frame statement, Chapront-Touze + Francou ELP-2000 citation, SE_MEAN_APOG correspondence (constant 12), Plan 03 cross-check contract (5 dates 1900-2050, 0.01 deg tolerance), arithmetic tolerance justification, AGPL test-only-dependency commitment, History placeholder for Plan 04.

## Decisions Made

- **Frame statement leans on `_ut` vs `calc`:** Explicitly documented that input is JD-UT (consumed by `swe.calc_ut`, not `swe.calc`) so Plan 03 cannot accidentally use the wrong API and inject a Delta-T error.
- **Listed all four rate-constant call sites, not just the formula site:** orbital.py:591 (formula), orbital.py:146 (ORBITAL_ELEMENTS), planets.py:153 (lon_speed), planets.py:458 (avg_speeds, truncated to 0.111404). Plan 04 cannot accidentally fix one and miss the others.
- **History placeholder is a literal sentinel string, not a TBD section:** Used `[TO BE FILLED BY PLAN 04 -- either "agreement within X.XXXX deg ..." or "formula corrected to A + B*d ..."]` so Plan 04 can do a deterministic find-and-replace.
- **ASCII-only enforced:** No Unicode degree sign, no Greek letters in math, no em-dashes. Verified with `python3` ord-check pass. Matches existing `docs/aspect_timelines.md` and `docs/complex.md` conventions.

## Deviations from Plan

None - plan executed exactly as written.

The plan specified 9 sections, a verbatim formula citation, a specific Chapront source attribution, a 0.01 deg tolerance arithmetic derivation, an AGPL commitment, and a Plan 04 History placeholder. All ten substantive `verify` grep checks passed on first run, and `git status --porcelain ketu/ pyproject.toml` returned empty, confirming zero source files were modified.

---

**Total deviations:** 0
**Impact on plan:** None - clean execution.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for Plan 02 (`08-02-test-only-dependency`):

- The AGPL commitment in `LILITH_DEFINITION.md` Section 8 is now the contract Plan 02 must encode in `pyproject.toml` (`[project.optional-dependencies] test = ["pysweph>=2.10.3.6"]`) and verify with the two-venv runtime-isolation test.
- The Cross-Check section (Section 6) names the test file (`tests/test_lilith_cross_check.py`), the reference call (`swe.calc_ut(jd, swe.MEAN_APOG)`), the tolerance (`0.01 deg`), the date range (1900, 1950, 2000, 2025, 2050), and the install command (`pip install -e .[test]`) -- the full contract Plan 03 will implement.
- The History section is pre-seeded with the Plan 04 placeholder, so Plan 04 has a single search-and-replace to land its result.
- No blockers. Plans 02 and 03 can run sequentially; Plan 04 is conditional on Plan 03's empirical outcome.

## Self-Check: PASSED

Verified all claims in this summary against disk:

- `docs/LILITH_DEFINITION.md` exists (209 lines, matches claim).
- `.planning/phases/08-lilith-verification-fix/08-01-SUMMARY.md` exists.
- Commit `596da4c` exists in `git log --all`.

---

*Phase: 08-lilith-verification-fix*
*Completed: 2026-05-06*
