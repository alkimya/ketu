---
phase: 12-release-preparation-v1-1-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
  - ketu/__init__.py
autonomous: true

must_haves:
  truths:
    - "pyproject.toml declares version 1.1.0"
    - "ketu/__init__.py declares __version__ = \"1.1.0\""
    - "tests/test_version.py passes (importlib.metadata == ketu.__version__)"
    - "Full pytest suite still passes (no regressions from the version bump)"
    - "mypy --strict on ketu/ remains clean"
  artifacts:
    - path: "pyproject.toml"
      provides: "Build/distribution metadata; version source for importlib.metadata"
      contains: "version = \"1.1.0\""
    - path: "ketu/__init__.py"
      provides: "Importable __version__ attribute"
      contains: "__version__ = \"1.1.0\""
  key_links:
    - from: "pyproject.toml [project].version"
      to: "ketu/__init__.py __version__"
      via: "tests/test_version.py::test_version_matches_metadata (importlib.metadata.version('ketu') == ketu.__version__)"
      pattern: "version = \"1\\.1\\.0\""
---

<objective>
Bump Ketu's version string from `1.0.0` to `1.1.0` in BOTH the dual hard-coded
locations enforced by `tests/test_version.py`, then prove the bump didn't break
anything by running the full test suite and mypy.

Purpose: Closes REL-01. The two-source pattern (pyproject + `__init__.py`)
gated by a single sync test is a deliberate v1.0 stability decision (see
`.planning/phases/07-release-preparation/07-02-SUMMARY.md`); v1.1 keeps it.
This plan does NOT create a new sync test — `tests/test_version.py` already
exists and already enforces parity. The plan only flips two strings and
verifies.

Output: Two files updated to `1.1.0` on `gsd/v1.1-milestone`, committed in a
single atomic commit, with `pytest tests/test_version.py` and the full
`pytest tests/` both green.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/12-release-preparation-v1-1-0/12-RESEARCH.md

@pyproject.toml
@ketu/__init__.py
@tests/test_version.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bump version 1.0.0 -> 1.1.0 in both source files (atomic)</name>
  <files>pyproject.toml, ketu/__init__.py</files>
  <action>
Make exactly two single-line edits on `gsd/v1.1-milestone`:

1. `pyproject.toml` line 7 — change `version = "1.0.0"` to `version = "1.1.0"`.
   - Verified ground truth: research confirms this is line 7, single-line
     simple string in `[project]` table. No `dynamic = ["version"]` to
     unwind. No `setup.cfg` / `setup.py`. Touch only this one line.

2. `ketu/__init__.py` line 55 — change `__version__ = "1.0.0"` to
   `__version__ = "1.1.0"`. Do NOT touch the `__all__` list at line 69
   that already lists `"__version__"` — it stays.

Both edits MUST be in the same git commit. Pitfall 1 from RESEARCH.md
(version bumped in only one file): if pyproject says 1.1.0 but
__init__.py says 1.0.0 (or vice versa), `importlib.metadata.version("ketu")
!= ketu.__version__` and `tests/test_version.py::test_version_matches_metadata`
fails. Atomic commit prevents a transient half-bumped state.

Use Edit tool (not sed) for both files to keep the diff minimal — no
trailing-whitespace churn, no line-ending churn. Do NOT reformat
either file.

After editing, do NOT run any tests in this task — Task 2 owns that.
  </action>
  <verify>
Two grep checks must both succeed:
```bash
grep -n '^version = "1.1.0"$' pyproject.toml         # expect line 7
grep -n '^__version__ = "1.1.0"$' ketu/__init__.py   # expect line 55
```
And neither file shall still contain `"1.0.0"`:
```bash
! grep -n '"1\.0\.0"' pyproject.toml
! grep -n '__version__ = "1\.0\.0"' ketu/__init__.py
```
`git diff --stat` shows exactly two files changed, each with a small
delta (one or two lines).
  </verify>
  <done>
Both `pyproject.toml` and `ketu/__init__.py` declare `1.1.0`. No other
edits to either file. Changes are staged but not yet committed (commit
happens in Task 2 after the test suite confirms the bump is safe).
  </done>
</task>

<task type="auto">
  <name>Task 2: Verify version-sync test + full test suite + mypy, then commit</name>
  <files>(no file edits; pytest + mypy + git only)</files>
  <action>
Run three gates in order. Stop on first failure.

