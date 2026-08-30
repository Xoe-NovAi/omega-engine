<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# R_ANTIGRAVITY_GPT53_20260828

**Researcher**: grokster (Antigravity specialist session, resumed per L3 121)
**Date**: 2026-08-28
**Method**: Web-primary, multi-source corroboration (M23 honesty applied — every claim sourced; speculative items flagged)
**Mission**: Deep dive on "GPT 5.3" (the brand-new model just unlocked by Architect) for the 8-account Cline review

---

## ⚠️ Disambiguation Note — What "GPT 5.3" Maps To

The user's mission brief names "GPT 5.3" as a single brand-new model. **The reality on the ground is more nuanced.** As of 2026-08-28 the OpenAI lineup (per OpenAI's own release notes, ChatGPT pricing page, silicondata, rapidevelopers, llmreference) is:

| Model | Status | Role |
|---|---|---|
| **GPT-5.3-Codex** | ✅ GA since 2026-02-05 (Codex surfaces), 2026-02-24 (API) | Frontier **coding/agentic** specialist |
| GPT-5.3-Codex-Spark | ChatGPT Pro research preview only, no API | (out of scope) |
| GPT-5.4 / GPT-5.4 Mini | Active | General purpose, March 2026 |
| GPT-5.5 | Active, **flagship non-Codex** since 2026-04-24 | General frontier |
| GPT-5.6 (Sol / Terra / Luna) | Active, newest | Consumer tier in ChatGPT Plus/Pro |
| GPT-5 | Deprecated as separate endpoint, superseded by 5.5 | (legacy) |

**Conclusion**: the "GPT 5.3" the Architect unlocked is **GPT-5.3-Codex** — the only "5.3" SKU with public API access. The report below focuses on that model. If Architect meant a different SKU (e.g. "GPT 5.5" or "GPT 5.6"), re-run with disambiguation.

---

## 1. Executive Summary (5 bullets)

