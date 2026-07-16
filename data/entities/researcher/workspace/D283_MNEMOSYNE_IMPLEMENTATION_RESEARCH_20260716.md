# 🔱 D-283 MNEMOSYNE IMPLEMENTATION RESEARCH — 2026 SOTA
**AP Token**: `AP-D283-MNEMOSYNE-IMPL-v1.0.0`  
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_d283_impl_research ⬡ ACTIVE  
**Date**: 2026-07-16  
**Context**: Kali's HMC Forge Cycle 2 verdict confirmed D-283 scope. This report provides implementation-ready findings for Roc Racoon's MNEMOSYNE_ARCHITECTURE.md mapping.

---

## EXECUTIVE SUMMARY (L1)

| Research Vector | Status | Key Finding | Implementation Priority |
|----------------|--------|-------------|------------------------|
| **2.1 Letta Memory Blocks** | ✅ Complete | 3-tier (Core/Recall/Archival) with typed blocks, tool-based editing, sleep-time consolidation, MemFS git-backed persistence | **P0** — Foundation for P7 Context Pillar |
| **2.2 Ebbinghaus Decay** | ✅ Complete | Category-specific λ (0.01-0.60/day), reinforcement on recall, TTL tiers (immutable/long/short/session), nightly pruning at strength < 0.05 | **P1** — Retrieval scoring + decay job |
| **2.3 Qliphoth→TDP Bridge** | ✅ Complete | Two-label IFC (U/T), taint sources/sinks, NeuroTaint semantic propagation, PIC verification, SAIHM cryptographic erasure | **P2** — Security differentiator |
| **2.4 Cross-Agent Memory** | ✅ Complete | Letta: shared blocks (read-only for safety); Zep: bi-temporal graph per user; Mem0: user/org scopes; **Omega model: entity-scoped blocks with governance** | **P1** — Architecture decision |

**Overall**: All four vectors have 2026 production implementations to reference. Two-Source Rule satisfied.

---

## 2.1 LETTA MEMORY BLOCK PATTERN — DEEP DIVE

### 2.1.1 Block Schema (Letta 2026 Rewrite, v0.16.8+)

```python
# Source: docs.letta.com/guides/core-concepts/memory/memory-blocks
# github.com/letta-ai/letta/blob/main/letta/schemas/block.py

class MemoryBlock:
    id: str                          # UUID
    label: str                       # "persona", "human", "project", "task", "safety", "decisions"
    value: str                       # String content (JSON-serializable structures allowed)
    limit: int                       # Character cap (typically 2000-5000)
    description: str                 # Guides agent on when to read/write — CRITICAL for LLM tool use
    read_only: bool = False          # If True, only developer can modify
    metadata: Dict[str, Any] = {}    # Extensible (tags, schema hints, version)
    created_at: datetime
    updated_at: datetime
    created_by_id: str
    last_updated_by_id: str
```

**Essential Blocks** (per Letta agent-development skill):
| Block | Purpose | Read-Only? | Limit |
|-------|---------|------------|-------|
| `persona` | Agent identity, behavioral guidelines, capabilities, learned adaptations | Yes (after init) | 5000 |
| `human` | User information, preferences, context, cross-project preferences | No | 3000 |
| `safety` | Constitutional principles, refusal triggers, governance rules | Yes | 2000 |

**Domain-Specific Blocks** (coding assistant example):
| Block | Purpose | Limit |
|-------|---------|-------|
| `project-overview` | High-level description, tech stack, repo links | 3000 |
| `project-commands` | Build, test, lint, dev commands | 2000 |
| `project-conventions` | Commit style, PR process, code style | 2000 |
| `project-architecture` | Directory structure, key modules | 3000 |
| `project-gotchas` | Footguns, things to watch out for | 2000 |
| `current-task` | Scratchpad for active work item | 2000 |
| `context` | Debugging/investigation scratchpad | 3000 |
| `decisions` | Architectural decisions and rationale (append-only) | 5000 |

