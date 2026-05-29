"""
Spike SPK-01 : Ajustement Chebyshev-par-segment pour Chiron (geocentrique)
===========================================================================
Script jetable — NE PAS importer depuis ketu/, NE PAS collecter par pytest.

Objectif :
  Mesurer la précision max de l'ajustement Chebyshev-par-segment de la longitude
  écliptique géocentrique de Chiron versus l'oracle Swiss Ephemeris (pyswisseph),
  sur toute la plage 1950-2050 UTC.

Livrables :
  - Table de sweep des configurations (seg_d, degré, n_segs, coeffs/seg,
    total_coeffs, .npz KB lon-only, max |Δλ|, <0.01° ?)
  - Précision lat/dist pour la config primaire (32j, deg=10)
  - Confirmation de l'évaluateur pur-NumPy (chebval, sans scipy)

Usage :
  SE_EPHE_PATH=/chemin/vers/dossier_avec_seas_18 \\
    python spike_chiron_chebyshev.py

Auteur : Dr. Sophie Chen (spike Phase 23)
"""

import os
import sys
import math
import numpy as np
from numpy.polynomial.chebyshev import Chebyshev, chebval

# ---------------------------------------------------------------------------
# 1. CONFIGURATION DE L'ORACLE
# ---------------------------------------------------------------------------

def setup_oracle() -> None:
    """Configure le chemin d'éphéméride pyswisseph et vérifie l'accès à Chiron."""
    import swisseph as swe  # type: ignore

    # Ordre de recherche : variable d'environnement, puis chemin local connu
    ephe_dir = os.environ.get(
        "SE_EPHE_PATH",
        "/home/loc/workspace/rahu/kerykeion/kerykeion/sweph",
    )
    swe.set_ephe_path(ephe_dir)

    # Vérification rapide : une date connue (J2000.0)
    jd_test = 2451545.0  # 2000-01-01 12:00 TT ≈ UT
    try:
        xx, retflag, errmsg = swe.calc_ut(
            jd_test, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED
        )
    except Exception as exc:
        print(
            f"\n[ERREUR] Impossible de calculer la position de Chiron.\n"
            f"  Dossier essayé : {ephe_dir}\n"
            f"  Le fichier seas_18.se1 doit être présent dans ce dossier.\n"
            f"  Définis la variable SE_EPHE_PATH si le fichier est ailleurs.\n"
            f"  Erreur originale : {exc}\n"
        )
        sys.exit(1)

    print(f"Oracle pyswisseph prêt.")
    print(f"  set_ephe_path : {ephe_dir}")
    print(f"  retflag J2000 : {retflag}  "
          f"({'SWIEPH+SPEED' if retflag == 258 else 'MOSEPH+SPEED (fallback Moshier)' if retflag == 260 else retflag})")
    print(f"  swe.CHIRON    : {swe.CHIRON}")
    print()
    return retflag, ephe_dir


# ---------------------------------------------------------------------------
# 2. CALCUL DE LA PLAGE DE DATES ET DE JD
# ---------------------------------------------------------------------------

def compute_jd_range():
    """Calcule jd0/jd1 pour 1950-01-01 .. 2050-01-01 UTC via swe.julday."""
    import swisseph as swe  # type: ignore
    jd0 = swe.julday(1950, 1, 1, 0.0)   # UT grégorien
    jd1 = swe.julday(2050, 1, 1, 0.0)
    total_days = jd1 - jd0
    print(f"Plage : 1950-01-01 .. 2050-01-01 UTC")
    print(f"  jd0          : {jd0:.4f}")
    print(f"  jd1          : {jd1:.4f}")
    print(f"  total_days   : {total_days:.1f}")
    print()
    return jd0, jd1, total_days


# ---------------------------------------------------------------------------
# 3. ÉCHANTILLONNEURS CHIRON (LON déroulée, LAT, DIST)
# ---------------------------------------------------------------------------

