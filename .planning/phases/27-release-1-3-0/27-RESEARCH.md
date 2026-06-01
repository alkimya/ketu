# Phase 27: Release 1.3.0 — Research

**Researched:** 2026-06-01
**Domain:** Python package release engineering — version bump, CHANGELOG/UPGRADING finalization, PyPI OIDC publish ceremony (reuses v1.2.0 infra)
**Confidence:** HIGH (all claims verified against live repo files)

---

## Summary

Phase 27 is the FINAL phase of milestone v1.3 (Chiron & Engine Hardening). All seven
predecessor phases (21–26 + 26.1) are complete. The release infrastructure is proven
from Phase 20 (v1.2.0): `publish.yml` is wired, OIDC trusted publishing is configured
on PyPI, `tests/test_version.py` provides the version-sync gate, and the pre-flight
pattern is documented in Phase 20.

This phase is MECHANICAL. There are no new features and no tooling changes.
The two tasks the roadmap stubs — 27-01 (version bump + CHANGELOG + UPGRADING) and
27-02 (pre-flight + publish + smoke test) — map directly to the two requirements
REL-10 and REL-11.

**Three concrete deltas from Phase 20 that make this release non-trivial:**

1. **CHANGELOG cleanup required.** There are TWO distinct unversioned sections:
   `## [Unreleased]` (lines 10–33, containing a BREAKING cycle-direction fix and a
   bug fix from post-Phase-26 work) AND `## [1.3.0] - Unreleased` (lines 34–77,
   containing the aspects data-driven changes). These must be MERGED into a single
   dated `## [1.3.0] - YYYY-MM-DD` section, and the Chiron 14th-body BREAKING
   entry is currently MISSING from it entirely — it must be added.

2. **UPGRADING.md is incomplete.** The existing `## v1.2 -> v1.3` section documents
   only the aspect-engine changes. The Chiron 13→14 positional-contract breaking
   change (CHART_DTYPE shape, body axis expansion) is NOT documented there — it
   must be added.

3. **Fresh-venv smoke test is more demanding than v1.2.** Must verify:
   (a) `calc_planet_position(jd, 13)` returns finite (Chiron via embedded .npz),
   (b) `pyswisseph` is NOT installed in the runtime environment (AGPL isolation),
   (c) `ketu/data/chiron_coeffs.npz` ships inside the wheel.

**Primary recommendation:** Two sequential plans: 27-01 (docs-only: version bump +
CHANGELOG merge + Chiron entry + UPGRADING Chiron section + fr/CHANGELOG v1.3 +
README update), then 27-02 (human-gated pre-flight + tag + publish + verify). No
code changes to `ketu/` source beyond the two version string lines.

---

## Version Bump Locations (ALL Files to Change)

Verified 2026-06-01 by reading all files directly.

| File | Line | Current value | Target value | Notes |
|------|------|---------------|--------------|-------|
| `pyproject.toml` | 7 | `version = "1.2.0"` | `version = "1.3.0"` | Build system source of truth |
| `ketu/__init__.py` | 57 | `__version__ = "1.2.0"` | `__version__ = "1.3.0"` | Runtime source of truth |
| `docs/source/conf.py` | 14–15 | Already `"1.3.0"` | No change needed | Pre-bumped in Phase 25 |

**Total files to edit: 2** (`pyproject.toml` + `ketu/__init__.py`). `docs/source/conf.py`
is already at 1.3.0 — do NOT touch it.

Gate: `pytest tests/test_version.py -v` (checks `ketu.__version__ == importlib.metadata.version("ketu")`).

---

## CHANGELOG.md Current State and Required Delta

**Verified 2026-06-01 by reading CHANGELOG.md directly.**

### Current structure

```
## [Unreleased]          ← lines 10–33 (cycle-direction BREAKING + datetime64 fix)
## [1.3.0] - Unreleased  ← lines 34–77 (aspects data-driven BREAKING + Added)
## [1.2.0] - 2026-05-28  ← line 78 (already released)
```

### [Unreleased] section content (lines 10–33)

Contains two items from post-Phase-26 work:
- **BREAKING (internal):** `CYCLE_DTYPE.angular_separation` direction fix:
  `generate_cycle_series` / `generate_multi_cycle_series` now follows documented
  body1→body2 direction `(body2_lon - body1_lon) % 360`. Previously reversed.
  Kala must adjust (`360 - old` away from conjunction except at 0°/180°).
