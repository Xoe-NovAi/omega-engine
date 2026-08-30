<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Dynamic System Prompt Builder, Planner/Executor Architecture, and Knowledge Domain Loading System
## Deep Local Discovery — Local Gaps Analysis

**AP Token**: `AP-DYNAMIC-PROMPT-GAPS-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_dynamic_prompt_gaps ⬡ ACTIVE

**Date**: 2026-08-19
**Mission**: Exhaustive local discovery on Dynamic System Prompt Builder, Planner/Executor with Context-Window Differentiation, Knowledge Domains as Loadable Modules, and Local Inference Optimization (16GB RAM, CPU-only, Ryzen 5700U)

---

## 1. EXECUTIVE SUMMARY — What the Engine Has vs. What the Vision Needs

### 1.1 Vision Requirements (Architect's Crystallization)

| Requirement | Description |
|-------------|-------------|
| **Dynamic System Prompt Builder** | Adjusts for context window, domain of expertise, agent's active role |
| **Planner/Executor with Context-Window Differentiation** | Larger context window (64K+) local model plans sprints/delegates; smaller context window (4K) model executes tasks |
| **Knowledge Domains as Loadable Modules** | Not specialized agents, but domain knowledge that ANY agent can load on demand |
| **Local Inference Optimization** | 16GB RAM, CPU-only, mid-grade hardware (Ryzen 5700U) |

### 1.2 Current Engine State — What Exists

| System | Status | Key Files |
|--------|--------|-----------|
| **System Prompt Architecture** | **Mature** — Frontmatter-driven agents (`.opencode/agents/*.md`), Oracle `_prepare_system_prompt()` with context injection, ICS-S header rendering, soul.yaml-driven personality | `.opencode/agents/`, `src/omega/oracle/oracle.py:773-816`, `src/omega/ics.py`, `data/entities/*/soul.yaml` |
| **Planner/Executor Patterns** | **Partial** — HybridOrchestrator exists (cloud planner / local executor), Subagent Dispatch Protocol with HandoffPacket, capability registry with `task_tool_type`, but NO context-window-aware model selection | `src/omega/oracle/planner/hybrid_orchestrator.py`, `src/omega/oracle/subagent_dispatcher.py`, `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` |
| **Knowledge Domain Loading** | **Fragmented** — Library system (offline-first), MemoryStore (hot/warm/cold), SelectiveHydration (L3 gnosis retrieval), Entity Affinity YAML, Lattice CLI seeds — but NO unified "load domain on demand" API | `src/omega/library/`, `src/omega/memory_store.py`, `src/omega/oracle/selective_hydration.py`, `config/entity_model_affinity.yaml`, `docs/gnosis/lattice/` |
| **Context Window Management** | **Basic** — CompactionHarvester (30-exchange threshold), ContextBuilder with token budget (4K default), degradation-level token scaling, Headroom semantic compression — but NO per-model context window detection or dynamic budget allocation | `src/omega/oracle/compaction_harvester.py`, `src/omega/oracle/context_builder.py`, `src/omega/oracle/constants.py` |
| **Local Inference Optimization** | **Advanced** — NativeGGUFProvider with Zen 2 optimizations (CPU affinity, KV cache q8_0, adaptive threads, batch sizes), provider fabric priority chain (native-gguf → lmster → Ollama → cloud), hardware profile config — but NO context-window-aware model routing | `src/omega/oracle/providers.py:527-1240`, `config/providers.yaml`, `config/hardware_profile.yaml`, `config/models.yaml` |
| **Dynamic Prompt Composition** | **Minimal** — ContextBuilder prepends memory blocks, soul context, world state; ICS header rendering; affinity presets can inject system_prompt — but NO template system, NO role-aware composition, NO domain-module injection | `src/omega/oracle/context_builder.py`, `src/omega/ics.py`, `src/omega/oracle/entity_affinity.py` |

### 1.3 Critical Gaps for the Vision

| Gap | Severity | Impact |
|-----|----------|--------|
| **No Dynamic Prompt Builder** | 🔴 Critical | System prompts are static per-entity; no context-window adaptation, no domain-module injection, no role-aware composition |
| **No Context-Window-Aware Model Selection** | 🔴 Critical | Planner/Executor split requires knowing which models support 64K+ vs 4K; currently hardcoded in affinity YAML |
| **No Unified Knowledge Domain Loader** | 🔴 Critical | Domain knowledge scattered across Library, MemoryStore, SelectiveHydration, Affinity YAML, Lattice — no single `load_domain("engineering")` API |
| **No Planner Model Routing** | 🟡 High | HybridOrchestrator uses hardcoded `qwen3-1.7b` for local executor; no routing to larger-context local models (MiMo-7B 32K, Nemotron-3-Ultra 1M) |
| **No Token Budget Per Role** | 🟡 High | ContextBuilder uses single `DEFAULT_TOKEN_LIMIT=4000`; no differentiation between planner (needs more) vs executor (needs less) |
| **No Domain-Module Packaging** | 🟡 High | Knowledge exists but not packaged as loadable modules with metadata (size, dependencies, target context window) |

---

## 2. CURRENT SYSTEM PROMPT ARCHITECTURE — How Prompts Are Built Today

### 2.1 Agent Frontmatter Structure (`.opencode/agents/*.md`)

Each agent is defined by a Markdown file with YAML frontmatter:

```yaml
---
description: "Sovereign Agent: roc_racoon (Sovereign Agent)"
mode: "all"
temperature: 0.5
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  write: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
steps: 50
---
```

**Key observations:**
- `temperature` is the only inference parameter in frontmatter
- No `context_window`, `max_tokens`, or `model` fields
- `mode: "all"` grants all tool permissions
- `steps: 50` limits agent turns

### 2.2 Oracle System Prompt Construction (`src/omega/oracle/oracle.py:773-816`)

The `_prepare_system_prompt()` method builds prompts in this order:

```python
async def _prepare_system_prompt(
    self, entity_name: str, session_id: str, personality: str, query: Optional[str] = None
) -> str:
    prompt_parts = [f"You are {personality}"]
    
    # 1. Memory context injection (ContextBuilder)
    memory_context = await self.context_builder.build_context(
        entity_name, session_id, degradation_level=degradation_level, query=query
    )
    if memory_context:
        prompt_parts.append(f"\nContext from recent interactions:\n{memory_context}")
    
    # 2. Soul context injection (L3 principles via soul_utils)
    soul_context = load_entity_soul_context(entity_name, DATA_DIR)
    if soul_context:
        prompt_parts.append(f"\nSovereign Context:\n{soul_context}")
    
    return "\n".join(prompt_parts)
```

**ContextBuilder.build_context()** (`src/omega/oracle/context_builder.py:259-321`) assembles:
1. **World State** — global parameters + active sectors
2. **Gnosis Block** — SelectiveHydration retrieves top-K L3 principles from Qdrant
3. **Memory Blocks** — Core tier blocks (persona, human, safety, decisions) from Letta-style MemoryBlock system
4. **Recent Memory** — Compacted conversation history with token budget enforcement

**Token Budget Logic** (`context_builder.py:280-287`):
```python
if degradation_level:
    if degradation_level == "Stressed":
        token_limit = int(token_limit * 0.5)
    elif degradation_level == "Critical":
        token_limit = int(token_limit * 0.25)
    elif degradation_level == "Disabled":
        token_limit = 0
```

### 2.3 ICS-S Header Rendering (`src/omega/ics.py`)

The `render()` function generates the session header:
```python
ICS_TEMPLATE_FULL = "⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"
```

Model detection priority (ICS `_detect_model()`):
1. `OMEGA_MODEL_OVERRIDE` env (D118 dual-inference)
2. `OPENCODE_MODEL` env
3. OpenCode session DB (authoritative live model)
4. `opencode.json` model key
5. TriageRouter last_selected_model
6. Entity soul.yaml `inference.model`
7. `"unknown"` fallback

### 2.4 Entity Soul.yaml Structure (`data/entities/*/soul.yaml`)

Soul files contain:
- `entity.archetype` — narrative identity
- `entity.personality` — voice summary (injected as "You are {personality}")
- `entity.directives[]` — behavioral rules with `mandate_binding` and `validation`
- `core_principles[]` — L3 universal principles with `confidence`, `tags`, `mandates`
- `metrics_infrastructure` — soul health tracking config

**Soul Context Extraction** (`src/omega/soul_utils.py:17-53`):
- Path 1: `soul_evolution.lessons_learned` with L3 keys
- Path 2: `directives[].rule` or `directive` (dual-key lookup)
- Path 3: `identity.values[]` + `identity.strengths[]`
- Capped at 3 items (M18 Token Efficiency)

### 2.5 Entity Affinity Inference Presets (`config/entity_model_affinity.yaml`)

Entities can override inference parameters via `inference_presets`:
```yaml
roc_racoon:
  inference_presets:
    temperature: 0.3
    system_prompt: "You are RocRacoon, the Sovereign Miner..."
    preferred_context: 8192
