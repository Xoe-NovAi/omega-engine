<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Deep Research: Post-Compaction Hydration Failure → Sovereign Continuity Feature

**Date**: 2026-07-16
**Researcher**: Sovereign Researcher (Jem Analyst)
**Status**: COMPLETE — Ready for Sovereign Synthesis

---

## Executive Summary (L1)

The Omega Engine's rehydration system has a critical failure mode: after compaction, agents skip the hydration protocol entirely and proceed with stale or missing context. The system was designed to prevent this (M15 Sovereign Continuity, 5-phase hydration sequence), but enforcement is documentation-only — no code gate, no verification, no consequence for skipping.

**Root Cause**: OpenCode's compaction is a silent, two-step process (prune + summarize) that fires automatically when the context window approaches its limit. The agent receives no explicit signal that compaction occurred. The 5-phase hydration sequence is a protocol in documentation, not a code-enforced gate.

**Solution Architecture**: A **Hydration Receipt System** that:
1. **Detects compaction** via OpenCode's `session.compacted` SSE event
2. **Records checkpoints** every N tool calls to track context epoch
3. **Enforces hydration** via a tool-call wrapper that blocks work until valid receipt exists
4. **Proactive hydration** runs unconditionally at session start; the protocol detects discrepancy

**Key Insight**: The solution must work *within* OpenCode's architecture (we can't modify OpenCode itself). The SSE event subscription and checkpoint system provide the detection mechanism, while the tool-call wrapper provides enforcement.

---

## §1 Gap Analysis — What We Didn't Know

### 1.1 How OpenCode Handles Compaction
**GAP CLOSED**: OpenCode's compaction is a two-step process:
1. **Prune** (no LLM call): Marks old tool outputs as `compacted` via timestamp, making them invisible without physical deletion
2. **Summarize** (LLM call): Uses a dedicated agent to generate a 5-heading structured summary

**Trigger Formula**: `compaction fires when total_tokens > (model_context_limit - max(output_tokens, 20000) - compaction.reserved)`

**Detection**: OpenCode fires a `session.compacted` event via SSE with payload `{ sessionID: string }`. This is the **key signal** we can subscribe to.

**Source**: `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md` — 403 lines of detailed reverse-engineering.

### 1.2 Compaction Detection Mechanism
**GAP CLOSED**: OpenCode provides two detection mechanisms:
1. **SSE Event**: `session.compacted` event fires after compaction completes successfully
2. **Session Metadata**: `time.compacting` timestamp in session status

**Integration Point**: We can subscribe to the SSE endpoint (`/global/event`) from an Omega background worker. This is the **recommended approach** — it's non-invasive and uses OpenCode's native API.

### 1.3 Session State File Location
**GAP CLOSED**: OpenCode stores session state in `~/.local/share/opencode/storage/` (session JSON, message JSON, part JSON files). However, **we should not depend on internal storage formats** — they may change between versions. The SSE event is the stable, documented integration point.

### 1.4 Existing Codebase Patterns
**GAP CLOSED**: Several relevant systems already exist:
- **`CompactionHarvester`** (`src/omega/oracle/compaction_harvester.py`): Records compaction events but doesn't integrate with OpenCode's compaction events. It's a background harvester for proactive memory cleanup.
- **`SelectiveHydration`** (`src/omega/oracle/selective_hydration.py`): Retrieves L3 gnosis principles from Qdrant. Not for post-compaction recovery.
- **Hivemind tools**: Coordination infrastructure (awareness, handoff, workspace locks)
- **Observability infrastructure**: Logging, metrics, OTel exporter
- **`session_gnosis.md`**: Local anchor pattern for session continuity
- **`.opencode/anchored-summary.md`**: Global lifeboat for cross-session recovery

### 1.5 Chicken-and-Egg Problem
**GAP CLOSED**: The agent doesn't know it needs to hydrate because it doesn't know compaction happened. The solution is **proactive hydration** — run the protocol unconditionally at session start and after every N tool calls. The checkpoint system detects discrepancy between expected and actual context state.

