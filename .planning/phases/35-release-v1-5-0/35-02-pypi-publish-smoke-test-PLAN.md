---
phase: 35-release-v1-5-0
plan: 02
type: execute
wave: 2
depends_on: ["35-01"]
files_modified:
  - CHANGELOG.md
  - docs/source/changelog.md
  - fr/CHANGELOG.md
autonomous: false
user_setup:
  - service: pypi
    why: "PyPI OIDC trusted publishing target for ketu==1.5.0 (already configured from Phase 20 — verification only, no token needed)"
    dashboard_config:
      - task: "Confirm trusted publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi"
        location: "https://pypi.org/manage/project/ketu/settings/publishing/"

must_haves:
  truths:
    - "Local pre-flight passes ALL hard gates: clean tree on main, version synced to 1.5.0 in all THREE files (incl. conf.py), CHANGELOG [1.5.0] dated (no Unreleased), fr/CHANGELOG [1.5.0] dated, UPGRADING has v1.4 -> v1.5, docs/source/changelog.md [1.5.0] dated (no Unreleased), numpydoc + interrogate + full suite + mypy --strict CLEAN, build + twine check green"
    - "Local wheel contains ketu/data/chiron_coeffs.npz (verified via python -m zipfile -l) and is named ketu-1.5.0-py3-none-any.whl; sdist ships fr/CHANGELOG.md"
    - "Fresh-venv install of the LOCAL wheel passes the four v1.5 assertions: declination(2451545.0, 1) is a finite float in [-90, 90]; is_ascending_declination(2451545.0, 1) is a bool; is_out_of_bounds(2451545.0, 1) is a bool; `ketu --harmonics h7 aspects --date 2024-01-01` output contains 'H7-1'; plus all-subpackage imports and importlib.util.find_spec('swisseph') is None"
    - "A BLOCKING human go/no-go checkpoint is reached and approved BEFORE any tag push / PyPI publish"
    - "v1.5.0 git tag exists on main and is pushed; origin/main is ALSO pushed (RTD follows main); publish.yml runs on the tag and publishes ketu==1.5.0 to PyPI via OIDC"
    - "GitHub release v1.5.0 exists with sdist + wheel attached"
    - "Fresh-venv 'pip install ketu==1.5.0' FROM PyPI re-confirms the four v1.5 assertions + all-subpackage imports + no swisseph at runtime"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "[1.5.0] entry with the FINAL release date (re-confirmed/corrected here if 35-01 ran on a prior day)"
      contains: "## [1.5.0] - 20"
  key_links:
    - from: "git tag v1.5.0 on main"
      to: "publish.yml workflow"
      via: "on.push.tags: ['v*.*.*'] trigger"
      pattern: "v1\\.5\\.0"
    - from: "publish.yml OIDC job"
      to: "PyPI ketu project"
      via: "trusted publishing (id-token: write, environment: pypi)"
      pattern: "gh-action-pypi-publish"
    - from: "git push origin main"
      to: "ReadTheDocs v1.5 docs build"
      via: "RTD follows origin/main, not the tag (push BOTH)"
      pattern: "push origin main"
    - from: "from ketu.calculations import declination"
      to: "fresh-venv smoke assertion"
      via: "the four v1.5 functions are in ketu.calculations (NOT ketu.__all__)"
      pattern: "from ketu\\.calculations import declination"
---

<objective>
Run the v1.5.0 release ceremony: full local pre-flight (mypy --strict clean +
build + declination/harmonics-aware fresh-venv smoke on the LOCAL wheel), a
BLOCKING human go/no-go checkpoint (the next step pushes a tag that IRREVERSIBLY
publishes to PyPI), then tag + push tag + push origin/main + GitHub release, then
verify the published artifact installs from PyPI in a clean venv and satisfies all
four v1.5 assertions with NO pyswisseph at runtime.

