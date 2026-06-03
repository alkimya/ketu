---
phase: 32-release-v1-4-0
plan: 01
subsystem: release
tags: [mypy, versioning, changelog, upgrading, readme, release-prep]

# Dependency graph
requires:
  - phase: 31-documentation-en-fr
    provides: "docs/source/conf.py already at 1.4.0; changelog.md body with [1.4.0] Added/Changed drafted"
provides:
  - "mypy --strict gate cleared (synastry/api.py:392 cast fix)"
  - "version bumped to 1.4.0 in both source-of-truth files (pyproject.toml + ketu/__init__.py)"
  - "CHANGELOG.md dated [1.4.0] section (Added: dynamic generator + Chiron 1900-2100; Changed: orb 0->4 + clamp + docs recentring)"
  - "fr/CHANGELOG.md matching French [1.4.0] section"
  - "docs/source/changelog.md [1.4.0] and [1.3.0] date-stamped (no XX placeholders)"
  - "UPGRADING.md v1.3->v1.4 section (orb break + clamp + range + additive generator)"
  - "README.md What's New in v1.4.0 section above v1.3.0"
affects: [32-02-release-gate, tagging, pypi-publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "cast(np.ndarray, ...) for typing-only no-op on boolean-indexed ndarray returns"
    - "Keep-a-Changelog fresh-authored section (no Unreleased to merge)"

key-files:
  created: []
  modified:
    - ketu/synastry/api.py
    - pyproject.toml
    - ketu/__init__.py
    - CHANGELOG.md
    - fr/CHANGELOG.md
    - docs/source/changelog.md
    - UPGRADING.md
    - README.md

key-decisions:
  - "cast(np.ndarray, out[...]) at synastry/api.py:392 is the correct fix for no-any-return — typing-only no-op, zero runtime change"
  - "CHANGELOG.md [1.4.0] authored fresh (no [Unreleased] to merge); [1.3.0] and below untouched"
  - "docs/source/conf.py NOT touched — already at 1.4.0 from Phase 31 (editing would create spurious diff)"
  - "Release date 2026-06-03 (UTC) used consistently across CHANGELOG.md, fr/CHANGELOG.md, docs/source/changelog.md"

patterns-established:
  - "Version bump requires two edits: pyproject.toml version field + ketu/__init__.__version__ — always together"
  - "UPGRADING.md newest-first: v1.3->v1.4 inserted before v1.2->v1.3"
  - "README What's New newest-first: v1.4.0 inserted before v1.3.0 with --- separator"

# Metrics
duration: 4min
completed: 2026-06-03
---

# Phase 32 Plan 01: Version Bump, CHANGELOG & Upgrading Guide Summary

**mypy --strict gate cleared (cast fix in synastry/api.py), version bumped 1.3.0->1.4.0, CHANGELOG [1.4.0] authored fresh with Added/Changed bullets, fr/CHANGELOG synced, docs date-stamped, UPGRADING v1.3->v1.4 and README What's New sections added**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-06-03T16:27:03Z
- **Completed:** 2026-06-03T16:30:59Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Fixed pre-existing `mypy --strict` error (`no-any-return` at `synastry/api.py:392`) introduced by Phase 28; zero mypy errors now across 69 source files
- Bumped version to 1.4.0 in both source-of-truth files (`pyproject.toml` + `ketu/__init__.py`); version sync gate green (2/2 test_version.py tests pass); `docs/source/conf.py` untouched
- Authored fresh CHANGELOG.md `[1.4.0]` section dated 2026-06-03 (Added: `generate_harmonic_aspects` + Chiron 1900-2100; Changed: Chiron orb 0->4 + clamp + docs recentring), synced to fr/CHANGELOG.md in French, date-stamped the docs/source/changelog.md placeholders for both [1.4.0] and [1.3.0]
- Added `## v1.3 -> v1.4` as the new first section in UPGRADING.md (four subsections: orb break, clamp, range, additive generator with runnable 1920 verify snippet)
- Added `## What's New in v1.4.0` above existing v1.3.0 section in README.md
- Full suite green: 1537 passed, 2 skipped, 100% coverage

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix mypy no-any-return and bump version to 1.4.0** — `df6c1c3` (feat)
2. **Task 2: Author CHANGELOG [1.4.0] fresh, sync fr/CHANGELOG, date-stamp docs** — `01e5c24` (docs)
3. **Task 3: Add UPGRADING v1.3->v1.4 and README What's New v1.4.0** — `6861cff` (docs)

**Plan metadata:** (final commit below)

## Files Created/Modified

- `ketu/synastry/api.py` — added `cast` to typing imports; wrapped filtered-mode return in `cast(np.ndarray, ...)` at line 392
- `pyproject.toml` — version `1.3.0` -> `1.4.0`
- `ketu/__init__.py` — `__version__` `1.3.0` -> `1.4.0`
- `CHANGELOG.md` — fresh `## [1.4.0] - 2026-06-03` block inserted above `[1.3.0]`
- `fr/CHANGELOG.md` — matching French `## [1.4.0] - 2026-06-03` block inserted above `[1.3.0]`
- `docs/source/changelog.md` — `[1.4.0] - 2026-06-XX` -> `2026-06-03`; `[1.3.0] - 2026-06-XX` -> `2026-06-01`
- `UPGRADING.md` — new `## v1.3 -> v1.4` first section with four subsections
- `README.md` — new `## What's New in v1.4.0` above existing `## What's New in v1.3.0`

## Decisions Made

- `cast(np.ndarray, out[out["aspect_type"] != -1])` is the correct typing-only fix for the `no-any-return` error — `cast` is a runtime no-op, zero behaviour change
- CHANGELOG.md `[1.4.0]` authored fresh because there was no `[Unreleased]` section to merge (unlike v1.3 release)
- `docs/source/conf.py` deliberately left untouched — it was pre-bumped to 1.4.0 in Phase 31 (Sphinx metadata); touching it would create a spurious no-op diff

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. The `pytest tests/test_version.py` run correctly showed coverage < 100% for the isolated run (only 2 files exercised); both tests passed. The full `pytest tests/` run confirmed 1537 passed / 100% coverage.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- mypy --strict gate: CLEAR
- Version sync gate: CLEAR (pyproject.toml == ketu/__init__.py == importlib.metadata == "1.4.0")
- CHANGELOG: COMPLETE (dated, no Unreleased, no XX placeholder)
- UPGRADING / README: COMPLETE
- Ready for Phase 32-02 (release gate: fresh-venv smoke + PyPI publish via OIDC)
- Per `feedback_validation_review_before_release`: user milestone review checkpoint must precede the tag/publish step

---
*Phase: 32-release-v1-4-0*
*Completed: 2026-06-03*

## Self-Check: PASSED

Files exist:
- FOUND: ketu/synastry/api.py (cast fix)
- FOUND: pyproject.toml (1.4.0)
- FOUND: ketu/__init__.py (1.4.0)
- FOUND: CHANGELOG.md ([1.4.0] - 2026-06-03)
- FOUND: fr/CHANGELOG.md ([1.4.0] - 2026-06-03)
- FOUND: docs/source/changelog.md (dates resolved)
- FOUND: UPGRADING.md (v1.3 -> v1.4 section)
- FOUND: README.md (What's New in v1.4.0)

Commits verified: df6c1c3, 01e5c24, 6861cff — all present in git log.
