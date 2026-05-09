---
status: complete
phase: 14-chart-abstraction-foundation
source:
  - 14-01-SUMMARY.md
  - 14-02-SUMMARY.md
  - 14-03-SUMMARY.md
  - 14-04-SUMMARY.md
  - 14-05-SUMMARY.md
mode: auto-gates
rationale: |
  Phase 14 is a pure NumPy backend library (no UI, no CLI user-facing).
  The "user" is the downstream code consumer (Kala via KetuAdapter,
  Phases 16/17/18/19). UAT here = the contractual gates that protect
  that consumer surface, run programmatically.
started: 2026-05-09
updated: 2026-05-09
---

## Current Test

[testing complete]

## Tests

### 1. Phase 14 test suite green (charts only)
expected: `pytest tests/charts/ -v --no-cov` returns exit 0 and 134 tests pass (was 120 pre-fix; +14 ratchets from code-review-fix).
result: pass
evidence: "134 passed, 73 warnings in 1.79s"

### 2. Coverage gate `make charts-coverage`
expected: `make charts-coverage` returns exit 0 and reports >=95% coverage on `ketu/charts/` (CHART-05 contract).
result: pass
evidence: |
  ketu/charts/__init__.py    4    0  100%
  ketu/charts/api.py        77    0  100%
  ketu/charts/core.py        3    0  100%
  TOTAL                     84    0  100%

### 3. Doc gates `make doc-gates`
expected: `make doc-gates` returns exit 0 — interrogate >=95% AND numpydoc lint clean on `ketu/charts/`.
result: pass
evidence: "Doc gates OK (numpydoc warnings on aspects/timelines.py are pre-Phase-13 carry-overs, deferred per pyproject.toml line 121; not blocking phase 14)."

### 4. mypy --strict on `ketu/charts/`
expected: `mypy --strict ketu/charts/` returns "Success: no issues found" on the 3 source files.
result: pass
evidence: "Success: no issues found in 3 source files"

### 5. AGPL boundary ratchet (no runtime swisseph)
expected: After `import ketu.charts` and a real `compute_chart` call, no module starting with `swisseph` or `swe` appears in `sys.modules`.
result: pass
evidence: "AGPL boundary OK — no swisseph in sys.modules after compute_chart + is_day_chart"

### 6. Doctest examples in `ketu/charts/`
expected: `pytest --doctest-modules ketu/charts/` returns exit 0 and runs >=3 doctests (is_day_chart Examples block).
result: issue
reported: "1 doctest fails: ketu.charts.api.is_day_chart line 461 expects bool(is_day_chart(2451545.0, 69.65, 18.96)) == True (Tromsø J2000 noon), but code returns False. The code is physically correct (Tromsø at 69.65°N is in polar night on Jan 1 — Sun never rises). The docstring example was correct under the OLD `sun_house >= 7` formulation (which falsely reported polar-night locations as 'day' based on which house the Sun mapped to, ignoring whether it was actually above the horizon). The WR-01 refactor (commit 40696eb) fixed the geometry to ASC-delta, which now correctly returns False for polar night — but the docstring example at api.py:461 was not updated."
severity: minor
fix_needed: |
  Update ketu/charts/api.py:459-462 to either:
    (a) Change Expected from True to False with a clarifying comment ("Tromsø J2000 noon — polar night, Sun never rises in January"), OR
    (b) Pick a non-polar-night fixture (e.g. Tromsø in July: 2451725.0 = 2000-07-01 noon) where the answer IS True and Porphyry fallback IS demonstrating safety without changing the sect answer.
  Option (b) is cleaner — it preserves the docstring's intent ("polar safety means we get a valid bool, not raise") without conflating it with sect outcome.

### 7. Full test suite zero-regression
expected: `pytest tests/ --no-cov -x` returns exit 0; total >=858 tests passing (was 844 pre-fix; code-review-fix added +14 ratchets).
result: pass
evidence: "858 passed, 113 warnings in 9.98s"

### 8. Smoke canary — end-to-end consumer call
expected: A fresh `python -c` invocation can import ketu, call compute_chart(Paris J2000) → CHART_DTYPE shape () with system='placidus', call is_day_chart(Paris noon)=True and (Paris midnight)=False, verify aspect_matrix symmetric with diagonal == -1.
result: pass
evidence: |
  1. import ketu OK
  2. compute_chart OK — shape=(), system=placidus
  3. is_day_chart Paris J2000 noon = True OK
  4. aspect_matrix symmetric + diagonal == -1 OK
  5. is_day_chart Paris J2000 midnight = False OK (D-13 night)

## Summary

total: 8
passed: 7
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "is_day_chart docstring example for Tromsø J2000 noon (api.py:459-462) must agree with code behavior"
  status: failed
  reason: "Stale doctest: docstring expects True (old sun_house >= 7 formulation), code returns False (correct ASC-delta after WR-01 fix). Tromsø at lat=69.65 in January is physical polar night — code answer is correct. Docstring lags code."
  severity: minor
  test: 6
  artifacts:
    - ketu/charts/api.py:459-462
  missing: []
  diagnosis: "Code-review fix WR-01 (commit 40696eb) refactored is_day_chart to ASC-delta semantics, which correctly identifies Tromsø J2000 as polar night (False). The docstring example was not updated. The 134-test charts suite passed because no test pinned the OLD docstring example as a behavior contract — only --doctest-modules surfaces it."
  recommended_fix: |
    Edit ketu/charts/api.py:459-462. Two options:
    (a) Change ``True`` → ``False`` with a comment line above: "Tromsø J2000 noon — polar night in January, hence False":
        >>> bool(is_day_chart(2451545.0, 69.65, 18.96))
        False
    (b) Switch to a polar-summer fixture where Porphyry safety demonstrates without conflating with sect outcome. JD 2451725.0 = 2000-07-01 noon UT, Tromsø lat=69.65, lon=18.96 — Sun is well above horizon (midnight sun period). Expected: True.
        >>> bool(is_day_chart(2451725.0, 69.65, 18.96))
        True
    Option (b) is cleaner: it preserves the docstring intent ("polar safety means a clean bool, not a HighLatitudeError") without mixing the polar-night edge case with the sect calculation.
