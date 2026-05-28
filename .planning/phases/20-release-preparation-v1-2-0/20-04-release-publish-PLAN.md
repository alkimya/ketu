---
phase: 20-release-preparation-v1-2-0
plan: 04
type: execute
wave: 3
depends_on: ["20-01", "20-02", "20-03"]
files_modified:
  - CHANGELOG.md
  - fr/CHANGELOG.md
autonomous: false
user_setup:
  - service: pypi
    why: "PyPI OIDC trusted publishing target for ketu==1.2.0 (already configured externally — verification only, no token needed)"
    dashboard_config:
      - task: "Confirm trusted publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi"
        location: "https://pypi.org/manage/project/ketu/settings/publishing/"

must_haves:
  truths:
    - "Local pre-flight passes: clean tree, version synced, CHANGELOG dated, numpydoc clean, build + twine check green, fresh-venv smoke-imports all v1.2 subpackages"
    - "v1.2.0 git tag exists on main and is pushed"
    - "publish.yml runs on the tag, builds sdist+wheel, publishes ketu==1.2.0 to PyPI via OIDC"
    - "GitHub release v1.2.0 exists with sdist + wheel attached"
    - "Fresh-venv 'pip install ketu==1.2.0' from PyPI smoke-imports cleanly (ketu.__version__ == '1.2.0' and all new subpackages import)"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "[1.2.0] entry with the FINAL release date"
      contains: "## [1.2.0] -"
  key_links:
    - from: "git tag v1.2.0 on main"
      to: "publish.yml workflow"
      via: "on.push.tags: ['v*.*.*'] trigger"
      pattern: "v1\\.2\\.0"
    - from: "publish.yml OIDC job"
      to: "PyPI ketu project"
      via: "trusted publishing (id-token: write, environment: pypi)"
      pattern: "gh-action-pypi-publish"
---

<objective>
Run the v1.2.0 release ceremony: full local pre-flight, a HUMAN
go/no-go checkpoint (the next step pushes a tag that IRREVERSIBLY
publishes to PyPI), then tag + push + GitHub release, then verify the
published artifact installs from PyPI in a clean venv (OPS-05).

