# Phase 13: Doc Gates & CI Foundation - Research

**Researched:** 2026-05-08
**Domain:** Python documentation tooling (interrogate + numpydoc) wired into GitHub Actions CI for a NumPy-first scientific library
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Optional-dependencies layout
- **D-01:** Add a new `dev` group: `[project.optional-dependencies].dev = ["interrogate>=…", "numpydoc>=…"]`. Do NOT colocate with `test = ["pysweph"]` — `test` holds an AGPL dep and we keep that boundary clean.
- **D-02:** `tests.yml` already runs `pip install -e ".[dev]" || pip install -e .` — that command works as soon as the `dev` group exists; the fallback can stay (defensive).
- **D-03:** `dev` group is the right home even though the gates run in CI: it keeps the install verb intuitive (`pip install -e .[dev]`) for contributors running the gates locally before pushing.

#### `numpydoc validate` posture and scope
- **D-04:** Phase 13 lands `numpydoc validate` as **non-blocking warnings** in CI (errors surface in build log, build still succeeds).
- **D-05:** Gate flips to **blocking** in Phase 20 (release prep). Phase 20's plan must include a "flip numpydoc to blocking" step explicitly.
- **D-06:** Public scope for `numpydoc validate` = everything under `ketu/` **except** modules/files starting with `_` and `ketu/lunar_calendar.py`.
- **D-07:** `interrogate` scope follows the same exclusion list (no `_*`, no `lunar_calendar.py`). The interrogate config goes in `[tool.interrogate]` inside `pyproject.toml`.

#### Baseline cleanup (v1.1 → clean)
- **D-08:** Any pre-existing docstring gap surfaced by `interrogate` or `numpydoc validate` is **fixed in this phase, not deferred**. Phase 13 does not merge until both gates run green on the in-scope surface.
- **D-09:** Audit step is the first task: enumerate every public function/class/module that fails either gate, classify, and bound the work before writing fixes.
- **D-10:** Modules at higher-than-average legacy risk: `calculations.py`, `complex.py`, top-level `__init__.py` re-exports.

#### Aspirational references cleanup (OPS-01 / OPS-02 final closure)
- **D-11:** Once CI is green, every public-doc mention of "interrogate ≥95%" / "numpydoc validate" is reformulated to "**enforced by CI** (`tests.yml`)". Files to sweep: `CHANGELOG.md`, `README.md`, any reference under `docs/`.
- **D-12:** `.planning/` files are NOT touched in this phase's reformulation pass.
- **D-13:** No new aspirational claims are added in Phase 13.

### Claude's Discretion (researcher resolves below)
- Pin versions or use floor `>=X.Y` for `interrogate` and `numpydoc` — researched, recommendation in Standard Stack.
- Whether `numpydoc validate` runs as a separate CI step or piggybacks on `Type check` — researched, recommendation in Architecture Patterns.
- Order of fix-up commits inside Phase 13 — recommended sequence in Architecture Patterns.
- Exact `[tool.interrogate]` and `[tool.numpydoc_validation]` configuration knobs — recommended config in Code Examples.

### Deferred Ideas (OUT OF SCOPE)
- Sphinx `-W` warnings as build gate.
- Pre-commit hook for interrogate.
- `fr/CHANGELOG.md` reformulation pass (OPS-04 — Phase 20).
- Tightening project-wide coverage `fail_under` from 70 to 90.
- Per-module numpydoc severity overrides (only if warning-phase noise demands it).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| OPS-01 | `interrogate ≥95%` installé en `[project.optional-dependencies]` (test-only) et wiré dans CI ; échoue le build si en dessous du seuil | `[VERIFIED: live audit on this codebase]` baseline = 98.2% with ignore-init-method/magic/nested-functions and `lunar_calendar.py` excluded; only **4 missing module-level docstrings** in `houses/placidus.py` need writing to clear the gate. Pre-flight invocation, recommended `[tool.interrogate]` block, and CI step shape provided in Code Examples. Note: REQUIREMENTS.md says "test-only" but the locked decision (D-01) supersedes this — the group is named `dev`, not `test`, to preserve the AGPL boundary. |
| OPS-02 | `numpydoc validate` wiré dans CI sur les modules publics ; warnings non-bloquants au début, gate à activer en fin de milestone | `[VERIFIED: live audit on this codebase]` baseline = 231 issues (with community-default suppressions SA01/EX01/ES01) concentrated in 3 modules: `complex.py` (124), `calculations.py` (68), `cycles/calculator.py` (22). 80%+ of issues are mechanical (missing trailing periods, summary-on-same-line). Recommended config (`[tool.numpydoc_validation]`), CI step shape with `continue-on-error: true`, and warning→blocking flip recipe provided. |
</phase_requirements>

## Summary

Phase 13 wires two off-the-shelf, production-ready tools (`interrogate` and `numpydoc`) into the existing GitHub Actions matrix. Both tools are mature scientific-Python ecosystem citizens — `interrogate` powers docstring-coverage gates in projects like Mars, sktime, and Apache Beam; `numpydoc validate` is what NumPy and SciPy themselves use to police docstring style. Wiring them is well-trodden territory; the work in this phase is **almost entirely the audit-and-fix pass**, not the CI plumbing.

A live pre-flight audit on the current `ketu/` codebase (Python 3.13.5, in-tree venv) gives precise sizing:

- **interrogate baseline:** 93.8% with default settings → **98.2% with the recommended `--ignore-init-method --ignore-magic --ignore-nested-functions` configuration and `lunar_calendar.py` excluded**. The 4 remaining misses are all module-level helpers in `houses/placidus.py` (`_ra_formula_cusp_2/3/11/12`). Adding 4 one-line docstrings clears the ≥95% gate. **No `--ignore-semiprivate` or `--ignore-private` is needed** — D-08 says fix gaps, not paper them over, and these are 4-line trivial fixes.
- **numpydoc baseline:** 231 issues across 9 files (with the SciPy-community default suppressions SA01/EX01/ES01). 124/231 are in `complex.py` alone. 80%+ of issues are mechanical period/summary-line fixes auto-fixable with editor regex; only 4 truly-missing docstrings (GL08) and ~14 substantive (PR01 missing param docs, RT01 missing Returns section, GL06/GL07 non-standard section names in `__init__.py` and `core.py`). All in D-10's flagged risk modules — confirming Sophie's instinct.
- **Aspirational refs:** **Zero hits** in `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`, `UPGRADING.md`, or `docs/source/` for `interrogate`, `numpydoc`, or `≥95%`. The aspirational claims live exclusively in `.planning/` (PROJECT, MILESTONES, STATE, ROADMAP), which D-12 explicitly excludes from the reformulation pass. **The reformulation task per D-11 is effectively a no-op verify-only audit** — confirm zero public-doc claims, document the result, move on.

