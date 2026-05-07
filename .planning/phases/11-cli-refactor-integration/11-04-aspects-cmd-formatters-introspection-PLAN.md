---
phase: 11-cli-refactor-integration
plan: 04
type: execute
wave: 3
depends_on: ["11-02", "11-03"]
files_modified:
  - ketu/cli/aspects_cmd.py
  - ketu/cli/formatters.py
  - ketu/cli/introspection.py
  - ketu/cli/parser.py
  - tests/cli/test_aspects_cmd.py
  - tests/cli/test_introspection.py
  - tests/cli/test_resolved_header.py
autonomous: true

must_haves:
  truths:
    - "ketu/cli/aspects_cmd.py exports cmd_aspects(args) -> int"
    - "cmd_aspects calls print_positions and print_aspects from ketu.display (kept as library helpers)"
    - "When --harmonics is None, cmd_aspects defaults to CLASSICAL via resolve_aspect_set(None)"
    - "When --harmonics produces a non-default mask, calculate_aspects(jd, aspects=mask) is used so output respects the selection"
    - "cmd_aspects always emits the v1.0 'Aspect Timing Example' Sun-Moon trailing block to stdout — preserves CLI-03 byte-identical contract under --harmonics all (research Open Question 2 resolution: always emit)"
    - "ketu/cli/formatters.py exports emit_resolved_config(mask, preset_name, house_system) — writes header to STDERR (CLI-06)"
    - "Resolved-config header on stderr does NOT pollute stdout (CLI-03 escape hatch preserved)"
    - "ketu/cli/introspection.py exports cmd_list_aspect_sets() and cmd_list_house_systems() — human-readable output to stdout"
    - "cmd_list_aspect_sets shows classical / traditional / extended / all with aspect angles for each"
    - "cmd_list_house_systems iterates ketu.houses.SYSTEMS keys + a one-line description"
    - "parser.py replaces _stub_aspects, _stub_list_aspect_sets, _stub_list_house_systems with real impls"
    - "main() invocations of `aspects` subcommand emit the resolved-config header to stderr before running the calculation"
  artifacts:
    - path: ketu/cli/aspects_cmd.py
      provides: "cmd_aspects(args) dispatcher; calls calculate_aspects with mask; emits v1.0 timing demo block"
      exports: ["cmd_aspects"]
      min_lines: 70
    - path: ketu/cli/formatters.py
      provides: "emit_resolved_config — stderr resolved-config header (CLI-06)"
      exports: ["emit_resolved_config"]
      min_lines: 30
    - path: ketu/cli/introspection.py
      provides: "cmd_list_aspect_sets + cmd_list_house_systems — stdout descriptions"
      exports: ["cmd_list_aspect_sets", "cmd_list_house_systems"]
      min_lines: 40
    - path: ketu/cli/parser.py
      provides: "Real dispatchers wired (no stubs left)"
      contains: "from .aspects_cmd import cmd_aspects"
    - path: tests/cli/test_aspects_cmd.py
      provides: "End-to-end aspects cmd tests + Aspect Timing Example block presence"
      min_lines: 60
    - path: tests/cli/test_introspection.py
      provides: "--list-aspect-sets / --list-house-systems output tests"
      min_lines: 40
    - path: tests/cli/test_resolved_header.py
      provides: "CLI-06 header on stderr; stdout untouched verification"
      min_lines: 40
  key_links:
    - from: ketu/cli/aspects_cmd.py
      to: ketu.aspects.calculate_aspects
      via: "Calls with aspects=mask (resolved from args.harmonics)"
      pattern: "calculate_aspects\\("
    - from: ketu/cli/aspects_cmd.py
      to: ketu/display.py:print_positions
      via: "Reuses existing library formatter (display.py:main is deleted in Plan 11-05; print_positions/print_aspects survive)"
      pattern: "from ketu\\.display import .*print_positions"
    - from: ketu/cli/formatters.py
      to: sys.stderr
      via: "All resolved-config output writes to file=sys.stderr (preserves CLI-03 stdout)"
      pattern: "file=sys\\.stderr"
    - from: ketu/cli/introspection.py
      to: ketu/houses/registry.py:SYSTEMS
      via: "Iterates SYSTEMS dict for --list-house-systems"
      pattern: "from ketu\\.houses import.*SYSTEMS|SYSTEMS"
    - from: ketu/cli/parser.py
      to: ketu/cli/aspects_cmd.py:cmd_aspects
      via: "p_aspects.set_defaults(func=cmd_aspects) replaces _stub_aspects"
      pattern: "set_defaults\\(func=cmd_aspects\\)"
