# Exemples Ketu

Ce dossier contient des exemples pratiques d'utilisation de la bibliothèque Ketu.

## Liste des exemples

### 01 - Positions planétaires de base

**Fichier**: [`01_basic_positions.py`](01_basic_positions.py)

Calculs fondamentaux :

- Conversion de dates en jour julien
- Obtention des positions (longitude, latitude, distance)
- Détermination des signes zodiacaux
- Détection des rétrogradations

```bash
python examples/01_basic_positions.py
```

### 02 - Aspects astrologiques

**Fichier**: [`02_aspects.py`](02_aspects.py)

Calculs d'aspects :

- Aspect entre deux planètes spécifiques
- Calcul de tous les aspects du moment
- Filtrage par orbe (serrés, exacts)
- Présentation détaillée

```bash
python examples/02_aspects.py
```

### 03 - Séries temporelles

**Fichier**: [`04_time_series.py`](04_time_series.py)

Calculs sur plusieurs jours :

- Évolution des positions planétaires
- Détection des changements de signe
- Périodes de rétrogradation
- Statistiques (min, max, vitesse moyenne)

```bash
python examples/04_time_series.py
```

## Utilisation

### Prérequis

```bash
pip install ketu
# ou depuis les sources :
pip install -e .
```

### Exécution

Tous les exemples sont des scripts Python autonomes :

```bash
# Depuis la racine du projet
python examples/01_basic_positions.py
python examples/02_aspects.py
# etc.

# Ou rends-les exécutables
chmod +x examples/*.py
./examples/01_basic_positions.py
```

## Documentation complète

Pour plus de détails, consulte la documentation :

- [Guide de démarrage rapide](../docs/source/quickstart.md)
- [Référence API](../docs/source/api.md)
- [Concepts astrologiques](../docs/source/concepts.md)
- [Documentation en ligne](https://ketu.readthedocs.io)

## Cas d'usage

### Analyse de transit

```python
# Voir exemple 04 - Séries temporelles
detect_sign_changes(start_date, 365, 0)  # Soleil sur 1 an
```

### Recherche d'aspects serrés

```python
# Voir exemple 02 - Aspects
tight_aspects = [asp for asp in aspects if abs(asp[3]) < 1]
```

## Conseils

### Performance

Les calculs utilisent un cache LRU automatique. Pour des boucles sur de nombreuses dates :

```python
# Vide le cache si nécessaire
ketu.body_properties.cache_clear()
```

---

Pour toute question : <https://github.com/alkimya/ketu/issues>
