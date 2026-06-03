# Phase 12: Release Preparation v1.1.0 - Research

**Researched:** 2026-05-07
**Domain:** Python package release engineering (PyPI Trusted Publishing, GitHub releases, semver bump, breaking-change documentation)
**Confidence:** HIGH

## Summary

Phase 12 is the final, sequential phase of the v1.1 milestone. The hard
work is already done: phases 8-11 shipped Lilith fix, configurable
aspects (CLASSICAL default), houses module, and CLI refactor. Phase 12's
job is the release engineering layer on top: bump `1.0.0 -> 1.1.0`,
finish the partially-written CHANGELOG/UPGRADING entries, run pre-flight
checks, push the tag, and let the existing trusted-publishing workflow
publish to PyPI.

Crucially, **most of the infrastructure already exists** from Phase 7
(v1.0 release): trusted publisher is configured on PyPI, the
`.github/workflows/publish.yml` workflow is wired (tag push on `v*.*.*`
-> build -> twine check -> OIDC publish to `pypi` environment), and
`tests/test_version.py` already provides the version-sync gate. The
CHANGELOG.md `[1.1.0] - UNRELEASED` section already documents Lilith
(Phase 8) and houses (Phase 10). The UPGRADING.md `v1.0 -> v1.1` section
already documents Lilith. **The gaps Phase 12 must close** are
narrow and well-defined.

**Primary recommendation:** Decompose Phase 12 into four small
sequential plans (12-01 version bump, 12-02 changelog completion,
12-03 upgrading completion, 12-04 release publish), with 12-02 and
12-03 parallelizable. The version bump must land before the publish.
Do **not** add interrogate or strict numpydoc validation as a release
gate — they are aspirational in the ROADMAP but not currently wired
into CI; flagging this as out-of-scope keeps the release shippable.

## Standard Stack

### Core (already installed/configured)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| setuptools | >=61.0 | Build backend | Configured in `pyproject.toml`; v1.0 shipped on this. |
| build | latest | PEP 517 build frontend | Used by `publish.yml`; replaces `python setup.py`. |
| twine | latest | sdist/wheel validation + (fallback) upload | `publish.yml` runs `twine check dist/*`. |
| pypa/gh-action-pypi-publish | release/v1 | OIDC trusted publisher | Already wired in `publish.yml`; tokenless. |
| pytest | latest | Test runner | 724+ tests; `pytest tests/` is the gate. |
| mypy | latest | Static typing | `--strict` enforced in tests.yml on Python 3.11. |

### Supporting (recommended, not yet wired)
| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| check-wheel-contents | latest | Wheel content validation | Pre-flight: detect missing `py.typed`, stray files. Optional. |
| readme_renderer | latest | README markdown render check | `twine check` already does this; only add for deep debugging. |
| gh (GitHub CLI) | latest | Create release with notes | Final step after PyPI publish succeeds. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hard-coded version in two files | `importlib.metadata` dynamic | Already a v1.0 decision: keep dual-source pattern (pyproject + `__init__.py`) gated by `tests/test_version.py`. **Don't change this in v1.1** — it's a stability feature, not a wart. |
| Tag-triggered publish | `release: published` event | Tag-trigger is simpler and matches v1.0; do not change. |
| `setuptools-scm` | Read git tag | Not used; not needed; out of scope. |

**Installation (Phase 12 dev workflow):**
```bash
# All already present in venv if you have [test] extra installed.
pip install -e .[test]
pip install build twine  # for local pre-flight
# gh CLI is system-installed; verify with: gh --version
```

## User Constraints

This phase has no `CONTEXT.md` (no `/gsd:discuss-phase` was run).
Treat all aspects as Claude's discretion within the goal/requirements
bounds defined in `.planning/ROADMAP.md` Phase 12.

**Hard constraints from ROADMAP / requirements:**
- REL-01: version `1.0.0 -> 1.1.0` in BOTH `pyproject.toml` AND
  `ketu/__init__.py`; the version-sync test must pass.
- REL-02: CHANGELOG section "BREAKING / Numerical Behavior Changes"
  must list: CLI default change, Lilith correction, new houses module.
- REL-03: UPGRADING.md must have explicit migration recipes for
  script users (CLI), Kala adapter, Lilith consumers.
- REL-04: GitHub release v1.1.0 + PyPI publish via existing trusted
  publishing OIDC workflow.

**Cross-cutting (from ROADMAP cross-cutting constraints):**
- `core.aspects` array length-14 append-only — already verified by
  Phase 9 invariant test; nothing to do here.
- No new runtime dependencies — `pysweph` stays test-only; nothing to
  do here.
- mypy strict, vectorization, UTC datetimes, cache key hashes — all
  already enforced; nothing to do here.

## Current State of the Repository (Verified 2026-05-07)

This section is the **ground truth** the planner needs. Every claim
below was verified by reading the actual file at the cited path.

### Version locations (REL-01)
- `pyproject.toml:7` — `version = "1.0.0"` (single line, simple
  string).
- `ketu/__init__.py:55` — `__version__ = "1.0.0"`.
- These are the only two places. No `setup.cfg`, no `setup.py`.

### Version-sync test (REL-01) — ALREADY EXISTS
- `tests/test_version.py` already implements:
  - `test_version_matches_metadata()` — `importlib.metadata.version("ketu")` vs. `ketu.__version__`.
  - `test_version_format()` — semver regex.
- Runs as part of `pytest tests/`. **No new test needed.** The plan
  must only verify it passes after the bump (it will fail if you
  bump only one of the two locations, which is exactly its job).

