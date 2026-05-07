---
phase: 11-cli-refactor-integration
plan: 05
type: execute
wave: 4
depends_on: ["11-04"]
files_modified:
  - pyproject.toml
  - ketu/__main__.py
  - ketu/display.py
  - tests/test_ketu.py
autonomous: true

must_haves:
  truths:
    - "pyproject.toml [project.scripts] ketu = 'ketu.cli:main' (was: 'ketu.display:main')"
    - "pyproject.toml [tool.setuptools] packages list includes 'ketu.cli'"
    - "ketu/__main__.py imports main from ketu.cli (was: from ketu.display)"
    - "ketu/display.py:main() function is DELETED"
    - "ketu/display.py __all__ no longer includes 'main' — exports only print_positions and print_aspects"
    - "tests/test_ketu.py: TestMain class deleted (its only test exercises the legacy interactive main)"
    - "tests/test_ketu.py: any 'from ketu.display import main' / 'main' usage removed"
    - "After re-install, `ketu` console script invokes argparse CLI (no input() prompt)"
    - "Both python -m ketu AND ketu console script route to ketu.cli:main"
    - "All existing 638+ tests still pass; CLI test count unchanged from end of Plan 11-04"
  artifacts:
    - path: pyproject.toml
      provides: "ketu console script + setuptools packages updated to ketu.cli"
      contains: "ketu = \"ketu.cli:main\""
    - path: ketu/__main__.py
      provides: "python -m ketu routes to ketu.cli:main"
      contains: "from ketu.cli import main"
    - path: ketu/display.py
      provides: "Library helpers print_positions, print_aspects ONLY (main() deleted)"
      exports: ["print_positions", "print_aspects"]
    - path: tests/test_ketu.py
      provides: "TestMain class removed; remaining display tests untouched"
  key_links:
    - from: pyproject.toml
      to: ketu/cli/__init__.py:main
      via: "[project.scripts] ketu console_script entry point"
      pattern: "ketu = \"ketu\\.cli:main\""
    - from: ketu/__main__.py
      to: ketu/cli/__init__.py:main
      via: "Module entry point (python -m ketu)"
      pattern: "from ketu\\.cli import main"
    - from: ketu/display.py
      to: "(removed main)"
      via: "Library helpers only — no CLI logic"
      pattern: "__all__ = \\[\"print_positions\", \"print_aspects\"\\]"
---

<objective>
Repoint both entry points (`pyproject.toml [project.scripts] ketu` AND `ketu/__main__.py`) to `ketu.cli:main`, delete the legacy interactive `ketu/display.py:main()`, update `__all__` and `tests/test_ketu.py:TestMain` accordingly, and reinstall the package so the `ketu` console script picks up the new entry point.

Critical (research §Pitfall 7): Both entry points must change in the SAME plan/commit. Updating only `pyproject.toml` and forgetting `ketu/__main__.py` means `python -m ketu` still routes to the old code; updating `ketu/__main__.py` and forgetting `pyproject.toml` means the installed `ketu` script still routes to the old code.

Critical (research §Pitfall 8): Test file `tests/test_ketu.py:TestMain` imports `from ketu.display import main`. Once `main` is deleted from `display.py`, that import fails at collection time — must be removed before running tests.

Purpose: Closes CLI-01 (interactive `input()` prompt removed everywhere). Sets up Plan 11-06's byte-identical regression test (which runs `python -m ketu --harmonics all aspects ...` and requires this plan's `__main__.py` repoint).

Output:
  - `pyproject.toml` — `[project.scripts] ketu = "ketu.cli:main"` + `ketu.cli` added to packages list
  - `ketu/__main__.py` — `from ketu.cli import main`
  - `ketu/display.py` — `main()` deleted; `__all__` updated
  - `tests/test_ketu.py` — `TestMain` class deleted; legacy `main` import removed
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

# Files this plan modifies
@pyproject.toml
@ketu/__main__.py
@ketu/display.py
@tests/test_ketu.py

# What's now wired and ready (Plans 11-01 through 11-04 complete)
@ketu/cli/__init__.py
@ketu/cli/parser.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Repoint entry points (pyproject.toml + __main__.py)</name>
  <files>pyproject.toml, ketu/__main__.py</files>
  <action>
**Edit pyproject.toml** — TWO edits in this single file:

1. `[project.scripts]` section — change line 54 from:

```toml
ketu = "ketu.display:main"
```

to:

```toml
ketu = "ketu.cli:main"
```

2. `[tool.setuptools]` packages list — line 57. Current value:

```toml
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses"]
```

Add `"ketu.cli"`:

```toml
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses", "ketu.cli"]
```

DO NOT touch any other `pyproject.toml` section (version stays at 1.0.0; that's Plan 12's job).

