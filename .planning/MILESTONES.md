# Milestones

Historical record of shipped versions. Most recent first.

---

## v1.4 Dynamic Harmonics & Chiron Range — Shipped 2026-06-03

**Tag:** `v1.4.0` (commit `3f3f9b4`, annotated SHA `ca9e24c`)
**PyPI:** <https://pypi.org/project/ketu/1.4.0/>
**GitHub release:** <https://github.com/alkimya/ketu/releases/tag/v1.4.0>
**Phases:** 28-32 (5 phases)
**Plans:** 15 (3 + 1 + 2 + 7 + 2)
**Tests:** 1539 collected (pure-NumPy runtime; `pyswisseph` build/test-only)
**Timeline:** 2026-06-02 → 2026-06-03 (~1 day, intensive)
**Git range:** 64 commits since `v1.3.0`; 93 files changed (+10,629 / −1,252), of which 49 source files (+3,308 / −959)
**LOC:** ~38,932 Python (ketu/ + tests/)
**Coverage:** 100% maintained (fail_under=100); mypy `--strict` clean; numpydoc + interrogate gates held

### Delivered

Ketu made aspect harmonics open-ended. A new `generate_harmonic_aspects(h)` generator produces first-class aspects for ANY integer harmonic `h` — not just the preset set `{1,2,3,5,6,9,10}` — wired through the full detection chain (`calculate_aspects` scalar/vectorized/batch, cycles, synastry) via a `dynamic_specs=` parameter, with per-pair orbs derived from `core.bodies['orb']` × dynamic coefficient. The dynamic path is strictly PARALLEL and ADDITIVE: the frozen 14-row `core.aspects` table and its named-preset sha256 fingerprints (V1/V13) stay byte-identical, and `_VALID_HARMONICS` never gates the dynamic path. Alongside, Chiron's validity range widened to 1900–2100 (`.npz` regenerated, 2283 segments, max|Δλ|=0.001214°), its natal orb corrected 0°→4° (Pluto parity, single-source `core.bodies['orb']`), and the documentation (en + fr) was recentred on the 180°-division default. Closed with `ketu==1.4.0` on PyPI via OIDC.

### Key Accomplishments

1. **Dynamic harmonic generator** (Phase 28) — `generate_harmonic_aspects(h)` for any integer `h` in [2..64], returning `(angle, coef)` specs using the unified 360° convention (`fold_to_0_180(k·360/h)` for `k=1..h//2`, coef `k/h`, mirror pairs deduplicated, 0°/360° never emitted, blank symbol for unnamed high harmonics). `HARMONIC_DTYPE` is a drop-in mirror of `core.aspects`; `DynamicAspectSpec` type alias for the `dynamic_specs=` parameter; `_fold_to_0_180` helper implements the locked convention. New module `ketu/aspects/harmonics.py` independent of `presets`/`_VALID_HARMONICS`, 100% covered (96-test suite), V1 sha256 fingerprint guard preserved.
2. **Detection-chain integration** (Phase 28) — `dynamic_specs=` threaded through `calculate_aspects` (scalar/vectorized/batch, `i_asp=-2` sentinel for dynamic rows), `calculate_synastry` (`aspect_type=-2`), and `generate_cycle_series`/`multi` (extended candidate set). `find_aspect_timing` and `find_aspects_between_dates` guarded so off-table dynamic angles resolve via a synthetic name instead of raising `IndexError`.
3. **Chiron orb 0°→4°** (Phase 29) — single-source change in `core.bodies['orb'][13]` propagating automatically to `_BODY_ORBS_16`, synastry, cycles, and the CLI (no manual duplication). CLI byte-stable fixture regenerated and manually audited (2 new Semi-sextile lines); synastry docstrings corrected to remove Chiron from the zero-orb group; explicit pinning test `test_synastry_orb_limit_chiron_chiron_parity_pluto`.
4. **Chiron range 1900–2100** (Phase 30) — blocking pre-commit spike measured max|Δλ| over the widened range incl. the ~1895–96 perihelion just below the lower bound (dense 1900–1910 edge sampling): degree=10/seg=32d held the < 0.01° gate (max 0.001214°, 8.2× margin) — no degree bump needed. `chiron_coeffs.npz` regenerated over 1900–2100 (2283 segments), `actual_len` partial-segment fix preserved, runtime stays 100% pure NumPy; regression refs re-pinned with pre-1950 + post-2050 wings; bounds-clamp tests added (clamping, not `ValueError`).
5. **Documentation recentred (en + fr)** (Phase 31) — `concepts.md` recentred on the 180°-division default; aspect tables collapsed to CLASSICAL (5) / TRADITIONAL (7) with default vs opt-in marked, EXTENDED (H5/H9/H10) framed as "available in code"; `generate_harmonic_aspects(h)` documented with a runnable h=7 example + the accepted ~2× smaller full-circle orb note; Chiron range/orb corrected across `migration.md`, `relational_charts.md`, `api.md`, `chiron.md`; stale `EXTENDED.*default` / `classical.*default` claims removed; no Kala reference anywhere. Full French gettext cycle: 7 catalogs re-extracted, translated to 0 untranslated/0 fuzzy, 7 `.mo` recompiled; en + fr build at the 1-warning baseline.
6. **Release 1.4.0** (Phase 32) — mypy `--strict` cleared (`synastry/api.py` cast fix); version → 1.4.0 in `pyproject.toml` + `ketu/__init__.py`; fresh-authored dated `[1.4.0]` CHANGELOG (Added: dynamic generator + Chiron 1900–2100; Changed: orb 0°→4° + clamp + docs recentring), `fr/CHANGELOG.md` synced; UPGRADING v1.3→v1.4 + README "What's New". Tag `v1.4.0` + `origin/main` BOTH pushed (RTD follows main, PyPI follows tag); GitHub release with sdist + wheel; OIDC publish (`publish.yml` SUCCESS); post-publish fresh-venv smoke FROM PyPI passed all four assertions (`generate_harmonic_aspects(7)=[51.4286,102.8571,154.2857]`, Chiron orb=4.0, `calc_planet_position(jd_1920,13)` finite, `find_spec('swisseph')=None`).

