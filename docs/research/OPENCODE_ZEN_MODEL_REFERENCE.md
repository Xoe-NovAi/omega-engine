# 🔱 OpenCode Zen Model Reference for Omega Engine
⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_core ⬡ ZEN-REFERENCE

**AP Token**: `AP-ZEN-MODEL-REF-v1.0.0`
**Status**: LIVE | **Last Updated**: 2026-05-15
**Source**: https://opencode.ai/docs/zen/ (fetched live)

---

## §0 Purpose

This document is the canonical reference for all OpenCode Zen models used within the Omega Engine. It maps every available model to its capabilities, cost, context window, benchmark scores, and — most critically — which Omega Engine blocker each model is best suited to resolve.

This document is designed to be **machine-updatable** via the always-current system described in §4.

---

## §1 Current Model Roster (as of 2026-05-15)

### §1.1 Free Models

| Model ID | Context | SWE-bench Ver. | Input $/1M | Output $/1M | Specialty |
|---|---|---|---|---|---|
| `big-pickle` | 200K | — | Free | Free | Stealth model, general purpose, used as current agent |
| `deepseek-v4-flash-free` | 200K | ~79% | Free | Free | Fast coding, multi-file edits, strong Python/TS |
| `minimax-m2.5-free` | 205K | 80.2% | Free | Free | Agentic coding, budget throughput |
| `ring-2.6-1t-free` | — | — | Free | Free | 1T parameter, deep reasoning |
| `nemotron-3-super-free` | 205K | — | Free | Free | NVIDIA-hosted, general coding |
| `qwen3.6-plus-free` | 262K | 78.8% | Free | Free | Long context, multi-language |

### §1.2 Paid Models — Tier 1 (Budget, < $1/1M in)

| Model ID | Context | SWE-bench Ver. | Input | Output | Specialty |
|---|---|---|---|---|---|
| `gpt-5-nano` | 400K | — | $0.05 | $0.40 | Cheapest GPT, simple tasks |
| `gpt-5.4-nano` | 400K | — | $0.20 | $1.25 | Fast simple edits |
| `gpt-5.1-codex-mini` | 400K | — | $0.25 | $2.00 | Compact Codex, small edits |
| `minimax-m2.5` | 205K | 80.2% | $0.30 | $1.20 | Best value agentic coding |
| `minimax-m2.7` | 205K | ~79% | $0.30 | $1.20 | M2.5 successor |
| `qwen3.5-plus` | 262K | — | $0.20 | $1.20 | Multi-language, long context |

### §1.3 Paid Models — Tier 2 (Mid-Range, $1-$5/1M in)

| Model ID | Context | SWE-bench Ver. | Input | Output | Specialty |
|---|---|---|---|---|---|
| `gemini-3-flash` | 1.0M | 78.0% | $0.50 | $3.00 | Fast, 1M context, good value |
| `qwen3.6-plus` | 262K | 78.8% | $0.50 | $3.00 | Long context reasoning |
| `kimi-k2.5` | 262K | 76.8% | $0.60 | $3.00 | Code gen, algorithmic |
| `glm-5` | 205K | 77.8% | $1.00 | $3.20 | MIT-licensed, practical SWE |
| `gpt-5-codex` | 400K | ~78% | $1.07 | $8.50 | Code-specific GPT-5 |
| `gpt-5` | 400K | ~75% | $1.07 | $8.50 | General purpose GPT-5 |
| `gpt-5.1-codex` | 400K | ~78% | $1.07 | $8.50 | Better Codex |
| `gpt-5.1-codex-max` | 400K | ~79% | $1.25 | $10.00 | Deep Codex reasoning |
| `glm-5.1` | 205K | ~79% | $1.40 | $4.40 | Latest GLM, improved coding |
| `kimi-k2.6` | 262K | 80.2% | $0.95 | $4.00 | Open-weight 1T, top value |
| `gpt-5.4-mini` | 400K | ~76% | $0.75 | $4.50 | Compact GPT-5.4 |
| `gpt-5.2` | 400K | 80.0% | $1.75 | $14.00 | Strong general coding |
| `gpt-5.2-codex` | 400K | ~79.5% | $1.75 | $14.00 | Codex variant |
| `gpt-5.3-codex` | 400K | 85.0% | $1.75 | $14.00 | Top Codex for complex SWE |
| `gpt-5.3-codex-spark` | 128K | — | $1.75 | $14.00 | Fast Codex, limited ctx |
| `gemini-3.1-pro` | 1.0M | 80.6% | $2.00 | $12.00 | Strong all-rounder, 1M ctx |

