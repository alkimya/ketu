---
phase: 35-release-v1-5-0
plan: "01"
subsystem: release
tags: [version-bump, changelog, upgrading, readme, docs]

requires:
  - phase: 34-harmonics-debt
    provides: Harmonics debt (ASP-F1/F2/F3) fully implemented and tested
  - phase: 33-lunar-declination
    provides: Declination delta surface (DECL-01..09) fully implemented and tested

provides:
  - "Version 1.5.0 in all three source-of-truth files (pyproject.toml, ketu/__init__.py, docs/source/conf.py)"
  - "Date-stamped [1.5.0] English changelogs (root CHANGELOG.md + docs/source/changelog.md)"
  - "New French [1.5.0] section in fr/CHANGELOG.md (6 Added + 2 Changed + 2 Fixed + 2 Notes)"
  - "UPGRADING.md v1.4 -> v1.5 section (body_decl dtype, node-speed correction, additive API)"
  - "README Roadmap checklist updated with two v1.5 entries"

affects:
  - "35-02-quality-gates (next plan)"
  - "35-03-pypi-publish (final plan)"
  - ReadTheDocs (conf.py bump ensures RTD shows 1.5.0, not stale 1.4.0)
  - Kala (body_decl and node-speed migration notes in UPGRADING.md)

tech-stack:
  added: []
  patterns:
    - "THREE source-of-truth version files must be bumped: pyproject.toml + ketu/__init__.py + docs/source/conf.py (unlike Phase 32 where conf.py was pre-bumped)"
    - "Changelog date-stamping: replace Unreleased with UTC date, leave content byte-identical"
    - "fr/CHANGELOG.md follows identical heading idiom to EN: Ajouts / Modifie / Corrige / Notes"

key-files:
  created: []
  modified:
    - pyproject.toml
    - ketu/__init__.py
    - docs/source/conf.py
    - CHANGELOG.md
    - docs/source/changelog.md
    - fr/CHANGELOG.md
    - UPGRADING.md
    - README.md

key-decisions:
  - "conf.py MUST be bumped here (was NOT pre-bumped by Phases 33/34, unlike Phase 32's pattern)"
  - "Changelog content left byte-identical — only the Unreleased header date replaced with 2026-06-04"
  - "fr/CHANGELOG.md MD024 duplicate-heading warning is pre-existing changelog style, not enforced in CI"
  - "No What's New section added to README (no v1.4 equivalent exists — adding one would create inconsistency)"

patterns-established:
  - "v1.5 additive release: no breaking changes, only body_decl (additive dtype) and node-speed fix"

duration: 4min
completed: 2026-06-04
---

# Phase 35 Plan 01: Version Bump, Changelog, Upgrading Summary

**v1.5.0 version metadata synced across all three source-of-truth files, changelogs date-stamped (content untouched), French [1.5.0] section authored, UPGRADING v1.4->v1.5 written, README Roadmap updated — no ketu/ calculation logic changed**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-06-04T10:11:18Z
- **Completed:** 2026-06-04T10:14:58Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Bumped version to 1.5.0 in all THREE source-of-truth files (pyproject.toml, ketu/__init__.py, docs/source/conf.py) — the conf.py bump is the critical step ensuring RTD renders 1.5.0, not stale 1.4.0
- Date-stamped both [1.5.0] changelog stubs (root + docs RTD) by replacing `Unreleased` with `2026-06-04`; pre-authored content left byte-identical
- Authored the French [1.5.0] section in fr/CHANGELOG.md (6 Added + 2 Changed + 2 Fixed + 2 Notes bullets, above [1.4.0])
- Added UPGRADING.md `## v1.4 -> v1.5` as the new first section covering body_decl additive dtype, node-speed correction, and additive API surface
- Updated README Roadmap checklist with two v1.5 entries (declination helpers + dynamic harmonic CLI)
- Full suite green: 1626 passed, 2 skipped, 100% coverage

## Task Commits

1. **Task 1: Bump version to 1.5.0 in THREE files** - `f917271` (chore)
2. **Task 2: Date-stamp changelogs and author French section** - `634a176` (docs)
3. **Task 3: Add UPGRADING v1.4->v1.5 and update README Roadmap** - `3295af0` (docs)

## Files Created/Modified

- `pyproject.toml` — version 1.4.0 -> 1.5.0 (line 7)
- `ketu/__init__.py` — __version__ 1.4.0 -> 1.5.0 (line 57)
- `docs/source/conf.py` — release + version 1.4.0 -> 1.5.0 (lines 14-15)
- `CHANGELOG.md` — [1.5.0] header: Unreleased -> 2026-06-04 (content untouched)
- `docs/source/changelog.md` — [1.5.0] header: Unreleased -> 2026-06-04 (content untouched)
- `fr/CHANGELOG.md` — new [1.5.0] dated French section (71 lines) inserted above [1.4.0]
- `UPGRADING.md` — new `## v1.4 -> v1.5` first section (3 sub-sections, ~90 lines)
- `README.md` — 2 Roadmap checklist entries added after data-driven aspect engine entry

## Decisions Made

- conf.py was NOT pre-bumped by Phases 33/34 (unlike Phase 32 pattern): must be bumped here to avoid RTD showing stale 1.4.0
- Changelog content left byte-identical — only the Unreleased header date token replaced with 2026-06-04
- fr/CHANGELOG.md MD024 duplicate-heading linter warning is pre-existing changelog style (### Ajouts already appeared 4 times before this edit); not enforced in CI, no config exists
- No `## What's New in v1.5.0` section added to README (no v1.4 equivalent — adding one would create an inconsistency per plan spec)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All verifications passed on first attempt. The MD024 markdownlint warning observed after fr/CHANGELOG.md edit is pre-existing style from the file's prior sections and not enforced by any CI gate.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Version 1.5.0 is correctly stamped in all three source-of-truth files
- Changelogs are dated and content-complete
- UPGRADING.md migration notes are complete for downstream (Kala)
- Ready for Plan 35-02 (quality gates: mypy --strict + full suite final confirmation)
- mypy --strict is already clean (confirmed in STATE.md — no fix task needed, unlike Phase 32)

---
*Phase: 35-release-v1-5-0*
*Completed: 2026-06-04*
