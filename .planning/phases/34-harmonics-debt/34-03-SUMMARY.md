---
phase: 34-harmonics-debt
plan: 03
subsystem: cli
tags: [harmonics, argparse, display, namedtuple, mypy, coverage]

# Dependency graph
requires:
  - phase: 34-01
    provides: "H{h}-{k} naming contract + generate_harmonic_aspects + DynamicAspectSpec type alias"
provides:
  - "HarmonicsSelection NamedTuple (mask, dynamic_specs) replaces bare ndarray return from parse_harmonics_spec"
  - "^h(\\d+)$ parse branch: --harmonics h7 accepted, range delegated to generate_harmonic_aspects"
  - "print_aspects(dynamic_specs=) with _resolve_dynamic_name: fixes Quadrinovile bug for i_asp=-2 rows"
  - "cmd_aspects destructures HarmonicsSelection, threads dynamic_specs=, emits harmonic header label"
  - "emit_resolved_config(dynamic_label=) override for h<N> all-False mask"
  - "Tight grammar: h7,h11 and traditional,h7 rejected (deferred, HARMF-01)"
  - "100% coverage on all changed modules; mypy --strict clean; 1617 tests pass"
affects: ["34-04"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "NamedTuple for structured CLI parse results (HarmonicsSelection)"
    - "_normalize_dynamic_specs reused from calculator.py (DRY)"
    - "assert isinstance(dyn, np.ndarray) for mypy narrowing of DynamicAspectSpec union"
    - "monkeypatch defensive ValueError test for unreachable branch coverage"

key-files:
  created: []
  modified:
    - ketu/cli/harmonics_spec.py
    - ketu/display.py
    - ketu/cli/aspects_cmd.py
    - ketu/cli/formatters.py
    - ketu/cli/parser.py
    - tests/cli/test_harmonics_spec.py
    - tests/cli/test_parser.py
    - tests/cli/test_aspects_cmd.py

key-decisions:
  - "HarmonicsSelection NamedTuple replaces bare ndarray: cleaner typed contract, enables dynamic_specs=None distinction"
  - "_resolve_dynamic_name recomputes angular separation from jdate+body IDs to identify matched dyn row (no angle stored in result dtype)"
  - "assert isinstance(dyn, np.ndarray) at _harmonic_label call site for mypy narrowing (h<N> always produces single array)"
  - "monkeypatch test for defensive ValueError in preset branch (unreachable normally, required for 100% coverage gate)"
  - "test_comma_only_empty_list_rejected covers line 140 (empty list after comma-split with all-blank parts)"

# Metrics
duration: 11min
completed: 2026-06-03
---

# Phase 34 Plan 03: CLI h7 Engine F1 Summary

**`--harmonics h7` wired end-to-end: HarmonicsSelection NamedTuple + h<N> parse branch + Quadrinovile bug fix + harmonic header label; 1617 tests, 100% coverage, mypy --strict clean**

## Performance

- **Duration:** 11 min
- **Started:** 2026-06-03T20:34:47Z
- **Completed:** 2026-06-03T20:45:51Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- `HarmonicsSelection(mask, dynamic_specs)` NamedTuple replaces bare `ndarray` return from `parse_harmonics_spec`; mypy `--strict` clean throughout
- `^h(\d+)$` parse branch inserted after comma, before bare-int trap; range delegated to `generate_harmonic_aspects` (ValueError wrapped as ArgumentTypeError); `h7,h11` and `traditional,h7` rejected by the existing comma/unrecognized branches (Tight grammar)
- Fixed Quadrinovile bug: `print_aspects` now accepts `dynamic_specs=` and uses `_resolve_dynamic_name` to look up `H{h}-{k}` names by recomputing angular separation, bypassing the erroneous `_CORE_ASPECTS['name'][-2]` path
- `cmd_aspects` destructures `HarmonicsSelection`, threads `dynamic_specs=`, emits `# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 103°, H7-3 154°)` via `_harmonic_label` + `emit_resolved_config(dynamic_label=)`
- All 11 previously-broken test assertions updated to `.mask` access; 15 new tests in `TestHarmonicTokenF1` + 3 integration tests + 1 custom-mask test; full suite 1617 passed, 100% coverage on all changed modules

## Task Commits

1. **Task 1: HarmonicsSelection + h<N> branch; print_aspects dynamic_specs** — `e9efc2f` (feat)
2. **Task 2: cmd_aspects destructure + thread dynamic_specs + harmonic header; formatters + parser help** — `74608e1` (feat)
3. **Task 3: Update broken assertions + TestHarmonicTokenF1 + h7 integration tests** — `a466b48` (test)

## Files Created/Modified

- `ketu/cli/harmonics_spec.py` — `HarmonicsSelection` NamedTuple; `_H_TOKEN_RE`; h<N> branch; updated module + function docstrings
- `ketu/display.py` — `print_aspects(dynamic_specs=)`; `_resolve_dynamic_name` helper; imports `_normalize_dynamic_specs`, `long`, `distance`
- `ketu/cli/aspects_cmd.py` — `_harmonic_label()` helper; `cmd_aspects` restructured for `HarmonicsSelection`; `dynamic_specs=` threading
- `ketu/cli/formatters.py` — `emit_resolved_config(dynamic_label=None)` override parameter
- `ketu/cli/parser.py` — `--harmonics` help text extended with `h<N>` form; adjacent comment updated
- `tests/cli/test_harmonics_spec.py` — All 11 existing assertions updated to `.mask`; `dynamic_specs is None` assertions added; `TestHarmonicTokenF1` (13 tests); defensive coverage tests
- `tests/cli/test_parser.py` — `test_top_level_harmonics_present` updated to `HarmonicsSelection` + `.mask` access
- `tests/cli/test_aspects_cmd.py` — `TestAspectsCmdCustomMask` (1 test); `TestAspectsCmdHarmonicsH7` (3 integration tests)

## Decisions Made

- `_resolve_dynamic_name` recomputes the actual angular separation between body IDs at jdate to identify which dynamic spec row was matched (the result dtype stores `dyn_angle - dist`, not `dyn_angle` itself, so the angle cannot be recovered without knowing `dist`)
- `assert isinstance(dyn, np.ndarray)` at the `_harmonic_label` call site narrows the `DynamicAspectSpec` union type for mypy (h<N> always produces a single ndarray from `generate_harmonic_aspects`)
- Defensive `ValueError` branch in the preset path (lines 127-128) covered via `monkeypatch` — unreachable in normal operation but required by the `fail_under=100` gate
- Empty-list branch (line 140: `parse_harmonics_spec(",")`) covered by a new test in `TestInvalidInputs`
- `_preset_label_for_mask` `"custom"` branch (line 68 in `aspects_cmd.py`) covered by `TestAspectsCmdCustomMask` using `--harmonics 0,4`

## Deviations from Plan

None — plan executed exactly as written. All locked decisions honored (Tight grammar, h<N>-only, classical Aspect Timing Example unchanged, byte-stable fixture passes).

## Issues Encountered

- `mypy --strict` flagged `_harmonic_label(dyn)` where `dyn: DynamicAspectSpec` (union type); resolved with `assert isinstance(dyn, np.ndarray)` narrowing — no structural change needed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- HARM-06 and HARM-07 fully satisfied: `--harmonics h7` accepted end-to-end; `HarmonicsSelection` NamedTuple stable; Tight grammar tested; Quadrinovile bug fixed
- Plan 34-04 (byte-stability fixture + docs en+fr) can proceed: the CLI is functional and the `H{h}-{k}` name output is pinnable
- No blockers

---
*Phase: 34-harmonics-debt*
*Completed: 2026-06-03*
