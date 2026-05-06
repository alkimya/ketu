---
phase: 08-lilith-verification-fix
plan: 03
type: execute
wave: 2
depends_on:
  - "08-01"
  - "08-02"
files_modified:
  - tests/test_lilith_cross_check.py
autonomous: true

must_haves:
  truths:
    - "User runs `pip install -e .[test]` and then `pytest tests/test_lilith_cross_check.py -v` and sees 5 parametrized test cases either all PASS (delta < 0.01 deg on all dates) or one or more FAIL with explicit Ketu/swe/delta values reported"
    - "User runs `pytest tests/` (no [test] extra installed) and sees the harness module reported as SKIPPED, not failed"
    - "User reads the test file and sees TOLERANCE_DEG = 0.01 named as a module constant with arithmetic justification in the comment, not a magic number"
    - "User reads the test file and sees `swe.calc_ut` (NOT `swe.calc`) used exclusively"
    - "User opens the recorded harness output (in SUMMARY.md) and sees the EMPIRICAL MAX ERROR across all 5 dates as a single number (e.g. `max |delta| = 0.0034 deg`); this number determines whether Plan 04 runs or is skipped"
  artifacts:
    - path: "tests/test_lilith_cross_check.py"
      provides: "Parametrized cross-check of get_lilith_position vs swe.MEAN_APOG on 5 dates spanning 1900-2050"
      exports: ["test_lilith_matches_swiss_ephemeris", "_signed_circular_diff", "TOLERANCE_DEG", "CROSS_CHECK_DATES"]
      contains: "swe.MEAN_APOG"
      min_lines: 60
  key_links:
    - from: "tests/test_lilith_cross_check.py"
      to: "ketu.ephemeris.orbital.get_lilith_position"
      via: "direct import + per-date call"
      pattern: "from ketu\\.ephemeris\\.orbital import get_lilith_position"
    - from: "tests/test_lilith_cross_check.py"
      to: "swisseph.calc_ut(jd, swisseph.MEAN_APOG)"
      via: "reference computation per date"
      pattern: "swe\\.calc_ut\\([^,]+,\\s*swe\\.MEAN_APOG\\)"
    - from: "tests/test_lilith_cross_check.py"
      to: "ketu.ephemeris.time.utc_to_julian"
      via: "JD-UT construction (matches calc_ut input contract)"
      pattern: "utc_to_julian"
    - from: "test module"
      to: "pytest skip when pysweph absent"
      via: "pytest.importorskip at module top"
      pattern: "pytest\\.importorskip\\(\"swisseph\""
---

<objective>
Write `tests/test_lilith_cross_check.py` — a parametrized pytest harness that compares Ketu's `get_lilith_position(jd)` against Swiss Ephemeris's `swe.calc_ut(jd, swe.MEAN_APOG)` on 5 dates spanning 1900, 1950, 2000, 2025, 2050 with explicit `TOLERANCE_DEG = 0.01`. Run the harness. Record the empirical max error. The numerical result of this run drives the conditional fork in Plan 04.

Purpose: REQUIREMENTS LIL-02 + ROADMAP success criterion #2. This is the entire empirical content of Phase 8 — every other plan exists to support, document, or react to what this harness reports.

Output: One new test file + a recorded measurement (max |delta| in degrees across 5 dates) carried forward in SUMMARY.md to gate Plan 04.
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
@.planning/phases/08-lilith-verification-fix/08-01-SUMMARY.md
@.planning/phases/08-lilith-verification-fix/08-02-SUMMARY.md
@ketu/ephemeris/orbital.py
@ketu/ephemeris/time.py
@tests/test_planets_coverage.py
@docs/LILITH_DEFINITION.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Write tests/test_lilith_cross_check.py with module-level importorskip and 5-date parametrized cross-check</name>
  <files>tests/test_lilith_cross_check.py</files>
  <action>
Create `tests/test_lilith_cross_check.py` (new file). Use the EXACT structure from `08-RESEARCH.md` "Pattern 3" code block as the basis. Required elements:

1. **Module docstring** — Numpydoc-style. State purpose, that the module is auto-skipped when `pysweph` is not installed, and reference `docs/LILITH_DEFINITION.md` for the tolerance derivation.

