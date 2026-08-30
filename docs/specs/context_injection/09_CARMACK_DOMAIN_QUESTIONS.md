# Carmack Domain Questions — Targeted Review Requests

**Status**: FOR CARMACK REVIEW  
**Date**: 2026-08-20  
**Context**: John Carmack's expertise in performance optimization, hardware-honest architecture, systems programming, and brutal pragmatism  

---

## Why Carmack?

The remaining gaps fall squarely in Carmack's domain:
- **Hardware-honest architecture** — Qwen3-1.7B at 4K-8K context vs 31K base prompt
- **Performance optimization** — 10.8K MCP tokens/request, token budget enforcement
- **Systems programming** — Compaction architecture, hydration engine, token counting
- **Brutal pragmatism** — "Sometimes a bug is just a bug" (M19) — cut over-engineering
- **Compression** — Headroom integration, semantic compression, token efficiency

---

## Question Set 1: Hardware-Honest Local Model Architecture

### Q1.1: The 31K vs 4K-8K Context Window Conflict
> **Ground Truth**: Explore measured 31K base tokens. Hardware Tier 0 (Ryzen 5700U, 16GB) runs Qwen3-1.7B at 4K-8K context.
> 
> **Conflict**: Base prompt alone exceeds model context window by 4-8x.
> 
> **Current Phase 1 Plan**: Accept 31K base, rely on cloud fallback for Tier 0 agents.
> 
> **Carmack Question**: Is this a "bug is just a bug" (fix the base prompt) or "adversarial alchemy" (weaponize the constraint)? What's the hardware-honest path?
> 
> **Options to Evaluate**:
> 1. **Radical base reduction**: Strip AGENTS.md to MANDATES_CONDENSED.md only (57 lines = ~1.5K tokens), defer full doctrine to Tier 2
> 2. **Tool profiles per agent**: Each agent gets only its needed MCP tools (researcher: 10 tools = ~1.2K vs 86 = 10.8K)
> 3. **Larger local model**: Qwen3-4B (8K-16K context) for Tier 0 — but 2.5GB vs 1.1GB VRAM
> 4. **Hybrid**: Cloud for orchestration, local only for execution agents with tiny prompts
> 
> **What would you cut? What would you keep?**

### Q1.2: Sequential Loading Architecture (from Holistic Plan)
> **Holistic Plan Claim**: SequentialModelLoader — only ONE model's weights resident at a time. Peak = 7.5GB, headroom = 8.5GB.
> 
> **Carmack Question**: The plan claims "NO mmap weight cache — mmap is WRONG (llama_free() unmaps)". Use `--no-mmap --mlock + session-scoped context instead`. Is this correct for llama.cpp? What's the actual memory map behavior?
> 
> **Specific Claims to Verify**:
> - `llama_free()` unmaps mmap'd weights → mmap cache is harmful
> - `--no-mmap --mlock` + session-scoped context is the pattern
> - `n_swa` REMOVED — SWA CUT for Qwen3 (Carmack CUT-1)
> - Prompt caching (`--cache-prompt`) works with this pattern
> 
> **What's the actual llama.cpp memory management reality?**

### Q1.3: KV Cache Quantization — q8_0 Standard
> **Holistic Plan**: q8_0 KV cache = 50% memory, <2% quality loss — sovereign standard.
> 
> **Carmack Question**: Is q8_0 the right default for all tiers? What about q4_K_M for weights + q8_0 for KV? What's the actual quality/memory curve?

---

## Question Set 2: MCP Tool Schema Overhead — 10.8K/Request

