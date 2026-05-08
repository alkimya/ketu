---
phase: 12-release-preparation-v1-1-0
plan: 04
subsystem: release
tags: [release, pypi, github-release, tag, oidc, trusted-publishing, ceremony]

# Dependency graph
requires:
  - phase: 12-release-preparation-v1-1-0
    provides: "12-01 version bump (pyproject.toml + ketu/__init__.py at 1.1.0); 12-02 CHANGELOG/README completion; 12-03 UPGRADING completion"
  - phase: 11-cli-refactor-integration
    provides: "ketu.cli:main entry point + argparse subcommands (CLI-01..CLI-06) — feature surface published"
  - phase: 10-houses-module
    provides: "ketu.calculate_houses + house_of + HOUSES_DTYPE — public API published"
  - phase: 09-configurable-aspects
    provides: "ketu.aspects.presets {CLASSICAL, TRADITIONAL, EXTENDED} + resolve_aspect_set — public API published"
  - phase: 08-lilith-calibration
    provides: "Corrected Lilith Mean Apogee formula matching SE_MEAN_APOG within 0.01 deg"
provides:
  - "v1.1.0 git tag (annotated, on commit reachable from main)"
  - "ketu 1.1.0 on PyPI (wheel + sdist) via trusted-publishing OIDC"
  - "GitHub release v1.1.0 with notes + dist artefacts attached"
  - "Closure of REL-04 and Phase 12; v1.1 milestone closed"
