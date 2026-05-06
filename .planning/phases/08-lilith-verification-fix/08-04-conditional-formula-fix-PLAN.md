---
phase: 08-lilith-verification-fix
plan: 04
type: execute
wave: 3
depends_on:
  - "08-03"
files_modified:
  - ketu/ephemeris/orbital.py
  - ketu/ephemeris/planets.py
  - tests/test_lilith_cross_check.py
  - docs/LILITH_DEFINITION.md
autonomous: true

must_haves:
  truths:
    - "User reads `08-03-SUMMARY.md` and finds either `Plan 04 NO-OP` or `Plan 04 FORMULA-CORRECTION` explicitly stated; this plan branches accordingly"
    - "If branch is NO-OP: zero source code lines change; this plan writes only its own SUMMARY documenting the no-op decision"
    - "If branch is FORMULA-CORRECTION: ALL THREE Lilith rate sites are updated consistently — `orbital.py:591` (epoch + rate), `orbital.py:146` ORBITAL_ELEMENTS row, `planets.py:153` lon_speed, `planets.py:458` avg_speeds[12] — no site is left with the old constant"
    - "If branch is FORMULA-CORRECTION: `tests/test_lilith_cross_check.py` is enhanced with regression-baseline assertions pinning the new per-date Ketu values to the corresponding `swe.calc_ut` reference (still computed at test time, not hardcoded)"
    - "If branch is FORMULA-CORRECTION: harness runs green at `MAX |delta| < 0.01 deg` post-fix"
    - "If branch is FORMULA-CORRECTION: existing test suite still passes (no test_planets_coverage regression because the speed-ratio test at lines 477-482 doesn't hardcode 0.111404 — verified before fix)"
    - "If branch is FORMULA-CORRECTION: `docs/LILITH_DEFINITION.md` Formula and History sections are updated with old vs new constants and magnitude"
  artifacts:
    - path: "ketu/ephemeris/orbital.py"
      provides: "Corrected get_lilith_position formula (only if branch=FORMULA-CORRECTION)"
      contains: "get_lilith_position"
    - path: "ketu/ephemeris/planets.py"
      provides: "Consistent Lilith speed across lon_speed and avg_speeds[12] (only if branch=FORMULA-CORRECTION)"
      contains: "Lilith"
    - path: "docs/LILITH_DEFINITION.md"
      provides: "Updated Formula + History sections recording old/new constants and magnitude (always updated by this plan, even if branch=NO-OP)"
      contains: "v1.1"
  key_links:
    - from: "ketu/ephemeris/orbital.py:591 (formula)"
      to: "ketu/ephemeris/orbital.py:146 (ORBITAL_ELEMENTS rate)"
      via: "shared rate constant — must be byte-identical"
      pattern: "0\\.\\d+"
    - from: "ketu/ephemeris/orbital.py (rate)"
      to: "ketu/ephemeris/planets.py:153 (lon_speed) and :458 (avg_speeds[12])"
      via: "Lilith rate appears in three plumbing layers; consistency invariant"
      pattern: "0\\.\\d+"
    - from: "tests/test_lilith_cross_check.py"
      to: "post-fix harness pass with delta < 0.01 deg"
      via: "regression baseline anchored to swe.calc_ut reference"
      pattern: "swe\\.calc_ut"
---

<objective>
Conditionally correct Ketu's Lilith formula based on the empirical verdict recorded in `08-03-SUMMARY.md`. This plan has TWO mutually exclusive branches, selected by reading `08-03-SUMMARY.md`:

- **Branch NO-OP**: Plan 03 reported `MAX |delta| <= 0.01 deg`. The formula is correct within the tolerance defined in `LILITH_DEFINITION.md`. This plan changes ZERO code lines. It writes a SUMMARY confirming the no-op decision and marks Plan 05's CHANGELOG/UPGRADING template as the "agreement" (zero-magnitude) variant.

- **Branch FORMULA-CORRECTION**: Plan 03 reported `MAX |delta| > 0.01 deg`. This plan derives corrected constants from the per-date `swe.calc_ut` reference values, updates ALL THREE codebase sites consistently, enhances the harness with regression baselines, and updates `docs/LILITH_DEFINITION.md`'s Formula + History sections.