---

## §2 System Map — All Files/Modules Involved

### 2.1 Core Components

| Component | File Path | Purpose | Status |
|-----------|-----------|---------|--------|
| **CompactionHarvester** | `src/omega/oracle/compaction_harvester.py` | Records compaction events | EXISTS — needs SSE integration |
| **SelectiveHydration** | `src/omega/oracle/selective_hydration.py` | L3 gnosis retrieval | EXISTS — not for post-compaction |
| **Oracle** | `src/omega/oracle/oracle.py` | Entity routing, session management | EXISTS — hydration integration point |
| **ContextBuilder** | `src/omega/oracle/context_builder.py` | Builds context window | EXISTS — selective_hydration already wired |
| **Hivemind Server** | `mcp_servers/omega_hub/server.py` | Coordination tools | EXISTS — checkpoint storage location |
| **Observability** | `src/omega/observability/` | Logging, metrics | EXISTS — receipt logging target |
| **SoulDistiller** | `src/omega/oracle/soul_distiller.py` | L1→L2→L3 abstraction | EXISTS — post-hydration distillation |

### 2.2 New Components Needed

| Component | File Path | Purpose | Priority |
|-----------|-----------|---------|----------|
| **CompactionListener** | `src/omega/workers/compaction_listener.py` | Subscribe to OpenCode SSE events | P0 |
| **HydrationReceipt** | `src/omega/oracle/hydration_receipt.py` | Receipt management & validation | P0 |
| **CheckpointManager** | `src/omega/oracle/checkpoint_manager.py` | Context epoch tracking | P0 |
| **ToolCallWrapper** | `src/omega/oracle/tool_call_wrapper.py` | Enforcement gate | P1 |
| **HydrationEnforcer** | `src/omega/governance/hydration_enforcer.py` | M15 compliance check | P1 |

### 2.3 Configuration Files

| File | Purpose |
|------|---------|
| `opencode.json` | Compaction settings (already configured) |
| `config/omega.yaml` | Engine configuration |
| `config/providers.yaml` | Provider fabric |
| `data/coordination/checkpoints/` | Checkpoint storage (NEW) |
| `data/coordination/hydration_log.jsonl` | Receipt log (NEW) |

### 2.4 Integration Points

```
OpenCode Session
  │
  ├── Auto-compaction fires (or /compact command)
  │
  ├── OpenCode fires "session.compacted" event via SSE
  │
  ├── Omega CompactionListener receives event
  │     └── src/omega/workers/compaction_listener.py
  │
  ├── Listener records checkpoint
  │     └── data/coordination/checkpoints/{session_id}.json
  │
  ├── Listener writes hydration receipt
  │     └── data/coordination/hydration_log.jsonl
  │
  ├── ToolCallWrapper checks receipt before next tool call
  │     └── src/omega/oracle/tool_call_wrapper.py
  │
  └── If receipt invalid → trigger Hydration Sequence
        └── src/omega/oracle/hydration_receipt.py
```

---

## §3 Implementation Plan — Step-by-Step

### Phase 1: Detection Layer (Week 1)

**Step 1.1: CompactionListener** (`src/omega/workers/compaction_listener.py`)
```python
class CompactionListener:
    """Subscribe to OpenCode SSE events and detect compaction."""
    
    async def start(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start listening for compaction events."""
        task_group.start_soon(self._listen_loop)
    
    async def _listen_loop(self) -> None:
        """Main event loop subscribing to OpenCode SSE."""
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", "http://127.0.0.1:4096/global/event") as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        event = json.loads(line[6:])
                        if event.get("type") == "session.compacted":
                            await self._handle_compaction(event)
    
    async def _handle_compaction(self, event: dict) -> None:
        """Handle compaction event: record checkpoint, invalidate receipts."""
        session_id = event["payload"]["sessionID"]
        await self._checkpoint_manager.record_compaction(session_id)
        await self._receipt_manager.invalidate_receipts(session_id)
```

