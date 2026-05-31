# 🔱 Multi-Project Claude Code Orchestration — Research Report

⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ trc_research ⬡ RESEARCH

**AP Token**: `AP-RES-MULTI-PROJECT-v1.0.0`
**Date**: 2026-05-22
**Sources**: Anthropic official docs, Chanl Blog, Claude Lab, Felo Search Blog, GitHub community tools, DEV community

---

## 1. Splitting a Large Codebase Across Multiple Projects

### Pattern: Orchestrator with subagents (one per architectural layer)

The dominant pattern for monorepos with multiple services/architectural layers is **orchestrator + subagents**. A main Claude Code session acts as the planner/manager that dispatches subagents, each handling one architectural layer. Task ordering follows the "DRY onion" pattern: inner layers first, outer layers last. Backend before SDK. SDK before UI. Each layer depends on the shape of the layer below it.

**Source**: `https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern` (Chanl Blog, 2026-04-01)

> "If the task touches more than one project with different conventions, use subagents. If it touches multiple files in the same project, a single session is usually fine."

> "Task ordering follows what we call the DRY onion. Inner layers first, outer layers last. Backend before SDK. SDK before UI. This matters because each layer depends on the shape of the layer below it."

### Pattern: Per-subdirectory CLAUDE.md files

Claude Code automatically walks up the directory tree and loads every CLAUDE.md it finds, creating a hierarchy. The root CLAUDE.md is a **navigation hub** (not an encyclopedia), subdirectory CLAUDE.md files contain project-specific context.

**Source**: `https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start` (Anthropic, 2026-05-14)

> "Initializing in subdirectories, not at the repo root. Claude works best when it's scoped to the part of the codebase that's actually relevant to the task."

> "For organizations where code isn't consolidated in a conventional directory structure, a lightweight markdown file at the repo root listing each top-level folder with a one-line description of what lives there gives Claude a table of contents."

**Source**: `https://www.channel.tel/blog/claude-extension-stack-part-4-composing-production-stack` (Chanl Blog, 2026-03-19)

> "Our CLAUDE.md used to be over 600 lines — it contained all backend patterns, all frontend rules, all deploy procedures, everything. Claude would frequently ignore rules buried deep in the file. Splitting to a navigation hub with scoped rules was a turning point."

### Pattern: Scoped rules via `.claude/rules/` with glob frontmatter

Rules files have a `globs:` frontmatter field. When you edit a backend service file, only backend rules load. When you edit a React component, only frontend rules load.

**Source**: `https://www.channel.tel/blog/claude-extension-stack-part-4-composing-production-stack`

> "Underappreciated feature in the entire extension stack. Each rules file has a `globs:` frontmatter that scopes it to specific file patterns."

### Pattern: Codebase maps for discovery

For repos with dozens of top-level folders, a lightweight markdown file at the repo root listing each folder with a one-line description gives Claude a table of contents it can scan before opening files.

**Source**: `https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start` (Anthropic playbook)

> "For codebases with hundreds of top-level folders, this works best as a layered approach: the root file describes only the highest-level structure, and subdirectory CLAUDE.md files provide the next level of detail."

### Pattern: One project per microservice (multi-repo)

For organizations with separate repositories per microservice, community tools like `patricio0312rev/workspaces` provide Claude Code plugins that manage multi-repo workspaces with cross-project awareness (dependency mapping, cross-repo search, service health checks).

**Source**: `https://github.com/patricio0312rev/workspaces` (2026-01-25)

> "Workspaces fixes this by giving Claude Code awareness of your entire project structure — not just the single repo you're sitting in."

---

## 2. Maintaining Consistency Across Projects

### Pattern: Hierarchical CLAUDE.md loading (the layered approach)

Claude Code reads CLAUDE.md files additively as it moves through the directory tree. Root file = big picture + critical gotchas only. Subdirectory files = local conventions.

