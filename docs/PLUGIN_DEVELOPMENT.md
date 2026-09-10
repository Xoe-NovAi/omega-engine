# Plugin Development — OpenCode + gnosis-leash Pattern

How OpenCode plugins (the "hooks" mechanism) work, and how to extend
`gnosis-leash.js` or write your own.

## Context

OpenCode's documented "hooks" are implemented as **plugin events** (not a
`hooks` config key). Verified in `@opencode-ai/plugin` and `@opencode-ai/sdk`
type definitions (v1.18.30). HP's "hooks on every open/close" = session events.

**Plugin locations** (auto-loaded at startup):
- Global: `~/.config/opencode/plugins/`
- Project: `.opencode/plugins/`
- npm: `"plugin": ["pkg-name"]` in `opencode.json`

A plugin is an ESM module exporting named plugin functions. Each receives a
context object `{ project, client, $, directory, worktree }` and returns a
hooks object.

## The event surface (verified locally)

**Lifecycle:** `session.created`, `session.idle`, `session.updated`,
`session.deleted`, `session.compacted`, `session.status`, `session.error`

**Live stream:** `session.next.*` (steps, text delta, tool called/failed/
success, model switch, reasoning, compaction started/delta/ended, revert staged/
committed/cleared, retried, synthetic, prompt admitted/prompted, context updated)

**Hooks (return object keys):**
- `event: async ({ event }) => {}` — catches all event types
- `"tool.execute.before"` / `"tool.execute.after"`
- `"shell.env"`
- `"permission.ask"`
- `"command.execute.before"`
- `experimental.chat.system.transform` — append to every system prompt
- `experimental.chat.messages.transform`
- `experimental.session.compacting` — **fire before compaction summary generation**; inject `output.context` or replace `output.prompt`
- `experimental.compaction.autocontinue`

## Pattern: gnosis-leash.js

Installed at `~/.config/opencode/plugins/gnosis-leash.js`.

```js
export const GnosisLeash = async ({ project, client, $, directory }) => {
  return {
    event: async ({ event }) => {
      const type = event?.type || "";
      if (type === "session.created")   appendEvent({ kind: "session.created", ... });
      if (type === "session.idle")      appendEvent({ kind: "session.idle", ... });
      if (type === "session.compacted") appendEvent({ kind: "session.compacted", ... });
    },
    "experimental.session.compacting": async (_, output) => {
      output.context = (output.context || []).concat([
        "## ⬡ GNOSIS LEASH — temple context",
        ...readIndexRules(),   // WanderGround INDEX.md rules
      ]);
      return output;
    },
    "experimental.chat.system.transform": async (_, output) => {
      output.system = (output.system || "") + "\n\n" + rules;
      return output;
    },
  };
};
```

**Golden rules for plugin code:**
- Never throw — wrap every hook body in try/catch; a plugin failure must not
  break the session.
- Keep hooks cheap (sync fs reads OK; no network in `event`).
- State goes to a JSONL timeline (append-only), not to stdout.
- `$` is Bun's shell API — available for subprocess work in hooks if needed.

## Testing a plugin

```bash
# Load check (server starts, plugin must not crash):
timeout 10 opencode serve

# Watch the timeline while you use the TUI:
tail -f ~/.config/opencode/plugins/state/gnosis-events.jsonl
# In another terminal: opencode → send a message → /compact
```

## Your hook ideas map

| Want to happen | Use |
|----------------|-----|
| Auto-log session start | `session.created` |
| Auto-log session end | `session.idle` |
| Inject context into compaction | `experimental.session.compacting` |
| Add rules to system prompt | `experimental.chat.system.transform` |
| Guard `.env` reads | `tool.execute.before` |
| Add env vars to every shell | `shell.env` |
| Notify when done | `session.idle` + `$` notify-send |
| Track model switches mid-session | `session.next.model.switched` |