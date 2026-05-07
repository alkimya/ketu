---
phase: 11-cli-refactor-integration
plan: 02
type: execute
wave: 2
depends_on: ["11-01"]
files_modified:
  - ketu/cli/harmonics_spec.py
  - ketu/cli/parser.py
  - tests/cli/test_harmonics_spec.py
autonomous: true

must_haves:
  truths:
    - "ketu/cli/harmonics_spec.py exports parse_harmonics_spec(value: str) -> np.ndarray (length-14 np.bool_)"
    - "Preset names accepted (case-insensitive): 'classical', 'traditional', 'extended', 'all' — 'all' aliases 'extended'"
    - "Comma-separated indices accepted: '0,4,7,9,13' returns the CLASSICAL mask (5 Trues at those positions)"
    - "Bare integer rejected: '12' raises argparse.ArgumentTypeError mentioning named presets"
    - "Empty string rejected: '' raises argparse.ArgumentTypeError"
    - "Unrecognized spec rejected: 'foobar' raises argparse.ArgumentTypeError"
    - "parser.py wires type=parse_harmonics_spec on --harmonics (replacing type=str placeholder)"
    - "argparse renders ArgumentTypeError as 'error: argument --harmonics: <msg>' and exits 2 (no traceback)"
  artifacts:
    - path: ketu/cli/harmonics_spec.py
      provides: "parse_harmonics_spec validator + _PRESET_NAMES constant"
      exports: ["parse_harmonics_spec"]
      min_lines: 40
    - path: ketu/cli/parser.py
      provides: "Top-level --harmonics argument now uses parse_harmonics_spec"
      contains: "type=parse_harmonics_spec"
    - path: tests/cli/test_harmonics_spec.py
      provides: "Unit + argparse integration tests for parse_harmonics_spec"
      min_lines: 80
  key_links:
    - from: ketu/cli/harmonics_spec.py
      to: ketu/aspects/presets.py:resolve_aspect_set
      via: "Delegates resolution; harmonics_spec is a thin tokenizer"
      pattern: "from ketu\\.aspects\\.presets import resolve_aspect_set"
    - from: ketu/cli/parser.py
      to: ketu/cli/harmonics_spec.py:parse_harmonics_spec
      via: "type=parse_harmonics_spec on the --harmonics argument"
      pattern: "type=parse_harmonics_spec"
    - from: ketu/cli/harmonics_spec.py
      to: argparse.ArgumentTypeError
      via: "Raised on every invalid input path so argparse renders cleanly"
      pattern: "raise argparse\\.ArgumentTypeError"
---

