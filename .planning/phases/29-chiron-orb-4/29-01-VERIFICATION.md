---
phase: 29-chiron-orb-4
verified: 2026-06-03T11:35:00Z
status: passed
score: 6/6 must-haves verified
re_verification: false
---

# Phase 29: Chiron Orb 4° Verification Report

**Phase Goal:** Chiron's natal orb is 4° (Pluto parity) — a single-source constant change that propagates automatically to all aspect detection, synastry, cycles, and the CLI — with test artifacts updated to reflect the new value.
**Verified:** 2026-06-03T11:35:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                     | Status     | Evidence                                                                                           |
|----|-------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------------------------------------|
| 1  | core.bodies['orb'][13] == 4.0, identical to Pluto (id=9)                                  | VERIFIED   | `ketu/core.py:84` `("Chiron", 13, 4, 0.019)` matches `("Pluto", 9, 4, 0.004)` at line 80         |
| 2  | _BODY_ORBS_16[13] == 4.0 propagated automatically, no second source patched               | VERIFIED   | `orbs.py:71` slices `_BODIES["orb"]` at import time; python probe confirms `_BODY_ORBS_16[13]=4.0`|
| 3  | CLI fixture gains exactly 2 new lines (Sun-Chiron + Moon-Chiron Semi-sextile), 0 removed  | VERIFIED   | `git show fcbadec` shows `2 ++, 0 --`; fixture lines 27+34 are the exact Semi-sextile lines       |
| 4  | test_synastry_orb_limit_chiron_chiron_parity_pluto pins _BODY_ORBS_16[13]==4.0 via orb limit==2.0 | VERIFIED | Test exists at `test_orbs.py:109`, asserts `synastry_orb_limit(13,13,0) == approx(2.0)`; PASSES |
| 5  | Synastry docstrings no longer group Chiron with Rahu/Ketu/Lilith                          | VERIFIED   | `test_modes_idempotent.py` module docstring (line 7) and test docstring (line 112) list only `Rahu / Ketu / Lilith`; grep confirms no `Lilith / Chiron` or `Lilith, Chiron` pattern anywhere |
| 6  | Full suite 1531 tests pass, 100% coverage, frozen fingerprints unchanged                  | VERIFIED   | `pytest tests/ -q` reports `1531 passed, 2 skipped`, `Total coverage: 100.00%`; fingerprint test passes |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact                                              | Expected                                                     | Status   | Details                                                                          |
|-------------------------------------------------------|--------------------------------------------------------------|----------|----------------------------------------------------------------------------------|
| `ketu/core.py`                                        | Single source: Chiron orb=4 in bodies structured array       | VERIFIED | Line 84: `("Chiron", 13, 4, 0.019)` — only change is orb field 0→4             |
| `tests/cli/fixtures/v1_1_reference_output.txt`        | Regenerated with 2 new Chiron Semi-sextile lines             | VERIFIED | 2355 bytes; lines 27+34 contain Sun-Chiron and Moon-Chiron Semi-sextile         |
| `tests/synastry/test_orbs.py`                         | New test `test_synastry_orb_limit_chiron_chiron_parity_pluto`| VERIFIED | Lines 109-116: test exists, asserts orb limit == 2.0, passes                   |
| `tests/synastry/test_modes_idempotent.py`             | Chiron removed from zero-orb group in 2 docstrings           | VERIFIED | Module docstring line 7, test docstring line 112: both list `Rahu / Ketu / Lilith` only |

### Key Link Verification

| From                                   | To                                       | Via                                              | Status  | Details                                                                  |
|----------------------------------------|------------------------------------------|--------------------------------------------------|---------|--------------------------------------------------------------------------|
| `ketu/core.py bodies['orb'][13]`       | `ketu/synastry/orbs.py _BODY_ORBS_16[13]`| `_build_body_orbs_16()` slices `_BODIES["orb"]` | WIRED   | `orbs.py:71` slices at import; python probe confirms value propagated    |
| `ketu/core.py bodies['orb']`           | `tests/cli/fixtures/v1_1_reference_output.txt` | `python -m ketu --harmonics all aspects`   | WIRED   | Fixture regenerated from live CLI; `test_v1_1_reference_byte_stable.py` compares byte-for-byte and passes |

### Requirements Coverage

| Requirement | Status    | Blocking Issue |
|-------------|-----------|----------------|
| CHIR-06     | SATISFIED | — (Chiron orb=4 in single source, propagated automatically) |
| CHIR-07     | SATISFIED | — (CLI fixture regenerated, audited: exactly 2 lines added, 0 removed) |
| CHIR-08     | SATISFIED | — (Docstrings corrected; pinning test added and passing) |

### Anti-Patterns Found

No blockers or warnings detected.

- No TODO/FIXME/placeholder comments in modified files
- No empty implementations or stub returns
- No hard-coded numeric literals duplicating the orb value (single-source respected)
- No out-of-scope `.npz` or Chiron-range work introduced
- No new runtime dependencies (pure-NumPy preserved)

### Human Verification Required

None — all success criteria are fully verifiable programmatically via the test suite.

### Gaps Summary

No gaps. All 6 truths verified, all 4 artifacts present and substantive, both key links wired.

---

_Verified: 2026-06-03T11:35:00Z_
_Verifier: Claude (gsd-verifier)_
