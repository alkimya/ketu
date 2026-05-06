---
phase: 09-configurable-aspects
plan: 02
subsystem: api
tags: [numpy, presets, aspect-mask, resolver, frozen-array, numpy-typing]

# Dependency graph
requires:
  - phase: 09-configurable-aspects
    provides: "core.aspects 14-row registry (unchanged) — pinned by plan 09-03 invariant test"
provides:
  - "ketu/aspects/presets.py — frozen length-14 bool masks (CLASSICAL=5, TRADITIONAL=7, EXTENDED=14)"
  - "resolve_aspect_set() single-call resolver for None / str preset / Sequence[str|int] / np.ndarray (bool|int)"
  - "AspectSetSpec type alias for typed public API surface"
  - "ASP-06 forward-looking cache rule documented in module docstring + resolver docstring"
  - "Re-exports at ketu.aspects subpackage level (CLASSICAL/TRADITIONAL/EXTENDED/AspectSetSpec/resolve_aspect_set)"
affects:
  - 09-04a-calculator-refactor (consumes resolve_aspect_set in calculator hot loops)
  - 09-04b-default-migration (flips public API defaults to CLASSICAL via resolver)
  - 09-05-integration-and-benchmark (verifies resolver behavior end-to-end)
  - kala (downstream — opt-in to EXTENDED for v1.0 behavior)

# Tech tracking
tech-stack:
  added:
    - "interrogate 1.7.0 (test-time dev tool for docstring coverage gate, ≥95%)"
  patterns:
    - "Frozen np.ndarray pattern (writeable=False) for module-level constants — accidental mutation raises ValueError"
    - "Single-call resolver pattern: resolve once at API entry, pass mask to hot loops"
    - "Defensive bool-rejection in Sequence to prevent silent [True, False] -> [1, 0] index coercion"
    - "numpy.typing.NDArray[np.bool_] for typed mask returns under mypy --strict"

key-files:
  created:
    - "ketu/aspects/presets.py (229 lines, 100% docstring + 100% test coverage)"
    - "tests/test_aspect_presets.py (357 lines, 56 tests)"
  modified:
    - "ketu/aspects/__init__.py (re-export 5 new names + docstring update)"

key-decisions:
  - "Bool items in Sequence rejected explicitly (defensive Rule 2 add): [True, False] would silently coerce to indices [1, 0] without this guard. Plan didn't specify, but allowing it would be a correctness/UX bug."
  - "Multi-dim int ndarray rejected with clear 'must be 1-D' error: caught by 100% coverage drive, prevents confusing downstream IndexError."
  - "interrogate dev-only dep added (not pinned in pyproject) — used to verify ASP-02 docstring gate; no runtime impact."
  - "numpy.typing.NDArray[np.bool_] used throughout (per ketu/aspects/core.py prior art) for mypy strict compliance — np.ndarray bare alias was insufficient."
  - "Defensive assert len(_ASPECTS) == 14 at module load: redundant with plan 09-03 invariant test, but catches drift at first import (fail-fast)."

patterns-established:
  - "Frozen mask pattern: build via _indices_to_mask helper, set writeable=False, expose as module constant"
  - "Resolver dispatch: None -> default, str -> preset table, np.ndarray -> shape/dtype branch, Sequence -> per-item validation with explicit bool rejection"
  - "Forward-looking cache rule documented in TWO places (module docstring + inline near resolver) per plan instruction — discoverable from both code-reading entry points"

# Metrics
duration: 5m 25s
completed: 2026-05-06
---

# Phase 09 Plan 02: Presets Module Summary

**Frozen length-14 bool-mask presets (CLASSICAL/TRADITIONAL/EXTENDED) plus six-branch `resolve_aspect_set` resolver — foundation for ASP-04/ASP-05 hot-loop replacement in Wave 2.**

## Performance

- **Duration:** 5m 25s
- **Started:** 2026-05-06T19:09:23Z
- **Completed:** 2026-05-06T19:14:48Z
- **Tasks:** 3
- **Files modified:** 3 (1 created module, 1 modified subpackage init, 1 created test file)

## Accomplishments

