---
phase: 17-composite-chart-midpoint-variant
plan: 01
subsystem: composite
tags: [composite, circular-midpoint, numpy, davison-deferred, foundation, COMP-02, COMP-04]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE (output dtype for calculate_composite in Plan 17-02)
  - phase: 16-synastry
    provides: pair-chart subpackage precedent (ketu/synastry/ layout, __init__.py docstring shape)
provides:
  - ketu.composite subpackage skeleton (importable, registered in pyproject.toml)
  - circular_midpoint(lon_a, lon_b) helper — short-arc midpoint modulo 360°, vectorised
  - COMP-02 regression suite (18 tests pinned, mid(359°, 1°) == 0.0 binding)
  - COMP-04 module docstring (Davison loudly deferred to v1.3, no aspirational reference)
affects:
  - 17-02-PLAN (calculate_composite — consumes circular_midpoint)
  - 17-03-PLAN (oracle fixtures — built on top of Plan 17-02)
  - 17-04-PLAN (close-out — coverage gate, Makefile, CHANGELOG)

# Tech tracking
tech-stack:
  added: []  # No new dependencies — pure NumPy
  patterns:
    - "Algebraic short-arc midpoint via signed-diff (a + ((b-a) mod 360 in (-180,180])/2) mod 360 — float-exact for representable means"
    - "Antipodal pin convention: |delta| == 180° collapses to 0.0 (matches np.angle(0+0j))"
    - "Defensive % 360.0 normalisation on entry (negative + >360° inputs accepted)"
    - "Scalar inputs return 0-d ndarray (Ketu API style; callers use .item() for Python float)"

key-files:
  created:
    - ketu/composite/__init__.py
    - ketu/composite/core.py
    - tests/composite/__init__.py
    - tests/composite/test_circular_midpoint.py
  modified:
    - pyproject.toml

key-decisions:
  - "circular_midpoint formulation switched from complex-exponential (~1 ulp drift) to signed-diff algebraic (float-exact for representable means like mid(10°,20°)==15°) — aligns with Task 1 verify command strict equality"
  - "Antipodal pin (|delta|==180°) handled via np.isclose + np.where guard, returning 0.0 (matches np.angle(0+0j) convention, pinned in test_antipodal_pinned_convention tripwire)"
  - "ketu.composite package appended at END of pyproject.toml [tool.setuptools].packages list (synastry precedent — list is non-alphabetical)"
  - "Davison deferred-to-v1.3 in Notes block of __init__.py docstring; NO stub function, NO TODO comment, NO See Also Davison entry (COMP-04 binding)"

patterns-established:
  - "Pair-chart subpackage layout mirrors ketu/synastry/ — __init__.py (docstring + re-exports), core.py (helper)"
  - "Test package layout mirrors tests/synastry/ — __init__.py + per-feature test_*.py files"
  - "Doc gates ratchet: numpydoc lint + interrogate 100% on every new module from Plan 1 (not retrofitted)"

# Metrics
duration: ~7 min
completed: 2026-05-24
---

# Phase 17 Plan 01: Composite Chart Foundation Summary

**ketu.composite subpackage skeleton with circular_midpoint helper (signed-diff algebraic, exact float math), Davison-deferred module docstring, and the 18-test COMP-02 regression ratchet pinning mid(359°, 1°) == 0.0**

## Performance

- **Duration:** ~7 min (6m 43s)
- **Started:** 2026-05-24T10:17:38Z
- **Completed:** 2026-05-24T10:24:21Z
- **Tasks:** 3 / 3
- **Files created:** 4 (`ketu/composite/__init__.py`, `ketu/composite/core.py`, `tests/composite/__init__.py`, `tests/composite/test_circular_midpoint.py`)
- **Files modified:** 1 (`pyproject.toml`)
- **Tests added:** 18 (project suite: 1065 → 1083, all PASS)

## Accomplishments

- **ketu.composite subpackage live and registered** — `from ketu.composite import circular_midpoint` resolves; `ketu.composite` appears in `[tool.setuptools].packages` (appended at end per synastry precedent).
- **`circular_midpoint(lon_a, lon_b)` shipped** — vectorised short-arc midpoint on the unit circle modulo 360°; signed-diff algebraic formulation (float-exact for representable means); defensive `% 360.0` normalisation; antipodal pin via `np.isclose + np.where` guard.
- **COMP-02 binding pinned** — `test_wraparound_359_1_returns_zero` ratchets `circular_midpoint(359.0, 1.0) == 0.0` (NOT 180.0) at strict equality; 9-case parametrized wraparound suite covers `(359,1)`, `(0,358)`, `(270,90)`, `(45,315)` plus commutativity; antipodal tripwire `mid(0°, 180°) == 0.0` documented as `np.angle(0+0j)` convention.
- **COMP-04 docstring binding satisfied** — `ketu/composite/__init__.py` Notes block loudly defers Davison to v1.3 with the exact sentence "Davison composite is NOT in scope"; zero aspirational references (no `def davison_composite`, no `# TODO: davison`, no See Also Davison entry); jd/lat/lon bookkeeping clarification + UTC-only contract restatement included.
- **Doc gates green from day one** — numpydoc lint clean on both new modules; interrogate 100% on `ketu/composite/`; no warnings in pytest run.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ketu/composite/core.py with circular_midpoint helper** — `f1c9050` (feat)
2. **Task 2: Create ketu/composite/__init__.py with package docstring and Davison-deferred Notes block** — `099e546` (feat)
3. **Task 3: Pin the COMP-02 ratchet suite (circular_midpoint wraparound + antipodal + vectorisation)** — `385349d` (test)

