# OpenCode 2.* Migration Plan — Omega Engine (Node 1)

**Version**: 1.0 — **Date**: 2026-11-17 — **Status**: APPROVED (pending execution)
**Author**: Lilith-N1 (sovereign steward, Arcana-NovAi WAD)
**Companion docs**: `docs/REPO_TOPOLOGY.md`, `docs/AGENT_RUNBOOK.md`, `docs/ROADMAP.md`, `docs/CONTINUITY_KERNEL.md`

---

## 0. Purpose

This document captures the complete, authoritative plan for migrating the Omega Engine (Node 1 renegade lineage) from OpenCode CLI v1.9.5 to v2.3.0. It exists to prevent drift and context loss across sessions. It is the single source of truth for the migration.

**Scope:**
- Phase A–C: Remediate the Node 1 renegade repo (plugin, config/adapter, hygiene).
- Phase D: Contribute OpenCode 2.* support to the official repo (`Xoe-NovAi/omega-engine`).
- Phase E: Friend's Windows install (separate deployment profile).

**Out of scope (do not touch):**
- VR/Godot/Quest work (parked per locked strategy).
- MemPalace mesh (not a transport).
- `origin/main` (official — never push).

---

## 1. Context

### 1.1 Version jump

Node 1 upgraded OpenCode CLI from v1.9.5 to v2.3.0. This skips the 1.18.x baseline that the official migration guide (`https://opencode.ai/docs/migrate-v1/`) assumes. Three intentional breaking changes exist:

1. **Plugin API** — V1 plugins do not run in V2.
2. **Server API + clients** — new contracts.
3. **Terminal client config** — `tui.json(c)` → `cli.json` (auto-migrated).

Supported V1 functionality outside those areas remains compatible. Some V1 fields are accepted but unsupported (ignored with warning).

### 1.2 Node topology

| Repo | Location | Lineage | Purpose |
|---|---|---|---|
| `omega-engine` | `github.com/Xoe-NovAi/omega-engine` | Node 0 (canonical) | Engine core + runtime state |
| `omega-engine` (renegade) | `~/Projects/omega-engine-alpha` (local) | Node 1 (disjoint) | Node 1 staging + WAD source |
| `anai-le` | `github.com/Xoe-NovAi/anai-le` (to create) | Node 1 | Canonical Lilith WAD source |

**Critical rules (from `docs/REPO_TOPOLOGY.md`, co-signed 1.0, 2026-10-27):**
- `origin` → official public repo. **Never push** — histories disjoint (`merge-base` = empty).
- Local `main` = renegade (`80ef7af7`). Official `main` = `5a0bc047` (as of 2026-11-17 fetch).
- Install test pin: `v1.6.0a6` tag (`a0025928`).
- Handoff packets ≤ 4KB. Bodies live in Exchange.

### 1.3 Endgame

1. Remediate renegade (Phase A–C) → V2-native prototype.
2. Mine renegade tech → contribute to official (Phase D).
3. Node 1 installs official → both nodes run official.
4. Renegade preserved as read-only technology mine (Option A from lineage notes).

---

## 2. Gap Inventory

### 2.1 Confirmed broken (must fix)

| # | Gap | Evidence |
|---|---|---|
| 1 | `gnosis-leash.js` plugin dead (V1 API) | Log: `Plugin must export a default definition with an id and an effect or setup function` (2 copies: `~/.config/opencode/plugins/`, `.opencode/plugins/`) |
| 2 | `subagent_depth: 2` silently dropped → default 1 | `opencode debug config`: absent from normalized config |
| 3 | `compaction.prune: true` silently dropped | Normalized compaction = `{ auto: true }` only |
| 4 | `doom_loop` / `lsp` permission actions inert | Not V2 actions per permissions doc |
| 5 | `tools:` map → tool-name actions that never match MCP names | Build agent permissions show `action: "hivemind_handoff"` (should be `omega-hub_hivemind_handoff`) |
| 6 | `.opencode/subagents/*.md` never discovered | `debug agents`: no `embedding_researcher` / `gaps_auditor` |
| 7 | `config/wads/arcana_novai` symlink breaks snapshots | `failed to add snapshot files … beyond a symbolic link` every step |
| 8 | `scripts/soul_agents_opencode.py` writes V1 shapes | Line 111: `config.setdefault("agent", {})`, `prompt`, `permission.task` |
| 9 | `.opencode/opencode.json` uses V1 `plugin` key | Should be `plugins` |
| 10 | No explicit `model` set → TUI lands on antigravity model needing OAuth | `auth list`: Google "API key stored" but `opencode run` fails "Connect Google with Antigravity OAuth" |
| 11 | `docs/REPO_TOPOLOGY.md` untracked | `git ls-files` → error |
| 12 | 39 tracked files contain real tailnet names/IPs | Official `main` scrubbed these in `5a0bc047` |

