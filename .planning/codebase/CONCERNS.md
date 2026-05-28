# Codebase Concerns

**Analysis Date:** 2026-05-29

## Coverage Analysis

### Overall Status

**Interrogate (docstring coverage):** 100% ✓ (blocking gate at 95%)

**Test Coverage:** 98.35% overall — VERIFIED 2026-05-29 via `pytest tests/ --cov=ketu` (1284 passed, 2 skipped; 52 missing lines / 3149). Required gate 70%; no global per-module floor pre-v1.2, but v1.2 subpackages enforce ≥95% via dedicated `make <module>-coverage` targets.

> **NOTE (corrected 2026-05-29):** An earlier draft of this section cited figures from the stale root `coverage.json` (dated 2026-05-09, untracked, never committed). That file references deleted modules (`ketu/export/*`, `ketu/resonance.py` — removed in v1.0) and reports a misleading 64.18% global. It is a pre-v1.2 artifact and should be deleted (or git-ignored). The numbers below are from a fresh measured run, not that file.

**Key Gap:** `ketu/houses/_ecliptic.py` at 64% (10 lines uncovered: 43-47, 69-73) — the only sub-90% module in the project and the single meaningful coverage outlier.

### Complete Missing-Lines Inventory (measured 2026-05-29)

The full set of uncovered lines across the whole package — exactly 52 lines, all listed:

| File | Cov | Missing lines |
|------|-----|---------------|
| `ketu/houses/_ecliptic.py` | 64% | 43-47, 69-73 (RA↔λ conversions) |
| `ketu/cli/harmonics_spec.py` | 92% | 80-81, 93 |
| `ketu/cycles/calculator.py` | 96% | 26-29, 222 |
| `ketu/display.py` | 96% | 28 |
| `ketu/cli/houses_cmd.py` | 97% | 74 |
| `ketu/cli/synastry_cmd.py` | 98% | 70 |
| `ketu/ephemeris/time.py` | 98% | 88, 369 |
| `ketu/complex.py` | 99% | 421 |
| `ketu/ephemeris/orbital.py` | 99% | 227 |
| `ketu/ephemeris/planets.py` | 99% | 354, 362, 448 |

All v1.2 subpackages (`charts/`, `synastry/`, `composite/`, `returns/`, `parts/`) and all house systems except `_ecliptic.py` are at 100%. Reaching 100% project-wide is a bounded, ~52-line task concentrated in the files above.

### Coverage Gaps by Module

**Critical (Below 90%):**

- `ketu/houses/_ecliptic.py` — 64% coverage
  - Files: `ketu/houses/_ecliptic.py`
  - Uncovered lines: 43-47 (ra_to_lambda), 69-73 (lambda_to_ra)
  - Problem: Ecliptic-coordinate transformation math is untested. These internal helpers serve Placidus (ketu/houses/placidus.py:374) and Koch (ketu/houses/koch.py) house systems, but the conversion formulas themselves have no direct unit tests.
  - Risk: Silent correctness regressions in house cusp calculation if either conversion is refactored.
  - Impact: High — both functions are load-bearing for RA↔λ conversions; incorrect formulas propagate to all cusp calculations using them.
  - Fix approach: Add parametrized unit tests for RA↔λ round-trip identity and cross-check against Swiss Ephemeris oracle values (pyswisseph test-only).

**High (Below 95%):**

- `ketu/cli/harmonics_spec.py` — 92% coverage
  - Files: `ketu/cli/harmonics_spec.py`
  - Uncovered lines: 80-81, 93
  - Problem: Harmonics CLI spec parser has edge-case handling not covered (likely error paths or optional numeric parsing).
  - Impact: Medium — CLI infrastructure; internal to command parsing, not core calculations.
  - Fix approach: Add explicit error-case tests (e.g., invalid harmonic range, out-of-order tokens).

- `ketu/aspects/core.py` — 94% coverage
  - Files: `ketu/aspects/core.py`
  - Uncovered lines: 68-69, 185, 336, 380, 409, 428
  - Problem: Core aspect validation code has sparse coverage — likely error conditions (ValueError raises) when aspect names/angles are invalid.
  - Impact: Medium — error paths for invalid user input.
  - Fix approach: Add tests for invalid aspect names, bad aspect indices, non-existent angles.

