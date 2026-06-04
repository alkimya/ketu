---
phase: 37-documentation-release-v1-6-0
plan: "02"
subsystem: release-metadata
tags: [version-bump, changelog, upgrading, readme, release-prep]
dependency_graph:
  requires: []
  provides: [version-1.6.0-metadata, changelog-1.6.0, upgrading-v1.5-to-v1.6]
  affects: [pyproject.toml, ketu/__init__.py, docs/source/conf.py, CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md, UPGRADING.md, README.md]
tech_stack:
  added: []
  patterns: [newest-first-changelog, additive-release-notes]
key_files:
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
decisions:
  - "conf.py bumped here (was NOT pre-bumped by Phase 36) — confirmed live before edit"
  - "CHANGELOG.md authored from scratch — Phase 36 did NOT pre-author a [1.6.0] stub"
  - "fr/CHANGELOG.md uses ### Ajouts + ### Notes matching existing v1.5 section style"
  - "UPGRADING ## v1.5 -> v1.6 inserted as first section (newest-first ordering)"
  - "README Roadmap entry added after Dynamic harmonic CLI line; no What's New section"
metrics:
  duration: "~8 min"
  completed: "2026-06-04"
  tasks: 3
  files: 8
---

# Phase 37 Plan 02: Version Bump, Changelog, Upgrading, README Summary

**One-liner:** Version bumped to 1.6.0 in all three source-of-truth files; [1.6.0] changelog authored from scratch (EN root + RTD docs copy + French); UPGRADING v1.5→v1.6 added; README Roadmap updated.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Bump version to 1.6.0 in THREE files (incl. conf.py) | 490885a | pyproject.toml, ketu/__init__.py, docs/source/conf.py |
| 2 | Author the [1.6.0] changelog FROM SCRATCH (root + RTD + French) | 2ca5122 | CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md |
| 3 | Add UPGRADING v1.5→v1.6 section and update README Roadmap | e87bc4e | UPGRADING.md, README.md |

## Verification Results

- `pyproject.toml` line 7: `version = "1.6.0"` — CONFIRMED
- `ketu/__init__.py` line 57: `__version__ = "1.6.0"` — CONFIRMED
- `docs/source/conf.py`: `release = "1.6.0"` + `version = "1.6.0"`, no `1.5.0` remains — CONFIRMED
- `CHANGELOG.md`: exactly one `## [1.6.0] - 2026-06-04` section, no Unreleased — CONFIRMED; `find_declination_aspects`, `ketu.declination`, `CHART_DTYPE` present — CONFIRMED
- `docs/source/changelog.md`: `## [1.6.0] - 2026-06-04` with `### Added 1.6.0` / `### Notes 1.6.0` idiom, byte-identical bullet content — CONFIRMED
- `fr/CHANGELOG.md`: `## [1.6.0] - 2026-06-04` above `[1.5.0]`, `contre-parallèle`, `find_declination_aspects` — CONFIRMED
- `UPGRADING.md`: `## v1.5 -> v1.6` as first section, `ketu.declination`, `CHART_DTYPE is UNCHANGED/byte-identical/no ratchet`, Kala guidance; `## v1.4 -> v1.5` intact — CONFIRMED
- `README.md`: declination aspects + `ketu.declination` in Roadmap; no `What's New in v1.6.0` — CONFIRMED
- Note: `pytest tests/test_version.py` and `pytest tests/ -q` could not be run (bash permission restriction during execution); version string edits are file-verified correct.

## Deviations from Plan

None — plan executed exactly as written. conf.py was confirmed at 1.5.0 before the edit (matching the plan's stated precondition). CHANGELOG.md confirmed no [1.6.0] stub existed before authoring.

## Known Stubs

None. All edits are complete metadata/documentation.

## Threat Flags

None. This plan touches only metadata, changelogs, and documentation files — no new network endpoints, auth paths, or schema changes.

## Self-Check

Checking created/modified files exist and commits are present.
