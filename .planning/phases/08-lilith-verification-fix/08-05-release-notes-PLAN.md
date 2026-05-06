---
phase: 08-lilith-verification-fix
plan: 05
type: execute
wave: 4
depends_on:
  - "08-04"
files_modified:
  - CHANGELOG.md
  - UPGRADING.md
autonomous: true

must_haves:
  truths:
    - "User reads CHANGELOG.md and finds an explicit Lilith entry under v1.1.0 with the magnitude stated as a number (zero-magnitude is acceptable, but 'unspecified' is not)"
    - "User reads UPGRADING.md v1.0 -> v1.1 section and finds a Lilith subsection that either confirms 'no action required' (NO-OP branch) or provides a numerical recipe with concrete v1.0/v1.1 deltas (FORMULA-CORRECTION branch)"
    - "If branch == FORMULA-CORRECTION: user finds a per-date table in UPGRADING.md showing v1.0 Lilith vs v1.1 Lilith on at least 3 dates with the delta in degrees"
    - "Magnitude statement is consistent across LILITH_DEFINITION.md, CHANGELOG.md, and UPGRADING.md (same number, formatted to the same precision)"
    - "CHANGELOG entry follows the existing 'Keep a Changelog' format used by prior entries (per phase 06 pattern)"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "v1.1.0 Lilith verification/correction entry with explicit magnitude"
      contains: "Lilith"
    - path: "UPGRADING.md"
      provides: "v1.0 -> v1.1 Lilith migration section with numerical recipe (or no-action confirmation)"
      contains: "Lilith"
  key_links:
    - from: "CHANGELOG.md v1.1.0 section"
      to: "docs/LILITH_DEFINITION.md History v1.1 entry"
      via: "same MAX |delta| value, same precision formatting"
      pattern: "Lilith"
    - from: "UPGRADING.md v1.0 -> v1.1 section"
      to: "docs/LILITH_DEFINITION.md"
      via: "explicit cross-link"
      pattern: "LILITH_DEFINITION"
---

<objective>
Document the Lilith verification result in CHANGELOG.md and UPGRADING.md with an EXPLICIT magnitude statement — zero-magnitude is allowed, but "unspecified" is not. The two files communicate the v1.0 -> v1.1 numerical change (or its absence) to PyPI users.

Purpose: REQUIREMENTS LIL-05 + ROADMAP success criterion #5. Phase 8 always produces release notes — even if the formula was unchanged, the verification result itself is news to v1.0 users.

Output: One paragraph in `CHANGELOG.md` v1.1.0 section + one subsection in `UPGRADING.md` v1.0 -> v1.1 section.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/08-lilith-verification-fix/08-RESEARCH.md
@.planning/phases/08-lilith-verification-fix/08-03-SUMMARY.md
@.planning/phases/08-lilith-verification-fix/08-04-SUMMARY.md
@docs/LILITH_DEFINITION.md
@CHANGELOG.md
@UPGRADING.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add v1.1.0 Lilith entry to CHANGELOG.md (matches branch from Plan 04)</name>
  <files>CHANGELOG.md</files>
  <action>
Read `08-04-SUMMARY.md` to determine which branch ran. Read existing `CHANGELOG.md` to understand its formatting conventions (Keep a Changelog format, per phase 06 patterns recorded in history-digest).

Locate or create the `## [1.1.0] - UNRELEASED` section at the top of `CHANGELOG.md` (after the header but before any prior released versions). If the section already exists from prior v1.1 work (Phase 9, 10), append to it. If not, add it.

**If branch == NO-OP:**

Add under the v1.1.0 section (creating a `### Verified` subsection if absent):

```markdown
### Verified

- **Lilith (Mean Apogee) longitude**: cross-checked against Swiss Ephemeris
  `SE_MEAN_APOG` on five dates (1900-06-15, 1950-03-21, 2000-01-01,
  2025-09-23, 2050-12-21). Maximum deviation: MAX_DELTA deg, well below
  the 0.01 deg tolerance documented in `docs/LILITH_DEFINITION.md`. No
  formula change in v1.1. Test harness shipped at
  `tests/test_lilith_cross_check.py`.
```

Substitute `MAX_DELTA` with the actual value from `08-03-SUMMARY.md` (e.g. `0.000023`). Same precision (6 decimals) used throughout the phase.

**If branch == FORMULA-CORRECTION:**

Add under the v1.1.0 section a `### Fixed (BREAKING - Numerical Behavior Change)` subsection:

```markdown
### Fixed (BREAKING - Numerical Behavior Change)

- **Lilith (Mean Apogee) longitude formula corrected** to match Swiss
  Ephemeris `SE_MEAN_APOG`. Old formula in v1.0 deviated by up to
  MAX_DELTA deg on dates within 1900-2050 (root cause: ROOT_CAUSE).
  New formula and constants documented in `docs/LILITH_DEFINITION.md`.
  Concrete examples and migration recipe in `UPGRADING.md`. Recompute
  any cached Lilith values from v1.0 (e.g. ML feature arrays, lunation
  timing tables).
```

