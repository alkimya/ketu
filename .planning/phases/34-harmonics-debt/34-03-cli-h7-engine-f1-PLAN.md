---
phase: 34-harmonics-debt
plan: 03
type: execute
wave: 2
depends_on: ["34-01"]
files_modified:
  - ketu/cli/harmonics_spec.py
  - ketu/cli/aspects_cmd.py
  - ketu/cli/formatters.py
  - ketu/cli/parser.py
  - ketu/display.py
  - tests/cli/test_harmonics_spec.py
  - tests/cli/test_parser.py
  - tests/cli/test_aspects_cmd.py
autonomous: true

must_haves:
  truths:
    - "parse_harmonics_spec returns a HarmonicsSelection NamedTuple (mask, dynamic_specs), clean under mypy --strict"
    - "'--harmonics h7' (case-insensitive) is accepted and produces 3 dynamic specs (H7-1/2/3) with an all-False mask"
    - "'h7' is parsed by ^h(\\d+)$ AFTER the preset+comma branches and BEFORE the bare-int trap"
    - "Tight grammar: 'h7,h11' and 'traditional,h7' are rejected (deferred), preset and index-list inputs still return dynamic_specs=None"
    - "print_aspects accepts dynamic_specs= and displays synthetic H7-k names for i_asp=-2 rows (NOT Quadrinovile)"
    - "cmd_aspects threads dynamic_specs= through and the stderr header labels the selection '# Aspect set: h7 (...)'"
    - "h<N> range validation is delegated to generate_harmonic_aspects (h1/h0/h65 rejected via wrapped ValueError)"
  artifacts:
    - path: ketu/cli/harmonics_spec.py
      provides: "HarmonicsSelection NamedTuple + ^h(\\d+)$ parse branch; parse_harmonics_spec returns HarmonicsSelection"
      contains: "class HarmonicsSelection"
    - path: ketu/display.py
      provides: "print_aspects(jdate, aspects=None, dynamic_specs=None) with synthetic-name lookup for i_asp=-2"
      contains: "dynamic_specs"
    - path: ketu/cli/aspects_cmd.py
      provides: "destructures HarmonicsSelection, threads dynamic_specs=, harmonic header label"
      contains: "dynamic_specs"
    - path: ketu/cli/formatters.py
      provides: "emit_resolved_config gains dynamic_label override for the harmonic case"
      contains: "dynamic_label"
    - path: tests/cli/test_harmonics_spec.py
      provides: "TestHarmonicTokenF1 + updated existing assertions accessing .mask"
      contains: "TestHarmonicTokenF1"
  key_links:
    - from: ketu.cli.aspects_cmd.cmd_aspects
      to: ketu.cli.harmonics_spec.HarmonicsSelection
      via: "destructure args.harmonics.mask / args.harmonics.dynamic_specs"
      pattern: "\\.dynamic_specs"
    - from: ketu.cli.aspects_cmd.cmd_aspects
      to: ketu.display.print_aspects
      via: "print_aspects(jd, aspects=mask, dynamic_specs=dyn)"
      pattern: "print_aspects\\("
    - from: ketu.cli.harmonics_spec.parse_harmonics_spec
      to: ketu.aspects.harmonics.generate_harmonic_aspects
      via: "h<N> branch calls generate_harmonic_aspects(h); range ValueError wrapped as ArgumentTypeError"
      pattern: "generate_harmonic_aspects"
---

<objective>
Pay down debt **F1 (ASP-F1) — engine surface (HARM-06, HARM-07)**: wire
`--harmonics h7` end-to-end through the parser, the spec validator, the command
dispatcher, and the display layer.

Purpose: This is the broadest debt. It DEPENDS on F2 (Plan 01) — the `H{h}-{k}`
naming contract must be stable before the CLI surfaces it. This plan delivers
the CODE + unit/integration tests; the byte-stability fixture + docs are split
into Plan 04 (Wave 3) which depends on this plan's CLI being functional.

A bug discovered in research (NOT in the original brief) is fixed here:
`print_aspects` in `display.py` does `_CORE_ASPECTS['name'][i_asp]`, and for
dynamic rows `i_asp=-2` maps to `b'Quadrinovile'` — WRONG. `print_aspects` MUST
be extended with `dynamic_specs=` to display the correct synthetic `H7-k` names.

Output:
- `HarmonicsSelection` NamedTuple `(mask, dynamic_specs)` + a `^h(\d+)$` parse
  branch in `harmonics_spec.py`.
