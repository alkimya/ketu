# Phase 13: Doc Gates & CI Foundation - Pattern Map

**Mapped:** 2026-05-08
**Files analyzed:** 7 modified files (no new files)
**Analogs found:** 7 / 7 (every modified file has a concrete in-repo precedent)

## Overview

Phase 13 is pure ops/CI work — no new Python module is created. Every change either (a) adds a new section/step to an existing config/workflow, or (b) edits docstrings already present in the source tree. For every (a), the repo already contains a structurally-identical block that the new block can mirror line-for-line. For every (b), the repo contains adjacent, already-clean docstrings in the same module (or in a sibling module like `ketu/houses/_ecliptic.py`) that demonstrate the canonical numpydoc shape this project uses.

The planner's job is therefore "copy this block, change these literals" — not "design a new pattern".

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `pyproject.toml` (new `[project.optional-dependencies].dev`) | package metadata — optional deps group | declarative-config | `[project.optional-dependencies].test` (lines 41-44, same file) | exact (sibling group) |
| `pyproject.toml` (new `[tool.interrogate]`) | tool config — exclusion list + thresholds | declarative-config | `[tool.coverage.run]` (lines 78-84) for `exclude`/`omit` shape; `[tool.coverage.report]` (lines 86-93) for `fail_under` shape | exact (same shape, different tool) |
| `pyproject.toml` (new `[tool.numpydoc_validation]`) | tool config — checks + exclusion list | declarative-config | `[tool.mypy]` block (lines 96-120) for the "global config + per-module overrides" pattern; `[tool.coverage.run].omit` for the exclusion-list shape | exact (mirror of mypy structure) |
| `.github/workflows/tests.yml` (new "Doc coverage gate (interrogate)" step) | CI workflow step — blocking gate, 3.13-only | CI step (request-response within Actions runner) | "Check coverage threshold" step (lines 41-44) — same `if: matrix.python-version == '3.13'` gating + same `python -m <tool>` invocation form | exact |
| `.github/workflows/tests.yml` (new "Doc style audit (numpydoc)" step) | CI workflow step — non-blocking warning, 3.13-only | CI step (request-response within Actions runner) | "Type check" step (lines 35-39) for `if: matrix.python-version == 'X.Y'` gating + tool install pattern; same Coverage step for the 3.13 gating | role-match (gating identical, `continue-on-error: true` is new) |
| `Makefile` (optional new `doc-gates` target) | dev convenience target | shell-script recipe | `houses-coverage` target (lines 21-39) — same `## doc-gates: …` help-comment header convention, same `$(PYTHON) -m <tool>` invocation, same `.PHONY` registration | exact |
| `ketu/houses/placidus.py` (4 missing docstrings on `_ra_formula_cusp_2/3/11/12`) | source — module-level helper functions | docstring-only edit | `_iterate_cusp_ra` (lines 114-150, same file) and `ra_to_lambda` in `ketu/houses/_ecliptic.py` (lines 15-47) — both show the canonical numpydoc shape this codebase uses | exact (sibling functions) |
| `ketu/complex.py`, `ketu/calculations.py`, `ketu/cycles/calculator.py` (numpydoc fixes — bulk) | source — public-API docstring polish | docstring-only edit | `ketu/houses/_ecliptic.py` (full file) and `ketu/houses/placidus.py:_iterate_cusp_ra` — already-clean numpydoc style in the same project | role-match (clean siblings; same library, same convention) |
| `CHANGELOG.md`, `README.md` (positive-add of "enforced by CI" wording) | public docs — narrative addition | text edit | README "Documentation" section (lines 226-237) for the "list-of-features" voice; CHANGELOG `### Added` sub-section under `## [1.1.0]` (line 59 forward) for the entry shape | role-match |

**No new files are created in Phase 13.** Every entry above is a modification to an existing file.

## Pattern Assignments

### `pyproject.toml` — new `[project.optional-dependencies].dev` group

**Analog:** `pyproject.toml` itself, `[project.optional-dependencies].test` group (lines 41-44, same file).

**Precedent block** (lines 41-44 of current `pyproject.toml`):
```toml
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
```

**Pattern to mirror** — append the new group as a sibling, NOT colocate with `test` (D-01 forbids mixing AGPL + quality tooling):
```toml
[project.optional-dependencies]
test = [
    "pysweph>=2.10.3.6",
]
dev = [
    "interrogate>=1.7.0",
    "numpydoc>=1.10.0",
]
```