2. **Import gate** — TOP of file, before any other imports from `ketu.*`:
   ```python
   import pytest

   pytest.importorskip("swisseph", minversion="2.10.3.6")  # runtime gate, no binding
   import swisseph as swe  # static-typing import; picks up pyproject mypy override
   ```
   Rationale: when running `pytest tests/` without the `[test]` extra installed, `pytest.importorskip` raises `pytest.skip.Exception` at collection time and the entire module is collected as SKIPPED rather than ERRORED. The subsequent `import swisseph as swe` only executes after the gate passes; it gives mypy a real `import` statement to which the pyproject `[[tool.mypy.overrides]] module = ["swisseph.*"]` rule applies. Do NOT bind `swe = pytest.importorskip(...)` because that returns `ModuleType` and `mypy --strict` will reject every `swe.MEAN_APOG` / `swe.calc_ut(...)` attribute access (the override matches `import swisseph` statements, not local variables).

3. **Tolerance constant** — Module-level:
   ```python
   TOLERANCE_DEG = 0.01
   ```
   With a comment block above it stating the arithmetic from `docs/LILITH_DEFINITION.md` §"Tolerance Justification": 0.01 deg = 36 arcseconds = ~129 minutes of mean-apogee drift at the 0.111404 deg/day rate.

4. **CROSS_CHECK_DATES list** — 5 datetimes with `tzinfo=timezone.utc`:
   - `datetime(1900, 6, 15, 12, 0, tzinfo=timezone.utc)`
   - `datetime(1950, 3, 21, 18, 30, tzinfo=timezone.utc)`
   - `datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc)`  (J2000.0)
   - `datetime(2025, 9, 23, 6, 0, tzinfo=timezone.utc)`
   - `datetime(2050, 12, 21, 0, 0, tzinfo=timezone.utc)`

   Add a comment explaining the dates: "Mid-month, mid-day to avoid integer-JD coincidences. J2000.0 included as a self-consistency anchor; 1900 and 2050 expose any rate drift across the requirement window."

5. **Helper `_signed_circular_diff(a, b)`** — Returns smallest signed angular difference in (-180, 180]:
   ```python
   def _signed_circular_diff(a: float, b: float) -> float:
       """Smallest signed angular difference a - b in (-180, 180]."""
       return (a - b + 180.0) % 360.0 - 180.0
   ```
   Required: handles 359.99 vs 0.005 wrap-around correctly (returns approximately -0.015, NOT 359.985).

6. **Parametrized test** — `@pytest.mark.parametrize("dt", CROSS_CHECK_DATES, ids=lambda d: d.isoformat())`:
   ```python
   def test_lilith_matches_swiss_ephemeris(dt):
       jd = utc_to_julian(dt)
       xx, _retflag = swe.calc_ut(jd, swe.MEAN_APOG)
       expected_lon = xx[0]
       actual_lon = get_lilith_position(jd)
       delta = _signed_circular_diff(actual_lon, expected_lon)
       assert abs(delta) < TOLERANCE_DEG, (
           f"Lilith mismatch on {dt.isoformat()}: "
           f"Ketu={actual_lon:.6f} deg, swe={expected_lon:.6f} deg, "
           f"delta={delta:+.6f} deg (tolerance {TOLERANCE_DEG} deg)"
       )
   ```
   - MUST unpack `xx, _retflag = swe.calc_ut(...)` to avoid the 6-tuple pitfall (research §Pitfall 6).
   - MUST use `swe.calc_ut`, NOT `swe.calc` (research §Pitfall 2).
   - MUST use `abs(delta) < TOLERANCE_DEG`, NOT `==` on floats.

7. **Imports** (after the importorskip gate):
   ```python
   import numpy as np  # only if needed; remove if unused
   from datetime import datetime, timezone
   from ketu.ephemeris.orbital import get_lilith_position
   from ketu.ephemeris.time import utc_to_julian
   ```
   Drop `numpy` import if not used in final version — keep file minimal.

8. **Future-work note in module docstring** — Single sentence: "The same pattern can verify `swe.MEAN_NODE` and `swe.TRUE_NODE` in a future phase; out of scope for v1.1."

9. **Type annotations** — Add type hints on `_signed_circular_diff` (already shown) and on `test_lilith_matches_swiss_ephemeris(dt: datetime) -> None`. The mypy override `module = ["swisseph.*"]` already in `pyproject.toml` allows untyped `swe` calls.

Forbidden patterns (the verify step will grep for absence):
- `swe.calc(` (without `_ut`) — wrong time scale
- `swe.set_sid_mode(` — would shift to sidereal frame
- `==` for delta comparison — never on floats
- Hardcoded JD numbers (use `utc_to_julian` always)
- Hardcoded "expected" longitudes (the WHOLE point is to compute them from `swe.calc_ut` at test time, not pin from current Ketu output)
  </action>
  <verify>
