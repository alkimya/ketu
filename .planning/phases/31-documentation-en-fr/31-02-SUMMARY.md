---
phase: 31-documentation-en-fr
plan: "02"
subsystem: docs
tags: [migration, chiron, aspects, EXTENDED, TRADITIONAL, DOC-15, DOC-16]

requires:
  - phase: 30-chiron-range-1900-2100
    provides: "Chiron range 1900-2100, silent clamping behavior (no ValueError)"
  - phase: 26-aspects-data-driven
    provides: "TRADITIONAL as library default (7 half-circle aspects), EXTENDED demoted"

provides:
  - "migration.md with no stale EXTENDED-default claim (DOC-15 satisfied)"
  - "migration.md with corrected Chiron range 1900-2100 and silent clamping (DOC-16 Chiron-behavior satisfied)"

affects:
  - 31-documentation-en-fr (sibling plans: concepts.md, relational_charts.md, api.md)
  - 32-release-v1-4-0

tech-stack:
  added: []
  patterns:
    - "Annotate historical defaults in migration guides (preserve v1.1 history, clarify current default)"

key-files:
  created: []
  modified:
    - docs/source/migration.md

key-decisions:
  - "Historical accuracy preserved: EXTENDED WAS the v1.1 default; migration.md annotates this while pointing to TRADITIONAL as the current v1.3+ default"
  - "Chiron behavior change: Phase 30 changed ValueError to silent clamping; migration.md now reflects both the new range (1900-2100) and new behavior (clamp)"

duration: 1min
completed: "2026-06-03"
---

# Phase 31 Plan 02: Documentation en+fr (migration.md) Summary

**Removed stale EXTENDED-as-default claim from migration.md and corrected Chiron range 1950-2050/ValueError to 1900-2100/silent-clamping (DOC-15 + DOC-16)**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-06-03T14:07:19Z
- **Completed:** 2026-06-03T14:08:30Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Fixed the Chiron date-range line (line 58): "1950–2050 … raises a ValueError" replaced with "1900–2100 (expanded in v1.4) … silently clamped" — reflects Phase 30 runtime change
- Corrected the v1.0→v1.1 prose (line 131): replaced "behavior is unchanged (EXTENDED = all 14 aspects)" with a v1.1 historical annotation + explicit TRADITIONAL pointer to concepts.md
- Fixed the accompanying code comment (line 136): "v1.0 behavior (unchanged default)" rewritten to clarify EXTENDED was the v1.1-era default; current v1.3+ default is TRADITIONAL

## Before / After

### Task 1 — Chiron date-range line

**Before (line 58):**
```
Valid date range: 1950–2050. Attempting to compute Chiron outside this range raises a `ValueError`.
```

**After:**
```
Valid date range: 1900–2100 (expanded in v1.4). Out-of-range input is silently clamped to the nearest segment boundary — no `ValueError` is raised.
```

**grep proof:**
- `grep -n "1900–2100\|clamped" migration.md` → 1 hit (line 58)
- `grep -n "1950–2050" migration.md` → 0 hits
- `grep -n "ValueError" migration.md` → 0 hits

### Task 2 — Stale EXTENDED-default claim

**Before (line 131):**
```
`calculate_aspects` now accepts an optional `aspects` parameter. Without it, behavior is unchanged (EXTENDED = all 14 aspects).
```

**After:**
```
`calculate_aspects` now accepts an optional `aspects` parameter. When introduced in v1.1 the default was `EXTENDED` (all 14 aspects). **As of v1.3 the library default is `TRADITIONAL`** (7 half-circle aspects); see [Aspects](concepts.md) for the preset table.
```

**Before (line 136 code comment):**
```python
# v1.0 behavior (unchanged default)
```

**After:**
```python
# v1.1 default at the time (EXTENDED — all 14 aspects; the current v1.3+ default is TRADITIONAL)
```

**grep proof:**
- `grep -ni "unchanged (EXTENDED\|EXTENDED = all 14 aspects" migration.md` → 0 hits
- `grep -n "TRADITIONAL" migration.md` → 3 hits (line 131 prose, line 134 import, line 136 comment)

## Task Commits

1. **Task 1: Fix Chiron date-range line (1900-2100 + clamping, not ValueError)** - `578a3d0` (fix)
2. **Task 2: Correct stale EXTENDED-default claim in v1.0→v1.1 section** - `19a4168` (fix)

## Files Created/Modified

- `docs/source/migration.md` — Two targeted edits: Chiron range/behavior line and v1.0→v1.1 EXTENDED-default prose + comment

## Decisions Made

- Historical accuracy preserved: the plan explicitly said to annotate EXTENDED as the v1.1-era default while naming TRADITIONAL as the current default — not to erase the v1.1 history. Executed exactly as specified.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- migration.md: DOC-15 (no stale EXTENDED-as-default) and DOC-16 (Chiron 1900-2100 + clamping) both satisfied
- Sibling plans (31-01 concepts.md, 31-03 relational_charts.md, 31-04 api.md, 31-05 chiron.md, 31-06 changelog.md) run in parallel — no dependency on this plan
- Phase 32 (Release v1.4.0) can proceed once all Phase 31 plans are complete

---
*Phase: 31-documentation-en-fr*
*Completed: 2026-06-03*
