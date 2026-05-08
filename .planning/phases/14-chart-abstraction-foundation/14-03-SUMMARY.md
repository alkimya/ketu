---
phase: 14-chart-abstraction-foundation
plan: 03
subsystem: charts
tags: [numpy, structured-array, aspects, dense-matrix, ml-interop, vectorisation]

# Dependency graph
requires:
  - phase: 14-chart-abstraction-foundation/14-02
    provides: compute_chart pipeline with broadcast + houses + body positions
              (aspect block sentinel-initialised, awaiting wave 03 wiring)
  - phase: 14-chart-abstraction-foundation/14-01
    provides: CHART_DTYPE structure with aspect_matrix (i1, (13,13)) and
              aspect_orbs (f4, (13,13)) field shapes
provides:
  - Dense (13, 13) intra-chart aspect projection via _build_aspect_matrix
  - aspects=AspectSetSpec pass-through to compute_chart (D-10)
  - aspects=None default resolves to CLASSICAL preset (D-07)
  - Symmetric upper/lower triangle mirror (D-17)
  - Diagonal -1/NaN sentinels preserved (D-06)
  - 12 dedicated aspect-matrix tests including 3 hand-validated charts
affects:
  - 14-05 (doc gates final sweep — aspect_matrix surfaces are now public)
  - 16-synastry (will consume aspect_matrix for cross-chart aspect comparison)
  - 17-composite (will compose aspect matrices from two charts)
  - 18-solar-return (will generate batched charts; the Python loop on S
                     is the documented v1.2 trade-off, profile in P16)
  - 19-arabic-parts (will read aspect_matrix indirectly via lots formulas)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_build_aspect_matrix private helper: project structured records into dense matrix"
    - "np.ndindex(jd_b.shape) for scalar-or-batch traversal (A1 confirmed)"
    - "Symmetric-mirror pattern: matrix[i,j] = matrix[j,i] in record-projection loop"

key-files:
  created:
    - tests/charts/test_aspect_matrix.py
  modified:
    - ketu/charts/api.py
    - tests/charts/test_compute_chart.py

key-decisions:
  - "_build_aspect_matrix as private helper inside ketu/charts/api.py (not its own module): ~30 lines of glue, no separate concern justifying a sect.py-style split"
  - "Python loop over leading shape S: explicit v1.2 trade-off (D-16) tracked via TODO(v1.3) marker for resolve_aspect_set hoisting"
  - "Aspect-set re-resolution per S iteration accepted for v1.2: resolver runs ~µs, S typically <= hundreds (synastry/composite/return)"
  - "Test-subset assertion uses Python set membership instead of NumPy reductions to dodge the _NoValueType bug under coverage.py + swisseph + numpy lazy reload"

patterns-established:
  - "Bidirectional round-trip aspect-matrix tests: standalone records → matrix cells AND matrix cells → standalone records"
  - "Batch vs scalar consistency tests for new vectorised wrappers (5-timestamp parametrisation)"
  - "Hand-validated charts spot-check + cross-validation vs internal oracle (calculate_aspects_vectorized standalone)"

requirements-completed: [CHART-03]

# Metrics
duration: 11min
completed: 2026-05-08
---

# Phase 14 Plan 03: Dense aspect_matrix wired in compute_chart Summary

**Dense (13, 13) intra-chart aspect projection plugged into compute_chart via _build_aspect_matrix, with symmetric mirror, sentinel diagonal, and AspectSetSpec pass-through — closing the aspect block that was sentinel-only in plan 14-02**

## Performance

- **Duration:** 11 min
- **Started:** 2026-05-08T22:56:56Z
- **Completed:** 2026-05-08T23:07:55Z
- **Tasks:** 4 (helper + wiring + test transformation + new tests)
- **Files modified:** 3 (1 created, 2 modified)

## Accomplishments

- `_build_aspect_matrix` helper added to `ketu/charts/api.py`: projects every record from `calculate_aspects_vectorized` into the dense `(13, 13)` matrix, mirrors upper-triangle into lower-triangle (D-17), keeps diagonal at sentinel (D-06).
- `compute_chart` now consumes the `aspects` parameter (no longer `del aspects`); the Plan-02 transitional sentinel-init block was replaced by the live call to `_build_aspect_matrix`.
- The previous transitory test `test_compute_chart_aspect_matrix_sentinel_until_wave_03` was transformed into `test_compute_chart_aspect_matrix_diagonal_is_sentinel` — a structural ratchet on the diagonal-only invariant that survives the wiring.
- 12 new dedicated tests in `tests/charts/test_aspect_matrix.py` covering D-06 (diagonal sentinels), D-07 (CLASSICAL default), D-10 (AspectSetSpec pass-through), D-16 (Python-loop wrapping correctness), D-17 (symmetry), Pitfall 6 (caller-mask equivalence), Assumption A1 (`np.ndindex(())`), batch-vs-scalar consistency, and 3 hand-validated charts (J2000_Paris, 1900_NewYork, Sagan_NYC_1934).

## Task Commits

