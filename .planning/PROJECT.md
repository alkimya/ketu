# Ketu

## What This Is

Ketu is a pure-Python astronomical-astrological library for planetary cycle calculations, built for financial analysis. It computes ephemerides, detects aspects (with configurable aspect sets), generates cycle time series, resolves full natal charts (`compute_chart` → `CHART_DTYPE`), calculates astrological houses (six systems: Placidus / Koch / Porphyry / Whole Sign / Equal / Regiomontanus via an extensible registry), and supports relational charts (synastry, midpoint composite), predictive charts (solar + lunar returns, standard or relocated), and an extensible Arabic Parts framework — all on top of a structured-array, ML-interop foundation. NumPy is the only core dependency. Published on PyPI, it feeds the Solaris trading ecosystem (Kala ML, Surya agent) but is designed as a standalone public library.

## Core Value

Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Current State

**Latest shipped:** v1.6.0 (PyPI 2026-06-04) — <https://pypi.org/project/ketu/1.6.0/>

v1.6 added the additive `ketu.declination` subpackage — detection of **parallel** and **contra-parallel** aspects on the equatorial declination axis (δ), the last lightweight Ketu engine milestone before the Rahu UI project. Two pure-NumPy public functions: `find_declination_aspects(body_decl)` (scalar/single-chart detector over the `(14,)` `chart["body_decl"]` array → a `DECLA_ASPECT_DTYPE` structured array of upper-triangle P/CP pairs; `np.empty(0, …)` when none, never `None`) and `declination_aspect_masks(body_decl)` (vectorized batch path `(S,14)`→`DeclinationAspectMasks` NamedTuple of `(S,91)` masks, pure broadcasting, no Python body loop). Orbs are body-derived: `max((orb_b1+orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` with `DECLA_COEF=1/12` (Sun/Moon = exactly 1.0°) and `MIN_DECL_ORB=0.5°` (floor so zero-orb bodies stay detectable). Documented en + fr (signed-δ definitions, same-hemisphere rule, orb formula, biodynamic framing parallel ≈ conjunction / contra ≈ opposition, the parallel ≠ longitude-conjunction distinction, P/CP symbols). All ADDITIVE: `CHART_DTYPE` byte-identical (companion function, not a dtype field — no ratchet break), the frozen 14-row `core.aspects` table + V1/V13 fingerprints unchanged, and the new names are reachable only via `ketu.declination.*` (not `ketu.__all__`). 1654 tests; 100% coverage; mypy `--strict` clean; runtime stays pure NumPy (`pyswisseph` test/build-only).

**Prior:** v1.5.0 (2026-06-04) promoted equatorial declination δ to a first-class, vectorizable quantity — `declination` / `declination_velocity` / `is_ascending_declination` (biodynamic montant/descendant) / `is_out_of_bounds` in `ketu.calculations`, a `body_decl` field added to `CHART_DTYPE`, plus the dynamic-harmonics debt paid down (`H{h}-{k}` naming contract, `find_aspect_timing` `dyn_coef=`, CLI `--harmonics h7`). v1.4.0 (2026-06-03) made aspect harmonics open-ended — `generate_harmonic_aspects(h)` for ANY integer harmonic wired through the full detection chain via `dynamic_specs=`, the frozen `core.aspects` table + fingerprints byte-identical; Chiron range widened to 1900–2100 and its orb corrected 0°→4°; docs (en+fr) recentred on the 180°-division default. v1.3.0 (2026-06-01) embedded Chiron as the 14th body (Chebyshev `.npz`, pure-NumPy runtime), hardened the engine to 100% coverage, and made the aspect engine data-driven (default = TRADITIONAL 7). The 13→14 body shift deliberately broke the frozen-body-count ratchet and the internal Ketu↔Kala positional contract (Kala adapts).

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

**v1.3 Chiron & engine hardening** (full requirements archived in `.planning/milestones/v1.3-REQUIREMENTS.md`):

