# Ketu Documentation

**Ketu** est une bibliothèque Python pour calculer les positions planétaires et les aspects astrologiques, basée sur `pyswisseph` et `numpy`.

## Vue d'ensemble

Ketu permet de :

- 🌟 Calculer les positions précises des corps célestes (Soleil, Lune, planètes, Nœuds, Lilith)
- ⚡ Déterminer les aspects entre les planètes
- 📅 Convertir entre différents systèmes temporels (UTC, Julian)
- 🔮 Identifier les rétrogradations et les signes zodiacaux
- 📊 Générer des séries temporelles d'aspects (à venir)

## Navigation

```{toctree}
:maxdepth: 2
:caption: Guide utilisateur
installation
quickstart
concepts
examples
API <api>
changelog
contributing
```

## Fonctionnalités principales

### Corps célestes supportés

Corps               |   Symbole |   Orbe    |   Vitesse moyenne
--------------------|-----------|-----------|-------------------
Soleil              |   ☉       |  12°      |  0.986°/jour
Lune                |   ☽       |  12°      |  13.176°/jour
Mercure             |   ☿       |  8°       |  1.383°/jour
Vénus               |   ♀       |  8°       |  1.2°/jour
Mars                |   ♂       |  10°      |  0.524°/jour
Jupiter             |   ♃       |  10°      |  0.083°/jour
Saturne             |   ♄       |  10°      |  0.034°/jour
Uranus              |   ♅       |  6°       |  0.012°/jour
Neptune             |   ♆       |  6°       |  0.007°/jour
Pluton              |   ♇       |  4°       |  0.004°/jour
Rahu (Nœud moyen)   |   ☊       |  0º       |  -0.013°/jour
Lilith (Lune Noire) |   ⚸       |  0º       |  -0.113°/jour

### Aspects majeurs

Aspect      |   Angle   |   Symbole    |   Harmonique
------------|-----------|--------------|--------------
Conjonction |   0°      |   ☌          |   1
Semi-sextile|   30°     |   ⚺          |   1/6
Sextile     |   60°     |   ⚹          |   1/3
Carré       |   90°     |   □          |    1/2
Trigone     |   120°    |   △          |    2/3
Quinconce   |   150°    |   ⚻          |   5/6
Opposition  |   180°    |   ☍          |   1

## Exemple rapide

```python
from datetime import datetime
from zoneinfo import ZoneInfo
import ketu

# Créer une date
paris = ZoneInfo("Europe/Paris")
dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)

# Calculer et afficher
jday = ketu.utc_to_julian(dt)
ketu.print_positions(jday)
ketu.print_aspects(jday)
```

## Indices et tables

{ref}`genindex`

{ref}`search`

## Licence

MIT License - Copyright (c) 2024 Loc Cosnier

## Contact

- Auteur : Loc Cosnier
- Email : <loc.cosnier@pm.me>
- GitHub : alkimya/ketu
- PyPI : pypi.org/project/ketu
