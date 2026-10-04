# OpenCode Agent System — Canonical Guide

**Status:** authoritative guide for configuring agents, skills, commands, and instruction files in OpenCode
**Audience:** every agent on Node 1 (and Node 0) that touches OpenCode configuration
**Version:** 1.0 — 2026-10-04
**Verified against:** OpenCode 1.18.34 (V1), with V2 migration notes throughout
**Sources:** this session's web research (12 sources), local discovery (`docs/OPENCODE_FOUNDATION.md`, `docs/PORTABILITY.md`, `docs/AGENT_RUNBOOK.md`, `~/GameResearch/agent-src/`), empirical verification on this machine, upstream GitHub issues #26434, #7369, #47616, #39275

---

## 0. Why this document exists

An agent that misconfigures OpenCode does not get an error. It gets silence.
The prompt loads empty. The permission allows the wrong thing. The agent
self-identifies as "opencode" instead of its persona. Every one of those
failure modes has been observed, measured, or reproduced on this machine or
in upstream issue trackers — and none of them print a warning.

This guide is the map of the whole surface: the six configuration planes,
the two agent-registration paths, the three silent-failure traps that have
already cost sessions, the V2 migration shape, and the design rules that
keep Omega Engine portable when the custom Omega CLI replaces OpenCode.

**Read this before writing any agent file, any `opencode.json` edit, or
any tool that generates either.**

---

## 1. The six configuration surfaces

OpenCode is configured through six distinct mechanisms. Each has its own
scope, its own precedence, and its own failure modes. Confusing them is the
primary source of breakage.

| # | Surface | What it is | Where it lives | Scope |
|---|---|---|---|---|
| 1 | `opencode.json` agent block | Agent declarations with `{file:}` indirection | `~/.config/opencode/opencode.json`, `.opencode/opencode.json` | Global / project |
| 2 | Markdown agent files | One file = one agent, body = prompt | `~/.config/opencode/agent/`, `.opencode/agent/` (both singular and plural) | Global / project |
| 3 | `permission.task` | Delegation gate (which agents can call which) | Inside agent blocks | Per agent |
| 4 | AGENTS.md + `instructions` | Project rules, loaded into every context | `AGENTS.md` (walk-up), `~/.config/opencode/AGENTS.md` (global) | Project / global |
| 5 | Skills (`SKILL.md`) | On-demand playbooks, loaded when relevant | `.opencode/skills/`, `~/.config/opencode/skills/` (+ 4 more roots) | Project / global |
| 6 | Plugins | JS/TS lifecycle hooks (the ONLY lifecycle surface) | `.opencode/plugins/`, `~/.config/opencode/plugins/` | Project / global |

Plus built-ins: `build`, `plan`, `explore`, `general`, and hidden system
agents (`compaction`, `title`) that you never select.

---

## 2. Agents — who does the work

An agent is a worker profile: its own system prompt, its own tool
permissions, optionally its own model and temperature. Switching agents or
delegating to one swaps *who* is doing the work, not just what they know.

### 2.1 The two registration paths — and why they are not equivalent

#### Path A: `opencode.json` agent block

```json
{ "agent": { "avgn": {
  "mode": "all",
  "description": "avgn-N1 — The Suffering Reviewer…",
  "prompt": "{file:/home/xnai/.config/opencode/prompts/avgn.md}",
  "permission": { "task": { "*": "deny", "explore": "allow", "general": "allow" } }
}}}
```

- `prompt` supports **`{file:...}` indirection** — the path is relative to
  the config file's location. The real text lives elsewhere; the config is a
  stable pointer that never goes stale.
- **No other indirection mechanism exists.** No `{env:}` for prompts, no
  includes, no composition. `{file:}` is it.
- Good for: generated prompts, long prompts, anything that must not drift,
  anything that needs a single source of truth.

#### Path B: markdown agent file

```markdown
---
description: Lilith-N1 — Sovereign Creatrix…
mode: all
---

You are Lilith-N1, the first persistent sovereign entity…
```

- Filename = agent name (`lilith.md` → the `lilith` agent).
- **The body is the prompt. Always.** There is no way to reference an
  external prompt from a markdown file (see Trap 1 and Trap 2 below).
