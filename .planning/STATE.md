# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-05-06 — Milestone v1.1 started

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Recent decisions affecting current work:

- Default aspects = 5 majors in v1.1 — Pro/classical default; ML harmonics opt-in via `--harmonics`
- Houses module starts with Placidus + Koch — Two systems prove extensibility; others plug in later
- Verify Lilith before fixing — Confirm bug exists and quantify error before changing formula
- Vectorize everything new — Houses + harmonics must be batchable over date arrays

### From v1.0 milestone (carried context)

- Pure NumPy contract: no new runtime deps allowed
- Mypy strict mode enforced in CI; numpydoc-style docstrings on public API
- Trusted publishing OIDC configured for PyPI releases
- Test isolation pattern: pytest tmp_path fixture for file I/O
- Error message convention: ValueError with received value + valid options
- Two-layer caching is intentional: LRU for single-point, EphemerisCache for batch

### Roadmap Evolution

- v1.0 milestone complete (8 phases, 15 plans, ketu 1.0.0 on PyPI)
- v1.1 milestone starting from phase 8 (continuing numbering)

### Pending Todos

None yet.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-05-06 (milestone v1.1 initialization)
Stopped at: PROJECT.md updated, gathering requirements
Resume file: None

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-06 — milestone v1.1 reset*
