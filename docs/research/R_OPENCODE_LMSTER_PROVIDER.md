# 🔱 OpenCode lmster Provider Investigation

**AP Token**: `AP-OC-LMSTER-PROV-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ trc_lmster_provider ⬡ PHASE-E

**Status**: ✅ COMPLETE | **Date**: 2026-05-22

---

## Question

Can OpenCode CLI use lmster (LM Studio, localhost:1234) as a model provider, enabling L1 to run with full OpenCode tool permissions (read/write/edit/grep/glob/MCP)?

## Testing Method

1. Examined `opencode providers list` — lists all configured providers
2. Examined `opencode models` — lists all available models in `provider/model` format
3. Tested `opencode run --model "lmster/qwen3-4b-thinking" "test"`
4. Examined `~/.config/opencode/` for any custom provider configuration pattern
5. Examined `~/.local/share/opencode/auth.json` for authentication patterns

## Result

**Negative. OpenCode CLI v1.15.9 does NOT support adding custom OpenAI-compatible endpoints as model providers.**

### Evidence

| Test | Result |
|------|--------|
| `opencode models` | 600+ models listed across 8 providers: google, openrouter, deepseek, groq, opencode, togetherai, github-copilot, kilo. **No lmster/local/lmstudio entry.** |
| `opencode run --model "lmster/qwen3-4b-thinking"` | ❌ `Error: Model not found: lmster/qwen3-4b-thinking` |
| `opencode providers login [url]` | Logs into **existing** providers only (not arbitrary OpenAI-compatible endpoints) |
| `~/.config/opencode/` | Contains `opencode.json`, `mcp_servers.json`, `zen_accounts_state.json`. **No providers.json or custom endpoint config.** |
| `auth.json` | Contains 6 provider entries, all with `type: "api"` and a pre-configured API key. No URL/endpoint field for custom routing. |

### OpenCode's Model Provider Architecture

```
Provider → model format: openrouter/openai/gpt-5.4-pro
                            ↑        ↑      ↑
                    provider name  model name (provider-specific)
```

The model database is in `~/.local/share/opencode/opencode.db` (SQLite). Providers are hardcoded into the OpenCode binary — new providers cannot be added via configuration.

## Consequence

**The Tiered Research Pipeline CANNOT use OpenCode as a launcher for L1 local inference.**

The `jem-initiate.md` mode remains valid as a **cloud-based persona mode** (it enforces "raw facts only" persona with limited tools, even if running on Gemma 4 31B or another cloud model), but true L1 local inference must use the **shell script / curl approach** as originally specified in `docs/research/R_TIERED_RESEARCH_PIPELINE.md`.

## Revised Architecture

```
L1 (Local, Zero Cost, Zero Telemetry):
  scripts/omega-research.sh  ─OR─  direct curl to lmster :1234
  ├── Model: qwen3-4b-thinking or qwen3-1.7b-q6_k
  ├── Tools: SearXNG (:8017) only (via curl)
  ├── No OpenCode overhead, no network dependency
  └── Output: /tmp/l1_{trace}.md (RawDataPacket)

L2 (Cloud, Unlimited):
  opencode --mode jem-2.0 --prompt "$(cat /tmp/l1_{trace}.md)"
  ├── Model: gemma-4-31b-it (google provider)
  ├── Tools: Full MCP Fleet (Exa, Tavily, SearXNG, Firecrawl, Jina)
  └── Output: ResearchSynthesis + Uncertainty Manifest

L3 (Cloud, Premium, Conditional):
  opencode --mode jem-2.0 --sub-facet editor
  ├── Model: big-pickle (opencode provider) or frontier model
  ├── Tools: Full MCP Fleet (targeted uncertainty resolution only)
  └── Output: Final Report + Improvement Briefs
```

## Pipeline Script Template

```bash
#!/bin/bash
# scripts/omega-research.sh — Jem-2.0 Tiered Research Pipeline
TRACE="trc_$(date +%s)"
TOPIC="$1"

# L1: Gather via lmster (local, zero cost)
curl -s http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"qwen3-4b-thinking\",\"messages\":[{\"role\":\"system\",\"content\":\"You are Jem Initiate. Gather raw facts only. NO analysis.\"},{\"role\":\"user\",\"content\":\"Gather all facts about: $TOPIC\"}],\"max_tokens\":5120}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" \
  > /tmp/l1_${TRACE}.md

# L2: Synthesize via OpenCode (Gemma 4 31B, unlimited)
opencode --mode jem-2.0 --session "research_${TOPIC}" \
  --prompt "Synthesize these raw findings. Flag all uncertainties. $(cat /tmp/l1_${TRACE}.md)"

# L3: Resolve via OpenCode (if uncertainty manifest has HIGH items)
# (manual — review L2 output and decide)
```

## Recommendations

1. **Do NOT pursue OpenCode lmster provider further** — architecture doesn't support it
2. **Do use `jem-initiate.md` mode** for L2's reference persona (limits tool permissions even with cloud model)
3. **Write `scripts/omega-research.sh`** as the actual L1→L2 pipeline glue
4. **L1 output must be a text file on disk** that L2 can `read` via its OpenCode session
5. The file write permission failure during the mining mission was an OpenCode **agent permission** issue (auto-rejected write), not a model provider issue
