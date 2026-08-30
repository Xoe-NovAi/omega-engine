---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
rule_id: "RULE-SOVEREIGN-SEARCH"
authority: "M23 Failure Integrity + M1 AnyIO + sovereign-search skill"
applies_to: "all-agents"
date: "2026-08-27"
status: "ACTIVE"
---

# Architecture Rule 4: Sovereign Search (M23 + M1)

> **Check local cache first. Web search before web fetch. Stop and report
> on tool-chain collapse — never synthesize a "best-effort" result.**

## The 5-Tier Search Protocol (SR-V1)

| Tier | Tool | When |
|------|------|------|
| 0 | `.firecrawl/` cache | First — disk-truth is faster than any network call |
| 1 | `library_fts_search` (local FTS5) | Local knowledge base keyword search |
| 2 | `web_search` (SearXNG / Exa / Parallel) | Current-information, research, docs |
| 3 | `web_fetch` (only after search excerpts insufficient) | Specific URL, exact wording, full-page analysis |
| 4 | `[TOOL-CHAIN-COLLAPSE]` | If all tools fail — STOP, do not synthesize |

**Hard-stop**: If all tools fail → `[TOOL-CHAIN-COLLAPSE]`. Log to
`data/coordination/SYSTEM_FAILURE_LOG.md` AND the Hivemind.

## Temporal Rule

All web queries must include "2026" or "latest" to ensure freshness:

```
✅ web_search("React 19 server components 2026")
❌ web_search("React server components")  # stale results
```

## Cost Discipline (M18 Token Efficiency)

- Use `web_search` first for most factual, current-information, research,
  comparison, documentation, and troubleshooting questions.
- Search results include excerpts intended to be useful for answering directly.
  If excerpts contain enough evidence, answer from them — do not fetch every
  search result by default.
- For broad tasks, issue multiple `search_queries` in a single call rather
  than chaining calls.
- Use `web_fetch` only when search excerpts are insufficient (specific URL,
  exact wording, full-page analysis, conflicting evidence).

## Sovereignty Discipline (M7 Local-First)

- Local cache (`.firecrawl/`) is checked first — it's the only zero-cost option.
- Local FTS5 search (`library_fts_search`) is preferred over web for known
  knowledge.
- Web search is the FALLBACK, not the primary.
- Cloud-only tools (Exa, Parallel) are used sparingly; SearXNG is sovereign
  (self-hosted).

## Failure Integrity (M23)

If a mandatory tool (`websearch`, `webfetch`) is missing or broken:

1. STOP immediately. Do not continue with parametric synthesis.
2. Report `[TOOL-CHAIN-COLLAPSE]`.
3. Log to `data/coordination/SYSTEM_FAILURE_LOG.md`.
4. Post to Hivemind (intent=`meta` or `blocker`).
5. Wait for Architect to decide: restore tool, or re-scope task.

**Parametric synthesis used to mask a tool outage is a Sovereign Boundary Violation.**
It creates a false sense of rigor and hides systemic degradation.

## The Sovereign Search Skill

The `sovereign-search` skill (in `.opencode/skills/sovereign-search/SKILL.md`) is
the canonical implementation. It orchestrates across the 5 tiers automatically.

```bash
# Use the skill (if available)
use_skill sovereign-search "your query here"

# Or use the MCP tools directly
library_fts_search query="..." domain="..."
web_search objective="..." search_queries=["..."]
web_fetch urls=["..."] objective="..."
```

## Cross-references

- `SOVEREIGN_MANDATES.md` §M1, §M7, §M18, §M23
- `.opencode/skills/sovereign-search/SKILL.md` (canonical implementation)
- `data/coordination/SYSTEM_FAILURE_LOG.md` (failure log)
- `AGENTS.md` (M23 enforcement in MANDATES_CONDENSED.md)