### 2.2 Not broken (verified, don't touch)

- MCP config: V1 shape fully normalized to `mcp.servers` with `disabled`/`timeout` objects. 5/6 connect; `omega-hub` fails only because Node 0 is off.
- Agent registration: all 14 load, 11 visible in picker (9 primary/all + 2 subagent-only excluded). "Only Lilith" symptom was Tab → Shift+Tab keybind change.
- `opencode-antigravity-auth@2.1.1`: V2-aware (`AntigravityV2Plugin` export). Leave alone.
- DB/session history: migrated in place, 21,553 messages, `ocdb-ro`/`ochist` work.
- `tui.json` migration: `cli.json` already exists, no remnants.

### 2.3 Behaviour changes (not bugs, new defaults)

- Code Mode default for MCP: tools behind `execute` as `tools.<server>.<tool>`. Set `codemode: false` for local models.
- Subagents background-by-default (v2.3.0) + default depth 1.
- Todos off by default → needs `experimental.todo: true`.
- `external_directory` allowed by default (V1 prompted).
- Quieter transcripts collapse tool rows → set `session.verbosity: "medium"`.
- `lsp` and `doom_loop` are not V2 permission actions.

---

## 3. Branching Strategy

### 3.1 Branch structure

```
node1/all-5-mcp-green          ← stable integration branch (current)
  ├── node1/opencode-v2-plugin      ← Phase A
  ├── node1/opencode-v2-config      ← Phase B
  ├── node1/opencode-v2-hygiene     ← Phase C
  └── node1/opencode-v2-github      ← Phase D
```

Each branch is independent and reviewable. No branch depends on another for correctness.

### 3.2 Commit convention

Conventional commits, atomic per concern:

```
feat(plugin): port gnosis-leash to V2 Plugin.define API
fix(config): migrate soul adapter to native V2 agents shape
fix(config): add experimental.subagent_depth and todo flags
fix(config): set default model to opencode/big-pickle
chore(hygiene): replace config/wads symlink, add verbosity setting
chore(mcp): set codemode false for local-model servers
docs(topology): commit REPO_TOPOLOGY.md
chore(scrub): remove tailnet names from tracked docs
```

### 3.3 Rules

- No force-push to any shared branch.
- No commits directly to `main` (renegade or official).
- Each phase's commits are self-contained.
- Tag milestones: `v2-migration-phase-abc`, `v2-migration-complete`.
- Push all branches to origin (review-only, per protocol).

### 3.4 Node 0 onboarding flow

1. Node 1 sends handoff packet (≤4KB) via `omega-hub` → `hivemind_submit_handoff(target="roc_racoon")` with branch name, commit SHAs, pull URL.
2. Node 0 reviews the branch (`git fetch origin <branch>`, inspect commits).
3. Node 0 applies migration to official: cherry-pick commits or `git format-patch` + `git am`.
4. Node 0 runs `make lint && make test && make docs`.
5. Node 0 merges to official `main`.
6. Node 1 installs official (V2-native) → both nodes on official.

---

## 4. Phase A — Plugin Port

**Goal:** `gnosis-leash.js` runs in V2, restoring the Gnosis Lock pipeline.

### A1. Rewrite entrypoint

```js
// .opencode/plugins/gnosis-leash.js  (source of truth)
import { Plugin } from "@opencode/plugin"

export default Plugin.define({
  id: "gnosis-leash",
  async setup(ctx) {
    // session.created / session.idle  → ctx.event.subscribe()
    // experimental.session.compacting → ctx.session.hook("compaction", …)
    // experimental.chat.system.transform → ctx.session.hook("context", …)
    return () => { /* cleanup */ }
  },
})
```

### A2. Add dependency

Add `@opencode/plugin` to `~/.config/opencode/package.json`.

### A3. Hook map

