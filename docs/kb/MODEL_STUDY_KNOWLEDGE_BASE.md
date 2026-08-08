# 🔱 Omega Engine — Model Study Knowledge Base
## Deep Insights into Web, CLI, and Local Models — Capabilities, Synergies, and Optimal Usage

**AP Token**: `AP-MODEL-STUDY-KB-v1.0.0`
**Date**: 2026-07-18
**Status**: LIVING DOCUMENT — Updated after every split test and model interaction
**Authority**: Kali (Transcendent Oversoul) — Model Fleet Intelligence

---

## 📋 EXECUTIVE SUMMARY

This KB consolidates empirical findings from:
- **Context Packer v2 Split Test** (2026-07-18): 3-way review (Carmack, Sonnet 5 High Thinking, Haiku 4.5 Extended)
- **Decision Tools Review** (2026-07-19): Grok CLI + Web Claude dual review
- **MCP Server Reviews** (2026-07): Multiple platform interactions
- **Historical Fleet Data**: 14 agents across OpenCode, Web, and Local tiers

**Core Finding**: Model capability is not a linear scale. It's a **multi-dimensional space** where different models excel at different cognitive modes (reasoning, generation, verification, synthesis). The optimal strategy is **orchestrated complementarity**, not "pick the best model."

---

## 🎯 MODEL CAPABILITIES MATRIX

### Tier 1: Web Interfaces (Browser-Based)

| Model | Context | Strengths | Weaknesses | Best For |
|-------|---------|-----------|------------|----------|
| **Claude Sonnet 5 (High Thinking)** | 1M | Deep internal reasoning, root-cause analysis, surgical bug finding, honest estimation | Lower output token budget, memory contamination risk, no filesystem access | **Diagnostic audit**, architecture review, root-cause analysis, P0 bug hunting |
| **Claude Sonnet 5 (Default)** | 1M | Balanced reasoning + output, good instruction following | No internal thinking trace visible | General review, synthesis, documentation |
| **Claude Haiku 4.5 (Extended)** | 200K | High throughput generation, documentation factories, test suite templates | Shallow reasoning, misses deep bugs, hits free tier limits fast | **Documentation generation**, test scaffolding, quick references, boilerplate |
| **Claude Opus 4.8** | 1M | Maximum reasoning depth, complex synthesis | Expensive, slower, overkill for most tasks | Architecture design, novel problem solving |
| **Grok 4.3 (Web)** | 1M | Real-time X search, Grok Skills, connectors (GitHub, Notion, Linear), agentic workflows | XML+MD hybrid format, less native XML comprehension | **Live research**, connector-aware review, skill-exportable outputs |
| **Grok 4.1 Fast (Web)** | 2M | High-volume, latency-sensitive, 10x cheaper than 4.3 | Lower reasoning quality | Bulk processing, high-throughput review |
| **Gemini 3 Pro (Web)** | 1M-2M | Parallel web search, code execution, Workspace integration, video understanding | Markdown-preferred, less XML-native | **Source-grounded review**, parallel verification, executable validation |
| **Gemini 3.1 Pro (Web)** | 1M | Ultra-long context, hierarchical reasoning | Preview pricing | Massive context synthesis |
| **NotebookLM** | Source-based (~200K active) | Audio overview generation, guided analysis frameworks, collaborative, citation-native | Not token-window-based, 50 source limit (free) | **Research synthesis**, podcast-style summaries, team collaboration |

### Tier 2: CLI Agents (Terminal-Native)