def sample_chiron_unwrapped(jd_array: np.ndarray) -> np.ndarray:
    """
    Échantillonne la longitude géocentrique écliptique de Chiron (déroulée).

    Pour un jd_array croissant, calcule swe.calc_ut par JD, prend lon=xx[0],
    et DÉROULE via un offset cumulatif (diff>180 → offset-=360 ; diff<-180 →
    offset+=360) pour obtenir une série lisse/monotone (sans saut 0/360).

    Paramètres
    ----------
    jd_array : np.ndarray
        Tableau de jours juliens croissants.

    Retourne
    --------
    np.ndarray
        Longitudes déroulées (peuvent dépasser 360° ou être négatives).
    """
    import swisseph as swe  # type: ignore
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    offset = 0.0
    prev_lon = None
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(jd, swe.CHIRON, flags)
        lon = xx[0]
        if prev_lon is not None:
            diff = lon - prev_lon
            if diff > 180.0:
                offset -= 360.0
            elif diff < -180.0:
                offset += 360.0
        result[i] = lon + offset
        prev_lon = lon
    return result


def sample_chiron_lat(jd_array: np.ndarray) -> np.ndarray:
    """Échantillonne la latitude géocentrique écliptique de Chiron (pas de déroulage)."""
    import swisseph as swe  # type: ignore
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(jd, swe.CHIRON, flags)
        result[i] = xx[1]
    return result


def sample_chiron_dist(jd_array: np.ndarray) -> np.ndarray:
    """Échantillonne la distance géocentrique de Chiron en UA (pas de déroulage)."""
    import swisseph as swe  # type: ignore
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(jd, swe.CHIRON, flags)
        result[i] = xx[2]
    return result


# ---------------------------------------------------------------------------
# 4. AJUSTEMENT ET MESURE D'ERREUR SUR UN SEGMENT
# ---------------------------------------------------------------------------

def fit_and_measure_segment(
    jd_s: float,
    jd_e: float,
    degree: int,
    sampler,
    n_val: int = 200,
) -> tuple[np.ndarray, float, float]:
    """
    Ajuste un polynôme de Chebyshev sur [jd_s, jd_e] et mesure l'erreur max.

    Noeuds d'ajustement : n_fit = degree+8, uniformes dans [-1,1].
    Grille de validation : n_val points, DISTINCTS des noeuds d'ajustement.

    Retourne
    --------
    coef : np.ndarray
        Coefficients Chebyshev (degree+1).
    max_err : float
        Erreur max absolue sur la grille de validation (en unités de la quantité).
    worst_jd : float
        JD de la pire erreur sur la grille de validation.
    """
    actual_len = jd_e - jd_s

    # Noeuds d'ajustement (overdéterminé, uniformes)
    n_fit = degree + 8
    t_fit = np.linspace(-1.0, 1.0, n_fit)
    jd_fit = jd_s + (t_fit + 1.0) / 2.0 * actual_len
    y_fit = sampler(jd_fit)

    # Ajustement Chebyshev (moindres carrés)
    poly = Chebyshev.fit(t_fit, y_fit, degree, domain=[-1.0, 1.0])

    # Grille de validation distincte et plus dense
    t_val = np.linspace(-1.0, 1.0, n_val)
    jd_val = jd_s + (t_val + 1.0) / 2.0 * actual_len
    y_true = sampler(jd_val)
    y_pred = chebval(t_val, poly.coef)

    errors = np.abs(y_pred - y_true)
    max_err = float(np.max(errors))
    worst_jd = float(jd_val[np.argmax(errors)])

    return poly.coef, max_err, worst_jd


# ---------------------------------------------------------------------------
# 5. SWEEP DE CONFIGURATIONS
# ---------------------------------------------------------------------------

