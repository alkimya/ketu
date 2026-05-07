# Changelog

> Consultez la version française dans `fr/CHANGELOG.md`.

All notable changes to Ketu are documented here.

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
format and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-08

### BREAKING / Numerical Behavior Changes (Summary)

This release contains three user-visible behavior changes from v1.0.
Read each in detail in the dedicated sub-sections below and consult
`UPGRADING.md` for migration recipes.

1. **CLI default aspect set: EXTENDED (14) -> CLASSICAL (5).** The
   `ketu` CLI now emits 5 major aspects by default (Conjunction,
   Sextile, Square, Trine, Opposition). Restore v1.0 behavior with
   `ketu --harmonics extended`. (Phase 9 / ASP-04)
2. **Lilith (Mean Apogee) longitude formula corrected.** Values now
   match Swiss Ephemeris `SE_MEAN_APOG` to better than 0.01 deg. v1.0
   values were approximately 180 deg off on every date. Recompute
   any cached Lilith data. (Phase 8 / LIL-03)
3. **Houses module replaces broken `calculate_house_cusps`.** The v1.0
   `ketu.ephemeris.calculate_house_cusps` always returned an Equal
   House fallback regardless of system; it has been removed. Use the
   new `ketu.calculate_houses(...)` API or the `ketu houses` CLI
   subcommand. (Phase 10 / HOU-10)

### Removed (BREAKING)

- **`ketu.ephemeris.calculate_house_cusps`** — broken equal-house
  placeholder removed. The v1.0/v0.x function returned an Equal House
  fallback regardless of the requested `house_system` argument and was
  never connected to a real algorithm. It also exposed the wrong return
  shape vs. mainstream Swiss-Ephemeris-compatible APIs (it returned
  `(cusps, ascmc)` with a 6-element ascmc instead of the standard
  13-tuple Placidus result). Use `ketu.calculate_houses(jd, lat, lon,
  system='placidus' | 'koch' | 'porphyry')` from the new `ketu.houses`
  module instead — vectorised, registry-extensible, with explicit
  `polar_fallback={"raise","porphyry"}` semantics. (HOU-10)

### Changed (BREAKING)

- **CLI default aspect set is now CLASSICAL (5 aspects) instead of
  the implicit EXTENDED (14 aspects) of v1.0.** The new default
  surfaces only the 5 major aspects (Conjunction, Opposition, Trine,
  Square, Sextile). v1.0 emitted all 14 harmonics by default; users
  who scraped CLI stdout will see approximately 64% fewer aspect
  rows per body pair. The `core.aspects` array remains length-14
  append-only (Kala positional indexing is unaffected — verified by
  the Phase 9 invariant test); only the *default selection* changed.
  Restore v1.0 behavior with `ketu --harmonics extended`. List
  available presets with `ketu --list-aspect-sets`. (Phase 9 /
  ASP-04, ASP-08)

### Added

- **`ketu.houses` module** — Placidus, Koch, and Porphyry house systems
  registered through a `@register("name")` decorator and dispatched via
  `calculate_houses(jd, lat, lon, system, polar_fallback)`. Output is a
  `HOUSES_DTYPE` structured array with 12 cusps + ASC/MC/ARMC/Vertex,
  vectorised over the broadcast of `(jd, lat, lon)`. New systems plug
  in via the registry without modifying `calculate_houses` dispatch.
  Includes `house_of(planet_lon, cusps)` for the 1..12 house lookup
  and `HighLatitudeError` raised by default at `|lat| > polar_circle(jd)`.
  (HOU-02 .. HOU-10)

### Fixed (BREAKING - Numerical Behavior Change)

- **Lilith (Mean Apogee) longitude formula corrected** to match Swiss
  Ephemeris `SE_MEAN_APOG`. The v1.0 formula
  (`83.3532 + 0.1114040803 * d`) was actually computing the lunar mean
  *perigee* longitude, not the apogee, producing a systematic offset of
  approximately 180 deg on every date. Empirical max |delta| vs.
  `swe.calc_ut(jd, swe.MEAN_APOG)` over 1900-2050 was 179.936579 deg
  (Plan 03 cross-check). The v1.1 formula adds 180 deg to the epoch,
  refines the secular rate, and adds a single sin() perturbation term
  (period approximately 1095 days) fitted by joint nonlinear least
  squares against `swe.MEAN_APOG` over 55K daily samples 1900-2050. This
  is a deliberate deviation from a pure Chapront secular linear formula:
  Ketu v1.1 ships `linear secular term + 1 sin() perturbation`, not a
  raw ELP-2000 polynomial. Post-fix max |delta| vs. Swiss Ephemeris is
  0.002693 deg on the five Plan 03 cross-check dates and 0.007815 deg
  over 55K daily samples 1900-2050 -- both well below the 0.01 deg
  tolerance documented in `docs/LILITH_DEFINITION.md`.
