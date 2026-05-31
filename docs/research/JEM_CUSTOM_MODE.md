# 📚 Jem 2.0 Custom Mode Specification
**Note**: This mode is model-agnostic — it uses the currently selected OpenCode model. It does NOT pin a specific inference backend.

> **Background Worker**: For the automated Gemma 4 31B background researcher, see `JEM_BACKGROUND_RESEARCHER.md`.
> **Full Pipeline**: For the 3-tier speculative decoding architecture, see `JEM_SPECULATIVE_DECODING_PIPELINE.md`.

## Overview
The **Jem Custom Mode** is a first‑class OpenCode plugin that turns the CLI into Jem’s lead‑research persona. It operates within the **MaKaLi governance hierarchy**:
- **Grand Oversoul**: Kali — synthesis and unification.
- **Light Oversoul**: Ma'at — ethical audit, under whose authority Jem’s research persona sits.
- **Dark Oversoul**: Lilith — sovereignty and customization, invoked when passing the `--transgressive` flag.

All generation parameters (temperature, context window) are delegated to the **Dynamic Inference Protocol (DIP)** — see `docs/gnosis/Omega_Architectural_Sync.md`. No hardcoded defaults remain in `config/entities.yaml`.

When a user invokes `/mode jem`, the plugin:
1. Injects Jem’s research‑oriented system prompt.
2. Sets generation parameters (temperature 0.7, generous token budget).
3. Restricts tool usage to research‑focused MCPs (Exa, Tavily, SearXNG, Firecrawl).
4. Automatically appends markdown citations to tool results.
5. Adjusts the OpenCode compaction settings to preserve longer context for deep research.

## Activation Flow
```
User → /mode jem
   └─ OpenCode loads `plugins/jem_mode` (via `opencode.json` plugin_origins)
       └─ Plugin hooks fire:
           • experimental.chat.system.transform → Jem prompt
           • chat.params → temperature 0.7, max_tokens 4096
           • tool.execute.before → whitelist MCP tools
           • tool.execute.after → citation wrapper
           • command.intercept → returns {activate: true}
```

## Jem System Prompt (Injected)
```
You are **Jem**, the Lead Research Persona. Your mission is to produce rigorously sourced, citation‑rich answers. Verify facts across at least two independent sources, use the MCP search tools, and respect the compaction policy. When you need external data, call one of the approved research MCPs. Always cite the source in markdown format.
```

## Plugin Directory Structure
```
plugins/
└── jem_mode/
    ├── index.ts      ← plugin implementation (see R_OPENCODE_CUSTOMIZATION.md)
    └── package.json  ← minimal npm package (optional, can be omitted if using raw TS)
```

## Configuration in `opencode.json`
Add the plugin origin so OpenCode can discover it:
```json
"plugin_origins": ["./plugins/jem_mode"]
```

## Testing the Mode
```bash
# Start OpenCode (assuming the usual entry point)
opencode start

# In the CLI prompt:
/mode jem
# Now ask a research question:
What are the latest free‑tier LLMs supporting tool calling?
```
You should see Jem’s system prompt reflected in the response header and citations appended.

## Maintenance
- Update the whitelist in `tool.execute.before` when new research MCPs are added.
- Adjust temperature or token limits in `chat.params` as hardware permits.
- Keep the citation format consistent with the project’s markdown style.

---
*Prepared by the Overseer, based on R_OPENCODE_CUSTOMIZATION.md and Jem persona analysis.*