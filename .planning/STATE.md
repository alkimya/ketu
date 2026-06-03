---
gsd_state_version: 1.0
milestone: v1.4
milestone_name: Dynamic Harmonics & Chiron Range
status: in-progress
last_updated: "2026-06-03T14:10:00Z"
last_activity: 2026-06-03
progress:
  total_phases: 5
  completed_phases: 3
  total_plans: 13
  completed_plans: 8
  percent: 62
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-02 — milestone v1.4 started)

**Core value:** Cycle calculations must be correct, tested, and performant.
**Current focus:** MILESTONE v1.4 (Dynamic Harmonics & Chiron Range) — roadmapped, ready to plan. 5 phases (28-32). Intent axes: (1) on-the-fly aspect generator for arbitrary integer harmonics integrated through the full detection chain, frozen table + preset fingerprints preserved; (2) Chiron orb 0°→4° (Pluto parity); (3) Chiron range 1900–2100 (regenerate `.npz`, re-validate < 0.01°, including perihelion spike); (4) doc coherence (concepts.md recentred on 180°-division default, EXTENDED out of tables, migration/relational fixes, full fr gettext cycle); (5) Release 1.4.0. Phases start at **28** (v1.3 ended at Phase 27 + inserted 26.1). v1.3.0 live on PyPI; v1.0–v1.3 archived to `.planning/milestones/`.

## Current Position

Phase: 31-documentation-en-fr — IN PROGRESS (1/6 plans done, Wave 1 parallel)
Plan: 1/6 done (31-01 concepts.md complete); sibling plans 31-02..31-06 in parallel
Status: 31-01 complete; concepts.md recentred on 180°-division default; generate_harmonic_aspects documented; Chiron range 1900-2100 noted
Last activity: 2026-06-03 — Phase 31-01 COMPLETE; concepts.md tables trimmed (H5/H9/H10 prose note, 14→7 coefficient table), generate_harmonic_aspects subsection added, Chiron 1900-2100 note updated

Progress: [████████░░░░░░] 62% — Phase 30 complete; Phase 31 in progress (8/13 plans)

## v1.4 Roadmap Structure

- **Phase 28: Dynamic Harmonic Generator + Detection Integration** (ASP-04, ASP-05, ASP-06, ASP-07, ASP-08, ASP-09) — new public `generate_harmonic_aspects(h)` returning `(angle, coef)` specs for any integer harmonic via the 360° convention (`fold_to_0_180(k·360/h)`, `coef=k/h`); wire `dynamic_specs` parameter into `calculate_aspects` (scalar/vectorized/batch), `find_aspects_between_dates`, `calculate_synastry`; guard `find_aspect_timing:427` and `find_aspects_between_dates:534` table-index lookups against IndexError on dynamic angles; `i_asp=-2` sentinel for dynamic rows; frozen `core.aspects` table and sha256 fingerprints byte-identical; `_VALID_HARMONICS` never consulted on dynamic path; full numpydoc + 100% coverage. First v1.4 phase; independent of Phase 29.
- **Phase 29: Chiron Orb 4°** (CHIR-06, CHIR-07, CHIR-08) — single constant change `core.bodies['orb']` for Chiron 0→4 (Pluto parity); regenerate + manually audit `tests/cli/fixtures/v1_1_reference_output.txt`; fix synastry test docstrings/asserts that grouped Chiron with zero-orb points; add explicit test pinning Chiron orb=4°. Independent of Phase 28; MUST precede Phase 30.
- **Phase 30: Chiron Range 1900–2100** (CHIR-09, CHIR-10, CHIR-11) — BLOCKING SPIKE first: run generator over 1900–2100 and measure `max|Δλ|` vs Swiss Ephemeris including the ~1895–1896 perihelion region; raise degree (10→12) if the < 0.01° gate fails; only after spike passes: regenerate `ketu/data/chiron_coeffs.npz` (new `jd_start`/`jd_end`, `actual_len` fix preserved); re-pin regression refs spanning 1900–2100. MUST follow Phase 29.
- **Phase 31: Documentation (en + fr)** (DOC-14, DOC-15, DOC-16, DOC-17) — recentre `concepts.md` on 180°-division default (CLASSICAL/TRADITIONAL tables only, EXTENDED out of tables); fix `migration.md` and `relational_charts.md` stale default-aspect claims; document `generate_harmonic_aspects`, Chiron 1900–2100, Chiron orb 4°; no Kala references; full fr gettext cycle (re-extract, merge, translate zero English-fallback, recompile); en+fr build at 1-warning baseline. MUST follow all feature phases (28+29+30).
- **Phase 32: Release v1.4.0** (REL-12, REL-13) — version bump 1.4.0 (`pyproject.toml` + `ketu/__init__.py`); CHANGELOG `[1.4.0]` Added/Changed; fr CHANGELOG synced; PyPI via OIDC + GitHub release (sdist+wheel); push `origin/main` AND tag; fresh-venv smoke (dynamic generator, Chiron 4° orb, 1900–2100 range, no `pyswisseph` at runtime). MUST follow Phase 31.

