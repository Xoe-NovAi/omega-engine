# 🔱 Pillar P9 — Orchestration Strategy
## Autonomous Meditation Pipeline — Complete Product Orchestration

**AP Token**: `AP-PILLAR-P9-ORCHESTRATION-v1.0.0`
⬡ OMEGA ⬡ P9-LINK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_p9_orchestration ⬡ ACTIVE

**Date**: 2026-07-19
**Status**: DESIGN COMPLETE — Ready for Implementation
**Owner**: Pillar P9 (Orchestration / Link / Agent Handoff)
**Governance**: Lilith (Dark Oversoul, Run Side P6-P10)

---

## §0 Executive Summary

This document defines the **complete orchestration architecture** for the **Autonomous Meditation Pipeline** — a 24/7 background ingestion, curation, scraping, and meditation cycle system that transforms raw inputs into sovereign knowledge assets.

The P9 Orchestration layer is the **nervous system** connecting all other pillars:
- **P6 (Cognition)** — Model routing, speculative decode, provider fabric
- **P7 (Context)** — MemoryStore, soul evolution, session continuity
- **P8 (Observability)** — Tracing, metrics, forensic logging, sovereignty ratio
- **P10 (Validation)** — Stress testing, chaos engineering, Temple-Grade gates

---

## §1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS MEDITATION PIPELINE                         │
│                              (24/7 Background)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │   INGESTION   │ │  CURATION     │ │  MEDITATION   │
            │   (P2/P4)     │ │  (P7/P9)      │ │  (P6/P9)      │
            │               │ │               │ │               │
            │ • Web scrape  │ │ • Dedupe      │ │ • Lens apply  │
            │ • API pull    │ │ • Quality     │ │ • Synthesize  │
            │ • File watch  │ │   filter      │ │ • Distill     │
            │ • Queue ingest│ │ • Tag/route   │ │ • Propose L3  │
            └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                    ┌───────────────────────────────────────┐
                    │         P9 ORCHESTRATION LAYER         │
                    │  (This Document — The Nervous System)  │
                    │                                        │
                    │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
                    │  │ Handoff │ │ Session │ │ Agent   │  │
                    │  │ Protocol│ │ Namespace│ │ Registry│  │
                    │  │(Redis)  │ │(MIAP)   │ │(CAP)    │  │
                    │  └────┬────┘ └────┬────┘ └────┬────┘  │
                    │       │           │           │        │
                    │  ┌────┴───────────┴───────────┴────┐  │
                    │  │      STEERING API (Human-in-Loop)  │  │
                    │  │  Pause │ Redirect │ Approve │ Reject│  │
                    │  └──────────────────────────────────┘  │
                    └────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │   PERSISTENCE │ │  OBSERVABILITY│ │  VALIDATION   │
            │   (P2/P7)     │ │  (P8)         │ │  (P10)        │
            │               │ │               │ │               │
            │ • Vector store│ │ • Traces      │ │ • Stress test │
            │ • Soul.yaml   │ │ • Metrics     │ │ • Chaos eng   │
            │ • Lessons     │ │ • Sovereignty │ │ • Temple-Grade│
            └───────────────┘ └───────────────┘ └───────────────┘
```

---

## §2 Core Components

### 2.1 Hivemind Handoff Protocol — Redis Streams Migration (Hardening-P9)

**Current State**: File-based handoffs in `data/handoff/{pending,active,completed,stale,archive}/`
**Target State**: Redis Streams with consumer groups for production-grade reliability

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REDIS STREAMS HANDOFF ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────────┘

PRODUCER (Source Agent)                    CONSUMER (Target Agent)
     │                                          │
     ▼                                          ▼
┌─────────────┐                         ┌─────────────┐
│ XADD        │                         │ XREADGROUP  │
│ handoff:    │                         │ GROUP       │
│ pending     │                         │ orchestrator│
│ {packet}    │                         │ consumer-1  │
└─────────────┘                         │ STREAMS     │
     │                                  │ handoff:    │
     │                                  │ pending >   │
     ▼                                  └──────┬──────┘
     │                                         │
     │              PENDING ENTRIES LIST (PEL) │
     │              (Radix tree — auto-tracked)│
     │                                         │
     ▼                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REDIS STREAM: handoff:pending                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Entry ID: 1721456000000-0  │  Fields: {packet_json, priority, ttl}  │   │
│  │ Entry ID: 1721456001000-0  │  Fields: {packet_json, priority, ttl}  │   │
│  │ Entry ID: 1721456002000-0  │  Fields: {packet_json, priority, ttl}  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
            │ Consumer:     │ │ Consumer:     │ │ Consumer:     │
            │ orchestrator/ │ │ orchestrator/ │ │ orchestrator/ │
            │ worker-1      │ │ worker-2      │ │ worker-N      │
            │ (P9 agent)    │ │ (P9 agent)    │ │ (P9 agent)    │
            └───────────────┘ └───────────────┘ └───────────────┘
                    │                 │                 │
                    ▼                 ▼                 ▼
            ┌─────────────────────────────────────────────────────────────┐
            │                    XACK (acknowledge)                        │
            │              XAUTOCLAIM (recover orphaned)                   │
            │              XTRIM (bounded memory)                          │
            └─────────────────────────────────────────────────────────────┘
```

