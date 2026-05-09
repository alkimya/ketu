---
status: complete
final_status: all_passed_after_fix
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
result: pass
evidence: "3 passed in 0.13s (after fix commit c8c5071)"
fix_history:
  - issue: "Stale doctest at api.py:461 — Tromsø J2000 noon expected True, code correctly returns False (polar night)."
  - fix: "Commit c8c5071 — switched example to JD 2451727.0 (Tromsø 2000-07-01 noon UT, midsummer). Sun above horizon, Porphyry fallback still demonstrated, no conflation with polar-night sect outcome."
  - root_cause: "WR-01 refactor (commit 40696eb) fixed is_day_chart geometry to ASC-delta but did not update the polar-safety docstring example. The 134-test charts suite passed because no test pinned the OLD docstring as a behavior contract — only --doctest-modules surfaced it."

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
passed: 8
issues: 0
pending: 0
skipped: 0
issues_fixed_inline: 1

## Gaps

[none — Test 6 issue was diagnosed and fixed inline in commit c8c5071, Tests 1-8 all green after fix]
