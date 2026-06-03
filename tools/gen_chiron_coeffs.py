"""
Générateur offline des coefficients Chebyshev de Chiron (build-only).
======================================================================

Ce script est **exécuté une seule fois** au moment du build, avec l'extra
``[test]`` de pyswisseph installé et le fichier ``seas_18.se1`` disponible.
Il NE DOIT PAS être importé par le package ``ketu/`` et NE SERA PAS collecté
par pytest (``tools/`` est hors de ``testpaths=["tests"]``).

Paramètres verrouillés (23-DECISION.md, plage étendue Phase 30-02) :
  - Plage     : 1900-01-01 .. 2100-01-01 UTC
  - seg_len   : 32 jours
  - degree    : 10  (11 coefficients/segment)
  - n_segs    : 2283  (ceil(73049 / 32))
  - Quantités : 3 — lon (déroulée), lat, dist
  - Oracle    : swe.calc_ut(jd, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)
  - retflag 260 (Moshier fallback) ACCEPTABLE (seas_18.se1 seul sans sepl_18.se1)

Layout .npz (``np.savez_compressed``) :
  - lon_coeffs  : shape (2283, 11), float64
  - lat_coeffs  : shape (2283, 11), float64
  - dist_coeffs : shape (2283, 11), float64
  - seg_starts  : shape (2283,),    float64  (JD début de chaque segment)
  - seg_len     : scalaire float64  (32.0)
  - degree      : scalaire int32    (10)
  - jd_start    : scalaire float64  (2415020.5)
  - jd_end      : scalaire float64  (2488069.5)

Usage::

    # Standard (produit ketu/data/chiron_coeffs.npz par défaut) :
    SE_EPHE_PATH=/chemin/vers/dossier_avec_seas_18.se1 \\
        python tools/gen_chiron_coeffs.py

    # Sortie personnalisée :
    SE_EPHE_PATH=... python tools/gen_chiron_coeffs.py --output /tmp/chiron.npz

    # Imprimer les longitudes de référence pour les 7 JD de pin (plan 24-04) :
    SE_EPHE_PATH=... python tools/gen_chiron_coeffs.py --dump-refs

Phase 24-01.
"""

import argparse
import math
import os
import sys
import numpy as np
from numpy.polynomial.chebyshev import Chebyshev

# ---------------------------------------------------------------------------
# PARAMÈTRES VERROUILLÉS (23-DECISION.md — NE PAS MODIFIER)
# ---------------------------------------------------------------------------

_SEG_LEN: float = 32.0   # jours juliens par segment
_DEGREE: int = 10         # degré du polynôme de Chebyshev (11 coefficients)
_N_FIT: int = _DEGREE + 8  # noeuds d'ajustement (overdéterminé)

# JDs de référence pour --dump-refs (plan 24-04, étendu Phase 30-02) :
# 1920-01-01 (aile pré-1950), 1950-01-01, 1970-01-01, 1990-01-01, J2000.0,
# 2010-01-01, 2030-01-01, 2050-01-01, 2080-01-01 (aile post-2050)
_REF_JDS: list[float] = [
    2422324.5,  # 1920-01-01 (aile pré-1950)
    2433282.5,  # 1950-01-01
    2440587.5,  # 1970-01-01
    2447892.5,  # 1990-01-01
    2451545.0,  # J2000.0
    2455197.5,  # 2010-01-01
    2462501.5,  # 2030-01-01
    2469807.5,  # 2050-01-01
    2480764.5,  # 2080-01-01 (aile post-2050)
]

_DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ketu", "data", "chiron_coeffs.npz",
)

_DEFAULT_EPHE_PATH = "/home/loc/workspace/rahu/kerykeion/kerykeion/sweph"


# ---------------------------------------------------------------------------
# 1. CONFIGURATION DE L'ORACLE
# ---------------------------------------------------------------------------

