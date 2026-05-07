---
phase: 11-cli-refactor-integration
plan: 03
type: execute
wave: 2
depends_on: ["11-01"]
files_modified:
  - ketu/cli/_dates.py
  - ketu/cli/houses_cmd.py
  - ketu/cli/parser.py
  - tests/cli/test_dates.py
  - tests/cli/test_houses_cmd.py
autonomous: true

must_haves:
  truths:
    - "ketu/cli/_dates.py exports parse_iso_utc(value) -> float (Julian Date)"
    - "parse_iso_utc handles trailing 'Z' on Python 3.10 by replacing with '+00:00' BEFORE calling fromisoformat"
    - "parse_iso_utc treats naive datetimes as UTC (matches utc_to_julian convention)"
    - "ketu/cli/houses_cmd.py exports cmd_houses(args) -> int dispatcher"
    - "cmd_houses calls ketu.calculate_houses(jd, lat, lon, system, polar_fallback) — registry dispatch, no inline if/elif"
    - "cmd_houses prints 12 cusps to stdout (one per line, formatted as 'House N: SIGN DD°MM\\'SS\\\"' or numeric degrees)"
    - "cmd_houses prints ASC and MC angles to stdout"
    - "parser.py imports cmd_houses and replaces _stub_houses in p_houses.set_defaults(func=...)"
    - "ketu houses --date X --lat Y --lon Z --system placidus returns same cusps as ketu.calculate_houses Python API"
    - "Python 3.10 'Z' shim test exists and exercises the shim regardless of running interpreter version"
  artifacts:
    - path: ketu/cli/_dates.py
      provides: "parse_iso_utc(value: str) -> float (JD); shared by aspects_cmd and houses_cmd"
      exports: ["parse_iso_utc"]
      min_lines: 30
    - path: ketu/cli/houses_cmd.py
      provides: "cmd_houses(args) dispatcher + house cusp formatter"
      exports: ["cmd_houses"]
      min_lines: 60
    - path: ketu/cli/parser.py
      provides: "p_houses now dispatches to cmd_houses (real impl, not stub)"
      contains: "from .houses_cmd import cmd_houses"
    - path: tests/cli/test_dates.py
      provides: "parse_iso_utc unit tests including 'Z' shim regression"
      min_lines: 40
    - path: tests/cli/test_houses_cmd.py
      provides: "cmd_houses end-to-end tests via main(['houses', ...])"
      min_lines: 60
  key_links:
    - from: ketu/cli/_dates.py
      to: ketu/ephemeris/time.py:utc_to_julian
      via: "Final JD conversion delegates to existing function"
      pattern: "from ketu\\.ephemeris\\.time import utc_to_julian|from ketu import.*utc_to_julian|utc_to_julian"
    - from: ketu/cli/houses_cmd.py
      to: ketu.calculate_houses
      via: "Public API call (registry dispatch through ketu.houses)"
      pattern: "calculate_houses\\("
    - from: ketu/cli/parser.py
      to: ketu/cli/houses_cmd.py:cmd_houses
      via: "p_houses.set_defaults(func=cmd_houses) replaces stub"
      pattern: "set_defaults\\(func=cmd_houses\\)"
---

<objective>
Implement the `ketu houses` subcommand end-to-end: parse `--date ISO` (with the Python-3.10 'Z' shim), call `ketu.calculate_houses(jd, lat, lon, system, polar_fallback)` (Phase 10 deliverable), and format the 12 cusps + ASC + MC for stdout. Wire `cmd_houses` into `parser.py` (replaces `_stub_houses`).

Purpose: CLI-04 requirement. Verifies that the new houses public API is reachable from the CLI and produces identical results to the Python API.

Output:
  - ketu/cli/_dates.py — `parse_iso_utc(value: str) -> float` shared by aspects_cmd (Plan 11-04) and houses_cmd
  - ketu/cli/houses_cmd.py — `cmd_houses(args)` dispatcher
  - ketu/cli/parser.py — wired (replaces `_stub_houses`)
  - tests/cli/test_dates.py + test_houses_cmd.py — coverage
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

