---
phase: 09-configurable-aspects
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/aspects/presets.py
  - ketu/aspects/__init__.py
  - tests/test_aspect_presets.py
autonomous: true
plan_id: "09-02"
requirements:
  - ASP-02
  - ASP-04
  - ASP-05
  - ASP-06

must_haves:
  truths:
    - "from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED resolves to length-14 boolean masks summing to 5, 7, 14"
    - "from ketu.aspects import CLASSICAL, TRADITIONAL, EXTENDED works (re-exported from subpackage __init__)"
    - "resolve_aspect_set(None) returns CLASSICAL by default — observable behavior"
    - "resolve_aspect_set accepts: None, str preset name (case-insensitive), Sequence[str] aspect names, Sequence[int] indices, np.ndarray bool length-14, np.ndarray int indices"
    - "Preset masks are frozen (mask.flags.writeable == False) — accidental mutation raises ValueError"
    - "Resolver raises ValueError with informative message on: unknown preset name, unknown aspect name, out-of-range index, wrong-length boolean mask, invalid item type"
    - "Module docstring documents the LRU-cache rule for ASP-06 (forward-looking)"
  artifacts:
    - path: "ketu/aspects/presets.py"
      provides: "CLASSICAL, TRADITIONAL, EXTENDED constants + resolve_aspect_set + AspectSetSpec type alias"
      exports: ["CLASSICAL", "TRADITIONAL", "EXTENDED", "AspectSetSpec", "resolve_aspect_set"]
      contains: "def resolve_aspect_set"
      min_lines: 100
    - path: "ketu/aspects/__init__.py"
      provides: "Re-export of CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set at subpackage level"
      contains: "from ketu.aspects.presets import"
    - path: "tests/test_aspect_presets.py"
      provides: "Unit tests for resolver + preset constants (≥15 test functions covering all spec branches and error paths)"
      contains: "def test_resolve_none_returns_classical"
      min_lines: 100
  key_links:
    - from: "ketu/aspects/presets.py"
      to: "ketu.core.aspects"
      via: "import for length-14 sanity assert and name lookup"
      pattern: "from ketu\\.core import aspects"
    - from: "ketu/aspects/__init__.py"
      to: "ketu/aspects/presets.py"
      via: "re-export"
      pattern: "from ketu\\.aspects\\.presets import"
    - from: "tests/test_aspect_presets.py"
      to: "ketu/aspects/presets.py"
      via: "imports CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set"
      pattern: "from ketu\\.aspects\\.presets import"
---

<objective>
Create the `ketu/aspects/presets.py` module containing CLASSICAL/TRADITIONAL/EXTENDED preset masks and the `resolve_aspect_set` resolver. Re-export at the subpackage `__init__.py` level. Write comprehensive unit tests.

Purpose: ASP-02 (presets exposed), ASP-04 (default = CLASSICAL via resolver), ASP-05 foundation (single-call resolver returns mask, ready for hot-loop replacement in Wave 2), ASP-06 documented (forward-looking cache rule). This is the foundation Wave 2 builds upon — no other plan in Wave 1 touches this file.

Output:
- `ketu/aspects/presets.py` — preset constants + resolver
- `ketu/aspects/__init__.py` — updated to re-export presets API
- `tests/test_aspect_presets.py` — new test file (resolver + invariant unit tests; integration tests for `calculate_aspects` etc. live in Plan 09-05, not here)
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

# core.aspects definition (rows 0-13 are the canonical mapping)
@ketu/core.py

# Existing pattern: how other modules look up aspect names by str (use S16 / .encode())
@ketu/aspects/core.py

