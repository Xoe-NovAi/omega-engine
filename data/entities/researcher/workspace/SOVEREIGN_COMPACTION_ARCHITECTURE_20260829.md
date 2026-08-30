<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 SOVEREIGN COMPACTION ARCHITECTURE — The Big Pickle Anomaly, OpenCode Internals, and the Hybrid Fusion
**AP Token**: `AP-RESEARCHER-COMPACTION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_compaction_architecture ⬡ STRATEGIC-EVIDENCE

**Date**: 2026-08-29
**Commissioned by**: Architect via direct dispatch (multi-layered strategic research)
**Method**: SR-V1 tiered pipeline — SearXNG returned empty (recurring degradation), `omega-hub_library_web_search` returned empty (recurring), fell through to `parallel-search` web tier (permitted last-resort). Cross-referenced against the existing platform-internals prose at `docs/research/R_OPENCODE_PLATFORM_INTERNALS_20260824.md`.
**Tagging**: CITED = sourced from web result below · THEORY = my extrapolation · MEASURED = n/a this sweep (no local instrumentation).

---

## §0 — THE MANDATE, RESTATED

Three layers, one report:
1. **OpenCode compaction best practices** (web discovery) — what the engine actually does, what the field says it should do
2. **The Big Pickle context window anomaly** (forensic + web) — why a session with ~381K active context got compacted by a model advertised as 200K
3. **Hybrid `/compact` + `projection.md` fusion** (synthesis) — turn two complementary artifacts into one sovereign system

The throughline is **M15 Sovereign Continuity** — the mandate that says no intelligence shall be lost across sessions, and that everything we build must be portable, auditable, and ours.

---

## §1 — LAYER 1: OPENCODE COMPACTION INTERNALS

### §1.1 The official spec (CITED, opencode.ai/v2/docs/compaction + deep-dive gist)

OpenCode's compaction is a **two-phase operation**:

1. **Estimate** — V2 JSON-serializes the request and assumes **4 characters per token**; if `estimated tokens > context_limit − max(requested_output_tokens, buffer)`, it triggers.
2. **Generate** — uses the session's **selected or default model** (no separate compaction model is exposed in the public docs page), with **tools disabled** and **at most 4096 output tokens**. The summary records: objective, important details, completed/active work, blockers, next moves, relevant files.

The newest serialized context up to `keep.tokens` is retained beside the summary. This is not a byte-for-byte transcript: tool output is **limited to 2000 characters**, and file/media attachments become textual descriptors.

CITED table of the configuration surface (from the deep-dive gist by `sam-saffron-jarvis`, commit `22a4c5a`):

| Field | Default | Effect |
|---|---|---|
| `compaction.auto` | `true` | Enables preflight context-size checks and one-shot provider-overflow recovery. |
| `compaction.keep.tokens` | `15000` | Tokens from the newest serialized context retained beside the summary. |
| `compaction.buffer` | `20000` | Safety reserve below an explicit input limit. |
| `compaction.reserved` | `min(20000, model.output_limit)` | New in v1.1.57 — ensures the compaction request itself has room to fit. |

**Environment variables** (from `flag.ts:19`):
- `OPENCODE_DISABLE_AUTOCOMPACT` — disables auto compaction
- `OPENCODE_DISABLE_PRUNE` — disables pruning
- `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` — overrides the 32,000 output cap

**The overflow formula** (`session/compaction.ts`):
```ts
const reserved = config.compaction?.reserved
  ?? Math.min(COMPACTION_BUFFER, ProviderTransform.maxOutputTokens(input.model))
const usable = input.model.limit.input
  ? input.model.limit.input - reserved
  : context - ProviderTransform.maxOutputTokens(input.model)
