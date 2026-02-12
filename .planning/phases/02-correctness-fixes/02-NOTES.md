# Phase 2: Correctness Fixes - Notes

Bugs discovered during real-world usage of Ketu in Solaris.

## Bug: Moon velocity inconsistency

**Source:** User report (2026-02-12) from Solaris integration
**Symptom:** `vlong()` returns inconsistent velocity values for the Moon
**Impact:** Downstream cycle calculations in Solaris rely on accurate lunar velocity

## Bug: vlong() / long() naming confusion

**Source:** User report (2026-02-12) from Solaris integration
**Symptom:** Claude (in Kala/Solaris context) confused `vlong()` with `long()`, interpreting `vlong` as "longitude value" instead of its actual meaning "longitude velocity" (degrees/day)
**Root cause:** Function naming is ambiguous — `vlong` prefix `v` could mean "value" or "velocity"
**Impact:** Incorrect function calls in downstream code when Claude assists with Kala integration

### Clarification
- `long()` = **longitude** (position in degrees)
- `vlong()` = **velocity of longitude** (degrees/day)

---

*Notes added: 2026-02-12*
