# R_PLATFORM_EXPERTISE_WEB_HARDENING_20260826

**AP Token**: AP-JEM-v1.0.0
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ PLATFORM-WEB-HARDENING

**Date**: 2026-08-26
**Consumer**: grokster (`data/entities/grokster/kb/`)
**Method**: Jem 3-phase pipeline (Discovery → Synthesis → Verification). Web-first; local repo had zero coverage on Priority-1 targets.
**Confidence scale**: `verified` (primary source, code or official doc read directly) / `multi-source` (≥2 independent sources agree) / `single-source` / `unresolved`.

---

## Executive Summary

All five undocumented OpenCode targets are now **filled from primary sources** (official docs fetched 2026-08-25 vintage + source code on `dev` branch). Headline findings:

1. **Fork ambiguity resolved**: sst/opencode → anomalyco/opencode is a *rename* (Jan 2, 2026), not a fork; vendor is Anomaly Innovations (ex-SST team).
2. **`experimental.session.compacting`** semantics fully specified: `output.context.push()` appends; `output.prompt =` fully replaces (context then ignored). Companion event `session.compacted {sessionID}`.
3. **`subagent_depth`** (default 1) counts depth by walking `parentID` chains; at-limit `task` calls fail with an agent-visible error. The real nesting gate is the explicit `task` permission rule — and enabling it via global config or frontmatter `tools:{task:true}` has produced 600+ session runaway recursions in the wild.
4. **Keybinds live in `tui.json`, not opencode.json** — full default map captured incl. `variant_cycle` (ctrl+t), command palette (ctrl+p), subagent child/parent navigation.
5. **Snapshots**: separate internal Git object DB under `~/.local/share/opencode/snapshot/`; `snapshots:false` disables; `/undo` has four documented hazard classes (stale trees, nested repos, non-git false success, stale-state restore).
6. **`opencode db [query] --format json|tsv`** + `db path` confirmed; `/global/event` SSE confirmed; **`OPENCODE_SESSION_ID` is NOT in the official env table** → treat as unofficial internal behavior.
7. **Version state**: latest v1.18.23 (Aug 25, 2026); a V2 rewrite with a new plugin hook API is in flight upstream — pinned-binary plugin code should stay on V1 hooks until a deliberate migration.
8. Priority-2 platforms filled: Codex CLI (sandbox/approval dials, AGENTS.md 32KiB, config.toml), Claude Code (CLAUDE.md hierarchy + 200-line load cap, subagent memory scopes, depth=1 Task), VS Code Copilot (instruction-file taxonomy verified from official docs; AGENTS.md + CLAUDE.md both read natively).
9. AGENTS.md is now Linux Foundation-governed (AAIF, Dec 2025), 60k+ repos — grokster's standard thesis validated; new watch item: OpenAI Agent Plugins spec (Aug 6, 2026).
10. Version-pinning best practice converges on what the fleet already does; formalize as env version-matrix + session-version tagging + drain-before-upgrade.

Verdict table (Priority-1 targets):

| # | Target | Verdict |
|---|---|---|
| 1 | Hook event payload schemas | **FILLED** (verified official + multi-source payloads) |
| 2 | `subagent_depth` semantics | **FILLED** (verified from source) |
| 3 | TUI keybind/command surface | **FILLED** (verified official) |
| 4 | Snapshot/revert system | **FILLED** (architecture verified + hazards multi-source) |
| 5 | `opencode db` / OPENCODE_SESSION_ID / SSE | **FILLED** (OPENCODE_SESSION_ID runtime behavior = unresolved caveat) |

---

## §1 OpenCode Deep Fill — Five Undocumented Targets

### §1.0 Fork Ambiguity Resolution (prerequisite)

