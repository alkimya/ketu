# Phase 15 : Additional House Systems — Research

**Recherche :** 2026-05-09
**Domaine :** Géométrie sphérique des house systems (Whole Sign, Equal, Regiomontanus) sur stack pure-NumPy 2.x ; extension du registre `SYSTEMS` v1.1 sans rupture additive ; oracle Swiss Ephemeris (pyswisseph 2.10.03) test-only.
**Confiance globale :** HIGH — les trois formules sont closed-form, le registre est conçu pour ça (HOU-02), et pyswisseph supporte W/E/R en oracle pour les 10 reference charts.

---

## Résumé exécutif

Phase 15 est de **l'extension par registre pur**, sans modification de code existant. Les trois nouveaux systèmes sont mathématiquement triviaux comparés à Placidus (zéro itération, formules closed-form courtes) :

- **Whole Sign** : `cusp[k] = floor(asc/30)*30 + 30*k` — alignement sur le signe de l'ASC. Polar-safe par construction (n'utilise que ASC, qui se calcule fermé via `compute_ascmc` à toute latitude < 90°).
- **Equal** : `cusp[k] = (asc + 30*k) mod 360` — espacement régulier depuis l'ASC. Polar-safe par construction.
- **Regiomontanus** : `fh1 = atan(tan(lat)/2)`, `fh2 = atan(tan(lat)·cos(30°))`, puis quatre appels à `Asc1(armc + offset_k, fh_k, sin_eps, cos_eps)` (mêmes plumbing que Koch) — pas d'itération, mais singularité aux pôles `|lat| ≥ 90 - eps`. Le code C swisseph (`swehouse.c` case `'R'`) sert de référence canonique.

**Recommandation principale :** mimer **strictement** la structure des modules `koch.py` (closed-form, helper `_asc1`, NaN à la singularité polaire) et `porphyry.py` (closed-form, polar-safe). Ne pas réinventer `_asc1` — le sortir dans `_ecliptic.py` (déjà module interne) ou le dupliquer verbatim entre `koch.py` et `regiomontanus.py` (le fichier C swisseph fait pareil, c'est une fonction de 5 lignes).

**Plan recommandé :** 4 plans atomiques en 2 vagues — voir §10. Vague 1 : oracle-snapshot extension (le snapshot JSON committé doit gagner les 3 nouveaux systèmes pour les 10 reference charts). Vague 2 (parallèle) : Whole Sign + Equal (un plan), Regiomontanus (un plan), CLI/integration/intro (un plan).

---

## <user_constraints>

## User Constraints (CONTEXT.md absent)

Aucun fichier `15-CONTEXT.md` n'existe au moment de cette recherche. Les contraintes proviennent directement de :

### Decisions verrouillées (REQUIREMENTS.md, ROADMAP.md, CLAUDE.md)

- **HOU2-01** : Whole Sign — chaque maison = un signe, démarrant **au signe de l'ASC** (sign-floor, pas ASC-anchored equal) ; polar-safe ; enregistré dans `SYSTEMS`.
- **HOU2-02** : Equal — cusps espacés de 30° **depuis l'ASC** (pas depuis le MC) ; polar-safe ; enregistré dans `SYSTEMS`.
- **HOU2-03** : Regiomontanus — division équateur céleste projetée via prime vertical ; enregistré dans `SYSTEMS`. (Singularité polaire connue — voir §6.)
- **HOU2-04** : `--list-house-systems` CLI doit retourner exactement `placidus, koch, porphyry, whole_sign, equal, regiomontanus` (6 systèmes triés).
- **HOU2-05** : Chaque nouveau système validé contre Swiss Ephemeris sur les 10 reference charts existants (gate v1.1) ; max ASC delta documenté.
- **Non-breaking minor strict** (v1.2) : aucun défaut changé sur les APIs existantes ; aucun export retiré ; aucun champ `HOUSES_DTYPE` modifié.
- **Pure-NumPy contract** : pas de scipy, pas de swisseph **runtime**. pyswisseph reste test-only (AGPL).
- **Vectorisable** : pas de boucle Python sur `S` (broadcast shape) dans le hot path. Les 4 cusps Regiomontanus peuvent être stack-és en une seule passe vectorisée.
- **UTC-only** : `jd` toujours Julian Date UT.
- **Coverage gates** : ≥95 % sur le code nouveau (`whole_sign.py`, `equal.py`, `regiomontanus.py`) ; ≥85 % par module ; project ≥90 %.
- **Doc gates** (Phase 13 OPS-01, OPS-02) : `numpydoc validate` clean ; `interrogate ≥95 %`. **MUST pass dès le départ** ; pas de carve-out pour le code Phase 15.
- **Mypy `--strict`** clean sur les nouveaux modules (cf. `pyproject.toml` `[[tool.mypy.overrides]]` n'a pas d'exception pour `ketu.houses.*`).
- **Persona Sophie** (français + tutoiement) dans tous les artefacts conversationnels (PLAN.md, SUMMARY.md, RESEARCH.md narratifs). Code et docstrings restent en anglais (précédent v1.1/Phase 14).

### Claude's Discretion

- **Naming des modules** : `whole_sign.py` vs `wholesign.py` vs combinaisons à plat dans `_simple.py`. Recommandation : un fichier par système (mimétisme parfait avec `koch.py`, `porphyry.py`, `placidus.py`). Les trois fichiers seront triviaux (~50 lignes chacun pour Whole Sign/Equal, ~80 lignes pour Regiomontanus).
- **Polar singularity behavior** pour Regiomontanus : NaN-propagation comme Koch (pour que `polar_fallback="porphyry"` route correctement), ou laisser swisseph-style "swap MC/IC at polar latitudes" ? Recommandation : **NaN à `|lat| ≥ 90 - eps`** (cohérence avec Koch ; le swap swisseph-style serait une digression vs HOU-06). Plan 15-RESEARCH §6.
- **Découpage des plans** : combiner Whole Sign et Equal dans un seul plan (formules quasi-identiques, deux fichiers triviaux) ou séparer ? Recommandation : **un seul plan** "two-trivial-systems", parce que les deux partagent l'invariant `cusp[k+1] - cusp[k] == 30°` et seraient testés en parallèle.
- **Snapshot regeneration** : étendre `tests/houses/fixtures/reference_charts.json` avec 3 nouveaux blocs (whole_sign, equal, regiomontanus) pour les 10 charts existants. Le script de régénération n'existe pas encore — voir §11 (Wave 0).
- **CLI choices argparse** : `choices=[...]` actuellement hardcoded à `["placidus", "koch", "porphyry"]` dans `parser.py:135`. Le passer dynamique (`choices=sorted(SYSTEMS.keys())`) ou hardcoder les 6 ? Recommandation : **dynamique via `sorted(SYSTEMS.keys())`** — cohérent avec l'esprit de la registry et fait passer HOU2-04 sans toucher au parser quand on ajoutera Campanus/Topocentric en v1.3.

### Deferred Ideas (OUT OF SCOPE Phase 15)

- **Campanus, Topocentric (Polich/Page), Alcabitius** — registry doit les supporter mais ils ne sont **pas livrés** v1.2 (REQUIREMENTS.md « Out of Scope » ligne 94). N'écris pas de code ni de tests pour eux.
- **Sidereal Whole Sign / ayanamsha** — Phase 15 = tropical only. Le code C swisseph case `'W'` a une branche sidereal (`if (ihs == 'W')` après calcul ASC sidéral) ; on ne l'implémente pas.
- **MC-anchored Equal (système 'D' swisseph)** — HOU2-02 est explicitement **ASC-anchored** ("cusps espacés de 30° depuis l'ASC"). Pas de variante.
- **Polar fallback custom pour Regiomontanus** — on suit le contrat HOU-06 v1.1 : NaN propagation → caller route vers `porphyry` ou `HighLatitudeError`. Pas de logique polaire spéciale dans `regiomontanus.py`.
- **JSON output pour `--list-house-systems`** — research §Open Question 4 du Phase 11 reportait à v1.2, mais pas dans le scope HOU2-04 (qui demande seulement les 6 noms listés).

</user_constraints>

---

## <phase_requirements>

## Phase Requirements

| ID | Description (REQUIREMENTS.md) | Research Support |
|----|-------------------------------|------------------|
| HOU2-01 | Whole Sign houses — chaque maison = un signe, démarrant au signe de l'ASC ; polar-safe ; enregistré dans `SYSTEMS` | §3 (formule), §6 (polar safety), §4 (registry pattern) |
| HOU2-02 | Equal houses — cusps espacés de 30° depuis l'ASC ; polar-safe ; enregistré dans `SYSTEMS` | §3 (formule), §6 (polar safety), §4 (registry pattern) |
| HOU2-03 | Regiomontanus houses — division équateur céleste projetée via prime vertical ; enregistré dans `SYSTEMS` | §3 (formule canonique swisseph), §6 (singularité polaire), §4 (registry pattern) |
| HOU2-04 | `--list-house-systems` retourne `placidus, koch, porphyry, whole_sign, equal, regiomontanus` (5+ systèmes) | §7 (CLI integration), §8 (parser changes) |
| HOU2-05 | Chaque nouveau système validé contre Swiss Ephemeris sur les 10 reference charts existants ; max ASC delta documenté | §5 (oracle), §11 (snapshot regeneration), §9 (validation architecture) |

</phase_requirements>

---

## Architectural Responsibility Map

| Capability | Tier primaire | Tier secondaire | Rationale |
|---|---|---|---|
| Algorithme Whole Sign | `ketu/houses/whole_sign.py` | — | Pattern v1.1 : un fichier par système (`placidus.py`, `koch.py`, `porphyry.py`). |
| Algorithme Equal | `ketu/houses/equal.py` | — | Idem ; Whole Sign et Equal sont des systèmes distincts dans l'API publique même si la formule diffère d'un seul `floor`. |
| Algorithme Regiomontanus | `ketu/houses/regiomontanus.py` | — | Idem ; reuse du helper `_asc1` (à factoriser ou dupliquer — voir §3.3). |
| Helper `_asc1` (RA → ecliptic via pole height) | `ketu/houses/_ecliptic.py` (refactor) ou duplication dans `regiomontanus.py` | `koch.py` (déjà privé) | Recommandation : extraire `_asc1` de `koch.py` vers `_ecliptic.py` car Phase 15 en a besoin. Le rendre `_asc1(x, lat, sin_eps, cos_eps)` public au sein de `ketu.houses` (underscore-internal). |
| Registry registration | `@register("whole_sign")`, `@register("equal")`, `@register("regiomontanus")` dans chaque module | `__init__.py` trigger imports (déjà le pattern) | Pattern HOU-02 ; cf. `houses/__init__.py:41-43`. Trois nouvelles lignes `from . import whole_sign  # noqa: F401` etc. |
| HOUSES_DTYPE consumption | inchangé | — | Le dtype existant (jd, lat, lon, system, cusps[12], asc, mc, armc, vertex) accommode parfaitement les 3 nouveaux systèmes — `system` est `U10` donc `"whole_sign"` (10 chars) tient pile. |
| CLI parser `--system` choices | `ketu/cli/parser.py:135` | — | Passer de `["placidus", "koch", "porphyry"]` hardcoded à `sorted(SYSTEMS.keys())` dynamique. Simple changement d'1 ligne. |
| `--list-house-systems` description | `ketu/cli/introspection.py:_SYSTEM_DESCRIPTIONS` | — | Ajouter 3 entrées au dict `_SYSTEM_DESCRIPTIONS`. Cosmétique. |
| Oracle test fixtures | `tests/houses/conftest.py:SYSTEM_BYTES` (étendre) | `tests/houses/fixtures/reference_charts.json` (régénérer) | Ajouter `"whole_sign": b"W", "equal": b"E", "regiomontanus": b"R"` à `SYSTEM_BYTES`. Le snapshot JSON doit être régénéré pour inclure les 3 systèmes × 10 charts = 30 nouveaux blocs. |
| Tests algorithm-tier (bit-exact vs `swe_oracle_armc`) | `tests/houses/test_whole_sign.py`, `test_equal.py`, `test_regiomontanus.py` | conftest.py existant | Pattern Koch/Porphyry : test parametré par les 8 non-polar reference charts ; tolerance `ALGO_TOL_DEG = 1e-6` (machine precision). |
| Tests end-to-end (snapshot + drift Reykjavik) | mêmes fichiers de test | — | Pattern `test_koch.py:99-128` : tolerance 1 arcmin sur les 7 charts non-polaires "tight", avec exception pinned pour Reykjavik si Regiomontanus amplifie eps drift. |
| Tests polar safety | `tests/houses/test_polar_safety.py` (étendre) | — | Whole Sign/Equal : assert no-NaN à lat=70°/80°/89°. Regiomontanus : assert NaN à `|lat| ≥ 90 - eps_mean(jd)` (pattern Koch). |

---

## 1. Quel est l'état de la registry et du dispatch v1.1 ?

### `SYSTEMS` registry — entièrement extensible

`ketu/houses/registry.py:34-41` définit la signature du contrat :

```python
HouseSystemFn = Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]
# (armc, lat, eps) -> cusps shape (..., 12)

SYSTEMS: dict[str, HouseSystemFn] = {}

@register(name)  # decorator inserts into SYSTEMS[name.lower()]
```

Trois choses à savoir :

1. **Signature uniforme** : `(armc, lat, eps) -> cusps[..., 12]`. C'est le **seul** contrat à respecter. Whole Sign et Equal ne consomment pas `eps` (ils dérivent leurs cusps de `asc` qu'on recompute closed-form depuis `armc`+`lat`+`eps`) — mais ils doivent **accepter** le paramètre par signature.
2. **`@register("name")` est case-insensitive** (lowercase normalisé) — donc `"whole_sign"`, `"WHOLE_SIGN"`, `"Whole_Sign"` pointent tous vers la même entrée.
3. **Trigger imports** : `houses/__init__.py:41-43` importe explicitement `placidus`, `koch`, `porphyry` pour déclencher leurs décorateurs. **Le piège classique** est d'oublier d'ajouter les 3 nouveaux trigger imports (cf. Pitfall 2 ci-dessous).

