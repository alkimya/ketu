# Phase 20: Release Preparation v1.2.0 - Research

**Researched:** 2026-05-28
**Domain:** Python package release engineering — GitHub Actions refresh (Node 24), fr/CHANGELOG.md decision, numpydoc gate flip, PyPI trusted-publishing workflow.
**Confidence:** HIGH (all claims verified against live repo files)

---

## Summary

Phase 20 is the final phase of milestone v1.2. The infrastructure is
**already proven** from Phase 12 (v1.1.0 release). The publish workflow
exists, OIDC trusted publishing is configured on PyPI, and
`tests/test_version.py` provides the version-sync gate. Three OPS
requirements are not yet done: action version bumps (OPS-03), fr/CHANGELOG
decision (OPS-04), and the v1.2.0 publish ceremony itself (OPS-05).

Two additional items discovered during this research that are **not** in
the OPS requirements but must be in Phase 20's scope:

1. **The numpydoc gate must be flipped from warning to blocking.** The
   `tests.yml` step has `continue-on-error: true` and an in-file comment
   "Phase 20 (OPS-02 finalization): remove continue-on-error: true and
   the GL01 suppression". There are currently **103 numpydoc lint
   violations** across 10 files (mainly SS03 and PR09 — all fixable by
   adding periods). These must be fixed before flipping the gate.

2. **The Arabic Parts (Phase 19) CHANGELOG entry is missing from
   [Unreleased].** Every prior feature phase (16 synastry, 17 composite,
   18 returns) added its CHANGELOG bullet in a dedicated docs commit.
   Phase 19 had no such commit. Phase 20 must synthesize the v1.2.0
   CHANGELOG `[Unreleased]` → `[1.2.0]` entry, so it MUST include the
   Arabic Parts summary text that was never written.

**Primary recommendation:** Decompose Phase 20 into four sequential plans:
20-01 action version bump (OPS-03), 20-02 numpydoc fix + gate flip (OPS-02
finalization), 20-03 fr/CHANGELOG decision + CHANGELOG/UPGRADING/README
close-out (OPS-04 + OPS-05 prep), 20-04 release publish ceremony (OPS-05).
Plans 20-01 and 20-02 can run in parallel. 20-04 depends on all three.

---

## User Constraints

No CONTEXT.md exists for Phase 20 (no `/gsd:discuss-phase` was run).
All decisions are Claude's discretion within the OPS-03/04/05 requirements.

**Hard constraints from ROADMAP / requirements:**
- OPS-03: `actions/checkout@v5+`, `actions/setup-python@v6+`,
  `actions/upload-artifact@v5+`; zero Node 20 deprecation warnings.
- OPS-04: `fr/CHANGELOG.md` created (synthesized from English, not
  double-maintained) OR the aspirational reference removed — decision
  documented.
- OPS-05: `ketu==1.2.0` published on PyPI via OIDC trusted publishing;
  GitHub release with sdist + wheel; CHANGELOG `[1.2.0]` entry;
  UPGRADING.md additive-only migration recipes.
- No BREAKING heading in `[1.2.0]` — this is a non-breaking minor.
- `ketu.__version__ == importlib.metadata.version("ketu") == "1.2.0"`.

---

## Current State of the Repository (Verified 2026-05-28)

### Version locations (OPS-05)

- `pyproject.toml:7` — `version = "1.1.0"` (must bump to `"1.2.0"`)
- `ketu/__init__.py:57` — `__version__ = "1.1.0"` (must bump to `"1.2.0"`)
- No other version locations (no `setup.cfg`, no `setup.py`).
- `tests/test_version.py` — already implements `test_version_matches_metadata()`
  and `test_version_format()`. No new test needed; run after bump to verify.

### Git tags (OPS-05)

Currently: `0.1`, `v0.2.0`, `v0.2.1`, `v0.4.0`, `v1.0.0`, `v1.1.0`.
`v1.1.0` is on `main` and is live on PyPI. `v1.2.0` does NOT yet exist.

### PyPI state

- `ketu==1.1.0` is live: `pip install ketu` works.
- `ketu==1.2.0` is NOT on PyPI — version is clear.
- Trusted publisher configured (per Phase 7 and Phase 12 research):
  Owner=`alkimya`, Repo=`ketu`, Workflow=`publish.yml`, Environment=`pypi`.
  This persists across releases — no PyPI-side configuration needed.

### GitHub Actions — current action versions (OPS-03)

| File | Step | Current version | Required version |
|------|------|----------------|-----------------|
| `tests.yml` | checkout | `actions/checkout@v4` | `@v5+` |
| `tests.yml` | setup-python | `actions/setup-python@v5` | `@v6+` |
| `tests.yml` | codecov | `codecov/codecov-action@v4` | No OPS-03 requirement but check for Node 20 warnings |
| `publish.yml` | checkout | `actions/checkout@v4` | `@v5+` |
| `publish.yml` | setup-python | `actions/setup-python@v5` | `@v6+` |
| `publish.yml` | upload-artifact | `actions/upload-artifact@v4` | `@v5+` |
| `publish.yml` | download-artifact | `actions/download-artifact@v4` | No OPS-03 requirement explicitly, but must be consistent |
| `publish.yml` | pypa publish | `pypa/gh-action-pypi-publish@release/v1` | No change required |

