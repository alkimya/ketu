# Changelog

Tous les changements notables de Ketu sont documentés ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### À venir

- Suppression de la dépendance à pyswisseph
- Implémentation pure numpy des calculs planétaires
- Recherche d'aspects exacts entre deux dates
- Génération de calendriers d'aspects
- API pour les progressions et directions

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
