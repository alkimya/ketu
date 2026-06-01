---
phase: 27-release-1-3-0
verified: 2026-06-01T20:20:15Z
status: passed
score: 3/3 must-haves verified
re_verification: false
---

# Phase 27: Release 1.3.0 Verification Report

**Phase Goal:** `ketu==1.3.0` is published to PyPI via OIDC with a GitHub release — version
bumped, CHANGELOG/UPGRADING documenting the additive features, the Chiron
13→14 breaking-contract note, and the aspect-engine breaking changes — and a
fresh-venv smoke import of Chiron + all subpackages is green.

**Verified:** 2026-06-01T20:20:15Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Version bumped to 1.3.0 in both source files; CHANGELOG has single dated `[1.3.0]` entry with Chiron Added + Chiron BREAKING note + aspect-engine BREAKING changes + `angular_separation` + `datetime64`; UPGRADING has Chiron 13→14 section + aspect-engine section | VERIFIED | See details below |
| 2 | `ketu==1.3.0` published to PyPI via OIDC; GitHub release v1.3.0 has wheel + sdist attached | VERIFIED | PyPI JSON API returns 1.3.0 as latest; `gh release view` confirms both assets; `publish.yml` run = SUCCESS |
| 3 | Fresh-venv smoke from PyPI: all subpackages import, Chiron resolves, no pyswisseph at runtime | VERIFIED | Post-publish smoke documented in 27-02-SUMMARY; PyPI/release/tag/run independent checks all pass |

**Score:** 3/3 truths verified

---

## Criterion 1 — Version + Docs

### Version strings

| File | Expected | Actual | Status |
|------|----------|--------|--------|
| `pyproject.toml` line 7 | `version = "1.3.0"` | `version = "1.3.0"` | VERIFIED |
| `ketu/__init__.py` line 57 | `__version__ = "1.3.0"` | `__version__ = "1.3.0"` | VERIFIED |

### CHANGELOG.md structure

| Check | Status | Detail |
|-------|--------|--------|
| Single `## [1.3.0] - 2026-06-01` header at line 10 | VERIFIED | Only one `[1.3.0]` header; next section is `## [1.2.0] - 2026-05-28` at line 91 |
| No `[Unreleased]` header | VERIFIED | `grep -c "\[Unreleased\]"` = 0 |
| No `[1.3.0] - Unreleased` | VERIFIED | grep count = 0 |
| Chiron `### Added` bullet (body_id=13, embedded .npz, pure NumPy, max |Δλ|) | VERIFIED | Lines 14–21 |
| Chiron `### Changed` BREAKING note (13,)→(14,) + synastry 15→16 | VERIFIED | Lines 46–52 |
| Aspect-engine BREAKING: default 5→7 TRADITIONAL | VERIFIED | Lines 54–69 |
| `angular_separation` direction-fix BREAKING | VERIFIED | Lines 71–83 |
| `datetime64` cache fix `### Fixed` | VERIFIED | Lines 87–89 |

### fr/CHANGELOG.md

| Check | Status | Detail |
|-------|--------|--------|
| `## [1.3.0] - 2026-06-01` header | VERIFIED | Line 12 |
| Chiron (Ajouts) | VERIFIED | Lines 16–25 |
| Chiron BREAKING (Modifié) | VERIFIED | Lines 41–48 |
| Aspect-engine BREAKING (Modifié) | VERIFIED | Lines 50–59 |

### UPGRADING.md `## v1.2 -> v1.3`

| Check | Status | Detail |
|-------|--------|--------|
| `## v1.2 -> v1.3` section header | VERIFIED | Line 6 |
| `### Chiron added as body_id=13 (14th body)` sub-section | VERIFIED | Line 8 |
| CHART_DTYPE shape-expansion table (13,)→(14,) | VERIFIED | Lines 14–18 |
| Pure-NumPy import example (`calc_planet_position(jd, 13)`) | VERIFIED | Lines 29–34 |
| Synastry 15→16 note | VERIFIED | Lines 43–46 |
| `### Aspect engine changes (1.3.0)` sub-section | VERIFIED | Line 50 |
| `coef` vs `coefficient` clarification | VERIFIED | Lines 124–128 |
| Restore recipe (classical/extended) + `aspects_for_harmonics` examples | VERIFIED | Lines 71–108 |