---

<objective>
Wire the `ketu aspects` subcommand end-to-end (CLI-02), the resolved-config header (CLI-06, emitted to stderr), and the introspection commands `--list-aspect-sets` / `--list-house-systems` (CLI-05). After this plan, the new CLI is functionally complete — Plan 11-05 only repoints the entry points and Plan 11-06 only adds the byte-identical regression test.

Critical decisions inherited from research §Open Questions:
- **Q2 (Aspect Timing Example block):** ALWAYS emitted under the `aspects` subcommand regardless of `--harmonics`. v1.0 already emitted it for all aspect sets; preserves CLI-03 byte-identical contract under `--harmonics all` without conditional logic.
- **Q4 (introspection format):** human-readable indented list to stdout. JSON deferred to v1.2.
- **Q6 (--polar-fallback):** already added in Plan 11-01 parser scaffolding.
- **Resolved-config header → stderr** (research §Pattern 4): keeps stdout pristine for CLI-03.

Output:
  - ketu/cli/aspects_cmd.py — `cmd_aspects(args)` dispatcher (positions + aspects + Aspect Timing Example)
  - ketu/cli/formatters.py — `emit_resolved_config(...)` to stderr
  - ketu/cli/introspection.py — `cmd_list_aspect_sets` + `cmd_list_house_systems`
  - ketu/cli/parser.py — wires all real dispatchers (no stubs left)
  - tests/cli/test_aspects_cmd.py + test_introspection.py + test_resolved_header.py
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

# Phase 9 deliverables — what cmd_aspects calls
@ketu/aspects/presets.py
@ketu/aspects/calculator.py

# Existing library helpers that survive the refactor
@ketu/display.py

# core.aspects — for resolved-config angle formatting
@ketu/core.py

# Phase 10 deliverable — for --list-house-systems
@ketu/houses/__init__.py

# Parser this plan modifies
@ketu/cli/parser.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement aspects_cmd, formatters, and introspection modules</name>
  <files>ketu/cli/aspects_cmd.py, ketu/cli/formatters.py, ketu/cli/introspection.py</files>
  <action>
**Create ketu/cli/formatters.py** — resolved-config header to stderr (CLI-06).

```python
"""Resolved-config header — CLI-06.

Emitted to STDERR (NOT stdout) so the byte-identical CLI-03 escape hatch
(`--harmonics all` matching v1.0 stdout) is preserved. Stdout = data,
stderr = diagnostics — standard Unix split.
"""
from __future__ import annotations

import sys

import numpy as np
import numpy.typing as npt

from ketu.core import aspects as _CORE_ASPECTS


def emit_resolved_config(
    mask: npt.NDArray[np.bool_] | None,
    preset_name: str | None,
    house_system: str | None = None,
) -> None:
    """Echo the resolved CLI configuration to STDERR.

    Parameters
    ----------
    mask : np.ndarray of np.bool_ or None
        Length-14 boolean mask selecting rows of ``ketu.core.aspects``.
        ``None`` means "no aspect filter applied" (e.g. ``ketu houses``
        with no aspects subcommand).
    preset_name : str or None
        Human-readable label for the aspect set (e.g. ``"classical"``,
        ``"all"``, or ``"custom"`` for explicit-list spec). ``None`` if
        no aspect command was invoked.
    house_system : str or None
        Selected house system (e.g. ``"placidus"``), or None if the
        command isn't house-related.

    Notes
    -----
    Format is intentionally simple, parseable line-by-line, and
    discoverable: every line starts with ``# `` so downstream tools
    can grep/strip with ``sed '/^# /d'``.
    """
    print("# Ketu v1.1.0", file=sys.stderr)
    if mask is not None and preset_name is not None:
        names = [n.decode() if isinstance(n, bytes) else str(n)
                 for n in _CORE_ASPECTS["name"][mask]]
        angles = [int(a) for a in _CORE_ASPECTS["angle"][mask]]
        details = ", ".join(f"{name} {ang}°" for name, ang in zip(names, angles))
        print(
            f"# Aspect set: {preset_name} ({len(names)} aspects: {details})",
            file=sys.stderr,
        )
    if house_system is not None:
        print(f"# House system: {house_system}", file=sys.stderr)
```

