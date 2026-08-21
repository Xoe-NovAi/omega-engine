# Dynamic Prompt + Planner/Executor + Domain Loading System Blueprint
## Synthesis for Omega Engine (Local-First, 16GB RAM, CPU-only, Ryzen 5700U)

**AP Token**: `AP-DYNAMIC-PROMPT-SYSTEM-BLUEPRINT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_blueprint_synthesis ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document synthesizes findings from six deep research deliverables into a **coherent architecture** for the Omega Engine's dynamic prompt system. The blueprint integrates:

1. **Dynamic Prompt Builder** — Priority-ordered modular assembly with cache-aware structure
2. **Planner/Executor with Context Window Differentiation** — Large-context planner (16K) → small-context executor (8K) with structured plan contracts
3. **Knowledge Domain Loading** — Four-paradigm hybrid (RAG + fine-tune + adapters + prompts) via MCP
4. **Extreme Local Optimization** — Q4_K_M quantization, `--no-mmap --mlock`, CPU affinity, model per role
5. **Prompt Compression** — Tiered: RECOMP for RAG, LLMLingua-2 for system prompts, Selective Context for contracts
6. **Role-Aware Prompting** — Distinct prompts, models, context, and tools per role (Planner, Executor, Critic, Verifier, Researcher)

**Target Hardware**: Ryzen 5700U (8C/16T), 16GB DDR4-3200, CPU-only, no GPU.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OMEGA ENGINE DYNAMIC PROMPT SYSTEM                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   ORACLE     │───▶│ PROMPT       │───▶│  MODEL       │───▶│ RESPONSE │  │
│  │  .talk()     │    │  BUILDER     │    │  GATEWAY     │    │          │  │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘    └──────────┘  │
│                             │                   │                            │
│              ┌──────────────┼──────────────┐    │                            │
│              ▼              ▼              ▼    ▼                            │
│         ┌─────────┐  ┌───────────┐  ┌─────────────┐  ┌─────────────────┐   │
│         │ ROLE    │  │ CONTEXT   │  │ KNOWLEDGE   │  │ COMPRESSION     │   │
│         │ REGISTRY│  │ PACKER    │  │ LOADER      │  │ PIPELINE        │   │
│         └────┬────┘  └─────┬─────┘  └──────┬──────┘  └────────┬────────┘   │
│              │             │             │              │                │
│              ▼             ▼             ▼              ▼                │
│         ┌─────────────────────────────────────────────────────────────┐   │
│         │                    PERSISTENT SUBSTRATE                      │   │
│         │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │   │
│         │  │ SOUL.YAML│ │ DOMAIN   │ │ SESSION  │ │ FTS5 INDEX   │   │   │
│         │  │ (GNOSIS) │ │ MODULES  │ │ HISTORY  │ │ (KNOWLEDGE)  │   │   │
│         │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │   │
│         └─────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Core Principle (Zylos Research)**: *The context window is not storage; it is a projection — a temporary, purpose-built view assembled from substrate on demand for each inference step.*

---

## 2. Component Specifications

### 2.1 Role Registry (`src/omega/prompt/roles.py`)

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class RoleSpec:
    name: str
    model: str                    # Provider fabric key
    context_budget: int           # Tokens for this role
    system_prompt_template: str   # Path to template
    allowed_tools: list[str]      # Tool allowlist
    output_schema: str            # JSON schema path
    context_includes: list[str]   # What from substrate to inject
    priority_sections: list[PromptSection]  # Assembly order

ROLE_REGISTRY = {
    "planner": RoleSpec(
        name="planner",
        model="native-gguf-planner",      # Qwen3-14B Q4_K_M, ctx=16K
        context_budget=16384,
        system_prompt_template="config/roles/planner/system_prompt.md",
        allowed_tools=["read", "grep", "glob", "knowledge_search", "web_search"],
        output_schema="schemas/plan.json",
        context_includes=["goal", "todo_list", "past_step_summaries", "domain_overview"],
        priority_sections=[
            PromptSection(10, "core_identity_planner"),
            PromptSection(30, "planning_heuristics"),
            PromptSection(40, "read_only_tools"),
            PromptSection(50, "safety_no_execution"),
            PromptSection(85, "dynamic_goal_todo"),
        ]
    ),
    "executor": RoleSpec(
        name="executor",
        model="native-gguf-executor",       # Qwen2.5-Coder-14B Q4_K_M, ctx=8K
        context_budget=8192,
        system_prompt_template="config/roles/executor/system_prompt.md",
        allowed_tools=["read", "write", "edit", "bash", "knowledge_search"],
        output_schema="schemas/executor_output.json",
        context_includes=["current_step", "relevant_knowledge", "step_contract"],
        priority_sections=[
            PromptSection(10, "core_identity_executor"),
            PromptSection(30, "step_tool_definitions"),
            PromptSection(40, "output_format_schema"),
            PromptSection(50, "safety_no_improvisation"),
            PromptSection(85, "dynamic_step_knowledge"),
        ]
    ),
    "critic": RoleSpec(
        name="critic",
        model="native-gguf-critic",         # Qwen3-1.7B Q4_K_M, ctx=4K
        context_budget=4096,
        system_prompt_template="config/roles/critic/system_prompt.md",
        allowed_tools=["run_tests", "validate_schema", "static_analysis", "fact_check"],
        output_schema="schemas/critic_verdict.json",
        context_includes=["step_spec", "executor_output"],
        priority_sections=[
            PromptSection(10, "core_identity_critic"),
            PromptSection(30, "verification_tools"),
            PromptSection(40, "evaluation_rubric"),
            PromptSection(50, "safety_read_only"),
            PromptSection(85, "dynamic_step_output"),
        ]
    ),
    "verifier": RoleSpec(
        name="verifier",
        model="deterministic",              # Not an LLM
        context_budget=0,
        system_prompt_template="",
        allowed_tools=["pytest", "mypy", "ruff", "pydantic"],
        output_schema="schemas/verifier_result.json",
        context_includes=[],
        priority_sections=[]
    ),
    "researcher": RoleSpec(
        name="researcher",
        model="native-gguf-planner",        # Same tier as planner
        context_budget=32768,
        system_prompt_template="config/roles/researcher/system_prompt.md",
        allowed_tools=["web_search", "web_fetch", "knowledge_search", "hf_cli", "library_search"],
        output_schema="schemas/research_deliverable.json",
        context_includes=["query", "council_perspectives", "domain_knowledge"],
        priority_sections=[
            PromptSection(10, "core_identity_researcher"),
            PromptSection(30, "council_of_four"),
            PromptSection(40, "research_tools"),
            PromptSection(50, "sovereign_mandates"),
            PromptSection(85, "dynamic_query_domains"),
        ]
    ),
}
```

