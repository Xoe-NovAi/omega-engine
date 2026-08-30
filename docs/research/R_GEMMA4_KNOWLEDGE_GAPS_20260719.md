# 🔱 Gemma 4 Strategy — Knowledge Gap Analysis for Web Research

**AP Token**: `AP-GEMMA4-KNOWLEDGE-GAPS-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-19

**Source**: Meditation hardening pass 4 (Kali Synthesis) + Phase 2 Collisions + Phase 3 Emergent Sequencing
**Purpose**: Identify every knowledge gap that requires web research to ground the hardened strategy before Week 1 implementation.

---

## Executive Summary

The meditation revealed **15 critical knowledge gaps** across 5 domains. Each gap blocks a specific implementation decision or introduces risk if assumed. This document structures them for systematic web research using Sovereign Search Protocol (Tiers 1-4).

| Domain | Gaps | Blocking |
|--------|------|----------|
| **OpenCode Architecture** | 3 | OpenCode PR target, config package version detection |
| **Google API & Providers** | 5 | Vertex vs AI Studio schemas, quota mechanics, thinking tokens |
| **Industry Patterns** | 3 | Capability schemas, Redis Lua quota, chaos testing |
| **Heritage & Compliance** | 2 | Pi project vet record, M14 pipeline execution |
| **Omega Internals** | 2 | Meditation pipeline real run, Hivemind handoff protocol |

---

## Domain 1: OpenCode Architecture (3 Gaps)

### Gap 1.1: OpenCode V2 Provider Architecture — Is `transform.ts` Deprecated?
**Blocking**: OpenCode upstream PR target (Step 8)
**Question**: Does OpenCode 1.18+ use the V2 hand-rolled LLM layer that removes AI SDK dependency? If so, `transform.ts` is legacy and PR must target new protocol axes.
**Research Needed**:
- OpenCode 1.18+ release notes / changelog
- `packages/opencode/src/provider/` directory structure in main branch
- MartianLee analysis (2026-06-29) — verify V2 status
- OpenCode GitHub issues discussing V2 migration
**Search Queries**:
- `opencode 1.18 provider architecture V2 transform.ts deprecated`
- `opencode hand-rolled LLM layer 4 axes provider protocol`
- `site:github.com anomalyco/opencode transform.ts 2026`
**Sources**: GitHub (anomalyco/opencode), OpenCode docs, MartianLee blog

### Gap 1.2: OpenCode Config Merge Semantics — Exact Behavior
**Blocking**: Community config package design (Step 8)
**Question**: Deep-merge for objects, last-write-wins for scalars — but what about arrays? Does `provider.google.models` array replace or merge by key?
**Research Needed**:
- OpenCode config source code (`packages/opencode/src/config/`)
- Config documentation examples showing merge behavior
- Community issues about model config override
**Search Queries**:
- `opencode config merge deep merge objects last-write-wins scalars`
- `opencode provider.google.models array merge behavior`
- `site:github.com anomalyco/opencode config merge`

### Gap 1.3: OpenCode Version Detection — Programmatic Approach
**Blocking**: Config package version-gating (Step 8)
**Question**: How to reliably detect OpenCode version from within a config package install script? CLI flag? Environment variable? Package.json?
**Research Needed**:
- `opencode --version` output format
- OpenCode runtime environment variables
- npm package version detection patterns
**Search Queries**:
- `opencode version detection cli environment variable`
- `opencode runtime version check script`

---

## Domain 2: Google API & Providers (5 Gaps)

### Gap 2.1: Vertex AI vs AI Studio — Exact Thinking Config Schemas
**Blocking**: GoogleCompatProvider adapter design (Step 2), Capability Matrix auth_type field
**Question**: What are the EXACT request/response schemas for thinking config on each platform?
**Research Needed**:
- Vertex AI Gemini 2.5 thinking config: `thinkingConfig.thinkingBudget` format, limits
- AI Studio Gemma 4 thinking config: `thinkingConfig.thinkingLevel` enum values
- API version differences: `v1` vs `v1beta` support per model
- Authentication differences: API key vs OAuth vs service account
**Search Queries**:
- `vertex ai gemini 2.5 thinkingConfig thinkingBudget schema`
- `google ai studio gemma 4 thinkingConfig thinkingLevel MINIMAL HIGH`
- `generativelanguage.googleapis.com v1 vs v1beta gemma 4`
- `google cloud vertex ai gemini thinking budget tokens`

### Gap 2.2: Google AI Studio Free Tier — Rolling Window Mechanics
**Blocking**: Pre-flight estimation, quota manager design (Steps 4, 5)
**Question**: Is 16k TPM a hard rolling minute window? Per-project? Per-key? Per-model? How does `retry-after` header work?
**Research Needed**:
- Official Google AI Studio quota documentation (2026)
- Rate limit headers: `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, `retry-after`
- Quota reset timing: minute boundary? sliding window?
- Per-model vs per-project limits for Gemma 4
**Search Queries**:
- `google ai studio free tier 16k tpm rolling window 2026`
- `generativelanguage.googleapis.com rate limit headers x-ratelimit`
- `google ai studio quota reset timing minute sliding window`
- `gemma 4 rate limits 15 rpm 1500 rpd`

