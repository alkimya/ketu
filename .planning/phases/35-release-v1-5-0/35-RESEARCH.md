# Phase 35: Release v1.5.0 — Research

**Researched:** 2026-06-04
**Domain:** Python package release engineering — version bump, CHANGELOG date-stamping,
UPGRADING, README, conf.py bump, PyPI OIDC publish ceremony (reuses v1.4.0 infra proven
in Phase 32)
**Confidence:** HIGH (all claims verified against live repo files and live venv 2026-06-04)

---

## Summary

Phase 35 is the FINAL phase of milestone v1.5 (Lunar Declination & Harmonics Debt). All
three predecessor phases (33–34) are complete. The release infrastructure is proven from
Phase 20 (v1.2.0), Phase 27 (v1.3.0), and Phase 32 (v1.4.0): `publish.yml` is wired,
OIDC trusted publishing is configured on PyPI, and the pre-flight+publish ceremony is
established.

This phase is MECHANICAL. There are no new features to implement. The two plan slots map
directly to REL-01 and REL-02/REL-03:
- **35-01** (wave 1, autonomous): version bump + date-stamp root CHANGELOG + sync
  fr/CHANGELOG + add UPGRADING `v1.4 -> v1.5` + update README Roadmap + date-stamp
  docs/source/changelog.md + bump conf.py.
- **35-02** (wave 2, human-gated): full pre-flight (HARD GATES) → BLOCKING human
  go/no-go → tag v1.5.0 + push tag + push origin/main + GitHub release + post-publish
  smoke from PyPI.

**Gold-standard precedent:** Phase 32 (v1.4.0 release). This RESEARCH.md mirrors the
Phase 32 RESEARCH.md structure exactly and flags every v1.5-specific delta.

**Four concrete deltas from Phase 32 that change what Plan 35-01 must do:**

1. **CHANGELOG.md already has a `[1.5.0] - Unreleased` section** (authored during Phases
   33/34 docs work). Unlike v1.4 (where the block needed to be authored fresh from
   scratch), v1.5 only requires replacing `Unreleased` with the real release date. The
   content is complete and uses the correct root format (`### Added` / `### Changed` /
   `### Fixed` / `### Notes` — no version-suffix like `### Added 1.5.0`).

2. **`docs/source/conf.py` is at `release = "1.4.0"` / `version = "1.4.0"` and MUST be
   bumped.** This is the OPPOSITE of the Phase 32 situation (where conf.py was pre-bumped
   by Phase 31 and explicitly must NOT be touched). For v1.5, Phase 33/34 did NOT
   pre-bump conf.py, so Plan 35-01 MUST bump it along with pyproject.toml and
   ketu/__init__.py. Planner must not replicate "Phase 32 Pitfall 5 / Pitfall 8"
   (skipping conf.py because it was pre-bumped) — that pitfall is INVERTED here.

3. **mypy --strict is ALREADY CLEAN.** Phase 32 required fixing a pre-existing
   `ketu/synastry/api.py:392 no-any-return` error before tagging. That fix was delivered
   in Plan 32-01. As of 2026-06-04, `python -m mypy --strict ketu/` reports zero errors
   ("Success: no issues found in 69 source files"). No mypy fix task is needed in 35-01.

4. **`fr/CHANGELOG.md` has NO `[1.5.0]` section yet** (top section is `[1.4.0] -
   2026-06-03`). A new French `[1.5.0] - <date>` section must be authored in 35-01,
   translating the six Added bullets, two Changed bullets, two Fixed bullets, and two
   Notes. This is the same pattern as Phase 32 (fr did not have [1.4.0] either).

**Locked user constraint (feedback_validation_review_before_release):** The user
personally reviews the entire milestone BEFORE any irreversible action. Plan 35-02 MUST
contain a `type="checkpoint:human-verify" gate="blocking"` task BEFORE the tag push and
PyPI publish. Auto-publish is NOT acceptable.

**Primary recommendation:** Two sequential plans mirroring Phase 32:
- **35-01** (wave 1, autonomous): three file bumps (pyproject.toml + ketu/__init__.py +
  docs/source/conf.py), date-stamp root CHANGELOG `[1.5.0]`, date-stamp
  docs/source/changelog.md `[1.5.0]`, author fr/CHANGELOG `[1.5.0]` French translation,
  add UPGRADING `## v1.4 -> v1.5`, update README.
- **35-02** (wave 2, human-gated): full v1.5-aware pre-flight (HARD GATES) → BLOCKING
  human go/no-go → tag v1.5.0 + push tag + push origin/main + GitHub release
  (sdist+wheel) → post-publish fresh-venv smoke from PyPI.

---

## DELTAS FROM PHASE 32 (the single most important section for the planner)

| Item | Phase 32 situation | Phase 35 situation | Action required |
|------|-------------------|--------------------|-----------------|
| Root CHANGELOG `[1.5.0]` block | Did NOT exist — had to be authored fresh | **EXISTS as `[1.5.0] - Unreleased`** (line 10) | Only date-stamp: replace `Unreleased` with real date |
| Root CHANGELOG `[1.5.0]` format | N/A (fresh authoring) | Uses root format: `### Added` / `### Changed` / `### Fixed` / `### Notes` (no version suffix) | No format fix needed — already correct |
| Root CHANGELOG `### Changed` content | N/A | Has two bullets (H{h}-{k} naming + find_aspect_timing dyn_coef=) — **NOT empty** | No action — content is complete |
| `docs/source/changelog.md` `[1.5.0]` | Written in Phase 31 with `2026-06-XX` placeholder | **EXISTS as `[1.5.0] - Unreleased`** (line 8) | Date-stamp: replace `Unreleased` with real date |
| `docs/source/conf.py` | Pre-bumped to 1.4.0 in Phase 31 — **do NOT touch** (Pitfall 5/8) | At `1.4.0` — **MUST be bumped to 1.5.0** | Edit lines 14–15: `"1.4.0"` → `"1.5.0"` |
| `pyproject.toml` | line 7: `"1.3.0"` → `"1.4.0"` | **line 7: `"1.4.0"` → `"1.5.0"`** | Same pattern |
| `ketu/__init__.py` | line 57: `"1.3.0"` → `"1.4.0"` | **line 57: `"1.4.0"` → `"1.5.0"`** | Same pattern |
| `fr/CHANGELOG.md` | Top section was `[1.3.0]` — had to add `[1.4.0]` French section | **Top section is `[1.4.0]` — must add `[1.5.0]` French section** | Same pattern — translate 6+2+2+2 bullets |
| `mypy --strict` pre-flight | FAIL (1 error at synastry/api.py:392) — must fix first | **PASS (zero errors, 69 source files)** | No fix task needed |
| Test count | 1537 passed, 2 skipped | **1626 passed, 2 skipped** | Pre-flight expects ~1626 |
| `UPGRADING.md` top section | `## v1.2 -> v1.3` (no v1.3 → v1.4 section) | `## v1.3 -> v1.4` (exists) — **no `## v1.4 -> v1.5` section** | Add `## v1.4 -> v1.5` as new first section |
| README `## What's New` section | Existed for v1.3.0 but not v1.4.0 — had to add | **No `## What's New` sections at all** (README was rewritten) | README update strategy changed — see below |
| Smoke assertions | H7 angles + Chiron orb=4.0 + Chiron@1920 + no-swisseph | **declination() + is_ascending_declination() + is_out_of_bounds() + --harmonics h7 + no-swisseph** | Four new v1.5 assertions |
| v1.5.0 git tag | Does not exist | Does not exist | Must create |
| PyPI slot 1.5.0 | Available | **Available (confirmed via JSON API)** | |

