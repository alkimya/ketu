---
phase: 14
phase_name: chart-abstraction-foundation
audit_date: 2026-05-09
auditor: gsd-secure-phase
asvs_level: 1
block_on: critical
declared_threats: 0           # No <threat_model> in PLANs; SUMMARYs 14-03 / 14-05 explicit "Threat Flags: None"
verified_threats: 6           # Independent verification of the 6 concerns surfaced in the audit constraints
threats_open: 0
unregistered_flags: 0
status: SECURED
---

# Phase 14 — Security Audit Report

**Audit scope:** the six concrete attack surfaces called out in the audit
constraints, plus the declared "zero threats" claim from SUMMARYs 14-03 /
14-05. Phase 14 is a pure NumPy backend library — no UI, no CLI, no server,
no auth, no FS writes, no network. The only consumer is downstream Python
code (Kala via KetuAdapter; future Phases 16/17/18/19).

**Verdict:** SECURED. Every claimed mitigation is present in the code and
empirically verified by triggering real calls. No declared threat is open;
no new attack surface introduced. The "zero threats" claim from the
SUMMARYs holds up under independent verification.

---

## 1. Declared threat register

The phase planning artifacts (`14-01-PLAN.md` … `14-05-PLAN.md`,
`14-CONTEXT.md`, `14-RESEARCH.md`) contain **no** `<threat_model>` block.
SUMMARYs 14-03 and 14-05 explicitly carry:

> **Threat Flags:** None — this plan is purely additive composition (no
> new endpoints, auth surfaces, file-access patterns, or schema changes).

SUMMARYs 14-01, 14-02 and 14-04 do not carry a Threat Flags section at
all (silent on threats). Cross-cutting v1.2 constraint
"AGPL boundary — runtime imports of `ketu/charts/` must not introduce
swisseph" is the only security-shaped invariant tracked in CONTEXT.md
(line 530).

The declared register is therefore empty. The audit independently
verifies the six concrete concerns called out in the audit prompt.

## 2. Threat verification — six concrete surfaces

### T-1 — AGPL boundary: `ketu/charts/` does not load swisseph at runtime

**Severity if open:** CRITICAL (project licence boundary; Swiss Ephemeris is
AGPL, ketu ships under MIT).

**Verification method:** static grep + dynamic ratchet (real-call trigger
before checking `sys.modules`).

**Static evidence:**
```
$ grep -nE 'swisseph|swe_|^import swe|from swe' ketu/charts/*.py
ketu/charts/api.py:14:Both are pure NumPy. No swisseph runtime import — …
```
Single hit; it's a docstring reference, not an import statement. No
`import swisseph`, no `import swe`, no `from swisseph import …` anywhere
in `ketu/charts/__init__.py`, `ketu/charts/core.py`, `ketu/charts/api.py`.

**Dynamic evidence (this audit, 2026-05-09):**
```
import sys
import ketu.charts
from ketu.charts import compute_chart, is_day_chart
chart = compute_chart(2451545.0, 48.86, 2.35)         # full pipeline
result = is_day_chart(2451545.0, 48.86, 2.35)         # sect helper
swe_modules = [m for m in sys.modules
               if 'swisseph' in m.lower() or m.startswith(('swe.','swe'))
                  or m == 'swe']
# → []
```
After triggering both public functions, zero swisseph-shaped modules are
loaded. The dependency chain `compute_chart → calculate_houses →
calc_planet_position_batch → ephemeris.{time,orbital,coordinates,planets}`
is itself pure-numpy; the docstring references to "pyswisseph" /
"swehouse.c" found in `ketu/houses/*.py`, `ketu/ephemeris/*.py` are
attributions/cross-check notes, not imports (manual line-by-line review
2026-05-09).

**Ratchet tests pinning this in CI:**

| Test | File:line | Catches lazy import? |
|---|---|---|
| `test_no_runtime_swisseph_import` | `tests/charts/test_dtype.py:238-254` | No (import-time only) |
| `test_compute_chart_no_runtime_swisseph_import` | `tests/charts/test_compute_chart.py:253-273` | No (import-time only) |
| `test_no_runtime_swisseph_import_via_is_day_chart` | `tests/charts/test_is_day_chart.py:324-344` | **Yes** — calls `is_day_chart(...)` first, then checks `sys.modules` |

The third ratchet (`test_is_day_chart.py:324-344`) explicitly triggers
`is_day_chart(2451545.0, 48.86, 2.35)` *before* the `sys.modules` check
(line 334). Lazy/deferred imports inside `is_day_chart`,
`compute_ascmc`, `calc_planet_position_batch`, or any of the orbital-math
modules they reach would surface here. Stronger than a pure import-time
ratchet.