- **`ketu/aspects/presets.py` (229 lines, 100% docstring coverage):** Three frozen `np.bool_` masks of length 14 (sums 5/7/14), plus single-call resolver that dispatches on six input types (None / str / Sequence[str|int] / np.ndarray bool / np.ndarray int / mixed Sequence).
- **Re-export at subpackage level:** `from ketu.aspects import CLASSICAL` works and is in `__all__` — clean public API surface for downstream Wave 2 plans and external consumers.
- **`tests/test_aspect_presets.py` (357 lines, 56 tests, 100% coverage):** Exhaustive happy-path + error-path coverage including parametrized name/index/mask cases, frozen-mutation guards, custom-default behavior, and defensive bool-rejection in sequences.
- **ASP-06 forward-looking rule documented** in module docstring and inline near resolver: future caches that depend on `aspects=` MUST hash `mask.tobytes()` in keys.
- **Zero regression:** Full test suite of 479 tests still passes (was 423 before this plan; +56 new tests).

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ketu/aspects/presets.py with constants and resolver** — `f223271` (feat)
2. **Task 2: Re-export presets from ketu/aspects/__init__.py** — `78085d1` (feat)
3. **Task 3: Write tests/test_aspect_presets.py — resolver and constants unit tests** — `5481408` (test)

**Plan metadata commit:** _(this SUMMARY.md, see final commit)_

## Files Created/Modified

- `ketu/aspects/presets.py` **(created, 229 lines)** — `CLASSICAL`/`TRADITIONAL`/`EXTENDED` frozen masks, `_indices_to_mask` helper, `resolve_aspect_set` resolver, `AspectSetSpec` type alias, `_PRESET_BY_NAME` lookup table, ASP-06 forward-looking docstring.
- `ketu/aspects/__init__.py` **(modified, +18 lines)** — added imports of 5 new names from `ketu.aspects.presets` and appended them to `__all__` under a "Presets (Phase 9 — configurable aspects)" section comment; module docstring updated to mention presets submodule.
- `tests/test_aspect_presets.py` **(created, 357 lines, 56 tests)** — 8 constant tests, 14 happy-path resolver tests, 11 error-path tests, 3 invariant-on-output tests, plus parametrized variants for case-insensitive preset names, name lists, integer ranges, mask shapes, and item types.

## Resolver Behavior Matrix

| Input type                                  | Returns                                              | Raises                                              |
| ------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------- |
| `None`                                      | `default` (CLASSICAL by default)                     | —                                                   |
| `"classical"` / `"Classical"` / `"CLASSICAL"` | `CLASSICAL` (case-insensitive)                       | —                                                   |
| `"traditional"`                             | `TRADITIONAL`                                        | —                                                   |
| `"extended"`                                | `EXTENDED`                                           | —                                                   |
| `"unknown"`                                 | —                                                    | `ValueError("unknown aspect preset: ...")`          |
| `["Conjunction", "Trine"]`                  | mask with indices [0, 9] True                        | —                                                   |
| `["Bogus"]`                                 | —                                                    | `ValueError("unknown aspect name: ...")` (lists 14) |
| `[0, 4, 7, 9, 13]`                          | `CLASSICAL`                                          | —                                                   |
| `[14]` / `[-1]` / `[100]`                   | —                                                    | `ValueError("aspect index out of range: ...")`      |
| `[1.5]` / `[None]` / `[True]` / `[b"x"]`    | —                                                    | `ValueError("invalid aspect spec item: ...")`       |
| `np.zeros(14, bool)` / `np.ones(14, bool)`  | passthrough (input unchanged)                        | —                                                   |
| `np.zeros(13, bool)`                        | —                                                    | `ValueError("...shape (14,)...")`                   |
| `np.array([0, 13], dtype=intp)`             | mask with indices [0, 13] True                       | —                                                   |
| `np.array([[0, 4], [7, 13]], dtype=intp)`   | —                                                    | `ValueError("...must be 1-D...")`                   |
| Mixed `["Conjunction", 7, "Trine", 13]`     | mask with indices [0, 7, 9, 13] True                 | —                                                   |

## Decisions Made

