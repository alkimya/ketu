# Ketu v1.2 — Requirements

**Milestone:** v1.2 Astrologie relationnelle et prédictive
**Framing:** non-breaking minor strict — toutes les nouvelles APIs sont additives. Aucun changement de défaut sur les APIs existantes. Aucun export retiré.
**Defined:** 2026-05-08 from `.planning/research/v1.2-SCOPE.md` + `v1.2-OPEN_QUESTIONS.md` (pre-research working docs) and `/gsd-new-milestone` questioning.

---

## v1.2 Requirements

### Chart abstraction (foundation — upstream of synastry/composite/return)

- [x] **CHART-01** : `ketu/charts/` subpackage created with `__init__.py` exposing public API *(Phase 14, 2026-05-09)*
- [x] **CHART-02** : `CHART_DTYPE` structured array defined (positions par body + ASC + MC + ARMC + Vertex + cusps + aspects scalaires) — analogue de `HOUSES_DTYPE` / `CYCLE_DTYPE`, ML-interop NumPy-first *(Phase 14, 2026-05-09)*
- [x] **CHART-03** : `compute_chart(jd, lat, lon, system="placidus", aspects="classical") → CHART_DTYPE` calcule un thème complet en un appel, vectorisable sur des arrays de `jd` *(Phase 14, 2026-05-09)*
- [x] **CHART-04** : `is_day_chart(jd, lat, lon) → bool` helper vectorisable (Sun au-dessus de l'ASC = jour, sunrise inclusive) *(Phase 14, 2026-05-09)*
- [x] **CHART-05** : Couverture ≥95 % sur `ketu/charts/` (gate identique à v1.1 houses) — atteint 100% *(Phase 14, 2026-05-09)*

### Additional house systems (Tier 1)

- [x] **HOU2-01** : Whole Sign houses — chaque maison = un signe, démarrant au signe de l'ASC ; polar-safe ; enregistré dans `SYSTEMS`
- [x] **HOU2-02** : Equal houses — cusps espacés de 30° depuis l'ASC ; polar-safe ; enregistré dans `SYSTEMS`
- [x] **HOU2-03** : Regiomontanus houses — division de l'équateur céleste projetée via le prime vertical ; enregistré dans `SYSTEMS`
- [x] **HOU2-04** : `--list-house-systems` retourne désormais `placidus, koch, porphyry, whole_sign, equal, regiomontanus` (5+ systèmes)
- [x] **HOU2-05** : Chaque nouveau système validé contre Swiss Ephemeris sur les 10 reference charts existants (gate identique v1.1) ; max ASC delta documenté

### Synastry (Tier 1 — relational)

- [x] **SYN-01** : `calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry") → SYNASTRY_DTYPE` calcule les aspects inter-charts (cross-product N×M des bodies)
- [x] **SYN-02** : `SYNASTRY_DTYPE` structured array préserve l'origine de chaque body (chart A vs chart B) + aspect type + orb + applying/separating
- [x] **SYN-03** : Convention d'orbs synastry (3-5° pour les majeurs) documentée et applicable via le param `orbs=`, distinct de l'orb natale (8-10°)
- [x] **SYN-04** : Output mode dense (matrice N×M) ET filtré (liste d'aspects orbés) — caller choisit
- [x] **SYN-05** : Tests synastry vs Astro.com / Solar Fire sur 3+ paires de charts (oracle hand-validated)

### Composite chart (Tier 1 — midpoint variant only)

- [x] **COMP-01** : `calculate_composite(chart_a, chart_b, system="placidus") → CHART_DTYPE` retourne un composite midpoint sous forme de `CHART_DTYPE`
- [x] **COMP-02** : `circular_midpoint(lon_a, lon_b)` helper modulo 360° vectorisable ; cas-test pinné `mid(359°, 1°) = 0°` (PAS 180°)
- [x] **COMP-03** : Composite houses calculées depuis composite ASC + composite MC (pas re-computées indépendamment)
- [x] **COMP-04** : Tests composite vs Astro.com sur 2+ paires de charts (self-consistency oracle PRIMARY ; Astro.com manual cross-check deferred — see 17-04-SUMMARY.md "Astro.com Manual Cross-Check")
- [x] **COMP-05** : ≥95% line coverage gate on `ketu/composite/` via `make composite-coverage` target + `composite_coverage_gate` pytest marker (Plan 17-04 close-out addition; mirror of SYN-05 / CHART-05 / HOU-09).

### Solar return (Tier 1 — predictive)

- [x] **RET-01** : `solar_return(natal_jd, natal_lat, natal_lon, target_year, return_lat=None, return_lon=None, system="placidus") → CHART_DTYPE` ; si `return_lat/lon` sont None, utilise lat/lon natals (standard) ; sinon relocated
- [x] **RET-02** : Root-finding pure-NumPy sur `Sun_longitude(t) − natal_Sun_longitude` ; gestion explicite du wrap-around 360°→0° (pre-unwrap ou résidus atan2-style)
- [x] **RET-03** : Convergence tolerance `<1 arc-second` sur le temps résolu (convention pro-tools)
- [x] **RET-04** : Tests solar return vs Astro.com sur 3+ années cibles (incluant un cas wrap-around)
- [x] **RET-05** : Documentation explicite de la distinction `natal_lat/lon` (pour le longitude natal du Soleil) vs `return_lat/lon` (pour les houses de retour)
- [x] **RET-06** : ≥95% line coverage gate on `ketu/returns/` via `make returns-coverage` target + `returns_coverage_gate` pytest marker (Plan 18-01 close-out addition; mirror of COMP-05 / SYN-05 / CHART-05 / HOU-09).

### Lunar return (Tier 1 — predictive)

- [x] **LRET-01** : `lunar_return(natal_jd, natal_lat, natal_lon, target_jd, return_lat=None, return_lon=None, system="placidus") → CHART_DTYPE` ; résout le premier retour lunaire ≥ `target_jd` (~27.32 jours de période sidérale) ; relocation via `return_lat/lon` (None = standard)
- [x] **LRET-02** : Root-finding pure-NumPy sur `Moon_longitude(t) − natal_Moon_longitude` partageant la même infrastructure de wrap-around 360°→0° que `solar_return` (pre-unwrap ou résidus atan2-style) ; **factorisation explicite** d'un helper interne `_solve_return(body, ...)` réutilisé par les deux returns
- [x] **LRET-03** : Convergence tolerance `<1 arc-second` sur le temps résolu (même convention pro-tools que RET-03)
- [x] **LRET-04** : Tests lunar return vs Astro.com sur 3+ dates cibles (incluant un cas wrap-around et un cas où le retour tombe à cheval sur le jour suivant le `target_jd`)
- [x] **LRET-05** : Documentation explicite des sémantiques de `target_jd` (cible temporelle, pas une année comme RET-01) et de la distinction `natal_lat/lon` vs `return_lat/lon` (mêmes pièges que RET-05)

### Arabic Parts framework (Tier 2)

- [ ] **PARTS-01** : `ketu/parts/` subpackage avec `PARTS` registry extensible (analogue à `SYSTEMS`)
- [ ] **PARTS-02** : `Part` dtype/spec : `(name, day_formula, night_formula)` où chaque formula est `Callable[(asc_lon, body_lons), lon]`
- [ ] **PARTS-03** : `calculate_part(part_name, chart) → lon` détermine sect via `is_day_chart`, applique la bonne formula
- [ ] **PARTS-04** : `calculate_all_parts(chart, parts=None) → dict[str, float]` retourne tous les parts du registry (ou ceux listés)
- [ ] **PARTS-05** : Part of Fortune livrée (Lot of Fortune) — formula day `ASC + Moon − Sun`, night `ASC + Sun − Moon` (sect-aware)
- [ ] **PARTS-06** : Part of Spirit livrée (Lot of Spirit) — formula day `ASC + Sun − Moon`, night `ASC + Moon − Sun` (sect-aware, miroir de Fortune). *Scope réduit 2026-05-28 : les 5 autres Hermetic Lots (Eros, Necessity, Courage, Victory, Nemesis) reportés à v1.3 — variantes de tradition concurrentes, registry extensible les absorbe additivement.*
- [ ] **PARTS-07** : Part of Marriage livré — formula `ASC + Descendant − Venus` (≡ `ASC + (ASC+180°) − Venus`), **fixe** (pas d'inversion jour/nuit ; opt-out du dispatch sect-aware)
- [ ] **PARTS-08** : `--list-parts` flag CLI introspection, analogue à `--list-house-systems`

### Tier 3 — ops debt (deadline septembre 2026)

- [x] **OPS-01** : `interrogate ≥95%` installé en `[project.optional-dependencies]` (test-only) et wiré dans CI ; échoue le build si en dessous du seuil
- [x] **OPS-02** : `numpydoc validate` wiré dans CI sur les modules publics ; warnings non-bloquants au début, gate à activer en fin de milestone
- [ ] **OPS-03** : Workflows refresh — `actions/checkout@v5+`, `actions/setup-python@v6+`, `actions/upload-artifact@v5+` (Node.js 24) ; tous les warnings Node 20 supprimés
- [ ] **OPS-04** : `fr/CHANGELOG.md` créé (synthétisé depuis l'anglais, pas double-maintenu) OU la référence aspirationnelle retirée — décision finale documentée
- [ ] **OPS-05** : v1.2 release published on PyPI as `ketu==1.2.0` via OIDC trusted publishing ; GitHub release avec sdist + wheel ; CHANGELOG `[1.2.0]` + UPGRADING.md migration recipes (additive only)

---

## Future Requirements (v1.3+)

Captured here so they don't drift. Pulled from `v1.2-SCOPE.md` and resolved questions.

- **Chiron + Centaurs (Pholus, Nessus, Chariklo)** — v1.3 dédié ; spike Chebyshev-by-segment polynomial fit pipeline en option
- **Davison composite** — chart pour temps + lat/lon midpoints ; complément du midpoint composite v1.2
- **Lunar return** — même algo que solar return avec fenêtre 28j ; cheap si `solar_return` est généralisable
- **Transits / progressions / directions** — techniques prédictives au-delà du solar return ; v1.3 ou v1.4
- **True / Osculating Lilith (h13)** — variante apogee instantané ; rare en pratique
- **Asteroid Lilith #1181** — corps différent de h12 Mean Lilith
- **Asteroids (Ceres, Pallas, Juno, Vesta), fixed stars** — v1.4+ (même problème dépendance que Chiron)

---

## Out of Scope

Explicit boundaries pour v1.2.

- **BREAKING changes** — v1.1 a brûlé le quota (Lilith ~180°, CLI default flip, `calculate_house_cusps` removal). v1.2 = additive only ; aucun changement de défaut, aucun export retiré.
- **Davison composite** — defer v1.3 ; midpoint suffit pour v1.2
- **Chiron + autres bodies** — defer v1.3 ; nécessite swisseph runtime ou Chebyshev-fit pipeline (tooling pas en place)
- **Transits / progressions** — solar return uniquement pour v1.2 ; transits = continuous time-series, problème de forme différent
- **Lunar return** — defer post-`solar_return` si demande surface
- **Autres house systems** au-delà de Whole Sign / Equal / Regiomontanus — Campanus, Topocentric, Alcabitius : registry les supporte mais pas livrés v1.2
- **scipy / autres deps runtime** — pure-NumPy contract reste non-négociable (cf. CLAUDE.md). Bisection / Newton step en NumPy maison pour solar return.
- **`pyswisseph` runtime** — toujours test-only (AGPL non-contamination)
- **Web API / GUI / SVG charts** — Ketu reste une library
- **Timezone handling inside Ketu** — UTC requis ; conversion = caller's responsibility (réaffirmé loudly dans synastry/return docstrings où l'erreur serait commune)

---

## Traceability

Each REQ-ID maps to exactly one phase. Filled by `gsd-roadmapper` 2026-05-08.

| REQ-ID    | Phase    | Status  |
|-----------|----------|---------|
| CHART-01  | Phase 14 | ✓ Done  |
| CHART-02  | Phase 14 | ✓ Done  |
| CHART-03  | Phase 14 | ✓ Done  |
| CHART-04  | Phase 14 | ✓ Done  |
| CHART-05  | Phase 14 | ✓ Done  |
| HOU2-01   | Phase 15 | Complete |
| HOU2-02   | Phase 15 | Complete |
| HOU2-03   | Phase 15 | Complete |
| HOU2-04   | Phase 15 | Complete |
| HOU2-05   | Phase 15 | Complete |
| SYN-01    | Phase 16 | Done |
| SYN-02    | Phase 16 | Done |
| SYN-03    | Phase 16 | Done |
| SYN-04    | Phase 16 | Done |
| SYN-05    | Phase 16 | Done |
| COMP-01   | Phase 17 | Done |
| COMP-02   | Phase 17 | Done |
| COMP-03   | Phase 17 | Done |
| COMP-04   | Phase 17 | Done |
| COMP-05   | Phase 17 | Done |
| RET-01    | Phase 18 | Done |
| RET-02    | Phase 18 | Done |
| RET-03    | Phase 18 | Done |
| LRET-01   | Phase 18 | Done |
| LRET-02   | Phase 18 | Done |
| LRET-03   | Phase 18 | Done |
| LRET-04   | Phase 18 | Done |
| LRET-05   | Phase 18 | Done |
| RET-04    | Phase 18 | Done |
| RET-05    | Phase 18 | Done |
| RET-06    | Phase 18 | Done |
| PARTS-01  | Phase 19 | Pending |
| PARTS-02  | Phase 19 | Pending |
| PARTS-03  | Phase 19 | Pending |
| PARTS-04  | Phase 19 | Pending |
| PARTS-05  | Phase 19 | Pending |
| PARTS-06  | Phase 19 | Pending |
| PARTS-07  | Phase 19 | Pending |
| PARTS-08  | Phase 19 | Pending |
| OPS-01    | Phase 13 | Complete |
| OPS-02    | Phase 13 | Complete |
| OPS-03    | Phase 20 | Pending |
| OPS-04    | Phase 20 | Pending |
| OPS-05    | Phase 20 | Pending |

**Coverage:** 37/37 v1.2 requirements mapped — no orphans, no double-mappings.

---

*Defined: 2026-05-08 by Sophie Chen during `/gsd-new-milestone`. Pre-research docs (`v1.2-SCOPE.md`, `v1.2-OPEN_QUESTIONS.md`) consumed and superseded by this file. Research path skipped (decided non-breaking minor with prior architectural decisions already captured). Traceability filled by `gsd-roadmapper` 2026-05-08 after roadmap approval.*