**Edit ketu/__main__.py** — change the import on line 6:

Replace ENTIRE FILE with:

```python
"""Entry point for running Ketu as a module.

This allows running Ketu with: python -m ketu

Routes to ``ketu.cli:main`` (the argparse-based CLI). The legacy
``ketu.display:main`` interactive prompt was deleted in Phase 11.
"""

from ketu.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

Notes:
- Wrap the call in `raise SystemExit(main())` so the integer return code from `main()` becomes the process exit code (matches argparse convention; Plan 11-06's subprocess test checks `result.returncode`).
- Keep the file short and focused.

**Reinstall the package** so the new entry point is registered:

```bash
source venv/bin/activate
pip install -e . --quiet
```

Without this, the `ketu` console script in the venv still has the old shebang/wrapper pointing at `ketu.display:main`. Plan 11-06's tests use `python -m ketu` (not `ketu`), so technically Plan 11-06 doesn't strictly require the reinstall — but reinstall is hygiene and the success criterion specifies the `ketu` script must work too.

Verify the reinstall:

```bash
python -c "import ketu.cli; print(ketu.cli.main)"   # should print a function
ketu --help  2>&1 | head -5                          # should print argparse help, NOT prompt for input
python -m ketu --help 2>&1 | head -5                 # should print argparse help
```
  </action>
  <verify>
1. `grep "ketu = " pyproject.toml | head -1` returns `ketu = "ketu.cli:main"`.
2. `grep "ketu.cli" pyproject.toml` finds the package in the setuptools list.
3. `cat ketu/__main__.py` shows `from ketu.cli import main` and `raise SystemExit(main())`.
4. After `pip install -e .`: `ketu --help` prints argparse usage (no `input()` prompt).
5. `python -m ketu --help` prints argparse usage.
6. `python -m ketu --list-aspect-sets` lists the 4 presets.
  </verify>
  <done>
- pyproject.toml [project.scripts] ketu = "ketu.cli:main".
- pyproject.toml [tool.setuptools] packages includes "ketu.cli".
- ketu/__main__.py imports from ketu.cli and exits with main()'s return code.
- pip install -e . succeeds with the new metadata.
- Both entry points (`ketu` and `python -m ketu`) route to the argparse CLI; no more interactive prompt.
  </done>
</task>

<task type="auto">
  <name>Task 2: Delete display.py:main(), update __all__, and clean up tests/test_ketu.py</name>
  <files>ketu/display.py, tests/test_ketu.py</files>
  <action>
**Edit ketu/display.py** — delete the `main()` function and update `__all__`.

Open the file, find lines 67-94 (the `def main():` body and any blank lines after it). Delete the entire function. Also delete the trailing `from datetime import datetime` and `from zoneinfo import ZoneInfo` imports IF they are no longer used after `main()` is gone (they are imported at the top of the file; check whether `print_positions` / `print_aspects` reference them — they do NOT, so the imports can be removed).

After edits, `ketu/display.py` should contain:
- module docstring (updated to remove "main command-line interface" mention; replace with "Library helpers for formatted output")
- numpy import
- existing imports needed by print_positions / print_aspects: `from .core import signs, aspects` + `from .calculations import body_name, body_sign, positions, is_retrograde, dd_to_dms` + `from .aspects import calculate_aspects` (drop `body_id`, `find_aspects_between_dates`, `utc_to_julian`, `julian_to_utc` — they were only used by `main()`)
- `print_positions` function (UNCHANGED)
- `print_aspects` function (UNCHANGED)
- `__all__ = ["print_positions", "print_aspects"]` (drop "main")
- DROP top-level imports `from datetime import datetime`, `from zoneinfo import ZoneInfo` (only used by main())

Updated module docstring suggestion:

```python
"""Library formatters for Ketu astronomical output.

Provides ``print_positions`` and ``print_aspects`` — pure-stdout
formatted dumps used by the CLI (``ketu.cli.aspects_cmd``) and
documentation examples. The legacy interactive ``main()`` prompt was
removed in Phase 11; the argparse-based CLI lives in ``ketu.cli``.
"""
```

After this edit, the file is ~50 lines (was ~101).

**Edit tests/test_ketu.py** — delete the `TestMain` class entirely AND remove the `main` import.

1. Find the import line (around line 102 per STATE.md):

```python
from ketu.display import (
    print_positions,
    print_aspects,
    main,
)
```

Update to:

```python
from ketu.display import (
    print_positions,
    print_aspects,
)
```

(Adjust to match the actual existing form in the file — could be a single line or multi-line. Just remove the `main` symbol.)

2. Delete the `TestMain` class (lines 376-387 per STATE.md). It's the only consumer of the deleted `main`. The class body:

```python
class TestMain:
    """Test main CLI function"""

    def test_main_invalid_input(self, monkeypatch, capsys):
        """Test main with invalid input"""
        inputs = iter(["invalid-date", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs, ""))

        main()
        captured = capsys.readouterr()

        assert "Error" in captured.out or "error" in captured.out
