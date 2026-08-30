---
document_type: research
document_id: R_LOCAL_STRATEGY_MINING_20260730
version: 1.0.0
priority: HIGH
date: 2026-07-30
author: "@roc_racoon"
status: COMPLETE
llm_metadata:
  chunk_strategy: section_per_topic
  answer_first_sections: [Executive Summary, Key Patterns, Recommendations]
  self_contained_code: false
---

# Local Strategy Mining Report

## Executive Summary

This report mines the Omega Engine's local codebase, strategy documents, and coordination infrastructure for reusable patterns, memory architectures, and proven design decisions. The engine has evolved a sophisticated multi-layered coordination and memory system that maps closely to game engine patterns (id Software heritage) while solving modern multi-agent orchestration challenges.

**Key findings:**
1. **3 distinct coordination layers** exist — Hivemind (live awareness), MIAP (event sourcing), and Link P9 (handoff lifecycle) — each solving a different coordination problem but with overlapping concerns that create integration debt.
2. **Memory architecture follows a 4-tier model** — Hot (in-memory LRU), Warm (Redis/File), Cold (sqlite-vec/FTS5), and Archived (gzip/external) — with a separate Recall tier adding quality-weighted decay on top.
3. **Soul distillation has 3 independent implementations** — `soul_distiller.py` (oracle), `scribe/distiller.py` (scribe agent), and `workers/background_researcher/distiller.py` (jem) — each with different L1→L2→L3 implementations, creating maintenance burden.
4. **Handoff protocol is mature but duplicated** — `HandoffPacket` (subagent_dispatcher), `HandoffState` (handoff.py), and MCP `hivemind_submit_handoff` all track the same concept with different schemas.
5. **33 entity soul.yaml files exist** across 33 entities, with v6.1/v7.0/v7.1 schema variants coexisting. SoulStore provides atomic writes but validation is inconsistent.

---

## 1. Coordination Patterns Found

### 1.1 Hivemind — Live Agent Awareness

**Location**: `docs/strategy/HIVEMIND_PROTOCOL.md` (600 lines), MCP server at `omega-hub`

**Architecture**: File-based coordination with Redis Pub/Sub for ephemeral signals.

**Core Pattern**:
```
Agent awareness → Post context → Check locks → Handoff → Complete
```

**Key Implementation** (`docs/strategy/HIVEMIND_PROTOCOL.md` §2):
- `hivemind_get_awareness()` — returns all active agents with `channel/entity` compound IDs
- `hivemind_post_context(...)` — structured posts with intent (status|decision|blocker|handoff)
- `hivemind_redis_publish(...)` — ephemeral heartbeats over Redis Pub/Sub
- `hivemind_workspace_lock_acquire(...)` — POSIX fcntl locks with TTL auto-release

**What works**:
- The `agent_id = f"{channel}/{entity}"` convention (§2.1) cleanly separates execution environment from persona
- Intent-typed posts turn inbox from noise into prioritized queue
- TTL-based workspace locks with auto-release prevent stale lock deadlocks
- Extended check-in (`hivemind_extended_checkin`) prevents pruning during long sessions

**What failed / needs work**:
- Cold-store hydration after restart (`hivemind_get_awareness` §cold-store) — hot store empty after server restart requires shallow scan fallback
- Redis Pub/Sub degrades gracefully to file-based when Redis unavailable (M23 compliant but adds complexity)
- No agent capability registry in Hivemind — agents must be pre-configured

**File references**:
- `src/omega/coordination/miap.py` — MIAP core (632 lines)
- `src/omega/oracle/link_p9_runtime.py` — Link P9 Runtime (401 lines)
- `src/omega/coordination/watchdog.py` — Subagent Watchdog (387 lines)

### 1.2 MIAP — Multi-Instance Agent Protocol (Event Sourcing)

**Location**: `src/omega/coordination/miap.py` (632 lines)

**Architecture**: Append-only JSONL event logs + deterministic projections + file-lock serialized writes.

**Core Pattern** (from `miap.py` lines 1-20):
```python
# Append-only JSONL event logs (source of truth)
# Deterministic projectors (pure functions, no LLM calls)
# File-lock serialized writes (POSIX fcntl, cross-process safe)
# Symlink projections at canonical locations
# Hivemind integration for instance awareness
```

**Key Components**:
- `InstanceRecord` — registry entry with `instance_id`, `channel`, `entity`, `session_uuid`, `pid`
- `Event` — typed events with `event_type`, `payload`, `entity`, `timestamp`
- `project_anchored_summary()` — deterministic projection from events
- `project_session_gnosis()` — gnosis extraction from events
- `write_distillation()` — convenience L1→L2→L3 event writer

