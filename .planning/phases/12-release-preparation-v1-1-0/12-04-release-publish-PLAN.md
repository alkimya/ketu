---
phase: 12-release-preparation-v1-1-0
plan: 04
type: execute
wave: 2
depends_on:
  - 12-01
  - 12-02
  - 12-03
files_modified:
  - CHANGELOG.md     # date-stamp the [1.1.0] header (UNRELEASED -> YYYY-MM-DD)

autonomous: false

must_haves:
  truths:
    - "The CHANGELOG [1.1.0] header reads ## [1.1.0] - <YYYY-MM-DD> on the tagged commit (not UNRELEASED)"
    - "gsd/v1.1-milestone is merged to main BEFORE the v1.1.0 tag is pushed (RESEARCH §Pitfall 3)"
    - "git tag -a v1.1.0 is pushed and exists on a commit reachable from main"
    - "PyPI lists ketu 1.1.0 (https://pypi.org/project/ketu/1.1.0/) populated by the trusted-publishing OIDC workflow"
    - "GitHub release v1.1.0 is published with title and notes pointing at CHANGELOG and UPGRADING"
    - "pip install ketu==1.1.0 in a fresh venv reports __version__ == '1.1.0' and pytest passes the project test suite"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "Date-stamped v1.1.0 release entry"
      contains: "## [1.1.0] - 2026-"
    - path: "git tag v1.1.0"
      provides: "Annotated tag on a commit reachable from main; trigger for publish.yml"
      contains: "Release 1.1.0"
    - path: "https://pypi.org/project/ketu/1.1.0/"
      provides: "Published wheel + sdist on PyPI"
      contains: "ketu-1.1.0-py3-none-any.whl"
    - path: "GitHub release v1.1.0"
      provides: "User-visible release notes with CHANGELOG/UPGRADING links"
      contains: "Ketu 1.1.0"
  key_links:
    - from: "git tag v1.1.0 push"
      to: ".github/workflows/publish.yml (build + publish-to-pypi jobs)"
      via: "tag-trigger on push.tags ['v*.*.*'] -> OIDC trusted publish"
      pattern: "v1\\.1\\.0"
    - from: "publish.yml publish-to-pypi job"
      to: "PyPI ketu/1.1.0"
      via: "pypa/gh-action-pypi-publish@release/v1 in environment: pypi (id-token: write)"
      pattern: "trusted publishing"
    - from: "fresh-venv smoke test (post-publish)"
      to: "ketu.__version__ == '1.1.0'"
      via: "pip install ketu==1.1.0 + python -c 'import ketu; assert ketu.__version__ == \"1.1.0\"'"
      pattern: "ketu==1\\.1\\.0"
---

<objective>
Run the v1.1.0 release ceremony: pre-flight build/test, merge to main,
date-stamp CHANGELOG, tag, push tag, watch the trusted-publishing
workflow, create GitHub release, and verify post-publish with a
fresh-venv smoke install.

Purpose: Closes REL-04. PyPI is **unforgiving** — versions cannot be
deleted or republished. Every step here moves risk left into pre-flight
before the unrecoverable tag-push step. This plan is deliberately
human-in-loop with multiple checkpoints because (a) merge-to-main
needs PR review, (b) the tag push is irreversible, and (c) the
trusted-publishing workflow runs asynchronously on GitHub Actions and
needs human eyes during the few minutes it takes.

Output: ketu 1.1.0 on PyPI, v1.1.0 git tag on main, GitHub release v1.1.0
with notes, smoke-tested in a fresh venv. STATE.md updated to mark
Phase 12 complete and v1.1 milestone closed.

This plan does NOT add any new code. The ONLY file edit is the CHANGELOG
date-stamp (`UNRELEASED` -> `YYYY-MM-DD`), and that is committed on
`main` immediately before the tag.
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

@.github/workflows/publish.yml
@.github/workflows/tests.yml
@CHANGELOG.md
@pyproject.toml
@ketu/__init__.py
@MANIFEST.in
</context>

<tasks>

<task type="auto">
  <name>Task 1: Local pre-flight (build + twine check + fresh-venv smoke + PyPI availability)</name>
  <files>(no source edits; build artefacts in dist/ are transient)</files>
  <action>
This task is the entire pre-flight script from RESEARCH §Code Examples
"REL-04: Local pre-flight script", adapted for THIS environment. It
must run cleanly on `gsd/v1.1-milestone` HEAD (i.e., AFTER plans 12-01,
12-02, 12-03 have all landed). All sub-steps are idempotent and
non-destructive.

