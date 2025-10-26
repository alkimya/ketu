#!/usr/bin/env python3
"""
Exemple 5 : Personnalisation des orbes

Montre comment :
- Modifier temporairement les orbes
- Comparer les résultats avec différents orbes
- Restaurer les orbes d'origine
"""

import ketu
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np


def compare_orb_settings(jday):
    """Comparer les aspects avec différents réglages d'orbes"""

    print("\n" + "=" * 60)
    print("COMPARAISON DES ORBES")
    print("=" * 60)

    # Sauvegarder les orbes originaux
    original_orbs = ketu.bodies["orb"].copy()

    # Orbes par défaut (Abu Ma'shar)
    print("\n--- ORBES PAR DÉFAUT (Abu Ma'shar) ---")
    print("Orbes :", dict(zip([b.decode() for b in ketu.bodies["name"]], ketu.bodies["orb"])))
    aspects_default = ketu.calculate_aspects(jday)
    print(f"Nombre d'aspects : {len(aspects_default)}")

    # Orbes serrés (50%)
    print("\n--- ORBES SERRÉS (50% des orbes par défaut) ---")
    ketu.bodies["orb"] = original_orbs * 0.5
    aspects_tight = ketu.calculate_aspects(jday)
    print(f"Nombre d'aspects : {len(aspects_tight)}")

    # Orbes larges (150%)
    print("\n--- ORBES LARGES (150% des orbes par défaut) ---")
    ketu.bodies["orb"] = original_orbs * 1.5
    aspects_wide = ketu.calculate_aspects(jday)
    print(f"Nombre d'aspects : {len(aspects_wide)}")

    # Restaurer les orbes d'origine
    ketu.bodies["orb"] = original_orbs
    print("\n✓ Orbes restaurés")

    return aspects_default, aspects_tight, aspects_wide


def show_aspect_details(aspects, title):
    """Afficher les détails des aspects"""

    print(f"\n{title}")
    print("-" * 60)

    if len(aspects) == 0:
        print("Aucun aspect trouvé")
        return

    for aspect in aspects:
        b1, b2, asp_idx, orb = aspect
        name1 = ketu.body_name(b1)
        name2 = ketu.body_name(b2)
        asp_name = ketu.aspects["name"][asp_idx].decode()

        print(f"{name1:10} - {name2:10} : {asp_name:12} (orbe: {orb:+6.2f}°)")


def custom_orb_example(jday):
    """Exemple d'utilisation d'orbes personnalisés"""

    print("\n" + "=" * 60)
    print("ORBES PERSONNALISÉS")
    print("=" * 60)

    # Sauvegarder
    original_orbs = ketu.bodies["orb"].copy()

    # Configuration personnalisée : orbes plus serrés pour les planètes rapides
    print("\nConfiguration personnalisée:")
    print("  - Planètes intérieures (☿♀☉): orbes réduits de 30%")
    print("  - Planètes extérieures: orbes standard")

    custom_orbs = original_orbs.copy()
    custom_orbs[0] *= 0.7  # Soleil
    custom_orbs[1] *= 0.7  # Lune
    custom_orbs[2] *= 0.7  # Mercure
    custom_orbs[3] *= 0.7  # Vénus

    ketu.bodies["orb"] = custom_orbs
    aspects_custom = ketu.calculate_aspects(jday)

    show_aspect_details(aspects_custom, "Aspects avec orbes personnalisés")

    # Restaurer
    ketu.bodies["orb"] = original_orbs


def main():
    print("=" * 60)
    print("EXEMPLE 5 : PERSONNALISATION DES ORBES")
    print("=" * 60)

    # Date de test
    paris = ZoneInfo("Europe/Paris")
    dt = datetime(2020, 12, 21, 19, 20, tzinfo=paris)
    print(f"\nDate : {dt.strftime('%d/%m/%Y %H:%M %Z')}")

    jday = ketu.utc_to_julian(dt)

    # Comparaison des réglages
    default, tight, wide = compare_orb_settings(jday)

    # Afficher les différences
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Orbes par défaut  : {len(default)} aspects")
    print(f"Orbes serrés (50%): {len(tight)} aspects")
    print(f"Orbes larges (150%): {len(wide)} aspects")

    # Exemple d'orbes personnalisés
    custom_orb_example(jday)

    print("\n" + "=" * 60)
    print("NOTE: Les orbes ont été restaurés à leurs valeurs par défaut")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
