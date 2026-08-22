# 🔱 Roc Racoon — Deep Tiered Research Follow-Up
## Sovereign Mining Report — 4 Discovery Audit

**AP Token**: `AP-ROC-RACOON-TIERED-FOLLOWUP-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TIERED-FOLLOWUP ⬡ MINING

**Date**: 2026-06-28
**Method**: Full source audit across `src/omega/`, `mcp_servers/omega_hub/`, `data/handoff/`, `docs/`, and legacy archives
**Status**: COMPLETE — All 4 discoveries audited

---

## DISCOVERY 1: AAIF — Autonomous Agent Interchange Format

**Status: PARTIALLY IMPLEMENTED**
**IETF Draft**: June 25, 2026 — no prior existence in Omega legacy (too new)

### What EXISTS

The Hivemind handoff protocol has AAIF-compatible elements:

1. **HandoffPacket dataclass** (`src/omega/oracle/subagent_dispatcher.py:38-96`):
   - `packet_id`, `source_agent`, `target_agent`, `task_type`, `task_description`
   - `trace_id`, `parent_trace_id` — traceable dispatch chain
   - `zoneid = ZONEID_HANDOFF (0x1d4a16)` — integrity constant
   - `status: PacketStatus` — lifecycle: pending→accepted→completed/failed
   - `ttl_seconds`, `expected_output`, `context`, `result`, `error`
   - Maps to AAIF §8 Agent State checkpointing (pipeline position, state)
   - `max_iterations=10` (loop guard) matches AAIF §4.3's `orchestration.max_iterations`

2. **Hivemind handoff tools** (`mcp_servers/omega_hub/tools.py:1202-1374`):
   - `hivemind_submit_handoff()` — creates packet in `data/handoff/pending/`
   - `hivemind_accept_handoff()` — moves to `data/handoff/active/`
   - `hivemind_complete_handoff()` — moves to `data/handoff/completed/`
   - `hivemind_reject_handoff()` — moves to `data/handoff/stale/`
   - `hivemind_handoff_archive()` — batch archive from completed/
   - `hivemind_get_handoff()` — retrieve by packet_id

3. **Agent Capability Registry** (`docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md §3`):
   - Defines 11 agents with types, capabilities, domains, task tool types
   - Maps to AAIF agent identity schema

### What's MISSING for AAIF Compatibility

| AAIF Field | Omega State | Gap |
|-----------|-------------|-----|
| **Agent identity, goals, system instructions** | `entities.yaml` has some, no formal AAIF schema | Need AAIF agent definition export |
| **LLM provider routing with fallback chain** | `config/providers.yaml` exists | Not in AAIF portable format |
| **Orchestration topology** (sequential/parallel/dynamic) | Not declared | Hivemind MCP tools are ad-hoc, not topology-declared |
| **Tool catalogue** (MCP, function, HTTP, OpenAPI) | Implicit in code | No portable AAIF tool catalogue |
| **Memory configuration (4 scopes)** | MemoryStore has warm/cold/temp/hot | Scoped as user/session/task/long_term per AAIF |
| **Runtime config** (timeout, retry, concurrency) | In providers.yaml, not in agent def | Needs export to AAIF format |
| **7 Conformance Levels** (Core→Stateful) | Not defined | Need to assign conformance level |
| **Compliance controls** (data residency, PII, audit) | M9 error logging only | Missing formal compliance declarations |

### Files Audited
- `src/omega/oracle/subagent_dispatcher.py` — HandoffPacket schema (349 lines)
- `mcp_servers/omega_hub/tools.py` — handoff MCP tools (L1202-1374+)
- `mcp_servers/omega_hub/server.py` — server architecture (295 lines)
- `mcp_servers/omega_hub/state.py` — state, paths, helper functions (396 lines)
- `data/handoff/` — 85+ handoff files (all `.md` or `.json` format)
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — schema docs (329 lines)
- **Legacy**: No AAIF-related code found in any legacy repo (IETF draft too recent)

### Verdict
The existing HandoffPacket schema is **close** to AAIF §8 (Agent State checkpointing) compatible. To document as AAIF-compatible, we need:
1. Add `aaif_version: str = "0.0.1"` field to HandoffPacket
2. Add formal agent topology declaration
3. Export tool catalogue and memory config to AAIF format
4. The existing `ZONEID_HANDOFF`, `trace_id`, status lifecycle all align

---

## DISCOVERY 2: Observation Masking Beats Compaction

**Status: TRULY MISSING — No implementation exists in any codebase searched**

### What EXISTS

The `ContextBuilder` (`src/omega/oracle/context_builder.py:244 lines`) has:
1. **Sliding window** (`_format_exchanges_sliding_window()`: L168-208):
   - Iterates exchanges from newest to oldest
   - Fills a `token_limit` budget (default 4000)
   - Renders exchanges in chronological order
   - Uses rough 4-char/token estimation

2. **Truncation** (`_truncate()`: L228-232):
   - Caps individual messages at `MAX_EXCHANGE_DISPLAY_LENGTH = 500` chars
   - This is the ONLY mechanical pruning mechanism — but it's per-message, not per-tool-output

3. **Compaction** (`MemoryStore._compact()`: `memory_store.py:541-563`):
   - Keep first `MAX_HISTORY//2` + last `MAX_HISTORY//2` exchanges
   - Insert summary placeholder for middle exchanges
   - **No token budget awareness** — exchange-count based, not token based