### Cusp ordering pinné

Tous les systèmes v1.1 retournent `[asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]` avec `c1=asc`, `c4=ic`, `c7=desc`, `c10=mc` (cf. `porphyry.py:188-192`, `koch.py:168-172`, `placidus.py:351-364`). **Whole Sign brise cette convention** : `c1` est le sign-floor de l'ASC, **pas l'ASC lui-même**. Idem pour `c4` (= `c1 + 90°`, **pas l'IC**), `c7` (`c1 + 180°`), `c10` (`c1 + 270°`). C'est le comportement attendu et **conforme à swisseph** :

```
swisseph J2000 Paris (ASC=26.77° Aries, MC=281.78°):
  Whole Sign cusps = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
  → c10 = 270° (NOT MC=281.78°)
```

**Implication** : les tests existants comme `test_koch_cusps_5_6_8_9_are_opposites_of_11_12_2_3` (pinning `cusp[i+6] = cusp[i] + 180°`) **fonctionnent toujours** pour Whole Sign et Equal (les opposites tiennent) **mais PAS** le test "c10 == mc" qui est implicite dans `placidus_cusps`/`koch_cusps`. Le test à NE PAS écrire pour Whole Sign : aucune assertion `cusps[9] == mc`.

### Polar fallback contract — `is_polar` + `NaN`-propagation

`api.py:124-151` route `polar_fallback`. Le contrat existant :
- Si `system_lower == "porphyry"` → skip polar gate (Porphyry est lui-même le fallback).
- Sinon, `polar_mask = is_polar(lat_b, jd_b)` et :
  - `polar_fallback="raise"` → `HighLatitudeError`.
  - `polar_fallback="porphyry"` → substituer Porphyry cusps via `np.where(mask_b, cusps_porphyry, cusps)`.

Pour Phase 15, **Whole Sign et Equal ne déclenchent pas le polar gate** parce qu'ils sont mathematiquement définis à toute latitude `< 90°` (cf. tests swisseph §pré-recherche : aucune erreur à lat=89°). **Donc** `calculate_houses(jd=J2000, lat=80, lon=0, system="whole_sign")` doit **succéder** sans `HighLatitudeError`, comme Porphyry.

**Comment ?** Trois options :
1. **Étendre `api.py:126`** : `system_lower != "porphyry"` → `system_lower not in {"porphyry", "whole_sign", "equal"}`. Liste hardcodée.
2. **Trait dans la registry** : ajouter un attribut `is_polar_safe: bool` aux fonctions enregistrées (changement de signature).
3. **NaN-free promise par construction** : ne rien changer à `api.py`, faire en sorte que `whole_sign_cusps` et `equal_cusps` ne produisent **jamais** de NaN. Comme `polar_fallback="raise"` lève **avant** le dispatch (parce que `is_polar` est `True`), ce serait un faux positif.

**Recommandation : option 1 (hardcode)**. Plus simple, pas de changement de signature, cohérent avec le hardcode existant pour Porphyry. Étendre la liste à 3 systèmes ajoute 1 SLOC. La signature est une charge légère ; un attribut sur les fns est une sur-ingénierie pour 3 systèmes polar-safe sur 6.

**Justification additionnelle** : avec option 1, `calculate_houses(80, 0, system="whole_sign")` ne lève pas `HighLatitudeError` même quand `polar_fallback="raise"`, ce qui est le comportement attendu — Whole Sign EST polar-safe.

---

## 2. `HOUSES_DTYPE` accommode-t-il les 3 nouveaux systèmes ?

Oui, sans modification.

`ketu/houses/core.py:35-45` définit :

```python
HOUSES_DTYPE = np.dtype([
    ("jd",      "f8"),
    ("lat",     "f8"),
    ("lon",     "f8"),
    ("system",  "U10"),    # ← capacité 10 chars
    ("cusps",   "f8", (12,)),
    ("asc",     "f8"),
    ("mc",      "f8"),
    ("armc",    "f8"),
    ("vertex",  "f8"),
])
```

Vérification capacité `U10` :
- `"whole_sign"` = 10 chars ✓ (juste pile — **ne pas renommer en `"whole-sign"` ou `"wholesign"`** ; les 10 chars sont budgétés).
- `"equal"` = 5 chars ✓
- `"regiomontanus"` = 13 chars **❌ DÉPASSE LA CAPACITÉ U10**.

⚠️ **Problème détecté** : le nom `"regiomontanus"` (13 chars) ne tient pas dans `U10`. Trois options :

1. **Tronquer en `"regio"` (5 chars)** — break la lisibilité.
2. **Renommer en `"regiomont"` (9 chars)** — abréviation acceptable mais non-canonique.
3. **Étendre `HOUSES_DTYPE['system']` à `U16` ou `U20`**.

L'option 3 est la seule **non-breaking**. Mais elle modifie un dtype publié en v1.1 — la capacité `U10` est documentée dans la docstring. Attention :
- `np.dtype([..., ("system", "U16"), ...])` est **techniquement** un dtype différent. Du code qui fait `assert arr.dtype == HOUSES_DTYPE` casserait si HOUSES_DTYPE change. Mais l'écriture `arr["system"] = "regiomontanus"` produit toujours une string ; la lecture est string-comparable. Le caster dtype-équivalence est rare en pratique.
- **Test à vérifier** : `tests/houses/test_dtype.py` pin-t-il la capacité U10 ? À grep avant de proposer le changement.

[VERIFIED: ketu/houses/core.py:35-45 + ketu/houses/__init__.py docstring]

**Recommandation** : passer à `U13` ou `U16` (le strict-minimum pour `"regiomontanus"`) comme **changement additif** (la valeur stockée reste comparée par contenu, pas par dtype). Le planner devra :

1. Grep `HOUSES_DTYPE` dans tests/ pour identifier les tests qui assert dtype-equality (`arr.dtype == HOUSES_DTYPE`).
2. Si tests présents, ils continueront de passer (même pattern). Si un test compare `arr.dtype.itemsize`, il faut le mettre à jour.
3. Documenter dans CHANGELOG : "HOUSES_DTYPE['system'] capacity grown from U10 → U16 to accommodate longer system names. Existing data remains valid; consumers comparing dtype equality may need to use field-by-field comparison."

⚠️ **Cette extension de dtype n'est PAS un breaking change selon les standards numpy** — un `arr` de `U10` se cast librement vers `U16`, et vice-versa pour les valeurs ≤ 10 chars. Mais c'est **une décision à acter explicitement** dans le PLAN (probablement Plan 15-01 "registry + dtype").

[ASSUMED] : cette analyse suppose qu'aucun consumer downstream (Kala) n'a verrouillé `HOUSES_DTYPE['system'].itemsize == 10`. À confirmer en discuss-phase si la consultation Kala est faisable.

**Alternative pragmatique** : si la modification de dtype est jugée trop risquée, utiliser `"regio"` (5 chars) comme nom canonique et le documenter comme alias officiel pour Regiomontanus. Trade-off : utilisateur écrira `system="regio"` qui est moins lisible. Mais pas de touch sur HOUSES_DTYPE.

---

## 3. Formules canoniques — references swisseph C source

Source primaire : [swehouse.c sur github aloistr/swisseph](https://github.com/aloistr/swisseph/blob/master/swehouse.c) (fork mainstream du Swiss Ephemeris pyswisseph 2.10.03 wrap). Cross-checked via `swe.houses_ex(jd, lat, lon, hsys)` au moment de cette recherche (2026-05-09, J2000 Paris).

### 3.1 Whole Sign — `case 'W'`

```c
acmc = swe_difdeg2n(hsp->ac, hsp->mc);
if (acmc < 0) {
  hsp->ac = swe_degnorm(hsp->ac + 180);
  hsp->cusp[1] = hsp->ac;
}
hsp->cusp[1] = hsp->ac - fmod(hsp->ac, 30);
for (i = 2; i <= 12; i++)
  hsp->cusp[i] = swe_degnorm(hsp->cusp[1] + (i-1) * 30);
```

[CITED: swehouse.c case 'W']

**Traduction NumPy vectorisée** :

```python
@register("whole_sign")
def whole_sign_cusps(armc, lat, eps):
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    # ASC and MC closed-form (same as ascmc.compute_ascmc).
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad), np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad) + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0
    # Polar ASC swap (same as porphyry.py:159-161): if ASC behind MC, flip ASC by 180°.
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
    asc = np.where(acmc_signed < 0.0, (asc + 180.0) % 360.0, asc)
    # Sign-floor cusp 1.
    cusp_1 = asc - (asc % 30.0)  # in [0, 360); aligned to nearest sign boundary below
    # cusps 2..12 = cusp_1 + 30*k mod 360
    offsets = np.arange(12, dtype=np.float64) * 30.0
    cusps = (cusp_1[..., np.newaxis] + offsets) % 360.0  # shape (*S, 12)
    return cusps
```

⚠️ **Attention au polar ASC swap** : swisseph fait le swap **avant** le sign-floor (voir l'ordre dans le C). Le faire dans l'autre ordre donne des cusps off de 180° à lat=70°+. Validé empiriquement : à lat=70° N, J2000, lon=0, `ASC ≈ 316.39°` post-swap = `300°` sign-floor → cusps `[300, 330, 0, 30, ...]`. Sans swap, on aurait obtenu `[60, 90, 120, ...]` (off par 240°).

### 3.2 Equal — `case 'E'` (et `case 'A'`, qui est un alias dans swisseph)

```c
acmc = swe_difdeg2n(hsp->ac, hsp->mc);
if (acmc < 0) {
  hsp->ac = swe_degnorm(hsp->ac + 180);
  hsp->cusp[1] = hsp->ac;
}
for (i = 2; i <= 12; i++) {
  hsp->cusp[i] = swe_degnorm(hsp->cusp[1] + (i-1) * 30);
}
```

[CITED: swehouse.c case 'E', case 'A']

**Identique à Whole Sign sauf pas de `fmod` sign-floor**. La factorisation possible est tentante mais découplez : un fichier par système, pas de helper partagé entre Whole Sign et Equal — les futures variantes (sidereal Whole Sign, Vehlow Equal `'V'`) se développeraient mieux sur des bases séparées.

```python
@register("equal")
def equal_cusps(armc, lat, eps):
    # ... même calcul ASC + polar swap ...
    cusp_1 = asc  # NOT sign-floored
    offsets = np.arange(12, dtype=np.float64) * 30.0
    cusps = (cusp_1[..., np.newaxis] + offsets) % 360.0
    return cusps
```

### 3.3 Regiomontanus — `case 'R'`

```c
fh1 = atand(tanfi * 0.5);
fh2 = atand(tanfi * cosd(30));
hsp->cusp[11] = Asc1(30 + th, fh1, sine, cose);
hsp->cusp[12] = Asc1(60 + th, fh2, sine, cose);
hsp->cusp[2]  = Asc1(120 + th, fh2, sine, cose);
hsp->cusp[3]  = Asc1(150 + th, fh1, sine, cose);
```

Où `tanfi = tan(lat)`, `th = ARMC` (deg), `sine = sin(eps)`, `cose = cos(eps)`. Cusps 1, 4, 7, 10 = ASC, IC, DESC, MC closed-form. Cusps 5, 6, 8, 9 = opposites de 11, 12, 2, 3.

[CITED: swehouse.c case 'R']

**`Asc1` est déjà implémenté** dans `ketu/houses/koch.py:44-89` :

```python
def _asc1(x, lat, sin_eps, cos_eps):
    x_rad = np.deg2rad(x % 360.0)
    lat_rad = np.deg2rad(lat)
    num = np.cos(x_rad - np.pi/2)
    den = -(np.tan(lat_rad) * sin_eps + cos_eps * np.sin(x_rad - np.pi/2))
    lam = np.arctan2(num, den)
    return np.rad2deg(lam) % 360.0
```

**MAIS** : pour Regiomontanus, `lat` doit être remplacé par les **pole heights** `fh1`, `fh2` (et **PAS** la latitude géographique). C'est ça le sens de "projection via prime vertical" : on évalue `Asc1` non pas à `lat`, mais à des pseudo-latitudes calculées à partir de `lat` :

```python
@register("regiomontanus")
def regiomontanus_cusps(armc, lat, eps):
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_b = armc_b.astype(np.float64)
    lat_b = lat_b.astype(np.float64)
    eps_b = eps_b.astype(np.float64)
    
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)
    sin_eps = np.sin(eps_rad)
    cos_eps = np.cos(eps_rad)
    tanfi = np.tan(lat_rad)
    cos30 = np.cos(np.deg2rad(30.0))
    
    # Pole heights for the 1/3 and 2/3 great-circle subdivisions.
    fh1 = np.rad2deg(np.arctan(tanfi * 0.5))     # for cusps 11, 3
    fh2 = np.rad2deg(np.arctan(tanfi * cos30))   # for cusps 12, 2
    
    # ASC, MC closed-form (same as compute_ascmc).
    armc_rad = np.deg2rad(armc_b)
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad), np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad) + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0
    ic = (mc + 180.0) % 360.0
    desc = (asc + 180.0) % 360.0
    
    # Iterated cusps via _asc1 with pole-height substituted for latitude.
    cusp_11 = _asc1(armc_b + 30.0,  fh1, sin_eps, cos_eps)
    cusp_12 = _asc1(armc_b + 60.0,  fh2, sin_eps, cos_eps)
    cusp_2  = _asc1(armc_b + 120.0, fh2, sin_eps, cos_eps)
    cusp_3  = _asc1(armc_b + 150.0, fh1, sin_eps, cos_eps)
    
    # Cusps 5/6/8/9 = opposites by construction.
    cusp_5 = (cusp_11 + 180.0) % 360.0
    cusp_6 = (cusp_12 + 180.0) % 360.0
    cusp_8 = (cusp_2  + 180.0) % 360.0
    cusp_9 = (cusp_3  + 180.0) % 360.0
    
    # Polar singularity (same as Koch).
    polar_mask = np.abs(lat_b) >= (90.0 - eps_b)
    
    cusps = np.stack([
        asc, cusp_2, cusp_3, ic,
        cusp_5, cusp_6, desc, cusp_8,
        cusp_9, mc, cusp_11, cusp_12,
    ], axis=-1)
    
    if polar_mask.any():
        mask_b = np.broadcast_to(polar_mask[..., np.newaxis], cusps.shape)
        cusps = np.where(mask_b, np.nan, cusps)
    
    return cusps
```

⚠️ **Note importante** : `_asc1` est actuellement défini dans `koch.py` (`koch.py:44-89` ; nom Python `_asc1`). **Décision de design** : où le mettre ?

- **Option A** : dupliquer dans `regiomontanus.py`. Inconvénient : DRY violation, mais le fichier C swisseph fait pareil entre fonctions.
- **Option B** : extraire vers `ketu/houses/_ecliptic.py` (déjà module interne). Avantage : DRY, cohérence avec `ra_to_lambda`/`lambda_to_ra`. **Recommandation : OPTION B**, plan 15-02 "Regiomontanus + factorisation _asc1".

Si OPTION B retenue : modifier `koch.py` pour `from ._ecliptic import _asc1`, et **conserver** `MAX_ITER`/`TOL_DEG` constants dans `koch.py` (tests `test_koch_iter_constants_match_research` les pinnent).

---

## 4. Comment ajouter un système au registre — pattern HOU-02

`ketu/houses/__init__.py:41-43` :

```python
from . import placidus  # noqa: F401  registers 'placidus' in SYSTEMS
from . import koch       # noqa: F401  registers 'koch' in SYSTEMS
from . import porphyry   # noqa: F401  registers 'porphyry' in SYSTEMS
```

Pour Phase 15, ajouter **3 lignes** :

```python
from . import whole_sign   # noqa: F401  registers 'whole_sign'
from . import equal        # noqa: F401  registers 'equal'
from . import regiomontanus # noqa: F401  registers 'regiomontanus'
```

**ET** un test pin dans `test_integration.py:57-62` (le pattern existe déjà pour les 3 systèmes v1.1) :

```python
def test_systems_has_all_six_systems_at_import_time():
    for name in ("placidus", "koch", "porphyry",
                 "whole_sign", "equal", "regiomontanus"):
        assert name in SYSTEMS
```

---

## 5. Comment l'oracle Swiss Ephemeris valide les nouveaux systèmes

### 5.1 Étendre `SYSTEM_BYTES`

`tests/houses/conftest.py:77-81` actuellement :

```python
SYSTEM_BYTES: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyry": b"O",
}
```

Ajouter :

```python
    "whole_sign": b"W",
    "equal": b"E",
    "regiomontanus": b"R",
}
```

[VERIFIED: tests at runtime 2026-05-09 confirmed swe_houses_ex accepts b'W'/b'E'/b'R' on swisseph 2.10.03]

### 5.2 Régénérer `tests/houses/fixtures/reference_charts.json`

Le snapshot JSON committé contient actuellement les 10 charts × 3 systèmes (placidus, koch, porphyry) — voir le fichier (~80+ lines per chart). **Phase 15 doit l'étendre** pour inclure les 3 nouveaux systèmes pour les mêmes 10 charts → 10 × 6 = 60 blocs total.

⚠️ **Le script de régénération n'existe pas encore**. Le commentaire dans `conftest.py:248-250` mentionne `scripts/snapshot_reference_charts.py` mais ce fichier n'est **pas dans le repo**. **Wave 0** doit créer ce script (réutiliser le pattern `swe_oracle()` du conftest).

Format actuel du snapshot (vérifié sur `1900_NewYork`) :

```json
{
  "charts": {
    "1900_NewYork": {
      "meta": {"jd": ..., "label": ..., "lat": ..., "lon": ...},
      "systems": {
        "placidus": {"armc": ..., "asc": ..., "cusps": [...], "mc": ..., "vertex": ...},
        "koch": {...},
        "porphyry": {...}
      }
    }
  }
}
```

Pour les charts polaires (`J2000_Lat70_North`, `J2000_Lat80_North`) :
- `placidus`/`koch` actuellement stockent `{"polar": true, "error": "..."}` (pas de cusps).
- `whole_sign`/`equal`/`regiomontanus` à lat=70° et 80° : **swisseph les calcule sans erreur** (vérifié empiriquement). Donc les blocs auront des cusps réels.

### 5.3 Tolérances vs swisseph

Pattern Koch (`tests/houses/test_koch.py:30-46`) :
- **Algorithm tier** (`swe_oracle_armc` avec ARMC fourni) : `ALGO_TOL_DEG = 1e-6` (machine precision sur les algorithmes purs).
- **End-to-end tier** (snapshot match avec compute_ascmc full chain) : `<1 arcmin` sur 7 charts non-polaires "tight" + tolerance étendue à `~3 arcmin` sur Reykjavik (cause : eps_mean vs eps_true drift, amplifié par cos(lat) à 64°N).

**Predictions pour Phase 15** :

| Système | Algorithm tier | Reykjavik end-to-end | Justification |
|---|---|---|---|
| Whole Sign | bit-exact (1e-6°) | ~51″ (= ASC drift seul) | sign-floor n'amplifie rien ; cusps = floor(ASC) + multiples de 30° ; le floor "absorbe" ±15° de drift ASC. Risque réel : ASC drift > 30° ferait sauter d'un signe entier ; seul à craindre vers les pôles. |
| Equal | bit-exact (1e-6°) | ~51″ (= ASC drift seul) | offset rigide ; toute drift ASC se transmet 1:1 sur les 12 cusps. |
| Regiomontanus | bit-exact (1e-6°) | inconnue [ASSUMED ~2-3' à Reykjavik] | reuse `_asc1` qui est utilisé par Koch. Comportement identique à Koch sur eps_mean vs eps_true. À empiriser avant pin. |

[ASSUMED] : Reykjavik Regiomontanus drift est estimé par analogie avec Koch. À mesurer en Plan 15-02 et pinned avant validation. Si > 3 arcmin, accepter une `REGIO_REYKJAVIK_TOL = 3 * ARCMIN_DEG` ou re-tester avec eps_true.

### 5.4 Comportement polaire des nouveaux systèmes (vérifié empiriquement)

Mesures à `J2000.0` (`jd=2451545.0`), `lon=0`, `eps_mean ≈ 23.44°`, `armc ≈ 280.46°` :

| lat | system | swisseph cusps[0] | swisseph mc | comportement |
|---|---|---|---|---|
| 70° | whole_sign | 300.0 | 279.61 | OK, mc swap normal (mc = 279.61 < 360-eps) |
| 70° | equal | 316.39 | 279.61 | OK, asc-anchored |
| 70° | regiomontanus | 316.39 | **99.61** (swap) | swisseph swap MC↔IC à `\|lat\| > 90-eps`. c10=99.61 (=swap MC). |
| 80° | whole_sign | 330.0 | 99.61 | OK |
| 80° | equal | 352.36 | 99.61 | OK |
| 80° | regiomontanus | 352.36 | 99.61 | NaN dans notre impl (Koch-pattern) ; swisseph retourne valeurs après swap. |
| 89° | whole_sign | 330.0 | 99.61 | OK |
| 89° | equal | 359.52 | 99.61 | OK |
| 89° | regiomontanus | 359.52 | 99.61 | NaN dans notre impl. |

**Décision de design (cf. §6)** : pour Regiomontanus, **propager NaN** à `|lat| ≥ 90 - eps_mean(jd)`. Ne PAS répliquer le swap swisseph-style — ce serait diverger du pattern HOU-06 v1.1 (Koch fait NaN, le caller route via `polar_fallback`). L'oracle test pour Regiomontanus à lat=70°/80° devrait :

- algorithm tier : skip (l'algorithme retourne NaN, l'oracle retourne valeurs swap).
- end-to-end : `polar_fallback="porphyry"` substitution → vérifier que les cusps polar sont `==` Porphyry direct call.

---

## 6. Polar safety — comportement de chaque système

| Système | Polar-safe ? | Comportement à `\|lat\| ≥ 90 - eps` | Justification |
|---|---|---|---|
| Whole Sign | ✅ | cusps finis ; sign-floor de ASC fonctionne à toute lat < 90° | ASC closed-form depuis `armc, lat, eps` ; tan(lat) → ∞ uniquement à `lat == 90°` (jamais atteint). |
| Equal | ✅ | cusps finis ; ASC-offset fonctionne à toute lat < 90° | idem. |
| Regiomontanus | ❌ | `tan(lat)` dans `fh1 = atan(tan(lat)/2)` se sature ; cusps deviennent inutilisables | Singularité comme Koch (qui fait `cos(lat)` divisor). Recommandation : **NaN-propagate à `\|lat\| ≥ 90 - eps`** (pattern Koch `koch.py:140-143`). |

**Implication pour `api.py`** : la liste hardcodée des systèmes polar-safe passe de `{"porphyry"}` à `{"porphyry", "whole_sign", "equal"}` (cf. §1, option 1).

**Test pinning à écrire** :

```python
# tests/houses/test_polar_safety.py — extension
@pytest.mark.parametrize("system", ["whole_sign", "equal"])
def test_simple_systems_finite_at_polar_lat(system):
    """Whole Sign and Equal must not NaN at lat=80° — they are polar-safe by construction."""
    for lat in (70.0, 80.0, 89.0):
        ascmc = compute_ascmc(2451545.0, lat, 0.0)
        cusps = SYSTEMS[system](
            np.asarray(ascmc["armc"]),
            np.asarray(lat),
            np.asarray(ascmc["eps"]),
        )
        assert not np.isnan(cusps).any(), f"{system} NaN at lat={lat}°"

def test_regiomontanus_yields_nan_above_polar_circle():
    """Regiomontanus NaN-propagates beyond polar circle — caller routes via polar_fallback."""
    jd = 2451545.0
    lat = float(polar_circle(jd)) + 1.0
    ascmc = compute_ascmc(jd, lat, 0.0)
    cusps = regiomontanus_cusps(
        np.asarray(ascmc["armc"]),
        np.asarray(lat),
        np.asarray(ascmc["eps"]),
    )
    assert np.isnan(cusps).any()
```

Et dans `test_integration.py`, le test `test_calculate_houses_polar_default_raise_for_koch` doit être étendu pour `regiomontanus`. Whole Sign et Equal au contraire ne doivent **pas** lever — ils succèdent comme Porphyry direct.

---

## 7. CLI integration — qu'est-ce qui doit changer

Trois fichiers touchés, tous changements minimes :

### 7.1 `ketu/cli/parser.py:135` — choices argparse

Actuellement :

```python
p_houses.add_argument(
    "--system",
    choices=["placidus", "koch", "porphyry"],   # hardcoded
    default="placidus",
    ...
)
```

**Recommandation** : passer en dynamique pour suivre la registry :

```python
from ketu.houses import SYSTEMS as _HOUSE_SYSTEMS
...
p_houses.add_argument(
    "--system",
    choices=sorted(_HOUSE_SYSTEMS.keys()),
    default="placidus",
    ...
)
```

⚠️ **Caveat** : argparse `choices` est évalué au build time du parser. Si la registry n'est pas peuplée au moment où `build_parser()` tourne, `choices` sera incomplet. Mais `from ketu.houses import SYSTEMS` déclenche les trigger imports → registry peuplée à l'import. C'est OK.

⚠️ **Caveat 2** : un test existant (`test_houses_cmd.py:53-59`) **assert que `--system regiomontanus` est rejeté avec exit code 2**. Ce test est **incompatible avec Phase 15** et **doit être supprimé/inversé**. C'est cassé en v1.1 mais devient accepting v1.2 — c'est l'intention, pas un bug.

### 7.2 `ketu/cli/introspection.py:22-26` — descriptions

Étendre `_SYSTEM_DESCRIPTIONS` avec 3 entrées :

```python
_SYSTEM_DESCRIPTIONS = {
    "placidus": "...",
    "koch": "...",
    "porphyry": "...",
    "whole_sign": "Whole Sign — chaque maison = un signe ; cusp 1 au début du signe de l'ASC ; polar-safe (v1.2)",
    "equal": "Equal — cusps espacés de 30° depuis l'ASC ; polar-safe (v1.2)",
    "regiomontanus": "Regiomontanus — division de l'équateur céleste projetée via prime vertical (v1.2)",
}
```

L'ordre d'output est `sorted(SYSTEMS.keys())` → `equal, koch, placidus, porphyry, regiomontanus, whole_sign`. C'est l'ordre alphabétique, pas l'ordre de REQUIREMENTS HOU2-04. À vérifier en discuss-phase si l'ordre comptait.

### 7.3 Aide help-text top-level

`parser.py:54` mentionne explicitement les 3 systèmes v1.1 dans le help-text de `--list-house-systems`. Mettre à jour pour refléter les 6.

---

## 8. État de l'art — pyswisseph 2.10.03 confirmation

Vérifié à la session de recherche (2026-05-09) :

```python
import swisseph as swe  # version 2.10.03
swe.houses_ex(2451545.0, 48.8566, 2.3522, b'W')  # OK
swe.houses_ex(2451545.0, 48.8566, 2.3522, b'E')  # OK
swe.houses_ex(2451545.0, 48.8566, 2.3522, b'R')  # OK
```

[VERIFIED: pyswisseph runtime 2026-05-09]

Pas de breaking change attendu sur les codes hsys avant pyswisseph 3.x (calendrier inconnu, mais codes hsys sont gravés dans le manuel Astrodienst de 1997).

[CITED: https://deepwiki.com/aloistr/swisseph/4.1-house-systems pour la liste complète des codes hsys]

---

## 9. Validation Architecture (Nyquist gates)

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest 8.x (`pyproject.toml [tool.pytest.ini_options]`) |
| Quick run command (per task) | `pytest tests/houses/test_whole_sign.py tests/houses/test_equal.py tests/houses/test_regiomontanus.py -x` |
| Full suite command (per wave merge) | `pytest tests/ --cov=ketu.houses --cov-fail-under=95` |
| Phase gate | `pytest tests/ --cov=ketu --cov-report=term-missing` + numpydoc validate + interrogate |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists ? |
|---|---|---|---|---|
| HOU2-01 | `whole_sign` enregistré et computable | unit + algorithm-tier | `pytest tests/houses/test_whole_sign.py::test_registered tests/houses/test_whole_sign.py::test_algorithm_matches_oracle_armc -x` | ❌ Wave 0 |
| HOU2-02 | `equal` enregistré et computable | unit + algorithm-tier | `pytest tests/houses/test_equal.py::test_registered tests/houses/test_equal.py::test_algorithm_matches_oracle_armc -x` | ❌ Wave 0 |
| HOU2-03 | `regiomontanus` enregistré et computable | unit + algorithm-tier | `pytest tests/houses/test_regiomontanus.py::test_registered tests/houses/test_regiomontanus.py::test_algorithm_matches_oracle_armc -x` | ❌ Wave 0 |
| HOU2-04 | `--list-house-systems` retourne les 6 noms | CLI integration | `pytest tests/cli/test_introspection.py::TestListHouseSystems -x` (existant ; étendre) | ✅ existant à étendre |
| HOU2-05 | snapshot match sur 10 reference charts × 3 nouveaux systèmes | end-to-end snapshot | `pytest tests/houses/test_oracle_smoke.py::test_loaded_reference_snapshot_matches_oracle -x` (existant ; auto-étendu si snapshot regen inclut 3 systèmes) | ✅ existant à étendre |

### Sampling rate

- **Per task commit** : `pytest tests/houses/ -x -v`
- **Per wave merge** : `pytest tests/ --cov=ketu.houses --cov-fail-under=95`
- **Phase gate** : full suite green + `numpydoc validate ketu/houses/` + `interrogate ketu/houses/ -f 95`

### Wave 0 Gaps

- [ ] `tests/houses/test_whole_sign.py` — couvre HOU2-01 (registry, formule, polar safety, vectorisation).
- [ ] `tests/houses/test_equal.py` — couvre HOU2-02 (mêmes catégories).
- [ ] `tests/houses/test_regiomontanus.py` — couvre HOU2-03 (registry, formule, **polar NaN**, vectorisation).
- [ ] `scripts/snapshot_reference_charts.py` — script de régénération du JSON snapshot (n'existe pas en v1.1 — était promis dans `conftest.py:249` mais jamais committé). Utilise `swe_oracle(jd, lat, lon, system)` × `reference_charts` × 6 systèmes.
- [ ] Régénérer `tests/houses/fixtures/reference_charts.json` avec 6 systèmes × 10 charts.
- [ ] Étendre `SYSTEM_BYTES` dans `tests/houses/conftest.py:77-81`.
- [ ] **Aucune install supplémentaire** — pytest, numpy, pyswisseph (test-only) déjà dans `[project.optional-dependencies].test` (v1.0).

### Sampling strategy pour le Swiss Ephemeris oracle

Les 10 reference charts existants couvrent :
- **Équateur** (lat=0°) — degenerate case ASC formula.
- **Mid-latitudes nord** (Greenwich 51.5°, Paris 48.86°, NY 40.7°, Tokyo 35.7°).
- **Hémisphère sud** (Sydney -33.9°, Buenos Aires -34.6°).
- **Time boundaries** (1900, J2000, 2050).
- **Pre-polar** (Reykjavik 64.1°, juste sous le polar circle).
- **Polaire** (lat=70°, lat=80°) — pour Whole Sign/Equal cusps réels ; pour Regiomontanus → NaN propagation contract.

**Cas couvertes par les 10 charts pour Phase 15** :
- Wraparound 0°/360° (`J2000_Sydney` ASC ≈ Aries late degrees, `J2000_BuenosAires` ARMC ≈ 0°). Pour Whole Sign : ASC=29.99° Pisces → cusp 1 = 0° Pisces, cusps modulo correctement.
- Polar singularité (lat=70/80) : NaN contract pour Regiomontanus, finite contract pour Whole Sign/Equal.

⚠️ **Cas potentiellement non couvert** : ASC = 0.0° exact (sign boundary). Pour Whole Sign, `floor(0/30) * 30 = 0` ; pour Equal, ASC=0 → cusp_1=0. Pas de bug attendu mais **un test pinned** pour `floor(asc % 30) == 0` à la frontière de signe est prudent. Voir Pitfall 3 ci-dessous.

---

## 10. Recommandation de découpage en plans

4 plans atomiques, exécutables en 2 vagues :

### Vague 1 (séquentielle — fondation)

| # | Plan | Scope | Couverture REQ |
|---|---|---|---|
| 1 | **`15-01-oracle-snapshot-regeneration.md`** | Crée `scripts/snapshot_reference_charts.py` (fonction `regenerate(charts, systems, output_path)` qui appelle `swe_oracle()` pour chaque combinaison et écrit le JSON dans le format existant). Étendre `SYSTEM_BYTES` à 6 entrées. Régénérer `tests/houses/fixtures/reference_charts.json` avec les 60 blocs (10 × 6). Pin par `test_loaded_reference_snapshot_matches_oracle` qui passe automatiquement. **Optionnel** : extraire `_asc1` de `koch.py` vers `_ecliptic.py` (refactor préparatoire pour Plan 3). | Préparation pour HOU2-05 |

### Vague 2 (3 plans parallèles)

| # | Plan | Scope | Couverture REQ |
|---|---|---|---|
| 2 | **`15-02-whole-sign-and-equal.md`** | Crée `ketu/houses/whole_sign.py` (`@register("whole_sign")` ; ~50 lignes) ET `ketu/houses/equal.py` (`@register("equal")` ; ~45 lignes). Trigger imports dans `__init__.py`. Étendre la liste polar-safe dans `api.py:126`. Tests : `test_whole_sign.py` + `test_equal.py` (algorithm-tier vs swe_oracle_armc bit-exact ; end-to-end snapshot ≤1 arcmin sur 8 charts non-polaires ; polar safety lat=70°/80°/89° no-NaN ; sign-floor invariant pour Whole Sign ; constant-step invariant pour Equal). | HOU2-01, HOU2-02 |
| 3 | **`15-03-regiomontanus.md`** | Crée `ketu/houses/regiomontanus.py` (`@register("regiomontanus")` ; ~80 lignes ; reuse `_asc1` factorisé en Plan 1 OU dupliqué). Trigger import dans `__init__.py`. Tests : `test_regiomontanus.py` (algorithm-tier vs swe_oracle_armc bit-exact 1e-6° ; end-to-end snapshot tolerance < 1 arcmin sur 7 charts "tight" + Reykjavik avec tolerance pinned empirique ; polar NaN-propagation ; vectorisation ; integration avec polar_fallback="porphyry"). | HOU2-03 |
| 4 | **`15-04-cli-and-integration.md`** | Modifier `ketu/cli/parser.py:135` (`choices=sorted(SYSTEMS.keys())` dynamique). Étendre `ketu/cli/introspection.py:_SYSTEM_DESCRIPTIONS` avec 3 entrées. Mettre à jour le help-text de `--list-house-systems`. Tests : `tests/cli/test_introspection.py::TestListHouseSystems::test_lists_registered_systems` étendu pour 6 noms ; `tests/cli/test_houses_cmd.py::TestHousesCmdFlags::test_invalid_system_rejected` **inversé** pour valider `regiomontanus` accepté ; ajouter `test_six_systems_match_python_api` parametré. **Doc gates** : `numpydoc validate ketu/houses/` clean ; `interrogate ketu/houses/ -f 95` ≥95%. **Coverage** : `pytest tests/houses/ --cov=ketu.houses --cov-fail-under=95`. **HOUSES_DTYPE['system']** : si U10 trop court pour `"regiomontanus"`, étendre à U16 dans `core.py` + UPDATING.md note. | HOU2-04, HOU2-05 (validation finale) |

### Justification du découpage

- **Plan 1 isolé** : la régénération du snapshot conditionne tout le reste — Plans 2 et 3 ne peuvent pas tester end-to-end sans le JSON à jour. Sortir aussi `_asc1` factor en même temps évite que Plan 3 attende sur Plan 2 si on choisissait `_asc1` dans `whole_sign.py` (qui n'en a pas besoin).
- **Plans 2 et 3 parallèles** : Whole Sign et Equal sont algorithmiquement triviaux et indépendants de Regiomontanus. Plan 3 (Regiomontanus) est plus complexe (closed-form mais singularité polaire à gérer). Découpés, ils peuvent être développés et review-és en parallèle.
- **Plan 4 final** : CLI + integration + doc gates est le finishing touch. Le sortir évite que chaque plan d'implémentation ait à se distraire avec le parser et les introspection descriptions, pourtant cosmétiques.

### Variantes acceptables

- **Fusion Plan 2 + 3** : "trois systèmes en un seul plan" si le planner juge que 3 fichiers de ~50-80 lignes ne méritent pas deux plans séparés. Trade-off : un plan plus large, un test step plus lourd. Recommandation : garder séparés parce que Regiomontanus a un risque non-trivial (le pole-height substitution est facile à mal coder ; mieux qu'il ait son propre review).
- **Sortir un plan dédié pour `_asc1` extraction** : sur-ingénierie — c'est un refactor de 5 lignes à incorporer dans Plan 1.
- **Plan séparé pour HOUSES_DTYPE U10 → U16** : si la décision est jugée ambiguë et nécessite discussion utilisateur, le sortir comme Plan 0 ou comme branch de Plan 1. Ne pas le mettre dans Plan 4 (qui est censé être finition CLI).

---

## 11. Pitfalls communs identifiés

### Pitfall 1 — Polar ASC swap ordre dans Whole Sign

**Erreur** : appliquer le sign-floor (`asc - asc % 30`) **avant** le polar ASC swap (`asc → (asc + 180) % 360 if acmc < 0`).
**Pourquoi ça arrive** : le sign-floor est conceptuellement le "pas final" du Whole Sign ; on est tenté de le mettre en sortie de la fonction.
**Comment l'éviter** : suivre l'ordre du code C swisseph (`swehouse.c` case `'W'` lignes ~1100) : (1) compute ASC, (2) compute MC, (3) compute `acmc`, (4) **swap si négatif**, (5) sign-floor cusp[1], (6) cusp[2..12] = cusp[1] + 30k.
**Signe précurseur** : test à lat=70° N J2000 retourne cusps `[60, 90, 120, ...]` au lieu de `[300, 330, 0, ...]`.

### Pitfall 2 — Oubli du trigger import dans `__init__.py`

**Erreur** : créer `ketu/houses/whole_sign.py` avec `@register("whole_sign")` mais oublier `from . import whole_sign` dans `__init__.py`.
**Pourquoi ça arrive** : le décorateur `@register` est silencieux ; aucun message d'erreur si le module n'est pas importé.
**Comment l'éviter** : pattern documenté dans `houses/__init__.py:37-43` ("Trigger registration of built-in systems by importing the modules"). Le test `test_systems_has_all_six_systems_at_import_time` failera fast.
**Signe précurseur** : `calculate_houses(jd, lat, lon, system="whole_sign")` lève `ValueError("unknown house system 'whole_sign'")`.

### Pitfall 3 — ASC=0° exact à la frontière de signe (Whole Sign)

**Erreur** : assumer que `asc % 30 == 0` est rare et ne pas tester. À ASC=0.0°, `cusp_1 = 0 - 0 = 0` (Aries 0°). À ASC=30.0°, `cusp_1 = 30 - 0 = 30` (Taurus 0°). C'est correct mathématiquement, mais un test pinné évite les regressions.
**Pourquoi ça arrive** : test param avec ASC = 0.001° puis ASC = 29.999° passes ; ASC = 0.0° exact n'est jamais testé.
**Comment l'éviter** : pinner `assert whole_sign_cusps(armc=270, lat=0, eps=23.44)["cusps"][0] == 0.0` (un cas où ASC est calculable à 0°).
**Signe précurseur** : aucun bug visible, mais le test reste un trap-for-future-refactor.

### Pitfall 4 — Regiomontanus pole-height substitution

**Erreur** : appeler `_asc1(armc + 30, lat, sin_eps, cos_eps)` au lieu de `_asc1(armc + 30, fh1, sin_eps, cos_eps)` pour cusp 11. Le `lat` ici doit être la **pole height**, pas la latitude géographique.
**Pourquoi ça arrive** : `_asc1(x, lat, ...)` a `lat` comme paramètre nommé (cf. `koch.py:44`) ; intuitivement on passe la latitude géographique.
**Comment l'éviter** : nommer la variable de boucle `pole_height` (pas `lat`) et documenter dans la docstring ("`lat` here is the great-circle pole height, not the geographic latitude — for Regiomontanus this is `atan(tan(geo_lat) * X)`").
**Signe précurseur** : algorithm-tier test échoue avec drift uniforme ~10° sur tous les cusps non-trivial.

### Pitfall 5 — `_asc1` extraction casse Koch tests

**Erreur** : déplacer `_asc1` de `koch.py` vers `_ecliptic.py` mais oublier de mettre à jour `koch.py:_asc1` callers (qui sont locaux, donc 4 sites dans `koch.py` lignes 157-160).
**Pourquoi ça arrive** : refactor mécanique copy-paste ; on déplace la définition mais pas l'import.
**Comment l'éviter** : `from ._ecliptic import _asc1` au top de `koch.py`. Le test `test_koch_algorithm_matches_oracle_armc_at_machine_precision` détectera l'erreur (NameError).
**Signe précurseur** : `pytest tests/houses/test_koch.py` fait NameError dès l'import.

### Pitfall 6 — Snapshot regen oublie 1 ou 2 systèmes

**Erreur** : régénérer le snapshot avec uniquement les 3 nouveaux systèmes, écrasant les 3 anciens.
**Pourquoi ça arrive** : le script de régénération a une boucle `for system in NEW_SYSTEMS` au lieu de `for system in ALL_SYSTEMS`.
**Comment l'éviter** : itérer sur **tous** les noms (placidus + koch + porphyry + whole_sign + equal + regiomontanus). Le test `test_loaded_reference_snapshot_matches_oracle` (test_oracle_smoke.py:71) failera si un système est manquant.
**Signe précurseur** : `test_oracle_smoke.py::test_loaded_reference_snapshot_matches_oracle` échoue avec `KeyError` sur un système manquant.

### Pitfall 7 — `test_invalid_system_rejected` reste bloquant

**Erreur** : le test `tests/cli/test_houses_cmd.py:53-59` assert que `--system regiomontanus` est **rejeté** (legacy v1.1). Phase 15 le rend valide. Si on oublie d'inverser ce test, le passage de `parser.choices` à `sorted(SYSTEMS.keys())` casse le test.
**Pourquoi ça arrive** : le test décrit un comportement d'avant-Phase-15 ; oublier qu'il existe est facile.
**Comment l'éviter** : grep `regiomontanus` dans `tests/` AVANT de toucher `parser.py`. Inverser le test : `--system regiomontanus` doit être **accepté** (rc==0). Choisir un autre nom invalide pour le test rejet (`--system nonexistent_xyz`).
**Signe précurseur** : `pytest tests/cli/test_houses_cmd.py::TestHousesCmdFlags::test_invalid_system_rejected` échoue après changement de `parser.py`.

---

## 12. Architecture — diagramme de flux

```
                          calculate_houses(jd, lat, lon, system, polar_fallback)
                                          │
                                          ▼
                                  get_system(system)            (raises ValueError if unknown)
                                          │
                                          ▼
                                  compute_ascmc(jd, lat, lon)   (closed-form via arctan2)
                                          │
                                          │  → armc, eps, asc, mc, vertex
                                          ▼
                          ┌──────────────────────────────────┐
                          │  Polar gate (api.py:124-137)     │
                          │  is_polar(lat, jd) ?              │
                          │  YES + system NOT IN              │
                          │  {"porphyry","whole_sign","equal"}│
                          │    → raise / fallback             │
                          │  YES + system in polar-safe set   │
                          │    → SKIP polar gate              │
                          │  NO → normal path                 │
                          └──────────────────────────────────┘
                                          │
                                          ▼
                              sys_fn(armc, lat, eps)            (registry dispatch)
                                          │
              ┌────────────────────┬──────┴─────────┬─────────────────────┬──────────────────┐
              │                    │                │                     │                  │
              ▼                    ▼                ▼                     ▼                  ▼
       placidus_cusps       koch_cusps      porphyry_cusps        NEW: whole_sign_cusps    regiomontanus_cusps
       (iterated)           (closed-form    (closed-form          (closed-form ASC          (closed-form,
                            ad3 trisection)  trisection)           + sign-floor)            pole-height
                                                                                            + _asc1)
                                                                  ▼
                                                             NEW: equal_cusps
                                                             (closed-form ASC + 30k offset)
                                          │
                                          ▼
                          cusps shape (..., 12)
                                          │
                                          ▼
                        Polar fallback (api.py:146-151)
                        polar_fallback="porphyry" + any_polar
                          → np.where(mask, porphyry, cusps)
                                          │
                                          ▼
                          HOUSES_DTYPE structured array
```

---

## 13. Phase Constraints (from CLAUDE.md + cross-cutting v1.2)

Le planner **DOIT** vérifier que chaque plan honore :

- **Persona Sophie Chen** : français + tutoiement dans tous les artefacts conversationnels (PLAN.md narratifs, SUMMARY.md). Code et docstrings restent en anglais (précédent v1.1, Phase 14).
- **Standalone** : `ketu` ne dépend ni de Kala ni de MarketStream. (HOUSES_DTYPE consumé par Kala via positional-indexing — toute extension U10→U16 doit être notifiée Kala-side, mais sans modifier le code Ketu pour cela.)
- **Venv** : `venv/`, pas `.venv/`.
- **NumPy first** : structured array `HOUSES_DTYPE` reste source de vérité ; pas de dataclass, pas de dict de scalaires.
- **Non-breaking minor strict (v1.2)** : Phase 15 est **purement additive**. Aucune fonction existante modifiée dans son contrat ; aucun export retiré ; l'ajout de 3 systèmes au registry et 3 entrées dans `_SYSTEM_DESCRIPTIONS` sont stricts ajouts. **Caveat** : extension HOUSES_DTYPE U10→U16 si nécessaire est techniquement non-breaking côté NumPy (cast automatique) mais à documenter.
- **Pure-NumPy contract** : zéro nouvelle dépendance runtime. `pyswisseph` reste test-only AGPL.
- **Vectorisation** : pas de boucle Python sur le shape `S` dans le hot path. Les 3 nouveaux systèmes peuvent stack-er leurs cusps en une seule opération (cf. snippets §3).
- **UTC-only** : `jd` est Julian Date UT (cf. docstrings v1.1).
- **Mypy `--strict`** clean sur les nouveaux modules. `pyproject.toml` `[[tool.mypy.overrides]]` n'a pas d'exception pour `ketu.houses.*`. Les nouveaux modules suivent le pattern (no `Any`, type hints partout, `from __future__ import annotations`).
- **Doc gates depuis Phase 13** : `interrogate ≥95 %` + `numpydoc validate` doivent rester verts. Phase 15 ajoute du code couvert dès le départ — pas de carve-out.
- **Coverage gates** : ≥95 % sur les nouveaux modules (`whole_sign.py`, `equal.py`, `regiomontanus.py`) ; ≥85 % par module ; project ≥90 %.
- **AGPL boundary** : runtime imports de `ketu/houses/` ne doivent **pas** introduire `swisseph`. Tests-only (`test_no_runtime_swisseph_import` dans `test_integration.py:214` continue de passer).

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | HOUSES_DTYPE['system'] capacity (U10) doit être étendu à U16 pour `"regiomontanus"` (13 chars) | §2 | Si pas étendu : silent truncation à `"regiomonta"` ; sera détecté par `test_calculate_houses_meta_fields_populated` qui assert exact match — donc échec fast. Risk LOW. |
| A2 | Reykjavik Regiomontanus drift est ~2-3 arcmin (analogie Koch) | §5.3 | À mesurer en Plan 15-03 ; si > 3' acceptons une tolerance pinned plus large. Pas de blocker, mais l'estimation peut casser le `<1 arcmin` gate générique du `test_calculate_houses_all_3_systems_match_oracle` qui devient `test_..._all_6_systems_...`. |
| A3 | Aucun consumer downstream (Kala, autre) ne hardcode `HOUSES_DTYPE['system'].itemsize == 10` | §2 | Si Kala le fait, l'extension U10→U16 casserait Kala. À confirmer avec discuss-phase OU choisir l'alternative `system="regio"` (5 chars) qui ne touche pas le dtype. |
| A4 | `scripts/snapshot_reference_charts.py` n'existe pas — référence dans `conftest.py:248-250` est aspirationnelle | §11 Wave 0 | Vérifié par `find . -name "snapshot*"` (résultat vide). Wave 0 doit créer ce script. Risk LOW (la création est triviale). |
| A5 | pyswisseph 2.10.03 W/E/R hsys codes restent stables jusqu'à Phase 15 livraison | §8 | swisseph 2.10 est stable depuis 2023 ; pas d'évidence de breaking change. Risk MINIMAL. |
| A6 | Polar ASC swap (cf. porphyry.py:159-161) est nécessaire dans whole_sign et equal aussi | §3.1 | Vérifié par lecture du source C swisseph (`acmc < 0` → ASC swap). Sans ce swap, lat=70° N donnerait des cusps 180° off. Risk LOW (validable rapidement par snapshot match). |

---

## Open Questions

1. **Renommage `regiomontanus` → `regio` ?**
   - **Ce qu'on sait** : "regiomontanus" est 13 chars > U10 capacity de HOUSES_DTYPE['system'].
   - **Ce qui est unclear** : Kala ou autre consumer hardcode-t-il une comparaison de dtype-itemsize ?
   - **Recommandation** : poser la question en discuss-phase. Si Kala ne vérifie pas, étendre dtype à U16 (option propre) ; sinon utiliser `"regio"` comme alias canonique.

2. **Ordre des systèmes dans `--list-house-systems` output** :
   - **Ce qu'on sait** : actuellement `sorted(SYSTEMS.keys())` → ordre alphabétique. Avec 6 systèmes : `equal, koch, placidus, porphyry, regiomontanus, whole_sign`.
   - **Ce qui est unclear** : HOU2-04 demande "placidus, koch, porphyry, whole_sign, equal, regiomontanus" — ordre v1.1 d'abord puis v1.2. Le test pinned doit-il forcer cet ordre ?
   - **Recommandation** : garder ordre alphabétique (cohérent + déterministe + ne casse pas si v1.3 ajoute Campanus). Documenter l'ordre dans le help-text si nécessaire.

3. **Polar Regiomontanus : NaN-propagate ou swisseph-style swap ?**
   - **Ce qu'on sait** : swisseph fait MC ↔ IC swap à `|lat| > 90 - eps` ; Koch fait NaN dans Ketu ; le contrat HOU-06 v1.1 prévoit `polar_fallback` pour gérer le NaN.
   - **Ce qui est unclear** : si on suit le pattern Koch (NaN), `polar_fallback="porphyry"` substitue Porphyry pour les éléments polaires Regiomontanus. Mais l'utilisateur qui demande Regiomontanus à 80° N ne reçoit jamais "vrai Regiomontanus polar" — il reçoit Porphyry. C'est cohérent avec Koch, mais c'est une décision.
   - **Recommandation** : NaN-propagate (cohérence Koch ; simplicité) ; documenter dans la docstring.

4. **`HOU2-04` format** : « 5+ systèmes » : le `+` signifie-t-il « peut être plus » (acceptable Phase 16/17 ajouts) ou strictement 6 ?
   - **Ce qu'on sait** : REQUIREMENTS.md ligne 24 dit « 5+ systèmes » avec énumération exacte de 6. Ambiguïté de formulation.
   - **Recommandation** : Le test pin les 6 noms exacts (cf. §7.2), mais accepte que d'autres systèmes puissent être présents (ex: si un user-side `@register` ajoute un système ad-hoc, le test ne doit pas casser). Pattern : `for name in EXPECTED_SIX: assert name in actual`, pas `assert actual == EXPECTED_SIX`.

5. **Snapshot regen process : reproductible ?**
   - **Ce qu'on sait** : `tests/houses/fixtures/reference_charts.json` est committé. Le test `test_loaded_reference_snapshot_matches_oracle` re-vérifie à chaque run que swisseph live retourne les mêmes valeurs (1e-9 tolerance) — donc le snapshot est self-validating contre le pyswisseph runtime.
   - **Ce qui est unclear** : si swisseph patche un bug et retourne des valeurs différentes en 2.11, le snapshot doit être régénéré. Le script doit être **committé** pour que future-Sophie puisse le re-runner.
   - **Recommandation** : committer `scripts/snapshot_reference_charts.py` en Plan 15-01 ; ajouter une note dans `tests/houses/conftest.py:248-250` qui pointe vers le script effectif.

---

## Standard Stack

### Core (déjà installé v1.1)

| Library | Version | Purpose | Why standard |
|---|---|---|---|
| numpy | 2.3.5 (vérifié runtime 2026-05-09) | Structured arrays, broadcast, vectorisation | Pure-NumPy contract ; HOUSES_DTYPE consumed by Kala via positional indexing. |
| pyswisseph | 2.10.03 (vérifié runtime 2026-05-09) | Test-only oracle | AGPL non-contamination via `[project.optional-dependencies].test`. Provides `swe.houses_ex(jd, lat, lon, hsys)` and `swe.houses_armc(armc, lat, eps, hsys)` — both used by `tests/houses/conftest.py`. |
| pytest | 8.x | Test runner | déjà la convention v1.1. |

### Supporting

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| numpydoc | déjà dans `[project.optional-dependencies].test` | Docstring validation | Phase 13 OPS-02 gate ; doit passer clean sur `ketu/houses/` v1.2. |
| interrogate | déjà dans `[project.optional-dependencies].test` | Coverage de docstrings | Phase 13 OPS-01 gate ; ≥95% sur `ketu/houses/` v1.2. |
| mypy (--strict) | déjà la convention v1.1 | Type-check | Pas d'exception pour `ketu.houses.*` dans `pyproject.toml [[tool.mypy.overrides]]`. |

### Alternatives considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| pyswisseph oracle | self-implementation full suite (Meeus formulas) | Self-impl manque l'oracle indépendant qui catch nos bugs ; pyswisseph est l'industrie standard ; AGPL OK en test-only. |
| `_asc1` factor → `_ecliptic.py` | Duplication dans `regiomontanus.py` (mimic C source) | DRY win pour factorisation ; coût : 1 import additionnel dans Plan 1. Recommandation : factoriser. |
| HOUSES_DTYPE U10 → U16 | Renommer `regiomontanus` → `regio` | U16 préserve la lisibilité (`"regiomontanus"` est ce que l'utilisateur tape) ; risque ~zero pour Kala (pas évidence de itemsize check). |
| Hardcode polar-safe systems list dans `api.py:126` | Ajouter attribut `is_polar_safe: bool` sur les fns enregistrées | Hardcode est plus simple pour 3 systèmes ; attribut serait sur-ingénierie. |

**Installation** : aucune nouvelle install nécessaire (toutes les deps test-only sont déjà dans `[project.optional-dependencies].test` depuis v1.0/v1.1).

**Version verification** :

```bash
python -c "import swisseph; print(swisseph.version)"  # → 2.10.03 [VERIFIED 2026-05-09]
python -c "import numpy; print(numpy.__version__)"    # → 2.3.5 [VERIFIED 2026-05-09]
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Whole Sign formule | Implementation custom de "find ASC's sign" | Direct `asc - asc % 30` | swisseph fait pareil (`fmod(ac, 30)`). Pas de cas particulier ; mod 30 inclut `asc==0.0`. |
| Equal formule | Implementation custom des 12 cusps | Stack `(asc + offsets) % 360` | swisseph fait pareil. Vectorisation triviale ; pas besoin de boucle. |
| Regiomontanus formule | Implementation custom du prime vertical projection | Reuse `_asc1(armc + offset, fh, sin_eps, cos_eps)` (factorisé depuis Koch) | Le code C swisseph utilise la même `Asc1`. Inutile de réinventer. |
| Polar ASC swap | Custom logic à chaque module | Pattern `acmc_signed < 0 → asc + 180` (cf. porphyry.py:159-161) | DRY ; même bug peut survenir dans 3 modules sans pattern partagé. |
| Snapshot oracle | swisseph re-implementation pour Whole Sign / Equal / Regio | `swe.houses_ex(jd, lat, lon, b'W'/b'E'/b'R')` | swisseph 2.10.03 retourne les valeurs canoniques en bytes-form. |

**Key insight** : Phase 15 est essentiellement de la **transcription fidèle** du source C swisseph (cases `'W'`, `'E'`, `'R'`) en NumPy vectorisé. Aucune des trois formules ne nécessite de math nouvelle ou d'innovation. Le risque principal est dans les **détails** : ordre du polar swap, pole-height substitution, NaN propagation aux pôles. Tous résolus par référence directe au source.

---

## Code Examples

### Example 1 — Whole Sign full implementation

```python
# Source: ketu/houses/whole_sign.py (proposed)
from __future__ import annotations
import numpy as np
from .registry import register


@register("whole_sign")
def whole_sign_cusps(
    armc: np.ndarray, lat: np.ndarray, eps: np.ndarray,
) -> np.ndarray:
    """Compute the 12 Whole Sign house cusps.

    Each house occupies one zodiac sign; cusp 1 is at the start of the
    sign containing the Ascendant. Closed-form, vectorized, polar-safe.

    Source: swehouse.c case 'W' (https://github.com/aloistr/swisseph).

    Parameters
    ----------
    armc, lat, eps : np.ndarray
        Right ascension of MC (deg), geographic latitude (deg), obliquity (deg).

    Returns
    -------
    np.ndarray
        Shape (..., 12). Cusps in [0, 360); cusp[0]=cusp_1 at sign start.
    """
    armc_b, lat_b, eps_b = np.broadcast_arrays(armc, lat, eps)
    armc_rad = np.deg2rad(armc_b)
    eps_rad = np.deg2rad(eps_b)
    lat_rad = np.deg2rad(lat_b)
    # ASC and MC closed-form (matches compute_ascmc).
    mc = np.rad2deg(np.arctan2(
        np.sin(armc_rad), np.cos(armc_rad) * np.cos(eps_rad),
    )) % 360.0
    asc = np.rad2deg(np.arctan2(
        np.cos(armc_rad),
        -(np.sin(eps_rad) * np.tan(lat_rad)
          + np.cos(eps_rad) * np.sin(armc_rad)),
    )) % 360.0
    # Polar ASC swap (cf. porphyry.py:159-161).
    acmc_signed = ((asc - mc + 540.0) % 360.0) - 180.0
    asc = np.where(acmc_signed < 0.0, (asc + 180.0) % 360.0, asc)
    # Sign-floor cusp 1, then 30° steps.
    cusp_1 = asc - (asc % 30.0)
    offsets = np.arange(12, dtype=np.float64) * 30.0
    cusps: np.ndarray = (cusp_1[..., np.newaxis] + offsets) % 360.0
    return cusps
```

### Example 2 — Regiomontanus pole-height substitution

```python
# Source: swehouse.c case 'R'
fh1 = atand(tanfi * 0.5);                    # pole height for cusps 11, 3
fh2 = atand(tanfi * cosd(30));               # pole height for cusps 12, 2
hsp->cusp[11] = Asc1(30 + th, fh1, sine, cose);
hsp->cusp[12] = Asc1(60 + th, fh2, sine, cose);
hsp->cusp[2]  = Asc1(120 + th, fh2, sine, cose);
hsp->cusp[3]  = Asc1(150 + th, fh1, sine, cose);
```

[CITED: https://github.com/aloistr/swisseph/blob/master/swehouse.c case 'R']

### Example 3 — algorithm-tier test pattern (Koch-style)

```python
# Source: tests/houses/test_koch.py:54-90 (pattern to mimic for new systems)
@pytest.mark.parametrize("label", NON_POLAR_LABELS)
def test_whole_sign_algorithm_matches_oracle_armc_at_machine_precision(
    label: str,
    reference_charts: list[dict[str, Any]],
) -> None:
    from tests.houses.conftest import swe_oracle_armc
    chart = next(c for c in reference_charts if c["label"] == label)
    ascmc = compute_ascmc(chart["jd"], chart["lat"], chart["lon"])
    armc, eps, lat = float(ascmc["armc"]), float(ascmc["eps"]), float(chart["lat"])
    cusps = whole_sign_cusps(np.asarray(armc), np.asarray(lat), np.asarray(eps))
    oracle = swe_oracle_armc(armc, lat, eps, "whole_sign")
    deltas = np.abs(((cusps - oracle["cusps"] + 180.0) % 360.0) - 180.0)
    for i in range(12):
        assert float(deltas[i]) < ALGO_TOL_DEG
```

### Example 4 — étendre `SYSTEM_BYTES` dans le conftest

```python
# Source: tests/houses/conftest.py:77-81 (proposed extension)
SYSTEM_BYTES: dict[str, bytes] = {
    "placidus":      b"P",
    "koch":          b"K",
    "porphyry":      b"O",
    "whole_sign":    b"W",   # v1.2
    "equal":         b"E",   # v1.2
    "regiomontanus": b"R",   # v1.2
}
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| v1.1 = 3 systèmes hardcodés | v1.2 = 6 systèmes via registry HOU-02 | Phase 15 | Registry était déjà conçu extensible ; phase 15 est la première qui prouve l'extensibilité (HOU-02 promise v1.1). |
| `--system` choices = 3 noms hardcoded | `--system` choices = `sorted(SYSTEMS.keys())` dynamique | Phase 15 | Ajout futur (v1.3 Campanus etc.) sans changement de parser. |
| HOUSES_DTYPE['system'] = U10 | (potentiel) U16 pour `"regiomontanus"` | Phase 15 (si décidé) | NumPy-cast non-breaking, mais à documenter. |
| Snapshot fixtures = 3 systèmes × 10 charts | Snapshot fixtures = 6 systèmes × 10 charts | Phase 15 | Volume × 2 ; 60 blocs JSON. |

**Deprecated/outdated** : aucun ; tout est purement additif (non-breaking minor strict v1.2).

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| numpy | runtime + tests | ✓ | 2.3.5 | — |
| pyswisseph | tests-only oracle | ✓ | 2.10.03 | — (test-only ; absence skip wholesale via `pytest.importorskip` cf. conftest.py:59) |
| pytest | tests | ✓ | (latest from `[project.optional-dependencies].test`) | — |
| mypy | dev/CI | ✓ (Phase 13 wired) | strict mode | — |
| numpydoc | dev/CI | ✓ (Phase 13 OPS-02 wired) | — | — |
| interrogate | dev/CI | ✓ (Phase 13 OPS-01 wired) | — | — |

**Missing dependencies with no fallback** : aucune.

**Missing dependencies with fallback** : aucune.

---

## Sources

### Primaire (HIGH confidence)

- [swehouse.c source — github.com/aloistr/swisseph](https://github.com/aloistr/swisseph/blob/master/swehouse.c) — formules canoniques W/E/R, pattern polar swap, contraintes de polar circle.
- pyswisseph 2.10.03 runtime [VERIFIED 2026-05-09] — `swe.houses_ex(jd, lat, lon, hsys)` confirme acceptance des bytes `b'W'`, `b'E'`, `b'R'` ; comportement polar empiriquement vérifié.
- `ketu/houses/` v1.1 source code — pattern `@register`, signature `(armc, lat, eps) -> cusps[..., 12]`, `_asc1` helper, polar fallback contract HOU-06.
- `tests/houses/conftest.py` v1.1 — `swe_oracle()`, `swe_oracle_armc()`, `reference_charts` fixture (10 charts), `SYSTEM_BYTES` mapping.
- `.planning/REQUIREMENTS.md` — HOU2-01..05 verbatim.
- `.planning/phases/14-chart-abstraction-foundation/14-RESEARCH.md` — format/style référence v1.2.

### Secondaire (MEDIUM confidence)

- [DeepWiki swisseph house systems](https://deepwiki.com/aloistr/swisseph/4.1-house-systems) — liste des hsys codes ; cohérent avec swehouse.c.
- [Astrolabe / Astrodienst overview house systems](https://www.astro.com/faq/fq_fh_owhouse_e.htm) — taxonomie générale (W = Whole Sign, E = Equal, R = Regiomontanus) ; pas de formule détaillée.
- [Quadibloc Astrological House Systems](http://www.quadibloc.com/other/as01.htm) — explication conceptuelle "prime vertical projection" pour Regiomontanus.

### Tertiaire (LOW confidence — nécessite validation)

- [Occultish blog — Regiomontanus House System](https://occultish.app/blog/the-regiomontanus-house-system-astrology-101) — narrative non-technique ; pas utilisé pour formule ni gates.
- WebSearch sur formules Regiomontanus — toutes les sources convergent vers "division équateur en 12 → projection via prime vertical" mais formules exactes uniquement dans swehouse.c.

---

## Metadata

**Confidence breakdown** :
- Standard stack : HIGH — pyswisseph 2.10.03 + numpy 2.3.5 confirmés runtime ; pas de nouvelle dep nécessaire.
- Architecture : HIGH — Pattern registry/dispatch est en place v1.1 ; les 3 nouveaux fichiers suivent le moule (`koch.py`, `porphyry.py`).
- Formules : HIGH — Source primaire swehouse.c case `'W'`, `'E'`, `'R'` ; cross-checked empiriquement avec swisseph 2.10.03 sur Paris J2000.
- Polar safety : HIGH — Whole Sign/Equal polar-safe par construction (math validée) ; Regiomontanus singularité Koch-pattern (NaN-propagate).
- HOUSES_DTYPE U10 capacity : MEDIUM — A1 assumption posée ; à confirmer en discuss-phase si Kala dépend de itemsize.
- Reykjavik Regiomontanus drift estimation : MEDIUM — A2 assumption par analogie ; à mesurer empiriquement en Plan 15-03.
- Pitfalls : HIGH — pattern v1.1 stable ; les 7 pitfalls identifiés sont validables par tests.
- Coverage target : HIGH — précédent v1.1 atteint 96.75% ; Phase 14 100%.

**Research date** : 2026-05-09
**Valid until** : 2026-06-09 (30 days — pyswisseph stable, swehouse.c stable depuis 2018+).
