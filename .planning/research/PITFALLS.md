# Pitfalls Research: Ketu v1.1 — Configurable Aspects, Houses, Lilith Fix

**Domain:** Python scientific library (astronomy/astrology), v1.0.0 published on PyPI, downstream consumers (Kala, Surya)
**Researched:** 2026-05-06
**Confidence:** HIGH (codebase inspection + Swiss Ephemeris docs + community sources verified across 2+ sources)

---

## Critical Pitfalls

### Pitfall 1: Silent Breaking Change in NumPy Structured Array Shape

**What goes wrong:**
Kala's `KetuAdapter` consumes `aspects` as a 14-element `np.ndarray` (verified in `ketu/core.py:84` — 14 rows). If v1.1 changes the *shape* of `aspects` (e.g., adds harmonic 12 → 21 rows), Kala's ML feature pipeline silently produces wrong features (different column count, NaN-padded rows, or index-shifted lookups). NumPy doesn't raise — it just gives wrong numbers.

**Why it happens:**
Configurable aspect sets feel "additive." Developer adds 7 new aspects to the `aspects` array thinking "more options is fine." But `aspects` is a *public global* that downstream code indexes by position (`aspects[7]` = Square in v1.0). Any reordering or expansion shifts those indexes.

**How to avoid:**
1. Treat the `aspects` constant as a **frozen, append-only** structured array. Document the order as part of the public contract.
2. New aspects must be appended at the end, never inserted in the middle.
3. Add a runtime invariant test: `assert aspects['name'][7] == b'Square'` — this fails loudly if anyone reorders.
4. Provide aspect sets as *named filters*, not by mutating the global: `get_aspect_set("traditional")` returns a view/copy with stable indexing.
5. Coordinate with Kala maintainer: if 14-element shape is essential, expose `LEGACY_14_ASPECTS` constant explicitly.

**Warning signs:**

- PR diff modifies the order of rows in `ketu/core.py:aspects`
- Test suite passes but Kala integration test fails
- `len(ketu.core.aspects) != 14` in v1.1 without a major version bump

**Phase to address:** Phase 1 (configurable aspects design) — *before any code is written*, decide: append-only or named-views? Documented in DESIGN.md.

---

### Pitfall 2: LRU Cache Keys Don't Include Aspect Set / House System

**What goes wrong:**
`ketu/aspects/core.py:73` uses `@lru_cache(maxsize=256)` on `_cached_planet_position_batch(jd_tuple, planet_id)`. Position cache is fine. But if v1.1 adds caches for *aspect calculations* or *house cusps* keyed only on `(jd, lat, lon)`, then changing the active aspect set or house system mid-session returns stale results computed against the *previous* configuration.

**Why it happens:**
Configuration feels orthogonal to inputs. Developer caches `compute_aspects(jd, body1, body2)` and forgets that "which aspects are valid" is part of the result.

**How to avoid:**
1. Every cache key must include a configuration fingerprint: `(jd_tuple, body1, body2, aspect_set_hash, orb_policy_hash)`.
2. Make config objects **frozen and hashable** (`@dataclass(frozen=True)`) so they can be cache keys directly.
3. Expose a `cache_clear_all()` helper and call it in tests that switch config.
4. Document that mutating the global aspect set requires `_cached_planet_position_batch.cache_clear()`.
5. For house systems, include the system char (`'P'`, `'K'`) in any cache key.

**Warning signs:**

- A test that sets `aspect_set = "traditional"`, calls API, then sets `aspect_set = "harmonic_12"` and gets traditional results.
- Cache stats (`.cache_info()`) show 100% hit rate after a config change (should be 0%).

**Phase to address:** Phase 1 (configurable aspects core) and Phase 2 (houses) — must be designed in from day one.

---

### Pitfall 3: Picking the Wrong Lilith and Validating Against the Wrong Authority

**What goes wrong:**
Three definitions exist: **Mean Lilith** (lunar apogee, smooth ~40°/yr precession, no retrograde — what Ketu currently implements per `ketu/core.py:77`), **True/Osculating Lilith** (instantaneous apogee, can retrograde, differs from Mean by up to 30°), and **Asteroid Lilith #1181** (a real minor planet, completely different orbit). Fixing "the Lilith bug" without specifying *which* Lilith leads to:

