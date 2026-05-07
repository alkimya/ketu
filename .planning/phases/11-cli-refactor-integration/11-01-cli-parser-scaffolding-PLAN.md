---
phase: 11-cli-refactor-integration
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - ketu/cli/__init__.py
  - ketu/cli/parser.py
  - tests/cli/__init__.py
  - tests/cli/conftest.py
  - tests/cli/test_parser.py
autonomous: true

must_haves:
  truths:
    - "ketu/cli/ subpackage exists with __init__.py re-exporting main"
    - "build_parser() returns an argparse.ArgumentParser with prog='ketu', description set"
    - "Top-level parser declares --list-aspect-sets and --list-house-systems (store_true)"
    - "Top-level parser declares --harmonics SPEC (default=None) — type validator wired in Plan 11-02"
    - "Subparsers added with dest='command', required=False (so introspection flags work without a subcommand)"
    - "aspects and houses subparsers exist as named-but-stub-dispatched parsers"
    - "main(argv) parses args, short-circuits introspection, dispatches via args.func, falls back to print_help()"
    - "Running ketu (no args) exits 0 and prints help to stdout (does NOT crash with AttributeError on args.func)"
  artifacts:
    - path: ketu/cli/__init__.py
      provides: "Re-exports main from parser"
      contains: "from .parser import main"
    - path: ketu/cli/parser.py
      provides: "build_parser() + main() entry"
      exports: ["build_parser", "main"]
      min_lines: 60
    - path: tests/cli/__init__.py
      provides: "Marker so tests/cli/ is a package"
    - path: tests/cli/conftest.py
      provides: "Shared CLI test fixtures (capsys helpers + invoke_main)"
    - path: tests/cli/test_parser.py
      provides: "build_parser unit tests + main() no-arg / --help / unknown-subcommand paths"
      min_lines: 40
  key_links:
    - from: ketu/cli/parser.py
      to: argparse
      via: "build_parser() constructs ArgumentParser + add_subparsers(dest='command', required=False)"
      pattern: "add_subparsers\\(dest=.command., required=False\\)"
    - from: ketu/cli/parser.py
      to: ketu/cli/parser.py:main
      via: "set_defaults(func=...) + getattr(args, 'func', None) dispatch"
      pattern: "getattr\\(args, .func., None\\)"
    - from: ketu/cli/__init__.py
      to: ketu/cli/parser.py
      via: "main re-export"
      pattern: "from \\.parser import main"
---

<objective>
Lay down the `ketu/cli/` subpackage skeleton: `__init__.py` re-exporting `main`, `parser.py` building the top-level argparse tree with `aspects` and `houses` subparsers (stub-dispatched for now), introspection flags (`--list-aspect-sets`, `--list-house-systems`) declared but not yet implemented, and `--harmonics SPEC` declared with `type=str` placeholder (real validator wired in Plan 11-02). Set up `tests/cli/` mirror.

Purpose: Foundational scaffold every other Phase 11 plan plugs into. Parser skeleton + main() entry + test layout. No business logic — pure argparse plumbing (CLI-01 partial: subcommand structure + each subcommand has its own --help; full CLI-01 closed when Plan 11-05 deletes `display.py:main()`).

Output:
  - ketu/cli/__init__.py — re-exports main
  - ketu/cli/parser.py — build_parser() + main(argv) with set_defaults dispatch
  - tests/cli/__init__.py + conftest.py + test_parser.py — test mirror established
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
@.planning/phases/11-cli-refactor-integration/11-RESEARCH.md

# Existing precedent: argparse-based CLI lives in tests/benchmark_aspects_batch.py — style reference
@tests/benchmark_aspects_batch.py

# What we're replacing (legacy interactive main() — kept INTACT this plan; deleted in Plan 11-05)
@ketu/display.py

# Test layout precedent — tests/houses/ mirrors ketu/houses/
# (No file ref needed; ls-only inspection)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ketu/cli/ subpackage with parser.py and __init__.py</name>
  <files>ketu/cli/__init__.py, ketu/cli/parser.py</files>
  <action>
Create the new `ketu/cli/` directory and two files inside it.

