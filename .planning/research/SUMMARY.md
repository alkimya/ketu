# Project Research Summary

**Project:** Ketu v1.4 — Dynamic Harmonics & Chiron Range
**Domain:** Pure-NumPy astronomical-astrological library (additive milestone on shipped v1.3.0)
**Researched:** 2026-06-02
**Confidence:** HIGH (stack, architecture, pitfalls verified against in-repo source; MEDIUM for Chiron orb convention)

---

## Executive Summary

Ketu v1.4 adds three discrete features to the shipped 1.3.0 library, plus documentation
recentring and a release: (1) a dynamic/open-ended harmonic aspect generator for any
integer h; (2) a Chiron orb fix from 0° to 4°; (3) a Chiron ephemeris range extension
from 1950-2050 to 1900-2100. The stack requires **no new dependencies** — NumPy remains
the sole runtime dependency and pyswisseph remains build-only (already present for Phase
23/24). All three features are additive: the frozen 14-row `core.aspects` table and its
SHA-256 fingerprints are preserved intact, the `bodies` array shape and dtype are
unchanged, and no existing API contracts are broken.

The dynamic harmonic generator is architecturally novel: it cannot reuse the existing
`aspects_for_harmonics` bool[14] mask system because that mask can only select rows that
already exist in the frozen table, and H7/H11/H17 angles have no table rows. Instead, a
new parallel function generates `(angle, coef)` pairs on the fly using the standard
360-degree-division convention, and these pairs are injected into the existing detection
hot-loop via a unified `spec_list` seam. Two functions in `calculator.py`
(`find_aspect_timing` ~line 427 and `find_aspects_between_dates` ~line 534) contain
hardcoded `np.where(_CORE_ASPECTS["angle"] == ...)` table lookups that will raise
`IndexError` for dynamic angles and **must be guarded** before the generator is exposed.

The single biggest open risk in the entire milestone is the Chiron 1900-2100 accuracy
gate near the 1895-1896 perihelion. Chiron's high eccentricity (0.38) means the locked
Phase 23 Chebyshev parameters (seg=32 days, degree=10) were validated only for
1950-2050, where the perihelion was safely outside the window. Extending to 1900 brings
the perihelion region within range and may push `max|Δλ|` past the 0.01° gate on the
early wings. This is an **empirical unknown that must be validated with a short spike
before the `.npz` is regenerated and committed**. If the gate fails, either the lower
bound shifts to ~1905 or the degree parameter is raised for early segments — both
requiring a new decision log entry.

---

## Key Findings

### Recommended Stack

No stack changes are required for any v1.4 feature. The existing dependencies cover
everything: NumPy for all computation (harmonic angle arithmetic, Chebyshev evaluation,
structured arrays), and pyswisseph + `seas_18.se1` as build-only tools for regenerating
the Chiron `.npz`. The `seas_18.se1` asteroid file covers 1800-2400 CE, so the 1900-2100
target range is entirely within its documented window with 100-year margins on each side.
The retflag=260 (Moshier fallback) deviation measured empirically in Phase 23 was
0.000067° — three orders of magnitude under the 0.01° gate — and that measurement holds
for 1900-2100 because Moshier Sun/Moon error is not epoch-dependent in this range.

**Core technologies:**
- `numpy>=1.20.0` (runtime): all angle arithmetic, Chebyshev evaluation, structured arrays — no change required
- `pyswisseph>=2.10.0` (build-only, test extras): oracle for `.npz` regeneration — no version bump needed
- `seas_18.se1` (build-only data file): Chiron orbital data 1800-2400 — already sufficient for 1900-2100

**What NOT to add:** scipy, sympy, astropy, any runtime pyswisseph. The AGPL isolation
architecture (build-only generator + embedded `.npz` + pure-NumPy eval) is a core library
invariant and must not be broken.

### Expected Features

**Must have (table stakes):**
- **Dynamic harmonic generator** — `generate_harmonic_aspects(h)` returning `HARMONIC_SPEC_DTYPE` array for any integer h; standard 360-division convention (coef = k/h); parallel path that never touches `core.aspects` or `_VALID_HARMONICS`; `dynamic_specs` parameter added to `calculate_aspects`, `calculate_aspects_vectorized`, `calculate_aspects_batch`, `find_aspects_between_dates`, `calculate_synastry`
- **Chiron orb 0° → 4°** — single constant change in `core.py` line 84; propagates automatically through all orb formula code; parity with Pluto (same 4° orb in current table); requires test/fixture updates

