# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — Phase 8 (Lilith Verification & Fix)

## Current Position

Phase: 8 of 12 (Lilith Verification & Fix)
Plan: 3 of 5 complete — next is Plan 04 (conditional formula fix, FORMULA-CORRECTION branch)
Status: Plan 08-03 complete (cross-check harness fails 5/5 with max |delta| = 179.94 deg — Lilith bug empirically confirmed); Plan 08-04 unblocked and must execute its FORMULA-CORRECTION branch
Last activity: 2026-05-06 — Plan 08-03 executed; harness `tests/test_lilith_cross_check.py` created (commits `2ff8c92`, `143072a`); empirical max |delta| = 179.936579 deg recorded in 08-03-SUMMARY.md

Progress: [███░░░░░░░] v1.0 complete; v1.1 1/5 phases (Phase 8: 3/5 plans)

## Performance Metrics

**Velocity (v1.0 reference baseline):**

- Total plans completed (v1.0): 16
- v1.1 plans completed: 3 (Phase 8: 08-01, 08-02, 08-03)

**By Phase (v1.1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 8. Lilith Verification & Fix | 3 | ~8m 36s | ~2m 52s |
| 9. Configurable Aspects | 0 | — | — |
| 10. Houses Module | 0 | — | — |
| 11. CLI Refactor & Integration | 0 | — | — |
| 12. Release Preparation v1.1.0 | 0 | — | — |

*Updated after each plan completion*
| Phase 08 P01 | 2min | 1 tasks | 1 files |
| Phase 08 P02 | 2m 5s | 2 tasks | 1 files |
| Phase 08 P03 | 4m 31s | 2 tasks | 1 files |

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

Last session: 2026-05-06 (Plan 08-03 execution)
Stopped at: Completed `08-03-cross-check-harness-PLAN.md` — `tests/test_lilith_cross_check.py` created and run; harness fails 5/5 (max |delta| = 179.936579 deg, ~18000x tolerance); Plan 04 branch = **FORMULA-CORRECTION**; suspected root cause: epoch constant 83.3532 deg is off by 180 deg (Ketu computes perigee, swe expects apogee); residual after +180 deg correction = 0.111 deg (still 11x tolerance, secondary frame/rate term to address); ready to invoke `/gsd:execute-phase 8 04` for the formula fix
Resume file: None

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-06 — Plan 08-03 complete (cross-check harness landed; Lilith bug empirically confirmed; Plan 04 = FORMULA-CORRECTION)*