### Gap 2.3: Thinking Token Billing — Exact Mechanics
**Blocking**: Budget gate multiplier, TokenLedger design (Steps 4, 5)
**Question**: Thinking tokens count as output tokens. What percentage? Is `thoughtsTokenCount` always returned? How to estimate before request?
**Research Needed**:
- Google AI pricing page: thinking token billing details
- Cookbook #1198: `thoughtsTokenCount` field behavior
- Response structure: where `thoughtsTokenCount` appears
- Estimation: can we predict thinking token count from prompt?
**Search Queries**:
- `google ai studio thinking tokens billing output tokens 2026`
- `gemma 4 thoughtsTokenCount response field`
- `google generative ai thinking token count estimation`

### Gap 2.4: OpenRouter — Upstream Provider Pinning & Routing
**Blocking**: CapabilitySelector OpenRouter routing, `:free` suffix handling (Steps 4, 5)
**Question**: How to pin upstream provider? What are latency/cost differences? Does auto-routing change model behavior?
**Research Needed**:
- OpenRouter provider parameter: `provider: "google-ai-studio"` syntax
- Upstream providers for `google/gemma-4-31b-it:free` (Google AI Studio, OpenInference, others)
- Latency benchmarks: Google AI Studio vs OpenInference via OpenRouter
- Routing modes: `auto` vs `specific` provider
**Search Queries**:
- `openrouter provider parameter google-ai-studio pin upstream`
- `openrouter google gemma 4 31b free upstream providers latency`
- `openrouter routing mode auto vs specific provider behavior`

### Gap 2.5: Gemma 4 12B Unified — Capabilities & MTP Drafters
**Blocking**: Capability Matrix entry for new model (Step 2)
**Question**: Released June 3, 2026. What are thinking levels? MTP drafter specs? Context window?
**Research Needed**:
- Google Gemma releases page (June 2026)
- 12B Unified model card: thinking config, MTP drafter details
- Performance vs 31B/26B
**Search Queries**:
- `gemma 4 12b unified release june 2026 thinking config`
- `gemma 4 mtp multi-token prediction drafter 12b`
- `google gemma releases 2026 12b unified`

---

## Domain 3: Industry Patterns (3 Gaps)

### Gap 3.1: Provider Capability Declaration Schemas — Production References
**Blocking**: Capability Matrix schema design (Step 2)
**Question**: What exact fields do LiteLLM, Vercel AI SDK, LangChain use for capability declaration?
**Research Needed**:
- LiteLLM model registry: `supports_reasoning`, `thinking_config_schema`, `max_tokens`
- Vercel AI SDK `LanguageModelV3` interface + `providerOptions`
- LangChain `BaseChatModel` + `model_kwargs` patterns
- Models.dev API response schema
**Search Queries**:
- `litellm model registry supports_reasoning thinking_config_schema`
- `vercel ai sdk LanguageModelV3 providerOptions thinking`
- `langchain BaseChatModel model_kwargs provider specific`
- `models.dev api schema capabilities reasoning`

### Gap 3.2: Redis Lua Atomic Quota Check-and-Consume — Production Patterns
**Blocking**: Concurrent quota race handling (Step 4)
**Question**: Exact Lua script for atomic token bucket check-and-consume with TTL?
**Research Needed**:
- Redis token bucket Lua script patterns
- Sliding window vs fixed window implementations
- Per-key TTL management
- Error handling: script timeout, Redis unavailable
**Search Queries**:
- `redis lua token bucket atomic check and consume sliding window`
- `redis quota management lua script ttl per key`
- `redis rate limiting lua script production patterns`

### Gap 3.3: Chaos Testing for LLM Provider Failover — Specific Test Implementations
**Blocking**: Chaos test `test_quota_exhaustion_mid_thinking_stream` (Step 6)
**Question**: How to mock streaming response with mid-stream 429? Idempotency key patterns? Partial response stitching?
**Research Needed**:
- Testing streaming LLM responses with errors
- Idempotency keys for LLM requests (OpenAI, Anthropic, Google)
- Partial response handling: stitching fallback response
- Existing chaos test frameworks: Chaos Mesh, Litmus, custom
**Search Queries**:
- `chaos testing llm provider failover streaming 429 mid-stream`
- `idempotency key llm request openai anthropic google`
- `partial streaming response stitching fallback llm`
- `chaos engineering llm applications 2026`

---

## Domain 4: Heritage & Compliance (2 Gaps)

### Gap 4.1: Pi Project PR #2903 — Exact Implementation Details
**Blocking**: Heritage vetting (Step 1), OpenCode PR reference
**Question**: What exact regex? What thinking level mapping? Full diff?
**Research Needed**:
- Pi PR #2903 full diff (files changed)
- `isGemma4Model` regex pattern
- Thinking level mapping: `minimal`/`low` → `MINIMAL`, `medium`/`high` → `HIGH`
- Any other Gemma 4 fixes in same PR
**Search Queries**:
- `github.com/earendil-works/pi/pull/2903`
- `pi gemma 4 thinking level mapping regex`
- `earendil-works pi gemma 4 transform.ts fix`