1. Version-sync gate (the targeted test):
```bash
source venv/bin/activate
pytest tests/test_version.py -v
```
Expect: 2 passed (test_version_matches_metadata + test_version_format).
This is the existing test established in v1.0 — it is the gate that
catches half-bumped state.

If it fails with `AssertionError: 1.0.0 != 1.1.0` (or vice versa):
- One of the two files wasn't bumped. Re-run Task 1 verify greps and
  fix.
- DO NOT proceed to commit until both files agree.

2. Full test suite (no regressions from the bump):
```bash
pytest tests/ -q
```
Expect: 724 passed (per Phase 11 SUMMARY) ± a small drift. Capture the
exact passing count for the SUMMARY (used as the headline number in
the GH release notes by Plan 12-04).

If pytest reports failures: a string-bump should not break anything.
If something fails, it's a sign of a pre-existing flaky test or a
fixture that mentions `1.0.0` literally. grep `tests/` for `1.0.0`
string matches (`grep -rn '"1\.0\.0"' tests/`) and resolve case-by-case
before committing.

3. mypy gate:
```bash
mypy ketu/ --strict
```
Expect: `Success: no issues found`. A version-string change must not
affect typing.

Only after all three gates pass: commit atomically.
```bash
node ./.claude/get-shit-done/bin/gsd-tools.js commit \
  "chore(12-01): bump version 1.0.0 -> 1.1.0" \
  --files pyproject.toml ketu/__init__.py
```
The gsd-tools.js wrapper handles the Co-Authored-By trailer and
respects the project's commit-signing convention. Per Phase 11
environmental note (Plan 11-01), if GPG signing fails, fall back to
`git -c commit.gpgsign=false commit ...` for this single commit
(no global config change).

Verify the commit was created:
```bash
git log -1 --oneline
git show --stat HEAD
```
  </action>
  <verify>
- `pytest tests/test_version.py -v` reports 2 passed.
- `pytest tests/ -q` reports the full suite green (capture count).
- `mypy ketu/ --strict` reports `Success: no issues found`.
- `git log -1 --pretty=format:'%s'` returns the commit subject
  `chore(12-01): bump version 1.0.0 -> 1.1.0` (or close — gsd-tools
  may rewrite slightly).
- `git show HEAD -- pyproject.toml ketu/__init__.py` shows exactly
  two diff hunks (one per file), each touching a single line.
- `git status --porcelain` is clean (no other unstaged changes).
  </verify>
  <done>
Bumped version is committed on `gsd/v1.1-milestone`. The version-sync
test passes — Pitfall 1 (half-bumped state) is provably absent.
The full test count is captured in the plan SUMMARY for downstream use
by Plan 12-04 (release notes need to cite a number). REL-01 is
fully closed: both version locations are in sync, and the gate that
enforces parity passes.
  </done>
</task>

</tasks>

<verification>
Phase-level verification of REL-01 after Plan 12-01:

```bash
# Version is bumped in both locations
grep '^version = "1.1.0"$' pyproject.toml
grep '^__version__ = "1.1.0"$' ketu/__init__.py

# Sync gate passes
pytest tests/test_version.py -v

# No regressions
pytest tests/ -q
mypy ketu/ --strict

# importlib agrees with attribute (the underlying contract of the sync test)
python -c "
import importlib.metadata as m
import ketu
assert m.version('ketu') == ketu.__version__ == '1.1.0', \
    f'metadata={m.version(\"ketu\")!r} vs attr={ketu.__version__!r}'
print('OK 1.1.0')
"
```

Expected: every command above is silent or prints success.
</verification>

<success_criteria>
- `pyproject.toml` `[project].version == "1.1.0"`.
- `ketu/__init__.py __version__ == "1.1.0"`.
- `tests/test_version.py` passes (2 tests).
- Full suite (`pytest tests/`) passes; numeric count captured.
- `mypy ketu/ --strict` clean.
- Single atomic commit on `gsd/v1.1-milestone` touching exactly two files.
- REL-01 closed.
</success_criteria>

<output>
After completion, create `.planning/phases/12-release-preparation-v1-1-0/12-01-SUMMARY.md`
including:
- Confirmed pre-bump and post-bump version strings.
- Test count delta (724 baseline -> N actual).
- Commit hash of the version bump.
- Any deviations or surprises (e.g., a stray `1.0.0` string in a test
  fixture that needed adjusting).
</output>
