---
phase: 09-configurable-aspects
plan: 04
type: execute
wave: 2
depends_on:
  - "09-02"
files_modified:
  - ketu/aspects/calculator.py
  - ketu/aspects/windows.py
  - ketu/aspects/timelines.py
  - ketu/aspects/transits.py
autonomous: true
plan_id: "09-04"
requirements:
  - ASP-03
  - ASP-04
  - ASP-05

must_haves:
  truths:
    - "calculate_aspects(jd, aspects=None) returns 5-aspect output (CLASSICAL by default)"
    - "calculate_aspects(jd, aspects=EXTENDED) returns 14-aspect output (legacy v1.0 behavior)"
    - "calculate_aspects_vectorized and calculate_aspects_batch accept aspects= and behave identically to calculate_aspects on default semantics"
    - "Hot loops at calculator.py:143 and :239 emit canonical i_asp (0-13 index into core.aspects), NOT k (filtered subset position) — Kala positional contract preserved"
    - "Resolver runs ONCE at API entry per call — never inside per-pair or per-date loops"
    - "find_aspects_timeline (windows.py), generate_aspect_timeline (timelines.py), find_transits_to_position and compare_dates_transits (transits.py) all default to CLASSICAL preset (replacing the four hardcoded literal lists)"
    - "find_aspect_window (single-aspect API) is NOT modified — it takes a single aspect, not a set"
  artifacts:
    - path: "ketu/aspects/calculator.py"
      provides: "calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch with aspects= parameter"
      contains: "resolve_aspect_set"
    - path: "ketu/aspects/windows.py"
      provides: "find_aspects_timeline default migrated from hardcoded list to CLASSICAL preset"
      contains: "CLASSICAL"
    - path: "ketu/aspects/timelines.py"
      provides: "generate_aspect_timeline default migrated from hardcoded list to CLASSICAL preset"
      contains: "CLASSICAL"
    - path: "ketu/aspects/transits.py"
      provides: "find_transits_to_position and compare_dates_transits defaults migrated to CLASSICAL preset"
      contains: "CLASSICAL"
  key_links:
    - from: "ketu/aspects/calculator.py"
      to: "ketu/aspects/presets.py"
      via: "resolve_aspect_set called once at top of each public function"
      pattern: "from ketu\\.aspects\\.presets import resolve_aspect_set"
    - from: "ketu/aspects/calculator.py hot loop (was line 143)"
      to: "selected_indices array"
      via: "enumerate(selected_indices) emits canonical i_asp 0-13"
      pattern: "enumerate\\(selected_indices\\)"
    - from: "ketu/aspects/windows.py default block (was lines 431-437)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded ['Conjunction', ...] list"
      pattern: "from ketu\\.aspects\\.presets import|aspects_list = \\[\"Conjunction\""
    - from: "ketu/aspects/timelines.py default block (was line 398)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded list"
      pattern: "from ketu\\.aspects\\.presets import"
    - from: "ketu/aspects/transits.py default blocks (was lines 304, 521)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded list (BOTH sites)"
      pattern: "from ketu\\.aspects\\.presets import"
---

