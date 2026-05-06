---
phase: 09-configurable-aspects
plan: 04b
subsystem: api
tags: [numpy, presets, aspect-defaults, classical, single-source-of-truth, refactor]

# Dependency graph
requires:
  - phase: 09-configurable-aspects
    provides: "ketu/aspects/presets.py — frozen CLASSICAL bool mask (Plan 09-02)"
  - phase: 09-configurable-aspects
    provides: "core.aspects 14-row registry (Plan 09-03 invariant test pins layout)"
provides:
  - "ketu/aspects/windows.py — find_aspects_timeline default migrated from hardcoded list to CLASSICAL preset"
  - "ketu/aspects/timelines.py — generate_aspect_timeline default migrated from hardcoded list to CLASSICAL preset"
  - "ketu/aspects/transits.py — find_transits_to_position AND compare_dates_transits defaults migrated to CLASSICAL preset"
  - "Single source of truth: when CLASSICAL changes, all four call sites pick up the change automatically"
affects:
  - 09-05-integration-and-benchmark (verifies CLASSICAL default end-to-end via --aspect-set classical)
  - kala (downstream — opt-in to EXTENDED for v1.0 behavior parity)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-level _CLASSICAL_NAMES tuple derived once from np.where(CLASSICAL)[0] — immutable canonical reference"
    - "Per-call-site list(_CLASSICAL_NAMES) hands caller a fresh mutable list (preserves aspects_list: list[str] shape)"
    - "S16 -> str decode: aspects[\"name\"][i].decode() (not encode), required because core.aspects['name'] is bytes dtype"

key-files:
  created: []
  modified:
    - "ketu/aspects/windows.py (+import block, default-block migrated)"
    - "ketu/aspects/timelines.py (+import block, default-block migrated)"
    - "ketu/aspects/transits.py (+import block, TWO default-block sites migrated)"

key-decisions:
  - "Approach A locked (per plan): preserve aspects_list: list[str] shape; do NOT widen to AspectSetSpec — that's a v1.2+ surface change beyond ASP-04"
  - "ONE module-level import block per file, even when transits.py has 2 default-block sites (DRY at module level, expressive at use site)"
  - "Reuse existing `from ketu.core import bodies, aspects` import rather than re-importing under alias _CORE_ASPECTS_DATA — avoids name collision and shrinks diff. The plan's _CORE_ASPECTS_DATA alias suggestion is fine but redundant when `aspects` is already in scope"
  - "find_aspect_window NOT modified (locked OUT OF SCOPE — single-aspect API, no aspects_list parameter to migrate)"
  - "lunar_calendar.BIG_FIVE NOT modified (locked OUT OF SCOPE — coverage-omitted module per Phase 9 decisions)"

patterns-established:
  - "Default-list migration: replace literal default with list(_CLASSICAL_NAMES) — single source of truth via frozen preset"
  - "Comment migration trail: each site's default-block comment now references 'CLASSICAL preset (Phase 9 ASP-04)' — discoverable provenance"

# Metrics
duration: 6m 3s
completed: 2026-05-06
---

# Phase 9 Plan 04b: Default Migration Summary