Purpose: publishing to PyPI is permanent — a version number can never be
reused. Every gate must be green and a human must explicitly approve
before the tag is pushed. This plan automates everything up to and after
the push, and gates the push itself on user confirmation.
Output: ketu==1.2.0 live on PyPI, GitHub release v1.2.0 with sdist+wheel,
verified clean install.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/20-release-preparation-v1-2-0/20-RESEARCH.md
@.github/workflows/publish.yml
@CHANGELOG.md
@pyproject.toml
@ketu/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Date-stamp the release and run the full local pre-flight</name>
  <files>CHANGELOG.md, fr/CHANGELOG.md</files>
  <action>
    1. Determine the actual release date (today, UTC). If it differs from
       the date plan 20-03 wrote in the `## [1.2.0] - YYYY-MM-DD` headers,
       update BOTH `CHANGELOG.md` and `fr/CHANGELOG.md` to the real release
       date. The header must be a real date — NEVER "UNRELEASED" (research
       Pitfall 5).
    2. Run the pre-flight (adapted from 20-RESEARCH.md "Pre-flight Script",
       VERSION=1.2.0). Each step is a hard gate — STOP on first failure:
       a. Working tree: if anything is uncommitted that should be part of
          the release, ensure 20-01/20-02/20-03 commits + this date-stamp
          are committed to main. (Tag must point at a commit that contains
          all release artifacts.)
       b. Version sync: `grep version pyproject.toml` + `__init__.py` both
          "1.2.0"; `pip install -e . -q && pytest tests/test_version.py -v`.
       c. CHANGELOG dated: `grep -q '^## \[1.2.0\] - 20' CHANGELOG.md` and
          NOT `UNRELEASED`.
       d. numpydoc clean (gate from 20-02):
          `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")`
          — zero violations. `python -m interrogate ketu/` — 100%.
       e. Full suite: `pytest tests/ -q` — all pass. `mypy ketu/ --strict`.
       f. Build: `rm -rf dist build ketu.egg-info && python -m build --sdist --wheel`.
       g. `pip install -q twine && python -m twine check dist/*` — PASSED.
       h. Fresh-venv smoke test of the WHEEL:
          ```
          TMP=$(mktemp -d); python -m venv "$TMP"
          "$TMP/bin/pip" install -q dist/ketu-1.2.0-py3-none-any.whl
          "$TMP/bin/python" -c "import ketu; assert ketu.__version__=='1.2.0'"
          "$TMP/bin/python" -c "from ketu.synastry import calculate_synastry"
          "$TMP/bin/python" -c "from ketu.composite import calculate_composite"
          "$TMP/bin/python" -c "from ketu.returns import solar_return"
          "$TMP/bin/python" -c "from ketu.parts import calculate_part"
          "$TMP/bin/python" -c "from ketu import calculate_houses; calculate_houses(2451545.0,48.85,2.35,system='whole_sign')"
          rm -rf "$TMP"
          ```
       i. PyPI clear: query https://pypi.org/pypi/ketu/json and assert
          '1.2.0' not in releases.
       j. sdist contents: `tar -tzf dist/ketu-1.2.0.tar.gz | grep fr/CHANGELOG.md`
          — confirms the generated French changelog ships.
    3. Pre-flight: also verify branch is `main` and `git log --oneline -5`
       shows the version-bump + changelog commits.

    Report the pre-flight result clearly. If ANY step fails, do NOT proceed
    to Task 2 — surface the failure for fixing.
  </action>
  <verify>
    All pre-flight gates pass; `dist/ketu-1.2.0-py3-none-any.whl` and
    `dist/ketu-1.2.0.tar.gz` exist and `twine check` is green; fresh-venv
    smoke-import of all v1.2 subpackages succeeds; PyPI confirms 1.2.0 is
    not yet published; CHANGELOG + fr/CHANGELOG dated with the real date.
  </verify>
  <done>
    Release is build-verified locally: version synced, all gates green,
    wheel installs and imports cleanly in a fresh venv, PyPI slot is free,
    both changelogs carry the final release date.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Human go/no-go before irreversible PyPI publish</name>
  <action>
    PAUSE for explicit human approval. Present the Task 1 pre-flight result
    and the trusted-publisher confirmation, then wait. Do NOT push the tag
    until the user replies "approved". See what-built / how-to-verify below.
  </action>
  <what-built>
    A fully pre-flighted v1.2.0 release candidate: version 1.2.0 synced in
    pyproject.toml + ketu/__init__.py, dated [1.2.0] CHANGELOG (EN + FR),
    additive UPGRADING/README, Node-24 workflows, blocking numpydoc gate,
    a locally-built + twine-checked sdist+wheel that smoke-imports cleanly
    in a fresh venv, and a confirmed-free PyPI 1.2.0 slot.
  </what-built>
  <how-to-verify>
    This is the point of no return. Pushing the tag triggers publish.yml
    which IRREVERSIBLY publishes ketu==1.2.0 to PyPI — a version number can
    never be reused or unpublished-and-replaced.

    Before approving, confirm:
    1. The pre-flight output from Task 1 shows EVERY gate PASSED (version
       sync, tests, numpydoc clean, twine check, fresh-venv smoke import,
       PyPI slot free).
    2. The PyPI trusted publisher is configured (one-time, external — should
       already exist from v1.0/v1.1): visit
       https://pypi.org/manage/project/ketu/settings/publishing/ and confirm
       Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi.
    3. You are publishing from `main` and the CHANGELOG date is correct.

    Reply "approved" to push the v1.2.0 tag and publish. Reply with any
    concern to halt — nothing irreversible has happened yet.
  </how-to-verify>
  <resume-signal>Type "approved" to tag + push + publish, or describe what to fix.</resume-signal>
