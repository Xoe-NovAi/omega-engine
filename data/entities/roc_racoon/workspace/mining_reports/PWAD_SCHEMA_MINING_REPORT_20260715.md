<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PWAD Schema Mining Report — Legacy Archaeology for Dimension Framework

**Date**: 2026-07-15
**Agent**: Roc Racoon (Sovereign Miner)
**Purpose**: Mine ALL legacy repositories and archives for patterns to inform the PWAD Schema and Dimension Registry design

---

## Executive Summary

After exhaustive archaeological mining across 7 archive locations (Old Stacks, docs-backup, foundation-legacy, Grok exports, mining queue, omega-library, and the current omega-engine), I found **21 implementable patterns** organized into 5 categories. The current omega-engine already has a mature WAD system (`wad_loader.py`, `entity_registry.py`, `capability_registry.py`, `entity_affinity.py`, `entity_workspace.py`) that provides the foundation. The Dimension Framework should EXTEND these existing systems, not replace them.

---

## Category 1: WAD Loading Code

### Finding 1.1: `WADLoader` — The Current Engine's WAD Loader (PRIMARY)

**File**: `src/omega/oracle/wad_loader.py` (505 lines)
**Pattern**: Full WAD lifecycle — discovery, manifest validation, entity/voice/world loading, adapter registration
**Relevance**: THE canonical reference for PWAD loading. Already implements IWAD/PWAD separation with priority-based override.

**Key Code** (lines 69-235):
```python
class WADLoader:
    """Loads Omega Engine stacks (WADs) from the filesystem."""
    
    async def load_all_wads(self) -> Dict[str, bool]:
        """Discover and load all WADs in the wads directory."""
        # Auto-discovers WAD directories, loads each
        async for entry in anyio.Path(self.wads_dir).iterdir():
            if await entry.is_dir():
                success, _ = await self.load_wad(entry.name)
                results[entry.name] = success

    async def load_wad(self, stack_name: str, priority: int = 0) -> Tuple[bool, Optional[Path]]:
        """Load a specific WAD stack."""
        # 1. Path traversal guard
        # 2. Manifest validation (field types, required fields, size limits)
        # 3. Load Entities from entities/ directory
        # 4. Load Voices from voices/ directory
        # 5. Resolve Hierarchy Path
        # 6. Load World State (First Breath)
        # 7. Register Memory Adapters
```

**Portability**: EXTEND — Add Dimension-specific loading hooks (tools, workflows, metrics) to the existing `load_wad()` pipeline.

---

### Finding 1.2: Legacy `config_loader.py` — TOML-Based Config Layering

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/config_loader.py` (717 lines)
**Pattern**: Pydantic-validated config with LRU caching, dot-notation access, section validation
**Relevance**: Shows how the old system layered configs with validation — maps to PWAD config inheritance.

**Key Code** (lines 38-151):
```python
class XnaiConfig(BaseModel):
    """Complete Xoe-NovAi configuration schema."""
    metadata: MetadataConfig
    project: ProjectConfig
    models: ModelsConfig
    performance: PerformanceConfig
    server: ServerConfig
    redis: RedisConfig

# Config resolution: env var → repo root → module local → container default
def _default_config_candidates() -> list:
    candidates = []
    env_path = os.getenv("CONFIG_PATH")
    if env_path:
        candidates.append(Path(env_path))
    # ... fallback chain
```

**Portability**: REFERENCE — The Pydantic schema validation pattern maps to PWAD manifest validation. The fallback chain pattern (env → root → local → default) is useful for PWAD config resolution.

---

### Finding 1.3: Legacy `docker-compose.yml` — Service Orchestration as "WAD"

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/docker-compose.yml` (341 lines)
**Pattern**: Multi-service orchestration with resource limits, health checks, dependency chains
**Relevance**: Shows how services were composed — each service (rag, ui, crawler, curation_worker) is a proto-Dimension with its own config, resource limits, and health checks.

**Key Code** (lines 14-47):
```yaml
services:
  redis:
    image: redis:7.4.1
    healthcheck: ...
    deploy:
      resources:
        limits: { memory: 256M }
  
  rag:
    depends_on: { redis: { condition: service_healthy } }
    deploy:
      resources:
        limits: { memory: 4G, cpus: '2.0' }
    environment:
      - RAG_API_URL=http://rag:8000
      - LLM_MODEL_PATH=/models/local/all/gemma-3-4b-it-UD-Q5_K_XL.gguf
```