- `print_aspects(..., dynamic_specs=None)` with synthetic-name lookup.
- `cmd_aspects` destructuring + `dynamic_specs=` threading + harmonic header label.
- `emit_resolved_config(..., dynamic_label=None)`.
- Updated `--harmonics` help text.
- ALL existing test assertions that accessed the raw mask updated to `.mask`,
  plus a new `TestHarmonicTokenF1` unit class and `--harmonics h7` integration
  tests.
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
@.planning/phases/34-harmonics-debt/34-RESEARCH.md

@ketu/cli/harmonics_spec.py
@ketu/cli/aspects_cmd.py
@ketu/cli/formatters.py
@ketu/cli/parser.py
@ketu/display.py
@ketu/aspects/harmonics.py
@ketu/aspects/calculator.py

**Hard gates (bake into verification):**
- `fail_under=100` coverage, zero pragma — every NEW branch covered:
  the `^h(\d+)$` branch, the wrapped-ValueError range-rejection path, the
  `dynamic_specs is not None` path in `print_aspects`, the `_harmonic_label`
  helper, the `dynamic_label` path in `emit_resolved_config`.
- mypy `--strict` clean on all changed modules — `HarmonicsSelection` NamedTuple
  typed; consumers annotated `HarmonicsSelection | None`.
- numpydoc + interrogate pass for `harmonics_spec.py` (module + function
  docstrings), `display.py` (`print_aspects`), `formatters.py`, `aspects_cmd.py`.
- Pure-NumPy runtime (no pyswisseph under `ketu/`).
- core.aspects V1/V13 sha256 fingerprints byte-identical (no core.py change).

**Locked decisions (do NOT reopen):**
- Grammar = Tight: `h7` alone OR the existing comma index list. `traditional,h7`
  and `h7,h11` are EXPLICITLY DEFERRED (HARMF-01). Do NOT implement them.
- CLI token: `h<N>` via regex `^h(\d+)$`, applied AFTER preset + comma branches,
  BEFORE the bare-int trap. Case-insensitive (existing `.lower()` handles it).
  Range validation left to `generate_harmonic_aspects` — let its `ValueError`
  propagate, wrapped as `argparse.ArgumentTypeError`.
- `parse_harmonics_spec` returns `HarmonicsSelection` NamedTuple `(mask,
  dynamic_specs)`, reusing the existing `DynamicAspectSpec` type alias from
  `ketu.aspects.harmonics` (do NOT invent a new alias). For preset / index-list
  inputs, `dynamic_specs=None`. For `h<N>`, `mask` is all-False (length-14) and
  `dynamic_specs` holds the generator output.
- Header label: thread harmonic token(s) into the resolved-config stderr header
  (e.g. `# Aspect set: h7 (3 aspects: H7-1 51°, ...)`). The all-False mask would
  otherwise produce `(0 aspects: )` — use the `dynamic_label` override.
- The always-on "Aspect Timing Example" Sun-Moon block in `aspects_cmd.py:109-125`
  stays classical-pinned and UNCHANGED.
</context>

<tasks>

<task type="auto">
  <name>Task 1: HarmonicsSelection + ^h(\d+)$ branch; print_aspects dynamic_specs</name>
  <files>ketu/cli/harmonics_spec.py, ketu/display.py</files>
  <action>
