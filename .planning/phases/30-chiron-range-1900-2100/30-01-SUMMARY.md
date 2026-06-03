---
phase: 30-chiron-range-1900-2100
plan: "01"
subsystem: ephemeris/chiron
tags: [chiron, chebyshev, spike, accuracy, 1900-2100]
dependency_graph:
  requires: [29-01]
  provides: [degree_final=10, seg_len=32.0, max_delta_lon=0.001214deg, gate=PASS]
  affects: [30-02]
tech_stack:
  added: []
  patterns: [ephemeral-spike, in-memory-override, dense-edge-sampling]
key_files:
  created: []
  modified:
    - .planning/PROJECT.md
    - .planning/STATE.md
decisions:
  - "[Phase 30-01] degree_final=10, seg_len=32.0: gate PASS < 0.01 deg over 1900-2100 (max 0.001214 deg, margin 8.2x)"
metrics:
  duration: "~3 minutes (generation 2283 segs + validation + decision recording)"
  completed: "2026-06-03"
  tasks_completed: 3
  files_modified: 2
---

# Phase 30 Plan 01: Chiron 1900-2100 Accuracy Spike Summary

## One-liner

degree=10 / seg=32d Chebyshev holds max|delta-lon|=0.001214 deg over full 1900-2100 range — gate PASS with 8.2x margin, no parameter change needed.

## What Was Done

Executed the blocking accuracy spike for Phase 30 before any `.npz` regeneration. Created an ephemeral script at `/tmp/chiron_spike_30.py` (never committed), ran the full measurement pipeline, recorded the verdict in the decision log, and deleted the spike script.

### Pre-flight build check (Task 1)

- `pyswisseph` imported successfully
- `swe.CHIRON = 15` confirmed
- Oracle at J2000.0: `retflag=260` (Moshier fallback, expected and acceptable)
- Oracle at 1900-01-01 (JD=2415020.5): `retflag=260`, lon=258.8960 deg — PASS
- Oracle at 2100-01-01 (JD=2488069.5): `retflag=260`, lon=241.8599 deg — PASS

### degree=10 measurement over 1900-2100 (Task 1)

Generator invoked via in-memory override (`g._DEGREE=10`, `g._N_FIT=18`, `g._SEG_LEN=32.0`) — no edit to committed `tools/gen_chiron_coeffs.py`.

- Total range: 73049 days
- n_segs: 2283 (ceil(73049/32)) — confirmed

#### Dense edge report: segments 0-10 (1900-1910), 500 pts/seg

| seg | JD start   | max delta-lon |
|-----|------------|---------------|
| 0   | 2415020.5  | 0.000005 deg  |
| 1   | 2415052.5  | 0.000004 deg  |
| 2   | 2415084.5  | 0.000007 deg  |
| 3   | 2415116.5  | 0.000011 deg  |
| 4   | 2415148.5  | 0.000013 deg  |
| 5   | 2415180.5  | 0.000010 deg  |
| 6   | 2415212.5  | 0.000006 deg  |
| 7   | 2415244.5  | 0.000004 deg  |
| 8   | 2415276.5  | 0.000006 deg  |
| 9   | 2415308.5  | 0.000010 deg  |
| 10  | 2415340.5  | 0.000012 deg  |

The perihelion-aftermath edge (1900-1910) is well-behaved: max 0.000013 deg across all 11 segments — two orders of magnitude below the 0.01 deg gate.

#### Full validation (200 pts/seg, 2283 segments)

- `max|delta-lon| = 0.001214 deg` — GATE PASS (< 0.01 deg, margin 8.2x)
- `max|delta-lat| = 0.001079 deg`
- `max|delta-dist| = 0.000000184 AU`
- `worst_jd = 2424624.04` (1926-04-18, segment 300) — unrelated to perihelion aftermath

### Degree decision branch (Task 2)

Gate PASS at degree=10 on first try. No fallback to degree=12 needed. Decision:

```
degree_final = 10
seg_len_final = 32.0
max|delta-lon| = 0.001214 deg
worst_jd = 2424624.04  (1926-04-18)
GATE = PASS
```

### Decision log recorded (Task 3)

Gate PASSED — autonomous path taken (no user pause required).

- `PROJECT.md` Key Decisions table: new row `[Phase 30-01]` appended
- `STATE.md` Decisions section: new bullet `[Phase 30-01]` appended
- Spike script deleted: `rm -f /tmp/chiron_spike_30.py`
- `git status --porcelain tools/ ketu/ tests/ pyproject.toml` returned EMPTY

## Key Parameters for Plan 30-02

Plan 30-02 must regenerate `ketu/data/chiron_coeffs.npz` with:

| Parameter | Value |
|-----------|-------|
| `degree_final` | 10 |
| `seg_len_final` | 32.0 days |
| `_N_FIT` | 18 (degree + 8) |
| `jd_start` | 2415020.5 (1900-01-01 UTC) |
| `jd_end` | 2488069.5 (2100-01-01 UTC) |
| `n_segs` | 2283 |
| `last_seg_actual_len` | 25.0 days (73049 % 32) |
| Expected coefficient shape | (2283, 11) |
| Expected `seg_starts` shape | (2283,) |

The `actual_len` fix (Phase 24-04) in `_eval_chiron_qty` reads `jd_end` from the `.npz` directly — no code change needed in `chiron.py`.

## Deviations from Plan

None — plan executed exactly as written. degree=10 GATE passed on first attempt; no degree=12 fallback needed; no seg_len reduction needed; no escalation.

## Self-Check

**Files created:**
- `.planning/phases/30-chiron-range-1900-2100/30-01-SUMMARY.md` — this file

**Files modified:**
- `.planning/PROJECT.md` — Key Decisions row `[Phase 30-01]` appended at line 198
- `.planning/STATE.md` — Decision bullet `[Phase 30-01]` appended after Phase 29-01 entry

**Commit:** 6fab1c0 — `feat(30-01): record Chiron 1900-2100 spike verdict — degree=10 PASS`

**Spike script:** deleted from `/tmp/chiron_spike_30.py`; never staged under repo tree

**Source gate:** `git status --porcelain tools/ ketu/ tests/ pyproject.toml` = EMPTY (confirmed)

## Self-Check: PASSED