**Primary recommendation:** Pin floors (`interrogate>=1.7.0`, `numpydoc>=1.10.0`), run both gates as **two separate CI steps** on Python 3.13 only (matches existing version-gating for coverage and mypy), use `continue-on-error: true` for the numpydoc step, and use `verbose = 1` in interrogate config so the score prints in green-build logs as a positive signal. The audit-and-fix pass is the load-bearing work — budget it as **2 commits/plans dedicated to docstring fixes** (one for `complex.py`, one for `calculations.py` + `cycles/calculator.py` + `__init__.py` + `core.py`), not the CI wiring.

## Architectural Responsibility Map

This phase is pure CI / build-tooling work — no library API surface changes, no runtime tier owners. The capability map is unconventional but useful for sanity-checking task placement:

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Docstring coverage measurement | Build / CI tooling | — | `interrogate` runs in CI as a quality gate; never imported by library code |
| Docstring style validation | Build / CI tooling | — | `numpydoc lint` runs in CI as a (warning) quality gate |
| Tool installation declaration | Package metadata (`pyproject.toml`) | — | `[project.optional-dependencies].dev` |
| Tool configuration | Package metadata (`pyproject.toml`) | — | `[tool.interrogate]` and `[tool.numpydoc_validation]` |
| CI step orchestration | GitHub Actions workflow (`.github/workflows/tests.yml`) | — | Two new steps gated to Python 3.13 only |
| Source-level docstring fixes | Library source (`ketu/`) | — | Edits to docstrings only — **no signature, behavior, or export changes** (non-breaking minor strict per cross-cutting constraint) |
| Public-doc reformulation | Public docs (`CHANGELOG.md`, `README.md`, `docs/`) | — | Audit-only — confirmed empty per D-11 sweep below |

**Why this matters:** The temptation in a "doc gates" phase is to creep into Sphinx config, RST polish, or contributor-facing docs. The locked scope (CONTEXT.md `<domain>`) confines this phase to **CI tooling + source docstring repair + public-claim reformulation**. Anything else (Sphinx `-W`, pre-commit hooks, French CHANGELOG) is in `<deferred>` for a reason.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `interrogate` | `>=1.7.0` | Docstring coverage measurement (every public function/class/module is documented?) | De facto Python docstring-coverage tool; `pyproject.toml`-native config; clean exit codes for CI gating. `[VERIFIED: PyPI release 2024-04-07]`. Runs cleanly on Python 3.13.5 in this repo's venv despite classifiers stopping at 3.12 — bytecode-forward-compat. |
| `numpydoc` | `>=1.10.0` | Docstring **style** validation (NumPy convention: param tables, Returns sections, etc.) — used via `python -m numpydoc lint <files>` | This is what NumPy and SciPy themselves use to police docstring style. AST-based `lint` subcommand needs no import — won't break on import-time side effects. `[VERIFIED: PyPI release 2025-12-02]`. Requires Python ≥3.10 (matches Ketu's matrix exactly). |

**Pin floors, not exact versions** — both packages are mature with stable CLIs and configuration shapes. Floors avoid pinning churn while protecting against pre-1.7/pre-1.10 bugs (interrogate 1.6 had a `ignore-overloaded-functions` regression; numpydoc 1.9 changed `lint` semantics). `[VERIFIED: PyPI versions list, 2026-05-08]`.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `sphinx` | (transitive) | Required by `numpydoc` (>=6) | Already installed in dev environment via `docs/requirements-docs.txt` — no new install footprint |
| `tomli` | (transitive, conditional) | TOML parsing for Python <3.11 | Pulled in for the 3.10 leg of the matrix; harmless |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `interrogate` | `docstr-coverage` | Older, less active maintenance, no `pyproject.toml` config block. Reject — interrogate is the modern choice. |
| `numpydoc lint` | `pydocstyle` (D-codes) | Different style family (PEP-257-centric, not NumPy). Wrong fit — Ketu already uses NumPy-style docstrings throughout. |
| `numpydoc lint` | `ruff D-codes` | Ruff is faster but enforces pydocstyle, not numpydoc-style. Wrong fit. |
| `numpydoc validate` (single object) | `numpydoc lint` (multi-file AST) | `validate` requires importing the object (side effect risk); `lint` walks AST without importing. **Use `lint`.** `[VERIFIED: ran both during audit]`. |

**Installation (added to `pyproject.toml`):**
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

**Version verification (run on 2026-05-08):**
```bash
$ pip index versions interrogate
interrogate (1.7.0)
  LATEST:    1.7.0  # released 2024-04-07

$ pip index versions numpydoc
numpydoc (1.10.0)
  LATEST:    1.10.0  # released 2025-12-02
```

`[VERIFIED: pip index versions, executed in this session]`

## Architecture Patterns

### System Diagram (CI flow)

```
┌─────────────────────────────────────────────────────────────────┐
│ .github/workflows/tests.yml — push/PR/manual trigger            │
│                                                                  │
│  matrix: {3.10, 3.11, 3.12, 3.13}                               │
│  │                                                               │
│  ├─→ checkout @v4 ─→ setup-python ─→ pip install -e .[dev]      │
│  │                                                               │
│  ├─→ Run tests           (all matrix)                           │
│  ├─→ Type check          (3.11 only)                            │
│  ├─→ Coverage threshold  (3.13 only)                            │
│  ├─→ ★ NEW Doc gate (interrogate)  (3.13 only, BLOCKING)        │
│  ├─→ ★ NEW Style gate (numpydoc)   (3.13 only, WARNING)         │
│  └─→ Codecov upload      (3.13 only)                            │
└─────────────────────────────────────────────────────────────────┘
                                          │
              ┌───────────────────────────┴───────────────────────┐
              ▼                                                    ▼
   pyproject.toml ── reads config ──→ [tool.interrogate]   [tool.numpydoc_validation]
              │                       fail-under = 95       checks = ["all", SA01,
              │                       exclude = [_*, lunar_calendar]   EX01, ES01, ...]
              │                                              exclude = [^ketu\._]
              ▼
       ketu/ source tree ── docstrings checked against both gates
```

