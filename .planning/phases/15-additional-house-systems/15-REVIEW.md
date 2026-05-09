---
phase: 15-additional-house-systems
reviewed: 2026-05-09T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - CHANGELOG.md
  - .gitignore
  - ketu/cli/introspection.py
  - ketu/cli/parser.py
  - ketu/houses/api.py
  - ketu/houses/core.py
  - ketu/houses/_ecliptic.py
  - ketu/houses/equal.py
  - ketu/houses/__init__.py
  - ketu/houses/koch.py
  - ketu/houses/regiomontanus.py
  - ketu/houses/whole_sign.py
  - scripts/snapshot_reference_charts.py
  - tests/cli/test_houses_cmd.py
  - tests/cli/test_introspection.py
  - tests/cli/test_parser.py
  - tests/houses/conftest.py
  - tests/houses/test_dtype.py
  - tests/houses/test_equal.py
  - tests/houses/test_integration.py
  - tests/houses/test_oracle_smoke.py
  - tests/houses/test_polar_safety.py
  - tests/houses/test_regiomontanus.py
  - tests/houses/test_whole_sign.py
findings:
  critical: 0
  warning: 5
  info: 8
  total: 13
status: issues_found
---

# Phase 15 — Code Review Report (Sophie Chen)

**Reviewed :** 2026-05-09
**Depth :** standard
**Files Reviewed :** 23
**Status :** issues_found

## Résumé

Salut, c'est Sophie. J'ai passé Phase 15 au peigne fin — l'ajout de Whole Sign,
Equal et Regiomontanus, plus le bump U10→U16, plus l'extension du CLI et de
l'introspection. Globalement le code est propre, bien testé (snapshot oracle
multi-systèmes, deux niveaux de tolérance, polar safety couverts) et fidèle à
swisseph. Je note **0 BLOCKER** : le code est prêt à merger.

Cela dit, j'ai trouvé **5 WARNING** réels qui méritent d'être corrigés avant de
fermer la phase, et **8 INFO** qui sont des dettes de qualité sans urgence :

- Un test Whole Sign **buggé** (no-op silencieux) qui prétend couvrir le cas
  Pitfall 3 (ASC = 0° boundary) mais ne l'exerce jamais — sa condition ne peut
  pas être atteinte par construction (WR-01).
- Une **incohérence de seuil** entre `is_polar` (`>` strict avec marge
  `POLAR_EPS_TOL`) et le `polar_mask` interne de Koch/Regiomontanus (`>=` sans
  marge) — produit une bande d'1e-9° au bord du cercle polaire où les deux
  voient la latitude différemment (WR-02).
- `tests/houses/test_dtype.py` se présente comme "no swisseph dependency" mais
  est skippé en bloc parce que le `conftest.py` parent fait
  `pytest.importorskip("swisseph")` au niveau module (WR-03).
- `.gitignore` qui s'ignore lui-même + utilise un blocklist `/scripts/*` à
  whitelist explicite, fragile pour les futurs ajouts (WR-04).
- Duplication (DRY) du bloc closed-form ASC + polar swap entre `equal.py`,
  `whole_sign.py` et `porphyry.py` — 3 copies de la même logique (WR-05).

Les INFO ratchetent surtout sur la cohérence du registre (`cmd_list_aspect_sets`
itère sur des noms hardcodés au lieu de `_PRESET_DESCRIPTIONS.keys()`),
quelques variables computées-mais-inutilisées, des constantes mortes
(`MAX_ITER`/`TOL_DEG` dans `regiomontanus.py` et `koch.py`), et la couverture
de tests qui omet quelques branches (mid-lat doit rester Placidus sous
fallback, par exemple).

## Warnings

### WR-01 : Test Whole Sign sign-boundary est un no-op silencieux

**File :** `tests/houses/test_whole_sign.py:125-141`

**Issue :** Le test `test_whole_sign_asc_at_sign_boundary_yields_cusp_1_zero`
prétend couvrir Pitfall 3 (ASC ≈ 0°, frontière de signe) mais sa logique est
incohérente :

