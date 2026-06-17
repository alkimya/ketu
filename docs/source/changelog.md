# Changelog

All notable changes to Ketu are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-06-15

### Changed 1.7.0

- **Rahu / Ketu / Lilith longitude orb: 0° → 2°** (`core.bodies`, single-source).
  All consumers (`get_orb`, `calculate_aspects*`, synastry, composite, CLI) inherit
  the change with zero further edits. Point-to-point conjunction threshold is now 2°;
  point-to-planet mean: e.g. Rahu-Sun yields (2+12)/2 = 7°. Chiron (orb = 4°) and
  all other planet rows are unchanged. (Phase 38 — ORB-01)
- **Tautological Rahu-Ketu Opposition suppressed** (`aspects/calculator.py`
  `_is_tautological_node_opposition`): the engine now silently drops the North-Node /
  South-Node Opposition (which is always present by definition and carries no
  astrological information). Every other Rahu/Ketu aspect is detected normally.
  (Phase 38 — ORB-02)

### Notes 1.7.0

- **BREAKING RESULTS — MINOR release, not a patch**: aspect detection results change
  for all consumers. Node/Lilith aspects that were previously invisible (orb 0 → inside
  2°) now appear. This is a deliberate, reviewed behaviour change shipped as a MINOR
  version per Semantic Versioning. Downstream code (any oracle/snapshot that
  enumerates node or Lilith aspects) **must treat the upgrade as deliberate** — do not
  `pip install -U` as a neutral patch.
- **`CHART_DTYPE` and `core.aspects` are byte-identical**: no dtype ratchet break.
  Only detection results change. (Phase 38)

## [1.6.0] - 2026-06-04

### Added 1.6.0

- **`ketu.declination` subpackage — declination aspects (parallels &
  contra-parallels)**: a NEW additive subpackage detecting parallel (`P`)
  and contra-parallel (`CP`) aspects on the equatorial declination axis (δ),
  independent of ecliptic longitude. (Phase 36)
- **`find_declination_aspects(body_decl)`**: scalar/single-chart detector.
  Takes the `(14,)` signed-δ `chart["body_decl"]` array; returns a
  `DECLA_ASPECT_DTYPE` structured array (upper-triangle pairs, sorted,
  deduplicated); `np.empty(0, …)` when none detected (never `None`).
- **`declination_aspect_masks(body_decl)`**: vectorized batch path. Accepts
  `(S, 14)` or `(14,)` (promoted via `np.atleast_2d`); returns a
  `DeclinationAspectMasks` NamedTuple of `(S, 91)` masks + `(91,)`
  index/orb vectors. Pure broadcasting, no Python body loop.
- **`DeclinationAspectMasks` NamedTuple** (6 fields: `parallel`, `contra`,
  `gap`, `idx_i`, `idx_j`, `orb_pairs`).
- **`DECLA_ASPECT_DTYPE`** (5 fields: `body1`, `body2`, `kind` ∈ {"P","CP"},
  `gap`, `orb`).
- **`DECLA_COEF = 1/12` and `MIN_DECL_ORB = 0.5°`**: the body-derived orb
  formula `max((orb_b1 + orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` → Sun/Moon
  = 1.0°, zero-orb bodies (Rahu/Ketu/Lilith) floored to 0.5°.

### Notes 1.6.0

- **`CHART_DTYPE` unchanged — additive subpackage**: `ketu.declination` is a
  purely additive companion to the v1.5 declination δ infrastructure. The
  `body_decl` field (shape `(14,)`) shipped in v1.5 is the sole input;
  `CHART_DTYPE` is byte-identical to v1.5 (no ratchet break). The new names
  are reachable via `ketu.declination.*` only — `ketu.__all__` is unchanged.
- **Parallel ≠ longitude conjunction**: declination aspects are independent
  of ecliptic-longitude aspects. The frozen 14-row `core.aspects` table is
  byte-identical to v1.5.

## [1.5.0] - 2026-06-04

### Added 1.5.0