**Exact changes required by OPS-03:**
- `actions/checkout@v4` → `actions/checkout@v5` (both workflow files)
- `actions/setup-python@v5` → `actions/setup-python@v6` (both workflow files)
- `actions/upload-artifact@v4` → `actions/upload-artifact@v5` (publish.yml)
- Check: `actions/download-artifact@v4` — must bump to `@v5` for artifact name/path
  compatibility with `upload-artifact@v5` (artifact v4/v5 format incompatibility).
- Check: `codecov/codecov-action@v4` — not in OPS-03 scope but should be reviewed
  for Node 20 warnings; bump to `@v5` if it emits deprecation warnings.

**Total: 2 workflow files, at most 6 action version changes.**

### numpydoc gate state (OPS-02 finalization — Phase 20 to-do)

The `tests.yml` "Doc style audit (numpydoc)" step has `continue-on-error: true`
with this in-code comment:

```
# Phase 20 (OPS-02 finalization): remove `continue-on-error: true` and
# the `"GL01"` suppression in `[tool.numpydoc_validation].checks` to
# flip this gate to blocking (per Phase 13 decisions D-04 / D-05).
```

And `pyproject.toml:126`:
```toml
"GL01",  # ignore during warning phase (Phase 13–19); fix and remove in Phase 20
```

**Current numpydoc violations (103 total across 10 files):**

| File | Issues |
|------|--------|
| `ketu/ephemeris/time.py` | 24 (SS03 ×7, PR09 ×8, RT05 ×6, PR08 ×2, PR09×1) |
| `ketu/aspects/timelines.py` | 12 (SS03, PR09 ×7, RT01 ×3, RT05) |
| `ketu/ephemeris/orbital.py` | 11 (SS03 ×9, PR01 ×1, RT01 ×1) |
| `ketu/ephemeris/coordinates.py` | 10 (SS03 ×10) |
| `ketu/cache/ephemeris_cache.py` | 10 (SS03 ×7, RT01 ×2, PR01 ×1) |
| `ketu/aspects/core.py` | 10 (SS03 ×10) |
| `ketu/ephemeris/planets.py` | 9 (SS03 ×8, GL08 ×1) |
| `ketu/aspects/calculator.py` | 7 (SS03 ×7) |
| `ketu/aspects/transits.py` | 3 (SS03 ×3) |
| `ketu/aspects/windows.py` | 2 (SS03 ×2) |
| `ketu/aspects/presets.py` | 2 (GL06, GL07 — unknown section "Public API") |

**Violation codes:**
- `SS03` (64): Summary does not end with period → add `.` to docstring summary lines
- `PR09` (15): Parameter description should finish with `.`
- `RT05` (8): Return value description should finish with `.`
- `RT01` (6): No Returns section found → add `Returns` section
- `PR01` (2): Parameter not documented
- `PR08` (2): Parameter description should start with capital letter
- `GL06/GL07` (2): Unknown section "Public API" in `aspects/presets.py`
- `GL08` (1): Object without docstring (`ephemeris/planets.py:302`)

**Note:** GL01 violations (0 currently) — GL01 is already being suppressed
in `pyproject.toml`. Removing the suppression may expose additional GL01
violations. However, since no GL01 issues appear currently even with the
suppression, removing it should be safe. Verify by running numpydoc lint
with GL01 removed from the exclude list before committing.

**interrogate status:** PASSES already at 100% (267/267). No action
needed for interrogate.

### fr/CHANGELOG.md (OPS-04)

`fr/` directory does NOT exist in the repo. The only reference keeping this
aspirational file alive is in `CHANGELOG.md` line 3:

```markdown
> Consultez la version française dans `fr/CHANGELOG.md`.
```

This single blockquote has been deliberately left untouched since Phase 13
(13-CONTEXT.md § Deferred Ideas explicitly called this out as OPS-04 Phase 20
territory). All Phase 13-19 plans have a hard guard "DO NOT touch fr/CHANGELOG.md".

**`fr/CHANGELOG.md` reference locations (all found):**
1. `CHANGELOG.md:3` — the blockquote `> Consultez la version française dans \`fr/CHANGELOG.md\`.`
2. `MANIFEST.in` — `recursive-include fr *.md` (includes `fr/` in sdist if it exists)

**Decision required (OPS-04):** Either:
- (A) CREATE `fr/CHANGELOG.md` — synthesize from English CHANGELOG;
  keep the blockquote in `CHANGELOG.md`; add a French `## [1.2.0]` entry