**Portability**: REFERENCE — The resource limits pattern maps to PWAD hardware budgets. The `depends_on` chain maps to PWAD dependency declarations.

---

### Finding 1.4: Legacy `[phase2.agents]` — Priority-Based Agent Registration

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/config.toml` (413 lines)
**Pattern**: TOML-based agent registry with priority, knowledge_path, and enabled flags
**Relevance**: DIRECT PREDECESSOR to the Dimension Registry — shows the original plan for composable agents.

**Key Code** (lines 315-328):
```toml
[phase2]
multi_agent_enabled = false
max_concurrent_agents = 4
agent_task_queue_size = 100

[phase2.agents]
coding_assistant = { enabled = false, priority = 1, knowledge_path = "/knowledge/coder" }
library_curator = { enabled = false, priority = 2, knowledge_path = "/knowledge/curator" }
writing_assistant = { enabled = false, priority = 3, knowledge_path = "/knowledge/editor" }
project_manager = { enabled = false, priority = 4, knowledge_path = "/knowledge/manager" }
self_learning = { enabled = false, priority = 5, knowledge_path = "/knowledge/learner" }
```

**Portability**: ADAPT — This is the EXACT pattern for PWAD Dimension declarations: `name = { enabled, priority, knowledge_path, tools, workflows }`.

---

## Category 2: Entity/Module/Plugin Registry Patterns

### Finding 2.1: `EntityRegistry` — The Current Engine's Entity Registry (PRIMARY)

**File**: `src/omega/oracle/entity_registry.py` (918 lines)
**Pattern**: YAML-backed CRUD with 3-tier resolution (name → slot → role), layered entity projection, lazy deletion, ZONEID integrity, dual-index lookup (name + capability)
**Relevance**: THE canonical entity system. PWAD Dimensions must register entities through this system.

**Key Code** (lines 120-167, 429-482):
```python
@dataclass
class Entity:
    name: str
    domains: List[str]
    model: str
    personality: str
    capabilities: List[str] = field(default_factory=list)
    slots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # WAD-defined, engine-agnostic
    wad_source: Optional[str] = None  # Which WAD loaded this entity
    priority: int = 0  # Layer priority for Shadow-Stacking

class EntityRegistry:
    def get(self, name: str) -> Optional[Entity]:
        """3-Tier Resolution: Direct name → Slot ID → Role"""
        # Tier 1: Direct entity match
        # Tier 2: Slot match (P1, P2, etc.)
        # Tier 3: Role match
```

**Portability**: EXTEND — Add `dimension` field to Entity dataclass for Dimension association. Add `tools` and `workflows` lists.

---

### Finding 2.2: `CapabilityRegistry` — Agent Skill Discovery

**File**: `src/omega/oracle/capability_registry.py` (127 lines)
**Pattern**: Publish/subscribe for agent capabilities — agents publish skills, others discover experts
**Relevance**: Maps directly to PWAD tool registration — each Dimension publishes its tools.

**Key Code** (lines 34-127):
```python
class CapabilityRegistry:
    async def publish(self, agent_id: str, capabilities: Dict[str, Any]) -> bool:
        """Publish capabilities for an agent."""
        self._registry[agent_id] = {
            "capabilities": capabilities,
            "updated_at": ...
        }

    async def discover_expert(self, query: str) -> Optional[str]:
        """Discover best agent for a task by keyword overlap + confidence."""
        for agent_id, data in self._registry.items():
            caps = data.get("capabilities", {})
            domains = set(" ".join(caps.get("domains", [])).lower().split())
            skills = set(" ".join(caps.get("skills", [])).lower().split())
            tools = set(" ".join(caps.get("tools", [])).lower().split())
            overlap = len(query_tokens & domains | skills | tools)
            score = overlap * confidence
