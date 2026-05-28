# Coding Conventions

**Analysis Date:** 2026-05-29

## Naming Patterns

**Files:**
- Lowercase with underscores: `ephemeris_cache.py`, `aspect_windows.py`
- Test files match source: `test_api.py` mirrors `api.py`
- Module-level private symbols: prefix with `_` (e.g., `_CORE_ASPECTS`, `_TOL_DEG`)

**Functions:**
- Lowercase with underscores: `calculate_aspects`, `calc_planet_position`
- Public API functions: no leading underscore
- Private helpers in same file: `_vectorised_body_properties`, `_signed_residual_deg`
- Vectorized operations: explicit `*_vectorized` or `*_batch` suffix (e.g., `calculate_aspects_vectorized`, `calc_planet_position_batch`)

**Variables:**
- Snake_case for local variables and parameters: `jd`, `lat`, `lon`, `body_id`, `aspect_orbs`
- Constants: UPPERCASE with underscores: `BODY_COUNT`, `MERCURY_RETRO_JD`, `SYSTEM_BYTES`
- Session-scoped fixture names: descriptive lowercase with underscore prefix: `natal_diana`, `natal_charles`

**Types:**
- Class names: PascalCase: `PartSpec`, `HighLatitudeError`, `AspectSetSpec`
- Type aliases: PascalCase or descriptive: `ArrayLike`, `PartFormula`
- NumPy structured array dtypes: uppercase with underscore: `HOUSES_DTYPE`, `CHART_DTYPE`, `CYCLE_DTYPE`

## Code Style

**Formatting:**
- Black-style formatting (inferred from codebase consistency)
- Line continuations: implicit multiline within function signatures and tuples
- Imports: organized by group (stdlib, third-party, local) with blank line separators

**Linting:**
- mypy --strict mode enabled (see pyproject.toml `[tool.mypy]`)
- Type hints required everywhere (except test modules which have `disallow_untyped_defs = false`)
- No `# type: ignore` without explicit discussion; pragma comments require justification

**Docstrings:**
- **Style:** numpydoc (NumPy docstring format; see `[tool.interrogate] style = "sphinx"`)
- **CRITICAL: Summary placement** — The summary line MUST be on the line AFTER the opening `"""`, NOT on the same line. This is a BLOCKING requirement in CI (`numpydoc lint`):
  ```python
  # CORRECT:
  def foo():
      """
      One-line summary here.
      
      Longer description (optional).
      """
  
  # INCORRECT (GL01 gate failure):
  def foo():
      """One-line summary here."""
  ```
- **Coverage gate:** `interrogate >= 95%` fail-under enforced in CI; missing docstrings block the build
- **Sections used:**
  - `Parameters` (with types, via `type: description` syntax)
  - `Returns` (with type and description)
  - `Raises` (exceptions that can be raised)
  - `Notes` (implementation details, algorithm notes, precision info)
  - `Examples` (code examples; often omitted for internal helpers)
  - `See Also` (cross-references to related functions)
  - `Attributes` (for classes and dataclasses)
- **Example from codebase** (`ketu/core.py`):
  ```python
  """
  Core data structures and constants for Ketu astrological calculations.

  This module contains the fundamental astronomical and astrological data structures
  used throughout the Ketu library, including planetary bodies, aspects, and zodiac signs.

  Notes
  -----
  Orb values are inspired by medieval Islamic astronomers...
  """
  ```

## Import Organization

**Order:**
1. `from __future__ import annotations` (if used, for forward-reference string literals)
2. Standard library imports (`datetime`, `json`, `pathlib`, etc.)
3. Third-party imports (`numpy`, `pytest` in tests)
4. Local imports (`from ketu.core import`, `from .api import`)
5. Blank line before each group

**Path Aliases:**
- Relative imports within package: `.api`, `.core`, `.registry` (e.g., `from .api import calculate_part`)
- Absolute imports when crossing subpackage boundaries: `from ketu.core import bodies`
- Rename on import to avoid name collision: `from ketu.core import aspects as _CORE_ASPECTS` when the parameter name needs to be free (e.g., in `calculate_aspects(aspects=...)`), see `ketu/aspects/calculator.py`

