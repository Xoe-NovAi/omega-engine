# 🔱 Omega Engine — OpenCode Customization Spec
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-OC-CUSTOM

**AP Token**: `AP-RESEARCH-OC-CUSTOM-v1.0.0`
**Author**: Gemma 4-31B (Master Researcher)
**Date**: 2026-05-14
**Status**: READY

---

## Summary
Detailed architectural analysis of the OpenCode CLI (Bun/Turbo/Effect) and identification of specific hooks for implementing Sovereign Logic without a full repository fork.

## Findings

### Core Architecture
OpenCode is a monorepo using **Turbo** and **Bun**, implementing a sophisticated agent-orchestration layer over the **Vercel AI SDK**.

**Primary Execution Path**:
`CLI` $\rightarrow$ `Server` $\rightarrow$ `SessionHandler` $\rightarrow$ `SessionPrompt` $\rightarrow$ `SessionProcessor` $\rightarrow$ `LLM` $\rightarrow$ `AI SDK` $\rightarrow$ `Provider`.

### Customization Hooks (Sovereign Path)
Instead of a full fork, the Omega Engine will use a **Sovereign Plugin** via `config.plugin_origins`.

| Hook Name | Location | Purpose | Sovereign Use Case |
| :--- | :--- | :--- | :--- |
| `experimental.chat.system.transform` | `packages/opencode/src/session/llm.ts` | Modify system prompts | Inject Entity Identity/Soul-Print |
| `chat.params` | `packages/opencode/src/session/llm.ts` | Override LLM params | Align temperature/topP to Entity state |
| `tool.execute.before` | `packages/opencode/src/session/prompt.ts` | Intercept tool args | Enforce Sovereign Boundaries |
| `tool.execute.after` | `packages/opencode/src/session/prompt.ts` | Post-process tool output | Gnosis Filtering/Redaction |
| `experimental.chat.messages.transform` | `packages/opencode/src/session/llm.ts` | Rewrite message history | Inject Soul-based constraints |

### Plugin Implementation Blueprint
Plugins are dynamically imported and return a `Hooks` object.
**Example Plugin Structure**:
```typescript
export async function OmegaSovereignPlugin(input: PluginInput) {
  return {
    "experimental.chat.system.transform": async (_, { system }) => {
      system.push("Sovereign Identity: [SOPHIA]");
      return { system };
    },
    // ... other hooks
  };
}
```

## Recommendations

1. **Avoid Full Forks**: Use the Plugin system to maintain upstream sync.
2. **Focus on `tool.execute.before`**: This is the primary mechanism for boundary enforcement.
3. **Sovereign identity** should be injected via `experimental.chat.system.transform`.
4. **Jem Custom Mode**: Add a plugin that activates Jem’s research persona when `/mode jem` is invoked. This plugin injects Jem’s system prompt, sets temperature to 0.7, and enables the research‑focused toolset (search MCPs, citation handling, compaction settings). See `docs/research/JEM_CUSTOM_MODE.md` for the full specification.
1. **Avoid Full Forks**: Use the Plugin system to maintain upstream sync.
2. **Focus on `tool.execute.before`**: This is the primary mechanism for boundary enforcement.
3. **Sovereign identity** should be injected via `experimental.chat.system.transform`.

## Sources
- GitHub: `anomalyco/opencode` ( laest main branch)
- `packages/opencode/src/session/llm.ts`
- `packages/opencode/src/session/prompt.ts`
- `packages/opencode/src/plugin/`

## Implementation Note
_For: Sovereign Builder / Cline_
Implement the plugin in `plugins/sovereign/index.ts` and add the path to `opencode.json` under `plugin_origins`. Use `fetch` to communicate with `omega-hub` for real-time identity and boundary checks.