```

**Portability**: EXTEND — Add `dimension_id` to capability entries. Add tool metadata (MCP bindings, resource requirements).

---

### Finding 2.3: `EntityAffinityResolver` — Model-Tier Routing

**File**: `src/omega/oracle/entity_affinity.py` (468 lines)
**Pattern**: YAML-backed routing rules with structured match conditions, tier fallback chains
**Relevance**: Maps to PWAD model routing — each Dimension can declare preferred models per tier.

**Key Code** (lines 100-166, 396-423):
```python
class MatchCondition:
    """Structured match conditions: domain, complexity_gt, online, requires, prompt_length_lt"""
    @staticmethod
    def evaluate(match_block: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """ALL conditions must pass (AND logic)."""
        for key, value in match_block.items():
            if not MatchCondition._evaluate_single(key, value, context):
                return False
        return True

class EntityAffinityResolver:
    def _match_rules(self, entity_config, context) -> str:
        """First routing rule that matches wins."""
        for rule in entity_config.get("routing_rules", []):
            if MatchCondition.evaluate(rule["match"], context):
                return rule["use"]  # Target tier
        return "local_fast"  # Default
```

**Portability**: ADAPT — The routing rule pattern applies to PWAD capability routing. The tier fallback chain (iris → local_fast → local_deep → cloud) is directly reusable.

---

### Finding 2.4: `EntityWorkspaceManager` — Per-Entity Scaffolding

**File**: `src/omega/oracle/entity_workspace.py` (571 lines)
**Pattern**: Auto-scaffold directories, soul.yaml, knowledge/, workspace/, INDEX.yaml for each entity
**Relevance**: Maps to PWAD workspace initialization — each Dimension needs its own workspace structure.

**Key Code** (lines 127-290):
```python
class EntityWorkspaceManager:
    @staticmethod
    def scaffold_workspace(name, archetype, slots) -> Path:
        """Create: data/entities/{name}/
        ├── soul.yaml (v6.1)
        ├── knowledge/
        │   └── INDEX.yaml
        ├── workspace/
        ├── memory/
        │   ├── approved_lessons.yaml
        │   ├── proposed_lessons.yaml
        │   └── sessions.yaml
        └── audit.log
        """
```

**Portability**: ADAPT — Extend to scaffold PWAD-specific directories (tools/, workflows/, metrics/).

---

### Finding 2.5: Legacy Persona JSON — Rich Entity Definitions

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/docs/personas/lilith.json` (62 lines)
**Pattern**: Rich persona with domain_expertise, personality_traits, value_system, voice_profile, query_modifiers, response_templates
**Relevance**: Shows the DEPTH of entity configuration the old system planned — maps to PWAD entity metadata.

**Key Code**:
```json
{
  "name": "Lilith",
  "archetype": "goddess",
  "domain_expertise": ["shadow_work", "feminine_power", "mysticism", ...],
  "personality_traits": { "mysterious": 0.95, "empowering": 0.9, ... },
  "voice_profile": {
    "piper_voice": "en_US-zara-medium",
    "prosody_modifiers": { "pause_after_period": 0.8, ... }
  },
  "query_modifiers": {
    "add_terms": ["shadow", "transformation", ...],
    "boost_terms": ["dark_goddess", "inner_alchemy", ...],
    "filter_out": ["patriarchal", "oppressive", ...]
  },
  "response_templates": { ... }
}
```

**Portability**: ADAPT — The `query_modifiers` pattern maps to PWAD query enhancement. The `domain_expertise` list maps to PWAD capability declarations.

---

## Category 3: WAD/Lump/Packaged Capability Patterns

### Finding 3.1: Current WAD Directory Structure (PRIMARY)

**Path**: `config/wads/`
**Pattern**: Two WADs exist: `_omega_default` (IWAD) and `arcana_novai` (PWAD)
**Relevance**: THE existing implementation. PWAD Dimensions must coexist with this structure.

**Current Structure**:
```
config/wads/
├── _omega_default/           # IWAD — The Company
│   ├── manifest.yaml         # name, version, entities[], startup
│   ├── entities.yaml         # Flat entity definitions
│   ├── entities/             # Per-entity YAML files
│   │   ├── kali.yaml
│   │   ├── maat.yaml
│   │   ├── lilith.yaml
│   │   ├── sysadmin.yaml
│   │   └── ... (24 entity files)
│   ├── hierarchy.yaml        # 5-tier org structure
│   ├── ethics.yaml           # Ethics framework
│   ├── roles.yaml            # Role definitions
│   ├── voices/               # Voice configs
│   │   └── jem.yaml
│   └── soul.template.yaml    # Soul template
│
├── arcana_novai/             # PWAD — Personal AI OS
│   ├── manifest.yaml         # type: iwad (should be pwad?)
│   ├── entities.yaml         # Flat entity definitions
│   ├── entities/             # Per-entity files
│   │   └── personal/
│   │       └── movie-expert.yaml
│   ├── hierarchy.yaml        # Entity hierarchy
│   ├── axioms.yaml           # Axiom definitions
│   ├── qliphoth.yaml         # Failure taxonomy
│   ├── spheres.yaml          # Kabbalistic spheres
│   ├── vault_schema.yaml     # Memory vault schema
│   └── world/                # World state data
│       └── core/
│           └── physics.yaml
```

**Portability**: EXTEND — Add `dimensions/` subdirectory to each WAD for Dimension declarations.

---

### Finding 3.2: WAD Manifest Schema

**File**: `config/wads/_omega_default/manifest.yaml` and `config/wads/arcana_novai/manifest.yaml`
**Pattern**: `wad:` wrapper with name, version, requires_engine, author, description, type, mode, entities[], voices{}, startup{}, dependencies[]
**Relevance**: THE manifest schema that PWAD Dimensions must extend.

**Key Code**:
```yaml
wad:
  name: "_omega_default — The Company"
  version: "1.0.0"
  requires_engine: ">=0.5.0"
  type: iwad
  mode: production
  startup:
    message: "The Company is loaded..."
  entities:
    - "default.yaml"
    - "kali.yaml"
    - "maat.yaml"
    # ... 15 entities
  voices:
    primary: "jem.yaml"
  dependencies: []
```

**Portability**: EXTEND — Add `dimensions:` section to manifest for PWAD dimension declarations:
```yaml
wad:
  dimensions:
    research_lab:
      enabled: true
      priority: 1
      entities: [jem, researcher, roc_racoon]
      tools: [library_fts_search, library_web_search, sovereign_search]
      workflows: [deep_research, legacy_mining]
      metrics: { queries_per_hour: 0, tokens_used: 0 }
```

---

### Finding 3.3: Entity File Schema (Current)

**File**: `config/wads/_omega_default/entities/roc_racoon.yaml`
**Pattern**: `entity:` wrapper with name, domains[], model, personality, temperature, context_window, pillars[], role, container
**Relevance**: THE entity definition schema. PWAD Dimensions reference entities by these files.

**Key Code**:
```yaml
entity:
  name: Roc Racoon
  domains:
    - mining
    - legacy
    - archaeology
    - patterns
    - extraction
    - search
  model: rocracoon-3b-instruct
  personality: |
    You are Roc Racoon, the Sovereign Miner...
  temperature: 0.4
  context_window: 8192
  pillars:
    - "P9: Coordination"
  role: Sovereign Miner — Reports to Lilith (CISO)
  container: false
```

**Portability**: EXTEND — Add `dimension:` and `tools:` fields:
```yaml
entity:
  name: Roc Racoon
  dimension: research_lab  # NEW: Dimension association
  tools:                   # NEW: Tool declarations
    - name: legacy_mine
      description: Mine legacy repos for patterns
      mcp_tool: omega-hub_library_fts_search
    - name: pattern_extract
      description: Extract reusable patterns from code
  workflows:               # NEW: Workflow participation
    - deep_research
    - legacy_archaeology
```

---

### Finding 3.4: Hierarchy YAML — Organizational Structure

**File**: `config/wads/_omega_default/hierarchy.yaml` (101 lines)
**Pattern**: 5-tier hierarchy (Field → Founder → Executive → Department → Keepers) with `governs`, `reports_to`, `governs_pillars` fields
**Relevance**: Maps to PWAD Dimension hierarchy — Dimensions can have their own internal structure.

**Key Code**:
```yaml
hierarchy:
  sophia:
    name: Sophia
    title: "The Containing Awareness"
    contains: [kali_founder, maat_cto, lilith_ciso]
  
  kali_founder:
    name: Kali
    title: "Founder"
    governs: [maat_cto, lilith_ciso]
  
  maat_cto:
    name: Ma'at
    title: "CTO"
    governs_pillars: [P1, P2, P3, P4, P5]
    governs_keepers: [sysadmin, datastore, buildmaster, bridge, sentinel]
```

**Portability**: ADAPT — Each PWAD Dimension can declare its own `dimension_hierarchy.yaml` for internal organization.

---

### Finding 3.5: Cvar Table — Named-Constant Registry

**File**: `src/omega/cvar_table.py` (588 lines)
**Pattern**: Typed, queryable, auditable constant table with namespace hierarchy (zoneid.*, config.*)
**Relevance**: Maps to PWAD configuration — Dimensions can register their own cvars under `config.dimension.{name}.*`.

**Key Code** (lines 159-442):
```python
CVAR_TABLE: Dict[str, CvarDef] = {
    "zoneid.entity": CvarDef("zoneid.entity", 0x1d4a12, "zoneid", ...),
    "config.entity.default": CvarDef("config.entity.default", "default", "str", ...),
    "config.gguf.n_ctx": CvarDef("config.gguf.n_ctx", 4096, "int", ...),
    "config.hivemind.enabled": CvarDef("config.hivemind.enabled", True, "bool", ...),
}
```

**Portability**: ADAPT — PWAD Dimensions register cvars under `config.dimension.{name}.*`:
```python
# Auto-registered when PWAD loads:
"config.dimension.research_lab.max_concurrent_queries": CvarDef(...),
"config.dimension.research_lab.default_search_depth": CvarDef(...),
```

---

## Category 4: Dimension/Domain Routing

### Finding 4.1: `Oracle` Routing (Current Engine)

**File**: `src/omega/oracle/oracle.py` (1308 lines)
**Pattern**: Intent detection → entity selection → model routing → speculative decode → response
**Relevance**: THE routing layer. PWAD Dimensions must integrate with this routing.

**Key Code** (lines 100-130):
```python
class Oracle:
    """Single-source-of-truth for query routing, speculative decoding, entity summoning."""
    
    # Routing flow:
    # 1. IntentMatcher detects intent (talk, summon, list, etc.)
    # 2. TriageRouter selects entity based on domain matching
    # 3. EntityAffinityResolver picks model+tier
    # 4. ModelGateway dispatches to provider
    # 5. Iris speculative decode for confidence check
```

**Portability**: EXTEND — Add Dimension-aware routing: detect query → match Dimension → select entity within Dimension.

---

### Finding 4.2: `TriageRouter` — Entity Selection

**File**: `src/omega/orchestration/triage_router.py` (referenced in oracle.py)
**Pattern**: Request classification and entity selection based on query analysis
**Relevance**: Maps to PWAD Dimension routing — TriageRouter should consider Dimension context.

**Key Code** (from oracle.py import):
```python
from ..orchestration.triage_router import TriageRouter, TriageRequest, TaskRequest, EntityContext, Constraints, SessionContext, ModelSelection
```

**Portability**: EXTEND — Add `dimension_id` to TriageRequest for Dimension-scoped routing.

---

### Finding 4.3: `SemanticRouter` — Query Routing

**File**: `src/omega/oracle/semantic_router.py` (referenced in oracle.py)
**Pattern**: Semantic analysis for query routing
**Relevance**: Maps to PWAD Dimension detection — SemanticRouter should detect which Dimension a query targets.

**Portability**: EXTEND — Add Dimension detection to semantic analysis.

---

### Finding 4.4: `find_by_domain()` — Domain Keyword Matching

**File**: `src/omega/oracle/entity_registry.py` (lines 767-805)
**Pattern**: Score entities by domain keyword overlap with query, prefer earliest mention
**Relevance**: THE domain matching algorithm. PWAD Dimensions use domains for capability routing.

**Key Code**:
```python
def find_by_domain(self, text: str) -> Optional[Entity]:
    """Score each entity by domain keyword overlap."""
    for key, layers in self._entities.items():
        projected = self._project_entity(active_layers)
        score = 0
        for keyword in projected.domains:
            if keyword.lower() in words:
                score += 1
        if score > best_score:
            best_entity = projected
    return best_entity
```

**Portability**: EXTEND — Add Dimension-level domain matching before entity-level matching.

---

### Finding 4.5: Legacy `crawl.sources` — Source Routing with Priorities

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/config.toml` (lines 182-189)
**Pattern**: Source-specific routing with priority and URL patterns
**Relevance**: Maps to PWAD tool routing — each Dimension can declare preferred tools with priority.

**Key Code**:
```toml
[crawl.sources]
gutenberg = { enabled = true, priority = 1, url_pattern = ".gutenberg.org" }
arxiv = { enabled = true, priority = 2, url_pattern = ".arxiv.org" }
pubmed = { enabled = true, priority = 3, url_pattern = ".nih.gov" }
youtube = { enabled = true, priority = 4, url_pattern = ".youtube.com" }
```

**Portability**: ADAPT — PWAD tool routing uses the same pattern:
```yaml
dimensions:
  research_lab:
    tools:
      library_fts_search: { enabled: true, priority: 1 }
      library_web_search: { enabled: true, priority: 2 }
      sovereign_search: { enabled: true, priority: 3 }
```

---

## Category 5: Workbench/Project Management Code

### Finding 5.1: Workbench Database (Referenced in Master Synthesis)

**Path**: `data/workbench/workbench.db` (SQLite)
**Pattern**: 21 projects, 57 items, 10 decisions, 22 artifacts tracked in SQLite with views
**Relevance**: Maps to PWAD Dimension metrics and project tracking.

**Key SQL Views** (from Master Synthesis):
```sql
-- Project summary
SELECT name, status, priority, total_tasks, tasks_done, tasks_blocked 
FROM v_project_summary ORDER BY priority;

-- Mining pipeline
SELECT * FROM v_mining_pipeline;

-- P0 tasks
SELECT id, title FROM work_items 
WHERE priority='P0' AND status='backlog' 
ORDER BY workstream;
```

**Portability**: REFERENCE — PWAD Dimensions can expose their own metrics tables.

---

### Finding 5.2: Decision Logging (PIVOT_LOG.md)

**Path**: `docs/decisions/PIVOT_LOG.md` (227 decisions, D1-D231)
**Pattern**: Immutable decision log with context, decision, rationale, and status
**Relevance**: Maps to PWAD Dimension decision tracking — each Dimension logs its architectural decisions.

**Portability**: REFERENCE — PWAD Dimensions can have their own `decisions.yaml` files.

---

### Finding 5.3: Hivemind Coordination — Cross-Agent Awareness

**File**: `mcp_servers/omega_hub/` (referenced in oracle.py)
**Pattern**: 6 MCP tools for cross-agent coordination (post_context, get_awareness, heartbeat, get_live_feed, get_workspace_lock, acknowledge)
**Relevance**: Maps to PWAD Dimension coordination — Dimensions use Hivemind for inter-Dimension communication.

**Key Code** (from omega-hub tools):
```python
# Hivemind tools:
hivemind_post_context()    # Announce presence and status
hivemind_get_awareness()   # Check who's active
hivemind_heartbeat()       # Stay alive
hivemind_workspace_lock()  # Claim domain
```

**Portability**: EXTEND — Add Dimension-aware awareness (which Dimensions are active).

---

### Finding 5.4: `SovereignAuditLog` — Modification Tracking

**File**: `src/omega/oracle/entity_workspace.py` (lines 92-108)
**Pattern**: Immutable audit log for all workspace modifications with timestamp and action
**Relevance**: Maps to PWAD Dimension audit trail — all Dimension state changes are logged.

**Key Code**:
```python
class SovereignAuditLog:
    def log(self, action: str, details: str):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entry = f"[{timestamp}] ACTION: {action} | DETAILS: {details}\n"
        with open(self.log_file, "a") as f:
            f.write(entry)
```

**Portability**: REUSE — Directly applicable to PWAD Dimension audit trails.

---

### Finding 5.5: Legacy `dependencies.py` — Singleton Resource Management

**File**: `/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/app/XNAi_rag_app/dependencies.py` (738 lines)
**Pattern**: Singleton pattern for Redis, HTTP client, LLM, embeddings, vectorstore with retry decorators
**Relevance**: Maps to PWAD Dimension resource management — shared resources (Redis, HTTP) are singletons.

**Key Code**:
```python
# Global singletons
_redis_client: Optional[Any] = None
_http_client: Optional[httpx.AsyncClient] = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host=..., port=..., ...)
    return _redis_client

