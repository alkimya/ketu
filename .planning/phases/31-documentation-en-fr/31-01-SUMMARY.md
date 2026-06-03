---
phase: 31-documentation-en-fr
plan: 01
subsystem: docs
tags: [sphinx, myst-markdown, aspects, harmonics, chiron, concepts]

# Dependency graph
requires:
  - phase: 30-chiron-range-1900-2100
    provides: "Chiron .npz 1900-2100 (2283 segs, degree=10, gate PASS max|Δλ|=0.001214°)"
  - phase: 28-dynamic-harmonic-generator
    provides: "generate_harmonic_aspects(h) public API with dynamic_specs= integration"
provides:
  - "concepts.md recentred on 180°-division default (TRADITIONAL baseline)"
  - "EXTENDED H5/H9/H10 harmonics removed from tables; framed as 'available in code'"
  - "14-row coefficient table reduced to 7 half-circle aspects (with API pointer for full table)"
  - "generate_harmonic_aspects(h) documented with runnable h=7 example + ~2× orb note"
  - "Chiron range note updated to 1900–2100 with clamping"
affects: [31-02, 31-03, 31-04, 31-05, 31-06, 32-release-preparation-v1-4-0]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "DOC-14: 180°-division default is framing baseline; full-circle opt-in is secondary"
    - "DOC-16: generate_harmonic_aspects documented as dynamic-specs= drop-in consumer"

key-files:
  created: []
  modified:
    - docs/source/concepts.md

key-decisions:
  - "EXTENDED constant kept in code docs (calculate_aspects(jday, aspects=EXTENDED) code example preserved); only removed from doc TABLES"
  - "generate_harmonic_aspects subsection placed immediately after Configurable Aspect Sets, before ## Orbs — logical grouping"
  - "Chiron range: 1950-2050 → 1900-2100 (expanded in v1.4); clamping note added (not ValueError); no 'ValueError' wording per Phase 30-02 decision"
  - "Introductory Harmonic Theory paragraph reframed: 180°-division default is baseline, full-circle opt-in noted without a separate Division-column explanation"

patterns-established:
  - "Half-circle aspects are the narrative baseline; full-circle aspects are presented as opt-in addenda"

# Metrics
duration: 2min
completed: 2026-06-03
---

# Phase 31 Plan 01: Documentation — concepts.md Summary

**concepts.md recentred on the 180°-division default: tables trimmed to 7 half-circle aspects (TRADITIONAL), H5/H9/H10 collapsed to a prose note, generate_harmonic_aspects(h) documented with a runnable h=7 example and accepted-behaviour orb note, Chiron range updated to 1900–2100 with clamping.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-06-03T14:07:19Z
- **Completed:** 2026-06-03T14:09:31Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Collapsed H5/H9/H10 `####` subsections into a single "available in code" prose note after H6
- Summary Table trimmed from 7 rows to 4 rows (H1/H2/H3/H6 only)
- "Aspect Types and Harmonic Coefficients" table trimmed from 14 rows to 7 rows (half-circle only); prose pointer added to API page for full 14-row table
- Reframed Harmonic Theory intro: 180°-division default is baseline; full-circle opt-in noted; stale `180°/n vs 360°/n` Division-column explanation removed
- New `### Dynamic Harmonic Generator (generate_harmonic_aspects)` subsection added between Configurable Aspect Sets and ## Orbs, with runnable h=7 example and ~2× orb note
- Chiron range note updated: 1950–2050 → **1900–2100** (expanded in v1.4); clamping note added

## Table Before/After Row Counts

| Table | Before | After |
| ----- | ------ | ----- |
| Summary Table (data rows) | 7 | 4 |
| Aspect Types and Harmonic Coefficients (data rows) | 14 | 7 |
| H1/H2/H3/H6/H5/H9/H10 `####` subsections | 7 | 4 |

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove H5/H9/H10 from tables, collapse subsections, restructure coefficient table** — `c8a0bd7` (feat)
2. **Task 2: Add generate_harmonic_aspects subsection + orb note, update Chiron range** — `ca9b9ec` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `/home/loc/workspace/ketu/docs/source/concepts.md` — Recentred on 180°-division default; EXTENDED out of tables; generate_harmonic_aspects documented; Chiron 1900–2100

## Decisions Made

- EXTENDED code example (`calculate_aspects(jday, aspects=EXTENDED)`) preserved verbatim — EXTENDED is removed from doc TABLES only, not from code documentation.
- `generate_harmonic_aspects` subsection placed immediately after Configurable Aspect Sets and before `## Orbs` — this maintains the logical flow: named presets → dynamic generator → orb calculation.
- Chiron clamping note added without "ValueError" wording (Phase 30-02 changed behaviour to silent clamping).
- Harmonic Theory intro rewritten: removed the stale "Division column switches between 180°/n and 360°/n" sentence since the Summary Table no longer has 360° rows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated stale introductory paragraph in Harmonic Theory**

- **Found during:** Task 1 (after removing 360° rows from Summary Table)
- **Issue:** The introductory text at lines 72–77 explained that the Division column "switches between 180°/n and 360°/n depending on the harmonic" — but after removing the 360° rows from the Summary Table, this explanation was both inaccurate and confusing.
- **Fix:** Rewrote the Harmonic Theory intro to establish the 180°-division default as the baseline, and relegate full-circle harmonics to a brief opt-in note — consistent with the new framing objective.
- **Files modified:** docs/source/concepts.md
- **Verification:** No stale 360°/n language in table context; intro correctly describes the 4-row Summary Table.
- **Committed in:** c8a0bd7 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — stale paragraph inconsistent with new table structure)
**Impact on plan:** Necessary for coherence; the intro paragraph was describing a Division column that no longer has 360° rows. No scope creep.

## Verification Results (grep checks)

```text
grep -c "360°/5|360°/9|360°/10" → 0  (PASS)
grep -n "aspects=EXTENDED"       → line 135  (PASS)
grep -n "generate_harmonic_aspects" → lines 162, 164, 170, 173, 181  (PASS)
grep -c "1950|2050"              → 0  (PASS)
```

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- concepts.md is complete for Phase 31; sibling plans 31-02..31-06 edit other files independently.
- Phase 31 Wave 2 (gettext cycle) can process concepts.md once all Wave 1 English edits are done.
- The `generate_harmonic_aspects` subsection and the corrected Chiron range note are ready for French translation in Wave 2.

## Self-Check: PASSED

- `docs/source/concepts.md`: FOUND
- `31-01-SUMMARY.md`: FOUND
- Commit `c8a0bd7` (Task 1): FOUND
- Commit `ca9b9ec` (Task 2): FOUND

---
*Phase: 31-documentation-en-fr*
*Completed: 2026-06-03*