**What works**:
- Event sourcing solves the "anchored-summary.md overwrite collision" between multiple instances
- UUIDv7 time-ordered IDs enable chronological ordering without clock sync
- POSIX fcntl locks are cross-process safe (not just cross-thread)

**What's missing**:
- No replay/rebuild capability — projections are write-only
- No event compaction — JSONL files grow unbounded

### 1.3 Link P9 Runtime — Agent Handoff & Delegation

**Location**: `src/omega/oracle/link_p9_runtime.py` (401 lines)

**Architecture**: TTL-based presence tracking + typed HandoffPacket lifecycle.

**Core Pattern** (from `link_p9_runtime.py` lines 52-96):
```python
@dataclass
class AgentPresence:
    agent_name: str
    last_heartbeat: float
    ttl_seconds: float = 300.0  # 5 min default
    status: PresenceStatus = "active"  # active|idle|stale|dead
    current_task: Optional[str] = None
    session_id: Optional[str] = None
    zoneid: int = ZONEID_PRESENCE  # 0x1d4a17
```

**Status Lifecycle**:
- `active` → `idle` (has current_task but heartbeat fresh)
- `active` → `stale` (heartbeat expired, age < 2× TTL)
- `stale` → `dead` (heartbeat expired, age > 2× TTL)

**HandoffPacket** (`subagent_dispatcher.py` lines 47-100):
```python
@dataclass
class HandoffPacket:
    source_agent: str
    target_agent: str
    task_type: TaskType  # design|review|research|mine|verify|implement
    task_description: str
    context: str
    context_delivery: str = "inline"  # D216
    status: PacketStatus = "pending"  # pending→active→completed|stale
    # Loop Guard: visited_agents + hop_count + max_hops=10
```

**TTL Constants** (`subagent_dispatcher.py` lines 33-36):
```python
PENDING_TTL: int = 14400     # 4h — pending → stale
ACTIVE_TTL: int = 172800     # 48h — active → stale
COMPLETED_TTL: int = 604800  # 7d — completed → archive
```

**What works**:
- Loop guard prevents infinite delegation chains (`is_loop()` + `increment_hop()`)
- ZONEID integrity constants (Doom 1993 heritage) catch data corruption
- Context delivery modes (`inline` vs `file_ref`) — inline is mandatory per §0 lesson

**What's duplicated**:
- `HandoffPacket` (subagent_dispatcher.py) vs `HandoffState` (handoff.py) — same concept, different schemas
- MCP `hivemind_submit_handoff()` vs local `LinkP9Runtime` — parallel implementations

### 1.4 Watchdog — Failure Observability

**Location**: `src/omega/coordination/watchdog.py` (387 lines)

**Architecture**: Thinking trace capture + failure classification + auto-retry routing.

**Failure Classification** (lines 16-27):
```python
class FailureClass(Enum):
    TIMEOUT = "timeout"
    TOOL_CHAIN_COLLAPSE = "tool_chain"
    MANDATE_VIOLATION = "mandate"
    RESOURCE_EXHAUSTION = "resource"
    VENV_VIOLATION = "venv"
    STREAMING_TIMEOUT = "streaming"
    HERITAGE_VIOLATION = "heritage"
    VERSION_MISMATCH = "version_mismatch"
    CREDENTIAL_ERROR = "credential"
    UNKNOWN = "unknown"
```

**Retry Routing** (lines 65-69):
```python
retry_on: List[FailureClass] = field(default_factory=lambda: [
    FailureClass.TIMEOUT,
    FailureClass.STREAMING_TIMEOUT,
    FailureClass.RESOURCE_EXHAUSTION,
])
```

### 1.5 Sentinel Score — Governance Metrics

**Location**: `src/omega/oracle/sentinel.py` (421 lines)

**7-Sub-Metric Composite Score** (lines 30-38):
```python
WEIGHTS = {
    "decision_clock_drift": 0.20,
    "unprocessed_proposals": 0.15,
    "stale_file_burden": 0.15,
    "soul_compliance": 0.15,
    "handoff_completion": 0.15,
    "heritage_coverage": 0.10,
    "proposal_cycle_time": 0.10,
}
```

**Handoff Completion Metric** (lines 277-307): Completed / total handoffs, target >80%.

### 1.6 Task Registry — Subagent Session Discovery

