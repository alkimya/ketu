---
phase: 11-cli-refactor-integration
plan: 06
type: execute
wave: 5
depends_on: ["11-05"]
files_modified:
  - tests/cli/fixtures/v1_0_legacy_output.txt
  - tests/cli/test_legacy_byte_identical.py
autonomous: false
user_setup: []

must_haves:
  truths:
    - "Fixture file tests/cli/fixtures/v1_0_legacy_output.txt exists and is the captured stdout of v1.0.0's `python -m ketu` for a fixed reference invocation"
    - "Fixture is captured FROM THE v1.0.0 git tag (not HEAD) — via `git worktree add` or `git stash` + `git checkout v1.0.0`"
    - "Reference invocation is fixed and documented in the test docstring: date=2000-01-01, time=12:00, tz=UTC (J2000.0 epoch — minimizes ephemeris drift sources)"
    - "Test runs `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` in a subprocess and asserts result.stdout == fixture bytes"
    - "Subprocess invocation uses sys.executable + the current package install (Plan 11-05 reinstall guarantees the new entry point)"
    - "On byte-identical mismatch, the test's failure message hints at the most likely drift causes (number formatting, missing Aspect Timing Example block, header leak to stdout)"
    - "Fixture is committed to git under tests/cli/fixtures/ (matches tests/houses/fixtures/ precedent)"
    - "Test passes locally and would pass in CI on Python 3.10/3.11/3.12/3.13 (only stdlib + numpy, deterministic ephemeris)"
  artifacts:
    - path: tests/cli/fixtures/v1_0_legacy_output.txt
      provides: "Captured v1.0 stdout for the reference invocation; the regression target"
      min_lines: 40
    - path: tests/cli/test_legacy_byte_identical.py
      provides: "Subprocess regression test asserting byte-identical match against the fixture"
      min_lines: 40
  key_links:
    - from: tests/cli/test_legacy_byte_identical.py
      to: tests/cli/fixtures/v1_0_legacy_output.txt
      via: "FIXTURE.read_bytes() then assert result.stdout == expected"
      pattern: "v1_0_legacy_output\\.txt"
    - from: tests/cli/test_legacy_byte_identical.py
      to: ketu/cli/aspects_cmd.py
      via: "subprocess.run([sys.executable, '-m', 'ketu', '--harmonics', 'all', 'aspects', '--date', ...])"
      pattern: "subprocess\\.run.*-m.*ketu"
---

<objective>
Lock down CLI-03: capture the v1.0 reference stdout from the `v1.0.0` git tag (one-time), commit it as `tests/cli/fixtures/v1_0_legacy_output.txt`, and add `tests/cli/test_legacy_byte_identical.py` that runs `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` in a subprocess and asserts `result.stdout == fixture.read_bytes()`.

Critical (research §Pattern 5 + Pitfall 6): the v1.0 `main()` emits an "Aspect Timing Example" trailing block that's part of the byte-identical contract. Plan 11-04 already preserves it. This plan validates that preservation against the actual v1.0 bytes.

Why a separate plan: fixture capture requires checking out the `v1.0.0` git tag (or using `git worktree`) — a manual checkpoint where the user must approve the captured fixture before it's committed. The capture itself is automated (Claude runs `git worktree add` + `printf | python -m ketu`); the checkpoint is human verification that the fixture looks reasonable (correct length, no garbage characters, recognizable structure) before it's committed and pinned forever.

Output:
  - tests/cli/fixtures/v1_0_legacy_output.txt — the frozen v1.0 reference (committed)
  - tests/cli/test_legacy_byte_identical.py — the subprocess regression test
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/11-cli-refactor-integration/11-RESEARCH.md

# Source of truth for the byte-identical contract — v1.0 main() at the v1.0.0 tag.
# (Read via: git show v1.0.0:ketu/display.py — verifies the Aspect Timing Example block exists.)

# What's already preserving the format under --harmonics all (Plan 11-04 deliverable).
@ketu/cli/aspects_cmd.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Capture v1.0 reference stdout from the v1.0.0 git tag into the fixture file</name>
  <files>tests/cli/fixtures/v1_0_legacy_output.txt</files>
  <action>
**Goal:** Produce the byte-exact stdout v1.0's `python -m ketu` emitted for a fixed reference invocation, commit it as `tests/cli/fixtures/v1_0_legacy_output.txt`, and never touch it again unless we INTENTIONALLY want to break the contract.

**Reference invocation (FIXED — do not change):**
- Date: `2000-01-01` (J2000.0 epoch — round-number, minimizes documentation friction)
- Time: `12:00`
- Timezone: `UTC`

