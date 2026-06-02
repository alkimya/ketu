# Ketu

## What This Is

Ketu is a pure-Python astronomical-astrological library for planetary cycle calculations, built for financial analysis. It computes ephemerides, detects aspects (with configurable aspect sets), generates cycle time series, resolves full natal charts (`compute_chart` → `CHART_DTYPE`), calculates astrological houses (six systems: Placidus / Koch / Porphyry / Whole Sign / Equal / Regiomontanus via an extensible registry), and supports relational charts (synastry, midpoint composite), predictive charts (solar + lunar returns, standard or relocated), and an extensible Arabic Parts framework — all on top of a structured-array, ML-interop foundation. NumPy is the only core dependency. Published on PyPI, it feeds the Solaris trading ecosystem (Kala ML, Surya agent) but is designed as a standalone public library.

## Core Value

Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Current State

**Latest shipped:** v1.3.0 (PyPI 2026-06-01) — <https://pypi.org/project/ketu/1.3.0/>

v1.3 embedded Chiron as the 14th body (Chebyshev-by-segment coefficients in an embedded `.npz`, evaluated by a pure-NumPy runtime — zero swisseph), after hardening the ephemeris engine (per-body strategies replacing the `calc_planet_position` if-elif, split `orbital.py`, consolidated fixtures) and lifting project coverage to 100%. The aspect engine became data-driven (one declarative `Aspect` table the engine iterates over; `aspects_for_harmonics` for harmonic-based selection; library default = TRADITIONAL 7 half-circle aspects). Sphinx docs (en+fr) were brought to the full v1.1/v1.2/v1.3 surface — 17 `.po` catalogs 100% translated. The 13→14 body shift deliberately broke the frozen-body-count ratchet and the internal Ketu↔Kala positional contract (Kala adapts). 1399 tests; mypy `--strict` clean; runtime stays pure NumPy (`pyswisseph` test/build-only).

## Current Milestone: v1.4 Dynamic Harmonics & Chiron Range

**Goal:** Make aspect harmonics open-ended — any integer harmonic (H17, etc.) usable as a first-class aspect across the whole detection chain via an on-the-fly generator, without disturbing the frozen `core.aspects` table or its preset fingerprints — then widen Chiron's validity range to 1900–2100, correct its orb to 4° (Pluto parity), recentre the documentation on the 180°-division default (H1/H2/H3/H6), and ship `ketu==1.4.0`.

**Target features (ordered intent — phases set by roadmap):**

1. **Dynamic harmonics** (engine) — an on-the-fly aspect generator: any integer `h` yields its aspect angles (`360/h × k`) and harmonic coefficient (`1/h`) as first-class aspects, integrated through the full detection chain (`calculate_aspects`, orbs, cycles, synastry). The frozen 14-aspect `core.aspects` table, the named presets, and their sha256 fingerprints are PRESERVED — the dynamic path is additive, not a replacement. No reference to Kala anywhere in Ketu docs.
2. **Chiron range 1900–2100** (data) — regenerate `ketu/data/chiron_coeffs.npz` over 1900–2100 (vs current 1950–2050) via the offline `tools/gen_chiron_coeffs.py` build-only generator; re-validate accuracy < 0.01° on the widened range; re-pin regression references. Runtime unchanged (pure-NumPy eval), only embedded data + clamp bounds.
3. **Chiron orb 0°→4°** (behaviour) — align `core.bodies['orb']` for Chiron to 4° (astrological intent; Pluto parity). Propagates through the single-source orb derivation to aspect detection; regenerate the byte-stable CLI fixture (`tests/cli/fixtures/v1_1_reference_output.txt`) and adjust synastry orb-mirroring asserts. CHANGELOG `Changed`/`Fixed`.
4. **Documentation coherence** (docs) — recentre `concepts.md` on the 180°-division default (H1/H2/H3/H6); tables show only CLASSICAL(5)/TRADITIONAL(7) and mark default vs opt-in; move EXTENDED (H5/H9/H10) out of the tables (kept in code); document the dynamic-harmonics generator + Chiron 1900–2100 + orb 4°; fix `migration.md` (default = TRADITIONAL, not "EXTENDED=14 unchanged") and `relational_charts.md` (default = TRADITIONAL, not "classical"); recompile touched fr `.po`/`.mo`.
5. **Release 1.4.0** (ceremony) — version bump, CHANGELOG `[1.4.0]` (Added: dynamic harmonics, Chiron 1900–2100; Changed: Chiron orb 4°, docs), push **main + tag**, GitHub release + PyPI via OIDC.