### §1.4 Paid Models — Tier 3 (Premium, $5-$10/1M in)

| Model ID | Context | SWE-bench Ver. | Input | Output | Specialty |
|---|---|---|---|---|---|
| `claude-sonnet-4-6` | 1.0M | 79.6% | $3.00 | $15.00 | Best daily driver, balanced |
| `claude-sonnet-4-5` | 1.0M | 79.3% | $3.00 | $15.00 | Previous gen Sonnet |
| `claude-sonnet-4` | 1.0M | ~77% | $3.00 | $15.00 | Original Sonnet 4 |
| `claude-opus-4-5` | 200K | 80.9% | $5.00 | $25.00 | Strong reasoning (deprecating) |
| `claude-opus-4-6` | 1.0M | 80.8% | $5.00 | $25.00 | Top-tier, 1M ctx |
| `claude-opus-4-7` | 1.0M | 87.6% | $5.00 | $25.00 | **Best Claude on Zen** |
| `claude-haiku-4-5` | 200K | 73.3% | $1.00 | $5.00 | Fast, cheap Claude |
| `gpt-5.4` | 1.1M | ~78% | $2.50 | $15.00 | Strong all-rounder, 1.1M |

### §1.5 Paid Models — Tier 4 (Frontier, >$10/1M in)

| Model ID | Context | SWE-bench Ver. | Input | Output | Specialty |
|---|---|---|---|---|---|
| `gpt-5.5` | 1.1M | 88.7% | $5.00 | $30.00 | **Best on Zen**, top SWE |
| `gpt-5.5-pro` | 1.1M | — | $30.00 | $180.00 | Extreme reasoning, $$$ |
| `gpt-5.4-pro` | 1.1M | — | $30.00 | $180.00 | Max GPT-5.4 |
| `claude-opus-4-1` | 200K | ~75% | $15.00 | $75.00 | Legacy Opus, expensive |

---

## §2 Model Capability Deep-Dive

### §2.1 Top SWE-bench Performers (Available on Zen)

| Rank | Model | SWE-bench Verified | Context | Cost (in/out per 1M) |
|---|---|---|---|---|
| 1 | GPT-5.5 | 88.7% | 1.1M | $5 / $30 |
| 2 | Claude Opus 4.7 | 87.6% | 1.0M | $5 / $25 |
| 3 | GPT-5.3 Codex | 85.0% | 400K | $1.75 / $14 |
| 4 | Claude Opus 4.5 | 80.9% | 200K | $5 / $25 |
| 5 | Claude Opus 4.6 | 80.8% | 1.0M | $5 / $25 |
| 6 | DeepSeek V4 Flash | ~79% | 1.0M | Free |
| 7 | Gemini 3.1 Pro | 80.6% | 1.0M | $2 / $12 |
| 8 | Kimi K2.6 | 80.2% | 262K | $0.95 / $4 |
| 9 | MiniMax M2.5 | 80.2% | 205K | $0.30 / $1.20 |
| 10 | GPT-5.2 | 80.0% | 400K | $1.75 / $14 |
| 11 | Claude Sonnet 4.6 | 79.6% | 1.0M | $3 / $15 |
| 12 | Qwen3.6 Plus | 78.8% | 262K | $0.50 / $3 |
| 13 | GLM 5.1 | ~79% | 205K | $1.40 / $4.40 |

### §2.2 Specialty Mapping

| Specialty | Best Model | Runner-Up | Budget Pick |
|---|---|---|---|
| **Complex multi-file SWE** | GPT-5.5 | Claude Opus 4.7 | GPT-5.3 Codex |
| **Deep reasoning/architecture** | Claude Opus 4.7 | GPT-5.5 | DeepSeek V4 Flash |
| **Fast daily coding** | Claude Sonnet 4.6 | GPT-5.4 | MiniMax M2.5 |
| **Long context (1M+)** | Claude Opus 4.6/4.7 | Gemini 3.1 Pro | DeepSeek V4 Flash |
| **Cost-sensitive coding** | MiniMax M2.5 | Qwen3.6 Plus | DeepSeek V4 Flash (free) |
| **Python/TypeScript** | GPT-5.3 Codex | Claude Opus 4.6 | deepseek-v4-flash-free |
| **System architecture** | Claude Opus 4.7 | GPT-5.5 | Qwen3.6 Plus |
| **Simple string/conf edits** | Any free model | GPT-5 Nano | big-pickle |
| **API integration** | Claude Sonnet 4.6 | GPT-5.4 | deepseek-v4-flash-free |
| **Dev-ops/CLI scripting** | Claude Sonnet 4.6 | Gemini 3.1 Pro | minimax-m2.5-free |
| **Creative/generation** | Claude Opus 4.6 | GPT-5.4 | qwen3.6-plus-free |

