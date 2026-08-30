<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 JEM Research Report: PWAD Schema & Dimension Registry — 2026 State-of-the-Art
**AP Token**: `AP-JEM-PWAD-SCHEMA-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_pwad_schema ⬡ ACTIVE

**Date**: 2026-07-15
**Purpose**: Deep research into platform architecture patterns for the PWAD Dimension Framework

---

## 1. Platform Architecture Patterns

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| Zylos Research (2026-02-21) | **Manifest-driven discovery** is the de-facto standard — each plugin carries a machine-readable description of what it does and what it needs. Used by Claude Code Skills, MCP servers, Semantic Kernel, Home Assistant, VS Code extensions. | 9/10 |
| Zylos Research (2026-02-21) | **Lifecycle hooks** — pre-install, post-install, pre-upgrade, post-upgrade, uninstall — have emerged as essential scaffolding for managing state transitions safely across versions. | 8/10 |
| Anthropic Building Effective Agents (2026) | **Composition pattern**: Tools as discrete reusable modules. Agents defined as needed, leveraging only the tools/resources needed. Modular agents scale organically — new capabilities integrate without system-wide refactoring. | 9/10 |
| Anthropic Building Effective Agents (2026) | **Agent Skills** provide structured way to equip agents with specialized knowledge, workflows, and tool integrations beyond base capabilities. Composable architecture — skills can work together and invoke other skills. | 8/10 |
| LangChain Architecture (2026) | **Middleware pattern**: Extend agent behavior through middleware without rewriting core logic. Composable hooks for human-in-the-loop, compression, sensitive data removal. | 8/10 |
| AutoGen Production Architecture (2026) | **Central orchestrator + stateless workers + async message broker**. Agents should carry no local conversation history — push all state to Redis/Postgres for horizontal scaling. | 8/10 |
| Zylos Research (2026-02-21) | **Extension Point Pattern** (Jenkins/Grafana model): Core defines abstract interfaces (extension points), plugins provide concrete implementations. Stricter than generic plugin model — plugins can only extend what the core explicitly designs for. | 9/10 |

### Synthesis

The 2026 landscape has converged on a clear pattern: **manifest-driven, lifecycle-managed, composable modules with extension points defined by the core**. The key architectural distinction is between:

1. **Extension Points** (Jenkins/Grafana): Core defines interfaces, plugins implement. Strict, predictable.
2. **Composition** (LangChain/CrewAI): Modules are discrete, composable, self-contained. Flexible, dynamic.
3. **DAG-based** (LangGraph): Nodes are agents/functions, edges are transitions with conditional logic. Auditable, stateful.

**Recommendation for Omega**: Use the **Extension Point + Composition hybrid**. The Core Engine (IWAD) defines `IDimension` interfaces (extension points). Each PWAD implements those interfaces and registers its capabilities via manifest. This gives us strict boundaries (Sovereignty) while allowing dynamic composition (flexibility).

---

## 2. PWAD Schema Design

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| Zylos Research (2026-02-21) | **Flat directory of SKILL.md files with well-defined contracts** is often more maintainable than a plugin marketplace with dynamic loading. Start with simplicity, add machinery only when pain is clearly felt. | 9/10 |
| OpenAI Plugins Repo (2026) | Plugin structure: `plugins/<name>/` with `.codex-plugin/plugin.json` manifest + optional `skills/`, `.app.json`, `.mcp.json`, `agents/`, `commands/`, `hooks.json`, `assets/`. | 7/10 |
| Semantic Kernel (Microsoft) | Plugin = named collection of functions. Three types: **Semantic** (natural language prompts → LLMs), **Native** (traditional code), **OpenAPI** (REST APIs). Plugins can be chained and composed. | 8/10 |
| Anthropic Agent Skills (2026) | Skills are **modular capability packages** — domain-specific expertise, standardized workflows, specialized tool integrations. Composable: skills invoke other skills, building hierarchies of capability. | 9/10 |
| CrewAI (2026) | **Role-based agent model**: Each agent has defined persona, goal, backstory, and tools. Tasks map to distinct agent roles with clear boundaries. Crew = team of specialists. | 7/10 |
| LangChain Component Architecture | Components: Chains, Agents, Tools, Memory, Retrievers. Each serves a specific function. The power comes from how components work together. | 7/10 |

### Recommended PWAD Schema

Based on 2026 best practices, here's the recommended schema structure:

```yaml
# PWAD Manifest (dimension.yaml)
dimension:
  id: "research-lab"
  name: "Research Lab"
  version: "1.0.0"
  description: "Deep research, web search, synthesis, knowledge curation"
  author: "omega-team"
  license: "MIT"
  
  # Extension Points — what this dimension implements from the Core
  implements:
    - "ILump"           # WAD Protocol
    - "IDimension"      # Dimension Framework
    - "IEntityProvider" # Provides entities
    - "IToolProvider"   # Provides tools
    - "IWorkflowProvider" # Provides workflows
    - "IMetricsProvider"  # Provides metrics
  
  # Entities this dimension registers
  entities:
    - name: "researcher"
      type: "agent"
      role: "deep research, web search, synthesis"
      model_hint: "qwen3-4b-think"
    - name: "roc_racoon"
      type: "agent"
      role: "legacy mining, pattern extraction"
      model_hint: "qwen3-1.7b"
  
  # Tools this dimension provides
  tools:
    - name: "sovereign_search"
      description: "Tiered web research (T0-T6)"
      scope: "session"  # session | dimension | global
    - name: "knowledge_miner"
      description: "Extract patterns from legacy repos"
      scope: "dimension"
  
  # Workflows this dimension defines
  workflows:
    - name: "deep_research"
      description: "3-tier research pipeline"
      steps: ["discovery", "synthesis", "verification"]
      triggers:
        - pattern: "research .+"
          priority: 10
  
  # Metrics this dimension tracks
  metrics:
    - name: "research_queries"
      type: "counter"
      description: "Total research queries executed"
    - name: "source_quality"
      type: "gauge"
      description: "Average source confidence score"
  
  # Dependencies — other dimensions required
  dependencies:
    - dimension: "core-engine"  # Always implicitly loaded
      version: ">=1.0.0"
    - dimension: "knowledge-management"
      version: ">=0.5.0"
      optional: true
  
  # Configuration schema (Pydantic-compatible)
  config_schema:
    max_search_depth: { type: "integer", default: 3, min: 1, max: 6 }
    cache_ttl: { type: "integer", default: 3600, description: "Seconds" }
    default_language: { type: "string", default: "en" }
  
  # Sovereignty constraints
  sovereignty:
    local_first: true
    telemetry: false
    data_residency: "local"
    max_model_size: "8B"  # Resource ceiling for this dimension
