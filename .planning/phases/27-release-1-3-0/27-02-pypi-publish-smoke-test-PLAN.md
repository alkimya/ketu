---
phase: 27-release-1-3-0
plan: 02
type: execute
wave: 2
depends_on: ["27-01"]
files_modified:
  - CHANGELOG.md
  - fr/CHANGELOG.md
autonomous: false
user_setup:
  - service: pypi
    why: "PyPI OIDC trusted publishing target for ketu==1.3.0 (already configured from Phase 20 — verification only, no token needed)"
    dashboard_config:
      - task: "Confirm trusted publisher = Owner:alkimya, Repo:ketu, Workflow:publish.yml, Environment:pypi"
        location: "https://pypi.org/manage/project/ketu/settings/publishing/"

must_haves:
  truths:
    - "Local pre-flight passes: clean tree on main, version synced to 1.3.0, CHANGELOG dated (no Unreleased), UPGRADING has Chiron section, numpydoc + interrogate + full suite + mypy --strict green, build + twine check green"
    - "Local wheel contains ketu/data/chiron_coeffs.npz (verified via python -m zipfile -l)"
    - "Fresh-venv install of the LOCAL wheel resolves Chiron (calc_planet_position(2451545.0, 13) finite, 0<=lon<360), imports all subpackages, and has NO swisseph (importlib.util.find_spec('swisseph') is None)"
    - "v1.3.0 git tag exists on main and is pushed; publish.yml runs on the tag and publishes ketu==1.3.0 to PyPI via OIDC"
    - "GitHub release v1.3.0 exists with sdist + wheel attached"
    - "Fresh-venv 'pip install ketu==1.3.0' FROM PyPI smoke-imports all subpackages, resolves Chiron, and confirms no swisseph at runtime"
  artifacts:
    - path: "CHANGELOG.md"
      provides: "[1.3.0] entry with the FINAL release date (date-stamp confirmed/corrected here if needed)"
      contains: "## [1.3.0] -"
  key_links:
    - from: "git tag v1.3.0 on main"
      to: "publish.yml workflow"
      via: "on.push.tags: ['v*.*.*'] trigger"
      pattern: "v1\\.3\\.0"
    - from: "publish.yml OIDC job"
      to: "PyPI ketu project"
      via: "trusted publishing (id-token: write, environment: pypi)"
      pattern: "gh-action-pypi-publish"
    - from: "ketu/data/chiron_coeffs.npz in the wheel"
      to: "calc_planet_position(jd, 13)"
      via: "pure-NumPy Chebyshev evaluator loads the embedded .npz at runtime"
      pattern: "chiron_coeffs\\.npz"
---

<objective>
Run the v1.3.0 release ceremony: full local pre-flight (build + Chiron-aware
fresh-venv smoke on the LOCAL wheel), a HUMAN go/no-go checkpoint (the next
step pushes a tag that IRREVERSIBLY publishes to PyPI), then tag + push +
GitHub release, then verify the published artifact installs from PyPI in a
clean venv and resolves Chiron with NO pyswisseph.

