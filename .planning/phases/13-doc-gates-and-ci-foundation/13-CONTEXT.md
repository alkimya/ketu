# Phase 13: Doc Gates & CI Foundation - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

CI infrastructure that gates docstring quality on every commit, with the v1.1 codebase brought to a clean baseline so the gates pass green from day one. Pure ops/CI work — no public library API surface changes, no new runtime dependencies.

**In scope:**
- Wire `interrogate ≥95%` (blocking) into `tests.yml`.
- Wire `numpydoc validate` (warning at first, blocking from Phase 20) into `tests.yml` on the public surface of `ketu/`.
- Add `interrogate` and `numpydoc` to a new `dev` group in `[project.optional-dependencies]`.
- Audit the v1.1 codebase against both gates and fix every pre-existing docstring gap so the very first CI run on Phase 13 is green.
- Reformulate every aspirational reference to those gates into accurate "enforced by CI" wording in CHANGELOG, README, and `.planning/` (PROJECT, MILESTONES, STATE) so OPS-01 / OPS-02 traceability is closed.

**Out of scope:**
- Node.js workflow refresh (OPS-03 — Phase 20).
- `fr/CHANGELOG.md` decision (OPS-04 — Phase 20).
- Coverage gate changes (current `fail_under = 70` project + `houses_coverage_gate` ≥95% on `ketu.houses` stay as-is; ≥95% on new modules is enforced phase-by-phase, not here).
- Sphinx build gate (`-W` warnings) — not in v1.2 requirements; deferred unless surfaced.

</domain>

<decisions>
## Implementation Decisions

### Optional-dependencies layout
- **D-01:** Add a new `dev` group: `[project.optional-dependencies].dev = ["interrogate>=…", "numpydoc>=…"]`. Do NOT colocate with `test = ["pysweph"]` — `test` holds an AGPL dep and we keep that boundary clean.
- **D-02:** `tests.yml` already runs `pip install -e ".[dev]" || pip install -e .` — that command works as soon as the `dev` group exists; the fallback can stay (defensive).
- **D-03:** `dev` group is the right home even though the gates run in CI: it keeps the install verb intuitive (`pip install -e .[dev]`) for contributors running the gates locally before pushing.

### `numpydoc validate` posture and scope
- **D-04:** Phase 13 lands `numpydoc validate` as **non-blocking warnings** in CI (errors surface in build log, build still succeeds). This matches ROADMAP success criterion 13.2 and gives Phases 14–19 a soft enforcement signal without halting unrelated work on a docstring nit.
- **D-05:** Gate flips to **blocking** in Phase 20 (release prep). Phase 20's plan must include a "flip numpydoc to blocking" step explicitly — capture this as a forward note when writing Phase 20 (planner's job, not ours).
- **D-06:** Public scope for `numpydoc validate` = everything under `ketu/` **except** modules/files starting with `_` (Python convention for private). Also exclude `ketu/lunar_calendar.py` to mirror the existing `[tool.coverage.run].omit` carve-out — it's already treated as legacy/unmaintained surface.
- **D-07:** `interrogate` scope follows the same exclusion list (no `_*`, no `lunar_calendar.py`) so the two gates stay aligned. The interrogate config goes in `[tool.interrogate]` inside `pyproject.toml`.

### Baseline cleanup (v1.1 → clean)
- **D-08:** ROADMAP success criterion 13.4 is taken literally: any pre-existing docstring gap surfaced by `interrogate` or `numpydoc validate` is **fixed in this phase, not deferred**. Phase 13 does not merge until both gates run green on the in-scope surface.
- **D-09:** Audit step is the first task: enumerate every public function/class/module that fails either gate, classify (missing docstring vs malformed numpydoc vs deprecated → exclude), and bound the work before writing fixes. If the audit reveals >2 days of writing, surface that to user with Sophie's voice — no silent scope creep.
- **D-10:** Modules at higher-than-average legacy risk (write docstrings carefully, may have stale signatures): `calculations.py`, `complex.py`, top-level `__init__.py` re-exports. Modules already known clean (touched in v1.1): `aspects/`, `cycles/`, `houses/`, `ephemeris/`. Audit will confirm.