<objective>
Thread the `aspects=` parameter through the three calculator APIs (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`) and migrate the four hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` default lists to the `CLASSICAL` preset. This is the biggest plan in Phase 9; every other plan is foundation for this or verification of this.

Purpose: ASP-03 (parameter on three batch APIs), ASP-04 (default = CLASSICAL — no kwargs returns 5 majors), ASP-05 (resolver once at entry, no filter inside hot loops). Bundling all four sites into one plan ensures atomic landing — partial migration would leave half the package on hardcoded lists and half on presets.

Output:
- `ketu/aspects/calculator.py` — three functions get `aspects=None` parameter; hot loops at the (current) lines 143 and 239 are refactored to iterate `selected_indices` while emitting canonical `i_asp`.
- `ketu/aspects/windows.py` — `find_aspects_timeline` default migrated.
- `ketu/aspects/timelines.py` — `generate_aspect_timeline` default migrated.
- `ketu/aspects/transits.py` — `find_transits_to_position` AND `compare_dates_transits` defaults migrated (two sites in this file).
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

# Files being modified
@ketu/aspects/calculator.py
@ketu/aspects/windows.py
@ketu/aspects/timelines.py
@ketu/aspects/transits.py

# The presets module being consumed (created in Plan 09-02)
@ketu/aspects/presets.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Refactor calculator.py — thread aspects= through three batch APIs and rewrite hot loops</name>
  <files>ketu/aspects/calculator.py</files>
  <action>
    This is the highest-stakes file in the phase. Refactor THREE public functions while preserving the canonical `i_asp` semantic (Kala contract).

    **Add at the top of the file (after existing imports):**

        from ketu.aspects.presets import resolve_aspect_set, AspectSetSpec

    **Function 1 — calculate_aspects (currently starts at line 73):**

    Update signature to:
        def calculate_aspects(
            jdate: float,
            l_bodies=bodies,
            aspects: AspectSetSpec = None,
        ) -> np.ndarray:

    NOTE: the existing parameter `l_bodies` and the new parameter `aspects` collide naming-wise with the imported `aspects` constant from `ketu.core` (line 14: `from ketu.core import bodies, aspects`). Strategy: rename the module-level import to a private alias to avoid confusion:

        # CHANGE line 14 from:
        #   from ketu.core import bodies, aspects
        # to:
        from ketu.core import bodies, aspects as _CORE_ASPECTS

    Then update ALL existing references to the module-level `aspects` constant inside this file (currently used at lines 40, 64, 143, 147, 239, 240) to reference `_CORE_ASPECTS` instead. Verify with grep before save: `grep -n "aspects\\[" ketu/aspects/calculator.py` — every match must reference either `_CORE_ASPECTS["..."]` or a local filtered copy, NOT a parameter named `aspects`.

    Now in `calculate_aspects` body (the SCALAR per-pair function — NOT vectorized — currently around lines 73-127), update the `for i_asp, aspect in enumerate(aspects["angle"])` loop (currently line 64 — actually this is inside `get_aspect`, NOT `calculate_aspects`; verify by reading the file before editing). Apply the SAME pattern as Function 2 below.

    Re-read the file CAREFULLY to identify which functions actually contain hot loops over aspects:
      - `get_aspect` (line 44-70) — has loop `for i_asp, aspect in enumerate(aspects["angle"])` at line 64. This is a low-level per-pair scan; ASP-03 does NOT mention adding `aspects=` to `get_aspect`. Leave `get_aspect` UNCHANGED — it remains keyed on the full 14 aspects (it only ever returns the FIRST match anyway). This is consistent with the research recommendation (lines 514-516: only multi-aspect APIs get `aspects=`).
      - `calculate_aspects` (line 73 onward, scalar-vectorized hybrid) — verify whether this function has the hot loop at line 143 or whether that's `calculate_aspects_vectorized`.
      - `calculate_aspects_vectorized` — has hot loop currently at line 143 per research.
      - `calculate_aspects_batch` — has hot loop currently at line 239 per research.
      - `find_aspect_timing` (line 268) — single-aspect timing search, do NOT add `aspects=` (out of scope per research).
      - `find_aspects_between_dates` — verify whether this is multi-aspect; if so, add `aspects=` parameter following the same pattern.

    **Function 2 — calculate_aspects_vectorized (hot loop at current line 143):**

    Update signature:
        def calculate_aspects_vectorized(
            jdate: float,
            l_bodies=bodies,
            aspects: AspectSetSpec = None,
        ) -> np.ndarray:

    At the very top of the body (above the existing `i_indices, j_indices = ...` setup):

        mask = resolve_aspect_set(aspects)              # length-14 bool, ONCE per call
        selected_indices = np.where(mask)[0]            # canonical 0-13 indices, dtype intp
        selected_angles = _CORE_ASPECTS["angle"][mask]  # filtered, parallel to selected_indices
        selected_coefs = _CORE_ASPECTS["coef"][mask]

    Replace the existing hot loop:
        # OLD (line 143):
        for i_asp, aspect_angle in enumerate(aspects["angle"]):
            ...
            aspect_coef = aspects["coef"][i_asp]

    With:
        # NEW:
        for k, i_asp in enumerate(selected_indices):
            aspect_angle = float(selected_angles[k])
            aspect_coef = float(selected_coefs[k])
            ...

    CRITICAL — Kala contract preservation: the `results.append((..., i_asp, ...))` line MUST emit `int(i_asp)` (the canonical index from `selected_indices[k]`), NOT `k` (the position within the filtered subset). Per research Pitfall 1: "Renumbering `i_asp` to be 0..N-1 within the selected set... breaks Kala's positional lookup."

    The `if i_asp == 0:  # Conjunction` branch is correct as-is — `i_asp == 0` still means "Conjunction" in canonical indexing. After the refactor, it still works because Conjunction is in CLASSICAL (index 0 → True in mask → first iteration emits i_asp=0).

    **Function 3 — calculate_aspects_batch (hot loop at current line 239):**

    Update signature:
        def calculate_aspects_batch(
            jdates: np.ndarray,
            l_bodies=bodies,
            aspects: AspectSetSpec = None,
        ) -> List[np.ndarray]:

    PERFORMANCE-CRITICAL: resolver MUST be called ABOVE the per-date loop (currently `for date_idx in range(n_dates):` at line 234), NOT inside it. Per research Anti-Pattern: "Putting the resolver call in the per-date loop... It's already efficient because the per-aspect-type loop is INSIDE the per-date loop — but the resolver itself must execute once per API call (above the date loop), not per date."

    Sequence:
        # 1. Above any loop:
        mask = resolve_aspect_set(aspects)
        selected_indices = np.where(mask)[0]
        selected_angles = _CORE_ASPECTS["angle"][mask]
        selected_coefs = _CORE_ASPECTS["coef"][mask]

        # 2. Existing date loop unchanged at top:
        for date_idx in range(n_dates):
            ...
            # 3. Inner aspect loop refactored same as Function 2:
            for k, i_asp in enumerate(selected_indices):
                aspect_angle = float(selected_angles[k])
                aspect_coef = float(selected_coefs[k])
                ...
                date_results.append((body1_ids[idx], body2_ids[idx], int(i_asp), orb_values[i]))

    **Function 4 — calculate_aspects (the original wrapper):**

    If `calculate_aspects` is implemented as a thin wrapper over `calculate_aspects_vectorized`, add `aspects: AspectSetSpec = None` to its signature and pass it through. If it has its own hot loop, refactor identically to Function 2. (Verify by reading the file first.)

    **Function 5 — find_aspects_between_dates:**

    Locate this function in calculator.py. If its signature/body iterates aspects similarly, apply the same pattern. If it delegates entirely to one of the above, just thread `aspects=` through.

    **Numpydoc updates:**

    For each modified signature, update the docstring's Parameters section with:

        aspects : AspectSetSpec, default None
            Aspect set to compute. None resolves to CLASSICAL (5 majors:
            Conjunction, Sextile, Square, Trine, Opposition). Accepts a preset
            name ("classical", "traditional", "extended"), a list of aspect
            names or indices, or a length-14 boolean mask. The result's
            ``i_asp`` field is always a canonical 0-13 index into
            ``ketu.core.aspects``, regardless of the selected subset.

    Add a docstring note documenting the canonical i_asp invariant explicitly:

        Notes
        -----
        The ``i_asp`` field in the returned structured array is the canonical
        index into ``ketu.core.aspects`` (0-13), not a position within the
        selected subset. Downstream consumers (e.g. Kala) rely on this
        positional contract.

    **Mypy strict:**
    - `AspectSetSpec` is the type alias from presets module.
    - The `mask`, `selected_indices`, `selected_angles`, `selected_coefs` locals are `np.ndarray`. If mypy needs help, annotate explicitly.

    **Anti-patterns to NOT introduce (from research):**
    - Do NOT filter inside the per-pair loop (`if i_asp in selected_indices: ...`) — pre-filter ONCE.
    - Do NOT mutate `_CORE_ASPECTS` (no `_CORE_ASPECTS = _CORE_ASPECTS[mask]`).
    - Do NOT renumber emitted i_asp.
    - Do NOT use `aspects=CLASSICAL` as the default in the function signature — use `aspects=None` (mutable-default trap protection per research Pitfall 5).
  </action>
  <verify>
    Run smoke import: `python -c "from ketu.aspects import calculate_aspects, calculate_aspects_vectorized, calculate_aspects_batch, CLASSICAL, EXTENDED"` — succeeds.

    Run behavior smoke:
        python -c "
        from ketu.aspects import calculate_aspects, EXTENDED, CLASSICAL
        from ketu.calculations import utc_to_julian
        from datetime import datetime, timezone
        jd = utc_to_julian(datetime(2025, 1, 1, tzinfo=timezone.utc))
        r_default = calculate_aspects(jd)
        r_classical = calculate_aspects(jd, aspects=CLASSICAL)
        r_extended = calculate_aspects(jd, aspects=EXTENDED)
        # Default == CLASSICAL
        assert sorted(r_default.tolist()) == sorted(r_classical.tolist()), 'default != CLASSICAL'
        # CLASSICAL ⊆ EXTENDED (every classical-only result is also in extended)
        # NOTE: EXTENDED returns the FIRST aspect-match per pair (matched_pairs set),
        # so it can have FEWER rows than CLASSICAL when a closer harmonic eclipses
        # a major aspect. The correct invariant is: every i_asp in r_classical is
        # in {0,4,7,9,13}, and r_extended may include i_asp values outside that set.
        cl_codes = set(int(x) for x in r_classical['i_asp'])
        ext_codes = set(int(x) for x in r_extended['i_asp'])
        assert cl_codes <= {0, 4, 7, 9, 13}, f'CLASSICAL leaked non-classical: {cl_codes - {0,4,7,9,13}}'
        # Canonical i_asp preserved in classical: max possible is 13 (Opposition)
        if len(r_classical):
            assert int(r_classical['i_asp'].max()) <= 13, 'i_asp out of canonical range'
        print('OK', len(r_default), len(r_classical), len(r_extended))
        "

    Run existing test suite: `pytest tests/test_aspects_vectorization.py tests/test_ketu.py -x -v` — should pass (the existing tests likely call `calculate_aspects(jd)` without kwargs; with the default flip, results may differ. SOME EXISTING TESTS MAY FAIL if they hardcoded EXTENDED-era expectations).

    For ANY test that fails due to default flip, the fix is to update the test call to `calculate_aspects(jd, aspects=EXTENDED)` (preserving v1.0 expectation) — DO NOT loosen the assertion. Document each such update in the SUMMARY.

    `mypy --strict ketu/aspects/calculator.py` — passes.
  </verify>
  <done>
    Three calculator functions accept `aspects=` parameter; hot loops at lines (formerly) 143 and 239 are refactored to `enumerate(selected_indices)` emitting canonical `i_asp`; resolver called once per API call (not per date); module-level `aspects` import renamed to `_CORE_ASPECTS` to avoid name collision; behavior smoke test passes; no test regressions OR all regressions are documented as default-flip artifacts (with `aspects=EXTENDED` retrofit applied to preserve v1.0 expectations).
  </done>
</task>

<task type="auto">
  <name>Task 2: Migrate four hardcoded-list default sites to CLASSICAL preset</name>
  <files>ketu/aspects/windows.py
ketu/aspects/timelines.py
ketu/aspects/transits.py</files>
  <action>
    Replace the four `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` literal default lists with imports from `ketu.aspects.presets`. The four sites (verified by grep):

    1. `ketu/aspects/windows.py:431-437` — inside `find_aspects_timeline` function default block.
    2. `ketu/aspects/timelines.py:398-399` — inside `generate_aspect_timeline` function default block.
    3. `ketu/aspects/transits.py:304-305` — inside `find_transits_to_position` function default block.
    4. `ketu/aspects/transits.py:521-522` — inside `compare_dates_transits` function default block.

    **Strategy decision (key):** these functions take `aspects_list` (a list of NAMES like `["Conjunction", ...]`), not a boolean mask. They iterate aspect names downstream and pass them to single-aspect APIs (e.g. `find_aspect_window(aspect="Conjunction")`). They DO NOT use the calculator hot-loop mask path.

    Two acceptable migration approaches:

    **Approach A (minimal, preferred):** keep `aspects_list` as a list-of-names parameter, but derive the default from CLASSICAL via a small helper. Cleaner default; no API surface change.

        # At top of file:
        from ketu.aspects.presets import CLASSICAL
        from ketu.core import aspects as _CORE_ASPECTS

        # Inside each function (replacing the hardcoded list):
        if aspects_list is None:
            aspects_list = [
                _CORE_ASPECTS["name"][i].decode()
                for i in np.where(CLASSICAL)[0]
            ]

    OR even simpler if the order is well-known and deterministic:

        # At top of file (defined ONCE per module to avoid re-computing):
        from ketu.aspects.presets import CLASSICAL
        from ketu.core import aspects as _CORE_ASPECTS_DATA
        _CLASSICAL_NAMES = tuple(_CORE_ASPECTS_DATA["name"][i].decode() for i in np.where(CLASSICAL)[0])

        # Inside each function:
        if aspects_list is None:
            aspects_list = list(_CLASSICAL_NAMES)  # `list()` to give caller a fresh mutable list

    Approach A is preferred because:
      - Backward-compatible: `aspects_list` parameter name and shape (list of strings) unchanged.
      - Single source of truth: when CLASSICAL changes, the four call sites pick up the change automatically.
      - No circular-import risk (presets imports from ketu.core; this file imports from ketu.aspects.presets and ketu.core — same DAG).

    **Approach B (more invasive, NOT recommended for this plan):** widen `aspects_list` parameter to accept `AspectSetSpec` and call `resolve_aspect_set` internally. This would require changing the per-aspect downstream loop to convert mask back to names, doubling the work. SKIP this approach — keep the surface minimal in v1.1.

    **Apply Approach A to all four sites:**

    For each of the four function bodies, replace:
        if aspects_list is None:
            aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

    With:
        if aspects_list is None:
            aspects_list = list(_CLASSICAL_NAMES)

    And add at the top of each of the three files (windows.py, timelines.py, transits.py — note transits.py has 2 sites but only needs ONE import block at the top):

        # Default aspect set sourced from presets module (Phase 9, ASP-04).
        # Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"] lists.
        from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
        from ketu.core import aspects as _CORE_ASPECTS_DATA
        import numpy as np  # if not already imported
        _CLASSICAL_NAMES = tuple(
            _CORE_ASPECTS_DATA["name"][i].decode()
            for i in np.where(_CLASSICAL_MASK)[0]
        )

    NOTE: `numpy` is already imported in all three files (verify with `grep -n "^import numpy" ketu/aspects/{windows,timelines,transits}.py`); the `import numpy as np` line above is just a safety reminder — do not duplicate.

    NOTE on `windows.py:430` — the comment says "Default to all major aspects". Update to "Default to CLASSICAL preset (5 majors) per Phase 9 ASP-04". Same edit for `timelines.py:397` ("Default aspects: BIG_FIVE" → "Default aspects: CLASSICAL preset (Phase 9)") and the two transits.py sites.

    **Anti-patterns to avoid:**
    - Do NOT add `aspects: AspectSetSpec` to these four functions' signatures in this plan. (That would be a parameter SHAPE change beyond ASP-03's scope.)
    - Do NOT delete the hardcoded list inline and replace with `CLASSICAL` mask directly — the downstream code expects a `list[str]` of names, not a bool mask.
    - Do NOT touch `lunar_calendar.py:16 BIG_FIVE` (out of scope per research — coverage-omitted module).
    - Do NOT touch `find_aspect_window` (single-aspect API, out of scope per research line 514).
  </action>
  <verify>
    Grep audit:
      grep -n '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' ketu/aspects/*.py
    Should return ZERO matches in `windows.py`, `timelines.py`, `transits.py`. Matches in test files or `lunar_calendar.py` are fine.

    Grep audit (positive):
      grep -n '_CLASSICAL_NAMES\|CLASSICAL' ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
    Should show the new import block + usages in all three files.

    Smoke test:
        python -c "
        from ketu.aspects import find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits
        from datetime import datetime, timezone
        # Just confirm imports work and functions are callable with no aspects_list
        # (we don't run them — they hit the actual ephemeris which is slow)
        import inspect
        for fn in (find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits):
            sig = inspect.signature(fn)
            assert 'aspects_list' in sig.parameters, f'{fn.__name__} missing aspects_list'
            assert sig.parameters['aspects_list'].default is None, f'{fn.__name__} default is not None'
        print('OK')
        "

    `pytest tests/test_aspect_timelines.py tests/test_aspect_windows.py tests/test_transits.py -x` — passes (or any failures are documented as default-flip artifacts and patched per the windows/timelines/transits-specific test invocations to pin EXTENDED behavior where prior tests assumed it).

    `mypy --strict ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py` — passes.
  </verify>
  <done>
    All four hardcoded-list sites migrated to derive from CLASSICAL preset; grep confirms zero remaining `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` literal lists in `ketu/aspects/{windows,timelines,transits}.py`; functions still callable with default `aspects_list=None`; existing tests pass (or default-flip regressions are documented + retrofitted with explicit `aspects_list=` arguments).
  </done>
</task>

</tasks>

<verification>
- `grep -rn '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' ketu/aspects/` returns ZERO matches (`lunar_calendar.py` and test files are out of scope).
- All three batch calculator APIs (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`) accept `aspects=` keyword.
- `calculate_aspects(jd)` with no kwargs returns same result as `calculate_aspects(jd, aspects=CLASSICAL)`.
- `result['i_asp']` values for `aspects=CLASSICAL` are all in `{0, 4, 7, 9, 13}` — never renumbered to `0..4`.
- `mypy --strict ketu/aspects/calculator.py ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py` passes.
- `pytest tests/ -x` passes. Default-flip regressions in existing tests are documented in SUMMARY.md, with each fix being either (a) explicit `aspects=EXTENDED` to pin v1.0 expectation, or (b) updating the count assertion to match CLASSICAL output. NO assertion is loosened to `>= 0` or similar.
- `interrogate ketu/aspects/calculator.py -f 95` passes (numpydoc on updated signatures).
</verification>

<success_criteria>
- ASP-03 satisfied: three batch APIs (`calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`) accept `aspects=` parameter.
- ASP-04 satisfied: `aspects=None` default resolves to CLASSICAL — observable: `calculate_aspects(jd)` returns no row with `i_asp` outside `{0, 4, 7, 9, 13}`.
- ASP-05 satisfied: `resolve_aspect_set` called ONCE at API entry per call (verified by grep — exactly one call site per public function, NOT inside per-date or per-pair loops).
- Kala contract preserved: emitted `i_asp` is canonical 0-13 index, NOT filtered subset position. Verified by smoke test asserting `i_asp.max() <= 13` and presence of `i_asp == 13` (Opposition) in CLASSICAL output where geometry permits.
- Four hardcoded-list sites migrated to CLASSICAL-derived names; single source of truth established.
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-04-SUMMARY.md` documenting:
- Each of the three calculator functions: before/after signature, hot-loop refactor diff summary
- The four hardcoded-list migration sites with file:line references (before line numbers as per research, after line numbers as per current file post-edit)
- List of any existing test that needed `aspects=EXTENDED` retrofit to preserve v1.0 behavior expectations (with file:line and reason)
- Confirmation that `_CORE_ASPECTS` is the new name of the imported `aspects` constant inside `calculator.py` (avoids parameter-shadowing)
- Smoke test transcript: `calculate_aspects(jd)` count vs `calculate_aspects(jd, aspects=EXTENDED)` count for a fixed test date
</output>
