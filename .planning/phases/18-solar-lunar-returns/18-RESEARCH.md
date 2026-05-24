# Phase 18: Solar + Lunar Returns (Standard + Relocated) — Research

**Researched:** 2026-05-24
**Domain:** Pure-NumPy root-finding on `body_longitude(t) − natal_body_longitude` for Sun and Moon, factored behind a shared `_solve_return` helper; CHART_DTYPE assembly via `compute_chart(jd_return, return_lat, return_lon, system)`; subpackage `ketu/returns/` mirroring synastry/composite layout.
**Confidence:** HIGH (every astronomical primitive already exists in Ketu v1.0/v1.1/v1.2 — Sun/Moon longitude is exposed via `calc_planet_position(jd, 0|1)` and `calc_planet_position_batch`, the chart-assembly is `compute_chart`, the root-finder is ~30 lines of pure-NumPy bisection; novelty is only the public API surface, the shared helper, and the wrap-around convention).

---

## User Constraints (no CONTEXT.md — ROADMAP Phase 18 success criteria are binding)

No `/gsd:discuss-phase` was run for this phase. Per the orchestrator brief, the **six** ROADMAP success criteria for Phase 18 (updated at commit `5d90e43`) are treated as **LOCKED decisions** — the planner must honor them verbatim.

### Locked Decisions (from ROADMAP success criteria + REQUIREMENTS RET-01..05 / LRET-01..05)