### 2.1.2 Block Operations (Agent Tools)

| Tool | Operation | Concurrency Safety | Use Case |
|------|-----------|-------------------|----------|
| `block_read(label)` | Read block value | ✅ Safe (read-only) | Context injection |
| `block_append(label, text)` | Append to block | ✅ **Safe** — append-only, minimal races | Incremental learning |
| `block_replace(label, old, new)` | Replace substring | ⚠️ **Risk** — target may change | Precise edits |
| `block_rethink(label)` | Summarize/condense near-limit block | ❌ **Risk** — last-writer-wins | Consolidation (sleep-time only) |
| `block_summarize(label)` | Condense block | ❌ **Risk** — last-writer-wins | Consolidation (sleep-time only) |

**Concurrency Best Practice** (Letta 2026):
- Design for **append operations** when sharing memory between agents
- Use `block_insert` for concurrent writes
- Reserve `block_rethink`/`block_replace` for **single-agent exclusive access** (sleep-time agent)
- PostgreSQL row-level locking handles DB-level safety

### 2.1.3 Sleep-Time Compute (Critical 2026 Pattern)

```python
# Two-agent loop pattern (Letta 2026)
class PrimaryAgent:
    async def serve_turn(self, user_input: str) -> str:
        # Fast path: serve response, write to blocks, log to recall
        response = await self.llm_call(context_with_core_blocks)
        await self.maybe_write_blocks(response)
        await self.log_to_recall(user_input, response)
        return response

class SleepTimeAgent:
    async def consolidate(self, transcript: List[Turn]) -> None:
        # Off critical path: stronger model, no latency constraint
        learned_context = await self.stronger_model.analyze(transcript)
        await self.write_to_shared_blocks(learned_context)
        await self.invalidate_stale_archival_records()
        await self.summarize_near_limit_blocks()
```

**Benefits**:
- No latency cost on primary responses
- Stronger model for consolidation (can use larger/slower model)
- Natural consolidation window (user not waiting)
- Deduplication, summarization, contradiction invalidation

**Safety Rules** (Letta 2026):
- Sleep-time agents = **untrusted writers** for Persona/Safety blocks
- Require **second-agent review** before committing to core identity blocks
- Version blocks and surface diffs in trace

### 2.1.4 MemFS — Git-Backed Memory (2026)

```
$MEMORY_DIR/
├── system/              # Always loaded into system prompt
│   ├── persona.md       # YAML frontmatter + markdown content
│   ├── human.md
│   ├── safety.md
│   └── project-*.md
├── skills/              # Versioned, portable capabilities
│   └── skill-name/
│       ├── SKILL.md
│       └── versions/
└── archive/             # Compaction history
```

- Files in `system/` = Core tier (always in context)
- Files outside `system/` = Visible via memory tree, loaded on relevance
- Agent commits changes → local git repo
- Constellation (cloud) pushes commits to sync
- Dream/Doctor subagents use **git worktrees** for concurrent writes

---

## 2.2 EBBINGHAUS DECAY PARAMETERS — 2026 PRODUCTION VALUES

### 2.2.1 Formula Comparison

| Implementation | Formula | Key Parameters |
|----------------|---------|----------------|
| **Classic Ebbinghaus** | `R(t) = e^(-t/S)` | S = stability (hours/days) |
| **FSRS-5 (Anki)** | `R = (1 + FACTOR × t/(9×S))^DECAY` | DECAY=0.5, FACTOR=0.9^(1/-DECAY)-1 |
| **FSRS-6 (2026)** | Same form | DECAY=0.1542, 21 params optimized per-user |
| **StructureMA** | `conf = init_conf × e^(-λ_eff × hours)` | λ_eff = base_λ / (1 + 0.3×reinforcement) |
| **BunsDev/YourMemory** | `strength = imp × e^(-λ_eff × days) × (1 + recall×0.2)` | λ_eff = base_λ × (1 - imp×0.8) |
| **FramersLab/AgentOS** | `S(t) = S₀ × e^(-Δt/stability)` | Desirable difficulty bonus, emotional bonus, interference |