**Module-level constants** (often imported):
- Pinned at top after docstring and imports
- Documented with inline comments explaining origin or usage
- Example (`ketu/core.py`): `EXPECTED_ASPECT_FINGERPRINT_V1 = "c5bd177..."`

## Error Handling

**Pattern:** Custom exception classes inherit from standard exceptions for semantic clarity:
- `class HighLatitudeError(ValueError)` in `ketu/houses/core.py` — raised when `|lat| > polar_circle` for latitude-dependent house systems
- Exceptions carry diagnostic context: `HighLatitudeError` includes the latitude, system name, and polar limit in its message

**Validation:**
- Explicit type hints + mypy --strict + runtime asserts for critical invariants
- Example (`tests/test_ketu.py`): assertions pinning v1.0 core.aspects byte fingerprint to catch unintended dtype changes
- Example (`ketu/returns/_solve.py`): tolerance constant `_TOL_DEG = 0.0002777...` (1 arc-second) with explicit bounds testing

**None / Sentinel values:**
- Use explicit `None` for optional parameters: `return_lat=None` defaults to natal lat
- No sentinel types; clear intent via docstring `default: "raise"` vs `"porphyry"`

## Logging

**Framework:** Standard library `logging` module (not used extensively):
- Console output via `print()` for CLI utilities (see `ketu/display.py`)
- Tests use assertions + pytest output capture; no logging instrumentation in library code

**When to log:** Not applicable — library is math-focused, no runtime logging infrastructure.

## Comments

**When to Comment:**
- Explain WHY, not WHAT: comments describe algorithm choice or non-obvious logic
- Example (`ketu/houses/api.py` line 28–29): `"The Python overhead is constant in S (Pitfall 1 from RESEARCH §5)."` — references research document
- Example (`tests/houses/conftest.py` line 33–43): `"IMPORTANT: numpy MUST be imported BEFORE swisseph..."` — unusual import ordering with explanation

**Docstrings vs Inline Comments:**
- Use docstrings for public APIs; use inline comments for algorithms and gotchas
- Comments on non-obvious computational lines, e.g., `B = 0` branch for pre-Gregorian calendars in `utc_to_julian`

## Function Design

**Size:** Functions are compact, typically 5–50 lines:
- Vectorized functions intentionally loop over bodies (not timestamps), keeping Python loop count constant: see `_vectorised_body_properties` in `ketu/charts/api.py` (lines 57–105)
- Helper functions extracted to reduce cognitive load (e.g., `_signed_residual_deg` for solar/lunar return residuals)

**Parameters:**
- Type hints on all parameters (mypy --strict enforced)
- No default mutable arguments; `None` as default with explicit None-checks
- Positional parameters for required inputs; keyword-only parameters with `*` separator for options:
  ```python
  def calculate_houses(
      jd: ArrayLike,
      lat: ArrayLike,
      lon: ArrayLike,
      system: str = "placidus",
      polar_fallback: Literal["raise", "porphyry"] = "raise",
  ) -> np.ndarray:
  ```

**Return Values:**
- Structured arrays (NumPy dtypes) for multi-field results: `CHART_DTYPE`, `HOUSES_DTYPE`, `CYCLE_DTYPE`
- Scalar values wrapped in 0-d arrays when consistency with batch paths is needed
- Type hint return type explicitly (no `Any`; mypy checks return-value assignments)

## Module Design

**Exports:**
- Public API via `__all__` list in `__init__.py` (e.g., `ketu.houses` exports `calculate_houses`, `HighLatitudeError`)
- Private symbols prefixed with `_` (e.g., `_CORE_ASPECTS`, `_vectorised_body_properties`)
- Submodules own their exports; cross-module imports are explicit (no `from .* import *`)

**Barrel Files:**
- `ketu/__init__.py` imports and documents all public submodules and top-level APIs
- `ketu/parts/__init__.py` calls `register()` on built-in parts; users register custom parts via `from ketu.parts.registry import register`
- `ketu/houses/registry.py` is analogous for house systems

