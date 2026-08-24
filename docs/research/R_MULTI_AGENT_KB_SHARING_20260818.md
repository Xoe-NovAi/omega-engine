# Multi-Agent Knowledge Sharing Protocols — Frontier Research

**AP Token**: `AP-MULTI-AGENT-KB-SHARING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_multi_agent_kb_sharing ⬡ ACTIVE

**Date**: 2026-08-18
**Status**: DELIVERABLE — Deep Web Research

---

## Executive Summary (L1)

Production multi-agent systems have converged on **three architectural patterns** for knowledge sharing:

| Pattern | Coordination | Best For | Key Implementation |
|---------|-------------|----------|-------------------|
| **Shared State / Knowledge Bus** | Centralized state object with per-agent namespaces | 2-5 agents, clear role separation | LangGraph `TypedDict` with nested per-agent state + reducers |
| **Hierarchical Delegation** | Supervisor routes to sub-agents; sub-agents can have their own sub-agents | Large teams with sub-domains | Google ADK `sub_agents`, LangGraph `langgraph-supervisor` |
| **Peer-to-Peer (Swarm)** | Direct agent handoffs without central coordinator | Peer agents with equal authority | LangGraph `langgraph-swarm`, AutoGen group chat |

**The frontier insight**: The "knowledge bus" is not a separate layer — it's **structured shared state with explicit ownership boundaries**. The most production-ready systems (LangGraph, Google ADK, Spacebot) treat knowledge as **namespaced, typed, reducible state** that flows through a graph, not a free-form document store.

---

## Dialectic Analysis (L2)

### The Architect (Systemic Logic): Structured State as Knowledge Bus

**Finding**: LangGraph's state schema pattern is the most robust "knowledge bus" implementation in production.

```python
# From teachyou.ai/blog/langgraph-state-schemas (2026-06-16)
class ResearcherState(TypedDict):
    findings: List[str]
    sources_checked: int

class CoderState(TypedDict):
    code_draft: str
    test_results: List[str]

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]  # Shared coordination surface
    task: str
    next_agent: str
    researcher: ResearcherState  # Owned namespace
    coder: CoderState            # Owned namespace
