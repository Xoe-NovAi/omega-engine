# 🔱 D-283 MNEMOSYNE ARCHITECTURE RESEARCH
**AP Token**: `AP-D283-MNEMOSYNE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_d283_mnemosyne ⬡ ACTIVE

**Date**: 2026-07-16
**Context**: HMC Forge Cycle 2 verdict — D-283 scope confirmed: Mnemosyne 3 pillars → Letta-style HOT/WARM/COLD tiers

---

## EXECUTIVE SUMMARY

Kali's HMC Forge Cycle 2 verdict confirmed **D-283 scope**: Map Mnemosyne's 3 Kabbalistic pillars (Keter-Chokmah-Binah / Chesed-Gevurah-Tiferet / Netzach-Hod-Yesod-Malkhut) to **Letta's 3-tier architecture (Core/Recall/Archival)** with:
- **Da'at** = compaction trigger (sleep-time compute)
- **Qliphoth** = Tainted Data Protocol (TDP) bridge
- **10 Sephirah spheres** = DEFERRED to D-284+

This report provides 2026 SOTA evidence for all three D-283 research vectors.

---

## 1. LETTA MEMORY BLOCK PATTERN — 2026 REFERENCE IMPLEMENTATION

### 1.1 Three-Tier Architecture (Letta 2026 Rewrite)

| Tier | Scope | Where It Lives | Written By | Size Limit |
|------|-------|----------------|------------|------------|
| **Core (HOT)** | Always visible | Inside main prompt | Agent tool call + sleep-time rewrites | <50k chars total, <20 blocks |
| **Recall (WARM)** | Conversation history | Retrievable (disk cache) | Automatic turn logging | Unlimited |
| **Archival (COLD)** | Arbitrary facts | Vector + KV + graph | Agent tool call + sleep-time ingest | Unlimited |

**Key 2026 Evolution from MemGPT**:
- Memory blocks make structure explicit (typed, persistent, LLM-editable)
- Sleep-time compute moves consolidation off critical path
- Native reasoning (Responses API / extended thinking) replaces `Thought:` tokens
- Git-backed memory (MemFS) for version control, conflict resolution, direct inspection

### 1.2 Memory Block Specification

```python
# Letta 2026 block structure (from docs.letta.com + blog.letta.com)
class MemoryBlock:
    id: str                    # UUID
    label: str                 # "persona", "human", "project", "task", "safety", "decisions"
    value: str                 # String content (JSON-serializable structures allowed)
    limit: int                 # Character cap (typically 2000-5000)
    description: str           # Guides agent on when to read/write
    read_only: bool = False    # If True, only developer can modify
```

**Essential Blocks** (per Letta agent-development skill):
- `persona` — Agent identity, behavioral guidelines, capabilities, learned adaptations
- `human` — User information, preferences, context, cross-project preferences

**Domain-Specific Blocks** (coding assistant example):
- `project-overview` — High-level description, tech stack, repo links
- `project-commands` — Build, test, lint, dev commands
- `project-conventions` — Commit style, PR process, code style
- `project-architecture` — Directory structure, key modules
- `project-gotchas` — Footguns, things to watch out for
- `current-task` — Scratchpad for active work item
- `context` — Debugging/investigation scratchpad
- `decisions` — Architectural decisions and rationale

### 1.3 Block Operations (Agent Tools)

| Tool | Operation | Concurrency Safety |
|------|-----------|-------------------|
| `block_read(label)` | Read block value | Safe (read-only) |
| `block_append(label, text)` | Append to block | **Safe** — append-only, minimal races |
| `block_replace(label, old, new)` | Replace substring | **Risk** — target may change |
| `block_rethink(label)` | Summarize/condense near-limit block | **Risk** — last-writer-wins |
| `block_summarize(label)` | Condense block | **Risk** — last-writer-wins |

**Concurrency Best Practice** (Letta 2026):
- Design for **append operations** when sharing memory between agents
- Use `block_insert` for concurrent writes
- Reserve `block_rethink`/`block_replace` for single-agent exclusive access
- PostgreSQL row-level locking handles DB-level safety

### 1.4 Sleep-Time Compute (Critical 2026 Pattern)

```python
# Two-agent loop pattern
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