**Create ketu/cli/introspection.py** — `--list-aspect-sets` and `--list-house-systems` (CLI-05).

```python
"""Introspection commands — CLI-05.

Human-readable indented list to STDOUT. JSON output deferred to v1.2
(research §Open Question 4).
"""
from __future__ import annotations

import numpy as np

from ketu.aspects.presets import resolve_aspect_set
from ketu.core import aspects as _CORE_ASPECTS
from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS


_PRESET_DESCRIPTIONS = {
    "classical": "5 majors (Conjunction, Sextile, Square, Trine, Opposition) — v1.1 default",
    "traditional": "7 aspects (CLASSICAL + Semi-sextile + Quincunx)",
    "extended": "14 aspects (all rows of core.aspects, including harmonics 5/9/10)",
    "all": "alias for 'extended' — v1.0 14-aspect output (CLI-03 byte-identical escape hatch)",
}

_SYSTEM_DESCRIPTIONS = {
    "placidus": "Time-based; iterative trisection of the diurnal/nocturnal arcs (v1.1)",
    "koch": "Birthplace-based; closed-form trisection of the oblique-ascension arc (v1.1)",
    "porphyry": "Space-based; equal trisection of the ARMC quadrants — works at all latitudes (v1.1, also the polar fallback)",
}


def cmd_list_aspect_sets() -> None:
    """Print available aspect-set presets with descriptions to stdout."""
    print("Available aspect sets (use with --harmonics SPEC):")
    print()
    for name in ("classical", "traditional", "extended", "all"):
        # Resolve the mask so we can show the actual angles.
        mask = resolve_aspect_set("extended" if name == "all" else name)
        names = [n.decode() if isinstance(n, bytes) else str(n)
                 for n in _CORE_ASPECTS["name"][mask]]
        angles = [int(a) for a in _CORE_ASPECTS["angle"][mask]]
        angle_str = ", ".join(f"{n} {a}°" for n, a in zip(names, angles))
        desc = _PRESET_DESCRIPTIONS.get(name, "")
        print(f"  {name:12} : {desc}")
        print(f"  {'':12}   ({len(names)} aspects: {angle_str})")
        print()
    print("You may also pass an explicit comma-separated list of aspect indices,")
    print("e.g. --harmonics 0,4,7,9,13 (= classical).")


def cmd_list_house_systems() -> None:
    """Print available house systems with descriptions to stdout."""
    print("Available house systems (use with --system NAME on `ketu houses`):")
    print()
    for name in sorted(_HOUSE_SYSTEMS.keys()):
        desc = _SYSTEM_DESCRIPTIONS.get(name, "(no description available)")
        print(f"  {name:10} : {desc}")
    print()
    print("At polar latitudes, use --polar-fallback porphyry to substitute Porphyry")
    print("cusps for offending elements (default: --polar-fallback raise).")
```

**Create ketu/cli/aspects_cmd.py** — the `ketu aspects` dispatcher.

This is the most subtle module. Three things must happen in this order:
1. Resolve `args.harmonics` (None → CLASSICAL via `resolve_aspect_set(None)`).
2. Emit the resolved-config header to stderr.
3. Print positions + aspects to stdout.
4. Always emit the v1.0 'Aspect Timing Example' trailing Sun-Moon block to stdout (research §Open Question 2 resolution: always emit, regardless of --harmonics; matches v1.0 behavior so CLI-03 byte-identical Just Works under `--harmonics all`).

Critical: `ketu.aspects.calculate_aspects(jdate, aspects=mask)` accepts an `aspects=` kwarg per Plan 09-04a. Pass the resolved mask. For `display.print_positions` and `display.print_aspects` (the existing library helpers) — note that `print_aspects` calls `calculate_aspects(jdate)` with NO aspects= filter, which means it still uses the default. That's the issue. We have two options:

Option A: copy the loop from `display.print_aspects` into `aspects_cmd.py` and pass `aspects=mask` to `calculate_aspects`.

Option B: keep `display.print_positions` (no filter dependency) and rewrite the aspects-printing loop locally in aspects_cmd.

Choose **Option B** — clearer separation, no need to widen `print_aspects`'s signature, and it's only a 6-line loop. Mirror v1.0's exact format string so CLI-03 byte-identical falls out.

```python
"""Dispatcher for `ketu aspects ...` subcommand.

Calls :func:`ketu.aspects.calculate_aspects` with the resolved
``--harmonics`` mask, then prints positions + aspects to STDOUT in the
v1.0-compatible format (which is the contract for CLI-03 byte-identical
under ``--harmonics all``).

Open Question 2 resolution (research §Open Questions): the trailing
"Aspect Timing Example" Sun-Moon block is ALWAYS emitted regardless of
``--harmonics`` value. v1.0 emitted it for all aspect sets (it's a
fixed Sun-Moon timing demo, not aspect-set-dependent). Always emitting
preserves the byte-identical contract for ``--harmonics all`` AND
gives non-`all` users the same demo block (no surprising behaviour
change from v1.0).
"""
from __future__ import annotations

import argparse

import numpy as np

from ketu.aspects import calculate_aspects, find_aspects_between_dates
from ketu.aspects.presets import resolve_aspect_set
from ketu.calculations import (
    body_id,
    body_name,
    dd_to_dms,
    julian_to_utc,
)
from ketu.core import aspects as _CORE_ASPECTS
from ketu.display import print_positions  # surviving library helper

from ._dates import parse_iso_utc
from .formatters import emit_resolved_config


def _preset_label_for_mask(mask: np.ndarray, raw_arg: object) -> str:
    """Best-effort human label for the resolved-config header.

    Returns the string the user passed if it was a recognized preset;
    otherwise 'custom' for explicit-list specs; 'classical' if --harmonics
    was not given (mask was resolved from None).
    """
    # raw_arg is what the user passed on the CLI (a numpy mask after
    # type=parse_harmonics_spec, or None if --harmonics omitted). We don't
    # know the original string here; preserve the most useful label.
    # Simplest robust mapping: count Trues.
    n = int(mask.sum())
    if n == 5:
        return "classical"
    if n == 7:
        return "traditional"
    if n == 14:
        # extended and 'all' produce the same mask; report 'extended' as the
        # canonical name (the alias is documented in --help).
        return "extended"
    return "custom"


def cmd_aspects(args: argparse.Namespace) -> int:
    """Compute and print body positions + aspects for a date.

    Parameters
    ----------
    args : argparse.Namespace
        Required: ``date``. Optional (top-level): ``harmonics`` — a
        length-14 ``np.bool_`` mask or None (None resolves to CLASSICAL
        via :func:`ketu.aspects.presets.resolve_aspect_set`).

    Returns
    -------
    int
        Exit code (0 on success).
    """
    # Resolve --harmonics: None → CLASSICAL (Phase 9 default).
    if args.harmonics is None:
        mask = resolve_aspect_set(None)
        preset_label = "classical"
    else:
        mask = args.harmonics  # already a length-14 np.bool_ mask
        preset_label = _preset_label_for_mask(mask, args.harmonics)

    # Resolved-config header to STDERR (CLI-06; preserves CLI-03 stdout).
    emit_resolved_config(mask, preset_label, house_system=None)

    jd = parse_iso_utc(args.date)

    # Positions block — reuse existing library helper unchanged.
    print_positions(jd)

    # Aspects block — reproduce v1.0 format here so we can pass aspects=mask.
    print()
    print("------------- Bodies Aspects -------------")
    for asp in calculate_aspects(jd, aspects=mask):
        body1, body2, i_asp, orb = asp
        degs, mins, secs = dd_to_dms(orb)
        name_bytes = _CORE_ASPECTS["name"][int(i_asp)]
        aspect_name = name_bytes.decode() if isinstance(name_bytes, bytes) else str(name_bytes)
        print(
            f"{body_name(int(body1)):7} - {body_name(int(body2)):12}: "
            f"{aspect_name:12} "
            f"{degs:>2}°{mins:>2}'{secs:>2}\""
        )

    # Aspect Timing Example — ALWAYS emitted (research §Open Question 2).
    # Reproduces v1.0 main()'s trailing Sun-Moon timing demo verbatim.
    print()
    print("------------- Aspect Timing Example -------------")
    sun_id = body_id("Sun")
    moon_id = body_id("Moon")
    aspects_found = find_aspects_between_dates(jd - 15, jd + 15, sun_id, moon_id)
    for entry in aspects_found[:3]:
        exact_jd, b1, b2, asp_name, _asp_val = entry
        exact_dt = julian_to_utc(float(exact_jd))
        print(f"{body_name(int(b1))} {asp_name} {body_name(int(b2))} at {exact_dt}")

    return 0
```