**Data flow:** Both gates read `pyproject.toml` for config, walk `ketu/` excluding `lunar_calendar.py` and `_*` modules. Interrogate exits non-zero on <95% coverage (build fails). Numpydoc-lint exits non-zero on any unsuppressed issue, but the workflow step has `continue-on-error: true` so the build continues — issues surface in the Actions log without halting.

### Recommended Project Structure

No new directories — this phase touches only existing files:

```
ketu/                       # docstring repairs (audit-driven)
├── __init__.py             # GL06/GL07 fixes — non-standard sections → Notes
├── core.py                 # GL06/GL07 — same pattern as __init__.py
├── calculations.py         # ~68 numpydoc issues, ~0 interrogate (audit confirmed)
├── complex.py              # ~124 numpydoc issues, 4 interrogate misses (__post_init__, __repr__)
├── cycles/calculator.py    # ~22 numpydoc issues
├── display.py              # ~5 numpydoc issues
├── houses/placidus.py      # 4 interrogate misses (_ra_formula_cusp_2/3/11/12)
└── ... (other modules — clean)

pyproject.toml              # add [project.optional-dependencies].dev,
                            # [tool.interrogate], [tool.numpydoc_validation]

.github/workflows/tests.yml # add 2 CI steps (interrogate blocking, numpydoc warning)

CHANGELOG.md, README.md, docs/source/  # confirmed empty for aspirational refs (D-11 verify-only)
```

### Pattern 1: Two-Step CI Gating (separate, not piggybacked)

**What:** Run interrogate and numpydoc as two distinct workflow steps, both gated to Python 3.13 only (matches existing coverage/mypy version-gating).

**When to use:** Always, for both speed and signal-to-noise reasons. Piggybacking onto the existing `Type check` step (3.11) is rejected because (a) the `Type check` step's success/failure is then ambiguous when one of three sub-tools breaks, (b) Codecov upload patterns expect a clean per-step summary on the Actions tab, (c) GitHub Actions step-level annotations work best one-tool-per-step.

**Example:**
```yaml
# Source: pattern adapted from the existing tests.yml Coverage step
# (lines 41-44, gating with `if: matrix.python-version == '3.13'`)
- name: Doc coverage gate (interrogate ≥95%)
  if: matrix.python-version == '3.13'
  run: |
    python -m interrogate ketu/ --fail-under=95 -v
    # -v prints the per-file table → score visible in green-build logs

- name: Doc style audit (numpydoc — warning only)
  if: matrix.python-version == '3.13'
  continue-on-error: true
  run: |
    python -m numpydoc lint $(find ketu -name "*.py" \
        ! -path "*/__pycache__/*" \
        ! -name "lunar_calendar.py" \
        ! -name "_*.py")
```

`[VERIFIED: invocation tested in venv, both commands produce expected output]`

### Pattern 2: Recommended fix-up commit sequence (planner consumes this)

**What:** Phase 13 has 5 conceptual stages. They map naturally to **5 plans** with clear merge gates between them:

1. **Plan 1 — Add `dev` group + `[tool.interrogate]` config + audit baseline.** Land the `pyproject.toml` changes. Run `interrogate ketu/` locally; commit the score (98.2% with config, see audit). No CI changes yet — work locally first so we can iterate without burning CI cycles.
2. **Plan 2 — Wire interrogate into CI as BLOCKING (already passing).** Add the workflow step. CI run #1 must pass green on first push (it will: 98.2% > 95%). The commit message says "interrogate gate now enforced by CI" — this is the wording landed by D-11.
3. **Plan 3 — Add `[tool.numpydoc_validation]` config + audit baseline + fix all gaps.** This is the load-bearing plan. Work file-by-file: `complex.py` first (124 issues), then `calculations.py` (68), `cycles/calculator.py` (22), `__init__.py`/`core.py` (GL06/GL07 section renames), `display.py` (5). Verify locally with `python -m numpydoc lint ... --ignore SA01 EX01 ES01` until clean. Don't wire CI yet — keep iteration cheap.
4. **Plan 4 — Wire numpydoc into CI as WARNING (already clean, but warning posture is the locked decision).** Add the workflow step with `continue-on-error: true` per D-04. The "already clean" baseline ensures the build log is quiet on first push, which is what makes warning posture useful in Phases 14–19 (any new noise = a new gap).
5. **Plan 5 — Reformulation pass + traceability close.** Verify (already-confirmed) zero hits in CHANGELOG/README/docs for "interrogate"/"numpydoc"/"≥95%". Add a short paragraph to README explaining the gates ("Doc gates: `interrogate ≥95%` (enforced by CI) and `numpydoc validate` (warnings, blocking from v1.2.0)" — see Specifics in CONTEXT.md). Update `update_state` flow per D-12 boundary. Mark OPS-01/OPS-02 done.

**Why this sequence:** Each plan ends in a green CI state. Plans 1+3 do offline work (no CI), Plans 2+4 wire it. Audit→fix→wire (not wire→audit→fix) means the gates are never seen failing in the build log — first impression matters for contributors. Order is enforced by dependencies, not by aesthetic preference.

### Anti-Patterns to Avoid