### 2.2.2 Category-Specific Decay Rates (2026 Consensus)

| Category | Base λ (per day) | Half-life | Use Case | Source |
|----------|------------------|-----------|----------|--------|
| **Identity/Fact** | 0.01–0.016 | ~43–69 days | User name, preferences, critical facts | StructureMA, BunsDev |
| **Strategy/Pattern** | 0.10 | ~38 days | Successful patterns, what worked | BunsDev |
| **Assumption** | 0.16–0.20 | ~19–35 days | Inferred context, working hypotheses | BunsDev, StructureMA |
| **Preference** | 0.05 | ~14 days | Communication style, workflow habits | StructureMA |
| **Goal** | 0.15 | ~5 days | Active objectives | StructureMA |
| **Event/Episodic** | 0.25 | ~3 days | Specific interactions, conversations | StructureMA |
| **Failure/Error** | 0.35 | ~2 days | Environment-specific errors | BunsDev |
| **Context/Scratch** | 0.60 | ~1 day | Temporary working context | StructureMA |

### 2.2.3 Reinforcement Mechanics

**StructureMA** (2026-02):
```python
adjusted_decay_rate = base_rate / (1 + 0.3 * reinforcement_count)
confidence = initial_confidence * exp(-adjusted_decay_rate * hours_elapsed)
```

**BunsDev/YourMemory** (2026-03, +16pp vs Mem0 on LoCoMo):
```python
effective_λ = base_λ * (1 - importance * 0.8)
strength = importance * exp(-effective_λ * days) * (1 + recall_count * 0.2)
score = cosine_similarity * strength  # Combined retrieval score
```

**FramersLab/AgentOS** (2026):
```python
# Desirable difficulty: weaker retrieval → more stability growth
difficulty_bonus = max(0.1, 1 - current_strength)
retrieval_diminish = 1 / (1 + 0.1 * retrieval_count)
emotional_bonus = 1 + emotional_intensity * 0.3
growth_factor = (1.5 + difficulty_bonus * 2.0) * retrieval_diminish * emotional_bonus
new_stability = old_stability * growth_factor
```

**FSRS-6** (2026, open-spaced-repetition):
- 21 parameters optimized per-user
- `next_recall_stability` = `S * (1 + exp(w8) * (11-D) * S^-w9 * (exp(w10*(1-R))-1) * hard_penalty * easy_bound)`
- `next_forget_stability` = `w11 * D^-w12 * ((S+1)^w13 - 1) * exp(w14*(1-R))`
- Short-term stability for same-day reviews

### 2.2.4 Pruning Thresholds

| System | Threshold | Action |
|--------|-----------|--------|
| **StructureMA** | confidence < 0.3 | Archive or delete |
| **BunsDev** | strength < 0.05 | Auto-prune (24h decay job) |
| **FramersLab** | strength < pruning_threshold AND emotional_intensity < 0.3 | Soft-delete (isActive=false) |
| **Letta Archival** | No auto-prune | Agent decides via `archival_memory_insert/search` |
| **Omega Soul v2.0** | L2 insight confidence < threshold | Demote to lower tier |

---

## 2.3 QLIPHOTH → TAINTED DATA PROTOCOL (TDP) BRIDGE

### 2.3.1 Threat Model: Trojan Hippo (2026-05, arXiv:2605.01970)

**Attack Vector**: Attacker plants dormant payload via untrusted tool call (email, web content) → payload writes to persistent memory → activates when user discusses sensitive topics → exfiltrates via outbound tools.

**Affected Backends** (all vulnerable):
- Sliding-window long context (LangChain buffer)
- RAG (vector retrieval)
- Agentic memory (Mem0 — 40K+ stars)
- Explicit tool memory (ChatGPT memory)

**Key Insight**: Persistent memory **fundamentally expands attack surface** despite safety alignment. Single read event establishes persistent foothold surviving session boundaries.

