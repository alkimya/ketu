---
phase: 31-documentation-en-fr
plan: "06"
subsystem: docs
tags: [changelog, sphinx, conf.py, version-bump, v1.4, harmonics, chiron]

# Dependency graph
requires:
  - phase: 28-dynamic-harmonic-generator
    provides: generate_harmonic_aspects(h) public API
  - phase: 29-chiron-orb-4
    provides: Chiron orb 4 deg (Pluto parity)
  - phase: 30-chiron-range-1900-2100
    provides: .npz 2283 segs 1900-2100 max 0.001214 deg
provides:
  - "[1.4.0] changelog section in docs/source/changelog.md"
  - "Annotated v1.1 EXTENDED-default entry (historical accuracy preserved)"
  - "conf.py docs-build version/release bumped to 1.4.0"
affects: [32-release-v1-4-0]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Docs-build version (conf.py) bumped in documentation phase; package version (pyproject.toml + ketu/__init__.py) deferred to Release phase"

key-files:
  created: []
  modified:
    - docs/source/changelog.md
    - docs/source/conf.py

key-decisions:
  - "conf.py version/release bumped to 1.4.0 here (docs-build metadata); pyproject.toml + ketu/__init__.py stay at 1.3.0 until Phase 32"
  - "v1.1 EXTENDED entry annotated inline ('default at v1.1, changed to TRADITIONAL in v1.3') — history preserved, no rewrite"
  - "v1.3 Chiron entries (1142 segs / 1950-2050 / 0.005695 deg) left as-is — accurate for that release; v1.4 range expansion documented only in [1.4.0] section"

patterns-established:
  - "Changelog date placeholder style: '2026-06-XX' — final date set in Phase 32"

# Metrics
duration: 2min
completed: "2026-06-03"
---

# Phase 31 Plan 06: Changelog + Docs-Build Version Summary

**[1.4.0] changelog section documents dynamic-harmonic generator, Chiron 1900-2100 range, Chiron orb 4 deg, and clamping; conf.py docs-build version bumped to 1.4.0 with pyproject.toml/ketu/__init__.py untouched**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-06-03T14:27:39Z
- **Completed:** 2026-06-03T14:29:49Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `## [1.4.0] - 2026-06-XX` section above `[1.3.0]` in `docs/source/changelog.md`, listing Added (generate_harmonic_aspects dynamic generator, Chiron 1900-2100) and Changed (Chiron orb 0->4 deg, clamping behaviour, doc recentring on 180-division default)
- Annotated the v1.1 `EXTENDED (14 — default)` entry to read "default at v1.1, changed to TRADITIONAL in v1.3" — historical accuracy preserved without rewriting
- Bumped `docs/source/conf.py` `version` and `release` to `"1.4.0"` (docs-build metadata only); `pyproject.toml` and `ketu/__init__.py` remain at 1.3.0 (Phase 32 responsibility)

## Task Commits

1. **Task 1: Add the [1.4.0] changelog section** - `9f8cfee` (feat)
2. **Task 2: Annotate v1.1 EXTENDED-default + bump conf.py to 1.4.0** - `46d7f5a` (feat)

## Files Created/Modified

- `docs/source/changelog.md` — new [1.4.0] section (13 lines inserted) + v1.1 EXTENDED entry annotated
- `docs/source/conf.py` — `release` and `version` changed from `"1.3.0"` to `"1.4.0"` (lines 14-15 only)

## Decisions Made

- Bumped conf.py docs-build version here (documentation phase), not in Phase 32 — the RTD theme displays version prominently and leaving it at 1.3.0 during the documentation phase would be visible drift. Package version (`pyproject.toml` + `ketu/__init__.py`) deferred to Phase 32 (Release).
- Used inline annotation for v1.1 entry rather than footnote or separate section — keeps history readable in-place, no rewriting of facts.
- Date placeholder `2026-06-XX` matches existing changelog style; exact date filled at Phase 32 release time.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Grep Verification Results

```
grep -n "[1.4.0]" docs/source/changelog.md
  8:## [1.4.0] - 2026-06-XX

grep -n "generate_harmonic_aspects" docs/source/changelog.md
  12:- **generate_harmonic_aspects(h) — dynamic harmonic generator**: ...

grep -ni "EXTENDED.*default" docs/source/changelog.md
  54:- CLASSICAL (5), TRADITIONAL (7), EXTENDED (14 — default at v1.1, changed to TRADITIONAL in v1.3). ...

grep -n "1.4.0" docs/source/conf.py
  14:release = "1.4.0"
  15:version = "1.4.0"

grep -n "1.3.0" docs/source/conf.py
  (no output — 0 hits)

grep -ni "kala" docs/source/changelog.md
  (no output — 0 hits)

git status pyproject.toml ketu/__init__.py
  (no output — both files unchanged)
```

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DOC-16 changelog part satisfied: [1.4.0] section complete with all v1.4 feature entries
- DOC-15 changelog part satisfied: v1.1 EXTENDED-default annotation in place
- conf.py docs-build version is 1.4.0 — Sphinx builds will display correct version
- Phase 32 (Release) can proceed: bump pyproject.toml + ketu/__init__.py to 1.4.0, add root CHANGELOG.md [1.4.0] entry, PyPI publish

---
*Phase: 31-documentation-en-fr*
*Completed: 2026-06-03*
