# Exemples Ketu

Ce dossier contient des exemples pratiques d'utilisation de la bibliothèque Ketu.

## 📋 Liste des exemples

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

### 03 - Thème natal complet
**Fichier**: [`03_natal_chart.py`](03_natal_chart.py)

Génération de thème natal :
- Positions de toutes les planètes
- Signes zodiacaux et degrés
- Symboles de rétrogradation (℞)
- Aspects majeurs groupés par type
- Marqueurs d'orbe serrés (●/○)

```bash
python examples/03_natal_chart.py
```

### 04 - Séries temporelles
**Fichier**: [`04_time_series.py`](04_time_series.py)

Calculs sur plusieurs jours :
- Évolution des positions planétaires
- Détection des changements de signe
- Périodes de rétrogradation
- Statistiques (min, max, vitesse moyenne)

```bash
python examples/04_time_series.py
```

### 05 - Personnalisation des orbes
**Fichier**: [`05_custom_orbs.py`](05_custom_orbs.py)

Gestion des orbes :
- Comparaison de différents réglages
- Orbes serrés vs larges
- Configuration personnalisée
- Sauvegarde et restauration

```bash
python examples/05_custom_orbs.py
```

## 🚀 Utilisation

### Prérequis

Assure-toi que Ketu est installé :

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

### Modification

Tu peux facilement modifier les exemples :

```python
# Dans n'importe quel exemple, change la date :
dt = datetime(2024, 1, 1, 12, 0, tzinfo=ZoneInfo("Europe/Paris"))

# Ou le corps céleste :
mercury_position = ketu.long(jday, 2)  # 2 = Mercure
```

## 📚 Documentation complète

Pour plus de détails, consulte la documentation :

- [Guide de démarrage rapide](../docs/source/quickstart.md)
- [Référence API](../docs/source/api.md)
- [Concepts astrologiques](../docs/source/concepts.md)
- [Documentation en ligne](https://ketu.readthedocs.io)

## 🎯 Cas d'usage

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

### Thème natal personnalisé

```python
# Voir exemple 03 - Thème natal
theme_natal(1990, 5, 15, 14, 30, "Europe/Paris")
```

## 💡 Conseils

### Performance

Les calculs utilisent un cache LRU automatique. Pour des boucles sur de nombreuses dates :

```python
# Vide le cache si nécessaire
ketu.body_properties.cache_clear()
```

### Orbes

Les orbes par défaut suivent Abu Ma'shar. Pour des calculs plus serrés :

```python
import numpy as np
original = ketu.bodies["orb"].copy()
ketu.bodies["orb"] *= 0.7  # Réduit de 30%
# ... calculs ...
ketu.bodies["orb"] = original  # Restaure
```

### Bodies IDs

```python
# IDs des corps célestes
0  = Soleil       5  = Jupiter     10 = Rahu (Nœud moyen)
1  = Lune         6  = Saturne     11 = Nœud Nord (vrai)
2  = Mercure      7  = Uranus      12 = Lilith (Apogée moyen)
3  = Vénus        8  = Neptune
4  = Mars         9  = Pluton
```

## 🤝 Contribution

Tu as un exemple intéressant à partager ? N'hésite pas à :
1. Créer un nouveau fichier `06_ton_exemple.py`
2. Ajouter une description dans ce README
3. Soumettre une pull request

## ⚠️ Note

Ces exemples utilisent des données éphémérides via Swiss Ephemeris. Les calculs sont précis pour l'astrologie moderne mais ne remplacent pas des calculs astronomiques de précision scientifique.

---

Pour toute question : https://github.com/alkimya/ketu/issues
