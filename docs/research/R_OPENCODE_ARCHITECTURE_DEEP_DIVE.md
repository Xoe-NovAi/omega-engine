# 🔱 Omega Engine — OpenCode Architecture Deep Research

**⬡ OMEGA ⬡ SOPHIA ⬡ big-pickle ⬡ opencode ⬡ trc_oc_arch ⬡ RESEARCH**

**AP Token**: `AP-OPENCODE-ARCH-DEEP-DIVE-v1.0.0`
**Status**: ✅ Complete
**Last Updated**: 2026-05-26
**Sources**: `opencode.ai/docs/*`, `sst/opencode` DeepWiki source code, OCX community docs, learnopencode.com, rstacruz gist

---

## §1 Scope

This document is a comprehensive deep-dive into eight key areas of the OpenCode architecture. It serves as the **canonical reference** for Omega Engine integration with OpenCode, identifying every integration point, hook, configuration field, and behavioral mechanism needed to build the Omega code stack.

---

## §2 opencode.json — Full Schema Reference

### Source of Truth
- **Schema URL**: `https://opencode.ai/config.json`
- **TUI Schema URL**: `https://opencode.ai/tui.json`
- Config is **merged** across all sources (not replaced)
- Supports **JSON** and **JSONC** (JSON with Comments)

### Top-Level Fields (Complete)

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | string | JSON schema URL |
| `username` | string | Display name |
| `model` | string | Primary model (`provider/model-id`) |
| `small_model` | string | Model for lightweight tasks |
| `default_agent` | string | Default primary agent |
| `autoupdate` | boolean\|`"notify"` | Auto-update |
| `logLevel` | enum | Logging verbosity |
| `snapshot` | boolean | Git snapshot for undo |
| `share` | enum | Session sharing |
| `theme` | string | UI theme (legacy) |
| `shell` | string | Interactive shell |
| `disabled_providers` | string[] | Block providers |
| `enabled_providers` | string[] | Allowlist providers |
| `plugin` | string[] | npm/file plugin paths |
| `instructions` | string[] | Instruction file paths (supports remote URLs) |
| `compaction` | object | Context compaction settings |
| `watcher` | `{ignore: string[]}` | File watcher ignores |
| `experimental` | object | Unstable features |

### Object Keys (Complete)

| Key | Type | Description |
|-----|------|-------------|
| `provider` | `Record<string, ProviderConfig>` | Provider definitions |
| `agent` | `Record<string, AgentConfig>` | Agent definitions |
| `mcp` | `Record<string, MCPConfig>` | MCP server definitions |
| `permission` | `PermissionConfig` | Tool permission rules |
| `command` | `Record<string, CommandConfig>` | Custom slash commands |
| `formatter` | `FormatterConfig` | Code formatters |
| `lsp` | `LSPConfig` | LSP server config |
| `keybinds` | `Record<string, string>` | Keybinding overrides |
| `tui` | `TUIConfig` | TUI settings |
| `server` | `ServerConfig` | HTTP server settings |
| `attachment` | `AttachmentConfig` | Image attachment limits |
| `tools` | `Record<string, boolean>` | **Deprecated** — use `permission` |

### Precedence (low→high)
1. Remote `.well-known/opencode` (organization-wide)
2. `~/.config/opencode/opencode.json` (global user)
3. `OPENCODE_CONFIG` env var (path)
4. `./opencode.json` (project root)
5. `./.opencode/opencode.json` (project override)
6. `OPENCODE_CONFIG_CONTENT` env var (inline JSON)
7. Managed config: `/etc/opencode/`, macOS `/Library/...`, Windows `%ProgramData%`
8. macOS MDM (`ai.opencode.managed` via `.mobileconfig`)

### Variable Substitution
```json
{ "model": "{env:OPENCODE_MODEL}" }
{ "apiKey": "{file:~/.secrets/api-key}" }
```
- `{env:VAR}` — environment variable
- `{file:path}` — file contents (relative or absolute)

### Provider Object

