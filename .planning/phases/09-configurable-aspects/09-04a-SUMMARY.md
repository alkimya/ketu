---
phase: 09-configurable-aspects
plan: 04a
subsystem: api
tags: [aspects, calculator, refactor, configurable, kala-contract, mypy-strict]

# Dependency graph
requires:
  - phase: 09-02-presets-module
    provides: "ketu/aspects/presets.py — CLASSICAL/TRADITIONAL/EXTENDED frozen masks, AspectSetSpec type, resolve_aspect_set() resolver"
  - phase: 09-03-invariant-test
    provides: "sha256-fingerprinted core.aspects 14-row invariant — ensures preset masks remain valid"
provides:
  - "calculate_aspects(jd, *, aspects=None) — defaults to CLASSICAL via resolver"
  - "calculate_aspects_vectorized(jd, *, aspects=None) — refactored hot loop emits canonical i_asp"
  - "calculate_aspects_batch(jd_array, *, aspects=None) — resolver runs ONCE above per-date loop"
  - "find_aspects_between_dates(jd0, jd1, body1, body2, aspects=None) — filters search to selected angles"
  - "module-level rename: ketu.core.aspects -> _CORE_ASPECTS (frees parameter name)"
affects: [09-04b-default-migration, 09-05-integration-and-benchmark]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Resolver-once-above-hot-loop: resolve_aspect_set called at API entry, never inside per-date / per-pair loops"
    - "Canonical i_asp emission: enumerate(selected_indices) yields (k, i_asp); emit i_asp (NOT k) to preserve Kala positional contract"
    - "Module-level rename to _CORE_ASPECTS: frees the public parameter name `aspects=` while keeping the imported registry available internally"
    - "Post-hoc subset filter for low-level scanner reuse: calculate_aspects() reuses get_aspect() (out of scope) and filters its output by selected_indices_set rather than rewriting the scanner"

key-files:
  created: []
  modified:
    - "ketu/aspects/calculator.py — 4 public APIs gain aspects= parameter; 2 hot loops refactored; module import renamed"

key-decisions:
  - "calculate_aspects() retains its delegation to get_aspect() (the single-match scanner stays out of scope per ASP-07) and filters get_aspect() output post-hoc against selected_indices_set — preserves single source of truth for the scalar match logic without rewriting it"
  - "All four signatures use `aspects: AspectSetSpec = None` (NOT `aspects=CLASSICAL`) — research Pitfall 5 (mutable-default trap) + ASP-04 resolver-driven default"
  - "Hot-loop variable named `i_asp_val` (instead of shadowing `i_asp`) makes the int-cast intent explicit: `i_asp = int(i_asp_val)` clearly converts np.intp -> Python int before being emitted"
  - "find_aspects_between_dates internal asp_idx lookup uses _CORE_ASPECTS['angle'] (full 14 rows), NOT selected_angles — yields a canonical 0-13 index even when the search list was filtered, matching the Kala-style positional contract"

patterns-established:
  - "Resolver-once invariant: every public multi-aspect API in calculator.py calls resolve_aspect_set exactly once at entry; downstream loops consume only mask/selected_indices/selected_angles/selected_coefs locals"
  - "Type-annotated mask locals: `mask: npt.NDArray[np.bool_]`, `selected_indices: npt.NDArray[np.intp]`, etc. — gives mypy --strict full visibility and matches presets.py prior art"
  - "Comment-vs-code distinction in negative-grep verification: `grep -nE '^\\s*[^#].*\\baspects\\['` skips comments — surviving line 495 is a comment-only reference to documentation"

# Metrics
duration: 6m 34s
completed: 2026-05-07
---

# Phase 09 Plan 04a: Calculator Refactor Summary

**Threaded `aspects=AspectSetSpec` parameter through the four public multi-aspect APIs in `calculator.py`, refactored both hot loops to enumerate `selected_indices` while preserving Kala's canonical `i_asp` positional contract, and renamed the module-level `aspects` import to `_CORE_ASPECTS` — 479 tests pass with no test-file retrofit needed.**

## Performance

- **Duration:** 6m 34s
- **Started:** 2026-05-06T22:52:27Z
- **Completed:** 2026-05-06T22:59:01Z
- **Tasks:** 2 (1 discovery, 1 refactor)
- **Files modified:** 1 (`ketu/aspects/calculator.py`)

