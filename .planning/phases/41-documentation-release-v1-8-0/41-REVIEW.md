---
phase: 41-documentation-release-v1-8-0
reviewed: 2026-06-19T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - ketu/__init__.py
  - ketu/aspects/calculator.py
  - ketu/charts/core.py
  - ketu/houses/core.py
  - ketu/synastry/__init__.py
  - ketu/synastry/core.py
  - docs/source/conf.py
  - pyproject.toml
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 41: Code Review Report

**Reviewed:** 2026-06-19
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found (Info-only; no BLOCKER, no WARNING)

## Summary

Phase 41 is a documentation + release phase. Adversarial review of the eight
listed source files against base `044d72a` confirms the changes are confined to
exactly what the scope claimed, with no smuggled behavior change.

The `044d72a..HEAD` diff contains only the three version-string bumps
(`1.7.0` -> `1.8.0` in `ketu/__init__.py:57`, `docs/source/conf.py:14-15`,
`pyproject.toml:7`). The docstring name-clean edits landed earlier in commit
`c652576` (before the supplied base); I reviewed that commit's diff directly
since the scope explicitly asks whether those edits broke anything.

Verification performed (FORCE stance — tried to break it):

- **Version consistency:** All three source-of-truth files read `1.8.0`.
  `grep` finds no stray `1.7.0` anywhere in `ketu/` or the three release
  files. The only `1.7.0` hit (`pyproject.toml:46 interrogate>=1.7.0`) is an
  unrelated dependency pin, correctly left alone.
- **Runtime import:** `import ketu` succeeds and `ketu.__version__ == "1.8.0"`.
- **Doctest gate:** `pytest --doctest-modules` on the edited files plus
  `__init__.py` passes (3 collected, all green). The name-clean edits touched
  only prose in `Notes`/comment blocks; the executable `Examples` doctest in
  `calculate_aspects` (calculator.py:302-313) is byte-identical and still passes.
- **Identifier safety:** No code identifier, field name, dtype, signature, or
  control-flow line was altered. Every "Kala" -> "downstream consumer(s)"
  substitution is pure prose. No remaining `Kala` reference exists under
  `ketu/` (grep clean). Celestial-body names (Rahu/Ketu/Lilith/Chiron) are
  preserved verbatim.
- **numpydoc structure:** No section headers, underlines, or directive markers
  were changed by the substitutions; rST/MyST `conf.py` is untouched except the
  version pair. No line-length linter is configured (no black/ruff/flake8
  setting in any config file), so the slightly longer prose lines (max 87
  chars, all inside docstrings/comments) are not violations.

No correctness, security, or maintainability defect was found in the phase-41
changes. The two Info items below are pre-existing documentation staleness that
the name-clean edit passed over without touching — recorded for completeness and
accurately attributed to their origin commits, NOT as phase-41 regressions.

## Info

### IN-01: Stale "13-body axis" wording in CHART_DTYPE rationale (pre-existing)

**File:** `ketu/charts/core.py:22`
**Issue:** The numbered rationale reads "...for body ``i`` of the canonical
13-body axis." The axis has been 14 since the v1.3 D-08 Chiron ratchet — the
very next paragraph (lines 96-97) and the field comment (lines 91-94) correctly
state 14 with Chiron at index 13, so the document contradicts itself. This
wording predates phase 41: it originates in commit `b52154e`
(`feat(14-01): scaffold ketu.charts`) and was NOT introduced or altered by the
name-clean edit (`c652576`). It is therefore out of scope for this release
phase, recorded only so it is not lost.
**Fix:** In a future docs-touch, change "canonical 13-body axis" to "canonical
14-body axis" to match the field comment and the D-08 ratchet.

### IN-02: Stale "synastry indices 0..12" wording in SYNASTRY_DTYPE rationale (pre-existing)

**File:** `ketu/synastry/core.py:24`
**Issue:** Rationale point 1 reads "synastry indices 0..12 reuse
``ketu.core.bodies`` and indices 13..14 stand for ASC and MC." Post-D-08 the
canonical body axis runs 0..13 (Chiron at 13), with ASC=14 and MC=15 — exactly
as the field comment at lines 99-101 correctly documents ("13=Chiron, 14=ASC,
15=MC"). The "0..12 / 13..14" phrasing is the old 13-body mapping and
contradicts the corrected mapping a few lines down. This wording originates in
commit `fce8901` (`feat(16-01): create ketu.synastry skeleton`) and was NOT
touched by the phase-41 name-clean (`c652576`); it is out of scope for this
release phase.
**Fix:** In a future docs-touch, align to "indices 0..13 reuse
``ketu.core.bodies`` and indices 14..15 stand for ASC and MC."

---

_Reviewed: 2026-06-19_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