1. **Task 1+2: `_build_aspect_matrix` helper + branch into `compute_chart`** — `45a1a7c` (feat)
2. **Task 3: Transform aspect_matrix sentinel test into diagonal ratchet** — `1c8daea` (test)
3. **Task 4: Add 12 dense aspect_matrix tests + 3 hand-validated charts** — `9e61700` (test)
4. **Task 4 (hardening): Replace NumPy reductions with set membership to dodge `_NoValueType` bug under coverage** — `3766b24` (test)

_Note: Tasks 1 and 2 are combined into a single feat commit per the plan's "Atomic commit message" guidance — the helper exists only to be wired, splitting the commit would yield an intermediate unused function._

## Files Created/Modified

- `ketu/charts/api.py` — added `_build_aspect_matrix` (~70 lines including docstring), branched into `compute_chart`, updated `compute_chart` docstring to drop the Plan-02 transitional note and add the D-16 explanation, updated module docstring to drop the plan-by-plan sequence note.
- `tests/charts/test_compute_chart.py` — renamed transitional sentinel test to diagonal-only ratchet, updated module docstring to point to `test_aspect_matrix.py` for the exhaustive off-diagonal coverage.
- `tests/charts/test_aspect_matrix.py` — new file, 12 tests, ~370 lines.

## Decisions Made

- **Combine Tasks 1 + 2 into a single feat commit.** The plan describes them as separate tasks but the helper is meaningless until wired; splitting would either (a) leave an unused function in the repo for one commit, or (b) create a non-buildable intermediate state. The plan's own "Atomic commit message" template uses one combined message. (Recorded in Task Commits note.)
- **Recompute Sagan JD via `swe.julday`** (yields 2427750.711806) rather than copy the plan's literal 2427755.21. The plan literal carried a ~5-day drift; the recomputed value is what `swe` actually produces from the documented birth time 1934-11-09T05:05Z. Tests use the recomputed value; comments document the source.
- **Hand-validated chart spot-checks** use only structural invariants (Sun-Mercury Conjunction at J2000 — geometric inevitability since Mercury is always within 28 deg of the Sun and the Conjunction CLASSICAL orb spans 12 deg; Mercury-Rahu Conjunction at 1900-01-01 — ~0.04 deg orb visible in the standalone record list). The bidirectional round-trip test (parametrised on the same 3 charts) provides the exhaustive cross-validation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's incorrect aspect index for Trine (i_asp)**

- **Found during:** Task 4 (writing `test_aspect_matrix_handles_aspect_subset`)
- **Issue:** The plan's Task 4 §6 says `assert chart["aspect_matrix"][i, j] in {0, 7}` for a `["Conjunction", "Trine"]` subset, claiming Trine is `i_asp=7`. Actual canonical indices in `ketu.core.aspects`: Conjunction=0, Sextile=4, **Square=7**, Trine=**9**, Opposition=13.
- **Fix:** Test asserts `populated_values <= {0, 9}` and explicitly verifies Square (7) and Opposition (13) are filtered out (the original plan intent — that "non-requested aspects don't appear" — preserved).
- **Files modified:** tests/charts/test_aspect_matrix.py
- **Verification:** Test passes; Sagan chart yields populated cells only at i_asp ∈ {0, 9}; the explicit "no Square / no Opposition" assertions hold.
- **Committed in:** 9e61700 (Task 4 commit)

**2. [Rule 1 - Bug] Plan's incorrect Sagan JD literal**

- **Found during:** Task 4 (writing hand-validated charts)
- **Issue:** Plan §6 lists Sagan JD as 2427755.21 for 1934-11-09T05:05Z; actual value via `swe.julday(1934, 11, 9, 5+5/60)` is 2427750.711806 (~5-day drift). A 5-day drift is enough to alter most aspects.
- **Fix:** Tests use the recomputed value; in-test comment documents the source (`swe.julday`).
- **Files modified:** tests/charts/test_aspect_matrix.py
- **Verification:** Sagan chart shows 19 classical aspects (rich pattern as the plan expected) and the bidirectional round-trip test passes.
- **Committed in:** 9e61700 (Task 4 commit)

**3. [Rule 3 - Blocking] `_NoValueType` numpy+coverage+swisseph interaction in `(m == 7).sum()`**

- **Found during:** Task 4 verification gate (`pytest tests/charts/ --cov=ketu.charts`)
- **Issue:** The test `test_aspect_matrix_handles_aspect_subset` fails under `--cov=ketu.charts` only — `(m == 7).sum()` triggers the documented numpy lazy-reload bug under coverage.py + swisseph (cf. tests/houses/conftest.py:32-43). The reduction internals call `int(_NoValue)` which crashes when the sentinel is from a different numpy module instance than the reduction's caller. Same root cause that motivated the existing numpy-before-swisseph import discipline.
- **Fix:** Replaced both NumPy reductions with Python `set` membership tests on the already-derived `populated_values` set. Semantics identical; no NumPy reduction in the assertion path.
- **Files modified:** tests/charts/test_aspect_matrix.py
- **Verification:** `pytest tests/charts/ --cov=ketu.charts` now passes 14/14 aspect_matrix tests; all 120 charts tests pass under coverage.
- **Committed in:** 3766b24 (separate test commit for traceability)