Purpose: REL-11. Publishing to PyPI is permanent — a version number can never
be reused. Every gate must be green and a human must explicitly approve before
the tag is pushed. The v1.3 smoke test is stricter than v1.2: it must prove
(a) Chiron resolves from the embedded .npz, (b) the .npz actually ships in the
wheel, and (c) pyswisseph is NOT in the runtime environment (the core
pure-NumPy / AGPL-isolation invariant).
Output: ketu==1.3.0 live on PyPI, GitHub release v1.3.0 with sdist+wheel,
verified clean install + Chiron resolution + no-swisseph from PyPI.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/27-release-1-3-0/27-RESEARCH.md
@.github/workflows/publish.yml
@pyproject.toml
@ketu/__init__.py
@CHANGELOG.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Date-stamp the release and run the full Chiron-aware local pre-flight</name>
  <files>CHANGELOG.md, fr/CHANGELOG.md</files>
  <action>
    Assumes 27-01 is committed to main (version bumped, CHANGELOG merged +
    dated, UPGRADING Chiron section added). Run the v1.3.0 pre-flight from
    RESEARCH "Pre-flight Script (v1.3.0 version)", VERSION=1.3.0. Each step is
    a HARD GATE — STOP on the first failure and surface it; do NOT proceed to
    the checkpoint with any gate red.

    0. Date-stamp: confirm `## [1.3.0] - <date>` in CHANGELOG.md and
       fr/CHANGELOG.md carries TODAY's UTC date. If 27-01 ran on a prior day
       and the date is now stale, update BOTH files to the real release date.
       The header must be a real date — NEVER "Unreleased" (RESEARCH Pitfall 7).
       If the date is corrected, commit that change to main before tagging
       (the tag must point at a commit containing the final date).

    1. Clean tree on main:
       `test -z "$(git status --porcelain)"` AND
       `git branch --show-current` == `main` (RESEARCH Pitfall 9).
    2. Version sync: `grep 'version = "1.3.0"' pyproject.toml` and
       `grep '__version__ = "1.3.0"' ketu/__init__.py`;
       `pip install -e . -q && pytest tests/test_version.py -v`.
    3. CHANGELOG dated, not Unreleased:
       `grep -q '^## \[1.3.0\] - 20' CHANGELOG.md` AND
       `! grep -q '^## \[1.3.0\] - Unreleased' CHANGELOG.md` AND
       `! grep -q '^## \[Unreleased\]' CHANGELOG.md`.
    4. UPGRADING has the Chiron section: `grep -q 'Chiron' UPGRADING.md`.
    5. Quality gates (all must pass before tag):
       `python -m numpydoc lint $(find ketu -name "*.py" ! -path "*/__pycache__/*" ! -name "lunar_calendar.py" ! -name "_*.py")` — zero violations;
       `python -m interrogate ketu/` — passes (>=95%);
       `pytest tests/ -q` — all pass (~1399);
       `python -m mypy --strict ketu/` — clean.
    6. Build: `rm -rf dist build ketu.egg-info && python -m build --sdist --wheel`.
       Confirm pure-Python wheel name `dist/ketu-1.3.0-py3-none-any.whl`
       (RESEARCH Pitfall 10) and `dist/ketu-1.3.0.tar.gz`.
    7. `pip install -q twine && python -m twine check dist/*` — PASSED.
    8. .npz ships in the wheel (RESEARCH Pitfall 5):
       `python -m zipfile -l dist/ketu-1.3.0-py3-none-any.whl | grep 'ketu/data/chiron_coeffs.npz'`
       — MUST match.
    9. Fresh-venv smoke test of the LOCAL WHEEL (RESEARCH "Fresh-Venv Smoke
       Test", the four v1.3 assertions). Install ONLY the wheel (no `.[test]`
       extras → no pyswisseph):
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q dist/ketu-1.3.0-py3-none-any.whl
       # version
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.3.0'==m.version('ketu')"
       # all subpackage imports
       "$TMP/bin/python" -c "from ketu.core import bodies, aspects, signs; from ketu.calculations import long; from ketu.aspects import calculate_aspects, aspects_for_harmonics; from ketu.cycles import generate_cycle_series; from ketu.cache import EphemerisCache; from ketu.houses import calculate_houses; from ketu.charts import compute_chart; from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.ephemeris.planets import calc_planet_position; print('imports OK')"
       # Chiron resolves from embedded .npz (body_id=13)
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2451545.0,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0, lon; print(f'Chiron OK {lon:.4f}')"
       # pyswisseph NOT importable (AGPL isolation, RESEARCH Pitfall 4)
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None, 'pyswisseph LEAKED'; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
    10. PyPI slot clear: query https://pypi.org/pypi/ketu/json and assert
        '1.3.0' not in releases.
    11. sdist ships fr/CHANGELOG.md:
        `tar -tzf dist/ketu-1.3.0.tar.gz | grep 'fr/CHANGELOG.md'`.

    Report the full pre-flight result clearly (each gate PASS/FAIL). If ANY
    gate fails, STOP — do NOT advance to the checkpoint.
  </action>
  <verify>
    Every pre-flight gate PASSES; `dist/ketu-1.3.0-py3-none-any.whl` +
    `dist/ketu-1.3.0.tar.gz` exist and `twine check` is green; the wheel
    contains `ketu/data/chiron_coeffs.npz`; the fresh-venv local-wheel smoke
    test passes all four v1.3 assertions (version, all-imports, Chiron finite,
    no-swisseph); PyPI confirms 1.3.0 is not yet published; CHANGELOG +
    fr/CHANGELOG carry today's real release date.
  </verify>
  <done>
    Release is build-verified locally: version synced to 1.3.0, all quality
    gates green, the .npz ships in the wheel, the wheel installs and resolves
    Chiron + imports every subpackage in a fresh venv WITHOUT pyswisseph, the
    PyPI 1.3.0 slot is free, and both changelogs carry the final date.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Human go/no-go before irreversible PyPI publish</name>
  <action>
    PAUSE for explicit human approval. Present the Task 1 pre-flight result
    and the trusted-publisher confirmation, then wait. Do NOT push the tag
    until the user replies "approved". See what-built / how-to-verify below.
  </action>
  <what-built>
    A fully pre-flighted v1.3.0 release candidate: version 1.3.0 synced in
    pyproject.toml + ketu/__init__.py, a single dated `[1.3.0]` CHANGELOG
    (EN + FR) carrying both breaking notes (Chiron 13->14 positional contract
    + aspect default/coefficient/preset), UPGRADING `v1.2 -> v1.3` with the
    Chiron shape-table section, a locally-built + twine-checked sdist+wheel
    whose wheel embeds `ketu/data/chiron_coeffs.npz` and which — in a fresh
    venv — resolves Chiron via `calc_planet_position(jd, 13)`, imports every
    subpackage, and contains NO pyswisseph, plus a confirmed-free PyPI 1.3.0
    slot.
  </what-built>
  <how-to-verify>
    This is the point of no return. Pushing the tag triggers publish.yml which
    IRREVERSIBLY publishes ketu==1.3.0 to PyPI — a version number can never be
    reused or unpublished-and-replaced.

    Before approving, confirm:
    1. The pre-flight output from Task 1 shows EVERY gate PASSED — especially
       the three v1.3-specific ones: the wheel contains chiron_coeffs.npz, the
       fresh-venv Chiron `calc_planet_position(2451545.0, 13)` returns a finite
       longitude, and `find_spec('swisseph') is None` (no pyswisseph at
       runtime).
    2. The PyPI trusted publisher is configured (one-time, external — should
       already exist from Phase 20): visit
       https://pypi.org/manage/project/ketu/settings/publishing/ and confirm
       Owner=alkimya, Repo=ketu, Workflow=publish.yml, Environment=pypi.
    3. You are publishing from `main` and the CHANGELOG date is correct.

    Reply "approved" to push the v1.3.0 tag and publish. Reply with any concern
    to halt — nothing irreversible has happened yet.
  </how-to-verify>
  <resume-signal>Type "approved" to tag + push + publish, or describe what to fix.</resume-signal>
