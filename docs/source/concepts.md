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

### Planètes personnelles

- **Soleil** ☉ : Identité, ego, vitalité
- **Lune** ☽ : Émotions, inconscient, besoins
- **Mercure** ☿ : Communication, intellect
- **Vénus** ♀ : Amour, valeurs, harmonie
- **Mars** ♂ : Action, désir, énergie

### Planètes sociales

- **Jupiter** ♃ : Expansion, sagesse, opportunités
- **Saturne** ♄ : Structure, limites, responsabilité

### Planètes transpersonnelles

- **Uranus** ♅ : Innovation, rébellion, changement
- **Neptune** ♆ : Intuition, spiritualité, illusion
- **Pluton** ♇ : Transformation, pouvoir, régénération

### Points fictifs

- **Rahu** ☊ : Nœud Nord moyen, évolution karmique
- **Lilith** ⚸ : Lune Noire, part d'ombre

## Les aspects

### Théorie des harmoniques

Les aspects sont basés sur la division du cercle (360°) par des nombres entiers, créant des **harmoniques** :

Harmonique  |   Division    |   Aspects
------------|---------------|-----------------
1           |   360°/1      |   Conjonction (0°)
2           |   360°/2      |   Opposition (180°)
3           |   360°/3      |   Trigone (120°)
4           |   360°/4      |   Carré (90°)
6           |   360°/6      |   Sextile (60°)
12          |   360°/12     |   Semi-sextile (30°)

## Orbes

L'**orbe** est la tolérance angulaire acceptée pour qu'un aspect soit considéré comme actif.

```python
# Calcul de l'orbe dans Ketu
orbe = (orbe_planete1 + orbe_planete2) / 2 * coefficient_aspect
```

### Orbes par défaut (Abu Ma'shar)

Corps                   |   Orbe
------------------------|--------
Soleil, Lune            |   12°
Mercure, Vénus          |   8°
Mars, Jupiter, Saturne  |   10°
Uranus, Neptune         |   6°
Pluton                  |   4°

## Types d'aspects

### Aspects majeurs

- **Conjonction** (0°) : Fusion, intensification
- **Opposition** (180°) : Polarité, confrontation
- **Trigone** (120°) : Harmonie, fluidité
- **Carré** (90°) : Tension, défi
- **Sextile** (60°) : Opportunité, coopération

### Aspects mineurs

- **Semi-sextile** (30°) : Ajustement subtil
- **Quinconce** (150°) : Ajustement nécessaire

## Mouvements planétaires

### Rétrogradation

La **rétrogradation** est le mouvement apparent d'une planète qui semble reculer dans le zodiaque.

C'est une illusion optique due aux différences de vitesse orbitale.

```python
# Vérifier la rétrogradation
if ketu.is_retrograde(jday, planet_id):
    print("Planète rétrograde")
```

### Vitesses moyennes

Planète |   Vitesse moyenne |   Cycle complet
--------|-------------------|-------------------
Lune    |   13.18°/jour     |   27.3 jours
Mercure |   1.38°/jour      |   88 jours
Vénus   |   1.20°/jour      |   225 jours
Soleil  |   0.99°/jour      |   365.25 jours
Mars    |   0.52°/jour      |   687 jours
Jupiter |   0.08°/jour      |   11.9 ans
Saturne |   0.03°/jour      |   29.5 ans

## Signes du zodiaque

### Classification par élément

Élément |   Signes                      |   Qualités
--------|-------------------------------|---------------------------
Feu 🔥  |   Bélier, Lion, Sagittaire    |   Action, enthousiasme
Terre 🌍|   Taureau, Vierge, Capricorne |   Stabilité, pragmatisme
Air 💨  |   Gémeaux, Balance, Verseau   |   Communication, intellect
Eau 💧  |   Cancer, Scorpion, Poissons  |   Émotion, intuition

### Classification par mode

Mode    |   Signes                                  |   Qualités
--------|-------------------------------------------|----------------------------
Cardinal|   Bélier, Cancer, Balance, Capricorne     |   Initiative, leadership
Fixe    |   Taureau, Lion, Scorpion, Verseau        |   Stabilité, persistance
Mutable |   Gémeaux, Vierge, Sagittaire, Poissons   |   Adaptabilité, flexibilité

## Configurations planétaires

### Grand Trigone

Trois planètes formant des trigones entre elles (triangle équilatéral). Configuration harmonieuse mais pouvant créer de la complaisance.

### T-Carré

Deux planètes en opposition, toutes deux en carré à une troisième (planète apex). Configuration dynamique créant tension et motivation.

### Yod (Doigt de Dieu)

Deux planètes en sextile, toutes deux en quinconce à une troisième (planète apex). Configuration karmique demandant des ajustements.

### Grand Carré

Quatre planètes formant quatre carrés et deux oppositions. Configuration rare créant une forte tension mais aussi un grand potentiel.

## Cycles et retours

### Retours planétaires

- **Retour solaire** : Anniversaire astrologique (Soleil revient à sa position natale)
- **Retour lunaire** : Tous les 27.3 jours
- **Retour de Saturne** : Vers 29-30 ans et 58-60 ans
- **Retour de Jupiter** : Tous les 12 ans

### Progressions

Les progressions symboliques suivent la formule "un jour = un an" pour étudier l'évolution psychologique.

## Éphémérides Swiss

Ketu utilise **pyswisseph**, interface Python des Swiss Ephemeris, pour des calculs de haute précision :

- Précision : ±0.001" d'arc
- Période couverte : 13000 av. J.-C. à 17000 ap. J.-C.
- Données : JPL DE431/DE441

## Ressources

### Livres recommandés

- *Tetrabiblos* - Claude Ptolémée
- *The Book of Instruction* - Abu Ma'shar
- *The Book of Nativities* - Al-Biruni
- *Christian Astrology* - William Lilly

### Sites web

- [Swiss Ephemeris](https://www.astro.com/swisseph/)
- [Astrodienst](https://www.astro.com/)
- [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/)

## Prochaines étapes

- Explorez les [Exemples](examples.md) pour voir ces concepts en action
- Consultez l'[API Reference](api.md) pour l'implémentation technique
