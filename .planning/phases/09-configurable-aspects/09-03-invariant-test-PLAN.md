---
phase: 09-configurable-aspects
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/test_ketu.py
autonomous: true
plan_id: "09-03"
requirements:
  - ASP-01

must_haves:
  truths:
    - "core.aspects length-14 invariant is enforced — test fails on any deletion or shape change"
    - "core.aspects row order is enforced per-row (name, angle, coef) for all 14 rows — test fails on any reorder"
    - "A sha256 fingerprint over name.tobytes() + angle.tobytes() + coef.tobytes() is pinned — test fails on encoding/dtype drift even if values look equal"
    - "Tests fail with surgical, informative error messages identifying WHICH row drifted"
    - "Mutation test: temporarily swapping rows 1 and 2 in core.py causes test failures (verified during plan execution)"
  artifacts:
    - path: "tests/test_ketu.py"
      provides: "Strengthened test_aspects_structure (formerly lines 43-49) plus new fingerprint and per-row tests"
      contains: "EXPECTED_ASPECT_NAMES"
  key_links:
    - from: "tests/test_ketu.py"
      to: "ketu.core.aspects"
      via: "import + per-row assertions"
      pattern: "from ketu\\.core import aspects|aspects_data\\["
    - from: "tests/test_ketu.py"
      to: "hashlib.sha256"
      via: "byte-level fingerprint"
      pattern: "sha256"
---

<objective>
Strengthen the `core.aspects` invariant test in `tests/test_ketu.py:43-49`. The current test spot-checks 4 fields out of 42 (14 rows × 3 fields) and would silently pass on row reorder, coefficient drift, or dtype change.

Purpose: ASP-01 — "invariant test guarantees order and length". The CURRENT test (test_aspects_structure) is too weak per research Pitfall 6 ("Invariant test that's too weak (or too strong)"). Defense in depth: length + dtype.names + per-row name + per-row angle + per-row coef + sha256 byte fingerprint.

Output:
- Modified `tests/test_ketu.py` — `test_aspects_structure` either replaced or augmented with five additional assertion functions.
- The hash fingerprint is computed AT TEST WRITE TIME (during plan execution), not at runtime — pinned as a constant in the test file.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/09-configurable-aspects/09-RESEARCH.md

# Current core.aspects definition (the invariant target)
@ketu/core.py

# Existing weak test to strengthen (lines 43-49)
@tests/test_ketu.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Compute the canonical sha256 fingerprint</name>
  <files>(no files modified — discovery step; output is a single hex string captured for Task 2)</files>
  <action>
    Compute the v1.0-canonical fingerprint by running the following Python snippet (on the current HEAD, which still has the v1.0-spec core.aspects):

        python -c "
        import hashlib
        from ketu.core import aspects
        h = hashlib.sha256()
        h.update(aspects['name'].tobytes())
        h.update(aspects['angle'].tobytes())
        h.update(aspects['coef'].tobytes())
        print(h.hexdigest())
        print('len:', len(aspects))
        print('dtype.names:', aspects.dtype.names)
        print('name dtype:', aspects['name'].dtype)
        print('angle dtype:', aspects['angle'].dtype)
        print('coef dtype:', aspects['coef'].dtype)
        for i in range(len(aspects)):
            print(i, aspects['name'][i], aspects['angle'][i], aspects['coef'][i])
        "

    Capture:
    - The 64-char hex fingerprint → use as `EXPECTED_FINGERPRINT` in Task 2.
    - The dtype names tuple → use to assert `aspects.dtype.names == (...)`.
    - The 14 (name, angle, coef) rows → cross-check against the EXPECTED_NAMES/ANGLES/COEFS arrays in Task 2.

    Record all of the above output in the eventual SUMMARY.md as a verifiable provenance entry. The fingerprint is the v1.0 contract baked into the test.
  </action>
  <verify>
    The Python one-liner runs and prints a 64-character hex string + 14 row entries. The 14 names match the research's EXPECTED_NAMES list (research file lines 367-371): Conjunction, Semi-sextile, Decile, Novile, Sextile, Quintile, Binovile, Square, Tredecile, Trine, Biquintile, Quincunx, Quadrinovile, Opposition.
  </verify>
  <done>
    Fingerprint hex string captured. Dtype names tuple captured. 14 rows visually cross-checked against research lines 367-375. All values ready for Task 2.
  </done>
