# Architecture

**Analysis Date:** 2026-05-29

## Pattern Overview

**Overall:** Layered pure-NumPy library with registry-dispatched subpackages and structured-array (dtype) contracts for ML interop.

**Key Characteristics:**
- Pure NumPy (no scipy, no external runtime deps beyond numpy)
- Structured arrays (CHART_DTYPE, SYNASTRY_DTYPE, CYCLE_DTYPE, HOUSES_DTYPE) for ML-interop and batch operations
- Registry pattern (SYSTEMS for houses, PARTS for Arabic parts) allowing extensibility without dispatch changes
- Ephemeris layer (ketu/ephemeris/) providing canonical astronomical computations
- Vertical integration: ephemeris → positions → charts → {synastry, composite, returns, parts}
- Strict frozen body/aspect axes (D-08: 13 bodies max, 14 aspects max) per Kala positional contract

## Layers

**Ephemeris (Low-level Physics):**
- Purpose: Pure astronomical calculations (time conversions, orbital mechanics, coordinate transforms)
- Location: `ketu/ephemeris/time.py`, `ketu/ephemeris/orbital.py`, `ketu/ephemeris/coordinates.py`, `ketu/ephemeris/planets.py`
- Contains: Julian Date conversions, Kepler equation solver, heliocentric→geocentric transforms, ecliptic↔equatorial transforms
- Depends on: NumPy only
- Used by: Charts (compute_chart via calc_planet_position_batch), Cycles, direct calculation APIs

**Core Data (Constants):**
- Purpose: Shared astronomical/astrological constants (bodies, aspects, signs)
- Location: `ketu/core.py` (structured arrays: bodies, aspects), `ketu/calculations.py` (utility functions)
- Contains: 13-body axis (Sun=0 ... Lilith=12), 14-aspect angles (Conjunction=0° ... Opposition=180°), 12 zodiac signs
- Depends on: NumPy only
- Used by: All subpackages that read body IDs or aspect names

**Houses (Geometric Calculation):**
- Purpose: House system dispatch via registry; cusp computation for different coordinate frames
- Location: `ketu/houses/` (api.py, core.py, registry.py, placidus.py, koch.py, porphyry.py, whole_sign.py, equal.py, regiomontanus.py)
- Contains: Registry of 6 house systems; HOUSES_DTYPE structure; HighLatitudeError for polar handling
- Pattern: `@register` decorator on each system module populates SYSTEMS dict at import time
- Depends on: Ephemeris (time), Core data
- Used by: Charts (via calculate_houses), returns (relocated return charts)

**Aspects (Geometric Detection):**
- Purpose: Aspect finding (exact moments, windows, timelines), orb calculations, preset masks
- Location: `ketu/aspects/` (calculator.py, core.py, windows.py, timelines.py, transits.py, presets.py)
- Contains: calculate_aspects_vectorized (dense 13×13 matrix), aspect windows with bisection refinement, transit detection
- Depends on: Ephemeris (planets), Core data (aspect angles/orbs)
- Used by: Charts (via calculate_aspects_vectorized), Synastry, CLI

**Charts (Unified Natal Chart):**
- Purpose: Assemble a fully-resolved natal chart (positions, ASC/MC/cusps, intra-chart aspects) in one call
- Location: `ketu/charts/api.py`, `ketu/charts/core.py`
- Contains: compute_chart (vectorised over jd/lat/lon), is_day_chart (sect helper), CHART_DTYPE (14 fields: metadata + 13-body lons/lats/speeds + 12 cusps + ASC/MC/ARMC/Vertex + 13×13 aspect matrices)
- Pattern: _vectorised_body_properties (loops 13 bodies, each call to calc_planet_position_batch is natively vectorised); _build_aspect_matrix (loops leading shape S, each call to calculate_aspects_vectorized is natively vectorised)
- Depends on: Ephemeris, Houses, Aspects, Core data
- Used by: Synastry, Composite, Returns, Parts, CLI

**Synastry (Inter-Chart Aspects):**
- Purpose: Calculate aspects between two natal charts (15 bodies: 13 canonical + ASC + MC)
- Location: `ketu/synastry/api.py`, `ketu/synastry/core.py`, `ketu/synastry/orbs.py`
- Contains: calculate_synastry (takes two CHART_DTYPE, returns array of SYNASTRY_DTYPE rows), SYNASTRY_DTYPE (8 fields), orb presets/factor
- Pattern: Consumes chart pairs; applies synastry orb factor (0.5×) to natal orbs; supports mode="filtered" (only orbed) or mode="dense" (all 225 pairs with sentinels)
- Depends on: Charts, Aspects
- Used by: CLI (synastry_cmd)

