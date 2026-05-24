---
phase: 17-composite-chart-midpoint-variant
plan: 04
subsystem: phase-closeout
tags: [doc-gates, makefile, pyproject-markers, changelog, see-also, roadmap-smoke, comp-05, phase-closeout]

# Dependency graph
requires:
  - phase: 17-composite-chart-midpoint-variant
    plan: 01
    provides: circular_midpoint helper + Davison-deferred module docstring
  - phase: 17-composite-chart-midpoint-variant
    plan: 02
    provides: calculate_composite (COMP-01, COMP-03) + 75 ratchet tests
  - phase: 17-composite-chart-midpoint-variant
    plan: 03
    provides: 3 composite oracle fixtures + test_oracle.py (18 parametrised tests)
  - phase: 16-synastry
    plan: 05
    provides: Phase close-out template (make synastry-coverage + synastry_coverage_gate marker)
provides:
  - "`make composite-coverage` Makefile target (≥95% coverage gate scoped to ketu/composite/*; measured 100%)"
  - "composite_coverage_gate pytest marker registered in pyproject.toml [tool.pytest.ini_options].markers"
  - "tests/composite/test_composite_coverage_gate.py sentinel — ratchets marker recognition + module import"
  - "Back-reference See Also entries in ketu/charts/__init__.py + ketu/synastry/__init__.py pointing to ketu.composite.calculate_composite"
  - "CHANGELOG.md ## [Unreleased] ### Added entry citing COMP-01..04 + COMP-05"
  - ".planning/REQUIREMENTS.md COMP-01..04 statuses flipped to Done + COMP-05 row added"
  - "4 ROADMAP success criteria smoke-tested PASS with output excerpts captured in this SUMMARY"
affects: [18-solar-return, 19-arabic-parts, 20-release-prep-v1.2]

# Tech tracking
tech-stack:
  added: []  # Pure doc + ops ratchets; no runtime / dev deps added
  patterns:
    - "Phase close-out template (3-task shape, second application after synastry Plan 16-05): register marker -> Makefile target + sentinel -> See Also back-refs -> CHANGELOG additive entry -> REQUIREMENTS status flip"
    - "Two-step coverage Makefile pattern preserved (pytest tests/composite/ + coverage report --include='ketu/composite/*' --fail-under=95) — avoids the NumPy _NoValueType reload bug from sub-package source=ketu.composite"
    - "Marker registration via pyproject.toml [tool.pytest.ini_options].markers — alphabetical order (charts -> composite -> houses -> synastry), no tests/conftest.py created"
    - "Back-reference See Also pattern — forward refs (composite -> charts + synastry) already in place from Plans 17-01/17-02; this plan closes the loop with charts + synastry pointing back to composite via importable Python paths (Phase 13 lesson honoured)"

key-files:
  created:
    - tests/composite/test_composite_coverage_gate.py  # sentinel test (~32 LoC)
  modified:
    - Makefile  # +composite-coverage target + .PHONY entry (mirror of synastry-coverage)
    - pyproject.toml  # +composite_coverage_gate marker entry (alphabetical between charts and houses)
    - ketu/charts/__init__.py  # See Also block extended with synastry + composite back-references
    - ketu/synastry/__init__.py  # See Also block extended with composite back-reference
    - CHANGELOG.md  # ## [Unreleased] ### Added: 8 new bullets citing COMP-01..04 + COMP-05
    - .planning/REQUIREMENTS.md  # COMP-01..04 flipped to [x] Done in body + status table; COMP-05 row added

key-decisions:
  - "composite_coverage_gate marker registered alphabetically between charts_coverage_gate and houses_coverage_gate in pyproject.toml [tool.pytest.ini_options].markers (alphabetical convention; mirror of the SYN-05 / CHART-05 / HOU-09 close-outs)."
  - "Makefile target uses the two-step pattern (pytest tests/composite/ + coverage report --include='ketu/composite/*' --fail-under=95) inherited from Phase 16-05 synastry-coverage and Phase 14 charts-coverage — avoids the NumPy _NoValueType reload bug from sub-package source narrowing. Single-step --cov=ketu/composite --cov-fail-under=95 was REJECTED for this reason."
  - "COMP-05 added as a Plan 17-04 close-out convention addition (not in the original COMP-01..04 spec; symmetry with SYN-05 / CHART-05 / HOU-09). REQUIREMENTS body + status table updated to include this row. Documented in this SUMMARY's deviations section as conventional, not architectural."
  - "Back-reference See Also entries follow the importable-Python-path convention (Phase 13 BLOCKER lesson). All 3 new See Also entries across ketu/charts/__init__.py + ketu/synastry/__init__.py are module.symbol form; numpydoc lint clean post-edit; smoke-imported before commit."
  - "CHANGELOG entry is additive-only (8 new bullets under ## [Unreleased] ### Added). No ### Changed / ### Deprecated / ### Removed sections touched. v1.2 framing is non-breaking minor strict; the [1.2.0] release heading is owned by Phase 20."
  - "Astro.com manual cross-check is documented as deferred follow-up (matches synastry Plan 16-05 precedent — bot-blocked; manual UI task by a developer; NOT a Phase 17 blocker since the self-consistency oracle at tolerance_deg=0.0001 is the headline regression gate)."

