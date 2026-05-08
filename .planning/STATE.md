---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Astrologie relationnelle et prédictive
status: executing
last_updated: "2026-05-08T11:30:41.810Z"
last_activity: 2026-05-08
progress:
  total_phases: 1
  completed_phases: 0
  total_plans: 5
  completed_plans: 1
  percent: 20
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 — v1.2 milestone initialized)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 13 — doc-gates-and-ci-foundation

## Current Position

Phase: 13 (doc-gates-and-ci-foundation) — EXECUTING
Plan: 2 of 5
Status: Ready to execute
Progress: [░░░░░░░░░░] 0/8 v1.2 phases complete (0/37 REQs)
Last activity: 2026-05-08
Resume file: `.planning/phases/13-doc-gates-and-ci-foundation/13-01-PLAN.md`

## Performance Metrics

**Velocity totals:**

- v1.0: 16 plans / 7 phases (one decimal phase 2.1 inserted)
- v1.1: 27 plans / 5 phases (no decimal phases inserted)

**v1.1 phase breakdown (active time):**

| Phase                          | Plans | Active                                          | Avg/Plan      |
| ------------------------------ | ----- | ----------------------------------------------- | ------------- |
| 8. Lilith Verification & Fix   | 5     | ~22m 18s                                        | ~4m 28s       |
| 9. Configurable Aspects        | 6     | ~44m 58s                                        | ~7m 30s       |
| 10. Houses Module              | 6     | ~58m 10s                                        | ~9m 42s       |
| 11. CLI Refactor & Integration | 6     | ~34m 52s                                        | ~5m 49s       |
| 12. Release Preparation v1.1.0 | 4     | ~20m 26s active (~3h elapsed incl. checkpoints) | ~5m 6s active |

## Accumulated Context

**Open blockers:** None.

**v1.2 roadmap structure:**

- Phase 13: Doc Gates & CI Foundation (OPS-01, OPS-02) — early ops debt; gates apply to all subsequent v1.2 code
- Phase 14: Chart Abstraction Foundation (CHART-01..05) — keystone upstream of SYN/COMP/RET
- Phase 15: Additional House Systems (HOU2-01..05) — independent of CHART; extends `SYSTEMS` registry
- Phase 16: Synastry (SYN-01..05) — depends on Phase 14
- Phase 17: Composite Chart Midpoint (COMP-01..04) — depends on Phase 14
- Phase 18: Solar Return Standard + Relocated (RET-01..05) — depends on Phase 14
- Phase 19: Arabic Parts Framework + 8 Parts (PARTS-01..08) — depends on Phase 14 (`is_day_chart`)
- Phase 20: Release Preparation v1.2.0 (OPS-03, OPS-04, OPS-05) — late ops debt + PyPI publish

**v1.2 ops debt (will close during this milestone):**

- `interrogate ≥95%` not installed/wired into CI — Phase 13 (OPS-01)
- `numpydoc validate` not wired into CI — Phase 13 (OPS-02)
- Node.js 20 deprecation warnings on every workflow step — Phase 20 (OPS-03)
- `fr/CHANGELOG.md` aspirational reference — Phase 20 (OPS-04, decision)
- Venv shebangs hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` — workaround documented; not in v1.2 scope

**Working-tree leftovers (NOT v1.2 scope):**

- Stash `pre-release-merge: unrelated phase09/11 plan drift` left as-is

**Downstream impact (carried over from v1.1 BREAKING):**

- Kala (`solaris/kala`) — KetuAdapter must explicitly request `aspects=EXTENDED` for v1.0 behavior parity (documented in UPGRADING.md)
- Lilith consumers — recompute any cached values; ~180° shift on every date

**v1.2 framing constraints:**

- Non-breaking minor strict — all new APIs additive; no defaults changed; no exports removed
- Pure-NumPy contract preserved (no scipy / no swisseph runtime)
- Coverage gates: ≥90% project / ≥85% per module / ≥95% on new modules (`ketu/charts/`, `ketu/parts/`)

## Session Continuity

v1.2 roadmap written 2026-05-08. Next: `/gsd-plan-phase 13` to scaffold Phase 13 (Doc Gates & CI Foundation).