1. Il instancie `armc=0.0`, `lat=0.0`, `eps=23.4393` puis appelle séparément
   `compute_ascmc(2451545.0, 0.0, 0.0)` — l'ARMC de J2000 Greenwich vaut
   ~280°, **pas 0°**. L'`asc` lu n'est donc pas l'ASC qui correspond à
   `armc=0`, et le test introduit une incohérence entre les paramètres
   d'entrée (`armc=0`) et la valeur d'`asc` testée.
2. La condition `if asc % 30.0 < 0.01 or asc % 30.0 > 29.99` est rarement vraie
   pour l'ARMC réel de J2000 Greenwich — donc dans la quasi-totalité des
   exécutions le test **ne fait aucune assertion** et passe trivialement.
3. La variable locale `armc` (déclarée np.asarray(0.0)) est utilisée pour
   `whole_sign_cusps(armc, lat, eps)`, mais le `asc` vérifié vient d'un autre
   calcul — donc même si la condition était vraie, on comparerait des choux
   et des carottes.

Pitfall 3 n'est en fait pas couvert. Si quelqu'un casse le `floor(asc/30)*30`
pour produire un drift de -1° au cas où ASC = 0° exact, ce test ne le verra
pas.

**Fix :**
```python
def test_whole_sign_asc_at_sign_boundary_yields_cusp_1_zero() -> None:
    """At ASC near 0° exact (Aries 0°), cusps[0] = 0.0 — sign boundary case.

    Construit explicitement un (armc, lat, eps) tel que l'ASC tombe à
    0.0 ± 1e-6° (ou utilise un cas synthétique où on FORCE asc=0 par
    construction).
    """
    # Cherche un ARMC qui produit ASC=0 à lat=10° (sweep grossier puis fin).
    target_lat = 10.0
    eps = 23.4393
    eps_rad = np.deg2rad(eps)
    lat_rad = np.deg2rad(target_lat)
    # ASC=0 ⇔ atan2(cos(armc), -[sin(eps)tan(lat)+cos(eps)sin(armc)]) = 0
    # ⇔ cos(armc) = 0 et le dénominateur est positif.
    # Donc armc = 270° donne cos(armc) = 0 et sin(armc) = -1, dénominateur =
    # -[sin(eps)*tan(10°) - cos(eps)] > 0 → ASC = 0 exactement.
    armc = np.asarray(270.0, dtype=np.float64)
    cusps = whole_sign_cusps(
        armc, np.asarray(target_lat), np.asarray(eps),
    )
    # Indépendamment de la valeur exacte d'asc (qui doit être ~0 ou ~360),
    # cusps[0] DOIT être 0 (le floor de quelque chose proche de 0 ou
    # le floor de quelque chose proche de 360 = 360 % 360 = 0).
    assert abs(cusps[0]) < 1e-6 or abs(cusps[0] - 360.0) < 1e-6
```

Alternativement : `pytest.skip` proprement si la condition n'est pas remplie,
plutôt que passer silencieusement comme un test vert.

### WR-02 : Incohérence seuil polar — `is_polar` (`>` + marge) vs Koch/Regio (`>=` sans marge)

**File :** `ketu/houses/koch.py:96`, `ketu/houses/regiomontanus.py:118`,
`ketu/houses/porphyry.py:91-94`

**Issue :** Trois critères de bord polaire qui ne s'accordent pas exactement :

- `is_polar(lat, jd)` (porphyry.py:94) : `|lat| > polar_circle(jd) − POLAR_EPS_TOL`
  avec `POLAR_EPS_TOL = 1e-9` et `polar_circle = 90 − mean_obliquity(jd)`.
- `koch.py:96` : `polar_mask = np.abs(lat_b) >= (90.0 - eps_b)` (sans marge,
  comparison `>=`).
- `regiomontanus.py:118` : idem que Koch.

Conséquence : il existe une bande étroite de latitudes (largeur ~1e-9° à 0°
exactement à la frontière) où le comportement est mal défini :