**Source**: `https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start` (Anthropic, 2026-05-14)

**Source**: `https://claudefa.st/blog/guide/development/large-codebase-playbook` (ClaudeFast, 2026-05-21)

> "Keep the root CLAUDE.md under 100 lines and reserve it for cross-cutting context: the stack, the one-sentence purpose of each top-level folder, and conventions that apply everywhere."

### Pattern: Three-layer configuration

| Layer | Scope | File | Purpose |
|-------|-------|------|---------|
| Layer 1 | Global | `~/.claude/CLAUDE.md` | Universal rules for all projects |
| Layer 2 | Per-project | `project/CLAUDE.md` | Project-specific constraints, stack, conventions |
| Layer 3 | Agent specialization | `~/.claude/agents/*.md` | Role-specific agents (implementer, researcher, debugger) with model assignments |

**Source**: `https://doneyli.substack.com/p/the-3-layer-claude-code-configuration` (Doneyli De Jesus, 2026-03-01)

> "Multi-project governance. I work across 10 production projects. Global rules prevent the same mistakes across all of them."

### Pattern: Shared convention via symlinks (CONVENTIONS.md)

Centralize conventions in one file, distribute via symlinks across projects.

**Source**: `https://dev.to/odakin/solving-claude-codes-memory-loss-multi-project-design-patterns-3kjm` (DEV, 2026-03-20)

```
~/Claude/
├── CONVENTIONS.md → claude-config/CONVENTIONS.md (symlink)
├── claude-config/
│   ├── CONVENTIONS.md     # single source of truth
│   └── setup.sh           # bootstrap script
├── project-a/CLAUDE.md    # "See ~/Claude/CONVENTIONS.md" + project-specific
└── project-b/CLAUDE.md
```

### Pattern: CLDPM (Claude Project Manager)

An SDK and CLI for managing monorepos with multiple Claude Code projects. Enables sharing skills, agents, hooks, and rules across projects without duplication via a hybrid linking strategy (symlinks generated locally from config file references).

**Source**: `https://github.com/transilienceai/cldpm` (2026-01-29)

> "Shared components live in `shared/{type}/{name}` and are symlinked into each project's `.claude/` directory. The source of truth is `project.json`; symlinks are regenerated via `cldpm sync`."

| Command | Description |
|---------|-------------|
| `cldpm init` | Initialize a new mono repo |
| `cldpm create project` | Create a new project |
| `cldpm add skill:logging --to web-app` | Add shared component to a project |
| `cldpm sync --all` | Regenerate symlinks for shared components |

### Pattern: Hooks for mechanical enforcement

PostToolUse hooks can enforce consistency automatically. For example, a hook matching `Edit|Write` runs `post-edit-compile-check.sh`, which detects the project type and runs the appropriate checker — Claude can't forget or skip it.

**Source**: `https://doneyli.substack.com/p/the-3-layer-claude-code-configuration`

> "A hook matching Edit|Write runs post-edit-compile-check.sh, which detects the project type and runs the appropriate checker — the agent can't forget or skip it."

---

## 3. Planner/Manager → Subagent Handoff Patterns

### Pattern: Orchestrator + Subagents (the dominant pattern)

The main Claude thread acts as an orchestrator. It **never writes code directly** for multi-project tasks. Instead it plans, dispatches, and reviews. Multiple subagents get clean context windows — each with only their layer's rules.

**Source**: `https://www.channel.tel/blog/enforce-orchestrator-pattern-claude-code` (Chanl Blog, 2026-03-27)

**The three-layer enforcement stack**:
1. **CLAUDE.md** — tells Claude the workflow
2. **Skills** (e.g., `dispatch` skill) — structures work into phases: Plan → Dispatch → Verify
3. **Hooks** (PreToolUse) — denies source file edits on the main thread. Claude sees the denial and knows to dispatch instead.

**Source**: `https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern`

