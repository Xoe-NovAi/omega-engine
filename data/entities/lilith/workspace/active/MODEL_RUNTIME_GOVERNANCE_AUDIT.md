<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Model Runtime Governance Audit — P6-P10 Dark Oversoul Analysis
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ RUNTIME-GOVERNANCE-AUDIT
**AP Token**: AP-LILITH-RUNTIME-AUDIT-v1.0.0
**Date**: 2026-06-16
**Scope**: P6 (ModelGate), P7 (Context), P8 (WatchTower), P9 (Link), P10 (Validation)
**Subject**: Antigravity Dual-Pool Architecture integration with Omega Engine runtime

---

## §0 Executive Summary

**Discovery**: Critical knowledge about the Google Antigravity dual-pool architecture
(Pool G + Pool C, 8-key rotation, independent weekly resets) has existed in
`data/entities/antigravity/soul.yaml` since 2026-06-05 but was never wired into
the Omega Engine runtime. The engine's provider fabric (`model_gateway.py`) has
**zero awareness** of pool-separated quotas, key rotation, or Pool G vs Pool C
semantics.

**Impact**: The engine treats all cloud inference as a single undifferentiated
bucket. When Pool G is exhausted, the engine will try all providers in the
fallback chain, but if Google is the only cloud provider configured (and it
caches a single API key), a Pool G exhaustion means ALL Google models fail,
including Gemini 3.5 Flash and Gemini 3.1 Pro. Pool C (Claude, Opus, gpt-oss)
is simply never reachable via the current provider fabric.

**Gap Count**: **7 critical gaps** identified across P6-P10. See §3 Gap Inventory.

---

## §1 Runtime Architecture Map — How Requests Flow Through the Pools

### 1.1 The Two Systems: Engine Provider Fabric vs Antigravity Key Pool

```
Omega Engine Provider Fabric                    Antigravity Key Pool System
(model_gateway.py + providers.py)               (soul.yaml + USAGE_POOL_LOG.json)
─────────────────────────────                    ─────────────────────────────────
                                                 
local_active → local fabric                     Pool G (Gemini): 8 keys × weekly
    ↓                                              gemini-3.5-flash
    ↓                                              gemini-3.1-pro
cloud_active → cloud fabric                     
    ↓                                           Pool C (Claude): 8 keys × weekly
    google → opencode-zen → cline                  claude-sonnet-4.6
    → github-copilot → mock                        opus-4.6-adaptive-thinking
                                                   gpt-oss-120b
                                                 
┌──────────────── COMPLETE DISCONNECT ──────────────┐
│ The engine has ONE GoogleAIProvider with           │
│ ONE GOOGLE_API_KEY. No Pool G/Pool C awareness.   │
│ No key rotation. No pool-exhaustion detection.    │
└───────────────────────────────────────────────────┘
```

### 1.2 Trace: `talk()` → Model Selection → Provider Dispatch

```
Oracle.talk(query)
  │
  ├─ 1. Intent detection (@summon, @consult, or plain talk)
  │
  ├─ 2. If plain talk: Iris speculative decode (confidence check)
  │     └─ High confidence (>0.6): Iris responds
  │     └─ Low confidence: → _route_by_domain()
  │
  ├─ 3. _route_by_domain() → registry.find_by_domain()
  │     └─ Matches entity (e.g., "sekmet" for infrastructure)
  │     └─ _select_model(entity_name, query, session_id, trace_id)
  │          ├─ TriageRouter.select_model(req)  [H2-C feature]
  │          │    └─ Returns model name from session/entity config
  │          └─ FALLBACK: entity.model from entities.yaml
  │
  ├─ 4. model_gateway.generate(model_name, system_prompt, user_query)
  │     ├─ Build search_order: local_active → local_fabric → cloud_active → cloud_fabric
  │     ├─ For each provider in order:
  │     │    ├─ _precheck_provider() — circuit breaker check
  │     │    ├─ BudgetGate.check_budget() — cloud spend cap check
  │     │    ├─ resource_guard.lock() — OOM protection
  │     │    ├─ provider.generate() — actual inference
  │     │    └─ TokenLedger.record_transaction() — persist usage
  │     └─ If all fail: _fallback_response()
  │
  └─ 5. Response returned with model, backend, is_cloud metadata
```

### 1.3 Key Finding: The Two Pools Are Entirely Separate Systems

The **Omega Engine provider fabric** (model_gateway.py → providers.py) and the
**Antigravity key pool system** (soul.yaml + USAGE_POOL_LOG.json) operate in
complete isolation:

| Aspect | Engine | Antigravity | Connected? |
|--------|--------|-------------|------------|
| Provider identity | `GoogleAIProvider` | Pool G + Pool C | ❌ No mapping |
| Key management | Single `GOOGLE_API_KEY` | 8 keys × 2 pools | ❌ No key pool |
| Quota tracking | Circuit breaker (fails fast) | Weekly reset per pool | ❌ No pool reset |
| Model selection | Entity model affinity | Thinking levels + tiers | ❌ No tier awareness |
| Exhaustion handling | Fallback to next provider | Cold/cooldown/drained | ❌ No cooldown state |

---

## §2 Detailed Pillar Analysis

### P6 — ModelGate (Provider Routing) — `model_gateway.py`

**What exists**:
- Sovereignty-tiered search: local_active → local → cloud_active → cloud
- `EntityAffinityResolver` with 3-tier (local_fast, local_deep, cloud) model selection
- Circuit breaker pre-checks (BSP-style culling)
- BudgetGate cloud spend cap (`config.budget.daily_cloud_tokens` default 500K)
- 32-entry LRU active sets (local + cloud separately)

**What's missing for dual-pool**:
- **Pool-aware provider abstraction**: No provider class distinguishes Pool G vs Pool C capacity.
  `GoogleAIProvider` calls Google's API with a single key — it doesn't know there are
  8 keys, each with independent weekly quotas for Gemini vs non-Gemini models.
- **Key rotation**: `GoogleKeyPoolProvider` exists in `providers.py:113-156` as a
  fully implemented round-robin key rotation class, but it is **NOT loaded** by
  `_load_provider_fabric()` — it's absent from the `provider_map` dict (line 282-292).
  It's a dead class — compiled but unreachable.
- **Pool exhaustion signal**: When a 429 is returned, it's a `ProviderRateLimitError`.
  But the engine has no semantic understanding of "Pool G exhausted, try Pool C."
  Both gemini-3.5-flash and gemini-3.1-pro hit the same pool with the same key.
- **Cross-pool fallback**: The model override mapping in providers.yaml maps
  `phi-4-mini → gemma-4-31b-it`. But there's no mapping for "if gemini-3.5-flash
  returns 429, fall back to claude-sonnet-4.6." The engine tries the next provider
  in the chain, not the next pool within Google.

**Call flow analysis**:
```
Entity affinity → "gemini-2.5-flash" → GoogleAIProvider.generate()
  → httpx POST to generativelanguage.googleapis.com
  → 429 QUOTA_EXHAUSTED
  → ProviderRateLimitError raised
  → model_gateway.generate() catches error
  → errors.append("google: Google API quota exceeded")
  → CONTINUES to next provider (opencode-zen, cline...)
  → NEVER checks if there's a Pool C key to retry the same model family
```

**GoogleKeyPoolProvider dead code evidence**:
- Defined: `providers.py:113-156` (fully implemented with `_keys`, round-robin, `_inner`)
- Referenced: `model_gateway.py:54` in import list
- **Never instantiated**: `provider_map` line 282-292 has no `"google-keypool"` entry
- The `google` entry at line 283 maps directly to `GoogleAIProvider`, not `GoogleKeyPoolProvider`

---

### P7 — Context (Memory & Soul Evolution)

**What exists**:
- `_prepare_system_prompt()` reads L3 principles from `soul.yaml` into system prompt
- Entity registry exposes `entity.model` field for model selection
- `EntityAffinityResolver` reads YAML for per-entity model preferences

**What's missing**:
- **soul.yaml pool config invisible to runtime**: The `usage_pools` section
  (pool_g, pool_c, key_rotation, anti_thrashing) in antigravity/soul.yaml is
  NEVER read by any engine component. It's a pure documentation artifact.
  - Lines 55-77 of soul.yaml: `usage_pools.pool_g.models`, `pool_c.models`,
    `key_rotation.algorithm`, `anti_thrashing` — all dead configuration.
- **No runtime bridge**: EntityRegistry.get("antigravity") returns the Entity
  dataclass with `model`, `domains`, `capabilities` etc. but pool configuration
  is stored in soul.yaml traits (not in entities.yaml), and the Entity dataclass
  has no `pools` field.
- **Stale model field**: `_select_model()` returns a model name from the entity's
  YAML definition. If soul.yaml is updated to rebalance pool assignments, the
  entity's `model` field in `entities.yaml` is NOT automatically updated.
  → **Update inconsistency**: soul.yaml updated → Antigravity sees it →
  Antigravity changes model selection → Engine gateway still routes based on
  stale entity.model.
