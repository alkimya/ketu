---
phase: 12-release-preparation-v1-1-0
verified: 2026-05-08T00:30:00Z
status: passed
score: 9/9 must-haves verified
re_verification:
  previous_status: null
  note: "Initial verification — no prior VERIFICATION.md existed"
---

# Phase 12: Release Preparation v1.1.0 — Verification Report

**Phase Goal:** Ketu 1.1.0 is published to PyPI with a GitHub release, breaking-behavior changes documented, and a working migration guide for v1.0 users.
**Verified:** 2026-05-08T00:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth                                                                                       | Status     | Evidence                                                                                                                                |
| --- | ------------------------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Both source-of-truth version strings declare 1.1.0 and the sync test passes                 | VERIFIED   | `pyproject.toml` `version = "1.1.0"`, `ketu/__init__.py` `__version__ = "1.1.0"`, 31/31 version-related tests pass                       |
| 2   | CHANGELOG `[1.1.0]` section is date-stamped (NOT UNRELEASED) and covers all v1.1 phases     | VERIFIED   | Header `## [1.1.0] - 2026-05-08`; sections for BREAKING summary, Phase 9 CLI, Phase 11 CLI refactor, Phase 8 Lilith, Phase 10 houses     |
| 3   | UPGRADING.md ships all four v1.0 -> v1.1 migration recipes, with Lilith section preserved   | VERIFIED   | Sections at L14 Lilith, L101 CLI Default, L145 Kala adapter, L177 Houses Module, L218 stderr header (all under `## v1.0 -> v1.1`)        |
| 4   | PyPI page for ketu 1.1.0 resolves and lists the wheel + sdist                               | VERIFIED   | `HTTP 200` for https://pypi.org/project/ketu/1.1.0/; PyPI JSON returns `bdist_wheel` + `sdist`; CI sha256 matches 12-04-SUMMARY transcript |
| 5   | git tag v1.1.0 exists and is reachable from main                                            | VERIFIED   | `git tag -l v1.1.0` -> `v1.1.0`; SHA `54ce673`; `main..v1.1.0` = 0 commits ahead; only 1 docs commit (`237c42d`) on main after the tag    |
| 6   | GitHub release v1.1.0 published (not draft, not pre-release) with built artefacts attached  | VERIFIED   | `gh release view`: `isDraft=false`, `isPrerelease=false`, createdAt `2026-05-07T23:46:47Z`; assets: wheel (115780B) + sdist (305953B)    |
| 7   | `pip install ketu==1.1.0` from a fresh venv succeeds and re-exports public API              | VERIFIED   | Post-publish smoke transcript captured in 12-04-SUMMARY.md L80, L120, L127 — `__version__`, CLASSICAL.sum()==5, EXTENDED.sum()==14, houses imports all green |
| 8   | Full local test suite passes at 724 tests; CI matrix runs 557                                | VERIFIED   | `python -m pytest tests/ -q` -> `724 passed, 40 warnings in 13.62s`, 98.01% coverage; CI tests.yml run on `237c42d` succeeded; release notes document the 724 / 557 split |
| 9   | mypy --strict is clean across the package                                                   | VERIFIED   | `python -m mypy --strict ketu/` -> `Success: no issues found in 40 source files`                                                         |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact                                                | Expected                                            | Status     | Details                                                                                                  |
| ------------------------------------------------------- | --------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`                                        | `version = "1.1.0"`                                 | VERIFIED   | Confirmed by grep                                                                                        |
| `ketu/__init__.py`                                      | `__version__ = "1.1.0"`                             | VERIFIED   | Confirmed by grep                                                                                        |
| `tests/test_version.py`                                 | Sync gate green                                     | VERIFIED   | 2 sync-gate tests included in the 31/31 version-related green run                                        |
| `CHANGELOG.md` `[1.1.0]` section                        | Date-stamped, BREAKING + 4 phase entries            | VERIFIED   | `## [1.1.0] - 2026-05-08`; 8 sub-sections inc. BREAKING summary, Removed, Changed, Added, Fixed, Migration |
| `UPGRADING.md` `v1.0 -> v1.1` block                     | 4 recipes + Lilith preserved                        | VERIFIED   | Lilith (L14), CLI Default (L101), Kala adapter (L145), Houses (L177), stderr header (L218)              |
| `README.md` What's New section                          | Updated to v1.1                                     | VERIFIED   | L13: `## What's New in v1.1.0`                                                                           |
| Git tag `v1.1.0`                                        | Annotated, on main                                  | VERIFIED   | SHA `54ce673` on `main`                                                                                  |
| GitHub release `v1.1.0`                                 | Published, non-draft, with assets                   | VERIFIED   | URL https://github.com/alkimya/ketu/releases/tag/v1.1.0                                                  |
| PyPI release `ketu==1.1.0`                              | wheel + sdist live                                  | VERIFIED   | `ketu-1.1.0-py3-none-any.whl` sha256 `53b0ad66...`, `ketu-1.1.0.tar.gz` sha256 `1d540668...`             |
| `.planning/phases/12-release-preparation-v1-1-0/12-04-SUMMARY.md` | Post-publish smoke transcript captured     | VERIFIED   | Transcript at L120-127; references `/tmp/ketu-12-04-postpublish.txt`; SUMMARY L208 confirms FOUND        |

### Key Link Verification

| From                             | To                                            | Via                                       | Status     | Details                                                                                                  |
| -------------------------------- | --------------------------------------------- | ----------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------- |
| `pyproject.toml` version         | `ketu/__init__.py` __version__                | `tests/test_version.py` sync gate         | WIRED      | Both declare `1.1.0`; importlib.metadata round-trips in post-publish smoke                                |
| Local git tag `v1.1.0`           | GitHub `refs/tags/v1.1.0`                     | tag push triggered `publish.yml`          | WIRED      | Workflow run on `41ee42e` (date-stamp commit, the tagged SHA's parent message context) -> success         |
| `publish.yml` build              | PyPI `ketu==1.1.0`                            | trusted-publishing OIDC                   | WIRED      | Both wheel and sdist live with CI-built sha256s; `pip install ketu==1.1.0` works                          |
| GitHub release notes             | CHANGELOG / UPGRADING                         | repo-relative anchor links                | WIRED      | Body links `#110---2026-05-08` and `#v10---v11` resolve in `main` (sections present)                      |
| Post-publish smoke               | Public ketu API                               | `from ketu import calculate_houses, ...`  | WIRED      | Smoke imports `__version__`, `CLASSICAL`, `EXTENDED`, `calculate_houses`, `HOUSES_DTYPE`, `house_of` OK   |