- **Wiring before fixing.** Tempting because "the gate will tell us what's broken." But CI failures during the audit period are confusing and don't match the locked posture (interrogate is **blocking** from D-04 — no "let it fail for a while" period).
- **Using `--ignore-semiprivate` to paper over the 4 placidus helpers.** D-08 says fix gaps. Adding 4 one-line docstrings to `_ra_formula_cusp_*` is faster than thinking about whether to suppress, and aligned with the "no exclusion of internal-but-still-callable code" principle.
- **Suppressing too many numpydoc codes.** SA01/EX01/ES01 (See Also / Examples / Extended Summary) are the SciPy-community defaults — they accommodate that not every internal helper deserves a full literary docstring. **Don't suppress GL08, PR01, RT01 to "make it green faster"** — those are the substantive checks that catch real gaps.
- **Putting interrogate into `[test]` group with pysweph.** D-01 explicitly forbids this. AGPL boundary preservation matters: `pysweph` is AGPL and runtime-isolated to test fixtures; quality tooling has no contamination risk and belongs in its own group.
- **Running numpydoc on every Python version in the matrix.** Wasteful. Doc style is Python-version-independent; gate on 3.13 only (mirrors mypy on 3.11, coverage on 3.13).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Counting documented functions/classes | Custom AST walker for "has docstring?" check | `interrogate` | Edge cases: `@property`-decorated, `@typing.overload`, nested classes, magic methods, conditional `__init__.py` exports — interrogate handles all of these via flags. Hand-rolled walker = months of edge-case bugs. |
| Validating numpydoc-style docstring sections | Regex on `Parameters\n----------` | `numpydoc lint` | Numpydoc cross-references signature against docstring (PR01: param documented but not in signature; PR03: out-of-order). AST + signature inspection. Don't reinvent. |
| Per-file docstring exclusion logic | `if "lunar_calendar" in path: skip` | Tool-native `exclude` config in `pyproject.toml` | Both tools support glob/regex exclusion natively. Keeping exclusion in `pyproject.toml` aligns with the existing `[tool.coverage.run].omit` precedent (D-06, D-07). |
| Make-target invocation of doc gates | Custom shell script in `scripts/` | `Makefile` recipe pattern (existing `make houses-coverage`) | The Makefile already has the `make houses-coverage` precedent. `make doc-gates` is a 4-line recipe that mirrors it. Optional but Sophie-flavored — see Specifics in CONTEXT.md. |

**Key insight:** Both tools are mature; the `dev` group costs 2 lines in `pyproject.toml`; the CI steps cost ~10 lines in `tests.yml`. The phase's actual difficulty is **the audit-and-fix pass on existing docstrings**, not any new tooling. Don't sneak in custom scripts.

## Common Pitfalls

### Pitfall 1: numpydoc `lint` vs `validate` confusion

**What goes wrong:** Running `python -m numpydoc validate ketu` (no path → expects an importable dotted name like `numpy.ndarray`). Reports "ImportError" or non-actionable output.

**Why it happens:** `numpydoc validate` is a **single-object** validator (validates one importable Python object). For multi-file CI use, the right subcommand is `numpydoc lint <files>`, which walks AST without importing.

**How to avoid:** **Always use `lint` in CI.** `[VERIFIED: tested both modes during audit on 2026-05-08]`. The CI step incantation is:
```bash
python -m numpydoc lint $(find ketu -name "*.py" \
    ! -path "*/__pycache__/*" \
    ! -name "lunar_calendar.py" \
    ! -name "_*.py")
```

**Warning signs:** Step output starts with "Traceback (ImportError...)" instead of `path:line: CODE message` lines.

### Pitfall 2: Over-strict `RT01` (No Returns section) on `None` returners

**What goes wrong:** Numpydoc flags `RT01` on every function returning `None` (e.g., CLI entry points, mutating methods). False-positive flood.

**Why it happens:** Default config requires a `Returns` section even when return type is `None`.

**How to avoid:** Don't blanket-suppress RT01 — instead, add explicit `-> None` annotations to functions and write a real `Returns` section (`None`) or use the `Notes`-style docstring form. Sophie-flavored: the type annotation makes intent explicit; numpydoc accepts `Returns ... None\n    Method has no return value.` as valid. **Do NOT suppress RT01 globally.**

**Warning signs:** RT01 hits scattered across CLI handlers, `register()` decorators, and mutating dataclass methods.

### Pitfall 3: GL06 (unknown section) on legacy section names

**What goes wrong:** Top-level `ketu/__init__.py` and `ketu/core.py` use custom section headings ("Submodules", "Precision Guarantees", "Coordinate Transformations", "Body IDs", "Data Structures"). All flagged GL06 + GL07 (wrong order).

**Why it happens:** Numpydoc only recognizes a fixed allow-list: `Parameters, Attributes, Methods, Returns, Yields, Other Parameters, Raises, Warns, Warnings, See Also, Notes, References, Examples`.

**How to avoid:** Move the non-standard sections **into a single `Notes` section** with internal headings using bold or sub-paragraphs:
```
Notes
-----
**Submodules**

ketu.core
    Astronomical constants...

**Precision Guarantees**

- Angular separation: ±1e-6° ...
```

This satisfies GL06/GL07 without losing the structured information. Don't suppress — they're real signals.

**Warning signs:** Module-level docstrings in `__init__.py`, `core.py`, or any "umbrella" module trip GL06/GL07.

### Pitfall 4: `continue-on-error: true` masks the warning step in green builds

**What goes wrong:** Step shows green checkmark even when numpydoc has 47 unaddressed warnings. Contributors don't notice.

**Why it happens:** `continue-on-error: true` makes the GitHub Actions UI report "success" and `if: failure()` won't fire on subsequent steps. `[CITED: github.com/community/discussions/15452]`

**How to avoid:** Use `verbose` echo of the warning count in the step body so the count appears prominently in the log, and document the posture in the README ("warnings are not blocking but should not grow"). Phase 20 flips `continue-on-error: true` → `false` (or removes the line) to make the gate blocking. **The plan for Phase 13 must surface this clearly to the planner of Phase 20.**

**Warning signs:** Numpydoc warning count creeping up over phases 14–19 with no one noticing because all builds are green.

### Pitfall 5: `interrogate` Python 3.13 classifier gap

**What goes wrong:** `interrogate==1.7.0` PyPI metadata classifiers list Python 3.8 through 3.12 — not 3.13. Some pip resolvers in restrictive environments may decline the install.

**Why it happens:** interrogate 1.7.0 was released April 2024, before Python 3.13 went GA (October 2024). Author hasn't republished metadata.

**How to avoid:** `[VERIFIED: live test]` — it runs cleanly on Python 3.13.5 in this repo's venv. If a future pip strict mode breaks: pin `>=1.7.0` (current floor) and add `--ignore-requires-python` flag in CI as a defensive fallback. Not needed today. `[VERIFIED: PyPI JSON metadata, 2026-05-08]`

### Pitfall 6: `pip install -e ".[dev]" || pip install -e .` fallback masks dev-group errors

**What goes wrong:** If a typo or quoting error breaks the `dev` group, `pip` fails and silently falls through to `pip install -e .` — interrogate/numpydoc never installed → next step `python -m interrogate` fails with `ModuleNotFoundError: No module named 'interrogate'`. Confusing because the installation step is green.

**Why it happens:** The `||` shell short-circuit treats any pip failure as fall-through, including syntax errors in `pyproject.toml`.