---

## Version Bump Locations (ALL Files to Change)

Verified 2026-06-04 by reading all files directly.

| File | Line | Current value | Target value | Notes |
|------|------|---------------|--------------|-------|
| `pyproject.toml` | 7 | `version = "1.4.0"` | `version = "1.5.0"` | Build system source of truth |
| `ketu/__init__.py` | 57 | `__version__ = "1.4.0"` | `__version__ = "1.5.0"` | Runtime source of truth |
| `docs/source/conf.py` | 14 | `release = "1.4.0"` | `release = "1.5.0"` | **MUST bump — NOT pre-bumped by Phases 33/34** |
| `docs/source/conf.py` | 15 | `version = "1.4.0"` | `version = "1.5.0"` | Same file, adjacent line |

**Total files to edit: 3** (`pyproject.toml`, `ketu/__init__.py`, `docs/source/conf.py`).

**CRITICAL PITFALL (inverted from Phase 32):** Phase 32 Pitfall 5/8 was "don't touch
conf.py — already bumped." That pitfall is INVERTED here: conf.py was NOT pre-bumped.
If Plan 35-01 skips conf.py, RTD will continue to show 1.4.0 after the release.

Gate: `pip install -e . -q && pytest tests/test_version.py -v`

---

## CHANGELOG.md Current State and Required Delta

**Verified 2026-06-04 by reading CHANGELOG.md directly.**

### Current structure

```
## [1.5.0] - Unreleased   ← line 10 (the only change needed: date-stamp)
## [1.4.0] - 2026-06-03   ← line 70 (already dated, untouched)
## [1.3.0] - 2026-06-01   ← (further down, untouched)
```

