---
phase: 11-cli-refactor-integration
verified: 2026-05-07T20:40:00Z
status: passed
score: 6/6 must-haves verified
gaps: []
human_verification:
  - test: "Run ketu --harmonics classical aspects --date <date> and compare output rows against ketu --harmonics extended aspects"
    expected: "classical emits only the 5 major aspects; extended emits all 14"
    why_human: "Automated tests confirm counts differ; visual confirmation of correct subset semantics is faster with human eyes"
---

# Phase 11: CLI Refactor Integration Verification Report

**Phase Goal:** User invokes `ketu` via argparse subcommands, opts into harmonics through `--harmonics SPEC`, computes houses through `ketu houses ...`, and sees the resolved configuration echoed in output — backward compat preserved via `--harmonics all`.

**Verified:** 2026-05-07T20:40:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | `ketu --help` shows argparse subcommands; no `input()` prompt anywhere | VERIFIED | `python -m ketu --help` shows `{aspects,houses}` subparser tree; `grep -rn "input(" ketu/` returns nothing |
| 2  | Each subcommand has its own `--help` | VERIFIED | `ketu aspects --help` and `ketu houses --help` both show their own usage + options |
| 3  | `--harmonics classical/traditional/extended/all` accepted; bare int `--harmonics 12` rejected with clear error pointing to named presets | VERIFIED | Bare int produces `error: argument --harmonics: bare integer '12' is ambiguous … use a named preset (all, classical, extended, traditional)` with exit 2 |
| 4  | `ketu houses --date ... --lat ... --lon ... --system placidus` cusps match Python API | VERIFIED | API `calculate_houses` returns `148.5921°` for House 1; CLI prints `148.5921°`; values match |
| 5  | `ketu --list-aspect-sets` and `ketu --list-house-systems` produce human-readable output with descriptions | VERIFIED | Both commands produce named presets/systems with angle lists and descriptions to stdout |
| 6  | Every CLI invocation emits a resolved-config header on stderr (not stdout); `--harmonics all` stdout is byte-identical to v1.1 pinned fixture | VERIFIED | `ketu aspects 2>/dev/null` shows no `#` lines in stdout; stderr contains `# Ketu v1.1.0` + `# Aspect set: …`; `test_harmonics_all_byte_identical_to_v1_1_reference` passes; `ketu houses` stderr contains `# House system: placidus` |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/cli/parser.py` | argparse tree + `main()` dispatch | VERIFIED | 186 lines; `build_parser()` + `main()`; imports real dispatchers; no stubs |
| `ketu/cli/harmonics_spec.py` | `parse_harmonics_spec` type validator | VERIFIED | 118 lines; handles presets, comma-lists, rejects bare ints with clear error |
| `ketu/cli/aspects_cmd.py` | `cmd_aspects(args)` dispatcher | VERIFIED | 113 lines; calls `print_positions` + `print_aspects(jd, aspects=mask)` + Aspect Timing Example block |
| `ketu/cli/formatters.py` | `emit_resolved_config` to stderr | VERIFIED | 55 lines; emits `# Ketu v1.1.0`, `# Aspect set: …`, `# House system: …` to `sys.stderr` |
| `ketu/cli/introspection.py` | `cmd_list_aspect_sets` + `cmd_list_house_systems` | VERIFIED | 57 lines; iterates all presets and systems with descriptions |
| `ketu/cli/houses_cmd.py` | `cmd_houses` + `emit_resolved_config` call | VERIFIED | 84 lines; calls `emit_resolved_config(mask=None, preset_name=None, house_system=args.system)` |
| `ketu/display.py` | `print_aspects` accepts `aspects=` kwarg | VERIFIED | Forwards to `calculate_aspects(jdate, aspects=aspects)`; U+00BA `º` format preserved |
| `ketu/__main__.py` | Routes to `ketu.cli:main`; no legacy `display.main()` | VERIFIED | 9 lines; `from ketu.cli import main; raise SystemExit(main())`; `display.main` confirmed deleted |
| `pyproject.toml` | Entry point `ketu = "ketu.cli:main"` | VERIFIED | Line 54: `ketu = "ketu.cli:main"` |
| `tests/cli/fixtures/v1_1_reference_output.txt` | Pinned v1.1 stdout (2125 bytes, 52 lines) | VERIFIED | 2125 bytes; 52 lines; 41× U+00BA; 0× U+00B0 |
| `tests/cli/test_v1_1_reference_byte_stable.py` | 5-test subprocess regression | VERIFIED | 214 lines; all 5 tests pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/cli/parser.py` | `ketu/cli/aspects_cmd.py` | `from .aspects_cmd import cmd_aspects` | WIRED | Import confirmed; `p_aspects.set_defaults(func=cmd_aspects)` |
| `ketu/cli/parser.py` | `ketu/cli/houses_cmd.py` | `from .houses_cmd import cmd_houses` | WIRED | Import confirmed; `p_houses.set_defaults(func=cmd_houses)` |
| `ketu/cli/parser.py` | `ketu/cli/harmonics_spec.py` | `type=parse_harmonics_spec` | WIRED | Wired as argparse `type=` validator on `--harmonics` flag |
| `ketu/cli/aspects_cmd.py` | `ketu/display.py:print_aspects` | `print_aspects(jd, aspects=mask)` | WIRED | Confirmed in `aspects_cmd.py` line 99 |
| `ketu/display.py:print_aspects` | `ketu/aspects.calculate_aspects` | `calculate_aspects(jdate, aspects=aspects)` | WIRED | Forwarded kwarg at `display.py` line 72 |
| `ketu/cli/aspects_cmd.py` | `ketu/cli/formatters.py` | `emit_resolved_config(mask, preset_label, house_system=None)` | WIRED | Called before `print_positions`; goes to `sys.stderr` |
| `ketu/cli/houses_cmd.py` | `ketu/cli/formatters.py` | `emit_resolved_config(mask=None, preset_name=None, house_system=args.system)` | WIRED | First call in `cmd_houses`; BLOCKER 2 fix confirmed |
| `ketu/cli/parser.py` | `ketu/cli/introspection.py` | `cmd_list_aspect_sets()` / `cmd_list_house_systems()` | WIRED | Imported and called in `main()` introspection short-circuit |
| `tests/cli/test_v1_1_reference_byte_stable.py` | `tests/cli/fixtures/v1_1_reference_output.txt` | `FIXTURE.read_bytes()` then `assert result.stdout == expected` | WIRED | Confirmed at test lines 102 and 118 |
| `ketu/__main__.py` | `ketu/cli:main` | `from ketu.cli import main; raise SystemExit(main())` | WIRED | Confirmed |
| `pyproject.toml` entry point | `ketu/cli:main` | `ketu = "ketu.cli:main"` | WIRED | Line 54 confirmed |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| CLI-01: no interactive `input()` prompt | SATISFIED | `grep -rn "input(" ketu/` returns empty; `display.main()` deleted in Plan 11-05 |
| CLI-02: `--harmonics SPEC` validator; bare-int rejection | SATISFIED | `harmonics_spec.py` rejects bare ints with named-preset hint; comma-lists and presets accepted |
| CLI-03: byte-stable regression (pivoted to forward contract) | SATISFIED | Option A pivot: v1.1 fixture pinned; 5-test subprocess regression passes; documented in test docstring |
| CLI-04: `ketu houses` matches Python API | SATISFIED | House 1 = 148.5921° from both API and CLI for same inputs |
| CLI-05: `--list-aspect-sets`, `--list-house-systems` with descriptions | SATISFIED | Both commands produce named options with angles/descriptions to stdout |
| CLI-06: resolved-config header on stderr from BOTH `cmd_aspects` AND `cmd_houses` | SATISFIED | `aspects` emits `# Ketu v1.1.0` + `# Aspect set: …`; `houses` emits `# Ketu v1.1.0` + `# House system: …` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ketu/cli/parser.py` | 32 | Comment references "stubs in Plan 11-01" (historical documentation, not a live stub) | Info | None — describes the evolution arc in the docstring; the actual dispatchers at `set_defaults()` calls use real functions |

No blocking anti-patterns found. The single note is historical documentation in a docstring, not an empty implementation.

### Human Verification Required

#### 1. Aspect subset correctness

**Test:** Run `ketu --harmonics classical aspects --date 2026-05-06T12:00:00Z` then `ketu --harmonics extended aspects --date 2026-05-06T12:00:00Z` and compare the aspects rows.
**Expected:** Classical shows only 5-aspect types (Conjunction, Sextile, Square, Trine, Opposition); extended shows all 14 including Decile, Novile, etc.
**Why human:** Automated tests confirm row counts differ and masks are correct; human scan of the actual named aspects in both outputs gives fastest confidence that the right filter is applied semantically.

### Gaps Summary

No gaps. All six CLI requirements are implemented and verified against the actual codebase.

---

_Verified: 2026-05-07T20:40:00Z_
_Verifier: Claude (gsd-verifier)_
