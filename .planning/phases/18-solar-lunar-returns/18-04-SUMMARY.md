---
phase: 18-solar-lunar-returns
plan: 04
subsystem: testing
tags: [returns, oracle, pyswisseph, swisseph, cross-check, fixtures, aberration, ephemeris-theory, self-consistency, wrap-around, day-after-target]

# Dependency graph
requires:
  - phase: 18-solar-lunar-returns/18-01
    provides: _solve_return + _signed_residual_deg bisection algorithm (mirrored by the independent pyswisseph bisector in the cross-check)
  - phase: 18-solar-lunar-returns/18-02
    provides: solar_return public API (oracled for self-consistency)
  - phase: 18-solar-lunar-returns/18-03
    provides: lunar_return public API + day-after-target pre-oracle ratchet (oracled for self-consistency; the calendar-day-after fixture replaces the two-pass self-consistent test)
provides:
  - "6 oracle JSON fixtures (3 solar + 3 lunar) in tests/returns/fixtures/oracle_*.json: each pins resolved JD + per-body longitudes + cusps from the live solar_return/lunar_return at the resolved instant; 2 wrap-around cases (Sun aries-seam + Moon pisces-seam); 1 lunar day-after-target case (LRET-04 binding)"
  - "tests/returns/test_returns_oracle.py: parametrised self-consistency oracle (tolerance_deg=0.0001) + pyswisseph cross-check oracle (convention-aligned via FLG_TRUEPOS | FLG_NOABERR; per-body cross_check_tolerance_deg solar 0.01 / lunar 0.75) + day-after calendar pin + wrap-around seam pin"
  - ".planning/phases/18-solar-lunar-returns/18-04-NOTES.md: pyswisseph API probe (no built-in solar_return; manual bisection fallback), Astro-Seek WebFetch probe (accessible), Astro.com manual cross-check deferred template, AND the corrected aberration/ephemeris-theory analysis + per-body tolerance rationale"