# Phase 10 deliverables — what cmd_houses calls
@ketu/houses/__init__.py
@ketu/houses/api.py
@ketu/ephemeris/time.py

# Parser this plan modifies
@ketu/cli/parser.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ketu/cli/_dates.py with parse_iso_utc + Python-3.10 'Z' shim, with tests</name>
  <files>ketu/cli/_dates.py, tests/cli/test_dates.py</files>
  <action>
**Create ketu/cli/_dates.py** — shared date parser used by both `houses_cmd` and (later) `aspects_cmd`. Lives under a leading underscore because it's CLI-internal plumbing, not part of the public CLI API.

Critical: Python 3.10's `datetime.fromisoformat("2026-05-06T12:00:00Z")` raises `ValueError`. Python 3.11+ accepts `Z` natively. Project's `requires-python = ">=3.10"` means we MUST shim. Also: naive datetimes assumed UTC (matches `utc_to_julian` convention).

```python
"""ISO 8601 date parsing for the CLI.

Two responsibilities, both delegating to standard library + existing Ketu
helpers:

1. Parse the ``--date ISO`` argument into a timezone-aware UTC datetime.
2. Convert that datetime into a Julian Date via
   :func:`ketu.ephemeris.time.utc_to_julian`.

The trailing ``Z`` suffix is handled defensively for Python 3.10 (where
``datetime.fromisoformat`` rejects ``Z``; Python 3.11+ accepts it
natively; see :ref:`What's New in Python 3.11`).
"""
from __future__ import annotations

from datetime import datetime, timezone

from ketu.ephemeris.time import utc_to_julian


def parse_iso_utc(value: str) -> float:
    """Parse an ISO-8601 datetime string and return its Julian Date.

    Parameters
    ----------
    value : str
        ISO-8601 datetime, e.g. ``"2026-05-06T12:00:00Z"`` or
        ``"2026-05-06T12:00:00+00:00"``. Naive datetimes (no offset)
        are assumed to be UTC.

    Returns
    -------
    float
        Julian Date (UTC), via :func:`ketu.ephemeris.time.utc_to_julian`.

    Raises
    ------
    SystemExit
        If the input is not a valid ISO-8601 datetime. Raises with a
        helpful message; argparse-friendly.

    Notes
    -----
    Python 3.10 trap: ``datetime.fromisoformat("2026-05-06T12:00:00Z")``
    raises ``ValueError`` on 3.10 (only accepts ``+00:00``). 3.11+
    accepts ``Z`` natively. We unconditionally replace trailing ``Z``
    with ``+00:00`` before parsing — works on both.
    """
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(
            f"error: --date {value!r} is empty or not a string"
        )
    s = value.strip()
    # Python 3.10 'Z' shim: replace trailing Z with +00:00 BEFORE parsing.
    # Idempotent on Python 3.11+ (which accepts Z natively).
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise SystemExit(
            f"error: --date {value!r} is not a valid ISO-8601 datetime "
            f"(expected e.g. '2026-05-06T12:00:00Z' or "
            f"'2026-05-06T12:00:00+00:00'); {e}"
        )
    if dt.tzinfo is None:
        # Naive datetime → assume UTC (matches utc_to_julian's convention).
        dt = dt.replace(tzinfo=timezone.utc)
    # Convert to UTC explicitly (in case of non-UTC offset).
    dt_utc = dt.astimezone(timezone.utc)
    return utc_to_julian(dt_utc)
```

**Create tests/cli/test_dates.py** — exercises the shim regardless of which Python version is running.

```python
"""Unit tests for ketu.cli._dates.parse_iso_utc."""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import pytest

from ketu.cli._dates import parse_iso_utc
from ketu.ephemeris.time import utc_to_julian


class TestZShim:
    """Python-3.10 'Z' shim regression — must work on 3.10 AND 3.11+."""

    def test_z_suffix_accepted_on_all_python_versions(self):
        """The 'Z' shim is unconditional → must work on every Python the project supports."""
        jd = parse_iso_utc("2026-05-06T12:00:00Z")
        # Compare against an explicit UTC datetime → utc_to_julian path.
        expected_dt = datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone.utc)
        expected_jd = utc_to_julian(expected_dt)
        assert jd == pytest.approx(expected_jd, abs=1e-9)

    def test_plus_00_00_suffix_equivalent_to_z(self):
        jd_z = parse_iso_utc("2026-05-06T12:00:00Z")
        jd_offset = parse_iso_utc("2026-05-06T12:00:00+00:00")
        assert jd_z == pytest.approx(jd_offset, abs=1e-12)

    def test_z_shim_path_explicit_when_py310(self):
        """If running on Python 3.10, exercise the shim directly to ensure it isn't dead.

        On 3.11+, datetime.fromisoformat accepts Z natively; the shim is
        belt-and-suspenders. We assert the result matches regardless.
        """
        # Whatever Python we're on, the shim must produce the same result as
        # the explicit +00:00 form.
        from datetime import datetime, timezone
        ref = utc_to_julian(datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        assert parse_iso_utc("2000-01-01T00:00:00Z") == pytest.approx(ref, abs=1e-12)
        assert parse_iso_utc("2000-01-01T00:00:00+00:00") == pytest.approx(ref, abs=1e-12)
        # Inform the test report which interpreter ran (for CI debugging only).
        if sys.version_info < (3, 11):
            # On 3.10 the shim is mandatory; assert reaching here proves it.
            assert True


class TestNaiveDatetime:
    """Naive datetimes (no offset) are assumed UTC."""

    def test_naive_datetime_assumed_utc(self):
        jd_naive = parse_iso_utc("2026-05-06T12:00:00")
        jd_explicit = parse_iso_utc("2026-05-06T12:00:00Z")
        assert jd_naive == pytest.approx(jd_explicit, abs=1e-12)


class TestNonUTCOffset:
    """Non-UTC offsets converted to UTC before utc_to_julian."""

    def test_plus_2_hours_offset_converts_to_utc(self):
        # 14:00+02:00 == 12:00 UTC
        jd_paris = parse_iso_utc("2026-05-06T14:00:00+02:00")
        jd_utc = parse_iso_utc("2026-05-06T12:00:00Z")
        assert jd_paris == pytest.approx(jd_utc, abs=1e-9)


class TestErrors:
    """Bad input → SystemExit with helpful message."""

    def test_empty_string_rejected(self):
        with pytest.raises(SystemExit) as exc:
            parse_iso_utc("")
        assert "--date" in str(exc.value)

    def test_not_a_date_rejected(self):
        with pytest.raises(SystemExit) as exc:
            parse_iso_utc("not-a-date")
        assert "--date" in str(exc.value)

    def test_garbage_with_z_rejected(self):
        with pytest.raises(SystemExit):
            parse_iso_utc("xxxZ")
```

Notes:
- `parse_iso_utc` raises `SystemExit` (not ArgumentTypeError) because it's called from inside the dispatcher (post-parse), not as an argparse `type=` validator. SystemExit is the cleanest "abort with message" path post-parse.
- The shim test's existence + always-runs assertion is the safety belt against accidentally deleting the shim during refactoring (Pitfall 2).
  </action>
  <verify>
1. `python -c "from ketu.cli._dates import parse_iso_utc; print(parse_iso_utc('2026-05-06T12:00:00Z'))"` prints a float ~ 2461167.0.
2. `pytest tests/cli/test_dates.py -v` — all tests pass.
3. `mypy --strict ketu/cli/_dates.py` clean.
  </verify>
  <done>
- ketu/cli/_dates.py implements parse_iso_utc with explicit Z→+00:00 shim and naive-as-UTC convention.
- Delegates final JD conversion to ketu.ephemeris.time.utc_to_julian (no parallel JD math).
- tests/cli/test_dates.py covers: Z shim (always exercises shim path), +00:00 equivalence, naive=UTC, non-UTC offset conversion, and 3 error paths.
- mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Implement cmd_houses, wire into parser, and add end-to-end tests</name>
  <files>ketu/cli/houses_cmd.py, ketu/cli/parser.py, tests/cli/test_houses_cmd.py</files>
  <action>
**Create ketu/cli/houses_cmd.py** — the `ketu houses` dispatcher.

```python
"""Dispatcher for `ketu houses ...` subcommand.

