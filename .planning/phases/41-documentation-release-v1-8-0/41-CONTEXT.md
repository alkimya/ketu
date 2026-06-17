# Phase 41: Documentation + Release v1.8.0 - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Document the v1.8 declination-speed surface (delivered and validated in Phase 40)
in English and French, perform a **name-clean sweep** of all public-facing
artifacts so Ketu reads as a standalone public library with no private-project
names, bump the version to **1.8.0** in all three source-of-truth files, and ship
`ketu==1.8.0` to PyPI via OIDC trusted publishing behind a human go/no-go gate.

**The engine is done.** Phase 40 shipped DSPD-01..06 (verifier 6/6, 1691 tests,
100% coverage): `body_decl_speed` at `CHART_DTYPE` index 8 (16 fields),
`DECL_STANDSTILL_EPS = 0.001`, the chart-level `is_ascending_declination_chart`
helper, composite δ-speed derived from the chart's own frozen (λ,β). This phase
documents that surface and releases it — it does NOT touch the calculation.

**Requirements are pre-locked by `.planning/REQUIREMENTS.md` (DSPD-07, REL-01).**
Downstream agents MUST read REQUIREMENTS.md — the WHAT (MINOR-not-patch, EN+FR,
.mo recompiled, push main + tag, OIDC, human go/no-go, post-publish smoke) is
binding there. This CONTEXT.md resolves the gray areas the requirements left open
and records the name-clean decision (which extends DSPD-07's "Ketu/Rahu boundary"
language into a project-name-free framing).

</domain>

<decisions>
## Implementation Decisions

### Public-library framing — NO private-project names (the central steer)
- **D-01:** Ketu is the **public source of truth**; downstream consumers adapt to
  it. Phase 41 writes ALL new content (the `[1.8.0]` changelog EN+FR, the
  UPGRADING v1.7→v1.8 entry, the api.md / concepts.md additions) **with zero
  references to any private project** — no "Kala", no "Rahu" (as a project), no
  "Solaris", no "Surya", no "MarketStream", no `KetuAdapter`/`KetuDataAdapter`.
  Replace with generic, neutral phrasing: **"downstream consumers"** (EN) /
  **"consommateurs en aval"** (FR).
- **Why:** Rahu and Kala are private projects "pour l'instant"; a public PyPI
  library must not name them. Ketu stands on its own.
- **CRITICAL distinction — celestial bodies stay:** "Rahu", "Ketu", "Lilith" as
  the *celestial points* (North/South lunar nodes, Black Moon Lilith — body ids
  10/11/12) are legitimate astronomical terms and **MUST be preserved** wherever
  they name a body, an orb, an aspect, a node-speed, etc. Only the *Rahu UI
  project* / *Kala ML project* / *Solaris ecosystem* references are removed. The
  cleanup is a project-name purge, never an astronomy-term purge.

### Legacy cleanup scope — full sweep, including already-shipped entries
- **D-02:** Phase 41 purges **ALL** legacy private-project mentions, not just new
  content. Decided explicitly: **"Nettoyer tout le legacy."** This rewrites
  existing (already-published) changelog/upgrading entries to use the generic
  "downstream consumers" phrasing. Inventory to clean (project-name occurrences,
  body-name "Rahu/Ketu/Lilith" excluded):
  - `CHANGELOG.md` — 11 "Kala" hits
  - `fr/CHANGELOG.md` — 4 hits
  - `UPGRADING.md` — 13 "Kala" hits (also check `KetuDataAdapter`/`KetuAdapter`)
  - `docs/source/changelog.md` — 2 hits
  - `docs/source/concepts.md` — 2 hits
  - FR catalogs carrying "Kala": `docs/locale/fr/LC_MESSAGES/concepts.po`,
    `docs/locale/fr/LC_MESSAGES/changelog.po` (translation strings → recompile .mo)