```

Applied in `oracle.py:1024-1038` — affinity presets **prepend** to the built system prompt.

### 2.6 Missing from Current Architecture

| Missing Capability | Evidence |
|-------------------|----------|
| **Context-window-aware prompt truncation** | ContextBuilder uses fixed 4K budget; no awareness of model's actual context window |
| **Domain-module injection** | No mechanism to load "engineering domain" or "heritage domain" into prompt |
| **Role-aware composition** | Planner vs Executor roles not distinguished in prompt building |
| **Template system** | String concatenation only; no Jinja2, no structured templates |
| **Dynamic temperature/max_tokens per role** | Single temperature per entity; no planner (low temp) vs executor (higher temp) differentiation |


---

## 3. PLANNER/EXECUTOR PATTERNS — Existing Delegation, Subagent, Task_Tool_Type

### 3.1 HybridOrchestrator — Cloud Planner / Local Executor (`src/omega/oracle/planner/hybrid_orchestrator.py`)

**Architecture** (lines 13-25):
```
1. Cloud Planner (advisory): emits JSON DAG via cloud provider
2. Local Executor (primary): runs sub-tasks on native-gguf/lmster
3. Escalation: if local fails 2x, single sub-task escalates to cloud
```

**M7 Compliance** (lines 20-24):
- Local providers (native-gguf, lmster) ALWAYS tried first
- Cloud planner is advisory only — its DAG is a suggestion
- Local executor can reject sub-tasks that exceed complexity threshold
- Escalation is per-subtask, not per-goal (minimizes cloud usage)

**Planner System Prompt** (lines 53-67):
```python
PLANNER_SYSTEM_PROMPT = """You are an expert AI Planner. Decompose the user's goal into atomic,
highly specific sub-tasks. Ensure that tasks with no dependencies can run in parallel.
Formulate sub-tasks so they can be executed by small, fast local LLMs.

For each sub-task, specify:
  - id: unique identifier (e.g., "step_1")
  - description: detailed description of the atomic step
  - action_type: one of: extract, code, summarize, classify, reason, synthesize
  - complexity: one of: trivial, simple, moderate, complex, ambiguous
  - dependencies: IDs of sub-tasks that must complete first
  - expected_output_schema: JSON schema or GBNF grammar for output
  - estimated_tokens: estimated token count for this sub-task

Output valid JSON matching the ExecutionPlan schema. Do NOT include any
text outside the JSON."""
```

**Local Executor System Prompt** (lines 69-70):
```python
LOCAL_EXECUTOR_SYSTEM_PROMPT = """You are a precise local task executor. Output JSON strictly
matching the provided schema. Do not include any text outside the JSON."""
```

**Key Methods**:
- `generate_plan()` — calls cloud model (default: `claude-sonnet-4.6` via `antigravity`) to emit DAG
- `_generate_plan_local()` — fallback using `qwen3-1.7b` when cloud unavailable
- `execute_dag()` — runs ready tasks in parallel via `anyio.create_task_group()`
- `_execute_task_with_retry()` — tries local `max_local_retries` (default 2) times, then escalates to cloud
- `_execute_local()` — uses `qwen3-1.7b` with `temperature=0.0`, JSON schema enforcement
- `_execute_cloud()` — escalation path using cloud planner model

**Complexity Heuristic** (`src/omega/oracle/planner/dag_schema.py:263-347`):
```python
MAX_DEPENDENCY_DEPTH = 2  # >2 deps → cloud
MAX_LOCAL_TOKENS = 4096   # >4096 tokens → cloud
MAX_LOCAL_COMPLEXITY = ComplexityTier.SIMPLE  # Only trivial/simple run local

LOCAL_SAFE_ACTIONS = {EXTRACT, CODE, SUMMARIZE, CLASSIFY}
CLOUD_ONLY_ACTIONS = {REASON, SYNTHESIZE}

def should_run_locally(subtask: SubTask) -> bool:
    # Rule 1: Dependency depth > 2 → cloud
    # Rule 2: Context > 4096 tokens → cloud
    # Rule 3: REASON/SYNTHESIZE → cloud
    # Rule 4: Schema-constrained trivial/simple → local
    # Rule 5: Default — local only for trivial/simple
```

### 3.2 Subagent Dispatch Protocol (`src/omega/oracle/subagent_dispatcher.py`, `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`)

**HandoffPacket Schema** (lines 48-102):
```python
@dataclass
class HandoffPacket:
    source_agent: str
    target_agent: str
    task_type: TaskType  # design, review, research, mine, verify, implement
    task_description: str
    relevant_files: List[str]
    context: str
    context_delivery: str = "inline"  # "inline" | "file_ref" | "usm_key"
    packet_id: str = ""
    trace_id: str = ""
    zoneid: int = ZONEID_HANDOFF  # 0x1d4a16
    packet_type: PacketType = "request"
    status: PacketStatus = "pending"
    expected_output: str = ""
    ttl_seconds: int = 14400
    resolver_strategy: ResolverStrategy = "escalate"
    visited_agents: List[str] = []  # Loop guard
    hop_count: int = 0
    max_hops: int = 10
```

**Capability Registry** (lines 190-259) — Built from WAD `dispatch.yaml`:
```python
AgentDescriptor = {
    "mode": "primary" | "subagent",
    "purpose": str,
    "capabilities": List[str],
    "domains": List[str],
    "node_slot": str,  # e.g., "N1", "N3"
    "task_tool_type": str,  # "general", "explore", "scribe", "pillar"
    "owned_files": List[str],
    "role": str,
    "model": str,
}
```

**Dispatch Prompt Building** (`build_dispatch_prompt()`, lines 297-366):
- Embeds target agent's purpose, capabilities
- Inlines context (MANDATORY per §0 critical lesson)
- Lists relevant files with heritage tag extraction
- Includes heritage & mandates boilerplate

**Critical Lesson from Protocol** (`SUBAGENT_DISPATCH_PROTOCOL.md` §0):
> **Inline Context Is the Difference Between Empty Results and Temple-Grade Work**
> Three identical dispatches to `jem` — only the one with **inline context** (6 source docs embedded) succeeded (544-line report, 11 L3 proposals). File paths alone fail.

### 3.3 Agent Fleet Hierarchy (`docs/strategy/AGENTS.md` — referenced in protocol)

| Agent | Type | Capabilities | Domains | Task Tool Type |
|-------|------|-------------|---------|----------------|
| `kali` | Primary | Oversight, delegation, drift destruction | Strategy, fleet management | `general` |
| `maat` | Primary | Build Oversight (N1-N5) | Build side, hardening | `general` |
| `lilith` | Primary | Run Oversight (N6-N10) | Run side, operations | `general` |
| `roc_racoon` | Primary | Legacy mining, pattern extraction | Legacy repos, Grok exports | `explore` |
| `jem` | Primary | Research orchestration | 3-tier knowledge pipeline | `general` |
| `researcher` | Primary | Deep research, lattice reasoning | Web research, documentation | `general` |
| `verity` | Primary | Unified compliance + gnosis distillation | Code review + soul.yaml updates | `scribe` |
| `pillar` | Subagent | Slot-based domain agent | Parameterized by `--slot PX` | `pillar` |

### 3.4 Missing for Planner/Executor Vision

| Missing Piece | Current State | Needed for Vision |
|--------------|---------------|-------------------|
| **Context-window-aware model routing** | Hardcoded `qwen3-1.7b` for local executor | Route planner → MiMo-7B (32K) or Nemotron-3-Ultra (1M); executor → Qwen3-1.7B (8K) |
| **Planner-specific prompt template** | Single `PLANNER_SYSTEM_PROMPT` constant | Dynamic builder: context window, domain, role → tailored prompt |
| **Executor-specific prompt template** | Single `LOCAL_EXECUTOR_SYSTEM_PROMPT` | Minimal prompt for 4K context; grammar enforcement focus |
| **Per-role token budgets** | Single `MAX_LOCAL_TOKENS=4096` | Planner: 16K-32K; Executor: 2K-4K |
| **Dynamic complexity threshold** | Fixed `MAX_LOCAL_COMPLEXITY=SIMPLE` | Adjust based on available model's context window |
| **Planner/Executor model selection in affinity YAML** | Single `preferred_models` per entity | Separate `planner_model` and `executor_model` tiers |

---

## 4. KNOWLEDGE DOMAIN LOADING — Current Mechanisms (Library, Memory, Lattice, KB)

### 4.1 Library System (`src/omega/library/__init__.py`)

**Offline-first knowledge infrastructure** with submodules:
- `inbox.py` — Intake inbox (queues items for processing)
- `extractor.py` — Content extraction (web, PDF, RSS, HTML)
- `curator.py` — Curation pipeline (quality gates, classification)
- `library.py` — Offline library (storage, search, retrieval)
- `indexer.py` — Vector + FTS indexing
- `research.py` — Multi-depth research engine
- `security.py` — SSRF, path traversal, download size guards
- `coordinator.py` — Resource-aware background worker coordinator
- `rate_limiter.py` — Per-domain token bucket rate limiter
- `hivemind_bridge.py` — Curation event publishing to Hivemind

**Library Class** (`src/omega/library/library.py` — not read but inferred):
- Document storage with metadata
- Hybrid search (vector + FTS)
- Domain-organized collections

### 4.2 MemoryStore — Hot/Warm/Cold (`src/omega/memory_store.py`)

**Three-tier architecture** (lines 92-105):
- **Hot** — LRU cache (50 sessions max), OrderedDict per entity:session
- **Warm** — FileStorageProvider (JSONL on disk), Redis (optional)
- **Cold** — InMemoryStorageProvider fallback, external archive (90-day policy)

**Key Methods**:
- `get_history(entity_name, session_id, limit)` — returns recent exchanges
- `search_fts(query, entity_name, limit)` — BM25 keyword search
- `search(query, entity_name, limit)` — Hybrid RRF (FTS5 + Vector)
- `add_exchange()` — records user-assistant pair with metadata
- `sovereign_ingest()` — Sieve → Sign → Index pipeline for external content

**Memory Blocks** (D-283 Mnemosyne, `src/omega/memory/blocks.py`):
```python
class MemoryBlock:
    label: str           # "persona", "project-overview", "decisions"
    value: str           # content
    limit: int           # character cap (SLA)
    description: str     # guides agent WHEN to read/write
    read_only: bool      # governance
    category: BlockCategory  # IDENTITY, STRATEGY, ASSUMPTION, PREFERENCE, GOAL, EVENT, FAILURE, CONTEXT
    governance_level: GovernanceLevel  # PRIVATE, SHARED_READ, SHARED_WRITE, PUBLIC