- (B) REMOVE the reference — delete the blockquote in `CHANGELOG.md`;
  optionally also clean `MANIFEST.in` (the `recursive-include fr *.md` line
  is harmless if `fr/` doesn't exist, but may as well remove for cleanliness)

**Recommendation:** Option (A) — create `fr/CHANGELOG.md`. The Sophie Chen
persona and the project's bilingualism make this the better long-term choice.
The file is explicitly described in OPS-04 as "synthesized from English,
not double-maintained" — meaning it is a translation artifact, not a
parallel editorial track. Write it once, update it at each release in the
same PR that touches `CHANGELOG.md`. This is consistent with `MANIFEST.in`
already having `recursive-include fr *.md`.

### CHANGELOG.md — [Unreleased] section state (OPS-05)

The `[Unreleased]` section currently has **148 lines** of content across
`### Added` and `### Changed`. It covers phases 13-18 but is **missing
Phase 19 (Arabic Parts)**. Confirmed by `git log --follow CHANGELOG.md`:
the most recent CHANGELOG commit is `64d5daf docs(18-05)` (Phase 18 returns).
No commit for Phase 19.

**What is in [Unreleased] already (verified):**
- OPS-01/02: CI doc-quality gates (interrogate ≥95%, numpydoc warning)
- Phase 16: `ketu.synastry` + CLI `ketu synastry` + `ketu --list-orbs` (SYN-01..05)
- Phase 17: `ketu.composite` + `circular_midpoint` + oracle fixtures (COMP-01..04)
- Phase 18: `ketu.returns` (solar_return + lunar_return) + oracle fixtures (RET-01..06)
- Phase 15: `HOUSES_DTYPE['system']` U10→U16 for Regiomontanus (### Changed)

**What is MISSING from [Unreleased] (Phase 19 — Arabic Parts):**
- `ketu.parts` subpackage (registry, `PartSpec`, `PARTS` dict, `register`,
  `get_part`)
- `calculate_part(chart, name)` — sect-aware dispatch (Fortune/Spirit)
- `calculate_all_parts(chart, parts=None)` — dict output
- 3 built-in parts: Fortune (sect-aware), Spirit (sect-aware), Marriage
  (sect-invariant formula)
- `ketu --list-parts` CLI flag
- `make parts-coverage` Makefile target (100% on ketu/parts/)
- `parts_coverage_gate` pytest marker

**What is MISSING from [Unreleased] (Phases 14/15 — additional house systems):**
Phase 13-RESEARCH notes "three new house systems" in the v1.2 API summary.
Let me check what house systems were added in v1.2:
- Phase 15 added Whole Sign + Equal + Regiomontanus (per MEMORY.md).
- CHANGELOG `### Changed` only mentions `HOUSES_DTYPE['system']` U10→U16 width.
- No `### Added` bullet for the three new house systems themselves (Whole Sign,
  Equal, Regiomontanus) in [Unreleased]. These may be missing CHANGELOG entries too.

**Note to planner:** Plan 20-03 must also add Phases 14/15 bullets to the
[Unreleased] → [1.2.0] section. Grep `ketu/houses/` and Phase 15 SUMMARY
files to determine what was added.

### UPGRADING.md — v1.1 → v1.2 section (OPS-05)

The file currently has only `## v1.0 -> v1.1`. There is NO `## v1.1 -> v1.2`
section. All v1.2 APIs are additive-only (no breaking changes). The section
needs to be created as "v1.1 → v1.2 new APIs" with:
- `ketu.synastry` — new import path
- `ketu.composite` — new import path
- `ketu.returns` — new import path + API asymmetry note (solar_return takes
  `target_year` integer, lunar_return takes `target_jd` Julian Date)
- `ketu.parts` — new import path, sect-aware calculate_part
- Three new house systems: Whole Sign (`"whole_sign"`), Equal (`"equal"`),
  Regiomontanus (`"regiomontanus"`)
- Note: No breaking changes; all existing v1.1 code continues to work.

### README.md (OPS-05 adjacent)

`README.md` currently has `## What's New in v1.1.0` section (lines 13-50).
This should be updated to `## What's New in v1.2.0` with v1.2 highlights
(synastry, composite, returns, Arabic parts, 3 new house systems, doc gates).
This is part of the release ceremony plan (20-04 or 20-03).

### Publish workflow (OPS-05) — already wired

`.github/workflows/publish.yml` already has:
- Trigger: `on.push.tags: ['v*.*.*']` — tag-push trigger
- Job `build`: checkout, Python 3.11, `python -m build --sdist --wheel`,
  `twine check dist/*`, `upload-artifact@v4` (will become @v5 after OPS-03)
- Job `publish-to-pypi`: needs `build`, `environment: pypi`,
  `permissions.id-token: write`, `pypa/gh-action-pypi-publish@release/v1`
- **No changes needed to publish logic** — only action version bumps.

### Test count and quality gates (current)

- 1284 tests pass, 2 skipped. Run time ~11.6 seconds.
- `interrogate` passes at 100%.
- `numpydoc lint` has 103 violations (warning-only in CI).
- `mypy --strict` status: not re-run here; assumed green from Phase 19.
- Coverage: 43% on `--collect-only` run (partial), but project-wide gate is 70%
  enforced in `pyproject.toml [tool.coverage.report]`.

---

## Standard Stack

### Core (already installed/configured)
| Tool | Version | Purpose | Note |
|------|---------|---------|------|
| setuptools | ≥61.0 | Build backend | `pyproject.toml` — unchanged from v1.1 |
| build | latest | PEP 517 build frontend | Used by `publish.yml` |
| twine | latest | sdist/wheel validation | Used by `publish.yml` |
| pypa/gh-action-pypi-publish | `release/v1` | OIDC trusted publishing | Already wired, no change |
| pytest | latest | Test runner | 1284+ tests |
| interrogate | ≥1.7.0 | Docstring coverage gate | Already passing 100% |
| numpydoc | ≥1.10.0 | Docstring style audit | 103 violations to fix |

### Action Versions (post-OPS-03)
| Action | Current | Target |
|--------|---------|--------|
| `actions/checkout` | `@v4` | `@v5` |
| `actions/setup-python` | `@v5` | `@v6` |
| `actions/upload-artifact` | `@v4` | `@v5` |
| `actions/download-artifact` | `@v4` | `@v5` (must match upload) |
| `codecov/codecov-action` | `@v4` | `@v5` (check if Node 20 warnings) |

**Note on Node.js version mapping:**
- `actions/checkout@v4` uses Node 20 → `@v5` uses Node 24
- `actions/setup-python@v5` uses Node 20 → `@v6` uses Node 24
- `actions/upload-artifact@v4` uses Node 20 → `@v5` uses Node 24
- `actions/download-artifact@v4` uses Node 20 → `@v5` uses Node 24

Confidence: MEDIUM (based on GitHub Actions changelog knowledge as of
training; verify by checking release notes at
https://github.com/actions/checkout/releases and
https://github.com/actions/setup-python/releases before bumping).

---

## Architecture Patterns

### Recommended Plan Decomposition (Phase 20)

```
.planning/phases/20-release-preparation-v1-2-0/
├── 20-01-action-version-bump-PLAN.md         # OPS-03 (independent, parallelizable)
├── 20-02-numpydoc-fix-and-gate-flip-PLAN.md  # OPS-02 finalization (independent, parallelizable)
├── 20-03-changelog-upgrading-frchangelog-PLAN.md  # OPS-04 + OPS-05 prep
└── 20-04-release-publish-PLAN.md             # OPS-05 ceremony (depends: 01+02+03)
```

**Wave 1 (parallel):** 20-01 + 20-02
**Wave 2 (sequential):** 20-03 (depends on 01+02 being merged)
**Wave 3 (human-in-loop):** 20-04

**Why four plans:**
- 20-01 is pure YAML editing, no code risk.
- 20-02 is docstring editing across 10 Python files — high line count,
  zero logic change. Reviewable independently.
- 20-03 is doc-only (CHANGELOG.md, UPGRADING.md, README.md, possibly
  `fr/CHANGELOG.md` creation). Zero code risk.
- 20-04 is the release ceremony — human-validated checkpoint.

### Pattern 1: Dual Hard-Coded Version (keep from v1.1)
```toml
# pyproject.toml
version = "1.2.0"  # was "1.1.0"
```
```python
# ketu/__init__.py
__version__ = "1.2.0"  # was "1.1.0"
```
Gate: `pytest tests/test_version.py -v` (already in CI).

### Pattern 2: Tag-Triggered Trusted Publishing (unchanged)
Push `v1.2.0` tag → `publish.yml` builds + publishes to PyPI via OIDC.
Sequence: merge to main → version bump commit → CHANGELOG date-stamp commit
→ tag → push tag.

### Pattern 3: Pre-flight + Smoke Test (same as v1.1.0)
Build locally, `twine check dist/*`, fresh-venv install, smoke-import.
Add v1.2-specific smoke imports: `from ketu.synastry import calculate_synastry`,
`from ketu.composite import calculate_composite`,
`from ketu.returns import solar_return`,
`from ketu.parts import calculate_part`.

### Pattern 4: numpydoc SS03 Fix (mechanical)
Every `SS03` violation = docstring summary line not ending with `.`.
The fix is always: append `.` to the one-line summary.
Example:
```python
# Before (SS03):
def foo(x):
    """Compute something from x"""

# After:
def foo(x):
    """Compute something from x."""
```
For `PR09` violations: parameter descriptions need `.` at end.
For `RT05`: return value descriptions need `.`.
For `RT01`: functions need a `Returns` section added.
For `GL06/GL07`: `aspects/presets.py` has non-standard "Public API" section —
remove or rename to a standard numpydoc section.

### Anti-Patterns to Avoid
- **Don't tag before merging to main.** Tag must be on main for `git log main`
  to show v1.2.0.
- **Don't flip numpydoc gate before fixing all 103 violations.** CI will fail.
- **Don't commit fr/CHANGELOG.md as a full translation project.** It is
  synthesized-and-frozen per OPS-04; just translate the `[Unreleased]` →
  `[1.2.0]` section's key bullet points.
- **Don't add new features in Phase 20.** Zero changes to `ketu/` source
  beyond `__init__.py` version string and docstring period-fixes.
- **Don't upload-artifact@v5 + download-artifact@v4.** These must match;
  v5 changed the artifact name+path schema.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PyPI authentication | API tokens | OIDC trusted publishing (already wired) | Already configured, tokens are unnecessary risk |
| Build artifacts | Manual `setup.py` | `python -m build --sdist --wheel` | PEP 517; already in publish.yml |
| Wheel validation | Manual inspect | `twine check dist/*` | Already in publish.yml |
| Version sync check | grep scripts | `pytest tests/test_version.py` | Already exists |
| numpydoc violations | Manual audit | `python -m numpydoc lint $(find ketu ...)` | Already wired in Makefile `make doc-gates` |
| GitHub release notes | GitHub UI | `gh release create v1.2.0 --notes "..."` | Reproducible, audit-able |

---

## Common Pitfalls

### Pitfall 1: upload-artifact@v5 + download-artifact@v4 Mismatch
**What goes wrong:** v5 changed artifact format; v4 download-artifact can't read v5 artifacts. Publish job fails at download step.
**How to avoid:** Bump BOTH `upload-artifact` AND `download-artifact` to `@v5` in `publish.yml` in a single commit.

### Pitfall 2: numpydoc GL01 Suppression Removal Exposes New Failures
**What goes wrong:** Removing `"GL01"` from `pyproject.toml` causes previously-hidden GL01 errors to appear. Gate flip fails CI.
**How to avoid:** Run `python -m numpydoc lint $(find ketu -name "*.py" ...)` WITHOUT the GL01 suppression first (temporarily remove from pyproject.toml locally) to confirm zero GL01 failures before committing the removal.

### Pitfall 3: Arabic Parts CHANGELOG Not Included in [1.2.0]
**What goes wrong:** Phase 19 never wrote a CHANGELOG entry. If Phase 20 just promotes [Unreleased] → [1.2.0], Arabic Parts is silently omitted from the release notes.
**How to avoid:** Plan 20-03 must explicitly draft Arabic Parts bullets (registry, calculate_part, calculate_all_parts, 3 built-in parts, --list-parts CLI, make parts-coverage) for the [1.2.0] CHANGELOG entry.

### Pitfall 4: Version Bumped in Only One File
**What goes wrong:** `pyproject.toml = 1.2.0` but `ketu/__init__.py = 1.1.0` (or vice versa). `test_version_matches_metadata` fails.
**How to avoid:** Bump both in the same commit. Run `pytest tests/test_version.py -v` immediately.

### Pitfall 5: CHANGELOG `UNRELEASED` / Missing Date
**What goes wrong:** v1.2.0 ships with `## [1.2.0] - UNRELEASED` (or no date at all).
**How to avoid:** In Plan 20-04 first task: replace the date in the new `[1.2.0]` header with the actual release date (2026-05-28 or later).

### Pitfall 6: fr/CHANGELOG.md in MANIFEST.in
**What goes wrong:** `MANIFEST.in` has `recursive-include fr *.md`. If `fr/CHANGELOG.md` is created, it is included in the sdist — which is correct. If OPS-04 decision is to NOT create fr/CHANGELOG.md, the `MANIFEST.in` line is harmless (no `fr/` directory, no files included), but is confusing.
**How to avoid:** If decision is (B) remove reference, also remove the `recursive-include fr *.md` line from `MANIFEST.in`.

### Pitfall 7: numpydoc aspects/presets.py GL06/GL07
**What goes wrong:** `ketu/aspects/presets.py` has a non-standard "Public API" section in its module docstring. GL06 and GL07 are triggered. Flipping the gate causes CI failure if this is not fixed.
**How to avoid:** In 20-02, remove or rename the "Public API" section in `ketu/aspects/presets.py:1` to a standard numpydoc section (e.g., absorb into Notes or remove the section header entirely).

### Pitfall 8: Phase 15 House Systems Missing from CHANGELOG
**What goes wrong:** Whole Sign, Equal, and Regiomontanus house systems were added in Phase 15 (per MEMORY.md `858 tests verts, 6 systems alphabétiques CLI, HOU2-01..05 satisfaits`) but the [Unreleased] CHANGELOG section only mentions the `HOUSES_DTYPE['system']` U10→U16 width change under `### Changed`. The three new systems themselves may have been omitted.
**How to avoid:** In Plan 20-03, verify by reading `ketu/houses/` to determine which systems are present, then confirm whether they appear in [Unreleased]. Add bullets if missing.

### Pitfall 9: Missing Python 3.13 Classifier (LOW risk)
**What goes wrong:** `pyproject.toml` already has `"Programming Language :: Python :: 3.13"` in classifiers — this is fine. No action needed.

### Pitfall 10: Trusted Publisher Misconfigured After Repo Actions
**What goes wrong:** PyPI OIDC publisher is per (owner, repo, workflow, environment) tuple. If repo was renamed or moved, publish fails.
**How to avoid:** Pre-flight: visit https://pypi.org/manage/project/ketu/settings/publishing/ and confirm Publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi.

---

## Code Examples

### Pre-flight Script (v1.2.0 version)
```bash
#!/usr/bin/env bash
set -euo pipefail
VERSION="1.2.0"

# 1. Clean working tree
test -z "$(git status --porcelain)" || { echo "Dirty working tree"; exit 1; }

# 2. Version sync
grep -q "version = \"${VERSION}\"" pyproject.toml || { echo "pyproject.toml not bumped"; exit 1; }
grep -q "__version__ = \"${VERSION}\"" ketu/__init__.py || { echo "__init__.py not bumped"; exit 1; }
pytest tests/test_version.py -v

# 3. CHANGELOG dated (not UNRELEASED)
grep -q "^## \[${VERSION}\] - UNRELEASED" CHANGELOG.md && { echo "CHANGELOG still UNRELEASED"; exit 1; }
grep -q "^## \[${VERSION}\] - 20" CHANGELOG.md || { echo "Missing dated [${VERSION}] header"; exit 1; }

# 4. numpydoc clean (gate should be passing after 20-02)
FILES=$(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")
python -m numpydoc lint $FILES || { echo "numpydoc lint failed"; exit 1; }

# 5. Build
rm -rf dist/ build/ ketu.egg-info/
python -m build --sdist --wheel

# 6. twine check
python -m pip install --quiet twine
python -m twine check dist/*

# 7. Fresh venv smoke test
TMP=$(mktemp -d)
python -m venv "$TMP"
"$TMP/bin/pip" install --quiet "dist/ketu-${VERSION}-py3-none-any.whl"
"$TMP/bin/python" -c "import ketu; assert ketu.__version__ == '${VERSION}'"
"$TMP/bin/python" -c "from ketu.synastry import calculate_synastry; print('synastry OK')"
"$TMP/bin/python" -c "from ketu.composite import calculate_composite; print('composite OK')"
"$TMP/bin/python" -c "from ketu.returns import solar_return; print('returns OK')"
"$TMP/bin/python" -c "from ketu.parts import calculate_part; print('parts OK')"
"$TMP/bin/python" -c "from ketu import calculate_houses; h = calculate_houses(2451545.0, 48.85, 2.35, system='whole_sign'); print('whole_sign OK')"
rm -rf "$TMP"

# 8. PyPI clear
python3 -c "
import urllib.request, json
data = json.loads(urllib.request.urlopen('https://pypi.org/pypi/ketu/json').read())
versions = list(data['releases'].keys())
assert '${VERSION}' not in versions, f'PyPI already has ${VERSION}'
print(f'PyPI clear. Last: {sorted(versions)[-1]}')
"

echo "Pre-flight PASSED. Safe to: git tag -a v${VERSION} -m 'Release ${VERSION}' && git push origin v${VERSION}"
```

### OPS-03: Workflow Action Bump Template
```yaml
# tests.yml and publish.yml: replace all occurrences
- uses: actions/checkout@v5          # was @v4
- uses: actions/setup-python@v6      # was @v5
- uses: actions/upload-artifact@v5   # was @v4 (publish.yml only)
- uses: actions/download-artifact@v5 # was @v4 (publish.yml only)
- uses: codecov/codecov-action@v5    # was @v4 (check for Node 20 warnings)
```

### OPS-02: Gate Flip in tests.yml
Remove `continue-on-error: true` from the numpydoc step:
```yaml
# Before:
- name: Doc style audit (numpydoc — warning only, blocking from v1.2.0)
  if: matrix.python-version == '3.13'
  continue-on-error: true
  run: |
    ...

# After:
- name: Doc style audit (numpydoc — now blocking)
  if: matrix.python-version == '3.13'
  run: |
    ...
```

And in `pyproject.toml`, remove `"GL01"` from the `[tool.numpydoc_validation].checks` list:
```toml
# Before:
checks = [
    "all",
    "EX01",
    "SA01",
    "ES01",
    "GL01",  # ignore during warning phase (Phase 13–19); fix and remove in Phase 20
]

# After:
checks = [
    "all",
    "EX01",
    "SA01",
    "ES01",
]
```

### fr/CHANGELOG.md skeleton (if OPS-04 decision = create)
```markdown
# Journal des modifications

Ce fichier est une traduction synthétisée de l'anglais `CHANGELOG.md`.
Il n'est pas maintenu en parallèle — les mises à jour sont faites à chaque
release en même temps que la version anglaise.

Voir le [CHANGELOG.md](../CHANGELOG.md) pour la version complète et faisant foi.

## [1.2.0] - 2026-05-28

### Ajout

- **`ketu.synastry`** — calcul de synastrie entre deux charts (`SYNASTRY_DTYPE`) avec orbes adaptées (facteur 0.5). CLI : `ketu synastry`. (SYN-01..05)
- **`ketu.composite`** — chart composite midpoint via `calculate_composite`. `circular_midpoint` vectorisable. (COMP-01..04)
- **`ketu.returns`** — retours solaires et lunaires via `solar_return` / `lunar_return` partageant un solveur NumPy bisection. (RET-01..06, LRET-01..05)
- **`ketu.parts`** — framework des Parts Arabes (Fortune sect-aware, Esprit sect-aware, Mariage sect-invariant). CLI : `ketu --list-parts`. (PARTS-01..08)
- **Trois systèmes de maisons supplémentaires** — Maisons Égales, Maisons Entières (Whole Sign), Régiomontanus. (HOU2-01..05)
- **Gates de qualité de documentation CI** — `interrogate ≥95%` (bloquant) + `numpydoc validate` (bloquant depuis v1.2.0). (OPS-01, OPS-02)
- **Refresh des workflows** — `actions/checkout@v5`, `actions/setup-python@v6`, `actions/upload-artifact@v5` (Node.js 24). (OPS-03)

## [1.1.0] - 2026-05-08

Voir [CHANGELOG.md](../CHANGELOG.md#110---2026-05-08) pour les détails.

## [1.0.0]

Voir [CHANGELOG.md](../CHANGELOG.md#100) pour les détails.
```

### GitHub release creation (v1.2.0)
```bash
gh release create v1.2.0 \
  --title "Ketu 1.2.0 — Synastry, Composite, Returns, Arabic Parts, 3 new house systems" \
  --notes "$(cat <<'EOF'
Ketu 1.2.0 is a non-breaking feature release adding five major new subpackages
and three additional house systems. All v1.1 code continues to work unchanged.

**New in v1.2.0:**
- `ketu.synastry` — calculate synastry between two charts (SYNASTRY_DTYPE, 8 fields, 225 body pairs)
- `ketu.composite` — midpoint composite chart derivation from two CHART_DTYPE records
- `ketu.returns` — solar and lunar return charts with relocation support
- `ketu.parts` — Arabic Parts framework (Fortune, Spirit, Marriage; sect-aware dispatch)
- Three additional house systems: Whole Sign, Equal, Regiomontanus
- CI doc gates: interrogate ≥95% (blocking) + numpydoc (now blocking)
- Workflow refresh: Node.js 24 across all actions

**No breaking changes.** See [UPGRADING.md] for migration notes (additive APIs only).

- 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md#120---2026-05-28)
- 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v11---v12)
- 📦 `pip install ketu==1.2.0`

1284+ tests, mypy strict, 100% coverage on all new subpackages.
EOF
)"
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|-----------------|--------|
| `actions/checkout@v4` (Node 20) | `@v5` (Node 24) | Eliminates deprecation warnings |
| `actions/setup-python@v5` (Node 20) | `@v6` (Node 24) | Eliminates deprecation warnings |
| `actions/upload-artifact@v4` (Node 20) | `@v5` (Node 24) | Eliminates deprecation warnings; new artifact format |
| numpydoc `continue-on-error: true` | Blocking gate | OPS-02 finalization (Phase 20 to-do per in-code comment) |
| `fr/CHANGELOG.md` — non-existent aspirational reference | Created or removed (decision) | OPS-04 resolution |

**Deprecated / outdated:**
- `GL01` suppression in `pyproject.toml` — to be removed in Phase 20 (per pyproject.toml comment).
- `continue-on-error: true` on numpydoc step — to be removed in Phase 20 (per tests.yml comment).

---

## Open Questions

1. **OPS-04: Create fr/CHANGELOG.md or remove the reference?**
   - Known: `fr/` directory does not exist; the only in-repo reference is
     `CHANGELOG.md:3` and `MANIFEST.in` (harmless).
   - Recommendation: CREATE (Option A). Consistent with Sophie's bilingual
     persona. Low effort (single synthesized file, never double-maintained).
     Already covered by `MANIFEST.in recursive-include fr *.md`.

2. **Are codecov/codecov-action@v4 warnings a Node 20 issue?**
   - Known: `codecov/codecov-action@v4` is in `tests.yml`. OPS-03 explicitly
     requires checkout/setup-python/upload-artifact; it doesn't mention
     codecov. But if codecov@v4 emits Node 20 deprecation warnings, OPS-03's
     "zero Node 20 deprecation warnings" criterion would require bumping it too.
   - Recommendation: bump to `@v5` as part of OPS-03 sweep. Verify changelog
     at https://github.com/codecov/codecov-action/releases.

3. **Phase 15 CHANGELOG missing entries for Whole Sign / Equal / Regiomontanus?**
   - Known: [Unreleased] has `### Changed` for `HOUSES_DTYPE` width bump but no
     `### Added` entry for the three new house systems. Phase 15 MEMORY.md says
     "6 systems alphabétiques CLI, HOU2-01..05 satisfaits".
   - Recommendation: Plan 20-03 must check `ketu/houses/` for present systems
     and add bullets for any that appear in code but not in [Unreleased].

4. **Branch: is current HEAD on main?**
   - Known: git status shows `main` branch.
   - Confirmed: v1.1.0 tag is on main. Phase 20 work begins on main directly
     (no milestone branch). All commits can go straight to main.

5. **Should the pyproject.toml also list Python 3.14 / drop 3.10?**
   - Known: classifiers include 3.10, 3.11, 3.12, 3.13; matrix is the same.
   - Recommendation: Out of scope for Phase 20. Python 3.14 is pre-release
     as of 2026-05-28; 3.10 EOL is Oct 2026. Keep matrix unchanged.

---

## Out of Scope (Explicit)

The planner MUST NOT add tasks for:
- **New features or subpackages.** No code changes to `ketu/` source beyond
  `__init__.py` version string and docstring period-fixes in 10 existing files.
- **Davison composite** — deferred to v1.3 (per COMP-04 and phase 17 decisions).
- **Chiron / Centaurs** — v1.3+ per REQUIREMENTS.md.
- **TestPyPI dry-run** — optional (skipped in v1.0 and v1.1.0; local smoke
  test is sufficient).
- **Sphinx / ReadTheDocs republish** — RTD auto-builds on push to main.
- **Matrix expansion (Python 3.14, drop 3.10)** — out of scope; stability first.
- **Moving from setuptools to hatchling/poetry** — not in v1.2.
- **Sigstore attestation** — `pypa/gh-action-pypi-publish@release/v1` emits
  attestations by default; nothing to do.
- **Kala (sibling repo)** — migration recipe is text-only in UPGRADING.md.

---

## Sources

### Primary (HIGH confidence — verified against live repo)
- `pyproject.toml` (read directly) — version 1.1.0, action versions, numpydoc config, GL01 comment
- `ketu/__init__.py` (read directly) — `__version__ = "1.1.0"` at line 57
- `tests/test_version.py` (read directly) — confirms version-sync test exists
- `.github/workflows/tests.yml` (read directly) — all action @v4/@v5 pins; Phase 20 OPS-02 comment; numpydoc `continue-on-error: true`
- `.github/workflows/publish.yml` (read directly) — all action @v4/@v5 pins; trusted publishing wiring
- `CHANGELOG.md` (read directly) — `[Unreleased]` section covers Phase 13-18 but NOT Phase 19 (Arabic Parts); `fr/CHANGELOG.md` blockquote at line 3
- `UPGRADING.md` (read directly) — only `## v1.0 -> v1.1` exists; no v1.2 section
- `MANIFEST.in` (read directly) — `recursive-include fr *.md` present
- `README.md` (read directly) — `## What's New in v1.1.0` needs update
- `numpydoc lint` (run directly) — 103 violations in 10 files; violation breakdown verified
- `interrogate` (run directly) — 100% pass (267/267)
- `git tag -l` (run directly) — no `v1.2.0` tag
- PyPI JSON API (queried directly) — `ketu==1.2.0` not yet published
- `git log --follow CHANGELOG.md` (run directly) — last CHANGELOG commit is Phase 18 (returns); no Phase 19 entry

### Secondary (MEDIUM confidence)
- GitHub Actions changelog (training data, Aug 2025 cutoff): checkout@v5 = Node 24, setup-python@v6 = Node 24, upload-artifact@v5 = Node 24. Verify before bumping at official release pages.
- `.planning/MILESTONES.md`, `.planning/STATE.md` — confirm Phase 20 is next and OPS-03/04/05 are Pending.

### Tertiary (LOW confidence)
- Phase 15 CHANGELOG gap (Whole Sign / Equal / Regiomontanus missing from [Unreleased]) — inferred from absence in CHANGELOG diff; planner must verify by reading ketu/houses/ and Phase 15 SUMMARY files before writing plan 20-03.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — reused from Phase 12; no new tools
- Action versions: MEDIUM — verify against official release pages before bumping
- numpydoc violations: HIGH — run live against repo; all 103 counted
- fr/CHANGELOG state: HIGH — fr/ directory confirmed absent; single reference found
- CHANGELOG gap (Phase 19): HIGH — git log confirms no Phase 19 CHANGELOG commit
- PyPI state: HIGH — queried live API; 1.2.0 not taken
- Architecture (plan decomposition): HIGH — maps 1:1 to requirements

**Research date:** 2026-05-28
**Valid until:** 30 days (stable domain; re-check action versions at plan time)