</task>

<task type="auto">
  <name>Task 2: Tag, push, create GitHub release, and verify the PyPI install</name>
  <files></files>
  <action>
    Only after the human approves the checkpoint.
    1. Tag on main:
       `git tag -a v1.2.0 -m "Release 1.2.0 — Synastry, Composite, Returns, Arabic Parts, 3 new house systems"`
    2. Push the tag: `git push origin v1.2.0`. This triggers publish.yml
       (build job -> publish-to-pypi job via OIDC).
    3. Watch the workflow to completion:
       `gh run watch $(gh run list --workflow=publish.yml --limit 1 --json databaseId -q '.[0].databaseId')`
       (or `gh run list --workflow=publish.yml` then `gh run watch <id>`).
       It must finish SUCCESS. If it fails, capture logs
       (`gh run view <id> --log-failed`) and surface — do NOT re-tag the
       same version (the slot may be partially consumed); diagnose first.
    4. Create the GitHub release attaching the locally-built artifacts
       (so sdist + wheel are on the release page per OPS-05):
       ```
       gh release create v1.2.0 \
         --title "Ketu 1.2.0 — Synastry, Composite, Returns, Arabic Parts, 3 new house systems" \
         --notes "<additive summary: 5 new subpackages + 3 house systems, no breaking changes; links to CHANGELOG #120 and UPGRADING #v11---v12; pip install ketu==1.2.0>" \
         dist/ketu-1.2.0-py3-none-any.whl dist/ketu-1.2.0.tar.gz
       ```
       (Use the release-notes template in 20-RESEARCH.md as the body. Keep
       it additive-only — no breaking-change language.)
    5. POST-PUBLISH verification — fresh venv installing FROM PyPI (may
       need a short retry loop while PyPI's CDN propagates):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q "ketu==1.2.0"
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.2.0'==m.version('ketu')"
       "$TMP/bin/python" -c "from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu import calculate_houses; print('PyPI smoke OK')"
       rm -rf "$TMP"
       ```
    6. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.
    Report: PyPI URL, GitHub release URL, and the smoke-test result.
  </action>
  <verify>
    `git tag -l v1.2.0` shows the tag; `gh run list --workflow=publish.yml`
    shows the latest run SUCCESS; `gh release view v1.2.0` lists both
    `ketu-1.2.0-py3-none-any.whl` and `ketu-1.2.0.tar.gz` assets;
    PyPI JSON API includes 1.2.0; the fresh-venv `pip install ketu==1.2.0`
    + smoke import succeeds with `__version__ == metadata.version == "1.2.0"`.
  </verify>
  <done>
    v1.2.0 tagged on main and pushed; publish.yml succeeded; ketu==1.2.0 is
    live on PyPI; GitHub release v1.2.0 has sdist + wheel attached;
    fresh-venv install from PyPI smoke-imports all v1.2 subpackages cleanly.
  </done>
</task>

</tasks>

<verification>
- Pre-flight all-green before any irreversible action (Task 1).
- Human approval recorded before tag push (checkpoint).
- `git tag -l v1.2.0` present and pushed.
- `gh run list --workflow=publish.yml` latest run = SUCCESS.
- `gh release view v1.2.0` shows sdist + wheel assets.
- PyPI: `pip install ketu==1.2.0` in a clean venv -> import OK,
  `ketu.__version__ == importlib.metadata.version("ketu") == "1.2.0"`,
  all five new subpackages import.
</verification>

<success_criteria>
- ketu==1.2.0 published to PyPI via OIDC trusted publishing (phase success
  criterion #5 / OPS-05).
- GitHub release v1.2.0 attaches sdist + wheel.
- Fresh-venv install from PyPI smoke-imports cleanly.
- No irreversible action taken without the explicit human go/no-go.
</success_criteria>

<output>
After completion, create
`.planning/phases/20-release-preparation-v1-2-0/20-04-SUMMARY.md`
</output>
