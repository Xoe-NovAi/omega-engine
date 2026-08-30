# Knowledge Domain Loading / Context Packing Systems
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-KNOWLEDGE-DOMAIN-LOADING-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_knowledge_domain_loading ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **knowledge domain loading** — systems where agents dynamically load relevant knowledge modules into their context window. The frontier has moved beyond simple RAG to **four knowledge injection paradigms** (Dynamic Injection, Static Embedding, Modular Adapters, Prompt Optimization), **context-gated prompt engineering**, **Model Context Protocol (MCP)** for standardized tool-based knowledge access, and **modular knowledge packs** that can be composed per task.

Key finding: The 2026 consensus is **hybrid RAG + fine-tuning** — RAG handles knowledge retrieval (fresh documents, proprietary data, cited answers), fine-tuning handles behavior (consistent format, tone, policy adherence). Prompt engineering with direct context inclusion is sufficient for knowledge bases under ~100K tokens.

---

## 1. Four Knowledge Injection Paradigms (Survey Paper, 2025)
> **Source**: [Injecting Domain-Specific Knowledge into LLMs — Comprehensive Survey](https://arxiv.org/html/2502.10708v1) (Tang et al., Microsoft Research, 2025-02-15)

| Paradigm | Training Cost | Inference Speed | Limitations |
|----------|---------------|-----------------|-------------|
| **Dynamic Knowledge Injection** | None (requires retrieval module) | Slower (retrieval latency) | Relies heavily on retrieval quality |
| **Static Knowledge Embedding** | High (pretraining/fine-tuning) | No extra cost | Fixed knowledge; catastrophic forgetting risk |
| **Modular Knowledge Adapters** | Low (train small parameter subset) | Almost unaffected | Sensitive to training data quality |
| **Prompt Optimization** | None | Almost unaffected | Labor-intensive; limited to pre-existing knowledge |

**Unified formulation**:
- Dynamic: `y = M(x, R(x, K); θ)` — retrieval at inference
- Static: `Δθ = argmin Σ L(M(x_s; θ), y_s)` — fine-tuning
- Modular: Plug-and-play adapters activated per task
- Prompt: `y = M([prompt; x]; θ)` — engineered prompts

---

## 2. Dynamic Knowledge Injection — RAG & Beyond

### 2.1 Standard RAG Pipeline (Mudassir Khan, 2026-05-17)
> **Source**: [RAG vs Fine-Tuning vs Prompt Engineering — Decision Guide](https://mudassirkhan.me/blog/fine-tuning-vs-rag)

```
1. Document ingestion: Parse + chunk specs/test cases
2. Embedding: Get vector embeddings
3. Vector Store: Store in MongoDB Atlas Vector Search / Qdrant / FAISS
4. Context Assembly: On query, retrieve top-k relevant docs, add to prompt
5. Generate: Send to LLM with retrieval context
```

**Optimization tips**:
- Semantic chunking (headings, bullets) for better retrieval
- Cosine similarity + metadata filters for ranking
- Cache recent vector results in Redis for repeat queries

### 2.2 2026 Standard: Hybrid RAG + Fine-Tuning (Mudassir Khan, 2026)
> **Source**: [RAG vs Fine-Tuning vs Prompt Engineering](https://mudassirkhan.me/blog/fine-tuning-vs-rag)

> "The RAG versus fine-tuning debate is largely resolved in 2026. Most production-grade AI systems use both."

**Typical hybrid stack**:
- Fine-tuned base model → format and policy adherence (weight level)
- RAG pipeline layered on top → domain-specific knowledge retrieval (inference time)
- Structured system prompts + few-shot → task-specific framing

**Decision tree**:
1. Try prompt engineering first (Claude Sonnet 4.6, GPT-5.4, Gemini 2.5 Pro handle wide range)
2. If factual failure → add RAG
3. If behavioral failure → add fine-tuning
4. If both → run hybrid

### 2.3 When to Skip RAG (Mudassir Khan, 2026)
> **Source**: [RAG vs Fine-Tuning vs Prompt Engineering](https://mudassirkhan.me/blog/fine-tuning-vs-rag)

> "If your knowledge base fits in context, skip RAG. A knowledge base under roughly 100,000 tokens can be included directly in the context window using full context loading with prompt caching. The setup cost is lower than a RAG pipeline and latency is competitive."

---

## 3. Modular Knowledge Adapters & Packs

### 3.1 Modular Adapter Paradigm (Survey Paper, 2025)
> **Source**: [arXiv:2502.10708](https://arxiv.org/html/2502.10708v1)

**Key systems**:
- **K-Adapter** (Wang et al., 2021) — Plug-and-play modules for domain adaptation
- **KnowGPT** (Zhang et al., 2024) — Dynamically combines knowledge graphs with prompt optimization via RL to extract relevant subgraphs
- **StructTuning** (Liu et al., 2024) — Structure-aware embedding via two-stage strategy

**Advantage**: "Modular adapters serve as a middle ground, allowing plug-and-play components to enhance domain-specific capabilities with minimal training data."

### 3.2 Knowledge Packs Concept (Gemma Discussion, 2026)
> **Source**: [GitHub: Dynamic Knowledge Context Injection](https://github.com/google-deepmind/gemma/discussions/627)

> "Let users download lightweight 'knowledge packs' (April 2026 facts) alongside the base model. Model already learns to prioritize recent context over old training data, so this should be simple."

**Implication**: Knowledge as downloadable, versioned modules — not embedded in model weights.

### 3.3 DMoE: Decoupled Mixture-of-Experts (2026-06-12)
> **Source**: [arXiv:2606.14243](https://arxiv.org/pdf/2606.14243)

**DMoE** decouples knowledge modules from base model:
- RAG: Knowledge at prompt level (external context)
- Post-training: Modifies shared parameters (conflict/forgetting risk)
- **DMoE**: Modular parametric integration — knowledge modules separate from base model

> "DMoE decouples knowledge modules from the base model, enabling modular and efficient parametric integration."

---

## 4. Context-Gated Prompt Engineering

### 4.1 Selective Context Gating (Svedberg Open, 2026-06-24)
> **Source**: [Dynamic Domain Knowledge Injection Using Context-Gated Prompt Engineering](https://www.svedbergopen.com/index.php/ijaiml/article/view/925)

> "These results show the effectiveness of selective context gating for reducing irrelevant knowledge injection and enhancing domain-specific question answering. The proposed framework offers a practical solution for integrating specialized knowledge into LLMs without altering the model's parameters."

**Mechanism**: Gate/relevance scoring before injection — only high-relevance knowledge enters context.

### 4.2 Context-Gated Injection (arXiv:2505.02306 - SafeMate)
> **Source**: [SafeMate: Modular RAG-Based Agent for Context-Aware Emergency Guidance](https://ar5iv.labs.arxiv.org/html/2505.02306)

**SafeMate architecture**:
- MCP-driven agent framework
- FAISS with cosine similarity for relevant content identification
- Dynamic routing to tools: document retrieval, checklist generation, structured summarization
- Modular, tool-integrated agent interface (not fixed logical path)

---

## 5. Model Context Protocol (MCP) — Standardized Knowledge Access

### 5.1 MCP as Knowledge Layer (Multiple Sources, 2025-2026)
> **Sources**: 
> - [SafeMate (arXiv:2505.02306)](https://ar5iv.labs.arxiv.org/html/2505.02306)
> - [GrandLinux (2026-05-24)](https://www.grandlinux.com/en/blogs/claude-local-ai-planner-executor.html)
> - [Medium: MCP with LangGraph + Ollama](https://medium.com/@diwakarkumar_18755/understanding-model-context-protocol-mcp-with-langgraph-and-ollama-a-practical-guide-1aea1c2a9937)

**MCP role**: Common protocol for both planner and executor to access same tools and data sources. Enables plug-and-play across layers.

**SafeMate MCP stack**:
```
MCP Client (LangChain + LangGraph) 
    → FAISS retrieval (static knowledge)
    → LangChain MCP adapters (dynamic tools: YouTube, Google Maps, Weather)
    → MCP Server infrastructure (Smithery)
    → FastAPI backend
    → LLM composes multimodal output
```

### 5.2 Dynamic Context Injection via MCP (Medium, 2026)
> **Source**: [Dynamic Context Injection into LLMs](https://medium.com/@shivamchamoli1997/dynamic-context-injection-into-llms-a-scalable-approach-to-token-efficient-retrieval-augmented-dd5b37dfabeb)

MCP enables standardized, scalable context injection where knowledge sources are exposed as tools rather than prompt stuffing.

---

## 6. Context Packing & Selection Strategies

### 6.1 Context Engineering = Packing the Window (CoreConcept, 2026-07-21)
> **Source**: [Context Engineering: Packing the Window That Shapes the Answer](https://corecocept.com/blog/context-engineering)

> "Context engineering names that larger job: gather candidates, score them for the current goal, compress or summarize what must survive, drop noise, and leave headroom for the model's answer."

**Packing decision process**:
1. **Gather** candidates from substrate (memory, KB, tools, history)
2. **Score** for current goal (relevance, recency, authority)
3. **Compress** or summarize what must survive
4. **Drop** noise (low-score chunks that win by volume)
5. **Leave headroom** for model's answer

**Failure classes owned by context engineering**:
- Pollution: low-score chunks win by volume → cap and floor scores
- Stale memory: old "resolved" note blocks new outage → summarize with timestamps
- Empty retrieval: refuse or escalate — do not fill with random FAQ
- Injection: treat retrieved text as untrusted data, not instructions

### 6.2 Tiered Context Priority (Hoomanely, 2025-12-04)
> **Source**: [Dynamic Prompt Construction](https://tech.hoomanely.com/dynamic-prompt-construction-building-context-aware-prompts-at-runtime/)

When approaching token limits:
- **Critical** (must include) — never dropped
- **High Value** (include if space allows) — compressed first
- **Supplementary** (add opportunistically) — dropped first

Some implementations use **lazy context expansion**: start minimal, enrich with follow-up if initial response suggests missing information.

### 6.3 Agentic Patterns: Dynamic Context Injection (Agentic-Patterns.com, 2026)
> **Source**: [Dynamic Context Injection Pattern](https://www.agentic-patterns.com/patterns/dynamic-context-injection)

**Mechanisms for on-demand context injection**:
- **File/Folder At-Mentions**: `@src/components/Button.tsx` → agent ingests file content
- **Custom Slash Commands**: `/user:foo` loads predefined prompt/instruction from `~/.claude/commands/foo.md`

**Security controls required**:
- Allowlist-based directory access
- Regex-based credential scanning
- File size limits

---

## 7. Knowledge Domain Loading Architectures

### 7.1 Mnemosyne Kabbalistic Memory (Omega Legacy, Era 5)
> **Source**: Internal Omega Engine documentation (recovered from `omega_library/data_archive/mnemosyne/`)

13-sphere Kabbalistic memory system — precursor to `soul.yaml`:
- Each sphere = knowledge domain (e.g., Binah = understanding, Chokhmah = wisdom)
- Spheres interconnect via paths (22 paths = relationships)
- Dynamic loading: activate relevant spheres per task
- Migration script needed for modern `soul.yaml` integration

### 7.2 Lilith Tarot Genesis (Omega Legacy, Era 0)
> **Source**: Internal Omega Engine documentation (recovered from `omega_library/intake/mining_queue/Omega-Early-Material/tarot/`)

7-entity pantheon with archetypal knowledge domains:
- Each entity = specialized knowledge domain
- Tarot cards as domain activation triggers
- Rituals = composition protocols for multi-domain tasks

### 7.3 Modern Modular Knowledge Base Design (Survey Paper, 2025)
> **Source**: [arXiv:2502.10708](https://arxiv.org/html/2502.10708v1)

**Domain-specific benchmarks showing modular approach effectiveness**:

| Domain | System | Paradigm | Benchmark |
|--------|--------|----------|-----------|
| Biomedical | KnowGPT | Dynamic Injection | MedQA, PubMedQA |
| Biomedical | K-Adapter | Modular Adapters | MedQuA, emrQA |
| Chemistry | ChemCrow | Dynamic Injection | 18 expert tools |
| Materials | ChemDFM | Static Embedding | SciQ, PubChem |
| Legal | SA-MDKIF | Prompt Optimization | eRisk |
| Healthcare | ChronicCareGPT | Prompt Optimization | MedQA |

---

## 8. Context Packing Algorithms

### 8.1 Relevance Scoring + Budget Allocation (Hoomanely, 2025)
```python
class ContextPacker:
    def __init__(self, total_budget: int):
        self.total_budget = total_budget
        self.tiers = {
            "critical": 0.4,      # 40% guaranteed
            "high_value": 0.35,   # 35% if available
            "supplementary": 0.25 # 25% opportunistic
        }
    
    def pack(self, query: str, candidates: list[KnowledgeChunk]) -> str:
        # Score each chunk
        scored = [(c, self.relevance_score(c, query)) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate by tier
        packed = []
        remaining = self.total_budget
        for tier, ratio in self.tiers.items():
            tier_budget = int(self.total_budget * ratio)
            tier_chunks = [c for c, s in scored if c.tier == tier]
            packed.extend(self.select_by_budget(tier_chunks, tier_budget))
            remaining -= sum(c.tokens for c in packed if c.tier == tier)
        
        return self.format_context(packed)
```

### 8.2 Selective Context (Li et al., 2023) — Sentence-Level Filtering
> **Source**: [Selective Context GitHub](https://github.com/liyucheng09/Selective_Context), [arXiv:2310.06201](https://arxiv.org/abs/2310.06201)

**Mechanic**: Scoring model evaluates each sentence for relevance to task. Low-relevance sentences dropped.

**Performance**: 3-10× compression, 92-99% quality retention at 3-5× compression.

**Implementation**:
```bash
pip install selective-context
python -m spacy download en_core_web_sm

from selective_context import SelectiveContext
sc = SelectiveContext()
compressed = sc.compress(prompt, context, ratio=0.3)  # 30% of original
```

---

## 9. Production Systems Comparison

| System | Knowledge Paradigm | Loading Mechanism | Modularity | Context Packing |
|--------|-------------------|-------------------|------------|-----------------|
| **SafeMate** | RAG + MCP | Dynamic tool routing | High (MCP tools) | FAISS cosine + gating |
| **KnowGPT** | Dynamic + Prompt | KG subgraph extraction | Medium (RL-selected) | Subgraph → natural language |
| **K-Adapter** | Modular Adapters | Plug-and-play modules | High (per-domain adapters) | Adapter activation |
| **ChemCrow** | Dynamic Injection | 18 expert tools | High (tool per capability) | Tool selection by planner |
| **DMoE** | Parametric Modules | Decoupled MoE experts | High (expert per domain) | Expert routing |
| **Claude Code** | Direct Context | CLAUDE.md files | Low (static files) | Manual curation |
| **Selective Context** | Prompt Optimization | Sentence-level scoring | N/A (compression) | Relevance filtering |
| **Omega Engine (target)** | Hybrid | Domain modules + MCP | **Target: High** | **Target: Tiered + FTS5** |

---

## 10. Recommendations for Omega Engine

### 10.1 Adopt Four-Paradigm Hybrid Architecture
```python
class KnowledgeLoader:
    def __init__(self):
        # Paradigm 1: Dynamic Injection (RAG via MCP)
        self.rag = MCPRAGClient()
        
        # Paradigm 2: Static Embedding (fine-tuned base models per domain)
        self.fine_tuned = DomainModelRegistry()
        
        # Paradigm 3: Modular Adapters (LoRA/adapter per domain)
        self.adapters = AdapterRegistry()
        
        # Paradigm 4: Prompt Optimization (domain system prompts)
        self.prompts = DomainPromptRegistry()
    
    def load_for_task(self, task: Task, context_budget: int) -> LoadedKnowledge:
        # 1. Select fine-tuned base model for domain behavior
        model = self.fine_tuned.get(task.domain)
        
        # 2. Activate relevant adapters
        adapters = self.adapters.activate(task.domain, task.subdomain)
        
        # 3. Build domain system prompt
        system_prompt = self.prompts.build(task.domain, task.role)
        
        # 4. Retrieve dynamic knowledge via MCP (packed to budget)
        dynamic_knowledge = self.rag.retrieve_and_pack(
            query=task.query,
            domain=task.domain,
            budget=context_budget - system_prompt.tokens
        )
        
        return LoadedKnowledge(model, adapters, system_prompt, dynamic_knowledge)
```

### 10.2 Domain Module Structure
```
config/wads/arcana_nova/knowledge_domains/
├── tarot/
│   ├── domain.yaml          # Metadata, version, dependencies
│   ├── system_prompt.md     # Domain-specific system prompt
│   ├── adapter/             # LoRA adapter (optional)
│   ├── mcp_tools/           # MCP tool definitions
│   └── corpus/              # Static knowledge (Markdown, JSON)
├── kabbalah/
├── astrology/
└── software_engineering/
```

### 10.3 MCP-Based Knowledge Access
- Expose each knowledge domain as MCP server
- Planner and executor both use same MCP tools
- Tools: `search_domain`, `get_concept`, `get_relationship`, `get_ritual`
- Enables "knowledge packs" as downloadable MCP server bundles

### 10.4 Context Packing with FTS5-First Search (C-MEM-004)
- SQLite FTS5 index for all domain knowledge
- BM25 ranking → retrieve doc IDs → hydrate full records
- Hybrid scoring: `-rank + vec_score * 10` (negate FTS5 rank)
- Tiered budget enforcement per Hoomanely

### 10.5 Soul.yaml Integration
- Domain loading updates entity's active knowledge context
- Cross-pollination: insights from one domain inform another
- Gnosis distillation (L1→L2→L3) feeds back into domain corpus

---

## 11. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | Tang et al. (Microsoft, 2025) | arXiv survey | ✅ Direct fetch | arXiv:2502.10708, 4 paradigms, comparison table |
| 2 | Mudassir Khan (2026-05-17) | Engineering blog | ✅ Direct fetch | 2026 standard hybrid RAG+fine-tune, 100K token threshold |
| 3 | Svedberg Open (2026-06-24) | Journal article | ✅ Direct fetch | Context-gated prompt engineering |
| 4 | SafeMate (2025-05) | arXiv paper | ✅ Direct fetch | arXiv:2505.02306, MCP + FAISS + modular tools |
| 5 | DMoE (2026-06-12) | arXiv paper | ✅ Direct fetch | arXiv:2606.14243, decoupled MoE for knowledge |
| 6 | CoreConcept (2026-07-21) | Engineering blog | ✅ Direct fetch | Context engineering = packing, failure classes |
| 7 | Hoomanely (2025-12-04) | Engineering blog | ✅ Direct fetch | Tiered priority, lazy expansion |
| 8 | Agentic-Patterns.com (2026) | Pattern library | ✅ Direct fetch | At-mentions, slash commands, security controls |
| 9 | Selective Context (2023) | GitHub + paper | ✅ Direct fetch | Sentence-level, 3-10× compression |
| 10 | Gemma Discussion (2026) | GitHub discussion | ✅ Direct fetch | Knowledge packs concept |
| 11 | Omega Legacy (internal) | Recovered docs | ✅ Local access | Mnemosyne 13-sphere, Lilith 7-entity |

---

## 12. Unverified Claims (Flagged)

- **KnowGPT "significantly reduces API call costs"** — paper claim, no independent cost analysis
- **DMoE "enables modular and efficient parametric integration"** — paper claim, no open implementation
- **SafeMate "outperforms GPT-4o and GPT-3.5"** — paper claim on emergency benchmarks only
- **100K token threshold for skipping RAG** — Mudassir Khan heuristic, no systematic study
- **Mnemosyne/Lilith integration feasibility** — internal legacy, no modern implementation exists

---

*End of R_KNOWLEDGE_DOMAIN_LOADING_20260819.md*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
