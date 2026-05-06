# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — Phase 9 (Configurable Aspects)

## Current Position

Phase: 9 of 12 (Configurable Aspects) — **IN PROGRESS**
Plan: 3 of 6 complete (09-01, 09-02, 09-03 done — Wave 1 complete; 09-04a, 09-04b, 09-05 remaining)
Status: Wave 1 complete — Plan 09-01 baseline captured (`baseline-v1.0.json`, mean[365]=200.87ms, aspect_set=extended, drift=3.56% PASS); Plan 09-02 presets module (CLASSICAL/TRADITIONAL/EXTENDED frozen masks); Plan 09-03 invariant test (sha256 fingerprint `c5bd1773...9afb359`, mutation-tested). Wave 2 (09-04a calculator refactor, 09-04b default migration) is unblocked.
Last activity: 2026-05-06 — Plan 09-01 executed; commits `78085d1` (benchmark script via Wave-1 parallel collision with 09-02), `e6fca78` (baseline JSON capture) on `gsd/v1.1-milestone`

Progress: [████░░░░░░] v1.0 complete; v1.1 1/5 phases complete (Phase 8: 5/5 plans), Phase 9: 3/6 plans

## Performance Metrics

**Velocity (v1.0 reference baseline):**

- Total plans completed (v1.0): 16
- v1.1 plans completed: 8 (Phase 8: 08-01, 08-02, 08-03, 08-04, 08-05; Phase 9: 09-01, 09-02, 09-03)

**By Phase (v1.1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 8. Lilith Verification & Fix | 5 | ~22m 18s | ~4m 28s |
| 9. Configurable Aspects | 3 | ~13m 00s | ~4m 20s |
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
| Phase 09 P02 | 5m 25s | 3 tasks | 3 files |
| Phase 09 P01 | 6m 00s | 2 tasks | 1 files |

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
- [Phase 09]: [Phase 09-02]: ketu/aspects/presets.py — three frozen length-14 np.bool_ masks (CLASSICAL=5, TRADITIONAL=7, EXTENDED=14) with single-call resolve_aspect_set() dispatching on six input types (None / str preset case-insensitive / Sequence[str|int] / np.ndarray bool|int). Defensive bool-rejection in Sequence prevents silent [True, False] -> [1, 0] index coercion. ASP-06 forward-looking rule documented (no caches today materialize filtered aspects, but Wave 2 must hash mask.tobytes() if adding any). 100% test coverage on presets.py (56 tests).
- [Phase 09]: [Phase 09-01]: ASP-08 v1.0 baseline frozen at `.planning/phases/09-configurable-aspects/baseline-v1.0.json` (git_sha=049a9e7, aspect_set=extended, mean[365]=200.87ms cv=1.62%, 50 iter × 3 batch sizes, drift=3.56% PASS <5% gate). `tests/benchmark_aspects_batch.py` ships --aspect-set flag from day 1 and mismatch-rejection in --compare mode (no silent baseline-vs-comparison drift). Wave-1 parallel collision: identical script content authored independently by Plan 09-01 and committed via Plan 09-02 commit `78085d1` — md5 verified byte-identical, no merge needed.

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

Last session: 2026-05-06 (Plan 09-01 execution; Wave 1 closing)
Stopped at: Completed `09-01-baseline-capture-PLAN.md`. v1.0 baseline frozen at `.planning/phases/09-configurable-aspects/baseline-v1.0.json` with `aspect_set='extended'`, `git_sha=049a9e7ef8de0256ddf0016183a2cbc9adba2c57`, mean[365]=200.87ms ± 3.26ms (cv=1.62%); reproducibility drift between two consecutive captures = 3.56% (PASS <5% gate). `tests/benchmark_aspects_batch.py` (378 lines, mypy --strict clean) authored independently in Plan 09-01 matched byte-for-byte the script committed in parallel by Plan 09-02 commit `78085d1` — no merge conflict, single Task 2 commit `e6fca78` for the JSON. Wave 1 (09-01 baseline / 09-02 presets / 09-03 invariant) all green; `ketu/aspects/calculator.py` byte-identical to v1.0 at baseline-capture time. Wave 2 (09-04a calculator-refactor that wires `aspects=` kwarg, 09-04b default-migration) now unblocked. Wave-3 enforcement primitive verified end-to-end: `--compare` mode reads baseline `aspect_set` and rejects CLI override that disagrees (exits 2); `--aspect-set classical` on v1.0 HEAD exits 3 by design (will succeed post-09-04a). Run-to-run noise on `--compare` round-trip can hover at 5-7% on size 365 — Wave 3 should run multiple invocations and use median delta if any single run hovers near the gate.
Resume file: None

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-06 — Plan 09-01 complete; Phase 9: 3/6 plans (Wave 1 done). v1.0 calculate_aspects_batch baseline frozen; --aspect-set flag wired from day 1; aspect_set=extended locked; reproducibility drift 3.56% PASS; Wave 2 (09-04a/09-04b) unblocked*