# Subpackage __init__ to extend
@ketu/aspects/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ketu/aspects/presets.py with constants and resolver</name>
  <files>ketu/aspects/presets.py</files>
  <action>
    Create the module exactly per the research recipe (`09-RESEARCH.md` Pattern 1, lines 70-198). Key requirements:

    1. Module docstring: numpydoc-style, explains the three presets and the row-order mapping (indices 0-13 with names) per research lines 94-97.
    2. `from __future__ import annotations` first.
    3. Imports: `from typing import Sequence, Union`, `import numpy as np`, `from ketu.core import aspects as _ASPECTS`.
    4. Defensive `assert len(_ASPECTS) == 14` at module load with a descriptive message.
    5. Three private numpy index arrays:
       - `_CLASSICAL_INDICES = np.array([0, 4, 7, 9, 13], dtype=np.intp)`
       - `_TRADITIONAL_INDICES = np.array([0, 1, 4, 7, 9, 11, 13], dtype=np.intp)`
       - `_EXTENDED_INDICES = np.arange(14, dtype=np.intp)`
    6. Helper `_indices_to_mask(indices: np.ndarray) -> np.ndarray` that creates a length-14 bool mask, sets the indices to True, and freezes via `mask.flags.writeable = False`.
    7. Module-level public constants `CLASSICAL`, `TRADITIONAL`, `EXTENDED` — frozen length-14 bool masks.
    8. `_PRESET_BY_NAME = {"classical": CLASSICAL, "traditional": TRADITIONAL, "extended": EXTENDED}`.
    9. Type alias `AspectSetSpec = Union[None, str, Sequence[Union[str, int]], np.ndarray]`.
    10. `def resolve_aspect_set(spec: AspectSetSpec, default: np.ndarray = CLASSICAL) -> np.ndarray:` — full numpydoc docstring with Parameters/Returns/Raises sections.

    Resolver dispatch logic (per research Pattern 1, lines 148-189):
       - `spec is None` → return `default` (which is CLASSICAL by signature default).
       - `isinstance(spec, str)` → lowercase, look up in `_PRESET_BY_NAME`, raise ValueError with valid options listed if not found.
       - `isinstance(spec, np.ndarray)`:
         * dtype `np.bool_`: assert shape `(14,)`, raise ValueError if not.
         * else: treat as int indices, convert via `_indices_to_mask(np.asarray(spec, dtype=np.intp))`.
       - Else: iterate Sequence elements:
         * str → `np.where(_ASPECTS["name"] == item.encode())[0]`. CRITICAL: `_ASPECTS["name"]` is `S16` bytes dtype (per `ketu/core.py:103`). MUST `.encode()` the user's str. If empty result, raise ValueError listing valid names (decoded).
         * int (or np.integer) → range-check 0-13.
         * Else → ValueError "invalid aspect spec item".
       - Return `_indices_to_mask(np.array(indices, dtype=np.intp))`.

    11. Add a module-level forward-looking note (in the docstring AND as a code comment near the resolver):

        """
        ASP-06 forward-looking rule
        ----------------------------
        No current LRU cache (`ketu.calculations:body_properties`,
        `ketu.aspects.core:_cached_planet_position_batch`) materializes filtered aspect
        output, so cache keys today do NOT need to include the aspect-set hash. If a
        future cache memoizes a function whose return value depends on `aspects=`,
        its key MUST include `mask.tobytes()` (or equivalent) to avoid stale results
        across different aspect sets. See Phase 9 RESEARCH.md, Pitfall 4.
        """

    12. `__all__ = ["CLASSICAL", "TRADITIONAL", "EXTENDED", "AspectSetSpec", "resolve_aspect_set"]`.

    Anti-patterns to avoid (per research):
    - Do NOT use `aspects=CLASSICAL` as a function default in the resolver SIGNATURE — `default=CLASSICAL` IS okay because it's a frozen array, but downstream public APIs (calculator/windows/timelines/transits) must use `aspects=None` and resolve internally (Plan 09-04). The resolver itself is fine to default to CLASSICAL.
    - Do NOT mutate `_ASPECTS` at module load (read-only).
    - Do NOT add a class — flat module-level functions/constants only.

    Mypy strict requirements:
    - Type-annotate every function parameter and return.
    - `np.ndarray` is acceptable; if mypy complains, use `npt.NDArray[np.bool_]` from `numpy.typing` (already used elsewhere in this codebase — check `ketu/aspects/core.py` for prior art).

    Numpydoc + interrogate ≥95%:
    - Module docstring (top of file).
    - Resolver docstring with Parameters, Returns, Raises, Examples.
    - Constants commented (CLASSICAL = "5 majors: 0°, 60°, 90°, 120°, 180°" etc.).

    Reference research file at `.planning/phases/09-configurable-aspects/09-RESEARCH.md` lines 70-198 for the verified verbatim implementation pattern.
  </action>
  <verify>
    Run:
      python -c "from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set; import numpy as np; assert CLASSICAL.sum()==5 and TRADITIONAL.sum()==7 and EXTENDED.sum()==14; assert CLASSICAL.shape==(14,); assert np.array_equal(resolve_aspect_set(None), CLASSICAL); assert not CLASSICAL.flags.writeable; print('OK')"

    Run mypy: `mypy --strict ketu/aspects/presets.py`.
    Run interrogate: `interrogate ketu/aspects/presets.py -f 95` should pass.
  </verify>
  <done>
    File `ketu/aspects/presets.py` exists; module imports cleanly; CLASSICAL/TRADITIONAL/EXTENDED are length-14 frozen bool masks summing to 5/7/14; resolver handles all six spec types per research; mypy strict passes; interrogate ≥95% on the module.
  </done>
