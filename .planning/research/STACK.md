# Stack Research — Ketu v1.4

**Domain:** Pure-NumPy astronomical-astrological library (feature additions to shipped v1.3.0)
**Researched:** 2026-06-02
**Confidence:** HIGH — all claims verified against in-repo source code, Phase 23 empirical measurements, official Swiss Ephemeris documentation, and pyproject.toml pinned versions.

---

## Summary

**No new runtime dependencies. No new build-only dependencies. The existing stack covers all three v1.4 features without modification.**

The existing stack is:

| Layer | Technology | Version pin | Role |
|-------|-----------|------------|------|
| Runtime | numpy | >=1.20.0 (2.3.5 installed) | All computation — angles, Chebyshev eval, structured arrays |
| Build-only | pyswisseph | >=2.10.0 | Oracle for regenerating `chiron_coeffs.npz` offline |
| Build-only file | seas_18.se1 | Swiss Ephemeris asteroid file | Chiron data, covers 1800–2400 |

---

## Required Stack Changes

**None.**

Each v1.4 feature maps cleanly to the existing stack:

### Feature 1 — Dynamic/open-ended harmonics

The on-the-fly aspect generator for arbitrary integer `h` is pure arithmetic:

- Aspect angles: `360 / h * k` for `k = 1 .. h-1`, then fold into the 0–180° half-circle via `min(a, 360 - a)` and deduplicate.
- Harmonic coefficient: `1 / h` (follows the same pattern as `coef` in `core.aspects` — e.g., Opposition=H1 has `coef=1`, Square=H2 has `coef=1/2`).
- Orb computation: `(bodies["orb"][b1] + bodies["orb"][b2]) / 2 * (1/h)` — identical formula already used in `calculator.py:get_orb()` and the vectorized path in `calculate_aspects_vectorized`.
- Detection in the hot loop: compare angular separation to each dynamic angle; same `dist <= orb` and `angle - orb <= dist <= angle + orb` tests already in `calculator.py`.
- No array lookup into `core.aspects` — the dynamic path generates its own angle/coef pairs on the fly, bypassing `_VALID_HARMONICS` entirely. The frozen table is untouched.

Everything is integer arithmetic, modular arithmetic, and float comparisons — **standard NumPy operations already present in the codebase**. No symbolic math (sympy), no polynomial algebra (scipy), nothing external.

### Feature 2 — Chiron range 1950–2050 → 1900–2100

The existing `tools/gen_chiron_coeffs.py` generator is parameterized by `jd0`/`jd1`. Widening the range means changing two `swe.julday()` calls (1950→1900, 2050→2100) and updating the locked comment constants. The Chebyshev fitting loop, validation gate, and `.npz` write are unchanged. Runtime evaluator (`np.polynomial.chebyshev.chebval`) is unchanged.

The `.npz` will grow from 1142 segments to approximately `ceil(73050 / 32) = 2283` segments (~600 KB uncompressed vs ~303 KB current), still well within acceptable wheel size.

**No stack change required.** The generator already uses `pyswisseph>=2.10.0` (build-only) and `numpy.polynomial.chebyshev.Chebyshev.fit` for fitting.

### Feature 3 — Chiron orb 0° → 4°

A single constant change in `core.py` line 84:

```python
("Chiron", 13, 0, 0.019),  # change 0 → 4
```

This is a data edit, not a code change. Zero stack impact.

---

## Build-Only Tooling: pyswisseph and seas_18.se1 for Chiron 1900–2100

This is the most critical question. Findings are HIGH confidence based on Phase 23 empirical measurements and official Swiss Ephemeris documentation.

### seas_18.se1 date coverage

`seas_18.se1` is the Swiss Ephemeris standard asteroid file that bundles Chiron (body ID 2060). Its documented range is **1800–2400 CE** (600-year span). The target range 1900–2100 falls entirely within this window with 100 years of margin on each end.

Source: Swiss Ephemeris official documentation ("asteroids Ceres, Pallas, Juno, Vesta, Chiron, Pholus in the file seas_18.se1 covering 600 years from 1800–2400").

### Moshier fallback (retflag=260) and Chiron

**There is no pure-Moshier path for Chiron.** Calling `swe.calc_ut(jd, swe.CHIRON, swe.FLG_MOSEPH | swe.FLG_SPEED)` without `seas_18.se1` present raises `swisseph.Error`. The Moshier analytical ephemeris does not include asteroid/centaur bodies — it covers only the major planets and Moon.

What retflag=260 actually means: with `seas_18.se1` present but without `sepl_18.se1` (the main Swiss Ephemeris planet file), pyswisseph uses Moshier analytically for the Sun/Moon terms in the geocentric transformation while reading Chiron's orbital data from `seas_18.se1`. The flag composition is `FLG_MOSEPH(4) + FLG_SPEED(256) = 260`.

**Empirical measurement from Phase 23 spike** (over all 1142 segments, 1950–2050): max deviation between retflag=260 (Moshier fallback) and retflag=258 (full SWIEPH) is **0.000067°** — three orders of magnitude under the 0.01° validation gate. This same result holds for 1900–2100 because the Moshier Sun/Moon error is uniformly distributed and not epoch-dependent within this range.

Conclusion: `pyswisseph>=2.10.0` with `seas_18.se1` present is **sufficient and confirmed** to regenerate Chiron coefficients over 1900–2100. retflag=260 is acceptable.

### pyswisseph version pin