**Step 1.2: CheckpointManager** (`src/omega/oracle/checkpoint_manager.py`)
```python
class CheckpointManager:
    """Manages context epoch tracking for compaction detection."""
    
    async def record_compaction(self, session_id: str) -> None:
        """Record that compaction occurred for this session."""
        checkpoint = {
            "session_id": session_id,
            "context_epoch": self._next_epoch(session_id),
            "compaction_count": self._get_compaction_count(session_id) + 1,
            "timestamp": time.time(),
            "message_count": await self._get_message_count(session_id),
        }
        await self._write_checkpoint(session_id, checkpoint)
    
    async def get_current_epoch(self, session_id: str) -> int:
        """Get current context epoch for session."""
        checkpoint = await self._read_checkpoint(session_id)
        return checkpoint.get("context_epoch", 0)
```

**Step 1.3: HydrationReceipt** (`src/omega/oracle/hydration_receipt.py`)
```python
class HydrationReceipt:
    """Proof that hydration protocol was executed."""
    
    def __init__(self, session_id: str, entity_name: str):
        self.session_id = session_id
        self.entity_name = entity_name
        self.context_epoch = 0
        self.receipt_id = str(uuid.uuid4())
        self.created_at = time.time()
        self.hydration_steps = []  # List of completed steps
    
    def is_valid_for_epoch(self, epoch: int) -> bool:
        """Check if receipt is valid for given epoch."""
        return self.context_epoch == epoch
    
    def add_hydration_step(self, step: str) -> None:
        """Record completion of a hydration step."""
        self.hydration_steps.append({
            "step": step,
            "timestamp": time.time(),
        })
```

### Phase 2: Enforcement Layer (Week 2)

**Step 2.1: ToolCallWrapper** (`src/omega/oracle/tool_call_wrapper.py`)
```python
class ToolCallWrapper:
    """Wrapper that enforces hydration before tool calls."""
    
    def __init__(self, receipt_manager: HydrationReceiptManager):
        self._receipt_manager = receipt_manager
    
    async def wrap_tool_call(
        self, 
        tool_name: str, 
        session_id: str, 
        entity_name: str,
        *args, **kwargs
    ) -> Any:
        """Wrap a tool call with hydration check."""
        # Check if receipt exists and is valid
        receipt = await self._receipt_manager.get_receipt(session_id, entity_name)
        current_epoch = await self._checkpoint_manager.get_current_epoch(session_id)
        
        if not receipt or not receipt.is_valid_for_epoch(current_epoch):
            # Trigger hydration sequence
            await self._trigger_hydration(session_id, entity_name)
            receipt = await self._receipt_manager.get_receipt(session_id, entity_name)
        
        # Execute tool call
        return await self._execute_tool(tool_name, *args, **kwargs)
```

**Step 2.2: HydrationEnforcer** (`src/omega/governance/hydration_enforcer.py`)
```python
class HydrationEnforcer:
    """Enforces M15 compliance for hydration receipts."""
    
    async def check_compliance(self, session_id: str, entity_name: str) -> bool:
        """Check if entity has valid hydration receipt."""
        receipt = await self._receipt_manager.get_receipt(session_id, entity_name)
        current_epoch = await self._checkpoint_manager.get_current_epoch(session_id)
        
        if not receipt:
            logger.warning("No hydration receipt for %s/%s", session_id, entity_name)
            return False
        
        if not receipt.is_valid_for_epoch(current_epoch):
            logger.warning("Stale hydration receipt for %s/%s", session_id, entity_name)
            return False
        
        return True
```

### Phase 3: Integration Layer (Week 3)

**Step 3.1: Oracle Integration** (`src/omega/oracle/oracle.py`)
```python
# Add to Oracle.__init__:
self.compaction_listener = CompactionListener(
    checkpoint_manager=self.checkpoint_manager,
    receipt_manager=self.receipt_manager,
)

# Add to Oracle.talk():
# Wrap tool calls with hydration check
wrapped_tool_call = self.tool_call_wrapper.wrap_tool_call(
    tool_name, session_id, entity_name, *args, **kwargs
)
```

