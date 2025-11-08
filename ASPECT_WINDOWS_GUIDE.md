# Guide: Aspect Windows API

## Vue d'ensemble

Le module `aspect_windows` fournit une API moderne pour calculer les fenêtres temporelles des aspects astrologiques avec :

- **3 moments clés** : Début (entrée dans l'orbe), Exactitude, Fin (sortie de l'orbe)
- **Détection automatique des rétrogradations** : Gère jusqu'à 3 passages exacts
- **Haute précision** : ±1 seconde sur le moment exact
- **API claire** : Utilise des namedtuples immutables
- **Performance** : Recherche vectorisée + raffinement par bissection

---

## Installation rapide

```python
from ketu import find_aspect_window, find_aspects_timeline
```

---

## 📘 API Niveau 1 : `find_aspect_window()`

### Usage basique

Trouve UNE fenêtre d'aspect autour d'une date de référence.

```python
from ketu import find_aspect_window

# Exemple : Pleine Lune (Opposition Soleil-Lune)
result = find_aspect_window(
    body1="Sun",
    body2="Moon",
    aspect="Opposition",
    around_date="2024-03-25",
    search_days=3
)

# Résultat : AspectWindow
# - body1, body2, aspect (str)
# - moments (list[AspectMoment])
# - retrograde_count (int)

if result.moments:
    moment = result.moments[0]
    print(f"Début:      {moment.begin}")
    print(f"Exactitude: {moment.exact}")
    print(f"Fin:        {moment.end}")
    print(f"Orbe:       {moment.orb_used}°")
    print(f"Mouvement:  {moment.motion}")  # 'direct' ou 'retrograde'
```

### Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `body1` | str/int | - | Premier corps (nom ou ID) |
| `body2` | str/int | - | Second corps (nom ou ID) |
| `aspect` | str/int/float | - | Aspect (nom, index, ou angle) |
| `around_date` | datetime/str/float | - | Date de référence (datetime, ISO, ou JD) |
| `search_days` | float | 30 | Jours de recherche avant/après |
| `custom_orb` | float | None | Orbe personnalisé (sinon calculé) |
| `detect_retrograde` | bool | True | Activer détection multi-passages |

### Exemples

#### 1. Nouvelle Lune (Conjonction)

```python
result = find_aspect_window(
    body1="Sun",
    body2="Moon",
    aspect="Conjunction",
    around_date="2024-04-08",
    search_days=2
)
# Durée typique : ~40 heures
```

#### 2. Orbe personnalisé

```python
# Orbe serré pour travail de précision
result = find_aspect_window(
    body1="Sun",
    body2="Moon",
    aspect="Opposition",
    around_date="2024-03-25",
    custom_orb=5.0  # Au lieu de 12° par défaut
)
# Durée réduite : ~22 heures au lieu de 52h
```

#### 3. Planètes lentes (Jupiter-Saturne)

```python
# Grande Conjonction de 2020
result = find_aspect_window(
    body1="Jupiter",
    body2="Saturn",
    aspect="Conjunction",
    around_date="2020-12-21",
    search_days=60  # Recherche plus large nécessaire
)
# Durée : ~120 jours !
```

---

## 📗 API Niveau 2 : `find_aspects_timeline()`

### Usage basique

Trouve PLUSIEURS aspects sur une période donnée.

```python
from ketu import find_aspects_timeline

# Tous les aspects Soleil-Lune en mars 2024
timeline = find_aspects_timeline(
    body1="Sun",
    body2="Moon",
    aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
    start_date="2024-03-01",
    end_date="2024-03-31"
)

# Résultat : Liste d'AspectWindow triés chronologiquement
for window in timeline:
    moment = window.moments[0]
    print(f"{window.aspect:12s}: {moment.exact}")
```

### Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `body1` | str/int | - | Premier corps |
| `body2` | str/int | - | Second corps |
| `aspects_list` | List[str/int] | Major aspects | Liste d'aspects à chercher |
| `start_date` | datetime/str/float | - | Date de début |
| `end_date` | datetime/str/float | - | Date de fin |
| `custom_orb` | float | None | Orbe personnalisé |
| `detect_retrograde` | bool | True | Détection rétrogradations |

### Exemples

#### 1. Cycle de lunaison mensuel

