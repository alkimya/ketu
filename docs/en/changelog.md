# Changelog

All notable changes to Ketu are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Remove the pyswisseph dependency
- Implement planetary computations with pure NumPy
- Find exact aspect timings between two dates
- Generate aspect calendars
- Provide an API for progressions and directions

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
