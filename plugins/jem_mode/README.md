# Jem 2.0 — OpenCode Plugin

## Overview

The **Jem 2.0 Plugin** transforms OpenCode into Jem's research persona. When activated via `/mode jem`, it injects the research system prompt and provides access to the full research MCP fleet.

## Installation

The plugin is registered in `opencode.json` via `plugin_origins`:
```json
{
  "plugin_origins": ["./plugins/jem_mode"]
}
```

## Activation

```bash
# In OpenCode CLI:
/mode jem

# Now ask a research question:
Exa, what are the latest developments in open-source LLM fine-tuning?
```

## Requirements

- OpenCode v1.15.0+
- Research MCPs registered in `opencode.json` (Exa, Tavily, SearXNG, Firecrawl, Jina, Brave)
- API keys for external MCPs in `.env`

## Model Behavior

The Jem plugin is **model-agnostic** — it uses whatever model is currently selected in OpenCode. It does NOT pin a specific backend.

## Files

| File | Purpose |
|------|---------|
| `index.ts` | Plugin implementation (system prompt injection, tool whitelist) |
| `package.json` | npm package metadata |
| `README.md` | This file |

## Related

- `.opencode/modes/jem-2.0.md` — OpenCode custom mode definition (alternative to plugin)
- `docs/research/JEM_SPECULATIVE_DECODING_PIPELINE.md` — Full 3-tier pipeline architecture
- `docs/research/JEM_BACKGROUND_RESEARCHER.md` — Background worker operational spec