---
phase: 32-release-v1-4-0
plan: 02
type: execute
wave: 2
depends_on: ["32-01"]
files_modified:
  - CHANGELOG.md
  - fr/CHANGELOG.md
autonomous: false
user_setup:
  - service: pypi
    why: "PyPI OIDC trusted publishing target for ketu==1.4.0 (already configured from Phase 20 — verification only, no token needed)"
    dashboard_config:
      - task: "Confirm trusted publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi"
        location: "https://pypi.org/manage/project/ketu/settings/publishing/"

must_haves:
  truths:
    - "Local pre-flight passes ALL hard gates: clean tree on main, version synced to 1.4.0, CHANGELOG [1.4.0] dated (no Unreleased / no XX), fr/CHANGELOG [1.4.0] dated, UPGRADING has v1.3 -> v1.4, docs/source/changelog.md XX placeholders resolved, numpydoc + interrogate + full suite + mypy --strict CLEAN, build + twine check green"
    - "Local wheel contains ketu/data/chiron_coeffs.npz (verified via python -m zipfile -l) and is named ketu-1.4.0-py3-none-any.whl"
    - "Fresh-venv install of the LOCAL wheel: generate_harmonic_aspects(7) returns 3 rows with H7 angles ~[51.4286,102.8571,154.2857]; core.bodies['orb'] for Chiron == 4.0; calc_planet_position(2422324.5, 13) (1920, outside old 1950-2050) is finite in [0,360); all subpackages import; importlib.util.find_spec('swisseph') is None"
    - "A BLOCKING human go/no-go checkpoint is reached and approved BEFORE any tag push / PyPI publish"
    - "v1.4.0 git tag exists on main and is pushed; origin/main is ALSO pushed (RTD follows main); publish.yml runs on the tag and publishes ketu==1.4.0 to PyPI via OIDC"
    - "GitHub release v1.4.0 exists with sdist + wheel attached"
    - "Fresh-venv 'pip install ketu==1.4.0' FROM PyPI re-confirms the four v1.4 assertions + all-subpackage imports + no swisseph at runtime"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "[1.4.0] entry with the FINAL release date (date confirmed/corrected here if 32-01 ran on a prior day)"
      contains: "## [1.4.0] -"
  key_links:
    - from: "git tag v1.4.0 on main"
      to: "publish.yml workflow"
      via: "on.push.tags: ['v*.*.*'] trigger"
      pattern: "v1\\.4\\.0"
    - from: "publish.yml OIDC job"
      to: "PyPI ketu project"
      via: "trusted publishing (id-token: write, environment: pypi)"
      pattern: "gh-action-pypi-publish"
    - from: "git push origin main"
      to: "ReadTheDocs v1.4 docs build"
      via: "RTD follows origin/main, not the tag (push BOTH)"
      pattern: "push origin main"
    - from: "ketu/data/chiron_coeffs.npz in the wheel"
      to: "calc_planet_position(2422324.5, 13)"
      via: "pure-NumPy Chebyshev evaluator loads the embedded 1900-2100 .npz"
      pattern: "chiron_coeffs\\.npz"
---

<objective>
Run the v1.4.0 release ceremony: full local pre-flight (mypy --strict clean +
build + harmonics/Chiron-aware fresh-venv smoke on the LOCAL wheel), a BLOCKING
human go/no-go checkpoint (the next step pushes a tag that IRREVERSIBLY
publishes to PyPI), then tag + push tag + push origin/main + GitHub release,
then verify the published artifact installs from PyPI in a clean venv and
satisfies all four v1.4 assertions with NO pyswisseph at runtime.