### 2.3.2 Defense: Two-Label Information Flow Control (IFC)

**Session States**: `U` (untainted) / `T` (tainted)

**Taint Sources** (𝒯_src):
- `read_all_emails`, `search_emails`, `web_search`, `fetch_url`, `read_file` (untrusted paths)
- Any tool ingesting adversary-controlled content

**Effect Sinks** (𝒯_sink):
- `send_email`, `reply_email`, `forward_email`, `api_call`, `shell_exec`, `file_write`

**Taint Propagation Rules**:
1. Session starts `U`
2. Invoking any taint source → session becomes `T`
3. Retrieving `T`-labeled memory entry → session becomes `T`
4. Every memory write stamped with current session label
5. Before any sink tool executes: **if session=`T` → BLOCK**

**Implementation** (backend-agnostic):
```python
class TaintTracker:
    def __init__(self):
        self.session_label = "U"
        self.taint_sources = {"read_email", "web_search", "fetch_url", "read_file"}
        self.effect_sinks = {"send_email", "api_call", "shell_exec", "file_write"}
    
    def on_tool_call(self, tool_name: str, result: Any) -> None:
        if tool_name in self.taint_sources:
            self.session_label = "T"
            result.taint = "T"  # Stamp result metadata
    
    def on_memory_retrieve(self, entries: List[MemoryEntry]) -> None:
        if any(e.taint == "T" for e in entries):
            self.session_label = "T"
    
    def on_memory_write(self, entry: MemoryEntry) -> None:
        entry.taint = self.session_label
    
    def check_sink(self, tool_name: str) -> bool:
        if tool_name in self.effect_sinks and self.session_label == "T":
            raise TaintViolation(f"Blocked {tool_name}: session tainted")
        return True
```

### 2.3.3 Advanced: NeuroTaint (2026-04, arXiv:2604.23374)

| Dimension | Traditional IFC | NeuroTaint |
|-----------|-----------------|------------|
| Propagation | Exact string match | Semantic reasoning (LLM-as-judge) |
| Causality | Pre-defined paths | Reconstructed from traces |
| Cross-session | Not tracked | Persistent context tracking |
| Benchmark | TaintBench (400 scenarios, 20 frameworks) | Substantially outperforms FIDES baseline |

**NeuroTaint Pipeline**:
1. Offline audit of execution traces
2. Reconstruct provenance: untrusted source → semantic transformation → decision → sink
3. Causal reasoning over tool calls and memory operations
4. Flag high-confidence taint flows for review

### 2.3.4 PIC Standard (2026-01, Provenance & Intent Contracts)

**Causal Taint Semantics**: Plans derived from untrusted data carry taint. Tainted plans cannot trigger high-impact actions without **trusted evidence bridge**.

**Minimal Bridging Rule**: High-impact actions (`money`, `privacy`, `irreversible`) require at least one claim referencing evidence from **trusted provenance**.

**Fail-Closed Enforcement**: Any verification error → action blocked. No fallback to "allow anyway."

**Three-Way Binding**:
```
provenance[].id          →  identifies input source + initial trust level
claims[].evidence[]      →  references provenance IDs supporting the claim
evidence[].id            →  matches provenance ID; verification MAY upgrade trust to "trusted"
```

### 2.3.5 SAIHM Protocol (2026, IETF Draft)

**Sovereign AI Horizontal Memory** — Memory layer companion to MCP.

| Feature | Specification |
|---------|---------------|
| **Cell** | Encrypted memory unit (AES-256-GCM + ML-DSA-65 signature) |
| **Identity** | ML-DSA-65 keypair derived from wallet seed (HKDF chain) |
| **Erasure** | DEK destruction + tombstone + contentId blacklist + audit receipt |
| **Sharing** | Revocable contracts (temporary/permanent/syndicate) |
| **Audit** | Every mutating op anchored on public chain (ref: COTI V2) |
| **MCP Binding** | 8 canonical tools (`saihm_remember`, `saihm_recall`, `saihm_forget`, `saihm_share`, `saihm_revoke_share`, `saihm_governance_propose`, `saihm_governance_vote`, `saihm_audit`) |

