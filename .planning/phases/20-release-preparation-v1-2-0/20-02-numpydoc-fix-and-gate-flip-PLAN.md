---
phase: 20-release-preparation-v1-2-0
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/ephemeris/time.py
  - ketu/aspects/timelines.py
  - ketu/ephemeris/orbital.py
  - ketu/ephemeris/coordinates.py
  - ketu/cache/ephemeris_cache.py
  - ketu/aspects/core.py
  - ketu/ephemeris/planets.py
  - ketu/aspects/calculator.py
  - ketu/aspects/transits.py
  - ketu/aspects/windows.py
  - ketu/aspects/presets.py
  - pyproject.toml
  - .github/workflows/tests.yml
  - Makefile

autonomous: true

must_haves:
  truths:
    - "numpydoc lint reports ZERO violations across all linted ketu/*.py files"
    - "tests.yml numpydoc step has NO continue-on-error: true (gate is blocking)"
    - "pyproject.toml [tool.numpydoc_validation].checks no longer contains GL01"
    - "Makefile doc-gates target no longer swallows numpydoc failure (no '|| true' on the lint line) and the echo no longer says 'not blocking'"
    - "Full pytest suite still passes (no behavior changed — docstrings only)"
  artifacts:
    - path: "pyproject.toml"
      provides: "numpydoc config with GL01 suppression removed"
      contains: "[tool.numpydoc_validation]"
    - path: ".github/workflows/tests.yml"
      provides: "blocking numpydoc CI step"
      contains: "numpydoc lint"
    - path: "Makefile"
      provides: "local doc-gate that fails on numpydoc violations"
      contains: "doc-gates:"
  key_links:
    - from: "pyproject.toml checks list"
      to: "numpydoc lint behavior in CI"
      via: "GL01 removed -> stricter validation"
      pattern: "checks = \\["
---

<objective>
Fix all ~103 numpydoc docstring-style violations across 11 source files,
then flip the numpydoc gate from warning-only to blocking by removing
`continue-on-error: true` (tests.yml), the `GL01` suppression
(pyproject.toml), and the `|| true` / "not blocking" hedge (Makefile).
This is the OPS-02 finalization the in-code comment in tests.yml tags for
Phase 20.

Purpose: v1.2.0 ships with documentation quality enforced, not merely
warned. The gate MUST NOT be flipped until violations are zero or CI goes
red. interrogate already passes 100% — only numpydoc needs work. Pure
docstring edits, zero logic change. Runs Wave 1 parallel with 20-01 (no
file overlap).
Output: clean numpydoc lint, blocking CI gate, blocking local Makefile
gate.
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
@pyproject.toml
@.github/workflows/tests.yml
@Makefile
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix all numpydoc violations in the 11 source files</name>
  <files>ketu/ephemeris/time.py, ketu/aspects/timelines.py, ketu/ephemeris/orbital.py, ketu/ephemeris/coordinates.py, ketu/cache/ephemeris_cache.py, ketu/aspects/core.py, ketu/ephemeris/planets.py, ketu/aspects/calculator.py, ketu/aspects/transits.py, ketu/aspects/windows.py, ketu/aspects/presets.py</files>
  <action>
    First, enumerate the live violations so you fix the exact set, not a
    guess:
    ```
    source venv/bin/activate
    FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" \
        ! -name "lunar_calendar.py" ! -name "_*.py")
    python -m numpydoc lint $FILES
    ```
    The current violation profile (verified 2026-05-28) is:
    - SS03 x64 — summary line does not end with `.` -> append `.` to the
      one-line docstring summary.
    - PR09 x15 — parameter description does not finish with `.` -> append
      `.` to the offending Parameters entry.
    - RT05 x8 — return value description does not finish with `.` -> append
      `.` to the Returns entry.
    - RT01 x6 — no Returns section -> add a minimal `Returns` section
      documenting the actual return type/meaning (read the function body to
      describe it accurately; do NOT fabricate).
    - PR08 x2 — parameter description must start with a capital letter ->
      capitalize the first word of the description.
    - PR01 x2 — parameter not documented -> add the missing parameter to
      the Parameters section (match the signature; describe its real role).
    - GL08 x1 — object without docstring at `ketu/ephemeris/planets.py:302`
      -> add a short NumPy-style docstring.
    - GL06 x1 + GL07 x1 — `ketu/aspects/presets.py:1` module docstring has
      non-standard sections "Public API" and "ASP-06 forward-looking rule".
      Rename/absorb both into a standard `Notes` section OR remove the
      section headers and keep the prose as plain paragraphs. The section
      content must survive (it documents the public surface); only the
      non-standard SECTION HEADER must go. Re-run numpydoc on presets.py
      until GL06 AND GL07 both clear.

    Constraints:
    - Edit ONLY docstrings. Do NOT change any signature, logic, return
      value, or runtime string. interrogate is already 100% — keep it that
      way (do not delete docstrings).
    - These files appear in `pyproject.toml [tool.mypy.overrides]` with
      relaxed error codes — but you are not changing types, so mypy is
      unaffected. Still re-run mypy in verify to be safe.
    - Work file-by-file; after each file re-run numpydoc on just that file
      to confirm it reaches zero before moving on.
  </action>
  <verify>
    `FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py"); python -m numpydoc lint $FILES`
    produces NO output / zero violations (exit code 0).
    `python -m interrogate ketu/` still PASSES at 100%.
    `mypy ketu/ --strict` still passes (no new errors).
  </verify>
  <done>
    numpydoc lint is clean (0 violations) across all 11 files; interrogate
    still 100%; mypy strict still green.
  </done>