affects: [v1.1-milestone, public-distribution, downstream-consumers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Trusted-publishing release via .github/workflows/publish.yml: tag push -> CI rebuild + twine check -> OIDC handshake -> PyPI upload (no API token, no secrets in repo)"
    - "Date-stamp commit isolated: UNRELEASED -> YYYY-MM-DD as the LAST commit before tagging — makes the release-day decision auditable and not entangled with feature commits authored over multiple days"
    - "Two distinct fresh-venv smoke tests: pre-flight smoke against local dist/ wheel (Task 1, pre-tag), post-publish smoke against PyPI (Task 5, post-publish) — the second is the only one that proves the upload path actually works end-to-end"
    - "Pre-merge rebase (PR #26 merged with --rebase) keeps main's history linear; the v1.1.0 tag points directly at the date-stamp commit (41ee42e) reachable from main with no merge commit between"

key-files:
  created:
    - ".planning/phases/12-release-preparation-v1-1-0/12-04-SUMMARY.md"
  modified:
    - "CHANGELOG.md (Task 3 by prior executor: line 10 UNRELEASED -> 2026-05-08)"
    - ".planning/STATE.md (Phase 12 closure)"

key-decisions:
  - "Used --rebase merge for PR #26 (not --squash, not merge commit) per RESEARCH guidance: per-plan history preserved AND linear topology so v1.1.0 tag sits directly on date-stamp commit reachable from main"
  - "Local dist/ uploaded as GH release assets even though publish.yml rebuilt them in CI — gives users a fallback download path if PyPI is briefly unavailable; the local wheel is byte-identical-equivalent (same content; sha256 differs due to the build timestamp / pkginfo metadata in the WHEEL file, which is normal)"
  - "Post-publish smoke assertion corrected from plan's `len(CLASSICAL) == 5` to `int(CLASSICAL.sum()) == 5` (Rule 1) — CLASSICAL is a length-14 np.bool_ mask, NOT a length-5 list; the plan-as-written would have failed the smoke and forced a checkpoint after publish for what is a doc-vs-code bug, not a release defect"
  - "Out-of-scope items from RESEARCH (interrogate, numpydoc validate) explicitly NOT gated on this release — documented as gaps below; deferred to v1.2 docs hardening"

patterns-established:
  - "Tag push is the single irreversible step in the v1.x release ceremony — every other step (build, twine check, fresh-venv smoke against local wheel, PyPI availability check, trusted-publisher dashboard cross-check) runs BEFORE it"
  - "Continuation-agent handoff at human-action checkpoints: each prior executor commits its task then returns CHECKPOINT REACHED with completed-task table + commit hashes + current-task blocker — fresh executor verifies state still holds (HEAD, sha256, tag absence) before resuming"
  - "Release-notes body assembled from CHANGELOG.md by awk-extracting the [VERSION] block (between `^## \\[VERSION\\]` and the next `^## \\[`) — single source of truth, no copy-paste drift"

# Metrics
duration: ~3h (multi-session, human-in-loop)
completed: 2026-05-08
---

# Phase 12 Plan 04: Release-Publish Ceremony Summary

**Closes REL-04 and the v1.1 milestone: ketu 1.1.0 published on PyPI via trusted-publishing OIDC, GitHub release v1.1.0 live with notes + assets, post-publish fresh-venv smoke green.**

## Performance

- **Duration:** ~3h end-to-end across multiple sessions (human-in-loop checkpoints for PR review + irreversible tag push); active execution time (machine work only) ~12 min
- **Started:** 2026-05-07T22:47Z (Task 1 pre-flight by first executor)
- **Completed:** 2026-05-07T23:56Z (Task 6 SUMMARY/STATE on main)
- **Tasks:** 6 (4 auto, 2 human-checkpoint)
- **Continuation handoffs:** 3 (after Task 1 -> Task 2 PR/merge, after Task 2 -> Task 3 date-stamp, after Task 3 -> Task 4 tag-push)
- **Files modified across the plan:** `CHANGELOG.md` (Task 3, single-line date-stamp), `.planning/STATE.md` (Task 6), `.planning/phases/12-release-preparation-v1-1-0/12-04-SUMMARY.md` (Task 6, this file)

## Accomplishments

- Pre-flight (Task 1) green on `gsd/v1.1-milestone`: 724 tests, mypy `--strict` clean, `python -m build` + `twine check dist/*` PASSED on both wheel and sdist, fresh-venv smoke against local wheel OK, PyPI 1.1.0 confirmed not-yet-taken (latest was 1.0.0), CLI introspection (`--list-aspect-sets`, `--list-house-systems`) green from the freshly-installed wheel.
- PR #26 merged to main via `--rebase --delete-branch` (Task 2): history linear; remote `gsd/v1.1-milestone` branch deleted; main HEAD = `41ee42e` after Task 3.
- CHANGELOG.md date-stamped on main (Task 3): `## [1.1.0] - UNRELEASED` -> `## [1.1.0] - 2026-05-08`; single-line edit; commit `41ee42e` (`docs(release): date-stamp v1.1.0 CHANGELOG (2026-05-08)`); pushed.
- v1.1.0 annotated tag created and pushed (Task 4): tag SHA `54ce673`, points at commit `41ee42e`, message `Release 1.1.0 - configurable aspects, houses module, Lilith fix, CLI refactor`.
- publish.yml workflow run `25528308313` succeeded (Task 4): build job 18s, publish-to-pypi job 20s, total ~38s, OIDC handshake clean.
- PyPI listing confirmed live (Task 5): `https://pypi.org/project/ketu/1.1.0/` returns 200 with both `ketu-1.1.0-py3-none-any.whl` (CI sha256 `53b0ad668ccdea71af4ef8fbd9f73b6c8f20e31fefe618bb41906243498ea23b`) and `ketu-1.1.0.tar.gz` (CI sha256 `1d54066824e439352eecb7933572411029554e765a66feaedeff8581590aa9ae`).
- GitHub release v1.1.0 created (Task 5): `https://github.com/alkimya/ketu/releases/tag/v1.1.0`, title "Ketu 1.1.0 - Configurable aspects, houses module, Lilith correction", notes assembled from CHANGELOG [1.1.0] body + intro paragraph (links to UPGRADING.md v1.0->v1.1 anchor and CHANGELOG.md), both local dist artefacts attached as assets.
- Post-publish fresh-venv smoke (Task 6): `pip install ketu==1.1.0` from PyPI -> `import ketu; ketu.__version__ == '1.1.0'`, `importlib.metadata.version('ketu') == '1.1.0'`, `CLASSICAL.sum() == 5`, `EXTENDED.sum() == 14`, `from ketu import calculate_houses, HOUSES_DTYPE, house_of` all green.

## Task Commits

This plan's commits all live on `main` (the date-stamp commit was the only feature-touching commit; everything else was tag/release/state):

1. **Task 2 — PR #26 rebase-merged to main** — merge SHA `1353cc3` (per-plan commits from `gsd/v1.1-milestone` rebased linearly onto main; remote branch deleted)
2. **Task 3 — CHANGELOG date-stamp** — `41ee42e` (`docs(release): date-stamp v1.1.0 CHANGELOG (2026-05-08)`) — main HEAD before tag
3. **Task 4 — Annotated tag v1.1.0** — tag SHA `54ce673` (NOT a commit; annotated tag object pointing at `41ee42e`)
4. **Task 6 — SUMMARY + STATE** — pending after writing this file (will be `docs(12-04): complete release-publish ceremony — v1.1.0 published`)

## External Artefacts (the actual deliverables)

| Artefact | URL / Identifier |
| --- | --- |
| Tag (annotated) | `v1.1.0` -> commit `41ee42e` (tag object SHA `54ce673`) |
| publish.yml run | https://github.com/alkimya/ketu/actions/runs/25528308313 |
| PyPI page | https://pypi.org/project/ketu/1.1.0/ |
| PyPI wheel | https://files.pythonhosted.org/packages/.../ketu-1.1.0-py3-none-any.whl (sha256 `53b0ad668ccdea71af4ef8fbd9f73b6c8f20e31fefe618bb41906243498ea23b`) |
| PyPI sdist | https://files.pythonhosted.org/packages/.../ketu-1.1.0.tar.gz (sha256 `1d54066824e439352eecb7933572411029554e765a66feaedeff8581590aa9ae`) |
| GitHub release | https://github.com/alkimya/ketu/releases/tag/v1.1.0 |
| GitHub release wheel asset | `ketu-1.1.0-py3-none-any.whl` (115780 bytes; local sha256 `e3f4c61e475cfc036f1cfcf2c87cd5227027c80e59417af1117a95981cab9d6a`) |
| GitHub release sdist asset | `ketu-1.1.0.tar.gz` (305953 bytes; local sha256 `6ebb4ea8e5a53d4c00386ee0bc01ad752ff8f990c32314b40e94f790907d69e9`) |

**Note on dual sha256:** The local dist (uploaded as GH release asset) was built locally during Task 1 pre-flight; the PyPI dist was rebuilt by `publish.yml` in CI. Both contain the same Python source code; the sha256 difference is normal (build timestamp + WHEEL pkginfo metadata differs between local and CI builds). Functional equivalence verified by the post-publish smoke installing the PyPI wheel and finding `__version__ == '1.1.0'` plus all expected exports.

## Pre-flight Artefact Summary (captured by Task 1 executor)

```
Test count: 724
e3f4c61e475cfc036f1cfcf2c87cd5227027c80e59417af1117a95981cab9d6a  dist/ketu-1.1.0-py3-none-any.whl
6ebb4ea8e5a53d4c00386ee0bc01ad752ff8f990c32314b40e94f790907d69e9  dist/ketu-1.1.0.tar.gz
Pre-flight: OK
```

(Source: `/tmp/ketu-12-04-preflight-summary.txt` — captured at end of Task 1 step 11.)

## Post-publish Smoke Transcript (Task 6)

```
Post-publish smoke: OK - ketu 1.1.0 installs from PyPI and round-trips
  ketu.__version__ = 1.1.0
  importlib.metadata version = 1.1.0
  CLASSICAL.shape = (14,) dtype = bool sum = 5
  EXTENDED.shape  = (14,) dtype = bool sum = 14
```

Run from a fresh `python -m venv` -> `pip install --quiet --no-cache-dir ketu==1.1.0` -> assertions on `__version__`, importlib.metadata, CLASSICAL / EXTENDED mask shapes, dtypes, and bit counts; plus `from ketu import calculate_houses, HOUSES_DTYPE, house_of` import-only check (proves the public houses API is exported in the wheel). The venv was deleted after the test.

## Decisions Made

- **Merge strategy = `--rebase`** (not squash, not merge commit). Rationale: preserves the per-plan history (12-01 / 12-02 / 12-03 are still distinct commits on main) AND keeps the topology linear so the v1.1.0 tag sits directly on the Task 3 date-stamp commit `41ee42e` with no merge commit between (RESEARCH §Pitfall 3 averted).
- **Date-stamp commit is its own atomic commit on main, NOT a fixup of the version-bump commit.** The `UNRELEASED -> 2026-05-08` substitution is the only commit that knows the actual release date (the version bump was authored days earlier on the milestone branch). Isolating it as the LAST commit before tag makes post-mortem audit trivial: `git log --oneline -1 v1.1.0~0` always names the release date stamp, regardless of how the milestone branch was structured.
- **Rule 1 fix at Task 5 step 5:** plan-as-written asserts `len(CLASSICAL) == 5`. CLASSICAL is a length-14 `np.bool_` mask (5 True bits, 9 False bits) — `len(CLASSICAL) == 14`. Corrected to `int(CLASSICAL.sum()) == 5` (count True bits). Same correction applied to EXTENDED. Without this fix the post-publish smoke would have AssertionError'd, forcing a checkpoint return after publish for what is purely a plan documentation bug — the released wheel itself was correct (verified by the corrected assertion passing).
- **GH release notes link to `CHANGELOG.md#110---2026-05-08` and `UPGRADING.md#v10---v11`** anchors. Verified anchor format by reading the rendered CHANGELOG / UPGRADING in main; GitHub auto-generates anchors from headings via lower-case + hyphen-replace + period-strip.
- **Out-of-scope per RESEARCH:** `interrogate >=95%` and `numpydoc validate` were called out as v1.1 polish goals but never wired into CI. Not gating this release; deferred to v1.2 docs hardening. Documented as gaps below.
- **`fr/CHANGELOG.md` mirror:** does not exist in this repo; the heading at top of `CHANGELOG.md` (`> Consultez la version française dans fr/CHANGELOG.md.`) is aspirational. No date-stamp action taken; gap documented below.
- **Local dist attached to GH release as well as published to PyPI:** redundant in practice (PyPI is canonical), but gives a fallback download path if PyPI is briefly unavailable and is the convention from v1.0's release. Cost: ~420KB GH release storage; benefit: zero-friction fallback.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Post-publish smoke assertion used `len()` on np.bool_ mask**
- **Found during:** Task 5 step 5 (post-publish smoke) — caught by prior executor before resuming, applied here after `proceed` signal.
- **Issue:** Plan reference text:
  ```python
  from ketu.aspects.presets import CLASSICAL, EXTENDED
  assert len(CLASSICAL) == 5
  assert len(EXTENDED) == 14
  ```
  CLASSICAL and EXTENDED are length-14 `numpy.ndarray[bool]` masks (one bit per harmonic in `core.aspects`), so `len(CLASSICAL) == 14` always. The intended invariant is "5 of the 14 bits are True" -> `int(CLASSICAL.sum()) == 5`.
- **Fix:** Replaced both assertions with `int(CLASSICAL.sum()) == 5` and `int(EXTENDED.sum()) == 14`; added auxiliary `.shape == (14,)` and `.dtype == np.bool_` checks for readability.
- **Files modified:** None (assertion runs in an ephemeral subprocess; not committed to the repo).
- **Verification:** Smoke transcript above shows `CLASSICAL.shape = (14,) dtype = bool sum = 5` and `EXTENDED.shape = (14,) dtype = bool sum = 14` — both pass under the corrected assertion.
- **Plan-doc impact:** None retroactive; the plan file is now historical, but the next major release ceremony should reuse the corrected form.

**Total deviations:** 1 auto-fixed (1 doc-vs-code accuracy bug in the post-publish smoke assertion). Caught and resolved without escalating; no scope change; the released artefact was never at risk.

## Out-of-Scope Items (Documented as Gaps)

These items appeared in the v1.1 ROADMAP / RESEARCH but were explicitly out of scope per RESEARCH §Out of Scope and are intentionally NOT gating this release:

- **`interrogate >=95%` docstring coverage gate:** not installed, not configured in CI, not in `[project.optional-dependencies].dev`. Manual `interrogate ketu/` from a v1.2 development venv would be the path. No regression risk for v1.1 users.
- **`numpydoc validate` documentation linter:** not wired into `tests.yml` or any pre-commit hook. Same disposition as `interrogate`.
- **`fr/CHANGELOG.md` French mirror:** the header `> Consultez la version française dans fr/CHANGELOG.md.` exists in `CHANGELOG.md` but the file itself does not exist in the repo. Not date-stamped (nothing to stamp). Should either be created in v1.2 or the header should be removed; current state is "promise without delivery". Tracked as a docs cleanup item.

## Issues Encountered

- **None blocking.** publish.yml ran cleanly on the first push of `v1.1.0`. No OIDC issues, no twine warnings, no PyPI 4xx. Build job 18s, publish job 20s — well under the typical 3-7 min envelope.
- **Node.js 20 deprecation warning** on every step of the workflow (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4` running on Node 20). Cosmetic; will require a workflow refresh before September 2026 when Node 20 is removed. Tracked as v1.2 ops debt; non-blocking for v1.1.

## Verification Notes

Phase-level success criteria verified post-publish:

- `git tag --list v1.1.0` -> `v1.1.0` (tag exists locally + on origin via push)
- `git tag --contains 41ee42e | grep '^v1.1.0$'` -> `v1.1.0` (tag is reachable from main commit; Pitfall 3 averted)
- `curl -sf https://pypi.org/pypi/ketu/1.1.0/json` -> 200 with both `.whl` and `.tar.gz` URLs (PyPI public-facing API confirms publish)
- `gh release view v1.1.0` -> `tagName: v1.1.0`, `name: 'Ketu 1.1.0 - ...'`, two assets attached, `isDraft: false`, `isPrerelease: false`
- Fresh `pip install ketu==1.1.0` -> `__version__ == '1.1.0'` + all key imports succeed (post-publish smoke transcript above)
- `git show main:CHANGELOG.md | grep -q '^## \[1.1.0\] - 2026-05-08$'` -> 0 (date-stamp landed)
- `! git show main:CHANGELOG.md | grep -q '^## \[1.1.0\] - UNRELEASED$'` -> 0 (UNRELEASED removed)

## User Setup Required

None for end users — `pip install ketu==1.1.0` is the only action.

For repo maintainers, **no action required**: STATE.md update + this SUMMARY.md commit closes Phase 12 cleanly; v1.1 milestone is complete.

## Next Phase Readiness

- **REL-04 closed.** v1.1.0 is on PyPI; GitHub release is live; post-publish smoke green.
- **Phase 12 closed at 4/4 plans.** Plans 12-01 (version bump), 12-02 (CHANGELOG/README), 12-03 (UPGRADING), 12-04 (this) all complete.
- **v1.1 milestone closed at 5/5 phases.** Phases 8 (Lilith), 9 (Configurable Aspects), 10 (Houses), 11 (CLI Refactor), 12 (Release Prep) all done.
- **v1.2 milestone is the next planning frontier** (not in scope here). RESEARCH-flagged candidates for v1.2: docs hardening (interrogate + numpydoc), `eps_true` upgrade for high-latitude house precision (Plan 10-05 deferred item), `fr/CHANGELOG.md` mirror (or remove the aspirational header), Node.js 20 -> Node.js 24 workflow refresh.
- **No outstanding blockers.** A working-tree stash `pre-release-merge: unrelated phase09/11 plan drift` exists from a prior executor session — it is **NOT** part of v1.1 release scope and is left as-is for the user to triage when convenient. The release is complete regardless of stash disposition.

## Self-Check: PASSED

Verified after writing this SUMMARY.md:

- File `.planning/phases/12-release-preparation-v1-1-0/12-04-SUMMARY.md`: FOUND (this file)
- Tag `v1.1.0`: FOUND (`git tag -l v1.1.0` returns `v1.1.0`; tag SHA `54ce673`)
- Commit `41ee42e` (date-stamp): FOUND on main (`docs(release): date-stamp v1.1.0 CHANGELOG (2026-05-08)`)
- PyPI 1.1.0: FOUND (`curl -sf https://pypi.org/pypi/ketu/1.1.0/json` -> 200, both artefacts listed)
- GH release v1.1.0: FOUND (`gh release view v1.1.0` -> name/tag/assets present, draft=false)
- publish.yml run 25528308313: FOUND, conclusion=success
- Post-publish smoke transcript: FOUND in `/tmp/ketu-12-04-postpublish.txt`
- Pre-flight summary: FOUND in `/tmp/ketu-12-04-preflight-summary.txt`

---
*Phase: 12-release-preparation-v1-1-0*
*Completed: 2026-05-08*
*v1.1 milestone: CLOSED*