**Should have (differentiator):**
- **Chiron ephemeris 1900-2100** — doubles coverage to the standard range for serious astrological software; financial-astrology use cases need 1900s birth dates; requires offline spike-validate-then-regenerate sequence

**Documentation recentring (table stakes for release quality):**
- `concepts.md` tables recentred on TRADITIONAL/180°-division default (H1/H2/H3/H6); EXTENDED removed from tables but not from code
- `migration.md` and `relational_charts.md` default-aspect descriptions corrected from v1.1-era EXTENDED language to current TRADITIONAL default
- French gettext: `make update-po` → translate fuzzy entries → `make build-mo`

**Defer to v1.4.1 or later:**
- CLI `--harmonics h7` surface change (`parse_harmonics_spec` return type change, byte-stability implications for fixture)
- `get_aspect` dynamic-path support (not on the hot path post-Phase 26)
- `generate_cycle_series` dynamic-aspect-aware `aspect_orb` field (cycle engine is self-contained)

### Architecture Approach

The milestone divides cleanly into two independent change groups. Group A (dynamic
harmonics) introduces a new data representation (`HARMONIC_SPEC_DTYPE`) and a seam in
the detection loop where table-path and dynamic-path both lower into a unified
`list[(i_asp, angle, coef)]`. The sentinel `i_asp = -2` distinguishes dynamic aspects
from table aspects (0-13) throughout the output dtype. Group B (Chiron orb + range) is a
constant change in `core.py` that propagates automatically through all orb formula
plumbing, plus an offline `.npz` regeneration step.

**Major components and their v1.4 responsibilities:**

1. **`ketu/aspects/presets.py` (or new `ketu/aspects/harmonics.py`)** — host `generate_harmonic_aspects(h)` and `HARMONIC_SPEC_DTYPE`; existing `aspects_for_harmonics` is untouched
2. **`ketu/aspects/calculator.py`** — add `dynamic_specs` param to 4 multi-aspect functions; assemble unified `spec_list`; guard `find_aspect_timing:427` and `find_aspects_between_dates:534` against IndexError on dynamic angles not in the table
3. **`ketu/synastry/api.py`** — add `dynamic_specs` param; extend spec_list assembly; `aspect_type = -2` sentinel for dynamic rows (fits `i1` range [-128,127])
4. **`ketu/core.py`** — single-line Chiron orb constant change; propagates to `get_orb`, all three `calculate_aspects` variants, and `_BODY_ORBS_16` at import time
5. **`tools/gen_chiron_coeffs.py`** — update `jd0`/`jd1` to 1900/2100; extend `_REF_JDS`; rerun offline after spike validation
6. **`ketu/data/chiron_coeffs.npz`** — replaced in-place; wheel grows from ~290KB to ~580KB (acceptable, < 1MB target)
7. **`docs/`** — recentre concepts/migration/relational_charts; full gettext update cycle for fr locale

### Critical Pitfalls

1. **Chiron 1900-2100 perihelion accuracy risk — the milestone's single biggest unknown.** Chiron's 1895-1896 perihelion falls just inside the new lower bound. Phase 23 locked seg=32/degree=10 for 1950-2050 only. Running the generator over 1900-2100 may fail the `max|Δλ| < 0.01°` validation gate near the early segments. **Prevention: run a short validation spike BEFORE committing the regenerated `.npz`. If the gate fails, adjust parameters and write a new decision log entry. Do not assume Phase 23 parameters hold for the extended wings.**

2. **Dynamic path accidentally gated by `_VALID_HARMONICS`.** If the dynamic generator calls `aspects_for_harmonics` internally, it raises `ValueError: unknown harmonic: 7`. The dynamic path must be fully separate. **Prevention: code review gate — grep for any `aspects_for_harmonics` call in the new generator module; the dynamic path must never call it.**

3. **Hardcoded table lookups in `calculator.py` crash on dynamic angles.** `find_aspect_timing:427` and `find_aspects_between_dates:534` both do `np.where(_CORE_ASPECTS["angle"] == aspect_value)[0]` — IndexError for any dynamic angle not in the 14-row table. **Prevention: add guards to both locations in the same phase that introduces `dynamic_specs`; do not ship the generator without fixing both.**