- **User-visible impact:** Lilith longitudes returned by
  `get_lilith_position(jd)` and `calc_planet_position(jd, 12)` differ
  from v1.0 by approximately 180 deg on essentially every date.
  Concrete v1.0 -> v1.1 examples per date are tabulated in
  `UPGRADING.md`. **Recompute any cached Lilith values produced by
  v1.0** (ML feature arrays, lunation timing tables, aspect-window
  catalogues, charts). Other body positions are unchanged.
- **Single source of truth:** all four Lilith call sites
  (`ketu/ephemeris/orbital.py` x2, `ketu/ephemeris/planets.py` x2) now
  reference five private module-level constants (`_LILITH_MEAN_*`,
  `_LILITH_PERTURB_*`) declared once in `orbital.py`, eliminating the
  v1.0 four-site literal-duplication drift risk.

### Added

- **Lilith definition contract** (`docs/LILITH_DEFINITION.md`): single
  reference document stating which quantity Ketu computes (Mean Apogee,
  matching `SE_MEAN_APOG`), the exact formula, the reference frame
  (tropical, ecliptic of date, geocentric, mean orbit), the source
  (ELP-2000 / Chapront-Touze with one fitted perturbation), the 0.01
  deg cross-check tolerance and its derivation, and the v1.0 -> v1.1
  History.
- **Lilith cross-check harness** (`tests/test_lilith_cross_check.py`):
  parametrized pytest module verifying `get_lilith_position` against
  Swiss Ephemeris on five dates spanning 1900-2050, plus a tighter
  regression-baseline layer at 0.005 deg pinning the v1.1 fit. The
  harness uses `pytest.importorskip("swisseph")` so it skips cleanly
  when `pysweph` is not installed.
- **Test-only optional dependency** `pysweph>=2.10.3.6` under
  `[project.optional-dependencies].test` -- AGPL-licensed, never shipped
  in the runtime wheel. Verified empirically via two-venv runtime
  isolation test: `pip install ketu` MUST NOT pull `pysweph`;
  `pip install -e .[test]` MUST. See `docs/LILITH_DEFINITION.md`
  "AGPL and Test-Only Dependency Note" section.

### Added

- **CLI refactor (argparse-based)** — `ketu` is now an argparse
  multi-subcommand application:
  - `ketu aspects --date <ISO-UTC>` — aspect snapshot for a single
    instant (replaces the legacy interactive prompt).
  - `ketu houses --date <ISO-UTC> --lat <lat> --lon <lon>
    --system <name>` — house cusps for a single chart with optional
    `--polar-fallback {raise,porphyry}`.
  - `--harmonics {classical,traditional,extended,all,<comma-list>}` —
    select the aspect preset or pass an arbitrary comma-separated list
    of harmonic indices (e.g. `--harmonics 0,4,7,9,13`).
  - `ketu --list-aspect-sets` — print available aspect presets with
    their angles, then exit. Works with or without a subcommand.
  - `ketu --list-house-systems` — print available house systems with
    their polar-fallback hint, then exit. Works with or without a
    subcommand.
  - **Resolved-config stderr header** — every invocation emits a
    `# Ketu vX.Y.Z` line plus, when applicable, a `# Aspect set: <name>
    (N aspects: ...)` and/or `# House system: <name>` line to
    **stderr** (not stdout). Pipelines that consume stdout only are
    unaffected; pipelines that mix stdout and stderr should suppress
    with `2>/dev/null` or filter lines starting with `#`.
- **Forward byte-stability regression** — new test
  `tests/cli/test_v1_1_reference_byte_stable.py` pins the v1.1
  default `ketu --harmonics all aspects --date 2000-01-01T12:00:00Z`
  output (sha256 `067fa67672d2e3c727a30612364e4b9bb1699401768f4a8fc4819a0e951785ed`,
  fixture at `tests/cli/fixtures/v1_1_reference_output.txt`) — catches
  unintended format/encoding/header drift in future releases.
  (Phase 11 / CLI-03)

### Migration

See `UPGRADING.md` v1.0 -> v1.1 section for per-date v1.0 vs. v1.1
Lilith values, the action required, and downstream-consumer notes
(Kala, etc.). Non-Lilith bodies, cycles, harmonics, houses, and
aspect calculations are unaffected.

## [1.0.0] - 2026-02-12