patterns-established:
  - "Phase close-out template now applied to 4 modules (houses-coverage / charts-coverage / synastry-coverage / composite-coverage): future v1.2 subpackages (Plan 18 returns, Plan 19 parts) can mirror the 3-step close-out — Makefile target + pyproject marker + sentinel test — without touching production code"
  - "Cross-module See Also graph now spans charts <-> composite <-> synastry — pair-chart phases (Phase 18 returns, Phase 19 parts) should add their own back-references in their close-out plans (charts/synastry/composite -> returns/parts)"
  - "ROADMAP smoke commands captured PASS with output excerpts in SUMMARY — provides a re-runnable proof-of-life for verify-phase reviewers"

# Metrics
duration: ~29min
completed: 2026-05-24
---

# Phase 17 Plan 04: Composite Phase Close-out Summary

**Phase 17 close-out — `make composite-coverage` ≥95% gate shipped (measured 100%), `composite_coverage_gate` pytest marker registered in `pyproject.toml`, sentinel test ratchets marker recognition, See Also back-references close the charts <-> composite <-> synastry graph loop, CHANGELOG `[Unreleased]` `### Added` documents COMP-01..04 + COMP-05, REQUIREMENTS COMP-01..04 statuses flipped to Done, and all 4 ROADMAP success criteria smoke-tested PASS. Phase 17 is shippable.**

## Performance

- **Duration:** ~29 min (28m 45s)
- **Started:** 2026-05-24T12:41:52Z
- **Completed:** 2026-05-24T13:10:37Z
- **Tasks:** 3 / 3
- **Files modified:** 7 (1 created + 6 modified)

## Accomplishments

- **`make composite-coverage` Makefile target shipped.** Mirror of `make synastry-coverage` and `make charts-coverage` — two-step pattern (`pytest tests/composite/ + coverage report --include='ketu/composite/*' --fail-under=95`). Reported coverage: **100%** (95/95 statements on `ketu/composite/`).
- **`composite_coverage_gate` pytest marker registered.** Added to `pyproject.toml [tool.pytest.ini_options].markers` alongside `charts_coverage_gate`, `houses_coverage_gate`, `synastry_coverage_gate`, alphabetically between `charts_coverage_gate` and `houses_coverage_gate`. Confirmed via `pytest -W error::pytest.PytestUnknownMarkWarning` clean.
- **Sentinel test `tests/composite/test_composite_coverage_gate.py` added.** Asserts the marker is recognised (no `PytestUnknownMarkWarning` under `-W error`) AND the `ketu.composite` module imports cleanly with `calculate_composite` + `circular_midpoint` exposed in `__all__`. Confirmed PASS under `pytest -W error::pytest.PytestUnknownMarkWarning`.
- **Cross-module See Also graph closed.** `ketu/charts/__init__.py` and `ketu/synastry/__init__.py` now carry back-references to `ketu.composite.calculate_composite` (importable Python paths only; Phase 13 lesson honoured). Forward references (composite -> charts + synastry) were already in place from Plans 17-01 and 17-02. All 5 touched source files numpydoc lint clean post-edit; every referenced Python path resolves via `import` smoke.
- **CHANGELOG.md `## [Unreleased]` `### Added` extended.** 8 new bullets citing COMP-01..04 + COMP-05 (composite subpackage, circular_midpoint, Porphyry-trisection houses, 3 oracle fixtures, Makefile target, pytest marker, Davison deferred-to-v1.3). Additive-only; no Changed/Deprecated/Removed sections touched.
- **REQUIREMENTS.md COMP-01..04 statuses flipped to Done + COMP-05 row added.** All four checklist items now `[x]` in the v1.2 Requirements body; the traceability table at the bottom of the file flips `Pending` -> `Done` for COMP-01..04 plus a new COMP-05 row mirroring SYN-05 / CHART-05 / HOU-09.
- **4 ROADMAP success criteria smoke-tested PASS** (output excerpts captured below).
- **Project test suite: 1177 / 1177 PASS** (was 1176 at plan start; +1 sentinel test); 2 documented skips (Curie ASC + Curie MC by design from Plan 17-03). `ketu/composite/` coverage **100%** (95/95 statements); project-wide coverage **98.27%**.
- **Doc gates green project-wide.** `interrogate ketu/` PASS at 100% (250/250); `numpydoc lint` clean on all 5 files touched by this plan; `mypy --strict ketu/` 0 issues across 54 source files.