**Plan metadata:** (final docs commit follows this SUMMARY)

## Files Created/Modified

- `ketu/composite/__init__.py` — Subpackage entry: module docstring (public surface bullets + See Also to ketu.charts + ketu.synastry + Notes deferring Davison to v1.3 + jd/lat/lon bookkeeping clarification + UTC contract); re-exports `circular_midpoint` via `__all__`.
- `ketu/composite/core.py` — `circular_midpoint(lon_a, lon_b)` helper. Signed short-arc-difference formulation: `(b - a) mod 360` → signed delta in `(-180, +180]` → `(a + delta/2) mod 360`; antipodal guard via `np.isclose(|delta|, 180.0)` returning 0.0.
- `tests/composite/__init__.py` — Empty marker for test package.
- `tests/composite/test_circular_midpoint.py` — 18 tests across 4 classes (Wraparound, Vectorisation, DefensiveNormalisation, NanPropagation). Headline COMP-02 ratchet: `test_wraparound_359_1_returns_zero`.
- `pyproject.toml` (line 61) — Appended `"ketu.composite"` to `[tool.setuptools].packages` (mirrors synastry precedent — append at end of non-alphabetical list).

## Decisions Made

- **Formulation switch (complex → algebraic).** The plan-suggested complex-exponential formulation (`np.angle(exp(i*a) + exp(i*b))`) introduces ~1 ulp drift via `np.deg2rad`/`np.rad2deg` round-trip on inputs like `mid(10°, 20°)` (returns `14.999999999999998` instead of `15.0`). This made Task 1's strict-equality verify command (`assert float(circular_midpoint(10.0, 20.0)) == 15.0`) fail. Switched to the algebraically equivalent signed-diff formulation (`a + ((b-a) % 360 in (-180,180]) / 2) % 360`) documented as the alternative in 17-RESEARCH.md §Alternative formulation. This route is float-exact for representable means AND preserves all the documented properties (antipodal pin, NaN propagation, vectorisation, commutative behaviour on wraparound). Antipodal handling becomes an explicit `np.where(np.isclose(|delta|, 180.0), 0.0, mid)` guard rather than relying on `np.angle(0+0j) == 0.0`. Test suite (Task 3) passes both formulations equivalently because every test except the strict `== 15.0` uses `pytest.approx(..., abs=1e-9)`.

- **Antipodal convention pinned in code AND tests.** `mid(0°, 180°)` = `mid(90°, 270°)` = `mid(180°, 0°)` = `0.0` by explicit `np.isclose(|short|, 180.0)` guard. Tripwire test (`test_antipodal_pinned_convention`) fails loudly if future refactors change this convention without updating the docstring. Convention chosen to match `np.angle(0+0j) == 0.0` so callers familiar with the complex-formulation literature get expected behaviour.

- **Davison guard placement.** Module docstring (`__init__.py`) Notes block is the loudest visibility surface for a deferred-method warning. Avoided putting it in `core.py` because `core.py` is a helper module that doesn't reference Davison at all — putting the guard there would be ahistorical. Also avoided a `def davison_composite(*args, **kwargs): raise NotImplementedError("Deferred to v1.3")` stub: even with a clean NotImplementedError, the function existing in `dir(ketu.composite)` would mislead IDE autocomplete consumers; the Phase 17 standard is zero Davison surface area in the runtime API.

- **Scalar-input return type: 0-d ndarray.** Plan said "scalar inputs return a 0-d array (caller can call `.item()` if a Python float is required)". Implementation honours this — `circular_midpoint(10.0, 20.0)` returns `np.ndarray(15.0)` with `ndim == 0`, not a Python float. Test `test_scalar_returns_ndarray` ratchets this. Rationale: matches Ketu API style across the codebase (synastry, charts, aspects all return ndarray for scalar inputs).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Switched circular_midpoint formulation from complex-exponential to signed-diff algebraic**

