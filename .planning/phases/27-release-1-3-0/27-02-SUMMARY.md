---
phase: 27-release-1-3-0
plan: "02"
subsystem: infra
tags: [pypi, release, oidc, github-release, smoke-test, chiron]

# Dependency graph
requires:
  - phase: 27-01
    provides: "version 1.3.0 synced in pyproject.toml + ketu/__init__.py; CHANGELOG merged to one dated [1.3.0] - 2026-06-01 (EN+FR); UPGRADING Chiron 13->14 section; 1399 tests / 100% coverage / mypy strict clean"
provides:
  - "ketu==1.3.0 published to PyPI via OIDC (REL-11)"
  - "GitHub release v1.3.0 with sdist + wheel assets"
  - "Post-publish smoke: version + 6 subpackages + Chiron 251.6125° + no swisseph ALL PASS"
  - "Milestone v1.3 Chiron & Engine Hardening COMPLETE"
affects: [kala, downstream-consumers, future-release-phases]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Tag-triggered OIDC publish: git tag -a -> push -> publish.yml SUCCESS (reuses Phase 20 pattern)"
    - "GitHub release with local artifacts: gh release create --notes ... dist/*.whl dist/*.tar.gz"
    - "Post-publish retry loop: PyPI CDN propagated immediately (attempt 1 succeeded)"

key-files:
  created:
    - ".planning/phases/27-release-1-3-0/27-02-SUMMARY.md"
  modified:
    - ".planning/STATE.md"

key-decisions:
  - "ketu==1.3.0 published 2026-06-01 via OIDC trusted publishing (no API tokens); milestone v1.3 COMPLETE"
  - "GitHub release notes anchor link uses real date 2026-06-01 (replaced YYYY-MM-DD placeholder per RESEARCH Pattern 3)"
  - "Post-publish smoke ran on attempt 1 — PyPI CDN propagated immediately after OIDC publish"

patterns-established:
  - "Pattern: dist/ artifacts built in pre-flight (27-01) are REUSED at publish time — no rebuild before tagging"
  - "Pattern: gh run watch blocks until SUCCESS; fail-fast if publish-to-pypi job fails"

# Metrics
duration: 6min
completed: 2026-06-01
---

# Phase 27 Plan 02: PyPI Publish + Smoke Test Summary

**ketu==1.3.0 published to PyPI via OIDC (tagged v1.3.0 on main, publish.yml SUCCESS), GitHub release with wheel+sdist attached, post-publish smoke confirms Chiron at 251.6125° + no pyswisseph + all subpackages — REL-11 satisfied, milestone v1.3 COMPLETE**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-01T18:55:24Z
- **Completed:** 2026-06-01T19:01:57Z
- **Tasks:** 1 auto task (Task 2 — checkpoint already cleared by human approval)
- **Files modified:** 2 (.planning/STATE.md, .planning/phases/27-release-1-3-0/27-02-SUMMARY.md)

## Accomplishments

- Signed annotated tag v1.3.0 created on main (commit `1f9fb80`) and pushed; publish.yml triggered and completed SUCCESS in ~41s (build 18s + publish-to-pypi 23s)
- GitHub release v1.3.0 created at https://github.com/alkimya/ketu/releases/tag/v1.3.0 with both `ketu-1.3.0-py3-none-any.whl` and `ketu-1.3.0.tar.gz` attached
- Fresh-venv post-publish smoke test from PyPI: version 1.3.0 OK, 6 subpackages OK, Chiron `calc_planet_position(2451545.0, 13)` = **251.6125°** (finite, in [0,360)) OK, `find_spec('swisseph') is None` OK — all four assertions PASSED on first attempt
- Local build artifacts cleaned (dist/, build/, ketu.egg-info removed)

## Pre-flight Gate Summary (from Task 1 — prior agent)

