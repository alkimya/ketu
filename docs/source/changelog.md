# Changelog

All notable changes to Ketu are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-XX

### Added 1.3.0

- **Chiron (14th body, body_id=13)**: Centaur body between Saturn and Uranus. Computed via embedded Chebyshev polynomial coefficients (`.npz`), valid range 1950–2050, max error 0.005695° (sub-arcminute). Accessed via standard calculation functions: `long(jd, 13)`, `lat(jd, 13)`, etc.
- **`ketu/data/chiron_coeffs.npz`**: Embedded coefficient file (1142 segments, seg=32 days, degree=10, three quantities: longitude, latitude, distance). Generated offline from pyswisseph — not a runtime dependency.
- **`ketu/ephemeris/chiron.py`**: Pure-NumPy Chebyshev evaluator for Chiron positions.

### Breaking Changes 1.3.0

- **`CHART_DTYPE` body axis expanded from 13 to 14 bodies (D-08)**: `body_lons`, `body_lats`, `body_speeds` arrays are now shape `(14,)` instead of `(13,)`. The aspect matrices are now `(14, 14)`. Code that hardcodes the body count or uses index 12 as the last body must be updated. Index 13 = Chiron.
- **`SYNASTRY_BODY_COUNT` changed from 15 to 16**: Reflects the additional Chiron body (14 bodies + ASC + MC).

See [Migration Guide](migration.md) for upgrade instructions.

## [1.2.0] - 2026-04-XX

### Added 1.2.0

- **`ketu.charts` — Full natal chart (`compute_chart`)**: Returns a single `CHART_DTYPE` structured array combining body positions (13 bodies), house cusps, angles (ASC, MC, ARMC, Vertex), and a 13×13 aspect matrix. `is_day_chart(jd, lat, lon)` sect helper.
- **`ketu.synastry` — Inter-chart aspect analysis**: `calculate_synastry(chart_a, chart_b, aspects, orbs, mode)` returns `SYNASTRY_DTYPE` structured array with applying/separating flag and orb limits.
- **`ketu.composite` — Midpoint composite charts**: `calculate_composite(chart_a, chart_b, system)` returns a `CHART_DTYPE` where each body position is the shortest-arc circular midpoint. `circular_midpoint(lon_a, lon_b)` utility.
- **`ketu.returns` — Solar and lunar returns**: `solar_return(natal_jd, …, target_year)` and `lunar_return(natal_jd, …, target_jd)` both return `CHART_DTYPE` for the return chart. Support relocation via `return_lat/return_lon`.
- **`ketu.parts` — Arabic Parts / Hermetic Lots**: Registry-based system with built-in `fortune`, `spirit` (sect-aware Fortune/Spirit), and `marriage` (fixed formula). `calculate_part`, `calculate_all_parts`, `register`, `get_part`, `PartSpec`.
- **Additional house systems**: Whole Sign (`whole_sign`), Equal (`equal`), Regiomontanus (`regiomontanus`) added alongside the existing Placidus, Koch, Porphyry (v1.1).
- **Ephemeris refactor**: `ORBITAL_ELEMENTS` extracted to `_elements.py`; `apply_perturbations` to `_perturbations.py`; `orbital.py` is now a 70-LOC re-export hub.
- **BODY_STRATEGIES dispatch**: `planets.py` uses a strategy dict instead of if-elif chains, making body extension (e.g. Chiron in v1.3) clean.
- **Root `conftest.py`**: Shared session-scoped fixtures consolidated in `tests/conftest.py`.

## [1.1.0] - 2026-03-XX

### Added 1.1.0