**Notes for the planner:**
- Pin floors (`>=`), not exact pins — matches the `pysweph>=2.10.3.6` convention already used in `test`.
- The `tests.yml` install verb `pip install -e ".[dev]" || pip install -e .` (line 28) starts succeeding the moment this group exists; no workflow edit is required for the install step itself (D-02).

---

### `pyproject.toml` — new `[tool.interrogate]` block

**Analog (exclusion list shape):** `[tool.coverage.run].omit` (lines 78-84).
**Analog (threshold shape):** `[tool.coverage.report].fail_under` (lines 86-93).

**Precedent block — exclusion list** (lines 78-84):
```toml
[tool.coverage.run]
source = ["ketu"]
omit = [
    "*/tests/*",
    "ketu/__main__.py",
    "ketu/lunar_calendar.py",
]
```

**Precedent block — fail-under threshold** (lines 86-93):
```toml
[tool.coverage.report]
fail_under = 70
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

**Pattern to mirror** — keep `lunar_calendar.py` in the exclusion list verbatim to align with coverage's `omit` (D-06, D-07). Use `fail-under = 95` (not 70 — interrogate threshold is set by OPS-01). Use `verbose = 1` so the score prints in green-build logs as a positive signal (CONTEXT Specifics):
```toml
[tool.interrogate]
fail-under = 95
exclude = [
    "ketu/lunar_calendar.py",   # mirrors [tool.coverage.run].omit (D-06)
    "tests",
    "build",
    "docs",
]
ignore-init-method = true
ignore-magic = true
ignore-nested-functions = true
ignore-private = false        # D-08: fix gaps, don't paper them over
ignore-semiprivate = false    # D-08: same — the 4 placidus _ra_formula_* helpers get docstrings
verbose = 1
style = "sphinx"
```

**Verified output with this config (audit pre-flight, 2026-05-08):** 98.2% — gate passes on first run after the 4 placidus docstrings land.

---

### `pyproject.toml` — new `[tool.numpydoc_validation]` block

**Analog (global config + per-object override pattern):** `[tool.mypy]` block (lines 96-120, same file).
**Analog (exclusion list shape):** `[tool.coverage.run].omit` (already cited above).

**Precedent block — `[tool.mypy]` global + per-module overrides** (lines 96-120):
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[[tool.mypy.overrides]]
module = ["swisseph.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = [
    "ketu.calculations",
    "ketu.complex",
    "ketu.cycles.*",
    ...
]
disable_error_code = ["misc", "no-untyped-def", ...]
```

**Pattern to mirror** — same "global config first, per-target override second" structure. Numpydoc uses regex strings in `exclude` (not module paths), and `override_<CODE>` keys for per-object lenience:
```toml
[tool.numpydoc_validation]
checks = [
    "all",   # report every check
    "EX01",  # ignore: no examples section required (internal helpers)
    "SA01",  # ignore: no See Also required
    "ES01",  # ignore: no extended summary required
    "GL01",  # ignore during warning phase (Phase 13–19); fix and remove in Phase 20
]
exclude = [
    '\.lunar_calendar$',   # mirrors [tool.coverage.run].omit
    '\._',                 # any object whose name starts with underscore
]
override_SS05 = [          # tolerant of dataclass docstrings (mypy-overrides analog)
    '^Aspect$',
    '^ZodiacPoint$',
    '^CycleRatio$',
]
```

**Notes for the planner:**
- The `override_SS05` pattern is structurally identical to `[[tool.mypy.overrides]]` — "global default, then surgical exceptions" — so reviewers already familiar with the mypy block will recognize the shape.
- `GL01` suppression note: the audit shows 59 GL01 hits (all in `complex.py` + `calculations.py`, summary-on-same-line as `"""`). Suppressing during the warning phase is **Option A** in the research; Option B (fix all 59 in Phase 13) would require deleting the `"GL01"` line. Default to Option A; planner can flip if user prefers.

---

### `.github/workflows/tests.yml` — new "Doc coverage gate (interrogate)" step

**Analog:** "Check coverage threshold" step (lines 41-44, same file) — same Python-version gating, same `python -m <tool>` invocation, same blocking posture.