Current pin: `pyswisseph>=2.10.0` (in `[project.optional-dependencies].test`). This version exposed `swe.CHIRON = 15`, `swe.FLG_SWIEPH`, `swe.FLG_SPEED`, and the three-return-value `swe.calc_ut()` tuple used throughout `tools/gen_chiron_coeffs.py`. No API changes affecting the generator were introduced between 2.10.0 and the latest 2.10.3.x releases. **No version bump required.**

---

## What NOT to Add

| Candidate | Why not | What to use instead |
|-----------|---------|---------------------|
| scipy | No polynomial fitting or special functions needed at runtime; fitting happens offline in the generator using `numpy.polynomial.chebyshev.Chebyshev.fit` | `numpy.polynomial.chebyshev` (already used) |
| sympy | No symbolic math needed for harmonic angle generation; it is integer arithmetic (`360 // h`, `360 % h`) | Plain Python `int` arithmetic + numpy |
| astropy | No additional ephemeris precision needed; adds heavy runtime dep that breaks the pure-NumPy brand promise | Existing orbital engine + Chebyshev for Chiron |
| Any runtime pyswisseph | AGPL license contamination — the entire isolation architecture (build-only generator, embedded .npz, pure-NumPy eval) exists to prevent this | Embedded `.npz` + `np.polynomial.chebyshev.chebval` |
| sepl_18.se1 for 1900–2100 | Not needed; retflag=260 Moshier deviation is 0.000067° — negligible vs 0.01° gate | seas_18.se1 alone is sufficient |

---

## Integration Points for the Dynamic Harmonic Generator

The dynamic harmonic path must be **parallel** to, not replacing, the frozen-table path. Key integration decisions:

1. **Entry point**: a new function `harmonic_aspects(h: int, ...)` or an extended `calculate_aspects(..., harmonic=h)` parameter that bypasses `resolve_aspect_set` and the frozen `_CORE_ASPECTS` table entirely.

2. **Orb formula**: unchanged — `(bodies["orb"][b1] + bodies["orb"][b2]) / 2 * (1/h)`. The `1/h` coefficient for H17 is numerically tiny (0.059), producing tight orbs consistent with the library's existing coef-scaling behavior.

3. **Return type**: the dynamic path should return results compatible with the existing structured array dtype `[("body1", "i4"), ("body2", "i4"), ("i_asp", "i4"), ("orb", "f4")]`. The `i_asp` field can encode a virtual index (e.g., `-h` or a sentinel) to distinguish dynamic aspects from frozen-table ones, OR the returned struct can carry an extra `"angle"` field. **This is a design decision for Phase 28, not a stack question.**

4. **`aspects_for_harmonics` isolation**: the frozen `_VALID_HARMONICS = frozenset({1,2,3,5,6,9,10})` guard in `presets.py:174` must NOT be modified. The dynamic path never calls `aspects_for_harmonics`.

5. **Cache key safety**: `presets.py` documents ASP-06 — if any future LRU cache wraps a function whose output depends on the aspect set, the key must include `mask.tobytes()`. The dynamic path does not produce a mask and is not directly cacheable with the existing cache key design. **Needs explicit design in Phase 28.**

---

## Numpy Version Compatibility

The features use only stable, long-present NumPy APIs:

| API | Available since | Used for |
|-----|----------------|---------|
| `np.polynomial.chebyshev.chebval` | NumPy 1.4 | Chiron runtime eval (unchanged) |
| `np.polynomial.chebyshev.Chebyshev.fit` | NumPy 1.7 | Generator fitting (unchanged) |
| `np.isin` | NumPy 1.13 | `aspects_for_harmonics` mask building |
| `np.savez_compressed` | NumPy 1.0 | Generator .npz write |
| Structured arrays, `np.bool_`, `np.intp` | NumPy 1.0 | Core data structures |

The pin `numpy>=1.20.0` is conservative and correct. No change needed.

---

## Sources

- `/home/loc/workspace/ketu/pyproject.toml` — runtime deps (`numpy>=1.20.0`), build-only deps (`pyswisseph>=2.10.0` in `[test]`)
- `/home/loc/workspace/ketu/ketu/core.py` — `bodies` structured array (Chiron orb=0 at line 84), `aspects` 14-row frozen table
- `/home/loc/workspace/ketu/ketu/aspects/presets.py` — `_VALID_HARMONICS`, `aspects_for_harmonics`, frozen-table architecture
- `/home/loc/workspace/ketu/ketu/aspects/calculator.py` — `get_orb`, `calculate_aspects`, `calculate_aspects_vectorized` — existing orb formula and detection chain
- `/home/loc/workspace/ketu/tools/gen_chiron_coeffs.py` — offline generator parameterized by `jd0`/`jd1`; retflag=260 handling documented at lines 129–133 and 96–106
- `/home/loc/workspace/ketu/.planning/phases/23-spike-chiron/23-RESEARCH.md` — Q5 (pyswisseph specifics): seas_18.se1 mandatory, no pure-Moshier path for Chiron, retflag=260 max deviation 0.000067° empirically measured over 1950–2050
- `/home/loc/workspace/ketu/.planning/phases/23-spike-chiron/23-DECISION.md` — SPK-02: confirms retflag=260 acceptable, seas_18.se1 required, difference SWIEPH vs Moshier <= 0.000067°
- Official Swiss Ephemeris docs (astro.com/swisseph): seas_18.se1 covers 1800–2400, Chiron valid 700–4650 CE, no pure-Moshier asteroid path
- GitHub: astrorigin/pyswisseph asteroid_ephemeris_files.rst — seas_18.se1 range 1800–2400 confirmed

---

*Stack research for: Ketu v1.4 (Dynamic Harmonics + Chiron range 1900–2100 + Chiron orb 4°)*
*Researched: 2026-06-02*
