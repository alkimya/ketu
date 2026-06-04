---
phase: 37-documentation-release-v1-6-0
plan: 03
type: execute
wave: 2
depends_on: ["37-01", "37-02"]
files_modified:
  - CHANGELOG.md
  - docs/source/changelog.md
  - fr/CHANGELOG.md
autonomous: false
user_setup:
  - service: pypi
    why: "PyPI OIDC trusted publishing target for ketu==1.6.0 (already configured from Phase 20 — verification only, no token needed)"
    dashboard_config:
      - task: "Confirm trusted publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi"
        location: "https://pypi.org/manage/project/ketu/settings/publishing/"

must_haves:
  truths:
    - "Local pre-flight passes ALL hard gates: clean tree on main, version synced to 1.6.0 in all THREE files (incl. conf.py), CHANGELOG [1.6.0] dated (no Unreleased), fr/CHANGELOG [1.6.0] dated, UPGRADING has v1.5 -> v1.6, docs/source/changelog.md [1.6.0] dated, the new declination-aspects docs present in concepts.md + api.md, the FR concepts.po/api.po new strings translated (make html-fr builds), numpydoc + interrogate + full suite + mypy --strict CLEAN, build + twine check green"
    - "Local wheel contains ketu/data/chiron_coeffs.npz (verified via python -m zipfile -l) and is named ketu-1.6.0-py3-none-any.whl; sdist ships fr/CHANGELOG.md"
    - "Fresh-venv install of the LOCAL wheel passes the v1.6 declination-aspects assertion: `from ketu.declination import find_declination_aspects, DECLA_ASPECT_DTYPE`; a body_decl with Sun δ=+20.0 and Moon δ=+20.5 (same hemisphere, gap 0.5° ≤ 1.0° orb) yields a result whose dtype == DECLA_ASPECT_DTYPE and (res['kind']=='P').sum() >= 1; plus all-subpackage imports INCLUDING ketu.declination, version==1.6.0==metadata, and importlib.util.find_spec('swisseph') is None"
    - "A BLOCKING human go/no-go checkpoint is reached and approved BEFORE any tag push / PyPI publish (LOCKED: feedback_validation_review_before_release)"
    - "v1.6.0 git tag exists on main and is pushed; origin/main is ALSO pushed (RTD follows main — LOCKED: feedback_push_main_not_just_tag_on_release); publish.yml runs on the tag and publishes ketu==1.6.0 to PyPI via OIDC"
    - "GitHub release v1.6.0 exists with sdist + wheel attached"
    - "Fresh-venv 'pip install ketu==1.6.0' FROM PyPI re-confirms the v1.6 declination-aspects assertion + all-subpackage imports + no swisseph at runtime"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "[1.6.0] entry with the FINAL release date (re-confirmed/corrected here if 37-02 ran on a prior day)"
      contains: "## [1.6.0] - 20"
  key_links:
    - from: "git tag v1.6.0 on main"
      to: "publish.yml workflow"
      via: "on.push.tags: ['v*.*.*'] trigger"
      pattern: "v1\\.6\\.0"
    - from: "publish.yml OIDC job"
      to: "PyPI ketu project"
      via: "trusted publishing (id-token: write, environment: pypi)"
      pattern: "gh-action-pypi-publish"
    - from: "git push origin main"
      to: "ReadTheDocs v1.6 docs build"
      via: "RTD follows origin/main, not the tag (push BOTH)"
      pattern: "push origin main"
    - from: "from ketu.declination import find_declination_aspects"
      to: "fresh-venv smoke assertion"
      via: "the v1.6 detector is in ketu.declination (NOT ketu.__all__)"
      pattern: "from ketu\\.declination import find_declination_aspects"
---

<objective>
Run the v1.6.0 release ceremony: full local pre-flight (mypy --strict clean +
build + declination-aspects-aware fresh-venv smoke on the LOCAL wheel + the new
FR docs build), a BLOCKING human go/no-go checkpoint (the next step pushes a tag
that IRREVERSIBLY publishes to PyPI), then tag + push tag + push origin/main +
GitHub release, then verify the published artifact installs from PyPI in a clean
venv and detects a declination parallel with NO pyswisseph at runtime.