**Precedent block** (lines 41-44):
```yaml
    - name: Check coverage threshold
      if: matrix.python-version == '3.13'
      run: |
        pytest tests/ --cov=ketu --cov-fail-under=70 -q
```

**Pattern to mirror** — same `if:` gate, same `python -m` form. Insert AFTER the existing coverage step, BEFORE the Codecov upload step (lines 46-50):
```yaml
    - name: Doc coverage gate (interrogate ≥95%)
      if: matrix.python-version == '3.13'
      run: |
        python -m interrogate ketu/
```

**Why no `--fail-under=95` flag on the CLI:** the `[tool.interrogate]` block in `pyproject.toml` already sets `fail-under = 95`. Single source of truth. Mirrors the way coverage threshold lives in `pyproject.toml` `[tool.coverage.report].fail_under = 70` rather than being duplicated in the workflow.

**Why no separate install step:** `interrogate` lands via `pip install -e ".[dev]"` (line 28). The existing install step covers it.

---

### `.github/workflows/tests.yml` — new "Doc style audit (numpydoc)" step

**Analog (Python-version gating):** "Type check" step (lines 35-39, same file).
**Analog (3.13-only gating + invocation form):** "Check coverage threshold" step (lines 41-44).

**Precedent block — "Type check"** (lines 35-39):
```yaml
    - name: Type check
      if: matrix.python-version == '3.11'
      run: |
        pip install mypy
        mypy ketu/ --strict
```