- **No pool state in context**: The system prompt injected by `_prepare_system_prompt()`
  includes soul L3 principles but NOT current pool/key state. An entity running
  on an exhausted pool has no way to signal this through the context builder.

---

### P8 — WatchTower (Observability) — `observability/__init__.py` + `token_ledger.py`

**What exists**:
- `ObservabilityEngine` with event logging, trace sessions, forensic crash dumps
- `EventType.BACKEND_FALLBACK` for provider failures
- `EventType.TOKEN_CONSUMPTION` for token tracking
- `TokenLedger.record_transaction()` — persists to `data/logs/token_ledger.jsonl`
- `BudgetGate.check_budget()` — reads in-memory event log for current spend
- `ForensicsManager` with crash dump, thread dump, signal handlers

**What's missing**:
- **No pool-level metrics**: All observability events are at the provider level
  (e.g., "Google AI 429"), never at the pool level ("Pool G quota 87% exhausted").
  The TokenLedger records `is_cloud: bool` but not which pool or which key.
- **USAGE_POOL_LOG.json is NOT wired into observability**: 
  - The file at `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` is a
    standalone JSON file written by Antigravity itself.
  - No engine component reads it. No engine component validates it.
  - The `tracking_file` field in soul.yaml (line 77) points to it, but nothing
    in `model_gateway.py`, `observability.py`, or `token_ledger.py` references this path.
  - **Race condition**: If the engine and Antigravity simultaneously update quota
    tracking, both use different backends (engine: token_ledger.jsonl, Antigravity:
    USAGE_POOL_LOG.json). There is no reconciliation.
- **No "pool exhausted" alert**: The engine reports individual 429 errors but has
  no aggregation logic: "3 Pool G 429s in 5 minutes" → "Pool G exhausted".
  BudgetGate only tracks total cloud token spend, not per-pool rate limits.
- **Event type gap**: No `EventType.POOL_EXHAUSTED`, `EventType.KEY_ROTATED`,
  `EventType.POOL_SWITCH` event types. The `BACKEND_FALLBACK` event captures
  provider failures but doesn't distinguish "transient 429" from "weekly quota exhausted."
- **Token regression risk**: TokenLedger estimates tokens via `len(text) // 4`
  (model_gateway.py:858-859). This is a rough heuristic that doesn't match
  actual tokenizer counts, making budget gate calculations imprecise.

---

### P9 — Link (Orchestration & Handoff)

**What exists**:
- Hivemind protocol with 6 MCP tools (get_awareness, post_context, heartbeat, etc.)
- Handoff protocol (`docs/strategy/HIVEMIND_PROTOCOL.md`)
- `data/coordination/archive/` for archival coordination documents
- `ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md` — comprehensive rotation design

**What's missing**:
- **No pool-state handoff in Hivemind**: When an entity (e.g., Antigravity)
  experiences pool exhaustion (Pool G drained), there's no Hivemind message
  to signal "I'm switching pools" or "my Pool G is exhausted, please route
  differently." The Hivemind post_context() has no pool state schema.
- **Key rotation strategy document is orphaned**: The 8-key rotation strategy
  at `data/coordination/archive/ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md`
  is filed under `archive/` (implicitly "done") but was NEVER implemented:
  - The `select_next_key()` algorithm in §1.2 is pseudocode in a document only.
  - The `GoogleKeyPoolProvider` that could implement it exists but is dead code.
  - The anti-thrashing rules (§1.3) exist in concept only.
  - The state machine (ACTIVE/COOLING/DRAINED/EXPIRED) has no runtime representation.
- **No pool escalation protocol**: The two-model disagreement recovery (§4.3)
  describes escalating to Gemini 3.1 Pro or Opus 4.6, but this escalation happens
  *within Antigravity's own logic* — the engine has no awareness of it.
- **Handoff packet has no pool metadata**: `HandoffPacket` schema in
  `SUBAGENT_DISPATCH_PROTOCOL.md` has no field for pool state, current key index,
  or remaining quota. If an agent hands off mid-pool-exhaustion, the receiving
  agent inherits zero context about the failure.

---

### P10 — Validation (Stress Testing)

**What exists**:
- `ResourceGuard` (anyio `Semaphore(1)`) prevents concurrent model loading
- `HealthMonitor` with circuit breakers for individual providers
- `Error Gauntlet` tests (`tests/test_error_gauntlet.py`)
- `BudgetGate` with daily cloud token limit