Purpose: REL-13. Publishing to PyPI is permanent — a version number can never
be reused. Every gate must be green and a human must explicitly approve before
the tag is pushed (LOCKED constraint:
feedback_validation_review_before_release). The v1.4 smoke test is stricter
than v1.3: it proves (a) generate_harmonic_aspects(7) yields correct H7 angles,
(b) Chiron orb is 4°, (c) Chiron resolves at JD 2422324.5 (1920 — OUTSIDE the
old 1950-2050 range, proving the 1900-2100 .npz is active), and (d) pyswisseph
is absent at runtime. BOTH the tag AND origin/main are pushed (LOCKED
constraint: feedback_push_main_not_just_tag_on_release — RTD follows main, PyPI
follows the tag; pushing only the tag freezes the docs).
Output: ketu==1.4.0 live on PyPI via OIDC, GitHub release v1.4.0 with
sdist+wheel, origin/main pushed, verified clean install + four v1.4 assertions
+ no-swisseph from PyPI.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/32-release-v1-4-0/32-RESEARCH.md
@.github/workflows/publish.yml
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Date-stamp confirm and run the full harmonics+Chiron-aware local pre-flight (HARD GATES)</name>
  <files>CHANGELOG.md, fr/CHANGELOG.md</files>
  <action>
    Assumes 32-01 is committed to main (mypy fixed, version bumped, CHANGELOG
    [1.4.0] authored + dated, fr synced, UPGRADING + README + docs changelog
    done). Run the v1.4.0 pre-flight from RESEARCH "Pre-flight Script (v1.4.0)",
    VERSION=1.4.0. Each step is a HARD GATE — STOP on the first failure and
    surface it; do NOT proceed to the checkpoint with any gate red.

    0. Date-stamp confirm: verify `## [1.4.0] - <date>` in CHANGELOG.md and
       fr/CHANGELOG.md carries TODAY's UTC date. If 32-01 ran on a prior day and
       the date is now stale, update BOTH files to the real release date AND the
       docs/source/changelog.md [1.4.0] header to match, then commit that change
       to main before tagging (the tag must point at a commit carrying the final
       date). The header must be a real date — NEVER "Unreleased" / "2026-06-XX".

    1. Clean tree on main (RESEARCH Pitfall 11):
       `test -z "$(git status --porcelain)"` AND
       `git branch --show-current` == `main`.
    2. Version sync: `grep 'version = "1.4.0"' pyproject.toml` and
       `grep '__version__ = "1.4.0"' ketu/__init__.py`;
       `pip install -e . -q && pytest tests/test_version.py -v`.
    3. CHANGELOG [1.4.0] dated, no placeholders:
       `grep -q '^## \[1.4.0\] - 20' CHANGELOG.md` AND
       `! grep -q '^## \[1.4.0\] - 2026-06-XX' CHANGELOG.md` AND
       `! grep -q '^## \[Unreleased\]' CHANGELOG.md`.
    4. fr/CHANGELOG has dated [1.4.0]:
       `grep -q '^## \[1.4.0\] - 20' fr/CHANGELOG.md`.
    5. UPGRADING has the v1.3 -> v1.4 section (RESEARCH Pitfall 13):
       `grep -q 'v1\.3 -> v1\.4' UPGRADING.md`.
    6. docs/source/changelog.md placeholder resolved (RESEARCH Pitfall 2):
       `! grep -q '\[1.4.0\] - 2026-06-XX' docs/source/changelog.md`.
    7. Quality gates — ALL must pass before tag (mypy is the one that was RED at
       v1.3-time-of-research; RESEARCH Pitfall 4):
       `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` — zero violations;
       `python -m interrogate ketu/` — passes (>=95%);
       `pytest tests/ -q` — all pass (~1537 passed, 2 skipped);
       `python -m mypy --strict ketu/` — CLEAN (zero errors).
    8. Build: `rm -rf dist build ketu.egg-info && python -m build --sdist --wheel`.
       Confirm pure-Python wheel name `dist/ketu-1.4.0-py3-none-any.whl`
       (RESEARCH Pitfall 12) and `dist/ketu-1.4.0.tar.gz`.
    9. `pip install -q twine && python -m twine check dist/*` — PASSED.
   10. .npz ships in the wheel (RESEARCH Pitfall 7 — ~578 KB in v1.4, presence
       is what matters, not size):
       `python -m zipfile -l dist/ketu-1.4.0-py3-none-any.whl | grep 'ketu/data/chiron_coeffs.npz'`
       — MUST match.
   11. sdist ships fr/CHANGELOG.md:
       `tar -tzf dist/ketu-1.4.0.tar.gz | grep 'fr/CHANGELOG.md'`.
   12. Fresh-venv smoke test of the LOCAL WHEEL — the FOUR v1.4 assertions plus
       all-imports plus no-swisseph (RESEARCH "Fresh-Venv Smoke Test"). Install
       ONLY the wheel (no `.[test]` extras -> no pyswisseph, RESEARCH Pitfall
       9):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q dist/ketu-1.4.0-py3-none-any.whl
       # version
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.4.0'==m.version('ketu')"
       # all subpackage imports (incl. v1.4 generate_harmonic_aspects)
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import long; from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.cache import EphemerisCache; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('imports OK')"
       # v1.4 #1: generate_harmonic_aspects(7) -> 3 rows, H7 angles
       "$TMP/bin/python" -c "from ketu.aspects import generate_harmonic_aspects; h7=generate_harmonic_aspects(7); assert len(h7)==3; a=[float(x) for x in h7['angle']]; assert all(abs(x-e)<0.01 for x,e in zip(a,[360/7,720/7,1080/7])), a; print('H7 OK', [round(x,4) for x in a])"
       # v1.4 #2: Chiron orb == 4.0
       "$TMP/bin/python" -c "import numpy as np; from ketu.core import bodies; i=np.where(bodies['name']==b'Chiron')[0][0]; assert float(bodies['orb'][i])==4.0, bodies['orb'][i]; print('Chiron orb=4.0 OK')"
       # v1.4 #3: Chiron resolves at JD 2422324.5 (1920-01-01, outside old 1950-2050)
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2422324.5,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0, lon; print(f'Chiron 1920 OK {lon:.4f} (1900-2100 active)')"
       # v1.3 preserved: Chiron at J2000.0
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2451545.0,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0; print(f'Chiron J2000 OK {lon:.4f}')"
       # v1.4 #4: pyswisseph NOT importable (AGPL isolation)
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED'; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
   13. PyPI slot clear: query https://pypi.org/pypi/ketu/json and assert
       '1.4.0' not in releases.

    Report the full pre-flight result clearly (each gate PASS/FAIL). If ANY gate
    fails, STOP — do NOT advance to the checkpoint.
  </action>
  <verify>
    Every pre-flight gate PASSES; `python -m mypy --strict ketu/` is CLEAN;
    `dist/ketu-1.4.0-py3-none-any.whl` + `dist/ketu-1.4.0.tar.gz` exist and
    `twine check` is green; the wheel contains `ketu/data/chiron_coeffs.npz`;
    the fresh-venv local-wheel smoke passes the four v1.4 assertions
    (H7 angles, Chiron orb=4.0, Chiron@1920 finite, no-swisseph) plus
    all-imports and version; PyPI confirms 1.4.0 is not yet published; CHANGELOG
    + fr/CHANGELOG carry today's real release date.
  </verify>
  <done>
    Release is build-verified locally: mypy --strict clean, version synced to
    1.4.0, all quality gates green, the .npz ships in the wheel, the wheel
    installs in a fresh venv and satisfies all four v1.4 assertions (H7 angles,
    Chiron orb=4.0, Chiron@1920 finite, no-swisseph) plus all-subpackage
    imports, the PyPI 1.4.0 slot is free, and both changelogs carry the final
    date.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Human go/no-go before irreversible PyPI publish</name>
  <action>
    PAUSE for explicit human approval. Present the Task 1 pre-flight result and
    the trusted-publisher confirmation, then WAIT. Do NOT push the tag or
    origin/main until the user replies "approved". This is the LOCKED
    constraint feedback_validation_review_before_release — the user personally
    reviews the milestone before release. See what-built / how-to-verify below.
  </action>
  <what-built>
    A fully pre-flighted v1.4.0 release candidate: mypy --strict CLEAN (the
    Phase-28 synastry/api.py:392 no-any-return fixed), version 1.4.0 synced in
    pyproject.toml + ketu/__init__.py, a single dated `[1.4.0]` CHANGELOG
    (EN + FR) listing Added (generate_harmonic_aspects dynamic generator,
    Chiron 1900-2100 range) and Changed (Chiron orb 0°->4°, out-of-range clamp,
    docs recentring), UPGRADING `## v1.3 -> v1.4` with the orb-break + clamp +
    range + additive-generator notes, README `## What's New in v1.4.0`,
    date-stamped docs/source/changelog.md, and a locally-built + twine-checked
    sdist+wheel whose wheel embeds `ketu/data/chiron_coeffs.npz` and which — in
    a fresh venv — yields correct H7 angles from generate_harmonic_aspects(7),
    reports Chiron orb 4.0, resolves Chiron at JD 2422324.5 (1920, OUTSIDE the
    old 1950-2050 range — proving the 1900-2100 .npz is active), imports every
    subpackage, and contains NO pyswisseph, plus a confirmed-free PyPI 1.4.0
    slot.
  </what-built>
  <how-to-verify>
    This is the point of no return. Pushing the tag triggers publish.yml which
    IRREVERSIBLY publishes ketu==1.4.0 to PyPI — a version number can never be
    reused or unpublished-and-replaced.

    Before approving, confirm:
    1. The pre-flight output from Task 1 shows EVERY gate PASSED — especially
       mypy --strict CLEAN and the four v1.4-specific smoke assertions: the
       wheel contains chiron_coeffs.npz, generate_harmonic_aspects(7) returns
       angles ~[51.4286, 102.8571, 154.2857], core.bodies['orb'] for Chiron is
       4.0, the fresh-venv Chiron calc_planet_position(2422324.5, 13) returns a
       finite longitude (proving the 1900-2100 range), and
       find_spec('swisseph') is None (no pyswisseph at runtime).
    2. The PyPI trusted publisher is configured (one-time, external — should
       already exist from Phase 20): visit
       https://pypi.org/manage/project/ketu/settings/publishing/ and confirm
       Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi.
    3. You are publishing from `main` and the CHANGELOG date is correct.
    4. You have personally reviewed the v1.4 milestone and are ready to ship.

    Reply "approved" to push the v1.4.0 tag, push origin/main, and publish.
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
       `git tag -a v1.4.0 -m "Release 1.4.0 — Dynamic Harmonic Generator + Chiron Range 1900–2100"`
    2. Push the tag: `git push origin v1.4.0`. This triggers publish.yml (build
       job -> publish-to-pypi job via OIDC). publish.yml needs NO changes — it
       is already tag-triggered (`v*.*.*`) and Node-24/OIDC from Phase 20.
    3. Push origin/main: `git push origin main`. This is a FIRST-CLASS,
       NON-OPTIONAL step (LOCKED constraint
       feedback_push_main_not_just_tag_on_release, RESEARCH Pitfall 6). RTD
       follows main, NOT the tag — pushing only the tag freezes the docs at v1.3
       content even though PyPI has v1.4.0. Do BOTH pushes.
    4. Watch the workflow to completion:
       `gh run watch $(gh run list --workflow=publish.yml --limit 1 --json databaseId -q '.[0].databaseId')`
       (or `gh run list --workflow=publish.yml` then `gh run watch <id>`). It
       MUST finish SUCCESS. If it fails, capture logs (`gh run view <id>
       --log-failed`) and surface — do NOT re-tag the same version (the slot may
       be partially consumed); diagnose first.
    5. Create the GitHub release attaching the locally-built artifacts (so sdist
       + wheel are on the release page per REL-13). Use the EXACT release body
       and command from RESEARCH "GitHub Release Body (v1.4.0)":
       ```
       gh release create v1.4.0 \
         --title "Ketu 1.4.0 — Dynamic Harmonic Generator + Chiron Range 1900–2100" \
         --notes "$(cat <<'EOF'
       Ketu v1.4.0 adds a dynamic harmonic aspect generator and expands the Chiron ephemeris to
       the full 1900–2100 range. The frozen aspect table and all existing imports are unchanged.

       **New in v1.4.0:**
       - `generate_harmonic_aspects(h)` — build aspect specs on the fly for any harmonic 2–64.
         Pass as `dynamic_specs=` to `calculate_aspects`, `calculate_synastry`, `find_aspects_between_dates`.
         The frozen 14-row `core.aspects` and preset fingerprints are byte-identical.
       - Chiron range expanded to **1900–2100** (was 1950–2050): 2283 Chebyshev segments,
         max error 0.001214°, pure-NumPy runtime, ~578 KB `.npz`.

       **Changed in v1.4.0:**
       - Chiron orb **0° → 4°** (Pluto parity): Chiron now forms scored aspects in all detection paths
         (`calculate_aspects`, `compute_chart`, `calculate_synastry`, `find_aspects_between_dates`).
       - Chiron out-of-range input is now **silently clamped** to the nearest boundary (was `ValueError`).
       - Documentation recentred: summary tables show CLASSICAL (5) and TRADITIONAL (7) only;
         EXTENDED / full-circle minors remain available in code.

       **Migration (see UPGRADING.md → v1.3 → v1.4):**
       - Downstream code expecting **zero Chiron aspects** (old orb=0) must adapt — aspect counts
         and scores for body_id=13 will now be non-empty.
       - Code relying on `ValueError` for out-of-range JD must add explicit bounds checking.

       - 📋 [CHANGELOG](https://github.com/alkimya/ketu/blob/main/CHANGELOG.md)
       - 🔄 [UPGRADING](https://github.com/alkimya/ketu/blob/main/UPGRADING.md#v13---v14)
       - 📦 `pip install ketu==1.4.0`

       1537 tests, mypy --strict, 100% coverage.
       EOF
       )" \
         dist/ketu-1.4.0-py3-none-any.whl dist/ketu-1.4.0.tar.gz
       ```
    6. POST-PUBLISH verification — fresh venv installing FROM PyPI (may need a
       short retry loop while PyPI's CDN propagates). Re-run the four v1.4
       assertions against the PUBLISHED artifact:
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q "ketu==1.4.0"
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.4.0'==m.version('ketu')"
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.aspects import calculate_aspects, aspects_for_harmonics, generate_harmonic_aspects; from ketu.cycles import generate_cycle_series; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('subpackages OK')"
       "$TMP/bin/python" -c "from ketu.aspects import generate_harmonic_aspects; h7=generate_harmonic_aspects(7); assert len(h7)==3; a=[float(x) for x in h7['angle']]; assert all(abs(x-e)<0.01 for x,e in zip(a,[360/7,720/7,1080/7])); print('H7 OK', [round(x,4) for x in a])"
       "$TMP/bin/python" -c "import numpy as np; from ketu.core import bodies; i=np.where(bodies['name']==b'Chiron')[0][0]; assert float(bodies['orb'][i])==4.0; print('Chiron orb=4.0 OK')"
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2422324.5,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0; print(f'Chiron 1920 OK {lon:.4f}')"
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
    7. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.

    Report: PyPI URL, GitHub release URL, confirmation that BOTH the tag AND
    origin/main were pushed, and the post-publish smoke result (version + H7
    angles + Chiron orb 4.0 + Chiron@1920 longitude + no-swisseph).
  </action>
  <verify>
    `git tag -l v1.4.0` shows the tag; `git rev-parse origin/main` matches local
    main (origin/main pushed); `gh run list --workflow=publish.yml` latest run =
    SUCCESS; `gh release view v1.4.0` lists both `ketu-1.4.0-py3-none-any.whl`
    and `ketu-1.4.0.tar.gz` assets; PyPI JSON API includes 1.4.0; the fresh-venv
    `pip install ketu==1.4.0` from PyPI passes all four v1.4 assertions
    (version == metadata == "1.4.0"; H7 angles ~[51.4286,102.8571,154.2857];
    Chiron orb 4.0; Chiron@1920 finite in [0,360)) plus all-imports and
    `find_spec('swisseph') is None`.
  </verify>
  <done>
    v1.4.0 tagged on main and pushed; origin/main ALSO pushed (RTD will rebuild
    v1.4 docs); publish.yml succeeded; ketu==1.4.0 is live on PyPI; GitHub
    release v1.4.0 has sdist + wheel attached; fresh-venv install FROM PyPI
    yields correct H7 angles, Chiron orb 4.0, a finite Chiron@1920 longitude,
    imports all subpackages, and confirms no pyswisseph at runtime.
  </done>
</task>

</tasks>

<verification>
- Pre-flight all-green before any irreversible action (Task 1), including mypy --strict CLEAN, .npz-in-wheel, and the four v1.4 smoke assertions (H7 angles, Chiron orb 4.0, Chiron@1920 finite, no-swisseph).
- BLOCKING human approval recorded before tag push (checkpoint).
- `git tag -l v1.4.0` present and pushed; origin/main ALSO pushed (`git rev-parse origin/main` == local main).
- `gh run list --workflow=publish.yml` latest run = SUCCESS.
- `gh release view v1.4.0` shows sdist + wheel assets.
- PyPI: `pip install ketu==1.4.0` in a clean venv -> import OK, `ketu.__version__ == importlib.metadata.version("ketu") == "1.4.0"`, all subpackages import, generate_harmonic_aspects(7) H7 angles correct, Chiron orb 4.0, `calc_planet_position(2422324.5, 13)` finite, `find_spec('swisseph') is None`.
</verification>

<success_criteria>
REL-13 satisfied: ketu==1.4.0 published to PyPI via OIDC trusted publishing
(Success Criterion 2); GitHub release v1.4.0 attaches sdist + wheel; BOTH the
v1.4.0 tag AND origin/main are pushed (RTD follows main, PyPI follows tag —
Success Criterion 2); a fresh-venv `pip install ketu==1.4.0` smoke confirms
generate_harmonic_aspects(7) H7 angles, Chiron orb 4°, a finite Chiron
longitude at JD 2422324.5 (1900-2100 range), all-subpackage imports, and NO
pyswisseph at runtime (Success Criterion 3). No irreversible action taken
without the explicit human go/no-go.
</success_criteria>

<output>
After completion, create
`.planning/phases/32-release-v1-4-0/32-02-SUMMARY.md`
</output>
