---
phase: 40-declination-speed-field-chart-api
plan: "02"
subsystem: charts
tags: [chart, declination, speed, tdd, helper, vectorised]
dependency_graph:
  requires:
    - "body_decl_speed field in CHART_DTYPE (Plan 01)"
    - "DECL_STANDSTILL_EPS in ketu.calculations (Plan 01)"
  provides:
    - "compute_chart populates body_decl_speed via vectorised FD at Δt=0.01"
    - "is_ascending_declination_chart exported from ketu.charts"
    - "solar_return (and all returns) inherit body_decl_speed for free"
  affects:
    - "Plan 40-03 (composite body_decl_speed derivation) can now rely on populate logic"
    - "Rahu UI can read chart['body_decl_speed'] and call is_ascending_declination_chart"
tech_stack:
  added: []
  patterns:
    - "Forward finite-difference at Δt=0.01 vectorised over S+(14,) (mirrors declination_velocity scalar)"
    - "np.where nested for int8 ternary classification (+1/-1/0)"
    - "One-way charts→calculations import (DECL_STANDSTILL_EPS)"
    - "TDD RED/GREEN per task"
key_files:
  created:
    - tests/charts/test_chart_helpers.py
  modified:
    - ketu/charts/api.py
    - ketu/charts/__init__.py
    - tests/charts/test_compute_chart.py
    - tests/returns/test_solar_return.py
decisions:
  - "Reuse `decl` (δ₀) from the body_decl block — no second evaluation of the chain at jd_b; only jd_b+0.01 is new"
  - "Literal Δt=0.01 in compute_chart (no parameter) — mirrors declination_velocity verbatim for exact Δ==0 agreement"
  - "DECL_STANDSTILL_EPS imported from ketu.calculations (one-way; no cycle)"
  - "is_ascending_declination_chart name is DISTINCT from v1.5 scalar is_ascending_declination — avoids shadowing (Pitfall 6)"
  - "numpydoc docstring on is_ascending_declination_chart with See Also links to scalar + EPS"
metrics:
  duration: "7 minutes"
  completed: "2026-06-17"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 5
---

# Phase 40 Plan 02: compute_chart body_decl_speed Population + is_ascending_declination_chart Helper Summary

**One-liner:** `compute_chart` populates `body_decl_speed` via vectorised forward finite difference at Δt=0.01 d (matching `declination_velocity` exactly, Δ==0), and `is_ascending_declination_chart(chart)→np.int8` is exported from `ketu.charts` as the chart-level montant/descendant classifier.

## What Was Built

### Task 1: Populate body_decl_speed in compute_chart (vectorised FD at Δt=0.01)

After the `out["body_decl"] = decl` assignment in `compute_chart`, added a
forward-FD pass at `jd_b + 0.01`. The already-computed `decl` is reused as δ₀
(no re-evaluation of the coordinate chain at `jd_b`). Only δ₁ is new:

```python
_jd_b1 = jd_b + 0.01
_lons1, _lats1, _ = _vectorised_body_properties(_jd_b1)
_eps_b1 = np.asarray(
    true_obliquity(float(_jd_b1) if _jd_b1.ndim == 0 else _jd_b1)
)
_eps_bc1 = _eps_b1[..., np.newaxis]
_x1, _y1, _z1 = spherical_to_rectangular(_lons1, _lats1, 1.0)
_xe1, _ye1, _ze1 = ecliptic_to_equatorial(_x1, _y1, _z1, _eps_bc1)
_, _decl1, _ = rectangular_to_spherical(_xe1, _ye1, _ze1)
out["body_decl_speed"] = (_decl1 - decl) / 0.01
```

Key points:
- `jd_b.ndim == 0` guard on `true_obliquity` mirrors the body_decl block exactly (Pitfall 2)
- Literal `0.01` mirrors `declination_velocity(jdate, body)` verbatim — ensures Δ==0
- All coordinate-chain functions were already imported; no new imports needed
- Vectorised over all 14 bodies × leading shape S in one pass

Four tests added to `TestBodyDeclSpeed` in `tests/charts/test_compute_chart.py`:
- `test_body_decl_speed_present_and_not_all_zero` — anti zero-fill ratchet (DSPD-01)
- `test_body_decl_speed_matches_scalar_declination_velocity_exactly` — Δ==0 binding (DSPD-02)
- `test_body_decl_speed_vectorised_shape` — shape (N, 14) over array jd (DSPD-01)
- `test_body_decl_speed_all_finite` — no NaN/inf after FD pass

### Task 2: is_ascending_declination_chart helper + export + returns pinning

Added `from ketu.calculations import DECL_STANDSTILL_EPS` to the import block at the
top of `ketu/charts/api.py` (one-way charts→calculations; no cycle per RESEARCH Resolution 1).

