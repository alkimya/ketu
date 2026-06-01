---
phase: 26-aspects-data-driven
plan: "03"
subsystem: docs
tags: [changelog, upgrading, sphinx, gettext, i18n, aspects, breaking-change]

requires:
  - phase: 26-aspects-data-driven
    plan: "01"
    provides: "core.aspects 5-field dtype (harmonic + symbol columns)"
  - phase: 26-aspects-data-driven
    plan: "02"
    provides: "aspects_for_harmonics API + library default flip 5->7 + CLI pin"

provides:
  - "CHANGELOG [1.3.0] section: Added (aspects_for_harmonics + harmonic/symbol) + BREAKING (default 5->7)"
  - "UPGRADING v1.2->v1.3 section: two-part default shift + restore recipe + new API + Kala note"
  - "concepts.md: default-now-7 note + aspects_for_harmonics compose example (Harmonic Theory not duplicated)"
  - "api.md: aspects_for_harmonics docs + harmonic/symbol columns + coef==coefficient + 3 stale defaults fixed"
  - "fr gettext catalogs: api.po +18 / concepts.po +10 new msgids (English-fallback); en+fr build at 1 warning"

affects:
  - "27-release: CHANGELOG [1.3.0] + UPGRADING v1.2->v1.3 ready for Phase 27 version bump"

tech-stack:
  added: []
  patterns:
    - "Keep-a-Changelog: new [1.3.0] section placed between [Unreleased] (cycles) and [1.2.0]; Phase 27 merges on version bump"
    - "UPGRADING newest-first: v1.2->v1.3 prepended above v1.1->v1.2"
    - "fr gettext pipeline: make gettext + make update-po; msgstr English-fallback per Phase 25 convention"

key-files:
  created: []
  modified:
    - CHANGELOG.md
    - UPGRADING.md
    - docs/source/concepts.md
    - docs/source/api.md
    - docs/locale/fr/LC_MESSAGES/api.po
    - docs/locale/fr/LC_MESSAGES/concepts.po

key-decisions:
  - "CHANGELOG [1.3.0] placed separately from [Unreleased] (cycles entry stays unreleased); Phase 27 merges on bump"
  - "Three stale EXTENDED-default claims removed from api.md (preset table, calculate_aspects None param, compute_chart param)"
  - "concepts.md dual-base rule NOT duplicated; only the default-now-7 + minors-opt-in note added"
  - "CLI stays classical (5) — documented explicitly in CHANGELOG, UPGRADING, and api.md to prevent user confusion"
  - "coef==coefficient documented conceptually; field name 'coef' unchanged"
  - "Package version NOT bumped (Phase 27 owns REL-10)"

duration: 7min
completed: 2026-06-01
---

# Phase 26 Plan 03: Docs + fr gettext for Aspect Engine Breaking Change Summary

**CHANGELOG [1.3.0] + UPGRADING v1.2->v1.3 + concepts.md/api.md updated + fr gettext regenerated — the complete documentation layer for the v1.3.0 aspect contract**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-01T14:59:21Z
- **Completed:** 2026-06-01T15:06:20Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- **CHANGELOG.md:** new `## [1.3.0]` section (Keep-a-Changelog format) with `### Added`
  (aspects_for_harmonics + harmonic/symbol columns on core.aspects + coef==coefficient note) and
  `### Changed / BREAKING` (default 5→7, two-part shift explained, minors opt-in, CLI-stays-classical note,
  restore pointer to UPGRADING). Package version constants unchanged.

- **UPGRADING.md:** new `## v1.2 -> v1.3` section prepended (newest-first order), covering: the two-part
  default shift (CLASSICAL→TRADITIONAL, what moves in and what stays out), restore recipe with
  before/after code, `aspects_for_harmonics` new-API example, minors-now-opt-in note, CLI divergence
  (still classical=5), coef vs coefficient clarification, and generic Kala note (explicit `aspects=`
  callers unaffected).

- **concepts.md:** added default-now-7 + minors-opt-in note in Harmonic Theory (after the 14-aspect
  support statement); updated Configurable Aspect Sets section to list TRADITIONAL as library default and
  CLASSICAL as opt-in; added `aspects_for_harmonics` compose example. Dual-base rule (lines 70-126)
  NOT duplicated. Aspect Types table glyph+harmonic columns verified correct (already matched core.aspects
  from Plan 01 — no changes needed).

- **api.md:** documented `aspects_for_harmonics(harmonics)` (signature, valid harmonics, raises, 4
  examples); documented new `harmonic` and `symbol` columns on `core.aspects` + coef==coefficient
  conceptual mapping; fixed all 3 stale EXTENDED-default claims (preset table label, `calculate_aspects`
  `None →` description, `compute_chart` `aspects=` parameter default note).