- ✓ Chiron embedded as the 14th body (`body_id=13`) via Chebyshev-by-segment coefficients in an embedded `.npz`, evaluated by a pure-NumPy runtime (zero swisseph under `ketu/`); 6 insertion points via `BODY_STRATEGIES` with no special-casing — v1.3.0 (CHIR-01..05)
- ✓ Ephemeris engine hardened: `calc_planet_position` if-elif replaced by per-body `BODY_STRATEGIES`; `orbital.py` split; fixtures consolidated; project coverage lifted to 100% (`fail_under=100`, zero pragma) + 52 doctests + `make doctest` gate — v1.3.0
- ✓ Aspect engine data-driven: one declarative `Aspect` table the engine iterates over; `aspects_for_harmonics` for harmonic selection; library default = TRADITIONAL (7 half-circle aspects) — v1.3.0
- ✓ Sphinx docs (en+fr) brought to full v1.1/v1.2/v1.3 surface — 17 `.po` catalogs / 1405 messages 100% translated — v1.3.0
- ✓ `ketu==1.3.0` published on PyPI via OIDC; the 13→14 body shift broke the frozen-body-count ratchet + internal Ketu↔Kala positional contract (Kala adapts) — v1.3.0

**v1.4 Dynamic Harmonics & Chiron Range** (full requirements archived in `.planning/milestones/v1.4-REQUIREMENTS.md`):

- ✓ On-the-fly aspect generator `generate_harmonic_aspects(h)`: any integer harmonic `h` → angles `fold_to_0_180(k·360/h)` + coefficient `k/h`, mirror pairs deduplicated, 0°/360° never emitted — v1.4.0 (ASP-04, ASP-05)
- ✓ Dynamic aspects integrated through the full detection chain via `dynamic_specs=` (`calculate_aspects` scalar/vectorized/batch with `i_asp=-2`, cycles, synastry); off-table angles guarded against `IndexError` (synthetic name) — v1.4.0 (ASP-06, ASP-07, ASP-09)
- ✓ Frozen `core.aspects` table, named presets, and sha256 fingerprints PRESERVED (dynamic path additive); `_VALID_HARMONICS` never gates it — v1.4.0 (ASP-08)
- ✓ `chiron_coeffs.npz` regenerated over 1900–2100 (2283 segments) with a blocking pre-commit spike (degree=10 held, max|Δλ|=0.001214°, 8.2× margin); regression refs re-pinned with pre-1950 + post-2050 wings; out-of-range clamps (not `ValueError`) — v1.4.0 (CHIR-09, CHIR-10, CHIR-11)
- ✓ Chiron orb 0°→4° (Pluto parity, single-source `core.bodies['orb']`); CLI byte-stable fixture regenerated + audited; synastry orb asserts + pinning test — v1.4.0 (CHIR-06, CHIR-07, CHIR-08)
- ✓ Docs recentred on the 180°-division default; EXTENDED out of tables (kept in code); stale EXTENDED/classical default claims removed; `generate_harmonic_aspects` + Chiron 1900–2100/orb-4° documented; full fr gettext cycle (7 catalogs, 0 untranslated); en+fr build at the 1-warning baseline — v1.4.0 (DOC-14..17)
- ✓ `ketu==1.4.0` shipped to PyPI via OIDC (push main + tag); post-publish fresh-venv smoke 4/4 (dynamic generator, Chiron orb 4°, 1900–2100 range, no `pyswisseph` at runtime) — v1.4.0 (REL-12, REL-13)

**v1.5 Lunar Declination & Harmonics Debt** (full requirements archived in `.planning/milestones/v1.5-REQUIREMENTS.md`):