def setup_oracle(ephe_path: str) -> tuple[float, float, int]:
    """
    Configure le chemin d'éphéméride pyswisseph et retourne la plage JD.

    Paramètres
    ----------
    ephe_path : str
        Répertoire contenant ``seas_18.se1``.

    Retourne
    --------
    jd0 : float
        JD pour 1900-01-01 00:00 UT (2415020.5).
    jd1 : float
        JD pour 2100-01-01 00:00 UT (2488069.5).
    retflag : int
        Indicateur de retour de pyswisseph (260 = Moshier+SPEED, acceptable).

    Notes
    -----
    ``retflag == 260`` (MOSEPH+SPEED) est attendu et acceptable quand seul
    ``seas_18.se1`` est disponible (sans ``sepl_18.se1``). La différence vs
    SWIEPH est ≤ 0.000067° sur 1900-2100, négligeable face à la cible 0.01°.
    """
    import swisseph as swe  # type: ignore  # build-only

    swe.set_ephe_path(ephe_path)
    jd0 = swe.julday(1900, 1, 1, 0.0)
    jd1 = swe.julday(2100, 1, 1, 0.0)

    # Vérification rapide à J2000.0
    jd_test = 2451545.0
    try:
        xx, retflag, errmsg = swe.calc_ut(
            jd_test, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED
        )
    except Exception as exc:
        print(
            f"\n[ERREUR] Impossible de calculer la position de Chiron.\n"
            f"  Dossier essayé : {ephe_path}\n"
            f"  seas_18.se1 doit être présent dans ce dossier.\n"
            f"  Définir SE_EPHE_PATH si le fichier est ailleurs.\n"
            f"  Erreur originale : {exc}\n"
        )
        sys.exit(1)

    flag_desc = (
        "SWIEPH+SPEED" if retflag == 258
        else "MOSEPH+SPEED (fallback Moshier, acceptable)" if retflag == 260
        else str(retflag)
    )
    print(f"Oracle pyswisseph prêt.")
    print(f"  ephe_path  : {ephe_path}")
    print(f"  retflag    : {retflag}  ({flag_desc})")
    print(f"  swe.CHIRON : {swe.CHIRON}")
    print(f"  jd0        : {jd0:.4f}  (1900-01-01)")
    print(f"  jd1        : {jd1:.4f}  (2100-01-01)")
    total_days = jd1 - jd0
    n_segs = math.ceil(total_days / _SEG_LEN)
    print(f"  total_days : {total_days:.1f}")
    print(f"  n_segs     : {n_segs}  (ceil({total_days:.1f}/{_SEG_LEN}))")
    print()

    return jd0, jd1, retflag


# ---------------------------------------------------------------------------
# 2. ÉCHANTILLONNEURS CHIRON (lon déroulée, lat, dist)
# ---------------------------------------------------------------------------

def sample_chiron_unwrapped(jd_array: np.ndarray) -> np.ndarray:
    """
    Échantillonne la longitude géocentrique écliptique de Chiron (déroulée).

    Parcourt ``jd_array`` (croissant) et déroule les sauts 0°/360° via un
    offset cumulatif afin d'obtenir une série lisse pour l'ajustement
    Chebyshev.

    Paramètres
    ----------
    jd_array : np.ndarray
        Tableau de jours juliens croissants.

    Retourne
    --------
    np.ndarray
        Longitudes déroulées (peuvent dépasser 360° ou être négatives).

    Notes
    -----
    L'offset est appliqué localement à l'échelle du segment (32 j), donc
    les valeurs déroulées ne sont pas monotones globalement — elles le sont
    seulement à l'intérieur de chaque segment, ce qui suffit pour l'ajustement.
    """
    import swisseph as swe  # type: ignore  # build-only

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    offset = 0.0
    prev_lon = None
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(float(jd), swe.CHIRON, flags)
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
    """
    Échantillonne la latitude géocentrique écliptique de Chiron.

    Paramètres
    ----------
    jd_array : np.ndarray
        Tableau de jours juliens.

    Retourne
    --------
    np.ndarray
        Latitudes écliptiques géocentriques (degrés, pas de déroulage).
    """
    import swisseph as swe  # type: ignore  # build-only

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(float(jd), swe.CHIRON, flags)
        result[i] = xx[1]
    return result