- Implementing True Lilith, then validating against Astro.com which defaults to Mean Lilith → tests pass for wrong reason.
- Implementing Mean correctly, but the bug was actually the sign of the apogee longitude (Lilith is the apogee + 180° in some conventions).

**How to avoid:**
1. **Decide first, code second.** Phase 3 starts with a written decision: "Ketu computes *Mean* Lilith = Mean Lunar Apogee, longitude in tropical zodiac, defined as [precise formula citing source]."
2. Pick **two** independent reference sources (Swiss Ephemeris `swe_calc(SE_MEAN_APOG)` AND Astro.com), confirm they agree, then test against both.
3. Capture **at least 5 reference dates** (current epoch, J2000, 1900-01-01, 2000-01-01, 2050-01-01) accurate to 0.01° — hardcode as test fixtures.
4. Document that True Lilith and Asteroid Lilith are out-of-scope.

**Warning signs:**

- The fix PR has no link to a primary source defining Lilith.
- Test fixtures use values from a single online calculator.
- The word "Lilith" appears in the PR without "Mean" or "True" or "#1181" qualifier.

**Phase to address:** Phase 3 (Lilith fix) — first task is "write LILITH_DEFINITION.md and pick reference sources" before touching code.

---

### Pitfall 4: Lilith Fix Is a Silent Breaking Change for Users Built on the Bug

**What goes wrong:**
If Ketu v1.0 produces "wrong" Lilith longitudes and a downstream user (Kala? Surya?) trained ML models or stored chart data using those wrong values, fixing the math invalidates their data.

**How to avoid:**
1. Bump **minor version** at minimum (already planned: v1.1).
2. Add a **prominent CHANGELOG section** "Numerical Behavior Changes": "Lilith longitudes will differ from v1.0 by up to X° at any given date."
3. Document the magnitude of change with concrete examples.
4. Optional: legacy mode `ketu.set_lilith_mode("v1.0_legacy")` if backward compat matters.
5. Notify Kala and Surya maintainers *before* release.

**Phase to address:** Phase 3 (Lilith fix) for legacy mode; Phase final (release) for CHANGELOG/UPGRADING.md.

---

### Pitfall 5: Placidus Undefined Above ~66° Latitude — Silent NaN Propagation

**What goes wrong:**
At polar latitudes (>~66.56°), parts of the ecliptic never cross the horizon, and Placidus's semi-arc trisection has no solution. Naïve implementations:

- Return NaN cusps → propagate through downstream calculations as silent NaNs.
- Hang in iterative loops that never converge.
- Return finite-but-meaningless values from a numerical solver.

Koch has the same fundamental issue (also based on diurnal arcs).

**How to avoid:**
1. Detect polar regime explicitly: `if abs(latitude) > 66.56: ...`
2. Provide a **documented fallback**: Swiss Ephemeris's `houses_with_fallback` pattern uses **Porphyry** (works at all latitudes) when Placidus/Koch fail.
3. Allow user to choose: `polar_fallback="porphyry" | "whole_sign" | "raise"`.
4. Add explicit polar-region tests: 70°N, 80°N, 89°N (and southern equivalents).
5. Validate convergence: cap iterations (e.g., 50) and detect non-convergence.

**Phase to address:** Phase 2 (houses) — must include polar-fallback design and tests in DoD.

---

### Pitfall 6: Sidereal Time Precision Cliff — Small SidT Error → Big Cusp Error

**What goes wrong:**
House cusps depend on **Local Sidereal Time** (LST). 1 second of LST error ≈ 1 second-of-arc on MC. But:

- **1 minute of LST error** ≈ 15 arcminutes on MC ≈ a planet jumps house if near a cusp.
- **GMST formula errors** (wrong precession model, JD-vs-JDE confusion, UT1-vs-UTC) accumulate to minutes.
- **True vs Apparent obliquity**: using mean obliquity for cusp calculation introduces ~9″ error on Asc/Desc.

Ketu's existing `ephemeris/time.py` was tuned for *body positions* (~0.01° suffices). Houses need ~0.001° (10× tighter).