## Accomplishments

- Four public multi-aspect APIs (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`) accept `aspects: AspectSetSpec = None` parameter; `None` resolves to CLASSICAL (5 majors)
- Two hot loops refactored to `for k, i_asp_val in enumerate(selected_indices):` — emit canonical `int(i_asp)` (NOT `k`); Kala's positional contract preserved (verified: `i_asp` only ever in `{0, 4, 7, 9, 13}` for CLASSICAL)
- Resolver runs ONCE per API call; in `calculate_aspects_batch`, ABOVE the per-date loop (not per-date)
- Module-level `from ketu.core import bodies, aspects` renamed to `from ketu.core import bodies, aspects as _CORE_ASPECTS`; all 9 internal `aspects[` references updated; zero code-level `aspects[` references remain
- `find_aspects_between_dates` passes filtered `selected_angles` to downstream `find_all_aspects` — no leak of unselected aspects into the search
- `get_aspect` (single-match scanner) and `find_aspect_timing` (single-aspect timing search) untouched per ASP-07 scope (only the rename touches `find_aspect_timing`)

## Task Commits

1. **Task 1: Pre-execution discovery — locate hot loops by pattern and enumerate test-file blast radius** — discovery-only (no commit; outputs captured in this SUMMARY below)
2. **Task 2: Refactor calculator.py — rename core import, thread aspects= through four public functions, refactor hot loops, filter find_aspects_between_dates** — `d621415` (feat)

**Plan metadata:** _to be appended after final commit_

## Pre-execution Discovery (Task 1 verbatim grep output)

### Grep 1: Hot-loop sites in calculator.py
```
$ grep -n 'enumerate(aspects\["angle"\])' ketu/aspects/calculator.py
64:    for i_asp, aspect in enumerate(aspects["angle"]):       # get_aspect — OUT OF SCOPE
143:    for i_asp, aspect_angle in enumerate(aspects["angle"]):  # _vectorized — IN SCOPE
239:        for i_asp, aspect_angle in enumerate(aspects["angle"]):  # _batch — IN SCOPE
```
**Verdict:** Exactly 3 sites, 2 in scope (matches plan expectation).

### Grep 2: Module-level `aspects[` and `aspects,` references to rename
```
$ grep -n 'aspects\[\|aspects,' ketu/aspects/calculator.py
40:    orbs, coef = bodies["orb"], aspects["coef"]               # get_orb body
64:    for i_asp, aspect in enumerate(aspects["angle"]):         # get_aspect loop
143:   for i_asp, aspect_angle in enumerate(aspects["angle"]):   # vectorized loop
147:       aspect_coef = aspects["coef"][i_asp]                  # vectorized coef lookup
239:       for i_asp, aspect_angle in enumerate(aspects["angle"]):  # batch loop
240:           aspect_coef = aspects["coef"][i_asp]              # batch coef lookup
288:   asp_idx = np.where(aspects["angle"] == aspect_value)[0]   # find_aspect_timing
370:   aspect_list = find_all_aspects(... list(aspects["angle"]))  # find_aspects_between_dates
374:   asp_idx = np.where(aspects["angle"] == aspect_angle)[0][0]  # find_aspects_between_dates lookup
375:   aspect_name_bytes = aspects["name"][asp_idx]              # find_aspects_between_dates name
```
**Verdict:** 9 module-level references; ALL renamed to `_CORE_ASPECTS[`. Lines 143/147/239/240 also restructured by hot-loop refactor.

### Grep 3: `find_aspects_between_dates` aspect iteration
```
$ grep -n 'list(aspects\["angle"\])' ketu/aspects/calculator.py
370:   aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(aspects["angle"]))
```
**Verdict:** Single site; rewritten to `list(selected_angles)` after resolver runs.

### Grep 4: Test-file blast radius
```
$ grep -rln 'calculate_aspects\b\|calculate_aspects_vectorized\|calculate_aspects_batch' tests/
tests/benchmark_aspects_batch.py        — Plan 09-01 baseline harness (uses --aspect-set flag, threads through)
tests/benchmark.py                      — DEAD (broken `from ketu import ketu_refactored`); skip per Plan 09-01
tests/test_refactored.py                — calls calculate_aspects(jd) and find_aspects_between_dates(...) — both default-flip safe (loose count assertions)
tests/test_coverage_improvements.py     — 6 find_aspects_between_dates tests + 2 calculate_aspects_* tests; all pass
tests/test_ketu.py                      — calls calculate_aspects(jd) inside structural assertions and a perf loop; pass
tests/test_aspects_vectorization.py     — asserts calculate_aspects == calculate_aspects_vectorized at multiple JDs; pass (both default to CLASSICAL identically)
tests/test_regression/test_bug_02_aspects.py  — bug-02 regression: loop vs vectorized parity; pass (both default to CLASSICAL)
```
**Verdict:** 7 files (the plan listed 6; tests/benchmark_aspects_batch.py was added in Plan 09-01 since this plan was authored). NO retrofits needed — all tests use loose counts (`>= 1`, structure checks, parity assertions between sibling functions). Default-flip from EXTENDED-era to CLASSICAL did not break any assertion.

### Grep 5: `find_aspects_between_dates` external callers
```
$ grep -rln 'find_aspects_between_dates' ketu/ tests/
ketu/display.py                                 — CLI consumer (no kwargs; default flip is intentional)
ketu/aspects/__init__.py                        — re-export
ketu/aspects/README.md                          — documentation
ketu/aspects/calculator.py                      — definition site
tests/test_refactored.py                        — see Grep 4
tests/test_coverage_improvements.py             — see Grep 4
tests/benchmark.py                              — DEAD per Plan 09-01
```
**Verdict:** No production caller passes a positional 5th argument that would collide with the new `aspects=` kwarg. ketu/display.py uses positional `(jd_start, jd_end, body1, body2)` — clean default.

### Grep 6: LRU cache audit
```
$ grep -n '@lru_cache\|@functools\.lru_cache' ketu/aspects/*.py ketu/calculations.py
ketu/aspects/core.py:72:@lru_cache(maxsize=256)         _cached_planet_position_batch(jd_tuple, planet_id)
ketu/calculations.py:94:@lru_cache(maxsize=1024)        body_properties(jdate, body)
```

| Cache | Function | Aspect-set dependent? | Verdict |
|-------|----------|-----------------------|---------|
| `ketu/calculations.py:94` | `body_properties(jdate, body)` | NO — caches a single body's position; aspect set is downstream of position | **safe** |
| `ketu/aspects/core.py:72` | `_cached_planet_position_batch(jd_tuple, planet_id)` | NO — caches batch positions for ONE planet; aspect set never enters the call | **safe** |

**Forward-looking ASP-06 rule (per Plan 09-02 SUMMARY):** if any future cache memoizes a function whose return value depends on the resolved aspect set, its cache key MUST include `mask.tobytes()` to avoid stale results across different aspect sets. No such cache exists today.

## Files Created/Modified

- `ketu/aspects/calculator.py` — module-level `aspects` import renamed to `_CORE_ASPECTS`; four public APIs gain `aspects: AspectSetSpec = None` parameter; two hot loops refactored from `enumerate(aspects["angle"])` to `enumerate(selected_indices)` emitting canonical `int(i_asp)`; `find_aspects_between_dates` filters its downstream `find_all_aspects` call to `list(selected_angles)`; numpydoc Parameters and Notes sections added to all four modified signatures.

## Function-by-function refactor summary

| Function | Before signature | After signature | Hot-loop change | Where resolver runs |
|----------|------------------|-----------------|-----------------|---------------------|
| `calculate_aspects` | `(jdate, l_bodies=bodies)` | `(jdate, l_bodies=bodies, aspects: AspectSetSpec = None)` | Reuses `get_aspect`; post-hoc filter via `selected_indices_set` | At top of body |
| `calculate_aspects_vectorized` | `(jdate, l_bodies=bodies)` | `(jdate, l_bodies=bodies, aspects: AspectSetSpec = None)` | `enumerate(aspects["angle"])` → `enumerate(selected_indices)`; emit `int(i_asp)` not `k` | Above pair-distance computation |
| `calculate_aspects_batch` | `(jd_array, l_bodies=bodies)` | `(jd_array, l_bodies=bodies, aspects: AspectSetSpec = None)` | Same as `_vectorized` | **Above the per-date loop** (per ASP-05) |
| `find_aspects_between_dates` | `(jd0, jd1, body1=None, body2=None)` | `(jd0, jd1, body1=None, body2=None, aspects: AspectSetSpec = None)` | `list(aspects["angle"])` → `list(selected_angles)` in `find_all_aspects` call | Top of body |

## Smoke-test transcripts

### `calculate_aspects` family (2025-01-01 UTC)
```
$ python -c "<smoke from plan>"
OK default= 12 classical= 12 extended= 25
CLASSICAL i_asp codes: [0, 4, 7, 9, 13]            # ← only canonical major indices
EXTENDED  i_asp codes: [0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
```
- `default == CLASSICAL`: ✅ (12 rows each, sorted-equal)
- CLASSICAL i_asp ⊆ {0, 4, 7, 9, 13}: ✅ (Kala canonical contract preserved)
- EXTENDED includes harmonics 1, 5, 6, 8, 10, 11, 12: ✅ (legacy v1.0 behavior reproducible via `aspects=EXTENDED`)
- ratio extended/classical = 25/12 ≈ 2.08 (consistent with EXTENDED having 14 aspects vs CLASSICAL 5)

### `find_aspects_between_dates` (2025-01-01 to 2025-01-08, Sun-Moon)
```
$ python -c "<smoke from plan>"
OK def= 1 cls= 1 ext= 1
cls names: {'Square'}
ext names: {'Square'}
```
- `default == CLASSICAL`: ✅
- CLASSICAL aspect names ⊆ {Conjunction, Sextile, Square, Trine, Opposition}: ✅
- Single Sun-Moon Square in this 7-day window — present in all three aspect sets (Square is a major)

## Verification gate results

| Gate | Result |
|------|--------|
| `python -c "from ketu.aspects import calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch, find_aspects_between_dates, CLASSICAL, EXTENDED"` | ✅ Imports OK |
| `grep -nE '^\s*[^#].*\baspects\[' ketu/aspects/calculator.py` (code-level) | ✅ Zero matches (line 495 is a comment-only reference) |
| `grep -n 'enumerate(selected_indices)' ketu/aspects/calculator.py` | ✅ 2 matches (lines 210, 340) |
| `git diff -U0 ketu/aspects/windows.py \| grep -E "^\+.*def find_aspect_window"` | ✅ Empty (windows.py untouched — boundary respected for Plan 09-04b) |
| Behavior smoke `calculate_aspects(jd)` default vs CLASSICAL vs EXTENDED | ✅ default == CLASSICAL; CLASSICAL i_asp ⊆ {0,4,7,9,13}; EXTENDED has 25 rows on test date |
| Behavior smoke `find_aspects_between_dates` default vs CLASSICAL vs EXTENDED | ✅ default == CLASSICAL; names ⊆ majors |
| Full test suite `pytest tests/ --no-cov` | ✅ 479 passed, 0 failed |
| Targeted blast-radius `pytest tests/test_aspects_vectorization.py tests/test_ketu.py tests/test_refactored.py tests/test_coverage_improvements.py tests/test_regression/test_bug_02_aspects.py -x` | ✅ 63 passed |
| `mypy --strict ketu/aspects/calculator.py` | ✅ Success: no issues found in 1 source file |
| `interrogate ketu/aspects/calculator.py -f 95` | ✅ PASSED (100.0% docstring coverage) |
| `files_modified` discipline | ✅ Only `ketu/aspects/calculator.py` modified — no leak into windows/timelines/transits (Plan 09-04b territory) |

## Test-file retrofit list

**None.** All 7 test files in the blast radius pass without modification.

The plan anticipated possible `aspects=EXTENDED` retrofits where v1.0-era assertions hardcoded EXTENDED counts. None occurred because:
- `tests/test_aspects_vectorization.py` and `tests/test_regression/test_bug_02_aspects.py` assert PARITY between `calculate_aspects` and `calculate_aspects_vectorized`. Both functions now default to CLASSICAL identically — parity preserved.
- `tests/test_ketu.py` and `tests/test_coverage_improvements.py` use loose structural / count-bounded assertions (`len >= 1`, `0 <= i_asp < 14`, dtype.names matches).
- `tests/test_refactored.py` `test_find_aspects_between_dates` only prints results without count assertions.
- `tests/benchmark.py` is dead (broken import per Plan 09-01) — skipped.

## Decisions Made

1. **`calculate_aspects` reuses `get_aspect` and filters post-hoc** — Rather than rewriting the scalar match logic for the parameter, the wrapper keeps its `[get_aspect(jdate, *comb) for comb in combs(...)]` body and adds a post-hoc filter `int(aspect[2]) in selected_indices_set`. This preserves single source of truth for the scalar match logic (only `get_aspect` knows the conjunction-special-case rule) without violating ASP-07 scope (which excludes `get_aspect` from parameter changes).

2. **All four signatures use `aspects=None` literal default** — never `aspects=CLASSICAL`. Per research Pitfall 5 (mutable-default trap): even though CLASSICAL is a frozen `np.bool_` array, the resolver-driven default keeps a single source of truth (`resolve_aspect_set(None) → CLASSICAL`) and avoids surprises if CLASSICAL itself ever changed.

3. **Hot-loop variable named `i_asp_val` then re-bound** — `for k, i_asp_val in enumerate(selected_indices): i_asp = int(i_asp_val)`. Two reasons: (a) makes the np.intp → Python int conversion explicit (the structured-array dtype expects `i4`); (b) preserves the existing `if i_asp == 0:  # Conjunction` idiom unchanged.

4. **`find_aspects_between_dates` looks up canonical i_asp via FULL `_CORE_ASPECTS["angle"]`** — not against `selected_angles`. The `np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]` lookup yields the canonical 0-13 index even when the search list was filtered to a subset, matching Kala's positional contract.

## Deviations from Plan

**None - plan executed exactly as written.**

The plan was thorough enough that no Rule 1/2/3 fixes were needed:
- Rule 1 (auto-fix bugs): no bugs surfaced; all gates passed cleanly.
- Rule 2 (auto-add missing critical functionality): plan was complete (resolver positioning, type annotations, mypy --strict, docstrings, Kala-contract preservation all explicitly specified).
- Rule 3 (auto-fix blocking issues): all imports and dependencies (presets module, AspectSetSpec) were already in place from Wave 1 (Plan 09-02).

The minor *clarification* in Decision 1 (post-hoc filter for `calculate_aspects` instead of rewriting `get_aspect`) was resolved within plan guidance — the plan explicitly says "If `calculate_aspects` is implemented as a thin wrapper over `calculate_aspects_vectorized`, just add `aspects=` and pass it through. If it has its own hot loop, refactor identically." Since `calculate_aspects` does neither (it wraps `get_aspect`), the post-hoc filter is the natural third path consistent with "`get_aspect` stays UNCHANGED — out of scope".

## Issues Encountered

**None.** Single-pass execution: discovery → refactor → verify → commit.

One spurious-looking observation: `git status --short ketu/aspects/` initially showed `M` flags on `windows.py`, `timelines.py`, `transits.py`. This was stale index cache; `git status` (full) confirmed those files clean. Confirmed `git diff HEAD ketu/aspects/{windows,timelines,transits}.py` returns empty — boundary with Plan 09-04b respected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 09-04a closes calculator.py-side ASP-03/04/05/07 coverage. Wave 2 remaining work:
- **Plan 09-04b** (parallel sibling — `windows.py` / `timelines.py` / `transits.py` default-list migration) is **unblocked** and independent (this plan's `_CORE_ASPECTS` rename is contained to `calculator.py`).
- **Plan 09-05** (integration + benchmark — runs the v1.0 baseline harness against the now-CLASSICAL default and verifies <5% drift) waits on both 09-04a and 09-04b being merged.

The Kala contract was the highest-risk surface; smoke tests confirm it is preserved (`r_classical['i_asp']` codes are exactly `{0, 4, 7, 9, 13}` — never renumbered to `{0, 1, 2, 3, 4}`). Wave 3 (Plan 09-05) integration testing should compare `calculate_aspects_batch` output with v1.0 baseline using `aspects=EXTENDED` for byte-equality and `aspects=CLASSICAL` for default-default benchmark.

---
*Phase: 09-configurable-aspects*
*Completed: 2026-05-07*

## Self-Check: PASSED

- File exists: `.planning/phases/09-configurable-aspects/09-04a-SUMMARY.md` ✅
- File exists: `ketu/aspects/calculator.py` ✅
- Commit exists: `d621415` (Task 2 calculator.py refactor) ✅