| `|lat|` vs `polar_circle` | `is_polar` (api.py polar gate) | Koch/Regio NaN-out |
|---|---|---|
| `polar_circle - 1e-10` | False (under) | False (under) |
| **`polar_circle - 1e-12`** | **True** (under marge) | **False** (under) |
| `polar_circle` exactly | True (`>`) | True (`>=`) |
| `polar_circle + 1e-12` | True | True |

Dans la zone marquée en gras, `api.py` raise `HighLatitudeError` (parce que
`is_polar` retourne True via la marge), mais Koch/Regio renvoient des cusps
**finis** (non-NaN). Le user reçoit `HighLatitudeError` même si l'algorithme
aurait pu produire un résultat valide. Symétriquement, à `polar_circle`
exactement, Koch/Regio NaN-out (`>=`) mais `is_polar` ne les couvre que via
la marge `>` strict — les deux sont True dans ce cas, OK.

L'asymétrie dominante : **dans une bande de ~1e-9° immédiatement sous le
cercle polaire**, `api.py` raise alors que Koch/Regio aurait calculé
correctement. C'est observable mais pratiquement invisible (tolérance plus
fine que la précision de `mean_obliquity`).

Plus inquiétant : `is_polar` utilise `mean_obliquity(jd)` côté `api.py`,
tandis que Koch/Regio utilisent l'`eps` passé en paramètre par `compute_ascmc`
qui appelle aussi `mean_obliquity(jd_b)`. C'est cohérent **aujourd'hui**, mais
si on upgrade un jour `compute_ascmc` à `eps_true` (cf. test_integration.py
NON_POLAR_TOL_ARCMIN comment), le critère interne dérivera de `is_polar` —
nouveau bug latent.

**Fix :** Aligner les trois critères sur une seule source de vérité :

```python
# Option 1 (recommandée) : Koch/Regio appellent is_polar
from .porphyry import is_polar
# ...
polar_mask = np.abs(lat_b) > (90.0 - eps_b - POLAR_EPS_TOL)
```

Option 2 : Centraliser via une fonction `_polar_mask(lat, eps)` dans
`_ecliptic.py` pour que tous les systèmes (Koch, Regio, futurs) la consomment.

### WR-03 : `tests/houses/test_dtype.py` skippé inutilement sans swisseph

**File :** `tests/houses/conftest.py:59`, `tests/houses/test_dtype.py:1-10`

**Issue :** `tests/houses/conftest.py` exécute `pytest.importorskip("swisseph")`
au niveau module (ligne 59). Pytest applique cela à TOUS les fichiers du
sous-dossier `tests/houses/`, y compris `test_dtype.py` qui se proclame
explicitement "Pure structural assertions. No swisseph dependency, no oracle
access — these tests run without any optional deps installed." (lignes 3-4).

Conséquence : sur un environnement sans pyswisseph (`pip install ketu` sans
extras `[test]`), les tests structuraux `HOUSES_DTYPE` (8 tests dont la
ratchet U16 introduite par Phase 15-01) sont **silencieusement skippés**.
La ratchet de Phase 15 sur U16 ne protège rien dans cet environnement.

Pas un crash, mais une perte de couverture qui contredit le contrat documenté
du fichier — et la promesse "tests run without any optional deps installed".

**Fix :** Trois options dans l'ordre de préférence :

1. Déplacer `test_dtype.py` dans `tests/houses_no_swisseph/` (nouveau
   sous-dossier sans le importorskip global) ou directement dans `tests/`.
2. Refactor `conftest.py` pour mettre l'`importorskip` dans une `fixture`
   au lieu du niveau module — laisse les tests purement structuraux passer.
3. Ajouter en haut de `test_dtype.py` un skip-marker négatif qui re-active le
   test :

```python
# tests/houses/test_dtype.py
import pytest

# This file is structural-only — bypass the parent conftest's swisseph gate
# by NOT depending on any fixture that would trigger it.
pytestmark = pytest.mark.skipif(False, reason="")  # no-op marker
```
   …mais cela n'aide pas tant que le module-level `importorskip` du conftest
   tue la collection. Option 1 ou 2 est la vraie solution.

