---
phase: 08-lilith-verification-fix
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/LILITH_DEFINITION.md
autonomous: true

must_haves:
  truths:
    - "User opens docs/LILITH_DEFINITION.md and finds the exact formula Ketu currently ships (83.3532 + 0.1114040803 * d)"
    - "User reads the document and can identify the reference frame (tropical, ecliptic of date, geocentric, mean)"
    - "User finds explicit Chapront-Touze / Chapront / Francou citation pointing to ELP-2000 lunar theory"
    - "User finds the 0.01-degree tolerance justified by arithmetic (rate * time-equivalent), not by round-number convention"
    - "User finds a History section with a placeholder for the v1.0 -> v1.1 verification result (filled in by Plan 04)"
  artifacts:
    - path: "docs/LILITH_DEFINITION.md"
      provides: "Authoritative definition of Ketu's Lilith (Mean Apogee) computation"
      contains: "83.3532 + 0.1114040803"
      min_lines: 70
  key_links:
    - from: "docs/LILITH_DEFINITION.md"
      to: "ketu/ephemeris/orbital.py:591"
      via: "explicit formula citation matching the source line"
      pattern: "83\\.3532.*0\\.1114040803"
    - from: "docs/LILITH_DEFINITION.md"
      to: "Swiss Ephemeris SE_MEAN_APOG (constant value 12)"
      via: "named correspondence section"
      pattern: "SE_MEAN_APOG"
---

<objective>
Write `docs/LILITH_DEFINITION.md` from scratch as the authoritative reference for what Ketu's Lilith computation is, before any code is touched. This document is the contract the cross-check harness (Plan 03) tests against and the artifact a future maintainer reads to understand what changed in v1.1.