@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))
def get_llm(model_path=None, **kwargs) -> LlamaCpp:
    """Initialize LLM with retry logic."""
```

**Portability**: ADAPT — PWAD Dimensions use shared resource singletons from the IWAD core.

---

## Synthesis: What the PWAD Schema Needs

Based on all 21 findings, the PWAD Schema and Dimension Registry should:

### 1. Extend `WADLoader` (Finding 1.1)
- Add `dimensions/` subdirectory loading
- Add dimension manifest validation
- Add dimension tool/workflow registration

### 2. Extend `EntityRegistry` (Finding 2.1)
- Add `dimension` field to Entity dataclass
- Add `tools` and `workflows` lists to Entity
- Add Dimension-scoped entity lookup

### 3. Extend `CapabilityRegistry` (Finding 2.2)
- Add `dimension_id` to capability entries
- Add tool metadata (MCP bindings, resource requirements)
- Add Dimension-aware discovery

### 4. Extend `cvar_table` (Finding 3.5)
- Add `config.dimension.{name}.*` namespace
- Auto-register PWAD-specific cvars on load

### 5. Extend Routing (Findings 4.1-4.5)
- Add Dimension detection to TriageRouter
- Add Dimension-scoped entity matching
- Add Dimension priority to routing rules

### 6. New: `DimensionRegistry` (Synthesis)
```python
@dataclass
class Dimension:
    name: str
    description: str
    priority: int
    entities: List[str]
    tools: List[Dict[str, Any]]
    workflows: List[str]
    metrics: Dict[str, Any]
    dependencies: List[str]  # Other dimensions
    enabled: bool = True