### WR-04 : `.gitignore` s'ignore lui-même + whitelist scripts/ fragile

**File :** `.gitignore:6-7,14`

**Issue :** Deux pratiques fragiles :

1. **Ligne 14** : `.gitignore` apparaît dans `.gitignore`. Comme le fichier est
   déjà tracké (`git ls-files .gitignore` confirme), cette entrée est sans
   effet : git continue de versionner le fichier. Mais elle peut **piéger**
   un futur contributeur :
   - S'il fait `git rm --cached .gitignore` puis `git add .` (workflow naïf),
     il s'attendra à voir `.gitignore` réintégré — il ne le sera pas, et
     cette absence sera silencieuse.
   - Une nouvelle copie clonée n'est pas affectée, mais le fichier est en
     état "ignored-but-tracked", qui prête à confusion lors des audits.

2. **Lignes 6-7** : `/scripts/*` puis `!/scripts/snapshot_reference_charts.py`
   est un pattern **deny-by-default avec whitelist explicite**. Phase 15
   ajoute `snapshot_reference_charts.py` (Plan 15-01), c'est cohérent
   aujourd'hui. Mais si demain un contributeur ajoute
   `scripts/regen_kala_fixtures.py`, il sera **silencieusement ignoré** par
   git — il ne sera pas commité, l'auteur ne s'en rendra pas compte avant
   qu'un autre dev clone le repo et observe l'absence.

**Fix :**

1. Retirer la ligne 14 (`.gitignore` dans `.gitignore`) — sans effet, et
   trompeuse.

2. Inverser la stratégie scripts : whitelist par défaut → blacklist explicite.
   Au lieu de :
   ```gitignore
   /scripts/*
   !/scripts/snapshot_reference_charts.py
   ```
   Utiliser :
   ```gitignore
   # Specific scripts to exclude (e.g., experiments, sandbox)
   /scripts/sandbox_*.py
   /scripts/experiment_*.py
   ```
   Les nouveaux scripts seront committés par défaut ; seuls ceux que l'auteur
   marque explicitement seront ignorés. Plus prévisible, plus future-proof.

### WR-05 : Duplication closed-form ASC + polar swap entre 3 modules

**File :** `ketu/houses/equal.py:74-90`, `ketu/houses/whole_sign.py:88-105`,
`ketu/houses/porphyry.py:139-162` (et partiel dans `koch.py:81-89`,
`regiomontanus.py:101-110`)

**Issue :** Le bloc closed-form de l'ASC et MC, plus le polar ASC swap
(`acmc_signed = ((asc - mc + 540) % 360) - 180; swap_mask = acmc_signed < 0;
asc = where(swap, asc+180, asc)`) est **dupliqué dans 3 modules** :

- `porphyry.py:139-162` (origine, swap AC→AC complet avec acmc utilisé après)
- `whole_sign.py:88-105` (swap utilisé pour cusp_1 = floor(asc/30)*30)
- `equal.py:74-90` (swap utilisé pour cusps = asc + 30k)

Plus deux variantes simplifiées **sans swap** :