Purpose: Investigation-first ordering is mandatory (ROADMAP success criterion #1, REQUIREMENTS LIL-01). The definition must precede the harness, which must precede any conditional fix. Without this document there is no agreed reference for "correct."

Output: `docs/LILITH_DEFINITION.md` — single new markdown file in `docs/` (alongside `aspect_timelines.md`, `complex.md`).
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/08-lilith-verification-fix/08-RESEARCH.md
@ketu/ephemeris/orbital.py
@ketu/ephemeris/planets.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write LILITH_DEFINITION.md skeleton with formula, frame, source citation, tolerance, history placeholder</name>
  <files>docs/LILITH_DEFINITION.md</files>
  <action>
Create `docs/LILITH_DEFINITION.md` (new file). Use the skeleton from `08-RESEARCH.md` "Code Examples — `LILITH_DEFINITION.md` skeleton" verbatim as the structure, populated with the values the current codebase actually uses.

Required top-level sections (in this order):

1. **Title and one-line summary** — "Reference document for `ketu.ephemeris.orbital.get_lilith_position`."

2. **What Ketu Computes** — Body index 12, label `"Lilith"`, defined as the Mean Apogee of the Moon's orbit projected onto the ecliptic. State explicitly: this corresponds to Swiss Ephemeris's `SE_MEAN_APOG` (constant value `12`). Clarify that True / Osculating Apogee (`SE_OSCU_APOG`) is a separate quantity NOT implemented in v1.1 (deferred to v2 per LIL2-01).

3. **Formula** — Quote the exact current formula verbatim from `ketu/ephemeris/orbital.py:591`:

   ```
   lilith_lon = (83.3532 + 0.1114040803 * d) mod 360 degrees
   where d = JD_UT - 2451545.0  (days since J2000.0)
   ```

   - State `83.3532 deg`: mean longitude at J2000.0 (1 January 2000 12:00 UT).
   - State `0.1114040803 deg/day`: mean prograde rate ~ 40.69 deg/year.
   - State full revolution period: ~ 8.85 years (~ 3232.6 days).
   - Cross-reference the THREE codebase sites where the rate appears (research note 1):
     - `ketu/ephemeris/orbital.py:591` (longitude formula)
     - `ketu/ephemeris/orbital.py:146` (ORBITAL_ELEMENTS row, `0.1114040803`)
     - `ketu/ephemeris/planets.py:153` (lon_speed `0.1114040803`) and `:458` (avg_speeds `0.111404`)

4. **Reference Frame** — State explicitly:
   - Tropical, ecliptic of date (mean equinox of date)
   - Geocentric, mean orbit, projected onto ecliptic
   - Mean (smoothed); excludes short-period perturbations
   - Input is JD-UT (consumed by `swe.calc_ut`, NOT `swe.calc`)

5. **Source** — Cite Chapront-Touze, M.; Chapront, J.; Francou, G. — ELP-2000 lunar theory, Bureau des Longitudes (Paris). State: Swiss Ephemeris uses Moshier's reduction of ELP-2000 to a polynomial form covering 3000 BCE - 3000 CE. No `.se1` ephemeris files are required for `SE_MEAN_APOG`.

6. **Cross-Check** — Document the harness contract for Plan 03:
   - Test file: `tests/test_lilith_cross_check.py`
   - Reference: `swe.calc_ut(jd, swe.MEAN_APOG)`
   - Tolerance: `0.01 deg` (36 arcseconds)
   - Five dates spanning 1900, 1950, 2000, 2025, 2050
   - Run with: `pip install -e .[test]` then `pytest tests/test_lilith_cross_check.py -v`
   - State the test is gated by `pytest.importorskip("swisseph", minversion="2.10.3.6")` — skipped when `pysweph` is not installed.

7. **Tolerance Justification** — Explicit arithmetic:
   - `0.01 deg = 36 arcseconds`
   - Mean apogee rate: `0.111404 deg/day = 0.00464 deg/hour`
   - `0.01 deg / (0.111404 deg/day) ~ 0.0898 days ~ 2.15 hours ~ 129 minutes` of mean-apogee drift
   - Compare to user-facing precision: most published printed ephemerides quote Lilith to 0.1 deg; sign boundaries are 30 deg wide. 0.01 deg is one order of magnitude tighter than the user contract.
   - Conclusion: tolerance is conservative without being absurdly tight.

8. **AGPL & Test-Only Dependency Note** — State that `pysweph` (Swiss Ephemeris Python wrapper) is licensed AGPL/commercial; Ketu uses it only via `[project.optional-dependencies].test`. It is NEVER pulled into the runtime wheel. The two-venv runtime-isolation test (Plan 02) verifies this empirically.

9. **History** — Two bullets, the second a placeholder filled in by Plan 04:
   - `v0.x - v1.0`: formula `83.3532 + 0.1114040803*d` shipped; never externally verified.
   - `v1.1 (Phase 8)`: formula verified against Swiss Ephemeris. **Result: [TO BE FILLED BY PLAN 04 — either "agreement within X.XXXX deg on all sampled dates, no formula change" or "formula corrected to A + B*d, max error reduced from M to N deg"]**

DO NOT touch any code. DO NOT modify `orbital.py`, `planets.py`, `pyproject.toml`. This plan produces exactly ONE new file.

Use numpydoc-aware markdown formatting (fenced code blocks with `python` or `text`, ASCII-only math). Avoid Unicode that does not render in plain ASCII viewers (no degrees-sign Unicode, write `deg`).
  </action>
  <verify>
```bash
test -f docs/LILITH_DEFINITION.md && echo "EXISTS"
wc -l docs/LILITH_DEFINITION.md  # expect >= 70 lines
grep -F "83.3532" docs/LILITH_DEFINITION.md && echo "FORMULA EPOCH OK"
grep -F "0.1114040803" docs/LILITH_DEFINITION.md && echo "FORMULA RATE OK"
grep -F "SE_MEAN_APOG" docs/LILITH_DEFINITION.md && echo "SE CONSTANT NAMED"
grep -iE "chapront" docs/LILITH_DEFINITION.md && echo "SOURCE CITED"
grep -iE "tropical" docs/LILITH_DEFINITION.md && echo "FRAME STATED"
grep -iE "tolerance" docs/LILITH_DEFINITION.md && echo "TOLERANCE JUSTIFIED"
grep -iE "history|v1\\.1" docs/LILITH_DEFINITION.md && echo "HISTORY SECTION PRESENT"
# Code is untouched:
git status --porcelain ketu/ pyproject.toml | grep -v '^$' && echo "FAIL: code modified" || echo "CODE UNTOUCHED OK"
```
  </verify>
  <done>
`docs/LILITH_DEFINITION.md` exists with 9 named sections (What/Formula/Frame/Source/Cross-Check/Tolerance/AGPL/History/Title), all ten substantive grep checks pass, no code files modified, only `docs/LILITH_DEFINITION.md` appears in `git status --porcelain`.
  </done>
</task>

</tasks>

<verification>
- `git status --porcelain` shows exactly one new untracked file: `docs/LILITH_DEFINITION.md`
- All grep checks in Task 1 verify pass
- Document is ASCII-only (no Unicode rendering surprises)
- No imports of `swisseph` in any file (the dep is added in Plan 02)
</verification>

<success_criteria>
1. Single new file `docs/LILITH_DEFINITION.md` exists in the working tree.
2. Document contains all 9 named sections in stated order.
3. Document quotes the verbatim current Ketu formula and cites Chapront-Touze / Francou.
4. Tolerance justification is arithmetic, not "0.01 because the requirements said so."
5. History section has a placeholder explicitly marked for Plan 04.
6. Zero source files modified.
</success_criteria>

<output>
After completion, create `.planning/phases/08-lilith-verification-fix/08-01-SUMMARY.md` recording: file path created, line count, the 9 section headings, and confirmation that no code files were touched.
</output>
