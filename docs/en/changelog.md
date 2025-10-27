# Changelog

All notable changes to Ketu are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-10-27

- Minor fix

## [0.2.0] - 2025-10-27

### Added

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
- Renamed `timea.py` to `_timea.py` (private module)
- Optimised package structure for distribution
- Aligned the documentation with the new layout

### Technical

- Official support for Python 3.10–3.13
- Pytest configuration embedded in `pyproject.toml`
- Coverage configuration for CI analysis
- Package installable via `pip install ketu`
- Works seamlessly in virtual environments

## [0.1.0] - 2024-01-XX

### Added

- Interactive CLI to calculate positions and aspects
- Planetary position calculations via pyswisseph
- Detection of major aspects with orbs
- Conversions between time systems (UTC, Julian)
- Retrogradation detection
- Complete documentation with Sphinx and MyST
- Installable PyPI package
- Initial unit tests

### Features

- Support for 10 planets + Rahu + Lilith
- 7 major aspects (conjunction through opposition)
- Zodiac sign calculations
- Orb system based on Abu Ma'shar
- LRU cache to improve performance

### Technical

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