**A) `ketu/cli/harmonics_spec.py`:**
  - Add imports: `from typing import NamedTuple`, `import re`,
    `from ketu.aspects.harmonics import DynamicAspectSpec, generate_harmonic_aspects`.
  - Define the NamedTuple (numpydoc-documented):
    ```python
    class HarmonicsSelection(NamedTuple):
        mask: npt.NDArray[np.bool_]      # length-14, always present
        dynamic_specs: DynamicAspectSpec  # None for preset/list; array for h<N>
    ```
  - Compile `_H_TOKEN_RE = re.compile(r"^h(\d+)$")` at module level.
  - Change `parse_harmonics_spec` return type to `HarmonicsSelection`. Wrap the
    two existing successful returns (preset branch ~L79, comma branch ~L97) as
    `HarmonicsSelection(mask=<existing mask>, dynamic_specs=None)`.
  - Insert the NEW `h<N>` branch AFTER the comma branch (~L101) and BEFORE the
    bare-int trap (~L104):
    ```python
    m = _H_TOKEN_RE.match(s)
    if m:
        try:
            specs = generate_harmonic_aspects(int(m.group(1)))
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
        return HarmonicsSelection(
            mask=np.zeros(14, dtype=np.bool_), dynamic_specs=specs
        )
    ```
    Order is now: (1) preset, (2) comma, (3) `h<N>`, (4) bare-int rejection,
    (5) unrecognized. `h7,h11` enters the comma branch and fails (`int("h7")`
    → wrapped ArgumentTypeError) — the locked Tight-grammar rejection. The
    range check (`h1`/`h0`/`h65`) is delegated to `generate_harmonic_aspects`,
    whose ValueError is wrapped here.
  - Update the module docstring AND the function docstring (Returns section) to
    describe `HarmonicsSelection` and the `h<N>` form (was "returns a length-14
    np.bool_ mask").

**B) `ketu/display.py` — `print_aspects`:**
  - Import `from ketu.aspects.harmonics import DynamicAspectSpec` and the
    `_normalize_dynamic_specs` helper from `ketu.aspects.calculator` (reuse —
    do NOT duplicate the normalisation logic; keep DRY).
  - New signature:
    `def print_aspects(jdate, aspects=None, dynamic_specs: DynamicAspectSpec = None) -> None:`
    (default `None` keeps every existing `print_aspects(jd)` / `print_aspects(jd, aspects=mask)`
    call unchanged).
  - Forward `dynamic_specs=dynamic_specs` to `calculate_aspects(...)`.
  - For each row: when `i_asp == -2`, look up the synthetic name from the
    normalised dynamic specs by matching the row's angle, mirroring the name
    resolution in `calculator.py:744-759` (`np.where(dyn['angle'] == ...)` →
    decode bytes name). When `i_asp != -2`, keep the existing
    `_CORE_ASPECTS['name'][i_asp]` decode path. This fixes the
    `b'Quadrinovile'` bug for dynamic rows.
  - Update the `print_aspects` numpydoc (add `dynamic_specs` parameter block).
  </action>
  <verify>
`venv/bin/python -c "from ketu.cli.harmonics_spec import parse_harmonics_spec, HarmonicsSelection as H; r=parse_harmonics_spec('h7'); assert isinstance(r,H); assert r.mask.sum()==0; assert r.dynamic_specs['name'].tolist()==[b'H7-1',b'H7-2',b'H7-3']; print('h7 OK'); r2=parse_harmonics_spec('classical'); assert r2.dynamic_specs is None and r2.mask.sum()==5; print('preset OK')"`
→ prints OK lines. `venv/bin/python -c "from ketu.cli.harmonics_spec import parse_harmonics_spec; import argparse;\nfor bad in ['h1','h0','h65']:\n  try: parse_harmonics_spec(bad); raise SystemExit('should have raised '+bad)\n  except argparse.ArgumentTypeError: pass\nprint('range-reject OK')"`
→ prints range-reject OK. `venv/bin/mypy --strict ketu/cli/harmonics_spec.py ketu/display.py` → clean.
  </verify>
  <done>
parse_harmonics_spec returns HarmonicsSelection; `h7`/`H7` accepted (3 specs,
all-False mask); preset/list return dynamic_specs=None; h1/h0/h65 rejected via
wrapped ArgumentTypeError; print_aspects accepts dynamic_specs and resolves
i_asp=-2 to H7-k; mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 2: cmd_aspects destructure + thread dynamic_specs + harmonic header; formatters + parser help</name>
  <files>ketu/cli/aspects_cmd.py, ketu/cli/formatters.py, ketu/cli/parser.py</files>
  <action>
**A) `ketu/cli/formatters.py` — `emit_resolved_config`:**
  - Add an optional `dynamic_label: str | None = None` parameter. When provided
    (non-None), it OVERRIDES the mask-derived detail string: print
    `# Aspect set: {preset_name} ({dynamic_label})` instead of iterating the
    all-False mask (which would yield `(0 aspects: )`). When `dynamic_label` is
    None, behaviour is UNCHANGED (existing mask-iteration path) — this preserves
    the v1.1 byte-stable header for all existing invocations.
  - Update the numpydoc to document `dynamic_label`.

