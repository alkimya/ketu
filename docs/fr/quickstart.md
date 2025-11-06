# Guide de démarrage rapide

## Premier calcul

### Mode interactif (CLI)

Le plus simple pour commencer :

```bash
ketu
```

Suivez les invites :

1. Entrez une date (format ISO) : `2020-12-21`
2. Entrez une heure : `19:20`
3. Entrez un fuseau horaire : `Europe/Paris`

### Mode programmation

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Définir le moment
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Convertir en jour julien
jday = ketu.utc_to_julian(dt)

# Afficher les positions
ketu.print_positions(jday)
```

### Calculs de base

#### Positions planétaires

```python
import ketu
from datetime import datetime

# Date actuelle
dt = datetime.now()
jday = ketu.utc_to_julian(dt)

# Position du Soleil (id=0)
sun_longitude = ketu.long(jday, 0)
sun_latitude = ketu.lat(jday, 0)
sun_distance = ketu.dist_au(jday, 0)

print(f"Soleil: {sun_longitude:.2f}° longitude")
print(f"        {sun_latitude:.2f}° latitude")
print(f"        {sun_distance:.2f} AU")
```

#### Déterminer le signe zodiacal

```python
# Position de la Lune
moon_long = ketu.long(jday, 1)  # 1 = Lune

# Calculer le signe
sign_data = ketu.body_sign(moon_long)
sign_index = sign_data[0]
degrees = sign_data[1]
minutes = sign_data[2]

print(f"Lune en {ketu.signs[sign_index]} {degrees}°{minutes}'")
```

#### Vérifier la rétrogradation

```python
# Mercure (id=2)
if ketu.is_retrograde(jday, 2):
    print("Mercure est rétrograde")
else:
    print("Mercure est direct")
```

### Calcul des aspects

#### Aspects entre deux planètes

```python
# Aspect Soleil-Lune
aspect = ketu.get_aspect(jday, 0, 1)  # 0=Soleil, 1=Lune

if aspect:
    body1, body2, asp_type, orb = aspect
    aspect_name = ketu.aspects["name"][asp_type].decode()
    print(f"Soleil-Lune: {aspect_name} (orbe: {orb:.2f}°)")
else:
    print("Pas d'aspect Soleil-Lune")
```

#### Tous les aspects du moment

```python
# Calculer tous les aspects
aspects_array = ketu.calculate_aspects(jday)

# Afficher
for aspect in aspects_array:
    b1, b2, asp_idx, orb = aspect
    name1 = ketu.body_name(b1)
    name2 = ketu.body_name(b2)
    asp_name = ketu.aspects["name"][asp_idx].decode()
    
    print(f"{name1} - {name2}: {asp_name} ({orb:.2f}°)")
```

### Exemple complet : Thème natal

```python
import ketu
from datetime import datetime
from zoneinfo import ZoneInfo

def theme_natal(year, month, day, hour, minute, timezone_str):
    """Calculer un thème natal simple"""
    
    # Créer la date
    tz = ZoneInfo(timezone_str)
    dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    jday = ketu.utc_to_julian(dt)
    
    print(f"\n{'='*50}")
    print(f"THÈME NATAL - {dt.strftime('%d/%m/%Y %H:%M')} {timezone_str}")
    print(f"{'='*50}\n")
    
    # Positions des planètes
    print("POSITIONS PLANÉTAIRES:")
    print("-" * 30)
    
    for i, body in enumerate(ketu.bodies["name"]):
        if i > 9:  # Skip Rahu/Lilith pour simplifier
            break
            
        name = body.decode()
        longitude = ketu.long(jday, i)
        sign_data = ketu.body_sign(longitude)
        sign = ketu.signs[sign_data[0]]
        deg, min = sign_data[1], sign_data[2]
        
        # Vérifier rétrogradation
        retro = " ℞" if ketu.is_retrograde(jday, i) else ""
        
        print(f"{name:8} : {sign:12} {deg:2}°{min:02}'{retro}")
    
    # Aspects majeurs
    print(f"\nASPECTS MAJEURS:")
    print("-" * 30)
    
    aspects = ketu.calculate_aspects(jday)
    for aspect in aspects:
        b1, b2, asp_idx, orb = aspect
        # Afficher seulement les aspects avec orbe < 5°
        if abs(orb) < 5:
            name1 = ketu.body_name(b1)
            name2 = ketu.body_name(b2) 
            asp_name = ketu.aspects["name"][asp_idx].decode()
            print(f"{name1:8} {asp_name:12} {name2:8} ({orb:+.2f}°)")

# Utilisation
theme_natal(1990, 5, 15, 14, 30, "Europe/Paris")
```

### Trucs et astuces

#### Utiliser le cache

Les calculs de positions utilisent `@lru_cache` pour optimiser les performances :

```python

# Ces appels utilisent le cache
long1 = ketu.long(jday, 0)
lat1 = ketu.lat(jday, 0)  # Utilise le cache de body_properties

# Pour vider le cache
ketu.body_properties.cache_clear()
```

#### Travailler avec numpy

```python
import numpy as np

# Calculer les positions pour plusieurs jours
days = np.arange(jday, jday + 30, 1)  # 30 jours
sun_positions = [ketu.long(d, 0) for d in days]

# Trouver les changements de signe
signs = [ketu.body_sign(pos)[0] for pos in sun_positions]
changes = np.where(np.diff(signs))[0]
```

#### Personnaliser les orbes

```python
# Modifier temporairement les orbes
original_orbs = ketu.bodies["orb"].copy()

# Orbes plus serrés
ketu.bodies["orb"] = ketu.bodies["orb"] * 0.5

# Calculer avec les nouveaux orbes
aspects = ketu.calculate_aspects(jday)

# Pour calculer les orbes en fonction des aspects seulement
ketu.bodies["orb"] = 1
original_coefs = ketu.aspects["coef"].copy()

# Mettre une orbe de 6 à l'aspect carré par exemple, de même pour tous les aspects
ketu.aspect["coef"][np.where(aspect["name"] == "Square")] = 6

# Restaurer
ketu.bodies["orb"] = original_orbs
ketu.aspects["coef"] = original_coefs
```

### Prochaines étapes

- Explorez les [Exemples avancés](examples.md) pour des cas d'usage complexes
- Consultez la [Référence API](api.md) pour tous les détails
- Découvrez les [Concepts astrologiques](concepts.md) utilisés dans Ketu
