# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-05-08 after v1.1 milestone close)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** Planning frontier for v1.2 (TBD). Run `/gsd-new-milestone` to start questioning → research → requirements → roadmap.

## Current Position

**Status:** v1.1 milestone CLOSED 2026-05-08.

- v1.0 (Phases 1-7): ✓ Complete (16/16 plans, shipped 2026-02-12)
- v1.1 (Phases 8-12): ✓ Complete (27/27 plans, shipped 2026-05-08)
- v1.2: not yet planned

**Last shipped:** ketu 1.1.0 on PyPI via tag `v1.1.0` (commit `41ee42e`, annotated SHA `54ce673`). Trusted-publishing OIDC workflow run 25528308313 (~38s). PyPI live: <https://pypi.org/project/ketu/1.1.0/>. GitHub release: <https://github.com/alkimya/ketu/releases/tag/v1.1.0>.

Last activity: 2026-05-08 — v1.1 milestone archived to `.planning/milestones/v1.1-{ROADMAP,REQUIREMENTS}.md`. PROJECT.md evolution review complete; all v1.1 active requirements moved to Validated. ROADMAP.md collapsed v1.1 into `<details>` block. MILESTONES.md created with v1.1 + v1.0 entries.

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

**v1.2 ops debt (deferred from v1.1 close):**

- `interrogate ≥95%` not installed/wired into CI — aspirational header reference only
- `numpydoc validate` not wired into CI
- `fr/CHANGELOG.md` does not exist (header reference is aspirational)
- Node.js 20 deprecation warnings on every workflow step (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`) — non-blocking; September 2026 removal deadline
- Venv shebangs hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` (project relocated from `solaris/ketu/` → `ketu/`); workaround via `python -m` pattern

**Working-tree leftovers (NOT v1.1 scope):**

- Stash `pre-release-merge: unrelated phase09/11 plan drift` left as-is

**Downstream impact (v1.1 BREAKING):**

- Kala (`solaris/kala`) — KetuAdapter must explicitly request `aspects=EXTENDED` for v1.0 behavior parity (documented in UPGRADING.md)
- Lilith consumers — recompute any cached values; ~180° shift on every date

## Session Continuity

Resume the project with `/gsd-new-milestone` to start v1.2.
