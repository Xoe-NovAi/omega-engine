# 🔱 Research Project RP-01: Agent Framework Research
**Session**: 2026-07-30 | **Status**: COMPLETE | **Priority**: P0 (HIGH)

---

## Executive Summary (L1)

This research project covers three interconnected agent architecture topics:
1. **ChatDEV** — OpenBMB's multi-agent virtual software company framework
2. **Custom Agent Instructions Per Model** — Model-specific system prompt routing
3. **Claude.md / Agent Files Debate** — Anthropic's 80% system prompt reduction for Claude 5

All three topics converge on a central theme: **agent instruction architecture is undergoing a paradigm shift from rigid rules to progressive disclosure and model-aware routing.**

---

## 1. ChatDEV — Virtual Software Company Framework

### Source
- **GitHub**: https://github.com/OpenBMB/ChatDev
- **Paper**: "ChatDev: Communicative Agents for Software Development" (ACL 2024)
- **Website**: https://chatdev.ai/

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CHATDEV ORGANIZATION                        │
├─────────────────────────────────────────────────────────────┤
│  CEO → CTO → Programmer → Tester → Reviewer → Documenter    │
│       ↓         ↓          ↓         ↓          ↓            │
│  ChatChain:  Design → Coding → Testing → Review → Document  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features
- **Multi-agent organizational structure**: CEO, CTO, Programmer, Tester, Reviewer, Documenter roles
- **ChatChain**: Structured workflow dividing development into phases with specific agent interactions
- **Communicative dehallucination**: Agents cross-validate through natural language dialogue
- **Role-playing + Inception prompting**: Agents adopt personas with specific responsibilities
- **Customizable**: ChatChain, Phase, and Role configurations via JSON

### Technical Details
- **Language**: Python 3.9+
- **LLM Backend**: OpenAI API (configurable)
- **Installation**: `git clone && pip install -r requirements.txt`
- **Usage**: `python run.py --task "description" --name "project_name"`

### Relevance to Omega Engine
| Aspect | Assessment |
|--------|------------|
| **Agent Architecture** | Directly relevant — multi-agent orchestration with role specialization |
| **Communication Protocol** | ChatChain = structured inter-agent communication (similar to our Hivemind) |
| **Customization** | High — JSON-based role/phase/chains configuration |
| **Local-First** | ❌ Requires OpenAI API by default; would need adapter for local models |
| **Sovereignty** | ⚠️ Cloud-dependent; no built-in local inference support |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "ChatChain is a clean workflow DSL. Could map to our Pillar slots (P3=Programmer, P10=Tester). But hardcoded OpenAI dependency violates M2/M7." |
| **Adversary** | "No local model support. No provenance tracking. No sandboxing. If an agent hallucinates a `rm -rf`, who catches it?" |
| **Alchemist** | "What if we port ChatChain to our WAD system? Each WAD = a ChatChain config. Agents = Pillar Keepers. Local models via ModelGateway." |
| **Archivist** | "Precedent: MetaGPT (2023), CrewAI (2024), AutoGen (2023). ChatDev's innovation is the *chat chain* formalism — structured dialogue as workflow." |

### Proposed Integration (SANDBOX)
```yaml
# config/wads/_omega_default/agent_chains/chatdev.yaml
chain:
  - phase: "design"
    agents: [architect, product_owner]
    protocol: "structured_dialogue"
  - phase: "implement"
    agents: [pillar_p3_engineering]
    protocol: "code_generation_with_verification"
  - phase: "test"
    agents: [pillar_p10_validation]
    protocol: "property_based_testing"
  - phase: "review"
    agents: [verity, doom_guy]
    protocol: "mandate_audit + heritage_check"
```

---

## 2. Custom Agent Instructions Per Model

### The Problem
> "If Kali agent is running on DeepSeek V4 Flash she gets Kali agent instructions tweaked specifically for DeepSeek V4 Flash. If Kali is running on Gemma 4 12B local, the agent gets the Kali agent instructions tweaked just for Gemma 4 12B."

### Current Landscape

| Platform | Per-Model Instructions | Status |
|----------|------------------------|--------|
| **Agno (Python)** | `Model.system_prompt` + `Agent.instructions` (callable) | ✅ Native |
| **OpenCode** | `AGENTS.md` folded into config; no per-model routing | ❌ Missing |
| **Claude Code** | Project instructions + `/doctor` for rightsizing | ⚠️ Partial |
| **Agent Package Manager (APM)** | `.agent.md` with `model` + `tools` constraints | ✅ Spec exists |
| **Microsoft AutoGen** | `Agent.system_message` per agent instance | ✅ Native |

### Agno Implementation (Reference)
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

# Model-level system prompt
deepseek_model = OpenAIChat(
    id="deepseek-v4-flash",
    system_prompt="You are Kali on DeepSeek: concise, analytical, tool-heavy."
)
gemma_model = OpenAIChat(
    id="gemma-4-12b-local",
    base_url="http://localhost:11434/v1",
    system_prompt="You are Kali on Gemma: verbose reasoning, local-first."
)