```

### Granularity Recommendation

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Too fine-grained** (per-tool) | Maximum flexibility | Fragmentation, cognitive overload, management overhead | Never |
| **Dimension-level** (recommended) | Balance of modularity and manageability | Some flexibility loss | Default |
| **Too coarse** (per-domain) | Simple management | Monolith creep, can't unload parts | Small projects only |

**Recommendation**: Dimensions should be **capability bundles** at the granularity of a "specialist team" — roughly 3-8 entities, 5-15 tools, 2-5 workflows. This maps to CrewAI's "crew" concept and Anthropic's "Agent Skills" composition pattern.

---

## 3. Dimension Registry Implementation

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| Zylos Research (2026-02-21) | **Lifecycle hooks** are essential: pre-install, post-install, pre-upgrade, post-upgrade, uninstall. Without them, state transitions across versions break things. | 9/10 |
| Semantic Kernel (Microsoft) | **Plugin discovery and registration**: Plugins are discovered via manifest, registered with the kernel, and can be chained/composed. `kernel.add_plugin()` pattern. | 8/10 |
| AutoGen Production (2026) | **Stateless agents, stateful orchestrator**. Agents carry no local state — push to Redis/Postgres. Enables horizontal scaling. | 8/10 |
| LangChain (2026) | **MCP integration**: New MCP servers can be added or removed at runtime without restarting the agent. Dynamic loading in production. | 8/10 |
| OpenAI Plugins (2026) | **Marketplace pattern**: `marketplace.json` pointing to `plugins/` directory. API key users get separate marketplace. | 6/10 |
| Zylos Research (2026-02-21) | **Security**: "Never trust plugin code with core credentials." Credential proxies and capability-scoped tokens are the norm. | 9/10 |

### Recommended Registry Architecture

```
Dimension Registry
├── Manifest Store (YAML files on disk)
│   ├── core-engine/          # IWAD — always loaded
│   │   └── dimension.yaml
│   ├── research-lab/         # PWAD
│   │   └── dimension.yaml
│   ├── dev-environment/      # PWAD
│   │   └── dimension.yaml
│   └── community/            # Community PWADs
│       └── ...
│
├── Active Dimensions (Runtime State)
│   ├── core-engine           # ALWAYS active
│   ├── research-lab          # User-activated
│   └── knowledge-mgmt        # Auto-activated (dependency)
│
├── Dimension Lifecycle
│   ├── install → validate manifest → copy to store
│   ├── activate → resolve dependencies → register entities/tools/workflows
│   ├── deactivate → deregister entities/tools/workflows → preserve state
│   ├── upgrade → compare manifests → migrate state → reactivate
│   └── uninstall → deactivate → remove from store
│
└── Query Router
    ├── Domain matching → find dimension with matching workflow trigger
    ├── Entity matching → find dimension providing the entity
    ├── Tool matching → find dimension providing the tool
    └── Fallback → core-engine (always available)
