---
phase: 38-fictitious-point-orbs-engine
verified: 2026-06-15T19:47:18Z
status: passed
score: 4/4
overrides_applied: 0
---

# Phase 38: Fictitious-Point Orbs Engine — Verification Report

**Phase Goal:** Rahu, Ketu, and Lilith participate in aspect detection with a 2° orb, the tautological Rahu↔Ketu Opposition is suppressed, and the full test suite is green against the new oracles.
**Verified:** 2026-06-15T19:47:18Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `get_orb` for Rahu/Ketu/Lilith returns 2.0°; Rahu↔Sun returns 7.0°; Rahu↔Lilith returns 2.0° | VERIFIED | `python -c "…"` printed `ORB-01 OK`; `ketu/core.py` lines 81-83 confirmed `orb=2` for ids 10/11/12 |
| 2 | Aspect engine never emits (Rahu, Ketu) + Opposition; all other Rahu/Ketu/Lilith aspects detected normally | VERIFIED | `grep` counts 6 call sites in `calculator.py`; all four emit paths guarded; synastry has zero calls to filter; 12 dedicated tests pass |
| 3 | `test_orbs.py` and `test_modes_idempotent.py` pass with oracles rewritten to 2° orb; no silent update | VERIFIED | Three functions renamed `*_zero_orb` → `*_two_degree_orb`; assertions flipped `0.0 → 1.0`; idempotent invariants (`aspect_type==0`, `|orb|<1e-6`) unchanged; both files green |
| 4 | All test files referencing Rahu/Ketu/Lilith green; `pytest tests/` 0 failures, 100% coverage, `mypy --strict ketu/` clean | VERIFIED | `pytest tests/` → 1666 passed, 2 skipped, 100% coverage; `mypy --strict ketu/` → "Success: no issues found in 72 source files" |

**Score:** 4/4 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/core.py` | Rahu/Ketu/Lilith orb field = 2 in `bodies` rows id 10/11/12 | VERIFIED | Lines 81-83: `("Rahu", 10, 2, …)`, `("Ketu", 11, 2, …)`, `("Lilith", 12, 2, …)`; Chiron (id 13) remains orb=4 |
| `ketu/aspects/calculator.py` | `_is_tautological_node_opposition` + 3 constants + 5+ call sites | VERIFIED | `_RAHU_ID=10`, `_KETU_ID=11`, `_OPPOSITION_IASP=13` at lines 67-69; helper at line 72; 6 occurrences total (1 definition + 5 call sites) |
| `tests/aspects/test_node_opposition_filter.py` | 6 helper unit tests + 6 integration tests | VERIFIED | 12 tests covering all branches: suppress, order-insensitivity, conjunction keep, non-node-opposition keep, dynamic exempt, np.int32 coercion |
| `tests/synastry/test_orbs.py` | Rewritten oracles 0.0→1.0 for Rahu/Ketu/Lilith self-pairs | VERIFIED | Three functions renamed `*_two_degree_orb`; assertions confirm `synastry_orb_limit(10,10,0)==1.0`, `(11,11,0)==1.0`, `(12,12,0)==1.0` |
| `tests/synastry/test_modes_idempotent.py` | Stale docstring refreshed; assertions unchanged | VERIFIED | Module/test docstrings updated to reflect 2° orb; `aspect_type==0` and `|orb|<1e-6` invariants intact |
| `tests/cli/fixtures/v1_1_reference_output.txt` | Two new Rahu aspect lines added | VERIFIED | Lines `Sun - Rahu: Quincunx -6°45'18"` and `Venus - Rahu: Trine 3°33'33"` present; no Rahu↔Ketu Opposition appears |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/aspects/calculator.py::_detect_aspects_for_date` (static loop) | `_is_tautological_node_opposition` | Guard on `results.append`; pair still added to `matched_pairs` | WIRED | Lines 174-178: filter called before append; Opposition slot consumed |
| `ketu/aspects/calculator.py::_detect_aspects_for_date` (dynamic loop) | `_is_tautological_node_opposition` | Guard for D-01 uniformity; `i_asp=-2` always returns False | WIRED | Lines 190-193: guard present; dynamic rows structurally exempt |
| `ketu/aspects/calculator.py::get_aspect` | `_is_tautological_node_opposition` | `return None` when True (after body1>body2 swap) | WIRED | Lines 250-251: canonical order enforced by prior swap; helper returns None for Rahu↔Ketu Opposition |
| `ketu/aspects/calculator.py::calculate_aspects` | `_is_tautological_node_opposition` | Guards conjunction branch (line 345) and opposition branch (line 352) | WIRED | Both static emit branches guarded; conjunction guard is i_asp=0, never triggers; opposition guard suppresses append |
| `ketu/core.py::bodies['orb']` | `synastry._BODY_ORBS_16` | `_build_body_orbs_16()` reads `_BODIES["orb"]` at import time | WIRED | `ketu/synastry/orbs.py` lines 71-76: `np.concatenate([_BODIES["orb"].astype(np.float32), …])`; frozen at import |
| Synastry paths | `_is_tautological_node_opposition` | NOT called (D-05 decision: synastry is not filtered) | VERIFIED ABSENT | `grep -rn "_is_tautological_node_opposition" ketu/` excluding `calculator.py` returned no output |

