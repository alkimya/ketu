# Ketu

## What This Is

Ketu is a pure-Python astronomical-astrological library for planetary cycle calculations, built for financial analysis. It computes ephemerides, detects aspects (with configurable aspect sets), generates cycle time series, calculates astrological houses (Placidus / Koch / Porphyry with extensible registry), and produces ML-ready features via complex number representation. NumPy is the only core dependency. Published on PyPI, it feeds the Solaris trading ecosystem (Kala ML, Surya agent) but is designed as a standalone public library.

## Core Value

Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## Current State

**Latest shipped:** v1.1.0 (PyPI 2026-05-08) — <https://pypi.org/project/ketu/1.1.0/>

v1.1 evolved Ketu from a pure astronomical engine into an astronomical-astrological framework: configurable aspect sets (CLASSICAL default = 5 majors, opt-in TRADITIONAL/EXTENDED), extensible houses module (Placidus / Koch / Porphyry), and a Lilith formula correction (~180° shift, was computing perigee). Argparse CLI with subcommands replaced the legacy interactive `input()` prompt. 724 tests pass; mypy `--strict` clean; houses module at 96.75% coverage.

## Current Milestone: v1.2 Astrologie relationnelle et prédictive

**Goal:** Étendre Ketu de la chart natale astronomique vers l'astrologie relationnelle et prédictive, en s'appuyant sur le primitif `houses` livré en v1.1.

**Framing:** non-breaking minor strict — toutes nouvelles APIs additives, pas de changement de défaut, pas d'export retiré.

**Target features (Tier 1 — structurel):**

- **Chart abstraction (Option A)** — `CHART_DTYPE` structured array (positions + ASC/MC + houses + aspects) retournée par `compute_chart(jd, lat, lon, system)`. Upstream pour synastry / composite / solar return.
- **Additional house systems** — Whole Sign, Equal, Regiomontanus via `SYSTEMS` registry de v1.1
- **Synastry** — calcul d'aspects inter-charts entre deux thèmes natals
- **Composite chart (midpoint variant)** — fusion midpoint modulo 360° de deux thèmes
- **Solar return (standard + relocated)** — chart prédictif annuel ; root-finding pure-NumPy sur `Sun_longitude(t) − natal_Sun_longitude` ; relocation = `calculate_houses(jd_return, new_lat, new_lon, system)`

**Target features (Tier 2 — primitives):**

- **Arabic Parts framework + 8 parts livrées** — `PARTS` registry extensible (analogue à `SYSTEMS`) ; livrer Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis (7 Hermetic Lots) + Marriage (synergie synastry)
- **`is_day_chart(jd, lat, lon)` helper** — sect determination vectorisable, requis par les Parts day/night-formula

**Target features (Tier 3 — ops debt, deadline septembre 2026):**