4. **CLI byte-stable fixture gains new Chiron aspect lines at orb 4°.** `v1_1_reference_output.txt` will change because the wider orb window brings in new Chiron aspects at the reference date. `test_harmonics_all_byte_identical_to_v1_1_reference` fails immediately. **Prevention: regenerate fixture with the documented command AFTER the orb change; manually audit every new/changed Chiron line via `git diff` before committing.**

5. **Core.aspects SHA-256 fingerprint mutation.** `test_aspects_byte_fingerprint` pins two SHA-256 hashes. If the dynamic path accidentally stores results back into `ketu.core.aspects` or any module-level derived array, both fingerprint tests fail. **Prevention: dynamic path operates on transient in-function arrays only; consider `aspects.flags.writeable = False` in `core.py` as belt-and-suspenders.**

6. **Release: push `origin/main` AND the tag.** RTD follows `origin/main` for `latest` docs; PyPI OIDC triggers on the tag. Pushing only the tag leaves RTD frozen at v1.3 content. **Prevention: release checklist must explicitly include `git push origin main` before or alongside the tag push.** (Recorded in project memory from v1.3 release lesson.)

---

## Implications for Roadmap

Based on the combined research, the dependency graph is:

```
Phase A (dynamic harmonics + detection integration) ──────────────────────┐
Phase B (Chiron orb 4° + test/fixture updates) ── Phase C (Chiron range) ──── Phase D (docs) ── Phase E (release)
```

Phases A and B are fully independent and can be built in parallel or in either order.
Phase C must follow B (orb constant must be final before `.npz` regeneration to avoid
double fixture churn). Phase D must follow A+B+C (API surface stable). Phase E must
follow D.

### Phase 1: Dynamic Harmonic Generator + Detection Integration

**Rationale:** Fully additive, no shared files with Phase 2. The most architecturally
novel change in the milestone — establishes the `HARMONIC_SPEC_DTYPE` data representation,
the unified `spec_list` seam, and the `i_asp = -2` sentinel before any other phase depends
on the detection loop. The two hardcoded table lookups in `calculator.py` (lines 427, 534)
MUST be guarded in this phase before the generator is exposed to callers.
**Delivers:** `generate_harmonic_aspects(h)`, `HARMONIC_SPEC_DTYPE`, `dynamic_specs`
parameter on 5 functions, guards on both table-lookup crash points, full numpydoc
docstrings + doctests, tests for H7/H11/H17 through the full detection chain, SHA-256
fingerprint tests still passing.
**Features from FEATURES.md:** harmonic generator (P1 table stakes).
**Avoids:** Pitfalls 1-A (separate path, never calls `aspects_for_harmonics`), 1-B (no
table mutation), 1-C (no i_asp-keyed cache without key-schema comment), 2-A (k=1..h//2
loop), 2-B (float64 angles in match), 5-C (numpydoc/interrogate gate).

### Phase 2: Chiron Orb 4° + Test and Fixture Updates

**Rationale:** Fully independent of Phase 1. A one-line constant change with
well-understood propagation. Several test artifacts pin the old zero-orb behavior and
must be updated explicitly; the CLI fixture must be regenerated and manually audited.
**Delivers:** `core.py` Chiron orb 0→4; updated `test_modes_idempotent.py` docstrings
(remove Chiron from "zero-orb" group); new explicit `test_synastry_orb_limit_chiron_nonzero_orb`
assertion; regenerated and manually audited `v1_1_reference_output.txt`.
**Features from FEATURES.md:** Chiron orb fix (P1 table stakes / bug fix framing).
**Avoids:** Pitfalls 3-A (stale docstrings + new explicit test), 3-B (fixture regeneration
+ manual audit of each new Chiron line), 3-C (run `pytest -x` before fixture regeneration
to isolate all breaks individually).
**Must precede:** Phase 3 — avoids double fixture churn if orb and range land in the same
regeneration pass.

### Phase 3: Chiron Range Spike-Validate-Then-Regenerate

