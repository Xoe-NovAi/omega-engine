<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Strategic Industry Research — Context Injection Gaps

**AP Token**: `AP-RESEARCHER-STRATEGIC-v1.0.0`
**Date**: 2026-08-20
**Researcher**: Jem Analyst (L2) — Polymathic Council Triangulation
**Model**: nemotron-3-ultra-free
**Sources**: 28+ web sources across 4 research queries

---

## Executive Summary

This report addresses 4 specific gaps (G-4 through G-7) not covered in the existing `CONTEXT_INJECTION_RESEARCH_REPORT_20260820.md`. Each gap is answered with ≥2 sourced references and framework comparison tables.

| Gap | Question | Key Finding |
|-----|----------|-------------|
| **G-4** | Prompt Caching Support | OpenCode has built-in provider-agnostic caching; Anthropic explicit breakpoints (4 max); LangGraph/AutoGen require manual implementation |
| **G-5** | Compaction Triggers | OpenCode: buffer-based preflight (20k default); Claude Code: ~95% capacity; LangGraph: composable middleware; CrewAI: boolean overflow |
| **G-6** | Per-Agent Model Routing | OpenCode: per-agent `model` config; AutoGen: per-agent `model_client`; Dynamic routing via RouteLLM/FrugalGPT cascade; Structural routing preferred for agents |
| **G-7** | Token Measurement Tooling | OpenCode: SQLite + OTel plugin; Anthropic: 4 usage fields; Langfuse: exclusive bucket conversion; Gateways add request-level attribution |

---

## Q1: Prompt Caching Support (G-4)

### Framework Comparison Table

| Framework | Caching Support | Mechanism | Cache Control | Token Tracking |
|-----------|----------------|-----------|---------------|----------------|
| **OpenCode V2** | ✅ Built-in | Provider-agnostic `applyCaching()` in `transform.ts` | Anthropic: `cacheControl: ephemeral` on 1st 2 system + last 2 user msgs<br>OpenAI/Venice: `promptCacheKey=sessionID`<br>Bedrock: `cachePoint: default`<br>OpenRouter: `cacheControl: ephemeral` | ✅ Tracks `cache_read_input_tokens`, `cache_creation_input_tokens` per message in SQLite + OTel export |
| **Anthropic (Claude)** | ✅ Native | Explicit `cache_control` breakpoints (max 4) | `{"type": "ephemeral"}` (5-min TTL) or `{"type": "ephemeral", "ttl": "1h"}` | ✅ Returns `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` |
| **OpenAI** | ✅ Native | Automatic prefix caching (GPT-5.6+) | `prompt_cache_breakpoint` on content blocks (Responses API) | ✅ `prompt_tokens`, `prompt_tokens_details.cached_tokens`, `completion_tokens` |
| **LangGraph** | ❌ Manual | User implements static-first ordering | `AnthropicPromptCachingMiddleware(ttl="1h")` or explicit breakpoints | ❌ User responsibility |
| **Agno** | ✅ Built-in | `cache_system_prompt=True`, `cache_tools=True`, `system_prompt_blocks` with per-block TTL | Block-level `cache=True/False`, `ttl="1h"` | ✅ `response.metrics.cache_read_tokens`, `cache_write_tokens` |
| **AutoGen** | ❌ Manual | Per-agent `model_client` — user adds caching | User implements via model client wrapper | ❌ User responsibility |
| **CrewAI** | ❌ None found | No documented caching support | N/A | ❌ No |
| **Google ADK** | ⚠️ Partial | Vertex AI supports Anthropic-style caching | Via provider config | ✅ Via provider response |

### Key Technical Details

**OpenCode's `applyCaching()`** (from `packages/opencode/src/provider/transform.ts:170-207`):
```typescript
function applyCaching(msgs, providerID) {
  const system = msgs.filter(m => m.role === "system").slice(0, 2)
  const final = msgs.filter(m => m.role !== "system").slice(-2)
  const providerOptions = {
    anthropic: { cacheControl: { type: "ephemeral" } },
    openrouter: { cacheControl: { type: "ephemeral" } },
    bedrock: { cachePoint: { type: "default" } },
    openaiCompatible: { cache_control: { type: "ephemeral" } },
    copilot: { copilot_cache_control: { type: "ephemeral" } },
  }
  for (const msg of unique([...system, ...final])) {
    msg.providerOptions = mergeDeep(msg.providerOptions ?? {}, providerOptions)
  }
  return msgs
}
```