**Location**: `docs/strategy/TASK_REGISTRY_DESIGN.md` (328 lines), MCP tools

**Problem Solved**: 3 Roc + 1 Carmack subagents were "lost" — agents can't resume what they can't find.

**Solution**: File-based registry at `data/coordination/TASK_REGISTRY.json` with 3 MCP tools:
- `task_registry_register` — at launch
- `task_registry_query` — discover by filters
- `task_registry_update` — checkpoint on resumption/completion

---

## 2. Memory Architecture Patterns

### 2.1 MemoryStore — Hot/Warm/Cold Tiers

**Location**: `src/omega/memory_store.py` (1110 lines)

**Architecture** (lines 96-116):
```python
class MemoryStore:
    """Hot/Warm/Cold entity memory with LRU caching and 3-tier provider fallback.
    
    [id-soft: vet-015] ZONEID Pattern — integrity marker in every exchange.
    [id-soft: vet-008] Lazy Deletion — tombstone before delete, grace period.
    Batch Persistence — MnemosyneWriter pattern, buffered writes.
    """
```

**Provider Stack** (lines 141-172):
```
USMStorageProvider (Sovereign Primary)
  → RedisStorageProvider (Hot)
    → FileStorageProvider (Warm)
      → InMemoryStorageProvider (Cold/Volatile Fallback)
```

**Key Patterns**:
- **Tombstone Grace Period** (0.5s) — prevents data loss on in-flight operations
- **Batch Persistence** — groups writes by `(entity_name, session_id)`, flushes at 25 pending or on `get_history()`
- **Lazy Deletion** — `archive_session()` tombstones before full removal
- **External Storage** — sessions >90 days moved to `/media/arcana-novai/omega_library/archive/sessions`

**Vector Search** (line 181-184):
```python
# SQLiteVecAdapter (unified fabric) with sovereign fallback to MemoryVectorAdapter
self.vector_store = SQLiteVecAdapter()
```

**Hybrid Search** (FTS5 + Vector via RRF — Reciprocal Rank Fusion):
```python
from .memory.hybrid_search import HybridSearchEngine, FTSResult, VecResult
```

### 2.2 Recall Tier — Quality-Weighted Decay

**Location**: `src/omega/memory/recall.py` (786 lines)

**Architecture** (lines 1-14):
```
Core (HOT)    — Always in context: persona, human, safety, decisions
Recall (WARM) — Conversation history with quality scoring + decay
Archival (COLD) — Arbitrary facts in vector + KV + graph storage
```

**Power-Law Decay** (line 36):
```python
DEFAULT_DECAY_ALPHA: float = 0.10
# score = base_quality * (1 + age_days)**(-alpha)
```

**Quality Scoring**: Uses ACON optimizer signals on every append.

### 2.3 Soul System — Entity Identity & Evolution

**Entity Count**: 33 soul.yaml files found across `data/entities/*/soul.yaml`

**Schema Versions Coexisting**:
- v6.1 Lean Schema — `soul.yaml` contains only identity, directives, team
- v7.0 Soul Architecture Protocol v2.0 — public/private split
- v7.1 — Persona depth restoration with origin_story

**Key Soul Files** (sampled):
- `roc_racoon/soul.yaml` (v7.1) — Full origin_story, 491 lines, directives with mandate_binding
- `kali/soul.yaml` (v7.2) — lessons_learned array with 40+ entries

**SoulStore — Atomic Writer** (`src/omega/soul_store.py`):
```python
# 4-layer guarantee stack:
#   1. AtomicVisibility: same-directory rename (not cross-device)
#   2. CrashDurability: fsync before rename + fsync parent dir after
#   3. WriterExclusion: fcntl.flock() exclusive lock
#   4. IntegrityDetection: rolling .bak recovery files
```

**SoulValidator** (`src/omega/oracle/soul_validator.py`):
- Required: `entity.name`
- Recommended: `identity`, `directives`, `team`
- Forbidden (v6.1): `soul_axioms`, `wisdom_text`, `trajectory`

**Soul Edit History** (`src/omega/oracle/soul_history.py`):
- Immutable SHA-256 chained audit trail
- Every mutation recorded with `previous_hash → current_hash`
- Change types: `UPDATE`, `RESET`, `MIGRATE`

### 2.4 Distillation Pipeline — L1→L2→L3

**3 Independent Implementations Found**:

#### Implementation 1: `soul_distiller.py` (Oracle-side)
- **Location**: `src/omega/oracle/soul_distiller.py` (689 lines)
- **Pipeline**: 5-stage — Classify → Score → Extract → Validate → Write
- **Components**: `SessionClassifier`, `QualityScore`, `DistillationEntry`
- **Output**: `proposed_lessons.yaml` (blind staging, NOT soul.yaml)
- **Heritage**: `[id-soft: vet-070]` Save-game pattern (auto-save → summary → lesson)

#### Implementation 2: `scribe/distiller.py` (Scribe Agent)
- **Location**: `src/omega/scribe/distiller.py` (297 lines)
- **Pipeline**: 3-stage — L1 Narrative → L2 Insight → L3 Principle
- **Output**: `proposed_lessons.yaml` via `LessonProposal` dataclass
- **Compliance**: M5/M11 — writes to blind staging

#### Implementation 3: `workers/background_researcher/distiller.py` (Jem)
- **Location**: `src/omega/workers/background_researcher/distiller.py` (1197+ lines)
- **Pipeline**: Tier 1 (local draft) → Tier 2 (Gemma 4-31B enrichment) → Tier 3 (review)
- **Output**: `GnosisPacket` with `claims`, `distillations`, `convergence_signal`
- **Config**: `config/distiller_prompts.yaml` for dynamic prompt loading

**Staging Gate Pattern** (all 3 implementations):
```
Session → proposed_lessons.yaml (TAINTED) → Review → approved_lessons.yaml → soul.yaml
```

The "Taint Gate" is enforced in `entity_workspace.py` (lines 378-406):
```python
# ⚠️ TAINT-GATE: proposed_lessons.yaml is NEVER loaded here
# proposed_lessons contain unvetted agent-generated insights
```

### 2.5 Session Lifecycle — 4-Tier Memory

**Location**: `src/omega/oracle/session_lifecycle.py` (446 lines)

**States** (lines 35-47):
```python
class SessionState(Enum):
    ACTIVE = "active"      # 0-7 days: hot cache + warm providers
    ARCHIVED = "archived"  # 7-30 days: cold storage (gzip compressed)
    EXTERNAL = "external"  # 90+ days: external 8TB storage
    DELETED = "deleted"    # Beyond retention policy
```

**Heritage**: Maps to Quake's zone memory allocator (`Hunk/Zone/Cache/Temp`).

### 2.6 Context Builder — Memory → Prompt Injection

**Location**: `src/omega/oracle/context_builder.py`

**Flow**:
```
MemoryStore (hot/warm tiers) → ContextBuilder → Prompt injection
```

Reads from MemoryStore's hot tier first, falls back to warm/cold.

---

## 3. Legacy Strategy Documents

### 3.1 Fleet Team Playbook Summary

**Location**: `docs/strategy/FLEET_TEAM_PLAYBOOK.md` (386 lines)