</task>

<task type="auto">
  <name>Task 2: Strengthen test_aspects_structure with hash + per-row + dtype checks</name>
  <files>tests/test_ketu.py</files>
  <action>
    Edit `tests/test_ketu.py`. The current weak test is at lines 43-49 (within `class TestCoreData` based on the surrounding context). Strategy: REPLACE the body of `test_aspects_structure` with the strict-invariant block, AND add five new test functions in the same class, so the test count goes from 1 → 6 functions covering different invariant facets.

    Add at the top of the file (or in an appropriate test-data section near the top):

        import hashlib
        from ketu.core import aspects as aspects_data  # if not already imported under this name

        EXPECTED_ASPECT_NAMES = (
            b"Conjunction", b"Semi-sextile", b"Decile", b"Novile", b"Sextile",
            b"Quintile", b"Binovile", b"Square", b"Tredecile", b"Trine",
            b"Biquintile", b"Quincunx", b"Quadrinovile", b"Opposition",
        )
        EXPECTED_ASPECT_ANGLES = (0.0, 30.0, 36.0, 40.0, 60.0, 72.0, 80.0, 90.0,
                                  108.0, 120.0, 144.0, 150.0, 160.0, 180.0)
        # Coefficients per ketu/core.py:84-103 (verify these match before pinning)
        EXPECTED_ASPECT_COEFS = (1.0, 1/6, 1/10, 1/9, 1/3, 1/5, 2/9, 1/2,
                                  3/10, 2/3, 2/5, 5/6, 4/9, 1.0)

        # Pin v1.0 byte-level fingerprint — captured during Plan 09-03 execution.
        # If this test fails, core.aspects bytes changed. Verify the change is
        # APPEND-ONLY (rows 0-13 unchanged) per Phase 9 invariant before updating.
        EXPECTED_ASPECT_FINGERPRINT_V1 = "<PASTE-FROM-TASK-1>"

    Then within the existing `class TestCoreData:` (or whichever class hosts the current `test_aspects_structure`), update/add:

        def test_aspects_length(self):
            """ASP-01: core.aspects must remain length 14 (append-only invariant)."""
            assert len(aspects_data) == 14, (
                f"core.aspects length changed to {len(aspects_data)}; "
                "v1.1 invariant pins it at 14 (append-only)"
            )

        def test_aspects_dtype_names(self):
            """ASP-01: core.aspects field names must match v1.0 schema."""
            assert aspects_data.dtype.names == ("name", "angle", "coef")

        def test_aspects_structure(self):
            """ASP-01: per-row name + angle + coef checks (strengthened from v1.0)."""
            assert len(aspects_data) == 14
            for i, expected_name in enumerate(EXPECTED_ASPECT_NAMES):
                assert aspects_data["name"][i] == expected_name, (
                    f"row {i} name drifted: got {aspects_data['name'][i]!r}, "
                    f"expected {expected_name!r}"
                )
            for i, expected_angle in enumerate(EXPECTED_ASPECT_ANGLES):
                assert aspects_data["angle"][i] == pytest.approx(expected_angle, abs=1e-6), (
                    f"row {i} angle drifted: got {aspects_data['angle'][i]}, "
                    f"expected {expected_angle}"
                )
            for i, expected_coef in enumerate(EXPECTED_ASPECT_COEFS):
                assert aspects_data["coef"][i] == pytest.approx(expected_coef, abs=1e-6), (
                    f"row {i} coef drifted: got {aspects_data['coef'][i]}, "
                    f"expected {expected_coef}"
                )

        def test_aspects_byte_fingerprint(self):
            """ASP-01: sha256 fingerprint catches dtype/encoding drift that field-by-field tests miss."""
            h = hashlib.sha256()
            h.update(aspects_data["name"].tobytes())
            h.update(aspects_data["angle"].tobytes())
            h.update(aspects_data["coef"].tobytes())
            fingerprint = h.hexdigest()
            assert fingerprint == EXPECTED_ASPECT_FINGERPRINT_V1, (
                f"core.aspects bytes changed (got {fingerprint}); "
                "verify the change is an APPEND (rows 0-13 unchanged) per Phase 9 "
                "invariant, then update EXPECTED_ASPECT_FINGERPRINT_V1"
            )

    Substitute `EXPECTED_ASPECT_FINGERPRINT_V1` with the actual hex captured in Task 1.

    If `pytest` is not already imported at the top of the file, add `import pytest`. (It is almost certainly already imported.)

    The original `test_aspects_structure` was 7 lines; after this change it's 4 separate functions totaling ~50 lines. Keep all of them in the same test class (existing class structure preserved).

    Anti-patterns to avoid (per research Pitfall 6):
    - Do NOT make the fingerprint a "soft warning" — assertEqual it exactly.
    - Do NOT compare angle floats with == when they're stored as f4 — use `pytest.approx(abs=1e-6)`. (Note: angles like 60.0 ARE exact in f4 because they're integer-valued, but coefs like 1/6 are NOT — using `approx` for both is consistent and safe.)
    - Do NOT include a "TODO: tighten this later" comment — the strict version IS the deliverable.
    - Do NOT add a separate test file — the existing `tests/test_ketu.py` is the canonical home for core-data invariants.

    NOTE on `core.aspects` import name: in the existing `tests/test_ketu.py` file, the `aspects` from `ketu.core` is likely already imported under `aspects_data` or similar (verify by reading the existing top-of-file imports). Use whatever local name is already established. If the existing test uses `aspects_data`, keep using it (do NOT rename to `aspects` — would shadow the new presets `aspects=` parameter introduced in later plans).
  </action>
  <verify>
    Run: `pytest tests/test_ketu.py::TestCoreData -v` (or whatever the existing class is called — check the file). All four/five tests pass.
    Run: `pytest tests/test_ketu.py -v` — full file passes.
    Run a deliberate mutation test (do NOT commit this):
      1. Edit `ketu/core.py`: swap rows 1 and 2 in the `aspects` array (e.g. swap `Semi-sextile` and `Decile`).
      2. Run `pytest tests/test_ketu.py -v` — confirm at least `test_aspects_structure` AND `test_aspects_byte_fingerprint` BOTH fail with informative messages identifying the drift.
      3. Revert `ketu/core.py` (`git checkout -- ketu/core.py`).
      4. Run pytest again — all green.
    Document in summary that mutation test passed.
  </verify>
  <done>
    `tests/test_ketu.py` has the four new test functions (length, dtype_names, structure with per-row checks, byte_fingerprint). The fingerprint constant is a real 64-char hex (NOT the placeholder string). Mutation test confirmed test fails on row reorder. Existing test suite still passes (no other tests broken).
  </done>