- `ketu/calculations.py` — 94% coverage
  - Files: `ketu/calculations.py`
  - Uncovered lines: 170, 172, 174
  - Problem: `body_name()` function contains conditional branches (renaming logic for nodes/lilith compatibility) that are not exercised.
  - Impact: Low — legacy API shim; the actual naming is tested upstream.
  - Fix approach: Explicit test of body_name() return values for nodes/lilith.

### Medium-Coverage Modules (95-98%)

- `ketu/aspects/timelines.py` — 96%
- `ketu/aspects/windows.py` — 96%
- `ketu/cycles/calculator.py` — 96%
- `ketu/display.py` — 96%
- `ketu/ephemeris/time.py` — 98%
- `ketu/aspects/calculator.py` — 99%
- `ketu/cache/ephemeris_cache.py` — 99%
- `ketu/ephemeris/planets.py` — 99%
- `ketu/ephemeris/orbital.py` — 99%

**Action:** These are all ≥95% and locked by phase gates. No action required for v1.3.

---

## Docstring & numpydoc Quality Gaps

### Status

- **Interrogate gate:** 100% across all 55 modules (blocking at 95%)
- **numpydoc gate:** Passes cleanly (no violations reported)

### Known Docstring Debt

While docstrings meet the *interrogate* quantitative threshold (≥95%), **depth and completeness** vary:

**Thin/Formulaic Docstrings (100% interrogate-compliant but minimal examples/notes):**

- `ketu/core.py` — Data-structure module with enum-like bodies/aspects/signs. Docstrings are correct but examples are repetitive copy-paste.
- `ketu/calculations.py` — Wrapper functions around ephemeris layer have cookie-cutter docstrings. `body_properties()` is a thin LRU cache wrapper over an uncached version; the docstring doesn't explain the cache strategy.
- `ketu/display.py` — `print_positions()` and `print_aspects()` have minimal docstrings (37 lines total). The stdout format is described but the relationship to CLI (ketu/cli/aspects_cmd.py) is not.
- `ketu/ephemeris/time.py` — Time conversion docstrings are correct but lack guidance on which function to use when (e.g., when to call utc_to_julian vs terrestrial_to_universal).

**Not Docstring Debt, but Example Accuracy:**

- Some examples in `ketu/calculations.py` (e.g., `body_sign()`) are pedagogical but hard-coded with 2025 values that will drift. No mechanism to regenerate or pin them against a test fixture.

### Numpydoc Validation Overrides

The `pyproject.toml` contains two safety overrides:

```toml
override_SS05 = [
    '^Aspect$',
    '^ZodiacPoint$',
    '^CycleRatio$',
]
```

These suppress "Summary section should start with capital" errors for three dataclass/NamedTuple types. **Action:** None — these are intentional exemptions for short type definitions.

---

## Test Coverage Gaps (by Area)

### Untested Code Paths

**Priority 1 (Core Calculations):**

- `ketu/houses/_ecliptic.py` RA↔λ round-trip tests (see Coverage section above).
- `ketu/aspects/core.py` error paths (invalid aspect specs).
- `ketu/ephemeris/coordinates.py` — Overall 37.1% coverage per coverage.json! This is a discrepancy with the pytest report (which shows 100%). **Action:** Run `pytest tests/test_coordinates_coverage.py -v` to verify; if there's real uncovered code, add explicit tests.

### Low-Priority Gaps (Error Paths, Edge Cases)

- `ketu/cli/harmonics_spec.py` — Numeric parser edge cases.
- `ketu/display.py` line 28 — Likely an error condition path in print_aspects.
- `ketu/aspects/windows.py` lines 343, 350, 449, 458, 466 — Edge-case handling in window refinement.

---

## Known Bugs & Warnings

### Runtime Warnings

**1. orbital.py line 755 — Division by zero in heliocentric latitude calculation:**

```
/home/loc/workspace/ketu/ketu/ephemeris/orbital.py:755: RuntimeWarning: invalid value encountered in divide
    lat = np.rad2deg(np.arcsin(z / r))
```

