# AGENTS.md & Rules Ecosystem Evolution — Practical Guide (2025‑2026)

**AP Token**: `AP-AGENTS-MD-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_agents_md ⬡ ACTIVE

**Date**: 2026-08-18
**Purpose**: How teams actually structure AGENTS.md + rules/ hierarchy, rule formats agents follow, and how corrections become persistent rules in practice.

---

## Executive Summary

**AGENTS.md** emerged mid‑2025 as the **cross‑platform standard** for instructing AI coding agents (Claude Code, Cursor, OpenAI Codex, Devin, Amp, Jules, Factory). By 2026, it's the de‑facto configuration layer. The ecosystem that works:
- **Three‑tier hierarchy**: Global → Project → User/Rules
- **Imperative format with code examples** — not prose
- **Corrections → new rule files** versioned alongside code
- **Single source of truth** — no mixing with CLAUDE.md, .cursor/rules, config.toml

---

## 1. The Standard — agents.md

### Official Spec
| Source | URL | Access |
|--------|-----|--------|
| agents.md (official site) | <https://agents.md/> | ✅ |
| DeepWiki: AGENTS.md Format Documentation | <https://deepwiki.com/openai/agents.md/5-agents.md-format-documentation> | ✅ |
| OpenAI/agents.md GitHub | <https://github.com/openai/agents.md> | ✅ |

### Core Principles
1. **Plain Markdown** at repo root (`AGENTS.md`)
2. **No required fields** — but conventions emerged
3. **Loading order**: Global → Project → Nested (directory‑specific)
4. **Conflict resolution**: Later files override earlier; explicit `!override` syntax
5. **Tool‑agnostic** — works with any agent that implements the spec

---

## 2. Three‑Tier Hierarchy That Works

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: GLOBAL (per user/machine)                              │
│  ~/.config/opencode/AGENTS.md   (or ~/.claude/AGENTS.md, etc.)  │
│  • User preferences: language, style, default tools             │
│  • Global security rules: "never commit secrets"                │
│  • Loaded FIRST, lowest precedence                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: PROJECT (per repository)                               │
│  /path/to/repo/AGENTS.md                                        │
│  • Project overview, build/test commands                        │
│  • Architecture constraints, coding standards                   │
│  • Security notes, dependency policies                          │
│  • **Primary source of truth** — highest precedence             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: RULES DIRECTORY (path‑specific overrides)              │
│  /path/to/repo/rules/                                           │
│  ├── backend.md         # API / database rules                  │
│  ├── frontend.md        # React / TypeScript rules              │
│  ├── testing.md         # Test patterns, coverage requirements  │
│  ├── security.md        # Auth, secrets, validation rules       │
│  └── deployment.md      # CI/CD, environment rules              │
│  • Loaded AFTER project AGENTS.md                               │
│  • Path‑specific: rules/backend.md applies only under /backend  │
│  • **Corrections become new files here**                        │
└─────────────────────────────────────────────────────────────────┘
```

### Loading Order (per spec)
```
1. Global AGENTS.md
2. Project AGENTS.md
3. rules/*.md (alphabetical, but path‑specific matching applies)
4. Nested AGENTS.md in subdirectories (if any)
```
**Override rule**: Later wins. Explicit `!override` tag in rule file forces precedence.

---

## 3. Rule Format Agents Actually Follow

### ❌ What Fails (Prose / Vague)
```markdown
## Code Style
Please write clean, maintainable code. Follow best practices.
Use TypeScript strictly. Don't use any.
```

### ✅ What Works (Imperative + Examples)
```markdown
## Code Style — TypeScript

# rule: Use strict TypeScript — no `any`, no implicit any
# rule: Prefer `interface` over `type` for object shapes
# rule: Explicit return types on all exported functions

# example: GOOD
interface User {
  id: string;
  name: string;
  email: string;
}

function getUser(id: string): Promise<User> {
  return db.users.find(id);
}

# example: BAD
function getUser(id) {  // implicit any
  return db.users.find(id);  // no return type
}

const user: any = getUser("123");  // any forbidden
```

