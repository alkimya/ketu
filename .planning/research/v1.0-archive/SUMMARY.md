# Project Research Summary

**Project:** Ketu 1.0 Consolidation
**Domain:** Python scientific library (astronomical calculations for financial analysis)
**Researched:** 2026-02-12
**Confidence:** HIGH

## Executive Summary

Ketu is a mature Python astronomical calculation library (0.4.0 → 1.0.0) built on NumPy and swisseph. The consolidation focuses on hardening a working system, not building from scratch. Research confirms the existing stack (NumPy + swisseph) is optimal for the domain. The recommended approach is surgical: fix known bugs, remove anti-features (chart/icalendar exports), eliminate hidden dependencies, and standardize the API surface. This is a brownfield consolidation, not greenfield development.

The critical risk is breaking existing users without proper migration paths. 1.0.0 signals API stability, so all breaking changes must happen NOW with clear deprecation warnings. Scientific Python libraries demand strict semantic versioning—users cache computation results and expect reproducibility. The research identified 7 critical pitfalls (API breaks, SemVer confusion, hidden dependencies, module removal, test coverage gaps, precision loss, platform differences) that must be addressed before release. The recommended phase structure prioritizes API cleanup first, then correctness fixes, then quality hardening.

Key insight: This is NOT feature development. Success means shipping a stable, well-tested, correctly-documented version of what already works. The roadmap should reflect consolidation phases (cleanup, fix, test, document, release) rather than feature delivery phases. Target 70% test coverage with focus on critical modules (cycles, cache, aspects >85%) not overall metrics.

## Key Findings

### Recommended Stack

The existing stack requires minimal changes. Ketu has already chosen the right dependencies for its domain—astronomical calculations with NumPy-native output.

**Core technologies (no changes):**
- **Python 3.11+**: Already established, aligns with NEP 29 support policy
- **NumPy 1.x+2.x**: Core of numerical API, support both 1.x and 2.x with compatibility layer
- **swisseph**: Industry standard ephemeris, no viable alternatives for offline calculations

**Development tooling (additions recommended):**
- **ruff**: Replace flake8/black with single fast linter/formatter
- **mypy**: Enforce type hints in CI (currently not enforced)
- **pytest + pytest-cov**: Already present, formalize per-module coverage targets

**Key decision:** Support both NumPy 1.x and 2.x (flexible approach) with CI testing of both versions. Test matrix should cover Python 3.11-3.13 on Ubuntu, macOS, Windows.

**Philosophy preserved:** Minimize production dependencies. Current state (swisseph + NumPy only) is ideal. Every avoided dependency reduces installation complexity, security surface, and version compatibility issues. Pandas must be removed from aspect timelines—rewrite to use structured NumPy arrays (CYCLE_DTYPE already exists).

### Expected Features

Scientific Python libraries at 1.0 must meet higher standards than typical packages. Missing any table stakes feature signals immaturity.

**Must have (table stakes for 1.0):**
- Full type hints across all public functions (enables IDE support, mypy checking)
- Semantic versioning 2.0 with API stability guarantees (1.x = backward compatible)
- Comprehensive NumPy-style docstrings with working examples
- Input validation with contextual error messages (not cryptic swisseph errors)
- Clean `__all__` exports defining public API surface
- Deprecation policy documented (2-version window standard)
- Numerical accuracy documentation (precision limits, edge cases)
- Changelog following Keep-a-Changelog format

**Should have (differentiators vs skyfield/pyephem/astropy):**
- NumPy structured arrays everywhere (ML-ready, zero-copy to pandas)
- Complex number representation for elegant cycle math
- Performance benchmarks vs alternatives (prove speed advantage)
- Minimal dependencies (swisseph + NumPy only = easy deployment)
- Financial domain focus (DEFAULT_PAIRS chosen for trading analysis)
- Batch calculation optimization (vectorization over loop-based competitors)

**Anti-features (remove for 1.0):**
- Chart visualization (`ketu.export.chart`) — not calculation library's job
- iCalendar export (`ketu.export.icalendar`) — domain drift
- CLI/GUI — scope creep, stay library-only
- Pandas dependency — remove from aspect timelines, use structured arrays
- Built-in caching beyond ephemeris — user responsibility