> "The decision threshold we've settled on: if the task touches more than one project with different conventions, use subagents. If it touches multiple files in the same project, a single session is usually fine."

### Pattern: Claude Coordinator — 10-phase state machine

A complete orchestration system with explicit phases: `startup → intake → plan → delegate → integrate → review → test → promote-learnings → validate → close`.

**Source**: `https://github.com/dennisonbertram/claude-coordinator` (2026-03-27)

| Phase | What happens |
|-------|-------------|
| **startup** | Briefer reads context files |
| **intake** | Capture user intent, user confirms |
| **plan** | Planner produces task breakdown |
| **delegate** | Workers execute in parallel (worktree-isolated) |
| **integrate** | Validate worker output contracts |
| **review** | Reviewer (Opus + GPT-5.4) checks risky changes |
| **test** | UI/UX/System testers validate |
| **promote-learnings** | Learning-extractor analyzes artifacts + transcripts |
| **validate** | Intent-validator compares work against original intent |
| **close** | Write context packet for next session |

The coordinator uses a pure-delegation architecture: its only tool is `Agent`. It never reads or writes files directly — every operation goes through specialized subagents with JSON Schema output contracts.

### Pattern: Specialist routing via routing table

A skill includes a routing table so Claude knows which project owns which keyword:

| Keywords | Project | Context File |
|----------|---------|-------------|
| dashboard, ui, page, component | frontend-app | frontend-rules.md |
| schema, migration, model | database | backend-rules.md |

**Source**: `https://www.channel.tel/blog/enforce-orchestrator-pattern-claude-code`

### Pattern: cc-workspace — multi-repo orchestrator

An orchestrator (Opus) clarifies requirements, writes a plan, then delegates to teammates (Sonnet) who implement in parallel — each in their own repo, their own worktree, their own context. Session management for branch isolation across repos.

**Source**: `https://github.com/VincentVanN/cc-workspace` (2026-02-24)

| Role | Model | What it does |
|------|-------|-------------|
| **Orchestrator** | Opus 4.6 | Clarifies, plans, delegates, verifies |
| **Teammates** | Sonnet 4.6 | Implement in isolated worktree, test, commit |
| **Data extractors** | Haiku | Read-only. Collect raw data |
| **QA** | Sonnet 4.6 | Hostile mode, min 3 problems per service |

---

## 4. The "Project Portfolio" Approach

### Pattern: claude-ledger — portfolio-level awareness

A set of Claude Code hooks + CLI that automatically tracks activity across all projects, generates portfolio briefings at session start, and maps workstreams with cascade warnings.

**Source**: `https://github.com/claude-ledger/claude-ledger` (2026-03-22)

Claude Code's layered memory system + claude-ledger's addition:

```
Layer 1: CLAUDE.md          Per-project instructions
Layer 2: Auto-memory        Per-project facts
Layer 3: Todos/Tasks        Per-project work tracking
─────────────────────────────────────────────────
Layer 4: claude-ledger      Cross-project portfolio awareness  ← NEW
```

**Key features**:
- Automatic activity tracking via 5 hooks (PostToolUse, Stop, SessionEnd, SessionStart)
- Portfolio briefings with priority tiers and staleness detection
- Workstream dependency mapping with cascade warnings
- Git-backed for time-travel
- Concurrent session-safe (per-file locking, per-session IDs)

**Source**: same repo, `heuristic inference` section

> When you run `bootstrap`, claude-ledger infers project metadata:
> - >=10 commits/30d + CLAUDE.md → P1 (high priority)
> - >=3 commits/30d or has .mcp.json → P2 (medium)
> - Everything else → P3 (low)

### Pattern: Multi-Manus Planning Coordinator

A skill that extends the planning-with-files pattern with support for multiple projects, separate planning/source paths, and cross-machine sync via git.

**Source**: `https://github.com/kmichels/multi-manus-planning` (2026-01-09)