### Decisions Made (Outcomes)

- **Dynamic path PARALLEL to the frozen table, not a replacement** — ✓ Good. `core.aspects` V1/V13 fingerprints stayed byte-identical; `_VALID_HARMONICS` never consulted on the dynamic path.
- **Accept ~2× smaller full-circle dynamic orbs (no convention unification)** — ✓ Good. The half-circle (table) and full-circle (dynamic) orb conventions coexist as independent paths; documented, not reconciled.
- **Chiron orb single source `core.bodies['orb']`** — ✓ Good. One edit propagated to synastry/cycles/composite/CLI; `_BODY_ORBS_16` sliced read-only at import, never hand-edited.
- **Blocking spike BEFORE committing the 1900–2100 `.npz`** — ✓ Good. Empirically confirmed degree=10 holds the gate on the early wings (8.2× margin), avoiding an unnecessary degree bump and the size it would add.
- **v1.4 = additive minor, not a patch** — ✓ Good. The originally-scoped "v1.3.1 docs patch" was absorbed once dynamic harmonics + Chiron range made it a minor; only behaviour change (Chiron orb) documented in CHANGELOG.

### Issues Resolved

- `find_aspect_timing` / `find_aspects_between_dates` hardcoded table-index lookups guarded against `IndexError` for off-table dynamic angles (synthetic name).
- mypy `--strict` `no-any-return` in `synastry/api.py` fixed via `cast(np.ndarray, ...)` typing-only no-op.
- CHANGELOG authored fresh (no stale `Unreleased` to merge); docs `changelog.md` date-stamped (no XX placeholders).

### Issues Deferred (v1.5+)

- **CLI `--harmonics h7` arbitrary-harmonic flag** (ASP-F1) — return-type + CLI byte-stability work; the Python API is the v1.4 surface.
- **Formalize the synthetic off-table naming scheme** (`H7k1`) as a documented API contract (ASP-F2).
- **`find_aspect_timing` orb-derivation design debt** (orb passed directly vs table-derived) — documented in v1.4, refactor later (ASP-F3).
- **Chiron range beyond 1900–2100** — covers all relevant birth/event dates + near-future; wider adds segments/size for no demand.

### Technical Debt Incurred

None of significance — all 5 phases verified PASSED at their success criteria (28: 5/5, 29: 6/6, 30: 3/3, 31: 4/4, 32: 3/3). The deferred items above are scope decisions (tracked as ASP-F1..F3), not shortcuts.