### CHANGELOG.md — ALREADY PARTIALLY WRITTEN
The file exists at the repo root, follows **Keep a Changelog** format
plus semver. The `[1.1.0] - UNRELEASED` section at the top **already
contains**:
- `### Removed (BREAKING)` — `ketu.ephemeris.calculate_house_cusps`
  (HOU-10).
- `### Added` — `ketu.houses` module (HOU-02..HOU-10).
- `### Fixed (BREAKING - Numerical Behavior Change)` — Lilith
  formula correction with full magnitude detail (Phase 8).
- `### Added` — Lilith definition contract, cross-check harness,
  test-only `pysweph` extra.
- `### Migration` — pointer to UPGRADING.md.

**What is MISSING from CHANGELOG.md `[1.1.0]`:**
1. The CLI default change (Phase 9: EXTENDED -> CLASSICAL = 5 majors).
   This is the third item in REL-02 success criterion 2, and
   currently **completely unmentioned** in CHANGELOG.
2. New CLI subcommands and flags (Phase 11: `ketu houses`,
   `--aspect-set`, `--harmonics`, `--list-aspect-sets`,
   `--list-house-systems`, `# Aspect set:` resolved-config header on
   stderr).
3. Mention that the `[1.1.0]` section header date string `UNRELEASED`
   must be replaced with the actual release date (e.g. `2026-05-07`)
   when 12-04 cuts the release.
4. The roadmap's REL-02 phrasing asks for a single section titled
   "BREAKING / Numerical Behavior Changes". The current changelog
   uses Keep-a-Changelog subheadings (`### Fixed (BREAKING - ...)`,
   `### Removed (BREAKING)`). The planner must decide: (a) keep the
   existing structure and treat REL-02 as satisfied by the union of
   sub-headings, or (b) add a single rolled-up summary section near
   the top that mirrors REL-02's exact heading. Recommend (a) +
   add a small **rolled-up summary list** at the top of `[1.1.0]`
   for quick scanning.

### UPGRADING.md — ALREADY PARTIALLY WRITTEN
The file exists at the repo root. The `## v1.0 -> v1.1` section is
**very thorough on Lilith**: full per-date table, root cause, fix
formula with all 5 fitted constants, post-fix accuracy, action
required, downstream-consumer notes.

**What is MISSING from UPGRADING.md `v1.0 -> v1.1`:**
1. **CLI default-aspect-set migration** (the largest user-visible
   non-Lilith breaking change). Section "Other v1.0 -> v1.1 Changes"
   currently says "configurable aspects, houses module, CLI refactor
   is backward-compatible" — this is **misleading**: the CLI default
   *did* change from EXTENDED (14) to CLASSICAL (5), which means
   scripted users who parsed `ketu` CLI output will see ~64% fewer
   aspect rows. A migration recipe is mandatory here.
2. **Kala adapter migration recipe** (REL-03 explicit requirement).
   Kala's `KetuDataAdapter` (lives in sibling repo
   `/home/loc/workspace/solaris/kala/`, **not** in this repo) was
   getting EXTENDED implicitly in v1.0. In v1.1 it must explicitly
   request EXTENDED via the API parameter `aspects=EXTENDED` (or
   CLI `--aspect-set EXTENDED`). Migration text only — do not
   modify Kala from this repo.
3. **Houses module discoverability** — short subsection pointing to
   the new `ketu.houses` API and the `ketu houses` subcommand,
   noting that the legacy broken `ketu.ephemeris.calculate_house_cusps`
   was removed (already in CHANGELOG, but UPGRADING should
   cross-reference).
4. **`# Aspect set:` resolved-config header on stderr** — mildly
   breaking for users grepping stderr; one short note suffices.

### Publish workflow (REL-04) — ALREADY EXISTS
- `.github/workflows/publish.yml`:
  - Trigger: `on.push.tags: ['v*.*.*']` (tag-push trigger).
  - Job 1 `build`: checkout, Python 3.11, `python -m build --sdist
    --wheel`, `twine check dist/*`, upload artifact.
  - Job 2 `publish-to-pypi`: needs `build`, runs in `environment:
    pypi`, `permissions.id-token: write`, downloads artifact,
    `pypa/gh-action-pypi-publish@release/v1` (no token — OIDC
    trusted publishing).
