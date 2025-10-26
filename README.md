# Ketu

[![PyPI version](https://badge.fury.io/py/ketu.svg)](https://badge.fury.io/py/ketu)
[![Python Versions](https://img.shields.io/pypi/pyversions/ketu.svg)](https://pypi.org/project/ketu/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ketu** est une bibliothèque Python légère pour calculer les positions des corps astronomiques (Soleil, Lune, planètes et Nœud moyen aka Rahu) et générer des calendriers basés sur les aspects astrologiques.

![Terminal screen](https://github.com/alkimya/ketu/blob/main/res/screen.png)

## ✨ Fonctionnalités

- 🌍 **Calcul de positions planétaires** pour 13 corps célestes (Soleil, Lune, Mercure, Venus, Mars, Jupiter, Saturne, Uranus, Neptune, Pluton, Rahu/Nœud Nord, Lilith)
- ⭐ **Détection de 7 aspects majeurs** (Conjonction, Semi-sextile, Sextile, Carré, Trigone, Quinconce, Opposition)
- 🔄 **Détection des rétrogradations** et mouvements planétaires
- 🕐 **Conversion entre systèmes temporels** (UTC, Jour Julien)
- 🎯 **Système d'orbes** basé sur Abu Ma'shar (787-886) et Al-Biruni (973-1050)
- 🖥️ **Interface CLI interactive** pour une utilisation sans programmation
- 📊 **API Python simple** pour une intégration dans tes projets

## 📦 Installation

### Depuis PyPI (recommandé)

```bash
pip install ketu
```

### Depuis les sources

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
pip install -e .
```

## 🚀 Démarrage rapide

### Mode interactif (CLI)

Lance simplement la commande `ketu` et réponds aux questions :

```bash
ketu
```

Tu seras invité à entrer :

- Une date (format ISO : `2020-12-21`)
- Une heure (format ISO : `19:20`)
- Un fuseau horaire (ex : `Europe/Paris`)

Le programme affichera ensuite :

- Les positions de tous les corps célestes dans les signes zodiacaux
- Tous les aspects entre les planètes avec leurs orbes

### Utilisation programmatique

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Définir une date et heure
dtime = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
jday = ketu.utc_to_julian(dtime)

# Afficher les positions des planètes
ketu.print_positions(jday)

# Afficher les aspects entre les planètes
ketu.print_aspects(jday)
```

### Exemples avancés

#### Calculer la position d'une planète

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Convertir en jour Julien
dtime = datetime(2024, 10, 26, 12, 0, tzinfo=ZoneInfo("UTC"))
jday = ketu.utc_to_julian(dtime)

# Obtenir la longitude du Soleil (body id = 0)
sun_long = ketu.long(jday, 0)
print(f"Longitude du Soleil : {sun_long:.2f}°")

# Obtenir le signe zodiacal
sign, deg, mins, secs = ketu.body_sign(sun_long)
print(f"Position : {ketu.signs[sign]} {deg}°{mins}'{secs}\"")
```

#### Vérifier si une planète est rétrograde

```python
import ketu

# Mars (body id = 4)
if ketu.is_retrograde(jday, 4):
    print("Mars est rétrograde")
else:
    print("Mars est directe")
```

#### Calculer tous les aspects à une date

```python
import ketu

# Calculer tous les aspects
aspects_data = ketu.calculate_aspects(jday)

# Parcourir les aspects
for aspect in aspects_data:
    body1, body2, i_asp, orb = aspect
    print(f"{ketu.body_name(body1)} - {ketu.body_name(body2)}: "
          f"{ketu.aspects['name'][i_asp].decode()} (orbe: {orb:.2f}°)")
```

## 📚 Documentation complète

La documentation complète est disponible sur [ReadTheDocs](https://ketu.readthedocs.io) (en français).

Sections disponibles :

- **Installation** : Guide d'installation détaillé
- **Quickstart** : Tutoriel de démarrage rapide
- **Concepts** : Explication des concepts astrologiques et astronomiques
- **API Reference** : Documentation complète de toutes les fonctions
- **Examples** : Exemples d'utilisation avancés

## 🛠️ Prérequis

- Python 3.9 ou supérieur
- `numpy` >= 1.20.0 : Calculs numériques et tableaux
- `pyswisseph` >= 2.10.0 : Interface aux éphémérides Swiss Ephemeris

**Note** : La dépendance à `pyswisseph` sera supprimée dans une version future au profit d'une implémentation pure numpy.

## 📋 Corps célestes supportés

| Corps | ID | Orbe | Vitesse moyenne (°/jour) |
|-------|-----|------|--------------------------|
| Soleil | 0 | 12° | 0.986 |
| Lune | 1 | 12° | 13.176 |
| Mercure | 2 | 8° | 1.383 |
| Vénus | 3 | 8° | 1.200 |
| Mars | 4 | 10° | 0.524 |
| Jupiter | 5 | 10° | 0.083 |
| Saturne | 6 | 10° | 0.034 |
| Uranus | 7 | 6° | 0.012 |
| Neptune | 8 | 6° | 0.007 |
| Pluton | 9 | 4° | 0.004 |
| Rahu (Nœud moyen) | 10 | 0° | -0.013 |
| Nœud Nord (vrai) | 11 | 0° | -0.013 |
| Lilith (Apogée moyen) | 12 | 0° | 0.113 |

## 🎯 Aspects supportés

| Aspect | Angle | Coefficient d'orbe |
|--------|-------|-------------------|
| Conjonction | 0° | 1 |
| Semi-sextile | 30° | 1/6 |
| Sextile | 60° | 1/3 |
| Carré | 90° | 1/2 |
| Trigone | 120° | 2/3 |
| Quinconce | 150° | 5/6 |
| Opposition | 180° | 1 |

## 🗺️ Roadmap

- [ ] Suppression de la dépendance à pyswisseph
- [ ] Implémentation pure numpy des calculs planétaires
- [ ] Recherche d'aspects exacts entre deux dates
- [ ] Génération de calendriers d'aspects
- [ ] API pour les progressions et directions
- [ ] Support de plus de corps célestes (astéroïdes, etc.)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésite pas à :

- Ouvrir une issue pour signaler un bug ou proposer une fonctionnalité
- Soumettre une pull request
- Améliorer la documentation

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour plus de détails.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Swiss Ephemeris pour les données éphémérides précises
- Abu Ma'shar (787-886) et Al-Biruni (973-1050) pour leur travail fondateur sur les orbes planétaires

## 📧 Contact

Loc Cosnier - [@alkimya](https://github.com/alkimya)

Projet : [https://github.com/alkimya/ketu](https://github.com/alkimya/ketu)

---

Fait avec ❤️ pour la communauté astrologique
