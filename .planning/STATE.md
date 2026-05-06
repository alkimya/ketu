# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — Phase 8 (Lilith Verification & Fix)

## Current Position

Phase: 8 of 12 (Lilith Verification & Fix)
Plan: 4 of 5 complete — next is Plan 05 (release notes / CHANGELOG / UPGRADING)
Status: Plan 08-04 complete (FORMULA-CORRECTION branch executed; all 4 plumbing sites updated with single source-of-truth `_LILITH_*` constants in `ketu/ephemeris/orbital.py`; harness now 10/10 green at user-tolerance + regression-baseline tighter layer; existing 410-test suite still green at 420 passed); Plan 08-05 unblocked
Last activity: 2026-05-06 — Plan 08-04 executed; commits `39e3a71` (formula fix), `8af6085` (regression-baseline harness), `2bce430` (LILITH_DEFINITION.md update); post-fix max |delta| = 0.002693 deg on 5 plan dates, 0.007815 deg over 55K daily samples 1900-2050

Progress: [████░░░░░░] v1.0 complete; v1.1 1/5 phases (Phase 8: 4/5 plans)

## Performance Metrics

**Velocity (v1.0 reference baseline):**

- Total plans completed (v1.0): 16
- v1.1 plans completed: 4 (Phase 8: 08-01, 08-02, 08-03, 08-04)

**By Phase (v1.1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 8. Lilith Verification & Fix | 4 | ~18m 37s | ~4m 39s |
| 9. Configurable Aspects | 0 | — | — |
| 10. Houses Module | 0 | — | — |
| 11. CLI Refactor & Integration | 0 | — | — |
| 12. Release Preparation v1.1.0 | 0 | — | — |

*Updated after each plan completion*
| Phase 08 P01 | 2min | 1 tasks | 1 files |
| Phase 08 P02 | 2m 5s | 2 tasks | 1 files |
| Phase 08 P03 | 4m 31s | 2 tasks | 1 files |
| Phase 08 P04 | 10m 1s | 4 tasks | 4 files |

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

Last session: 2026-05-06 (Plan 08-04 execution)
Stopped at: Completed `08-04-conditional-formula-fix-PLAN.md` (FORMULA-CORRECTION branch). All 4 Lilith plumbing sites (`ketu/ephemeris/orbital.py` x2, `ketu/ephemeris/planets.py` x2) updated atomically with single source-of-truth `_LILITH_*` constants. v1.1 formula: linear secular term (`E + R*d`) plus one sinusoidal perturbation term (`A*sin(omega*d + phi)`), all 5 parameters jointly NLS-fitted vs. swe.MEAN_APOG over 55K daily samples 1900-2050. Post-fix max |delta| = 0.002693 deg on the 5 plan dates (3.7x under tolerance) and 0.007815 deg over 55K daily samples (1.3x under tolerance). Harness now 10/10 green (5 user-tolerance + 5 regression-baseline at 0.005 deg tighter layer). `docs/LILITH_DEFINITION.md` Formula and History sections rewritten; placeholder removed. Ready to invoke `/gsd:execute-phase 8 05` for release notes / CHANGELOG / UPGRADING.
Resume file: None

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-06 — Plan 08-04 complete (FORMULA-CORRECTION branch executed; all 4 plumbing sites updated; harness 10/10 green; max |delta| post-fix = 0.0027 deg on 5 plan dates)*
