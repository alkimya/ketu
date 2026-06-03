---
phase: 31-documentation-en-fr
plan: "04"
subsystem: api
tags: [documentation, harmonics, chiron, api-reference, markdown]

requires:
  - phase: 28-dynamic-harmonic-generator
    provides: generate_harmonic_aspects(h) function, dynamic_specs parameter, HARMONIC_DTYPE
  - phase: 30-chiron-range-1900-2100
    provides: expanded .npz (2283 segments, 1900-2100), max|Δλ|=0.001214°

provides:
  - generate_harmonic_aspects(h) documented in api.md with parameters/returns/raises, H7 runnable example, and full-circle orb note
  - Chiron range corrected to 1900-2100 (2283 segments, clamping) and accuracy to 0.001214°
  - No Kala references in api.md (0 hits verified)

affects: [32-release-v1-4-0, api.md consumers]

tech-stack:
  added: []
  patterns:
    - "Dynamic-specs subsection placed between aspects_for_harmonics and core.aspects columns"
    - "Chiron range/accuracy updated in-place without touching heading or code examples"

key-files:
  created: []
  modified:
    - docs/source/api.md

key-decisions:
  - "Subsection inserted between aspects_for_harmonics (line 189) and core.aspects columns (line 250+29) — no surrounding content changed"
  - "Chiron heading kept as 'New in v1.3' (Chiron shipped in v1.3); only the v1.4 range/accuracy numbers updated"
  - "MD032 blank-line warning fixed inline (blank line after **Parameters:** label)"

duration: 2min
completed: 2026-06-03
---

# Phase 31 Plan 04: api.md — generate_harmonic_aspects + Chiron range/accuracy Summary

**`generate_harmonic_aspects(h)` API subsection added to api.md (DOC-16), Chiron range corrected from 1950-2050/0.005695° to 1900-2100/0.001214° (DOC-15/DOC-16), 0 Kala references.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-06-03T14:07:41Z
- **Completed:** 2026-06-03T14:09:17Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Inserted `generate_harmonic_aspects(h)` subsection with full Parameters/Returns/Raises, a runnable H7 example (septile family), and the mandatory full-circle orb note ("accepted behaviour; the two conventions coexist without unification").
- Corrected the Chiron "Key facts" bullet: valid date range 1950-2050 → 1900-2100 (2283 segments, v1.4 expanded); added clamping note; max error 0.005695° → 0.001214°.
- Verified 0 Kala references and the Preset Aspect Sets table (TRADITIONAL = Library default v1.3+) unchanged.

## Task Commits

1. **Task 1: Add generate_harmonic_aspects(h) subsection** — `7e1a6f1` (feat)
2. **Task 2: Correct Chiron range/accuracy** — `2261091` (fix)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `docs/source/api.md` — new subsection (29 lines inserted between lines 219-221), two Chiron bullet lines updated

## Decisions Made

- `**Parameters:**` followed by a blank line before the list item to satisfy MD032/blanks-around-lists linter (auto-fixed inline — Rule 1).
- Chiron heading unchanged ("New in v1.3") per plan note: Chiron itself shipped v1.3, only range/accuracy are v1.4 changes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added blank line after `**Parameters:**` to satisfy MD032**
- **Found during:** Task 1 (after edit, IDE reported MD032 warning at line 226)
- **Issue:** `**Parameters:**` immediately followed by a list item without a blank line — linter warns "Lists should be surrounded by blank lines"
- **Fix:** Inserted a blank line between `**Parameters:**` and the `- h (int):` list item
- **Files modified:** docs/source/api.md
- **Verification:** No subsequent MD032 diagnostic reported
- **Committed in:** `7e1a6f1` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - linter compliance)
**Impact on plan:** Cosmetic — improves Markdown conformance with no content change.

## Grep Verification Results

```
generate_harmonic_aspects: 4 hits (subsection heading + 2 code lines + import)
dynamic_specs: 3 hits (Returns description + comment + code line)
1900–2100: 2 hits (valid date range + accuracy lines)
0.001214: 2 hits (same lines)
1950 / 2050 / 0.005695: 0 hits
kala (case-insensitive): 0 hits
TRADITIONAL = Library default: 1 hit (table row, unchanged)
```

## Issues Encountered

None.

## Next Phase Readiness

- `api.md` DOC-15 and DOC-16 requirements satisfied for the api reference page.
- Remaining plans in Phase 31 cover concepts.md, migration.md, relational_charts.md, chiron.md, changelog, conf.py, and fr gettext cycle.
- This plan is fully independent of sibling plans (file scope: api.md only).

---
*Phase: 31-documentation-en-fr*
*Completed: 2026-06-03*