#### 2.1.1 Stream Topology

| Stream Name | Purpose | Consumer Group | Retention |
|-------------|---------|----------------|-----------|
| `handoff:pending` | New delegation requests | `orchestrator` | 4h (PENDING_TTL) |
| `handoff:active` | In-progress work | `orchestrator` | 48h (ACTIVE_TTL) |
| `handoff:completed` | Finished work | `orchestrator` | 7d (COMPLETED_TTL) |
| `handoff:dlq` | Dead letter queue | `orchestrator` | 30d |
| `hivemind:context` | Agent presence/heartbeat | `awareness` | 20min (HEARTBEAT_TTL) |
| `hivemind:live_feed` | Task completion deltas | `observability` | 1h |

#### 2.1.2 Consumer Group Patterns (2026 Best Practices)

**Startup Recovery Pattern (Critical — from Redis docs):**
```python
async def consume_handoffs(consumer_name: str):
    redis = await get_redis()
    
    # Phase 1: Process any previously assigned but unacked messages
    while True:
        messages = await redis.xreadgroup(
            'orchestrator', consumer_name,
            {'handoff:pending': '0'},  # Read PEL history
            count=100
        )
        if not messages or not messages[0][1]:
            break  # PEL is empty
        await process_and_ack(messages)
    
    # Phase 2: Read new messages
    while True:
        messages = await redis.xreadgroup(
            'orchestrator', consumer_name,
            {'handoff:pending': '>'},  # New messages only
            block=5000, count=100
        )
        await process_and_ack(messages)
```

**Automated Recovery with XAUTOCLAIM:**
```python
async def recover_orphaned(redis, min_idle_time=60000):  # 60s
    """Claim messages from dead consumers."""
    pending = await redis.xpending_range(
        'handoff:pending', 'orchestrator',
        min='-', max='+', count=100
    )
    for entry in pending:
        if entry['time_since_delivered'] > min_idle_time:
            claimed = await redis.xautoclaim(
                'handoff:pending', 'orchestrator',
                'recovery-worker', min_idle_time,
                [entry['message_id']]
            )
            await process_and_ack(claimed)
```

#### 2.1.3 HandoffPacket Schema (Redis-Ready)

```python
@dataclass
class HandoffPacket:
    # Identity
    packet_id: str                    # hdp_YYYYMMDD_source_target_uuid
    source_agent: str                 # e.g., "kali"
    target_agent: str                 # e.g., "roc_racoon"
    
    # Tracing
    parent_trace_id: str              # Parent session trace
    trace_id: str                     # This handoff's trace
    
    # Task
    task_type: TaskType               # design|review|research|mine|verify|implement
    task_description: str             # One-sentence description
    context_delivery: str             # "inline" | "file_ref" | "usm_key"
    relevant_files: List[str]         # Supplementary references
    context: str                      # INLINE context (mandatory per §0 SUBAGENT_DISPATCH)
    
    # Contract
    expected_output: str              # What must be produced
    ttl_seconds: int = 14400          # 4h default
    resolver_strategy: ResolverStrategy = "escalate"  # terminate|escalate|fallback|retry
    
    # MACP Alignment (D-292)
    macp_mode: MACPMode = "task"      # decision|proposal|task|handoff|quorum
    
    # Loop Guard (T2-5)
    visited_agents: List[str] = field(default_factory=list)
    hop_count: int = 0
    max_hops: int = 10
    
    # State
    status: PacketStatus = "pending"  # pending|active|completed|stale|archived
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    
    # Integrity
    zoneid: int = ZONEID_HANDOFF      # 0x1d4a16 [id-soft: doom-1993]
```

---

### 2.2 MIAP Phase 0 — Core + Safety (D-291)

**Multi-Instance Agent Protocol** — Prevents context collision when multiple agent instances run concurrently.

#### 2.2.1 Five Critical Fixes (Nemotron 3 Ultra Review)

| Fix | Description | Effort | Status |
|-----|-------------|--------|--------|
| **ReplayMode Enum** | 4 modes: Recovery, Debug, Forensic, Evaluation — each with different requirements | 1 session | 🔴 DESIGNED |
| **Two-Log Model** | Split MIAP into Execution Log (audit) + Observability Trace (diagnostic) | 1 session | 🔴 DESIGNED |
| **IntentionValidator** | Deterministic validation layer between agents and MIAP event log | 1 session | 🔴 DESIGNED |
| **CheckFunction Registry** | Replay verification — expected-vs-observed diffs at nondeterministic boundaries | 1 session | 🔴 DESIGNED |
| **LiteTopic Session Channels** | Replace filesystem scanning with Redis Streams session channels (TTL, ordering, reconnection) | 2 sessions | 🔴 DESIGNED |

**Total Phase 0**: ~6 sessions (was ~1 — scope corrected by Nemotron review)