```bash
test -f tests/test_lilith_cross_check.py && echo "FILE EXISTS"
wc -l tests/test_lilith_cross_check.py  # >= 60

# Required content:
grep -F "pytest.importorskip(\"swisseph\"" tests/test_lilith_cross_check.py
grep -F "minversion=\"2.10.3.6\"" tests/test_lilith_cross_check.py
# NEW: separate `import swisseph as swe` is REQUIRED so mypy --strict picks up
# the pyproject `module = ["swisseph.*"]` override (the override matches direct
# import statements, NOT locals bound from importorskip).
grep -E "^import swisseph as swe$" tests/test_lilith_cross_check.py
grep -F "TOLERANCE_DEG = 0.01" tests/test_lilith_cross_check.py
grep -F "swe.MEAN_APOG" tests/test_lilith_cross_check.py
grep -F "swe.calc_ut" tests/test_lilith_cross_check.py
grep -F "utc_to_julian" tests/test_lilith_cross_check.py
grep -F "_signed_circular_diff" tests/test_lilith_cross_check.py
grep -E "datetime\\(1900" tests/test_lilith_cross_check.py
grep -E "datetime\\(1950" tests/test_lilith_cross_check.py
grep -E "datetime\\(2000" tests/test_lilith_cross_check.py
grep -E "datetime\\(2025" tests/test_lilith_cross_check.py
grep -E "datetime\\(2050" tests/test_lilith_cross_check.py

# Forbidden patterns (must produce ZERO matches):
! grep -E "swe\\.calc\\(" tests/test_lilith_cross_check.py
! grep -F "swe.set_sid_mode" tests/test_lilith_cross_check.py
! grep -E "delta\\s*==" tests/test_lilith_cross_check.py
# NEW: `swe = pytest.importorskip(...)` returns ModuleType and breaks mypy --strict.
# The recommended pattern is `pytest.importorskip("swisseph", ...)` (no binding)
# followed by a separate `import swisseph as swe`. Forbid the bound form:
! grep -E "^swe\\s*=\\s*pytest\\.importorskip" tests/test_lilith_cross_check.py

# Mypy strict on the new file:
mypy --strict tests/test_lilith_cross_check.py 2>&1 | tee /tmp/mypy-lilith.out
grep -E "Success|error:" /tmp/mypy-lilith.out
```
  </verify>
  <done>
File exists, all required grep matches succeed, all three forbidden patterns produce zero matches, mypy --strict reports Success on the file.
  </done>
</task>

<task type="auto">
  <name>Task 2: Run the harness, record empirical max |delta|, gate Plan 04 decision</name>
  <files>(no source files modified; produces empirical evidence)</files>
  <action>
Run the harness in a venv with `[test]` extras installed and capture the empirical result. The MAX |delta| across the 5 dates is the single most important number Phase 8 produces.

```bash
# Ensure pysweph is installed in the active environment:
pip install -e ".[test]"

# Run the harness verbose, capture full stdout:
pytest tests/test_lilith_cross_check.py -v --tb=short 2>&1 | tee /tmp/lilith-harness.out

# Always-pass diagnostic: ALSO run a one-off Python script that prints per-date deltas
# even if the test passes (so we record the actual error magnitudes, not just pass/fail):
python3 - <<'PY' 2>&1 | tee /tmp/lilith-deltas.out
import swisseph as swe
from datetime import datetime, timezone
from ketu.ephemeris.orbital import get_lilith_position
from ketu.ephemeris.time import utc_to_julian

dates = [
    datetime(1900, 6, 15, 12, 0, tzinfo=timezone.utc),
    datetime(1950, 3, 21, 18, 30, tzinfo=timezone.utc),
    datetime(2000, 1,  1, 12, 0, tzinfo=timezone.utc),
    datetime(2025, 9, 23,  6, 0, tzinfo=timezone.utc),
    datetime(2050, 12, 21, 0, 0, tzinfo=timezone.utc),
]
def signed(a, b): return (a - b + 180.0) % 360.0 - 180.0
print(f"{'date':<27} {'ketu':>12} {'swe':>12} {'delta':>10}")
maxabs = 0.0
for dt in dates:
    jd = utc_to_julian(dt)
    xx, _ = swe.calc_ut(jd, swe.MEAN_APOG)
    a = get_lilith_position(jd); e = xx[0]
    d = signed(a, e)
    print(f"{dt.isoformat():<27} {a:12.6f} {e:12.6f} {d:+10.6f}")
    if abs(d) > maxabs: maxabs = abs(d)
print(f"\nMAX |delta| = {maxabs:.6f} deg")
PY
```

Record the captured `MAX |delta|` value. This number gates Plan 04.