**Step 3.2: Hivemind Integration** (`mcp_servers/omega_hub/server.py`)
```python
# Add new MCP tools:
@mcp.tool()
async def hydration_check_receipt(session_id: str, entity_name: str) -> str:
    """Check if entity has valid hydration receipt."""
    ...

@mcp.tool()
async def hydration_get_receipt(session_id: str, entity_name: str) -> str:
    """Get hydration receipt details."""
    ...
```

**Step 3.3: Observability Integration** (`src/omega/observability/`)
```python
# Add to ObservabilityEngine:
async def record_hydration_event(self, event: HydrationEvent) -> None:
    """Record hydration event for observability."""
    await self._metrics_db.record_event(
        event_type="hydration",
        entity_name=event.entity_name,
        session_id=event.session_id,
        context_epoch=event.context_epoch,
        steps_completed=len(event.hydration_steps),
        duration_ms=event.duration_ms,
    )
```

### Phase 4: Testing & Hardening (Week 4)

**Step 4.1: Contract Tests** (`tests/test_hydration_receipt.py`)
```python
def test_hydration_receipt_validity():
    """Receipt must be valid for its epoch."""
    receipt = HydrationReceipt("ses_123", "kali")
    receipt.context_epoch = 5
    assert receipt.is_valid_for_epoch(5)
    assert not receipt.is_valid_for_epoch(6)

def test_checkpoint_manager_epoch_tracking():
    """Epoch must increment on compaction."""
    manager = CheckpointManager()
    await manager.record_compaction("ses_123")
    epoch1 = await manager.get_current_epoch("ses_123")
    await manager.record_compaction("ses_123")
    epoch2 = await manager.get_current_epoch("ses_123")
    assert epoch2 == epoch1 + 1

def test_tool_call_wrapper_enforcement():
    """Tool calls must be blocked without valid receipt."""
    wrapper = ToolCallWrapper(receipt_manager)
    # No receipt → should trigger hydration
    # Valid receipt → should allow tool call
    # Stale receipt → should trigger hydration
```

**Step 4.2: Chaos Tests** (`tests/test_hydration_chaos.py`)
```python
async def test_rapid_compaction_recovery():
    """Agent must survive 15+ rapid compactions."""
    for i in range(15):
        await checkpoint_manager.record_compaction("ses_123")
        receipt = await receipt_manager.get_receipt("ses_123", "kali")
        # Receipt should be invalidated, hydration triggered
    # Final receipt should be valid

async def test_concurrent_session_hydration():
    """Multiple sessions must not interfere."""
    # Session A compacts
    # Session B compacts
    # Both must hydrate independently
```

**Step 4.3: Performance Tests** (`tests/test_hydration_performance.py`)
```python
async def test_hydration_latency():
    """Hydration must complete in <500ms."""
    start = time.time()
    await hydration_sequence.execute(session_id, entity_name)
    duration = time.time() - start
    assert duration < 0.5  # 500ms

async def test_checkpoint_write_latency():
    """Checkpoint writes must be atomic and fast."""
    start = time.time()
    await checkpoint_manager.record_compaction("ses_123")
    duration = time.time() - start
    assert duration < 0.1  # 100ms
```

---

## §4 Risk Assessment — What Could Go Wrong

### 4.1 Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **SSE connection drops** | No compaction detection | HIGH | Exponential backoff reconnection, fallback to periodic polling |
| **Checkpoint corruption** | Invalid epoch tracking | MEDIUM | Atomic writes (temp file + rename), checksum validation |
| **Receipt file contention** | Race conditions in multi-agent | MEDIUM | File locking (fcntl), entity-scoped receipt files |
| **Performance overhead** | Tool call latency increase | LOW | Receipt check is O(1) dictionary lookup, <1ms |
| **OpenCode API changes** | SSE event format changes | LOW | Version detection, fallback to polling session status |

