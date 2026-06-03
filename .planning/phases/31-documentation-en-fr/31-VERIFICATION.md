---
phase: 31-documentation-en-fr
verified: 2026-06-03T14:31:30Z
status: passed
score: 4/4 must-haves verified
re_verification: false
---

# Phase 31: Documentation EN+FR Verification Report

**Phase Goal:** The Sphinx docs (en + fr) accurately reflect the v1.4 API surface — concepts.md recentred on the 180°-division default, stale default-aspect claims corrected, the dynamic-harmonics generator and Chiron updates documented — with zero English fallback in touched French gettext catalogs, and a clean build at the 1-warning baseline.

**Verified:** 2026-06-03T14:31:30Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1 | concepts.md aspect tables show CLASSICAL (5) and TRADITIONAL (7) only; H5/H9/H10 removed from tables but framed as opt-in; 180°-division default is the baseline framing | VERIFIED | Summary table (lines 101–108) shows only harmonics 1/2/3/6; "Aspect Types" table shows only the 7 TRADITIONAL aspects; H5/H9/H10 explicitly marked opt-in (lines 76, 97, 108, 231) |
| 2 | migration.md and relational_charts.md contain no stale EXTENDED/classical default claim for the library; only TRADITIONAL (7) is stated as current default | VERIFIED | migration.md line 131 correctly labels EXTENDED as historical v1.1 default; relational_charts.md line 81 correctly notes calculate_synastry's own "classical" is pinned for backward compat, distinct from library default; no rogue stale default strings found |
| 3 | generate_harmonic_aspects(h) documented in API and concepts with runnable example, ~2× smaller orb note, Chiron 1900–2100 range, Chiron orb 4°; no Kala references | VERIFIED | concepts.md lines 163–192: section + runnable code example (H7 septile) + orb note; api.md lines 221–248: full parameter docs + runnable example + orb note; Chiron 1900–2100 in concepts.md line 66, api.md line 754, chiron.md line 10; Chiron orb 4° in concepts.md line 214; zero Kala references found across all docs |
| 4 | All 7 touched FR catalogs: 0 untranslated, 0 fuzzy, .mo fresh; make html (en) and make html-fr each succeed at exactly 1 warning | VERIFIED | Babel analysis: all 7 catalogs 0 untranslated / 0 fuzzy; all 7 .mo files newer than or equal to .po files; both sphinx-build runs succeeded with exactly 1 warning ("display_version" theme option — pre-existing baseline) |

**Score:** 4/4 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/source/concepts.md` | 180°-division default framing, CLASSICAL+TRADITIONAL tables, H5/H9/H10 opt-in, generate_harmonic_aspects section, Chiron 1900–2100 + 4° orb | VERIFIED | All present and substantive |
| `docs/source/api.md` | generate_harmonic_aspects documented with example, orb note, Chiron 1900–2100 range | VERIFIED | api.md lines 221–248, 754–755 |
| `docs/source/migration.md` | No stale EXTENDED default; TRADITIONAL correctly stated as v1.3+ default | VERIFIED | Lines 131, 136 correctly frame EXTENDED as historical |
| `docs/source/relational_charts.md` | No stale library default claim; calculate_synastry's classical intentional and clearly labelled | VERIFIED | Line 81 explicitly distinguishes calculate_synastry's own default from the library default |
| `docs/source/chiron.md` | 1900–2100 range documented | VERIFIED | Line 10, 64 |
| `docs/locale/fr/LC_MESSAGES/concepts.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 268 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/migration.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 89 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/relational_charts.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 88 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/api.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 194 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/chiron.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 31 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/changelog.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 125 entries, 0/0, .mo fresh |
| `docs/locale/fr/LC_MESSAGES/architecture.po` | 0 untranslated, 0 fuzzy, .mo fresh | VERIFIED | 119 entries, 0/0, .mo fresh |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| concepts.md generate_harmonic_aspects section | aspects module | runnable code example | WIRED | Example imports from ketu.aspects, calls generate_harmonic_aspects(7), passes to calculate_aspects via dynamic_specs= |
| concepts.md Chiron mention | chiron.md | cross-reference link | WIRED | "See Chiron" link at concepts.md line 66 |
| api.md Chiron section | chiron_coeffs.npz | 1900–2100 range stated | WIRED | api.md line 754 correctly states 2283 segments, jd range |
| FR .po files | FR .mo files | compiled binary | WIRED | All 7 .mo files newer than or equal to .po source |

---

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| DOC-14 (recentre on 180° default) | SATISFIED | concepts.md uses 180°-division as framing baseline throughout; H5/H9/H10 are opt-in |
| DOC-15 (correct stale default-aspect claims) | SATISFIED | migration.md and relational_charts.md updated; no rogue EXTENDED-default or classical-default strings for the library |
| DOC-16 (document generate_harmonic_aspects, Chiron 1900–2100, orb 4°) | SATISFIED | generate_harmonic_aspects documented in concepts.md + api.md with runnable examples and orb note; Chiron range and orb present |
| DOC-17 (zero EN fallback in touched FR catalogs, clean build at 1-warning baseline) | SATISFIED | All 7 catalogs fully translated (0 untranslated / 0 fuzzy); both en and fr builds succeed at exactly 1 warning |

---

### Anti-Patterns Found

None detected. No TODO/FIXME/placeholder markers in touched files. No stale Kala references. No empty return stubs.

---

### Human Verification Required

None. All criteria are programmatically verifiable and verified.

---

### Gaps Summary

No gaps. All 4 must-have truths are verified against the actual codebase.

Notable observations for completeness:

- The repo-root CHANGELOG.md and docs/source/changelog.md correctly preserve the frozen 1950–2050 / 0.005695° history in `### Added 1.3.0`; the new `[1.4.0]` section documents the 1900–2100 expansion. This is intentional and correct.
- The single build warning (`display_version option not supported by theme`) is the established pre-phase baseline, not introduced by phase 31 work.
- concepts.md line 122 documents CLASSICAL (5) as "the old v1.2 default — still available as the opt-in 5 majors preset", satisfying the requirement that both CLASSICAL and TRADITIONAL be shown with their default-vs-opt-in status clearly marked.

---

_Verified: 2026-06-03T14:31:30Z_
_Verifier: Claude (gsd-verifier)_
