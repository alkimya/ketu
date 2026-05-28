---
phase: 19-arabic-parts-framework
verified: 2026-05-28T19:47:19Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 19: Arabic Parts Framework — Verification Report

**Phase Goal:** Users compute Part of Fortune, Part of Spirit, and Part of Marriage by name from any chart, with sect-aware day/night formula selection (Fortune/Spirit) and an extensible registry analogous to `SYSTEMS` — built so the remaining Hermetic Lots can be added in v1.3 without API change.
**Verified:** 2026-05-28T19:47:19Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `from ketu.parts import PARTS, calculate_part, calculate_all_parts` resolves; `PARTS` lists exactly 3 parts; registry is extensible without API change | VERIFIED | Import succeeds; `sorted(PARTS.keys()) == ['fortune', 'marriage', 'spirit']`; adding a 4th part via `register()` + `calculate_part()` works with no dispatch change; cleanup restores 3 |
| 2 | `calculate_part("fortune", chart)` reads `is_day_chart` and applies sect-correct formula; returns longitude in `[0, 360)` | VERIFIED | Fortune day `(ASC+Moon-Sun)%360 = 329.218608`, night `(ASC+Sun-Moon)%360 = 252.071415` — both match to `< 1e-9`; Spirit mirrors confirmed; Marriage `(2*ASC+180-Venus)%360` confirmed both sect |
| 3 | `calculate_all_parts(chart)` returns `dict[str, float]` for all 3; `parts=[...]` filters correctly | VERIFIED | Default returns `{'fortune', 'marriage', 'spirit'}`; `parts=['fortune']` returns `{'fortune'}`; all values in `[0, 360)` |
| 4 | `ketu --list-parts` prints all 3 names plus formula summary line; Marriage line notes "fixed" | VERIFIED | CLI output confirmed: fortune/spirit with sect description, marriage with "fixed - no sect inversion"; trailing note "fixed formula - day and night formulas are identical" |
| 5 | Coverage on `ketu/parts/` is ≥95%; Fortune+Spirit pinned day+night oracle; Marriage pinned once+ sect-invariant | VERIFIED | `make parts-coverage` passes: `ketu/parts/__init__.py` 100%, `api.py` 100%, `registry.py` 100% — TOTAL 100%; 8 oracle tests pass (Fortune day+night, Spirit day+night, Marriage day+night, mirror-differ day+night) |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/parts/__init__.py` | Public re-export + 3 `register()` calls | VERIFIED | 68 lines; exports `PARTS, PartSpec, calculate_all_parts, calculate_part, get_part, register`; registers fortune/spirit/marriage at import time |
| `ketu/parts/registry.py` | `PARTS` dict, `PartSpec` frozen dataclass, `register()`, `get_part()` | VERIFIED | 167 lines; `PartSpec(frozen=True)` with `name/day_formula/night_formula/description`; `PARTS: dict[str, PartSpec]`; both functions fully implemented |
| `ketu/parts/api.py` | `calculate_part()` + `calculate_all_parts()` with sect dispatch | VERIFIED | 148 lines; `calculate_part` calls `is_day_chart()` fresh (D-12 compliant), selects `spec.day_formula if is_day else spec.night_formula`; body indices frozen per D-08 (0=Sun, 1=Moon, 3=Venus) |
| `ketu/cli/introspection.py` | `cmd_list_parts()` | VERIFIED | Lines 129-145; imports `PARTS` from `ketu.parts`; iterates `sorted(_PARTS.keys())`; prints formula descriptions; trailing Marriage note |
| `ketu/cli/parser.py` | `--list-parts` flag wired to `cmd_list_parts` | VERIFIED | Lines 75-78 add `--list-parts`; line 305-307 dispatch `cmd_list_parts()` and return 0 |
| `tests/parts/test_parts_oracle.py` | 6 oracle tests (Fortune day+night, Spirit day+night, Marriage day+night) | VERIFIED | 8 oracle tests (6 direct + 2 mirror-differ guards); sect asserted at module level via `assert bool(is_day_chart(...)) is True/False`; `_TOL = 1e-9` |
| `tests/parts/test_parts_registry.py` | Registry tests (extensibility, filter, ValueError, Marriage identity) | VERIFIED | 13 tests covering exactly-3 constraint, case-insensitive lookup, ValueError with sorted available, extensibility round-trip, `calculate_all_parts` filter, `day_formula is night_formula` for Marriage |
| `tests/parts/test_parts_cli.py` | CLI tests for `--list-parts` | VERIFIED | 9 tests; all 3 names present, "fixed" in output, exit code 0, direct `cmd_list_parts()` call |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/parts/__init__.py` | `ketu/parts/api.py` | `from .api import calculate_all_parts, calculate_part` | WIRED | Line 25 |
| `ketu/parts/__init__.py` | `ketu/parts/registry.py` | `from .registry import PARTS, PartSpec, get_part, register` | WIRED | Line 26 |
| `ketu/parts/api.py` | `ketu.charts.api.is_day_chart` | direct call `is_day_chart(float(chart["jd"]), ...)` | WIRED | Line 84; result `bool()`-unwrapped per D-12 |
| `ketu/parts/api.py` | `ketu/parts/registry.py` | `from .registry import PARTS, get_part` | WIRED | Lines 23-24 |
| `ketu/cli/introspection.py` | `ketu/parts` | `from ketu.parts import PARTS as _PARTS` | WIRED | Line 13 |
| `ketu/cli/parser.py` | `ketu/cli/introspection.py` | `from .introspection import cmd_list_parts` | WIRED | Line 26; dispatched at line 305-307 |
| Marriage `night_formula` | Marriage `day_formula` | same callable object (`is` identity) | WIRED | `_marriage_formula` assigned once, passed as both `day_formula` and `night_formula`; `spec.day_formula is spec.night_formula` confirmed True |