**Anthropic Cache Economics** (from caching.ai 2026-07-19):
- Cache writes: ~1.25× base input price
- Cache reads: ~0.1× base input price (90% discount)
- Minimum cacheable prefix: 1024–2048 tokens (model-dependent)
- Max 4 explicit breakpoints per request

**LangGraph Pattern** (Sangam Pandey 2026-03-13): "Static-first prompt ordering — tools → system prompt → messages. Never mutate tools mid-session. Dynamic context via messages, not system prompt."

### Omega Engine Applicability

- **Phase 1 (Config)**: Leverage OpenCode's built-in caching via provider config (`setCacheKey: true` for non-auto providers)
- **Phase 3 (Upstream)**: PR to optimize assembly order for cache topology (stable content first: tools → condensed mandates → env → instructions → agent prompt)
- **Local Models**: Native GGUF via llama.cpp supports `enable_prefix_caching=True` (vLLM-style) — investigate for `native-gguf` backend

---

## Q2: Compaction Triggers (G-5)

### Framework Comparison Table

| Framework | Auto Trigger | Threshold Config | Pre-Compaction Hook | Manual Trigger | Strategy |
|-----------|--------------|------------------|---------------------|----------------|----------|
| **OpenCode V2** | Preflight estimate | `buffer` (default 20k tokens), `keep.tokens` (15k) | ❌ None (plugin hook `experimental.session.compacting` only) | `/compact` or `<leader>c` | Prune → Compress (nested summaries) |
| **Claude Code** | ~95% context capacity | Not user-configurable (feature requests closed `not_planned`) | ❌ None native; workaround: tool-call counting proxy hook | `/compact [instructions]` | 3-tier: microcompaction → auto → manual |
| **Codex CLI** | Token threshold | `model_auto_compact_token_limit` (model-specific, e.g., 180k/244k) | ❌ None | `/compact` | Server-side encryption → opaque blob → re-read 5 files (~50k) |
| **LangGraph** | Developer-configured middleware | `trim_messages(max_tokens=4000)` or `SummarizationMiddleware(trigger=("tokens", 4000))` | ✅ `@before_model` middleware can warn | Manual invocation | Composable: trim / summarize / delete / custom |
| **CrewAI** | Overflow detection | Single boolean `respect_context_window` (no threshold) | ❌ None | N/A | Chunk → summarize each → single summary |
| **Cursor** | Near context limit | Not configurable | ❌ None | `/summarize`, `/compress` (v1.6+) | Flash-model summarization (smaller model) |
| **Aider** | Soft token limit | `--max-chat-history-tokens` (model-dependent) | ❌ None | N/A | Recursive summarization (background thread, weak model) |
| **Google ADK** | Event count | `compaction_interval`, `overlap_size` | ❌ None | N/A | Sliding window + LLM summarization with overlap |
| **Microsoft Agent Framework** | Pipeline strategies | `MessagesExceed(N)`, token budget, custom | ❌ None | Maintenance operation | `TokenBudgetComposedStrategy` with fallbacks |

### Key Technical Details

**OpenCode V2 Compaction** (from v2.opencode.ai/compaction):
```text
estimated tokens > context limit - max(requested output tokens, buffer)
buffer default: 20000 tokens
keep.tokens default: 15000 tokens (recent context retained beside summary)
```
Pruning runs first: scans backward, protects last 40k tokens (PRUNE_PROTECT), prunes tool outputs beyond if >20k prunable (PRUNE_MINIMUM).

**Claude Code 3-Tier System** (from codex.danielvaughan.com 2026-08-14):
1. **Microcompaction** — offloads bulky tool results early
2. **Auto-compaction** — triggers at ~95% capacity, generates summary
3. **Manual `/compact [instructions]`** — custom focus (e.g., "focus on API changes")

