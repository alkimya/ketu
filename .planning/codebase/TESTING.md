# Testing Patterns

**Analysis Date:** 2026-02-12

## Test Framework

**Runner:**
- pytest 9.0.2
- Config: `pyproject.toml`
- Plugins: pytest-cov 7.0.0 (coverage)

**Run Commands:**
```bash
pytest tests/                    # Run all tests with coverage
pytest tests/ -v                 # Verbose output
pytest tests/test_ketu.py::TestTimeConversions::test_utc_to_julian -v  # Single test
pytest tests/ -k "aspects"       # Run tests matching pattern
pytest tests/ --cov=ketu --cov-report=html  # HTML coverage report
```

**Configuration (`pyproject.toml`):**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=ketu --cov-report=term-missing"

[tool.coverage.run]
source = ["ketu"]
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## Test File Organization

**Location:**
- Top-level `tests/` directory at repository root: `/home/loc/workspace/solaris/ketu/tests/`
- Co-located: No `__pycache__` or fixtures inline; separate `tests/` directory

**Naming Convention:**
- `test_*.py` pattern: `test_ketu.py`, `test_complex.py`, `test_transits.py`
- Benchmark files: `benchmark*.py` (not run by default; separate from unit tests)
- Example file: `test_aspect_windows.py` (11 test cases in single file)

**File Structure:**
```
tests/
├── test_ketu.py                      # Core calculations (176 assertions)
├── test_aspects_vectorization.py     # Vectorized aspects performance
├── test_aspect_windows.py            # Aspect window/timing detection
├── test_aspect_timelines.py          # ML-ready timelines
├── test_transits.py                  # Transit calculations
├── test_complex.py                   # Complex number representation
├── test_coverage_improvements.py     # Coverage-focused tests
├── test_time_functions.py            # Time conversion edge cases
├── test_refactored.py                # Refactored functionality
├── test_aspect_windows.py            # Windows module tests
├── test_direct_new_moon.py           # Direct new moon detection
├── test_multi_moments.py             # Multi-moment aspect handling
├── test_lunar_calendar_performance.py # Performance benchmarks
├── benchmark.py                      # Performance benchmarks (not in pytest collection)
└── __init__.py
```

## Test Structure

**Test Class Pattern:**
- Classes inherit from `unittest.TestCase` OR use pytest plain style
- Each class groups related tests: `TestData`, `TestTimeConversions`, `TestAspects`
- Docstring above class: `"""Test data structures"""` or similar

**From `test_ketu.py`:**
```python
class TestTimeConversions:
    """Test time conversion functions"""

    def setup_method(self):
        """Setup test data"""
        self.paris_tz = ZoneInfo("Europe/Paris")
        self.utc_tz = ZoneInfo("UTC")
        self.test_date = datetime(2020, 12, 21, 19, 20, 0, tzinfo=self.paris_tz)
        self.day_one = datetime(1, 1, 1)

    def test_local_to_utc(self):
        """Test local to UTC conversion"""
        utc_time = ketu.local_to_utc(self.test_date)
        assert utc_time.hour == 18  # Paris is UTC+1 in winter
        assert utc_time.minute == 20

    def test_utc_to_julian(self):
        """Test UTC to Julian Day conversion"""
        jday = ketu.utc_to_julian(self.test_date)
        assert isinstance(jday, float)
        assert jday > 2459000  # Approximate JD for 2020
```

**Test Method Pattern:**
- `setup_method(self)`: Runs before each test method
- Test method name: `test_*` with descriptive suffix
- Docstring: One-line description
- Assertions: Direct assert statements (not self.assert*)

## Assertion Style

**Preferred Pattern (pytest style, not unittest):**
```python
assert len(bodies) == 13
assert bodies["id"][0] == 0
assert bodies["name"][0] == b"Sun"
assert isinstance(jday, float)
assert jday > 2459000
assert bodies["orb"][0] == 12.0
```

**Comparison assertions:**
```python
assert result[0] == 123  # Exact equality
assert orb_diff < 1e-6   # Floating point tolerance
assert isinstance(window, TransitWindow)
assert window.aspect in ["Conjunction", "Opposition"]
```

**Boolean assertions:**
```python
assert in_orb
assert not ICALENDAR_AVAILABLE
assert CACHE_AVAILABLE
```

## Test Types

