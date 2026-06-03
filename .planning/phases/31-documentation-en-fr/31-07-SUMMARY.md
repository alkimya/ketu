---
phase: 31-documentation-en-fr
plan: 07
subsystem: docs/i18n
tags: [gettext, fr, sphinx-intl, DOC-17]
dependency_graph:
  requires: [31-01, 31-02, 31-03, 31-04, 31-05, 31-06]
  provides: [fr-gettext-cycle-complete, en-fr-builds-clean]
  affects: [docs/locale/fr/LC_MESSAGES/*.po, docs/locale/fr/LC_MESSAGES/*.mo]
tech_stack:
  added: []
  patterns: [gettext-extract-merge-translate-compile, myst-label-for-xref]
key_files:
  created: []
  modified:
    - docs/locale/fr/LC_MESSAGES/concepts.po
    - docs/locale/fr/LC_MESSAGES/migration.po
    - docs/locale/fr/LC_MESSAGES/relational_charts.po
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/chiron.po
    - docs/locale/fr/LC_MESSAGES/changelog.po
    - docs/locale/fr/LC_MESSAGES/architecture.po
    - docs/locale/fr/LC_MESSAGES/concepts.mo
    - docs/locale/fr/LC_MESSAGES/migration.mo
    - docs/locale/fr/LC_MESSAGES/relational_charts.mo
    - docs/locale/fr/LC_MESSAGES/api.mo
    - docs/locale/fr/LC_MESSAGES/chiron.mo
    - docs/locale/fr/LC_MESSAGES/changelog.mo
    - docs/locale/fr/LC_MESSAGES/architecture.mo
    - docs/source/concepts.md
    - docs/source/architecture.md
decisions:
  - "MyST explicit label syntax used for internal heading xrefs: add `(anchor-id)=` before heading to allow `#anchor-id` fragment links without myst.xref_missing warnings (MyST v5 does not auto-resolve fragment-only links during build)"
  - "architecture.md Chiron range updated to 1900-2100 / 2283 segs / 0.001214° as part of this plan (was out-of-scope for Wave-1 but caught by requirement grep)"
metrics:
  duration_minutes: 45
  completed_date: "2026-06-03"
  tasks_completed: 2
  files_modified: 16
---

# Phase 31 Plan 07: French Gettext Cycle (DOC-17) Summary

Full French gettext cycle on the 6 Wave-1-edited catalogs: re-extract POTs, merge fuzzies/empties, translate all to zero-English-fallback French, recompile .mo, and verify en+fr Sphinx builds at exactly 1 warning each (display_version baseline).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Re-extract POTs, merge, translate 6+1 catalogs | 19a780b | concepts.po, migration.po, relational_charts.po, api.po, chiron.po, changelog.po, architecture.po, concepts.md, architecture.md |
| 2 | Recompile .mo + verify en+fr builds at 1 warning | 5365c21 | 7 × .mo |

## Per-catalog Fuzzy/Empty counts (before → after)

| Catalog | Fuzzy before | Empty before | Fuzzy after | Empty after |
|---------|-------------|-------------|------------|------------|
| concepts.po | 3 | 9 | 0 | 0 |
| migration.po | 0 | 2 | 0 | 0 |
| relational_charts.po | 1 | 1 | 0 | 0 |
| api.po | 1 | 7 | 0 | 0 |
| chiron.po | 3 | 1 | 0 | 0 |
| changelog.po | 4 | 5 | 0 | 0 |
| architecture.po (deviation) | 2 | 0 | 0 | 0 |

All 6 originally-touched catalogs: 0 empty, 0 fuzzy (PASS).
Other 10 untouched catalogs: 0 fuzzy (PASS).

## Build Verification

| Build | WARNING count | WARNING text |
|-------|---------------|--------------|
| make html (EN) | 1 | "l'option 'display_version' n'est pas supportée pour ce thème" |
| make html-fr (FR) | 1 | "l'option 'display_version' n'est pas supportée pour ce thème" |

Both builds at exactly the 1-warning baseline. No myst.xref_missing, no myst.header, no broken xref.

## Recompiled .mo Sizes

| File | Size |
|------|------|
| api.mo | 28703 bytes |
| changelog.mo | 21956 bytes |
| chiron.mo | 5956 bytes |
| concepts.mo | 28279 bytes |
| migration.mo | 13379 bytes |
| relational_charts.mo | 9703 bytes |
| architecture.mo | (recompiled) |

## Requirement Greps (Final)

| Grep | Expected | Result |
|------|----------|--------|
| `1950\|2050` in docs/source/ (excl. changelog.md) | 0 | PASS (0) |
| `kala` in docs/source/ | 0 | PASS (0) |
| stale default strings | 0 | PASS (0) |
| `generate_harmonic_aspects` in api.md | ≥1 | PASS (4) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed myst.xref_missing warnings in concepts.md**
- **Found during:** Task 1 (gettext extraction)
- **Issue:** Internal links `[Configurable Aspect Sets](#configurable-aspect-sets-new-in-v11-updated-in-v13)` used wrong slug (v11 without dot). MyST v5 generates `v1-1` not `v11`. Two occurrences.
- **Fix:** Added MyST explicit label `(configurable-aspect-sets-new-in-v1-1-updated-in-v1-3)=` before the heading; corrected both fragment URLs in concepts.md.
- **Files modified:** docs/source/concepts.md
- **Commit:** 19a780b

**2. [Rule 2 - Missing Critical] Updated stale Chiron range in architecture.md**
- **Found during:** Task 2 requirement greps
- **Issue:** architecture.md had 3 occurrences of `1950–2050` / `1142 segments` / `0.005695°` — stale v1.3 values not updated during Wave-1 (architecture.md was not in the 6 Wave-1 plans' scope).
- **Fix:** Updated to `1900–2100`, `2283 segments`, `0.001214°` in architecture.md. Re-ran gettext+update-po (architecture.po got 2 fuzzies), translated them, recompiled architecture.mo.
- **Files modified:** docs/source/architecture.md, docs/locale/fr/LC_MESSAGES/architecture.po, docs/locale/fr/LC_MESSAGES/architecture.mo
- **Commit:** 19a780b, 5365c21

## Self-Check: PASSED