Defined `is_ascending_declination_chart(chart: np.ndarray) -> np.ndarray` after `is_day_chart`:

```python
def is_ascending_declination_chart(chart: np.ndarray) -> np.ndarray:
    speeds = np.asarray(chart["body_decl_speed"], dtype=np.float64)
    return np.where(
        speeds > DECL_STANDSTILL_EPS,
        np.int8(1),
        np.where(speeds < -DECL_STANDSTILL_EPS, np.int8(-1), np.int8(0)),
    ).astype(np.int8)
```

Full numpydoc docstring: short summary, Parameters, Returns (int8 +1/-1/0 semantics),
See Also linking the scalar `ketu.calculations.is_ascending_declination` and
`DECL_STANDSTILL_EPS`. Uses the DISTINCT name `is_ascending_declination_chart`.

Exported: `ketu/charts/__init__.py` updated to include `is_ascending_declination_chart`
in both the `from .api import ...` line and `__all__`.

New test file `tests/charts/test_chart_helpers.py` (8 tests):
- `test_is_ascending_declination_chart_importable` — import gate
- `TestIsAscendingDeclChartDtypeAndShape`: dtype is int8, scalar→(14,), vectorised→(N,14)
- `TestIsAscendingDeclChartConsistency`: ascending→+1, descending→-1 vs v1.5 scalar
- `TestIsAscendingDeclChartNeutral`: standstill speed→0; all-three-branches explicit

`tests/returns/test_solar_return.py`: appended `TestSolarReturnBodyDeclSpeedInherited`
— solar_return body_decl_speed is finite and non-zero (DSPD-03 returns inheritance).

## Verification Results

```
pytest tests/charts/ tests/returns/ -q --no-cov
231 passed in 3.43s

pytest tests/ -q (full suite with coverage)
1686 passed, 2 skipped
Required test coverage of 100.0% reached. Total coverage: 100.00%

python -m interrogate ketu/charts/ -v
TOTAL: 8 covered, 0 missed → 100.0% PASSED

python -c "from ketu.charts import is_ascending_declination_chart; print('OK')"  → OK
```

DSPD-02 exact-match verification:
```python
from ketu.charts import compute_chart
from ketu.calculations import declination_velocity
JD = 2460690.0
chart = compute_chart(JD, 48.8566, 2.3522)
chart_speed = float(chart["body_decl_speed"][1])      # Moon
scalar_speed = declination_velocity(JD, 1)
assert chart_speed - scalar_speed == 0.0               # Δ == 0 CONFIRMED
```

## TDD Gate Compliance

Both tasks followed the TDD RED/GREEN cycle:

| Task | RED commit | GREEN commit |
|------|-----------|-------------|
| Task 1 (body_decl_speed population) | 480cd35 | db3536b |
| Task 2 (is_ascending_declination_chart) | 3e585a4 | 7ea6abd |

RED commits verified to fail before GREEN implementation was written.

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 480cd35 | test(40-02) | Add failing TestBodyDeclSpeed tests — body_decl_speed anti-zero-fill + scalar match (RED) |
| db3536b | feat(40-02) | Populate body_decl_speed in compute_chart via vectorised FD at Δt=0.01 (GREEN) |
| 3e585a4 | test(40-02) | Add failing tests for is_ascending_declination_chart + returns pinning (RED) |
| 7ea6abd | feat(40-02) | Add is_ascending_declination_chart helper + export from ketu.charts (GREEN) |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. Both tasks produce fully wired, non-stub implementations. `body_decl_speed` carries
real FD-computed values (verified non-zero for Moon/Sun at test JD). `is_ascending_declination_chart`
returns real int8 classifications based on actual chart data.

## Threat Flags

None. Pure numerical computation — reads a structured-array field, returns int8. No new
external surface, no I/O, no parsing, no user-controlled input. The `ketu.charts` public
jd/lat/lon validation surface is unchanged. ASVS V5 input validation unchanged.

## Self-Check: PASSED

- `ketu/charts/api.py` modified: `is_ascending_declination_chart` defined at line ~572; body_decl_speed FD pass at line ~396
- `ketu/charts/__init__.py` modified: `is_ascending_declination_chart` in import + `__all__`
- `tests/charts/test_compute_chart.py` modified: `TestBodyDeclSpeed` class with 4 tests
- `tests/charts/test_chart_helpers.py` created: 8 tests for `is_ascending_declination_chart`
- `tests/returns/test_solar_return.py` modified: `TestSolarReturnBodyDeclSpeedInherited` class
- All 4 task commits in git history: 480cd35, db3536b, 3e585a4, 7ea6abd
- Full test suite: 1686 passed, 2 skipped, 100% coverage
- interrogate ketu/charts/: 100%
- Import gate: `from ketu.charts import is_ascending_declination_chart` succeeds