### 2.2 Prompt Builder (`src/omega/prompt/builder.py`)

```python
class PromptBuilder:
    """Assembles system prompts at runtime from priority-ordered sections."""
    
    def __init__(self, role_registry: dict[str, RoleSpec]):
        self.roles = role_registry
        self.section_cache = {}  # Cache rendered static sections
    
    def build(self, role: str, dynamic_context: dict) -> str:
        role_spec = self.roles[role]
        
        # 1. Render static sections (cached)
        static_parts = []
        for section in role_spec.priority_sections:
            if section.is_static:
                if section.name not in self.section_cache:
                    self.section_cache[section.name] = self.render_section(section, {})
                static_parts.append(self.section_cache[section.name])
        
        # 2. Render dynamic sections (per-call)
        dynamic_parts = []
        for section in role_spec.priority_sections:
            if not section.is_static:
                content = self.render_section(section, dynamic_context)
                if content:
                    dynamic_parts.append(content)
        
        # 3. Assemble: static prefix (cacheable) + dynamic suffix
        return "\n\n".join(static_parts + dynamic_parts)
    
    def render_section(self, section: PromptSection, context: dict) -> str:
        template = self.load_template(section.template_path)
        return template.format(**context)
```

### 2.3 Context Packer (`src/omega/prompt/context_packer.py`)