**Versioning note:** v1.4.0 is a **minor** (not a patch). It adds a new public capability (open-ended harmonics) and widens Chiron's validity range — both additive. The frozen `core.aspects` table and preset fingerprints stay intact; the dynamic generator is a parallel path. The Chiron orb change (0°→4°) is a behaviour change in aspect detection, documented in CHANGELOG. (The originally-scoped "v1.3.1 docs patch" was absorbed here once dynamic harmonics + Chiron range made the scope a minor, not a patch.)

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

**v0.x foundations (validated by v1.0):**

- ✓ Pure NumPy ephemeris engine (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu/Ketu, Lilith) — v0.3.0
- ✓ Batch position calculation (`calc_planet_position_batch`) — v0.3.0
- ✓ 14-aspect detection system (conjunction through undecile) — v0.4.0
- ✓ Aspect window detection (entry/exact/exit timing via binary search) — v0.4.0
- ✓ Cycle time series generation (`generate_cycle_series`, `generate_multi_cycle_series`) — v0.4.0
- ✓ CYCLE_DTYPE structured array format for ML interop — v0.4.0
- ✓ Complex number representation (`complex.py`) with ML feature extraction — v0.4.0
- ✓ Vectorized aspect calculation path — v0.4.0
- ✓ Ephemeris cache system for O(1) lookups — v0.4.0
- ✓ Lunar calendar generation — v0.4.0
- ✓ CLI entry point (`ketu` command) — v0.1.0
- ✓ LRU caching for repeated calculations — v0.2.0
- ✓ Transit calculations vs natal positions — v0.4.0
- ✓ Aspect timelines (ML-ready structured arrays) — v0.4.0

**v1.0 stability:**

- ✓ All CONCERNS.md bugs fixed (cache precedence, aspect non-determinism, Moon velocity wrap) — v1.0.0
- ✓ Export modules removed (chart, icalendar) — v1.0.0
- ✓ Pure NumPy contract (no hidden Pandas) — v1.0.0
- ✓ Complex representation integrated into cycle engine, vectorized ResonanceField — v1.0.0
- ✓ 91% test coverage (250 tests, Python 3.10-3.13 in CI) — v1.0.0
- ✓ Numpydoc-style docstrings on all public functions, mypy strict mode — v1.0.0
- ✓ Published on PyPI as `ketu==1.0.0` with trusted publishing OIDC — v1.0.0

**v1.1 flexibility & houses:**