Substitute `MAX_DELTA` and `ROOT_CAUSE` from `08-03-SUMMARY.md` (e.g. `0.041` deg, "frame-of-reference mismatch — v1.0 epoch was mean-of-J2000 while swe returns mean-of-date").

Both variants must:
- Use ASCII-only (no Unicode degrees-sign — write `deg`)
- Cross-link `docs/LILITH_DEFINITION.md` and `UPGRADING.md`
- Match the precision style of the rest of `CHANGELOG.md` (e.g. if prior entries used backticks for code, do the same)

Do NOT modify the historical `pyswisseph` references in older CHANGELOG entries (0.1.0, 0.2.0). Those are out of scope per research §"Deferred (out of scope)".
  </action>
  <verify>
```bash
grep -E "^\\[1\\.1\\.0\\]|^## \\[1\\.1\\.0\\]" CHANGELOG.md && echo "v1.1.0 SECTION PRESENT"
grep -F "Lilith" CHANGELOG.md | head -5
grep -F "LILITH_DEFINITION.md" CHANGELOG.md
grep -F "UPGRADING.md" CHANGELOG.md  # at least one cross-link

# Magnitude is a number, not "unspecified":
grep -iE "unspecified|TBD|TODO" CHANGELOG.md && echo "FAIL: magnitude not yet filled in" || echo "MAGNITUDE STATED"

# No accidentally rewritten older entries:
git diff CHANGELOG.md | grep -E "^-.*\\[0\\.[12]\\.0\\]" && echo "FAIL: older sections changed" || echo "HISTORICAL ENTRIES PRESERVED"
```
  </verify>
  <done>
`CHANGELOG.md` has a v1.1.0 section with a Lilith entry; the entry contains an explicit numeric magnitude (no "unspecified"); cross-links to `LILITH_DEFINITION.md` and `UPGRADING.md` are present; older release entries are untouched.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add v1.0 -> v1.1 Lilith subsection to UPGRADING.md</name>
  <files>UPGRADING.md</files>
  <action>
Read `08-04-SUMMARY.md` to determine which branch ran. Read existing `UPGRADING.md` to understand its formatting (per phase 06 it's the "single source of truth" for migration).

Locate or create a `## v1.0 -> v1.1` heading. If the section already exists from prior v1.1 work (Phase 9/10), append a `### Lilith (Black Moon) Calculation` subsection. If not, add the v1.0 -> v1.1 section first, then the subsection.

**If branch == NO-OP:**

```markdown
### Lilith (Black Moon) Calculation

The Mean Apogee Lilith formula is **unchanged** in v1.1. v1.0 values
were verified against Swiss Ephemeris (`SE_MEAN_APOG`) on five dates
spanning 1900-2050; maximum deviation was MAX_DELTA deg, well below the
documented 0.01 deg tolerance.

**Action required:** None. Existing v1.0 Lilith values remain valid.

See `docs/LILITH_DEFINITION.md` for the full definition and tolerance
justification.
```

**If branch == FORMULA-CORRECTION:**

```markdown
### Lilith (Black Moon) Calculation

The Mean Apogee Lilith formula has been **corrected** in v1.1 to match
Swiss Ephemeris's `SE_MEAN_APOG`. Values returned by
`get_lilith_position(jd)` and `calc_planet_position(jd, 12)` differ
from v1.0 by up to MAX_DELTA deg within the 1900-2050 range.

**Concrete examples:**

| Date              | v1.0 Lilith (deg) | v1.1 Lilith (deg) | Delta (deg) |
|-------------------|-------------------|-------------------|-------------|
| 1900-06-15 12 UT  | A.AAAAAA          | B.BBBBBB          | +/-C.CCCCCC |
| 2000-01-01 12 UT  | A.AAAAAA          | B.BBBBBB          | +/-C.CCCCCC |
| 2025-09-23 06 UT  | A.AAAAAA          | B.BBBBBB          | +/-C.CCCCCC |
| 2050-12-21 00 UT  | A.AAAAAA          | B.BBBBBB          | +/-C.CCCCCC |

**Action required:** Recompute any cached Lilith values produced by
v1.0. If you stored Ketu output (e.g. lunation timing arrays, ML
feature columns, aspect-window catalogues for Lilith) for downstream
consumption, regenerate them with v1.1.

**Downstream consumers (Kala etc.):** Lilith body index 12 is
unchanged; only the longitude returned for a given JD shifts within
the magnitude above. Positional arrays remain length-14; no schema
break.

See `docs/LILITH_DEFINITION.md` for the full definition, the new
constants, and the cross-check harness.
```

For the FORMULA-CORRECTION branch, populate the table with at least 3 dates from `08-04-SUMMARY.md`'s post-fix run. The v1.0 column is the OLD Ketu output (`83.3532 + 0.1114040803*d` evaluated at each date — compute via:
```python
from ketu.ephemeris.time import utc_to_julian
def old_lilith(jd): return (83.3532 + 0.1114040803 * (jd - 2451545.0)) % 360.0
```
inline). The v1.1 column is the NEW `get_lilith_position` output. The Delta column is `signed_circular_diff(v1_1, v1_0)` (note: this is direction-of-change of Ketu output, NOT Ketu-vs-swe — those are different things).