- **Trusted publisher was configured on PyPI during the v1.0 release**
  (see `.planning/phases/07-release-preparation/07-02-SUMMARY.md`
  key-decisions: "Configured trusted publisher: Owner=alkimya,
  Repository=ketu, Workflow=publish.yml, Environment=pypi"). It is
  per-project and persists across releases — **no PyPI-side
  configuration is needed for v1.1.0**.
- **No TestPyPI step in the workflow.** This is fine; for v1.1.0
  optional TestPyPI validation can be done locally with `twine
  upload --repository testpypi dist/*`. The plan should mark
  TestPyPI as optional, not mandatory.

### Tests workflow (`.github/workflows/tests.yml`)
- Triggers: push to `main` or `develop`, PR to `main`,
  `workflow_dispatch`. **Note: `gsd/v1.1-milestone` is NOT in
  the trigger list.** Tests on the milestone branch run only via
  manual `workflow_dispatch` or PR-to-main.
- Matrix: Python 3.10, 3.11, 3.12, 3.13.
- Steps: `pytest tests/ -v --cov=ketu --cov-report=term-missing`,
  `mypy ketu/ --strict` (3.11 only), `--cov-fail-under=70` (3.13
  only), Codecov upload (3.13 only).

### Branch state
- Working branch: `gsd/v1.1-milestone` (current branch, per
  `git branch -a`).
- Target branch: `main` (per `git branch -a`).
- v1.0.0 was tagged on `main` (`git tag -l` shows `v1.0.0`).
- **Implication:** the merge of `gsd/v1.1-milestone -> main` happens
  in 12-04 *before* tagging `v1.1.0`. The tag must be on a commit
  reachable from `main` so post-release `pip install ketu==1.1.0`
  reproducibly maps back to a commit on `main`.

### Test count and quality gates (current state)
- 724+ tests passing (per Phase 11 SUMMARY commits).
- mypy `--strict` clean (CI on Python 3.11).
- Coverage gate: `--cov-fail-under=70` (project-wide, Python 3.13
  job in `tests.yml`).
- Houses module gate: `make houses-coverage` enforces ≥95% on
  `ketu/houses/*` only (per Makefile).
- ASP-08 EXTENDED regression bound (Phase 9, ≤5%).
- v1.1 byte-stability test (`tests/cli/test_v1_1_reference_byte_stable.py`,
  fixture at `tests/cli/fixtures/v1_1_reference_output.txt`,
  sha256 `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`).
  This is a **forward** contract on v1.1, not a backward contract
  on v1.0. Don't try to make v1.0 byte-stable against this fixture.
- README badges and the "What's New in v1.0.0" section are
  out-of-date (still say 1.0.0). README rendering on PyPI is
  validated by `twine check`.

### NOT currently in CI / not a release blocker
- **`interrogate` is NOT installed or configured** anywhere in the
  repo. Not in `pyproject.toml`, not in `Makefile`, not in any
  workflow. The ROADMAP cross-cutting constraint and the Phase 12
  success criterion 4 mention "interrogate ≥95%" but this is
  aspirational. **Recommendation:** treat as out-of-scope for
  Phase 12 — installing and tuning interrogate to ≥95% across the
  whole package is its own piece of work and would block the
  release. Document this gap in the phase verification (or a
  follow-up phase).
- **`numpydoc` strict validation is NOT wired into CI** either.
  Phase 6 SUMMARY says docstrings are numpydoc-formatted, but
  there is no `numpydoc validate` gate in `tests.yml`. Same
  recommendation: out-of-scope for the release.
- **README.md still references "v1.0.0" extensively.** Updating
  README "What's New" to a v1.1.0 banner is a nice-to-have, not
  blocking. Recommend a small touch-up in 12-02 or as a sub-step
  of 12-04, but not a separate plan.

## Architecture Patterns

### Recommended Plan Decomposition (Phase 12)

```
.planning/phases/12-release-preparation-v1-1-0/
├── 12-01-version-bump-and-sync-PLAN.md         # REL-01 (depends: nothing)
├── 12-02-changelog-completion-PLAN.md          # REL-02 (depends: nothing; can run parallel to 01 + 03)
├── 12-03-upgrading-completion-PLAN.md          # REL-03 (depends: nothing; can run parallel to 01 + 02)
├── 12-04-release-publish-PLAN.md               # REL-04 (depends: 01, 02, 03 ALL complete)
└── 12-RESEARCH.md (this file)
```

**Why four plans, not one:** the four artifacts (version bump,
CHANGELOG, UPGRADING, publish) are independently authored and
independently reviewed. A single mega-plan would be hard to revert
piece-meal if (e.g.) the changelog wording needs revision after
the version bump landed. Plans 02 and 03 are doc-only and trivially
parallelizable. Plan 04 is the human-in-loop release checkpoint.

**Why not split 12-04 further:** the release sequence (merge to
main, tag, GH Actions runs, GitHub release, smoke-test) is a single
human-in-loop ceremony — splitting it into sub-plans adds
synchronization overhead without value. Inside 12-04, use a checklist.

### Pattern 1: Dual Hard-Coded Version (KEEP THIS)
**What:** Version is duplicated in `pyproject.toml` and
`ketu/__init__.py`, and `tests/test_version.py` enforces parity.
**When to use:** This is the v1.0 decision. Don't change it in v1.1.
**Example:**
```toml
# pyproject.toml
[project]
version = "1.1.0"  # bump here
```
```python
# ketu/__init__.py
__version__ = "1.1.0"  # AND here — test_version.py will fail otherwise
```
Source: `tests/test_version.py` (already in repo).

### Pattern 2: Tag-Triggered Trusted Publishing (ALREADY WIRED)
**What:** Push tag `v*.*.*` -> `publish.yml` builds + publishes to
PyPI via OIDC, with no API token.
**When to use:** This IS the v1.1 release path. Don't introduce
alternatives.
**Source:** `.github/workflows/publish.yml`,
[PyPI Trusted Publishers docs](https://docs.pypi.org/trusted-publishers/).

### Pattern 3: Pre-Flight Local Build + Smoke Test
**What:** Before pushing the tag, build locally, run `twine check`,
install in a fresh venv, verify `import ketu; ketu.__version__ ==
"1.1.0"`, run the test suite once. This is non-destructive and
catches the workflow-failure case where tag is pushed but build
fails — at which point the tag is "burned" on PyPI (PyPI never lets
you republish a version, even if upload failed mid-flight in some
edge cases).
**When to use:** Mandatory pre-step in 12-04.
**Example:**
```bash
# Local pre-flight (before pushing tag)
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel
python -m twine check dist/*
# Fresh venv install test
TMP_VENV=$(mktemp -d)
python -m venv "$TMP_VENV"
"$TMP_VENV/bin/pip" install -q dist/ketu-1.1.0-py3-none-any.whl
"$TMP_VENV/bin/python" -c "import ketu; assert ketu.__version__ == '1.1.0'"
"$TMP_VENV/bin/pip" install -q pytest pytest-cov numpy
"$TMP_VENV/bin/pytest" tests/ -q --no-cov  # smoke test
deactivate 2>/dev/null || true
rm -rf "$TMP_VENV"
```

### Anti-Patterns to Avoid
- **Don't tag before merging to `main`.** The v1.0 pattern was tag
  on `main`. Tagging `gsd/v1.1-milestone` directly would make the
  v1.1.0 commit unreachable from `main` after merge.
- **Don't `git tag --force` to retry a failed publish.** PyPI
  forbids re-uploading an already-uploaded `1.1.0`. If 12-04 fails
  partway, fix the issue, bump to `1.1.1` (yes, even for the first
  attempt), and re-tag. **Or** if the failure is in the workflow
  *before* PyPI accepts the upload (e.g., build fails, twine check
  fails), you can delete the tag and re-tag — but only if PyPI
  never received the file. Verify on PyPI before deciding.
- **Don't add `interrogate` as a release gate in this phase.** The
  ROADMAP mentions it but it's not configured. Adding it now
  blocks the release. Defer to a v1.1.x patch or v1.2 phase.
- **Don't try to make v1.1 byte-identical to v1.0 CLI output.** The
  byte-stability fixture from 11-06 (`v1_1_reference_output.txt`)
  is a v1.1 *self-pin*, not a v1.0 backward contract. v1.1 CLI
  output is intentionally different (5 aspects vs 14, new stderr
  header, new houses subcommand).
- **Don't update the `# What's New in v1.0.0` README section in a
  separate plan.** Roll it into 12-02 (CHANGELOG-adjacent) or
  12-04 (release ceremony).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PyPI authentication | API tokens checked into secrets | OIDC trusted publishing (already wired) | Tokens are long-lived; OIDC tokens expire in ~15min and are scoped to the workflow run. |
| Build artifacts | Custom `setup.py sdist bdist_wheel` | `python -m build --sdist --wheel` | PEP 517 standard, isolated build environments, reproducible. |
| Wheel metadata validation | Manual unzip + grep | `twine check dist/*` | Already in `publish.yml`; validates README rendering, classifier validity, license expression. |
| Version sync check | Manual grep before commit | `tests/test_version.py` (already exists) | Already enforced via pytest; CI catches it. |
| Release notes | Hand-typed in GitHub UI | `gh release create v1.1.0 --notes-file ...` extracted from CHANGELOG | Reproducible, audit-able; less risk of GitHub-flavored markdown drift. |
| Fresh-install validation | "Trust the wheel" | `python -m venv` + `pip install dist/*.whl` + smoke import | The single most-effective release blocker check; catches missing `py.typed`, stray dependencies, MANIFEST issues. |

**Key insight:** PyPI release is **unforgiving**. A version cannot
be deleted or republished. Every avoidable risk should be moved
left into pre-flight. The cost of a 5-minute fresh-venv check is
negligible vs. shipping `1.1.0` and discovering at user-install
time that `py.typed` is missing.

## Common Pitfalls

### Pitfall 1: Version Bumped in Only One File
**What goes wrong:** `pyproject.toml = 1.1.0` but
`ketu/__init__.py = 1.0.0` (or vice versa). `pip install
ketu==1.1.0` works but `import ketu; ketu.__version__` reports
`1.0.0`. Users debug for hours.
**Why it happens:** Two-source pattern requires manual sync.
**How to avoid:** Bump both in the **same commit**. Run
`pytest tests/test_version.py -v` locally before pushing.
`tests/test_version.py::test_version_matches_metadata` is the
gate. Plan 12-01 task: edit both files; verify; commit.
**Warning signs:** test_version.py fails locally OR in CI.

### Pitfall 2: CHANGELOG `UNRELEASED` Tag Not Replaced
**What goes wrong:** Tag `v1.1.0` is pushed but CHANGELOG.md still
says `## [1.1.0] - UNRELEASED`. PyPI page and GitHub release link
to a "release" that says it's not released.
**Why it happens:** Easy to forget — the release-prep author
edits CHANGELOG weeks before the actual release.
**How to avoid:** In Plan 12-04, **first task** is "replace
`UNRELEASED` with the actual release date in CHANGELOG.md, commit
`docs(release): set v1.1.0 release date YYYY-MM-DD`". This commit
is the LAST commit before tagging.
**Warning signs:** Search `grep -n UNRELEASED CHANGELOG.md` returns
the v1.1.0 section header.

### Pitfall 3: Tagging Before Merging to main
**What goes wrong:** Tag `v1.1.0` is pushed from
`gsd/v1.1-milestone`. The publish workflow runs and PyPI gets the
artifact. But `gsd/v1.1-milestone` is later merged to `main` via
a merge commit, and the v1.1.0 commit hash is no longer reachable
from `main` linearly. `git checkout v1.1.0` works but
`git log main` doesn't show `v1.1.0` as a parent.
**Why it happens:** Wrong order in release ceremony.
**How to avoid:** **Merge first, tag second.** Sequence in 12-04:
1. Open PR `gsd/v1.1-milestone -> main`. CI must pass.
2. Merge (use a fast-forward or merge commit; prefer fast-forward
   if the branch is rebased).
3. Checkout `main`, pull, verify `git log` shows the v1.1
   commits.
4. Replace `UNRELEASED` with date in CHANGELOG, commit on `main`.
5. **Then** tag: `git tag -a v1.1.0 -m "Release 1.1.0"`.
6. Push tag: `git push origin v1.1.0`.
**Warning signs:** `git tag -l --contains main` doesn't include
`v1.1.0`.

### Pitfall 4: Missing the CLI-Default Migration Recipe
**What goes wrong:** A v1.0 user pipes `ketu | wc -l` (or scrapes
stdout in a script) expecting 14 aspects per body. v1.1 emits 5.
Their script silently produces wrong output. UPGRADING.md says
"backward-compatible".
**Why it happens:** The current UPGRADING.md "Other v1.0 -> v1.1
Changes" subsection literally says configurable aspects "is
backward-compatible". This is wrong at the CLI default level.
**How to avoid:** Plan 12-03 must add a "CLI Default Aspect Set"
subsection with:
- Statement: "v1.0 default = EXTENDED (14 aspects). v1.1 default
  = CLASSICAL (5 aspects: Conjunction, Sextile, Square, Trine,
  Opposition)."
- Migration recipe (script users): `ketu --aspect-set EXTENDED
  ...` to restore.
- Migration recipe (Python API): pass `aspects=EXTENDED` from
  `ketu.aspects.presets`.
- Programmatic detection: `--list-aspect-sets` to list available
  presets.
**Warning signs:** UPGRADING.md grep for "EXTENDED" returns zero
hits in the v1.1 section.

### Pitfall 5: Kala Adapter Migration Recipe Forgotten
**What goes wrong:** Kala (sibling repo
`/home/loc/workspace/solaris/kala/`) was implicitly receiving
EXTENDED in v1.0. After Kala upgrades to ketu 1.1, its
`KetuDataAdapter` silently switches to CLASSICAL — Kala loses 9
aspect features per body without any error.
**Why it happens:** REL-03 explicitly calls this out, but the
fix lives in UPGRADING.md prose and is easy to skip.
**How to avoid:** Plan 12-03 dedicated subsection "Kala /
Downstream Adapter Migration" with concrete API-level recipe.
Note: do NOT modify Kala from this repo — Kala is a sibling
project.
**Warning signs:** UPGRADING.md grep for "Kala" returns zero hits
in the v1.1 section.

### Pitfall 6: README PyPI-Render Failure
**What goes wrong:** README.md uses GFM-only syntax (e.g., GitHub
alerts `> [!NOTE]`) that PyPI's renderer doesn't support. PyPI
shows a fallback "long_description rendering failed" or strips
the formatting.
**Why it happens:** README is GitHub-first, PyPI is an
afterthought.
**How to avoid:** `twine check dist/*` validates this and is
**already in publish.yml**. Pre-flight: run `python -m build`
locally and `python -m twine check dist/*`. Inspect the resulting
`dist/*.tar.gz` PKG-INFO to confirm the long_description.
**Warning signs:** `twine check` reports `WARNING` or `ERROR`.

### Pitfall 7: gsd/v1.1-milestone CI Status Unknown
**What goes wrong:** Tests workflow doesn't run on
`gsd/v1.1-milestone` automatically (only on `main`/`develop`/PR
to main/manual). The release-prep author assumes "CI is green"
without verifying.
**Why it happens:** Branch trigger gap in `tests.yml`.
**How to avoid:** Plan 12-04 first sub-step: trigger
`workflow_dispatch` on `tests.yml` for `gsd/v1.1-milestone`, OR
open the PR to main early and rely on PR CI. **Don't push the
tag until you've seen a green CI run on the actual commit
you're tagging.**
**Warning signs:** `gh run list --branch gsd/v1.1-milestone
--workflow tests.yml` shows no recent successful runs.

### Pitfall 8: PyPI 1.1.0 Reserved or Burned
**What goes wrong:** `1.1.0` was already uploaded (e.g., from a
previous abandoned attempt) and PyPI rejects the new upload.
You're stuck — must bump to `1.1.0.post1` or `1.1.1`.
**Why it happens:** Failed prior attempts; manual TestPyPI
upload that accidentally went to PyPI.
**How to avoid:** Pre-flight check (Plan 12-04, before tag): `pip
index versions ketu` or visit https://pypi.org/project/ketu/#history
to confirm `1.1.0` is NOT yet listed.
**Warning signs:** `pip install ketu==1.1.0` succeeds *before* you
've published.

### Pitfall 9: Trusted Publisher Misconfigured After Repo Rename
**What goes wrong:** PyPI trusted publisher is configured for
`alkimya/ketu` repo. If the repo was renamed/moved, the OIDC
token claim won't match and publish fails with a confusing
"trust" error.
**Why it happens:** Trusted publisher config is per
(owner,repo,workflow,environment) tuple.
**How to avoid:** Verify before tag: visit
https://pypi.org/manage/project/ketu/settings/publishing/
and confirm publisher matches: Owner=`alkimya`, Repo=`ketu`,
Workflow=`publish.yml`, Environment=`pypi`.
**Warning signs:** `publish-to-pypi` job in workflow logs shows
"OIDC token verification failed" or similar.

## Code Examples

### REL-01: Version Bump (in both files)
```toml
# pyproject.toml
[project]
name = "ketu"
version = "1.1.0"   # was "1.0.0"
```
```python
# ketu/__init__.py
__version__ = "1.1.0"  # was "1.0.0"
```
Source: existing repo files; pattern established in v1.0.

### REL-01: Version-sync verification
```bash
# Already exists; no new test needed.
pytest tests/test_version.py -v
# Expected: 2 passed
```
Source: `tests/test_version.py` (already in repo).

### REL-02: CHANGELOG section template (top-of-file scan summary)

Insert at the top of the existing `## [1.1.0]` section, just below
the version header line. Treat this as a "rolled-up summary" for
quick scanning; the existing detailed `### Removed (BREAKING)`,
`### Added`, `### Fixed (BREAKING - Numerical Behavior Change)`
subsections stay intact.

```markdown
## [1.1.0] - 2026-05-XX   <!-- replace UNRELEASED with date -->

### BREAKING / Numerical Behavior Changes (Summary)

This release contains three user-visible behavior changes from v1.0.
Read each in detail below and consult `UPGRADING.md` for migration
recipes.

1. **CLI default aspect set: EXTENDED (14) -> CLASSICAL (5).** The
   `ketu` CLI emits 5 major aspects (conjunction, opposition, trine,
   square, sextile) by default. Restore v1.0 behavior with
   `ketu --aspect-set EXTENDED`. (Phase 9 / ASP-04)
2. **Lilith longitude formula corrected.** Mean Apogee values now
   match Swiss Ephemeris `SE_MEAN_APOG` to <0.01 deg. v1.0 values
   were ~180 deg off on every date. Recompute any cached Lilith
   data. (Phase 8 / LIL-03)
3. **Houses module replaces broken `calculate_house_cusps`.** The
   v1.0 `ketu.ephemeris.calculate_house_cusps` always returned an
   Equal House fallback regardless of system; it has been removed.
   Use the new `ketu.calculate_houses(...)` API or the `ketu houses`
   subcommand. (Phase 10 / HOU-10)

Non-breaking but notable: new CLI subcommands and flags
(`ketu houses`, `--aspect-set`, `--harmonics`,
`--list-aspect-sets`, `--list-house-systems`); resolved-config
header `# Aspect set: ...` printed to stderr; sidereal time
tightened to apparent GST.
```

(The detailed sub-sections that already exist in CHANGELOG.md
follow this summary unchanged.)

### REL-03: UPGRADING.md additions (sketch)

Add **before** the existing "### Other v1.0 -> v1.1 Changes" sentence
(which currently misleads users by claiming "backward-compatible"),
or replace that sentence wholesale.

```markdown
### CLI Default Aspect Set (Phase 9)

In v1.0, the `ketu` CLI emitted **14 aspects per body pair** (the
EXTENDED preset: conjunction, opposition, trine, square, sextile,
quincunx, semisextile, semisquare, sesquisquare, quintile,
biquintile, novile, septile, decile).

In v1.1, the CLI default is **CLASSICAL: 5 major aspects only**
(conjunction, opposition, trine, square, sextile). Scripts that
parsed v1.0 CLI output will receive ~64% fewer aspect rows.

**Migration recipe (CLI users):**

```bash
# Restore v1.0 behavior:
ketu --aspect-set EXTENDED

# Or pin to v1.0:
pip install 'ketu<1.1'

# To list available presets:
ketu --list-aspect-sets
```

**Migration recipe (Python API users):**

```python
# v1.0 implicit:
from ketu.aspects import calculate_aspects
result = calculate_aspects(jd, bodies)  # got 14 aspects

# v1.1 explicit (recommended):
from ketu.aspects import calculate_aspects
from ketu.aspects.presets import EXTENDED
result = calculate_aspects(jd, bodies, aspects=EXTENDED)  # 14 aspects
```

### Kala / Downstream Adapter Migration (Phase 9)

If you maintain a downstream adapter that consumes Ketu's aspect
output (Kala's `KetuDataAdapter`, custom scripts, ML feature
pipelines), check whether you depend on the **count** or **set**
of aspect rows.

**Recipe:** explicitly request EXTENDED at the API boundary:

```python
# In your adapter's Ketu call site:
from ketu.aspects.presets import EXTENDED
from ketu.aspects import calculate_aspects_batch

aspects = calculate_aspects_batch(jds, bodies, aspects=EXTENDED)
# or via core.aspects, which remains length-14 append-only
```

`core.aspects` row order and length are **unchanged** (verified
by Phase 9 invariant test). Positional indexing into the length-14
array still works. Only the *default selection* changed.

### Houses Module (Phase 10)

The broken v1.0 placeholder `ketu.ephemeris.calculate_house_cusps`
is **removed**. Use the new `ketu.houses` module instead:

```python
# v1.0 (BROKEN, now removed):
from ketu.ephemeris import calculate_house_cusps  # ImportError

# v1.1:
from ketu import calculate_houses, house_of
houses = calculate_houses(jd, lat, lon, system='placidus')
ascendant = houses['cusps'][..., 0]  # cusp 1
which_house = house_of(planet_lon=200.0, cusps=houses['cusps'][0])
```

Or via CLI:

```bash
ketu houses --jd 2451545.0 --lat 48.85 --lon 2.35 --system placidus
ketu --list-house-systems
```

### Resolved-Config stderr Header (Phase 9)

The CLI now prints a `# Aspect set: <name>` header to **stderr**
(not stdout) to surface which preset was used. This is mildly
breaking only for users who pipe stderr through aspect-output
parsing; standard `ketu | parser` pipelines (stdout-only) are
unaffected. Suppress with `2>/dev/null` if needed.
```

### REL-04: Local pre-flight script
```bash
#!/usr/bin/env bash
# 12-04 pre-flight - run BEFORE pushing tag v1.1.0
set -euo pipefail
VERSION="1.1.0"

# 1. Verify clean working tree
test -z "$(git status --porcelain)" || { echo "Working tree not clean"; exit 1; }

# 2. Verify version sync
grep -q "version = \"${VERSION}\"" pyproject.toml || { echo "pyproject.toml not bumped"; exit 1; }
grep -q "__version__ = \"${VERSION}\"" ketu/__init__.py || { echo "__init__.py not bumped"; exit 1; }
pytest tests/test_version.py -v

# 3. Verify CHANGELOG date set
grep -q "^## \[${VERSION}\] - UNRELEASED" CHANGELOG.md && { echo "CHANGELOG still UNRELEASED"; exit 1; }
grep -q "^## \[${VERSION}\] - 20" CHANGELOG.md || { echo "CHANGELOG missing v${VERSION} dated section"; exit 1; }

# 4. Build
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel

# 5. twine check
python -m pip install --quiet twine
python -m twine check dist/*

# 6. Fresh venv install + smoke test
TMP=$(mktemp -d)
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"
"$TMP/bin/python" -c "import ketu; assert ketu.__version__ == '${VERSION}', f'got {ketu.__version__}'"
"$TMP/bin/python" -c "from ketu import calculate_houses, HOUSES_DTYPE; print('houses OK')"
"$TMP/bin/python" -c "from ketu.aspects.presets import CLASSICAL, EXTENDED; assert len(CLASSICAL) == 5; assert len(EXTENDED) == 14; print('presets OK')"
rm -rf "$TMP"

# 7. PyPI: confirm 1.1.0 not already taken
python -c "
import urllib.request, json
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/ketu/json').read())
versions = list(data['releases'].keys())
assert '${VERSION}' not in versions, f'PyPI already has ${VERSION}: {versions}'
print(f'PyPI clear, last version: {sorted(versions)[-1]}')
"

echo "Pre-flight OK. Safe to: git tag -a v${VERSION} -m 'Release ${VERSION}' && git push origin v${VERSION}"
```

### REL-04: GitHub release creation
```bash
# After PyPI publish succeeds (verify at https://pypi.org/project/ketu/1.1.0/)
gh release create v1.1.0 \
  --title "Ketu 1.1.0 - Configurable aspects, houses module, Lilith correction" \
  --notes "$(cat <<'EOF'
Ketu 1.1.0 introduces configurable aspect sets (5 majors by default,
opt-in EXTENDED for legacy 14), a new `ketu.houses` module
(Placidus/Koch/Porphyry/Equal/Whole-sign with polar fallback), a
corrected Lilith Mean Apogee formula matching Swiss Ephemeris, and
an argparse-based CLI with `ketu houses` subcommand and
introspection flags.

**This is a feature release with one breaking numerical change**
(Lilith longitudes shift by ~180 deg) and one breaking CLI default
change (EXTENDED -> CLASSICAL). See [UPGRADING.md] for migration
recipes.

- 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md#110---2026-05-XX)
- 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v10---v11)
- 📦 `pip install ketu==1.1.0`

Highlights:
- Configurable aspects: `--aspect-set {CLASSICAL,EXTENDED,custom}`
- New houses module: `ketu houses --system {placidus,koch,porphyry,equal,whole_sign}`
- Lilith fix: <0.01 deg vs Swiss Ephemeris (was ~180 deg off)
- 724+ tests, mypy strict, polar fallback, vectorized house calculations
EOF
)"
```

## State of the Art

| Old Approach (v1.0 era) | Current Approach (v1.1) | When Changed | Impact |
|-------------------------|--------------------------|--------------|--------|
| API token in GitHub secrets | OIDC trusted publishing | v1.0 release | Already wired, no action needed. |
| `python setup.py sdist bdist_wheel` | `python -m build --sdist --wheel` | PEP 517 (2017+) | Already wired in publish.yml. |
| Pin GitHub Action to commit SHA | `pypa/gh-action-pypi-publish@release/v1` | Recommended in PyPA docs | Already wired. |
| Implicit "latest" | `release/v1` tag | PyPA recommendation | Already wired. |
| No environment | `environment: pypi` with required reviewer | PyPA security recommendation | Already wired (no required reviewer set, but the environment exists). |

**Deprecated/outdated:**
- `setup.py`: not used; pyproject.toml is the canonical config.
- `pip install --index-url` to authenticate to PyPI: deprecated;
  trusted publishing supersedes.

## Open Questions

1. **Should the GitHub release title and notes be in French or English?**
   - What we know: README, CHANGELOG.md, UPGRADING.md are English
     primary, with `fr/CHANGELOG.md` as the French mirror. The
     v1.0.0 GitHub release was in English (per Phase 7 SUMMARY).
   - What's unclear: whether the v1.1 release should mirror in
     French.
   - Recommendation: English-only for the release notes (matches
     v1.0); update `fr/CHANGELOG.md` if it exists and is being
     maintained, but treat as nice-to-have.

2. **Should `tests.yml` be amended to also trigger on `gsd/v1.1-milestone`?**
   - What we know: current tests.yml triggers on `main` and
     `develop` only.
   - What's unclear: whether to add the milestone branch
     pre-merge for confidence-building.
   - Recommendation: open the PR to `main` early and rely on PR
     CI. Don't change `tests.yml` in Phase 12 — that's CI-policy
     work, not release work.

3. **Should `interrogate` be wired into CI as part of Phase 12?**
   - What we know: ROADMAP cross-cutting constraint and Phase 12
     success criterion 4 mention "interrogate ≥95%". `interrogate`
     is NOT installed or configured. The rest of the ROADMAP gates
     (mypy, pytest, coverage 70%, houses 95%) ARE wired.
   - What's unclear: whether the success criterion is a
     hard-gate or aspirational.
   - Recommendation: **out of scope** for Phase 12. Document the
     gap in 12-VERIFICATION.md and propose a follow-up phase or
     v1.1.1 patch. Adding interrogate now risks blocking the
     release on cosmetic docstring fixes.

4. **Should the README.md "What's New in v1.0.0" section be
   updated to "v1.1.0" in this phase?**
   - What we know: README is the long_description on PyPI and is
     visible to every new install. Currently shows v1.0.0
     highlights and badges referencing 1.0.0.
   - What's unclear: whether this is part of Phase 12's scope or
     a doc-update task for later.
   - Recommendation: include a small README update in Plan 12-02
     (alongside CHANGELOG) — change the "What's New" section to
     v1.1.0 highlights with a one-line link to CHANGELOG. Don't
     overhaul; just update the section header and 4-6 bullets.

5. **Is TestPyPI dry-run mandatory before PyPI publish?**
   - What we know: v1.0 release skipped TestPyPI per Phase 7
     SUMMARY. Local fresh-venv smoke-test was sufficient.
   - What's unclear: whether v1.1's larger surface (houses, CLI
     refactor) warrants TestPyPI insurance.
   - Recommendation: **optional**. Do TestPyPI only if local
     pre-flight uncovers any anomaly. Default path: skip TestPyPI,
     rely on the `twine check` + fresh-venv smoke test.

## Out of Scope (Explicit)

The planner should NOT add tasks for:

- **Adding `interrogate` to CI.** Aspirational; would block release.
- **Adding `numpydoc validate` to CI.** Same reason.
- **Refactoring `tests.yml` to trigger on `gsd/v1.1-milestone`.** CI
  policy, not release.
- **README overhaul.** Surgical update of "What's New" section is
  fine; a full rewrite is out.
- **Documentation site (Sphinx/RTD) republish.** ReadTheDocs
  auto-builds on push to `main`; no manual step needed.
- **French translations of new content.** Maintain `fr/CHANGELOG.md`
  if convenient, but not blocking.
- **New features.** No code changes to `ketu/` source beyond
  version-string bump in `__init__.py`.
- **Modifying Kala.** Kala lives at sibling
  `/home/loc/workspace/solaris/kala/`. Migration recipe is
  text-only.
- **Running pytest on Python 3.10/3.12 manually.** CI matrix
  handles this; pre-flight uses 3.11 (or whatever is in `venv/`).
- **Bumping `ketu-rs` or any other sibling project.**
- **Moving from setuptools to hatchling/poetry.** Stability over
  novelty; v1.1 keeps setuptools.
- **Adding a sigstore attestation step.** `pypa/gh-action-pypi-publish`
  emits attestations by default in `release/v1`; nothing to do.

## Sources

### Primary (HIGH confidence)
- `pyproject.toml` (read directly) — version line 7, classifiers,
  build backend, package list. State: 1.0.0, setuptools, py.typed
  shipped.
- `ketu/__init__.py` (read directly) — `__version__ = "1.0.0"` line
  55; exports include houses module symbols.
- `tests/test_version.py` (read directly) — confirms version-sync
  test exists; uses `importlib.metadata` and semver regex.
- `.github/workflows/publish.yml` (read directly) — confirms
  trusted publishing wiring: tag trigger, build job,
  publish-to-pypi job with `environment: pypi`,
  `permissions.id-token: write`, no token.
- `.github/workflows/tests.yml` (read directly) — confirms test
  triggers (main, develop, PR-to-main, manual), 4-version matrix,
  mypy strict on 3.11.
- `CHANGELOG.md` (read directly) — `## [1.1.0] - UNRELEASED`
  section is partially populated (Lilith + houses); CLI default
  change and Phase 11 CLI refactor not yet documented.
- `UPGRADING.md` (read directly) — v1.0 -> v1.1 section is
  Lilith-thorough; CLI default change and Kala recipe missing.
- `MANIFEST.in` (read directly) — README, LICENSE, CHANGELOG, fr
  docs included in sdist.
- `Makefile` (read directly) — `make houses-coverage` enforces
  HOU-09 ≥95% gate scoped to `ketu/houses/*`; `make mypy` runs
  `mypy --strict ketu/`.
- `.planning/phases/07-release-preparation/07-RESEARCH.md` and
  `07-02-SUMMARY.md` — prior v1.0 release artifacts; confirm
  trusted publisher was configured (Owner=alkimya, Repo=ketu,
  Workflow=publish.yml, Environment=pypi).
- [PyPI Trusted Publishers docs](https://docs.pypi.org/trusted-publishers/) — verified pattern matches `publish.yml`.
- [pypa/gh-action-pypi-publish README](https://github.com/pypa/gh-action-pypi-publish) — confirms `release/v1` tag, `id-token: write` requirement.
- [GitHub OIDC for PyPI](https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi) — confirms environment usage and security model.

### Secondary (MEDIUM confidence)
- WebSearch on "PyPI trusted publishing OIDC environment 2026 best
  practices" — multiple sources agree on (a) `id-token: write` at
  job level, (b) separate build/publish jobs, (c) `release/v1`
  pinning, (d) environment-based reviewer protection. Cross-verifies
  with PyPI docs.
- Phase 11 SUMMARY commits and `tests/cli/test_v1_1_reference_byte_stable.py`
  presence verified via git log and `find`.

### Tertiary (LOW confidence)
- Test count "724+" — claimed in Phase 11 SUMMARY commits; not
  re-verified in this research because `pytest --co` failed to run
  in the activated venv. The exact count may differ slightly.
  Actionable: in Plan 12-04 pre-flight, run `pytest tests/ -q`
  and capture the actual count for the release notes.

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — Reused from Phase 7 (v1.0 release);
  publish.yml unchanged; tools mature and stable.
- Architecture (plan decomposition): **HIGH** — Maps 1:1 to
  REL-01..REL-04 requirements; pattern matches Phase 7 (which used
  2 plans for a smaller release; v1.1's broader UPGRADING work
  justifies 4).
- Pitfalls: **HIGH** — Mostly verified against repo state and PyPI
  Trusted Publishing docs; pitfall 7 (CI trigger gap) and pitfall 9
  (publisher misconfig) are configuration-state-dependent and the
  planner should re-verify in 12-04 pre-flight.
- Repo state findings: **HIGH** — Every file claim was verified by
  `Read` or `grep` against the actual file at the cited path on
  branch `gsd/v1.1-milestone` at commit `f23fa63`.
- Test count and CI green status: **MEDIUM** — Claimed in commit
  history, not re-run in this research; planner should verify in
  pre-flight.

**Research date:** 2026-05-07
**Valid until:** 30 days from research (assuming no rapid PyPI
policy changes); refresh if Phase 12 starts after 2026-06-07 or
if the publish workflow is touched.
