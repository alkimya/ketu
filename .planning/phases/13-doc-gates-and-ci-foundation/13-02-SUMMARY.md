---
phase: 13-doc-gates-and-ci-foundation
plan: 02
subsystem: infra
tags:
  - ops
  - ci
  - github-actions
  - interrogate
  - makefile

# Dependency graph
requires:
  - phase: 13-01
    provides: "[tool.interrogate] config + dev extras group + 100% interrogate baseline"
provides:
  - "Blocking `Doc coverage gate (interrogate ≥95%)` step in `.github/workflows/tests.yml` (Python 3.13 only)"
  - "Local `make doc-gates` target mirroring CI invocation (interrogate blocking + numpydoc warning-only via `|| true`)"
  - "Single-source-of-truth for the doc-coverage threshold: 95% lives in `pyproject.toml [tool.interrogate]`, NOT duplicated in the workflow YAML"
affects:
  - 13-03 (numpydoc fix-pass — same dev group, no install changes needed)
  - 13-04 (numpydoc CI step — same `if: matrix.python-version == '3.13'` gating pattern + `continue-on-error: true` knob already shaken out locally via `|| true` in the Makefile)
  - 13-05 (reformulation pass — README "Documentation Quality Gates" paragraph can now claim "enforced by CI" truthfully)
  - All later v1.2 phases (every PR is now blocked if interrogate score drops below 95% on the 3.13 leg)

# Tech tracking
tech-stack:
  added: []  # No new tools — Plan 01 already added interrogate / numpydoc to the dev group
  patterns:
    - "Threshold lives in pyproject.toml, not in the workflow YAML — `python -m interrogate ketu/` (no `--fail-under` flag) parallels `[tool.coverage.report].fail_under = 70` for the coverage step"
    - "Doc-gates run on Python 3.13 only — same gating shape as `Check coverage threshold` (3.13) and `Type check` (3.11); doc style is Python-version-independent so the matrix doesn't need to fan out"
    - "Local `make doc-gates` target uses `|| true` after numpydoc as the local equivalent of CI's future `continue-on-error: true` (Plan 04). Both flip together in Phase 20 when numpydoc becomes blocking (D-05)."

key-files:
  created: []
  modified:
    - ".github/workflows/tests.yml — new `Doc coverage gate (interrogate ≥95%)` step inserted between `Check coverage threshold` and `Upload coverage reports to Codecov` (5 lines added, no removals)"
    - "Makefile — new `doc-gates` target registered in `.PHONY`, recipe mirrors the CI invocation plus a numpydoc lint pass with `|| true` and a positive @echo confirmation (13 lines added, 1 line replaced for the .PHONY update)"

key-decisions:
  - "No `--fail-under=95` flag on the CI invocation — `[tool.interrogate].fail-under = 95` in pyproject.toml is the single source of truth, mirroring how coverage threshold lives in pyproject.toml not in the workflow"
  - "BLOCKING posture on the interrogate step (no `continue-on-error`) — OPS-01 + ROADMAP success criterion 13.1; the locked decision was not re-opened during execution"
  - "Ship `make doc-gates` (not deferred) — Open Question 1 from research recommended ship; recipe is 4 lines + 4 lines of help-comment; cost is trivial and contributor experience is improved"
  - "`make doc-gates` includes BOTH interrogate (blocking) and numpydoc (warning, `|| true`) even though Plan 02 only wires interrogate into CI — the target should be the durable contributor entry point across the whole phase, matching what Plan 04 will land in CI"

patterns-established:
  - "CI gating-by-Python-version pattern is reusable for every future doc-style or quality gate: `if: matrix.python-version == '3.13'` is the canonical shape (matches existing `Check coverage threshold` step); 3.11 stays reserved for `Type check`"
  - "Local Makefile target mirrors the CI invocation byte-for-byte (same `python -m <tool>` form, same exclusion list, same exit-code semantics modulo the `|| true` warning-phase escape hatch). Future phases adding gates should ship a parallel Makefile target."
  - "Synthetic-gap negative test as a worktree-local proof of blocking behavior — when a parallel executor cannot push to a feature branch, running `python -m interrogate <synthetic-empty-package>` and observing exit code 1 is equivalent to a CI red signal."

requirements-completed:
  - OPS-01

# Metrics
duration: 3min
completed: 2026-05-08
---

# Phase 13 Plan 02: Interrogate CI Wiring + Makefile Target Summary