**MVP prioritization:** Phase structure should be API Cleanup → Documentation → Quality → Differentiation. Table stakes must be complete before release. Differentiators can be enhanced post-1.0 (e.g., property-based testing, performance regression CI).

### Architecture Approach

Ketu should remain a pure calculation library with three-layer architecture: Public API (type-hinted, documented, stable) → Internal Modules (implementation details) → External Dependencies (swisseph, NumPy). All calculations follow the same pattern: validate inputs → normalize to NumPy arrays → swisseph calculation → vectorized processing → structured array output. No side effects—pure functions only.

**Major components:**
1. **Public API** (`ketu/__init__.py`) — Explicit `__all__` exports, semantic versioning, stable signatures
2. **Cycle Engine** (`ketu.cycles.*`) — CYCLE_DTYPE structured arrays, DEFAULT_PAIRS, vectorized calculations
3. **Aspect Engine** (`ketu.aspects.*`) — 14-aspect detection, orb calculations, timelines (rewrite to NumPy, remove Pandas)
4. **Ephemeris Layer** (`ketu.core`, `ketu.ephemeris.*`) — swisseph wrappers, coordinate conversions, time utilities
5. **Complex/Resonance** (`complex.py`, `resonance.py`) — Complex number representation, needs full integration into cycle engine
6. **Cache** (`ketu.cache.*`) — Ephemeris caching only, fix operator precedence bug

**Critical patterns:**
- **Explicit public API surface**: Only export via `__all__`, anything not exported can change
- **Structured array returns**: All calculations return NumPy structured arrays with named fields
- **Scalar + vector polymorphism**: Functions accept single or array inputs, return matching shape
- **Named constants**: Domain values (CONJUNCTION=0.0, DEFAULT_ORB=8.0) centralized
- **Explicit validation**: Fail fast with contextual error messages before swisseph crashes

**Anti-patterns to avoid:**
- Object-oriented wrappers around calculations (functional approach better for NumPy)
- Global configuration state (explicit parameters only)
- Mixed return types (always structured arrays)
- Deep module hierarchies (flat public API via `__init__.py`)

**Module removal strategy:** Export modules (chart, icalendar) must be deprecated properly. Either release 0.5.0 with deprecation warnings first, OR provide extensive migration guide in CHANGELOG/UPGRADING.md. Test that old modules don't import after fresh venv wheel install.

### Critical Pitfalls

The top 7 pitfalls represent release-blocking issues. All must be addressed before 1.0.0.

1. **Breaking Public API Without Deprecation Path** — Users upgrade 0.4.0→1.0.0, code breaks with ImportError. Removed export modules need stubs with helpful error messages and migration guide. Create UPGRADING.md with before/after examples.

2. **SemVer Confusion - Users Expect Stability After 1.0** — Scientific libraries are extra sensitive because users cache results. Fix ALL known bugs before 1.0 (operator precedence in cache, aspect non-determinism). Document behavior changes in "Correctness Fixes" CHANGELOG section. Commit to strict SemVer: 1.x.y = bug fixes only, 2.0 for breaking changes.

3. **Hidden Dependencies Fail at Runtime** — Pandas import hidden in `aspects/timelines.py` causes runtime ImportError. Remove Pandas entirely—rewrite timelines to use CYCLE_DTYPE structured arrays. Test install in clean venv before release.

4. **Removing Modules from PyPI Package Without Proper Metadata** — Old `.pyc` files may persist after upgrade. Test clean install from wheel in fresh venv. Verify removed modules fail to import. Document upgrade path: `pip uninstall ketu && pip install ketu==1.0.0`.

5. **Test Coverage Number Hides Critical Gaps** — 70% overall can hide 0% coverage in critical modules. Set per-module targets: cycles/cache/aspects >85%, not just overall 70%. Prioritize failure mode tests (invalid inputs, edge cases, non-determinism).