```

**Essential Blocks** (auto-created per entity):
- `persona` — identity, behavioral guidelines (read_only, IDENTITY, 5000 chars)
- `human` — user info, preferences (PREFERENCE, 3000 chars)
- `safety` — constitutional principles (read_only, IDENTITY, 2000 chars)

**Domain Blocks** (created on demand):
- `project-overview`, `project-commands`, `project-conventions`, `project-architecture`, `project-gotchas`
- `current-task`, `context`, `decisions`, `failures`

### 4.3 SelectiveHydration — L3 Gnosis Retrieval (`src/omega/oracle/selective_hydration.py`)

**Purpose**: Retrieve L3 (Universal) principles from Qdrant by cosine similarity and inject into ContextBuilder.

**Pipeline** (lines 174-236):
1. Embed query via EmbeddingManager chain
2. Search vector adapter filtered by `entity_name` (collection: `l3_gnosis_{entity_name}`)
3. Filter by confidence threshold (default 0.5)
4. Deserialize to `L3Principle` objects
5. Sort by similarity descending, return top-K (default 5)

**L3Principle Dataclass** (lines 57-123):
```python
@dataclass
class L3Principle:
    entity_name: str
    content: str
    principle_id: str = ""  # hash of entity_name + content
    domain: str = "general"
    confidence: float = 1.0
    source: str = ""
    created_at: str = ""
    category: str = "general"
    similarity: float = 0.0  # populated at retrieval
```

**Integration**: Called from `ContextBuilder._build_gnosis_block()` (`context_builder.py:323-353`)

### 4.4 Entity Affinity YAML (`config/entity_model_affinity.yaml`)

**Structured Match Schema** (replaces legacy string evaluator):
```yaml
routing_rules:
  - match:
      domain: ["coding", "technical", "shell"]
    use: local_fast
  - match:
      complexity_gt: 0.7
    use: local_deep
  - match:
      online: true
      requires: ["verification"]
    use: cloud
```

**Inference Presets** per entity:
```yaml
inference_presets:
  temperature: 0.3
  system_prompt: "You are Sekhmet, Keeper of N1..."
  preferred_context: 8192
```

**Resolver** (`src/omega/oracle/entity_affinity.py:320-400`):
- Evaluates match conditions (domain, complexity_gt, online, requires, prompt_length_lt)
- First match wins
- Falls back through tier chain: cloud → local_deep → local_fast → iris

### 4.5 Lattice CLI Seeds (`docs/gnosis/lattice/`)

**Seed Files** (domain knowledge per CLI):
- `gemini_cli.md` — Deep research, subagent fleet management
- `opencode_cli.md` — Implementation, AnyIO hardening, local-first orchestration
- `cline_cli.md` — VSCodium integration, UI/UX hardening
- `copilot_cli.md` — Rapid prototyping, boilerplate generation
- `antigravity_cli.md` — Strategic oversight, architecture, high-altitude planning

**Jem-2.0 Oversoul** (3 sub-facets):
| Facet | Tier | Model | Soul File |
|-------|------|-------|-----------|
| Jem Initiate | L1 (Gather) | Qwen3-4B-Thinking (lmstudio) | `jem-initiate` |
| Jem Analyst | L2 (Synthesize) | Gemma 4 31B (Google) | `jem-2.0` |
| Jem Editor | L3 (Resolve) | Big Pickle (frontier) | `jem-editor` |

### 4.6 Agent KB Protocol (`docs/kb/AGENT_KB_PROTOCOL.md`)

**Omega-KB Protocol v1** — How agents interact with `docs/kb/`:
1. **Discovery** — Read INDEX.md → grep → read target entry
2. **Consumption** — Frontmatter → Core Knowledge → Antipatterns → Evolution Notes
3. **Contribution** — Draft → Changelog → PR → Human review → Merge
4. **Staleness** — 3-tier (Critical/Moderate/Cosmetic) + triggers (PIVOT, age, test failure)
5. **Maintenance** — Lint, orphan scan, refresh cycle

**File Format** — YAML frontmatter with `id`, `domain`, `tags`, `status`, `supersedes`, `reinforcement_count`

### 4.7 Missing for "Knowledge Domains as Loadable Modules"

| Missing Capability | Current Fragment | Vision Requirement |
|-------------------|------------------|-------------------|
| **Unified `load_domain(domain_name)` API** | Scattered across Library, MemoryStore, SelectiveHydration, Affinity, Lattice | Single call: `await load_domain("engineering")` → injects relevant blocks, principles, affinity presets |
| **Domain Module Packaging** | Loose files in multiple locations | Packaged modules: metadata (size, deps, target_context_window), blocks, principles, prompts |
| **Domain → Context Window Mapping** | Affinity YAML has `preferred_context` per entity | Domain declares optimal context window (e.g., "architecture" → 32K, "coding" → 8K) |
| **Cross-Entity Domain Sharing** | MemoryBlock `governance_level` supports SHARED_READ/WRITE | Domain modules loadable by ANY agent; governance per domain |
| **Domain Versioning/Updates** | KB protocol has versioning | Domain modules with semantic versioning, changelog, supersession |
| **Domain Dependency Graph** | None | Domains declare dependencies (e.g., "security" requires "infrastructure") |


---

## 5. CONTEXT WINDOW MANAGEMENT — Compaction, Token Budgets, Model Selection

### 5.1 CompactionHarvester (`src/omega/oracle/compaction_harvester.py`)

**Purpose**: Automated background trigger for memory compaction. Monitors active entity sessions and triggers compaction for those exceeding threshold.

**Configuration** (lines 24-29):
```python
DEFAULT_MAX_EXCHANGES = 30      # Max exchanges before compaction
DEFAULT_WARN_THRESHOLD = 25     # Warn at 25 exchanges (83%)
METRICS_WINDOW = 500            # Max events retained for metrics
```

**Assessment** (`assess_session()`, lines 120-132):
```python
def assess_session(self, entity_name: str, session_id: str, exchange_count: int) -> SessionSizeReport:
    needs_compaction = exchange_count > self.max_exchanges
    near_threshold = exchange_count >= self.warn_threshold
    return SessionSizeReport(entity_name, session_id, exchange_count, needs_compaction, near_threshold)