- **Note:** Rewriting historical changelog entries is normally avoided, but the
  user accepts it here because the goal is name-clean publication, not historical
  fidelity to internal project names. Keep the technical substance of each entry
  identical — only swap the project name for the generic term.

### Code-docstring cleanup — IN scope (rendered into public API docs)
- **D-03:** The name-clean sweep extends to **source-code docstrings**, because
  they render into the public Sphinx API docs via autodoc/numpydoc. Decided:
  **"Docs + docstrings."** Exact lines to clean (13 lines, 5 files):
  - `ketu/synastry/__init__.py:47`
  - `ketu/synastry/core.py:21, 46, 105`
  - `ketu/aspects/calculator.py:168, 299, 423, 460, 536`
  - `ketu/houses/core.py:10`
  - `ketu/charts/core.py:20, 97, 102`
- **Consequence:** touching code → Phase 41 MUST re-run the full quality gates
  (numpydoc validate, interrogate ≥95%, `make doctest`, mypy `--strict`) and the
  1691-test suite + 100% coverage, all of which were green at Phase 40 close.
  Replace "Kala (the downstream ML consumer)" → "the downstream ML consumer",
  "(Kala)" / "(e.g. Kala)" → "(downstream consumers)", "Kala's positional
  contract" → "the downstream positional contract", "Kala adapts to Ketu" →
  "downstream consumers adapt to Ketu". Preserve all technical meaning and any
  doctest examples byte-for-byte.

### Documentation depth & placement for the new v1.8 surface (DSPD-07)
- **D-04:** Document the new surface in the three established landing pages, at the
  depth used for `body_decl` in v1.5 (the direct precedent):
  - `docs/source/api.md` — `body_decl_speed` field in the `CHART_DTYPE` table,
    `DECL_STANDSTILL_EPS` constant, the chart-level `is_ascending_declination_chart`
    helper (with its `np.int8` {−1, 0, +1} per-body return + shape `(14,)` /
    `S+(14,)`), clearly distinguished from the v1.5 scalar
    `is_ascending_declination(jd, body)`.
  - `docs/source/concepts.md` — the dδ/dt meaning (deg/day, ↗/↘ reads off the
    sign, mirrors `body_speeds` for longitude), the Δt = 0.01 d FD-step rationale,
    and the `DECL_STANDSTILL_EPS` standstill contract (≈0 ⇒ neutral). Frame the
    boundary as a **library design principle** — *Ketu computes all the astronomy
    (including the finite difference) and the standstill threshold; consumers read
    a field and display it, computing no astronomy of their own* — WITHOUT naming
    any project (D-01).
  - `docs/source/changelog.md` (the Sphinx-rendered changelog) + the top-level
    `CHANGELOG.md` + `fr/CHANGELOG.md` — dated `[1.8.0]` entry, EN + FR.
- **D-05:** Include at least one short, runnable code example of reading
  `body_decl_speed` / calling `is_ascending_declination_chart` on a chart (montant
  / descendant), consistent with the doctest-as-gate convention — but keep it
  minimal; this is a derivative-field doc, not a new subsystem.

### UPGRADING v1.7→v1.8 content (REL-01)
- **D-06:** The UPGRADING entry explains the dtype layout grows (CHART_DTYPE now
  16 fields; `body_decl_speed` appended at index 8), why it's **MINOR-not-patch**,
  and gives **generic** migration guidance: named-field access
  (`chart["body_lons"]`) is unaffected; positional / `.view()` consumers must
  adapt and re-pin the PyPI version. NO project names — mirror the v1.5
  `body_decl` UPGRADING entry's structure but with the generic phrasing of D-01.

