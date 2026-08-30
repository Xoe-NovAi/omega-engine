# Remaining Gaps — Unresolved Questions for Carmack Review

**Status**: OPEN — Requires Carmack's architectural judgment  
**Date**: 2026-08-20  

---

## Gap Categories

### 🔴 Critical (Block Phase 1 Decisions)

#### RG-1: Local Model Viability with 31K Base Prompt
**Question**: Qwen3-1.7B (4K-8K context) vs 31K base system prompt — is this workable?
- Explore measured 31K base tokens (AGENTS.md + MCP + env + agent)
- Qwen3-1.7B context window: 4K-8K (per Hardware Tier 0)
- **Conflict**: Base prompt alone exceeds model context window
- **Options**:
  1. Reduce base prompt further (how? MCP is 10.8K, AGENTS.md is 20K)
  2. Use larger local model for Tier 0 agents (Qwen3-4B: 8K-16K?)
  3. Accept cloud fallback for Tier 0 agents (violates M7 Local-First)
  4. Architect tool profiles to reduce MCP per agent (Phase 2)
- **Need Carmack's call**: What's the hardware-honest path?

#### RG-2: MCP Tool Schema Overhead — 10.8K/Request
**Question**: 86 tools = 10.8K tokens/request. Is this acceptable for local models?
- Explore: 10.8K/request injected regardless of usage
- Ma'at: Exceeds mandate content we want to inject
- Researcher: Lazy loading PR needed (GitHub #35376)
- **Options**:
  1. Accept for Phase 1 (within 128K-1M cloud windows)
  2. Split omega-hub into domain-scoped MCP servers (connect on-demand)
  3. Tool profiles (dev/deploy/debug) — Phase 2 if opencode supports
  4. Build custom tool registry with lazy loading — upstream PR
- **Need Carmack's call**: Architectural direction — split servers vs lazy loading vs accept?

#### RG-3: Subagent Inheritance × Local Model Routing
**Question**: Subagents inherit parent's model, not their own config. How to route local?
- Lilith: Subagents use parent primary agent's model, not their own config
- Researcher: Structural routing captures 70%+ savings without classifier overhead
- **Conflict**: If kali (cloud) spawns researcher subagent, researcher gets cloud model
- **Options**:
  1. Parent agents for local work must use local models (kali→local for research tasks)
  2. Use `@agent` invocation with primary-mode agents for local subagents
  3. Build custom task() wrapper that forces model override
  4. Accept: only top-level agents get model routing; subagents inherit
- **Need Carmack's call**: What's the cleanest architecture?

---

### 🟡 High (Block Phase 2 Architecture)

#### RG-4: Compaction Threshold for Local Models
**Question**: 200K cloud context vs 8K-32K local — buffer must scale with context window
- Researcher: OpenCode buffer default 20K; keep.tokens 15K
- Lilith: For nemotron-3-ultra-free (1M/128K) threshold = 872K, preserves 50K
- **Problem**: Qwen3-1.7B (8K context) with 20K buffer = compaction ALWAYS
- **Options**:
  1. Per-model compaction config (OpenCode supports model-specific?)
  2. Dynamic buffer: `buffer = context_window * 0.1` (10%)
  3. Disable auto-compaction for local models (`OPENCODE_DISABLE_AUTOCOMPACT=1`)
  4. Custom compaction logic via plugin for local models
- **Need Carmack's call**: How to handle heterogeneous context windows?

#### RG-5: Token Budget Enforcement — Per-Agent vs Per-Session
**Question**: OpenCode tracks per-message; Omega needs per-agent budget enforcement
- Researcher: OpenCode SQLite tracks per-message tokens; budget enforcement needs aggregation
- Adversary: Per-agent budgets require aggregation layer
- **Options**:
  1. Build aggregation in Hydration Engine (Phase 2)
  2. Use OpenCode's per-message data + agent attribution
  3. Gateway-level enforcement (LiteLLM/TrueFoundry)
  4. Accept: measurement only, no enforcement (violates M18)
- **Need Carmack's call**: Where does enforcement live — engine, gateway, or both?

#### RG-6: Local Model Token Counting Accuracy
**Question**: tiktoken inaccurate for non-OpenAI tokenizers (Adversary finding)
- Researcher: Use tiktoken/@anthropic-ai/tokenizer for pre-flight
- Adversary: tiktoken is inaccurate for non-OpenAI tokenizers
- **Options**:
  1. Use model-specific tokenizers (llama.cpp has built-in?)
  2. Accept estimation error margin (±20%)
  3. Build tokenizer mapping per model family
  4. Skip pre-flight for local; rely on runtime OOM protection
- **Need Carmack's call**: What's the engineering trade-off?

---

### 🟢 Medium (Architectural Direction)

#### RG-7: Prompt Caching for Local Models
**Question**: llama.cpp prefix caching vs Anthropic explicit breakpoints — different architectures
- Researcher: llama.cpp supports `enable_prefix_caching=True` (vLLM-style)
- Researcher: OpenCode's `applyCaching()` is provider-agnostic but cloud-focused
- **Options**:
  1. Investigate llama.cpp prefix caching for native-gguf backend
  2. Build custom cache layer for local models
  3. Accept: no caching for local (cloud gets 90% discount, local doesn't need it)
- **Need Carmack's call**: Worth the engineering effort?

#### RG-8: Gateway vs In-Process Observability
**Question**: LiteLLM/TrueFoundry gateway vs in-process OTel export
- Researcher: Gateway adds request-level observability; in-process needs aggregation
- Security: Never log raw prompts to third-party SaaS (OpenLegion 2026-07-10)
- **Options**:
  1. In-process OTel → local Prometheus/Grafana (sovereign)
  2. LiteLLM gateway local deployment (adds hop, centralizes)
  3. Both: OTel for metrics, gateway for request tracing
- **Need Carmack's call**: Architecture preference?

#### RG-9: Tool Profiles vs Lazy Loading vs Split Servers
**Question**: Three approaches to MCP overhead — which to prioritize?
- Ma'at: Tool profiles (dev/deploy/debug) if opencode supports
- Researcher: Lazy loading PR (GitHub #35376)
- Alternative: Split omega-hub into domain-scoped MCP servers
- **Options**:
  1. Lazy loading PR (upstream, highest leverage)
  2. Tool profiles (config-only, if opencode adds support)
  3. Split servers (architectural, highest isolation)
  4. All three in sequence
- **Need Carmack's call**: Priority ordering?

#### RG-10: Structural Routing Completeness
**Question**: 4/6 agents local = 67% savings. Can we get higher?
- Current: kali/maat/lilith cloud, researcher/node/verity local
- **Options**:
  1. Move maat to local (build tasks on Qwen3-4B?)
  2. Move lilith to local (run tasks on Qwen3-4B?)
  3. Keep cloud for orchestration agents (reasoning quality)
  4. Hybrid: cloud for planning, local for execution
- **Need Carmack's call**: Quality vs cost trade-off for orchestration agents?

---

## Decision Framework for Carmack

For each gap, please provide:
1. **Verdict**: Accept/Reject/Defer/Modify
2. **Rationale**: Hardware-honest reasoning
3. **Implementation**: Who/when/how
4. **Risk**: What breaks if wrong

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_remaining_gaps ⬡ 2026-08-20*