```

**Compaction Event Recording** (`record_compaction()`, lines 136-160):
- Tracks before/after exchange count, duration, trigger type
- Maintains metrics window (500 events)
- Provides `get_metrics()` and `get_entity_metrics()`

**Background Loop** (`_harvest_loop()`, lines 247-257):
- Runs every 30 minutes (1800s)
- Currently passive — event-driven via `record_compaction()`

### 5.2 ContextBuilder Token Budget (`src/omega/oracle/context_builder.py`)

**DEFAULT_TOKEN_LIMIT = 4000** (line 39, `constants.py`)

**Budget Enforcement** (`build_context()`, lines 280-287):
```python
if degradation_level:
    if degradation_level == "Stressed":
        token_limit = int(token_limit * 0.5)      # 2000 tokens
    elif degradation_level == "Critical":
        token_limit = int(token_limit * 0.25)     # 1000 tokens
    elif degradation_level == "Disabled":
        token_limit = 0
```

**Compaction Pipeline** (`_compact_and_format_exchanges()`, lines 459-571):
1. **ObservationMaskingStrategy** — Culls repetitive "logged"/"confirmed" lines (zero cost)
2. **Headroom Semantic Compression** — 60-95% token reduction via structural compression
3. **Sliding Window** — Newest-first (or quality-weighted) fill to token budget
4. **TruncationStrategy** — Emergency hard truncate from oldest

**Quality-Weighted Selection** (lines 541-546):
```python
if quality_weighted and pairs:
    for pair in pairs:
        pair["_quality_score"] = self._score_exchange_quality(pair)
    pairs.sort(key=lambda p: p["_quality_score"], reverse=True)
```

**Token Estimation** (line 573-579): Rough `len(text) // 4` (4 chars/token)

### 5.3 OpenCode Compaction System (External Reference)

From `docs/research/R_OPENCODE_COMPACTION_DEEP_DIVE.md`:

**Official OpenCode Compaction Config**:
```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 2,
    "preserve_recent_tokens": 40000,
    "reserved": 10000
  }
}
```

**Trigger Formula**: `total_tokens > (model_context_limit - max(output_tokens, 20000) - compaction.reserved)`

**Two-Phase Process**:
1. **Prune** — Timestamp-based hiding of old tool outputs (no LLM call)
2. **Summarize** — LLM generates 5-heading structured summary; last user message replayed

**Agent Compaction Config** (separate model for summarization):
```json
{
  "agent": {
    "compaction": {
      "model": "google/gemma-4-31b-it",
      "steps": 1,
      "temperature": 0.3
    }
  }
}
```

### 5.4 Model Context Windows (from `config/models.yaml` and `config/model_registry/`)

| Model | Context Window | Provider | Role |
|-------|---------------|----------|------|
| `qwen3-1.7b` | 8192 | native-gguf | N1-N10 nodes, fast inference |
| `qwen3-4b-thinking` | 32768 | native-gguf | Ma'at/Lilith synthesis |
| `mimo-7b-rl-q4_k_m` | 32768 | native-gguf | Strong reasoning/coding |
| `nemotron-3-ultra-local` | 1000000 | native-gguf | Local frontier |
| `gemma-4-31b-it-free` | 262144 | google | Cloud workhorse (free tier) |
| `deepseek-v4-flash-free` | 1000000 | openrouter | Cloud research |
| `claude-sonnet-5-high-thinking` | 200000+ | opencode-zen | Cloud planning |

**From `config/model_registry/models/local/nemotron-3-ultra-local.yaml.md`**:
```yaml
context_window: 1000000
max_output_tokens: 32768
```

**From `config/model_registry/models/cloud/gemma-4-31b-it-free.yaml.md`**:
```yaml
context_window: 262144
```

### 5.5 Provider Selector & Model Routing (`src/omega/oracle/provider_selector.py`)

**Scoring Algorithm** (lines 62-92):
```python
Score = (BasePriority * 10) - PII_Penalty - Latency_Penalty - Stability_Penalty
```

- **BasePriority** from config (0 = highest)
- **PII_Penalty**: -100 for cloud providers if PII detected
- **Latency_Penalty**: `(ema_latency - 1000) / 100`
- **Stability_Penalty**: `cusum_g * 5.0`

**No Context Window Awareness**: Selector does NOT consider model context window in scoring.

### 5.6 TriageRouter (Referenced in `oracle.py:733-771`)

**Purpose**: Select optimal model for entity+query via constraints.

**Request Structure** (`src/omega/orchestration/triage_router.py` — inferred):
```python
TriageRequest:
  task: TaskRequest(description, domain)
  entity: EntityContext(name, soul_path)
  constraints: Constraints()
  session: SessionContext(id, trace_id)
```

**Constraints** — Not fully visible but likely include context window, cost, latency.

### 5.7 Missing for Context-Window-Aware Architecture

| Missing Capability | Current State | Required for Vision |
|-------------------|---------------|---------------------|
| **Per-model context window registry** | Scattered in `models.yaml`, `model_registry/`, provider configs | Single source: `model_context_windows[model_name] = tokens` |
| **Context-window-aware model selection** | ProviderSelector ignores context window | Planner routes to 64K+ models; Executor routes to 4K-8K models |
| **Dynamic token budget per role** | Single `DEFAULT_TOKEN_LIMIT=4000` | Planner: 16K-32K budget; Executor: 2K-4K budget |
| **Compaction threshold per model** | Fixed 30 exchanges | Scale threshold by model context window (Nemotron 1M → much higher) |
| **Context gauge / pressure detection** | DegradationManager (CPU/RAM only) | Token-pressure gauge: `current_tokens / model_context_window` |
| **Model fallback by context window** | Fallback by priority only | If 32K model full → try 8K model with compaction, not cloud |

---

## 6. LOCAL INFERENCE OPTIMIZATION — Current State for 16GB CPU-Only (Ryzen 5700U)

### 6.1 Hardware Profile (`config/hardware_profile.yaml`)

```yaml
cpu:
  vendor: "amd"
  model: "AMD Ryzen 7 5700U with Radeon Graphics"
  architecture: "x86_64"
  physical_cores: 8
  logical_threads: 16
  l3_cache_kb: 8192
  compute_cores: [0, 1, 2, 3, 4, 5, 6]   # 7 cores for compute
  io_threads: [7]                         # 1 core for I/O
  recommended_threads: 7
  numa_single_die: true
  microarch: "zen2"

memory:
  total_mb: 14793
  available_mb: 10305
  uma_carveout_mb: 8192
  uma_vram_mb: 512
  uma_gtt_mb: 7936
  swap_zram_mb: 16384       # DEPRECATED — now zswap + NVMe swap
  nvme_swap_mb: 32768
```

**Key Constraints**:
- 16GB total, ~10GB available for AI workloads
- UMA (Unified Memory Architecture) — 8GB carveout for iGPU
- Zen 2 microarchitecture — 8 physical cores, 16 threads
- Single NUMA die — `OMP_PROC_BIND=close` effective

### 6.2 NativeGGUFProvider — Zen 2 Optimizations (`src/omega/oracle/providers.py:527-1240`)

**CPU Affinity** (lines 673-690):
```python
def _apply_cpu_affinity(self) -> Dict[str, Any]:
    optimizer = _get_cpu_optimizer()
    result = optimizer.enforce_affinity(self._cores)  # cores [0,2,4,6] by default
```

**KV Cache Quantization** (lines 583-602):
```python
# Default: f16 (safe) — q8_0 crashes some models (Qwen3)
self._type_k = config.get("type_k", 1)  # GGML_TYPE_F16
self._type_v = config.get("type_v", 1)  # GGML_TYPE_F16

# Explicit kv_cache_type overrides both
kv_cache_type = config.get("kv_cache_type")  # "q8_0" → 50% memory vs f16
```

**Thread Configuration** (lines 573-576):
```python
self._n_threads = config.get("n_threads", n_threads_default)      # 6 default
self._n_threads_batch = config.get("n_threads_batch", self._n_threads)
```

**Batch Sizes** (lines 604-606, tuned for Zen 2 L2 cache 512KB/core):
```python
self._n_batch = config.get("n_batch", 512)
self._n_ubatch = config.get("n_ubatch", 32)
```

**Context Auto-Selection** (`_select_optimal_context()`, lines 733-755):
```python
for ctx in [32768, 16384, 8192, 4096]:
    est = self._estimate_context_memory(ctx)
    if est.get("fits_in_ram", False):
        return ctx
return 4096
```

**Memory Estimation** (`_estimate_context_memory()`, lines 692-731):
- Model size from file
- KV cache: ~2MB per 1K tokens for 4B model at q8_0
- Includes draft resident buffer
- Checks against `RAM_AVAILABLE_AI_MB`

