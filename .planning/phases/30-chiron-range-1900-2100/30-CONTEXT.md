# Phase 30: Chiron Range 1900–2100 - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Étendre la plage de validité des coefficients Chebyshev embarqués de Chiron de 1950–2050 à **1900–2100**, validée à **< 0.01°** contre Swiss Ephemeris (région du périhélie ~1895–1896 incluse, juste sous la borne basse), via un **spike bloquant** exécuté AVANT tout commit du `.npz`. Les callers avec des dates du début du XXe siècle reçoivent des positions Chiron exactes au lieu d'une erreur runtime.

L'évaluation runtime reste 100% pure NumPy (aucun import `pyswisseph` dans `ketu/ephemeris/chiron.py`). Le fix `actual_len` du dernier segment (Phase 24-04) est préservé lors de la régénération. Dépend de Phase 29 (orbe Chiron finalisé avant régénération du `.npz`, évite le double churn de fixture CLI).

**Hors périmètre** (autres phases) : documentation de la nouvelle plage (Phase 31), release/version bump (Phase 32), toute modification de la sémantique d'erreur au-delà de l'extension de plage.

</domain>

<decisions>
## Implementation Decisions

### Stratégie de repli du spike (si gate < 0.01° échoue sur les ailes 1900–1950)
- **Levier #1 = monter `degree` 10→12** (plus de termes Chebyshev par segment). C'est le premier essai si le gate casse sur les ailes à fort gradient près du périhélie.
- **Paramètres UNIFORMES sur toute la plage 1900–2100** — un seul `degree`, un seul `seg_len`. PAS de paramètres adaptatifs par région (segments hétérogènes rejetés : complexifient le générateur + l'évaluateur, et risquent le fix `actual_len`). Quitte à être légèrement sur-dimensionné au centre.
- **Borne basse 1900 ferme** ; remonter à ~1905 n'est accepté qu'en **tout dernier recours documenté**, et seulement après accord utilisateur explicite (cf. Traçabilité — Stop + demander).
- **Pas de contrainte stricte sur la taille du `.npz`** — la précision prime. La plage 2× plus large + `degree` potentiellement 12 peut faire ~doubler/tripler la taille du fichier embarqué dans le wheel ; c'est acceptable pour une lib d'éphémérides.

### Bornes & comportement hors-plage
- **Bornes calendaires** : `jd_start = JD(1900-01-01 UTC)`, `jd_end = JD(2100-01-01 UTC)`. Convention nette, facile à documenter et tester.
- **Comportement hors-plage actuel CONSERVÉ** — Phase 30 = données, pas sémantique d'erreur. On étend la plage de validité sans changer ce qui arrive à une date < 1900 ou > 2100. Le planner doit d'abord **inspecter et rapporter** le comportement actuel de `chiron.py` hors-plage (erreur ? clamp ? NaN ?) ; on le préserve tel quel.
- **Tests aux bornes ET juste dehors** : points pinnés à 1900.0 et 2100.0 (dedans, valides, longitude finie < 0.01°) + un point juste avant 1900 et juste après 2100 (vérifie que le comportement hors-plage attendu — celui d'aujourd'hui — est inchangé). Verrouille le contrat de plage.
- **Périhélie ~1895–96 (sous la borne)** : le spike doit **valider densément le bord 1900–1905 sous gradient** — échantillonnage dense de 1900–1910, pas de moyenne qui masquerait un pic local. C'est là que le gate risque de casser ; mesure prioritaire du worst-case.

### Stratégie de re-pinning des tests
- **Source de vérité = Swiss Ephemeris (pyswisseph)** — même oracle que le spike Phase 23 et la validation Phase 24. Longitudes générées par pyswisseph (build/test-only) puis pinnées en dur dans le test. Cohérent avec le gate < 0.01°.
- **Garder les refs existants 1950–2050 + AJOUTER les ailes** — non-régression du centre préservée, la couverture grandit sans rien retirer. Un ref n'est supprimé que s'il devient incohérent avec la nouvelle génération.
- **Densité minimale (CHIR-11)** : au moins **1 ref pré-1950** (ex. 1920) + **1 ref post-2050** (ex. 2080). Au moins un point dans la région à fort gradient 1900–1910 si le risque s'y matérialise.
- **Gate < 0.01° UNIFORME partout** — anciens et nouveaux refs, centre et ailes, tenus au même seuil. Contrat uniforme, simple à expliquer.

### Traçabilité du spike
- **Consigner dans le decision log STATE/PROJECT** (style `[Phase 23-01]`, `[Phase 24-04]`) : max|Δλ| mesuré, paramètres finaux retenus (`seg`/`degree`), et la décision (degree conservé à 10 ou monté à 12). Mémoire long-terme, retrouvable.
- **Spike ÉPHÉMÈRE** — rien committé sous `tools/`/`ketu/`/`tests/`/`pyproject` (précédent Phase 23 : « spike-only »). On mesure, on consigne le verdict dans le decision log, on jette le script de mesure.
- **Check pré-vol build EXPLICITE en première étape du spike** : vérifier que `pyswisseph` importe et que `seas_18.se1` (couvre 1800–2400, donc englobe 1900–2100) est trouvable ; échouer tôt avec un message clair si l'environnement build manque. Évite un spike à moitié fait.
- **Échec total → STOP + demander** : si même `degree=12` (et tout levier raisonnable à params uniformes) ne tient pas < 0.01° à 1900.0, le workflow **s'arrête et demande à l'utilisateur** avant de remonter la borne (~1905 = modification de requirement / scope). L'utilisateur valide tout rétrécissement de plage.

### Claude's Discretion
- Valeur exacte de `seg_len` si une réduction s'avérait nécessaire (mais en restant uniforme, jamais adaptatif).
- Choix exact des dates de référence pré-1950/post-2050 (1920 vs 1930, etc.) tant que le minimum CHIR-11 est respecté + au moins un point dans la zone à risque 1900–1910.
- Détails d'implémentation du script de spike éphémère (échantillonnage, format de sortie interne).
- Mécanique de génération des longitudes-oracle Swiss Ephemeris pour le pinning.

</decisions>

<specifics>
## Specific Ideas

- Le **spike est un gate dur** : ne PAS committer le nouveau `.npz` tant que la mesure max|Δλ| sur 1900–2100 (périhélie ~1895–96 inclus) ne passe pas < 0.01°. Ordre strict : pré-vol build → mesure densément échantillonnée (bord 1900–1905 prioritaire) → décision degree → consignation decision log → seulement ensuite régénération + commit `.npz`.
- Préserver impérativement le fix `actual_len` du dernier segment (Phase 24-04 : `actual_len = min(seg_start+seg_len, jd_end) - seg_start`) lors de la régénération.
- Runtime pur-NumPy NON-NÉGOCIABLE : `ketu/ephemeris/chiron.py` ne doit importer `pyswisseph` à aucun moment ; le `.npz` est régénéré offline par `tools/gen_chiron_coeffs.py` (build-only).

</specifics>

<deferred>
## Deferred Ideas

- Documentation de la plage Chiron 1900–2100 dans les docs Sphinx (en + fr) — **Phase 31** (DOC-16).
- Toute extension de plage au-delà de 1900–2100 (ex. 1800–2400 que `seas_18.se1` couvrirait) — hors scope ; si un jour pertinent, un script de validation réutilisable sous `tools/` pourrait être reconsidéré (rejeté ici au profit de l'éphémère).
- Modification de la sémantique d'erreur hors-plage (ValueError explicite avec message) — non retenu pour cette phase (comportement actuel conservé) ; pourrait être une amélioration future si souhaité.

</deferred>

---

*Phase: 30-chiron-range-1900-2100*
*Context gathered: 2026-06-03*