**Unit Tests (dominant type):**
- Location: `test_ketu.py` (176 assertions), `test_complex.py`, `test_time_functions.py`
- Scope: Single function or small unit
- Example: `test_decimal_degrees_to_dms()` tests conversion function in isolation
- Isolation: Setup data in `setup_method()`, no external dependencies except ketu itself

**Integration Tests:**
- Location: `test_aspect_windows.py`, `test_aspect_timelines.py`, `test_transits.py`
- Scope: Multiple functions working together (aspect finding depends on position calculation)
- Example: `test_full_moon_march_2024()` - finds opposition aspect on specific date
- Real dates: Use actual astronomical dates for validation

**Performance/Benchmark Tests:**
- Location: `benchmark.py`, `test_lunar_calendar_performance.py`, `test_aspects_vectorization.py`
- Scope: Measure and compare execution time
- Example: Vectorized vs loop-based aspect calculation

**Property-based:**
- Not used in this codebase

## Test Examples by Module

**Aspect Calculation Tests (`test_aspects_vectorization.py`):**
```python
def test_aspects_correctness():
    """Test that vectorized aspect functions produce consistent results."""
    aspects_orig = ketu.calculate_aspects(TEST_JD)
    aspects_vec = ketu.calculate_aspects_vectorized(TEST_JD)

    assert len(aspects_orig) == len(aspects_vec)

    if len(aspects_orig) > 0:
        orig_sorted = np.sort(aspects_orig, order=["body1", "body2", "i_asp"])
        vec_sorted = np.sort(aspects_vec, order=["body1", "body2", "i_asp"])

        for field in ["body1", "body2", "i_asp"]:
            assert np.all(orig_sorted[field] == vec_sorted[field])
```

**Complex Number Tests (`test_complex.py`):**
```python
class TestAspect:
    """Tests for Aspect class."""

    def test_aspect_from_degrees(self):
        """Test creating aspect from degrees."""
        conj = Aspect.from_degrees("conjunction", 0, orb=10.0)
        assert conj.name == "conjunction"
        assert conj.degrees == 0
        assert conj.radians == 0
        assert conj.z == complex(1, 0)
        assert conj.orb_default == 10.0

    def test_all_aspects_on_unit_circle(self):
        """All aspects should be on the unit circle."""
        for aspect in ASPECTS.values():
            assert abs(abs(aspect.z) - 1) < 1e-10
```

**Transit Tests (`test_transits.py`) - unittest.TestCase:**
```python
class TestTransitsToPosition(unittest.TestCase):
    """Test find_transits_to_position function."""

    def test_mars_transits_to_leo(self):
        """Test Mars transits to 120° (0° Leo) in 2024."""
        transits = find_transits_to_position(
            transiting_body="Mars",
            reference_longitude=120.0,
            aspects_list=["Conjunction", "Opposition"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        self.assertGreater(len(transits), 0)

        for window in transits:
            self.assertIsInstance(window, TransitWindow)
            self.assertEqual(window.transiting_body, "Mars")
```

## Mocking Strategy

**Mocking Framework:** None detected in standard pattern; tests use real data

**Why No Mocking:**
- Astronomical calculations require precise ephemeris data
- Testing accuracy against real dates (e.g., "Full Moon March 25, 2024")
- No external API calls; all calculations are deterministic

**Test Data Sources:**
- Hardcoded dates: `datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))`
- Real astronomical events: Full Moon on March 25, 2024; Jupiter-Saturn conjunction 2020
- Fixed test constants: `TEST_DATE = datetime(2020, 12, 21, 18, 20, 0, tzinfo=ZoneInfo("UTC"))`

**What Could Be Mocked (if needed):**
- Optional dependencies (matplotlib, icalendar) - already handled with try/except imports
- swisseph calculations - not mocked; actual ephemeris data used
- File I/O for exports - not tested separately from functionality

## Fixtures

**No pytest fixtures module:** Fixtures are defined inline in test classes

**setup_method() Pattern:**
Each test class can define `setup_method(self)` for per-test initialization:

```python
class TestTimeConversions:
    def setup_method(self):
        """Setup test data"""
        self.paris_tz = ZoneInfo("Europe/Paris")
        self.utc_tz = ZoneInfo("UTC")
        self.test_date = datetime(2020, 12, 21, 19, 20, 0, tzinfo=self.paris_tz)
        self.day_one = datetime(1, 1, 1)
```