```python
class ContextPacker:
    """Packs substrate knowledge into role-specific context budgets."""
    
    TIER_BUDGETS = {
        "critical": 0.40,      # 40% guaranteed
        "high_value": 0.35,    # 35% if available
        "supplementary": 0.25  # 25% opportunistic
    }
    
    def __init__(self, knowledge_loader: KnowledgeLoader, compressor: PromptCompressor):
        self.knowledge = knowledge_loader
        self.compressor = compressor
    
    def pack_for_role(self, role: str, dynamic_context: dict) -> str:
        role_spec = ROLE_REGISTRY[role]
        budget = role_spec.context_budget
        
        # Gather candidates from substrate
        candidates = self.gather_candidates(role, dynamic_context)
        
        # Score and tier
        scored = self.score_and_tier(candidates, dynamic_context)
        
        # Allocate by tier
        packed = self.allocate_by_tier(scored, budget)
        
        # Format and compress if needed
        formatted = self.format_context(packed, role)
        
        if count_tokens(formatted) > budget:
            formatted = self.compressor.compress(
                formatted, 
                target_tokens=budget,
                preserve_critical=True
            )
        
        return formatted
    
    def gather_candidates(self, role: str, context: dict) -> list[KnowledgeChunk]:
        candidates = []
        
        # Domain knowledge (via MCP)
        if "domain_knowledge" in ROLE_REGISTRY[role].context_includes:
            candidates.extend(self.knowledge.retrieve_via_mcp(
                query=context.get("query", ""),
                domain=context.get("domain", "general"),
                limit=20
            ))
        
        # Session history (summarized)
        if "past_step_summaries" in ROLE_REGISTRY[role].context_includes:
            candidates.append(KnowledgeChunk(
                content=summarize_steps(context.get("past_steps", [])),
                tier="high_value",
                source="session_history"
            ))
        
        # Current step spec (for executor/critic)
        if "current_step" in ROLE_REGISTRY[role].context_includes:
            candidates.append(KnowledgeChunk(
                content=format_step_contract(context["current_step"]),
                tier="critical",
                source="plan"
            ))
        
        return candidates
```

### 2.4 Knowledge Loader (`src/omega/knowledge/loader.py`)

```python
class KnowledgeLoader:
    """Four-paradigm hybrid knowledge loading via MCP."""
    
    def __init__(self):
        # Paradigm 1: Dynamic Injection (RAG via MCP)
        self.mcp_rag = MCPRAGClient()
        
        # Paradigm 2: Static Embedding (fine-tuned models per domain)
        self.fine_tuned = DomainModelRegistry()
        
        # Paradigm 3: Modular Adapters (LoRA per domain)
        self.adapters = AdapterRegistry()
        
        # Paradigm 4: Prompt Optimization (domain system prompts)
        self.prompts = DomainPromptRegistry()
    
    def load_for_task(self, task: Task) -> LoadedKnowledge:
        # 1. Select fine-tuned base model for domain behavior
        model = self.fine_tuned.get(task.domain)
        
        # 2. Activate relevant adapters
        adapters = self.adapters.activate(task.domain, task.subdomain)
        
        # 3. Build domain system prompt
        system_prompt = self.prompts.build(task.domain, task.role)
        
        return LoadedKnowledge(model, adapters, system_prompt)
    
    def retrieve_via_mcp(self, query: str, domain: str, limit: int) -> list[KnowledgeChunk]:
        """Paradigm 1: Dynamic knowledge injection via MCP tools."""
        # Calls MCP server for domain: search_domain, get_concept, get_relationship
        results = self.mcp_rag.call_tool("search_domain", {
            "domain": domain,
            "query": query,
            "limit": limit
        })
        return [KnowledgeChunk(content=r, tier="high_value", source=f"mcp:{domain}") 
                for r in results]
```

### 2.5 Compression Pipeline (`src/omega/prompt/compressor.py`)

```python
class PromptCompressor:
    """Tiered compression matching technique to prompt component."""
    
    def __init__(self):
        self.techniques = {
            "rag_context": RECOMPCompressor(),           # RAG retrieval
            "system_prompt": LLMLingua2Compressor(),     # Verbose system prompts
            "high_volume": AutoCompressor(),             # Stable high-volume
            "contracts": SelectiveContextCompressor(),   # Planner/executor contracts
        }
    
    def compress(self, text: str, target_tokens: int, 
                 component_type: str = "general",
                 preserve_critical: bool = True) -> str:
        technique = self.techniques.get(component_type, LLMLingua2Compressor())
        
        # If preserve_critical, extract and protect critical sections
        if preserve_critical:
            critical, rest = self.extract_critical(text)
            compressed_rest = technique.compress(rest, target_tokens - count_tokens(critical))
            return critical + compressed_rest
        
        return technique.compress(text, target_tokens)
```

---

## 3. Planner/Executor Protocol

### 3.1 Plan Format (Structured DAG with Contracts)