---

## §3 Blocker-to-Model Mapping

### §3.1 Current Omega Engine Blocker Resolution

| Blocker | Best Model | Why | Fallback Model |
|---|---|---|---|
| **MCP server config fix (stale npm packages)** | `claude-sonnet-4-6` | Best at understanding npm ecosystem, precise JSON edits, package.json semantics | `gpt-5.4` |
| **Google API key env var fix** | `big-pickle` | Trivial string replacement, any model works | `deepseek-v4-flash-free` |
| **Wire openrouter into provider_map** | `claude-sonnet-4-6` | Python API integration, import management, config structure knowledge | `gpt-5.3-codex` |
| **Fix lmster URL bug** | `big-pickle` or `deepseek-v4-flash-free` | Simple config string fix | any free model |
| **Fix path inconsistencies** | `claude-opus-4-7` | System architecture understanding, cross-file awareness | `gpt-5.3-codex` |
| **Test MCP servers via npm** | `claude-sonnet-4-6` | CLI/npm workflow knowledge, error handling | `gpt-5.4` |
| **ContextBuilder wiring** | `claude-opus-4-6` | Deep Python async understanding, AnyIO patterns | `gpt-5.3-codex` |
| **Cross-pollination design** | `claude-opus-4-7` | System design, soul schema, architectural thinking | `gpt-5.5` |

### §3.2 Cost-Optimized Resolution Strategy

For offline/batch work, use this priority chain to minimize cost while maintaining quality:

```
1. big-pickle (free)         → Simple string replacements, path fixes
2. deepseek-v4-flash-free    → Small code edits, npm commands
3. minimax-m2.5-free         → Python edits under 205K context
4. qwen3.6-plus-free         → Long context tasks
5. claude-sonnet-4-6         → Complex multi-file coding ($3/$15)
6. claude-opus-4-6           → Architecture decisions ($5/$25)
7. gpt-5.5                   → Hardest blockers, only if others fail ($5/$30)
```

### §3.3 Models Used in This Session (Observed Performance)

| Model | Observed Strengths | Observed Weaknesses | Best Omega Role |
|---|---|---|---|
| **big-pickle** (current) | Fast response, good tool use, reliable | No known SWE-bench score | Default agent, daily driving |
| **deepseek-v4-flash** | Fast, strong coding, free | Free tier data may train | Budget coding, quick fixes |
| **Qwen 3.6 Plus** | Strong reasoning, long ctx | Slower than flash | Complex analysis |
| **Gemini models** | 1M context, strong all-round | Variable quality via Zen | Long context tasks |

---

## §4 Always-Current System Design

### §4.1 Live Model Discovery API

OpenCode Zen exposes a machine-readable endpoint:

```
GET https://opencode.ai/zen/v1/models
```

Returns OpenAI-compatible response with all available models, their IDs, and metadata. This is the **single source of truth** for the current model roster.

### §4.2 Omega Engine Model Sync Script

Create `scripts/sync-zen-models.sh` (or a Python equivalent):

```bash
#!/usr/bin/env bash
# sync-zen-models.sh — Fetch current Zen model roster and update reference
# Run: weekly via cron or on OpenCode version change

OUTPUT="docs/research/OPENCODE_ZEN_MODEL_REFERENCE.md"
TMP=$(mktemp)

curl -s https://opencode.ai/zen/v1/models | jq '.' > "$TMP"

echo "# 🔱 OpenCode Zen Model Roster (auto-generated $(date +%Y-%m-%d))" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo '```json' >> "$OUTPUT"
cat "$TMP" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

rm "$TMP"
echo "Updated $OUTPUT"
```

### §4.3 OpenCode Zen Config as Omega Provider

The Zen provider can be configured in Omega's `config/providers.yaml`:

```yaml
- provider: opencode-zen
  type: api
  base_url: https://opencode.ai/zen/v1
  api_key_env: OPENCODE_API_KEY
  discovery_url: https://opencode.ai/zen/v1/models
  auto_discover: true
  fallback_priority: 4  # After native, lmster, ollama
```

### §4.4 How to Check Current Models via OpenCode CLI

```bash
# In OpenCode TUI:
/models

# Or check config for current:
cat ~/.config/opencode/opencode.json | jq '.provider.opencode.models'

# Or programmatically:
curl -s https://opencode.ai/zen/v1/models \
  -H "Authorization: Bearer $OPENCODE_API_KEY" \
  | jq '.data[].id'