**Disposition:** **CLOSED — mitigation present and pinned.** Zero
swisseph in the production runtime path; three independent CI ratchets
cover both static and dynamic lazy-import surfaces.

---

### T-2 — Input validation: numerical edge inputs (NaN, Inf, out-of-range lat)

**Severity if open:** LOW (no security boundary crossed in a backend
library; risk is silent NaN propagation through downstream consumers).

**Verification method:** dynamic black-box test on `compute_chart` with
default `polar_fallback="raise"` and `polar_fallback="porphyry"`, on
`is_day_chart`.

**Empirical results (2026-05-09):**

| Input | `compute_chart` (raise) | `compute_chart` (porphyry) | `is_day_chart` |
|---|---|---|---|
| `jd=NaN` | accepts; `asc=NaN`, `body_lons[0]=NaN` (NaN propagates) | accepts; same | returns `False` (clean bool) |
| `lat=NaN` | accepts; `asc=NaN` (NaN propagates) | accepts; same | returns clean bool |
| `jd=+Inf` | accepts; `asc=NaN` (Inf → NaN through arctan2) | same | returns clean bool |
| `lat=+Inf` | **raises `HighLatitudeError`** | accepts; `asc≈0.54°` (Porphyry math runs) | returns clean bool (no raise — D-15) |
| `lat=91` | **raises `HighLatitudeError`** ("latitude 91.0000° exceeds polar circle 66.5607°") | accepts; runs Porphyry | returns clean bool |
| `lat=1000` | **raises `HighLatitudeError`** | accepts | returns clean bool |
| `lat=-91` | **raises `HighLatitudeError`** | accepts | returns clean bool |

Behavior is bounded. NaN/Inf do not cause crashes, infinite loops, or
memory blowups. They propagate as NaN through fp64 IEEE-754 arithmetic
(documented industry-standard behavior). Out-of-range latitudes are
caught early at the polar-circle gate inside `calculate_houses` when
`polar_fallback="raise"`. With `polar_fallback="porphyry"` the helper
runs to completion regardless of latitude (consistent with D-11
pass-through and D-15 internal-Porphyry contracts).

**Disposition:** **CLOSED — bounded behavior.** No silent crash, no
hang, no memory leak. NaN propagation is the explicit IEEE-754 contract;
out-of-range lat is gated at `polar_fallback="raise"` (the default).
Consumers who want NaN-rejection at the call site can layer their own
validator above `compute_chart`; this is the right design boundary for a
backend library.

---

### T-3 — Input validation: `system` parameter (string injection / overflow)

**Severity if open:** LOW (no FS, no shell, no SQL, no template
rendering downstream of `chart["system"]`).

**Verification method:** dynamic black-box test with adversarial
strings; static review of every consumer of `chart["system"]`.

**Empirical results (2026-05-09):**

| `system=` | Outcome |
|---|---|
| `"A" * 100000` (100k chars) | `ValueError: unknown house system 'AAAA…'` (registry whitelist rejects) |
| `"../../etc/passwd"` | `ValueError: unknown house system '../../etc/passwd'; available: ['koch', 'placidus', 'porphyry']` |
| `"placidus\x00\x01\x02"` | `ValueError: unknown house system …` |
| `"placidus" + chr(0) + "extra"` | `ValueError: unknown house system …` |
| `chr(0) * 5` (5 NULs) | `ValueError: unknown house system …` |
| `"<script>alert(1)</script>"` | `ValueError: unknown house system …` |

The `system` parameter goes through `calculate_houses` →
`ketu.houses.registry.resolve(system)` which is a whitelist check
against the registered system names (`{placidus, koch, porphyry}`). All
adversarial strings fail the whitelist before reaching any downstream
consumer. No path-like, control-char, or oversized string survives long
enough to be stored in the U10 `chart["system"]` field.

**Static review of `chart["system"]` consumers:**
```
$ grep -rn 'chart\["system"\]\|system_field\|HOUSES_DTYPE.*system' ketu/ tests/charts/
```
returns only NumPy structured-array reads (positional indexing into the
U10 field) and string equality comparisons. No `os.path.join`, no
`open()`, no `subprocess`, no `eval`, no SQL, no template rendering
consumes `chart["system"]`. Even in the hypothetical case where a
malicious string passed the whitelist, NumPy's U10 would silently
truncate to 10 codepoints (e.g. `"../../etc/passwd"` → `"../../etc/"`),
which is harmless because no consumer treats this field as a path.