</task>

<task type="auto">
  <name>Task 2: Tag, push, create the GitHub release, and verify the PyPI install + Chiron</name>
  <files></files>
  <action>
    Only after the human approves the checkpoint.
    1. Tag on main:
       `git tag -a v1.3.0 -m "Release 1.3.0 — Chiron (14th body) + data-driven aspect engine"`
    2. Push the tag: `git push origin v1.3.0`. This triggers publish.yml
       (build job -> publish-to-pypi job via OIDC). publish.yml needs NO
       changes — it is already tag-triggered and Node-24 from Phase 20.
    3. Watch the workflow to completion:
       `gh run watch $(gh run list --workflow=publish.yml --limit 1 --json databaseId -q '.[0].databaseId')`
       (or `gh run list --workflow=publish.yml` then `gh run watch <id>`).
       It MUST finish SUCCESS. If it fails, capture logs
       (`gh run view <id> --log-failed`) and surface — do NOT re-tag the same
       version (the slot may be partially consumed); diagnose first.
    4. Create the GitHub release attaching the locally-built artifacts (so
       sdist + wheel are on the release page per REL-11). Use the release-notes
       body from RESEARCH "Pattern 3: GitHub Release Creation" (Chiron +
       aspects_for_harmonics + 5-field dtype + TRADITIONAL default; BREAKING:
       CHART_DTYPE 13->14, CYCLE_DTYPE angular_separation direction, aspect
       default; links to CHANGELOG/UPGRADING; `pip install ketu==1.3.0`;
       1399 tests / mypy --strict / 100% coverage / 57 doctests). Replace any
       `YYYY-MM-DD` placeholders in the anchor links with the real date used
       in the CHANGELOG header:
       ```
       gh release create v1.3.0 \
         --title "Ketu 1.3.0 — Chiron (14th body) + aspect-engine hardening" \
         --notes "<RESEARCH Pattern 3 body, with the real CHANGELOG date in the anchor links>" \
         dist/ketu-1.3.0-py3-none-any.whl dist/ketu-1.3.0.tar.gz
       ```
    5. POST-PUBLISH verification — fresh venv installing FROM PyPI (may need a
       short retry loop while PyPI's CDN propagates). This re-runs the three
       v1.3 assertions against the PUBLISHED artifact:
       ```
       TMP=$(mktemp -d); python -m venv "$TMP"
       "$TMP/bin/pip" install -q "ketu==1.3.0"
       "$TMP/bin/python" -c "import ketu, importlib.metadata as m; assert ketu.__version__=='1.3.0'==m.version('ketu')"
       "$TMP/bin/python" -c "from ketu.synastry import calculate_synastry; from ketu.composite import calculate_composite; from ketu.returns import solar_return; from ketu.parts import calculate_part; from ketu.aspects import aspects_for_harmonics; from ketu.charts import compute_chart; print('subpackages OK')"
       "$TMP/bin/python" -c "import math; from ketu.ephemeris.planets import calc_planet_position; lon=float(calc_planet_position(2451545.0,13)[0]); assert math.isfinite(lon) and 0.0<=lon<360.0; print(f'Chiron OK {lon:.4f}')"
       "$TMP/bin/python" -c "import importlib.util; assert importlib.util.find_spec('swisseph') is None; print('no swisseph OK')"
       rm -rf "$TMP"
       ```
    6. Clean local build artifacts: `rm -rf dist build ketu.egg-info`.
    Report: PyPI URL, GitHub release URL, and the post-publish smoke result
    (version + subpackages + Chiron longitude + no-swisseph).
  </action>
  <verify>
    `git tag -l v1.3.0` shows the tag; `gh run list --workflow=publish.yml`
    latest run = SUCCESS; `gh release view v1.3.0` lists both
    `ketu-1.3.0-py3-none-any.whl` and `ketu-1.3.0.tar.gz` assets; PyPI JSON
    API includes 1.3.0; the fresh-venv `pip install ketu==1.3.0` from PyPI
    passes all four assertions (version == metadata == "1.3.0", all subpackages
    import, Chiron `calc_planet_position(2451545.0, 13)` finite in [0,360),
    `find_spec('swisseph') is None`).
  </verify>
  <done>
    v1.3.0 tagged on main and pushed; publish.yml succeeded; ketu==1.3.0 is
    live on PyPI; GitHub release v1.3.0 has sdist + wheel attached; fresh-venv
    install FROM PyPI smoke-imports all subpackages, resolves Chiron, and
    confirms no pyswisseph at runtime.
  </done>
</task>

</tasks>

<verification>
- Pre-flight all-green before any irreversible action (Task 1), including the three v1.3 gates: .npz-in-wheel, Chiron-finite, no-swisseph.
- Human approval recorded before tag push (checkpoint).
- `git tag -l v1.3.0` present and pushed.
- `gh run list --workflow=publish.yml` latest run = SUCCESS.
- `gh release view v1.3.0` shows sdist + wheel assets.
- PyPI: `pip install ketu==1.3.0` in a clean venv -> import OK,
  `ketu.__version__ == importlib.metadata.version("ketu") == "1.3.0"`,
  all subpackages import, `calc_planet_position(2451545.0, 13)` finite,
  `find_spec('swisseph') is None`.
</verification>

<success_criteria>
REL-11 satisfied: ketu==1.3.0 published to PyPI via OIDC trusted publishing
(Success Criterion 2); GitHub release v1.3.0 attaches sdist + wheel; a
fresh-venv `pip install ketu==1.3.0` smoke-imports all subpackages and
resolves Chiron (`calc_planet_position(jd, 13)` finite) with NO pyswisseph in
the runtime environment (Success Criterion 3). No irreversible action taken
without the explicit human go/no-go.
</success_criteria>

<output>
After completion, create
`.planning/phases/27-release-1-3-0/27-02-SUMMARY.md`
</output>
