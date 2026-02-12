# Changelog

> Consultez la version française dans `fr/CHANGELOG.md`.

All notable changes to Ketu are documented here.

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
format and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