---

**Total deviations:** 3 auto-fixed (2 plan-data bugs corrected during implementation, 1 environment-blocking bug worked around).
**Impact on plan:** All auto-fixes preserve the plan's intent; the corrected aspect index and JD make the tests actually verify what they were supposed to. The numpy-coverage workaround follows the established repo pattern (no new abstraction introduced).

## Issues Encountered

- **PYTHONPATH discipline inside the worktree.** No `venv/` exists inside the worktree (it lives in the main repo). Running `python` requires `PYTHONPATH=<worktree>` so the worktree's source resolves first; otherwise newly-edited functions resolve to the main-repo files where the edits don't exist. Resolved by always prefixing test/script invocations with `PYTHONPATH=/home/loc/workspace/ketu/.claude/worktrees/agent-a02f4d428013394f9` and using `/home/loc/workspace/ketu/venv/bin/python` directly.

## Verification Gates

All gates from PLAN.md §"Verification gates" pass:

- `pytest tests/charts/test_aspect_matrix.py -v -x` — 14 passed
- `pytest tests/charts/test_compute_chart.py -v -x` — 34 passed (includes the transformed diagonal-only test)
- `pytest tests/charts/test_compute_chart_vectorisation.py -v -x` — passes (verified in suite run)
- `pytest tests/charts/ -v -x` — **120 passed**
- `pytest tests/ --no-cov -x` — **844 passed** (full repo, no regressions)
- `interrogate ketu/` — **PASSED (100%, gate ≥95%)**
- `numpydoc lint ketu/charts/api.py` — clean
- `mypy --strict ketu/charts/` — **Success: no issues found in 3 source files**
- `coverage on ketu/charts/` — **100% (api.py, core.py, __init__.py)** — gate ≥95% comfortably exceeded
- AGPL boundary smoke test — clean (no `swisseph` or `swe` in `sys.modules` after `import ketu.charts`)
- Sanity script (symmetry + sentinels + caller mask) — **OK**

## Done Criteria Status

- [x] CHART-03 (aspects portion) satisfied — `compute_chart["aspect_matrix"]` and `["aspect_orbs"]` populated per D-05/D-06/D-17.
- [x] D-07 satisfied — `aspects=None` ≡ `aspects="classical"` (test_aspect_matrix_default_aspects_is_classical).
- [x] D-10 satisfied — pass-through `AspectSetSpec` accepted (test_aspect_matrix_handles_aspect_subset).
- [x] D-16 honoured + traced — Python loop on S documented as v1.2 trade-off; TODO(v1.3) marker in code.
- [x] D-17 satisfied — `aspect_matrix == aspect_matrix.T` strict; `aspect_orbs == aspect_orbs.T` modulo NaN.
- [x] Diagonal `aspect_matrix[i, i] == -1` AND `np.isnan(aspect_orbs[i, i])` for all i (Pitfall 6 closed).
- [x] Scalar-jd traversal correct (Assumption A1 closed by test_aspect_matrix_scalar_jd_via_ndindex_empty_tuple).
- [x] `tests/charts/test_aspect_matrix.py` — **14 tests** (the plan asked for 12; the 2 extra come from the parametrised round-trip — 1 logical test × 3 fixtures = 3 test instances counted individually by pytest).
- [x] `test_compute_chart_aspect_matrix_sentinel_until_wave_03` transformed into `test_compute_chart_aspect_matrix_diagonal_is_sentinel` — passes green.
- [x] Doc gates green (interrogate 100%, numpydoc lint clean).
- [x] `mypy --strict ketu/charts/` — clean.
- [x] AGPL boundary intact.

## Threat Flags

None — this plan is purely additive composition (no new endpoints, auth surfaces, file-access patterns, or schema changes). The aspect_matrix consumes already-validated data from `calculate_aspects_vectorized` (Phase 9) and exposes it as a structured-array field; no new trust boundary introduced.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **CHART-03 fully covered.** The aspect block is the last piece of `compute_chart`; the function is now feature-complete except for the doc-gate sweep in plan 14-05.
- **Ready for plan 14-05** (final doc-gate verification + Makefile target). The Plan-02 transitional notes that 14-05 was supposed to mop up are already removed by this plan's docstring updates, simplifying 14-05 to a verification-only sweep.
- **Synastry (Phase 16) is unblocked downstream.** It will consume `aspect_matrix` cross-chart; the dense layout is the canonical interface.
- **No blockers identified.**

## Self-Check

Performed before final commit:

**Files exist:**
- `tests/charts/test_aspect_matrix.py` — FOUND
- `ketu/charts/api.py` (edited) — FOUND
- `tests/charts/test_compute_chart.py` (edited) — FOUND

**Commits exist:**
- `45a1a7c` — FOUND (`git log --oneline | grep 45a1a7c`)
- `1c8daea` — FOUND
- `9e61700` — FOUND
- `3766b24` — FOUND

## Self-Check: PASSED

---
*Phase: 14-chart-abstraction-foundation*
*Completed: 2026-05-08*
