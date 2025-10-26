# Concepts astrologiques

## Système de coordonnées

### Longitude écliptique

La **longitude écliptique** est la position d'un corps céleste mesurée le long de l'écliptique (plan orbital de la Terre autour du Soleil), exprimée en degrés de 0° à 360°.

- 0° = Point vernal (0° Bélier)
- 90° = Solstice d'été (0° Cancer)
- 180° = Équinoxe d'automne (0° Balance)
- 270° = Solstice d'hiver (0° Capricorne)

### Latitude écliptique

La **latitude écliptique** mesure la distance angulaire d'un corps au-dessus (+) ou en-dessous (-) du plan de l'écliptique.

### Distance en UA

L'**Unité Astronomique** (UA) est la distance moyenne Terre-Soleil, environ 149,6 millions de km.

## Temps astronomique

### Temps Universel Coordonné (UTC)

Le **UTC** est le standard de temps de référence, basé sur le temps atomique international.

### Jour Julien

Le **Jour Julien** (JD) est un système de datation continue utilisé en astronomie. Le JD commence à midi UTC le 1er janvier 4713 av. J.-C. du calendrier julien proleptique.

```python
# Conversion dans Ketu
jday = ketu.utc_to_julian(datetime_utc)
```

## Les corps célestes

Ketu calcule les positions de 13 corps célestes :

### Planètes classiques

- **Soleil** ☉
- **Lune** ☽
- **Mercure** ☿
- **Vénus** ♀
- **Mars** ♂
- **Jupiter** ♃
- **Saturne** ♄

### Planètes modernes

- **Uranus** ♅
- **Neptune** ♆
- **Pluton** ♇

### Points fictifs

- **Rahu** ☊ : Nœud Nord moyen
- **North Node** : Nœud Nord vrai
- **Lilith** ⚸ : Lune Noire (Apogée moyen)

## Les aspects

### Théorie des harmoniques

Les aspects sont basés sur la division du **demi-cercle** (180°) par des nombres entiers, créant des **harmoniques**. Puisqu'un aspect ne dépasse jamais 180° (au-delà on mesure de l'autre côté), on travaille sur une division du demi-cercle par 6.

#### Harmonique 1 (180°/1 = 180°)

- Conjonction (0°) : même point
- Opposition (180°) : point opposé

#### Harmonique 2 (180°/2 = 90°)

- Carré (90°) : quart de cercle

#### Harmonique 3 (180°/3 = 60°)

- Sextile (60°) : 1/3 du demi-cercle
- Trigone (120°) : 2/3 du demi-cercle

#### Harmonique 6 (180°/6 = 30°)

- Semi-sextile (30°) : 1/6 du demi-cercle
- Quinconce (150°) : 5/6 du demi-cercle

### Tableau récapitulatif

Harmonique | Division | Aspects
-----------|----------|------------------
1          | 180°/1   | Conjonction (0°), Opposition (180°)
2          | 180°/2   | Carré (90°)
3          | 180°/3   | Sextile (60°), Trigone (120°)
6          | 180°/6   | Semi-sextile (30°), Quinconce (150°)

## Orbes

### Principe des orbes