Notes:
- Aspect-printing format mirrors v1.0 `display.print_aspects` BYTE-FOR-BYTE (same field widths, same separators, same use of `degrees°minutes'seconds"`). Plan 11-06 will validate byte-identity against the v1.0 fixture; any drift here surfaces there.
- The trailing block also mirrors v1.0 verbatim. Format strings copied from `git show v1.0.0:ketu/display.py`.
- `_preset_label_for_mask` is a heuristic (we lost the original string after `type=parse_harmonics_spec` ran). For the resolved-config header on stderr this is fine; the byte-identical test only checks stdout.
- mypy --strict: ensure all `int(...)` and `float(...)` casts on numpy scalars are explicit so types are literal `int` / `float`. (Existing project pattern.)
  </action>
  <verify>
1. `python -c "from ketu.cli.aspects_cmd import cmd_aspects; from ketu.cli.formatters import emit_resolved_config; from ketu.cli.introspection import cmd_list_aspect_sets, cmd_list_house_systems"` — all imports succeed.
2. `mypy --strict ketu/cli/` clean.
3. Manual smoke: `python -c "from ketu.cli import main; main(['--list-aspect-sets'])"` prints 4 presets to stdout.
  </verify>
  <done>
- ketu/cli/formatters.py exposes emit_resolved_config writing to sys.stderr.
- ketu/cli/introspection.py exposes cmd_list_aspect_sets + cmd_list_house_systems with human-readable stdout output.
- ketu/cli/aspects_cmd.py exposes cmd_aspects: resolves --harmonics (None → CLASSICAL), emits resolved-config header to stderr, calls print_positions, prints aspects with the v1.0-format string, ALWAYS emits the Aspect Timing Example trailing block.
- mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Wire real dispatchers in parser.py and add tests for aspects/introspection/header</name>
  <files>ketu/cli/parser.py, tests/cli/test_aspects_cmd.py, tests/cli/test_introspection.py, tests/cli/test_resolved_header.py</files>
  <action>
**Edit ketu/cli/parser.py** — replace the three remaining stubs with real implementations.

1. Add imports at top of file:

```python
from .aspects_cmd import cmd_aspects
from .introspection import cmd_list_aspect_sets, cmd_list_house_systems
```

2. Update the introspection short-circuits in `main()`:

```python
if args.list_aspect_sets:
    cmd_list_aspect_sets()
    return 0
if args.list_house_systems:
    cmd_list_house_systems()
    return 0
```

3. Update the aspects subparser's `set_defaults`:

```python
p_aspects.set_defaults(func=cmd_aspects)  # was: func=_stub_aspects
```