- ✓ Equatorial declination δ as a first-class quantity: `declination(jdate, body)` (degrees [−90,+90], scalar + vectorized via the `coordinates.py` chain, Meeus 13.4 equivalent), `declination_velocity` (dδ/dt °/day, `lat_velocity` finite-difference idiom), pinned to Δ = 0 vs the rectangular chain — v1.5.0 (DECL-01..04)
- ✓ Biodynamic montant/descendant `is_ascending_declination` (True when dδ/dt > 0) — distinct from and parallel to the UNCHANGED β-based `is_ascending`; out-of-bounds `is_out_of_bounds` via instantaneous obliquity ε(jd) (`true_obliquity`) — v1.5.0 (DECL-05, DECL-06)
- ✓ `body_decl` field added to `CHART_DTYPE` (14 bodies, f8, additive, mirrors `body_lats`); populated by `compute_chart`, inherited by synastry / composite / returns (composite δ from the coordinates chain on composite λ,β, not parent-midpoint); dtype-layout ratchet test; Kala positional impact documented — v1.5.0 (DECL-07, DECL-08)
- ✓ Declination documented en + fr — the 4 functions + aspect-centric montant/descendant framing (~27.21 d draconic cycle, OOB nodal cycle) + explicit β-vs-δ distinction — v1.5.0 (DECL-09)
- ✓ `H{h}-{k}` synthetic off-table aspect naming pinned as a documented public API contract (TestNamingContractF2 + generator docstring); GENERATOR-vs-DETECTION two-channel distinction documented (DETECTION stays static-first: 120° → Trine, never H3-1) — v1.5.0 (HARM-01..03)
- ✓ `find_aspect_timing` gained `dyn_coef: Optional[float] = None` orb derivation (`(orb[b1]+orb[b2])/2 * dyn_coef`); static path + explicit `orb=` escape hatch byte-identical; explicit `orb` wins silently when both given — v1.5.0 (HARM-04, HARM-05)
- ✓ CLI `--harmonics h7` (h-prefixed, Tight grammar) via `HarmonicsSelection` NamedTuple clean under mypy `--strict`; Quadrinovile display bug fixed; new h7 byte-stability fixture audited, v1.1 fixture UNCHANGED; documented en + fr — v1.5.0 (HARM-06..09)
- ✓ `ketu==1.5.0` shipped to PyPI via OIDC (push main + tag); user go/no-go honoured before publish; post-publish fresh-venv smoke 4/4 (declination, montant/descendant, OOB, `--harmonics h7`, no `pyswisseph` at runtime) — v1.5.0 (REL-01..03)

**v1.6 Declination Aspects** (full requirements archived in `.planning/milestones/v1.6-REQUIREMENTS.md`):

- ✓ Parallel detection (`kind="P"`): same non-zero-sign declination within orb (`sign(δ₁)==sign(δ₂)≠0 ∧ |δ₁−δ₂|≤orb`); bodies at δ=0° form no parallel (zero-sign trap guarded) — v1.6.0 (DECLA-01)
- ✓ Contra-parallel detection (`kind="CP"`): opposite-sign mirrored declination within orb (`sign(δ₁)≠sign(δ₂) ∧ both≠0 ∧ |δ₁+δ₂|≤orb`) — v1.6.0 (DECLA-02)
- ✓ Body-derived δ orb `max((orb_b1+orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` with `DECLA_COEF=1/12` (Sun/Moon=1.0°) and `MIN_DECL_ORB=0.5°` floor (Rahu/Lilith stay detectable); frozen 14×14 `_ORB_MAT` — v1.6.0 (DECLA-03)
- ✓ Companion function `find_declination_aspects(body_decl)` → `DECLA_ASPECT_DTYPE` (5 fields: body1/body2 i1, kind U2, gap/orb f8), upper-triangle sorted, empty=`np.empty(0,…)`; vectorizable batch `declination_aspect_masks((S,14))→(S,91)` `DeclinationAspectMasks` NamedTuple, no Python body loop; `CHART_DTYPE` UNCHANGED (additive, no ratchet break) — v1.6.0 (DECLA-04)
- ✓ Documented en + fr: signed-δ definitions + same-hemisphere rule, body-derived orb formula (Sun/Moon=1.0°), aspect-centric biodynamic framing (parallel ≈ conjunction / contra ≈ opposition on δ), parallel ≠ longitude-conjunction distinction, `//`/`#` + `P`/`CP` symbols, OOB-interaction note; FR `.mo` recompiled (no English fallback) — v1.6.0 (DECLA-05)
- ✓ `ketu==1.6.0` shipped to PyPI via OIDC (push main + tag); user go/no-go honoured before publish; post-publish fresh-venv smoke FROM PyPI green (find_declination_aspects detects ≥1 parallel, dtype == DECLA_ASPECT_DTYPE, no `pyswisseph` at runtime) — v1.6.0

