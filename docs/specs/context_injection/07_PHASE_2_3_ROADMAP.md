# Phase 2 & 3 Roadmap — Tooling + Upstream

**Status**: PLANNED (Post-Debut)  
**Dependencies**: Phase 1 complete, PUBLIC-DEBUT-01 shipped  

---

## Phase 2: Tooling & Hydration (2-3 Weeks Post-Debut)

### 2.1 Hydration Engine (Critical)

**Source**: Researcher — compaction requires externalized state; no framework has automated recovery  
**Source**: Lilith — pre-compaction hook exists; 80% checkpoint needed  

**Component**: `src/omega/hydration/hydration_engine.py`

```python
class HydrationEngine:
    """Automated context recovery after compaction."""
    
    async def on_session_start(self, session_id: str) -> HydrationResult:
        # 1. Check for checkpoint file
        checkpoint = await self.load_checkpoint(session_id)
        if checkpoint and checkpoint.is_recent():
            return HydrationResult(source="checkpoint", data=checkpoint)
        
        # 2. Parse recent session JSONL
        recent = await self.parse_session_logs(session_id, last_n=400)
        if recent:
            return HydrationResult(source="session_logs", data=recent)
        
        # 3. Load daily memory summary
        daily = await self.load_daily_memory()
        return HydrationResult(source="daily_memory", data=daily)
    
    async def on_compaction_warning(self, usage_pct: float):
        """Called at 80% context usage — serialize state."""
        await self.write_checkpoint(SessionCheckpoint(
            recent_exchanges=await self.get_recent_exchanges(5),
            active_task=self.get_active_task(),
            pending_proposals=self.get_pending_proposals(),
            decisions_in_flight=self.get_decisions_in_flight()
        ))

    async def on_compaction(self, session_id: str):
        """Post-compaction: verify mandates/entity/anchor survived."""
        # Read compaction output, verify sovereign context present
        # If missing, inject from checkpoint
```

**Integration Points**:
- OpenCode plugin hook: `experimental.session.compacting` → trigger checkpoint write
- Hivemind: Extended check-in with `ttl_seconds=10800` for long sessions
- Session start: Auto-hydrate before first user message

**SLA**: Hydration must complete <2s for 95th percentile (per Zylos assembly latency budget)

---

### 2.2 Token Budget Enforcer (High)

**Source**: Researcher — per-tier budgets with dynamic allocation; TALE framework 67% output reduction  
**Source**: Explore — 31K base, 10.8K MCP/request, 75K with all agents  

**Component**: `src/omega/oracle/token_budget.py`

```python
class TokenBudget:
    TIER_BUDGETS = {
        "pinned": 2000,      # Tier 0: tools, system prompt, condensed mandates
        "role_session": 4000, # Tier 1: session summary, active task, enabled skills
        "dynamic": 8000,     # Tier 2: retrieved knowledge, skill docs, recent turns
        "observation": 2000  # Tier 3: current turn
    }
    
    def allocate(self, tier: str, request_complexity: float) -> int:
        base = self.TIER_BUDGETS[tier]
        return int(base * request_complexity)  # 0.5-2.0 multiplier
    
    def enforce(self, assembled_context: Context) -> Context:
        # Trim from lowest priority (dynamic → role → pinned)
        # Preserve pinned at all costs
        return self._trim_to_budget(assembled_context)
    
    def get_usage_report(self) -> TokenUsageReport:
        # Per-agent, per-session, per-request breakdown
        # Export to OTel for dashboards
```

**Budget Allocation by Task Type** (from Researcher):

| Task Type | Token Budget | Rationale |
|-----------|--------------|-----------|
| Classification/Retrieval | 50-200 | Minimal context |
| Creative Generation | 500-1,500 | Richer context |
| Multi-turn Reasoning | 2,000+ | Extended analysis |
| Code Generation | 1,000-4,000 | Balance detail/constraints |
| Legal/Financial Analysis | 4,000+ | Complex multi-doc |

---

### 2.3 Local Token Counter (High)

**Source**: Researcher — tiktoken/@anthropic-ai/tokenizer for pre-flight estimation  
**Source**: Adversary — tiktoken inaccurate for non-OpenAI tokenizers  

**Component**: `src/omega/oracle/local_token_counter.py`

```python
class LocalTokenCounter:
    """Pre-flight token estimation for local models."""
    
    def __init__(self):
        self.tokenizers = {
            "qwen3": self._load_qwen_tokenizer(),
            "nemotron": self._load_nemotron_tokenizer(),
            "fallback": tiktoken.get_encoding("cl100k_base")
        }
    
    def estimate(self, text: str, model_family: str) -> int:
        tokenizer = self.tokenizers.get(model_family, self.tokenizers["fallback"])
        return len(tokenizer.encode(text))
    
    def estimate_system_prompt(self, agent_name: str) -> int:
        # Sum: AGENTS.md + agent file + skills + MCP schemas (if applicable)
        # Return per-tier breakdown
```

**Integration**: Call before `omega talk` / `summon` to warn if context exceeds model limit.

---

### 2.4 Session Summary Compression (High)

**Source**: Researcher — hierarchical summarization; Zylos assembly engine pattern  

**Component**: `src/omega/oracle/session_summarizer.py`