Purpose: REL-03. Publishing to PyPI is permanent — a version number can never be
reused. Every gate must be green and a human must EXPLICITLY approve before the
tag is pushed (LOCKED constraint: feedback_validation_review_before_release — the
user personally reviews the whole milestone before release; auto-publish is NOT
acceptable). The v1.5 smoke test proves the additive surface: (a)
declination(2451545.0, 1) is a finite float in [-90, 90], (b)
is_ascending_declination(2451545.0, 1) is a bool, (c) is_out_of_bounds(2451545.0,
1) is a bool, (d) `ketu --harmonics h7 aspects --date 2024-01-01` emits "H7-1",
and the universal no-pyswisseph runtime check. BOTH the tag AND origin/main are
pushed (LOCKED constraint: feedback_push_main_not_just_tag_on_release — RTD
follows main, PyPI follows the tag; pushing only the tag freezes the docs).
Output: ketu==1.5.0 live on PyPI via OIDC, GitHub release v1.5.0 with sdist+wheel,
origin/main pushed, verified clean install + four v1.5 assertions + no-swisseph
from PyPI.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/35-release-v1-5-0/35-RESEARCH.md
@.github/workflows/publish.yml
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Date-stamp confirm and run the full declination+harmonics-aware local pre-flight (HARD GATES)</name>
  <files>CHANGELOG.md, docs/source/changelog.md, fr/CHANGELOG.md</files>
  <action>
    Assumes 35-01 is committed to main (version bumped in all THREE files incl.
    conf.py, CHANGELOG [1.5.0] date-stamped, fr/CHANGELOG [1.5.0] authored,
    docs/source/changelog.md date-stamped, UPGRADING v1.4 -> v1.5 added, README
    Roadmap updated). Run the v1.5.0 pre-flight from RESEARCH "Pre-flight Script
    (v1.5.0)", VERSION=1.5.0. Each step is a HARD GATE — STOP on the first
    failure and surface it; do NOT proceed to the checkpoint with any gate red.

    0. Date-stamp confirm: verify `## [1.5.0] - <date>` in CHANGELOG.md,
       docs/source/changelog.md, and fr/CHANGELOG.md all carry TODAY's UTC date.
       If 35-01 ran on a prior day and the date is now stale, update ALL THREE
       files to the real release date, then commit that change to main before
       tagging (the tag must point at a commit carrying the final date). The
       header must be a real date — NEVER "Unreleased".

    1. Clean tree on main:
       `test -z "$(git status --porcelain)"` AND
       `git branch --show-current` == `main`.
    2. Version sync in ALL THREE source-of-truth files (RESEARCH Pitfall 7 —
       conf.py is the easy-to-miss one):
       `grep -q 'version = "1.5.0"' pyproject.toml` and
       `grep -q '__version__ = "1.5.0"' ketu/__init__.py` and
       `grep -q 'release = "1.5.0"' docs/source/conf.py` and
       `grep -q 'version = "1.5.0"' docs/source/conf.py`;
       `pip install -e . -q && pytest tests/test_version.py -v`.
    3. CHANGELOG [1.5.0] dated, no placeholders:
       `grep -q '^## \[1.5.0\] - 20' CHANGELOG.md` AND
       `! grep -q '^## \[1.5.0\] - Unreleased' CHANGELOG.md` AND
       `! grep -q '^## \[Unreleased\]' CHANGELOG.md`.
    4. fr/CHANGELOG has dated [1.5.0] (RESEARCH Pitfall 8):
       `grep -q '^## \[1.5.0\] - 20' fr/CHANGELOG.md`.
    5. UPGRADING has the v1.4 -> v1.5 section (RESEARCH Pitfall 10):
       `grep -q 'v1\.4 -> v1\.5' UPGRADING.md`.
    6. docs/source/changelog.md [1.5.0] dated, Unreleased resolved
       (RESEARCH Pitfall 3):
       `! grep -q '^## \[1.5.0\] - Unreleased' docs/source/changelog.md` AND
       `grep -q '^## \[1.5.0\] - 20' docs/source/changelog.md`.
    7. Quality gates — ALL must pass before tag (mypy is ALREADY CLEAN for v1.5,
       unlike v1.4 — but re-confirm it as a hard gate anyway):
       `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` — zero violations;
       `python -m interrogate ketu/` — passes (>=95%);
       `pytest tests/ -q` — all pass (~1626 passed, 2 skipped);
       `python -m mypy --strict ketu/` — CLEAN (zero errors, 69 source files);
       `python -m pytest --doctest-modules ketu/ --no-cov --ignore=ketu/lunar_calendar.py --ignore=ketu/__main__.py` — passes.
    8. Build: `rm -rf dist build ketu.egg-info && python -m build --sdist --wheel`.
       Confirm pure-Python wheel name `dist/ketu-1.5.0-py3-none-any.whl` and
       `dist/ketu-1.5.0.tar.gz`.
    9. `pip install -q twine && python -m twine check dist/*` — PASSED.
   10. .npz ships in the wheel (~578 KB, presence is what matters):
       `python -m zipfile -l dist/ketu-1.5.0-py3-none-any.whl | grep 'ketu/data/chiron_coeffs.npz'`
       — MUST match.
   11. sdist ships fr/CHANGELOG.md:
       `tar -tzf dist/ketu-1.5.0.tar.gz | grep 'fr/CHANGELOG.md'`.
   12. Fresh-venv smoke test of the LOCAL WHEEL — the FOUR v1.5 assertions plus
       all-imports plus no-swisseph (RESEARCH "Fresh-Venv Smoke Test"). Install
       ONLY the wheel (no `.[test]` extras -> no pyswisseph, RESEARCH Pitfall 9).
       The four v1.5 functions are in `ketu.calculations`, NOT `ketu.__all__`
       (RESEARCH Pitfall 5); the CLI flag is TOP-LEVEL, not a subcommand flag
       (RESEARCH Pitfall 6):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q dist/ketu-1.5.0-py3-none-any.whl
       # version
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.5.0'==m.version('ketu')"
       # all subpackage imports (incl. v1.5 declination quartet + v1.4 generate_harmonic_aspects)
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import long; from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds; from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.cache import EphemerisCache; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('imports OK')"
       # v1.5 #1: declination(jd, body) -> finite float in [-90, 90]
       "$TMP/bin/python" -c "import math; from ketu.calculations import declination; d=float(declination(2451545.0,1)); assert math.isfinite(d) and -90.0<=d<=90.0, d; print(f'declination OK {d:.4f}')"
       # v1.5 #2: is_ascending_declination(jd, body) -> bool
       "$TMP/bin/python" -c "from ketu.calculations import is_ascending_declination; r=is_ascending_declination(2451545.0,1); assert isinstance(r,bool), type(r); print('is_ascending_declination OK', r)"
       # v1.5 #3: is_out_of_bounds(jd, body) -> bool
       "$TMP/bin/python" -c "from ketu.calculations import is_out_of_bounds; r=is_out_of_bounds(2451545.0,1); assert isinstance(r,bool), type(r); print('is_out_of_bounds OK', r)"
       # v1.5 #4: --harmonics h7 CLI (TOP-LEVEL flag) emits H7-1
       "$TMP/bin/python" -m ketu --harmonics h7 aspects --date 2024-01-01 | grep -q 'H7-1' || { echo 'FAIL: --harmonics h7 missing H7-1'; exit 1; }; echo '--harmonics h7 OK'
       # v1.4 preserved: generate_harmonic_aspects(7) -> 3 rows, H7 angles
       "$TMP/bin/python" -c "from ketu.aspects import generate_harmonic_aspects; h7=generate_harmonic_aspects(7); assert len(h7)==3; a=[float(x) for x in h7['angle']]; assert all(abs(x-e)<0.01 for x,e in zip(a,[360/7,720/7,1080/7])), a; print('H7 OK', [round(x,4) for x in a])"
       # v1.4 preserved: Chiron resolves at JD 2422324.5 (1920, 1900-2100 range active)
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2422324.5,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0, lon; print(f'Chiron 1920 OK {lon:.4f}')"
       # v1.5 #5 (universal): pyswisseph NOT importable (AGPL isolation)
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED'; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
   13. PyPI slot clear: query https://pypi.org/pypi/ketu/json and assert
       '1.5.0' not in releases (RESEARCH confirms the slot is currently free —
       re-check here just before publish).

    Report the full pre-flight result clearly (each gate PASS/FAIL). If ANY gate
    fails, STOP — do NOT advance to the checkpoint.
  </action>
  <verify>
    Every pre-flight gate PASSES; version synced to 1.5.0 in all THREE files
    (incl. conf.py); `python -m mypy --strict ketu/` is CLEAN;
    `dist/ketu-1.5.0-py3-none-any.whl` + `dist/ketu-1.5.0.tar.gz` exist and
    `twine check` is green; the wheel contains `ketu/data/chiron_coeffs.npz`;
    the fresh-venv local-wheel smoke passes the four v1.5 assertions
    (declination finite in [-90,90], is_ascending_declination bool,
    is_out_of_bounds bool, --harmonics h7 emits H7-1) plus all-imports, version,
    and no-swisseph; PyPI confirms 1.5.0 is not yet published; CHANGELOG +
    docs/source/changelog.md + fr/CHANGELOG carry today's real release date.
  </verify>
  <done>
    Release is build-verified locally: version synced to 1.5.0 across all three
    files, mypy --strict clean, all quality gates green, the .npz ships in the
    wheel, the wheel installs in a fresh venv and satisfies all four v1.5
    assertions (declination, is_ascending_declination, is_out_of_bounds,
    --harmonics h7) plus all-subpackage imports and no-swisseph, the PyPI 1.5.0
    slot is free, and all three changelogs carry the final date.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Human go/no-go before irreversible PyPI publish</name>
  <action>
    PAUSE for explicit human approval. Present the Task 1 pre-flight result and
    the trusted-publisher confirmation, then WAIT. Do NOT push the tag or
    origin/main until the user replies "approved". This is the LOCKED constraint
    feedback_validation_review_before_release — the user personally reviews the
    whole v1.5 milestone before release. See what-built / how-to-verify below.
  </action>
  <what-built>
    A fully pre-flighted v1.5.0 release candidate: version 1.5.0 synced in
    pyproject.toml + ketu/__init__.py + docs/source/conf.py (the conf.py bump is
    the Phase-32-inverted step so RTD renders 1.5.0); a single dated `[1.5.0]`
    CHANGELOG (EN root + RTD docs date-stamped from the pre-authored stubs,
    content byte-identical) listing Added (declination δ + declination_velocity +
    is_ascending_declination + is_out_of_bounds + body_decl + --harmonics h<N>),
    Changed (H{h}-{k} naming contract, find_aspect_timing dyn_coef=), Fixed (lunar
    node speed, duplicate-pair rows), and Notes (is_ascending β unchanged + Kala
    additive-dtype impact); a fresh dated French `[1.5.0]` section; UPGRADING
    `## v1.4 -> v1.5` (body_decl additive dtype, node-speed correction, additive
    API); a README Roadmap update; and a locally-built + twine-checked sdist+wheel
    whose wheel embeds `ketu/data/chiron_coeffs.npz` and which — in a fresh venv
    — yields a finite declination in [-90, 90], a bool is_ascending_declination, a
    bool is_out_of_bounds, emits "H7-1" from `ketu --harmonics h7 aspects --date
    2024-01-01`, imports every subpackage, and contains NO pyswisseph, plus a
    confirmed-free PyPI 1.5.0 slot. mypy --strict is CLEAN.
  </what-built>
  <how-to-verify>
    This is the point of no return. Pushing the tag triggers publish.yml which
    IRREVERSIBLY publishes ketu==1.5.0 to PyPI — a version number can never be
    reused or unpublished-and-replaced.

    Before approving, confirm:
    1. The pre-flight output from Task 1 shows EVERY gate PASSED — especially
       mypy --strict CLEAN, all THREE version files at 1.5.0 (incl. conf.py), and
       the four v1.5-specific smoke assertions: declination(2451545.0, 1) is a
       finite float in [-90, 90], is_ascending_declination(2451545.0, 1) is a
       bool, is_out_of_bounds(2451545.0, 1) is a bool, and
       `ketu --harmonics h7 aspects --date 2024-01-01` output contains "H7-1",
       plus find_spec('swisseph') is None (no pyswisseph at runtime).
    2. The PyPI trusted publisher is configured (one-time, external — should
       already exist from Phase 20): visit
       https://pypi.org/manage/project/ketu/settings/publishing/ and confirm
       Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi.
    3. You are publishing from `main` and the CHANGELOG date is correct.
    4. You have personally reviewed the entire v1.5 milestone (Phases 33 + 34 +
       35) and are ready to ship — this is the relecture-validation gate.

    Reply "approved" to push the v1.5.0 tag, push origin/main, and publish.
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
       `git tag -a v1.5.0 -m "Release 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI"`
    2. Push the tag: `git push origin v1.5.0`. This triggers publish.yml (build
       job -> publish-to-pypi job via OIDC). publish.yml needs NO changes — it is
       already tag-triggered (`v*.*.*`) and Node-24/OIDC from Phase 20.
    3. Push origin/main: `git push origin main`. This is a FIRST-CLASS,
       NON-OPTIONAL step (LOCKED constraint
       feedback_push_main_not_just_tag_on_release, RESEARCH Pitfall 4). RTD
       follows main, NOT the tag — pushing only the tag freezes the docs at v1.4
       content even though PyPI has v1.5.0. Do BOTH pushes.
    4. Watch the workflow to completion:
       `gh run watch $(gh run list --workflow=publish.yml --limit 1 --json databaseId -q '.[0].databaseId')`
       (or `gh run list --workflow=publish.yml` then `gh run watch <id>`). It
       MUST finish SUCCESS. If it fails, capture logs (`gh run view <id>
       --log-failed`) and surface — do NOT re-tag the same version (the slot may
       be partially consumed); diagnose first.
    5. Create the GitHub release attaching the locally-built artifacts (so sdist
       + wheel are on the release page per REL-03). Use the EXACT release body
       and command from RESEARCH "GitHub Release Body (v1.5.0)":
       ```
       gh release create v1.5.0 \
         --title "Ketu 1.5.0 — Lunar Declination δ + Dynamic Harmonics CLI" \
         --notes "$(cat <<'EOF'
       Ketu v1.5.0 adds equatorial declination δ helpers and the dynamic harmonics CLI
       surface. All additions are purely additive — no breaking changes. The `is_ascending`
       (β-trajectory) function and the frozen `core.aspects` table are byte-identical to v1.4.

       **New in v1.5.0:**
       - `declination(jdate, body)` — equatorial declination δ in degrees [−90, +90], scalar and vectorized.
       - `declination_velocity(jdate, body)` — dδ/dt in degrees/day (northward positive).
       - `is_ascending_declination(jdate, body)` — True when dδ/dt > 0 (Moon montante). Distinct from `is_ascending` (β-trajectory, unchanged).
       - `is_out_of_bounds(jdate, body)` — True when |δ| exceeds instantaneous obliquity ε(jd).
       - `CHART_DTYPE` gains `body_decl` (`float64[14]`) — declination δ for all 14 bodies (additive).
       - `--harmonics h<N>` CLI top-level flag (e.g. `ketu --harmonics h7 aspects --date …`).

       **Changed in v1.5.0:**
       - `H{h}-{k}` dynamic-aspect naming is a stable public API contract (pinned by tests).
       - `find_aspect_timing` gains `dyn_coef=` optional parameter for harmonic orb derivation.

       **Fixed in v1.5.0:**
       - Lunar node mean speed corrected (−0.013 → −0.052954 °/day, matching the true 18.6-year regression).
       - `calculate_aspects_batch` duplicate-pair rows eliminated (exactly one row per pair, static-first/dynamic-second).

       **Migration (see UPGRADING.md → v1.4 → v1.5):**
       - `CHART_DTYPE.body_decl` is additive — named field access unchanged; positional/`.view()` must adapt.
       - `core.bodies['speed'][10]` and `[11]` (Rahu/Ketu) hold the corrected nodal speed.
       - All new API surface is purely additive.

       - 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
       - 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v14---v15)
       - 📦 `pip install ketu==1.5.0`

       1626 tests, mypy --strict, 100% coverage.
       EOF
       )" \
         dist/ketu-1.5.0-py3-none-any.whl dist/ketu-1.5.0.tar.gz
       ```
    6. POST-PUBLISH verification — fresh venv installing FROM PyPI (may need a
       short retry loop while PyPI's CDN propagates). Re-run the four v1.5
       assertions against the PUBLISHED artifact (use the ketu.calculations
       import path — Pitfall 5 — and the top-level CLI flag — Pitfall 6):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q "ketu==1.5.0"
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.5.0'==m.version('ketu')"
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import declination, declination_velocity, is_ascending_declination, is_out_of_bounds; from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('subpackages OK')"
       "$TMP/bin/python" -c "import math; from ketu.calculations import declination; d=float(declination(2451545.0,1)); assert math.isfinite(d) and -90.0<=d<=90.0, d; print(f'declination OK {d:.4f}')"
       "$TMP/bin/python" -c "from ketu.calculations import is_ascending_declination; r=is_ascending_declination(2451545.0,1); assert isinstance(r,bool); print('is_ascending_declination OK', r)"
       "$TMP/bin/python" -c "from ketu.calculations import is_out_of_bounds; r=is_out_of_bounds(2451545.0,1); assert isinstance(r,bool); print('is_out_of_bounds OK', r)"
       "$TMP/bin/python" -m ketu --harmonics h7 aspects --date 2024-01-01 | grep -q 'H7-1' || { echo 'FAIL: --harmonics h7 missing H7-1'; exit 1; }; echo '--harmonics h7 OK'
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
    7. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.

    Report: PyPI URL, GitHub release URL, confirmation that BOTH the tag AND
    origin/main were pushed, and the post-publish smoke result (version +
    declination + is_ascending_declination + is_out_of_bounds + --harmonics h7 +
    no-swisseph).
  </action>
  <verify>
    `git tag -l v1.5.0` shows the tag; `git rev-parse origin/main` matches local
    main (origin/main pushed); `gh run list --workflow=publish.yml` latest run =
    SUCCESS; `gh release view v1.5.0` lists both `ketu-1.5.0-py3-none-any.whl`
    and `ketu-1.5.0.tar.gz` assets; PyPI JSON API includes 1.5.0; the fresh-venv
    `pip install ketu==1.5.0` from PyPI passes all four v1.5 assertions
    (version == metadata == "1.5.0"; declination finite in [-90,90];
    is_ascending_declination bool; is_out_of_bounds bool; --harmonics h7 emits
    H7-1) plus all-imports and `find_spec('swisseph') is None`.
  </verify>
  <done>
    v1.5.0 tagged on main and pushed; origin/main ALSO pushed (RTD will rebuild
    v1.5 docs); publish.yml succeeded; ketu==1.5.0 is live on PyPI; GitHub
    release v1.5.0 has sdist + wheel attached; fresh-venv install FROM PyPI
    yields a finite declination in [-90,90], a bool is_ascending_declination, a
    bool is_out_of_bounds, emits "H7-1" from `--harmonics h7`, imports all
    subpackages, and confirms no pyswisseph at runtime.
  </done>
</task>

</tasks>

<verification>
- Pre-flight all-green before any irreversible action (Task 1), including version synced in all THREE files (incl. conf.py), mypy --strict CLEAN, .npz-in-wheel, and the four v1.5 smoke assertions (declination, is_ascending_declination, is_out_of_bounds, --harmonics h7) plus no-swisseph.
- BLOCKING human approval recorded before tag push (checkpoint).
- `git tag -l v1.5.0` present and pushed; origin/main ALSO pushed (`git rev-parse origin/main` == local main).
- `gh run list --workflow=publish.yml` latest run = SUCCESS.
- `gh release view v1.5.0` shows sdist + wheel assets.
- PyPI: `pip install ketu==1.5.0` in a clean venv -> import OK, `ketu.__version__ == importlib.metadata.version("ketu") == "1.5.0"`, all subpackages import, declination(2451545.0, 1) finite in [-90,90], is_ascending_declination(2451545.0, 1) bool, is_out_of_bounds(2451545.0, 1) bool, `ketu --harmonics h7 aspects --date 2024-01-01` emits H7-1, `find_spec('swisseph') is None`.
</verification>

<success_criteria>
REL-03 satisfied: ketu==1.5.0 published to PyPI via OIDC trusted publishing
(Success Criterion 3); GitHub release v1.5.0 attaches sdist + wheel; BOTH the
v1.5.0 tag AND origin/main are pushed (RTD follows main, PyPI follows tag —
Success Criterion 3); a fresh-venv `pip install ketu==1.5.0` smoke confirms the
v1.5 surface — declination, montant/descendant (is_ascending_declination), OOB
(is_out_of_bounds), --harmonics h7 — with all-subpackage imports and NO
pyswisseph at runtime (Success Criterion 4). No irreversible action taken without
the explicit human go/no-go (LOCKED relecture-validation gate).
</success_criteria>

<output>
After completion, create
`.planning/phases/35-release-v1-5-0/35-02-SUMMARY.md`
</output>