- **Problem:** When computing heliocentric latitude from Cartesian coordinates (x, y, z), the radial distance `r = sqrt(x² + y² + z²)` can equal zero in edge cases (e.g., a body momentarily at the solar system barycenter, which never happens in practice but Meeus theory allows mathematically).
- **Impact:** Produces NaN latitude values in rare circumstances. Downstream code handles NaN gracefully (no crashes observed in 1284 test passes).
- **Carry-forward:** This was noted in commit 541b59c (`docs: capture todo - Fix RuntimeWarning divide-by-zero in orbital heliocentric latitude`) and is a known carry-forward item for future cleanup.
- **Fix approach (v1.3):** Add guard: `r = np.maximum(r, 1e-10)` before division to ensure `r > 0` always, or use `np.where(r > 0, ..., 0)` to set lat=0 when r≈0.

### Type Suppressions

**12 `# type: ignore` suppressions across codebase:**

- `ketu/calculations.py:92` — `return np.where()` return type union narrowing
- `ketu/ephemeris/planets.py:568-569` — Index assignment on ndarray (mypy strict flag too strict)
- `ketu/aspects/*.py` (6 instances) — `distance()` function overloading (scalar vs array) not fully captured by type hints

**Assessment:** All suppressions are justified; the underlying code is sound, but type hints would benefit from overload stubs. No functional bugs.

---

## Refactoring Targets

### 1. Duplicate Natal Chart Fixture Pattern

**Problem:** Across tests, the same "natal chart fixture setup" is duplicated in multiple test files:

- `tests/synastry/conftest.py` — `natal_chart` fixture
- `tests/composite/conftest.py` — Similar fixture (noted in memory as "duplicated from composite/synastry")
- `tests/returns/conftest.py` — Another copy
- `tests/charts/conftest.py` — Yet another

**Files involved:**
- `tests/synastry/conftest.py`
- `tests/composite/conftest.py`
- `tests/returns/conftest.py`
- `tests/charts/conftest.py`

**Impact:** Test maintenance burden; any change to the canonical natal chart (JD, lat, lon, birth data) must be coordinated across 4 files.

**Fix approach (v1.3):** Create `tests/conftest.py` (root-level) with a shared `natal_chart` fixture and reuse across subpackages. See Phase 17 MEMORY note: "fixture duplication carried forward."

### 2. Long Functions in Ephemeris Layer

**Candidates for extraction:**

- `ketu/ephemeris/orbital.py:get_body_position()` — 856 LOC
  - Sub-functions: `get_moon_position()`, `get_lunar_nodes()`, `get_lilith_position()` are monolithic.
  - Candidate extraction: Split Lilith (50 lines of sinusoidal fitting logic) into a separate `_lilith_module.py`.
  
- `ketu/aspects/calculator.py:calculate_aspects_vectorized()` — 167 LOC
  - Sub-functions: Nested loop for body-pair iteration + orb calculation.
  - Candidate extraction: Inner loop into a `_orb_check()` helper.

- `ketu/ephemeris/planets.py:calc_planet_position()` — 200+ LOC
  - Giant if-elif-else for body type branching (Sun, Moon, Rahu, Ketu, Lilith, planets).
  - Candidate refactor: Strategy pattern with per-body calculators (`_sun_position()`, `_moon_position()`, etc.).

**Assessment:** These are not *bugs*, but they are *fragile* — changing one body's logic requires careful manual patching of a large function. Refactoring is deferred to v1.3 cleanup phase.

### 3. Legacy display.py Module

**Status:** `ketu/display.py` is 26 LOC, simple formatter, 96% coverage (1 line uncovered).

**Problem:** This module predates the argparse CLI. It's still used for documentation examples and CLI output, but the interactive prompt it originally served was removed in Phase 11.

**Files:** `ketu/display.py`

**Impact:** Low — it's small and stable. But it sits at the boundary between library (ketu.calculations) and CLI (ketu.cli.aspects_cmd), creating a thin layer that duplicates formatting logic.

**Fix approach:** No action required for v1.3. If CLI refactoring occurs, consider consolidating into `ketu/cli/formatters.py`.

---

## Chiron (v1.3 Readiness)

### Current Ephemeris Architecture

**Body registration:**
- All 13 bodies (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu, Ketu, Lilith) are hard-coded in:
  - `ketu/core.py` — `bodies` structured array (67 lines)
  - `ketu/ephemeris/planets.py` — `BODY_INDICES` dict (35-49) + `SWE_IDS` dict (52-66)
  - `ketu/ephemeris/orbital.py` — `ORBITAL_ELEMENTS` array (67-250+)