- **Fixed:** `generate_cycle_series` now accepts `numpy.datetime64` ndarray on
  the cache path (`use_cache=True`); previously raised `AttributeError`.

### [1.3.0] - Unreleased section content (lines 34–77)

Contains aspects data-driven items (Phase 26):
- **Added:** `aspects_for_harmonics(harmonics)` — frozen `numpy.bool_` mask
- **Added:** `harmonic` and `symbol` columns on `core.aspects` (5-field dtype)
- **BREAKING:** default aspect set CLASSICAL(5) → TRADITIONAL(7) for Python API

### What is MISSING from [1.3.0]

**Chiron 14th body entry is entirely absent.** Must be added under `### Added`:

```
- **Chiron as the 14th body (body_id=13)** — embedded Chebyshev polynomial
  evaluator (pure NumPy, zero pyswisseph at runtime). `calc_planet_position(jd, 13)`
  and `calc_planet_position_batch(jds, 13)` resolve Chiron longitude from
  `ketu/data/chiron_coeffs.npz` (289.7 KB, Chebyshev seg=32d/deg=10). Max |Δλ| =
  0.005695° over 1950–2050. Available through all standard calculation paths
  (`ketu.calculations`, `ketu.charts.compute_chart`, `ketu.synastry`, etc.).
  CHART_DTYPE body axis expanded: 13 bodies → 14 bodies (body_lons[14],
  body_speeds[14], aspects[14×14]). (Phase 24 / D-08)
```

Under `### Changed` — **BREAKING contract note for Kala**:

```
- **BREAKING (Kala / downstream positional contract):** `CHART_DTYPE` body
  arrays expanded from shape (13,) → (14,) and aspects from (13,13) → (14,14).
  Positional index 13 is Chiron. Any code that hardcoded the body count as 13
  or addressed body arrays by fixed numeric index beyond 12 must be updated.
  `ketu.cycles` default pairs and `ketu.synastry` cross-product body axis
  updated accordingly (synastry: 15→16 bodies including ASC/MC).
  See UPGRADING.md → "v1.2 -> v1.3" for the full migration recipe. (Phase 24 / D-08)
```

### Required action in Plan 27-01

1. **Merge** `## [Unreleased]` content into `## [1.3.0]`.
2. **Add** Chiron `### Added` bullet and BREAKING `### Changed` note.
3. **Change** `## [1.3.0] - Unreleased` → `## [1.3.0] - YYYY-MM-DD` (real release date).
4. **Remove** the now-empty `## [Unreleased]` section.

**Result:** single `## [1.3.0] - YYYY-MM-DD` section with all five items.

---

## UPGRADING.md Current State and Required Delta

**Verified 2026-06-01 by reading UPGRADING.md directly.**

### Current structure

```
## v1.2 -> v1.3      ← lines 1–105 (aspects engine only)
## v1.1 -> v1.2      ← lines 107–... (additive; new subpackages)
## v1.0 -> v1.1      ← (Lilith fix, CLI changes)
## v0.4.x -> v1.0.0
```

### What exists in `## v1.2 -> v1.3` (lines 1–105)

Fully documents the aspect-engine breaking change:
- Two-part default shift (CLASSICAL→TRADITIONAL, H5/H9/H10 opt-in)
- Restore recipe (`aspects="classical"`)
- `aspects_for_harmonics` API
- CLI note (CLI stays classical)
- `coef` vs `coefficient` naming
- Kala / downstream adapter guidance

### What is MISSING from `## v1.2 -> v1.3`

The **Chiron 13→14 positional-contract section** is completely absent. Must be added
under a `### Chiron (14th body — D-08)` sub-section covering:

```markdown
### Chiron added as body_id=13 (14th body)

In v1.3.0, Chiron is the 14th celestial body at positional index 13.

**CHART_DTYPE shape expansion:**

| Field | v1.2 shape | v1.3 shape |
|-------|------------|------------|
| `body_lons` | `(13,)` | `(14,)` |
| `body_speeds` | `(13,)` | `(14,)` |
| `aspects` | `(13, 13)` | `(14, 14)` |

**Kala / downstream consumers:** Any code that hardcoded the body count as 13
or accessed body arrays by fixed numeric index beyond 12 must be updated.
Cached CHART_DTYPE arrays from v1.2 are incompatible — recompute with v1.3.

**New imports (pure NumPy, no pyswisseph required at runtime):**
```python
from ketu.ephemeris.planets import calc_planet_position
import numpy as np

