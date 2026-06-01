---
phase: 27-release-1-3-0
plan: 01
status: complete
completed: 2026-06-01
requirements: [REL-10]
---

# Summary: 27-01 — Version Bump + CHANGELOG + UPGRADING (REL-10)

## What was built

Bumped Ketu to **1.3.0** and finalized all release documentation so the
Wave-2 release ceremony can tag a commit whose docs are publication-ready.
No `ketu/` source logic changed — only the two version strings + docs.

### Task 1 — Version bump (commit `a9cf350`)
- `pyproject.toml:7` → `version = "1.3.0"`
- `ketu/__init__.py:57` → `__version__ = "1.3.0"`
- `docs/source/conf.py` deliberately **NOT** touched (already at 1.3.0 from
  Phase 25 — editing it would be a spurious no-op diff, RESEARCH Pitfall 8).
- Sync gate green: `pytest tests/test_version.py` → 2 passed
  (`ketu.__version__ == importlib.metadata.version("ketu") == "1.3.0"`).

### Task 2 — CHANGELOG merge + Chiron entries (commit `2658264`)
- Merged the two unversioned sections into ONE dated `## [1.3.0] - 2026-06-01`.
- Deleted the `## [Unreleased]` header; no `[1.3.0] - Unreleased` remains.
- Moved in: `### Changed` BREAKING `angular_separation` direction-fix
  (body1→body2, Kala `360 - old`) + `### Fixed` `datetime64` cycle-cache bullet.
- **ADDED** the previously-missing Chiron `### Added` bullet (14th body,
  body_id=13, embedded Chebyshev `.npz`, pure NumPy, max |Δλ| = 0.005695°
  over 1950-2050) and the Chiron `### Changed` BREAKING contract note
  (CHART_DTYPE (13,)→(14,) / (13,13)→(14,14), synastry axis 15→16).
- `fr/CHANGELOG.md`: synthesized French `## [1.3.0] - 2026-06-01` section
  (Ajouts / Modifié / Corrigé) translating the same bullets.

### Task 3 — UPGRADING Chiron section + README verify (commit `4251709`)
- Added a `### Chiron added as body_id=13 (14th body)` sub-section inside
  `## v1.2 -> v1.3`, BEFORE the existing aspect-engine section: CHART_DTYPE
  shape-expansion table, Kala/downstream recompute-caches guidance, the
  pure-NumPy import example, and the synastry 15→16 note.
- README `## What's New in v1.3.0` **verified complete** (covers Chiron +
  data-driven aspect engine + breaking default aspect set + full French docs)
  — **no change made**, per plan expectation.

## Verification

| Gate | Result |
|------|--------|
| `pytest tests/test_version.py` | 2 passed |
| Full suite `pytest tests/ -q` | 1399 passed, 2 skipped, **100% coverage** |
| CHANGELOG: 1 dated [1.3.0], 0 [Unreleased], 0 [1.3.0]-Unreleased | ✓ |
| CHANGELOG: Chiron + angular_separation + datetime64 present | ✓ |
| fr/CHANGELOG: dated [1.3.0] + Chiron | ✓ |
| UPGRADING: Chiron section + shape table + import example | ✓ |
| conf.py untouched | ✓ (clean diff) |
| Both changelogs date-stamped 2026-06-01 (today UTC) | ✓ |

## Key files

### Modified
- `pyproject.toml` — version 1.2.0 → 1.3.0
- `ketu/__init__.py` — __version__ 1.2.0 → 1.3.0
- `CHANGELOG.md` — single dated [1.3.0] with all 5 item-groups
- `fr/CHANGELOG.md` — French [1.3.0] section
- `UPGRADING.md` — Chiron 13→14 positional-contract section added

### Verified-only (no change)
- `README.md` — What's New in v1.3.0 confirmed complete
- `docs/source/conf.py` — already 1.3.0, intentionally untouched

## Deviations / notes

- **GPG signing stall (environment, not plan):** `commit.gpgsign=true` + no
  TTY caused the Task-3 commit to fail repeatedly (`gpg: cannot open
  '/dev/tty'`). Tasks 1-2 had committed earlier on a then-warm gpg-agent
  cache that expired before Task 3. Resolved by the user unlocking the GPG
  cache; the Task-3 commit then signed cleanly (`4251709`). Content was fully
  written before the commit succeeded — no rework, only the commit was delayed.

## Commits

- `a9cf350` chore(27-01): bump version to 1.3.0 in both source-of-truth files
- `2658264` docs(27-01): merge CHANGELOG into one dated [1.3.0] and add Chiron entries
- `4251709` docs(27-01): add Chiron 13->14 positional-contract section to UPGRADING

REL-10 satisfied. Ready for 27-02 (PyPI publish ceremony).