- `koch.py:81-89` (sans swap — Koch utilise `_asc1` pour les cusps trisectés,
  pas l'ASC raw)
- `regiomontanus.py:101-110` (sans swap)

Conséquence : trois copies du même formule à maintenir. Si un bug est
découvert dans l'une (ex : un edge case sur le wrap modulo), il faut le fixer
dans 3 endroits — Sophie n'a aucune garantie que les fixes sont synchronisés.

Pourquoi WARNING et pas INFO : ce n'est pas du style ; c'est un **vector
d'incohérence numérique** au cœur du calcul d'ASC à haute latitude. Un futur
contributeur qui modifie porphyry sans toucher equal/whole_sign produit un
drift silencieux entre les systèmes au-dessus du cercle polaire.

**Fix :** Extraire la logique partagée dans `_ecliptic.py` :

```python
# ketu/houses/_ecliptic.py

def _asc_with_polar_swap(
    armc_rad: np.ndarray,
    lat_rad: np.ndarray,
    eps_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (asc, mc, acmc_signed) closed-form with polar ASC swap.

    Mirrors swisseph's case 'O'/'W'/'E' polar branch: when the closed-form
    asc emerges in the antipodal quadrant (acmc_signed < 0), swap by 180°.
    """
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad),
        np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
    swap_mask = acmc_signed < 0.0
    asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)
    acmc_signed = np.where(swap_mask, acmc_signed + 180.0, acmc_signed)
    return asc, mc, acmc_signed
```

Puis `equal.py`, `whole_sign.py` et `porphyry.py` consomment cette helper
unique. Bénéfice secondaire : cela réduit la surface de tests régression
(une seule fonction à pinner via algorithm tier au lieu de 3).

## Info

### IN-01 : `cmd_list_aspect_sets` itère noms hardcodés au lieu de `_PRESET_DESCRIPTIONS.keys()`

**File :** `ketu/cli/introspection.py:36`

**Issue :** Le test `test_every_registered_system_has_description` (test_introspection.py:52)
ratchet contre une dérive `_SYSTEM_DESCRIPTIONS` vs `SYSTEMS`. **Aucun équivalent
n'existe pour les aspect sets** : `cmd_list_aspect_sets` itère sur le tuple
hardcodé `("classical", "traditional", "extended", "all")` au lieu de
`_PRESET_DESCRIPTIONS.keys()` (introspection.py:36).

Si demain on ajoute un preset `"harmonic_gates"` dans `_PRESET_DESCRIPTIONS`
mais qu'on oublie de le rajouter au tuple itéré, il ne sera **jamais affiché**
par `--list-aspect-sets`. Aucun test ne le détectera (pas de ratchet
équivalent à HOU2-04).

**Fix :**
```python
for name in _PRESET_DESCRIPTIONS:
    # ...
```
Et ajouter un test miroir de `test_every_registered_system_has_description`
pour les aspect sets.

### IN-02 : `MAX_ITER` et `TOL_DEG` morts dans `koch.py` et `regiomontanus.py`

**File :** `ketu/houses/koch.py:39-42`, `ketu/houses/regiomontanus.py:52-55`

**Issue :** Les deux constantes sont déclarées comme module-level
"reserved for future iterative variants" mais ne sont **jamais utilisées**
dans aucun code path. Test `test_regiomontanus_constants_unchanged`
(test_regiomontanus.py:256-260) les pinne à 50/1e-7, mais ce test ratchete
un contrat **purement vide** : modifier la constante n'a aucun effet
fonctionnel.

C'est de la **dead code visible**. Le commentaire "API parity with Placidus
tests" laisse penser que les tests Placidus consomment ces constantes — vérif
faite, ce n'est pas le cas (Placidus a son propre `MAX_ITER` interne).

**Fix :** Soit les supprimer franchement (avec le test), soit les marquer
clairement comme TODO :

```python
# TODO(v1.3): wired into iterative Regiomontanus variant if/when added.
#             Until then, dead code — consider removing.
MAX_ITER: int = 50
TOL_DEG: float = 1e-7
```

### IN-03 : `desc` et `acmc_signed` calculés mais inutilisés dans equal.py / whole_sign.py

**File :** `ketu/houses/equal.py:88-90`, `ketu/houses/whole_sign.py:103-105`

**Issue :** Dans `equal.py:88-90` et `whole_sign.py:103-105`, le bloc :
```python
acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
swap_mask = acmc_signed < 0.0
asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)
```
calcule `acmc_signed` puis ne l'utilise que pour produire `swap_mask`. La
variable `acmc_signed` peut être inlinée dans la condition pour économiser
une variable :

```python
swap_mask = (((asc - mc + 540.0) % 360.0) - 180.0) < 0.0
asc = np.where(swap_mask, (asc + 180.0) % 360.0, asc)
```

Pour `whole_sign.py` spécifiquement, la variable `mc` est calculée
uniquement pour le swap puis jetée — un commentaire explicit le fait
(ligne 87 : "we discard MC since Whole Sign cusps 4/7/10 are sign-floor
opposites, not the astronomical IC/DESC/MC"), mais cela renforce le besoin
du fix WR-05 (extraction d'une helper).

**Fix :** Inliner `acmc_signed`, ou — mieux — appliquer le fix WR-05
(extraire `_asc_with_polar_swap`) qui résout INF-03 par construction.

### IN-04 : Test mid-lat-stays-Placidus manquant sous polar_fallback="porphyry"

**File :** `tests/houses/test_integration.py:151-165` 
(`test_calculate_houses_polar_porphyry_substitutes_for_polar_only`)

**Issue :** Le test vérifie que sous `polar_fallback="porphyry"` le résultat
n'a pas de NaN, mais il ne vérifie **pas** que l'élément non-polaire
(Paris J2000, lat=48.86°) garde bien des cusps **Placidus**, pas Porphyry. Si
un bug fait substituer Porphyry partout (mask broadcast cassé), le test passe
toujours.

**Fix :** Ajouter une assertion qui compare le mid-lat element à un
`calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")` direct :

```python
r_direct_mid = calculate_houses(2451545.0, 48.8566, 2.3522, system="placidus")
mid_cusps = np.asarray(r["cusps"])[0]
direct_cusps = np.asarray(r_direct_mid["cusps"])
deltas = np.abs(((mid_cusps - direct_cusps + 180.0) % 360.0) - 180.0)
assert deltas.max() < 1e-9, "non-polar element must remain Placidus, not Porphyry"
```

### IN-05 : Indentation align suspect dans introspection.py:38

**File :** `ketu/cli/introspection.py:38-40`

**Issue :**
```python
mask = resolve_aspect_set("extended" if name == "all" else name)
names = [n.decode() if isinstance(n, bytes) else str(n)
         for n in _CORE_ASPECTS["name"][mask]]
```
La continuation `for n in _CORE_ASPECTS["name"][mask]]` est alignée à 9 spaces
(`"         for"`) — pas conforme PEP-8 (devrait être à `[` opening +1, soit
plus profond). Lisible mais inhabituel.

**Fix :** Reformatter :
```python
names = [
    n.decode() if isinstance(n, bytes) else str(n)
    for n in _CORE_ASPECTS["name"][mask]
]
```

### IN-06 : Snapshot script importe swisseph en top-level — fail-fast obscur

**File :** `scripts/snapshot_reference_charts.py:40`

**Issue :** `import swisseph as swe` au niveau module fait fail-fast avec
`ModuleNotFoundError` si pyswisseph n'est pas installé. C'est intentionnel
(le script n'a aucun sens sans swisseph), mais le message d'erreur
résultant (`ModuleNotFoundError: No module named 'swisseph'`) ne guide pas
l'utilisateur vers la bonne action (`pip install -e ".[test]"`).

**Fix :** Wrap l'import dans un try/except au niveau `main()` :

```python
def main(argv: list[str] | None = None) -> int:
    try:
        import swisseph as swe  # noqa: F401
    except ImportError as exc:
        print(
            "ERROR: pyswisseph not installed. "
            "Run `pip install -e \".[test]\"` to install the AGPL test "
            f"dependency. ({exc})",
            file=sys.stderr,
        )
        return 1
    # ...
```

Note : ce script vit sous `scripts/` (séparation production/test), donc
l'import top-level n'introduit pas swisseph dans la wheel runtime. Pas un
bug de packaging, juste UX.

### IN-07 : `regiomontanus.py:111-112` — `ic` et `desc` calculés mais inutilisés

**File :** `ketu/houses/regiomontanus.py:111-112`, `koch.py:90-91`

**Issue :** Dans `regiomontanus.py:111-112` :
```python
ic = (mc + 180.0) % 360.0
desc = (asc + 180.0) % 360.0
```
puis utilisés dans `np.stack` ligne 142-146 (`asc, cusp_2, cusp_3, ic, ...,
desc, ...`). OK, utilisés. **Ignore cette finding** — fausse alerte de mon
scan initial. Je laisse l'entrée pour traçabilité (j'ai vérifié et invalidé).

**Fix :** N/A — code correct. Item retiré de l'analyse.

### IN-08 : `parser.py` — choices=`sorted(_HOUSE_SYSTEMS.keys())` figé à build_parser() time

**File :** `ketu/cli/parser.py:135`

**Issue :** `build_parser()` capture `sorted(_HOUSE_SYSTEMS.keys())` au moment
où `build_parser` est appelée. Si un nouveau système est enregistré
**après** que `build_parser` ait été instanciée (ex : import différé,
plugin tiers), il **ne sera pas** dans `choices`. Pas un bug aujourd'hui (les
6 systèmes sont importés au niveau `ketu/houses/__init__.py`), mais c'est
une limitation cachée du registre.

Ratcheté indirectement par `test_houses_system_choices_enforced` :
l'invariance "tout nom registré est accepté" n'est pas testée explicitement
pour les 6 systèmes — `test_v12_systems_accepted` (test_houses_cmd.py:71-80)
le fait pour {whole_sign, equal, regiomontanus} mais pas pour
{placidus, koch, porphyry}.

**Fix :** Faible priorité. Si un jour le projet supporte des plugins
runtime, `build_parser()` devrait re-snapshotter `SYSTEMS.keys()` à chaque
appel (ce qu'il fait déjà — la closure est sur `_HOUSE_SYSTEMS` import-time,
mais la valeur retournée par `sorted(_HOUSE_SYSTEMS.keys())` capture
l'état au moment de l'appel à `build_parser`, pas plus tôt). Donc OK.

Note : Sophie verdict — INFO conservé pour visibilité, mais pas
actionnable jusqu'à ce qu'un cas réel surgisse.

---

## Couverture des risques (notés haut)

J'ai vérifié mais **pas trouvé** :

- ✓ Pas de hardcoded secret, pas de eval/exec, pas de SQL/command injection
  (le projet est pur calcul).
- ✓ Pas de chemin de fichier construit par concaténation user-input (le snapshot
  utilise `Path(__file__)`).
- ✓ Pas de mutable default arg dans les signatures publiques.
- ✓ Pas de bare `except:`.
- ✓ Pas de `eval()` ni `exec()`.
- ✓ Le polar swap est bien fait BEFORE le sign-floor dans whole_sign.py
  (Pitfall 1 du research §11) — ratcheté par les tests.
- ✓ Les pole heights de regiomontanus.py utilisent bien `atan(tan(geo_lat)/2)`
  et non `geo_lat/2` (Pitfall 4) — ratcheté par
  `test_regiomontanus_no_silent_nan_at_mid_latitudes`.
- ✓ La largeur U16 du field `system` est testée pour `regiomontanus` (13 chars)
  — `test_dtype_string_field_capacity` (modulo WR-03).
- ✓ Le snapshot oracle JSON est régénérable de façon déterministe (sort_keys,
  indent=2, JSON canonique).
- ✓ `regiomontanus_cusps` et `koch_cusps` propagent NaN au-dessus du cercle
  polaire — ratcheté par 4 tests dont le polar_safety global.
- ✓ `calculate_houses` retourne `system_lower` même sous fallback porphyry —
  contrat explicite documenté + testé par
  `test_calculate_houses_system_field_preserved_under_fallback`.

## Recommandations finales

Avant de fermer Phase 15 :

1. **Fixer WR-01 et WR-03** (10 min chacun) — défauts qualité pure.
2. **Discuter WR-02** — soit on aligne les seuils maintenant (15 min), soit
   on documente explicitement la zone d'incohérence comme acceptée (5 min).
3. **WR-05 (refactor DRY)** — j'aimerais le faire, mais c'est techniquement
   un Phase 16 (remaniement post-Phase 15). Acceptable de le porter en dette
   si on crée un ticket immédiatement.
4. **WR-04** : à reformuler dans une PR dédiée — ne pas inclure dans Phase 15.

INFO-01 à INFO-08 : à treater au cas par cas, aucun ne bloque.

Bon merge,
**Sophie Chen**

---

_Reviewed : 2026-05-09_
_Reviewer : Sophie Chen (gsd-code-reviewer)_
_Depth : standard_