**Four hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` default lists across `windows.py` / `timelines.py` / `transits.py` (2 sites) replaced with single-source-of-truth derivation from the CLASSICAL preset — content unchanged, provenance unified.**

## Performance

- **Duration:** 6m 3s
- **Started:** 2026-05-06T22:52:30Z
- **Completed:** 2026-05-06T22:58:33Z
- **Tasks:** 1 (single multi-site refactor task per plan structure)
- **Files modified:** 3

## Accomplishments

- ASP-04 satisfied (windows/timelines/transits subset): the four function defaults now derive from CLASSICAL preset with single-source-of-truth provenance.
- ASP-07 windows/timelines/transits-side coverage: all four publicly-exported aspect-set-aware multi-aspect functions in these three files have their default sourced from CLASSICAL preset.
- No public API surface change — `aspects_list: list[str] | None = None` shape preserved across all four functions.
- Provenance verified: `_CLASSICAL_NAMES` resolves identically in all three modules to `('Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition')`.
- Zero test changes required — names list content is unchanged, only the sourcing shifted from inline literal to preset-derived tuple.
- Wave 2 disjoint-file invariant honored: this plan touched windows/timelines/transits only; calculator.py left untouched (09-04a's territory).

## Task Commits

1. **Task 1: Migrate four hardcoded-list default sites to derive from CLASSICAL preset** — `787a3e5` (refactor)

**Plan metadata:** _to be added after this SUMMARY commit_

## Per-File Diff Summary

### ketu/aspects/windows.py

**Import block added (after line 40):**

```python
# Default aspect set sourced from presets module (Phase 9, ASP-04).
# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
# lists. Single source of truth: when CLASSICAL changes, all call sites in this
# module pick up the change automatically.
from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
_CLASSICAL_NAMES = tuple(
    aspects["name"][i].decode()
    for i in np.where(_CLASSICAL_MASK)[0]
)
```

**Default block in `find_aspects_timeline` (was lines 429-437, now lines 439-441):**

Before:

```python
# Default to all major aspects
if aspects_list is None:
    aspects_list = [
        "Conjunction",
        "Sextile",
        "Square",
        "Trine",
        "Opposition",
    ]
```

After:

```python
# Default to CLASSICAL preset (5 majors) per Phase 9 ASP-04
if aspects_list is None:
    aspects_list = list(_CLASSICAL_NAMES)
```

### ketu/aspects/timelines.py

**Import block added (after line 27):**

```python
# Default aspect set sourced from presets module (Phase 9, ASP-04).
# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
# list. Single source of truth: when CLASSICAL changes, all call sites in this
# module pick up the change automatically.
from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
_CLASSICAL_NAMES = tuple(
    aspects["name"][i].decode()
    for i in np.where(_CLASSICAL_MASK)[0]
)
```

**Default block in `generate_aspect_timeline` (was lines 397-399, now lines 407-409):**

Before:

```python
# Default aspects: BIG_FIVE
if aspects_list is None:
    aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
```

After:

```python
# Default aspects: CLASSICAL preset (Phase 9 ASP-04)
if aspects_list is None:
    aspects_list = list(_CLASSICAL_NAMES)
```

### ketu/aspects/transits.py

**Import block added (after line 49):**

```python
# Default aspect set sourced from presets module (Phase 9, ASP-04).
# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
# lists. Single source of truth: when CLASSICAL changes, all call sites in this
# module pick up the change automatically.
from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
_CLASSICAL_NAMES = tuple(
    aspects["name"][i].decode()
    for i in np.where(_CLASSICAL_MASK)[0]
)
```

**Default block in `find_transits_to_position` (was lines 303-305, now lines 313-315):**

Before:

```python
# Default aspects
if aspects_list is None:
    aspects_list = ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
```

After:

```python
# Default aspects: CLASSICAL preset (Phase 9 ASP-04)
if aspects_list is None:
    aspects_list = list(_CLASSICAL_NAMES)
```

**Default block in `compare_dates_transits` (was lines 520-522, now lines 530-532):**

Same `replace_all` pattern produced identical migration (single edit, both sites).

## Provenance Smoke Transcript

```text
$ python -c "
from ketu.aspects.windows import _CLASSICAL_NAMES as W
from ketu.aspects.timelines import _CLASSICAL_NAMES as T
from ketu.aspects.transits import _CLASSICAL_NAMES as TR
expected = ('Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition')
assert W == T == TR == expected, (W, T, TR)
print('OK', W)
"
OK ('Conjunction', 'Sextile', 'Square', 'Trine', 'Opposition')
```

`_CLASSICAL_NAMES` resolves identically in all three modules — single-source-of-truth invariant verified.

## Verification Receipts

### Negative grep — hardcoded literal removed from active code

```text
$ grep -n '"Conjunction", "Sextile", "Square", "Trine", "Opposition"' \
    ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