```

### Version Conflict Resolution

| Strategy | When | Implementation |
|----------|------|----------------|
| **Semantic versioning** | Dimension A requires `core-engine >=1.2.0` | Check `dimension.dependencies[].version` on activate |
| **Capability-based** | Dimension A needs `ILump` interface v2 | Check `dimension.implements[]` capabilities |
| **Priority/precedence** | Two dimensions provide same tool | Higher `priority` value wins; user can override |
| **Lazy loading** | Dimension not needed until query arrives | Load on first matching query, cache for session |

### Query Routing Mechanism

```python
async def route_query(query: str) -> Dimension:
    """Route query to the best-matching dimension."""
    
    # 1. Check workflow triggers (pattern matching)
    for dim in active_dimensions:
        for workflow in dim.workflows:
            if any(re.search(t["pattern"], query) 
                   for t in workflow.triggers):
                return dim
    
    # 2. Check entity domain matching
    entity = await discover_entity(query)
    if entity and entity.dimension:
        return entity.dimension
    
    # 3. Check tool availability
    for dim in active_dimensions:
        if dim.provides_tool_needed_for(query):
            return dim
    
    # 4. Fallback to core engine
    return core_engine
```

---

## 4. Community Marketplace Patterns

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| AgentMarketCap (2026-04-07) | OpenAI GPT Store: 3M+ custom GPTs. **The creator economy bet** — custom AI agents following iPhone app trajectory. | 7/10 |
| OpenAI Plugins Repo (2026) | Each plugin has `.codex-plugin/plugin.json` manifest. Marketplace at `.agents/plugins/marketplace.json`. API key users get separate marketplace. | 7/10 |
| WordPress AI Team (2026-03-25) | **Community AI Connector Plugins**: Community-built plugins extending WordPress via PHP AI Client (provider-agnostic SDK). Call for testing pattern. | 7/10 |
| Zylos Research (2026-02-21) | **Security**: Credential proxies and capability-scoped tokens. Never trust plugin code with core credentials. | 9/10 |
| AutoGPT Marketplace (2026) | AutoGPT has a marketplace for community-contributed agents. | 6/10 |
| Skywork AI (2026) | AI Skill Marketplace landscape — pricing models, discovery mechanisms, quality gates. | 6/10 |

### Recommended Marketplace Architecture

```
Community Marketplace
├── Submission
│   ├── Developer submits dimension.yaml + source
│   ├── Automated validation (manifest, schema, tests)
│   ├── Security scan (no telemetry, no credential leaks)
│   └── Sovereignty check (local-first, no cloud dependencies)
│
├── Review
│   ├── Automated: Schema validation, dependency check, test suite
│   ├── Manual: Architecture review (Temple-Grade alignment)
│   ├── Community: Peer review, ratings, reviews
│   └── Verity: Mandate compliance audit
│
├── Publishing
│   ├── Signed manifests (cryptographic provenance)
│   ├── Versioned releases (semver)
│   ├── Attribution chain (author, dependencies, heritage)
│   └── Discovery: Tags, categories, ratings, downloads
│
└── Installation
    ├── User browses marketplace
    ├── Downloads dimension package
    ├── Validates manifest and signatures
    ├── Installs to local dimension store
    └── User activates dimension