def run_config_sweep(
    jd0: float,
    jd1: float,
    total_days: float,
    configs: list[tuple[int, int]],
) -> list[dict]:
    """
    Lance l'ajustement sur tous les segments pour chaque configuration.

    Paramètres
    ----------
    configs : liste de (seg_len_days, degree)

    Retourne
    --------
    Liste de dicts avec les métriques de chaque configuration.
    """
    results = []

    for seg_len, degree in configs:
        n_segs = math.ceil(total_days / seg_len)
        max_err_global = 0.0
        worst_seg_jd = jd0
        print(f"  Config (seg={seg_len}j, deg={degree}) : {n_segs} segments...", end="", flush=True)

        for si in range(n_segs):
            jd_s = jd0 + si * seg_len
            jd_e = min(jd_s + seg_len, jd1)

            _, seg_err, seg_worst_jd = fit_and_measure_segment(
                jd_s, jd_e, degree, sample_chiron_unwrapped
            )
            if seg_err > max_err_global:
                max_err_global = seg_err
                worst_seg_jd = seg_worst_jd

        coeffs_per_seg = degree + 1
        total_coeffs = n_segs * coeffs_per_seg
        npz_lon_kb = total_coeffs * 8 / 1024
        ok = max_err_global < 0.01

        results.append({
            "seg_d": seg_len,
            "degree": degree,
            "n_segs": n_segs,
            "coeffs_per_seg": coeffs_per_seg,
            "total_coeffs": total_coeffs,
            "npz_lon_kb": npz_lon_kb,
            "max_err_deg": max_err_global,
            "ok": ok,
            "worst_jd": worst_seg_jd,
        })
        print(f" max|Δλ|={max_err_global:.6f}° {'✓' if ok else '✗'}")

    return results


# ---------------------------------------------------------------------------
# 6. PRÉCISION LAT/DIST POUR LA CONFIG PRIMAIRE
# ---------------------------------------------------------------------------

def measure_lat_dist_accuracy(
    jd0: float,
    jd1: float,
    total_days: float,
    seg_len: int,
    degree: int,
) -> dict:
    """Mesure la précision max pour lat et dist sur tous les segments."""
    n_segs = math.ceil(total_days / seg_len)
    max_lat_err = 0.0
    max_dist_err = 0.0
    print(f"  Précision lat/dist (seg={seg_len}j, deg={degree}) : {n_segs} segments...", end="", flush=True)

    for si in range(n_segs):
        jd_s = jd0 + si * seg_len
        jd_e = min(jd_s + seg_len, jd1)

        _, lat_err, _ = fit_and_measure_segment(
            jd_s, jd_e, degree, sample_chiron_lat
        )
        _, dist_err, _ = fit_and_measure_segment(
            jd_s, jd_e, degree, sample_chiron_dist
        )

        if lat_err > max_lat_err:
            max_lat_err = lat_err
        if dist_err > max_dist_err:
            max_dist_err = dist_err

    print(f" max|Δlat|={max_lat_err:.6f}° | max|Δdist|={max_dist_err:.9f} UA")
    return {"max_lat_deg": max_lat_err, "max_dist_au": max_dist_err}


# ---------------------------------------------------------------------------
# 7. VÉRIFICATION DE L'ÉVALUATEUR PUR-NUMPY
# ---------------------------------------------------------------------------

def verify_chebval_pure_numpy() -> None:
    """
    Confirme que chebval(t, coef) est équivalent à Chebyshev(coef)(t).
    Aucune dépendance scipy : pur NumPy.
    """
    import swisseph as swe  # type: ignore

    # Prendre un segment arbitraire (début de plage)
    jd0 = swe.julday(1950, 1, 1, 0.0)
    jd_e = jd0 + 32.0
    degree = 10
    n_fit = degree + 8
    t_fit = np.linspace(-1.0, 1.0, n_fit)
    jd_fit = jd0 + (t_fit + 1.0) / 2.0 * 32.0

    y_fit = sample_chiron_unwrapped(jd_fit)
    poly = Chebyshev.fit(t_fit, y_fit, degree, domain=[-1.0, 1.0])

    t_check = np.linspace(-1.0, 1.0, 57)
    y_poly = poly(t_check)
    y_chebval = chebval(t_check, poly.coef)

    assert np.allclose(y_poly, y_chebval, atol=1e-12), (
        f"chebval != poly(t) : diff max = {np.max(np.abs(y_poly - y_chebval))}"
    )
    print("evaluateur chebval pur-NumPy: OK")


# ---------------------------------------------------------------------------
# 8. FORMATAGE DE LA TABLE ASCII
# ---------------------------------------------------------------------------