**Rationale:** Carries the milestone's highest uncertainty. The perihelion accuracy
question cannot be resolved by analysis alone. Structure as: (a) spike sub-task — run
generator over 1900-2100 and check validation gate; (b) if gate passes, regenerate `.npz`
and extend regression refs; (c) if gate fails, decide on parameter adjustment and write
a new decision log entry before proceeding. Do not skip the spike sub-task.
**Delivers:** validated `chiron_coeffs.npz` covering 1900-2100; updated `gen_chiron_coeffs.py`
`jd0`/`jd1`; `test_chiron_regression.py` extended with at minimum one pre-1950 and one
post-2050 reference pin; documented `max|Δλ|` for the full new range.
**Features from FEATURES.md:** Chiron range extension (P2 differentiator).
**Avoids:** Pitfalls 4-A (jd_end in `.npz` correct, derived from `swe.julday` not
hardcoded), 4-B (spike first — empirical gate before commit), 4-C (new regression refs
in both wings, wheel size check < 1MB).
**Must follow:** Phase 2 (orb constant final).
**Build environment prerequisite:** pyswisseph + `seas_18.se1` accessible at run time on
the developer machine executing this phase.

### Phase 4: Documentation Recentring (en + fr)

**Rationale:** API surface must be stable before docs are written. This phase updates all
three stale doc files, runs the full gettext cycle for fr, and ensures no cross-document
contradictions remain. Follows the same flow executed successfully in Phase 26.1.
**Delivers:** `concepts.md` tables recentred on TRADITIONAL/180°-division default (EXTENDED
remains in code, framed as opt-in not default); `migration.md` and `relational_charts.md`
default-aspect language corrected from v1.1-era wording; fr `.po` files updated and
translated (zero fuzzy flags), `.mo` compiled; changelog v1.4 entry.
**Must follow:** Phases 1+2+3 (API and constant values final).
**Avoids:** Pitfalls 5-A (full gettext cycle, grep for fuzzy flags), 5-B (EXTENDED
narrative consistent — no paragraph contradicts the table removal), 5-D (grep for stale
`EXTENDED|classical.*default` strings across all doc source files).

### Phase 5: Release v1.4.0

**Rationale:** Standard release ceremony with one critical discipline item: push
`origin/main` before or alongside the tag. RTD follows main, PyPI OIDC follows the tag.
**Delivers:** pyproject.toml version bump; PyPI OIDC publish; `git push origin main` +
`git push origin v1.4.0`; RTD `latest` build confirmed at new SHA; CHANGELOG migration
note for downstream Chiron aspect consumers.
**Must follow:** Phase 4.
**Avoids:** Pitfall 6-A (push main not just tag), 6-B (CHANGELOG migration note so
downstream consumers — Kala — know Chiron now participates in aspects).

### Phase Ordering Rationale

- Phases 1 and 2 are independent and can run in parallel if capacity allows. Phase 1 is
  larger (new data representation + 5 function signatures + guards + doctests); Phase 2
  is smaller (1 constant + test/fixture work). Either order is valid.
- Phase 3 is gated on Phase 2 to avoid regenerating `v1_1_reference_output.txt` twice
  (once for the orb change, once for the range). If parallel execution is forced, accept
  the double fixture re-record.
- Phase 3 is the only phase with a build-environment prerequisite (pyswisseph +
  `seas_18.se1`). Verify the developer environment before starting Phase 3.
- Phase 3 is the only phase that may block on empirical results (accuracy gate). The
  spike sub-task must be the first step so a gate failure does not become a mid-phase
  surprise. Budget time for a potential parameter adjustment decision.

### Research Flags

**Needs deeper research / has open empirical questions:**
- **Phase 3 (Chiron range spike):** The perihelion accuracy question is the only truly
  open empirical question in the milestone. No analysis can substitute for running the
  generator. Plan a spike sub-task as the explicit first step with a go/no-go gate before
  the main `.npz` regeneration work.

**Standard patterns — skip additional research:**
- **Phase 1 (dynamic harmonics):** Math fully resolved (k=1..h//2, coef=k/h, fold via
  `min(a,360-a)`); all integration points identified with exact file:line references;
  output sentinel (`i_asp=-2`) and downstream implications documented. No architectural
  ambiguity remains.
- **Phase 2 (Chiron orb):** Single constant propagation through well-understood plumbing.
  Test artifacts to update enumerated with exact file and line references. No research
  needed.
- **Phase 4 (docs):** Follows the same gettext flow executed in Phase 26.1. Stale strings
  identified with exact grep commands. No research needed.
- **Phase 5 (release):** Standard PyPI OIDC + RTD ceremony. Discipline item (push
  main + tag) is documented in project memory.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All claims verified against in-repo source, Phase 23 empirical measurements, and Swiss Ephemeris official docs. No new deps required. |