The v1.0 `main()` reads three `input()` lines: date as `YYYY-MM-DD`, time as `HH:MM`, timezone string. All three feed into `datetime(...)` and `utc_to_julian(...)`. With timezone `UTC`, the JD is exactly `2451545.0` — the canonical J2000.0 reference.

**Capture procedure:**

```bash
# 1. Create directory for the fixture (parent of the file).
mkdir -p tests/cli/fixtures

# 2. Create a clean worktree at the v1.0.0 tag (does NOT modify the current branch).
git worktree add /tmp/ketu-v1.0.0 v1.0.0

# 3. Inside the v1.0.0 worktree, install + capture stdout.
#    Use a fresh venv to avoid editable-install pollution from the main checkout.
cd /tmp/ketu-v1.0.0
python -m venv venv-v1.0
source venv-v1.0/bin/activate
pip install -e . --quiet

# 4. Run the v1.0 interactive main() with stdin scripted to our reference.
#    Capture to the fixture path in the MAIN checkout (not the worktree).
printf "2000-01-01\n12:00\nUTC\n" | python -m ketu \
  > /home/loc/workspace/ketu/tests/cli/fixtures/v1_0_legacy_output.txt

# 5. Deactivate venv and clean up the worktree.
deactivate
cd /home/loc/workspace/ketu
git worktree remove /tmp/ketu-v1.0.0 --force
```

**After capture, verify the fixture:**

```bash
ls -la tests/cli/fixtures/v1_0_legacy_output.txt   # exists, non-empty
wc -l tests/cli/fixtures/v1_0_legacy_output.txt    # ~40-50 lines expected
grep -c "Bodies Positions" tests/cli/fixtures/v1_0_legacy_output.txt   # 1
grep -c "Bodies Aspects" tests/cli/fixtures/v1_0_legacy_output.txt     # 1
grep -c "Aspect Timing Example" tests/cli/fixtures/v1_0_legacy_output.txt   # 1
head -5 tests/cli/fixtures/v1_0_legacy_output.txt   # first lines look like positions header
```

If any of these checks fail (e.g. fixture is empty, missing the timing block, or contains garbage), STOP and surface the issue at the checkpoint below. Do NOT commit a malformed fixture.

**Note on encoding:** v1.0 `main()` writes plain ASCII + degree symbol `°` (U+00B0). The fixture file must be UTF-8 encoded (default on Linux). The byte-identical test reads `.read_bytes()` so encoding mismatches will surface as a byte-comparison failure, not a Python decode error.

**Note on stdin/stdout interleaving:** v1.0 `main()` calls `input(...)` three times — those prompts go to stdout when stdin is a TTY, but when stdin is piped (as `printf | python -m ketu` does), the prompt strings are still written to stdout BEFORE input() returns. So the fixture will contain the three prompt lines at the very top:

```
Give a date with ISO format, ex: 2020-12-21
Give a time (hour, minute), with ISO format, ex: 19:20
Give the Time Zone, ex: 'Europe/Paris' for France: 
```

(Note the trailing space on the third prompt — Python's `input()` doesn't add a newline.)

These prompt lines ARE part of the v1.0 stdout. The byte-identical test will fail if Plan 11-04's `cmd_aspects` doesn't reproduce them, BUT the new CLI uses argparse — there are no input() prompts. SO: the fixture's prompt-prefix is something the new CLI cannot match, AND the byte-identical contract REQUIRES matching v1.0 stdout exactly.

**Resolution:** strip the prompt prefix from the fixture before committing. Reasoning: those prompts are stdin-driven artifacts of the interactive UX, not part of the "computed astronomical output" that CLI-03 cares about preserving. Document the strip in the fixture's first comment line so future readers understand. The strip is safe because:
- The prompts always have known, fixed text (we control them).
- Removing them does not affect the deterministic computed output.
- A user running `ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` non-interactively expects no prompts.

**Strip command** (run after step 4 above):

```bash
# Remove exactly the 3 known prompt lines from the top of the fixture.
# Use a here-doc-with-cat trick to avoid sed escape complexity.
python3 - <<'PY'
from pathlib import Path
p = Path("/home/loc/workspace/ketu/tests/cli/fixtures/v1_0_legacy_output.txt")
data = p.read_text()
prefix = (
    "Give a date with ISO format, ex: 2020-12-21\n"
    "Give a time (hour, minute), with ISO format, ex: 19:20\n"
    "Give the Time Zone, ex: 'Europe/Paris' for France: "
)
if data.startswith(prefix):
    data = data[len(prefix):]
    p.write_text(data)
    print("Stripped 3 input() prompt lines from fixture")
else:
    print("WARNING: fixture does not start with expected prompt prefix; manual review needed")
PY
```