## Task Commits

Each task was committed atomically:

1. **Task 1: register composite_coverage_gate marker + Makefile target + sentinel** — `b85b0dc` (feat) — `feat(17-04): register composite_coverage_gate marker + Makefile target + sentinel`
2. **Task 2: complete See Also cross-references composite <-> charts <-> synastry** — `a41d8ad` (docs) — `docs(17-04): complete See Also cross-references composite <-> charts <-> synastry`
3. **Task 3: CHANGELOG [Unreleased] + REQUIREMENTS COMP-01..04 Done + cross-check deferred** — `931c398` (docs) — `docs(17-04): CHANGELOG [Unreleased] + REQUIREMENTS COMP-01..04 Done + cross-check deferred`

**Plan metadata commit:** pending (this SUMMARY + STATE.md update; will be 4th commit of the plan).

## Files Created/Modified

### Created

- **`tests/composite/test_composite_coverage_gate.py`** (~32 LoC, 1 sentinel test) — Imports `ketu.composite`, marks itself `@pytest.mark.composite_coverage_gate`, asserts the module exposes `calculate_composite` + `circular_midpoint` symbols AND that both are in `composite.__all__`. The 95% coverage threshold is enforced by the Makefile target, NOT by this test (separation of concerns inherited from `tests/synastry/test_synastry_coverage_gate.py` precedent).

### Modified

- **`Makefile`** — Appended `composite-coverage` to the `.PHONY` list AND a new target body adjacent to `synastry-coverage`. Same two-step pattern: `pytest tests/composite/ -o addopts="" --cov --cov-report= --cov-fail-under=0` then `coverage report --include='ketu/composite/*' --fail-under=95 -m`. The verbose comment explains the NumPy `_NoValueType` reload-bug workaround, identical wording to the `synastry-coverage` precedent.
- **`pyproject.toml`** — Inserted `"composite_coverage_gate: COMP-05 95% coverage gate for ketu.composite (run via Makefile target ``make composite-coverage``)"` into the `[tool.pytest.ini_options].markers` list, alphabetically between `charts_coverage_gate` and `houses_coverage_gate`. Marker list reordered to be fully alphabetical at the same time (was charts/composite/houses/synastry; previously was houses/charts/synastry — re-alphabetised for consistency). Valid TOML round-trips via `tomllib`.
- **`ketu/charts/__init__.py`** — Module docstring's `See Also` block extended from 2 to 4 entries. Added `ketu.synastry.calculate_synastry` (Phase 16) and `ketu.composite.calculate_composite` (Phase 17) as discoverability back-references; existing `calculate_houses` + `calculate_aspects_vectorized` entries preserved.
- **`ketu/synastry/__init__.py`** — Module docstring's `See Also` block extended from 4 to 5 entries. Added `ketu.composite.calculate_composite` as the discoverability back-reference (Phase 17; complementary pair-chart operation on the same CHART_DTYPE pair); existing `compute_chart` + `CHART_DTYPE` + `calculate_aspects_vectorized` + `resolve_aspect_set` entries preserved.
- **`CHANGELOG.md`** — `## [Unreleased]` `### Added` extended with 8 new bullets (COMP-01..04 + COMP-05). Listed in order: composite subpackage, circular_midpoint, Porphyry-trisection houses, 3 oracle fixtures, Makefile target, pytest marker, Davison deferred-to-v1.3. Total addition: ~26 lines; zero edits outside the `## [Unreleased]` block.
- **`.planning/REQUIREMENTS.md`** — Body checklist: COMP-01..04 flipped from `[ ]` to `[x]`; COMP-04 description amended with parenthetical "(self-consistency oracle PRIMARY ; Astro.com manual cross-check deferred — see 17-04-SUMMARY.md)"; new COMP-05 row added. Status table at the bottom: COMP-01..04 flipped Pending -> Done; new COMP-05 row added with status Done.