Dans la tradition arabe, chaque **planète possède une orbe** (zone d'influence) qui lui est propre. L'orbe d'un aspect entre deux planètes est calculée comme la **demi-somme des orbes des deux planètes**, multipliée par le **coefficient de l'harmonique**.

```python
# Calcul de l'orbe dans Ketu
orbe = (orbe_planete1 + orbe_planete2) / 2 * coefficient_harmonique
```

### Coefficients des harmoniques

Aspect       | Angle | Harmonique | Coefficient
-------------|-------|------------|------------
Conjonction  | 0°    | 1          | 1
Opposition   | 180°  | 1          | 1
Carré        | 90°   | 2          | 1/2
Sextile      | 60°   | 3          | 1/3
Trigone      | 120°  | 3          | 2/3
Semi-sextile | 30°   | 6          | 1/6
Quinconce    | 150°  | 6          | 5/6

### Exemples de calcul

#### Aspect Soleil-Lune (Conjonction)

- Orbe Soleil : 12°
- Orbe Lune : 12°
- Coefficient : 1 (conjonction)
- Orbe finale : (12 + 12) / 2 × 1 = **12°**

#### Aspect Mercure-Mars (Carré)

- Orbe Mercure : 8°
- Orbe Mars : 10°
- Coefficient : 1/2 (carré)
- Orbe finale : (8 + 10) / 2 × 0.5 = **4.5°**

#### Aspect Vénus-Jupiter (Sextile)

- Orbe Vénus : 8°
- Orbe Jupiter : 10°
- Coefficient : 1/3 (sextile)
- Orbe finale : (8 + 10) / 2 × 0.333 = **3°**

### Orbes par défaut (inspirées d'Abu Ma'shar)

Corps                   | Orbe
------------------------|--------
Soleil, Lune            | 12°
Mercure, Vénus          | 8°
Mars, Jupiter, Saturne  | 10°
Uranus, Neptune         | 6°
Pluton                  | 4°
Rahu, Lilith            | 0°

**Note** : Les orbes peuvent être personnalisées selon les besoins. Voir l'[exemple 05](../examples/05_custom_orbs.py).

## Types d'aspects

Ketu calcule 7 aspects majeurs basés sur les harmoniques 1, 2, 3 et 6 :

Aspect       | Angle | Symbole
-------------|-------|--------
Conjonction  | 0°    | ☌
Semi-sextile | 30°   | ⚺
Sextile      | 60°   | ⚹
Carré        | 90°   | □
Trigone      | 120°  | △
Quinconce    | 150°  | ⚻
Opposition   | 180°  | ☍

## Mouvements planétaires

### Rétrogradation

La **rétrogradation** est le mouvement apparent d'une planète qui semble reculer dans le zodiaque. C'est une illusion optique due aux différences de vitesse orbitale entre la Terre et la planète observée.

```python
# Vérifier la rétrogradation
if ketu.is_retrograde(jday, planet_id):
    print("Planète rétrograde")
```

### Vitesses moyennes

Planète | Vitesse moyenne | Cycle complet
--------|-----------------|-------------------
Lune    | 13.18°/jour     | 27.3 jours
Mercure | 1.38°/jour      | 88 jours
Vénus   | 1.20°/jour      | 225 jours
Soleil  | 0.99°/jour      | 365.25 jours
Mars    | 0.52°/jour      | 687 jours
Jupiter | 0.08°/jour      | 11.9 ans
Saturne | 0.03°/jour      | 29.5 ans
Uranus  | 0.01°/jour      | 84 ans
Neptune | 0.01°/jour      | 165 ans
Pluton  | 0.00°/jour      | 248 ans

## Signes du zodiaque

Ketu reconnaît les 12 signes du zodiaque tropical :

### Liste des signes

N° | Signe       | Symbole | Degré début | Degré fin
---|-------------|---------|-------------|----------
1  | Bélier      | ♈      | 0°          | 30°
2  | Taureau     | ♉      | 30°         | 60°
3  | Gémeaux     | ♊      | 60°         | 90°
4  | Cancer      | ♋      | 90°         | 120°
5  | Lion        | ♌      | 120°        | 150°
6  | Vierge      | ♍      | 150°        | 180°
7  | Balance     | ♎      | 180°        | 210°
8  | Scorpion    | ♏      | 210°        | 240°
9  | Sagittaire  | ♐      | 240°        | 270°
10 | Capricorne  | ♑      | 270°        | 300°
11 | Verseau     | ♒      | 300°        | 330°
12 | Poissons    | ♓      | 330°        | 360°

```python
# Obtenir le signe d'une planète
sign_data = ketu.body_sign(longitude)
sign_index = sign_data[0]  # 0-11
degrees = sign_data[1]      # 0-29
minutes = sign_data[2]      # 0-59
seconds = sign_data[3]      # 0-59

sign_name = ketu.signs[sign_index]
```

## Configurations planétaires

### Grand Trigone

Trois planètes formant des trigones entre elles (triangle équilatéral de 120°).

### T-Carré

Deux planètes en opposition (180°), toutes deux en carré (90°) à une troisième planète (apex).

### Yod (Doigt de Dieu)

Deux planètes en sextile (60°), toutes deux en quinconce (150°) à une troisième planète (apex).

### Grand Carré

Quatre planètes formant quatre carrés (90°) et deux oppositions (180°), créant un carré dans le thème.

## Cycles et retours

### Retours planétaires

Un **retour planétaire** se produit quand une planète revient à sa position natale (même longitude écliptique).

**Principaux retours :**

- **Retour solaire** : Anniversaire astrologique (365.25 jours)
- **Retour lunaire** : Environ tous les 27.3 jours
- **Retour de Jupiter** : Environ tous les 12 ans
- **Retour de Saturne** : Environ vers 29-30 ans et 58-60 ans

```python
# Calculer un retour
natal_position = ketu.long(natal_jday, planet_id)
current_position = ketu.long(current_jday, planet_id)

# Le retour se produit quand la différence < orbe
if abs(current_position - natal_position) < 1.0:
    print("Retour planétaire !")
```

## Éphémérides Swiss

Ketu utilise **pyswisseph**, interface Python des Swiss Ephemeris, pour des calculs de haute précision :

- Précision : ±0.001" d'arc
- Période couverte : 13000 av. J.-C. à 17000 ap. J.-C.
- Données : JPL DE431/DE441
- Modèle : Éphémérides planétaires du Jet Propulsion Laboratory (NASA)

## Ressources

### Sites web

- [Swiss Ephemeris](https://www.astro.com/swisseph/) - Documentation des éphémérides
- [Astrodienst](https://www.astro.com/) - Calculs astrologiques en ligne
- [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/) - Éphémérides astronomiques

### Documentation technique

- [pyswisseph Documentation](https://astrorigin.com/pyswisseph/) - Interface Python
- [JPL Ephemerides](https://ssd.jpl.nasa.gov/planets/eph_export.html) - Données sources

## Prochaines étapes

- Explorez les [Exemples](examples.md) pour voir ces concepts en action
- Consultez l'[API Reference](api.md) pour l'implémentation technique
- Lisez le [Guide de démarrage rapide](quickstart.md) pour commencer à coder
