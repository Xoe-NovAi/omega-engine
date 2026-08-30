<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — OpenCode+M3 (200K) ↔ Cline+M3 (1M) Dialog
# ⬡ OMEGA ⬡ SOPHIA ⬡ MiniMax-M3 (1M Cline) + MiniMax-M3 (200K OpenCode) ⬡ DIALOG
# AP: AP-DIALOG-M3-PAIR-v1.0.0
# Date: 2026-06-02
# Status: DIALOG OPEN

## Purpose

This handoff initiates a **bidirectional dialog** between:
- **OpenCode session** — `minimax-m3` (200K context) — running here
- **Cline session** — `minimax-m3` (1M context) — running via Cline CLI v3.0.15

Both instances run the same model family (MiniMax M3) but with different context
windows. Cline gets 1M, OpenCode gets 200K. We use Cline for **deep synthesis**
across many files; OpenCode for **focused execution** with surgical context.

## Protocol

1. OpenCode reads `HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` for engine map.
2. OpenCode posts context/continuation to `omega-hub` hivemind (CLI = `opencode-m3`).
3. Cline reads the hivemind via `hivemind_get_continuation(cli="opencode-m3")`.
4. Cline writes its response as a new file under `data/handoff/cline_to_opencode_*.md`
   AND posts a continuation note to the hivemind (CLI = `cline`).
5. OpenCode reads Cline's response and acts on it.

## Current Request — OpenCode → Cline (2026-06-02)

### Synthesis Task: Build the Model Reference Library (R100)

**Context**: The legacy stack at
`/home/arcana-novai/Documents/Archives/Old-Stacks/Xoe-NovAi/docs/ai-research/admin/ai-provider-matrix.md`
has a 327-line "AI Provider Capabilities Matrix" with 4 cloud providers (Grok,
Claude, ChatGPT, Gemini) rated on 7 metrics. The user wants a **new, comprehensive
Model Reference Library** that extends this pattern to:

1. **TIER 0 — Local Sovereign (GGUF models on disk)**
   - All models in `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/models.yaml`
   - Includes: qwen3-0.6b-q6_k, qwen3-1.7b, qwen3-1.7b-q6_k, qwen3-4b-thinking,
     deepseek-r1-qwen3-8b, krikri-8b, phi-4-mini, phi-2-omnimatrix, embeddinggemma-300m
   - Local file paths, RAM estimates, contexts, quantizations, strengths/weaknesses
2. **TIER 1 — Free Local Inference Servers**
   - Ollama (running on :11434 with `qwen2.5:0.5b`)
   - LM Studio (installed but not running)
   - Native GGUF (llama-cpp-python — not yet installed)
3. **TIER 2 — Free Cloud Models (when local is unavailable)**
   - Google AI Studio (Gemma 2 9B, Gemma 4 31B — `GOOGLE_API_KEY` in `.env`)
   - OpenRouter free tier models (`OPENROUTER_API_KEY` in `.env`)
   - OpenCode Zen (free tier: `minimax/minimax-m3` — **200K context**, NOT 1M)
   - GitHub Copilot (free tier: Haiku, GPT-4.1, etc.)
   - Hugging Face Inference (free for some models)
4. **TIER 3 — Free MCP-based Research Services**
   - **SearXNG** (running locally on :8017 — sovereign, JSON API, 14 engines)
   - **Firecrawl** (`firecrawl-mcp` 3.20.2, `FIRECRAWL_API_KEY` in `.env`)
   - **Exa** (remote streamable-http at `mcp.exa.ai/mcp`, `EXA_API_KEY` in `.env`)
   - **Jina** (remote streamable-http at `mcp.jina.ai/v1`, `JINA_API_KEY` in `.env`)
   - **Tavily** (`tavily-mcp` 0.2.20, `TAVILY_API_KEY` in `.env`)

### Deliverable

Write **`docs/research/R100_MODEL_REFERENCE_LIBRARY.md`** containing:

1. **Header** with metadata, version, last-updated, audience
2. **§0 Philosophy** — why we maintain a model library; tier system rationale
3. **§1 Tier 0 — Local Sovereign GGUFs** (table + per-model detail)
4. **§2 Tier 1 — Free Local Servers** (Ollama, LM Studio, native-gguf)
5. **§3 Tier 2 — Free Cloud Models** (Google, OpenRouter, OpenCode Zen, Copilot, HF)
6. **§4 Tier 3 — Free MCP Services** (SearXNG, Firecrawl, Exa, Jina, Tavily)
7. **§5 Strengths/Weaknesses Matrix** for ALL items (7-metric rating per legacy pattern)
8. **§6 Selection Algorithm** (Python) — `select_model(complexity, cost, sovereignty)`
9. **§7 Update Protocol** — how this doc is maintained (who, when, how)
10. **§8 Cross-References** — link to R99 (search APIs), R99_DEEP_RESEARCH, etc.

### Style

- Follow the legacy `ai-provider-matrix.md` style (markdown, tables, ratings)
- Cite the data source for every entry (file path + line number)
- Include the M3 free tier 200K correction (NOT 1M) in the OpenCode Zen section
- Note: 1M context is only available via Cline (and the Artisan handoff that produced
  this), NOT via OpenCode Zen's free tier

### Why 1M Context Helps

- 491-line handoff doc + 327-line matrix + ~150-line models.yaml + ~80-line
  providers.yaml + 15-line mcp_servers.json + 5 more handoffs ≈ **1,300+ lines**
- Plus all R-docs (~45 docs in `docs/research/`)
- OpenCode's 200K would force targeted reads; Cline's 1M can hold it ALL

## Status of This Dialog

- **OpenCode post**: Posted to hivemind at 2026-06-02T13:43:57Z
  (`hivemind_post_context` with CLI=`opencode-m3`, session=`ses_opencode_m3_20260602_dialog`)
- **Cline post**: Awaiting (Cline should read this file and the hivemind)
- **OpenCode work in parallel**: OpenCode will also build a draft R100 from focused
  200K context reads; Cline's 1M version will be richer

## What OpenCode Has Already Done (for Cline's awareness)

1. ✅ Verified SearXNG running on :8017 (JSON search returns Brave/mwmbl/Reddit)
2. ✅ Wired all 5 search MCPs to `~/.config/opencode/mcp_servers.json`:
   - Tavily: `tavily-mcp` 0.2.20 (corrected from `@tavily/mcp`)
   - Firecrawl: `firecrawl-mcp` 3.20.2
   - Exa: streamable-http `https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa`
   - Jina: streamable-http `https://mcp.jina.ai/v1` (returns "Jina AI Official MCP Server v1.4.0")
   - SearXNG: stdio `searxng-mcp` with `SEARXNG_SERVER_URL=http://127.0.0.1:8017`
3. ✅ Started SearXNG container via `systemctl --user start omega-searxng.service`
4. ✅ Discovered legacy `ai-provider-matrix.md` (327 lines, the pattern)
5. ✅ Cataloged legacy scripts (`catalog.json`) and persona JSONs (lilith.json)
6. ✅ Updated todos to reflect new state
7. ⏳ Building R100 Model Reference Library (in progress)
8. ⏳ Updating PIVOT_LOG with Decisions 83-86
9. ⏳ Reconciling M3 200K context in docs (NOT 1M)

## What OpenCode Needs from Cline (1M context requests)

1. **Build R100** as specified above
2. **Cross-reference all 5 handoffs in `data/handoff/`** for any conflicts/gaps
3. **Audit the OpenCode MCP router fix** (Section 5 of the handoff) — the open
   problem with the 4-of-5 startup failures
4. **Synthesize the WAD system gaps** into a concrete fix plan (Section 8)
5. **Suggest optimal routing** for the user's specific hardware (Ryzen 7 5700U)
   given the 1M context you can hold of all models simultaneously

## How Cline Should Respond

1. Write your synthesis to `docs/research/R100_MODEL_REFERENCE_LIBRARY.md`
2. Also write `data/handoff/cline_to_opencode_m3_response_20260602.md` with:
   - Path to R100
   - Summary of new findings beyond the Artisan handoff
   - Specific recommendations for the user's hardware
   - Open questions for OpenCode to verify
3. Post to hivemind (`hivemind_post_context` with CLI=`cline`)
4. OpenCode will read both files and the hivemind on next turn

---

*Sent from OpenCode+M3 (200K) to Cline+M3 (1M). Both run the same model family.
The 1M context window is the only differentiator — use it to read broadly; I
will execute narrowly.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: MiniMax-M3 (1M Cline) + MiniMax-M3 (200K OpenCode) | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
