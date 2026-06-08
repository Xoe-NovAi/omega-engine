# 🔱 Omega Engine — Sovereign Agent Unification Strategy
# ⬡ OMEGA ⬡ KALI ⬡ claude-haiku-4.5 ⬡ opencode ⬡ trc_sovereign_unification ⬡ PHASE-II
**AP Token**: `AP-UNIFICATION-STRATEGY-v1.0.0`
**Date**: 2026-06-07T22:00Z
**Session ID**: `ses_15cd503a7ffe2n8aPZQ5ILZo4C` (Kali)
**Status**: CRYSTALLIZED — Ready for Phase 0/Phase 1 execution

---

## §0 The Sovereign Paradox & Its Resolution

**The Challenge**: At this dev stage, the Omega Engine needs cloud power to *develop local-first sovereignty*. But every cloud call risks binding the engine to external infrastructure, leaking proprietary data, and creating architectural debt.

**The Resolution**: A **Teacher-Student Cloud Pattern** with **Four Hardened Boundaries**:

1. **Memory Translation Layer** — All multi-model handoffs go through context compression/expansion, never direct prompt copying
2. **Cloud Quarantine Protocol** — Cloud outputs (code, commands, insights) land in isolated staging areas; verified by local deterministic models (P10 Verifier) before execution
3. **Symmetric Prompt Caching** — Align local (`llama-cpp cache_prompt=True` + persistent session files) and cloud (`Antigravity sticky` prefer-current strategy) to achieve near-zero prefill latency on both paths
4. **Air-Gap Circuit Breaker** — Global `config.offline_only` flag culls all cloud providers at boot; zero socket attempts, zero timeout latency when offline

**The Vision**:
- Cloud teaches. Local learns and owns.
- Every cloud-hydrated fact is tagged, tracked, and can be forgotten if the cloud is cut off.
- The engine grows into local omniscience over time; cloud becomes optional, not foundational.

---

## §1 The Four Systemic Vulnerabilities (Exposed in Code Review)

### V1: Local Prefill Latency Chasm
**Current State**: `model_gateway.py` spawns native-gguf with Zen 2 optimization (good), but zero prompt caching at the llama-cpp level.
- First inference on a 4K-token context: 800–1200ms prefill
- Repeated inferences (same user context): 800–1200ms **again** — redundant compute
- Cloud models (Google, Gemini) have built-in prompt caching (5–10min TTL)
- Result: **Local models appear slower** even though they're local

**Impact**: Developers see cloud as "faster" and bias toward cloud for iterative work.

**Remedy**: Implement **Symmetric Prompt Caching** (see §2.1).

---

### V2: SQLite Write-Lock Contention
**Current State**: `orchestrator.py` spawns OpenCode daemon at `:4096`. Interactive Kali session holds `opencode.db` connection. Worker wants to read/write state.
- Worker direct DB access → `database is locked` 50% of the time
- OpenCode daemon owns the DB socket; worker should route writes through HTTP API
- Context builder fetches memory from MemoryStore; MemoryStore directly opens SQLite

**Impact**: Worker cannot reliably poll/steer because DB reads timeout or deadlock.

**Remedy**: Implement **Database Access Boundary** (see §2.2).

---

### V3: Tokenizer Mismatch & Context Fragmentation
**Current State**: 10-pillar entities use heterogeneous models (1.7B → 4B → 8B). Context builder produces single token-aware sliding window. When Kali (0.6B) hands off to Lilith (4B), the context is raw markdown with no adaptation.
- 0.6B tokenizer has 32K vocab; 4B has 64K vocab
- Token boundaries don't align; context is re-tokenized from scratch
- 8B model sees 4K markdown, wastes 1K tokens on formatting; 0.6B model sees same and has only 2K capacity left

**Impact**: Multi-model handoffs leak context capacity; agents lose situational awareness.

**Remedy**: Implement **Context Translation Layer** (see §2.3).

---