## Frozen Structured Arrays

**Convention:** NumPy structured array dtypes are treated as immutable once defined:
- Defined once at module load time (e.g., `CHART_DTYPE` in `ketu/charts/core.py`)
- Changes to dtype fields require explicit review and version bump (v1.2 bumped `HOUSES_DTYPE["system"]` from U10 to U16 for `"regiomontanus"`)
- Byte-level fingerprints tested in CI (e.g., `test_aspects_byte_fingerprint` in `tests/test_ketu.py`) to catch unintended dtype changes

**Example usage:**
```python
CYCLE_DTYPE = np.dtype([
    ('timestamp', 'datetime64[s]'),
    ('body1', 'U10'),
    ('body2', 'U10'),
    # ... 13 more fields
])
```

## Registry Extension Pattern

**Pattern:** Extensible registries use a `frozen dataclass` + `register()` + `get_item()` pattern:
- `ketu.houses.registry.register()` registers custom house systems (analogous to `SwissEph` hsys codes)
- `ketu.parts.registry.register()` registers custom Arabic Parts
- Registration is ONE-WAY: once registered, a system/part cannot be unregistered (no collision risk)

**Example** (`ketu/parts/registry.py`):
```python
@dataclass(frozen=True)
class PartSpec:
    name: str
    day_formula: PartFormula
    night_formula: PartFormula
    description: str = ""

PARTS: dict[str, PartSpec] = {}

def register(
    name: str,
    *,
    day_formula: PartFormula,
    night_formula: PartFormula,
    description: str = "",
) -> None:
    """Register a new Arabic Part in PARTS."""
    PARTS[name.lower()] = PartSpec(name.lower(), day_formula, night_formula, description)

def get_part(name: str) -> PartSpec:
    """Look up an Arabic Part by name (case-insensitive)."""
    return PARTS[name.lower()]
```

## UTC-Only Datetime Convention

**Rule:** All datetime computations use UTC (Coordinated Universal Time):
- Parameters documented as "Datetime (timezone-aware or naive assumed UTC)" in docstrings
- No timezone-aware arithmetic in library code; users convert to UTC before calling
- Example (`ketu/ephemeris/time.py` line 34–39): explicit UTC handling in `utc_to_julian`:
  ```python
  if dtime.tzinfo is not None:
      utc = dtime.astimezone(timezone.utc)
  else:
      utc = dtime
  ```
- Convention: store all computed times as float Julian Dates (JD) or `datetime.datetime` in UTC

## NumPy-Vectorized Style

**Hot Path Optimization:**
- No Python loops over timestamps in vectorized paths; use NumPy broadcasting
- Loops over bodies (small constant count, e.g., 13 bodies) are acceptable (see `_vectorised_body_properties` comment about "Pitfall 1")
- Example pattern (`ketu/charts/api.py` lines 96–100):
  ```python
  for body_id in range(_BODY_COUNT):  # _BODY_COUNT = 13 (constant)
      batch = calc_planet_position_batch(jd_flat, body_id)
      lons[:, body_id] = batch[:, 0]
  ```

**Batch Function Suffixes:**
- `*_batch(jd_array, ...)` — operates on 1-D array of timestamps, returns shape `(N, ...)` results
- `*_vectorized(...)` — broadcast-compatible shape on inputs (0-d, 1-d, 2-d, etc.), returns compatible output shape
- Example: `calc_planet_position_batch(jd_array, body_id)` in `ketu/ephemeris/planets.py` vs `calculate_aspects_vectorized(...)` in `ketu/aspects/calculator.py`

## Language Mix: French/English

**Documentation and persona:** French with tutoiement (informal you) in user-facing instructions (CLAUDE.md, persona-sophie.md)
**Code and docstrings:** English with occasional French comments for historical context (e.g., references to Abu Ma'shar, Al-Biruni)
**Test fixtures:** Named after historical figures (Diana, Charles, Marie Curie) — no translation

---

*Convention analysis: 2026-05-29*