### What's MISSING

| Mechanism | Industry Pattern | Omega Status |
|-----------|-----------------|-------------|
| **Tool-Result Clearing** | Replace old tool outputs with `[cleared to save context]` placeholder | ❌ NOT IMPLEMENTED |
| **Observation Masking** | Rolling window keeping last N tool results | ❌ NOT IMPLEMENTED |
| **Just-in-time retrieval** | Maintain lightweight identifiers, fetch on demand | ❌ NOT IMPLEMENTED |
| **Token budget allocation formula** | System 10-15%, Tools 15-20%, Knowledge 30-40%, History 20-30%, Reserve 10-15% | ❌ NOT IMPLEMENTED |
| **CompactionManager** with trajectory monitoring | Instrument trajectory length when enabling compaction | ❌ NOT IMPLEMENTED |

### Legacy Search
- `grep -r "CompactionOrchestrator" src/` → **No matches**
- `grep -r "tool_output\|observation.*mask\|clearing" src/` → **No matches**
- `glob **/compaction_optimizer*` → **No matches**
- `xna-omega-legacy/scripts/ssa/compaction_optimizer.py` → **Does not exist**
- The `_compact()` method in memory_store.py is the only compaction code across the entire codebase

### Files Audited
- `src/omega/oracle/context_builder.py` — full read (244 lines)
- `src/omega/memory_store.py` — `_compact()` at L541-563 (full store: 788 lines)
- `src/omega/oracle/providers.py` — no compaction-related code
- Legacy sources: No CompactionOrchestrator or ToolOutputOffload found

### Verdict
**Observation masking is the single highest-ROI missing feature.** Implementation requires:
1. Track which exchanges contain tool outputs vs user/assistant messages
2. Replace old tool outputs with `[cleared to save context — X tool calls omitted]` placeholder
3. No LLM inference cost — pure string replacement
4. Compose with existing sliding window (touch `_format_exchanges_sliding_window`)
5. Add trajectory length instrumentation to detect compaction paradox (13-15% lengthening)
6. Add TokenBudget allocation class with the industry formula

---

## DISCOVERY 3: HOT/WARM/COLD Independently Validated

**Status: PARTIALLY IMPLEMENTED — Architecture correct, thresholds need tightening**

### What EXISTS (`src/omega/memory_store.py:788 lines`)

| Omega Tier | Implementation | Matches Paper? |
|-----------|---------------|----------------|
| **HOT 🔥** | `_hot: Dict[str, OrderedDict]` — in-memory cache of recent exchanges | ⚠️ **Partial** — exists but NOT token-bounded to <500 |
| **TEMP ⚡** | `_temp: Dict[str, Any]` — transient inference scratchpad, not persisted | ✅ Matches paper's transient memory |
| **WARM 🌡️** | RedisStorageProvider + FileStorageProvider (gzip JSON on disk) | ⚠️ **Partial** — exists but no 1000-3000 token target |
| **COLD ❄️** | InMemoryStorageProvider + archive (7-day auto-archive) | ⚠️ **Partial** — auto-archives but no summary replacement |