**ketu/cli/__init__.py** — minimal re-export:

```python
"""Ketu command-line interface.

Public entry point: :func:`main`. Used by both ``python -m ketu`` (via
``ketu/__main__.py``, repointed in Plan 11-05) and the ``ketu`` console
script (via ``[project.scripts]`` in pyproject.toml, repointed in Plan
11-05).
"""
from __future__ import annotations

from .parser import main

__all__ = ["main"]
```

**ketu/cli/parser.py** — argparse tree + main() dispatch:

Implement EXACTLY this shape (numpydoc-style docstrings on `build_parser` and `main`; type hints throughout; mypy --strict clean):

```python
"""Argparse tree builder + main() dispatch for ketu CLI.

Subcommand pattern uses ``set_defaults(func=...)`` per subparser so
``main()`` dispatches via ``args.func(args)`` rather than an
if-elif ladder. Top-level introspection flags (``--list-aspect-sets``,
``--list-house-systems``) short-circuit before subcommand dispatch, which
is why ``add_subparsers`` uses ``required=False``.

Plan 11-01 lays the skeleton; Plans 11-02..11-04 wire the real type
validator, subcommand dispatchers, formatters, and introspection.
"""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

# Stub dispatchers — real implementations land in Plans 11-03 (houses) and
# 11-04 (aspects). For now they print a "not yet implemented" notice and
# return 0; this lets Plan 11-01 ship a parseable, runnable skeleton with
# tests pinning the dispatch shape. Each plan that lands a real
# implementation imports its dispatcher and re-points set_defaults.

def _stub_aspects(args: argparse.Namespace) -> int:
    print("ketu aspects: not yet implemented (wired in Plan 11-04)",
          file=sys.stderr)
    return 0

def _stub_houses(args: argparse.Namespace) -> int:
    print("ketu houses: not yet implemented (wired in Plan 11-03)",
          file=sys.stderr)
    return 0

def _stub_list_aspect_sets() -> None:
    print("(--list-aspect-sets: wired in Plan 11-04)", file=sys.stderr)

def _stub_list_house_systems() -> None:
    print("(--list-house-systems: wired in Plan 11-04)", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argparse tree.

    Returns
    -------
    argparse.ArgumentParser
        Top-level parser with ``aspects`` and ``houses`` subparsers, plus
        top-level flags ``--harmonics``, ``--list-aspect-sets``, and
        ``--list-house-systems``. Subcommands use
        ``set_defaults(func=...)``; the dispatchers are stubs in Plan
        11-01 and replaced in subsequent plans.
    """
    parser = argparse.ArgumentParser(
        prog="ketu",
        description=(
            "Ketu — astronomical body positions, planetary aspects, and "
            "house cusps. Pure-NumPy library; no external runtime deps."
        ),
    )

    # Top-level introspection flags. These short-circuit in main() before
    # subcommand dispatch.
    parser.add_argument(
        "--list-aspect-sets",
        action="store_true",
        help="List available aspect set presets (classical, traditional, extended, all) and exit.",
    )
    parser.add_argument(
        "--list-house-systems",
        action="store_true",
        help="List available house systems (placidus, koch, porphyry) and exit.",
    )

    # Top-level --harmonics SPEC. Plan 11-01 declares it with type=str so
    # the parser is constructible; Plan 11-02 swaps in parse_harmonics_spec
    # which returns a length-14 np.bool_ mask. Default=None means "use the
    # CLASSICAL preset" (resolved by aspects_cmd in Plan 11-04).
    parser.add_argument(
        "--harmonics",
        type=str,
        default=None,
        metavar="SPEC",
        help=(
            "Aspect set selector. Named preset ('classical' [default], "
            "'traditional', 'extended', 'all' alias for 'extended'), or "
            "comma-separated indices into core.aspects (e.g. '0,4,7,9,13' "
            "= classical). Bare integers (e.g. '12') are rejected — use "
            "named presets or comma-separated lists."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=False,  # introspection flags work without a subcommand
        title="subcommands",
        metavar="{aspects,houses}",
    )

    # `ketu aspects --date ISO`
    p_aspects = subparsers.add_parser(
        "aspects",
        help="Compute body positions and aspects for a date/time (UTC).",
        description=(
            "Compute body positions and planetary aspects. Uses --harmonics "
            "from the top-level parser to filter the aspect set."
        ),
    )
    p_aspects.add_argument(
        "--date",
        required=True,
        metavar="ISO",
        help="UTC date-time, ISO 8601 (e.g. 2026-05-06T12:00:00Z).",
    )
    p_aspects.set_defaults(func=_stub_aspects)

    # `ketu houses --date ISO --lat F --lon F --system NAME`
    p_houses = subparsers.add_parser(
        "houses",
        help="Compute house cusps for a date/time/location.",
        description=(
            "Compute the 12 house cusps using a registered house system. "
            "At polar latitudes, --polar-fallback porphyry substitutes "
            "Porphyry cusps for offending elements; --polar-fallback raise "
            "(default) raises HighLatitudeError."
        ),
    )
    p_houses.add_argument(
        "--date", required=True, metavar="ISO",
        help="UTC date-time, ISO 8601 (e.g. 2026-05-06T12:00:00Z).",
    )
    p_houses.add_argument(
        "--lat", required=True, type=float, metavar="DEG",
        help="Geographic latitude in degrees (positive North).",
    )
    p_houses.add_argument(
        "--lon", required=True, type=float, metavar="DEG",
        help="Geographic longitude in degrees (positive East).",
    )
    p_houses.add_argument(
        "--system", choices=["placidus", "koch", "porphyry"],
        default="placidus",
        help="House system (default: placidus).",
    )
    p_houses.add_argument(
        "--polar-fallback", choices=["raise", "porphyry"], default="raise",
        help=(
            "Behavior at polar latitudes: 'raise' (default) raises "
            "HighLatitudeError; 'porphyry' substitutes Porphyry cusps for "
            "offending elements."
        ),
    )
    p_houses.set_defaults(func=_stub_houses)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point.

    Parameters
    ----------
    argv : sequence of str, optional
        Argument vector. Defaults to ``sys.argv[1:]`` when None — argparse
        convention. Tests inject explicit lists.

    Returns
    -------
    int
        Process exit code (0 = success). argparse errors raise SystemExit
        directly with code 2 before this returns.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Introspection short-circuits.
    if args.list_aspect_sets:
        _stub_list_aspect_sets()
        return 0
    if args.list_house_systems:
        _stub_list_house_systems()
        return 0

    # No subcommand → print help and return 0.
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0

    return int(func(args) or 0)
```