Calls :func:`ketu.calculate_houses` (Phase 10 deliverable) — registry
dispatch, no inline if/elif. Formats the 12 cusps + ASC + MC for stdout.
The resolved-config header (CLI-06) is emitted by the formatter wired in
Plan 11-04 — kept out of this dispatcher to avoid coupling.
"""
from __future__ import annotations

import argparse

import numpy as np

from ketu import calculate_houses
from ketu.calculations import dd_to_dms
from ketu.core import signs

from ._dates import parse_iso_utc


def _format_cusp(cusp_deg: float) -> str:
    """Format a cusp longitude as 'SIGN DD°MM\\'SS\"' for stdout."""
    sign_index = int(cusp_deg // 30) % 12
    in_sign = cusp_deg - 30.0 * sign_index
    degs, mins, secs = dd_to_dms(in_sign)
    return f"{signs[sign_index]:15} {degs:>2}°{mins:>2}'{secs:>2}\""


def cmd_houses(args: argparse.Namespace) -> int:
    """Compute and print the 12 house cusps + ASC + MC.

    Parameters
    ----------
    args : argparse.Namespace
        Required attributes: ``date``, ``lat``, ``lon``, ``system``,
        ``polar_fallback``.

    Returns
    -------
    int
        Process exit code: 0 on success, non-zero handled by caller.
    """
    jd = parse_iso_utc(args.date)
    # Public API; registry dispatch happens inside calculate_houses.
    rec = calculate_houses(
        jd=jd,
        lat=args.lat,
        lon=args.lon,
        system=args.system,
        polar_fallback=args.polar_fallback,
    )
    cusps = np.asarray(rec["cusps"]).reshape(-1)
    if cusps.size != 12:
        raise SystemExit(
            f"error: calculate_houses returned {cusps.size} cusps, expected 12 "
            f"(this is a Ketu bug; please report)"
        )
    print()
    print("------------- House Cusps -------------")
    for i, cusp in enumerate(cusps, start=1):
        print(f"House {i:>2}: {_format_cusp(float(cusp))} ({float(cusp):8.4f}°)")
    asc = float(rec["asc"])
    mc = float(rec["mc"])
    print()
    print(f"ASC: {_format_cusp(asc)} ({asc:8.4f}°)")
    print(f"MC : {_format_cusp(mc)} ({mc:8.4f}°)")
    return 0
```

Notes:
- Imports `calculate_houses` from `ketu` (the public re-export); registry dispatch happens inside.
- Uses existing `dd_to_dms` and `signs` for formatting (existing project utilities — research §"Don't Hand-Roll").
- `_format_cusp` returns both the SIGN/D/M/S form AND the raw degrees; the line shows both for readability and machine-parseability.
- HOUSES_DTYPE access via `rec["cusps"]` etc. — the structured array convention from `ketu/houses/core.py` (HOU-05). `.reshape(-1)` flattens any leading shape (scalar inputs produce shape `(12,)` or `(1,12)` depending on broadcast).

**Edit ketu/cli/parser.py** — replace `_stub_houses` with the real `cmd_houses`. Two changes:

1. Add an import near the other CLI imports:

```python
from .houses_cmd import cmd_houses
```

2. Update the houses subparser's `set_defaults`:

```python
p_houses.set_defaults(func=cmd_houses)  # was: func=_stub_houses
```

You can DELETE the `_stub_houses` function entirely from parser.py (or leave it; deleting is cleaner). DO NOT touch `_stub_aspects` or `_stub_list_*` (those are still in use until Plan 11-04).

**Create tests/cli/test_houses_cmd.py** — end-to-end via `invoke_main`.

```python
"""End-to-end tests for `ketu houses ...` subcommand."""
from __future__ import annotations

import numpy as np
import pytest

from ketu import calculate_houses
from ketu.cli._dates import parse_iso_utc


class TestHousesCmdMatchesPythonAPI:
    """CLI output cusps match the Python API for the same inputs (CLI-04 success criterion 4)."""

    PARIS = ("2026-05-06T12:00:00Z", 48.85, 2.35)
    SYDNEY = ("2026-05-06T12:00:00Z", -33.87, 151.21)
    GREENWICH = ("2000-01-01T12:00:00Z", 51.4769, 0.0)

    @pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
    @pytest.mark.parametrize("loc", [PARIS, SYDNEY, GREENWICH])
    def test_cli_cusps_match_python_api(self, invoke_main, capsys, system, loc):
        date_iso, lat, lon = loc
        rc = invoke_main([
            "houses",
            "--date", date_iso, "--lat", str(lat), "--lon", str(lon),
            "--system", system,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "House Cusps" in out
        # Cross-check: parse the printed degrees and compare to API.
        jd = parse_iso_utc(date_iso)
        rec = calculate_houses(jd=jd, lat=lat, lon=lon, system=system, polar_fallback="raise")
        cusps_api = np.asarray(rec["cusps"]).reshape(-1)
        # Pull each "(NNN.NNNN°)" from the output lines for verification.
        import re
        printed = [float(m.group(1)) for m in re.finditer(r"\(\s*([\d.\-]+)°\)", out)]
        # 12 cusps + ASC + MC = 14 angles printed
        assert len(printed) == 14
        for i in range(12):
            assert printed[i] == pytest.approx(cusps_api[i], abs=1e-3)


class TestHousesCmdFlags:
    """Argument validation paths."""

    def test_missing_lat_rejected(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main(["houses", "--date", "2000-01-01T12:00:00Z", "--lon", "0"])
        assert exc.value.code == 2

    def test_invalid_system_rejected(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "houses", "--date", "2000-01-01T12:00:00Z",
                "--lat", "48.85", "--lon", "2.35",
                "--system", "regiomontanus",
            ])
        assert exc.value.code == 2

    def test_default_system_is_placidus(self, invoke_main, capsys):
        rc = invoke_main([
            "houses", "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
        ])
        assert rc == 0


class TestHousesCmdPolar:
    """Polar latitudes — default raise vs porphyry fallback."""

    def test_polar_default_raises(self, invoke_main, capsys):
        """At lat=80°, default --polar-fallback=raise propagates HighLatitudeError → SystemExit."""
        with pytest.raises(Exception) as exc:
            invoke_main([
                "houses", "--date", "2000-01-01T12:00:00Z",
                "--lat", "80.0", "--lon", "0.0",
                "--system", "placidus",
            ])
        # HighLatitudeError is a ValueError subclass; not yet caught by cmd_houses
        # (intentional — surfaces as a clear traceback or non-zero exit).

    def test_polar_porphyry_fallback_succeeds(self, invoke_main, capsys):
        """--polar-fallback porphyry substitutes Porphyry cusps and returns 0."""
        rc = invoke_main([
            "houses", "--date", "2000-01-01T12:00:00Z",
            "--lat", "80.0", "--lon", "0.0",
            "--system", "placidus",
            "--polar-fallback", "porphyry",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "House Cusps" in out


class TestHousesCmdISOZShim:
    """End-to-end: 'Z' suffix accepted (Python 3.10 + 3.11+)."""

    def test_z_suffix_accepted_via_cli(self, invoke_main, capsys):
        rc = invoke_main([
            "houses", "--date", "2026-05-06T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "placidus",
        ])
        assert rc == 0
        assert "House Cusps" in capsys.readouterr().out
```

Notes:
- TestHousesCmdMatchesPythonAPI parametrizes over 3 systems × 3 locations = 9 cases — proves CLI returns same cusps as Python API across the matrix.
- TestHousesCmdPolar.test_polar_default_raises: just confirms the polar path doesn't silently succeed; deliberately permissive (`pytest.raises(Exception)`) to avoid coupling to whatever exact exit shape cmd_houses ends up with for raised errors. Plan 11-04 may revisit this if it adds a try/except in cmd_houses for prettier output.
- The regex extracts `(NNN.NNNN°)` from each printed line; `len(printed) == 14` covers the 12 cusps + ASC + MC.
- Tolerance `abs=1e-3` on cusp degrees because the formatter rounds at the 4th decimal (`{:8.4f}`); the actual API value is float64 → exact match in the underlying structured array.
  </action>
  <verify>
1. `pytest tests/cli/test_houses_cmd.py -v` — all 12+ tests pass (3 systems × 3 locations + flag tests + polar tests + Z-shim test).
2. `pytest tests/cli/ -v` — full CLI test suite green (Plan 11-01 + 11-02 + 11-03 tests).
3. `pytest tests/ -v` — full project test suite green.
4. `mypy --strict ketu/cli/` clean.
5. Manual: `python -m ketu houses --date 2026-05-06T12:00:00Z --lat 48.85 --lon 2.35 --system placidus` prints 12 cusps + ASC + MC.
  </verify>
  <done>
- ketu/cli/houses_cmd.py implements cmd_houses(args) → calls public API, formats 12 cusps + ASC + MC.
- ketu/cli/parser.py wires p_houses.set_defaults(func=cmd_houses) (replaces _stub_houses).
- tests/cli/test_houses_cmd.py covers: 9 system×location parametric cases asserting CLI output cusps match Python API; flag validation; polar-default path; polar-porphyry fallback success; ISO Z shim end-to-end.
- mypy --strict clean.
- Full project test suite green.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/cli/ -v` — all CLI tests green (parser, harmonics_spec, dates, houses_cmd).
- `pytest tests/ -v` — full project suite green; no regression.
- `python -m ketu houses --date 2026-05-06T12:00:00Z --lat 48.85 --lon 2.35` prints cusps; same numbers as `python -c "from ketu import calculate_houses; ..."`.
- `mypy --strict ketu/cli/` clean.
</verification>

<success_criteria>
- CLI-04 fully covered: `ketu houses --date X --lat Y --lon Z --system NAME` returns same cusps as `ketu.calculate_houses(jd, lat, lon, system, polar_fallback)`.
- Python 3.10 'Z' shim implemented + tested (always-exercised path; survives any future refactor).
- Naive ISO datetime treated as UTC (matches `utc_to_julian` convention).
- Non-UTC offset converted to UTC before JD math.
- Default `--system` is `placidus`; choices enforced; invalid choice → SystemExit(2).
- `--polar-fallback porphyry` succeeds at lat=80°; default raises.
- mypy --strict clean.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-03-houses-subcommand-SUMMARY.md` documenting:
- parse_iso_utc Z-shim implementation (and how it's tested under any Python version)
- cmd_houses formatter output shape
- Files: cli/_dates.py NEW, cli/houses_cmd.py NEW, cli/parser.py edit (cmd_houses wired); tests/cli/test_dates.py NEW, tests/cli/test_houses_cmd.py NEW
- Test count delta
- Any deviations from plan
</output>