**Archive:** Roadmap details in `.planning/milestones/v1.4-ROADMAP.md`. Requirements in `.planning/milestones/v1.4-REQUIREMENTS.md`.

---

## v1.3 Chiron & Engine Hardening — Shipped 2026-06-01

**Tag:** `v1.3.0` (commit `1f9fb80`)
**PyPI:** <https://pypi.org/project/ketu/1.3.0/>
**GitHub release:** <https://github.com/alkimya/ketu/releases/tag/v1.3.0>
**Phases:** 21-27 (+ inserted 26.1) — 8 phases
**Plans:** 30 (4 + 3 + 2 + 5 + 3 + 3 + 8 + 2)
**Tests:** 1399 (pure-NumPy runtime; `pyswisseph` validation/build-only)
**Timeline:** 2026-05-29 → 2026-06-01 (~3 days)
**Git range:** 131 commits since `v1.2.0`
**Coverage:** 100% project (fail_under=100, zero pragma); mypy `--strict` clean; numpydoc + interrogate gates BLOCKING

### Delivered

Ketu embedded Chiron as the 14th body and hardened the engine to 100% coverage. After lifting coverage to 100% and refactoring the fragile `calc_planet_position` if-elif into per-body strategies (splitting `orbital.py`, consolidating fixtures), Chiron was added as a Chebyshev-by-segment fit in an embedded `.npz` evaluated by a pure-NumPy runtime (zero swisseph at runtime; offline `pyswisseph` generator is build-only). The aspect engine became data-driven — one declarative `Aspect` table the engine iterates over, `aspects_for_harmonics` for harmonic-based selection, library default = TRADITIONAL (7 half-circle aspects). The Sphinx docs (en + fr) were brought to the full v1.1/v1.2/v1.3 surface (17 `.po` catalogs, 1405 messages, 100% translated). The 13→14 body shift deliberately broke the frozen-body-count ratchet and the internal Ketu↔Kala positional contract (Kala adapts to Ketu, not vice-versa).

### Key Accomplishments

1. **Quality to 100% coverage** (Phase 21) — `fail_under=100` gate (zero pragma, `exclude_lines`), 8 orbital + `coordinates.py:278` div/0 guards, 52 doctests + `make doctest` gate.
2. **Ephemeris refactor** (Phase 22) — `calc_planet_position` if-elif replaced by per-body `BODY_STRATEGIES`; `orbital.py` split; fixtures consolidated — making Chiron a clean strategy, not aggravated debt.
3. **Chiron spike** (Phase 23) — GO verdict: Chebyshev seg=32d/degree=10/3-quantities locked; max|Δλ|=0.000861° (11.6× under 0.01°) over 1142 segments 1950–2050, evaluated by pure-NumPy `chebval`. Spike-only (nothing under `ketu/`/tests/pyproject).
4. **Chiron embedded** (Phase 24) — 14th body (`body_id=13`), `.npz` Chebyshev embedded + pure-NumPy evaluator (zero swisseph under `ketu/`); 6 insertion points via `BODY_STRATEGIES` with no special-casing; 13→14 ratchet break executed; max|Δλ|=0.005695°.
5. **Documentation + data-driven aspects** (Phases 25, 26) — docs brought to v1.1/v1.2/v1.3 surface; aspect engine made data-driven (one declarative table the engine iterates over).
6. **French documentation 100%** (Phase 26.1, INSERTED) — 17 `.po` / 1405 messages translated, en + fr build clean.
7. **Release 1.3.0** (Phase 27) — version → 1.3.0; `ketu==1.3.0` on PyPI via OIDC; tag + `origin/main` both pushed.

### Decisions Made (Outcomes)

- **Chiron via embedded Chebyshev coeffs, not swisseph runtime** — ✓ Good. Pure-NumPy runtime + AGPL isolation preserved; `.npz` in package, eval 100% NumPy.
- **Refactor ephemeris BEFORE adding Chiron** — ✓ Good. Chiron landed as a clean strategy, not aggravated if-elif debt.
- **v1.3 stays `1.3.0` despite breaking the 13→14 body freeze** — ✓ Good. Ketu is source-of-truth; public API stayed additive, only the internal Ketu↔Kala positional array broke (Kala adapts).
- **Aspect engine data-driven, library default TRADITIONAL (7)** — ✓ Good. One table the engine iterates; carried into v1.4 unchanged.