**How to avoid:**
1. Audit `ephemeris/time.py` GMST/LST functions before Phase 2 starts. Verify against IAU 2006/2000A formulas.
2. Consistently use the same obliquity (true apparent) for both body positions AND house cusps.
3. Reference test: compute Ascendant at 2000-01-01 12:00 UT, lat 51.5° (London). Cross-check with Astro.com to ≤ 1 arcminute.
4. Property test: increment time by 4 minutes; MC should advance by exactly 1 degree (modulo obliquity).

**Phase to address:** Phase 2 (houses) — pre-implementation audit of LST/obliquity.

---

### Pitfall 7: Iterative Placidus — Vectorization Trap and Convergence Failures

**What goes wrong:**
Placidus uses successive approximation per intermediate cusp (cusps 11, 12, 2, 3 are root-finding problems). Two failure modes:

1. **NaN propagation**: one iteration produces NaN; subsequent iterations never recover.
2. **Anti-vectorization**: developer tries to vectorize per-element-iteration over arrays, creating either ragged convergence or slow Python loops disguised as NumPy.

**How to avoid:**
1. **Don't over-vectorize.** A loop over dates calling a scalar Placidus function is acceptable for charts. Houses are NOT a hot path like aspect timeseries.
2. If batch is needed, use boolean-mask continuation: compute new estimate only where `not_converged` mask is True.
3. Hard cap iterations at ~50. If unconverged: NaN + warning, OR fallback to Porphyry.
4. Defensive: `np.where(np.isnan(x), fallback_value, x)` on outputs.
5. Benchmark target: 1000 charts/second is fine for v1.1 — don't sacrifice clarity for premature speed.

**Phase to address:** Phase 2 (houses) — make scalar-loop the default, optimize only if benchmarks demand.

---

### Pitfall 8: Inconsistent Aspect Filtering Across Modules

**What goes wrong:**
v1.1 adds configurable aspect sets. The filter must be applied consistently across:

- `ketu/aspects/calculator.py`
- `ketu/aspects/windows.py`
- `ketu/aspects/transits.py`
- `ketu/aspects/timelines.py`
- `ketu/cycles/calculator.py`
- CLI in `ketu/display.py` and `ketu/__main__.py`

If one module reads the configured set and another reads the global `aspects`, you get **mismatched outputs**: CLI shows 7 aspects but JSON export contains 14.

**How to avoid:**
1. Single source of truth: a `KetuConfig` (or `AspectConfig`) frozen dataclass passed explicitly to every public function.
2. Add a "config-consistency" integration test: configure `traditional` (5 aspects), call every public API, assert no result contains a non-traditional aspect.
3. mypy can help: type the parameter `aspect_set: AspectSet` and grep for any function not accepting it.
4. CLI must thread the same config to every command.

**Phase to address:** Phase 1 (configurable aspects) — DoD must include "all public APIs accept and respect aspect_set, integration test passes."

---

### Pitfall 9: User Confusion — `--harmonics 12` Ambiguity

**What goes wrong:**
`--harmonics 12` is ambiguous:

- "Set named harmonic-12" → 7 aspects (multiples of 30°)
- "Only the 12th harmonic" → 1 aspect (the 30° semi-sextile)
- "Harmonics up to 12" → all aspects with denominators ≤ 12
- "Highest harmonic = 12" → 12 aspects total

**How to avoid:**
1. **Don't accept bare integers.** Force unambiguous syntax:
   - `--aspect-set traditional` (named preset)
   - `--aspect-set "0,60,90,120,180"` (explicit angle list)
   - `--harmonic-up-to 12` (range)
   - `--harmonic-only 12` (single)
2. Provide named presets that are documented: `classical` (5), `traditional` (7), `extended` (14), `all-14` (legacy compat).
3. The CLI `--help` must list every preset with the exact aspect angles included.
4. Print the resolved aspect set at the start of CLI output: `# Using aspect set: classical [0°, 60°, 90°, 120°, 180°]`.
5. Add `--list-aspect-sets` subcommand.

**Phase to address:** Phase 1 (configurable aspects) — UX/CLI design must be settled before implementation.

---

### Pitfall 10: CLI Default Output Change Breaks Script Parsers

