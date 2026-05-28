---
phase: 20-release-preparation-v1-2-0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .github/workflows/tests.yml
  - .github/workflows/publish.yml
autonomous: true

must_haves:
  truths:
    - "tests.yml and publish.yml pin actions/checkout@v5, actions/setup-python@v6"
    - "publish.yml pins actions/upload-artifact@v5 AND actions/download-artifact@v5 (matched pair)"
    - "No workflow step references a Node-20 action major version (checkout@v4, setup-python@v5, upload-artifact@v4, download-artifact@v4, codecov-action@v4)"
  artifacts:
    - path: ".github/workflows/tests.yml"
      provides: "Node-24 action pins for the test matrix workflow"
      contains: "actions/checkout@v5"
    - path: ".github/workflows/publish.yml"
      provides: "Node-24 action pins for the build+publish workflow"
      contains: "actions/upload-artifact@v5"
  key_links:
    - from: "publish.yml build job"
      to: "publish.yml publish-to-pypi job"
      via: "matched artifact format"
      pattern: "actions/(upload|download)-artifact@v5"
---

<objective>
Bump all GitHub Actions to their Node.js-24 major versions across both
workflow files, clearing every Node-20 deprecation warning (OPS-03).

Purpose: GitHub deprecates Node-20 action runtimes; v1.2.0 must publish
on a green, warning-free CI. This is pure YAML editing with zero code
risk and is the lowest-risk plan of the phase — runs in Wave 1 parallel
with 20-02.
Output: Updated `.github/workflows/tests.yml` and
`.github/workflows/publish.yml` with all actions on Node-24 majors.
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
@.github/workflows/tests.yml
@.github/workflows/publish.yml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Bump actions in tests.yml to Node-24 majors</name>
  <files>.github/workflows/tests.yml</files>
  <action>
    Edit `.github/workflows/tests.yml` and bump these exact action pins
    (these are the ONLY action `uses:` lines in the file):
    - line ~18: `actions/checkout@v4` -> `actions/checkout@v5`
    - line ~21: `actions/setup-python@v5` -> `actions/setup-python@v6`
    - line ~67: `codecov/codecov-action@v4` -> `codecov/codecov-action@v5`

    Rationale for codecov bump: OPS-03 requires "zero Node 20 deprecation
    warnings" and `codecov/codecov-action@v4` runs on Node 20. `@v5` runs
    on Node 24. The `CODECOV_TOKEN` env var wiring is unchanged and
    compatible with v5.

    DO NOT touch any other line. Do NOT change the numpydoc step,
    interrogate step, mypy step, coverage step, the matrix, or triggers —
    those are owned by plan 20-02 (numpydoc step) or out of scope.
    Pin to the major tag form (`@v5`, `@v6`) — do NOT pin to a SHA or a
    minor/patch tag; this repo uses floating major tags consistently.
  </action>
  <verify>
    `grep -nE "actions/checkout@|actions/setup-python@|codecov/codecov-action@" .github/workflows/tests.yml`
    shows `@v5`, `@v6`, `@v5` respectively and NO `@v4` on checkout/codecov
    and NO `@v5` on setup-python. Run
    `grep -nE "@v4($|[^0-9])" .github/workflows/tests.yml` — must return
    nothing.
  </verify>
  <done>
    tests.yml has checkout@v5, setup-python@v6, codecov-action@v5 and zero
    Node-20-era action majors remain.
  </done>
</task>

<task type="auto">
  <name>Task 2: Bump actions in publish.yml to Node-24 majors (matched artifact pair)</name>
  <files>.github/workflows/publish.yml</files>
  <action>
    Edit `.github/workflows/publish.yml` and bump these exact action pins:
    - line ~12: `actions/checkout@v4` -> `actions/checkout@v5`
    - line ~13: `actions/setup-python@v5` -> `actions/setup-python@v6`
    - line ~25: `actions/upload-artifact@v4` -> `actions/upload-artifact@v5`
    - line ~38: `actions/download-artifact@v4` -> `actions/download-artifact@v5`

    CRITICAL (research Pitfall 1): `upload-artifact` and
    `download-artifact` MUST be bumped together — the v5 artifact format
    is incompatible with v4 readers. A mixed `upload@v5` + `download@v4`
    breaks the publish job at the download step. Both are in this single
    file, change both in this task.

    DO NOT change `pypa/gh-action-pypi-publish@release/v1` (line ~43) — it
    is a floating release branch ref, stays as-is, no Node-20 concern.
    DO NOT change the `environment: pypi`, `permissions.id-token: write`,
    or any build/twine logic. Pin to major tags (`@v5`, `@v6`).
  </action>
  <verify>
    `grep -nE "actions/(checkout|setup-python|upload-artifact|download-artifact)@" .github/workflows/publish.yml`
    shows checkout@v5, setup-python@v6, upload-artifact@v5,
    download-artifact@v5. Run `grep -nE "@v4($|[^0-9])" .github/workflows/publish.yml`
    — must return nothing. Confirm `pypa/gh-action-pypi-publish@release/v1`
    is still present and unchanged.
  </verify>
  <done>
    publish.yml has checkout@v5, setup-python@v6, and a MATCHED
    upload/download-artifact@v5 pair; pypa publish action unchanged; zero
    Node-20-era action majors remain.
  </done>
</task>

</tasks>

<verification>
- `grep -rnE "@v4($|[^0-9])" .github/workflows/` returns nothing (no
  action pinned to a v4 major remains).
- Both workflow files are valid YAML: `python -c "import yaml,sys;
  [yaml.safe_load(open(f)) for f in ('.github/workflows/tests.yml',
  '.github/workflows/publish.yml')]; print('YAML OK')"`.
- `pypa/gh-action-pypi-publish@release/v1` still present in publish.yml.
</verification>

<success_criteria>
- tests.yml: checkout@v5, setup-python@v6, codecov-action@v5.
- publish.yml: checkout@v5, setup-python@v6, upload-artifact@v5,
  download-artifact@v5, pypa publish@release/v1 unchanged.
- Zero Node-20-era action majors across both files (satisfies OPS-03 /
  phase success criterion #1).
</success_criteria>

<output>
After completion, create
`.planning/phases/20-release-preparation-v1-2-0/20-01-SUMMARY.md`
</output>