</task>

<task type="auto">
  <name>Task 2: Re-export presets from ketu/aspects/__init__.py</name>
  <files>ketu/aspects/__init__.py</files>
  <action>
    Edit `ketu/aspects/__init__.py` (currently 86 lines, exports calculator/windows/timelines/transits APIs).

    Add one new import block after the existing imports (e.g. after the `transits` import block, before the `__all__` list):

        # Aspect set presets and resolver (Phase 9)
        from ketu.aspects.presets import (
            CLASSICAL,
            TRADITIONAL,
            EXTENDED,
            AspectSetSpec,
            resolve_aspect_set,
        )

    Append to `__all__` (in a new "Presets" section comment for readability):

            # Presets
            "CLASSICAL",
            "TRADITIONAL",
            "EXTENDED",
            "AspectSetSpec",
            "resolve_aspect_set",

    Do NOT remove or reorder existing exports. Do NOT change the docstring (it already documents the subpackage as the place for "Core aspect calculations" — presets fit naturally).

    Optional: add a one-line update to the module docstring's submodule list mentioning `presets`.
  </action>
  <verify>
    Run: `python -c "from ketu.aspects import CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set; print('OK')"`.
    Run: `python -c "import ketu.aspects as A; assert 'CLASSICAL' in A.__all__ and 'resolve_aspect_set' in A.__all__; print('OK')"`.
    All existing tests still pass: `pytest tests/test_aspects_vectorization.py tests/test_ketu.py -x` (smoke check that the import-graph wasn't broken).
  </verify>
  <done>
    `from ketu.aspects import CLASSICAL` works; `__all__` includes the five new names; existing test suite passes (no regressions in aspect-related tests).
  </done>
</task>

<task type="auto">
  <name>Task 3: Write tests/test_aspect_presets.py — resolver and constants unit tests</name>
  <files>tests/test_aspect_presets.py</files>
  <action>
    Create a new test file with exhaustive coverage of the resolver and preset constants. Aim for ≥95% module coverage on `ketu/aspects/presets.py` (matches the v1.1 coverage target for new modules).

    Required test functions (each as a separate `def test_*`):

    **Constants (5 tests):**
    1. `test_classical_mask_shape_and_sum` — CLASSICAL.shape == (14,), dtype == np.bool_, sum() == 5, indices [0, 4, 7, 9, 13] are True.
    2. `test_traditional_mask_shape_and_sum` — sum() == 7, indices [0, 1, 4, 7, 9, 11, 13] are True.
    3. `test_extended_mask_shape_and_sum` — sum() == 14, all True.
    4. `test_classical_is_frozen` — `with pytest.raises(ValueError): CLASSICAL[0] = False`.
    5. `test_traditional_extends_classical` — `np.all(CLASSICAL & TRADITIONAL == CLASSICAL)` (CLASSICAL is a strict subset of TRADITIONAL).

    **Resolver — happy paths (8 tests):**
    6. `test_resolve_none_returns_classical` — `np.array_equal(resolve_aspect_set(None), CLASSICAL)`.
    7. `test_resolve_classical_string_lowercase` — `np.array_equal(resolve_aspect_set("classical"), CLASSICAL)`.
    8. `test_resolve_classical_string_mixed_case` — case-insensitive: `"Classical"`, `"CLASSICAL"`, `"classIcal"` all resolve.
    9. `test_resolve_traditional_string` — string "traditional" → TRADITIONAL.
    10. `test_resolve_extended_string` — string "extended" → EXTENDED.
    11. `test_resolve_name_list_parametrized` — pytest.mark.parametrize over: `(["Conjunction"], [0])`, `(["Trine", "Square"], [7, 9])`, `(["Conjunction", "Sextile", "Square", "Trine", "Opposition"], [0, 4, 7, 9, 13])`.
    12. `test_resolve_index_list` — `[0, 4, 7, 9, 13]` → CLASSICAL.
    13. `test_resolve_bool_mask_passthrough` — custom length-14 bool mask returns equal mask.
    14. `test_resolve_int_ndarray_indices` — `np.array([0, 13])` → mask with positions 0 and 13 True.

    **Resolver — error paths (6 tests):**
    15. `test_resolve_unknown_preset_raises_with_valid_options` — `pytest.raises(ValueError, match="unknown aspect preset")`. Message must list all three preset names.
    16. `test_resolve_unknown_aspect_name_raises` — `pytest.raises(ValueError, match="unknown aspect name")`.
    17. `test_resolve_out_of_range_index_raises` — index 14, -1, 100 each raises with "out of range".
    18. `test_resolve_wrong_length_bool_mask_raises` — length-13 or length-15 bool mask raises with "shape".
    19. `test_resolve_invalid_item_type_raises` — `[1.5]`, `[None]`, `[object()]` raise with "invalid aspect spec item".
    20. `test_resolve_unknown_name_lists_valid_options` — when name unknown, error message includes all 14 decoded names.

    **Custom default behavior (1 test):**
    21. `test_resolve_with_custom_default` — `resolve_aspect_set(None, default=EXTENDED)` returns EXTENDED.

    **Style requirements:**
    - Use pytest (not unittest) — matches existing `tests/test_aspects_vectorization.py` style.
    - Use `np.testing.assert_array_equal` for mask comparisons.
    - Numpydoc not required on test functions, but each test should have a one-line docstring.
    - Type hints on test parameters where pytest.parametrize is used.
  </action>
  <verify>
    `pytest tests/test_aspect_presets.py -v` — all tests pass.
    `pytest tests/test_aspect_presets.py --cov=ketu/aspects/presets --cov-report=term-missing` — coverage ≥95% on `ketu/aspects/presets.py`.
  </verify>
  <done>
    Test file exists with ≥21 test functions (or fewer if parametrize collapses some into one); pytest passes; coverage ≥95% on `ketu/aspects/presets.py`; all happy paths and error paths from research §"Resolver dispatch test pattern" are covered.
  </done>
</task>

</tasks>

<verification>
- `python -c "from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED, resolve_aspect_set"` succeeds.
- `python -c "from ketu.aspects import CLASSICAL"` succeeds (re-export works).
- `pytest tests/test_aspect_presets.py -v` — all tests pass.
- `pytest tests/ -x` (full suite, smoke) — no existing test broken by the new import.
- `mypy --strict ketu/aspects/presets.py` — passes.
- `interrogate ketu/aspects/presets.py -f 95` — passes (≥95% docstring coverage).
- `pytest --cov=ketu/aspects/presets --cov-report=term` — ≥95% coverage on the new module.
- `core.aspects` is UNCHANGED. Confirm with `git diff ketu/core.py` — no output.
</verification>

<success_criteria>
- ASP-02 satisfied: `from ketu.aspects.presets import CLASSICAL, TRADITIONAL, EXTENDED` resolves to length-14 masks summing to 5, 7, 14.
- ASP-04 foundation satisfied: `resolve_aspect_set(None)` returns CLASSICAL — observable via unit test.
- ASP-05 foundation satisfied: resolver returns a single boolean mask in one call (ready for hot-loop replacement in Plan 09-04).
- ASP-06 documented (not yet enforced — no new caches added in this plan): forward-looking comment in `presets.py` per research Pitfall 4.
- All five names exported from `ketu.aspects` subpackage `__init__`.
- No change to `ketu/core.py` (append-only invariant preserved).
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-02-SUMMARY.md` documenting:
- Module artifact (presets.py) line count and test coverage %
- Resolver behavior matrix (input type → output)
- Confirmation of ASP-02, ASP-04 (foundation), ASP-05 (foundation), ASP-06 (documented) satisfaction
- Note: API parameter wiring (the actual `aspects=` parameter on calculator functions) is Plan 09-04, not this plan.
</output>