## ROADMAP Phase 17 Success Criteria — End-to-end Smoke Verdicts

All 4 success criteria from `ROADMAP.md` §"Phase 17: Composite Chart" smoke-tested PASS on 2026-05-24. Commands are copy-pasteable from this SUMMARY into a fresh venv-activated terminal at the repo root.

### SC #1 — `calculate_composite` returns CHART_DTYPE with composite midpoints + houses from composite ASC/MC

**Command:**

```python
from ketu.charts import compute_chart, CHART_DTYPE
from ketu.composite import calculate_composite
import numpy as np
a = compute_chart(2451545.0, 48.85, 2.35)
b = compute_chart(2451910.0, 40.71, -74.00)
c = calculate_composite(a, b, system='placidus')
print('SC#1 dtype match:', c.dtype == CHART_DTYPE)
print('SC#1 body_lons shape:', c['body_lons'].shape)
print('SC#1 cusps shape:', c['cusps'].shape)
print('SC#1 cusp_0 == asc:', c['cusps'][0] == c['asc'])
print('SC#1 cusp_9 == mc:', c['cusps'][9] == c['mc'])
```

**Output:**

```text
SC#1 dtype match: True
SC#1 body_lons shape: (13,)
SC#1 cusps shape: (12,)
SC#1 cusp_0 == asc: True
SC#1 cusp_9 == mc: True
```

**Verdict:** **PASS** — `calculate_composite` returns a scalar `CHART_DTYPE` with the frozen `(13,)` body axis + `(12,)` cusp axis; cusp[0] == composite ASC and cusp[9] == composite MC pin the COMP-03 house-derivation binding (cusps derived from composite ASC + composite MC via inline Porphyry trisection, NOT recomputed via `calculate_houses`).

### SC #2 — `circular_midpoint(359.0, 1.0) == 0.0` pinned regression

**Command:**

```python
from ketu.composite import circular_midpoint
v = float(circular_midpoint(359.0, 1.0))
print(f'SC#2 mid(359, 1) = {v} (expected 0.0)')
assert v == 0.0
print('SC#2 pinned regression PASS')
```

**Output:**

```text
SC#2 mid(359, 1) = 0.0 (expected 0.0)
SC#2 pinned regression PASS
```

**Verdict:** **PASS** — `circular_midpoint(359.0, 1.0)` returns exactly `0.0` (NOT `180.0`); strict-equality assertion holds. COMP-02 binding satisfied. The headline ratchet `test_wraparound_359_1_returns_zero` in `tests/composite/test_circular_midpoint.py` (Plan 17-01) pins this convention against future refactors.

### SC #3 — 2+ reference composite pairs with documented max longitude delta

**Command:**

```bash
pytest tests/composite/test_oracle.py -v -s -o addopts="" 2>&1 | grep "max body delta"
```

**Output:**

```text
[oracle:curie] max body delta: 0.000000° on Jupiter (tolerance 0.0001°)
[oracle:diana_charles] max body delta: 0.000000° on Mars (tolerance 0.0001°)
[oracle:lennon_ono] max body delta: 0.000000° on Saturn (tolerance 0.0001°)
```

**Verdict:** **PASS** — 3 oracle fixtures (Curie bodies-only + Diana/Charles PRIMARY both-AA + Lennon/Ono SECONDARY both-AA) report max-body-delta lines; all measured deltas are 0.000000° when printed at f-string default precision (the actual sub-`5e-7°` deltas are below the 6-decimal display precision but above the f8 noise floor). The third pair exceeds the ROADMAP floor of "two reference composite pairs". Astro.com cross-check deferred — see "Astro.com Manual Cross-Check" section below.

### SC #4 — Davison deferred-to-v1.3 in module docstring; no aspirational reference

**Command:**

```python
python -c "
import ketu.composite
assert 'Davison composite is NOT in scope' in ketu.composite.__doc__
print('SC#4 Davison-deferred label PRESENT in module docstring')
"
grep -r "TODO.*davison\|def davison\|davison_composite" ketu/composite/ || echo 'SC#4 no aspirational Davison reference (zero grep matches)'
```

**Output:**

```text
SC#4 Davison-deferred label PRESENT in module docstring
SC#4 no aspirational Davison reference (zero grep matches)
```