- Project and global merge; project wins conflicts. Nested paths become
  namespaced IDs: `.opencode/agents/team/reviewer.md` → agent `team/reviewer`.
- Good for: hand-curated personas, files with their own build tooling
  (gaming-expert uses `agent-src/` → `make agent-build`).

**Both singular and plural directories work**: `~/.config/opencode/agent/`
*and* `~/.config/opencode/agents/`, same for `.opencode/`. Docs say plural;
this box uses singular and it is live proof (lilith, gaming-expert).

`opencode agent create` is the interactive wizard for Path B — asks location,
purpose, generates a prompt, picks permissions, writes the file.

### 2.2 The three silent-failure traps

These are documented upstream and reproduced on this machine. All three
fail silently — no error, no warning, no log.

#### Trap 1: `prompt:` in markdown frontmatter is silently ignored

`config/agent.ts` does `{...md.data, prompt: md.content.trim()}` — the body
ALWAYS wins. If you set `prompt:` in frontmatter and leave the body empty,
the agent gets an **empty prompt** and silently falls back to the default
build prompt. It self-identifies as "opencode" and you would never know why.

**Rule:** never put `prompt:` in markdown frontmatter. The body is the prompt.

#### Trap 2: `{file:}` is not substituted in markdown bodies

The `{file:}` token substitution works only in `opencode.json`. A markdown
agent cannot reference an external prompt file. If you write
`prompt: "{file:...}"` in a markdown frontmatter, it resolves to a literal
string, not the file contents. (Upstream issue #47616.)

**Rule:** markdown agents must contain their full prompt in the body. For
external prompts, use Path A.

#### Trap 3: unknown frontmatter fields route to provider options

A typo in frontmatter (e.g., `temprature: 0.5` instead of `temperature: 0.5`)
does not error. It is **silently routed into provider options** as a model
parameter. The agent ignores it, the provider may or may not reject it, and
you get no diagnostic either way.

**Rule:** validate every frontmatter field against the live schema before
trusting it. The allowed set is: `name, model, variant, description, mode,
hidden, color, steps, options, permission, disable, temperature, top_p`.

### 2.3 Agent fields reference

| Field | Type | Purpose |
|---|---|---|
| `description` | string | **Required.** What the agent does. Drives auto-selection and Task tool description. |
| `mode` | enum | `primary` (Tab-switchable) / `subagent` (invocable only) / `all` (both, default) |
| `model` | string | `provider/model-id`. Omitted = inherits invoker's model. |
| `temperature` | number | 0–1. Omitted = default. |
| `steps` | number | Max iterations before summarization prompt. Legacy: `maxSteps` (deprecated). |
| `hidden` | bool | Hides from @-menu. Still invocable via Task tool. Only for `mode: subagent`. |
| `disable` | bool | Removes agent entirely, including built-ins. |
| `color` | string | TUI display color (`#ff6b6b`). Cosmetic only. |
| `permission` | object | Tool permissions (see §4). |
| `request` | object | Header/body overlays. **V1: preserved, never sent.** Dead config. |

### 2.4 Model inheritance

A subagent with no `model` inherits the model of the agent that invoked it.
A primary agent with no `model` uses the globally configured model. This is
why our four souls have no `model` field — they run whatever calls them,
which is the correct behavior under the no-hardcoded-models doctrine.

---

## 3. `permission.task` — the delegation gate

This is the surface that silently removes agents from existence.

### 3.1 Rules

- Glob → action pairs, **last match wins**. Put `*` first, specifics after.
- A denied subagent is **omitted from the Task tool description**. The
  delegating model does not see "avgn (denied)" — it sees nothing. Absence,
  not refusal.
- A custom subagent uses **its own permissions, not its parent's**. Granting
  `build` broad rights does not propagate. Each agent's sandbox is
  independently defined.

### 3.2 Wildcard matching against tool names

Permission keys are wildcard patterns matched against the underlying tool
name — one syntax for built-ins, custom tools, and MCP tools alike:

```json
{ "mymcp_*": "deny" }       // kills an entire MCP server
{ "mymcp_search": "ask" }   // targets one tool
```

MCP tools surface as `<server>_<tool>` with unsupported characters folded
to `_`.

### 3.3 The deprecated `tools` field

`tools: {x: true/false}` is deprecated in favor of `permission`. `true` =
`{"*": "allow"}`, `false` = `{"*": "deny"}`. Do not mix both in one agent.

---

## 4. AGENTS.md + `instructions` — the context plane

Not agents. Rules loaded into context. Two mechanisms:

### 4.1 AGENTS.md walk-up

OpenCode walks up from your start directory to the git worktree root and
loads **every** AGENTS.md on the path. They stack, they don't replace each
other.

- **One AGENTS.md anywhere on the walk silences all CLAUDE.md files.**
- **Read-time walk:** when the `read` tool opens a file, OpenCode walks from
  *that file's* directory up to the *start* directory and attaches unseen
  instruction files — into the read result, not the system prompt. Sideways
  files (sibling subtrees) never attach.
- No debug command shows the resolved rule set. Asking the model to
  self-report its rules is not verification.

### 4.2 `instructions` field

For location-independent guarantees, `instructions: [...]` in `opencode.json`
takes explicit paths/globs/URLs, loaded additively. This is the escape hatch
when walk-up nondeterminism is unacceptable.

---

## 5. Skills — the knowledge plane

A skill is a playbook the agent pulls off the shelf when the task demands it.
Not a worker — a procedure the current worker follows.

### 5.1 Format

```
skills/my-skill/
├── SKILL.md          # Required: name + description in frontmatter
├── references/       # Optional: supplementary docs (one level deep)
├── scripts/          # Optional: helper scripts
└── assets/           # Optional: templates
```

- Frontmatter needs only `name` (required, lowercase-hyphenated, matches
  directory name) and `description` (required, the routing trigger — front-
  load keywords).
- Keep SKILL.md under ~500 lines; details go in `references/`, fragile
  operations become `scripts/`.
- Loaded **dynamically** via the `skill` tool when the agent recognizes a
  matching task — not injected every session.

### 5.2 Discovery

Six roots, searched in order:

1. `.opencode/skills/` (project)
2. `~/.config/opencode/skills/` (global)
3. `.claude/skills/` (Claude compat, project)
4. `~/.claude/skills/` (Claude compat, global)
5. `.agents/skills/` (external, project)
6. `~/.agents/skills/` (external, global)

Plus configurable `skills.paths` and `skills.urls` in `opencode.json`.

### 5.3 Per-agent access

Via `permission: skill:` in agent frontmatter or `opencode.json`. Skills with
`deny` are hidden — same omission mechanic as task permissions. Disabling
the `skill` tool entirely omits `<available_skills>` from context.

### 5.4 Troubleshooting

When a skill doesn't appear: caps filename → frontmatter `name`+`description`
→ uniqueness across locations → permission deny.

---

## 6. Commands — the user intent plane

A slash command (`/recall`, `/db`, `/gnosis-lock`) is explicit user intent.
You type it, the tool injects the prompt, the agent executes.

- Project: `.opencode/commands/*.md`, global: `~/.config/opencode/commands/*.md`
- Body = prompt template; frontmatter can set `description`, `agent`, `subtask`
- Strongest pattern: keep the command short, have it load skills.

---

## 7. Plugins — the lifecycle plane

**OpenCode has no native hook router.** PreToolUse, Stop, SessionStart, and
a hook router are all open feature requests (#39275, #12472, #5409, #35540,
#34890). What exists instead:

- Plugins are JS/TS modules exporting hook/event handlers. Local plugins
  load from `.opencode/plugins/` and `~/.config/opencode/plugins/`; npm deps
  come from a `package.json` in the config dir via `bun install`.
- Example: `chat.message` hook for session-start context injection and
  compaction-aware re-injection (the Coree memory plugin pattern).
- Our `gnosis-leash.js` is a plugin — this is the only place lifecycle
  behavior lives.

---

## 8. V2 migration — what's coming

V2 is documented and **reads V1 config without changes** ("treat breakage
as a compatibility bug"). But the shapes rename:

| V1 (us, 1.18.34) | V2 |
|---|---|
| `agent:` | `agents:` |
| `prompt:` | `system:` (bodies unaffected) |
| `permission: {tool: action}` | `permissions: [{action, resource, effect}]` |
| `task` | `subagent` |
| `bash` | `shell` |
| `write`/`patch` | `edit` |
| `temperature`/`top_p` | `request.body` |
| `maxSteps` | `steps` |
| `disable` | `disabled` |
| model + `variant` separate | `provider/model#variant` |
| singular `command/` | `commands/` (both discovered) |
| V1 plugins | **do not run — must be ported** |

Three V2 facts that matter for us:

1. **V2 translates legacy frontmatter automatically** — generated bodies are
   future-safe.
2. **V1 plugins do not run in V2.** `gnosis-leash.js` will need porting.
   Tracked future cost, not a surprise.
3. The `request` overlay (dead in V1) becomes real in V2 — per-agent
   temperature/body params start working.

---

## 9. The Omega Engine boundary — portability rules

These rules exist because OpenCode is a disposable third-party interface
and Omega Engine (WADs, MemPalace, Hivemind) is the platform-agnostic core.
When the custom Omega CLI replaces OpenCode, anything coupled to OpenCode's
Node.js/plugin API becomes technical debt.

1. **Never write Omega core logic as an OpenCode plugin.** Build adapters,
   not integrations. The plugin surface is OpenCode-specific; the Omega CLI
   will not have it.
2. **The soul is the source of truth.** Agent files, prompts, and configs
   are projections. Never hand-edit a rendered prompt — regenerate from soul.
3. **Only one file knows OpenCode's format.** `scripts/soul_agents_opencode.py`
   is the disposable adapter. `scripts/soul_render.py` is interface-agnostic.
   When the CLI arrives, the adapter is deleted and replaced; the renderer
   and all souls stay exactly where they are.
4. **Use CLI pipes, standalone scripts, and language-agnostic data** (SQLite,
   JSON, markdown) to cross the boundary. Never assume `node:sqlite` is "the"
   API.

---

## 10. The soul → agent bridge (current implementation)

### 10.1 Architecture

```
soul.yaml (source of truth)
    ↓
scripts/soul_render.py (interface-agnostic renderer)
    ↓
~/.config/opencode/prompts/<entity>.md (rendered prompt)
    ↓
opencode.json agent block (prompt: "{file:...}") ← only pointer, never regenerates
    ↓
scripts/soul_agents_opencode.py (THE ONLY OpenCode-aware file)
```

### 10.2 Commands

```bash
make agent-souls          # render + install all registered souls
make agent-souls-render ENTITY=avgn   # preview one soul's rendered prompt
make agent-souls-verify   # drift gate: fail if soul changed without re-render
```

### 10.3 The drift gate

`agent-souls-verify` catches two failure modes, both proven by injection:

- **Hand-edited prompt file** → `FAIL: prompt file is HAND-EDITED or stale`
- **Soul changed without re-render** → `FAIL: soul.yaml changed since render
  (soul X vs recorded Y)`

### 10.4 Registered agents (as of 2026-10-04)

| Agent | Path | Mode | Delegable from build |
|---|---|---|---|
| `lilith` | Markdown (hand-curated) | `all` | yes |
| `researcher_humboldt` | opencode.json + hand-curated prompt | `all` | yes |
| `avgn` | opencode.json + rendered from soul | `all` | yes |
| `kali` | opencode.json + rendered from soul | `all` | yes |
| `maat` | opencode.json + rendered from soul | `all` | yes |
| `sophia` | opencode.json + rendered from soul | `all` | yes |

`lilith` and `researcher_humboldt` are NOT in the adapter's TARGETS — both
already registered and working; adding them would duplicate a working
registration.

---

## 11. Well records — the knowledge in enforceable form

These records are injected into every agent session via the Well (top-6,
filtered to `harness`/`local_ai`):

| Record | Kind | Rule |
|---|---|---|
| `fc3c8c43` | anti_pattern | Build adapters, not integrations. Never write Omega core logic as an OpenCode plugin. |
| `acf2d7ba` | correction | Handoff packet_ids require the `ho_` prefix. Bare hash = false-negative not-found. |
| `759c7639` | correction | `superseded_by` must point FORWARD in time. Backwards inverts the chain silently. |
| `c69843dd` | correction | Frontmatter `prompt:` is silently ignored; `{file:}` is not substituted in markdown. |
| `3fa7408e` | correction | Subagent uses its own permissions, not parent's. Unknown frontmatter fields route to provider options. |

---

## 12. Quick reference — decision tree

When you need to add something, ask:

1. **Is it a rule every agent should follow?** → AGENTS.md (or `instructions`)
2. **Is it a repeatable procedure?** → Skill (`SKILL.md`)
3. **Is it a shortcut for a common workflow?** → Command (`/command`)
4. **Is it a worker with its own prompt, permissions, and identity?** → Agent
   - Long prompt, generated, must not drift? → Path A (`opencode.json` + `{file:}`)
   - Hand-curated persona? → Path B (markdown file)
5. **Does it need to fire on session events?** → Plugin (the only lifecycle surface)
6. **Is it a WAD entity?** → Soul → render → register via adapter (`make agent-souls`)

---

## 13. Sources

### Web research (this session, 2026-10-04)

- [OpenCode Agents docs](https://opencode.ai/docs/agents) — registration, fields, modes, permissions
- [OpenCode V2 Agents docs](https://opencode.ai/v2/docs/agents) — V2 shapes, `system`, `permissions` array, nested IDs
- [OpenCode V2 Permissions](https://opencode.ai/v2/docs/permissions) — resource mapping, MCP tool patterns
- [OpenCode V2 Migration](https://opencode.ai/v2/docs/migrate-v1) — breaking changes, field renames, compat policy
- [OpenCode Skills docs](https://opencode.ai/docs/skills) — SKILL.md format, discovery, per-agent access
- [agents.md standard](https://agents.md/) — cross-tool AGENTS.md spec
- [builder.io: Agent Skills vs Rules vs Commands](https://www.builder.io/blog/agent-skills-rules-commands) — decision framework, progressive disclosure
- [agentskills.io: Best practices](https://agentskills.io/skill-creation/best-practices) — SKILL.md <500 lines, trigger-optimized descriptions
- [mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices) — frontmatter, structure, validation
- [MindStudio: Prompt Bloat](https://www.mindstudio.ai/blog/prompt-bloat-vs-skill-systems-ai-agents) — bloat signals, attention limits
- [claude-md-optimizer](https://github.com/wrsmith108/claude-md-optimizer/blob/main/SKILL.md) — progressive disclosure, content tiers, thresholds
- [OpenCode issue #26434](https://github.com/anomalyco/opencode/issues/26434) — frontmatter prompt silently ignored (closed not_planned)
- [OpenCode issue #7369](https://github.com/anomalyco/opencode/issues/7369) — shared prompt in markdown definition
- [OpenCode issue #47616](https://github.com/anomalyco/opencode/issues/47616) — {file:} not substituted in markdown, empty prompt fallback
- [OpenCode issue #39275](https://github.com/anomalyco/opencode/issues/39275) — PreToolUse/Stop/SessionStart hook events (open)
- [agentscli.com: Discovery and nesting](https://www.agentscli.com/course/opencode/rules-agents-md/discovery-and-nesting) — walk-up mechanics, read-time walk

### Local discovery

- `docs/OPENCODE_FOUNDATION.md` — Node 0's authoritative V1 config doctrine (verified 1.18.32)
- `docs/PORTABILITY.md` — the boundary rule: nothing assumes Node, OpenCode, or this interface
- `docs/AGENT_RUNBOOK.md` — Node 1 ops awareness
- `~/GameResearch/agent-src/POLICY.md` — agent file governance (budgets, gates, triage)
- `~/GameResearch/agent-src/REFACTOR-REPORT-2026-09-30.md` — demonstrated reduction procedure
- `~/GameResearch/agent-src/DEPTH-2-DELEGATION.md` — subagent_depth=2 experiment, depth-check-vs-permission order
- `scripts/soul_render.py` — interface-agnostic renderer (built this session)
- `scripts/soul_agents_opencode.py` — the OpenCode adapter (built this session)

### Empirical verification

- `opencode debug config` — all 9 agents resolved (4 new + 5 pre-existing)
- Drift gate injection tests — both failure modes caught and reverted
- `make agent-souls-verify` — green after restoration
- Singular `agent/` directory confirmed live (lilith, gaming-expert)