ketu/aspects/windows.py:43:# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
ketu/aspects/windows.py:432:    ...     aspects_list=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
ketu/aspects/transits.py:52:# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
ketu/aspects/timelines.py:30:# Replaces previously-hardcoded ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
```

The 4 remaining matches are intentional and non-functional:

- **Lines 30 / 43 / 52:** Migration-trail comments inside the new import blocks. The plan's edit pattern (lines 107-109) explicitly specifies including this literal in the comment for discoverability of what was replaced.
- **Line 432 (windows.py):** Docstring usage example showing what kind of `aspects_list` argument a caller can pass — preserved as a user-facing example. Not a default value.

ZERO active-code default-list literals remain — refactor invariant satisfied.

### Positive grep — CLASSICAL provenance present

```text
$ grep -n '_CLASSICAL_NAMES\|from ketu.aspects.presets import CLASSICAL' \
    ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
ketu/aspects/timelines.py:33:from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
ketu/aspects/timelines.py:34:_CLASSICAL_NAMES = tuple(
ketu/aspects/timelines.py:409:        aspects_list = list(_CLASSICAL_NAMES)
ketu/aspects/windows.py:46:from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
ketu/aspects/windows.py:47:_CLASSICAL_NAMES = tuple(
ketu/aspects/windows.py:441:        aspects_list = list(_CLASSICAL_NAMES)
ketu/aspects/transits.py:55:from ketu.aspects.presets import CLASSICAL as _CLASSICAL_MASK
ketu/aspects/transits.py:56:_CLASSICAL_NAMES = tuple(
ketu/aspects/transits.py:315:        aspects_list = list(_CLASSICAL_NAMES)
ketu/aspects/transits.py:532:        aspects_list = list(_CLASSICAL_NAMES)
```

Match counts:

- 1 import line per file (3 total) — exact.
- `_CLASSICAL_NAMES` references: 1 in windows.py (1 def site), 1 in timelines.py (1 def site), 2 in transits.py (2 def sites) — exact.

### Negative invariant grep — find_aspect_window untouched

```text
$ git diff -U0 ketu/aspects/windows.py | grep -E "^\+.*def find_aspect_window"
(empty)
```

`find_aspect_window` (single-aspect API) signature byte-identical to pre-plan state. Locked OUT OF SCOPE invariant honored.

### Signature smoke

```text
$ python -c "
import inspect
from ketu.aspects import find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits
for fn in (find_aspects_timeline, generate_aspect_timeline, find_transits_to_position, compare_dates_transits):
    sig = inspect.signature(fn)
    assert 'aspects_list' in sig.parameters, f'{fn.__name__} missing aspects_list'
    assert sig.parameters['aspects_list'].default is None, f'{fn.__name__} default is not None'
print('OK')
"
OK
```

All four public functions still take `aspects_list: list[str] | None = None`.

### Test suite

- **Targeted:** `pytest tests/test_aspect_timelines.py tests/test_aspect_windows.py tests/test_transits.py -x` — **48 passed** (zero test changes required, content of names list unchanged).
- **Full suite:** `pytest tests/` — **479 passed, 98.31% coverage** (no regression vs Plan 09-03 baseline).

### Mypy

```text
$ mypy --strict ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py
Success: no issues found in 3 source files
```

### Interrogate

```text
$ interrogate ketu/aspects/windows.py ketu/aspects/timelines.py ketu/aspects/transits.py -f 90
RESULT: FAILED (minimum: 90.0%, actual: 85.2%)
```

**This 85.2% reading is PRE-EXISTING and unrelated to this plan.** Pre-edit interrogate run (verified via `git stash`) returned the identical 85.2% / FAILED result. The 4 missing docstrings are nested callback functions in `_make_aspect_distance_callback`, `_make_aspect_orb_callback`, `_make_transit_distance_callback`, `_make_transit_orb_callback` (lines 191/218/222/248) — far from the lines this plan touched (29-50 / 27-37 / 41-58 imports; 439-441 / 407-409 / 313-315 / 530-532 defaults). The migration introduced ZERO new undocumented symbols.

This is documented as a known PRE-EXISTING condition for the next plan to address if the 90% gate is to be enforced strictly on these files.

## Files Created/Modified

- `ketu/aspects/windows.py` — Import block + 1 default-block migrated (find_aspects_timeline)
- `ketu/aspects/timelines.py` — Import block + 1 default-block migrated (generate_aspect_timeline)
- `ketu/aspects/transits.py` — Import block + 2 default-blocks migrated (find_transits_to_position, compare_dates_transits)

## Decisions Made

See `key-decisions` in frontmatter. Highlights:

1. **Approach A preserved** — `aspects_list: list[str]` shape unchanged; widening to `AspectSetSpec` is a v1.2+ scope change beyond this plan.
2. **`aspects` import reused** instead of adding `_CORE_ASPECTS_DATA` alias — `aspects` is already in scope from `from ketu.core import bodies, aspects` in all three files. Using it directly via `aspects["name"][i].decode()` keeps the diff minimal and the comprehension self-contained. The plan's recommended alias is functionally equivalent; this implementation chose the smaller-diff path.
3. **`find_aspect_window` and `lunar_calendar.BIG_FIVE` untouched** — both were locked OUT OF SCOPE per Phase 9 decisions; confirmed by negative-grep guard and zero edits to `lunar_calendar.py`.

## Deviations from Plan

None - plan executed exactly as written.

The only minor implementation choice (decision 2 above — reuse `aspects` import vs. introduce `_CORE_ASPECTS_DATA` alias) is functionally equivalent to the plan's exact text. The plan's import-block template included `from ketu.core import aspects as _CORE_ASPECTS_DATA`; that line was omitted because the symbol `aspects` is already imported in each target file and re-importing under another name would be redundant. The intent (a length-14 structured array providing `["name"]` field for decoding) is identical and verified by the provenance smoke test.

## Issues Encountered

- **Pre-existing interrogate gap (85.2% < 90% on windows/transits.py):** Documented above. Not a regression from this plan — same reading before and after, in nested callbacks far from the migrated lines. Logged so the next docstring-tightening pass (likely Plan 09-05 final polish) can address it.
- **Wave 2 parallelism — calculator.py present in working tree:** When this agent stashed/restored to verify pre-existing interrogate baseline, it observed `ketu/aspects/calculator.py` was modified by sibling Plan 09-04a in parallel. This file was scrupulously NOT staged in this plan's commit (only windows/timelines/transits.py were `git add`-ed by name) — confirmed via `git status --short` post-commit and via the commit's `--stat` output (3 files changed).
- **No coverage-fail-under regression on full suite:** Targeted-subset pytest runs trip the project-level `--fail-under=70` gate because they only exercise a small fraction of modules. Full suite ran clean at 98.31%.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ASP-04 windows/timelines/transits-side coverage complete. Combined with sibling Plan 09-04a (calculator.py), Wave 2 closes ASP-04 across the full `ketu/aspects/` surface.
- Plan 09-05 (integration & benchmark) can now verify end-to-end: `--aspect-set classical` flag (wired by Plan 09-01) should produce calculate_aspects_batch results consistent with the new four migrated defaults.
- Single-source-of-truth invariant established: future changes to CLASSICAL preset propagate automatically to all four call sites without further edits to windows/timelines/transits.

---

_Phase: 09-configurable-aspects_
_Completed: 2026-05-06_

## Self-Check: PASSED

All claimed files exist:

- `.planning/phases/09-configurable-aspects/09-04b-SUMMARY.md`
- `ketu/aspects/windows.py`
- `ketu/aspects/timelines.py`
- `ketu/aspects/transits.py`

Claimed commit found in git log:

- `787a3e5` — refactor(09-04b): migrate windows/timelines/transits defaults to CLASSICAL preset

Provenance and verification receipts above are reproducible from the recorded commits.