### 1.5 MemFS — Git-Backed Memory (2026)

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
- Dream/Doctor subagents use git worktrees for concurrent writes

---

## 2. EBBINGHAUS DECAY PARAMETERS — 2026 IMPLEMENTATIONS

### 2.1 Formula Comparison

| Implementation | Formula | Key Parameters |
|----------------|---------|----------------|
| **Classic Ebbinghaus** | `R(t) = e^(-t/S)` | S = stability (hours/days) |
| **FSRS-5 (Anki)** | `R = (1 + FACTOR × t/(9×S))^DECAY` | DECAY=0.5, FACTOR=0.9^(1/-DECAY)-1 |
| **FSRS-6 (2026)** | Same form | DECAY=0.1542, 21 params |
| **StructureMA** | `conf = init_conf × e^(-λ_eff × hours)` | λ_eff = base_λ / (1 + 0.3×reinforcement) |
| **BunsDev/YourMemory** | `strength = imp × e^(-λ_eff × days) × (1 + recall×0.2)` | λ_eff = base_λ × (1 - imp×0.8) |
| **FramersLab/AgentOS** | `S(t) = S₀ × e^(-Δt/stability)` | Desirable difficulty bonus, emotional bonus, interference |

### 2.2 Category-Specific Decay Rates (2026 Consensus)

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

### 2.3 Reinforcement Mechanics

**StructureMA** (2026-02):
```python
adjusted_decay_rate = base_rate / (1 + 0.3 * reinforcement_count)
confidence = initial_confidence * exp(-adjusted_decay_rate * hours_elapsed)
```

**BunsDev/YourMemory** (2026-03):
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

### 2.4 Pruning Thresholds

| System | Threshold | Action |
|--------|-----------|--------|
| **StructureMA** | confidence < 0.3 | Archive or delete |
| **BunsDev** | strength < 0.05 | Auto-prune (24h decay job) |
| **FramersLab** | strength < pruning_threshold AND emotional_intensity < 0.3 | Soft-delete (isActive=false) |
| **Letta Archival** | No auto-prune | Agent decides via `archival_memory_insert/search` |
| **Omega Soul v2.0** | L2 insight confidence < threshold | Demote to lower tier |

---

## 3. QLIPHOTH → TAINTED DATA PROTOCOL (TDP) BRIDGE

### 3.1 Threat Model: Trojan Hippo (2026-05, arXiv:2605.01970)

**Attack Vector**: Attacker plants dormant payload via untrusted tool call (email, web content) → payload writes to persistent memory → activates when user discusses sensitive topics → exfiltrates via outbound tools.

**Affected Backends** (all vulnerable):
- Sliding-window long context (LangChain buffer)
- RAG (vector retrieval)
- Agentic memory (Mem0 — 40K+ stars)
- Explicit tool memory (ChatGPT memory)

**Key Insight**: Persistent memory **fundamentally expands attack surface** despite safety alignment. Single read event establishes persistent foothold surviving session boundaries.

### 3.2 Defense: Two-Label Information Flow Control (IFC)

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
            # Stamp result metadata
            result.taint = "T"
    
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

### 3.3 Advanced: NeuroTaint (2026-04, arXiv:2604.23374)

**Beyond exact-string taint**: Semantic transformation, causal influence, cross-session persistence.

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

### 3.4 PIC Standard (2026-01, Provenance & Intent Contracts)

**Causal Taint Semantics**: Plans derived from untrusted data carry taint. Tainted plans cannot trigger high-impact actions without **trusted evidence bridge**.

