#!/usr/bin/env python3
"""
Exemple 3 : Thème natal complet

Crée un thème natal avec :
- Positions de toutes les planètes
- Signes zodiacaux
- Rétrogradations
- Aspects majeurs
"""

import ketu
from datetime import datetime
from zoneinfo import ZoneInfo


def theme_natal(year, month, day, hour, minute, timezone_str):
    """Calculer et afficher un thème natal complet"""

    # Créer la date
    tz = ZoneInfo(timezone_str)
    dt = datetime(year, month, day, hour, minute, tzinfo=tz)
    jday = ketu.utc_to_julian(dt)

    print("\n" + "=" * 60)
    print(f"THÈME NATAL - {dt.strftime('%d/%m/%Y %H:%M')} {timezone_str}")
    print("=" * 60 + "\n")

    # Positions des planètes
    print("POSITIONS PLANÉTAIRES:")
    print("-" * 60)

    for i, body in enumerate(ketu.bodies["name"]):
        if i > 9:  # Skip Rahu/Lilith pour simplifier
            break

        name = body.decode()
        longitude = ketu.long(jday, i)
        sign_data = ketu.body_sign(longitude)
        sign = ketu.signs[sign_data[0]]
        deg, min, sec = sign_data[1], sign_data[2], sign_data[3]

        # Vérifier rétrogradation
        retro = " ℞" if ketu.is_retrograde(jday, i) else ""

        print(f"{name:10} : {sign:12} {deg:2}°{min:02}'{sec:02}\"{retro}")

    # Aspects majeurs
    print(f"\nASPECTS MAJEURS:")
    print("-" * 60)

    aspects = ketu.calculate_aspects(jday)

    # Grouper par type d'aspect
    aspect_groups = {}
    for aspect in aspects:
        b1, b2, asp_idx, orb = aspect
        # Afficher seulement les aspects avec orbe < 5°
        if abs(orb) < 5:
            asp_name = ketu.aspects["name"][asp_idx].decode()
            if asp_name not in aspect_groups:
                aspect_groups[asp_name] = []
            aspect_groups[asp_name].append((b1, b2, orb))

    # Afficher par type
    for asp_name in sorted(aspect_groups.keys()):
        print(f"\n{asp_name}:")
        for b1, b2, orb in aspect_groups[asp_name]:
            name1 = ketu.body_name(b1)
            name2 = ketu.body_name(b2)
            orb_marker = "●" if abs(orb) < 1 else "○"
            print(f"  {orb_marker} {name1:10} - {name2:10} ({orb:+5.2f}°)")

    print("\n" + "=" * 60)


def main():
    # Exemples de thèmes natals

    print("\n" + "#" * 60)
    print("# EXEMPLES DE THÈMES NATAUX")
    print("#" * 60)

    # Exemple 1 : Solstice d'hiver 2020
    print("\n### Exemple 1 : Solstice d'hiver 2020")
    theme_natal(2020, 12, 21, 19, 20, "Europe/Paris")

    # Exemple 2 : Date arbitraire
    print("\n### Exemple 2 : Date personnalisée")
    theme_natal(1990, 5, 15, 14, 30, "Europe/Paris")


if __name__ == "__main__":
    main()