6. **Complex Number Math - Precision Loss in Angle Wrapping** — Floating point errors compound through trig chains. Use epsilon comparisons (1e-6°) not exact equality. Test angles near 0°/360° boundary. Document precision guarantees (~1e-6 degrees sufficient for astrology, not astronomy).

7. **Platform-Specific Floating Point Differences** — Tests pass on Linux, fail on Windows/macOS due to BLAS differences. Use `numpy.testing.assert_allclose` with tolerances, not `==`. Test matrix: [Ubuntu, Windows, macOS] × [Python 3.11, 3.12, 3.13].

**Additional moderate pitfalls:** Wheel vs source distribution inconsistencies, type hints broken after module removal, PyPI metadata outdated, changelog vague, no rollback strategy (release 1.0.0rc1 first), version number drift across files.

## Implications for Roadmap

Based on research, recommended phase structure reflects consolidation workflow, not feature development.

### Phase 1: API Surface Cleanup
**Rationale:** Must define what's public before anything else. Breaking changes acceptable now, not after 1.0 release.
**Delivers:** Clean `__all__` exports, explicit public API, removed anti-features
**Addresses:** Table stakes feature "Clean __all__ exports", anti-features removal (chart/icalendar)
**Avoids:** Pitfall #1 (breaking API), Pitfall #4 (module removal)
**Components:** Audit all modules, define public API in `__init__.py`, remove export modules with stubs, create UPGRADING.md
**Research flag:** Standard patterns (Python `__all__` well-documented), skip research-phase

### Phase 2: Correctness Fixes
**Rationale:** Fix known bugs BEFORE 1.0 release. Behavior changes acceptable now (documented as "Correctness Fixes").
**Delivers:** All CONCERNS.md bugs resolved (cache operator precedence, aspect non-determinism)
**Addresses:** Pitfall #2 (SemVer stability expectations)
**Components:** Fix cache logic bug, fix aspect vectorization, add regression tests for each bug
**Research flag:** Skip research-phase (bugs already documented in CONCERNS.md)

### Phase 3: Dependency Cleanup
**Rationale:** Remove hidden Pandas dependency before release. Pandas forces users into heavier dependency tree.
**Delivers:** Pure NumPy library (swisseph + NumPy only)
**Addresses:** Pitfall #3 (hidden dependencies), stack recommendation (NumPy-only philosophy)
**Implements:** Rewrite `aspects/timelines.py` to use CYCLE_DTYPE instead of DataFrame
**Avoids:** Runtime ImportError for undeclared dependencies
**Research flag:** Skip research-phase (CYCLE_DTYPE already exists, straightforward rewrite)

### Phase 4: Test Coverage Hardening
**Rationale:** 70% overall misleading if critical modules untested. Target per-module coverage.
**Delivers:** Cycles/cache/aspects >85% coverage, edge cases tested, platform tests added
**Addresses:** Pitfall #5 (coverage gaps), Pitfall #6 (precision), Pitfall #7 (platform differences)
**Components:** Write tests for cache (0% → 85%), cycles (0% → 90%), update assertions to `assert_allclose`, add 0°/360° boundary tests
**Research flag:** Skip research-phase (standard pytest patterns)

### Phase 5: Complex Integration
**Rationale:** Complex number representation exists but not fully integrated. Two parallel systems create confusion.
**Delivers:** Unified cycle engine using complex math internally, degrees externally
**Addresses:** Differentiator feature (complex number representation), performance optimization
**Implements:** Full integration of `complex.py` and `resonance.py` into `cycles/calculator.py`
**Avoids:** Architectural fragility from parallel systems
**Research flag:** Needs research-phase (complex math integration patterns, performance optimization techniques)

### Phase 6: Documentation & Type Checking
**Rationale:** Table stakes for 1.0. NumPy-style docstrings, type hints enforcement, precision guarantees.
**Delivers:** Comprehensive docstrings with examples, mypy passing in strict mode, accuracy docs
**Addresses:** Multiple table stakes features (docstrings, type hints, numerical accuracy docs, examples)
**Components:** Write/update docstrings for all public functions, add mypy to CI, document precision limits
**Research flag:** Skip research-phase (NumPy docstring format well-documented, standard mypy config)

