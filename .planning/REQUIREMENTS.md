# Requirements: Ketu v1.1 Flexibility & Houses

**Defined:** 2026-05-06
**Core Value:** Cycle calculations must be correct, tested, and performant
**Milestone goal:** Make Ketu more flexible (configurable aspects), more complete (astrological houses), and more correct (Lilith fix) — evolving from astronomical to astronomical-astrological framework.

## v1.1 Requirements

Requirements for milestone v1.1. Each maps to roadmap phases (numbered from 8 onwards, continuing v1.0).

### Configurable Aspects (ASP)

- [ ] **ASP-01**: `core.aspects` constant remains length 14, append-only — invariant test guarantees order and length
- [ ] **ASP-02**: Module `ketu/aspects/presets.py` exposes `CLASSICAL` (5 majors), `TRADITIONAL` (7 = h12), `EXTENDED` (14 = legacy v1.0)
- [ ] **ASP-03**: `calculate_aspects()`, `calculate_aspects_vectorized()`, `calculate_aspects_batch()` accept `aspects=` parameter (list of names, preset name, or index array)
- [ ] **ASP-04**: Python API default changes — `aspects=None` resolves to `CLASSICAL` (5 majors); downstream consumers like Kala must explicitly request `EXTENDED` for legacy 14
- [ ] **ASP-05**: `aspect_set` is resolved to a NumPy boolean mask once at API entry — no filter inside hot loops
- [ ] **ASP-06**: LRU cache keys include `aspect_set` hash where applicable (no stale results after config change)
- [ ] **ASP-07**: Integration test: configure `CLASSICAL`, call all public aspect APIs, assert no result contains a non-classical aspect
- [ ] **ASP-08**: Benchmark: `calculate_aspects_batch()` regresses by no more than 5% vs v1.0 baseline

### CLI Refactor (CLI)

- [ ] **CLI-01**: `ketu` command uses argparse with subcommands (replaces interactive `input()` prompt)
- [ ] **CLI-02**: Flag `--harmonics SPEC` accepts preset name (`classical`, `traditional`, `extended`, `all`) OR explicit harmonic list (`9,10,11`)
- [ ] **CLI-03**: `--harmonics all` returns v1.0 14-aspect output byte-identical (legacy escape hatch, regression-tested)
- [ ] **CLI-04**: `ketu houses` subcommand: `--date ISO --lat FLOAT --lon FLOAT --system {placidus,koch}`
- [ ] **CLI-05**: Introspection flags `--list-aspect-sets` and `--list-house-systems` print available options with descriptions
- [ ] **CLI-06**: CLI output includes resolved config header (e.g. `# Aspect set: classical [0°, 60°, 90°, 120°, 180°]`)

### Houses Module (HOU)

- [ ] **HOU-01**: Audit `ephemeris/time.py` GMST/LST + obliquity precision; tighten if needed to achieve <1 arcmin error on Ascendant vs Astro.com reference
- [ ] **HOU-02**: New `ketu/houses/` subpackage with registry pattern (`SYSTEMS = {"placidus": ..., "koch": ...}`) for extensibility
- [ ] **HOU-03**: Placidus implementation with iteration cap (max 50) and explicit convergence detection
- [ ] **HOU-04**: Koch implementation (closed-form or iterative per chosen derivation)
- [ ] **HOU-05**: Output `HOUSES_DTYPE` structured array: 12 cusps + ASC + MC + ARMC + Vertex
- [ ] **HOU-06**: Polar fallback parameter `polar_fallback={"raise","porphyry"}`; `HighLatitudeError` raised by default beyond ±66.56°
- [ ] **HOU-07**: Helper `house_of(planet_lon, cusps) -> int` returns 1-12
- [ ] **HOU-08**: Vectorization over `(jd, lat, lon)` arrays (mask-based continuation for Placidus iteration)
- [ ] **HOU-09**: ≥95% coverage on `houses/`; ≥10 reference fixtures vs Astro.com / Swiss Ephemeris including polar lats (70°, 80°)
- [ ] **HOU-10**: Remove `calculate_house_cusps` placeholder stub from `ephemeris/planets.py` (currently returns wrong equal-house values)

### Lilith Verification & Fix (LIL)

- [ ] **LIL-01**: `LILITH_DEFINITION.md` written FIRST: documents Mean Apogee definition, tropical longitude convention, source citation (Chapront-Touz/Francou), explicit formula
- [ ] **LIL-02**: Test harness compares current Ketu formula (`ephemeris/orbital.py:591`) vs `pysweph SE_MEAN_APOG` on 5+ dates spanning 1900, 1950, 2000, 2025, 2050
- [ ] **LIL-03**: If empirical error >0.01°, formula is corrected; regression tests pin new values with explicit pysweph cross-check
- [ ] **LIL-04**: `pysweph>=2.10.3.6` added to `[project.optional-dependencies] test` (NOT runtime)
- [ ] **LIL-05**: CHANGELOG and UPGRADING.md document any Lilith value changes with magnitude (e.g. "Lilith differs by X° vs v1.0 on date Y")