### Issues Deferred (v1.4)

- **Dynamic harmonics generator** — open-ended harmonics beyond the preset set (shipped v1.4).
- **Chiron range beyond 1950–2050** — widened to 1900–2100 in v1.4.
- **Chiron orb** — corrected 0°→4° in v1.4.

### Technical Debt Incurred

None of significance — all phases verified PASSED at their success criteria. The deferred items above were scoped into v1.4.

**Archive:** Roadmap details in `.planning/milestones/v1.3-ROADMAP.md`. Requirements in `.planning/milestones/v1.3-REQUIREMENTS.md`.

---

## v1.2 Astrologie relationnelle et prédictive — Shipped 2026-05-28

**Tag:** `v1.2.0` (commit `d775663`)
**PyPI:** <https://pypi.org/project/ketu/1.2.0/>
**GitHub release:** <https://github.com/alkimya/ketu/releases/tag/v1.2.0>
**Phases:** 13-20 (8 phases)
**Plans:** 35 (5 + 5 + 4 + 5 + 4 + 5 + 3 + 4)
**Tests:** 1286 collected (pure-NumPy runtime; `pyswisseph` oracle suite test-only)
**Timeline:** 2026-05-08 → 2026-05-28 (~20 days)
**Git range:** 205 commits since `v1.1.0`
**Coverage:** 100% on all new subpackages (`ketu/charts/`, `ketu/synastry/`, `ketu/composite/`, `ketu/returns/`, `ketu/parts/`); ≥90% project, ≥85% per module gates held; ≥95% new-module gate exceeded

### Delivered

Ketu became a full relational and predictive astrology framework, strictly non-breaking (every API additive — no default change, no export removed). v1.2 shipped a chart-abstraction keystone (`CHART_DTYPE` / `compute_chart` / `is_day_chart`) that synastry, composite, and returns all build on; three new house systems proving the v1.1 registry extensibility claim; relational charts (synastry + midpoint composite); predictive charts (solar + lunar returns sharing one pure-NumPy `_solve_return` core with arc-second convergence); and an extensible Arabic Parts framework. The milestone also retired the v1.1 ops debt: doc gates flipped to BLOCKING and workflows moved to Node 24, closing with `ketu==1.2.0` on PyPI via OIDC.

### Key Accomplishments

1. **Chart abstraction foundation** (Phase 14) — `ketu/charts/` subpackage with frozen `CHART_DTYPE` (bodies + ASC/MC/ARMC/Vertex + cusps + aspects), `compute_chart(jd, lat, lon, system, aspects)` resolving a full chart in one vectorizable call (scalar + array `jd`), and `is_day_chart` refactored to an ASC-delta sunrise-inclusive test. The keystone upstream of SYN/COMP/RET. 100% coverage.
2. **Three new house systems** (Phase 15) — Whole Sign, Equal, Regiomontanus added through the existing `SYSTEMS` registry (Whole Sign + Equal polar-safe); `--list-house-systems` now lists six systems alphabetically; each validated against Swiss Ephemeris on the 10-reference-charts oracle.
3. **Synastry** (Phase 16) — `calculate_synastry(chart_a, chart_b)` with `SYNASTRY_DTYPE` preserving chart-of-origin on every body, dense (N×M) and filtered output modes, synastry-tightened orbs distinct from natal; 3 hand-validated couples (Curie, Diana/Charles, Lennon/Ono) as oracle fixtures.
4. **Composite (midpoint)** (Phase 17) — `calculate_composite(chart_a, chart_b)` returning `CHART_DTYPE` with `circular_midpoint` helper (`mid(359°, 1°) == 0.0` pinned), composite houses derived from composite ASC/MC; Davison explicitly deferred to v1.3. 100% coverage on `ketu/composite/`.
5. **Solar + Lunar Returns** (Phase 18) — `solar_return` (calendar-anchored `target_year`) and `lunar_return` (instant-anchored `target_jd`, first return ≥ target) sharing a single pure-NumPy `_solve_return` bisection helper with central 360°→0° wrap handling; arc-second convergence; self-consistency oracle at 0.0001° is the PRIMARY gate, pyswisseph cross-check is test-only (per-body tolerance relaxed with measured ephemeris-theory deltas). Ketu runtime stays pure NumPy. 100% coverage on `ketu/returns/`.
6. **Arabic Parts framework** (Phase 19) — `ketu/parts/` extensible registry analogous to `SYSTEMS`, sect-aware `calculate_part` (Fortune/Spirit invert day/night) + fixed Marriage (no sect inversion), `calculate_all_parts`, `--list-parts` CLI. Scope reduced to 3 parts; 5 remaining Hermetic Lots deferred to v1.3 (framework absorbs them additively). 100% coverage on `ketu/parts/`.
7. **Ops debt retired + release** (Phases 13, 20) — `interrogate ≥95%` + `numpydoc validate` wired early (Phase 13) then flipped to BLOCKING (Phase 20); workflows moved to Node 24 (`actions/checkout@v5`, `setup-python@v6`, `upload-artifact@v5`); version → 1.2.0; dated additive `[1.2.0]` CHANGELOG; `ketu==1.2.0` published on PyPI via OIDC (run 26602811661, ~33s), GitHub release with sdist + wheel, fresh-venv smoke green.