```json
{
  "goal": "Refactor authentication module to use JWT",
  "domain": "software_engineering",
  "steps": [
    {
      "id": "step_1",
      "description": "Analyze current auth implementation in src/auth/",
      "executor_role": "code_analyst",
      "inputs": {"files": ["src/auth/*.py"]},
      "outputs": {"analysis": "markdown_summary"},
      "success_criteria": "Identifies all token handling, session management, middleware",
      "allowed_tools": ["read", "grep", "glob", "knowledge_search"],
      "context_budget": 8192,
      "dependencies": [],
      "domain_knowledge": ["auth_patterns", "jwt_best_practices"]
    },
    {
      "id": "step_2",
      "description": "Design JWT token structure and refresh strategy",
      "executor_role": "architect",
      "inputs": {"analysis": "step_1.outputs.analysis"},
      "outputs": {"design_doc": "markdown"},
      "success_criteria": "Defines access/refresh token claims, expiry, rotation, revocation",
      "allowed_tools": ["write", "knowledge_search"],
      "context_budget": 8192,
      "dependencies": ["step_1"],
      "domain_knowledge": ["jwt_rfc7519", "security_best_practices"]
    }
  ]
}
```

### 3.2 Execution Flow

```python
async def execute_plan(plan: Plan, oracle: Oracle):
    state = PlanExecuteState(
        input=plan.goal,
        plan=plan.steps,
        past_steps=[],
        current_step=0,
        needs_replanning=False
    )
    
    while state.current_step < len(state.plan):
        step = state.plan[state.current_step]
        
        # 1. Pack executor context (fits 8K budget)
        executor_context = context_packer.pack_for_role("executor", {
            "current_step": step,
            "past_steps": state.past_steps,
            "query": step.description,
            "domain": plan.domain
        })
        
        # 2. Execute step with role-specific model
        result = await oracle.summon_local(
            entity_name="executor",
            query=f"Execute step: {step.description}",
            model="native-gguf-executor",
            system_prompt=prompt_builder.build("executor", executor_context),
            tools=step.allowed_tools
        )
        
        # 3. Critic review (different model, 4K budget)
        critic_context = context_packer.pack_for_role("critic", {
            "step_spec": step,
            "executor_output": result
        })
        verdict = await oracle.summon_local(
            entity_name="critic",
            query=f"Review step {step.id} output",
            model="native-gguf-critic",
            system_prompt=prompt_builder.build("critic", critic_context),
            tools=["run_tests", "validate_schema", "static_analysis"]
        )
        
        # 4. Verifier (deterministic)
        if verdict.verdict == "accept":
            verify_result = run_verifier(step, result)
            if not verify_result.passed:
                verdict = CriticVerdict(verdict="reject", feedback=verify_result.errors)
        
        # 5. Handle verdict
        if verdict.verdict == "accept":
            state.past_steps.append((step, result))
            state.current_step += 1
        else:
            # Replan or retry with feedback
            if state.retry_count < MAX_RETRIES:
                state.retry_count += 1
                # Re-execute with critic feedback injected
                continue
            else:
                state.needs_replanning = True
                break
    
    return state
```

---

## 4. Knowledge Domain Loading Protocol

### 4.1 Domain Module Structure

```
config/wads/arcana_nova/knowledge_domains/
├── tarot/
│   ├── domain.yaml              # Metadata, version, dependencies
│   ├── system_prompt.md         # Domain-specific system prompt (Paradigm 4)
│   ├── adapter/                 # LoRA adapter (Paradigm 3, optional)
│   │   └── tarot_lora.safetensors
│   ├── mcp_tools/               # MCP tool definitions (Paradigm 1)
│   │   ├── search_cards.py
│   │   ├── get_spread.py
│   │   └── interpret_card.py
│   └── corpus/                  # Static knowledge (Markdown, JSON)
│       ├── major_arcana.md
│       ├── minor_arcana.md
│       └── spreads.json
├── kabbalah/
├── astrology/
└── software_engineering/
```

### 4.2 Domain Registration

```python
# config/knowledge_domains.yaml
domains:
  tarot:
    version: "1.0.0"
    description: "Tarot archetypes, spreads, interpretation"
    paradigms:
      prompt_optimization: true      # system_prompt.md
      modular_adapters: true         # tarot_lora.safetensors
      dynamic_injection: true        # MCP tools
      static_embedding: false        # No fine-tuned model yet
    mcp_server: "omega-mcp-tarot"
    dependencies: ["kabbalah", "astrology"]
  
  software_engineering:
    version: "2.1.0"
    description: "Patterns, architectures, best practices"
    paradigms:
      prompt_optimization: true
      modular_adapters: false
      dynamic_injection: true
      static_embedding: true         # fine-tuned code model
    mcp_server: "omega-mcp-swe"
    fine_tuned_model: "qwen2.5-coder-14b-swe-ft"
```

