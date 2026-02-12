# Phase 1: API Surface Cleanup - Context

**Gathered:** 2026-02-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Define ketu's public API, remove export modules (charts, icalendar), clean up dependencies, and document the migration path from 0.4.0 to 1.0. This phase restructures what's exposed — no new features, no behavior changes to remaining modules.

</domain>

<decisions>
## Implementation Decisions

### Removal strategy
- Hard delete chart and icalendar modules — no stub modules, no deprecation warnings
- Standard Python ImportError if someone tries to import removed modules
- Full cleanup: delete related test files, fixtures, and config entries — no trace of removed modules
- Remove `fr/` directory (French translations) as part of this phase

### Public API shape
- Submodule access pattern: `from ketu.cycles import generate_cycle_series`, not flat top-level imports
- Users import from specific submodules (core, cycles, aspects), not from `ketu` directly
- `ketu.__init__.py` does NOT re-export submodule functions

### Dependency boundaries
- numpy is the ONLY hard dependency for v1.0
- swisseph already removed on develop branch — confirm and finalize removal
- svgwrite removed entirely (charts are gone)
- icalendar removed entirely
- matplotlib removed entirely
- No extras_require groups — just numpy, dev deps handled separately

### Migration guidance
- UPGRADING.md audience: internal use now, public-quality for PyPI release
- Keep library-generic — no Kala-specific references
- Tone: concise but professional for external developers

### Claude's Discretion
- What goes in `ketu.__all__` at top level (version, constants, or minimal)
- Whether submodules define their own `__all__`
- Whether to flatten or keep `ketu/cycles/` package structure
- UPGRADING.md depth and whether to write it in this phase or defer to Phase 6
- UPGRADING.md format (before/after snippets vs concise list)

</decisions>

<specifics>
## Specific Ideas

- swisseph is already removed on develop — the numpy-only story is already in progress
- User confirmed "seulement numpy" — strong preference for minimal dependency footprint
- Hard delete philosophy: clean break, no backwards compatibility shims

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-api-surface-cleanup*
*Context gathered: 2026-02-12*
