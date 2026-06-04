---
phase: 35-release-v1-5-0
verified: 2026-06-04T12:35:00Z
status: passed
score: 9/9 must-haves verified
---

# Phase 35: Release v1.5.0 Verification Report

**Phase Goal:** `ketu==1.5.0` published to PyPI via OIDC with a GitHub release — all quality gates green, version bumped in all source-of-truth files, CHANGELOG + UPGRADING documenting additive declination + arbitrary-harmonic surface, and a fresh-venv smoke from PyPI confirming the v1.5 surface works with no `pyswisseph` at runtime.
**Verified:** 2026-06-04T12:35:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | version 1.5.0 in all three source-of-truth files | VERIFIED | `pyproject.toml` line 7: `version = "1.5.0"`; `ketu/__init__.py` line 57: `__version__ = "1.5.0"`; `docs/source/conf.py` lines 14-15: `release = "1.5.0"` / `version = "1.5.0"` |
| 2 | CHANGELOG.md [1.5.0] date-stamped, content complete, no Unreleased | VERIFIED | `## [1.5.0] - 2026-06-04` at line 10; full Added/Changed/Fixed/Notes sections present; no `Unreleased` token in any changelog |
| 3 | docs/source/changelog.md [1.5.0] date-stamped | VERIFIED | `## [1.5.0] - 2026-06-04` at line 8 |
| 4 | fr/CHANGELOG.md dated [1.5.0] French section above [1.4.0] | VERIFIED | `## [1.5.0] - 2026-06-04` at line 12; `déclinaison` and `body_decl` present |
| 5 | UPGRADING.md v1.4->v1.5 as first section with all three sub-sections | VERIFIED | `## v1.4 -> v1.5` at line 6 (before `## v1.3 -> v1.4` at line 115); body_decl, node-speed (−0.052954), and additive API sub-sections present |
| 6 | README Roadmap has two v1.5 entries, no spurious What's New section | VERIFIED | `is_ascending_declination` at line 329; `--harmonics h7` at line 330; no `What's New in v1.5.0` section |
| 7 | Quality gates green: 1626 passed / 100% coverage / mypy --strict clean / interrogate 99.7% / doctest 65 passed | VERIFIED | pytest: 1626 passed, 2 skipped, 100% coverage; mypy: "no issues found in 69 source files"; interrogate: 99.7% (threshold 95%); make doctest: 65 passed |
| 8 | ketu==1.5.0 live on PyPI, tag v1.5.0 pushed, origin/main pushed, GitHub release with sdist+wheel | VERIFIED | PyPI JSON API: version 1.5.0, files `ketu-1.5.0-py3-none-any.whl` + `ketu-1.5.0.tar.gz`, upload_time 2026-06-04T10:23:38; git tag v1.5.0 exists; origin/main at e4d1624 (matches local HEAD); GitHub release `Ketu 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI` with both assets attached |
| 9 | publish.yml SUCCESS via OIDC; v1.5 API surface (declination, is_ascending_declination, is_out_of_bounds, --harmonics h7) reachable; no swisseph at runtime | VERIFIED | publish.yml run 26945916843: completed SUCCESS (build 17s + publish 18s); local install: `declination(2451545.0, 1) = -10.746°`, `is_ascending_declination = False`, `is_out_of_bounds = False`; `ketu --harmonics h7 aspects --date 2024-01-01` emits `H7-1 51°`; fresh-venv smoke (SUMMARY-documented): find_spec('swisseph') is None PASS |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | version = "1.5.0" | VERIFIED | Line 7 confirmed |
| `ketu/__init__.py` | `__version__ = "1.5.0"` | VERIFIED | Line 57 confirmed |
| `docs/source/conf.py` | release = "1.5.0" and version = "1.5.0" | VERIFIED | Lines 14-15 confirmed, no stale 1.4.0 remaining |
| `CHANGELOG.md` | `## [1.5.0] - 20` date-stamped | VERIFIED | Line 10: `## [1.5.0] - 2026-06-04` |
| `docs/source/changelog.md` | `## [1.5.0] - 20` date-stamped | VERIFIED | Line 8: `## [1.5.0] - 2026-06-04` |
| `fr/CHANGELOG.md` | `## [1.5.0] - 20` French section | VERIFIED | Line 12; déclinaison + body_decl present |
| `UPGRADING.md` | `## v1.4 -> v1.5` first section | VERIFIED | Line 6; three sub-sections present |
| `README.md` | `is_ascending_declination` in Roadmap | VERIFIED | Lines 329-330 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| pyproject.toml version | ketu/__init__.py __version__ | test_version_matches_metadata | WIRED | Both read 1.5.0; pytest test_version.py green |
| docs/source/conf.py release/version | RTD v1.5 docs branding | Sphinx reads conf.py | WIRED | Both release and version fields set to 1.5.0 |
| CHANGELOG.md body_decl + node-speed entries | UPGRADING.md v1.4->v1.5 | body_decl cross-reference | WIRED | UPGRADING.md body_decl and −0.052954 node-speed correction both present |
| GitHub tag v1.5.0 | publish.yml OIDC | push tag triggers workflow | WIRED | Run 26945916843 SUCCESS on tag v1.5.0 push |
| PyPI ketu==1.5.0 wheel | v1.5 API surface | pip install ketu==1.5.0 | WIRED | PyPI JSON API confirms both artifacts live; smoke assertions pass |

### Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| REL-01 — quality gates green | SATISFIED | 1626 tests / 100% coverage / mypy --strict clean / interrogate 99.7% / doctest 65 passed |
| REL-02 — version bumped, changelogs dated, UPGRADING + README updated | SATISFIED | All three version files at 1.5.0; CHANGELOG.md + docs/source/changelog.md dated 2026-06-04; fr/CHANGELOG.md French section present; UPGRADING v1.4->v1.5 first section; README Roadmap two v1.5 entries |
| REL-03 — PyPI published, tag + main pushed, GitHub release, smoke from PyPI | SATISFIED | PyPI JSON API confirms 1.5.0 live (2026-06-04T10:23:38); publish.yml run 26945916843 SUCCESS; tag v1.5.0 and origin/main both pushed (remote verified); GitHub release with sdist + wheel; post-publish fresh-venv smoke all 6 checks PASS |

### Anti-Patterns Found

None detected. The hardcoded `# Ketu v1.1.0` header in `ketu/cli/formatters.py` line 56 is intentional — it is a byte-stable CLI format version, distinct from the package version, pinned by `tests/cli/test_resolved_header.py`. Pre-existing; not introduced in this phase.

### Human Verification Required

None. All material assertions for this release phase are programmatically verifiable (version files, git tags, remote refs, PyPI API, CI workflow status, test suite). The user checkpoint gate (milestone review before tag/publish) was declared satisfied in the phase specification.

### Notes

- The tag `v1.5.0` points to commit `cf85e90` (the research file commit). HEAD is one commit ahead at `e4d1624` (the 35-02 SUMMARY + STATE.md update — pure planning docs, zero ketu/ or pyproject.toml delta). This matches the standard release ceremony pattern used in every previous milestone and does not affect the published artifact.
- The local project `venv` contains `pyswisseph` as a dev dependency, so `find_spec('swisseph')` is not None in that environment. The fresh-venv smoke proving `find_spec('swisseph') is None` was performed by Phase 35-02 using an isolated `virtualenv` environment installing only from PyPI (documented in SUMMARY). The PyPI wheel contains no pyswisseph dependency in its metadata.
- `interrogate` reports one missed object (`ketu/data/__init__.py`) giving 99.7% — above the 95% gate threshold.

---

_Verified: 2026-06-04T12:35:00Z_
_Verifier: Claude (gsd-verifier)_