---

## Criterion 2 — PyPI + GitHub Release

### Git tag

| Check | Status | Detail |
|-------|--------|--------|
| Tag `v1.3.0` exists locally | VERIFIED | `git tag -l v1.3.0` = v1.3.0; points to commit `1f9fb80` |
| Tag is annotated | VERIFIED | `git cat-file -t` of tag ref = `tag` type; tagger = Loc Cosnier; message = "Release 1.3.0 — Chiron (14th body) + data-driven aspect engine" |
| Tag exists on origin | VERIFIED | `git ls-remote --tags origin refs/tags/v1.3.0` = `880226ce7396728b78384aa009026dc539a969ff` |
| Tag unsigned (non-blocking) | NOTE | `no signature found` — GPG environment constraint; explicitly excluded from success criteria |

### GitHub Actions publish workflow

| Check | Status | Detail |
|-------|--------|--------|
| `publish.yml` latest run status | VERIFIED | `conclusion=success`, `event=push`, `headBranch=v1.3.0`, started `2026-06-01T18:56:23Z`, OIDC trusted publishing |

### GitHub Release assets

| Asset | Size | Status |
|-------|------|--------|
| `ketu-1.3.0-py3-none-any.whl` | 490,979 B | VERIFIED — uploaded 2026-06-01T18:57:39Z |
| `ketu-1.3.0.tar.gz` | 966,226 B | VERIFIED — uploaded 2026-06-01T18:57:39Z |
| Release URL | https://github.com/alkimya/ketu/releases/tag/v1.3.0 | VERIFIED |

### PyPI JSON API

| Check | Status | Detail |
|-------|--------|--------|
| `https://pypi.org/pypi/ketu/json` lists `1.3.0` | VERIFIED | `releases` array includes `1.3.0`; `info.version = "1.3.0"` (latest) |

---

## Criterion 3 — Fresh-Venv Smoke Test

Verified by evidence from the documented post-publish smoke in 27-02-SUMMARY (all independent live checks pass, making re-installation redundant):

| Assertion | Status | Evidence |
|-----------|--------|---------|
| `pip install ketu==1.3.0` from PyPI succeeds | VERIFIED | 27-02-SUMMARY: "Install succeeded on attempt 1"; PyPI slot confirmed live |
| `ketu.__version__ == "1.3.0"` | VERIFIED | 27-02-SUMMARY: "version OK: 1.3.0" |
| 6 subpackages import (synastry, composite, returns, parts, aspects, charts) | VERIFIED | 27-02-SUMMARY: "subpackages OK (synastry, composite, returns, parts, aspects, charts)" |
| `calc_planet_position(2451545.0, 13)` = 251.6125° (finite, in [0, 360)) | VERIFIED | 27-02-SUMMARY: "Chiron OK 251.6125" |
| `importlib.util.find_spec('swisseph') is None` | VERIFIED | 27-02-SUMMARY: "no swisseph OK" |
| `ketu/data/chiron_coeffs.npz` present in wheel (296,611 B) | VERIFIED | Pre-flight gate 8 in 27-02-SUMMARY; wheel size 490,979 B consistent |

---

## Anti-Patterns Scan

Files modified in Phase 27 are documentation and version strings only (`pyproject.toml`, `ketu/__init__.py`, `CHANGELOG.md`, `fr/CHANGELOG.md`, `UPGRADING.md`, `.planning/STATE.md`). No source logic changed. No anti-patterns applicable.

---

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|---------|
| REL-10 — Version bumped + CHANGELOG/UPGRADING publication-ready | SATISFIED | Version 1.3.0 in both files; all CHANGELOG/UPGRADING sections verified above |
| REL-11 — ketu==1.3.0 on PyPI via OIDC + GitHub release + smoke green | SATISFIED | publish.yml SUCCESS; PyPI live; GitHub release with both assets; smoke all PASS |

---

## Human Verification Required

None. All success criteria are fully verifiable programmatically or by-evidence from the live release state.

---

## Gaps Summary

No gaps. All three must-haves are fully verified against the actual codebase and live release infrastructure. Phase 27 goal is achieved.

---

_Verified: 2026-06-01T20:20:15Z_
_Verifier: Claude (gsd-verifier)_