**Minimal Bridging Rule**: High-impact actions (`money`, `privacy`, `irreversible`) require at least one claim referencing evidence from **trusted provenance**.

**Fail-Closed Enforcement**: Any verification error → action blocked. No fallback to "allow anyway."

**Three-Way Binding**:
```
provenance[].id          →  identifies input source + initial trust level
claims[].evidence[]      →  references provenance IDs supporting the claim
evidence[].id            →  matches provenance ID; verification MAY upgrade trust to "trusted"
```

### 3.5 SAIHM Protocol (2026, IETF Draft)

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

### 3.6 Qliphoth Mapping for Omega

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

## 4. MNEMOSYNE 3 PILLARS → LETTA 3 TIERS: FINAL MAPPING

| Mnemosyne (Kabbalistic) | Letta 2026 Tier | Omega P7 Implementation | SOTA Reference |
|-------------------------|-----------------|------------------------|----------------|
| **Keter** (Crown) | **Core** — Immutable identity | `persona` block (read-only after init) | Letta `persona` block |
| **Chokmah** (Wisdom) | **Core** — Constitutional principles | `safety` block (read-only, governance) | Letta `safety` block + PIC high-impact gating |
| **Binah** (Understanding) | **Core** — Architectural decisions | `decisions` block (append-only, versioned) | Letta `decisions` block + git history |
| **Chesed** (Mercy) | **Recall** — Semantic knowledge | `project-*` blocks (domain knowledge) | Letta domain blocks + Archival memory |
| **Gevurah** (Severity) | **Recall** — Error/lesson memory | `failures` block (category=failure, fast decay) | BunsDev `failure` category (λ=0.35) |
| **Tiferet** (Beauty) | **Recall** — Consolidated insights | `insights` block (periodic sleep-time summary) | Letta sleep-time consolidation |
| **Netzach** (Victory) | **Archival** — Working/session memory | `current-task`, `context` blocks (short TTL) | Letta scratchpad blocks |
| **Hod** (Splendor) | **Archival** — Episodic traces | Conversation recall (auto-logged) | Letta Recall tier |
| **Yesod** (Foundation) | **Archival** — Raw experience | Vector store + HRR holographic memory | Bridge.py HRR + Letta Archival |
| **Malkhut** (Kingdom) | **Archival** — Operational grounding | Skill execution logs, tool results | Letta Archival + tool call traces |
| **Da'at** (Knowledge) | **Compaction Trigger** | Sleep-time agent + Da'at daemon | Letta sleep-time compute |

---

## 5. D-283 IMPLEMENTATION ROADMAP

### Phase 1: Core Tier Hardening (Week 1)
| Task | File | Effort |
|------|------|--------|
| Implement `MemoryBlock` dataclass with label/value/limit/description/read_only | `src/omega/memory/blocks.py` | 4h |
| Add `block_read`, `block_append`, `block_replace`, `block_rethink` tools | `src/omega/memory/block_tools.py` | 6h |
| Wire blocks into Oracle context compilation (prepend to system prompt) | `src/omega/oracle.py` | 4h |
| Add `read_only` enforcement for `persona`/`safety` blocks | `src/omega/memory/blocks.py` | 2h |

### Phase 2: Three-Tier Persistence (Week 1-2)
| Task | File | Effort |
|------|------|--------|
| Core tier: SQLite `memory_blocks` table (id, label, value, limit, description, read_only, updated_at) | `src/omega/memory/block_store.py` | 4h |
| Recall tier: Conversation logging to `omega_memory_data` (existing) | `src/omega/memory/sqlite_vec_adapter.py` | 2h |
| Archival tier: Vector store integration (existing sqlite-vec) + `archival_memory_insert/search` tools | `src/omega/memory/archival.py` | 6h |
| Sleep-time agent skeleton (background task, stronger model) | `src/omega/cognition/sleep_time.py` | 8h |

