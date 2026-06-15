---
phase: 38-fictitious-point-orbs-engine
plan: "01"
subsystem: ketu/aspects
tags: [orb, fictitious-points, rahu, ketu, lilith, tautological-filter, tdd]
dependency_graph:
  requires: []
  provides:
    - "ketu/core.py::bodies[orb] rows id=10,11,12 set to 2° (ORB-01)"
    - "ketu/aspects/calculator.py::_is_tautological_node_opposition (ORB-02)"
    - "tests/aspects/test_node_opposition_filter.py — 12 tests (6 unit + 6 integration/keep)"
  affects:
    - "ketu/synastry/orbs.py::_BODY_ORBS_16 (data-driven, inherits automatically)"
    - "get_orb / calculate_aspects_vectorized / calculate_aspects_batch / calculate_aspects / get_aspect"
tech_stack:
  added: []
  patterns:
    - "pure helper modelled on get_orb (single-source, order-insensitive)"
    - "matched_pairs suppression: suppress emit but still mark pair consumed (first-match-wins preserved)"
key_files:
  created:
    - "tests/aspects/__init__.py"
    - "tests/aspects/test_node_opposition_filter.py"
  modified:
    - "ketu/core.py (3 rows: Rahu/Ketu/Lilith orb 0→2)"
    - "ketu/aspects/calculator.py (_RAHU_ID/_KETU_ID/_OPPOSITION_IASP constants + _is_tautological_node_opposition helper + 5 call sites)"
decisions:
  - "matched_pairs placement (Task 3 Site 1): suppress emit but still add pair to matched_pairs — opposition is i_asp=13, the last static row, so no other static aspect competes; the slot is consumed regardless to preserve first-match-wins invariant"
  - "calculate_aspects conjunction guard (Site 4a): guard present for D-01 uniformity even though i_asp=0 never matches _OPPOSITION_IASP=13; the helper short-circuits instantly (False) with zero runtime cost"
  - "type annotations on module constants: untyped (no ': int') to match plan acceptance grep '_OPPOSITION_IASP = 13'; mypy --strict infers the type correctly"
metrics:
  duration: "~25 minutes"
  completed: "2026-06-15"
  tasks_completed: 3
  files_changed: 4
---

# Phase 38 Plan 01: ORB-01 + ORB-02 — Fictitious-Point Orbs Engine Core Summary

**One-liner:** Single-source orb 0→2° for Rahu/Ketu/Lilith in `core.bodies` + shared `_is_tautological_node_opposition` helper wired into all four public natal/scalar emit paths.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | ORB-01: flip Rahu/Ketu/Lilith orb 0→2 in core.bodies | f45a7b2 | ketu/core.py |
| 2 | ORB-02: define helper + unit tests (RED→GREEN) | c01c250 | ketu/aspects/calculator.py, tests/aspects/__init__.py, tests/aspects/test_node_opposition_filter.py |
| 3 | ORB-02: wire helper into all natal/scalar emit paths | 38b3cf2 | ketu/aspects/calculator.py |

## What Was Built

### ORB-01: Single-source orb change (ketu/core.py)

Changed the `orb` field (3rd tuple position) from `0` to `2` for three rows in the `bodies` structured array:

```python
("Rahu",   10, 2, -0.052954)  # was 0
("Ketu",   11, 2, -0.052954)  # was 0
("Lilith", 12, 2,  0.113)     # was 0
```

All downstream consumers (get_orb, synastry._BODY_ORBS_16, cycles, composite, CLI) read `bodies["orb"]` data-driven and inherit the change with zero further edits. Chiron (id=13, orb=4) and all planet rows are unchanged.

Verified: `get_orb(10,10,0)==2.0`, `get_orb(10,0,0)==7.0` (Rahu↔Sun = (2+12)/2), `get_orb(13,13,0)==4.0` (Chiron unchanged), `get_orb(0,0,0)==12.0` (Sun unchanged).

### ORB-02: Shared helper + call sites (ketu/aspects/calculator.py)

Three module-level constants:
```python
_RAHU_ID = 10
_KETU_ID = 11
_OPPOSITION_IASP = 13  # Canonical index into core.aspects (last row)
```

One private pure helper:
```python
def _is_tautological_node_opposition(body1: int, body2: int, i_asp: int) -> bool:
```