### Phase 7: Release Preparation
**Rationale:** Testing wheel install, PyPI metadata, changelog formatting, release candidate before final.
**Delivers:** 1.0.0rc1 tested, then 1.0.0 final published to PyPI + GitHub release
**Addresses:** Pitfall #4 (module removal verification), Pitfall #8 (wheel vs source), Pitfall #10 (PyPI metadata), Pitfall #11 (changelog), Pitfall #12 (rollback strategy)
**Components:** Build wheel + sdist, test fresh venv install, update pyproject.toml metadata, release 1.0.0rc1, wait for feedback, release 1.0.0 final
**Research flag:** Skip research-phase (standard Python packaging workflow)

### Phase Ordering Rationale

- **API first**: Can't finalize tests/docs until public API is defined. Breaking changes must happen before 1.0.
- **Bugs second**: Correctness fixes change behavior—acceptable during consolidation, not after release.
- **Dependencies third**: Removing Pandas early prevents accidental new usage during later phases.
- **Tests fourth**: Can't write comprehensive tests until API stable and bugs fixed.
- **Integration fifth**: Complex math integration is optional enhancement, comes after table stakes.
- **Docs sixth**: Write docs after API/behavior finalized, before release.
- **Release last**: All validation checks before PyPI publish.

**Dependencies:**
- Phase 2-7 all depend on Phase 1 (API must be defined first)
- Phase 6 depends on Phase 1-3 (can't document unstable API)
- Phase 7 depends on all previous (release is final validation)

### Research Flags

**Phases needing research-phase:**
- **Phase 5 (Complex Integration)**: Complex math integration patterns, vectorization of ResonanceField calculations, performance optimization techniques. Domain is niche (astronomical cycles for finance), may need specialized research.

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (API Cleanup)**: Python `__all__` exports, module removal well-documented
- **Phase 2 (Correctness Fixes)**: Bugs already identified in CONCERNS.md, straightforward fixes
- **Phase 3 (Dependency Cleanup)**: NumPy structured arrays standard pattern
- **Phase 4 (Test Coverage)**: pytest, assert_allclose, coverage.py standard tools
- **Phase 6 (Documentation)**: NumPy docstring format, mypy configuration documented
- **Phase 7 (Release Prep)**: Python packaging (build, twine) established workflow

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing stack optimal for domain. NumPy+swisseph is industry standard for offline astronomical calculations. No changes needed to production dependencies. Development tooling additions (ruff, mypy) are standard Python tools. |
| Features | MEDIUM | Based on established Python scientific library conventions (NumPy, SciPy patterns). No web sources accessed due to permissions, but practices are well-documented in NEPs, SPEC guidelines. Verification needed: 2026 best practices evolution, latest NumPy typing conventions. |
| Architecture | HIGH | NumPy API design patterns, SciPy module organization, functional programming principles well-established. Patterns based on mature scientific Python projects. Current Ketu architecture already follows these patterns, consolidation reinforces them. |
| Pitfalls | HIGH | Codebase-specific pitfalls from direct CONCERNS.md analysis. Python packaging pitfalls from established PEPs (440, 517, 621). NumPy floating point pitfalls from documented standards. Complex number precision based on general floating point knowledge (medium confidence on domain-specific nuances). |

**Overall confidence:** HIGH

Research based on:
- Existing Ketu codebase analysis (CONCERNS.md, PROJECT.md, code structure)
- Python packaging standards (PEP 621, PEP 517, PEP 440, Semantic Versioning 2.0)
- NEP 29 (NumPy Enhancement Proposal 29 for Python version support)
- Scientific Python Ecosystem Coordination (SPEC) guidelines
- NumPy/SciPy API design patterns from mature projects
- Keep a Changelog format standard

### Gaps to Address

**NumPy 1.x vs 2.x compatibility:** Research recommends supporting both (Option B: Flexible). During Phase 3, validate approach—test both NumPy 1.x and 2.x in CI matrix. May need compatibility shims if breaking changes affect Ketu.

**Complex math precision limits:** Research identified floating point precision pitfall (1e-6 degrees). During Phase 5 integration, empirically measure precision loss through complex math pipeline. Document actual limits based on testing, not theoretical estimates.

**Performance benchmarks:** Differentiator feature identified but not detailed. During post-1.0 work, benchmark Ketu vs skyfield/astropy for common operations (planetary positions, aspect detection). Document specific use cases where Ketu is faster.

**Property-based testing:** Identified as high-value but deferred post-1.0. After 1.0 release, evaluate Hypothesis for testing cycle invariants (e.g., full moon always ~180°, conjunction always ~0°). Would catch edge cases unit tests miss.

**Platform-specific BLAS differences:** Research identified risk but didn't quantify magnitude. During Phase 4, measure actual differences across Ubuntu/Windows/macOS. Set tolerances based on empirical data, not assumptions.

**Deprecation strategy for exports:** Two options: (1) Release 0.5.0 with deprecation warnings first, OR (2) skip to 1.0.0 with extensive migration guide. During Phase 1, decide based on user base size. If many external users, do 0.5.0 first. If only Solaris ecosystem, skip to 1.0.0 with guide.

**Type stub generation:** Research mentions `py.typed` marker but didn't detail stub generation. Verify during Phase 6 that type stubs are included in wheel distribution. Test with mypy from external project importing ketu.

## Sources

### Primary (HIGH confidence)

**Codebase Analysis:**
- `.planning/codebase/CONCERNS.md` — Known bugs, gaps, performance issues, technical debt
- `.planning/PROJECT.md` — Project scope, validated features, constraints, key decisions
- `CHANGELOG.md` — Version history, SemVer claims, Keep-a-Changelog format usage
- `pyproject.toml` — Current dependencies, metadata, package structure
- `ketu/__init__.py` — Export structure, optional dependencies, version handling

**Python Standards:**
- PEP 440 (Version Identification and Dependency Specification) — Semantic versioning for Python
- PEP 517 (Build System Interface) — Modern Python package building
- PEP 621 (Project Metadata in pyproject.toml) — Standard metadata format
- NEP 29 (NumPy Enhancement Proposal 29) — Python version support policy
- Semantic Versioning 2.0.0 (semver.org) — Version bump rules for breaking changes
- Keep a Changelog (keepachangelog.com) — Changelog format standard

**Scientific Python Ecosystem:**
- NumPy Enhancement Proposals (NEPs) — NumPy API design patterns, version support
- Scientific Python Ecosystem Coordination (SPEC) guidelines — Cross-project standards
- NumPy Testing Guidelines — `assert_allclose`, tolerance-based floating point comparison
- SciPy Developer Guide — Platform testing, numerical precision, module organization

### Secondary (MEDIUM confidence)

**Established Practices:**
- Python Packaging User Guide (packaging.python.org) — Official PyPI packaging standards
- NumPy/SciPy contributor guides — Docstring format, testing standards
- Observation of mature scientific Python projects (scipy, scikit-learn, astropy) — API patterns

**Domain Knowledge:**
- swisseph documentation — Ephemeris calculation library, industry standard
- Astronomical software standards (Astropy Coordination Committee) — Relevant for ephemeris libraries
- Floating point arithmetic standards — IEEE 754, precision loss in trig operations

### Tertiary (LOW confidence)

**Inference Required:**
- Complex number precision for astronomical calculations — General floating point knowledge applied to domain
- Performance characteristics of vectorized NumPy vs loop-based Python — Known pattern but not measured for Ketu
- 2026 Python packaging best practices evolution — Practices may have evolved since knowledge cutoff

**Verification needed:**
- Current year (2026) Python/NumPy best practices — Cross-reference with official docs
- Specific competitor analysis — Examine skyfield, astropy actual API patterns (not accessed)
- Latest NumPy 2.x typing conventions — `numpy.typing` evolution since 2024

---
*Research completed: 2026-02-12*
*Ready for roadmap: yes*