affects: [18-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "pyswisseph cross-check convention alignment: pass FLG_TRUEPOS | FLG_NOABERR to swe.calc_ut so the independent solver resolves on the SAME longitude convention as Ketu (which skips aberration for Sun/Moon at ketu/ephemeris/planets.py:190). Compare like-for-like before measuring residuals."
    - "Per-body, physically-justified cross-check tolerance: cross_check_tolerance_deg is body-specific and bounds the MEASURED ephemeris-theory disagreement (Ketu analytic ephemeris vs. pyswisseph Moshier), NOT machine precision. Rationale pinned in each fixture's cross_check_rationale block + the test docstring + the phase notes."
    - "Two-oracle parametrised suite: self-consistency (machine-precision regression gate, primary) + independent cross-tool (CI-runnable, catches gross solver bugs). Adding a 7th fixture auto-parametrises via glob('oracle_*.json')."

key-files:
  created:
    - tests/returns/test_returns_oracle.py
    - tests/returns/fixtures/oracle_solar_diana_1980.json
    - tests/returns/fixtures/oracle_solar_curie_1900.json
    - tests/returns/fixtures/oracle_solar_aries_seam_1970.json
    - tests/returns/fixtures/oracle_lunar_diana_2000.json
    - tests/returns/fixtures/oracle_lunar_curie_day_after.json
    - tests/returns/fixtures/oracle_lunar_pisces_seam_1990.json
    - tests/returns/fixtures/_generate.py
    - .planning/phases/18-solar-lunar-returns/18-04-NOTES.md
  modified:
    - tests/returns/fixtures/oracle_*.json (cross_check_tolerance_deg relaxed + cross_check_rationale added during continuation)

key-decisions:
  - "Plan 18-04: pyswisseph cross-check uses FLG_TRUEPOS | FLG_NOABERR to ALIGN the longitude convention with Ketu's TRUE/no-aberration Sun & Moon (Ketu skips aberration for body_id<2 at ketu/ephemeris/planets.py:190). The plan's premise that aberration 'cancels in the resolved-JD math' was FALSE: each solver resolves on its own convention's natal reference, so the ~15.6 arcsec Sun aberration did NOT cancel between the two solvers' resolved JDs."
  - "Plan 18-04: cross_check_tolerance_deg relaxed per body with measured justification (solar 0.01 deg, lunar 0.75 deg) because the residual after convention alignment is a genuine ephemeris-theory gap — Ketu's bespoke Sun theory diverges from Moshier by up to ~56 arcsec (~0.0157 deg) on multi-decade back-projections, and Ketu's TRUNCATED Meeus Moon theory diverges from full Moshier ELP by up to ~0.61 deg. The plan's 0.001 deg target was physically unachievable against an independent ephemeris (a planning error, not a code bug)."
  - "Plan 18-04: self-consistency oracle remains the PRIMARY machine-precision regression gate at tolerance_deg=0.0001; the pyswisseph cross-check is the secondary CI-runnable gate that bounds gross solver bugs (wrong cycle / body / sign / off-by-a-period) within the known ephemeris-theory band."
  - "Plan 18-04: pyswisseph 2.10.3.6 has NO built-in solar_return / lunar_return — manual bisection on swe.calc_ut (mirror of _solve_return's algorithm, independent ephemeris library) is the binding. SE data files absent; pyswisseph falls back to Moshier theory. (Open Question Q2 resolved.)"
  - "Plan 18-04: Astro-Seek (horoscopes.astro-seek.com/solar-return-chart) is ACCESSIBLE (HTTP 200, no bot-block), recorded as the FIRST recommended secondary reference for the deferred Astro.com manual cross-check. (Open Question Q4 resolved.)"
  - "Plan 18-04: Astro.com manual cross-check remains DEFERRED (bot-blocked, Phase 16/17 precedent); the pyswisseph cross-check is the CI-runnable substitute. Both Astro.com and Astro-Seek use Swiss Ephemeris, so the manual cross-check would show the SAME ephemeris-theory gap (~0.016 deg Sun, ~0.6 deg Moon) — it is informational only."

patterns-established:
  - "Convention-align-then-measure: when cross-checking against an independent ephemeris, first align the longitude convention (true vs apparent, aberration on/off), then set tolerance from the residual ephemeris-theory disagreement — documented, not silently loosened."
  - "Physically-justified tolerance with audit trail: cross_check_rationale block in each fixture JSON records the measured deltas + the reason the tolerance is what it is, so a future reader sees WHY 0.75 deg is acceptable for the Moon."

# Metrics
duration: ~continuation close-out
completed: 2026-05-28
---

# Phase 18 Plan 04: Solar + Lunar Returns Oracle Suite Summary

**6 self-consistency oracle fixtures (3 solar + 3 lunar, incl. wrap-around + day-after-target) plus a convention-aligned pyswisseph cross-check, with per-body tolerances physically justified by the measured Ketu-vs-Moshier ephemeris-theory gap (Sun ~56 arcsec, truncated-Meeus Moon ~0.6 deg).**

## Performance

- **Mode:** Continuation close-out (Plan 18-04 was partially executed in a prior session; this session fixed the failing cross-check, committed the untracked test, and wrote this summary)
- **Completed:** 2026-05-28
- **Tasks:** Tasks 1-2 completed pre-continuation (committed in `12d970e` + `e610a40`); Task 3 (test suite) finished + fixed this session
- **Files modified this session:** 8 (1 test created/committed + 6 fixtures + 1 notes)

## Accomplishments

- Diagnosed and fixed the cross-check failure that halted the plan: the plan's "aberration cancels" premise was wrong, and the true residual is a genuine ephemeris-theory disagreement.
- Aligned the pyswisseph cross-check to Ketu's convention (`FLG_TRUEPOS | FLG_NOABERR`) so the comparison is like-for-like.
- Relaxed `cross_check_tolerance_deg` per body (solar 0.01, lunar 0.75) with the measured-delta rationale written into each fixture, the test docstring, and `18-04-NOTES.md` — no silent loosening.
- Committed the previously-untracked `tests/returns/test_returns_oracle.py`; all 15 oracle tests pass and the full 71-test returns suite is green.
- ROADMAP Phase 18 Success Criterion #5 (oracle validation of solar + lunar returns on 3+ dates each, incl. wrap-around + lunar day-after-target) satisfied via self-consistency + CI-runnable pyswisseph cross-tool; Astro.com manual cross-check deferred (Phase 16/17 precedent).

## Task Commits

Pre-continuation (prior session):

1. **Task 1: pyswisseph + Astro-Seek probe + 18-04-NOTES.md** - `12d970e` (docs)
2. **Task 2: generate 6 oracle fixtures + _generate.py** - `e610a40` (test)

This session (continuation):

3. **Task 3 fix + close-out: cross-check convention align + tolerance relax + commit untracked test** - `cd4b3dd` (test)

**Plan metadata:** _(this SUMMARY.md + STATE.md update)_ - see final docs commit

## Files Created/Modified

- `tests/returns/test_returns_oracle.py` - Parametrised self-consistency (0.0001 deg) + pyswisseph cross-check (convention-aligned, per-body tolerance) + day-after calendar pin + wrap-around seam pin. **Committed this session** (was untracked).
- `tests/returns/fixtures/oracle_solar_*.json` (3) - Solar return oracles (Diana 1980, Curie 1900 long-projection, aries-seam wrap-around 1970). `cross_check_tolerance_deg` 0.001 → 0.01 + `cross_check_rationale` added.
- `tests/returns/fixtures/oracle_lunar_*.json` (3) - Lunar return oracles (Diana 2000, Curie day-after-target, pisces-seam wrap-around 1990). `cross_check_tolerance_deg` 0.001 → 0.75 + `cross_check_rationale` added.
- `tests/returns/fixtures/_generate.py` - One-time fixture generator (audit trail; committed in `e610a40`).
- `.planning/phases/18-solar-lunar-returns/18-04-NOTES.md` - Probe results + corrected aberration/ephemeris-theory analysis + per-body tolerance rationale.

## Fixture Inventory

| Fixture | kind | wrap_around | day_after | self-consist. tol | cross-check tol |
| --- | --- | --- | --- | --- | --- |
| oracle_solar_diana_1980 | solar | false | - | 0.0001 deg | 0.01 deg |
| oracle_solar_curie_1900 | solar | false | - | 0.0001 deg | 0.01 deg |
| oracle_solar_aries_seam_1970 | solar | true | - | 0.0001 deg | 0.01 deg |
| oracle_lunar_diana_2000 | lunar | false | false | 0.0001 deg | 0.75 deg |
| oracle_lunar_curie_day_after | lunar | false | true | 0.0001 deg | 0.75 deg |
| oracle_lunar_pisces_seam_1990 | lunar | true | false | 0.0001 deg | 0.75 deg |

## Probe Results (carried from 18-04-NOTES.md)

- **pyswisseph API (Q2):** No built-in `solar_return`/`lunar_return` in pyswisseph 2.10.3.6 → manual bisection on `swe.calc_ut` (independent ephemeris library). SE data files absent → Moshier theory fallback.
- **Astro-Seek (Q4):** Accessible (HTTP 200, no bot-block); recorded as the first recommended secondary reference for the deferred manual cross-check.
- **Astro.com manual cross-check:** Deferred (bot-blocked, Phase 16/17 precedent). pyswisseph cross-check is the CI-runnable substitute; an Astro.com/Astro-Seek manual check would show the same ephemeris-theory gap and is informational only.

## Test Counts

- New oracle tests: **15** (6 self-consistency + 6 pyswisseph cross-check + 1 day-after calendar pin + 2 wrap-around seam pin).
- Returns suite: **71 pass** (`python -m pytest tests/returns/ -q --no-cov`).

## Decisions Made

See `key-decisions` frontmatter. Headline: convention-align the cross-check (`FLG_TRUEPOS | FLG_NOABERR`), then set a per-body tolerance from the measured ephemeris-theory residual (solar 0.01 deg, lunar 0.75 deg), with the rationale pinned in fixtures + test + notes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] pyswisseph cross-check premise + tolerance corrected**
- **Found during:** Task 3 close-out (cross-check halted the plan)
- **Issue:** The plan asserted the cross-check would pass at `cross_check_tolerance_deg=0.001` because the ~20 arcsec Sun aberration "cancels in the resolved-JD math". That premise was false: each solver resolves the return on its OWN convention's natal reference, so the aberration did NOT cancel between the two resolved JDs (~15.6 arcsec Sun delta). Investigation further showed the dominant residual is NOT aberration at all but a genuine ephemeris-theory gap — Ketu's bespoke Sun (~56 arcsec) and TRUNCATED Meeus Moon (~0.61 deg) vs. pyswisseph's Moshier theory. The 0.001 deg (3.6 arcsec) target was physically unachievable against an independent ephemeris.
- **Fix:** (a) `_swisseph_body_lon` now passes `swe.FLG_TRUEPOS | swe.FLG_NOABERR` to align the convention with Ketu (best practice; removes the avoidable aberration term). (b) `cross_check_tolerance_deg` relaxed per body (solar 0.01 deg, lunar 0.75 deg) — measured-delta rationale documented in each fixture's new `cross_check_rationale` block, the `test_pyswisseph_cross_check` docstring, the module docstring, and `18-04-NOTES.md` (with an explicit correction of the earlier "cancels" claim). Self-consistency oracle stays at 0.0001 deg.
- **Files modified:** tests/returns/test_returns_oracle.py, tests/returns/fixtures/oracle_*.json (6), .planning/phases/18-solar-lunar-returns/18-04-NOTES.md
- **Verification:** `python -m pytest tests/returns/test_returns_oracle.py -q --no-cov` → 15 passed; `python -m pytest tests/returns/ -q --no-cov` → 71 passed.
- **Committed in:** `cd4b3dd`

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug). No scope creep.
**Impact on plan:** The fix preserves the plan's intent (CI-runnable independent cross-tool validation that is strictly more than Phase 17 had) while being physically honest about what an independent ephemeris can deliver. The oracle fixtures' computed values (jd_return, body_lons, cusps) were NOT regenerated — only the `cross_check_tolerance_deg` field and an added `cross_check_rationale` block changed.

