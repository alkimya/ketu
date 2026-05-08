# Phase 13: Doc Gates & CI Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 13-doc-gates-and-ci-foundation
**Areas discussed:** Optional-deps group, numpydoc gate posture, Baseline cleanup scope, Aspirational refs cleanup

---

## Optional-deps group

| Option | Description | Selected |
|--------|-------------|----------|
| Nouveau `dev` | `[project.optional-dependencies].dev = [interrogate, numpydoc]`. CI fait `pip install -e .[dev,test]`. Sépare les outils de qualité du runtime AGPL pysweph. C'est ce que `tests.yml` installe déjà implicitement (`pip install -e .[dev]` puis fallback). | ✓ |
| Nouveau `docs-lint` | Groupe dédié `docs-lint = [interrogate, numpydoc]`. Plus sémantique mais multiplie les groupes. Sphinx reste dans son propre setup. | |
| Garder dans `test` | Comme dit la ROADMAP littéralement : `test = [pysweph, interrogate, numpydoc]`. Simple mais mélange une dep AGPL avec des outils de qualité. | |

**User's choice:** Nouveau `dev`
**Notes:** Préserve la séparation AGPL (pysweph reste seul dans `test`) et s'aligne avec la commande déjà câblée dans `tests.yml`. ROADMAP success criterion 13.1 dit "installed in `[project.optional-dependencies].test`" — décision : on s'écarte volontairement de la lettre de la ROADMAP pour préserver la ligne AGPL ; à mentionner dans le commit message du plan correspondant.

---

## numpydoc gate posture (when to flip warning → blocking)

| Option | Description | Selected |
|--------|-------------|----------|
| Phase 20 (release prep) | Le flip est une tâche explicite de Phase 20 (avec le bump 1.2.0). Cadence prévisible, déjà dans la roadmap. Cumule la dette si Phases 14-19 introduisent du code numpydoc-cassé. | ✓ |
| Phase 14 (premier nouveau module) | Gate blocking sur les nouveaux modules dès `ketu/charts/`, warning sur le legacy. Strict sur le neuf, tolérant sur l'ancien. Plus complexe à configurer. | |
| Direct blocking | Pas de phase de transition : gate clean dès Phase 13, blocking dès le merge. Implique de fixer 100% du legacy maintenant. Risque de scope creep. | |

**User's choice:** Phase 20 (release prep)
**Notes:** Le baseline cleanup (axe 3) couvre déjà les trous existants en Phase 13, donc la dette ne grossira pas — le warning suffit pour les nouveaux modules. Plan de Phase 20 doit explicitement contenir la tâche "flip numpydoc gate to blocking".

## numpydoc public scope

| Option | Description | Selected |
|--------|-------------|----------|
| Tout `ketu/` sauf `_private` | Scan récursif ; exclusions `__pycache__`, fichiers commençant par `_`, `lunar_calendar.py` (déjà omit dans coverage). Convention Python. | ✓ |
| Whitelist explicite | Liste blanche dans pyproject. Plus de contrôle mais maintenance à chaque nouveau sous-paquet. | |
| Que la surface API top-level | Seulement `ketu/__init__.py` `__all__`. Trop restrictif — laisse passer du code interne moche. | |

**User's choice:** Tout `ketu/` sauf `_private`
**Notes:** Aligne avec `[tool.coverage.run].omit` (qui exclut déjà `lunar_calendar.py`). Cohérence interrogate ↔ numpydoc ↔ coverage sur la même exclusion-list.

---

## Baseline cleanup scope

| Option | Description | Selected |
|--------|-------------|----------|
| Combler en Phase 13 (clean baseline) | ROADMAP 13.4 littéralement : 'any pre-existing gaps fixed in this phase, not deferred'. Audit + fixes + merge vert. Risque de scope qui gonfle. | ✓ |
| Combler ce qui est rapide, exclure le reste | Docstrings rapides ajoutées ; modules legacy exclus via `[tool.interrogate].exclude`. S'écarte de "clean baseline". | |
| Démarrer à 90%, monter à 95% en Phase 20 | Premier flip à 90% atteignable sans cleanup massif ; relèvement à 95% en Phase 20. Crée une nouvelle tension avec la ROADMAP. | |

**User's choice:** Combler en Phase 13 (clean baseline)
**Notes:** Une étape audit obligatoire en première sub-task du plan : énumérer chaque gap, classifier (missing / malformed / à exclure légitimement), et borner le travail. Si l'audit révèle plus de 2 jours de rédaction de docstrings, lever la main avant de plonger.

---

## Aspirational refs cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Remplacer par "enforced by CI" | CHANGELOG/README/MILESTONES gardent la mention reformulée : "Doc gates: interrogate ≥95% (enforced by CI in tests.yml)". Audit + edit chaque référence. La claim reste visible mais devient vraie. | ✓ |
| Supprimer simplement | Suppression totale des mentions dans les docs publiques. Plus simple mais les utilisateurs externes perdent l'info. | |
| Mix : public reformulé, .planning purgé | CHANGELOG/README → reformulé. `.planning/STATE.md`, `PROJECT.md`, `MILESTONES.md` → bullet "aspirationnel" → "wired (Phase 13)". Couvre les deux audiences. | |

**User's choice:** Remplacer par "enforced by CI"
**Notes:** L'utilisateur a choisi la reformulation publique (CHANGELOG/README). Décision implicite : `.planning/` n'est PAS dans le scope de cette reformulation — ces fichiers sont des tracking docs et seront mis à jour via le flow normal (`update_state`, milestone tracking) qui basculera "aspirationnel" vers "wired". Capturé en D-12.

---

## Claude's Discretion

- Pin de versions vs floor `>=X.Y` pour `interrogate` et `numpydoc` — décidé par le researcher selon la cadence PyPI.
- Step CI séparé vs piggyback sur `Type check` pour `numpydoc validate` — décidé par le planner selon le signal-to-noise du build log.
- Ordre des plans Phase 13 (audit → wire warning → fix gaps → flip interrogate blocking → reformuler refs) — séquencé par le planner.
- Knobs précis de `[tool.interrogate]` (`ignore-init-module`, `ignore-magic`, `verbose`) — défauts d'abord ; planner ajuste si besoin.
- Optionnel : cible `make doc-gates` pour exécution locale par les contributeurs avant push.

## Deferred Ideas

- Sphinx `-W` warnings as build gate — pas dans OPS-01/02 ; resurface en v1.3 si demandé.
- Pre-commit hook pour interrogate — quality-of-life ; pas dans la ROADMAP. Optionnel post-Phase 13.
- `fr/CHANGELOG.md` reformulation — c'est OPS-04 / Phase 20. Ne pas conflater avec OPS-01/02.
- Resserrement de `fail_under` projet de 70 → 90 — gate distinct, milestone-level avant clôture v1.2 ; pas du travail Phase 13.
- Overrides per-module numpydoc — seulement si la phase warning fait trop de bruit ; configuration par défaut d'abord.