1. **Defensive bool rejection in Sequence (auto-fix Rule 2):** Plan didn't specify, but `[True, False, True]` would silently coerce to indices `[1, 0, 1]` because `bool` is a subclass of `int` in Python. Added explicit `isinstance(item, bool)` check raising `ValueError("invalid aspect spec item")` before the int branch. Test `test_resolve_bool_in_sequence_rejected` covers this.
2. **Multi-dim int ndarray rejection (auto-fix Rule 2):** Found while driving 100% coverage. A 2-D int ndarray would have produced a confusing `IndexError` deep inside `_indices_to_mask`. Added explicit `ndim == 1` check with clear error. Test `test_resolve_multidim_int_ndarray_raises` covers this.
3. **`numpy.typing.NDArray[np.bool_]` for typed returns:** mypy `--strict` accepted bare `np.ndarray` for the implementation, but precise typing matches prior art in `ketu/aspects/core.py` and signals intent to downstream callers (Wave 2 calculator refactor).
4. **`assert len(_ASPECTS) == 14` at module load:** Redundant with plan 09-03's stronger invariant test, but provides fail-fast on first import — defense in depth.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Defensive `bool` rejection in Sequence iteration**
- **Found during:** Task 1 (Create presets.py) — design review while writing the resolver branch order.
- **Issue:** Without this guard, `resolve_aspect_set([True, False, True])` would resolve to mask indices `[1, 0, 1]` because `isinstance(True, int)` is `True` in Python. This is a silent correctness bug, not user-friendly.
- **Fix:** Added `isinstance(item, bool)` check at the top of the per-item loop, raising `ValueError("invalid aspect spec item: ... (expected str or int)")` — same error format as other invalid types.
- **Files modified:** `ketu/aspects/presets.py` (resolver, lines 197-201).
- **Verification:** New test `test_resolve_bool_in_sequence_rejected` confirms behavior.
- **Committed in:** `f223271` (Task 1).

**2. [Rule 2 - Missing Critical] Multi-dim int ndarray rejected with clear message**
- **Found during:** Task 3 (writing tests) — driving 100% coverage exposed an unhandled branch.
- **Issue:** `resolve_aspect_set(np.array([[0, 4], [7, 13]]))` would produce a confusing `IndexError` from `_indices_to_mask` rather than a clear ValueError. Plan said to "treat as int indices" but only specified 1-D handling.
- **Fix:** Added `if idx_array.ndim != 1: raise ValueError("integer aspect index array must be 1-D, got shape {spec.shape}")`.
- **Files modified:** `ketu/aspects/presets.py` (lines 178-182).
- **Verification:** New test `test_resolve_multidim_int_ndarray_raises` confirms the clear error.
- **Committed in:** `5481408` (Task 3, alongside the test that drove its discovery — note this means the fix landed AFTER Task 1 commit; the addition was small enough to fold into Task 3's test commit rather than amending Task 1).

**3. [Rule 3 - Blocking] interrogate package not installed in venv**
- **Found during:** Task 1 verification (`python -m interrogate ...` failed with `No module named interrogate`).
- **Issue:** Plan's verification step required `interrogate` ≥95% docstring gate, but the dev tool was missing from the venv (it's a test-time dependency, not in `pyproject.toml` runtime deps).
- **Fix:** `python -m pip install interrogate` (installed 1.7.0 + 4 transitive deps: tabulate, py, colorama, attrs).
- **Files modified:** None (venv-local install only; not pinned in pyproject.toml — matches v1.0 dev-tool convention where mypy/pytest are also venv-local).
- **Verification:** `interrogate ketu/aspects/presets.py -f 95` returns `PASSED (minimum: 95.0%, actual: 100.0%)`.
- **Committed in:** N/A (venv-local; no pyproject change).

### Parallel-Execution Note (Cross-plan, not a deviation in scope)

While committing Task 2 (`ketu/aspects/__init__.py` re-export), the working tree contained an untracked file `tests/benchmark_aspects_batch.py` that belongs to **plan 09-01 (baseline-capture)**, which was running in parallel. Despite explicitly staging only `ketu/aspects/__init__.py` via `git add ketu/aspects/__init__.py`, that file ended up in the Task 2 commit (`78085d1`). Investigation: the file was created by the parallel 09-01 agent between my init snapshot and my commit, and made it into the commit object via a parallel-write race. The file's content is correct and intentional (it is plan 09-01's deliverable per `09-01-baseline-capture-PLAN.md`). **Action:** Plan 09-01's executor should treat the benchmark file as already-committed and skip its own commit step for that file; their SUMMARY should reference commit `78085d1`. No content corruption, just commit attribution drift. This is the only side effect; my plan's three deliverables (`presets.py`, `__init__.py`, `test_aspect_presets.py`) are correct.