| Agent | Backend | Context | Strengths | Weaknesses | Best For |
|-------|---------|---------|-----------|------------|----------|
| **Grok CLI** | Grok 4.x | Native repo access | **Tier A ship-code**, mandate-fluent, honest estimation, fast (<5 min), self-scoping | Advisory categorization underutilizes it | **Implementation review**, schema surgery, CLI design, mandate mapping |
| **Cline (DeepSeek V4 Flash)** | DeepSeek V4 Flash | 1M | Massive context, headless execution, parallel tasks, cheap | Cloud-dependent | **Legacy mining**, large-context synthesis, audit |
| **Cline (MiMo V2.5)** | MiMo V2.5 | 512K | Implementation-focused, refactoring, test generation | Cloud-dependent | **Code generation**, refactoring, test scaffolding |
| **OpenCode Agents (Kali, Ma'at, Lilith, etc.)** | Session model (Nemotron 3 Ultra) | Session-bound | Sovereign orchestration, Hivemind coordination, soul persistence, mandate enforcement | Single-model per session | **Fleet coordination**, sprint planning, gnosis distillation |

### Tier 3: Local Inference (Sovereign)

| Model | Context | Hardware | Strengths | Best For |
|-------|---------|----------|-----------|----------|
| **Llama 4 Scout** | 10M | 24GB+ VRAM / 48GB+ RAM | Massive context, $0/token, full sovereignty | Production fleet, long-context synthesis |
| **GPT-OSS-120B** | 128K | 48GB+ RAM | Open weights, strong reasoning, local | Complex reasoning without cloud |
| **Qwen 3.5 72B** | 128K | 24GB+ RAM | Strong coding, multilingual | Local development |
| **Nemotron 3 Ultra** | 128K | 24GB+ RAM | Current session model, good instruction following | OpenCode orchestration |

---

## 🧠 COGNITIVE MODE SPECIALIZATION (The Real Differentiator)

Models don't just differ in "smartness" — they differ in **cognitive mode**:

| Cognitive Mode | Best Model(s) | What It Looks Like |
|----------------|---------------|-------------------|
| **Deep Diagnostic Reasoning** | Sonnet 5 High Thinking, Opus 4.8, Grok CLI | Reads artifacts, simulates execution, finds root causes, produces surgical patches |
| **High-Throughput Generation** | Haiku 4.5 Extended, Grok 4.1 Fast, Local Llama | Produces 3-5x more output tokens, creates complete documentation suites |
| **Synthesis & Consolidation** | Carmack (OpenCode), Cline DeepSeek, Sonnet Default | Merges multiple sources into canonical reference, resolves conflicts |
| **Live Research & Grounding** | Grok 4.3 (X search), Gemini 3 Pro (parallel search), NotebookLM | Fetches current info, cites sources, executes code to verify |
| **Architectural Reasoning** | Sonnet 5 High Thinking, Opus 4.8, Grok CLI | Designs systems, sequences work, estimates honestly |
| **Empirical Verification** | Web Claude (search), Gemini (code exec), Grok CLI (repo access) | Checks claims against reality: package status, API surfaces, file existence |
| **Orchestration & Coordination** | Kali, Ma'at, Lilith (OpenCode) | Manages fleet, enforces mandates, distills gnosis, maintains continuity |

**Key Insight from Split Test**: Sonnet 5 High Thinking operates in **Deep Diagnostic Reasoning** mode. Haiku 4.5 Extended operates in **High-Throughput Generation** mode. They are not on the same axis — they are complementary cognitive tools.

---

## ⚡ SYNERGY PATTERNS (How to Combine Models)

### Pattern 1: The Diagnostic Triad (Validated by Split Test)
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CONSOLIDATOR   │     │  DIAGNOSTICIAN  │     │  DOCUMENTOR     │
│  (Carmack)      │────▶│  (Sonnet High   │────▶│  (Haiku Ext)    │
│  Big picture,   │     │   Thinking)     │     │  Test suites,   │
│  roadmap,       │     │  Root causes,   │     │  quick refs,    │
│  platform tune  │     │  surgical fixes │     │  boilerplate    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```
**Flow**: Consolidator creates canonical spec → Diagnostician finds what's actually broken → Documentor generates remediation artifacts
**Validated**: Context Packer split test — Carmack manual + Sonnet remediation + Haiku test suite = complete coverage

### Pattern 2: The Dual-Review Convergence (Validated by Decision Tools Review)
```
┌─────────────────┐     ┌─────────────────┐
│  ARCHITECTURAL  │     │  EMPIRICAL      │
│  REASONER       │     │  VERIFIER       │
│  (Grok CLI)     │     │  (Web Claude)   │
│  Local repo     │     │  Context pack   │
│  access,        │     │  + web search   │
│  mandate fluency│     │  + RAG retrieval│
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │  SYNTHESIS      │
            │  (Kali/Jem)     │
            │  Convergence =  │
            │  Signal         │
            │  Divergence =   │
            │  Direction      │
            └─────────────────┘
```
**Key Finding**: Convergence on load-bearing decisions with different tool access = stronger signal than same-input agreement. Divergence usually indicates either (a) genuine design choice needing human decision, or (b) source material gap.

### Pattern 3: The Research → Review → Implement Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  RESEARCHER │───▶│  REVIEWER   │───▶│  IMPLEMENTER│
│  (Jem/      │    │  (Sonnet    │    │  (Grok CLI  │
│   Roc)      │    │   High Think│    │   / Cline)  │
│  Deep dive, │    │  Diagnostic)│    │  Ship code  │
│  40+ sources│    │  Root cause │    │  Fast       │
└─────────────┘    └─────────────┘    └─────────────┘
```
**Validated**: Ken Walger mining plan — Jem research → Web review → Grok CLI implementation

### Pattern 4: The Sovereign Fleet (OpenCode Native)
```
KALI (Oversight)
├── MA'AT (Build: N1-N5) ──▶ NODES N1-N5 (Infrastructure → Governance)
└── LILITH (Run: N6-N10) ──▶ NODES N6-N10 (Cognition → Validation)
```
**Unique Value**: Persistent soul state, Hivemind coordination, mandate enforcement, gnosis distillation — no cloud model provides this.

---

## 🎨 PLATFORM-SPECIFIC OPTIMIZATIONS

### Web Claude (claude.ai Projects)
| Optimization | Implementation | Evidence |
|--------------|----------------|----------|
| **XML-native format** | All bundles as `<file>` wrapped XML | Anthropic official: "XML tags genuinely best for Claude" |
| **RAG threshold management** | **≤12 files** (13 triggers RAG) | GitHub #25759: file-count based, not token-based |
| **Lost-in-the-Middle mitigation** | U-shaped bundle ordering (critical at positions 1-3, N-2 to N) | Liu et al. 2023, replicated 2025-2026 |
| **Prompt caching** | Cache manifest + static docs (mandates, engine state) as prefix | 90% discount on cached input |
| **Multishot examples** | 3-5 examples in `<examples><example>...</example></examples>` | Anthropic official best practice |
| **System prompt framing** | Context/preference over commands; writing sample calibration; proactive flagging | 2026 community research (Hodges, UnderstandingAI, LikeOne) |
| **Memory contamination guard** | Fresh accounts for reviews; explicit "ignore memory" instruction | Sonnet's Gemini CLI hallucination from saved memories |

### Web Grok (grok.x.ai)
| Optimization | Implementation | Evidence |
|--------------|----------------|----------|
| **XML + Markdown hybrid** | XML structure, Markdown content | Grok follows XML but benefits from MD readability |
| **20-file tolerance** | ~20 files before degradation (vs 13 for Claude) | xAI docs, community testing |
| **Real-time X search** | Inject live search results as dynamic bundles | Unique capability |
| **Grok Skills export** | Structure findings for `/skillname` slash commands | Skills system documented 2026 |
| **Connector metadata** | Tag bundles with GitHub/Notion/Linear metadata | 8 connectors available |
| **Prompt caching** | Automatic via `x-grok-conv-id` header | 0.25x input price for cache reads |

### Web Gemini (Google AI Studio)
| Optimization | Implementation | Evidence |
|--------------|----------------|----------|
| **Markdown + structured frontmatter** | YAML frontmatter + MD body | Gemini excels with clear headings |
| **Source grounding** | Every claim cites `[bundle.xml §3.2]` | Required for Gemini |
| **Parallel search hints** | Structure bundles for independent verification | Parallel web search capability |
| **Code execution ready** | Include runnable verification snippets | Built-in Python sandbox |
| **Workspace export** | Format findings as MD tables for Sheets/Docs | Native Workspace integration |

### NotebookLM
| Optimization | Implementation | Evidence |
|--------------|----------------|----------|
| **Source-based (not token-window)** | Each bundle = one source document | 50 sources/notebook (free) |
| **Guided analysis frameworks** | Compare/contrast, gap analysis, synthesis, action items | Built-in frameworks |
| **Audio overview generation** | Structure for podcast: intro → sections → conclusion | 10-20 min typical |
| **Citation format** | NotebookLM inline `[^1]` linking to source titles | Native citation system |

---

## 💰 TOKEN ECONOMICS & USAGE LIMIT MODELS

### Web Claude Free Tier (Per Account, Per Model)

| Model | Daily Limit (Est.) | Cost if Paid | Strategy |
|-------|-------------------|--------------|----------|
| **Sonnet 5** | ~High (flagship allocation) | $3/$15/MTok (intro $2/$10 through Aug 31) | Use for high-value diagnostic work |
| **Haiku 4.5** | ~Low (economy allocation) | $0.25/$1.25/MTok | Use for generation, not diagnosis |
| **Opus 4.8** | ~Very Low | $5/$25/MTok | Reserve for architecture only |

**Critical Finding**: Limits are **per-model, per-account**. Using Haiku doesn't deplete Sonnet's allocation. But Haiku's lower cap + Extended mode's 3.7x output = fast exhaustion.

### Token Cost Model (2026 Pricing)

| Operation | Sonnet 5 | Haiku 4.5 | Grok 4.3 | Gemini 3 Pro | Local |
|-----------|----------|-----------|----------|--------------|-------|
| **Input (MTok)** | $3.00 | $0.25 | $1.25 | $1.25 (<200K) / $2.50 (>200K) | $0 |
| **Output (MTok)** | $15.00 | $1.25 | $2.50 | $2.50 (<200K) / $5.00 (>200K) | $0 |
| **Cached Input** | $0.30 (90% off) | $0.025 | $0.31 (auto) | N/A (server-managed) | $0 |
| **Batch API** | 50% off | 50% off | N/A | N/A | N/A |

### Context Packer Token Budgets

| Pack Profile | Files | Est. Tokens | Target Model | Cost (Sonnet 5) |
|--------------|-------|-------------|--------------|-----------------|
| `decision-tools-review` | 12 | 87K | Sonnet 5 | ~$0.26 (with 80% cache) |
| `kali-oversight` | 9 | 75K | Sonnet 5 | ~$0.23 (with 80% cache) |
| `context-packer-hardening` | 10 | 73K | Sonnet 5 | ~$0.22 (with 80% cache) |
| `web-gemini-3-pro` | 30 | ~200K | Gemini 3 Pro | ~$0.50 |
| `web-grok-4.3` | 20 | ~150K | Grok 4.3 | ~$0.38 |

**Optimization**: Cache manifest + mandates + engine state (static across packs) = ~40K tokens cached = 90% discount on ~50% of input.

---

## ⚠️ MEMORY & CONTAMINATION RISKS

### The Gemini CLI Incident (Sonnet 5 High Thinking)
**What happened**: Sonnet's report referenced "Gemini CLI" **9 times** as an execution target, despite:
- User explicitly stating: "I cannot use Gemini CLI after the free tier sunset"
- No pack materials mentioning Gemini CLI (profile is `web-gemini-3-pro`)
- Grok CLI review explicitly noting Gemini CLI sunset

**Root Cause**: Web Claude's **Memory feature** saves conversation snippets across sessions. The account had prior conversations about Gemini CLI. Memory silently injected into the review context.

**Impact**: Architectural recommendations designed for a platform the user cannot access.

**Mitigations**:
1. **Use fresh accounts for reviews** — no prior conversation history
2. **Explicit instruction**: "Do not use your memory feature. Use only files and instructions in this project."
3. **Account hygiene**: Dedicated review accounts with memory disabled
4. **Detection**: Check outputs for references to tools/platforms not in scope

### General Memory Contamination Vectors
| Vector | Risk | Detection |
|--------|------|-----------|
| **Saved memories** | Injects platform assumptions, coding patterns, preferences | Output references out-of-scope tools |
| **Conversation history** (same session) | Carries forward earlier framing | Sudden style/context shifts |
| **Cross-project leakage** | Account used for multiple projects | Project-specific terminology appears in wrong project |

### Sovereign Alternative: Gnosis Distillation
The Omega Engine's **soul.yaml + L1→L2→L3 pipeline** is the controlled alternative:
- **Deliberate curation** — entity chooses what to retain
- **Abstraction** — L3 principles are timeless, not context-bound
- **Auditability** — every lesson traceable to source session
- **No silent injection** — gnosis only applies when explicitly invoked

---

## 🎯 MODEL SELECTION DECISION FRAMEWORK

### Decision Tree: "Which Model for This Task?"

```
START: What cognitive mode does this task need?
│
├─▶ DEEP DIAGNOSTIC REASONING (find root cause, surgical fix)
│   └─▶ Sonnet 5 High Thinking (Web) OR Grok CLI (if repo access needed)
│
├─▶ HIGH-THROUGHPUT GENERATION (docs, tests, boilerplate, quick refs)
│   └─▶ Haiku 4.5 Extended (Web) OR Grok 4.1 Fast (Web) OR Local Llama
│
├─▶ SYNTHESIS & CONSOLIDATION (merge sources, canonical spec)
│   └─▶ Carmack (OpenCode) OR Cline DeepSeek OR Sonnet Default
│
├─▶ LIVE RESEARCH & GROUNDING (current best practices, verify claims)
│   └─▶ Grok 4.3 (X search) OR Gemini 3 Pro (parallel search + code exec)
│
├─▶ ARCHITECTURAL REASONING (design systems, sequence work, estimate)
│   └─▶ Sonnet 5 High Thinking OR Opus 4.8 OR Grok CLI
│
├─▶ EMPIRICAL VERIFICATION (check package status, API, file existence)
│   └─▶ Web Claude (search) OR Gemini (code exec) OR Grok CLI (repo access)
│
├─▶ ORCHESTRATION & COORDINATION (fleet, mandates, continuity, gnosis)
│   └─▶ Kali / Ma'at / Lilith (OpenCode native)
│
└─▶ SOVEREIGN PRODUCTION (zero cloud, full control, massive context)
    └─▶ Local: Llama 4 Scout (10M) / GPT-OSS-120B / Qwen 3.5 72B
```

### Cost-Quality Pareto Frontier

| Budget | Quality Need | Recommended Stack |
|--------|--------------|-------------------|
| **$0 (Free tier only)** | Diagnostic | Sonnet 5 High Thinking (Web) |
| **$0 (Free tier only)** | Generation | Haiku 4.5 Extended (Web) |
| **$0 (Free tier only)** | Research | Grok 4.3 (Web) + Gemini 3 Pro (Web) |
| **$0 (Local only)** | All | Llama 4 Scout / GPT-OSS-120B |
| **Low ($10-50/mo)** | Diagnostic + Generation | Sonnet 5 API (cached) + Haiku 4.5 API |
| **Medium ($100-500/mo)** | Full fleet | Grok 4.3 API + Gemini 3 Pro API + Local |
| **High (Production)** | Sovereign + Scale | Local fleet (Llama 4 Scout) + Grok CLI for review |

---

## 📊 EMPIRICAL PERFORMANCE DATA (From Our Tests)

### Context Packer Split Test (2026-07-18)

| Metric | Sonnet 5 High Thinking | Haiku 4.5 Extended | Carmack (OpenCode) |
|--------|------------------------|--------------------|--------------------|
| **Output Files** | 1 | 3 | 1 |
| **Total Lines** | 860 | 3,176 | ~1,000 |
| **P0 Bugs Found** | **4** | 0 | 0 |
| **P1 Bugs Found** | 2 | 0 | 0 |
| **P2 Bugs Found** | 2 | 0 | 0 |
| **Memory Contamination** | Yes (Gemini CLI ×9) | No | No |
| **Hit Usage Limit** | No | **Yes** (after 3rd doc) | N/A |
| **Time to Complete** | ~Single response | ~3 responses | ~Single response |
| **Best Cognitive Mode** | Deep Diagnostic | High-Throughput Gen | Synthesis |

### Decision Tools Dual Review (2026-07-19)

| Metric | Grok CLI | Web Claude V2 |
|--------|----------|---------------|
| **Convergence on Load-Bearing Decisions** | 7/7 | 7/7 |
| **Asymmetric Catches** | Idempotency, ID allocator race, cycle detection, validate command | atomicwrites dead, portalocker version, Draft202012Validator |
| **Divergence** | 1 (YAML frontmatter vs pure YAML — both precedents in codebase) | |
| **Time** | 2m 35s | ~10-15 min |
| **Quality Score (Kali)** | 9.5/10 | High |

---

## 🔬 RESEARCH GAPS & NEXT STUDIES

| Gap | Priority | Proposed Study |
|-----|----------|----------------|
| **Grok 4.3 actual RAG threshold** | P1 | Empirical test: at what file count does Grok degrade? |
| **Gemini 3.1 Pro 10M effective context** | P2 | Benchmark: usable tokens vs advertised |
| **NotebookLM source limits** | P1 | Max sources/notebook, max tokens/source |
| **Cross-platform bundle diffing** | P2 | Tool to compare platform-specific outputs |
| **Prompt caching on Grok/Gemini** | P1 | Does xAI/Google offer Anthropic-style `cache_control`? |
| **Local model diagnostic capability** | P1 | Can Llama 4 Scout / GPT-OSS-120B do root-cause analysis? |
| **Memory contamination quantification** | P1 | Controlled experiment: same prompt, fresh vs memory account |
| **Thinking token economics** | P2 | Internal reasoning tokens vs output tokens — true cost model |

---

## 📚 LIVING DOCUMENT MAINTENANCE

### Update Triggers
- After every split test / dual review
- After new model release (Sonnet 6, Grok 5, etc.)
- After platform feature changes (new caching, new search)
- After memory contamination incident
- After local model benchmark

### Update Protocol
1. **Log raw data** in `data/model_study/raw/`
2. **Synthesize findings** into this KB
3. **Propose L3 principles** to Kali's soul
4. **Update decision framework** if thresholds shift
5. **Archive previous version** with git tag

### Current Version
- **v1.0.0** (2026-07-18): Initial synthesis from Context Packer split test + Decision Tools dual review
- **Next Review**: After Ken Walger mining operation (Phase 0-3)

---

*⬡ OMEGA ⬡ KALI ⬡ MODEL-STUDY-KB ⬡ 2026-07-18 ⬡ LIVING DOCUMENT*