---

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| PARTS-01: extensible registry, `register()` adds Lots without dispatch change | SATISFIED | `register()` adds to `PARTS` dict; `calculate_part` delegates to registry; test proves 4th lot works without touching `api.py` |
| PARTS-02: `get_part` raises `ValueError` with available list | SATISFIED | `get_part('nope')` → `ValueError: unknown part 'nope'; available: ['fortune', 'marriage', 'spirit']` |
| PARTS-03/04: sect-aware dispatch, no if/elif ladder | SATISFIED | `spec.day_formula if is_day else spec.night_formula` — registry IS dispatch |
| PARTS-05: Fortune formula correctness | SATISFIED | day `(ASC+Moon-Sun)%360`, night `(ASC+Sun-Moon)%360`, oracle-pinned |
| PARTS-06: Spirit formula correctness | SATISFIED | day `(ASC+Sun-Moon)%360`, night `(ASC+Moon-Sun)%360`, oracle-pinned |
| PARTS-07: Marriage sect-invariant, `day_formula is night_formula` | SATISFIED | `_marriage_formula` object assigned to both fields; callable identity asserted by test |
| PARTS-08: `--list-parts` CLI flag | SATISFIED | Flag registered, dispatched, output contains 3 names + formula lines + Marriage "fixed" note |

---

### Anti-Patterns Found

None. No TODOs, FIXMEs, placeholders, empty implementations, or stub returns found in `ketu/parts/`.

---

### Human Verification Required

None. All success criteria are programmatically verifiable (formulas, registry, CLI output text). No visual layout, real-time behavior, or external service involved.

---

## Summary

Phase 19 goal is fully achieved. All three Arabic Parts (Fortune, Spirit, Marriage) are implemented with correct sect-aware formulas, registered in an extensible `PARTS` dict analogous to `SYSTEMS`, exposed via the public API `from ketu.parts import PARTS, calculate_part, calculate_all_parts`, and surfaced in the CLI via `ketu --list-parts`. Coverage on `ketu/parts/` is 100% (gate requires ≥95%). All 31 parts tests pass. The full test suite (1284 tests) passes with 98.35% project-wide coverage. No regressions introduced.

---

_Verified: 2026-05-28T19:47:19Z_
_Verifier: Claude (gsd-verifier)_