**How to avoid:** Plan 2 (CI wiring) verification: do a deliberate destructive test first (intentionally typo the group name in a throwaway commit on a feature branch, confirm the CI step fails clearly, revert). Document in the plan's verification section. **OR** tighten the install step to fail fast: `pip install -e ".[dev]"` (no fallback) once we know the group exists — but per D-02 the fallback can stay as defensive belt-and-braces.

**Warning signs:** "Step succeeded" on install but the next step says `No module named 'interrogate'`.

## Code Examples

Verified patterns from the audit pre-flight (run 2026-05-08 against this codebase):

### Recommended `[tool.interrogate]` block

```toml
# Source: pre-flight audit on this codebase, plus interrogate 1.7.0 docs
# https://interrogate.readthedocs.io/en/latest/
[tool.interrogate]
fail-under = 95
exclude = [
    "ketu/lunar_calendar.py",  # mirrors [tool.coverage.run].omit (D-06)
    "tests",
    "build",
    "docs",
]
# Ignore the dunders and inits. Public-API-facing class docstrings
# carry the documentation contract; __init__/repr/eq are
# implementation detail.
ignore-init-method = true
ignore-magic = true
ignore-nested-functions = true
# Do NOT ignore-private / ignore-semiprivate. D-08: fix gaps, don't
# paper them over. The 4 _ra_formula_cusp_* helpers in
# houses/placidus.py get one-line docstrings, audit settled.
ignore-private = false
ignore-semiprivate = false
# Print the score in green-build logs as a positive signal (CONTEXT
# Specifics: "score appears in build logs as a positive signal").
verbose = 1
# Default sphinx style; matches NumPy convention used everywhere else.
style = "sphinx"
```

**Verified output with this config (98.2%, gate passes):**
```
| TOTAL                        |       218 |        4 |       214 |      98.2% |
---------------- RESULT: PASSED (minimum: 80.0%, actual: 98.2%) ----------------
```

### Recommended `[tool.numpydoc_validation]` block

```toml
# Source: numpydoc 1.10.0 docs https://numpydoc.readthedocs.io/en/latest/validation.html
# SciPy / scikit-learn community defaults applied.
[tool.numpydoc_validation]
checks = [
    "all",   # report all
    "EX01",  # ignore: no examples section required (internal helpers)
    "SA01",  # ignore: no See Also required
    "ES01",  # ignore: no extended summary required
    "GL01",  # ignore during warning phase: summary-line placement is cosmetic
             # and triggers ~59 hits across the audit baseline. PHASE 20:
             # remove this and fix the 59 instances when flipping to blocking.
]
# Exclude private modules and lunar_calendar (mirrors interrogate)
exclude = [
    '\.lunar_calendar$',
    '\._',  # any object whose name starts with underscore
]
# Optional: per-object override mechanism for legacy structures
override_SS05 = [  # "Summary must start with infinitive verb" - tolerant of dataclass docstrings
    '^Aspect$',
    '^ZodiacPoint$',
    '^CycleRatio$',
]
```

**Note on `GL01` suppression:** The audit shows 59 GL01 hits — almost all in `complex.py` and `calculations.py` where docstring summaries are on the same line as `"""`. **This is the single largest mechanical fix bucket.** Two options for the planner:
- **Option A (recommended):** Suppress `GL01` during warning phase, fix it as a single mechanical pass right before the Phase 20 flip.
- **Option B:** Don't suppress; fix all 59 in Phase 13 as part of Plan 3.

Option A is recommended because it lets Plan 3 focus on the substantive fixes (GL08 missing docstrings, PR01 missing param docs, RT01 missing Returns sections) and defers the cosmetic line-placement edits to a single Phase 20 sed/regex pass.

### Two CI steps for `tests.yml`

```yaml
# Source: existing tests.yml pattern (Coverage step lines 41-44, gated on 3.13)
# Insert AFTER the existing "Check coverage threshold" step, BEFORE Codecov upload.

    - name: Doc coverage gate (interrogate ≥95%)
      if: matrix.python-version == '3.13'
      run: |
        python -m interrogate ketu/

    - name: Doc style audit (numpydoc — warning only, blocking from v1.2.0)
      if: matrix.python-version == '3.13'
      continue-on-error: true
      run: |
        # Build file list excluding lunar_calendar and _* private modules
        FILES=$(find ketu -name "*.py" \
            ! -path "*/__pycache__/*" \
            ! -name "lunar_calendar.py" \
            ! -name "_*.py")
        echo "Validating $(echo "$FILES" | wc -l) files..."
        python -m numpydoc lint $FILES
```

`[VERIFIED: file globbing pattern tested in shell on 2026-05-08]`

### Optional `make doc-gates` Makefile target (Sophie-flavored, CONTEXT Specifics)

```makefile
## doc-gates: Run the doc-gate suite locally (interrogate + numpydoc lint).
##
## Mirrors what CI runs in tests.yml. Use before pushing to avoid
## learning about a gate failure from the GitHub Actions email.
.PHONY: doc-gates
doc-gates:
	$(PYTHON) -m interrogate ketu/
	$(PYTHON) -m numpydoc lint $$(find ketu -name "*.py" \
	    ! -path "*/__pycache__/*" \
	    ! -name "lunar_calendar.py" \
	    ! -name "_*.py") || true
	@echo "Doc gates OK (numpydoc warnings shown above; not blocking until v1.2.0)."
```

### Audit pre-flight invocation (Plan 1 baseline command)

```bash
# Run from repo root, with venv activated.
# Captures the pre-config baseline before any docstring fixes land.

# 1. interrogate baseline (default settings)
python -m interrogate -v ketu/    # 93.8% baseline, 15 misses

# 2. interrogate with proposed config (sanity-check that config matches gate)
python -m interrogate \
    --ignore-init-method --ignore-magic --ignore-nested-functions \
    --exclude ketu/lunar_calendar.py \
    -v ketu/                       # 98.2% baseline, 4 misses (placidus.py)

# 3. numpydoc baseline (community defaults)
python -m numpydoc lint $(find ketu -name "*.py" \
    ! -path "*/__pycache__/*" ! -name "lunar_calendar.py") \
    --ignore SA01 EX01 ES01        # 231 issues across 9 files

# 4. Per-file numpydoc count (sizes the work)
python -m numpydoc lint <files> --ignore SA01 EX01 ES01 \
    | grep -oE "ketu/[^ :]+\.py" | sort | uniq -c | sort -rn
# Expected output:
#     124 ketu/complex.py
#      68 ketu/calculations.py
#      22 ketu/cycles/calculator.py
#       6 ketu/__init__.py
#       5 ketu/display.py
#       3 ketu/core.py
#       1 ketu/__main__.py
#       1 ketu/ephemeris/__init__.py
#       1 ketu/cycles/__init__.py
```

