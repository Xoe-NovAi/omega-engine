<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# Web Research — Knowledge Gaps & Pain Points (2026-10-13)

**Researcher**: Cline (takeover for OpenCode agents — Zen/OpenRouter quota exhausted)
**Method**: direct fetch of 12 primary sources (spec pages, official docs, arXiv).
Note: the sovereign chain partially collapsed today — `library_discovery`
(all 10 queries empty/circuit-open), SearXNG (connection failed), Firecrawl
(no module), Exa (401 invalid key). Only `fetch_web_content` succeeded.
Exa key needs rotation; SearXNG daemon needs a health check.
**Supersedes nothing**; complements `KNOWLEDGE_GAPS_20261003.md` (P0 constraint
layer still open) and `HIVE_HARVESTER_RESEARCH_20261003.md`.

---

## 1. MCP 2026-07-28 — sessions, initialize, resumability ALL REMOVED

**Sources**: WorkOS "MCP went stateless" (Sep 2026, post-migration-notes-settled),
StartDebugging SSE→Streamable HTTP checklist (Jul 2026).

The revision is subtractions, not additions. Every request now carries protocol
version, client identity, capabilities in `_meta` — any request can land on any
replica behind plain round-robin, no shared session store, no sticky routing.

**What broke** (vs SSE / 2024-11-05 and vs 2025-11-25):
- Protocol-level sessions: gone. No `Mcp-Session-Id` economy at all.
- `initialize`/`initialized` handshake: gone → replaced by **`server/discover`
  RPC** (servers MUST implement; clients MAY call first, not required).
- Stream resumability: gone — `Last-Event-ID` and SSE event IDs removed from
  Streamable HTTP. A broken response stream now **loses the in-flight request
  outright**; nothing will tell you (no signal — silent loss).
- `ping`, `logging/setLevel`: gone. Roots, Sampling, Logging, HTTP+SSE
  transport, `includeContext` "thisServer"/"allServers", OAuth DCR: deprecated
  (12-month minimum window under the new deprecation policy).
- Elicitation (`elicitation/create`), `sampling/createMessage`, `roots/list`
  → replaced by **multi round-trip requests**: server returns
  `resultType: "input_required"` + `inputRequests`; client retries with
  `inputResponses`. The 2025-11-25 elicitation completion signal is gone.
- DCR deprecated in favor of **Client ID Metadata Documents (CIMD)**.
- Caching is now first-class: `tools/list`, `prompts/list`, `resources/list`,
  `resources/read`, `resources/templates/list` return **required `ttlMs` +
  `cacheScope`**.

**Notable correction to our internal lore**: the SSE-era checklist (written for
2025-11-25) says "dropped connections stop losing messages" via `Last-Event-ID`
replay — **2026-07-28 deletes exactly that mechanism**. Anyone citing
resumability as a property of our transport is describing the version we are
leaving, not the one we are on.

**Omega relevance**: our SDK (1.30.0) negotiates `2025-11-25`, not 2026-07-28
— Tier-1 SDKs have since caught up, so an SDK bump is the prerequisite to any
`server/discover` / `_meta`-carried identity work. The federation probe's
HTTP-400-on-`/mcp`-POST today is consistent with a server that has not made
this jump. Do NOT claim 2026-07-28 compliance before the SDK bump + probe
re-verification.
