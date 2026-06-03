---
phase: 31-documentation-en-fr
plan: "03"
subsystem: docs
tags: [aspects, TRADITIONAL, synastry, DOC-15]

requires:
  - phase: 28-dynamic-harmonic-generator
    provides: "TRADITIONAL as library-wide default for calculate_aspects (v1.3+)"
  - phase: 26-aspects-data-driven
    provides: "CLASSICAL/TRADITIONAL/EXTENDED distinction established"

provides:
  - "relational_charts.md compute_chart aspects param names TRADITIONAL as library default"
  - "relational_charts.md calculate_synastry aspects param clarifies classical is function-level default, pinned for byte stability"

affects:
  - 31-documentation-en-fr
  - 32-release-v1-4-0

tech-stack:
  added: []
  patterns:
    - "Distinguish library-wide default (TRADITIONAL) from function-level pinned default (classical in calculate_synastry)"

key-files:
  created: []
  modified:
    - docs/source/relational_charts.md

key-decisions:
  - "calculate_synastry aspects='classical' default is INTENTIONAL and must NOT be changed to TRADITIONAL — backward-compat byte stability"
  - "compute_chart aspects=None resolves to TRADITIONAL (7 half-circle aspects, v1.3+), not classical"

patterns-established:
  - "When documenting function defaults that differ from the library default, explicitly name both and state the reason for the deviation"

duration: 1min
completed: 2026-06-03
---

# Phase 31 Plan 03: relational_charts.md Aspects-Default Correction Summary

**Two surgical doc edits: compute_chart aspects=None now names TRADITIONAL as library default; calculate_synastry aspects="classical" explicitly framed as function-level backward-compat default, distinct from library-wide TRADITIONAL**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-06-03T14:07:26Z
- **Completed:** 2026-06-03T14:08:05Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- compute_chart `aspects` parameter (line 18): replaced "default classical set" with explicit TRADITIONAL (7 half-circle aspects, v1.3+)
- calculate_synastry `aspects` parameter (line 81): added clarifying note that `"classical"` is the function's own pinned default for backward-compatible byte stability, explicitly distinguished from the library-wide TRADITIONAL default of `calculate_aspects`
- calculate_synastry function signature (`aspects="classical"`) left unchanged — intentional default preserved

## Task Commits

1. **Task 1 + Task 2: Fix compute_chart + clarify calculate_synastry aspects defaults** — `2d1a522` (docs)

## Files Created/Modified

- `docs/source/relational_charts.md` — Two line edits fixing stale "default classical set" claim and adding synastry aspects-default clarification

## Decisions Made

- `calculate_synastry`'s `aspects="classical"` default is intentional and must NOT be changed to TRADITIONAL; the fix is to document the distinction, not change the signature.
- The plan specifies both edits in one file; committed together as a single atomic commit covering both tasks.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Verification Results

```
$ grep -n "default classical set" docs/source/relational_charts.md
(0 hits)

$ grep -n 'aspects="classical"' docs/source/relational_charts.md
75:calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")

$ grep -n "TRADITIONAL" docs/source/relational_charts.md
18:- `aspects` — aspect set spec (`None` uses the library default — **TRADITIONAL**, the 7 half-circle aspects, v1.3+)
81:- `aspects` — aspect set: `"classical"`, `"traditional"`, `"extended"`, or a list/mask. `calculate_synastry`'s own default is `"classical"` (5 major aspects), **pinned for backward-compatible byte stability** — this is distinct from the library-wide default of `calculate_aspects`, which is **TRADITIONAL** (7 half-circle aspects, v1.3+).
```

All must-have truths satisfied:
- compute_chart aspects param no longer says "default classical set" — names TRADITIONAL (v1.3+)
- calculate_synastry aspects param clarifies "classical" is the function's own default (backward-compat), distinct from library-wide TRADITIONAL
- calculate_synastry signature `aspects="classical"` unchanged
- No remaining text implies the LIBRARY default is classical

## Next Phase Readiness

- DOC-15 satisfied for relational_charts.md
- Phase 31 other plans (01, 02, 04, 05, 06, 07) handle remaining doc files and fr gettext cycle

## Self-Check: PASSED

- `docs/source/relational_charts.md` — FOUND (modified)
- Commit `2d1a522` — FOUND

---
*Phase: 31-documentation-en-fr*
*Completed: 2026-06-03*
