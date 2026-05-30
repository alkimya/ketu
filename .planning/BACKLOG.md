# Backlog

Idées et chantiers identifiés mais non planifiés dans le milestone courant. À promouvoir dans un milestone futur via `/gsd:new-milestone` ou `/gsd:review-backlog`.

---

## v1.4 (candidat)

### Aspects data-driven + harmoniques dynamiques

**Origine :** Phase 25 (Documentation) — relecture de `docs/source/concepts.md` par Loc le 2026-05-30. La section *Harmonic Theory* exposait une incohérence : le texte parlait de « fractions de 180° par 30° » alors que H5/H9/H10 (quintiles, noviles, deciles) divisent le **cercle entier (360°)**, pas le demi-cercle. La doc a été corrigée (commit `b6d1620`, branche `docs/fix-harmonic-theory-concepts`) mais le **code** garde les 14 aspects hardcodés.

**Vision (Loc) :** retirer Quintile/Biquintile/Novile/Binovile/Quadrinovile/Decile/Tredecile (les 7 aspects full-circle H5/H9/H10) du set **par défaut**, et offrir un mécanisme pour **activer dynamiquement les aspects d'une harmonique donnée** plutôt qu'un set figé à 14.

**Travail attendu :**

1. **Refactor data-driven** — remplacer les constantes d'aspects éparpillées dans `ketu/aspects/` par une table de données : `Aspect(name, angle, harmonic, coefficient, symbol)`. Le moteur itère sur la table, plus rien de hardcodé dans la logique de détection.
2. **Sélection par harmonique** — API pour composer un set d'aspects à partir d'une liste d'harmoniques (ex. `aspects_for_harmonics([1, 2, 3, 6])`), en plus des presets existants.
3. **Défaut sans H5/H9/H10** — le set par défaut ne contient plus que les harmoniques demi-cercle (1, 2, 3, 6 → 7 aspects). Les minor aspects restent disponibles mais opt-in.
4. **Migration / breaking change** — c'est un breaking change de l'API publique (set d'aspects + coefficients + presets `CLASSICAL/TRADITIONAL/EXTENDED`). À documenter dans CHANGELOG + UPGRADING. Coordination Kala possible.
5. **Doc EN + FR** — `concepts.md` (table Harmonic Theory), `api.md`, + régénération gettext FR.
6. **Tests** — couvrir la table, la sélection par harmonique, le nouveau défaut, la rétrocompat des presets.

**Pourquoi pas en v1.3 :** trop gros pour les dernières heures avant la release 1.3.0 ; hors axe BINDING du milestone (Quality→Refactor→Spike→Chiron→Docs→Release) ; empilerait un 2e breaking change non roadmappé sur le 13→14 déjà assumé ; défaire la doc EN/FR tout juste figée. Décision Loc + Sophie 2026-05-30 : doc-fix maintenant, refactor en v1.4.

**Taille estimée :** une phase entière (refactor + API + migration + tests + doc bilingue).
