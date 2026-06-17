---
phase: 40-declination-speed-field-chart-api
plan: "01"
subsystem: charts/calculations
tags: [dtype, chart, declination, speed, tdd]
dependency_graph:
  requires: []
  provides:
    - "DECL_STANDSTILL_EPS = 0.001 in ketu.calculations.__all__"
    - "body_decl_speed field at index 8 of CHART_DTYPE (16 fields total)"
    - "dtype ratchet re-pinned at 16 fields in tests/charts/test_dtype.py"
  affects:
    - "Plans 40-02 and 40-03 can now populate body_decl_speed"
    - "Kala positional-offset consumers must re-pin (new field at position 8)"
tech_stack:
  added: []
  patterns:
    - "#: numpydoc docstring on module-level constant"
    - "TDD RED/GREEN per task"
    - "additive dtype field (v1.5 body_decl precedent)"
key_files:
  created: []
  modified:
    - ketu/calculations.py
    - ketu/charts/core.py
    - tests/test_declination.py
    - tests/charts/test_dtype.py
decisions:
  - "DECL_STANDSTILL_EPS placed before declination_velocity (its natural home per PATTERNS.md)"
  - "body_decl_speed inserted at field index 8, immediately after body_decl (mirrors v1.5 pattern)"
  - "#: docstring carries empirical table from RESEARCH.md Resolution 3"
metrics:
  duration: "17 minutes"
  completed: "2026-06-17"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 4
---

# Phase 40 Plan 01: dtype Foundation and DECL_STANDSTILL_EPS Summary

**One-liner:** `body_decl_speed` field (dδ/dt, deg/day) appended to `CHART_DTYPE` at index 8 (15→16 fields) and `DECL_STANDSTILL_EPS = 0.001` constant exported from `ketu.calculations`, both tested via TDD RED/GREEN.

## What Was Built

### Task 1: DECL_STANDSTILL_EPS constant (ketu.calculations)

Added module-level constant `DECL_STANDSTILL_EPS: float = 0.001` (deg/day) to `ketu/calculations.py`, placed immediately before `declination_velocity`. Carries a `#:` numpydoc docstring with the empirical justification table from RESEARCH.md Resolution 3:
- Sun at exact solstice: ~0.000020 deg/day → correctly neutral
- Moon at exact δ-standstill: ~0.000041 deg/day → correctly neutral
- Jupiter/Uranus in motion: 0.003-0.005 deg/day → correctly ascending/descending

Added `"DECL_STANDSTILL_EPS"` to `__all__` near `"declination_velocity"`.

Four tests added to `tests/test_declination.py` (class `TestDeclStandstillEps`):
- `test_importable` — import succeeds
- `test_value` — equals 0.001
- `test_in_all` — appears in `ketu.calculations.__all__`
- `test_sun_solstice_classifies_neutral` — Sun at JD ~2460482.36: |dδ/dt| <= EPS
- `test_jupiter_in_motion_not_masked` — Jupiter at JD_DESC: |dδ/dt| > EPS

### Task 2: body_decl_speed in CHART_DTYPE + ratchet re-pin

Inserted `("body_decl_speed", "f8", (14,))` into `CHART_DTYPE` in `ketu/charts/core.py` immediately after `("body_decl", "f8", (14,))`, making it field index 8 of 16 (15→16 fields total).

Updated the `#:` docstring block:
- "15 total" → "16 total"
- Added `body_decl_speed` field documentation (dδ/dt deg/day, FD at Δt=0.01d, sign = montant/descendant, compare against DECL_STANDSTILL_EPS)
- Extended additive-field history to mention v1.8 and Kala re-pin requirement

Re-pinned the ratchet in `tests/charts/test_dtype.py` at all 5 locations:
1. `test_dtype_has_expected_field_names` — added `"body_decl_speed"` to expected tuple, "15 fields" → "16 fields", mention v1.8 in docstring
2. `test_dtype_subarray_shapes` — added `("body_decl_speed", (14,))` parametrize entry
3. `test_dtype_scalar_field_kinds` — added `("body_decl_speed", "f", 8)` parametrize entry
4. `test_dtype_supports_vectorized_construction` — added `assert arr["body_decl_speed"].shape == (5, 14)`
5. `test_dtype_scalar_zero_dim_construction` — added `assert elem["body_decl_speed"].shape == (14,)`

## Verification Results

```
pytest tests/charts/test_dtype.py tests/test_declination.py -q --no-cov
72 passed in 0.19s

pytest tests/ -q (full suite with coverage)
1673 passed, 2 skipped
Required test coverage of 100.0% reached. Total coverage: 100.00%

interrogate ketu/calculations.py -> 100.0% PASSED
interrogate ketu/charts/core.py  -> 100.0% PASSED

python -c "from ketu.calculations import DECL_STANDSTILL_EPS; assert DECL_STANDSTILL_EPS == 0.001"  OK
python -c "from ketu.charts import CHART_DTYPE; n=CHART_DTYPE.names; assert n[8]=='body_decl_speed'; assert len(n)==16"  OK
```

## TDD Gate Compliance

Both tasks followed the TDD RED/GREEN cycle:

| Task | RED commit | GREEN commit |
|------|-----------|-------------|
| Task 1 (DECL_STANDSTILL_EPS) | 90f6288 | ab6af82 |
| Task 2 (body_decl_speed ratchet) | ec199c2 | 792fcc6 |

RED commits verified to fail before GREEN implementation was written.

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 90f6288 | test(40-01) | Add failing tests for DECL_STANDSTILL_EPS (RED) |
| ab6af82 | feat(40-01) | Add DECL_STANDSTILL_EPS constant to ketu.calculations (GREEN) |
| ec199c2 | test(40-01) | Re-pin dtype ratchet to 16 fields with body_decl_speed (RED) |
| 792fcc6 | feat(40-01) | Append body_decl_speed to CHART_DTYPE, re-pin ratchet (GREEN) |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. This plan adds a dtype field and a constant; neither requires data population (that is Plan 02's responsibility for `compute_chart`). The field exists and is accessible — it will be zero-filled until Plan 02 populates it via the vectorized FD pass.

## Threat Flags

None. Pure numeric dtype field and float constant; no I/O, no parsing, no user-controlled input, no new external surface. ASVS V5 Input Validation at the `ketu.charts` public surface is unchanged.

## Self-Check: PASSED

- `ketu/calculations.py` modified and contains `DECL_STANDSTILL_EPS: float = 0.001` with #: docstring
- `ketu/charts/core.py` modified and contains `body_decl_speed` at index 8 of 16 fields
- `tests/test_declination.py` modified and contains `TestDeclStandstillEps` class with 5 tests
- `tests/charts/test_dtype.py` modified and contains `body_decl_speed` in all 5 ratchet locations
- All 4 commits exist in git history: 90f6288, ab6af82, ec199c2, 792fcc6
- Full test suite: 1673 passed, 2 skipped, 100% coverage
- numpydoc interrogate: both modules 100%
