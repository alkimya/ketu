---
phase: 33-lunar-declination
verified: 2026-06-03T20:20:05Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 33: Lunar Declination δ Verification Report

**Phase Goal:** A user can compute any body's equatorial declination δ (scalar and vectorized over date arrays), its rate of change, the Moon's biodynamic montant/descendant trajectory, and out-of-bounds state — and every computed chart (and the relational/predictive charts that inherit from it) carries declination in a new `body_decl` field, with the feature documented en + fr. All additive: `is_ascending` (ecliptic latitude β) stays byte-for-byte UNCHANGED.

**Verified:** 2026-06-03T20:20:05Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `declination(jdate, body)` works scalar and vectorized for all 14 bodies, range [−90,+90], pinned against coordinates chain (DECL-01, DECL-02, DECL-03) | VERIFIED | `ketu/calculations.py:448-500` — scalar path via `long`/`lat` + chain, array path via `calc_planet_position_batch`; `tests/test_declination.py` covers all 14 bodies; `tests/test_coordinates_coverage.py:698` (DECL-03) cross-checks against explicit chain and Meeus 13.4 to < 1e-9° over 50 dates |
| 2 | `declination_velocity` gives dδ/dt (°/day, forward FD, no wraparound) and `is_ascending_declination` returns True iff dδ/dt > 0 — parallel to, and distinct from, β-based `is_ascending` (DECL-04, DECL-05) | VERIFIED | `ketu/calculations.py:503-563`; `tests/test_declination.py` TestDeclinationVelocity + TestIsAscendingDeclination; `test_distinct_from_beta_is_ascending_at_jd_asc` explicitly proves the two disagree at JD=2460742.0 |
| 3 | `is_out_of_bounds(jdate, body)` returns True when |δ| > ε(jd) using instantaneous `true_obliquity` (DECL-06) | VERIFIED | `ketu/calculations.py:566-594`; `tests/test_declination.py` TestIsOutOfBounds covers in-bounds and OOB Moon cases; OOB Moon at JD_OOB=2460676.5 (|δ|≈25.88° > ε≈23.44°) |
| 4 | Every chart from `compute_chart` carries `body_decl` (14 bodies, f8) populated from ecliptic positions; `calculate_composite` derives it (not zero-fill); Returns inherit it for free; ratchet guards the field (DECL-07, DECL-08) | VERIFIED | `ketu/charts/core.py:103` — field in CHART_DTYPE; `ketu/charts/api.py:394` — `out["body_decl"] = decl`; `ketu/composite/api.py:252-266` — derived from composite λ,β (not zero-fill); `tests/returns/test_lunar_return.py:449,478` — non-zero assertion + machine-precision cross-check vs `declination()` array path; `tests/charts/test_dtype.py:44-83` — DECL-08 ratchet pins field name, shape (14,), f8 kind/itemsize, vectorized and 0-d construction |
| 5 | Feature documented EN + FR: four public functions, aspect-centric montant/descendant framing (draconic month ~27.21 d, OOB nodal cycle), explicit β-vs-δ distinction (DECL-09) | VERIFIED | `docs/source/api.md` — four functions with signatures, examples, β-vs-δ table; `docs/source/concepts.md` — draconic month, OOB/standstill, montant/descendant biodynamic framing, body_decl field section; `docs/source/changelog.md` — v1.5 declination entry; FR `.po` files: `api.po`, `concepts.po`, `changelog.po` all translated; `.mo` files compiled (2026-06-03 22:08, more recent than `.po`) |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/calculations.py` | Four declination functions + `__all__` | VERIFIED | `declination`, `declination_velocity`, `is_ascending_declination`, `is_out_of_bounds` all present at lines 448-594; all four in `__all__` (lines 682-685) |
| `ketu/charts/core.py` | `body_decl` field in CHART_DTYPE | VERIFIED | Line 103: `("body_decl", "f8", (14,))` after `body_speeds`, before `cusps`; `#:` doc block updated |
| `ketu/charts/api.py` | `compute_chart` populates `out["body_decl"]` | VERIFIED | Lines 379-394: vectorized derivation from already-fetched body_lons/body_lats + eps broadcast |
| `ketu/composite/api.py` | `calculate_composite` derives `body_decl` (not zero-fill) | VERIFIED | Lines 252-266: derives from composite λ,β via coordinates chain; explicitly assigned |
| `tests/test_declination.py` | DECL-01/02/04/05/06 tests | VERIFIED | 302 lines; covers all 14 bodies; velocity, ascending-declination, OOB; β-vs-δ independence |
| `tests/test_coordinates_coverage.py` | DECL-03 regression vs chain + Meeus | VERIFIED | `TestDeclinationEquivalenceDECL03` (line 698); 50 dates, tolerance < 1e-9°, both Sun and Moon |
| `tests/charts/test_dtype.py` | DECL-08 ratchet: body_decl field name, shape, kind | VERIFIED | Lines 44-150: field-name tuple, subarray-shapes, kind/itemsize, vectorized (5,14), 0-d (14,) all pin `body_decl` |
| `tests/composite/test_calculate_composite.py` | DECL-07 composite: non-zero, range, chain self-consistent | VERIFIED | Lines 252-317: `test_body_decl_is_not_all_zero`, `test_body_decl_in_valid_range`, `test_body_decl_matches_chain_rederviation` |
| `tests/returns/test_lunar_return.py` | DECL-07 returns: inherited body_decl non-zero + machine precision | VERIFIED | Lines 398-490: `test_body_decl_is_populated` (non-zero assert) + `test_body_decl_matches_declination_array_path` (exact match) |
| `docs/source/api.md` | EN: four functions + β-vs-δ section | VERIFIED | Four function subsections, OOB section, "Equatorial Declination (New in v1.5)" anchor section with β-vs-δ table |
| `docs/source/concepts.md` | EN: draconic month, montant/descendant, OOB | VERIFIED | Lines 306-375: full montant/descendant and OOB sections |
| `docs/locale/fr/LC_MESSAGES/api.po` + `.mo` | FR: translated + compiled | VERIFIED | All four functions translated; `.mo` compiled 2026-06-03 22:08 |
| `docs/locale/fr/LC_MESSAGES/concepts.po` + `.mo` | FR: montant/descendant + OOB translated | VERIFIED | `montant/descendant`, `hors limites` entries present; `.mo` compiled |
| `docs/locale/fr/LC_MESSAGES/changelog.po` + `.mo` | FR: v1.5 declination entry | VERIFIED | All msgids for declination changelog entries translated; `.mo` compiled |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ketu/calculations.py:declination` | `ecliptic_to_equatorial` + `rectangular_to_spherical` chain | scalar: `long`/`lat`; array: `calc_planet_position_batch` | WIRED | Both paths call the coordinates chain; no Python loop in array path |
| `ketu/calculations.py:is_out_of_bounds` | `true_obliquity` | `abs(declination(jdate, body)) > true_obliquity(jdate)` | WIRED | Direct call at line 594 |
| `ketu/charts/api.py:compute_chart` | `body_decl` field | `out["body_decl"] = decl` at line 394 | WIRED | Derived from already-fetched `body_lons`/`body_lats` + `eps_b` broadcast |
| `ketu/composite/api.py:calculate_composite` | `body_decl` field | explicit derivation from composite λ,β at lines 252-266 | WIRED | Not zero-fill; uses `ecliptic_to_equatorial` + `rectangular_to_spherical` |
| Returns (`solar.py`, `lunar.py`) | `body_decl` | delegate to `compute_chart` | WIRED | Both `return compute_chart(...)` — inherit `body_decl` for free |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| DECL-01 | SATISFIED | scalar `declination()` tested, all 14 bodies, range check |
| DECL-02 | SATISFIED | array path tested, shape preserved, matches per-element scalar |
| DECL-03 | SATISFIED | regression pinned vs explicit chain + Meeus 13.4, tolerance < 1e-9° |
| DECL-04 | SATISFIED | `declination_velocity` FD, no wraparound, all 14 bodies |
| DECL-05 | SATISFIED | `is_ascending_declination` distinct from β-based `is_ascending`; JD proof |
| DECL-06 | SATISFIED | `is_out_of_bounds` with instantaneous `true_obliquity` threshold |
| DECL-07 | SATISFIED | `body_decl` populated in `compute_chart`, `calculate_composite`, inherited by Returns |
| DECL-08 | SATISFIED | ratchet in `test_dtype.py`: field name, shape, kind/itemsize, vectorized, 0-d |
| DECL-09 | SATISFIED | EN + FR docs covering all four functions, montant/descendant framing, β-vs-δ, OOB |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns in phase 33 files. No stub implementations.

### Human Verification Required

None. All claims are programmatically verifiable.

## Test Suite Results

- **1584 tests passed, 2 skipped** (full suite via `pytest tests/`)
- **100% coverage** (required gate: `fail_under=100`)
- **mypy --strict clean** (69 source files, no issues)
- Phase 33 commits: 16 commits from `6183bad` to `ee4736b`

## Summary

Phase 33 goal is fully achieved. All five observable truths are verified against the actual source code:

1. Four public declination functions exist in `ketu/calculations.py` with correct implementations (scalar + vectorized paths, finite-difference velocity, OOB via instantaneous obliquity) and are exported in `__all__`.
2. `is_ascending` (β-based) is unchanged — still delegates to `lat_velocity`.
3. `body_decl` is in `CHART_DTYPE`, populated in `compute_chart` and explicitly in `calculate_composite` (not the zero-fill trap), inherited for free by Returns.
4. DECL-08 ratchet guards the field across five test locations in `test_dtype.py`.
5. EN and FR documentation covers all four functions, the draconic month (~27.21 d), montant/descendant biodynamic framing, the β-vs-δ distinction, OOB/standstill, and the `body_decl` field addition — with compiled `.mo` files.

---

_Verified: 2026-06-03T20:20:05Z_
_Verifier: Claude (gsd-verifier)_
