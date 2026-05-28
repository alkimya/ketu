---
phase: 19-arabic-parts-framework
plan: "01"
subsystem: astrology
tags: [arabic-parts, hermetic-lots, registry, sect-dispatch, numpy, dataclass]

requires:
  - phase: 14-chart-abstraction-foundation
    provides: CHART_DTYPE + compute_chart + is_day_chart (D-12 sect helper used by calculate_part)

provides:
  - ketu/parts/ subpackage with extensible PARTS registry
  - PartSpec frozen dataclass (name, day_formula, night_formula, description)
  - calculate_part(part_name, chart) -> float — sect-aware via is_day_chart dispatch
  - calculate_all_parts(chart, parts=None) -> dict[str, float]
  - 3 built-in parts registered at import time: fortune, spirit, marriage
  - register()/get_part() registry plumbing for future Lots

affects:
  - 19-02 (CLI --list-parts flag reads PARTS dict and descriptions)
  - 19-03 (oracle tests call calculate_part / calculate_all_parts)
  - ketu.charts.api.is_day_chart (back-reference: ketu/parts/api.py is the first Phase 19 consumer)

tech-stack:
  added: []
  patterns:
    - PartSpec frozen dataclass with day_formula/night_formula (two-callable pattern; no sect_aware flag)
    - register() plain keyword-only function (not decorator — spec carries two callables)
    - sect dispatch: spec.day_formula if is_day else spec.night_formula (pure registry, no if/elif)
    - is_day_chart called fresh per calculate_part invocation (D-12 — never cached in CHART_DTYPE)
    - Marriage night_formula = day_formula identity (sect-invariant by same-object assignment)

key-files:
  created:
    - ketu/parts/__init__.py
    - ketu/parts/registry.py
    - ketu/parts/api.py
  modified: []

key-decisions:
  - "PartSpec two-callable design (day_formula + night_formula) instead of sect_aware bool flag — dispatch is always spec.day_formula if is_day else spec.night_formula with no conditional branching"
  - "Marriage uses night_formula=day_formula identity (same callable object) — self-documenting sect-invariance, no special-case needed in dispatch"
  - "Marriage formula simplified to (2*ASC+180-Venus)%360 (avoids throwaway Descendant variable — RESEARCH Pitfall 4)"
  - "calculate_all_parts default order sorted(PARTS.keys()) — deterministic alphabetical order for ML/oracle tests (RESEARCH Pitfall 5)"
  - "register() is a plain function call not a decorator (unlike houses) — a part has no single function to decorate"

patterns-established:
  - "ketu/parts/ is a structural clone of ketu/houses/ with PartSpec replacing HouseSystemFn"
  - "built-in part registrations inline in __init__.py (3 simple lambdas; _parts_builtin.py not needed)"
  - "numpydoc module docstring summary must fit in a single line (SS06) — applied as Rule 1 auto-fix"

duration: ~4min
completed: "2026-05-28"
---

# Phase 19 Plan 01: Arabic Parts Framework — Registry + API Summary

**`ketu/parts/` subpackage with extensible PARTS registry, PartSpec frozen dataclass, sect-aware calculate_part/calculate_all_parts dispatch, and 3 built-in parts (Fortune, Spirit, Marriage) registered at import time**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-28T19:23:05Z
- **Completed:** 2026-05-28T19:27:08Z
- **Tasks:** 3
- **Files created:** 3

## Accomplishments

- `ketu/parts/registry.py`: `PartSpec` frozen dataclass + `PARTS` dict + `register()` plain keyword-only function + `get_part()` with sorted-available ValueError message
- `ketu/parts/api.py`: `calculate_part` reads `is_day_chart(jd, lat, lon)` fresh per call (D-12), selects `spec.day_formula if is_day else spec.night_formula` — no if/elif ladder; `calculate_all_parts` returns `dict[str, float]` with `sorted(PARTS.keys())` default
- `ketu/parts/__init__.py`: 3 built-in parts registered at import time — Fortune (sect-aware), Spirit (sect-aware mirror), Marriage (fixed; `night_formula=day_formula` identity)
- Full suite 1253 PASS + 2 SKIP (no regressions); interrogate 100% (8/8); numpydoc lint clean

## Task Commits

1. **Task 1: Create the parts registry** — `7f9b4d9` (feat)
2. **Task 2: Create the parts API** — `28c3de2` (feat)
3. **Task 3: Wire __init__.py with public re-exports + 3 built-in parts** — `a3e652a` (feat)

## Files Created

- `/home/loc/workspace/ketu/ketu/parts/registry.py` — PartSpec dataclass, PARTS dict, register(), get_part()
- `/home/loc/workspace/ketu/ketu/parts/api.py` — calculate_part (sect dispatch), calculate_all_parts (filter support)
- `/home/loc/workspace/ketu/ketu/parts/__init__.py` — public re-exports + 3 built-in part registrations

## Decisions Made

- **Two-callable PartSpec** (day_formula + night_formula) instead of `sect_aware: bool` flag — dispatch `spec.day_formula if is_day else spec.night_formula` is unconditional, no branching, no special-casing. Marriage passes the same callable for both.
- **Marriage formula** simplified to `(2*ASC + 180 - Venus) % 360` — avoids a throwaway Descendant variable (RESEARCH Pitfall 4). `description` contains `"fixed - no sect inversion"` as required by the plan.
- **Registrations inline in `__init__.py`** — 3 simple lambdas don't warrant a separate `_parts_builtin.py` module (RESEARCH §__init__.py sanctions either approach).
- **`sorted(PARTS.keys())` default order** in `calculate_all_parts` — deterministic alphabetical (fortune, marriage, spirit) for ML pipelines and oracle tests (RESEARCH Pitfall 5).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed numpydoc SS06 lint error in api.py module docstring**
- **Found during:** Task 3 (overall verification — `make doc-gates` equivalent)
- **Issue:** `ketu/parts/api.py` module docstring opened with a two-line summary ("Sect-aware dispatch for Arabic Parts: :func:`calculate_part` and\n:func:`calculate_all_parts`"); numpydoc SS06 requires the summary to fit on a single line.
- **Fix:** Rewrote the opening summary to a single line: "Sect-aware dispatch for Arabic Parts: :func:`calculate_part` + :func:`calculate_all_parts`."
- **Files modified:** `ketu/parts/api.py`
- **Verification:** `python -m numpydoc lint ketu/parts/api.py` — no output (clean).
- **Committed in:** `a3e652a` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — numpydoc SS06 one-line summary)
**Impact on plan:** Minor cosmetic fix; no logic change. Doc gate stays clean as required.

## Issues Encountered

None — all tasks executed cleanly after the SS06 docstring fix.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `from ketu.parts import PARTS, calculate_part, calculate_all_parts` resolves; PARTS has exactly 3 entries.
- Plan 02 (CLI `--list-parts` flag) can import `PARTS` and iterate `spec.description` immediately.
- Plan 03 (oracle tests) can call `calculate_part` / `calculate_all_parts` with `compute_chart` fixtures.
- PARTS-01 through PARTS-07 satisfied.

---
*Phase: 19-arabic-parts-framework*
*Completed: 2026-05-28*
