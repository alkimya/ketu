# Testing Patterns

**Analysis Date:** 2026-05-29

## Test Framework

**Runner:**
- pytest 7.x+ (configured in `pyproject.toml` `[tool.pytest.ini_options]`)
- Config: `pyproject.toml` (no separate pytest.ini)

**Assertion Library:**
- Standard pytest assertions + `numpy.testing` for array comparisons
- `pytest.approx()` for floating-point tolerances (not used; explicit tolerance constants preferred)
- `np.testing.assert_array_almost_equal()` for multi-element arrays
- `np.testing.assert_array_equal()` for bit-exact equality (used when numpy dtypes must not drift)

**Test Collection:**
- `python_files = "test_*.py"`
- `python_classes = "Test*"`
- `python_functions = "test_*"`

**Run Commands:**
```bash
# Full suite with coverage report
python -m pytest tests/ -v
# Alternative via Makefile
make test

# Fast run (no coverage instrumentation)
make test-fast

# Specific subpackage (e.g., houses)
python -m pytest tests/houses/ -v

# Per-module coverage gate (see Makefile targets)
make houses-coverage      # ketu.houses >= 95%
make charts-coverage      # ketu.charts >= 95%
make synastry-coverage    # ketu.synastry >= 95%
make composite-coverage   # ketu.composite >= 95%
make returns-coverage     # ketu.returns >= 95%
make parts-coverage       # ketu.parts >= 95%

# Doc gates (docstring + type coverage)
make doc-gates
```

**Current Test Count:** 1286 tests collected

## Test File Organization

**Location:**
- Co-located under `tests/` directory mirroring `ketu/` structure
- Each subpackage has its own `tests/` subdirectory: `tests/houses/`, `tests/charts/`, `tests/returns/`, `tests/synastry/`, `tests/composite/`, `tests/parts/`, `tests/cli/`

**Naming:**
- Files: `test_<component>.py` (e.g., `test_api.py`, `test_dtype.py`, `test_oracle.py`)
- Classes: `Test<Feature>` (e.g., `TestSolarReturnDtype`, `TestSolarReturnResidual`)
- Functions: `test_<scenario>` (e.g., `test_compute_chart_returns_chart_dtype`)

**Structure:**
```
tests/
├── test_ketu.py                           # Core data (core.py) invariant tests
├── test_refactored.py                     # Legacy/refactored module smoke tests
├── test_error_messages.py                 # Error handling validation
├── test_*.py                              # Top-level module tests
├── houses/
│   ├── conftest.py                        # Oracle fixtures (swisseph gated)
│   ├── test_api.py                        # calculate_houses + house_of public API
│   ├── test_*.py                          # Per-system tests (placidus, koch, etc.)
│   └── fixtures/
│       └── reference_charts.json          # Snapshotted oracle results
├── charts/
│   ├── conftest.py                        # CHART_DTYPE fixtures
│   ├── test_compute_chart.py              # compute_chart integration tests
│   ├── test_aspect_matrix.py              # Dense aspect block validation
│   └── test_*.py
├── returns/
│   ├── conftest.py                        # Natal fixtures (Diana, Charles, etc.)
│   ├── test_solar_return.py               # RET-01..03 public API
│   ├── test_returns_oracle.py             # Oracle cross-checks (pyswisseph)
│   └── test_*.py
├── synastry/
│   ├── conftest.py                        # Oracle fixtures + natal pairs
│   ├── test_synastry.py                   # Public API (synastry, synastry_batch)
│   ├── test_oracle.py                     # SYN-05 oracle validation
│   └── fixtures/
│       └── oracle_*.json                  # Hand-validated charts (Diana/Charles, etc.)
├── composite/
│   ├── conftest.py                        # Oracle fixtures + natal pairs
│   ├── test_composite.py                  # Public API (calculate_composite)
│   ├── test_oracle.py                     # COMP-04 oracle validation
│   └── fixtures/
│       └── oracle_*.json                  # Hand-validated composite charts
├── parts/
│   └── test_*.py                          # Arabic Parts registry + calculation tests
└── cli/
    └── test_*.py                          # CLI command tests
```

## Test Structure