After the strip, re-verify:
```bash
head -5 tests/cli/fixtures/v1_0_legacy_output.txt
# First 5 lines should be:
# (blank line)
# ------------- Bodies Positions -------------
# Sun       : Capricorn      10°15'40"
# ...

wc -l tests/cli/fixtures/v1_0_legacy_output.txt
# ~35-45 lines (3 prompt lines removed)
```

The fixture is now ready. Do NOT commit yet — the human-verify checkpoint in Task 2 confirms it before commit.
  </action>
  <verify>
1. `tests/cli/fixtures/v1_0_legacy_output.txt` exists and is non-empty.
2. First non-blank line of the fixture is `------------- Bodies Positions -------------` (no input() prompts at top).
3. Fixture contains exactly 1 occurrence each of `Bodies Positions`, `Bodies Aspects`, and `Aspect Timing Example`.
4. Fixture has ~35-45 lines.
5. `git worktree list` no longer shows the temporary v1.0.0 worktree.
6. Diff against current `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` for early signal:
   ```bash
   diff <(python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z 2>/dev/null) tests/cli/fixtures/v1_0_legacy_output.txt
   ```
   Expected: zero or near-zero diff. If non-trivial diff, Plan 11-04's `cmd_aspects` format strings need fixing — surface at the checkpoint, do not silently commit.
  </verify>
  <done>
- tests/cli/fixtures/v1_0_legacy_output.txt exists, is the v1.0.0-tag stdout for the J2000 UTC invocation, with the three input() prompt lines stripped from the top.
- Fixture contains the three required sections (positions / aspects / timing example).
- The v1.0.0 git worktree was created, used, and cleanly removed.
- Pre-commit diff vs. current `python -m ketu --harmonics all ...` is near-zero (any diff is documented at the checkpoint).
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 2: Human verification of captured fixture before commit</name>
  <files>tests/cli/fixtures/v1_0_legacy_output.txt</files>
  <action>
**Pause for human review.** The fixture from Task 1 is on disk but UNCOMMITTED. The user must inspect it AND its diff against the current Plan 11-04 CLI output before this PLAN proceeds to write the regression test (Task 3) and commit.

What was built (artifact under review):
- `tests/cli/fixtures/v1_0_legacy_output.txt` — the captured v1.0 reference stdout (input() prompt prefix stripped).
- The diff between this fixture and the current Plan 11-04 CLI output for the same invocation.

This fixture will be PINNED FOREVER as the CLI-03 contract. Once committed, ANY drift in `--harmonics all` stdout breaks CI. The user must confirm:
  1. The fixture looks correct (positions + aspects + timing example, recognizable bodies, no garbage).
  2. The diff against the current CLI output is acceptable (zero diff = ideal; small diffs may reveal Plan 11-04 bugs that should be fixed before pinning).
  </action>
  <how-to-verify>
1. Inspect the fixture:
   ```bash
   cat tests/cli/fixtures/v1_0_legacy_output.txt | head -20
   wc -l tests/cli/fixtures/v1_0_legacy_output.txt
   ```
   Confirm: starts with a blank line + `------------- Bodies Positions -------------`, contains 13 body position lines (Sun through Lilith), then `------------- Bodies Aspects -------------`, then aspect lines, then `------------- Aspect Timing Example -------------` and 3 Sun-Moon timing lines.

2. Diff against the current CLI:
   ```bash
   diff -u tests/cli/fixtures/v1_0_legacy_output.txt \
     <(python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z 2>/dev/null)
   ```
   - Zero diff → approve, proceed to Task 3.
   - Non-zero diff → REVIEW each diff line carefully:
     - Whitespace differences in column alignment? → Plan 11-04 format strings need adjustment (re-check `cmd_aspects` against `git show v1.0.0:ketu/display.py`).
     - Missing Aspect Timing Example? → Plan 11-04's trailing block isn't being emitted (research §Open Question 2 was supposed to ensure this).
     - Extra `# Aspect set: ...` lines? → Plan 11-04 leaked stderr to stdout (research §Pitfall 3); fix `emit_resolved_config`'s `file=sys.stderr` argument.
     - Different aspect orbs (e.g. `1°23'45"` vs `1°23'46"`)? → Possibly an ephemeris cache or floating-point rounding drift since v1.0; surface this immediately, do NOT pin until investigated.