---

**Total deviations:** 3 auto-fixed (2 missing critical, 1 blocking) + 1 cross-plan attribution note (not a deviation).
**Impact on plan:** All auto-fixes either prevent silent correctness bugs (deviations 1, 2) or are dev-tool installation (deviation 3 — necessary for the plan's own verification gate). No scope creep — all stay within `ketu/aspects/presets.py` and `tests/test_aspect_presets.py`. Deviation 1 alone produced one new test (`test_resolve_bool_in_sequence_rejected`); deviation 2 produced one new test (`test_resolve_multidim_int_ndarray_raises`).

## Issues Encountered

- **`pytest --cov=ketu.aspects.presets` (dotted form) reloads NumPy and breaks `array.sum()`:** Discovered when first running coverage with the dotted-name form. Six tests failed with `TypeError: int() argument must be a string, a bytes-like object or a real number, not '_NoValueType'`. Root cause: numpy's reload triggers a known stub-shadowing issue with `coverage.py`. **Workaround:** use file-path form `--cov=ketu/aspects/presets.py` instead. Standard pattern across the project; recorded here for future reference.
- **`venv/bin/mypy` shebang broken:** `mypy` symlink in venv had a bad shebang (`/bin/bash: ne peut exécuter`). Worked around by invoking `python -m mypy` instead. Pre-existing venv issue (not introduced by this plan); unrelated to plan scope.
- **`venv/bin/pip` similarly broken:** Same shebang issue. Used `python -m pip install interrogate`. Same pre-existing condition.

## ASP Requirement Satisfaction

| Requirement | Status                          | Evidence                                                                                                                                      |
| ----------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **ASP-02**  | **Satisfied**                   | `from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED` works; sums are 5/7/14; tests `test_classical_mask_shape_and_sum` etc.     |
| **ASP-04**  | **Foundation satisfied**        | `resolve_aspect_set(None)` returns CLASSICAL — observable via `test_resolve_none_returns_classical`. The actual API parameter wiring (e.g. `calculate_aspects(aspects=None)`) lives in plan 09-04a/b. |
| **ASP-05**  | **Foundation satisfied**        | Resolver returns a single boolean mask in one call — ready for hot-loop replacement in plan 09-04a (calculator refactor).                       |
| **ASP-06**  | **Documented (not enforced)**   | Forward-looking cache rule in module docstring and inline comment near resolver. No new caches added in this plan, so no enforcement is needed yet. Wave 2 plan 09-04a must respect this rule if it adds caching. |

## Self-Check: PASSED

- `ketu/aspects/presets.py` — FOUND (229 lines, 100% interrogate, 100% test coverage)
- `ketu/aspects/__init__.py` — FOUND (modified, re-exports verified)
- `tests/test_aspect_presets.py` — FOUND (357 lines, 56 tests passing)
- Commit `f223271` (Task 1) — FOUND
- Commit `78085d1` (Task 2) — FOUND
- Commit `5481408` (Task 3) — FOUND
- mypy --strict on presets.py — PASSES
- interrogate -f 95 on presets.py — PASSES (100%)
- Full test suite (479 tests) — PASSES
- `git diff ketu/core.py` — empty (append-only invariant preserved)

## Next Phase Readiness

- **Plan 09-04a (calculator-refactor) unblocked:** Can import `resolve_aspect_set` and replace `enumerate(aspects["angle"])` hot loops with mask-filtered iteration per research Pattern 2.
- **Plan 09-04b (default-migration) unblocked:** Public API parameters can switch to `aspects=None` and resolve internally — resolver semantics are pinned by 56 tests.
- **Plan 09-05 (integration-and-benchmark) unblocked for Wave 3:** Resolver behavior is fully specified and tested; benchmark can compare CLASSICAL fast path vs EXTENDED legacy path.
- **No blockers introduced.** ASP-06 is documented, not enforced — Wave 2 plans must continue to respect "no aspect-set-dependent caches without mask hash in key" rule (the only LRU caches in scope, `body_properties` and `_cached_planet_position_batch`, do not memoize aspect output).

---
*Phase: 09-configurable-aspects*
*Plan: 02 (presets-module)*
*Completed: 2026-05-06*