### Format Specification (from agents.md spec + community consensus)
| Element | Syntax | Purpose |
|---------|--------|---------|
| **Rule** | `# rule: <imperative statement>` | Machine‑parsable directive |
| **Example** | `# example: <GOOD|BAD>` + code block | Few‑shot for agent |
| **Override** | `# override: <reason>` | Forces precedence |
| **Context** | `# context: <file glob>` | Limits rule scope |
| **Tool** | `# tool: <tool_name>` | Applies when tool used |

### Real‑World Example (from BuildBetter 2026 guide)
```markdown
# AGENTS.md — Acme Corp Backend

## Project Overview
REST API for user management. Go 1.22, PostgreSQL, gRPC.

## Build & Test
# rule: Run `go build ./...` before commit
# rule: Run `go test ./... -race -count=3` — must pass
# tool: bash
# example: GOOD
$ go test ./... -race -count=3
ok  acme/user  2.34s

## Architecture
# rule: Handlers → Services → Repositories (no cross‑layer calls)
# rule: All DB queries via repository methods — no raw SQL in services
# context: internal/service/*.go

## Security
# rule: Never log PII (email, phone, IP) — use structured logging with redaction
# rule: All endpoints require valid JWT — use `auth.RequireAuth` middleware
# example: BAD
log.Printf("User login: %s", email)  // PII in logs
# example: GOOD
log.Info("User login", "user_id", user.ID)  // no PII
```

---

## 4. How Corrections Become Persistent Rules

### The Workflow (observed across Cursor, Claude Code, Devin, Codex teams)

```
1. Agent makes mistake (e.g., uses `any` in TypeScript)
   │
   ▼
2. Human corrects in chat: "Don't use `any` — use proper types"
   │
   ▼
3. Human (or agent) creates/updates rule file:
   /repo/rules/typescript.md
   # rule: No `any` — use explicit types or generics
   # example: BAD
   const x: any = fetchData();
   # example: GOOD
   const x: User = fetchData();
   │
   ▼
4. Rule file committed to repo (versioned with code)
   │
   ▼
5. Next session: Agent loads rules/ automatically
   → Mistake doesn't recur
```

### Key Sources
| Source | URL | Verified |
|--------|-----|----------|
| BuildBetter: AGENTS.md Complete Guide 2026 | <https://blog.buildbetter.ai/agents-md-complete-guide-for-engineering-teams-in-2026/> | ✅ |
| MorphLLM: AGENTS.md Spec 2026 | <https://www.morphllm.com/agents-md-guide> | ✅ |
| BetterClaw: AGENTS.md Best Practices | <https://www.betterclaw.io/blog/agents-md-best-practices> | ✅ |
| Aridanemartin: AI Context Layers Architecture | <https://aridanemartin.dev/blog/ai-context-layers-architecture/> | ✅ |
| Devin Docs: Rules & AGENTS.md | <https://docs.devin.ai/cli/extensibility/rules> | ✅ |
| Eastondev: AGENTS.md for OpenAI Codex | <https://eastondev.com/blog/en/posts/ai/20260626-codex-agents-md-project-rules/> | ✅ |

### What Makes It Stick
| Factor | Evidence |
|--------|----------|
| **Versioned with code** | Rule changes in same PR as code changes; `git blame` shows why |
| **Imperative + examples** | Agents pattern‑match `# rule:` and `# example:` blocks |
| **Path‑specific** | `rules/frontend.md` only loads in `/frontend` — no noise |
| **Team ownership** | Each rule file has a `OWNERS` entry; changes require review |
| **Agent‑assisted authoring** | "Create a rule for this correction" → agent drafts rule file |

---

## 5. Anti‑Patterns (What Causes Drift)

| Anti‑Pattern | Symptom | Fix |
|--------------|---------|-----|
| **Mixing AGENTS.md + CLAUDE.md + .cursor/rules** | Conflicting instructions; agent follows wrong one | **Pick one**: AGENTS.md + rules/ only |
| **Prose rules without examples** | Agent ignores or misinterprets | Add `# example: GOOD/BAD` blocks |
| **Global rules in project AGENTS.md** | Pollutes other projects | Move to `~/.config/opencode/AGENTS.md` |
| **No path scoping** | Backend rules apply to frontend (wrong) | Use `# context: internal/service/*.go` |
| **Rules not versioned** | Lost on clone; new team members miss them | Commit `rules/` to repo |
| **Too many rules (>200 lines)** | Agent truncates; misses critical ones | Split into `rules/*.md`; keep AGENTS.md < 150 lines |