### Decisions Made (Outcomes)

- **Chart abstraction as keystone before SYN/COMP/RET** — ✓ Good. `CHART_DTYPE` reused unchanged by all four downstream modules.
- **`is_day_chart` via ASC-delta (not horizon altitude)** — ✓ Good. Consistent with the ASC stored in the same `CHART_DTYPE`.
- **Single shared `_solve_return` for solar + lunar** (Phase 18 Success Criterion #3 binding) — ✓ Good. No inline bisection in either public API; grep ratchet enforces it.
- **Self-consistency oracle at 0.0001° as PRIMARY gate; pyswisseph cross-check test-only with per-body tolerance** — ✓ Good. Surfaced a genuine ephemeris-theory gap (Ketu TRUE Sun + truncated-Meeus Moon vs Swiss Ephemeris Moshier ELP) rather than masking it; runtime stays pure NumPy.
- **Reduce Arabic Parts from 8 to 3** — ✓ Good. The 5 deferred Lots had competing tradition variants; the registry absorbs them in v1.3 with no API change.
- **`pyswisseph` stays test-only (AGPL isolation)** — ✓ Good. Carried forward from v1.1; oracle/cross-check only.

### Issues Resolved

- v1.1 ops debt cleared: `interrogate`/`numpydoc` gates now BLOCKING in CI; Node 20 deprecation warnings eliminated (Node 24 actions).
- `circular_midpoint(359°, 1°)` wraparound pinned to `0.0` (not `180.0`).
- Lunar return mean-motion seed lift (Plan 18-03 Rule-1 deviation) — the planned blunt `target_jd + n·27.32` seed would have failed for most inputs; replaced with signed-residual mean-motion lift inside the ±1.5d bracket.
- pyswisseph cross-check premise corrected: Sun aberration does NOT cancel between the two resolved JDs; `_swisseph_body_lon` now passes `FLG_TRUEPOS | FLG_NOABERR` to align the convention with Ketu.
- Test-extra package typo `pysweph` → `pyswisseph` fixed.

### Issues Deferred (v1.3)

- **Davison composite** — midpoint composite shipped; Davison (time + lat/lon midpoints) deferred.
- **5 remaining Hermetic Lots** (Eros, Necessity, Courage, Victory, Nemesis) — competing tradition variants; need a domain-research pass.
- **Chiron + Centaurs, asteroids, fixed stars** — require swisseph runtime or a Chebyshev-fit pipeline (tooling not in place).
- **Transits / progressions / directions** — continuous time-series; different shape from return charts.
- **Astro.com manual cross-check** on resolved instants — anti-bot blocked; pyswisseph CI substitute is strictly stronger.

### Technical Debt Incurred

None of significance — all eight phases verified PASSED at their success criteria. The deferred items above are scope decisions, not shortcuts.

**Archive:** Roadmap details in `.planning/milestones/v1.2-ROADMAP.md`. Requirements in `.planning/milestones/v1.2-REQUIREMENTS.md`.

---

## v1.1 Flexibility & Houses — Shipped 2026-05-08

**Tag:** `v1.1.0` (commit `41ee42e`, annotated SHA `54ce673`)
**PyPI:** <https://pypi.org/project/ketu/1.1.0/>
**GitHub release:** <https://github.com/alkimya/ketu/releases/tag/v1.1.0>
**Phases:** 8-12 (5 phases)
**Plans:** 27 (5 + 6 + 6 + 6 + 4)
**Tests:** 724 passing local (557 in public CI; swisseph oracle suite local-only)
**Timeline:** 2026-02-12 → 2026-05-08 (~85 days)
**Git range:** 100 commits since `v1.0.0`; 147 files changed (+33,380 / −2,580)
**LOC:** ~22,148 Python (ketu/ + tests/)
**Coverage:** 96.75% on `ketu/houses/` (≥95% gate); ≥90% project (≥85% per module)

### Delivered

Ketu evolved from a pure astronomical engine into an astronomical-astrological framework. v1.1 shipped three orthogonal capabilities: configurable aspect sets (CLASSICAL default = 5 majors, opt-in TRADITIONAL/EXTENDED), an extensible houses module (Placidus / Koch / Porphyry with registry pattern), and a verified Lilith formula correction. The CLI was refactored to argparse subcommands; the legacy `input()` prompt was deleted.

### Key Accomplishments

1. **Lilith formula corrected** (Phase 8) — Empirical audit vs Swiss Ephemeris revealed max `|delta|` = 179.94° (Ketu was computing perigee, not apogee). FORMULA-CORRECTION applied at 4 plumbing sites; post-fix max `|delta|` = 0.002693° on plan dates, 0.007815° over 55K daily samples 1900-2050. Documented as BREAKING with per-date magnitude table; magnitude consistency invariant locked across CHANGELOG / UPGRADING / `LILITH_DEFINITION.md`.
2. **Configurable aspect sets** (Phase 9) — `ketu/aspects/presets.py` with frozen length-14 bool masks (`CLASSICAL`/`TRADITIONAL`/`EXTENDED`) + `resolve_aspect_set` resolver. Default flipped from EXTENDED (14) to CLASSICAL (5) — Kala and downstream adapters must opt-in to EXTENDED. `core.aspects` length-14 contract preserved with sha256 byte fingerprint invariant. Performance: EXTENDED is FASTER than v1.0 baseline (-10.10%).
3. **Houses module** (Phase 10) — `ketu/houses/` subpackage with `SYSTEMS` registry: Placidus (vectorized fixed-point iteration, MAX_ITER=50, NaN propagation at polar), Koch (closed-form ad3 trisection, bit-exact match vs swisseph case 'K'), Porphyry (closed-form, doubles as polar fallback). `HOUSES_DTYPE` structured array (12 cusps + ASC + MC + ARMC + Vertex) + `house_of(planet_lon, cusps)` helper. 96.75% module coverage; max ASC delta 0.858 arcmin vs Swiss Ephemeris over 8 reference charts.
4. **CLI refactor** (Phase 11) — argparse subcommands (`ketu aspects`, `ketu houses`); `--harmonics SPEC` accepts named presets or comma-separated indices (bare-int rejected); resolved-config stderr header (`# Aspect set: classical (5 aspects: Conjunction 0°, …)` and `# House system: placidus`); introspection flags `--list-aspect-sets` and `--list-house-systems`; legacy `display.py:main()` deleted (no `input()` calls anywhere); forward byte-stability regression test for `--harmonics all aspects --date 2000-01-01T12:00:00Z` (sha256 pinned).
5. **PyPI release** (Phase 12) — Version bumped 1.0.0 → 1.1.0; CHANGELOG `[1.1.0] - 2026-05-08` with BREAKING summary + Phase 9 + Phase 11 entries; UPGRADING.md migration recipes for CLI default shift, Kala adapter, Houses module replacement, stderr header; PR #26 rebase-merged to main; tag pushed; OIDC trusted-publish via `publish.yml` (run 25528308313, ~38s); GitHub release with sdist+wheel attached; fresh-venv smoke green.
6. **`sidereal_time()` tightened** to apparent GST (Meeus eq. 12.6 = mean GMST + nutation × cos(eps_mean)) — aligned with Swiss Ephemeris house functions; unblocks polar-boundary regression fence at lat=66.5° ASC error <50″.

### Decisions Made (Outcomes)

- **CLASSICAL as default aspect set** — ✓ Good. Kala opted in to EXTENDED cleanly via `aspects=EXTENDED` parameter.
- **Houses module starts with Placidus + Koch + Porphyry** — ✓ Good. Registry pattern validated; Porphyry doubles as polar fallback.
- **Verify Lilith before fixing** — ✓ Good. Empirical max `|delta|` 179.94° revealed perigee/apogee swap before any code change.
- **Vectorize everything new** — ✓ Good. Phase 9 EXTENDED benchmark FASTER than v1.0 baseline.
- **Plan 11-06 Option A pivot (forward-pin v1.1 instead of v1.0 backward)** — ✓ Good. Pins v1.1 forward, catches future format drift.
- **Test-only `pysweph` extra (AGPL isolation)** — ✓ Good. Empirically verified two-venv isolation.

### Issues Resolved

- Lilith formula was computing perigee, not apogee; corrected at 4 plumbing sites atomically.
- `core.aspects` length-14 contract preserved with sha256 byte-fingerprint invariant test.
- LST/obliquity precision tightened to apparent GST (Meeus eq. 12.6).
- Removed `calculate_house_cusps` placeholder stub (was returning wrong equal-house values).
- Legacy interactive `display.py:main()` deleted; no `input()` calls anywhere in `ketu/`.
- Editable-install dist-info regeneration trap documented for future major bumps.
- Venv shebang relocation drift (`solaris/ketu/` → `ketu/`) worked around via `python -m` pattern.

### Issues Deferred (v1.2 ops debt)

- `interrogate ≥95%` not installed/wired into CI — header reference is aspirational.
- `numpydoc validate` not wired into CI.
- `fr/CHANGELOG.md` does not exist (header reference is aspirational).
- Node.js 20 deprecation warnings on every workflow step (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`) — non-blocking; tracked before September 2026 removal.
- Working-tree stash `pre-release-merge: unrelated phase09/11 plan drift` left as-is — NOT v1.1 scope.

### Technical Debt Incurred

None of significance — all phases verified PASSED at 5/5 or 6/6 success criteria. The v1.2 ops debt above pre-existed v1.1 in most cases and was acknowledged but deliberately deferred.

### Velocity (v1.1)

| Phase                          | Plans | Active Time          | Avg/Plan          |
|--------------------------------|-------|----------------------|-------------------|
| 8. Lilith Verification & Fix   | 5     | ~22m 18s             | ~4m 28s           |
| 9. Configurable Aspects        | 6     | ~44m 58s             | ~7m 30s           |
| 10. Houses Module              | 6     | ~58m 10s             | ~9m 42s           |
| 11. CLI Refactor & Integration | 6     | ~34m 52s             | ~5m 49s           |
| 12. Release Preparation v1.1.0 | 4     | ~20m 26s active (~3h elapsed incl. checkpoints) | ~5m 6s active |
| **Total v1.1**                 | **27**| **~3h 0m active**    | **~6m 40s active**|

**Archive:** Roadmap details in `.planning/milestones/v1.1-ROADMAP.md`. Requirements in `.planning/milestones/v1.1-REQUIREMENTS.md`.

---

## v1.0 Production Stability — Shipped 2026-02-12

**Tag:** `v1.0.0`
**Phases:** 1-7 (incl. decimal Phase 2.1 inserted)
**Plans:** 16
**Tests:** 250 passing, 91% coverage
**Timeline:** Closed 2026-02-12

### v1.0 Delivered

Consolidated v0.4.0 development into a stable production library. Surgical refinement: fixed known bugs (cache precedence, aspect non-determinism, Moon velocity wrap), removed anti-features (chart, icalendar exports), eliminated hidden Pandas dependency, hardened tests to 91% coverage, integrated complex math into the cycle engine, finalized numpydoc-style docstrings + mypy strict mode, and published to PyPI as `ketu==1.0.0` via trusted-publishing OIDC.

### v1.0 Key Accomplishments

1. All CONCERNS.md bugs fixed.
2. Export modules removed (chart, icalendar).
3. Pure NumPy contract (no hidden Pandas dependency).
4. Complex representation integrated into cycle engine; vectorized ResonanceField.
5. 91% test coverage (250 tests, Python 3.10-3.13 in CI); mypy strict mode; numpydoc on all public functions.
6. Published on PyPI as `ketu==1.0.0` via trusted publishing OIDC.

**Archive:** Roadmap details in `.planning/milestones/v1.0-ROADMAP.md`. Requirements in `.planning/milestones/v1.0-REQUIREMENTS.md`.

