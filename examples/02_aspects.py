#!/usr/bin/env python3
"""
Exemple 2 : Calcul des aspects astrologiques

Montre comment :
- Calculer un aspect entre deux planètes
- Calculer tous les aspects du moment
- Filtrer les aspects par orbe
"""

import ketu
from datetime import datetime
from zoneinfo import ZoneInfo


def main():
    print("=" * 60)
    print("EXEMPLE 2 : ASPECTS ASTROLOGIQUES")
    print("=" * 60)

    # Date et heure
    paris = ZoneInfo("Europe/Paris")
    dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)
    print(f"\nDate : {dt.strftime('%d/%m/%Y %H:%M %Z')}")

    jday = ketu.utc_to_julian(dt)

    # Aspect entre Soleil et Lune
    print("\n--- ASPECT SOLEIL-LUNE ---")
    aspect = ketu.get_aspect(jday, 0, 1)  # 0=Soleil, 1=Lune

    if aspect:
        body1, body2, asp_type, orb = aspect
        aspect_name = ketu.aspects["name"][asp_type].decode()
        print(f"Aspect : {aspect_name}")
        print(f"Orbe   : {orb:.2f}°")
    else:
        print("Pas d'aspect Soleil-Lune")

    # Tous les aspects du moment
    print("\n--- TOUS LES ASPECTS ---")
    aspects_array = ketu.calculate_aspects(jday)

    print(f"Nombre d'aspects trouvés : {len(aspects_array)}")
    print()

    for aspect in aspects_array:
        b1, b2, asp_idx, orb = aspect
        name1 = ketu.body_name(b1)
        name2 = ketu.body_name(b2)
        asp_name = ketu.aspects["name"][asp_idx].decode()

        print(f"{name1:12} - {name2:12} : {asp_name:12} (orbe: {orb:+6.2f}°)")

    # Aspects serrés (orbe < 3°)
    print("\n--- ASPECTS SERRÉS (orbe < 3°) ---")
    tight_aspects = [asp for asp in aspects_array if abs(asp[3]) < 3]

    if tight_aspects:
        for aspect in tight_aspects:
            b1, b2, asp_idx, orb = aspect
            name1 = ketu.body_name(b1)
            name2 = ketu.body_name(b2)
            asp_name = ketu.aspects["name"][asp_idx].decode()

            print(f"{name1:12} - {name2:12} : {asp_name:12} (orbe: {orb:+6.2f}°)")
    else:
        print("Aucun aspect serré trouvé")

    # Aspects exacts (orbe < 1°)
    print("\n--- ASPECTS EXACTS (orbe < 1°) ---")
    exact_aspects = [asp for asp in aspects_array if abs(asp[3]) < 1]

    if exact_aspects:
        for aspect in exact_aspects:
            b1, b2, asp_idx, orb = aspect
            name1 = ketu.body_name(b1)
            name2 = ketu.body_name(b2)
            asp_name = ketu.aspects["name"][asp_idx].decode()

            print(f"⭐ {name1:12} - {name2:12} : {asp_name:12} (orbe: {orb:+6.2f}°)")
    else:
        print("Aucun aspect exact trouvé")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
