---
phase: 35-release-v1-5-0
plan: 02
subsystem: infra
tags: [pypi, oidc, github-release, smoke-test, release]

# Dependency graph
requires:
  - phase: 35-01
    provides: version 1.5.0 bumped in all 3 source-of-truth files, changelogs dated, UPGRADING updated, clean tree on main
provides:
  - ketu==1.5.0 published to PyPI via OIDC trusted publishing
  - GitHub release v1.5.0 with sdist + wheel attached
  - origin/main pushed (RTD rebuilds v1.5 docs)
  - Post-publish smoke confirming four v1.5 assertions from PyPI
affects: [kala-adapter, rahu-ui, rtd-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BOTH tag AND origin/main pushed: PyPI follows tag, RTD follows main — always both"
    - "virtualenv (not venv) for fresh-venv smoke on systems without python3-venv package"
    - "gh run watch for synchronous publish.yml gate before GitHub release creation"

key-files:
  created: []
  modified: []

key-decisions:
  - "Tag pushed before GitHub release creation — publish.yml OIDC attestation requires the tag to exist on the remote first"
  - "Used python -m virtualenv for fresh-venv smoke (python3-venv/ensurepip not installed on system Python 3.13)"
  - "dist/ artifacts from Task 1 reused directly — no rebuild needed (tree was clean, same HEAD)"

patterns-established:
  - "Release ceremony order: tag -> push tag -> push main -> watch workflow -> gh release create -> smoke from PyPI -> rm dist"

# Metrics
duration: 12min
completed: 2026-06-04
---

# Phase 35 Plan 02: PyPI Publish & Post-Publish Smoke Summary

**ketu==1.5.0 shipped to PyPI via OIDC (publish.yml SUCCESS), GitHub release v1.5.0 with sdist+wheel, origin/main pushed, and all four v1.5 assertions pass from a clean PyPI install.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-04T10:13:00Z
- **Completed:** 2026-06-04T10:25:41Z
- **Tasks:** 1 (Task 2 — tag, push, watch, GH release, smoke)
- **Files modified:** 0 (pure ops: tag, push, watch CI, create release, smoke test, rm dist)

## Accomplishments

- Tag v1.5.0 created on HEAD cf85e90 and pushed; origin/main advanced from 59a293b to cf85e90 (5 commits) — RTD will rebuild docs at v1.5
- publish.yml run 26945916843 completed SUCCESS (build 17s + publish-to-pypi 18s via OIDC trusted publishing)
- GitHub release `Ketu 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI` created at https://github.com/alkimya/ketu/releases/tag/v1.5.0 with both `ketu-1.5.0-py3-none-any.whl` (796 KB) and `ketu-1.5.0.tar.gz` (1.3 MB) attached
- Post-publish fresh-venv smoke from `pip install ketu==1.5.0` passes all six checks

## Task Commits

No new code commits for Task 2 — all work was operational (git ops, CI watch, GH release API, smoke test, artifact cleanup). The task-1 pre-flight commit already recorded the clean HEAD.

**Plan metadata commit:** created below (docs(35-02): complete pypi-publish-smoke-test plan)

## Files Created/Modified

None — Task 2 was a pure release operations task. No source or documentation files were modified.

## Post-Publish Smoke Results (FROM PyPI)

All six assertions PASS against the published `ketu==1.5.0` wheel:

| Check | Result |
|-------|--------|
| version: `ketu.__version__ == metadata == "1.5.0"` | PASS |
| subpackages import (all 11 subpackages incl. v1.5 quartet) | PASS |
| `declination(2451545.0, 1)` finite float in [-90, 90] | PASS — `-10.7460` |
| `is_ascending_declination(2451545.0, 1)` bool | PASS — `False` |
| `is_out_of_bounds(2451545.0, 1)` bool | PASS — `False` |
| `--harmonics h7 aspects --date 2024-01-01` emits `H7-1` | PASS — `H7-1 51°` confirmed |
| `find_spec('swisseph') is None` | PASS — no pyswisseph at runtime |

## Decisions Made

- dist/ artifacts reused from Task 1 (still present in dist/, tree clean) — no rebuild needed.
- Used `python -m virtualenv` (available in project venv) instead of `python -m venv` because `python3-venv`/`ensurepip` is not installed for system Python 3.13 on this Debian host. Outcome identical.
- GitHub release created AFTER publish.yml SUCCESS (not before) — ensures PyPI attestations are complete and the release notes reference an already-live PyPI package.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used virtualenv instead of venv for fresh-venv smoke**
- **Found during:** Task 2 (post-publish smoke)
- **Issue:** `python3 -m venv` failed with "ensurepip not available" on the system Python 3.13 — `python3-venv` package not installed on this Debian host. The fresh-venv smoke could not be created via `venv`.
- **Fix:** Used `python -m virtualenv` from the project venv (virtualenv 21.4.2, already installed as a dev dependency). Creates an equivalent isolated environment. Outcome: `pip install ketu==1.5.0` from PyPI, no local source on `sys.path`, identical isolation guarantee.
- **Files modified:** none
- **Verification:** All six smoke assertions passed with clean imports from the PyPI artifact.
- **Committed in:** n/a (operational fix, no code change)

---

**Total deviations:** 1 auto-fixed (1 blocking — environment workaround)
**Impact on plan:** Zero impact on correctness. The smoke test isolation is equivalent; PyPI artifact verified clean.

## Issues Encountered

- System Python 3.13 lacks `python3-venv` (ensurepip), so `python -m venv` fails on this Debian host. Resolved automatically with `python -m virtualenv` from the project venv. Not a blocker.

## User Setup Required

None — PyPI OIDC trusted publisher was already configured from Phase 20. No new external service configuration required.

## Next Phase Readiness

**Milestone v1.5 complete.** REL-01 + REL-02 + REL-03 all satisfied:

- REL-01: version bumped in pyproject.toml + ketu/__init__.py + docs/source/conf.py (Plan 35-01)
- REL-02: changelogs dated, fr/CHANGELOG authored, UPGRADING v1.4->v1.5 added, README updated (Plan 35-01)
- REL-03: ketu==1.5.0 live on PyPI, origin/main pushed (RTD follows main), GitHub release v1.5.0 with sdist+wheel, post-publish smoke green (Plan 35-02)

Next: `/gsd:complete-milestone` to archive the v1.5 milestone and start the v1.6 roadmap.

---
*Phase: 35-release-v1-5-0*
*Completed: 2026-06-04*