```

**Key principles**:
- **Ownership is explicit**: Each agent owns its nested state slice; only the supervisor touches coordination keys (`messages`, `next_agent`)
- **Reducers only where genuinely shared**: `add_messages` for conversation history; everything else is plain field replacement
- **Subgraph composition requires at least one shared key**: The `messages` key bridges parent and subgraph state

**Production validation**: Markaicode benchmark (2026-03-04) shows LangGraph at **4.2s total latency** for 3-agent pipeline vs CrewAI 7.8s, with native checkpointing and "High" production readiness.

### The Adversary (Critical Rigor): Where Shared State Breaks

**Failure modes documented in production**:

1. **Message pollution** (LangGraph docs): Sub-agents receive irrelevant messages from other agents' conversations. The shared message list grows with every interaction. *Fix: Filter messages per agent or use separate message channels.*

2. **Token budget explosion**: Each sub-agent call includes full conversation history. With 3 agents and 10 routing steps, supervisor processes 10x original message volume. *Fix: Summarize intermediate results, trim tool call messages, shorter context windows for sub-agents.*

3. **Cascading failures**: Research agent returns bad data → code agent writes incorrect code → review agent trusts research. *Fix: Explicit validation gates between agents.*

4. **Namespace collision**: Without explicit ownership, agents overwrite each other's scratch fields. *Fix: TypedDict with nested per-agent state (enforced by schema).*

### The Alchemist (Creative Synthesis): Novel Combinations

**Spacebot's Trace-Learning + Knowledge Bus** (zby/commonplace review, 2026-06-05):
- **Architecture**: Rust agent harness with SQLite graph memory + LanceDB hybrid recall
- **Innovation**: Background "persistence branches" extract typed memories from conversation traces → cortex synthesis generates daily summaries → injected as "pushed working context" into channel prompts
- **Key insight**: **Storage ≠ Activation**. Spacebot separates *writing* memories (trace extraction) from *reading* them (explicit recall tools + ambient push). This solves the "context dilution" problem of naive shared state.

**MemU Organizational Memory** (memu.pro blog, 2026):
- **Problem**: 10 Letta agents = 10 siloed knowledge bases
- **Solution**: Cross-agent memory layer that aggregates insights while preserving provenance (which agent created what, when, under what conditions)
- **Pattern**: **Agent-scoped self-editing memory + organizational memory network**. Each agent keeps autonomy; MemU adds cross-agent deduplication, conflict resolution, and pattern recognition across agent boundaries.

**Augment Cosmos** (augmentcode.com, 2026-06-18):
- **Architecture**: Event bus connects persistent memory to SDLC triggers (Linear tickets, Slack, incidents)
- **Governance**: Access control separates agent authority from user authority; human-gated writes; audit trails
- **Key metric**: "Only ~1/3 of organizations have built governed persistence" — massive greenfield

### The Archivist (Historical Truth): Provenance of Patterns

| System | Year | Contribution | Status |
|--------|------|--------------|--------|
| **AutoGen Group Chat** | 2023 | RetrieveUserProxyAgent for RAG in group chat | Legacy (0.2), migrated to 0.4 |
| **CrewAI Memory** | 2024 | Short-term/long-term/entity memory; `group_id` for shared team memory | Production, but multi-user isolation issues reported |
| **LangGraph State Schemas** | 2024-2025 | TypedDict + reducers + subgraph composition | **Current production standard** |
| **Google ADK Hierarchical** | 2025-2026 | `sub_agents`, `transfer_to_agent`, `escalate`, WorkflowAgents | GA 1.0 (2026-04), 150+ orgs on A2A |
| **Spacebot Trace-Learning** | 2025-2026 | SQLite+LanceDB, background persistence branches, cortex synthesis | Active development (Rust) |
| **MemU Cross-Agent Memory** | 2026 | Organizational memory network atop agent-scoped memory | Early production (Augment, MemU) |

---

## Triangulation: Convergence & Divergence

### Convergence (The Truth)

1. **Explicit ownership > implicit sharing**: Every production system moved from "giant shared dict" to **namespaced, typed state with clear write ownership**
2. **Storage and activation are separate concerns**: Spacebot, Letta, MemU all separate *writing* knowledge from *injecting* it into context
3. **Graph-based orchestration beats free-form chat**: LangGraph, ADK, AutoGen 0.4 all use structured graphs with checkpointing
4. **Provenance is non-negotiable for cross-agent memory**: MemU, Augment, Descope all track *which agent wrote what, when, under what delegation*

### Divergence (The Uncertainty)

| Dimension | Camp A | Camp B | Omega's Position |
|-----------|--------|--------|------------------|
| **Centralized vs Decentralized** | Supervisor/Hierarchical (LangGraph, ADK) | Swarm/Peer-to-Peer (langgraph-swarm, AutoGen) | **Hybrid**: Hierarchical for domain coordination; Swarm for peer handoffs within domain |
| **Memory Scope** | Per-agent (Letta, Mem0) | Shared organizational (MemU, Augment) | **Layered**: Agent-owned core + domain-shared semantic + organizational graph |
| **Knowledge Format** | Vector chunks (RAG) | Typed memories + graph (Spacebot, GraphRAG) | **Hybrid**: Vector for recall, Graph for reasoning, Typed blocks for always-on context |
| **Write Authority** | Agent self-edits (Letta) | Human-gated (Augment, Slite) | **Tiered**: Agent writes to owned namespace; cross-namespace writes require approval |

---

## Sovereign Synthesis: Omega's Knowledge Bus Architecture

### Core Principle: **Namespaced Reducible State Graph**

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR STATE (Coordination)          │
│  messages: Annotated[list, add_messages]                    │
│  active_domain: str                                         │
│  routing_decision: RouteDecision                            │
│  trace_id: str                                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  RESEARCHER   │     │   CODER       │     │   REVIEWER    │
│  STATE        │     │   STATE       │     │   STATE       │
│ (owned ns)    │     │ (owned ns)    │     │ (owned ns)    │
│ findings[]    │     │ code_draft    │     │ issues[]      │
│ sources[]     │     │ test_results  │     │ approvals[]   │
│ kb_queries[]  │     │ kb_refs[]     │     │ kb_refs[]     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              DOMAIN KNOWLEDGE LAYER (Shared, Versioned)     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Vector Index │  │ Knowledge    │  │ Typed Memory │      │
│  │ (Qdrant)     │  │ Graph (KG)   │  │ Blocks       │      │
│  │              │  │ (Neo4j/      │  │ (SQLite/     │      │
│  │ Hybrid:      │  │  Kuzu)       │  │  LanceDB)    │      │
│  │ BM25+Vec+KG  │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  Ownership: Domain Agent (e.g., Researcher owns research KB)│
│  Access: Read=All agents; Write=Owner + Approved delegates  │
└─────────────────────────────────────────────────────────────┘
```