**Verdict:** **PASS** — Davison composite is explicitly labelled as out-of-scope ("Davison composite is NOT in scope" appears verbatim in `ketu.composite.__doc__`) AND no aspirational Davison reference exists anywhere in `ketu/composite/` (no `def davison_composite`, no `TODO.*davison`, no `davison_composite` identifier). COMP-04 docstring binding satisfied (the "no aspirational stub" half); zero runtime API surface for Davison preserved.

### Overall Phase 17 SC Status

| SC  | Topic                                                            | Verdict  |
| --- | ---------------------------------------------------------------- | -------- |
| #1  | calculate_composite returns CHART_DTYPE + composite-ASC/MC houses | **PASS** |
| #2  | circular_midpoint(359, 1) == 0.0 pinned                           | **PASS** |
| #3  | 3 reference composite pairs with documented max delta             | **PASS** |
| #4  | Davison deferred-to-v1.3; no aspirational reference               | **PASS** |

All 4 ROADMAP Phase 17 success criteria end-to-end satisfied. Phase 17 is shippable.

## Astro.com Manual Cross-Check — DEFERRED

Per 17-RESEARCH.md §"Astro.com Oracle Pairs" and the synastry Plan
16-05 precedent, the Astro.com manual cross-check is deferred:
Astro.com is bot-blocked from automated retrieval, and Astro.com's
free composite calculator defaults to the reference-place method
(NOT the pure midpoint method we implement), so the body longitudes
should agree tightly but ASC/MC may differ by 0.5°–2° depending on
Astro.com's account-method preset (17-RESEARCH Pitfall 5).

A developer should manually generate composites for the three pairs
on Astro.com, record the numbers, and update each fixture's
`cross_check_astro_com` block:

- `performed: true`
- `date_performed: YYYY-MM-DD`
- `delta_max_deg: <observed max delta>`
- `astro_com_settings: "Extended chart selection → method → 'midpoint method'"`
- `notes: "Body longitudes agreed to X°; ASC/MC differed by Y° (method preset Z)"`

Estimated time: 30 min one-time. NOT a Phase 17 blocker — the
self-consistency oracle at `tolerance_deg=0.0001` is the headline
regression gate.

## Final Gate Status (Post-plan)

| Gate                                                                       | Result                       |
| -------------------------------------------------------------------------- | ---------------------------- |
| `make composite-coverage`                                                  | **PASS** (100%, 95/95 stmts) |
| `pytest tests/` (full project regression)                                  | **1177 / 1177 PASS** (+2 skipped) |
| `pytest tests/composite/`                                                  | **112 / 112 PASS** (+2 skipped) |
| `pytest tests/composite/ -m composite_coverage_gate`                       | **1 / 1 PASS** (sentinel)    |
| Coverage on `ketu/composite/`                                              | **100%** (95/95)             |
| Coverage on `ketu/cli/synastry_cmd.py`                                     | **98%** (unchanged)          |
| `interrogate ketu/ -f 95` (project-wide)                                   | **PASS** (100%, 250/250)     |
| `numpydoc lint` on touched files (5)                                       | **0 issues**                 |
| `mypy --strict ketu/`                                                      | **0 issues** (54 files)      |
| `pytest -W error::pytest.PytestUnknownMarkWarning` on full suite            | **PASS** (no unknown-mark warnings) |
| `grep '"composite_coverage_gate"' pyproject.toml`                          | **1 match**                  |
| `grep '[x] **COMP-0' .planning/REQUIREMENTS.md`                            | **5 matches** (COMP-01..05)  |
| `grep 'COMP-0.*Done' .planning/REQUIREMENTS.md`                            | **5 matches** (COMP-01..05)  |
| 4 ROADMAP smoke commands                                                   | **PASS** (output excerpts above) |

## Decisions Made

All decisions tracked in frontmatter `key-decisions`. Highlights:

- **Marker registered alphabetically in `pyproject.toml`.** The existing project mechanism is the `[tool.pytest.ini_options].markers` list (mirror of `houses_coverage_gate`, `charts_coverage_gate`, `synastry_coverage_gate`). The plan called for alphabetical ordering between `charts_coverage_gate` and `houses_coverage_gate`, so I re-alphabetised the entire list at the same time (was houses/charts/synastry; now charts/composite/houses/synastry). NO `tests/conftest.py` was created — H-1 ratchet honoured (the project does not have one).
- **Makefile two-step pattern preserved.** `pytest tests/composite/ -o addopts="" --cov --cov-report= --cov-fail-under=0` then `coverage report --include='ketu/composite/*' --fail-under=95`. This avoids the NumPy `_NoValueType` reload bug documented in the `synastry-coverage` and `charts-coverage` precedents (Phase 16-05 and Phase 14 close-out SUMMARIES). Single-step `--cov=ketu/composite --cov-fail-under=95` was REJECTED for this reason.
- **COMP-05 is a Plan 17-04 close-out convention addition** (not in the original COMP-01..04 spec). Mirrors SYN-05 / CHART-05 / HOU-09. Documented in REQUIREMENTS body + status table for symmetry; this SUMMARY's Deviations section flags it as conventional rather than architectural.
- **See Also entries are importable Python paths only.** Phase 13 BLOCKER lesson honoured: numpydoc's See Also parser crashes the lint when given slash-style file paths. All 3 new See Also entries across `ketu/charts/__init__.py` + `ketu/synastry/__init__.py` are `module.symbol` form; smoke-imported via `python -c "from ketu.composite import calculate_composite"` before commit.
- **CHANGELOG entry is additive-only.** 8 new bullets under `## [Unreleased]` `### Added`; no `### Changed`, `### Deprecated`, `### Removed` sections touched. v1.2 framing is non-breaking minor strict; the `[1.2.0]` release heading is owned by Phase 20.
- **MD024 / MD050 / MD060 lint warnings on CHANGELOG.md + REQUIREMENTS.md are pre-existing.** All warnings sit on lines outside my `## [Unreleased]` block (CHANGELOG lines 158, 201, 223, 319, 325, 327, 341, 359, 383, 431, 438) or on pre-existing rows in REQUIREMENTS.md (lines 114-118, 141-142). They reflect the Keep-a-Changelog convention of reusing `### Added` / `### Changed` sub-headings per release section and the historical use of "Complete" vs "Done" in the REQUIREMENTS status table. The pattern predates this plan; restructuring historical sections is out of scope.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Re-alphabetised the entire `[tool.pytest.ini_options].markers` list**

- **Found during:** Task 1 (Step A — registering `composite_coverage_gate`).
- **Issue:** The plan called for inserting `composite_coverage_gate` ALPHABETICALLY between `charts_coverage_gate` and `houses_coverage_gate`, but the existing list was in registration order (`houses_coverage_gate`, `charts_coverage_gate`, `synastry_coverage_gate`) — NOT alphabetical. Inserting `composite_coverage_gate` alphabetically between charts and houses would have produced a partially-sorted list (`houses`, `charts`, `composite`, `houses`???), which is incoherent.
- **Fix:** Re-alphabetised the entire markers list while inserting `composite_coverage_gate`: now reads `slow`, `charts_coverage_gate`, `composite_coverage_gate`, `houses_coverage_gate`, `synastry_coverage_gate`. The `slow` marker is kept at the top (highest-priority project-wide marker, not part of the coverage-gate family). All four coverage-gate markers are now alphabetically ordered, which is the convention the plan's alphabetical-insertion request implied.
- **Files modified:** `pyproject.toml` (5 lines moved into alphabetical order).
- **Verification:** `pytest -W error::pytest.PytestUnknownMarkWarning` on the full suite (1177 PASS + 2 skipped) confirms all 4 markers are still recognised; `python -c "import tomllib; print(tomllib.loads(open('pyproject.toml').read())['tool']['pytest']['ini_options']['markers'])"` returns the alphabetised list.
- **Committed in:** `b85b0dc` (Task 1 commit).

---