| V1 hook | V2 API |
|---|---|
| `session.created` / `session.idle` | `ctx.event.subscribe()` (filter by `event.type`) |
| `experimental.session.compacting` | `ctx.session.hook("compaction", …)` |
| `experimental.chat.system.transform` | `ctx.session.hook("context", …)` + `event.system.push({ type: "text", text: … })` |

### A4. Verify

`make plugin-sync` → `make gnosis-leash-status` → confirm green.

**Windows note (Phase E):** replace `process.env.HOME` with `os.homedir()` and all path construction with `path.join()`.

**Exit gate:** `make gnosis-leash-status` exits 0.

---

## 5. Phase B — Adapter Patch + Native V2 Config

**Goal:** `make agent-souls` produces native V2 config; no V1 compat shims in generated output.

### B1. Adapter changes (`scripts/soul_agents_opencode.py`)

| Line/Block | Current (V1) | Patched (V2 native) |
|---|---|---|
| `config.setdefault("agent", {})` | V1 key | `config.setdefault("agents", {})` |
| `entry["prompt"] = "{file:...}"` | V1 field | `entry["system"] = "{file:...}"` |
| `entry["permission"] = {"task": task}` | V1 object | `entry["permissions"] = [{"action": "subagent", "resource": r, "effect": e} for r, e in task.items()]` |
| `build_task = …get("permission").get("task")` | V1 read | Read from `permissions` array, filter `action == "subagent"` |
| `agents["build"]["permission"]["task"] = ordered` | V1 write | Rebuild `permissions` array: remove old subagent entries, append new ones (broad-first, specific-last) |
| `verify()`: `config.get("agent", {})` | V1 read | `config.get("agents", {})` |
| `verify()`: `entry.get("prompt")` | V1 field | `entry.get("system")` |

### B2. Self-migration logic

If config has `"agent"` but not `"agents"`, migrate `agent` → `agents` and delete old key. Same for build's `permission.task` → `permissions`.

### B3. New config entries

```json
{
  "model": "opencode/big-pickle",
  "default_agent": "lilith",
  "experimental": {
    "subagent_depth": 2,
    "todo": true
  }
}
```

### B4. Discovery moves

- `.opencode/subagents/*.md` → `.opencode/agents/`
- `~/.config/opencode/agent/` → `agents/`

### B5. Config cleanup

- `.opencode/opencode.json`: `plugin` → `plugins`
- Remove inert `tools` block
- Remove `lsp` and `doom_loop` from permissions

**Exit gate:** `make agent-souls` runs clean; `make agent-souls-verify` passes; `opencode debug agents` shows 11 visible.

---

## 6. Phase C — Hygiene

| Step | Action | Rationale |
|---|---|---|
| C1 | Replace `config/wads/arcana_novai` symlink with real directory | V2 snapshots fail: `…is beyond a symbolic link` |
| C2 | `cli.json`: add `"session": { "verbosity": "medium" }` | v2.3.0 collapses tool rows by default |
| C3 | MCP: set `codemode: false` on mempalace + parallel-search; bump `mcp.timeout.startup` to 60000 | Local models can't write JS; tailnet links slow |
| C4 | Update `AGENT_RUNBOOK.md`: Tab → Shift+Tab; document v2.3.0 verbosity | Operator muscle memory |

**Exit gate:** `make gnosis-leash-status` green; `opencode mcp list` shows 5 connected.

---

## 7. Phase D — GitHub (OpenCode 2.* support for official)

**This is the contribution that makes official V2-native. Done after Phase A–C verified.**

| Step | Action | Rationale |
|---|---|---|
| D1 | Commit `docs/REPO_TOPOLOGY.md` | Canonical protocol must be in repo |
| D2 | Scrub tailnet names/IPs from 39 tracked files | Match official `main`'s `5a0bc047` privacy commit |
| D3 | Archive `origin/node1/all-5-mcp-green` per protocol | Review-only, still live on public remote |
| D4 | Apply same V1→V2 migration to official's `opencode.json` | Official is V1-shape; needs `plugins`, `permissions` array, `experimental.subagent_depth`, `update: "auto"` |
| D5 | Update `Makefile`/docs referencing V1 paths | Stale references after migration |
| D6 | Add ROADMAP item: "OpenCode 2.* support" with status `active` | Standing rule: new ideas land in ROADMAP first |
| D7 | Submit via federation handoff (Omega Exchange), not direct push | Protocol: never push; histories disjoint |