**How a new body is added (Chiron):**

1. **core.py:** Add Chiron row to `bodies` structured array with id=13, orb, speed.
2. **orbital.py:** Add Chiron row to `ORBITAL_ELEMENTS` with J2000.0 orbital elements (N, i, w, a, e, M, and their rates).
3. **planets.py:** 
   - Add `"Chiron": 13` to `BODY_INDICES` and `13: "Chiron"` to `SWE_IDS`
   - Add Chiron branch to `calc_planet_position()` if-elif chain (around line 163)
   - Add Chiron to `get_planet_name()` dict (lines 214-229)
   - Add Chiron to `calculate_all_positions()` loop (line 248)

**Chiron-Specific Challenges:**

**1. Embedded Chebyshev Coefficients (v1.3 requirement):**

Current implementation uses Meeus *Astronomical Algorithms* truncated polynomials (e.g., Moon as sinusoid series, planets as Kepler + perturbations). Chiron's orbit is highly eccentric (e≈0.382) and chaotic-adjacent, making analytic Kepler insufficient.

**Action Required:**
- Pre-compute Chebyshev polynomial fits to JPL Horizons or Swiss Ephemeris Chiron positions over 1900-2100 (similar to Lilith fitting in Phase 8).
- Store coefficients as numpy array in `orbital.py` (or separate `_chiron_coeffs.py`).
- Implement `_chiron_position()` function that evaluates the polynomial at JD.
- Integrate into `calc_planet_position()` as a new branch (between Lilith and loop-end, ~line 162).

**Orbital elements source:** Use JPL Horizons mean elements or Swiss Ephemeris internal coefficients (pyswisseph test oracle only).

**2. Axis Size Freeze (Decision D-08):**

The charts module hard-codes 13 bodies per D-08 (Kala compatibility):

```python
# ketu/charts/api.py line 54
_BODY_COUNT: int = len(_CANONICAL_BODIES)
```

And test `test_body_count_frozen_at_thirteen()` enforces this:

```python
# tests/charts/test_compute_chart.py (implied)
assert len(bodies) == 13, "Axis freeze broken; update D-08 decision"
```

**When adding Chiron:**
1. Update D-08 decision in ROADMAP (or create D-XX for Chiron freeze).
2. Grow the axis from 13 to 14.
3. Run full test suite; the ratchet test will force a human review.
4. Coordinate with Kala team (if still active) on positional contract.

**3. Speed (°/day) Estimate for Chiron:**

Chiron orbital period ≈50.7 years, so mean motion ≈360° / (50.7 × 365.25) ≈ 0.0195°/day.

Store in `bodies` structured array (same pattern as Lilith: mean rate = 0.111°/day).

### Ephemeris Accuracy Boundaries (for documentation)

Current known divergences from Swiss Ephemeris:

| Body | Method | Max Error | Notes |
|------|--------|-----------|-------|
| Sun (geocentric) | Meeus truncated polynomials + aberration | ~56 arcsec | Custom implementation; TRUE Sun, not mean. |
| Moon | Meeus sinusoid series | ~0.61° | Truncated lunar theory; full theory ∈ pyswisseph. |
| Mercury-Pluto | Kepler + perturbations | ±0.1-0.5° | High-precision rates from JPL J2000.0. |
| Rahu/Ketu | Lunar nodes (regressing) | <0.01° | Analytic, no perturbations. |
| Lilith (mean apogee) | Fitted sinusoid (Phase 8) | ±0.008° | Verified against swe.MEAN_APOG. |
| Chiron (TBD v1.3) | TBD: Chebyshev? | TBD | To be determined post-Phase 21 research. |

**Recommendation for Chiron:** Use Chebyshev polynomial fit (like Lilith Phase 8) over Swiss Ephemeris Moshier positions, with cross-check residuals <0.01°.

---

## Security Considerations

### No Known Security Issues

- No external API keys or credentials embedded in source code.
- No unsafe deserialization (pickle, eval, exec).
- No SQL/command injection vectors (pure NumPy calculations).
- Type hints + mypy --strict over ~95% of codebase catch type confusion bugs.

**Recommendation:** Continue enforcing mypy --strict gate on all new code.

---