**Composite (Midpoint Composite Chart):**
- Purpose: Derive a midpoint composite chart from two natal charts
- Location: `ketu/composite/api.py`, `ketu/composite/core.py`
- Contains: calculate_composite (circular midpoints of bodies, ASC, MC; Porphyry-style cusp derivation), circular_midpoint helper
- Pattern: Pure midpoint method only (NOT Davison); composite (jd, lat, lon) are bookkeeping, not astronomical moment-and-place
- Depends on: Charts, Houses (Porphyry for composite cusps)
- Used by: CLI, manual pair-chart workflows

**Returns (Solar & Lunar):**
- Purpose: Find the moment when Sun/Moon returns to natal longitude; compute return chart at resolved instant
- Location: `ketu/returns/solar.py`, `ketu/returns/lunar.py`, `ketu/returns/_solve.py`
- Contains: solar_return (target_year → resolved instant), lunar_return (target_jd → first lunar return ≥ target_jd), _solve_return (bisection root-finder shared by both)
- Pattern: Shared bisection core (_solve_return) on signed-short-arc residual; Sun is never retrograde so bisection always converges monotonically
- Depends on: Charts, Ephemeris (planets for residual calculation)
- Used by: CLI, return-chart workflows

**Parts (Arabic Parts / Hermetic Lots):**
- Purpose: Registry of sect-aware formulas for Arabic Parts
- Location: `ketu/parts/registry.py`, `ketu/parts/api.py`
- Contains: Registry of PartSpec (day_formula, night_formula), 3 built-in parts (Fortune, Spirit, Marriage)
- Pattern: Dispatch on is_day_chart(chart); formula signature is (asc_lon, sun_lon, moon_lon, venus_lon) → longitude
- Depends on: Charts (is_day_chart, get body longitudes)
- Used by: CLI (--list-parts, introspection)

**Cycles (Time-Series Cycle State):**
- Purpose: Calculate instantaneous cycle state (separation, progress, phase, velocity) at given timestamps
- Location: `ketu/cycles/calculator.py`
- Contains: generate_cycle_series (body1, body2, timestamps → CYCLE_DTYPE array), CYCLE_DTYPE (julian_day, body IDs, lons, separation, cycle_progress, phase, velocities, retrograde flags, aspect proximity)
- Pattern: Vectorised over timestamps; optional EphemerisCache integration for batch workflows
- Depends on: Ephemeris (calc_planet_position_batch), Core data (body lookup), Complex (cycle_ratio_vectorized)
- Used by: Time-series analysis, ML training data

**Cache (High-Performance Lookups):**
- Purpose: Two-layer caching strategy: LRU (single-point repeated queries) + EphemerisCache (batch monthly pre-computation)
- Location: `ketu/cache/__init__.py`, `ketu/cache/ephemeris_cache.py`
- Contains: EphemerisCache (monthly pre-computation with interpolation), BODY_COUNT, get_default_cache singleton
- Pattern: Layer 1 = @lru_cache on calc_planet_position (automatic, test-only); Layer 2 = EphemerisCache (explicit user call)
- Depends on: Ephemeris (planets)
- Used by: Optional acceleration in Cycles, batch workflows

**Complex Representation:**
- Purpose: Unit-circle complex representation for zodiac points and cycle ratios (ML-friendly)
- Location: `ketu/complex.py`
- Contains: ZodiacPoint, CycleRatio, Aspect dataclasses, circular_mean/std, phase_locking_value
- Pattern: e^(iθ) representation; no discontinuity at 0°/360°; (Re(z), Im(z)) are linear ML features
- Depends on: NumPy only
- Used by: Cycles (cycle_ratio_vectorized), optional ML preprocessing

**CLI (Command-Line Interface):**
- Purpose: Argparse-based command-line dispatch for aspects, houses, synastry, introspection
- Location: `ketu/cli/parser.py`, `ketu/cli/aspects_cmd.py`, `ketu/cli/houses_cmd.py`, `ketu/cli/synastry_cmd.py`, `ketu/cli/introspection.py`
- Contains: Top-level argparse tree; subcommand dispatchers; harmonics/orb spec parsers
- Pattern: `set_defaults(func=...)` per subparser; introspection flags (--list-*) short-circuit before subcommand dispatch
- Entry point: `ketu/__main__.py` → `ketu.cli:main()`
- Depends on: Charts, Synastry, Aspects, Houses, Parts