---

## 6. Tool‑Specific Loading Behaviors (2026)

| Tool | Global Location | Project Load | Rules Dir | Nested AGENTS.md | Notes |
|------|-----------------|--------------|-----------|------------------|-------|
| **OpenCode** | `~/.config/opencode/AGENTS.md` | Repo root | `rules/` | Yes | Full spec support |
| **Claude Code** | `~/.claude/AGENTS.md` | Repo root | `.claude/rules/` | Yes | Reads AGENTS.md first |
| **Cursor** | `~/.cursor/AGENTS.md` | Repo root | `.cursor/rules/` | Yes | Converts to internal format |
| **OpenAI Codex** | `~/.codex/AGENTS.md` | Repo root | `rules/` | Yes | Via `codex` CLI |
| **Devin** | `~/.devin/AGENTS.md` | Repo root | `rules/` | Yes | Rules injected every session |
| **Amp** | `~/.amp/AGENTS.md` | Repo root | `rules/` | Yes | New entrant |

> **Consensus**: All major tools now support the same hierarchy. Differences are only in global config directory.

---

## 7. Omega Engine — Recommended Structure

```
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/
├── AGENTS.md                    # Project overview, build/test, core mandates
├── rules/
│   ├── mandates.md              # M1‑M27 (imperative, with examples)
│   ├── python.md                # AnyIO, type hints, error handling
│   ├── podman.md                # Quadlet patterns, keep-id, no :U
│   ├── heritage.md              # [id-soft:] tagging rules, vet log
│   ├── testing.md               # Temple‑Grade gates, contract tests
│   ├── git.md                   # Conventional commits, entity attribution
│   ├── research.md              # Sovereign Search Protocol, citation format
│   └── agents.md                # Subagent dispatch, handoff protocol
├── .opencode/
│   └── AGENTS.md                # OpenCode‑specific overrides (if any)
└── docs/
    └── AGENTS.md                # Documentation‑specific rules
```

### Sample `rules/mandates.md`
```markdown
# Sovereign Mandates — Imperative Rules

# rule: M1 — All async code MUST use AnyIO. Never import asyncio directly.
# example: GOOD
import anyio
async def fetch(url): return await anyio.to_thread.run_sync(requests.get, url)
# example: BAD
import asyncio
async def fetch(url): return await asyncio.to_thread(requests.get, url)

# rule: M2 — Engine/Stack firewall. No stack logic in src/omega/.
# context: src/omega/**

# rule: M7 — Local‑first provider order. Never add cloud provider before local.
# rule: M14 — Every [id-soft:] tag MUST have vet record in HERITAGE_VET_LOG.md
# rule: M23 — If mandatory tool fails, STOP. Report [TOOL-CHAIN-COLLAPSE].
```

---

## 8. Sources & Verification

| # | Source | Access | Verified |
|---|--------|--------|----------|
| 1 | agents.md official site | ✅ Public | ✅ |
| 2 | DeepWiki AGENTS.md Format | ✅ Public | ✅ |
| 3 | BuildBetter 2026 Guide | ✅ Public | ✅ |
| 4 | MorphLLM AGENTS.md Guide | ✅ Public | ✅ |
| 5 | BetterClaw Best Practices | ✅ Public | ✅ |
| 6 | Aridanemartin Context Layers | ✅ Public | ✅ |
| 7 | Devin Docs Rules | ✅ Public | ✅ |
| 8 | Eastondev Codex AGENTS.md | ✅ Public | ✅ |

> **Directional only**: Exact loading order behavior varies slightly by tool; test with your stack. "Imperative + examples" format is community consensus, not formal spec. Correction‑to‑rule workflow observed in multiple teams; not a standardized process.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_agents_md ⬡ DELIVERABLE-7*