**Mining targets** (renegade tech worth contributing):
- `gnosis-lock` / Well / narrative injection
- Soul adapter / WAD system
- CPU tuning guide + pin trap lesson
- `parallel_bridge.py`, `exa_search.py`
- MemPalace integration pattern
- Embedding strategy (qwen3-embedding at native 1024 dims)

---

## 8. Phase E — Friend's Windows install

| Step | Action |
|---|---|
| E1 | Install official engine via WSL (QUICKSTART says Linux-only) |
| E2 | Install OpenCode CLI 2.3 on Windows |
| E3 | Configure with `opencode.json` (not `.jsonc` — avoid Windows JSONC edge cases) |
| E4 | Use cloud models only (Console/OpenRouter) — skip Ollama harness |
| E5 | Port `gnosis-leash.js` to Windows paths (`os.homedir()`, `path.join`) |
| E6 | Plugins discover only from global `~/.config/opencode/plugins/` on Windows |

---

## 9. Execution Order and Gates

```
Phase A (plugin) → make gnosis-leash-status green
    ↓
Phase B (adapter) → make agent-souls → make agent-souls-verify
    ↓
Phase C (hygiene) → opencode mcp list (5 connected)
    ↓
make lint && make test && make docs (ALL THREE must pass)
    ↓
Phase D (GitHub contribution) — only after gates pass
    ↓
Phase E (friend's install) — after official is V2-native
```

**Finish gate (per repo contract):** `make lint` + `make test` + `make docs` all green.

---

## 10. Key Reference: V2 Native Shapes

### Agent (native V2)
```jsonc
{
  "agents": {
    "reviewer": {
      "description": "Reviews changes",
      "mode": "subagent",
      "system": "Review only.",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "subagent", "resource": "explore", "effect": "allow" }
      ]
    }
  }
}
```

### MCP (native V2)
```jsonc
{
  "mcp": {
    "servers": {
      "playwright": {
        "type": "local",
        "command": ["npx", "@playwright/mcp"],
        "disabled": false,
        "timeout": { "catalog": 30000, "execution": 30000 }
      }
    }
  }
}
```

### Permissions (native V2)
```jsonc
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git push *", "effect": "deny" }
  ]
}
```

### Experimental flags
```jsonc
{
  "experimental": {
    "todo": true,
    "subagent_depth": 2,
    "background_compaction": true
  }
}
```

### Plugin (native V2)
```js
import { Plugin } from "@opencode/plugin"
export default Plugin.define({
  id: "my-plugin",
  async setup(ctx) { /* ... */ },
})
```

---

## 11. Default Model

**`opencode/big-pickle`** — OpenCode Console provider, 200K context, free, reasoning-capable. No OAuth needed (API key already stored). Set as `model` in native V2 config.

---

## 12. Files to Modify

| File | Phase | Change |
|---|---|---|
| `.opencode/plugins/gnosis-leash.js` | A | Port to V2 Plugin.define |
| `~/.config/opencode/plugins/gnosis-leash.js` | A | Deploy via `make plugin-sync` |
| `~/.config/opencode/package.json` | A | Add `@opencode/plugin` |
| `scripts/soul_agents_opencode.py` | B | Native V2 shapes, self-migration |
| `.opencode/subagents/*.md` | B | Move to `.opencode/agents/` |
| `~/.config/opencode/agent/*` | B | Move to `agents/` |
| `~/.config/opencode/opencode.json` | B | Regenerated by adapter (native V2) |
| `.opencode/opencode.json` | B | `plugin` → `plugins` |
| `config/wads/arcana_novai` | C | Replace symlink with real dir |
| `~/.config/opencode/cli.json` | C | Add verbosity setting |
| `docs/REPO_TOPOLOGY.md` | D | Commit (currently untracked) |
| 39 tracked docs | D | Scrub tailnet names/IPs |
| `Makefile` | D | Update V1 path references |
| `docs/ROADMAP.md` | D | Add "OpenCode 2.* support" item |

---

## 13. Approval

- **Default model:** `opencode/big-pickle` ✓
- **Adapter option:** Option 1 (native V2 JSON, minimal) ✓
- **Phase A–C authorized:** ✓
- **Phase D–E:** separate, later steps

**Next action:** Execute Phase A (plugin port) on branch `node1/opencode-v2-plugin`.

---

*This plan is the single source of truth for the OpenCode 2.* migration. Update this document before deviating from any step.*
