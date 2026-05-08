---
phase: 13
slug: doc-gates-and-ci-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-08
revised: 2026-05-08
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
| **Full suite command**| `interrogate ketu/ && python -m numpydoc lint <files> && pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds (gates ~3s, full pytest ~25s)              |

---

## Sampling Rate

- **After every task commit:** Run the relevant gate (`interrogate ketu/` for docstring-fix tasks; `python -m numpydoc lint <files>` for numpydoc-fix tasks).
- **After every plan wave:** Full suite (interrogate + numpydoc + pytest).
- **Before `/gsd-verify-work`:** Full suite must be green; CI on the phase branch must be green; synthetic-gap negative test (Wave 0) confirmed.
- **Max feedback latency:** 30 seconds.

---

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
| -------- | ---- | ---- | ----------- | ---------- | --------------- | --------- | ----------------- | ----------- | ------ |
| 13-01-01 | 01   | 1    | OPS-01      | —          | N/A             | unit      | `pip install -e ".[dev]"` exits 0 AND `python -c "import interrogate, numpydoc"` exits 0 | ✅          | ⬜ pending |
| 13-01-02 | 01   | 1    | OPS-01      | —          | N/A             | unit      | `python -m interrogate ketu/` exits 0 with score ≥95% (4 placidus.py docstrings landed) | ✅          | ⬜ pending |
| 13-02-01 | 02   | 2    | OPS-01      | —          | N/A             | ci        | `Doc coverage gate (interrogate ≥95%)` step on Plan 02 PR shows green on Python 3.13 | ❌ W0       | ⬜ pending |
| 13-02-02 | 02   | 2    | OPS-01      | —          | N/A             | local     | `make doc-gates` exits 0 locally (interrogate green; numpydoc not yet wired but Makefile target invokes it cleanly) | ✅          | ⬜ pending |
| 13-03-01 | 03   | 2    | OPS-02      | —          | N/A             | unit      | `[tool.numpydoc_validation]` block parses; `'GL01'` ∈ checks; `\.lunar_calendar$` and `\._` ∈ exclude | ✅          | ⬜ pending |
| 13-03-02 | 03   | 2    | OPS-02      | —          | N/A             | unit      | `python -m numpydoc lint ketu/complex.py ketu/calculations.py ketu/cycles/calculator.py` produces ZERO output AND `pytest tests/ -q --no-cov` AND `mypy --strict` green | ✅          | ⬜ pending |
| 13-03-03 | 03   | 2    | OPS-02      | —          | N/A             | unit      | `python -m numpydoc lint ketu/__init__.py ketu/__main__.py ketu/core.py ketu/display.py ketu/cycles/__init__.py ketu/ephemeris/__init__.py` produces ZERO output AND non-standard sections folded into `Notes` | ✅          | ⬜ pending |
| 13-04-01 | 04   | 3    | OPS-02      | —          | N/A             | ci        | `tests.yml` has `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step with `continue-on-error: true`, gated to 3.13, AND YAML still parses | ❌ W0       | ⬜ pending |
| 13-05-01 | 05   | 4    | OPS-01, OPS-02 | —       | N/A             | grep      | Verify-only sweep: `grep -rni "interrog\|numpydoc\|≥95\|95%" CHANGELOG.md README.md docs/source/` returns zero hits OR only "(enforced by CI)" matches | ✅          | ⬜ pending |
| 13-05-02 | 05   | 4    | OPS-01, OPS-02 | —       | N/A             | grep      | README has the positive-add paragraph describing the gates as currently configured (interrogate blocking, numpydoc warning until v1.2.0) | ✅          | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Notes on task IDs:**
- Plan 01 has 2 tasks (`13-01-01` deps + interrogate config; `13-01-02` placidus.py docstrings).
- Plan 02 has 2 tasks (CI step wiring + Makefile target).
- Plan 03 has 3 tasks: (1) numpydoc config in pyproject.toml; (2) fix `complex.py` + `calculations.py` + `cycles/calculator.py`; (3) fix the 6 remaining files (`__init__.py`, `__main__.py`, `core.py`, `display.py`, `cycles/__init__.py`, `ephemeris/__init__.py`).
- Plan 04 has 1 task: wire numpydoc CI step (warning-only).
- Plan 05 has 2 tasks (verify-only public-doc sweep + positive-add README paragraph).

---

## Wave 0 Requirements

- [ ] No new test files required — gates ARE the test infrastructure for this phase.
- [ ] `pip install -e ".[dev]"` must succeed once Plan 01 lands (validates dev group syntax).

*Existing pytest/coverage infrastructure covers nothing new in this phase — Phase 13 adds CI-level gates, not application tests.*

---

## Manual-Only Verifications

| Behavior                                        | Requirement | Why Manual                                        | Test Instructions                                                                                              |
| ----------------------------------------------- | ----------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Synthetic-gap CI behavior (interrogate fails)   | OPS-01      | Requires pushing a branch and observing CI run    | Branch off main → remove a docstring from `ketu/cycles/calculator.py` → push → observe `Doc coverage gate (interrogate ≥95%)` step red on Python 3.13 leg → delete branch. Document result in Plan 02's SUMMARY. |
| Synthetic-warning CI behavior (numpydoc)        | OPS-02      | Requires pushing a branch and observing CI run    | Branch off main → delete a `Returns` section in `ketu/calculations.py` → push → observe `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step on Python 3.13 prints the issue, shows yellow/green (NOT red) because of `continue-on-error: true`, build overall stays green → delete branch. Document result in Plan 04's SUMMARY. |
| numpydoc warning visibility in CI logs          | OPS-02      | Requires inspecting GitHub Actions log UI         | Push the Phase 13 branch → open the `Doc style audit (numpydoc — warning only, blocking from v1.2.0)` step → confirm `Validating N files...` line is printed and step is green (Plan 03 cleared every issue, so no warnings expected on the clean baseline). |
| README/CHANGELOG reformulation reads naturally  | OPS-01, OPS-02 | Subjective phrasing review                     | Sophie/user reads the diff in Plan 05, confirms "(enforced by CI)" reads cleanly in context.                   |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or are explicitly listed under "Manual-Only Verifications"
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (Plan 02 Task 1 is CI-only — covered by Manual-Only Verifications + the synthetic-gap negative test)
- [ ] Wave 0: no new test infrastructure required; synthetic-gap negative tests are documented under Manual-Only Verifications
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