Decision (record in SUMMARY.md explicitly):
- If `MAX |delta| <= 0.01` -> harness PASSES, Plan 04 is a NO-OP. SUMMARY notes "Plan 04 will execute its no-change branch."
- If `MAX |delta| > 0.01` -> harness FAILS, Plan 04 must investigate and correct. SUMMARY notes "Plan 04 will execute its formula-correction branch. Per-date deltas: <table from /tmp/lilith-deltas.out>."

Also record the SHAPE of the error (research §Pitfall 1):
- Monotonic in time -> frame mismatch suspected (precession misalignment)
- Roughly constant -> epoch constant `83.3532` is off
- Roughly proportional to `d` (time since J2000) -> rate constant `0.1114040803` is off
- Random small noise -> within tolerance, no systematic bias

Do NOT modify `orbital.py` or `planets.py` in this plan. The conditional fix lives in Plan 04.

Existing test suite must remain green:
```bash
pytest tests/ --ignore=tests/test_lilith_cross_check.py -q 2>&1 | tail -5
# Then with extras (cross-check included):
pytest tests/ -q 2>&1 | tail -5
```
The `tests/` suite without the new file must show the same pass count as before (250 tests). With the new file added, pass count increases by 5 if harness passes, or some subset fails reporting actual deltas.
  </action>
  <verify>
```bash
# Harness output captured:
test -s /tmp/lilith-harness.out && echo "HARNESS OUT CAPTURED"
test -s /tmp/lilith-deltas.out && echo "PER-DATE DELTAS CAPTURED"

# Either passed (5 passed, 0 failed) OR failed with explicit deltas:
grep -E "passed|failed" /tmp/lilith-harness.out

# MAX |delta| line is present in deltas output:
grep -E "MAX \\|delta\\| =" /tmp/lilith-deltas.out

# Existing tests still pass:
pytest tests/ -q 2>&1 | tail -3

# Once 08-03-SUMMARY.md has been written (per the <output> contract below),
# enforce the exact two-line contract that Plan 04 Task 1 reads. These greps
# MUST match the precise format Plan 04 will parse — no leading whitespace,
# no trailing trash, exactly one of NO-OP or FORMULA-CORRECTION. Run AFTER
# SUMMARY.md is finalized (typically at the end of plan execution):
test -f .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md && \
  grep -E "^MAX \\|delta\\| = [0-9]+\\.[0-9]{6} deg$" \
    .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md && \
  echo "MAX DELTA LINE FORMATTED OK"
test -f .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md && \
  grep -E "^Plan 04: (NO-OP|FORMULA-CORRECTION)$" \
    .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md && \
  echo "PLAN 04 BRANCH LINE FORMATTED OK"
```
  </verify>
  <done>
Captured `/tmp/lilith-harness.out` and `/tmp/lilith-deltas.out` exist; SUMMARY.md records the exact `MAX |delta|` value, the per-date table, the error-shape diagnosis (monotonic/constant/proportional/noise), and the Plan 04 branch selection (no-change vs formula-correction). Existing test suite remains green.
  </done>
</task>

</tasks>

<verification>
- `tests/test_lilith_cross_check.py` exists and is mypy-strict clean
- Module-level `pytest.importorskip` makes the harness skip-safe in environments without `pysweph`
- `pytest tests/test_lilith_cross_check.py -v` produces a definite verdict (pass or fail with explicit deltas)
- The empirical MAX |delta| is captured as a number in SUMMARY.md
- The Plan 04 branch (no-op or formula-correction) is explicitly selected in SUMMARY.md
- Existing 250-test suite continues to pass
</verification>

<success_criteria>
1. New file `tests/test_lilith_cross_check.py` exists and conforms to research Pattern 3.
2. Five parametrized test cases run; each reports an explicit Ketu / swe / delta triple.
3. SUMMARY.md records the empirical MAX |delta| in degrees with 6 decimal places.
4. SUMMARY.md explicitly selects Plan 04's branch: NO-OP if MAX |delta| <= 0.01, FORMULA-CORRECTION otherwise.
5. SUMMARY.md classifies the error shape (monotonic / constant / proportional / noise).
6. Existing test suite still passes.
</success_criteria>

<output>
After completion, create `.planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md` containing:
- The full per-date table (date, ketu, swe, delta) from `/tmp/lilith-deltas.out`
- The single-number `MAX |delta| = X.XXXXXX deg` summary
- Pass/fail verdict and pytest output snippet
- Error-shape diagnosis (monotonic / constant / proportional / noise)
- Explicit branch selection: "Plan 04 NO-OP" or "Plan 04 FORMULA-CORRECTION"
- Suspected root cause if branch is FORMULA-CORRECTION (epoch / rate / frame), per research §Pitfall 1
</output>