**Worker Process Isolation** (lines 776-1022):
- Spawns separate process for llama.cpp inference
- Queues for request/response (multiprocessing.Queue)
- Prevents C++ crashes from taking down main process
- Supports SomaticState: `llama_copy_state_data` / `llama_set_state_data`

**SomaticState Serialization** (M20, lines 1028-1076):
```python
async def save_state(self) -> bytes:
    await anyio.to_thread.run_sync(self._req_queue.put, {"command": "SAVE_STATE"})
    response = await anyio.to_thread.run_sync(self._res_queue.get)
    return response.get("data")

async def load_state(self, state_bytes: bytes) -> bool:
    await anyio.to_thread.run_sync(self._req_queue.put, {"command": "LOAD_STATE", "state_bytes": state_bytes})
```

### 6.3 Provider Fabric Priority Chain (`config/providers.yaml:62-119`)

```yaml
inference:
  fallback_chain:
  - provider: native-gguf      # Priority 0 — LOCAL FIRST
    enabled: true
    is_cloud: false
  - provider: lmster           # Priority 1 — LOCAL
    enabled: true
    is_cloud: false
  - provider: ollama           # Priority 2 — LOCAL (disabled)
    enabled: false
    is_cloud: false
  - provider: antigravity      # Priority 3 — CLOUD
    enabled: true
    is_cloud: true
  - provider: google           # Priority 4 — CLOUD
    enabled: true
    is_cloud: true
  - provider: openrouter       # Priority 5 — CLOUD
    enabled: true
    is_cloud: true
  - provider: opencode-zen     # Priority 6 — CLOUD
    enabled: true
    is_cloud: true
  # ... more cloud providers
```

**MaKaLi Routing** (`providers.yaml:8-17`):
```yaml
maakali_routing:
  kali:
    prefer: native-gguf
    fallback: antigravity
  maat:
    prefer: antigravity
    fallback: google
  lilith:
    prefer: antigravity
    fallback: google
```

### 6.4 Workhorse Crisis & Mitigation (`docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`)

**Problem**: Gemma 4 31B free tier input token limit **16,000** since 2026-07-15 (was workhorse May-Jul).

**Paths** (G-1 ticket):
- G-1a: Billing Tier 1 (paid Google)
- G-1b: Antigravity OAuth (pool)
- G-1c: OpenCode Zen + WARP proxy pool
- G-1d: Paid alternative

**WARP Proxy Pool** (W-1 ticket):
- Multi-namespace proxy pool for IP-rotated OpenCode Zen
- Blocker: `/usr/local/bin/warp-ns-setup` truncated (syntax error line 49)
- Fix source: `warp-proxy-pool/scripts/warp-ns-setup.sh`

### 6.5 Model Registry & Sampling Overrides (`config/models.yaml:100-117`)

```yaml
sampling_overrides:
  gemma-4-31b:
    match: substring
    min_temperature: 0.85
    min_repetition_penalty: 1.2
    forced_logit_bias:
      759: -10.0        # ' la'
      2149: -10.0       # 'la-'
      236772: -10.0     # 'la-' (variant)
```

Applied in `ModelGateway._apply_sampling_overrides()` (lines 282-314).

### 6.6 Missing for Local-First Vision on 16GB

| Missing Optimization | Current State | Impact on Vision |
|---------------------|---------------|------------------|
| **Context-window-aware model routing** | Priority chain only | Planner needs 64K+ model (Nemotron/MiMo); Executor needs 4K-8K (Qwen3-1.7B) |
| **Dynamic context sizing per role** | Auto-select max that fits | Planner: allocate 32K-64K; Executor: allocate 4K-8K |
| **KV cache quantization per role** | Global config only | Planner: q8_0 for max context; Executor: f16 for speed |
| **Thread allocation per role** | Fixed 6 threads | Planner: more threads for throughput; Executor: fewer for latency |
| **Model pre-loading strategy** | Load on demand | Pre-load planner model (large) + executor model (small) |
| **Memory pressure → context reduction** | DegradationManager (CPU/RAM) | Token-pressure: auto-reduce context window before OOM |
| **SomaticState for planner continuity** | Implemented but unused | Planner saves state between sprints; Executor stateless |


---

## 7. DYNAMIC PROMPT COMPOSITION — Existing Template/Composition Systems

### 7.1 Current Composition Points

| Location | Method | Inputs | Output |
|----------|--------|--------|--------|
| `oracle.py:_prepare_system_prompt()` | String concatenation | personality + memory_context + soul_context | System prompt string |
| `context_builder.py:ContextBuilder.prepend_to_prompt()` | Static prepend | context_block + system_prompt | Combined prompt |
| `entity_affinity.py:AffinityResult.inference_presets.system_prompt` | Prepend | affinity system_prompt + base prompt | Enhanced prompt |
| `ics.py:render()` | Template format | entity, model, channel, trace, phase | ICS-S header string |
| `subagent_dispatcher.py:build_dispatch_prompt()` | Template with sections | HandoffPacket fields + capability registry | Task tool prompt |

### 7.2 ICS-S Header Template (`src/omega/ics.py:46-48`)

```python
ICS_TEMPLATE_FULL = "⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"
ICS_TEMPLATE_COMPACT = "⬡ {entity} ⬡ {phase}"
ICS_TEMPLATE_OFF = ""
```

**Auto-detection** (`_detect_model()`, lines 192-240):
1. `OMEGA_MODEL_OVERRIDE` env (D118)
2. `OPENCODE_MODEL` env
3. OpenCode session DB
4. `opencode.json` model key
5. TriageRouter last_selected_model
6. Entity soul.yaml `inference.model`
7. `"unknown"` fallback

### 7.3 Subagent Dispatch Prompt Template (`subagent_dispatcher.py:297-366`)

```python
lines = [
    f"# 🔱 Omega Engine — Subagent Dispatch: {packet.packet_id}",
    f"You are **{packet.target_agent}**.",
    f"Your role: {target_desc}",
    f"Your capabilities: {target_caps}",
    "## Source",
    f"This dispatch was created by **{packet.source_agent}** ({source_desc}).",
    f"Trace ID: `{packet.trace_id}`",
    "## Context",
    packet.context or "(No additional context provided)",
    "## Task",
    packet.task_description,
    "## Files to Read First",
    *[f"- `{f}`" for f in packet.relevant_files],
    "## Heritage Tags in Referenced Files",
    *[f"- {tag}" for tag in heritage_tags],
    "## Expected Output",
    packet.expected_output,
    "## Heritage & Mandates",
    "- Refer to PIVOT_LOG.md for prior architectural decisions.",
    "- Sovereign Mandate 13 (Temple-Grade T1-T11) applies to all changes.",
    "- Heritage attribution: every id Software-derived pattern MUST carry id-soft inline tags...",
    f"*Dispatch from {packet.source_agent} to {packet.target_agent} — {packet.packet_id}*"
]
```

**Critical**: Context is **inlined** (not file references) — hard lesson from protocol §0.

### 7.4 ContextBuilder Block Assembly (`context_builder.py:313-317`)

```python
# Order: world state (global) → gnosis (principles) → blocks (entity identity) → memory (conversation)
parts = [world_block, gnosis_block, blocks_text, memory_block]
full_context = "\n".join(p for p in parts if p and p.strip())
```

### 7.5 Missing for Dynamic Prompt Builder Vision

| Missing Capability | Current Approach | Vision Requirement |
|-------------------|------------------|-------------------|
| **Template Engine** | String concatenation + f-strings | Jinja2 or similar with inheritance, includes, conditionals |
| **Role-Aware Templates** | Single prompt per entity | Planner template vs Executor template vs Researcher template |
| **Context-Window-Adaptive Truncation** | Fixed 4K budget sliding window | Smart truncation: preserve decisions/errors, drop chatter |
| **Domain-Module Injection Slots** | None | `{{ domain_modules.engineering }}`, `{{ domain_modules.heritage }}` |
| **Per-Role Parameter Injection** | Affinity presets only | `{{ role.temperature }}`, `{{ role.max_tokens }}`, `{{ role.context_window }}` |
| **Prompt Versioning/Lineage** | None | Track prompt templates in git; A/B test prompt variants |
| **Composition Validation** | None | Verify token count < model context window before inference |

---

## 8. GAP ANALYSIS — Specific Missing Pieces for the Architect's Vision

### 8.1 Gap Matrix: Vision Requirement → Current State → Gap Severity