**B) `ketu/cli/aspects_cmd.py` — `cmd_aspects`:**
  - Replace the `args.harmonics` consumption block (lines ~90-95). New logic:
    ```python
    if args.harmonics is None:
        mask = resolve_aspect_set("classical"); dyn = None
        preset_label = "classical"; dynamic_label = None
    else:
        mask = args.harmonics.mask
        dyn = args.harmonics.dynamic_specs
        if dyn is None:
            preset_label = _preset_label_for_mask(mask); dynamic_label = None
        else:
            preset_label, dynamic_label = _harmonic_label(dyn)
    ```
  - Add a small module-level `_harmonic_label(dyn)` helper (numpydoc-documented)
    that derives the harmonic token + the detail string from the dynamic specs:
    `h = int(dyn['harmonic'][0])`; label = `f"h{h}"`; detail =
    e.g. `f"{len(dyn)} aspects: " + ", ".join(f"{name.decode()} {int(round(ang))}°" ...)`.
    Returns `(label, detail)` so the header reads
    `# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 103°, H7-3 154°)`.
  - Update the `emit_resolved_config` call to pass `dynamic_label=dynamic_label`.
  - Update the `print_aspects` call to
    `print_aspects(jd, aspects=mask, dynamic_specs=dyn)`.
  - Leave the trailing "Aspect Timing Example" Sun-Moon block (lines ~109-125)
    EXACTLY as-is — classical-pinned, no dynamic_specs (byte-stability of the
    v1.1 fixture depends on it).

**C) `ketu/cli/parser.py` — help text:**
  - Extend the `--harmonics` help string to document the `h<N>` form, e.g. add:
    "or an arbitrary harmonic 'h<N>' (e.g. 'h7' → septile family, h//2 dynamic
    aspects)." Update the stale "returns a length-14 mask" wording in the
    adjacent comment (lines ~82-84) to reflect `HarmonicsSelection`. No other
    parser change — `type=parse_harmonics_spec` already routes `h7`.
  </action>
  <verify>
`venv/bin/python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z 1>/tmp/h7.out 2>/tmp/h7.err; echo rc=$?`
→ rc=0. `grep -E "H7-1|H7-2|H7-3" /tmp/h7.out` → synthetic names present (NOT
Quadrinovile). `grep "Quadrinovile" /tmp/h7.out` → no match. `grep "# Aspect set: h7" /tmp/h7.err`
→ header label present. `grep "Aspect Timing Example" /tmp/h7.out` → trailing
block still emitted. `venv/bin/mypy --strict ketu/cli/aspects_cmd.py ketu/cli/formatters.py ketu/cli/parser.py`
→ clean.
  </verify>
  <done>
`--harmonics h7` runs (rc=0), stdout shows H7-1/2/3 (no Quadrinovile), stderr
shows `# Aspect set: h7 (...)`, the classical Aspect Timing Example block is
unchanged, mypy --strict clean.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update broken assertions + add TestHarmonicTokenF1 + h7 integration tests</name>
  <files>tests/cli/test_harmonics_spec.py, tests/cli/test_parser.py, tests/cli/test_aspects_cmd.py</files>
  <action>
The `HarmonicsSelection` return-type change breaks EVERY existing test that
accessed the raw return value as an ndarray. Research listed ~9; the actual
extent is larger (11 assignment sites in `test_harmonics_spec.py` + 4
assertions in `test_parser.py`). Update ALL of them — do NOT miss any:

**A) `tests/cli/test_harmonics_spec.py` — update existing (lines 15-67, 140):**
  - Every `mask = parse_harmonics_spec(<preset-or-list>)` site: either rename to
    `sel = parse_harmonics_spec(...)` and access `sel.mask`, OR keep the name and
    immediately destructure `mask = parse_harmonics_spec(...).mask`. Apply to all
    11 assignment sites (lines 16, 25, 31, 37-38, 43, 47, 55-56, 61, 66) and
    every downstream `.sum()/.dtype/.shape/.all()/[9]/np.array_equal(mask,...)`.
  - Line 140 (`test_argparse_classical_returns_5_aspect_mask`):
    `args.harmonics.sum()` → `args.harmonics.mask.sum()`.
  - For preset/list tests, ALSO assert `parse_harmonics_spec(...).dynamic_specs is None`
    (proves the dynamic channel is off for the classic paths — HARM-07).
  - The rejection tests (bare-int, empty, blank, foobar, out-of-range list) are
    UNCHANGED (they raise; no `.mask` access).

**B) `tests/cli/test_parser.py` — update lines 114-117:**
  - `isinstance(args.harmonics, np.ndarray)` →
    `isinstance(args.harmonics, HarmonicsSelection)` (import it).
  - `args.harmonics.dtype` → `args.harmonics.mask.dtype`;
    `.shape` → `.mask.shape`; `.sum()` → `.mask.sum()`.
  - `test_harmonics_default_is_none` (line ~119-125) is UNCHANGED (None path).

