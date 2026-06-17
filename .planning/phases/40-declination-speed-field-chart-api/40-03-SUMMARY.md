---
phase: 40-declination-speed-field-chart-api
plan: 03
status: complete
requirements: [DSPD-03]
completed: 2026-06-17
---

# Plan 40-03 Summary — Composite body_decl_speed derivation

## What was built

Derived `body_decl_speed` in the composite path (`ketu/composite/api.py`) per **D-01 /
DSPD-03**: a forward finite difference on the composite's OWN frozen (λ, β), advanced by
their **midpoint velocities** over Δt = 0.01 d. The composite has no canonical jd, so dδ/dt
is made self-consistent with the composite's frozen chart — the same self-consistency
discipline `body_decl` established in v1.5.

- **dλ/dt** reuses the already-stored `out["body_speeds"]` (composite midpoint of parent
  longitude speeds).
- **dβ/dt** is sourced from `calc_planet_position_batch(parent_jd, body)[0, 4]` (lat_speed,
  column 4) at each parent's natal jd, then averaged — it is **NOT zeroed** (for the Moon,
  Δβ contributes ~2.6× more to Δδ than Δλ over Δt=0.01 d).
- The frozen (λ₀, β₀) are advanced by these midpoint rates over Δt=0.01, the same
  coordinate chain (`spherical_to_rectangular → ecliptic_to_equatorial →
  rectangular_to_spherical`) yields δ₁, and the slope is `(δ₁ − δ₀) / 0.01`, reusing the
  already-computed `_decl` as δ₀.

Task 2 pinned **synastry inheritance** with no source change: two `compute_chart`-produced
natal charts each carry finite, non-zero `body_decl_speed`, and the synastry call still
succeeds with the 16-field `CHART_DTYPE` inputs. `SYNASTRY_DTYPE` deliberately does not
carry the field (inheritance is structural, not code — Pitfall 4).

## Key files

### Modified
- `ketu/composite/api.py` — `+42` lines: new `calc_planet_position_batch` import; the D-01
  FD block after `out["body_decl"] = _decl` (dβ/dt midpoint loop, frozen-field advance,
  coordinate chain at the advanced instant, slope assignment).

### Created (tests)
- `tests/composite/test_calculate_composite.py` — `+65`: `TestBodyDeclSpeed` (shape `(14,)`,
  not-all-zero, all-finite, and the binding **anti-averaging ratchet**
  `test_body_decl_speed_not_parent_midpoint` — proves the composite value differs from
  `(chart_a + chart_b)/2` for at least the Moon).
- `tests/synastry/test_calculate_synastry.py` — `+48`: synastry inheritance pinning test.

## Requirements satisfied

- **DSPD-03** — Composite `body_decl_speed` derived from the composite's own frozen λ,β
  (never the parent-speed midpoint, never a re-fetch at the composite jd, never via
  `compute_chart`); anti-averaging ratchet green; synastry inheritance pinned.

## Verification

- `pytest` full suite: **1691 passed, 2 skipped, 100% coverage**.
- COMP-03 anti-regression: **no real call to `compute_chart()` in `ketu/composite/api.py`**
  (only docstring/comment references) — ratchet stays green.
- `calc_planet_position_batch` imported; dβ/dt not zeroed.
- Anti-averaging ratchet `test_body_decl_speed_not_parent_midpoint` PASSED.

## Self-Check: PASSED

## Deviations

- **Commit hygiene (non-functional):** this plan's executor agent was interrupted by a
  session limit before emitting a clean `feat(40-03)` GREEN commit, the SUMMARY, and its
  return signal. The Task-1 implementation had landed under a `chore(40-03): checkpoint`
  commit (`ab969ba`) and the agent had also performed a superfluous (but harmless) wave-1+2
  merge into its own already-correctly-based worktree (`be03a14`). The orchestrator verified
  the implementation is complete and correct (full suite + COMP-03 + anti-averaging ratchet
  all green), then closed the plan manually by authoring this SUMMARY — the "close out
  manually" safe-resume path. No code was re-run or re-written; the delivered logic is
  exactly what the plan specified.
