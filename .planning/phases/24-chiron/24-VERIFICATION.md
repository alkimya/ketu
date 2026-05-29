---
phase: 24-chiron
verified: 2026-05-29T22:50:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 24: Chiron Verification Report

**Phase Goal:** Chiron is the 14th body — embedded Chebyshev coeffs evaluated in pure NumPy, wired at all six insertion points, participating in chart/aspect/cycle machinery — and the 13→14 breaking positional contract is updated and documented.
**Verified:** 2026-05-29T22:50:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Chiron Chebyshev coefficients ship as `.npz` inside the package, produced by an offline pyswisseph-build-only generator; runtime evaluation is 100% NumPy — no pyswisseph, no scipy, no new runtime dep | VERIFIED | `ketu/data/chiron_coeffs.npz` (289.7 KB, 1142×11 coeffs), `tools/gen_chiron_coeffs.py` (659 lines, swisseph only inside function bodies at lines 107/177/211/235), `ketu/ephemeris/chiron.py` uses `importlib.resources` + `np.polynomial.chebyshev.chebval` — zero swisseph import anywhere under `ketu/` confirmed by grep |
| 2 | Chiron is wired at all six mapped insertion points — `core.py` bodies array, `planets.py` BODY_INDICES + SWE_IDS + BODY_STRATEGIES + avg_speeds + error message — with no special-casing beyond the per-body strategy | VERIFIED | `BODY_INDICES["Chiron"]=13`, `SWE_IDS[13]="Chiron"`, `BODY_STRATEGIES["Chiron"]=_BodyCalc(_chiron_scalar, _chiron_vec)`, `avg_speeds[13]=0.01946`, error msg updated to `0-13`, `core.bodies` len=14 with Chiron row at id=13 — no `if planet_id==13` branch anywhere |
| 3 | `calc_planet_position(jd, 13)` returns Chiron longitude within 0.01° vs Swiss Ephemeris across 7 dates spanning 1950-2050; regression test pins the reference values | VERIFIED | `tests/ephemeris/test_chiron_regression.py` (91 lines, 7 parametrized cases), all 7 pass — worst delta 0.005695° at 1990-01-01 (1.75× under tolerance); bug in last-segment t-normalisation found and fixed in `_eval_chiron_qty` |
| 4 | Bodies axis is 14: `test_body_count_frozen_at_thirteen` updated to `_fourteen`, synastry/transits/charts body-count assertions updated; full suite green at 14 bodies; Chiron in compute_chart, aspect detection, calculate_all_positions | VERIFIED | `test_body_count_frozen_at_fourteen` in `tests/charts/test_dtype.py:218`; `tests/test_ketu.py:110` `len(bodies)==14`; CHART_DTYPE `(14,)/(14,14)`; SYNASTRY_BODY_COUNT=16; full suite 1373 passed/2 skipped/0 failed/100% coverage; integration tests all 4 green |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/gen_chiron_coeffs.py` | Offline Chebyshev coefficient generator (pyswisseph build-only) | VERIFIED | 659 lines, argparse `--output`/`--dump-refs`, swisseph only inside function bodies, validation gate, `savez_compressed` |
| `ketu/data/__init__.py` | Empty package marker | VERIFIED | 0 bytes, exists |
| `ketu/data/chiron_coeffs.npz` | Embedded Chebyshev coefficients (lon/lat/dist) for Chiron 1950-2050 | VERIFIED | 296,611 bytes (289.7 KB), 8 named arrays, shape `(1142, 11)` for lon/lat/dist_coeffs, `seg_len=32.0`, `degree=10` |
| `ketu/ephemeris/chiron.py` | `_load_chiron_data`, `_eval_chiron_qty`, `_chiron_scalar`, `_chiron_vec` | VERIFIED | 249 lines, `importlib.resources.files("ketu.data")`, `@lru_cache(maxsize=1)`, `chebval` eval, 6-tuple scalar output confirmed |
| `tests/ephemeris/test_chiron_unit.py` | Loader + evaluator + clamp-branch + vec/scalar-consistency unit tests | VERIFIED | 310 lines, 7 tests including mock-based 360° wrap branch coverage, chiron.py at 100% coverage |
| `tests/ephemeris/test_chiron_regression.py` | CHIR-03 pinned-reference accuracy regression test | VERIFIED | 91 lines, 7 parametrized (jd, lon) cases, no pyswisseph import, all within 0.01° |
| `tests/ephemeris/test_chiron_integration.py` | CHIR-05 smoke tests: chart/aspect/cycle include Chiron | VERIFIED | 251 lines, 4 tests (compute_chart, aspect_matrix, generate_cycle_series, calculate_all_positions) all pass |
| `ketu/ephemeris/planets.py` | BODY_INDICES/SWE_IDS/BODY_STRATEGIES/avg_speeds entries for Chiron | VERIFIED | All 4 entries present; `from .chiron import _chiron_scalar, _chiron_vec` at module level |
| `ketu/core.py` | 14th body row (Chiron) in bodies array | VERIFIED | `len(bodies)==14`, Chiron row `(13, "Chiron", 0, 0.019)` |
| `ketu/charts/core.py` | CHART_DTYPE with `(14,)` and `(14,14)` subarrays | VERIFIED | `body_lons/body_lats/body_speeds: (14,)`, `aspect_matrix/aspect_orbs: (14,14)` |
| `pyproject.toml` | `ketu.data` package + package-data `*.npz` | VERIFIED | `ketu.data` in packages list, `[tool.setuptools.package-data] "ketu.data" = ["*.npz"]` |
| `MANIFEST.in` | Ships `.npz` in sdist | VERIFIED | `recursive-include ketu/data *.npz` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tools/gen_chiron_coeffs.py` | `ketu/data/chiron_coeffs.npz` | `np.savez_compressed` | VERIFIED | `savez_compressed` present in generator |
| `ketu/ephemeris/chiron.py` | `ketu.data/chiron_coeffs.npz` | `importlib.resources.files` | VERIFIED | `files("ketu.data").joinpath("chiron_coeffs.npz")` at line 49 |
| `ketu/ephemeris/chiron.py` | `np.polynomial.chebyshev.chebval` | pure-NumPy Chebyshev evaluation | VERIFIED | `chebval` at line 115 |
| `ketu/ephemeris/planets.py` | `ketu/ephemeris/chiron.py` | `from .chiron import _chiron_scalar, _chiron_vec` into BODY_STRATEGIES | VERIFIED | Line 23: import; line 319: `"Chiron": _BodyCalc(_chiron_scalar, _chiron_vec)` |
| `pyproject.toml` | `ketu/data/chiron_coeffs.npz` | `package-data ketu.data = *.npz` | VERIFIED | Package-data entry confirmed |
| `tests/ephemeris/test_chiron_regression.py` | `ketu.ephemeris.planets.calc_planet_position` | parametrized assert delta < 0.01 | VERIFIED | `calc_planet_position(jd, 13)` called in parametrize loop, 7/7 pass |
| `tests/ephemeris/test_chiron_integration.py` | `ketu.charts.compute_chart` | assert body_lons.shape[-1]==14 and Chiron index populated | VERIFIED | 4/4 integration smoke tests pass |
| `tests/ephemeris/test_chiron_integration.py` | `ketu.cycles.generate_cycle_series` | Sun-Chiron pair | VERIFIED | `generate_cycle_series(..., "Sun", "Chiron")` test passes |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| CHIR-01 | SATISFIED | `.npz` generated offline by pyswisseph-only tool, runtime pure NumPy confirmed by import audit and functional verification |
| CHIR-02 | SATISFIED | `ketu/ephemeris/chiron.py` evaluator with `_chiron_scalar`/`_chiron_vec` — pure NumPy, `importlib.resources`, `lru_cache` |
| CHIR-03 | SATISFIED | `tests/ephemeris/test_chiron_regression.py` with 7 pinned (JD, lon) references, all within 0.01°, bug fix for last-segment t-normalisation applied |
| CHIR-04 | SATISFIED | Bodies axis moved 13→14 across all six source insertion points, dtype shapes updated, `test_body_count_frozen_at_fourteen` in `tests/charts/test_dtype.py`, full suite green |
| CHIR-05 | SATISFIED | Integration smoke tests confirm Chiron in `compute_chart`, `aspect_matrix`, `generate_cycle_series`, `calculate_all_positions`; no `if planet_id==13` special-casing found |