`[VERIFIED: each command run during this research session, output as documented]`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `numpydoc validate <module.attr>` (single object) | `numpydoc lint <files>` | numpydoc 1.7.0+ | AST-based, no import side effects, bulk-friendly. Use `lint` everywhere. |
| `pydocstyle` for docstring style | `numpydoc lint` for NumPy projects | (long-established) | NumPy projects use NumPy convention; pydocstyle enforces a different convention. |
| `interrogate` with positional config | `[tool.interrogate]` in `pyproject.toml` | interrogate 1.5.0+ | Mature in current 1.7.0 — preferred over CLI flags for reproducibility. |
| Hand-written docstring coverage scripts | `interrogate` | (community standard since ~2020) | All major scientific Python repos (NumPy, scipy, sktime, mars-project) use interrogate. |
| `actions/checkout@v4` + `actions/setup-python@v5` | `@v5+` / `@v6+` (Node 24) | September 2026 deadline | **Out of scope for Phase 13** — handled in Phase 20 (OPS-03). Don't preempt. |

**Deprecated/outdated:**
- `numpydoc validate` (single object) for CI use — use `lint` (multi-file).
- `interrogate --config setup.cfg` — use `pyproject.toml` `[tool.interrogate]`.

## Runtime State Inventory

> Phase 13 is a CI-tooling and source-docstring-edit phase, not a rename/refactor phase. No runtime state is being renamed or migrated. This section is included to satisfy the rename/refactor inventory check explicitly:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — verified by inspection. No data stores are keyed off `interrogate` / `numpydoc` strings. | None |
| Live service config | None — verified by inspection. No external services (Datadog/Cloudflare/etc.) reference these tool names. | None |
| OS-registered state | None — verified by inspection. No systemd/launchd/Task Scheduler entries. | None |
| Secrets/env vars | None — verified by inspection. No env vars by these names; CI uses `CODECOV_TOKEN` only (unaffected). | None |
| Build artifacts / installed packages | `ketu.egg-info/` exists in tree (legacy from `pip install -e .`). Not affected by Phase 13 — neither tool changes the `[project]` block. After `dev` group is added, contributors should re-run `pip install -e ".[dev]"` to pick up the new optional. | Documentation note in plan: "Run `pip install -e .[dev]` after pulling Phase 13 plan 1 to install interrogate/numpydoc locally." |

**Nothing in any stored-state category needs migration.** The phase is purely additive in `pyproject.toml`, additive in `tests.yml`, and edit-only on existing source docstrings.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.13 | CI doc-gate steps (3.13-only) | ✓ | 3.13.5 (in repo venv) | — |
| Python 3.10/3.11/3.12 | CI matrix legs | ✓ (GitHub Actions matrix) | as set up | — |
| `interrogate` | OPS-01 gate | ✓ (already installed) | 1.7.0 | — |
| `numpydoc` | OPS-02 gate | ✓ (just installed) | 1.10.0 | — |
| `sphinx` (transitive) | numpydoc dep (>=6) | ✓ | 9.1.0 | — |
| `pip` index access (CI) | Tool install step | ✓ (GitHub Actions network) | — | — |
| `bash` `find` (CI step) | numpydoc file globbing | ✓ (ubuntu-latest runner) | — | shell-portable |
| `tomli` (Python <3.11) | TOML parsing in interrogate/numpydoc | auto via deps | (transitive) | — |
| Codecov | Existing coverage upload step (unchanged) | ✓ | (action v4) | — |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None — every required dep is either already installed in the dev venv or comes free in the GitHub Actions ubuntu-latest runner.