Order-insensitive (Rahu/Ketu pair matched in either order), np.int32 args coerced via `int()`, dynamic rows (i_asp=-2) exempt.

**Call sites (5 total):**

1. `_detect_aspects_for_date` static emit loop — suppress `results.append`; pair STILL added to `matched_pairs`
2. `_detect_aspects_for_date` dynamic emit loop — guard for D-01 uniformity; always returns False (structurally exempt)
3. `get_aspect` — `return None` when helper is True (after body1>body2 swap)
4a. `calculate_aspects` conjunction branch — guard for uniformity; i_asp=0 never triggers
4b. `calculate_aspects` opposition branch — suppress `aspects_data.append` when helper is True

### Tests (tests/aspects/test_node_opposition_filter.py)

12 tests total:

**Helper unit tests (6):**
- `test_canonical_rahu_ketu_opposition_is_true` — (10,11,13) → True
- `test_swapped_ketu_rahu_opposition_is_true` — (11,10,13) → True (order-insensitive)
- `test_rahu_ketu_conjunction_is_false` — (10,11,0) → False (conjunction still emits)
- `test_rahu_sun_opposition_is_false` — (10,0,13) → False (Rahu↔Sun still emits)
- `test_dynamic_row_exempt` — (10,11,-2) → False (dynamic rows exempt)
- `test_numpy_int32_coercion` — (np.int32(10), np.int32(11), 13) → True

**Integration tests (6):**
- `test_vectorized_drops_rahu_ketu_opposition` — vectorized path: no (10,11,13) row at JD=2451545.0
- `test_batch_drops_rahu_ketu_opposition` — batch path: same
- `test_calculate_aspects_drops_rahu_ketu_opposition` — slow path: same
- `test_get_aspect_returns_none_for_rahu_ketu_opposition` — scalar path: returns None (or non-opposition)
- `test_rahu_ketu_conjunction_keep_branch` — helper returns False for (10,11,0) (verified at unit level)
- `test_rahu_sun_opposition_keep_branch_vectorized` — scans 365 days from J2000; first hit at JD=2451562.0 (~2000-01-18, sep=173.47°) confirms Rahu↔Sun opposition detected normally

**Julian date used for primary integration tests:** JD=2451545.0 (J2000.0 — 2000-01-01 12:00 TT). Rahu and Ketu are always ~180° apart by astronomical definition.

**Julian date for Rahu↔Sun opposition keep-branch:** JD=2451562.0 (~2000-01-18, separation=173.47° within the 7° orb).

## matched_pairs Placement Decision (Task 3 Site 1)

In the `_detect_aspects_for_date` static emit loop, when the tautological Rahu↔Ketu Opposition is detected:
- The `results.append(...)` is **skipped** (suppressed)
- The pair is **still added** to `matched_pairs`

**Rationale:** The Opposition aspect is i_asp=13 (the last static row). No other static aspect occupies a higher i_asp that could "fill the slot" after suppression — the first-match-wins contract is already terminal for this pair on this aspect. Adding to `matched_pairs` regardless ensures the dynamic-aspects loop also doesn't re-emit for this pair. This is the safest and most conservative placement; it mirrors what `get_aspect` does (returns None — slot consumed, no fallback).

## Deviations from Plan

**None** — plan executed exactly as written.

The only structural decision was the `matched_pairs` placement (documented in the SUMMARY per the `<output>` requirement in the plan), which was pre-flagged in the plan as requiring a documented decision.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. The changes are:
- A data-only edit (3 integer fields in a frozen NumPy array)
- A pure function addition with no I/O
- Call-site guards (conditional skips)

All three STRIDE threats (T-38-01, T-38-02, T-38-03) from the plan's threat model are mitigated by the unit and integration tests. Threat flags: none.

## Known Stubs

None — all functionality is fully implemented and tested. No placeholder text, empty stubs, or missing data sources.

## Self-Check: PASSED

- `ketu/core.py` exists and contains `("Rahu", 10, 2,`: FOUND
- `ketu/aspects/calculator.py` contains `_is_tautological_node_opposition`: FOUND (6 occurrences)
- `tests/aspects/test_node_opposition_filter.py` exists: FOUND
- Commits f45a7b2, c01c250, 38b3cf2: FOUND in git log