```
~/scripts/
├── .planning/
│   ├── index.md                    # Coordinator (active project, registry)
│   └── projects/
│       ├── project-a/ (task_plan.md, findings.md, progress.md)
│       └── project-b/
```

Session isolation via `.active.override.$CLAUDE_CODE_SESSION_ID` files. Multiple Claude Code sessions can work on different projects in the same workspace without conflicts.

---

## 5. Cross-Project Context Transfer

### Pattern: CLAUDE.md + SESSION.md split

Split permanent instructions (CLAUDE.md) from volatile session state (SESSION.md). SESSION.md tracks current progress, next steps, key decisions. Auto-recording during sessions, read at resume.

**Source**: `https://dev.to/odakin/solving-claude-codes-memory-loss-multi-project-design-patterns-3kjm` (DEV, 2026-03-20)

```
my-project/
├── CLAUDE.md      ← "How to work on this" (permanent)
└── SESSION.md     ← "Where we are now" (volatile)
```

> "How to Resume" → read SESSION.md → SESSION.md says exactly where to resume → Work continues.

### Pattern: work-bridge — cross-tool handoff

A local-first handoff tool that reads a source session, normalizes useful project context, and writes it into target tool format (CLAUDE.md, GEMINI.md, AGENTS.md).

**Source**: `https://github.com/jaeyoung0509/work-bridge` (2026-04-07)

Context preserved across tools:
- Task title and current goal
- Session summary and decisions
- Project instruction context (applied into CLAUDE.md, GEMINI.md, AGENTS.md)
- Project-scoped skills (materialized into native repo skill roots)
- Effective MCP config

### Pattern: handoff tool — context transfer via HANDOFF.md

Seamless context transfer, decision journaling, and workspace management for AI coding agents. Snapshotting file state, exporting intelligent diffs, recording architectural decisions, spawning agents side-by-side in tmux.

**Source**: `https://github.com/sahilraut22/Handoff` (2026-03-28)

Format: `HANDOFF.md` with YAML frontmatter. Decisions stored as YAML files in `.handoff/decisions/{id}.yaml`. Agent-to-agent IPC via tmux pane routing.

### Pattern: session-handoff — 5-phase end-of-session protocol

End-of-session handoff that captures all knowledge, dispatches output across canonical buckets, and prepares paste-ready prompts for next session.

**Source**: `https://github.com/wan-huiyan/session-handoff` (2026-04-02)

5 phases: Capture → Dispatch → Prepare → Commit/PR/Verify → Consolidate.
Consolidation triggers automatically when 3+ handoff docs exist, producing a single source-of-truth plan.

### Pattern: Workspine — repo-native delivery spine

Planning, phase artifacts, verification reports, and handoff checkpoints live in `.planning/`. Survives cold starts, runtime switches, and session loss.

**Source**: `https://github.com/PatrickSys/workspine` (2026-02-21)

> "When you switch runtimes or come back after a week, the repo still knows what was planned, what was executed, what was verified, and where you stopped."

### Pattern: Context packet (Claude Coordinator)

At session end, the coordinator writes `.coord/context-packet.md` — a compressed summary of current milestone, progress percentage, key decisions, open blockers, and state needed for resumption.

**Source**: `https://github.com/dennisonbertram/claude-coordinator`

### Pattern: claudew — tmux workspace manager with auto-context preservation

Named workspaces tied to specific repo directories, tmux-based sessions that survive terminal closures, fuzzy-finder selection (fzf). Each workspace maintains `context.md`, `decisions.md`, `continuation.md`.

**Source**: `https://github.com/pmossman/claudew/tree/v0.1.3` (2025-10-25)

---

## 6. Tooling and Scripts for Multi-Project Management

### claude-ledger (Python)
- Portfolio-level tracking across 10-50+ projects
- Auto-discovers projects, infers priority from activity
- Generate briefings, workstream cascade warnings
- **Install**: `pip install claude-ledger`
- **Source**: `https://github.com/claude-ledger/claude-ledger`