def jd_to_iso(jd: float) -> str:
    """Convertit un JD en date ISO approximative (année-mois-jour)."""
    import swisseph as swe  # type: ignore
    # swe.revjul retourne (year, month, day, hour)
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def print_table(results: list[dict]) -> None:
    """Affiche la table de sweep des configurations."""
    header = (
        f"{'seg (d)':>7} {'deg':>3} {'n_segs':>7} "
        f"{'coef/seg':>8} {'total_coef':>10} "
        f"{'npz_lon (KB)':>12} {'max|Δλ| (°)':>13} {'<0.01°?':>8}"
    )
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for r in results:
        primary_marker = " *" if r["seg_d"] == 32 and r["degree"] == 10 else "  "
        ok_str = "OUI" if r["ok"] else "NON"
        print(
            f"{r['seg_d']:>7} {r['degree']:>3} {r['n_segs']:>7} "
            f"{r['coeffs_per_seg']:>8} {r['total_coeffs']:>10} "
            f"{r['npz_lon_kb']:>12.1f} {r['max_err_deg']:>13.6f} {ok_str:>8}{primary_marker}"
        )
    print(sep)
    print("  * = config primaire recommandée")


# ---------------------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("Spike SPK-01 : Ajustement Chebyshev-par-segment — Chiron")
    print("=" * 70)
    print()

    # 1. Oracle
    retflag, ephe_dir = setup_oracle()

    # 2. Plage de dates
    jd0, jd1, total_days = compute_jd_range()

    # 3. Sweep des configurations
    # Config primaire + bracketing (seg_len_jours, degré)
    CONFIGS = [
        (32, 10),  # primaire
        (32,  8),  # bracketing degré inférieur
        (32, 12),  # bracketing degré supérieur
        (16,  8),  # segments plus courts
        (64,  8),  # segments plus longs
    ]

    print("=== SWEEP DES CONFIGURATIONS (longitude uniquement) ===")
    print()
    sweep_results = run_config_sweep(jd0, jd1, total_days, CONFIGS)
    print()

    # Résultats de la config primaire
    primary = next(r for r in sweep_results if r["seg_d"] == 32 and r["degree"] == 10)
    worst_date = jd_to_iso(primary["worst_jd"])
    worst_jd_val = primary["worst_jd"]

    # Empreinte lon+lat+dist pour la config primaire
    n_segs_primary = primary["n_segs"]
    total_coeffs_3q = n_segs_primary * (10 + 1) * 3
    npz_3q_kb = total_coeffs_3q * 8 / 1024

    # 4. Précision lat/dist pour la config primaire
    print("=== PRÉCISION LAT/DIST (config primaire 32j, deg=10) ===")
    print()
    lat_dist = measure_lat_dist_accuracy(jd0, jd1, total_days, seg_len=32, degree=10)
    print()

    # 5. Vérification évaluateur pur-NumPy
    print("=== VÉRIFICATION ÉVALUATEUR PUR-NUMPY ===")
    print()
    verify_chebval_pure_numpy()
    print()

    # 6. Affichage de la table finale
    print("=" * 70)
    print("TABLE DE SWEEP — max |Δλ| sur TOUS les segments (grille 200 pts)")
    print("=" * 70)
    print()
    print_table(sweep_results)
    print()

    # 7. Récapitulatif config primaire
    print("=== CONFIG PRIMAIRE (32j, deg=10) — RÉCAPITULATIF ===")
    print()
    print(f"  n_segs              : {primary['n_segs']}")
    print(f"  coeffs/seg (lon)    : {primary['coeffs_per_seg']}")
    print(f"  total coeffs (lon)  : {primary['total_coeffs']}")
    print(f"  .npz lon-only       : {primary['npz_lon_kb']:.1f} KB")
    print(f"  total coeffs (×3)   : {total_coeffs_3q}")
    print(f"  .npz lon+lat+dist   : {npz_3q_kb:.1f} KB")
    print(f"  max |Δλ| (°)        : {primary['max_err_deg']:.6f}")
    print(f"  marge vs 0.01°      : {0.01 / primary['max_err_deg']:.1f}×")
    print(f"  max |Δlat| (°)      : {lat_dist['max_lat_deg']:.6f}")
    print(f"  max |Δdist| (UA)    : {lat_dist['max_dist_au']:.9f}")
    print(f"  segment le pire     : {worst_date}  (JD {worst_jd_val:.2f})")
    print(f"  retflag oracle      : {retflag}")
    print(f"  <0.01° ?            : {'OUI' if primary['ok'] else 'NON'}")
    print()
    print("=" * 70)
    print("Spike SPK-01 terminé.")
    print("=" * 70)