### Gap 4.2: M14 Heritage Vetting Pipeline — Vet Record Format
**Blocking**: Pi project vet record creation (Step 1)
**Question**: Exact `HERITAGE_VET_LOG.md` entry format? Scope declaration template? Score criteria?
**Research Needed**:
- `docs/strategy/HERITAGE_VETTING_PIPELINE.md` (local)
- `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (local examples)
- Vet record required fields: file:line, technique, hardware constraint, scope
- Minimum score 7/10 criteria
**Search Queries**: (Local files first, then web if needed)
- `heritage vetting pipeline scope declaration template`
- `id-soft tag vet record format file line hardware constraint`

---

## Domain 5: Omega Internals (2 Gaps)

### Gap 5.1: Meditation Pipeline — Real Execution via MCP Hub
**Blocking**: Real meditation run (Step 7)
**Question**: How to invoke `/meditate` command programmatically via Omega Hub MCP? Session management? Lens set parameter passing?
**Research Needed**:
- Omega Hub MCP tools for meditation
- `omega-hub_oracle_summon` with entity `kali` and meditation prompt
- Session namespace isolation (D-290) integration
- MIAP (D-291) session directory structure
**Search Queries**: (Local code first)
- `omega-engine oracle meditate mcp`
- `omega hub meditation protocol mcp tools`

### Gap 5.2: Hivemind Handoff Protocol — Sequential Lock Handoff
**Blocking**: P6→P9 handoff for Capability Matrix → CapabilitySelector (Step 4)
**Question**: Exact workspace lock acquire/release sequence? Context posting format? Continuation field usage?
**Research Needed**:
- `docs/strategy/HIVEMIND_PROTOCOL.md` (local)
- `omega-hub_hivemind_workspace_lock_acquire` parameters
- `omega-hub_hivemind_post_context` continuation field
- Live feed append format
**Search Queries**: (Local docs first)
- `omega hivemind workspace lock handoff protocol`
- `hivemind post context continuation field format`

---

## Research Priority Matrix

| Priority | Gaps | Reason |
|----------|------|--------|
| **P0 — Blocks Step 1-2** | 1.1, 2.1, 2.2, 2.3, 4.1, 4.2 | Heritage vet + adapter design need these first |
| **P1 — Blocks Step 3-4** | 1.2, 1.3, 2.4, 2.5, 3.1 | Matrix schema + selector routing |
| **P2 — Blocks Step 5-6** | 3.2, 3.3 | Quota atomic ops + chaos test |
| **P3 — Blocks Step 7-8** | 5.1, 5.2 | Meditation run + handoff protocol |

---

## Research Execution Plan

### Session 1 (Today): P0 Gaps
- [ ] Gap 4.1: Pi PR #2903 full diff (GitHub)
- [ ] Gap 4.2: M14 vet record format (local docs)
- [ ] Gap 2.1: Vertex vs AI Studio schemas (Google docs)
- [ ] Gap 2.2: Free tier quota mechanics (Google docs + forums)
- [ ] Gap 2.3: Thinking token billing (Google pricing + cookbook)
- [ ] Gap 1.1: OpenCode V2 status (GitHub + MartianLee)

### Session 2 (Tomorrow): P1 Gaps
- [ ] Gap 3.1: Capability schemas (LiteLLM, Vercel, LangChain docs)
- [ ] Gap 2.4: OpenRouter pinning (OpenRouter docs)
- [ ] Gap 2.5: Gemma 4 12B (Google releases)
- [ ] Gap 1.2: Config merge (OpenCode source)
- [ ] Gap 1.3: Version detection (OpenCode CLI)

### Session 3 (Day 3): P2 Gaps
- [ ] Gap 3.2: Redis Lua quota (Redis patterns + blogs)
- [ ] Gap 3.3: Chaos testing (engineering blogs)

### Session 4 (Day 4): P3 Gaps
- [ ] Gap 5.1: Meditation MCP (local code)
- [ ] Gap 5.2: Hivemind handoff (local docs)

---

## Output Format

Each gap research produces a **Gap Research Card**:

```markdown
## Gap X.Y: [Title]
**Status**: RESEARCHED / PARTIAL / BLOCKED
**Sources**: [URLs with access dates]
**Findings**: [Key facts, exact values, schemas]
**Decision Impact**: [How this changes implementation]
**Remaining Questions**: [What still unknown]
```

All cards compiled into: `docs/research/R_GEMMA4_GAP_RESEARCH_20260719.md`

---

## Success Criteria

- [ ] All 15 gaps have at least 2 primary sources
- [ ] No implementation decision based on assumption
- [ ] Heritage vet record draft ready for doom_guy/verity
- [ ] Capability Matrix schema finalized with industry references
- [ ] Chaos test design grounded in production patterns
- [ ] Meditation pipeline execution path verified

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