### BREAKING CHANGES

**This is a MAJOR version bump. See [UPGRADING.md](UPGRADING.md) for detailed migration guide.**

#### Removed: Export modules (chart and icalendar)

Ketu 1.0 is a pure calculation library. Visualization and calendar export features have been removed:

- **Removed modules**: `ketu.export.chart`, `ketu.export.icalendar`
- **Removed functions**:
  - `draw_zodiacal_chart()` — Chart rendering with matplotlib/svgwrite
  - `export_lunations_to_ical()` — iCalendar lunation export
  - `export_aspects_to_ical()` — iCalendar aspect export
  - `export_transits_to_ical()` — iCalendar transit export
- **Removed constants**: `PLANETS_DEFAULT`, `BIG_FIVE` (from export module)
- **Why**: Ketu focuses on numerical calculations. Visualization and export belong in application layers (GUI, web dashboards, etc.)
- **Migration**: See [UPGRADING.md](UPGRADING.md) for migration paths, or pin to `ketu==0.4.0`

#### Removed: Optional dependencies

- **Removed**: matplotlib, icalendar, svgwrite as optional dependencies
- **Removed install extras**: `ketu[chart]`, `ketu[icalendar]`, `ketu[all]`
- **Core is now NumPy-only**: `pip install ketu` has zero optional extras
- **Why**: Simplifies installation and reinforces Ketu's role as a calculation library

#### Removed: Pandas dependency

- `generate_aspect_timeline()` now returns NumPy structured array (was DataFrame)
- `AspectTimeline.to_pandas()` method removed
- **Why**: Ketu's contract is NumPy-only. Pandas conversion is trivial if needed.
- **Migration**: Use `import pandas as pd; df = pd.DataFrame(timeline)` for manual conversion

#### Renamed: Velocity functions (breaking)

- `vlong()` → `long_velocity()`
- `vlat()` → `lat_velocity()`
- `vdist_au()` → `dist_velocity_au()`
- **Why**: Explicit names prevent confusion. The old "v" prefix was ambiguous.
- **Migration**: Use find-and-replace in your codebase (see [UPGRADING.md](UPGRADING.md))

#### Changed: Public API surface

- `ketu.__init__.py` exports only metadata + core constants (bodies, aspects, signs)
- Functions accessed via submodule imports: `from ketu.calculations import long`
- `ketu.__all__` explicitly lists public API
- **Why**: Clear public API boundary, better organization
- **Migration**: Most users won't notice this change. Use public API imports if importing from internal modules.

### Fixed (Correctness)

**IMPORTANT: These fixes change calculation results. Recompute cached 0.4.0 results.**

- **Cache operator precedence bug**: `use_cache=False` was ignored due to missing parentheses in boolean expression
- **Aspect vectorization non-determinism**: `calculate_aspects_vectorized()` now returns consistent results (pair duplication issue fixed)
- **Moon velocity wrapping**: Correct velocity at 360°/0° boundary using ±180° wrapping (was showing ±360° spikes)

### Added

- **Numerical precision guarantees**: ±1e-6° for angular separation (documented in docstrings)
- **Type hints for all public functions**: mypy strict mode compliance
- **NumPy-style docstrings**: Examples section in all public functions
- **Standardized error messages**: All `ValueError` messages include received value + valid options
- **Two-layer caching strategy**: LRU for single-point, EphemerisCache for batch (documented in cache/__init__.py)

### Changed

- **Complex number representation**: Used internally for cycle calculations (degrees externally)
- **Test coverage**: 91.48% overall (cache 89%, cycles 96%)
- **Test count**: 250 tests pass across all modules (was 126 in 0.4.0)
- **Documentation**: Comprehensive migration guide ([UPGRADING.md](UPGRADING.md)) following pandas 3.0 structure

### Performance

- **Vectorized batch ephemeris**: `calc_planet_position_batch()` eliminates Python loops
- **Cache efficiency**: Two-layer strategy optimizes for both single-point and batch use cases

## [0.4.0] - 2025-12-10

### Added

- **Aspect Timelines Module**: Complete ML-ready aspect timeline generation
  - `generate_aspect_timeline()`: Generate aspects between any two bodies
  - `AspectTimeline` class with ML-ready export methods (NumPy, Pandas, JSON)
  - `AspectEvent` dataclass with full cycle information
  - Time window approach (aspects between dates, not full cycles)
  - Complete cycle information (phase, velocity, separation, retrograde)
  - Pattern discovery tools for aspect clusters and retrograde periods
  - Full documentation in `docs/aspect_timelines.md`