## Critical Milestone Constraints

- **Pure-NumPy runtime NON-NEGOTIABLE** — dynamic harmonic generation is plain NumPy arithmetic; Chiron `.npz` regenerated offline by pyswisseph-build-only `tools/gen_chiron_coeffs.py`; runtime eval 100% NumPy. `pyswisseph` test/build-only (AGPL isolation). No scipy or new runtime dep.
- **Frozen `core.aspects` table** — sha256 fingerprints V1 `c5bd177...` + V13 `3258530...` must be byte-identical after Phase 28; dynamic path is a parallel, additive path that never mutates the 14-row table.
- **`_VALID_HARMONICS` must NOT gate the dynamic path** — grep gate: no `aspects_for_harmonics` call inside `generate_harmonic_aspects`; ValueError would fire on H7/H11/H17.
- **IndexError guards MUST ship with Phase 28** — `find_aspect_timing:427` and `find_aspects_between_dates:534` both do `np.where(_CORE_ASPECTS["angle"] == ...)[0]` and crash on any dynamic angle; both guards land in the same phase that introduces `dynamic_specs`.
- **Phase 30 perihelion spike is a hard gate** — do NOT commit the new `.npz` until the accuracy measurement over 1900–2100 (including perihelion ~1895–1896) passes < 0.01°; if it fails, adjust parameters and write a new decision log entry.
- **CRITICAL (release):** Push `origin/main` AND the tag `v1.4.0` — RTD follows main, PyPI OIDC follows the tag; pushing only the tag freezes docs at v1.3 content (lesson from v1.3 release).

## Performance Metrics

**Velocity totals (shipped milestones):**

- v1.0: 16 plans / 7 phases (decimal Phase 2.1 inserted)
- v1.1: 27 plans / 5 phases (~3h active)
- v1.2: 35 plans / 8 phases (~20 days elapsed)
- v1.3: 30 plans / 8 phases (21-27 + 26.1) (2026-05-29 → 2026-06-01)

*Updated after each plan completion.*

## Accumulated Context

### Decisions

Full log in PROJECT.md Key Decisions table. Key v1.3 → v1.4 carry-forwards:

- [Phase 26-02]: `aspects_for_harmonics` returns frozen `np.bool_[14]` mask from harmonic column; TRADITIONAL=`aspects_for_harmonics([1,2,3,6])`; EXTENDED=`aspects_for_harmonics([1,2,3,5,6,9,10])`; CLASSICAL stays curated 5-index list. Library default = TRADITIONAL (7). CLI pinned to "classical" (byte-stable).
- [Phase 26-01]: `core.aspects` V1 fingerprint `c5bd177...` (name/angle/coef) + V13 fingerprint `3258530...` (all 5 columns) — both MUST remain byte-identical after Phase 28.
- [Phase 24-04]: Last-segment `actual_len` fix in `_eval_chiron_qty` — `actual_len=min(seg_start+seg_len, jd_end)-seg_start`; this fix MUST be preserved when `.npz` is regenerated in Phase 30.
- [Phase 23-01/02]: Phase 23 locked params for 1950–2050: `seg=32d`, `degree=10`, 3 quantities (lon/lat/dist). Phase 30 spike measures whether these hold for 1900–2100 before committing.
- [Phase 27-02]: Lesson — push `origin/main` in addition to the tag; RTD follows main, PyPI follows tag. Phase 32 release checklist must explicitly include `git push origin main`.
- [Phase 28-01]: `generate_harmonic_aspects(h)` bounds [2..64]: h=1 degenerate (0 rows via h//2=0), h>64 impractically small orbs (coef=k/h). Both rejected via ValueError.
- [Phase 28-01]: `DynamicAspectSpec = Optional[Union[NDArray, List[NDArray]]]` — type alias for `dynamic_specs=` parameter across all consumers (calculator, synastry, cycles). Plans 02/03 import from `ketu.aspects.harmonics`.
- [Phase 28-01]: `HARMONIC_DTYPE` mirrors `core.aspects.dtype` exactly (5 fields S16/f4/f4/i4/U4). Consumers need no dtype conversion. H-names stored as bytes (S16 field).
- [Phase 28-01]: `_fold_to_0_180` is the canonical fold; all consumers must import from `ketu.aspects.harmonics`, not reimplement.
- [Phase 28-03]: `aspect_type=-2` sentinel for dynamic synastry rows; filtered-mode predicate changed to `!= -1` (keeps -2, drops -1).
- [Phase 28-03]: Cycles full-circle expansion: generator emits folded [0,180]; mirror `360-theta` added for waning detection (not 0/180 poles). `dynamic_specs=None` path byte-identical via `effective_*` variables.
- [Phase 28-03]: Empty list `dynamic_specs=[]` falls back silently to static candidate set (no crash, no extension).
- [Phase 28-02]: `find_aspect_timing` orb param: explicit `orb=float` skips table lookup entirely (dynamic path); `orb=None` does table lookup with clear ValueError on miss (never IndexError). Simpler than coef param.
- [Phase 28-02]: Two unreachable defensive fallback branches in `find_aspects_between_dates` name resolution marked `pragma: no cover` — `find_all_aspects` only returns angles from the search list, so lookups always succeed for well-formed calls.
- [Phase 28-02]: `_normalize_dynamic_specs` centralises None/single/list normalization — imported/reused by all calculator consumers (not reimplemented per-function).
- [Phase 29-01]: Chiron natal orb=4° (Pluto parity); single literal in `core.bodies['orb'][13]`; `_BODY_ORBS_16` rebuilds from it at import — no second source patched. CLI fixture audited: exactly 2 added lines (Sun-Chiron + Moon-Chiron Semi-sextile), 0 removed. orbs.py docstring already correct (no Chiron in zero-orb group).
- [Phase 30-01]: Chiron range 1900-2100 spike: max|delta-lon|=0.001214 deg, params seg=32d/degree=10, gate PASS < 0.01 deg; new .npz = 2283 segs, jd_start=2415020.5, jd_end=2488069.5. Dense 1900-1910 edge: segs 0-10 max 0.000013 deg (worst 1900 seg 0.000005 deg). Worst case 1926-04-18 (seg 300, JD 2424624.04). Ephemeral spike thrown away (spike-only). Plan 30-02 regenerates with degree=10.
- [Phase 30-02]: .npz regenerated with degree=10 / jd_start=2415020.5 / jd_end=2488069.5 / 2283 segs / shape (2283,11) / 577 KB. Gate PASS max|Δλ|=0.001214° (margin 8.2×). Wing refs added: 1920-01-01 (2.609080°) + 2080-01-01 (36.885249°). No 1905 ref needed (1900-1910 edge max 0.000013°). actual_len fix (Phase 24-04) preserved; zero pyswisseph in chiron.py. 1537 tests, 100% coverage.
- [Phase 31-03]: relational_charts.md DOC-15 — compute_chart aspects=None now names TRADITIONAL (v1.3+) as library default; calculate_synastry aspects="classical" explicitly documented as function-level backward-compat default (NOT changed to TRADITIONAL — intentional byte-stability pin). No remaining "default classical set" text in relational_charts.md.
- [Phase 31-05]: chiron.md: ValueError behavior replaced with silent clamping (Phase 30); range 1900-2100, accuracy 0.001214° documented with v1.4 badges
- [Phase 31-02]: migration.md DOC-15 — stale "behavior is unchanged (EXTENDED = all 14 aspects)" replaced with v1.1 history annotation + explicit TRADITIONAL pointer; code comment updated. DOC-16 Chiron-behavior — "1950-2050 / raises ValueError" replaced with "1900-2100 (v1.4) / silently clamped".
- [Phase 31-documentation-en-fr]: conf.py version/release bumped to 1.4.0 here (docs-build metadata); pyproject.toml + ketu/__init__.py stay at 1.3.0 until Phase 32

### Roadmap Evolution

- v1.4 roadmapped 2026-06-02: 5 phases (28-32), 18 requirements mapped (ASP-04..09, CHIR-06..11, DOC-14..17, REL-12..13), 100% coverage. Phase 28 and Phase 29 are independent; Phase 30 depends on 29; Phase 31 depends on 28+29+30; Phase 32 depends on 31.
- v1.3 ROADMAP archived to `.planning/milestones/v1.3-ROADMAP.md` on 2026-06-02 before v1.4 roadmap was written.

### Pending Todos

None at roadmap time.

### Blockers/Concerns

- **Phase 30 perihelion accuracy** — RESOLVED by Phase 30-01 spike. degree=10/seg=32d PASSES < 0.01 deg over 1900-2100 (max 0.001214 deg, 8.2x margin). No parameter change needed. Plan 30-02 executed; .npz regenerated.
- **Build environment prerequisite for Phase 30** — RESOLVED. pyswisseph + seas_18.se1 confirmed accessible at /home/loc/workspace/rahu/kerykeion/kerykeion/sweph.
- **Phase 30 .npz regeneration** — RESOLVED by Phase 30-02. .npz regenerated (2283 segs, 1900-2100, gate PASS). Phase 30 COMPLETE.

## Session Continuity

Last session: 2026-06-03 — Phase 31-06 EXECUTED (2/2 tasks). [1.4.0] changelog section added to docs/source/changelog.md; v1.1 EXTENDED-default entry annotated; conf.py docs-build version/release bumped to 1.4.0 (pyproject.toml + ketu/__init__.py unchanged).
Stopped at: Phase 31-06 complete — changelog.md + conf.py updated for v1.4. Remaining Phase 31 plans (31-07 gettext fr) in progress in parallel.
Resume file: None — Phase 30 COMPLETE; next phase is 31-documentation.