**The `[1.5.0]` section is COMPLETE in content.** The only change needed is replacing
`Unreleased` with the real release date (today's UTC date in `YYYY-MM-DD` form).

### [1.5.0] section content (verified complete)

The section contains:

**`### Added`** (6 bullets):
- `declination(jdate, body)` — equatorial declination δ (Phase 33)
- `declination_velocity(jdate, body)` — dδ/dt (Phase 33)
- `is_ascending_declination(jdate, body)` — montant/descendant helper (Phase 33)
- `is_out_of_bounds(jdate, body)` — OOB via instantaneous obliquity (Phase 33)
- `CHART_DTYPE` — `body_decl` field additive (Phase 33)
- `--harmonics h<N>` CLI surface (Phase 34)

**`### Changed`** (2 bullets — NOT empty, which is acceptable for root format):
- `H{h}-{k}` naming promoted to public API contract (Phase 34)
- `find_aspect_timing` gains `dyn_coef=` parameter (Phase 34)

**`### Fixed`** (2 bullets):
- Lunar node mean speed corrected (Phase 33)
- `calculate_aspects_batch` duplicate-pair rows eliminated (Phase 33)

**`### Notes`** (2 bullets — Kala impact note + is_ascending(β) unchanged):
- Non-standard subsection for v1.5 (not a Keep-a-Changelog standard section).
  This is acceptable — it was authored during Phase 33/34 and documents
  the additive-but-noteworthy `body_decl` dtype change for Kala.

### Required action in Plan 35-01

1. Read CHANGELOG.md line 10 to confirm `## [1.5.0] - Unreleased`.
2. Replace `Unreleased` with today's UTC date (`date -u +%F`).
3. Confirm `## [1.4.0] - 2026-06-03` at line 70 is untouched.
4. Assert no `## [Unreleased]` remains.

---

## docs/source/changelog.md Date-Stamp

**Verified 2026-06-04.**

`docs/source/changelog.md` line 8 reads: `## [1.5.0] - Unreleased`

Identical pattern to the root CHANGELOG: replace `Unreleased` with the real release date.

**Also verify:** The `## [1.2.0] - 2026-04-XX` placeholder (line 62 approx) is OUT OF
SCOPE — pre-dates Phase 32, left as-is per established practice. The `[1.3.0]` section
at line 47 is already dated `2026-06-01` (fixed by Plan 32-01). No action needed beyond
the `[1.5.0]` date-stamp.

---

## fr/CHANGELOG.md Required Delta

**Verified 2026-06-04. Current top section: `## [1.4.0] - 2026-06-03`.**

No `[1.5.0]` section exists. A new French `## [1.5.0] - <date>` section must be added
above `## [1.4.0] - 2026-06-03`. The file uses `### Ajouts` / `### Modifié` headers.

The v1.5 French section must translate:
- 6 `### Ajouts` bullets: declination, declination_velocity, is_ascending_declination,
  is_out_of_bounds, body_decl, --harmonics h<N>
- 2 `### Modifié` bullets: H{h}-{k} naming contract, find_aspect_timing dyn_coef=
- 2 `### Corrigé` bullets: nœuds lunaires vitesse, calculate_aspects_batch doublons
- 2 `### Notes` bullets: is_ascending(β) inchangé, impact Kala (additif)

The EN root CHANGELOG is authoritative (per the fr/ header note).

---

## UPGRADING.md Required Delta

**Verified 2026-06-04.**

`UPGRADING.md` currently has `## v1.3 -> v1.4` as the topmost section (line 6).
There is NO `## v1.4 -> v1.5` section. It must be added as the **new first section**,
before `## v1.3 -> v1.4`.

### Rationale for UPGRADING entry

v1.5 is fully additive — no breaking changes. However, three items warrant migration
notes for downstream consumers (primarily Kala):

1. **`CHART_DTYPE` gains `body_decl`** (additive dtype field): code using named field
   access (`chart["body_lons"]`) is unaffected. Code using positional access or `.view()`
   on the raw dtype must adapt. The field is a `float64[14]` appended at the end.

2. **Lunar node mean speed corrected** (`core.bodies['speed'][10]` and `[11]` changed
   from ~−0.013 to −0.052954 °/day): downstream code reading `core.bodies['speed']`
   for Rahu (10) or Ketu (11) will see the corrected value. Any cached speed ratios
   involving the nodes must be recomputed.

3. **New public API** (purely additive, no migration needed): `declination()`,
   `declination_velocity()`, `is_ascending_declination()`, `is_out_of_bounds()`,
   `--harmonics h<N>` CLI, `H{h}-{k}` naming contract, `find_aspect_timing(dyn_coef=)`.

### `## v1.4 -> v1.5` content to add

```markdown
## v1.4 -> v1.5

### CHART_DTYPE gains body_decl — additive dtype change

In v1.5.0, `CHART_DTYPE` gains a new `body_decl` field (`float64[14]`): equatorial
declination δ for all 14 bodies. This is purely additive — no existing field is removed
or reordered.

- Code using **named field access** (`chart["body_lons"]`, `chart["body_decl"]`) is
  **unaffected** — NumPy structured arrays support named access regardless of field order.
- Code using **positional access** (`chart[..., N]`) or `.view()` on the raw dtype
  **must adapt** — the byte layout changed (new field appended at the end).
- `compute_chart` and `calculate_composite` both populate `body_decl` automatically.

**Kala guidance:** Update `CHART_DTYPE` definitions to include `body_decl`. Named access
patterns require no code changes. A ratchet test in the Ketu test suite pins the dtype
sha256 fingerprint.

### Lunar node mean speed corrected in core.bodies

In v1.5.0, `core.bodies['speed']` for Rahu (index 10) and Ketu (index 11) is corrected
from approximately −0.013°/day to −0.052954°/day (the true nodal regression rate:
360° over ~18.6 years).

- Code that reads `core.bodies['speed'][10]` or `core.bodies['speed'][11]` will see the
  corrected value.
- Any downstream speed-ratio calculations or adaptive step sizes involving the nodes
  will behave more accurately. Recompute any cached values that sourced the old speed.
- The `calculate_speed_ratio` function now sources average speeds from
  `core.bodies['speed']` (single source of truth, was a duplicated table).

### New API surface — additive, no migration needed

All of the following are purely additive. No existing imports, callers, or return types
change:

- `from ketu.calculations import declination` — equatorial declination δ, scalar and
  vectorized.
- `from ketu.calculations import declination_velocity` — dδ/dt in degrees/day.
- `from ketu.calculations import is_ascending_declination` — True when dδ/dt > 0
  (Moon montante biodynamic helper). Distinct from `is_ascending` (β-trajectory).
- `from ketu.calculations import is_out_of_bounds` — True when |δ| > instantaneous
  obliquity ε(jd).
- `--harmonics h<N>` CLI top-level flag — e.g. `ketu --harmonics h7 aspects --date …`
- `H{h}-{k}` naming is a public API contract — dynamic harmonic rows are stable.
- `find_aspect_timing(..., dyn_coef=None)` — optional parameter, backwards compatible.
```

---

## README.md Required Delta

**Verified 2026-06-04.**

The README has NO `## What's New` sections — the v1.4.0 release did not add one
(unlike what was done in Phase 32 for v1.4 which added `## What's New in v1.4.0` to the
README). The current README (356 lines) has only standard sections (Features, Installation,
Quick Start, Advanced Examples, Documentation, Requirements, Supported bodies, etc.) and
a `## Roadmap` section (line 312) with a checklist.

**Strategy for v1.5:** Add two new entries to the `## Roadmap` checklist (line 312) to
document the v1.5 additions, keeping the README minimal. Do NOT add a `## What's New
in v1.5.0` section if none exists for v1.4 — that would create an inconsistency.

Alternatively, verify whether the user/CONTEXT.md specifies a README strategy. Since
there is no CONTEXT.md for Phase 35, Claude's discretion applies.

**Recommended approach:** Add the following two entries to the `## Roadmap` checklist
after the existing `- [x] Data-driven aspect engine with harmonic-based selection`:

```markdown
- [x] Equatorial declination δ, montant/descendant, OOB helpers (`declination`,
  `is_ascending_declination`, `is_out_of_bounds`)
- [x] Dynamic harmonic CLI (`--harmonics h7`) + `H{h}-{k}` naming contract +
  `find_aspect_timing(dyn_coef=)`
```

This is minimal, consistent with the existing README style, and avoids a `What's New`
section without a v1.4 equivalent.

---

## PyPI and Git Tag State

**Verified 2026-06-04 against live repo and PyPI JSON API.**

| Item | State |
|------|-------|
| Current PyPI live version | 1.4.0 |
| `v1.5.0` tag | Does NOT yet exist |
| `v1.4.0` tag | Exists on main |
| PyPI slot `ketu==1.5.0` | **Available** (confirmed: releases = [1.0.0, 1.1.0, 1.2.0, 1.3.0, 1.4.0]) |
| OIDC trusted publisher | Configured from Phase 20 — Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi — no changes needed |

---

## Publish Workflow (publish.yml)

**Verified 2026-06-04 by reading `.github/workflows/publish.yml` directly.**

```yaml
on:
  push:
    tags:
      - 'v*.*.*'          # trigger: push v1.5.0 tag
jobs:
  build:                   # Python 3.11, python -m build --sdist --wheel, twine check
  publish-to-pypi:         # needs build, environment: pypi, id-token: write
                           # uses: pypa/gh-action-pypi-publish@release/v1
```

**No changes to publish.yml are needed for v1.5.0.** Actions versions (Node 24 from
Phase 20, unchanged):
- `actions/checkout@v5`
- `actions/setup-python@v6`
- `actions/upload-artifact@v5` / `actions/download-artifact@v5`
- `pypa/gh-action-pypi-publish@release/v1`

**CRITICAL (from project memory):** Push BOTH the tag AND `origin/main`:
```bash
git push origin v1.5.0     # triggers publish.yml → PyPI
git push origin main        # RTD follows main, not the tag
```
Pushing only the tag leaves RTD docs frozen (feedback_push_main_not_just_tag_on_release).

---

## Quality Gates Status (as of 2026-06-04, verified live)

| Gate | Status | Command | Notes |
|------|--------|---------|-------|
| `pytest tests/ -q` | **PASS** | `python -m pytest tests/` | **1626 passed, 2 skipped** |
| `python -m mypy --strict ketu/` | **PASS** | `make mypy` | Zero errors, 69 source files |
| `python -m interrogate ketu/` | **PASS** | `make doc-gates` | 99.7% (minimum 95%) |
| `python -m numpydoc lint $(...)` | **PASS** | `make doc-gates` | Zero violations |
| `make doctest` | **PASS** | `python -m pytest --doctest-modules ketu/ --no-cov --ignore=ketu/lunar_calendar.py --ignore=ketu/__main__.py` | 65 passed, 1 skipped |
| `fail_under=100` coverage | **PASS** | Built into `pytest tests/` | 100.00% |

**ALL quality gates are currently green. No fixes are required before tagging.**

Note: STATE.md says 1623 tests but live run shows **1626 passed** (3 additional tests
landed after the STATE.md was last updated). This is the correct current count.

---

## Smoke Test Import Paths (v1.5-specific)

**Verified 2026-06-04 by executing functions live in the dev venv.**

The four v1.5 functions are all in `ketu.calculations`:

```python
from ketu.calculations import declination, declination_velocity
from ketu.calculations import is_ascending_declination, is_out_of_bounds
```

These are NOT in `ketu.__all__` (which exports only `bodies`, `aspects`, `signs`,
`HOUSES_DTYPE`, `HighLatitudeError`, `HOUSE_SYSTEMS`, `calculate_houses`, `house_of`).
The smoke test must use the `ketu.calculations` submodule path.

The `--harmonics h7` CLI flag is a TOP-LEVEL flag, not a subcommand flag:

```bash
ketu --harmonics h7 aspects --date 2024-01-01
# NOT: ketu aspects --date 2024-01-01 --harmonics h7  (fails)
```

Live execution results (J2000.0, Moon body_id=1):
- `declination(2451545.0, 1)` → `-10.7460°` (finite, in [-90, 90])
- `is_ascending_declination(2451545.0, 1)` → `False`
- `is_out_of_bounds(2451545.0, 1)` → `False`
- `ketu --harmonics h7 aspects --date 2024-01-01` → shows "Aspect set: h7 (3 aspects:
  H7-1 51°, H7-2 103°, H7-3 154°)"