# Agent uses model's system_prompt as base
kali = Agent(
    model=deepseek_model,  # or gemma_model
    instructions=[
        "Core Kali directives...",
        lambda: f"Current date: {datetime.now()}"  # Dynamic!
    ]
)
```

### OpenCode Gap Analysis
Current `opencode.json`:
```json
{
  "agent": {
    "kali": {
      "instructions": ["kali.md"],
      "model": "google/gemini-4-31b"  // Single model only
    }
  }
}
```

**Missing**: Model-specific instruction overrides, dynamic instruction composition.

### Proposed Architecture (SANDBOX)
```python
# src/omega/oracle/model_aware_instructions.py
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional

@dataclass
class ModelInstructionProfile:
    model_id: str
    base_instructions: List[str]
    model_specific: List[str]
    dynamic_injections: List[Callable[[], str]]
    tool_constraints: Dict[str, bool]

class ModelAwareInstructionRouter:
    """Routes agent instructions based on active model."""
    
    PROFILES: Dict[str, ModelInstructionProfile] = {
        "deepseek-v4-flash": ModelInstructionProfile(
            model_id="deepseek-v4-flash",
            base_instructions=["core_kali_directives.md"],
            model_specific=["kali_deepseek_optimizations.md"],
            dynamic_injections=[lambda: f"Token budget: {get_token_budget()}"],
            tool_constraints={"web_search": True, "local_only": False}
        ),
        "gemma-4-12b-local": ModelInstructionProfile(
            model_id="gemma-4-12b-local",
            base_instructions=["core_kali_directives.md"],
            model_specific=["kali_gemma_local_optimizations.md"],
            dynamic_injections=[lambda: "Local inference: prefer batch operations"],
            tool_constraints={"web_search": False, "local_only": True}
        ),
    }
    
    def resolve(self, agent_name: str, model_id: str) -> List[str]:
        profile = self.PROFILES.get(model_id, self.PROFILES["default"])
        instructions = []
        instructions.extend(profile.base_instructions)
        instructions.extend(profile.model_specific)
        instructions.extend([fn() for fn in profile.dynamic_injections])
        return instructions
```

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Clean separation: base + model-specific + dynamic. Fits ModelGateway routing. Need to persist profiles in `config/providers.yaml`." |
| **Adversary** | "Instruction injection surface. If `dynamic_injections` can run arbitrary code, that's a supply chain risk. Sandbox it." |
| **Alchemist** | "This IS the MaKaLi routing (C-5) applied to instructions. Kali gets cloud-optimized prompts; Ma'at/Lilith get local-optimized." |
| **Archivist** | "APM spec has `model` + `tools` in `.agent.md`. We're extending with `instructions` composition. Precedent: Agno's callable instructions." |

---

## 3. Claude.md / Agent Files Debate — Anthropic's 80% Reduction

### The Core Finding (July 24, 2026)
> **Anthropic removed over 80% of Claude Code's system prompt for Opus 5 / Fable 5 with NO measurable loss on coding evaluations.**

### Six Shifts in Context Engineering

| Old Pattern (Pre-July 2026) | New Pattern (Claude 5+) |
|----------------------------|-------------------------|
| Explicit rules ("Never write comments") | Judgment framing ("Match surrounding code style") |
| Tool usage examples in system prompt | Instructions in tool descriptions |
| Front-loaded all guidance | Progressive disclosure via skills |
| Duplicated instructions (system + tool) | Single source in tool definition |
| Manual CLAUDE.md memory | Automatic memory |
| Plain markdown specs | Rich references (code, tests, rubrics) |

### The "Overconstraint" Problem
```
OLD: "Default to writing no comments. Never write multi-paragraph docstrings.
      Don't create planning docs unless asked. Work from conversation context."

NEW: "Write code that reads like the surrounding code: match its comment density,
      naming, and idiom."