4. DELETE all four stub functions (`_stub_aspects`, `_stub_houses` if still present from Plan 11-03 leftovers, `_stub_list_aspect_sets`, `_stub_list_house_systems`) — they are no longer referenced. Keep `_stub_aspects` ONLY if mypy --strict requires it (it shouldn't; deletion is clean).

After this edit, `parser.py` contains zero stubs.

**Update tests/cli/test_parser.py** — Plan 11-01's stub-marker assertions are now stale. Update:

```python
# OLD (Plan 11-01):
def test_main_aspects_dispatches_to_func(self, invoke_main, capsys):
    rc = invoke_main(["aspects", "--date", "2026-05-06T12:00:00Z"])
    assert rc == 0
    err = capsys.readouterr().err
    assert "Plan 11-04" in err or "not yet implemented" in err

# NEW (Plan 11-04 — real dispatcher):
def test_main_aspects_dispatches_to_func(self, invoke_main, capsys):
    """`ketu aspects --date X` runs cmd_aspects → exit 0; resolved-config header on stderr."""
    rc = invoke_main(["aspects", "--date", "2026-05-06T12:00:00Z"])
    assert rc == 0
    out = capsys.readouterr()
    assert "Bodies Positions" in out.out
    assert "Aspect set:" in out.err   # CLI-06 header on stderr
```

Similarly update `test_main_list_aspect_sets_short_circuits` and `test_main_list_house_systems_short_circuits` to assert real content rather than the stub markers:

```python
def test_main_list_aspect_sets_short_circuits(self, invoke_main, capsys):
    rc = invoke_main(["--list-aspect-sets"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "classical" in out
    assert "traditional" in out
    assert "extended" in out
    assert "all" in out

def test_main_list_house_systems_short_circuits(self, invoke_main, capsys):
    rc = invoke_main(["--list-house-systems"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "placidus" in out
    assert "koch" in out
    assert "porphyry" in out
```

**Create tests/cli/test_aspects_cmd.py** — end-to-end aspects subcommand tests.

```python
"""End-to-end tests for `ketu aspects ...` subcommand."""
from __future__ import annotations

import pytest


class TestAspectsCmdDefaultClassical:
    """Without --harmonics, CLASSICAL (5 majors) is the default (Phase 9)."""

    def test_default_classical_runs(self, invoke_main, capsys):
        rc = invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Bodies Positions" in out
        assert "Bodies Aspects" in out

    def test_default_classical_header_on_stderr(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        assert "Aspect set: classical" in err


class TestAspectsCmdHarmonicsAll:
    """--harmonics all matches v1.0 14-aspect output structure."""

    def test_all_runs_and_header_says_extended(self, invoke_main, capsys):
        """'all' aliases 'extended' — header label resolves to 'extended'."""
        rc = invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        assert "Bodies Aspects" in captured.out
        # 'all' → mask of 14 Trues → label = 'extended' (research recommended canonical name).
        assert "Aspect set: extended" in captured.err


class TestAspectsCmdTimingExampleAlwaysEmitted:
    """Research Open Question 2 resolution: trailing 'Aspect Timing Example' ALWAYS emitted."""

    def test_timing_example_present_under_classical(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out

    def test_timing_example_present_under_all(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out

    def test_timing_example_present_under_traditional(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "traditional",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        assert "Aspect Timing Example" in out


class TestAspectsCmdHarmonicsList:
    """--harmonics 0,4,7,9,13 == classical."""

    def test_explicit_classical_indices_match_named_classical(self, invoke_main, capsys):
        rc1 = invoke_main([
            "--harmonics", "0,4,7,9,13",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out1 = capsys.readouterr().out
        rc2 = invoke_main([
            "--harmonics", "classical",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out2 = capsys.readouterr().out
        assert rc1 == 0 and rc2 == 0
        # Aspect content (everything between "Bodies Aspects" and "Aspect Timing Example")
        # should match — same mask → same aspects.
        def aspects_block(s: str) -> str:
            i = s.find("Bodies Aspects")
            j = s.find("Aspect Timing Example", i)
            return s[i:j] if (i >= 0 and j >= 0) else s
        assert aspects_block(out1) == aspects_block(out2)


class TestAspectsCmdRejectsBareInteger:
    """CLI-02 / Pitfall 9: --harmonics 12 → SystemExit(2) on stderr."""

    def test_bare_int_rejected_via_cli(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "--harmonics", "12",
                "aspects", "--date", "2000-01-01T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "bare integer" in err
        assert "named preset" in err
```

**Create tests/cli/test_introspection.py** — `--list-aspect-sets` / `--list-house-systems`.

```python
"""Tests for introspection commands (CLI-05)."""
from __future__ import annotations


class TestListAspectSets:
    def test_lists_all_four_presets(self, invoke_main, capsys):
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0
        out = capsys.readouterr().out
        for name in ("classical", "traditional", "extended", "all"):
            assert name in out

    def test_shows_aspect_angles_for_classical(self, invoke_main, capsys):
        invoke_main(["--list-aspect-sets"])
        out = capsys.readouterr().out
        # Classical includes Conjunction 0°, Sextile 60°, Square 90°, Trine 120°, Opposition 180°.
        assert "0°" in out and "60°" in out and "90°" in out and "120°" in out and "180°" in out


class TestListHouseSystems:
    def test_lists_registered_systems(self, invoke_main, capsys):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
        out = capsys.readouterr().out
        for name in ("placidus", "koch", "porphyry"):
            assert name in out

    def test_mentions_polar_fallback_hint(self, invoke_main, capsys):
        invoke_main(["--list-house-systems"])
        out = capsys.readouterr().out
        assert "polar-fallback" in out or "porphyry" in out  # the polar fallback hint


class TestIntrospectionShortCircuits:
    """Introspection flags work WITHOUT a subcommand (Pitfall 1)."""

    def test_list_aspect_sets_no_subcommand(self, invoke_main):
        rc = invoke_main(["--list-aspect-sets"])
        assert rc == 0  # would be SystemExit(2) if subparsers required=True

    def test_list_house_systems_no_subcommand(self, invoke_main):
        rc = invoke_main(["--list-house-systems"])
        assert rc == 0
```

**Create tests/cli/test_resolved_header.py** — CLI-06 header on stderr; CLI-03 stdout untouched assertion.

```python
"""Tests for the resolved-config header (CLI-06) — STDERR-only contract."""
from __future__ import annotations


class TestResolvedConfigHeaderOnStderr:
    """Header emitted to stderr; stdout is untouched (research §Pattern 4)."""

    def test_aspects_header_on_stderr(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        captured = capsys.readouterr()
        # Header on stderr.
        assert "# Aspect set:" in captured.err
        assert "# Ketu v1.1.0" in captured.err
        # Header NOT on stdout (CLI-03 byte-identical contract).
        assert "# Aspect set:" not in captured.out
        assert "# Ketu v1.1.0" not in captured.out

    def test_classical_label_in_header(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        assert "Aspect set: classical" in err

    def test_extended_label_when_all(self, invoke_main, capsys):
        """`--harmonics all` → header label is 'extended' (canonical name)."""
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        err = capsys.readouterr().err
        assert "Aspect set: extended" in err

    def test_header_lists_aspect_count_and_angles(self, invoke_main, capsys):
        invoke_main(["aspects", "--date", "2000-01-01T12:00:00Z"])
        err = capsys.readouterr().err
        # Classical → 5 aspects.
        assert "5 aspects" in err
        # Some recognizable angle present.
        assert "0°" in err and "180°" in err


class TestStdoutPristineUnderHarmonicsAll:
    """CLI-03 spirit-check: under --harmonics all, no '# ...' meta-line is on stdout."""

    def test_no_hash_lines_in_stdout(self, invoke_main, capsys):
        invoke_main([
            "--harmonics", "all",
            "aspects", "--date", "2000-01-01T12:00:00Z",
        ])
        out = capsys.readouterr().out
        for line in out.splitlines():
            # The only `#`-prefixed line allowed on stdout would be a v1.0
            # output line, but v1.0 doesn't emit any. Anything starting
            # with '# ' is a leak from the resolved-config header.
            assert not line.startswith("# "), (
                f"Resolved-config header leaked to stdout: {line!r}"
            )
```

Notes:
- These tests do not yet check byte-identity against the v1.0 fixture — that's Plan 11-06's job. They DO check the structural invariant (no `# ...` lines on stdout) which is a necessary condition for CLI-03 to pass.
- Total new tests: ~22 (aspects_cmd: 8, introspection: 7, resolved_header: 5+).
  </action>
  <verify>
1. `pytest tests/cli/ -v` — all CLI tests green: parser (updated), harmonics_spec, dates, houses_cmd (Plan 11-03), aspects_cmd (new), introspection (new), resolved_header (new).
2. `pytest tests/ -v` — full project suite green; no regression.
3. `mypy --strict ketu/cli/` clean.
4. Manual: `python -m ketu --list-aspect-sets` lists 4 presets; `python -m ketu --list-house-systems` lists placidus/koch/porphyry.
5. Manual: `python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z 2>/dev/null` — stdout has Bodies Positions / Bodies Aspects / Aspect Timing Example; no `# `-prefixed lines.
6. Manual: same command piped `2>&1 >/dev/null` shows the resolved-config header.
  </verify>
  <done>
- parser.py: all stub functions removed; real cmd_aspects + cmd_list_aspect_sets + cmd_list_house_systems wired.
- aspects_cmd: resolves --harmonics (None → classical), header → stderr, positions → stdout, aspects → stdout (v1.0 format), Aspect Timing Example trailing block ALWAYS emitted.
- introspection: lists 4 aspect presets with angles + 3 house systems with descriptions; works without a subcommand.
- formatters: emit_resolved_config to stderr; '# Ketu v1.1.0' + '# Aspect set: NAME (N aspects: ...)' + optional '# House system: NAME'.
- tests cover: default-classical, --harmonics all, --harmonics list, bare-int reject, list-aspect-sets, list-house-systems, no-subcommand short-circuit, header-on-stderr, stdout-pristine.
- Plan 11-01's stub-marker assertions in test_parser.py replaced with real-content assertions.
- mypy --strict clean.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/cli/ -v` — all CLI tests green.
- `pytest tests/ -v` — full project suite green.
- `mypy --strict ketu/cli/` clean.
- Manual smoke: every `python -m ketu ...` invocation produces a `# Aspect set:` line on stderr (or `# House system:` line for `houses` subcommand once Plan 11-03's cmd_houses is updated, see open follow-up note below).
- The CLI-03 stdout-pristine invariant is structurally proven (no `# ` lines on stdout under `--harmonics all`).

Open follow-up note (NOT a blocker for this plan): Plan 11-03's cmd_houses currently does NOT call emit_resolved_config. This plan introduces the formatter; cmd_houses can OPTIONALLY be updated to call it for CLI-06 coverage on the `houses` subcommand too. Decision: leave cmd_houses unchanged in this plan — it's a one-line addition the executor can decide. The success criterion 5 ("every CLI invocation echoes resolved-config header") is BEST satisfied by also calling emit_resolved_config from cmd_houses; doing so is in scope here. Add it: at the top of cmd_houses, after parse_iso_utc, call `emit_resolved_config(mask=None, preset_name=None, house_system=args.system)`.
</verification>

<success_criteria>
- CLI-02 fully wired end-to-end: `--harmonics SPEC` flows from CLI → mask → calculate_aspects → output respecting selection. Bare integer rejected with helpful error.
- CLI-05 fully wired: `--list-aspect-sets` and `--list-house-systems` emit human-readable, accurate, non-empty output to stdout, work without a subcommand.
- CLI-06 fully wired (aspects subcommand and houses subcommand): resolved-config header emitted to STDERR; STDOUT is pristine under `--harmonics all` (no `# ` leak).
- v1.0 'Aspect Timing Example' trailing block ALWAYS emitted under `aspects` subcommand (CLI-03 prerequisite; research §Open Question 2 resolution).
- All Plan 11-01 stub-marker assertions in test_parser.py updated to real-content assertions.
- 0 stubs remain in parser.py.
- Full project test suite green; mypy --strict clean.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-04-aspects-cmd-formatters-introspection-SUMMARY.md` documenting:
- Files: cli/aspects_cmd.py NEW, cli/formatters.py NEW, cli/introspection.py NEW, cli/parser.py edit (3 stubs removed); tests/cli/test_aspects_cmd.py NEW, tests/cli/test_introspection.py NEW, tests/cli/test_resolved_header.py NEW; tests/cli/test_parser.py updated.
- Key decisions: Aspect Timing Example always emitted (research Open Q2); preset label heuristic by sum-count; cmd_houses also calls emit_resolved_config for CLI-06 coverage.
- Test count delta (added ~22+ tests; updated 3 in test_parser.py).
- Any deviations from plan.
</output>