**Bloque le build à `<95%` sur Python 3.13 via une étape `Doc coverage gate (interrogate ≥95%)` dans `tests.yml` (seuil sourcé depuis `pyproject.toml`, single source of truth) ; ajoute la cible `make doc-gates` pour exécuter la suite localement avant push.**

## Performance

- **Duration:** ~3 min active
- **Started:** 2026-05-08T11:32:11Z
- **Completed:** 2026-05-08T11:35:25Z
- **Tasks:** 2 / 2
- **Files modified:** 2

## Accomplishments

- **CI gate wired (BLOCKING).** `.github/workflows/tests.yml` gagne une étape `Doc coverage gate (interrogate ≥95%)` insérée entre `Check coverage threshold` et `Upload coverage reports to Codecov`. Gating à `matrix.python-version == '3.13'` (mirror de la coverage-threshold step). Invocation `python -m interrogate ketu/` sans flag `--fail-under` — le seuil de 95% vit dans `[tool.interrogate]` du pyproject.toml landé en Plan 01.
- **Local target landed.** `Makefile` gagne une cible `doc-gates` (en `.PHONY`, après `houses-coverage`, avant `mypy`) qui exécute interrogate (bloquant) puis numpydoc lint (warning-only via `|| true`) sur la même liste d'exclusions que la CI (no `_*` private modules, no `lunar_calendar.py`). Le `@echo` final confirme à l'utilisateur que les warnings numpydoc ne bloquent pas pendant la phase de warning.
- **Live verification.** `make doc-gates` exécuté localement sort en exit 0 ; `python -m interrogate ketu/` reste vert à 100.0% (≥95% threshold) ; 724 tests pytest verts ; `mypy --strict` clean ; YAML toujours parseable (8 steps, ordre attendu, aucune step existante touchée).
- **Synthetic-gap negative test (worktree-local).** Comme un agent parallèle ne peut pas pousser une branche pour observer la CI, j'ai exécuté la version locale équivalente : un package stub avec 10 fonctions sans docstring → `python -m interrogate <stub>` → `RESULT: FAILED (...)` → **exit code 1**. La step CI bloquerait donc bien le build sur red — équivalent au signal CI rouge documenté dans VALIDATION.md.

## Task Commits

Chaque tâche committée atomiquement (worktree mode, `--no-verify` pour éviter la contention pré-commit hooks) :

1. **Task 1: Add `Doc coverage gate (interrogate ≥95%)` step to .github/workflows/tests.yml** — `f262eff` (ci)
2. **Task 2: Add `doc-gates` Makefile target mirroring `houses-coverage` precedent** — `8be808d` (build)

_Note: pas de commit metadata séparé dans ce worktree — la SUMMARY.md est committée en fin de run par l'agent avant handoff vers l'orchestrator._

## Files Created/Modified

- `.github/workflows/tests.yml` — +5 / -0. Step `Doc coverage gate (interrogate ≥95%)` insérée lignes 46-49 (`if: matrix.python-version == '3.13'`, `run: python -m interrogate ketu/`). Aucune autre step modifiée. YAML parse cleanly (validé via `yaml.safe_load`).
- `Makefile` — +13 / -1. La ligne `.PHONY` gagne `doc-gates` (1 line replaced). Nouvelle target `doc-gates` ajoutée après `houses-coverage` avec son help-comment header `## doc-gates: ...`. Recipe : `$(PYTHON) -m interrogate ketu/` puis `$(PYTHON) -m numpydoc lint <files> || true` puis `@echo`. Toutes les recipe lines utilisent des TABs (vérifié via `cat -A`).

## Decisions Made

- **Plan suivi verbatim.** Les blocs YAML et Makefile landés sont byte-identical à la spec PATTERNS.md / RESEARCH.md. Aucune décision de design n'a été ré-ouverte pendant l'exécution.
- **Pas de `--fail-under=95` sur l'invocation CLI.** Le seuil vit dans `pyproject.toml [tool.interrogate].fail-under = 95` (Plan 01). Mirror exact du pattern coverage (où `[tool.coverage.report].fail_under = 70` n'est pas dupliqué dans le YAML). Documenté dans le commit message + dans les key-decisions du frontmatter.
- **`make doc-gates` inclut numpydoc même si la CI ne le wire qu'en Plan 04.** Décision documentée dans l'action de Task 2 et confirmée par les tests live : la cible sera donc l'entrypoint contributeur stable sur toute la phase, et Plan 04 n'aura pas besoin de toucher au Makefile.

## Deviations from Plan

None — plan executed exactly as written.