**Sphinx note:** numpydoc declares `sphinx>=6` as a runtime dependency (so it can render `.. autosummary::` blocks). In CI, this means installing `numpydoc` will pull `sphinx` ~= 9.1 onto the runner. Acceptable transitive footprint; no Sphinx invocation happens in CI for Phase 13. `[VERIFIED: PyPI metadata, numpydoc 1.10.0 requires sphinx>=6]`

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 8.x` + `pytest-cov` (already in CI per `tests.yml` line 28) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (line 62-76) |
| Quick run command | `python -m pytest tests/ -v --no-cov` |
| Full suite command | `python -m pytest tests/` (auto-runs coverage per `addopts`) |
| Doc-gate quick run | `make doc-gates` (if added) OR `python -m interrogate ketu/ && python -m numpydoc lint <files>` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| OPS-01 | `interrogate ≥95%` blocks the build when below threshold | smoke (CI integration) | `python -m interrogate ketu/ --fail-under=95` returns exit 0 ON PASS, exit 1 ON FAIL | ✅ `pyproject.toml [tool.interrogate]` config — Plan 1 |
| OPS-01 | `dev` group resolves and installs both tools cleanly | smoke (CI integration) | `pip install -e ".[dev]" && python -c "import interrogate, numpydoc"` returns exit 0 | ✅ `pyproject.toml [project.optional-dependencies].dev` — Plan 1 |
| OPS-01 | CI step in `tests.yml` runs the gate on Python 3.13 only | manual-only (workflow inspection) | `grep -A2 'interrogate' .github/workflows/tests.yml` shows the step gated to 3.13 | ✅ `tests.yml` — Plan 2 |
| OPS-02 | `numpydoc lint` runs in CI, surfaces warnings, doesn't block | smoke (CI integration) | `python -m numpydoc lint <files>` produces output; CI step has `continue-on-error: true` | ✅ `pyproject.toml [tool.numpydoc_validation]` config + `tests.yml` step — Plans 3+4 |
| OPS-02 | `numpydoc lint` produces zero issues on the post-fix codebase | unit (regression) | `python -m numpydoc lint <files> --ignore SA01 EX01 ES01 GL01` returns clean (zero issues) | ⚠️ depends on Plan 3 fix-pass completion |
| OPS-01/02 | Reformulation pass touches no `.planning/` files | manual-only (commit inspection) | `git diff --stat plan-5-base..HEAD -- '.planning/'` shows zero entries | manual review |
| OPS-01/02 | Public docs claim the gate truthfully | manual-only (sweep) | `grep -rni "interrogate\|numpydoc" CHANGELOG.md README.md docs/source/` shows only "enforced by CI" wording | ⚠️ verify-only — audit confirmed currently zero hits |

### Sampling Rate

- **Per task commit (during Plan 3 fix-pass):**
  ```bash
  python -m numpydoc lint <files-being-edited> --ignore SA01 EX01 ES01 GL01
  ```
  Run on each file as it's edited. Fast (sub-second per file).

- **Per plan merge (gate verification):**
  ```bash
  python -m interrogate ketu/                 # must pass after Plan 1
  python -m numpydoc lint <full-file-list>    # must produce ≤baseline issues after Plan 3
  python -m pytest tests/                     # full suite still green (no behavior changes — docstring-only edits)
  ```

- **Phase gate (before `/gsd-verify-work`):**
  - `python -m interrogate ketu/` **passes** (interrogate ≥95%)
  - `python -m numpydoc lint <files>` produces output but does NOT halt CI (warning posture per D-04)
  - Full test suite green
  - CI on PR for the final commit shows the two new steps (one passing, one warning-only) in the Actions log

### Wave 0 Gaps

- [ ] **No new test files needed.** Phase 13 is docstring-only edits + CI plumbing — no behavior change → no new behavior tests. The audit pre-flight invocation IS the regression gate (it's what CI runs).
- [ ] **`make doc-gates` Makefile target** (optional, recommended) — covers OPS-01/OPS-02 local-runnability for contributors. See Code Examples.
- [ ] **No framework install:** pytest/coverage/mypy already installed; `interrogate` already installed; `numpydoc` will be installed by Plan 1's `pip install -e ".[dev]"` after the dev group lands.

*(No test infrastructure additions required — Phase 13 is exceptionally test-light because it adds no behavior.)*

## Aspirational References Audit (D-11 verification)

> Per D-11, every public-doc mention of "interrogate ≥95%" / "numpydoc validate" must be reformulated to "**enforced by CI** (`tests.yml`)". Per D-12, `.planning/` is excluded from this sweep.

**Sweep command run on 2026-05-08:**
```bash
grep -rni "interrog\|numpydoc\|≥95\|>= *95\|95 *%\|95%\|aspirat" \
    /home/loc/workspace/ketu/CHANGELOG.md \
    /home/loc/workspace/ketu/README.md \
    /home/loc/workspace/ketu/CONTRIBUTING.md \
    /home/loc/workspace/ketu/UPGRADING.md \
    /home/loc/workspace/ketu/docs/source/
