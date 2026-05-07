---
phase: 10-houses-module
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/ephemeris/time.py
  - tests/houses/__init__.py
  - tests/houses/test_lst_obliquity_precision.py
  - .planning/phases/10-houses-module/lst-audit-report.md
autonomous: true
plan_id: "10-01"
requirements:
  - HOU-01

must_haves:
  truths:
    - "GMST/LST precision is empirically measured against swe.sidtime over 1900-2100 BEFORE any houses code lands"
    - "Mean obliquity precision is empirically measured against swe.calc_ut(SE_ECL_NUT)[1] over 1900-2100 (already excellent — confirm, don't fix)"
    - "Decision documented in lst-audit-report.md: tighten GMST or accept current precision (with measured worst-case ASC error and headroom vs <1 arcmin spec)"
    - "If tightened: ketu.ephemeris.time.sidereal_time uses IAU 2006 GMST polynomial (Meeus 12.4) and matches swe.sidtime within 1 arcsec over 1900-2100"
    - "If not tightened: lst-audit-report.md justifies acceptance with measured worst-case ASC error multiplier × GMST drift < 60 arcsec at all polar lats sampled (66.5°, 70°, 80°)"
    - "tests/houses/test_lst_obliquity_precision.py asserts the chosen precision contract — fails CI if regressed"
    - "tests/houses/test_lst_obliquity_precision.py includes a polar-ASC regression fence: parametrized over the 5 sample dates at lat=66.5°, asserts |delta_asc| < 50 arcsec via swe.houses_armc isolation (10 arcsec headroom vs HOU-01 60-arcsec spec)"
    - "ASP-style state.md blocker 'LST/obliquity precision audit' is closed by this plan's completion"
  artifacts:
    - path: "ketu/ephemeris/time.py"
      provides: "sidereal_time() — possibly tightened to IAU 2006 GMST polynomial; signature unchanged (jd: float, longitude: float = 0.0) -> float"
      contains: "def sidereal_time"
    - path: "tests/houses/__init__.py"
      provides: "Empty marker file establishing tests/houses/ subpackage"
      min_lines: 0
    - path: "tests/houses/test_lst_obliquity_precision.py"
      provides: "Empirical precision assertions vs swisseph oracle for sidereal_time, mean_obliquity, longitude-offset linearity, AND polar-ASC regression fence at lat=66.5° (via swe.houses_armc) over 5+ dates spanning 1900-2100"
      contains: "def test_"
      min_lines: 90
    - path: ".planning/phases/10-houses-module/lst-audit-report.md"
      provides: "Audit decision document — empirical numbers + verdict (tighten | accept) + rationale tied to <1 arcmin HOU-01 spec"
      contains: "Verdict"
      min_lines: 40
  key_links:
    - from: "tests/houses/test_lst_obliquity_precision.py"
      to: "ketu.ephemeris.time.sidereal_time"
      via: "direct import + parametrized comparison vs swe.sidtime"
      pattern: "from ketu\\.ephemeris\\.time import sidereal_time"
    - from: "tests/houses/test_lst_obliquity_precision.py"
      to: "ketu.ephemeris.coordinates.mean_obliquity"
      via: "direct import + comparison vs swe.calc_ut(SE_ECL_NUT)"
      pattern: "mean_obliquity"
    - from: "tests/houses/test_lst_obliquity_precision.py"
      to: "swisseph oracle"
      via: "pytest.importorskip('swisseph') module gate (test-only dep, AGPL-safe; matches Phase 8 pattern)"
      pattern: "importorskip\\(.swisseph.\\)"
---

<objective>
Audit and (if needed) tighten Greenwich Mean Sidereal Time precision in `ketu.ephemeris.time.sidereal_time` so all downstream Placidus/Koch/Porphyry house calculations rest on a sub-arcsecond LST. Mean obliquity is already at ~0.05 arcsec (per research) — confirm with a test, do NOT touch.

Purpose: HOU-01 spec is "<1 arcmin Ascendant error vs Astro.com / Swiss Ephemeris." ASC error scales as ~2× GMST error at mid-latitudes (~2.5× at lat 66°). Research measured ketu's current GMST drift at +12.77″ at J2000 and -16.28″ at 1900-01-01. Worst-case ASC error today: ~33″ at lat 66° in 1900 — INSIDE spec but tight. This plan MEASURES the precision, then DECIDES (and records) whether to tighten.

State.md flags this as the Phase 10 blocker: "LST/obliquity precision audit (Phase 10 first task) — current ephemeris/time.py tuned for ~0.01°; houses need ~0.001°. Audit must precede implementation per HOU-01." This plan closes that blocker.