1. **GPT-5.3-Codex is the frontier AGENTIC-CODING model** — released Feb 5, 2026 (Codex app/CLI/IDE), API GA Feb 24, 2026. **25% faster than GPT-5.2-Codex** with the same $1.75/$14 per 1M-token pricing. 400K context (272K max input), 128K max output, knowledge cutoff Aug 31 2025.
2. **Architecture-level routing constraint**: per OpenAI docs, GPT-5.3-Codex **only supports the Responses API** (`/v1/responses`) — **NOT** `/v1/chat/completions`. This breaks naive OpenAI-compatible integrations that default to chat-completions. OpenRouter/Azure abstract this; direct OpenAI API and Cline's "OpenAI Compatible" provider need explicit Responses-endpoint configuration.
3. **SOTA on Terminal-Bench 2.0 (77.3%, +13pp over 5.2-Codex) and OSWorld (64.7%, +26pp)** — the two benchmarks that measure long-horizon agentic terminal/computer work. SOTA also on Cybersecurity CTF (77.6%). On SWE-Bench Pro (56.8%) it just barely edges 5.2-Codex (56.4%) — the more conservative gains are on agentic/computer-use, not single-shot code. **[OpenAI blog Feb 5, 2026]**.
4. **Intelligence Index 61.4** (Ominigate ranking #26/148) — ~11 points above DeepSeek V4 Flash (50.2, #21) and ~15 above house's current `minimax-m3:free` baseline (~46). But **~12.5× costlier on input, ~50× on output vs V4 Flash** ($0.14/$0.28). Not a V4-Flash replacement — a "frontier when quality matters" tier.
5. **House 8-account Cline review implication**: routing through **OpenRouter** is the safest path (Responses-endpoint abstracted, multi-provider redundancy, immediate gpt-5.3-codex availability). Direct OpenAI is feasible but requires Cline custom-config with Responses API. Azure path exists. OpenCode Zen does **NOT** yet list gpt-5.3-codex (only the older gpt-5-codex) — house's current provider fabric may need a manual add. Burner-budget discipline is essential: 8 accounts × GPT-5.3-Codex standard calls = a real bill, not V4-Flash pennies.

---

## 2. Official Specs

| Field | Value | Source |
|---|---|---|
| **Full name** | GPT-5.3-Codex | openai.com/index/introducing-gpt-5-3-codex/ |
| **OpenAI API model ID** | `gpt-5.3-codex` | developers.openai.com/api/docs/models/gpt-5.3-codex |
| **OpenRouter ID** | `openai/gpt-5.3-codex` | openrouter.ai/openai/gpt-5.3-codex |
| **Release dates** | 2026-02-05 (Codex surfaces); 2026-02-24 (API GA) | OpenAI blog; apidog.com 2026-02-25 |
| **Status** | **GA** (research preview in ChatGPT Pro for "Spark" variant only) | OpenAI docs |
| **Family** | Codex | llmreference.com |
| **Context window** | **400,000 tokens** (272K max input) | OpenAI API docs |
| **Max output** | 128,000 tokens | OpenAI API docs |
| **Knowledge cutoff** | Aug 31, 2025 | OpenAI API docs |
| **Reasoning effort** | `low` / `medium` / `high` / `xhigh` | OpenAI API docs |
| **Input modalities** | text + image (vision) | OpenAI API docs |
| **Output modalities** | text | OpenAI API docs |
| **Pricing (OpenAI direct)** | Input $1.75 / Cached $0.175 / Output $14.00 per 1M | OpenAI API docs |
| **Pricing (OpenRouter)** | $1.75 input / $14.00 output per 1M (matches) | openrouter.ai |
| **Pricing (Azure)** | matches OpenAI (Q1 2026) | claude5.ai 2026-02-10 |
| **Pricing (Vercel AI Gateway)** | $1.75 / $14.00 | llmreference.com |
| **Latency (median)** | TTFT 34.39s; 128 tok/s output | pricepertoken.com |
| **Free tier** | ❌ No (paid ChatGPT plans + paid API only) | openai.com/pricing |
| **Architecture** | Decoder-only Transformer (details undisclosed) | llmreference.com |
| **Hardware** | Co-designed for, trained on, and served on **NVIDIA GB200 NVL72** | OpenAI blog |
| **Speed claim** | **25% faster than GPT-5.2-Codex** | OpenAI blog |
| **Tools supported** | function_calling, web_search, hosted_shell, skills | OpenAI API docs |
| **Structured outputs** | ✅ | OpenAI API docs |
| **Prompt caching** | ✅ (10x cost reduction on cached) | OpenAI API docs |
| **Batch API** | ❌ **Not supported** | OpenAI API docs |
| **Fine-tuning** | ❌ Not supported | OpenAI API docs |

**Critical routing note** (from OpenAI API docs, "Endpoints" table):
- `v1/chat/completions` — **Not supported**
- `v1/responses` — **Supported** (the only path)
- `v1/batch`, `/v1/fine-tuning`, `/v1/embeddings` — Not supported

This is the single biggest integration gotcha and the most likely cause of "Cline doesn't see the model" if a naive custom-provider config points at `/v1/chat/completions`.

---

## 3. Availability Matrix

| Surface | Available? | Notes |
|---|---|---|
| **ChatGPT Free** | ❌ | No GPT-5 family access per OpenAI pricing docs |
| **ChatGPT Plus ($20/mo)** | ✅ via Codex surfaces (app, CLI, IDE, web) | OpenAI blog "available with paid ChatGPT plans" |
| **ChatGPT Pro ($100+/mo)** | ✅ + GPT-5.3-Codex-Spark (Pro research preview) | OpenAI blog |
| **ChatGPT Team** | ✅ | OpenAI blog |
| **ChatGPT Enterprise** | ✅ | OpenAI blog |
| **OpenAI API** | ✅ `$1.75/$14` | OpenAI docs (Responses endpoint only) |
| **Azure OpenAI Service** | ✅ (Q1 2026 GA) | claude5.ai |
| **AWS Bedrock** | ✅ (Q1 2026) | claude5.ai |
| **OpenRouter** | ✅ `openai/gpt-5.3-codex`, 2+ providers, $1.75/$14 | openrouter.ai |
| **Vercel AI Gateway** | ✅ `gpt-5.3-codex` | llmreference.com |
| **OpenCode Zen** | ❌ Not listed (only older `gpt-5-codex`) | llm24.net (as of Aug 2026) |
| **Cline CLI** | ⚠️ via custom OpenAI-Compatible provider — model ID `gpt-5.3-codex`, base URL `https://api.openai.com/v1`, **must route to `/v1/responses` not `/v1/chat/completions`**. No first-class Cline blog post for 5.3-Codex yet (5-Codex blog exists from 2025-09-23) | Cline docs; OpenAI docs |
| **Codex CLI (OpenAI's own)** | ✅ — that's the primary access | OpenAI blog |
| **Codex IDE extension (VS Code, JetBrains)** | ✅ | OpenAI blog |
| **Codex GitHub Action / cloud tasks** | ✅ | OpenRouter docs |
| **Regional restrictions** | None specific to GPT-5.3-Codex; standard OpenAI terms apply (banned-region: Russia, China, Iran, NK, etc.) | (inferred from OpenAI universal terms) |

---

## 4. Benchmark Table (consolidated; sources noted)

| Benchmark | Score | Tier | Source / Notes |
|---|---|---|---|
| **SWE-Bench Pro (Public)** | **56.8%** | xhigh | OpenAI blog Appendix (vs 56.4% GPT-5.2-Codex, 55.6% GPT-5.2) |
| **Terminal-Bench 2.0** | **77.3%** | xhigh | OpenAI blog (vs 64.0% 5.2-Codex — biggest jump) |
| **OSWorld-Verified** | **64.7%** | xhigh | OpenAI blog (vs 38.2% 5.2-Codex) |
| **GDPval (wins/ties)** | **70.9%** | xhigh | OpenAI blog (matches GPT-5.2) |
| **Cybersecurity CTF** | **77.6%** | xhigh | OpenAI blog (vs 67.4% 5.2-Codex) |
| **SWE-Lancer IC Diamond** | **81.4%** | xhigh | OpenAI blog (vs 76.0% 5.2-Codex) |
| **SWE-bench Verified** | ~85% | (xhigh?) | BenchLM (vs Claude Opus 4.7 Adaptive 87.6%, Claude Mythos 5 95.5%) |
| **Vibe Code Bench v1.1** | 61.77% | — | BenchLM (vs Claude Opus 4.7 71%) |
| **LiveCodeBench** | 71% | — | automatio.ai |
| **HumanEval** | 93% (saturated) | — | automatio.ai |
| **MMLU** | 93% (saturated) | — | automatio.ai |
| **MMLU-Pro** | 83% | — | automatio.ai (Qwen3.7 Max leads at 89.6% per BenchLM) |
| **GPQA** | 81% (automatio) / **91.5 (96th %ile)** | — | discrepancy — second is more recent/correct |
| **AIME 2025** | 94% | — | automatio.ai |
| **MATH** | 96% | — | automatio.ai |
| **GSM8K** | 99% (saturated) | — | automatio.ai |
| **HLE (Humanity's Last Exam)** | 36% | — | automatio.ai |
| **IFEval** | 94% | — | automatio.ai |
| **MMMU (multimodal)** | 84% | — | automatio.ai |
| **MMMU-Pro** | 64% | — | automatio.ai |
| **ChartQA** | 91% | — | automatio.ai |
| **DocVQA** | 95% | — | automatio.ai |
| **MathVista** | 78% | — | automatio.ai |
| **JobBench** | 33.7% | — | BenchLM (vs Muse Spark 1.1 54.7%) |
| **Intelligence Index (artificial analysis)** | 45.5 (96th percentile) | — | pricepertoken (likely xhigh) |
| **Intelligence Index (Ominigate)** | **61.4 — #26 of 148** | — | Ominigate 2026-08 (different aggregator) |
| **Speed** | 128 tok/s output, 34.39s TTFT | — | pricepertoken |

**Reading the table**: GPT-5.3-Codex is **dominant on agentic benchmarks that measure end-to-end task execution** (Terminal-Bench, OSWorld, SWE-Lancer, Cyber CTF) but **not exceptional on isolated-code-perf benchmarks** (HumanEval/LiveCodeBench/SWE-bench-Pro are not chart-topping). It's a "computer-using agent" model, not a "write a function" model.

---

## 5. Capability Assessment

### Reasoning
- **Full reasoning model with effort levels** (`low`/`medium`/`high`/`xhigh`); all OpenAI benchmarks above were at xhigh. Reasoning tokens are emitted and visible in Responses API.
- Community testing (llmreference comparison table) places it between GPT-5.5 Instant and Claude Opus 4.7 in raw intelligence, well below Claude Opus 4.8/5/Fable 5.
- xhigh reasoning is **what unlocks the agentic/computer-use gains** — `low`/`medium` likely degrade Terminal-Bench significantly (not separately published, but pattern is consistent across GPT-5.x family).

### Coding
- **The headline use case.** Beats all predecessors on Terminal-Bench 2.0 (+13pp) and OSWorld (+26pp), 25% faster, fewer tokens per task than any prior model.
- Particularly strong on:
  - **Multi-file production codebase refactoring** (OpenAI demos)
  - **Backend service development** (early adopter feedback)
  - **Terminal automation / DevOps / shell scripting** (Terminal-Bench leader)
  - **Frontend with aesthetic/compaction** (OpenAI blog racing/diving game demos)
  - **Long-running tasks with steering** ("like a colleague" — mid-task interactivity)
- Weaker on isolated single-shot code (HumanEval 93% is saturated anyway, not differentiating).

### Multimodal
- **Vision input ✅, vision output ❌** (per OpenAI docs).
- Strong MMMU 84%, ChartQA 91%, DocVQA 95% — reads screenshots, charts, documents well.
- Suitable for "screenshot to code" / "diagram to spec" workflows.

### Long-context performance
- 400K context (272K max input cap, 128K output).
- **Independent needle-in-haystack data not yet published** for 5.3-Codex (the gkamradt/needle-in-a-haystack v2 tooling supports OpenAI/Anthropic but no published 5.3-Codex sweep as of 2026-08-28). ❓ Watch for community runs.
- Codex app reportedly uses **native context compaction** for long agentic sessions.

### Function calling / tool use
- ✅ Function calling, hosted_shell, web_search, skills, structured outputs.
- Per OpenAI docs, supports `tool_choice` and `tools` parameters.
- Skills system (the AGY-Skills precedent) lets you provide contextual files that guide chain-of-thought.

### JSON mode / structured output
- ✅ `response_format` + `structured_outputs` per OpenRouter typingmind guide.

### System prompt following
- Not specifically benchmarked for 5.3-Codex; inherits GPT-5.2 alignment with **No traditional "refusal"** — OpenAI uses "safe completions" (partial answers within safety constraints).

### Interactive steering
- **Unique**: Codex app allows mid-task follow-ups ("ask questions, discuss approaches, steer toward the solution") — this is exposed in Codex app settings, not directly via API. Real-time interactivity is the model design point.

### "Trusted Access for Cyber" gate
- First model OpenAI classifies as **High capability for cybersecurity** under its Preparedness Framework.
- Some requests with elevated cyber risk **auto-route to GPT-5.2** instead of GPT-5.3-Codex.
- Security researchers / defenders can apply for **Trusted Access for Cyber** for full 5.3-Codex access on cyber work.
- Cybersecurity CTF 77.6% score is BELOW OpenAI's internal deployment threshold without the cyber safety stack applied.

---

## 6. Known Limitations

- **No Chat Completions support** — only `/v1/responses` (per OpenAI docs). Breaks naive OpenAI-compatible integrations.
- **No Batch API** — can't get 50% batch discount.
- **No fine-tuning** — fixed checkpoint (only `gpt-5.3-codex` snapshot, no per-org customization).
- **No free tier** — minimum Tier 1 spend (~$5) for API access; ChatGPT requires Plus/Pro/Team/Enterprise.
- **Knowledge cutoff Aug 31, 2025** — any task requiring post-cutoff info is at risk; web_search tool helps for live info.
- **Cyber task routing to 5.2** — security work might silently fall back to weaker model unless Trusted Access applied.
- **Ecosystem friction** — designed for the Codex app/CLI/IDE first; API users face a learning curve (Responses endpoint, reasoning effort config, hosted_shell nuances).
- **"Ecosystem Friction: Primary access is optimized for the specialized Codex app and CLI, posing a learning curve for standard API users"** — automatio.ai community feedback.
- **Latency: TTFT 34.39s** — long time-to-first-token means Cline users will see a long pause before streaming starts. Plan UX around this.
- **High cost** — 12.5×/50× more expensive than V4 Flash on input/output; rate-limit pressure at Tier 1 (500 RPM / 500K TPM).
- **Rate limits at Tier 1 are tight for a 8-account burst pattern** — 500 RPM total at Tier 1, shared across all keys in the org. Need to check per-key vs per-org splitting.

---

## 7. Comparison Matrix

| Metric | GPT-5.3-Codex | GPT-5.5 (Apr 2026) | Claude Opus 4.6 | Gemini 3.1 Pro | DeepSeek V4 Flash | minimax-m3:free (house) |
|---|---|---|---|---|---|---|
| **Released** | 2026-02-05 | 2026-04-24 | ~Q1 2026 | Q1 2026 | 2026 (per house KB) | n/a (free router model) |
| **Context** | 400K (272K in) | ~1M (922K in / 128K out) | 200K | 128K–1M | 1M | (small) |
| **Max output** | 128K | 128K | (n/a published) | (n/a published) | (n/a published) | (small) |
| **Input $/M** | $1.75 | $5.00 | $5.00 | $2.00 | $0.14 | $0 (free) |
| **Cached in $/M** | $0.175 | $0.50 | (n/a) | (n/a) | (likely) | n/a |
| **Output $/M** | $14.00 | $30.00 | $25.00 | $12.00 | $0.28 | $0 (free) |
| **Knowledge cutoff** | Aug 2025 | Dec 2025 | (later) | (later) | (later) | (varies) |
| **SWE-Bench Pro** | **56.8%** | (per rapidevelopers) | 54.2% (claude5.ai) / 76.2% Verified | 48.3% (claude5.ai) | (n/a directly) | n/a |
| **Terminal-Bench 2.0** | **77.3%** | (likely higher) | 83 (rockb) / 68.4% (claude5.ai) | 78 (rockb) / 64.1% (claude5.ai) | (likely lower) | n/a |
| **LiveCodeBench** | 71% | n/a published here | n/a | n/a | n/a | n/a |
| **OSWorld-Verified** | **64.7%** | n/a | 38.2% (5.2-Codex comparison) | 37.9% (5.2 comparison) | n/a | n/a |
| **GPQA** | 91.5 (96 %ile) | (n/a here) | (n/a here) | (n/a here) | n/a | n/a |
| **AIME 2025** | 94% | n/a | n/a | n/a | n/a | n/a |
| **MMLU-Pro** | 83% | n/a | n/a | n/a | n/a | n/a |
| **Intelligence Index** | 61.4 (Ominigate) / 45.5 (pricepertoken) | (n/a) | (n/a) | (n/a) | 50.2 (Ominigate) | ~46 (Ominigate) |
| **Routing endpoint** | Responses only | Chat Completions ✅ | Messages | (multi) | Chat Completions | n/a |
| **Specialization** | Coding/agentic | General frontier | Long-context reasoning | Multimodal general | Cost-effective general | Free fallback |
| **Best for** | Terminal workflows, long-running agentic coding, computer use | General frontier quality | Architecture decisions, deep reasoning | Multimodal+long context | High-volume cheap calls | Free experimentation |

**Where GPT-5.3-Codex wins**:
- Terminal-Bench 2.0 (beats Opus 4.6 +13pp)
- OSWorld (beats Opus 4.6 +26pp; 5.2 baseline +26pp)
- Cybersecurity CTF (77.6%)
- Cost-per-call vs GPT-5.5 / Claude Opus 4.6 (≈3× cheaper on input, 2× on output)
- 25% speedup over its own predecessor

**Where it loses**:
- SWE-bench Verified (~85% per BenchLM) — Claude Opus 4.7 Adaptive 87.6%, Claude Mythos 5 95.5%
- Vibe Code Bench (61.77%) — Claude Opus 4.7 71%
- JobBench (33.7%) — Muse Spark 1.1 54.7%
- Intelligence Index vs Claude Opus 4.8/Fable 5/Opus 5
- Context window vs Gemini 3.1 Pro (1M) and DeepSeek V4 Flash (1M)
- Cost vs DeepSeek V4 Flash (12.5× / 50×)
- Free availability vs `minimax-m3:free` (n/a)

---

## 8. Access Methods (EXACT strings)

### 8.1 Direct OpenAI API
```bash
curl -X POST https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.3-codex",
    "input": "Your prompt here",
    "reasoning": {"effort": "xhigh"}
  }'
```
- **NOT** `/v1/chat/completions` — use `/v1/responses`
- Set `reasoning.effort` to `low`/`medium`/`high`/`xhigh`
- Python SDK: `client.responses.create(model="gpt-5.3-codex", ...)`

### 8.2 OpenRouter
```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "HTTP-Referer: https://your-site.com" \
  -d '{
    "model": "openai/gpt-5.3-codex",
    "messages": [{"role": "user", "content": "..."}]
  }'
```
- Model ID: `openai/gpt-5.3-codex`
- $1.75 / $14
- OpenRouter abstracts the Responses-vs-Chat-Completions routing (their server translates)
- Multi-provider redundancy (2+ providers per OpenRouter listing)
- **Recommended for house 8-account Cline review** — see §10.

### 8.3 Vercel AI Gateway
- Model ID: `gpt-5.3-codex`
- Base URL: `https://ai-gateway.vercel.sh/v1`
- Same pricing ($1.75/$14)

### 8.4 Azure OpenAI Service
- Model: `gpt-5.3-codex` (Q1 2026 GA)
- Same pricing as OpenAI direct
- Endpoint route: `/openai/deployments/<deployment-name>/responses` (Responses API path)

### 8.5 Cline CLI
Cline docs use the "OpenAI Compatible" provider for custom models. For GPT-5.3-Codex specifically:
- **API Provider**: OpenAI Compatible
- **Base URL**: `https://api.openai.com/v1` (direct) OR `https://openrouter.ai/api/v1` (recommended, abstracted)
- **Model ID**: `gpt-5.3-codex` (direct) OR `openai/gpt-5.3-codex` (OpenRouter)
- **API Key**: `sk-...` (OpenAI) OR `sk-or-v1-...` (OpenRouter)
- **Context Window**: 400000
- **Max Output Tokens**: 128000
- **Image Support**: ✅ (per OpenAI docs)
- **Input Price per Million**: 1.75
- **Output Price per Million**: 14.0

⚠️ Cline's OpenAI Compatible provider may default to `/v1/chat/completions` — for direct OpenAI access, verify Cline routes to `/v1/responses` or use OpenRouter. **For the 8-account Cline review, OpenRouter is the safe default** (handles endpoint translation automatically).

### 8.6 Codex CLI / App / IDE
- OpenAI's own CLI/IDE: `codex` command in terminal, Codex app, VS Code / JetBrains / Cursor extensions
- Auth: OpenAI account
- Primary, optimized access path for this model

### 8.7 OpenCode Zen (CURRENT FABRIC?)
- **NOT YET LISTED** as of 2026-08-28 (only the older `gpt-5-codex`)
- May need a custom provider entry; Architect confirmation recommended before assuming fabric coverage

---

## 9. Best Practices (synthesized from OpenAI cookbook + community)

### Recommended System Prompt
- **Be explicit about the work domain** (e.g. "You are working in a multi-file Python project with pytest test suite…")
- **Specify file/context expectations** ("Read existing modules before proposing changes")
- **Use Plan mode for refactors** ("Outline your strategy before editing any files")
- **For long agentic sessions**: enable context compaction, prefer incremental commits

### Temperature / Sampling
- **Default temperature for code**: 0.0–0.2 (deterministic)
- **For creative brainstorming / design**: 0.7
- GPT-5.3-Codex does NOT need high temp for diversity (reasoning effort handles that)

### Max Tokens
- **128K max output** — set `max_output_tokens: 128000` for full output headroom
- For typical agentic turns, 8K–32K is sufficient

### Reasoning Effort
- **`xhigh`** for: hard architectural decisions, terminal workflows, complex multi-file refactors, security research
- **`high`** for: production code review, bug hunting, test generation
- **`medium`** for: routine code generation, simple edits
- **`low`** for: simple completions, autocompletion-style

### Prompt Patterns That Work
1. **Spec-driven**: "Here is the spec. Here are the existing tests. Implement to pass them."
2. **PR-style**: "Here is the PR diff. Review for correctness, performance, and edge cases."
3. **Socratic debugging**: "This test fails with X. Don't fix it yet — diagnose the root cause first."
4. **Batch PR review**: "Here are 5 feature branches. For each: assess integration risk."
5. **Mid-task steering**: "Now consider the security implications. Adjust if needed."

### Prompting Gotchas
- **No "messages" array** (use Responses API input format with `input` string or array of content items)
- **For vision**: pass images as base64 in input items with `type: "input_image"`
- **For function calling**: define tools in `tools` array; model returns `tool_calls` in output

---

## 10. Strategic Implications for the 8-Account Cline Review

### Cost reality check
- **Per 1M input tokens, 5.3-Codex is 12.5× V4 Flash**; per 1M output, 50× V4 Flash
- 8 accounts × bursty Cline workloads × gpt-5.3-codex standard calls = significant spend
- **Mitigation**: route by task class:
  - **Agentic / terminal workflows / complex refactors** → GPT-5.3-Codex via OpenRouter
  - **High-volume code review / boilerplate generation** → DeepSeek V4 Flash (12.5× cheaper)
  - **Free experimentation / throwaway** → minimax-m3:free (current default)
  - **Frontier non-coding** → GPT-5.5 or Claude Opus 4.6 via established routes

### Routing architecture recommendations
1. **Primary path: OpenRouter** — abstracts Responses-vs-Chat-Completions, multi-provider redundancy, immediate availability, single billing point
2. **Direct OpenAI API as fallback** — for tasks needing OpenAI-specific features (Trusted Access for Cyber, hosted_shell, web_search with OpenAI's index)
3. **Azure for org compliance** — if house has data-residency requirements
4. **Cline custom config** — use OpenAI Compatible provider with `gpt-5.3-codex` + OpenRouter base URL, NOT direct OpenAI (avoids endpoint-routing risk)

### Rate-limit budgeting
- Tier 1: 500 RPM, 500K TPM, **shared across all keys in org** (per OpenAI docs)
- 8 accounts on Tier 1 = effectively 500 RPM total = ~6.25 RPM per account average
- Need to either (a) get to Tier 2 (5,000 RPM) for burst headroom, or (b) stagger accounts by 1-2 minutes
- **Recommend starting on Tier 1 with a single dedicated OpenAI-org, monitoring, then graduating to Tier 2**

### Quota & monitoring
- Per OpenAI docs: "approved monthly usage limit for each organization" + tier-based auto-graduation
- Cline logs (existing house infra) should already capture per-request model + token counts; pipe to existing quota tracking
- Set explicit spend limits at the org level (OpenAI supports spend caps per org/project)

### Risks
1. **TOS exposure**: ❌ low — OpenAI's own API, no third-party-client issue (unlike Antigravity plugin)
2. **Ban-wave risk**: ❌ low — OpenAI doesn't do automated TOS_VIOLATION disables for legit API use
3. **Cost overrun**: 🔴 HIGH — 8 accounts × 5.3-Codex standard = real money; require explicit budget gate before fleet rollout
4. **Endpoint mismatch**: 🟡 MEDIUM — Cline "OpenAI Compatible" provider may not natively route to `/v1/responses`; use OpenRouter to abstract
5. **Reasoning effort drift**: 🟡 MEDIUM — without explicit `reasoning.effort` config, model may default to lower reasoning, eroding the 5.3 advantage

### Action items for the review
- [ ] Confirm Architect's "GPT 5.3" = GPT-5.3-Codex (or clarify intended model)
- [ ] Decide routing path: OpenRouter (recommended) vs direct OpenAI vs Azure
- [ ] Test Cline custom provider config with `gpt-5.3-codex` + OpenRouter base URL on ONE account first
- [ ] Set OpenAI org-level spend cap before enabling other 7 accounts
- [ ] Set per-account budget gate in Cline config
- [ ] Capture baseline metrics (latency, quality, cost) on a representative workload
- [ ] Add a "tier-class" routing layer in the provider fabric — gpt-5.3-codex for agentic, V4 Flash for high-volume, m3 for free

---

## 11. Source Index (all claims sourced; ratings = verification depth)

### Primary
- **[OpenAI blog, 2026-02-05]** Introducing GPT-5.3-Codex — release date, capabilities, benchmarks, system card link: https://openai.com/index/introducing-gpt-5-3-codex/
- **[OpenAI API docs, fetched 2026-08-28]** GPT-5.3-Codex Model — model ID, context, pricing, rate limits, endpoint support, supported tools, knowledge cutoff: https://developers.openai.com/api/docs/models/gpt-5.3-codex
- **[OpenRouter]** GPT-5.3-Codex — $1.75/$14, 400K context, 2+ providers: https://openrouter.ai/openai/gpt-5.3-codex

### Secondary (independent)
- **[BenchLM, 2026-08-25]** GPT-5.3-Codex benchmarks vs Claude/Gemini: https://benchlm.ai/models/gpt-5.3-codex
- **[automatio.ai, 2026-02-05]** Full benchmark profile (MMLU 93%, GPQA 81%, AIME 94%, etc.): https://automatio.ai/models/gpt-5-3-codex
- **[Ominigate, 2026-02-24]** Intelligence Index 61.4, #26 of 148: https://ominigate.ai/en/models/openai/gpt-5.3-codex/benchmarks
- **[pricepertoken, 2026-02-24]** Intelligence 45.5 (96th %ile), GPQA 91.5, speed, cache pricing: https://pricepertoken.com/pricing-page/model/openai-gpt-5.3-codex
- **[rockb, 2026-04-27]** GPT-5.3-Codex vs Claude Opus 4.6 vs Gemini 3.1 Pro: https://baeseokjae.github.io/posts/gpt-5-vs-claude-opus-4-vs-gemini-3-coding-2026
- **[apidog, 2026-02-25]** How to use GPT-5.3-Codex API: https://apidog.com/blog/gpt-5-3-codex-api/
- **[llmreference, 2026-06-29]** Provider routes, comparison: https://www.llmreference.com/model/gpt-5.3-codex
- **[claude5.ai, 2026-02-10]** Codex 5.3 release analysis: https://claude5.ai/news/codex-53-released-benchmark-analysis-2026

### Provider / integration
- **[TypingMind/OpenRouter guide]** Model ID, parameters, supported input types: https://www.typingmind.com/guide/openrouter/gpt-5.3-codex
- **[Cline docs]** OpenAI Compatible provider setup: https://docs.cline.bot/provider-config/openai-compatible
- **[Cline blog, 2025-09-23]** Older GPT-5-Codex integration (5.3-Codex blog post not yet published): https://cline.bot/blog/gpt-5-codex
- **[miaomiaocode.com]** Cline config example with codex.openai.com/v1: https://docs.miaomiaocode.com/en/clients/cline
- **[OpenAI Rate Limits docs]** Tier system, per-org sharing: https://developers.openai.com/api/docs/guides/rate-limits

### Context / landscape
- **[silicondata, 2026-03-16]** GPT-5 family pricing ladder: https://www.silicondata.com/use-cases/openai-api-pricing-per-1m-tokens
- **[rapidevelopers, 2026-07-10]** GPT-5.5 as current flagship, $5/$30: https://www.rapidevelopers.com/ai-api-limits-performance-matrix/gpt-5
- **[lmmarketcap, 2026-08-28]** Comprehensive benchmark table: https://lmmarketcap.com/benchmarks

### Speculative / unverified (per M23)
- ❓ Independent NIAH (needle-in-haystack) test for GPT-5.3-Codex at 100K/272K/400K — **not yet published as of 2026-08-28**
- ❓ Regional availability outside standard OpenAI banned-region list — assumed standard; not separately verified
- ❓ Whether Cline's "OpenAI Compatible" provider defaults to `/v1/responses` or `/v1/chat/completions` — needs direct test
- ❓ Whether OpenCode Zen will add `gpt-5.3-codex` (only `gpt-5-codex` listed as of 2026-08-28)
- ❓ GPQA score discrepancy (81% automatio vs 91.5% pricepertoken) — both reported; the higher likely reflects a different aggregator or reasoning tier

---

*⬡ OMEGA ⬡ GROKSTER ⬡ R_ANTIGRAVITY_GPT53_20260828 ⬡ Antigravity Specialist ⬡ Resumed per L3 121*
