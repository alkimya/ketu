---
phase: 36-declination-aspects-core
plan: "01"
subsystem: declination
tags: [numpy, structured-arrays, aspects, declination, parallels, contra-parallels]

requires:
  - phase: 35-v15-release
    provides: body_decl field in CHART_DTYPE + declination() scalar function (v1.5 infrastructure)

provides:
  - ketu/declination/ sub-package with DECLA_ASPECT_DTYPE (5-field contract), DECLA_COEF=1/12, MIN_DECL_ORB=0.5
  - find_declination_aspects(body_decl) — fully vectorized P/CP detector, single unified DECLA_ASPECT_DTYPE return
  - frozen 14x14 _ORB_MAT pre-computed from ketu.core.bodies orbs
  - 19 scalar tests covering dtype ratchet, 4 pitfall guards, JD 2451717.0 10-aspect oracle, orb formula values

affects:
  - 36-02 (batch function adds declination_aspect_masks to this same sub-package)
  - 37-v16-release (ships ketu.declination as part of v1.6.0)

tech-stack:
  added: []
  patterns:
    - "3-file sub-package layout (core.py + api.py + __init__.py) mirroring ketu/synastry/"
    - "np.triu_indices(14, k=1) for 91 upper-triangle body pairs — fully vectorized, no Python body-loop"
    - "Frozen orb matrix _ORB_MAT at module load time (mat.flags.writeable = False)"
    - "Empty-result contract: np.empty(0, dtype=DECLA_ASPECT_DTYPE) — never None, never tuple"
    - "sort by body1*14+body2 after P/CP concatenation to maintain canonical pair order"

key-files:
  created:
    - ketu/declination/__init__.py
    - ketu/declination/core.py
    - ketu/declination/api.py
    - tests/declination/__init__.py
    - tests/declination/conftest.py
    - tests/declination/test_dtype.py
    - tests/declination/test_find_aspects.py
  modified:
    - pyproject.toml

key-decisions:
  - "CHART_DTYPE and ketu/__init__.__all__ left byte-identical — purely additive sub-package"
  - "Orb matrix frozen at module level (_ORB_MAT) using mat.flags.writeable=False pattern from synastry"
  - "Single unified array return (not tuple) — P/CP distinguished by kind field, sorted by (body1,body2)"
  - "No separate orbs.py — formula is one expression, merged into core.py"
  - "pyproject.toml packages list extended to include ketu.declination"

patterns-established:
  - "Declination aspects use DECLA_COEF=1/12 applied to natal orb, floored at MIN_DECL_ORB=0.5"
  - "Zero-sign guard: sign(0)==0 means bodies at delta=0 participate in no aspect"
  - "gap_p=|d1-d2| for P; gap_cp=|d1+d2| for CP — always compute separately (sign conflation pitfall)"

duration: 15min
completed: "2026-06-04"
---

# Phase 36 Plan 01: Declination Aspects Core — Sub-package Foundation Summary

Pure-NumPy ketu/declination/ sub-package with DECLA_ASPECT_DTYPE, frozen 14x14 orb matrix, and fully vectorized find_declination_aspects() delivering DECLA-01/02/03 (parallels, contra-parallels, body-derived orb formula)

## Performance

- **Duration:** ~15 min
- **Started:** 2026-06-04T14:02:47Z
- **Completed:** 2026-06-04T14:09:17Z
- **Tasks:** 3 (Task 3 required no code changes — all gates satisfied by Tasks 1+2)
- **Files created:** 7 new files
- **Files modified:** 1 (pyproject.toml)

## Accomplishments

- Created `ketu/declination/` sub-package mirroring `ketu/synastry/` 3-file layout (core.py + api.py + `__init__.py`)
- `DECLA_ASPECT_DTYPE` declares the 5-field frozen contract: `(body1 i1, body2 i1, kind U2, gap f8, orb f8)`, itemsize=26
- `find_declination_aspects(body_decl)` is fully vectorized via `np.triu_indices(14, k=1)` — 91 upper-triangle pairs, no Python body loop, single unified DECLA_ASPECT_DTYPE return sorted by `(body1, body2)`
- Frozen `_ORB_MAT` (14×14, f8, `writeable=False`) pre-computed at module load from `ketu.core.bodies` orbs; Sun/Moon=1.0°, Rahu/Lilith=0.5° (floor)
- 19 new tests all pass; full suite: 1646 passed, 2 skipped, 100% coverage, mypy `--strict` clean, interrogate 100% docstring coverage

## Task Commits

Each task was committed atomically:

1. Task 1: Create ketu/declination/ core + api + `__init__` + register package — `b2d84b1` (feat)
2. **Task 2: Scalar test suite — dtype ratchet, conftest fixtures, 4 pitfalls, JD oracle, orb formula** — `310f843` (test)
3. **Task 3: Quality gates — mypy, 100% coverage, interrogate** — no files changed (all gates satisfied)

## Files Created/Modified

- `ketu/declination/core.py` — DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB, _build_orb_matrix(), _ORB_MAT
- `ketu/declination/api.py` — find_declination_aspects(body_decl) fully vectorized scalar detector
- `ketu/declination/__init__.py` — public re-exports with sub-module-only exposure (`ketu.__all__` unchanged)
- `tests/declination/__init__.py` — package marker
- `tests/declination/conftest.py` — body_decl_solstice (JD 2451717.0) + body_decl_zeros fixtures
- `tests/declination/test_dtype.py` — DECLA_ASPECT_DTYPE ratchets (11 tests)
- `tests/declination/test_find_aspects.py` — pitfalls + oracle + orb formula + negative seed (8 tests)
- `pyproject.toml` — added "ketu.declination" to packages list

## Decisions Made

- `CHART_DTYPE` and top-level `ketu/__init__.__all__` left byte-identical — additive-only design (no ratchet break)
- Orb matrix frozen at module level (`_ORB_MAT.flags.writeable = False`) following synastry `_BODY_ORBS_16` pattern
- Single unified array return (not tuple): P/CP rows concatenated then stable-sorted by `(body1, body2)` key
- No separate `orbs.py` — the declination orb formula is one expression, merged into `core.py`

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. All quality gates (mypy --strict, 100% coverage, interrogate 100%) passed on first run without any fixes needed.

## Next Phase Readiness

- `ketu.declination` sub-package is importable, tested, and registered in `pyproject.toml`
- Phase 36-02 can add the batch function (`declination_aspect_masks`) to `ketu/declination/api.py` and re-export from `__init__.py`
- All frozen-contract ratchets (CHART_DTYPE, core.aspects V1/V13 sha256 fingerprints, body-count-14) remain green

## Self-Check: PASSED

All created files verified on disk. Both task commits (b2d84b1, 310f843) confirmed in git log.

---
*Phase: 36-declination-aspects-core*
*Completed: 2026-06-04*
