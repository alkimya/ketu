# Architecture

Cette page décrit l'architecture interne de Ketu v0.3.0.

## Structure des Modules

```
ketu/
├── __init__.py          # API publique et imports
├── core.py              # Structures de données (corps, aspects, signes)
├── calculations.py      # Fonctions de calcul de haut niveau
├── display.py           # CLI et utilitaires d'affichage
├── aspect_windows.py    # Calculs de timing d'aspects
├── transits.py          # Calculs de transits
├── chart.py             # Visualisation de cartes zodiacales
├── icalendar_export.py  # Utilitaires d'export iCalendar
└── ephemeris/           # Calculs astronomiques bas niveau
    ├── __init__.py      # API du package ephemeris
    ├── time.py          # Conversions de temps et équation du temps
    ├── orbital.py       # Mécanique orbitale et solveur de Kepler
    ├── coordinates.py   # Transformations de coordonnées
    └── planets.py       # Calculs de positions planétaires
```

## Composants Principaux

### Structures de Données (core.py)

Définit les structures de données fondamentales :

- **bodies** : Dictionnaire avec noms, IDs, symboles, orbes, vitesses des planètes
- **aspects** : Dictionnaire avec noms, angles, coefficients, symboles des aspects
- **signs** : Liste des noms de signes zodiacaux

Implémentées comme des tableaux structurés NumPy pour un accès efficace.

### Calculs (calculations.py)

API de haut niveau enveloppant les fonctions ephemeris :

- `positions()` - Obtenir toutes les positions planétaires
- `calculate_aspects()` - Détecter tous les aspects
- `find_aspect_timing()` - Trouver les moments exacts d'aspects
- `is_retrograde()` - Vérifier le mouvement rétrograde

### Affichage (display.py)

Fonctions d'affichage orientées utilisateur :

- `print_positions()` - Table de positions formatée
- `print_aspects()` - Table d'aspects formatée
- `main()` - Point d'entrée CLI interactif

## Package Ephemeris

### Conversions de Temps (ephemeris/time.py)

Gère tous les calculs liés au temps :

- **Conversions UTC ↔ Jour Julien**
- **Équation du temps**
- **Temps sidéral**
- **Corrections Delta T** pour dates historiques

Utilise des formules purement mathématiques - pas de dépendances externes.

### Mécanique Orbitale (ephemeris/orbital.py)

Calculs astronomiques principaux :

- **Solveur de Kepler** - Résout l'équation de Kepler avec Newton-Raphson
- **Éléments orbitaux** - Paramètres orbitaux planétaires
- **Perturbations** - Perturbations planétaires majeures
- **Position depuis éléments** - Convertit éléments orbitaux en position

### Transformations de Coordonnées (ephemeris/coordinates.py)

Conversions de systèmes de coordonnées :

- **Coordonnées Écliptiques ↔ Équatoriales**
- **Positions Héliocentriques ↔ Géocentriques**
- **Coordonnées Rectangulaires ↔ Sphériques**
- **Corrections de nutation**
- **Corrections d'aberration**

### Calculs Planétaires (ephemeris/planets.py)

Fonctions de position planétaire de haut niveau :

- `calc_planet_position()` - Calcul pour une seule date
- `calc_planet_position_batch()` - Calcul par batch vectorisé
- `find_exact_aspect()` - Recherche binaire pour aspects exacts
- `body_properties()` - Obtenir position complète + vitesse

## Fonctionnalités Avancées

### Fenêtres d'Aspects (aspect_windows.py)

Suivi temporel des aspects :

- **AspectMoment** - Instant où l'aspect est exact
- **AspectWindow** - Durée du début à la fin de l'aspect
- `find_aspect_window()` - Trouver toutes les fenêtres dans une plage de dates
- `find_aspects_timeline()` - Timeline complète des aspects

Utilise recherche binaire et descente de gradient pour la précision.

### Transits (transits.py)

Calculs de thème natal et de transits :

- **NatalPosition** - Stocke position planétaire natale
- **TransitAspect** - Décrit aspect transit-natal
- `get_natal_positions()` - Extraire positions natales
- `find_transits_to_position()` - Trouver transits vers un point
- `compare_dates_transits()` - Comparaison complète de transits

## Principes de Conception

### Séparation des Préoccupations

- **ephemeris/**: Calculs astronomiques purs
- **calculations.py**: Interprétations astrologiques
- **display.py**: Interface utilisateur
- **Modules avancés**: Fonctionnalités optionnelles

### Vectorisation en Premier

Toutes les fonctions principales supportent entrées scalaires et tableaux via broadcasting NumPy.

### Pas d'État Global

Toutes les fonctions sont pures - mêmes entrées produisent toujours mêmes sorties.

### Dépendances Optionnelles

Fonctionnalités avancées (cartes, iCalendar) sont des extras optionnels.