---

## Fresh-Venv Smoke Test (REL-03) — v1.5.0 Assertions

Four v1.5 assertions to add to the Phase 32 smoke pattern:

1. **`declination(jd, body)`** — returns finite float in [-90, 90]
2. **`is_ascending_declination(jd, body)`** — returns bool (True or False)
3. **`is_out_of_bounds(jd, body)`** — returns bool
4. **`--harmonics h7` CLI** — exits 0 and output contains "H7-1"

Plus the preserved v1.4 assertion (Chiron@1920) and the universal no-swisseph check.

**Complete Fresh-Venv Smoke Test for Plan 35-02:**

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.5.0"

# 1. Verify wheel exists and is pure-Python
ls dist/ketu-${VERSION}-py3-none-any.whl || { echo "FAIL: wheel not found"; exit 1; }

# 2. Verify .npz ships in wheel (unchanged from v1.4, ~578 KB)
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep -q "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }
echo "OK: chiron_coeffs.npz present in wheel"

# 3. Fresh venv
TMP=$(mktemp -d)
trap "rm -rf '$TMP'" EXIT
python -m venv "$TMP"

# 4. Install ONLY the wheel (no .[test] extras → no pyswisseph)
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

# 5. Version check
"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}', f'Bad __version__: {ketu.__version__}'
assert m.version('ketu') == '${VERSION}', f'Bad metadata: {m.version(\"ketu\")}'
print('version OK:', ketu.__version__)
"

# 6. All subpackage imports (including v1.5 declination + v1.4 generate_harmonic_aspects)
"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds
from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects
from ketu.cycles import generate_cycle_series
from ketu.cache import EphemerisCache
from ketu.houses import calculate_houses
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.composite import calculate_composite
from ketu.returns import solar_return
from ketu.parts import calculate_part
from ketu.ephemeris.planets import calc_planet_position
print('all subpackage imports OK')
"

# 7. v1.5 NEW: declination() returns finite float in [-90, 90]
"$TMP/bin/python" -c "
import math
from ketu.calculations import declination
jd = 2451545.0  # J2000.0
d = declination(jd, 1)  # Moon
d_f = float(d)
assert math.isfinite(d_f), f'declination not finite: {d_f}'
assert -90.0 <= d_f <= 90.0, f'declination out of range: {d_f}'
print(f'declination OK: Moon @ J2000 = {d_f:.4f}°')
"

# 8. v1.5 NEW: is_ascending_declination() returns bool
"$TMP/bin/python" -c "
from ketu.calculations import is_ascending_declination
jd = 2451545.0
result = is_ascending_declination(jd, 1)
assert isinstance(result, bool), f'is_ascending_declination not bool: {type(result)}'
print(f'is_ascending_declination OK: Moon @ J2000 = {result}')
"

# 9. v1.5 NEW: is_out_of_bounds() returns bool
"$TMP/bin/python" -c "
from ketu.calculations import is_out_of_bounds
jd = 2451545.0
result = is_out_of_bounds(jd, 1)
assert isinstance(result, bool), f'is_out_of_bounds not bool: {type(result)}'
print(f'is_out_of_bounds OK: Moon @ J2000 = {result}')
"

# 10. v1.5 NEW: --harmonics h7 CLI exits 0 and shows H7 aspects
"$TMP/bin/python" -m ketu --harmonics h7 aspects --date 2024-01-01 > /tmp/h7_out.txt 2>&1
grep -q "H7-1" /tmp/h7_out.txt || { echo "FAIL: --harmonics h7 output missing H7-1"; cat /tmp/h7_out.txt; exit 1; }
echo "OK: --harmonics h7 CLI works: $(grep 'Aspect set' /tmp/h7_out.txt)"

# 11. v1.4 preserved: generate_harmonic_aspects(7) — correct H7 angles
"$TMP/bin/python" -c "
from ketu.aspects import generate_harmonic_aspects
h7 = generate_harmonic_aspects(7)
assert len(h7) == 3, f'Expected 3 H7 rows, got {len(h7)}'
angles = [float(a) for a in h7['angle']]
expected = [360/7, 720/7, 1080/7]
for a, e in zip(angles, expected):
    assert abs(a - e) < 0.01, f'H7 angle off: {a} vs {e}'
print(f'H7 generate_harmonic_aspects OK: {[round(a,4) for a in angles]}')
"

# 12. v1.4 preserved: Chiron resolves at JD 2422324.5 (1920-01-01 — outside old 1950-2050)
"$TMP/bin/python" -c "
import math
from ketu.ephemeris.planets import calc_planet_position
jd = 2422324.5  # 1920-01-01
pos = calc_planet_position(jd, 13)
lon = float(pos[0])
assert math.isfinite(lon), f'Chiron longitude not finite at 1920: {lon}'
assert 0.0 <= lon < 360.0, f'Chiron longitude out of range at 1920: {lon}'
print(f'Chiron 1920 OK: lon={lon:.4f}° (proves 1900-2100 range active)')
"

# 13. pyswisseph NOT installed (AGPL isolation)
"$TMP/bin/python" -c "
import importlib.util
spec = importlib.util.find_spec('swisseph')
assert spec is None, 'FAIL: pyswisseph is importable in runtime venv'
print('pyswisseph NOT in runtime venv: OK')
"

