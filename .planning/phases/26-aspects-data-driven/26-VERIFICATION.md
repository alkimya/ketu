---
phase: 26-aspects-data-driven
verified: 2026-06-01T15:14:08Z
status: passed
score: 4/4 must-haves verified
---

# Phase 26: Aspects Data-Driven + Dynamic Harmonics — Verification Report

**Phase Goal:** The aspect engine is data-driven — aspects live in a single declarative table (name, angle, harmonic, coefficient, symbol) and the detection logic iterates over it — with dynamic selection by harmonic, the full-circle minor aspects (H5/H9/H10) removed from the default set, and the public preset/coefficient surface migrated cleanly. Landing this BEFORE the release means v1.3.0 ships the final aspect contract (no breaking 1.4 follow-up).
**Verified:** 2026-06-01T15:14:08Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Aspects defined in one declarative data table with name, angle, harmonic, coef(=coefficient), symbol; detection iterates the table | VERIFIED | `core.aspects.dtype.names == ('name', 'angle', 'coef', 'harmonic', 'symbol')`, 14 rows, V1 fingerprint c5bd177... unchanged |
| 2 | `aspects_for_harmonics([1,2,3,6])` composes 7 half-circle aspects; CLASSICAL/TRADITIONAL/EXTENDED presets intact | VERIFIED | Function exists in `ketu.aspects`, sum=7 for [1,2,3,6], sum=7 for [5,9,10], sum=14 for all; ValueError on [7]/bool/str; frozen mask |
| 3 | Default aspect set is the 7 half-circle set (H1/2/3/6); full-circle minors opt-in; CLI stays classical(5) | VERIFIED | `resolve_aspect_set(None)==TRADITIONAL`, sum=7; `compute_chart()` default==traditional; CLI `None` branch calls `resolve_aspect_set("classical")`, sum=5 |
| 4 | Breaking change documented in CHANGELOG+UPGRADING; concepts.md+api.md updated; fr gettext regenerated; suite green at 100% | VERIFIED | CHANGELOG [1.3.0] with Added+BREAKING; UPGRADING v1.2->v1.3 with restore recipe; concepts.md/api.md have `aspects_for_harmonics` + no stale EXTENDED-default claims; api.po+concepts.po regenerated; 1399 tests, 100% coverage, 57 doctests |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ketu/core.py` | 5-field dtype with harmonic (i4) + symbol (U4) | VERIFIED | dtype.names = ('name','angle','coef','harmonic','symbol'); 14 rows; harmonic=[1,6,10,9,3,5,9,2,10,3,5,6,9,1]; 7 majors glyphed; 7 minors blank |
| `ketu/aspects/presets.py` | `aspects_for_harmonics` + harmonic-derived presets + flipped resolver default | VERIFIED | `_VALID_HARMONICS` data-driven from table; `aspects_for_harmonics` at line 113; TRADITIONAL/EXTENDED derived via function at lines 193-194; `resolve_aspect_set` default=TRADITIONAL at line 209 |
| `ketu/aspects/__init__.py` | Export `aspects_for_harmonics` | VERIFIED | Import at line 64; in `__all__` at line 103 |
| `ketu/cli/aspects_cmd.py` | None branch pinned to `resolve_aspect_set("classical")` | VERIFIED | Line 91: `mask = resolve_aspect_set("classical")` with comment explaining intentional divergence |
| `tests/cli/test_cli_default_divergence.py` | Regression test locking CLI(5) != library(7) | VERIFIED | File exists; 3 tests: library_default_is_seven_half_circle, cli_bare_default_is_classical_five, cli_and_library_defaults_differ |
| `tests/charts/test_aspect_matrix.py` | D-07 ratchet re-pointed to traditional | VERIFIED | `test_aspect_matrix_default_aspects_is_traditional` at line 81 |
| `CHANGELOG.md` | [1.3.0] BREAKING aspect-engine entry | VERIFIED | `## [1.3.0] - Unreleased` at line 34; Added+BREAKING entries present |
| `UPGRADING.md` | v1.2 -> v1.3 migration section | VERIFIED | `## v1.2 -> v1.3` at line 6; two-part shift, restore recipe, new API example, Kala note |
| `docs/source/concepts.md` | default-now-7 note + `aspects_for_harmonics` example | VERIFIED | `aspects_for_harmonics` present; "7 half-circle aspects" default noted |
| `docs/source/api.md` | `aspects_for_harmonics` docs + harmonic/symbol + coef mapping + stale defaults fixed | VERIFIED | New section at line 189; harmonic/symbol documented; coef==coefficient mapping noted; no stale EXTENDED-default claims |
| `docs/locale/fr/LC_MESSAGES/api.po` | Regenerated with new msgids | VERIFIED | `aspects_for_harmonics` present in catalog |
| `docs/locale/fr/LC_MESSAGES/concepts.po` | Regenerated with new msgids | VERIFIED | `aspects_for_harmonics` present in catalog |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `core.aspects` dtype | harmonic + symbol columns after coef | field order (name,angle,coef,harmonic,symbol) | WIRED | dtype.names verified live; V1 fingerprint proves append-only stability |
| `aspects_for_harmonics` | `core.aspects['harmonic']` column | `_ASPECTS['harmonic']` lookup in presets.py | WIRED | `_VALID_HARMONICS` derived data-driven; mask built via `np.isin(_ASPECTS["harmonic"], ...)` |
| `resolve_aspect_set(None)` | 7 half-circle default | `default=TRADITIONAL` param | WIRED | Verified live: `resolve_aspect_set(None).sum() == 7`, equals TRADITIONAL |
| `ketu/cli/aspects_cmd.py None branch` | classical(5) | `resolve_aspect_set("classical")` explicit | WIRED | Line 91; all 139 CLI tests green; byte-stable contract preserved |
| `compute_chart(aspects=None)` | 7 half-circle aspect matrix | threads None -> resolve_aspect_set(None) -> TRADITIONAL | WIRED | Verified live: `compute_chart(jd, ...) aspect_matrix` byte-equal to `compute_chart(jd, ..., aspects="traditional")` |
| `docs/source/api.md` | 7 half-circle default (not EXTENDED) | replace stale EXTENDED claims | WIRED | 3 stale claims removed; grep confirms no EXTENDED-default language remains |