## Current Milestone: v1.7 Fictitious-Point Orbs

**Goal:** Give Rahu, Ketu, and Lilith a non-zero orb (0°→2°) so the fictitious points actually enter aspect — unblocking a Rahu (frontend) need — while filtering out the tautological Rahu↔Ketu opposition.

**Target features:**
- Orb 0°→2° on Rahu (10), Ketu (11), Lilith (12) in `ketu/core.py` `bodies` table; everything inherits data-driven (`get_orb`, `synastry_orb_limit` read the table). Point↔point conjunction = 2°; point↔planet (e.g. Sun 12°) = 7°.
- Targeted filter of the `(Rahu, Ketu)` pair AND `Opposition` aspect SIMULTANEOUSLY in the aspect engine — tautological (Ketu = South Node, exact 180° opposite of Rahu by construction); pollutes the reading once the orb is non-zero. Rahu and Ketu stay FULLY active for all their other aspects.
- Synastry IN SCOPE: the points inherit the new orb everywhere; `orb=0` oracles rewritten + full regression sweep (~40 test files reference the points).
- `ketu==1.7.0` shipped to PyPI via OIDC; user go/no-go relecture-validation before publish.

**Why MINOR (1.7.0), not patch 1.6.1:** the change alters aspect RESULTS for every consumer (Kala included) — new aspects appear. orb=0 was an intentional modelling decision (Abu Ma'shar / Al-Biruni, fictitious points with no orb, frozen in the oracles), not a bug. A patch would tell Kala a `pip install -U` is safe while it silently shifts its node calculations. Kala adapts post-release (Ketu is source-of-truth) — not a blocker.

**After v1.7:** the **Rahu** UI project (separate repo `~/workspace/rahu`, consumes `ketu` from PyPI, FastAPI + SvelteKit + D3/SVG). v1.7 was triggered by a Rahu need: with orb=0 the points never form aspects, so the frontend would render an empty node/Lilith aspect grid. No further bodies, houses, or parts are planned for the Ketu engine. A Rust rewrite stays explicitly rejected.

### Active

<!-- v1.7 requirements (full list in .planning/REQUIREMENTS.md). -->

- **ORB-01** — Rahu/Ketu/Lilith orb 0°→2° in `core.bodies` (single-source; all consumers inherit)
- **ORB-02** — Targeted filter: suppress ONLY the `(Rahu, Ketu)` + `Opposition` detection (both conditions), keep all other point aspects active
- **ORB-03** — Synastry oracles rewritten for the new orb; full regression sweep over point-referencing tests green
- **ORB-04** — Docs (en + fr) updated: new 2° point orb, the Rahu↔Ketu opposition filter rationale, the MINOR-not-patch Kala note
- **REL-01** — `ketu==1.7.0` shipped to PyPI via OIDC (push main + tag), human go/no-go honoured, post-publish fresh-venv smoke green

**Deferred (future candidates, not committed):**

- **HARMF-01** — Rich `--harmonics` CLI grammar: multi-harmonic (`h7,h11`) and preset+harmonic mixing (`traditional,h7`). v1.5 shipped only the Tight single-token form; v1.6 stayed DECLA-only. Remains a future candidate.
- **Declination synastry / dedicated CLI surface** — v1.6 shipped in-orb detection only (no applying/timing/synastry/CLI for declination aspects). Natural follow-ups if demand surfaces.

### Out of Scope

<!-- Explicit boundaries (audited at v1.2 close; declination scope tranché at v1.5 open). -->

- ✓ SHIPPED v1.6 (was here as a candidate): Declination aspects (parallels / contra-parallels) — the `ketu.declination` subpackage (`find_declination_aspects` + `declination_aspect_masks`), body-derived δ orbs, docs en+fr. In-orb detection only; declination synastry / applying-timing / dedicated CLI remain out of scope (future candidates above)
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

**v1.6.0 shipped on PyPI on 2026-06-04** — the additive `ketu.declination` subpackage: parallel + contra-parallel detection on the δ axis (`find_declination_aspects` scalar + `declination_aspect_masks` batch + `DeclinationAspectMasks` + `DECLA_ASPECT_DTYPE` + `DECLA_COEF=1/12` + `MIN_DECL_ORB=0.5°`), consuming the v1.5 `body_decl` field. Documented en+fr. A non-breaking additive minor: `CHART_DTYPE` byte-identical (companion function, not a field), the frozen `core.aspects` table + fingerprints unchanged, names reachable only via `ketu.declination.*`. 1654 tests; 100% coverage; mypy `--strict` clean; runtime pure NumPy (`pyswisseph` test/build-only). The final lightweight Ketu engine milestone before the Rahu UI project.

**Tag `v1.6.0`** points at commit `455cb36`. PyPI: <https://pypi.org/project/ketu/1.6.0/>. GitHub release (sdist + wheel): <https://github.com/alkimya/ketu/releases/tag/v1.6.0>. Published via OIDC trusted publishing (`publish.yml` run 26978132507 SUCCESS); both `origin/main` and the tag pushed (RTD follows main, PyPI follows tag); the user go/no-go relecture-validation gate was honoured before publish; post-publish fresh-venv smoke FROM PyPI confirmed the v1.6 surface (find_declination_aspects detects a Sun/Moon parallel, dtype == DECLA_ASPECT_DTYPE, no `pyswisseph` at runtime). Milestone audit PASSED 5/5; cross-phase integration checker PASS (0 blocker).

**CI note — RESOLVED 2026-06-04:** `publish.yml` was running Node.js-20 artifact actions (`upload-artifact@v5`, `download-artifact@v5`) which GitHub would have forced to Node 24 on 2026-06-16. Bumped to `upload-artifact@v7` + `download-artifact@v8` (Node-24 defaults; GitHub-hosted runners satisfy the ≥2.327.1 runner requirement automatically). `checkout@v5` + `setup-python@v6` were not flagged (already Node-24-compatible) and left as-is.

**Prior milestones:** v1.5.0 (2026-06-04) first-class declination δ + harmonics debt (archived `.planning/milestones/v1.5-*`). v1.4.0 (2026-06-03) open-ended aspect harmonics + Chiron range/orb (archived `.planning/milestones/v1.4-*`). v1.3.0 (2026-06-01) embedded Chiron as the 14th body + 100% coverage + data-driven aspects (archived `.planning/milestones/v1.3-*`). v1.2.0 (2026-05-28) shipped the relational + predictive framework (archived `.planning/milestones/v1.2-*`).

**v1.2 ops debt — RESOLVED:**

- ✓ `interrogate ≥95%` installed and BLOCKING in CI (Phase 13 wired, Phase 20 confirmed blocking)
- ✓ `numpydoc validate` BLOCKING in CI on public modules (flipped from warning-only at milestone close, Phase 20)
- ✓ `fr/CHANGELOG.md` decision finalized (Phase 20)
- ✓ Node 20 deprecation warnings eliminated — workflows on Node 24 (`actions/checkout@v5`, `setup-python@v6`, `upload-artifact@v5`)

**Carried-forward note:**

- Venv shebangs were hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` after the project relocated to `ketu/`. **RESOLVED 2026-05-30**: all 59 `venv/bin/*` shebangs rewritten to the current `/home/loc/workspace/ketu/venv/bin/python3` (+ cosmetic `pyvenv.cfg` path); wrappers (`sphinx-build`, `sphinx-intl`, `pytest`, `mypy`, `pip`) now run directly. The `python -m` invocation is no longer required (still works, but optional).

**Ephemeris-theory note (from Phase 18):** Ketu's bespoke TRUE Sun theory diverges from Swiss Ephemeris Moshier by up to ~56 arcsec on multi-decade back-projections, and the truncated-Meeus Moon theory by up to ~0.61° in longitude. The returns oracle uses self-consistency at 0.0001° as the PRIMARY gate; the pyswisseph cross-check is test-only with per-body tolerances reflecting these measured deltas. This is a known accuracy boundary, not a bug.

**Downstream impact:**

- Kala (`solaris/kala`) — **v1.3 broke two internal contracts** (13→14 body count + `angular_separation` body1→body2 convention); Ketu is source-of-truth, Kala adapts post-release (not a Ketu blocker). v1.4 is otherwise additive: the dynamic-harmonics path is opt-in (`dynamic_specs=`), and the only behaviour change is Chiron's orb (0°→4°) — relevant only to consumers reading Chiron aspect detections. The v1.1 `aspects=EXTENDED` opt-in note still applies for v1.0 behavior parity.

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
| v1.3 stays `1.3.0` despite breaking the 13→14 body freeze | Ketu is the source-of-truth library; Kala adapts to Ketu, not vice-versa. Public Ketu API stays additive; the broken contract is the internal Ketu↔Kala positional array | ✓ Good (v1.3) — shipped 1.3.0; public API additive, only internal Ketu↔Kala array broke as planned |
| Chiron via embedded Chebyshev coeffs, NOT swisseph runtime | Preserves pure-NumPy runtime + AGPL isolation; offline pyswisseph generator is build-only → `.npz` in package, eval is 100% NumPy | ✓ Good (v1.3) — zero swisseph under `ketu/`; reused unchanged by v1.4 range widening |
| Refactor ephemeris BEFORE adding Chiron | Chiron adds a branch to the fragile `calc_planet_position` if-elif; refactoring first makes Chiron a clean strategy, not aggravated debt | ✓ Good (v1.3) — Chiron landed as a clean `BODY_STRATEGIES` entry, no special-casing |
| [Phase 30-01] Chiron range 1900–2100 spike: degree=10, seg=32d, max delta-lon=0.001214 deg (gate < 0.01 deg) | Perihelion ~1895–96 just below 1900 bound; dense 1900–1910 edge sampling confirms uniform-param fit holds (segs 0–10 max 0.000013 deg); worst case at 1926-04-18 (seg 300) | ✓ Good (v1.4) — degree kept at 10, 8.2× margin; no bump needed |
| Dynamic harmonics = parallel additive path, NOT replacing the frozen table | Fingerprint contract must hold; `core.aspects` 14-row table never grows; `_VALID_HARMONICS` never gates the dynamic path | ✓ Good (v1.4) — V1/V13 sha256 fingerprints byte-identical; `generate_harmonic_aspects(h)` independent of presets |
| Accept ~2× smaller full-circle dynamic orbs (no convention unification) | Half-circle (table) and full-circle (dynamic) orb conventions coexist as independent paths; unification deferred | ✓ Good (v1.4) — documented as a known note, not reconciled; no scope creep |
| Chiron orb single source `core.bodies['orb']` (0°→4°, Pluto parity) | One edit propagates to synastry/cycles/composite/CLI; `_BODY_ORBS_16` sliced read-only at import, never hand-edited | ✓ Good (v1.4) — single constant change, all consumers propagated automatically |
| v1.4 = additive minor, absorbed the "v1.3.1 docs patch" | Dynamic harmonics + Chiron range made the scope a minor; only behaviour change (Chiron orb) documented in CHANGELOG | ✓ Good (v1.4) — shipped as 1.4.0; docs patch folded in as DOC-14..17 |
| `is_ascending_declination` distinct from β-based `is_ascending` | δ (equatorial) and β (ecliptic latitude) are separate quantities; both are valid; changing `is_ascending` semantics would be breaking | ✓ Good (v1.5) — both ship; anchor 2025-03-07 confirms they don't flip on the same days |
| OOB threshold = instantaneous obliquity ε(jd), not fixed 23°26′ | Physically correct and free via `true_obliquity`; the fixed threshold is slightly wrong at range edges | ✓ Good (v1.5) |
| Declination reuses the `coordinates.py` chain (Meeus 13.4 equivalent) | No new astronomy code; numerically equivalent to the direct formula | ✓ Good (v1.5) — regression test pins Δ = 0 vs the rectangular chain |
| Composite `body_decl` from the coordinates chain on composite λ,β (not parent-midpoint) | Midpointing parents' δ would be a zero-fill trap and physically wrong | ✓ Good (v1.5) |
| Harmonics debt grouped into ONE phase, order F2 → F3 → F1 | The CLI surface (F1) depends on a stable naming contract (F2) | ✓ Good (v1.5) — order held; CLI landed on a frozen contract |
| `find_aspect_timing` `dyn_coef: Optional[float]`; explicit `orb` wins silently when both given | `Optional[float]` clean under `--strict` (no `np.void` single-row typing); escape hatch short-circuits regardless of `dyn_coef` | ✓ Good (v1.5) — precedence defined + tested, no `ValueError` |
| CLI grammar Tight (`h7` alone + index list); `h7,h11` / `traditional,h7` deferred | Mixing/multi adds grammar + byte-stability cost for little immediate need | ✓ Good (v1.5) — deferred as HARMF-01; v1.1 fixture stayed byte-identical |
| User go/no-go before irreversible PyPI publish (relecture-validation) | The user personally reviews the whole milestone before tag/publish; auto-publish unacceptable | ✓ Good (v1.5) — checkpoint reached, user approved, then tag + main pushed |
| Declination aspects = companion function, NOT a `CHART_DTYPE` field | Keeps `CHART_DTYPE` byte-identical (no ratchet break); detection consumes the existing `body_decl` array | ✓ Good (v1.6) — `find_declination_aspects` + masks live in a separate `ketu.declination` subpackage; CHART_DTYPE unchanged |
| Unified `DECLA_ASPECT_DTYPE` (P+CP by `kind` field), not separate arrays | One return type, sorted upper-triangle, `np.empty(0,…)` for none — never `None`/tuple | ✓ Good (v1.6) — single contract; `body1`/`body2` chosen as `i1` (compact, sufficient for 14 indices) |
| δ orb `DECLA_COEF=1/12`, `MIN_DECL_ORB=0.5°` floor | `1/12` = reciprocal of max body orb (12°) → Sun/Moon lands on the published 1.0° consensus; floor keeps zero-orb bodies (Rahu/Ketu/Lilith) detectable | ✓ Good (v1.6) — exact fraction, not a magic number; verified by test |
| v1.6 LIGHT scope: DECLA only, in-orb detection | Final lightweight engine milestone before Rahu; no synastry δ / no applying-timing / no dedicated CLI; HARMF-01 deferred | ✓ Good (v1.6) — shipped tight; follow-ups remain explicit future candidates |
| MyST cross-doc links use explicit-label `[text](#label)`, not `file.md#anchor` | Bare-hash explicit-label form resolves in both EN and FR builds with no `xref_missing` warning | ✓ Good (v1.6) — cleared the warning in both builds |
| Commit recompiled `.mo` files (repo convention over plan premise) | Git history shows `.mo` are versioned every docs phase; `.po`-without-`.mo` would ship stale French docs (English fallback) | ✓ Good (v1.6) — FR docs render `contre-parallèle`; convention upheld |

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

Last updated: 2026-06-15 — v1.7 (Fictitious-Point Orbs) milestone STARTED via `/gsd-new-milestone`. Scope: orb 0°→2° on Rahu/Ketu/Lilith in `core.bodies`, targeted filter of the tautological `(Rahu, Ketu)` + Opposition detection, synastry in scope (oracles rewritten), shipped as MINOR `1.7.0` (aspect results change for consumers — not a patch). Triggered by a Rahu (frontend) need; Rahu UI project follows v1.7. ORB-01..04 + REL-01 active. Next: `/gsd-plan-phase` once the roadmap is approved.