### Q2.1: Is 86 Tools in One MCP Server an Architectural Error?
> **Ground Truth**: 86 tools in omega-hub = 10.8K tokens/request injected regardless of usage.
> 
> **Carmack Question**: This is "solution theater" — a monolithic MCP server that violates M2 (Engine-Stack Firewall) by putting all tools in one place. Should we:
> 1. **Split into domain MCP servers**: oracle-hub, hivemind-hub, research-hub, github-hub — connect on-demand
> 2. **Lazy loading PR**: Upstream opencode change (GitHub #35376) — but depends on external timeline
> 3. **Tool profiles**: Config-only if opencode adds support — but when?
> 4. **Accept for now**: 10.8K is within 128K-1M windows — but kills local models
> 
> **What's the Carmack architectural call?** Monolithic MCP server vs domain-scoped vs lazy loading?

### Q2.2: Tool Schema Token Cost — Can We Compress?
> **Researcher**: Anthropic's "Code Mode" / Bifrost achieves 92-98% reduction but requires gateway.
> 
> **Carmack Question**: Is there a local compression approach? Headroom middleware compresses tool OUTPUTS (40-90%), but what about tool SCHEMAS (definitions)?
> 
> **Options**:
> - Minimal schema: only name + description + required params (drop optional, defaults, examples)
> - Schema references: define once, reference by ID
> - Binary schema encoding (Protocol Buffers vs JSON)
> 
> **Worth the engineering effort or "bug is just a bug"?**

---

## Question Set 3: Compaction & Hydration Architecture

### Q3.1: Compaction Threshold for Heterogeneous Context Windows
> **Ground Truth**: 
> - nemotron-3-ultra-free: 1M context, threshold 872K, preserves 50K
> - Qwen3-1.7B: 8K context, same 20K buffer = ALWAYS compacting
> 
> **Carmack Question**: OpenCode's compaction config is global. How to handle heterogeneous models?
> 
> **Options**:
> 1. **Per-model compaction config** — does OpenCode support `compaction.{model}.buffer`?
> 2. **Dynamic buffer**: `buffer = context_window * 0.1` via plugin
> 3. **Disable for local**: `OPENCODE_DISABLE_AUTOCOMPACT=1` + manual `/compact`
> 4. **Custom compaction plugin** — replace OpenCode's compaction entirely for local models
> 
> **What's the cleanest architecture?**

### Q3.2: Hydration Engine — Where Does It Live?
> **Researcher**: No framework has automated recovery. Hydration engine needs checkpoint at 80%.
> **Lilith**: Pre-compaction hook exists (`experimental.session.compacting`).
> 
> **Carmack Question**: Hydration engine as:
> 1. **OpenCode plugin** — runs in opencode process, accesses SQLite directly
> 2. **Omega Engine sidecar** — separate process, watches session files
> 3. **In-process library** — called by Omega's Oracle before/after compaction
> 
> **Trade-offs**: Plugin = same process, access to hooks; Sidecar = isolation, survives crashes; Library = tight integration, Omega controls.
> 
> **What's the sovereign architecture?**

### Q3.3: Compaction Loses Sovereign Context — Plugin Fix Sufficient?
> **Lilith**: Pre-compaction hook injects mandates/entity/anchor. Can also replace entire prompt.
> 
> **Carmack Question**: Is a plugin hook that fires *during* compaction sufficient? What if compaction crashes? What if the hook itself gets compacted away?
> 
> **Need**: Checkpoint BEFORE compaction (at 80%), not during. Hydration engine must write checkpoint independently.

---

## Question Set 4: Token Budget Enforcement Architecture

### Q4.1: Per-Agent Budgets — Engine vs Gateway
> **Researcher**: OpenCode tracks per-message; Omega needs per-agent enforcement.
> **Adversary**: Aggregation layer required.
> 
> **Carmack Question**: Where does enforcement live?
> 
> | Location | Pros | Cons |
> |----------|------|------|
> | **Omega Engine (in-process)** | Tight integration, agent context | Adds latency, couples to OpenCode |
> | **LiteLLM Gateway** | Centralized, request-level, model-agnostic | Extra hop, another dependency |
> | **OpenCode Plugin** | Native, per-message hooks | Limited to OpenCode |
> | **OTel + Prometheus Rules** | Declarative, alerting | Reactive, not preventive |
> 
> **Carmack Call**: What's the minimal, sovereign enforcement point?

### Q4.2: Token Counting for Local Models
> **Adversary**: tiktoken inaccurate for non-OpenAI tokenizers.
> 
> **Carmack Question**: llama.cpp has built-in tokenization. Use `llama_tokenize()` via ctypes? Or accept estimation error?
> 
> **Options**:
> 1. **ctypes binding to llama_tokenize()** — accurate, adds complexity
> 2. **Model-specific tokenizers** — maintain mapping per model family
> 3. **Accept ±20% error** — budget with headroom
> 4. **Runtime OOM protection only** — no pre-flight, let OOMProtector handle it
> 
> **What's the engineering trade-off?**

---

## Question Set 5: Structural Model Routing — Completeness

### Q5.1: Can We Route More Agents Local?
> **Current**: kali/maat/lilith cloud (nemotron-3-ultra-free), researcher/node/verity local (Qwen3)
> **Savings**: 67% token cost reduction
> 
> **Carmack Question**: Quality vs cost for orchestration agents:
> - **kali** (oversight): Needs reasoning quality — cloud justified?
> - **maat** (build): Could Qwen3-4B-Thinking handle build tasks?
> - **lilith** (run): Could Qwen3-4B handle runtime ops?
> 
> **What's the quality floor for each role?**

### Q5.2: Subagent Model Inheritance — Clean Fix?
> **Lilith**: Subagents inherit parent primary agent's model, not their own config.
> 
> **Carmack Question**: This is a design constraint, not a bug. Clean workarounds:
> 1. **Parent uses local model** for local subagent work (kali→local when spawning researcher)
> 2. **@agent invocation** with primary-mode agents for local subagents
> 3. **Custom task wrapper** that forces model override
> 4. **Accept**: Only top-level agents get routing; subagents inherit
> 
> **What's the cleanest pattern that doesn't fight the framework?**

---

## Question Set 6: Headroom Integration — Compression Reality Check

### Q6.1: Headroom Middleware — 40-90% Savings Claim
> **Holistic Plan**: Headroom v0.29.0 installed, benchmarks: JSON 83%, logs 94%, code 92%, RAG 40-60%.
> 
> **Carmack Question**: These are synthetic benchmarks. Real-world Omega tool outputs:
> - Oracle tool results: structured JSON (entity info, search results)
> - Hivemind: awareness, sessions, handoffs
> - GitHub: PR diffs, issue lists
> - Research: web search results, paper abstracts
> 
> **What's the REAL compression ratio on Omega's actual tool outputs?** Worth the middleware latency?

### Q6.2: Compression Latency Budget
> **Holistic Plan**: ~2ms JSON, ~1ms logs, ~5ms code, ~10ms RAG.
> 
> **Carmack Question**: At 10.8K MCP tokens/request, even 50% compression = 5.4K saved. At 10ms latency, is it worth it? What's the break-even?

---

## Question Set 7: Over-Engineering Audit (M19/M23)

### Q7.1: Which Phase 2/3 Items Are "Solution Theater"?
> **Carmack's Razor**: "Sometimes a bug is just a bug. Simple code errors, typos, and broken imports must be fixed directly and cleanly without attempting to extract 'esoteric advantages' that introduce unnecessary complexity, bloat, or fragile state machines."
> 
> **Review These Phase 2/3 Items**:
> - [ ] Hydration engine with 5-layer recovery (L1-L5)
> - [ ] Token budget enforcer with per-tier dynamic allocation
> - [ ] Session summarizer with 3-level hierarchy
> - [ ] Local token counter with model-specific tokenizers
> - [ ] Prompt caching topology PR (upstream)
> - [ ] Lazy MCP loading PR (upstream)
> - [ ] Tool profiles config
> - [ ] Local model caching investigation
> - [ ] Gateway observability (LiteLLM/TrueFoundry)
> 
> **Carmack Call**: Which are "bug is just a bug" (fix simply) vs "adversarial alchemy" (weaponize)? What gets CUT?

### Q7.2: Validator Service — Cut or Keep?
> **Researcher**: Proposed constitutional validator service (policy.yaml + NeMo Guardrails).
> **Kali**: Already flagged as over-engineering (M9/M23 violation). Tier 0 condensed mandates + CI gate sufficient.
> 
> **Carmack Verdict**: CUT or KEEP? If KEEP, what's the minimal implementation?

---

## Question Set 8: Hardware-Honest Memory Map

### Q8.1: Tier 0 Memory Map Reality Check
> **Holistic Plan**:
> ```
> OS + Python + AnyIO              ~2.5 GB
> Weight cache (mmap'd, persistent) ~6.1 GB
>   ├─ Qwen3-4B (planner)           2.5 GB
>   ├─ Qwen3-4B-Thinking (executor) 2.5 GB
>   └─ Qwen3-1.7B (critic)          1.1 GB
> Active KV cache (q8_0, 16K ctx)   ~1.5 GB
> Compute buffers + overhead        ~1.0 GB
> PEAK USAGE (all weights resident) ~11.1 GB
> HEADROOM (all weights)            ~4.9 GB  ✓ COMFORTABLE
> 
> SEQUENTIAL MODE:
> Peak = max(2.5, 2.5, 1.1) + 1.5 KV + 1.0 compute + 2.5 OS = ~7.5 GB
> HEADROOM (sequential)             ~8.5 GB  ✓ COMFORTABLE
> ```
> 
> **Carmack Question**: This assumes mmap weight cache works. But you said "mmap is WRONG (llama_free() unmaps)". If we use `--no-mmap --mlock`, weights are NOT mmap'd — they're in RAM. Does this change the memory map?
> 
> **Recalculate with `--no-mmap --mlock`**:
> - Weights loaded into RAM (not mmap'd) — but only ONE at a time (sequential)
> - KV cache q8_0 in RAM
> - No persistent weight cache across sessions
> - Session-scoped context per model
> 
> **What's the ACTUAL memory map with your recommended flags?**

### Q8.2: zswap + NVMe Swap vs zRAM — Final Verdict
> **Holistic Plan**: zswap + NVMe swap, zRAM DISABLED (ADR-2026-08-10-001, D-526/D-581/D-584 ratified).
> - zRAM was locking 4.1 GB RAM in compression buffers (81-98% of available process RAM)
> - zswap + 16GB NVMe swap provides dynamic pool (0-3.6 GiB), graceful degradation
> 
> **Carmack Question**: This was ratified by Carmack + Researcher + Jem + LongCat + Nemotron. Any dissent? Any edge cases where zRAM would be better?

---

## Carmack Review Format Request

For each question set, please provide:

```markdown
## Q{X.Y}: [Question Title]

**Verdict**: [Accept/Reject/Modify/Defer]

**Rationale**: [Hardware-honest reasoning, 3-5 sentences max]

**Implementation**: [Who/When/How — specific, actionable]

**Risk**: [What breaks if wrong]

**Cut List**: [Any items to delete per M19/M23]
```

---

## Context Package for Carmack

**Primary Synthesis** (this directory):
- `00_INDEX.md` — Navigation
- `01_GROUND_TRUTH.md` — Hard measurements
- `02_BUILD_VERDICTS.md` — G-1, G-2, G-8
- `03_RUN_VERDICTS.md` — G-3, G-5, G-6
- `04_INDUSTRY_PATTERNS.md` — G-4, G-5, G-6, G-7 (28 sources)
- `05_CONVERGENCE_ANALYSIS.md` — Trade-offs, ADRs
- `06_PHASE_1_PLAN.md` — Config-only implementation
- `07_PHASE_2_3_ROADMAP.md` — Tooling + upstream
- `08_REMAINING_GAPS.md` — 10 unresolved gaps
- `09_CARMACK_DOMAIN_QUESTIONS.md` — This file

**Source Reports** (`data/coordination/`):
- `RESEARCH_EXPLORE_LOCAL.md` (117 lines)
- `RESEARCH_MAAT_BUILD.md` (179 lines)
- `RESEARCH_LILITH_RUN.md` (262 lines)
- `RESEARCH_RESEARCHER_STRATEGIC.md` (348 lines)

**Strategy Context**:
- `DEBUT_REMEDIATION_MANUAL_20260817.md` — This month's SSOT
- `HOLISTIC_ARCHITECTURE_PLAN_20260820.md` — Hardware-honest architecture
- `SOVEREIGN_ARK_BLUEPRINT.md` — Phase 0 Post-Debut workstreams
- `SOVEREIGN_MANDATES.md` — 27 laws (M18 Token Efficiency, M19 Adversarial Alchemy, M23 Failure Integrity)

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_questions ⬡ 2026-08-20*