**C) Add `class TestHarmonicTokenF1` to `tests/cli/test_harmonics_spec.py`**
  (covers HARM-06/07, every new branch):
  - `test_h7_accepted_returns_named_tuple` — isinstance HarmonicsSelection.
  - `test_h7_mask_is_all_false` — `len==14`, `.mask.sum()==0`.
  - `test_h7_dynamic_specs_has_3_rows` — `len(.dynamic_specs)==3`.
  - `test_h7_dynamic_specs_names` — `['name'].tolist()==[b'H7-1',b'H7-2',b'H7-3']`.
  - `test_H7_uppercase_accepted` — `parse_harmonics_spec('H7')` works (case-insensitive).
  - `test_h2_accepted_1_row` and `test_h64_accepted_32_rows` — boundaries.
  - `test_h1_rejected`, `test_h65_rejected`, `test_h0_rejected` — out-of-range →
    `pytest.raises(argparse.ArgumentTypeError)` (delegated range check).
  - `test_h7_comma_h11_rejected` — `parse_harmonics_spec('h7,h11')` raises
    ArgumentTypeError (Tight grammar — `h7,h11` deferred).
  - `test_traditional_comma_h7_rejected` — `parse_harmonics_spec('traditional,h7')`
    raises (mixing deferred).
  - `test_argparse_h7_end_to_end` — `build_parser().parse_args(['--harmonics','h7','aspects','--date',...])`
    yields `args.harmonics` a HarmonicsSelection with 3 dynamic specs.

**D) Add `--harmonics h7` integration tests to `tests/cli/test_aspects_cmd.py`**
  (use the existing `invoke_main`/`capsys` fixtures, mirror
  `TestAspectsCmdHarmonicsAll`):
  - `test_h7_runs_and_shows_synthetic_names` — invoke `--harmonics h7 aspects
    --date 2000-01-01T12:00:00Z`; assert rc==0; stdout contains `H7-` and does
    NOT contain `Quadrinovile`.
  - `test_h7_header_says_h7` — stderr contains `# Aspect set: h7`.
  - `test_h7_timing_example_still_classical` — stdout still contains the
    "Aspect Timing Example" block (always-on, classical-pinned).
  </action>
  <verify>
`venv/bin/pytest tests/cli/test_harmonics_spec.py tests/cli/test_parser.py tests/cli/test_aspects_cmd.py -v`
→ all pass (updated existing + new TestHarmonicTokenF1 + h7 integration).
`venv/bin/pytest tests/ -q` → full suite green. Coverage:
`venv/bin/pytest tests/cli/ --cov=ketu/cli/harmonics_spec --cov=ketu/cli/aspects_cmd --cov=ketu/cli/formatters --cov=ketu/display --cov-report=term-missing -q`
→ no missing lines in the changed modules (all new branches covered).
  </verify>
  <done>
All previously-broken assertions updated to `.mask`; TestHarmonicTokenF1 + h7
integration tests pass; Tight-grammar rejections (`h7,h11`, `traditional,h7`)
tested; full suite green; 100% coverage on changed CLI/display modules.
  </done>
</task>

</tasks>

<verification>
- `venv/bin/pytest tests/ -q` → full suite green; `fail_under=100`; zero pragma.
- `venv/bin/mypy --strict ketu/cli/harmonics_spec.py ketu/cli/aspects_cmd.py ketu/cli/formatters.py ketu/cli/parser.py ketu/display.py`
  → clean.
- numpydoc + interrogate pass for the changed public functions.
- `venv/bin/python -m ketu --harmonics h7 aspects --date 2000-01-01T12:00:00Z`
  → rc=0, H7-k names in stdout, `# Aspect set: h7` in stderr, no Quadrinovile.
- Existing `TestV1_1ReferenceByteStable` still passes UNCHANGED (no fixture
  re-pin; the h7 fixture itself is Plan 04).
- V1/V13 sha256 fingerprint tests green (no core.aspects drift).
</verification>

<success_criteria>
- HARM-06: `--harmonics h7` (case-insensitive) accepted; yields h//2 dynamic
  aspects via dynamic_specs=; disambiguated from bare-int and preset/index syntax.
- HARM-07: parse_harmonics_spec returns the HarmonicsSelection NamedTuple
  (mask + dynamic_specs), mypy --strict clean; Tight grammar (`h7,h11` and
  `traditional,h7` rejected/deferred).
- print_aspects Quadrinovile bug fixed (i_asp=-2 → H7-k).
- All broken test assertions updated; coverage 100% on changed modules.
</success_criteria>

<output>
After completion, create `.planning/phases/34-harmonics-debt/34-03-SUMMARY.md`.
</output>