</task>

</tasks>

<verification>
- `pytest tests/test_ketu.py -v` — all tests pass on current HEAD.
- `EXPECTED_ASPECT_FINGERPRINT_V1` is a 64-char lowercase hex string in `tests/test_ketu.py`, not a placeholder.
- Mutation test: temporarily swap rows in `core.py`, confirm `test_aspects_structure` AND `test_aspects_byte_fingerprint` BOTH fail with informative messages, then revert.
- `core.aspects` itself is UNCHANGED — `git diff ketu/core.py` is empty.
- `pytest tests/ -x` (full suite) still green.
</verification>

<success_criteria>
- ASP-01 satisfied: invariant test pins length 14, dtype names, per-row name/angle/coef, and sha256 byte fingerprint.
- Test failures produce surgical messages identifying WHICH row drifted (not just "structure changed").
- Mutation test verified: row swap detected.
- No change to `ketu/core.py` (append-only contract preserved).
</success_criteria>

<output>
After completion, create `.planning/phases/09-configurable-aspects/09-03-SUMMARY.md` documenting:
- The captured fingerprint (full 64-char hex)
- The captured dtype.names tuple and field dtypes
- The 14-row name/angle/coef table verified
- Mutation test result (row swap detected → both structure + fingerprint tests fail)
- Updated test file path and line count delta (e.g. "tests/test_ketu.py: 7 lines → 50+ lines for invariant block")
</output>
