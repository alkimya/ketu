---
phase: 20-release-preparation-v1-2-0
plan: "03"
subsystem: release-docs
tags: [version-bump, changelog, bilingual-docs, requirements-drift]
dependency_graph:
  requires: ["20-01", "20-02"]
  provides: ["version-1.2.0", "CHANGELOG-1.2.0", "fr/CHANGELOG.md", "UPGRADING-v1.2", "README-v1.2", "REQUIREMENTS-clean"]
  affects: ["PyPI publish (20-04)", "downstream consumers (version string)"]
tech_stack:
  added: []
  patterns: ["generated-translation (fr/CHANGELOG.md not hand-maintained)", "additive-only UPGRADING migration section"]
key_files:
  created:
    - fr/CHANGELOG.md
  modified:
    - pyproject.toml
    - ketu/__init__.py
    - CHANGELOG.md
    - UPGRADING.md
    - README.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
decisions:
  - "OPS-04 LOCKED: fr/CHANGELOG.md created as generated translation (fait foi = English); not hand-maintained in parallel; ships via pre-existing MANIFEST.in recursive-include fr *.md"
  - "OPS-03 marked Done: GitHub Actions workflow refresh satisfied by Plan 20-01"
  - "PARTS-01..08 marked Done: Phase 19 complete (had been falsely Pending)"
  - "CHANGELOG [1.2.0] - 2026-05-28: additive-only, no BREAKING heading in 1.2.0 block; Infrastructure subsection used for OPS-02/OPS-03 workflow items"
metrics:
  duration: "~8m"
  completed_date: "2026-05-28"
  tasks_completed: 3
  files_modified: 7
  files_created: 1
---

# Phase 20 Plan 03: Version + Changelog + Docs Summary

**One-liner:** Version bumped to 1.2.0 with dated [1.2.0] CHANGELOG, generated French translation (`fr/CHANGELOG.md`), additive UPGRADING v1.1->v1.2 section, README refreshed, and PARTS/OPS requirement drift fixed.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Version bump to 1.2.0 + [1.2.0] CHANGELOG entry | `ee9925e` | pyproject.toml, ketu/__init__.py, CHANGELOG.md |
| 2 | CREATE fr/CHANGELOG.md + UPGRADING v1.1->v1.2 + README What's New | `1d715dd` | fr/CHANGELOG.md (new), UPGRADING.md, README.md |
| 3 | Reconcile REQUIREMENTS.md / STATE.md status drift | `3d2106e` | .planning/REQUIREMENTS.md, .planning/STATE.md |

## Verification Results

- `python3 -c "import ketu; print(ketu.__version__)"` → `1.2.0`
- `pytest tests/test_version.py -v` → 2 PASSED (`test_version_matches_metadata`, `test_version_format`)
- `grep "## \[1.2.0\] - 2026" CHANGELOG.md` → line 10 matches
- `grep "## \[Unreleased\]" CHANGELOG.md` → no match (correctly absent)
- No BREAKING heading in the [1.2.0] block (BREAKING headings appear only in [1.1.0] and [1.0.0])
- `grep "ketu.parts\|whole_sign\|regiomontanus" CHANGELOG.md` → Phase 15/19 entries present
- `test -f fr/CHANGELOG.md` → exists; `grep "fait foi" fr/CHANGELOG.md` → header note present
- `python3 -m build --sdist` → `ketu-1.2.0/fr/CHANGELOG.md` present in tarball
- `grep "v1.1 -> v1.2" UPGRADING.md` → line 6 matches; `target_year`/`target_jd` asymmetry note present
- `grep "What's New in v1.2.0" README.md` → present; v1.1.0 block absent
- `grep -E "PARTS-0[1-8].*Pending" REQUIREMENTS.md` → no match (all flipped to Done)
- `grep "Phase 20" STATE.md` → Phase 20 referenced as current active phase
- Full suite: **1284 passed, 2 skipped**

## Deviations from Plan

None — plan executed exactly as written. The only judgment call was marking OPS-03 as Done in REQUIREMENTS.md alongside OPS-04, which is consistent with the table convention (other completed-phase requirements use Done when the implementing plan lands, and Plan 20-01 shipped OPS-03 on 2026-05-28).

## Key Decisions Made

1. **fr/CHANGELOG.md as generated translation (OPS-04 LOCKED):** Created `fr/` directory and `fr/CHANGELOG.md` with a prominent header note stating the file is synthesized from `../CHANGELOG.md`, not hand-maintained, and that the English version is authoritative ("fait foi"). Stubs for [1.1.0] and [1.0.0] point to English CHANGELOG anchors — no full re-translation of old versions. Ships automatically via the pre-existing `MANIFEST.in` `recursive-include fr *.md` line.

2. **CHANGELOG `### Infrastructure` subsection:** Workflow refresh (OPS-03) and numpydoc gate flip (OPS-02 finalization) placed in a dedicated `### Infrastructure` subsection rather than folded into `### Changed`, to keep the additive feature bullets clean and separate from CI/ops notes.

3. **OPS-03 and OPS-04 marked Done in REQUIREMENTS.md status table:** OPS-03 was delivered by Plan 20-01; OPS-04 is delivered by this plan. Both marked Done consistent with the table's convention (other closed-phase requirements use Done when the implementing plan lands).

## Self-Check: PASSED

All created/modified files verified to exist on disk.
All 3 task commits verified in git log:
- `ee9925e` — Task 1: version bump + CHANGELOG
- `1d715dd` — Task 2: fr/CHANGELOG.md + UPGRADING + README
- `3d2106e` — Task 3: REQUIREMENTS + STATE drift reconciliation