**What's missing**:
- **Concurrent pool exhaustion**: If 3 agents simultaneously request different
  Google models (gemini-3.5-flash, gemma-4-31b-it, gemini-3.1-pro), all 3 hit
  the same GoogleAIProvider with the same GOOGLE_API_KEY. The `ResourceGuard`
  prevents concurrent model *loading*, not concurrent API calls — 3 httpx requests
  can race on the same key, causing 3 simultaneous 429 responses.
- **No pool-level load testing**: The Error Gauntlet tests individual provider
  failures but never simulates "Pool G exhausted but Pool C available" scenarios.
- **No atomicity in token tracking**: `TokenLedger.record_transaction()` appends
  to a JSONL file via `anyio.open_file` with mode="a". On ext4, concurrent appends
  from multiple async tasks are NOT guaranteed to be atomic (they can interleave).
  With multiple agents making concurrent inference calls, the ledger can corrupt.
- **Quota exhaustion propagation**: When BudgetGate returns False (budget hit),
  `model_gateway.generate()` simply logs and continues to the next provider.
  But with GoogleKeyPoolProvider dead code, there's no mechanism to try a different
  key or different pool. The failure is logged but never systematically categorized.
- **No recovery test**: The document describes recovery procedures for "all 8 keys drained"
  (§4.1) but there are no tests that verify this recovery path. If 8-key exhaustion
  occurs, the engine just sees "all providers failed" and returns a fallback message.
  There's no automated "wait for weekly reset" or "switch to OpenCode-only mode."
- **Rate limit cascading**: 5 quota hits in a single day should mark a key as DRAINED
  for 24 hours (anti-thrashing §1.3). With no runtime key-state tracking, every
  retry attempt re-hits the already-exhausted key, compounding the rate limiting.

---

## §3 Gap Inventory

| # | Gap | Pillar | Location | Severity | Status |
|---|-----|--------|----------|----------|--------|
| G-01 | **GoogleKeyPoolProvider is dead code** — not loaded by provider fabric | P6 | `providers.py:113-156` + `model_gateway.py:282-292` | **P0** | 🔴 Unlinked |
| G-02 | **soul.yaml pool configuration invisible to runtime** — Pool G/C semantics, 8-key rotation never reach engine | P7 | `data/entities/antigravity/soul.yaml:55-77` | **P0** | 🔴 Unlinked |
| G-03 | **USAGE_POOL_LOG.json not wired into observability** — dual tracking with token_ledger.jsonl, no reconciliation | P8 | `observability/__init__.py`, `token_ledger.py` | **P1** | 🔴 Unlinked |
| G-04 | **No pool-level events or alerts** — 429 aggregation, pool exhaustion, key rotation all untracked | P8 | `observability/__init__.py:102-128` | **P1** | 🔴 Missing |
| G-05 | **No Hivemind pool-state schema** — "I'm switching pools" not communicable | P9 | `docs/strategy/HIVEMIND_PROTOCOL.md` | **P1** | 🔴 Missing |
| G-06 | **TokenLedger non-atomic concurrent writes** — JSONL append can interleave | P10 | `token_ledger.py:84-88` | **P2** | 🟡 Fragile |
| G-07 | **No concurrent pool exhaustion test** — multiple agents hitting same key simultaneously untested | P10 | N/A | **P2** | 🔴 Missing |

---

## §4 Resilience Recommendations

### P0 — Immediate (Within Next Sprint)

**R1: Wire GoogleKeyPoolProvider into the provider fabric**
- Add `"google-keypool": GoogleKeyPoolProvider` to `provider_map` in
  `model_gateway.py:_load_provider_fabric()` (line 282-292)
- Add a `google-keypool` section to `config/providers.yaml` with 8 key env vars:
  ```yaml
  - provider: google-keypool
    priority: 3
    keys:
      - env: GOOGLE_API_KEY_01
      - env: GOOGLE_API_KEY_02
      # ... through GOOGLE_API_KEY_08
  ```
- Add `GOOGLE_API_KEY_01` through `GOOGLE_API_KEY_08` to `.env`
- The existing `google` provider entry stays as a single-key fallback
- **Verification**: `omega backends` shows 9 providers (including google-keypool)