Purpose: REQUIREMENTS LIL-03 + ROADMAP success criterion #3. The conditional structure is the whole point — Phase 8 must not invent a fix that wasn't proven necessary by Plan 03.

Precondition: `08-03-SUMMARY.md` must exist and contain a line of the exact form `MAX |delta| = X.XXXXXX deg` AND a line of the exact form `Plan 04: <NO-OP|FORMULA-CORRECTION>`. If either is missing, halt with a clear error pointing back to Plan 03.

Output: Either a no-op SUMMARY (branch NO-OP) or a coordinated 3-site code change + harness enhancement + definition update (branch FORMULA-CORRECTION).

Note on `files_modified`: the frontmatter `files_modified` list is the MAXIMAL (FORMULA-CORRECTION-branch) set — `ketu/ephemeris/orbital.py`, `ketu/ephemeris/planets.py`, `tests/test_lilith_cross_check.py`, `docs/LILITH_DEFINITION.md`. On the NO-OP branch, ONLY `docs/LILITH_DEFINITION.md` is modified (Task 4); the other three files are listed conditionally and remain untouched. `git status --porcelain` after the NO-OP branch must show exactly one modified file: `docs/LILITH_DEFINITION.md`.
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
@.planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md
@docs/LILITH_DEFINITION.md
@ketu/ephemeris/orbital.py
@ketu/ephemeris/planets.py
@tests/test_lilith_cross_check.py
@tests/test_planets_coverage.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Read 08-03-SUMMARY.md, parse branch decision, halt or proceed accordingly</name>
  <files>(no files modified)</files>
  <action>
Read `.planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md`. Extract:

1. The numeric value after `MAX |delta| = ` (degrees, 6 decimal places). Store as `max_delta`.
2. The branch line `Plan 04: NO-OP` or `Plan 04: FORMULA-CORRECTION`. Store as `branch`.
3. The per-date table (5 rows: date, ketu, swe, delta).
4. The error-shape diagnosis (monotonic / constant / proportional / noise).
5. The suspected root cause if branch is FORMULA-CORRECTION (epoch / rate / frame).

Validate consistency:
- If `branch == NO-OP` and `max_delta > 0.01` -> raise; the SUMMARY is internally inconsistent.
- If `branch == FORMULA-CORRECTION` and `max_delta <= 0.01` -> raise; the SUMMARY is internally inconsistent.
- If either field is missing entirely -> halt with: "Plan 03 SUMMARY incomplete; cannot decide branch. Re-run Plan 03 with the diagnostic script that emits MAX |delta| and Plan 04 branch lines."

Echo the decision clearly:
```text
Plan 04 branch: <NO-OP|FORMULA-CORRECTION>
max |delta| from Plan 03: X.XXXXXX deg
Tolerance: 0.01 deg
```

Skip Tasks 2 and 3 below if branch == NO-OP. Run them if branch == FORMULA-CORRECTION.
Always run Task 4 (definition + summary update) regardless of branch.
  </action>
  <verify>
```bash
test -f .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md && echo "PRECONDITION OK"
grep -E "MAX \\|delta\\| =" .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md
grep -E "Plan 04: (NO-OP|FORMULA-CORRECTION)" .planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md
```
  </verify>
  <done>
Branch decision is unambiguously parsed. Subsequent tasks know whether to skip or execute.
  </done>
</task>

<task type="auto">
  <name>Task 2 (CONDITIONAL — only if branch == FORMULA-CORRECTION): Derive new constants, update all THREE codebase sites consistently</name>
  <files>ketu/ephemeris/orbital.py, ketu/ephemeris/planets.py</files>
  <action>
**SKIP THIS TASK IF Task 1 selected branch == NO-OP.**

Derive the corrected constants. The three error-shape branches are quoted verbatim from research §Pitfall 1 ("Warning sign: Error monotonic in time across the 5 dates -> frame mismatch. Error roughly constant -> epoch constant `83.3532` is off. Error roughly proportional to `d` -> rate constant `0.1114040803` is off."):

