# Phase 16: Synastry - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Compute aspects between two natal charts via `calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")`. Returns a `SYNASTRY_DTYPE` NumPy structured array. Supports two output modes (dense N×N matrix / filtered orbed list) and uses synastry-tightened orbs distinct from natal orbs. Also exposes a `ketu synastry` CLI sub-command. Depends on Phase 14 (`CHART_DTYPE`).

**Out of scope** (deferred to other phases): composite charts (Phase 17), solar return (Phase 18), Arabic Parts cross-chart (Phase 19), Davison composite (v1.3+), transits-to-natal (separate concern), batch synastry over arrays of charts.

</domain>

<decisions>
## Implementation Decisions

### SYNASTRY_DTYPE schema
- Schema composition and exact field list → **Claude's Discretion** during research/planning. Floor: the 5 mandatory fields from ROADMAP success criterion #1 (`body_a, body_b, aspect_type, orb, applying`). Researcher should evaluate field economy against `CYCLE_DTYPE` (16 fields) and `HOUSES_DTYPE` precedents — pick the level that gives auto-sufficiency without bloating memory for ML batch use.
- **Self-pairs INCLUDED** in dense mode — Sun_A↔Sun_B, Moon_A↔Moon_B are the canonical synastry aspects (ego compatibility, emotional compatibility). Matrix is fully populated, no diagonal skip.
- Bodies eligible for synastry → **Claude's Discretion**. Researcher to align with `CHART_DTYPE` body set from Phase 14 (planets + ASC/MC at minimum — ASC contact is astrologically critical in synastry).
- `applying` field semantics → **Claude's Discretion**. Researcher to choose between velocity-based natal convention (using natal speeds stored in CHART_DTYPE) vs always-False MVP. Document the choice loudly in docstring.

### Dense vs filtered API
- **Mode selector**: `mode="dense" | "filtered"` (explicit string parameter, extensible to future modes).
- **Default**: `mode="filtered"` — practical default for astrological use (significant aspects only, not a 13×13 mostly-empty matrix).
- **Output schema identity** between modes → **Claude's Discretion**. Both modes share the same `SYNASTRY_DTYPE`; researcher decides whether dense fills `aspect_type="none"` / `orb=NaN` for non-aspected pairs OR returns a stable-shape masked array.
- **Batch over arrays of charts**: NOT in scope. MVP is single-pair only — `calculate_synastry(chart_a: CHART_DTYPE scalar, chart_b: CHART_DTYPE scalar)`. Vectorization across multiple chart pairs deferred (YAGNI). The v1.2 "Vectorizable" constraint applies to the internal aspect computation over body pairs (NumPy-style), not to the public batch surface.
- **Row ordering in filtered mode** → **Claude's Discretion**. Researcher to pick between orb-ascending (astro.com convention) or canonical body-pair order (predictable for ML/tests).

