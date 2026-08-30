<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N7 Web Research — Context Windows & OpenCode Compaction Semantics

**Tasking**: N7 context session (Memory & State, omega-engine repo)
**Scope**: WEB RESEARCH ONLY — no code changes
**Researcher**: @researcher (Sovereign Researcher)
**Date**: 2026-08-21
**Method**: Sovereign Search Protocol (websearch → webfetch → fallbacks). Primary sources preferred (official docs, model cards, GitHub source/changelog); every claim cited with URL + publication date where available. Unresolvable items are explicitly flagged.

**Local context being resolved**: live config caps `qwen3-4b-thinking` at `context_length: 8192`; internal review prose claims "Qwen3-4B (8K–16K)".

---

## Answers

### Q-B3: `OPENCODE_DISABLE_AUTOCOMPACT` — REAL and documented

**Verdict**: Real, documented env var. It disables **automatic** compaction only (maps to `compaction.auto: false`); manual `/compact` still works. Known bypass bug via provider-overflow recovery path as recently as v1.17.7 (June 2026).

Evidence (all primary):
- Defined in source: `packages/opencode/src/flag/flag.ts` → `export const OPENCODE_DISABLE_AUTOCOMPACT = truthy("OPENCODE_DISABLE_AUTOCOMPACT")`. Present identically on both `sst/opencode@dev` and `anomalyco/opencode@dev` (repo appears under both orgs; content identical). https://github.com/sst/opencode/blob/dev/packages/opencode/src/flag/flag.ts (accessed 2026-08-21)
- Officially documented in CLI env-var table: "`OPENCODE_DISABLE_AUTOCOMPACT` | boolean | Disable automatic context compaction". https://opencode.ai/docs/cli/ (accessed 2026-08-21)
- Semantics confirmed in config loader (`packages/opencode/src/config/config.ts`, dev): `if (Flag.OPENCODE_DISABLE_AUTOCOMPACT) { result.compaction = { ...result.compaction, auto: false } }` — i.e., it is exactly equivalent to setting `compaction.auto: false`, applied at config-load time (process-global scope; no per-agent/per-session variant exists). Companion flag `OPENCODE_DISABLE_PRUNE` maps to `compaction.prune: false`. https://github.com/sst/opencode/blob/dev/packages/opencode/src/config/config.ts (accessed 2026-08-21)
- Maintainer-side explanation (issue #3325, opened 2025-10-21): the var "controls whether opencode triggers a compaction when the token usage exceeds the context window"; manual `/compact` remains available. https://github.com/anomalyco/opencode/issues/3325
- ⚠️ Caveat: bug reports show the disable path being **bypassed** by the provider-overflow auto-recovery path: #16882 (2026-03-10), #30664 (repro on v1.15.13, 2026-06-04), #32385 "[Bug] Compaction ignores 'auto: false' config and OPENCODE_DISABLE_AUTOCOMPACT env vars" (v1.17.7, 2026-06-14). Fix attempts: PR #17936 (closed unmerged), PR #30749, PR #32864 (2026-06-18); a comment notes the issue persisted on latest dev even after refactor #33404. Treat "fully off" as unreliable until verified on the pinned version. https://github.com/anomalyco/opencode/issues/32385

### Q-B4: Plugin hook `experimental.session.compacting`

**Verdict**: Real, implemented in core (`session/compaction.ts`), fires **before** summary generation. A plugin may BOTH append to `output.context: string[]` AND wholesale replace `output.prompt` (prompt wins if set). Status: experimental prefix = explicitly unstable API.

Evidence (primary source, `packages/opencode/src/session/compaction.ts`, present on sst/opencode@dev, anomalyco/opencode@dev, and historical commits e.g. 47f33329, 57ce1b9c):
```ts
// Allow plugins to inject context or replace compaction prompt.
const compacting = yield* plugin.trigger(
  "experimental.session.compacting",
  { sessionID: input.sessionID },
  { context: [], prompt: undefined },
)
const nextPrompt = compacting.prompt ?? buildPrompt({ previousSummary, context: compacting.context })
```
https://github.com/sst/opencode/blob/dev/packages/opencode/src/session/compaction.ts (accessed 2026-08-21)

- Exact payload shape: input `{ sessionID: string }`; output `{ context: string[]; prompt?: string }`. If `output.prompt` is set it **replaces** the entire built compaction prompt (anchor + SUMMARY_TEMPLATE + context are discarded); otherwise pushed `context` strings are appended after the template. https://github.com/sst/opencode/blob/dev/packages/opencode/src/session/compaction.ts
- Firing timing: inside `processCompaction`, immediately before message selection is serialized and the summary request is dispatched to the "compaction" agent — i.e., pre-summary-generation, once per compaction run (manual `/compact` or auto). Same source as above.
- Stability/history: introduced via community PR tracked in issue #5698 ("feat(plugin): add experimental.session.compacting hook"); original proposal was append-only `{ context: string[] }`; maintainer note: "Talked w/ Dax we will merge but mark as [experimental]" precisely because prompt-replacement use cases were anticipated but unproven. https://github.com/sst/opencode/issues/5698 (accessed 2026-08-21)
- Documented in third-party API references as an Experimental Hook: Symposium table lists `experimental.session.compacting` — "Push to `output.context` or replace `output.prompt` during compaction". https://symposium.dev/design/agent-details/opencode.html (secondary, accessed 2026-08-21)
- Related sibling hook in same file: `experimental.compaction.autocontinue` (output `{ enabled: boolean }`) gates the automatic post-compaction "continue" prompt. Same source as above.
- Real-world consumer example replacing `output.prompt`: Agentuity plugin `onCompacting` sets `output.prompt = fullPrompt`. https://cdn.jsdelivr.net/npm/@agentuity/opencode@3.1.18/src/plugin/hooks/session-memory.ts (secondary, accessed 2026-08-21)

**Not found**: an official opencode.ai/docs/plugins page section documenting this hook's payload (the official plugins doc does not enumerate every experimental hook as of access date) — payload shape above is taken from core source, which is authoritative.

### Q-B5: Skills system frontmatter & loading semantics

**Verdict**: v1.x recognizes ONLY `{name, description, license, compatibility, metadata}` in SKILL.md frontmatter. **No `auto_load`/`always_load` key exists** — skills are advertised (name+description only) and loaded strictly on-demand via the native `skill` tool. Per-agent skill filtering EXISTS via `permission.skill` pattern rules in agent frontmatter.

Evidence:
- Official docs (primary): "Only these fields are recognized: `name` (required), `description` (required), `license` (optional), `compatibility` (optional), `metadata` (optional, string-to-string map)". Loading model: "Skills are loaded on-demand via the native `skill` tool — agents see available skills and can load the full content when needed." Discovery locations: `.opencode/skills/*/SKILL.md`, `~/.config/opencode/skills/*/SKILL.md`, plus Claude-compatible `.claude/skills/` and agent-compatible `.agents/skills/` (project walks up to git worktree). https://opencode.ai/docs/skills/ (accessed 2026-08-21)
- Injection mechanics (docs): available skills listed inside the `skill` tool description as `<available_skills><skill><name>…</name><description>…</description></skill>…`; full body enters context only after `skill({ name: "…" })`. Same URL.
- Per-agent filtering (docs): global `{"permission": {"skill": {"internal-*": "deny", …}}}` in opencode.json; per-agent override in agent frontmatter `permission: {skill: {…}}`; behavior table: `allow` = loads immediately, `deny` = hidden from agent + rejected, `ask` = prompt on load. Same URL.
- Source confirmation (primary): `packages/opencode/src/skill/index.ts` — parser accepts only `{name, description}` via zod safeParse (`z.object({ name: z.string(), description: z.string() }).safeParse(md.data)`); discovery scans `.claude`, `.agents` externals + `.opencode/{skill,skills}` + config `skills.paths`/`skills.urls`; `Skill.available(agent)` filters with `Permission.evaluate("skill", skill.name, agent.permission).action !== "deny"`. https://github.com/anomalyco/opencode/blob/51e310c9/packages/opencode/src/skill/index.ts (accessed 2026-08-21)
- V2 delta (secondary product line, primary docs at https://opencode.ai/v2/docs/skills): V2 adds `slash` (hide from interactive command catalogs) and `metadata.opencode/autoinvoke: false` (omit from model-facing discovery) — the closest existing keys to an "auto_load" concept, but both are **discovery opt-outs**, not pre-injection loaders. V2 does not enforce the Agent-Skills name regex or folder-name match. (accessed 2026-08-21)
- Note: a built-in `customize-opencode` skill ships in-binary and is registered before disk scan so user skills of the same name override it. https://github.com/anomalyco/opencode/blob/2a33addd/packages/opencode/src/skill/index.ts (accessed 2026-08-21)

**Conclusion for omega-engine**: any `auto_load:`/`always_load:` frontmatter keys in our SKILL.md files are inert upstream metadata (ignored by the zod parse); the supported lever for forcing/limiting skill availability per agent is `permission.skill` patterns in agent frontmatter/opencode.json.

### Q-B6: Agent config key `toolProfile`

**Verdict**: Does NOT exist upstream in any opencode version checked. It is purely a forward-looking/stub name. The official per-agent tool-control keys are `tools` (boolean map, marked `@deprecated` in favor of `permission`) and `permission`.

Evidence:
- Official JSON schema (primary, live-fetched 2026-08-21): `AgentConfig` properties = `model, variant, temperature, top_p, prompt, tools (@deprecated Use 'permission' field instead), disable, description, mode (subagent|primary|all), hidden, options, color, steps, maxSteps (@deprecated Use 'steps'), permission`. No `toolProfile` / `tool_profile` anywhere in the schema. https://opencode.ai/config.json
- Note: `AgentConfig` does not set `additionalProperties: false`, so an unknown `toolProfile` key will neither validate-fail nor do anything — silently inert.
- The `toolProfile` concept exists only in third-party wrappers/orchestrators, each with their own semantics: Crewship (`tool_profile` FULL|CODING|MINIMAL in its own Go orchestrator, explicitly noting for the OpenCode adapter "Profile-based built-in curation not yet wired"), claw-pilot (`toolProfile` written to its own runtime.json), aiden (`core/v4/toolProfiles.ts`). https://docs.crewship.ai/guides/cli-adapters , https://github.com/swoelffel/claw-pilot/blob/main/src/core/agent-provisioner.ts , https://github.com/taracodlabs/aiden/blob/main/core/v4/toolProfiles.ts (all secondary, accessed 2026-08-21)

### Q-B7: AGENTS.md discovery & `instructions: []` injection (current)

**Verdict**: BOTH mechanisms inject content into model context in current versions; they are additive, not alternatives. AGENTS.md is the guaranteed automatic-discovery path; `instructions` in opencode.json adds extra files/globs/URLs, combined WITH AGENTS.md.

Evidence (official Rules doc, primary, footer "Last updated: Aug 20, 2026"): https://opencode.ai/docs/rules/
- Discovery order at startup: (1) local files traversing UP from cwd (`AGENTS.md`, then `CLAUDE.md` fallback), (2) global `~/.config/opencode/AGENTS.md`, (3) Claude Code fallback `~/.claude/CLAUDE.md` unless disabled via `OPENCODE_DISABLE_CLAUDE_CODE*`. First match wins per category (AGENTS.md beats CLAUDE.md in same dir).
- Custom Instructions section: `instructions` accepts file paths, glob patterns (e.g. `packages/*/AGENTS.md`), and remote URLs (5s fetch timeout); explicit statement: "**All instruction files are combined with your `AGENTS.md` files.**"
- Schema confirmation (primary): `"instructions": {"type": "array", "items": {"type": "string"}, "description": "Additional instruction files or patterns to include"}` in https://opencode.ai/config.json (accessed 2026-08-21). Config loader concatenates `instructions` arrays across global/project config files with dedup (`mergeConfigConcatArrays`, packages/opencode/src/config/config.ts).
- Practical implication for omega-engine: relying on `instructions: []` alone works, but AGENTS.md remains the zero-config guaranteed injection; `instructions` cannot *replace* AGENTS.md content, only augment it.

### Q-B1: Qwen3-4B true context window

**Verdict**: The internal review prose "Qwen3-4B (8K–16K)" is **wrong** for both variants. Official native trained context: **Qwen3-4B (Apr 2025) = 32,768 tokens** (YaRN-validated to **131,072**, factor 4.0); **Qwen3-4B-Thinking-2507 = 262,144 tokens NATIVE** (no YaRN needed). The live `context_length: 8192` cap is a RAM/KV-budget choice, not a model limitation.

Evidence (primary — official model cards):
- Qwen3-4B card, Model Overview: "Context Length: 32,768 natively and 131,072 tokens with YaRN." https://huggingface.co/Qwen/Qwen3-4B (accessed 2026-08-21; model released Apr 2025)
- Same card, Processing Long Texts: YaRN config `{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768}` validated to 131,072; llama.cpp usage `llama-server ... --rope-scaling yarn --rope-scale 4 --yarn-orig-ctx 32768`. **Caveats (verbatim)**: all OSS frameworks implement *static* YaRN — "scaling factor remains constant regardless of input length, **potentially impacting performance on shorter texts**"; add rope_scaling only when long contexts are required; tune factor to expected length (e.g. factor 2.0 for ~65,536); "If the average context length does not exceed 32,768 tokens, we do not recommend enabling YaRN… as it may potentially degrade model performance." Also: `max_position_embeddings` in config.json = **40,960** (32,768 output reserve + 8,192 typical prompts) — this is the number baked into the original GGUF metadata.
- Qwen3-4B-Thinking-2507 card: "Context Length: **262,144 natively**"; "Enhanced 256K long-context understanding"; thinking-only model. Deployment examples pass `--context-length 262144` / `--max-model-len 262144`, with the note: "If you encounter out-of-memory (OOM) issues, you may consider reducing the context length to a smaller value. However, since the model may require longer token sequences for reasoning, **we strongly recommend using a context length greater than 131,072 when possible**." Recommended output length 32,768 (up to 81,920 for hard benchmarks). https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507 (accessed 2026-08-21; released Jul 2025)

Runtime defaults for Qwen3-4B GGUF:
- **llama.cpp** (primary source): `common.h` master → `int32_t n_ctx = 0; // context size, 0 == context the model was trained with`; CLI/server README: `-c, --ctx-size N (default: 0, 0 = loaded from model)`; `llama-context.cpp`: `cparams.n_ctx = params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx`, warns "possible training context overflow" above `n_ctx_train`. Memory auto-fit can shrink ctx (`fit_params_min_ctx = 4096`). https://github.com/ggml-org/llama.cpp/blob/master/common/common.h , https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md (accessed 2026-08-21). Net effect: modern llama.cpp defaults to the GGUF's trained context — 40,960 for original Qwen3-4B GGUF, 262,144 for Thinking-2507 GGUF (subject to VRAM fit).
- **Ollama** (primary): default `num_ctx` was 2048; raised to **4096** in Apr 2025 (PR #10364 merged 2025-04-21, lowering numParallel 4→2; docs updated in PR #11189). Ollama does NOT honor GGUF trained context by default. https://github.com/ollama/ollama/pull/10364 , https://github.com/ollama/ollama/pull/11189
- **LM Studio** (primary docs + changelog): context length is a per-load parameter (`lms load --context-length N`) with per-model defaults (My Models → gear) and, since v0.3.24 (Aug 2025), a global "default context length for all models" App Setting. **No single universal default number is officially published**; docs/examples show 4096, and field reports show loads at other values (e.g. 2048 for an MLX glm4, 32768 in one bug report) depending on saved per-model config (`llm.load.contextLength`). Verdict: treat LM Studio as "unset until proven otherwise" — do not assume trained context. https://lmstudio.ai/docs/cli/local-models/load , https://lmstudio.ai/changelog/lmstudio-v0.3.24 , https://lmstudio.ai/docs/app/advanced/per-model ; secondary: https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/546 , https://github.com/lmstudio-ai/mlx-engine/issues/152 (accessed 2026-08-21)

Defensibility verdict for `qwen3-4b-thinking` on llama.cpp-class runtimes:
1. **8,192 (current cap)** — safe, zero quality risk, but wasteful of the model's actual capability; for a *thinking* model it can truncate reasoning chains on complex tasks (Qwen recommends ≥131,072 when feasible for the 2507 variant).
2. **32,768** — the original Qwen3-4B's native window; zero-scaling quality floor. Reasonable mid-point.
3. **65,536–131,072** — original variant needs YaRN factor 2.0–4.0 (static scaling; mild short-context degradation per Qwen). Thinking-2507 needs NO scaling in this range (native).
4. **Up to 262,144** — Thinking-2507 native max; KV-cache cost dominates (researcher-derived estimate, not cited: 36 layers × 8 KV heads × 128 head_dim × 2 (K,V) × 2 bytes ≈ ~144 KB/token fp16 → ~4.5 GB at 32K, ~18 GB at 131K, ~36 GB at 256K before quantized-KV savings).
5. Beyond native (original variant, >131K) — not validated by Qwen; not defensible.
**Bottom line**: raise the cap from 8192 toward 32,768+ as RAM allows; the "8K–16K" prose should be corrected to "32K native (128K YaRN)" for base Qwen3-4B or "256K native" for the 2507 Thinking refresh — confirm which checkpoint our GGUF was built from.

### Q-B2: opencode compaction config semantics (v1.18.x era)

**Verdict**: v1.x honors `{auto, prune, tail_turns, preserve_recent_tokens, reserved}` (the "legacy" family — confirmed in the LIVE official JSON schema today). `{buffer, keep.tokens}` is the **V2-only** family (separate product line, own docs). If both families are set, the running major version simply ignores the other family's keys (V1 code never reads them; V2 docs call V1 settings "migration context"). Note: the V1 `compaction` schema object sets `additionalProperties: false`, so cross-family keys may trip strict validation rather than silently pass.

Key-by-key (V1, current stable docs + live schema, both accessed 2026-08-21):
- `auto` (bool, default true) — preflight auto-compaction when context nears full. https://opencode.ai/docs/config/ , https://opencode.ai/config.json
- `prune` (bool, default false) — prune old tool outputs. Same sources.
- `reserved` (int) — token buffer; see formula below. Introduced by PR #12924 ("add compaction.reserved (configurable token buffer…) … adjust isOverflow … within 20k instead of within 32k"). https://github.com/anomalyco/opencode/pull/12924
- `tail_turns` (int) + `preserve_recent_tokens` (int) — keep recent turns verbatim. Added as `tail_turns`/`tail_tokens` by PR #21822 (2026-04-10); `tail_tokens` renamed to **`preserve_recent_tokens`** in release **v1.14.19** (commit "tweak: rename tail_tokens -> preserve_recent_tokens (#23491)"). https://github.com/anomalyco/opencode/pull/21822 , https://github.com/anomalyco/opencode/releases/tag/v1.14.19
- Docs page currently highlights only `{auto, prune, reserved}`; `tail_turns`/`preserve_recent_tokens` appear in the schema but not yet in the docs prose — schema is authoritative.

V2 family (https://opencode.ai/v2/docs/compaction, accessed 2026-08-21): `auto` (same meaning; does NOT disable manual `/compact` or one-shot overflow recovery), `keep.tokens` (default 15000 — newest serialized context retained beside summary), `buffer` (default 20000 — safety reserve). Explicit statement: "**V1 used additional tail-turn and pruning behavior. Those V1 details are only migration context.**"

Exact trigger formulas:
- **V1** (primary source, `packages/opencode/src/session/overflow.ts`, sst/opencode@dev, accessed 2026-08-21):
```ts
const COMPACTION_BUFFER = 20_000
usable = model.limit.input
  ? max(0, limit.input − reserved)                       // reserved = cfg.compaction.reserved ?? min(20_000, maxOutputTokens(model))
  : max(0, limit.context − maxOutputTokens(model))
isOverflow = !(cfg.compaction.auto === false)
          && model.limit.context !== 0
          && totalTokens >= usable                        // totalTokens = tokens.total || input+output+cache.read+cache.write
```
i.e. compact when measured total tokens ≥ usable; `auto:false` short-circuits the preflight check entirely.
- **V2** (docs): `estimated tokens > context limit − max(requested output tokens, buffer)`, where the estimate JSON-serializes the request assuming 4 chars/token; plus one-shot provider-overflow compact-and-retry even when `auto:false` (documented V2 behavior).

Known reliability caveats (both families): provider-overflow recovery path historically bypassed `auto:false`/env-var disables (#16882 → #30664 → #32385, seen through v1.17.7; fix attempts #17936 unmerged, #30749, #32864). See Q-B3.

---

## Source Register
*Compiled by N7 session from the inline citations above (researcher's register append was cut; all URLs already cited inline with access date 2026-08-21).*

| # | Title / Location | Type | Supports |
|---|------------------|------|----------|
| 1 | `packages/opencode/src/flag/flag.ts` (sst/opencode@dev) | Primary (source) | Q-B3 |
| 2 | https://opencode.ai/docs/cli/ (env-var table) | Primary (docs) | Q-B3 |
| 3 | `packages/opencode/src/config/config.ts` (dev) | Primary (source) | Q-B3, Q-B7 |
| 4 | anomalyco/opencode issue #3325 | Primary (maintainer) | Q-B3 |
| 5 | anomalyco/opencode issues #16882, #30664, #32385; PRs #17936, #30749, #32864 | Primary (bug trail) | Q-B3, Q-B2 caveat |
| 6 | `packages/opencode/src/session/compaction.ts` (dev) | Primary (source) | Q-B4 |
| 7 | sst/opencode issue #5698 (hook origin) | Primary | Q-B4 |
| 8 | symposium.dev opencode API reference | Secondary | Q-B4 |
| 9 | @agentuity/opencode session-memory.ts | Secondary (consumer example) | Q-B4 |
| 10 | https://opencode.ai/docs/skills/ | Primary (docs) | Q-B5 |
| 11 | `packages/opencode/src/skill/index.ts` @51e310c9 | Primary (source) | Q-B5 |
| 12 | https://opencode.ai/v2/docs/skills | Primary (V2 docs) | Q-B5 |
| 13 | https://opencode.ai/config.json (live schema) | Primary (schema) | Q-B5, Q-B6, Q-B7, Q-B2 |
| 14 | Crewship / claw-pilot / aiden repos+docs | Secondary | Q-B6 (toolProfile elsewhere) |
| 15 | https://opencode.ai/docs/rules/ (updated Aug 20 2026) | Primary (docs) | Q-B7 |
| 16 | https://huggingface.co/Qwen/Qwen3-4B (model card) | Primary | Q-B1 |
| 17 | https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507 (model card) | Primary | Q-B1 |
| 18 | llama.cpp `common/common.h` + `tools/server/README.md` | Primary (source/docs) | Q-B1 |
| 19 | Ollama PRs #10364, #11189 | Primary | Q-B1 |
| 20 | LM Studio docs (load, per-model) + changelog v0.3.24 | Primary (docs) | Q-B1 |
| 21 | `packages/opencode/src/session/overflow.ts` (dev) | Primary (source) | Q-B2 formula |
| 22 | PRs #12924, #21822; release v1.14.19 | Primary | Q-B2 key history |
| 23 | https://opencode.ai/v2/docs/compaction | Primary (V2 docs) | Q-B2 |

**Reconciliation note (N7)**: Q-B2 (web: v1.x honors V1 family only; `{buffer, keep.tokens}` = V2 product line) vs Deep Dig II DD-II-2 (local binary strings contain BOTH families; decompiled trigger math consumes `buffer`(20k)/`keep.tokens`(8k)). The 8k value matches neither V2 doc default (15k) nor our live reserved (10000) — resolve by pinning WHICH binary/version this machine runs (`opencode --version` vs git SHA) before trusting any spec target block. Logged as hazard D3 in `N7_DOMAIN_INDEX.md`.

---

## Deep Dive: Model Config Semantics

*Appended 2026-08-21 by @researcher for N7 Phase 1 spec review (pinned binary: opencode 1.18.19). Sources: official docs (updated Aug 20, 2026), live config.json schema, and source on sst/opencode@dev (fetched 2026-08-21). Dev branch moves fast; where behavior is version-sensitive this is flagged. All findings apply to the 1.x line unless noted.*

### DD-1: Does `agent.<name>.model` PIN or DEFAULT?

**Verdict**: It is a **hard pin against TUI interactive switching** (`/models` selections get reverted to the agent's configured model) but a **soft default against explicit programmatic invocation** (`opencode run --model X --agent Y` wins). Docs call it an "override"; the accurate mental model is "per-agent floor".

Exact precedence (primary source, `packages/opencode/src/session/prompt.ts` → `createUserMessage`, sst/opencode@dev, accessed 2026-08-21):
```ts
const model = input.model ?? ag.model ?? (yield* currentModel(input.sessionID))
```
and `currentModel(sessionID)` resolves: (1) model stored on the session row (`SessionTable.model`, written by `setAgentModel` after every message), (2) first user message in session carrying a model, (3) `provider.defaultModel()` — which itself follows the documented startup order: `--model/-m` flag → config `model` key → last-used model → first model by internal priority (https://opencode.ai/docs/models/, "Loading models", updated Aug 20 2026).

So the full chain: **explicit per-call model (CLI `-m/--model`, SDK `input.model`) > agent.config.model > session-stored model > global config.model / last-used > provider internal default**. Same chain in `shellImpl` (`input.model ?? agent.model ?? currentModel`). https://github.com/sst/opencode/blob/dev/packages/opencode/src/session/prompt.ts

TUI reality (issue tracker, primary):
- Maintainer (issue #1661): "the model selection is tied to agent so when you switch agents it will switch to last used model for that agent (**if the agent doesn't have specified one**)". https://github.com/anomalyco/opencode/issues/1661 (2025-08-07)
- Issue #13456 "[Bug] TUI model selection gets overwritten by agent default model": a TUI `createEffect` re-enforces `value.model` whenever agent state refreshes, reverting manual `/models` picks for agents that define `model`; per-agent manual selections were also not persisted in `modelStore.save()`. Open as of Feb 2026 (v1.4.x era); referenced fix PR #30290 targets navigation cases. https://github.com/anomalyco/opencode/issues/13456
- Issue #24743 (feature request, 1.4.x): users explicitly ask for "user's explicit runtime choice should take precedence within that session" over agent-pinned models — confirming that is NOT current behavior. https://github.com/anomalyco/opencode/issues/24743
- Related: #3550, #2770 (agent cycling + model display; both trace to missing `provider/` prefix or TUI sync quirks — closed/fixed).

**Answer to the Architect**: setting `agent.researcher.model = "lmstudio/qwen3-4b-thinking"` does NOT lock out `opencode run -m google/gemini-3-pro --agent researcher` (flag wins). But inside the TUI, `/models` switches will snap back to the pinned model for that agent. If he wants `/models` freedom, do NOT pin `agent.model`; rely on inheritance instead (see DD-3 recommendation).

### DD-2: Exact semantics of `variant`

**Verdict**: `variant` selects a **named configuration preset for the same model** (reasoning-effort / thinking-budget class options) — NOT a different checkpoint. It is a *conditional default*: applies only when the resolved model IS the agent's own configured model AND the model actually declares that variant; otherwise silently dropped (no error).

Evidence:
- Schema (primary, live): `AgentConfig.variant`: "Default model variant for this agent (**applies only when using the agent's configured model**)." https://opencode.ai/config.json (accessed 2026-08-21)
- Resolution logic (primary source, `session/prompt.ts` @dev):
```ts
const same = ag.model && model.providerID === ag.model.providerID && model.modelID === ag.model.modelID
const variant = input.variant ?? (ag.variant && full?.variants?.[ag.variant] ? ag.variant : undefined)
```
Two consequences: (a) if the user overrides the model at runtime, `ag.variant` does NOT apply (the `same` guard fails); (b) if the model has no variants map containing that name, variant resolves `undefined` — request proceeds without it, silently. https://github.com/sst/opencode/blob/dev/packages/opencode/src/session/prompt.ts
- What variants ARE (official docs, updated Aug 20 2026): per-provider built-in presets — Anthropic `high`/`max` (thinking budget), OpenAI `none|minimal|low|medium|high|xhigh` (reasoning effort), Google `low`/`high`; "many other providers have built-in defaults too". Custom variants: `provider.<id>.models.<model>.variants.<name>` = arbitrary option overrides; `"disabled": true` retires one. https://opencode.ai/docs/models/ §Variants
- Which providers consume it: any model whose models.dev/provider metadata declares `variants` (registry-checked at runtime via `full?.variants?.[name]`). **Nemotron `high/medium/low` specifics were NOT confirmable from fetched primary docs** ("many others" is undocumented); verify empirically with `opencode models --verbose` against the pinned 1.18.19 binary before spec'ing nemotron variants.
- Invocation-time alternatives: `opencode run --variant <name>` CLI flag ("Model variant (provider-specific reasoning effort)") — https://opencode.ai/docs/cli/ ; `variant_cycle` keybind in TUI — https://opencode.ai/docs/keybinds (referenced from Models doc); per-command `variant` field in CommandConfig — schema; SDK/plugin `input.variant` — prompt.ts. **No env var for variant exists** in the documented env table.
- Note: `variant` is distinct from the deprecated per-agent pass-through options pattern (`reasoningEffort: "high"` directly on AgentConfig passes raw provider options — Agents doc §Additional); variant is the *named, reusable* layer over the same mechanism.

### DD-3: Flexible management patterns (local-first default WITHOUT hard-binding)

**Verdict**: The supported combination is **global `model` key (or agent inheritance) + per-invocation `-m` flag**. There is no env var for model choice, no agent-level fallback chains, and `/models` persistence is per-agent "last used" — which pinned agent models override.

Sub-findings (all accessed 2026-08-21):

1. **Per-invocation flags** (primary, CLI doc): `opencode run [-m|--model provider/model] [--agent name] [--variant name]`; TUI accepts the same `-m`/`--agent` at launch. Flag beats everything (DD-1 chain). https://opencode.ai/docs/cli/
2. **Env vars**: the complete documented env table contains **NO model-selection variable** (no `OPENCODE_MODEL`). Env-based levers are indirect: `OPENCODE_CONFIG` (alt config path), `OPENCODE_CONFIG_DIR`, `OPENCODE_CONFIG_CONTENT` (inline JSON — can carry `"model"`). https://opencode.ai/docs/cli/ §Environment variables
3. **Config layering** (primary, config loader source + docs): merge order ≈ global `~/.config/opencode/{config,opencode}.jsonc` → `OPENCODE_CONFIG` file → project `.opencode/opencode.json(c)` walked up to worktree → `OPENCODE_CONFIG_CONTENT` → console/org remote → MDM managed prefs (last). Deep merge: later sources win scalars; arrays concatenate + dedupe (`mergeConfigConcatArrays`). `default_agent` picks the startup primary agent. Practical profile-switching = swap which file `OPENCODE_CONFIG` points at (third-party tools like `raise` automate symlink-swapping the whole config dir). https://github.com/sst/opencode/blob/dev/packages/opencode/src/config/config.ts ; https://opencode.ai/docs/config/
4. **Fallback chains**: **none exist** at agent or config level — the schema has no fallback/retry-models key anywhere (verified full-schema read), and no cross-provider failover is documented. What exists: capped automatic retries with jitter (changelog, https://opencode.ai/changelog), `small_model` for background tasks like title generation with `retries: 2` (prompt.ts), and the compaction overflow-retry path (Q-B2). Provider failure = surfaced error; failover is the CALLER's job → omega fabric must own fallback, exactly as Architect assumed.
5. **`/models` persistence**: selection is stored per-agent as "last used" and seeds startup priority #3 (Models doc); it survives restarts UNLESS an agent pins `model` (then the pin re-applies — #13456/#1661). Switching agents shows each agent's own last-used model.

**Recommendation (target outcome: "defaults to local qwen3-4b-thinking; Architect overrides per-invocation without editing config")**:
- Set top-level `"model": "lmstudio/qwen3-4b-thinking"` in the PROJECT opencode.json (layered under global if desired). Do **not** set `agent.<name>.model` for the 6 agents — primary agents inherit the global default; subagents inherit their invoker's model (Agents doc §Model tip). Optionally pin `model` only on hidden system agents (title/summary/compaction) where hard-binding a cheap local model is genuinely wanted.
- Architect's overrides then work everywhere: TUI `/models` (nothing reverts it, since no agent pin), `opencode run -m … --agent …`, or launch-time `-m`.
- If a per-agent default is still desired for ONE agent, accept the tradeoff: CLI `-m` still wins, but TUI `/models` becomes non-durable for that agent (#13456).
- Keep `variant` off the spec unless the target model declares variants (`opencode models --verbose` on 1.18.19); a stale variant value is silently inert, so it's safe-but-useless if unsupported.

*Deep-Dive source addendum*: prompt.ts + agent.ts + config.ts (sst/opencode@dev, 2026-08-21) · opencode.ai/docs/{models,agents,cli,config}/ (Aug 20 2026) · opencode.ai/config.json (live) · issues #1661, #2770, #3015, #3550, #13456, #24743 · changelog. All primary except issue threads (primary-first-party but anecdotal).

---

## Deep Dive: Onboarding & Knowledge Curation Patterns

*Appended 2026-08-21 by @researcher. Grounding pass for the N7 NODE ONBOARDING PROTOCOL (repeatable "subagent-mined KB + node-expert annotation" across 10 domain sessions). All URLs accessed 2026-08-21.*

### OD-1: Technical onboarding runbooks/apprenticeship patterns

**Core finding**: mature orgs converge on *graduated apprenticeship around canonical artifacts* — the novice does real work under expert review against a written canon, and graduates when their output stops needing correction.

Evidence:
- **Software Engineering at Google, Ch.3 "Knowledge"** (primary, free HTML edition): knowledge-distribution mechanisms "range from the utterly simple (**ask questions; write down what you know**) to the much more structured, such as tutorials and classes"; requires psychological safety to admit knowledge gaps. Key scaling pattern: "a human expert already familiar with a guideline can **send a link** to a fellow engineer… The expert saves time by not needing to personally explain… and the learner now knows there is a **canonical source of trustworthy information**." The **readability program**: standardized mentorship through code review — centralized volunteer reviewers (~1–2% of engineers) coach authors until they "graduate"; explicitly "a mentoring and cooperative process, not a gatekeeping or adversarial one". https://abseil.io/resources/swe-book/html/ch03.html (book pub. 2020)
- **Same book, Ch.10 "Documentation"** (primary): treat docs like code inside the engineering workflow; `go/` links make documents canonical; **identify the primary audience before writing**; open docs with TL;DR gates for "stumblers"; design doc required before major work; "**freshness dates**… note the last time a document was reviewed, and metadata… will send email reminders when the document hasn't been touched in, for example, **three months**"; track docs as bugs. https://abseil.io/resources/swe-book/html/ch10.html
- **SRE on-call/runbook discipline** (primary: Google SRE Workbook ch.8–9, https://sre.google/workbook/oncall/ , https://sre.google/workbook/incident-response/ ; craft synthesis secondary: Raccoon Page, 2026-05-11, https://raccoon.page/blog/how-to-write-a-runbook/ ): one short ordered procedure per recurring situation — symptom → checks → steps-in-order → verification → rollback → escalation; 200–600 words; **linked directly from the alert**; indexed in a single register; "**reviewed when it's used and culled when nobody's used it in a quarter**". The SRE Workbook's "five As" of a good runbook: Actionable, Accessible, Accurate, Authoritative, Adaptable (secondary restatement: https://www.prskavec.net/courses/how-to-make-oncall/chapter10a/ , 2024-04-17).

**Mapping to our pipeline** (`read charter → directed mining → annotate → consultable`):
| Our phase | Literature pattern |
|---|---|
| read charter | audience-first writing + TL;DR gate (Ch.10); canonical-link culture (Ch.3) |
| directed mining | readability-style apprenticeship: subagent output reviewed against canon until it "graduates" |
| annotate | "write down what you know" at proficiency-time (Ch.3) — annotation is part of doing, not an afterthought |
| consultable | canonical stable address (go/-link analog) + alert-linked runbook + single index register |

### OD-2: Knowledge base curation best practices

**Core finding**: KB rot is prevented by giving every artifact exactly ONE job, making decisions immutable-but-superseded, and attaching time/usage-based review triggers — three independent literatures agree.

Evidence:
- **Diátaxis** (primary, https://diataxis.fr/start-here/ , https://diataxis.fr/tutorials-how-to/ ): four documentation forms mapped on two axes (acquisition↔application, study↔work): **tutorials** (learning-oriented, managed safe path, teacher's responsibility), **how-to guides** (task-oriented, forking real-world paths, user's responsibility), **reference** (dry, accurate, complete facts), **explanation** (the *why*, discursive). "The single most common conflation… is that between the tutorial and the how-to guide." Each form has distinct obligations; mixing jobs in one artifact is the root failure mode.
- **Zettelkasten atomicity** (primary, https://zettelkasten.de/atomicity/guide/ and https://zettelkasten.de/posts/principle-of-atomicity-difference-between-principle-and-implementation/ , 2025-08-12): one knowledge building block per note; crucially, **atomicity is a desired OUTCOME, not an input gate** — notes enter non-atomic and are atomized through work ("atomicity was achieved in your Zettelkasten, not outside of it"); unique identifiers give each note both separateness and the possibility of connection; atomization "fosters re-use which in turn multiplies the amount of connections"; structure notes serve as entry points/map views.
- **ADRs** (primary: Michael Nygard, 2011-11-15, https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions ; hub: https://adr.github.io/ ; synthesis: Martin Fowler, https://martinfowler.com/bliki/ArchitectureDecisionRecord.html ): short numbered monotonic files in-repo (`doc/arch/adr-NNN-*.md`) with context / decision / consequences / status; **never modified once accepted — superseded with a link** ("It's still relevant to know that it was the decision, but is no longer the decision"); "the consequences of one ADR are very likely to become the context for subsequent ADRs"; Fowler adds recording confidence level and explicit re-evaluation triggers.
- **Genre distinctions**: runbook = one procedure for one recurring symptom, fires from an alert; playbook = response shape for a class of incident (raccoon.page, above). FAQ is not a Diátaxis category — its items decompose into how-to/reference entries. Decision records ≠ explanation: rationale logs are append-only.
- **Freshness conventions**: Google's freshness-date metadata + 3-month review reminders (Ch.10, above); quarterly usage-based culling for runbooks (raccoon.page); ADR status lifecycle (proposed/accepted/superseded).

**What prevents KB rot (ranked)**: (1) single-job typing of every artifact (Diátaxis); (2) immutability + supersession for decisions (ADR); (3) scheduled review dates wired to notifications (Google); (4) usage-based culling (SRE); (5) atomicity-as-outcome so units stay linkable/reusable (Zettelkasten).

### OD-3: Context-loading literature for AI agents

**Core finding**: 2025–2026 practice has converged on **map-first, drill-on-demand** — front-load only a small curated index into context; keep the corpus behind stable addresses the agent fetches just-in-time; persist distillates externally so nothing is ever re-researched.

Evidence:
- **Anthropic, "Effective context engineering for AI agents"** (primary, 2025-09-29, https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents ): shift from embedding pre-retrieval to "**just in time**" strategies — "agents maintain **lightweight identifiers** (file paths, stored queries, web links) and use these references to dynamically load data into context at runtime using tools." Autonomous navigation enables "**progressive disclosure**… agents incrementally discover relevant context through exploration… assemble understanding layer by layer." Explicit **hybrid model**: "CLAUDE.md files are naively dropped into context up front, while primitives like glob and grep allow it to navigate its environment and retrieve files just-in-time." Long-horizon levers: compaction, structured note-taking (NOTES.md / memory tool — "agents build up knowledge bases over time"), and sub-agent architectures where deep explorers "return only a condensed, distilled summary (often 1,000–2,000 tokens)". Guiding principle: "find the smallest set of high-signal tokens."
- **Claude Cookbook, "Context engineering: memory, compaction, and tool clearing"** (primary, 2026-03-20, https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools ): decomposes the three primitives by scope — compaction = whole-transcript distillation; tool-result clearing = surgical drop of re-fetchable payloads; memory = cross-session external storage ("Session 2 picks up where Session 1 left off"); includes a workload→primitive mapping framework.
- **llms.txt spec v2** (primary, Jeremy Howard / Answer.AI, 2024-09-03, https://llmstxt.org/ ): a curated markdown overview at site root that "stays small enough to fit in context. **The detail lives behind the links, and is fetched only when needed**"; fixed shape = H1 name + blockquote summary + free detail + H2 file-lists of annotated links; an "Optional" section holds what "an agent can skip when a shorter context is needed"; authoring guidance includes testing by "asking an agent questions about your content, giving it only your llms.txt as a starting point."

**Consensus mechanics for our protocol**: (a) the *only* thing front-loaded is the map (charter/index ≈ llms.txt ≈ CLAUDE.md slot); (b) corpus entries are individually addressable and self-describing so JIT fetch beats stale indexing; (c) mined knowledge is written back as external distillates (memory-tool pattern), making consultation O(lookup), never re-research.

### Patterns worth embedding (keyed to pipeline phases G/M/A/D/W/C/X/E)

1. **(G/M) Charter-as-map**: give each node KB an llms.txt-shaped index — H1 + blockquote charter + annotated H2 link-lists with an Optional tier. Front-load ONLY this map; it directs mining targets and keeps session context small (llmstxt.org; Anthropic hybrid).
2. **(M/A) Apprenticeship graduation gate**: treat subagent mining output like Google readability CLs — node-expert annotation IS the review loop; artifacts promote from raw-mine → annotated → canonical only after expert pass, with rationale citations attached (SWE Book Ch.3).
3. **(A/D) Atomicity as outcome, not gate**: accept non-atomic mine dumps; during distillation split to one-knowledge-building-block notes with unique IDs + structure-note entry points, because atomic units are what make cross-node linking (X) cheap later (zettelkasten.de).
4. **(W/C) Single-job typing + immutable decisions**: every KB artifact gets exactly one Diátaxis job (tutorial/how-to/reference/explanation) plus runbook-vs-playbook-vs-decision-record genre tags; decisions live as numbered ADRs that are superseded, never edited (diataxis.fr; Nygard).
5. **(C/E) Rot controls + JIT consult contract**: freshness date on every artifact with review reminder (Google's 3-month pattern), quarterly usage-based culling (SRE), status lifecycle metadata; agents consult via map→drill→write-back so the KB improves on every consultation instead of decaying (Anthropic memory/compaction patterns).

---

## Deep Dive: Documenting Novel Signature Systems

*Appended 2026-08-21 by @researcher. Grounding for debut-day docs of the Omega agent-signature format (`⬡ OMEGA ⬡ ENTITY ⬡ [NODE] ⬡ model ⬡ channel ⬡ trace ⬡ phase ⬡ session_id`). All URLs accessed 2026-08-21.*

### SG-1: Prior art for format/spec documentation

**Common doc skeleton extracted across five respected formats**: (1) concept model & motivation → (2) formal grammar or naming rules → (3) field-semantics table with requirement levels → (4) canonical examples → (5) extension/registry/deprecation policy. Every project below implements all five in some form:

- **OpenTelemetry Semantic Conventions** (primary, https://opentelemetry.io/docs/specs/semconv/ , v1.44.0): *Concept*: "common set of semantic attributes which provide meaning to data… easier correlation and consumption." *Naming rules as grammar-substitute*: lowercase, dot-namespaced `{object}.{property}`, printable Basic Latin only, no two attributes share a name, `otel.*` namespace RESERVED ("Any additions… MUST be approved as part of OpenTelemetry specification") — https://opentelemetry.io/docs/specs/semconv/general/naming/ . *Field-semantics table with requirement levels*: Required / Conditionally Required / Recommended / Opt-In, each defined by included-by-default / config-includable behavior (https://opentelemetry.io/docs/specs/semconv/general/attribute-requirement-level/ ). *Extension policy*: attributes "SHOULD NOT be removed… SHOULD be deprecated"; system-specific names must live under the system's root namespace matching its `*.system.name` value.
- **Git commit trailers** (primary, https://git-scm.com/docs/git-interpret-trailers ): *Concept*: "trailer lines that look similar to **RFC 822 e-mail headers**, at the end of the otherwise free-form part of a commit message." *Grammar*: `token: value`, default separator `:` configurable via `trailer.separators`; whitespace rules stated precisely (none inside token, folding allowed like RFC 822); recognition heuristic — a trailing group that is all-trailers OR "contains at least one Git-generated or user-configured trailer and consists of **at least 25% trailers**", preceded by blank lines. *Examples*: `Signed-off-by`, `Acked-by` shown inline. *Extension policy*: user-configured `trailer.<token>.key` aliases; `--trailer` CLI. Note the deliberate choice: **lenient prose heuristics instead of strict ABNF** because trailers coexist with free-form text.
- **Semantic Versioning** (primary, https://semver.org/ ): *Concept* first ("software using Semantic Versioning MUST declare a public API"); numbered normative rules with RFC-2119 keywords; precedence grammar given as a compact BNF-like block near the END of the spec; extensive FAQ; extension policy via build-metadata (`+`) and pre-release identifiers being excluded from precedence.
- **Conventional Commits** (primary, https://www.conventionalcommits.org/ ): leads with **examples before rules** ("Commit message with description and breaking change footer…"); then a normative "Specification" section keyed by RFC-2119 keywords; vocabulary tables (`feat`/`fix`/types); footer conventions (`BREAKING CHANGE:`); explicit scope for tooling ("should be used for tooling" rationale).
- **Structured logging**: *logfmt* (canonical writeup: Brandur Leach, https://brandur.org/logfmt , 2014; implementation home: github.com/go-logfmt/logfmt) documents itself almost entirely by **example pairs** (input line ↔ decoded key-values) plus a name=value convention statement — proof that a tiny format can ship with prose+examples alone. *syslog RFC 5424* (primary, https://www.rfc-editor.org/rfc/rfc5424 , §6 STRUCTURED-DATA): full ABNF for `SD-ELEMENT = "[" SD-ID *(SP SD-PARAM) "]"`, registered-vs-enterprise IDs (`@`-suffixed private namespaces = reserved-extension mechanism), NILVALUE `-` for absence, and an explicit "escapes and escaping" section — the heavyweight end of the spectrum.

**Skeleton verdict**: our signature doc should mirror OTel most closely (namespaced fields + requirement levels + reserved namespaces), borrow Conventional Commits' examples-first ordering, and adopt git-trailer-grade precision about separators/whitespace since our delimiter is `⬡`.

### SG-2: Formal grammar practice

**When ABNF/EBNF/railroads vs prose+examples**:
- **Full ABNF (RFC 5234)** is used when machines must interoperate on a WIRE format: RFC 5424 structured-data; HTTP signatures drafts. `draft-cavage-http-signatures` shows the layered pattern (primary, https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12 ; early draft with explicit ABNF: https://www.ietf.org/archive/id/draft-cavage-http-signatures-01.txt : `params := keyId "," algorithm [", " headers] …`): each parameter then gets a **requirement keyword + semantics paragraph** ("REQUIRED. The `keyId` field is an opaque string… Management of keys… is out of scope"), followed by step-numbered create/verify algorithms and worked RSA/HMAC examples, plus an IANA-style algorithm registry appendix with active/deprecated statuses.
- **Naming-rule tables instead of grammars** when the format is a set of key-value conventions rather than positional syntax: OTel semconv constrains names via character-set + namespace rules and a regex-checked tooling note, never full ABNF.
- **Railroad diagrams** appear where tokens nest visually (SQLite's SQL syntax diagrams, https://www.sqlite.org/lang.html ) — overkill for a single-line signature.
- **Prose heuristics** suffice when the parser is deliberately lenient (git's 25%-trailers rule).
- RFC style context: the RFC Editor's own guidance keeps ABNF for protocol elements while surrounding text carries semantics (see RFC 5424 §6 and the cavage drafts above as in-the-wild demonstrations).

**Minimum viable formality for a v1 community launch** (synthesis): one short normative grammar block (plain EBNF is fine — ~6 productions for `signature := "⬡" marker SP entity SP node SP model SP channel SP trace SP phase SP session_id` shape), RFC-2119 keywords (REQUIRED/OPTIONAL per field), a field table, two-plus canonical examples, and ONE paragraph of extension policy (reserved namespaces + versioning). Anything less invites divergent emitters; anything more slows debut.

### SG-3: LLM-friendly structure per Diátaxis + llms.txt

Our audience is unusual: humans read the signature once; **agents will parse it forever**. Map the SG-1 skeleton onto both frameworks:

| Skeleton element | Diátaxis quadrant | llms.txt placement |
|---|---|---|
| Concept model & motivation ("what is this string?") | **Explanation** (the *why* — provenance philosophy, M22 truth-anchor: log what actually generated a response) | blockquote summary at top |
| "Read your first signature" walkthrough | **Tutorial** (learning-oriented, safe, single path) | first H2 link-list entry |
| Parse/emit recipes per language (regex, formatter) | **How-to guides** (task-oriented, forking by language) | H2 `### How-to` file-list |
| Field-semantics table + grammar + requirement levels | **Reference** (dry, complete, no interpretation — exactly Diátaxis's reference obligation) | H2 `### Reference` → stable `.md` version of the spec page |
| Extension policy, reserved namespaces, versioning history | Reference (normative part) + Explanation (rationale) | main sections; history in `Optional` |

llms.txt-specific requirements (per https://llmstxt.org/ , accessed 2026-08-21): H1 project name; blockquote summary that "contains key information necessary for understanding the rest"; H2 file-lists with `[name](url): note` annotated links pointing at **markdown versions** (`page.md`); an `Optional` section for skippable depth; test the result by "asking an agent questions about your content, giving it only your llms.txt as a starting point." For a parse-target format specifically: ship one **golden fixture example** (exact bytes of a valid signature) in the reference page so agents can unit-test their parsers without reading prose — this is the cavage worked-example pattern transposed to an agentic audience. Progressive-disclosure contract (Anthropic 2025-09-29, see OD-3): the map page stays tiny; grammar/reference/how-to live behind links fetched only when an agent needs to implement a parser or emitter.

### Synthesis: Debut-Day Doc Skeleton

One-page community ICS docs site, prioritized:

**P0 — must ship tonight**
1. Annotated golden example: one real signature with each field labeled inline (Conventional Commits' examples-first move).
2. Field semantics table: 8 fields × {type, REQUIRED/OPTIONAL, allowed values, example} — OTel requirement-level column included.
3. Normative grammar block (~6 EBNF productions) + delimiter/whitespace rules stated to git-trailer precision.
4. Two copy-paste examples: full form + minimal form (which fields may be omitted, mirroring RFC 5424's NILVALUE concept).
5. One-paragraph extension policy: reserved namespaces (`omega.*` analog of `otel.*`), how new NODE names are added, versioning statement.
6. `/llms.txt` at site root: blockquote summary + H2 link-lists to the above as `.md`.

**P1 — this week**
7. How-to recipes: parser regex + emitter function per language (Diátaxis how-to).
8. Explanation page: why provenance signatures exist (truth-anchor, observability lineage).
9. Changelog with SemVer-style versioning of the FORMAT itself.

**P2 — later**
10. Tutorial walkthrough ("trace one session through its signatures").
11. Registry page for community extensions; railroad diagram if the grammar ever grows nesting; i18n.

### N7 Annotation — Spec Impact on `02_OPENCODE_JSON_DIFF.md` (2026-08-21)

**Verdict synthesis**: our current Phase 1 target pins `model` (+`variant`) on all 6 agents. That
gives local-first defaults but (a) makes TUI `/models` switches non-durable for those agents
(#13456 snap-back), (b) `variant` values are probably silently inert for our LM Studio models
(no confirmed variants map), and (c) changes nothing about CLI `-m`, which always wins.

**Recommended remediation of `02` (pending Architect approval)**:
1. **Add top-level `"model": "lmstudio/qwen3-4b-thinking"`** to the target state → M7 local-first
   becomes the TRUE default for every agent that doesn't pin (primary agents inherit it; task()
   subagents inherit their invoker).
2. **Strip `model` from researcher/maat/lilith/node** — they inherit the global local default and
   gain durable `/models` freedom. Keep exactly TWO pins: `kali` (deliberate cloud quality floor,
   Q5.1) and `verity` (hidden subagent; cheap-critic binding is the design intent; TUI freedom N/A).
3. **Drop `variant` from all agents** pending `opencode models --verbose` on 1.18.19 confirming
   the target models declare variants (stale variant = silently inert, so current spec values are
   likely decorative). Re-add per-model only where verified.
4. **Document the precedence chain + no-fallback fact** in `02`'s rationale table: CLI `-m/--variant`
   > agent pin > session last-used > global > provider default; opencode has NO agent-level
   provider fallback — failover remains Omega fabric's job (consistent with N6 domain).

Net effect: Architect's CLI stays fully flexible (`/models` durable, `-m` supreme), fleet still
defaults local-first, kali/verity bindings intentional rather than accidental.