Notes:
- `from __future__ import annotations` (project convention; matches `ketu/houses/`).
- `Sequence[str] | None` for argv — works on Python 3.10+ thanks to `__future__ import annotations`.
- Stubs print to stderr (Plan 11-04 will replace with real impls; tests in this plan assert exit code 0 and that the stub message appears).
- No mypy ignore-comments. mypy --strict must be clean.
  </action>
  <verify>
1. `ls ketu/cli/` shows `__init__.py` and `parser.py`.
2. `python -c "from ketu.cli import main; print(main)"` prints a function.
3. `python -m venv venv && source venv/bin/activate && python -c "from ketu.cli.parser import build_parser; p = build_parser(); p.parse_args(['--help'])"` prints help and SystemExit 0 (capture stdout via subprocess if running interactively).
4. `mypy --strict ketu/cli/` reports no errors.
  </verify>
  <done>
- `ketu/cli/` directory created with `__init__.py` (re-exporting `main`) and `parser.py` (≥60 lines).
- `build_parser()` returns a parser with: prog='ketu', --list-aspect-sets, --list-house-systems, --harmonics (top-level), and `aspects` + `houses` subparsers each with their own --help text.
- `main()` short-circuits introspection flags, dispatches via `args.func`, falls back to `parser.print_help()` when no subcommand given.
- mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create tests/cli/ scaffold with conftest helpers and parser unit tests</name>
  <files>tests/cli/__init__.py, tests/cli/conftest.py, tests/cli/test_parser.py</files>
  <action>
Create three files mirroring the `tests/houses/` precedent.

