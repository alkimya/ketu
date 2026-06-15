---
phase: 39-documentation-release-v1-7-0
plan: "01"
status: complete
requirements: [ORB-04]
date: 2026-06-15
---

# 39-01 Summary — Document v1.7 fictitious-point orb (EN + FR)

## What was built

Documented the v1.7 fictitious-point orb change (Rahu/Ketu/Lilith now carry a
2° longitude orb, was 0°) in English source docs + README, then refreshed and
translated the French `.po` and recompiled the `.mo`.

### Task 1 — English docs + README (commit 73d1811)
- **docs/source/index.md**: bodies table now shows Rahu `2°`, **added a Ketu
  (Mean South Node) row** `2° / -0.052954°/day`, Lilith `2°`, Chiron `4°`.
- **docs/source/concepts.md**: added a *Fictitious Points: Rahu, Ketu, Lilith*
  subsection (2° orb history, point↔point=2°, Rahu↔Sun=7° worked examples); the
  **Rahu↔Ketu Opposition filter** with its **tautological** rationale (Ketu is
  the exact 180° opposite of Rahu by construction, so a non-zero orb would emit
  a permanent tautological Opposition — engine suppresses *only* that
  pair+aspect); a **`v1.7 — fictitious-point orbs (MINOR, not patch)`** callout
  (aspect RESULTS change → Kala must opt in deliberately, not a neutral
  `pip install -U`). Fixed the stale "zero-orb bodies" wording in the
  declination section to qualify longitude=2° (v1.7) vs the independent 0.5°
  declination floor.
- **docs/source/api.md**: `MIN_DECL_ORB` note no longer calls them flatly
  zero-orb; qualifies longitude orb 2° (v1.7) vs the 0.5° declination floor.
- **README.md**: bodies table corrected to match `ketu/core.py` — Rahu/Ketu/
  Lilith `2°`, id-11 relabelled **Ketu (Mean South Node)** (was "True North
  Node"), Chiron `4°`.

### Task 2 — French translation + .mo recompile (commit aad3cbc)
- `make gettext` + `make update-po` merged the new/changed msgids into the FR
  `.po` for index/concepts/api.
- Translated every new and fuzzy `msgstr` (no English fallback), cleared fuzzy
  flags: *Points fictifs*, *filtre d'opposition Rahu↔Ketu* (**tautologique**,
  *Nœud Sud*, *opposé à Rahu par construction*), the **MINOR** / *version mineure
  et non un correctif* / *Kala doit traiter la mise à jour comme délibérée*
  callout, and the declination-independence note.
- `make build-mo` recompiled the `.mo` binaries.
- `sphinx-intl stat`: **0 fuzzy / 0 untranslated** for index.po, concepts.po,
  api.po. `.mo` are newer than their `.po`.

## Verification
- `grep -qi tautolog docs/source/concepts.md` ✓
- `grep -q MINOR docs/source/concepts.md` ✓
- `grep -q "Ketu (Mean South Node)" README.md` ✓
- index.md / README orb tables match `ketu/core.py` (ids 10/11/12 = 2, 13 = 4) ✓
- FR stat clean (0/0) on all three pages ✓

## Deviations
- **Executor restart (orchestrator-side).** The first parallel worktree
  executor completed Task 1 correctly but never committed and stalled on
  cosmetic MD060 table-alignment lint before starting Task 2; its turn ended
  with uncommitted work. SendMessage/continuation was unavailable in this
  runtime, so the orchestrator salvaged the worktree's verified Task-1 diff
  (`git apply --3way` onto main, after confirming the table values matched
  `core.py`), removed the abandoned worktree, then finished Task 2 inline. Net
  result is identical to the plan; the only change is two atomic commits on
  `main` instead of a worktree branch.
- Out of scope (left for 39-02): the POT merge also touched `changelog.po`/
  `changelog.mo` — reverted here so the changelog i18n stays in 39-02's domain.

## Scope boundary respected
No changes to CHANGELOG.md, UPGRADING.md, pyproject.toml, ketu/__init__.py, or
docs/source/conf.py (all 39-02).
