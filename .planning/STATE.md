# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-06)

**Core value:** Cycle calculations must be correct, tested, and performant
**Current focus:** Milestone v1.1 Flexibility & Houses — Phase 10 (Houses Module)

## Current Position

Phase: 10 of 12 (Houses Module) — **IN PROGRESS**
Plan: 3 of 6 complete (10-01 lst-precision-audit — Wave 1; 10-02 oracle-harness-and-fixtures — Wave 2; 10-03 registry-dtype-ascmc — Wave 2)
Status: Wave 2 closing — Plan 10-03 landed the `ketu.houses` subpackage scaffold: `HOUSES_DTYPE` (9 fields incl. `cusps (12,)` subarray, HOU-05), `HighLatitudeError` (ValueError subclass with lat/system/polar_lat attrs), `SYSTEMS` registry + `@register("name")` decorator + case-insensitive `get_system` dispatch (HOU-02), and the closed-form **vectorized** `compute_ascmc(jd, lat, lon) → dict[asc, mc, armc, vertex, eps]` via `np.arctan2` (Pitfall 2 avoided). All 8 non-polar reference charts (consumed via Plan 10-02's `loaded_reference_snapshot` fixture) agree with pyswisseph oracle to **<1 arcmin on ASC/MC/ARMC** (worst case 51.5″ ASC at 2050_Reykjavik, lat 64.1°N) and **<5 arcmin on Vertex** (worst case 15.5″ at J2000_Tokyo). Public API stubs `calculate_houses` / `house_of` raise `NotImplementedError` until Plan 10-06. `pyproject.toml` includes `ketu.houses`; `ketu/__init__.py` re-exports 5 new names; `grep -r "swisseph" ketu/houses/` returns nothing (pure-NumPy contract preserved). 538 tests pass (510 + 28 new); mypy --strict clean across 8 source/test files. **Vertex formula deviation Rule 1**: plan reference text omitted the anti-meridian shift (yielded antivertex, off by ~168°); production code uses the corrected `armc + 180` form, cross-checked at 0.42″ vs swisseph oracle.
Last activity: 2026-05-07 — Plan 10-03 executed; commits `71c30ce` (subpackage skeleton) + `fb2a161` (compute_ascmc) + `a5992dc` (28 new tests) on `gsd/v1.1-milestone`

Progress: [███████░░░] v1.0 complete; v1.1 2/5 phases complete (Phase 8: 5/5, Phase 9: 6/6 awaiting check-phase), Phase 10: 3/6 plans

## Performance Metrics

**Velocity (v1.0 reference baseline):**

- Total plans completed (v1.0): 16
- v1.1 plans completed: 14 (Phase 8: 08-01, 08-02, 08-03, 08-04, 08-05; Phase 9: 09-01, 09-02, 09-03, 09-04a, 09-04b, 09-05; Phase 10: 10-01, 10-02, 10-03)

**By Phase (v1.1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 8. Lilith Verification & Fix | 5 | ~22m 18s | ~4m 28s |
| 9. Configurable Aspects | 6 | ~44m 58s | ~7m 30s |
| 10. Houses Module | 3 | ~20m 54s | ~6m 58s |
| 11. CLI Refactor & Integration | 0 | — | — |
| 12. Release Preparation v1.1.0 | 0 | — | — |

*Updated after each plan completion*
| Phase 08 P01 | 2min | 1 tasks | 1 files |
| Phase 08 P02 | 2m 5s | 2 tasks | 1 files |
| Phase 08 P03 | 4m 31s | 2 tasks | 1 files |
| Phase 08 P04 | 10m 1s | 4 tasks | 4 files |
| Phase 08 P05 | 3m 41s | 2 tasks | 2 files |
| Phase 09 P03 | 1m 35s | 1 tasks | 1 files |
| Phase 09 P02 | 5m 25s | 3 tasks | 3 files |
| Phase 09 P01 | 6m 00s | 2 tasks | 1 files |
| Phase 09 P04a | 6m 34s | 2 tasks | 1 files |
| Phase 09 P04b | 6m 3s | 1 tasks | 3 files |
| Phase 09 P05 | 19m 21s | 2 tasks | 3 files |
| Phase 10 P01 | 9m 1s | 2 tasks | 4 files |
| Phase 10 P02 | 4m 5s | 2 tasks | 3 files |
| Phase 10 P03 | 7m 48s | 3 tasks | 8 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Recent decisions affecting current work:

- Default aspects = 5 majors in v1.1 — Pro/classical default; ML harmonics opt-in via `--harmonics`
- Houses module starts with Placidus + Koch — two systems prove extensibility; others plug in later
- Verify Lilith before fixing — confirm bug exists and quantify error before changing formula
- Vectorize everything new — houses + harmonics must be batchable over date arrays
- `core.aspects` stays length-14 append-only (Kala uses positional indexing — non-negotiable)
- `pysweph>=2.10.3.6` is test-only dependency (AGPL-safe; no runtime deps added)
- [Phase 08]: Test-only optional extra pattern: AGPL-licensed pysweph lives under [project.optional-dependencies].test, never in [project].dependencies — proven empirically with two-venv install test
- [Phase 08-01]: Investigation-first ordering enforced — `docs/LILITH_DEFINITION.md` (contract for harness/fix) lands BEFORE any code change; tolerance derived arithmetically (0.01 deg ≈ 129 min mean apogee drift), not a round-number convention; History section pre-seeded with literal Plan 04 sentinel for atomic update
- [Phase 08]: Plan 04 branch = FORMULA-CORRECTION (empirical max |delta| = 179.94 deg, ~18000x tolerance); suspected root cause: epoch constant 83.3532 off by 180 deg (Ketu computes perigee, swe expects apogee); residual after +180 deg correction is 0.111 deg (still 11x tolerance) -- secondary frame/rate term to address
- [Phase 08]: Cross-check harness pattern locked: pytest.importorskip module-level gate (no binding) + separate import for mypy --strict + manual swe.version check (since pysweph __version__ is int date stamp) + always-pass diagnostic Python script alongside assertion test to capture deltas regardless of pass/fail; defensive index-based tuple unpack for foreign C-extension return shape
- [Phase 08-04]: Single source of truth for Lilith constants — 5 private module-level constants `_LILITH_MEAN_*` and `_LILITH_PERTURB_*` in `ketu/ephemeris/orbital.py`; all 4 plumbing sites (orbital.py x2, planets.py x2) reference them by name. Eliminates v1.0's 4-site duplication drift risk
- [Phase 08-04]: Pure linear correction insufficient — secondary residual ~0.124 deg has dominant 1095-day (3 sidereal years) sinusoidal signature. v1.1 formula adds one trig perturbation term (linear secular + 1 sin), fitted via joint Nelder-Mead NLS over 55K daily samples 1900-2050. Pattern: when a mean-element formula misses external reference by sinusoidal residual, add the dominant FFT-identified perturbation
- [Phase 08-04]: REGRESSION_TOLERANCE_DEG = 0.005 — half of user-facing 0.01 deg, ~1.85x post-fit max (0.002693). Pins agreement margin without hardcoding Ketu output (research §"Anti-patterns" preserved). Test-only threshold; production users still bound by 0.01 deg contract
- [Phase 08-04]: avg_speeds[12] uses `round(_LILITH_MEAN_RATE_DEG_PER_DAY, 6)` — preserves 6-decimal `avg_speeds` dict convention while inheriting from source-of-truth named constant
- [Phase 08]: [Phase 08-05] Magnitude consistency invariant locked across CHANGELOG/UPGRADING/LILITH_DEFINITION at 6-decimal precision: pre-fix 179.936579 deg (user-visible breaking-change), post-fix 0.002693 deg (5 dates) and 0.007815 deg (55K daily samples) -- both <0.01 deg tolerance. Per-date table in UPGRADING live-computed from get_lilith_position rather than copied from Plan 04 SUMMARY
- [Phase 08]: [Phase 08-05] Deviation from pure Chapront secular linear stated transparently in CHANGELOG and UPGRADING (NOT minimized): both files explicitly state v1.1 ships 'linear secular term + 1 sin() perturbation', not a raw ELP-2000 polynomial. Per execution-context note from Wave 3 orchestrator
- [Phase 09]: [Phase 09-03]: core.aspects invariant pinned via sha256 byte fingerprint (c5bd1773...9afb359) + per-row name/angle/coef + length 14 + dtype.names. Mutation test verified surgical row-drift detection. Defense-in-depth pattern: any future drift in rows 0-13 fails with informative messages identifying the affected row index
- [Phase 09]: [Phase 09-02]: ketu/aspects/presets.py — three frozen length-14 np.bool_ masks (CLASSICAL=5, TRADITIONAL=7, EXTENDED=14) with single-call resolve_aspect_set() dispatching on six input types (None / str preset case-insensitive / Sequence[str|int] / np.ndarray bool|int). Defensive bool-rejection in Sequence prevents silent [True, False] -> [1, 0] index coercion. ASP-06 forward-looking rule documented (no caches today materialize filtered aspects, but Wave 2 must hash mask.tobytes() if adding any). 100% test coverage on presets.py (56 tests).
- [Phase 09]: [Phase 09-01]: ASP-08 v1.0 baseline frozen at `.planning/phases/09-configurable-aspects/baseline-v1.0.json` (git_sha=049a9e7, aspect_set=extended, mean[365]=200.87ms cv=1.62%, 50 iter × 3 batch sizes, drift=3.56% PASS <5% gate). `tests/benchmark_aspects_batch.py` ships --aspect-set flag from day 1 and mismatch-rejection in --compare mode (no silent baseline-vs-comparison drift). Wave-1 parallel collision: identical script content authored independently by Plan 09-01 and committed via Plan 09-02 commit `78085d1` — md5 verified byte-identical, no merge needed.
- [Phase 09]: [Phase 09-04a]: `ketu/aspects/calculator.py` refactor threads `aspects: AspectSetSpec = None` (default → CLASSICAL via resolver) through 4 public multi-aspect APIs. Module-level `from ketu.core import aspects` renamed to `aspects as _CORE_ASPECTS` to free the parameter name. 2 hot loops rewritten to `for k, i_asp_val in enumerate(selected_indices)` emitting canonical `int(i_asp)` (NOT `k`) — Kala positional contract preserved. Resolver runs ONCE per API call; in `calculate_aspects_batch` ABOVE the per-date loop (never per-date). `find_aspects_between_dates` passes filtered `selected_angles` to downstream `find_all_aspects` (no leak of unselected aspects). LRU-cache audit: 2 sites (`_cached_planet_position_batch`, `body_properties`), both safe — neither materializes filtered aspect output. `calculate_aspects` reuses out-of-scope scanner `get_aspect` with post-hoc filter via `selected_indices_set` — preserves single source of truth for scalar match logic without rewriting scanner. 479 tests pass with NO retrofit needed (all assertions use loose count/structure checks or sibling-parity); mypy --strict clean; interrogate 100%.
- [Phase 09]: [Phase 09-04b]: Four hardcoded `["Conjunction", "Sextile", "Square", "Trine", "Opposition"]` literal default lists (1 in windows.py find_aspects_timeline, 1 in timelines.py generate_aspect_timeline, 2 in transits.py find_transits_to_position + compare_dates_transits) replaced with `list(_CLASSICAL_NAMES)` derivation from CLASSICAL preset. Per file: ONE module-level import block + `_CLASSICAL_NAMES = tuple(aspects["name"][i].decode() for i in np.where(_CLASSICAL_MASK)[0])`. Approach A locked (preserve `aspects_list: list[str]` shape; do NOT widen to AspectSetSpec — v1.2+ scope). `find_aspect_window` (single-aspect API) and `lunar_calendar.BIG_FIVE` untouched. Single-source-of-truth invariant verified by provenance smoke test: all three modules resolve to canonical 5-major tuple. 479 tests pass; mypy --strict clean. Pre-existing interrogate gap (85.2% < 90% in nested callbacks) verified unrelated to this plan via git-stash baseline comparison.
- [Phase 09]: [Phase 09-05]: ASP-07 verified by 9-test `TestAspectPresetsIntegration` class extending `tests/test_aspect_presets.py` — covers `calculate_aspects` / `_vectorized` / `_batch` / `find_aspects_between_dates` with CLASSICAL/TRADITIONAL/EXTENDED + default-flip + canonical-i_asp + EXTENDED-superset assertions. ASP-08 verified by `benchmark-comparison.json`: Phase 9 EXTENDED is -10% to -15% FASTER than v1.0 baseline on every batch size (30/90/365); CLASSICAL is -33% to -41% faster (matches research's 30-65% inner-loop speedup prediction). HARD GATE passed with margin; no CONDITIONAL band needed.
- [Phase 09]: [Phase 09-05]: Hot-loop perf regression discovered and auto-fixed (deviation Rule 1). Plan 09-04a's calculator refactor introduced per-date Python-scalar casts (`int(i_asp)` / `float(angle)` / `float(coef)`) AND per-date orb-array recomputation `(orbs_body1+orbs_body2)/2 * coef` — paid `n_dates × n_aspects` times instead of `n_aspects` times. Initial 200-iter benchmark showed +6-7% regression on EXTENDED. Fix: hoist all per-aspect work above per-date loop — pre-cast lists `selected_iasp_ints` / `selected_angles_f` / `selected_coefs_f` + pre-multiplied `selected_orbs_per_aspect = [pair_orb_sums * c for c in selected_coefs_f]` (date-independent). Result: regression turned into -8% to -15% improvement. Pattern locked: any future hot-loop refactor of `calculate_aspects_batch` MUST be benchmarked at ≥200 iterations against baseline-v1.0.json before merging — the 50-iter compare default is noise-dominated at 5% gate width. Fix commit `b847176`.
- [Phase 10]: [Phase 10-01]: LST/obliquity precision audit verdict TIGHTEN. Root cause was a mean-vs-apparent semantic mismatch, NOT a polynomial-precision issue: ketu's `sidereal_time()` returned mean GMST while `swe.sidtime` (and `swe.houses_armc`) consume apparent GST. Fix = mean GMST + equation of equinoxes per Meeus 2nd ed. eq. 12.6 (`EE = nut_lon × cos(eps_mean)`), reusing existing `nutation()` and `mean_obliquity()` from `coordinates.py` — no new dep, no new formula, signature `(jd, longitude=0.0) -> float` preserved. Empirical drift collapsed: GST 16.4″ → 2.05″, polar ASC at lat=66.5° 227″ → 8.7″ (HOU-01 60″ spec comfortably met). `tests/houses/` subpackage established (`__init__.py` marker + `test_lst_obliquity_precision.py` with 4 parametrized tests = 16 cases). TOL_GMST_ARCSEC = 5.0 (NOT plan-suggested 1.0): 4-term truncated nutation series in `coordinates.nutation()` leaves ~2″ residual; full IAU 2000A is v1.2 scope. TOL_POLAR_ASC_ARCSEC = 50.0 (10″ headroom vs HOU-01 60″ spec). Polar boundary fence at lat=66.5° intentionally includes 2024-06-21 Placidus singularity sample to expose near-circumpolar instability for Plan 10-05 Porphyry-fallback design. Pattern locked: `swe.houses_armc(armc, lat, eps, b'P')` isolation for primitive-drift fences — separates Placidus-implementation errors from input-precision errors; Plan 10-04/10-05 will reuse.
- [Phase 10]: [Phase 10-02]: Oracle harness landed in `tests/houses/conftest.py` — `SYSTEM_BYTES` dict (`{placidus: b'P', koch: b'K', porphyry: b'O'}`) centralises Pitfall 8 (bytes-vs-str) at the boundary; `swe_oracle(jd, lat, lon, system)` slices `cusps_t[1:13]` solving Pitfall 7 (13-tuple/0-indexed) once. `swe_oracle_armc(armc, lat, eps, system)` complements via `swe.houses_armc` so Plans 03/04/05 can isolate algorithm error from sidereal-time error. `reference_charts` session-scoped fixture: 10 entries (Greenwich, Paris, Sydney, Tokyo, BuenosAires, Equator, NewYork@1900, Reykjavik@2050, polar 70°/80° at J2000) — exactly meets HOU-09 floor with no slack. `tests/houses/fixtures/reference_charts.json` (641 lines, 20 KB, sha256 `b7762c9b7c255f6d8ecb382853d0cdacd7a5a1347964d3a377493790c6769581`, swisseph 2.10.03) snapshots 10×3 = 30 entries; polar Placidus/Koch marked `{error: 'swisseph.houses_ex: error', polar: True}`, polar Porphyry produces full closed-form cusps even at lat=80° (the polar fallback path Plan 10-05 must reproduce). 6 pure-infra smoke tests with snapshot-vs-live tolerance 1e-9 deg (deterministic swisseph; any drift = environmental change worth flagging). Snapshot script is one-off scaffolding (NOT committed; lived at `snapshot_reference_charts_tmp.py` then deleted) — only the JSON output is tracked. Wave 3 (Plans 10-04 and 10-05) can run in parallel reading the same JSON without modifying it. Deviation: 1 mypy-only float-cast on `mean_obliquity()` return for `swe_oracle_armc(eps: float)` parameter — vectorised return type `float | np.ndarray` flagged by `--strict`.
- [Phase 10]: [Phase 10-03]: `ketu.houses` subpackage scaffold landed — `HOUSES_DTYPE` (9 fields: jd/lat/lon/system/cusps[12]/asc/mc/armc/vertex; outer (N,) → cusps (N,12)) + `HighLatitudeError` (ValueError subclass; carries lat/system/polar_lat with helpful "polar_fallback='porphyry'" hint in message) + `SYSTEMS` registry dict + `@register("name")` decorator (lowercase normalisation) + `get_system(name)` dispatch (case-insensitive lookup; ValueError-with-options on unknown). `compute_ascmc(jd, lat, lon)` returns dict[asc, mc, armc, vertex, eps] vectorised over arbitrary broadcast shape; all four angles via `np.arctan2` (Pitfall 2). `compute_armc = (sidereal_time(jd, 0.0) + lon) % 360` — explicit decomposition matching Pitfall 5 audit form; lifts scalar `sidereal_time` via list-comp (microseconds for 1000 charts). Vertex formula required deviation Rule 1: plan reference text was `atan2(cos(armc), -[sin(eps)tan(90-lat) + cos(eps)sin(armc)])` which yields the **antivertex** (off by ~168° from oracle); correct form evaluates ASC closed-form at `armc + 180` (anti-meridian) with co-latitude — empirical cross-check at J2000_Paris: 0.42″ vs oracle 190.1198°. 28 new tests (5 dtype + 5 registry + 18 ascmc): worst-case oracle deltas — ASC 51.5″ @ 2050_Reykjavik, MC 1.2″ @ J2000_BuenosAires, ARMC 1.9″ @ Reykjavik, Vertex 15.5″ @ J2000_Tokyo (all <60″ HOU-01 spec / <300″ Vertex advisory). 538 tests pass (510 + 28); mypy --strict clean across 8 files; `grep "swisseph" ketu/houses/` returns nothing (pure-NumPy contract preserved). `pyproject.toml` updated with `ketu.houses`; `ketu/__init__.py` re-exports `HOUSES_DTYPE`, `HighLatitudeError`, `HOUSE_SYSTEMS` (renamed from `SYSTEMS` to avoid clobbering top-level globals), `calculate_houses`, `house_of`. Stubs raise `NotImplementedError` with explicit "wired in Plan 10-06" message — signature + docstring contract stable now. Deviation Rule 3: mypy-strict typed-local pattern (`result: np.ndarray = np.rad2deg(...) % 360.0; return result`) required because numpy ufunc % returns `Any`; pattern reused across `_ecliptic.py` and `ascmc.py`. Pattern locked for Plans 10-04 / 10-05: registry signature `(armc, lat, eps) -> cusps[..., 12]`; Placidus/Koch/Porphyry plug in via `@register` without touching `calculate_houses`.

### From v1.0 milestone (carried context)

- Pure NumPy contract: no new runtime deps allowed
- Mypy strict mode enforced in CI; numpydoc-style docstrings on public API; interrogate ≥95%
- Trusted publishing OIDC configured for PyPI releases
- Test isolation pattern: pytest tmp_path fixture for file I/O
- Error message convention: ValueError with received value + valid options
- Two-layer caching is intentional: LRU for single-point, EphemerisCache for batch
- v1.0 milestone roadmap archived to `.planning/milestones/v1.0-ROADMAP.md`

### Roadmap Evolution

- v1.0 milestone complete (8 phases including 2.1 insertion, 16 plans, ketu 1.0.0 on PyPI 2026-02-12)
- v1.1 milestone planned: 5 phases (8-12), 33 requirements, parallelizable 8/9/10 then 11 then 12

### Pending Todos

None yet.

### Blockers/Concerns

- **Kala aspect-count dependency unverified** (Phase 9 risk) — confirm with Kala maintainer that `KetuAdapter` either tolerates `EXTENDED` opt-in or is updated before Phase 9 merge
- ~~**LST/obliquity precision audit** (Phase 10 first task)~~ **CLOSED by Plan 10-01 (commits `0cb3ad0` + `bcfdcf6`).** Verdict TIGHTEN; `sidereal_time()` upgraded to apparent GST; max GST drift 2.05″, max polar ASC error 8.7″ — well inside HOU-01 <60″ spec.
- **Placidus near-circumpolar instability** (Phase 10-05 design concern) — empirically observed at 2024-06-21 lat=66.5° / ARMC=269.7° via Plan 10-01's regression fence: `dASC/dARMC ~70″/1″`, swisseph itself fails for lat ≥ 66.6° at this ARMC. Plan 10-05 (`koch-porphyry-polar`) must absorb this with Porphyry fallback above the polar circle; the regression fence in `tests/houses/test_lst_obliquity_precision.py` Test 4 will catch any regression.

## Session Continuity

Last session: 2026-05-07 (Plan 10-03 execution; Phase 10 Wave 2 closing)
Stopped at: Completed `10-03-registry-dtype-ascmc-PLAN.md`. `ketu.houses` subpackage scaffold landed across 5 source files (`__init__.py` + `core.py` + `registry.py` + `_ecliptic.py` + `ascmc.py`) and 3 test files (`test_dtype.py` + `test_registry.py` + `test_ascmc.py`). HOU-02 (registry pattern) + HOU-05 (HOUSES_DTYPE structured array) requirements partial-landed; Plans 10-04 and 10-05 plug Placidus / Koch / Porphyry into the same `SYSTEMS` dict via `@register("name")` without touching dispatch logic. Closed-form vectorised ASC/MC/ARMC/Vertex via `np.arctan2`: 8/8 non-polar charts agree with pyswisseph oracle <1 arcmin on ASC/MC/ARMC, Vertex <5 arcmin advisory. Worst case ASC 51.5″ at 2050_Reykjavik (lat 64.1°N — yellow flag for high-latitude precision; Plan 10-05 should monitor). Plan 10-03 commits do NOT include conftest.py / fixtures/ artifacts (those are Plan 10-02's responsibility). Two deviations documented in 10-03-SUMMARY.md: (1) Rule 1 Vertex formula correction — plan reference text omitted anti-meridian shift, fix is `armc + 180` + co-latitude; (2) Rule 3 mypy-strict typed-local pattern for ndarray return casts (numpy ufunc % 360 returns Any). Public API stubs `calculate_houses` / `house_of` declared with full signature + docstring; bodies raise `NotImplementedError` until Plan 10-06. `HOUSE_SYSTEMS` exported at top-level (renamed from `SYSTEMS` to avoid clobbering); `pyproject.toml [tool.setuptools].packages` includes `ketu.houses`. 538 tests pass (510 + 28 new); mypy --strict clean across 8 files; coverage 97.50%. Commits `71c30ce` (Task 1 — skeleton) + `fb2a161` (Task 2 — ascmc) + `a5992dc` (Task 3 — tests) on `gsd/v1.1-milestone`. Pre-existing branch state (Phase 9 awaiting `/gsd:check-phase`, "Kala aspect-count dependency unverified" pre-merge action, `venv/bin/{pytest,mypy}` shebang workaround) carried forward.
Resume file: Plan 10-04 (`placidus-implementation`) — Wave 3 next plan; can `from ketu.houses.registry import register` and `from ketu.houses.ascmc import compute_ascmc` to plug Placidus into the dispatch and consume the closed-form ARMC/eps. Plan 10-05 (`koch-porphyry-polar`) parallelisable in same wave.

---
*State initialized: 2026-02-12*
*Last updated: 2026-05-07 — Plan 10-03 complete; Phase 10: 3/6 plans. ketu.houses subpackage skeleton + closed-form ASC/MC/ARMC/Vertex (vectorised, np.arctan2) landed; ASC <1 arcmin oracle agreement on 8/8 non-polar charts; SYSTEMS registry pattern ready for Wave 3 (Placidus + Koch + Porphyry). Vertex anti-meridian deviation Rule 1 logged.*