Output:
- `tests/houses/__init__.py` (empty marker — establishes the test subpackage so subsequent plans can drop tests in)
- `tests/houses/test_lst_obliquity_precision.py` — empirical regression tests vs swisseph oracle
- `.planning/phases/10-houses-module/lst-audit-report.md` — decision document recording empirical numbers and the tighten-vs-accept verdict
- `ketu/ephemeris/time.py::sidereal_time` — IAU 2006 polynomial form ONLY IF audit verdict says tighten
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/10-houses-module/10-RESEARCH.md

# The function under audit (current IAU 1982 form)
@ketu/ephemeris/time.py

# Reference for already-excellent obliquity (do NOT modify)
@ketu/ephemeris/coordinates.py

# Reference pattern for pytest.importorskip swisseph oracle gating (Phase 8 precedent)
@tests/test_lilith_cross_check.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Empirically measure GMST and obliquity drift, write audit report, decide tighten-vs-accept</name>
  <files>.planning/phases/10-houses-module/lst-audit-report.md</files>
  <action>
    Run from `venv/bin/activate`. Measure ketu's current `sidereal_time(jd, 0.0)` (returns degrees) vs `swe.sidtime(jd) * 15.0` (swisseph returns hours; multiply by 15 deg/hour to compare). Measure `mean_obliquity(jd)` (degrees) vs `swe.calc_ut(jd, swe.ECL_NUT)[0][1]` (degrees, mean obliquity at index 1 of returned tuple-of-floats).

    Sample dates (covering the v1.1 valid range 1900-2050 plus margin):
    - 1900-01-01 12h UT → jd ≈ 2415021.0
    - J2000 → jd = 2451545.0
    - 2024-06-21 0h UT (recent) → jd ≈ 2460482.5
    - 2050-12-31 12h UT → jd ≈ 2470204.0
    - 2100-01-01 12h UT → jd ≈ 2488069.5

    For each date, compute and record (in arcseconds, convert via `delta_deg * 3600`):
    - `gmst_drift_arcsec = (sidereal_time(jd, 0.0) - swe.sidtime(jd) * 15.0) * 3600`  (handle 360° wrap: subtract `round(d/360)*360` before scaling)
    - `obliquity_drift_arcsec = (mean_obliquity(jd) - swe.calc_ut(jd, swe.ECL_NUT)[0][1]) * 3600`

    Then compute the worst-case ASC error multiplier. ASC formula sensitivity: `dASC/dARMC ≈ |cos(asc - armc)| / [cos²(eps)·cos²(lat) + ...]` — empirically dominated by `~1/cos(lat)` for the latitude term. Sample three latitudes per date: 0°, 49° (Paris-like), 66.5° (polar boundary). For each (jd, lat) pair, compute swisseph's ASC twice — once with ketu's GMST (input as ARMC via `houses_armc`), once with swisseph's GMST. Record `asc_error_arcsec`.

    Write `.planning/phases/10-houses-module/lst-audit-report.md` with sections:

    1. **Methodology** — sample dates, measurement formula, swisseph version reported by `swe.version` (note: it's a date int, not semver).
    2. **GMST drift table** — 5 dates × {drift_arcsec}; include max |drift|.
    3. **Obliquity drift table** — 5 dates × {drift_arcsec}; should be ≤0.1 arcsec everywhere (already excellent per research §"Empirical baseline").
    4. **ASC error sensitivity table** — 5 dates × 3 lats × {asc_error_arcsec}; include max |asc_error|.
    5. **Spec comparison** — HOU-01 spec is <60 arcsec (1 arcmin). Compute headroom = 60 - max|asc_error|. If headroom > 30 arcsec at all polar samples, ACCEPT; if headroom < 30 arcsec OR negative anywhere, TIGHTEN.
    6. **Verdict** — single line: `Verdict: ACCEPT` or `Verdict: TIGHTEN`. Followed by 2-3 sentences justifying the call against the headroom rule.
    7. **If TIGHTEN: target formula** — IAU 2006 GMST (Meeus 2nd ed. eq. 12.4):
         `GMST = 24110.54841 + 8640184.812866·T + 0.093104·T² - 6.2e-6·T³` (seconds at 0h UT1; needs UT1 fraction-of-day added; convert to degrees via × 15/3600 → degrees). The current code uses the ALL-IN-ONE form `280.46061837 + 360.98564736629·d + 0.000387933·T² - T³/38710000` which is the IAU 1982 form; the difference is the T² coefficient (`+0.000387933` IAU 1982 vs `+0.0000258·T²` IAU 2006 reduced — verify against Meeus before coding).

    Use the script approach: write `scripts/audit_lst_obliquity.py` (NOT committed; one-off measurement; or just paste the Python session output). The deliverable is the markdown report, not the script.

    Anti-patterns to avoid:
    - Don't take "all good" on faith — measure ALL 5 dates and ALL 3 latitudes. Polar latitudes are the stress test.
    - Don't compare GMST in degrees vs hours without unit conversion (`swe.sidtime` returns hours, `sidereal_time` returns degrees — multiply hours × 15 = degrees).
    - Don't ignore the 360° wrap when computing drift: `delta = (a - b + 180) % 360 - 180` then × 3600 → arcsec.
    - Don't write the verdict before computing the headroom — the call must be data-driven, not vibes-based.
  </action>
  <verify>
    `cat .planning/phases/10-houses-module/lst-audit-report.md` shows all 7 sections populated, with concrete arcsec numbers in the three tables (no placeholders like "TBD"). The Verdict line is present and reads exactly "Verdict: ACCEPT" or "Verdict: TIGHTEN" — no other phrasing.

    The numbers must be reproducible: run the measurement Python snippet a second time → same values within 0.01 arcsec (sidereal_time is deterministic, no clock dependency).
  </verify>
  <done>
    Audit report exists at the specified path; all 5 sample dates measured for GMST and obliquity; all 3 latitudes measured for ASC sensitivity; max|drift| and max|asc_error| numbers stated; Verdict line is exactly one of ACCEPT or TIGHTEN; if TIGHTEN, the target IAU 2006 formula is written out with coefficients.
  </done>
</task>

<task type="auto">
  <name>Task 2: Apply tightening (if verdict=TIGHTEN) and create regression tests in tests/houses/</name>
  <files>ketu/ephemeris/time.py
tests/houses/__init__.py
tests/houses/test_lst_obliquity_precision.py</files>
  <action>
    Step A — Create `tests/houses/__init__.py` as an empty file (just the subpackage marker; one blank line is fine). This file establishes the `tests/houses/` test directory that all subsequent Phase 10 plans drop tests into.

    Step B — Create `tests/houses/test_lst_obliquity_precision.py`:

    - Module docstring: "HOU-01 precision regression tests for sidereal_time() and mean_obliquity() against swisseph oracle. The asserted tolerances reflect the audit verdict in lst-audit-report.md."
    - Use `pytest.importorskip("swisseph")` at module-level (returns the module) AND a separate `import swisseph as swe` for mypy --strict (matches Phase 8's `tests/test_lilith_cross_check.py` pattern). Document the dual-import in a comment: "module-level skip-if-missing gate + named import for type-checking; mypy honours [tool.mypy.overrides] swisseph.* ignore_missing_imports."
    - Parametrize the same 5 sample dates from Task 1 (1900, J2000, 2024, 2050, 2100).
    - Test 1 — `test_sidereal_time_matches_swisseph_within_tolerance(jd)`:
        - Compute `ketu_gmst_deg = sidereal_time(jd, 0.0)`
        - Compute `swe_gmst_deg = swe.sidtime(jd) * 15.0`
        - Compute `delta_arcsec = abs(((ketu_gmst_deg - swe_gmst_deg + 180) % 360) - 180) * 3600`
        - Assert `delta_arcsec < TOL_GMST_ARCSEC`. Set `TOL_GMST_ARCSEC = 1.0` if Task 1 verdict was TIGHTEN, else `TOL_GMST_ARCSEC = 20.0` (current measured worst-case ~16.3″ + headroom). The exact number lives in a module-level constant with a code comment citing lst-audit-report.md.
    - Test 2 — `test_mean_obliquity_matches_swisseph_within_tolerance(jd)`:
        - Compute `ketu_eps_deg = mean_obliquity(jd)`
        - Compute `swe_eps_deg = swe.calc_ut(jd, swe.ECL_NUT)[0][1]`  # tuple-of-floats, mean obliquity at index 1
        - Assert `abs(ketu_eps_deg - swe_eps_deg) * 3600 < TOL_OBLIQUITY_ARCSEC`. Set `TOL_OBLIQUITY_ARCSEC = 0.1` (research empirically measured ±0.05″; 0.1″ is 2× headroom — already-excellent confirmation, NOT a fix).
    - Test 3 — `test_sidereal_time_longitude_offset_is_pure_addition()`:
        - For jd = J2000 and three longitudes (0°, 90°E, -45°W), assert `sidereal_time(jd, lon) == (sidereal_time(jd, 0) + lon) % 360` within 1e-9 deg. (Cheap correctness check; catches any future bug where longitude is swapped or signed wrong.)
    - Test 4 — `test_asc_error_within_spec_at_polar_boundary(jd)` (parametrized over the 5 sample dates × `lat=66.5`):
        - The audit narrative captures the polar-ASC headroom argument (max worst-case ~33″ at lat 66°), but Tests 1-3 only fence GMST/obliquity drift directly. This test fences the resulting ASC error so any future regression is caught automatically. Threshold: 50.0 arcsec (10-arcsec headroom vs HOU-01 60-arcsec spec; intentionally tighter than spec so we hear about it before we ship).
        - For each `jd` in the 5 sample dates, with `lat = 66.5°`:
            - Compute `armc_ketu_deg = sidereal_time(jd, 0.0)` (ketu's GMST → ARMC at lon=0 is just GMST in degrees).
            - Compute `eps_ketu_deg = mean_obliquity(jd)`.
            - Feed BOTH into the SAME oracle call: `cusps_oracle, ascmc_oracle = swe.houses_armc(armc_ketu_deg, 66.5, eps_ketu_deg, b"P")` → `asc_oracle_at_ketu_armc = ascmc_oracle[0]`. (Using `houses_armc` not `houses_ex`: this isolates the ASC formula from any sidereal-time mismatch — both ketu and oracle see the same ARMC and obliquity.)
            - Then call the SAME oracle with swisseph's own ARMC: `armc_swe_deg = swe.sidtime(jd) * 15.0`; eps_swe = `swe.calc_ut(jd, swe.ECL_NUT)[0][1]`; `_, ascmc_swe = swe.houses_armc(armc_swe_deg, 66.5, eps_swe, b"P") → asc_swe = ascmc_swe[0]`.
            - The delta `delta_asc_arcsec = abs(((asc_oracle_at_ketu_armc - asc_swe + 180) % 360) - 180) * 3600` is the ASC error attributable to ketu's GMST + obliquity drift propagating through Placidus's ASC formula at the polar boundary.
            - Assert `delta_asc_arcsec < 50.0` with f-string error message: `f"jd={jd} lat=66.5 ASC error {delta_asc_arcsec:.3f} arcsec ≥ 50.0 (spec: 60.0)"`.
        - Use `pytest.importorskip("swisseph")` already at module level (Test 1 covers this); no extra gating needed. Document in a code comment that this test is the "automatic regression fence" referenced in lst-audit-report.md §5 and that swisseph's `houses_armc` accepts ARMC in degrees (not hours) — Pitfall 7 from research applies via the houses_ex path; `houses_armc` is the same units convention.
    - All assertions use `numpy.testing` style only if vectorizing; here scalars are fine — use plain `assert` with f-string error message including the actual delta in arcsec for fast triage.

    Step C — IF Task 1 verdict is TIGHTEN, modify `ketu/ephemeris/time.py::sidereal_time` to use the IAU 2006 form documented in lst-audit-report.md §7. Preserve the function signature `(jd: float, longitude: float = 0.0) -> float` exactly — no breaking changes. Write a numpydoc-style "Notes" section in the docstring: "Uses IAU 2006 GMST polynomial (Meeus 2nd ed. eq. 12.4); accuracy <1 arcsec vs Swiss Ephemeris over 1900-2100 (verified by tests/houses/test_lst_obliquity_precision.py)." Update the inline comment "GMST at 0h UT" to reflect the 2006 source. Do NOT change `mean_obliquity` (already excellent).

    Step D — IF Task 1 verdict is ACCEPT, leave `ketu/ephemeris/time.py` untouched. Document in the docstring "Notes" section: "GMST drift vs Swiss Ephemeris is up to ~16 arcsec at 1900-01-01 (~32 arcsec ASC error at lat 66.5°), well within HOU-01 <60 arcsec spec; tightening deferred (see lst-audit-report.md)." This is a docstring-only edit; the formula stays the IAU 1982 form.

    Anti-patterns to avoid:
    - Do NOT widen the test tolerance silently to make the test pass when the formula is broken. The TOL_* constants must reflect the audit verdict; if verdict was TIGHTEN, TOL_GMST_ARCSEC = 1.0 and the test FAILS until the tightening lands.
    - Do NOT add a swisseph runtime dep — `pytest.importorskip` MUST be the only gate (matches Phase 8 contract: pyswisseph is `[project.optional-dependencies].test`, never `[project].dependencies`).
    - Do NOT assert obliquity at <0.05 arcsec — current accuracy is ~0.05″, leave 2× headroom (0.1″) so tropospheric formula refinements in v1.2+ don't regress this gate.
    - Do NOT modify `mean_obliquity` "while we're here" — research is unambiguous: it's already at IAU 2006 accuracy. Touching it is scope creep that risks regression.
    - Do NOT add a `tests/houses/conftest.py` here — that's Plan 10-02's deliverable. This plan only creates `__init__.py` (package marker) + `test_lst_obliquity_precision.py` (the audit's regression test).
  </action>
  <verify>
    `pytest tests/houses/test_lst_obliquity_precision.py -v` runs and passes (skipped only if `pip install -e ".[test]"` was not run, in which case the importorskip kicks in). 4 tests total: Test 1 (5 dates), Test 2 (5 dates), Test 3 (single, 3 longitudes inside), Test 4 (5 dates) = 16 test cases pass.

    `mypy --strict ketu/ephemeris/time.py tests/houses/test_lst_obliquity_precision.py` is clean.

    `pytest tests/ -v` (full suite) — 488+ existing tests still pass; new 15 tests added cleanly. If verdict was TIGHTEN, sidereal_time output may shift by up to ~16 arcsec; verify no existing test in `tests/test_time_functions.py` or similar pinned the IAU 1982 output value to < 1 arcsec. If any breaks, that's a real signal — investigate (likely the existing test was loosely tolerant or was masking the imprecision).

    `python -c "from ketu.ephemeris.time import sidereal_time; print(sidereal_time(2451545.0, 0.0))"` runs without error.
  </verify>
  <done>
    `tests/houses/__init__.py` exists. `tests/houses/test_lst_obliquity_precision.py` exists with 4 tests asserting GMST <TOL_GMST_ARCSEC, obliquity <0.1 arcsec, longitude-offset linearity, AND polar-ASC regression fence at lat=66.5° <50 arcsec via swe.houses_armc isolation. All tests pass. If verdict was TIGHTEN: `ketu/ephemeris/time.py::sidereal_time` uses IAU 2006 polynomial and TOL_GMST_ARCSEC = 1.0. If verdict was ACCEPT: formula unchanged, TOL_GMST_ARCSEC = 20.0 (research worst-case + headroom), docstring notes updated. mypy --strict clean. State.md blocker "LST/obliquity precision audit" is resolved.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/houses/test_lst_obliquity_precision.py -v` passes (or skips wholesale if swisseph not installed — never partial-skip).
- `cat .planning/phases/10-houses-module/lst-audit-report.md` exists, contains numbers, contains "Verdict: ACCEPT" or "Verdict: TIGHTEN".
- `mypy --strict ketu/ephemeris/time.py tests/houses/test_lst_obliquity_precision.py` is clean.
- `pytest tests/` (full suite) shows 488+16 = 504+ tests pass; no regressions.
- `git log --oneline -5` shows the audit report committed in this plan's commit (plus formula change if verdict=TIGHTEN).
- The state.md blocker "LST/obliquity precision audit (Phase 10 first task)" is resolvable — i.e. on plan completion, the next planner reading state.md should be able to mark this blocker closed.
</verification>

<success_criteria>
- HOU-01 satisfied: ketu's sidereal_time and mean_obliquity precision is empirically measured against swisseph and either tightened or formally accepted with documented headroom.
- Subsequent plans (10-04 Placidus, 10-05 Koch) can compute ARMC = sidereal_time(jd, lon) and trust it to <1 arcsec (TIGHTEN) or <20 arcsec (ACCEPT) — the choice and its consequences are recorded in lst-audit-report.md.
- `tests/houses/` test subpackage exists and is wired into the pytest collection (`tests/houses/__init__.py` present).
- swisseph remains a test-only dep (verified by `grep -L swisseph ketu/` should match every file under ketu/ — no runtime imports added).
</success_criteria>

<output>
After completion, create `.planning/phases/10-houses-module/10-01-SUMMARY.md` documenting:
- The 5 sample dates × {GMST drift, obliquity drift} measurements (table)
- The 5 dates × 3 latitudes × ASC error sensitivity (table)
- Verdict (ACCEPT or TIGHTEN) and 1-paragraph rationale
- TOL_GMST_ARCSEC chosen (1.0 if TIGHTEN, 20.0 if ACCEPT) and why
- If TIGHTEN: diff summary of the time.py change (lines edited, formula reference)
- Polar-ASC regression fence (Test 4): max |delta_asc| at lat=66.5° across 5 dates, headroom vs 50-arcsec assertion threshold
- Confirmation that 488+16 tests pass and mypy --strict is clean
- Confirmation that state.md blocker "LST/obliquity precision audit" is closed
</output>