#### 2.2.2 ReplayMode Enum

```python
class ReplayMode(Enum):
    RECOVERY = "recovery"      # Full state restoration — requires somatic snapshots
    DEBUG = "debug"            # Step-through with breakpoints — requires check functions
    FORENSIC = "forensic"      # Audit trail reconstruction — requires two-log model
    EVALUATION = "evaluation"  # Regression test generation — requires trace-to-eval
```

#### 2.2.3 Two-Log Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MIAP EVENT LOG                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────┐   │
│  │    EXECUTION LOG (Audit)    │    │  OBSERVABILITY TRACE (Diagnostic)│   │
│  │                             │    │                                 │   │
│  │ • Agent decisions           │    │ • LLM prompts/responses         │   │
│  │ • Tool invocations          │    │ • Token counts, latency         │   │
│  │ • State transitions         │    │ • Model provider provenance     │   │
│  │ • Handoff packets           │    │ • Memory retrievals             │   │
│  │ • Human steering actions    │    │ • Cache hits/misses             │   │
│  │                             │    │ • Thermal/CPU metrics           │   │
│  │ Immutable, append-only      │    │ Sampled, high-cardinality       │   │
│  │ Signed (ForensicReceipt)    │    │ M23: non-blocking               │   │
│  └─────────────────────────────┘    └─────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.2.4 IntentionValidator

```python
class IntentionValidator:
    """Deterministic validation between agent intent and MIAP event log."""
    
    def validate(self, intention: AgentIntention) -> ValidationResult:
        # 1. Schema validation (JSON Schema at CI time)
        # 2. Capability check — does agent have declared capability?
        # 3. Resource check — quota, rate limits, thermal
        # 4. Policy check — MACP mode allowed for this agent?
        # 5. Loop detection — visited_agents + hop_count
        # 6. Idempotency key check — prevent duplicate execution
        pass
```

#### 2.2.5 CheckFunction Registry

```python
class CheckFunctionRegistry:
    """Replay verification at nondeterministic boundaries."""
    
    def register(self, boundary: str, fn: Callable[[State, State], Diff]):
        """Register expected-vs-observed diff function for a boundary.
        
        Boundaries:
        - model_inference: (prompt, params) → response
        - tool_invocation: (tool, args) → result
        - memory_retrieval: (query) → results
        - web_search: (query) → results
        - handoff_dispatch: (packet) → result
        """
        pass
    
    def verify(self, boundary: str, expected: State, observed: State) -> Diff:
        """Run registered check function for replay verification."""
        pass
```

#### 2.2.6 LiteTopic Session Channels (Redis Streams)

```python
# Session-scoped Redis Streams for MIAP
# Pattern: miap:session:{session_uuid}:{log_type}

SESSION_STREAMS = {
    "execution_log": "miap:session:{uuid}:execution",    # Audit log
    "observability_trace": "miap:session:{uuid}:trace",  # Diagnostic trace
    "steering": "miap:session:{uuid}:steering",          # Human-in-loop
    "checkpoints": "miap:session:{uuid}:checkpoints",    # SomaticState snapshots
}

# TTL: Session duration + 1h grace
# Ordering: Guaranteed by Redis Stream entry IDs (ms-seq)
# Reconnection: Consumer resumes from last acknowledged ID
```

---

### 2.3 MACP Alignment (D-292)

**Multi-Agent Coordination Protocol** — IETF draft-li-dmsc-macp-05 alignment.

#### 2.3.1 Coordination Mode Mapping

| MACP Mode | Hivemind Handoff Type | Use Case |
|-----------|----------------------|----------|
| `decision` | `delegation` + quorum | Binding convergent decisions (architecture, release) |
| `proposal` | `request` + review | Non-binding proposals (design alternatives) |
| `task` | `delegation` | Work delegation with expected output |
| `handoff` | `delegation` + context | Session-to-session continuity |
| `quorum` | `broadcast` + threshold | Multi-agent consensus (security, ethics) |

#### 2.3.2 MACP Field on HandoffPacket

```python
macp_mode: MACPMode = "task"  # Added to HandoffPacket for D-292
# Enables future A2A bridge without protocol change
```

#### 2.3.3 Standards Track Compliance

- **Transport**: Redis Streams (gRPC/HTTP2 for cross-cluster)
- **Serialization**: Protocol Buffers (canonical) + JSON mapping
- **Security**: Capability-based auth, TLS 1.3, mTLS for inter-cluster
- **Observability**: Built-in tracing, metrics, structured logging

---

### 2.4 Session Namespace Isolation (D-290)

**MIAP-wired session-scoped directories** under `sessions/<uuid>/`