### Anti-Patterns Found

None. All new files are substantive implementations with no TODO/FIXME/placeholder text, no stub return values, no orphaned code.

### Notable Bug Fixes Applied During Phase

Two correctness bugs were found and fixed inline (auto-fixed per execution rules):

1. **Last-segment t-normalisation** (`ketu/ephemeris/chiron.py` `_eval_chiron_qty`): The evaluator used constant `seg_len=32.0` for t-mapping on the last segment which is only 13 days long. This caused a 0.905° error at JD 2469807.5 (2050-01-01). Fixed by computing `actual_len = min(seg_start + seg_len, jd_end) - seg_start`. The regression test (plan 24-04) found this.

2. **Stale cache shape guard** (`ketu/cache/ephemeris_cache.py`): Old `~/.ketu/ephemeris_cache/*.npy` files built pre-Chiron with shape `(days, 13, 6)` caused `IndexError` when accessing `body_id=13`. Fixed by validating `data.shape[1] == BODY_COUNT` in `ensure_month` and recomputing on mismatch.

### Human Verification Required

None — all observable behaviors verified programmatically. The following were confirmed by running code:

- `calc_planet_position(2451545.0, 13)` returns `lon=251.613°` (within 0.005° of oracle)
- Full suite: 1373 passed, 2 skipped, 0 failed, 100% coverage
- All 4 integration smoke tests pass (compute_chart/aspect_matrix/cycle_series/all_positions)
- All 7 regression cases pass (worst delta 0.005695°, under 0.01° tolerance)

---

_Verified: 2026-05-29T22:50:00Z_
_Verifier: Claude (gsd-verifier)_