```python
timeline = find_aspects_timeline(
    body1="Sun",
    body2="Moon",
    aspects_list=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
    start_date="2024-03-01",
    end_date="2024-03-31"
)
# Résultat : ~9 aspects lunaires dans le mois
```

#### 2. Aspects Vénus-Mars sur l'année

```python
timeline = find_aspects_timeline(
    body1="Venus",
    body2="Mars",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
# Résultat : 4 aspects majeurs en 2024
```

---

## 🔍 Structures de données

### AspectMoment (namedtuple)

Représente un moment d'aspect unique.

```python
AspectMoment(
    begin=datetime,      # Entrée dans l'orbe
    exact=datetime,      # Moment exact
    end=datetime,        # Sortie de l'orbe
    orb_used=float,      # Orbe utilisé (degrés)
    motion='direct'      # 'direct' ou 'retrograde'
)
```

**Propriétés** :
- Immutable (namedtuple)
- Accès par attribut : `moment.exact`
- Accès par index : `moment[1]`
- Compatible NumPy

### AspectWindow (namedtuple)

Résultat complet d'une recherche d'aspect.

```python
AspectWindow(
    body1='Sun',
    body2='Moon',
    aspect='Opposition',
    moments=[AspectMoment(...)],  # 1-3 moments si rétrogradation
    retrograde_count=0
)
```

---

## ⚙️ Détection des rétrogradations

Quand une planète rétrograde pendant un aspect, il peut y avoir **3 moments exacts** :

```
Approche → Recul (rétro) → Approche finale
   ★          ★               ★
1er exact  2e exact        3e exact
```

### Exemple : Mars-Jupiter carré avec rétrogradation

```python
result = find_aspect_window(
    body1="Mars",
    body2="Jupiter",
    aspect="Square",
    around_date="2025-08-15",
    search_days=180,
    detect_retrograde=True  # Activé par défaut
)

# result.moments contiendra 3 AspectMoment si rétrogradation
# result.retrograde_count = 1

for i, moment in enumerate(result.moments, 1):
    print(f"Passage {i} ({moment.motion}):")
    print(f"  Exact: {moment.exact}")
```

---

## 📊 Spécifications d'aspects

### Par nom

```python
aspect="Conjunction"  # 0°
aspect="Semi-sextile" # 30°
aspect="Sextile"      # 60°
aspect="Square"       # 90°
aspect="Trine"        # 120°
aspect="Quincunx"     # 150°
aspect="Opposition"   # 180°
```

### Par index (0-6)

```python
aspect=0  # Conjunction
aspect=6  # Opposition
```

### Par angle

```python
aspect=180.0  # Opposition
aspect=90.0   # Square
```

---

## 🎯 Cas d'usage typiques

### 1. Calendrier lunaire complet

```python
# Nouvelles lunes et pleines lunes de l'année
lunations = find_aspects_timeline(
    body1="Sun",
    body2="Moon",
    aspects_list=["Conjunction", "Opposition"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)

for window in lunations:
    phase = "Nouvelle Lune" if window.aspect == "Conjunction" else "Pleine Lune"
    exact = window.moments[0].exact
    print(f"{phase}: {exact.strftime('%Y-%m-%d %H:%M UTC')}")
```

### 2. Alertes d'aspects exacts

```python
# Trouver quand un aspect devient exact (à la minute près)
result = find_aspect_window(
    body1="Venus",
    body2="Mars",
    aspect="Conjunction",
    around_date="2024-02-22",
    search_days=5
)

if result.moments:
    exact = result.moments[0].exact
    print(f"Conjonction Vénus-Mars exacte le {exact.strftime('%d %B %Y à %H:%M:%S UTC')}")
```

### 3. Durées d'aspects variables

```python
# Comparer durées avec différents orbes
for orb in [3.0, 6.0, 12.0]:
    result = find_aspect_window(
        body1="Sun",
        body2="Moon",
        aspect="Opposition",
        around_date="2024-03-25",
        custom_orb=orb
    )
    duration = (result.moments[0].end - result.moments[0].begin).total_seconds() / 3600
    print(f"Orbe {orb}° → Durée: {duration:.1f}h")

# Output:
# Orbe 3.0° → Durée: 13.2h
# Orbe 6.0° → Durée: 26.4h
# Orbe 12.0° → Durée: 52.7h
```