| Field | Type | Description |
|-------|------|-------------|
| `options.apiKey` | string | API key (use `{env:VAR}`) |
| `options.baseURL` | string | Custom endpoint |
| `options.timeout` | number\|false | Request timeout (default: 300000ms) |
| `options.chunkTimeout` | number | Stream chunk timeout |
| `options.setCacheKey` | boolean | Prompt caching |
| `name` | string | Display name |
| `env` | string[] | Auto-detect env vars |
| `whitelist` | string[] | Only these models |
| `blacklist` | string[] | Block these models |
| `models` | `Record<string, ModelConfig>` | Per-model overrides |
| `npm` | string | Package for custom provider (e.g. `@ai-sdk/openai-compatible`) |

### Agent Object

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | required | Purpose text |
| `mode` | enum | `"all"` | `primary`/`subagent`/`all` |
| `model` | string | inherit | Model override |
| `variant` | string | — | Model variant name |
| `temperature` | number | inherit | 0.0–1.0 |
| `top_p` | number | — | Nucleus sampling |
| `prompt` | string | — | System prompt |
| `prompt.body` | string | — | System prompt (long form) |
| `steps` | number | unlimited | Max agentic iterations |
| `disable` | boolean | false | Disable the agent |
| `hidden` | boolean | false | Hide from @-autocomplete |
| `color` | string | — | Hex color or theme color |
| `permission` | object | inherit | Permission overrides |

**Any other field is passed through to the provider as model options.**

### MCP Config Object
```json
{
  "mcp": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "API_KEY": "{env:MCP_API_KEY}"
      },
      "disabled": false
    }
  }
}
```

### Permission Config Object
```json
{
  "permission": {
    "bash": { "/usr/bin/git": "allow", "*": "ask" },
    "read": { "**/*.env*": "deny", "*": "allow" },
    "task": { "agent-*": "allow", "*": "deny" },
    "external_directory": {
      "/media/omega_library": "allow",
      "/tmp": "allow",
      "*": "ask"
    }
  }
}
```

