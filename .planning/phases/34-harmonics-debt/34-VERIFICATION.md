---
phase: 34-harmonics-debt
verified: 2026-06-03T23:15:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 34: Harmonics Debt Verification Report

**Phase Goal:** The three dynamic-harmonics debts left open by v1.4 are paid down — the synthetic off-table aspect naming scheme H{h}-{k} is a documented, pinned public API contract; find_aspect_timing can derive its dynamic orb itself from a coefficient instead of the caller passing it raw; and a user can request an arbitrary harmonic on the CLI via --harmonics h7 — all while the frozen 14-row core.aspects table and its V1/V13 sha256 preset fingerprints stay byte-identical.
**Verified:** 2026-06-03T23:15:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | H{h}-{k} naming scheme is a documented public API contract, pinned by TestNamingContractF2 covering h=2..64, boundary h=2 (opposition-only), even-h folding last row to 180°, and h7 exact names | VERIFIED | TestNamingContractF2 (5 tests) at tests/test_dynamic_harmonics.py:654 passes; generate_harmonic_aspects docstring at harmonics.py:169 carries "Public API contract (frozen, v1.5+)" paragraph; regex sweep over all h in [2..64] confirmed programmatically |
| 2 | Docs distinguish GENERATOR channel (always H{h}-{k}) from DETECTION channel (canonical table name on collision, 120° → Trine not H3-1) | VERIFIED | concepts.md line 196-209 has (synthetic-harmonic-naming)= subsection with explicit GENERATOR/DETECTION paragraphs; collision test confirmed: calculate_aspects with generate_harmonic_aspects(3) yields i_asp=9 (Trine), not i_asp=-2 |
| 3 | find_aspect_timing accepts dyn_coef=None, derives orb via (orb_b1+orb_b2)/2*dyn_coef; explicit orb wins silently when both given; static and explicit-orb paths backward-compatible; off-table-no-args raises ValueError | VERIFIED | Signature confirmed: (jdate, body1, body2, aspect_value, orb=None, dyn_coef=None); all 4 behavioral properties verified programmatically; TestFindAspectTimingF3 (5 tests) at tests/test_find_aspect_timing_f3.py:28 passes |
| 4 | --harmonics h7 accepted end-to-end (case-insensitive, h-prefixed, Tight grammar, range-delegated); parse_harmonics_spec returns HarmonicsSelection NamedTuple; h7,h11 and traditional,h7 rejected; H7-k names in stdout, not Quadrinovile; # Aspect set: h7 in stderr | VERIFIED | rc=0, stdout has 6 H7- rows, 0 Quadrinovile, stderr shows "# Aspect set: h7 (3 aspects: H7-1 51°, H7-2 103°, H7-3 154°)"; TestHarmonicTokenF1 (13 tests at test_harmonics_spec.py:202) and TestAspectsCmdHarmonicsH7 (3 integration tests) all pass |
| 5 | Existing v1.1 CLI byte-stability fixture unchanged; new h7 fixture generated and audited (H7-k names, no Quadrinovile, U+00BA degree symbol, timing block present, # Aspect set: h7 on stderr); --harmonics h7 CLI surface documented en + fr; V1/V13 sha256 fingerprints byte-identical | VERIFIED | TestV1_1ReferenceByteStable passes unchanged; TestHarmonicsH7ByteStable (6 tests) passes; h7 fixture: 6 H7- rows, 0 Quadrinovile, 20 U+00BA (0 U+00B0), Aspect Timing Example present; concepts.md and api.md carry h7 CLI section; FR PO files fully translated (0 fuzzy entries); V1/V13 fingerprint tests pass |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_dynamic_harmonics.py` | TestNamingContractF2 pinning class (5 tests) | VERIFIED | Class at line 654; all 5 methods present and passing |
| `ketu/aspects/harmonics.py` | "Public API contract" paragraph in docstring | VERIFIED | Lines 169+ contain the frozen-v1.5+ contract statement with H{h}-{k} |
| `docs/source/concepts.md` | Two-channel GENERATOR/DETECTION distinction + traditional-name table | VERIFIED | (synthetic-harmonic-naming)= subsection at line 196; septile/novile table present |
| `ketu/aspects/calculator.py` | find_aspect_timing with dyn_coef param + 3-branch orb resolution | VERIFIED | dyn_coef at line 574; 3-branch block with explicit-orb-first precedence |
| `tests/test_find_aspect_timing_f3.py` | TestFindAspectTimingF3 (5 tests) | VERIFIED | All 5 methods present and passing |
| `docs/source/api.md` | dyn_coef documented with precedence; find_aspect_timing section | VERIFIED | Line 414 has updated find_aspect_timing with dyn_coef parameter table |
| `ketu/cli/harmonics_spec.py` | HarmonicsSelection NamedTuple + ^h(\d+)$ parse branch | VERIFIED | HarmonicsSelection at line 65; _H_TOKEN_RE; h<N> branch functional |
| `ketu/display.py` | print_aspects(dynamic_specs=) with synthetic-name lookup for i_asp=-2 | VERIFIED | dynamic_specs param at line 95; _normalize_dynamic_specs imported and used |
| `ketu/cli/aspects_cmd.py` | _harmonic_label() + cmd_aspects destructures HarmonicsSelection + dynamic_specs= threading | VERIFIED | _harmonic_label at line 71; dynamic_specs at line 134, 154 |
| `ketu/cli/formatters.py` | emit_resolved_config(dynamic_label=None) override | VERIFIED | dynamic_label at line 23; override logic at line 58 |
| `tests/cli/test_harmonics_spec.py` | TestHarmonicTokenF1 (13 tests) | VERIFIED | All 13 test methods present and passing |
| `tests/cli/test_aspects_cmd.py` | TestAspectsCmdHarmonicsH7 (3 integration tests) | VERIFIED | All 3 tests present and passing |
| `tests/cli/fixtures/harmonics_h7_reference_output.txt` | Pinned h7 stdout fixture | VERIFIED | Non-empty; 6 H7- rows; 0 Quadrinovile; Aspect Timing Example present |
| `tests/cli/test_v1_1_reference_byte_stable.py` | TestHarmonicsH7ByteStable sibling class (6 tests) | VERIFIED | Class at line 230; all 6 tests present and passing; existing TestV1_1ReferenceByteStable untouched |
| `docs/locale/fr/LC_MESSAGES/concepts.mo` | Compiled French translation | VERIFIED | .mo newer than .po (both 2026-06-03T22:56); 0 fuzzy entries in .po |
| `docs/locale/fr/LC_MESSAGES/api.mo` | Compiled French translation | VERIFIED | .mo newer than .po (both 2026-06-03T22:56); 0 fuzzy entries in .po |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| tests/test_dynamic_harmonics.py | ketu.aspects.harmonics.generate_harmonic_aspects | import + ['name'].tolist() assertions | WIRED | generate_harmonic_aspects called directly in TestNamingContractF2 |
| tests/test_dynamic_harmonics.py | ketu.aspects.calculator.calculate_aspects | collision test: i_asp==9 (Trine) | WIRED | calculate_aspects used in test_naming_collision_detection_prefers_table_name |
| tests/test_find_aspect_timing_f3.py | ketu.aspects.calculator.find_aspect_timing | dyn_coef= and orb= calls | WIRED | All 5 test methods call find_aspect_timing directly |
| ketu.aspects.calculator.find_aspect_timing | ketu.core.bodies | (bodies['orb'][b1]+bodies['orb'][b2])/2*dyn_coef | WIRED | Confirmed at calculator.py lines 631-634 |
| ketu.cli.aspects_cmd.cmd_aspects | ketu.cli.harmonics_spec.HarmonicsSelection | .mask and .dynamic_specs destructure | WIRED | Lines 134, 142 in aspects_cmd.py |
| ketu.cli.aspects_cmd.cmd_aspects | ketu.display.print_aspects | print_aspects(jd, aspects=mask, dynamic_specs=dyn) | WIRED | Line 154 in aspects_cmd.py |
| ketu.cli.harmonics_spec.parse_harmonics_spec | ketu.aspects.harmonics.generate_harmonic_aspects | h<N> branch calls generate_harmonic_aspects(h) | WIRED | ValueError wrapped as ArgumentTypeError |
| tests/cli/test_v1_1_reference_byte_stable.py | tests/cli/fixtures/harmonics_h7_reference_output.txt | subprocess compare byte-for-byte | WIRED | FIXTURE_H7 constant and test_h7_byte_identical_to_fixture at line 255 |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| HARM-01: H{h}-{k} documented public API contract | SATISFIED | harmonics.py docstring + concepts.md + api.md |
| HARM-02: Pinning test for h7 exact, h2 boundary, even-h last row, all h in [2..64] | SATISFIED | TestNamingContractF2 with 5 tests |
| HARM-03: GENERATOR/DETECTION distinction documented and tested | SATISFIED | concepts.md two-channel subsection; collision test in TestNamingContractF2 |
| HARM-04: find_aspect_timing derives orb from dyn_coef | SATISFIED | 3-branch block implemented; formula matches calculate_aspects |
| HARM-05: Static path + explicit-orb escape hatch backward-compatible; precedence defined and tested | SATISFIED | TestFindAspectTimingF3 covers all 4 behavioral properties |
| HARM-06: --harmonics h7 accepted end-to-end | SATISFIED | rc=0, H7-k in stdout, no Quadrinovile, Tight grammar enforced |
| HARM-07: HarmonicsSelection NamedTuple, mypy --strict clean, Tight grammar tested | SATISFIED | 6 source files mypy --strict clean; HarmonicsSelection typed |
| HARM-08: v1.1 fixture unchanged; new h7 fixture generated and audited | SATISFIED | TestV1_1ReferenceByteStable passes; TestHarmonicsH7ByteStable 6 tests pass |
| HARM-09: --harmonics h7 CLI surface documented en + fr | SATISFIED | concepts.md + api.md; FR PO/MO updated with 0 fuzzy entries |
| core.aspects V1/V13 fingerprints byte-identical | SATISFIED | V1/V13 fingerprint tests pass; core.py last modified commit d3c057a (Phase 29) |

### Anti-Patterns Found

None. All modified production files clean (no TODO/FIXME/placeholder/return null patterns).

### Human Verification Required

None. All verification is automatable and complete.

### Gaps Summary

No gaps. All 5 observable truths verified, all 16 artifacts present and substantive and wired, all 9 HARM requirements satisfied.

**Additional quality gates confirmed:**
- Full test suite: 1623 passed, 2 skipped, 100% coverage, 0 pragma
- mypy --strict: clean on all 6 changed production modules
- FR PO/MO files: 0 fuzzy entries; .mo files newer than .po files
- h7 fixture audit: H7-k names (6 rows), 0 Quadrinovile, 20 U+00BA degree symbols, Aspect Timing Example present, # Aspect set: h7 on stderr

---
_Verified: 2026-06-03T23:15:00Z_
_Verifier: Claude (gsd-verifier)_