### claude-projects (Node.js) — `ccode` CLI
- Multi-project task dispatch with background execution
- Batch processing from YAML files
- Central config in `~/.claude-projects.yaml`
- **Install**: `npm install -g claude-projects`
- **Source**: `https://github.com/Mansuro/claude-projects`

### workspaces (Claude Code Plugin)
- Multi-repo workspace management
- Clone, setup, and coordinate multiple related repos
- Cross-project dependency awareness
- **Install**: Claude Code plugin marketplace
- **Source**: `https://github.com/patricio0312rev/workspaces`

### claude-coordinator (Shell/Plugin)
- 10-phase state machine orchestration
- Pure-delegation architecture
- JSON Schema output contracts
- TDD audit-trail commits
- **Install**: `claude plugin install claude-coordinator` or `./install.sh`
- **Source**: `https://github.com/dennisonbertram/claude-coordinator`

### claude-worktrees (Shell)
- Git worktree isolation for parallel Claude Code sessions
- Symlinked CLAUDE.md + copied `.claude/` config per workspace
- `task-new.sh` and `task-done.sh` scripts
- **Source**: `https://github.com/NullRabbitLabs/claude-worktrees`

### CLDPM (Python/TypeScript)
- Shared component management for monorepos
- Symlink-based distribution of skills, agents, hooks, rules
- Remote project support with sparse checkout
- **Install**: `pip install cldpm` or `npm install cldpm`
- **Source**: `https://github.com/transilienceai/cldpm`

### cc-workspace (Shell)
- Multi-repo orchestrator with session branch management
- Phase-based planning and parallel dispatch
- Source-branch-per-repo configuration
- **Source**: `https://github.com/VincentVanN/cc-workspace`

### claude-mpm (Python/Node.js)
- 47+ specialized agents, PM orchestration
- Tmux integration, MCP integration
- Event-driven inbox system for cross-project communication
- **Install**: `claude-mpm`
- **Source**: `https://github.com/bobmatnyc/claude-mpm`

### MemClaw (Claude Code Plugin)
- Persistent per-project workspaces
- Automatic tracking of living README, artifacts, tasks
- Cross-agent sharing (Claude Code, OpenClaw, Gemini CLI, Codex)
- Team sharing
- **Install**: Plugin marketplace from Felo Inc.
- **Source**: `https://memclaw.me` / `https://github.com/Felo-Inc/memclaw`

### work-bridge (Shell/Python)
- Cross-tool session handoff (Claude Code ↔ Codex ↔ OpenCode ↔ Cursor)
- Materializes context as instruction files + skills + MCP config
- **Source**: `https://github.com/jaeyoung0509/work-bridge`

### Handoff (Shell)
- Context transfer, decision journaling, agent IPC via tmux
- HANDOFF.md v2.0 protocol with YAML frontmatter
- **Source**: `https://github.com/sahilraut22/Handoff`

### session-handoff (Skill)
- 5-phase end-of-session capture and consolidation
- 7 canonical doc buckets taxonomy
- Doc-freshness reverse-lint
- **Source**: `https://github.com/wan-huiyan/session-handoff`

### Workspine (Skill/CLI)
- 14 workflows, 10 roles, pause/resume
- Preflight gates before execution
- Runtime-agnostic (Claude Code, Codex, Cursor, Copilot, Gemini)
- **Source**: `https://github.com/PatrickSys/workspine`

### multi-manus-planning (Skill)
- Multi-project planning coordinator with session isolation
- Obsidian vault integration, cross-machine git sync
- **Source**: `https://github.com/kmichels/multi-manus-planning`

### claudew (Shell)
- tmux-powered workspace manager
- Auto-context preservation (context.md, decisions.md, continuation.md)
- Fuzzy finder for project switching
- **Source**: `https://github.com/pmossman/claudew/tree/v0.1.3`