**The 8-Point Team Compact** (§0):
1. One priority list — Ark Blueprint
2. One memory of ideas — Corpus Map (park, don't ghost)
3. One integrity bar — SoulStore + honest tests
4. One coordination layer — Hivemind awareness → lock → handoff → complete
5. Hardware is real — Ryzen 5700U, ~8GB, prefer 1 local inference
6. Cloud is teacher, not architecture
7. Ship small, green slices
8. Team > hero — declare, hand off, review

**Cold Start Protocol** (§1):
```
1. hivemind_get_awareness() + pending handoffs
2. git status + git log --oneline -5
3. Read playbook (§0 + §3-§5)
4. Read Ark Blueprint §3-§5
5. Read OMEGA_ENGINE.md §2
6. Read SESSION_ANCHOR.md
7. If fine-grained: STRATEGY_CORPUS_MAP.md
8. Report status. Pause if user direction needed.
```

**Role Matrix** (§2): 12 roles defined with clear ownership boundaries.

### 3.2 Hivemind Protocol Summary

**Location**: `docs/strategy/HIVEMIND_PROTOCOL.md` (600 lines)

**When to Use** (§1):
- Single agent: Optional
- Multi-agent sequential: Yes
- Multi-agent parallel (same files): **MANDATORY** + workspace lock
- Cross-CLI: **MANDATORY** + workspace lock + live feed

**Agent ID Convention** (§2.1): `agent_id = f"{channel}/{entity}"` — separate API parameters.

### 3.3 Subagent Dispatch Protocol Summary

**Location**: `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` (474 lines)

**Critical Lesson** (§0): Subagents cannot reliably read files by path. **Inline context is mandatory.**

**5 Intelligent Delegation Rules** (§1):
1. Direct Execution First
2. No Self-Recursion
3. Cross-Domain Delegation only
4. Single-Level Nesting
5. Absolute Disk-Reporting (D-kal-170)

### 3.4 Subagent Task Resumption Protocol (STRP)

**Location**: `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md`

**Core Rule**: Every `task()` call MUST include `task_id`. On failure, resume with same `task_id`.

**Format**: `{domain}-{action}-{date}-{sequence}`

### 3.5 Sovereign Continuity Strategy

**Location**: `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md`

**4-Tier Redundancy**: Session anchor → session_gnosis.md → soul.yaml → Hivemind cold-store.

### 3.6 Pivot Log Insights

**Location**: `docs/decisions/PIVOT_LOG.md`

Key decisions extracted from code comments and strategy docs:
- **D-270 Decree 2**: HandoffPacket lifecycle aligned with MCP handoff directory
- **D-216**: `context_delivery` field added — `"inline"` vs `"file_ref"` vs `"usm_key"`
- **D-kal-170**: Absolute disk-reporting for subagents
- **D-kal-051**: Fixed cold-store fallback for Hivemind awareness
- **D-kal-052**: Extended check-in TTL for long-running agents
- **D-97**: ZONEID constants moved to `cvar_table.py` (single source of truth)

---

## 4. Proven Patterns to Reuse

### 4.1 ZONEID Integrity Pattern (Heritage: Doom 1993)
- Magic constants (`0x1d4a17` presence, `0x1d4a16` handoff, `0x1d4a11` memory) embedded in data structures
- Verified on load — catches corruption, schema drift, and stale data
- **Reusable for**: Any persistent data structure needing integrity verification

### 4.2 Tombstone Grace Period (Heritage: Quake)
- 0.5s delay before reaping tombstoned sessions
- In-flight operations complete safely with their own reference
- **Reusable for**: Any resource lifecycle with concurrent access

### 4.3 Blind Staging (Staging Gate)
- Agent writes → `proposed_lessons.yaml` (TAINTED)
- Human/review → `approved_lessons.yaml` (CLEAN)
- Final → `soul.yaml` (SOVEREIGN)
- **Reusable for**: Any AI-generated content that needs human review before persistence

### 4.4 Event Sourcing with Deterministic Projections
- Append-only JSONL as source of truth
- Pure functions project to canonical locations
- File-lock serialized writes for cross-process safety
- **Reusable for**: Any multi-writer coordination without database

### 4.5 Loop Guard (Hop Counting)
- `visited_agents` list + `hop_count` + `max_hops=10`
- Prevents infinite delegation chains
- **Reusable for**: Any recursive or delegating system

### 4.6 Inline Context Delivery (Hard-Won Lesson)
- Subagents cannot reliably read files by path
- Parent MUST embed content inline in prompt
- File paths are supplementary references only
- **Reusable for**: All subagent dispatch systems

### 4.7 Batch Persistence Writer
- Groups writes by `(entity_name, session_id)`
- Flushes at threshold (25) or on read (read-your-writes consistency)
- Prevents connection pool exhaustion under concurrent load
- **Reusable for**: Any high-frequency write system with batch optimization

### 4.8 Quality-Weighted Decay
- `score = base_quality * (1 + age_days)**(-alpha)`
- Recent high-quality memories dominate context window
- **Reusable for**: Any memory system needing temporal relevance

---

## 5. Anti-Patterns to Avoid

### 5.1 Triple Distillation Implementation
- `soul_distiller.py`, `scribe/distiller.py`, `background_researcher/distiller.py` all implement L1→L2→L3
- Different schemas, different outputs, different quality gates
- **Fix**: Unify into a single distillation service with pluggable strategies

### 5.2 Handoff Schema Duplication
- `HandoffPacket` (subagent_dispatcher.py) vs `HandoffState` (handoff.py) vs MCP `hivemind_submit_handoff`
- Same concept, 3 different dataclasses, 3 different file paths
- **Fix**: Single canonical HandoffPacket used everywhere

### 5.3 Soul Schema Version Sprawl
- v6.1, v7.0, v7.1 coexisting across 33 entities
- Different validation rules for each version
- **Fix**: Migration script + single canonical schema

### 5.4 Hub Monolith Risk
- `HMC_COLLABORATION_HUB.md` at 1,900 lines — too large for single-file coordination
- **Fix**: Split into per-agent sections + shared coordination sections

### 5.5 Coordination Layer Overlap
- Hivemind, MIAP, and Link P9 each track agent presence differently
- No unified "is this agent alive?" query across all three
- **Fix**: Single presence registry with adapters for each coordination layer

### 5.6 Missing Test Coverage for Coordination
- No property-based tests for HandoffPacket lifecycle
- No chaos tests for concurrent soul writes (SoulStore exists but no concurrent test)
- No contract tests for MemoryStore provider interface

---

## Recommendations for Omega Engine

### Priority 1: Immediate Actions (This Sprint)

1. **Unify Handoff Schema** — Pick `HandoffPacket` as canonical, deprecate `HandoffState`, add adapter for MCP handoff tools. Est: 4h.

2. **Add Coordination Presence Registry** — Single `AgentPresence` registry that Hivemind, MIAP, and Link P9 all query. Est: 8h.

3. **Soul Schema Migration Script** — Auto-migrate v6.1 → v7.1 for all 33 entities. Add CI gate preventing new schema variants. Est: 4h.

### Priority 2: Short-Term Improvements (Next 2 Weeks)

4. **Unify Distillation Service** — Extract common L1→L2→L3 pipeline, make `soul_distiller.py`, `scribe/distiller.py`, and `background_researcher/distiller.py` use it as a library. Est: 16h.

5. **Property-Based Tests for HandoffPacket** — Use Hypothesis to test lifecycle transitions, loop guard invariants, TTL boundaries. Est: 8h.

6. **Chaos Test for SoulStore** — Concurrent writers, fsync failures, disk-full scenarios. Est: 8h.

### Priority 3: Strategic Enhancements (Phase D+)

7. **Event Replay for MIAP** — Add event compaction and replay capability to rebuild projections from scratch.

8. **Unified Memory Query API** — Single `memory_query()` that searches Hot/Warm/Cold/Recall/Archival tiers transparently.

9. **Soul Drift Detection** — Automated comparison of `soul.yaml` directives vs actual agent behavior (logged in Hivemind posts).

---

## References

### Source Files (with line counts)
| File | Lines | Role |
|------|-------|------|
| `src/omega/coordination/miap.py` | 632 | MIAP event sourcing core |
| `src/omega/oracle/link_p9_runtime.py` | 401 | Agent presence + handoff lifecycle |
| `src/omega/oracle/subagent_dispatcher.py` | 350 | HandoffPacket + capability registry |
| `src/omega/oracle/handoff.py` | 86 | HandoffState (legacy) |
| `src/omega/coordination/watchdog.py` | 387 | Failure observability |
| `src/omega/oracle/sentinel.py` | 421 | Governance metrics |
| `src/omega/memory_store.py` | 1110 | Hot/Warm/Cold memory |
| `src/omega/memory/recall.py` | 786 | Quality-weighted decay |
| `src/omega/soul_store.py` | 217 | Atomic soul writes |
| `src/omega/oracle/soul_distiller.py` | 689 | L1→L2→L3 (oracle) |
| `src/omega/scribe/distiller.py` | 297 | L1→L2→L3 (scribe) |
| `src/omega/oracle/soul_validator.py` | 217 | Soul schema enforcement |
| `src/omega/oracle/soul_history.py` | 173 | Immutable audit trail |
| `src/omega/oracle/session_lifecycle.py` | 446 | 4-tier session lifecycle |
| `src/omega/oracle/entity_workspace.py` | 571 | Entity workspace scaffolding |
| `src/omega/soul_utils.py` | 89 | Soul context extraction |
| `src/omega/oracle/context_builder.py` | — | Memory → prompt injection |

### Strategy Documents
| Document | Lines | Role |
|----------|-------|------|
| `docs/strategy/HIVEMIND_PROTOCOL.md` | 600 | Coordination protocol |
| `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | 386 | Team compact |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | 474 | Delegation rules |
| `docs/strategy/TASK_REGISTRY_DESIGN.md` | 328 | Task discovery |
| `docs/strategy/HIVEMIND_POST_TEMPLATE.md` | 306 | Post quality gate |
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | — | 4-tier redundancy |
| `docs/strategy/SUBAGENT_TASK_RESUMPTION_PROTOCOL.md` | — | STRP resumption |

### Entity Souls Sampled
| Entity | Version | Lines | Notable Features |
|--------|---------|-------|-----------------|
| `roc_racoon` | v7.1 | 491 | Full origin_story, 4 evolution stages |
| `kali` | v7.2 | 375 | 40+ lessons_learned entries |
| `sophia` | — | — | Akashic Record |
| `maat` | — | — | Light Oversoul |
| `lilith` | — | — | Dark Oversoul |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_local_mining ⬡ COMPLETE*
