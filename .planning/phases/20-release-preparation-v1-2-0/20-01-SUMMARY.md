---
phase: 20-release-preparation-v1-2-0
plan: 01
subsystem: infra
tags: [github-actions, ci, node24, workflow, yaml]

# Dependency graph
requires: []
provides:
  - Node-24 action pins in tests.yml (checkout@v5, setup-python@v6, codecov-action@v5)
  - Node-24 action pins in publish.yml (checkout@v5, setup-python@v6, upload-artifact@v5, download-artifact@v5)
  - Matched upload/download-artifact@v5 pair in publish.yml
affects: [release, ci, publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Floating major-tag pins (@v5, @v6) — no SHA or minor/patch pinning"
    - "upload-artifact and download-artifact bumped as matched pair (v5 format incompatible with v4 reader)"

key-files:
  created: []
  modified:
    - .github/workflows/tests.yml
    - .github/workflows/publish.yml

key-decisions:
  - "codecov/codecov-action bumped to @v5 (Node-24 runtime, CODECOV_TOKEN wiring unchanged)"
  - "upload-artifact@v5 + download-artifact@v5 bumped as matched pair — v5 artifact format is incompatible with v4 download"
  - "pypa/gh-action-pypi-publish@release/v1 unchanged — floating release branch ref, no Node-20 concern"

patterns-established:
  - "Major-tag floating refs consistent across both workflow files"

# Metrics
duration: 1min
completed: 2026-05-28
---

# Phase 20 Plan 01: Action Version Bump Summary

**GitHub Actions upgraded to Node-24 runtime across tests.yml and publish.yml — zero Node-20 deprecation warnings on CI (OPS-03 satisfied)**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-05-28T20:19:22Z
- **Completed:** 2026-05-28T20:20:45Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- tests.yml: `actions/checkout@v4` -> `@v5`, `actions/setup-python@v5` -> `@v6`, `codecov/codecov-action@v4` -> `@v5`
- publish.yml: `actions/checkout@v4` -> `@v5`, `actions/setup-python@v5` -> `@v6`, matched pair `upload-artifact@v4` -> `@v5` + `download-artifact@v4` -> `@v5`
- YAML validity confirmed for both files; `pypa/gh-action-pypi-publish@release/v1` preserved unchanged
- Zero `@v4` major-version references remain across both workflow files

## Task Commits

Each task was committed atomically:

1. **Task 1: Bump actions in tests.yml to Node-24 majors** - `3d6e7da` (chore)
2. **Task 2: Bump actions in publish.yml to Node-24 majors (matched artifact pair)** - `bb63b8d` (chore)

## Files Created/Modified

- `.github/workflows/tests.yml` - checkout@v5, setup-python@v6, codecov-action@v5
- `.github/workflows/publish.yml` - checkout@v5, setup-python@v6, upload-artifact@v5, download-artifact@v5 (matched pair)

## Decisions Made

- `codecov/codecov-action` bumped from @v4 to @v5: v4 runs on Node-20 (triggers deprecation warning); v5 runs on Node-24. CODECOV_TOKEN env var wiring is identical in both versions.
- `upload-artifact` and `download-artifact` bumped together as a matched pair: the v5 artifact format is incompatible with the v4 download reader. A mixed upload@v5 + download@v4 configuration would fail the publish job silently at the download step.
- `pypa/gh-action-pypi-publish@release/v1` left unchanged: this is a floating release branch reference (not a major-version integer tag), and it has no Node-20 runtime concern.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- OPS-03 (Node-20 deprecation warnings) satisfied
- Plans 20-02 and 20-03 can proceed independently
- Both workflow files are YAML-valid and ready for CI

---
*Phase: 20-release-preparation-v1-2-0*
*Completed: 2026-05-28*
