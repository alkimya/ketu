---
phase: 30-chiron-range-1900-2100
plan: "02"
subsystem: ephemeris/chiron
tags: [chiron, chebyshev, npz, 1900-2100, regression, bounds]
dependency_graph:
  requires: [30-01]
  provides: [chiron_npz_1900_2100, chiron_regression_9refs, chiron_bounds_tests]
  affects: [31-documentation]
tech_stack:
  added: []
  patterns: [offline-generator, chebyshev-segments, pure-numpy-runtime]
key_files:
  created: []
  modified:
    - tools/gen_chiron_coeffs.py
    - ketu/data/chiron_coeffs.npz
    - ketu/ephemeris/chiron.py
    - tests/ephemeris/test_chiron_unit.py
    - tests/ephemeris/test_chiron_regression.py
decisions:
  - "[Phase 30-02] degree_final=10 confirmed by spike; .npz regenerated with jd_start=2415020.5, jd_end=2488069.5, 2283 segs, shape (2283,11), gate PASS max|Δλ|=0.001214° < 0.01°"
  - "[Phase 30-02] Wing refs 1920+2080 added; no 1905 needed (spike: 1900-1910 max 0.000013°, two orders below gate)"
metrics:
  duration: "~10 minutes (generation 2283 segs ~7 min + validation + edits)"
  completed: "2026-06-03"
  tasks_completed: 3
  files_modified: 5
---

# Phase 30 Plan 02: Chiron Range 1900-2100 (.npz Regeneration) Summary

## One-liner

Chiron Chebyshev .npz regenerated over 1900-2100 (2283 segs, 577 KB, gate PASS max|delta-lon|=0.001214 deg, 8.2x margin) — regression re-pinned to 9 refs spanning 1920-2080, bounds clamp contract locked.

## What Was Done

Extended the permanent generator to cover 1900-2100 and regenerated `ketu/data/chiron_coeffs.npz` using the spike-confirmed parameters (degree=10, seg=32d). Updated the unit test atomically with the new shape, re-pinned the regression to span 1920-2080 (7 original + 2 wing refs), added 4 bounds tests locking the silent-clamp contract, and refreshed all stale 1950/2050 docstrings to 1900/2100.

### Task 1 — Generator edits + .npz regeneration (commit 9bb30ce)

**Generator changes (`tools/gen_chiron_coeffs.py`):**
- `setup_oracle()`: `swe.julday(1950,1,1,0.0)` → `swe.julday(1900,1,1,0.0)` and `swe.julday(2050,1,1,0.0)` → `swe.julday(2100,1,1,0.0)`
- `_REF_JDS`: added `2422324.5` (1920-01-01) and `2480764.5` (2080-01-01) as wing dates; sorted ascending; comment updated to list all 9 dates
- Docstrings refreshed: module header, `setup_oracle`, `generate_all_coefficients`, `dump_reference_longitudes` — all stale "1950/2050" updated to "1900/2100"
- `_DEGREE = 10` left unchanged (spike verdict: gate PASS at degree=10, no raise needed)

**Regenerated .npz metadata:**

| Parameter | Value |
|-----------|-------|
| `lon_coeffs` shape | (2283, 11) |
| `seg_starts` shape | (2283,) |
| `degree` | 10 |
| `jd_start` | 2415020.5 (1900-01-01) |
| `jd_end` | 2488069.5 (2100-01-01) |
| `seg_len` | 32.0 days |
| file size | 577.2 KB |
| gate result | PASS: max\|Δλ\|=0.001214° < 0.01° (margin 8.2×) |
| worst JD | 2424624.04 (1926-04-18, seg 300) |

**Wing ref oracle longitudes (captured via `--dump-refs`):**

| Date | JD | Oracle longitude | retflag |
|------|----|-----------------|---------|
| 1920-01-01 | 2422324.5 | 2.609080° | 260 |
| 2080-01-01 | 2480764.5 | 36.885249° | 260 |

### Task 2 — Unit test + chiron.py docstrings (commit 6503f9b)

**Verified (not re-implemented):**
- Phase 24-04 `actual_len = min(seg_starts[si] + seg_len, jd_end) - seg_starts[si]` at line 113 is **PRESERVED** — reads `jd_end` from `.npz` directly, auto-adapts to new jd_end=2488069.5 and last_seg=25.0 days
- `grep -nE "swisseph|pyswisseph|\bswe\b" ketu/ephemeris/chiron.py` → only docstring mention ("Évaluateur Chiron pur-NumPy — zéro pyswisseph"), zero import statements — AGPL ratchet intact