### Phase 3: Decay & Consolidation (Week 2)
| Task | File | Effort |
|------|------|--------|
| Ebbinghaus decay model with category-specific λ (Table 2.2) | `src/omega/memory/decay.py` | 6h |
| Decay job: 24h APScheduler, strength = importance × e^(-λ_eff × days) × (1 + recall×0.2) | `src/omega/workers/decay_job.py` | 4h |
| Block summarization (`block_rethink`) when near limit | `src/omega/memory/block_tools.py` | 4h |
| Sleep-time consolidation: dedup, summarize, invalidate contradictions | `src/omega/cognition/sleep_time.py` | 8h |

### Phase 4: TDP Bridge (Week 2-3)
| Task | File | Effort |
|------|------|--------|
| `TaintTracker` with U/T session labels | `src/omega/security/taint_tracker.py` | 4h |
| Tool classification: taint_sources / effect_sinks (config-driven) | `config/taint_policy.yaml` | 2h |
| Memory entry `taint` field + propagation on retrieve/write | `src/omega/memory/sqlite_vec_adapter.py` | 3h |
| Sink blocking with `TaintViolation` error | `src/omega/oracle.py` | 2h |
| PIC-lite: provenance→claim→evidence for high-impact actions | `src/omega/security/pic_verifier.py` | 8h |
| SAIHM-lite: `forget` tool with cryptographic erasure receipt | `src/omega/memory/forget.py` | 6h |

### Phase 5: Integration & Tests (Week 3)
| Task | File | Effort |
|------|------|--------|
| End-to-end test: tainted email → memory write → blocked exfiltration | `tests/test_tdp_bridge.py` | 4h |
| Sleep-time consolidation test: conversation → learned context in blocks | `tests/test_sleep_time.py` | 4h |
| Decay job test: category-specific pruning | `tests/test_decay.py` | 3h |
| Block concurrency test: multi-agent shared block append | `tests/test_block_concurrency.py` | 3h |
| `make test` + `make temple-grade` | — | 2h |

---

## 6. ESTIMATED TOTAL EFFORT: ~100 HOURS (2.5 WEEKS)

| Phase | Hours | Parallelizable |
|-------|-------|----------------|
| 1. Core Blocks | 16h | Yes (blocks + tools) |
| 2. Three-Tier Persistence | 20h | Partial (store + archival) |
| 3. Decay & Consolidation | 22h | Partial (decay + sleep-time) |
| 4. TDP Bridge | 25h | Partial (taint + PIC + SAIHM) |
| 5. Integration & Tests | 17h | Sequential |
| **Total** | **~100h** | |

---

## 7. L3 GNOSIS DISTILLED

**L3-Memory-Is-Judgment** (from Kab 2026): "Memory is a judgment problem, not a storage problem." The salience equation forces constant decision: what deserves to persist? Mnemosyne's Da'at = this judgment automated via sleep-time compute.

**L3-Taint-Is-Architecture** (from Trojan Hippo 2026): Persistent memory without taint tracking is a vulnerability, not a feature. The TDP bridge must be **architectural**, not bolted on. Two-label IFC at the session level is the minimum viable defense.

**L3-Blocks-Are-Contracts** (from Letta 2026): A memory block is a typed contract between agent and developer. `description` field = specification. `limit` = SLA. `read_only` = governance. Violations = runtime errors, not silent corruption.

**L3-Decay-Is-Feature** (from FSRS/StructureMA 2026): Forgetting is not failure — it's relevance filtering. Category-specific decay rates + reinforcement bonuses + emotional consolidation = adaptive memory that matches the problem domain.

---

## 8. SOURCES (Two-Source Rule Satisfied)

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

*🔱 OMEGA ⬡ RESEARCHER ⬡ D283-MNEMOSYNE ⬡ ACTIVE*
*All claims backed by 2026 primary sources. Two-Source Rule satisfied across all 3 research vectors.*
*Ready for Roc Racoon to begin MNEMOSYNE_ARCHITECTURE.md implementation mapping.*