- **CI doc gates (early)** — wire `interrogate ≥95%` + `numpydoc validate` tôt dans le milestone (touche tout le code suivant)
- **Workflow refresh (late)** — Node.js 20 → 24 sur `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4` en phase isolée tardive
- **`fr/CHANGELOG.md`** — créer (synthétisé depuis l'anglais, non double-maintenu) OU retirer la référence aspirationnelle

**Pre-research working docs (consumed):**

- [.planning/research/v1.2-SCOPE.md](research/v1.2-SCOPE.md) — three-tier scope sketch with risk register
- [.planning/research/v1.2-OPEN_QUESTIONS.md](research/v1.2-OPEN_QUESTIONS.md) — questions résolues lors du `/gsd-new-milestone` 2026-05-08

**Explicitly DEFERRED to v1.3:**

- **Chiron** — Centaur asteroid, very widely used in modern astrology, but requires either swisseph dependency or a Chebyshev-by-segment polynomial fit pipeline. User chose to make Chiron a dedicated v1.3 milestone (likely with other Centaurs: Pholus, Nessus, Chariklo). See `v1.2-SCOPE.md` § Out of scope for the technical reasoning.
- **Davison composite** — chart pour temps + lat/lon midpoints. v1.2 ship midpoint composite uniquement.
- **Lunar return** — même algo que solar return avec fenêtre 28j. Reportable post-solar-return si demande surface.

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

### Active

<!-- Current scope: v1.2 — see .planning/REQUIREMENTS.md for the full list with REQ-IDs. -->

v1.2 milestone scope agreed 2026-05-08 (PROJECT-00 through TIER3-NN — pending REQUIREMENTS.md generation immediately after milestone init).

Headlines:

- Chart abstraction `CHART_DTYPE` (Option A) — upstream architectural piece
- Whole Sign / Equal / Regiomontanus house systems via existing `SYSTEMS` registry
- Synastry, midpoint composite, solar return (standard + relocated)
- Arabic Parts framework + 7 Hermetic Lots + Marriage; `is_day_chart` helper
- CI doc gates (early), Node 20 → 24 workflow refresh (late), `fr/CHANGELOG.md` decision

### Out of Scope

<!-- Explicit boundaries (reaffirmed at v1.1 close). -->

- True/Osculating Lilith (h13) — defer to v1.2 — Mean Lilith is de-facto standard in 95% of astrology software
- Asteroid Lilith #1181 — defer to v1.2+ — different body, separate effort
- Whole Sign / Equal / Regiomontanus / Campanus houses (concrete impl) — architecture supports them via registry; ship deferred concretes if user demand surfaces
- Chiron, Centaurs, asteroids, fixed stars — defer to future milestone
- Arabic Parts / Lots — defer to future milestone
- Timezone handling inside Ketu — UTC remains required; timezone conversion is caller's responsibility
- `pyswisseph` or `pysweph` as runtime dependency — test-only is acceptable; license (AGPL) and brand promise (NumPy-only) prevent runtime
- Chart/SVG visualization — still removed, deferred to post-Ketu GUI tooling
- iCalendar export — still removed, deferred to post-Ketu GUI tooling
- Real-time streaming calculations — still batch-oriented
- Web API — Ketu is a library, not a service
- French documentation rebuild — still deferred (`fr/CHANGELOG.md` aspirational only — create or remove in v1.2)
- `click` / `typer` CLI dependencies — argparse stdlib was sufficient; no new runtime deps
- Bare `--harmonics 12` integer parsing — too ambiguous; forced named presets or explicit list

## Context

**v1.1.0 shipped on PyPI on 2026-05-08** — Lilith corrected (was computing perigee, now apogee — ~180° shift documented as BREAKING with per-date magnitude table); CLI default aspect set flipped from 14 to 5 (Kala must explicitly opt-in to EXTENDED); houses module landed with Placidus/Koch/Porphyry; argparse CLI replaced legacy `input()` prompt. 724 tests pass (557 in public CI, swisseph oracle suite local-only). LOC: ~22.1k Python (ketu/ + tests/). Tech stack unchanged: pure NumPy core, pysweph test-only.

**Tag `v1.1.0`** points at commit `41ee42e` (date-stamped CHANGELOG); annotated tag SHA `54ce673`. PyPI wheel sha256 `53b0ad668ccdea71af4ef8fbd9f73b6c8f20e31fefe618bb41906243498ea23b`. GitHub release: <https://github.com/alkimya/ketu/releases/tag/v1.1.0>.

**Known v1.2 ops debt:**

- `interrogate >=95%` not installed/wired into CI — header reference is aspirational
- `numpydoc validate` not wired into CI
- `fr/CHANGELOG.md` does not exist (header reference is aspirational)
- Node.js 20 deprecation warnings on every workflow step (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`) — non-blocking; tracked before September 2026 removal
- Venv shebangs hardcoded to `/home/loc/workspace/solaris/ketu/venv/bin/python3` (project relocated from `solaris/ketu/` to `ketu/`); workaround via `python -m` pattern documented

**Downstream impact:**

- Kala (`solaris/kala`) — KetuAdapter must explicitly request `aspects=EXTENDED` for v1.0 behavior parity; documented in UPGRADING.md
- Lilith consumers — recompute any cached values; ~180° shift on every date

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
| v1.2 framing = non-breaking minor strict | v1.1 burned the BREAKING quota (Lilith / CLI default / `calculate_house_cusps`); v1.2 must be additive only | Pending (v1.2 scope decision) |
| `Chart` abstraction = Option A (`CHART_DTYPE` structured array) | Cohérent avec CYCLE_DTYPE / HOUSES_DTYPE existants ; ML-interop NumPy-first ; batchable | Pending (v1.2 scope decision) |
| Composite chart = midpoint variant only | Standard universel ; Davison reportable v1.3 si demande surface | Pending (v1.2 scope decision) |
| Solar return = standard + relocated | Relocation quasi gratuite si l'abstraction Chart est correcte ; très utilisée en pratique moderne | Pending (v1.2 scope decision) |
| Arabic Parts = framework + 7 Hermetic Lots + Marriage | Framework cost fixe (registry) ; marginal cost par Part ~5 lignes ; Marriage = synergie synastry | Pending (v1.2 scope decision) |
| Tier 3 ordering = doc gates early, workflows late | Doc gates touchent tout le code suivant ; workflow refresh isolé en fin de milestone | Pending (v1.2 scope decision) |

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

Last updated: 2026-05-08 — v1.2 milestone initialized.