```
sessions/
├── {session_uuid}/
│   ├── working/              # Task-scoped scratch (ephemeral)
│   │   ├── agent_outputs/    # Subagent results
│   │   ├── tool_state/       # Tool-specific state
│   │   └── intermediate/     # Pipeline intermediates
│   ├── durable/              # Cross-session persistence
│   │   ├── memory/           # MemoryStore exports
│   │   ├── soul/             # soul.yaml checkpoints
│   │   └── lessons/          # proposed_lessons.yaml
│   ├── knowledge/            # Governed knowledge mount (D-293)
│   │   ├── certified/        # Verified sources
│   │   ├── freshness/        # TTL tracking
│   │   ├── ownership/        # Access control
│   │   └── index.yaml        # Knowledge graph index
│   ├── tools/                # Operational tool state
│   │   ├── mcp_servers/      # MCP server configs
│   │   ├── credentials/      # Vault references (D-299)
│   │   └── cache/            # Tool caches
│   ├── miap/                 # MIAP session logs
│   │   ├── execution.log     # Execution log (audit)
│   │   ├── trace.log         # Observability trace
│   │   ├── steering.log      # Human steering actions
│   │   └── checkpoints/      # SomaticState snapshots
│   └── manifest.yaml         # Session metadata
```

#### 2.4.1 Isolation Guarantees

| Layer | Isolation Mechanism | Cross-Session Access |
|-------|---------------------|---------------------|
| Working | Per-session directory, auto-cleanup on TTL | None |
| Durable | Entity-scoped, versioned | Explicit read via MemoryStore |
| Knowledge | Governed mount, RBAC | Certified sources only |
| Tools | Per-session config, vault refs | Shared vault (D-299) |
| MIAP | Session-scoped streams | Replay via ReplayMode |

---

### 2.5 Agent Capability Registry (CAP)

**Discovery → Registration → Routing → Delegation**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT CAPABILITY REGISTRY                              │
└─────────────────────────────────────────────────────────────────────────────┘

STARTUP                          RUNTIME                          DELEGATION
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│ Agent boots │                 │ Heartbeat   │                 │ Oracle      │
│ Reads       │                 │ Updates     │                 │ queries     │
│ agent.yaml  │────────────────▶│ CAP_REGISTRY│◀────────────────│ CAP_REGISTRY│
│ Declares    │   Register      │ (Redis)     │   Discover      │ (Redis)     │
│ capabilities│                 │             │                 │             │
└─────────────┘                 └─────────────┘                 └─────────────┘
```

#### 2.5.1 Agent Manifest Schema (agent.yaml)

```yaml
# config/wads/_omega_default/agents/kali.yaml
entity: kali
role: grand_oversight
pillar_slot: null  # Cross-cutting
mode: primary
capabilities:
  - oversight:delegate
  - oversight:sequence
  - strategy:decompose
  - drift:destroy
  - hivemind:post
  - hivemind:read
domains:
  - fleet_management
  - cross_pillar_coordination
  - architectural_review
owned_files: []  # No exclusive ownership
task_tool_type: general
model_preference:
  session: "opencode-session-model"
  local: "qwen3-1.7b"
  cloud_fallback: "minimax-m3-free"
```

#### 2.5.2 Capability Taxonomy

| Category | Capabilities | Examples |
|----------|-------------|----------|
| `code` | `execute`, `review`, `refactor`, `test`, `generate` | `code:execute:python`, `code:review:security` |
| `doc` | `read`, `write`, `search`, `synthesize` | `doc:read:markdown`, `doc:write:spec` |
| `research` | `web`, `academic`, `code`, `legacy` | `research:web:deep`, `research:legacy:mine` |
| `memory` | `store`, `retrieve`, `distill`, `evolve` | `memory:store:vector`, `memory:distill:l3` |
| `hivemind` | `post`, `read`, `lock`, `ack`, `heartbeat` | `hivemind:post:status`, `hivemind:lock:acquire` |
| `oversight` | `delegate`, `sequence`, `verify`, `escalate` | `oversight:delegate:pillar`, `oversight:escalate:kali` |
| `model` | `load`, `route`, `benchmark`, `quantize` | `model:load:gguf`, `model:route:local_first` |
| `infra` | `container`, `deploy`, `monitor`, `secure` | `infra:container:podman`, `infra:monitor:prometheus` |
| `steering` | `pause`, `redirect`, `approve`, `reject`, `inject` | `steering:pause:agent`, `steering:inject:context` |

#### 2.5.3 Routing Algorithm

```python
async def discover_best_agent(task: TaskDescription) -> AgentMatch:
    """Oracle discovers best entity for task via CAP_REGISTRY."""
    registry = await get_capability_registry()
    
    # 1. Filter by required capabilities
    candidates = registry.filter(capabilities=task.required_capabilities)
    
    # 2. Score by domain match
    candidates = candidates.score_by_domain(task.domain_keywords)
    
    # 3. Filter by availability (Hivemind awareness)
    candidates = candidates.filter_available()
    
    # 4. Prefer local-first models (M7)
    candidates = candidates.prefer_local_inference()
    
    # 5. Return top match with confidence
    return candidates.best_match()