### Orbs synastry source
- **Foundation formula**: re-use Ketu's house orb formula `orb_pair = (bodies["orb"][b1] + bodies["orb"][b2]) / 2 * aspects["coef"][asp]` from `ketu/aspects/calculator.py:32`. The values for `bodies["orb"]` (12, 12, 8, 10, 8, 10, 10, 6, 6, 4, 0, 0, 0) and `aspects["coef"]` are AUTHORITATIVE — synastry orbs must derive from this formula, not redefine ab initio.
- **Tightening mechanism for synastry** → **Claude's Discretion**. Researcher to choose:
  - Global multiplicative factor (`synastry_orb = natal_orb × SYNASTRY_FACTOR`)
  - Dedicated synastry coefficient table parallel to `aspects["coef"]`
  - Body-orb override table for synastry
  Document the chosen formula AND its source/citation in the docstring (success criterion #3 demands citation).
- **Storage location** → **Claude's Discretion**. Researcher to decide between (a) extending Phase 9's `ORBS` registry with a `"synastry"` preset (consistent with the v1.1 registry-extensibility pattern) vs (b) a dedicated `ketu/synastry/orbs.py` module. Pick whichever aligns with Phase 9's existing pattern.
- **User override** → **Claude's Discretion**. Researcher to decide what override surface to expose (`orbs={"factor": 0.5}` dict, `synastry_orb_factor=...` scalar param, or no override in MVP). Align with Phase 9's `aspects=` configurability pattern.
- **`orbs="classical"` accepted in synastry** → **Claude's Discretion**. Decide whether to allow natal-orb width inside synastry for expert comparison views, or restrict to tightened synastry orbs only.

### CLI exposition
- **Sub-command IN SCOPE**: `ketu synastry` is a full sub-command of the CLI, on par with `ketu houses` and `ketu aspects`. NOT an API-only phase.
- **Default output format**: aligned ASCII table (human-readable), consistent with `ketu houses` convention. `--json` flag for programmatic use. NOT JSON-by-default.
- **Input args design** → **Claude's Discretion**. Researcher to pick between repeated suffixed args (`--date-a ... --lat-a ...`), optional YAML/JSON chart files (`--chart-a alice.yaml`), or grouped positional specs. Align with argparse patterns already used in `ketu houses` / `ketu aspects`.
- **Flags exposed**:
  - `--mode dense|filtered` (default: filtered)
  - `--system <house_system>` (default: placidus) — same registry as Phase 15 (6 systems: placidus/koch/porphyry/whole_sign/equal/regiomontanus)
- **`--list-orbs` introspection flag**: IN SCOPE. Mirrors `--list-house-systems` (Phase 11/15) and `--list-aspects` patterns. Prints the synastry orb table (per body × aspect or per body + coef formula representation).

### Claude's Discretion (consolidated)
- Exact `SYNASTRY_DTYPE` field set beyond the 5 mandatory
- Body scope (planets only / +ASC/MC / full CHART_DTYPE bodies)
- `applying` field computation strategy
- Output schema identity in dense mode (NaN-fill vs masked)
- Row ordering in filtered mode
- Synastry orb tightening formula (factor / per-aspect / per-body)
- Storage location for synastry orbs (ORBS registry extension vs dedicated module)
- User override surface for orbs
- Whether `orbs="classical"` is accepted in synastry
- CLI input args design (suffixed / file / positional)
- `--list-orbs` exact print format

</decisions>

<specifics>
## Specific Ideas

- **Reuse Ketu's existing orb formula, not external orb tables.** The user explicitly anchored synastry orbs to the in-house formula `(orb_body1 + orb_body2) / 2 * coef_aspect` (defined in `ketu/aspects/calculator.py:32` with `bodies["orb"]` from `ketu/core.py:65`). Synastry tightening must be a transformation OF this formula (a factor, a coefficient table, etc.), NOT a parallel hardcoded table from Robert Hand / Astro.com — those serve only as cross-validation references, not as primary source.
- **Self-pairs are the headline of synastry**: Sun_A↔Sun_B (ego compatibility) and Moon_A↔Moon_B (emotional compatibility) MUST be present in dense output. This is non-negotiable astrologically.
- **CLI parity with `ketu houses`**: same shell experience — aligned tables, `--json` opt-in, `--list-*` introspection, same argparse style.
- **3 oracle synastry pairs** (success criterion #4): hand-validated against Astro.com or Solar Fire. Researcher to scout for celebrity/public-figure pairs whose data is unambiguously known (birth times documented) — avoid synthetic pairs.

</specifics>

<deferred>
## Deferred Ideas

- **Batch synastry** (N×M chart pairs in one call) — re-evaluate if downstream Kala consumers need it; not v1.2 scope.
- **Composite chart** — Phase 17 (already planned).
- **Solar return synastry** (return chart ↔ natal chart) — naturally falls in Phase 18 territory, not here.
- **Davison composite** — explicit v1.3 deferral (already noted in Phase 17 success criteria).
- **Transit-to-natal aspects** — different concern (single chart + moving date), not synastry.
- **Synastry interpretation engine** (text rendering of aspect meanings) — out of Ketu's pure-calc scope.

</deferred>

---

*Phase: 16-synastry*
*Context gathered: 2026-05-10*