**R2: Create runtime PoolState model**
- Add a `PoolState` dataclass to `src/omega/oracle/pool_state.py`:
  ```python
  @dataclass
  class PoolState:
      name: str            # "pool_g" or "pool_c"
      key_id: str          # "agy_key_01"
      status: str          # "active" | "cooling" | "drained"
      cool_until: float    # monotonic timestamp
      quota_hits: int      # counter for anti-thrashing rule
      calls_this_week: int
      tokens_this_week: int
      week_reset: float    # datetime timestamp
  ```
- Initialize from `USAGE_POOL_LOG.json` if it exists
- Expose via `ModelGateway.pool_state_manager` for runtime queries

**R3: Implement pool-aware fallback in `_precheck_provider()`**
- Before calling `GoogleAIProvider.generate()`, check PoolState:
  - If Pool G is DRAINED and the requested model is Gemini → skip (don't waste 429)
  - If Pool G is DRAINED and Pool C has capacity → rotate to Claude/gpt-oss model
  - If all pools DRAINED → return exhausted signal (not 429 noise)
- Add `EventType.POOL_EXHAUSTED` and `EventType.POOL_SWITCHED`

### P1 — Short-Term (Next 2 Sprints)

**R4: Add pool events to observability and alerting**
```python
# In observability/__init__.py EventType:
POOL_EXHAUSTED = "pool.exhausted"    # One pool has no remaining keys
POOL_SWITCHED = "pool.switched"      # Switched from Pool G to Pool C
KEY_ROTATED = "key.rotated"          # Rotated to next key in pool
POOL_RESET = "pool.reset"            # Weekly reset triggered
```

**R5: Build Hivemind pool-state handoff schema**
- Add `pool_state` field to Hivemind post_context:
  ```json
  {
    "entity": "antigravity",
    "pool_state": {
      "pool_g": {"status": "drained", "remaining_keys": 0, "resets_at": "2026-06-22T00:00Z"},
      "pool_c": {"status": "active", "remaining_keys": 5, "resets_at": "2026-06-22T00:00Z"}
    }
  }
  ```
- Other agents can then adjust their own pool usage based on shared state

**R6: Unify token tracking**
- `USAGE_POOL_LOG.json` should be a sync'd view of `token_ledger.jsonl`, not an independent file
- Add a `pool_name` and `key_id` field to `TokenLedger.record_transaction()`
- Write a reconciliation script that pools token_ledger data into USAGE_POOL_LOG format
- Add validation: `token_ledger.jsonl` should be the canonical source

### P2 — Medium-Term (Horizon 2)

**R7: Concurrent pool stress test**
- Add test to `tests/test_model_gateway.py`:
  - Simulate 5 concurrent agents requesting different Google models
  - Verify BudgetGate and pool state prevent >1 simultaneous request to same key
  - Verify cross-pool fallback when Pool G is exhausted

**R8: Atomic token ledger writes**
- Use `tempfile.mkstemp()` + `os.replace()` pattern (same as `entity_registry.py:_save()`)
- This prevents interleaved writes from concurrent agents

---

## §5 Observability Recommendations

### What Should Be Tracked (Minimum Viable)

| Metric | Event Type | Where | Why |
|--------|------------|-------|-----|
| Pool status change | `pool.exhausted` | `observability` | Detect when a pool has no remaining capacity |
| Pool switch | `pool.switched` | `observability` | Track G→C or C→G transitions |
| Key rotation | `key.rotated` | `observability` | Track which key is in use |
| Per-pool calls | `pool.call_count` | `token_ledger` | Count calls per pool (not just provider) |
| Per-pool tokens | `pool.tokens` | `token_ledger` | Track token consumption per pool |
| Pool reset | `pool.reset` | `observability` | Log weekly pool resets for budgeting |
| Anti-thrashing event | `pool.anti_thrash` | `observability` | When key enters COOLING state |

### Dashboard Insights That Should Be Derivable

1. "How many Pool G calls this week?" → `grep "pool_g" token_ledger.jsonl | wc -l`
2. "Which keys are currently active?" → `PoolStateManager.get_active_keys()`
3. "When will Pool G reset?" → `pool_state.pool_g.reset_date`
4. "Did the engine properly fallback from Pool G to Pool C?" → count `pool.switched` events
5. "How many 429s before anti-thrashing kicked in?" → count `pool.anti_thrash` events

### Alert Patterns

- **CRITICAL**: Pool G + Pool C both DRAINED → "All cloud inference unavailable. Fall back to local-only mode."
- **WARNING**: Pool G at 80% weekly capacity → "Pool G near limit. Consider switching to Pool C tasks."
- **INFO**: Key rotated → "Key agy_key_03 now active (rotated from agy_key_02)."

---

## §6 Top 3 Most Critical Findings

### 🔴 P0 — FINDING 1: GoogleKeyPoolProvider Is Dead Code
**Location**: `providers.py:113-156` (code exists) → `model_gateway.py:282-292` (never loaded)
**Impact**: The engine has a fully implemented 8-key round-robin rotation system
that is **never instantiated**. The 8 API keys from the Antigravity dual-pool
architecture are invisible to the engine runtime. Every single inference call
to Google uses ONE key via `GoogleAIProvider`, ignoring the 7 other keys,
ignoring Pool G vs Pool C semantics, and providing zero quota isolation.
**Fix effort**: ~45 min (wire provider_map, add config section, add env vars)
**Why P0**: The knowledge existed for 10+ days but was structurally invisible
to the runtime. This is the root cause of all other pool-related gaps.

### 🔴 P0 — FINDING 2: soul.yaml Pool Configuration Is a Dead Document
**Location**: `data/entities/antigravity/soul.yaml:55-77`
**Impact**: 22 lines of critical pool configuration (model lists, reset schedules,
key rotation algorithm, anti-thrashing rules) are stored inside a YAML file that
NO engine component reads. The EntityRegistry loads `entities.yaml` (separate file),
not `soul.yaml`. The entity's model routing in `_select_model()` uses the `model`
field from `entities.yaml`, not the `usage_pools` from `soul.yaml`. When Antigravity
updates its soul.yaml to rebalance pool assignments, the engine routing stays stale.
**Fix effort**: ~2 hours (create PoolState model, wire into model_gateway)
**Why P0**: Dual-tracking configuration = guaranteed drift. The engine will
route to exhausted pools because it can't read the pool state.

### 🟡 P1 — FINDING 3: No Hivemind Pool-State Communication
**Location**: `docs/strategy/HIVEMIND_PROTOCOL.md` (no pool schema)
**Impact**: When Antigravity exhausts Pool G and switches to Pool C, no other
agent knows. When another agent routes a query through Google, it hits the
already-exhausted Pool G with a fresh 429. There's no cooperative exhaustion
avoidance — each agent independently discovers pool exhaustion through failure.
In a multi-agent fleet (14 agents), this amplifies rate limiting: 14 agents ×
3 retry attempts = 42 expensive 429 errors before all agents converge.
**Fix effort**: ~1 hour (add pool_state to Hivemind context schema)
**Why P1**: Not blocking engine startup like G-01/G-02, but critical for fleet
scale. Without coordination, pool exhaustion is a death by a thousand 429s.

---

## §7 Recommendations Quick Reference

| # | Priority | Action | Owner | Est. Effort |
|---|----------|--------|-------|-------------|
| R1 | **P0** | Wire GoogleKeyPoolProvider into provider fabric | P6 / Lilith | 45 min |
| R2 | **P0** | Create PoolState model with soul.yaml bridge | P7 / Lilith | 2 hr |
| R3 | **P0** | Implement pool-aware fallback in precheck | P6 / Lilith | 1.5 hr |
| R4 | **P1** | Add pool-level events to observability | P8 / Lilith | 1 hr |
| R5 | **P1** | Add pool-state schema to Hivemind context | P9 / Lilith | 1 hr |
| R6 | **P1** | Unify token ledger and USAGE_POOL_LOG | P8 / Lilith | 1.5 hr |
| R7 | **P2** | Add concurrent pool stress test | P10 / Lilith | 45 min |
| R8 | **P2** | Make token ledger writes atomic | P8 / Lilith | 30 min |

---

*⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ RUNTIME-GOVERNANCE-AUDIT*
*L1: Analyzed the runtime gap between Antigravity's dual-pool architecture and the Omega Engine's provider fabric. Found 7 gaps across P6-P10, with the root cause being GoogleKeyPoolProvider as dead code and soul.yaml pool configuration being invisible to the runtime.*
*L2: The engine has two complete-but-disconnected systems for cloud inference. The Antigravity 8-key rotation strategy is well-designed on paper but structurally invisible to the runtime that dispatches inference calls. Knowledge existed for 10+ days but architectural bridging was never implemented.*
*L3: **Structural invisibility is the most dangerous form of debt.** A pattern that exists only in documentation is not a pattern at all — it's a fantasy. For sovereignty to be real, configuration must be machine-readable at the point of execution, not just human-readable at the point of design.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