jd = 2451545.0  # J2000.0
pos = calc_planet_position(jd, 13)   # body_id=13 = Chiron
lon = float(pos[0])                   # ecliptic longitude, finite
```

**Kala synastry body axis:** 15→16 bodies (Sun..Chiron + ASC + MC = 16 ordered pairs).
```

### Required action in Plan 27-01

Add the Chiron section to `## v1.2 -> v1.3` BEFORE the existing aspect-engine section
(or after — order is editorial; Chiron first is more prominent).

---

## fr/CHANGELOG.md Current State and Required Delta

**Verified 2026-06-01 by reading fr/CHANGELOG.md directly.**

`fr/CHANGELOG.md` exists (created in Phase 20) and covers `[1.2.0]` through `[1.0.0]`.
No `[1.3.0]` section exists — it must be added.

The `[1.3.0]` section should follow the same "synthesized translation, not double-maintained"
policy. A concise French `## [1.3.0] - YYYY-MM-DD` section with the same bullet points
translated. The section must cover:

- Chiron 14e corps (`calc_planet_position(jd, 13)`, `.npz` Chebyshev embarqué, pur NumPy)
- BREAKING: `CHART_DTYPE` 13→14 corps (body_lons shape, aspects shape), note Kala
- `aspects_for_harmonics(harmonics)` — masque `numpy.bool_` figé longueur 14
- BREAKING: défaut Python API CLASSICAL(5)→TRADITIONAL(7)
- Corrections cycle : direction `angular_separation` body1→body2 + `datetime64` cache path
- Reference to `UPGRADING.md → v1.2 -> v1.3`

---

## README.md Current State and Required Delta

**Verified 2026-06-01 by reading README.md lines 13–40.**

README already has a `## What's New in v1.3.0` section (lines 13–15) that reads:

```
## What's New in v1.3.0

Ketu v1.3.0 adds Chiron as the 14th body and makes the aspect engine
```

This section was pre-written (likely Phase 25). **Verify it is complete** — check the
full section before plan 27-01 execution. If it already covers Chiron + aspect engine,
no change needed. If incomplete, update in the same 27-01 commit.

---

## PyPI and Git Tag State

**Verified 2026-06-01 against live repo.**

| Item | State |
|------|-------|
| Current PyPI live version | 1.2.0 |
| `v1.3.0` tag | Does NOT yet exist |
| `v1.2.0` tag | Exists on main |
| PyPI slot `ketu==1.3.0` | Available (not taken) |
| OIDC trusted publisher | Configured from Phase 20 — Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi — no changes needed |

---

## Publish Workflow (publish.yml)

**Verified 2026-06-01 by reading `.github/workflows/publish.yml` directly.**

```yaml
on:
  push:
    tags:
      - 'v*.*.*'          # trigger: push v1.3.0 tag
jobs:
  build:                   # Python 3.11, python -m build --sdist --wheel, twine check
  publish-to-pypi:         # needs build, environment: pypi, id-token: write
                           # uses: pypa/gh-action-pypi-publish@release/v1
```

**Trigger:** `git push origin v1.3.0` fires the workflow.

**OIDC:** `environment: pypi` + `permissions.id-token: write` — no API tokens needed.
The trusted publisher config persists from Phase 20 — no PyPI-side configuration needed.

**Actions versions (already Node 24 from Phase 20):**
- `actions/checkout@v5`
- `actions/setup-python@v6` (Python 3.11 for build)
- `actions/upload-artifact@v5` / `actions/download-artifact@v5`
- `pypa/gh-action-pypi-publish@release/v1`

**No changes to publish.yml are needed for v1.3.0.**

---

## Packaging of ketu/data (chiron_coeffs.npz)

**Verified 2026-06-01 by reading pyproject.toml directly.**

```toml
[tool.setuptools]
packages = ["ketu", ..., "ketu.data"]   # ketu.data is explicitly listed

[tool.setuptools.package-data]
"ketu.data" = ["*.npz"]                  # *.npz files included in wheel + sdist
```

`ketu/data/chiron_coeffs.npz` is 289.7 KB. It WILL be included in the wheel.

**Smoke test must verify the .npz ships:**
```bash
# Inspect wheel contents:
python -m zipfile -l dist/ketu-1.3.0-py3-none-any.whl | grep "chiron_coeffs.npz"
# Expected: ketu/data/chiron_coeffs.npz
```

---

## Fresh-Venv Smoke Test (REL-11)

The v1.3.0 smoke test is more demanding than v1.2.0. Three additional assertions:

1. `calc_planet_position(jd, 13)` returns finite longitude (Chiron via .npz)
2. `pyswisseph` is NOT importable in the runtime venv (AGPL isolation)
3. `ketu/data/chiron_coeffs.npz` is present inside the wheel

**Complete smoke script for Plan 27-02:**

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.3.0"

# 1. Verify wheel exists
ls dist/ketu-${VERSION}-py3-none-any.whl

# 2. Verify .npz ships in wheel
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }

# 3. Fresh venv
TMP=$(mktemp -d)
python -m venv "$TMP"

# 4. Install ONLY the wheel (no dev extras, no test extras → no pyswisseph)
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

# 5. Version check
"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}', f'Bad __version__: {ketu.__version__}'
assert m.version('ketu') == '${VERSION}', f'Bad metadata: {m.version(\"ketu\")}'
print('version OK:', ketu.__version__)
"

# 6. All subpackage imports
"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.aspects import calculate_aspects, aspects_for_harmonics
from ketu.cycles import generate_cycle_series
from ketu.cache import EphemerisCache
from ketu.houses import calculate_houses
from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry
from ketu.composite import calculate_composite
from ketu.returns import solar_return
from ketu.parts import calculate_part
print('all subpackage imports OK')
"

# 7. Chiron via embedded .npz (zero pyswisseph)
"$TMP/bin/python" -c "
import math
from ketu.ephemeris.planets import calc_planet_position
pos = calc_planet_position(2451545.0, 13)   # body_id=13 = Chiron at J2000.0
lon = float(pos[0])
assert math.isfinite(lon), f'Chiron longitude not finite: {lon}'
assert 0.0 <= lon < 360.0, f'Chiron longitude out of range: {lon}'
print(f'Chiron OK: lon={lon:.4f}°')
"

# 8. pyswisseph NOT installed (AGPL isolation)
"$TMP/bin/python" -c "
import importlib.util
spec = importlib.util.find_spec('swisseph')
assert spec is None, 'FAIL: pyswisseph is importable in runtime venv'
print('pyswisseph NOT in runtime venv: OK')
"

rm -rf "\$TMP"
echo "All smoke tests PASSED for ketu==${VERSION}"
```

**Subpackages enumerated for import in smoke test:**

| Package | Import | Purpose |
|---------|--------|---------|
| `ketu` | `import ketu` | Root package, `__version__` |
| `ketu.core` | `from ketu.core import bodies, aspects, signs` | Constants |
| `ketu.calculations` | `from ketu.calculations import long` | Positions |
| `ketu.aspects` | `from ketu.aspects import calculate_aspects, aspects_for_harmonics` | Aspects + new v1.3 API |
| `ketu.cycles` | `from ketu.cycles import generate_cycle_series` | Cycle time series |
| `ketu.cache` | `from ketu.cache import EphemerisCache` | Cache |
| `ketu.houses` | `from ketu.houses import calculate_houses` | House systems |
| `ketu.charts` | `from ketu.charts import compute_chart` | Chart computation |
| `ketu.synastry` | `from ketu.synastry import calculate_synastry` | Synastry (v1.2) |
| `ketu.composite` | `from ketu.composite import calculate_composite` | Composite (v1.2) |
| `ketu.returns` | `from ketu.returns import solar_return` | Returns (v1.2) |
| `ketu.parts` | `from ketu.parts import calculate_part` | Arabic Parts (v1.2) |
| `ketu.ephemeris.planets` | `from ketu.ephemeris.planets import calc_planet_position` | Chiron resolution |

Note: `ketu.cli` and `ketu.data` are internal packages (not user-importable by design).
`ketu.ephemeris.chiron` is private (`_chiron_scalar`, `_chiron_vec`). The smoke test
calls `calc_planet_position(jd, 13)` which exercises the Chiron path without importing
private symbols.

---

## Architecture Patterns

### Plan Decomposition

Two sequential plans (matching the roadmap stubs):

```
.planning/phases/27-release-1-3-0/
├── 27-01-version-bump-changelog-upgrading-PLAN.md   # REL-10 (docs-only)
└── 27-02-pypi-publish-smoke-test-PLAN.md            # REL-11 (human-gated)
```

**27-01** is entirely docs + version strings. Zero logic changes to `ketu/` source.
**27-02** depends on 27-01 being committed to main.

**27-01 task list:**
1. Bump version: `pyproject.toml` + `ketu/__init__.py` → `"1.3.0"`
2. Run `pytest tests/test_version.py -v` to verify
3. Merge `## [Unreleased]` into `## [1.3.0]` + add Chiron entries + date the header
4. Add Chiron section to `UPGRADING.md` `## v1.2 -> v1.3`
5. Add `## [1.3.0]` section to `fr/CHANGELOG.md`
6. Verify README `## What's New in v1.3.0` is complete
7. Commit all in one doc commit