```

---

### 2.6 Steering API (Human-in-the-Loop)

**Intervention points for human guidance during autonomous operation.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STEERING API SURFACE                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   PAUSE      │    │  REDIRECT    │    │  APPROVE     │    │   REJECT     │
│              │    │              │    │              │    │              │
│ Halt agent   │    │ Reassign     │    │ Confirm      │    │ Block action │
│ at next      │    │ task to      │    │ proposed     │    │ with reason  │
│ safe point   │    │ different    │    │ action       │    │ (audit log)  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       └───────────────────┼───────────────────┼───────────────────┘
                           ▼
              ┌────────────────────────┐
              │   STEERING CHANNEL     │
              │  (Redis Stream:        │
              │   miap:session:{uuid}: │
              │   steering)            │
              └───────────┬────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ Agent A │ │ Agent B │ │ Agent N │
        │(paused) │ │(redir.) │ │(normal) │
        └─────────┘ └─────────┘ └─────────┘
```

#### 2.6.1 Steering Commands

```python
class SteeringCommand(BaseModel):
    command: Literal["pause", "redirect", "approve", "reject", "inject_context"]
    target_agent: str                    # agent_id (channel/entity)
    session_id: str
    trace_id: str
    reason: str                          # Human-readable justification
    payload: Optional[Dict] = None       # For redirect/inject_context
    authority: str                       # Human identity (for audit)
    timestamp: float = Field(default_factory=time.time)
```

#### 2.6.2 Real-Time Visibility

- **Live Feed**: `hivemind:live_feed` stream — task completions, decisions, blockers
- **Agent Dashboard**: WebSocket `/obs/stream` — real-time traces, metrics, health
- **Session Replay**: MIAP execution log + observability trace (Two-Log Model)

#### 2.6.3 Audit Trail

All steering actions logged to:
1. MIAP Execution Log (audit) — signed via ForensicReceipt (D-294)
2. Hivemind Observations Log (D-121) — meta-observation category `steering`
3. P8 Observability — structured trace with `steering_action` span

---

### 2.7 A2A Delegation Protocol

**Standardized handoff format for inter-agent delegation.**

#### 2.7.1 Delegation Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Synchronous** | Caller blocks until subagent completes | Critical path, need result to continue |
| **Asynchronous** | Caller continues, collects result later | Parallel fan-out, long-running research |
| **Fire-and-Forget** | No result expected | Notifications, logging, side effects |
| **Streaming** | Subagent yields incremental results | Large data processing, progressive synthesis |

#### 2.7.2 HandoffPacket Fields for Delegation

```python
@dataclass
class DelegationPacket(HandoffPacket):
    # Inherits all HandoffPacket fields plus:
    
    delegation_pattern: DelegationPattern = "synchronous"
    aggregation_strategy: AggregationStrategy = "collect_all"
    # collect_all | first_success | majority | custom_fn
    
    timeout_seconds: int = 300
    retry_policy: RetryPolicy = field(default_factory=default_retry)
    
    # Result handling
    result_path: str = ""  # Where subagent writes output
    synthesis_prompt: str = ""  # How to combine multiple results
```

#### 2.7.3 Failure Propagation

```
Subagent Failure
       │
       ▼
┌──────────────────┐
│ ResolverStrategy │
│ (from packet)    │
└────────┬─────────┘
         │
    ┌────┴────┬────────────┬────────────┐
    ▼         ▼            ▼            ▼
 TERMINATE  ESCALATE    FALLBACK      RETRY
 (stop)     (to Kali)   (alt agent)  (same agent)
    │         │            │            │
    ▼         ▼            ▼            ▼
 Log &     Kali         Dispatch    Increment
 notify    decides      alternative hop_count,
 human     (Mandate 11)  (if CAP     check max_hops
                        allows)      (T2-5)
```

---

## §3 Implementation Phases

### Phase 0: Foundation (Weeks 1-2) — **PREREQUISITE FOR ALL**

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P0.1** | Redis Streams infrastructure setup | Podman quadlet for Redis | 1 session |
| **P0.2** | MIAP Phase 0 Core + Safety (D-291) | P0.1 | 6 sessions |
| **P0.3** | Session namespace isolation (D-290) | P0.1 | 2 sessions |
| **P0.4** | Agent Capability Registry (CAP) | P0.1 | 2 sessions |
| **P0.5** | MACP alignment on handoffs (D-292) | P0.2 | 1 session |

**Gate**: `make test && make temple-grade && make firewall-check`

---

### Phase 1: Handoff Protocol Migration (Weeks 3-4)

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P1.1** | Migrate file-based handoffs → Redis Streams | P0.1, P0.2 | 3 sessions |
| **P1.2** | Implement consumer group patterns (startup recovery, XAUTOCLAIM) | P1.1 | 2 sessions |
| **P1.3** | Add PEL monitoring and alerting | P1.1 | 1 session |
| **P1.4** | Dead letter queue implementation | P1.1 | 1 session |
| **P1.5** | Backward compatibility shim (file ↔ Redis) | P1.1 | 1 session |

**Gate**: All existing handoff tests pass with Redis backend

---