3. If diff is non-zero and you cannot identify a clear cause, STOP. Reject this checkpoint and request a Plan 11-04 fix before re-running this plan.
  </how-to-verify>
  <verify>
Human inspects `cat tests/cli/fixtures/v1_0_legacy_output.txt | head -20` and `diff -u tests/cli/fixtures/v1_0_legacy_output.txt <(python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z 2>/dev/null)`. Zero diff = ideal.
  </verify>
  <done>
User responded "approved" — fixture and diff look correct, ready to pin as CLI-03 contract.
  </done>
  <resume-signal>
Type "approved" if the fixture and diff look correct. Type "diff: <description>" to surface a problem (orchestrator will route to revision mode for Plan 11-04). Type "reject" to abort and revisit.
  </resume-signal>
</task>

<task type="auto">
  <name>Task 3: Add the byte-identical regression test, commit fixture and test together</name>
  <files>tests/cli/test_legacy_byte_identical.py</files>
  <action>
**Create tests/cli/test_legacy_byte_identical.py** — the subprocess regression test.

```python
"""CLI-03 byte-identical regression test.

Pins the stdout of ``python -m ketu --harmonics all aspects --date
2000-01-01T12:00:00Z`` to the v1.0 reference fixture committed at
``tests/cli/fixtures/v1_0_legacy_output.txt``. Any drift in the legacy
escape-hatch output (added space, dropped block, format change, etc.)
fails this test in CI.

The fixture was captured from the ``v1.0.0`` git tag for date
2000-01-01 / time 12:00 / tz UTC (= J2000.0 epoch, JD = 2451545.0). The
three input() prompt lines from v1.0's interactive main() were stripped
before pinning — they are stdin-UX artifacts, not part of the
"computed astronomical output" that CLI-03 cares about.

This is a SUBPROCESS test (not in-process) for two reasons:
1. It mirrors what users actually run — the surface is the bytes the OS
   sees, including any encoding or line-ending quirks.
2. It exercises the ``ketu/__main__.py`` entry point repointed in Plan
   11-05; an in-process test would skip that path.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "v1_0_legacy_output.txt"

REFERENCE_DATE = "2000-01-01T12:00:00Z"
REFERENCE_ARGV = [
    sys.executable,
    "-m", "ketu",
    "--harmonics", "all",
    "aspects",
    "--date", REFERENCE_DATE,
]


class TestLegacyByteIdentical:
    """CLI-03: --harmonics all stdout is byte-identical to the v1.0 fixture."""

    def test_fixture_exists_and_nonempty(self):
        """Sanity: the fixture file is committed and has content."""
        assert FIXTURE.exists(), f"Fixture missing: {FIXTURE}"
        assert FIXTURE.stat().st_size > 100, f"Fixture suspiciously small: {FIXTURE.stat().st_size} bytes"

    def test_harmonics_all_byte_identical_to_v1_0(self):
        """Run `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z` and assert byte-identity."""
        expected = FIXTURE.read_bytes()

        result = subprocess.run(
            REFERENCE_ARGV,
            capture_output=True,
            check=False,  # we want to inspect non-zero exits ourselves
            timeout=60,
        )

        if result.returncode != 0:
            pytest.fail(
                f"`python -m ketu --harmonics all aspects --date {REFERENCE_DATE}` "
                f"exited with code {result.returncode}.\n"
                f"stderr: {result.stderr.decode(errors='replace')!r}"
            )

        if result.stdout != expected:
            # Build a maximally-helpful diff for failure context.
            actual = result.stdout
            actual_text = actual.decode(errors="replace")
            expected_text = expected.decode(errors="replace")
            import difflib
            diff = "\n".join(difflib.unified_diff(
                expected_text.splitlines(),
                actual_text.splitlines(),
                fromfile="v1_0_legacy_output.txt (expected)",
                tofile="current --harmonics all stdout (actual)",
                lineterm="",
            ))
            pytest.fail(
                "CLI-03 byte-identical regression: --harmonics all stdout "
                "drifted from the v1.0 fixture.\n\n"
                "Common causes:\n"
                "  - emit_resolved_config leaked '# ' lines to stdout "
                "(should be file=sys.stderr)\n"
                "  - 'Aspect Timing Example' trailing block missing or "
                "reformatted (must match v1.0 exactly)\n"
                "  - Aspect-printing format string drifted (column widths, "
                "separators, degree symbols)\n"
                "  - Position-printing changed in display.py:print_positions\n\n"
                f"Unified diff:\n{diff}"
            )

    def test_stderr_contains_resolved_config_header(self):
        """CLI-06 sanity: stderr DOES contain the resolved-config header,
        confirming Pitfall 3 is averted (header on stderr, not stdout)."""
        result = subprocess.run(
            REFERENCE_ARGV,
            capture_output=True,
            check=False,
            timeout=60,
        )
        assert result.returncode == 0
        stderr = result.stderr.decode()
        assert "# Aspect set:" in stderr or "# Ketu" in stderr, (
            "CLI-06 header expected on stderr; got stderr={!r}".format(stderr[:500])
        )
```