- **Kala Integration**: Perfect pipeline from Ketu (ephemeris) to Kala (ML)
  - `KetuDataAdapter`: Convert AspectTimeline → enriched DataFrames
  - `AspectPatternDiscovery`: Discover patterns in aspect cycles
  - `generate_full_planetary_calendar()`: Generate all aspects for multiple planet pairs
  - Feature engineering with 27+ ML-ready features
  - Examples and documentation for complete integration

### Changed

- **Module Reorganization**: All aspect-related code consolidated into `ketu.aspects` package
  - `ketu.aspects.core`: Low-level aspect calculations
  - `ketu.aspects.calculator`: High-level aspect finding (formerly `ketu.aspects`)
  - `ketu.aspects.windows`: Aspect window detection (formerly `ketu.aspect_windows`)
  - `ketu.aspects.timelines`: ML-ready timelines (formerly `ketu.aspect_timelines`)
  - `ketu.aspects.transits`: Transit calculations (formerly `ketu.transits`)
  - All imports updated throughout codebase
  - Backward compatibility maintained through `ketu.__init__.py`

- **Documentation Restructuring**: Moved to single-source i18n workflow
  - Migrated from parallel EN/FR to sphinx-intl with PO translations
  - English as single source of truth in `docs/source/`
  - French translations in `docs/locale/fr/LC_MESSAGES/`
  - 558 translations migrated automatically (60%)
  - Professional translation workflow with industry-standard PO files

### Fixed

- All 126 tests passing after restructuring
- Import paths corrected throughout modules
- Export module compatibility maintained

### Performance

- Lunar calendar optimization: 11% faster (478ms → 427ms)
- Full lunar month (21 planet pairs): ~2.6 seconds
- Complete planetary calendar generation: <10 seconds for full year

### Documentation

- New `docs/aspect_timelines.md`: Complete aspect timeline documentation
- Kala integration guide: `kala/KETU_INTEGRATION.md`
- Examples:
  - `examples/aspect_timeline_demo.py`: 5 comprehensive demos
  - `examples/full_planetary_calendar.py`: Complete calendar generation
  - `examples/ketu_to_kala_data.py`: Export pipeline for ML
  - `kala/examples/ketu_kala_pipeline.py`: Full integration demo

### Technical

- Package structure:
  - New `ketu/aspects/` package for all aspect calculations
  - Cleaner separation of concerns
  - Better modularity and maintainability
- Test coverage: 94% for aspect timelines module
- All imports use absolute paths (`ketu.aspects.X`)
- Type hints and docstrings throughout

## [0.2.1] - 2025-10-27

- Minor fix...

## [0.2.0] - 2025-10-27

### Added 0.2.0

- Full packaging setup for a PyPI release
- `pyproject.toml` metadata and dependencies
- `requirements.txt` for a minimal install
- Public exports in `ketu/__init__.py`
- Expanded README with usage examples
- PyPI, Python versions, and license badges
- `MANIFEST.in` to ship data files
- GitHub Actions workflow for automated tests
- GitHub Actions workflow for PyPI publishing
- CI coverage for Python 3.9 through 3.13
- `ketu` CLI entry point
- Support for 13 celestial bodies (added True Node)
- English and French documentation

### Changed

- Fixed and hardened the unit tests
- Removed the obsolete `_timea.py` profiling helper
- Optimised package structure for distribution
- Aligned the documentation with the new layout

### Technical

- Official support for Python 3.10–3.13
- Pytest configuration embedded in `pyproject.toml`
- Coverage configuration for CI analysis
- Package installable via `pip install ketu`
- Works seamlessly in virtual environments

## [0.1.0] - 2024-01-XX

### Added 0.1.0

- Interactive CLI to compute positions and aspects
- Planetary position computations through pyswisseph
- Detection of major aspects with orb handling
- Conversion helpers between UTC and Julian Day
- Retrogradation detection
- Complete documentation with Sphinx and MyST
- Initial PyPI-ready packaging
- Foundational unit tests

### Features

- Support for 12 initial celestial bodies
- Seven major aspects (conjunction to opposition)
- Zodiac sign computations
- Orb system inspired by Abu Ma'shar
- LRU cache to improve performance
- Requires Python 3.9+
- Dependencies: numpy, pyswisseph
- Modular, documented codebase

## [0.0.1] - 2023-01-XX

### Initial

- Prototype groundwork
- Basic position calculations
- Command-line interface

---

## Versioning Convention

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible feature additions
- **PATCH**: Backward-compatible bug fixes

## Links

- [Version comparison](https://github.com/alkimya/ketu/compare/)
- [All releases](https://github.com/alkimya/ketu/releases)
