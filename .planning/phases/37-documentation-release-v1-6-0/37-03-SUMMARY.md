---
phase: 37-documentation-release-v1-6-0
plan: 03
subsystem: release
tags: [pypi, oidc, release, twine, github-release, declination-aspects, smoke-test]

# Dependency graph
requires:
  - phase: 37-documentation-release-v1-6-0
    provides: 37-01 (declination-aspects docs EN/FR) + 37-02 (version bump 1.6.0, changelogs, UPGRADING, README)
provides:
  - ketu==1.6.0 published to PyPI via OIDC trusted publishing
  - GitHub release v1.6.0 with sdist + wheel attached
  - v1.6.0 tag on main + origin/main pushed (RTD rebuilds v1.6 docs)
affects: [Kala (KetuAdapter consumes ketu==1.6.0), Rahu (future, consumes from PyPI)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fresh-venv smoke must run from a non-repo cwd (e.g. /tmp) so the local ketu/ source tree does not shadow the installed wheel"
    - "python -m venv fails in this sandbox (ensurepip missing); use uv venv / uv pip (or virtualenv) for isolated install tests"

key-files:
  created:
    - .planning/phases/37-documentation-release-v1-6-0/37-03-SUMMARY.md
  modified: []

key-decisions:
  - "Fixed a release-blocking CI-gate failure in Phase 36 code (ketu/declination/api.py) discovered during pre-flight: numpydoc GL01×3 + GL06/GL07 + a doctest np.str_ mismatch (commit 455cb36, docstring-only). The plan assumed gates were already clean; they were not."
  - "BLOCKING human go/no-go checkpoint honored — waited for explicit 'approved' before tagging (LOCKED feedback_validation_review_before_release). User reviewed the milestone first."
  - "Pushed BOTH the tag AND origin/main (LOCKED feedback_push_main_not_just_tag_on_release) — RTD follows main, PyPI follows the tag."

patterns-established:
  - "Pre-flight before irreversible publish: 14 hard gates (date-stamp, version sync ×3 incl. conf.py, changelogs, feature docs en+fr + .mo, quality gates, build, twine, .npz-in-wheel, fr-CHANGELOG-in-sdist, fresh-venv local-wheel smoke, PyPI slot free) — STOP on first red."

requirements-completed: [DECLA-05]

# Metrics
duration: ~25min
completed: 2026-06-04
---

# Phase 37: Documentation & Release v1.6.0 — Plan 03 Summary

**Shipped ketu==1.6.0 to PyPI via OIDC after a 14-gate local pre-flight and an explicit human go/no-go; both the tag and origin/main pushed, GitHub release attached, post-publish smoke from PyPI green.**

## Performance

- **Duration:** ~25 min (pre-flight + checkpoint wait + publish + verify)
- **Completed:** 2026-06-04
- **Tasks:** 2 auto + 1 blocking checkpoint (all done)
- **Files modified (production):** 1 (ketu/declination/api.py docstring fix)

## Accomplishments

### Task 1 — Pre-flight (14/14 hard gates PASS)
- Date-stamp 2026-06-04 across CHANGELOG.md / docs/source/changelog.md / fr/CHANGELOG.md
- Version 1.6.0 synced in pyproject.toml + ketu/__init__.py + docs/source/conf.py (release + version)
- Changelogs dated (no "Unreleased"), UPGRADING v1.5 → v1.6 present
- v1.6 feature docs (concepts.md + api.md EN) present, FR `.po` translated, `make html-fr` renders « contre-parallèle »
- Quality: numpydoc 0 violation, interrogate 99.7%, **mypy --strict CLEAN**, 1654 passed / 100% coverage, doctest green
- Build: pure-Python wheel + sdist; `twine check` PASSED; `.npz` (591 KB) in wheel; `fr/CHANGELOG.md` in sdist
- Fresh-venv local-wheel smoke (run from /tmp): version, all-imports incl. ketu.declination, parallel `[(0,1,'P',0.5,1.0)]`, empty-result, no-swisseph
- PyPI 1.6.0 slot confirmed free (was at 1.5.0)

### Checkpoint — Human go/no-go (BLOCKING)
Paused, presented the full pre-flight + the 3 deviations, and **waited**. User chose to review the milestone first, then replied "approved". No irreversible action before approval.

### Task 2 — Publish
- `git tag -a v1.6.0` on main (455cb36) → `git push origin v1.6.0` (triggered publish.yml) → `git push origin main`
- publish.yml run 26978132507: **SUCCESS** (build + publish-to-pypi via OIDC, 42s)
- GitHub release v1.6.0 created with `ketu-1.6.0-py3-none-any.whl` + `ketu-1.6.0.tar.gz` attached
- Post-publish smoke FROM PyPI (fresh venv, from /tmp): version 1.6.0 == metadata, all subpackages import (incl. ketu.declination), parallel `[(0,1,'P',0.5,1.0)]` detected, no pyswisseph
- Local build artifacts cleaned

## Deviations

1. **Release blocker fixed (commit 455cb36).** Pre-flight caught numpydoc (GL01×3, GL06/GL07) + a doctest `np.str_` mismatch in the Phase 36 `ketu/declination/api.py` docstrings — both gated as blocking by CI (tests.yml). Fixed docstring-only (summary placement, "Design notes" → "Notes" after "See Also", `str(result["kind"][0])`). No logic change.
2. **Sandbox venv workaround.** `python -m venv` can't bootstrap pip here (ensurepip missing); used `uv venv` / `uv pip` for the fresh-venv smokes. The first PyPI smoke needed `--refresh` to bypass uv's stale index cache (the artifact was in the simple index; the workflow was already SUCCESS).

## Verification

- `git tag -l v1.6.0` present; tag^{commit} == main == origin/main (455cb36)
- `gh run list --workflow=publish.yml` latest = SUCCESS
- `gh release view v1.6.0` lists both wheel + sdist assets
- PyPI simple index serves ketu-1.6.0 wheel + sdist; JSON API includes 1.6.0
- Fresh-venv `pip install ketu==1.6.0` from PyPI: version == metadata == "1.6.0", find_declination_aspects yields a DECLA_ASPECT_DTYPE result with ≥1 'P' row, find_spec('swisseph') is None

## Outcome

**ketu==1.6.0 is live on PyPI.** v1.6 (Declination Aspects) milestone delivered: the additive `ketu.declination` subpackage (parallels & contra-parallels), fully documented en+fr, with no breaking changes (CHART_DTYPE byte-identical, core.aspects unchanged).

- PyPI: https://pypi.org/project/ketu/1.6.0/
- Release: https://github.com/alkimya/ketu/releases/tag/v1.6.0
