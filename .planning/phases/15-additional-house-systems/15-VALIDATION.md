---
phase: 15
slug: additional-house-systems
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-09
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`pyproject.toml [tool.pytest.ini_options]`) |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `pytest tests/houses/ -x -v` |
| **Full suite command** | `pytest tests/ --cov=ketu.houses --cov-fail-under=95` |
| **Estimated runtime** | ~30 seconds (full suite ~90 seconds) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/houses/ -x -v`
- **After every plan wave:** Run `pytest tests/ --cov=ketu.houses --cov-fail-under=95`
- **Before `/gsd-verify-work`:** Full suite must be green + `numpydoc validate ketu/houses/` + `interrogate ketu/houses/ -f 95`
- **Max feedback latency:** ~30 seconds (test suite per task)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | HOU2-05 (snapshot foundation) | — | Idempotent snapshot regen; oracle reproducibility | unit + integration | `pytest tests/houses/test_oracle_smoke.py -x` | ❌ W0 | ⬜ pending |
| 15-01-02 | 01 | 1 | HOU2-01..03 (DTYPE bump) | — | DTYPE width U10→U16 non-breaking on read paths | unit | `pytest tests/houses/test_dtype.py -x` | ✅ existing | ⬜ pending |
| 15-02-01 | 02 | 2 | HOU2-01 (whole_sign registered) | — | N/A | unit | `pytest tests/houses/test_whole_sign.py::test_registered -x` | ❌ W0 | ⬜ pending |
| 15-02-02 | 02 | 2 | HOU2-01 (whole_sign algo bit-exact) | — | N/A | algorithm-tier | `pytest tests/houses/test_whole_sign.py::test_algorithm_matches_oracle_armc -x` | ❌ W0 | ⬜ pending |
| 15-02-03 | 02 | 2 | HOU2-02 (equal registered) | — | N/A | unit | `pytest tests/houses/test_equal.py::test_registered -x` | ❌ W0 | ⬜ pending |
| 15-02-04 | 02 | 2 | HOU2-02 (equal algo bit-exact) | — | N/A | algorithm-tier | `pytest tests/houses/test_equal.py::test_algorithm_matches_oracle_armc -x` | ❌ W0 | ⬜ pending |
| 15-02-05 | 02 | 2 | HOU2-01/02 (polar safety no-NaN) | — | Polar-safe by construction | unit | `pytest tests/houses/test_polar_safety.py -x -k whole_sign` | ✅ existing to extend | ⬜ pending |
| 15-03-01 | 03 | 2 | HOU2-03 (regiomontanus registered) | — | N/A | unit | `pytest tests/houses/test_regiomontanus.py::test_registered -x` | ❌ W0 | ⬜ pending |
| 15-03-02 | 03 | 2 | HOU2-03 (regio algo bit-exact) | — | N/A | algorithm-tier | `pytest tests/houses/test_regiomontanus.py::test_algorithm_matches_oracle_armc -x` | ❌ W0 | ⬜ pending |
| 15-03-03 | 03 | 2 | HOU2-03 (polar NaN propagation) | — | NaN at \|lat\| ≥ 90 - eps_mean(jd); HighLatitudeError on raise | unit + integration | `pytest tests/houses/test_regiomontanus.py::test_yields_nan_above_polar_circle -x` | ❌ W0 | ⬜ pending |
| 15-03-04 | 03 | 2 | HOU2-03 (polar_fallback integration) | — | polar_fallback="porphyry" routes correctly | integration | `pytest tests/houses/test_integration.py -x -k regio` | ✅ existing to extend | ⬜ pending |
| 15-04-01 | 04 | 2 | HOU2-04 (CLI list 6 systems) | — | N/A | CLI | `pytest tests/cli/test_introspection.py::TestListHouseSystems -x` | ✅ existing to extend | ⬜ pending |
| 15-04-02 | 04 | 2 | HOU2-04 (CLI parser accepts new systems) | — | Invalid system rejected; valid systems accepted | CLI | `pytest tests/cli/test_houses_cmd.py -x -k system` | ✅ existing to invert | ⬜ pending |
| 15-04-03 | 04 | 2 | HOU2-05 (end-to-end oracle gate) | — | Snapshot match ≤1 arcmin on 7 tight charts | end-to-end | `pytest tests/houses/test_oracle_smoke.py::test_loaded_reference_snapshot_matches_oracle -x` | ✅ existing | ⬜ pending |
| 15-04-04 | 04 | 2 | OPS-01/02 (doc gates clean on new code) | — | numpydoc + interrogate green on ketu/houses/ | doc | `numpydoc validate ketu/houses/ && interrogate ketu/houses/ -f 95` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/houses/test_whole_sign.py` — stubs for HOU2-01 (registry, formula, polar safety, vectorization, sign-boundary)
- [ ] `tests/houses/test_equal.py` — stubs for HOU2-02 (registry, formula, polar safety, vectorization, constant-step invariant)
- [ ] `tests/houses/test_regiomontanus.py` — stubs for HOU2-03 (registry, formula, **polar NaN**, vectorization, integration with polar_fallback)
- [ ] `scripts/snapshot_reference_charts.py` — snapshot regeneration script (referenced in `tests/houses/conftest.py:248-252` but never committed in v1.1)
- [ ] Regenerate `tests/houses/fixtures/reference_charts.json` with 6 systems × 10 charts = 60 blocks
- [ ] Extend `tests/houses/conftest.py:SYSTEM_BYTES` with `b"W"`, `b"E"`, `b"R"`
- [ ] Invert legacy `tests/cli/test_houses_cmd.py:53-59` test (was rejecting `regiomontanus`)
- [ ] No new framework install — pytest, numpy, pyswisseph (test-only) already in `[project.optional-dependencies].test`

---

## Manual-Only Verifications

*All phase behaviors have automated verification. Reykjavik Regio drift tolerance is empirically measured during Plan 15-03 development; the value is then pinned as an automated test parameter — no manual gate at execution time.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (snapshot script, 3 test files, SYSTEM_BYTES extension)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s (per task) / < 90s (per wave)
- [ ] `nyquist_compliant: true` set in frontmatter (after planner produces PLAN.md files)

**Approval:** pending (will flip to `nyquist_compliant: true` after gsd-plan-checker green pass)

---

## Sampling Strategy Notes (from RESEARCH §9)

**10 reference charts cover :**
- Equator (lat=0°) — degenerate ASC formula
- Mid-latitudes north (Greenwich 51.5°, Paris 48.86°, NY 40.7°, Tokyo 35.7°)
- Southern hemisphere (Sydney -33.9°, Buenos Aires -34.6°)
- Time boundaries (1900, J2000, 2050)
- Pre-polar (Reykjavik 64.1°)
- Polar (lat=70°, 80°) — finite for Whole Sign/Equal, NaN for Regiomontanus

**Tolerance gates:**
- Algorithm tier (vs `swe_oracle_armc`): `1e-6°` (machine precision)
- End-to-end snapshot: `1 arcmin` on 7 tight non-polar charts
- Reykjavik Regio: empirically measured (estimated 2-5 arcmin), pinned as exception
- Polar Regio: NaN at `|lat| ≥ 90 - eps_mean(jd)`

**Edge case to add:** ASC = 0.0° exact (sign boundary) — `floor(0/30)*30 = 0` for Whole Sign, `cusp_1 = 0` for Equal. Not buggy by design but pinned regression test recommended (per Pitfall 3 in RESEARCH).
