"""Example: Finding planetary transits to reference positions.

This example demonstrates the transit calculation API that allows you to:
1. Find transits to a fixed longitude (e.g., natal position)
2. Get natal/reference planetary positions
3. Compare two dates to find transiting aspects
"""

from datetime import datetime
from ketu.aspects import (
    find_transits_to_position,
    get_natal_positions,
    compare_dates_transits,
)


def example_1_mars_transit_to_fixed_position():
    """Example 1: When does Mars transit 120° (0° Leo)?"""
    print("=" * 70)
    print("Example 1: Mars Transits to 120° (0° Leo) in 2024")
    print("=" * 70)

    transits = find_transits_to_position(
        transiting_body="Mars",
        reference_longitude=120.0,  # 0° Leo
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    if transits:
        print(f"\nTrouvé {len(transits)} transit(s):\n")
        for i, window in enumerate(transits, 1):
            print(f"{i}. {window.aspect}")
            moment = window.moments[0]
            print(f"   Exact:  {moment.exact.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"   Début:  {moment.begin.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"   Fin:    {moment.end.strftime('%Y-%m-%d %H:%M UTC')}")
            duration = (moment.end - moment.begin).total_seconds() / 86400
            print(f"   Durée:  {duration:.1f} jours")
            print(f"   Mouvement: {moment.motion}")
            print()
    else:
        print("\nAucun transit trouvé")


def example_2_get_natal_chart_positions():
    """Example 2: Get planetary positions for a birth chart."""
    print("=" * 70)
    print("Example 2: Positions Natales (15 mai 1990)")
    print("=" * 70)

    natal = get_natal_positions("1990-05-15 14:30")

    print("\nPositions planétaires à la naissance:\n")

    signs = [
        "Bélier", "Taureau", "Gémeaux", "Cancer",
        "Lion", "Vierge", "Balance", "Scorpion",
        "Sagittaire", "Capricorne", "Verseau", "Poissons"
    ]

    for body_name, pos in list(natal.items())[:10]:  # First 10 planets
        sign_idx = int(pos.longitude / 30)
        sign_deg = pos.longitude % 30
        print(f"{body_name:12s}: {sign_deg:5.2f}° {signs[sign_idx]:12s} ({pos.longitude:6.2f}°)")


def example_3_compare_natal_and_current():
    """Example 3: Compare natal chart with current transits."""
    print("\n" + "=" * 70)
    print("Example 3: Transits Actuels sur Thème Natal")
    print("=" * 70)

    print("\nThème natal: 15 mai 1990, 14:30 UTC")
    print("Date actuelle: 21 novembre 2024, 12:00 UTC\n")

    transits = compare_dates_transits(
        natal_date="1990-05-15 14:30",
        transit_date="2024-11-21 12:00",
        aspects_list=["Conjunction", "Square", "Trine", "Opposition"],
    )

    if transits:
        print(f"Trouvé {len(transits)} aspect(s) de transit:\n")

        # Group by aspect type
        by_aspect = {}
        for t in transits:
            if t.aspect not in by_aspect:
                by_aspect[t.aspect] = []
            by_aspect[t.aspect].append(t)

        for aspect_name in ["Conjunction", "Square", "Trine", "Opposition"]:
            if aspect_name in by_aspect:
                print(f"\n{aspect_name}s:")
                for t in by_aspect[aspect_name]:
                    print(f"  - {t.transiting_body:10s} → natal {t.natal_body}")
    else:
        print("Aucun transit trouvé")


def example_4_jupiter_return():
    """Example 4: Jupiter Return (transit Jupiter conjunct natal Jupiter)."""
    print("\n" + "=" * 70)
    print("Example 4: Retour de Jupiter")
    print("=" * 70)

    # Get natal Jupiter position
    natal = get_natal_positions("1990-05-15 14:30")
    natal_jupiter_lon = natal["Jupiter"].longitude

    print(f"\nJupiter natal: {natal_jupiter_lon:.2f}°")
    print("Recherche des retours de Jupiter (conjonction avec Jupiter natal)...\n")

    # Find when transiting Jupiter returns to natal position
    # Jupiter return happens about every 12 years
    transits = find_transits_to_position(
        transiting_body="Jupiter",
        reference_longitude=natal_jupiter_lon,
        aspects_list=["Conjunction"],
        start_date="2000-01-01",
        end_date="2030-12-31",  # 30 years
    )

    if transits:
        print(f"Trouvé {len(transits)} retour(s) de Jupiter:\n")
        for i, window in enumerate(transits, 1):
            moment = window.moments[0]
            age = 2000 + (moment.exact.year - 1990)  # Approximative age
            print(f"{i}. {moment.exact.strftime('%Y-%m-%d %H:%M UTC')} (âge: ~{age} ans)")
            if len(window.moments) > 1:
                print(f"   Rétrogradation: {len(window.moments)} passages exacts")
                for j, m in enumerate(window.moments, 1):
                    print(f"     Passage {j}: {m.exact.strftime('%Y-%m-%d')}")
            print()


def example_5_saturn_squares():
    """Example 5: Saturn squares (crisis points)."""
    print("=" * 70)
    print("Example 5: Carrés de Saturne (crises)")
    print("=" * 70)

    # Get natal Saturn position
    natal = get_natal_positions("1990-05-15 14:30")
    natal_saturn_lon = natal["Saturn"].longitude

    print(f"\nSaturne natal: {natal_saturn_lon:.2f}°")
    print("Recherche des carrés de Saturne...\n")

    # Find Saturn squares (every ~7 years)
    transits = find_transits_to_position(
        transiting_body="Saturn",
        reference_longitude=natal_saturn_lon,
        aspects_list=["Square"],
        start_date="1990-01-01",
        end_date="2030-12-31",
    )

    if transits:
        print(f"Trouvé {len(transits)} carré(s) de Saturne:\n")
        for i, window in enumerate(transits, 1):
            moment = window.moments[0]
            age = moment.exact.year - 1990
            print(f"{i}. {moment.exact.strftime('%Y-%m-%d')} (âge: {age} ans)")
    else:
        print("Aucun carré trouvé dans la période")


def example_6_moon_transits_quick():
    """Example 6: Moon transits (fast, frequent)."""
    print("\n" + "=" * 70)
    print("Example 6: Transits de la Lune (rapides)")
    print("=" * 70)

    # Moon transits to 0° Aries in one month
    print("\nLune transitant 0° Bélier en janvier 2024:\n")

    transits = find_transits_to_position(
        transiting_body="Moon",
        reference_longitude=0.0,
        aspects_list=["Conjunction"],
        start_date="2024-01-01",
        end_date="2024-02-01",
    )

    if transits:
        print(f"Trouvé {len(transits)} transit(s) (Lune fait le tour en ~28 jours):\n")
        for i, window in enumerate(transits, 1):
            moment = window.moments[0]
            duration_hours = (moment.end - moment.begin).total_seconds() / 3600
            print(f"{i}. Exact: {moment.exact.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"   Durée: {duration_hours:.1f} heures")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "TRANSITS EXAMPLES" + " " * 31 + "║")
    print("╚" + "═" * 68 + "╝")

    # Run all examples
    example_1_mars_transit_to_fixed_position()
    example_2_get_natal_chart_positions()
    example_3_compare_natal_and_current()
    example_4_jupiter_return()
    example_5_saturn_squares()
    example_6_moon_transits_quick()

    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70 + "\n")
