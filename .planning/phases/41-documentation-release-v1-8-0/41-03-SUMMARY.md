---
phase: 41-documentation-release-v1-8-0
plan: 03
subsystem: release
tags: [pypi, oidc, version-bump, smoke-test, release]

# Dependency graph
requires:
  - phase: 41-01
    provides: EN docs + name-clean sweep across changelogs, UPGRADING, docstrings, concepts.md, api.md
  - phase: 41-02
    provides: FR translations + recompiled .mo + clean EN/FR Sphinx builds at 1-warning baseline
provides:
  - ketu==1.8.0 live on PyPI (OIDC OIDC trusted publishing, run 27820463468)
  - annotated tag v1.8.0 at commit 0c20d4c on origin
  - origin/main pushed (RTD follows main)
  - post-publish fresh-venv smoke green (SMOKE_OK, D-08)
affects: [Rahu UI project — can now pip install ketu==1.8.0 and read body_decl_speed from CHART_DTYPE]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OIDC trusted publishing via push-main + push-tag (established since v1.4, unchanged)"
    - "post-publish fresh-venv smoke confirms pure-NumPy runtime contract"

key-files:
  created:
    - .planning/phases/41-documentation-release-v1-8-0/smoke_v18.py
  modified:
    - pyproject.toml (version 1.7.0 -> 1.8.0, committed 0c20d4c — Task 1, prior invocation)
    - ketu/__init__.py (__version__ 1.7.0 -> 1.8.0, committed 0c20d4c — Task 1, prior invocation)
    - docs/source/conf.py (release + version 1.7.0 -> 1.8.0, committed 0c20d4c — Task 1, prior invocation)

key-decisions:
  - "Push BOTH main and the tag: RTD follows origin/main, PyPI follows the tag (established prior-release pattern)"
  - "virtualenv from project venv used instead of python3 -m venv (python3-venv package not installed on Debian)"
  - "smoke_v18.py uses np.dtype(CHART_DTYPE).names not iteration over CHART_DTYPE directly (VoidDType not iterable in NumPy 2.x)"

patterns-established:
  - "Post-publish D-08 smoke: (a) dtype field present, (b) populated/finite/non-zero, (c) constant importable, (d) pyswisseph absent"

requirements-completed: [REL-01]

# Metrics
duration: 7min
completed: 2026-06-19
---

# Phase 41 Plan 03: Release v1.8.0 Summary

**ketu==1.8.0 shipped to PyPI via OIDC (run 27820463468); body_decl_speed, DECL_STANDSTILL_EPS, and is_ascending_declination_chart confirmed live in a fresh-venv post-publish smoke.**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-19T10:28:00Z
- **Completed:** 2026-06-19T10:34:44Z
- **Tasks:** 3/3 complete (Task 1 + gate Task 2 were completed in the prior invocation; Task 3 executed here)
- **Files modified:** 4 (pyproject.toml, ketu/__init__.py, docs/source/conf.py via prior commit; smoke_v18.py created here)

## Accomplishments

- Pushed origin/main (50 commits — the entire v1.8 milestone, previously unpushed)
- Created annotated tag v1.8.0 at HEAD (0c20d4c) and pushed it — triggering publish.yml OIDC build
- publish.yml run 27820463468 succeeded in ~33 s (build 16 s + publish 17 s); ketu==1.8.0 live on PyPI
- Wrote and ran post-publish smoke (D-08): all 4 assertions green in a fresh venv pip-installed FROM PyPI

## Task Commits

Each task committed atomically:

1. **Task 1: Version bump 1.8.0** - `0c20d4c` (chore) — prior invocation
2. **Task 2: Human go/no-go gate** — no commit (review-only checkpoint); user approved
3. **Task 3: Release + smoke** - `e5de840` (chore: smoke_v18.py)

**git push:** origin/main at 0c20d4c; tag v1.8.0 at 0c20d4c

## Files Created/Modified

- `pyproject.toml` — version = "1.8.0" (line 7)
- `ketu/__init__.py` — `__version__ = "1.8.0"` (line 57)
- `docs/source/conf.py` — release + version = "1.8.0" (lines 14-15)
- `.planning/phases/41-documentation-release-v1-8-0/smoke_v18.py` — D-08 post-publish smoke assertions

## Release Artefacts

| Artefact | Value |
|----------|-------|
| PyPI URL | https://pypi.org/project/ketu/1.8.0/ |
| GitHub Actions run | https://github.com/alkimya/ketu/actions/runs/27820463468 |
| Tag | v1.8.0 at 0c20d4c |
| Wheel | ketu-1.8.0-py3-none-any.whl |

## Smoke Results (D-08)

```
(a) body_decl_speed in CHART_DTYPE.names — OK
(b) body_decl_speed populated — shape (14,), finite, not all-zero — OK
(c) DECL_STANDSTILL_EPS = 0.001 — OK
(d) import swisseph raises ImportError — runtime stays pure NumPy — OK

SMOKE_OK
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] smoke_v18.py: CHART_DTYPE not iterable in NumPy 2.x**
- **Found during:** Task 3 — first smoke run
- **Issue:** `[f[0] for f in CHART_DTYPE]` raises `TypeError: 'numpy.dtypes.VoidDType' object is not iterable` in NumPy 2.4.6 (the version pip-installed with ketu==1.8.0 in the smoke venv). In NumPy 2.x, a dtype object is no longer directly iterable.
- **Fix:** Changed to `np.dtype(CHART_DTYPE).names` — the correct, version-stable API for reading dtype field names.
- **Files modified:** `.planning/phases/41-documentation-release-v1-8-0/smoke_v18.py`
- **Commit:** `e5de840` (same commit, fixed before staging)

**2. [Rule 3 - Blocking] python3 -m venv unavailable (python3-venv not installed)**
- **Found during:** Task 3 — fresh venv creation
- **Issue:** `python3 -m venv /tmp/ketu18smoke` fails with "ensurepip is not available" — the `python3-venv` Debian package is not installed.
- **Fix:** Used `virtualenv` from the project venv (`/home/loc/workspace/ketu/venv/bin/virtualenv`) to create the fresh smoke venv. Produces an identical isolated environment for smoke purposes.
- **Commit:** N/A (execution-time workaround, not a code change)

## Known Stubs

None — plan goal fully achieved; ketu==1.8.0 is live on PyPI and smoke passes.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced in this plan. The published wheel is the reviewed source built by OIDC from the exact tagged commit — T-41-05 mitigation holds.

## Self-Check: PASSED

- [x] smoke_v18.py exists: `/home/loc/workspace/ketu/.planning/phases/41-documentation-release-v1-8-0/smoke_v18.py`
- [x] Commit e5de840 exists
- [x] Commit 0c20d4c exists (version bump, prior invocation)
- [x] `git ls-remote --tags origin` shows refs/tags/v1.8.0
- [x] PyPI JSON API confirms 1.8.0 present
- [x] publish.yml run 27820463468: success
- [x] Smoke printed SMOKE_OK