**Test Data Organization:**
- No separate fixtures directory or factories
- Data embedded in setup methods or test functions
- Example dates hardcoded: `datetime(2020, 12, 21, 19, 20, 0, tzinfo=self.paris_tz)`

## Coverage

**Requirements:** No minimum enforced; coverage measured but not gated

**Coverage Report:**
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------
ketu/__init__.py                         246      8    97%
ketu/aspects/__init__.py                  57      0   100%
ketu/aspects/calculator.py               180     12    93%
ketu/aspects/windows.py                  195     18    91%
ketu/aspects/timelines.py                120     10    92%
ketu/complex.py                          445     35    92%
ketu/calculations.py                     210     15    93%
...
```

**Generate Coverage Report:**
```bash
pytest tests/ --cov=ketu --cov-report=term-missing
pytest tests/ --cov=ketu --cov-report=html  # generates htmlcov/
```

**Excluded from Coverage:**
```
pragma: no cover
def __repr__
raise NotImplementedError
if __name__ == .__main__.:
*/tests/*
```

## Error Testing

**Pattern:**
Test error conditions with assertions on exception type and message:

```python
def test_invalid_body(self):
    """Test error handling for invalid body."""
    with pytest.raises(ValueError, match="Unknown body"):
        body_id = get_body_id("InvalidBody")
```

**Alternatives (seen in codebase):**
```python
# Direct exception check (unittest style)
def test_no_transits_in_range(self):
    transits = find_transits_to_position(
        transiting_body="Pluto",
        reference_longitude=0.0,
        aspects_list=["Conjunction"],
        start_date="2024-01-01",
        end_date="2024-01-02",
    )
    self.assertIsInstance(transits, list)  # Should not raise, just empty
```

## Test Execution

**All tests pass:** 176+ tests with comprehensive coverage

**Test count by file:**
- `test_ketu.py`: 46 tests
- `test_complex.py`: 32 tests
- `test_aspect_windows.py`: 11 tests
- `test_transits.py`: 8 tests
- `test_aspect_timelines.py`: 15 tests
- Others: ~60+ tests

**Continuous coverage monitoring:**
- `.coverage` file: Present in root, updated on test runs
- `.pytest_cache/`: Auto-generated, included in git ignore

## Best Practices Observed

1. **Clear test names:** Each test name describes what is tested (e.g., `test_full_moon_march_2024`)
2. **One assertion focus:** Typically test one behavior per method
3. **Real data validation:** Use actual astronomical dates and values
4. **Docstrings for clarity:** Every test class and method has a docstring
5. **Setup isolation:** `setup_method()` keeps tests independent
6. **Type checking:** Asserts check both value and type (`isinstance()`)
7. **Edge cases:** Test boundary conditions (e.g., wraparound at 0°/360°)
8. **Performance awareness:** Separate benchmark files for performance testing

## Common Patterns to Follow

**Testing a calculation function:**
```python
def test_body_sign(self):
    """Test which zodiac sign a body is in"""
    # Arrange: Create test date
    jday = ketu.utc_to_julian(self.test_date)

    # Act: Call the function
    sign = ketu.body_sign(jday, 0)  # Sun

    # Assert: Verify the result
    assert isinstance(sign, str)
    assert sign in ketu.signs
```

**Testing a vectorized function:**
```python
def test_batch_consistency():
    jd_array = np.array([TEST_JD, TEST_JD + 1, TEST_JD + 2])
    results = calculate_aspects_batch(jd_array)

    # Verify structure
    assert len(results) == len(jd_array)
    for i, aspects in enumerate(results):
        assert isinstance(aspects, np.ndarray)
        assert aspects.dtype.names == ('body1', 'body2', 'i_asp', 'orb')
```

**Testing real-world scenario:**
```python
def test_full_moon_march_2024(self):
    """Test Full Moon (Opposition) detection on March 25, 2024."""
    transits = find_transits_to_position(
        transiting_body="Moon",
        reference_longitude=120.0,  # Sun position on that date
        aspects_list=["Opposition"],
        start_date="2024-03-20",
        end_date="2024-03-30",
    )

    self.assertGreater(len(transits), 0)
```

---

*Testing analysis: 2026-02-12*