### Requirements Coverage

| Requirement | Status    | Evidence                                                                                                                         |
| ----------- | --------- | -------------------------------------------------------------------------------------------------------------------------------- |
| REL-01      | SATISFIED | Version `1.1.0` in both `pyproject.toml` and `ketu/__init__.py`; sync test green; 12-01-SUMMARY confirms (Truth 1)                 |
| REL-02      | SATISFIED | CHANGELOG `[1.1.0]` date-stamped with BREAKING summary + Phase 8/9/10/11 entries; README "What's New" updated (Truth 2 + L13 README) |
| REL-03      | SATISFIED | UPGRADING covers CLI default, Kala adapter, Houses module, stderr header; Lilith section preserved (Truth 3)                       |
| REL-04      | SATISFIED | PyPI 1.1.0 live, GH release published, post-publish smoke green, tag reachable from main (Truths 4-7)                              |

### Anti-Patterns Found

None. The phase work is documentation + release ceremony — no code changes other than the version bump. Scanned 12-04-SUMMARY's commit/file lists for TODO/FIXME/placeholder markers tied to phase 12 work; only legitimate `## [Unreleased]` placeholder for the *next* release was retained at top of CHANGELOG, which is correct hygiene.

### Human Verification Required

None blocking. The release is irrevocable (PyPI version numbers cannot be reused), and every automated check above passes. Optional follow-ups for the human:

1. **Skim the rendered GitHub release page** at https://github.com/alkimya/ketu/releases/tag/v1.1.0 to confirm Markdown renders cleanly (anchors, code blocks, asset links). This is cosmetic; programmatically `gh release view` returns the expected body and assets.
2. **Confirm Kala downstream adoption plan** is on the calendar (per UPGRADING L145 guidance). Out of scope for this phase, but the ASP-04 / CLI-06 migration recipe is a downstream-action document.

### Gaps Summary

No gaps. All nine observable truths verified against the actual codebase, the actual git tag, the actual GitHub release, and the actual PyPI listing. Phase 12 has achieved its goal: ketu 1.1.0 is on PyPI, the GitHub release is live, breaking-behavior changes are documented in CHANGELOG, and v1.0 -> v1.1 migration recipes ship in UPGRADING.md. The v1.1 milestone is closed.

---

*Verified: 2026-05-08T00:30:00Z*
*Verifier: Claude (gsd-verifier)*