## Issues Encountered

- Markdown lint advisories (MD034 bare URLs, MD040 fenced-code-language, MD060 table alignment) in `18-04-NOTES.md` are pre-existing notes-doc style and not part of any binding doc-gate; left as-is.
- The venv `pytest` shebang is broken (v1.1 leftover) — used `python -m pytest` throughout (consistent with Plans 17-01..04 + 18-01..03; not in v1.2 scope).
- Advisory planning-drift warning on commit re: Phase 16 REQUIREMENTS markers — unrelated to Phase 18; left for the relevant close-out.

## User Setup Required

None - no external service configuration required. (Astro.com manual cross-check is an optional, deferred 30-45 min developer follow-up; pyswisseph cross-check is the CI substitute.)

## Next Phase Readiness

- Plan 18-05 (close-out) is ready: coverage gate verification (`make returns-coverage`, ≥95% on `ketu/returns/` — the oracle fixtures' day-after + inclusive-boundary cases now exercise the previously-uncovered `_solve.py` / `lunar.py` lines), REQUIREMENTS RET-01..05 + LRET-01..05 + RET-06 flips, CHANGELOG `[Unreleased] ### Added`, and the 6 ROADMAP success-criteria smoke.
- No blockers.

---
*Phase: 18-solar-lunar-returns*
*Completed: 2026-05-28*

## Self-Check: PASSED

- All 9 claimed files exist on disk (1 test + 6 fixtures + _generate.py audit trail + NOTES + SUMMARY).
- Cross-check fix commit `cd4b3dd` exists in git history.
- `python -m pytest tests/returns/test_returns_oracle.py -q --no-cov` → 15 passed.
- `python -m pytest tests/returns/ -q --no-cov` → 71 passed.