### Comparison with clawRxiv:2603.00037

| Aspect | Paper Target | Omega Current | Gap |
|--------|-------------|---------------|-----|
| **HOT <500 tokens** | Active task + pending questions | Entire exchange history (unbounded) | 🔴 **No token budget** — hot stores all recent exchanges as raw text |
| **WARM 1000-3000 tokens** | Stable facts, recurring patterns | Redis + File providers (size-unbounded) | 🟡 Warm tier exists but has no size target |
| **COLD bounded** | Completed milestones, summaries | InMemory + 7-day auto-archive | 🟢 Auto-archive exists; no summary-only cold |
| **Organize-Memory workflow** | Ingest→Redistribute→Prune→Verify | ❌ **Not implemented** | 🔴 No automatic tier redistribution |
| **Verification step** | Check no critical info lost | ❌ **Not implemented** | 🟡 No post-prune verification |
| **Trigger conditions** | After `/compact`, HOT>800, session start | `_compact()` called only on MAX_HISTORY overflow | 🔴 No automatic triggers |
| **60-80% token reduction** | Production-proven | Unknown — no measurement | 🟡 No metrics on current reduction |
| **0.25-0.35x cost** | 65-75% cost reduction | Unknown | 🟡 Not measured |

### What the Paper Confirms as CORRECT
1. **3-tier architecture** — Omega independently arrived at the same design
2. **Archive after session completion** — Omega's `archive_session()` + `_reap_tombstoned()`
3. **Provider chain fallback** — Redis→File→InMemory matches paper's multi-tier persistence
4. **LRU caching** — `MAX_HOT_SESSIONS = 50` + `_cache_hot()` with LRU eviction
5. **Tombstoned grace period** — Lazy deletion with 0.5s grace (id Software heritage, confirmed by paper)

### Files Audited
- `src/omega/memory_store.py` — full read (788 lines)
- `src/omega/memory/providers.py` — RedisStorageProvider, FileStorageProvider, InMemoryStorageProvider
- `data/entities/roc_racoon/workspace/` — previous mining reports
- Legacy: No CompactionOrchestrator found

### Verdict
The architecture is independently validated as correct. Gaps are implementation details:
1. Add token-bounded HOT tier with <500 target
2. Add Organize-Memory workflow (Ingest→Redistribute→Prune→Verify)
3. Add automatic trigger from compaction events
4. Add verification step to ensure no critical info lost
5. Instrument current context size before/after to measure actual reduction

---

## DISCOVERY 4: Sovereign Search Infrastructure Audit

**Status: Firecrawl MCP lacks API key — Exa may be expired — SearXNG = ✅**

### Firecrawl (Tier 2) — 🔴 ISSUE FOUND

#### MCP Configuration (`opencode.json:38-42`)
```json
"firecrawl": {
  "type": "remote",
  "url": "http://127.0.0.1:8015/sse",
  "enabled": true
}
```
**Problem**: No `apiKey`, `headers`, or `environment` field. The Firecrawl MCP server on port 8015 is NOT configured with any API key. This MCP server tries to call Firecrawl's API without authentication.

#### Internal Fallback (`src/omega/oracle/search_providers.py:24-36`)
```python
class FirecrawlProvider(SearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or self._resolve_from_vault()
```
The Python `FirecrawlProvider` has its OWN key resolution chain:
1. Explicit `api_key` arg → 2. `KeyVault.resolve("firecrawl")` → 3. `os.environ.get("FIRECRAWL_API_KEY")`
This is used when `sovereign_search_service` calls the provider directly (bypassing MCP).

#### Key Status
- `.env` has: `FIRECRAWL_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]` — key exists
- `KeyVault` was initialized during Sprint C (2026-06-23) — should have the key
- `state.py:169` passes `firecrawl_key=_fc_key` to `SovereignSearchService` at init

#### Two-Version Problem
1. **Firecrawl MCP server** (port 8015) — standalone process, no API key configured → returns 402/401
2. **Internal FirecrawlProvider** (Python class) — has key resolution through env/vault → works