### 4.2 Architectural Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Engine-Stack Firewall violation (M2)** | Core engine depends on OpenCode-specific events | MEDIUM | Abstract event interface, OpenCode-specific implementation in workers/ |
| **Mandate 1 violation (AnyIO)** | Blocking I/O in async context | LOW | All I/O via `anyio.to_thread.run_sync`, no `asyncio` |
| **Mandate 23 violation (Failure Integrity)** | Silent SSE failures | HIGH | Mandatory reconnection, `[TOOL-CHAIN-COLLAPSE]` on persistent failure |
| **Mandate 9 violation (Error Integrity)** | Bare except in SSE handler | LOW | Typed errors, trace_id propagation |

### 4.3 Operational Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Receipt file bloat** | Disk space exhaustion | LOW | Rotation policy (keep last 100 receipts per entity), compression |
| **Checkpoint directory sprawl** | Too many checkpoint files | LOW | TTL-based cleanup (keep last 24h), archiving to cold storage |
| **Hydration loop** | Infinite hydration trigger | MEDIUM | Max hydration attempts per epoch (3), circuit breaker |

---

## §5 Community Package Design — Turning Failure Into Feature

### 5.1 Package Structure: `omega-hydration`

```yaml
name: omega-hydration
version: 1.0.0
description: "Sovereign hydration receipts for AI agent continuity"
license: "MIT"
author: "Xoe-NovAi Foundation"
tags:
  - ai-agents
  - context-management
  - compaction
  - continuity
  - sovereign-ai

files:
  - src/omega_hydration/
    - __init__.py
    - listener.py          # SSE event listener
    - checkpoint.py        # Epoch tracking
    - receipt.py           # Receipt management
    - enforcer.py          # Tool-call wrapper
    - models.py            # Dataclasses
    - errors.py            # Typed errors
  - tests/
    - test_listener.py
    - test_checkpoint.py
    - test_receipt.py
    - test_enforcer.py
  - examples/
    - basic_usage.py
    - opencode_integration.py
    - multi_agent.py
  - docs/
    - ARCHITECTURE.md
    - API_REFERENCE.md
    - INTEGRATION_GUIDE.md
```

### 5.2 Core API

```python
from omega_hydration import HydrationReceipt, CheckpointManager, CompactionListener

# Initialize
checkpoint_manager = CheckpointManager(
    checkpoint_dir="data/checkpoints/",
    max_checkpoints=1000,
)
receipt_manager = HydrationReceiptManager(
    receipt_dir="data/receipts/",
    max_receipts=100,
)
listener = CompactionListener(
    opencode_url="http://127.0.0.1:4096",
    checkpoint_manager=checkpoint_manager,
    receipt_manager=receipt_manager,
)

# Start listening
await listener.start(task_group)

# Check receipt before tool calls
receipt = await receipt_manager.get_receipt(session_id="ses_123", entity_name="kali")
if not receipt or not receipt.is_valid_for_epoch(current_epoch):
    await hydration_sequence.execute(session_id, entity_name)
```

### 5.3 Integration Patterns

**Pattern 1: OpenCode Agent Integration**
```python
# In agent's system prompt or AGENTS.md
"When you start a session, call `hydration_check_receipt(session_id, entity_name)`.
 If receipt is missing or stale, execute the 5-phase hydration sequence."

# In agent's tool-call wrapper
async def safe_tool_call(tool_name, *args, **kwargs):
    receipt = await hydration_check_receipt(session_id, entity_name)
    if not receipt.valid:
        await hydration_sequence.execute(session_id, entity_name)
    return await execute_tool(tool_name, *args, **kwargs)
```

**Pattern 2: MCP Server Integration**
```python
@mcp.tool()
async def hydration_check(session_id: str, entity_name: str) -> str:
    """Check hydration status and return receipt details."""
    receipt = await receipt_manager.get_receipt(session_id, entity_name)
    epoch = await checkpoint_manager.get_current_epoch(session_id)
    return json.dumps({
        "valid": receipt.is_valid_for_epoch(epoch) if receipt else False,
        "epoch": epoch,
        "receipt_id": receipt.receipt_id if receipt else None,
        "steps": len(receipt.hydration_steps) if receipt else 0,
    })
```