**VERDICT: NOT A FORK — a rename.** The canonical repository is now **`github.com/anomalyco/opencode`** (default branch `dev`). Commit `3c41e4e8f12b7f06258490bb7a85388de1eca381` ("chore: rename repo references from sst/opencode to anomalyco/opencode", PR #6687, 2026-01-02) migrated all references. The vendor is **Anomaly Innovations** (anoma.ly) — the same team formerly known as SST (Serverless Stack); Jay V (CEO), Frank Wang (CTO), Dax Raad, Adam Elmore. `opencode.ai` docs footer now reads "© Anomaly" with edit-links pointing at `anomalyco/opencode/edit/dev/...`. Community docs (e.g. joshuadavidthomas/opencode-plugins-manual) still anchor source links to `sst/opencode` commit SHAs — those SHAs remain valid history in the renamed repo. npm package remains `opencode-ai`. No action needed beyond updating KB URLs; any doc claiming a "fork split" is wrong (the 2025 opencode-ai/Charm split that produced Crush is a *different*, earlier event).

Confidence: **verified** (official docs footer + rename commit + third-party corroboration).

---

### §1.1 Hook Event Payload Schemas (Target 1) — FILLED

**Canonical source**: official Plugins doc, https://opencode.ai/docs/plugins/ (last updated 2026-08-25); community cross-ref: joshuadavidthomas/opencode-plugins-manual `docs/07-events.md` (source-anchored to sst/opencode commit `3efc95b`). Best live ground truth: OpenAPI spec at `http://127.0.0.1:4096/doc` on any running instance.

**Plugin function context**: `async ({ project, client, $, directory, worktree }) => ({ ...hooks })`. Types from `@opencode-ai/plugin`. Load order: global config plugins → project config plugins → global plugin dir (`~/.config/opencode/plugins/`) → project dir (`.opencode/plugins/`). npm plugins auto-installed via Bun into `~/.cache/opencode/node_modules/`.

**Hook signatures (input/output pairs)**:

| Hook | Input | Output (mutable) | Notes |
|---|---|---|---|
| `event` | `{ event: { type, properties } }` | — | Wildcard bus subscription; filter by `event.type` |
| `chat.message` | message parts | `output.parts` | Intercept before LLM |
| `chat.params` | — | `output.temperature`, `topP`, … | LLM parameter override |
| `tool.execute.before` | `{ tool, args, sessionID }` (callID also present per event schema) | `output.args` | Throwing blocks execution (canonical `.env` guard pattern) |
| `tool.execute.after` | `{ tool, args, result }` (+sessionID/callID/title/output/metadata per event schema) | mutable output | Runs post-execution |
| `permission.ask` | `{ tool, args }` | `output.status = "approved"\|"denied"` | Override permission decisions |
| `experimental.session.compacting` | — | `output.context: string[]`, `output.prompt?: string` | See below |
| `shell.env` | `{ cwd }` | `output.env` (map) | Injected into ALL shell exec (AI tools + user terminals) |
| `tool.definition` | — | description mutation | Can rewrite built-in tool descriptions |

**`experimental.session.compacting` exact semantics (verified from official doc examples)**:
- Fires before the LLM generates the continuation summary.
- `output.context.push("...")` appends domain context to the default compaction prompt.
- Setting `output.prompt = "..."` **completely replaces** the default compaction prompt; when set, `output.context` is ignored.
- Companion *event* (not hook): `session.compacted` → payload `{ sessionID: string }`, fired after compaction completes. Defined in `packages/opencode/src/session/compaction.ts`.
- Note: `session.idle` is deprecated in favor of `session.status` (`{ sessionID, status }`) but still emitted.

**Event payload shapes (selected, verified against two independent sources)**:

| Event | Payload |
|---|---|
| `session.created/updated/deleted` | `{ info: SessionInfo }` |
| `session.error` | `{ sessionID?: string, error: object }` |
| `session.diff` | `{ sessionID, diff: FileDiff[] }` where FileDiff = `{ file, before, after, additions, deletions }` |
| `message.part.updated` | `{ part: Part, delta?: string }` |
| `file.edited` | `{ file: string }` (agent edits only; watcher event covers external changes) |
| `command.executed` | `{ name, sessionID, arguments, messageID }` |
| `tui.toast.show` | `{ title?, message, variant, duration? }` |
| `installation.updated` | `{ version }`; `installation.update.available` → `{ version }` |
| `pty.exited` | `{ id, exitCode }` |
| `vcs.branch.updated` | `{ branch?: string }` |

Confidence: hooks table & compaction semantics = **verified** (official docs, fetched 2026-08-26). Payload table = **multi-source** (official event list + plugin-manual source anchors + airgap-aiops telemetry-validated schemas; minor field drift possible across versions).

---

### §1.2 `subagent_depth` Config Semantics (Target 2) — FILLED

**Primary source**: `packages/opencode/src/tool/task.ts` on `anomalyco/opencode@dev` (read via GitHub), corroborated by issues #17721/#18100/#36878/#39112.

**Mechanism (from source)**:
```ts
const parent = yield* sessions.get(ctx.sessionID)
let current = parent; let depth = 0
while (current.parentID) { depth++; current = yield* sessions.get(current.parentID) }
if (depth >= (cfg.subagent_depth ?? 1)) {
  return Effect.fail(new Error(`Subagent depth limit reached (${cfg.subagent_depth ?? 1}). Increase "subagent_depth" to allow nested subagents.`))
}
```

Findings:
1. **Default = 1** (`cfg.subagent_depth ?? 1`). Top-level key in `opencode.json` (not nested under agent).
2. **Depth counting**: walk `parentID` chain from current session upward; root session = depth 0. A depth-N session may spawn while `depth < subagent_depth`. So `subagent_depth: 2` ⇒ root(0)→child(1)→grandchild(2); grandchild cannot spawn.
3. **Behavior at limit**: the `task` tool call FAILS with the error above (agent-visible, recoverable — agent told to do work directly). Not silent.
4. **Permission interplay — the real gate is `canTask`**: the task tool is stripped from child sessions unless the target agent has an explicit `task` permission rule (`agent.permission.some(rule => rule.permission === "task")`). Three ways this becomes true: (a) global `"task": "allow"` propagates to all agents; (b) agent frontmatter `tools: { task: true }` silently normalizes to `permission.task: "allow"` (via `normalize()` in `config/agent.ts`); (c) explicit per-agent permission block. Wildcard `"*": "allow"` alone does NOT enable nesting.
5. **Runaway-recursion hazard (multi-issue confirmed)**: with any of the three triggers above there is NO hard runtime ceiling other than `subagent_depth` itself — #18100 recorded 612 nested sessions in 73 min (stopped only by credit exhaustion); #18100's author hit 20 levels / 47 sessions via pure model re-delegation. `steps` does NOT bound the tree (fresh counter per session); `doom_loop` doesn't see cross-session recursion. Issue #36878 confirms as of v1.17.20/dev there is still no same-agent cycle guard.
6. **Known bug at depth ≥2**: "ask" permissions inside nested subagents never surface to the user → session stalls (#39112, open, v1.18.7; family: #13715, #30635, #24644). Fleet implication: treat `subagent_depth ≥ 2` as unstable until that family closes.
7. Background subagents require `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`.
8. Community mitigation plugins exist if pinning old versions: `opencode-subagent-depth-limit` (maxDepth default 2, fail-closed option) and Opencode-Nested-Subagents-Plugin.

Confidence: mechanism/limit-behavior = **verified** (source code). Hazard history = **multi-source** (4 issue threads). Depth≥2 ask-stall = **single-source** (open issue, reproduced by reporter).

---

### §1.3 TUI Keybind / Command Surface (Target 3) — FILLED

**Primary source**: https://opencode.ai/docs/keybinds/ (updated 2026-08-25).

1. **Keybinds live in a SEPARATE file: `tui.json`** (schema `https://opencode.ai/tui.json`), NOT `opencode.json`. Overridable via `OPENCODE_TUI_CONFIG` env. Top-level keys seen: `leader_timeout` (default **2000 ms**), `keybinds`.
2. **Leader key**: default `<leader>` = `ctrl+x`; most actions are two-stroke leader sequences. Subagent navigation deliberately bypasses leader: `session_child_first` `<leader>down`, `session_child_cycle` `right`, `session_child_cycle_reverse` `left`, `session_parent` `up`.
3. **Key surfaces of fleet relevance** (defaults):
   - `command_list` = `ctrl+p` (the command palette)
   - `variant_cycle` = `ctrl+t`; `variant_list` = none — variant cycling is a first-class TUI action
   - `model_list` `<leader>m`, `model_provider_list` `ctrl+a`, `model_cycle_recent` `f2` / reverse `shift+f2`
   - `agent_list` `<leader>a`, `agent_cycle` `tab` / reverse `shift+tab`
   - `session_compact` `<leader>c` (manual compaction trigger), `session_new` `<leader>n`, `session_list` `<leader>l`, `session_timeline` `<leader>g`, `session_fork` none-by-default, `session_interrupt` `escape`
   - `messages_undo` `<leader>u`, `messages_redo` `<leader>r` (drives the snapshot revert system, §1.4)
   - `messages_copy` `<leader>y`, `messages_toggle_conceal` `<leader>h`
   - `which_key_toggle` `ctrl+alt+k` (chord-discovery UI exists)
   - Input editing: full emacs-style set (`input_line_home` ctrl+a, `input_delete_to_line_end` ctrl+k, …), `input_newline` = `shift+return,ctrl+return,alt+return,ctrl+j`
4. **Binding value grammar**: comma-separated string OR array OR object `{ key, event?, preventDefault?, fallthrough? }`. Disable with `"none"` or `false`.
5. **Windows deltas**: `input_undo` gains `ctrl+z`; `terminal_suspend` forced off (no POSIX suspend).
6. Desktop app prompt input has a separate built-in Readline/Emacs shortcut set, currently NOT configurable via opencode.json.

Confidence: **verified** (official docs page fetched in full).

---

### §1.4 Snapshot / Revert System (Target 4) — FILLED (with hazard warnings)

**Primary sources**: V2 snapshots doc https://opencode.ai/v2/docs/snapshots ("Undo"); server API docs (`/session/:id/revert`, `/unrevert`, `/session/:id/diff`); SDK-level audit (K-Arthur/opencode-harness, 2026-06-15, against `@opencode-ai/sdk` 1.17.7); bug issues #10287/#5910/#30065/#38672.

**Architecture**:
- Snapshots are **enabled by default**; disable with `"snapshots": false` in opencode.json. Disabling does not delete stored snapshots.
- Uses a **separate internal Git object database inside the OpenCode data directory** (`~/.local/share/opencode/snapshot/<project-hash>/`) — does NOT create commits, move branches, or touch your repo's index. Requires the project to be a Git repo; without Git, conversation rollback still works but no file state is restored.
- Capture points: immediately before each model step and after each cleanly completed step; changed paths recorded on the assistant message.
- Scope: session's active directory only; tracked files + untracked-not-ignored files; single untracked file > **2 MiB excluded**; ignored files, paths outside active dir, Git metadata changes never captured.
- **Message part types**: `SnapshotPart` exists alongside `PatchPart`; step parts carry `.snapshot` hashes (`StepStart/StepFinish.snapshot`). Revert API body: `{ messageID, partID?, snapshot? }`.
- Restoration semantics: selects a conversation boundary, restores only paths attributed to cleanly completed assistant steps after it; created files removed if absent earlier; "reverted" messages leave the active projection but remain in durable history (not secure erasure).
- Redo = `POST /session/:id/unrevert` (restores all reverted messages). Diff query: `GET /session/:id/diff?messageID=` → `FileDiff[]`.

**Known hazards (fleet-relevant)**:
- #10287 (Windows): undo restored weeks-old state, silently deleted ~1300 lines of committed code; workaround `git checkout -- .`. Closed, but defines the failure-class severity.
- #5910: external (non-OpenCode) edits make snapshot tree stale → undo captures/restores stale hash.
- #30065 (open): nested independent git repos under the launch dir are NOT protected by /undo — silent partial revert.
- #38672: non-Git directory → /undo reports success but reverts nothing.
- KB rule of thumb: **never trust /undo on a dirty worktree; commit before long agent runs.**

Confidence: architecture/config = **verified** (official V2 doc + server docs). Part-type details = **multi-source**. Hazard list = **multi-source** (issue tracker).

---

### §1.5 `opencode db` CLI, `OPENCODE_SESSION_ID`, `/global/event` SSE (Target 5) — FILLED (one caveat)

**`opencode db` (verified, official CLI docs)**:
```
opencode db [query]        # run a query against the session database
  --format json|tsv         # output format
opencode db path           # print the database path
```
DB lives at `~/.local/share/opencode/opencode.db` (SQLite — matches what our opencode-sessions-explorer reads). House gotcha "db pipe truncation" (grokster GOTCHAS.md) should be cross-checked against `--format json`.

**`/global/event` SSE contract (verified)**: `GET /global/event` → global SSE stream (cross-project events). Per-instance stream: `GET /event` (first event `server.connected`, then bus events). Related: `/global/health` → `{ healthy: true, version }`. Full REST surface includes sessions/messages/diff/revert endpoints (§1.4). OpenAPI 3.1 spec at `http://<host>:<port>/doc`; SDK is generated from it.

**`OPENCODE_SESSION_ID`: NOT officially documented.** The official env-var table (CLI docs, updated 2026-08-25) does not list it. Documented vars include `OPENCODE_CONFIG*`, `OPENCODE_TUI_CONFIG`, `OPENCODE_SERVER_USERNAME/PASSWORD`, `OPENCODE_DISABLE_AUTOCOMPACT`, `OPENCODE_DISABLE_CLAUDE_CODE(_PROMPT/_SKILLS)`, `OPENCODE_CLIENT`, plus Experimental section (`OPENCODE_EXPERIMENTAL_EVENT_SYSTEM`, `_BACKGROUND_SUBAGENTS`, `_PLAN_MODE`, `_WORKSPACES`, `_SCOUT`, `_NATIVE_LLM`, …). If the fleet observes `OPENCODE_SESSION_ID` set in opencode-spawned shells, treat as **undocumented internal behavior** — real but unofficial, changeable without changelog. Recommended KB wording: "observed-in-practice; absent from official env table as of v1.18.21."

Confidence: db + SSE = **verified**. OPENCODE_SESSION_ID absence = verified absence in official table; runtime behavior remains **single-source/unresolved** pending local probe (`opencode run` + `env | grep OPENCODE`).

---

## §2 Version Delta Intelligence (OpenCode)

**Latest release**: **v1.18.23** (2026-08-25, commit `ef2880f`, released by `opencode-agent` bot). Repo: ~201k stars / 26.1k forks; ~1,100 releases total, cadence roughly daily. House binary pin implication: any pin older than ~v1.18.15 is missing compaction/revert correctness fixes below.

**Deltas since ~1.18.x relevant to fleet concerns** (all **verified** from release notes):

| Version | Date | Fleet-relevant change |
|---|---|---|
| v1.18.23 | Aug 25 | Cloudflare AI Gateway routing fixes; parent session IDs in headers for session-aware providers |
| v1.18.22 | Aug 24 | `textVerbosity` no longer sent to openai-compatible providers that don't support it (house provider-fabric relevance) |
| v1.18.20 | Aug 21 | **Failed subagent tool calls surface a resumable `task_id`** (directly validates house task_id-continuation playbook); permission requests from subagents now answerable during `opencode run`; more network-error retry variants |
| v1.18.19 | Aug 20 | "Preserved compatibility with existing v1 databases" (V2 migration is underway upstream); Codex rate limits matched to ChatGPT subscription |
| v1.18.17 | Aug 12 | **Compaction keeps complete recent turns + clearer summaries for smaller models**; capped automatic session retries + jitter (retry-storm fix) |
| v1.18.16 | Aug 10 | **Unknown top-level config fields are ignored instead of failing config parse** — pinned-binary configs gain forward-compatibility |
| v1.18.15 | Aug 7 | **Revert/fork use real message chronology instead of message-ID ordering**; repeated compaction keeps earlier tool-call history in summaries |

**The V2 track (strategic)**: a V2 rewrite exists behind `opencode.ai/v2/docs/*` and the `2.0` issue label (umbrella #34921 "V2: implement and repair revert/undo flows"; #34359 TUI migration; #34433/#34434 VCS/diff APIs). V2 introduces a *new plugin API* — registration-style hooks (`ctx.session.hook("context"|"model.request"|"http.request"|"http.response")`, `ctx.shell.hook("create.before")`, `ctx.event.subscribe()`) replacing/augmenting the V1 hooks-object return. **Fleet guidance**: the V1 hook surface (§1.1) remains the documented stable API on the 1.18.x line our binary pins to; when evaluating an upgrade past the V2 cutover, budget for plugin rewrite + revert-flow shakeout (#34921 was still open as of 2026-07-02).

---

## §3 Shallow Platform Fills (Priority 2)

### §3.1 Codex CLI (OpenAI)

- **Architecture**: Rust binary; all inference server-side (OpenAI API). Config: `~/.codex/config.toml` + `~/.codex/auth.json`. Non-interactive: `codex exec [--json] [--output-schema schema.json]`, `codex exec resume --last "<prompt>"`.
- **Sandbox model (two independent dials)**: `sandbox_mode` = `read-only | workspace-write | danger-full-access`; `approval_policy` = `untrusted | on-request | never` (older marketing names: Suggest / Auto Edit / Full Auto; `--full-auto` ≈ workspace-write + on-request; `--yolo` bypasses both). Network denied by default under workspace-write. Configurable `[sandbox] allow_read/allow_write/deny_write/allow_network` blocks. Mid-session switch via `/permissions`.
- **AGENTS.md**: primary instruction format — concatenated into context each session; **32 KiB default cap**; nested monorepo discovery (nearest-wins walking up); `AGENTS.override.md` for temporary overrides; `~/.codex/AGENTS.md` global. Confidence: multi-source.
- **Subagents/tasks**: no OpenCode-style subagent tree; multi-agent work goes through the OpenAI Agents SDK or `codex-acp` adapter (JetBrains/Copilot surfaces). Hooks exist (`developers.openai.com/codex/cli/hooks`). MCP supported via config.toml.
- **Version**: `rust-v0.143.0` cited 2026-07-08 (**single-source**, via Vaughan's citation of openai/codex releases). Default model family per mid-2026 guides: GPT-5.x series (**single-source** for exact name).
- **2026 development**: GitHub Copilot app can run Codex as agent provider (Jul 2026); JetBrains integration ignores `.aiignore` (security-relevant gap, single-source).

### §3.2 Claude Code (Anthropic)

- **CLAUDE.md hierarchy**: enterprise policy → `~/.claude/CLAUDE.md` → project root → `CLAUDE.local.md` (gitignored) → `.claude/rules/*.md` path-scoped Rules (added with the June 18, 2026 "Steering Claude Code" release alongside Skills/Subagents/Hooks/Output Styles as five primitives). Per-file effective load ≈ **first 200 lines or 25 KB** — overflow silently dropped. Confidence: multi-source.
- **Subagents**: `.claude/agents/*.md` markdown definitions (frontmatter: tools, model, `memory` scope `user|project|local`, per-subagent `hooks`, MCP servers). Spawned via Task tool; **depth=1 delegation by default** (subagents don't nest) — matches OpenCode's `subagent_depth: 1` default. Subagent persistent memory: `MEMORY.md` (200-line/25KB head injected) under `.claude/agent-memory/<name>/`. Built-in Explore/Plan agents skip CLAUDE.md loading. Confidence: **verified** against official docs (code.claude.com/docs/en/sub-agents excerpts).
- **Hooks**: lifecycle event system in `settings.json`; official docs at code.claude.com/docs/en/hooks (+hooks-guide). "25 lifecycle events" figure is **single-source** (community guide) — verify count against official page before quoting.
- **Agent Teams**: peer-multi-agent coordination (shared task list, DMs, per-agent worktrees, 1M context) — **experimental**, single-source details.
- **Plugins/marketplace**: first-class spring 2026 (skills bundling skills+MCP+commands).
- **Version pinning**: npm install deprecated in favor of native installer; pin via `curl -fsSL claude.ai/install.sh | bash -s <version>`; `DISABLE_AUTOUPDATER=1`. Exact current version number: **unresolved** this pass.

### §3.3 VS Code + Copilot agent mode

- **Agent mode + MCP**: GA to all VS Code users with MCP support (GitHub Blog, Apr 2026 announcement of full rollout; earlier preview Feb 2025). MCP servers configured in `.vscode/mcp.json` (or `MCP: Add Server` command); tool confirmation dialogs built in. Confidence: **verified** (official VS Code docs).
- **Instruction files (official taxonomy)**: `.github/copilot-instructions.md` (always-on, single file); `*.instructions.md` with `applyTo` glob patterns (file-based, default dir `.github/instructions/`); **`AGENTS.md` natively read** (`chat.useAgentsMdFile` setting; experimental nested AGENTS.md via `chat.useNestedAgentsMdFiles`); **`CLAUDE.md` also detected** (root, `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md`, `CLAUDE.local.md`) via `chat.useClaudeMdFile`; organization-level instructions defined at GitHub org level; `/init` generates instructions. Confidence: **verified** (code.visualstudio.com/docs/agent-customization/custom-instructions).
- **Gap**: classic Copilot CLI (`gh copilot suggest/explain`) does NOT read `copilot-instructions.md` (multi-source). GitHub-side Copilot code review gained repo-level MCP config + `.github/skills/*/SKILL.md` GA 2026-07-29 (GitHub Changelog, **verified**).
- **House pattern note**: Copilot remains most useful to Omega as a priority-6 cloud *provider* through OpenCode's transform.ts normalization; agent-mode parity with OpenCode agents is partial (no equivalent of custom agent permission matrices).

---

## §4 Standard & Best-Practice Validation (Priority 3)

### §4.1 AGENTS.md standard status — Aug 2026

**Governance change since grokster's R_AGENTS_MD_RULES_ECOSYSTEM_20260818.md research window**: AGENTS.md was donated to the **Agentic AI Foundation (AAIF), a Linux Foundation directed fund, in December 2025** (same governance wave that brought MCP under the Foundation; founding members OpenAI/Anthropic/Block). Adoption: **60,000+ public repos**, native readers include Codex CLI, GitHub Copilot (incl. coding agent + VS Code), Cursor, Windsurf, Amp, Devin, Aider, Zed, Factory, Jules, Kilo, RooCode, Warp, JetBrains Junie — i.e., grokster's "cross-tool standard" thesis is **validated and strengthened**; it is now vendor-neutral governed infrastructure, not an OpenAI convention.

Corrections/refinements to fold in:
1. **Claude Code still does not read AGENTS.md natively** — canonical workaround is first-line `@AGENTS.md` import in CLAUDE.md (or symlink). Multi-source.
2. **Gemini CLI support is disputed across sources**: one tracker says "No — uses GEMINI.md"; another says it reads AGENTS.md alongside GEMINI.md. Mark **unresolved**; treat GEMINI.md as primary for Gemini CLI.
3. VS Code reads AGENTS.md natively (**verified** from official docs) — stronger than "partial".
4. Spec remains minimal plain Markdown (no required fields); v1.1 proposes optional frontmatter (`description`, `tags`) — not yet standard.
5. **NEW (post-dates grokster's doc): OpenAI "Agent Plugins" v1.0.0 Working Draft announced 2026-08-06** (agent-plugins.org, developed with AWS, Cursor, GitHub, VS Code, Vercel) — portable packaging of Agent Skills + MCP config across clients. This is the next standardization wave after AGENTS.md; watch-list item for the fleet's skills architecture.

### §4.2 Multi-platform expertise maintenance & version pinning (2026 patterns)

Validated against 2026 industry practice (Zylos safe-upgrade research, multi-tool config guides):

1. **Pin exact versions; kill auto-updaters in production** (`DISABLE_AUTOUPDATER=1` for Claude Code; `OPENCODE_DISABLE_AUTOUPDATE` exists in OpenCode env table — verified). Never `latest` tags; use digests in containers.
2. **Environment version matrix** (`version-policy.yaml` pattern): dev = floating minor, staging/prod = exact pin, prod auto-update off. Maps cleanly onto Omega's pinned-binary practice — formalize it.
3. **Session-version tagging + drain-before-upgrade**: tag which runtime created each session; drain active sessions before upgrading (prevents session-state desync — exactly our opencode.db compatibility concern; note upstream v1.18.19 "preserved v1 database compatibility").
4. **Separate runtime upgrades from agent/config changes**; changelog review as pre-upgrade checklist step; canary + rollback metrics (task success rate, latency, cost deltas).
5. **Single-source-of-truth instruction files with derivation**: canonical AGENTS.md → symlink/import for CLAUDE.md/GEMINI.md/copilot-instructions.md (community `agents-skeleton` pattern; `rule-porter` converters). Directly applicable to Omega: our repo-root AGENTS.md should be SSOT, derived files generated not hand-maintained.
6. **Freshness metadata on knowledge docs** (grokster's rot_class/last_verified) matches industry "treat platform knowledge as a dependency with its own expiry" — keep and extend to fleet-level PLATFORM_GNOSIS_MAP entries.

---

## §5 KB Patch Recommendations (for grokster)

| # | File | Patch |
|---|---|---|
| P1 | `platforms/opencode/ARCHITECTURE.md` | Add §"Repo identity": canonical repo = `anomalyco/opencode` (rename of sst/opencode, Jan 2026) — update all URLs; add SnapshotPart/revert/unrevert semantics (§1.4 above); add V1-vs-V2 plugin API split warning with upgrade guidance. |
| P2 | `platforms/opencode/CONFIG_REFERENCE.md` | Add `subagent_depth` (top-level key, default 1, parentID-chain depth count, agent-visible error at limit); add `snapshots` bool key; document that TUI keys live in **tui.json** not opencode.json (leader_timeout, keybinds, variant_cycle=ctrl+t); mark `OPENCODE_SESSION_ID` as undocumented-internal; note v1.18.16+ ignores unknown top-level config fields. |
| P3 | `platforms/opencode/GOTCHAS.md` | New gotchas: (G+) global `"task": "allow"` or frontmatter `tools: {task: true}` ⇒ unbounded subagent recursion (#18100: 612 sessions/73min); (G+) `subagent_depth ≥ 2` + "ask" permissions ⇒ silent stall (#39112 family); (G+) `/undo` hazards: dirty worktree (#10287), nested git repos unprotected (#30065), non-git dir false success (#38672). |
| P4 | `other_platforms/CODEX_CLAUDE_CODE_VSCODE.md` | Replace shallow-state bodies with §3 content above; retain honesty markers only where single-source (Codex version, Claude hooks count, Agent Teams). Add Copilot-instruction-file taxonomy incl. AGENTS.md/CLAUDE.md detection. |
| P5 | `INDEX.md` + `MINING_LOG.md` | Bump last_verified for patched docs; log this R-doc as provenance source; add `docs/research/R_PLATFORM_EXPERTISE_WEB_HARDENING_20260826.md` to navigation; add Agent Plugins spec to watch-list. |

---

## §6 Source Index

Primary (fetched/read directly, 2026-08-26):
- https://opencode.ai/docs/plugins/ — plugin hooks, compaction hooks, load order
- https://opencode.ai/docs/keybinds/ — full tui.json keybind map
- https://opencode.ai/docs/cli/ — command reference, env vars, experimental flags
- https://opencode.ai/docs/server/ — REST/SSE surface, /global/event, /doc OpenAPI
- https://opencode.ai/v2/docs/snapshots — snapshot/revert architecture
- https://github.com/anomalyco/opencode/releases — v1.18.14…v1.18.23 notes
- https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/task.ts — subagent_depth source
- https://raw.githubusercontent.com/joshuadavidthomas/opencode-plugins-manual/main/docs/07-events.md — event payload schemas w/ source anchors
- https://code.visualstudio.com/docs/agent-customization/custom-instructions — VS Code instruction files
- https://code.claude.com/docs/en/sub-agents — Claude Code subagents/memory

Secondary (search excerpts, not fully fetched):
- https://github.com/anomalyco/opencode/issues/17721, /18100, /36878, /39112, /34921, /10287, /5910, /30065, /38672, /3073
- https://github.com/YanzuoLu/opencode-subagent-depth-limit (community depth-limit plugin)
- https://releasealert.dev/github/anomalyco/opencode (release cadence/stats)
- https://tomrochette.com/agents/opencode/ (repo-move corroboration)
- https://aiwiki.ai/wiki/opencode (company history, Anthropic OAuth incident)
- https://codex.danielvaughan.com/2026/07/09/... (Codex multi-surface/Copilot integration)
- https://www.obviousworks.ch / news.creeta.com / prakashbhandari.com.np (Claude Code 2026 guides)
- https://thepromptshelf.dev/blog/github-copilot-instructions-md-complete-guide-2026/
- https://codersera.com/blog/agents-md-complete-guide-2026/ ; https://genno-whittlery.github.io/agent-notes/2026-agents-md-standard.html ; https://agents.md/
- https://explainx.ai/blog/agent-plugins-openai-standard-aws-cursor-github-vscode-2026 (Agent Plugins)
- https://zylos.ai/research/2026-03-06-ai-agent-version-management-safe-upgrade-patterns/
- https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated/ ; https://github.blog/changelog/2026-07-29-copilot-code-review-agent-skills-and-mcp-now-generally-available
- https://computingforgeeks.com/codex-cli-cheat-sheet ; https://inventivehq.com/knowledge-base/openai/how-to-configure-sandbox-modes

Could NOT verify this pass:
- `OPENCODE_SESSION_ID` runtime behavior (absent from official env table; needs local probe)
- Exact current Claude Code release number; exact current Codex CLI release beyond rust-v0.143.0 (Jul 8 2026 citation)
- Gemini CLI native AGENTS.md support (conflicting secondary sources)
- Claude Code hooks event count ("25") and Agent Teams version claims (single-source community figures)

---
*⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ trc_synthesis ⬡ 2026-08-26*