- **`declination(jdate, body)` — equatorial declination δ**: returns δ in degrees [−90, +90] (north positive, south negative). Scalar and vectorized (array `jdate` via `calc_planet_position_batch`, loop-free). Computed via the ecliptic-to-equatorial chain (`spherical_to_rectangular → ecliptic_to_equatorial → rectangular_to_spherical`), numerically equivalent to Meeus eq. 13.4 to machine precision.
- **`declination_velocity(jdate, body)`**: dδ/dt in degrees/day (positive = northward). Forward finite difference, step 0.01 day — mirrors the `lat_velocity` FD idiom.
- **`is_ascending_declination(jdate, body)`**: `True` when dδ/dt > 0 (Moon montante). Biodynamic montant/descendant helper. **Distinct from `is_ascending`** (β-trajectory) — the two can disagree for the same body on the same date.
- **`is_out_of_bounds(jdate, body)`**: `True` when |δ| > ε(jd). OOB threshold uses the instantaneous true obliquity (not mean obliquity). The Moon can exceed ε during major lunar standstill (~18.6-year nodal cycle; peak ~2024–2025).
- **`CHART_DTYPE` — `body_decl` field (additive)**: new `float64[14]` field holding equatorial declination δ for all 14 bodies. `compute_chart` and `calculate_composite` both populate it via the coordinates chain. Body count remains 14; this is an additive dtype change.
- **`--harmonics h<N>` CLI surface for dynamic harmonics**: the `aspects` command accepts `--harmonics h7` (and any `h2`–`h64`) to detect dynamic harmonic aspects alongside the static set, via the `dynamic_specs=` engine path.

### Changed 1.5.0

- **`H{h}-{k}` dynamic-aspect naming promoted to a public API contract**: dynamic harmonic rows are named `H{h}-{k}` (harmonic `h`, multiple `k`), pinned by tests and documented as stable.
- **`find_aspect_timing` gains a `dyn_coef=` parameter**: the orb for a dynamic aspect is derived from `(orb[b1] + orb[b2]) / 2 × dyn_coef`, matching the detection path.

### Fixed 1.5.0

- **Lunar node mean speed corrected (−0.013 → −0.052954 °/day)**: `core.bodies['speed']` for Rahu and Ketu held a value ~4× too slow. The true nodal regression is 360° over ~18.6 years (≈ −0.052991 °/day); the engine already produced −0.052954 °/day for the nodes, so the table is now consistent with the computed motion. `calculate_speed_ratio` now sources its average speeds from `core.bodies['speed']` (single source of truth).
- **`calculate_aspects_batch` duplicate-pair rows eliminated**: with overlapping orbs (e.g. the EXTENDED set) the batch path could emit more than one row for the same `(body1, body2)` pair on a single date. Both `calculate_aspects_vectorized` and `calculate_aspects_batch` now share a single detection core, enforcing "exactly one row per pair" (static-first / dynamic-second, first-match-wins) identically.

### Notes 1.5.0

- **`is_ascending` (β) unchanged**: the existing ecliptic-latitude-based `is_ascending` is byte-for-byte identical to v1.4. The new `is_ascending_declination` is an independent, parallel helper.
- **Downstream impact (additive, not breaking for named access)**: `CHART_DTYPE` gains `body_decl` as an additive field. Code using named field access (`chart["body_lons"]`) is unaffected. Code using positional access or `.view()` on the raw dtype must adapt. The node-speed fix changes `core.bodies['speed'][10]` / `[11]`.

## [1.4.0] - 2026-06-03

### Added 1.4.0

- **`generate_harmonic_aspects(h)` — dynamic harmonic generator**: builds aspect specs on the fly for ANY integer harmonic `h` (2 ≤ h ≤ 64), using the full-circle 360° convention folded to 0–180° (`coef = k/h`). Returns a structured array that is a drop-in for `core.aspects`; pass it as the `dynamic_specs=` argument to `calculate_aspects`, `find_aspects_between_dates`, and `calculate_synastry`. The frozen 14-row `core.aspects` table and preset fingerprints are byte-identical (parallel code path).
- **Chiron range expanded to 1900–2100**: `ketu/data/chiron_coeffs.npz` regenerated (2283 Chebyshev segments, `jd_start=2415020.5`, `jd_end=2488069.5`), max error 0.001214° over the new range. Pure-NumPy runtime preserved.

### Changed 1.4.0

- **Chiron orb 0° → 4°** (Pluto parity): `core.bodies['orb']` for Chiron is now 4°, so Chiron now forms scored aspects.
- **Chiron out-of-range behaviour**: input outside 1900–2100 is now **silently clamped** to the nearest segment boundary (previously raised `ValueError`).
- **Documentation recentred on the 180°-division default**: `concepts.md` aspect tables now show CLASSICAL (5) and TRADITIONAL (7) only; the full-circle minor harmonics (H5/H9/H10 / EXTENDED) remain available in code but are out of the summary tables.

## [1.3.0] - 2026-06-01

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

- **`ketu.aspects` — Configurable aspect sets**: `CLASSICAL` (5 aspects), `TRADITIONAL` (7), `EXTENDED` (14 — default at v1.1, changed to `TRADITIONAL` in v1.3). `AspectSetSpec = Union[str, list, ndarray, None]`, `resolve_aspect_set`. `calculate_aspects(jdate, l_bodies, aspects=None)` now accepts an aspect-set spec.
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