### Release gate sequence (REL-01)
- **D-07:** The release follows the established, rodé sequence (8th release-doc
  phase): (1) write/clean all docs EN+FR, (2) recompile FR `.mo` (no English
  fallback), (3) build docs EN+FR clean at the 1-warning baseline, (4) bump 1.8.0
  in all THREE source-of-truth files — `pyproject.toml:7`, `ketu/__init__.py:57`,
  `docs/source/conf.py:14-15` (`release` + `version`), (5) **human go/no-go
  relecture-validation checkpoint** (the user personally reviews the whole
  milestone before the irreversible publish — locked decision, every milestone),
  (6) push main + tag `v1.8.0` → OIDC publish.yml, (7) post-publish fresh-venv
  smoke FROM PyPI.
- **D-08:** Post-publish smoke must confirm (from REQUIREMENTS REL-01 + ROADMAP
  criterion 4): `body_decl_speed` present in `CHART_DTYPE`, populated with
  non-trivial values for a test chart, `DECL_STANDSTILL_EPS` importable, and no
  `pyswisseph` at runtime.

### Claude's Discretion
- Exact wording of the generic replacements ("downstream consumers" vs "downstream
  ML consumer" vs "ML pipelines") is the executor's call as long as no project is
  named and technical meaning is preserved.
- Whether the changelog example lives in `concepts.md` or `api.md` — planner picks
  the more natural home.
- Whether `make doctest` gains a new doctest for `is_ascending_declination_chart`
  or the example stays prose — executor's call, but prefer a doctest (convention).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap (binding — read first)
- `.planning/REQUIREMENTS.md` — DSPD-07 + REL-01; the binding requirement
  contract. The WHAT (MINOR 1.8.0, EN+FR, .mo recompiled, push main+tag, OIDC,
  human go/no-go, post-publish smoke contents) is locked here, not in this file.
- `.planning/ROADMAP.md` § "Phase 41: Documentation + Release v1.8.0" — goal,
  depends-on (Phase 40), 4 success criteria (what must be TRUE).
- `.planning/PROJECT.md` — milestone v1.8 intent, Key Decisions table (esp. the
  "User go/no-go before irreversible PyPI publish" and MINOR-bump rationale rows),
  Constraints (NumPy-only runtime, pyswisseph test-only, OIDC release).

### Phase 40 (the surface being documented)
- `.planning/phases/40-declination-speed-field-chart-api/40-CONTEXT.md` — the
  D-01..D-03 implementation decisions behind the field, the standstill value, and
  the int8 {−1,0,+1} helper encoding.
- `ketu/charts/core.py:113` — the `("body_decl_speed", "f8", (14,))` field
  (CHART_DTYPE comment block at lines 63-113 documents intent).
- `ketu/charts/api.py:396-411, 572-618` — `compute_chart` FD at Δt=0.01 d +
  `is_ascending_declination_chart` (int8 {−1,0,+1}, shape (14,)/S+(14,)).
- `ketu/calculations.py:497-544` — `DECL_STANDSTILL_EPS = 0.001` (+ rationale
  comment) and the v1.5 scalar `is_ascending_declination(jd, body)` to contrast.
- `ketu/composite/api.py:269-308` — composite δ-speed derived from frozen (λ,β),
  not parent-midpoint (DSPD-03 trap).

### Files Phase 41 edits — version source-of-truth (all THREE)
- `pyproject.toml:7` — `version = "1.7.0"` → `1.8.0`
- `ketu/__init__.py:57` — `__version__ = "1.7.0"` → `1.8.0`
- `docs/source/conf.py:14-15` — `release` + `version` `"1.7.0"` → `1.8.0`

### Files Phase 41 edits — docs & changelogs
- `docs/source/api.md`, `docs/source/concepts.md` — new v1.8 surface (D-04).
- `docs/source/changelog.md`, `CHANGELOG.md`, `fr/CHANGELOG.md` — `[1.8.0]` entry.
- `UPGRADING.md` — v1.7→v1.8 entry (D-06) + legacy name-clean (D-02).
- `docs/locale/fr/LC_MESSAGES/*.po` (+ recompiled `.mo`) — FR translations for the
  new content AND the name-clean of `concepts.po` / `changelog.po`.

### Files Phase 41 edits — source docstrings (name-clean, D-03)
- `ketu/synastry/__init__.py`, `ketu/synastry/core.py`,
  `ketu/aspects/calculator.py`, `ketu/houses/core.py`, `ketu/charts/core.py` —
  13 lines listed in D-03.

### Historical / background (read for context, NOT shipped or edited)
- `KETU-GAPS-declination.md` (repo root, untracked) — the original 2026-06-16
  gap-analysis that motivated v1.8 (Option B = the `body_decl_speed` patch was
  chosen). Background only; it already names Rahu/Kala but is internal and not
  part of the published library, so it is NOT in the cleanup scope.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The v1.5 `body_decl` docs precedent** — the closest analog for depth, table
  placement (CHART_DTYPE table in api.md), and the UPGRADING "dtype layout grows /
  named-access-safe / positional-must-adapt" structure. Phase 41 mirrors it,
  swapping in the new field and the generic (no-project-name) phrasing.
- **The 7 prior release-doc phases** (v1.1..v1.7) — the bump+tag+OIDC+smoke
  sequence is fully established; v1.7's Phase 39 is the most recent template.
- **Established generic phrasing already present** — `docs/source/changelog.md:93`
  ("Code using named field access … is unaffected. Code using positional access or
  `.view()` … must adapt") is the exact pattern for the v1.8 UPGRADING entry,
  minus the project name that follows it.

### Established Patterns
- **EN+FR doc parity via gettext** — `docs/source/*.md` (EN) +
  `docs/locale/fr/LC_MESSAGES/*.po`→`.mo` (FR). Convention: **commit the
  recompiled `.mo`** (else French renders English fallback). Repo history shows
  `.mo` versioned every docs phase.
- **Three version source-of-truth files** kept in lockstep (pyproject /
  `__init__` / conf.py).
- **Quality gates are BLOCKING in CI** — numpydoc validate, interrogate ≥95%,
  `make doctest`, mypy `--strict`, 100% coverage, full test suite. Because D-03
  touches docstrings, ALL of these must stay green.

### Integration Points
- Sphinx autodoc/numpydoc pulls docstrings from `ketu/` into the public API docs
  — this is WHY docstring name-cleaning (D-03) is in scope: a "Kala" left in a
  docstring would render on the public docs site.
- OIDC trusted publishing via `publish.yml` (Node-24 artifact actions already
  bumped, per PROJECT.md CI note) — release is push-main-+-tag triggered.

</code_context>

<specifics>
## Specific Ideas

- User's exact words on the framing: **"Aucune référence à Rahu et Kala, ce sont
  des projets privés pour l'instant. Ketu est la source de vérité, Kala et Rahu
  sont consommateurs et s'adaptent."** This is the governing constraint for ALL
  Phase 41 prose.
- Generic replacement vocabulary: EN "downstream consumers" / "the downstream ML
  consumer"; FR "consommateurs en aval".
- Preserve celestial-body names Rahu/Ketu/Lilith everywhere they denote a body.

</specifics>

<deferred>
## Deferred Ideas

- **Tests carry "kala" in oracle comments** (`tests/test_ketu.py`,
  `tests/test_aspect_presets.py`, `tests/synastry/test_dtype.py`,
  `tests/charts/test_dtype.py`) — NOT in scope: tests are neither shipped in the
  wheel nor rendered in public docs. If a future "scrub all internal references"
  pass is wanted, it's a separate, optional chore. Noted so it isn't forgotten;
  do not let it expand Phase 41.
- **HARMF-01** (rich `--harmonics` grammar) and **DECLA-F1** (declination
  synastry / timing / CLI) remain future candidates per REQUIREMENTS.md — not this
  milestone.

</deferred>

---

*Phase: 41-documentation-release-v1-8-0*
*Context gathered: 2026-06-17*
