# Phase 11: CLI Refactor & Integration — Research

**Researched:** 2026-05-07
**Domain:** Python stdlib `argparse` (subcommands, custom type validators, dispatch), CLI testing with pytest `capsys` + `monkeypatch`, ISO 8601 date parsing under Python 3.10+, byte-identical regression fixtures
**Confidence:** HIGH (argparse patterns are stdlib, codebase entry points read directly, v1.0 main() inspected at the v1.0.0 tag, prior CLI precedent in `tests/benchmark_aspects_batch.py`)

> **Note on `<user_constraints>`:** No CONTEXT.md exists for this phase (`/gsd:discuss-phase` was not run). All requirements from `.planning/REQUIREMENTS.md` (CLI-01 through CLI-06) and the success criteria in `.planning/ROADMAP.md` Phase 11 entry are treated as locked specs. Implementation details left open are flagged as "Claude's discretion" inline.

---

## Summary

Phase 11 replaces `ketu/display.py:main()`'s legacy interactive `input()` prompt with an argparse-based CLI exposing two subcommands (`aspects` and `houses`) plus introspection flags (`--list-aspect-sets`, `--list-house-systems`). The Python APIs that back each subcommand already exist and are stable: Phase 9 shipped `ketu.aspects.presets` (CLASSICAL/TRADITIONAL/EXTENDED masks + `resolve_aspect_set`) and Phase 10 shipped `ketu.houses` (`calculate_houses`, `house_of`, `SYSTEMS`, `HighLatitudeError`). The CLI is the surface that exposes them — no new computation lives here.

The hard engineering items are: (1) **CLI-03 byte-identical legacy compat** — `--harmonics all` must reproduce v1.0's exact stdout for a captured reference invocation; the v1.0 `main()` printed positions + aspects + a 3-aspect timing demo, and that exact format must be preserved when `--harmonics all` is in effect. The v1.0 output must be captured FROM THE `v1.0.0` GIT TAG (the legacy `main()` is unchanged at HEAD vs the tag), saved as a fixture, and asserted byte-equal in CI. (2) **CLI-06 resolved-config header vs CLI-03 byte-identical**: the header must NOT corrupt `--harmonics all` stdout. Cleanest resolution: emit the resolved-config header to **stderr**, keeping stdout pristine for the legacy escape hatch. Documenting this convention is a Plan-level decision. (3) **`--harmonics SPEC` parser**: must accept preset names, `all` (alias for `extended`), explicit harmonic-index lists `9,10,11`, and reject bare integers `12` with a helpful error. The cleanest pattern is `type=harmonics_spec` callable raising `argparse.ArgumentTypeError` (auto-rendered as `error: argument --harmonics: <message>`).

