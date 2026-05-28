# Milestones

Historical record of shipped versions. Most recent first.

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