```

DELETE the entire class. Do NOT replace it — Plan 11-04's `tests/cli/test_parser.py` and `tests/cli/test_aspects_cmd.py` already cover the equivalent territory at the new entry point.

**Verify nothing else references the deleted `main`:**

```bash
grep -rn "from ketu.display import.*main\|ketu\.display\.main\|display\.main" \
    ketu/ tests/ docs/ 2>/dev/null
```

Expected output: empty (no matches). If any matches surface, update those references too — likely candidates are docs/source/api.md and any examples/. For docs, update the entry-point reference if necessary; for examples, replace with `ketu.cli` if relevant.

**Verify the existing TestDisplay class still works** — it calls `print_positions(self.jday)` and `print_aspects(self.jday)` directly. Those functions are UNCHANGED in this plan; the tests should still pass. Run them after the edit:

```bash
pytest tests/test_ketu.py::TestDisplay -v
```

Expected: 2 tests pass (`test_print_positions`, `test_print_aspects`).
  </action>
  <verify>
1. `grep -c "def main" ketu/display.py` returns `0`.
2. `grep "main" ketu/display.py` finds NO matches in the body (only in the docstring describing what was removed).
3. `python -c "from ketu.display import print_positions, print_aspects"` succeeds.
4. `python -c "from ketu.display import main"` raises `ImportError`.
5. `grep -n "TestMain\|class TestMain\|test_main_invalid" tests/test_ketu.py` returns nothing.
6. `pytest tests/test_ketu.py -v` — all remaining tests pass; no collection errors.
7. `pytest tests/ -v` — full suite green.
8. `mypy --strict ketu/display.py` clean.
9. `grep -rn "from ketu.display import.*main\|ketu\.display\.main" ketu/ tests/` empty.
  </verify>
  <done>
- ketu/display.py: main() deleted; __all__ = ["print_positions", "print_aspects"]; unused datetime/zoneinfo/body_id/find_aspects_between_dates/utc_to_julian/julian_to_utc imports removed; module docstring updated.
- tests/test_ketu.py: TestMain class deleted; `main` removed from the `from ketu.display import (...)` import block.
- No remaining references to `ketu.display.main` anywhere in ketu/, tests/, or docs/.
- TestDisplay class still passes (print_positions / print_aspects unchanged).
- Full project test suite green; mypy --strict clean.
- Both `ketu --help` (console script) and `python -m ketu --help` show argparse usage; no interactive prompt anywhere (CLI-01 closed).
  </done>
</task>

</tasks>

<verification>
- `pytest tests/ -v` — full project suite green; no collection errors from missing `main` import.
- `mypy --strict ketu/` clean (note: also strict on display.py now that main is gone — fewer lines, easier).
- `ketu --help` prints argparse usage without prompting for input.
- `python -m ketu --help` prints argparse usage.
- `python -m ketu` (no args) prints argparse help to stdout, returns 0.
- `python -m ketu --list-aspect-sets` lists 4 presets.
- `grep -rn "from ketu.display import.*main\|ketu\.display:main" .` empty (except possibly in CHANGELOG/migration docs which are Plan 12 scope — not this plan's concern).
</verification>

<success_criteria>
- CLI-01 fully closed: NO interactive `input()` prompt anywhere in ketu/. Subcommands have their own `--help`.
- Both entry points repointed: `pyproject.toml [project.scripts]` AND `ketu/__main__.py`.
- `pip install -e .` regenerates the `ketu` console script wrapper pointing at `ketu.cli:main`.
- Legacy `display.py:main()` deleted; `display.py:print_positions` and `display.py:print_aspects` survive as library helpers (still imported by `ketu.cli.aspects_cmd`).
- `tests/test_ketu.py:TestMain` deleted; `from ketu.display import main` removed everywhere.
- Full project test suite green; mypy --strict clean.
- Plan 11-06 can now run `python -m ketu --harmonics all aspects --date ...` in a subprocess and route to the argparse CLI.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-05-entry-point-repoint-legacy-removal-SUMMARY.md` documenting:
- pyproject.toml diff (project.scripts + packages)
- __main__.py diff
- display.py diff (lines deleted, imports trimmed)
- tests/test_ketu.py diff (class removed, import trimmed)
- Re-install command result (pip install -e .)
- Test count delta (TestMain removed → -1 test; full suite still green)
- Any deviations from plan
</output>
