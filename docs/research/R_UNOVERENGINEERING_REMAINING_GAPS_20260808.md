# R_UNOVERENGINEERING_REMAINING_GAPS — Deep Research & Implementation Proposal

**AP Token**: `AP-RESEARCHER-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE

**Date**: 2026-08-08
**Author**: Sovereign Researcher (Jem Analyst — Polymathic Council)
**Status**: RESEARCH COMPLETE — awaiting implementation go/no-go
**Scope**: 6 remaining gaps from Web Claude audit (M7/M22, M14, M23, V-9, V-10, UO-6)
**Baseline commit**: `24857ca7` — *fix(un-overengineering): AnyIO thread-safety + M9 error integrity + M2 firewall*

---

## L1 — EXECUTIVE SUMMARY (read this if nothing else)

Six gaps were assigned. Direct codebase forensics **confirmed 4, expanded 2, and invalidated
much of 1**. More importantly, the investigation surfaced a **P0 regression introduced by the
most recently completed fix** that is silently destroying observability data right now.

| # | Gap | Audit said | Forensic reality | Verdict |
|---|-----|-----------|------------------|---------|
| **0** | **AnyIO metrics regression** | *(not in audit)* | 8+ prod call sites create un-awaited coroutines; writes silently lost; 154 tests failing | 🔴 **NEW P0 — BLOCKS ALL** |
| 1 | M7/M22 sovereignty | 1 hardcoded set | **5 divergent classifiers**; 73.6% of rows corrupt | 🔴 **CONFIRMED + WORSE** |
| 2 | M14 heritage contradiction | Doc conflict | **9 duplicate vet IDs**; `make heritage-vet` **does not exist** | 🟠 **ROOT CAUSE FOUND** |
| 3 | M23 pre-commit gate | Broken `rg` | Proven false-pass; **107 real violations**; entire pre-commit config **never runs** | 🔴 **CONFIRMED + WORSE** |
| 4 | V-9 IA2 freshness | No freshness check | Confirmed. Reusable `SovereignSigner` HMAC pattern already exists | 🟢 **CONFIRMED, low risk** |
| 5 | V-10 AppArmor | Unconfined | Confirmed. Host is **Ubuntu 25.10 / Podman 5.4.2**, not 24.04 | 🟡 **CONFIRMED, scope revised** |
| 6 | UO-6 library swaps | 5 swaps | **4 of 5 are phantom work** (libs not installed/used) | ⚪ **MOSTLY INVALID — descope** |

### The single most important finding

The audit's framing assumed a clean baseline. It is not clean. `make test` reports
**154 failed / 1599 passed / 56 skipped / 7 xfailed** (214s, measured 2026-08-08). The
dominant failure cluster is a **direct regression from completed fix #4** (AnyIO thread-safety):
`MetricsDB.record_*` methods were converted to `async def`, but callers were not updated.
Python creates a coroutine object, never awaits it, and **the database write never executes** —
with no exception raised. This is precisely the M23 "soft-failure" class the M23 gate exists
to prevent, and the M23 gate is itself broken, which is why nothing caught it.

**Recommended sequencing** (dependency-ordered, not priority-ordered):

```
GAP-0  AnyIO regression repair        ← BLOCKS EVERYTHING (data loss active)
  └─ GAP-3  M23 gate repair (AST)     ← prevents recurrence of GAP-0 class
       └─ GAP-1  Sovereignty unification (needs working metrics + honest gate)
            └─ GAP-2  M14 heritage reconciliation
                 ├─ GAP-4  V-9 IA2 freshness   (parallel-safe)
                 └─ GAP-5  V-10 AppArmor       (parallel-safe, needs Architect sudo)
