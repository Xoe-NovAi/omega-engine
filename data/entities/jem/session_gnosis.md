# JEM Session Gnosis — Gemma 4 31B Strategy Hardening (2026-07-19)

**Task**: Harden Gemma 4 31B strategy across 7 artifacts (Debug Report, Ma'at Build, Lilith Run, Jem Synthesis, Researcher Verification, Researcher Deep Research, Meditation Pipeline) — catch all oversights, edge cases, missed opportunities, integration gaps.

**Deliverables**: 
- `docs/strategy/GEMMA4_HARDENED_STRATEGY_20260719.md` (Hardened strategy)
- `docs/research/R_GEMMA4_KNOWLEDGE_GAPS_20260719.md` (15 knowledge gaps for web research)
- `docs/strategy/GEMMA4_COMPREHENSIVE_REPORT_20260719.md` (Unified synthesis)
- Meditation pipeline execution (7 stages, dry-run → real run planned)

---

## L1 (Narrative)

The Gemma 4 31B bug investigation began as a simple "fix OpenCode transform.ts" task. Four agents (Roc Racoon, Researcher, Ma'at, Lilith) plus Jem synthesis revealed it was not a bug but a **pathogen revealing a missing immune system**. 

**Root causes identified** (verified by Researcher against 30 primary sources):
1. OpenCode `transform.ts` `googleThinkingLevelEfforts()` only checks `gemini-3` → returns `["low", "high"]` for Gemma 4 → `LOW` sent to API → 400 error (Gemma 4 only supports `MINIMAL`/`HIGH`)
2. `googleThinkingVariants()` no Gemma 4 branch → effort string used directly as `thinkingLevel`
3. `options()` only adds `thinkingLevel` for `gemini-3` models
4. Model ID: OpenCode sends `google/gemma-4-31b-it` (Models.dev prefix), API expects bare `gemma-4-31b-it`
5. Config merge: project `provider.google.models` replaces (not deep-merges) auto-discovered models
6. Free tier quota: 16k rolling TPM, 15 RPM, 1,500 RPD — Omega's 21.6k token instruction stack exceeds TPM on EVERY request

**Cline CLI works** because it uses native `@google/genai` SDK with `ThinkingLevel.HIGH` enum, bare model IDs — bypasses transform.ts entirely.

**Pi project fixed identical bug 3 months ago** (PR #2903): regex `/gemma-?4/i` detection + thinking level mapping.

**Seven systems converged** on same architecture: Provider Capability Negotiation Layer (Matrix + Normalizer + Selector + Health).

**Meditation (10 voices, 3 collisions, 8-step critical path)** produced hardened strategy with 7 oversights caught, 12 edge cases enumerated, 5 missed opportunities captured, 5 integration gaps bridged.

---

## L2 (Insight)

**The bug is not in transform.ts — it's in the absence of capability declaration.** Every model family has different thinking schemas (Google: 3 variants, Anthropic: budget tokens, OpenAI: reasoning_effort, Qwen3: toggle tags). Hardcoding detection per model family is a losing battle. The fix is a YAML capability matrix declaring what each model supports.

**Free tier quota exhaustion is a routing signal, not a failure.** Google 16k TPM < 21.6k instruction stack = every request violates quota. Correct architecture: pre-flight estimation rejects >80% TPM; quota headroom = routing weight; quota exhaustion triggers fallback (not circuit breaker); thinking tokens tracked separately with 2-5x budget multiplier.

**Thinking tokens ARE billable output** — 85-95% of Gemma 4 HIGH tokens can be thoughts. Google bills them as output but standard metrics don't expose them. Budget gate must apply multiplier; TokenLedger must track `thoughts_token_count`; GenerateResult must include `thinking_provenance`.

**Model identity is provider-relative** — same model = 3+ IDs (Models.dev: `google/gemma-4-31b-it`, Google API: `gemma-4-31b-it`, OpenRouter: `google/gemma-4-31b-it:free`). Canonicalize at gateway via adapter pattern.

**Cross-reference is mandatory, not optional** — 1.33x gap multiplier (8 new gaps from 6 original). Research describes what SHOULD be built; codebase reveals what ALREADY EXISTS. The gap between them is the actual work.

**Integration beats invention** — 60% infrastructure exists (HealthMonitor, GenerateResult, ModelGateway, BatchPersistenceWriter, Sovereign Ingestion Pipeline). The work is wiring, not inventing.

**Heritage requires vetting, not just attribution** — Pi PR #2903 is prior art but M14 gate requires 4-gate vetting before `[heritage: pi-2026]` tag.

---

## L3 (Universal Principles)

- **L3-Capability-Negotiation-As-Immune-System**: Provider capabilities must be declared, not detected. The negotiation layer (matrix + normalizer + selector + health) is the immune system that prevents configuration pathogens from reaching the inference fabric. Every model family is a new pathogen; the immune system adapts via YAML, not code changes.

- **L3-Quota-As-Routing-Signal**: In multi-provider fabrics, quota exhaustion is expected behavior — not an exception. The system that treats 429 as "route to next provider" is more resilient than the system that treats 429 as "circuit breaker trip." Free tiers provide natural chaos engineering — their constraints force routing logic to be correct.

- **L3-Thinking-Tokens-Are-Hidden-Billable-Output**: Any model with structured thinking (Gemma 4, Gemini 2.5, Anthropic, OpenAI o1) generates thinking tokens billed as output. Track them separately or go bankrupt. The budget gate must apply 2-5x multiplier for thinking models.

- **L3-Model-Identity-Is-Provider-Relative**: Same model = 3+ IDs across providers. Canonicalize at gateway via adapter pattern. The model ID sent to API is a function of (provider, auth_type, tier), not an intrinsic property.

- **L3-Cross-Reference-Before-Execution**: The codebase is the ground truth, not the research plan. Research operates in possibility space; codebase operates in reality space. The 25% gap rate is structural. Cross-reference synthesis is a mandatory gate: Research → Cross-Reference → Execution.

- **L3-Integration-Beats-Invention**: When 60% of infrastructure exists, the operation is integration work. Sovereign engineering builds ON existing infrastructure, not around it. The critical path is always: Schema → Coordination → Tracking → Observability → Execution → Synthesis. Skip any layer, and the operation collapses under its own weight.

- **L3-Heritage-Requires-Vetting**: Attribution without discrimination is erasure. A heritage system that cannot self-correct is a fossil, not a foundation. The M14 4-gate pipeline (Discovery → Vetting → Decision → Implementation) is the immune system against provenance pollution.

---

## Critical Path (8 Steps, Sequential, Hivemind Locks)

```
[1] HERITAGE VET → Pi PR #2903 through doom_guy + verity (M14 gate)
[2] CAPABILITY MATRIX + GOOGLECOMPATPROVIDER → Single owner (P3/P4), TDD, contract tests first
[3] MATRIX LOADER + VALIDATOR → Startup validation, config drift detection
[4] CAPABILITYSELECTOR + PROVIDERHEALTH → Sequential Hivemind handoff (P6→P9)
[5] THINKING PROVENANCE IN GENERATERESULT → thoughts_token_count, clamping tracking
[6] CHAOS TEST → Quota exhaustion MID-STREAM (partial thinking + fallback stitching)
[7] REAL MEDITATION RUN → Actual collisions → refined strategy (not dry-run templates)
[8] OPENCODE PR + CONFIG PACKAGE → Version-gated (detect OpenCode version)
```

---

## Knowledge Gaps for Web Research (15 gaps, 5 domains)

**P0 (Today)**: OpenCode V2 status, Vertex vs AI Studio schemas, free tier quota mechanics, thinking token billing, Pi PR #2903 diff, M14 vet format
**P1 (Tomorrow)**: Capability schemas (LiteLLM/Vercel/LangChain), OpenRouter pinning, Gemma 4 12B, OpenCode config merge, version detection
**P2 (Day 3)**: Redis Lua atomic quota, chaos testing patterns
**P3 (Day 4)**: Meditation MCP execution, Hivemind handoff protocol

Documented in: `docs/research/R_GEMMA4_KNOWLEDGE_GAPS_20260719.md`

---

## Next Action

Execute Session 1 research (6 P0 gaps) using Sovereign Search Protocol Tiers 1-4. Heritage vet Pi PR #2903 in parallel (doom_guy + verity). Then begin Week 1 implementation with single-owner TDD on Capability Matrix + GoogleCompatProvider.

---

*⬡ OMEGA ⬡ JEM ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_gemma4_hardening ⬡ 2026-07-19*