- **Found during:** Task 1 (verify command execution).
- **Issue:** The plan's recommended `np.angle(exp(i*a) + exp(i*b))` formulation introduces ~1 ulp floating-point drift on representable means via the `deg2rad`/`rad2deg` round-trip. `circular_midpoint(10.0, 20.0)` returned `14.999999999999998` instead of `15.0`. This failed Task 1's verify command `assert float(circular_midpoint(10.0, 20.0)) == 15.0` (strict equality), even though Task 3's pytest.approx-based test passes both formulations.
- **Fix:** Replaced the complex-exponential implementation with the algebraically equivalent signed-diff formulation documented as the alternative route in 17-RESEARCH.md §Alternative formulation (lines 144–148): compute the signed short-arc difference `b - a` in `(-180, +180]` via modular arithmetic, then add half that delta to `a` (modulo 360°). This is float-exact for representable means while preserving all the documented properties (wraparound, antipodal pin, NaN propagation, vectorisation, defensive `% 360.0` normalisation).
- **Files modified:** `ketu/composite/core.py` (full implementation body rewritten; docstring updated to reference the signed-diff formulation in Notes section).
- **Verification:** Task 1 verify command `assert float(circular_midpoint(10.0, 20.0)) == 15.0` now PASSES; all 18 tests in Task 3 suite PASS; full project suite 1083/1083 PASS; numpydoc + interrogate gates clean.
- **Committed in:** `f1c9050` (Task 1 commit — the fix landed before the file was committed; never had a broken commit on the tree).

---

**Total deviations:** 1 auto-fixed (1 bug — strict-equality verify command failed against the plan's recommended formulation; switched to the explicitly-documented alternative route which is exact for representable means).

**Impact on plan:** No scope change. The signed-diff formulation is explicitly listed in 17-RESEARCH.md §Alternative formulation as algebraically equivalent and "marginally faster (no trig calls)". The deviation is a choice between two equally-valid formulations documented in the research file; the strict-equality verify command made the choice obvious post-hoc. All downstream consumers (Plan 17-02 `calculate_composite`) are agnostic to which formulation is used — the public contract `mid(359°, 1°) == 0.0` + antipodal pin + vectorisation is identical.

## Issues Encountered

- **Pytest shebang broken on venv binary.** `venv/bin/pytest` has a hardcoded shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` (working-tree leftover documented in STATE.md as a v1.1 carry-over, NOT in v1.2 scope). Worked around by invoking `python -m pytest` instead of `pytest` directly. No effect on the plan execution.
- **Pre-existing `ketu/composite/core.py` staged on the working tree.** When the executor agent loaded the repo, `git status` showed `A ketu/composite/core.py` already staged (likely from a prior interrupted run). The file existed with the complex-exponential formulation. Read + verified + rewrote with the algebraic formulation before committing — no orphan staged state survived the Task 1 commit.

## Self-Check: PASSED

Verification of claims:

- **Files exist (all 5):**
  - `ketu/composite/__init__.py` — FOUND
  - `ketu/composite/core.py` — FOUND
  - `tests/composite/__init__.py` — FOUND
  - `tests/composite/test_circular_midpoint.py` — FOUND
  - `pyproject.toml` (modified) — FOUND with "ketu.composite" entry
- **Commits exist:**
  - `f1c9050` — Task 1 (core.py) — FOUND
  - `099e546` — Task 2 (__init__.py + pyproject.toml) — FOUND
  - `385349d` — Task 3 (test suite) — FOUND
- **Verification gates (6/6 PASS):**
  - V1 COMP-02 binding test: PASS
  - V2 Davison guard string in docstring: PASS
  - V3 No Davison stub/TODO/See-Also reference: PASS (grep returns zero matches)
  - V4 pyproject.toml registration: PASS (1 match)
  - V5 Doc gates (numpydoc lint + interrogate): PASS (numpydoc silent; interrogate 100%)
  - V6 Full project test suite: PASS (1083/1083, coverage 98.23%)

## Next Phase Readiness

- **Plan 17-02 (calculate_composite implementation):** Foundation surface frozen. `circular_midpoint` is importable, vectorisable, and pinned by 18 regression tests. The `__all__` export will be extended to include `calculate_composite` in Plan 17-02's `__init__.py` edit. The Davison-deferred Notes block already mentions `calculate_composite` so Plan 17-02 only needs to drop the implementation file + the export line.
- **Plan 17-03 (oracle fixtures):** Will reuse the three synastry oracle birth records (Curie, Diana/Charles, Lennon/Ono). No new birth-data research needed — see 17-RESEARCH.md §Astro.com Oracle Pairs.
- **Plan 17-04 (close-out):** `composite_coverage_gate` pytest marker + `make composite-coverage` Makefile target + CHANGELOG `[Unreleased]` entry follow the synastry Plan 16-05 close-out template exactly (mirror of `synastry_coverage_gate`).

---

*Phase: 17-composite-chart-midpoint-variant*
*Completed: 2026-05-24*