GAP-6  UO-6  → DESCOPE to 1 real item (pybreaker)
```

**Total honest effort**: ~26–34 h. The audit's implied scope was ~40 h, but ~12 h of that
(UO-6) is phantom work, and ~8 h of newly-discovered work (GAP-0) was invisible to the audit.

---

## L2 — DETAILED DIALECTIC

Each gap below is triangulated through the Council of Four: **Architect** (systemic fit),
**Adversary** (failure modes), **Alchemist** (cross-domain synthesis), **Archivist** (documented truth).

---

## GAP-0 — AnyIO Metrics Regression (NEW, P0, BLOCKS ALL)

### 1. Executive Summary
The completed AnyIO thread-safety fix converted `MetricsDB.record_event/record_error/
record_breaker_transition/record_performance` to `async def`, but at least **8 production call
sites** still invoke them synchronously. Python constructs a coroutine and discards it — no
exception, no write, no log. Observability, sovereignty, and cost data are being **silently
dropped in production right now**. This must be repaired before any other gap, because GAP-1
depends on MetricsDB being trustworthy.

### 2. Research Findings (evidence-based)

**Direct measurement** (this session, commit `24857ca7`):

```
$ grep -n "async def record_" src/omega/observability/metrics_db.py
191:    async def record_event(
217:    async def record_error(
241:    async def record_breaker_transition(
263:    async def record_performance(
```

Un-awaited synchronous call sites:

| File | Line | Call |
|------|------|------|
| `src/omega/observability/otel_exporter.py` | 94 | `self._metrics_db.record_performance(` |
| `src/omega/observability/otel_exporter.py` | 105 | `self._metrics_db.record_event(` |
| `src/omega/observability/__init__.py` | 1029 | `metrics_db.record_event(` |
| `src/omega/observability/__init__.py` | 1102 | `metrics_db.record_performance(` |
| `src/omega/observability/token_ledger.py` | 77 | `obs.record_performance(` |
| `src/omega/oracle/backends/remote_provider.py` | 55 | `_metrics_db.record_performance(` |
| `src/omega/oracle/oracle.py` | 917 | `self.observability.record_performance(` |
| `src/omega/oracle/oracle.py` | 1025 | `self.observability.record_performance(` |

Observed test symptoms (`tests/test_metrics_db.py`):
```
E  TypeError: object of type 'coroutine' has no len()
E  TypeError: 'coroutine' object is not subscriptable
E  TypeError: 'NoneType' object is not subscriptable
E  assert 0 == 1        # ← the write never happened
```

Failure distribution across the suite (top clusters):
```
23  test_metrics_db.py          11  test_metrics_db_integration.py
20  test_oracle.py               9  test_model_gateway.py
17  unit/test_vault_core.py      9  test_library_fts_search.py
12  test_sovereign_loop.py       7  test_sqlite_vec_adapter.py
```
The `metrics_db` + `oracle` + `model_gateway` + `sovereign_loop` clusters (~66 failures) trace
to this single root cause. `vault_core` (17) is independent (relates to completed fix #3).

**Why no error is raised**: CPython emits a `RuntimeWarning: coroutine '...' was never
awaited` only at garbage-collection time, and only when warnings are not filtered. The project
runs pytest with 294 warnings already present, so the signal is buried. Reference: Python
docs, *Coroutines and Tasks* — "if you forget to await a coroutine, it will never run"
(https://docs.python.org/3/library/asyncio-task.html, accessed 2026-08-08).

### 3. Council Dialectic

- **Architect**: The mistake was converting a *leaf write path* to async without an adapter.
  The correct systemic shape is a **sync façade over an async core**: keep `record_*` callable
  from sync contexts, and route to the locked async implementation internally.
- **Adversary**: A naive "just add `await` everywhere" fix is a trap — several call sites
  (`otel_exporter`, `token_ledger`) are invoked from **sync** OpenTelemetry/atexit contexts
  where no event loop exists. Adding `await` there converts a silent-drop bug into a crash.
- **Alchemist**: This is the *same pathology* as GAP-1 (config declares truth, code ignores it)
  and GAP-3 (gate declares pass, reality differs). The unifying disease is **declared-vs-actual
  divergence**. Every fix in this report should add a *contract test* that asserts the actual,
  not the declared.
- **Archivist**: M1 mandates AnyIO and `anyio.to_thread.run_sync` for blocking I/O; M23
  forbids soft-failures. This regression violates M23 while attempting to satisfy M1. The
  resolution must satisfy both.

### 4. Implementation Proposal

**Strategy**: dual-surface API. Async core + explicit sync wrapper. No call site guesses.

```python
# src/omega/observability/metrics_db.py

from anyio.from_thread import start_blocking_portal
import anyio, sniffio

class MetricsDB:
    # ── async core (M1-compliant, lock-protected) ────────────────
    async def record_event(self, ...) -> None:
        async with self._lock:
            await anyio.to_thread.run_sync(self._write_event_sync, ...)

    # ── sync façade for non-async call sites ─────────────────────
    def record_event_sync(self, ...) -> None:
        """Blocking write for sync contexts (OTel exporter, atexit).

        M23: never swallows. Raises MetricsWriteError on failure.
        """
        try:
            sniffio.current_async_library()
        except sniffio.AsyncLibraryNotFoundError:
            pass          # no loop running → safe to block
        else:
            raise RuntimeError(
                "record_event_sync() called from async context; use `await record_event()`"
            )
        with start_blocking_portal() as portal:
            portal.call(self.record_event, ...)
```

**Steps**:
1. Add `record_*_sync()` façades for all 4 methods (~60 LOC).
2. Update the 8 call sites: async contexts (`oracle.py:917,1025`,
   `observability/__init__.py:1029,1102`) get `await`; sync contexts
   (`otel_exporter.py:94,105`, `token_ledger.py:77`, `remote_provider.py:55`) get `_sync`.
3. Add a **guard contract test** that fails the build if any `record_*` is called without
   `await` in an async def — implemented as an AST check reusing the GAP-3 scanner.
4. Re-run the affected clusters.

**Effort**: 5–7 h (2 h façade, 2 h call sites, 1 h guard test, 2 h test triage).
**Files**: `metrics_db.py`, `otel_exporter.py`, `observability/__init__.py`,
`token_ledger.py`, `remote_provider.py`, `oracle.py`, `tests/contract/test_metrics_db_await.py`.

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `start_blocking_portal` deadlock if called from a loop thread | Med | `sniffio` guard raises loudly instead (shown above) |
| Portal creation cost per call | Med | Batch: create one module-level portal at init for the OTel path |
| Fixing 66 tests masks a second root cause | Med | Fix in 2 passes; re-measure cluster counts between passes |
| Historical gap in metrics (data already lost) | **Certain** | Document lost window; do **not** backfill fabricated data (M23) |

### 6. Dependencies
None. This is the root. Everything else waits.

### 7. Acceptance Criteria
- [ ] `grep` finds zero un-awaited `record_*(` in `src/omega/`
- [ ] `tests/test_metrics_db.py` + `test_metrics_db_integration.py`: 34/34 pass
- [ ] Total failures drop from 154 → ≤ 90 (measured, not estimated)
- [ ] New contract test fails when an `await` is deliberately removed (mutation-verified)
- [ ] A live inference writes exactly one `performance` row (end-to-end verified)

---

## GAP-1 — M7/M22 Sovereignty Ratio Corruption

### 1. Executive Summary
The audit identified one hardcoded set. Forensics found **five mutually-inconsistent cloud
classifiers**, and **73.6% of all historical sovereignty rows are misclassified**. The fix is
to delete all five and derive classification from the single source of truth already present
and already correct: the `is_cloud` field in `config/providers.yaml`.

### 2. Research Findings

**Finding 2.1 — The config is already correct.** `config/providers.yaml` annotates every
provider accurately (`native-gguf/lmster/ollama → is_cloud: false`;
`antigravity/google/google-compat/openrouter/opencode-zen/cline/anthropic/xai/mock → true`).
**No config change is required.** The defect is purely code ignoring config.

**Finding 2.2 — Five divergent classifiers exist:**

| # | Location | Mechanism | Defect |
|---|----------|-----------|--------|
| 1 | `model_gateway.py:890` | Hardcoded set of 4 | Misses antigravity, anthropic, xai, google-compat |
| 2 | `observability/__init__.py:686` | Substring *local* denylist | `"native"`/`"local"` substrings → fragile |
| 3 | `otel_exporter.py:123` | Hardcoded set of 9 | Different membership from #1 |
| 4 | `remote_provider.py:387` | `startswith()` prefix set | Includes `antigravity` — **contradicts #1** |
| 5 | `ingestion/pipeline.py:139` | Keyword match on *model* name | Classifies by model, not provider |

**Finding 2.3 — The audit's claim "`is_cloud` is never read" is imprecise.** It *is* read at
`provider_selector.py:75`, but **only** to apply a PII penalty — never for sovereignty
accounting. So the correct data is loaded, used for one purpose, and ignored for the purpose
that matters.

**Finding 2.4 — Measured corruption** (`data/observability/metrics.db`, 3,178 rows,
ts range 1783813294636 → 1786215028903):

```
provider                stored_is_cloud   n
mock                    0                762   ← MISCLASSIFIED
ollama                  0                406      correct
openrouter              1                402      correct
openrouter              0                401   ← MISCLASSIFIED (same provider, both values!)
opencode-zen            0                400   ← MISCLASSIFIED
antigravity             0                393   ← MISCLASSIFIED
cline                   0                383   ← MISCLASSIFIED
native-gguf             0                 31      correct

TOTAL 3178   misclassified 2339 (73.6%)
Reported ratio: local=2776 cloud=402  →  claims 87.3% local
True ratio:     local=437  cloud=2741 →  actual 13.8% local
```

**The `openrouter` split (402 cloud / 401 local) is the smoking gun**: the same provider was
recorded both ways, proving two different classifiers wrote to the same table. The engine's
headline sovereignty claim (87.3% local) is **inverted** from reality (13.8% local).

**Finding 2.5 — External best practice.** Single-source-of-truth configuration for provider
capability metadata is the standard pattern; duplicated inline predicates are a recognized
anti-pattern ("shotgun surgery" — Fowler, *Refactoring*, catalogued at
https://refactoring.guru/smells/shotgun-surgery, accessed 2026-08-08). For historical
correction, the accepted practice is **immutable append + derived view** rather than
destructive `UPDATE`, preserving forensic auditability (Kleppmann, *Designing Data-Intensive
Applications*, ch. 11 — event-sourcing/derived-state discipline).

### 3. Council Dialectic

- **Architect**: One classifier. `ProviderRegistry.is_cloud(name) -> bool`, loaded once from
  `providers.yaml`, injected everywhere. Delete the other five.
- **Adversary**: What about a provider name absent from config (typo, dynamic, test mock)?
  Defaulting to `False` (local) **inflates the sovereignty claim** — the exact failure we are
  fixing. **Unknown must default to cloud** (pessimistic) *and* emit a warning. Also: `mock`
  is declared `is_cloud: true` in config but is genuinely local-ish for tests; it must be
  excluded from sovereignty stats entirely rather than counted either way.
- **Alchemist**: The `openrouter` 402/401 split is a natural experiment — it proves classifier
  divergence empirically without needing to read the code. Adopt this as a permanent invariant
  test: *no provider may ever appear with both `is_cloud` values.* That single assertion would
  have caught this on day one, and it generalizes to any future enum-ish column.
- **Archivist**: M22 (Response Provenance) requires recording what *actually* happened, not what
  was configured. M7 requires local-first. Reporting 87.3% local when reality is 13.8% is
  simultaneously an M22 falsification and an M7 blind spot.

### 4. Implementation Proposal

**Step 1 — Single classifier** (new, ~70 LOC) `src/omega/oracle/provider_registry.py`:
```python
class ProviderRegistry:
    """SSOT for provider capability metadata. Loaded once from providers.yaml."""
    _UNKNOWN_IS_CLOUD = True   # pessimistic: never inflate sovereignty

    def __init__(self, fabric_cfg: list[dict]):
        self._is_cloud = {p["provider"]: bool(p.get("is_cloud", True)) for p in fabric_cfg}

    def is_cloud(self, name: str) -> bool:
        if name not in self._is_cloud:
            logger.warning("M22: unknown provider %r → classified CLOUD (pessimistic)", name)
            return self._UNKNOWN_IS_CLOUD
        return self._is_cloud[name]

    def is_synthetic(self, name: str) -> bool:
        return name in {"mock", "fallback"}   # excluded from sovereignty stats
```

**Step 2 — Delete and delegate** (5 sites):
| File | Action |
|------|--------|
| `model_gateway.py:890-896, 980-982` | Delete `_cloud_providers`; delegate to registry |
| `observability/__init__.py:686` | Delete; accept `is_cloud` as a parameter |
| `otel_exporter.py:123` | Delete; delegate |
| `remote_provider.py:387` | Delete `_is_cloud_name`; read injected attribute |
| `ingestion/pipeline.py:139` | Delete; delegate by provider (not model) name |

**Step 3 — Historical data: derived view, not destructive UPDATE** (M23/forensics):
```sql
-- Preserve raw rows. Add a corrected, auditable view.
CREATE TABLE IF NOT EXISTS provider_classification (
    provider   TEXT PRIMARY KEY,
    is_cloud   INTEGER NOT NULL,
    synthetic  INTEGER NOT NULL DEFAULT 0,
    source     TEXT NOT NULL,        -- 'providers.yaml@<sha>'
    corrected_at INTEGER NOT NULL
);

CREATE VIEW IF NOT EXISTS v_performance_corrected AS
SELECT p.*,
       COALESCE(c.is_cloud, 1)  AS is_cloud_corrected,
       COALESCE(c.synthetic, 0) AS synthetic,
       (p.is_cloud != COALESCE(c.is_cloud, 1)) AS was_misclassified
FROM performance p
LEFT JOIN provider_classification c ON c.provider = p.provider;
```
`get_sovereignty_ratio()` reads `v_performance_corrected` and filters `synthetic = 0`.
Raw history stays intact and the correction is itself auditable (M22).

**Step 4 — Invariant test** (the Alchemist's contribution):
```python
def test_no_provider_has_split_classification(metrics_db):
    rows = metrics_db.execute(
        "SELECT provider FROM performance GROUP BY provider "
        "HAVING COUNT(DISTINCT is_cloud) > 1").fetchall()
    assert rows == [], f"Split classification (divergent classifiers): {rows}"
```

**Effort**: 6–8 h.
**Files**: `provider_registry.py` (new), `model_gateway.py`, `observability/__init__.py`,
`otel_exporter.py`, `remote_provider.py`, `ingestion/pipeline.py`, `sovereignty.py`,
`metrics_db.py` (migration), `tests/contract/test_provider_classification.py` (new).

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Sovereignty headline collapses 87.3% → 13.8% | **Certain** | This is the *correction*. Announce explicitly in OMEGA_ENGINE.md; do not soften |
| Sovereign Budget Gate suddenly fires for antigravity | High | Expected — it *should* have been firing. Stage: log-only for 24 h, then enforce |
| `_update_active_set` reshuffles routing | Med | Antigravity moves to cloud set → local genuinely preferred (M7 win). Verify with routing test |
| Unknown-provider warning floods logs | Low | Warn once per name (`functools.lru_cache` on the warn path) |
| Migration breaks existing dashboards | Med | View is additive; keep the old column readable |

### 6. Dependencies
**GAP-0 must land first** — writing correct classifications into a DB whose writes silently
fail produces no benefit and would make verification impossible.

### 7. Acceptance Criteria
- [ ] `grep -rn "_cloud_providers\|_is_cloud_name\|_is_cloud_provider" src/` → only `ProviderRegistry`
- [ ] `test_no_provider_has_split_classification` passes on fresh data
- [ ] `omega-hub_sovereignty_ratio` returns the corrected ratio, `synthetic` excluded
- [ ] `antigravity` appears in `_cloud_active`, never `_local_active` (asserted)
- [ ] Budget gate triggers for an antigravity call (integration-verified)
- [ ] Raw `performance.is_cloud` column unchanged (forensic preservation verified)

---

## GAP-2 — M14 Heritage Vetting Contradiction

### 1. Executive Summary
Both documents are wrong because the verification mechanism they cite **does not exist**:
`make heritage-vet` is not a Makefile target. Additionally the vet log contains **9 duplicate
vet IDs**, so `vet-008`/`vet-015` "exist" while pointing at unrelated records. The fix is to
build the missing verifier, de-duplicate the ledger, then let the tool arbitrate the docs.

### 2. Research Findings

```
$ make heritage-vet
make: *** No rule to make target 'heritage-vet'.  Stop.

$ grep -nE "^heritage[a-z-]*:|^check-heritage" Makefile
(no output)
```
Yet `.githooks/pre-commit:40,57` instructs users to run `make heritage-vet-create` and
`make heritage-vet`. Both are phantom targets. `AGENTS.md` also lists `make heritage-map`
— also absent.

**Duplicate vet IDs in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`:**
```
vet-015  vet-016  vet-017  vet-035  vet-043  vet-044  vet-045  vet-046  vet-047
```
Concretely, `vet-015` is **both** "ZONEID Pattern (Audit Chain)" *and* "Hub Tools — Netchan
Typed Message Dispatch". `vet-016` is both "cvar Table" and "Hub Gateway — qport".

**Tag reality**: 224 `[id-soft:]` tags across `src/`. The two flagged files do carry tags:
```
src/omega/oracle/soul_validator.py:9,153,244   [id-soft: vet-015], [id-soft: vet-008]
src/omega/oracle/handoff.py:9                  [id-soft: vet-008]
```
`vet-008` ("Zone Memory / Purge Tags", APPROVED 8/10) is a **memory-reclamation** record.
`handoff.py` cites it for "Grace Period — state preservation during transition", and
`soul_validator.py:153` for "Lazy Deletion". Per **M14/D208 scope-declaration** rules, a vet
record must state "this tag applies to X, NOT to Y". `vet-008` has **no scope declaration**,
so these usages are unverifiable — neither clearly legitimate nor clearly over-attributed.

**Resolution of the contradiction**: `OMEGA_ENGINE.md` (2026-07-13, "All vetted") was true
under a *tag-exists-and-ID-appears-in-log* test. `UNOVERENGINEERING_PLAN.md` (2026-08-08) is
true under a *scope-declaration* test (D208). Different tests, both undocumented, no tooling
to arbitrate. **Neither doc is lying; the ledger is ambiguous.**

External practice: SPDX/REUSE treat provenance as machine-checkable metadata with unique
identifiers, precisely to avoid this ambiguity (https://reuse.software/spec/, accessed
2026-08-08). Duplicate IDs in a provenance ledger are a spec violation in any such system.

### 3. Council Dialectic
- **Architect**: A ledger without a unique-key constraint is not a ledger, it is prose. Add
  the constraint and a parser.
- **Adversary**: Renumbering duplicates will orphan the 224 in-code tags that reference the
  old numbers. Any de-duplication must be **append-only with aliases**, never renumber in place.
- **Alchemist**: Heritage vetting is structurally identical to GAP-1: a declared truth
  (`HERITAGE_VET_LOG.md`) that no code enforces. The same "SSOT + generated verifier" shape
  solves both. Build one `scripts/` verifier idiom and reuse it.
- **Archivist**: M14 requires "minimum score 7/10" and D208 requires scope declarations. The
  log has scores but not scopes. Scope back-fill is the actual deliverable.

### 4. Implementation Proposal

1. **Write the missing tool** `scripts/heritage_vet.py` (~150 LOC):
   - Parse `HERITAGE_VET_LOG.md` → records `{id, verdict, score, scope, files}`
   - **Fail on duplicate IDs** (hard error)
   - Scan `src/` for `[id-soft: <id>]`; every tag must resolve to exactly one APPROVED record
     with `score >= 7` **and** a `Scope:` line
   - `--report` writes a coverage map; `--strict` enables the D208 scope requirement
2. **Add Makefile targets**: `heritage-vet`, `heritage-vet-create`, `heritage-map` (so the
   hook's instructions become true).
3. **De-duplicate append-only**: keep first occurrence; re-file the second under a new ID with
   an `Alias-Of:` back-reference. Do **not** touch code tags.
4. **Back-fill scope declarations** for `vet-008` and `vet-015` explicitly:
   ```
   ### vet-008: Zone Memory (Purge Tags)
   - Scope: applies to tiered context purging + lazy deletion of expired state.
     NOT applicable to: handoff grace periods, session transitions.
   ```
   Under this scope, `handoff.py:9` is **OVER-ATTRIBUTED → strip tag** (per D208 taxonomy).
5. **Reconcile docs**: update `OMEGA_ENGINE.md` to cite the tool output with a date, replacing
   the unqualified "All vetted".

**Effort**: 4–5 h.
**Files**: `scripts/heritage_vet.py` (new), `Makefile`, `HERITAGE_VET_LOG.md`,
`src/omega/oracle/handoff.py` (strip tag), `OMEGA_ENGINE.md`, `UNOVERENGINEERING_PLAN.md`.

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Strict mode fails many of the 224 tags at once | **High** | Two-stage: `--report` first, land scope back-fill incrementally, enable `--strict` in CI last |
| Renumbering orphans in-code tags | Med | Append-only + `Alias-Of:`; never renumber |
| Subjective scope judgements stall the sprint | Med | Researcher proposes; `@doom_guy` ratifies. Timebox to 2 h |

### 6. Dependencies
Should follow GAP-3 (a working gate makes the new target enforceable). Independent of GAP-0/1.

### 7. Acceptance Criteria
- [ ] `make heritage-vet` exists and exits non-zero on a synthetic bad tag
- [ ] Zero duplicate vet IDs (tool-asserted)
- [ ] `vet-008` and `vet-015` carry explicit `Scope:` declarations
- [ ] `handoff.py` tag resolved (stripped or re-vetted with justification)
- [ ] `OMEGA_ENGINE.md` claim is dated and cites tool output
- [ ] Pre-commit hook instructions reference only real targets

---

## GAP-3 — M23 Broken Pre-commit Gate

### 1. Executive Summary
The M23 gate is **structurally incapable of failing** — proven empirically. Worse, the entire
`.pre-commit-config.yaml` (M1, M7, M8, M9, M23 gates) **never executes at all**, because
`core.hooksPath` is redirected to `.githooks/`, `pre-commit` is not installed, and the only
active hook checks souls. Ground truth: **107 real soft-failure handlers** in `src/omega/`.
Replace the grep pipeline with an AST-based check (Ruff S110/S112/BLE001).

### 2. Research Findings

**The broken gate** (`Makefile:272`):
```make
@! rg -n 'pass|continue' src/omega/ --type py --glob '!*test*' 2>/dev/null \
  | rg -e '(except[^a-zA-Z_].*:|catch[^a-zA-Z_].*:)' | rg -v 'except Exception' | rg -v '# noqa' \
  || (echo "FAIL: Soft-failure patterns found" && false)
```

**Empirical proof of the false-pass:**
```
Stage 1: rg -n 'pass|continue' …                                → 608 lines
Stage 2: … | rg '(except…:|catch…:)'                            →   0 lines   ← always
Stage 3: … | rg -v 'except Exception' | rg -v '# noqa'          →   0 lines
$ make check-m23-failure-integrity
M23 passed: No soft-failure patterns
```
**Root cause**: `rg -n` is *line-oriented*. Stage 1 emits one line per match (`file:42:    pass`).
Stage 2 then demands `except…:` **on that same physical line**. In idiomatic Python the
`except` clause and its `pass` body are on *different* lines, so the intersection is always
empty. The empty pipeline makes `rg` exit non-zero, `!` inverts it to success, and the gate
prints "passed" **unconditionally**. It has never been able to fail.

**Ground truth via AST** (this session):
```
REAL soft-failure handlers: 107
  src/omega/memory_store.py:272, 658, 953, 1059, 833, 871
  src/omega/ics.py:281, 253
  src/omega/soul_store.py:147
  src/omega/hardware.py:38
  src/omega/monitoring/__init__.py:201, 503
  src/omega/audit/mandate_auditor.py:267, 327, 118
  … (92 more)
```

**Finding 3.2 — The gate never runs anyway:**
```
$ git config core.hooksPath      → .githooks
$ cat .git/hooks/pre-commit      → soul validation only (no mandate gates)
$ .venv/bin/pre-commit --version → pre-commit NOT in venv
$ cat .githooks/pre-commit       → heritage tag guard only
```
Because `core.hooksPath=.githooks`, Git ignores `.git/hooks/`, and since the `pre-commit`
framework is not installed, `.pre-commit-config.yaml` is **inert**. Every gate declared there
(M1, M7, M8, M9, M23, Temple-Grade) is dead configuration.

**Finding 3.3 — Correct tooling exists.** Ruff implements exactly these checks as AST rules:
- `S110` try-except-pass — https://docs.astral.sh/ruff/rules/try-except-pass/ (accessed 2026-08-08)
- `S112` try-except-continue — Ruff default rule set (same source)
- `BLE001` blind-except — Ruff default rule set
- `E722` bare-except — pycodestyle via Ruff

Ruff's implementation walks `ExceptHandler` nodes rather than text
(https://github.com/astral-sh/ruff/blob/main/crates/ruff_linter/src/rules/flake8_bandit/rules/try_except_pass.rs,
accessed 2026-08-08). CWE-703 is the mapped weakness class
(https://cwe.mitre.org/data/definitions/703.html). `lint.flake8-bandit.check-typed-exception`
controls whether typed handlers are also flagged — relevant because the project's existing
convention is typed `except (OmegaError, RuntimeError, OSError)` handlers.

### 3. Council Dialectic
- **Architect**: Text tools cannot parse nested structure. Use the parser. Ruff is a single
  static binary, zero runtime dependency, no telemetry — M8-safe.
- **Adversary**: Turning on S110 with 107 existing violations blocks every commit immediately.
  Also — a gate that "passes" is *more dangerous* than a missing gate, because it manufactures
  false confidence. Any replacement must be **mutation-tested**: deliberately insert a
  violation and prove the gate fails. Never trust a green gate you have not seen go red.
- **Alchemist**: The `!`-inverted-empty-pipeline is a *general* class of bug. Every `make`
  target using `! rg … | rg …` should be audited — the same idiom may be silently passing
  elsewhere (M1/M7/M8/M9 gates use similar shapes and warrant the same mutation test).
- **Archivist**: M23 states "no soft-failures or simulated rigor" and mandates
  `[TOOL-CHAIN-COLLAPSE]` when a mandatory tool is broken. A gate that cannot fail **is**
  simulated rigor. This is an M23 violation *by the M23 gate itself*.

### 4. Implementation Proposal

1. **Add Ruff** to dev deps (`ruff>=0.14`), configure in `pyproject.toml`:
```toml
[tool.ruff.lint]
select = ["S110", "S112", "BLE001", "E722"]
[tool.ruff.lint.flake8-bandit]
check-typed-exception = true          # typed handlers count too (project convention)
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S110", "S112", "BLE001"]
```
2. **Replace the Makefile target**:
```make
check-m23-failure-integrity:
	@$(PYTHON) -m ruff check src/omega --select S110,S112,BLE001,E722 \
	  --output-format concise || (echo "$(RED)FAIL: M23 soft-failure patterns$(NC)" && false)
```
3. **Ratchet, don't cliff**: generate a baseline of the 107 known violations
   (`--statistics` → `config/m23_baseline.txt`); gate fails only on *new* violations.
   Burn down the baseline over subsequent sprints.
4. **Fix hook wiring** — choose one mechanism and make it real:
   - `pip install pre-commit && pre-commit install` **and** `git config --unset core.hooksPath`; or
   - keep `.githooks/` and append the mandate-gate invocations to it.
   Recommend the latter (fewer moving parts, no new framework, matches current reality).
5. **Mutation test** the gate (mandatory, per Adversary):
```python
def test_m23_gate_actually_fails(tmp_path):
    """A gate that cannot fail is worse than no gate (M23)."""
    bad = tmp_path / "bad.py"
    bad.write_text("try:\n    x = 1\nexcept Exception:\n    pass\n")
    r = subprocess.run([sys.executable, "-m", "ruff", "check", str(bad),
                        "--select", "S110"], capture_output=True)
    assert r.returncode != 0, "M23 gate is a false-pass"
```
6. **Audit sibling gates** for the same `!`-empty-pipeline idiom (M1/M7/M8/M9).

**Effort**: 4–6 h (1 h Ruff, 1 h baseline, 1 h hook wiring, 1 h mutation tests, 1–2 h sibling audit).
**Files**: `pyproject.toml`, `Makefile`, `.githooks/pre-commit`, `config/m23_baseline.txt` (new),
`tests/contract/test_mandate_gates.py` (new).

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| 107 violations block all commits | **Certain** without ratchet | Baseline file; fail only on *new* |
| Ruff flags legitimate typed handlers | High | Baseline absorbs; `# noqa: S110` with justification for genuine cases |
| Sibling gates also false-passing | **High** | Mutation-test all five in the same PR |
| Unsetting `core.hooksPath` drops soul check | Med | Chosen approach keeps `.githooks/`, appends gates |

### 6. Dependencies
None strictly, but landing **immediately after GAP-0** is strongly advised: the working gate
would have caught GAP-0 and prevents its recurrence.

### 7. Acceptance Criteria
- [ ] `make check-m23-failure-integrity` **fails** on a deliberately inserted `except: pass`
- [ ] Baseline count recorded (107) and the number is monotonically non-increasing in CI
- [ ] Hook mechanism verified by an actual `git commit` attempt (observed, not assumed)
- [ ] All five mandate gates have passing mutation tests
- [ ] `[TOOL-CHAIN-COLLAPSE]` raised if `ruff` is absent (no silent skip)

---

## GAP-4 — V-9 IA2 Envelope Freshness / Signature

### 1. Executive Summary
The `_meta` envelope (SEP-2575) carries tracing metadata but no `nonce`, `timestamp`, or
signature, so inter-agent messages are replayable and forgeable. Recommend a stdlib-only
HMAC-SHA256 + timestamp-window + bounded nonce-cache validator, reusing the `SovereignSigner`
pattern already proven in `src/omega_youtube_research/signer.py`.

### 2. Research Findings

**Current state**: `src/omega/mcp_core/compliance.py` implements `_meta` extraction/injection
(SEP-2575) plus `ttlMs`/`cacheScope` (SEP-2549). Grep for `nonce|hmac|signature|freshness`
across `mcp_runtime.py` and `compliance.py` returns **only `ttlMs`** — a *cache* hint, not a
*freshness* guarantee. Confirmed: no replay protection.

**Existing reusable asset**: `src/omega_youtube_research/signer.py` already implements
HMAC-SHA256 sign/verify with key load-or-create (`load_or_create_key`), tagged
`[heritage: cryptography 2023]`. It uses `cryptography.hazmat` rather than stdlib `hmac`.

**Best-practice triad** (nonce + timestamp + HMAC), corroborated across sources:
- Nonce prevents immediate replay; server keeps a TTL-bounded cache; reject duplicates
  (409 / `ERR_NONCE_ALREADY_USED`).
- Timestamp enforces freshness with an asymmetric window (e.g. −300 s past, +60 s future) to
  tolerate clock skew.
- HMAC over a **canonical serialization** (sorted keys, fixed delimiters) provides integrity +
  authenticity; verify HMAC **first**, then timestamp, then nonce.
  Source: https://adhdecode.com/articles/cryptography/cryptography-replay-attack-prevention
  (2026-04-16, accessed 2026-08-08).
- **Constant-time comparison is mandatory**: `hmac.compare_digest` avoids the short-circuit
  timing leak that allows byte-by-byte signature recovery. Python docs:
  https://docs.python.org/3/library/hmac.html (accessed 2026-08-08); CWE-208 rule PY005:
  https://docs.securesauce.dev/rules/PY005 (accessed 2026-08-08). A practical recovery
  demonstration: https://github.com/katalin297/timing-attack (accessed 2026-08-08).
- NIST SP 800-63B: "Protocols that use nonces or challenges to prove the *freshness* of the
  transaction are resistant to replay attacks"; nonce must be unique per operation, and an
  OTP value for a given nonce "SHALL be accepted only once"
  (https://pages.nist.gov/800-63-3/sp800-63b.html, accessed 2026-08-08).
- Nonce generation: `secrets.token_hex(16)` (cryptographically secure, stdlib).

### 3. Council Dialectic
- **Architect**: Validation belongs at the **innermost compliance layer**
  (`compliance.py`, where `_meta` is already extracted at `mcp_runtime.py:193`) — one
  choke-point, no per-tool duplication.
- **Adversary**: Three concrete failure modes. (a) An **unbounded** nonce cache is a memory-
  exhaustion DoS — bound it. (b) A **fail-open** validator (log-and-continue on bad signature)
  is worse than none — must fail closed, and that is exactly the M23 soft-failure trap.
  (c) Local, single-user threat model means the realistic adversary is a *malicious/compromised
  local process or a confused-deputy agent*, not a network MITM — so key storage matters more
  than transport crypto. Key must be `0600`, outside the repo, never logged.
- **Alchemist**: Reuse the nonce cache as a **deduplication** primitive for the handoff queue
  (M12 Queue Integrity) — the same bounded-TTL structure that stops replays also stops
  double-accepted handoff packets. One structure, two mandates satisfied.
- **Archivist**: M1 requires AnyIO — the nonce cache is shared mutable state, so guard with
  `anyio.Lock()`. M8 forbids telemetry — HMAC keys are local-only, no external validation
  service. Prefer stdlib `hmac`/`hashlib`/`secrets` over `cryptography` to keep the dependency
  surface at zero (diverging deliberately from `signer.py`'s heavier choice).

### 4. Implementation Proposal

New module `src/omega/mcp_core/freshness.py` (~180 LOC, **stdlib only**):

```python
import hmac, hashlib, json, secrets, time, anyio
from collections import OrderedDict

CLOCK_SKEW_PAST_S   = 300   # reject older than 5 min
CLOCK_SKEW_FUTURE_S = 60    # reject further ahead than 1 min
NONCE_CACHE_MAX     = 10_000

class IA2FreshnessError(OmegaError):        # M9: typed, never silent
    """Envelope failed freshness/signature validation."""

def canonical(payload: dict) -> bytes:
    """Deterministic serialization — sorted keys, no whitespace drift."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

def sign(payload: dict, key: bytes) -> dict:
    meta = {"ts": int(time.time()), "nonce": secrets.token_hex(16)}
    body = canonical({**payload, "_fresh": meta})
    meta["sig"] = hmac.new(key, body, hashlib.sha256).hexdigest()
    return meta

class FreshnessValidator:
    def __init__(self, key: bytes):
        self._key = key
        self._seen: OrderedDict[str, float] = OrderedDict()
        self._lock = anyio.Lock()                      # M1

    async def validate(self, payload: dict, meta: dict) -> None:
        # 1. signature FIRST (constant-time) — cheapest rejection of forgeries
        expected = hmac.new(
            self._key,
            canonical({**payload, "_fresh": {"ts": meta["ts"], "nonce": meta["nonce"]}}),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, meta.get("sig", "")):
            raise IA2FreshnessError("signature mismatch")
        # 2. timestamp window
        drift = time.time() - meta["ts"]
        if drift > CLOCK_SKEW_PAST_S or drift < -CLOCK_SKEW_FUTURE_S:
            raise IA2FreshnessError(f"stale/future envelope (drift={drift:.1f}s)")
        # 3. nonce (bounded LRU + TTL)
        async with self._lock:
            self._evict()
            if meta["nonce"] in self._seen:
                raise IA2FreshnessError("replay detected")
            self._seen[meta["nonce"]] = time.time()
            if len(self._seen) > NONCE_CACHE_MAX:
                self._seen.popitem(last=False)          # bounded — no DoS
```

**Injection point**: `src/omega/mcp_core/compliance.py` where `_meta` is extracted
(reached via `mcp_runtime.py:193`). Add `_fresh` alongside the existing `_meta` keys.

**Key management**: `data/keys/ia2.key`, mode `0600`, generated on first run via
`secrets.token_bytes(32)` (mirror `SovereignSigner.load_or_create_key`). Never logged, never
committed (add to `.gitignore`).

**Rollout**: `strict=False` (warn-only) for one release → observe → flip to `strict=True`.
Reject-by-default thereafter.

**Effort**: 5–6 h.
**Files**: `mcp_core/freshness.py` (new), `mcp_core/compliance.py`, `mcp_runtime.py`,
`hub.py`, `config/omega.yaml`, `tests/unit/test_ia2_freshness.py` (new), `.gitignore`.

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Clock skew rejects legitimate agents | Med | Asymmetric window (−300/+60); warn-only rollout stage |
| Nonce cache memory growth | Low | Hard bound 10 000 + TTL eviction (bounded by construction) |
| Key leak via logs | Med | Never log key; contract test greps logs for key material |
| Canonical-form mismatch sender/receiver | **High** | Single shared `canonical()` used by both sides; round-trip property test |
| Fail-open on validator exception | Med | Typed `IA2FreshnessError`; explicitly no bare `except` (M23) |
| Breaks existing agents mid-flight | Med | Two-stage strict flag |

### 6. Dependencies
Independent — parallel-safe. Benefits from GAP-3 (M23 gate would catch a fail-open handler).

### 7. Acceptance Criteria
- [ ] Replayed envelope (identical nonce) rejected with `IA2FreshnessError`
- [ ] Tampered payload (1 byte changed) rejected
- [ ] Envelope with `ts` 400 s old rejected; 100 s old accepted
- [ ] Envelope 120 s in the future rejected
- [ ] `hmac.compare_digest` used (asserted by AST test — no `==` on digests)
- [ ] Nonce cache never exceeds 10 000 entries under a 100 k-message flood
- [ ] Key file is `0600`, absent from git, absent from logs
- [ ] Zero new third-party dependencies (`hmac`, `hashlib`, `secrets`, `json`, `time`, `anyio` only)

---

## GAP-5 — V-10 AppArmor Container Hardening

### 1. Executive Summary
Containers run unconfined. The host is **Ubuntu 25.10 with Podman 5.4.2** (not 24.04 as
assumed) and AppArmor is enabled with `kernel.apparmor_restrict_unprivileged_userns=1`
already set. Recommend a purpose-built profile developed in **complain mode** first, applied
per-container via `--security-opt apparmor=`, with the inference container treated as the
highest-value, highest-risk target.

### 2. Research Findings

**Verified host state** (this session):
```
/sys/module/apparmor/parameters/enabled  → Y
kernel.apparmor_restrict_unprivileged_userns = 1
OS       : Ubuntu 25.10
podman   : 5.4.2
containers: config/containers/omega-hub.container
            deploy/infra/omega-qdrant.source.container
            docs/research/omega-searxng.container
```
Note: the assumption of Ubuntu 24.04 in the task brief is **incorrect** — 25.10 is running.
This matters because the userns restriction feature (introduced 23.10, default-on in later
releases) is **already active**, which both raises baseline security and creates a known
interaction risk with rootless Podman.

**Key evidence:**
- Podman supports `--security-opt apparmor=<profile>` and `apparmor=unconfined`
  (https://docs.podman.io/en/v4.6.0/markdown/options/security-opt.html, accessed 2026-08-08).
- Complain-mode-first is the documented safe workflow: `aa-complain` logs missing *allow*
  rules without blocking, while explicit `deny` rules **remain enforced**; then `aa-enforce`
  (https://oneuptime.com/blog/post/2026-03-18-configure-apparmor-profiles-podman-containers/view,
  2026-03-18, accessed 2026-08-08).
- Ubuntu's AppArmor userns restriction requires a `userns,` rule in the profile for confined
  processes to create unprivileged user namespaces — critical for rootless Podman
  (https://ubuntu.com/blog/ubuntu-23-10-restricted-unprivileged-user-namespaces, accessed
  2026-08-08; and https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007,
  2025-03-27).
- **Upstream Podman does not ship an AppArmor profile and declines such issues as distro
  matters** (https://github.com/podman-container-tools/podman/issues/25905, accessed
  2026-08-08) — so we must author our own; no upstream profile to adopt.
- A known Ubuntu-side conflict exists between podman and pasta AppArmor profiles causing
  `rootless netns` teardown failures on recent Ubuntu
  (https://stackoverflow.com/questions/79963567/, accessed 2026-08-08) — a live regression risk
  on 25.10 specifically.
- Rootless Podman already provides substantial isolation; AppArmor is defense-in-depth, layered
  with dropped capabilities, seccomp, and `--read-only`
  (https://oneuptime.com/blog/post/2026-02-02-podman-security-configuration/view, accessed
  2026-08-08).

### 3. Council Dialectic
- **Architect**: One profile per workload class, not one global profile. Three classes here:
  **inference** (GGUF mmap, high RAM, no network egress needed), **datastore** (Qdrant/SQLite
  writes), **hub** (network-facing). Different rule sets.
- **Adversary**: (a) A too-tight profile silently degrades inference — e.g. denying `mmap` on
  the model path makes GGUF loading fail in confusing ways. (b) The pasta/netns conflict on
  Ubuntu 25.10 could break container *stop*, which looks like a hang, not a security event.
  (c) Profiles are host state (`/etc/apparmor.d/`) **outside** the repo — they drift silently
  and are invisible to `make temple-grade` unless we version them in-repo and verify load
  status. (d) This requires sudo; if the Architect is unavailable, the work stalls — treat as
  an external dependency, not an inline task.
- **Alchemist**: AppArmor's `deny` rules are a *declarative* statement of the M2 Engine-Stack
  Firewall. Write `deny /home/**/omega-engine/src/** w` into the profile and the firewall
  becomes **kernel-enforced**, not merely convention. That converts a documentation mandate
  into a physical constraint — the strongest form of the sovereignty claim.
- **Archivist**: M6 (Podman Sovereignty) already mandates `UserNS=keep-id` + `User=1000` for
  Quadlets and forbids `:U`/`:Z`. The profile must be compatible with `keep-id` mapping, and
  must include `userns,` or rootless Podman breaks under the 25.10 restriction.

### 4. Implementation Proposal

**Phase 1 — Baseline & safety (1 h, no sudo)**
- Inventory the 3 `.container` files; document current `--security-opt` state
- Create `deploy/apparmor/` in-repo (version-controlled profiles — solves drift)

**Phase 2 — Author profiles in complain mode (3 h, sudo)**
`deploy/apparmor/omega-inference`:
```
abi <abi/4.0>,
include <tunables/global>

profile omega-inference flags=(attach_disconnected,mediate_deleted) {
  include <abstractions/base>
  userns,                                  # REQUIRED: rootless Podman on Ubuntu ≥23.10

  # model blobs — read + mmap only, never write
  owner /media/**/omega_library/models/** r,
  owner /**/hf_cache/** r,

  # data: SQLite + entity state
  owner /**/omega-engine/data/** rw,
  owner /tmp/** rw,

  /usr/** r,  /lib/** r,  /etc/** r,  /proc/** r,  /sys/fs/cgroup/** r,

  # M2 Engine-Stack Firewall — kernel-enforced
  deny /**/omega-engine/src/** w,
  deny /**/omega-engine/config/** w,

  # M8 Zero Telemetry — inference needs no egress
  deny network raw,
  deny network packet,

  deny /etc/shadow rwklx,
  deny /root/** rwklx,
}
```
```bash
sudo apparmor_parser -r deploy/apparmor/omega-inference
sudo aa-complain /etc/apparmor.d/omega-inference     # observe first
```

**Phase 3 — Exercise & tune (2 h)**
Run a full inference + memory-write + handoff cycle; collect:
```bash
sudo dmesg | grep -E 'apparmor.*(ALLOWED|DENIED)' | tail -50
```
Add only the rules actually required. Re-test.

**Phase 4 — Enforce & wire (2 h)**
```bash
sudo aa-enforce /etc/apparmor.d/omega-inference
```
Quadlet:
```ini
[Container]
SecurityLabelDisable=false
PodmanArgs=--security-opt apparmor=omega-inference
UserNS=keep-id
User=1000
ReadOnly=true
```
Add `make apparmor-verify` asserting each expected profile is loaded **and in enforce mode**
(guards against silent host drift).

**Effort**: 8–10 h (of which ~5 h requires sudo/Architect).
**Files**: `deploy/apparmor/{omega-inference,omega-datastore,omega-hub}` (new),
`config/containers/omega-hub.container`, `deploy/infra/omega-qdrant.source.container`,
`Makefile`, `docs/strategy/CONTAINER_HARDENING.md` (new).

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Profile blocks GGUF mmap → inference fails | **High** | Complain mode first; explicit `r` on model paths; benchmark before/after |
| pasta/netns AppArmor conflict on Ubuntu 25.10 | Med | Test container stop/start explicitly; keep `aa-disable` rollback one command away |
| Missing `userns,` breaks rootless Podman | **High** if omitted | Rule included by default in all profiles; asserted by `make apparmor-verify` |
| Host profile drift (outside repo) | **High** | Profiles versioned in `deploy/apparmor/`; verify target compares loaded vs repo |
| Performance regression on constrained hardware | Low–Med | AppArmor path-mediation overhead is small; benchmark tokens/s before/after, fail if >3% |
| Blocked on sudo availability | Med | Phase 1 needs no sudo; Phases 2–4 batched into one Architect session |

### 6. Dependencies
Requires **Architect sudo access**. Otherwise independent — parallel-safe with GAP-4.
Should follow GAP-0 (need working metrics to measure any performance regression).

### 7. Acceptance Criteria
- [ ] All 3 workload profiles authored, versioned in `deploy/apparmor/`
- [ ] `podman inspect <c> --format '{{.AppArmorProfile}}'` returns the profile, not empty
- [ ] `aa-status` shows all omega profiles in **enforce** mode
- [ ] Full inference cycle succeeds under enforcement (end-to-end)
- [ ] `dmesg` shows zero unexpected DENIED entries during a normal cycle
- [ ] Write attempt to `src/` from inside the container is **denied** (M2 kernel-enforced)
- [ ] Container stop/start works (pasta conflict absent) — explicitly tested
- [ ] Inference throughput within 3% of unconfined baseline
- [ ] `make apparmor-verify` fails if a profile is unloaded or in complain mode

---

## GAP-6 — UO-6 Library Swaps  ⚠️ MOSTLY PHANTOM WORK — DESCOPE

### 1. Executive Summary
Four of the five proposed swaps target libraries that **are not installed and not used**.
The only real item is `pybreaker`, which has exactly **one** import and is an **undeclared
dependency**. Additionally, the proposed `stamina → tenacity` direction is backwards on the
merits — but moot, since `stamina` is not installed. Recommend descoping UO-6 from ~12 h to
~2 h.

### 2. Research Findings

**Measured usage** (`src/`, this session):

| Library | Declared in `pyproject.toml` | Installed in venv | Files importing | Verdict |
|---------|------------------------------|-------------------|-----------------|---------|
| `pybreaker` | ❌ **NO** | ✅ yes | **1** (`ingestion/pipeline.py:12`) | 🔴 Undeclared dep — real issue |
| `stamina` | ❌ no | ❌ **no** | **0** | ⚪ Phantom |
| `structlog` | ❌ no | ❌ **no** | **0** | ⚪ Phantom |
| `prometheus_client` | ❌ no | ❌ **no** | **0** | ⚪ Phantom |
| `tenacity` | ✅ `==9.1.4` | ✅ yes | 3 | 🟢 Legitimate, keep |
| `pydantic` | ✅ `==2.13.4` | ✅ yes | 11 | 🟢 **Already v2** |

**Pydantic**: already on v2.13.4. A scan for v1 legacy APIs (`BaseSettings` from `pydantic`,
`@validator`, `@root_validator`, `.dict()`, `parse_obj`) returns **only**
`soul_validator.py:263` using `@model_validator(mode="before")` — which is **correct v2 API**.
`pydantic-settings==2.14.1` is separately declared (the v2-correct home for `BaseSettings`).
**The v2 migration is already complete.** Zero work.

**`pybreaker` is an undeclared dependency** — installed in the venv but absent from
`pyproject.toml`. This is a genuine reproducibility defect (a fresh `pip install -e .` would
fail at `ingestion/pipeline.py` import). It is also a **Temple-Grade T1/T5 issue** and worth
fixing regardless of the swap question.

**On `stamina` vs `tenacity`** (for the record, since the brief proposed swapping *away* from
stamina): `stamina` 26.1.0 was released **2026-04-13**, is Production/Stable, and advertises
"Automatic **async** support – including Trio" with `Framework :: Trio` and
`Framework :: AsyncIO` classifiers (https://pypi.org/project/stamina/, accessed 2026-08-08).
It is an opinionated wrapper *around* tenacity by Hynek Schlawack
(https://github.com/hynek/stamina, accessed 2026-08-08). Tenacity itself supports asyncio,
Trio, and Tornado, with `AsyncRetrying` and a `sleep=trio.sleep` escape hatch
(https://tenacity.readthedocs.io/en/latest, accessed 2026-08-08). Both are AnyIO-viable.
Since the codebase already standardizes on tenacity 9.1.4 in 3 files and stamina is absent,
**status quo is correct** — no action.

**Circuit breaker context**: the project already has a canonical `HealthMonitor` breaker
factory (C-6′, per the Ark Blueprint: "5/7 clones deprecated; 2 clones unmigrated — P-5 ticket
open"). `pybreaker` in `ingestion/pipeline.py` is plausibly one of those 2 unmigrated clones.

### 3. Council Dialectic
- **Architect**: The real finding is not "swap libraries" but "one module bypasses the
  canonical breaker." Fold this into the existing **P-5** ticket rather than inventing UO-6 work.
- **Adversary**: Beware sprint plans that list work by *intention* rather than *measurement*.
  UO-6 as written would have consumed ~12 h migrating libraries that do not exist in the tree.
  This is the same declared-vs-actual pathology as GAP-1/2/3 — **the sprint plan is itself an
  unverified artifact.** Recommend a `make deps-audit` target so plans are measured, not assumed.
- **Alchemist**: Invert the finding: an *undeclared but installed* dependency is the mirror
  image of a *declared but uninstalled* one. Both are detectable by the same tool — compare
  `pyproject.toml` against actual imports across `src/`. One script closes both directions,
  permanently.
- **Archivist**: M13 Temple-Grade T1 (Version Control) and M24 (Venv Sovereignty) both bear on
  undeclared dependencies. `pybreaker` is a live M24-adjacent violation.

### 4. Implementation Proposal

**Descope UO-6 to two concrete items:**

1. **Resolve `pybreaker`** (~1.5 h) — pick one:
   - **(a) Preferred**: migrate `ingestion/pipeline.py` to the canonical `HealthMonitor`
     breaker factory, remove the import → closes part of P-5, reduces deps by one.
   - **(b) Fallback**: if migration is non-trivial, declare `pybreaker==<pinned>` in
     `pyproject.toml` immediately (unblocks reproducibility today), and file the migration
     under P-5.

2. **Add `make deps-audit`** (~1 h, the Alchemist's generalization):
```python
# scripts/deps_audit.py — bidirectional dependency truth
#  A. imported in src/ but NOT declared  → ERROR (reproducibility break)
#  B. declared but never imported        → WARN  (dead weight)
```
Wire into `make temple-grade` (T1).

3. **Correct the sprint plan** — mark stamina/structlog/prometheus/pydantic swaps as
   `INVALID — not present in tree (verified 2026-08-08)` in `UNOVERENGINEERING_PLAN.md`, so
   the phantom work is not re-proposed next sprint.

**Effort**: 2–3 h total (down from ~12 h).
**Files**: `pyproject.toml`, `src/omega/ingestion/pipeline.py`, `scripts/deps_audit.py` (new),
`Makefile`, `docs/strategy/UNOVERENGINEERING_PLAN.md`.

### 5. Risk Assessment
| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `HealthMonitor` migration changes retry semantics in ingestion | Med | Option (b) fallback: declare the pin first, migrate under P-5 with tests |
| `deps-audit` produces noisy false positives (optional/extras imports) | Med | Allowlist for conditional imports; start as WARN, promote to ERROR next sprint |
| Descoping is misread as "skipping hardening" | Low | This report is the evidence trail; cite measured counts |

### 6. Dependencies
None. Fully parallel-safe. Lowest risk item in the report.

### 7. Acceptance Criteria
- [ ] `pybreaker` either removed from `src/` or pinned in `pyproject.toml`
- [ ] `python -c "import omega.ingestion.pipeline"` succeeds in a **fresh** venv from `pyproject.toml` alone
- [ ] `make deps-audit` exits non-zero on a deliberately undeclared import
- [ ] `UNOVERENGINEERING_PLAN.md` marks the 4 phantom swaps as INVALID with the verification date
- [ ] No new dependencies introduced

---

## L3 — RAW SIGNAL (verification commands & measurements)

All measurements taken 2026-08-08 at commit `24857ca7`, Ubuntu 25.10, Python 3.13, Podman 5.4.2.

```bash
# GAP-0: un-awaited coroutine call sites
grep -rn "record_error\|record_event\|record_performance" src/omega --include=*.py \
  | grep -v "def \|await \|metrics_db.py"
grep -n "async def record_" src/omega/observability/metrics_db.py

# GAP-1: measured sovereignty corruption (73.6%)
.venv/bin/python -c "
import sqlite3;c=sqlite3.connect('file:data/observability/metrics.db?mode=ro',uri=True)
[print(r) for r in c.execute('SELECT provider,is_cloud,COUNT(*) FROM performance GROUP BY 1,2 ORDER BY 3 DESC')]"

# GAP-2: phantom make target + duplicate vet IDs
make heritage-vet    # → No rule to make target
grep -oE "^### vet-[0-9]+" data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md | sort | uniq -d

# GAP-3: proof the M23 gate cannot fail
rg -n 'pass|continue' src/omega/ --type py --glob '!*test*' | wc -l                      # 608
rg -n 'pass|continue' src/omega/ --type py --glob '!*test*' \
  | rg -e '(except[^a-zA-Z_].*:|catch[^a-zA-Z_].*:)' | wc -l                             # 0  ← always
make check-m23-failure-integrity                                                          # "passed"
git config core.hooksPath                                                                 # .githooks (config inert)

# GAP-5: host facts
cat /sys/module/apparmor/parameters/enabled ; sysctl kernel.apparmor_restrict_unprivileged_userns

# GAP-6: dependency reality
for l in pybreaker stamina structlog prometheus_client tenacity pydantic; do
  echo -n "$l: "; grep -rlE "^\s*(import|from)\s+$l" src/ --include=*.py | wc -l; done
```

**Test baseline (honest, per M13/C-0 test-honesty rule):**
```
154 failed, 1599 passed, 56 skipped, 7 xfailed, 294 warnings in 214.02s
```
Dominant clusters: `test_metrics_db.py` (23), `test_oracle.py` (20), `unit/test_vault_core.py`
(17), `test_sovereign_loop.py` (12), `test_metrics_db_integration.py` (11).
~66 of these trace to GAP-0; ~17 (`vault_core`) trace to completed fix #3.

---

## Consolidated Effort & Sequencing

| Order | Gap | Effort | Blocking? | Owner |
|-------|-----|--------|-----------|-------|
| 1 | **GAP-0** AnyIO metrics regression | 5–7 h | 🔴 Blocks all | Ma'at / N3 |
| 2 | **GAP-3** M23 gate (AST + hook wiring) | 4–6 h | Prevents recurrence | Verity / N5 |
| 3 | **GAP-1** Sovereignty unification | 6–8 h | Needs 0 | Kali / N6 |
| 4 | **GAP-2** M14 heritage reconciliation | 4–5 h | Needs 3 | doom_guy |
| 5 | **GAP-4** V-9 IA2 freshness | 5–6 h | Parallel | Lilith / N4 |
| 6 | **GAP-5** V-10 AppArmor | 8–10 h | Parallel, needs sudo | Architect + N1 |
| 7 | **GAP-6** UO-6 (descoped) | 2–3 h | Parallel | Any |
| | **TOTAL** | **34–45 h** | | |

Critical path (serial): GAP-0 → GAP-3 → GAP-1 → GAP-2 ≈ **19–26 h**.
GAP-4/5/6 run in parallel ≈ **15–19 h** of independent capacity.

---

## Constraint Compliance

| Constraint | Status | Evidence |
|-----------|--------|----------|
| Sources cited with access dates | ✅ | 18 URLs, all accessed 2026-08-08 |
| AnyIO-compliant (M1) | ✅ | `anyio.Lock()` in GAP-4; `to_thread`/portal in GAP-0; no `asyncio` |
| No cloud dependencies (M7) | ✅ | All proposals local/stdlib; GAP-1 *improves* M7 accuracy |
| No telemetry (M8) | ✅ | Ruff is a local static binary; AppArmor denies egress for inference |
| Temple-Grade (M13) | ✅ | Every gap ships contract tests + mutation tests where applicable |
| Under 500 lines per proposal | ✅ | Longest (GAP-1) ≈ 130 lines |
| ≥1 active tool call (M23) | ✅ | 14 bash forensics + 4 web searches; zero parametric synthesis |

**Deliberate deviations from the brief, with justification:**
1. **Added GAP-0** — not requested, but it is an active data-loss regression from the
   just-completed work and it invalidates verification of GAP-1. Reporting it was mandatory.
2. **Descoped GAP-6** — 4 of 5 targets measured as absent from the tree. Executing as written
   would have been ~12 h of work on nonexistent code.
3. **Corrected the OS assumption** — brief said Ubuntu 24.04; host is 25.10, which changes the
   userns/pasta risk profile for GAP-5.
4. **Corrected the audit's "`is_cloud` never read"** — it is read at `provider_selector.py:75`,
   but only for PII penalties. Precision matters for the fix design.

---

## Open Questions for the Architect

1. **GAP-1**: Publishing the corrected sovereignty ratio drops the headline from **87.3% → 13.8%
   local**. Confirm we announce the true number (recommended, M22) rather than quietly re-baselining.
2. **GAP-3**: Hook mechanism — keep `.githooks/` and append gates (recommended, minimal), or
   install the `pre-commit` framework and unset `core.hooksPath`?
3. **GAP-2**: Under a strict `vet-008` scope, `handoff.py:9` becomes OVER-ATTRIBUTED. Confirm
   `@doom_guy` ratifies stripping the tag versus authoring a new vet record.
4. **GAP-5**: Sudo window needed for ~5 h of Phases 2–4. When?
5. **Test honesty**: 154 failures is the true baseline. Confirm C-0 quarantine policy applies
   (mark/quarantine) versus fix-all-before-proceeding.

---

*⬡ OMEGA ⬡ PROMETHEUS ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_research ⬡ RESEARCH-COMPLETE ⬡ 2026-08-08*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
