---
phase: 31-documentation-en-fr
plan: "05"
subsystem: docs
tags: [docs, chiron, v1.4, range, accuracy, clamping]
dependency_graph:
  requires: [30-02]
  provides: [DOC-16-chiron.md]
  affects: [docs/source/chiron.md]
tech_stack:
  added: []
  patterns: [markdown-edit]
key_files:
  created: []
  modified:
    - docs/source/chiron.md
decisions:
  - "ValueError example removed; replaced with silent-clamping code example (Phase 30 behavior change)"
  - "v1.4 badges use 'expanded in v1.4' / 'improved in v1.4' prose, mirroring existing (New in v1.3) pattern"
metrics:
  duration: "~8 minutes"
  completed: "2026-06-03T14:08:28Z"
  tasks_completed: 2
  files_modified: 1
---

# Phase 31 Plan 05: chiron.md v1.4 Update Summary

chiron.md updated with 1900-2100 range, 0.001214° accuracy, and Phase 30 clamping behavior replacing the stale ValueError example.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update Implementation Details table (range + accuracy rows) | 51b2de3 | docs/source/chiron.md |
| 2 | Rewrite Date Range and Error Behaviour section (clamping, not ValueError) | 19a4168 | docs/source/chiron.md |

## Changes Made

### Task 1 — Implementation Details table

**Valid date range row** (line 10): replaced stale `1950-01-01 to 2050-12-31 (Julian Days ~2433282 to ~2469807)` with `1900-01-01 to 2100-12-31 (Julian Days 2415020.5 to 2488069.5) — expanded in v1.4`.

**Position accuracy row** (line 11): replaced `max error 0.005695° (sub-arcminute, ~20 arcseconds)` with `max error 0.001214° (sub-arcminute, ~4 arcseconds) — improved in v1.4`.

Both values are exact from Phase 30-02: jd_start=2415020.5, jd_end=2488069.5, max|Δλ|=0.001214°.

### Task 2 — Date Range and Error Behaviour section

Replaced the paragraph "Requesting Chiron outside 1950-2050 raises a `ValueError`" and the raising code example with:

- New intro sentence: "Chiron's embedded coefficients cover **1900-01-01 to 2100-12-31** (expanded in v1.4). Input outside this range is **silently clamped** to the nearest segment boundary — no `ValueError` is raised."
- New code example showing clamped call with comment `# Out-of-range JD: result is clamped to the nearest boundary (no exception)`.
- Accuracy in prose updated: `0.005695° (about 20 arcseconds)` → `0.001214° (about 4 arcseconds)`.

The old `# This raises ValueError: JD outside Chiron's supported range` comment and old `long(2300000.0, 13)` raising call are fully removed.

## Verification Results

| Check | Result |
|-------|--------|
| `grep -n "ValueError" chiron.md` | 1 hit — only the "no `ValueError` is raised" clamping note (correct) |
| `grep -n "1950\|2050\|0.005695" chiron.md` | 0 hits |
| `grep -n "clamp" chiron.md` | 3 hits (section prose + 2 code comment lines) |
| `grep -n "1900" chiron.md` | 3 hits (table row + section prose + code comment) |
| `grep -n "2100" chiron.md` | 3 hits |
| `grep -n "0.001214" chiron.md` | 2 hits (table row + section prose) |
| `grep -ni "kala" chiron.md` | 0 hits |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- `/home/loc/workspace/ketu/docs/source/chiron.md` — FOUND
- Commit `51b2de3` — FOUND (Task 1)
- Commit `19a4168` — FOUND (Task 2)
- All grep verifications pass (see table above)