### Release v1.1.0 (REL)

- [ ] **REL-01**: Version bumped 1.0.0 → 1.1.0 in `pyproject.toml` AND `ketu/__init__.py` (sync test passes)
- [ ] **REL-02**: CHANGELOG section "BREAKING / Numerical Behavior Changes" documents: CLI default change, Lilith correction (if any), new houses module
- [ ] **REL-03**: UPGRADING.md updated with v1.0 → v1.1 migration guide (script users, Kala adapter, Lilith consumers)
- [ ] **REL-04**: GitHub release v1.1.0 + PyPI publish via trusted publishing OIDC (workflow already configured)

## v2 Requirements (Deferred)

Acknowledged but not in v1.1 roadmap.

### Future Lilith Variants

- **LIL2-01**: True/Osculating Lilith (h13) — instantaneous apogee with retrograde motion
- **LIL2-02**: Asteroid Lilith #1181 — different body entirely

### Future House Systems

- **HOU2-01**: Whole Sign houses (trivial trig, polar-safe)
- **HOU2-02**: Equal houses (trivial trig, polar-safe)
- **HOU2-03**: Porphyry houses (currently used as polar fallback only)
- **HOU2-04**: Regiomontanus houses
- **HOU2-05**: Campanus houses

### Other

- **AST-01**: Asteroids (Ceres, Pallas, Juno, Vesta) and Centaurs (Chiron)
- **AST-02**: Fixed stars
- **AST-03**: Arabic Parts / Lots

## Out of Scope

Explicitly excluded from v1.1.

| Feature | Reason |
|---------|--------|
| True/Osculating Lilith | Defer to v1.2 — Mean Lilith is de-facto standard in 95% of astrology software |
| Asteroid Lilith #1181 | Defer to v1.2+ — different body, separate effort |
| Whole Sign / Equal / Porphyry / Regiomontanus houses (concrete impl) | Architecture supports them via registry; ship Placidus + Koch in v1.1 to prove pattern |
| Chiron, Centaurs, asteroids, fixed stars | Defer to future milestone |
| Arabic Parts / Lots | Defer to future milestone |
| Timezone handling inside Ketu | UTC remains required; timezone conversion is caller's responsibility |
| `pyswisseph` or `pysweph` as runtime dependency | Test-only is acceptable; license (AGPL) and brand promise (NumPy-only) prevent runtime |
| Chart/SVG visualization | Still removed since v1.0; deferred to post-Ketu GUI tooling |
| iCalendar export | Still removed since v1.0 |
| Real-time streaming calculations | Still batch-oriented |
| Web API | Ketu is a library, not a service |
| French documentation rebuild | Still deferred |
| `click` / `typer` CLI dependencies | argparse stdlib is sufficient; no new runtime deps |
| Bare `--harmonics 12` integer parsing | Too ambiguous (set vs single vs range); force named presets or explicit list |

## Traceability

Mapping requirements to roadmap phases. Phase numbering continues from v1.0 (last phase was 7).

| Requirement | Phase | Status |
|-------------|-------|--------|
| LIL-01 | Phase 8 | Pending |
| LIL-02 | Phase 8 | Pending |
| LIL-03 | Phase 8 | Pending |
| LIL-04 | Phase 8 | Pending |
| LIL-05 | Phase 8 | Pending |
| ASP-01 | Phase 9 | Pending |
| ASP-02 | Phase 9 | Pending |
| ASP-03 | Phase 9 | Pending |
| ASP-04 | Phase 9 | Pending |
| ASP-05 | Phase 9 | Pending |
| ASP-06 | Phase 9 | Pending |
| ASP-07 | Phase 9 | Pending |
| ASP-08 | Phase 9 | Pending |
| HOU-01 | Phase 10 | Pending |
| HOU-02 | Phase 10 | Pending |
| HOU-03 | Phase 10 | Pending |
| HOU-04 | Phase 10 | Pending |
| HOU-05 | Phase 10 | Pending |
| HOU-06 | Phase 10 | Pending |
| HOU-07 | Phase 10 | Pending |
| HOU-08 | Phase 10 | Pending |
| HOU-09 | Phase 10 | Pending |
| HOU-10 | Phase 10 | Pending |
| CLI-01 | Phase 11 | Pending |
| CLI-02 | Phase 11 | Pending |
| CLI-03 | Phase 11 | Pending |
| CLI-04 | Phase 11 | Pending |
| CLI-05 | Phase 11 | Pending |
| CLI-06 | Phase 11 | Pending |
| REL-01 | Phase 12 | Pending |
| REL-02 | Phase 12 | Pending |
| REL-03 | Phase 12 | Pending |
| REL-04 | Phase 12 | Pending |

**Coverage:**

- v1.1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-06*
*Last updated: 2026-05-06 after initial v1.1 definition*