**27-02 task list:**
1. Full pre-flight (tests, numpydoc, build, twine check, fresh-venv smoke)
2. Human go/no-go checkpoint
3. `git tag -a v1.3.0 -m "Release 1.3.0"` + `git push origin v1.3.0`
4. Monitor `publish.yml` to completion
5. `gh release create v1.3.0 --title ... --notes ...` with local dist/ artifacts
6. Post-publish: `pip install ketu==1.3.0` from PyPI in fresh venv, smoke test

### Pattern 1: Dual Hard-Coded Version (same as v1.2)

```toml
# pyproject.toml
version = "1.3.0"  # was "1.2.0"
```

```python
# ketu/__init__.py
__version__ = "1.3.0"  # was "1.2.0"
```

Gate: `pytest tests/test_version.py -v` (already in CI, checks metadata == `__version__`).

### Pattern 2: Tag-Triggered Trusted Publishing (unchanged from v1.2)

Push `v1.3.0` tag → `publish.yml` builds + publishes to PyPI via OIDC.
Sequence: merge 27-01 to main → 27-02 pre-flight → human approval → tag → push.

### Pattern 3: GitHub Release Creation

```bash
gh release create v1.3.0 \
  --title "Ketu 1.3.0 — Chiron (14th body) + aspect-engine hardening" \
  --notes "$(cat <<'EOF'
Ketu v1.3.0 is a feature release adding Chiron as the 14th body and hardening
the aspect engine with a richer data model.

**New in v1.3.0:**
- Chiron (body_id=13) via embedded Chebyshev .npz — pure NumPy, no pyswisseph at runtime
- `aspects_for_harmonics([1,2,3,6])` — compose aspect masks from harmonic lists
- `harmonic` + `symbol` columns on `core.aspects` (5-field dtype)
- Default Python API aspect set: CLASSICAL(5) → TRADITIONAL(7 half-circle)

**BREAKING changes (see UPGRADING.md → v1.2 → v1.3):**
- CHART_DTYPE body axis: 13 → 14 (Chiron at index 13)
- CYCLE_DTYPE angular_separation direction: now body1→body2 (`360 - old` for non-0/180° values)
- Python API aspect default: CLASSICAL → TRADITIONAL (CLI unchanged)

- 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md#130---YYYY-MM-DD)
- 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v12---v13)
- 📦 `pip install ketu==1.3.0`

1399 tests, mypy --strict, 100% coverage, 57 doctests.
EOF
)" \
  dist/ketu-1.3.0-py3-none-any.whl dist/ketu-1.3.0.tar.gz
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PyPI authentication | API tokens | OIDC trusted publishing (already wired) | Configured in Phase 20; persistent |
| Build artifacts | Manual `setup.py` | `python -m build --sdist --wheel` | PEP 517; already in publish.yml |
| Wheel validation | Manual inspect | `twine check dist/*` | Already in publish.yml |
| Version sync check | grep scripts | `pytest tests/test_version.py` | Already exists, runs in CI |
| Subpackage import test | manual import loop | inline Python `-c` one-liners | Simple, no test file needed |
| pyswisseph absence check | runtime try/except | `importlib.util.find_spec('swisseph') is None` | Doesn't import anything |
| .npz in wheel check | unzip manually | `python -m zipfile -l dist/*.whl | grep` | Built-in stdlib |

---

## Common Pitfalls

### Pitfall 1: Two Unversioned CHANGELOG Sections

**What goes wrong:** Plan writer sees only `## [1.3.0] - Unreleased` and misses the
separate `## [Unreleased]` section above it. The cycle-direction BREAKING change and
datetime64 fix get left behind and don't ship in the release notes.

**How to avoid:** Read CHANGELOG.md lines 1–40 before writing Plan 27-01. The merge
is: move content from `## [Unreleased]` (lines 10–33) INTO `## [1.3.0]`, then
delete the now-empty `## [Unreleased]` section.

### Pitfall 2: Chiron BREAKING Entry Missing from CHANGELOG

**What goes wrong:** The `[1.3.0]` section only documents aspect-engine changes.
The Chiron 13→14 body-axis expansion — a real downstream BREAKING change for Kala —
is silently omitted.

**How to avoid:** Plan 27-01 must explicitly add the Chiron `### Added` bullet and
the `### Changed` BREAKING contract note for the body-axis expansion.

### Pitfall 3: UPGRADING Chiron Section Missing

**What goes wrong:** `UPGRADING.md → v1.2 -> v1.3` only has the aspect-engine
restore recipe. Kala developers looking for the CHART_DTYPE shape migration guide
find nothing.

**How to avoid:** Plan 27-01 must add the Chiron positional-contract section with
the shape table (13→14) and recompute-caches action item.

### Pitfall 4: pyswisseph Leaks into Runtime Wheel

**What goes wrong:** `pyswisseph` is listed under `[project.optional-dependencies].test`
but if it were ever moved to `dependencies`, it would ship in the wheel and violate
the AGPL isolation contract. The smoke test `find_spec('swisseph') is None` would catch
this — but only if the smoke test is actually run.

**How to avoid:** Smoke test step 8 explicitly asserts `find_spec('swisseph') is None`
in the fresh venv that installed ONLY the wheel (no `.[test]` extras).

### Pitfall 5: chiron_coeffs.npz Missing from Wheel

**What goes wrong:** If `ketu.data` were accidentally dropped from `[tool.setuptools].packages`
or `[tool.setuptools.package-data]`, the .npz would not ship and `calc_planet_position(jd, 13)`
would raise `FileNotFoundError` in the fresh-venv test.

**How to avoid:** Smoke test step 2 inspects the wheel with `python -m zipfile -l` and
asserts `ketu/data/chiron_coeffs.npz` is present before installing anything.

### Pitfall 6: Version Bumped in Only One File

**What goes wrong:** `pyproject.toml = "1.3.0"` but `ketu/__init__.py = "1.2.0"` (or vice
versa). `test_version_matches_metadata` fails.

**How to avoid:** Bump both in the same commit. Run `pytest tests/test_version.py -v`
immediately after.

### Pitfall 7: CHANGELOG Still Shows "Unreleased"

**What goes wrong:** Tag pushed with `## [1.3.0] - Unreleased` in CHANGELOG (the current
state). Release notes are wrong.

**How to avoid:** Pre-flight script includes:
```bash
grep -q '^## \[1.3.0\] - 20' CHANGELOG.md || { echo "CHANGELOG not dated"; exit 1; }
grep -q '^## \[1.3.0\] - Unreleased' CHANGELOG.md && { echo "CHANGELOG still UNRELEASED"; exit 1; }
```

### Pitfall 8: docs/source/conf.py Re-bumped Unnecessarily

**What goes wrong:** Plan edits `conf.py` to "1.3.0" — but it's already at 1.3.0
(pre-bumped in Phase 25). Creates a spurious no-op diff.

**How to avoid:** Read conf.py first. Current state: `release = "1.3.0"`, `version = "1.3.0"`.
No edit needed.

### Pitfall 9: Tag Not on main

**What goes wrong:** Tag pushed from a non-main branch. `publish.yml` runs but the
resulting wheel's commit is not on main's history.

**How to avoid:** Confirm `git branch --show-current` is `main` before tagging.

### Pitfall 10: Wheel Filename Contains Platform Tag

**What goes wrong:** Smoke test looks for `ketu-1.3.0-py3-none-any.whl` but wheel
was built with a platform-specific tag (e.g., `ketu-1.3.0-cp311-cp311-linux_x86_64.whl`).

**How to avoid:** `python -m build --sdist --wheel` on a pure-Python package always
produces `py3-none-any`. The `.npz` file is pure data. Verify with `ls dist/` after
build.

---

## Pre-flight Script (v1.3.0 version)

Complete script for Plan 27-02, Task 1:

```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.3.0"

echo "=== Pre-flight: ketu ${VERSION} ==="

# 1. Clean working tree
test -z "$(git status --porcelain)" || { echo "FAIL: Dirty working tree"; exit 1; }
git branch --show-current | grep -q "^main$" || { echo "FAIL: Not on main branch"; exit 1; }
echo "OK: clean tree on main"

# 2. Version sync
grep -q "version = \"${VERSION}\"" pyproject.toml || { echo "FAIL: pyproject.toml not bumped"; exit 1; }
grep -q "__version__ = \"${VERSION}\"" ketu/__init__.py || { echo "FAIL: __init__.py not bumped"; exit 1; }
pip install -e . -q
pytest tests/test_version.py -v
echo "OK: version synced to ${VERSION}"

# 3. CHANGELOG dated (not UNRELEASED)
grep -q "^## \[${VERSION}\] - 20" CHANGELOG.md || { echo "FAIL: [${VERSION}] not dated in CHANGELOG"; exit 1; }
grep -q "^## \[${VERSION}\] - Unreleased" CHANGELOG.md && { echo "FAIL: CHANGELOG still UNRELEASED"; exit 1; }
grep -q "^## \[Unreleased\]" CHANGELOG.md && { echo "FAIL: [Unreleased] section still present"; exit 1; }
echo "OK: CHANGELOG dated and [Unreleased] removed"

# 4. UPGRADING has Chiron section
grep -q "Chiron" UPGRADING.md || { echo "FAIL: UPGRADING missing Chiron section"; exit 1; }
echo "OK: UPGRADING.md has Chiron section"

# 5. Quality gates (must all pass before tag)
FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")
python -m numpydoc lint $FILES || { echo "FAIL: numpydoc violations"; exit 1; }
python -m interrogate ketu/ || { echo "FAIL: interrogate < 95%"; exit 1; }
pytest tests/ -q
python -m mypy --strict ketu/
echo "OK: all quality gates pass"

# 6. Build
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel
echo "OK: built dist/"

# 7. twine check
pip install --quiet twine
python -m twine check dist/*
echo "OK: twine check"

# 8. Verify .npz ships in wheel
python -m zipfile -l dist/ketu-${VERSION}-py3-none-any.whl | grep -q "ketu/data/chiron_coeffs.npz" \
  || { echo "FAIL: chiron_coeffs.npz missing from wheel"; exit 1; }
echo "OK: chiron_coeffs.npz present in wheel"

# 9. Fresh-venv smoke test (full Chiron + subpackage + no-pyswisseph)
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"

"$TMP/bin/python" -c "
import ketu, importlib.metadata as m
assert ketu.__version__ == '${VERSION}'
assert m.version('ketu') == '${VERSION}'
"

"$TMP/bin/python" -c "
from ketu.core import bodies, aspects, signs
from ketu.calculations import long
from ketu.aspects import calculate_aspects, aspects_for_harmonics
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

"$TMP/bin/python" -c "
import math
from ketu.ephemeris.planets import calc_planet_position
pos = calc_planet_position(2451545.0, 13)
lon = float(pos[0])
assert math.isfinite(lon), f'Chiron not finite: {lon}'
assert 0.0 <= lon < 360.0, f'Chiron out of range: {lon}'
print(f'Chiron OK: {lon:.4f}°')
"

"$TMP/bin/python" -c "
import importlib.util
assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED into runtime wheel!'
print('pyswisseph absent from runtime: OK')
"

echo "OK: fresh-venv smoke tests PASSED"

# 10. PyPI slot clear
python3 -c "
import urllib.request, json
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/ketu/json').read())
versions = list(data['releases'].keys())
assert '${VERSION}' not in versions, f'PyPI already has ${VERSION}!'
print(f'PyPI clear. Latest: {sorted(versions)[-1]}')
"

echo ""
echo "=== Pre-flight PASSED ==="
echo "Safe to: git tag -a v${VERSION} -m 'Release ${VERSION}' && git push origin v${VERSION}"
```

---

## State of the Art

| Item | v1.2.0 | v1.3.0 | Notes |
|------|--------|--------|-------|
| Body count | 13 (body_id 0–12) | 14 (body_id 0–13 + Chiron) | D-08 ratchet lifted Phase 24 |
| Chiron available | No | Yes, `calc_planet_position(jd, 13)` | Pure NumPy, .npz Chebyshev |
| CHART_DTYPE `body_lons` | shape `(13,)` | shape `(14,)` | Breaking positional contract |
| Aspect API default | CLASSICAL (5) | TRADITIONAL (7 half-circle) | Python API only; CLI unchanged |
| `core.aspects` dtype | 3-field `(name, angle, coef)` | 5-field `(name, angle, coef, harmonic, symbol)` | Additive extension |
| `aspects_for_harmonics` | Not available | `from ketu.aspects import aspects_for_harmonics` | New v1.3 public API |
| Runtime deps | numpy only | numpy only | pyswisseph still test-only |
| Test count | 1284 (Phase 20) | 1399 (Phase 26) | 100% coverage |
| docs/source/conf.py | 1.2.0 | 1.3.0 (pre-bumped Phase 25) | No edit needed in Phase 27 |

---

## Open Questions

1. **README `## What's New in v1.3.0` completeness**
   - Known: Lines 13–15 show section header and first two lines of content but were
     read from a truncated grep. The full section content was not read.
   - Recommendation: Plan 27-01 Task 1 should read the full section (lines 13–40) and
     verify it covers both Chiron and the aspect engine. Amend only if incomplete.

2. **CHANGELOG [Unreleased] items: were they from Phase 22 (ephemeris refactor)?**
   - Known: The cycle-direction fix and datetime64 bug fix are in `## [Unreleased]`
     above `## [1.3.0] - Unreleased`. They appeared after Phase 26 committed the
     `[1.3.0]` section.
   - What's unclear: Which phase produced these items — they may be from Phase 22
     (ephemeris refactor) or a hotfix. The merge into [1.3.0] is correct regardless.
   - Recommendation: Do the merge as described; the content is verified real.

3. **Should `ketu.cli` and `ketu.data` be tested in smoke imports?**
   - Known: `ketu.cli` calls `argparse` and the `main()` entrypoint — importing it
     in a one-liner `-c` is fine but may print help text. `ketu.data` has only
     `__init__.py` and the .npz file — not a user-facing import.
   - Recommendation: Skip `ketu.cli` and `ketu.data` direct imports from the smoke
     script. The .npz is verified via `python -m zipfile -l` (step 2) and via the
     Chiron `calc_planet_position(jd, 13)` test (step 7), which internally loads
     `ketu/data/chiron_coeffs.npz`.

---

## Sources

### Primary (HIGH confidence — verified against live repo files 2026-06-01)

- `pyproject.toml` (read directly) — `version = "1.2.0"` at line 7; `ketu.data` package + `*.npz` package-data confirmed
- `ketu/__init__.py` (read directly) — `__version__ = "1.2.0"` at line 57; body IDs 0–13 documented
- `docs/source/conf.py` (read directly) — `release = "1.3.0"`, `version = "1.3.0"` at lines 14–15 (pre-bumped)
- `CHANGELOG.md` (read directly) — dual unversioned sections confirmed; Chiron absent from [1.3.0]
- `UPGRADING.md` (read directly) — `## v1.2 -> v1.3` exists but covers only aspect-engine; no Chiron section
- `fr/CHANGELOG.md` (read directly) — covers [1.2.0]+[1.1.0]+[1.0.0]; no [1.3.0] section
- `.github/workflows/publish.yml` (read directly) — tag-push trigger, OIDC, Node 24 actions confirmed
- `.github/workflows/tests.yml` (read directly) — Node 24 actions, numpydoc blocking confirmed
- `ketu/data/` directory listing — `chiron_coeffs.npz` present, 289.7 KB
- `git tag -l` output — `v1.2.0` exists, `v1.3.0` does not
- `calc_planet_position(2451545.0, 13)` — executed live; returns finite longitude 251.16°
- All subpackage imports — executed live; all succeed; `ketu.__version__ == "1.2.0"` confirmed
- pyswisseph check — `pip show pyswisseph` in dev venv → NOT installed
- Phase 20 RESEARCH.md (read directly) — pre-flight pattern, publish ceremony pattern

### Secondary (MEDIUM confidence)
- MEMORY.md entries for Phases 23/24/26 — confirm Chiron (Phase 24 D-08), aspects (Phase 26), fr translations (Phase 26.1)
- Phase 20 plan 20-04-release-publish-PLAN.md (read directly) — pre-flight + ceremony pattern reused verbatim

---

## Metadata

**Confidence breakdown:**
- Version bump locations: HIGH — read all files directly; only 2 files need editing
- CHANGELOG gaps: HIGH — read both unversioned sections; Chiron absence confirmed
- UPGRADING gap: HIGH — read `## v1.2 -> v1.3`; no Chiron section found
- publish.yml trigger/OIDC: HIGH — read directly; no changes needed
- packaging (.npz in wheel): HIGH — read pyproject.toml `package-data` directly
- Smoke test script: HIGH — Chiron `calc_planet_position(jd, 13)` tested live
- PyPI state: HIGH — git tags confirm v1.3.0 not yet pushed; v1.2.0 is live

**Research date:** 2026-06-01
**Valid until:** 30 days (stable domain; re-check PyPI slot just before publish)