- ✓ Default aspect set is 5 majors (CLASSICAL); opt-in TRADITIONAL (7) / EXTENDED (14); backward compat via `--harmonics extended` — v1.1.0
- ✓ CLI flag `--harmonics SPEC` (preset name OR `9,10,11` index list); bare-int rejected with clear error — v1.1.0
- ✓ Python API accepts named presets (`CLASSICAL`/`TRADITIONAL`/`EXTENDED`) and explicit lists/masks via `aspects=` — v1.1.0
- ✓ `core.aspects` length-14 append-only invariant pinned by sha256 byte fingerprint — v1.1.0
- ✓ Argparse CLI with subcommands (`ketu aspects`, `ketu houses`); legacy `input()` prompt deleted — v1.1.0 (CLI-01)
- ✓ Houses module with extensible registry (`SYSTEMS = {"placidus", "koch", "porphyry"}`) — v1.1.0
- ✓ Placidus implementation (vectorized, MAX_ITER=50, NaN propagation at polar) — v1.1.0
- ✓ Koch implementation (closed-form ad3 trisection; bit-exact match vs swisseph case 'K') — v1.1.0
- ✓ Porphyry implementation (closed-form, doubles as polar fallback) — v1.1.0
- ✓ `house_of(planet_lon, cusps)` helper — v1.1.0 (vectorized)
- ✓ `ketu houses --date ISO --lat F --lon F --system {placidus,koch,porphyry}` CLI subcommand — v1.1.0
- ✓ Resolved-config stderr header (`# Aspect set: ...`, `# House system: ...`) — v1.1.0 (CLI-06)
- ✓ Introspection flags `--list-aspect-sets` / `--list-house-systems` — v1.1.0 (CLI-05)
- ✓ Lilith verified vs Swiss Ephemeris (5+ dates 1900-2050); FORMULA-CORRECTION applied — v1.1.0
- ✓ Lilith regression tests pinning post-fix values; max |delta| 0.002693° on plan dates, 0.007815° over 55K daily samples — v1.1.0
- ✓ `pysweph>=2.10.3.6` as test-only optional dependency (AGPL non-contamination of runtime) — v1.1.0 (LIL-04)
- ✓ CHANGELOG and UPGRADING.md document Lilith correction with magnitude consistency invariant — v1.1.0
- ✓ Removed `calculate_house_cusps` placeholder stub from `ephemeris/planets.py` — v1.1.0 (HOU-10, BREAKING)
- ✓ `sidereal_time()` tightened to apparent GST (Meeus eq. 12.6) — v1.1.0 (HOU-01)
- ✓ Houses module ≥95% coverage gate (achieved 96.75%) with 10 reference charts × 3 systems vs Swiss Ephemeris (incl. polar lats 70°/80°) — v1.1.0
- ✓ Aspect benchmark: EXTENDED is FASTER than v1.0 baseline (-10.10%) — v1.1.0 (ASP-08 over-delivered)
- ✓ Forward byte-stability regression test for `--harmonics all aspects --date 2000-01-01T12:00:00Z` (sha256 pinned) — v1.1.0 (CLI-03 Option A)
- ✓ Bumped version to 1.1.0, GitHub release, PyPI publish via OIDC — v1.1.0

**v1.2 relational & predictive astrology** (full requirements archived in `.planning/milestones/v1.2-REQUIREMENTS.md`):

- ✓ Chart abstraction: `ketu/charts/` with frozen `CHART_DTYPE`, one-call `compute_chart(jd, lat, lon, system, aspects)` (scalar + array `jd`), `is_day_chart` (ASC-delta sunrise-inclusive) — v1.2.0 (CHART-01..05, 100% coverage)
- ✓ Three new house systems via `SYSTEMS` registry: Whole Sign, Equal, Regiomontanus (Whole Sign + Equal polar-safe); six total; `--list-house-systems` lists all six — v1.2.0 (HOU2-01..05)
- ✓ Synastry: `calculate_synastry(chart_a, chart_b)` → `SYNASTRY_DTYPE` (chart-of-origin preserved), dense + filtered modes, synastry-tightened orbs distinct from natal; 3 hand-validated oracle couples — v1.2.0 (SYN-01..05)
- ✓ Composite (midpoint): `calculate_composite(chart_a, chart_b)` → `CHART_DTYPE`, `circular_midpoint` (`mid(359°, 1°) == 0.0` pinned), composite houses from composite ASC/MC — v1.2.0 (COMP-01..05, 100% coverage)
- ✓ Solar + Lunar Returns: `solar_return` (target_year) + `lunar_return` (target_jd, first return ≥ target) sharing one pure-NumPy `_solve_return` core with central wrap handling, arc-second convergence, standard + relocated — v1.2.0 (RET-01..06, LRET-01..05, 100% coverage)
- ✓ Arabic Parts framework: `ketu/parts/` extensible registry, sect-aware `calculate_part` (Fortune/Spirit invert day/night) + fixed Marriage, `calculate_all_parts`, `--list-parts` CLI — v1.2.0 (PARTS-01..08, 100% coverage)
- ✓ Ops debt retired: `interrogate ≥95%` + `numpydoc validate` BLOCKING in CI; workflows on Node 24; `ketu==1.2.0` published via OIDC with GitHub release — v1.2.0 (OPS-01..05)

