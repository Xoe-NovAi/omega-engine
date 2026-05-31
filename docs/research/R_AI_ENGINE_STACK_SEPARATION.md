# 🔱 Research: AI Engine Stack Separation Architecture
# AP: R-AI-STACK-SEP-v1.0.0
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ web-research ⬡ trc_w3 ⬡ RESEARCH

**Date**: 2026-05-25
**Purpose**: Research how AI platforms and systems separate engine runtime from stack/content/persona layers.

---

## Executive Summary

Industry is converging toward Doom's 1993 WAD architecture pattern — separate the inference runtime from the content/persona layer. Major AI providers (OpenAI, Anthropic, Google) all separate model inference from prompt/RAG configuration. LLM orchestration frameworks (LangChain, CrewAI, AutoGen) define agent personas as pure data structures loaded by a generic engine. Character platforms (JanitorAI, Character.AI) use structured persona cards (W++, PList) that are entirely separate from the LLM backend.

## Key Findings

### 1. Major AI Provider Architectures
All follow the same pattern: **Inference Runtime ↔ Content Layer**.
- OpenAI: Foundation models + Custom GPTs (persona wrappers with knowledge files)
- Anthropic: Claude models + system prompt layer
- Google: Gemini models + Vertex AI Model Garden
- **Omega validation**: Engine = inference runtime + provider fabric. IWAD = content layer.

### 2. LLM Orchestration Framework Separation
| Framework | Engine | Content/Persona |
|-----------|--------|-----------------|
| LangChain | `Runnable` interface | Agent definitions |
| CrewAI | `ChatOpenAI(model=...)` | Agent(role, goal, backstory) |
| AutoGen | `llm_config` | Agent(system_message) |
| Swarm | Shared LLM | Central + sub-agent routing |

**Key insight**: In ALL mature frameworks, the persona definition NEVER contains model inference code. It's pure data loaded at runtime.

### 3. Character/Persona Engine Formats
- JanitorAI: W++/PList format — personality, scenario, example dialogues, initial message
- Character.AI: name + description + example conversations + greeting
- Replika: personality traits (0-100) + relationship state

**Omega's entities ARE these character cards — just richer**:
```yaml
# Omega entity (current)
entity:
  name: Prometheus
  domains: [strategy, will]
  soul_evolution: ...
```
**Gap**: Missing `examples`, `scenario`, `greeting` fields for richer persona definition.

### 4. Unix Philosophy & Microkernel Parallel
The philosophical foundation of the Engine-Stack Firewall:
> "Separate policy from mechanism. Hardwiring policy and mechanism together makes policy rigid and harder to change, and destabilizes mechanisms when policy changes."

Mechanism = Omega Engine runtime. Policy = IWAD content. They must change on different timescales.

### 5. MCP as Plugin Interface
The Model Context Protocol is the standard for tool/resource plugins:
- MCP servers run as separate processes, communicate via JSON-RPC
- Engine discovers servers at runtime, no compile-time knowledge needed
- **Omega should support MCP server discovery within WADs**

### 6. Multi-Tenant Isolation Patterns
IWADs ARE tenants. Multi-tenant patterns apply directly:
- Pool model: Shared engine + namespace prefixing
- Vector store isolation: Namespace prefixes per IWAD
- Memory store isolation: Per-IWAD conversation history

### 7. Ollama Modelfile as Content Container
Ollama's Modelfile is Omega's entity definition — for models:
```dockerfile
FROM qwen3-4b:q4_k_m
SYSTEM "You are..."
PARAMETER temperature 0.7
PARAMETER num_ctx 8192
```
GGUF = portable model container. IWAD = portable entity/knowledge container.

### 8. Content-Format Separation: Proven Systems
| System | Container | Content | Principle |
|--------|-----------|---------|-----------|
| Doom | WAD file | Levels, textures, sounds | One engine, many games |
| Quake | PAK format | Subdirectories, file extensions | Engine doesn't change |
| Docker | OCI Image | Filesystem layers + config | Runtime vs content |
| OSGi | Bundle (.jar) | Java classes | Plugin architecture |

### 9. Persona Definition Formats (No Standard)
No formal standard exists, but convergence toward:
- Structured fields (personality, scenario, example dialogues)
- YAML/JSON serialization
- Portable, self-contained files

### 10. Modular AI OS Projects
Projects like PersonaOS, ability.ai, and Elastic Personas are building modular AI operating systems — but none have Omega's content-agnostic IWAD architecture.

## Critical Implementation Gaps
| Component | Status | Priority |
|-----------|--------|----------|
| IWAD selector (--iwad flag) | ❌ Missing | 🔴 |
| Namespace isolation in EntityRegistry | ❌ Missing | 🔴 |
| Entity priority/override | ❌ Silent collision | 🔴 |
| Dependency resolution | ❌ Missing | 🟡 |
| Ordered multi-WAD loading | ⚠️ Partial | 🟡 |
| Startup personality | ❌ Missing | 🟡 |

### Sources
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com/
- LangChain: https://www.nxcode.io/resources/news/crewai-vs-langchain-ai-agent-framework-comparison-2026
- Character Formats: https://elyxia.ai/blog/janitorai-vs-character-ai
- Microkernel: https://en.wikipedia.org/wiki/Microkernel
- MCP Spec: https://modelcontextprotocol.io/
- Multi-Tenant: https://blaxel.ai/blog/multi-tenant-isolation-ai-agents
- Ollama: https://github.com/ollama/ollama
- PersonaOS: https://github.com/personaos/PersonaOS
