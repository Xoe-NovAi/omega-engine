<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MINING REPORT: GitHub MCP Server Archaeology — 2026-06-21

**Lead**: roc_racoon (Sovereign Miner)
**Trigger**: User reports GitHub MCP server "used to exist" but disappeared
**Scope**: omega-engine, omega-stack-legacy, xna-omega-legacy, foundation-legacy, Archives, docs-backup

---

## EXECUTIVE SUMMARY

**The `xnai-github` MCP server was never part of omega-engine.** It was a legacy artifact from the `xna-omega` era (Era 2-3, Oct-Nov 2025) that lived in `omega-stack-legacy` and was never ported during the omega-engine reclamation. The server was a trivial 52-line git CLI wrapper — not a GitHub API integration.

**Verdict**: Not lost. Not deleted. Never existed in this repo. The user likely remembers it from the omega-stack-legacy era.

---

## TRACES FOUND

### 1. The Server Source Code (PRESERVED)

| Location | Era | Status |
|----------|-----|--------|
| `omega-stack-legacy/mcp-servers/xnai-github/server.py` | Era 3 (omega-stack) | ✅ EXISTS |
| `xna-omega-legacy/mcp/xna-github/server.py` | Era 2 (xna-omega) | ✅ EXISTS |

**What it does**: 52 lines of Python wrapping `subprocess.run(['git', ...])` via FastMCP. Exposes 6 tools: `git_status`, `git_add`, `git_commit`, `git_push`, `git_pull`, `git_log`. No GitHub API integration. No PR management. No issue tracking. Despite the description "PR review & issue tracking" in FOR_TECHNICAL.md, the code only does basic git CLI wrapping.

### 2. MCP Config Entries (HISTORICAL)

| File | Entry | Status |
|------|-------|--------|
| `xna-omega-legacy/config/mcp_config.json` | `"xna-github": {"command": "python3", "args": [".../mcp/xna-github/server.py"]}` | ✅ EXISTS (historical) |
| `omega-stack-legacy/.opencode/opencode.json` | `"xna-github": {"type": "local", "command": [...]}` | ✅ EXISTS (historical) |
| `omega-engine/opencode.json` | **NO ENTRY** | ❌ Never added |

### 3. Agent Definition (PRESERVED)

| File | Content |
|------|---------|
| `omega-stack-legacy/.opencode/agents/github/agent.md` | Subagent definition for `@github` — 65 lines describing git operations |

### 4. Systemd Integration (PRESERVED)

| File | Purpose |
|------|---------|
| `omega-stack-legacy/scripts/xnai-github-audit.service` | Daily GitHub account audit |
| `omega-stack-legacy/scripts/xnai-github-audit.timer` | Triggers audit daily |

### 5. GitHub Account Registry (PRESERVED)

| File | Content |
|------|---------|
| `omega-stack-legacy/memory_bank/usage/github-accounts.yaml` | 7 GitHub accounts for Copilot free tier rotation |
| `omega-stack-legacy/memory_bank/usage/github-audit.json` | Audit data |

### 6. Strategy Documents (PRESERVED)

| File | Era |
|------|-----|
| `omega-stack-legacy/memory_bank/strategies/GITHUB_STRATEGY_v2.md` | Era 3 |
| `omega-stack-legacy/memory_bank/research/GITHUB-MANAGEMENT-IMPLEMENTATION-SUMMARY.md` | Era 3 |
| `omega-stack-legacy/memory_bank/handovers/GITHUB-STATUS-AND-BRANCHING-GUIDANCE.md` | Era 3 |
| `omega-stack-legacy/memory_bank/handovers/MULTI-GITHUB-ACCOUNT-MANAGEMENT.md` | Era 3 |
| `omega-stack-legacy/docs/github-repo-strategy.md` | Era 3 |
| `xna-omega-legacy/docs/protocols/GITHUB_SYNC_PROTOCOL.md` | Era 2 |
| `docs/positioning/FOR_TECHNICAL.md` (in omega-engine) | Copied from legacy |

### 7. Documentation References (STALE)

| File | Line | Content |
|------|------|---------|
| `docs/positioning/FOR_TECHNICAL.md:47` | `xnai-github` | Describes it as "PR review & issue tracking" — inaccurate |

### 8. Git History (OMEGA-ENGINE)