| Vision Requirement | Current State | Gap | Severity |
|-------------------|---------------|-----|----------|
| **Dynamic System Prompt Builder** | Static concatenation in `_prepare_system_prompt()` | No template engine, no role-aware composition, no domain injection slots | 🔴 Critical |
| **Context-Window-Aware Prompt Sizing** | Fixed 4K token limit, degradation scaling only | No per-model context window registry, no planner/executor budget differentiation | 🔴 Critical |
| **Planner/Executor Model Split** | Single `qwen3-1.7b` for local executor | No routing to large-context models (Nemotron 1M, MiMo 32K) for planner | 🔴 Critical |
| **Knowledge Domains as Loadable Modules** | Fragmented: Library, MemoryStore, SelectiveHydration, Affinity YAML, Lattice | No unified `load_domain()` API, no domain packaging, no cross-agent sharing | 🔴 Critical |
| **Per-Role Token Budgets** | Single `DEFAULT_TOKEN_LIMIT=4000` | Planner needs 16K-32K; Executor needs 2K-4K | 🟡 High |
| **Dynamic Complexity Thresholds** | Fixed `MAX_LOCAL_COMPLEXITY=SIMPLE` | Threshold should scale with available model context window | 🟡 High |
| **Domain → Context Window Mapping** | Affinity YAML `preferred_context` per entity | Domain declares optimal context (e.g., "architecture"→32K, "coding"→8K) | 🟡 High |
| **Planner-Specific Prompt Template** | Single `PLANNER_SYSTEM_PROMPT` constant | Minimal, structured, grammar-enforced for large-context model | 🟡 High |
| **Executor-Specific Prompt Template** | Single `LOCAL_EXECUTOR_SYSTEM_PROMPT` | Ultra-minimal for 4K context, JSON schema focus | 🟡 High |
| **SomaticState for Planner Continuity** | Implemented in NativeGGUFProvider, unused | Planner saves state between sprints; instant resume | 🟢 Medium |
| **Prompt Template Versioning** | None | Git-tracked prompt templates with A/B testing | 🟢 Medium |
| **Cross-Agent Domain Sharing** | MemoryBlock governance supports it | Domain modules loadable by ANY agent with governance | 🟢 Medium |

### 8.2 Cross-Reference with GAP_REGISTRY.json

**Relevant Existing Gaps**:
- **R2** — Model context window detection mechanism (dynamic vs static, tier mapping) — *Partially resolved: windows known, detection code path open*
- **R33** — Cold session context estimation (0.7x multiplier, transition triggers) — *Outstanding*
- **R34** — Provider-specific band adjustments (per-provider gauge bands) — *Outstanding*
- **R35** — Model-specific degradation thresholds — *Outstanding*
- **R36** — Baseline calibration methodology — *Outstanding*
- **R37** — Identity fluidity architecture (E-0) — *Outstanding*
- **R38** — NotebookLM integration (NL-1) — *Outstanding*
- **R14b** — Nemotron plugin fallback chain — *Outstanding*
- **R31** — Streaming plugin scope reduction — *Resolved*

**New Gaps Identified by This Analysis** (not in registry):
| Proposed Gap ID | Topic | Dependent Vision Component |
|----------------|-------|---------------------------|
| **DP-1** | Dynamic Prompt Builder — template engine, role-aware composition, domain injection | Dynamic System Prompt Builder |
| **DP-2** | Context Window Registry — single source for all model context windows | Planner/Executor split, token budgets |
| **DP-3** | Planner/Executor Model Router — routes by role + context window need | Planner/Executor with Context-Window Differentiation |
| **DP-4** | Domain Module Loader — unified `load_domain()` API with packaging | Knowledge Domains as Loadable Modules |
| **DP-5** | Per-Role Token Budget Manager — planner vs executor budgets | Context-Window Differentiation |
| **DP-6** | Domain Context Window Map — domain → optimal context window | Knowledge Domains + Planner/Executor |
| **DP-7** | Planner/Executor Prompt Templates — versioned, validated templates | Dynamic Prompt Builder |
| **DP-8** | SomaticState Planner Integration — state save/restore for planning continuity | Planner/Executor Architecture |

### 8.3 Cross-Reference with RESEARCH_PLAN_PHASE1_4_20260813.md

**Phase 1 (Context Gauge)** — R2, R33, R34, R35, R36 directly relevant
**Phase 2 (zswap + Streaming)** — Not directly relevant
**Phase 3 (Un-overengineering)** — R37 (Identity fluidity) relevant for dynamic role switching
**Phase 4 (Phase D Gate)** — Not directly relevant

### 8.4 Cross-Reference with PIVOT_LOG.md (Key Decisions)

| Decision | Relevance |
|----------|-----------|
| **D-528** — pyresilience > tenacity (locked) | Retry strategy for planner/executor escalation |
| **D-533** — This manual is execution SSOT (not Ark) | Confirms this gap analysis is authoritative for current sprint |
| **D-536** — One router: ProviderSelector + providers.yaml | Simplifies model routing but needs context-window awareness |
| **D-537** — UO Phase 1 library swaps rejected | Don't add new deps; build on existing infrastructure |
| **D-538** — SDP/Cognitive Sovereignty/Qdrant/JIT/Instruction Router PARKED | Don't build those; focus on core gaps |

---

## 9. BLUEPRINT RECOMMENDATIONS — Local-Evidence-Based Architecture

### 9.1 Dynamic System Prompt Builder (`src/omega/oracle/prompt_builder.py` — NEW)

```python
# src/omega/oracle/prompt_builder.py
"""
Dynamic System Prompt Builder — composes prompts from:
  - Role template (planner/executor/researcher/etc.)
  - Domain modules (injected at {{ domain_slots }})
  - Entity personality + soul context
  - Memory context (ContextBuilder)
  - Context-window-aware truncation
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import jinja2

@dataclass
class PromptSpec:
    role: str                    # "planner", "executor", "researcher", "miner"
    entity_name: str
    domain_modules: List[str]    # ["engineering", "heritage", "architecture"]
    context_window: int          # Model's actual context window
    token_budget: int            # Allocated for this role
    temperature: float
    max_tokens: int

class DynamicPromptBuilder:
    def __init__(self, template_dir: Path = Path("config/prompt_templates")):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._register_filters()
    
    def _register_filters(self):
        self.env.filters['token_estimate'] = lambda s: len(s) // 4
        self.env.filters['truncate_to'] = lambda s, n: s[:n] + "..." if len(s) > n else s
    
    async def build(self, spec: PromptSpec, 
                    memory_context: str,
                    soul_context: str,
                    world_context: str) -> str:
        """Build complete system prompt for a role."""
        
        # Load role template
        template = self.env.get_template(f"roles/{spec.role}.j2")
        
        # Load domain modules
        domain_blocks = {}
        for domain in spec.domain_modules:
            domain_blocks[domain] = await self._load_domain_module(domain, spec.token_budget)
        
        # Calculate dynamic budgets
        budgets = self._calculate_budgets(spec, memory_context, soul_context, world_context, domain_blocks)
        
        # Render
        return template.render(
            entity=spec.entity_name,
            role=spec.role,
            personality=await self._get_personality(spec.entity_name),
            memory_context=memory_context,
            soul_context=soul_context,
            world_context=world_context,
            domain_blocks=domain_blocks,
            budgets=budgets,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
            context_window=spec.context_window,
        )
    
    def _calculate_budgets(self, spec, memory, soul, world, domains) -> Dict[str, int]:
        """Allocate token budget across sections proportionally."""
        total_fixed = sum(len(s) for s in [soul, world] if s)
        available = spec.token_budget - total_fixed - 500  # 500 reserve
        
        # Memory gets 50%, domains split 50%
        memory_budget = min(len(memory), available // 2)
        domain_budget = available - memory_budget
        per_domain = domain_budget // max(1, len(domains))
        
        return {
            "memory": memory_budget,
            "per_domain": per_domain,
            "total": spec.token_budget,
        }
    
    async def _load_domain_module(self, domain: str, budget: int) -> str:
        """Load domain knowledge module, truncated to budget."""
        # Implementation: read from config/domains/{domain}.yaml or Library
        pass
```

**Template Structure** (`config/prompt_templates/roles/`):
```
config/prompt_templates/
├── roles/
│   ├── planner.j2          # Large context, structured reasoning
│   ├── executor.j2         # Minimal, JSON schema focus
│   ├── researcher.j2       # Research-oriented, citation format
│   └── miner.j2            # Legacy archaeology focus
├── domains/
│   ├── engineering.j2
│   ├── heritage.j2
│   ├── architecture.j2
│   └── ...
└── blocks/
    ├── memory.j2
    ├── soul.j2
    └── world.j2
```

### 9.2 Context Window Registry (`config/model_context_windows.yaml` — NEW)

