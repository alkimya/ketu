# Ketu

## What This Is

Ketu is a pure-Python astronomical library for planetary cycle calculations, built for financial analysis. It computes ephemerides, detects aspects, generates cycle time series, calculates astrological houses, and produces ML-ready features via complex number representation. NumPy is the only core dependency. Published on PyPI, it feeds the Solaris trading ecosystem (Kala ML, Surya agent) but is designed as a standalone public library.

## Core Value

Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Current Milestone: v1.1 Flexibility & Houses

**Goal:** Make Ketu more flexible (configurable aspects), more complete (astrological houses), and more correct (Lilith fix) — evolving from astronomical to astronomical-astrological framework.

**Target features:**
- Configurable default aspects (5 majors by default; opt-in harmonics 9/10/11/12 via CLI flags and Python API)
- Extensible house system (Placidus + Koch in v1.1, architecture scalable to others)
- Lilith calculation fix (verified against external reference)

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Pure NumPy ephemeris engine (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Ketu, Lilith) — v0.3.0
- ✓ Batch position calculation (`calc_planet_position_batch`) — v0.3.0
- ✓ 14-aspect detection system (conjunction through undecile) — v0.4.0
- ✓ Aspect window detection (entry/exact/exit timing via binary search) — v0.4.0
- ✓ Cycle time series generation (`generate_cycle_series`, `generate_multi_cycle_series`) — v0.4.0
- ✓ CYCLE_DTYPE structured array format for ML interop — v0.4.0
- ✓ Complex number representation (`complex.py`) with ML feature extraction — v0.4.0
- ✓ Vectorized aspect calculation path — v0.4.0
- ✓ Ephemeris cache system for O(1) lookups — v0.4.0
- ✓ Lunar calendar generation — v0.4.0
- ✓ CLI entry point (`ketu` command) — v0.1.0
- ✓ LRU caching for repeated calculations — v0.2.0
- ✓ Transit calculations vs natal positions — v0.4.0
- ✓ Aspect timelines (ML-ready structured arrays) — v0.4.0
- ✓ All CONCERNS.md bugs fixed (cache precedence, aspect non-determinism, Moon velocity wrap) — v1.0.0
- ✓ Export modules removed (chart, icalendar) — v1.0.0
- ✓ Pure NumPy contract (no hidden Pandas) — v1.0.0
- ✓ Complex representation integrated into cycle engine, vectorized ResonanceField — v1.0.0
- ✓ 91% test coverage (250 tests, Python 3.10-3.13 in CI) — v1.0.0
- ✓ Numpydoc-style docstrings on all public functions, mypy strict mode — v1.0.0
- ✓ Published on PyPI as `ketu==1.0.0` with trusted publishing OIDC — v1.0.0

### Active

<!-- Current scope: v1.1 Flexibility & Houses. -->

- [ ] Default aspect set is 5 majors (conjunction, opposition, trine, square, sextile) — backward compat via `--harmonics all`
- [ ] CLI flag `--harmonics N[,M,...]` opts into harmonics 9, 10, 11, 12, or `all`
- [ ] Python API accepts explicit aspect list AND named presets (`classical`, `traditional`, `extended`)
- [ ] House calculation module with extensible registry pattern
- [ ] Placidus house system implementation (vectorized over date arrays)
- [ ] Koch house system implementation (vectorized over date arrays)
- [ ] Helper to assign planet → house given cusps
- [ ] CLI subcommand for house calculation (`ketu houses --date ... --lat ... --lon ...`)
- [ ] Lilith calculation verified against external reference (Astro.com / Swiss Ephemeris) for known dates
- [ ] Lilith fix lands with regression tests covering 1900, 1950, 2000, 2025, 2050
- [ ] CHANGELOG and UPGRADING.md document the CLI default change
- [ ] Bump version to 1.1.0, GitHub release, PyPI publish

### Out of Scope

<!-- Explicit boundaries. -->

- Additional house systems beyond Placidus + Koch (Whole Sign, Equal, Porphyry, Regiomontanus...) — architecture supports them, defer concrete implementations
- Chiron, Centaurs, asteroids, fixed stars — defer to future milestone
- Arabic Parts / Lots — defer to future milestone
- Timezone handling (UTC remains required) — out of Ketu's scope, push to caller
- Chart/SVG visualization — still removed, deferred to post-Ketu GUI tooling
- iCalendar export — still removed, deferred to post-Ketu GUI tooling
- Real-time streaming calculations — still batch-oriented
- Web API — Ketu is a library, not a service
- French documentation rebuild — still deferred

## Context

Ketu v1.0.0 shipped on PyPI on 2026-02-12 — clean public API, pure NumPy, 91% test coverage, mypy strict, numpydoc-style docstrings everywhere. The library is consumed by Kala (KetuAdapter) and Surya in the Solaris trading ecosystem.

v1.1 trigger came from CLI usage: harmonics 9/10/11 were added in v0.4 for ML feature engineering inside Kala, but they leaked into the default CLI output, producing noisy aspect lists for everyday astrological use. The user's personal default is the 5 traditional majors (conjunction, opposition, trine, square, sextile); harmonic 12 (adding semi-sextile + quinconce) is the "traditional 7" set; harmonics 9/10/11 should remain available but opt-in.

Ketu also lacks astrological houses — a missing primitive for full chart analysis. The user wants Ketu to evolve from astronomical to astronomical-astrological framework, starting with Placidus + Koch and an architecture that scales to other systems.

Lilith calculations are suspected to be incorrect (visual inspection) and need verification against an external authoritative reference (Astro.com / Swiss Ephemeris) before fix.

Key technical context:
- Existing aspect filtering is hardcoded in `core.py` and used throughout `aspects/`, `cycles/`
- House calculation is a new domain — needs research on Placidus/Koch formulae and scalable architecture
- Lilith handled in `ephemeris/planets.py` alongside other points; current formula provenance unclear
- All new code must be vectorized (NumPy batch operations) — performance is non-negotiable

## Constraints

- **Dependency**: NumPy only as core dependency — no new runtime deps
- **Compatibility**: Python 3.10+ (tested 3.10-3.13)
- **Performance**: All new calculations must be vectorizable over date arrays (no Python loops)
- **API stability**: Backward compat must be reachable via flag (`--harmonics all` for the 14-aspect legacy default)
- **Testing**: Maintain ≥90% test coverage across new modules, with regression tests for Lilith
- **Time inputs**: UTC only — no timezone handling inside Ketu
- **Release**: Full GitHub release + PyPI publish

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Remove all export modules | Pure calculation library — exports belong in future GUI layer | ✓ Good (v1.0) |
| Complex math internal, degrees external | Complex numbers better for computation, degrees better for humans | ✓ Good (v1.0) |
| Fix all CONCERNS.md bugs | Clean slate for 1.0 — no known bugs at release | ✓ Good (v1.0) |
| Remove Pandas dependency | Keep NumPy-only contract, use structured arrays instead | ✓ Good (v1.0) |
| Breaking API changes OK for 1.0 | Major version bump justifies cleanup | ✓ Good (v1.0) |
| Default aspects = 5 majors in v1.1 | Pro/classical default; ML harmonics opt-in via `--harmonics` | — Pending |
| Houses module starts with Placidus + Koch | Two systems prove extensibility; others can plug in later | — Pending |
| Verify Lilith before fixing | Confirm bug exists and quantify error before changing formula | — Pending |
| Vectorize everything new | Houses + harmonics must be batchable over date arrays | — Pending |

---
*Last updated: 2026-05-06 after milestone v1.1 initialization*