class DimensionRegistry:
    """Loads, validates, and manages PWAD Dimensions."""
    
    async def load_dimension(self, dimension_path: Path) -> Dimension:
        """Load a dimension from its manifest."""
    
    def get_dimension(self, name: str) -> Optional[Dimension]:
        """Get a dimension by name."""
    
    def discover_dimension(self, query: str) -> Optional[Dimension]:
        """Find the best dimension for a query."""
    
    def list_active(self) -> List[Dimension]:
        """List all enabled dimensions."""
```

### 7. New: `DimensionManifest` Schema (YAML)
```yaml
dimension:
  name: "research_lab"
  description: "Deep research, library search, legacy mining"
  version: "1.0.0"
  priority: 1
  
  entities:
    - jem
    - researcher
    - roc_racoon
  
  tools:
    - name: library_fts_search
      mcp_tool: omega-hub_library_fts_search
      priority: 1
      description: "Full-text search across library"
    - name: library_web_search
      mcp_tool: omega-hub_library_web_search
      priority: 2
      description: "Web search via Sovereign Search pipeline"
    - name: sovereign_search
      mcp_tool: omega-hub_sovereign_search
      priority: 3
      description: "Deep research with tiered extraction"
  
  workflows:
    - deep_research
    - legacy_archaeology
    - pattern_extraction
  
  hardware_budget:
    max_ram_mb: 4096
    max_cpu_threads: 4
    preferred_model_tier: local_fast
  
  dependencies: []
  
  metrics:
    queries_per_hour: 0
    tokens_used: 0
    avg_latency_ms: 0
```

---

## Next Steps

1. **Create `src/omega/oracle/dimension_registry.py`** — New module following EntityRegistry patterns
2. **Create `src/omega/oracle/dimension_loader.py`** — Extend WADLoader for dimension loading
3. **Add `dimension` field to Entity dataclass** — Backward-compatible with default=None
4. **Create `config/wads/_omega_default/dimensions/`** — Default dimension definitions
5. **Extend `cvar_table.py`** — Add `config.dimension.*` namespace
6. **Extend `triage_router.py`** — Add dimension-aware routing
7. **Write tests** — Follow existing test patterns in `tests/`

---

*🔱 OMEGA ⬡ ROC_RACOON ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_mining ⬡ PWAD-SCHEMA-MINING-COMPLETE*