```bash
set -euo pipefail
VERSION="1.1.0"
cd /home/loc/workspace/ketu
source venv/bin/activate

# 1. Working tree must be clean (no uncommitted changes from 01/02/03)
test -z "$(git status --porcelain)" || {
  echo "ERROR: Working tree not clean. Resolve before pre-flight."
  git status --short
  exit 1
}

# 2. We are on gsd/v1.1-milestone (the merge to main happens in Task 2)
[ "$(git rev-parse --abbrev-ref HEAD)" = "gsd/v1.1-milestone" ] || {
  echo "ERROR: not on gsd/v1.1-milestone"
  exit 1
}

# 3. Confirm Plans 01..03 landed by spot-checking sentinel strings
grep -q '^version = "1.1.0"$' pyproject.toml             || { echo "12-01 not landed"; exit 1; }
grep -q '^__version__ = "1.1.0"$' ketu/__init__.py       || { echo "12-01 not landed"; exit 1; }
grep -q "^### BREAKING / Numerical Behavior Changes (Summary)$" CHANGELOG.md \
                                                         || { echo "12-02 not landed"; exit 1; }
grep -q "^## What's New in v1.1.0$" README.md            || { echo "12-02 not landed"; exit 1; }
grep -q "^### CLI Default Aspect Set " UPGRADING.md      || { echo "12-03 not landed"; exit 1; }
grep -q "^### Kala / Downstream Adapter Migration " UPGRADING.md || { echo "12-03 not landed"; exit 1; }

# 4. Full test suite (exact count goes into the GH release notes)
pytest tests/ -q | tee /tmp/ketu-12-04-pytest.log
TEST_COUNT=$(grep -E "^[0-9]+ passed" /tmp/ketu-12-04-pytest.log \
             | head -1 | awk '{print $1}')
echo "Tests passed: ${TEST_COUNT}"
[ -n "${TEST_COUNT}" ] && [ "${TEST_COUNT}" -ge 250 ] || {
  echo "ERROR: pytest count missing or below 250 (got '${TEST_COUNT}')"
  exit 1
}

# 5. mypy strict (release gate)
mypy ketu/ --strict

# 6. Build sdist + wheel
rm -rf dist/ build/ ketu.egg-info/
pip install --quiet --upgrade build twine
python -m build --sdist --wheel

# 7. Validate the artefacts (this is what publish.yml runs in CI)
python -m twine check dist/*
# Expect: PASSED for both sdist and wheel.

# 8. Fresh-venv install + smoke (the single most-effective release blocker)
TMP=$(mktemp -d)
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"
"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}', f'attr={ketu.__version__!r}'
assert m.version('ketu') == '${VERSION}', f'meta={m.version(\"ketu\")!r}'
from ketu import calculate_houses, HOUSES_DTYPE, house_of
from ketu.aspects.presets import CLASSICAL, EXTENDED
assert len(CLASSICAL) == 5, f'CLASSICAL len {len(CLASSICAL)}'
assert len(EXTENDED) == 14, f'EXTENDED len {len(EXTENDED)}'
print('Fresh-venv smoke: OK')
"
# CLI smoke (entry point repointed in 11-05)
"$TMP/bin/pip" install --quiet pytest pytest-cov numpy
"$TMP/bin/python" -m ketu --list-aspect-sets > /tmp/ketu-list-aspect-sets.txt
"$TMP/bin/python" -m ketu --list-house-systems > /tmp/ketu-list-house-systems.txt
grep -q "classical" /tmp/ketu-list-aspect-sets.txt
grep -q "placidus"  /tmp/ketu-list-house-systems.txt
rm -rf "$TMP"

# 9. PyPI availability — confirm 1.1.0 is NOT already taken (Pitfall 8)
python - <<'PY'
import urllib.request, json
data = json.loads(urllib.request.urlopen(
    'https://pypi.org/pypi/ketu/json', timeout=10).read())
versions = list(data['releases'].keys())
assert '1.1.0' not in versions, f'PyPI already has 1.1.0; existing versions: {versions}'
print(f'PyPI clear; latest existing version: {sorted(versions)[-1]}')
PY

# 10. Trusted publisher config sanity (Pitfall 9 — manual visual check)
echo "Visit https://pypi.org/manage/project/ketu/settings/publishing/"
echo "Confirm: Owner=alkimya, Repo=ketu, Workflow=publish.yml,"
echo "         Environment=pypi (matches v1.0 release)."
echo "If it doesn't match, STOP and fix before tagging."

# 11. Capture pre-flight artefacts for the SUMMARY
ls -la dist/ > /tmp/ketu-12-04-dist.txt
echo "Test count: ${TEST_COUNT}" > /tmp/ketu-12-04-preflight-summary.txt
shasum -a 256 dist/* >> /tmp/ketu-12-04-preflight-summary.txt
echo "Pre-flight: OK"
```

If ANY step fails, STOP. Diagnose. Re-run from step 1. Do NOT
proceed to Task 2.

Common fixes:
- twine check WARNING about README rendering -> fix README markdown
  (likely a stray `> [!NOTE]` or a code fence not closed). Fix on
  `gsd/v1.1-milestone`, commit as a `docs(12-04): pre-flight fix`
  patch, re-run pre-flight.
