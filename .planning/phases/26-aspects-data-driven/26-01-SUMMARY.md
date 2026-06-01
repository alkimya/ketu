---
phase: 26-aspects-data-driven
plan: "01"
subsystem: core
tags: [numpy, structured-arrays, aspects, harmonics, astrological-glyphs]

requires:
  - phase: 25-documentation
    provides: concepts.md with harmonic mapping (half-circle vs full-circle convention)

provides:
  - "core.aspects enriched with harmonic (i4) + symbol (U4) columns (5-field dtype)"
  - "Frozen harmonic vector [1,6,10,9,3,5,9,2,10,3,5,6,9,1] canonical source of truth"
  - "7 major glyph symbols (U+260C/U+26BA/U+26B9/U+25A1/U+25B3/U+26BB/U+260D); 7 minors blank"
  - "V1 byte fingerprint still passes (name/angle/coef byte-stable); V13 fingerprint pinned"

affects:
  - "26-02: aspects_for_harmonics reads the harmonic column to build TRADITIONAL/EXTENDED masks"
  - "26-03: CHANGELOG + api.md references the 5-field schema"

tech-stack:
  added: []
  patterns:
    - "Append-only dtype extension: new fields added after existing; positional bytes of prior fields unchanged"
    - "Dual fingerprint pattern: V1 proves stability, V13 pins the extension"
    - "Half-circle harmonic convention: Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6 (NOT naive 360/angle)"

key-files:
  created: []
  modified:
    - ketu/core.py
    - tests/test_ketu.py

key-decisions:
  - "harmonic dtype U4 for symbol (headroom, no truncation risk for multi-codepoint glyphs)"
  - "7 minors get blank symbol ('') — no tofu glyphs for Decile/Novile/Quintile/Binovile/Tredecile/Biquintile/Quadrinovile"
  - "Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6 frozen (half-circle convention from concepts.md)"
  - "Append harmonic+symbol AFTER coef so V1 name+angle+coef bytes stay bit-for-bit identical"
  - "Keep field name 'coef' (not 'coefficient') — rename deferred to api.md/CHANGELOG in Plan 03"

patterns-established:
  - "Dual fingerprint: V1 (prior fields only) proves append-only stability; V13 (all fields) pins new data"
  - "Per-row harmonic + symbol loops in test_aspects_structure cover 100% of new columns independently of fingerprint"

duration: 4min
completed: 2026-06-01
---

# Phase 26 Plan 01: Aspects Data-Driven — Core Array Enrichment Summary

**core.aspects extended from 3 to 5 fields with frozen harmonic vector [1,6,10,9,3,5,9,2,10,3,5,6,9,1] and 7 major Unicode glyphs, byte-stable append to name/angle/coef (V1 fingerprint unchanged)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-01T14:25:31Z
- **Completed:** 2026-06-01T14:29:18Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Enriched `core.aspects` dtype from `(name, angle, coef)` to `(name, angle, coef, harmonic, symbol)` — the data foundation for data-driven harmonic selection in Plan 02
- Frozen harmonic mapping: half-circle convention (Sextile=H3, Trine=H3, Semi-sextile=H6, Quincunx=H6) per concepts.md — guards against naive 360/angle reading
- 7 major astrological glyphs as Unicode escapes; 7 minors left blank — avoids tofu/encoding issues
- V1 byte fingerprint `c5bd177...` still passes (name/angle/coef bytes unchanged); V13 fingerprint `3258530...` pins harmonic+symbol; 100% coverage gate maintained (1378 tests)

## Task Commits

1. **Task 1: Add harmonic + symbol columns to core.aspects** - `b1090f7` (feat)
2. **Task 2: Flip dtype-names test + add per-row assertions + new fingerprint** - `db2db5c` (test)

**Plan metadata:** (final commit below)

## Files Created/Modified

- `/home/loc/workspace/ketu/ketu/core.py` — dtype extended (3 → 5 fields); 14 rows each gain harmonic (int) + symbol (str); module docstring updated; comment block updated
- `/home/loc/workspace/ketu/tests/test_ketu.py` — `test_aspects_dtype_names` updated to 5-field assertion; `EXPECTED_ASPECT_HARMONICS` + `EXPECTED_ASPECT_SYMBOLS` added; `test_aspects_structure` extended with per-row harmonic+symbol loops; `test_aspects_byte_fingerprint` gains V13 assertion

## Final dtype and frozen vectors

```
dtype: (name, angle, coef, harmonic, symbol)
       S16    f4     f4    i4        U4

harmonic vector: [1, 6, 10, 9, 3, 5, 9, 2, 10, 3, 5, 6, 9, 1]
                 Con Ssx Dec Nov Sex Qui Bin Sq  Tre Tri Biq Qui Qno Opp

symbol vector:   ☌  ⚺  ""  "" ⚹  ""  ""  □   ""  △  ""  ⚻  ""  ☍
                 (7 majors filled; 7 minors blank)

V1 fingerprint (name+angle+coef):                     c5bd177316ce98d4...  [UNCHANGED]
V13 fingerprint (name+angle+coef+harmonic+symbol):    3258530818272989c...  [NEW]
```

## Decisions Made

- Append-only extension: harmonic + symbol added AFTER coef so bytes for name/angle/coef remain identical — V1 fingerprint proves this
- Half-circle harmonic convention frozen: Sextile=H3, Trine=H3 (they divide the half-circle 180/60=3, 180/120→not-integer, but the concepts.md convention uses the shared H3 harmonic base); Semi-sextile=H6, Quincunx=H6
- 7 minors get `""` (blank) — no tofu risk; symbol dtype U4 gives headroom for multi-codepoint glyphs
- Unicode glyphs stored as literal chars in source (UTF-8 file), matching plan spec codepoints

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 02 (`aspects_for_harmonics`) can now read `aspects['harmonic']` to build the TRADITIONAL and EXTENDED masks
- The `symbol` column is the canonical glyph source of truth for display/CLI
- V1 fingerprint stability confirmed — no downstream regressions expected

## Self-Check: PASSED

- [x] `ketu/core.py` exists and has 5-field dtype
- [x] `tests/test_ketu.py` exists with `EXPECTED_ASPECT_HARMONICS`
- [x] Commit `b1090f7` (feat Task 1) exists
- [x] Commit `db2db5c` (test Task 2) exists
- [x] 1378 tests pass, 100% coverage, 56 doctests green

---
*Phase: 26-aspects-data-driven*
*Completed: 2026-06-01*