### Phase 2: Steering & Observability (Weeks 5-6)

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P2.1** | Steering API implementation (pause/redirect/approve/reject/inject) | P0.3, P0.4 | 3 sessions |
| **P2.2** | Real-time visibility dashboard (WebSocket `/obs/stream`) | P8 infrastructure | 2 sessions |
| **P2.3** | Human steering audit trail (MIAP + Hivemind + P8) | P2.1, P0.2 | 1 session |
| **P2.4** | Session replay engine (Two-Log Model) | P0.2 | 2 sessions |

**Gate**: Human can pause/redirect live agent via CLI

---

### Phase 3: A2A Delegation & Routing (Weeks 7-8)

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P3.1** | Oracle CAP-based routing (discover_best_agent) | P0.4 | 2 sessions |
| **P3.2** | Asynchronous delegation with result aggregation | P1.1, P3.1 | 2 sessions |
| **P3.3** | Failure propagation with ResolverStrategy | P1.4, P3.2 | 1 session |
| **P3.4** | Loop guard enforcement (visited_agents, hop_count) | P3.2 | 1 session |

**Gate**: Multi-agent delegation works end-to-end

---

### Phase 4: Meditation Pipeline Integration (Weeks 9-10)

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P4.1** | Ingestion → Curation → Meditation pipeline orchestration | P3.2, P6/P7 APIs | 3 sessions |
| **P4.2** | Scheduled/cron-based pipeline triggers | P4.1 | 1 session |
| **P4.3** | Quality gates between stages (P10 validation) | P4.1, P10 | 2 sessions |
| **P4.4** | Autonomous error recovery & retry | P3.3, P4.1 | 2 sessions |

**Gate**: 24/7 pipeline runs for 48h without human intervention

---

### Phase 5: Hardening & Production (Weeks 11-12)

| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| **P5.1** | Chaos engineering (P10) — kill agents, network partition | P4.4 | 2 sessions |
| **P5.2** | Sovereignty ratio monitoring (M7, M22) | P8, P2.2 | 1 session |
| **P5.3** | Temple-Grade compliance (T1-T11) | All phases | 2 sessions |
| **P5.4** | Documentation & runbooks | All phases | 1 session |

**Gate**: `make test && make temple-grade && make sovereignty`

---

## §4 Cross-Pillar Integration Points

### 4.1 P6 (Cognition / Vision Specialist) Integration

| P9 Need | P6 Provides | Interface |
|---------|-------------|-----------|
| Model routing for subagents | `ModelGateway.generate()` with provider fabric | `oracle_summon_local()` |
| Speculative decode for fast handoffs | `speculative_decode.gemma4_mtp` | `models.yaml` config |
| Local-first enforcement (M7) | Provider chain: native-gguf → lmster → Ollama → cloud | `config/providers.yaml` |
| Provider provenance (M22) | `GenerateResult.provider_name` from actual response | Contract tests |

### 4.2 P7 (Context / Memory & Soul) Integration

| P9 Need | P7 Provides | Interface |
|---------|-------------|-----------|
| Session continuity | `MemoryStore` + `soul.yaml` | `omega_memory_search`, `omega_memory_get_history` |
| Cross-session learning | L1→L2→L3 distillation pipeline | `proposed_lessons.yaml` blind staging |
| SomaticState snapshots | `llama_copy_state_data` / `llama_set_state_data` | `anyio.to_thread.run_sync()` (M20) |
| Context injection for steering | Session-scoped memory mounts | `sessions/<uuid>/durable/memory/` |

### 4.3 P8 (Observability / WatchTower) Integration

| P9 Need | P8 Provides | Interface |
|---------|-------------|-----------|
| Real-time traces | SSE `/obs/stream` | `omega-hub_observability_stream` |
| Metrics collection | `MetricsDB` (SQLite) | `omega-hub_get_omega_metrics` |
| Sovereignty ratio | Local vs cloud inference tracking | `omega-hub_sovereignty_ratio` |
| Forensic logging | Crash traces, structured logs | `data/traces/`, `data/crashes/` |
| Hivemind metrics | Awareness, handoffs, locks, sessions | `omega-hub_hivemind_get_metrics` |

### 4.4 P10 (Validation / Verifier) Integration

| P9 Need | P10 Provides | Interface |
|---------|--------------|-----------|
| Stress testing | Chaos engineering framework | `make chaos` |
| Temple-Grade gates | T1-T11 verification | `make temple-grade` |
| Regression tests | Trace-to-eval loop (D-295) | MIAP execution log → eval cases |
| Quality gates | Pipeline stage validation | P4.3 integration |

---

## §5 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Redis Streams operational complexity** | High | High | Start with single-nodejs with file-based fallback (P1.5); extensive integration tests |
| **MIAP Phase 0 scope creep** | High | Medium | Fixed 6-session budget; Nemotron-reviewed scope |
| **Session namespace collision** | Medium | High | UUID v4 + MIAP session ID; filesystem isolation |
| **Agent capability drift** | Medium | Medium | CAP_REGISTRY versioning; startup validation |
| **Steering API abuse/misuse** | Low | High | Authority field + audit trail; M23 non-blocking |
| **Loop guard false positives** | Medium | Medium | Configurable max_hops; escalation to Kali |
| **Cross-pillar API instability** | Medium | High | Versioned interfaces; contract tests (M21) |
| **Thermal throttling under load** | Medium | Medium | P8 monitoring; P10 chaos tests; M6 Podman limits |