---

## ⚡ Performance

| Opération | Temps typique | Notes |
|-----------|---------------|-------|
| Aspect unique (rapides) | ~3-5 ms | Soleil-Lune |
| Aspect unique (lentes) | ~60 ms | Jupiter-Saturne |
| Timeline 1 mois | ~70 ms | 3-4 aspects |
| Timeline 1 an | ~200-500 ms | Dépend des corps |

**Précision** : ±1 seconde sur le moment exact

**Méthode** :
1. Grille adaptative vectorisée (détection rapide)
2. Interpolation quadratique (estimation)
3. Bissection itérative (raffinement à ±1s)

---

## 🔬 Comparaison avec ancienne API

| Critère | `find_aspect_timing()` | `find_aspect_window()` |
|---------|------------------------|-------------------------|
| Précision | ~6 heures (pas fixe) | ±1 seconde |
| Vitesse | 0.36 ms | 3.1 ms (8x plus lent) |
| Rétrogradations | ❌ Non | ✅ Oui |
| Timeline | ❌ Non | ✅ Oui |
| Orbe custom | ❌ Non | ✅ Oui |
| API | Tuple anonyme | Namedtuple |

**Recommandation** : Utiliser `find_aspect_window()` pour tous les nouveaux projets.

---

## 📝 Notes importantes

### Orbes par défaut

Les orbes sont calculés selon la formule traditionnelle :
```
orb = (orb_body1 + orb_body2) / 2 × aspect_coefficient
```

Exemples :
- Soleil-Lune Opposition : (12 + 12) / 2 × 1.0 = **12°**
- Mercure-Vénus Sextile : (8 + 10) / 2 × 1/3 = **3°**
- Jupiter-Saturne Conjonction : (10 + 10) / 2 × 1.0 = **10°**

### Gestion des fuseaux horaires

Les résultats sont toujours en **UTC**. Pour convertir en heure locale :

```python
from datetime import timezone
import zoneinfo

moment = result.moments[0]
utc_time = moment.exact
paris_time = utc_time.astimezone(zoneinfo.ZoneInfo("Europe/Paris"))
print(f"Heure de Paris : {paris_time}")
```

### Cas limites

```python
# Si aucun aspect trouvé
result = find_aspect_window(...)
if not result.moments:
    print("Aucun aspect dans la période de recherche")

# Si recherche trop étroite
result = find_aspect_window(
    ...,
    search_days=0.01  # Très étroit : 15 minutes
)
# Peut ne rien trouver même si aspect proche
```

---

## 🧪 Tests

Tests unitaires disponibles dans `tests/test_aspect_windows.py` :

```bash
pytest tests/test_aspect_windows.py -v
```

Couverture : **91%**

---

## 📚 Voir aussi

- `examples/05_aspect_windows.py` - Exemples complets
- `benchmark_aspect_windows.py` - Benchmarks de performance
- `ASPECT_TIMING_ANALYSIS.md` - Analyse technique des algorithmes

---

## ✨ Exemples avancés

### Suivi d'un transité sur plusieurs mois

```python
# Mars carré natal Soleil
natal_sun_lon = 120.0  # 0° Lion

# Simuler en créant un aspect personnalisé
# (nécessite adaptation du code pour longitude fixe)
```

### Export vers calendrier

```python
import icalendar
from datetime import timedelta

timeline = find_aspects_timeline(...)

cal = icalendar.Calendar()
for window in timeline:
    moment = window.moments[0]
    event = icalendar.Event()
    event.add('summary', f'{window.body1}-{window.body2} {window.aspect}')
    event.add('dtstart', moment.exact)
    event.add('dtend', moment.exact + timedelta(minutes=30))
    cal.add_component(event)

with open('aspects.ics', 'wb') as f:
    f.write(cal.to_ical())
```

---

## 🤝 Contribuer

Pour améliorer ce module :

1. Tests : Ajouter des cas de rétrogradation complexes
2. Performance : Optimiser la grille adaptative
3. Features : Aspects mineurs (semi-square, quintile, etc.)
4. Documentation : Plus d'exemples pratiques

---

**Version** : 0.2.0+
**Auteur** : Ketu Contributors
**Licence** : MIT
