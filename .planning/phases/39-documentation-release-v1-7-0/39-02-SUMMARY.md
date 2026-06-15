---
phase: 39-documentation-release-v1-7-0
plan: "02"
subsystem: release-metadata
tags: [version-bump, changelog, upgrading, readme, release-prep, v1.7.0]
dependency_graph:
  requires:
    - phase: 38-fictitious-point-orbs-engine
      provides: "Rahu/Ketu/Lilith orb 0→2° + tautological Opposition filter facts"
    - phase: 39-01
      provides: "ORB-04 EN+FR docs updated (orb table, Sphinx, README bodies section)"
  provides:
    - "pyproject.toml: version = 1.7.0"
    - "ketu/__init__.py: __version__ = 1.7.0"
    - "docs/source/conf.py: release = version = 1.7.0"
    - "CHANGELOG.md: [1.7.0] - 2026-06-15 entry (Changed + Notes), newest-first"
    - "docs/source/changelog.md: RTD copy of [1.7.0] entry, content-identical"
    - "fr/CHANGELOG.md: French [1.7.0] section above [1.6.0]"
    - "UPGRADING.md: ## v1.6 -> v1.7 section at top with ### Kala guidance"
    - "README.md: fictitious-point orbs roadmap item added (checked)"
  affects:
    - "39-03-PLAN.md (release ceremony) — consumes these version artifacts"
tech_stack:
  added: []
  patterns:
    - "Newest-first ordering enforced in CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md, UPGRADING.md"
    - "RTD heading convention: ### Changed 1.7.0 / ### Notes 1.7.0 (suffixed, no MD024 collision)"
    - "Three version source-of-truth files bumped in lockstep (pyproject.toml / ketu/__init__.py / docs/source/conf.py)"
key_files:
  created: []
  modified:
    - "pyproject.toml (version 1.6.0 → 1.7.0)"
    - "ketu/__init__.py (__version__ 1.6.0 → 1.7.0)"
    - "docs/source/conf.py (release + version 1.6.0 → 1.7.0)"
    - "CHANGELOG.md ([1.7.0] - 2026-06-15 section inserted above [1.6.0])"
    - "docs/source/changelog.md ([1.7.0] RTD copy inserted above [1.6.0])"
    - "fr/CHANGELOG.md ([1.7.0] French section inserted above [1.6.0])"
    - "UPGRADING.md (## v1.6 -> v1.7 section inserted at top)"
    - "README.md (fictitious-point orbs roadmap item added)"
decisions:
  - "RTD changelog uses suffixed headings (### Changed 1.7.0) to match existing v1.6.0 convention and avoid MD024 duplicate-heading lint errors"
  - "UPGRADING Kala guidance makes explicit that pip install -U 1.7.0 is NOT neutral — node/Lilith oracle re-pinning required"
  - "README roadmap entry uses [x] checked item (v1.7 shipped); no version badge updated (badge auto-updates from PyPI)"
metrics:
  duration: "~20 minutes"
  completed: "2026-06-15"
  tasks_completed: 3
  files_changed: 8
---

# Phase 39 Plan 02: Version Bump + Changelog + UPGRADING Summary

**One-liner:** Version bumped to 1.7.0 across all three source-of-truth files; dated [1.7.0] changelog entries authored in EN root, RTD copy, and French; UPGRADING v1.6 -> v1.7 section with explicit Kala guidance (results change, not a neutral upgrade).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Bump version to 1.7.0 in all three source-of-truth files | 67405e0 | pyproject.toml, ketu/__init__.py, docs/source/conf.py |
| 2 | Author [1.7.0] CHANGELOG (EN root + RTD copy) and French CHANGELOG | 44e3a35 | CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md |
| 3 | Add UPGRADING v1.6 -> v1.7 section + README roadmap touch-up | 978d185 | UPGRADING.md, README.md |

## What Was Built

### Task 1: Version 1.7.0 across source-of-truth files

Three files bumped from 1.6.0 to 1.7.0:

- `pyproject.toml` line 7: `version = "1.7.0"` (PyPI ingests this)
- `ketu/__init__.py` line 57: `__version__ = "1.7.0"` (runtime import)
- `docs/source/conf.py` lines 14-15: `release = "1.7.0"`, `version = "1.7.0"` (Sphinx/RTD)

Verified: `python -c "import ketu; print(ketu.__version__)"` → `1.7.0`

### Task 2: Dated [1.7.0] changelog entries

**CHANGELOG.md** (root, Keep-a-Changelog format): new `## [1.7.0] - 2026-06-15` section inserted above `## [1.6.0]` with:
- `### Changed`: Rahu/Ketu/Lilith orb 0→2° (single-source, all consumers inherit); tautological Rahu-Ketu Opposition now suppressed
- `### Notes`: BREAKING RESULTS callout — MINOR release because aspect results change; downstream (Kala) must treat upgrade as deliberate

**docs/source/changelog.md** (RTD copy): content-identical, using RTD heading convention `### Changed 1.7.0` / `### Notes 1.7.0` (suffixed to avoid Sphinx header collision).

**fr/CHANGELOG.md** (French): `## [1.7.0] - 2026-06-15` section with:
- `### Modifications`: orbe de longitude Rahu/Ketu/Lilith 0° → 2°; opposition tautologique Rahu-Ketu supprimée
- `### Notes`: rupture de résultats — version mineure et non un correctif; Kala doit traiter la mise à jour comme délibérée

### Task 3: UPGRADING.md migration guide + README

**UPGRADING.md**: `## v1.6 -> v1.7` section inserted at the top (newest-first), covering:
- Rahu/Ketu/Lilith orb 0→2° — single-source, all consumer paths inherit
- Tautological Rahu-Ketu Opposition suppressed — explains why (always 180° by definition)
- CHART_DTYPE and core.aspects byte-identical — no dtype ratchet break
- `### Kala guidance` subsection: `pip install -U ketu` to 1.7.0 is NOT neutral; lists concrete items to re-pin (CLI fixture gained Sun-Rahu Quincunx + Venus-Rahu Trine; synastry self-pair orb-limit oracles changed 0.0→1.0)

**README.md**: Added `[x] Fictitious-point longitude orbs — Rahu/Ketu/Lilith orb 0° → 2°; tautological Rahu-Ketu Opposition suppressed` to the Roadmap section.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All version strings, changelog entries, and migration notes are fully authored.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan is pure text/metadata edits.

## Self-Check: PASSED

Files exist:
- pyproject.toml: version = "1.7.0" FOUND
- ketu/__init__.py: __version__ = "1.7.0" FOUND
- docs/source/conf.py: release/version = "1.7.0" FOUND
- CHANGELOG.md: [1.7.0] - 2026-06-15 FOUND (above [1.6.0])
- docs/source/changelog.md: [1.7.0] FOUND
- fr/CHANGELOG.md: [1.7.0] FOUND
- UPGRADING.md: ## v1.6 -> v1.7 + Kala guidance FOUND
- README.md: Fictitious-point roadmap item FOUND

Commits:
- 67405e0 FOUND (chore(39-02): bump version)
- 44e3a35 FOUND (docs(39-02): author [1.7.0] changelog)
- 978d185 FOUND (docs(39-02): add UPGRADING v1.6 -> v1.7)
