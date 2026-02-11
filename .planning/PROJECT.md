# Ketu 1.0

## What This Is

Ketu is a pure-Python astronomical library for planetary cycle calculations, built for financial analysis. It computes ephemerides, detects aspects, generates cycle time series, and produces ML-ready features via complex number representation. NumPy is the only core dependency. Published on PyPI, it feeds the Solaris trading ecosystem (Kala ML, Surya agent) but is designed as a standalone public library.

## Core Value

Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. Inferred from existing codebase. -->

- ✓ Pure NumPy ephemeris engine (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Ketu, Lilith) — v0.3.0
- ✓ Batch position calculation (`calc_planet_position_batch`) — v0.3.0
- ✓ 14-aspect detection system (conjunction through undecile) — v0.4.0
- ✓ Aspect window detection (entry/exact/exit timing via binary search) — v0.4.0
- ✓ Cycle time series generation (`generate_cycle_series`, `generate_multi_cycle_series`) — v0.4.0
- ✓ CYCLE_DTYPE structured array format for ML/Pandas interop — v0.4.0
- ✓ Complex number representation (`complex.py`) with ML feature extraction — v0.4.0
- ✓ Vectorized aspect calculation path — v0.4.0
- ✓ Ephemeris cache system for O(1) lookups — v0.4.0
- ✓ Lunar calendar generation — v0.4.0
- ✓ CLI entry point (`ketu` command) — v0.1.0
- ✓ LRU caching for repeated calculations — v0.2.0
- ✓ Transit calculations vs natal positions — v0.4.0
- ✓ Aspect timelines (ML-ready structured arrays) — v0.4.0

### Active

<!-- Current scope: consolidation toward 1.0. -->

- [ ] Fix all known bugs from CONCERNS.md (operator precedence, aspect non-determinism)
- [ ] Remove export modules (chart, icalendar) — pure calculation library
- [ ] Remove hidden Pandas dependency in aspect timelines
- [ ] Integrate complex representation fully into cycle engine
- [ ] Achieve 70% test coverage (currently ~62%)
- [ ] Fix ResonanceField performance (vectorize loop-based calculation)
- [ ] Consolidate dual caching strategies
- [ ] Standardize error messages across modules
- [ ] Update documentation for 1.0 API
- [ ] Bump version to 1.0.0
- [ ] Create GitHub release + publish to PyPI

### Out of Scope

<!-- Explicit boundaries. -->

- Chart/SVG visualization — removed for 1.0, may return in future GUI version
- iCalendar export — removed for 1.0, may return in future GUI version
- Matplotlib dependency — removed entirely
- Real-time streaming calculations — not needed for batch analysis workflow
- Web API — Ketu is a library, not a service
- French documentation rebuild — defer to post-1.0

## Context

Ketu v0.4.0 has 176 passing tests but ~38% of the codebase is untested. The CONCERNS.md audit identified 2 known bugs, performance bottlenecks, architectural fragility, and code duplication. The library replaced swisseph (C extension) with pure NumPy in v0.3.0, making it fully portable. Complex number representation was added in v0.4.0 but isn't fully integrated into the cycle engine — two parallel systems exist.

The Solaris ecosystem depends on Ketu via Kala (KetuAdapter). Breaking changes are acceptable for 1.0 since downstream consumers can be updated simultaneously.

Key technical debt:
- Operator precedence bug in cache logic (`cycles/calculator.py`)
- Non-deterministic aspect vectorization (30 vs 31 aspects)
- ResonanceField uses Python loops instead of vectorized batch operations
- Hidden Pandas import in `aspects/timelines.py`
- Export modules with optional deps that fail at runtime
- Inconsistent error handling across modules

## Constraints

- **Dependency**: NumPy only as core dependency — no new runtime deps
- **Compatibility**: Python 3.10+ (tested 3.10-3.13)
- **Performance**: Cycle calculations must remain sub-second for 10K timestamps
- **API**: Breaking changes acceptable (major version bump to 1.0)
- **Testing**: Must reach 70% coverage before release
- **Release**: Full GitHub release + PyPI publish required

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Remove all export modules | Pure calculation library — exports belong in future GUI layer | — Pending |
| Complex math internal, degrees external | Complex numbers better for computation, degrees better for humans | — Pending |
| Fix all CONCERNS.md bugs | Clean slate for 1.0 — no known bugs at release | — Pending |
| Remove Pandas dependency | Keep NumPy-only contract, use structured arrays instead | — Pending |
| Breaking API changes OK | Major version bump justifies cleanup | — Pending |

---
*Last updated: 2026-02-12 after initialization*