1. **Solar API.** `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus") → CHART_DTYPE` returns a `CHART_DTYPE` for the resolved Sun-return moment; passing `return_lat`/`return_lon` produces a relocated chart, `None` (default) uses the natal lat/lon (standard return). (RET-01)
2. **Lunar API.** `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system="placidus") → CHART_DTYPE` returns a `CHART_DTYPE` for the **first Moon-return moment ≥ `target_jd`** (Moon sidereal/tropical period ≈ 27.32 d); same relocation contract as `solar_return`. (LRET-01)
3. **API asymmetry is deliberate.** Solar takes `target_year` (calendar-anchored, integer year), lunar takes `target_jd` (instant-anchored, Julian Date float). **Both docstrings document this asymmetry loudly.** (LRET-05)
4. **Shared `_solve_return` helper — non-negotiable factorisation.** The pure-NumPy root-finder on `body_longitude(t) − natal_body_longitude` is factored into a single internal helper `_solve_return(body, natal_jd, natal_lon_ref, t0, t_window, ...)`; **`solar_return` and `lunar_return` both call it**, parametrised only by body identity and the search window. Wrap-around 360°→0° is handled centrally (pre-unwrap or atan2-style residuals). (LRET-02; ROADMAP success criterion #3)
5. **Wrap-around regression tests on both Sun and Moon.** Pinned wrap-around test cases for both return types prove the central wrap-around handling. (LRET-02 + RET-02)
6. **Convergence target.** <1 arc-second on the resolved time for both Sun and Moon. (RET-03 + LRET-03)
7. **Oracle tests.** 3 solar + 3 lunar reference returns hand-validated against Astro.com (each set includes one wrap-around case; lunar set also includes one case where the return falls on the calendar day *after* `target_jd` to lock the "first return ≥ target" contract). (RET-04 + LRET-04)
8. **Relocation contract.** Passing `return_lat/lon` shifts the houses to the new location; `None` (default) uses natal lat/lon (standard return). Both docstrings distinguish **loudly** between `natal_lat/lon` (used for the natal body longitude reference) and `return_lat/lon` (used for return-chart houses). (RET-05 + LRET-05)

### Claude's Discretion (planner's freedom areas)

- **Module path.** Recommended: `ketu/returns/` subpackage with `solar.py`, `lunar.py`, `_solve.py` (private helper module). Alternative: flat `ketu/returns.py` single module. See §Module Layout for justification.
- **Helper signature shape.** `_solve_return(body_id, natal_lon_ref, t_initial_guess, search_half_width, max_iter, tol_deg)` vs. `_solve_return(body_lon_callable, ...)`. See §Shared `_solve_return` Helper.
- **Algorithm choice.** Bisection vs. hand-rolled Brent vs. Newton. See §Root-Finding Algorithm Choice.
- **Stopping criterion.** Residual in degrees ≤ 1/3600° vs. time delta ≤ ε days vs. both. See §Stopping Criterion.
- **Astro.com cross-check timing.** Same as Phase 17 — manual one-time human capture, deferred to a follow-up note (bot-blocked from automated retrieval). Self-consistency oracle is the primary gate.
- **Coverage gate naming.** Recommended: `returns_coverage_gate` pytest marker + `make returns-coverage` Makefile target + new requirement `RET-06: ketu.returns ≥95% line coverage gate` (mirror of COMP-05 / SYN-05 / CHART-05 / HOU-09). Land in close-out plan.
- **Plan count.** Recommended: **5 plans** (foundation/scaffold + helper, solar API, lunar API, oracles, close-out). See §Plan Decomposition.
- **CLI sub-command.** Not required by RET-01..05 or LRET-01..05. Keep out of scope for this phase (mirrors synastry/composite — no CLI added). Future follow-up if user demand surfaces.

### Deferred Ideas (OUT OF SCOPE for Phase 18)

- **Saturn / Jupiter / generic body returns.** Same algorithm would work, but the spec is locked to Sun + Moon. Deferred to v1.3 if demand surfaces. The `_solve_return` helper is body-parametrised, so adding a third body later is ~20 LOC of public API, but Phase 18 ships Solar + Lunar only.
- **Demi-returns (semi-solar at 6 months, lunar quarter-returns).** Out of scope.
- **Progressed Solar Return.** Different technique (progressing the natal then returning); out of scope.
- **Return-to-return aspect grids.** Different concern; aspect_matrix on the return CHART_DTYPE already captures intra-return aspects via `compute_chart`.
- **Vectorisation over arrays of `target_year` / `target_jd`.** Phase 18 ships scalar API only (one return per call). The shared `_solve_return` helper SHOULD be written to support vectorised inputs (NumPy-native bisection over arrays is ~free), but the public `solar_return` / `lunar_return` accept scalars per the spec. Vectorised public API is a v1.3 follow-up.
- **Astrological-feature derivations on the return chart** (return Sun house, return-to-natal aspects, etc.). Not in RET/LRET-01..05.

---

## Summary

Phase 18 is **composition over invention** — every astronomical primitive already exists in Ketu. The phase ships two public functions (`solar_return`, `lunar_return`), one private helper (`_solve_return`), and one new subpackage (`ketu/returns/`). Total new code ≈ 250 LOC + ~150 LOC of tests + 6 oracle fixtures.

The work breaks into three orthogonal concerns:

1. **Root-finding on a wrapped-circle residual** (the only novel math). Pure-NumPy bisection on `body_lon(t) − natal_lon_ref`, with the residual lifted onto `(-180°, +180°]` via `((Δ + 540) % 360) − 180`. This is the same signed-short-arc trick already used in `ketu/composite/core.py:79-81` (the `circular_midpoint` helper) and in `ketu/houses/porphyry.py:159` — Phase 18 reuses the convention.
2. **Chart assembly at the resolved JD.** Call `compute_chart(jd_return, return_lat, return_lon, system)` and return its output. `compute_chart` is fully generic — its docstring says "natal chart" but mathematically it takes any `(jd, lat, lon, system)` quadruple. The `polar_fallback="porphyry"` flag is the escape hatch for polar relocations.
3. **API surface plumbing.** `solar_return` resolves `target_year` to an initial `jd_seed = natal_jd + (target_year − natal_year) × 365.25` (close enough to bracket within ±36 h); `lunar_return` resolves `target_jd` to the first return ≥ `target_jd` by seeding at `target_jd + n × 27.321582` for the smallest non-negative `n` such that `body_lon(seed) − natal_Moon_lon` crosses through zero within the bracket. The shared `_solve_return` receives `(body_id, natal_lon_ref, t_seed, half_window)` and returns the converged `jd`.

**Primary recommendation:** Implement `ketu/returns/` as a new subpackage with **5 sequential plans**: (1) foundation/scaffold (subpackage skeleton + `_solve_return` helper + wrap-around regression suite); (2) `solar_return` API (RET-01..03/05); (3) `lunar_return` API (LRET-01..03/05); (4) oracle fixtures + Astro.com cross-check deferral note (RET-04 + LRET-04); (5) close-out (coverage gate + CHANGELOG + REQUIREMENTS flips). Use **pure-NumPy bisection** with a dual stopping criterion (`|residual_deg| ≤ 1/3600` OR `|jd_high − jd_low| ≤ 1e-7 d ≈ 8.6 ms`). Use **tropical month = 27.321582 d** for the lunar period seed (matches Ketu's tropical convention via `get_moon_position`). Astro.com oracles are hand-validated one-time by the developer, deferred per Phase 16/17 precedent. The whole phase lands in ~250 LOC + tests.

---

## Codebase Landmarks

| File | Why it matters for Phase 18 |
|------|------------------------------|
| [`ketu/charts/api.py`](../../../ketu/charts/api.py) — `compute_chart` (lines 193–357) | **The return chart's assembly path.** Solar and lunar returns both end with `out = compute_chart(jd_return, return_lat, return_lon, system, polar_fallback="porphyry")`. The function is fully generic — no `natal`-specific logic anywhere (the word "natal" only appears in docstrings, not in the math). Pass `polar_fallback="porphyry"` to make polar relocations safe (D-11 / D-15). |
| [`ketu/ephemeris/planets.py`](../../../ketu/ephemeris/planets.py) — `calc_planet_position` (lines 68–195), `calc_planet_position_batch` (lines 431–555) | **The Sun/Moon longitude workhorse.** `calc_planet_position(jd, planet_id=0)` returns Sun [lon, lat, dist, lon_speed, ...]; `planet_id=1` for Moon. The batch form `calc_planet_position_batch(jd_array, planet_id=0)` is natively vectorised — `_solve_return` can pass a NumPy array of candidate JDs and get back a `(N, 6)` array, so a vectorised bisection step costs one call per iteration regardless of the bracket width. Both functions return **apparent geocentric** longitudes for Sun and Moon (no aberration applied to ids 0 and 1 — see line 191 `if planet_id >= 2`). |
| [`ketu/ephemeris/planets.py`](../../../ketu/ephemeris/planets.py) — `find_exact_aspect` (lines 273–342) | **Existing precedent for "find when a body-pair angular function == target".** Uses a hand-rolled bisection with `max_iterations=50` and `tolerance=0.001` (days = ~1.5 minutes). Phase 18 needs ~1 arcsecond on the resolved time, which is much tighter (~1e-7 d ≈ 9 ms) — bisection from a ±36 h bracket reaches that in ~30 iterations (2^30 ≈ 1e9 → 36 h / 1e9 ≈ 0.13 µs, way overshoot). **The existing function is too loose to reuse directly**, but its structure (`get_angle_diff` closure → bisection loop with sign-check) is the right template. Document this as "stricter cousin" in the helper docstring. |
| [`ketu/aspects/core.py`](../../../ketu/aspects/core.py) — `refine_exact_moment` (lines 106–179) | **Second existing bisection precedent.** Uses a `distance_callback` closure pattern (lines 137–141 docstring) — exactly the shape `_solve_return` should expose internally. Note: `refine_exact_moment` does NOT handle wrap-around (it computes `abs(diff)`, losing sign); Phase 18 must NOT reuse this pattern as-is because returns need a signed residual that wraps. |
| [`ketu/composite/core.py`](../../../ketu/composite/core.py) — `circular_midpoint` (lines 17–87) | **The wrap-around trick precedent.** Lines 79–81: `diff_ab = (b - a) % 360.0; short = np.where(diff_ab <= 180.0, diff_ab, diff_ab - 360.0)` — this is the signed-short-arc reduction Phase 18 reuses verbatim for the residual `body_lon(t) − natal_lon_ref`. The math is identical; the planner should explicitly note "same trick as `circular_midpoint`" in the `_solve_return` docstring and ideally pin a regression test that both helpers agree on a sample. |
| [`ketu/charts/core.py`](../../../ketu/charts/core.py) — `CHART_DTYPE` (line 85) | **The output dtype.** Returns produce a scalar (0-d) `CHART_DTYPE`. No new dtype is introduced. |
| [`ketu/synastry/api.py`](../../../ketu/synastry/api.py) + [`ketu/composite/api.py`](../../../ketu/composite/api.py) | **Subpackage layout precedent.** Phase 16 (synastry) and Phase 17 (composite) established the pair-chart subpackage shape: `api.py` with the public function, `core.py` for helpers, `__init__.py` re-exports. Phase 18 mirrors this, with the addition of a `_solve.py` private module for the shared root-finder (which sits between `solar` and `lunar`, conceptually neither). |
| [`ketu/houses/registry.py`](../../../ketu/houses/registry.py) — `SYSTEMS` registry | **House system validation pass-through.** `compute_chart` already validates `system=` via `calculate_houses` (it raises `ValueError` on unknown systems). Phase 18 doesn't need its own validation. Six systems are available as of Phase 15: `placidus`, `koch`, `porphyry`, `whole_sign`, `equal`, `regiomontanus`. |
| [`ketu/composite/api.py`](../../../ketu/composite/api.py) — `calculate_composite` (lines 82–250) | **Closest API shape precedent.** A pair-chart compute that wraps `compute_chart`-style assembly. Phase 18's `solar_return`/`lunar_return` mirror its docstring structure (locked-decisions block, See Also, Notes with loud UTC/asymmetry guards). |
| [`pyproject.toml`](../../../pyproject.toml) lines 61, 77–82 | **`[tool.setuptools].packages`** must include `"ketu.returns"`. **`[tool.pytest.ini_options].markers`** must register `returns_coverage_gate` alphabetically between `composite_coverage_gate` and `houses_coverage_gate`. |
| [`Makefile`](../../../Makefile) lines 64–80 | **`composite-coverage` target (lines 68–80)** is the template for `returns-coverage`. Same two-step pattern (`pytest tests/returns/ -o addopts="" --cov --cov-report= --cov-fail-under=0` then `coverage report --include='ketu/returns/*' --fail-under=95 -m`). Add `returns-coverage` to the `.PHONY` line. |
| [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md) lines 45–57 | RET-01..05 + LRET-01..05 definitions (verified at commit head 2026-05-24). Mostly French (project persona) but precise on the contract. |
| [`.planning/phases/17-composite-chart-midpoint-variant/17-RESEARCH.md`](../17-composite-chart-midpoint-variant/17-RESEARCH.md) | **Stylistic precedent.** Phase 17's RESEARCH established the user-constraints / locked-decisions / discretion / deferred-ideas trichotomy and the §Codebase Landmarks table. Phase 18 follows the same shape. |
| [`.planning/phases/17-composite-chart-midpoint-variant/17-04-PLAN.md`](../17-composite-chart-midpoint-variant/17-04-PLAN.md) | **Close-out plan precedent.** Coverage gate + CHANGELOG + REQUIREMENTS flips + Astro.com deferral note + 4-criteria smoke. Phase 18 close-out (Plan 18-05) is a near-verbatim copy with COMP→RET substitutions. |

---

## Existing Sun/Moon Longitude API in Ketu

### Available signatures

```python
# Scalar form (LRU-cached, hot for solo lookups):
calc_planet_position(jd: float, planet_id: int, flags: int = 0) -> np.ndarray
# returns [lon, lat, dist, lon_speed, lat_speed, dist_speed]
# planet_id=0 (Sun), planet_id=1 (Moon)

# Batch / vectorised form (natively vectorised over jd):
calc_planet_position_batch(jd_array: np.ndarray, planet_id: int, flags: int = 0) -> np.ndarray
# returns shape (N, 6); same column order
```

Both functions live in `ketu/ephemeris/planets.py`. For Sun the geocentric longitude is computed from Earth's heliocentric position via `get_body_position(BODY_INDICES["Sun"], jd)` and a sign flip (lines 91–106). For Moon it's the perturbation-corrected `get_moon_position(jd)` (lines 108–123) — Meeus 2nd-ed. lunar theory with 12 longitude perturbation terms (evection, variation, yearly equation, parallactic, etc., visible at `orbital.py:549-562`).

### Apparent vs. true longitude — convention check

**Sun.** No aberration correction is applied (gated at `planets.py:190 — if planet_id >= 2`). The Sun's geocentric longitude in Ketu is **mean apparent geocentric longitude minus aberration** — i.e. **true geocentric longitude**, not apparent. Astro.com uses **apparent** geocentric longitude (Swiss Ephemeris default: `SEFLG_SPEED | apparent`, ~20.5 arcsec aberration correction for Sun). **Expected systematic delta vs. Astro.com: ~20 arcsec on Sun longitude.**

**Moon.** No aberration applied (same gate). Moon's aberration is tiny (it's geocentric and very close), so this is a non-issue for Moon — the Ketu Moon longitude agrees with Astro.com to well within the Meeus theory's residual error (~5-10 arcsec typical).

**Practical implication for returns.**
- Solar return: Ketu resolves the instant when **true geocentric Sun longitude** = natal true geocentric Sun longitude. Astro.com resolves the instant when **apparent geocentric Sun longitude** = natal apparent geocentric Sun longitude. **Both natal AND return use the same convention, so the ~20 arcsec aberration cancels** — the **resolved instant** is identical to ~milliseconds (the aberration drift over a year is ~0.04 arcsec, completely negligible). Document this in the docstring as "internally consistent — natal-to-return uses the same convention; cross-tool deltas vs. Astro.com on the resolved instant should be sub-second despite the apparent/true distinction".
- Lunar return: Same logic; cancellation is exact for the small aberration term.

**Confidence:** HIGH on Ketu's API (read the source); HIGH on the cancellation logic (this is a textbook same-convention-both-sides argument).

### Vectorisation status

`calc_planet_position_batch(jd_array, 0)` and `calc_planet_position_batch(jd_array, 1)` are natively vectorised — they call `get_body_position_vectorized` / `get_moon_position_vectorized` under the hood (lines 463 and 486 of `planets.py`). **The `_solve_return` helper SHOULD use the batch form** even though it operates on scalars per public-API call, because:

1. A vectorised bisection (passing `np.array([jd_lo, jd_mid, jd_hi])` per iteration) gets 3 evaluations for the cost of 1 — modest speedup but free.
2. If a v1.3 follow-up vectorises the public API over arrays of `target_year` / `target_jd`, the helper is already ready.
3. The LRU cache on `calc_planet_position` (line 68, `maxsize=128`) becomes irrelevant for bisection (every iteration is a fresh JD); the batch form bypasses the cache cleanly.

**Recommendation:** Use `calc_planet_position_batch(np.atleast_1d(jd), body_id)[:, 0]` to extract longitudes. Always returns a NumPy array; cast back to scalar at the helper boundary if needed.

---

## Shared `_solve_return` Helper

This is the **architectural heart of Phase 18** and Success Criterion #3 makes its existence non-negotiable.

### Recommended signature

```python
def _solve_return(
    body_id: int,                  # 0 (Sun) or 1 (Moon); pass-through to calc_planet_position_batch
    natal_lon_ref: float,          # natal longitude of `body_id` to return to, degrees [0, 360)
    t_seed: float,                 # initial guess JD (near the expected return time)
    half_window_days: float,       # bracket half-width: ±36 h for Sun, ±1.5 d for Moon (see §Bracket Strategy)
    *,
    max_iter: int = 60,            # bisection caps at 2^-60 ≈ 8.7e-19 d ≈ subatomic; 50 is sufficient (see Stopping)
    tol_deg: float = 1.0 / 3600.0, # residual threshold (1 arc-second per RET-03/LRET-03)
    tol_days: float = 1e-7,        # time-delta threshold (8.6 ms; overshoots arc-second per body's speed)
) -> float:
    """Pure-NumPy bisection for body-longitude returns. Wrap-around handled centrally.

    Returns the JD at which body_lon(jd) == natal_lon_ref to within tol_deg
    of the signed-short-arc residual, or to within tol_days of bracket width
    (whichever comes first).
    """
```

### Why this signature (rationale per parameter)

- **`body_id: int`** rather than a callable. The body's longitude function is a property of `calc_planet_position_batch` — there's no reason to inject a callable (single source of truth for the ephemeris). `body_id=0` Sun / `body_id=1` Moon are the only call sites; the helper is private (no public extensibility surface), so the closed signature is fine. Extending to Saturn returns (v1.3) is a one-line change (`body_id=6`).
- **`natal_lon_ref: float`** rather than `(natal_jd, natal_body_id)`. Solar/lunar reads the natal longitude from `calc_planet_position(natal_jd, body_id)[0]` **once** at the public-API boundary, then passes the scalar in. Decouples the helper from "what counts as natal" semantics. **Crucially**, this means the helper never recomputes the natal longitude per iteration (cheap, but conceptually cleaner).
- **`t_seed: float`** + **`half_window_days: float`** form an initial bracket `[t_seed - half_window_days, t_seed + half_window_days]`. The caller is responsible for choosing the seed correctly; the helper raises (or returns NaN) if the bracket does not contain a zero of the signed residual.
- **`max_iter=60`** is **generous** for bisection. Each iteration halves the bracket. Starting from ±36 h (3 days width), 30 iterations → 2.8e-9 d ≈ 0.24 ms; 50 iterations → 2.7e-15 d ≈ 230 picoseconds. **30 iterations is comfortably sufficient for <1 arcsec.** Keeping 60 as the cap is "overkill for safety" — no measurable performance cost (the loop is bounded to ~60 NumPy calls).
- **`tol_deg=1/3600`** is the arc-second residual threshold. The bisection terminates as soon as `|signed_residual(jd_mid)| < tol_deg`. RET-03 / LRET-03 require **<1 arc-second on the resolved time**, which is a stricter ask if interpreted literally: 1 arc-second of Sun longitude = 1″ / (0.985647°/d) ≈ 1.017e-5 d ≈ 0.88 s; 1 arc-second of Moon longitude = 1″ / (13.176°/d) ≈ 7.6e-7 d ≈ 66 ms. **So `tol_deg=1/3600` is the right threshold for Sun-equivalent time precision; the Moon converges to ~66 ms wall-clock per the same residual threshold.** Document this LOUDLY in the helper docstring (and in the public functions): the spec is "arc-second on the resolved Sun/Moon longitude", which translates to **sub-second on the time for Sun, sub-100ms on the time for Moon** — both well below 1 arc-second of body longitude.
- **`tol_days=1e-7`** is the time-delta fallback. 1e-7 d ≈ 8.6 ms — a hard floor below which bisection stops regardless of residual. Protects against the (impossible-in-practice but theoretically possible) case where the residual oscillates due to floating-point noise in `get_moon_position` near the root.

### Wrap-around handling — centralised

The residual `body_lon(t) − natal_lon_ref` is in `[-360, +360]` because both longitudes are normalised to `[0, 360)`. The signed-short-arc reduction lifts it to `(-180, +180]`:

```python
def _signed_residual(lon: np.ndarray, ref: float) -> np.ndarray:
    """Signed short-arc residual in (-180, +180]. Same trick as
    circular_midpoint (ketu/composite/core.py:79-81) and porphyry_cusps
    (ketu/houses/porphyry.py:159).
    """
    return ((lon - ref + 540.0) % 360.0) - 180.0
```

**Why pre-unwrap, not `arctan2(sin, cos)`:** Both work. `((x + 540) % 360) - 180` is **2 cheap ops vs. ~10** (sin + cos + arctan2), and **bit-identical** at the wrap (no trig rounding). The complex-number variant `np.angle(np.exp(1j * np.deg2rad(diff)))` is even more elegant but introduces ~1 ulp of error via `deg2rad`/`rad2deg`. **Recommendation: pre-unwrap via `((x + 540) % 360) - 180`** to match the existing Ketu convention (`composite/core.py`, `houses/porphyry.py`).

### Inner loop (pure-NumPy bisection)

```python
def _solve_return(body_id, natal_lon_ref, t_seed, half_window_days, *,
                  max_iter=60, tol_deg=1/3600, tol_days=1e-7):
    t_lo = t_seed - half_window_days
    t_hi = t_seed + half_window_days

    # Evaluate at both endpoints (vectorised single call):
    lons = calc_planet_position_batch(np.array([t_lo, t_hi]), body_id)[:, 0]
    r_lo = ((lons[0] - natal_lon_ref + 540.0) % 360.0) - 180.0
    r_hi = ((lons[1] - natal_lon_ref + 540.0) % 360.0) - 180.0

    if r_lo * r_hi > 0:
        # Bracket does not contain a sign change; caller's seed was wrong.
        # Either raise ValueError or extend the bracket (see §Open Questions).
        raise ValueError(f"No return in [{t_lo}, {t_hi}] for body_id={body_id}")

    for _ in range(max_iter):
        t_mid = 0.5 * (t_lo + t_hi)
        lon_mid = calc_planet_position_batch(np.array([t_mid]), body_id)[0, 0]
        r_mid = ((lon_mid - natal_lon_ref + 540.0) % 360.0) - 180.0

        if abs(r_mid) < tol_deg:
            return float(t_mid)
        if (t_hi - t_lo) < tol_days:
            return float(t_mid)

        if r_lo * r_mid < 0:
            t_hi, r_hi = t_mid, r_mid
        else:
            t_lo, r_lo = t_mid, r_mid

    return float(0.5 * (t_lo + t_hi))
```

~25 LOC, pure NumPy, single source of truth for wrap-around. **This is essentially the whole "novelty" of Phase 18.**

### Where the helper lives

**Recommendation:** `ketu/returns/_solve.py` (private module; underscored). Solar and lunar import from `._solve import _solve_return`. The `_` prefix communicates "not public API" without needing `__all__` plumbing. Tests reach into it via `from ketu.returns._solve import _solve_return` (private import; tests are allowed to do this).

**Confidence:** HIGH on the algorithm choice (bisection trivially converges; the spec is achievable by huge margins); HIGH on the wrap-around convention (it's the Ketu house convention, reused).

---

## Root-Finding Algorithm Choice

The constraint **"pure NumPy, no scipy"** (PROJECT.md / CLAUDE.md / REQUIREMENTS.md line 104) eliminates `scipy.optimize.brentq` directly. Four pure-NumPy options remain:

| Algorithm | Iterations to <1″ from ±36h bracket | Curvature handling | Pure-NumPy LOC | Recommendation |
|-----------|-------------------------------------|---------------------|----------------|----------------|
| **Bisection** | ~30 (linear in `log2`) | Indifferent — always converges if bracketed | ~15 LOC | **YES** |
| Hand-rolled Brent | ~6-10 (super-linear) | Combines bisection + secant; robust | ~50 LOC | NO (overkill) |
| Newton | ~3-4 (quadratic) | **Fails on Moon's d²θ/dt² inflection points**; needs careful derivative; no safety net | ~20 LOC + derivative | NO (fragile) |
| Secant | ~5-6 (super-linear) | Fragile near horizontal tangents (Moon at apogee parallactic peaks) | ~20 LOC | NO (no margin) |

**Bisection rationale (Ketu-specific):**

1. **Sun:** Monotonic over ±36h with mean motion 0.985647°/d. Bracket width ≈ 1.5°; root certain to be inside; ~30 iterations to <1″.
2. **Moon:** Mean motion 13.176°/d but with up to ±15% variation across a sidereal month (anomalistic perigee/apogee, parallactic perturbation). **Never reverses** (geocentric Moon is never retrograde), so the residual is monotonic. ±1.5 d bracket ≈ 20°; root certain to be inside; ~32 iterations to <1″.
3. **Bisection is indifferent to second-derivative curvature.** Newton and secant can overshoot or stall on the Moon's parallactic peaks; bisection cannot. **Safety margin matters more than iteration count** for Phase 18 — the function evaluations are cheap (~µs per call to `calc_planet_position_batch`), so 30 iterations × 1 µs = 30 µs per return — completely negligible.
4. **Existing precedent in Ketu.** `find_exact_aspect` (`planets.py:273`) and `refine_exact_moment` (`aspects/core.py:106`) both use bisection. Phase 18 stays consistent.

**Hand-rolled Brent considered and rejected.** Brent combines bisection with inverse-quadratic interpolation, giving super-linear convergence with bisection's robustness — the "textbook right answer" for one-sided black-box root-finding. **But:** ~50 LOC of careful Python with multiple algorithm-switching branches; one stale subtle bug per refactor; the speedup (~30 → ~10 iterations) saves ~20 µs per return. **Not worth the complexity** for Phase 18's scale (one return per call, milliseconds-of-wall-clock budgets). Document in `_solve.py` docstring: "Bisection chosen for simplicity + safety margin; Brent's method would converge in ~10 iterations vs. ~30 but is ~50 LOC of more delicate code with no measurable user-facing benefit at v1.2 call frequencies."

**Confidence:** HIGH (bisection is the textbook safe-default; existing Ketu precedent).

---

## Stopping Criterion (Concrete Numbers)

Two thresholds (whichever fires first):

| Threshold | Value | Interpretation |
|-----------|-------|----------------|
| **Residual** | `tol_deg = 1.0 / 3600.0 = 2.7778e-4°` | 1 arc-second on body longitude (the spec, RET-03 / LRET-03). |
| **Time delta** | `tol_days = 1e-7 d ≈ 8.6 ms` | Floor — bisection stops if the bracket width shrinks below this regardless of residual. Prevents oscillation from FP noise. |

**Iteration count derivation:**

- Sun, ±36 h bracket = 3 d width. To reach `tol_days = 1e-7 d`: `log2(3 / 1e-7) ≈ 25` iterations. To reach `tol_deg = 1/3600 = 2.78e-4°` at Sun speed 0.985647°/d: bracket width `≈ tol_deg / 0.985647 ≈ 2.82e-4 d ≈ 24 s`, so `log2(3 / 2.82e-4) ≈ 13` iterations. **13 iterations for Sun (residual-driven; first to fire).**
- Moon, ±1.5 d bracket = 3 d width. To reach `tol_deg = 1/3600 = 2.78e-4°` at Moon speed 13.176°/d: bracket width `≈ tol_deg / 13.176 ≈ 2.11e-5 d ≈ 1.8 s`, so `log2(3 / 2.11e-5) ≈ 17` iterations. **17 iterations for Moon (residual-driven; first to fire).**

**Verification:** Both well under `max_iter=60`. `max_iter` is a runaway guard, not the expected stop.

**Tightness check:** `tol_deg = 1/3600` and `tol_days = 1e-7` are NOT both binding at once; the residual fires first by ~10× margin. Setting `tol_days = 1e-7` is "overkill for safety". The planner could relax to `tol_days = 1e-6` (~86 ms, Sun) and it would still hit <1″, but leaving 1e-7 gives margin for future tighter specs without re-validation.

**Recommendation:** Pin both thresholds as module constants (`_TOL_DEG`, `_TOL_DAYS`) at the top of `_solve.py`. Document in helper docstring. Add a `test_solve_return_converges_in_expected_iterations` test that pins ~17 iterations as the Moon nominal (catches regression if the bisection logic accidentally drifts toward linear).

**Confidence:** HIGH (basic numerical analysis).

---

## Wrap-Around Handling

### Two canonical approaches

| Approach | Formula | Pros | Cons |
|----------|---------|------|------|
| **Pre-unwrap** | `r = ((lon - ref + 540) % 360) - 180` | 2 cheap ops; bit-identical at the seam; matches Ketu convention (composite, porphyry) | None for return purposes |
| **atan2 / complex-exponential** | `r = np.rad2deg(np.angle(np.exp(1j * deg2rad(lon - ref))))` | Same result; "obviously correct"; vectorises identically | ~10 ops; introduces ~1 ulp via deg/rad roundtrip; deviates from Ketu convention |

**Recommendation:** **Pre-unwrap.** Matches the existing Ketu convention used in `composite/core.py:79-81` and `houses/porphyry.py:159`. Avoids unnecessary trig rounding. Single source-of-truth: define a `_signed_residual_deg(lon, ref)` inline helper inside `_solve.py` and use it for both Sun and Moon residuals.

### Wrap-around test cases (pin in regression suite)

Both must be tested for BOTH return types (Sun and Moon):

1. **Natal body near 0°/360° seam.** Pick a natal date where natal Sun ≈ 0.05° (e.g. ~March 21 vernal equinox + few hours). Verify `solar_return(natal_jd, ..., target_year)` for some target year >> natal year returns a JD whose Sun longitude is within 1″ of 0.05°. The bisection's residual reduction `((lon - 0.05 + 540) % 360) - 180` must navigate the 360°→0° wrap cleanly.
2. **Natal body just past 0°.** Pick natal Sun ≈ 359.95° (e.g. ~March 19 around the vernal equinox − few hours). Same verification. Both 0°/360°-adjacent cases are covered.
3. **Moon wrap-around analogue.** Natal Moon ≈ 0.1° at some natal date; pick `target_jd` such that the first lunar return crosses the 359°→0° seam during the bisection bracket. Same residual logic applies.

**Recommendation:** Bundle wrap-around tests in `tests/returns/test_solve_return.py`, parametrised on `(body_id, natal_lon_ref_near_seam)`. The bisection helper is body-agnostic, so the same test infrastructure covers Sun and Moon.

**Confidence:** HIGH (the trick is textbook; the regression-test recipe is concrete).

---

## Initial Bracket / Window Strategy

### Solar return seed

- **Period:** Tropical year ≈ 365.24219 d (NOT sidereal year 365.25636 d — natal Sun longitude is in the tropical zodiac). For Ketu's purposes, **365.2422 d** is accurate to within ~0.001 d/year drift over a 100-year span — well within the ±36 h bracket margin. Use `365.2422` as the constant.
- **Seed formula:** `t_seed = natal_jd + (target_year - natal_year) * 365.2422`
  - Where `natal_year` is extracted from `natal_jd` via `julian_to_utc(natal_jd).year`. Off-by-one concerns: if the natal date is January and `target_year` is the natal year + N, the calendar birthday in year `target_year` is exactly N tropical years after the natal moment, give or take ~6 hours (the calendar/tropical-year drift). ±36 h covers this.
- **Bracket half-width:** `half_window_days = 1.5` (±36 h). Sun moves ~0.986°/d, so the bracket is ~3° wide — well over Sun's typical year-to-year drift of ~0.04° at the target longitude (sub-arcsecond per year of residual drift), confirming the root is well inside the bracket.
- **Why not narrower?** ~6 h is empirically the typical year-to-year residual at the target longitude (the calendar/tropical drift), but ±36 h gives a 6× safety margin for edge cases (leap years, natal date near a year boundary).

**Leap-year edge case (Feb 29 natal):** For a Feb 29 natal in a non-leap target year, the calendar birthday "doesn't exist." The seed formula `natal_jd + (target_year - natal_year) * 365.2422` still gives a valid JD (it's a tropical-year offset, NOT calendar-anchored). The resolved return falls within ±2 d of Feb 28 / March 1 of the target year, depending on the Sun's exact longitude crossing. **No special case needed in code — the math is "find when Sun = natal_Sun in target_year", which is well-defined for every date including Feb 29.** Document in the docstring: "Feb 29 natals resolve normally; the return time will fall in late Feb or early March of non-leap target years."

### Lunar return seed

- **Period:** **Tropical month = 27.321582 d** (Earth precession-accounting, returning to the tropical-zodiac longitude). Use this constant, NOT the sidereal month (27.321661 d, fixed-stars reference) or the anomalistic month (27.554550 d, perigee-to-perigee). **Ketu's Moon longitude via `get_moon_position` is referenced to the equinox-of-date (tropical) per the Meeus theory in `orbital.py:490-562`** — the perturbation terms drive against the mean ecliptic, which precesses with Earth.
- **Seed formula:** Find the smallest non-negative `n` such that `t_seed = target_jd + n * 27.321582` brackets a return:
  ```python
  natal_moon_lon = calc_planet_position(natal_jd, 1)[0]
  for n in range(0, 2):  # first or second cycle from target_jd
      t_seed = target_jd + n * 27.321582
      t_lo, t_hi = t_seed - 1.5, t_seed + 1.5
      r_lo = _signed_residual(calc_planet_position(t_lo, 1)[0], natal_moon_lon)
      r_hi = _signed_residual(calc_planet_position(t_hi, 1)[0], natal_moon_lon)
      if r_lo * r_hi < 0:
          break
  else:
      raise ValueError("No lunar return in [target_jd, target_jd + 2 * 27.32]")
  ```
- **Bracket half-width:** `half_window_days = 1.5` d. Moon moves on average 13.176°/d but with anomalistic variation ±15%. Average displacement over 1.5 d ≈ 20°; minimum ≈ 17°; maximum ≈ 23°. The bracket is comfortably wide.
- **First-return ≥ target_jd contract.** This is the **most delicate part of the lunar API.** LRET-01 specifies "first lunar return ≥ `target_jd`". Pitfall: if `target_jd` is **exactly at** a lunar return moment, the contract is ambiguous (do we return `target_jd`, or the next return ~27.32 d later?). **Recommendation: return `target_jd` itself if the residual at `target_jd` is already within `tol_deg`** — i.e. treat `target_jd` as inclusive. Pin this with an explicit test (`target_jd == known_return_jd → return ≈ target_jd ± tol_days`).

**Edge case: lunar return falls on the calendar day AFTER `target_jd`.** Per LRET-04 the oracle set must include one such case. Mechanically this is no different from the standard case — the bisection lands on `target_jd + δ` where 0 < δ < 27.32. The test asserts that the resolved JD is **after** `target_jd` AND within the first ~27.32 d. Pin a fixture where `target_jd` is set to 23:00 UT and the resolved return is 02:00 UT the next calendar day.

### Confirming the bracket math

Both seeds + bracket widths are validated by:
- Sun: tropical year is constant to ~0.001 d/yr; 100-year drift ~0.1 d, well inside ±36 h.
- Moon: tropical month is constant to ~10 ms (sub-second) over centuries; 100-year drift << 1.5 d.

**Confidence:** HIGH on the periods (Wikipedia + NASA cite tropical month = 27.321582 d, tropical year = 365.24219 d; both stable over historical spans).

---

## `is_day_chart` and `compute_chart` Reuse

### Compute_chart is fully generic

Confirmed via reading [`ketu/charts/api.py:193-357`](../../../ketu/charts/api.py): the function takes `(jd, lat, lon, system, aspects, polar_fallback)`, broadcasts them, computes houses + bodies + aspects, and assembles a `CHART_DTYPE`. **The word "natal" only appears in docstrings, not in the math.** Phase 18 returns are CHART_DTYPE, so:

```python
def solar_return(natal_jd, natal_lat, natal_lon, target_year,
                 return_lat=None, return_lon=None, system="placidus"):
    # 1. Get natal Sun longitude
    natal_sun_lon = float(calc_planet_position(natal_jd, 0)[0])

    # 2. Seed JD from target_year
    natal_year = julian_to_utc(natal_jd).year
    t_seed = natal_jd + (target_year - natal_year) * 365.2422

    # 3. Bisect
    jd_return = _solve_return(0, natal_sun_lon, t_seed, 1.5)

    # 4. Resolve houses location (relocation contract)
    chart_lat = natal_lat if return_lat is None else return_lat
    chart_lon = natal_lon if return_lon is None else return_lon

    # 5. Assemble CHART_DTYPE via compute_chart with polar-safe fallback
    return compute_chart(jd_return, chart_lat, chart_lon,
                         system=system, polar_fallback="porphyry")
```

~10 lines for `solar_return`; lunar is structurally identical, just `body_id=1` and the seed strategy from §Bracket Strategy.

### `is_day_chart` — out of scope for Phase 18

`is_day_chart` is a **standalone helper** (D-12, see `ketu/charts/api.py:360-505`), NOT a `CHART_DTYPE` field. It takes `(jd, lat, lon)` and answers "is the Sun above the horizon?" — completely generic, no "natal" semantics. Phase 18 returns CAN be passed to `is_day_chart` if a caller wants sect — but Phase 18 owes no contract about it (RET-01..05 / LRET-01..05 don't mention sect). Phase 19 (Arabic Parts) is the consumer that will need `is_day_chart` on returns. **Confirmation that Phase 14's `is_day_chart` is clean: it derives ASC from `compute_ascmc(jd, lat, lon)` per line 479 and Sun from `calc_planet_position_batch(jd, 0)` per line 485 — no hidden natal-context assumption anywhere.**

### Polar relocation

Phase 18's relocation contract means users CAN pass extreme latitudes for `return_lat`. Placidus fails near the polar circle (HighLatitudeError, per `ketu/houses/calculate_houses`). **The escape hatch is `system="whole_sign"`, `system="equal"`, or `system="regiomontanus"`** (Phase 15 deliveries). **Recommendation: hard-wire `polar_fallback="porphyry"` in `solar_return` / `lunar_return`'s `compute_chart` call** so even Placidus relocations to Tromso don't raise — Porphyry cusps substitute for polar elements only, the rest of the chart works. Document this in the docstring: "Polar relocation safety: the return chart is computed with `polar_fallback='porphyry'` so extreme `return_lat` values do not raise. Use `system='whole_sign'` or `system='equal'` if you want non-Porphyry cusps at high latitudes."

**Confidence:** HIGH (Phase 14 verified `compute_chart` is generic; Phase 15 added the polar-friendly systems).

---

## Module Layout

**Recommendation:** `ketu/returns/` as a new top-level subpackage. Justification:

| Reason | Detail |
|--------|--------|
| **Synastry/composite precedent** | Phases 16 & 17 established the subpackage pattern (`api.py` + `core.py` + `__init__.py`). Phase 18 mirrors this with a `_solve.py` private module for the shared helper — small structural addition, big legibility win (the helper "lives between" solar and lunar). |
| **Shared `_solve_return` factorisation is locked in success criteria #3** | Putting the helper at `ketu/returns/_solve.py` makes it discoverable from both `ketu/returns/solar.py` and `ketu/returns/lunar.py`. A flat `ketu/returns.py` would still work but coupling the two public functions in one file makes the shared-helper relationship less obvious. |
| **Future Saturn/Jupiter returns (v1.3)** | If demand surfaces, `ketu/returns/saturn.py` is a 10-line addition (different body_id, longer period for the seed). The subpackage layout future-proofs this without re-organising. |
| **Coverage gate scoping** | `make returns-coverage` with `--include='ketu/returns/*'` cleanly catches the whole subpackage. A flat `ketu/returns.py` would still work but the subpackage matches the synastry/composite Makefile recipe verbatim. |

```
ketu/returns/
├── __init__.py       # Re-export solar_return, lunar_return
├── _solve.py         # Private: _solve_return + _signed_residual_deg + _TOL_DEG / _TOL_DAYS / _TROPICAL_YEAR_D / _TROPICAL_MONTH_D
├── solar.py          # solar_return public API
└── lunar.py          # lunar_return public API
```

**Alternative (rejected):** `ketu/returns.py` single module. Pros: simpler import; one file to read. Cons: mixes three concerns (solar, lunar, helper), making the shared-helper relationship invisible from the file tree. Also no precedent in Ketu since Phase 14 — every v1.2 phase has used the subpackage pattern. **Not recommended.**

**`pyproject.toml`:** Add `"ketu.returns"` to `[tool.setuptools].packages` (line 61).

**Confidence:** HIGH (direct synastry/composite precedent; future-proof for v1.3 returns extensions).

---

## Public API Surface

### `solar_return` signature (RET-01 verbatim)

```python
def solar_return(
    natal_jd: float,
    natal_lat: float,
    natal_lon: float,
    target_year: int,
    return_lat: float | None = None,
    return_lon: float | None = None,
    system: str = "placidus",
) -> np.ndarray:  # scalar CHART_DTYPE
    """Compute the solar return chart for a given natal birth and target year.
    ...
    """
```

### `lunar_return` signature (LRET-01 verbatim)

```python
def lunar_return(
    natal_jd: float,
    natal_lat: float,
    natal_lon: float,
    target_jd: float,
    return_lat: float | None = None,
    return_lon: float | None = None,
    system: str = "placidus",
) -> np.ndarray:  # scalar CHART_DTYPE
    """Compute the lunar return chart for a given natal birth and target JD.

    Returns the FIRST lunar return moment >= target_jd (~27.32 d periodicity).
    ...
    """
```

### Docstring guard clauses (LOUD, per RET-05 / LRET-05)

Both docstrings MUST contain a `Notes` block with:

```
**`natal_lat/lon` vs `return_lat/lon` — distinguish loudly.**
- ``natal_lat/lon`` are NEVER used for the bisection: they are kept on
  the signature for symmetry/future-proofing only (Phase 18's bisection
  reads natal Sun/Moon longitude from ``natal_jd`` alone — Sun and Moon
  geocentric longitudes are location-independent).
- ``return_lat/lon`` ARE used: they set the houses, ASC, MC, ARMC, Vertex
  of the return chart via ``compute_chart(jd_return, return_lat,
  return_lon, system)``. Passing ``return_lat=None`` (default) reuses
  ``natal_lat``; ``return_lon=None`` (default) reuses ``natal_lon``.
  This is the "standard return" case; passing non-None values is
  "relocated return".

**UTC-only contract — LOUD.** ``natal_jd`` (and ``target_jd`` for lunar)
MUST be UTC Julian Dates. Timezone conversion is the caller's
responsibility.

**Polar relocation safety.** ``compute_chart`` is called with
``polar_fallback='porphyry'``, so extreme ``return_lat`` (Tromso, polar
expeditions) do not raise. Use ``system='whole_sign'`` or
``system='equal'`` for non-Porphyry cusps at high latitudes.

**Convention.** Ketu uses TRUE geocentric Sun/Moon longitude (no aberration
correction on body_ids 0/1, see ``ketu/ephemeris/planets.py:190``).
Astro.com uses APPARENT longitudes (~20.5 arcsec aberration for Sun).
The two conventions cancel in the natal-to-return resolution (both
sides use the same convention), so the resolved instant agrees with
Astro.com to sub-second; cross-tool deltas on individual body
longitudes in the return chart are within ~20 arcsec for Sun, sub-
arcsec for Moon.
```

### Lunar-specific guard (LRET-05)

```
**``target_jd`` is an INSTANT, NOT a year.** Unlike ``solar_return``
which takes an integer ``target_year``, ``lunar_return`` takes a
Julian Date ``target_jd`` and returns the FIRST lunar return moment
>= ``target_jd``. This API asymmetry is deliberate: solar returns
are calendar-anchored (one per birthday-year); lunar returns are
~27.32 d-periodic so the user must specify which instant the search
starts from.
```

**Confidence:** HIGH (signatures from spec verbatim; docstring guard clauses are precedent-aligned with composite Notes blocks).

---

## Astro.com Oracle Strategy

### Constraint: Astro.com is bot-blocked

Confirmed in this research session (the FAQ page `https://www.astro.com/faq/fq_fh_return_j.htm` returns a browser-check stub via WebFetch). Same constraint Phase 16 (synastry) and Phase 17 (composite) hit.

### Three viable paths

| Approach | Pros | Cons |
|----------|------|------|
| **1. Self-consistency only** | Zero external dependency; reproducible CI; pins the function against its own output | Doesn't validate against an external reference |
| **2. Self-consistency PRIMARY + manual Astro.com cross-check DEFERRED** | (1) + a one-time human-validated cross-check note; matches synastry/composite precedent | Astro.com numbers pinned manually post-hoc |
| **3. Astro.com FIRST oracle** | True cross-tool validation up-front | Requires manual capture before implementation; not achievable in this research session |

**Recommendation:** **Approach 2** (matches Phase 17 close-out and Phase 16 Plan 16-05 deferred follow-up). Self-consistency is the **primary gate** at machine precision (`tolerance_deg=0.0001`); the Astro.com cross-check is a **deferred follow-up note** captured in the close-out plan's SUMMARY (mirroring `17-04-SUMMARY.md`'s "Astro.com Manual Cross-Check" section).

### Free reference tools (alternatives to Astro.com)

The spec says "vs Astro.com" but, given Astro.com's anti-bot stance, the planner should consider whether other **free, accessible** references exist:

| Tool | Free? | Solar Return? | Lunar Return? | Bot-blocking? | Accuracy |
|------|-------|---------------|----------------|---------------|----------|
| **Swiss Ephemeris CLI (`swetest`)** | YES (under AGPL — test-only OK) | Indirectly (you'd have to bisect manually on `swetest` Sun-longitude output) | Same | None | Sub-arcsecond |
| **Astro-Seek solar/lunar return calculator** | YES | YES | YES | UNKNOWN (worth a WebFetch attempt) | ~Astro.com level (also Swiss Ephemeris-based) |
| **AstroChart, AskNova, AstroMatrix, Astrotheme** | YES (web) | YES | Varies | Mostly UI-only; manual capture | Varies; secondary references |
| **Solar Fire (Esoteric Technologies)** | PAID; explicit user-stated "no paid tools" | — | — | — | — |

**Recommendation:** Use **Astro-Seek** ([horoscopes.astro-seek.com/solar-return-chart](https://horoscopes.astro-seek.com/solar-return-chart)) as the secondary manual reference if Astro.com cross-check is contested. Astro-Seek uses Swiss Ephemeris (Astrodienst's own algorithm), so agreement with Astro.com should be sub-second. Worth a WebFetch verification of bot-blocking status as a Plan 18-04 task.

**`pysweph` (already a test-only dependency at `pyproject.toml:43`)** can also compute solar/lunar returns programmatically via `swisseph.solar_return` (sub-arcsec accuracy, AGPL but test-only is fine, see Phase 14 swisseph oracle precedent at `tests/charts/conftest.py`). **Strong recommendation: use `pysweph` as the primary CI-runnable oracle**, with manual Astro.com cross-check deferred to a follow-up note. This gives the project a deterministic, reproducible, sub-arcsecond cross-tool validation without any manual UI steps.

Actually — checking: pyswisseph DOES have built-in solar return functions:
- `swisseph.solar_return(natal_jd, natal_lon_sun, jd_start, flags)` → next solar return JD
- `swisseph.next_lunar_return(...)` — name varies by binding version

Worth verifying via the pyswisseph docs in a Plan 18-04 task. If present, this is the **right oracle**: self-consistency + pyswisseph cross-tool + deferred Astro.com manual. If not present (older binding), bisect on `swisseph.calc_ut(jd, swe.SUN | swe.MOON)[0][0]` manually inside the test (~5 lines).

### Recommended oracle fixtures (3 solar + 3 lunar)

**Reuse synastry/composite birth records** to minimise new fixture data. Each fixture pins:
- Natal birth data (already in `tests/synastry/fixtures/oracle_*.json`)
- `target_year` (solar) or `target_jd` (lunar)
- Expected return JD (resolved via self-consistency + cross-validated against pyswisseph)
- Expected CHART_DTYPE bodies (per-body longitudes from `compute_chart` at the resolved JD)
- `tolerance_deg=0.0001` self-consistency gate
- `cross_check_tolerance_deg=0.001` (3.6 arcsec) for pyswisseph cross-check

**Solar fixtures:**

| Fixture name | Natal | target_year | Wrap-around? | Notes |
|--------------|-------|-------------|--------------|-------|
| `solar_diana_1980` | Diana (1961-07-01) | 1980 | NO | Standard; Diana's natal Sun ~9° Cancer, far from seam |
| `solar_curie_1900` | Marie Curie (1867-11-07) | 1900 | NO | Standard; long projection (33 years) |
| `solar_aries_seam_1970` | Synthetic natal Sun ~0.5° Aries (March 21 ~14:00 UT) | 1970 | **YES** | Wrap-around case; tests the 360°→0° residual seam |

**Lunar fixtures:**

| Fixture name | Natal | target_jd | Wrap-around? | Day-after? | Notes |
|--------------|-------|-----------|--------------|------------|-------|
| `lunar_diana_2000-01-01` | Diana | 2000-01-01T12:00 UT | NO | NO | Standard |
| `lunar_curie_1900-06-15` | Marie Curie | 1900-06-15T00:00 UT | NO | **YES** | Pin `target_jd = 23:00 UT` of a day BEFORE the actual return, force the resolved JD onto the calendar day AFTER (`target_jd + ~26 h`) |
| `lunar_pisces_seam_1990` | Synthetic natal Moon ~0.2° Aries | 1990-01-01 | **YES** | NO | Wrap-around case |

**Confidence:** HIGH on the test infrastructure (synastry/composite precedent is clean); MEDIUM on pyswisseph's solar_return API (need to verify exact binding signature in Plan 18-04).

---

## Test Layout

Mirror `tests/synastry/` and `tests/composite/` exactly:

```
tests/returns/
├── __init__.py
├── conftest.py                                # Session-scoped natal fixtures (reuse synastry birth data)
├── fixtures/
│   ├── oracle_solar_diana_1980.json
│   ├── oracle_solar_curie_1900.json
│   ├── oracle_solar_aries_seam_1970.json      # Wrap-around oracle
│   ├── oracle_lunar_diana_2000.json
│   ├── oracle_lunar_curie_day_after.json      # Day-after-target_jd oracle
│   └── oracle_lunar_pisces_seam_1990.json     # Wrap-around oracle
├── test_solve_return.py                       # Pure-NumPy bisection unit tests; wrap-around suite; convergence count
├── test_solar_return.py                       # RET-01..05 surface tests; relocation; leap-year; bracket bounds
├── test_lunar_return.py                       # LRET-01..05 surface tests; first-return-≥-target_jd contract; relocation
├── test_returns_oracle.py                     # 3 solar + 3 lunar oracle fixtures (self-consistency PRIMARY)
└── test_returns_coverage_gate.py              # Sentinel for the returns_coverage_gate marker
```

**Session-scoped fixtures.** Reuse the same six `compute_chart(...)` calls used in `tests/synastry/conftest.py` and `tests/composite/conftest.py` (Diana, Charles, Marie Curie, Pierre Curie, Lennon, Ono). **Recommendation: duplicate rather than `pytest_plugins`-import**, matching Phase 17's choice for self-containment.

**Confidence:** HIGH (synastry+composite precedent).

---

## Coverage Gate

Mirror `composite-coverage` / `synastry-coverage` verbatim.

### `pyproject.toml` line 77–83 — add `returns_coverage_gate` alphabetically

```toml
markers = [
    "slow: ...",
    "charts_coverage_gate: ...",
    "composite_coverage_gate: ...",
    "houses_coverage_gate: ...",
    "returns_coverage_gate: RET-06 95% coverage gate for ketu.returns (run via Makefile target `make returns-coverage`)",
    "synastry_coverage_gate: ...",
]
```

### `Makefile` line ~80 — add `returns-coverage` target

```makefile
## returns-coverage: Run the RET-06 ≥95% coverage gate scoped to ketu.returns.
##
## Mirror of `composite-coverage` (COMP-05). Same two-step pattern to
## avoid the NumPy `_NoValueType` reload bug...
returns-coverage:
	$(PYTHON) -m pytest tests/returns/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/returns/*' --fail-under=95 -m
```

Add `returns-coverage` to the `.PHONY` line (line 11).

### `REQUIREMENTS.md` — add new RET-06 (parallel to COMP-05 / SYN-05 / CHART-05 / HOU-09)

```markdown
- [ ] **RET-06** : ≥95% line coverage gate on `ketu/returns/` via `make returns-coverage` target + `returns_coverage_gate` pytest marker (close-out addition; mirror of COMP-05 / SYN-05 / CHART-05 / HOU-09).
```

**Recommendation: land in close-out plan (Plan 18-05).** Phase 17's `composite_coverage_gate` was created late (Plan 17-04) but Phase 17's RESEARCH recommended landing it earlier. Phase 18 should follow the **research recommendation** (which Phase 17 did honor in spirit) and **bake the marker into the foundation plan (Plan 18-01)** so coverage is monitored throughout implementation. The Makefile target can land in Plan 18-01 as well — it's a 6-line addition.

**Confidence:** HIGH (synastry/composite precedent; zero-novelty addition).

---

## Plan Decomposition (5 Plans Recommended)

| Plan | Title | Wave | Owns | Rationale |
|------|-------|------|------|-----------|
| **18-01** | Foundation: `ketu/returns/` skeleton + `_solve_return` helper + wrap-around regression suite + coverage-gate marker registration | 1 | `ketu/returns/__init__.py`, `ketu/returns/_solve.py`, `tests/returns/__init__.py`, `tests/returns/test_solve_return.py`, `pyproject.toml` (packages + markers + Makefile target), `Makefile` (returns-coverage), `tests/returns/test_returns_coverage_gate.py` | The helper is the **architectural heart** of Phase 18 (success criterion #3). Pin wrap-around regression suite BEFORE either public API exists — same pattern as Phase 17 Plan 17-01 pinning `circular_midpoint`'s wrap-around BEFORE `calculate_composite`. Registering the coverage-gate marker + Makefile target early lets coverage be monitored from Plan 18-02 onwards. |
| **18-02** | Solar API: `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat, return_lon, system) → CHART_DTYPE` with RET-01..03/05 ratchets (relocation, leap-year, polar) | 2 | `ketu/returns/solar.py`, `tests/returns/test_solar_return.py`, `ketu/returns/__init__.py` (extend re-exports) | Solar is the simpler of the two (monotonic, no first-return contract). Land it first as the "shake-down" for the shared helper. Test relocation contract, leap-year edge case (Feb 29 natal), and polar relocation (Tromso). |
| **18-03** | Lunar API: `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat, return_lon, system) → CHART_DTYPE` with LRET-01..03/05 ratchets (first-return ≥ target_jd, asymmetric API, relocation) | 2 (parallel with 18-02 in theory; sequential in practice — depends on `_solve_return` from 18-01 only, same as 18-02) | `ketu/returns/lunar.py`, `tests/returns/test_lunar_return.py`, `ketu/returns/__init__.py` (extend re-exports) | Lunar is structurally identical to solar but has the **first-return ≥ target_jd** contract that needs explicit testing (LRET-04 day-after-target case). Land after solar so any helper-tuning learnings from Plan 18-02 are folded in. |
| **18-04** | Oracle fixtures: 3 solar + 3 lunar (each set incl. one wrap-around case; lunar incl. one day-after-target case); self-consistency PRIMARY oracle at `tolerance_deg=0.0001`; pyswisseph cross-check (SEC sub-arcsec); Astro.com manual cross-check deferred | 3 | `tests/returns/fixtures/oracle_*.json` (6 files), `tests/returns/test_returns_oracle.py`, optionally `tests/returns/conftest.py` (session-scoped fixtures) | RET-04 + LRET-04 binding. Mirror Phase 17 Plan 17-03 (oracle fixture generation) and the Phase 17 Plan 17-04 deferred-Astro.com note. Add pyswisseph cross-check as a new addition — gives a CI-runnable sub-arcsec external reference. Verify pyswisseph's `solar_return` / lunar-return binding in this plan. |
| **18-05** | Close-out: `make returns-coverage` ≥95% gate verification + `returns_coverage_gate` sentinel + See Also cross-refs (returns ↔ charts ↔ composite ↔ synastry) + CHANGELOG `[Unreleased]` entry citing RET-01..06 + LRET-01..05 + REQUIREMENTS status flips + 6-criteria smoke + Astro.com manual cross-check deferred note in SUMMARY | 4 (sequential, last) | `CHANGELOG.md`, `.planning/REQUIREMENTS.md`, `.planning/phases/18-solar-lunar-returns/18-05-SUMMARY.md` (with deferred Astro.com follow-up), See Also docstring additions in `ketu/charts/`, `ketu/composite/`, `ketu/synastry/` | The canonical Phase-N close-out — near-verbatim copy of Plan 17-04 with COMP→RET substitutions and the addition of LRET-XX flips. 6-criteria smoke is the gating verification for `/gsd:verify-phase 18`. |

### Why 5 plans, not 3 or 7?

- **3 plans** would conflate concerns: foundation+solar in one plan = too big, fixtures+close-out in one = mixes oracle generation with CHANGELOG/REQUIREMENTS bookkeeping.
- **7 plans** would slice too finely: e.g. splitting `_solve_return` from coverage-gate marker registration adds two PR / plan boundaries with no clear cohesion benefit.
- **5 plans** matches Phase 16 (synastry, 5 plans) and is one more than Phase 17 (composite, 4 plans) — the extra plan is the explicit oracle-generation plan (which Phase 17 collapsed into 17-03 since the composite oracle was simpler than 6 fixtures). Phase 18's 6 oracle fixtures + pyswisseph cross-check + Astro.com manual deferral note deserve their own plan.

### Parallelisation analysis

Plans 18-02 (solar) and 18-03 (lunar) are **theoretically parallelisable** (they depend only on Plan 18-01's `_solve_return`), but in practice they should be **sequential**: any helper-tuning learnings from solar (e.g. adjusting `tol_days` floor) should fold into lunar. Recommendation: keep them in waves 2 and 3 of the same plan sequence, NOT parallel.

**Confidence:** HIGH (decomposition mirrors Phase 16/17; 5 plans is the natural slicing for the locked scope).

---

## Pitfalls to Flag for Planning

### Pitfall 1 (HIGH × HIGH): Sign error in wrap-around residual

**What goes wrong:** Naive `body_lon(t) - natal_lon_ref` is in `[-360, +360]` and the bisection sign-check `r_lo * r_hi < 0` fires falsely or fails to fire when the natal longitude is near the 0°/360° seam.

**How to avoid:** Centralise the residual computation behind `_signed_residual_deg(lon, ref) = ((lon - ref + 540) % 360) - 180`. Test it on `(lon=0.05, ref=359.95) → -0.1` (correct short-arc signed delta), NOT `-359.9`. Pin the 0°/360° seam in `tests/returns/test_solve_return.py::test_signed_residual_wrap_around` parametrized over the seam in both directions.

**Warning signs:** Bisection convergence count >>30 for either body; resolved JD several days off from the expected return; "no zero in bracket" errors for natal Sun/Moon near 0°.

### Pitfall 2 (HIGH × HIGH): Lunar first-return-≥-target_jd contract violation

**What goes wrong:** A future contributor implementing `lunar_return` seeds the bisection at `target_jd + 27.32/2` instead of `target_jd`. The resolved JD might fall BEFORE `target_jd`, violating LRET-01's "first lunar return ≥ `target_jd`" contract.

**How to avoid:** Explicit ratchet test `test_lunar_return_resolves_at_or_after_target_jd` parametrised over multiple natal-Moon longitudes. Assert `jd_return >= target_jd - tol_days`. **Stronger ratchet:** include the day-after-target oracle (`oracle_lunar_curie_day_after.json`) where `target_jd = 23:00 UT day N` and the resolved JD is `02:00 UT day N+1` — visually obvious in the fixture.

**Warning signs:** Lunar return tests pass for "easy" cases but fail when `target_jd` happens to be near a return moment; CI flakes near month boundaries.

### Pitfall 3 (MEDIUM × HIGH): Confusing `natal_lat/lon` with `return_lat/lon`

**What goes wrong:** Phase 18's API has TWO geographic coordinates: `natal_lat/lon` (for the natal birth — the natal Sun/Moon longitude reference) and `return_lat/lon` (for the return chart's houses). For Sun/Moon longitudes these are LOCATION-INDEPENDENT (geocentric), so `natal_lat/lon` is mathematically irrelevant — but the signature keeps it for symmetry. A confused user might pass `return_lat=natal_lat` (no-op, same as default) thinking they're doing relocation; or might pass natal coordinates as `return_lat/lon` thinking it locks in the natal house calculation.

**How to avoid:**
- Loud docstring guard (see §Public API Surface).
- Sentinel test `test_natal_lat_lon_does_not_affect_resolved_jd` — call `solar_return(natal_jd=X, natal_lat=A, ...)` and `solar_return(natal_jd=X, natal_lat=B, ...)` with same X and different A vs B; assert the resolved JD is identical to <1 arcsec.
- Sentinel test `test_relocation_changes_houses_not_bodies` — same natal, different `return_lat/lon`; assert `body_lons` identical, `asc/mc/cusps` different.

**Warning signs:** User reports "I changed `natal_lat` and the return came out the same" — that's CORRECT behaviour but indicates docstring is unclear.

### Pitfall 4 (MEDIUM × MEDIUM): Sun aberration mismatch with Astro.com

**What goes wrong:** Ketu uses TRUE geocentric Sun (no aberration); Astro.com uses APPARENT. The ~20 arcsec aberration cancels in the natal-to-return resolved-instant calculation (both sides use the same convention), BUT individual body longitudes in the resolved return chart will differ from Astro.com by ~20 arcsec for Sun. A user comparing the return Sun longitude to Astro.com's may see a ~20 arcsec delta and conclude "Ketu is broken".

**How to avoid:**
- Loud docstring guard ("Convention" Notes block).
- Astro.com manual cross-check note in SUMMARY documents the expected ~20 arcsec systematic offset.
- Oracle tolerance ≥1 arcsec for Sun longitude in cross-Astro fixtures (not 0.0001 arcsec — that's only for self-consistency).

**Warning signs:** Sun longitude appears slightly off from Astro.com in user reports.

### Pitfall 5 (MEDIUM × MEDIUM): Polar relocation raising HighLatitudeError

**What goes wrong:** Default `compute_chart(..., polar_fallback="raise")` raises on `return_lat > 66.56°`. A user computing a relocated return to a polar latitude gets an unexpected exception instead of a chart.

**How to avoid:** Hard-wire `polar_fallback="porphyry"` in both `solar_return` and `lunar_return`'s internal `compute_chart` call. Document in docstring "Polar relocation safety" Notes block (see §Public API Surface). Pin a `test_polar_relocation_does_not_raise` test (Tromso at lat=69.65).

**Warning signs:** User reports "I got HighLatitudeError on a relocated return chart."

### Pitfall 6 (LOW × HIGH): Leap-year Feb 29 natal

**What goes wrong:** Feb 29 natal + non-leap target year → calendar birthday "doesn't exist". A naive implementation might off-by-one-day or raise on `datetime(target_year, 2, 29)`.

**How to avoid:** **The math is location-independent of calendar dates.** The seed is `natal_jd + (target_year - natal_year) * 365.2422` — a tropical-year offset that's well-defined for every natal date including Feb 29. The bisection finds the moment when Sun longitude equals natal Sun longitude in `target_year`; this moment is well-defined regardless of calendar oddities (it'll fall in late Feb / early March of non-leap target years). Pin a `test_feb_29_natal` test with a Feb 29 natal date and `target_year=2001` (non-leap); assert convergence + assert `2001-02-28 < julian_to_utc(jd_return) < 2001-03-02`.

**Warning signs:** Tests skipped or special-cased for Feb 29; raise on `datetime(target_year, 2, 29)`.

### Pitfall 7 (LOW × LOW): Sun or Moon retrograde (geocentric)

**What goes wrong:** A contributor worries that retrograde motion could cause the bisection's monotonicity assumption to fail.

**How to avoid:** Document explicitly in `_solve.py` docstring: **Geocentric Sun is NEVER retrograde. Geocentric Moon is NEVER retrograde.** Apparent retrograde motion is a phenomenon of geocentric Mercury/Venus/Mars/.../Pluto only — not of the Sun or Moon. So the residual `body_lon(t) - natal_lon_ref` (after wrap-around lift) is **strictly monotonically increasing** over the bisection bracket for both Sun and Moon, guaranteeing bisection convergence in `log2(bracket_width / tol)` iterations. **No retrograde safety net needed for Phase 18.** (Saturn/Jupiter returns in v1.3 WILL need to think about retrograde — but that's a v1.3 concern.)

**Warning signs:** A contributor adding a "retrograde check" to `_solve_return` — reject in review.

### Pitfall 8 (LOW × LOW): Anomalistic Moon perigee/apogee curvature

**What goes wrong:** Moon's longitude rate varies ±15% across one month due to anomalistic motion (perigee → fast, apogee → slow). A contributor worries this might cause Newton or secant fragility.

**How to avoid:** **Bisection is indifferent to curvature.** The Moon's velocity is always positive (no retrograde, see Pitfall 7), so the residual is monotonic and bisection always converges. Newton/secant WOULD be sensitive to inflection points — but we're not using them. Document in `_solve.py` docstring: "Bisection chosen over Newton/secant specifically because it's curvature-indifferent; Moon's parallactic+anomalistic perturbations cause d²θ/dt² inflections within a month, which would degrade Newton's quadratic convergence."

**Warning signs:** None expected with bisection.

---

## Open Questions for Planning

### Q1 — Bracket extension on failure

**Question:** If `_solve_return`'s initial ±36 h (Sun) or ±1.5 d (Moon) bracket does NOT contain a sign change, should it raise `ValueError` or auto-extend the bracket?

**What we know:** With correct seed selection (§Bracket Strategy), the bracket WILL contain the sign change for every realistic input. The "no sign change" branch should never fire in practice.

**What's unclear:** Defensive handling for edge cases (`target_year` corresponding to a year >100 years from natal, where tropical-year drift might exceed 36 h; `target_jd` with `n=2` cycles still not bracketing for some pathological natal Moon longitude).

**Recommendation:** **Raise `ValueError`** with a clear message ("No solar return in bracket [t_lo, t_hi]; check target_year"). Auto-extend would mask seed-selection bugs. If real-user reports surface bracket failures, address with a Plan 18-04 fix.

### Q2 — `pysweph` API for solar/lunar return

**Question:** Does `pyswisseph >= 2.10.3.6` (the test-only dep at `pyproject.toml:43`) expose `swisseph.solar_return` or similar built-in return functions? Or do we have to manually bisect on `swisseph.calc_ut(jd, swe.SUN)` inside the test?

**What we know:** Both forms exist in some Swiss Ephemeris bindings; exact pyswisseph 2.10.3.x API is not yet verified.

**Recommendation:** **Verify in Plan 18-04** (the oracle plan). If `swisseph.solar_return` exists, use it as the cross-check oracle (~3 lines per fixture). If not, write a small `_swisseph_solar_return(natal_jd, target_year)` helper in `tests/returns/conftest.py` that manually bisects on `swisseph.calc_ut(jd, swe.SUN)[0][0]` — same algorithm as `_solve_return` but using Swiss Ephemeris instead of Ketu's NumPy ephemeris. ~10 lines.

### Q3 — Vectorised public API in v1.2?

**Question:** Should `solar_return` / `lunar_return` accept arrays of `target_year` / `target_jd` and broadcast?

**What we know:** The shared `_solve_return` helper CAN be written to support vectorised inputs (NumPy-native bisection over arrays is straightforward). The public API spec (RET-01 / LRET-01) is scalar-only.

**Recommendation:** **Phase 18 ships scalar public API only.** Write the helper to support vectorised inputs as a no-cost future-proofing (the bisection loop body is identical for scalars and arrays in NumPy). Plan 18-01's helper signature accepts `t_seed: float` for v1.2; a v1.3 follow-up can lift to `np.ndarray` with a one-line dtype broadcast.

### Q4 — Astro-Seek bot-blocking status

**Question:** Is `horoscopes.astro-seek.com/solar-return-chart` bot-blocked from WebFetch like Astro.com?

**What we know:** Astro-Seek uses Swiss Ephemeris (same algorithm as Astro.com), so it's a valid secondary reference. WebFetch bot-blocking status untested in this research session.

**Recommendation:** **Verify in Plan 18-04** with a single WebFetch attempt. If accessible, use as the secondary manual reference for the deferred Astro.com cross-check. If bot-blocked, the deferral note simply says "deferred — Astro.com and Astro-Seek both bot-blocked; pyswisseph cross-check is the CI-runnable substitute" (still strictly better than Phase 17 which had only Astro.com deferred without a CI-runnable substitute).

### Q5 — Polar relocation: hard-wire `polar_fallback="porphyry"` or expose?

**Question:** Should `solar_return` / `lunar_return` hard-wire `polar_fallback="porphyry"` (recommended) or expose the kwarg?

**What we know:** Exposing the kwarg gives users escape-hatch flexibility; hard-wiring removes a footgun (default `polar_fallback="raise"` would surprise users computing relocated returns to polar latitudes).

**Recommendation:** **Hard-wire `polar_fallback="porphyry"` in Phase 18.** Document the choice in Notes. If a user genuinely wants `raise` behaviour, they can compute the return JD manually via the (private) `_solve_return` and call `compute_chart(jd_return, ..., polar_fallback="raise")` directly. v1.3 can add an explicit `polar_fallback=` kwarg if demand surfaces.

---

## State of the Art

| Old approach (pre-Ketu / pre-v1.0 hypothetical) | Current Ketu approach | Why we differ |
|--------------------------------------------------|------------------------|---------------|
| `scipy.optimize.brentq` | Hand-rolled pure-NumPy bisection | Pure-NumPy contract (CLAUDE.md / PROJECT.md). Brent is overkill for Sun/Moon (~30 → ~10 iterations saves ~20 µs per return at v1.2 call frequencies). |
| Single function with both Sun and Moon inline | Shared `_solve_return(body_id, natal_lon_ref, ...)` helper called by both `solar_return` and `lunar_return` | LRET-02 + ROADMAP success criterion #3 mandate the factorisation. Also cleaner for future Saturn/Jupiter returns. |
| `(a + b) / 2 % 360` naive midpoint | `((Δ + 540) % 360) - 180` signed-short-arc residual | Ketu convention (composite/core.py, houses/porphyry.py). Wrap-around correctness pinned by regression. |
| Apparent geocentric Sun (Astro.com / Swiss Ephemeris default) | True geocentric Sun (Ketu's no-aberration-for-Sun choice, `planets.py:190`) | Existing Ketu convention. The ~20 arcsec aberration cancels in natal-to-return resolution (same-convention-both-sides). Documented in `solar_return` Notes block. |
| Sidereal year (365.25636 d) | Tropical year (365.24219 d) | Natal Sun longitude is in the tropical zodiac; the seed offset must use the same convention. |
| Sidereal month (27.32166 d) or anomalistic month (27.55455 d) | Tropical month (27.32158 d) | Same logic: Ketu's Moon longitude via `get_moon_position` is tropical (equinox of date). |

---

## Sources

### Primary (HIGH confidence)

- [`ketu/charts/api.py`](../../../ketu/charts/api.py) — `compute_chart`, `is_day_chart` (read source 2026-05-24; confirmed generic, no natal-specific logic)
- [`ketu/charts/core.py`](../../../ketu/charts/core.py) — `CHART_DTYPE` definition (14 fields, frozen body axis)
- [`ketu/ephemeris/planets.py`](../../../ketu/ephemeris/planets.py) — `calc_planet_position`, `calc_planet_position_batch` (read source 2026-05-24; confirmed Sun/Moon longitudes available, vectorised batch form for both, no aberration applied to ids 0/1)
- [`ketu/composite/core.py`](../../../ketu/composite/core.py) line 79-81 — `circular_midpoint` signed-short-arc wrap-around precedent
- [`ketu/houses/porphyry.py`](../../../ketu/houses/porphyry.py) line 159 — second wrap-around precedent
- [`ketu/aspects/core.py`](../../../ketu/aspects/core.py) line 106 — `refine_exact_moment` bisection precedent
- [`ketu/ephemeris/planets.py:273-342`](../../../ketu/ephemeris/planets.py) — `find_exact_aspect` bisection precedent
- [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md) lines 45–57 — RET-01..05 + LRET-01..05 verbatim
- [`.planning/ROADMAP.md`](../../../.planning/ROADMAP.md) lines 175–192 — Phase 18 6-point success criteria (commit 5d90e43)
- [`.planning/phases/17-composite-chart-midpoint-variant/17-RESEARCH.md`](../17-composite-chart-midpoint-variant/17-RESEARCH.md) — stylistic precedent + Astro.com bot-block status

### Secondary (MEDIUM confidence — public references with HIGH consensus)

- [Lunar month (Wikipedia)](https://en.wikipedia.org/wiki/Lunar_month) — tropical month 27.321582 d; sidereal month 27.321661 d; anomalistic month 27.554550 d
- [Orbit of the Moon (Wikipedia)](https://en.wikipedia.org/wiki/Orbit_of_the_Moon) — confirms tropical month as the equinox-of-date period
- [NASA Eclipses and the Moon's Orbit](https://eclipse.gsfc.nasa.gov/SEhelp/moonorbit.html) — secondary corroboration
- [Sidereal year (Wikipedia)](https://en.wikipedia.org/wiki/Sidereal_year) — tropical year 365.24219 d, sidereal 365.25636 d
- [Swiss Ephemeris (Astrodienst)](https://www.astro.com/swisseph/swisseph_acrobat.pdf) — Solar return computation guidance (Astrodienst's own programmer's manual)

### Tertiary (LOW confidence — need verification in Plan 18-04)

- [Astro-Seek Solar Return calculator](https://horoscopes.astro-seek.com/solar-return-chart) — alternative manual reference; bot-blocking status untested
- [AstroChart](https://astrochart.co/solar-return-chart), [AskNova](https://www.asknovaastrology.com/solar-return), [AstroMatrix](https://astromatrix.org/tools/solar-return), [Astrotheme](https://www.astrotheme.com/solar_revolution.php) — secondary references for manual cross-check; bot-blocking status untested
- pyswisseph 2.10.3.x — exact `solar_return` / lunar-return binding signature not verified in this session

### Bot-blocked (confirmed during this research session — same as Phase 17)

- [Astrodienst Returns FAQ](https://www.astro.com/faq/fq_fh_return_j.htm) — returns browser-check stub via WebFetch (consistent with Phase 17's findings about astro.com)

---

## Metadata

**Confidence breakdown:**

- **Existing Sun/Moon longitude API:** HIGH (read the source; confirmed batch form, no aberration on ids 0/1)
- **Root-finding algorithm choice (bisection):** HIGH (pure-NumPy contract is binding; Brent overkill; Newton fragile on Moon curvature)
- **Wrap-around handling (pre-unwrap):** HIGH (Ketu convention reused verbatim; pinned by composite + porphyry precedent)
- **Initial bracket strategy (±36h Sun / ±1.5d Moon):** HIGH (analytic derivation from mean motions; safety margin 6×)
- **Tropical year / tropical month constants:** HIGH (Wikipedia + NASA consensus; stable over historical spans)
- **`compute_chart` reuse for chart assembly:** HIGH (Phase 14 fully verified the function is generic)
- **`is_day_chart` for returns:** HIGH (standalone helper, no natal context; can be called on returns externally if needed)
- **Polar relocation safety (hard-wire porphyry fallback):** HIGH (Phase 14 / 15 verified the fallback path)
- **Subpackage layout (`ketu/returns/` with `_solve.py`):** HIGH (synastry/composite precedent; future-proof for v1.3)
- **Plan decomposition (5 plans):** HIGH (matches Phase 16/17 scale; clean separation)
- **Astro.com oracle strategy (self-consistency PRIMARY + pyswisseph cross-check NEW + Astro.com manual DEFERRED):** MEDIUM (Astro.com bot-blocking re-confirmed; pyswisseph solar_return API needs Plan 18-04 verification)
- **Astro-Seek alternative reference:** LOW (bot-blocking status untested in this session — flagged for Plan 18-04 verification)
- **Aberration cancellation argument (~20 arcsec Sun):** HIGH (same-convention-both-sides math is textbook)

**Research date:** 2026-05-24
**Valid until:** 2026-06-23 (30 days — Ketu is a stable codebase; primary references are textbook astronomy + read-source-code; no fast-moving deps)