| Features | HIGH (math) / MEDIUM (Chiron orb value) | Harmonic angle math verified against existing `core.aspects` entries. Chiron 4° is defensible but no single authoritative standard; community range is 2-5°; user confirmed 4°. |
| Architecture | HIGH | Every integration point identified with exact file:line references. Both crash-risk functions in `calculator.py` pinpointed. Output sentinel design and propagation through synastry/cycles documented. |
| Pitfalls | HIGH | All pitfalls grounded in actual source code and test invariants verified by direct inspection. Perihelion accuracy risk correctly flagged as empirical-unknown, not analysable-away. |

**Overall confidence:** HIGH for scope definition and implementation plan; MEDIUM for
Phase 3 execution timeline (depends on empirical accuracy gate result which may require
parameter renegotiation).

### Gaps to Address

- **Chiron 1900-2100 accuracy near perihelion (Phase 3):** Whether seg=32/degree=10 passes the 0.01° gate for the 1900-1950 wing is unknown until the generator is run. Plan as a spike sub-task. If the gate fails: options are (a) raise `degree` from 10 to 12 for early segments, (b) reduce `seg_len` for early segments, (c) shift lower bound to ~1905. Each option requires a new decision log entry analogous to 23-DECISION.md.
- **CLI surface for dynamic harmonics (deferred):** `parse_harmonics_spec` returns a bool[14] mask. Supporting `--harmonics h7` on the CLI requires a return-type change with byte-stability implications for the reference fixture. Scoped out of Phase 1; track as v1.4.1 or a Phase 1.1 follow-on.
- **`find_aspect_timing` orb derivation design debt (Phase 1):** This function takes `aspect_value: float` and derives orb by table lookup. For dynamic angles the guard skips the lookup, but the function signature remains inconsistent. Document as known design debt; a `coef` parameter or deprecation of the table-lookup path is a future cleanup.

---

## Sources

### Primary (HIGH confidence — verified against in-repo source)
- `/home/loc/workspace/ketu/ketu/core.py` — `bodies` array, `aspects` frozen 14-row table, Chiron orb=0 at line 84
- `/home/loc/workspace/ketu/ketu/aspects/presets.py` — `_VALID_HARMONICS`, `aspects_for_harmonics`, `EXTENDED`, `_CORE_ASPECTS`
- `/home/loc/workspace/ketu/ketu/aspects/calculator.py` — detection hot loop, `find_aspect_timing:427`, `find_aspects_between_dates:534`, `get_orb` orb formula
- `/home/loc/workspace/ketu/ketu/synastry/api.py` — `calculate_synastry` loop, `_BODY_ORBS_16` propagation
- `/home/loc/workspace/ketu/ketu/synastry/orbs.py` — `_build_body_orbs_16`, `synastry_orb_limit`
- `/home/loc/workspace/ketu/tools/gen_chiron_coeffs.py` — generator parameterization, retflag=260 handling, `jd0`/`jd1` constants
- `/home/loc/workspace/ketu/.planning/phases/23-spike-chiron/23-RESEARCH.md` and `23-DECISION.md` — empirical max|Δλ|=0.000861° for 1950-2050, seg=32/degree=10 locked, retflag=260 deviation 0.000067°
- `/home/loc/workspace/ketu/pyproject.toml` — dependency pins, interrogate gate (95%), numpydoc gate (blocking)
- `/home/loc/workspace/ketu/tests/` — `test_ketu.py` SHA-256 fingerprint tests, `test_modes_idempotent.py`, `test_orbs.py`, `v1_1_reference_output.txt`, `test_chiron_regression.py`

### Secondary (MEDIUM confidence — community consensus, multiple sources)
- Swiss Ephemeris official docs (astro.com/swisseph): `seas_18.se1` covers 1800-2400; no pure-Moshier path for Chiron
- John M. Addey, *Harmonics in Astrology* (1976): 360/h angle generation principle (via webSearch references)
- David Cochrane vibrational astrology: orb = base_orb / h (MEDIUM; web sources, content not fully extractable)
- Serennu Chiron ephemeris (1920-2099): confirms conventional range expectation for astrological software
- saturnseason.com orb conventions: 2-4° most common for Chiron aspects

### Tertiary (LOW confidence — single source or inference)
- Cochrane *The First 32 Harmonics* (2021): no established individual names beyond H12 for higher harmonics (content not directly accessible)

---

*Research completed: 2026-06-02*
*Ready for roadmap: yes*
