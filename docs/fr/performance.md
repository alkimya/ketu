# Guide de Performance

Ketu v0.3.0 utilise la vectorisation NumPy pure pour obtenir des améliorations de performance massives par rapport à la version précédente.

## Benchmarks

### Calculs de Séries Temporelles

Pour calculer les positions planétaires sur 365 jours :

- **208x plus rapide** que l'approche par boucles
- De ~3,2s à ~15ms pour une année complète

### Calculs d'Aspects

Pour détecter tous les aspects entre planètes :

- **14,55x plus rapide** avec la vectorisation
- De ~120ms à ~8ms par date

### Calculs de Positions Individuelles

Pour calculer les positions de planètes individuelles :

- **67x plus rapide** pour les planètes extérieures
- **59x plus rapide** pour les calculs lunaires
- Solveur de Kepler optimisé avec méthode Newton-Raphson

## Fonctions Vectorisées

### Calculs de Positions par Batch

```python
import numpy as np
from ketu import utc_to_julian
from datetime import datetime, timedelta

# Calculer les positions du Soleil pour une année
dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)]
jd_array = np.array([utc_to_julian(d) for d in dates])

# Utiliser le calcul par batch vectorisé
from ketu.ephemeris.planets import calc_planet_position_batch
positions = calc_planet_position_batch(jd_array, planet_id=0)  # Soleil

# Extraire les composantes
longitudes = positions[:, 0]
latitudes = positions[:, 1]
distances = positions[:, 2]
```

### Détection d'Aspects Vectorisée

```python
import ketu

# Calculer tous les aspects pour plusieurs dates efficacement
aspects_batch = ketu.calculate_aspects_batch(jd_array)
```

## Techniques d'Optimisation

### Cache LRU

La bibliothèque utilise `functools.lru_cache` avec des tailles de cache optimales :

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def body_properties(jdate, body):
    # Mis en cache pour les calculs répétés
    # Accélération 6,7x vs sans cache
    ...
```

### Broadcasting NumPy

Tous les calculs de distance et d'angle utilisent le broadcasting NumPy pour des opérations efficaces sur les tableaux.

### Solveur de Kepler Optimisé

Le solveur d'équation de Kepler utilise l'itération Newton-Raphson avec tolérance adaptive :

- Convergence typique en 3-5 itérations
- Epsilon adaptatif basé sur l'excentricité
- Vectorisé pour les calculs par batch

## Bonnes Pratiques

### Utiliser les Fonctions Batch

Pour l'analyse de séries temporelles :

```python
# Bon : Utiliser les fonctions batch
positions = calc_planet_position_batch(jd_array, planet_id)

# À éviter : Appels individuels dans une boucle
positions = [calc_planet_position(jd, planet_id) for jd in jd_array]
```

### Pré-allouer les Tableaux

Pour les calculs à grande échelle :

```python
import numpy as np

# Pré-allouer le tableau de résultats
results = np.zeros((len(dates), 6))

# Remplir avec le calcul par batch
results = calc_planet_position_batch(jd_array, planet_id)
```

### Mettre en Cache les Conversions de Dates Juliennes

```python
# Convertir les dates une fois
jd_array = np.array([utc_to_julian(d) for d in dates])

# Réutiliser pour plusieurs calculs
sun_pos = calc_planet_position_batch(jd_array, 0)
moon_pos = calc_planet_position_batch(jd_array, 1)
```

## Conseils de Performance

1. **Utiliser les fonctions vectorisées** pour les opérations en masse
2. **Mettre en cache les dates juliennes** lors du calcul de plusieurs corps
3. **Pré-allouer les tableaux** pour les grands ensembles de données
4. **Éviter les boucles Python** sur les dates - utiliser des tableaux NumPy
5. **Réutiliser les calculs** - exploiter le cache LRU

## Optimisations Futures

Améliorations de performance prévues :

- [ ] Compilation JIT avec Numba (optionnel)
- [ ] Calcul parallèle pour corps indépendants
- [ ] Optimisations SIMD pour transformations de coordonnées
- [ ] Accélération GPU pour calculs à grande échelle (optionnel)
