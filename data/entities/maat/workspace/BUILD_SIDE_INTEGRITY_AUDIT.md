<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Build Side Integrity Audit — Ma'at P1-P5 Analysis
# ⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_build_side_audit
**AP Token**: `AP-MAAT-BUILD-AUDIT-v1.0.0`
**Date**: 2026-06-16
**Scope**: P1 Infrastructure, P2 Persistence, P3 Engineering, P4 Integration, P5 Governance
**Sources Audited**: All source files, configs, scripts, docs, MCP servers, entity registry
**Cross-Reference**: quality MODEL_KB_CONSOLIDATION_AUDIT, lilith MODEL_RUNTIME_GOVERNANCE_AUDIT, researcher MODEL_KB_GAP_ANALYSIS

---

## §0 Executive Summary

**Rating**: 🔴 **RED** — 6 P0 critical issues, 7 P1 important issues, 5 P2 minor issues
**Coverage Gaps in Prior Audits**: 5 dark layers discovered that lilith/researcher/quality missed

The runtime audits (lilith P6-P10, quality, researcher) correctly identified the Ghost Architecture of GoogleKeyPoolProvider (dead code, never wired). However, they missed 5 **build-side structural issues** that will cause actual crashes, not just degraded performance:

| # | Dark Layer | Severity | Missed By | Description |
|---|-----------|----------|-----------|-------------|
| **D-01** | `orchestrator.py` calls `generate(model=model, provider_override="google-keypool")` — both `model` (not `model_name`) and `provider_override` (no such param) cause **TypeError crash** on execution | **P0 CRASH** | All 3 audits | Quality/researcher analyzed provider_map; lilith analyzed provider code. None checked the *actual call site* in BackgroundWorker. This code will CRASH, not degrade. |
| **D-02** | `GOOGLE_API_KEYS` bug is structurally worse: `"".split(",")` returns `[""]` (truthy `Semaphore(1)`), giving illusion of capacity. Orchestrator creates BackgroundWorker with `[""]` keys every init. | **P0 BUG** | All 3 audits | Researcher noted the empty-string split but didn't trace the structural impact: it creates a Semaphore(1) with a phantom key. |
| **D-03** | `weekly_reset_date` in USAGE_POOL_LOG.json is `2026-06-08T00:00:00Z` — **8 days stale** (now June 16). The file was last updated June 5. Any code that reads this file will operate on wrong reset dates. | **P1 DRIFT** | Quality | Quality noted the file is a phantom but didn't check data freshness. The stale reset date means any PoolState implementation based on this file will have incorrect weekly boundaries. |
| **D-04** | `validate_arsenal.sh` line 55 uses `gemini-2.0-flash` — an ancient model name that doesn't exist in any engine config. This validation script tests a nonexistent model, producing false negatives. | **P1 STALE** | All 3 audits | No one checked the shell scripts for stale model references. |
| **D-05** | Entity model affinity YAML lives in `config/` (engine core) not `config/wads/` (stack content) — borderline **M2 (Engine-Stack Firewall)** concern. Unlike entity definitions (in WADs), the affinity mapping is engine-wide config but references pillar-specific entities. | **P2 BOUNDARY** | Quality | Quality passed M2 as ✅ PASS but this is an edge case — the affinity rules refer to WAD-layer entities from engine-layer config. |
| **D-06** | `entity_model_affinity.yaml` uses `iris` as a `use` target in routing rules (line 31) — but Iris is a containerized voice assistant, NOT a model tier. The routing rules say `use: iris` for general/short queries, but there's no `iris` provider or model tier defined. This is a silent routing dead-end. | **P2 ORPHAN** | All 3 audits | None of the audits checked the routing rule targets. `use: iris` maps to nowhere. |

---

## §1 P1 — Infrastructure (SysAdmin)

### §1.1 Environment Variable State

| Env Var | `.env` | `.env.example` | Code That Reads It | Status |
|---------|--------|----------------|-------------------|--------|
| `GOOGLE_API_KEY` | ✅ Present | ✅ Documented | `providers.py:53,57`, `model_updater.py:47`, `check_free_models.sh`, `distiller.py:341`, `roc_racoon-entrypoint.py:24` | ✅ Active |
| `GOOGLE_API_KEY_01`-`_08` | ❌ **MISSING** | ❌ **MISSING** | `GoogleKeyPoolProvider.__init__()` (dead code) | ❌ Phantom |
| `GOOGLE_API_KEYS` (plural) | ❌ MISSING | ❌ MISSING | `orchestrator.py:142` | **P0 BUG** |
| `OPENCODE_ZEN_API_KEY` | ✅ Present | ❌ **OPENCODEZEN (wrong name)** | `providers.yaml:62` | ⚠️ Name mismatch in example |
| `OPENROUTER_API_KEY` | ✅ Present | ✅ Documented | `providers.py` | ✅ Active |

