---
phase: 36-declination-aspects-core
verified: 2026-06-04T14:21:32Z
status: passed
score: 5/5 must-haves verified
---

# Phase 36: Declination Aspects Core — Verification Report

**Phase Goal:** Users can detect parallel and contra-parallel aspects between all 14 bodies in a natal chart using a dedicated, vectorizable companion function.
**Verified:** 2026-06-04T14:21:32Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `find_declination_aspects(body_decl)` returns a unified DECLA_ASPECT_DTYPE structured array distinguishing kind="P" (same non-zero sign, `\|d1-d2\|<=orb`) and kind="CP" (opposite non-zero signs, `\|d1+d2\|<=orb`), with body1<body2, empty=`np.empty(0,...)` | VERIFIED | `ketu/declination/api.py` lines 144-181 implement fully vectorized detection via `np.triu_indices`; empty case returns `np.empty(0, dtype=DECLA_ASPECT_DTYPE)`; all 27 declination tests pass |
| 2 | Per-pair orb = `max((orb_b1+orb_b2)/2 * 1/12, 0.5)`: Sun/Moon=1.0, Rahu/Lilith=0.5 | VERIFIED | `core.py` `_build_orb_matrix()` implements formula exactly; `test_orb_formula_values` asserts `_ORB_MAT[0,1]==1.0`, `_ORB_MAT[10,12]==0.5`; Python confirms Sun/Moon=1.0, Rahu/Lilith=0.5 |
| 3 | Four pitfall guards pass: +15/-15 is CP not P; 7-deg Sun/Moon gap not parallel; all-zero yields zero; Rahu/Lilith gap 0.1 yields one P via floor | VERIFIED | `test_pitfall_sign_conflation`, `test_pitfall_orb_inflation`, `test_pitfall_zero_sign_trap`, `test_pitfall_min_orb_floor` — all 4 pass |
| 4 | Vectorized batch path `declination_aspect_masks(body_decl)` accepts shape (S,14) and returns `DeclinationAspectMasks` NamedTuple with parallel/contra masks (S,91), no Python body loop | VERIFIED | `api.py` lines 184-256 implement pure broadcasting; `test_no_python_body_loop` passes (inspect.getsource confirms no `for` in code body); batch shapes (3,91) confirmed at runtime |
| 5 | CHART_DTYPE ratchet, core.aspects V1/V13 fingerprints, body-count-14 ratchet all green; 100% coverage; mypy --strict clean | VERIFIED | All 4 frozen-contract tests pass; full suite 1654 passed / 100% coverage; `mypy --strict ketu/declination/` reports "Success: no issues found"; no existing ketu source files touched except pyproject.toml |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/declination/core.py` | DECLA_ASPECT_DTYPE (5 fields), DECLA_COEF=1/12, MIN_DECL_ORB=0.5, frozen 14x14 `_ORB_MAT` | VERIFIED | 122 lines; dtype defined with 5 exact fields; `_build_orb_matrix()` with `flags.writeable=False`; module docstring present |
| `ketu/declination/api.py` | `find_declination_aspects` scalar + `declination_aspect_masks` batch + `DeclinationAspectMasks` NamedTuple | VERIFIED | 264 lines; both functions and NamedTuple implemented; full numpydoc docstrings; imports from `.core` |
| `ketu/declination/__init__.py` | Re-exports of dtype, consts, and both functions + `DeclinationAspectMasks` | VERIFIED | Exports all 6 public names in `__all__`; module docstring present |
| `pyproject.toml` | `ketu.declination` in packages list | VERIFIED | Line 70: `"ketu.declination"` present in setuptools packages list |
| `tests/declination/test_find_aspects.py` | 4 pitfall tests + JD 2451717.0 10-aspect oracle + orb formula test | VERIFIED | 259 lines; all 8 test functions present and passing |
| `tests/declination/test_batch.py` | Batch shape/dtype/NamedTuple + no-loop assertion + multi-chart + scalar-consistency oracle | VERIFIED | 207 lines; all 8 test functions present and passing |
| `tests/declination/test_dtype.py` | DECLA_ASPECT_DTYPE ratchet (9 tests) | VERIFIED | 123 lines; all 9 structural tests present and passing |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/declination/api.py` | `ketu/declination/core.py` | `from .core import DECLA_ASPECT_DTYPE, _ORB_MAT` | WIRED | Line 47: `from .core import DECLA_ASPECT_DTYPE, _ORB_MAT` |
| `ketu/declination/core.py` | `ketu.core.bodies` | orb matrix built from `bodies['orb']` | WIRED | Line 44: `from ketu.core import bodies as _BODIES`; used at line 102 |
| `ketu/declination/__init__.py` | `ketu/declination/api.py` | re-exports all public names | WIRED | Line 48: imports `DeclinationAspectMasks`, `declination_aspect_masks`, `find_declination_aspects` |
| `declination_aspect_masks` hot path | `_ORB_MAT[idx_i, idx_j]` | fancy-indexing, no rebuild | WIRED | Line 245: `orb_pairs = _ORB_MAT[idx_i, idx_j]`; no Python `for` loop in function body |
| `tests/declination/test_batch.py` | `find_declination_aspects` | scalar-consistency oracle | WIRED | Lines 137-140: row-for-row comparison between batch and scalar results |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| DECLA-01: Parallel detection | SATISFIED | `find_declination_aspects` detects kind="P" via `(s1==s2) & (s1!=0) & (gap_p<=orb)` |
| DECLA-02: Contra-parallel detection | SATISFIED | `find_declination_aspects` detects kind="CP" via `(s1!=s2) & (s1!=0) & (s2!=0) & (gap_cp<=orb)` |
| DECLA-03: Body-derived orb formula with floor | SATISFIED | `_build_orb_matrix()` computes `max((o1+o2)/2 * DECLA_COEF, MIN_DECL_ORB)`; verified by `test_orb_formula_values` |
| DECLA-04: Vectorizable batch companion function | SATISFIED | `declination_aspect_masks((S,14))` returns `DeclinationAspectMasks` NamedTuple with `(S,91)` masks; no Python body loop |

### Anti-Patterns Found

None. No TODOs, FIXMEs, placeholders, empty returns, or stub implementations detected in the three source files.

### Human Verification Required

None. All goal criteria are fully verifiable programmatically via the test suite and quality gates.

### Summary

Phase 36 fully achieves its goal. The `ketu/declination/` subpackage delivers all four DECLA requirements as a purely additive companion to v1.5 infrastructure:

- The 3-file layout (`core.py` / `api.py` / `__init__.py`) mirrors `ketu/synastry/` exactly.
- `find_declination_aspects` is fully vectorized internally via `np.triu_indices`; returns a single unified DECLA_ASPECT_DTYPE array (P+CP mixed, sorted by pair); empty result is always `np.empty(0, dtype=DECLA_ASPECT_DTYPE)`.
- `declination_aspect_masks` provides the batch path with pure broadcasting — confirmed no Python `for` loop by source inspection test.
- All four pitfall guards pass; the JD 2451717.0 oracle delivers exactly 10 aspects (5P+5CP) with exact pairs matching the research brief.
- No frozen contract was touched: CHART_DTYPE, `core.aspects` V1/V13 fingerprints, and the 14-body ratchet all stay green.
- Quality gates: `mypy --strict` clean, 100% line coverage (zero pragmas), `interrogate` 100% on new package.
- Full suite: **1654 passed, 2 skipped** (the 2 skipped are pre-existing, unrelated to this phase).

---

_Verified: 2026-06-04T14:21:32Z_
_Verifier: Claude (gsd-verifier)_
