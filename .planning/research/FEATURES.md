# Feature Landscape

**Domain:** Python astronomical calculation library
**Researched:** 2026-02-12
**Confidence:** MEDIUM (based on established Python scientific library conventions and NumPy ecosystem practices)

## Table Stakes

Features users expect from a 1.0 production scientific Python library. Missing any = users perceive library as incomplete or immature.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Full type hints** | Standard since Python 3.5, required for IDE support, static analysis | Low | All public functions, return types, numpy.typing for arrays |
| **Semantic versioning** | 1.0 = API stability promise | Low | SemVer 2.0: MAJOR.MINOR.PATCH |
| **API stability guarantees** | 1.0 = public API won't break in minor releases | Low | Documented in CONTRIBUTING or API docs |
| **Deprecation policy** | How breaking changes are communicated | Low | 2-version deprecation window is standard |
| **Comprehensive docstrings** | NumPy/SciPy standard format | Medium | Parameters, Returns, Examples, Notes sections |
| **Error messages with context** | Scientific users need to understand WHY calculation failed | Medium | Include input values, valid ranges, what violated |
| **Input validation** | Catch bad inputs before swisseph crashes | Low | Check date ranges, body names, array shapes |
| **Vectorized operations** | NumPy users expect array inputs to work | Medium | Already have structured arrays, ensure all funcs accept them |
| **Numerical accuracy documentation** | Users need to know precision limits | Medium | Document swisseph precision, rounding behavior, edge cases |
| **Examples in docstrings** | Every public function needs working example | Low | Copy-paste ready, use real dates/values |
| **Package metadata** | PyPI classifiers, keywords, license | Low | Setup.py/pyproject.toml complete |
| **Versioned documentation** | Docs for each release | Low | ReadTheDocs or similar |
| **Clean __all__ exports** | Explicit public API surface | Low | Only export intended public functions |
| **Changelog** | What changed between versions | Low | Keep-a-Changelog format, already exists |

## Differentiators

Features that distinguish Ketu from alternatives (skyfield, pyephem, astropy). Not expected, but provide competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **NumPy structured arrays** | ML-ready output, zero-copy to pandas/polars | Low | Already implemented (CYCLE_DTYPE), extend to all outputs |
| **Complex number representation** | Elegant cycle math, resonance detection | Medium | Already in resonance.py, integrate into core API |
| **Performance benchmarks** | Prove speed vs alternatives | Medium | Benchmark vs skyfield for common operations |
| **Minimal dependencies** | swisseph + numpy only = easy deployment | Low | Already achieved, maintain this |
| **Financial domain focus** | Cycles optimized for trading analysis | Low | DEFAULT_PAIRS chosen for finance, document this |
| **Batch calculation optimization** | Faster than loop-based alternatives | Medium | Vectorization already present, document performance gains |
| **Readable source code** | Scientists want to understand calculations | Low | Code clarity over cleverness |

## Anti-Features

Features to explicitly NOT build for 1.0. Scope creep risks or out-of-domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Chart visualization** | Not a calculation library's job, many better tools exist | Remove export/chart.py (already planned), point users to matplotlib/plotly |
| **iCalendar export** | Domain drift, maintenance burden | Remove export/icalendar.py (already planned), not core value |
| **GUI or CLI** | Scope creep, hard to maintain | Stay library-only, users can build their own |
| **Data fetching** | Not astronomical calculation | No price data, no API clients, pure calculation only |
| **Built-in caching beyond ephemeris** | Complex cache invalidation, user responsibility | Keep ephemeris_cache.py for swisseph only, remove other caching |
| **Configuration files** | Python API is configuration | No config files, no environment variables, pure functions |
| **Astrology interpretations** | Subjective, out of scope | Calculations only, no "meaning" of aspects |
| **Historical calendar conversions** | Astronomical calendar is sufficient | No Julian/Gregorian edge cases beyond what swisseph provides |
| **Orbital mechanics simulation** | Different domain (use poliastro) | Use swisseph results, don't reimplement orbital math |
| **Multi-language support** | English docs sufficient for scientific library | English-only for 1.0 |

## Feature Dependencies

```
Type hints → API stability (can't change types without breaking)
Input validation → Error messages (validation failures need clear errors)
Vectorization → NumPy structured arrays (arrays enable vectorization)
Examples in docstrings → Versioned docs (examples must stay current)
Semantic versioning → Deprecation policy (versions enable deprecation windows)
```

## Testing Expectations

Scientific Python libraries have higher testing standards than typical packages.

| Test Type | Why Required | Complexity | Coverage Target |
|-----------|--------------|------------|-----------------|
| **Unit tests** | Basic correctness | Low | 70% line coverage (already targeted) |
| **Numerical accuracy tests** | Verify vs known astronomical events | Medium | All calculations vs JPL Horizons or similar |
| **Edge case tests** | Date boundaries, invalid inputs | Low | Extreme dates, missing bodies, bad arrays |
| **Property-based tests** | Invariants (e.g., full moon phase always ~180°) | Medium | Use Hypothesis for cycle properties |
| **Regression tests** | Prevent known bugs from returning | Low | Add test for every fixed bug |
| **Performance regression tests** | Catch slowdowns | Medium | Benchmark suite in CI |
| **Docstring example tests** | Examples stay valid | Low | Use doctest or pytest-examples |