Both branches must:
- Use ASCII-only formatting
- Cross-link `docs/LILITH_DEFINITION.md`
- State the action required clearly ("None" or recipe)
- Use the same `MAX_DELTA` value as CHANGELOG.md (consistency invariant — research §Pitfall 5 "Tolerance theatre" applies to magnitude reporting too: same precision, same number)

Do NOT modify any prior version sections in `UPGRADING.md` (e.g. v0.x -> v1.0). Append-only.
  </action>
  <verify>
```bash
grep -E "v1\\.0\\s*->\\s*v1\\.1|## v1\\.0 to v1\\.1" UPGRADING.md && echo "v1.0->v1.1 SECTION PRESENT"
grep -F "Lilith" UPGRADING.md | head -5
grep -F "LILITH_DEFINITION.md" UPGRADING.md
grep -iE "action required" UPGRADING.md  # explicit action statement

# If FORMULA-CORRECTION branch, the table is populated (no placeholder rows):
! grep -F "A.AAAAAA" UPGRADING.md
! grep -F "B.BBBBBB" UPGRADING.md
! grep -F "C.CCCCCC" UPGRADING.md

# Magnitude consistency: same number appears in both files:
MAGNITUDE_CHANGELOG=$(grep -oE "[0-9]+\\.[0-9]{4,}" CHANGELOG.md | head -1)
MAGNITUDE_UPGRADING=$(grep -oE "[0-9]+\\.[0-9]{4,}" UPGRADING.md | head -1)
echo "CHANGELOG: $MAGNITUDE_CHANGELOG / UPGRADING: $MAGNITUDE_UPGRADING"
[ "$MAGNITUDE_CHANGELOG" = "$MAGNITUDE_UPGRADING" ] && echo "MAGNITUDES CONSISTENT" || echo "WARN: differing precision; verify manually"

# Pre-existing sections preserved:
git diff UPGRADING.md | grep -E "^-## v0|^-## .*1\\.0\\.0" && echo "FAIL: older sections changed" || echo "PRIOR SECTIONS PRESERVED"
```
  </verify>
  <done>
`UPGRADING.md` has a v1.0 -> v1.1 section with a Lilith subsection that explicitly states the required action (None or recipe). If FORMULA-CORRECTION branch, the per-date table is populated with real numbers (no placeholder text). Magnitudes in CHANGELOG.md and UPGRADING.md are formatted to the same precision.
  </done>
</task>

</tasks>

<verification>
- `CHANGELOG.md` v1.1.0 section has a Lilith entry with explicit numeric magnitude
- `UPGRADING.md` v1.0 -> v1.1 section has a Lilith subsection with stated action
- Both files cross-link `docs/LILITH_DEFINITION.md`
- If branch == FORMULA-CORRECTION, UPGRADING.md table is populated (no `A.AAAAAA` placeholders)
- The same magnitude number appears in CHANGELOG, UPGRADING, and `docs/LILITH_DEFINITION.md` History
- Older release entries in both files are untouched (`git diff` confirms append-only)
- mypy / pytest are not affected by these documentation-only changes; both still pass
</verification>

<success_criteria>
1. `CHANGELOG.md` has an explicit, magnitude-stating Lilith entry under v1.1.0.
2. `UPGRADING.md` has a Lilith subsection under v1.0 -> v1.1 with a clear action statement.
3. If FORMULA-CORRECTION branch: at least 3-row per-date table with real numbers in UPGRADING.md.
4. Magnitude precision is consistent across CHANGELOG, UPGRADING, and `LILITH_DEFINITION.md` History.
5. Existing release entries are append-only preserved.
</success_criteria>

<output>
After completion, create `.planning/phases/08-lilith-verification-fix/08-05-SUMMARY.md` containing:
- Branch executed (NO-OP or FORMULA-CORRECTION)
- The CHANGELOG diff added (verbatim)
- The UPGRADING diff added (verbatim)
- The single magnitude number used across all three documents (consistency proof)
- Confirmation that older sections of both files are unchanged (`git diff --stat` summary)
- Closing statement: "Phase 8 (Lilith Verification & Fix) complete. v1.1.0 release notes for Lilith are now finalized."
</output>
