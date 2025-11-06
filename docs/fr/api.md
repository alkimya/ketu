# Référence API

## Vue d'ensemble

```python
import ketu
```

L'API de Ketu est organisée en plusieurs catégories :

- **Données** : Arrays structurés des corps et aspects
- **Conversions** : Temps et coordonnées
- **Calculs** : Positions et aspects
- **Utilitaires** : Affichage et helpers

## Données

### `bodies`

```python
ketu.bodies: numpy.ndarray
```

Array structuré contenant les informations des corps célestes.

**Structure :**

- `name` (S12) : Nom du corps
- `id` (i4) : Identifiant Swiss Ephemeris
- `orb` (f4) : Orbe en degrés
- `speed` (f4) : Vitesse moyenne en °/jour

**Exemple :**

```python
>>> ketu.bodies["name"][:3]
array([b'Sun', b'Moon', b'Mercury'], dtype='|S12')

>>> ketu.bodies["orb"][:3]
array([12., 12., 8.], dtype=float32)
```

### `aspects`

```python
ketu.aspects: numpy.ndarray
```

Array structuré des aspects astrologiques.

**Structure :**

- `name` (S12) : Nom de l'aspect
- `value` (f4) : Angle en degrés
- `coef` (f4) : Coefficient pour le calcul d'orbe

**Exemple :**

```python
>>> ketu.aspects["name"]
array([b'Conjunction', b'Semi-sextile', b'Sextile', ...])

>>> ketu.aspects["value"]
array([0., 30., 60., 90., 120., 150., 180.])
```

### `signs`

```python
ketu.signs: List[str]
```

Liste des signes du zodiaque.

```python
>>> ketu.signs[0]
'Aries'
>>> ketu.signs[11]
'Pisces'
```

## Conversions temporelles

### `local_to_utc()`

```python
def local_to_utc(dtime: datetime, zoneinfo: ZoneInfo = None) -> datetime
```

Convertit une datetime locale en UTC.

**Paramètres :**

- `dtime` : datetime à convertir
- `zoneinfo` : timezone (optionnel si dtime a déjà tzinfo)

**Retour :** datetime en UTC

**Exemple :**

```python
paris = ZoneInfo("Europe/Paris")
local = datetime(2024, 1, 1, 12, 0, tzinfo=paris)
utc = ketu.local_to_utc(local)
```

### `utc_to_julian()`

```python
def utc_to_julian(dtime: datetime) -> float
```

Convertit une datetime UTC en Jour Julien.

**Paramètres :**

- `dtime` : datetime (UTC ou avec tzinfo)

**Retour :** Jour Julien (float)

**Exemple :**

```python
dt = datetime(2024, 1, 1, 12, 0)
jday = ketu.utc_to_julian(dt)
# jday = 2460310.0
```

## Conversions angulaires

### `decimal_degrees_to_dms()`

```python
def decimal_degrees_to_dms(deg: float) -> numpy.ndarray
```

Convertit des degrés décimaux en degrés, minutes, secondes.

**Paramètres :**

- `deg` : angle en degrés décimaux

**Retour :** array [degrés, minutes, secondes]

**Exemple :**

```python

>>> ketu.decimal_degrees_to_dms(123.456)
array([123, 27, 21], dtype=int32)
```

### `distance()`

```python
def distance(pos1: float, pos2: float) -> float
```

Calcule la distance angulaire entre deux positions.

**Paramètres :**

- `pos1`, `pos2` : positions en degrés

**Retour :** distance en degrés (0-180)

**Exemple :**

```python
>>> ketu.distance(10, 350)
20.0  # Plus court chemin
```

### `get_orb()`

```python
def get_orb(body1: int, body2: int, asp: int) -> float
```

Calcule l'orbe pour un aspect entre deux corps.

**Paramètres :**

- `body1`, `body2` : indices des corps
- `asp` : indice de l'aspect

**Retour :** orbe maximum en degrés

## Fonctions de position

### `body_properties()`

```python
@lru_cache
def body_properties(jday: float, body: int) -> numpy.ndarray
```

Calcule toutes les propriétés d'un corps (fonction cachée).

**Paramètres :**

- `jday` : Jour Julien
- `body` : ID du corps

**Retour :** array [longitude, latitude, distance, vlong, vlat, vdist]

### `long()`, `lat()`, `dist_au()`

```python
def long(jday: float, body: int) -> float
def lat(jday: float, body: int) -> float
def dist_au(jday: float, body: int) -> float
```

Retournent respectivement la longitude, latitude et distance d'un corps.

**Paramètres :**

- `jday` : Jour Julien
- `body` : ID du corps (0=Soleil, 1=Lune, etc.)

**Retour :** valeur en degrés ou AU

### `vlong()`, `vlat()`, `vdist_au()`

```python
def vlong(jday: float, body: int) -> float
def vlat(jday: float, body: int) -> float
def vdist_au(jday: float, body: int) -> float
```

Vitesses de déplacement (degrés/jour ou AU/jour).

## Fonctions d'analyse

### `is_retrograde()`

```python
def is_retrograde(jday: float, body: int) -> bool
```

Vérifie si un corps est rétrograde.

**Exemple :**

```python
if ketu.is_retrograde(jday, 2):  # Mercure
    print("Mercure rétrograde!")
```

### `is_ascending()`

```python
def is_ascending(jday: float, body: int) -> bool
```

Vérifie si la latitude d'un corps augmente.

### `body_sign()`

```python
def body_sign(b_long: float) -> numpy.ndarray
```

Détermine le signe et la position exacte.

**Paramètres :**

- `b_long` : longitude en degrés

**Retour :** array [signe, degrés, minutes, secondes]

`body_name()` et `body_id()`

```python
def body_name(body: int) -> str
def body_id(b_name: str) -> int
```

Conversion entre ID et nom d'un corps.

## Calculs d'aspects

### `get_aspect()`

```python
def get_aspect(jday: float, body1: int, body2: int) -> Optional[Tuple]
```

Calcule l'aspect entre deux corps.

**Retour :** tuple (body1, body2, aspect_id, orbe) ou None

### `calculate_aspects()`

```python
def calculate_aspects(jday: float, l_bodies=bodies) -> numpy.ndarray
```

Calcule tous les aspects entre les corps.

**Retour :** array structuré des aspects

### `positions()`

```python
def positions(jday: float, l_bodies=bodies) -> numpy.ndarray
```

Calcule toutes les longitudes des corps.

## Fonctions d'affichage

### `print_positions()` et `print_aspects()`

```python
def print_positions(jday: float) -> None
def print_aspects(jday: float) -> None
```

Affichent les positions et aspects formatés.

## Fonction principale

### `main()`

```python
def main() -> None
```

Point d'entrée pour l'interface CLI interactive.

## Notes techniques

- Les calculs utilisent `@lru_cache` pour optimiser les performances
- Les IDs des corps suivent la convention Swiss Ephemeris
- Les angles sont toujours en degrés (0-360)
- La précision temporelle est d'environ 1 seconde

## Voir aussi

- [Concepts](concepts.md) pour la théorie
- [Exemples](examples.md) pour plus de cas d'usage
- [Swiss Ephemeris](https://www.astro.com/swisseph/) pour les détails techniques
