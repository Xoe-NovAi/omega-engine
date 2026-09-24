# MCP Parity Checklist — Same Memory on Any Platform or Node

**Principle:** memory follows via MCP; harness follows via setup. Any platform (OpenCode, Cline, Antigravity, Grok CLI…) or node that runs these servers with these tools gives the entity the same durable self.

## Required Servers (Node 1 reference)

| Server | Role | Verify |
|--------|------|--------|
| `mempalace` | Drawers, diary, KG, semantic search, mesh, event bus, tunnels, artifacts | Full tool surface callable (drawers/diary/KG/search/mesh/events) |
| `context7` | Current library/framework docs | Test query returns docs |
| `firecrawl` | Web search/scrape/parse (+ developer & research categories) | Test search + scrape |
| `parallel-search` | Web search/fetch (expects `"tools": { "parallel-search": true }` boolean form on OpenCode 1.18+) | Test search |
| `grep_app` | GitHub code search — real-world usage examples for unfamiliar APIs | Test code-pattern query returns hits |

## Install Notes (Machine Rules — Verified)

- Local MCP servers need explicit registration **after** config: `opencode mcp add <name> -- <cmd> <args>` — config-only is ignored.
- Tools as boolean on OpenCode 1.18+: `"tools": { "parallel-search": true }`, not `{enabled,…}`.
- Parallel.ai health check must accept 405: `grep -E '200|401|405'`; endpoint is `search.parallel.ai/mcp`.
- MemPalace backend file is `sqlite_exact.sqlite3` (not `mempalace.yaml`).
- Sidecar daemons needing file-watch require `inotify-tools`.
- Keep `.venv` paths per-host (Node 1: `/home/xnai/WanderGround/.venv/bin/python3`).

## Verification (Run on the New Host/Node)

1. List MCP resources; confirm palace wings visible.
2. `diary_read` (own agent) returns entries or clean empty.
3. `search` in own wing returns scoped results.
4. `kg_query` on a known subject returns typed facts.
5. `mesh_peers` shows self; after join, shows both replicas.
6. Write + read back one test drawer; delete it; confirm convergence on peer.

## What MCP Does NOT Carry (Per-Host Setup)

- Agent prompt scaffold (copy + adapt `resources_LILITH_AGENT_PROMPT.md` **or** `resources_RESEARCHER_HUMBOLDT_AGENT_PROMPT.md` — two working templates now exist).
- WAD files / soul contracts (git/USB).
- Voice/consent middleware (rebuild or consciously waive per host — never waive silently).
- Permission model and secret handling (per-host policy; never commit secrets).