**Disposition:** **CLOSED — whitelist + truncation defense in depth.**
Any adversarial `system` string is rejected at the registry boundary;
the U10 field caps at 10 codepoints; no downstream consumer treats the
field as a filesystem path or shell argument.

---

### T-4 — DoS via massive broadcast (`jd=np.zeros(10**9)`)

**Severity if open:** LOW (caller's problem in a backend library; no
attacker-controlled input boundary in v1.2; relevant only if Phase
16/17/18/19 ever exposes `compute_chart` behind a network endpoint).

**Verification method:** static review for early-bound checks; empirical
benchmark on a moderate-size batch.

**Empirical evidence:**
- Source review: `compute_chart` does not check `jd_b.size` before
  allocating `np.empty(leading_shape, dtype=CHART_DTYPE)` (~1349 bytes
  per element per RESEARCH.md §2 sizing). For 10⁹ elements the
  allocation would attempt ~1.3 TB and fail with `MemoryError` /
  `numpy.core._exceptions.MemoryError`. No infinite loop, no silent
  hang.
- Benchmark this audit: 1,000-element batch completes in ~464 ms on the
  audit machine; well within ML-batch operational profile (synastry /
  composite / solar-return batches are typically in the 10²–10³ range
  per RESEARCH.md §3, D-16).
- No documented MAX_SHAPE / MAX_SIZE / `if jd_b.size > …: raise` guard
  (`grep` confirms).

**Disposition:** **CLOSED for v1.2** — accepted risk, documented here.

This is the *caller's* memory budget to manage. The library is a pure
NumPy primitive; bounding the input shape is policy, not mechanism, and
belongs above the library. Should Phase 16/17/18/19 (or any future
consumer) expose `compute_chart` behind an attacker-reachable surface,
that consumer must layer its own input-size check (e.g.
`if size > MAX: raise`) before the call. **Recorded as accepted risk in
this report; not a blocker for Phase 14.**

---

### T-5 — Numerical fingerprinting via `HighLatitudeError`

**Severity if open:** NEGLIGIBLE (no auth context, no tenant separation,
no secrets in the error path).

**Verification method:** review the exception message and call graph.

**Evidence:**
- `HighLatitudeError` message: `"latitude 91.0000° exceeds polar circle
  66.5607° for house system 'placidus'; pass polar_fallback='porphyry'
  to fall back."` (verified empirically). Contains only inputs the
  caller already knows (their own latitude, the system they passed)
  plus the well-known polar-circle constant.
- Phase 14 has no notion of "user", "tenant", "secret", or "internal
  state to leak". The error message is identical for every caller.
- Latitude enumeration is irrelevant: the polar circle is a
  deterministic, time-dependent astronomical constant
  (`polar_circle(jd)`), not derived from any caller-private value.

**Disposition:** **CLOSED — no information disclosure surface.** The
exception messages reveal only deterministic public-domain astronomical
constants and the caller's own inputs.

---

### T-6 — Path-like injection via `system` (truncation / downstream FS use)

**Severity if open:** LOW (covered by T-3 whitelist; this entry pins
the orthogonal "what if someone bypasses the whitelist later"
follow-on concern).

**Verification method:** dependency-graph review for any code that
treats `chart["system"]` (post-storage in CHART_DTYPE) as a filesystem
path or shell argument.

**Evidence:**
- Whitelist at the boundary (T-3): no path-like string can reach the
  CHART_DTYPE store in the current code. Verified.
- Truncation: even if T-3 ever regressed, the `U10` field caps at 10
  codepoints. `"../../etc/passwd"` → `"../../etc/"`. Still harmless
  because…
- No downstream consumer of `chart["system"]` does FS/shell I/O. Static
  review of `ketu/`, `tests/`, and the planned-but-future Phase
  16/17/18/19 plans (in `.planning/phases/`) shows `chart["system"]` is
  read only for:
  * structured-array equality assertions in tests
  * docstring/example renders
  * round-trip identity checks
  No `open(chart["system"])`, no `os.path.join(…, chart["system"])`, no
  `subprocess.run([…, chart["system"]])`. Any future consumer that does
  FS I/O on this field must layer its own validator — this is the same
  right-design-boundary argument as T-4.

**Disposition:** **CLOSED — whitelist + truncation + zero downstream
FS use.** Defense in depth verified.

---

## 3. Summary table