```python
class SessionSummarizer:
    """Hierarchical session summarization for compaction survival."""
    
    async def summarize(self, session_id: str, level: int = 1) -> Summary:
        # Level 1: Per-turn summaries (tool calls → outcomes)
        # Level 2: Per-task summaries (objective → result → decisions)
        # Level 3: Session summary (goals → outcomes → open items)
        
    async def compress_for_compaction(self, session_id: str, target_tokens: int) -> str:
        # Progressive compression: Level 3 → Level 2 → Level 1 → raw
        # Preserve: decisions, active files, pending proposals, entity context
```

---

## Phase 3: Upstream Features (1-2 Months, Requires OpenCode PRs)

### 3.1 Prompt Caching Topology Optimization (Critical)

**Source**: Researcher — Zylos Research: stable-first ordering = 60-90% savings  
**Source**: Researcher — OpenCode's `applyCaching()` caches 1st 2 system + last 2 user messages  

**Current Assembly Order (Cache-Unfriendly)**:
```
[providerPrompt, envBlock, instructions, agentPrompt, userOverride]
```

**Optimized Order (Cache-Friendly)**:
```typescript
// In packages/opencode/src/session/llm.ts
system = [
  { text: providerPrompt, cache_control: { type: "ephemeral" } },      // Breakpoint 1
  { text: toolSchemas, cache_control: { type: "ephemeral" } },         // Breakpoint 2
  { text: condensedMandates, cache_control: { type: "ephemeral" } },   // Breakpoint 3
  { text: envBlock },                                                   // Dynamic
  { text: instructions },                                               // Dynamic
  { text: agentPrompt },                                                // Dynamic
  { text: userOverride }                                                // Dynamic
]
```

**Expected Savings**: 60-80% per-call input cost reduction for long-running agents (Zylos Research)

**PR Scope**: Modify `llm.ts` assembly order + add `cache_control` to stable blocks

---

### 3.2 Lazy MCP Tool Loading (High)

**Source**: Ma'at — GitHub #35376 open; 10.8K tokens/request for 86 tools  
**Source**: Researcher — Anthropic's "Code Mode" / Bifrost achieves 92-98% reduction  

**Proposal**: Add `lazy_load: true` to MCP tool registration

```typescript
// In packages/opencode/src/mcp/mcp.ts
interface MCPToolConfig {
  name: string;
  description: string;
  lazy_load?: boolean;      // New: defer schema until tool invoked
  category?: string;        // For tool profiles (dev/deploy/debug)
}

// In prompt.ts:resolveTools()
async resolveTools(agent: Agent, task?: Task): Promise<Tool[]> {
  const allTools = await this.registry.getAll();
  if (task) {
    // Filter by task-relevant tools (semantic matching or category)
    return this.filterToolsForTask(allTools, task);
  }
  return agent.permissions.filterTools(allTools);
}
```

**Expected Savings**: 90%+ reduction in MCP schema tokens for typical tasks (only 5-10 tools needed)

---

### 3.3 Dynamic Tool Registration / Tool Profiles (Medium)

**Source**: Ma'at — consider tool profiles (dev/deploy/debug) if opencode adds support  

**Proposal**: Tool profiles in opencode.json

```json
{
  "toolProfiles": {
    "dev": ["oracle_talk", "oracle_summon", "hivemind_*", "local_queue_*"],
    "deploy": ["github_*", "spawn_local_worker", "delegate_task"],
    "debug": ["search_*", "headroom_retrieve", "oracle_assess_intent"],
    "research": ["sovereign_search", "search_extract", "oracle_discover_entity"]
  },
  "agent": {
    "researcher": { "toolProfile": "research" },
    "maat": { "toolProfile": "dev" },
    "kali": { "toolProfile": "deploy" }
  }
}
```

---

### 3.4 Local Model Caching Strategy (Investigation)

**Source**: Researcher — llama.cpp prefix caching vs Anthropic explicit breakpoints  
**Divergence**: Different architectures, same goal  

**Investigation Needed**:
- llama.cpp `enable_prefix_caching=True` (vLLM-style) — does it work with GGUF?
- How to integrate with OpenCode's `applyCaching()` for local backends?
- Cache key strategy for local models (session-based vs content-based)

---

## Dependencies Graph

```
Phase 1 (Config)
├── AGENTS.md ──┐
├── opencode.json ──┼──→ Phase 2 (Tooling)
├── Compaction plugin ──┤
├── Skills opt-in ──────┘
└── Model routing ────────→ Independent

Phase 2 (Tooling)
├── Hydration engine ◄──── Requires: Checkpoint format (Phase 1)
├── Token budget ────────── Requires: Tier budgets (Phase 1)
├── Summary compression ─── Requires: Summarizer model (local)
├── Local token counter ─── Requires: tiktoken integration
└── OTel export ────────── Requires: OTel collector + Prometheus

Phase 3 (Upstream)
├── Prompt caching topology ◄ Requires: OpenCode PR review/merge
├── Lazy MCP loading ───────── Requires: OpenCode PR review/merge
├── Tool profiles ──────────── Requires: OpenCode PR review/merge
└── Local model caching ────── Requires: llama.cpp investigation
```

---

## Validation Checkpoints

| Checkpoint | Criteria | Go/No-Go |
|------------|----------|----------|
| **Phase 1 Complete** | Global system prompt <60K tokens; all agents functional; compaction plugin loads | Token count + agent smoke tests |
| **Phase 2 Complete** | Hydration <2s; token budget enforced; 95% compaction recovery; OTel dashboards live | Integration test suite |
| **Phase 3 Complete** | Cache hit rate >60%; lazy MCP working; tool profiles functional; local caching verified | Production canary (10% traffic) |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_phase23_roadmap ⬡ 2026-08-20*