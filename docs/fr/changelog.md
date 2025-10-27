# Changelog

Tous les changements notables de Ketu sont documentés ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-27

### Ajouté

- Configuration complète pour publication sur PyPI
- `pyproject.toml` avec métadonnées et dépendances
- `requirements.txt` pour installation simple
- Exports publics dans `ketu/__init__.py`
- README enrichi avec exemples d'utilisation
- Badges PyPI, Python versions et licence
- MANIFEST.in pour distribution des fichiers
- GitHub Actions pour tests automatiques (CI)
- GitHub Actions pour publication automatique sur PyPI
- Workflow de tests sur Python 3.9 à 3.13
- Point d'entrée CLI `ketu` pour ligne de commande
- Support de 13 corps célestes (ajout du Nœud Nord)
- Documentation française et anglaise

### Modifié

- Tests unitaires corrigés et validés
- Module `timea.py` renommé en `_timea.py` (privé)
- Structure du package optimisée pour distribution
- Documentation alignée avec la nouvelle structure

### Technique

- Python 3.10-3.13 supportés et testés
- Configuration pytest dans pyproject.toml
- Configuration coverage pour analyse de code
- Package installable via `pip install ketu`
- Compatible avec les environnements virtuels

## [0.1.0] - 2024-01-XX

### Ajouté

- Interface CLI interactive pour calculer les positions et aspects
- Calcul des positions planétaires via pyswisseph
- Détection des aspects majeurs avec orbes
- Conversion entre systèmes temporels (UTC, Julien)
- Détection des rétrogradations
- Documentation complète avec Sphinx et MyST
- Package PyPI installable
- Tests unitaires de base

### Fonctionnalités

- Support de 10 planètes + Rahu + Lilith
- 7 aspects majeurs (conjonction à opposition)
- Calcul des signes zodiacaux
- Système d'orbes basé sur Abu Ma'shar
- Cache LRU pour optimiser les performances

### Technique

- Python 3.9+ requis
- Dépendances : numpy, pyswisseph
- Architecture modulaire
- Code documenté et typé

## [0.0.1] - 2023-01-XX

### Initial

- Prototype de base
- Calculs simples de positions
- Interface ligne de commande

---

## Convention de versioning

- **MAJOR** : Changements incompatibles de l'API
- **MINOR** : Ajout de fonctionnalités rétro-compatibles
- **PATCH** : Corrections de bugs rétro-compatibles

## Liens

- [Comparaison des versions](https://github.com/alkimya/ketu/compare/)
- [Toutes les releases](https://github.com/alkimya/ketu/releases)
