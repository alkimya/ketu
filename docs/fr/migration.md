# Guide de Migration

Ce guide vous aide à migrer de Ketu v0.2.x (basé sur pyswisseph) vers v0.3.0 (NumPy pur).

## Ce qui a Changé

### Dépendances

**Avant (v0.2.x) :**
```bash
pip install ketu  # Installait pyswisseph + numpy
```

**Après (v0.3.0) :**
```bash
pip install ketu  # Seulement numpy requis
pip install ketu[chart]  # Avec visualisation
pip install ketu[all]  # Avec toutes les fonctionnalités optionnelles
```

### Dépendance Retirée

- **pyswisseph** : Complètement retiré - plus de dépendances binaires
- **Problèmes de plateforme** : Corrigés - pur Python + NumPy fonctionne partout

### Nouvelles Dépendances Optionnelles

- **matplotlib** : Pour visualisation de cartes (`ketu[chart]`)
- **icalendar** : Pour export calendrier (`ketu[icalendar]`)

## Compatibilité API

### API de Haut Niveau (Inchangée)

L'API principale reste entièrement compatible :

```python
# Ce code fonctionne identiquement en v0.2.x et v0.3.0
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

dtime = datetime(2020, 12, 21, 19, 20, tzinfo=ZoneInfo("Europe/Paris"))
jday = ketu.utc_to_julian(dtime)

# Toutes ces fonctions fonctionnent pareil
ketu.print_positions(jday)
ketu.print_aspects(jday)
positions = ketu.positions(jday)
aspects = ketu.calculate_aspects(jday)
```

### Nouvelles Fonctions

v0.3.0 ajoute de nouvelles fonctionnalités :

```python
# Fenêtres d'aspects
windows = ketu.find_aspect_window(jd_start, jd_end, body1=0, body2=1, aspect=0)

# Transits
natal_pos = ketu.get_natal_positions(natal_jd)
transits = ketu.compare_dates_transits(natal_pos, transit_jd)

# Visualisation de cartes (nécessite matplotlib)
ketu.draw_zodiacal_chart(jday, output_file="chart.svg")

# Export iCalendar (nécessite icalendar)
ketu.export_lunations_to_ical(jd_start, jd_end, "lunations.ics")
```

## Différences de Précision

### Swiss Ephemeris (v0.2.x)

- Précision : ±0.001° (précision seconde d'arc)
- Basé sur éphémérides JPL
- Théorie de perturbation complète

### NumPy Pur (v0.3.0)

- Précision : ±0,1° pour planètes intérieures, ±0,5° pour extérieures
- Basé sur VSOP87/perturbations simplifiées
- Largement suffisant pour usages astrologiques

### Quand se Préoccuper

Vous n'avez **probablement pas besoin** de la précision Swiss Ephemeris si :
- Vous faites de l'astrologie (orbes typiquement 1-12°)
- Vous travaillez avec aspects (tolérance d'orbe >> 0,5°)
- Vous avez besoin d'aspects exacts à la minute (v0.3.0 gère cela)

Vous **pourriez préférer** Swiss Ephemeris si :
- Vous avez besoin de précision seconde d'arc pour astronomie scientifique
- Vous calculez positions d'astéroïdes (pas encore supporté en v0.3.0)
- Vous avez besoin de positions pour dates hors 1800-2200 CE

## Comparaison de Performance

### Séries Temporelles (365 jours)

- v0.2.x : ~3,2 secondes
- v0.3.0 : ~15 millisecondes
- **Accélération : 208x**

### Calculs d'Aspects

- v0.2.x : ~120 millisecondes
- v0.3.0 : ~8 millisecondes
- **Accélération : 14,55x**

## Étapes de Migration

### Étape 1 : Mettre à Jour le Package

```bash
pip install --upgrade ketu
```

### Étape 2 : Retirer pyswisseph (Optionnel)

```bash
pip uninstall pyswisseph
```

### Étape 3 : Tester Votre Code

Exécutez votre code existant - il devrait fonctionner sans changements :

```python
# Votre code existant
import ketu

jday = ketu.utc_to_julian(datetime.now())
ketu.print_positions(jday)
```

### Étape 4 : Ajouter Fonctionnalités Optionnelles

Si vous voulez les nouvelles fonctionnalités :

```bash
# Pour visualisation de cartes
pip install ketu[chart]

# Pour export iCalendar
pip install ketu[icalendar]

# Pour tout
pip install ketu[all]
```

## Changements Incompatibles

### Aucun pour l'API Publique

L'API publique (`ketu.*`) n'a **aucun changement incompatible**.

### Changements Internes

Si vous importiez depuis des modules internes :

**Avant :**
```python
# Ne faites pas cela - API interne
from ketu.ketu import body_properties
```

**Après :**
```python
# Utilisez l'API publique à la place
from ketu import body_properties
```

## Problèmes Courants

### Erreurs d'Import

**Problème :**
```python
ImportError: No module named 'swisseph'
```

**Solution :**
C'est attendu - pyswisseph n'est plus utilisé. Votre code devrait toujours fonctionner.

### Préoccupations de Précision

**Problème :** "Les positions sont légèrement différentes de v0.2.x"

**Solution :** C'est attendu. Les différences sont typiquement < 0,5° et négligeables pour l'astrologie.

### Fonctionnalités Manquantes

**Problème :** "Impossible de trouver la fonction X"

**Solution :** Vérifiez si c'est une nouvelle fonctionnalité nécessitant des dépendances optionnelles :

```bash
pip install ketu[all]
```

## Obtenir de l'Aide

Si vous rencontrez des problèmes :

1. Consultez la [documentation](https://ketu.readthedocs.io)
2. Examinez les [exemples](examples.md)
3. Ouvrez un [issue](https://github.com/alkimya/ketu/issues)

## Retour Arrière

Si vous devez revenir à v0.2.x :

```bash
pip install ketu==0.2.1
pip install pyswisseph
```

Note : v0.2.x ne recevra plus de mises à jour.