## Performance Concerns

### Known Bottlenecks

**1. Python Loop in compute_chart() (v1.2 design trade-off):**

- Location: `ketu/charts/api.py:175-180` (_build_aspect_matrix)
- Problem: Loop over leading shape S (chart batch dimension) in Python; each iteration calls `calculate_aspects_vectorized()`.
- Trade-off: Acceptable for S ∈ {1, 100} (typical use case); would degrade for S > 10k.
- Fix approach (v1.3): Benchmark S=10k; if profiling shows >30% of chart compute is Python overhead, consider vectorising the loop over S using numpy.einsum or einsum-like broadcast trick (D-16, discussed in charts/api.py:153-157).

**2. LRU Cache Size (body_properties in calculations.py):**

- Location: `ketu/calculations.py:98` — `@lru_cache(maxsize=1024)`
- Problem: With ~400-600 unique JDs per typical use (transits, aspects batch), cache hit rate is high. But cache never evicts; older entries remain in memory.
- Impact: Low for typical use (memory ~50-100 MB per 1000 cached entries). Acceptable for v1.2.
- Fix approach: Monitor in v1.3; consider switching to `functools.cache` (unbounded, Python 3.9+) or explicit cache size limit based on profiling.

**3. No Query Optimization in cycles module:**

- Location: `ketu/cycles/calculator.py`
- Problem: Cycle calculations loop over all timestamps; no early-exit or caching strategy for repeated calculations.
- Impact: Medium — acceptable for typical use (dozens of years of daily/hourly data); would degrade for continuous minute-by-minute calculations.
- Fix approach (v1.3): Profile against real-world data (e.g., 50 years daily = ~18k points); consider caching intermediate results across batches.

---

## Technical Debt Summary (Priority Order for v1.3)

| Debt Item | Severity | Effort | v1.3 Target |
|-----------|----------|--------|-------------|
| **_ecliptic.py low coverage (64%)** | High | Medium | YES — add RA↔λ unit tests |
| **Chiron ephemeris + Chebyshev setup** | High | High | YES (depends on Phase 21 research) |
| **Duplicate natal fixtures** | Medium | Low | YES — consolidate to tests/conftest.py |
| **Division-by-zero warning (orbital.py:755)** | Medium | Low | YES — add guard clause |
| **aspects/core.py error paths** | Medium | Low | YES — add invalid-spec tests |
| **Long ephemeris functions (orbital.py, planets.py)** | Low | Medium | NO — defer to cleanup phase after Chiron |
| **Display.py consolidation** | Low | Low | NO — defer to CLI refactor |
| **compute_chart() Python loop vectorisation** | Low | High | NO — benchmark first, v1.4 if needed |

---

## Carry-Forward Items from v1.2

**From commit history and memory:**

1. **TODO(v1.3) in charts/api.py:171** — Hoist `resolve_aspect_set(aspects)` above loop if profiling shows cost. (Low priority; currently runs at ~µs.)

2. **venv shebangs hardcoded to solaris/ketu path** — Not observed in current codebase; verify if this is legacy.

3. **Numpydoc gate recently became blocking** — Flipped in Phase 20 (commit ae80c17). All current code passes; monitor for new violations.

4. **Python 3.10 minimum** — `pyproject.toml:10` pins to `requires-python = ">=3.10"`. ClassVar, TypeAlias, and match statements are available; leverage for v1.3 refactors if beneficial.

---

## Recommendations for v1.3 Planning

### Must-Do (Blocking for release):

1. **Chiron ephemeris implementation** — Research + Chebyshev fit + integration (Phase 21 scope).
2. **_ecliptic.py coverage to 100%** — Add RA↔λ round-trip tests.
3. **Division-by-zero fix** — Guard clause in orbital.py:755.

### Should-Do (Quality gates):

4. **Consolidate natal fixtures** — Reduce test maintenance debt.
5. **aspects/core.py error paths** — Ensure error handling is tested.
6. **Docstring depth review** — examples.py may benefit from dynamic generation vs hard-coded values.

### Nice-to-Have (Refactoring):

7. **Long-function extraction** — Defer unless other changes necessitate it.
8. **compute_chart() vectorisation** — Profile first; likely not needed for typical use case (S < 10k).

---

*Technical concerns audit: 2026-05-29*