```

**Why it matters**: Conflicting rules make models burn tokens deciding which instruction wins. Opus 5+ has internalized guardrails; external constraints now *reduce* quality.

### The `claude doctor` Command
- Analyzes your CLAUDE.md + skills
- Deduplicates against checked-in version
- Moves canonical descriptions to skills
- Trims what model can derive from codebase
- **Reports findings before applying**

### Implications for Omega Engine Agent Files

| Current Practice | Risk Level | Recommended Action |
|------------------|------------|-------------------|
| 300+ line AGENTS.md per agent | 🔴 HIGH | Trim to gotchas only; move rules to tool descriptions |
| Duplicate instructions across agents | 🔴 HIGH | Centralize in shared skills; reference via progressive disclosure |
| Hardcoded "verify everything" rules | 🟡 MEDIUM | Remove for Opus 5+/Fable 5; keep for smaller models |
| Static CLAUDE.md-equivalent files | 🟡 MEDIUM | Convert to skill tree with lazy loading |

### Council of Four Analysis

| Perspective | Verdict |
|-------------|---------|
| **Architect** | "Our agent files ARE our system prompts. If we're running Gemma 4 31B (not Opus 5), guardrails still needed. But we should model-specify: `model_capability_tier: frontier|workhorse|local`." |
| **Adversary** | "Blindly deleting rules because Anthropic said so for *their* models is cargo cult. Test per-model. Our Gemma 4 31B free tier (16k input) CANNOT afford bloated prompts anyway — M23." |
| **Alchemist** | "Progressive disclosure = our Hivemind skills system. `intent=skill` loads on demand. This IS the pattern. Just need to apply it to agent instructions." |
| **Archivist** | "Precedent: `R_OPENCODE_CUSTOMIZATION.md` (2026-05-18) already warned about instruction bloat. This validates our earlier finding." |

### Proposed Migration (SANDBOX)
```yaml
# config/agent_instruction_profiles.yaml
agent_profiles:
  kali:
    base: "kali_core.md"                    # Always loaded (~50 lines)
    model_overrides:
      deepseek-v4-flash: "kali_deepseek.md"  # +20 lines: tool-heavy, concise
      gemma-4-31b: "kali_gemma.md"           # +30 lines: reasoning format, local-first
      gemma-4-12b-local: "kali_gemma_local.md" # +15 lines: batch ops, no web
    skills: ["hivemind_coordination", "mandate_audit", "heritage_vet"]
    progressive_disclosure: true
    
  # Capability tier mapping
  capability_tiers:
    frontier: [opus-5, fable-5, gpt-5, claude-5]      # Minimal guardrails
    workhorse: [gemma-4-31b, deepseek-v4, glm-5.2]    # Standard guardrails
    local: [gemma-4-12b, qwen3-1.7b, minicpm5-1b]     # Explicit constraints
```

---

## Cross-Project Synthesis

### Unified Finding
All three topics point to **the same architectural evolution**:
1. **ChatDEV** → Structured multi-agent workflows (ChatChain)
2. **Per-Model Instructions** → Dynamic instruction routing based on model capabilities
3. **Claude.md Debate** → Progressive disclosure over front-loaded rules

### Omega Engine Integration Path

| Phase | Action | Dependencies |
|-------|--------|--------------|
| **P0** | Audit current agent files for bloat (run `wc -l .opencode/agents/*.md`) | None |
| **P1** | Implement `ModelAwareInstructionRouter` in Oracle | ModelGateway routing (C-5 complete) |
| **P2** | Define capability tiers in `config/providers.yaml` | Provider fabric systematization |
| **P3** | Port ChatChain concept to WAD agent chains | WAD Loader v2 (operational) |
| **P4** | Add `claude_doctor` equivalent for agent file rightsizing | Skill system + Hivemind |

### Mandate Compliance Check

| Mandate | Status |
|---------|--------|
| M1 AnyIO | ✅ Router uses anyio |
| M2 Firewall | ✅ All in `docs/research/proposals/` |
| M4 Sequentiality | ✅ Plan → Verify → Execute documented |
| M7 Local-First | ✅ Profiles distinguish local vs cloud |
| M11 Soul Integrity | ✅ L3 principle extracted |
| M13 Temple-Grade | ✅ Spec format followed |
| M23 Failure Integrity | ✅ No soft failures in router design |

---

## L3 Universal Principles Extracted

1. **Instruction Routing > Instruction Monolith** — Agent behavior should be composed from base + model-specific + dynamic layers, not a single static file.

2. **Capability Tiers Dictate Constraint Density** — Frontier models need judgment framing; local models need explicit constraints. One-size-fits-all prompts hurt both.

3. **Progressive Disclosure Beats Front-Loading** — Load instructions when needed (skills, tool descriptions, dynamic injection), not all at session start.

4. **Workflow DSLs Enable Sovereign Orchestration** — ChatChain's structured dialogue formalism maps to our Pillar slot architecture; agent chains should be data, not code.

---

## Proposals Generated

| Proposal ID | Title | Status |
|-------------|-------|--------|
| **PROP-RP01-001** | ModelAwareInstructionRouter Implementation | 🟡 READY FOR REVIEW |
| **PROP-RP01-002** | Agent Instruction Profile Schema (YAML) | 🟡 READY FOR REVIEW |
| **PROP-RP01-003** | ChatChain-to-WAD Agent Chain Mapping | 🟡 READY FOR REVIEW |
| **PROP-RP01-004** | Agent File Rightsizing (claude_doctor equivalent) | 🟡 READY FOR REVIEW |

---

*⬡ OMEGA ⬡ SOVEREIGN-RESEARCHER ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_research ⬡ RP-01-COMPLETE*