**What goes wrong:**
v1.0 CLI emits 14 aspects in a specific format. Users have shell scripts piping `ketu` output through `jq`, `grep`, or `awk`. v1.1 changes the default → all those scripts silently produce different (or empty) results.

**How to avoid:**
1. **Must provide escape hatch**: `--harmonics all` (or `--aspect-set legacy-14`) tested and stable.
2. CHANGELOG with giant "BREAKING" banner for the default change.
3. UPGRADING.md with migration examples.
4. Output format **versioned**: emit `"format_version": "1.1"` in JSON outputs.

**Phase to address:** Phase 1 (legacy escape hatch); release phase (CHANGELOG and migration docs).

---

### Pitfall 11: Performance Regression — Filter In Inner Loop Instead of Upfront

**What goes wrong:**
Naïve implementation: in the per-date inner loop of `compute_aspects`, check `if aspect_name in user_aspect_set: ...`. With Python set lookups in the hot path, this can 2-5× slow down vectorized calculations.

**How to avoid:**
1. **Resolve filter once, before any loop.** Convert `aspect_set` to a NumPy boolean mask on the full `aspects` array at API entry. Subsequent code uses `aspects[mask]` (a view).
2. Maintain a benchmark suite. Run on every PR. Regress threshold: 10%.
3. If config-aware path is 50% slower than v1.0 baseline, reject the PR.

**Phase to address:** Phase 1 (configurable aspects) — DoD includes "benchmark <= v1.0 baseline within 5%."

---

### Pitfall 12: Test Coverage Drop When Adding Houses Module

**What goes wrong:**
Houses is substantial (~500 LOC: Placidus, Koch, sidereal time, polar fallback). Mediocre tests drop coverage from 91% → 85%. CI passes (no gate at 90%?), quality erodes silently.

**How to avoid:**
1. **Add coverage gate**: CI fails if `coverage < 90%` (project-wide) AND `coverage < 85%` (any module).
2. For `houses`, target ≥ 95%.
3. Reference fixtures: capture 10+ test cases (varied lat, including polar) from Swiss Ephemeris. Hardcode as `tests/fixtures/houses_reference.json`.
4. Property tests: cusps sum to 360°; cusps monotonic mod 360; Asc + 180° ≈ Desc.
5. Cross-system test: Whole-Sign cusps == 30° × sign boundaries.

**Phase to address:** Phase 2 (houses) — coverage gate added as part of phase, fixtures committed before merge.

---

### Pitfall 13: Documentation Drift — numpydoc + mypy Strict Not Maintained

**What goes wrong:**
Existing modules pass mypy strict + have full numpydoc. New `houses/` module added with sparse docstrings or `Any` types as a shortcut. Sphinx builds succeed but new module is undocumented.

**How to avoid:**
1. mypy strict enforced in CI for the entire package.
2. Sphinx build is part of CI: `-W` flag treats warnings as errors.
3. Pre-commit hook: `interrogate --fail-under=95`.
4. Each phase DoD: "All public APIs have numpydoc with Parameters / Returns / Examples."

**Phase to address:** Every phase — CI gate.

---

### Pitfall 14: Forgetting to Export New Modules in `__init__.py`

**What goes wrong:**
`ketu/__init__.py` has an `__all__` list. Developer adds `ketu/houses/` but forgets to expose `compute_houses` at top-level. Users can `from ketu.houses import compute_houses` but `from ketu import compute_houses` fails.

**How to avoid:**
1. Phase DoD checklist: "New public APIs in `ketu/__init__.py.__all__`."
2. Smoke test: `tests/test_public_api.py` enumerates expected top-level exports.
3. Sphinx autodoc surfaces missing exports.