**tests/cli/__init__.py** — empty marker (mirrors `tests/houses/__init__.py`).

**tests/cli/conftest.py** — shared CLI fixtures:

```python
"""Shared fixtures for tests/cli/.

The CLI is exercised by injecting argv into ``ketu.cli.main(argv)`` and
capturing stdout/stderr via pytest's ``capsys`` fixture. Subprocess-based
testing lives in test_legacy_byte_identical.py only (Plan 11-06) — every
other test should use in-process invocation for speed.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import pytest

# Make sure tests can locate the v1.0 fixture file (used in Plan 11-06).
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def invoke_main():
    """Return a callable that runs ``ketu.cli.main(argv)`` and returns the rc.

    Imported lazily inside the fixture so a missing import (e.g. during
    Plan 11-01 scaffolding) surfaces as a test failure, not a collection
    error.
    """
    def _invoke(argv: Sequence[str]) -> int:
        from ketu.cli import main
        return main(list(argv))
    return _invoke
```

**tests/cli/test_parser.py** — unit tests for parser shape + main() dispatch:

```python
"""Unit tests for ketu.cli.parser — argparse tree shape and main() dispatch."""
from __future__ import annotations

import pytest

from ketu.cli.parser import build_parser, main


class TestBuildParser:
    """build_parser() shape: prog, subparsers, top-level flags."""

    def test_prog_is_ketu(self):
        parser = build_parser()
        assert parser.prog == "ketu"

    def test_subparsers_present(self):
        """aspects and houses subparsers are registered."""
        parser = build_parser()
        # Inspect via parse_args round-trip: --help on each must not crash.
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["aspects", "--help"])
        assert exc.value.code == 0
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["houses", "--help"])
        assert exc.value.code == 0

    def test_aspects_requires_date(self, capsys):
        """`ketu aspects` without --date is rejected with code 2."""
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["aspects"])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--date" in err

    def test_houses_requires_date_lat_lon(self, capsys):
        """`ketu houses` without --date/--lat/--lon is rejected."""
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["houses"])
        assert exc.value.code == 2

    def test_houses_system_default_is_placidus(self):
        parser = build_parser()
        args = parser.parse_args([
            "houses",
            "--date", "2026-05-06T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
        ])
        assert args.system == "placidus"

    def test_houses_system_choices_enforced(self, capsys):
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([
                "houses",
                "--date", "2026-05-06T12:00:00Z",
                "--lat", "48.85", "--lon", "2.35",
                "--system", "regiomontanus",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "regiomontanus" in err or "invalid choice" in err

    def test_top_level_harmonics_present(self):
        parser = build_parser()
        # Sub-position; top-level flag goes BEFORE the subcommand.
        args = parser.parse_args([
            "--harmonics", "classical",
            "aspects", "--date", "2026-05-06T12:00:00Z",
        ])
        assert args.harmonics == "classical"  # str passthrough — Plan 11-02 swaps validator

    def test_introspection_flags_default_false(self):
        parser = build_parser()
        # Need a subcommand or main() will print help; here we just check
        # the namespace shape after a successful parse.
        args = parser.parse_args([
            "aspects", "--date", "2026-05-06T12:00:00Z",
        ])
        assert args.list_aspect_sets is False
        assert args.list_house_systems is False


class TestMainDispatch:
    """main(argv) entry point — short-circuit / dispatch / fallback."""

    def test_main_no_args_prints_help_returns_0(self, invoke_main, capsys):
        """`ketu` with no args prints help to stdout and returns 0
        (does NOT crash with AttributeError on missing args.func — Pitfall 4
        in research)."""
        rc = invoke_main([])
        assert rc == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower() or "ketu" in captured.out

    def test_main_list_aspect_sets_short_circuits(self, invoke_main, capsys):
        """--list-aspect-sets short-circuits before subcommand dispatch."""
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0
        # Stub message lives on stderr per Plan 11-01; Plan 11-04 replaces with real content.
        err = capsys.readouterr().err
        assert "list-aspect-sets" in err.lower() or "Plan 11-04" in err

    def test_main_list_house_systems_short_circuits(self, invoke_main, capsys):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
        err = capsys.readouterr().err
        assert "list-house-systems" in err.lower() or "Plan 11-04" in err

    def test_main_aspects_dispatches_to_func(self, invoke_main, capsys):
        """Stub aspects dispatcher returns 0 and writes its marker to stderr."""
        rc = invoke_main(["aspects", "--date", "2026-05-06T12:00:00Z"])
        assert rc == 0
        err = capsys.readouterr().err
        # Plan 11-04 will replace this with real output; here we just
        # confirm dispatch reached the stub.
        assert "Plan 11-04" in err or "not yet implemented" in err

    def test_main_houses_dispatches_to_func(self, invoke_main, capsys):
        """Stub houses dispatcher returns 0 and writes its marker to stderr."""
        rc = invoke_main([
            "houses",
            "--date", "2026-05-06T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
        ])
        assert rc == 0
        err = capsys.readouterr().err
        assert "Plan 11-03" in err or "not yet implemented" in err

    def test_main_unknown_subcommand_rejected(self, invoke_main, capsys):
        """Unknown subcommand → argparse SystemExit(2)."""
        with pytest.raises(SystemExit) as exc:
            invoke_main(["nonexistent-subcommand"])
        assert exc.value.code == 2
```