| Gate | Result |
|------|--------|
| 1. Clean tree on main | PASS |
| 2. Version sync 1.3.0 (pyproject + __init__) + test_version | PASS |
| 3. CHANGELOG dated [1.3.0] - 2026-06-01 (no Unreleased) | PASS |
| 4. UPGRADING.md has Chiron section | PASS |
| 5a. numpydoc lint — 0 violations | PASS |
| 5b. interrogate ketu/ — 99.7% | PASS |
| 5c. pytest tests/ — 1399 passed / 2 skipped / 100% coverage | PASS |
| 5d. mypy --strict ketu/ — clean (68 files) | PASS |
| 6. Build: ketu-1.3.0-py3-none-any.whl (490979 B) + ketu-1.3.0.tar.gz (966226 B) | PASS |
| 7. twine check dist/* — PASSED | PASS |
| 8. Wheel contains ketu/data/chiron_coeffs.npz (296611 B) | PASS |
| 9. Fresh-venv LOCAL wheel: version + imports + Chiron 251.6125° + no swisseph | PASS |
| 10. PyPI slot 1.3.0 FREE | PASS |
| 11. sdist ships fr/CHANGELOG.md | PASS |

**All 11 gates / 17 assertions PASSED → human approved → tag pushed**

## Task Commits

Task 2 (release ceremony) does not create source commits — the ceremony IS the publish event.

Prior Task 1 commits (from 27-01 execution + pre-flight prep):
- `a9cf350` — chore(27-01): bump version to 1.3.0 in both source-of-truth files
- `2658264` — docs(27-01): merge CHANGELOG into one dated [1.3.0] and add Chiron entries
- `4251709` — docs(27-01): add Chiron 13->14 positional-contract section to UPGRADING
- `1f9fb80` — docs(27-01): complete plan — SUMMARY.md + STATE.md (REL-10 satisfied) **← v1.3.0 tag points here**

**Plan metadata commit:** created at end of this execution (docs(27-02): complete release ceremony — STATE.md + SUMMARY.md)

## Release Artifacts

| Artifact | URL |
|----------|-----|
| PyPI package | https://pypi.org/project/ketu/1.3.0/ |
| GitHub release | https://github.com/alkimya/ketu/releases/tag/v1.3.0 |
| Wheel | ketu-1.3.0-py3-none-any.whl (490979 B) |
| sdist | ketu-1.3.0.tar.gz (966226 B) |
| Chiron data | ketu/data/chiron_coeffs.npz (296611 B in wheel) |

## Post-Publish Smoke Test Results

```
Attempt 1: pip install ketu==1.3.0 from PyPI...  -> Install succeeded on attempt 1
version OK: 1.3.0
subpackages OK   (synastry, composite, returns, parts, aspects, charts)
Chiron OK 251.6125
no swisseph OK
=== POST-PUBLISH SMOKE PASSED ===
```

## Files Created/Modified

- `.planning/phases/27-release-1-3-0/27-02-SUMMARY.md` — this file (created)
- `.planning/STATE.md` — Phase 27 COMPLETE, milestone v1.3 COMPLETE (modified)

## Decisions Made

- Tag was created as signed annotated tag (`git tag -a`) — gpg-agent cache was warm, no TTY issues
- `gh release create` used the RESEARCH Pattern 3 release notes body verbatim, replacing `YYYY-MM-DD` anchor-link placeholder with real date `2026-06-01`
- PyPI CDN propagated immediately — retry loop triggered 0 retries (1 attempt total)

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. All steps completed first-attempt without errors.

## REL-11 Satisfaction

REL-11 is **SATISFIED**:
- ketu==1.3.0 published to PyPI via OIDC trusted publishing (no API tokens) — SUCCESS
- GitHub release v1.3.0 has sdist + wheel attached — SUCCESS
- Fresh-venv `pip install ketu==1.3.0` smoke: version + all subpackages + Chiron finite + no pyswisseph — ALL PASS
- No irreversible action taken without the explicit human go/no-go (checkpoint cleared by prior agent handoff)

## Milestone v1.3 Status

**COMPLETE.** All 8 phases (21-27 + 26.1) delivered:
- Phase 21: Quality (QAL-10/11/12) — 100% coverage, numpydoc, doctests
- Phase 22: Ephemeris Refactor (REF-01/02/03) — strategy extraction, orbital.py split
- Phase 23: Spike Chiron (SPK-01/02) — GO verdict, Chebyshev params locked
- Phase 24: Chiron (CHIR-01..05) — 14th body, embedded .npz, D-08 breaking change
- Phase 25: Documentation (DOC-10/11/12) — 12 docs pages lifted to v1.3 surface
- Phase 26: Aspects Data-Driven (ASP-01/02/03) — 5-field dtype, aspects_for_harmonics, TRADITIONAL default
- Phase 26.1: French Translation (DOC-13) — 17/17 .po 100% translated, all .mo compiled
- Phase 27: Release 1.3.0 (REL-10/11) — version bump + PyPI publish + smoke test

**ketu v1.3.0 is live on PyPI.** 1399 tests / 100% coverage / mypy --strict / 57 doctests.

## Next Phase Readiness

Milestone v1.3 is archived. The next milestone (v1.4+) begins with a fresh planning cycle.
Kala downstream: adapt to the 13→14 body-axis positional contract (CHART_DTYPE shape expansion) per UPGRADING.md → v1.2 -> v1.3.

---
*Phase: 27-release-1-3-0*
*Completed: 2026-06-01*