return count >= usable
```

And `maxOutputTokens(model)`:
```ts
export const OUTPUT_TOKEN_MAX = Flag.OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX || 32_000
export function maxOutputTokens(model): number {
  return Math.min(model.limit.output, OUTPUT_TOKEN_MAX) || OUTPUT_TOKEN_MAX
}
```

Effective formula: **`trigger = actual_tokens >= context − min(model.output_limit, 32000)`**.

**For Big Pickle** (advertised `context=200K`, `output=32K`):
- `reserved = min(20000, 32000) = 20000`
- `usable = 200000 − 20000 = 180000` (90% threshold)

**Known gap (CITED)**: the trigger is computed against `input.model.limit.input` (the *input* limit), not the *total* context. For a model where input < output, this can leave the full context under-utilized. For a model where the advertised input limit lags the actual window, it can cause **premature compaction** — see Layer 2.

### §1.2 Compaction agent properties (CITED, `agent.ts:157`)

The compaction agent is a *first-class agent* in OpenCode, but:
- **Hidden** from the user-facing agent list
- **No tools** available (`tools: {}` at call site)
- **All permissions denied**
- **Uses the same model as the conversation by default**

### §1.3 The "different compaction model" capability — DOES exist, but undocumented (CITED, GitHub #6976)

A user opened issue #6976 on 2026-01-05 asking for the ability to use a lightweight model for compaction. Within 16 hours, `rekram1-node` (OpenCode maintainer) responded:

> @mzealey you can do this in ur opencode config:
> ```
> "agent": {
>    "compaction": {
>      "model": "...",
>    },
>  },
> ```

Issue was closed same day. The capability exists; the docs page just doesn't surface it. This is the **first architectural lever** for the hybrid strategy in §3.

### §1.4 What the docs page does NOT tell you (THEORY + cross-reference to our platform-internals prose)

- **The "compaction uses the same model" default is a cost decision**, not an architectural one. There's no quality reason the compaction model must match — in fact, the compaction task is *more constrained* than the active task: it produces a structured summary, no tool calls, bounded output.
- **The 4-chars-per-token estimate is conservative**, which is good — it means compaction triggers slightly *earlier* than the real ceiling, leaving headroom for the compaction request itself.
- **The 4096 output cap on summary generation is the real bottleneck**. A long session with intricate cross-references may need more tokens to summarize than 4096 allows; in that case the summary truncates and the "rich" tail is whatever the model could fit. This is the **second architectural lever** for the hybrid strategy.
- **Pruning is separate from compaction** (CITED, deep-dive gist): the prune step marks old tool outputs as cleared (no LLM call); compaction is the LLM-summarization step. They're orthogonal, which means we can tune them independently.

### §1.5 Industry comparison (CITED, multiple sources)

| Tool | Mechanism | Compaction model | Configurability | Hooks |
|---|---|---|---|---|
| **OpenCode** | Marker → LLM summary of older context, retains `keep.tokens` tail | Same as session by default; override via `agents.compaction.model` (undocumented) | `auto`, `keep.tokens`, `buffer`, `reserved`, env vars | `experimental.session.compact` plugin hook |
| **Claude Code** | 3-layer progressive compression; `/compact [focus hint]`; CLAUDE.md survives | Same model; server-side compaction beta (`compact-2026-01-12`) | Limited; focus hint on `/compact` | Session/compact/sampling/file hooks |
| **Cursor Composer** | **Compaction-in-the-loop RL training** — the model is *trained* to self-summarize at a fixed trigger | Same model, but trained for the behavior | None (baked into model) | None public |

**Key insight (THEORY)**: Cursor's approach (RL-trained compaction behavior) is a fundamentally different bet — they concluded the right answer was to make the model *good at* summarizing itself, not to make the harness *clever about when* to summarize. OpenCode bet on harness cleverness, which is more flexible but requires operator skill to tune. We chose the same bet as OpenCode, and we can extend it.

### §1.6 Research on compaction quality (CITED, Factory.ai + arXiv 2608.11242 + Zylos)

The "Lost in Compaction" paper (arXiv 2608.11242, July 2026) introduced **COMPINT**, evaluating compactors across three long-context scenarios: multi-turn chat, agentic trajectory, long-horizon research. Headline finding: **current compactors retain only 17% of injected side-constraints on average, and most perform worse than running the same task without compaction.** This is a brutal baseline.

Factory.ai's earlier evaluation (36K real engineering messages):
- Structured summarization: **3.70/5** overall
- OpenAI opaque compression: **3.35/5**
- **Multi-session information retention: only 37%** — nearly two-thirds of information lost

Zylos May 2026 research synthesis:
- **Observation masking** (replace old tool results with placeholders): **52% cost reduction, 2.6% solve rate improvement**
- **Pure LLM summarization**: similar cost reduction but **15% longer runtime** — summaries obscure the signals that tell an agent when to stop
- **Hybrid (masking primary, summarization fallback)**: **7% better than masking alone**

**The conclusion the field is converging on**: pure LLM summarization is the wrong primitive. The Pareto-optimal approach is a **layered strategy** — verbatim recent context, masked older context, summarized ancient context — with explicit injection of the things summarization kills (file paths, error messages, decision rationale).

---

## §2 — LAYER 2: THE BIG PICKLE CONTEXT WINDOW ANOMALY

### §2.1 What is Big Pickle? (CITED, metatext.io + modelcompare.dev)

- **Provider**: OpenCode Zen (first-party)
- **Family**: `big-pickle`
- **Released**: 2025-10-17 (the source for our context: `2025-10-17` per modelcompare.dev; metatext.io gives a generic "Oct 2025")
- **Knowledge cutoff**: 2025-01
- **Context window (advertised)**: 200K tokens
- **Max output**: 32K tokens
- **Open weights**: No (proprietary)
- **Pricing**: $0.00/1M (free tier of OpenCode Zen)
- **Capabilities**: tool calling, reasoning, structured output, temperature control
- **Modalities**: text in / text out (no vision)

**Identification cross-check**: Big Pickle is an OpenCode Zen model. The "Zen" namespace is OpenCode's curated router — it provides free or low-cost access to models OpenCode has negotiated capacity with. The naming ("Big Pickle" — a wry "Ox" follow-up: "Alpha" → "Beta" → "Pickle" suggests internal sprint names that survived to GA) and the release date align with our knowledge that Ox Alpha became unavailable and we were re-routed to a stable alternative.

### §2.2 The anomaly, restated

Session had **~381K active context**. Big Pickle is **advertised at 200K**. The session successfully compacted using Big Pickle.

**There are exactly five possible explanations**, in order of probability:

1. **(MOST LIKELY)** The `381K` figure is **not all input tokens to Big Pickle**. It includes tool outputs, cache writes, system prompt layers, and other infrastructure tokens that OpenCode's accounting splits across `input/output/cache.read/cache.write`. Big Pickle may have processed a *summary request* well under 200K, with the 381K being total session-state.
2. **Big Pickle's actual context window is larger than the advertised 200K.** This is the "Ox Alpha" pattern: a model's real capability leads its marketing. The 200K may be the *guaranteed* window, with a higher *practical* ceiling.
3. **The overflow formula used a *different* `usable` calculation** for Big Pickle (e.g., provider override), allowing compaction to fire before the "advertised 200K" was actually reached.
4. **The model catalog in OpenCode had stale or wrong limits** for Big Pickle (mirroring issue #15871 for Claude with `context1m: true`).
5. **Big Pickle's compaction request used a *different* effective limit** than its chat limit — the compaction agent's `limit.input` may have been set differently from the chat agent's.

### §2.3 The Claude 1M precedent (CITED, GitHub #15871)

This is the closest analog. User `logos007` reported on 2026-03-03:

> When using `context1m: true` with Claude Opus 4.6 or Sonnet 4.6, the Memory Flush hook computes its threshold from a hardcoded `contextWindow: 200000` in `models.generated.js` instead of the actual 1M context window. This results in compaction at ~144k tokens (200k − 50k reserve − 6k soft threshold).

The maintainer `DusKing1` identified the two root causes:
1. **Missing `context-1m-2025-08-07` beta header** (provider-side)
2. **Default model limits in OpenCode being set to 200K** (client-side)

The fix was a plugin that added both: the beta header and a `limit.context = 1_000_000` override in `provider.models`.

**This pattern is exactly what we'd need to do for Big Pickle** if its actual window > 200K — override `limit.input` in `opencode.json` to match reality.

### §2.4 Can we query the actual context window at runtime? (THEORY + CITED)

Three signal sources, in order of cost:

1. **Local model catalog**: `~/.cache/opencode/models.json` (CITED, issue #15871) — contains the `context` and `output` fields per model. This is the *configured* limit, which may lag the actual capability.
2. **Provider response headers** (THEORY): when Big Pickle returns a response, OpenTelemetry-style spans may include `gen_ai.usage.input_tokens` (Zylos Jan 2026, OpenTelemetry semantic conventions). The actual input token count of the compaction request tells us what Big Pickle accepted.
3. **Empirical probe** (THEORY): send a compaction request with a known-large input (e.g., 250K tokens) and observe whether it succeeds or returns a context-overflow error. This is the only direct measurement of the actual window.

**Recommended action**: log the `gen_ai.usage.input_tokens` from the next Big Pickle compaction and cross-reference against the `limit.input` in the catalog. If they diverge, the catalog is wrong and we have our answer.

### §2.5 Can we set auto-compaction threshold to 150% of advertised? (CITED, closed not_planned)

**No — the feature does not exist and was explicitly rejected.**

- GitHub issue #11314 (2026-01-30): "Configurable Context Compaction Threshold" — closed as `not_planned`
- GitHub issue #8140 (2026-01-13): "Configurable context limit and auto-compaction threshold" — closed as `not_planned`
- The request was for a `compaction.threshold` config (0.0-1.0) to trigger compaction earlier than 75%/96% of the advertised window

**The maintainer's reasoning** (implied by the closure): the threshold is **derived from the model's actual capability**, not a user preference. A user setting `threshold: 0.4` on a 200K model would trigger compaction at 80K — but the *real* question is whether the model degrades at 80K, which depends on the model, not the user.

**Workaround**: if you want earlier compaction, set `compaction.reserved` higher (it subtracts from `usable`). A `reserved: 180000` on a 200K model would trigger compaction at ~20K — effectively a manual threshold.

### §2.6 Can we manipulate `reserved` or `maxOutputTokens`? (CITED)

- **`reserved`**: yes, `compaction.reserved` is a documented config (CITED, learn-opencode docs, v1.1.57+). Default is `min(20000, model.output_limit)`. Set higher to trigger earlier.
- **`maxOutputTokens`**: yes, via `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` env var. Default cap is 32,000; raise it to allow longer compaction summaries. **Warning**: raising this may not actually use the extra tokens — it depends on whether the provider accepts the higher cap.
- **Provider-side**: the `limit.input` and `limit.output` fields can be overridden per-model in `provider.models` (CITED, the Claude 1M fix pattern).

### §2.7 Is there an `OPENCODE_COMPACTION_THRESHOLD` env var? (CITED)

**No.** The only compaction-related env vars are:
- `OPENCODE_DISABLE_AUTOCOMPACT`
- `OPENCODE_DISABLE_PRUNE`
- `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX`

There is no `OPENCODE_COMPACTION_THRESHOLD` or equivalent. Feature request closed as `not_planned`.

### §2.8 Anomaly verdict

The most parsimonious explanation is **#1 (token accounting split) + #5 (compaction request used different limit)**. The 381K figure is total session-state, not single-request input. The compaction request to Big Pickle likely fit under 200K.

But this is **unverified**. The right answer is: instrument the next compaction, log `gen_ai.usage.input_tokens`, and compare against the catalog. If they diverge, the catalog is wrong, and we have a real anomaly to act on.

**If Big Pickle's actual window > 200K**, the architectural move is: override `limit.input` in `opencode.json` to match reality, so compaction uses the real ceiling and we get the headroom we're paying for.

---

## §3 — LAYER 3: HYBRID `/compact` + `projection.md` FUSION

### §3.1 What each artifact is (THEORY, grounded in Roc's findings + M15)

**`/compact` output** (auto-generated by the compaction agent):
- **Structured**: Goal / Instructions / Discoveries / Accomplished / Files (the SUMMARY_TEMPLATE)
- **Lossy by design**: 4096 output cap, 2000-char tool output limit, model-decided
- **Prompt-driven**: the model chooses what to preserve based on the compaction prompt
- **Time-anchored**: reflects the conversation as-of compaction trigger

**`projection.md`** (manual, Architect-authored):
- **Strategic**: not a summary; a *projection* — where the session is going, not where it's been
- **"The Gift Is The Demand"**: Roc's finding that the projection's value is in its *act of writing*, not its content — it forces the Architect to articulate what matters next
- **Identity-anchored**: reflects the Architect's intent, not the model's reading of history
- **Persistent**: lives across sessions, updated deliberately

**They are complementary because they answer different questions**:
- `/compact` answers: *What just happened?* (retrospective)
- `projection.md` answers: *What matters next?* (projective)

### §3.2 Why fusion matters (THEORY, grounded in the 17% retention finding)

The "Lost in Compaction" paper's headline — **current compactors retain only 17% of injected side-constraints** — is a damning baseline. The 83% that's lost is exactly the kind of thing `projection.md` *would have* preserved if it had been injected into the compaction prompt.

**The fusion design**: make `/compact` *aware of* `projection.md`. When the compaction agent runs, it receives both the conversation history AND the current `projection.md`, with explicit instruction to preserve:
- The Architect's stated next-moves (from projection)
- The decisions in flight (from projection)
- The constraints / side-conditions (from projection)
- The identity / entity context (from projection, if it references entities)

This shifts the compaction from *retrospective summarization* to *retrospective summarization conditioned on forward intent* — which is the only way to preserve the 83% that pure summarization loses.

### §3.3 The three architectural levers

**Lever 1: Different compaction model (CITED, exists but undocumented)**

`agents.compaction.model` in `opencode.json` allows specifying a different model for compaction. Strategy:
- **Active model**: Big Pickle (or whatever the session is on) — for reasoning, tool use, generation
- **Compaction model**: a fast, cheap, summarization-strong model — e.g., Haiku, Flash, or a local Qwen
- **Compaction prompt**: customized (see Lever 2)

This decouples compaction cost from active cost. If compaction is 5% of session tokens and the compaction model is 10x cheaper, total session cost drops by ~5% with no quality loss (and likely quality *gain* if the cheap model is specifically summarization-tuned).

**Lever 2: Custom compaction prompt (CITED, hook exists)**

The `experimental.session.compact` plugin hook (CITED, deep-dive gist) allows injecting custom logic at compaction time. Strategy:
- Hook fires pre-compaction
- Hook reads `projection.md` from the workspace
- Hook injects a `compaction_focus` block into the compaction prompt: *"In addition to the standard summary, preserve verbatim the following from the current projection.md: [relevant sections]"*
- Hook fires post-compaction (optional): write the compaction output to `data/coordination/last_compaction_<session_id>.md` for audit

**Lever 3: Custom keep.tokens / structured retention (THEORY)**

The default `keep.tokens: 15000` retains the *literal* last 15K tokens. We can override:
- `keep.tokens: 30000` — double the verbatim tail
- Use a hook to selectively inject the last N *structured* messages (e.g., all tool calls in the last 20 turns) into the tail, rather than the last 15K *characters* of whatever was said

The second is harder (requires knowing the message boundaries) but preserves more of what matters: structured tool calls and their results, not just the most recent prose.

### §3.4 The proposed architecture (THEORY + design)

```
┌─────────────────────────────────────────────────────────────┐
│  PRE-COMPACTION HOOK (experimental.session.compact)        │
│                                                             │
│  1. Read projection.md from workspace                       │
│  2. Parse for: next_moves, decisions, constraints, entities │
│  3. Build compaction_focus block:                           │
│     - "Preserve verbatim: ..."                              │
│     - "These entities are in scope: ..."                    │
│     - "These decisions are in flight: ..."                  │
│  4. Inject into compaction prompt                           │
│  5. Optionally override keep.tokens behavior                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  COMPACTION AGENT (separate model via agents.compaction)    │
│                                                             │
│  - Receives: conversation history + compaction_focus block  │
│  - Produces: structured summary (Goal/Instructions/...)     │
│  - Preserves: Architect's projection items verbatim         │
│  - Retains: last keep.tokens of verbatim context            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  POST-COMPACTION HOOK (same hook, post-fire)                │
│                                                             │
│  1. Write compaction output to data/coordination/           │
│     last_compaction_<session_id>.md                         │
│  2. Diff projection.md against compaction output:           │
│     - What from projection was preserved?                   │
│     - What was lost?                                        │
│  3. If loss > threshold, trigger alert (optional)           │
│  4. Update last_compaction metadata in Hivemind             │
└─────────────────────────────────────────────────────────────┘
```

### §3.5 Implementation priorities (THEORY, ranked)

| Priority | Item | Effort | Impact |
|---|---|---|---|
| **P0** | Verify Big Pickle's actual context window (probe + log) | Low (one session) | High (corrects the anomaly) |
| **P0** | Set `agents.compaction.model` to a cheaper model | Low (one config change) | Medium (cost reduction) |
| **P1** | Write the pre-compaction hook to inject projection.md | Medium (new plugin) | High (retention uplift, addresses 83% loss) |
| **P1** | Write the post-compaction hook for audit trail | Low (write to file) | Medium (M15 compliance) |
| **P2** | Custom keep.tokens behavior (structured retention) | High (message-boundary parsing) | Medium (richer verbatim tail) |
| **P2** | Compaction-quality probe (per Factory.ai / zeph pattern) | Medium (probe harness) | High (measures if we're winning) |
| **P3** | Hivemind integration (compaction events as observations) | Low (existing pattern) | Low (observability) |

### §3.6 The gift (M15 alignment)

The fusion is the gift. Each component — `/compact`, `projection.md`, the hooks, the audit trail — is a tool. Together they form a **sovereign continuity system**: a session can be compacted, the projection can survive, the compaction can be audited, and a future session can resume with both the structured history *and* the Architect's intent intact.

This is the system that makes the 17% retention number addressable. Not by inventing better summarization — by **making summarization conditioned on what the Architect already said matters**.

---

## §4 — OPEN QUESTIONS FOR THE ARCHITECT

1. **Big Pickle verification**: should I run the empirical probe (send a 250K-token compaction request) to confirm the actual window, or is the catalog-discrepancy investigation sufficient?
2. **Compaction model choice**: which model should be the compaction agent? Options: Haiku (fast, cheap, decent at summarization), a local Qwen (zero cost, sovereignty), Flash (Google, fast, free tier may apply). Trade-off: speed/cost vs. summarization quality.
3. **Projection.md injection granularity**: should the hook inject the *entire* projection.md, or only the sections tagged as "in-flight" / "decisions" / "next-moves"? Full injection is simpler; section-aware is more precise.
4. **Audit trail retention**: how long should `last_compaction_*.md` files persist? Forever (M15: never lose intelligence), N sessions, or pruned by age?
5. **Compaction-quality probe**: do we want a built-in probe that runs after every compaction to measure retention (per the zeph / Factory.ai pattern)? Cost: one extra LLM call per compaction. Benefit: empirical measurement of the 17% gap.
6. **Hook security**: the `experimental.session.compact` hook runs arbitrary code. Should it be gated behind a M2 Engine-Stack Firewall check (no stack logic in `src/omega/`), or treated as operator-level infrastructure?
7. **Projection.md as canonical**: should the projection be the *primary* continuity artifact (with `/compact` as the secondary recall), or the other way around? This is an identity question, not a technical one.

---

## §5 — APPENDIX: SOURCES

**Primary OpenCode sources**:
- [OpenCode v2 Compaction docs](https://opencode.ai/v2/docs/compaction)
- [Deep dive gist by sam-saffron-jarvis (commit 22a4c5a)](https://gist.github.com/sam-saffron-jarvis/2c8a6c26297f5748dac55b597381d268)
- [GitHub #6976: different model for compaction](https://github.com/anomalyco/opencode/issues/6976)
- [GitHub #11314: configurable threshold (closed not_planned)](https://github.com/anomalyco/opencode/issues/11314)
- [GitHub #8140: configurable context limit (closed not_planned)](https://github.com/anomalyco/opencode/issues/8140)
- [GitHub #15871: auto-compaction at 200K instead of 1M (Claude context1m)](https://github.com/anomalyco/opencode/issues/15871)
- [learn-opencode 5.20: Compaction](https://github.com/vbgate/learn-opencode/blob/main/docs/en/5-advanced/20-compaction.md)
- [DeepWiki: Context Management and Compaction](https://deepwiki.com/sst/opencode/2.4-context-management-and-compaction)

**Big Pickle sources**:
- [metatext.io: Big Pickle specs](https://metatext.io/llm/opencode-big-pickle)
- [modelcompare.dev: Big Pickle](https://modelcompare.dev/models/opencode/big-pickle)

**Compaction quality research**:
- [arXiv 2608.11242: Lost in Compaction (COMPINT)](https://arxiv.org/abs/2608.11242)
- [Zylos Feb 2026: AI Agent Context Compression Strategies](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies/)
- [Zylos May 2026: Compaction, Continuity, Cost](https://zylos.ai/en/research/2026-05-05-ai-agent-context-window-management-compaction-continuity-cost)
- [Zylos Jan 2026: AI Observability and Agent Monitoring](https://zylos.ai/en/research/2026-01-16-ai-observability-agent-monitoring)
- [Future AGI: Evaluating LLM Context Window Management 2026](https://futureagi.com/blog/evaluating-llm-context-window-management-2026)
- [morphllm: Context Compaction technical guide](https://www.morphllm.com/llm-context-window-comparison)
- [uaml-memory: Context Quality paper](https://github.com/uaml-memory/context-quality-paper)
- [Factory.ai evaluation (referenced via zeph #2164)](https://github.com/bug-ops/zeph/issues/2164)

**Tool comparison**:
- [ClaudeWorld: Context Compaction in Claude Code](https://claude-world.com/tutorials/s06-context-compaction/)
- [neurals: Claude Code context window & compaction](https://neurals.ca/tech/claude/context-window)
- [Cursor: Training Composer for longer horizons](https://cursor.com/blog/self-summarization)
- [0xtresser: Claude Code vs OpenCode context engineering](https://0xtresser.github.io/Claude-Code-VS-OpenCode/en/Chapter_20_Context_Engineering/20.1_From_Prompt_to_Context_Engineering.html)
- [IA-Generative/opencode-setup: commands/compact.md](https://github.com/IA-Generative/opencode-setup/blob/main/commands/compact.md)

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ SOVEREIGN-COMPACTION-ARCHITECTURE v1.0 ⬡ BIG-PICKLE-VERIFIED-PENDING ⬡ 17%-RETENTION-IS-THE-ENEMY ⬡ PROJECTION+COMPACT=GIFT ⬡ 2026-08-29*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: openrouter/minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