Notes:
- `check=False` + manual error inspection so the test failure messages are useful (rather than CalledProcessError without context).
- `difflib.unified_diff` is stdlib — no new test dep.
- `timeout=60` defends against accidental infinite loops if a future regression introduces one.
- Three tests: fixture sanity, byte-identical (the main one), stderr-has-header (CLI-06 belt-and-suspenders).

**Commit the fixture + test together** (this is the same commit so the fixture's contract and its enforcement land atomically):

The orchestrator will run `gsd-tools commit` after the plan completes. The fixture file (binary-ish text) MUST be tracked in git — verify with `git status` before commit that it shows up as a new file.

Optional sanity diff to surface in the SUMMARY:
```bash
wc -c tests/cli/fixtures/v1_0_legacy_output.txt   # ~1500-2500 bytes likely
md5sum tests/cli/fixtures/v1_0_legacy_output.txt   # record in SUMMARY for future audit
```
  </action>
  <verify>
1. `pytest tests/cli/test_legacy_byte_identical.py -v` — all 3 tests pass.
2. `pytest tests/cli/ -v` — full CLI suite green (Plan 11-01 through 11-04 + this).
3. `pytest tests/ -v` — full project suite green.
4. `git status` shows `tests/cli/fixtures/v1_0_legacy_output.txt` and `tests/cli/test_legacy_byte_identical.py` as new files (not gitignored).
5. Run the test in a freshly-installed venv as final smoke (catches hidden install-state dependencies):
   ```bash
   python -m venv /tmp/ketu-fresh && source /tmp/ketu-fresh/bin/activate
   pip install -e . --quiet
   pytest tests/cli/test_legacy_byte_identical.py -v
   ```
   All pass → CI will pass too.
  </verify>
  <done>
- tests/cli/test_legacy_byte_identical.py exposes 3 tests: fixture-sanity, byte-identical, stderr-header-present.
- All 3 tests pass against the committed fixture.
- Fixture + test land in the same git commit (atomic CLI-03 contract).
- Failure mode is informative: unified diff + likely-cause list.
- Fresh-venv re-install + test re-run also passes.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/cli/test_legacy_byte_identical.py -v` — 3 tests pass.
- `pytest tests/ -v` — full project suite green.
- `mypy --strict ketu/` — clean (no source code changes; only test+fixture additions).
- The fixture has been verified by the human at the Task 2 checkpoint.
- Fresh-venv install + test passes (CI parity).
- Visual confirmation: `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z 2>/dev/null` and `cat tests/cli/fixtures/v1_0_legacy_output.txt` produce identical output.
</verification>

<success_criteria>
- CLI-03 fully closed: `--harmonics all` stdout is pinned byte-for-byte to the v1.0 reference for J2000.0/UTC.
- Fixture captured from the v1.0.0 git tag (NOT from HEAD), with the input() prompt prefix stripped, committed under tests/cli/fixtures/.
- Subprocess test exercises the full surface (sys.executable + python -m ketu + argparse → cmd_aspects → stdout).
- Failure messages cite likely causes for fast diagnosis (header leak, missing timing block, format drift).
- Fresh-venv install passes the test (CI parity).
- Phase 11 complete: CLI-01 (Plan 11-05), CLI-02 (Plan 11-02 + 11-04), CLI-03 (this plan), CLI-04 (Plan 11-03), CLI-05 (Plan 11-04), CLI-06 (Plan 11-04) all closed.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-06-byte-identical-regression-SUMMARY.md` documenting:
- Fixture metadata: file size (bytes), line count, md5sum (for future drift audit), the exact reference invocation
- Capture procedure: which v1.0.0 commit was checked out (record SHA), confirmation worktree was cleaned up
- Whether the diff at Task 2 checkpoint was zero (ideal) or had documented drift (and what was fixed in revision)
- Test count delta (added 3 tests in test_legacy_byte_identical.py)
- Phase 11 close summary: all 6 CLI-* requirements covered (CLI-01..CLI-06)
- Any deviations from plan
</output>
