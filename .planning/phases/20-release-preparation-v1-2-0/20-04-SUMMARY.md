---
phase: 20-release-preparation-v1-2-0
plan: "04"
subsystem: infra
tags: [pypi, oidc, trusted-publishing, github-actions, release, changelog]

requires:
  - phase: 20-release-preparation-v1-2-0-plan-01
    provides: GitHub Actions upgraded to Node.js 24 (OPS-03)
  - phase: 20-release-preparation-v1-2-0-plan-02
    provides: numpydoc gate flipped to blocking (OPS-02 finalisation)
  - phase: 20-release-preparation-v1-2-0-plan-03
    provides: version 1.2.0 synced, CHANGELOG dated, fr/CHANGELOG.md created, UPGRADING.md updated

provides:
  - ketu==1.2.0 live on PyPI via OIDC trusted publishing (OPS-05)
  - GitHub release v1.2.0 with sdist + wheel attached
  - Fresh-venv smoke-import from PyPI verified for all 5 new subpackages
  - v1.2.0 annotated tag on main

affects: [kala-downstream, any pip install ketu users]

tech-stack:
  added: []
  patterns:
    - "Tag-triggered OIDC trusted publishing: annotated tag push -> publish.yml (build job -> publish-to-pypi job via id-token: write)"
    - "Pre-flight + human go/no-go gate before any irreversible PyPI push"
    - "Fresh-venv PyPI CDN propagation retry: verify immediately, PyPI JSON API shows version in under 30s post-workflow"

key-files:
  created: []
  modified:
    - dist/ (cleaned after release)

key-decisions:
  - "Tag v1.2.0 pushed on commit 4631546 (pre-flighted in Task 1 / prior session)"
  - "GitHub release created with locally-built sdist + wheel (not workflow artifacts) per plan spec OPS-05"
  - "PyPI CDN propagation confirmed <30s after workflow SUCCESS — no retry needed"

patterns-established:
  - "Release ceremony pattern: pre-flight -> human gate -> annotated tag push -> gh run watch -> gh release create with assets -> fresh-venv pip install smoke"

duration: ~10min (continuation; Task 1 pre-flighted separately)
completed: "2026-05-28"
---

# Phase 20 Plan 04: Release Publish Summary

**ketu==1.2.0 shipped to PyPI via OIDC trusted publishing in 33s (build 16s + publish 17s); GitHub release v1.2.0 created with sdist + wheel; fresh-venv smoke-import from PyPI passes all 5 new subpackages**

## Performance

- **Duration:** ~10 min (continuation after Task 1 pre-flight committed in prior session as 4631546)
- **Started:** 2026-05-28T21:10:00Z (continuation)
- **Completed:** 2026-05-28T21:20:08Z
- **Tasks:** 2 (Task 1 pre-committed; Task 2 executed in this session)
- **Files modified:** 0 (release ceremony — no source changes; dist/ created then cleaned)

## Accomplishments

- Annotated tag v1.2.0 created on commit 4631546 and pushed to origin
- `publish.yml` workflow (run 26602811661) completed SUCCESS in 33s: build job (16s) + publish-to-pypi job (17s) via OIDC trusted publishing — no token, no manual upload
- GitHub release v1.2.0 created at https://github.com/alkimya/ketu/releases/tag/v1.2.0 with both sdist (`ketu-1.2.0.tar.gz`) and wheel (`ketu-1.2.0-py3-none-any.whl`) attached
- Fresh-venv `pip install ketu==1.2.0` from PyPI smoke-imports cleanly: `ketu.__version__ == importlib.metadata.version("ketu") == "1.2.0"` and all 5 new subpackages import (`ketu.synastry`, `ketu.composite`, `ketu.returns`, `ketu.parts`, `ketu.houses` whole_sign system)

## Task Commits

1. **Task 1: Date-stamp release + full local pre-flight (all 11 gates PASS)** — `4631546` (pre-committed, continuation)
2. **Task 2: Tag v1.2.0, push, watch publish.yml, create GitHub release, verify PyPI** — no source commit (release ceremony: tag push + gh CLI operations only)

**Plan metadata commit:** (see final commit below)

## Files Created/Modified

- `dist/ketu-1.2.0-py3-none-any.whl` — created by Task 1 pre-flight; used for GitHub release attachment; cleaned after
- `dist/ketu-1.2.0.tar.gz` — created by Task 1 pre-flight; used for GitHub release attachment; cleaned after
- `git tag v1.2.0` — annotated tag on commit 4631546

## Decisions Made

- GitHub release body uses an additive narrative (no breaking-change language, migration section confirms all v1.1 code works unchanged) — consistent with v1.2 non-breaking minor framing
- Locally-built artifacts attached to GitHub release (not workflow artifacts) per plan spec — provides immediate human verification of the shipped binaries

## Deviations from Plan

None — plan executed exactly as written. PyPI CDN propagation was instantaneous (<30s), so no retry loop was needed.

## Issues Encountered

None. The publish.yml workflow succeeded on the first run. The PyPI JSON API reflected 1.2.0 within 30 seconds of workflow completion (confirmed before creating the GitHub release). The Node.js 20 deprecation annotation on `actions/upload-artifact@v5` in the workflow output is a harmless GitHub-side notice — the action itself ran successfully (OPS-03 bumped artifacts to @v5 which uses Node 24; the annotation is a GitHub runner banner, not a failure).

## User Setup Required

None — no external service configuration required. The PyPI OIDC trusted publisher was already configured from prior releases (Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi).

## Next Phase Readiness

Phase 20 is complete. Milestone v1.2 is DONE.

- ketu==1.2.0 is live on PyPI: `pip install ketu==1.2.0`
- GitHub release: https://github.com/alkimya/ketu/releases/tag/v1.2.0
- PyPI package page: https://pypi.org/project/ketu/1.2.0/
- 1284 tests pass (2 skipped). Coverage ≥90% project-wide. numpydoc gate blocking. All 5 new subpackages (synastry, composite, returns, parts, houses extension) smoke-import cleanly from the published artifact.
- No blockers for v1.3 planning.

---
*Phase: 20-release-preparation-v1-2-0*
*Completed: 2026-05-28*