Notes:
- Tests use `invoke_main` fixture (in-process) — fast, no subprocess overhead.
- A few tests will need to be UPDATED in later plans (e.g. `test_main_aspects_dispatches_to_func` checks for "Plan 11-04" stub marker; Plan 11-04 must update or replace those assertions to check real behaviour). This is intentional — leaves a clear breadcrumb for follow-on plans.
- All tests pass on Python 3.10+ (no walrus, no union types in code body).
  </action>
  <verify>
Run from repo root with the test virtualenv active:

```
pytest tests/cli/test_parser.py -v
```

Expected: 12 tests pass (or however many were defined above). 0 errors.

Also confirm:
- `pytest tests/ -v` — full suite still green (655+ existing tests + new tests/cli/test_parser.py tests; no regression).
- `mypy --strict ketu/cli/` clean.
  </verify>
  <done>
- `tests/cli/__init__.py` exists (empty marker).
- `tests/cli/conftest.py` exposes `invoke_main` fixture and FIXTURES_DIR Path constant.
- `tests/cli/test_parser.py` contains TestBuildParser + TestMainDispatch with at least 10 passing tests covering: prog name, subparser presence, required args, default --system=placidus, --system choices enforcement, --harmonics top-level, introspection flag defaults, no-args help fallback, both subcommand stub dispatch, list-* short-circuit, unknown-subcommand rejection.
- All new tests pass; full project test suite still green.
  </done>
</task>

</tasks>

<verification>
- `python -c "from ketu.cli import main; main(['--help'])"` prints help, exits 0.
- `pytest tests/cli/test_parser.py -v` — all green.
- `pytest tests/ -v` — full suite green (no regression on the existing 638 tests).
- `mypy --strict ketu/cli/` — clean.
- `grep -r "from ketu.cli" tests/cli/` shows the test file imports work.
</verification>

<success_criteria>
- ketu/cli/ subpackage created with proper __init__.py + parser.py.
- build_parser() exposes a complete argparse tree (top-level flags + aspects + houses subparsers + own --help per subcommand).
- main() handles introspection short-circuit, subcommand dispatch via set_defaults(func=...), and the no-subcommand fallback (prints help, returns 0) — Pitfall 4 prevented.
- tests/cli/ scaffolding established (mirrors tests/houses/).
- ≥10 unit tests pinning the parser shape and main() dispatch contract.
- 0 regressions in the full project test suite; mypy --strict clean.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-01-cli-parser-scaffolding-SUMMARY.md` documenting:
- Files created (cli/__init__.py, cli/parser.py, tests/cli/__init__.py, tests/cli/conftest.py, tests/cli/test_parser.py)
- Key decisions: stub dispatchers (replaced in 11-03/11-04), top-level --harmonics with type=str placeholder (real validator in 11-02), subparsers required=False
- Test count delta (added N tests/cli/test_parser.py tests)
- Any deviations from plan
</output>