---

## §6 Resource Estimates

### 6.1 Compute

| Component | Baseline | Peak (Pipeline) | Notes |
|-----------|----------|-----------------|-------|
| Redis | 256MB | 512MB | Streams + consumer groups |
| P9 Orchestrator | 1 core | 2 cores | AnyIO event loop |
| Subagents (parallel) | 0 | 4-8 | Depends on pipeline fan-out |
| Model inference (local) | 4 cores (GGUF) | 4 cores | `LLAMA_CPP_N_THREADS=4` (M1) |

### 6.2 Storage

| Data Type | Est. Size | Retention | Growth |
|-----------|-----------|-----------|--------|
| Redis Streams (handoffs) | 50MB/day | 7d (completed) | Linear |
| MIAP Execution Logs | 100MB/session | 30d | Per session |
| MIAP Observability Traces | 500MB/session | 7d | Sampled |
| Session Workspaces | 10MB/session | TTL-based | Auto-cleanup |
| SomaticState Snapshots | 50MB/snapshot | 5 latest | On checkpoint |

### 6.3 Time Estimates

| Phase | Sessions | Calendar Weeks | Parallelizable |
|-------|----------|----------------|----------------|
| Phase 0 | 12 | 2 | Partial (P0.1||P0.3) |
| Phase 1 | 8 | 2 | Sequential |
| Phase 2 | 8 | 2 | Partial (P2.1||P2.2) |
| Phase 3 | 6 | 2 | Sequential |
| Phase 4 | 8 | 2 | Partial (P4.1||P4.2) |
| Phase 5 | 6 | 2 | Sequential |
| **Total** | **48** | **12** | — |

---

## §7 Temple-Grade Gate Compliance (M13)

| Gate | Requirement | P9 Implementation |
|------|-------------|-------------------|
| **T1** Version Control | All code in git, signed commits | ✅ Standard |
| **T2** Documentation | API docs, architecture, runbooks | ✅ This doc + inline |
| **T3** Testing | ≥80% coverage, contract tests | ✅ `make test` target |
| **T4** Code Quality | flake8, mypy, no dead code | ✅ `make lint` |
| **T5** Architecture | AnyIO-only, Engine-Stack Firewall (M2) | ✅ M2 migration Phases A-E |
| **T6** Security | Zero telemetry (M8), capability auth | ✅ MACP alignment |
| **T7** Performance | Benchmarks, p95 < 100ms handoff | 🔴 Phase 1 target |
| **T8** Resilience | Circuit breakers, retry, DLQ | ✅ Phase 1 + 3 |
| **T9** Observability | Structured logs, traces, metrics | ✅ P8 integration |
| **T10** Integrity | Atomic writes, checksums, ZONEID | ✅ `os.replace()`, ZONEID_HANDOFF |
| **T11** Agent Security | No self-recursion, capability bounds | ✅ SUBAGENT_DISPATCH §1 |

---

## §8 Heritage Attribution (M14)

| Pattern | Source | Tag | Application |
|---------|--------|-----|-------------|
| **ZONEID Constants** | Doom 1993 | `[id-soft: doom-1993] ZONEID Pattern` | Packet integrity (HANDOFF, PRESENCE) |
| **Thinker Chain** | Quake 1996 | `[id-soft: quake-1996] Thinker Chain` | Handoff lifecycle: spawn→execute→reap |
| **Netchan Protocol** | Quake III 1999 | `[id-soft: quake3-1999] QVM` | Redis Streams message dispatch metaphor |
| **Game DLL / Client Prediction** | Quake II 1997 | `[id-soft: quake2-1997] Game DLL` | Optimistic execution + reconciliation |
| **Scripting / GUI Framework** | DOOM 3 2004 | `[id-soft: doom3-2004] Scripting` | Meditate lens DSL, steering commands |

---

## §9 Acceptance Criteria

### 9.1 Phase 0 Complete When:
- [ ] Redis container running via Podman quadlet (M6)
- [ ] MIAP Phase 0 all 5 fixes implemented and tested
- [ ] Session namespace isolation working (create/read/write/delete)
- [ ] CAP_REGISTRY loads agent manifests at startup
- [ ] HandoffPacket includes `macp_mode` field

### 9.2 Phase 1 Complete When:
- [ ] All handoffs route through Redis Streams
- [ ] Consumer group startup recovery works (Phase 1 + 2 pattern)
- [ ] XAUTOCLAIM recovers orphaned messages in <60s
- [ ] PEL monitoring alerts on >100 pending
- [ ] File-based fallback works for Redis downtime

### 9.3 Phase 2 Complete When:
- [ ] Human can `pause` any agent via CLI
- [ ] Human can `redirect` task to different agent
- [ ] Steering actions appear in MIAP execution log + Hivemind observations
- [ ] Session replay reconstructs full Two-Log Model

