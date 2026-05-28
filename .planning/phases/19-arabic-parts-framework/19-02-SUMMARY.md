---
phase: 19-arabic-parts-framework
plan: "02"
subsystem: cli
tags: [arabic-parts, cli, introspection, argparse, ketu-parts]

# Dependency graph
requires:
  - phase: 19-01
    provides: "ketu/parts/ subpackage with PARTS registry (fortune/spirit/marriage)"
provides:
  - "--list-parts CLI introspection flag (PARTS-08)"
  - "cmd_list_parts() function in ketu/cli/introspection.py"
  - "_PART_DESCRIPTIONS dict with formula summaries for all 3 parts"
affects:
  - 19-03
  - phase-20

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "data-driven CLI introspection: sorted(PARTS.keys()) iteration for automatic v1.3 surface"
    - "first-wins ladder: --list-parts appended LAST after --list-orbs in main() short-circuit"

key-files:
  created: []
  modified:
    - ketu/cli/introspection.py
    - ketu/cli/parser.py

key-decisions:
  - "--list-parts appended LAST in first-wins ladder (after list_orbs) — preserves test_list_flags_collision_first_wins regression"
  - "data-driven iteration over sorted(_PARTS.keys()) — v1.3 Lots surface automatically without touching cmd_list_parts"
  - "trailing Marriage note ('fixed formula - day and night formulas are identical') as canonical location for the fixed-formula annotation"

patterns-established:
  - "cmd_list_parts mirrors cmd_list_house_systems pattern: {name:10} column, header, blank lines, trailing note"
  - "CLI introspection imports _PARTS as a module-level alias — consistent with _HOUSE_SYSTEMS pattern"

# Metrics
duration: ~2min
completed: "2026-05-28"
---

# Phase 19 Plan 02: CLI --list-parts Introspection Summary

**`--list-parts` store_true flag + `cmd_list_parts()` wired into ketu CLI, iterating `sorted(PARTS.keys())` with formula summaries and a fixed-formula trailing note for Marriage (PARTS-08)**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-28T19:30:40Z
- **Completed:** 2026-05-28T19:33:19Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `cmd_list_parts()` + `_PART_DESCRIPTIONS` added to `ketu/cli/introspection.py`, mirroring `cmd_list_house_systems` pattern exactly
- `--list-parts` argparse flag wired in `build_parser()` after `--list-orbs`; short-circuit added LAST in `main()` first-wins ladder
- `ketu --list-parts` prints 3 sorted parts with formula summaries and trailing Marriage note; exits 0
- interrogate 100% (5/5 functions in introspection.py documented); `test_list_flags_collision_first_wins` unaffected; 1253 PASS + 2 SKIP baseline unchanged

## Task Commits

1. **Task 1: cmd_list_parts() + _PART_DESCRIPTIONS** - `bb001c6` (feat)
2. **Task 2: --list-parts flag + short-circuit in parser.py** - `b48b32d` (feat)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `ketu/cli/introspection.py` — added `from ketu.parts import PARTS as _PARTS`, `_PART_DESCRIPTIONS` dict, and `cmd_list_parts()` function (19 lines added)
- `ketu/cli/parser.py` — extended introspection import to include `cmd_list_parts`; added `--list-parts` store_true flag; added `if args.list_parts:` short-circuit last in ladder (9 lines added)

## Decisions Made

- `--list-parts` appended LAST in first-wins ladder (after `list_orbs`) to preserve `test_list_flags_collision_first_wins` pin (Phase 16-04 decision: ladder order = source-declaration order, NOT alphabetical).
- Data-driven iteration over `sorted(_PARTS.keys())` so a v1.3 Lot registered via `register()` surfaces automatically in the CLI output without touching `cmd_list_parts` — mirrors `cmd_list_orbs` / `cmd_list_house_systems` convention.
- Trailing note `"Marriage note: fixed formula - day and night formulas are identical."` is the canonical location for the no-sect-inversion annotation (Plan 03 CLI test asserts on it).

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- PARTS-08 satisfied: `ketu --list-parts` discoverable introspection flag live.
- Ready for Plan 19-03: test suite (CLI tests for `--list-parts` + unit tests for `calculate_part` / `calculate_all_parts`).
- Suite baseline: 1253 PASS + 2 SKIP (unchanged from Plan 19-01).

---
*Phase: 19-arabic-parts-framework*
*Completed: 2026-05-28*