**Updated (`tests/ephemeris/test_chiron_unit.py`):**
- `test_load_chiron_data_shapes`: `(1142, 11)` → `(2283, 11)`, `(1142,)` → `(2283,)` — updated atomically with the .npz
- Stale "1950-2050" in comments updated to "1900-2100"
- Clamp test docstrings: "before 1950" → "before 1900", "after 2050" → "after 2100"

**Refreshed (`ketu/ephemeris/chiron.py`):**
- `_load_chiron_data` docstring + example: `(1142, 11)` → `(2283, 11)`
- `_eval_chiron_qty` docstring: `2469807.5 for the 1950-2050 range` → `2488069.5 for the 1900-2100 range`; `before 1950 or after 2050` → `before 1900 or after 2100`

### Task 3 — Regression re-pinned + bounds tests (commit ebdfe8d)

**Re-pinned `_CHIRON_REFS` in `tests/ephemeris/test_chiron_regression.py`:**

| JD | Date | Longitude | Delta vs oracle |
|----|------|-----------|-----------------|
| 2422324.5 | 1920-01-01 | 2.609080° | NEW wing ref |
| 2433282.5 | 1950-01-01 | 255.777223° | preserved |
| 2440587.5 | 1970-01-01 | 2.520351° | preserved |
| 2447892.5 | 1990-01-01 | 103.847482° | preserved |
| 2451545.0 | J2000.0 | 251.617624° | preserved |
| 2455197.5 | 2010-01-01 | 323.115304° | preserved |
| 2462501.5 | 2030-01-01 | 38.042056° | preserved |
| 2469807.5 | 2050-01-01 | 246.587706° | preserved |
| 2480764.5 | 2080-01-01 | 36.885249° | NEW wing ref |

All 9 refs confirmed < 0.01° delta (max measured = 0.001214°).

**4 new bounds tests added (pure-NumPy, no pyswisseph):**
- `test_bounds_at_jd_start` — evaluates at jd_start=2415020.5 (lower bound), asserts finite lon in [0,360)
- `test_bounds_just_before_jd_start` — jd_start−1 is out-of-range; silent clamp → finite result, no exception
- `test_bounds_at_jd_end` — jd_end−1 (inside last segment), asserts finite lon in [0,360)
- `test_bounds_just_after_jd_end` — jd_end+1 is out-of-range; silent clamp → finite result, no exception

## Key Parameters Delivered to Phase 31

| Parameter | Value |
|-----------|-------|
| `degree_final` | 10 |
| `n_segs` | 2283 |
| `jd_start` | 2415020.5 (1900-01-01) |
| `jd_end` | 2488069.5 (2100-01-01) |
| `last_seg_actual_len` | 25.0 days |
| actual_len fix preserved | YES (Phase 24-04) |
| pure-NumPy runtime | YES (zero pyswisseph in chiron.py) |

## Deviations from Plan

None — plan executed exactly as written. degree=10 needed no change (spike already confirmed gate PASS). No 1905 wing ref added (spike showed 1900-1910 edge max 0.000013°, two orders below gate — plan explicitly marked this as "optional, not required"). All 3 tasks executed in sequence without blocking issues.

## Final Verification Results

- `pytest tests/ -q`: **1537 passed, 2 skipped**, 100% coverage (fail_under=100 satisfied)
- Doctest gate (`--doctest-modules ketu/ --no-cov --ignore=ketu/lunar_calendar.py`): **60 passed, 1 skipped**
- `git status --porcelain`: only declared 5 files modified + `.planning/` untracked; zero leftover spike artifacts under repo tree

## Self-Check

**Files created:**
- `.planning/phases/30-chiron-range-1900-2100/30-02-SUMMARY.md` — this file

**Files modified:**
- `tools/gen_chiron_coeffs.py` — generator range 1900-2100, _REF_JDS + docstrings
- `ketu/data/chiron_coeffs.npz` — regenerated (2283 segs, 577.2 KB)
- `ketu/ephemeris/chiron.py` — docstrings refreshed, actual_len + pure-NumPy preserved
- `tests/ephemeris/test_chiron_unit.py` — shape assertions updated atomically
- `tests/ephemeris/test_chiron_regression.py` — 9 refs + 4 bounds tests

**Commits:**
- `9bb30ce` — feat(30-02): extend generator to 1900-2100, regenerate .npz (2283 segs)
- `6503f9b` — feat(30-02): update unit test shapes (2283,11), refresh chiron.py docstrings
- `ebdfe8d` — feat(30-02): re-pin regression refs to 1900-2100 + add bounds clamp tests

## Self-Check: PASSED