Purpose: publishing to PyPI is permanent — a version number can never be reused.
Every gate must be green and a human must EXPLICITLY approve before the tag is
pushed (LOCKED constraint feedback_validation_review_before_release — the user
personally reviews the whole v1.6 milestone before release; auto-publish is NOT
acceptable). The v1.6 smoke test proves the additive declination-aspects surface:
`find_declination_aspects` on a Sun/Moon same-hemisphere body_decl detects at
least one parallel (`kind == 'P'`), the result dtype matches `DECLA_ASPECT_DTYPE`,
and the universal no-pyswisseph runtime check holds. BOTH the tag AND origin/main
are pushed (LOCKED constraint feedback_push_main_not_just_tag_on_release — RTD
follows main, PyPI follows the tag; pushing only the tag freezes the docs at v1.5
even though PyPI has v1.6.0).
Output: ketu==1.6.0 live on PyPI via OIDC, GitHub release v1.6.0 with sdist+wheel,
origin/main pushed, verified clean install + declination-aspects parallel
detection + no-swisseph from PyPI.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/DECLINATION_ASPECTS.md
@.github/workflows/publish.yml
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
@ketu/declination/__init__.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Date-stamp confirm and run the full declination-aspects-aware local pre-flight (HARD GATES)</name>
  <files>CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md</files>
  <action>
    Assumes 37-01 (feature docs en+fr) AND 37-02 (version bump + changelogs +
    UPGRADING + README) are committed to main. Run the v1.6.0 pre-flight. Each step
    is a HARD GATE — STOP on the first failure and surface it; do NOT proceed to
    the checkpoint with any gate red. VERSION=1.6.0.

    0. Date-stamp confirm: verify `## [1.6.0] - <date>` in CHANGELOG.md,
       docs/source/changelog.md, and fr/CHANGELOG.md all carry TODAY's UTC date.
       If 37-02 ran on a prior day and the date is now stale, update ALL THREE
       files to the real release date, then commit that change to main before
       tagging (the tag must point at a commit carrying the final date). The header
       must be a real date — NEVER "Unreleased".

    1. Clean tree on main:
       `test -z "$(git status --porcelain)"` AND
       `git branch --show-current` == `main`.
    2. Version sync in ALL THREE source-of-truth files (conf.py is the
       easy-to-miss one):
       `grep -q 'version = "1.6.0"' pyproject.toml` and
       `grep -q '__version__ = "1.6.0"' ketu/__init__.py` and
       `grep -q 'release = "1.6.0"' docs/source/conf.py` and
       `grep -q 'version = "1.6.0"' docs/source/conf.py`;
       `pip install -e . -q && pytest tests/test_version.py -v`.
    3. CHANGELOG [1.6.0] dated, no placeholders:
       `grep -q '^## \[1.6.0\] - 20' CHANGELOG.md` AND
       `! grep -q '^## \[1.6.0\] - Unreleased' CHANGELOG.md` AND
       `! grep -q '^## \[Unreleased\]' CHANGELOG.md`.
    4. fr/CHANGELOG has dated [1.6.0]:
       `grep -q '^## \[1.6.0\] - 20' fr/CHANGELOG.md`.
    5. UPGRADING has the v1.5 -> v1.6 section:
       `grep -q 'v1\.5 -> v1\.6' UPGRADING.md`.
    6. docs/source/changelog.md [1.6.0] dated, Unreleased resolved:
       `! grep -q '^## \[1.6.0\] - Unreleased' docs/source/changelog.md` AND
       `grep -q '^## \[1.6.0\] - 20' docs/source/changelog.md`.
    7. v1.6 FEATURE DOCS present (DECLA-05, from 37-01):
       `grep -q '^## Declination Aspects' docs/source/concepts.md` AND
       `grep -q 'find_declination_aspects' docs/source/api.md` AND
       `grep -q 'contre-parallèle' docs/locale/fr/LC_MESSAGES/concepts.po` (FR
       translated). Then build the French docs to confirm the .mo recompiles and
       the new strings render in French (no English fallback):
       `make -C docs html-fr` succeeds AND
       `grep -rq 'contre-parallèle' docs/build/html-fr/` matches; then
       `make -C docs clean` (do not commit build artifacts).
    8. Quality gates — ALL must pass before tag (mypy is ALREADY CLEAN for v1.6 —
       docs/metadata-only release — but re-confirm it as a hard gate):
       `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` — zero violations;
       `python -m interrogate ketu/` — passes (>=95%);
       `pytest tests/ -q` — all pass (~1654 passed, 2 skipped — VERIFY the live count at execute time; it was 1654 on 2026-06-04);
       `python -m mypy --strict ketu/` — CLEAN (zero errors);
       `python -m pytest --doctest-modules ketu/ --no-cov --ignore=ketu/lunar_calendar.py --ignore=ketu/__main__.py` — passes.
    9. Build: `rm -rf dist build ketu.egg-info && python -m build --sdist --wheel`.
       Confirm pure-Python wheel name `dist/ketu-1.6.0-py3-none-any.whl` and
       `dist/ketu-1.6.0.tar.gz`.
   10. `pip install -q twine && python -m twine check dist/*` — PASSED.
   11. .npz ships in the wheel (~578 KB, presence is what matters):
       `python -m zipfile -l dist/ketu-1.6.0-py3-none-any.whl | grep 'ketu/data/chiron_coeffs.npz'`
       — MUST match.
   12. sdist ships fr/CHANGELOG.md:
       `tar -tzf dist/ketu-1.6.0.tar.gz | grep 'fr/CHANGELOG.md'`.
   13. Fresh-venv smoke test of the LOCAL WHEEL — the v1.6 declination-aspects
       assertion plus all-imports plus no-swisseph. Install ONLY the wheel (no
       `.[test]` extras -> no pyswisseph). The detector is in `ketu.declination`,
       NOT `ketu.__all__`. The chosen body_decl vector deterministically yields one
       parallel: Sun (index 0) δ=+20.0° and Moon (index 1) δ=+20.5° are on the SAME
       hemisphere with a 0.5° gap, and the Sun/Moon orb is exactly 1.0° (both have
       natal orb 12° → mean 12° × 1/12 = 1.0°), so 0.5° ≤ 1.0° → exactly one `P`
       row `(0, 1, 'P', 0.5, 1.0)`. All other bodies are at δ=0 (sign 0 → form no
       aspect), so the result is exactly that single parallel. (Verified live on
       2026-06-04: `find_declination_aspects` returns `[(0, 1, 'P', 0.5, 1.0)]`.)
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q dist/ketu-1.6.0-py3-none-any.whl
       # version
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.6.0'==m.version('ketu')"
       # all subpackage imports (incl. the NEW ketu.declination surface)
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds; from ketu.declination import find_declination_aspects, declination_aspect_masks, DeclinationAspectMasks, DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB; from ketu.aspects import calculate_aspects, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.cache import EphemerisCache; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('imports OK')"
       # v1.6 #1: find_declination_aspects detects >=1 parallel (Sun/Moon same hemisphere within 1.0° orb)
       "$TMP/bin/python" -c "import numpy as np; from ketu.declination import find_declination_aspects, DECLA_ASPECT_DTYPE; d=np.zeros(14); d[0]=20.0; d[1]=20.5; res=find_declination_aspects(d); assert res.dtype==DECLA_ASPECT_DTYPE, res.dtype; assert int((res['kind']=='P').sum())>=1, res; print('declination parallel OK', res.tolist())"
       # v1.6 #2: empty-result contract — all bodies at δ=0 → no aspects, never None
       "$TMP/bin/python" -c "import numpy as np; from ketu.declination import find_declination_aspects, DECLA_ASPECT_DTYPE; r=find_declination_aspects(np.zeros(14)); assert r.dtype==DECLA_ASPECT_DTYPE and len(r)==0; print('empty-result OK')"
       # v1.6 #3 (universal): pyswisseph NOT importable (AGPL isolation)
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED'; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
   14. PyPI slot clear: query https://pypi.org/pypi/ketu/json and assert
       '1.6.0' not in releases (re-check just before publish).

    Report the full pre-flight result clearly (each gate PASS/FAIL). If ANY gate
    fails, STOP — do NOT advance to the checkpoint.
  </action>
  <verify>
    Every pre-flight gate PASSES; version synced to 1.6.0 in all THREE files (incl.
    conf.py); the new declination-aspects docs present (concepts.md + api.md) and
    FR translated (make html-fr builds, renders « contre-parallèle »);
    `python -m mypy --strict ketu/` is CLEAN;
    `dist/ketu-1.6.0-py3-none-any.whl` + `dist/ketu-1.6.0.tar.gz` exist and
    `twine check` is green; the wheel contains `ketu/data/chiron_coeffs.npz`; the
    fresh-venv local-wheel smoke passes the v1.6 assertion (dtype == DECLA_ASPECT_DTYPE
    and (kind=='P').sum() >= 1) plus all-imports (incl. ketu.declination), version,
    and no-swisseph; PyPI confirms 1.6.0 is not yet published; all three changelogs
    carry today's real release date.
  </verify>
  <done>
    Release is build-verified locally: version synced to 1.6.0 across all three
    files, the v1.6 feature docs (en+fr) are present and the FR .mo recompiles,
    mypy --strict clean, all quality gates green, the .npz ships in the wheel, the
    wheel installs in a fresh venv and detects a declination parallel via
    find_declination_aspects (>=1 'P' row, dtype == DECLA_ASPECT_DTYPE) plus
    all-subpackage imports and no-swisseph, the PyPI 1.6.0 slot is free, and all
    three changelogs carry the final date.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Human go/no-go before irreversible PyPI publish</name>
  <action>
    PAUSE for explicit human approval. Present the Task 1 pre-flight result and the
    trusted-publisher confirmation, then WAIT. Do NOT push the tag or origin/main
    until the user replies "approved". This is the LOCKED constraint
    feedback_validation_review_before_release — the user personally reviews the
    whole v1.6 milestone before release. See what-built / how-to-verify below.
  </action>
  <what-built>
    A fully pre-flighted v1.6.0 release candidate: version 1.6.0 synced in
    pyproject.toml + ketu/__init__.py + docs/source/conf.py (the conf.py bump
    prevents stale 1.5.0 RTD branding); a single dated `[1.6.0]` CHANGELOG (EN root
    + RTD docs, content matched) listing the new `ketu.declination` subpackage
    (find_declination_aspects + declination_aspect_masks + DeclinationAspectMasks +
    DECLA_ASPECT_DTYPE + DECLA_COEF + MIN_DECL_ORB) and Notes (CHART_DTYPE unchanged
    / additive / core.aspects byte-identical); a fresh dated French `[1.6.0]`
    section; UPGRADING `## v1.5 -> v1.6` (purely additive, no ratchet break); a
    README Roadmap update; the NEW v1.6 feature documentation (concepts.md +
    api.md, EN) with its French translation (.po updated, .mo recompile verified
    via `make html-fr` rendering « contre-parallèle »); and a locally-built +
    twine-checked sdist+wheel whose wheel embeds `ketu/data/chiron_coeffs.npz` and
    which — in a fresh venv — detects a Sun/Moon parallel via
    find_declination_aspects (>=1 'P' row, dtype == DECLA_ASPECT_DTYPE), imports
    every subpackage including ketu.declination, and contains NO pyswisseph, plus a
    confirmed-free PyPI 1.6.0 slot. mypy --strict is CLEAN.
  </what-built>
  <how-to-verify>
    This is the point of no return. Pushing the tag triggers publish.yml which
    IRREVERSIBLY publishes ketu==1.6.0 to PyPI — a version number can never be
    reused or unpublished-and-replaced.

    Before approving, confirm:
    1. The pre-flight output from Task 1 shows EVERY gate PASSED — especially mypy
       --strict CLEAN, all THREE version files at 1.6.0 (incl. conf.py), the new
       declination-aspects docs (en concepts.md + api.md) present and FR translated
       (make html-fr renders « contre-parallèle »), and the v1.6 smoke assertion:
       `from ketu.declination import find_declination_aspects, DECLA_ASPECT_DTYPE`,
       a Sun/Moon same-hemisphere body_decl yields a result with dtype ==
       DECLA_ASPECT_DTYPE and at least one `kind == 'P'` row, plus
       find_spec('swisseph') is None (no pyswisseph at runtime).
    2. The PyPI trusted publisher is configured (one-time, external — should
       already exist from Phase 20): visit
       https://pypi.org/manage/project/ketu/settings/publishing/ and confirm
       Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi.
    3. You are publishing from `main` and the CHANGELOG date is correct.
    4. You have personally reviewed the entire v1.6 milestone (Phase 36 detection
       core + Phase 37 docs/release) and are ready to ship — this is the
       relecture-validation gate.

    Reply "approved" to push the v1.6.0 tag, push origin/main, and publish.
    Reply with any concern to halt — nothing irreversible has happened yet.
  </how-to-verify>
  <resume-signal>Type "approved" to tag + push tag + push origin/main + publish, or describe what to fix.</resume-signal>
