# 🔱 Research: Claude Code vs Claude Projects — Deep Comparison
**AP Token**: `AP-RESEARCH-CODE-vs-PROJECTS-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ RESEARCH
**Status**: Complete | **Date**: 2026-05-22

---

## §1 Fundamental Architectural Difference

### Claude Code — Terminal-Native Agentic Loop

Claude Code is a **terminal-native AI coding agent** built on an agentic loop (gather context → take action → verify results). It runs as a CLI process, has direct filesystem access, can execute shell commands, and edits files in place.

- **Runtime**: Bun (not Node.js), ~512K lines TypeScript across 1,900+ files (90% written by Claude itself). [Source: DuoCode anatomy, 2026-03-31](https://duocodetech.com/blog/claude-code-anatomy)
- **Core architecture**: `AsyncGenerator`-based query loop (`query.ts`). The model proposes tool calls, the agent executes them, feeds results back, and repeats until the task is complete. [Source: Claude Code official docs](https://code.claude.com/docs/en/how-claude-code-works)
- **~40 built-in tools** across 5 categories: file operations, search, execution (shell), web, code intelligence. Plus tools for spawning subagents, asking questions, orchestration. [Source: Claude Code official docs](https://code.claude.com/docs/en/how-claude-code-works)
- **Three execution environments**: Local (your machine), Cloud (Anthropic-managed VMs), Remote Control (browser-based). [Source: same]
- **Multiple interfaces**: Terminal, Desktop app, VS Code/JetBrains extensions, claude.ai/code, Slack, CI/CD (GitHub Actions, GitLab CI). Same agentic loop across all. [Source: same]
- **Context window**: Up to 1M tokens (Opus 4.6/Sonnet 4.6), 200K default. [Source: Claude Code docs — "when context fills up" section]
- **Permission system**: 7-mode layered pipeline — deny-first rule evaluation, ML-based auto-mode classifier (YOLO), user prompts, coordinator handlers. [Source: Rivista.ai journal paper "Dive into Claude Code", 2026-04](https://www.rivista.ai/wp-content/uploads/2026/04/2604.14228v1.pdf)
- **UI**: Custom Ink (React) terminal rendering with Yoga WASM layout engine, double-buffered at 16ms (60fps in terminal). [Source: DuoCode anatomy](https://duocodetech.com/blog/claude-code-anatomy)
- **Settings hierarchy**: 4 scopes — Enterprise (managed), User (`~/.claude/settings.json`), Project (`.claude/settings.json`), Local (`.claude/settings.local.json`). [Source: Claude Code docs — settings](https://code.claude.com/docs/en/settings)
- **Session persistence**: Conversations saved as plaintext JSONL under `~/.claude/projects/`. Resume with `--continue`/`--resume`, fork with `--fork-session`/`/branch`. [Source: Claude Code docs — sessions section](https://code.claude.com/docs/en/how-claude-code-works)

### Claude Projects — Web-Based Persistent Workspace

Claude Projects is a **web-based persistent workspace** on claude.ai. It provides a shared knowledge base (uploaded documents), custom instructions (system prompt extension), and organized chat history — all scoped to a single project.

- **Three core components**: Knowledge Base (uploaded documents), Custom Instructions (persistent system prompt), Chat History (grouped conversations). [Source: Claude Help Center — "What are projects?"](https://support.anthropic.com/en/articles/9517075-what-are-projects)
- **No filesystem access**: Projects cannot read local files. Users must explicitly upload documents (PDF, DOCX, TXT, MD, code files, CSV, HTML). Max 20 files per chat, 30MB each. [Source: Suprmind — Claude Features 2026](https://suprmind.ai/hub/claude/features/)
- **Context window**: 200K tokens on paid plans (Pro, Max, Team), 500K on Enterprise. [Source: fwdslash.ai — "What Is a Claude Project?"](https://www.fwdslash.ai/blog/what-is-a-claude-project)
- **RAG mode**: Automatically activates when project knowledge approaches the context window limit (~150K tokens). Expands effective capacity up to 10x. Uses a "project knowledge search tool" for semantic retrieval. [Source: Claude Help Center — "RAG for projects"](https://support.anthropic.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)
- **No agentic loop**: Claude responds to prompts but does not autonomously read files, run commands, or iterate on outputs. No tool-calling loop for codebase operations.
- **Available across**: Web (claude.ai), iOS/Android apps, Claude Desktop. [Source: inkeybit — "Claude Projects Complete Guide 2026"](https://www.inkeybit.com/blog/claude-projects-complete-guide)
- **Team access**: Available on Team and Enterprise plans — shared knowledge base, collaborative editing. [Source: same]

---

## §2 CLAUDE.md vs Project Instructions/Knowledge — Are They the Same?

### They Are NOT the Same Format

| Dimension | Claude Code CLAUDE.md | Claude Projects Custom Instructions |
|-----------|----------------------|-------------------------------------|
| **Format** | Plain markdown file on filesystem | Text input field in claude.ai UI |
| **Location** | `./CLAUDE.md`, `~/.claude/CLAUDE.md`, `./.claude/rules/*.md`, etc. | In-browser, stored on Anthropic servers |
| **Scope** | Hierarchical — global → user → project → local → subdirectory → path-scoped rules | Single flat set of instructions per project |
| **Conditional loading** | Yes — path-scoped rules via YAML frontmatter (`paths:` field) | No |
| **Imports** | Yes — `@path/to/file` syntax, recursive (max 5 hops) | No |
| **File organization** | Modular `.claude/rules/` directory, subdirectory CLAUDE.md files on demand | Single monolithic instructions field |
| **Version control** | Yes — committed to git (team-shared) | No — stored on Anthropic servers |
| **Auto-generated** | Yes — `/init` command analyzes codebase | No |
| **Custom slash commands** | Yes — define in CLAUDE.md, type `/command-name` | No |
| **Loaded into** | Context as a user message after system prompt | System prompt extension (every conversation in project) |
| **Size limit** | Recommended <200 lines per file | No hard limit (bounded by context window) |
| **Skill/hook/command support** | Yes — skills (on-demand), hooks (event-triggered scripts), commands (`/name`) | No — none of these exist in Projects |

Sources:
- [Claude Code docs — Memory/CLAUDE.md](https://code.claude.com/docs/en/memory)
- [SFEIR Institute — CLAUDE.md Memory System Deep Dive](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/)
- [Claude Code Guides — CLAUDE.md Best Practices 2026](https://claudecodeguides.com/claude-code-claude-md-best-practices/)
- [StackNotice — CLAUDE.md Ultimate Guide 2026](https://stacknotice.com/blog/claude-code-claude-md-ultimate-guide-2026)

### Claude Code's CLAUDE.md Hierarchy (6 levels)

| Level | Location | Loaded | Shared |
|-------|----------|--------|--------|
| Managed Policy | `/etc/claude-code/CLAUDE.md` (Linux) | Every session | All org users |
| User | `~/.claude/CLAUDE.md` | Every session | Just you |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Every session | Team (via git) |
| Project Rules | `.claude/rules/*.md` | Every session or on path match | Team (via git) |
| Local | `./CLAUDE.local.md` | Every session | Just you (gitignored) |
| Auto Memory | `~/.claude/projects/*/memory/MEMORY.md` | Every session (first 200 lines/25KB) | Just you (machine-local) |
| Subdirectory | `./subdir/CLAUDE.md` | On demand when Claude reads files in that dir | Team (via git) |

Source: [Claude Code docs — Memory](https://code.claude.com/docs/en/memory)

### Claude Projects' Knowledge Architecture

- **Knowledge Base**: Files uploaded to the project — PDF, DOCX, TXT, MD, code, CSV, HTML. No format enforcement. [Source: Claude Help Center](https://support.anthropic.com/en/articles/9517075-what-are-projects)
- **Custom Instructions**: A single text field that applies to every conversation as a system prompt extension. No structured format required. [Source: same]
- **PRISM methodology**: The community-developed best practice for Projects is to use a "conductor pattern" — keep instructions short (4K-8K chars), split domain knowledge into operational and reference files, use YAML frontmatter for semantic triggers. [Source: GitHub — ArchiJones-AI/PRISM v3.4](https://github.com/ArchiJones-AI/PRISM)
- **No auto-memory**: Claude Projects has "Memory" as a separate feature (not project-scoped) — Claude saves facts about you across all conversations. [Source: StackNotice — "Claude Projects and Memory: The Complete Guide"](https://stacknotice.com/blog/claude-projects-memory-guide-2026)

> **Key difference**: CLAUDE.md is a **hierarchical file system of modular, conditionally-loaded instructions** that teams version-control. Projects' instructions are a **single flat text field** combined with a **RAG-indexed document store**.

---

## §3 Memory/Context Persistence Model

### Claude Code — Dual-Layer Memory

| Layer | What | Who Writes | Loaded How |
|-------|------|-----------|------------|
| **CLAUDE.md** (instructions) | Persistent rules, conventions, commands | Human | Every session, in full (injected as user message after system prompt) |
| **Auto Memory** (learnings) | Build commands, debugging insights, patterns Claude discovers | Claude (automatic) | Every session, first 200 lines or 25KB of MEMORY.md |

- Auto memory is **machine-local**, stored at `~/.claude/projects/<project>/memory/`. Not shared across worktrees or cloud.
- Claude decides what to save — it "decides what's worth remembering based on whether the information would be useful in a future conversation." [Source: Claude Code docs — Auto memory](https://code.claude.com/docs/en/memory#auto-memory)
- Auto memory can be toggled via `/memory` or `autoMemoryEnabled` setting.
- Context compaction is automatic: Claude clears older tool outputs first, then summarizes conversation if needed. Project-root CLAUDE.md survives compaction (re-reads from disk). Nested CLAUDE.md files reload on demand. [Source: Claude Code docs — context window section](https://code.claude.com/docs/en/how-claude-code-works)
- **Subagent memory**: Subagents get their own fresh context window. Their work does NOT bloat the main conversation context. Fork subagents can inherit parent context. [Source: Claude Code docs — subagents](https://code.claude.com/docs/en/sub-agents)

### Claude Projects — Hybrid Context/RAG Model

| Tier | Scope | Content | Persistence |
|------|-------|---------|------------|
| Knowledge Base | All Project conversations | Uploaded documents | Until manually removed |
| Custom Instructions | All Project conversations | Role and behavior rules | Until manually edited |
| Conversation History | Single conversation | Dialogue turns, tool calls, artifacts | Archived with conversation |

- **Below ~150K tokens**: Project content loads directly into the context window (full visibility). [Source: Claude Help Center — RAG for Projects](https://support.anthropic.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)
- **Above ~150K tokens**: RAG activates automatically. Claude uses a "project knowledge search tool" — semantic retrieval of relevant chunks instead of loading everything. Up to 10x expansion. [Source: same]
- **No cross-conversation memory**: "Notably, memory does not automatically transfer between separate conversations within a Project." If a decision is made in Conversation A, Claude does not know about it in Conversation B unless it's in the Knowledge Base or Custom Instructions. [Source: YiteAI Tools — "Claude Managed Agents Overview"](https://tools.yiteai.com/en/books/claude-guide/ch29)
- **Separate Memory feature**: Claude also has a user-level "Memory" that saves facts across all conversations (not project-scoped). Claude saves automatically; users can instruct it to remember/forget. [Source: StackNotice — "Claude Projects and Memory"](https://stacknotice.com/blog/claude-projects-memory-guide-2026)

### Key Contrast

| | Code (CLAUDE.md + Auto Memory) | Projects (KB + Instructions) |
|---|---|---|
| **Persistence model** | File-based, hierarchical, conditionally loaded | RAG-based retrieval from document store |
| **Cross-session** | Yes — CLAUDE.md + auto memory load every session | Yes — KB + instructions always present |
| **Cross-conversation** | N/A (single conversation at a time) | NO — conversations are isolated |
| **Machine-local** | Yes — files on disk | No — stored on Anthropic servers |
| **Version controlled** | Yes — CLAUDE.md committed to git | No |
| **Capacity** | Bounded by context window + compaction | Up to 10x context via RAG |

---

## §4 When to Use One vs the Other

### Claude Code — Use When

1. **Working on a real codebase** — Claude needs to read, edit, and write files across the project. [Source: AI Codex — "Claude Code vs the web app"](https://www.aicodex.to/articles/claude-code-vs-web-app)
2. **Multi-file tasks and refactoring** — Renaming, restructuring, updating patterns across many files. [Source: same]
3. **Running commands** — Build, test, lint, git operations, CI/CD pipelines. [Source: Ready Solutions AI — "Claude vs Claude Code"](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/)
4. **Debugging with full context** — Read error output, search source, fix, re-run. [Source: same]
5. **Terminal-native or SSH workflows** — Works over SSH, tmux, Docker, any terminal. [Source: Buildberg — "How Claude Code Actually Works"](https://www.buildberg.co/blog/claude-code-complete-guide)
6. **CI/CD automation** — Headless mode (`-p` flag) for pipelines. [Source: same]
7. **Large refactors needing 1M token context** — Surfacing connections across frontend, backend, database. [Source: ClaudeGuide — "Claude Code vs GitHub Copilot"](https://claudeguide.io/claude-code-vs-github-copilot)
8. **Sub-agent orchestration** — Spawning parallel workers for independent tasks. [Source: Claude Code docs](https://code.claude.com/docs/en/how-claude-code-works)

### Claude Projects — Use When

1. **Planning, strategy, design thinking** — Brainstorming, architecture decisions, reframing problems. [Source: Ready Solutions AI](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/)
2. **Document-heavy research** — Policy libraries, client materials, recurring reference docs. [Source: c-ai.chat — "How Claude Handles Long Documents"](https://c-ai.chat/features/how-claude-processes-long-documents/)
3. **Knowledge work that benefits from RAG** — Large corpuses that don't fit in context, need selective retrieval. [Source: same]
4. **Non-developer professionals** — Attorneys, consultants, therapists, researchers — anyone who doesn't need terminal access. [Source: The AI Career Lab](https://theaicareerlab.com/blog/claude-code-vs-claude-ai-which-one)
5. **Persistent workspaces for recurring tasks** — Same documents referenced daily/weekly. [Source: inkeybit — "Claude Projects Complete Guide 2026"](https://www.inkeybit.com/blog/claude-projects-complete-guide)
6. **Artifact-heavy outputs** — Interactive React components, SVGs, HTML dashboards, diagrams (Projects supports Artifacts, Code does not). [Source: ShareDuo — "Claude artifacts vs Claude Code"](https://www.shareduo.com/blog/claude-artifacts-vs-claude-code)
7. **Collaboration with non-technical team members** — Team/Enterprise sharing, no setup required. [Source: ESPO.AI — "Complete Guide to Claude Projects"](https://espo.ai/resources/claude-projects-guide)
8. **Quick prototypes to show stakeholders** — Zero setup, shareable via link. [Source: ShareDuo](https://www.shareduo.com/blog/claude-artifacts-vs-claude-code)

---

## §5 Best Practices for Combining Them

### The Three-Stage Workflow (Recommended by Anthropic docs and community)

| Stage | Tool | What Happens |
|-------|------|-------------|
| **1. Plan/Design** | Claude Projects | Architecture decisions, research, spec writing. Project holds permanent context (docs, style guides, requirements). |
| **2. Plan Mode** | Claude Code (Plan Mode) | Read-only analysis of the actual codebase. Produces file-by-file plan with verification steps. |
| **3. Implementation** | Claude Code (execution) | Autonomous multi-file changes, tests, git commits. |

Source: [Ready Solutions AI](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/)

### Typical Daily Split (from practitioners)

- **Claude.ai Projects** for: Persistent context about the project (architecture docs, API specs, coding standards), research tasks, brainstorming, writing documentation.
- **Claude Code** for: Actual file editing, running tests, debugging, refactoring, PR reviews, CI/CD automation.

Source: [StackNotice — "Claude Projects and Memory"](https://stacknotice.com/blog/claude-projects-memory-guide-2026)

### Connection Between the Two

From Anthropic's official docs:
- "Claude.ai Project stores: The API spec, architecture diagram, and coding standards for the SaaS project they're building."
- "CLAUDE.md in the repo stores: The exact rules Claude Code should follow when editing files — patterns, forbidden patterns, test locations."

They serve complementary roles: Projects holds "what" and "why" (knowledge docs), CLAUDE.md holds "how" (editorial rules). [Source: StackNotice](https://stacknotice.com/blog/claude-projects-memory-guide-2026)

### The "Three or More Rounds" Heuristic

"If you find yourself having three or more rounds of Claude Code tangling in implementation detail when you haven't written a line of code yet, that's a design conversation you're having in the wrong surface. Switch to Claude.ai." — [Ready Solutions AI](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/)

And conversely: "If you find yourself asking Claude.ai to produce a specific code change and then copy-pasting the output into your editor, you're doing manual work Claude Code would do for you. Switch."

---

## §6 Features Exclusive to Each Product

### Features Exclusive to Claude Code

| Feature | Description | Source |
|---------|-------------|--------|
| **Sub-agents** | Spawn independent agent instances with isolated context windows, custom tools, and permissions. Can run in foreground, background, or parallel. Built-in types: Explore (read-only), Plan, General-purpose. Custom agents via `.claude/agents/*.md`. | [Claude Code docs — subagents](https://code.claude.com/docs/en/sub-agents), [Anthropic blog — "Subagents in Claude Code"](https://claude.com/blog/subagents-in-claude-code) |
| **Hooks** | Shell commands that auto-execute at lifecycle events: PreToolUse, PostToolUse, InstructionsLoaded, PreCommit, etc. 27 event types. Can block/rewrite/annotate tool calls. | [Claude Code docs — hooks](https://code.claude.com/docs/en/hooks), [Rivista.ai paper](https://www.rivista.ai/wp-content/uploads/2026/04/2604.14228v1.pdf) |
| **Skills** | On-demand instruction sets defined as SKILL.md files. Lazy-loaded (only descriptions loaded at startup, full content when invoked). Can include argument substitution, inline shell commands. | [Claude Code docs — skills](https://code.claude.com/docs/en/skills), [Buildberg guide](https://www.buildberg.co/blog/claude-code-complete-guide) |
| **MCP (Model Context Protocol)** | Connect external tools as MCP servers. 4 transport variants: stdio, SSE, HTTP, WebSocket, SDK. Subagents can inherit MCP tools. | [Claude Code docs — MCP](https://code.claude.com/docs/en/mcp), [yanchuk gist](https://gist.github.com/yanchuk/0c47dd351c2805236e44ec3935e9095d) |
| **Custom slash commands** | Define `/command-name` in CLAUDE.md that executes multi-step workflows. | [StackNotice — CLAUDE.md Ultimate Guide](https://stacknotice.com/blog/claude-code-claude-md-ultimate-guide-2026) |
| **Full shell execution** | Run any bash command with a 7-mode permission system. Git operations, package management, build tools. | [Claude Code docs](https://code.claude.com/docs/en/how-claude-code-works) |
| **CI/CD integration** | Headless mode with `-p` flag, GitHub Actions, GitLab CI. JSON output for programmatic consumption. | [same] |
| **Plan Mode** | Read-only mode that forces Claude to create a plan before editing. | [same] |
| **Auto Mode** (research preview) | ML-classifier-based autonomous tool approval. | [same] |
| **Checkpoints** | Automatic file snapshots before every edit. Reversible with `Esc` key. | [same] |
| **Fork subagents** | Subagents that inherit the full parent conversation context (byte-identical prefix for prompt cache optimization). | [Claude Code docs — subagents](https://code.claude.com/docs/en/sub-agents), [Dive into Claude Code paper](https://www.rivista.ai/wp-content/uploads/2026/04/2604.14228v1.pdf) |
| **Git worktree isolation** | Subagents can operate in isolated git worktrees — separate copies of the repo. | [Claude Code docs — subagents](https://code.claude.com/docs/en/sub-agents) |
| **Plugins** | Community-created packages with tools, hooks, commands. Distributed via plugin marketplace. | [Claude Code docs — plugins](https://code.claude.com/docs/en/plugins) |
| **Remote Control** | Browser-based control of local machine Claude Code sessions. | [Claude Code docs](https://code.claude.com/docs/en/how-claude-code-works) |
| **Ultrareview** (research preview) | Cloud-based fleet of bug-hunting agents against a branch or PR. | [Claude Code docs — Week 17](https://code.claude.com/docs/en/whats-new/2026-w17) |
| **Session recap** | One-line summary when returning to a backgrounded session. | [same] |
| **Custom themes** | Build and switch between named color themes. | [same] |
| **Routines/background tasks** | Scheduled and background execution (desktop). | [Claude Code docs](https://code.claude.com/docs/en/how-claude-code-works) |
| **Stdin/stdout control protocol** | Programmatic control via JSON messages over stdin/stdout. Powers VS Code, JetBrains extensions. | [Buildberg guide](https://www.buildberg.co/blog/claude-code-complete-guide) |

### Features Exclusive to Claude Projects

| Feature | Description | Source |
|---------|-------------|--------|
| **RAG knowledge base** | Upload documents — Claude automatically indexes and retrieves relevant chunks via semantic search. Up to 10x context expansion. | [Claude Help Center — RAG for Projects](https://support.anthropic.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects) |
| **Artifacts** | Claude can generate interactive, renderable outputs: React components, HTML pages, SVGs, Mermaid diagrams, code. Live preview in the chat window. Since April 2026, live artifacts can connect to MCP servers. | [Suprmind — Claude Features 2026](https://suprmind.ai/hub/claude/features/), [ShareDuo](https://www.shareduo.com/blog/claude-artifacts-vs-claude-code) |
| **Web-based access** | Zero setup — works in any browser on any machine. No installation required. | [AI Codex](https://www.aicodex.to/articles/claude-code-vs-web-app) |
| **Mobile/tablet access** | iOS and Android apps. | [inkeybit](https://www.inkeybit.com/blog/claude-projects-complete-guide) |
| **Google Workspace connectors** | Direct integration with Google Drive, Docs, Sheets, Gmail for Research mode. | [Claude Help Center](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors) |
| **Research mode** | Agentic research combining web search, Google Workspace access, and integrations for multi-source reports. | [Suprmind](https://suprmind.ai/hub/claude/features/) |
| **Claude Design** | Visual design canvas (since April 2026). | [Ready Solutions AI](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/) |
| **Team collaboration** | Shared projects, knowledge base, and instructions across team members on Team/Enterprise plans. | [Claude Help Center](https://support.anthropic.com/en/articles/9517075-what-are-projects) |
| **Pre-built Skills (web)** | PowerPoint, Excel, Word, PDF skills on all plans (bundled). | [Ready Solutions AI](https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/) |
| **No installation** | Works on any machine with a browser — university labs, work computers, managed devices. | [The AI Career Lab](https://theaicareerlab.com/blog/claude-code-vs-claude-ai-which-one) |
| **Cross-machine persistence** | Project knowledge, instructions, memory stored on Anthropic servers — accessible from any device. | [ESPO.AI](https://espo.ai/resources/claude-projects-guide) |
| **Image analysis** | Upload and analyze images (PNG, JPEG, GIF, WEBP) for vision-enabled models. | [Suprmind](https://suprmind.ai/hub/claude/features/) |
| **Cowork integration** (Desktop) | Desktop app "Cowork" tab allows Claude to read/edit local files with GUI — a bridge between Projects (no FS access) and Code (terminal-only). | [inkeybit](https://www.inkeybit.com/blog/claude-projects-complete-guide) |

---

## §7 Summary Data Sources

| Source | URL |
|--------|-----|
| Claude Code official documentation | https://code.claude.com/docs/en/how-claude-code-works |
| Claude Code Memory docs | https://code.claude.com/docs/en/memory |
| Claude Code settings docs | https://code.claude.com/docs/en/settings |
| Claude Code subagents docs | https://code.claude.com/docs/en/sub-agents |
| Anthropic blog — Subagents in Claude Code | https://claude.com/blog/subagents-in-claude-code |
| Claude Code Week 17 release notes | https://code.claude.com/docs/en/whats-new/2026-w17 |
| Claude Help Center — RAG for Projects | https://support.anthropic.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects |
| Claude Help Center — What are projects? | https://support.anthropic.com/en/articles/9517075-what-are-projects |
| Claude Help Center — Context window size | https://support.claude.com/en/articles/8606394-how-large-is-the-context-window-on-paid-claude-plans |
| Claude Help Center — CLAUDE.md guide | https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts |
| Rivista.ai — Dive into Claude Code academic paper | https://www.rivista.ai/wp-content/uploads/2026/04/2604.14228v1.pdf |
| DuoCode — Claude Code anatomy (source analysis) | https://duocodetech.com/blog/claude-code-anatomy |
| yanchuk gist — Architecture deep dive | https://gist.github.com/yanchuk/0c47dd351c2805236e44ec3935e9095d |
| wayou gist — Architecture report with Mermaid | https://gist.github.com/wayou/a94f2bc6e2d2a3f87148f6a38bc3db0b |
| Claude code from source — Ch 8 sub-agents | https://claude-code-from-source.com/ch08-sub-agents/ |
| FlorianBruniaux — Claude Code ultimate guide | https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/guide/ultimate-guide.md |
| GitHub — PRISM Project methodology | https://github.com/ArchiJones-AI/PRISM |
| Ready Solutions AI — Claude vs Claude Code | https://readysolutions.ai/blog/2026-04-20-claude-vs-claude-code-when-to-use-each/ |
| AI Codex — Claude Code vs web app | https://www.aicodex.to/articles/claude-code-vs-web-app |
| Buildberg — How Claude Code Actually Works | https://www.buildberg.co/blog/claude-code-complete-guide |
| The AI Career Lab — Which do you need? | https://theaicareerlab.com/blog/claude-code-vs-claude-ai-which-one |
| ShareDuo — Artifacts vs Claude Code | https://www.shareduo.com/blog/claude-artifacts-vs-claude-code |
| inkeybit — Claude Projects Complete Guide | https://www.inkeybit.com/blog/claude-projects-complete-guide |
| ESPO.AI — Complete Guide to Claude Projects | https://espo.ai/resources/claude-projects-guide |
| StackNotice — CLAUDE.md Ultimate Guide | https://stacknotice.com/blog/claude-code-claude-md-ultimate-guide-2026 |
| StackNotice — Projects and Memory | https://stacknotice.com/blog/claude-projects-memory-guide-2026 |
| SFEIR Institute — CLAUDE.md Memory System | https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/ |
| SFEIR Institute — Deep Dive | https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/ |
| Claude Code Guides — CLAUDE.md Best Practices | https://claudecodeguides.com/claude-code-claude-md-best-practices/ |
| Claude Code Guides — Skills vs Hooks vs Commands | https://claudecodeguides.com/claude-code-skills-vs-hooks-vs-commands-2026/ |
| ClaudeLab — Mastering Claude Projects | https://claudelab.net/en/articles/claude-ai/claude-projects-advanced-knowledge-workflow |
| ClaudeLab — Custom Subagents | https://claudelab.net/en/articles/claude-code/claude-code-custom-subagents-at-mention-guide |
| Suprmind — Claude Features 2026 | https://suprmind.ai/hub/claude/features/ |
| fwdslash.ai — What Is a Claude Project? | https://www.fwdslash.ai/blog/what-is-a-claude-project |
| Dev Community — Complete Guide to CLAUDE.md | https://dev.to/serenitiesai/the-complete-guide-to-claudemd-files-for-ai-development-2026-4316 |
| Developers Digest — How to Write CLAUDE.md | https://www.developersdigest.tech/blog/how-to-write-claudemd-the-complete-guide |
| YiteAI Tools — Claude Managed Agents Overview | https://tools.yiteai.com/en/books/claude-guide/ch29 |
| Subagent delegation patterns (OpenClaw Academy) | https://inbounter.com/learn/claude/workflows/subagents |
| GitHub bug report — Agent tool not available to subagents | https://github.com/anthropics/claude-code/issues/46424 |
| GitHub — Claude Code architecture docs | https://github.com/nirholas/claude-code/blob/main/docs/architecture.md |