- **fr gettext:** `make gettext` + `make update-po` via module form; api.po +18 new msgids /
  concepts.po +10 new msgids; msgstr stays English-fallback (Phase 25 convention); en + fr builds each
  at 1 warning (Phase 25 baseline maintained). migrate_translations.py NOT run.

- **Full test suite:** 1399 tests pass, 100% coverage (docs edits touch no code paths).

## Task Commits

1. **Task 1: CHANGELOG [1.3.0] + UPGRADING v1.2->v1.3** — `ef33e8d` (docs)
2. **Task 2: Update concepts.md + api.md** — `bc07849` (docs)
3. **Task 3: Regenerate fr gettext catalogs** — `3d560ae` (chore)

**Plan metadata:** (final commit below)

## Files Created/Modified

- `/home/loc/workspace/ketu/CHANGELOG.md` — new `## [1.3.0]` section (Added + BREAKING); version
  constants untouched
- `/home/loc/workspace/ketu/UPGRADING.md` — new `## v1.2 -> v1.3` section prepended; v1.1->v1.2
  unchanged
- `/home/loc/workspace/ketu/docs/source/concepts.md` — Harmonic Theory note + Configurable Aspect Sets
  updated + aspects_for_harmonics compose example; Aspect Types table verified correct
- `/home/loc/workspace/ketu/docs/source/api.md` — aspects_for_harmonics section + harmonic/symbol/coef
  docs + 3 stale-default fixes
- `/home/loc/workspace/ketu/docs/locale/fr/LC_MESSAGES/api.po` — +18 new msgids, msgstr English-fallback
- `/home/loc/workspace/ketu/docs/locale/fr/LC_MESSAGES/concepts.po` — +10 new msgids, msgstr English-fallback

## Three Stale Default Claims Fixed

| Location | Old (stale) | New (correct) |
|---|---|---|
| api.md preset table | `EXTENDED | All 14 aspects (default)` | `EXTENDED | All 14 aspects | Includes full-circle minors (H5/H9/H10)` |
| api.md `calculate_aspects` param | `None → EXTENDED` | `None → TRADITIONAL (7 half-circle, v1.3+ default)` |
| api.md `compute_chart` param | `default: EXTENDED` | `default: TRADITIONAL — the 7 half-circle aspects, v1.3+` |

## Build Status

| Language | Warnings | Status |
|---|---|---|
| en | 1 | Clean (Phase 25 baseline) |
| fr | 1 | Clean (Phase 25 baseline) |

## Decisions Made

- CHANGELOG [1.3.0] kept separate from [Unreleased] (cycles angular_separation entry) — Phase 27
  merges them when bumping the version
- concepts.md Harmonic Theory dual-base rule (lines 70-126) NOT duplicated — only the new default note
  added after the 14-aspect summary statement
- Aspect Types table in concepts.md already had correct glyph + harmonic columns from Plan 01 —
  verified, no changes needed
- changelog.po NOT updated (CHANGELOG.md is not a docs/source/ page; not in the Sphinx gettext scope)
- Package version NOT bumped — Phase 27 owns REL-10

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None.

## Next Phase Readiness

- Phase 26 is COMPLETE (all 3 plans done). Phase 27 (Release 1.3.0) can now proceed:
  - CHANGELOG [1.3.0] ready (Phase 27 merges [Unreleased] + [1.3.0] on bump)
  - UPGRADING v1.2->v1.3 section written
  - All API docs accurate for the v1.3.0 surface
  - fr gettext catalogs up to date

## Self-Check: PASSED

- [x] `CHANGELOG.md` has `## [1.3.0]` section with Added + BREAKING entries — `grep "1.3.0" CHANGELOG.md` found line 34
- [x] `UPGRADING.md` has `## v1.2 -> v1.3` section — `grep "v1.2 -> v1.3" UPGRADING.md` found line 6
- [x] `docs/source/concepts.md` has `aspects_for_harmonics` and "half-circle" notes
- [x] `docs/source/api.md` has `aspects_for_harmonics` section + harmonic/symbol + coef docs
- [x] No stale EXTENDED-default claims in api.md — verified with 3 explicit greps
- [x] `docs/locale/fr/LC_MESSAGES/api.po` and `concepts.po` modified — git status confirmed
- [x] en + fr docs build at 1 warning each — verified with make html + make html-fr
- [x] 1399 tests pass, 100% coverage
- [x] Commit `ef33e8d` (Task 1) exists
- [x] Commit `bc07849` (Task 2) exists
- [x] Commit `3d560ae` (Task 3) exists

---
*Phase: 26-aspects-data-driven*
*Completed: 2026-06-01*