## MVP Recommendation

For 1.0 consolidation, prioritize in order:

### Phase 1: API Cleanup (Foundation)
1. **Clean __all__ exports** - Define public API surface
2. **Full type hints** - Enable static analysis
3. **Input validation** - Prevent silent failures
4. **Remove anti-features** - Delete chart/icalendar exports

### Phase 2: Documentation (Communication)
5. **Comprehensive docstrings** - NumPy format with examples
6. **API stability guarantees** - Document versioning policy
7. **Deprecation policy** - How to handle breaking changes
8. **Numerical accuracy docs** - Precision limits and edge cases

### Phase 3: Quality (Trust)
9. **Edge case tests** - Boundary conditions
10. **Docstring example tests** - Keep examples working
11. **Error messages with context** - Better debugging
12. **70% test coverage** - Already targeted

### Phase 4: Differentiation (Value)
13. **NumPy structured arrays everywhere** - ML-ready outputs
14. **Performance benchmarks** - Prove speed advantage
15. **Complex number integration** - Resonance API

Defer for post-1.0:
- **Property-based tests**: HIGH value but can come after 1.0
- **Performance regression CI**: Once benchmarks exist
- **Versioned docs hosting**: Can use GitHub releases until traffic justifies RTD

## 1.0 Semantic Guarantees

What "1.0" promises to users:

| Aspect | Guarantee |
|--------|-----------|
| **Public API** | Breaking changes only in MAJOR versions (2.0, 3.0, etc.) |
| **Function signatures** | Parameters won't change in minor versions (1.1, 1.2) |
| **Return types** | Structured array fields won't be removed in minor versions |
| **Behavior** | Bug fixes allowed, but calculation changes documented |
| **Dependencies** | Major version bumps (numpy 2.x → 3.x) require Ketu major bump |
| **Python version** | Support policy (e.g., "follows NEP 29" for 3-year support) |
| **Deprecations** | 2-version window: deprecate in 1.1, remove in 1.3 |

## API Design Patterns

What a "clean" NumPy-based API looks like:

### Pattern 1: Consistent Input/Output Types
```python
# Good: Always return structured arrays
def planetary_positions(timestamps: np.ndarray, bodies: list[str]) -> np.ndarray:
    """Returns structured array with dtype [('timestamp', 'datetime64[s]'), ('lon', 'f8'), ...]"""

# Bad: Sometimes dict, sometimes array
def planetary_positions(...) -> dict | np.ndarray:
```

### Pattern 2: Explicit Parameters Over Magic
```python
# Good: Explicit orb
def find_aspects(timestamps, body1, body2, orb_degrees=8.0):

# Bad: Global config
ASPECT_ORB = 8.0  # Module-level config is hidden dependency
def find_aspects(timestamps, body1, body2):
```

### Pattern 3: Vectorization by Default
```python
# Good: Accept scalar or array
def cycle_phase(timestamp: datetime | np.ndarray) -> float | np.ndarray:
    timestamps = np.atleast_1d(timestamp)
    # ... calculate ...
    return result if result.shape == (1,) else result

# Bad: Separate functions for scalar/vector
def cycle_phase(timestamp: datetime) -> float:
def cycle_phases(timestamps: np.ndarray) -> np.ndarray:
```

### Pattern 4: Named Constants Over Magic Numbers
```python
# Good: Named
CONJUNCTION = 0.0
OPPOSITION = 180.0

# Bad: Magic numbers in code
if separation < 0.1:  # What does 0.1 mean?
```

## Error Handling Strategy

Scientific libraries need informative errors:

```python
# Good: Context and guidance
raise ValueError(
    f"Invalid date {timestamp}: swisseph supports years -13200 to 16800. "
    f"For historical dates beyond this range, consider using JPL Horizons."
)

# Bad: Cryptic
raise ValueError("Invalid date")
```

Error categories:
- **ValueError**: Invalid input (bad date, unknown body, negative orb)
- **TypeError**: Wrong type (string instead of datetime)
- **RuntimeError**: Swisseph calculation failed (ephemeris file missing)
- **NotImplementedError**: Feature explicitly not supported

## Sources

**Confidence: MEDIUM**

Based on established conventions in the Python scientific ecosystem. No web sources accessed due to permission constraints, but these practices are well-documented in:

- NumPy Enhancement Proposals (NEPs), particularly NEP 29 (Python version support)
- SciPy contributor guide (docstring format, testing standards)
- Scientific Python Ecosystem Coordination (SPEC) documents
- Semantic Versioning 2.0.0 specification
- Python Packaging Authority (PyPA) guidelines

**Verification needed:**
- Current year (2026) best practices may have evolved
- Specific competitor analysis (skyfield, astropy API patterns)
- Latest NumPy typing conventions (numpy.typing evolution)

**Recommendation:** Cross-reference with official NumPy/SciPy documentation and examine 2-3 mature scientific Python libraries (scipy, scikit-learn, astropy) for current API patterns before finalizing 1.0 API surface.
