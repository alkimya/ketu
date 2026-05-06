---
phase: 08-lilith-verification-fix
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - pyproject.toml
autonomous: true

must_haves:
  truths:
    - "User runs `pip install -e .` in a fresh venv and `python -c \"import swisseph\"` FAILS with ModuleNotFoundError"
    - "User runs `pip install -e .[test]` in a fresh venv and `python -c \"import swisseph; print(swisseph.MEAN_APOG)\"` prints `12`"
    - "User opens `pyproject.toml` and sees `pysweph>=2.10.3.6` only inside `[project.optional-dependencies].test`, never in the top-level `dependencies`"
    - "Existing test suite (`pytest tests/`) continues to pass with the new pyproject section"
  artifacts:
    - path: "pyproject.toml"
      provides: "[project.optional-dependencies].test extra with pysweph>=2.10.3.6"
      contains: "pysweph>=2.10.3.6"
  key_links:
    - from: "pyproject.toml [project.optional-dependencies].test"
      to: "pysweph PyPI package (>= 2.10.3.6)"
      via: "PEP 621 optional-dependencies extra named 'test'"
      pattern: "\\[project\\.optional-dependencies\\]"
    - from: "pyproject.toml [project] dependencies"
      to: "MUST NOT contain pysweph"
      via: "runtime isolation invariant"
      pattern: "^dependencies\\s*=\\s*\\[\\s*\"numpy"
---

<objective>
Add `pysweph>=2.10.3.6` as a test-only optional dependency to `pyproject.toml`, then prove via two-venv installation tests that it does NOT contaminate the runtime wheel. AGPL non-contamination is verified empirically, not assumed.

Purpose: REQUIREMENTS LIL-04 + ROADMAP success criterion #4. The cross-check harness (Plan 03) imports `swisseph` via `pytest.importorskip`; without this extra installed, the harness skips. The pure-NumPy runtime contract (PROJECT.md, locked decision in STATE.md) requires that no AGPL code lands in the published wheel.

Output: One-line addition of `[project.optional-dependencies]` section to `pyproject.toml` + empirical two-venv verification artifact.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/08-lilith-verification-fix/08-RESEARCH.md
@pyproject.toml
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add [project.optional-dependencies].test = ["pysweph>=2.10.3.6"] to pyproject.toml</name>
  <files>pyproject.toml</files>
  <action>
Open `pyproject.toml`. Locate the `[project]` table; the existing `dependencies = ["numpy>=1.20.0"]` block ends around line 39. The next section is `[project.urls]` at line 41.

Insert a new section AFTER `dependencies = [...]` and BEFORE `[project.urls]`:

```toml
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

Constraints:
- Do NOT add `pysweph` to `dependencies` (the top-level list). Verify after editing that `dependencies` still contains exactly `numpy>=1.20.0` and nothing else.
- Do NOT touch `[tool.mypy]` overrides; the existing `module = ["swisseph.*"]` ignore is already in place and continues to work.
- Use exact specifier `>=2.10.3.6` (lower bound only — not pinned). This is locked by REQUIREMENTS LIL-04 and STATE.md.
- Preserve TOML formatting (4-space indent inside arrays, trailing comma after the last entry).

Why `pysweph` and not `pyswisseph`: locked decision in STATE.md and research §"Standard Stack". The community fork ships current wheels (2026-02 release) where the upstream stalled in mid-2023; same `import swisseph as swe` API.
  </action>
  <verify>
```bash
# Section exists in correct location:
grep -n "\\[project.optional-dependencies\\]" pyproject.toml
grep -n "pysweph>=2.10.3.6" pyproject.toml

# Top-level dependencies unchanged:
python3 -c "
import tomllib
with open('pyproject.toml','rb') as f:
    d = tomllib.load(f)
runtime = d['project']['dependencies']
extras = d['project']['optional-dependencies']
assert runtime == ['numpy>=1.20.0'], f'Runtime deps changed: {runtime}'
assert 'test' in extras, 'test extra missing'
assert 'pysweph>=2.10.3.6' in extras['test'], f'pysweph not in test extra: {extras}'
print('TOML structure OK')
"