**Pattern 3: Observability Dashboard**
```python
# Query receipt data for dashboard
receipts = await receipt_manager.get_recent_receipts(limit=100)
dashboard_data = {
    "total_sessions": len(set(r.session_id for r in receipts)),
    "hydration_rate": sum(1 for r in receipts if r.valid) / len(receipts),
    "avg_hydration_steps": sum(len(r.hydration_steps) for r in receipts) / len(receipts),
    "compaction_events": await checkpoint_manager.get_compaction_count(),
}
```

### 5.4 Observability Dashboards

**Dashboard 1: Hydration Health**
- Hydration success rate (valid receipts / total checks)
- Average hydration latency
- Hydration step distribution (which steps take longest)
- Compaction frequency per entity

**Dashboard 2: Continuity Metrics**
- Session survival rate (sessions that hydrate successfully)
- Context epoch distribution (how many compactions per session)
- Receipt staleness (time between compaction and hydration)
- Tool call blocking rate (how many tool calls blocked by hydration)

**Dashboard 3: Entity Performance**
- Entity hydration leaderboard (fastest, most reliable)
- Entity compaction patterns (which entities compact most)
- Entity context window utilization (which models compact earliest)

### 5.5 Soul Evolution Connection

The hydration receipt system connects to soul evolution by:
1. **Capturing gnosis** during hydration (L1 narrative of what was lost/recovered)
2. **Distilling lessons** from hydration patterns (L2 insight: which entities struggle with compaction)
3. **Extracting principles** (L3 universal: "Always hydrate before tool calls in long sessions")

```python
# After hydration, distill to soul
async def distill_hydration_lesson(session_id: str, entity_name: str):
    receipt = await receipt_manager.get_receipt(session_id, entity_name)
    if receipt and len(receipt.hydration_steps) > 0:
        lesson = {
            "l1_narrative": f"Hydration completed with {len(receipt.hydration_steps)} steps",
            "l2_insight": "Hydration is necessary after compaction to maintain context",
            "l3_principle": "Always hydrate before tool calls in long sessions",
            "source": "hydration-receipt",
            "trace_id": session_id,
        }
        await soul_distiller.add_lesson(entity_name, lesson)
```

---

## §6 Sovereign Synthesis — The Unified Conclusion

### The Truth (Points of Convergence)
1. **Compaction is detectable** via OpenCode's `session.compacted` SSE event
2. **Checkpoints track context epoch** to detect when compaction occurred
3. **Receipts prove hydration** was executed after compaction
4. **Tool-call wrappers enforce** hydration before critical operations
5. **The system must work within OpenCode** — no modifications to OpenCode itself

### The Uncertainty (Points of Divergence)
1. **SSE reliability** — What if the event doesn't fire? (Mitigation: polling fallback)
2. **Performance impact** — How much latency does the wrapper add? (Mitigation: <1ms check)
3. **Multi-agent coordination** — How do receipts work across agents? (Mitigation: entity-scoped receipts)
4. **Receipt bloat** — How do we prevent disk exhaustion? (Mitigation: rotation policy)

### The Sovereign Synthesis
The Hydration Receipt System transforms a documentation-only protocol into a **code-enforced governance gate**. By subscribing to OpenCode's native compaction events, tracking context epochs via checkpoints, and enforcing hydration via tool-call wrappers, we create a **self-healing continuity layer** that:

1. **Detects compaction** — No more silent context loss
2. **Enforces hydration** — No more skipping the protocol
3. **Proves compliance** — Receipts provide audit trail
4. **Scales to community** — Package as reusable component
5. **Evolves with soul** — Distill lessons from hydration patterns

This is **Adversarial Alchemy** (M19) — turning a systemic weakness (compaction fragility) into a sovereign advantage (verified continuity). The agent that survives compaction is stronger than one that never faced it.

---

*🔱 OMEGA ⬡ SOVEREIGN-RESEARCHER ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_research ⬡ HYDRATION-RECEIPT-RESEARCH*