---

## 7. Community Best Practices for Dozens of Projects

### Use the 3-Layer Configuration

For 10+ projects:
- Layer 1 (global `~/.claude/CLAUDE.md`): universal rules, learned lessons
- Layer 2 (per-project `CLAUDE.md`): stack, constraints, key facts (14 key learnings, 11 "don't do this" rules)
- Layer 3 (agent definitions in `~/.claude/agents/*.md`): model assignment per role

**Source**: `https://doneyli.substack.com/p/the-3-layer-claude-code-configuration`

> "When I learn something the hard way in one project (like 'never remove Docker resource limits'), every project benefits immediately."

### Don't Work on Two Projects in One Session

Dedicate each Claude Code session to one project. Start session, load context, do work, end session.

**Source**: `https://felo.ai/blog/claude-code-multiple-projects-guide/`

> "Even with workspace isolation, it's cleaner to dedicate each Claude Code session to one project. Mixing projects in one conversation increases the chance of context bleed."

### Keep CLAUDE.md Under 200 Lines / 10K Words

For reliable adherence by the model. Claude reliably follows rules in the first 200 lines and intermittently ignores rules deeper in the file.

**Source**: `https://deepwiki.com/shanraisshan/claude-code-best-practice/4.6-project-structure` (DeepWiki, 2026-04-13)

**Source**: `https://inventivehq.com/knowledge-base/claude/how-to-work-with-large-codebases` (InventiveHQ)

### Use `permissions.deny` in `.claude/settings.json`

List commands and file paths Claude should refuse to touch. Commit to the repo so exclusions are version-controlled and apply to every contributor.

**Source**: `https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start` (Anthropic playbook)

> "Committing permissions.deny rules in .claude/settings.json means the exclusions are version-controlled."

### The Agent Teams Decision Tree

1. **Single agent** for single-project work
2. **Subagents** when task crosses project boundaries with different conventions (3+ distinct steps across projects)
3. **Agent Teams** when agents need to coordinate (API contract discussion between backend/frontend)
4. **External orchestrators** (Tier 2) when you need visual oversight of 5+ agents

Source: `https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern`

### Schedule Harness Review Every 3-6 Months

A CLAUDE.md rule that was useful on older models might become friction on newer models. Review after every major model release.

**Source**: `https://claudefa.st/blog/guide/development/large-codebase-playbook`

> "A CLAUDE.md rule that tells Claude to break every refactor into single-file changes was a useful constraint on older models... On a newer model that handles them well, that same rule becomes friction."

### Use Worktrees for Isolation, Not for Architecture

Git worktrees isolate file edits and prevent merge conflicts, but they do not solve architecture, contract consistency, or testing strategy.

**Source**: `https://www.aakashx.com/blog/parallel-claude-code-agents/` (Aakash Ahuja, 2026-05-16)

> "The safest workflow: plan first, scaffold shared contracts, split by ownership boundary, dispatch agents in worktrees, run targeted tests, merge in dependency order, then run an integrated validation pass."

### The DRY Onion Ordering

Inner layers first, outer layers last: Backend → SDK → UI. This prevents the cross-layer contract mismatch problem.

**Source**: `https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern`

### Maximum 7 Parallel Agents

Claude Code can spin up a maximum of 7 parallel agents. In practice: 3-4 on 4-core, 5-6 on 8-core, 7 on 16+ cores.

**Source**: `https://claudelab.net/en/articles/claude-code/claude-code-parallel-development-mastery` (Claude Lab, 2026-03-30)

### CLAUDE.md is Your Operating System

At scale, CLAUDE.md is not project documentation — it is the operating system for your agent. Layered files, scoped rules, codebase maps, ignore files, and permission denies form a complete context engineering harness.

**Source**: `https://claudefa.st/blog/guide/development/large-codebase-playbook`

> "The model is one ingredient. The harness around it is the rest."