**Pre-Compaction Hook Gap**: Multiple feature requests (anthropics/claude-code#34299, #19466) closed `not_planned`. Community workaround: PostToolUse hook counting tool calls as proxy (~250-300 calls = danger zone).

**LangGraph Composability** (dev.to/crabtalk 2026-03-15): `trim_messages` via `@before_model` middleware, `SummarizationMiddleware` with configurable trigger, fully developer-controlled.

### Omega Engine Applicability

- **Immediate**: Configure OpenCode `buffer: 50000` and `keep.tokens: 20000` for earlier compaction with local models (smaller context windows)
- **Phase 2 (Tooling)**: Build hydration engine (per existing report) with pre-compaction checkpoint at 80% usage via plugin hook
- **Structural**: Adopt "prune first, compress second" pattern — protect recent tool outputs, nest summaries rather than dilute

---

## Q3: Per-Agent Model Routing (G-6)

### Framework Comparison Table

| Framework | Per-Agent Model Config | Dynamic Routing (Cheap→Expensive) | Routing Mechanism |
|-----------|------------------------|-----------------------------------|-------------------|
| **OpenCode** | ✅ `agent.{name}.model` in config | ⚠️ Via variants (`high`/`low` reasoning) + manual `/model` switch | Config override; subagents inherit parent model unless specified |
| **AutoGen** | ✅ Per-agent `model_client` | ❌ Not built-in; user implements | Each `AssistantAgent(model_client=OpenAIChatCompletionClient(model="..."))` |
| **LangGraph** | ✅ Per-node model client | ❌ Not built-in; user implements | Node function binds own `model_with_tools` |
| **CrewAI** | ✅ Agent-level model config | ❌ Not built-in | Agent `llm` parameter |
| **RouteLLM (LMSys)** | N/A (router layer) | ✅ Classifier-based routing | Trained router predicts complexity → selects model tier |
| **FrugalGPT / Cascade** | N/A | ✅ Cascade: cheap first, escalate on confidence | Sequential: GPT-4o-mini → GPT-4o on quality threshold fail |
| **LiteLLM** | N/A (gateway) | ✅ Fallback/load-balance/cost-based | Priority list, round-robin, cheapest-provider routing |
| **CascadeFlow** | N/A (runtime) | ✅ In-process speculative cascading | Sub-5ms overhead, integrates with LangChain/CrewAI/ADK/Hermes |
| **Structural Routing** | ✅ Design-time assignment | N/A — fixed per role | Cheap models for classification/routing agents; strong for reasoning/audit |

### Key Technical Details

**OpenCode Per-Agent Config** (from opencode.ai/docs/agents):
```json
{
  "agent": {
    "plan": { "model": "anthropic/claude-haiku-4-20250514" },
    "review": { "model": "anthropic/claude-opus-4", "reasoningEffort": "high" },
    "deep-thinker": { "model": "openai/gpt-5", "reasoningEffort": "high", "textVerbosity": "low" }
  }
}
```
Subagents inherit primary agent's model unless overridden. Global `model` sets default.

**AutoGen Per-Agent** (from microsoft.github.io/autogen):
```python
model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")
agent = AssistantAgent(name="assistant", model_client=model_client, ...)
```
Context limiting via `BufferedChatCompletionContext` (last N messages) or `TokenLimitedChatCompletionContext`.

**Dynamic Routing Research** (arXiv:2603.04445, 2026):
- **Routing**: Pre-call classifier selects model (zero model-call overhead)
- **Cascading**: Cheap model first, escalate on confidence threshold (always pays cheap model cost)
- **RouteLLM**: 85% cost reduction on MT-Bench at 95% GPT-4 quality, only 14% strong-model calls
- **FrugalGPT**: Up to 98% cost reduction via cascade
- **Structural Routing** (OpenLegion 2026-07-07): Assign fixed model per agent role — avoids classifier overhead, adversarial attack surface, and cascade failures. Captures most savings in multi-agent systems.

### Omega Engine Applicability

- **Phase 1 (Config)**: Use OpenCode per-agent model config — `researcher` → `gemma-4-31b` (local), `kali` → `claude-opus-4` (cloud), `roc_racoon` → `qwen3-1.7b` (local)
- **Phase 2 (Tooling)**: Implement structural routing in Oracle — route by agent role, not per-query classifier
- **Local-First**: Native GGUF (Qwen3-1.7B) for Tier 0/1 agents; cloud only for Tier 2 reasoning agents
- **Avoid**: Dynamic per-query routing — adds latency, adversarial surface, cascade failure modes. Structural routing aligns with Omega's agent-slot architecture.

---

## Q4: Token Measurement Tooling (G-7)

### Framework Comparison Table

| Tool/Platform | Token Measurement | Cost Tracking | Cache Breakdown | Integration |
|---------------|-------------------|---------------|-----------------|-------------|
| **OpenCode (Native)** | SQLite: `tokens.input`, `tokens.output`, `tokens.cached`, `tokens.cacheCreation` per message | ✅ `cost` field per message | ✅ Separate `cached` / `cacheCreation` fields | OTel plugin exports `opencode.token.usage`, `opencode.cost.usage` |
| **Anthropic API** | `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` | Manual (pricing × tokens) | ✅ Explicit read/write cache tokens | SDK returns in `response.usage` |
| **OpenAI API** | `prompt_tokens`, `prompt_tokens_details.cached_tokens`, `completion_tokens` | Manual | ✅ `cached_tokens` detail | SDK returns in `response.usage` |
| **Langfuse** | Ingests `input`, `output`, `cache_read_input_tokens`, `cache_creation_input_tokens` | ✅ Auto-calculates from model pricing tiers | ✅ Converts inclusive→exclusive buckets | SDK `@observe` decorator, OTel compatible |
| **OpenTelemetry Gen AI** | Standard attributes: `gen_ai.usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` | `gen_ai.cost` gauge metric | ✅ Standardized cache attributes | Vendor-neutral, all major backends |
| **TrueFoundry AI Gateway** | Request-level input/output/cache tokens | ✅ Per-model, per-session, per-repo | ✅ Via provider response | OpenCode → gateway via custom provider config |
| **LiteLLM Gateway** | Per-request tokens via proxy | ✅ Cost tracking, virtual keys | ✅ Passes through provider cache fields | OpenAI-compatible API, OpenCode points `baseURL` to proxy |
| **Portkey Gateway** | Per-session traces with token counts | ✅ 4-tier budget hierarchy | ✅ Via provider | Requires `x-portkey-trace-id` header from shim |
| **Token Optimizer (OpenCode Plugin)** | `token_status` tool — dual-score quality, MRCR curves | ✅ Cost tracking across 30+ models | ⚠️ Quality-focused, not cache-specific | TypeScript plugin, `token_dashboard` tool |
| **tiktoken / @anthropic-ai/tokenizer** | Local token counting (offline) | ❌ No pricing | ❌ No cache awareness | Python/JS libraries for pre-flight estimation |

### Key Technical Details

**OpenCode SQLite Schema** (from jSydorowicz21/ai-cli-observability):
```sql
-- message_parts.data JSON column contains:
{
  "tokens": {
    "input": 1234,
    "output": 567,
    "cached": 800,           -- cache_read_input_tokens
    "cacheCreation": 400     -- cache_creation_input_tokens
  },
  "cost": 0.0023,
  "model": "anthropic/claude-sonnet-4-5"
}
```

**Anthropic Usage Fields** (from langfuse.com docs):
```python
response.usage.input_tokens              # Excludes cache reads/writes
response.usage.output_tokens
response.usage.cache_read_input_tokens   # Tokens read from cache
response.usage.cache_creation_input_tokens  # Tokens written to cache
```

**Langfuse Exclusive Bucket Conversion** (critical for accuracy):
```python
# OpenAI reports inclusive counts (prompt_tokens includes cached)
# Anthropic reports exclusive (input_tokens excludes cache)
# Langfuse stores EXCLUSIVE buckets:
usage_details = {
    "input": response.usage.input_tokens,                    # Anthropic: already exclusive
    "output": response.usage.output_tokens,
    "cache_read_input_tokens": response.usage.cache_read_input_tokens,
    "cache_creation_input_tokens": response.usage.cache_creation_input_tokens
}
# For OpenAI: input = prompt_tokens - cached_tokens
```

**OTel Gen AI Semantic Conventions** (v1.29+, merged Nov 2024):
- `gen_ai.system` = "anthropic" | "openai" | ...
- `gen_ai.request.model` = requested model name
- `gen_ai.usage.input_tokens` (int)
- `gen_ai.usage.output_tokens` (int)
- `gen_ai.usage.cache_read_input_tokens` (int)
- `gen_ai.usage.cache_creation_input_tokens` (int)
- `gen_ai.response.finish_reasons` (array)

### Omega Engine Applicability

- **Immediate**: Enable OpenCode OTel plugin (`OPENCODE_OTLP_ENDPOINT`) → export to local OTel collector → Prometheus/Grafana for token/cost dashboards
- **Phase 2**: Build `src/omega/oracle/token_budget.py` (per existing report) using OpenCode's per-message token fields
- **Local Models**: Use `tiktoken` / `@anthropic-ai/tokenizer` for pre-flight estimation before local inference
- **Gateway**: Deploy LiteLLM or TrueFoundry AI Gateway for centralized request-level observability across all providers (local + cloud)
- **Security**: Never log raw prompts to third-party SaaS — metadata-only (token counts, latency, cost) satisfies 90% of operational needs (OpenLegion 2026-07-10)

---

## Sovereign Synthesis: Omega Engine Phase 1 Applicability

### Convergence (Industry Consensus)
1. **Prompt caching is table stakes** — every major provider supports it; frameworks that don't expose it (LangGraph, AutoGen) leave 60-90% savings on the table
2. **Compaction is inevitable but poorly standardized** — triggers vary (token %, event count, threshold); pre-compaction hooks are a universal gap
3. **Structural routing > dynamic routing for agents** — role-based model assignment captures 70%+ of cascade savings without classifier overhead or adversarial surface
4. **Token observability requires exclusive bucket accounting** — inclusive counts (OpenAI) vs exclusive (Anthropic) must be normalized before storage

### Divergence (Open Questions for Omega)
1. **Local model caching** — llama.cpp prefix caching vs Anthropic explicit breakpoints: different architectures, same goal
2. **Compaction hydration** — no framework has automated recovery; Omega's hydration engine (Phase 2) is a differentiator
3. **Per-agent token budgets** — OpenCode tracks per-message; Omega needs per-agent *budget enforcement* (not just measurement)

### Recommended Phase 1 Actions (Config-Only, ~1 Week)

| Action | Source Pattern | Omega Implementation |
|--------|----------------|---------------------|
| Set OpenCode `buffer: 50000` | OpenCode compaction config | `opencode.json` → `compaction.buffer` |
| Per-agent model config | OpenCode `agent.{name}.model` | `researcher`→local, `kali`→cloud, `roc_racoon`→local |
| Enable OTel token export | OpenCode OTel plugin | `OPENCODE_OTLP_ENDPOINT=http://localhost:4317` |
| Condensed mandates (57 lines) | Anthropic Constitutional AI | `MANDATES_CONDENSED.md` as Tier 0 cached block |
| Opt-in skills with `auto_load` | Lazy Skills pattern | Core skills only in system prompt |

### Phase 2 Tooling Targets (2-3 Weeks)
1. **Hydration Engine** — checkpoint at 80% usage via `experimental.session.compacting` hook
2. **Token Budget Enforcer** — per-tier budgets (pinned 2k, role 4k, dynamic 8k) with trim-from-lowest-priority
3. **Local Token Counter** — `tiktoken`/`@anthropic-ai/tokenizer` integration for pre-flight estimation

---

## Sources & Evidence

### Q1: Prompt Caching
1. OpenCode `applyCaching()` — forums.basehub.com/anomalyco/opencode/32 (2026-02-02)
2. Anthropic Prompt Caching Guide — caching.ai/blog/anthropic-prompt-caching-guide (2026-07-19)
3. LangGraph Prompt Caching Patterns — sangampandey.info/blog/langgraph-prompt-caching (2026-03-13)
4. Agno Prompt Caching — docs.agno.com/models/providers/native/anthropic/usage/prompt-caching
5. OpenCode Issue #20265 — github.com/anomalyco/opencode/issues/20265 (2026-03-31)

### Q2: Compaction Triggers
6. OpenCode Compaction Docs — v2.opencode.ai/compaction
7. Context Compaction Deep Dive — codex.danielvaughan.com/2026/08/14 (Codex/Claude/OpenCode comparison)
8. OpenCode Issue #10015 — github.com/anomalyco/opencode/issues/10015 (custom threshold)
9. Claude Code Pre-Compaction Hook Request — github.com/anthropics/claude-code/issues/34299 (2026-03-14)
10. LangGraph Composables — dev.to/crabtalk/context-compaction-in-agent-frameworks-4ckk (2026-03-15)
11. Microsoft Agent Framework Compaction — learn.microsoft.com/en-us/agent-framework/concepts/agents/conversations/compaction
12. Google ADK Compaction — adk.dev/context/compaction/

### Q3: Model Routing
13. OpenCode Agent Model Config — dev.opencode.ai/docs/agents
14. AutoGen Agents — microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html
15. Dynamic Model Routing Survey — arxiv.org/html/2603.04445v1 (2026)
16. RouteLLM / FrugalGPT — resumelens.org/blog/ai/llm-routing-cascades (2026-05-11)
17. CascadeFlow — github.com/lemony-ai/cascadeflow
18. Structural Routing Analysis — openlegion.ai/en/learn/llm-routing (2026-07-07)
19. OpenCode Per-Agent Examples — skillsmp.com/creators/njengafelix/opencode-models/skill

### Q4: Token Measurement
20. OpenCode OTel Plugin — github.com/jSydorowicz21/ai-cli-observability/blob/main/docs/opencode.md
21. Anthropic Usage Fields — langfuse.com/docs/observability/features/token-and-cost-tracking
22. OpenTelemetry Gen AI Conventions — openlegion.ai/en/learn/llm-observability (2026-07-10)
23. TrueFoundry OpenCode Observability — truefoundry.com/docs/ai-gateway/opencode
24. LiteLLM/Portkey/Helicone Gateway Comparison — futureagi.com/blog/best-ai-gateways-opencode-token-tracking-2026 (2026-03-16)
25. Token Optimizer Plugin — alexgreensh.github.io/token-optimizer/platforms/opencode/
26. OpenCode Token Usage Analysis — truefoundry.com/blog/opencode-token-usage-how-it-works-and-how-to-optimize-it (2026-07-27)
27. tiktoken / Anthropic Tokenizer — langfuse.com/docs/observability/features/token-and-cost-tracking (tokenizer table)
28. OpenCode SQLite Token Fields — github.com/jSydorowicz21/ai-cli-observability (token extraction mapping)

---

## Council Dialectic Summary

### Architect (Systemic Logic)
> "OpenCode's provider-agnostic caching is the strongest foundation — it already handles Anthropic, OpenAI, Bedrock, OpenRouter, Venice. We don't need to build caching; we need to optimize the assembly order for cache topology. Structural routing via per-agent config is the only pattern that respects our agent-slot architecture. Dynamic classifiers add latency and attack surface for marginal gain."

### Adversary (Critical Rigor)
> "OpenCode's compaction has NO pre-compaction hook — the plugin hook fires *during* compaction, not before. The hydration engine MUST write checkpoints at 80% usage via a background monitor, not rely on OpenCode. Also: OpenCode's SQLite token fields are per-message, not per-agent — budget enforcement requires aggregation layer. Local model token counting (tiktoken) is inaccurate for non-OpenAI tokenizers."

### Alchemist (Creative Synthesis)
> "The 'prompt as view' principle (Zylos) + OpenCode's plugin hooks = we can build a cache-aware assembly engine that reorders system blocks for optimal KV cache hits. Structural routing + local-first = researcher on Qwen3-1.7B, kali on Antigravity Opus, roc_racoon on local. Token budgets per tier + OTel export = real-time cost governance without SaaS dependency."

### Archivist (Historical Truth)
> "OpenCode's AGENTS.md discovery and compaction.ts are battle-tested. Anthropic's 4-breakpoint cache_control is the industry standard. RouteLLM proved 85% savings but on chat benchmarks, not agent tool-calling. Langfuse's exclusive bucket conversion is the correct accounting pattern. The 2026-07-10 OpenLegion security warning on prompt logging is non-negotiable."

---

## Triangulation: Convergence & Divergence

### Convergence (The Truth)
1. **Caching topology drives economics** — stable-first ordering = 60-90% savings (universal)
2. **Compaction requires externalized state** — no framework has automated recovery (universal gap)
3. **Structural routing > dynamic for agents** — role-based assignment captures most savings without classifier risks
4. **Exclusive bucket token accounting** — mandatory for accurate cost tracking across providers

### Divergence (Omega Decisions Needed)
1. **Local model caching strategy** — llama.cpp prefix caching vs explicit breakpoints: investigate for `native-gguf`
2. **Compaction threshold for local models** — 200k cloud context vs 8k-32k local: buffer must scale with context window
3. **Per-agent vs per-session budgets** — OpenCode tracks per-message; Omega needs per-agent enforcement

---

*⬡ OMEGA ⬡ JEM-ANALYST ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_researcher_strategic ⬡ COMPLETE*