### Active

<!-- v1.4 Dynamic Harmonics & Chiron Range — scoped 2026-06-02. Building toward these. -->

- [ ] On-the-fly aspect generator: any integer harmonic `h` → angles `360/h × k` + coefficient `1/h`
- [ ] Dynamic aspects integrated through the full detection chain (`calculate_aspects`, orbs, cycles, synastry)
- [ ] Frozen `core.aspects` table, named presets, and sha256 fingerprints PRESERVED (dynamic path additive)
- [ ] Regenerate `chiron_coeffs.npz` over 1900–2100; re-validate accuracy < 0.01°; re-pin regression refs
- [ ] Chiron orb 0°→4° (Pluto parity); regenerate CLI byte-stable fixture + synastry orb asserts
- [ ] Recentre `concepts.md` on 180°-division default (H1/H2/H3/H6); tables show CLASSICAL(5)/TRADITIONAL(7) only, mark default vs opt-in; EXTENDED out of tables
- [ ] Fix `migration.md` (default = TRADITIONAL) and `relational_charts.md` (default = TRADITIONAL, not "classical")
- [ ] Document dynamic-harmonics generator + Chiron 1900–2100 + orb 4°; recompile touched fr `.po`/`.mo`
- [ ] Ship `ketu==1.4.0` (push main + tag, GitHub release + PyPI via OIDC)

### Out of Scope

<!-- Explicit boundaries (audited at v1.2 close). -->

- True/Osculating Lilith (h13) — defer; Mean Lilith is de-facto standard in 95% of astrology software
- Asteroid Lilith #1181 — defer; different body, separate effort
- Davison composite — defer beyond v1.3; v1.2 shipped midpoint composite only; v1.3 focuses on Chiron + engine hardening
- Campanus / Topocentric / Alcabitius houses — registry supports them; ship concretes if user demand surfaces (Whole Sign / Equal / Regiomontanus shipped in v1.2)
- Any body beyond Chiron (centaurs, asteroids, fixed stars) — no additional bodies planned; pure-NumPy contract holds and Chiron is the single deliberate addition. Future bodies are a separately-scoped decision, not a standing candidate list
- 5 remaining Hermetic Lots (Eros, Necessity, Courage, Victory, Nemesis) — defer beyond v1.3; competing tradition variants; v1.2 registry absorbs them additively
- Progressions / directions — defer; predictive techniques distinct from transits (already shipped, v0.4.0) and from the return-chart solver
- Timezone handling inside Ketu — UTC remains required; timezone conversion is caller's responsibility
- `pyswisseph` as runtime dependency — test-only only; license (AGPL) and brand promise (NumPy-only) prevent runtime
- scipy / other runtime deps — pure-NumPy contract non-negotiable; bespoke NumPy bisection used for returns
- Chart/SVG visualization — still removed, deferred to post-Ketu GUI tooling
- iCalendar export — still removed, deferred to post-Ketu GUI tooling
- Real-time streaming calculations — still batch-oriented
- Web API — Ketu is a library, not a service
- `click` / `typer` CLI dependencies — argparse stdlib was sufficient; no new runtime deps
- Bare `--harmonics 12` integer parsing — too ambiguous; forced named presets or explicit list

## Context

**v1.2.0 shipped on PyPI on 2026-05-28** — relational + predictive framework on a non-breaking minor: chart abstraction (`CHART_DTYPE` / `compute_chart` / `is_day_chart`), three new house systems (six total), synastry, midpoint composite, solar + lunar returns (shared `_solve_return`), Arabic Parts framework. All v1.1 ops debt retired (doc gates BLOCKING, Node 24 workflows). 1286 tests collected; 100% coverage on every new subpackage; runtime stays pure NumPy (`pyswisseph` test-only). LOC: ~34.2k Python (ketu/ + tests/).

**Tag `v1.2.0`** points at commit `d775663`. PyPI: <https://pypi.org/project/ketu/1.2.0/>. GitHub release (sdist + wheel): <https://github.com/alkimya/ketu/releases/tag/v1.2.0>. Published via OIDC trusted publishing (`publish.yml` run 26602811661, ~33s); fresh-venv `pip install ketu==1.2.0` smoke-imports all 5 new subpackages cleanly.