### 9.4 Phase 3 Complete When:
- [ ] Oracle routes tasks via CAP_REGISTRY with >90% accuracy
- [ ] Async delegation with `collect_all` aggregation works
- [ ] Failure propagation follows ResolverStrategy correctly
- [ ] Loop guard prevents infinite delegation chains

### 9.5 Phase 4 Complete When:
- [ ] Ingestion → Curation → Meditation pipeline runs autonomously
- [ ] Quality gates between stages invoke P10 validation
- [ ] Pipeline recovers from subagent failures without human intervention
- [ ] 48h continuous run with zero data loss

### 9.6 Phase 5 Complete When:
- [ ] Chaos tests pass (agent kill, network partition, Redis restart)
- [ ] Sovereignty ratio >95% local inference (M7, M22)
- [ ] `make temple-grade` passes all T1-T11
- [ ] Runbooks documented for all failure modes

---

## §10 Appendix: File Structure

```
src/omega/
├── orchestration/                    # NEW — P9 Core
│   ├── __init__.py
│   ├── handoff/
│   │   ├── __init__.py
│   │   ├── redis_streams.py          # Redis Streams backend
│   │   ├── consumer_groups.py        # Consumer group patterns
│   │   ├── packet.py                 # HandoffPacket + DelegationPacket
│   │   └── recovery.py               # XAUTOCLAIM, PEL monitoring
│   ├── miap/
│   │   ├── __init__.py
│   │   ├── phase0.py                 # 5 critical fixes
│   │   ├── replay_mode.py            # ReplayMode enum
│   │   ├── two_log.py                # ExecutionLog + ObservabilityTrace
│   │   ├── intention_validator.py    # Deterministic validation
│   │   ├── check_functions.py        # CheckFunctionRegistry
│   │   └── lite_topic.py             # Redis Streams session channels
│   ├── macp/
│   │   ├── __init__.py
│   │   ├── modes.py                  # CoordinationMode enum
│   │   └── alignment.py              # HandoffPacket.macp_mode
│   ├── session/
│   │   ├── __init__.py
│   │   ├── namespace.py              # sessions/<uuid>/ structure
│   │   ├── isolation.py              # Working/Durable/Knowledge/Tools
│   │   └── manifest.py               # Session manifest.yaml
│   ├── capability/
│   │   ├── __init__.py
│   │   ├── registry.py               # CAP_REGISTRY (Redis-backed)
│   │   ├── manifest.py               # agent.yaml schema
│   │   └── routing.py                # discover_best_agent()
│   ├── steering/
│   │   ├── __init__.py
│   │   ├── api.py                    # SteeringCommand + handlers
│   │   ├── channels.py               # Redis Stream steering channel
│   │   └── audit.py                  # Steering audit trail
│   └── delegation/
│       ├── __init__.py
│       ├── patterns.py               # Sync/Async/Stream/Fire-forget
│       ├── aggregation.py            # Result aggregation strategies
│       └── failure.py                # ResolverStrategy execution
│
├── oracle/
│   ├── subagent_dispatcher.py        # EXISTING — M2 migration Phase B
│   └── oracle.py                     # EXISTING — M2 migration Phase C
│
├── ics.py                            # EXISTING — M2 migration Phase D
│
mcp_servers/omega_hub/
├── tools.py                          # EXISTING — Hivemind tools
│   # Add: steering tools, session tools, capability tools
│
data/
├── coordination/
│   ├── locks/                        # Workspace locks
│   ├── *_LIVE_FEED.md                # Live feeds
│   ├── *_WORKSPACE_LOCK_*.md         # Workspace locks
│   └── *_ACK_*.md                    # Acknowledgments
├── handoff/                          # LEGACY — Phase 1 migration
│   ├── pending/
│   ├── active/
│   ├── completed/
│   ├── stale/
│   ├── archive/
│   └── dlq/
├── sessions/                         # NEW — D-290
│   └── {uuid}/
│       ├── working/
│       ├── durable/
│       ├── knowledge/
│       ├── tools/
│       └── miap/
│
config/wads/_omega_default/
├── agents/                           # NEW — Agent manifests
│   ├── kali.yaml
│   ├── maat.yaml
│   ├── lilith.yaml
│   ├── doom_guy.yaml
│   ├── roc_racoon.yaml
│   ├── jem.yaml
│   ├── researcher.yaml
│   ├── verity.yaml
│   └── pillar.yaml                   # Template for P1-P10
├── meditate/
│   └── lenses.yaml                   # Base lenses (13 universal)
└── macp/
    └── modes.yaml                    # MACP mode definitions
```

---

## §11 Next Steps

1. **Immediate**: Create `src/omega/orchestration/` package structure
2. **Day 1-2**: Implement Redis Streams infrastructure (P0.1)
3. **Day 3-8**: MIAP Phase 0 implementation (P0.2) — 5 fixes
4. **Day 9-10**: Session namespace + CAP_REGISTRY (P0.3, P0.4)
5. **Week 3**: Begin Phase 1 handoff migration

---

*⬡ OMEGA ⬡ P9-LINK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_p9_orchestration ⬡ STRATEGY COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