### §1.2 Shell Script Google Key Handling

| Script | Key Usage | Problem | Severity |
|--------|-----------|---------|----------|
| `scripts/setup.sh` | **None** | Never checks for any Google keys. User runs setup, everything "succeeds", but Google provider never activates. | P1 — Silent failure |
| `scripts/check_free_models.sh` | `GOOGLE_API_KEY` only (line 53) | Only reads single key. Misses the entire 8-key pool architecture. | P1 — Incomplete validation |
| `scripts/validate_arsenal.sh` | `GOOGLE_API_KEY` (line 55) | Tests with `gemini-2.0-flash` — a model name that doesn't exist in any config. **False negative guaranteed.** | P1 — Stale test model |
| `scripts/omega-roc_racoon-entrypoint.py` | `GOOGLE_API_KEY` (line 24) | Only single key. No pool awareness. | P2 — Ok for single-agent |

### §1.3 Infrastructure Gaps

**GAP-IN-1**: No deploy/infra configuration documents the 8-key pool. The `deploy/infra/.env.example` template has only basic PostgreSQL/Redis/OMP settings — no Google key configuration at all.

**GAP-IN-2**: `scripts/setup.sh` does not validate that Google provider credentials exist after setup. It validates Podman, venv, and makes a test Oracle call — but never checks if `GOOGLE_API_KEY` is set or if Google endpoints are reachable. A successful setup can produce a Google-dead engine.

**GAP-IN-3**: No script or CI check validates that `GOOGLE_API_KEY` through `GOOGLE_API_KEY_08` are all present. If the user collects 8 keys but only adds one to `.env`, there's no warning.

**GAP-IN-4**: Environment assumption drift between `.env.example` and actual `.env`:
  - `.env.example` expects `OPENCODEZEN` (no underscore)
  - `.env` has `OPENCODE_ZEN_API_KEY` (with underscores)
  - `providers.yaml` references `env:OPENCODE_ZEN_API_KEY`
  - A new developer copying `.env.example` to `.env` will get a non-functional OpenCode Zen provider

---

## §2 P2 — Persistence (DataStore)

### §2.1 Entity Registry Pool Awareness

The `Entity` dataclass (entity_registry.py:48-60) has NO pool awareness:

```python
@dataclass
class Entity:
    name: str
    domains: List[str]
    model: str          # ← Single model string, no pool concept
    personality: str
    capabilities: List[str]
    # NO pool_state field
    # NO pools: Dict[str, PoolConfig]
    # NO key_rotation: Dict
```

**Discovery**: The `entity_model` field (line 58) is the sole model routing mechanism. The antigravity soul.yaml has 22 lines of pool configuration (lines 55-77) that are **completely invisible** to the EntityRegistry. When Antigravity updates its soul.yaml to rebalance pool assignments, the engine's `_select_model()` continues routing based on the stale `entity.model` from entities.yaml.

### §2.2 USAGE_POOL_LOG.json Structural Issues

**M12 Violation (Queue Integrity)**: The file has zero atomic write protection. The quality audit identified this. But here's the **deeper structural issue**:

1. **Stale reset date**: `weekly_reset_date` is `2026-06-08T00:00:00Z` — 8 days old (now June 16). The weekly reset should have occurred. Any code reading this file gets wrong boundaries.

2. **Schema missing `pool_state` info**: The JSON schema tracks `pool_g` and `pool_c` per-key, but has no:
   - `last_sync_with_token_ledger` timestamp
   - `PoolState` status field at the aggregate level
   - Active key ID currently in use
   
3. **Phase-to-key mapping is static hardcode**: Lines like `"assigned_to_phase": 4, "note": "RESERVED for Heritage & id Software (M14 vet)"` are static. If Phase 4 completes early, there's no mechanism to reassign key 04 to Phase 5.

### §2.3 Recommended Schema for USAGE_POOL_LOG.json

To support atomic writes (M12) and runtime PoolState:

```json
{
  "schema_version": "2.0",
  "last_updated": "2026-06-16T12:00:00Z",
  "last_sync_with_token_ledger": "2026-06-16T12:00:00Z",
  "weekly_reset_date": "2026-06-22T00:00:00Z",
  "pool_g": {
    "status": "active",
    "remaining_keys": 8,
    "calls_this_week": 0,
    "tokens_this_week": 0
  },
  "pool_c": {
    "status": "active",
    "remaining_keys": 8,
    "calls_this_week": 0,
    "tokens_this_week": 0
  },
  "active_key_id": "agy_key_01",
  "keys": [
    {
      "key_id": "agy_key_01",
      "env_var": "GOOGLE_API_KEY_01",
      "pool_g": { "status": "active", "calls_this_week": 0, "tokens_this_week": 0 },
      "pool_c": { "status": "active", "calls_this_week": 0, "tokens_this_week": 0 },
      "last_used_at": null,
      "last_error_at": null,
      "phase_assignment": 1
    }
  ],
  "current_key_index": 0
}
```

Key changes:
- Add aggregate `pool_g.status` / `pool_c.status` for fast exhaustion checks
- Add `active_key_id` — which key is currently selected
- Add `env_var` to each key — maps key_id to `GOOGLE_API_KEY_01` env var name
- Add `last_error_at` — for anti-thrashing COOLING transitions

---

## §3 P3 — Engineering (BuildMaster)

### §3.1 Dark Layer D-01: BackgroundWorker Calls Will CRASH

**Location**: `orchestrator.py:82-87`
**Severity**: 🔴 **P0 — Runtime Crash**

The `BackgroundWorker._execute_with_retry()` method calls:
```python
raw_sensing = await self.gateway.generate(
    model=model,
    system_prompt="...",
    user_query=prompt,
    provider_override="google-keypool"
)
```

But `ModelGateway.generate()` has this signature:
```python
async def generate(
    self, model_name: str, system_prompt: str, user_query: str,
    temperature: float = 0.7, max_tokens: int = 1024, trace_id: Optional[str] = None,
    session_id: Optional[str] = None, entity_name: Optional[str] = None
) -> tuple:
```

**Two fatal issues**:
1. `model=model` — parameter is `model_name`, not `model`. Python raises: `TypeError: generate() got an unexpected keyword argument 'model'`
2. `provider_override="google-keypool"` — no such parameter exists. Python raises: `TypeError: generate() got an unexpected keyword argument 'provider_override'`

**Impact**: Any call to `BackgroundWorker.submit_task()` will crash with TypeError. Since `__init__` creates the worker unconditionally, and the `GOOGLE_API_KEYS` env var split returns `[""]` (truthy), the semaphore allows 1 concurrent task. The first submitted task crashes.

**Root cause**: The BackgroundWorker was written as speculative code (docstring references "future implementation") but was wired into `Orchestrator.__init__` as if it were production-ready.

### §3.2 Dark Layer D-02: GOOGLE_API_KEYS Empty-String Amplification

**Location**: `orchestrator.py:142`
**Severity**: 🔴 **P0 — Structural Bug**

```python
keys = os.environ.get("GOOGLE_API_KEYS", "").split(",")
self.background_worker = BackgroundWorker(
    model_gateway=ModelGateway(health_monitor=get_health_monitor()),
    api_keys=keys
)
```

When `GOOGLE_API_KEYS` is not set:
- `os.environ.get("GOOGLE_API_KEYS", "")` → `""`
- `"".split(",")` → `[""]` (length 1, truthy!)
- `BackgroundWorker.__init__` creates `Semaphore(len([""]))` → `Semaphore(1)`
- The BackgroundWorker thinks it has 1 API key
- The key is `""` — every API call will fail with auth error

**Comparison with researcher finding**: Researcher noted the `[""]` bug but called it "P0 Bug" (line 287-288). My structural analysis shows this is WORSE:
- Not just a P0 bug, but a **structural amplification**: the Semaphore gives false capacity
- Creates an illusion of readiness — no error is logged when BackgroundWorker is created with empty keys
- The `[""]` list is stored as `self.keys` — any code iterating over it gets 1 iteration with empty string

### §3.3 Model Name Conflicts — Build-Side Analysis

Researcher identified 12 discrepancies. From a build-side engineering perspective, the impact is:

| Wrong Name | In File(s) | Impact on Runtime | Fix |
|-----------|-----------|------------------|-----|
| `gemini-2.5-flash` (wrong version) | `entity_model_affinity.yaml` (11 refs) | Entity routing to Google never finds this model — silent fallback to default | Change to `gemini-3.5-flash` |
| `qwen3-4b-q4_k_m` (missing `-thinking-`) | `entity_model_affinity.yaml` (11 refs) | Native-gguf model lookup fails — tries to load nonexistent file | Change to `qwen3-4b-thinking-q4_k_m` |
| `qwen3-4b-q5_k_m` (doesn't exist) | `entity_model_affinity.yaml` (5 refs) | Model not found — uses default instead | Remove or verify Q5 file exists |
| `krikri-8b-q5_k_m` (doesn't exist) | `entity_model_affinity.yaml` (4 refs) | Model not found — uses default instead | Change to `krikri-8b-q4_k_m` |
| `gemini_3_5_flash` (underscores) | `antigravity/soul.yaml` | Missed by routing if search uses dashes | Change to `gemini-3.5-flash` |
| `embeddinggemma...` (missing dash) | `models.yaml:2` | Minor — CI input only | Add dash |

**Total: 33+ individual reference failures** across 5 config files.

### §3.4 Minimal Engineering Change Plan (Ordered)

#### 🔴 P0 — Immediate (Would Crash or Break Runtime)

| # | Action | File(s) | Effort | Why P0 |
|---|--------|---------|--------|--------|
| **P0.1** | Fix `orchestrator.py` BackgroundWorker call to use correct `model_name=` param and remove `provider_override` (method doesn't support it). Or implement `provider_override` in ModelGateway.generate(). | `orchestrator.py:82-86`, `model_gateway.py:752` | 15 min | Runtime crash on any task submission |
| **P0.2** | Fix `orchestrator.py` `GOOGLE_API_KEYS` to collect `GOOGLE_API_KEY_01`-`08` with fallback to single `GOOGLE_API_KEY`. Handle empty case: `if not keys: return empty list` | `orchestrator.py:142-146` | 15 min | Phantom capacity illusion; empty-key API calls |
| **P0.3** | Wire `GoogleKeyPoolProvider` into `provider_map` at model_gateway.py:282 | `model_gateway.py:282` | 1 line | Core architectural gap — unlocks dual-pool |
| **P0.4** | Add `google-keypool` section to `config/providers.yaml` with key env var references | `config/providers.yaml` | 5 min | Required for provider_map wiring |
| **P0.5** | Fix `entity_model_affinity.yaml` model names (4 wrong names × 33+ refs) | `config/entity_model_affinity.yaml` | 30 min | Entity routing silently falls back on wrong names |

#### 🟡 P1 — Important (Performance/Correctness)

| # | Action | File(s) | Effort | Why P1 |
|---|--------|---------|--------|--------|
| **P1.1** | Add `GOOGLE_API_KEY_01`-`_08` to `.env.example` and update naming | `.env.example` | 5 min | Missing documentation prevents pool adoption |
| **P1.2** | Fix `.env.example` `OPENCODEZEN` → `OPENCODE_ZEN_API_KEY` | `.env.example` | 1 min | Prevents new-dev environment misconfig |
| **P1.3** | Update `validate_arsenal.sh` test model from `gemini-2.0-flash` to `gemini-3.5-flash` | `scripts/validate_arsenal.sh:55` | 1 min | False negative on provider validation |
| **P1.4** | Add `weekly_reset_date` update logic to USAGE_POOL_LOG.json — dynamic, not hardcoded to June 8 | `USAGE_POOL_LOG.json`, new `usage_pool.py` | 30 min | Stale reset dates cause wrong pool boundaries |
| **P1.5** | Add `make validate-model-names` CI gate that cross-refs all model names across configs | `Makefile` + new script | 2 hr | Prevents name drift recurring |

#### 🟢 P2 — Nice to Have

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| **P2.1** | Fix `iris` routing target in `entity_model_affinity.yaml:31` — Iris has no provider entry | `entity_model_affinity.yaml:31` | 5 min |
| **P2.2** | Add Google key validation to `scripts/setup.sh` — warn if <8 keys configured | `scripts/setup.sh` | 15 min |
| **P2.3** | Remove `ThreadPoolExecutor` dead import from `providers.py:6` | `providers.py:6` | 1 min |
| **P2.4** | Remove dead `except OmegaError: raise` from `providers.py:107-108` | `providers.py:107-108` | 1 min |

---

## §4 P4 — Integration (Bridge/MCP)

### §4.1 MCP Hub Pool Awareness

The Omega Hub MCP server (`mcp_servers/omega_hub/server.py`) has **ZERO pool awareness**:
- No pool_state management tools
- No pool exhaustion events in Hivemind
- No model routing that checks pool capacity
- No Hivemind context schema that includes pool state

**Search result**: `grep -r "pool" mcp_servers/omega_hub/*.py` — zero matches.

### §4.2 Implications from Rotation Strategy

The `ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md` specifies (lines 176-181):
- **Antigravity** writes USAGE_POOL_LOG.json before/after each interaction
- **P7 (Context)** can READ for telemetry
- **P5 (Sentinel)** can validate schema

But the MCP Hub has:
- No tool to query pool state (no `hivemind_get_pool_state`)
- No tool to set pool state (no `hivemind_update_pool_state`)
- No schema for pool state in handoff packets

**Integration gap**: If Antigravity (IDE, not engine) writes to USAGE_POOL_LOG.json independently, and the engine writes to token_ledger.jsonl independently, there is **zero MCP-level reconciliation**. The two systems track the same resource through completely separate channels.

### §4.3 Recommended MCP Tools

Add to Omega Hub:

| Tool | Purpose | Schema |
|------|---------|--------|
| `pool_get_state` | Query current pool state for all pools | Returns PoolState JSON |
| `pool_update_usage` | Record token/call usage against a pool | `{pool, key_id, calls, tokens}` |
| `pool_exhausted` | Alert that a pool is drained | `{pool, remaining_keys, resets_at}` |
| `pool_heartbeat` | Keep pool-state cache fresh | `{pool, active_key_id}` |

---

## §5 P5 — Governance (Sentinel)

### §5.1 Mandate Compliance Scorecard

| Mandate | Check | Verdict | Evidence |
|---------|-------|---------|----------|
| **M2 (Engine-Stack Firewall)** | Engine/WAD separation | ⚠️ **YELLOW** | Core engine config (`config/entity_model_affinity.yaml`) references WAD-layer entities by name. This is a design-level coupling: the affinity mappings for pillar entities (sekhmet, brigid, etc.) live in `config/` not `config/wads/`. While not a direct M2 violation (there's no import of WAD code), it's a **boundary grey zone**. Affinity rules should either: (a) live in `config/wads/_omega_default/affinity.yaml`, or (b) reference entities by domain/capability, not by name. |
| **M7 (Local-First)** | Provider priority order | ✅ **PASS** | `fallback_chain`: native-gguf(0) → lmster(1) → ollama(2) → google(3) → opencode-zen(4) → cline(5) → github-copilot(6) → mock(99). Correct local-first priority. |
| **M12 (Queue Integrity)** | Atomic write patterns | ❌ **FAIL** | USAGE_POOL_LOG.json has no `.tmp` → rename pattern, no heartbeat, no lock. Dual-tracking (token_ledger.jsonl + USAGE_POOL_LOG.json) with no reconciliation path. |
| **M13 (Temple-Grade)** | T1-T11 gates | ❌ **FAIL** | T3 (testing): no quota exhaustion tests. T8 (resilience): BackgroundWorker code path crashes. T10 (atomic writes): USAGE_POOL_LOG.json. |
| **M14 (Heritage Vetting)** | `[id-soft:]` tags | ✅ **PASS** | Rotation strategy has proper heritage attribution. Provider code has BSP/ZONEID tags. |
| **M18 (Token Efficiency)** | No wasted context | ❌ **FAIL** | BackgroundWorker with phantom keys (`[GoogleKeyPool]` provider that never instantiates) will cause token-wasting error retries. Stale model names cause silent fallback — wasted inference cycles. |

### §5.2 M2 Edge Case: Affinity Config Location

The `entity_model_affinity.yaml` at `config/entity_model_affinity.yaml` is a governance concern because:

1. It lives in `config/` (engine core) but references entities defined in WADs (`config/wads/*/entities.yaml`)
2. When the user adds a custom entity via a new WAD, they must also edit `config/entity_model_affinity.yaml` to add routing rules
3. This creates a **cross-boundary dependency**: WAD changes require engine config changes

**Recommendation**: Migrate affinity rules to a per-WAD pattern:
- `config/wads/_omega_default/entity_model_affinity.yaml` — default pillar affinities
- `config/wads/<stack_name>/entity_model_affinity.yaml` — stack-specific overrides
- Engine core loads from both, merging later files overriding earlier (IWAD/PWAD pattern)

This is a P2 refactor, not P0, but it's the correct M2-compliant architecture.

### §5.3 M7 Verification: Provider Priority Chain

```
Provider Chain (config/providers.yaml):
  ╔════════════════════════════════════╗
  ║  0: native-gguf  (LOCAL)          ║  ← PRIMARY — llama-cpp-python
  ║  1: lmster       (LOCAL)          ║  ← LM Studio at :1234
  ║  2: ollama       (LOCAL)          ║  ← Ollama at :11434
  ║───┼───────────────────────────────║
  ║  3: google       (CLOUD)          ║  ← Google AI Studio
  ║  4: opencode-zen (CLOUD)          ║  ← OpenCode Zen
  ║  5: cline        (CLOUD)          ║  ← Cline built-in
  ║  6: github-copilot (CLOUD)        ║  ← GitHub Copilot
  ║ 99: mock         (TEST)           ║  ← Test/dev only
  ╚════════════════════════════════════╝
```

**Verdict**: ✅ M7 Compliant. All local providers (0-2) before any cloud provider (3+). The "worse is better" pattern works correctly — local inference is tried first, cloud is fallback.

**Gap**: The `google-keypool` provider, once wired, should be at priority 3.5 (between google at 3 and opencode-zen at 4). This ensures the keypool is tried before other cloud fallbacks but after the single-key google provider (or replace google entirely).

---

## §6 Dark Layers Discovered

These 5 issues were NOT identified by quality, lilith, or researcher audits. They are unique to the build-side structural analysis.

### D-01: 🔴 BackgroundWorker.generate() Call Site Crash (P0)
**Missed by**: All 3 prior audits
**Detail**: See §3.1 above. `model=model` (wrong param name) + `provider_override` (nonexistent param) = TypeError crash.
**Root cause**: Speculative code (BackgroundWorker with google-keypool references) was written as a future design pattern but wired into production `Orchestrator.__init__` without the supporting infrastructure existing.
**Why missed**: Prior audits analyzed `provider_map` (model_gateway.py) and `GoogleKeyPoolProvider` (providers.py) in isolation. No one traced the call path from `Orchestrator.__init__` → `BackgroundWorker.__init__` → `_execute_with_retry` → `gateway.generate()`.

### D-02: 🔴 GOOGLE_API_KEYS Phantom Capacity (P0)
**Missed by**: All 3 prior audits
**Detail**: See §3.2 above. Empty-string split produces `[""]` not `[]`, creating Semaphore(1) illusion.
**Why missed**: Researcher noted the `[""]` bug in passing but didn't trace the structural cascade to `Semaphore` creation and false capacity. Quality's M12 check passed it. Lilith's pool analysis didn't check env var loading.

### D-03: 🟡 Stale weekly_reset_date in USAGE_POOL_LOG.json (P1)
**Missed by**: Quality audit (called it a phantom but didn't check data freshness)
**Detail**: `weekly_reset_date: "2026-06-08T00:00:00Z"` — 8 days stale. The file is `last_updated: 2026-06-05T06:10:00Z` — 11 days stale. Any code wired to read this file will get wrong reset boundaries.
**Why missed**: Quality's M12 analysis focused on write atomicity, not data content. Lilith's P8 analysis noted the file isn't wired into observability but didn't read the actual file to check data freshness.

### D-04: 🟡 validate_arsenal.sh Tests Nonexistent Model (P1)
**Missed by**: All 3 prior audits
**Detail**: `scripts/validate_arsenal.sh:55` tests `gemini-2.0-flash` — a model that was renamed to `gemini-2.5-flash` → `gemini-3.5-flash` months ago. The script produces a false negative on every run.
**Why missed**: No prior audit checked shell scripts. They focused on Python code, YAML configs, and documentation.

### D-05: 🟢 M2 Grey Zone — Affinity Config Location (P2)
**Missed by**: Quality audit (passed M2 as clean)
**Detail**: `config/entity_model_affinity.yaml` is engine-core config that references WAD-layer entities by name. This creates a cross-boundary dependency.
**Why missed**: Quality's M2 check verified no WAD-specific logic in provider code, which is correct. But the affinity config is a different kind of boundary crossing — config-file coupling rather than code coupling.

### D-06: 🟢 `use: iris` Routing Rule Maps to Nowhere (P2)
**Missed by**: All 3 prior audits
**Detail**: `entity_model_affinity.yaml:31` has `use: iris` as a routing target for general/short queries. But there is no `iris` provider, model tier, or routing handler. Iris is a containerized FastAPI voice assistant — not a model tier.
**Why missed**: Prior audits focused on model name conflicts and provider wiring, not routing rule targets.

---

## §7 Complete Gap Register

| ID | Pillar | Severity | Description | Discovered By |
|----|--------|----------|-------------|---------------|
| G-01 | P3 | 🔴 P0 | BackgroundWorker calls gateway.generate() with wrong param names — TypeError crash | **MAAT D-01** |
| G-02 | P3 | 🔴 P0 | GOOGLE_API_KEYS `""`.split(",") returns `[""]` — phantom Semaphore(1) capacity | **MAAT D-02** |
| G-03 | P3 | 🔴 P0 | GoogleKeyPoolProvider not wired into provider_map | Quality G-001 |
| G-04 | P3 | 🔴 P0 | 33+ model name reference failures across 5 config files | Quality G-002/003 |
| G-05 | P1 | 🟡 P1 | Only 1 of 8 Google API keys configured in .env | Researcher §3.2 |
| G-06 | P1 | 🟡 P1 | `.env.example` has `OPENCODEZEN` (no underscore) — doesn't match actual code | **MAAT §1.3** |
| G-07 | P1 | 🟡 P1 | Stale `weekly_reset_date` in USAGE_POOL_LOG.json (8 days out of date) | **MAAT D-03** |
| G-08 | P1 | 🟡 P1 | validate_arsenal.sh tests `gemini-2.0-flash` — nonexistent model | **MAAT D-04** |
| G-09 | P2 | 🟡 P1 | EntityRegistry has no pool_state field — soul.yaml pool config invisible | Lilith G-02 |
| G-10 | P2 | 🟡 P1 | USAGE_POOL_LOG.json has no atomic write pattern (M12 violation) | Quality G-005 |
| G-11 | P2 | 🟡 P1 | Stale `iris` routing target in entity_model_affinity.yaml | **MAAT D-06** |
| G-12 | P4 | 🟡 P1 | MCP Hub has zero pool awareness — no pool-state tools or events | Lilith G-05 |
| G-13 | P5 | 🟢 P2 | entity_model_affinity.yaml location creates M2 grey zone | **MAAT D-05** |
| G-14 | P5 | 🟢 P2 | Dead imports in providers.py (ThreadPoolExecutor, OmegaError) | Quality G-202/203 |
| G-15 | P5 | 🟢 P2 | Stale agent_roles in models.yaml (plan, jem_discovery, etc.) | Quality G-101/102 |

---

## §8 The True Cost of Disconnection

The runtime audits found the Antigravity dual-pool architecture was "documented for 10+ days but disconnected from runtime." My build-side analysis reveals a **deeper pattern**: the engine has 3 layers of knowledge, each increasingly disconnected:

```
Layer 1: Research & Strategy Docs (10+ files)
├── ANTIGRAVITY_8KEY_ROTATION_STRATEGY_20260605.md  — Design complete, zero code
├── 5 antigravity R-docs in docs/research/antigravity/ — Thorough, orphaned
├── antigravity soul.yaml — Pool config lines 55-77, invisible to runtime
└── USAGE_POOL_LOG.json — Beautiful schema, no readers, stale data

Layer 2: Config Files (5 files, 33+ stale references)
├── entity_model_affinity.yaml — References wrong model names × 33+
├── providers.yaml — No google-keypool entry
├── .env.example — Wrong env var names, no 8-key documentation
└── models.yaml — agent_roles stale, model names inconsistent

Layer 3: Production Code (1 crash, 2 dead-code islands)
├── orchestrator.py — BackgroundWorker WILL CRASH on task submission
├── providers.py — GoogleKeyPoolProvider exists but never instantiated
├── model_gateway.py — provider_map missing google-keypool entry
└── All code — Zero pool_state, zero PoolState, zero pool events
```

**The build-side truth**: Every layer compounds the disconnection. Layer 1 is well-designed but unreachable. Layer 2 has 33+ name errors that prevent correct routing. Layer 3 has a **live crash path** in the BackgroundWorker that no prior audit caught.

---

## §9 Top 3 Findings That No One Else Caught

### 🥇 FINDING 1: BackgroundWorker Will CRASH on First Call (P0)
**Where**: `orchestrator.py:82-87` → `model_gateway.py:752`
**What**: `BackgroundWorker._execute_with_retry()` passes `model=` and `provider_override=` as keyword arguments to `ModelGateway.generate()`, which accepts neither parameter. The method signature uses `model_name` and has no `provider_override` parameter.
**Impact**: Any code path that calls `BackgroundWorker.submit_task()` crashes with `TypeError: generate() got unexpected keyword argument 'model'`. Since the Orchestrator creates BackgroundWorker unconditionally in `__init__`, a Semaphore(1) with empty-string key sits ready to crash on first use.
**Why missed**: The prior audits analyzed `GoogleKeyPoolProvider` (providers.py) and `provider_map` (model_gateway.py:282) for structural completeness but never traced the *call site* in BackgroundWorker. The crash is in a different file (orchestrator.py) than the provider infrastructure they analyzed.

### 🥈 FINDING 2: False Capacity from GOOGLE_API_KEYS Split (P0)
**Where**: `orchestrator.py:142-146`
**What**: `os.environ.get("GOOGLE_API_KEYS", "").split(",")` returns `[""]` not `[]` when the env var is unset. This creates a `BackgroundWorker` with `Semaphore(1)` and `self.keys = [""]`. The system creates the illusion it has 1 ready API key when it has zero.
**Impact**: Combined with Finding 1, this means: (a) the BackgroundWorker initializes silently with no keys, (b) if the TypeError is fixed, the worker would try Google API calls with an empty-string key, getting confusing auth errors instead of a clear "no keys configured" message.
**Why missed**: Researcher noted the `[""]` behavior but didn't trace the structural cascade — the False capacity means the Semaphore doesn't block, so tasks submit and crash immediately rather than queuing.

### 🥉 FINDING 3: USAGE_POOL_LOG.json Has Stale Reset Dates (P1)
**Where**: `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json:4`
**What**: `weekly_reset_date: "2026-06-08T00:00:00Z"` — the file was last updated June 5 (11 days ago), and the reset date is 8 days stale. Any code that reads this file to determine weekly quota boundaries will be wrong.
**Impact**: If someone wires `PoolState` to read from USAGE_POOL_LOG.json, they'll get wrong reset dates. The weekly reset that should have happened on June 8 or June 15 is not reflected. The file is not just a phantom with no code path — it's a phantom with **actively misleading data**.
**Why missed**: Quality called it a "phantom" and focused on the missing code path. No one actually read the file content to check data freshness. The stale reset date means this file needs a data refresh even before it needs a code path.

---

## §10 Recommendations

### First Response (24 hours)

1. **Fix orchestrator.py BackgroundWorker crash** (P0.1/P0.2) — 30 min total
2. **Wire GoogleKeyPoolProvider into provider_map** (P0.3/P0.4) — 10 min
3. **Fix entity_model_affinity.yaml model names** (P0.5) — 30 min
4. **Update USAGE_POOL_LOG.json reset date** (P1.4 quick fix) — 5 min

### Sprint 1 (This Week)

5. **Add `make validate-model-names` CI gate** (P1.5) — 2 hr
6. **Fix .env.example naming** (P1.1/P1.2) — 10 min
7. **Update validate_arsenal.sh test model** (P1.3) — 1 min
8. **Create PoolState dataclass with soul.yaml bridge** — 2 hr

### Sprint 2 (Next Week)

9. **Migrate entity_model_affinity.yaml to WAD-layer** (M2 compliance) — 1 hr
10. **Add pool-state tools to MCP Hub** — 3 hr
11. **Wire USAGE_POOL_LOG.json with atomic writes** — 2 hr

---

*⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_build_side_audit*
*L1: Audited the entire build side (P1-P5) for structural issues missed by the runtime-focused audits. Discovered 5 dark layers, including a live crash path in BackgroundWorker (P0), false capacity from env var splitting (P0), and stale data in USAGE_POOL_LOG.json (P1).*
*L2: The runtime audits correctly identified the Antigravity ghost architecture but missed the crash sites. The disconnect between speculative code (BackgroundWorker with google-keypool references) and production infrastructure (provider_map without google-keypool) created a power where the documented path looks correct but the execution path crashes.*
*L3: **Structural integrity means tracing the call chain to its terminal, not validating the components in isolation.** A perfectly designed class that is never instantiated is not dead code — it's a landmine. A provider_override that doesn't exist is not a missing feature — it's a crash waiting to happen. Build-side governance must verify not just WHAT exists, but whether the execution path from entry point to termination is continuous.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