**v1.2 ops debt — RESOLVED:**

- ✓ `interrogate ≥95%` installed and BLOCKING in CI (Phase 13 wired, Phase 20 confirmed blocking)
- ✓ `numpydoc validate` BLOCKING in CI on public modules (flipped from warning-only at milestone close, Phase 20)
- ✓ `fr/CHANGELOG.md` decision finalized (Phase 20)
- ✓ Node 20 deprecation warnings eliminated — workflows on Node 24 (`actions/checkout@v5`, `setup-python@v6`, `upload-artifact@v5`)

**Carried-forward note:**

- Venv shebangs were hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` after the project relocated to `ketu/`. **RESOLVED 2026-05-30**: all 59 `venv/bin/*` shebangs rewritten to the current `/home/loc/workspace/ketu/venv/bin/python3` (+ cosmetic `pyvenv.cfg` path); wrappers (`sphinx-build`, `sphinx-intl`, `pytest`, `mypy`, `pip`) now run directly. The `python -m` invocation is no longer required (still works, but optional).

**Ephemeris-theory note (from Phase 18):** Ketu's bespoke TRUE Sun theory diverges from Swiss Ephemeris Moshier by up to ~56 arcsec on multi-decade back-projections, and the truncated-Meeus Moon theory by up to ~0.61° in longitude. The returns oracle uses self-consistency at 0.0001° as the PRIMARY gate; the pyswisseph cross-check is test-only with per-body tolerances reflecting these measured deltas. This is a known accuracy boundary, not a bug.

**Downstream impact:**

- Kala (`solaris/kala`) — v1.2 is additive; no breaking changes. The v1.1 `aspects=EXTENDED` opt-in note still applies for v1.0 behavior parity.

## Constraints

- **Dependency:** NumPy only as core dependency — no new runtime deps (pysweph is test-only)
- **Compatibility:** Python 3.10+ (tested 3.10-3.13)
- **Performance:** All new calculations must be vectorizable over date arrays (no Python loops in hot paths)
- **API stability:** Backward compat reachable via flag (`--harmonics extended` for legacy 14-aspect CLI default; `aspects=EXTENDED` Python API)
- **Testing:** Maintain ≥90% project coverage, ≥85% per module, ≥95% on new modules
- **Time inputs:** UTC only — no timezone handling inside Ketu
- **Release:** Full GitHub release + PyPI publish via OIDC

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Remove all export modules | Pure calculation library — exports belong in future GUI layer | ✓ Good (v1.0) |
| Complex math internal, degrees external | Complex numbers better for computation, degrees better for humans | ✓ Good (v1.0) |
| Fix all CONCERNS.md bugs | Clean slate for 1.0 — no known bugs at release | ✓ Good (v1.0) |
| Remove Pandas dependency | Keep NumPy-only contract, use structured arrays instead | ✓ Good (v1.0) |
| Breaking API changes OK for 1.0 | Major version bump justifies cleanup | ✓ Good (v1.0) |
| Default aspects = 5 majors (CLASSICAL) in v1.1 | Pro/classical default; ML harmonics opt-in via `--harmonics` | ✓ Good (v1.1) — Kala opted in to EXTENDED cleanly |
| Houses module starts with Placidus + Koch + Porphyry | Three systems prove extensibility; Porphyry doubles as polar fallback | ✓ Good (v1.1) — registry pattern validated |
| Verify Lilith before fixing | Confirm bug exists and quantify error before changing formula | ✓ Good (v1.1) — empirical max abs delta 179.94° revealed perigee/apogee swap |
| Vectorize everything new | Houses + harmonics must be batchable over date arrays | ✓ Good (v1.1) — EXTENDED benchmark FASTER than v1.0 baseline |
| Plan 11-06 Option A pivot (forward-pin v1.1 instead of v1.0 backward) | Phases 8 + 9 deliberately broke v1.0 byte-identity; backward contract was already lost in reality | ✓ Good (v1.1) — pins v1.1 forward, catches future format drift |
| Test-only `pysweph` extra (AGPL isolation) | License + brand promise (NumPy-only runtime) prevent AGPL contamination of runtime wheel | ✓ Good (v1.1) — empirically verified two-venv isolation |
| Apparent GST (Meeus eq. 12.6) for `sidereal_time()` | Aligns with Swiss Ephemeris house functions; <1 arcmin ASC error gate met | ✓ Good (v1.1) |
| Magnitude consistency invariant across CHANGELOG / UPGRADING / LILITH_DEFINITION | Single source of truth for documented magnitudes; same numbers, same precision, three docs | ✓ Good (v1.1) |
| v1.2 framing = non-breaking minor strict | v1.1 burned the BREAKING quota (Lilith / CLI default / `calculate_house_cusps`); v1.2 must be additive only | ✓ Good (v1.2) — shipped fully additive, no default change, no export removed |
| `Chart` abstraction = Option A (`CHART_DTYPE` structured array) | Cohérent avec CYCLE_DTYPE / HOUSES_DTYPE existants ; ML-interop NumPy-first ; batchable | ✓ Good (v1.2) — reused unchanged by synastry / composite / returns |
| Composite chart = midpoint variant only | Standard universel ; Davison reportable v1.3 si demande surface | ✓ Good (v1.2) — Davison cleanly deferred to v1.3 |
| Solar return = standard + relocated | Relocation quasi gratuite si l'abstraction Chart est correcte ; très utilisée en pratique moderne | ✓ Good (v1.2) — relocation contract shared with lunar return |
| Arabic Parts = framework + 7 Hermetic Lots + Marriage | Framework cost fixe (registry) ; marginal cost par Part ~5 lignes ; Marriage = synergie synastry | ⚠️ Revisit (v1.2) — scope reduced to 3 (Fortune/Spirit/Marriage); 5 Lots had competing tradition variants, deferred to v1.3; registry absorbs them additively |
| Tier 3 ordering = doc gates early, workflows late | Doc gates touchent tout le code suivant ; workflow refresh isolé en fin de milestone | ✓ Good (v1.2) — doc gates landed Phase 13, flipped blocking Phase 20 |
| Lunar return pulled INTO v1.2 (was "defer post-solar") | `_solve_return` generalized cleanly across Sun and Moon; marginal cost was a seed-cycle search, not a new solver | ✓ Good (v1.2) — LRET-01..05 + RET-06 added mid-milestone; shared core held |
| Single shared `_solve_return` for solar + lunar (grep-ratchet enforced) | One root-finder, central 360°→0° wrap handling; no inline bisection in either public API | ✓ Good (v1.2) — Phase 18 Success Criterion #3 binding |
| Returns oracle: self-consistency at 0.0001° PRIMARY, pyswisseph cross-check test-only with per-body tolerance | Surfaces a genuine ephemeris-theory gap (Ketu TRUE Sun + truncated-Meeus Moon vs Swiss Moshier ELP) rather than masking it; runtime stays pure NumPy | ✓ Good (v1.2) — measured deltas documented in fixtures + NOTES |
| `is_day_chart` via ASC-delta (not horizon altitude) | Consistent with the ASC stored in the same `CHART_DTYPE` | ✓ Good (v1.2) |
| v1.3 stays `1.3.0` despite breaking the 13→14 body freeze | Ketu is the source-of-truth library; Kala adapts to Ketu, not vice-versa. Public Ketu API stays additive; the broken contract is the internal Ketu↔Kala positional array | — Pending (v1.3) |
| Chiron via embedded Chebyshev coeffs, NOT swisseph runtime | Preserves pure-NumPy runtime + AGPL isolation; offline pyswisseph generator is build-only → `.npz` in package, eval is 100% NumPy | — Pending (v1.3) |
| Refactor ephemeris BEFORE adding Chiron | Chiron adds a branch to the fragile `calc_planet_position` if-elif; refactoring first makes Chiron a clean strategy, not aggravated debt | — Pending (v1.3) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

Last updated: 2026-06-02 — milestone v1.4 (Dynamic Harmonics & Chiron Range) started.