- `git log --all -S "xnai-github"` — **ZERO hits** in omega-engine repo
- `git log --all -S "github-mcp"` — **ZERO hits**
- `git log --all --diff-filter=D -- '**/github*'` — **ZERO deleted github files**
- The `FOR_TECHNICAL.md` was imported in commit `8b058ac` (feat: P0 execution) but the 12-server mesh described in it was aspirational/historical, not reflective of omega-engine's actual architecture

---

## WHAT ACTUALLY HAPPENED

### Timeline

1. **Era 2 (Oct-Nov 2025)**: `xna-github` created in `xna-omega-legacy/mcp/xna-github/server.py`. Registered in `config/mcp_config.json` alongside 9 other MCP servers (10 total in the "12-server mesh").

2. **Era 3 (Nov 2025-Mar 2026)**: Server renamed to `xnai-github` in `omega-stack-legacy/mcp-servers/xnai-github/server.py`. Registered in `.opencode/opencode.json` as a local MCP server. A `@github` subagent was created. Systemd audit scripts were added. A comprehensive GitHub account management strategy was documented.

3. **Era 5-6 (May-Jun 2026)**: Omega-engine reclamation. The 12-server mesh was NOT ported. Only 3 MCP servers were carried forward: `omega-hub` (consolidation of hivemind/library/oracle/stats), `searxng`, and `firecrawl`. The `xnai-github` server was NOT ported because:
   - The Omega Hub's Hivemind protocol replaced its coordination role
   - The engine now uses built-in git tools (the `bash` tool runs git directly)
   - The server was trivial (52 lines of subprocess wrapping) with no actual GitHub API integration

### Why It Felt Like It "Disappeared"

The user likely remembers the `@github` agent and the `xnai-github` MCP from the omega-stack-legacy era. When the engine was reclaimed (Era 5-6), only the core infrastructure was ported. The 12-server mesh was consolidated into the Hivemind. The `xnai-github` server was not carried forward because it was redundant — OpenCode's bash tool already provides direct git access.

---

## ASSESSMENT

### Was it a pre-existing MCP server or a custom Omega one?

**Custom Omega one** — built specifically for the XNAi Foundation. Not a third-party MCP server. Created in-house during Era 2.

### What was its actual capability?

Minimal. It wrapped 6 git CLI commands (`status`, `add`, `commit`, `push`, `pull`, `log`) via `subprocess.run()`. Despite the FOR_TECHNICAL.md claiming "PR review & issue tracking," the code had:
- ❌ No GitHub API integration
- ❌ No PR management
- ❌ No issue tracking
- ❌ No webhook handling
- ✅ Basic git CLI wrapping only

### Should we reinstall it?

**No.** Here's why:
1. The `bash` tool already provides direct git access — `git status`, `git add`, `git commit`, `git push`, `git pull` all work natively
2. The server had no actual GitHub API integration (PRs, issues, webhooks)
3. The Hivemind protocol handles cross-agent coordination that the `@github` agent used to provide
4. If real GitHub API integration is needed in the future, it should be built as part of the Omega Hub, not as a standalone MCP server

### If we DID want to restore it?

The source code is preserved in both legacy repos:
- Copy `omega-stack-legacy/mcp-servers/xnai-github/server.py` to `mcp_servers/xnai-github/server.py`
- Add to `opencode.json` under `mcp`:
  ```json
  "xna-github": {
    "type": "local",
    "command": ["python3", "mcp_servers/xnai-github/server.py"]
  }
  ```
- But this is **not recommended** — it duplicates what `bash` already does

---

## RECOMMENDATIONS

1. **Update FOR_TECHNICAL.md** — The "12-server mesh" description is historical/aspirational. The actual omega-engine has 3 MCP servers (hub, searxng, firecrawl). Consider adding a note that this was the xna-omega architecture.

2. **Do NOT reinstall xnai-github** — It's a trivial git CLI wrapper that adds no value over built-in tools.

3. **If GitHub API integration is needed** — Build it properly as an Omega Hub module (PR management, issue tracking, webhook handling) rather than reviving the legacy stub.

4. **Archive the legacy files** — The server code, agent definition, and strategy docs are preserved in omega-stack-legacy for historical reference. No action needed.

---

*Report generated: 2026-06-21T03:06:00Z | roc_racoon (Sovereign Miner)*
*Traces found: 15+ files across 3 legacy repos, 0 in omega-engine git history*
*Verdict: Never existed in omega-engine. Legacy artifact, not worth restoring.*