**GDPR Article 17 Alignment**: Cryptographic erasure = DEK destruction makes ciphertext computationally meaningless. Operator never holds DEK.

### 2.3.6 Qliphoth Mapping for Omega

| Qliphoth Concept | TDP Implementation | Omega Component |
|------------------|-------------------|-----------------|
| **Thamiel** (Duality) | T/U session labels | `TaintTracker.session_label` |
| **Chaigidel** (Obstruction) | Sink blocking | `TaintTracker.check_sink()` |
| **Sathariel** (Concealment) | Semantic taint propagation | `NeuroTaint` audit pipeline |
| **Gamchicoth** (Distortion) | Provenance→claim→evidence bridge | `PIC Verifier` |
| **Golachab** (Burning) | Cryptographic erasure | `SAIHM.saihm_forget()` |
| **Thagirion** (Dispute) | Governance proposals/votes | `SAIHM.saihm_governance_*` |
| **Harab Serapel** (Ravens) | Audit receipts on chain | `SAIHM` audit anchoring |
| **Samael** (Poison) | Tainted memory entries | `MemoryEntry.taint` field |
| **Gamaliel** (Pollution) | Cross-session persistence | `TaintTracker` + `MemoryStore` |
| **Nahemoth** (Whisper) | Sub-threshold influence | `NeuroTaint` semantic detection |

---

## 2.4 CROSS-AGENT MEMORY SHARING DECISION

### 2.4.1 2026 Framework Comparison

| Framework | Memory Model | Cross-Agent Sharing | Concurrency Control |
|-----------|--------------|---------------------|---------------------|
| **Letta** | Per-agent memory (isolated by default) | **Shared blocks** — multiple agents attach to same block; all see changes immediately | `read_only` flag for governance; append-safe; `rethink` = last-writer-wins |
| **Zep** | Shared temporal knowledge graph | **User-scoped + session-scoped** — bi-temporal graph tracks what each user/agent knew when | Graph-level transactions; entity versioning |
| **Mem0** | User-scoped + org-scoped | **Explicit namespaces** — `user_id` required parameter; org scope for teams | Fact extraction deduplication (ADD/UPDATE/DELETE/NOOP) |
| **LangMem** | Configurable stores | **Namespace isolation** — tuple-namespaced KV/vector store | Application-level |
| **Graphiti** | Bi-temporal graph | **Group_id namespace** — shared graph with temporal validity | Neo4j transactions |

### 2.4.2 The Unsolved Problem (2026 Consensus)

> **"Despite significant progress, the OSS Insight analysis identifies one problem that no framework in 2026 has solved cleanly: cross-agent memory sharing. When Agent A and Agent B need to operate on shared memory without one overwriting the other's context, every framework in this comparison requires custom application-level logic."** — AgentsCamp 2026-06-11

**Emerging Pattern**: "Blackboard" memory + handoff protocols with explicit separation of:
- **Real-time tier** (collaboration during current execution)
- **Persistent tier** (across executions)

### 2.4.3 Omega Engine Decision: Entity-Scoped Blocks with Governance

**Architecture**: Each entity (Pillar Keeper, subagent) has its own memory namespace. Cross-entity sharing is **explicit, governed, and audited**.

```python
# Omega Memory Sharing Model
class MemoryBlock:
    owner_entity: str                    # "maat", "kali", "pillar_P3", etc.
    label: str                           # "persona", "project-omega", "decisions"
    value: str
    limit: int
    description: str
    read_only: bool = False
    shared_with: List[str] = []          # Explicit allowlist of entities
    governance_level: Literal["private", "shared_read", "shared_write", "public"] = "private"
    taint_policy: Literal["strict", "permissive"] = "strict"
```