```yaml
# Single source of truth for ALL model context windows
# Populated from config/models.yaml, config/model_registry/, provider configs

model_context_windows:
  # Local models
  qwen3-1.7b: 8192
  qwen3-1.7b-q6_k: 8192
  qwen3-4b-thinking: 32768
  qwen3-4b-thinking-q4_k_m: 32768
  mimo-7b-rl-q4_k_m: 32768
  nemotron-3-ultra-local: 1000000
  rocracoon-3b-q4_k_m: 8192
  rocracoon-3b-q5_k_m: 8192
  
  # Cloud models
  gemma-4-31b-it-free: 262144
  gemini-2.5-pro: 1048576
  gemini-2.5-flash: 1048576
  deepseek-v4-flash-free: 1000000
  claude-sonnet-5-high-thinking: 200000
  claude-opus-4.8: 200000
  nemotron-3-super-free: 1000000

# Role-based context window allocation (for local models)
role_context_allocation:
  planner:
    primary: nemotron-3-ultra-local    # 1M context
    fallback: mimo-7b-rl-q4_k_m        # 32K context
    token_budget: 32768                # 32K for planning
  executor:
    primary: qwen3-1.7b                # 8K context
    fallback: qwen3-4b-thinking        # 32K context
    token_budget: 4096                 # 4K for execution
  researcher:
    primary: nemotron-3-ultra-local    # 1M context
    fallback: mimo-7b-rl-q4_k_m        # 32K context
    token_budget: 16384                # 16K for research
```

**Registry Loader** (`src/omega/oracle/context_registry.py` — NEW):
```python
class ContextWindowRegistry:
    def __init__(self, yaml_path: Path = Path("config/model_context_windows.yaml")):
        self._data = yaml.safe_load(yaml_path.read_text())
    
    def get_context_window(self, model_name: str) -> int:
        return self._data["model_context_windows"].get(model_name, 4096)
    
    def get_role_allocation(self, role: str) -> Dict[str, Any]:
        return self._data["role_context_allocation"].get(role, {})
    
    def select_model_for_role(self, role: str, available_models: List[str]) -> str:
        """Pick best available model for role based on context window."""
        allocation = self.get_role_allocation(role)
        for model in [allocation.get("primary"), allocation.get("fallback")]:
            if model and model in available_models:
                return model
        return available_models[0] if available_models else "qwen3-1.7b"
```

### 9.3 Planner/Executor Model Router (Extend `ProviderSelector`)

```python
# In src/omega/oracle/provider_selector.py — extend get_ordered_providers()

async def get_ordered_providers_for_role(
    self, 
    model_name: str, 
    query: str, 
    role: str  # "planner" | "executor" | "researcher"
) -> List[Any]:
    """Role-aware provider selection with context window consideration."""
    
    registry = ContextWindowRegistry()
    role_allocation = registry.get_role_allocation(role)
    required_context = role_allocation.get("token_budget", 4096)
    
    # Filter providers by context window capability
    providers = await self.model_gateway.get_available_providers(model_name)
    
    scored = []
    for provider in providers:
        # Get model's actual context window
        model_ctx = registry.get_context_window(provider.model_name)
        
        # Score: prefer models that meet role's context requirement
        context_score = 0
        if model_ctx >= required_context:
            context_score = 100
        elif model_ctx >= required_context * 0.5:
            context_score = 50
        else:
            context_score = -100  # Penalize insufficient context
        
        # Base score from existing logic
        base_score = self._calculate_score(provider, query)
        
        scored.append((provider, base_score + context_score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, s in scored]
```

### 9.4 Domain Module Loader (`src/omega/oracle/domain_loader.py` — NEW)

```python
"""
Knowledge Domain Loader — loads domain modules on demand.
Domain modules are packaged YAML with:
  - metadata: name, version, description, target_context_window, dependencies
  - blocks: MemoryBlock definitions (persona, decisions, conventions, etc.)
  - principles: L3 gnosis principles for the domain
  - prompts: prompt snippets for injection
  - affinity_overrides: inference presets for the domain
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
import yaml

@dataclass
class DomainModule:
    name: str
    version: str
    description: str
    target_context_window: int
    dependencies: List[str]
    blocks: Dict[str, Dict]           # MemoryBlock templates
    principles: List[Dict]            # L3 principles
    prompt_snippets: Dict[str, str]   # Named prompt fragments
    affinity_overrides: Dict[str, Any] # Inference presets

class DomainLoader:
    def __init__(self, domains_dir: Path = Path("config/domains")):
        self.domains_dir = domains_dir
        self._cache: Dict[str, DomainModule] = {}
    
    async def load_domain(self, domain_name: str) -> DomainModule:
        """Load domain module with dependency resolution."""
        if domain_name in self._cache:
            return self._cache[domain_name]
        
        domain_path = self.domains_dir / f"{domain_name}.yaml"
        if not domain_path.exists():
            raise ValueError(f"Domain module not found: {domain_name}")
        
        data = yaml.safe_load(domain_path.read_text())
        module = DomainModule(**data)
        
        # Resolve dependencies
        for dep in module.dependencies:
            await self.load_domain(dep)
        
        self._cache[domain_name] = module
        return module
    
    async def load_domains(self, domain_names: List[str]) -> List[DomainModule]:
        """Load multiple domains, resolving shared dependencies once."""
        modules = []
        for name in domain_names:
            modules.append(await self.load_domain(name))
        return modules
    
    def format_domain_context(self, modules: List[DomainModule], budget_per_domain: int) -> str:
        """Format loaded domains into context block for prompt injection."""
        parts = ["## Domain Knowledge Modules\n"]
        for module in modules:
            parts.append(f"### {module.name} (v{module.version})")
            parts.append(module.description)
            
            # Inject blocks (truncated to budget)
            for label, block in module.blocks.items():
                content = block.get("value", "")
                if content:
                    truncated = content[:budget_per_domain]
                    parts.append(f"#### {label}")
                    parts.append(truncated)
            
            # Inject principles
            if module.principles:
                parts.append("#### Principles")
                for p in module.principles[:3]:  # Top 3
                    parts.append(f"- {p.get('content', '')}")
            
            parts.append("---")
        
        return "\n".join(parts)
```

**Domain Module Example** (`config/domains/engineering.yaml`):
```yaml
name: "engineering"
version: "1.0.0"
description: "Software engineering practices, patterns, and conventions"
target_context_window: 8192
dependencies: []
blocks:
  project-conventions:
    label: "project-conventions"
    description: "Commit style, PR process, code style"
    limit: 2000
    category: "STRATEGY"
  project-architecture:
    label: "project-architecture"
    description: "Directory structure, key modules"
    limit: 3000
    category: "STRATEGY"
  project-gotchas:
    label: "project-gotchas"
    description: "Footguns, things to watch out for"
    limit: 2000
    category: "FAILURE"
principles:
  - content: "L3-Substrate-Enforces-Contract: Logical-layer protocols are wishes until the physical layer enforces them."
    domain: "engineering"
    confidence: 0.98
  - content: "L3-Firewall-Is-Constitution: The Engine-Stack Firewall (M2) is the constitutional boundary."
    domain: "engineering"
    confidence: 0.98
prompt_snippets:
  code_review: "Review for: M1 AnyIO, M2 Firewall, M7 Local-First, M13 Temple-Grade, M22 Provenance"
  implementation: "Follow Plan → Verify → Execute. No cowboy coding."
affinity_overrides:
  temperature: 0.3
  preferred_context: 8192
```

### 9.5 Integration Points — Minimal Changes to Existing Code

| File | Change | Purpose |
|------|--------|---------|
| `oracle.py:_prepare_system_prompt()` | Delegate to `DynamicPromptBuilder.build()` | Replace string concatenation with template system |
| `oracle.py:_summon()` | Pass `role` parameter (planner/executor) | Enable role-aware prompt building |
| `hybrid_orchestrator.py:generate_plan()` | Use `get_ordered_providers_for_role("planner")` | Route planner to large-context model |
| `hybrid_orchestrator.py:_execute_local()` | Use `get_ordered_providers_for_role("executor")` | Route executor to small-context model |
| `entity_affinity.yaml` | Add `planner_model`/`executor_model` tiers | Declare per-role model preferences |
| `context_builder.py` | Accept `role` parameter for budget allocation | Different token budgets per role |

### 9.6 Implementation Priority (Evidence-Based)