echo "All smoke tests PASSED for ketu==${VERSION}"
```

---

## Pre-flight Script (v1.5.0)

Complete script for Plan 35-02, Task 1:

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.5.0"

echo "=== Pre-flight: ketu ${VERSION} ==="

# 1. Clean working tree on main
test -z "$(git status --porcelain)" || { echo "FAIL: Dirty working tree"; exit 1; }
git branch --show-current | grep -q "^main$" || { echo "FAIL: Not on main branch"; exit 1; }
echo "OK: clean tree on main"

# 2. Version sync in all THREE source-of-truth files
grep -q "version = \"${VERSION}\"" pyproject.toml || { echo "FAIL: pyproject.toml not bumped"; exit 1; }
grep -q "__version__ = \"${VERSION}\"" ketu/__init__.py || { echo "FAIL: __init__.py not bumped"; exit 1; }
grep -q "release = \"${VERSION}\"" docs/source/conf.py || { echo "FAIL: conf.py release not bumped"; exit 1; }
grep -q "version = \"${VERSION}\"" docs/source/conf.py || { echo "FAIL: conf.py version not bumped"; exit 1; }
pip install -e . -q
pytest tests/test_version.py -v
echo "OK: version synced to ${VERSION} in pyproject.toml + ketu/__init__.py + conf.py"

# 3. CHANGELOG [1.5.0] dated (not Unreleased, not XX placeholder)
grep -q "^## \[${VERSION}\] - 20" CHANGELOG.md || { echo "FAIL: [${VERSION}] not dated in CHANGELOG"; exit 1; }
! grep -q "^## \[${VERSION}\] - Unreleased" CHANGELOG.md || { echo "FAIL: CHANGELOG still has Unreleased"; exit 1; }
! grep -q "^## \[Unreleased\]" CHANGELOG.md || { echo "FAIL: [Unreleased] section present"; exit 1; }
echo "OK: CHANGELOG dated and no Unreleased"

# 4. fr/CHANGELOG has matching [1.5.0] section
grep -q "^## \[${VERSION}\] - 20" fr/CHANGELOG.md || { echo "FAIL: fr/CHANGELOG.md missing [${VERSION}]"; exit 1; }
echo "OK: fr/CHANGELOG.md has dated [${VERSION}]"

# 5. UPGRADING has v1.4 -> v1.5 section
grep -q "v1\.4 -> v1\.5" UPGRADING.md || { echo "FAIL: UPGRADING missing v1.4 -> v1.5 section"; exit 1; }
echo "OK: UPGRADING.md has v1.4 -> v1.5 section"

# 6. docs/source/changelog.md placeholder resolved (Unreleased replaced)
! grep -q "^\## \[${VERSION}\] - Unreleased" docs/source/changelog.md || { echo "FAIL: docs/source/changelog.md still has Unreleased"; exit 1; }
grep -q "^\## \[${VERSION}\] - 20" docs/source/changelog.md || { echo "FAIL: docs/source/changelog.md [${VERSION}] not dated"; exit 1; }
echo "OK: docs/source/changelog.md date-stamped"

# 7. Quality gates (ALL must pass before tag)
FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")
python -m numpydoc lint $FILES || { echo "FAIL: numpydoc violations"; exit 1; }
python -m interrogate ketu/ || { echo "FAIL: interrogate < 95%"; exit 1; }
pytest tests/ -q
python -m mypy --strict ketu/
python -m pytest --doctest-modules ketu/ --no-cov --ignore=ketu/lunar_calendar.py --ignore=ketu/__main__.py
echo "OK: all quality gates pass"

# 8. Build
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel
ls dist/ketu-${VERSION}-py3-none-any.whl || { echo "FAIL: wheel has unexpected platform tag"; exit 1; }
echo "OK: built dist/"

# 9. twine check
pip install --quiet twine
python -m twine check dist/*
echo "OK: twine check"

# 10. Verify .npz ships in wheel (unchanged from v1.4)
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep -q "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }
echo "OK: chiron_coeffs.npz present in wheel"

# 11. sdist ships fr/CHANGELOG.md
tar -tzf dist/ketu-${VERSION}.tar.gz | grep -q "fr/CHANGELOG.md" \
  || { echo "FAIL: fr/CHANGELOG.md missing from sdist"; exit 1; }
echo "OK: fr/CHANGELOG.md in sdist"

# 12. Fresh-venv smoke test (local wheel) — four v1.5 assertions
TMP=$(mktemp -d)
trap "rm -rf '$TMP'" EXIT
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}' == m.version('ketu'), f'version mismatch: {ketu.__version__}'
print('version OK')
"

"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds
from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects
from ketu.cycles import generate_cycle_series
from ketu.cache import EphemerisCache
from ketu.houses import calculate_houses
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.composite import calculate_composite
from ketu.returns import solar_return
from ketu.parts import calculate_part
from ketu.ephemeris.planets import calc_planet_position
print('all imports OK')
"

# v1.5 new: declination
"$TMP/bin/python" -c "
import math; from ketu.calculations import declination
d = float(declination(2451545.0, 1))
assert math.isfinite(d) and -90.0 <= d <= 90.0, f'bad declination: {d}'
print(f'declination OK: {d:.4f}°')
"

# v1.5 new: is_ascending_declination
"$TMP/bin/python" -c "
from ketu.calculations import is_ascending_declination
result = is_ascending_declination(2451545.0, 1)
assert isinstance(result, bool)
print(f'is_ascending_declination OK: {result}')
"

# v1.5 new: is_out_of_bounds
"$TMP/bin/python" -c "
from ketu.calculations import is_out_of_bounds
result = is_out_of_bounds(2451545.0, 1)
assert isinstance(result, bool)
print(f'is_out_of_bounds OK: {result}')
"

# v1.5 new: --harmonics h7 CLI
"$TMP/bin/python" -m ketu --harmonics h7 aspects --date 2024-01-01 | grep -q "H7-1" \
  || { echo "FAIL: --harmonics h7 CLI missing H7-1"; exit 1; }
echo "OK: --harmonics h7 CLI"

# v1.4 preserved: generate_harmonic_aspects(7) H7 angles
"$TMP/bin/python" -c "
from ketu.aspects import generate_harmonic_aspects
h7 = generate_harmonic_aspects(7)
assert len(h7) == 3
angles = [float(a) for a in h7['angle']]
assert all(abs(a - e) < 0.01 for a, e in zip(angles, [360/7, 720/7, 1080/7]))
print(f'H7 OK: {[round(a,4) for a in angles]}')
"

# v1.4 preserved: Chiron at 1920 (1900-2100 range active)
"$TMP/bin/python" -c "
import math; from ketu.ephemeris.planets import calc_planet_position
lon = float(calc_planet_position(2422324.5, 13)[0])
assert math.isfinite(lon) and 0.0 <= lon < 360.0
print(f'Chiron 1920 OK: {lon:.4f}°')
"

# AGPL isolation
"$TMP/bin/python" -c "
import importlib.util
assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED into runtime wheel!'
print('pyswisseph absent: OK')
"

echo "OK: fresh-venv smoke tests PASSED"

# 13. PyPI slot clear
python3 -c "
import urllib.request, json
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/ketu/json').read())
versions = list(data['releases'].keys())
assert '${VERSION}' not in versions, f'PyPI already has ${VERSION}!'
print(f'PyPI clear. Latest: {sorted(versions)[-1]}')
"

echo ""
echo "=== Pre-flight PASSED ==="
echo "Safe to: git tag -a v${VERSION} -m 'Release ${VERSION}' && git push origin v${VERSION} && git push origin main"
```