---

## Data-Flow Trace (Level 4)

Not applicable — this phase produces pure-function library code with no dynamic data rendering. The "data flow" is deterministic numeric computation from Julian dates → aspect rows, verified by the integration tests.

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| ORB-01: get_orb returns correct values for all bodies | `python -c "from ketu.aspects.calculator import get_orb; assert …; print('ORB-01 OK')"` | `ORB-01 OK` | PASS |
| ORB-02: helper branches correct | `python -c "from ketu.aspects.calculator import _is_tautological_node_opposition as f; …; print('helper OK')"` | `helper OK` | PASS |
| ORB-02/03: all 12 dedicated tests | `pytest tests/aspects/test_node_opposition_filter.py -q` | `12 passed` | PASS |
| ORB-03: full suite green + 100% coverage | `pytest tests/ -q` | `1666 passed, 2 skipped, 100% coverage` | PASS |
| Type safety: ketu package | `mypy --strict ketu/` | `Success: no issues found in 72 source files` | PASS |
| CLI snapshot contains new Rahu detections | `grep "Sun.*Rahu.*Quincunx\|Venus.*Rahu.*Trine" tests/cli/fixtures/v1_1_reference_output.txt` | 2 matches | PASS |
| CLI snapshot contains no Rahu↔Ketu Opposition | `grep "Rahu.*Ketu.*Opposition\|Ketu.*Rahu.*Opposition" tests/cli/fixtures/v1_1_reference_output.txt` | no output | PASS |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ORB-01 | 38-01 | Rahu/Ketu/Lilith orb 0°→2° single-source edit in `ketu/core.py` | SATISFIED | `core.py` lines 81-83; `get_orb` spot-check passes |
| ORB-02 | 38-01 | Shared `_is_tautological_node_opposition` helper wired into all natal/scalar emit paths, NOT synastry | SATISFIED | Helper at `calculator.py:72`; 5 call sites in calculator; zero in synastry |
| ORB-03 | 38-02 | Full test suite green against new 2° orb and filter; every changed oracle deliberately re-pinned | SATISFIED | 1666 passed, 100% coverage; per-delta register in 38-02-SUMMARY.md documents all 5 oracle changes |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | None found | — | No debt markers, no stubs, no empty implementations in any modified file |

Scan covered: `ketu/core.py`, `ketu/aspects/calculator.py`, `tests/aspects/test_node_opposition_filter.py`, `tests/synastry/test_orbs.py`, `tests/synastry/test_modes_idempotent.py`, `tests/cli/fixtures/v1_1_reference_output.txt`.

---

## Note on mypy --strict ketu/ tests/

Running `mypy --strict ketu/ tests/` (including the test tree) reports 225 errors in 41 test files. These are pre-existing errors from earlier phases — confirmed identical before and after this phase's changes. They reside in `tests/parts/`, `tests/cli/`, `tests/composite/`, and are suppressed by `pyproject.toml` overrides for the `tests.*` namespace. The phase success criterion is `mypy --strict ketu/` (source package only), which is clean. This is a known baseline deviation, not introduced by phase 38.

---

## Human Verification Required

None. All success criteria are verifiable programmatically. No visual UI, real-time behavior, or external service integration involved.

---

## Gaps Summary

No gaps. All four ROADMAP success criteria are met with direct codebase evidence:

1. **ORB-01** — Single-source orb change confirmed in `core.py` at the byte level; `get_orb` returns exactly the values the plan requires.
2. **ORB-02** — Helper exists, is pure, is private (absent from `__all__`), is order-insensitive, coerces `np.int32`, and is wired into exactly the four logical call sites the plan specifies. Synastry is confirmed clean.
3. **ORB-03** — Synastry oracle rewrites are deliberate (functions renamed, docstrings corrected, rationale documented). Idempotent diagonal invariants are unchanged. CLI fixture carries exactly two new Rahu detections with documented reasons.
4. **Full gates** — 1666 tests pass, 100% coverage maintained, `mypy --strict ketu/` clean.

---

_Verified: 2026-06-15T19:47:18Z_
_Verifier: Claude (gsd-verifier)_