</task>

<task type="auto">
  <name>Task 2: Flip the gate to blocking in tests.yml, pyproject.toml, and Makefile</name>
  <files>.github/workflows/tests.yml, pyproject.toml, Makefile</files>
  <action>
    Only do this AFTER Task 1 verifies zero numpydoc violations. Flipping
    the gate with violations still present turns CI red.

    1. `.github/workflows/tests.yml` — the "Doc style audit (numpydoc ...)"
       step (~lines 51-63):
       - Remove the `continue-on-error: true` line.
       - Remove the 3-line Phase-20 TODO comment block above the step name
         (the `# Phase 20 (OPS-02 finalization): ...` comment — its job is
         done now).
       - Rename the step from "Doc style audit (numpydoc — warning only,
         blocking from v1.2.0)" to "Doc style audit (numpydoc — blocking)".
       - Leave the `if: matrix.python-version == '3.13'`, the FILES find
         command, and the lint invocation unchanged.

    2. `pyproject.toml` — `[tool.numpydoc_validation].checks` list (~line
       121-127): remove the `"GL01",  # ignore during warning phase ...`
       entry entirely. Keep `"all"`, `"EX01"`, `"SA01"`, `"ES01"`. Verified:
       there are currently ZERO live GL01 violations, so removing the
       suppression is safe (research Pitfall 2).

    3. `Makefile` — `doc-gates:` target (~lines 113-120):
       - Remove the trailing `|| true` from the `numpydoc lint ...` command
         so a local violation fails `make doc-gates`.
       - Change the final echo from "Doc gates OK (numpydoc warnings shown
         above; not blocking until v1.2.0)." to a non-hedged message, e.g.
         "Doc gates OK (interrogate + numpydoc both blocking)."

    After all three edits, run `make doc-gates` — it must exit 0 (because
    Task 1 made lint clean) and no longer print the "not blocking" hedge.
  </action>
  <verify>
    `grep -n "continue-on-error" .github/workflows/tests.yml` returns
    nothing. `grep -n "GL01" pyproject.toml` returns nothing.
    `grep -n "|| true" Makefile` returns nothing on the doc-gates lint line
    (`sed -n '113,121p' Makefile` shows no `|| true`).
    `make doc-gates` exits 0 with no "not blocking" text.
    Sanity: temporarily breaking one docstring summary (remove a period)
    then running `make doc-gates` exits NON-zero — confirms the gate is
    now blocking — then restore the period.
  </verify>
  <done>
    numpydoc gate is blocking in CI (no continue-on-error), in config
    (no GL01 suppression), and locally (Makefile fails on violations);
    `make doc-gates` passes on the clean tree.
  </done>
</task>

</tasks>

<verification>
- `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` — zero violations.
- `python -m interrogate ketu/` — PASSED 100%.
- `grep -rn "continue-on-error\|GL01" .github/workflows/tests.yml pyproject.toml` — nothing.
- `pytest tests/ -q` — full suite still passes (docstring-only change).
- `mypy ketu/ --strict` — green.
</verification>

<success_criteria>
- Zero numpydoc violations (satisfies OPS-02 finalization precondition).
- numpydoc gate blocking in tests.yml, pyproject.toml, and Makefile.
- No regressions: interrogate 100%, full pytest suite passes, mypy strict
  green.
</success_criteria>

<output>
After completion, create
`.planning/phases/20-release-preparation-v1-2-0/20-02-SUMMARY.md`
</output>