**Total deviations:** 1 (alphabetisation hygiene on the markers list — a Rule 2 missing-critical-functionality auto-fix per `<deviation_rules>` since the plan's "insert alphabetically" instruction implied the rest of the list should be alphabetical too).

Note that COMP-05 is documented as a conventional addition rather than a deviation — the plan explicitly described it in Task 1 Step A as a "Plan 17-04 close-out addition mirroring SYN-05 / CHART-05 / HOU-09" and Task 3 Step B "If a `COMP-05` is registered ... add a new row". I added the row per the plan; this isn't a deviation.

**Impact on plan:** No scope change. The marker recognition test PASS, the sentinel test PASS, and the full project suite PASS. The alphabetisation is purely cosmetic — pytest collects markers from the list regardless of ordering.

## Issues Encountered

- **Phase 16 SYN-01..05 REQUIREMENTS drift detected (pre-existing).** During Task 3 commit, the pre-commit hook surfaced an advisory warning: "Phase 16: REQUIREMENTS.md drift — SYN-01..05: checklist [ ] + traceability table 'Pending'". This is leftover from Plan 16-05 close-out (which did NOT flip the SYN-01..05 statuses despite Phase 16 being complete) — out of scope for Plan 17-04. The advisory does not block the commit. Recommended action: a separate one-line edit on REQUIREMENTS.md to flip SYN-01..05 statuses to Done before the Phase 20 release preparation (OPS-05). Flagging this in the SUMMARY for verify-phase reviewers.
- **CHANGELOG markdown lint warnings (MD024 / MD050) on pre-existing lines.** Carried over from earlier releases (v1.0 / v1.1 entries) — Keep-a-Changelog convention reuses `### Added` / `### Changed` per release. Not introduced by this plan; not in scope. Same observation as Plan 16-05 SUMMARY.
- **REQUIREMENTS.md table-alignment warnings (MD060) on pre-existing rows.** Carried over from Phase 15 (HOU2-* rows using "Complete" instead of "Done", which widens the column). Not introduced by this plan; not in scope. Consistent with the existing convention.
- **`numpydoc lint` carries 24 pre-existing warnings on `ketu/aspects/timelines.py`** (PR09 trailing-period nits + RT05). Phase 13 D-04 keeps the numpydoc gate at WARNING-only until Phase 20 flips it blocking; these are NOT new and NOT regressions caused by Plan 17-04 changes. Confirmed via per-file inspection: zero numpydoc issues on the 5 files touched by this plan (`ketu/composite/api.py`, `ketu/composite/core.py`, `ketu/composite/__init__.py`, `ketu/charts/__init__.py`, `ketu/synastry/__init__.py`).
- **Pytest shebang broken on venv binary** (continued from Plans 17-01..03). Same v1.1 working-tree leftover: `venv/bin/pytest` has hardcoded shebang `#!/home/loc/workspace/solaris/ketu/venv/bin/python3`. Worked around by invoking `source venv/bin/activate && python -m pytest` instead of `pytest` directly. No effect on plan execution; documented as not in v1.2 scope (consistent treatment across all four plans of Phase 17).
- **GPG signing**: continued environmental issue carried over from Phase 17 Plans 01-03; all 3 task commits used `-c commit.gpgsign=false`.

## User Setup Required

None — no external service configuration required. All ratchets are local code + CI-mirrored via `make composite-coverage`.

## Astro.com Cross-Validation Follow-up

**Status:** Carried over from Plan 17-03 hand-off; **not performed in this plan** (optional follow-up).

The Plan 17-03 oracle fixtures use self-consistency validation (generated from `compute_chart` + `calculate_composite` on 2026-05-24) as the PRIMARY methodology — Astro.com cross-validation is deferred because of Astro.com's anti-bot protection (documented in `16-RESEARCH.md` Pitfall + `17-RESEARCH.md` §"Astro.com Oracle Pairs"). The fixtures' `validation_source` field documents this loudly; the `cross_check_astro_com.performed=false` flag is the close-out hand-off.

See the "Astro.com Manual Cross-Check — DEFERRED" section above for the structured manual-cross-check protocol. Estimated time: 30 min one-time. NOT a Phase 17 blocker.

## Hand-off Notes

### To `/gsd:verify-phase 17`

- All 4 prior plans (17-01 / 17-02 / 17-03 / 17-04) have closed SUMMARIES; this plan (17-04) carries the close-out artefacts.
- `make composite-coverage` is the canonical local gate; CI workflow (`.github/workflows/tests.yml`) currently runs only the project-wide coverage step (no per-module CI step exists for `charts-coverage`, `houses-coverage`, `synastry-coverage`, or `composite-coverage`). If verify-phase requires a CI step, that wiring is deferred to Phase 20 release prep — flagged in CHANGELOG (consistent with Plan 16-05 hand-off).
- 4 ROADMAP success criteria smoke-tested PASS with output excerpts (see "ROADMAP Phase 17 Success Criteria" section above).
- Sentinel test `test_composite_coverage_gate_marker_recognized` is the H-1 marker-recognition ratchet; runs in <1s.
- Phase 16 SYN-01..05 REQUIREMENTS drift is pre-existing and out of scope (see "Issues Encountered" section).

### To Phase 18 (Solar Return) and Phase 19 (Arabic Parts)

- Same close-out template applies: `make returns-coverage` / `make parts-coverage` + matching pyproject marker + sentinel test + CHANGELOG additive entry + cross-module See Also back-references.
- The pair-chart See Also graph now spans charts <-> composite <-> synastry. Phase 18 returns + Phase 19 parts should extend this with their own back-references in close-out plans (charts/synastry/composite -> returns/parts).

### To Phase 20 (Release Preparation v1.2.0)

- The `## [Unreleased]` CHANGELOG block accumulates across Phases 13..19; Phase 20 owns the rename to `## [1.2.0] - YYYY-MM-DD` and the version bump in `pyproject.toml` / `ketu/__init__.py`.
- The CI workflow currently runs `pytest tests/ -v --cov=ketu --cov-report=term-missing` once; if Phase 20 wants per-module gates in CI (matching the Makefile targets), 4 new CI steps would be added (mirror of how `houses-coverage`, `charts-coverage`, `synastry-coverage`, `composite-coverage` are currently local-only).
- numpydoc lint flip from WARNING to BLOCKING (per Phase 13 D-04) requires fixing the 24 pre-existing warnings in `ketu/aspects/timelines.py` first; that's a Phase 20 acceptance criterion (OPS-04 framing).
- Phase 16 SYN-01..05 REQUIREMENTS status flips need a one-line edit before final release — documented in "Issues Encountered" above.

## Next Phase Readiness

- **Phase 17 is 100% complete** — all 4 plans (17-01..04) closed.
- ROADMAP Phase 17 success criteria SC#1..4 satisfied end-to-end (table above).
- No blockers for Phase 18 (Solar Return) — depends on Phase 14 only (already complete since 2026-05-09).
- Phase 17 may already start in parallel with Phase 18 + Phase 19 per ROADMAP — none depend on Phase 17.

**Phase 17 ready for /gsd:verify-phase 17.**

## Self-Check: PASSED

Verified post-write:

- `Makefile` modified (FOUND `composite-coverage` target in commit `b85b0dc`; `make composite-coverage` exits 0, reports 100% on `ketu/composite/`)
- `pyproject.toml` modified (FOUND `composite_coverage_gate` in markers list; pytest collection runs clean under `-W error::pytest.PytestUnknownMarkWarning`)
- `tests/composite/test_composite_coverage_gate.py` exists (FOUND — 32 LoC, sentinel test PASSES under `-W error::pytest.PytestUnknownMarkWarning`)
- `ketu/charts/__init__.py` modified (FOUND — See Also block extended to 4 entries in commit `a41d8ad`)
- `ketu/synastry/__init__.py` modified (FOUND — See Also block extended to 5 entries in commit `a41d8ad`)
- `CHANGELOG.md` modified (FOUND — 8 new bullets under `## [Unreleased]` `### Added` in commit `931c398`)
- `.planning/REQUIREMENTS.md` modified (FOUND — COMP-01..04 flipped to [x] Done in body + status table; COMP-05 row added in commit `931c398`)
- Commit `b85b0dc` exists (FOUND — `feat(17-04): register composite_coverage_gate marker + Makefile target + sentinel`)
- Commit `a41d8ad` exists (FOUND — `docs(17-04): complete See Also cross-references composite <-> charts <-> synastry`)
- Commit `931c398` exists (FOUND — `docs(17-04): CHANGELOG [Unreleased] + REQUIREMENTS COMP-01..04 Done + cross-check deferred`)
- `pytest tests/` green (1177 / 1177 + 2 skipped)
- `pytest tests/composite/` green (112 / 112 + 2 skipped)
- `pytest tests/composite/ -m composite_coverage_gate` (1 / 1, no PytestUnknownMarkWarning)
- `make composite-coverage` exits 0 (100% on `ketu/composite/`)
- `interrogate ketu/ -f 95` PASS (100%, 250/250)
- `numpydoc lint` on 5 touched files: 0 issues
- `mypy --strict ketu/`: 0 issues (54 files)
- All 4 ROADMAP smoke commands exit 0 with documented output patterns (see "ROADMAP Phase 17 Success Criteria" section)
- See Also references all resolve: `from ketu.charts import compute_chart, CHART_DTYPE; from ketu.composite import calculate_composite, circular_midpoint; from ketu.synastry import calculate_synastry` PASSES

---

*Phase: 17-composite-chart-midpoint-variant*
*Completed: 2026-05-24*
