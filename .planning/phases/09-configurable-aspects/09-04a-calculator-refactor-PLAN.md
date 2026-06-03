---
phase: 09-configurable-aspects
plan: 04a
type: execute
wave: 2
depends_on:
  - "09-02"
files_modified:
  - ketu/aspects/calculator.py
autonomous: true
plan_id: "09-04a"
requirements:
  - ASP-03
  - ASP-04
  - ASP-05
  - ASP-07

must_haves:
  truths:
    - "calculate_aspects(jd, aspects=None) returns CLASSICAL output by default"
    - "calculate_aspects(jd, aspects=EXTENDED) reproduces v1.0 14-aspect behavior"
    - "calculate_aspects_vectorized accepts aspects= and behaves identically to calculate_aspects on default semantics"
    - "calculate_aspects_batch accepts aspects= and behaves identically; resolver runs ONCE above the per-date loop"
    - "find_aspects_between_dates accepts aspects= and threads it into find_all_aspects (no leak of non-selected aspect angles)"
    - "Hot loops at calculator.py (currently :143 and :239 — orientation only; locate by pattern) emit canonical i_asp from selected_indices[k], NOT k"
    - "Module-level `from ketu.core import aspects` is renamed to `from ketu.core import aspects as _CORE_ASPECTS` to avoid parameter-shadowing"
    - "get_aspect (low-level single-match scanner) is NOT modified — out of scope per research line 514"
  artifacts:
    - path: "ketu/aspects/calculator.py"
      provides: "calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch, find_aspects_between_dates with aspects= parameter"
      contains: "resolve_aspect_set"
  key_links:
    - from: "ketu/aspects/calculator.py"
      to: "ketu/aspects/presets.py"
      via: "resolve_aspect_set called once at top of each public multi-aspect function"
      pattern: "from ketu\\.aspects\\.presets import resolve_aspect_set"
    - from: "ketu/aspects/calculator.py hot loops"
      to: "selected_indices array"
      via: "enumerate(selected_indices) emits canonical i_asp 0-13"
      pattern: "enumerate\\(selected_indices\\)"
    - from: "ketu/aspects/calculator.py find_aspects_between_dates"
      to: "find_all_aspects(...)"
      via: "selected_angles passed instead of full list(aspects['angle'])"
      pattern: "find_all_aspects\\(.*selected_angles"
---