---

## GitHub Release Body (v1.5.0)

```
Ketu v1.5.0 — Equatorial Declination δ + Dynamic Harmonics CLI + Harmonics Debt

**New in v1.5.0:**
- `declination(jdate, body)` — equatorial declination δ in degrees (scalar + vectorized).
- `declination_velocity(jdate, body)` — dδ/dt in degrees/day (northward positive).
- `is_ascending_declination(jdate, body)` — True when Moon (or any body) is montante. Distinct from `is_ascending` (β-trajectory, unchanged).
- `is_out_of_bounds(jdate, body)` — True when |δ| > instantaneous obliquity ε(jd).
- `CHART_DTYPE` gains `body_decl` field (additive float64[14]).
- `--harmonics h7` CLI (and any `h2`–`h64`) at the top-level parser.

**Changed in v1.5.0:**
- `H{h}-{k}` dynamic-aspect naming is now a stable public API contract (pinned by tests).
- `find_aspect_timing` gains `dyn_coef=` parameter for harmonic orb derivation.

**Fixed in v1.5.0:**
- Lunar node mean speed corrected (−0.013 → −0.052954 °/day, matching computed motion).
- `calculate_aspects_batch` duplicate-pair rows eliminated (static-first/dynamic-second, first-match-wins).

**Migration (see UPGRADING.md → v1.4 → v1.5):**
- `CHART_DTYPE` body_decl is additive — named access unaffected; positional/`.view()` must adapt.
- Node speed in `core.bodies['speed'][10/11]` updated to true value.
- All new API is purely additive.

- [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
- [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v14---v15)
- `pip install ketu==1.5.0`

1626 tests, mypy --strict, 100% coverage.
```

Command:

```bash
gh release create v1.5.0 \
  --title "Ketu 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI" \
  --notes "$(cat <<'EOF'
Ketu v1.5.0 adds equatorial declination δ helpers and the dynamic harmonics CLI
surface. All additions are purely additive — no breaking changes. The `is_ascending`
(β-trajectory) function and the frozen `core.aspects` table are byte-identical to v1.4.

**New in v1.5.0:**
- `declination(jdate, body)` — equatorial declination δ in degrees [−90, +90], scalar and vectorized.
- `declination_velocity(jdate, body)` — dδ/dt in degrees/day (northward positive).
- `is_ascending_declination(jdate, body)` — True when dδ/dt > 0 (Moon montante). Distinct from `is_ascending` (β-trajectory, unchanged).
- `is_out_of_bounds(jdate, body)` — True when |δ| exceeds instantaneous obliquity ε(jd).
- `CHART_DTYPE` gains `body_decl` (`float64[14]`) — declination δ for all 14 bodies (additive).
- `--harmonics h<N>` CLI top-level flag (e.g. `ketu --harmonics h7 aspects --date …`).

**Changed in v1.5.0:**
- `H{h}-{k}` dynamic-aspect naming is a stable public API contract (pinned by tests).
- `find_aspect_timing` gains `dyn_coef=` optional parameter for harmonic orb derivation.

**Fixed in v1.5.0:**
- Lunar node mean speed corrected (−0.013 → −0.052954 °/day, matching the true 18.6-year regression).
- `calculate_aspects_batch` duplicate-pair rows eliminated (exactly one row per pair, static-first/dynamic-second).

**Migration (see UPGRADING.md → v1.4 → v1.5):**
- `CHART_DTYPE.body_decl` is additive — named field access unchanged; positional/`.view()` must adapt.
- `core.bodies['speed'][10]` and `[11]` (Rahu/Ketu) hold the corrected nodal speed.
- All new API surface is purely additive.

- 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
- 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v14---v15)
- 📦 `pip install ketu==1.5.0`

1626 tests, mypy --strict, 100% coverage.
EOF
)" \
  dist/ketu-1.5.0-py3-none-any.whl dist/ketu-1.5.0.tar.gz
```

---

## Plan Decomposition

```
.planning/phases/35-release-v1-5-0/
├── 35-01-version-bump-changelog-upgrading-PLAN.md   # REL-01 + REL-02 (docs+version, wave 1)
└── 35-02-pypi-publish-smoke-test-PLAN.md            # REL-03 (human-gated, wave 2)
```

### Plan 35-01 task list (no mypy fix needed — gates are all green)

1. Bump version in THREE files (unlike Phase 32 which was only two files):
   - `pyproject.toml` line 7: `"1.4.0"` → `"1.5.0"`
   - `ketu/__init__.py` line 57: `"1.4.0"` → `"1.5.0"`
   - `docs/source/conf.py` lines 14–15: `"1.4.0"` → `"1.5.0"` (CRITICAL — see Pitfall 2)
2. Run `pytest tests/test_version.py -v` to verify sync gate.
3. Date-stamp root `CHANGELOG.md` line 10: `Unreleased` → today's UTC date.
4. Date-stamp `docs/source/changelog.md` line 8: `Unreleased` → same date.
5. Author `fr/CHANGELOG.md` `[1.5.0]` section in French (fresh, above `[1.4.0]`).
6. Add `## v1.4 -> v1.5` section to `UPGRADING.md` (new first section, before `## v1.3 -> v1.4`).
7. Update `README.md` `## Roadmap` checklist with v1.5 entries.
8. Commit all changes in one atomic commit.
9. Run full suite: `pytest tests/ -q` to confirm nothing broken.

### Plan 35-02 task list

1. Date-stamp confirm + full pre-flight (the script above) — HARD GATES, stop on first failure.
2. **BLOCKING human go/no-go checkpoint** (present pre-flight results; wait for "approved").
3. `git tag -a v1.5.0 -m "Release 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI"`
4. `git push origin v1.5.0` — triggers publish.yml.
5. `git push origin main` — RTD follows main (feedback_push_main_not_just_tag_on_release).
6. Watch `publish.yml` to completion via `gh run watch`.
7. `gh release create v1.5.0` with sdist + wheel, using the release body above.
8. Post-publish verification: fresh venv `pip install ketu==1.5.0` from PyPI, run full
   smoke assertions (four v1.5 checks + H7 angles + Chiron@1920 + all-imports + no-swisseph).
9. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.

---

## Numbered Pitfalls (v1.5-specific)

### Pitfall 1: Date-stamping root CHANGELOG [1.5.0] — different from Phase 32

**What goes wrong:** Plan writer follows Phase 32 pattern (author content from scratch)
instead of only date-stamping the existing section. Overwrites the carefully-authored
content with a fresh block, losing the `### Fixed` and `### Notes` subsections.

