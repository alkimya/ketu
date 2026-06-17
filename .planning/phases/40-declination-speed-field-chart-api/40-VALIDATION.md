---
phase: 40
slug: declination-speed-field-chart-api
status: draft
nyquist_compliant: false
wave_0_complete: false
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

> Tasks are placeholders until the planner emits PLAN.md; the planner fills exact task IDs.
> The requirement → test mapping below is the binding contract the planner must satisfy.

| Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| DSPD-01 | — | N/A (pure numeric) | unit | `pytest tests/charts/test_dtype.py tests/charts/test_compute_chart.py -q` | ❌ W0 (new test file) | ⬜ pending |
| DSPD-02 | — | N/A | unit | `pytest tests/charts/test_compute_chart.py -k decl_speed_matches_scalar -q` | ❌ W0 | ⬜ pending |
| DSPD-03 (synastry) | — | N/A | unit | `pytest tests/synastry/ -k decl_speed -q` | ❌ W0 | ⬜ pending |
| DSPD-03 (returns) | — | N/A | unit | `pytest tests/returns/ -k decl_speed -q` | ❌ W0 | ⬜ pending |
| DSPD-03 (composite) | — | N/A | unit | `pytest tests/composite/test_calculate_composite.py -k decl_speed -q` | ❌ W0 | ⬜ pending |
| DSPD-04 | — | N/A | unit | `pytest tests/charts/test_dtype.py -q` | ✅ (ratchet re-pin) | ⬜ pending |
| DSPD-05 | — | N/A | unit | `pytest tests/test_declination.py -k standstill_eps -q` | ❌ W0 | ⬜ pending |
| DSPD-06 | — | N/A | unit | `pytest tests/charts/ -k ascending_declination_chart -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

New test functions are needed — no existing file covers these behaviors:

- [ ] `tests/charts/test_compute_chart.py` — `TestBodyDeclSpeed`: present-in-dtype, matches-scalar-FD (Δ=0), vectorised shape `(N,14)`, non-zero-finite (anti zero-fill ratchet) — DSPD-01, DSPD-02
- [ ] `tests/composite/test_calculate_composite.py` — `TestBodyDeclSpeed`: shape `(14,)`, non-zero, **differs from naïve parent-midpoint** (DSPD-03 anti-averaging ratchet), finite
- [ ] `tests/test_declination.py` — `DECL_STANDSTILL_EPS` importable from `ketu.calculations`, value pinned to `0.001`, Sun-at-solstice classifies neutral, Jupiter-in-motion not masked — DSPD-05
- [ ] `tests/charts/` — `is_ascending_declination_chart`: returns `int8`, shape `S+(14,)`, consistent with v1.5 scalar, neutral (`0`) at standstill — DSPD-06
- [ ] `tests/synastry/` + `tests/returns/` — pinning assertions that inherited charts carry finite non-zero `body_decl_speed` — DSPD-03

*Ratchet update (existing file): `tests/charts/test_dtype.py` — 5 locations re-pinned for the 16th field (DSPD-04).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

*All phase behaviors have automated verification (pure numerical, no I/O, no UI).*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