## Data Flow

**Natal Chart Computation:**
1. User calls `compute_chart(jd, lat, lon, system)`
2. _vectorised_body_properties: loops 13 bodies → calc_planet_position_batch (natively vectorised on jd)
3. Collect lon/lat/speed arrays (shape S + (13,))
4. calculate_houses: dispatch via SYSTEMS registry (e.g. "placidus") → cusps, ASC, MC, ARMC, Vertex
5. _build_aspect_matrix: loop over leading shape S → calculate_aspects_vectorized → 13×13 aspect matrix
6. Assemble CHART_DTYPE with metadata (jd, lat, lon, system) + positions + houses + aspects
7. Return structured array of CHART_DTYPE

**Synastry Computation:**
1. User calls `calculate_synastry(chart_a, chart_b, mode='filtered')`
2. Extract (lon_a, lon_b) from CHART_DTYPE for each of 15 bodies (13 canonical + ASC + MC)
3. Loop 15×15 body pairs; calculate_aspects_vectorized on (lon_a[i], lon_b[j])
4. Apply synastry orb factor (0.5× natal)
5. Filter (mode='filtered') or keep all (mode='dense')
6. Return array of SYNASTRY_DTYPE rows (body_a, body_b, lon_a, lon_b, aspect_type, orb, applying, orb_limit)

**Composite Computation:**
1. User calls `calculate_composite(chart_a, chart_b)`
2. Circular midpoint of bodies: circular_midpoint(lon_a[i], lon_b[i]) for i in 13
3. Circular midpoint of ASC, MC, ARMC, Vertex
4. Porphyry-style cusps from composite ASC + composite MC
5. Compute intra-chart aspects (same as step 5 of natal chart computation)
6. Return CHART_DTYPE for composite

**Solar Return Computation:**
1. User calls `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None)`
2. _solve_return: bisection on Sun-longitude residual ((sun_lon(t) - natal_sun_lon + 540) % 360) - 180
3. Bracket: (target_year Jan 1, target_year Dec 31); tolerance: 1 arcsecond
4. Once converged to jd_return, compute_chart(jd_return, return_lat or natal_lat, return_lon or natal_lon)
5. Return CHART_DTYPE for return

**Lunar Return Computation:**
1. User calls `lunar_return(natal_jd, natal_lat, natal_lon, target_jd)`
2. _solve_return: bisection on Moon-longitude residual ((moon_lon(t) - natal_moon_lon + 540) % 360) - 180
3. Bracket: (target_jd, target_jd + 27.32 days); tolerance: 1 arcsecond
4. Once converged, compute_chart(jd_return, natal_lat, natal_lon)
5. Return CHART_DTYPE for return

**State Management:**

CHART_DTYPE is the canonical state container:
- Immutable at the point of creation (frozen structured array)
- Self-describing (carries jd, lat, lon, system, all positions, all cusps, all aspects)
- Consumed downstream by Synastry, Composite, Returns, Parts (all read-only)
- No mutable registries on instances; all registries (SYSTEMS, PARTS) are module-level

## Key Abstractions

**CHART_DTYPE (Canonical Chart Structure):**
- Purpose: Unified natal chart record — positions, houses, aspects, metadata
- Location: `ketu/charts/core.py`
- Pattern: 14 fields (jd, lat, lon, system + body_lons/lats/speeds (13,) + cusps (12,) + ASC/MC/ARMC/Vertex + aspect_matrix (13,13) + aspect_orbs (13,13))
- Contract: 13-body axis is FROZEN (D-08 Kala positional contract); adding Chiron is v1.3 BREAKING change
- ML interop: Kala indexes chart["body_lons"][i] positionally per canonical body axis order

**SYNASTRY_DTYPE (Inter-Chart Aspect Record):**
- Purpose: One inter-chart aspect between two charts
- Location: `ketu/synastry/core.py`
- Pattern: 8 fields (body_a, body_b, lon_a, lon_b, aspect_type, orb, applying, orb_limit)
- Contract: 15-body axis (13 canonical + ASC + MC) is FROZEN; Vertex is v1.3 candidate

**HOUSES_DTYPE (House Cusp Record):**
- Purpose: Cusp results for one calculation (jd, lat, lon, system)
- Location: `ketu/houses/core.py`
- Pattern: 9 fields (jd, lat, lon, system + cusps (12,) + asc/mc/armc/vertex)
- Inlined in CHART_DTYPE; not nested (D-03 decision)