</task>

<task type="auto">
  <name>Task 2: Tag, push tag AND origin/main, create the GitHub release, and verify the PyPI install</name>
  <files></files>
  <action>
    Only after the human approves the checkpoint.

    1. Tag on main:
       `git tag -a v1.6.0 -m "Release 1.6.0 — Declination Aspects (parallels & contra-parallels)"`
    2. Push the tag: `git push origin v1.6.0`. This triggers publish.yml (build job
       -> publish-to-pypi job via OIDC). publish.yml needs NO changes — it is
       already tag-triggered (`v*.*.*`) and OIDC from Phase 20.
    3. Push origin/main: `git push origin main`. This is a FIRST-CLASS, NON-OPTIONAL
       step (LOCKED constraint feedback_push_main_not_just_tag_on_release). RTD
       follows main, NOT the tag — pushing only the tag freezes the docs at v1.5
       content even though PyPI has v1.6.0. Do BOTH pushes.
    4. Watch the workflow to completion:
       `gh run watch $(gh run list --workflow=publish.yml --limit 1 --json databaseId -q '.[0].databaseId')`
       (or `gh run list --workflow=publish.yml` then `gh run watch <id>`). It MUST
       finish SUCCESS. If it fails, capture logs (`gh run view <id> --log-failed`)
       and surface — do NOT re-tag the same version (the slot may be partially
       consumed); diagnose first.
    5. Create the GitHub release attaching the locally-built artifacts (so sdist +
       wheel are on the release page). Use this release body:
       ```
       gh release create v1.6.0 \
         --title "Ketu 1.6.0 — Declination Aspects (parallels & contra-parallels)" \
         --notes "$(cat <<'EOF'
       Ketu v1.6.0 adds the `ketu.declination` subpackage — detection of parallel and
       contra-parallel aspects on the equatorial declination axis (δ), independent of
       ecliptic longitude. All additions are purely additive — no breaking changes.
       `CHART_DTYPE` is byte-identical to v1.5 (no ratchet break) and the frozen
       `core.aspects` table is unchanged.

       **New in v1.6.0 (`ketu.declination`):**
       - `find_declination_aspects(body_decl)` — scalar/single-chart detector over the `(14,)` `chart["body_decl"]` array; returns a `DECLA_ASPECT_DTYPE` structured array (upper-triangle pairs, sorted, deduplicated); `np.empty(0, …)` when none (never `None`).
       - `declination_aspect_masks(body_decl)` — vectorized batch path, `(S, 14)` or `(14,)` → `DeclinationAspectMasks` NamedTuple of `(S, 91)` masks + `(91,)` index/orb vectors (pure broadcasting).
       - `DeclinationAspectMasks` NamedTuple (parallel, contra, gap, idx_i, idx_j, orb_pairs).
       - `DECLA_ASPECT_DTYPE` (body1, body2, kind ∈ {P, CP}, gap, orb).
       - `DECLA_COEF = 1/12`, `MIN_DECL_ORB = 0.5°` — orb formula `max((orb_b1+orb_b2)/2 × DECLA_COEF, MIN_DECL_ORB)` → Sun/Moon = 1.0°, zero-orb bodies floored to 0.5°.

       **Definitions:**
       - Parallel (`P`): `sign(δ₁) == sign(δ₂) ≠ 0` and `|δ₁ − δ₂| ≤ orb` (same hemisphere). ≈ conjunction by declination.
       - Contra-parallel (`CP`): opposite signs and `|δ₁ + δ₂| ≤ orb`. ≈ opposition by declination.
       - Parallel ≠ longitude conjunction — δ and ecliptic longitude are independent measurements.

       **Migration (see UPGRADING.md → v1.5 → v1.6):**
       - Purely additive. `ketu.declination` names are reachable via `ketu.declination.*` only (`ketu.__all__` unchanged).
       - `CHART_DTYPE` is UNCHANGED — no ratchet break.

       - 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
       - 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v15---v16)
       - 📦 `pip install ketu==1.6.0`

       mypy --strict, 100% coverage.
       EOF
       )" \
         dist/ketu-1.6.0-py3-none-any.whl dist/ketu-1.6.0.tar.gz
       ```
    6. POST-PUBLISH verification — fresh venv installing FROM PyPI (may need a short
       retry loop while PyPI's CDN propagates). Re-run the v1.6 assertion against
       the PUBLISHED artifact (ketu.declination import path; the deterministic
       Sun/Moon parallel vector):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q "ketu==1.6.0"
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.6.0'==m.version('ketu')"
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import declination, is_out_of_bounds; from ketu.declination import find_declination_aspects, declination_aspect_masks, DeclinationAspectMasks, DECLA_ASPECT_DTYPE, DECLA_COEF, MIN_DECL_ORB; from ketu.aspects import calculate_aspects, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('subpackages OK')"
       "$TMP/bin/python" -c "import numpy as np; from ketu.declination import find_declination_aspects, DECLA_ASPECT_DTYPE; d=np.zeros(14); d[0]=20.0; d[1]=20.5; res=find_declination_aspects(d); assert res.dtype==DECLA_ASPECT_DTYPE; assert int((res['kind']=='P').sum())>=1, res; print('declination parallel OK', res.tolist())"
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
    7. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.

    Report: PyPI URL, GitHub release URL, confirmation that BOTH the tag AND
    origin/main were pushed, and the post-publish smoke result (version +
    declination parallel detection + no-swisseph).
  </action>
  <verify>
    `git tag -l v1.6.0` shows the tag; `git rev-parse origin/main` matches local
    main (origin/main pushed); `gh run list --workflow=publish.yml` latest run =
    SUCCESS; `gh release view v1.6.0` lists both `ketu-1.6.0-py3-none-any.whl` and
    `ketu-1.6.0.tar.gz` assets; PyPI JSON API includes 1.6.0; the fresh-venv
    `pip install ketu==1.6.0` from PyPI passes the v1.6 assertion (version ==
    metadata == "1.6.0"; find_declination_aspects on the Sun/Moon vector yields a
    DECLA_ASPECT_DTYPE result with >=1 'P' row) plus all-imports (incl.
    ketu.declination) and `find_spec('swisseph') is None`.
  </verify>
  <done>
    v1.6.0 tagged on main and pushed; origin/main ALSO pushed (RTD will rebuild
    v1.6 docs); publish.yml succeeded; ketu==1.6.0 is live on PyPI; GitHub release
    v1.6.0 has sdist + wheel attached; fresh-venv install FROM PyPI detects a
    declination parallel via find_declination_aspects (>=1 'P' row, dtype ==
    DECLA_ASPECT_DTYPE), imports all subpackages including ketu.declination, and
    confirms no pyswisseph at runtime.
  </done>
</task>

</tasks>

<verification>
- Pre-flight all-green before any irreversible action (Task 1), including version synced in all THREE files (incl. conf.py), the new v1.6 feature docs en+fr present (make html-fr renders « contre-parallèle »), mypy --strict CLEAN, .npz-in-wheel, and the v1.6 declination-aspects smoke assertion plus no-swisseph.
- BLOCKING human approval recorded before tag push (checkpoint).
- `git tag -l v1.6.0` present and pushed; origin/main ALSO pushed (`git rev-parse origin/main` == local main).
- `gh run list --workflow=publish.yml` latest run = SUCCESS.
- `gh release view v1.6.0` shows sdist + wheel assets.
- PyPI: `pip install ketu==1.6.0` in a clean venv -> import OK, `ketu.__version__ == importlib.metadata.version("ketu") == "1.6.0"`, all subpackages import (incl. ketu.declination), `find_declination_aspects` on the Sun/Moon (+20.0/+20.5) vector yields a `DECLA_ASPECT_DTYPE` result with >=1 `kind=='P'` row, `find_spec('swisseph') is None`.
</verification>

<success_criteria>
ketu==1.6.0 published to PyPI via OIDC trusted publishing; GitHub release v1.6.0
attaches sdist + wheel; BOTH the v1.6.0 tag AND origin/main are pushed (RTD follows
main, PyPI follows tag); a fresh-venv `pip install ketu==1.6.0` smoke confirms the
v1.6 surface — find_declination_aspects detects at least one parallel on a Sun/Moon
same-hemisphere body_decl, result dtype == DECLA_ASPECT_DTYPE — with all-subpackage
imports (incl. ketu.declination) and NO pyswisseph at runtime. No irreversible
action taken without the explicit human go/no-go (LOCKED relecture-validation gate).
</success_criteria>

<output>
After completion, create
`.planning/phases/37-documentation-release-v1-6-0/37-03-SUMMARY.md`
</output>
</content>
</invoke>