**Phase to address:** Every phase that adds public APIs.

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. Aspect array shape change | Phase 1 — design before code | Invariant test on aspect order + length |
| 2. LRU cache config-blind | Phase 1 + Phase 2 | Test: change config, assert cache miss |
| 3. Wrong Lilith definition | Phase 3 — DEFINITION.md before code | 5+ reference dates from 2 sources agree |
| 4. Lilith breaks stored data | Phase 3 + release phase | UPGRADING.md Lilith section; legacy mode test |
| 5. Placidus polar undefined | Phase 2 — fallback in DoD | Test at lat=70°,80° passes |
| 6. Sidereal time precision | Phase 2 — pre-implementation audit | Cusps within 1 arcmin of Astro.com |
| 7. Placidus iterative convergence | Phase 2 — implementation | Iteration cap test + NaN-recovery test |
| 8. Inconsistent aspect filtering | Phase 1 — config threaded everywhere | Integration test asserts ≤5 aspects |
| 9. CLI `--harmonics 12` ambiguity | Phase 1 — UX/CLI design first | `--help` lists named presets |
| 10. CLI default change breaks scripts | Phase 1 (legacy flag) + release | `--harmonics all` returns v1.0 output |
| 11. Filter-in-inner-loop perf | Phase 1 — benchmark gate | ≤5% regression vs v1.0 |
| 12. Coverage drop adding houses | Phase 2 — coverage gate | CI fails if <90% |
| 13. Docs / mypy drift | Every phase — CI gate | mypy strict + sphinx -W + interrogate |
| 14. Missing top-level exports | Each public-API phase | `tests/test_public_api.py` |

---

## "Looks Done But Isn't" Checklist

- [ ] **Configurable aspects:** CLI threading verified — `ketu cycles --aspect-set X` and `ketu transits --aspect-set X` both honor X
- [ ] **Configurable aspects:** Cache invalidation verified — fresh results after config change
- [ ] **Houses:** Polar-region tests — `compute_houses(lat=80)` documented behavior
- [ ] **Houses:** Convergence cap exists — non-convergence raises or warns
- [ ] **Houses:** ≥10 reference charts validated against Astro.com or Swiss Ephemeris
- [ ] **Lilith fix:** `LILITH_DEFINITION.md` exists with primary source citation
- [ ] **Lilith fix:** Legacy mode (or documented as truly removed)
- [ ] **Lilith fix:** 5+ epoch reference values spanning 1900-2050
- [ ] **CLI:** `--list-aspect-sets` / `--list-house-systems` introspection commands
- [ ] **CLI:** Resolved config echoed in output
- [ ] **Public API:** `from ketu import compute_houses` works
- [ ] **Docs:** UPGRADING.md migration steps for v1.0 → v1.1
- [ ] **Docs:** Performance disclosure with benchmark numbers in CHANGELOG
- [ ] **CI:** Coverage gate fails at <90%
- [ ] **CI:** Benchmark regression check tracked
- [ ] **Downstream:** Kala / Surya maintainers notified before release

---

## Confidence Notes

- **HIGH:** Pitfalls 1, 2, 8, 11, 12, 13, 14 (verifiable in Ketu codebase)
- **HIGH:** Pitfalls 5, 6 (verified via Swiss Ephemeris docs, Astrowiki — Placidus polar limit at ±66.56° well-established)
- **HIGH:** Pitfall 3 (three Lilith definitions confirmed across 4+ independent sources)
- **MEDIUM:** Pitfall 7 (Placidus iterative convergence — failure modes inferred from numerical analysis)
- **MEDIUM:** Pitfall 4 (downstream impact — depends on whether Kala/Surya persist Lilith values)
- **HIGH:** Pitfalls 9, 10 (CLI UX patterns)

---

## Sources

- Ketu codebase: `ketu/core.py`, `ketu/aspects/core.py:73`
- [Astrodienst Astrowiki — Placidus House System](https://www.astro.com/astrowiki/en/Placidus_House_System)
- [Wikipedia: House (astrology) — polar limitations](https://en.wikipedia.org/wiki/House_(astrology))
- [Swiss Ephemeris official documentation](https://www.astro.com/swisseph/swisseph.htm)
- [pyswisseph house_cusp_calculation manual](https://github.com/astrorigin/pyswisseph/blob/master/docs/programmers_manual/house_cusp_calculation.rst)
- [Serennu — Mean & True Black Moon Lilith](https://serennu.com/astrology/mean-true-black-moon.php)
- [Kerykeion — Lilith calculations: Mean vs True](https://kerykeion.net/content/learn-astrology/lilith-true-vs-mean)
- [stjarnhimlen — sidereal time precision](https://stjarnhimlen.se/comp/ppcomp.html)