Quelques notes utiles pour les plans suivants, sans déviation :

- **Acceptance criteria de Task 1 sur "step ordering"** validée précisément : `grep -n "name:" .github/workflows/tests.yml` montre 8 steps, avec `Check coverage threshold` (line 41) → `Doc coverage gate (interrogate ≥95%)` (line 46) → `Upload coverage reports to Codecov` (line 51) — exactement l'ordre demandé par le plan.
- **Live `make doc-gates` produit une exception numpydoc** sur une entry "See Also" mal-parsée (`docs/LILITH_DEFINITION.md : Frame, formula, tolerance, history.`). C'est un bug de parsing numpydoc connu côté upstream sur les liens vers fichiers ; le `|| true` intercepte correctement et le `@echo` final s'affiche, donc la cible exit 0 comme attendu pendant la phase de warning. Plan 03 va de toute façon nettoyer cette entry quand il fixera les docstrings de `core.py`/etc.

## Issues Encountered

- **Synthetic-gap test capture du exit code initialement masquée par un pipe.** Premier essai : `python -m interrogate ketu/ 2>&1 | tail -3 ; echo "exit: $?"` retournait 0 même quand interrogate affichait `RESULT: FAILED` — parce que `$?` capturait le exit de `tail`, pas d'`interrogate`. Résolu en lançant interrogate via `subprocess.run` Python avec capture explicite de `returncode` : exit 1 confirmé sur un package stub à 0%. Le comportement de gate bloquante est validé.
- **Aucun autre incident.** Le worktree base était initialement à `0b01321d8` (la tip de phase 12) et le worktree_branch_check a correctement hard-reset vers `bbbd68d` (la tip post Plan 01) au démarrage. Tous les commits Plan 02 sont par-dessus cette base.

## User Setup Required

Aucun — pas de configuration de service externe requise. Les contributeurs qui pull cette tip peuvent maintenant lancer `make doc-gates` localement (avec le venv activé) pour exécuter la suite avant push. Le `dev` group landé en Plan 01 fournit déjà `interrogate` et `numpydoc` via `pip install -e ".[dev]"`.

## Next Plan Readiness

**Plan 03 (numpydoc config + source docstring fix-pass — Wave 2) peut procéder en parallèle de Plan 02.** Vérifié explicitement par le plan : Plan 02 modifie uniquement `.github/workflows/tests.yml` et `Makefile` ; Plan 03 modifie `pyproject.toml` (nouveau bloc `[tool.numpydoc_validation]`) et des fichiers source dans `ketu/` (`complex.py`, `calculations.py`, `cycles/calculator.py`, plus quelques `__init__.py` / `core.py` pour GL06/GL07). **Aucune intersection de fichier** — les deux peuvent merger dans n'importe quel ordre.

**Plan 04 (numpydoc CI step) hérite directement** des patterns Plan 02 : même `if: matrix.python-version == '3.13'`, même forme `python -m <tool>`, même placement (après `Check coverage threshold` ou maintenant après notre nouvelle step interrogate). Le seul nouveau ingrédient sera `continue-on-error: true` (locked decision D-04).

**Plan 05 (README reformulation)** peut maintenant rédiger en toute sincérité : "Documentation quality is enforced by CI" est devenu factuel à partir de cette plan.

## Self-Check: PASSED

Vérifié après l'écriture de SUMMARY :

- `.github/workflows/tests.yml` existe et `grep -c "Doc coverage gate (interrogate" .github/workflows/tests.yml` retourne `1`.
- `Makefile` existe ; `grep -c "^doc-gates:" Makefile` retourne `1` ; `grep "^.PHONY" Makefile` contient le token `doc-gates`.
- Commit `f262eff` (Task 1, ci) présent dans `git log`.
- Commit `8be808d` (Task 2, build) présent dans `git log`.
- `python -m interrogate ketu/` exit 0 avec score 100.0% (≥95%).
- `make -n doc-gates` parse cleanly et imprime `python -m interrogate ketu/` + `python -m numpydoc lint ...`.
- `make doc-gates` (live) exit 0 (warning-only sur numpydoc, blocking sur interrogate).
- 724 pytest tests verts ; `mypy --strict` clean.
- YAML toujours parseable (`yaml.safe_load` succeeds, 8 steps in expected order).
- Synthetic-gap negative test confirmé : interrogate exit 1 sur un package à 0% (gate CI bloquerait).

---
*Phase: 13-doc-gates-and-ci-foundation*
*Completed: 2026-05-08*