**How to avoid:** Read CHANGELOG.md first. Confirm `## [1.5.0] - Unreleased` is at line
10 with complete content. The ONLY edit is replacing `Unreleased` with the real date.
Do NOT rewrite the block.

### Pitfall 2: Skipping conf.py bump (inverted Phase 32 Pitfall 5/8)

**What goes wrong:** Plan replicates Phase 32 instruction "do NOT touch conf.py — already
at target version." For v1.4, conf.py was pre-bumped by Phase 31. For v1.5, NO
pre-bump happened. Skipping conf.py leaves RTD showing "1.4.0" after the release.

**How to avoid:** Plan 35-01 Task 1 explicitly includes conf.py (lines 14–15) in the
version bump. Pre-flight step 2 asserts `grep -q "release = \"${VERSION}\"" docs/source/conf.py`.

### Pitfall 3: docs/source/changelog.md still has Unreleased after edit

**What goes wrong:** Edit only the root CHANGELOG, forget docs/source/changelog.md.
RTD shows "Unreleased" in the docs changelog after the release.

**How to avoid:** Plan 35-01 Task 4 explicitly date-stamps docs/source/changelog.md
line 8. Pre-flight step 6 asserts the Unreleased token is gone.

### Pitfall 4: Push tag but forget to push main (RTD docs freeze)

**What goes wrong:** `git push origin v1.5.0` fires publish.yml and PyPI gets the new
version. But `origin/main` is not pushed. RTD follows main, so docs remain at v1.4
content even though PyPI has v1.5.0.

**How to avoid:** Plan 35-02 Task 5 explicitly includes `git push origin main` as a
separate first-class step AFTER the tag push (feedback_push_main_not_just_tag_on_release).

### Pitfall 5: Smoke test uses wrong import path for declination functions

**What goes wrong:** Smoke test tries `from ketu import declination` (not in `ketu.__all__`)
or `from ketu import is_ascending_declination`. Both fail with ImportError.

**How to avoid:** All four v1.5 functions are in `ketu.calculations`. The correct path is
`from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds`.

### Pitfall 6: CLI --harmonics used as subcommand flag not top-level flag

**What goes wrong:** Smoke test runs `ketu aspects --date 2024-01-01 --harmonics h7` —
this fails ("unrecognized arguments: --harmonics h7"). The `--harmonics` flag is a
TOP-LEVEL parser flag, not a subcommand flag.

**How to avoid:** Smoke test uses `ketu --harmonics h7 aspects --date 2024-01-01`.
The pre-flight CLI check runs the command in this order.

### Pitfall 7: Version bumped in only two files (missing conf.py)

**What goes wrong:** `pyproject.toml = "1.5.0"` and `ketu/__init__.py = "1.5.0"` but
`docs/source/conf.py = "1.4.0"`. `test_version.py` passes (it only checks the two
source-of-truth files) but RTD shows stale 1.4.0 branding.

**How to avoid:** Pre-flight step 2 asserts ALL THREE files are at `${VERSION}`.

### Pitfall 8: fr/CHANGELOG missing [1.5.0] (not just date-stamp)

**What goes wrong:** Plan date-stamps only the root and docs changelogs but forgets that
fr/CHANGELOG.md has NO `[1.5.0]` section at all (unlike the root, which has one).
fr/CHANGELOG.md's top section remains `[1.4.0] - 2026-06-03` after the release.

**How to avoid:** Plan 35-01 Task 5 authors a NEW French `## [1.5.0]` section above
`## [1.4.0]`. Pre-flight step 4 asserts `grep -q "^## \[${VERSION}\] - 20" fr/CHANGELOG.md`.

### Pitfall 9: pyswisseph appears in fresh-venv (misleading dev venv result)

**What goes wrong:** Same as Phase 32 Pitfall 9. In the dev venv, `swisseph` IS
importable (under `.[test]` extras). The smoke test must run in a clean venv installing
ONLY the wheel.

**How to avoid:** Smoke test always uses a `mktemp -d` venv with no `.[test]` extras.

### Pitfall 10: UPGRADING entry omitted because v1.5 is "fully additive"

**What goes wrong:** Plan skips UPGRADING because v1.5 has no breaking changes. But the
`body_decl` additive dtype change IS relevant to positional consumers (Kala), and the
node-speed fix changes a value that downstream code may have cached.

**How to avoid:** Plan 35-01 Task 6 adds `## v1.4 -> v1.5` to UPGRADING.md covering the
three notes (body_decl positional impact, node-speed correction, additive API).
Pre-flight step 5 asserts `grep -q "v1\.4 -> v1\.5" UPGRADING.md`.

---

## Exact File/Line Targets for Every Edit (Plan 35-01)

| File | Edit | Location | Action |
|------|------|----------|--------|
| `pyproject.toml` | Version bump | line 7 | `"1.4.0"` → `"1.5.0"` |
| `ketu/__init__.py` | Version bump | line 57 | `"1.4.0"` → `"1.5.0"` |
| `docs/source/conf.py` | Version bump | lines 14–15 | `"1.4.0"` → `"1.5.0"` (both `release` and `version`) |
| `CHANGELOG.md` | Date-stamp `[1.5.0]` | line 10 | `Unreleased` → real UTC date |
| `docs/source/changelog.md` | Date-stamp `[1.5.0]` | line 8 | `Unreleased` → real UTC date |
| `fr/CHANGELOG.md` | Add `[1.5.0]` section | Before `## [1.4.0] - 2026-06-03` | New French section |
| `UPGRADING.md` | Add `v1.4 -> v1.5` | line 1 (new first section) | Insert before `## v1.3 -> v1.4` |
| `README.md` | Update `## Roadmap` checklist | Near line 329 | Add v1.5 entries |

**No source code changes to `ketu/` are needed.** All quality gates are already green.

---

## Subpackages for Smoke Import Table (v1.5 additions bolded)

| Package | Import | v1.5 note |
|---------|--------|-----------|
| `ketu` | `import ketu` | `__version__` check |
| `ketu.core` | `from ketu.core import bodies, aspects, signs` | |
| `ketu.calculations` | `from ketu.calculations import long` | |
| `ketu.calculations` | **`from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds`** | **All four new in v1.5** |
| `ketu.aspects` | `from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects` | |
| `ketu.cycles` | `from ketu.cycles import generate_cycle_series` | |
| `ketu.cache` | `from ketu.cache import EphemerisCache` | |
| `ketu.houses` | `from ketu.houses import calculate_houses` | |
| `ketu.charts` | `from ketu.charts import compute_chart` | |
| `ketu.synastry` | `from ketu.synastry import calculate_synastry` | |
| `ketu.composite` | `from ketu.composite import calculate_composite` | |
| `ketu.returns` | `from ketu.returns import solar_return` | |
| `ketu.parts` | `from ketu.parts import calculate_part` | |
| `ketu.ephemeris.planets` | `from ketu.ephemeris.planets import calc_planet_position` | |