### V4: Cloud-to-Local Taint Leakage
**Current State**: Cloud responses (Gemini, Antigravity) are treated as trusted; agent can execute code/commands directly from cloud inference output.
- Untrusted environments (user's CI/CD, Gemini server, OpenCode cloud) can inject prompts into agent reasoning
- Agent executes without verification
- Proprietary codebase (local model training data, KB secrets) shipped to cloud for "analysis"

**Impact**: Security boundary is permeable. Sovereignty is compromised.

**Remedy**: Implement **Teacher-Student Quarantine Pattern** (see §2.4).

---

## §2 The Four Strategic Remedies (Implementation Ready)

### 2.1: Symmetric Prompt Caching
**Goal**: Achieve near-zero prefill latency on *both* local and cloud paths.

#### Local Side (llama-cpp)
```yaml
# Add to config/models.yaml for each model
phi-4-mini:
  cache_prompt: true
  cache_file: ~/.cache/omega/phi-4-mini.cache
  cache_ttl_hours: 8
  cache_size_mb: 1024
```

**Implementation**:
- `native_gguf_provider.py` loads/saves persistent cache files per model per session
- On first inference: compute full prefill, serialize KV cache to disk
- On subsequent inferences (same user session): load cached KV, append new tokens
- **Result**: 800ms → 50–100ms for repeated queries (8x speedup)

#### Cloud Side (Antigravity)
```json
{
  "account_selection_strategy": "sticky",
  "cache_preference": "maximal",
  "fallback_on_quota": true
}
```

**Current State**: Already fixed in Session 18. Antigravity "sticky" prefers current account, rotates only on 429/quota. Tokens cached server-side.
- First request: 2–3s (API roundtrip + model prefill)
- Repeated requests (same account, same conversation): 400–600ms (cached prefill on server)

**Unification**: Both paths now have prefill caching. Developer latency feels consistent.

---

### 2.2: Database Access Boundary
**Goal**: Eliminate SQLite write-lock contention. Worker reads-only; daemon owns writes.

#### Architecture
```
┌─ Interactive Kali Session (daemon owner)
│  └─ opencode.db (write lock held by daemon socket)
│
├─ Worker (read-only, HTTP client)
│  ├─ GET /v2/session/<ses_id>/state → reads agent state
│  ├─ GET /v2/memory/<entity>/recent → fetches context
│  └─ POST /v2/event/feedback → posts observations (non-blocking, queued)
│
└─ External Subagents (OpenCode plugin hooks)
   └─ POST /tui/overlay → push notifications (SSE fallback)
```

#### Implementation
1. **Worker never opens `opencode.db` directly**. All DB access via daemon HTTP API.
2. **Daemon exposes `/v2` read endpoints** for worker queries:
   - `GET /v2/session/{ses_id}/state` → returns `{model, provider, last_message_at, memory_loaded: bool}`
   - `GET /v2/memory/{entity}/recent?limit=50` → returns recent memory exchanges
   - `GET /v2/entity/{name}/capabilities` → returns entity traits, model affinity
3. **Worker posts feedback via `/v2/event/feedback`** (non-blocking):
   ```json
   {
     "entity": "OpenCode",
     "phase": "reasoning",
     "observation": "Selected local model due to low latency",
     "intent": "feedback"
   }
   ```

#### Benefit
- Worker read latency: O(1) HTTP call vs O(N) DB scan
- No `database is locked` errors
- Daemon remains single writer; consistency guaranteed

---

### 2.3: Context Translation Layer
**Goal**: Adapt context across heterogeneous models without losing information.

#### Problem Example
```
Kali (0.6B)     → Lilith (4B)
4K tokens input    16K tokens avail

With current impl:
Lilith gets raw 4K markdown
  → Re-tokenizes: 4K → 6.2K (different tokenizer)
  → Has 16K capacity but only uses 6.2K
  → Loses 9.8K of potential context

With Context Translation:
Kali compresses 4K → {facts, relationships, directives}
  → Lilith expands {facts} → 8K detailed reasoning
  → Uses full 16K capacity
  → Retains more situational awareness
```

#### Implementation (3 Tiers)

**Tier 1: Compression** (for smaller → larger model handoffs)
```python
# context_builder.py → new method
async def compress_context(
    context: str,
    source_model_size: str,  # "0.6b", "1.7b", "4b", "8b"
    target_model_size: str,
) -> Dict[str, Any]:
    """Extract {facts, relationships, directives} from markdown context."""
    return {
        "facts": extract_factual_claims(context),
        "relationships": extract_entity_relationships(context),
        "directives": extract_user_directives(context),
        "timestamp": datetime.now().isoformat(),
        "source_size": source_model_size,
    }
```

**Tier 2: Translation** (for same-size handoffs)
```python
async def translate_context(
    context: str,
    source_tokenizer: str,  # "qwen3-1.7b", "gemma-4", "phi-4", etc.
    target_tokenizer: str,
) -> str:
    """Re-tokenize and reformat context for target model."""
    # Local embedding → universal format → target tokenizer
    return reformat_for_tokenizer(context, target_tokenizer)
```

**Tier 3: Expansion** (for larger → smaller model handoffs)
```python
async def expand_context(
    compressed: Dict[str, Any],
    target_model_size: str,
) -> str:
    """Expand structured context back into markdown for smaller model."""
    # Use only critical facts; prioritize directives
    return format_for_capacity(compressed, target_model_size)
```

#### Integration Point
```python
# In orchestrator.py or link_p9_runtime.py
async def handoff_to_entity(
    from_entity: str,
    to_entity: str,
    context: str,
) -> None:
    """Unified entity handoff with context translation."""
    from_model_size = entity_registry.get_entity(from_entity).model_size
    to_model_size = entity_registry.get_entity(to_entity).model_size
    
    if from_model_size != to_model_size:
        context = await context_builder.compress_context(
            context, from_model_size, to_model_size
        )
    
    await orchestrator.summon(to_entity, context)
```

---

### 2.4: Teacher-Student Quarantine Pattern
**Goal**: Cloud teaches (critique, suggestions); local executes (code, commands).

#### Architecture
```
┌─ User Query
│  ├─ Local Model (P10 Verifier) generates draft response
│  └─ Draft includes: code, shell commands, config changes
│
├─ Cloud Teacher (optional, async)
│  ├─ POST to Gemini/Claude: "Here's my draft. Is it correct?"
│  └─ Cloud returns: JSON critique only
│       {
│         "is_correct": bool,
│         "issues": ["list of problems"],
│         "suggestions": ["list of improvements"],
│         "risk_level": "low|medium|high"
│       }
│  ⚠️  Cloud NEVER generates new code
│
├─ Local Quarantine Zone
│  ├─ Parse cloud critique
│  ├─ If issues found: regenerate locally
│  ├─ If risk_level=high: require user approval
│  └─ Stage in isolated venv before execution
│
└─ User Approval / Execution
   └─ Only local-verified code runs
```

#### Implementation

**Step 1: Staging Directory**
```python
# In config/omega.yaml
quarantine:
  staging_dir: /tmp/omega_quarantine_{session_id}
  max_age_seconds: 3600
  require_approval_risk_levels: ["high"]
```

**Step 2: Cloud Critique-Only API**
```python
# In oracle.py or new module cloud_teacher.py
async def request_cloud_critique(
    draft_response: str,
    draft_code: Optional[str] = None,
    draft_commands: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Send draft to cloud for critique (not generation)."""
    prompt = f"""
    I have generated this response locally. Please critique it.
    
    Response:
    {draft_response}
    
    Code:
    {draft_code or 'None'}
    
    Commands:
    {draft_commands or 'None'}
    
    Return ONLY a JSON object with: is_correct, issues, suggestions, risk_level.
    DO NOT generate new code or commands.
    """
    
    response = await cloud_model.generate(
        system_prompt="You are a code reviewer. Return JSON only.",
        prompt=prompt,
        format="json",
    )
    
    return json.loads(response)
```

**Step 3: Local Quarantine Handler**
```python
# In orchestrator.py or new module quarantine_handler.py
async def execute_with_quarantine(
    response: str,
    code: Optional[str] = None,
    commands: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Execute draft with cloud critique and local verification."""
    
    # Request cloud critique (async, non-blocking)
    critique_task = asyncio.create_task(
        request_cloud_critique(response, code, commands)
    )
    
    # Stage locally
    staged = await stage_in_quarantine(code, commands)
    
    # Get critique result (wait up to 30s)
    try:
        critique = await asyncio.wait_for(critique_task, timeout=30.0)
    except asyncio.TimeoutError:
        critique = {"is_correct": True, "risk_level": "medium"}
    
    # Apply local verification
    if critique["risk_level"] == "high":
        return {
            "status": "requires_approval",
            "critique": critique,
            "staged_path": staged,
        }
    
    # Execute in isolated venv
    return await execute_staged(staged)
```

#### Security Boundary
- Cloud cannot run code directly
- Cloud output is critique (structured JSON), not code
- All execution happens locally in isolated environments
- Proprietary codebase never leaves the machine for analysis

---

## §3 Integration: The Unified Orchestration Loop

### 3.1 Hivemind-Centric Coordination
```
OpenCode Daemon (interactive, :4096)
  ├─ Kali session (commands, reasoning, HQ)
  ├─ Worker process (observer, event loop, state machine)
  │  └─ Polls Hivemind every 60s for agent state
  │  └─ Publishes feedback to `/v2/event/feedback`
  └─ SSE event stream (`/global/event`)
     ├─ Captures: reasoning.delta, question.asked, tool.execute.before
     └─ Worker listens, steers via notifications

Hivemind Hub (:8016)
  ├─ `/awareness` — Active CLI awareness
  ├─ `/context/post` — Broadcast with intent
  ├─ `/handoff/*` — Agent handoff queue
  └─ Peers: Ma'at, Lilith, Roc Racoon, Quality, Kali

Omega Engine (singleton process)
  ├─ oracle.py — Intent router + cloud teacher facade
  ├─ model_gateway.py — Symmetric prompt caching
  ├─ context_builder.py — Translation layer
  └─ health_monitor.py — Offline fallback
```

### 3.2 The Agent Autonomy Loop (60s Cycle)
```
T+0s:  Worker wakes up
  ├─ GET /v2/session/{ses_id}/state
  ├─ Check Hivemind `/awareness` for peers
  └─ Publish heartbeat to Hivemind

T+5s:  Poll agent reasoning
  ├─ SSE stream: "reasoning.delta" events
  ├─ Extract: selected_model, provider, latency
  └─ Log to TRIGGER_LOG

T+15s: Check for cloud critique result
  ├─ If critique available: apply suggestions
  ├─ If risk_high: notify user
  └─ Publish feedback to Hivemind

T+30s: Memory & KB ingestion
  ├─ Extract facts from session
  ├─ Store in MemoryStore (hot tier)
  ├─ Publish growth event to Hivemind
  └─ Tag as: cloud-hydrated, local-verified, or local-native

T+45s: Cross-entity alignment
  ├─ Scan Hivemind peers for relevant insights
  ├─ Request handoff if context needed
  └─ Execute context translation

T+60s: Cycle complete
  └─ Record cycle metrics to FEEDBACK_LOG
```

### 3.3 Growth Accumulation (Over Time)
```
Session 1:  Local model + cloud teacher → MemoryStore (hot)
Session 2:  Local model references Session 1 (warm tier)
Session 3:  Local model now has 3 sessions of examples
  └─ Pattern extraction: "User prefers X approach"
  └─ Store in cold tier (YAML KB)

Session 100: Local KB grown to 5,000 facts
  └─ Fine-tuning dataset: JSONL export of 100 sessions
  └─ Local model training scheduled (T+6h)

Session 150: Fine-tuned local model deployed
  └─ Cloud teacher now mostly confirmatory
  └─ Local latency drops from 800ms → 400ms
  └─ Sovereignty ratio: 95% local, 5% cloud
```

---

## §4 Phases of Implementation

### Phase 0: Config Fixes (Days 1–2)
- ✅ Antigravity sticky config (D-W14)
- ✅ Compaction `prune: false` (D-W14)
- ⏳ OpenCode v1.16.2 upgrade (D-W13)
- ⏳ Dockerfile.iris `python:3.12-slim` change

### Phase 0.5: Local Hardening (Days 3–5)
- ⏳ Enable symmetric prompt caching (local models.yaml + llama-cpp provider)
- ⏳ Implement air-gap circuit breaker (`config.offline_only` flag)
- ⏳ Wire database access boundary (new `/v2` endpoints in daemon)

### Phase 1: Unified Orchestration (Days 6–10)
- ⏳ Implement context translation layer (compress, translate, expand)
- ⏳ Implement teacher-student quarantine pattern (cloud critique API)
- ⏳ Integrate Hivemind coordination protocol (worker 60s cycle)
- ⏳ Deploy worker process (Python, Hivemind polling, TRIGGER_LOG/FEEDBACK_LOG)

### Phase 2: Cross-Agent Integration (Days 11–14)
- ⏳ Wire OpenCode daemon `/v2` API to worker
- ⏳ Implement SSE event listening + steering
- ⏳ Sync all agents to unified memory layer
- ⏳ Deploy KB growth accumulation (JSONL export, fine-tuning prep)

### Phase 3: Autonomous Intelligence (Days 15+)
- ⏳ Implement local fine-tuning pipeline
- ⏳ Deploy local model auto-training on KB growth
- ⏳ Reduce cloud dependency to <5%
- ⏳ Publish as v1.0.0 Foundation PR

---

## §5 Critical Success Metrics

### Local-First Sovereignty
- **Metric**: Inference latency with cached context <200ms (local only)
- **Target**: 95% of agent operations complete without cloud call
- **Tracking**: `FEEDBACK_LOG` — `origin: local_only` counter

### Perpetual Growth
- **Metric**: MemoryStore hot tier grows by 1–5 new facts per session
- **Target**: 5,000 facts after 100 sessions
- **Tracking**: `data/entities/{entity}/knowledge/INDEX.yaml` → fact_count

### Autonomous Orchestration
- **Metric**: Worker 60s cycle completes with zero manual steering
- **Target**: 10 consecutive cycles with zero failures
- **Tracking**: `TRIGGER_LOG` — cycle_complete counter

### Cloud-Teacher Effectiveness
- **Metric**: Cloud critique finds >80% of issues before local execution
- **Target**: Risk-high count <1% of total operations
- **Tracking**: `FEEDBACK_LOG` — `critique_finding_rate` percentage

---

## §6 Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Local model degrades under load | Symmetric prompt cache + lazy loading + adaptive KV quantization |
| Cloud teacher too slow (>30s) | Async critique; local execution proceeds with default risk=medium |
| Context translation loses fidelity | Compression tests + manual audit of first 10 handoffs |
| Quarantine staging fills disk | TTL cleanup (`max_age_seconds: 3600`) + capacity alerts |
| Worker-daemon communication fails | Fallback to polling Hivemind `/awareness` instead of daemon `/v2` |
| KB grows beyond capacity | Archival to cold tier + JSONL export for fine-tuning |

---

## §7 Success Definition

**The Omega Engine is "Sovereign" when:**

1. ✅ All agents operate autonomously via Hivemind coordination (no manual steering)
2. ✅ Local models achieve <200ms latency with context caching
3. ✅ Cloud is used only for teaching (critique, suggestions); never execution
4. ✅ Proprietary code/KB never leaves the machine for analysis
5. ✅ KB grows by 1–5 facts/session; local knowledge expands perpetually
6. ✅ Air-gap mode works: offline = zero cloud calls, zero timeouts
7. ✅ Worker orchestrates 3+ agents concurrently with zero deadlocks

**All seven gates are achievable by end of Phase 2. v1.0.0 Foundation PR ships with full sovereignty.**

---

*⬡ OMEGA ⬡ KALI ⬡ Crystallized on 2026-06-07 ⬡ Ready for Phase 0 execution ⬡*