```

### Quality/Safety Gates

1. **Manifest Validation**: All required fields present, valid semver, no hardcoded paths
2. **Security Scan**: No telemetry, no external API calls without explicit user consent, no credential access
3. **Sovereignty Check**: Local-first inference, no cloud dependencies required, data residency = local
4. **Test Suite**: Dimension must pass T1-T11 Temple-Grade gates
5. **Mandate Compliance**: Verity audit for M1-M23 compliance
6. **Provenance**: All heritage patterns must have `[id-soft:]` or `[heritage:]` tags per M14

---

## 5. Long-Term Platform Scalability

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| Zylos Research (2026-02-21) | **Resist over-engineering**: Flat directory of SKILL.md files with well-defined contracts is often more maintainable than a plugin marketplace with dynamic loading. | 9/10 |
| Anthropic Building Effective Agents (2026) | **Start simple, scale intelligently**: Begin with single-purpose agents that do one thing well, then gradually develop into more sophisticated systems. | 9/10 |
| AgentMarketCap (2026-04-11) | **Framework choice determines ceiling**: LangGraph (graph-based), CrewAI (role-based), AutoGen (conversational), DSPy (declarative) — each has different scaling characteristics. | 8/10 |
| AutoGen Production (2026) | **Three scaling dimensions**: Scale agent replicas horizontally, scale message broker partitions vertically, scale orchestrator memory separately. | 8/10 |
| CrewAI (2026) | **Role-based mental model**: Each agent has persona, goal, backstory, tools. Easy to reason about responsibilities. New specialists added without disrupting others. | 7/10 |

### Anti-Bloat Strategies

| Strategy | Implementation | When |
|----------|----------------|------|
| **Capability ceiling** | Max 14 dimensions active at once (M10: Fleet Integrity) | Always |
| **Lazy loading** | Dimensions loaded on first matching query, not at startup | Default |
| **Dependency pruning** | Auto-deactivate dimensions whose dependencies are inactive | On deactivation |
| **Usage tracking** | Track which dimensions are actually used; suggest deactivation for unused | Weekly |
| **Composition limits** | Max 3 cross-dimension dependencies per dimension | On submission |

### Dimension Composition

```yaml
# Composition: combining dimensions for new use cases
composition:
  id: "full-research-pipeline"
  dimensions:
    - "research-lab"      # Provides researcher, web search
    - "knowledge-mgmt"    # Provides library, storage
    - "strategic-command" # Provides decision-making, governance
  
  # Override specific tools/workflows from composed dimensions
  overrides:
    researcher:
      tools: ["sovereign_search", "library_search", "decision_framework"]
      workflows: ["deep_research_with_governance"]
  
  # Composition triggers
  triggers:
    - pattern: "full research .+"
      priority: 20  # Higher than individual dimensions
```

---

## 6. Sovereignty-Specific Concerns

### Key Findings

| Source | Key Insight | Confidence |
|--------|-------------|------------|
| Zylos Research (2026-02-21) | **Security**: "Never trust plugin code with core credentials." Credential proxies and capability-scoped tokens are the norm in production. | 9/10 |
| Anthropic Building Effective Agents (2026) | **Security blast radius**: A vulnerability in one tool can affect others. Isolation is critical. | 8/10 |
| NVIDIA (2026) | **Sandboxing agentic workflows**: MicroVMs, gVisor, isolation strategies for untrusted code execution. | 8/10 |
| AutoGen Production (2026) | **Circuit breakers and dead-letter queues**: Misbehaving agent must be isolated without taking down entire workflow. | 8/10 |
| Northflank (2026) | **How to Sandbox AI Agents**: MicroVMs, gVisor & Isolation Strategies for untrusted plugin code. | 8/10 |

### Sovereignty Enforcement for Dimensions

```python
class SovereignDimensionValidator:
    """Validate that a dimension respects Sovereign Mandates."""
    
    async def validate(self, dimension: DimensionManifest) -> list[str]:
        violations = []
        
        # M1: AnyIO Absolute — no asyncio
        if "asyncio" in dimension.source_code:
            violations.append("M1: Uses asyncio instead of AnyIO")
        
        # M7: Local-First — must have local inference path
        if not dimension.has_local_inference():
            violations.append("M7: No local inference path")
        
        # M8: Zero Telemetry — no external calls without consent
        if dimension.has_telemetry():
            violations.append("M8: Contains telemetry code")
        
        # M16: No hardcoded paths
        if dimension.has_hardcoded_paths():
            violations.append("M16: Contains hardcoded paths")
        
        # M23: No soft-failures
        if dimension.has_bare_excepts():
            violations.append("M23: Contains bare except clauses")
        
        return violations