### Requirements Coverage

No explicit REQUIREMENTS.md entries mapped to Phase 26 beyond the Success Criteria above. All 4 stated success criteria satisfied.

### Anti-Patterns Found

None. Scanned `ketu/core.py`, `ketu/aspects/presets.py`, `ketu/aspects/__init__.py`, `ketu/cli/aspects_cmd.py`, `tests/cli/test_cli_default_divergence.py` — no TODO/FIXME/PLACEHOLDER/empty-return patterns found.

### Human Verification Required

None. All goal-relevant behaviors are verifiable programmatically.

### Summary

Phase 26 goal fully achieved. The aspect engine is data-driven: `core.aspects` is a 5-field NumPy structured array (name, angle, coef, harmonic, symbol) serving as the single source of truth. `aspects_for_harmonics` composes masks from the harmonic column with no hardcoded indices. The library default is the 7 half-circle aspects (TRADITIONAL); full-circle minors are opt-in. The CLI is pinned to classical(5) preserving the v1.0/v1.1 byte-stable contract. All user decisions (half-circle convention, blank minor symbols, `coef` field name, CLI divergence) are implemented and tested. CHANGELOG [1.3.0] and UPGRADING v1.2->v1.3 document the breaking change with restore recipe. The suite passes 1399 tests at 100% coverage with 57 doctests and mypy --strict clean.

---
_Verified: 2026-06-01T15:14:08Z_
_Verifier: Claude (gsd-verifier)_