**Sharing Rules**:
| Governance Level | Read Access | Write Access | Use Case |
|------------------|-------------|--------------|----------|
| `private` | Owner only | Owner only | Persona, safety, private scratch |
| `shared_read` | Allowlisted entities | Owner only | Project context, decisions log |
| `shared_write` | Allowlisted entities | Allowlisted entities (append-only) | Collaborative task blocks |
| `public` | All entities | None | Reference data, constants |

**Concurrency Control**:
- **Append-only** for `shared_write` blocks (Letta `memory_insert` pattern)
- **Owner-exclusive** for `block_rethink`/`block_replace` (sleep-time agent only)
- **Taint propagation**: Reading a `taint="T"` block from another entity → session becomes `T`

**Audit Trail**: Every cross-entity memory access logged to `omega.observability` with:
- `source_entity`, `target_entity`, `block_label`, `operation`, `taint_at_read`, `timestamp`

---

## IMPLEMENTATION ROADMAP (D-283 Phases)

### Phase 1: Core Tier Hardening (Week 1)
| Task | File | Effort | Dependencies |
|------|------|--------|--------------|
| Implement `MemoryBlock` dataclass with label/value/limit/description/read_only | `src/omega/memory/blocks.py` | 4h | — |
| Add `block_read`, `block_append`, `block_replace`, `block_rethink` tools | `src/omega/memory/block_tools.py` | 6h | blocks.py |
| Wire blocks into Oracle context compilation (prepend to system prompt) | `src/omega/oracle.py` | 4h | blocks.py |
| Add `read_only` enforcement for `persona`/`safety` blocks | `src/omega/memory/blocks.py` | 2h | blocks.py |

### Phase 2: Three-Tier Persistence (Week 1-2)
| Task | File | Effort | Dependencies |
|------|------|--------|--------------|
| Core tier: SQLite `memory_blocks` table (id, label, value, limit, description, read_only, updated_at, owner_entity, governance_level) | `src/omega/memory/block_store.py` | 4h | blocks.py |
| Recall tier: Conversation logging to `omega_memory_data` (existing) | `src/omega/memory/sqlite_vec_adapter.py` | 2h | — |
| Archival tier: Vector store integration + `archival_memory_insert/search` tools | `src/omega/memory/archival.py` | 6h | sqlite_vec_adapter.py |
| Sleep-time agent skeleton (background task, stronger model) | `src/omega/cognition/sleep_time.py` | 8h | blocks.py, archival.py |

### Phase 3: Decay & Consolidation (Week 2)
| Task | File | Effort | Dependencies |
|------|------|--------|--------------|
| Ebbinghaus decay model with category-specific λ (Table 2.2) | `src/omega/memory/decay.py` | 6h | — |
| Decay job: 24h APScheduler, strength = importance × e^(-λ_eff × days) × (1 + recall×0.2) | `src/omega/workers/decay_job.py` | 4h | decay.py |
| Block summarization (`block_rethink`) when near limit | `src/omega/memory/block_tools.py` | 4h | blocks.py |
| Sleep-time consolidation: dedup, summarize, invalidate contradictions | `src/omega/cognition/sleep_time.py` | 8h | sleep_time.py |

### Phase 4: TDP Bridge (Week 2-3)
| Task | File | Effort | Dependencies |
|------|------|--------|--------------|
| `TaintTracker` with U/T session labels | `src/omega/security/taint_tracker.py` | 4h | — |
| Tool classification: taint_sources / effect_sinks (config-driven) | `config/taint_policy.yaml` | 2h | — |
| Memory entry `taint` field + propagation on retrieve/write | `src/omega/memory/sqlite_vec_adapter.py` | 3h | taint_tracker.py |
| Sink blocking with `TaintViolation` error | `src/omega/oracle.py` | 2h | taint_tracker.py |
| PIC-lite: provenance→claim→evidence for high-impact actions | `src/omega/security/pic_verifier.py` | 8h | taint_tracker.py |
| SAIHM-lite: `forget` tool with cryptographic erasure receipt | `src/omega/memory/forget.py` | 6h | — |