- **`ketu.aspects` — Configurable aspect sets**: `CLASSICAL` (5 aspects), `TRADITIONAL` (7), `EXTENDED` (14 — default). `AspectSetSpec = Union[str, list, ndarray, None]`, `resolve_aspect_set`. `calculate_aspects(jdate, l_bodies, aspects=None)` now accepts an aspect-set spec.
- **`ketu.houses` — House system calculations**: `calculate_houses(jd, lat, lon, system, polar_fallback)`, `house_of(planet_lon, cusps)`, `HOUSES_DTYPE`, `SYSTEMS`, `HighLatitudeError`, `register`. Initial systems: `placidus`, `koch`, `porphyry`.
- **`HOUSES_DTYPE`**: Structured array with fields `jd`, `lat`, `lon`, `system`, `cusps[12]`, `asc`, `mc`, `armc`, `vertex`.

## [1.0.0] - 2026-02-12

### Breaking Changes 1.0.0

- **Removed export modules**: `ketu.export.chart`, `ketu.export.icalendar` — Ketu is now a pure calculation library
- **Removed pandas dependency**: `generate_aspect_timeline()` returns NumPy structured array; use `pd.DataFrame(timeline)` for manual conversion
- **Renamed velocity functions**: `vlong()` → `long_velocity()`, `vlat()` → `lat_velocity()`, `vdist_au()` → `dist_velocity_au()`
- **Public API surface**: `ketu.__init__.py` exports only metadata + core constants; functions accessed via submodule imports

### Fixed 1.0.0

- **Cache operator precedence bug**: `use_cache=False` was ignored due to missing parentheses
- **Aspect vectorization non-determinism**: `calculate_aspects_vectorized()` now returns consistent results
- **Moon velocity wrapping**: Correct velocity at 360°/0° boundary (was showing ±360° spikes)

### Added 1.0.0

- **Type hints everywhere**: mypy strict mode compliance
- **NumPy-style docstrings**: Examples section in all public functions
- **Standardized error messages**: All `ValueError` messages include received value and valid options
- **Numerical precision guarantees**: ±1e-6° for angular separation (documented)
- **98% test coverage**: 408 tests across all modules

## [0.4.0] - 2026-01-14

### Added 0.4.0

- **Complex Engine**: New `ketu.complex` module using $e^{i\theta}$ representation for cycles.
- **Expanded Aspects**: Support for 14 aspects (Harmonics H1-H6, H9, H10).
- **Ephemeris Cache**: Persistent cache for O(1) position lookups.
- **Vectorized Cycles**: Refactored `ketu.cycles` to use complex vector operations.
- **ML Features**: Direct generation of Machine Learning features (`cos_phase`, `sin_phase`).

## [0.3.0] - 2025-12-XX

### Added 0.3.0

- **Pure NumPy**: Removed dependency on `pyswisseph` binary.
- **New Modules**: `ketu.ephemeris`, `ketu.cycles`.
- **Performance**: Significant speedups in time series generation.

## [0.2.1] - 2025-10-27

- Minor fix

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

### Changed 0.2.0

- Fixed and hardened the unit tests
- Renamed `timea.py` to `_timea.py` (private module)
- Optimised package structure for distribution
- Aligned the documentation with the new layout

### Technical PyPI deployment 0.2.0

- Official support for Python 3.10–3.13
- Pytest configuration embedded in `pyproject.toml`
- Coverage configuration for CI analysis
- Package installable via `pip install ketu`
- Works seamlessly in virtual environments

## [0.1.0] - 2024-01-XX

### Added 0.1.0

- Interactive CLI to calculate positions and aspects
- Planetary position calculations via pyswisseph
- Detection of major aspects with orbs
- Conversions between time systems (UTC, Julian)
- Retrogradation detection
- Complete documentation with Sphinx and MyST
- Installable PyPI package
- Initial unit tests

### Features 0.1.0

- Support for 10 planets + Rahu + Lilith
- 7 major aspects (conjunction through opposition)
- Zodiac sign calculations
- Orb system based on Abu Ma'shar
- LRU cache to improve performance

### Technical 0.1.0

- Requires Python 3.9+
- Dependencies: numpy, pyswisseph
- Modular architecture
- Documented, typed code

## [0.0.1] - 2023-01-XX

### Initial

- Prototype
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
