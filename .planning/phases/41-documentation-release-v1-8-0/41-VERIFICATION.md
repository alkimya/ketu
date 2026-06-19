---
phase: 41-documentation-release-v1-8-0
verified: 2026-06-19T10:51:11Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
human_verification_resolved:
  - test: "Inspect the rendered French Sphinx build (make html SPHINXOPTS=\"-D language=fr\" from docs/) and navigate to the Concepts page, section 'CHART_DTYPE — champ body_decl_speed (Nouveau dans v1.8)'. Confirm the prose appears in French — not as English fallback."
    expected: "All v1.8 prose in the Concepts FR page renders in French; code blocks and identifiers remain byte-identical to EN."
    resolution: "CONFIRMED 2026-06-19. Orchestrator rebuilt FR docs clean (1-warning baseline) and inspected build/html/concepts.html directly: heading renders 'CHART_DTYPE — champ body_decl_speed (Nouveau dans v1.8)'; French prose markers present (consommateurs en aval, déclinaison ×22, montant/descendant ×12, seuil ×4, vitesse ×4); no English fallback. User confirmed ('OK — clore la phase'), having also spot-checked FR docs at the go/no-go gate."
---

# Phase 41: Documentation + Release v1.8.0 Verification Report

**Phase Goal:** The `body_decl_speed` field, the 0.01 d FD step, `DECL_STANDSTILL_EPS`, the chart-level helper, and the Ketu/Rahu boundary are fully documented in English and French, the version is bumped to 1.8.0, and `ketu==1.8.0` is live on PyPI.
**Verified:** 2026-06-19T10:51:11Z
**Status:** passed (human FR-rendering item resolved by orchestrator HTML inspection + user confirmation 2026-06-19)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `docs/source/api.md` and `docs/source/concepts.md` (EN + FR) document `body_decl_speed`, `DECL_STANDSTILL_EPS`, the chart-level `is_ascending_declination_chart` helper (distinct from v1.5 scalar), the 0.01 d step rationale, and the boundary principle; FR `.mo` recompiled (no English fallback) | ✓ VERIFIED | `api.md:180-247,638-655` — DECL_STANDSTILL_EPS section (value 0.001, purpose, scope note), is_ascending_declination_chart section with explicit "Distinct from the v1.5 scalar" comparison table, CHART_DTYPE table rows for body_decl + body_decl_speed; `concepts.md:482-543` — body_decl_speed meaning, Δt=0.01 d FD rationale, standstill contract, "Library design principle" stating downstream consumers compute no astronomy; FR catalogs: concepts.po has 6 translated v1.8 entries (heading + field intro + sign + FD rationale + standstill + boundary), api.po has 14 translated v1.8 entries; all 3 .mo newer than .po |
| 2 | `CHANGELOG.md` has a dated `[1.8.0]` entry (EN + FR via `fr/CHANGELOG.md`) documenting the new field and MINOR-not-patch rationale; `UPGRADING.md` gives explicit downstream re-pin guidance (dtype layout grows, positional/`.view()` users must adapt) | ✓ VERIFIED | `CHANGELOG.md:10-37` — `## [1.8.0] - 2026-06-17` with Added (body_decl_speed, DECL_STANDSTILL_EPS, is_ascending_declination_chart) and Notes (MINOR-not-patch, 16 fields, named-access safe, positional-must-adapt, link to UPGRADING); `fr/CHANGELOG.md:12-42` — identical structure in French; `UPGRADING.md:6-65` — "## v1.7 -> v1.8" above "## v1.6 -> v1.7" (newest-first), mentions 16 fields, MINOR, named-access safe, positional-must-adapt, verify snippet for `chart["body_decl_speed"].shape == (14,)`, and "Re-pin the `ketu` version in your project after upgrading" |
| 3 | `ketu==1.8.0` is live on PyPI via OIDC trusted publishing (push main + tag); human go/no-go gate honoured before publish | ✓ VERIFIED | `git ls-remote --tags origin` shows `refs/tags/v1.8.0` at `0c20d4c`; PyPI JSON API confirms 1.8.0 is live (latest version = 1.8.0); 41-03-SUMMARY.md records OIDC run 27820463468 succeeded; human gate evidence: 41-03-SUMMARY.md "Task 2: Human go/no-go gate — no commit (review-only checkpoint); user approved"; plan 03 is `autonomous: false` (hard stop enforced) |
| 4 | Post-publish fresh-venv smoke FROM PyPI confirms: `body_decl_speed` present in `CHART_DTYPE`, field populated with non-trivial values, `DECL_STANDSTILL_EPS` importable, no `pyswisseph` at runtime | ✓ VERIFIED | Re-ran `smoke_v18.py` in a fresh venv (`virtualenv /tmp/ketu18smoke_verify` + `pip install ketu==1.8.0` from PyPI) during this verification session: (a) body_decl_speed in CHART_DTYPE.names — OK; (b) shape (14,), finite, not all-zero — OK; (c) DECL_STANDSTILL_EPS = 0.001 — OK; (d) import swisseph raises ImportError — OK; printed SMOKE_OK. pyswisseph is in `[project.optional-dependencies] test` only — not a runtime dep of the wheel. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/source/api.md` | body_decl_speed + DECL_STANDSTILL_EPS + is_ascending_declination_chart EN docs | ✓ VERIFIED | body_decl_speed at line 647 (CHART_DTYPE table), DECL_STANDSTILL_EPS section at line 180, is_ascending_declination_chart section at line 199 with explicit distinctness table; runnable example at lines 231-246 |
| `docs/source/concepts.md` | dδ/dt concept + Δt step + standstill contract + boundary principle | ✓ VERIFIED | Section at lines 482-543: field intro, sign meaning, FD rationale (Δt=0.01 d), standstill contract, library design principle in generic terms |
| `CHANGELOG.md` | `[1.8.0]` EN changelog entry | ✓ VERIFIED | `## [1.8.0] - 2026-06-17` at line 10, dated and with Added + Notes sections |
| `fr/CHANGELOG.md` | `[1.8.0]` FR changelog entry | ✓ VERIFIED | `## [1.8.0] - 2026-06-17` at line 12 with Ajouts + Notes in French |
| `UPGRADING.md` | v1.7 -> v1.8 migration entry | ✓ VERIFIED | `## v1.7 -> v1.8` at line 6 (above `## v1.6 -> v1.7`), 16 fields, re-pin guidance, verify snippet |
| `docs/locale/fr/LC_MESSAGES/concepts.po` | FR translations of v1.8 concept content + name-clean | ✓ VERIFIED | 6 v1.8 msgid/msgstr pairs; 0 private-project name hits |
| `docs/locale/fr/LC_MESSAGES/concepts.mo` | Recompiled FR concepts catalog | ✓ VERIFIED | concepts.mo mtime 17 juin 21:16 > concepts.po mtime 17 juin 21:16 (newer) |
| `docs/locale/fr/LC_MESSAGES/api.po` | FR translations of v1.8 API docs | ✓ VERIFIED | 14 v1.8 msgid/msgstr pairs for DECL_STANDSTILL_EPS + is_ascending_declination_chart sections |
| `docs/locale/fr/LC_MESSAGES/api.mo` | Recompiled FR API catalog | ✓ VERIFIED | api.mo mtime 17 juin 21:13 > api.po mtime 17 juin 21:12 (newer) |
| `docs/locale/fr/LC_MESSAGES/changelog.po` | FR translations of [1.8.0] changelog | ✓ VERIFIED | 5 v1.8 msgid/msgstr pairs; [1.8.0] header translated |
| `docs/locale/fr/LC_MESSAGES/changelog.mo` | Recompiled FR changelog catalog | ✓ VERIFIED | changelog.mo mtime 17 juin 21:16 > changelog.po mtime 17 juin 21:15 (newer) |
| `pyproject.toml` | version = 1.8.0 | ✓ VERIFIED | Line 7: `version = "1.8.0"` |
| `ketu/__init__.py` | `__version__ = "1.8.0"` | ✓ VERIFIED | Line 57: `__version__ = "1.8.0"` |
| `docs/source/conf.py` | release + version = 1.8.0 | ✓ VERIFIED | Lines 14-15: `release = "1.8.0"` and `version = "1.8.0"` |
| `ketu/aspects/calculator.py` | name-cleaned docstrings | ✓ VERIFIED | `grep -rl 'Kala\|...' ketu/ --include='*.py'` returns zero files |
| `ketu/charts/core.py` | name-cleaned CHART_DTYPE docstring | ✓ VERIFIED | Zero private-project names in ketu/*.py |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `docs/source/api.md` | `ketu.charts.is_ascending_declination_chart` | documented chart-level helper distinct from v1.5 scalar | ✓ WIRED | Line 199: `### is_ascending_declination_chart(chart) — New in v1.8`; line 207: "**Distinct from the v1.5 scalar `is_ascending_declination(jdate, body)`:**" with comparison table |
| `docs/source/concepts.md` | `ketu.calculations.DECL_STANDSTILL_EPS` | documented standstill contract | ✓ WIRED | Line 500-502: defines DECL_STANDSTILL_EPS = 0.001 as public constant; line 507-511: library design principle referencing it |
| `git tag v1.8.0` | `.github/workflows/publish.yml` | tag push triggers OIDC publish | ✓ WIRED | `git ls-remote --tags origin` confirms refs/tags/v1.8.0 at 0c20d4c; OIDC run 27820463468 succeeded |
| `fresh venv` | `pypi.org/project/ketu/1.8.0` | `pip install ketu==1.8.0` FROM PyPI | ✓ WIRED | Fresh venv smoke re-run during verification: SMOKE_OK, body_decl_speed confirmed present and populated |
| `docs/locale/fr/LC_MESSAGES/concepts.po` | `docs/source/concepts.md` | gettext msgid -> msgstr | ✓ WIRED | 1451: msgid "CHART_DTYPE — body_decl_speed field (New in v1.8)" → msgstr "CHART_DTYPE — champ body_decl_speed (Nouveau dans v1.8)" |
| `docs/locale/fr/LC_MESSAGES/concepts.mo` | `docs/locale/fr/LC_MESSAGES/concepts.po` | sphinx-intl recompile | ✓ WIRED | .mo newer than .po confirmed |

### Data-Flow Trace (Level 4)

Fresh-venv smoke (run during this verification session) confirms the full chain:

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `smoke_v18.py` assertion (b) | `chart["body_decl_speed"]` | `ketu.charts.compute_chart` populating via finite-difference over `ketu.ephemeris` | Yes — shape (14,), all finite, not all-zero (non-trivial values from real ephemeris computation) | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| body_decl_speed present in CHART_DTYPE (published wheel) | fresh-venv `pip install ketu==1.8.0` + smoke_v18.py (a) | body_decl_speed in CHART_DTYPE.names — OK | ✓ PASS |
| body_decl_speed populated with non-trivial values | smoke_v18.py (b) | shape (14,), finite, not all-zero — OK | ✓ PASS |
| DECL_STANDSTILL_EPS importable from ketu.calculations | smoke_v18.py (c) | DECL_STANDSTILL_EPS = 0.001 — OK | ✓ PASS |
| pyswisseph absent at runtime | smoke_v18.py (d) | import swisseph raises ImportError — OK | ✓ PASS |
| Full test suite green | `pytest tests/ -q --tb=no` | 1691 passed, 2 skipped, 100% coverage | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes exist for this phase. The equivalent is `smoke_v18.py` run above — exit code 0, SMOKE_OK printed.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| DSPD-07 | 41-01 / 41-02 | Documentation EN + FR of body_decl_speed, Δt step, DECL_STANDSTILL_EPS, chart-level helper, boundary principle; FR .po translated + .mo recompiled | ✓ SATISFIED | All five documentation items confirmed in api.md + concepts.md (EN); concepts.po + api.po + changelog.po (FR, all non-empty); .mo recompiled; name-clean sweep returns zero across all shipped artifacts |
| REL-01 | 41-03 | ketu==1.8.0 shipped to PyPI via OIDC; MINOR bump in 3 files; dated [1.8.0] changelog EN+FR + UPGRADING v1.7→v1.8; human go/no-go honoured; post-publish smoke | ✓ SATISFIED | PyPI 1.8.0 confirmed live; tag v1.8.0 at 0c20d4c on origin; 3 version files all read 1.8.0; CHANGELOG.md + fr/CHANGELOG.md both have dated [1.8.0]; UPGRADING.md has v1.7->v1.8 section with re-pin guidance; human gate honoured (autonomous: false, "user approved" in SUMMARY); smoke re-run SMOKE_OK |

Note: REQUIREMENTS.md traceability table still shows DSPD-07 as "Pending" and the checkbox as `- [ ]` — this is a stale tracking artifact (the requirements file was not updated post-execution). The codebase evidence confirms the requirement is fully satisfied.

### Anti-Patterns Found

Scanned all files modified by this phase (ketu/synastry/__init__.py, ketu/synastry/core.py, ketu/aspects/calculator.py, ketu/houses/core.py, ketu/charts/core.py, docs/source/api.md, docs/source/concepts.md, CHANGELOG.md, docs/source/changelog.md, UPGRADING.md, fr/CHANGELOG.md, docs/locale/fr/LC_MESSAGES/*.po, pyproject.toml, ketu/__init__.py, docs/source/conf.py).

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ketu/charts/core.py` | 22 | Stale "canonical 13-body axis" (should be 14; pre-existing since commit b52154e, not introduced by phase 41) | INFO | Documentation-only; no correctness impact; pre-dates this phase |
| `ketu/synastry/core.py` | 24 | Stale "synastry indices 0..12" (should be 0..13; pre-existing since commit fce8901, not introduced by phase 41) | INFO | Documentation-only; no correctness impact; pre-dates this phase |

No TBD/FIXME/XXX debt markers found. No placeholders or empty implementations. No private-project names in any shipped artifact (grep across ketu/, docs/source/, docs/locale/, CHANGELOG.md, fr/CHANGELOG.md, UPGRADING.md returns zero hits).

### Human Verification Required

#### 1. FR Sphinx Build Rendering Check

**Test:** Build the FR docs locally: `cd docs && make html SPHINXOPTS="-D language=fr"`, then open `docs/_build/html/fr/concepts.html` and navigate to the section "CHART_DTYPE — champ body_decl_speed (Nouveau dans v1.8)".
**Expected:** The prose about dδ/dt meaning, the Δt=0.01 d finite-difference rationale, the standstill contract paragraph, and the library design principle all render in French. Code blocks and identifiers (body_decl_speed, DECL_STANDSTILL_EPS, etc.) are byte-identical to EN. No paragraph shows English text where French is expected.
**Why human:** The .mo binaries are confirmed recompiled and newer than their .po (verified by mtime check), and all v1.8 msgstr in concepts.po are non-empty (0 empty msgstr found after the v1.8 section). However, confirming that the built HTML actually renders French prose — rather than falling back to English due to a Sphinx locale resolution issue — requires visual inspection of the rendered output. A grep on the .po cannot substitute for the final HTML artifact.

### Gaps Summary

No gaps found. All four roadmap success criteria are verified against the codebase. One human verification item remains (FR rendered docs visual confirmation) — this is a spot-check, not a code gap.

---

_Verified: 2026-06-19T10:51:11Z_
_Verifier: Claude (gsd-verifier)_