### Protocol: **A2A + MCP + Structured Handoff**

Building on the 2026 standardization (A2A protocol >150 orgs, MCP for tools, ADK for orchestration):

```python
# Handoff packet carries knowledge context explicitly
class KnowledgeHandoff(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    # Knowledge context transferred
    relevant_kb_queries: List[str]           # What KB queries were run
    kb_results_summary: str                  # Key findings
    kb_refs: List[KBRef]                     # Specific KB entries (ids, versions)
    confidence: float                        # How confident in transferred knowledge
    requires_verification: bool              # Should receiver re-verify?
    provenance: ProvenanceChain              # Full delegation chain
```

### Freshness Integration (from Topic 3 Research)

Every KB entry carries:
```python
class KBEntry(BaseModel):
    content: str
    embedding: List[float]
    kg_node_id: Optional[str]
    # Freshness metadata (MANDATORY)
    source_url: Optional[str]
    source_hash: str
    embedded_at: datetime
    embedding_model_version: str
    freshness_tier: Literal["hot", "warm", "cold", "static"]  # half-life class
    last_verified: datetime
    verified_by: str  # agent or human
    decay_half_life_days: float
```

---

## Deliverable: Implementation Checklist for Omega

| Component | Source Pattern | Omega Adaptation |
|-----------|----------------|------------------|
| **State Schema** | LangGraph TypedDict + reducers | Pydantic + custom reducers for AnyIO |
| **Subgraph Composition** | LangGraph compiled subgraphs | Omega Node subgraphs with shared `messages` key |
| **Cross-Agent Memory** | MemU organizational layer | Domain KB + Organizational Graph (separate layers) |
| **Trace Learning** | Spacebot persistence branches | Background distillation workers (Roc Racoon) |
| **Handoff Protocol** | A2A + ADK `transfer_to_agent` | A2A-compliant + KB context transfer |
| **Access Control** | Descope Agentic Identity Hub | Node-owned KB namespaces + RBAC |
| **Freshness** | temporal-rag + tiered reindexing | Per-entry half-life + automated re-verification |
| **Observability** | LangSmith + custom metrics | Omega Hub observability + Hivemind metrics |

---

## Sources (Verified)

1. **LangGraph State Schemas** — teachyou.ai/blog/langgraph-state-schemas (2026-06-16) — *Primary source for state schema patterns*
2. **Production Multi-Agent with LangGraph** — markaicode.com/langgraph-production-agent (2026-03-04) — *Benchmarks, checkpointing, error recovery*
3. **LangGraph Multi-Agent Workflows** — langchain.com/blog/langgraph-multi-agent-workflows (2026-04-17) — *Architecture patterns*
4. **CrewAI Shared Memory** — docs.memmachine.ai/install_guide/integrate/crewai — *group_id pattern*
5. **AutoGen Group Chat RAG** — microsoft.github.io/autogen/0.2/docs/notebooks/agentchat_groupchat_RAG — *RetrieveUserProxyAgent*
6. **Spacebot Review** — zby/commonplace/kb/agent-memory-systems/reviews/spacebot.md (2026-06-05) — *Code-grounded review of Rust harness*
7. **MemU Cross-Agent Memory** — memu.pro/blog/letta-ai-stateful-memory-agent — *Organizational memory network*
8. **Augment Cosmos** — augmentcode.com/guides/cross-agent-organizational-memory (2026-06-18) — *Event bus, governance, failure modes*
9. **A2A Protocol** — a2a-protocol.org, linuxfoundation.org press (2026-04-09) — *150+ orgs, production standard*
10. **Google ADK Hierarchical** — github.com/google/adk-python/discussions/3945, cloud.google.com/blog (2025-11-05) — *sub_agents, transfer_to_agent, WorkflowAgents*

---

## Unverified / Directional Claims (Flagged)

- ⚠️ **MemU production scale**: Claims "100k interactions across 10 agents" — no independent verification found
- ⚠️ **Augment Cosmos deployment**: Described as "platform" but appears to be commercial product; architecture patterns are sound but implementation details proprietary
- ⚠️ **Spacebot maturity**: Active development; reviewed commit from 2026-06-05 but not widely deployed outside spacedriveapp
- ⚠️ **LangGraph Swarm vs Supervisor benchmarks**: "Swarm slightly outperforms supervisor" cited in Anthropic guide but no public benchmark data

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_multi_agent_kb_sharing ⬡ DELIVERABLE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