**Pattern to mirror** — same `if:` gate (but on 3.13, matching the doc-gates' Python target), `python -m` invocation form, plus a new ingredient (`continue-on-error: true`) that has no in-repo precedent and is the warning-posture knob locked by D-04:
```yaml
    - name: Doc style audit (numpydoc — warning only, blocking from v1.2.0)
      if: matrix.python-version == '3.13'
      continue-on-error: true
      run: |
        FILES=$(find ketu -name "*.py" \
            ! -path "*/__pycache__/*" \
            ! -name "lunar_calendar.py" \
            ! -name "_*.py")
        echo "Validating $(echo "$FILES" | wc -l) files..."
        python -m numpydoc lint $FILES
```

**Notes for the planner:**
- `continue-on-error: true` is new to this workflow — there is no existing analog. The locked decision D-04 is the source. Pitfall 4 in `13-RESEARCH.md` documents the UX caveat ("step shows green checkmark even when warnings present") and Phase 20 must flip it.
- File globbing via `find` is the same shell idiom Sophie uses in `Makefile:houses-coverage` (which uses `coverage report --include='ketu/houses/*'` — a parallel "subset of `ketu/`" filtering pattern).

---

### `Makefile` — optional new `doc-gates` target

**Analog:** `houses-coverage` target (lines 21-39, same file) — same help-comment convention, same `.PHONY` registration, same `$(PYTHON) -m <tool>` invocation.

**Precedent block** (lines 21-39):
```makefile
.PHONY: test test-fast houses-coverage mypy clean

## houses-coverage: Run the HOU-09 ≥95% coverage gate scoped to ketu.houses.
##
## This is a separate invocation from the project-wide `pytest tests/` so
## a partial test run (e.g. `pytest tests/test_ephemeris.py`) cannot
## silently miss the gate.
##
## Two-step pattern. [...]
houses-coverage:
	$(PYTHON) -m pytest tests/houses/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/houses/*' --fail-under=95 -m
```

**Pattern to mirror** — same `## name: description` help-comment header (the project's documented convention), add `doc-gates` to the `.PHONY` line, same `$(PYTHON) -m` invocation form:
```makefile
.PHONY: test test-fast houses-coverage doc-gates mypy clean

## doc-gates: Run the doc-gate suite locally (interrogate + numpydoc lint).
##
## Mirrors what CI runs in tests.yml. Use before pushing to avoid
## learning about a gate failure from the GitHub Actions email.
doc-gates:
	$(PYTHON) -m interrogate ketu/
	$(PYTHON) -m numpydoc lint $$(find ketu -name "*.py" \
	    ! -path "*/__pycache__/*" \
	    ! -name "lunar_calendar.py" \
	    ! -name "_*.py") || true
	@echo "Doc gates OK (numpydoc warnings shown above; not blocking until v1.2.0)."
```

**Notes for the planner:**
- The `|| true` on the numpydoc line is the local equivalent of `continue-on-error: true` in the workflow — keeps `make doc-gates` from exiting non-zero on warnings during the warning phase. Phase 20 removes it when numpydoc flips to blocking.
- Open Question 1 in research: "ship `doc-gates` or not?" Recommendation: **ship it.** The Makefile precedent is set; the cost is ~10 lines.

---

### `ketu/houses/placidus.py` — 4 missing docstrings on `_ra_formula_cusp_2/3/11/12`

**Analogs (shape):** `_iterate_cusp_ra` (lines 114-150, same file) and `ra_to_lambda` in `ketu/houses/_ecliptic.py` (lines 15-47).

**Precedent block — sibling function with full numpydoc docstring** (`placidus.py` lines 114-150):
```python
def _iterate_cusp_ra(
    armc: np.ndarray,
    lat: np.ndarray,
    eps: np.ndarray,
    cusp_number: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Solve for the right ascension of a Placidus iterated cusp.

    Mask-based fixed-point iteration: at each step, only elements that
    [...]

    Parameters
    ----------
    armc : np.ndarray
        Right Ascension of the Medium Coeli, degrees.
    lat : np.ndarray
        Geographic latitude, degrees.
    [...]

    Returns
    -------
    ra : np.ndarray
        Right ascension of the cusp, degrees, ``[0, 360)``. ``NaN`` where
        the iteration did not converge or the polar boundary was hit.
    [...]
    """
```

**Current state of the 4 helpers** (`placidus.py` lines 82-95) — no docstrings:
```python
def _ra_formula_cusp_11(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_12(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 2.0 * (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_2(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 180.0 - 2.0 * (90.0 - AD) / 3.0) % 360.0


def _ra_formula_cusp_3(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    return (armc + 180.0 - (90.0 - AD) / 3.0) % 360.0
```

**Module-level comment on lines 73-79 already documents the formulas as a group** — the per-function docstrings can be one-line summaries that point back at the table:

**Pattern to apply** (one-line summary, no Parameters/Returns sections — interrogate just needs *a* docstring; the surrounding module docstring + the `_CUSP_FORMULAS` dispatch table on line 100 already carry the substantive doc):
```python
def _ra_formula_cusp_11(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    """RA of Placidus cusp 11: ``ARMC + (90 + AD) / 3`` (mod 360)."""
    return (armc + (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_12(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    """RA of Placidus cusp 12: ``ARMC + 2 * (90 + AD) / 3`` (mod 360)."""
    return (armc + 2.0 * (90.0 + AD) / 3.0) % 360.0


def _ra_formula_cusp_2(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    """RA of Placidus cusp 2: ``ARMC + 180 - 2 * (90 - AD) / 3`` (mod 360)."""
    return (armc + 180.0 - 2.0 * (90.0 - AD) / 3.0) % 360.0


def _ra_formula_cusp_3(armc: np.ndarray, AD: np.ndarray) -> np.ndarray:
    """RA of Placidus cusp 3: ``ARMC + 180 - (90 - AD) / 3`` (mod 360)."""
    return (armc + 180.0 - (90.0 - AD) / 3.0) % 360.0
```

**Why one-liners are sufficient here:**
1. The module docstring (lines 1-46) already documents these as a unit ("Per-cusp scaling table").
2. Numpydoc isn't run on `_*` private names (D-06 + the `\._` regex in `[tool.numpydoc_validation].exclude`) — so the docstring only needs to satisfy `interrogate` (presence check), not numpydoc (style check). Interrogate's `ignore-private = false` (D-08) is what surfaces them as gate failures.
3. The 4 helpers have identical signatures and trivial bodies — a 4-line numpydoc block per function would be 80% boilerplate noise. The dispatch table on line 100 (`_CUSP_FORMULAS = {11: _ra_formula_cusp_11, ...}`) is where a future reader looks for the "which function does what" question.

**Anti-pattern to avoid:** Suppressing these via `ignore-semiprivate = true` in the interrogate config. D-08 forbids it. 4 one-line docstrings is faster than thinking about the suppression.

---

### `ketu/complex.py`, `ketu/calculations.py`, `ketu/cycles/calculator.py` — numpydoc fixes (bulk)

**Analog:** `ketu/houses/_ecliptic.py` (full file, ~80 lines) and `ketu/houses/placidus.py:_iterate_cusp_ra` (lines 114-150) — already-clean numpydoc style in the same project, both shown above.

**Audit baseline (from research, verified live 2026-05-08):**
- `complex.py` — 124 numpydoc issues (largest single bucket)
- `calculations.py` — 68 issues
- `cycles/calculator.py` — 22 issues
- `__init__.py` — 6 issues (GL06/GL07 — non-standard sections "Submodules", "Precision Guarantees", etc.)
- `display.py` — 5 issues
- `core.py` — 3 issues (GL06/GL07 — "Data Structures" section)

**Pattern category 1 — GL01 (summary line on same line as `"""`).** Largest mechanical bucket (~59 hits). Current shape in `complex.py` line 79-80:
```python
def from_degrees(cls, name: str, degrees: float, orb: float = 8.0) -> Aspect:
    """Create an aspect from degrees   <-- summary on same line as opening triple-quote
```
**Numpydoc-compliant shape (already used in `_ecliptic.py:ra_to_lambda` line 16):**
```python
def ra_to_lambda(ra: np.ndarray, eps: np.ndarray) -> np.ndarray:
    """Convert right ascension on the ecliptic to ecliptic longitude.   <-- ends with period

    For a point on the ecliptic [...]
    """
```
Two mechanical changes per occurrence: (a) trailing period on the summary line, (b) blank line before the body. Editor regex: `s/"""([A-Z][^"\n.]+)$/"""\1./` (add trailing period if absent). **Recommendation:** suppress GL01 in `[tool.numpydoc_validation]` during the warning phase per Option A in research; fix mechanically in Phase 20.

**Pattern category 2 — GL06/GL07 (non-standard section names).** Affects `__init__.py` (lines 7-45) and `core.py` (lines 7-34). Current shape:
```rst
Submodules
----------
ketu.core
    Astronomical constants...

Precision Guarantees
--------------------
- Angular separation: ±1e-6° ...
```
**Numpydoc-compliant shape — fold into `Notes`:**
```rst
Notes
-----
**Submodules**

ketu.core
    Astronomical constants...

**Precision Guarantees**

- Angular separation: ±1e-6° ...
```
Single edit per file: rename top-level `Submodules`/`Precision Guarantees`/`Coordinate Transformations`/`Body IDs`/`Data Structures` headings into bold sub-paragraphs under one `Notes` section. The existing `Examples` section in `__init__.py` (line 46) already follows the numpydoc convention — leave it.

**Pattern category 3 — PR01 (parameter documented but not in signature) and RT01 (missing Returns section).** ~14 substantive hits across `complex.py`/`calculations.py`/`cycles/calculator.py`. The fix is real writing: add the missing `Parameters`/`Returns` blocks using the shape already used in `_ecliptic.py:ra_to_lambda` (lines 22-34) and `placidus.py:_iterate_cusp_ra` (lines 129-150). Don't suppress these — they catch real gaps.

**Pattern category 4 — GL08 (truly missing docstrings, ~4 in `complex.py` on `__post_init__`/`__repr__`).** These overlap with interrogate's `ignore-magic = true` (so interrogate doesn't see them) but numpydoc does. Either add a one-line summary or leave them — numpydoc's default is to flag them; we've already chosen to suppress dunders in the interrogate config. **Recommendation:** add a one-line summary; takes 30 seconds per dunder.

**Notes for the planner:**
- The fix-pass should be one plan (Plan 3 in the research's recommended sequence) chunked file-by-file inside the plan. Don't split into 5 plans — the merge surface stays smaller as one plan.
- After Plan 3, `python -m numpydoc lint $FILES --ignore SA01 EX01 ES01 GL01` should produce zero output. That's the regression check.
- No signature changes, no behavior changes — pure docstring edits. The 250 existing tests must stay green (they will: docstrings are runtime no-ops outside `__doc__` access).

---

### `CHANGELOG.md` and `README.md` — positive-add of "enforced by CI" wording

**Analog (README narrative voice):** README "Documentation" section (lines 226-237) and "Requirements" section (lines 239-244).
**Analog (CHANGELOG entry shape):** `### Added` sub-section under `## [1.1.0]` (line 59 onward).

**Aspirational-refs audit result (verified live 2026-05-08):** Zero hits in CHANGELOG, README, CONTRIBUTING, UPGRADING, docs/source/ for `interrogate`, `numpydoc`, `≥95%`. **The "reformulation pass" is not a rewrite — it's a positive-add.**

**Precedent block — README "Documentation" section** (lines 226-237):
```markdown
## Documentation

The full documentation is hosted on [Read the Docs](https://ketu.readthedocs.io).

Included sections:

- **Installation**: detailed setup instructions
- **Quickstart**: guided tour of the basics
- **Concepts**: astrological and astronomical background
- **API Reference**: all functions documented
- **Examples**: advanced usage patterns
- **Developer Guide**: architecture and performance details
```

**Pattern to mirror** — append a short paragraph in this same voice, either at the end of the existing "Documentation" section or in a new "Quality Gates" sub-section just above "Roadmap" (line 316). Suggested wording (Sophie voice — concise, factual):
```markdown
### Documentation Quality Gates

Documentation quality is enforced by CI on every push:

- **`interrogate ≥95%`** (blocking) — every public function, class, and module has a docstring.
- **`numpydoc validate`** (warning, blocking from v1.2.0) — docstrings follow the NumPy convention.

Run both locally before pushing: `make doc-gates`.
```

**Precedent block — CHANGELOG `### Added` shape under `## [1.1.0]`** (line 59 onward):
```markdown
### Added

- **`ketu.houses` module** — Placidus, Koch, and Porphyry house systems
  registered through a `@register("name")` decorator [...]. (HOU-02 .. HOU-10)
```

**Pattern to mirror** — same `### Added` heading, same `- **<thing>** — <description>. (<requirement-IDs>)` entry shape. The Phase 13 entry lives under the `## [Unreleased]` or `## [1.2.0]` heading (whichever the milestone-tracking flow uses). Suggested wording:
```markdown
### Added

- **CI doc-quality gates** — `interrogate ≥95%` (blocking) and
  `numpydoc validate` (warnings, blocking from v1.2.0) are now wired
  into `tests.yml`. New `[project.optional-dependencies].dev` group
  installs both tools (`pip install -e .[dev]`); `make doc-gates`
  runs the full suite locally. (OPS-01, OPS-02)
```

**Notes for the planner:**
- D-12: `.planning/` files (STATE, MILESTONES, PROJECT) are NOT touched in this Phase 13 reformulation pass — they update through the normal `update_state` flow.
- D-13: No new aspirational claims. Every claim added by Plan 5 is backed by code that has already landed in Plans 1-4.
- The CHANGELOG entry references `OPS-01` and `OPS-02` to close traceability — same convention as the existing `(HOU-02 .. HOU-10)` and `(Phase 9 / ASP-04)` references on lines 21, 30, 43, 57, 69 of CHANGELOG.

---

## Shared Patterns

### Shared Pattern 1 — Python-version gating in `tests.yml`

**Source:** `.github/workflows/tests.yml` lines 35-36 (`Type check` on 3.11) and lines 41-42 (`Check coverage threshold` on 3.13).

**Apply to:** Both new doc-gate steps. Both run on 3.13 only (matches coverage; doc style is Python-version-independent and we don't pay 4× the runtime).

**Excerpt:**
```yaml
    - name: <step name>
      if: matrix.python-version == '3.13'
      run: |
        python -m <tool> ketu/
```

**Anti-pattern:** Running the gates on every matrix leg. Wasteful; doc style does not depend on the Python interpreter version. Mirror the existing version-gating discipline.

---

### Shared Pattern 2 — `lunar_calendar.py` exclusion

**Source:** `pyproject.toml` `[tool.coverage.run].omit` line 83 (`"ketu/lunar_calendar.py"`).

**Apply to:** Both new `[tool.interrogate].exclude` and `[tool.numpydoc_validation].exclude`.

**Excerpt:**
```toml
# in [tool.coverage.run]
omit = [
    "*/tests/*",
    "ketu/__main__.py",
    "ketu/lunar_calendar.py",   # <-- this line is the precedent
]
```

**Why mirror:** `lunar_calendar.py` is treated as legacy/unmaintained surface in this project. All three quality tools (coverage, interrogate, numpydoc) should agree on this. D-06 + D-07 explicitly require alignment.

---

### Shared Pattern 3 — `python -m <tool>` invocation form

**Source:** `Makefile` line 9 (`PYTHON ?= python`) + every Make target (lines 14-49) + the comment at the top of the Makefile explaining the choice (lines 1-7):
> "All recipes invoke pytest/mypy through `python -m` so they pick up the active venv (or the venv at `./venv`) — direct `pytest`/`mypy` shebangs in this repo's `venv/bin/` were observed to mis-resolve in some environments."

**Apply to:** Every new tool invocation in `tests.yml` AND in `Makefile`. Use `python -m interrogate`, `python -m numpydoc lint`, NOT bare `interrogate`/`numpydoc`.

**Excerpt:**
```makefile
$(PYTHON) -m pytest tests/
$(PYTHON) -m coverage report --include='ketu/houses/*' --fail-under=95 -m
$(PYTHON) -m mypy --strict ketu/
```

**Why mirror:** Documented project convention with a known reason (shebang drift in the in-tree venv). New code that invokes a tool via its bare name would regress this fix.

---

### Shared Pattern 4 — Numpydoc-style docstring shape

**Source:** `ketu/houses/_ecliptic.py:ra_to_lambda` (lines 15-47) and `ketu/houses/placidus.py:_iterate_cusp_ra` (lines 114-150).

**Apply to:** Every docstring added or repaired in `ketu/complex.py`, `ketu/calculations.py`, `ketu/cycles/calculator.py`.

**Canonical shape (the project's numpydoc dialect):**
```python
def function_name(arg1: T1, arg2: T2) -> ReturnT:
    """One-line imperative summary ending with a period.

    Optional extended description, free-form, can span multiple
    paragraphs. Use ``double-backticks`` for inline code; use
    :func:`module.func` for cross-references.

    Parameters
    ----------
    arg1 : T1
        Description of arg1.
    arg2 : T2
        Description of arg2, possibly multi-line. Use the same indent.

    Returns
    -------
    name : ReturnT
        Description of the return value. Name optional but Sophie-flavored.

    Notes
    -----
    Optional. Use for non-trivial caveats, references to research docs,
    or for folding non-standard sections (Submodules, Data Structures, etc.)
    that would otherwise trigger GL06/GL07.
    """
```

**Why this exact shape:** It's what already passes the gate everywhere in `ketu/houses/` (the cleanest-currently subtree per audit). Mirroring it produces zero new numpydoc warnings in the repaired files.

---

## No Analog Found

None. Every modification in Phase 13 has a concrete in-repo precedent. The one element with **no** in-repo precedent is `continue-on-error: true` in the new numpydoc step — but that flag is locked by D-04 and documented in the research (Pitfall 4); the planner does not need to invent it.

---

## Metadata

**Analog search scope:**
- `/home/loc/workspace/ketu/pyproject.toml` (full)
- `/home/loc/workspace/ketu/.github/workflows/tests.yml` (full)
- `/home/loc/workspace/ketu/Makefile` (full)
- `/home/loc/workspace/ketu/ketu/houses/placidus.py` (full)
- `/home/loc/workspace/ketu/ketu/houses/_ecliptic.py` (lines 1-80, sufficient — clean numpydoc throughout)
- `/home/loc/workspace/ketu/ketu/__init__.py` (lines 1-100)
- `/home/loc/workspace/ketu/ketu/core.py` (lines 1-80, GL06/GL07 sample)
- `/home/loc/workspace/ketu/ketu/complex.py` (lines 1-120, GL01/GL08 sample)
- `/home/loc/workspace/ketu/ketu/calculations.py` (lines 1-100, GL01/PR01/RT01 sample)
- `/home/loc/workspace/ketu/ketu/cycles/calculator.py` (lines 1-80, GL01 sample)
- `/home/loc/workspace/ketu/CHANGELOG.md` (sections + lines 1-75)
- `/home/loc/workspace/ketu/README.md` (sections + key blocks at 226-244, 316-340)

**Files scanned:** 12

**Pattern extraction date:** 2026-05-08

**Notes for the planner:**
- Every Plan 1-5 task in the research's recommended sequence has a concrete excerpt to mirror. The plans should reference this map by section heading (e.g., "see PATTERNS.md § `pyproject.toml — new [tool.interrogate] block`") rather than re-quoting the precedent.
- The two patterns *without* an in-repo precedent — `continue-on-error: true` and the `[tool.numpydoc_validation].override_<CODE>` mechanism — are explicitly called out above. Both are locked by decisions/research; no design work is needed.