---

## State of the Art

| Item | v1.4.0 | v1.5.0 | Notes |
|------|--------|--------|-------|
| Body count | 14 | 14 (unchanged) | No structural change |
| `CHART_DTYPE` fields | No `body_decl` | **`body_decl` added (float64[14])** | Additive |
| Declination API | Not available | **`declination()`, `declination_velocity()`, `is_ascending_declination()`, `is_out_of_bounds()`** | All in `ketu.calculations` |
| Harmonics CLI | Not available | **`ketu --harmonics h7 aspects --date …`** | Top-level flag |
| `H{h}-{k}` naming | Informal | **Public API contract, pinned by tests** | Phase 34 |
| `find_aspect_timing` | No `dyn_coef` | **`dyn_coef=None` optional param** | Backwards compatible |
| Node mean speed | ~−0.013°/day (wrong) | **−0.052954°/day (corrected)** | Affects `core.bodies['speed'][10/11]` |
| Test count | 1537 (Phase 32 state) | **1626 passed, 2 skipped** | 100% coverage |
| mypy --strict | 1 error (fixed in Plan 32-01) | **PASS — zero errors, 69 files** | No fix needed for v1.5 |
| docs/source/conf.py | Already 1.4.0 (pre-bumped Phase 31) | **At 1.4.0 — MUST bump to 1.5.0** | INVERTED from Phase 32 |
| Root CHANGELOG [1.5.0] | Does not exist | **Exists as `Unreleased` stub** | Only needs date-stamp |
| docs/source/changelog.md [1.5.0] | Does not exist | **Exists as `Unreleased` stub** | Only needs date-stamp |
| fr/CHANGELOG [1.5.0] | Does not exist | **Does not exist** | Must author French section |
| UPGRADING v1.4 → v1.5 | Does not exist | **Does not exist** | Must add |
| README What's New | No v1.4 section exists | **No v1.5 section exists** | Update Roadmap checklist instead |
| PyPI slot 1.5.0 | N/A | **Available** (confirmed) | |
| v1.5.0 git tag | Does not exist | **Must create** | |

---

## Open Questions

1. **README update strategy:** The current README has no `## What's New` sections (Phase
   32 for v1.4 did add one, but it appears the README was rewritten/restructured and no
   longer has it). The recommendation is to add v1.5 entries to the `## Roadmap`
   checklist rather than creating a new `## What's New in v1.5.0` section without a v1.4
   equivalent. The planner should decide: (a) add only Roadmap entries, or (b) also
   add a `## What's New in v1.5.0` section. Either is acceptable; (a) is simpler.
   **Recommendation:** Option (a) — Roadmap checklist update only.

2. **`### Notes` subsection in root CHANGELOG:** The `[1.5.0]` root block uses
   `### Notes` (non-standard Keep-a-Changelog section). This was authored during Phase
   33/34 and is complete. Since it is already in the section, Plan 35-01 simply
   date-stamps it and leaves it as-is. No normalization needed.

---

## Sources

### Primary (HIGH confidence — verified against live repo files 2026-06-04)

- `pyproject.toml` (read directly) — `version = "1.4.0"` at line 7; `ketu.data` package + `*.npz` package-data confirmed; `pyswisseph` under `[test]` extras only
- `ketu/__init__.py` (read directly) — `__version__ = "1.4.0"` at line 57; `__all__` does NOT include declination functions
- `docs/source/conf.py` (read directly) — `release = "1.4.0"`, `version = "1.4.0"` at lines 14–15 (NOT pre-bumped — MUST change)
- `CHANGELOG.md` (read directly) — `## [1.5.0] - Unreleased` at line 10 with complete content; `## [1.4.0] - 2026-06-03` at line 70
- `fr/CHANGELOG.md` (read directly) — `## [1.4.0] - 2026-06-03` is the current top section; no `[1.5.0]` section
- `docs/source/changelog.md` (read directly) — `## [1.5.0] - Unreleased` at line 8 with complete content
- `UPGRADING.md` (read directly) — `## v1.3 -> v1.4` is the topmost section; no `## v1.4 -> v1.5` section
- `README.md` (read directly) — No `## What's New` sections; `## Roadmap` at line 312
- `.github/workflows/publish.yml` (read directly) — tag-push trigger, OIDC, Node 24 actions confirmed; no changes needed
- `ketu/calculations.py` (read directly) — `declination` at line 440, `declination_velocity` at 495, `is_ascending_declination` at 527, `is_out_of_bounds` at 558; all in `ketu.calculations`
- `Makefile` (read directly) — `make test`, `make mypy`, `make doc-gates`, `make doctest` commands confirmed
- `git tag -l` output — `v1.4.0` exists, `v1.5.0` does not
- PyPI JSON API — 1.5.0 slot confirmed available; latest is 1.4.0
- `pytest tests/ -q` (executed live) — **1626 passed, 2 skipped**
- `python -m mypy --strict ketu/` (executed live) — **zero errors, 69 source files**
- `python -m interrogate ketu/` (executed live) — 99.7% PASS
- `python -m numpydoc lint` (executed live) — zero violations
- `declination(2451545.0, 1)` (executed live) — −10.7460° (finite, in [-90, 90])
- `is_ascending_declination(2451545.0, 1)` (executed live) — False (bool)
- `is_out_of_bounds(2451545.0, 1)` (executed live) — False (bool)
- `ketu --harmonics h7 aspects --date 2024-01-01` (executed live) — shows "H7-1 51°, H7-2 103°, H7-3 154°"

### Secondary (MEDIUM confidence)

- Phase 32 RESEARCH.md + PLAN files (read directly) — pre-flight pattern, ceremony pattern, pitfalls adapted for v1.5
- MEMORY.md entries — feedback_push_main_not_just_tag_on_release, feedback_validation_review_before_release, project_v15_scope_intent confirmed

---

## Metadata

**Confidence breakdown:**
- Version bump locations: HIGH — read all files directly; exactly 3 files need editing
- CHANGELOG state: HIGH — read directly; Unreleased stub exists; only date-stamp needed
- UPGRADING gap: HIGH — read directly; no v1.4 → v1.5 section
- docs/source/changelog.md state: HIGH — Unreleased stub confirmed
- conf.py state: HIGH — at 1.4.0; MUST bump
- fr/CHANGELOG gap: HIGH — no [1.5.0] section; must author
- publish.yml trigger/OIDC: HIGH — read directly; no changes needed
- Smoke test assertions: HIGH — all four v1.5 functions executed live; import paths confirmed
- mypy/coverage/test gates: HIGH — executed live; all green
- PyPI state: HIGH — JSON API confirmed; 1.5.0 slot free

**Research date:** 2026-06-04
**Valid until:** 30 days (stable domain; re-check PyPI slot just before publish)

---

## RESEARCH COMPLETE
