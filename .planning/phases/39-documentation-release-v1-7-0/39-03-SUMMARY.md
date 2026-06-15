---
phase: 39-documentation-release-v1-7-0
plan: "03"
status: complete
requirements: [REL-01]
date: 2026-06-15
---

# 39-03 Summary — Release ceremony: ship ketu==1.7.0 to PyPI

## What was built

`ketu==1.7.0` is live on PyPI (OIDC trusted publishing), origin/main + tag
v1.7.0 pushed, GitHub release v1.7.0 created with sdist+wheel, and a
post-publish fresh-venv smoke FROM PyPI passes. The blocking human go/no-go
relecture-validation was honoured before any irreversible action.

### Task 1 — Local pre-flight (reversible)
- `make test`: **1666 passed**, 2 skipped, **100% coverage**.
- `make mypy` (`mypy --strict ketu/`): clean, 72 files.
- `make doctest`: **caught a stale docstring** — `synastry_orb_limit`'s example
  still claimed Rahu was a zero-orb body (returned `0.0`); with v1.7's 2° orb it
  returns `1.0`. Fixed the doctest, the Returns prose, and the user-facing
  `ketu --list-orbs` CLI note (commit 94828ac). Re-ran: 67 passed.
- `make doc-gates`: PASSED (interrogate 99.7% ≥ 95%, numpydoc clean).
- `python -m build` → `ketu-1.7.0.tar.gz` + `ketu-1.7.0-py3-none-any.whl`;
  `twine check dist/*` PASSED.
- Local-wheel fresh-venv smoke (virtualenv, since system python lacks
  ensurepip): version 1.7.0; orbs=2; ≥1 node/Lilith aspect; Rahu-Ketu
  Opposition absent; no runtime swisseph.

### Task 2 — Human go/no-go relecture-validation (BLOCKING)
- Presented the full milestone + pre-flight results and PAUSED.
- User asked "La doc Sphinx est-elle à jour ?" → built EN+FR Sphinx HTML and
  **found a broken cross-reference**: the 39-01 api.md edit linked to
  `concepts.md#orbs`, but `myst_heading_anchors` is not enabled so the anchor
  did not resolve (`local id not found in doc concepts: orbs`). Dropped the
  fragment, re-translated the FR `.po` entry, recompiled `api.mo` (commit
  a26653f). Re-built clean EN+FR HTML with v1.7 content rendered (tautolog/MINOR
  EN; tautologique/version mineure FR). Re-ran gates (all green) + rebuilt dist.
- User then gave an explicit **go**. No tag/push/publish occurred before this.

### Task 3 — Tag, push, OIDC publish, GitHub release (irreversible)
- Annotated tag `v1.7.0` created.
- Pushed **both** `origin/main` (4a08af9..a26653f — RTD follows main) and the
  tag (`v1.7.0` → 77a64eb — PyPI follows the tag).
- `publish.yml` OIDC run **27578609150 SUCCESS** (build + twine + publish-to-pypi
  with digital attestations).
- `gh release create v1.7.0` with `ketu-1.7.0-py3-none-any.whl` +
  `ketu-1.7.0.tar.gz` attached.

### Task 4 — Post-publish fresh-venv smoke FROM PyPI
- PyPI confirmed `1.7.0` is the latest release.
- `pip install ketu==1.7.0` into a throwaway virtualenv **run from a neutral cwd**
  (first attempt shadowed by the local repo's `ketu/` on sys.path — re-run from
  `/tmp` so import resolved to site-packages).
- Verified: `ketu.__file__` in site-packages; `__version__ == 1.7.0`;
  `find_spec("swisseph") is None`; orbs Rahu/Ketu/Lilith = 2; 3 node/Lilith
  aspects detected; Rahu-Ketu Opposition absent.

## Verification (must-haves)
- Local pre-flight green (pytest/coverage/mypy/doctest/doc-gates/build/twine/
  local smoke) ✓
- Blocking human go honoured before any irreversible action ✓
- Tag v1.7.0 created; origin/main + tag pushed; publish.yml OIDC SUCCESS ✓
- ketu==1.7.0 live on PyPI; post-publish PyPI smoke passes ✓
- GitHub release v1.7.0 with sdist+wheel ✓

## Deviations
- **Two pre-flight defects fixed inline** (both in ORB-04's spirit — docs must
  match the 2° orb): the stale `synastry_orb_limit` doctest / CLI orb=0 note
  (94828ac) and the broken `concepts.md#orbs` Sphinx xref from 39-01 (a26653f).
  Both were caught by gates (doctest; Sphinx build during the human checkpoint),
  not shipped.
- System `python -m venv` unusable (no ensurepip) → used `virtualenv` for both
  smoke venvs.
- Pre-existing, unrelated Sphinx warnings left as-is: `display_version` theme
  option, and the duplicate `equatorial-declination-new-in-v1-5` label (v1.5-era,
  present in both api.md and concepts.md before this phase).

## Links
- PyPI: ketu 1.7.0 (latest)
- GitHub release: https://github.com/alkimya/ketu/releases/tag/v1.7.0
- publish.yml run: 27578609150 (success)