| Threat | Category | Disposition | Evidence |
|---|---|---|---|
| T-1 — AGPL runtime boundary | Licence/supply-chain | mitigate (CLOSED) | `tests/charts/test_dtype.py:238-254`, `tests/charts/test_compute_chart.py:253-273`, `tests/charts/test_is_day_chart.py:324-344` (with real-call trigger); empirical `sys.modules` check 2026-05-09 |
| T-2 — Numeric edge inputs | Input validation | mitigate (CLOSED) | Empirical NaN/Inf/out-of-range matrix; `HighLatitudeError` gate at default `polar_fallback="raise"` (`ketu/houses/api.py` polar check) |
| T-3 — Adversarial `system` strings | Input validation | mitigate (CLOSED) | Registry whitelist rejection of all adversarial strings (verified empirically); U10 truncation as second-line defense |
| T-4 — DoS via massive broadcast | Resource exhaustion | accept | No bound check in `compute_chart`; v1.2 accepted risk; future network-exposed consumers must layer their own input-size check (recorded in §4 Accepted Risks) |
| T-5 — Fingerprinting via exceptions | Information disclosure | mitigate (CLOSED) | Exception messages contain only caller-known inputs + public astronomical constants; no auth/tenant context exists in Phase 14 |
| T-6 — Path-like via `system` | Injection | mitigate (CLOSED) | T-3 whitelist + U10 cap + zero downstream FS/shell consumers |

## 4. Accepted Risks

### AR-1 — Unbounded input shape on `compute_chart` (T-4)

**Risk:** A caller passing `jd=np.zeros(10**9)` causes `np.empty(…,
dtype=CHART_DTYPE)` to attempt ~1.3 TB allocation and fail with
`MemoryError`. No DoS amplification, no silent hang, just a hard fail
on the caller side.

**Why accepted for v1.2:**
1. Phase 14 is a pure NumPy backend library; no attacker-controlled
   input boundary exists in v1.2.
2. The only consumers are downstream Python code (Kala via
   KetuAdapter; future Phases 16/17/18/19) — all in-process Python,
   not network-reachable.
3. Bounding input shape is policy, not mechanism; it belongs above
   the library. Encoding a magic constant in `compute_chart` would
   be wrong-layer.

**Trigger to re-evaluate:** any phase that exposes `compute_chart` (or
`is_day_chart`) behind a network surface, RPC endpoint, or
attacker-reachable input. That phase MUST layer an input-size check
before the call. To be reviewed at Phase 16 (synastry) planning if
batched-API is ever surfaced.

**Owner:** Sophie / future phase planner.
**Status:** open as accepted risk; not a blocker for Phase 14.

## 5. Unregistered Flags

None. Nothing in the implementation surfaces new attack surface beyond
what the audit's six surfaces cover. SUMMARYs 14-03 and 14-05 carry
explicit "Threat Flags: None" sections; SUMMARYs 14-01, 14-02, 14-04 do
not carry a Threat Flags section but the underlying changes are
likewise composition-only (no new endpoints, no new file access, no new
schema, no new auth surface, no new dependency).

## 6. Audit Methodology

- **Static analysis:** `grep -nE 'swisseph|swe_|^import swe|from swe'`
  across `ketu/charts/`, `ketu/houses/`, `ketu/ephemeris/`,
  `ketu/aspects/`, `ketu/calculations.py`. Manual review of every hit
  to confirm docstring vs. import.
- **Dynamic analysis:** `python -c` invocations triggering real calls
  to `compute_chart` and `is_day_chart`, then probing `sys.modules`.
- **Adversarial inputs:** NaN, Inf, ±91°, ±1000°, 100k-char string,
  `"../../etc/passwd"`, `\x00\x01\x02` control chars, `<script>` HTML
  injection, NUL-only string.
- **Source review:** read all 5 SUMMARY files, REVIEW.md, REVIEW-FIX.md,
  VERIFICATION.md, UAT.md, plus `ketu/charts/__init__.py`,
  `ketu/charts/core.py`, `ketu/charts/api.py`, and the four test files
  in `tests/charts/`.
- **Test execution:** `pytest tests/charts/ --no-cov` → 134 passed
  (matches UAT.md and PHASE-CLOSE record).

## 7. Conclusion

**SECURED.** The "zero declared threats" claim from SUMMARYs 14-03 and
14-05 holds up under independent verification. No declared mitigation is
absent from the code; no new attack surface introduced; no information
disclosure or injection path identified. The single accepted risk
(unbounded input shape, AR-1) is the correct design boundary for a
pure-NumPy backend library and is documented for future
network-exposed consumers.

The phase is safe to ship and to be consumed by downstream Phases
16/17/18/19.

---

*Audit: 2026-05-09 — gsd-secure-phase — Sophie Chen persona*
*Tests: 134/134 charts passing, 858/858 full suite (UAT.md cross-ref)*
*ASVS Level: 1 (backend library — no auth/session/transport surface)*