<objective>
Implement the `--harmonics SPEC` argparse type validator that accepts named presets (`classical`, `traditional`, `extended`, `all`), comma-separated aspect indices (`0,4,7,9,13`), and rejects bare integers (`12`) with a helpful error pointing to named presets. Wire it into `parser.py` so `parser.parse_args` returns a length-14 `np.bool_` mask in `args.harmonics` (or `None` if the flag wasn't given).

Purpose: CLI-02 requirement. The validator is a thin tokenizer that delegates to `ketu.aspects.presets.resolve_aspect_set` (Phase 9 deliverable) — no parallel resolution logic. Bare-integer rejection enforces REQUIREMENTS.md line 101.

Output:
  - ketu/cli/harmonics_spec.py — `parse_harmonics_spec(s: str) -> np.ndarray`
  - ketu/cli/parser.py — wires `type=parse_harmonics_spec` (Plan 11-01 left it as `type=str`)
  - tests/cli/test_harmonics_spec.py — exhaustive validator tests
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

# Phase 9 deliverable — the resolver this plan delegates to
@ketu/aspects/presets.py

# Parser this plan modifies
@ketu/cli/parser.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement parse_harmonics_spec in ketu/cli/harmonics_spec.py</name>
  <files>ketu/cli/harmonics_spec.py</files>
  <action>
Create `ketu/cli/harmonics_spec.py` implementing the validator. It MUST delegate resolution to `ketu.aspects.presets.resolve_aspect_set` — do NOT recreate preset masks here.

Spec (verbatim from research §Pattern 2):
- `"classical" / "traditional" / "extended" / "all"` (case-insensitive) → preset mask. `"all"` aliases `"extended"`.
- `"0,4,7,9,13"` (comma-present, integer-coercible after strip) → call `resolve_aspect_set([0,4,7,9,13])`.
- `"12"` (NO comma, single integer) → REJECT with `argparse.ArgumentTypeError` mentioning named presets.
- `""` empty → REJECT.
- `"foobar"` → REJECT (unrecognized).

Critical: detect comma BEFORE attempting `int()` to enforce the bare-integer rule (Pitfall 5).

Critical: `resolve_aspect_set` may raise `ValueError` for out-of-range indices or duplicates — re-raise as `argparse.ArgumentTypeError` so argparse renders cleanly. Per argparse docs, ArgumentTypeError/TypeError/ValueError are caught and rendered as `error: argument --harmonics: <message>` with `SystemExit(2)`.

```python
"""--harmonics SPEC argparse type validator.

Accepts a string spec and returns a length-14 ``np.bool_`` mask suitable
for filtering ``ketu.core.aspects``. The mask is produced by
:func:`ketu.aspects.presets.resolve_aspect_set` (Phase 9 deliverable);
this module is a thin tokenizer that picks the right input shape
(preset name vs. comma-separated indices) before delegating.

Spec semantics (from REQUIREMENTS.md CLI-02 + research Pattern 2):

- ``"classical"`` / ``"traditional"`` / ``"extended"`` / ``"all"``
  (case-insensitive) → named preset. ``"all"`` aliases ``"extended"``
  (preserves the v1.0 14-aspect output via CLI-03 byte-identical).
- ``"0,4,7,9,13"`` → comma-separated canonical aspect indices into
  ``ketu.core.aspects`` (length-14 registry, append-only).
- ``"12"`` → REJECTED (Pitfall 5; REQUIREMENTS.md line 101). Bare
  integers are ambiguous (single? harmonic? subset?). Use a named
  preset or comma-separated list.
- ``""`` empty → REJECTED.
- Anything else → REJECTED with a hint listing valid preset names.

argparse convention: this function is wired as ``type=parse_harmonics_spec``
on the ``--harmonics`` argument. argparse catches ArgumentTypeError /
TypeError / ValueError and renders ``error: argument --harmonics: <msg>``
with ``SystemExit(2)``.
"""
from __future__ import annotations

import argparse
from typing import FrozenSet

import numpy as np
import numpy.typing as npt

from ketu.aspects.presets import resolve_aspect_set

_PRESET_NAMES: FrozenSet[str] = frozenset({"classical", "traditional", "extended", "all"})


def parse_harmonics_spec(value: str) -> npt.NDArray[np.bool_]:
    """Parse a ``--harmonics SPEC`` string into a length-14 boolean mask.

    Parameters
    ----------
    value : str
        Spec string. See module docstring for accepted forms.

    Returns
    -------
    np.ndarray of np.bool_, shape (14,)
        Boolean mask indexable into ``ketu.core.aspects``.

    Raises
    ------
    argparse.ArgumentTypeError
        On any invalid spec. argparse converts this to a clean
        ``error: argument --harmonics: <message>`` and exits with code 2.
    """
    if value is None or value == "":
        raise argparse.ArgumentTypeError(
            "--harmonics requires a value (named preset or comma-separated list)"
        )

    s = value.strip().lower()
    if not s:
        raise argparse.ArgumentTypeError(
            "--harmonics requires a non-blank value"
        )

    # Preset names — including 'all' alias for 'extended'.
    if s in _PRESET_NAMES:
        if s == "all":
            s = "extended"
        try:
            return resolve_aspect_set(s)
        except ValueError as e:  # defensive — resolve_aspect_set should accept all preset names
            raise argparse.ArgumentTypeError(str(e))

    # Comma-present → list of indices.
    if "," in s:
        try:
            indices = [int(x.strip()) for x in s.split(",") if x.strip()]
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}: expected comma-separated "
                f"integers in [0, 14) (e.g. '0,4,7,9,13')"
            )
        if not indices:
            raise argparse.ArgumentTypeError(
                f"empty harmonics list {value!r}"
            )
        try:
            return resolve_aspect_set(indices)
        except (ValueError, TypeError) as e:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}: {e}"
            )

    # No comma — try bare integer detection (must REJECT per spec).
    try:
        int(s)
    except ValueError:
        pass  # not an integer — fall through to "unrecognized" branch
    else:
        valid = sorted(_PRESET_NAMES)
        raise argparse.ArgumentTypeError(
            f"bare integer {value!r} is ambiguous (single index? harmonic "
            f"number? subset?); use a named preset ({', '.join(valid)}) or "
            f"a comma-separated list (e.g. '{value},...')"
        )

    valid = sorted(_PRESET_NAMES)
    raise argparse.ArgumentTypeError(
        f"unrecognized harmonics spec {value!r}: expected one of "
        f"{valid} or comma-separated indices in [0, 14)"
    )
```

Notes:
- `from __future__ import annotations` (project convention).
- Public symbol exposed: just `parse_harmonics_spec`. No `__all__` needed (module is internal CLI plumbing).
- mypy --strict clean: explicit `npt.NDArray[np.bool_]` return type.
  </action>
  <verify>
1. `python -c "from ketu.cli.harmonics_spec import parse_harmonics_spec; m = parse_harmonics_spec('classical'); print(m.shape, m.sum())"` → `(14,) 5`.
2. `python -c "from ketu.cli.harmonics_spec import parse_harmonics_spec; m = parse_harmonics_spec('all'); print(m.sum())"` → `14`.
3. `python -c "from ketu.cli.harmonics_spec import parse_harmonics_spec; parse_harmonics_spec('12')"` raises `argparse.ArgumentTypeError`.
4. `mypy --strict ketu/cli/harmonics_spec.py` clean.
  </verify>
  <done>
- ketu/cli/harmonics_spec.py implements parse_harmonics_spec(value: str) -> npt.NDArray[np.bool_].
- All 5 spec branches implemented: preset (incl. 'all' alias), comma-list, bare-integer reject, empty reject, unrecognized reject.
- Delegates to ketu.aspects.presets.resolve_aspect_set — no parallel preset masks.
- mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: Wire parse_harmonics_spec into parser.py and add validator tests</name>
  <files>ketu/cli/parser.py, tests/cli/test_harmonics_spec.py</files>
  <action>
**Edit ketu/cli/parser.py** — replace the placeholder `type=str` on the top-level `--harmonics` argument with the real validator. Two changes:

1. Add an import at the top of the file (after the stdlib imports, before the stub functions):

```python
from .harmonics_spec import parse_harmonics_spec
```

2. Update the `--harmonics` `add_argument` call:

```python
parser.add_argument(
    "--harmonics",
    type=parse_harmonics_spec,   # was: type=str (Plan 11-01 placeholder)
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
```

That's the only edit to `parser.py`.

**One existing test to update**: `tests/cli/test_parser.py::TestBuildParser::test_top_level_harmonics_present` was written in Plan 11-01 expecting `args.harmonics == "classical"` (string passthrough). After this task, it will be a length-14 np.bool_ array. Update the assertion:

```python
def test_top_level_harmonics_present(self):
    parser = build_parser()
    args = parser.parse_args([
        "--harmonics", "classical",
        "aspects", "--date", "2026-05-06T12:00:00Z",
    ])
    # After Plan 11-02, type=parse_harmonics_spec returns a length-14 mask.
    import numpy as np
    assert isinstance(args.harmonics, np.ndarray)
    assert args.harmonics.dtype == np.bool_
    assert args.harmonics.shape == (14,)
    assert args.harmonics.sum() == 5  # CLASSICAL = 5 majors
```

**Create tests/cli/test_harmonics_spec.py** — exhaustive coverage:

```python
"""Unit tests for ketu.cli.harmonics_spec.parse_harmonics_spec."""
from __future__ import annotations

import argparse

import numpy as np
import pytest

from ketu.cli.harmonics_spec import parse_harmonics_spec


class TestPresetNames:
    """Named presets: classical, traditional, extended, all (case-insensitive)."""

    def test_classical_returns_5_aspect_mask(self):
        mask = parse_harmonics_spec("classical")
        assert isinstance(mask, np.ndarray)
        assert mask.dtype == np.bool_
        assert mask.shape == (14,)
        assert mask.sum() == 5
        # Conjunction (0), Sextile (4), Square (7), Trine (9), Opposition (13)
        assert list(np.where(mask)[0]) == [0, 4, 7, 9, 13]

    def test_traditional_returns_7_aspect_mask(self):
        mask = parse_harmonics_spec("traditional")
        assert mask.sum() == 7
        # CLASSICAL + Semi-sextile (1) + Quincunx (11)
        assert list(np.where(mask)[0]) == [0, 1, 4, 7, 9, 11, 13]

    def test_extended_returns_14_aspect_mask(self):
        mask = parse_harmonics_spec("extended")
        assert mask.sum() == 14
        assert mask.all()

    def test_all_aliases_extended(self):
        """'all' is an alias for 'extended' (CLI-02 + ROADMAP backward compat)."""
        mask_all = parse_harmonics_spec("all")
        mask_extended = parse_harmonics_spec("extended")
        assert np.array_equal(mask_all, mask_extended)

    def test_preset_names_case_insensitive(self):
        for variant in ["CLASSICAL", "Classical", "cLaSsIcAl"]:
            mask = parse_harmonics_spec(variant)
            assert mask.sum() == 5

    def test_preset_names_strip_whitespace(self):
        mask = parse_harmonics_spec("  classical  ")
        assert mask.sum() == 5


class TestCommaSeparatedIndices:
    """Explicit aspect-index lists."""

    def test_classical_indices_match_preset(self):
        mask = parse_harmonics_spec("0,4,7,9,13")
        preset = parse_harmonics_spec("classical")
        assert np.array_equal(mask, preset)

    def test_single_index_with_comma_accepted(self):
        """'9,' (Trine only) is unambiguous — a list of one — and is accepted."""
        mask = parse_harmonics_spec("9,")
        assert mask.sum() == 1
        assert mask[9]

    def test_indices_with_whitespace(self):
        mask = parse_harmonics_spec(" 0 , 4 , 7 , 9 , 13 ")
        assert mask.sum() == 5

    def test_out_of_range_index_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("0,99")
        assert "0,99" in str(exc.value) or "99" in str(exc.value)

    def test_non_integer_in_list_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("0,foo,7")
        assert "0,foo,7" in str(exc.value)


class TestBareIntegerRejection:
    """REQUIREMENTS.md line 101 + research Pitfall 5: bare integer must reject."""

    def test_bare_integer_12_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("12")
        msg = str(exc.value)
        assert "bare integer" in msg
        assert "named preset" in msg or "preset" in msg

    def test_bare_integer_0_rejected(self):
        """Even '0' (which would be a valid index in a list) rejects when bare."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("0")

    def test_bare_integer_9_rejected(self):
        """Even '9' (Trine) rejects when bare — must use '9,' or 'classical'."""
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("9")


class TestInvalidInputs:
    """Empty / whitespace / unrecognized."""

    def test_empty_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError):
            parse_harmonics_spec("   ")

    def test_unrecognized_word_rejected(self):
        with pytest.raises(argparse.ArgumentTypeError) as exc:
            parse_harmonics_spec("foobar")
        assert "foobar" in str(exc.value)


class TestArgparseIntegration:
    """End-to-end: parser.parse_args(['--harmonics', '12', ...]) → SystemExit(2)."""

    def test_argparse_renders_bare_integer_error_cleanly(self, capsys):
        """Bare-integer rejection surfaces via argparse's standard error path."""
        from ketu.cli.parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([
                "--harmonics", "12",
                "aspects", "--date", "2026-05-06T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--harmonics" in err
        assert "bare integer" in err

    def test_argparse_classical_returns_5_aspect_mask(self):
        from ketu.cli.parser import build_parser
        parser = build_parser()
        args = parser.parse_args([
            "--harmonics", "classical",
            "aspects", "--date", "2026-05-06T12:00:00Z",
        ])
        assert args.harmonics.sum() == 5

    def test_argparse_default_is_none(self):
        """Without --harmonics, args.harmonics is None (resolved to CLASSICAL by aspects_cmd in 11-04)."""
        from ketu.cli.parser import build_parser
        parser = build_parser()
        args = parser.parse_args(["aspects", "--date", "2026-05-06T12:00:00Z"])
        assert args.harmonics is None

    def test_argparse_renders_unrecognized_error(self, capsys):
        from ketu.cli.parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([
                "--harmonics", "foobar",
                "aspects", "--date", "2026-05-06T12:00:00Z",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "foobar" in err
```

Notes:
- TestArgparseIntegration tests both the validator AND its argparse wiring — proves Task 1 + Task 2 wiring as a unit.
- The bare-integer rejection test uses `capsys.readouterr().err` (Pitfall 9 — argparse writes to stderr).
- Total: ~22 tests. All in-process (no subprocess).
  </action>
  <verify>
1. `pytest tests/cli/test_harmonics_spec.py -v` — all ~22 tests pass.
2. `pytest tests/cli/test_parser.py -v` — Plan 11-01 tests still pass after the `test_top_level_harmonics_present` update.
3. `pytest tests/ -v` — full suite green.
4. `mypy --strict ketu/cli/` — clean.
  </verify>
  <done>
- ketu/cli/parser.py wires `type=parse_harmonics_spec` (replacing Plan 11-01's `type=str`).
- tests/cli/test_parser.py::test_top_level_harmonics_present updated to assert numpy mask shape, dtype, sum.
- tests/cli/test_harmonics_spec.py provides exhaustive coverage:
  - 4 preset names (classical, traditional, extended, all-alias) + case-insensitive + whitespace-strip
  - Comma-separated lists (matching CLASSICAL, single-with-trailing-comma, whitespace-tolerant, out-of-range reject, non-int reject)
  - Bare-integer rejection (12, 0, 9)
  - Invalid inputs (empty, whitespace-only, unrecognized word)
  - 4 argparse end-to-end tests (bare-int → SystemExit(2) on stderr, classical → 5-bit mask, default=None, unrecognized → SystemExit(2))
- Full project test suite green; mypy --strict clean.
  </done>
</task>

</tasks>

<verification>
- `pytest tests/cli/ -v` — all parser + harmonics_spec tests pass.
- `pytest tests/ -v` — full suite green; no regression in 638 existing tests.
- `mypy --strict ketu/cli/` clean.
- Sanity check: `python -c "from ketu.cli.parser import build_parser; p = build_parser(); a = p.parse_args(['--harmonics','classical','aspects','--date','2000-01-01T00:00:00Z']); print(a.harmonics.sum())"` prints `5`.
- Sanity check: `python -c "from ketu.cli.parser import build_parser; build_parser().parse_args(['--harmonics','12','aspects','--date','2000-01-01T00:00:00Z'])"` exits 2 with `bare integer` in stderr.
</verification>

<success_criteria>
- CLI-02 fully covered at the validator layer:
  - Named presets: classical / traditional / extended / all (case-insensitive)
  - Comma-separated indices: 0,4,7,9,13 etc.
  - Bare integer 12 rejected with helpful error
  - Empty / unrecognized rejected
- argparse renders ArgumentTypeError as `error: argument --harmonics: <msg>` with SystemExit(2) — no traceback (Pitfall 9 covered).
- Validator delegates to `ketu.aspects.presets.resolve_aspect_set` (no parallel mask logic).
- mypy --strict clean on the new module.
</success_criteria>

<output>
After completion, create `.planning/phases/11-cli-refactor-integration/11-02-harmonics-spec-validator-SUMMARY.md` documenting:
- parse_harmonics_spec implementation summary (input branches, error rendering)
- Files modified (cli/harmonics_spec.py NEW; cli/parser.py edit; tests/cli/test_harmonics_spec.py NEW; tests/cli/test_parser.py: test_top_level_harmonics_present updated)
- Test count delta (added ~22 tests; updated 1)
- Any deviations from plan
</output>
