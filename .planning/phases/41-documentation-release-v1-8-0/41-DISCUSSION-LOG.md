# Phase 41: Documentation + Release v1.8.0 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-17
**Phase:** 41-documentation-release-v1-8-0
**Areas discussed:** Doc depth (+ name-clean steer), Legacy cleanup scope, Code-docstring scope

---

## Gray-area selection (entry point)

| Option | Description | Selected |
|--------|-------------|----------|
| Profondeur de la doc | Where/how deeply to document body_decl_speed; pages, example, constant + helper placement | ✓ |
| UPGRADING & Kala | Content of the v1.7→v1.8 upgrade guide for the dtype growth | (folded into doc scope) |
| Frontière Ketu/Rahu | How to phrase the "consumer computes no astronomy" boundary | (reframed by steer) |
| Gate de release | Exact go/no-go sequence + post-publish smoke | (folded — workflow is rodé) |

**User's choice:** "Profondeur de la doc. Je crois que le workflow est assez connu,
on révise un peu sur quoi mettre dans la doc."
**Notes:** Critical steer added: **"Aucune référence à Rahu et Kala, ce sont des
projets privés pour l'instant. Ketu est la source de vérité, Kala et Rahu sont
consommateurs et s'adaptent."** This reframed the whole phase: the release
mechanics are known and locked; the open work is documentation depth + a
project-name-free public framing. The boundary statement (DSPD-07) becomes a
generic library design principle, no project names.

---

## Legacy cleanup scope

| Option | Description | Selected |
|--------|-------------|----------|
| Nettoyer tout le legacy | Purge ALL Kala/Solaris project mentions everywhere (CHANGELOG, fr/CHANGELOG, UPGRADING, docs/source, .po/.mo), incl. already-published entries → generic "downstream consumers" | ✓ |
| Nouveau contenu seulement | Only the v1.8 entry is name-clean; historical entries left as-is | |
| Nettoyer seulement actifs | New content + only "living" files; freeze the historical changelog | |

**User's choice:** Nettoyer tout le legacy.
**Notes:** Accepts rewriting already-published changelog/upgrading entries to be
name-clean. Technical substance preserved; only project names swapped for the
generic term. Celestial-body names (Rahu/Ketu/Lilith) explicitly preserved —
the purge targets the *projects* (Rahu UI / Kala ML / Solaris), never the
astronomy terms (lunar nodes / Black Moon Lilith, body ids 10/11/12). Inventory:
CHANGELOG.md 11, UPGRADING.md 13, fr/CHANGELOG.md 4, docs/source/changelog.md 2,
docs/source/concepts.md 2, plus FR concepts.po / changelog.po.

---

## Code-docstring scope

| Option | Description | Selected |
|--------|-------------|----------|
| Docs + docstrings | Name-clean extends to source docstrings (rendered into public API docs via autodoc); re-run all quality gates + 1691 tests | ✓ |
| Docs seulement | Only standalone doc files; leave "Kala" in source docstrings (avoid touching code in a release phase) | |

**User's choice:** Docs + docstrings.
**Notes:** 13 docstring lines across 5 files (synastry/__init__.py,
synastry/core.py, aspects/calculator.py, houses/core.py, charts/core.py) render
into the public Sphinx API docs. Cleaning them means re-running numpydoc /
interrogate / make doctest / mypy --strict + the full suite (all green at Phase 40
close). Replace "(Kala)" / "Kala (the downstream ML consumer)" / "Kala's
positional contract" / "Kala adapts to Ketu" with generic equivalents; preserve
all technical meaning and any doctest examples verbatim.

---

## Claude's Discretion

- Exact generic-replacement wording ("downstream consumers" / "the downstream ML
  consumer" / "consommateurs en aval") as long as no project is named and meaning
  is preserved.
- Whether the changelog code example lives in concepts.md or api.md.
- Whether to add a dedicated doctest for `is_ascending_declination_chart` (prefer
  yes, per the doctest-as-gate convention) or keep the example as prose.

## Deferred Ideas

- Tests carry "kala" in oracle comments (test_ketu.py, test_aspect_presets.py,
  synastry/test_dtype.py, charts/test_dtype.py) — NOT in scope (tests aren't
  shipped or rendered); a future optional "scrub internal refs" chore.
- HARMF-01 (rich --harmonics grammar) and DECLA-F1 (declination synastry/timing/
  CLI) remain future candidates per REQUIREMENTS.md — not this milestone.
