---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Astrologie relationnelle et prédictive
status: executing
last_updated: "2026-05-09T08:03:31Z"
last_activity: 2026-05-09
progress:
  total_phases: 8
  completed_phases: 3
  total_plans: 14
  completed_plans: 14
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 — v1.2 milestone initialized)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Phase 15 — additional-house-systems

## Current Position

Phase: 15 (additional-house-systems) — COMPLETE
Plan: 4 of 4
Status: All plans complete (HOU2-01..05 satisfied)
Progress: [██████████] 100%
Last activity: 2026-05-09
Resume file: None

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
| Phase 15 P01 | 6 | 5 tasks | 9 files |
| Phase 15 P02 | 8min | 7 tasks | 7 files |
| Phase 15 P03 | 7min | 5 tasks | 5 files |
| Phase 15 P04 | 7min | 7 tasks | 5 files |

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

## Decisions

- Plan 15-03: REYKJAVIK_REGIO_TOL_ARCMIN pinned at 1.0' (measured 0.86' on 2026-05-09) — decision-tree case <1' bucket per Plan 15-03 Task 5.
- Plan 15-03: Pole-height naming convention (`pole_height_outer_deg` / `pole_height_inner_deg`) as visual ratchet against Pitfall 4 (geographic latitude vs pole height); grep gate enforces no `_asc1` call receives raw geographic latitude in `regiomontanus.py`.
- Plan 15-03: Regiomontanus follows Koch-style NaN propagation at polar boundary (D-02 verrouillé in 15-CONTEXT.md), NOT swisseph `MC<->IC` swap; existing `api.py` `polar_fallback` machinery routes NaN to Porphyry without modification (verified by 2 dedicated integration tests).
- Plan 15-04: Parser dispatcher dynamique via `choices=sorted(SYSTEMS.keys())` (D-07 verrouillé) — future-proof, Campanus/Topocentric/Alcabitius en v1.3 ne nécessiteront aucune modification du parser.
- Plan 15-04: Top-level `--list-house-systems` help rendu statique générique (`"List all registered house systems and exit."`) — évite la dette de maintenance ; détails dans le subcommand `--system` help.
- Plan 15-04: Pitfall 7 affecte 2 emplacements (test_houses_cmd.py ET test_parser.py) — auto-fix Rule 1 sur le second emplacement non identifié dans le plan ; substitution `regiomontanus` → `nonexistent_xyz` ratchet la sémantique CLI sans dépendance à la blacklist.

## Session Continuity

v1.2 roadmap written 2026-05-08. Phase 15 close : 15-01 (foundation), 15-02 (whole_sign + equal), 15-03 (regiomontanus), 15-04 (CLI integration + phase gates) tous complétés. HOU2-01..05 satisfaits ; 909 tests verts ; 6 systèmes registrés ; 4 success criteria de Phase 15 verified end-to-end. Next: Phase 16 (Synastry) ou Phase 13 (Doc Gates & CI Foundation, en attente).