### Aspirational references cleanup (OPS-01 / OPS-02 final closure)
- **D-11:** Once CI is green, every public-doc mention of "interrogate ≥95%" / "numpydoc validate" is reformulated to "**enforced by CI** (`tests.yml`)" — the claim stays visible (good for users/contributors) but is now factually accurate. Files to sweep: `CHANGELOG.md`, `README.md`, any reference under `docs/` (Sphinx).
- **D-12:** `.planning/` files are NOT touched in this phase's reformulation pass — `STATE.md`, `PROJECT.md`, `MILESTONES.md` are tracking documents that record "was aspirational, now wired" as part of the v1.2 narrative; they get updated by the normal `update_state` / milestone-tracking flow, not as CHANGELOG-style edits. (User chose "Replace with 'enforced by CI'" for the public-facing claim — `.planning/` is internal and follows its own update cadence.)
- **D-13:** No new aspirational claims are added in Phase 13. If a future phase needs a new gate, it wires it in the same phase that adds the claim — never in a "we'll wire it later" comment.

### Claude's Discretion
- Pin versions or use floor `>=X.Y` for `interrogate` and `numpydoc` — researcher decides based on PyPI release cadence and Python 3.10–3.13 compatibility.
- Whether `numpydoc validate` runs as a separate CI step or piggybacks on the existing `Type check` step — planner decides based on signal-to-noise on the build log.
- Order of fix-up commits inside Phase 13 (audit → wire (warning) → fix gaps → flip interrogate to blocking → reformulate refs) — planner sequences the plans.
- Exact `[tool.interrogate]` configuration knobs (`ignore-init-module`, `ignore-magic`, `fail-under`, `verbose`) — defaults usually fine; planner picks.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` § "Phase 13: Doc Gates & CI Foundation" — goal, depends-on, success criteria 1–4.
- `.planning/REQUIREMENTS.md` § "Tier 3 — ops debt" — OPS-01 (interrogate ≥95%, blocking) and OPS-02 (numpydoc validate, warnings then blocking).
- `.planning/STATE.md` § "v1.2 ops debt" — current "not installed/wired into CI" status that this phase closes.
- `.planning/PROJECT.md` § "CI doc gates (early)" — the rationale for landing this in Phase 13 rather than late.

### v1.2 framing constraints (apply to every phase, including this one)
- `.planning/ROADMAP.md` § "Cross-Cutting Constraints (v1.2)" — non-breaking minor strict, pure-NumPy, Python 3.10+, mypy --strict clean.
- `CLAUDE.md` § "Règles importantes" — no runtime dep additions; venv = `venv/` not `.venv/`.

### Existing CI / tooling configuration
- `.github/workflows/tests.yml` — current matrix (3.10–3.13), install verb (`pip install -e ".[dev]" || pip install -e .`), coverage check (3.13), mypy strict (3.11), Codecov upload.
- `pyproject.toml` § `[project.optional-dependencies]` — current state: only `test = ["pysweph"]`. New `dev` group lands here.
- `pyproject.toml` § `[tool.coverage.run]` — `omit` list including `ketu/lunar_calendar.py` is the precedent for exclusion-list shape.
- `pyproject.toml` § `[tool.mypy]` — strict + per-module overrides; pattern to mirror for `[tool.interrogate]` + `[tool.numpydoc_validation]`.

### Aspirational claims to reformulate
- `CHANGELOG.md` (root) — unverified, audit during plan.
- `README.md` (root) — unverified, audit during plan.
- `docs/` (Sphinx) — unverified, audit during plan.
- (`.planning/MILESTONES.md`, `.planning/PROJECT.md`, `.planning/STATE.md` mention these as "aspirational" — those are tracking docs, see D-12; flip from "aspirational" to "wired" happens in the normal milestone update flow.)

### Pre-research input (already absorbed but retained for traceability)
- `.planning/research/v1.2-OPEN_QUESTIONS.md` § Q5 + SR-Q3 — Tier 3 ordering rationale and "are interrogate / numpydoc already in optional-dependencies?" (answer: no — confirmed via direct read).
- `.planning/research/v1.2-SCOPE.md` § "interrogate ≥95%" / "numpydoc validate" bullets — original "wire it" recommendation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`tests.yml` matrix and install pattern** — already supports a `dev` extras group (`pip install -e ".[dev]"`); adding the group is a no-op for the workflow file beyond appending two new CI steps for the gates.
- **`[tool.coverage.run].omit` precedent** — same shape will be reused for `[tool.interrogate].exclude` and `[tool.numpydoc_validation].exclude`. Keep the exclusion lists consistent across the three tools.
- **`Makefile` target convention** (`make houses-coverage` for the v1.1 ≥95% scoped gate) — same convention works for `make doc-gates` if a local one-shot is useful for contributors. Optional, planner decides.

### Established Patterns
- **Per-module mypy overrides** in `pyproject.toml` are how Ketu handles "strict in general, soft on legacy modules." Same pattern can apply to `numpydoc_validation` if any specific module needs lenient rules during the warning phase. Don't over-use it — defaults first.
- **CI step gating by Python version** (e.g., mypy on 3.11, coverage check on 3.13) — keeps the matrix fast. Doc gates run on a single Python version (3.13) — they're version-independent, no need for matrix duplication.
- **AGPL non-contamination boundary** between `test` (pysweph, AGPL) and runtime/quality tooling — D-01 directly preserves this boundary by adding a separate `dev` group.

### Integration Points
- Two new CI steps in `.github/workflows/tests.yml` (one for `interrogate --fail-under=95`, one for `python -m numpydoc validate`).
- Two new `pyproject.toml` sections: `[tool.interrogate]` and `[tool.numpydoc_validation]`.
- One new entry under `[project.optional-dependencies]`: `dev`.
- Edits across `CHANGELOG.md`, `README.md`, possibly `docs/` for the reformulation pass (D-11).
- Docstring fixes spread across `ketu/` modules — surface count bounded by audit (D-09).

</code_context>

<specifics>
## Specific Ideas

- "**Enforced by CI**" is the canonical replacement phrasing for aspirational claims. Use it verbatim where the claim was previously bare ("interrogate ≥95%" → "interrogate ≥95% (enforced by CI)").
- The CI step should print the score even when passing, so the score appears in build logs as a positive signal (not just absence of failure). Same idea for `numpydoc validate` warning count.
- `make doc-gates` (or equivalent) for local one-shot is **optional** but Sophie-flavored ("contributors should be able to run the gates without pushing first").

</specifics>

<deferred>
## Deferred Ideas

- **Sphinx `-W` warnings as build gate** — not in OPS-01/OPS-02; surface again only if v1.3+ requirements call for it.
- **Pre-commit hook for interrogate** — useful for contributors but not required by ROADMAP. Could land as a quality-of-life follow-up after Phase 13 if Sophie wants; not in scope.
- **`fr/CHANGELOG.md` reformulation pass** — D-11 is OPS-01/OPS-02 only. The `fr/CHANGELOG.md` decision (OPS-04) is its own item in Phase 20; don't conflate.
- **Tightening `fail_under` from 70 to 90 (project-wide coverage)** — separate gate, separate phase. v1.2 requirements only ask for the new-module ≥95% rule per phase; project-wide ≥90% promised in roadmap will land before milestone close, but not as Phase 13 work.
- **Per-module numpydoc severity overrides** — only if the warning-phase signal is too noisy. Default config first; override later if needed.

</deferred>

---

*Phase: 13-doc-gates-and-ci-foundation*
*Context gathered: 2026-05-08*
