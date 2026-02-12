# Requirements: Ketu 1.0

**Defined:** 2026-02-12
**Core Value:** Cycle calculations must be correct, tested, and performant

## v1 Requirements

Requirements for 1.0.0 release. Each maps to roadmap phases.

### Bug Fixes

- [ ] **BUG-01**: Operator precedence in cache logic fixed — `use_cache=False` correctly disables cache
- [ ] **BUG-02**: Aspect vectorization is deterministic — `calculate_aspects_vectorized()` returns consistent count across all dates

### Module Removal

- [ ] **REM-01**: Export package removed — `ketu/export/` directory deleted (chart.py, icalendar.py, constants.py)
- [ ] **REM-02**: Optional dependencies removed from pyproject.toml — no matplotlib, icalendar, or `[chart]`/`[icalendar]`/`[all]` extras
- [ ] **REM-03**: Hidden Pandas dependency removed — `generate_aspect_timeline()` returns NumPy structured array, not DataFrame
- [ ] **REM-04**: Public API cleaned — `__init__.py` `__all__` audited, export-related functions removed, internals marked private

### Complex Math Integration

- [ ] **CPX-01**: Cycle engine uses complex numbers internally — angular separation computed via complex arithmetic, degrees as output
- [ ] **CPX-02**: ResonanceField vectorized — `_get_trace()` uses `calc_planet_position_batch()` instead of Python loop
- [ ] **CPX-03**: Caching strategies consolidated — single coherent caching approach (not LRU + EphemerisCache in parallel)

### Code Quality

- [ ] **QAL-01**: Error messages standardized — consistent ValueError/TypeError with context across all modules
- [ ] **QAL-02**: Pytest `slow` marker registered in pyproject.toml config

### Testing

- [ ] **TST-01**: Overall test coverage reaches 70%
- [ ] **TST-02**: `cycles/calculator.py` has tests covering cycle generation, aspect proximity, and edge cases
- [ ] **TST-03**: `cache/ephemeris_cache.py` has tests covering cache hit/miss, file I/O, and invalidation
- [ ] **TST-04**: All tests pass on Python 3.10-3.13

### Documentation & Release

- [ ] **DOC-01**: Documentation updated for 1.0 API — no references to chart, icalendar, matplotlib, or removed functions
- [ ] **DOC-02**: CHANGELOG.md has detailed BREAKING CHANGES section for 0.4.0 → 1.0.0
- [ ] **DOC-03**: Version bumped to 1.0.0 in pyproject.toml and `ketu/__init__.py`
- [ ] **DOC-04**: PyPI classifiers updated (Development Status :: 5 - Production/Stable)
- [ ] **DOC-05**: GitHub release created with tag v1.0.0
- [ ] **DOC-06**: Package published to PyPI

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Type Safety

- **TYP-01**: All public functions have complete type hints with `numpy.typing`
- **TYP-02**: `mypy --strict` passes in CI

### Platform Testing

- **PLT-01**: CI tests on Linux, macOS, Windows matrix
- **PLT-02**: NumPy 2.x compatibility verified

### Advanced

- **ADV-01**: Migration guide (UPGRADING.md) with code examples
- **ADV-02**: Release candidate (1.0.0rc1) published before final
- **ADV-03**: API surface audit targets 30-40 public functions (down from ~60)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Chart/SVG visualization | Removed — belongs in future GUI layer |
| iCalendar export | Removed — belongs in future GUI layer |
| Matplotlib dependency | Removed entirely |
| French documentation rebuild | Defer to post-1.0 |
| Real-time streaming | Not needed for batch analysis |
| Web API | Ketu is a library, not a service |
| swisseph re-integration | Already replaced with pure NumPy in v0.3.0 |
| Logging framework | Nice-to-have, not blocking 1.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BUG-01 | Phase ? | Pending |
| BUG-02 | Phase ? | Pending |
| REM-01 | Phase ? | Pending |
| REM-02 | Phase ? | Pending |
| REM-03 | Phase ? | Pending |
| REM-04 | Phase ? | Pending |
| CPX-01 | Phase ? | Pending |
| CPX-02 | Phase ? | Pending |
| CPX-03 | Phase ? | Pending |
| QAL-01 | Phase ? | Pending |
| QAL-02 | Phase ? | Pending |
| TST-01 | Phase ? | Pending |
| TST-02 | Phase ? | Pending |
| TST-03 | Phase ? | Pending |
| TST-04 | Phase ? | Pending |
| DOC-01 | Phase ? | Pending |
| DOC-02 | Phase ? | Pending |
| DOC-03 | Phase ? | Pending |
| DOC-04 | Phase ? | Pending |
| DOC-05 | Phase ? | Pending |
| DOC-06 | Phase ? | Pending |

**Coverage:**
- v1 requirements: 21 total
- Mapped to phases: 0
- Unmapped: 21

---
*Requirements defined: 2026-02-12*
*Last updated: 2026-02-12 after initial definition*