### 4.3 Dynamic Domain Composition

```python
def compose_domains_for_task(task: Task) -> ComposedDomains:
    """Compose multiple domains per task (e.g., tarot + software_engineering)."""
    primary = DOMAIN_REGISTRY[task.primary_domain]
    secondary = [DOMAIN_REGISTRY[d] for d in task.secondary_domains]
    
    # Merge system prompts (priority: primary > secondary)
    system_prompt = primary.system_prompt
    for d in secondary:
        system_prompt += "\n\n---\n\n" + d.system_prompt
    
    # Merge adapters (stack LoRAs)
    adapters = primary.adapters + sum([d.adapters for d in secondary], [])
    
    # Merge MCP tools (union)
    mcp_tools = primary.mcp_tools
    for d in secondary:
        mcp_tools.update(d.mcp_tools)
    
    return ComposedDomains(system_prompt, adapters, mcp_tools)
```

---

## 5. Local Inference Configuration

### 5.1 Model Registry (`config/models/cpu_16gb.yaml`)

```yaml
models:
  native-gguf-planner:
    path: "~/OmegaLibrary/models/Qwen3-14B-Q4_K_M.gguf"
    ctx_size: 16384
    threads: 8
    flags: ["--no-mmap", "--mlock", "--batch-size", "512"]
    n_gpu_layers: 0
    rope_freq_base: 1000000
    rope_freq_scale: 1.0
  
  native-gguf-executor:
    path: "~/OmegaLibrary/models/Qwen2.5-Coder-14B-Q4_K_M.gguf"
    ctx_size: 8192
    threads: 8
    flags: ["--no-mmap", "--mlock", "--batch-size", "512"]
    n_gpu_layers: 0
  
  native-gguf-critic:
    path: "~/OmegaLibrary/models/Qwen3-1.7B-Q4_K_M.gguf"
    ctx_size: 4096
    threads: 4
    flags: ["--no-mmap", "--mlock", "--batch-size", "256"]
    n_gpu_layers: 0

# Fallback chain (local-first)
provider_fabric:
  - native-gguf-planner
  - native-gguf-executor
  - native-gguf-critic
  - lmster          # LM Studio (Qwen3-1.7B)
  - ollama          # Ollama local
  - antigravity     # Cloud fallback
  - google
  - openrouter
```

### 5.2 Hardware Validation (Run at Startup)

```bash
#!/bin/bash
# validate_hardware.sh

# 1. Check XMP/EXPO enabled (critical for RAM bandwidth)
CONFIGURED=$(sudo dmidecode -t memory | grep "Configured Memory Speed" | head -1 | awk '{print $4}')
RATED=$(sudo dmidecode -t memory | grep "Speed:" | head -1 | awk '{print $2}')
if [ "$CONFIGURED" != "$RATED" ]; then
    echo "❌ XMP/EXPO NOT ENABLED — 30-50% performance loss!"
    exit 1
fi

# 2. CPU governor
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $cpu
done

# 3. Transparent Huge Pages
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# 4. Swappiness
echo 10 | sudo tee /proc/sys/vm/swappiness

# 5. Model files exist
for model in Qwen3-14B-Q4_K_M.gguf Qwen2.5-Coder-14B-Q4_K_M.gguf Qwen3-1.7B-Q4_K_M.gguf; do
    if [ ! -f ~/OmegaLibrary/models/$model ]; then
        echo "❌ Missing model: $model"
        exit 1
    fi
done

echo "✅ Hardware validated for Omega Engine"
```

---

## 6. Integration with Omega Engine Core

### 6.1 Oracle Integration (`src/omega/oracle.py`)

