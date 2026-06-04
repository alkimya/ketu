---
gsd_state_version: 1.0
milestone: v1.6
milestone_name: Declination Aspects
status: completed
stopped_at: Completed 36-02-PLAN.md — Phase 36 complete. Phase 37 (v1.6 release) is next.
last_updated: "2026-06-04T21:06:58.264Z"
last_activity: 2026-06-04 -- Phase 37 marked complete
progress:
  total_phases: 2
  completed_phases: 2
  total_plans: 5
  completed_plans: 5
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-04 — v1.6 roadmap created)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 37 — documentation-release-v1-6-0

## Current Position

Phase: 37 — COMPLETE
Plan: 1 of 3
Status: Phase 37 complete
Last activity: 2026-06-04 -- Phase 37 marked complete

Progress: ██████████ 100%

## Next Step

Execute Phase 37 — v1.6 release (tag v1.6.0, publish to PyPI, user relecture-validation gate required first).

## Accumulated Context

### Decisions

Full log in `.planning/PROJECT.md` Key Decisions table. Relevant for v1.6:

- `CHART_DTYPE` is UNCHANGED (companion function, not a dtype field) — no ratchet break.
- Frozen 14-row `core.aspects` table + V1/V13 sha256 fingerprints stay byte-identical — DECLA aspects live in a SEPARATE `DECLA_ASPECT_DTYPE`.
- Orb formula: `max((orb_b1+orb_b2)/2 * (1/12), 0.5)` — `DECLA_COEF=1/12` yields exactly 1.0° for Sun/Moon; `MIN_DECL_ORB=0.5°` floor keeps Rahu/Ketu/Lilith (orb=0) detectable.
- Detection is vectorizable batch (`(S,14)→(S,91)` upper-triangle) — no Python loop in the hot path.
- Research pitfalls are REQUIRED test cases: sign conflation (+15°/−15° is CP, not P), orb inflation (7° Sun/Moon gap not parallel), zero-sign trap (both at δ=0 → no aspect), MIN_DECL_ORB floor (Rahu/Lilith gap 0.1° → detected).
- User go/no-go relecture-validation REQUIRED before any irreversible publish (tag, PyPI, GitHub release) — hard gate in Phase 37.
- Plan 36-01: find_declination_aspects returns ONE unified DECLA_ASPECT_DTYPE array (P+CP by kind field), sorted by (body1,body2), empty = np.empty(0) never None/tuple — no orbs.py (formula merged into core.py).
- Plan 36-01: `_ORB_MAT` frozen 14x14 at module load; `ketu.__all__` and `CHART_DTYPE` byte-identical — additive sub-package only.
- Plan 36-02: `DeclinationAspectMasks` uses `typing.NamedTuple` (mypy `--strict` compatible); `np.count_nonzero()` in tests avoids pytest-cov/numpy bool `.sum()` interaction; no-loop assertion strips docstring before checking source.
- Plan 36-02: Phase 36 fully complete — `ketu.declination` delivers DECLA-01..04, 1654 tests green, 100% coverage, mypy `--strict` clean, interrogate 100%.

### Blockers/Concerns

None. v1.6 builds additively on the green v1.5 base (1627 tests, 100% coverage, mypy `--strict` clean).

### Pending Todos

None.

## Performance Metrics

**Velocity (shipped milestones):**

| Milestone | Phases | Plans | Active time |
|-----------|--------|-------|-------------|
| v1.0      | 7      | 16    | —           |
| v1.1      | 5      | 27    | ~3h         |
| v1.2      | 8      | 35    | ~20d elapsed|
| v1.3      | 8+1    | 30    | ~3d         |
| v1.4      | 5      | 15    | ~1d         |
| v1.5      | 3      | 9     | ~1d         |

*Updated after each plan completion*

## Session Continuity

Last session: 2026-06-04 — Plan 36-02 executed: DeclinationAspectMasks NamedTuple + declination_aspect_masks batch function, 8 tests green, all quality gates pass.
Stopped at: Completed 36-02-PLAN.md — Phase 36 complete. Phase 37 (v1.6 release) is next.
Resume file: None
