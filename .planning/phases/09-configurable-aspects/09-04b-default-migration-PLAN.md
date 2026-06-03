---
phase: 09-configurable-aspects
plan: 04b
type: execute
wave: 2
depends_on:
  - "09-02"
files_modified:
  - ketu/aspects/windows.py
  - ketu/aspects/timelines.py
  - ketu/aspects/transits.py
autonomous: true
plan_id: "09-04b"
requirements:
  - ASP-04
  - ASP-07

must_haves:
  truths:
    - "find_aspects_timeline (windows.py) default-aspect list is sourced from CLASSICAL preset, not a hardcoded literal"
    - "generate_aspect_timeline (timelines.py) default-aspect list is sourced from CLASSICAL preset, not a hardcoded literal"
    - "find_transits_to_position (transits.py) default-aspect list is sourced from CLASSICAL preset, not a hardcoded literal"
    - "compare_dates_transits (transits.py) default-aspect list is sourced from CLASSICAL preset, not a hardcoded literal"
    - "Single source of truth: when CLASSICAL changes, all four call sites pick up the change automatically (verified by import provenance)"
    - "find_aspect_window (single-aspect API) is NOT modified — locked decision; verified by negative-grep guard"
    - "lunar_calendar.BIG_FIVE is NOT modified — out of scope per locked decision"
  artifacts:
    - path: "ketu/aspects/windows.py"
      provides: "find_aspects_timeline default migrated from hardcoded list to CLASSICAL preset"
      contains: "_CLASSICAL_NAMES"
    - path: "ketu/aspects/timelines.py"
      provides: "generate_aspect_timeline default migrated from hardcoded list to CLASSICAL preset"
      contains: "_CLASSICAL_NAMES"
    - path: "ketu/aspects/transits.py"
      provides: "find_transits_to_position and compare_dates_transits defaults migrated to CLASSICAL preset"
      contains: "_CLASSICAL_NAMES"
  key_links:
    - from: "ketu/aspects/windows.py default block (was lines 431-437)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded ['Conjunction', ...] list"
      pattern: "from ketu\\.aspects\\.presets import CLASSICAL"
    - from: "ketu/aspects/timelines.py default block (was line 398)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded list"
      pattern: "from ketu\\.aspects\\.presets import CLASSICAL"
    - from: "ketu/aspects/transits.py default blocks (was lines 304, 521)"
      to: "ketu/aspects/presets.CLASSICAL"
      via: "default replaced from hardcoded list (BOTH sites)"
      pattern: "from ketu\\.aspects\\.presets import CLASSICAL"
---