# Existing test suite still parses pyproject (sanity):
python3 -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('TOML PARSES')"
```
  </verify>
  <done>
`pyproject.toml` contains a `[project.optional-dependencies]` section with `test = ["pysweph>=2.10.3.6"]`. Top-level `dependencies` still contains exactly `numpy>=1.20.0`. The TOML parses without error.
  </done>
</task>

<task type="auto">
  <name>Task 2: Empirically verify two-venv runtime isolation (AGPL non-contamination check)</name>
  <files>(no files modified; this task produces evidence only)</files>
  <action>
Run two clean-venv installation tests to PROVE that `pysweph` is reachable via the `[test]` extra and unreachable without it. This is the empirical guard against AGPL contamination of the published wheel — the most important verification in Phase 8 after the harness itself.

Execute exactly these commands from the repo root and capture the output of EACH `python -c` invocation. The expected outcomes are explicit; deviations FAIL this task.

```bash
# Pin the install target to an absolute path: pip install -e <path> resolves the
# target by cwd, and these checks run from /tmp venvs whose cwd may not be the
# repo root. REPO_ROOT is computed once and reused.
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Venv 1: runtime install — must NOT pull pysweph
python3 -m venv /tmp/ketu-runtime-check
/tmp/ketu-runtime-check/bin/pip install --upgrade pip
/tmp/ketu-runtime-check/bin/pip install -e "$REPO_ROOT"
# Expect: ModuleNotFoundError: No module named 'swisseph'
/tmp/ketu-runtime-check/bin/python -c "import swisseph" 2>&1 | tee /tmp/ketu-runtime-check.out
# Verify the failure mode is exactly ModuleNotFoundError (not ImportError-other):
/tmp/ketu-runtime-check/bin/python -c "
try:
    import swisseph
    print('FAIL: swisseph imported in runtime venv')
    raise SystemExit(1)
except ModuleNotFoundError:
    print('OK: swisseph correctly absent from runtime install')
"
rm -rf /tmp/ketu-runtime-check

# Venv 2: test install — MUST pull pysweph
python3 -m venv /tmp/ketu-test-check
/tmp/ketu-test-check/bin/pip install --upgrade pip
/tmp/ketu-test-check/bin/pip install -e "$REPO_ROOT[test]"
# Expect: prints "12" (the SE_MEAN_APOG constant)
/tmp/ketu-test-check/bin/python -c "import swisseph; print(swisseph.MEAN_APOG)" 2>&1 | tee /tmp/ketu-test-check.out
# Sanity: confirm the package name is pysweph not pyswisseph
/tmp/ketu-test-check/bin/pip show pysweph | grep -E "^(Name|Version):"
rm -rf /tmp/ketu-test-check
```

Failure modes that BLOCK this plan:
- Venv 1 successfully imports `swisseph` -> `pysweph` leaked into runtime. Revert pyproject changes and retry.
- Venv 2 fails to install `pysweph` -> the extra spec is wrong, OR the running platform has no `pysweph` wheel. If platform-specific, document in summary; do NOT remove the spec.
- Venv 2 prints something other than `12` for `swisseph.MEAN_APOG` -> the `pysweph` API contract has changed; halt and escalate before proceeding to Plan 03.

Capture both `/tmp/ketu-runtime-check.out` and `/tmp/ketu-test-check.out` contents in the SUMMARY.md.
  </action>
  <verify>
```bash
# Re-run the smoke versions of each venv test in-place (or paste the captured outputs):
# Runtime venv must report "OK: swisseph correctly absent"
# Test venv must print exactly "12"
# pip show must report Name: pysweph and Version: >= 2.10.3.6
echo "Manual verification: Task 2 stdout above must show all three OK markers."
```
  </verify>
  <done>
Empirical evidence captured in SUMMARY.md proves: (a) runtime install does NOT have `swisseph` importable; (b) `[test]` install DOES expose `swisseph.MEAN_APOG == 12`; (c) the installed package is `pysweph` (not `pyswisseph`) at version >= 2.10.3.6.
  </done>
</task>

</tasks>

<verification>
- `pyproject.toml` diff shows only insertion of one new section
- Top-level `[project].dependencies` is byte-identical to before edit (still `["numpy>=1.20.0"]`)
- Existing test suite (`pytest tests/`) still passes — pyproject changes do not affect existing tests
- `mypy --strict` continues to pass (the `module = ["swisseph.*"]` override is already in place)
- The two-venv evidence is captured in SUMMARY.md
</verification>

<success_criteria>
1. `pyproject.toml` contains `[project.optional-dependencies].test = ["pysweph>=2.10.3.6"]`.
2. `pyproject.toml` `[project].dependencies` is unchanged (only `numpy>=1.20.0`).
3. A fresh venv with `pip install -e .` cannot import `swisseph` — proven empirically.
4. A fresh venv with `pip install -e ".[test]"` can import `swisseph` and `swisseph.MEAN_APOG == 12` — proven empirically.
5. Both venv evidence outputs are captured in `08-02-SUMMARY.md`.
</success_criteria>

<output>
After completion, create `.planning/phases/08-lilith-verification-fix/08-02-SUMMARY.md` containing:
- The exact diff added to `pyproject.toml`
- Captured stdout from runtime venv (showing ModuleNotFoundError or "OK: swisseph correctly absent")
- Captured stdout from test venv (showing `swisseph.MEAN_APOG == 12` and `pip show pysweph` Name/Version)
- Confirmation that platform/Python version supports `pysweph` wheels (record platform.machine() / sys.version)
</output>