**Class Organization:**
Tests are organized into class-per-feature groups for clarity:

```python
class TestComputeChartDtype:
    """D-06: return dtype is CHART_DTYPE."""
    
    def test_returns_scalar_chart_dtype(self) -> None:
        """Scalar input returns 0-d CHART_DTYPE element."""
        chart = compute_chart(2451545.0, 48.86, 2.35)
        assert chart.dtype == CHART_DTYPE
        assert chart.shape == ()

class TestComputeChartMetadata:
    """Round-trip metadata: jd, lat, lon, system."""
    
    def test_meta_fields_populated(self) -> None:
        """jd, lat, lon, system round-trip from inputs."""
        # ...

class TestComputeChartHousesInline:
    """Houses-inline equivalence (D-03)."""
    
    @pytest.mark.parametrize("system", ["placidus", "koch"])
    def test_houses_match_calculate_houses(self, system: str) -> None:
        # ...
```

**Setup/Teardown:**
- Session-scoped fixtures for expensive oracles (swisseph calls)
- No explicit teardown (pytest auto-cleans fixtures)
- Example (`tests/returns/conftest.py`): `@pytest.fixture(scope="session")` for natal triples (Diana, Charles, Curie couple, Lennon/Ono)

**Assertion Patterns:**
```python
# Scalar field equality (bit-exact)
assert float(chart["jd"]) == 2451545.0

# Array equality (bit-exact for dtype roundtrip)
np.testing.assert_array_equal(chart_a["cusps"], chart_b["cusps"])

# Array equality with tolerance (floating-point)
np.testing.assert_array_almost_equal(chart_a["body_lons"], chart_b["body_lons"])

# Relative tolerance (rare; prefer absolute)
np.testing.assert_allclose(result, expected, rtol=1e-10, atol=0)

# Assertion messages include diagnostic context
assert residual < _TOL_DEG, (
    f"target_year={target_year}: residual={residual} deg exceeds {_TOL_DEG} deg"
)
```

## Mocking

**Framework:** NOT used extensively — library is math-focused with minimal external dependencies

**Test-only dependencies:**
- `pyswisseph` imported via `pytest.importorskip("swisseph")` in conftest.py
- Entire `tests/houses/` tree is SKIPPED (collected but marked skipped) when swisseph is absent
- Example (`tests/houses/conftest.py` line 59): `pytest.importorskip("swisseph")` at module level ensures the entire `tests/houses/` directory is skipped cohesively, not with piecemeal errors

**What to Mock:** None in production code — library uses NumPy and no network/file I/O.

**What NOT to Mock:** Oracle computations (swisseph); instead, compare against reference charts or snapshot fixtures.

## Fixtures and Factories

**Test Data:**
Highly curated hand-validated natal charts. No factories or randomized data generation.

**Fixtures** (`tests/*/conftest.py`):

1. **Natal Triples** (used across returns/synastry/composite):
   - `natal_diana` — Princess Diana, 1961-07-01 18:45 UT, Sandringham (52.83 N, 0.50 E)
   - `natal_charles` — Prince Charles, 1948-11-14 21:14 UT, London (51.50 N, -0.17 E)
   - `natal_marie_curie` — Marie Curie, 1867-11-07 10:36 UT, Warsaw (52.23 N, 21.01 E)
   - `natal_pierre_curie` — Pierre Curie, 1859-05-15 12:00 UT, Paris (48.85 N, 2.35 E)
   - `natal_lennon` — John Lennon, 1940-10-09 18:30 UT, Liverpool (53.41 N, -2.99 E)
   - `natal_ono` — Yoko Ono, 1933-02-18 20:30 UT, Tokyo (35.68 N, 139.69 E)
   
   All sourced from **AstroDatabank** (AA rating = high confidence).

2. **Oracle Fixtures** (snapshots):
   - `tests/houses/fixtures/reference_charts.json` — 10+ chart dicts spanning normal/mid/southern/1900/2050/polar latitudes
   - `tests/synastry/fixtures/oracle_diana_charles.json` — Synastry chart (Diana + Charles)
   - `tests/synastry/fixtures/oracle_curie.json` — Synastry chart (Marie + Pierre)
   - `tests/composite/fixtures/oracle_diana_charles.json` — Composite chart (Diana + Charles)
   - Similar for other couples