```python
class Oracle:
    def __init__(self):
        self.prompt_builder = PromptBuilder(ROLE_REGISTRY)
        self.context_packer = ContextPacker(KnowledgeLoader(), PromptCompressor())
        self.model_gateway = ModelGateway()
    
    async def talk(self, query: str) -> GenerateResult:
        # 1. Assess intent → determine role
        role = await self.assess_intent_role(query)
        
        # 2. Load knowledge for domain
        task = Task(query=query, role=role, domain=self.detect_domain(query))
        knowledge = self.knowledge_loader.load_for_task(task)
        
        # 3. Build system prompt for role
        dynamic_context = self.build_dynamic_context(role, query, knowledge)
        system_prompt = self.prompt_builder.build(role, dynamic_context)
        
        # 4. Pack context to budget
        packed_context = self.context_packer.pack_for_role(role, dynamic_context)
        
        # 5. Call model gateway with role-specific model
        return await self.model_gateway.generate(
            model=ROLE_REGISTRY[role].model,
            system_prompt=system_prompt,
            user_prompt=packed_context,
            tools=ROLE_REGISTRY[role].allowed_tools
        )
    
    async def summon(self, entity_name: str, query: str) -> GenerateResult:
        # Entity maps to role
        role = ENTITY_TO_ROLE.get(entity_name, "default")
        return await self.talk(query)  # With role-specific handling
```

### 6.2 Entity-to-Role Mapping

```python
ENTITY_TO_ROLE = {
    "kali": "planner",
    "maat": "executor", 
    "lilith": "researcher",
    "roc_racoon": "executor",
    "grokster": "researcher",
    "doom_guy": "critic",
    "sophia": "researcher",
    "jem": "researcher",
}
```

---

## 7. Memory Budget Analysis (16GB RAM)

| Component | Model Size | KV Cache (max ctx) | RAM Usage |
|-----------|------------|-------------------|-----------|
| Planner (Qwen3-14B Q4_K_M) | ~8.5 GB | ~1.5 GB (16K ctx) | **~10 GB** |
| Executor (Qwen2.5-Coder-14B Q4_K_M) | ~8.5 GB | ~0.8 GB (8K ctx) | **~9.3 GB** |
| Critic (Qwen3-1.7B Q4_K_M) | ~1.2 GB | ~0.2 GB (4K ctx) | **~1.4 GB** |
| OS + Python + Overhead | — | — | **~2 GB** |
| **Total (sequential)** | — | — | **~10-12 GB peak** |
| **Total (concurrent)** | — | — | **~22 GB (EXCEEDS 16GB)** |

**Decision**: Run models **sequentially** (not concurrent). Planner → Executor → Critic pipeline.
- Planner runs, completes, unloads
- Executor runs, completes, unloads  
- Critic runs, completes, unloads
- Peak RAM: ~12 GB (fits with 4 GB headroom)

**Implementation**: `ModelGateway` manages model loading/unloading with reference counting.

---

## 8. Deployment Checklist

### 8.1 Pre-Deployment
- [ ] Hardware validation script passes
- [ ] All 3 GGUF models downloaded to `~/OmegaLibrary/models/`
- [ ] MCP servers for knowledge domains running
- [ ] FTS5 index built for all domain corpora
- [ ] Role prompt templates authored and tested
- [ ] Compression pipeline benchmarks on representative prompts

### 8.2 Configuration Files
- [ ] `config/roles/registry.yaml` — Role specifications
- [ ] `config/models/cpu_16gb.yaml` — Model registry
- [ ] `config/knowledge_domains.yaml` — Domain registry
- [ ] `config/providers.yaml` — Provider fabric with local-first priority
- [ ] `schemas/` — JSON schemas for all role outputs

### 8.3 Testing
- [ ] Planner generates valid plans for 10 representative tasks
- [ ] Executor completes steps within context budget
- [ ] Critic catches injected bugs in test suite
- [ ] Verifier runs deterministically
- [ ] Researcher produces fractal deliverables
- [ ] Domain loading works for single + multi-domain tasks
- [ ] Compression reduces tokens 2-5× with >90% quality retention
- [ ] Full pipeline runs without OOM on 16GB RAM

---

## 9. Risk Assessment & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Planner model too weak for complex tasks** | Medium | High | Fallback to cloud (Antigravity) for planning only |
| **Executor fails on multi-file tasks** | Medium | High | Use Qwen2.5-Coder-14B as minimum; split tasks smaller |
| **Context packing drops critical info** | Low | High | Tiered budgets + critical preservation in compressor |
| **MCP server latency adds overhead** | Medium | Medium | Local MCP servers; cache frequent queries |
| **Model loading/unloading latency** | Medium | Low | Keep planner loaded during session; lazy load others |
| **RAM fragmentation from `--no-mmap`** | Low | Medium | Monitor; fallback to mmap if fragmentation detected |
| **Knowledge domain conflicts** | Low | Medium | Explicit domain composition priority rules |