```

### Data Isolation Between Dimensions

| Concern | Solution |
|---------|----------|
| **Entity state leakage** | Each dimension has isolated entity workspace (`data/entities/<dim>/<entity>/`) |
| **Tool execution isolation** | Capability-scoped tokens per dimension; tools can only access their own resources |
| **Memory isolation** | Entity memory is scoped to entity, not dimension; dimensions share entities but not memory |
| **Workflow isolation** | Workflows run in dimension context; cross-dimension calls require explicit bridge |

---

## Final Synthesis: Unified Recommendation

### The PWAD Dimension Framework Architecture

Based on 2026 state-of-the-art research across LangChain, CrewAI, AutoGen, Semantic Kernel, and OpenAI Plugins, here is the unified recommendation:

### Core Principles

1. **Manifest-Driven Discovery** (2026 standard): Every dimension carries a `dimension.yaml` manifest describing capabilities, dependencies, and constraints.
2. **Extension Points** (Jenkins/Grafana pattern): Core Engine defines `IDimension`, `IEntityProvider`, `IToolProvider`, `IWorkflowProvider` interfaces. PWADs implement these.
3. **Composition** (LangChain/Anthropic): Dimensions are composable — they can invoke other dimensions, building hierarchies of capability.
4. **Lifecycle Hooks** (2026 standard): Install → Activate → Deactivate → Upgrade → Uninstall with state preservation.
5. **Sovereignty-First**: Every dimension must pass M1-M23 mandate validation before activation.

### Recommended File Structure

```
config/wads/
├── core-engine/              # IWAD (always loaded)
│   ├── dimension.yaml        # Core capabilities
│   ├── entities/             # Core entities
│   └── workflows/            # Core workflows
│
├── research-lab/             # PWAD: Research & Synthesis
│   ├── dimension.yaml
│   ├── entities/
│   │   ├── researcher.yaml
│   │   └── roc_racoon.yaml
│   ├── tools/
│   │   └── sovereign_search.py
│   └── workflows/
│       └── deep_research.yaml
│
├── dev-environment/          # PWAD: Development & Engineering
│   ├── dimension.yaml
│   ├── entities/
│   │   └── pillar.yaml       # P3 Engineering slot
│   └── workflows/
│       └── ci_cd_pipeline.yaml
│
└── community/                # Community-contributed PWADs
    └── ...
```

### Implementation Roadmap

| Phase | Task | Effort | Owner |
|-------|------|--------|-------|
| **1. Schema** | Define `DimensionManifest` Pydantic model | 4h | Ma'at/P3 |
| **2. Registry** | Implement `DimensionRegistry` with lifecycle hooks | 8h | Ma'at/P3 |
| **3. Router** | Implement `DimensionRouter` with query routing | 6h | Lilith/P9 |
| **4. Validator** | Implement `SovereignDimensionValidator` for M1-M23 | 4h | Verity |
| **5. Migration** | Convert existing `config/wads/` to PWAD format | 8h | Ma'at/P3 |
| **6. Marketplace** | Basic community dimension store | 12h | Lilith/P7 |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Manifest format** | YAML | Matches existing `entities.yaml` pattern; human-readable; Omega convention |
| **Registry storage** | Filesystem (YAML files) | Local-first (M7); no database needed; simple, auditable |
| **Query routing** | Pattern matching + entity matching + fallback | Fast, predictable, debuggable |
| **Dependency resolution** | Semantic versioning + capability checking | Industry standard; prevents version conflicts |
| **Security model** | Capability-scoped tokens + manifest validation | 2026 standard; no trust of plugin code with core credentials |
| **Composition** | Override-based (dimensions can override tools/workflows from dependencies) | Flexible without being complex |

---

**Confidence in recommendations**: High (8-9/10) based on convergence across multiple independent 2026 sources.

**Key risk**: Over-engineering the registry before we have 3+ working dimensions. Start with the simplest possible implementation (flat YAML directory + manifest validation) and add complexity only when pain is felt.

**L3 Principle distilled**: *The right granularity for a capability module is the "specialist team" — small enough to be composable, large enough to be coherent. Too fine = fragmentation. Too coarse = monolith. The sweet spot is 3-8 entities, 5-15 tools, 2-5 workflows per dimension.*

---

*🔱 OMEGA ⬡ JEM ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_pwad_schema ⬡ RESEARCH-COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