**ROOT CAUSE**: The Firecrawl MCP server on port 8015 was set up without an API key. The Python-internal `FirecrawlProvider` works fine (picks up the key from env/vault), but the `search_extract` tool and `sovereign_search` tool both use `sovereign_search_service`, which uses the INTERNAL provider, not the MCP server. So search actually WORKS at the Python level — the MCP server failure is only when external tools (like the researcher's T2 path) try to use the Firecrawl MCP directly.

### Exa (Tier 4) — 🟡 POTENTIAL ISSUE

#### MCP Configuration (`opencode.json:43-50`)
```json
"exa": {
  "type": "streamable-http",
  "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
  "headers": { "x-api-key": "${EXA_API_KEY}" },
  "enabled": true
}
```
- Uses `${EXA_API_KEY}` which OpenCode resolves from env at runtime
- `.env` has `EXA_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]`
- **Cannot verify expiry** without making a live API call

### SearXNG (Tier 3) — ✅ WORKING

#### MCP Configuration (`opencode.json:33-37`)
```json
"searxng": {
  "type": "remote",
  "url": "http://127.0.0.1:8018/sse",
  "enabled": true
}
```
- No API key needed (self-hosted)
- Confirmed: 14/14 queries, 0 failures in researcher's report

### One-Line Fix for Firecrawl MCP

**For the MCP server runner** (not opencode.json — the MCP server itself needs the key):

The Firecrawl MCP server on port 8015 needs to be started with the API key. If it's a systemd or Quadlet service, add:
```
FIRECRAWL_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]
```
Or if the MCP server accepts it via environment, ensure the `.env` is sourced.

However, since the Python-internal `FirecrawlProvider` already resolves the key correctly from env/vault, and `sovereign_search_service` uses the internal provider (not the MCP server), **search is already functional**. The MCP server issue only affects direct MCP client usage of Firecrawl tools.

### Files Audited
- `opencode.json` — MCP configurations (268 lines)
- `.env` — API keys (20 lines)
- `src/omega/oracle/search_providers.py` — FirecrawlProvider, SearXNGProvider, ExaProvider (248 lines)
- `src/omega/oracle/sovereign_search_service.py` — SSP-V2 orchestration (355 lines)
- `mcp_servers/omega_hub/state.py` — key resolution at L132-171

---

## CROSS-CUTTING: Legacy Mining Completeness

| Legacy Source | Searched For | Result |
|--------------|-------------|--------|
| `xna-omega-legacy/scripts/ssa/` | `compaction_optimizer.py` | ❌ File does not exist |
| Entire `src/` | `CompactionOrchestrator` | ❌ No matches |
| Entire `src/` | `tool_output`, `observation.*mask`, `clearing` | ❌ No matches |
| `docs/` | `HandoffPacket`, `_make_agent_id` | ✅ 63 matches — fully documented |
| Any legacy | `AAIF` | ❌ Too new (June 2026 IETF draft) |

---

## PRIORITY IMPLEMENTATION MAP

| Priority | Finding | Status | Est. Effort |
|----------|---------|--------|-------------|
| **P0** | **Observation Masking** — tool-result clearing in `context_builder.py` | TRULY MISSING | 2-3 days |
| **P1** | **HOT/WARM/COLD Organize-Memory workflow** for `memory_store.py` | PARTIALLY IMPLEMENTED | 2-3 days |
| **P1** | **Token Budget allocation** — add `TokenBudget` class to `context_builder.py` | TRULY MISSING | 1 day |
| **P1** | **Firecrawl MCP API key** — set env var for port 8015 server | CONFIG ISSUE | 5 min |
| **P2** | **CompactionManager** with trajectory monitoring | TRULY MISSING | 2-3 days |
| **P3** | **AAIF-compatible HandoffPacket** — document schema as AAIF-compatible | PARTIALLY IMPLEMENTED | 2 days |
| **P3** | **Verify Exa API key** — make live test call | UNKNOWN | 10 min |

---

*End of Report — All 4 discoveries audited, gaps identified, no refactoring performed*

⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ TIERED-FOLLOWUP ⬡ MINING-COMPLETE