<objective>
Refactor `ketu/aspects/calculator.py` ONLY: thread `aspects=` parameter through all four public multi-aspect functions (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`), rewrite the two hot loops to emit canonical `i_asp` from `selected_indices[k]`, and rename the module-level `aspects` import to `_CORE_ASPECTS` to free the parameter name.

Purpose: ASP-03 (parameter on multi-aspect APIs), ASP-04 (default = CLASSICAL), ASP-05 (resolver once at entry, no filter inside hot loops), ASP-07 foundation (all public aspect APIs accept `aspects=` — verified via grep that `find_aspects_between_dates` iterates aspect angles and is publicly exported, so it is REQUIRED in scope, not conditional).

Scope split rationale: this plan is calculator.py-only. The four hardcoded-list default migrations in `windows.py`, `timelines.py`, `transits.py` move to Plan 09-04b (parallel with this plan in Wave 2; both depend only on 09-02 presets). Splitting fits the ~50% context budget and isolates the highest-risk file (calculator.py — Kala contract).

Output:
- `ketu/aspects/calculator.py` — four functions get `aspects=AspectSetSpec = None` parameter; the two hot loops are refactored to iterate `selected_indices`; `find_aspects_between_dates` filters the angle list passed to `find_all_aspects`; module-level `aspects` import is renamed to `_CORE_ASPECTS`.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/09-configurable-aspects/09-RESEARCH.md
@.planning/phases/09-configurable-aspects/09-02-SUMMARY.md

# The file being refactored (the only file modified in this plan)
@ketu/aspects/calculator.py

# The presets module being consumed (created in Plan 09-02)
@ketu/aspects/presets.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-execution discovery — locate hot loops by pattern and enumerate dependent test files</name>
  <files>(no files modified — discovery step; outputs feed Task 2 grep audits)</files>
  <action>
    Before editing, run these greps to lock down the actual hot-loop sites and the test-file blast radius (line numbers in this plan are for ORIENTATION only — code may have drifted since the research pass; rely on patterns, not line numbers):

    1. Hot-loop sites in calculator.py:
        grep -n 'enumerate(aspects\["angle"\])' ketu/aspects/calculator.py
       Expect: three sites (one in `get_aspect` — OUT OF SCOPE; two in `calculate_aspects_vectorized` and `calculate_aspects_batch` — IN SCOPE). Record the actual line numbers in the SUMMARY.

    2. Module-level `aspects` import sites that need renaming:
        grep -n 'aspects\[\|aspects,' ketu/aspects/calculator.py
       Every match must be classified: either (a) refers to the module-level imported `aspects` from `ketu.core` and must become `_CORE_ASPECTS`, or (b) refers to a parameter/local — leave alone.

    3. find_aspects_between_dates aspect iteration:
        grep -n 'list(aspects\["angle"\])' ketu/aspects/calculator.py
       Expected at the call to `find_all_aspects(...)`. This site MUST be filtered to `selected_angles` after Task 2's resolver runs.

    4. Test files that call calculate_aspects / _vectorized / _batch (default-flip blast radius — Task 2 will need to retrofit any that hardcoded EXTENDED-era expectations):
        grep -rln 'calculate_aspects\b\|calculate_aspects_vectorized\|calculate_aspects_batch' tests/
       Expected list (verified): tests/benchmark.py, tests/test_ketu.py, tests/test_refactored.py, tests/test_coverage_improvements.py, tests/test_regression/test_bug_02_aspects.py, tests/test_aspects_vectorization.py.
       Document each file in SUMMARY: per-file count of call sites and whether any needed `aspects=EXTENDED` retrofit to preserve v1.0 expectations.

    5. find_aspects_between_dates external callers (out-of-test blast radius):
        grep -rln 'find_aspects_between_dates' ketu/ tests/
       Expected: ketu/display.py, ketu/aspects/__init__.py (re-export), tests/benchmark.py, tests/test_coverage_improvements.py, tests/test_refactored.py.

    6. LRU-cache audit for ASP-06 (verify no current cache materializes filtered aspect output):
        grep -n '@lru_cache\|@functools\.lru_cache' ketu/aspects/*.py ketu/calculations.py
       For each match, manually confirm the cached function's return value does NOT depend on aspect-set filtering. Document audit result in SUMMARY (mapping function → "safe / requires-key-update").

    Record all six grep outputs verbatim in `09-04a-SUMMARY.md` so the executor and the checker can reproduce the discovery.
  </action>
  <verify>
    All six greps run successfully. Hot-loop site count is exactly three (get_aspect + vectorized + batch); modify only the latter two. Test-file list matches the six expected files (or document any new file added since this plan was written). No surprise LRU cache touches aspect output.
  </verify>
  <done>
    Discovery outputs captured for the SUMMARY. Executor has a definitive list of: (a) two in-scope hot-loop sites in calculator.py, (b) every module-level `aspects[` reference to rename, (c) the test-file blast radius, (d) cache audit result.
  </done>
</task>

<task type="auto">
  <name>Task 2: Refactor calculator.py — rename core import, thread aspects= through four public functions, refactor hot loops, filter find_aspects_between_dates</name>
  <files>ketu/aspects/calculator.py</files>
  <action>
    Edit `ketu/aspects/calculator.py` IN PLACE. Apply changes in the order below to keep diffs reviewable.

    **Step 1 — Add the presets import (after the existing `from ketu.core import bodies, aspects` line):**

        from ketu.aspects.presets import resolve_aspect_set, AspectSetSpec

    **Step 2 — Rename the module-level `aspects` import to `_CORE_ASPECTS`:**

        # CHANGE:
        #   from ketu.core import bodies, aspects
        # TO:
        from ketu.core import bodies, aspects as _CORE_ASPECTS

    Then update every reference inside this file. Per Task 1's grep, the references live around lines 40, 64, 143, 147, 239, 240, 288, 370, 374, 375 (orientation only — re-locate by pattern). Each `aspects[` becomes `_CORE_ASPECTS[`. Verify with:
        grep -n '\baspects\[' ketu/aspects/calculator.py
    Should return ZERO matches after the edit (every `aspects[` is now `_CORE_ASPECTS[`). The token `aspects` should appear only as: the new parameter name in four signatures, the import-as alias on the import line, and inside docstrings.

    **Step 3 — `calculate_aspects_vectorized` (hot loop site #1):**

    Update the signature to add `aspects: AspectSetSpec = None` (keep `aspects=None` as the literal default — never `aspects=CLASSICAL`, per research Pitfall 5 mutable-default trap and ASP-04 resolver-driven default).

    At the top of the function body (above the existing `i_indices, j_indices = ...` setup):

        mask = resolve_aspect_set(aspects)              # length-14 bool, ONCE per call
        selected_indices = np.where(mask)[0]            # canonical 0-13 indices, dtype intp
        selected_angles = _CORE_ASPECTS["angle"][mask]  # filtered, parallel to selected_indices
        selected_coefs = _CORE_ASPECTS["coef"][mask]

    Replace the existing hot loop (currently `for i_asp, aspect_angle in enumerate(aspects["angle"])` near line 143):

        # OLD:
        for i_asp, aspect_angle in enumerate(aspects["angle"]):
            ...
            aspect_coef = aspects["coef"][i_asp]
            ...

        # NEW:
        for k, i_asp in enumerate(selected_indices):
            aspect_angle = float(selected_angles[k])
            aspect_coef = float(selected_coefs[k])
            ...

    CRITICAL — Kala contract preservation: the `results.append((..., i_asp, ...))` line MUST emit `int(i_asp)` (the canonical index from `selected_indices[k]`), NOT `k` (filtered subset position). Per research Pitfall 1: "Renumbering `i_asp` to be 0..N-1 within the selected set... breaks Kala's positional lookup."

    The `if i_asp == 0:  # Conjunction` branch is correct as-is — `i_asp == 0` still means "Conjunction" canonically. After refactor, Conjunction is in CLASSICAL (index 0 → True in mask → first iteration emits i_asp=0).

    **Step 4 — `calculate_aspects_batch` (hot loop site #2):**

    Update the signature to add `aspects: AspectSetSpec = None`.

    PERFORMANCE-CRITICAL: resolver MUST be called ABOVE the per-date loop (`for date_idx in range(n_dates):` near line 234), NOT inside it. Per research: "the per-aspect-type loop is INSIDE the per-date loop — but the resolver itself must execute once per API call (above the date loop), not per date."

    Apply the same pattern as Step 3, but place the four `mask`/`selected_*` locals ABOVE the date loop, not inside it. The inner aspect loop (currently `for i_asp, aspect_angle in enumerate(aspects["angle"])` near line 239) becomes `for k, i_asp in enumerate(selected_indices):`. The append site emits `int(i_asp)`.

    **Step 5 — `calculate_aspects` (the scalar/wrapper function):**

    Read the actual body before editing. If `calculate_aspects` is implemented as a thin wrapper over `calculate_aspects_vectorized`, just add `aspects: AspectSetSpec = None` to its signature and pass it through. If it has its own hot loop (separate from `get_aspect`), refactor identically to Step 3. Note: `get_aspect` (line 44, single-match scanner) stays UNCHANGED — out of scope.

    **Step 6 — `find_aspects_between_dates` (currently lines 331-380):**

    Per Task 1 grep, this function calls `find_all_aspects(jdate_start, jdate_end, b1, b2, list(aspects["angle"]))` — it iterates over the FULL angle list, then maps results back via `np.where(aspects["angle"] == aspect_angle)`. This is a multi-aspect API per ASP-07 ("all public aspect APIs"), and it is publicly exported in `__all__` and re-exported by `ketu/aspects/__init__.py`. It MUST accept `aspects=`.

    Update signature:
        def find_aspects_between_dates(
            jdate_start: float,
            jdate_end: float,
            body1: Optional[int] = None,
            body2: Optional[int] = None,
            aspects: AspectSetSpec = None,
        ) -> List[Tuple]:

    At the top of the body (above the `pairs = ...` selection block):

        mask = resolve_aspect_set(aspects)
        selected_angles = _CORE_ASPECTS["angle"][mask]
        # The downstream find_all_aspects call iterates the angle list; passing the
        # filtered list confines the search to the selected aspects only.

    Then change:
        # OLD:
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(aspects["angle"]))
        # NEW:
        aspect_list = find_all_aspects(jdate_start, jdate_end, b1, b2, list(selected_angles))

    The downstream `np.where(_CORE_ASPECTS["angle"] == aspect_angle)[0][0]` lookup naturally yields a canonical 0-13 index — no renumbering, no further changes needed there. (If two angles ever collide — they don't in v1.0 — this would need disambiguation, but core.aspects has no duplicate angles.)

    Add to docstring Parameters:

        aspects : AspectSetSpec, default None
            Aspect set to search for. None resolves to CLASSICAL (5 majors).
            Accepts a preset name ("classical", "traditional", "extended"),
            a list of aspect names or indices, or a length-14 boolean mask.

    **Step 7 — Numpydoc updates for the four modified signatures:**

    For each modified signature, add to the Parameters section:

        aspects : AspectSetSpec, default None
            Aspect set to compute. None resolves to CLASSICAL (5 majors:
            Conjunction, Sextile, Square, Trine, Opposition). Accepts a preset
            name ("classical", "traditional", "extended"), a list of aspect
            names or indices, or a length-14 boolean mask. The result's
            ``i_asp`` field is always a canonical 0-13 index into
            ``ketu.core.aspects``, regardless of the selected subset.

    Add a Notes section to the three structured-array-returning functions documenting the canonical-i_asp invariant:

        Notes
        -----
        The ``i_asp`` field in the returned structured array is the canonical
        index into ``ketu.core.aspects`` (0-13), not a position within the
        selected subset. Downstream consumers (e.g. Kala) rely on this
        positional contract.

    **Step 8 — Mypy strict:**
    - `AspectSetSpec` is the imported type alias.
    - `mask`, `selected_indices`, `selected_angles`, `selected_coefs` are `np.ndarray`. If mypy needs help, annotate explicitly (existing aspect modules already use `npt.NDArray[np.bool_]` etc. — match prior art).

    **Step 9 — Test-file retrofit (the default-flip blast):**

    Per Task 1 grep, six test files call the modified APIs. After Step 8, run:
        pytest tests/test_ketu.py tests/test_refactored.py tests/test_coverage_improvements.py tests/test_regression/test_bug_02_aspects.py tests/test_aspects_vectorization.py -x -v

    For ANY failure caused by the default flip (test asserts EXTENDED-era counts/i_asp values), the fix is to add `aspects=EXTENDED` to the call site to PRESERVE the v1.0 expectation. DO NOT loosen assertions to `>= 0` or similar. Document each retrofit in SUMMARY (file:line, before, after, reason).

    Skip `tests/benchmark.py` — it has dead `from ketu import ketu_refactored` imports (verified by Plan 09-01) and is not part of the active test suite.

    **Anti-patterns to NOT introduce (per research):**
    - Do NOT filter inside the per-pair loop (`if i_asp in selected_indices: ...`) — pre-filter ONCE.
    - Do NOT mutate `_CORE_ASPECTS` (no `_CORE_ASPECTS = _CORE_ASPECTS[mask]`).
    - Do NOT renumber emitted i_asp.
    - Do NOT use `aspects=CLASSICAL` as the default in any signature — use `aspects=None`.
    - Do NOT add `aspects=` to `get_aspect` (single-match scanner) or `find_aspect_timing` (single-aspect timing search) — both out of scope per research line 514.
    - Do NOT modify `ketu/aspects/windows.py`, `timelines.py`, or `transits.py` in this plan — those four hardcoded-list defaults belong to Plan 09-04b.
  </action>
  <verify>
    Smoke import: `python -c "from ketu.aspects import calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch, find_aspects_between_dates, CLASSICAL, EXTENDED"` — succeeds.

    Behavior smoke (calculate_aspects family):
        python -c "
        from ketu.aspects import calculate_aspects, EXTENDED, CLASSICAL
        from ketu.calculations import utc_to_julian
        from datetime import datetime, timezone
        jd = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
        r_default = calculate_aspects(jd)
        r_classical = calculate_aspects(jd, aspects=CLASSICAL)
        r_extended = calculate_aspects(jd, aspects=EXTENDED)
        assert sorted(r_default.tolist()) == sorted(r_classical.tolist()), 'default != CLASSICAL'
        cl_codes = set(int(x) for x in r_classical['i_asp'])
        assert cl_codes <= {0, 4, 7, 9, 13}, f'CLASSICAL leaked non-classical: {cl_codes - {0,4,7,9,13}}'
        if len(r_classical):
            assert int(r_classical['i_asp'].max()) <= 13, 'i_asp out of canonical range'
        print('OK', len(r_default), len(r_classical), len(r_extended))
        "

    Behavior smoke (find_aspects_between_dates):
        python -c "
        from ketu.aspects import find_aspects_between_dates, CLASSICAL, EXTENDED
        from ketu.calculations import utc_to_julian
        from datetime import datetime, timezone, timedelta
        jd0 = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
        jd1 = utc_to_julian(datetime(2025, 1, 8, tzinfo=timezone.utc))
        # Default = CLASSICAL: should NOT contain Quintile/Quincunx etc.
        r_def = find_aspects_between_dates(jd0, jd1, body1=0, body2=1)
        r_cls = find_aspects_between_dates(jd0, jd1, body1=0, body2=1, aspects=CLASSICAL)
        r_ext = find_aspects_between_dates(jd0, jd1, body1=0, body2=1, aspects=EXTENDED)
        cl_names = {row[3] for row in r_cls}
        assert cl_names <= {'Conjunction','Sextile','Square','Trine','Opposition'}, cl_names
        # default == classical
        assert r_def == r_cls, 'find_aspects_between_dates default != CLASSICAL'
        print('OK', len(r_def), len(r_cls), len(r_ext))
        "

    Negative grep (after Step 2):
        grep -n '\baspects\[' ketu/aspects/calculator.py
    Should return ZERO matches.

    Positive grep (after Step 7):
        grep -n 'enumerate(selected_indices)' ketu/aspects/calculator.py
    Should return at least two matches (the two refactored hot loops).

    Negative invariant grep (Warning 6 enforcement — windows.py is OUT OF SCOPE for this plan):
        git diff -U0 ketu/aspects/windows.py | grep -E "^\+.*def find_aspect_window"
    Should return EMPTY (single-aspect API not modified). Note: 09-04a does NOT touch windows.py at all (windows.py is not in this plan's `files_modified`); this grep verifies the boundary is respected.

    Test suite: `pytest tests/test_aspects_vectorization.py tests/test_ketu.py tests/test_refactored.py tests/test_coverage_improvements.py tests/test_regression/test_bug_02_aspects.py -x -v` — passes (with documented `aspects=EXTENDED` retrofits where needed).

    Mypy: `mypy --strict ketu/aspects/calculator.py` — passes.
  </verify>
  <done>
    Four calculator functions accept `aspects=` parameter (calculate_aspects, _vectorized, _batch, find_aspects_between_dates); two hot loops are refactored to `enumerate(selected_indices)` emitting canonical `int(i_asp)`; resolver called once per API call (not per date); module-level `aspects` import renamed to `_CORE_ASPECTS` and zero `\baspects\[` references remain in calculator.py; behavior smoke tests pass; mypy strict passes; existing test suite passes (with documented `aspects=EXTENDED` retrofits where required); LRU-cache audit recorded in SUMMARY.
  </done>
</task>

</tasks>

<verification>
- `grep -n '\baspects\[' ketu/aspects/calculator.py` returns ZERO matches (every reference uses `_CORE_ASPECTS`).
- `grep -n 'enumerate(selected_indices)' ketu/aspects/calculator.py` returns ≥2 matches (the two refactored hot loops).
- All four batch/multi-aspect calculator APIs accept `aspects=` keyword: `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`.
- `calculate_aspects(jd)` with no kwargs returns the same result as `calculate_aspects(jd, aspects=CLASSICAL)`.
- `result['i_asp']` values for `aspects=CLASSICAL` are all in `{0, 4, 7, 9, 13}` — never renumbered to `0..4`.
- `find_aspects_between_dates(jd0, jd1, ..., aspects=CLASSICAL)` returns rows whose aspect_name is only in `{Conjunction, Sextile, Square, Trine, Opposition}`.
- Negative invariant: `git diff -U0 ketu/aspects/windows.py | grep -E "^\+.*def find_aspect_window"` is empty (windows.py untouched here; that file's modification belongs to Plan 09-04b).
- LRU-cache audit recorded in SUMMARY: every `@lru_cache`/`@functools.lru_cache` site in `ketu/aspects/*.py` and `ketu/calculations.py` confirmed safe (return value does NOT depend on aspect-set filtering) OR flagged for future fix.
- `mypy --strict ketu/aspects/calculator.py` passes.
- `interrogate ketu/aspects/calculator.py -f 95` passes (numpydoc on updated signatures).
- `files_modified` lists ONLY `ketu/aspects/calculator.py` — no leak into windows/timelines/transits.
</verification>

<success_criteria>
- ASP-03 satisfied (calculator subset): three batch APIs (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`) plus `find_aspects_between_dates` accept `aspects=` parameter.
- ASP-04 satisfied (calculator subset): `aspects=None` default resolves to CLASSICAL — observable: `calculate_aspects(jd)` returns no row with `i_asp` outside `{0, 4, 7, 9, 13}`, AND `find_aspects_between_dates(...)` returns no row whose name is outside the 5-major set.
- ASP-05 satisfied (calculator subset): `resolve_aspect_set` called ONCE at API entry per call (verified by grep — exactly one call site per public function, NOT inside per-date or per-pair loops).
- ASP-07 calculator-side coverage: every calculator.py public multi-aspect API accepts `aspects=`. The remaining ASP-07 surface (windows/timelines/transits) is covered by Plan 09-04b.
- Kala contract preserved: emitted `i_asp` is canonical 0-13 index, NOT filtered subset position. Verified by smoke test asserting `i_asp.max() <= 13` and presence of canonical indices in CLASSICAL output where geometry permits.
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-04a-SUMMARY.md` documenting:
- Each of the four modified functions: before/after signature, hot-loop refactor diff summary
- Module-level rename: `aspects` → `_CORE_ASPECTS` confirmed via grep (zero remaining `\baspects\[`)
- find_aspects_between_dates filtering: `list(aspects["angle"])` → `list(selected_angles)` confirmed
- Pre-execution discovery output verbatim (Task 1's six greps)
- Test-file retrofit list: file:line, before/after call, reason — for every test that needed `aspects=EXTENDED` to preserve v1.0 expectation
- LRU-cache audit table: every `@lru_cache` / `@functools.lru_cache` site in `ketu/aspects/*.py` and `ketu/calculations.py` with safe / requires-key-update verdict
- Smoke test transcript: `calculate_aspects(jd)` count vs `calculate_aspects(jd, aspects=EXTENDED)` count for a fixed test date; `find_aspects_between_dates` default vs EXTENDED row count
</output>