def sample_chiron_dist(jd_array: np.ndarray) -> np.ndarray:
    """
    Échantillonne la distance géocentrique de Chiron en UA.

    Paramètres
    ----------
    jd_array : np.ndarray
        Tableau de jours juliens.

    Retourne
    --------
    np.ndarray
        Distances en unités astronomiques (pas de déroulage).
    """
    import swisseph as swe  # type: ignore  # build-only

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = np.empty(len(jd_array))
    for i, jd in enumerate(jd_array):
        xx, _, _ = swe.calc_ut(float(jd), swe.CHIRON, flags)
        result[i] = xx[2]
    return result


# ---------------------------------------------------------------------------
# 3. AJUSTEMENT CHEBYSHEV D'UN SEGMENT
# ---------------------------------------------------------------------------

def fit_segment(
    jd_s: float,
    jd_e: float,
    sampler,
) -> np.ndarray:
    """
    Ajuste un polynôme de Chebyshev de degré ``_DEGREE`` sur ``[jd_s, jd_e]``.

    Paramètres
    ----------
    jd_s : float
        JD de début du segment (inclus).
    jd_e : float
        JD de fin du segment (exclu, peut être jd_s + seg_len ou jd1 si dernier segment).
    sampler : callable
        Fonction ``f(jd_array) -> np.ndarray`` qui interroge l'oracle Swiss Ephemeris.

    Retourne
    --------
    np.ndarray
        Tableau de ``_DEGREE + 1`` coefficients Chebyshev (float64), dans le
        domaine standard ``[-1, 1]``.

    Notes
    -----
    Noeuds d'ajustement : ``n_fit = _DEGREE + 8`` points uniformes dans ``[-1, 1]``.
    L'ajustement utilise ``Chebyshev.fit(t_fit, y_fit, _DEGREE, domain=[-1.0, 1.0])``,
    ce qui correspond à ``np.polynomial.chebyshev.chebval(t, coef)`` avec
    ``t = 2*(jd - jd_s)/(jd_e - jd_s) - 1``.
    """
    actual_len = jd_e - jd_s
    t_fit = np.linspace(-1.0, 1.0, _N_FIT)
    jd_fit = jd_s + (t_fit + 1.0) / 2.0 * actual_len
    y_fit = sampler(jd_fit)
    poly = Chebyshev.fit(t_fit, y_fit, _DEGREE, domain=[-1.0, 1.0])
    return poly.coef.astype(np.float64)


# ---------------------------------------------------------------------------
# 4. AJUSTEMENT COMPLET 1950-2050 (3 QUANTITÉS)
# ---------------------------------------------------------------------------