- Test failure -> a regression slipped in. Triage; if it's blocking,
  fix on `gsd/v1.1-milestone` and re-run pre-flight.
- PyPI 1.1.0 already exists -> serious. Visit pypi.org/project/ketu
  to check who/what published it. If a previous abandoned attempt
  reserved it, you must bump to `1.1.0.post1` or `1.1.1` (Pitfall 8) —
  this requires reverting Plan 12-01 and replanning.

Write the captured pre-flight summary
(`/tmp/ketu-12-04-preflight-summary.txt`) to the plan SUMMARY in
the final task — needed for audit and for the GH release notes
(test count + sha256 of artefacts).
  </action>
  <verify>
- All `set -euo pipefail` steps complete without error.
- `pytest tests/ -q` reports `<COUNT> passed` with COUNT >= 250.
- `mypy ketu/ --strict` reports `Success: no issues found`.
- `python -m twine check dist/*` reports `PASSED` on both files.
- Fresh-venv smoke prints `Fresh-venv smoke: OK`.
- `ketu --list-aspect-sets` and `ketu --list-house-systems` produce
  recognizable output (classical, placidus).
- `pip index versions ketu` (or the inline urllib check) confirms
  PyPI does NOT yet have 1.1.0.
- TEST_COUNT and dist/ sha256 captured to /tmp/ for the SUMMARY.
- Trusted publisher dashboard visually matches v1.0 config (manual).
  </verify>
  <done>
Build + tests + mypy + twine + fresh-venv smoke + PyPI availability all
green on `gsd/v1.1-milestone` HEAD. The `dist/` directory contains the
sdist and wheel that will be rebuilt identically in CI by `publish.yml`.
We are now safe to merge to main and tag.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: CHECKPOINT — Open PR gsd/v1.1-milestone -> main, wait for green CI, merge</name>
  <what-built>
Plans 12-01, 12-02, 12-03 are committed on `gsd/v1.1-milestone`. Local
pre-flight (Task 1) is green. The branch is ready to merge to `main`
so that the eventual v1.1.0 tag sits on a commit reachable from `main`
(per RESEARCH §Pitfall 3 — tag-on-feature-branch leaves the tagged
commit dangling after merge).

`tests.yml` does NOT trigger automatically on `gsd/v1.1-milestone`
(RESEARCH §Pitfall 7 — the workflow only runs on `main`/`develop`/PR
to main/manual). Opening the PR triggers PR-CI which is the gate we
rely on.
  </what-built>
  <how-to-verify>