| Priority | Component | Evidence | Effort |
|----------|-----------|----------|--------|
| **P0** | Context Window Registry (`model_context_windows.yaml`) | Models.yaml + model_registry already have data; single source needed | 2h |
| **P0** | Planner/Executor Model Router | HybridOrchestrator exists; just needs context-window-aware selection | 4h |
| **P0** | Dynamic Prompt Builder (core) | `_prepare_system_prompt()` is single integration point | 8h |
| **P1** | Domain Loader + 3-4 core domains | Library/MemoryStore/SelectiveHydration have content; needs packaging | 12h |
| **P1** | Role Templates (planner/executor) | HybridOrchestrator has prompts; needs templating | 4h |
| **P1** | Per-Role Token Budgets | ContextBuilder has budget logic; needs role parameter | 3h |
| **P2** | SomaticState Planner Integration | NativeGGUFProvider has save/load; needs orchestration | 6h |
| **P2** | Prompt Template Versioning | Git-tracked templates; A/B test framework | 8h |

### 9.7 Configuration Changes Required

**`config/entity_model_affinity.yaml`** — Add per-role tiers:
```yaml
kali:
  preferred_models:
    planner:
      model: "nemotron-3-ultra-local"
      provider: "native-gguf"
    executor:
      model: "qwen3-1.7b"
      provider: "native-gguf"
  # ... existing tiers remain for backward compat
```

**`config/providers.yaml`** — Add context window metadata:
```yaml
providers:
  native-gguf:
    supported_models:
      nemotron-3-ultra-local:
        context_window: 1000000
      mimo-7b-rl-q4_k_m:
        context_window: 32768
      qwen3-1.7b:
        context_window: 8192
```

**New Files**:
- `config/model_context_windows.yaml` — Single source registry
- `config/prompt_templates/roles/*.j2` — Role templates
- `config/domains/*.yaml` — Domain modules
- `src/omega/oracle/prompt_builder.py` — DynamicPromptBuilder
- `src/omega/oracle/context_registry.py` — ContextWindowRegistry
- `src/omega/oracle/domain_loader.py` — DomainLoader

---

## 10. FILES ACCESSED / COULD NOT ACCESS

### Successfully Read (Complete)
- `.opencode/agents/roc_racoon.md`
- `src/omega/oracle/oracle.py` (1200+ lines)
- `src/omega/ics.py`
- `data/entities/roc_racoon/soul.yaml`
- `src/omega/oracle/context_builder.py`
- `src/omega/oracle/subagent_dispatcher.py`
- `src/omega/oracle/planner/hybrid_orchestrator.py`
- `src/omega/oracle/providers.py` (1240+ lines)
- `src/omega/oracle/model_gateway.py` (1190+ lines)
- `config/providers.yaml`
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
- `src/omega/memory_store.py`
- `src/omega/library/__init__.py`
- `docs/kb/AGENT_KB_PROTOCOL.md`
- `docs/gnosis/lattice/lattice_manifest.md`
- `config/hardware_profile.yaml`
- `src/omega/soul_utils.py`
- `data/coordination/GAP_REGISTRY.json`
- `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md`
- `src/omega/oracle/selective_hydration.py`
- `src/omega/oracle/entity_affinity.py`
- `src/omega/oracle/provider_selector.py`
- `src/omega/oracle/compaction_harvester.py`
- `src/omega/oracle/planner/dag_schema.py`
- `config/models.yaml`
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`
- `src/omega/oracle/entity_registry.py`
- `src/omega/memory/blocks.py`
- `src/omega/constants.py`
- `.agents/AGENTS.md`

### Not Found / Could Not Access
- `docs/strategy/AGENTS.md` — Does not exist (referenced in protocol but missing)
- `src/omega/oracle/constants.py` — Exists but only re-exports from `cvar_table`
- `src/omega/orchestration/triage_router.py` — Referenced but not read (internal)
- `src/omega/memory/vector_adapters.py` — Referenced but not read
- `config/entity_model_affinity.yaml` — Read successfully

---

## 11. TOP 10 MOST IMPORTANT LOCAL FINDINGS

1. **System prompts are built via string concatenation in `_prepare_system_prompt()`** — personality + ContextBuilder memory + soul_utils L3 principles. No template engine, no role awareness, no domain injection slots.

2. **HybridOrchestrator EXISTS but hardcodes `qwen3-1.7b` for local executor** — Planner uses cloud (antigravity/claude-sonnet-4.6); executor uses local `qwen3-1.7b` with `temperature=0.0`. No routing to larger-context local models (Nemotron 1M, MiMo 32K).

3. **Context window management is fragmented** — `DEFAULT_TOKEN_LIMIT=4000` in constants; CompactionHarvester triggers at 30 exchanges; ContextBuilder scales by degradation level (50%/25%); OpenCode has its own compaction (40K preserve, 10K reserved). No single source of truth for model context windows.

4. **NativeGGUFProvider has sophisticated Zen 2 optimizations** — CPU affinity (cores 0,2,4,6), KV cache quantization (q8_0/f16), adaptive context selection (32K→16K→8K→4K), worker process isolation, SomaticState serialization. But no context-window-aware model routing.

5. **Knowledge domains scattered across 5 systems** — Library (offline-first), MemoryStore (hot/warm/cold + MemoryBlocks), SelectiveHydration (L3 gnosis from Qdrant), Entity Affinity YAML (routing + inference presets), Lattice CLI seeds (per-tool knowledge). No unified loader.

6. **Subagent Dispatch Protocol mandates INLINE CONTEXT** — Critical lesson: file paths fail; only inline content works. HandoffPacket has `context_delivery: "inline"` default. Capability registry includes `task_tool_type` for Task tool routing.

7. **Provider fabric is local-first with priority chain** — native-gguf (0) → lmster (1) → ollama (2, disabled) → antigravity (3) → google (4) → openrouter (5) → opencode-zen (6). MaKaLi routing overrides for Kali/Ma'at/Lilith. ProviderSelector scores by priority, PII penalty, latency, stability — but NOT context window.

8. **Entity Affinity YAML uses structured match schema** — Replaces legacy string evaluator. Supports domain, complexity_gt, online, requires, prompt_length_lt. First match wins. Inference presets can prepend system_prompt. But single tier per entity, not planner/executor split.

9. **MemoryBlocks provide typed, governed memory** — Letta-style: persona/human/safety (essential), project-* (domain), decisions/failures. Categories with decay rates. Governance levels (PRIVATE/SHARED_READ/SHARED_WRITE/PUBLIC). But not packaged as loadable domain modules.

10. **Workhorse crisis (Gemma 4 31B 16K limit) drives cloud dependency** — G-1/W-1 tickets for billing/OAuth/WARP. Local models (Nemotron 1M, MiMo 32K) exist but not routed for planning workloads.

---

## 12. TOP 5 ARCHITECTURE RECOMMENDATIONS (LOCAL EVIDENCE-BASED)

### 1. **Build DynamicPromptBuilder with Jinja2 Templates** (P0)
- **Integration Point**: `oracle.py:_prepare_system_prompt()` — single delegation point
- **Templates**: `config/prompt_templates/roles/{planner,executor,researcher,miner}.j2`
- **Injection Slots**: `{{ domain_blocks.engineering }}`, `{{ soul_context }}`, `{{ memory_context }}`
- **Evidence**: Current concatenation in 43 lines; templates enable role-aware composition

### 2. **Create Context Window Registry + Role-Aware Model Router** (P0)
- **New File**: `config/model_context_windows.yaml` — consolidates models.yaml + model_registry
- **Extend**: `ProviderSelector.get_ordered_providers_for_role(role)` 
- **Evidence**: Nemotron 1M, MiMo 32K, Qwen3 8K exist but unused for planning; HybridOrchestrator hardcodes qwen3-1.7b

### 3. **Package Domain Modules with Unified Loader** (P1)
- **New Files**: `config/domains/{engineering,heritage,architecture,security}.yaml`
- **New Module**: `src/omega/oracle/domain_loader.py` — `load_domain("engineering")`
- **Evidence**: MemoryBlocks, SelectiveHydration principles, Affinity presets, Lattice seeds all have domain content but no unified API

### 4. **Implement Per-Role Token Budgets in ContextBuilder** (P1)
- **Change**: `ContextBuilder.build_context(role="planner"|"executor")`
- **Budgets**: Planner 32K, Executor 4K, Researcher 16K (configurable in model_context_windows.yaml)
- **Evidence**: Single `DEFAULT_TOKEN_LIMIT=4000` used for all roles; degradation scaling only

### 5. **Add Planner/Executor Tiers to Entity Affinity YAML** (P1)
- **Change**: Add `planner:` and `executor:` under `preferred_models` per entity
- **Fallback**: Existing tiers remain for backward compatibility
- **Evidence**: Affinity YAML already has structured schema; just needs role dimension

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_dynamic_prompt_gaps ⬡ COMPLETE*

**Deliverable**: `data/coordination/DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md`

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