3. **CHART_DTYPE Fixtures** (`tests/charts/conftest.py`):
   - Session-scoped pre-computed `CHART_DTYPE` arrays for reference locations (Greenwich, Paris, Sydney, Tokyo, Buenos Aires, equator, NYC, Reykjavik)
   - Parametrized across systems and years

**Location:**
- Conftest files: `tests/<subpackage>/conftest.py`
- JSON snapshots: `tests/<subpackage>/fixtures/`

## Coverage

**Requirements:**
- Project-wide: >= 70% (fail_under in `pyproject.toml`)
- Per-module gates (Makefile targets):
  - `ketu.houses`: >= 95% (HOU-09)
  - `ketu.charts`: >= 95% (CHART-05)
  - `ketu.synastry`: >= 95% (SYN-05)
  - `ketu.composite`: >= 95% (COMP-05)
  - `ketu.returns`: >= 95% (RET-06)
  - `ketu.parts`: >= 95% (PARTS coverage gate)

**Current State (Partial Module Run):**
- `tests/charts` + `tests/returns` + `tests/composite` + `tests/synastry` + `tests/parts`: **478 tests collected**
- Full suite: **1286 tests collected**

**Modules at 100% coverage:**
- `ketu/charts/` (Phase 14 completion)
- `ketu/synastry/` (Phase 16 completion; synastry vectors + aspects)
- `ketu/composite/` (Phase 17 completion)
- `ketu/returns/` (Phase 18 completion)
- `ketu/parts/` (Phase 19 completion)

**Below 95% (as of last build):**
- `ketu/synastry/orbs.py`: 62% (26 lines, 10 uncovered — optional orb overrides not fully exercised)

**View Coverage:**
```bash
# Full report (after pytest run)
python -m coverage report

# HTML report
python -m coverage html && open htmlcov/index.html
```

**Exclude patterns** (`pyproject.toml`):
- `*/tests/*`
- `ketu/__main__.py`
- `ketu/lunar_calendar.py` (utility not in public API)

## Test Types

**Unit Tests:**
- Isolated function tests (e.g., `test_utc_to_julian` in `tests/test_time_functions.py`)
- Scope: single function or small helper
- No external dependencies (no swisseph)

**Integration Tests:**
- End-to-end API tests (e.g., `test_compute_chart_returns_chart_dtype`)
- Cover dtype contracts, parameter passing, houses-inline equivalence (D-03)
- Example: `tests/charts/test_compute_chart.py` validates `compute_chart` output against `calculate_houses` + `calc_planet_position_batch` primitives

**Oracle Tests:**
- Compare against pyswisseph reference implementation (test-only AGPL dep)
- Pattern: `test_oracle.py` in each subpackage (`tests/houses/`, `tests/synastry/`, `tests/composite/`)
- High tolerance: ≥0.0001° PRIMARY, then per-body tolerance for systematic error (e.g., Lilith ±0.001°)
- Example (`tests/synastry/test_oracle.py`): cross-check synastry aspects against swisseph positions

**E2E Tests:**
- CLI tests in `tests/cli/` (command-line parsing, output formatting)
- Lunar calendar tests (if enabled)

## Common Patterns

**Async Testing:**
Not applicable (library is synchronous NumPy-based).

**Error Testing:**
```python
def test_polar_latitude_raises(self) -> None:
    """|lat| > polar_circle(jd) raises HighLatitudeError."""
    with pytest.raises(HighLatitudeError) as exc_info:
        calculate_houses(jd=2451545.0, lat=80.0, lon=0.0, system="placidus")
    assert "polar" in str(exc_info.value).lower()
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
@pytest.mark.parametrize("target_year", [1980, 1990, 2000, 2010])
def test_residual_under_one_arcsecond(self, target_year: int) -> None:
    """RET-03: resolved Sun residual < 1 arc-second for all target years."""
    # ...
```

**Precision Testing:**
Tolerance constants defined at module level with docstring rationale:

```python
# tolerance for cross-checking inline bodies against underlying primitive
BODY_LONS_INLINE_TOL_DEG = 1e-12  # fp64 round-off headroom

# tolerance for solar/lunar return residual
_TOL_DEG = 0.0002777...  # 1 arc-second; binding per RET-03

# oracle comparison tolerance (pyswisseph)
PRIMARY_TOL = 0.0001  # degrees; body-default
LILITH_TOL = 0.001   # Black Moon systematic error
```

## Oracle-Test Pattern (Self-Consistency)

**Primary Validation (ketu vs ketu):**
- **Example:** `test_compute_chart_houses_inline_matches_calculate_houses` in `tests/charts/test_compute_chart.py`
- Calls `compute_chart()` and then separately `calculate_houses()`
- Compares the nested `chart["cusps"]` field against the direct `calculate_houses()` result
- Tolerance: **1e-12 degrees** (bit-exact; any drift is a regression)
- Purpose: detect unintended changes in house calculation pipeline or dtype casting

**Secondary Validation (ketu vs pyswisseph):**
- **Example:** `test_body_lons_match_oracle` in `tests/composite/test_oracle.py`
- Loads pre-computed oracle fixture (JSON snapshot of pyswisseph result)
- Calls `calculate_composite()` on the natal pair
- Compares body longitudes with tolerance **0.0001 degrees** (PRIMARY_TOL)
- Per-body tolerance overrides for systematic error (e.g., Lilith ±0.001°)
- Tolerance rationale documented in docstring

**Hand-Validated Fixture Curation:**
- **Diana + Charles** (synastry/composite): AA rating from AstroDatabank
- **Marie + Pierre Curie** (synastry): AA rating
- **John Lennon + Yoko Ono** (synastry): verified against multiple astro software
- Each fixture includes JD, lat, lon, and optionally pre-computed oracle body positions
- **Never modified** — if a fixture fails, the oracle call itself is re-run and the result is hand-verified

**Precision Ratchet:**
- Oracle tests use `pytest.mark.slow` and run separately (`make test` includes them; ad-hoc runs can skip with `-m "not slow"`)
- Per-body tolerance tuned after oracle snapshot capture (see `tests/synastry/test_oracle.py` for tolerance mappings)

## Markers and Gating

**Pytest Markers** (defined in `pyproject.toml`):
- `slow`: marks tests as slow; deselect with `-m "not slow"` if needed
- `charts_coverage_gate`: CHART-05 95% gate for `ketu.charts` (run via `make charts-coverage`)
- `composite_coverage_gate`: COMP-05 95% gate for `ketu.composite` (run via `make composite-coverage`)
- `houses_coverage_gate`: HOU-09 95% gate for `ketu.houses` (run via `make houses-coverage`)
- `parts_coverage_gate`: PARTS >=95% gate for `ketu.parts` (run via `make parts-coverage`)
- `returns_coverage_gate`: RET-06 95% gate for `ketu.returns` (run via `make returns-coverage`)
- `synastry_coverage_gate`: SYN-05 95% gate for `ketu.synastry` (run via `make synastry-coverage`)

**Doc Gates** (CI-only, blocking):
- `interrogate ketu/` — 95% docstring coverage
- `numpydoc lint <files>` — numpydoc style validation (GL01 summary-placement blocker)
- `mypy --strict ketu/` — type checking with strict mode
- All three gates block builds

## Key Test Invariants

**Phase 9 (ASP-01):**
- `core.aspects` row order, count, dtype, byte-level fingerprint pinned via `test_aspects_byte_fingerprint`
- Append-only invariant: rows 0–13 must never change

**Phase 10 (HOU-05, HOU-09):**
- `HOUSES_DTYPE` structure pinned to support Kala consumer positional indexing
- Per-system accuracy vs swisseph oracle

**Phase 14 (D-03, D-06):**
- Houses inline = bit-for-bit equivalent to `calculate_houses()` call (no intermediate casts)
- Aspect matrix diagonal contains sentinel values (no body has aspect with itself)

**Phase 17–19:**
- Composite, synastry, returns, parts all at 100% coverage
- Oracle tests validate against pyswisseph (test-only, AGPL-bounded)

---

*Testing analysis: 2026-05-29*
