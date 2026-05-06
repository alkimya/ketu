# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — Phase 9 (Configurable Aspects)

## Current Position

Phase: 9 of 12 (Configurable Aspects) — **IN PROGRESS**
Plan: 1 of 6 complete (09-03 done; 09-01, 09-02, 09-04a, 09-04b, 09-05 remaining)
Status: Plan 09-03 complete — `core.aspects` v1.1 invariant locked: length 14 + dtype.names + per-row name/angle/coef + sha256 byte fingerprint `c5bd1773...9afb359`. Mutation test verified surgical row-drift detection. 423 tests green, no regressions; `core.aspects` itself unchanged (append-only contract preserved)
Last activity: 2026-05-06 — Plan 09-03 executed; commit `e5a529d` (test) on `gsd/v1.1-milestone`

Progress: [████░░░░░░] v1.0 complete; v1.1 1/5 phases complete (Phase 8: 5/5 plans), Phase 9: 1/6 plans

## Performance Metrics

**Velocity (v1.0 reference baseline):**

- Total plans completed (v1.0): 16
- v1.1 plans completed: 6 (Phase 8: 08-01, 08-02, 08-03, 08-04, 08-05; Phase 9: 09-03)

**By Phase (v1.1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 8. Lilith Verification & Fix | 5 | ~22m 18s | ~4m 28s |
| 9. Configurable Aspects | 1 | ~1m 35s | ~1m 35s |
| 10. Houses Module | 0 | — | — |
| 11. CLI Refactor & Integration | 0 | — | — |
| 12. Release Preparation v1.1.0 | 0 | — | — |

*Updated after each plan completion*
| Phase 08 P01 | 2min | 1 tasks | 1 files |
| Phase 08 P02 | 2m 5s | 2 tasks | 1 files |
| Phase 08 P03 | 4m 31s | 2 tasks | 1 files |
| Phase 08 P04 | 10m 1s | 4 tasks | 4 files |
| Phase 08 P05 | 3m 41s | 2 tasks | 2 files |
| Phase 09 P03 | 1m 35s | 1 tasks | 1 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Recent decisions affecting current work:

- Default aspects = 5 majors in v1.1 — Pro/classical default; ML harmonics opt-in via `--harmonics`
- Houses module starts with Placidus + Koch — two systems prove extensibility; others plug in later
- Verify Lilith before fixing — confirm bug exists and quantify error before changing formula
- Vectorize everything new — houses + harmonics must be batchable over date arrays
- `core.aspects` stays length-14 append-only (Kala uses positional indexing — non-negotiable)
- `pysweph>=2.10.3.6` is test-only dependency (AGPL-safe; no runtime deps added)
- [Phase 08]: Test-only optional extra pattern: AGPL-licensed pysweph lives under [project.optional-dependencies].test, never in [project].dependencies — proven empirically with two-venv install test
- [Phase 08-01]: Investigation-first ordering enforced — `docs/LILITH_DEFINITION.md` (contract for harness/fix) lands BEFORE any code change; tolerance derived arithmetically (0.01 deg ≈ 129 min mean apogee drift), not a round-number convention; History section pre-seeded with literal Plan 04 sentinel for atomic update
- [Phase 08]: Plan 04 branch = FORMULA-CORRECTION (empirical max |delta| = 179.94 deg, ~18000x tolerance); suspected root cause: epoch constant 83.3532 off by 180 deg (Ketu computes perigee, swe expects apogee); residual after +180 deg correction is 0.111 deg (still 11x tolerance) -- secondary frame/rate term to address
- [Phase 08]: Cross-check harness pattern locked: pytest.importorskip module-level gate (no binding) + separate import for mypy --strict + manual swe.version check (since pysweph __version__ is int date stamp) + always-pass diagnostic Python script alongside assertion test to capture deltas regardless of pass/fail; defensive index-based tuple unpack for foreign C-extension return shape
- [Phase 08-04]: Single source of truth for Lilith constants — 5 private module-level constants `_LILITH_MEAN_*` and `_LILITH_PERTURB_*` in `ketu/ephemeris/orbital.py`; all 4 plumbing sites (orbital.py x2, planets.py x2) reference them by name. Eliminates v1.0's 4-site duplication drift risk
- [Phase 08-04]: Pure linear correction insufficient — secondary residual ~0.124 deg has dominant 1095-day (3 sidereal years) sinusoidal signature. v1.1 formula adds one trig perturbation term (linear secular + 1 sin), fitted via joint Nelder-Mead NLS over 55K daily samples 1900-2050. Pattern: when a mean-element formula misses external reference by sinusoidal residual, add the dominant FFT-identified perturbation
- [Phase 08-04]: REGRESSION_TOLERANCE_DEG = 0.005 — half of user-facing 0.01 deg, ~1.85x post-fit max (0.002693). Pins agreement margin without hardcoding Ketu output (research §"Anti-patterns" preserved). Test-only threshold; production users still bound by 0.01 deg contract
- [Phase 08-04]: avg_speeds[12] uses `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)` — preserves 6-decimal `avg_speeds` dict convention while inheriting from source-of-truth named constant
- [Phase 08]: [Phase 08-05] Magnitude consistency invariant locked across CHANGELOG/UPGRADING/LILITH_DEFINITION at 6-decimal precision: pre-fix 179.936579 deg (user-visible breaking-change), post-fix 0.002693 deg (5 dates) and 0.007815 deg (55K daily samples) -- both <0.01 deg tolerance. Per-date table in UPGRADING live-computed from get_lilith_position rather than copied from Plan 04 SUMMARY
- [Phase 08]: [Phase 08-05] Deviation from pure Chapront secular linear stated transparently in CHANGELOG and UPGRADING (NOT minimized): both files explicitly state v1.1 ships 'linear secular term + 1 sin() perturbation', not a raw ELP-2000 polynomial. Per execution-context note from Wave 3 orchestrator
- [Phase 09]: [Phase 09-03]: core.aspects invariant pinned via sha256 byte fingerprint (c5bd1773...9afb359) + per-row name/angle/coef + length 14 + dtype.names. Mutation test verified surgical row-drift detection. Defense-in-depth pattern: any future drift in rows 0-13 fails with informative messages identifying the affected row index

### From v1.0 milestone (carried context)

- Pure NumPy contract: no new runtime deps allowed
- Mypy strict mode enforced in CI; numpydoc-style docstrings on public API; interrogate ≥95%
- Trusted publishing OIDC configured for PyPI releases
- Test isolation pattern: pytest tmp_path fixture for file I/O
- Error message convention: ValueError with received value + valid options
- Two-layer caching is intentional: LRU for single-point, EphemerisCache for batch
- v1.0 milestone roadmap archived to `.planning/milestones/v1.0-ROADMAP.md`

### Roadmap Evolution

- v1.0 milestone complete (8 phases including 2.1 insertion, 16 plans, ketu 1.0.0 on PyPI 2026-02-12)
- v1.1 milestone planned: 5 phases (8-12), 33 requirements, parallelizable 8/9/10 then 11 then 12

### Pending Todos

None yet.

### Blockers/Concerns

- **Kala aspect-count dependency unverified** (Phase 9 risk) — confirm with Kala maintainer that `KetuAdapter` either tolerates `EXTENDED` opt-in or is updated before Phase 9 merge
- **LST/obliquity precision audit** (Phase 10 first task) — current `ephemeris/time.py` tuned for ~0.01°; houses need ~0.001°. Audit must precede implementation per HOU-01

## Session Continuity

Last session: 2026-05-06 (Plan 09-03 execution)
Stopped at: Completed `09-03-invariant-test-PLAN.md` (commit `e5a529d`). `core.aspects` v1.1 invariant locked in `tests/test_ketu.py::TestData`: length 14 + dtype.names + per-row name/angle/coef (with `pytest.approx(abs=1e-6)`) + sha256 byte fingerprint `c5bd177316ce98d428bee011a5b0f17ae247d1dee1e478c2389af51d39afb359`. Mutation test verified: row swap in `ketu/core.py` causes BOTH `test_aspects_structure` AND `test_aspects_byte_fingerprint` to fail with surgical messages identifying the drifted row index, then revert restores green. 423/423 tests passing on full suite, no regressions. `core.aspects` itself unchanged — append-only contract preserved per Phase 9 invariant. Plans 09-04a (calculator-refactor) and 09-04b (default-migration) now have machine-enforceable safety net for any future drift in rows 0-13. Note: plan referenced class name `TestCoreData`; actual class in `tests/test_ketu.py` is `TestData` — used existing class (no rename), tests landed correctly.
Resume file: None

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-06 — Plan 09-03 complete; Phase 9: 1/6 plans (~1m 35s). core.aspects invariant pinned via sha256 fingerprint; mutation test verified surgical row-drift detection; defense-in-depth pattern (length + dtype + per-row + bytes) established for structured-array invariants*