**CYCLE_DTYPE (Instantaneous Cycle State):**
- Purpose: Time-series snapshot of planetary cycle at a given moment
- Location: `ketu/cycles/calculator.py`
- Pattern: 16 fields (julian_day, body IDs, lons, separation, cycle_progress, phase, velocities, retrograde flags, aspect proximity)
- ML interop: Natural feature vector for correlation analysis with price data

**SYSTEMS Registry (House Dispatch):**
- Purpose: Pluggable house-system implementations
- Location: `ketu/houses/registry.py` (registry dict) + individual system modules
- Pattern: `@register` decorator on each system (placidus.py, koch.py, porphyry.py, whole_sign.py, equal.py, regiomontanus.py); at import time, each decorator populates SYSTEMS dict
- Extensibility: v1.3 Lot is one `register(...)` call without touching dispatch logic
- Location of implementations: `ketu/houses/{placidus,koch,porphyry,whole_sign,equal,regiomontanus}.py`

**PARTS Registry (Arabic Part Dispatch):**
- Purpose: Pluggable sect-aware Hermetic Lot implementations
- Location: `ketu/parts/registry.py` (registry dict) + trigger-import in `ketu/parts/__init__.py`
- Pattern: PartSpec(name, day_formula, night_formula, description); register(name, day_formula=..., night_formula=...)
- Built-in parts: Fortune, Spirit, Marriage (registered at `ketu/parts/__init__.py` import time)
- Extensibility: v1.3 Lot is one register(...) call without touching dispatch logic

**AspectSetSpec (Aspect Preset Resolver):**
- Purpose: Flexible aspect set specification (named preset, list, or boolean mask)
- Location: `ketu/aspects/presets.py`
- Pattern: resolve_aspect_set(spec) → length-14 boolean mask; CLASSICAL/TRADITIONAL/EXTENDED presets
- Used by: calculate_aspects_vectorized (phase 14 D-07 default = CLASSICAL), CLI (--harmonics)

## Entry Points

**CLI Entry Point:**
- Location: `ketu/__main__.py`, `ketu/cli/parser.py`
- Triggers: `python -m ketu` or `ketu` (console script)
- Responsibilities: Argparse tree dispatch to `cmd_aspects`, `cmd_houses`, `cmd_synastry`, `cmd_list_*` introspection
- Pattern: Subcommands via `set_defaults(func=...)` + introspection flags short-circuit before subcommand dispatch

**Python API Entry Points:**
- `ketu.charts.compute_chart` — Natal chart
- `ketu.synastry.calculate_synastry` — Inter-chart aspects
- `ketu.composite.calculate_composite` — Midpoint composite
- `ketu.returns.solar_return`, `ketu.returns.lunar_return` — Returns
- `ketu.parts.calculate_part`, `ketu.parts.calculate_all_parts` — Arabic Parts
- `ketu.cycles.generate_cycle_series` — Cycle time series
- `ketu.aspects.calculate_aspects`, `ketu.aspects.find_aspect_window` — Aspect detection

## Error Handling

**Strategy:** Validation at boundaries; fail fast with specific error types.

**Patterns:**

- `HighLatitudeError` (subclass ValueError): Raised when |lat| exceeds polar circle for house system; caller can pass `polar_fallback='porphyry'` to recover
- `ValueError`: Raised for unknown body names, unknown house systems, unknown aspect sets, unknown parts
- No silent defaults: Typos in system/aspect/part names are caught immediately
- Ephemeris precision guarantees documented in docstrings; no error on precision loss (acceptable ±0.1° for outer planets, ±1e-6° for aspects)

## Cross-Cutting Concerns

**Logging:** No explicit logging module; diagnostics via standard library (print for CLI, optional caller logger integration)

**Validation:** Per-module input validation at API boundaries; NumPy broadcasting alignment checked implicitly via operations

**Authentication:** Not applicable (pure astronomical library, no external service calls)

**Timezone Handling:** LOUD contract: all timestamps MUST be UTC Julian Dates; caller is responsible for local→UTC conversion via `ketu.calculations.local_to_utc`

**Coordinate Frames:** All longitudes in ecliptic coordinates, degrees [0, 360); latitudes in ecliptic degrees; always geocentric except where noted

**Numerical Precision:** ±1e-6° (0.0036 arcseconds) for aspect separation; ±0.1° for inner planets, ±0.5° for outer planets; ±0.01° for Moon. Julian Date conversion ±1 second. Best accuracy 1800-2200 CE.

---

*Architecture analysis: 2026-05-29*