```

**Result:** Zero hits across all 5 search targets. `[VERIFIED: live grep, 2026-05-08]`

**Implication for the planner:** **Plan 5's reformulation pass is verify-only, not edit-heavy.** The planner should structure Plan 5 as:
1. Re-run the sweep above on the post-fix HEAD; confirm zero hits.
2. **Add positive reformulated language** to the README (one short paragraph) describing the gates as currently configured: e.g. *"Documentation quality is enforced by CI: `interrogate ≥95%` (blocking) and `numpydoc validate` (warning, blocking from v1.2.0)."* This is what closes OPS-01/OPS-02 traceability without leaving any aspirational claim un-backed.
3. Update `.planning/STATE.md` and `.planning/MILESTONES.md` via the normal `update_state` flow per D-12 (NOT in Plan 5's diff).

**Why this matters:** The original framing assumed there were existing aspirational claims to reformulate. The audit shows there aren't — the only claims live in `.planning/` (which D-12 excludes). The "reformulation pass" is therefore a positive-add of the gate description to README, not a rewrite of stale claims.

## Project Constraints (from CLAUDE.md)

| Directive | Source | Phase 13 Compliance Note |
|-----------|--------|--------------------------|
| Persona is Sophie Chen, French/tutoiement | CLAUDE.md "Persona" | Plan 5's added README/docstring text follows this voice |
| Ketu has no MarketStream / Kala dependency | CLAUDE.md "Standalone" | Phase 13 adds no runtime deps; tooling is dev-only — boundary preserved |
| Venv is `venv/`, not `.venv/` | CLAUDE.md "Venv" | Audit invocations and `make doc-gates` target use `venv/` (and `python -m` to dodge shebang drift documented in STATE.md) |
| NumPy first, structured arrays for ML interop | CLAUDE.md "NumPy first" | N/A — no calculation changes in Phase 13 |
| Type hints partout, NumPy for performance | CLAUDE.md "Conventions" | Docstring fixes preserve existing type hints; no signature changes |
| DateTime always UTC | CLAUDE.md "Conventions" | N/A — no datetime code touched |
| **No runtime dep additions** | CLAUDE.md "Règles importantes" + CONTEXT cross-cutting constraints | `dev` group is `[project.optional-dependencies]`, NOT `[project.dependencies]` — pure-NumPy runtime preserved |

`[VERIFIED: CLAUDE.md inspected]`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `pip install -e ".[dev]" \|\| pip install -e .` fallback in tests.yml will work as soon as `[project.optional-dependencies].dev` exists in pyproject.toml. | Architecture Patterns | If the install command has a hidden quoting issue specific to certain pip versions, Plan 2's first CI run could install successfully but then `python -m interrogate` would fail with ModuleNotFoundError. Mitigated by Plan 2 having the destructive-test verification step (Pitfall 6). `[ASSUMED]` based on standard pip behavior, not tested in this session. |
| A2 | The single READMEparagraph added in Plan 5 is the only "positive" public-doc text needed to close OPS-01/OPS-02 traceability. | Aspirational Refs Audit | If the user expects a more detailed contributor doc (e.g., a docstring style guide section), Plan 5 will be under-scoped. Mitigated by the planner offering the option in the plan-checker review or `/gsd-discuss-phase` re-entry. `[ASSUMED]` from CONTEXT Specifics + D-11 wording, not directly confirmed with user. |
| A3 | Suppressing GL01 during the warning phase (numpydoc) is acceptable and the 59 GL01 hits will be fixed in a single mechanical pass right before the Phase 20 blocking-flip. | Code Examples / numpydoc config | If the planner or user prefers to fix all 59 in Phase 13 (option B in the GL01 note), Plan 3's scope grows by ~1 hour of mechanical regex edits. Mitigated by surfacing the choice explicitly in the `[tool.numpydoc_validation]` block. `[ASSUMED]` based on signal-to-noise tradeoff; user has not been asked. |

## Open Questions (RESOLVED)

1. **Should `make doc-gates` (Sophie-flavored local one-shot) actually land?**
   - What we know: CONTEXT Specifics says it's optional but Sophie-flavored; the Makefile already has the `houses-coverage` precedent; recipe is 4 lines.
   - What's unclear: User preference for "yes ship it" vs "leave it to contributors' shell aliases".
   - **RESOLVED:** Recommendation: **Ship it.** Makefile precedent is set; cost is minimal; contributor experience is improved. Planner can include in Plan 4 or Plan 5. _(Resolution: Plan 02 ships `make doc-gates`; consistent with the plan set as written.)_

2. **Plan 3 vs Plan 4 scope split — single load-bearing plan or two?**
   - What we know: Plan 3 (numpydoc config + audit + fix all gaps) is the largest plan in the phase. Plan 4 (wire numpydoc into CI) is a 5-line change.
   - What's unclear: Whether the planner will want to split Plan 3 by file (e.g., one plan for `complex.py` alone, one for `calculations.py`+rest) given that `complex.py` is 124/231 of the issues.
   - **RESOLVED:** Recommendation: Single Plan 3 covering all files, but the plan's task list can naturally chunk by file. The fix is mechanical enough that file-level chunking inside one plan is preferable to plan-level chunking — keeps the merge surface small. _(Resolution: Plan 03 is a single plan with 3 tasks chunked by file group; consistent with the plan set as written.)_

3. **`pip install -e ".[dev]"` vs `pip install -e ".[dev,test]"` in CI?**
   - What we know: Currently CI runs `pip install -e ".[dev]" || pip install -e .` then `pip install pytest pytest-cov` separately (line 28-29 of tests.yml). `test = ["pysweph"]` is the AGPL group.
   - What's unclear: Whether the existing CI install verb covers pysweph for tests that need it. Line 28's plain `pip install pytest pytest-cov` doesn't pull pysweph; presumably tests that need it `pytest.importorskip("swisseph")`.
   - **RESOLVED:** Recommendation: **Don't change the install verb in Phase 13.** D-02 says "the fallback can stay (defensive)". If pysweph-related test runs need the AGPL extra later, that's a separate change in OPS-03/Phase 20, not here. Out of scope. _(Resolution: install verb left untouched in all 5 plans; consistent with the plan set as written.)_

## Sources

### Primary (HIGH confidence)
- **Live audit run on this codebase** (2026-05-08, Python 3.13.5 in `venv/`): `python -m interrogate ketu/` (default + with-config), `python -m numpydoc lint <files>` (default + with-suppressions). All counts and per-file numbers cited above are from this run.
- **`pyproject.toml`** at `/home/loc/workspace/ketu/pyproject.toml` — read in full; current optional-deps shape, mypy/coverage config conventions confirmed.
- **`.github/workflows/tests.yml`** at `/home/loc/workspace/ketu/.github/workflows/tests.yml` — read in full; matrix and existing version-gating pattern confirmed.
- **CONTEXT.md** at `/home/loc/workspace/ketu/.planning/phases/13-doc-gates-and-ci-foundation/13-CONTEXT.md` — locked decisions D-01..D-13.
- **REQUIREMENTS.md** § "Tier 3 — ops debt" — OPS-01, OPS-02 wording.
- **CLAUDE.md** — project rules (venv, no runtime deps, persona).
- **interrogate official docs** https://interrogate.readthedocs.io/en/latest/ — fetched 2026-05-08; complete `[tool.interrogate]` option reference.
- **numpydoc validation docs** https://numpydoc.readthedocs.io/en/latest/validation.html — fetched 2026-05-08; complete error code reference + `[tool.numpydoc_validation]` config shape.
- **PyPI JSON metadata** https://pypi.org/pypi/interrogate/1.7.0/json and https://pypi.org/pypi/numpydoc/1.10.0/json — fetched 2026-05-08; release dates, Python compat, runtime deps.

### Secondary (MEDIUM confidence)
- **GitHub community discussion #15452** ("Properly show continue-on-error jobs/steps in PR UI") — for the `continue-on-error: true` UX caveat documented in Pitfall 4.
- **interrogate's own pyproject.toml** (econchick/interrogate on GitHub) — referenced for example production scientific-Python config shape.

### Tertiary (LOW confidence)
- None. All recommendations in this research are backed by live verification or primary docs.

## Metadata

**Confidence breakdown:**
- Standard stack (`interrogate>=1.7.0`, `numpydoc>=1.10.0`): **HIGH** — both versions verified against PyPI metadata in this session, both running cleanly in the repo's Python 3.13 venv.
- `[tool.interrogate]` config (98.2% baseline, 4 misses to fix): **HIGH** — live audit run produced these exact numbers.
- `[tool.numpydoc_validation]` config (231 issues with community defaults): **HIGH** — live audit run produced these exact numbers, broken down per-file and per-error-code.
- CI step shape (separate steps, 3.13-gated, `continue-on-error: true` for numpydoc): **HIGH** — pattern matches existing `tests.yml` precedent (mypy on 3.11, coverage on 3.13) and is documented in numpydoc docs.
- Aspirational-refs audit (zero hits in public docs): **HIGH** — live grep over CHANGELOG/README/CONTRIBUTING/UPGRADING/docs/source.
- Plan sequence (5 plans, audit→wire→fix→wire→reformulate): **MEDIUM** — based on the audit-first principle in D-09 and the fix-before-wire principle that prevents broken-CI commits; planner is free to merge Plans 1+2 or 3+4 if the granularity feels too fine.
- Pin-floor strategy (`>=`, not `==`): **MEDIUM** — both tools have stable APIs but no formal LTS guarantee. Floors are the conservative scientific-Python convention; if the user prefers exact pins for reproducibility, the cost is one extra line of `pin-version` ceremony.

**Research date:** 2026-05-08
**Valid until:** 2026-06-08 (30 days; both tools have low release velocity, audit results are not version-sensitive within this window)

---

*Research conducted by Sophie Chen via `/gsd-research-phase 13`. Pre-flight audit run live against the v1.1.0 codebase. Six pitfalls documented with verification protocol per the GSD research-phase contract. Three open questions surfaced for the planner.*