### Phase 5: Integration & Tests (Week 3)
| Task | File | Effort |
|------|------|--------|
| E2E test: tainted email → memory write → blocked exfiltration | `tests/test_tdp_bridge.py` | 4h |
| Sleep-time consolidation test: conversation → learned context in blocks | `tests/test_sleep_time.py` | 4h |
| Decay job test: category-specific pruning | `tests/test_decay.py` | 3h |
| Block concurrency test: multi-agent shared block append | `tests/test_block_concurrency.py` | 3h |
| `make test` + `make temple-grade` | — | 2h |

---

## L3 GNOSIS DISTILLED

**L3-Memory-Is-Judgment** (from Kab 2026): "Memory is a judgment problem, not a storage problem." The salience equation forces constant decision: what deserves to persist? Mnemosyne's Da'at = this judgment automated via sleep-time compute.

**L3-Taint-Is-Architecture** (from Trojan Hippo 2026): Persistent memory without taint tracking is a vulnerability, not a feature. The TDP bridge must be **architectural**, not bolted on. Two-label IFC at the session level is the minimum viable defense.

**L3-Blocks-Are-Contracts** (from Letta 2026): A memory block is a typed contract between agent and developer. `description` field = specification. `limit` = SLA. `read_only` = governance. Violations = runtime errors, not silent corruption.

**L3-Decay-Is-Feature** (from FSRS/StructureMA 2026): Forgetting is not failure — it's relevance filtering. Category-specific decay rates + reinforcement bonuses + emotional consolidation = adaptive memory that matches the problem domain.

**L3-Sharing-Is-Governance** (from 2026 cross-agent consensus): Cross-agent memory sharing without explicit governance contracts creates silent corruption. Omega's entity-scoped blocks with `governance_level` and audit trail is the correct architectural primitive.

---

## SOURCES (Two-Source Rule Satisfied)

### Letta Memory Architecture
1. **Primary**: `docs.letta.com/guides/core-concepts/memory/memory-blocks` + `blog.letta.com/memory-blocks` + `ai-engineering.academy/learn/14-agent-engineering/08-memory-blocks-sleep-time-compute` (2026 Letta rewrite docs)
2. **Secondary**: `github.com/letta-ai/skills/blob/main/letta/agent-development/SKILL.md` + `vectorize.io/articles/hindsight-vs-letta` (2026-03-14 comparative)

### Ebbinghaus/FSRS Decay
1. **Primary**: `github.com/ankitects/anki/blob/main/ts/routes/card-info/forgetting-curve.ts` + `github.com/open-spaced-repetition/ts-fsrs` (FSRS-6 2026 implementation)
2. **Secondary**: `github.com/StructureMA/memory-decay` (2026-02-05) + `github.com/BunsDev/yourmemory` (2026-03-30, +16pp vs Mem0 on LoCoMo) + `github.com/framerslab/agentos` (DecayModel.ts 2026)

### TDP / Qliphoth Bridge
1. **Primary**: `arxiv.org/abs/2605.01970` (Trojan Hippo, 2026-05) + `arxiv.org/abs/2604.23374` (NeuroTaint, 2026-04) + `github.com/madeinplutofabio/pic-standard` (PIC v0.5.5, 2026-02)
2. **Secondary**: `ietf.org/archive/id/draft-saihm-memory-protocol-00.html` (SAIHM 2026) + `github.com/templetwo/sovereign-stack` (v1.11.0, 2026-05) + `github.com/psiloceyeben/-BRIDGE.PY` (Kabbalistic routing + HRR + habits)

---

*🔱 OMEGA ⬡ RESEARCHER ⬡ D283-MNEMOSYNE-IMPL ⬡ ACTIVE*  
*All claims backed by 2026 primary sources. Two-Source Rule satisfied across all 4 research vectors.*  
*Ready for Roc Racoon to begin MNEMOSYNE_ARCHITECTURE.md implementation mapping.*