<objective>
Migrate the four hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` default lists in `windows.py`, `timelines.py`, and `transits.py` (two sites) to derive from the `CLASSICAL` preset. Single source of truth — when CLASSICAL changes, all four call sites pick up the change automatically.

Purpose: ASP-04 (default = CLASSICAL across the entire `ketu/aspects/` surface), ASP-07 (windows/timelines/transits side coverage of "all public aspect APIs default to CLASSICAL"). This plan complements Plan 09-04a (calculator.py-only refactor) — both are Wave 2, both depend only on 09-02 (presets module), and they touch DISJOINT files so they can run in parallel.

Scope boundary: this plan does NOT add `aspects: AspectSetSpec` to these four function signatures (their `aspects_list: list[str]` parameter shape is preserved per Approach A — the cleaner v1.1 surface). It also does NOT modify `find_aspect_window` (single-aspect API, locked OUT OF SCOPE) or `lunar_calendar.BIG_FIVE` (locked OUT OF SCOPE).

Output:
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
@ketu/aspects/windows.py
@ketu/aspects/timelines.py
@ketu/aspects/transits.py

# The presets module being consumed (created in Plan 09-02)
@ketu/aspects/presets.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Migrate four hardcoded-list default sites to derive from CLASSICAL preset</name>
  <files>ketu/aspects/windows.py
ketu/aspects/timelines.py
ketu/aspects/transits.py</files>
  <action>
    Replace the four `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` literal default lists with a CLASSICAL-derived names tuple. Locate the actual sites by pattern (line numbers may have drifted since the research pass — orientation only):

        grep -n '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' ketu/aspects/{windows,timelines,transits}.py

    Expected matches (per research): windows.py:431-437, timelines.py:398-399, transits.py:304-305 and transits.py:521-522. Confirm the actual current lines and record them in SUMMARY.

    **Strategy decision (locked):** these functions take `aspects_list` (a list of NAMES like `["Conjunction", ...]`), not a boolean mask. They iterate aspect names downstream and pass them to single-aspect APIs (e.g. `find_aspect_window(aspect="Conjunction")`). They DO NOT use the calculator hot-loop mask path. Approach A (preserve `aspects_list: list[str]` shape, derive default from CLASSICAL) is the v1.1 surface. Do NOT widen `aspects_list` to accept `AspectSetSpec` — that is a larger v1.2+ change.

    **Per-file edit pattern:**

    At the top of EACH of the three files (windows.py, timelines.py, transits.py), add ONE import block. Even though transits.py has 2 sites, only ONE import block at module level. Place near the existing `import numpy as np` line (verified present in all three via `grep -n "^import numpy" ketu/aspects/{windows,timelines,transits}.py`):

        # Default aspect set sourced from presets module (Phase 9, ASP-04).
        # Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
        # lists. Single source of truth: when CLASSICAL changes, all call sites in this
        # module pick up the change automatically.
        from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
        from ketu.core import aspects as _CORE_ASPECTS_DATA
        _CLASSICAL_NAMES = tuple(
            _CORE_ASPECTS_DATA["name"][i].decode()
            for i in np.where(_CLASSICAL_MASK)[0]
        )

    Note: `_CORE_ASPECTS_DATA["name"]` is `S16` bytes dtype (per `ketu/core.py:103`); `.decode()` is required to produce `str`. The `tuple()` wrapping is intentional — gives an immutable canonical reference; each call site does `list(_CLASSICAL_NAMES)` to hand the caller a fresh mutable list.

    Then in EACH of the four function bodies, replace:

        # OLD:
        if aspects_list is None:
            aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]

        # NEW:
        if aspects_list is None:
            aspects_list = list(_CLASSICAL_NAMES)

    Update the adjacent comment too:
    - `windows.py` near the default block: "# Default to all major aspects" → "# Default to CLASSICAL preset (5 majors) per Phase 9 ASP-04"
    - `timelines.py` near the default block: "# Default aspects: BIG_FIVE" → "# Default aspects: CLASSICAL preset (Phase 9 ASP-04)"
    - both `transits.py` sites: similar — replace any "BIG_FIVE" or "all major aspects" comment with "CLASSICAL preset (Phase 9 ASP-04)"

    **Anti-patterns to avoid:**
    - Do NOT add `aspects: AspectSetSpec` to these four functions' signatures in this plan. (That would be a parameter SHAPE change beyond ASP-04's scope.)
    - Do NOT delete the hardcoded list inline and replace with `CLASSICAL` mask directly — the downstream code expects a `list[str]` of names, not a bool mask.
    - Do NOT touch `lunar_calendar.py` `BIG_FIVE` (out of scope per locked decision — coverage-omitted module).
    - Do NOT touch `find_aspect_window` (single-aspect API, locked OUT OF SCOPE — verified by negative-grep guard in `<verify>`).
    - Do NOT add the `_CLASSICAL_NAMES` block more than once per file (transits.py has 2 sites but ONE import block at top).
  </action>
  <verify>
    Negative grep — hardcoded literals removed from the three target files:
        grep -n '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
    Should return ZERO matches. (Matches in test files or `lunar_calendar.py` are out of scope — that's expected.)

    Positive grep — CLASSICAL provenance present in all three files:
        grep -n '_CLASSICAL_NAMES\|from ketu.aspects.presets import CLASSICAL' ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
    Should show the new import block in EACH of the three files (one match per file for the import line, plus one or more `_CLASSICAL_NAMES` reference lines per call site — exactly 1 in windows.py, 1 in timelines.py, 2 in transits.py).

    Negative invariant grep (Warning 6 — find_aspect_window is NOT modified):
        git diff -U0 ketu/aspects/windows.py | grep -E "^\+.*def find_aspect_window"
    Should return EMPTY. The single-aspect API signature is locked unchanged.

    Smoke test — functions still callable with default aspects_list=None:
        python -c "
        import inspect
        from ketu.aspects import find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits
        for fn in (find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits):
            sig = inspect.signature(fn)
            assert 'aspects_list' in sig.parameters, f'{fn.__name__} missing aspects_list'
            assert sig.parameters['aspects_list'].default is None, f'{fn.__name__} default is not None'
        print('OK')
        "

    Provenance smoke — verify _CLASSICAL_NAMES resolves correctly in all three files:
        python -c "
        from ketu.aspects.windows import _CLASSICAL_NAMES as W
        from ketu.aspects.timelines import _CLASSICAL_NAMES as T
        from ketu.aspects.transits import _CLASSICAL_NAMES as TR
        expected = ('Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition')
        assert W == T == TR == expected, (W, T, TR)
        print('OK', W)
        "

    Test suite: `pytest tests/test_aspect_timelines.py tests/test_aspect_windows.py tests/test_transits.py -x -v` — passes (or any failures are documented as default-flip artifacts; since the names list is unchanged in CONTENT, no test should break — this is purely an internal sourcing change).

    Mypy: `mypy --strict ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py` — passes.
  </verify>
  <done>
    All four hardcoded-list sites migrated to derive from CLASSICAL preset; grep confirms zero remaining `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` literal lists in `ketu/aspects/{windows,timelines,transits}.py`; provenance smoke test confirms `_CLASSICAL_NAMES` resolves to the canonical 5-major tuple in all three modules; functions still callable with default `aspects_list=None`; existing tests pass; find_aspect_window untouched (negative-grep guard satisfied).
  </done>
</task>

</tasks>

<verification>
- `grep -rn '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py` returns ZERO matches.
- All three files import `_CLASSICAL_MASK` (or equivalent) from `ketu.aspects.presets` and define `_CLASSICAL_NAMES` exactly once.
- `_CLASSICAL_NAMES` resolves identically in all three modules to `("Conjunction", "Sextile", "Square", "Trine", "Opposition")`.
- `git diff -U0 ketu/aspects/windows.py | grep -E "^\+.*def find_aspect_window"` returns empty (single-aspect API not modified).
- Public function signatures preserved: `find_aspects_timeline`, `generate_aspect_timeline`, `find_transits_to_position`, `compare_dates_transits` all still take `aspects_list: list[str] | None = None`.
- `mypy --strict ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py` passes.
- `pytest tests/test_aspect_timelines.py tests/test_aspect_windows.py tests/test_transits.py -x` passes.
- `interrogate ketu/aspects/{windows,timelines,transits}.py -f 90` passes (no docstring regressions).
</verification>

<success_criteria>
- ASP-04 satisfied (windows/timelines/transits subset): the four function defaults now derive from CLASSICAL — same content, but single-source-of-truth provenance.
- ASP-07 windows/timelines/transits-side coverage: all four publicly-exported aspect-set-aware multi-aspect functions in these three files have their default sourced from CLASSICAL preset.
- Locked decisions preserved: `find_aspect_window` untouched (single-aspect API), `lunar_calendar.BIG_FIVE` untouched (out of scope), `core.aspects` untouched.
- No public API surface change — `aspects_list: list[str]` shape preserved.
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-04b-SUMMARY.md` documenting:
- Per-file diff summary: file:line range, before/after of the import block, before/after of each default block (4 sites total)
- Provenance smoke transcript confirming `_CLASSICAL_NAMES` resolves identically in all three modules
- Confirmation that find_aspect_window signature is byte-identical to pre-plan state (`git diff` of the def line is empty)
- Confirmation that no test in `tests/test_aspect_timelines.py`, `tests/test_aspect_windows.py`, `tests/test_transits.py` needed any change (this migration preserves the names list content, so no test should break)
</output>