**Primary recommendation:** Create a new `ketu/cli/` subpackage (mirroring `ketu/aspects/` and `ketu/houses/` layout) with `__init__.py` re-exporting `main`, `parser.py` building the argparse tree, `harmonics_spec.py` with the `--harmonics` type validator, `aspects_cmd.py` and `houses_cmd.py` for subcommand dispatchers (via `set_defaults(func=...)`), `formatters.py` for the resolved-config header. Repoint `[project.scripts] ketu` to `ketu.cli:main`. Keep `display.py:print_positions` and `print_aspects` callable as library functions (used by `aspects_cmd`); only delete `display.py:main()`. Tests live in `tests/cli/` mirroring the subpackage. Capture the v1.0 byte-identical fixture from the `v1.0.0` git tag using `subprocess.run(['python', '-m', 'ketu'], input=...)` once, freeze it under `tests/cli/fixtures/v1_0_legacy_output.txt`, regress against it in CI.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `argparse` | stdlib | Subcommands (`add_subparsers`), `type=` validators, `set_defaults(func=...)` dispatch, `--help` auto-generation | Project requirement: REQUIREMENTS.md line 100 explicitly forbids `click`/`typer` ("argparse stdlib is sufficient; no new runtime deps"). v1.1 keeps the zero-runtime-dep contract beyond NumPy. |
| `datetime` + `zoneinfo` | stdlib | Parse `--date ISO`, build timezone-aware UTC datetime | Already used in `ketu/ephemeris/time.py:utc_to_julian`. ISO parsing via `datetime.fromisoformat()`. |
| `numpy` | >=1.20 (existing) | Read aspect output, format cusps array | The project's only runtime dep. CLI consumes already-vectorized APIs; no new array work. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `sys` | stdlib | `sys.argv` injection point, `sys.stderr` for resolved-config header, `sys.exit()` return code | Standard CLI plumbing |
| `pytest` (existing) | — | `capsys` fixture for stdout/stderr capture, `monkeypatch.setattr(sys, "argv", ...)` for arg injection, `pytest.raises(SystemExit)` for argparse error paths | Mirror existing test style in `tests/test_ketu.py:TestMain` |
| `subprocess` | stdlib | One-shot byte-identical regression: invoke `python -m ketu --harmonics all ...` in a subprocess, diff stdout against the v1.0 fixture | Pure-import tests cannot capture the exact bytes the user sees (encoding, line endings); subprocess is the honest surface for CLI-03 |
| `pathlib` | stdlib | Locate `tests/cli/fixtures/v1_0_legacy_output.txt` relative to the test file | Project convention (see `tests/houses/conftest.py` fixture loading) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `argparse` | `click` | Forbidden by REQUIREMENTS.md line 100 (no new runtime deps). |
| `argparse` | `typer` | Same. Also depends on Click + Pydantic; even more transitive deps. |
| `argparse` subcommands | Single command + positional `mode` | Subcommands give per-subcommand `--help`, distinct argument schemas (houses needs `--lat/--lon`, aspects doesn't), and idiomatic `ketu houses --help` UX. CLI-01 success criterion explicitly says "each subcommand has its own `--help`". |
| `datetime.fromisoformat` | `dateutil.parser.parse` | `dateutil` is not a runtime dep. `fromisoformat` covers ISO 8601 (with the Python-3.10 'Z' caveat documented below). |
| Subprocess test for CLI-03 | In-process `main(['--harmonics', 'all', ...])` + `capsys` | Subprocess is more honest (mirrors what the user runs) but is slower. Use subprocess for the CLI-03 fixture regression; in-process for everything else. |
| Single `ketu/cli.py` module | `ketu/cli/` subpackage | Subpackage layout matches existing `ketu/aspects/` and `ketu/houses/` precedent; isolates argparse from formatters from harmonics-spec parser; easier to test piece-by-piece. |

**Installation:** No new dependencies. Update `pyproject.toml`:
```toml
[project.scripts]
ketu = "ketu.cli:main"   # was: "ketu.display:main"

[tool.setuptools]
packages = ["ketu", "ketu.ephemeris", "ketu.aspects", "ketu.cycles", "ketu.cache", "ketu.houses", "ketu.cli"]
```

---

## Architecture Patterns

### Recommended Project Structure

```
ketu/cli/
├── __init__.py            # Re-exports main()
├── parser.py              # build_parser() — argparse tree (top-level + subparsers)
├── harmonics_spec.py      # parse_harmonics_spec(s: str) -> AspectSetSpec — type= callable
├── aspects_cmd.py         # cmd_aspects(args) — dispatches to print_positions/print_aspects
├── houses_cmd.py          # cmd_houses(args) — dispatches to ketu.houses.calculate_houses
├── formatters.py          # format_resolved_config_header(...) — CLI-06 stderr header
└── introspection.py       # cmd_list_aspect_sets(), cmd_list_house_systems()

tests/cli/
├── __init__.py
├── conftest.py            # Fixture loaders, subprocess helper
├── test_parser.py         # build_parser() — argparse correctness, defaults, choices
├── test_harmonics_spec.py # parse_harmonics_spec() — preset names, lists, rejection
├── test_aspects_cmd.py    # cmd_aspects() — output format, --harmonics propagation
├── test_houses_cmd.py     # cmd_houses() — date parsing, system dispatch, polar fallback
├── test_introspection.py  # --list-aspect-sets / --list-house-systems output
├── test_resolved_header.py # CLI-06 — header rendered to stderr, content matches selected set
├── test_legacy_byte_identical.py  # CLI-03 — subprocess regression vs v1.0 fixture
└── fixtures/
    └── v1_0_legacy_output.txt     # Captured from `git checkout v1.0.0; python -m ketu`

ketu/display.py            # MODIFIED: keep print_positions, print_aspects; DELETE main()
ketu/__main__.py           # MODIFIED: from ketu.cli import main
pyproject.toml             # MODIFIED: [project.scripts] ketu = "ketu.cli:main"
```

### Pattern 1: argparse subcommands with `set_defaults(func=...)` dispatch (CLI-01)

**What:** Top-level parser holds global flags (`--harmonics`, `--list-aspect-sets`, `--list-house-systems`); `add_subparsers(dest='command', required=False)` exposes `aspects` and `houses` subcommands; each subparser gets its own arguments and `set_defaults(func=cmd_xxx)`. `main()` calls `args.func(args)` after parsing.

**Why `required=False`:** Top-level introspection flags (`--list-aspect-sets`) must work without a subcommand. With `required=True`, `ketu --list-aspect-sets` would fail with "the following arguments are required: command".

**When to use:** Whenever you'd write an `if cmd == "aspects": ... elif cmd == "houses": ...` ladder. Function dispatch is the documented argparse pattern (see Sources).

**Example:**
```python
# ketu/cli/parser.py
# Source: https://docs.python.org/3/library/argparse.html (subcommands section)
import argparse
from .harmonics_spec import parse_harmonics_spec
from .aspects_cmd import cmd_aspects
from .houses_cmd import cmd_houses
from .introspection import cmd_list_aspect_sets, cmd_list_house_systems

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ketu",
        description="Ketu — astronomical body positions and planetary aspects.",
    )
    # Top-level introspection flags. These short-circuit to a printer and exit.
    parser.add_argument(
        "--list-aspect-sets", action="store_true",
        help="List available aspect set presets and exit.",
    )
    parser.add_argument(
        "--list-house-systems", action="store_true",
        help="List available house systems and exit.",
    )
    # Top-level --harmonics SPEC default applies when subcommand is `aspects`.
    parser.add_argument(
        "--harmonics", type=parse_harmonics_spec, default=None,
        metavar="SPEC",
        help=(
            "Aspect set: 'classical' (default), 'traditional', 'extended', "
            "'all' (alias for 'extended', preserves v1.0 14-aspect output), "
            "or comma-separated indices 0-13 (e.g. '0,4,7,9,13'). "
            "Bare integers (e.g. '12') are rejected; use named presets or "
            "explicit lists."
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    # `ketu aspects ...`
    p_aspects = subparsers.add_parser(
        "aspects",
        help="Compute body positions and aspects for a date/time.",
    )
    p_aspects.add_argument("--date", required=True, metavar="ISO",
                           help="UTC date-time, ISO 8601 (e.g. 2026-05-06T12:00:00Z).")
    p_aspects.set_defaults(func=cmd_aspects)

    # `ketu houses ...`
    p_houses = subparsers.add_parser(
        "houses",
        help="Compute house cusps for a date/time/location.",
    )
    p_houses.add_argument("--date", required=True, metavar="ISO")
    p_houses.add_argument("--lat", required=True, type=float)
    p_houses.add_argument("--lon", required=True, type=float)
    p_houses.add_argument("--system", choices=["placidus", "koch", "porphyry"],
                          default="placidus")
    p_houses.add_argument("--polar-fallback", choices=["raise", "porphyry"],
                          default="raise")
    p_houses.set_defaults(func=cmd_houses)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Introspection short-circuits.
    if args.list_aspect_sets:
        cmd_list_aspect_sets()
        return 0
    if args.list_house_systems:
        cmd_list_house_systems()
        return 0

    if not getattr(args, "func", None):
        parser.print_help()
        return 0

    return int(args.func(args) or 0)
```

### Pattern 2: `type=` callable raising `ArgumentTypeError` (CLI-02)

**What:** Custom argparse type that validates the `--harmonics SPEC` syntax and resolves to a length-14 boolean mask via the existing `resolve_aspect_set`.

**Why this shape:** argparse catches `ArgumentTypeError`/`TypeError`/`ValueError` from `type=` callables and renders a clean `error: argument --harmonics: <message>` (no traceback). Per docs: "If the function raises ArgumentTypeError, TypeError, or ValueError, the exception is caught and a nicely formatted error message is displayed."

**Spec semantics:**
- `"classical"` / `"traditional"` / `"extended"` → preset (case-insensitive)
- `"all"` → alias for `"extended"` (CLI-02 explicitly lists `all`; ROADMAP Goal: "backward compat preserved via `--harmonics all`")
- `"9,10,13"` (comma-separated, all integers in `[0, 14)`) → list of canonical aspect indices
- `"12"` (a single bare integer with no comma) → REJECTED with hint to named presets (REQUIREMENTS.md line 101: "Bare `--harmonics 12` integer parsing — Too ambiguous (set vs single vs range); force named presets or explicit list")
- `""` empty → reject

**Example:**
```python
# ketu/cli/harmonics_spec.py
# Source: https://docs.python.org/3/library/argparse.html (custom types)
import argparse
import numpy as np
from ketu.aspects.presets import resolve_aspect_set, _PRESET_BY_NAME  # internal use OK

_PRESET_NAMES = frozenset({"classical", "traditional", "extended", "all"})


def parse_harmonics_spec(value: str) -> np.ndarray:
    """argparse type= callable for --harmonics SPEC.

    Returns a length-14 np.bool_ mask. Raises ArgumentTypeError on bad input.
    """
    if not value:
        raise argparse.ArgumentTypeError(
            "--harmonics requires a value (named preset or comma-separated list)"
        )

    s = value.strip().lower()

    # Preset names (including 'all' alias for 'extended').
    if s in _PRESET_NAMES:
        if s == "all":
            s = "extended"
        return resolve_aspect_set(s)  # str path → preset mask

    # Comma-separated indices.
    if "," in s:
        try:
            indices = [int(x) for x in s.split(",")]
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}; expected comma-separated "
                f"integers in [0, 14) (e.g. '0,4,7,9,13')"
            )
        try:
            return resolve_aspect_set(indices)  # list[int] path
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))

    # Bare single integer — explicitly rejected per REQUIREMENTS.md line 101.
    try:
        int(s)
    except ValueError:
        pass
    else:
        valid = sorted(_PRESET_NAMES)
        raise argparse.ArgumentTypeError(
            f"bare integer {value!r} is ambiguous (single? harmonic? subset?); "
            f"use a named preset ({', '.join(valid)}) or a comma-separated "
            f"list (e.g. '{value},...')"
        )

    raise argparse.ArgumentTypeError(
        f"unrecognized harmonics spec {value!r}; "
        f"expected one of {sorted(_PRESET_NAMES)} or comma-separated indices"
    )
```

### Pattern 3: ISO 8601 `--date` parsing with Python-3.10 'Z' compat shim

**What:** `--date 2026-05-06T12:00:00Z` → timezone-aware UTC `datetime` → JD via existing `ketu.calculations.utc_to_julian`.

**The Python 3.10 trap:** `datetime.fromisoformat("2026-05-06T12:00:00Z")` raises `ValueError` on Python 3.10. It works on 3.11+ (Python 3.11 expanded `fromisoformat` to "most ISO 8601 formats" including the `Z` suffix — see [What's New in Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html)). Project's `requires-python = ">=3.10"`, so the CLI MUST support both. The standard workaround: replace trailing `Z` with `+00:00` before parsing.

**Example:**
```python
# ketu/cli/houses_cmd.py (date helper, also reusable in aspects_cmd)
from datetime import datetime, timezone
from ketu.ephemeris.time import utc_to_julian

def parse_iso_utc(value: str) -> float:
    """Parse ISO 8601 string to Julian Date. Handles trailing 'Z' on Python 3.10.

    Source: https://docs.python.org/3/library/datetime.html
    Python 3.10 fromisoformat() does not accept 'Z'; 3.11+ does. Replace
    'Z' with '+00:00' for cross-version compat.
    """
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise SystemExit(
            f"error: --date {value!r} is not a valid ISO 8601 datetime "
            f"(expected e.g. '2026-05-06T12:00:00Z' or '2026-05-06T12:00:00+00:00'); {e}"
        )
    if dt.tzinfo is None:
        # Naive datetime → assume UTC, matches utc_to_julian's existing convention.
        dt = dt.replace(tzinfo=timezone.utc)
    return utc_to_julian(dt)
```

### Pattern 4: Resolved-config header to **stderr** (CLI-06 reconciled with CLI-03)

**What:** The CLI-06 header (`# Aspect set: classical [0°, 60°, 90°, 120°, 180°]`) goes to **stderr**, NOT stdout. This is the cleanest way to satisfy both:
- CLI-06: every CLI invocation echoes a resolved-config header (✓ — present, just on stderr)
- CLI-03: `--harmonics all` byte-identical to v1.0 (✓ — stdout is untouched)

**Convention:** stdout = data; stderr = diagnostics + headers. This matches Unix conventions and is the standard answer for "how do you log without polluting machine-parseable output". `git status`, `make`, `pytest -v` etc. all use this split.

**Header format (proposed; planner has discretion):**
```
# Ketu v1.1.0
# Aspect set: classical (5 aspects: Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°)
# House system: placidus
```

Format details (e.g. degree symbol vs `deg`, comma vs space-separated, "5 aspects" vs explicit list) are Plan-level decisions. The acceptance test should:
- Assert header is emitted to stderr (use `capsys.readouterr().err`).
- Assert it contains `# Aspect set: <preset_name>`.
- Assert it lists the aspect angles (specific text format flexible).
- Assert stdout is BYTE-IDENTICAL when `--harmonics all` is set.

**Example:**
```python
# ketu/cli/formatters.py
import sys
import numpy as np
from ketu.core import aspects as ASPECTS

def emit_resolved_config(mask: np.ndarray, preset_name: str | None,
                        house_system: str | None) -> None:
    """CLI-06: echo resolved config to stderr (keeps stdout pristine for CLI-03)."""
    selected_angles = ASPECTS["angle"][mask]
    selected_names = [n.decode() for n in ASPECTS["name"][mask]]
    name_label = preset_name or "custom"
    angles_fmt = ", ".join(
        f"{name} {int(angle)}°" for name, angle in zip(selected_names, selected_angles)
    )
    print(f"# Ketu v1.1.0", file=sys.stderr)
    print(f"# Aspect set: {name_label} ({len(selected_names)} aspects: {angles_fmt})",
          file=sys.stderr)
    if house_system:
        print(f"# House system: {house_system}", file=sys.stderr)
```

### Pattern 5: Byte-identical CLI-03 regression via captured fixture

**What:** Capture the v1.0 stdout for a known invocation ONCE from the `v1.0.0` git tag, freeze it under `tests/cli/fixtures/v1_0_legacy_output.txt`, regress in CI by running `python -m ketu --harmonics all aspects --date <fixed-iso>` in a subprocess and asserting `stdout == fixture`.

**Capture procedure (one-shot, documented in plan):**
```bash
# Run from a clean checkout of v1.0.0 tag (or a worktree)
git worktree add /tmp/ketu-v1.0 v1.0.0
cd /tmp/ketu-v1.0
python -m venv venv && source venv/bin/activate && pip install -e .
# v1.0 main() reads three input() lines: date (YYYY-MM-DD), time (HH:MM), tz
# Use a fixed reference invocation (planner picks date; recommend J2000.0 epoch
# at 12:00 UTC for stability: 2000-01-01 / 12:00 / UTC).
printf "2000-01-01\n12:00\nUTC\n" | python -m ketu \
  > /home/loc/workspace/ketu/tests/cli/fixtures/v1_0_legacy_output.txt
```

**Regression test shape:**
```python
# tests/cli/test_legacy_byte_identical.py
import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "v1_0_legacy_output.txt"

def test_harmonics_all_byte_identical_to_v1_0():
    """CLI-03: --harmonics all stdout must match v1.0 fixture byte-for-byte."""
    expected = FIXTURE.read_bytes()
    # Same date the fixture was captured for.
    result = subprocess.run(
        [sys.executable, "-m", "ketu",
         "--harmonics", "all",
         "aspects", "--date", "2000-01-01T12:00:00Z"],
        capture_output=True, check=True,
    )
    assert result.stdout == expected, (
        "CLI-03 regression: --harmonics all stdout drifted from v1.0. "
        "Diff between captured fixture and current output."
    )
```

**Critical caveat:** v1.0's `main()` prints a `------------- Aspect Timing Example -------------` block scanning `find_aspects_between_dates(jday-15, jday+15, sun_id, moon_id)` and printing the first 3 results. This is part of the byte-identical contract. The new `aspects` subcommand must reproduce this trailing section EXACTLY when `--harmonics all` is in effect. Plan should consider whether this is opt-in (`--legacy-demo`) or always emitted under `all`. Marking as Open Question 2.

### Anti-Patterns to Avoid

- **Resolved-config header on stdout:** breaks CLI-03 byte-identical guarantee; forces ugly opt-out flag. Use stderr.
- **Single mega-`main()` with if-elif on subcommand string:** what we just removed. Use `set_defaults(func=...)` per subcommand.
- **Calling `argparse` from inside `display.py`:** keeps the CLI tangled with display helpers. New `ketu/cli/` subpackage isolates concerns; `display.py` keeps `print_positions`/`print_aspects` as pure library helpers.
- **Hand-rolling ISO 8601 parsing with regex:** use `datetime.fromisoformat` + the `Z`→`+00:00` shim. Python 3.11+ handles `Z` natively; the shim covers 3.10.
- **Importing argparse types into `ketu/`'s public namespace (`__init__.py`):** CLI is a leaf consumer, not part of the library API. Keep `from ketu.cli import main` only at the entry point (`__main__.py` and `pyproject.toml [project.scripts]`).
- **Putting the v1.0 fixture under `tests/fixtures/` (project-wide):** namespace it under `tests/cli/fixtures/` to match the `tests/houses/fixtures/reference_charts.json` precedent.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Subcommand dispatch | `if cmd == "aspects": ... elif ...` ladder | `subparsers.add_parser(...).set_defaults(func=...)` + `args.func(args)` | argparse-documented pattern; scales to N subcommands without parser edits; also auto-generates per-subcommand `--help`. |
| `--harmonics` validation error rendering | Custom error class + manual stderr printing | `argparse.ArgumentTypeError` raised from `type=` callable | argparse auto-renders as `error: argument --harmonics: <message>` and exits with code 2; matches every other argparse program on the system. |
| Aspect spec parsing | Custom AST/regex over `"classical \| 0,4,7"` | Reuse `ketu.aspects.presets.resolve_aspect_set` (Phase 9 deliverable) | Already accepts `str` (preset name), `Sequence[int]` (indices), and `np.ndarray[bool]`. CLI's `harmonics_spec` is a thin tokenizer that delegates resolution. |
| House system dispatch | `if system == "placidus": ...` in CLI | `ketu.houses.calculate_houses(system=args.system)` (Phase 10 deliverable) | The houses module already dispatches via `SYSTEMS` registry. CLI passes through. |
| ISO 8601 date parsing | `re.match(r"\d{4}-\d{2}-\d{2}T...")` | `datetime.fromisoformat` + `Z`→`+00:00` shim | stdlib + 1-line workaround handles all valid ISO 8601 inputs the user will type. dateutil is a forbidden new runtime dep. |
| Capturing stdout/stderr in tests | `redirect_stdout` context manager + `io.StringIO` | pytest's `capsys` fixture (already used in `tests/test_ketu.py:TestDisplay`) | Standard pytest idiom; no new infrastructure. |
| Byte-identical regression infrastructure | Custom diff/snapshot tool | Plain `subprocess.run(...).stdout == fixture_bytes` | The whole point of CLI-03 is byte equality; a raw bytes comparison is the strongest assertion possible. No syrupy/snapshot library needed. |
| JD conversion from datetime | New helper | `ketu.ephemeris.time.utc_to_julian` (existing) | Already used everywhere; mature; tested. CLI just calls it. |

**Key insight:** Phase 11 is almost entirely glue. Every domain primitive (preset resolution, JD conversion, house calculation, aspect calculation, formatting) already exists in `ketu.{aspects,houses,ephemeris,display}`. The only new code is argparse wiring + the `--harmonics` syntax tokenizer + a stderr formatter + tests. Resist the temptation to duplicate or "improve" upstream APIs in the CLI layer.

---

## Common Pitfalls

### Pitfall 1: `add_subparsers(required=True)` blocks `--list-aspect-sets`

**What goes wrong:** With `required=True`, `ketu --list-aspect-sets` exits with `error: the following arguments are required: command` because the subcommand is missing.

**Why it happens:** argparse evaluates the `required=True` constraint regardless of which top-level flags fired. The user's intent ("just list, no subcommand needed") doesn't reach the parser.

**How to avoid:** Use `required=False`. In `main()`, after `parse_args`, branch: if introspection flag set → handle and return; elif `args.func` exists → dispatch; else → `parser.print_help()`.

**Warning signs:** `tests/cli/test_introspection.py` invocations of `ketu --list-aspect-sets` raising `SystemExit` with non-zero code.

### Pitfall 2: Python 3.10 `datetime.fromisoformat('...Z')` raises `ValueError`

**What goes wrong:** `--date 2026-05-06T12:00:00Z` works on Python 3.11+ but raises `ValueError: Invalid isoformat string: '2026-05-06T12:00:00Z'` on Python 3.10.

**Why it happens:** `datetime.fromisoformat` was expanded to support most of ISO 8601 (including `Z`) in Python 3.11 ([Python 3.11 release notes](https://docs.python.org/3.11/whatsnew/3.11.html)). On 3.10 it only accepts what `isoformat()` emits — `+00:00`, never `Z`.

**How to avoid:** Replace trailing `Z` with `+00:00` before calling `fromisoformat`. CI tests must run on 3.10 to catch this (project supports 3.10/3.11/3.12/3.13 per pyproject classifiers).

**Warning signs:** Tests pass on 3.11+ but `pytest tests/cli/` fails on 3.10 with "Invalid isoformat string".

### Pitfall 3: Resolved-config header on stdout breaks CLI-03 byte-identity

**What goes wrong:** Emit `# Aspect set: ...` to stdout, then `--harmonics all` adds a header line that v1.0 didn't have, and the byte-identical fixture comparison fails.

**Why it happens:** Conflating "user-visible output" (header for humans) with "machine-parseable output" (data for scripts/tests). v1.0's stdout was pure data; CLI-06 is metadata.

**How to avoid:** Header → stderr; data → stdout. Standard Unix convention. The CLI-03 byte test asserts only `result.stdout`, never `result.stderr`. CLI-06 test asserts the header on stderr.

**Warning signs:** `test_harmonics_all_byte_identical_to_v1_0` fails because of an extra leading `# ...` line; or CLI-06 test asserts `captured.out` instead of `captured.err`.

### Pitfall 4: Forgetting that `args.func` is absent when no subcommand is given

**What goes wrong:** `ketu` (no args) → `args.func` is unset → `args.func(args)` raises `AttributeError`.

**Why it happens:** `set_defaults(func=...)` only fires for the chosen subparser. With `required=False`, no subparser is chosen → `args` lacks `func`.

**How to avoid:** Use `getattr(args, "func", None)` and fall back to `parser.print_help()`. (See Pattern 1 example above.)

**Warning signs:** `ketu` with no args crashes with `AttributeError: 'Namespace' object has no attribute 'func'`.

### Pitfall 5: `bool` is a subclass of `int` in Python — bare integer check trap

**What goes wrong:** A user passes `--harmonics 0` and the parser silently treats it as preset index `0` (Conjunction-only)? Or `--harmonics 12` should reject (per spec) but `int("12")` succeeds?

**Why it happens:** `int(s)` succeeds for any digit-only string. The "bare integer rejection" rule is policy, not arithmetic.

**How to avoid:** Detect the absence of comma BEFORE `int()`. The spec is: comma-present → list path; comma-absent + valid int → REJECT explicitly with helpful error; comma-absent + non-int + not-a-preset → unrecognized error. (See Pattern 2 example.)

**Warning signs:** Test `--harmonics 12` does NOT raise SystemExit, or raises with the wrong error text.

### Pitfall 6: v1.0 `main()` includes a "Aspect Timing Example" block — easy to miss

**What goes wrong:** Plan implements `aspects` subcommand printing positions + aspects, captures the v1.0 fixture, then byte-identical fails because v1.0 ALSO printed three Sun-Moon timing demo lines under `------------- Aspect Timing Example -------------`.

**Why it happens:** The legacy `main()` (verified at `git show v1.0.0:ketu/display.py`) calls `find_aspects_between_dates(jday - 15, jday + 15, sun_id, moon_id)` and prints the first 3 results. This is part of the v1.0 stdout contract.

**How to avoid:** Read the v1.0 `main()` carefully (already done in this research; see file at `git show v1.0.0:ketu/display.py`). The new `aspects` subcommand under `--harmonics all` MUST emit this trailing block in the same format. Or: gate it behind `--legacy-demo` and capture the v1.0 fixture WITHOUT it. Decision deferred to plan.

**Warning signs:** `test_harmonics_all_byte_identical_to_v1_0` fails with diff showing missing `------------- Aspect Timing Example -------------` and 3 lines of "Sun ... Moon at ...".

### Pitfall 7: `pyproject.toml [project.scripts]` not updated → `ketu` still routes to old `display.main`

**What goes wrong:** Implementer renames `ketu.cli:main` but forgets `pyproject.toml`, then `pip install -e .` still installs the old entry point. Manual testing succeeds (`python -m ketu` uses `__main__.py`), but `ketu` (the installed script) breaks or shows old behavior.

**Why it happens:** Two parallel entry points: the `__main__.py` module (used by `python -m ketu`) and the `[project.scripts]` console script (used by `ketu`). Both must be updated.

**How to avoid:** Update both in the SAME plan/commit:
1. `pyproject.toml`: `ketu = "ketu.cli:main"` (was: `ketu.display:main`).
2. `ketu/__main__.py`: `from ketu.cli import main`.
3. Add `ketu.cli` to `[tool.setuptools] packages` list.
4. Reinstall via `pip install -e .` so the script entry point is regenerated.

**Warning signs:** `pip show ketu` shows console_scripts pointing to `ketu.display:main`; manual `ketu` invocation prompts for input (legacy interactive mode) instead of showing argparse help.

### Pitfall 8: Coverage drop on `display.py:main` deletion

**What goes wrong:** Deleting the legacy interactive `main()` removes lines that `tests/test_ketu.py:TestMain.test_main_invalid_input` exercises. If the test isn't updated/removed, it imports `from ketu.display import main` and ImportError-fails. Also project coverage may drop (the deleted lines are subtracted from numerator AND denominator, but net effect varies).

**Why it happens:** `tests/test_ketu.py:102` does `from ketu.display import main` and `tests/test_ketu.py:377-387` defines `TestMain.test_main_invalid_input`. These have to be reworked to import from `ketu.cli`.

**How to avoid:** Plan task explicitly: (a) remove `main` from `display.py:__all__`, (b) delete the `def main()` body, (c) update `tests/test_ketu.py` to drop the import + delete `TestMain` (or move its intent to `tests/cli/`). Coverage check post-refactor.

**Warning signs:** `pytest tests/test_ketu.py` ImportError; coverage report shows `ketu.cli.parser` at 0% because no tests target it yet.

### Pitfall 9: `argparse` writes errors to stderr and `SystemExit(2)` — testing requires both

**What goes wrong:** Testing `--harmonics 12` rejection looks for the error message in `capsys.readouterr().out`, but argparse writes errors to stderr and exits. Test sees an empty `out` and a confusing `SystemExit` and assumes nothing happened.

**Why it happens:** argparse's error path is `_sys.stderr.write(...)` + `_sys.exit(2)`. capsys still captures stderr if you read `.err`.

**How to avoid:** Test pattern is `with pytest.raises(SystemExit) as excinfo: main(['--harmonics', '12'])` then assert `excinfo.value.code == 2` and `"bare integer" in capsys.readouterr().err`.

**Warning signs:** Test silently passes because the assertion target is empty stdout; or test fails with "DID NOT RAISE".

---

## Code Examples

Verified patterns from official sources.

### Example 1: Subparsers with function dispatch (CLI-01)

```python
# Source: https://docs.python.org/3/library/argparse.html (sub-commands section)
import argparse

def cmd_aspects(args):
    print(f"aspects: date={args.date}")

def cmd_houses(args):
    print(f"houses: date={args.date} lat={args.lat}")

parser = argparse.ArgumentParser(prog="ketu")
subparsers = parser.add_subparsers(dest="command", required=False)

p_aspects = subparsers.add_parser("aspects")
p_aspects.add_argument("--date", required=True)
p_aspects.set_defaults(func=cmd_aspects)

p_houses = subparsers.add_parser("houses")
p_houses.add_argument("--date", required=True)
p_houses.add_argument("--lat", type=float, required=True)
p_houses.set_defaults(func=cmd_houses)

args = parser.parse_args()
if hasattr(args, "func"):
    args.func(args)
else:
    parser.print_help()
```

### Example 2: Custom `type=` validator with `ArgumentTypeError` (CLI-02)

```python
# Source: https://docs.python.org/3/library/argparse.html (custom-types section)
import argparse

def positive_int(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid integer")
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{ivalue} must be positive")
    return ivalue

parser = argparse.ArgumentParser()
parser.add_argument("--n", type=positive_int)
# $ prog --n abc
# error: argument --n: 'abc' is not a valid integer
```

### Example 3: pytest testing argparse (CLI test fixtures)

```python
# Source: https://til.simonwillison.net/pytest/pytest-argparse
# and https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
import pytest
from ketu.cli import main

def test_harmonics_classical_default(capsys):
    """CLI-02: --harmonics classical produces 5-aspect output."""
    rc = main(["--harmonics", "classical", "aspects", "--date", "2000-01-01T12:00:00Z"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Bodies Aspects" in captured.out
    # Header on stderr, not stdout
    assert "# Aspect set: classical" in captured.err

def test_harmonics_bare_integer_rejected(capsys):
    """CLI-02 / REQUIREMENTS.md line 101: bare integer rejected."""
    with pytest.raises(SystemExit) as excinfo:
        main(["--harmonics", "12", "aspects", "--date", "2000-01-01T12:00:00Z"])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "bare integer" in err
    assert "named preset" in err
```

### Example 4: Subprocess byte-identical regression (CLI-03)

```python
# Source: https://docs.python.org/3/library/subprocess.html
import subprocess, sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "v1_0_legacy_output.txt"

def test_harmonics_all_byte_identical_to_v1_0():
    expected = FIXTURE.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "ketu",
         "--harmonics", "all",
         "aspects", "--date", "2000-01-01T12:00:00Z"],
        capture_output=True, check=True,
    )
    assert result.stdout == expected
```

### Example 5: ISO 8601 with Python-3.10 'Z' shim

```python
# Source: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
# Python 3.11 added 'Z' support; 3.10 needs the +00:00 shim.
from datetime import datetime, timezone

def parse_iso_utc(value: str) -> datetime:
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Interactive `input()` prompts in `display.py:main()` | argparse subcommands with `--date ISO` flag | Phase 11 (this) | Users gain non-interactive scripting; `ketu` becomes pipeable; legacy interactive mode goes away. |
| `aspects=None` defaults to all 14 (v1.0) | `aspects=None` defaults to CLASSICAL (5 majors) — Phase 9 | v1.1 | CLI's `--harmonics all` is the only escape hatch for users who relied on v1.0's 14-aspect output. CLI-03 byte-identity is the regression test. |
| `tests/test_ketu.py:TestMain.test_main_invalid_input` (single test, monkeypatches `input`) | New `tests/cli/` package with parser/spec/cmd/byte-identical/introspection tests | Phase 11 | Larger test surface, but each test is small and orthogonal. Use the `tests/houses/` directory as a layout precedent. |
| `pyproject.toml [project.scripts] ketu = "ketu.display:main"` | `ketu = "ketu.cli:main"` | Phase 11 | Both `ketu` (console script) and `python -m ketu` (via `ketu/__main__.py`) must route to the new entry. Two-spot edit; easy to miss one. |
| Python 3.10 `fromisoformat` rejects `Z` | Python 3.11+ accepts `Z` natively | Python 3.11 (Oct 2022) | While project still supports 3.10 (per pyproject), CLI must shim. Plan should add a 3.10 CI lane or assert via `sys.version_info` that the shim path is exercised. |

**Deprecated/outdated:**
- `display.main()` interactive prompt: removed in Phase 11. Tests under `tests/test_ketu.py:TestMain` are removed/replaced.
- `from ketu.display import main`: removed; replaced by `from ketu.cli import main`.

---

## Open Questions

1. **Top-level `--harmonics` flag inheritance to `aspects` subcommand: parent parser or duplicate?**
   - What we know: argparse supports two patterns: (a) flag declared at top-level parser only — visible BEFORE the subcommand (`ketu --harmonics classical aspects ...`); (b) flag declared via `parents=[shared]` parent parser pattern, allowing it on either side of the subcommand name. The success criteria example uses `ketu --harmonics classical` (BEFORE `aspects`), suggesting top-level only.
   - What's unclear: does the user expect `ketu aspects --harmonics classical --date ...` to work too? Some argparse programs allow both; some force one position.
   - Recommendation: **Top-level only** for v1.1. Reason: matches the documented CLI examples in success criteria; simpler argparse tree; easy to extend later via `parents=[]` if user feedback demands it. Document this in `--help`.

2. **Does `--harmonics all` include the v1.0 "Aspect Timing Example" trailing block?**
   - What we know: v1.0 `main()` always printed `------------- Aspect Timing Example -------------` followed by Sun-Moon timing demo (3 lines). Verified by `git show v1.0.0:ketu/display.py` (lines 79-89). For CLI-03 byte-identity, this block must be reproduced VERBATIM under `--harmonics all`.
   - What's unclear: should this block ALSO appear under non-`all` invocations (`--harmonics classical`)? It's unrelated to aspect set selection — it's a Sun-Moon timing demo regardless of the aspect set. Including it always = surprising; hiding it always except `all` = conditional logic that smells wrong.
   - Recommendation: **always emit** when running `aspects` subcommand, regardless of `--harmonics`. The v1.0 baseline already emits it for all aspect sets (it's not aspect-set-dependent). The byte-identical test pins v1.0's output for the `all` invocation, but the block can be present for `classical` too — no fixture conflict. Plan should call this explicitly.

3. **`--harmonics 9,10,11` interpretation: aspect indices (0-13) or harmonic numbers?**
   - What we know: REQUIREMENTS.md CLI-02 example is "explicit harmonic list (`9,10,11`)". The flag is named `--harmonics`. But `core.aspects` has 14 entries indexed 0-13 (corresponding to harmonics 1, 6, 10, 9, 3, 5, 9, 2, 10, 3, 5, 6, 9, 2 per row). Existing `resolve_aspect_set` accepts `Sequence[int]` as canonical 0-13 indices.
   - What's unclear: does `--harmonics 9,10,11` mean (a) "aspect indices 9, 10, 11 in core.aspects" (= Trine, Biquintile, Quincunx) or (b) "all aspects belonging to harmonics 9, 10, 11" (= Novile+Binovile+Quadrinovile + Decile+Tredecile + nothing for H11)?
   - Recommendation: **Interpret as canonical aspect indices 0-13**, matching `resolve_aspect_set`'s existing contract. The flag NAME is `--harmonics` (legacy/marketing), but the SEMANTICS are "aspect indices into the registry". Document this clearly in `--help` text. If users want true harmonic-number semantics later, add a `--harmonic-numbers` flag. Plan task should add a `--help` example: `--harmonics 9,10,13` → "Trine, Biquintile, Opposition". This sidesteps the H11-doesn't-exist problem cleanly.

4. **Should `--list-aspect-sets` and `--list-house-systems` output be human-readable, machine-parseable, or both?**
   - What we know: success criterion 5 says "available options with descriptions" — implies human-readable.
   - What's unclear: should the format be JSON-on-stdout (machine-parseable), an indented list (human), or both via `--json` flag?
   - Recommendation: **human-readable indented list to stdout** for v1.1; if downstream Kala or scripts need machine output, add `--json` later. Format suggestion: `<name>: <count> aspects (<example angles>)` per line. Plan-level decision; both formats acceptable.

5. **CI matrix: do we have Python 3.10 in CI to catch the `Z` shim regression?**
   - What we know: `pyproject.toml` lists `Programming Language :: Python :: 3.10` through `3.13`. Whether CI actually runs all four is not visible from the repo root without inspecting `.github/workflows/`.
   - What's unclear: if CI is 3.11+ only, the 3.10 `Z` regression won't surface in CI.
   - Recommendation: plan task to verify CI matrix; if 3.10 missing, add it (or at minimum, gate the shim with a `sys.version_info < (3, 11)` test to force the shim to be exercised on every Python). Marking as a planning concern, not a blocker.

6. **Does `ketu houses` need a `--polar-fallback` flag?**
   - What we know: `calculate_houses` accepts `polar_fallback={"raise","porphyry"}`. Default is `"raise"`. CLI-04 spec lists only `--date --lat --lon --system`; no mention of polar fallback.
   - What's unclear: at high latitudes, default `"raise"` will print a confusing `HighLatitudeError`. Without an opt-in, the CLI is unusable above 66.56°.
   - Recommendation: **add `--polar-fallback {raise,porphyry}` with default `raise`** even though CLI-04 doesn't require it. Cost: one line of argparse. Benefit: usable CLI for users in Helsinki, Reykjavik, etc. Plan-level decision; this is a small surface addition, not a spec deviation.

---

## Sources

### Primary (HIGH confidence)
- [Python 3.x argparse module documentation](https://docs.python.org/3/library/argparse.html) — subcommands (`add_subparsers`), `dest`, `required` (added 3.7), `set_defaults(func=...)` dispatch pattern, `type=` callable + `ArgumentTypeError`, `parser.error()`, parent parser pattern.
- [Python 3.x datetime module documentation](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) — `fromisoformat` ISO 8601 support, including 'Z' suffix.
- [What's New in Python 3.11](https://docs.python.org/3.11/whatsnew/3.11.html) — confirms `fromisoformat` extended to "most ISO 8601 formats" in 3.11; 3.10 still requires the `Z`→`+00:00` shim.
- Codebase reads (HIGH — direct file inspection):
  - `ketu/display.py` — current legacy `main()` to be replaced (verified at HEAD AND at `v1.0.0` tag — identical content).
  - `ketu/aspects/presets.py` — Phase 9's `resolve_aspect_set`, `_PRESET_BY_NAME`, `CLASSICAL/TRADITIONAL/EXTENDED` masks.
  - `ketu/houses/__init__.py`, `ketu/houses/api.py`, `ketu/houses/registry.py` — Phase 10's `calculate_houses`, `house_of`, `SYSTEMS`, `HighLatitudeError`.
  - `ketu/ephemeris/time.py` — `utc_to_julian` (timezone-aware datetime → JD).
  - `ketu/__init__.py` — top-level public re-exports of all required APIs.
  - `tests/benchmark_aspects_batch.py` — existing argparse-based CLI in the project, useful as style reference.
  - `pyproject.toml` — `[project.scripts] ketu = "ketu.display:main"`, packages list, Python version classifiers.
  - `.planning/REQUIREMENTS.md` lines 22-29 — CLI-01..CLI-06 verbatim.
  - `.planning/ROADMAP.md` Phase 11 entry — success criteria.
  - `.planning/STATE.md` — confirms Phase 10 closed, Phase 11 unblocked.

### Secondary (MEDIUM confidence — verified against official docs)
- [PythonTest: Testing argparse Applications](https://pythontest.com/testing-argparse-apps/) — capsys, monkeypatch, parse_args(argv=None) pattern.
- [Simon Willison: pytest-argparse TIL](https://til.simonwillison.net/pytest/pytest-argparse) — `pytest.raises(SystemExit)` + capsys pattern.
- [Mike DePalatis: Simplifying argparse with subcommands](https://mike.depalatis.net/blog/simplifying-argparse.html) — function dispatch idiom; cross-checked against official docs.
- [Ruff rule FURB162: fromisoformat-replace-z](https://docs.astral.sh/ruff/rules/fromisoformat-replace-z/) — confirms the `Z`→`+00:00` shim is the standard idiom; Ruff suggests removing it on 3.11+.
- [Issue 35829: parse 'Z' timezone suffix in fromisoformat()](https://bugs.python.org/issue35829) — original cpython issue tracking the 3.11 enhancement.

### Tertiary (LOW confidence — single-source or community-only, marked for verification by the planner)
- [Medium: Custom argparse types](https://medium.com/@zackbunch/how-to-create-custom-argparse-types-in-python-608c17d1f94a) — illustrative only; pattern verified against official docs.
- [DEV Community: argparse subparsers article](https://dev.to/taikedz/ive-parked-my-side-projects-3o62) — illustrative.

---

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — argparse/datetime/numpy are all stdlib or already a dep; pattern verified against official docs and existing project precedent (`tests/benchmark_aspects_batch.py`).
- Architecture: **HIGH** — subpackage layout mirrors existing `ketu/aspects/` and `ketu/houses/`; argparse subcommands + `set_defaults(func=...)` is the documented stdlib pattern; resolved-config-on-stderr is standard Unix.
- Pitfalls: **HIGH** — Python 3.10 `Z` trap verified via Python release notes + Ruff rule + cpython issue tracker; v1.0 main() inspected at the `v1.0.0` tag (not just HEAD); CLI-03 byte-identity reasoning is mechanically verifiable.
- Open questions: **MEDIUM** — Q1 (parent parser inheritance), Q3 (harmonics number semantics), Q6 (polar fallback flag) are user-experience calls that the planner or future user feedback should resolve. Q5 (CI matrix) requires repo inspection.

**Research date:** 2026-05-07
**Valid until:** 30 days (2026-06-07) — argparse and datetime are extremely stable stdlib APIs; the only churn risk is project-internal (Phase 9 or 10 surface changes), which is unlikely now both phases are closed.