---

## 10. Phased Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Implement `PromptBuilder` with priority sections
- [ ] Implement `ContextPacker` with tiered budgets
- [ ] Author role prompt templates (planner, executor, critic)
- [ ] Integrate with `Oracle.talk()` and `Oracle.summon()`

### Phase 2: Planner/Executor (Week 3-4)
- [ ] Implement plan DAG schema + validation
- [ ] Build execution loop with critic + verifier
- [ ] Add replanning on critic rejection
- [ ] Test on 5 real coding tasks

### Phase 3: Knowledge Domains (Week 5-6)
- [ ] Implement `KnowledgeLoader` four-paradigm hybrid
- [ ] Deploy MCP servers for 3 domains (tarot, kabbalah, swe)
- [ ] Build FTS5 indexes for domain corpora
- [ ] Test dynamic domain composition

### Phase 4: Compression & Optimization (Week 7-8)
- [ ] Integrate LLMLingua-2, RECOMP, Selective Context
- [ ] Benchmark compression ratios per component
- [ ] Tune tier budgets per role
- [ ] Hardware validation + OS tuning script

### Phase 5: Researcher Role & Polish (Week 9-10)
- [ ] Implement researcher role with Council of Four
- [ ] Fractal deliverable generation
- [ ] End-to-end integration testing
- [ ] Documentation + examples

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Planner context utilization** | < 80% of 16K | Token count per call |
| **Executor context utilization** | < 80% of 8K | Token count per call |
| **Critic context utilization** | < 80% of 4K | Token count per call |
| **Plan success rate** | > 85% | Steps completed without replan |
| **Critic catch rate** | > 90% | Injected bugs detected |
| **Compression ratio (system prompts)** | 3-5× | LLMLingua-2 |
| **Compression ratio (RAG context)** | 5-10× | RECOMP |
| **Compression ratio (contracts)** | 2-3× | Selective Context |
| **Peak RAM usage** | < 14 GB | `psutil` monitoring |
| **Planner latency** | < 30s | Wall clock |
| **Executor latency per step** | < 15s | Wall clock |
| **Critic latency** | < 5s | Wall clock |

---

## 12. Sources Synthesis

This blueprint integrates findings from all six research deliverables:

| Deliverable | Key Contributions to Blueprint |
|-------------|--------------------------------|
| **R_DYNAMIC_PROMPT_BUILDERS** | Substrate/Projection, priority sections (10-95), cache-aware static prefix, mode variants |
| **R_PLANNER_EXECUTOR_CONTEXT_WINDOW** | Multi-model (planner 14B, executor 14B, critic 1.7B), structured plan contracts, context packing per step |
| **R_KNOWLEDGE_DOMAIN_LOADING** | Four paradigms hybrid, MCP for dynamic injection, domain modules, FTS5-first search |
| **R_LOCAL_INFERENCE_OPTIMIZATION_CPU** | Q4_K_M default, `--no-mmap --mlock`, sequential model loading, Ryzen 5700U tuning |
| **R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION** | Tiered compression per component, RECOMP for RAG, LLMLingua-2 for prompts, Selective Context for contracts |
| **R_ROLE_AWARE_PROMPTING** | Distinct prompts/models/context per role, verifier as deterministic, communicative dehallucination |

---

## 13. Unresolved Questions (Requiring Architect Decision)

1. **Model selection**: Qwen3-14B vs Llama-3.1-8B for planner? (Qwen3 better reasoning, Llama better tool use)
2. **Executor minimum**: Is Qwen2.5-Coder-14B sufficient, or need 32B? (32B exceeds 16GB concurrent)
3. **Critic model**: Qwen3-1.7B vs 3B vs 7B? (Different from executor architecture critical)
4. **Domain fine-tuning**: Invest in fine-tuned models for tarot/kabbalah? (Paradigm 2)
5. **AutoCompressor**: Worth fine-tuning for stable high-volume prompts? (High upfront cost)
6. **Context distillation**: Distill domain prompts into soft prompts for researcher role?
7. **Concurrent vs sequential**: Accept sequential latency for RAM fit, or optimize for concurrent?

---

*End of R_DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md*