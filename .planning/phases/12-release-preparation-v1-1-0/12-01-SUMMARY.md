---
phase: 12-release-preparation-v1-1-0
plan: 01
subsystem: release
tags: [versioning, semver, pyproject, importlib-metadata, release-prep]

# Dependency graph
requires:
  - phase: 07-release-preparation
    provides: "Two-source version pattern (pyproject.toml + ketu/__init__.py) gated by tests/test_version.py::test_version_matches_metadata"
  - phase: 11-cli-refactor-integration
    provides: "Stable 724-test green baseline carried forward unchanged into v1.1.0"
provides:
  - "pyproject.toml [project].version = \"1.1.0\""
  - "ketu/__init__.py __version__ = \"1.1.0\""
  - "importlib.metadata.version('ketu') == ketu.__version__ == '1.1.0' (sync gate green)"
  - "Captured baseline test count (724 passed) for use as headline number in Plan 12-04 GH release notes"
affects: [12-02-changelog-completion, 12-03-upgrading-completion, 12-04-release-publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-source version with single sync test (kept from v1.0.0)"
    - "Editable-install metadata refresh pattern: after bumping pyproject.toml [project].version, re-run `pip install -e . --no-deps` to regenerate venv dist-info before test_version.py can pass"

key-files:
  created: []
  modified:
    - "pyproject.toml (line 7: version 1.0.0 -> 1.1.0)"
    - "ketu/__init__.py (line 55: __version__ 1.0.0 -> 1.1.0)"

key-decisions:
  - "Atomic two-file commit prevents transient half-bumped state — commit 81f2dc3 touches exactly the two version locations and nothing else"
  - "Editable-install dist-info refresh treated as Rule 3 (blocking) deviation, not as a plan change — venv-local side-effect required to make `importlib.metadata.version('ketu')` reflect the new pyproject value"
  - "Test count headline = 724 (zero drift vs Phase 11 baseline) — version-string bump must be a no-op for everything except the sync test, and it was"

patterns-established:
  - "Editable-install metadata refresh: bumping pyproject [project].version requires `python -m pip install -e . --no-deps` to regenerate {sitepackages}/ketu-X.Y.Z.dist-info/ before importlib.metadata reflects the bump (test_version_matches_metadata fails until this is done)"
  - "Stale venv-shebang workaround: invoke pytest/mypy as `python -m pytest` / `python -m mypy` when venv was relocated and shebangs hardcode an old path (no venv rebuild needed; symlinks to the system python still work)"

# Metrics
duration: 1m 44s
completed: 2026-05-07
---

# Phase 12 Plan 01: Version Bump and Sync Summary

**Version bumped 1.0.0 -> 1.1.0 in both required source locations with atomic commit; full 724-test suite stays green and importlib.metadata sync gate passes — REL-01 closed.**

## Performance

- **Duration:** 1m 44s
- **Started:** 2026-05-07T22:36:09Z
- **Completed:** 2026-05-07T22:37:53Z
- **Tasks:** 2
- **Files modified:** 2 (pyproject.toml, ketu/__init__.py)

## Accomplishments

- `pyproject.toml [project].version` flipped `1.0.0` -> `1.1.0` (line 7, single-line edit, no reformatting)
- `ketu/__init__.py __version__` flipped `1.0.0` -> `1.1.0` (line 55, single-line edit; `__all__` and surrounding code untouched)
- Single atomic commit (`81f2dc3`) covers both files — Pitfall 1 (half-bumped state) provably absent
- Three-gate verification all green: version-sync test (2 passed) -> full pytest (**724 passed**) -> mypy --strict (Success: no issues found in 40 source files)
- Captured headline test count **724** for Plan 12-04 GH release notes (zero drift vs Phase 11 baseline of 724)

## Task Commits

Each task was committed atomically (per the plan's explicit instruction that BOTH file edits land in a SINGLE commit at the end of Task 2):

1. **Task 1: Bump version 1.0.0 -> 1.1.0 in both source files** — staged with Task 2 (no separate commit by design)
2. **Task 2: Verify version-sync test + full test suite + mypy, then commit** — `81f2dc3` (chore)
   - `chore(12-01): bump version 1.0.0 -> 1.1.0`
   - 2 files changed, 2 insertions(+), 2 deletions(-)

_Note: Plan 12-01 deliberately uses a single commit for the whole plan — the two file edits are semantically inseparable (sync test would fail if half-applied), so the plan called out atomicity explicitly. Task 1 staged only; Task 2 ran the gates and committed._

## Files Created/Modified

- `pyproject.toml` — line 7 bumped `version = "1.0.0"` -> `version = "1.1.0"` (no other changes)
- `ketu/__init__.py` — line 55 bumped `__version__ = "1.0.0"` -> `__version__ = "1.1.0"` (no other changes)

## Decisions Made

- **Atomic single-commit shape preserved.** The plan explicitly mandated one commit for both files. Verified by `git show --stat HEAD`: exactly 2 files, 2 insertions, 2 deletions, both single-line.
- **No fixture grep needed.** `grep -rn '"1\.0\.0"' tests/` was implicitly clean — full pytest stayed at 724 passed (zero failures), so no test fixture was hardcoded against the old version string. The `1.0.0`-string-search escape hatch from the plan was not exercised.
- **Underlying contract assertion run.** Beyond the test_version.py gate, the explicit phase-level python one-liner (`importlib.metadata.version('ketu') == ketu.__version__ == '1.1.0'`) was executed and passed — proves the sync test's assertion empirically rather than by-test-result alone.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Refreshed editable-install dist-info to regenerate package metadata to 1.1.0**

- **Found during:** Task 2 (Gate 1 first run)
- **Issue:** After bumping `pyproject.toml [project].version` to `1.1.0`, the FIRST run of `pytest tests/test_version.py` failed with `AssertionError: Version mismatch: package metadata=1.0.0, ketu.__version__=1.1.0`. Cause: editable installs (`pip install -e .`) materialize `pyproject.toml`'s metadata into `{sitepackages}/ketu-X.Y.Z.dist-info/` AT INSTALL TIME — `importlib.metadata.version("ketu")` reads the dist-info, NOT live pyproject.toml. The venv was last installed at v1.0.0, so dist-info still reported `1.0.0` even though both source files now declared `1.1.0`. Symptom looked like a half-bumped state but was actually a stale-install state.
- **Fix:** Ran `/home/loc/workspace/ketu/venv/bin/python -m pip install -e . --no-deps` to regenerate dist-info. Output confirmed `Uninstalling ketu-1.0.0` -> `Successfully installed ketu-1.1.0`. No source files touched, no dependencies reinstalled (`--no-deps` keeps numpy + pytest pinned).
- **Files modified:** None in repo. Only venv-local side-effect: `{venv}/lib/python3.13/site-packages/ketu-1.1.0.dist-info/` regenerated; `{venv}/lib/python3.13/site-packages/ketu-1.0.0.dist-info/` removed.
- **Verification:** Re-ran Gate 1 (`pytest tests/test_version.py -v`) — both tests pass. Re-ran phase-level contract assertion `importlib.metadata.version('ketu') == ketu.__version__ == '1.1.0'` — passes.
- **Committed in:** Not committed (transient venv state, not source-controlled).

**2. [Rule 3 - Blocking] Worked around stale venv shebang via `python -m {tool}` invocation**

- **Found during:** Task 2 (Gate 1, first attempt)
- **Issue:** `source venv/bin/activate && pytest tests/test_version.py` failed with `/home/loc/workspace/ketu/venv/bin/pytest: ne peut exécuter: le fichier requis n'a pas été trouvé`. Inspection (`head -1 venv/bin/pytest`) revealed the shebang hardcodes `#!/home/loc/workspace/solaris/ketu/venv/bin/python3` — the venv was created at `solaris/ketu/venv/` and the project tree was relocated to `/home/loc/workspace/ketu/`. The `python` symlink still resolved (`-> /usr/bin/python3`), but tool wrapper scripts pointed at a non-existent interpreter path.
- **Fix:** Invoked tools via `/home/loc/workspace/ketu/venv/bin/python -m pytest` and `python -m mypy` instead of relying on activated-venv shebang dispatch. Bypasses the broken wrapper while still using the venv's installed `pytest` / `mypy` packages.
- **Files modified:** None.
- **Verification:** All three gates ran successfully via `python -m {tool}` form.
- **Committed in:** Not committed (no source change).

---

**Total deviations:** 2 auto-fixed (both Rule 3 - Blocking)
**Impact on plan:** Both deviations are environmental (venv installation state), not plan defects. The plan's three-gate sequence and atomic-commit requirement were honored exactly. The `pip install -e .` refresh is a known artifact of the two-source version pattern with editable installs and should be promoted to Plan 12-RESEARCH addenda for future major-version bumps. The shebang issue is venv-local and unrelated to v1.1.0 release prep.

## Issues Encountered

None during planned work. Both blocking issues above were pre-existing environmental conditions surfaced by the version-bump verification gates (which is exactly what those gates exist to do).

## User Setup Required

None - no external service configuration required for this plan.

## Next Phase Readiness

REL-01 fully closed. Plan 12-02 (CHANGELOG completion) is unblocked and can begin immediately:

- **What's ready:** Both version locations declare `1.1.0`. The sync gate (`tests/test_version.py`) — which is the single source of truth for two-location parity — is green. Editable install in venv reflects 1.1.0. `724 passed` baseline carried forward for Plan 12-04 release-notes copy.
- **What's NOT yet done (deferred to Plan 12-02..12-04):**
  - `CHANGELOG.md` does not yet describe the v1.1.0 entry (Plan 12-02).
  - `UPGRADING.md` does not yet have a `1.0.0 -> 1.1.0` migration section (Plan 12-03).
  - No git tag exists yet; no GitHub release published (Plan 12-04).
- **Concerns:** None. The version is now atomically `1.1.0` everywhere it must be; downstream plans only have to write prose and create the tag.

## Self-Check

Verifying claims made in this SUMMARY before signaling completion:

- pyproject.toml exists and contains `version = "1.1.0"` at line 7: FOUND
- ketu/__init__.py exists and contains `__version__ = "1.1.0"` at line 55: FOUND
- Commit 81f2dc3 exists in git log: FOUND
- Commit 81f2dc3 subject is `chore(12-01): bump version 1.0.0 -> 1.1.0`: FOUND
- Commit 81f2dc3 changes exactly 2 files, 2 insertions, 2 deletions: FOUND
- importlib.metadata.version('ketu') == '1.1.0' AND ketu.__version__ == '1.1.0': FOUND
- pytest tests/test_version.py: 2 passed: FOUND
- pytest tests/: 724 passed: FOUND
- mypy ketu/ --strict: Success no issues found in 40 source files: FOUND

## Self-Check: PASSED

---
*Phase: 12-release-preparation-v1-1-0*
*Completed: 2026-05-07*
