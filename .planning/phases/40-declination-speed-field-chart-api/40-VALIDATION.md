---
phase: 40
slug: declination-speed-field-chart-api
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-17
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest tests/charts/ tests/composite/ tests/test_declination.py -x -q` |
| **Full suite command** | `pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds (full suite) |

> Coverage gate: `fail_under = 100` (pyproject.toml) — 100% required, zero `# pragma: no cover` allowed (per Phase 21 quality gate).

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/charts/ tests/composite/ tests/test_declination.py -x -q`
- **After every plan wave:** Run `pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green AND coverage 100%
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

> Task IDs are filled from the emitted PLAN.md files. The requirement → test mapping
> below is the binding contract; every requirement maps to an automated command.

| Requirement | Plan / Task | Threat Ref | Test Type | Automated Command | File Exists | Status |
|-------------|-------------|------------|-----------|-------------------|-------------|--------|
| DSPD-01 | 40-01 T2 / 40-02 T1 | — | unit | `pytest tests/charts/test_dtype.py tests/charts/test_compute_chart.py -q` | created by 40-02 T1 (test class) | ⬜ pending |
| DSPD-02 | 40-02 T1 | — | unit | `pytest tests/charts/test_compute_chart.py -k decl_speed_matches_scalar -q` | created by 40-02 T1 | ⬜ pending |
| DSPD-03 (synastry) | 40-03 T2 | — | unit | `pytest tests/synastry/ -k decl_speed -q` | created by 40-03 T2 | ⬜ pending |
| DSPD-03 (returns) | 40-02 T2 | — | unit | `pytest tests/returns/test_solar_return.py -k decl_speed -q` | created by 40-02 T2 | ⬜ pending |
| DSPD-03 (composite) | 40-03 T1 | — | unit | `pytest tests/composite/test_calculate_composite.py -k decl_speed -q` | created by 40-03 T1 | ⬜ pending |
| DSPD-04 | 40-01 T2 | — | unit | `pytest tests/charts/test_dtype.py -q` | ✅ (ratchet re-pin) | ⬜ pending |
| DSPD-05 | 40-01 T1 | — | unit | `pytest tests/test_declination.py -k standstill -q` | created by 40-01 T1 | ⬜ pending |
| DSPD-06 | 40-02 T2 | — | unit | `pytest tests/charts/test_chart_helpers.py -q` | created by 40-02 T2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 test scaffolds are folded into the implementing tasks (each behavior-adding
task is `tdd="true"` with an explicit `<behavior>` block — exact I/O is known from
RESEARCH.md, so RED→GREEN is deterministic). New test functions:

- [x] `tests/charts/test_compute_chart.py` — `TestBodyDeclSpeed` (40-02 T1): present-in-dtype, matches-scalar-FD (Δ=0), vectorised shape `(N,14)`, non-zero-finite — DSPD-01, DSPD-02
- [x] `tests/charts/test_chart_helpers.py` — `is_ascending_declination_chart` (40-02 T2): returns `int8`, shape `S+(14,)`, consistent with v1.5 scalar, neutral (`0`) at standstill, all three branches — DSPD-06
- [x] `tests/composite/test_calculate_composite.py` — `TestBodyDeclSpeed` (40-03 T1): shape `(14,)`, non-zero, finite, **differs from naïve parent-midpoint** (DSPD-03 anti-averaging ratchet)
- [x] `tests/test_declination.py` — `DECL_STANDSTILL_EPS` (40-01 T1): importable, value `0.001`, Sun-at-solstice neutral, Jupiter-in-motion not masked — DSPD-05
- [x] `tests/synastry/test_calculate_synastry.py` (40-03 T2) + `tests/returns/test_solar_return.py` (40-02 T2): pinning assertions that inherited charts carry finite non-zero `body_decl_speed` — DSPD-03

*Ratchet update (existing file): `tests/charts/test_dtype.py` — 5 locations re-pinned for the 16th field (DSPD-04, 40-01 T2).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (pure numerical, no I/O, no UI).*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved (planner, 2026-06-17) — 3 plans, every DSPD-01..06 mapped to an automated command.