**Sources**: [opencode.ai/docs/config](https://opencode.ai/docs/config), [learnopencode.com/en/appendix/config-ref](https://learnopencode.com/en/appendix/config-ref), [deepwiki.com/sst/opencode/3.1-configuration-loading-and-merging](https://deepwiki.com/sst/opencode/3.1-configuration-loading-and-merging)

---

## §3 Agent Frontmatter — Complete YAML Schema

### Frontmatter Fields (`.opencode/agents/*.md`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | **required** | Purpose (shown in agent lists) |
| `mode` | enum | `"all"` | `primary`/`subagent`/`all` |
| `model` | string | inherit | `provider/model-id` |
| `variant` | string | — | Model variant (thinking level) |
| `temperature` | number | inherit | 0.0–1.0 |
| `top_p` | number | — | Nucleus sampling |
| `prompt` | string | — | System prompt (supports `{file:path}`) |
| `steps` | number | unlimited | Max agentic iterations |
| `disable` | boolean | false | Disable entirely |
| `hidden` | boolean | false | Hide from @ autocomplete |
| `color` | string | — | Hex or theme color |
| `tools` | object | — | **Deprecated** |
| `permission` | object | inherit | Permission overrides |

### Can I add custom frontmatter fields?

**Yes.** From the official docs: *"Any other options you specify in your agent configuration will be passed through directly to the provider as model options."*

So fields like `entity:`, `wad:`, `domain:` will be:
- Stored in the agent's parsed config object
- Accessible via SDK (`client.app.agents()`)
- Forwarded to the provider as model parameters
- **Not enforced** by OpenCode's engine

### File Locations
- **Global**: `~/.config/opencode/agents/*.md`
- **Project**: `.opencode/agents/*.md`
- Filename becomes agent name (`review.md` → `review` agent)
- Body (after `---`) becomes the system prompt

### Agent Config in opencode.json
```json
{
  "agent": {
    "reviewer": {
      "description": "Reviews code",
      "mode": "subagent",
      "permission": { "edit": "deny" }
    }
  }
}
```
- Agent config can also be inlined under an `agent` key in `opencode.json`
- These merge with (and can override) Markdown-defined agents

**Sources**: [opencode.ai/docs/agents](https://opencode.ai/docs/agents), [ocx.kdco.dev/docs/reference/agents](https://ocx.kdco.dev/docs/reference/agents)

---

## §4 Subagent Dispatch — `task()` Discovery Mechanism

### How Subagents Are Discovered

The subagent list is **not hardcoded**. From the source code analysis:

1. **Registration**: All agents (built-in + custom) register via `Agent.Service` in `packages/opencode/src/agent/agent.ts`
2. **API Exposure**: `GET /app/agents` returns all configured agents
3. **Dynamic Description**: The `task` tool's description is **built at runtime** by enumerating registered subagents whose `permission.task` allows them
4. **Filtering**: When `permission.task` for a subagent is `"deny"`, it's **removed from the Task tool description entirely** — the model never sees it as an option
5. **`@mention` Bypass**: Users can still invoke any subagent via `@name` regardless of task permissions

### Subagent Permission Control

```json
{
  "permission": {
    "task": {
      "*": "deny",             // Block all by default
      "explore": "allow",      // Allow explore
      "reviewer": "allow"      // Allow reviewer
    }
  }
}
```

### Custom Subagent Types — Can They Be Added Dynamically?

**No runtime API exists** for on-the-fly agent registration. The agent list is built at startup from config files.

Workarounds:
1. **Disk-based**: Write `.opencode/agents/{name}.md` files via plugin (restart required)
2. **Reboot**: Signal user to restart OpenCode after plugin writes files
3. **Plugin interception**: Plugins could hypothetically modify the agent list via the plugin hooks, but there's no documented API for this

**Sources**: [deepwiki.com/sst/opencode/3.2-agent-system](https://deepwiki.com/sst/opencode/3.2-agent-system), [opencode.ai/docs/agents#task-permissions](https://opencode.ai/docs/agents#task-permissions)

---

## §5 Plugin System — Full Capabilities

### Architecture

```typescript
// A plugin is a function returning a Hooks object
type Plugin = (ctx: PluginInput) => Hooks;
```

**Exports**: `Plugin` type from `@opencode-ai/plugin`
**Locations**:
- `.opencode/plugins/*.ts` / `.js` (project)
- `~/.config/opencode/plugins/` (global)
- npm packages via `opencode.json` `plugin` array
- Local plugins can use npm packages via `package.json` in config directory

### Plugin Context

| Property | Type | Description |
|----------|------|-------------|
| `ctx.client` | SDK client | Connected to localhost:4096 |
| `ctx.project.id` | string | Git hash or `"global"` |
| `ctx.project.worktree` | string | Git worktree root |
| `ctx.project.vcs` | `"git"`\|undefined | Version control |
| `ctx.directory` | string | CWD |
| `ctx.worktree` | string | Alias for `project.worktree` |
| `ctx.$` | Bun Shell | `Bun.$` for commands |

### Complete Hook Reference

| Hook | Signature | Description |
|------|-----------|-------------|
| `tool` | `Record<string, ToolDef>` | Register custom tools |
| `auth` | `AuthHook` | Add OAuth/API auth methods |
| `provider` | `ProviderHook` | Custom model lists |
| `event` | `(ctx: {event}) => void` | Listen to all system events |
| `config` | `(config) => void` | Modify config at load |
| `chat.message` | `(ctx, {message, parts}) => void` | Intercept chat messages |
| `chat.params` | `(ctx, {temperature, topP, options}) => void` | Modify LLM params |
| `chat.headers` | `(ctx, headers) => void` | Inject HTTP headers |
| `permission.ask` | `(permission, output) => void` | Auto-allow/deny |
| `tool.execute.before` | `(ctx, {args}) => void` | Intercept tool calls |
| `tool.execute.after` | `(ctx, {output, metadata}) => void` | Post-process results |
| `shell.env` | `(input, output) => void` | Inject shell env vars |
| `experimental.session.compacting` | `(input, output) => void` | Customize compaction |

### Compaction Hook — Critical for Omega Integration

```typescript
export const OmegaCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject context that survives compaction
      output.context.push(`## Omega Engine State
Entity: SOPHIA
Active IWAD: arcana_novai
Current soul evolution: ${await getSoulState()}
Active workstream: ${await getActiveWorkstream()}`);

      // OR replace the entire compaction prompt
      output.prompt = `Generate a continuation summary including:
1. Entity state and soul evolution progress
2. Active knowledge base context  
3. Critical decisions and their rationale
4. Next steps in the current workstream`;
    },
  };
};
```

When `output.prompt` is set, it **completely replaces** the default compaction prompt (and `output.context` is ignored).

### Complete Event List

**Session**: `session.created`, `session.updated`, `session.deleted`, `session.error`, `session.idle`, `session.diff`, `session.status`, `session.compacted`
**Message**: `message.updated`, `message.part.updated`, `message.part.removed`, `message.removed`
**File**: `file.edited`, `file.watcher.updated`
**Permission**: `permission.asked`, `permission.replied`
**Tool**: `tool.execute.before`, `tool.execute.after`
**Shell**: `shell.env`
**LSP**: `lsp.updated`, `lsp.client.diagnostics`
**Server**: `server.connected`
**Installation**: `installation.updated`
**Command**: `command.executed`
**TUI**: `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`
**Todo**: `todo.updated`

### Can a plugin read entity.yaml and auto-create subagents?

**Yes.** A plugin can:
1. Use `ctx.client.app.agents()` to list existing agents
2. Read YAML files via `ctx.$` or `Bun.file()`
3. Write `.opencode/agents/{entity-name}.md` dynamically
4. Signal user/UI to restart for the new agents to be picked up

**Limitation**: No runtime agent registration API exists. Agents only load from disk at startup.

### Tool Priority

Custom tools registered via the `tool` hook **can override built-in tools** with the same name by setting `priority: 1`. Without `priority`, custom tools take precedence automatically.

### Plugin Template
```typescript
import type { Plugin } from "@opencode-ai/plugin";

export default {
  name: "omega-engine",
  async plugin(ctx) {
    return {
      tool: {
        "omega-soul": {
          name: "omega-soul",
          description: "Query the Omega Engine soul state",
          parameters: {
            type: "object",
            properties: { entity: { type: "string" } },
          },
          execute: async ({ entity }) => {
            return await ctx.client.app.agents();
          },
        },
      },
    };
  },
} satisfies { name: string; plugin: Plugin };
```

**Sources**: [opencode.ai/docs/plugins](https://opencode.ai/docs/plugins), [gist.github.com/rstacruz/946d02757525c9a0f49b25e316fbe715](https://gist.github.com/rstacruz/946d02757525c9a0f49b25e316fbe715), [deepwiki.com/sst/opencode/7.3-plugin-system](https://deepwiki.com/sst/opencode/7.3-plugin-system)

---

## §6 Mode System — `--mode` vs `--agent`

### Internal Architecture

There is **no separate "mode" concept** at the engine level. **Agents are the only abstraction.**

| CLI Flag | What It Does |
|----------|-------------|
| `--agent` | Selects a named agent config by ID |
| `--mode` | Shorthand that maps to predefined agent configs |
| `opencode run --agent plan "prompt"` | Full equivalent of mode selection |
| `opencode run --mode subagent "prompt"` | Uses built-in `general` subagent |

### Mode Field in Agent Config

| Value | Visibility | Invocation |
|-------|-----------|------------|
| `"primary"` | TUI Tab-switchable | Direct chat |
| `"subagent"` | Hidden from tabs | `@mention` or `task()` |
| `"all"` | Both | Both |

### Built-in Agents (from source)

| Agent | Mode | Permission Signature |
|-------|------|---------------------|
| `build` | `primary` | Full tool access (default) |
| `plan` | `primary` | `edit: deny`, `bash: deny` — analysis only; edits only within `.opencode/plans/*.md` |
| `general` | `subagent` | Denies `todowrite` |
| `explore` | `subagent` | Read-only: only `grep`, `glob`, `list`, `bash`, `read`, web tools |
| `scout` | `subagent` | Repo cloning + overview |
| `composition` | `primary` (hidden) | System compaction agent |
| `title` | `primary` (hidden) | Title generation |
| `summary` | `primary` (hidden) | Session summary |

### Permission Resolution Priority (high→low)
1. **Session approvals** (SQLite-persisted user choices)
2. **Agent-specific** (`agent.{name}.permission`)
3. **Global config** (`permission` key)
4. **Built-in hardcoded defaults** (e.g., `*.env` = `ask`, `external_directory` = `ask`, `doom_loop` = `ask`)

**Sources**: [opencode.ai/docs/agents#mode](https://opencode.ai/docs/agents#mode), [deepwiki.com/sst/opencode/3.2-agent-system](https://deepwiki.com/sst/opencode/3.2-agent-system), [opencode.ai/docs/permissions](https://opencode.ai/docs/permissions)

---

## §7 Custom Provider Capabilities

### How Granular?

**Very granular.** Three mechanisms:

#### 1. NPM-based Custom Providers
```json
{
  "provider": {
    "omega-fabric": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Omega Provider Fabric",
      "options": {
        "baseURL": "http://localhost:8080/v1",
        "apiKey": "{env:OMEGA_FABRIC_KEY}"
      },
      "models": {
        "gemma-4-31b": { "name": "Gemma 4 31B" },
        "qwen3-4b": { "name": "Qwen 3 4B" }
      }
    }
  }
}
```

#### 2. Plugin-based Providers
```typescript
export const OmegaProvider: Plugin = async (ctx) => {
  return {
    provider: {
      provider: 'omega-fabric',
      models: async () => {
        const fabric = await loadProviderFabric();
        return fabric.models.map(m => ({
          id: m.id,
          name: m.name,
          provider: 'omega-fabric',
        }));
      },
    },
    auth: {
      provider: 'omega-fabric',
      loader: async (auth, provider) => {
        return { apiKey: await resolveFabricKey() };
      },
    },
  };
};
```

#### 3. Model Variants
```json
{
  "provider": { "omega-fabric": { "models": {
    "gemma-4-31b": {
      "variants": {
        "fast": { "temperature": 0.7 },
        "precise": { "temperature": 0.1, "reasoningEffort": "high" }
      }
    }
  }}}
}
```

#### 4. Provider Filters
- `whitelist`: Only these models pass
- `blacklist`: Block these models

### Can we point OpenCode at the Omega Engine's provider fabric?

**Yes, two approaches:**

**A. Direct endpoint** — If the Omega Engine exposes an OpenAI-compatible endpoint:
```json
{
  "omega": { "options": { "baseURL": "http://localhost:8080/v1" } }
}
```

**B. Plugin routing** — Plugin intercepts model selection to route based on entity:
```typescript
"chat.params": async (input, output) => {
  const entity = input.prompt.match(/entity: (\w+)/)?.[1];
  if (entity === 'SEKHMET') output.model = 'qwen3-1.7b'; // Small model
  if (entity === 'SOPHIA') output.model = 'gemma-4-31b'; // Big model
}
```

**Sources**: [opencode.ai/docs/models](https://opencode.ai/docs/models), [opencode.ai/docs/config#provider-specific-options](https://opencode.ai/docs/config#provider-specific-options), [deepwiki.com/sst/opencode/3.3-provider-and-model-configuration](https://deepwiki.com/sst/opencode/3.3-provider-and-model-configuration)

---

## §8 Permission System — Full Reference

### All Permission Keys

| Key | Granular? | Default | Tool(s) Gated |
|-----|-----------|---------|---------------|
| `read` | Path | `allow` (`.env*` denied) | `read` |
| `edit` | Path | `allow` | `edit`, `write`, `apply_patch` |
| `glob` | Pattern | `allow` | `glob` |
| `grep` | Pattern | `allow` | `grep` |
| `list` | No | `allow` | `list` |
| `bash` | Command | `allow` | `bash` |
| `task` | Agent name | `allow` | `task` |
| `skill` | Skill name | `allow` | `skill` |
| `lsp` | No | `allow` | LSP queries |
| `webfetch` | URL | `allow` | `webfetch` |
| `websearch` | No | `allow` | `websearch` |
| `todowrite` | No | `allow` | `todowrite`, `todoread` |
| `question` | No | `allow` | `question` |
| `external_directory` | Path | `ask` | Paths outside worktree |
| `doom_loop` | No | `ask` | Same call repeated 3× |

### Actions

| Value | Behavior |
|-------|----------|
| `"allow"` | Execute without user prompt |
| `"ask"` | Prompt user (once / always for session / reject with feedback) |
| `"deny"` | Block, throw `DeniedError` to model |

### Wildcard/Pattern Rules

- `*` matches zero or more chars
- `?` matches exactly one char
- **Last matching rule wins** — put broad `"*"` first, specifics after
- `~` / `$HOME` expanded in patterns
- Matching is **tool-specific**:
  - `bash`: matches parsed command string (`git status --porcelain`)
  - `read`/`edit`: matches file path
  - `webfetch`: matches URL
  - `task`: matches subagent name
  - `external_directory`: matches directory path
- MCP tools: `"mymcp_*": "deny"` blocks an entire MCP server

### Doom Loop Detection
- Triggers when **same tool call repeats 3 times** with identical input
- Default action: `ask`
- User can provide feedback via `CorrectedError` → sent back to LLM

### Interactive Approval Flow
1. Tool hits `ask` rule
2. `Permission.Service` creates `Deferred` promise
3. Publishes `permission.asked` event on Bus
4. UI renders prompt
5. User responds: `once` | `always` (persisted to SQLite) | `reject` (with optional feedback)
6. `Deferred` resolved → tool continues or `CorrectedError` returned to LLM

### Per-Agent Permission Examples

```json
{
  "agent": {
    "orchestrator": {
      "permission": {
        "bash": { "git *": "allow", "*": "ask" },
        "task": { "*": "deny", "explore": "allow", "reviewer": "ask" },
        "edit": { "*.md": "allow", "*": "deny" }
      }
    }
  }
}
```

### Plugin Hook for Auto-Permission
```typescript
"permission.ask": async (permission, output) => {
  if (permission.type === 'read_file' && permission.path.endsWith('.md')) {
    output.status = 'allow';  // Auto-allow markdown reads
  }
  if (permission.type === 'bash' && permission.command.startsWith('git ')) {
    output.status = 'allow';  // Auto-allow git commands
  }
}
```

**Sources**: [opencode.ai/docs/permissions](https://opencode.ai/docs/permissions), [deepwiki.com/sst/opencode/5.2-permission-system](https://deepwiki.com/sst/opencode/5.2-permission-system)

---

## §9 Compaction System — Full Control

### Config Options

```json
{
  "compaction": {
    "auto": true,      // Auto-compact when context full (default: true)
    "prune": true,      // Remove old tool outputs (default: true)
    "reserved": 10000   // Token buffer during compaction
  }
}
```

### Internal Parameters (from source)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `OUTPUT_TOKEN_MAX` | 32,000 | Reserved for model output |
| `COMPACTION_BUFFER` | 20,000 | Safety buffer |
| `PRUNE_PROTECT` | 40,000 | Only prune if tool output exceeds this |
| `PRUNE_MINIMUM` | 20,000 | Minimum amount to prune |
| `DEFAULT_TAIL_TURNS` | 2 | Recent turns protected from pruning |

### Overflow Detection

```
isOverflow = tokens > (model.context_limit - output_token_max - compaction_buffer)
           = tokens > (model.context_limit - 32000 - 20000)
```

### Pruning Algorithm
1. Scans messages **newest to oldest**
2. Skips last `DEFAULT_TAIL_TURNS` (2) — recent context protected
3. Only prunes if total tool output > 40K AND candidate > 20K tokens
4. Never prunes `skill` tool parts

### Summary Template

The compaction summary captures: **Goal**, **Constraints**, **Progress**, **Key Decisions**, **Next Steps**, **Critical Context** — this maps directly to the Gnosis Preservation Protocol's L1→L2→L3 distillation format.

### Media Stripping on Overflow
When `overflow=true`, media (images, PDFs) are converted to text placeholders to prevent immediate re-overflow.

### Plugin Compaction Hook

```typescript
export const GnosisKeeper: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Read gnosis buffer
      const buffer = await Bun.file("/tmp/omega/gnosis_buffer.md").text();
      
      output.context.push(`## Gnosis State
${buffer}`);

      // Or replace entirely
      output.prompt = `Generate a structured summary with:
Goal, Constraints, Progress, Key Decisions, Next Steps, Critical Context`;
    },
  };
};
```

### Error State
If compaction itself fails (session too large even for compaction agent), a `ContextOverflowError` is attached and the session terminates. This is unrecoverable.

### Can compaction be disabled?
Yes — `"compaction": { "auto": false }`. But context will eventually saturate.

**Sources**: [opencode.ai/docs/config#compaction](https://opencode.ai/docs/config#compaction), [opencode.ai/docs/plugins#compaction-hooks](https://opencode.ai/docs/plugins#compaction-hooks), [deepwiki.com/sst/opencode/2.4-context-management-and-compaction](https://deepwiki.com/sst/opencode/2.4-context-management-and-compaction)

---

## §10 Omega Engine Integration Points (Summary)

| Integration Point | Mechanism | Status |
|-----------------|-----------|--------|
| Entity routing via agent frontmatter | Custom fields `entity:`, `wad:`, `domain:` pass through to agent config | ✅ Proven |
| Gnosis Preservation in compaction | `experimental.session.compacting` plugin hook | ✅ Proven |
| Provider fabric routing | NPM `@ai-sdk/openai-compatible` or plugin `provider` hook | ✅ Proven |
| Subagent fleet management | Write `.md` files + config disk; task permission scoping | ⚠️ Requires restart |
| Soul state injection | `config` plugin hook or compaction hook `output.context` | ✅ Proven |
| Custom tools (soul query, entity list) | `tool` plugin hook with `priority: 1` | ✅ Proven |
| Permission automation for Omega tools | `permission.ask` plugin hook | ✅ Proven |
| Runtime agent creation | No API exists — write `.md` files + signal restart | 🔲 Not possible |
| Agent-to-Agent Protocol | OpenCode ACP (Agent Client Protocol) | 📅 Needs research |
| Cross-session memory persistence | `event` hook listens to `session.compacted` + compaction inject | ✅ Proven |

---

## §11 Key Design Decisions for Omega OpenCode Stack

1. **Compaction is the critical hook** — the `experimental.session.compacting` hook is the single most important integration point for the Gnosis Preservation Protocol. It allows injecting soul state, entity context, and workstream data directly into the compaction summary.

2. **Custom frontmatter is sufficient** — `entity:`, `wad:`, and `domain:` fields in agent YAML frontmatter are passed through without issue. No need for schema extensions.

3. **Task permission scoping** — the `permission.task` key can scope Omega entity subagents to only be callable from specific orchestrator agents.

4. **Plugin-based provider routing** — the provider fabric can be exposed as an OpenAI-compatible endpoint, or a plugin can use the `provider` and `chat.params` hooks for entity-aware model routing.

5. **No runtime agent registration** — a bootstrap process that runs at OpenCode startup should generate `.opencode/agents/*.md` files from entity.yaml definitions.

6. **Auto-permission for trusted patterns** — the `permission.ask` plugin hook can auto-allow Omega-specific patterns (e.g., reading soul files, querying the workbench database).

---

## §12 Sources

| Source | URL |
|--------|-----|
| Official Config Docs | https://opencode.ai/docs/config |
| Official Agents Docs | https://opencode.ai/docs/agents |
| Official Permissions Docs | https://opencode.ai/docs/permissions |
| Official Plugins Docs | https://opencode.ai/docs/plugins |
| Official SDK Docs | https://opencode.ai/docs/sdk |
| Official Tools Docs | https://opencode.ai/docs/tools |
| Official Custom Tools Docs | https://opencode.ai/docs/custom-tools |
| Official Rules Docs | https://opencode.ai/docs/rules |
| Official Models Docs | https://opencode.ai/docs/models |
| Schema URL | https://opencode.ai/config.json |
| DeepWiki: Agent System | https://deepwiki.com/sst/opencode/3.2-agent-system |
| DeepWiki: Config Loading | https://deepwiki.com/sst/opencode/3.1-configuration-loading-and-merging |
| DeepWiki: Compaction | https://deepwiki.com/sst/opencode/2.4-context-management-and-compaction |
| DeepWiki: Permission System | https://deepwiki.com/sst/opencode/5.2-permission-system |
| DeepWiki: Plugin System | https://deepwiki.com/sst/opencode/7.3-plugin-system |
| DeepWiki: Provider Config | https://deepwiki.com/sst/opencode/3.3-provider-and-model-configuration |
| Community Config Ref | https://learnopencode.com/en/appendix/config-ref |
| Plugin Dev Guide (Gist) | https://gist.github.com/rstacruz/946d02757525c9a0f49b25e316fbe715 |
| OCX Agents Reference | https://ocx.kdco.dev/docs/reference/agents |
| Zenn Config Guide | https://zenn.dev/is0383kk/articles/12223c665775f2 |