def generate_all_coefficients(
    jd0: float,
    jd1: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Génère les coefficients Chebyshev pour lon, lat et dist sur 1900-2100.

    Paramètres
    ----------
    jd0 : float
        JD de début (1900-01-01 00:00 UT).
    jd1 : float
        JD de fin   (2100-01-01 00:00 UT).

    Retourne
    --------
    lon_coeffs : np.ndarray, shape (n_segs, degree+1)
        Coefficients Chebyshev pour la longitude déroulée (re-wrap % 360 à l'éval).
    lat_coeffs : np.ndarray, shape (n_segs, degree+1)
        Coefficients Chebyshev pour la latitude.
    dist_coeffs : np.ndarray, shape (n_segs, degree+1)
        Coefficients Chebyshev pour la distance en UA.
    seg_starts : np.ndarray, shape (n_segs,)
        JD de début de chaque segment (jd0 + si * seg_len).

    Notes
    -----
    Le dernier segment peut être plus court que ``_SEG_LEN`` si la plage totale
    n'est pas divisible par 32. L'ajustement utilise la longueur réelle du
    dernier segment.
    """
    total_days = jd1 - jd0
    n_segs = math.ceil(total_days / _SEG_LEN)
    deg1 = _DEGREE + 1

    lon_coeffs = np.zeros((n_segs, deg1), dtype=np.float64)
    lat_coeffs = np.zeros((n_segs, deg1), dtype=np.float64)
    dist_coeffs = np.zeros((n_segs, deg1), dtype=np.float64)
    seg_starts = np.empty(n_segs, dtype=np.float64)

    print(f"Ajustement Chebyshev : {n_segs} segments × 3 quantités...")
    for si in range(n_segs):
        jd_s = jd0 + si * _SEG_LEN
        jd_e = min(jd_s + _SEG_LEN, jd1)
        seg_starts[si] = jd_s

        lon_coeffs[si] = fit_segment(jd_s, jd_e, sample_chiron_unwrapped)
        lat_coeffs[si] = fit_segment(jd_s, jd_e, sample_chiron_lat)
        dist_coeffs[si] = fit_segment(jd_s, jd_e, sample_chiron_dist)

        if (si + 1) % 100 == 0 or si == n_segs - 1:
            print(f"  ... {si + 1}/{n_segs} segments traités", flush=True)

    print()
    return lon_coeffs, lat_coeffs, dist_coeffs, seg_starts


# ---------------------------------------------------------------------------
# 5. VALIDATION (pur-NumPy — GATE avant écriture)
# ---------------------------------------------------------------------------

def validate_coefficients(
    lon_coeffs: np.ndarray,
    lat_coeffs: np.ndarray,
    dist_coeffs: np.ndarray,
    seg_starts: np.ndarray,
    jd0: float,
    jd1: float,
    n_val_per_seg: int = 200,
) -> tuple[float, float, float, float]:
    """
    Valide les coefficients en comparant l'évaluateur pur-NumPy à l'oracle.

    Pour chaque segment, échantillonne ``n_val_per_seg`` points sur une grille
    dense, évalue les coefficients avec ``np.polynomial.chebyshev.chebval``
    (pur NumPy, sans objet Chebyshev) et compare au vrai oracle pyswisseph.
    Retourne les erreurs max pour lon, lat et dist.

    Paramètres
    ----------
    lon_coeffs : np.ndarray, shape (n_segs, degree+1)
    lat_coeffs : np.ndarray, shape (n_segs, degree+1)
    dist_coeffs : np.ndarray, shape (n_segs, degree+1)
    seg_starts : np.ndarray, shape (n_segs,)
    jd0 : float
        JD de début de la plage.
    jd1 : float
        JD de fin de la plage.
    n_val_per_seg : int
        Nombre de points de validation par segment (défaut 200).

    Retourne
    --------
    max_lon_err : float
        Erreur maximale sur la longitude (degrés).
    max_lat_err : float
        Erreur maximale sur la latitude (degrés).
    max_dist_err : float
        Erreur maximale sur la distance (UA).
    worst_jd : float
        JD du segment le plus difficile (longitude).

    Notes
    -----
    La longitude est re-wrappée modulo 360° côté prédit **et** côté oracle
    avant comparaison, afin d'éliminer les artefacts de déroulage.
    """
    import swisseph as swe  # type: ignore  # build-only
    import numpy.polynomial.chebyshev as npc

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    n_segs = len(seg_starts)
    max_lon_err = 0.0
    max_lat_err = 0.0
    max_dist_err = 0.0
    worst_jd = jd0

    print(f"Validation pur-NumPy : {n_segs} segments × {n_val_per_seg} points...")
    for si in range(n_segs):
        jd_s = seg_starts[si]
        jd_e = min(jd_s + _SEG_LEN, jd1)
        actual_len = jd_e - jd_s

        t_val = np.linspace(-1.0, 1.0, n_val_per_seg)
        jd_val = jd_s + (t_val + 1.0) / 2.0 * actual_len

        # Évaluateur pur-NumPy (chebval, pas l'objet Chebyshev)
        lon_pred = npc.chebval(t_val, lon_coeffs[si]) % 360.0
        lat_pred = npc.chebval(t_val, lat_coeffs[si])
        dist_pred = npc.chebval(t_val, dist_coeffs[si])

        # Oracle pour la validation
        lon_true = np.empty(n_val_per_seg)
        lat_true = np.empty(n_val_per_seg)
        dist_true = np.empty(n_val_per_seg)
        for k, jd in enumerate(jd_val):
            xx, _, _ = swe.calc_ut(float(jd), swe.CHIRON, flags)
            lon_true[k] = xx[0] % 360.0
            lat_true[k] = xx[1]
            dist_true[k] = xx[2]

        lon_errs = np.abs(lon_pred - lon_true)
        # Correction wrap (ex. 359.9 vs 0.1 → erreur réelle = 0.2°, pas 359.8°)
        lon_errs = np.minimum(lon_errs, 360.0 - lon_errs)
        lat_errs = np.abs(lat_pred - lat_true)
        dist_errs = np.abs(dist_pred - dist_true)

        seg_max_lon = float(np.max(lon_errs))
        seg_max_lat = float(np.max(lat_errs))
        seg_max_dist = float(np.max(dist_errs))

        if seg_max_lon > max_lon_err:
            max_lon_err = seg_max_lon
            worst_jd = float(jd_val[np.argmax(lon_errs)])

        if seg_max_lat > max_lat_err:
            max_lat_err = seg_max_lat
        if seg_max_dist > max_dist_err:
            max_dist_err = seg_max_dist

        if (si + 1) % 100 == 0 or si == n_segs - 1:
            print(f"  ... {si + 1}/{n_segs} validés | max|Δλ| courant={max_lon_err:.6f}°", flush=True)

    print()
    return max_lon_err, max_lat_err, max_dist_err, worst_jd


# ---------------------------------------------------------------------------
# 6. DUMP DES LONGITUDES DE RÉFÉRENCE (--dump-refs)
# ---------------------------------------------------------------------------

def dump_reference_longitudes() -> None:
    """
    Imprime les 9 longitudes de référence Chiron pour les JDs pin (plan 24-04, étendu Phase 30-02).

    Appelle l'oracle pyswisseph pour chacun des 9 JDs verrouillés et imprime
    une liste Python de tuples (jd, lon) prête à être copiée dans le fichier
    de test de régression.

    Notes
    -----
    Les dates correspondent à : 1920-01-01 (aile pré-1950), 1950-01-01,
    1970-01-01, 1990-01-01, J2000.0, 2010-01-01, 2030-01-01, 2050-01-01,
    2080-01-01 (aile post-2050).
    """
    import swisseph as swe  # type: ignore  # build-only

    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    labels = [
        "1920-01-01",
        "1950-01-01",
        "1970-01-01",
        "1990-01-01",
        "J2000.0   ",
        "2010-01-01",
        "2030-01-01",
        "2050-01-01",
        "2080-01-01",
    ]
    print("# Longitudes de référence Chiron (oracle pyswisseph + seas_18.se1)")
    print("# Copiez cette liste dans tests/ephemeris/test_chiron_regression.py")
    print()
    print("_CHIRON_REFS: list[tuple[float, float]] = [")
    for jd, label in zip(_REF_JDS, labels):
        xx, retflag, _ = swe.calc_ut(jd, swe.CHIRON, flags)
        lon = xx[0] % 360.0
        print(f"    ({jd}, {lon:.6f}),  # {label}  retflag={retflag}")
    print("]")


# ---------------------------------------------------------------------------
# 7. ÉCRITURE DU .NPZ
# ---------------------------------------------------------------------------

def write_npz(
    output_path: str,
    lon_coeffs: np.ndarray,
    lat_coeffs: np.ndarray,
    dist_coeffs: np.ndarray,
    seg_starts: np.ndarray,
    jd0: float,
    jd1: float,
) -> None:
    """
    Écrit le fichier ``.npz`` compressé avec le layout verrouillé.

    Paramètres
    ----------
    output_path : str
        Chemin de sortie (ex. ``ketu/data/chiron_coeffs.npz``).
    lon_coeffs : np.ndarray, shape (n_segs, 11)
    lat_coeffs : np.ndarray, shape (n_segs, 11)
    dist_coeffs : np.ndarray, shape (n_segs, 11)
    seg_starts : np.ndarray, shape (n_segs,)
    jd0 : float
        JD de début de la plage.
    jd1 : float
        JD de fin de la plage.

    Notes
    -----
    Le fichier .npz contiendra exactement 8 tableaux nommés : ``lon_coeffs``,
    ``lat_coeffs``, ``dist_coeffs``, ``seg_starts``, ``seg_len``, ``degree``,
    ``jd_start``, ``jd_end``.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    np.savez_compressed(
        output_path,
        lon_coeffs=lon_coeffs,
        lat_coeffs=lat_coeffs,
        dist_coeffs=dist_coeffs,
        seg_starts=seg_starts,
        seg_len=np.float64(_SEG_LEN),
        degree=np.int32(_DEGREE),
        jd_start=np.float64(jd0),
        jd_end=np.float64(jd1),
    )
    import os as _os
    size_kb = _os.path.getsize(output_path) / 1024
    print(f"Fichier écrit : {output_path}  ({size_kb:.1f} KB)")


# ---------------------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Point d'entrée du générateur offline.

    Analyse les arguments CLI, configure l'oracle, génère les coefficients,
    valide la précision (gate max|Δλ| < 0.01°) et écrit le .npz.

    Notes
    -----
    Quitte avec ``sys.exit(1)`` si la validation échoue (max|Δλ| >= 0.01°).
    Ce comportement est intentionnel : le .npz ne doit JAMAIS être écrit sans
    que la précision ait été confirmée.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Générateur offline des coefficients Chebyshev de Chiron (build-only). "
            "Nécessite pyswisseph [test] et seas_18.se1. "
            "NE PAS importer depuis ketu/."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemples :\n"
            "  SE_EPHE_PATH=/chemin/sweph python tools/gen_chiron_coeffs.py\n"
            "  SE_EPHE_PATH=/chemin/sweph python tools/gen_chiron_coeffs.py "
            "--output /tmp/chiron.npz\n"
            "  SE_EPHE_PATH=/chemin/sweph python tools/gen_chiron_coeffs.py --dump-refs\n"
        ),
    )
    parser.add_argument(
        "--output",
        default=_DEFAULT_OUTPUT,
        help=(
            "Chemin de sortie du .npz "
            f"(défaut : ketu/data/chiron_coeffs.npz)"
        ),
    )
    parser.add_argument(
        "--dump-refs",
        action="store_true",
        help=(
            "Imprime les 9 longitudes de référence Chiron (JDs pin pour plan 24-04/30-02) "
            "et quitte sans générer le .npz."
        ),
    )
    args = parser.parse_args()

    # Chemin de l'éphéméride : variable d'environnement ou chemin connu
    ephe_path = os.environ.get("SE_EPHE_PATH", _DEFAULT_EPHE_PATH)

    print("=" * 70)
    print("Générateur Chiron Chebyshev (Phase 24-01)")
    print("=" * 70)
    print()

    # Mode --dump-refs : imprimer les références et quitter
    if args.dump_refs:
        # Besoin de setup_oracle pour configurer swe.set_ephe_path
        setup_oracle(ephe_path)
        dump_reference_longitudes()
        return

    # Mode standard : générer le .npz complet
    jd0, jd1, _retflag = setup_oracle(ephe_path)

    # Générer tous les coefficients
    lon_coeffs, lat_coeffs, dist_coeffs, seg_starts = generate_all_coefficients(
        jd0, jd1
    )

    # GATE DE VALIDATION (pur-NumPy vs oracle)
    print("=== GATE DE VALIDATION (pur-NumPy vs oracle) ===")
    print()
    max_lon_err, max_lat_err, max_dist_err, worst_jd = validate_coefficients(
        lon_coeffs, lat_coeffs, dist_coeffs, seg_starts, jd0, jd1
    )

    print(f"  max|Δλ|   : {max_lon_err:.6f}°  (cible : < 0.01°)")
    print(f"  max|Δlat| : {max_lat_err:.6f}°")
    print(f"  max|Δdist|: {max_dist_err:.9f} UA")
    print(f"  pire JD   : {worst_jd:.2f}")
    print()

    _THRESHOLD = 0.01  # degrés
    if max_lon_err >= _THRESHOLD:
        print(
            f"[ERREUR] VALIDATION ÉCHOUÉE : max|Δλ|={max_lon_err:.6f}° "
            f">= {_THRESHOLD}°\n"
            f"  Le .npz ne sera PAS écrit. Vérifier les paramètres."
        )
        sys.exit(1)

    print(f"Validation OK : max|Δλ|={max_lon_err:.6f}° < {_THRESHOLD}°  "
          f"(marge {_THRESHOLD / max_lon_err:.1f}×)")
    print()

    # Écriture du .npz
    write_npz(args.output, lon_coeffs, lat_coeffs, dist_coeffs, seg_starts, jd0, jd1)

    print()
    print("=" * 70)
    print("Générateur terminé avec succès.")
    print("=" * 70)


if __name__ == "__main__":
    main()