1. Open the PR with the `gh` CLI (Claude does this automatically):

   ```bash
   gh pr create \
     --base main \
     --head gsd/v1.1-milestone \
     --title "Release v1.1.0: configurable aspects, houses module, Lilith fix, CLI refactor" \
     --body "$(cat <<'EOF'
## Summary

Closes the v1.1 milestone (Phases 8-12). Three breaking behavior
changes vs v1.0:
- **Lilith** (Mean Apogee) longitude formula corrected (~180 deg
  shift) — Phase 8.
- **CLI default** changed from EXTENDED (14 aspects) to CLASSICAL
  (5 majors) — Phase 9. Restore with `--harmonics extended`.
- **Houses** module replaces broken `calculate_house_cusps` — Phase 10.

Plus: argparse-based CLI with `ketu houses` and `ketu aspects`
subcommands, resolved-config stderr header, forward byte-stability
regression test (Phase 11).

See [CHANGELOG.md](CHANGELOG.md#110---unreleased) and
[UPGRADING.md](UPGRADING.md#v10---v11) for migration recipes.

## Test plan

- [x] `pytest tests/` green on milestone branch (724+ tests)
- [x] `mypy ketu/ --strict` clean
- [x] Local `python -m build` + `twine check dist/*` PASSED
- [x] Fresh-venv install of dist/ wheel: `ketu.__version__ == "1.1.0"`
- [x] `ketu --list-aspect-sets` and `ketu --list-house-systems` work
- [ ] CI workflow `tests.yml` matrix passes (Python 3.10, 3.11, 3.12, 3.13)
- [ ] CI mypy --strict passes (Python 3.11)
- [ ] CI coverage gate passes (>=70% project, >=95% houses)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
   ```

2. Wait for CI on the PR. Watch progress:
   ```bash
   gh pr checks --watch
   ```

3. Once all checks are green:
   ```bash
   gh pr view --json url,state,mergeable
   ```

4. Merge the PR. Choose merge strategy:
   - **Preferred**: fast-forward if `gsd/v1.1-milestone` is already
     rebased on top of `main` (linear history).
   - **Fallback**: standard merge commit. The merge commit will be the
     parent of the tag.

   ```bash
   # Try fast-forward; fall back to merge commit
   gh pr merge --merge --delete-branch=false
   # If you specifically want fast-forward:
   #   gh pr merge --rebase --delete-branch=false
   # Don't squash — we want the per-plan history preserved.
   ```

5. After merge, sync local main and verify:
   ```bash
   git checkout main
   git pull origin main
   git log --oneline -10        # see the v1.1 commits at the tip
   ```

6. **Sanity check** — the version-bump commit and the doc commits
   are now reachable from `main`:
   ```bash
   git log main --oneline | head -10
   grep '^version = "1.1.0"$' pyproject.toml
   ```

**STOP HERE if:**
- CI fails on the PR. Diagnose, fix on `gsd/v1.1-milestone`, push, wait.
- The PR cannot be merged (conflicts, etc.). Resolve by
  rebasing `gsd/v1.1-milestone` on `main`, force-push, re-run pre-flight.
- The trusted-publisher dashboard at
  https://pypi.org/manage/project/ketu/settings/publishing/
  doesn't list `alkimya/ketu` + `publish.yml` + `pypi` environment.
  Re-add it before tagging — otherwise OIDC publish will fail.

**Resume after:** PR is merged, `git checkout main && git pull` shows
v1.1 commits at HEAD, CI is green on `main`.
  </how-to-verify>
  <resume-signal>
Type `merged` once the PR is merged to main and `git checkout main &&
git pull` shows the v1.1 commits at HEAD with green CI. If anything
above failed, type `failed: <description>` and Claude will diagnose.
  </resume-signal>

  <files>(no source edits in this checkpoint task; see Tasks 1, 3, 5 of this plan for the file edits this checkpoint gates)</files>
  <action>See <how-to-verify> above. This is a human-in-loop checkpoint: Claude has automated everything it can; the resume-signal below tells Claude when to proceed.</action>
  <verify>See <how-to-verify> above. The user types the resume-signal once the listed checks all pass.</verify>
  <done>PR is merged to main, `git checkout main && git pull` shows v1.1 commits at HEAD with green CI.</done>
</task>

<task type="auto">
  <name>Task 3: Date-stamp CHANGELOG on main (last commit before tag)</name>
  <files>CHANGELOG.md</files>
  <action>
This task runs **on `main`**, AFTER Task 2's merge has landed. It
replaces the `UNRELEASED` placeholder with today's date so the
v1.1.0 tag points at a commit whose CHANGELOG says
`## [1.1.0] - YYYY-MM-DD` (RESEARCH §Pitfall 2 — UNRELEASED tag never
replaced).

```bash
set -euo pipefail
cd /home/loc/workspace/ketu
git checkout main
git pull origin main

TODAY=$(date -u +%Y-%m-%d)

# Sanity: the [1.1.0] - UNRELEASED line is exactly where 12-02 left it
grep -nq '^## \[1.1.0\] - UNRELEASED$' CHANGELOG.md || {
  echo "ERROR: cannot find '## [1.1.0] - UNRELEASED' in CHANGELOG.md"
  echo "If 12-02 used different formatting, locate manually before"
  echo "running this Edit."
  exit 1
}

# Replace UNRELEASED with the date (single occurrence by design)
# Use sed -i carefully; alternatively use the Edit tool.
sed -i "s/^## \[1\.1\.0\] - UNRELEASED$/## [1.1.0] - ${TODAY}/" CHANGELOG.md

# Verify the substitution worked
grep -q "^## \[1.1.0\] - ${TODAY}$" CHANGELOG.md
! grep -q "^## \[1.1.0\] - UNRELEASED$" CHANGELOG.md

# Optional French mirror — only if it exists and references UNRELEASED
if [ -f fr/CHANGELOG.md ] && grep -q '^## \[1.1.0\] - UNRELEASED$' fr/CHANGELOG.md; then
  sed -i "s/^## \[1\.1\.0\] - UNRELEASED$/## [1.1.0] - ${TODAY}/" fr/CHANGELOG.md
  echo "fr/CHANGELOG.md also date-stamped"
fi

# Commit (this is the LAST commit before tagging)
node ./.claude/get-shit-done/bin/gsd-tools.js commit \
  "docs(release): set v1.1.0 release date ${TODAY}" \
  --files CHANGELOG.md ${UPDATE_FR:+fr/CHANGELOG.md}

# Push to main
git push origin main

# Verify push landed
git log -1 --oneline
git diff origin/main HEAD   # expect: empty (we just pushed)
```

If `fr/CHANGELOG.md` does not exist or does not reference
UNRELEASED, the second `sed` is skipped. If it does exist, it gets
the same treatment in the same commit. Use whichever path the
script reports.

**Why this is its own commit:** the `UNRELEASED` -> date substitution
is the kind of edit that's easy to forget, and isolating it makes
post-mortem audit trivial: "what was the LAST commit before tag
v1.1.0? Answer: the date stamp." Plus the date stamp shouldn't be
on `gsd/v1.1-milestone` because that branch was authored over multiple
days; only the post-merge commit knows the real release date.
  </action>
  <verify>
- `grep -q "^## \[1.1.0\] - 2026-" CHANGELOG.md` succeeds.
- `! grep -q "^## \[1.1.0\] - UNRELEASED$" CHANGELOG.md` succeeds (no
  UNRELEASED in the v1.1 header).
- `git log -1 --pretty=format:'%s'` shows
  `docs(release): set v1.1.0 release date <YYYY-MM-DD>`.
- `git rev-parse HEAD` matches `git rev-parse origin/main` (push landed).
- `git show --stat HEAD` lists CHANGELOG.md (and fr/CHANGELOG.md if
  applicable) and nothing else.
  </verify>
  <done>
CHANGELOG.md `[1.1.0]` header is date-stamped on `main`, committed, and
pushed. The next commit on `main` will be the v1.1.0 tag.
  </done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 4: CHECKPOINT — Tag v1.1.0, push tag, watch publish.yml</name>
  <what-built>
`main` HEAD now has:
- Version 1.1.0 in both `pyproject.toml` and `ketu/__init__.py` (12-01).
- Complete CHANGELOG and updated README (12-02).
- Complete UPGRADING.md (12-03).
- Date-stamped `[1.1.0] - YYYY-MM-DD` header (Task 3).

The next action — pushing the annotated tag `v1.1.0` — triggers the
trusted-publishing workflow `.github/workflows/publish.yml`. PyPI is
**unforgiving**: if the workflow fails after the upload step, the
version is burned; if before, the tag can be deleted and re-pushed.
This is a human-in-loop step because tag pushing has irreversible
PyPI consequences.

Trusted publishing requirements (already configured per Phase 7):
- Workflow file: `.github/workflows/publish.yml`
- Environment: `pypi`
- `permissions.id-token: write` at the publish job
- PyPI dashboard: Owner=`alkimya`, Repo=`ketu`, Workflow=`publish.yml`,
  Environment=`pypi`
  </what-built>
  <how-to-verify>
This is the irreversible step. Read every line below before acting.

1. Confirm position:
   ```bash
   cd /home/loc/workspace/ketu
   [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || { echo "Not on main"; exit 1; }
   git pull origin main
   git log -1 --pretty='%H %s'
   # Expect the previous commit subject:
   #   docs(release): set v1.1.0 release date YYYY-MM-DD
   ```

2. Confirm 1.1.0 is still NOT on PyPI (Pitfall 8 last-chance check):
   ```bash
   curl -s https://pypi.org/pypi/ketu/json | python -c "
   import json, sys
   data = json.load(sys.stdin)
   assert '1.1.0' not in data['releases'], 'PyPI already has 1.1.0!'
   print('PyPI clear, latest:', sorted(data['releases'].keys())[-1])
   "
   ```

3. Create the annotated tag and push:
   ```bash
   git tag -a v1.1.0 -m "Release 1.1.0 - configurable aspects, houses module, Lilith fix, CLI refactor"
   git push origin v1.1.0
   ```

   This is the irreversible step. The push triggers
   `.github/workflows/publish.yml` (build job + publish-to-pypi job).

4. Watch the workflow run. Open in a terminal:
   ```bash
   gh run watch
   # OR pick the most recent publish.yml run:
   gh run list --workflow publish.yml --limit 1
   gh run watch $(gh run list --workflow publish.yml --limit 1 --json databaseId --jq '.[0].databaseId')
   ```

   Expected timeline (~3-7 minutes total):
   - `build` job: checkout -> Python 3.11 -> `python -m build --sdist
     --wheel` -> `twine check dist/*` (PASSED) -> upload artifact.
   - `publish-to-pypi` job (needs `build`, runs in `environment: pypi`):
     download artifact -> `pypa/gh-action-pypi-publish@release/v1`
     OIDC handshake -> upload to PyPI -> done.

5. Once `publish-to-pypi` is green, verify on PyPI:
   ```bash
   curl -s https://pypi.org/pypi/ketu/1.1.0/json | python -c "
   import json, sys
   data = json.load(sys.stdin)
   urls = data['urls']
   print('PyPI 1.1.0:', [u['filename'] for u in urls])
   assert any(u['filename'].endswith('.whl') for u in urls), 'no wheel'
   assert any(u['filename'].endswith('.tar.gz') for u in urls), 'no sdist'
   print('OK')
   "
   ```

   Expect: a wheel `ketu-1.1.0-py3-none-any.whl` and an sdist
   `ketu-1.1.0.tar.gz` are listed.

6. Visit https://pypi.org/project/ketu/1.1.0/ in a browser and
   confirm the README "What's New in v1.1.0" banner renders correctly.

**FAILURE PLAYBOOK**

- If `build` fails (rare; pre-flight should have caught this):
  - PyPI never received the upload. Tag can be safely deleted:
    `git push --delete origin v1.1.0 && git tag -d v1.1.0`.
  - Fix the issue on `main`, re-run from Task 1.

- If `publish-to-pypi` fails with "OIDC token verification failed"
  or "trust" error:
  - This is RESEARCH §Pitfall 9 (publisher misconfigured).
  - PyPI did NOT accept the upload, so the version is NOT burned.
  - Visit https://pypi.org/manage/project/ketu/settings/publishing/
    and verify Owner/Repo/Workflow/Environment exactly match.
  - Fix the dashboard, then re-run the workflow:
    `gh run rerun <run-id>` (no need to delete the tag).

- If `publish-to-pypi` fails with "File already exists" (Pitfall 8):
  - PyPI accepted the upload but the workflow blew up partway. The
    version is BURNED. Bump to 1.1.0.post1 or 1.1.1 (replan 12-01,
    12-04 with the new version).

**Resume only when:** the `publish-to-pypi` job is green AND PyPI
shows `ketu-1.1.0-py3-none-any.whl` and `ketu-1.1.0.tar.gz`.
  </how-to-verify>
  <resume-signal>
Type `published` once `gh run list --workflow publish.yml` shows the
v1.1.0 run as `success` and `pip install ketu==1.1.0` is available
from PyPI. If something failed, type `failed: <run-id> <error
summary>` and Claude will follow the failure playbook above.
  </resume-signal>

  <files>(no source edits in this checkpoint task; see Tasks 1, 3, 5 of this plan for the file edits this checkpoint gates)</files>
  <action>See <how-to-verify> above. This is a human-in-loop checkpoint: Claude has automated everything it can; the resume-signal below tells Claude when to proceed.</action>
  <verify>See <how-to-verify> above. The user types the resume-signal once the listed checks all pass.</verify>
  <done>v1.1.0 git tag is on a commit reachable from main, the publish.yml workflow's publish-to-pypi job is green, and PyPI lists ketu-1.1.0 wheel + sdist.</done>
</task>

<task type="auto">
  <name>Task 5: Create GitHub release v1.1.0 + post-publish smoke test</name>
  <files>(no source edits; gh release + smoke install)</files>
  <action>
This task runs AFTER Task 4 confirms PyPI publish succeeded.

1. Extract the v1.1.0 changelog body for the GH release notes
   (everything between `## [1.1.0]` and the next `## [`):
   ```bash
   cd /home/loc/workspace/ketu
   awk '
     /^## \[1\.1\.0\]/        { p=1; next }
     /^## \[/ && p             { exit }
     p                         { print }
   ' CHANGELOG.md > /tmp/ketu-1.1.0-notes.md

   # Sanity: file is non-empty
   [ -s /tmp/ketu-1.1.0-notes.md ] || { echo "extracted notes empty"; exit 1; }
   wc -l /tmp/ketu-1.1.0-notes.md
   ```

2. Prepend a one-paragraph release intro to the extracted notes:
   ```bash
   cat > /tmp/ketu-1.1.0-release.md <<'EOF'
Ketu 1.1.0 introduces configurable aspect sets (5 majors by default,
opt-in `EXTENDED` for the legacy 14), a new `ketu.houses` module
(Placidus / Koch / Porphyry / Equal / Whole-sign with polar
fallback), a corrected Lilith Mean Apogee formula matching Swiss
Ephemeris to better than 0.01 deg, and an argparse-based CLI with
`ketu houses` and `ketu aspects` subcommands plus introspection
flags.

This is a feature release with **two breaking behavior changes**
from v1.0 (Lilith longitudes shift by ~180 deg, CLI default emits
5 aspects instead of 14). See [UPGRADING.md] for migration recipes.

- [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md#110)
- [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v10---v11)
- `pip install ketu==1.1.0`

---

EOF
   cat /tmp/ketu-1.1.0-notes.md >> /tmp/ketu-1.1.0-release.md
   ```

3. Create the GitHub release. The tag already exists (Task 4); use
   `gh release create` with the existing tag:
   ```bash
   gh release create v1.1.0 \
     --title "Ketu 1.1.0 - Configurable aspects, houses module, Lilith correction" \
     --notes-file /tmp/ketu-1.1.0-release.md \
     --verify-tag
   ```

   Expect: a URL like https://github.com/alkimya/ketu/releases/tag/v1.1.0
   in the gh CLI output.

4. Verify the GH release:
   ```bash
   gh release view v1.1.0 --json url,tagName,name,body
   ```
   Expect: `tagName == "v1.1.0"`, `name` contains "Ketu 1.1.0", body
   non-empty.

5. **Post-publish smoke test from PyPI in a fresh venv** (the final
   gate — proves users can actually install):
   ```bash
   POST_TMP=$(mktemp -d)
   python -m venv "$POST_TMP"
   "$POST_TMP/bin/pip" install --quiet --no-cache-dir "ketu==1.1.0"
   "$POST_TMP/bin/python" -c "
   import ketu, importlib.metadata as m
   assert ketu.__version__ == '1.1.0', f'attr={ketu.__version__!r}'
   assert m.version('ketu') == '1.1.0', f'meta={m.version(\"ketu\")!r}'
   from ketu import calculate_houses, HOUSES_DTYPE, house_of
   from ketu.aspects.presets import CLASSICAL, EXTENDED
   assert len(CLASSICAL) == 5
   assert len(EXTENDED) == 14
   print('Post-publish smoke (PyPI install): OK')
   "

   # Optional but recommended: run the project test suite from the
   # PyPI-installed wheel against this repo's tests/.
   "$POST_TMP/bin/pip" install --quiet pytest pytest-cov numpy
   "$POST_TMP/bin/pytest" tests/ -q --no-cov 2>&1 | tail -5

   rm -rf "$POST_TMP"
   ```

   This satisfies REL-04 success criterion 4: "User runs
   `pip install ketu==1.1.0` from PyPI in a fresh venv and the test
   suite passes (250+ tests, mypy strict)".

   Note: `numpydoc validate` and `interrogate ≥95%` from the ROADMAP
   success criterion are **out of scope** per RESEARCH §Out of Scope —
   neither is wired into CI; document the gap in the SUMMARY.

6. Capture the smoke-install transcript for the SUMMARY.

If anything in this task fails:
- GH release creation failure: re-run `gh release create` with same
  args (idempotent if no partial release was created; otherwise use
  `gh release edit v1.1.0`).
- Fresh-venv smoke failure (e.g., import error): the published wheel
  has a defect. This is a CRITICAL post-publish state. Plan an
  immediate `1.1.1` patch release; do NOT yank 1.1.0 unless it is
  unequivocally broken (yanking is a heavy-handed PyPI action).
  </action>
  <verify>
- `/tmp/ketu-1.1.0-notes.md` extracted from CHANGELOG.md is non-empty
  and contains the BREAKING summary (sentinel:
  `grep -q "EXTENDED (14) -> CLASSICAL (5)" /tmp/ketu-1.1.0-notes.md`).
- `gh release view v1.1.0` returns success with `name` non-empty.
- Visit https://github.com/alkimya/ketu/releases/tag/v1.1.0 and
  confirm the page renders.
- Fresh venv install of `ketu==1.1.0` from PyPI prints
  `Post-publish smoke (PyPI install): OK`.
- Optional `pytest tests/` from the fresh venv reports >=250 tests
  passing.
  </verify>
  <done>
GitHub release v1.1.0 is published with notes extracted from
CHANGELOG.md. PyPI install in a fresh venv reports
`__version__ == '1.1.0'` and the test suite passes. REL-04 closed.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 6: CHECKPOINT — End-to-end user-facing verification</name>
  <what-built>
The full release ceremony is complete:
- v1.1.0 tag on `main`, reachable from `main`.
- ketu 1.1.0 on PyPI with sdist + wheel.
- GitHub release v1.1.0 with notes pointing at CHANGELOG and UPGRADING.
- Fresh-venv smoke install verified.

This last checkpoint is the user putting on a v1.0-user hat and
walking through the migration recipes from UPGRADING.md, end-to-end,
to make sure the released artefact actually serves the documented
upgrade path.
  </what-built>
  <how-to-verify>
1. Open https://pypi.org/project/ketu/1.1.0/ in a browser.
   - The README banner says "What's New in v1.1.0".
   - The PyPI sidebar shows version 1.1.0 as the latest.
   - The "Project links" section is intact.

2. Open https://github.com/alkimya/ketu/releases/tag/v1.1.0 and
   confirm the release notes render (no broken links, no raw
   markdown showing).

3. Pretend to be a v1.0 user. In a clean shell:
   ```bash
   FRESH=$(mktemp -d) && python -m venv "$FRESH" && \
     "$FRESH/bin/pip" install --quiet "ketu==1.1.0"

   # Recipe from UPGRADING.md "CLI Default Aspect Set":
   "$FRESH/bin/python" -m ketu --harmonics extended aspects --date 2000-01-01T12:00:00Z 2>/dev/null | wc -l
   # Expect: a number reflecting 14 aspects per body pair (~52 lines).

   "$FRESH/bin/python" -m ketu --list-aspect-sets
   # Expect: classical, traditional, extended, all (4 presets).

   "$FRESH/bin/python" -m ketu --list-house-systems
   # Expect: placidus, koch, porphyry (or full set including equal,
   #         whole_sign — see what's actually wired).

   # Recipe from UPGRADING.md "Houses Module":
   "$FRESH/bin/python" -c "
   from ketu import calculate_houses
   import numpy as np
   r = calculate_houses(2451545.0, 48.85, 2.35, system='placidus')
   print('cusps:', r['cusps'])
   "
   # Expect: 12 floats representing house cusps in degrees.

   rm -rf "$FRESH"
   ```

4. Update STATE.md to mark Phase 12 closed and v1.1 milestone complete:
   ```bash
   cd /home/loc/workspace/ketu
   git checkout main
   # Edit STATE.md "Current Position" to:
   #   Phase: 12 of 12 (Release Preparation v1.1.0) — COMPLETE
   #   Plan: 4 of 4 complete
   #   v1.1.0 published to PyPI on YYYY-MM-DD; GitHub release v1.1.0 live.
   # Edit STATE.md "Last activity" to today's date with the publish
   # confirmation.
   git add .planning/STATE.md
   git commit -m "docs(state): close Phase 12 (v1.1.0 released)"
   git push origin main
   ```

5. Final sanity:
   ```bash
   git tag --contains main | grep -q '^v1.1.0$'
   ```
   Tag is reachable from main. Pitfall 3 averted.

**Resume after**: all the above checks pass; STATE.md is updated and
pushed; the user has visually confirmed the PyPI page and GitHub
release page render correctly.
  </how-to-verify>
  <resume-signal>
Type `released` once you have visually confirmed PyPI 1.1.0 and the
GitHub release page, run the migration recipes from a fresh venv
and they work, and STATE.md is updated and pushed. If any user-facing
artefact is broken, type `broken: <description>` and Claude will
diagnose (likely path: a 1.1.1 patch).
  </resume-signal>

  <files>(no source edits in this checkpoint task; see Tasks 1, 3, 5 of this plan for the file edits this checkpoint gates)</files>
  <action>See <how-to-verify> above. This is a human-in-loop checkpoint: Claude has automated everything it can; the resume-signal below tells Claude when to proceed.</action>
  <verify>See <how-to-verify> above. The user types the resume-signal once the listed checks all pass.</verify>
  <done>PyPI 1.1.0 page and GH release v1.1.0 page render correctly; UPGRADING.md migration recipes work end-to-end from a fresh-venv install; STATE.md is updated and pushed marking Phase 12 closed.</done>
</task>

</tasks>

<verification>
Phase-level verification of REL-04 after Plan 12-04:

```bash
# Tag exists and is on main
git tag --list v1.1.0
git tag --contains main | grep -q '^v1.1.0$'

# PyPI shows 1.1.0
curl -s https://pypi.org/pypi/ketu/1.1.0/json | python -c "
import json, sys
data = json.load(sys.stdin)
assert any(u['filename'].endswith('.whl') for u in data['urls'])
print('PyPI 1.1.0: published')
"

# GitHub release exists
gh release view v1.1.0 --json tagName,name | grep -q v1.1.0

# Fresh venv install works
T=$(mktemp -d) && python -m venv "$T" && "$T/bin/pip" install --quiet ketu==1.1.0 && \
  "$T/bin/python" -c "import ketu; assert ketu.__version__ == '1.1.0'; print('OK')" && \
  rm -rf "$T"

# CHANGELOG date stamp landed (not UNRELEASED)
git show main:CHANGELOG.md | grep -q '^## \[1.1.0\] - 2026-'
! git show main:CHANGELOG.md | grep -q '^## \[1.1.0\] - UNRELEASED$'

# STATE.md marks Phase 12 closed
git show main:.planning/STATE.md | grep -q "Phase: 12.*COMPLETE\|Phase 12.*closed"
```
</verification>

<success_criteria>
- v1.1.0 git tag exists on a commit reachable from `main`.
- ketu 1.1.0 is published on PyPI with sdist + wheel.
- GitHub release v1.1.0 is live with notes extracted from CHANGELOG.
- `pip install ketu==1.1.0` in a fresh venv: `__version__ == "1.1.0"`,
  imports succeed, presets have correct lengths, project tests pass.
- CHANGELOG.md `[1.1.0]` is date-stamped on `main`.
- STATE.md is updated to mark Phase 12 closed and v1.1 milestone
  complete.
- Out-of-scope items (interrogate, numpydoc, fr/CHANGELOG mirror if
  absent) are documented as gaps in the SUMMARY, not blockers.
- REL-04 closed.
</success_criteria>

<output>
After completion, create `.planning/phases/12-release-preparation-v1-1-0/12-04-SUMMARY.md`
including:
- Pre-flight artefact summary (`/tmp/ketu-12-04-preflight-summary.txt`):
  test count, sha256 of dist/*.whl and dist/*.tar.gz.
- Merge commit hash on main (Task 2).
- Date-stamp commit hash on main (Task 3).
- v1.1.0 tag commit hash and the GH Actions run URL.
- PyPI URL https://pypi.org/project/ketu/1.1.0/ and the wheel filename.
- GitHub release URL.
- Post-publish smoke test transcript snippet.
- Out-of-scope items confirmed as gaps:
  - `interrogate` not installed/configured (RESEARCH §Out of Scope).
  - `numpydoc validate` not wired into CI.
  - `fr/CHANGELOG.md` date-stamped or skipped.
- Any deviations or post-mortem notes (e.g., a workflow rerun was
  needed; Pitfall 8 vs 9 was hit; etc.).
</output>
