---
phase: 13
slug: doc-gates-and-ci-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-08
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Phase 13 is pure ops/CI work — validation = the gates themselves run green locally and in CI, plus a synthetic-gap negative test proves the gates fail correctly.

---

## Test Infrastructure

| Property              | Value                                                  |
| --------------------- | ------------------------------------------------------ |
| **Framework**         | pytest 7.x (existing) + interrogate 1.7.0 + numpydoc 1.10.0 |
| **Config file**       | `pyproject.toml` (`[tool.interrogate]`, `[tool.numpydoc_validation]`) |
| **Quick run command** | `interrogate ketu/` (≤2s)                              |
| **Full suite command**| `interrogate ketu/ && python -m numpydoc validate ketu/ && pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds (gates ~3s, full pytest ~25s)              |

---

## Sampling Rate

- **After every task commit:** Run the relevant gate (`interrogate ketu/` for docstring-fix tasks; `python -m numpydoc validate ketu/<module>.py` for numpydoc-fix tasks).
- **After every plan wave:** Full suite (interrogate + numpydoc + pytest).
- **Before `/gsd-verify-work`:** Full suite must be green; CI on the phase branch must be green; synthetic-gap negative test (Wave 0) confirmed.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| -------- | ---- | ---- | ----------- | ---------- | --------------- | --------- | ----------------- | ----------- | ------ |
| 13-01-01 | 01   | 1    | OPS-01      | —          | N/A             | unit      | `pip install -e ".[dev]"` exits 0 | ✅          | ⬜ pending |
| 13-01-02 | 01   | 1    | OPS-01      | —          | N/A             | unit      | `interrogate ketu/ --fail-under=95` exits 0 | ✅          | ⬜ pending |
| 13-02-01 | 02   | 2    | OPS-01      | —          | N/A             | ci        | CI step "Doc coverage (interrogate)" green on PR | ❌ W0       | ⬜ pending |
| 13-02-02 | 02   | 2    | OPS-01      | —          | N/A             | ci        | Synthetic-gap branch fails CI (negative test) | ❌ W0       | ⬜ pending |
| 13-03-01 | 03   | 2    | OPS-02      | —          | N/A             | unit      | `python -m numpydoc validate ketu/` reports 0 issues | ✅          | ⬜ pending |
| 13-04-01 | 04   | 3    | OPS-02      | —          | N/A             | ci        | CI step "Numpydoc validate (warning)" runs; build green | ❌ W0       | ⬜ pending |
| 13-04-02 | 04   | 3    | OPS-02      | —          | N/A             | ci        | Synthetic-gap branch surfaces warning in log | ❌ W0       | ⬜ pending |
| 13-05-01 | 05   | 3    | OPS-01, OPS-02 | —       | N/A             | grep      | `grep -rn "interrogate.*95\|numpydoc validate" CHANGELOG.md README.md docs/source/` returns only "(enforced by CI)" matches | ✅          | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] No new test files required — gates ARE the test infrastructure for this phase.
- [ ] `pip install -e ".[dev]"` must succeed once Plan 01 lands (validates dev group syntax).
- [ ] Synthetic-gap negative test: a throwaway branch removes one docstring → confirm CI fails on `interrogate` step. Run once, document result, delete branch.

*Existing pytest/coverage infrastructure covers nothing new in this phase — Phase 13 adds CI-level gates, not application tests.*

---

## Manual-Only Verifications

| Behavior                                        | Requirement | Why Manual                                        | Test Instructions                                                                                              |
| ----------------------------------------------- | ----------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Synthetic-gap CI behavior (interrogate fails)   | OPS-01      | Requires pushing a branch and observing CI run    | Branch off main → remove a docstring from `ketu/cycles/calculator.py` → push → observe `Doc coverage` step red → delete branch. |
| numpydoc warning visibility in CI logs          | OPS-02      | Requires inspecting GitHub Actions log UI         | Push the Phase 13 PR → open the `Numpydoc validate (warning)` step → confirm issue count is printed and step is yellow/green (not red). |
| README/CHANGELOG reformulation reads naturally  | OPS-01, OPS-02 | Subjective phrasing review                     | Sophie/user reads the diff in Plan 05, confirms "(enforced by CI)" reads cleanly in context.                   |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (synthetic-gap negative tests)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