```

### §4.5 Model Change Frequency & Pattern

| Aspect | Observation |
|---|---|
| **New models added** | ~2-4 per month (tracking AI release cadence) |
| **Free models** | Rotate quarterly (promotional, limited time) |
| **Deprecations** | Announced ~2 months in advance (see §1.6) |
| **Price changes** | Rare — Zen sells at cost, passes drops through |
| **Current deprecations** | GPT-5.2 Codex, 5.1 Codex variants deprecated Jul 23, 2026 |

### §4.6 Agent Ownership

| Role | Agent | Responsibility |
|---|---|---|
| **Monitor** | Researcher Agent (Gemma 4-31B) | Weekly check of `/zen/v1/models`, update INDEX.md |
| **Update** | Builder Agent (any implementation agent) | Update blocker mappings when models change |
| **Audit** | Opus 4.6 (Oversight) | Monthly review of model usage costs vs quality |

### §4.7 Automated Agent Instruction

Include this in agent system prompts for model-aware routing:

```
When choosing a model for a task:
1. Check OPENCODE_ZEN_MODEL_REFERENCE.md for current roster
2. Use the cheapest model that can handle the task
3. For simple string edits: use free tier
4. For complex multi-file architecture: use Claude Opus 4.6/4.7 or GPT-5.5
5. For daily coding: Claude Sonnet 4.6
6. For budget coding: MiniMax M2.5 or DeepSeek V4 Flash Free
```

---

## §5 Appendix: Historical Model Changes

### Deprecated / Removed Models (Tracked)

| Model ID | Deprecated | Replaced By | Notes |
|---|---|---|---|
| `gpt-5.2-codex` | Jul 23, 2026 | `gpt-5.3-codex` | Upgraded |
| `gpt-5.1-codex` | Jul 23, 2026 | `gpt-5.2-codex` / `gpt-5.3-codex` | Upgraded |
| `gpt-5.1-codex-max` | Jul 23, 2026 | `gpt-5.3-codex` | Upgraded |
| `gpt-5.1-codex-mini` | Jul 23, 2026 | `gpt-5.3-codex-spark` | Upgraded |
| `gpt-5-codex` | Jul 23, 2026 | `gpt-5.1-codex` | Upgraded |
| `claude-sonnet-4` | Jun 15, 2026 | `claude-sonnet-4-5` / `claude-sonnet-4-6` | Upgraded |
| `glm-5` | May 14, 2026 | `glm-5.1` | Upgraded |
| `minimax-m2.1` | Mar 15, 2026 | `minimax-m2.5` | Upgraded |
| `gemini-3-pro` | Mar 9, 2026 | `gemini-3.1-pro` | Upgraded |
| `qwen3-coder-480b` | Feb 6, 2026 | `qwen3.6-plus` | Replaced |

### Newly Added Models (2026 Q2)

| Model ID | Added | Source |
|---|---|---|
| `gpt-5.5` | ~Apr 23, 2026 | OpenAI |
| `gpt-5.4` | ~Mar 2026 | OpenAI |
| `claude-opus-4-7` | ~Apr 2026 | Anthropic |
| `kimi-k2.6` | ~Apr 2026 | Moonshot |
| `glm-5.1` | ~Apr 2026 | Zhipu |
| `ring-2.6-1t-free` | ~May 2026 | InclusionAI |
| `big-pickle` | ~May 2026 | Stealth |

---

## §6 Quick Reference — Omega Engine Task Resolution

| Task Category | Recommended Model | Why |
|---|---|---|
| **Config string fixes** | `big-pickle` / `deepseek-v4-flash-free` | Free, fast, good enough |
| **Python code edits (single file)** | `claude-sonnet-4-6` | Best balance of precision and cost |
| **Python code edits (multi-file)** | `gpt-5.3-codex` | Codex specialization |
| **Architecture design** | `claude-opus-4-7` | Deep reasoning, 1M ctx |
| **npm / CLI operations** | `claude-sonnet-4-6` | Best tool use understanding |
| **Provider API integration** | `claude-sonnet-4-6` | API pattern knowledge |
| **Testing / dev-ops** | `gemini-3.1-pro` | Good at systematic workflows |
| **Soul schema design** | `claude-opus-4-6` | Philosophical + technical blend |
| **Long context analysis** | `gemini-3.1-pro` / `claude-opus-4-7` | 1M+ context windows |

---

*This document is auto-update ready. Run `scripts/sync-zen-models.sh` to refresh the model roster from OpenCode Zen's live API.*
