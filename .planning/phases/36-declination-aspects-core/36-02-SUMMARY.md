---
phase: 36-declination-aspects-core
plan: "02"
subsystem: declination
tags: [numpy, structured-arrays, aspects, declination, parallels, contra-parallels, batch, vectorized]

requires:
  - phase: 36-declination-aspects-core
    plan: "01"
    provides: ketu/declination/ sub-package with _ORB_MAT + find_declination_aspects (36-01 foundation)

provides:
  - declination_aspect_masks(body_decl) — pure-broadcasting batch detector (S,14)->(S,91) no Python body loop
  - DeclinationAspectMasks NamedTuple — 6 fields: parallel/contra/gap (S,91) + idx_i/idx_j/orb_pairs (91,)
  - 8 batch tests: NamedTuple contract, shapes/dtypes, triu alignment, atleast_2d promotion, no-loop guard, scalar oracle, multi-chart independence, gap formula

affects:
  - 37-v16-release (ships ketu.declination.declination_aspect_masks as part of v1.6.0 DECLA-04)

tech-stack:
  added: []
  patterns:
    - "NamedTuple pattern (typing.NamedTuple, mypy --strict compatible) mirroring ketu/cli/harmonics_spec.py HarmonicsSelection"
    - "np.atleast_2d() for single-chart (14,) -> (S,14) promotion in batch path"
    - "np.count_nonzero() instead of .sum() for bool array counting (pytest-cov numpy interaction)"
    - "inspect.getsource + docstring-strip for vectorization contract assertion"

key-files:
  created:
    - tests/declination/test_batch.py
  modified:
    - ketu/declination/api.py
    - ketu/declination/__init__.py

key-decisions:
  - "DeclinationAspectMasks uses typing.NamedTuple (not dataclass) for mypy --strict compatibility and field destructuring"
  - "np.count_nonzero() used in tests instead of .sum() to avoid pytest-cov / numpy bool array interaction (TypeError with _NoValueType)"
  - "No-loop test strips docstring from getsource output before asserting 'for ' absence (docstring naturally contains 'for' in prose)"

duration: ~5min
completed: "2026-06-04"
---

# Phase 36 Plan 02: Declination Aspects Core — Batch Function Summary

Pure-broadcasting declination_aspect_masks(body_decl) batch function returning a DeclinationAspectMasks NamedTuple of (S,91) bool masks, using precomputed _ORB_MAT fancy-indexing with no Python body loop — delivers DECLA-04

## Performance

- **Duration:** ~5 min
- **Started:** 2026-06-04T14:12:48Z
- **Completed:** 2026-06-04T14:17:44Z
- **Tasks:** 2
- **Files created:** 1 new file
- **Files modified:** 2

## Accomplishments

- `DeclinationAspectMasks` NamedTuple (6 fields in exact order): `parallel`, `contra`, `gap` `(S,91)` + `idx_i`, `idx_j`, `orb_pairs` `(91,)` — mypy `--strict` clean via `typing.NamedTuple`
- `declination_aspect_masks(body_decl)` accepts `(S, 14)` or `(14,)` (promoted via `np.atleast_2d`); pure broadcasting against `_ORB_MAT[idx_i, idx_j]` fancy-indexed once — no Python loop over bodies
- Full numpydoc docstrings on both NamedTuple and function (interrogate 100%)
- Both names re-exported in `ketu.declination.__all__`; `ketu.__init__.__all__` and `CHART_DTYPE` byte-identical
- 8 batch tests all pass: NamedTuple fields, shapes/dtypes, triu alignment, single-chart promotion, no-loop guard, row-for-row scalar consistency oracle (5P+5CP on JD 2451717.0), multi-chart independence, gap formula
- Full suite: 1654 passed, 2 skipped; `ketu.declination` at 100% coverage; mypy `--strict` clean; interrogate 100%

## Task Commits

Each task was committed atomically:

1. **Task 1: Add DeclinationAspectMasks NamedTuple + declination_aspect_masks batch function + re-export** — `b9378e8` (feat)
2. **Task 2: Batch test suite — shapes/dtypes/NamedTuple, no-loop, multi-chart, scalar-consistency oracle** — `c529a38` (test)

## Files Created/Modified

- `ketu/declination/api.py` — Added `DeclinationAspectMasks` NamedTuple + `declination_aspect_masks()` batch function; `__all__` extended with both new names
- `ketu/declination/__init__.py` — Re-exports `DeclinationAspectMasks` + `declination_aspect_masks`; `__all__` extended to 6 names; docstring updated for DECLA-04
- `tests/declination/test_batch.py` — 8 batch tests covering all plan requirements

## Decisions Made

- `DeclinationAspectMasks` uses `typing.NamedTuple` (not dataclass) — field destructuring + mypy `--strict` compatible, consistent with `HarmonicsSelection` precedent in `ketu/cli/harmonics_spec.py`
- `np.count_nonzero()` used in tests rather than `.sum()` on bool arrays — avoids a pytest-cov interaction with numpy internals (TypeError with `_NoValueType`)
- No-loop assertion strips docstring from `inspect.getsource()` output before checking for `"for "` — docstring naturally contains the word "for" in prose, which would be a false positive

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_no_python_body_loop false-positive on docstring content**
- **Found during:** Task 2 execution
- **Issue:** `inspect.getsource(declination_aspect_masks)` includes the docstring; the docstring contains "for a single chart", "for the 14 bodies" etc., causing `"for " not in src` to always fail
- **Fix:** Extended the test to strip the docstring block from the source before asserting — only the actual code lines are checked
- **Files modified:** `tests/declination/test_batch.py`
- **Commit:** `c529a38`

**2. [Rule 1 - Bug] pytest-cov / numpy bool .sum() interaction**
- **Found during:** Task 2 test run with coverage
- **Issue:** `r.parallel[0].sum() == 5` raised `TypeError: int() argument must be a string...not '_NoValueType'` when run under pytest-cov, but passed without coverage. Root cause: pytest-cov monkeypatches numpy ufunc dispatch in a way that breaks `.sum()` on small bool arrays in certain contexts
- **Fix:** Replaced `.sum()` with `int(np.count_nonzero(...))` which bypasses the affected code path
- **Files modified:** `tests/declination/test_batch.py`
- **Commit:** `c529a38`

## Issues Encountered

One mypy/interrogate issue was anticipated but did not occur — the NamedTuple docstring format (numpydoc Attributes section) was accepted by interrogate without any special handling.

## Self-Check: PASSED

All files verified on disk. Both task commits (b9378e8, c529a38) confirmed in git log.

---
*Phase: 36-declination-aspects-core*
*Completed: 2026-06-04*