1. **Constant offset (error roughly CONSTANT across all 5 dates) — epoch correction only.** Per research §Pitfall 1, "Error roughly constant -> epoch constant `83.3532` is off." Compute `new_epoch = swe.calc_ut(2451545.0, swe.MEAN_APOG)[0][0]` (i.e. `swe`'s value at J2000.0 exactly). Replace `83.3532` with the high-precision value; keep the rate `0.1114040803` UNCHANGED.

2. **Proportional in `d` (error grows roughly LINEARLY with date, near-zero at J2000) — rate correction only.** Per research §Pitfall 1, "Error roughly proportional to `d` -> rate constant `0.1114040803` is off." Linear-fit `swe`'s longitude over the 5 dates: `new_rate = (lon_swe(jd_late) - lon_swe(jd_early)) / (jd_late - jd_early)` with appropriate unwrapping. Use the 1900 and 2050 anchors for maximum lever arm. Keep the epoch `83.3532` UNCHANGED.

3. **Mixed/monotonic (error MONOTONIC in time with non-zero intercept at J2000) — frame mismatch; full polyfit gives both epoch and rate.** Per research §Pitfall 1, "Error monotonic in time across the 5 dates -> frame mismatch." This is the most likely diagnosis (precession misalignment between Ketu's mean-of-J2000 and `swe`'s mean-of-date). Linear-regress `lon_swe` against `d` over the 5 dates: `new_rate, new_epoch = np.polyfit(d, lon_swe_unwrapped, 1)`. BOTH epoch AND rate are updated.

Distinguishing branch 2 (proportional) from branch 3 (monotonic-with-intercept): inspect the per-date delta column from `/tmp/lilith-deltas.out`. If `delta(2000-01-01) ~= 0` and `|delta|` grows roughly linearly with `|d|`, it is proportional (branch 2). If `delta(2000-01-01)` is non-zero AND `|delta|` grows monotonically, it is mixed/frame-mismatch (branch 3).

For ALL strategies, the regression input is the 5 per-date `swe.calc_ut` values from Plan 03's `/tmp/lilith-deltas.out` (or recomputed in this task). Do NOT pin from current Ketu output.

**Constant derivation snippet (executable; run inline to compute then patch):**

```python
import numpy as np
import swisseph as swe
from datetime import datetime, timezone
from ketu.ephemeris.time import utc_to_julian

dates = [
    datetime(1900, 6, 15, 12, 0, tzinfo=timezone.utc),
    datetime(1950, 3, 21, 18, 30, tzinfo=timezone.utc),
    datetime(2000, 1,  1, 12, 0, tzinfo=timezone.utc),
    datetime(2025, 9, 23,  6, 0, tzinfo=timezone.utc),
    datetime(2050, 12, 21, 0, 0, tzinfo=timezone.utc),
]
jds = np.array([utc_to_julian(dt) for dt in dates])
d = jds - 2451545.0
lons = np.array([swe.calc_ut(jd, swe.MEAN_APOG)[0][0] for jd in jds])

# Unwrap to a continuous monotonic sequence for regression:
lons_unwrapped = np.unwrap(np.deg2rad(lons))
lons_unwrapped_deg = np.rad2deg(lons_unwrapped)

# Linear fit: lon = epoch + rate * d
rate, epoch = np.polyfit(d, lons_unwrapped_deg, 1)
# Reduce epoch mod 360 for storage:
epoch_mod = epoch % 360.0

print(f"Derived epoch (mod 360): {epoch_mod:.10f}")
print(f"Derived rate            : {rate:.10f}")
print(f"Old epoch: 83.3532, old rate: 0.1114040803")
```

Apply the new constants to ALL THREE sites (research note 1):

**Site A — `ketu/ephemeris/orbital.py:591`** (`get_lilith_position` body):
```python
# OLD:
lilith = normalize_angle(83.3532 + 0.1114040803 * d)
# NEW:
lilith = normalize_angle(NEW_EPOCH + NEW_RATE * d)
```
Use full precision (10+ decimal places). Update the function docstring to reflect derivation source: "Constants fitted to Swiss Ephemeris SE_MEAN_APOG over 1900-2050; see docs/LILITH_DEFINITION.md."

**Site B — `ketu/ephemeris/orbital.py:146`** (`ORBITAL_ELEMENTS` Lilith row):
```python
# OLD: ("Lilith", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1114040803),
# The last numeric column is the rate (mean motion). Replace with NEW_RATE.
```

**Site C — `ketu/ephemeris/planets.py:153`** (`lon_speed` for Lilith branch):
```python
# OLD: lon_speed = 0.1114040803  # degrees per day
# NEW: lon_speed = NEW_RATE      # matches orbital.py NEW_RATE; see docs/LILITH_DEFINITION.md
```

**Site D — `ketu/ephemeris/planets.py:458`** (`avg_speeds[12]`):
```python
# OLD: 12: 0.111404,  # Lilith
# NEW: 12: round(NEW_RATE, 6),  # Lilith — matches orbital.py NEW_RATE rounded to 6dp
```
This site uses 6-decimal precision (consistent with neighboring entries like `0.524167` Mars). Round `NEW_RATE` to 6dp here only.

**Verify all four sites are consistent:** the 6-decimal rounding at site D must equal `round(NEW_RATE, 6)` and the full-precision rate at sites A/B/C must be byte-identical to each other.

Define a single private constant if helpful:
```python
# In ketu/ephemeris/orbital.py near top of module:
_LILITH_MEAN_EPOCH_DEG = NEW_EPOCH       # mean longitude of lunar apogee at J2000.0
_LILITH_MEAN_RATE_DEG_PER_DAY = NEW_RATE # fitted to SE_MEAN_APOG over 1900-2050
```
Then reference `_LILITH_MEAN_EPOCH_DEG` and `_LILITH_MEAN_RATE_DEG_PER_DAY` in both site A and site B (the ORBITAL_ELEMENTS construction). Site C imports from `orbital`. Site D uses the rounded value with a comment cross-referencing the source.

Adding the named constants reduces drift risk for future maintainers. The constants are private (`_` prefix) — not part of the public API.

Run mypy after the edit:
```bash
mypy --strict ketu/ 2>&1 | tail -20
```
Must report Success. The `pyproject.toml [[tool.mypy.overrides]] module = ["swisseph.*"]` is pre-existing; we are not adding new untyped imports.
  </action>
  <verify>
```bash
# If branch == NO-OP, this verify is trivially "skipped" — task 2 didn't run.
# If branch == FORMULA-CORRECTION:

# Structural check 1 — the named constants exist and are exported from orbital.py:
grep -E "^_LILITH_MEAN_EPOCH_DEG\\s*=" ketu/ephemeris/orbital.py
grep -E "^_LILITH_MEAN_RATE_DEG_PER_DAY\\s*=" ketu/ephemeris/orbital.py

# Structural check 2 — the formula at orbital.py:591 references the named constants
# (NOT a duplicated literal):
grep -E "_LILITH_MEAN_EPOCH_DEG\\s*\\+\\s*_LILITH_MEAN_RATE_DEG_PER_DAY\\s*\\*\\s*d" ketu/ephemeris/orbital.py

# Structural check 3 — ORBITAL_ELEMENTS row at orbital.py:146 references the named rate
# constant (NOT a duplicated literal):
grep -F "_LILITH_MEAN_RATE_DEG_PER_DAY" ketu/ephemeris/orbital.py

# Structural check 4 — planets.py imports and uses the named rate constant:
grep -E "from\\s+ketu\\.ephemeris\\.orbital\\s+import.*_LILITH_MEAN_RATE_DEG_PER_DAY" ketu/ephemeris/planets.py
# Site C (lon_speed) uses full-precision constant by name:
grep -E "lon_speed\\s*=\\s*_LILITH_MEAN_RATE_DEG_PER_DAY" ketu/ephemeris/planets.py
# Site D (avg_speeds[12]) uses round() of the named constant — NOT a duplicated literal:
grep -E "12:\\s*round\\(_LILITH_MEAN_RATE_DEG_PER_DAY,\\s*6\\)" ketu/ephemeris/planets.py

# Structural check 5 — the legacy literals are NOT used as standalone constants anywhere
# in the source (neither as concatenated formula nor as duplicated row literal). Note:
# legacy 6-decimal `0.111404` may legitimately appear in a comment or test string; we
# only forbid it as a Python expression value.
! grep -E "^\\s*\\(?\\s*83\\.3532\\s*\\+\\s*0\\.1114040803" ketu/ephemeris/orbital.py
! grep -E "^\\s*lon_speed\\s*=\\s*0\\.1114040803\\b" ketu/ephemeris/planets.py

# Numerical check — at least one of (rate, epoch) actually changed from the legacy values
# (the entire point of this branch):
python3 -c "
from ketu.ephemeris.orbital import _LILITH_MEAN_RATE_DEG_PER_DAY, _LILITH_MEAN_EPOCH_DEG
assert (_LILITH_MEAN_RATE_DEG_PER_DAY, _LILITH_MEAN_EPOCH_DEG) != (0.1114040803, 83.3532), \
    'FORMULA-CORRECTION branch must change at least one of (rate, epoch); current values match legacy'
print(f'rate={_LILITH_MEAN_RATE_DEG_PER_DAY!r}, epoch={_LILITH_MEAN_EPOCH_DEG!r}')
"

# Site-D rounding consistency — round(rate, 6) must equal the literal stored in
# avg_speeds[12]. We don't grep for the rounded literal directly (it might equal
# the legacy 0.111404 by coincidence, or differ); we read the dict in Python:
python3 -c "
from ketu.ephemeris.orbital import _LILITH_MEAN_RATE_DEG_PER_DAY
from ketu.ephemeris.planets import avg_speeds  # adjust import path to match planets.py
expected = round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)
actual = avg_speeds[12]
assert actual == expected, f'avg_speeds[12]={actual!r} but round(rate,6)={expected!r}'
print(f'avg_speeds[12]={actual!r} matches round(rate,6)')
" || echo "NOTE: if avg_speeds is not module-level in planets.py, replace this with a structural grep on round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6) at line 458"

# Mypy still strict-clean:
mypy --strict ketu/ 2>&1 | grep -E "Success|error:"

# Harness now passes:
pytest tests/test_lilith_cross_check.py -v 2>&1 | tee /tmp/lilith-harness-postfix.out
grep "5 passed" /tmp/lilith-harness-postfix.out

# Existing test suite still green:
pytest tests/ -q 2>&1 | tail -3
```

Rationale for the structural-check style: the previous draft used literal-string forbidden-pattern checks (`! grep -F "0.111404," ...` and `! grep -F "0.1114040803" ...`) which fail spuriously on a legitimate fix. If the corrected rate happens to round to `0.111404` at 6 decimal places (entirely possible if only the epoch is off, or if the rate is corrected only in the 7th+ decimal), the file legitimately contains `12: 0.111404,` after the fix and `! grep -F "0.111404,"` would FAIL. By switching to (a) positive structural checks that the named constants exist and are referenced everywhere they should be, (b) a numerical Python check that the constants actually differ from legacy, and (c) a single regex forbidding the OLD literal-as-formula form (not bare 6-dp numbers), the verify step distinguishes "fix did the wrong thing" from "fix happens to round to the same 6-dp string as legacy."
  </verify>
  <done>
All three sites (orbital.py:591, orbital.py:146, planets.py:153, planets.py:458) reference the new constants consistently. Mypy strict passes. Harness reports 5/5 passed. Existing test suite still passes.
  </done>
</task>

<task type="auto">
  <name>Task 3 (CONDITIONAL — only if branch == FORMULA-CORRECTION): Enhance harness with regression-baseline anchor on the new constants</name>
  <files>tests/test_lilith_cross_check.py</files>
  <action>
**SKIP THIS TASK IF Task 1 selected branch == NO-OP.**

The harness already asserts `abs(delta) < TOLERANCE_DEG` against `swe.calc_ut`. Add a SECOND, tighter regression layer that pins Ketu's NEW values to a tighter post-fix tolerance (e.g. 0.001 deg) so future accidental edits to the new constants are detected immediately.

Add to `tests/test_lilith_cross_check.py`:

```python
# Regression tolerance: 100x tighter than user-facing tolerance.
# After the v1.1 formula correction, agreement with swe.MEAN_APOG should be at
# this floor on all sampled dates. A widening of error here implies an unintended
# change to _LILITH_MEAN_EPOCH_DEG or _LILITH_MEAN_RATE_DEG_PER_DAY in
# ketu/ephemeris/orbital.py.
REGRESSION_TOLERANCE_DEG = 0.001  # adjust to actual post-fit residual + safety margin


@pytest.mark.parametrize("dt", CROSS_CHECK_DATES, ids=lambda d: d.isoformat())
def test_lilith_regression_baseline(dt: datetime) -> None:
    """Pin the post-v1.1 fit to a tighter tolerance than the user-facing 0.01 deg."""
    jd = utc_to_julian(dt)
    xx, _retflag = swe.calc_ut(jd, swe.MEAN_APOG)
    expected_lon = xx[0]
    actual_lon = get_lilith_position(jd)
    delta = _signed_circular_diff(actual_lon, expected_lon)
    assert abs(delta) < REGRESSION_TOLERANCE_DEG, (
        f"Regression baseline broken on {dt.isoformat()}: "
        f"delta={delta:+.6f} deg exceeds tighter regression tolerance "
        f"{REGRESSION_TOLERANCE_DEG} deg (was set after v1.1 fit; widening "
        f"indicates unintended formula edit)"
    )
```

Tune `REGRESSION_TOLERANCE_DEG` to the actual post-fit max residual + 50% safety margin. If the fit is excellent (e.g. max residual 0.0003 deg post-fit), set the tolerance to 0.0005 deg. Document the choice in the constant's docstring.

Do NOT hardcode expected longitudes (that would be a Ketu-tests-Ketu loop — research §"Anti-patterns"). Continue to compute reference values from `swe.calc_ut` at test time; only the tolerance number is pinned.

**LIL-03 interpretation note:** REQUIREMENTS LIL-03 says "pin new values with explicit pysweph cross-check." That requirement is satisfied by computing the reference at test time from `swe.calc_ut` (NOT by hardcoding numeric Ketu values into the test). Hardcoding Ketu output would create a Ketu-tests-Ketu loop (research §"Anti-patterns"); the cross-check IS the pinning. The `REGRESSION_TOLERANCE_DEG` constant pins the *agreement margin* between Ketu and `swe`, which is the only externally-anchored quantity worth pinning.

**Import-pattern preservation (propagated from Plan 03 Task 1):** This task adds new test functions to the SAME file, reusing the module-level `pytest.importorskip("swisseph", minversion="2.10.3.6")` runtime gate and the separate `import swisseph as swe` static-typing import established in Plan 03 Task 1. Do NOT introduce a `swe = pytest.importorskip(...)` binding here — that returns `ModuleType` and breaks `mypy --strict` on every `swe.MEAN_APOG` / `swe.calc_ut` access. Reuse the existing `swe` symbol from the module-level `import swisseph as swe`.
  </action>
  <verify>
```bash
grep -F "REGRESSION_TOLERANCE_DEG" tests/test_lilith_cross_check.py
grep -F "test_lilith_regression_baseline" tests/test_lilith_cross_check.py

# Import-pattern from Plan 03 Task 1 is preserved (separate runtime gate + static-typing import):
grep -E "^import swisseph as swe$" tests/test_lilith_cross_check.py
! grep -E "^swe\\s*=\\s*pytest\\.importorskip" tests/test_lilith_cross_check.py

# Both test functions pass:
pytest tests/test_lilith_cross_check.py -v 2>&1 | grep -E "passed|failed"
# Expect: 10 passed (5 original + 5 regression).

mypy --strict tests/test_lilith_cross_check.py 2>&1 | grep -E "Success|error:"
```
  </verify>
  <done>
Harness has 10 passing parametrized cases (5 user-tolerance + 5 regression-tolerance). Mypy strict still passes on the test file. The Plan 03 import-pattern (`pytest.importorskip` runtime gate + separate `import swisseph as swe`) is preserved; no `swe = pytest.importorskip(...)` rebinding was introduced.
  </done>
</task>

<task type="auto">
  <name>Task 4 (ALWAYS RUNS): Update docs/LILITH_DEFINITION.md Formula + History sections with verdict</name>
  <files>docs/LILITH_DEFINITION.md</files>
  <action>
Update `docs/LILITH_DEFINITION.md` to reflect Plan 03's verdict and Plan 04's action.

**If branch == NO-OP:**

- Leave the §"Formula" section UNCHANGED (it already documents the v1.0 / v1.1 formula).
- Update §"History" — replace the placeholder with:
  ```markdown
  - v1.1 (Phase 8): formula verified against Swiss Ephemeris on five dates
    spanning 1900-2050. Maximum deviation: X.XXXXXX deg (well below the
    0.01 deg tolerance). No formula change. See `tests/test_lilith_cross_check.py`.
  ```
  Substitute the actual `MAX |delta|` from Plan 03's SUMMARY.

**If branch == FORMULA-CORRECTION:**

- Update §"Formula" — replace the OLD formula block with the NEW one:
  ```text
  lilith_lon = (NEW_EPOCH + NEW_RATE * d) mod 360 deg
  where d = JD_UT - 2451545.0
  ```
  with full-precision constants. Add a one-line note: "Constants derived in v1.1 by linear regression of `swe.calc_ut(jd, swe.MEAN_APOG)` over five dates spanning 1900-2050; see Phase 8."
- Update §"History" — replace the placeholder with:
  ```markdown
  - v1.1 (Phase 8): formula corrected after Swiss Ephemeris cross-check
    revealed up to MAX_DELTA deg deviation across 1900-2050 (likely cause:
    ROOT_CAUSE_FROM_PLAN_03). Constants updated:
      - epoch: 83.3532 deg -> NEW_EPOCH deg
      - rate : 0.1114040803 deg/day -> NEW_RATE deg/day
    Three code sites updated for consistency:
      - ketu/ephemeris/orbital.py (formula + ORBITAL_ELEMENTS row)
      - ketu/ephemeris/planets.py (lon_speed and avg_speeds[12])
    Concrete v1.0 -> v1.1 numerical change examples are tabulated in
    `UPGRADING.md` (see Plan 05).
  ```

In BOTH branches, the §"Cross-Check" section already references the harness — no change needed there.

ASCII-only formatting; consistent with the rest of the document (no Unicode degrees-sign).
  </action>
  <verify>
```bash
# History section was updated (placeholder is gone):
! grep -F "TO BE FILLED BY PLAN 04" docs/LILITH_DEFINITION.md
! grep -iF "to be filled" docs/LILITH_DEFINITION.md

# History section now includes v1.1 verdict:
grep -E "v1\\.1.*(verified|corrected)" docs/LILITH_DEFINITION.md

# If branch == FORMULA-CORRECTION, the new constants are present:
# (Skip this check if branch == NO-OP.)

# Markdown still well-formed (no merge conflict markers):
! grep -E "^<{3,}|^>{3,}|^={3,}" docs/LILITH_DEFINITION.md
```
  </verify>
  <done>
`docs/LILITH_DEFINITION.md` History section reflects Plan 03's verdict; placeholder is removed. If branch == FORMULA-CORRECTION, the Formula section also documents the new constants and lists the three updated code sites.
  </done>
</task>

</tasks>

<verification>
- Plan 03's SUMMARY was successfully parsed (no halt)
- Branch decision was made consistently with `MAX |delta|` vs 0.01 tolerance
- If branch == NO-OP: zero source code lines changed in `ketu/`; only documentation updated
- If branch == FORMULA-CORRECTION: all three plumbing sites (orbital.py:591/146, planets.py:153/458) reference consistent new constants
- If branch == FORMULA-CORRECTION: harness has 10 passing test cases (5 user-tol + 5 regression-tol)
- Mypy strict passes
- Existing test suite (250 prior tests) still passes
</verification>

<success_criteria>
1. Plan 03's SUMMARY was parsed; branch is unambiguously selected.
2. If NO-OP: code untouched; `docs/LILITH_DEFINITION.md` History section updated with the empirical max delta.
3. If FORMULA-CORRECTION: all FOUR code sites updated (orbital.py:591 formula, orbital.py:146 ORBITAL_ELEMENTS, planets.py:153 lon_speed, planets.py:458 avg_speeds); harness extended with regression baselines; LILITH_DEFINITION.md Formula+History updated.
4. Mypy --strict passes on entire `ketu/` and on `tests/test_lilith_cross_check.py`.
5. `pytest tests/` is green (existing 250 + 5 or 10 new).
</success_criteria>

<output>
After completion, create `.planning/phases/08-lilith-verification-fix/08-04-SUMMARY.md` containing:
- Branch selected (NO-OP or FORMULA-CORRECTION) with the parsed `MAX |delta|` value
- If NO-OP: a one-line "no code changed; LILITH_DEFINITION.md History updated" record
- If FORMULA-CORRECTION:
  - Old constants vs new constants (full precision)
  - Linear-regression residuals (max, mean, per-date)
  - Diff summary of the four code sites updated
  - Post-fix harness run output (10 passed)
  - REGRESSION_TOLERANCE_DEG chosen and justification
- Pointer to Plan 05 with the magnitude string to embed in CHANGELOG/UPGRADING
</output>
