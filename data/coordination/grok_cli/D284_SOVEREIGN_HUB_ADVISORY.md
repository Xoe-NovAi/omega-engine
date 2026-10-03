<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# D-284 Sovereign Hub — Streamable HTTP + SHIELDMCP (Advisory Spec)
**Packet**: `ho_28b149118c70`  
**Author**: `grok-cli/grok` · 2026-07-17  
**Role**: Advisory only — Horizon 3 — **do not implement**

---

## Live footprint note

Handoff cites `src/omega/mcp_hub/{server,gateway,tools,middleware}.py`.  
**Observed**: no `src/omega/mcp_hub/` package; closest surface includes `src/omega/iris/server.py` (and deploy/MCP config elsewhere).  

**Action for implementers**: re-map file list to actual Hub entrypoints before coding. Treat handoff paths as **logical** components, not guaranteed paths.

---

## Target architecture (agree with Kali table)

| Layer | Current (reported) | Target | Grok note |
|-------|-------------------|--------|-----------|
| Transport | SSE `/sse` | Streamable HTTP `/mcp` | Align MCP 2025+ streamable HTTP; dual-run SSE deprecation window |
| Auth | None / weak | OAuth 2.1 **PKCE** + JWT | **Self-hosted** (Hydra/Ory or Keycloak) for M7 sovereignty |
| Proxy | Direct tools | SHIELDMCP Intent Digest | Mutating tools only (IA2) |
| Discovery | Ad hoc | `/.well-known/agent-card.json` | **Per hub** first; per-entity later if multi-tenant |

---

## Decision recommendations (Kali’s 4 questions)

| # | Question | Recommendation | Rationale |
|---|----------|----------------|-----------|
| 1 | OAuth provider | **Self-hosted** (Ory Hydra or Keycloak on podman) | Sovereignty; no external IdP |
| 2 | Token storage | **SQLite** on single-node 5700U; Redis only if multi-node later | Match M23 local-first |
| 3 | SHIELDMCP scope | **Mutating tools only** + optional allowlist for high-risk reads | Latency; IA2 draft-then-commit |
| 4 | Agent card location | **Hub-level** `/.well-known/agent-card.json` first | Simpler ops; entity cards phase 2 |

### SHIELDMCP pattern (confirm)

```
Client → SHIELDMCP → MCP tools
         Intent Digest {tool, args_hash, risk_level, requires_confirmation}
         Mutating: draft → human/architect confirm → commit
```

Stage drafts in `data/shieldmcp/staging/` (file-backed) for crash safety — not only memory.

---

## Firecrawl 405

Treat SSE 405 as **transport mismatch** evidence, not Firecrawl-only bug. Migration order:

1. Streamable HTTP endpoint + health probe  
2. Client dual-stack  
3. Deprecate SSE  
4. Re-test Firecrawl MCP path  

---

## Security / Temple-Grade

- T11: JWT audience + short TTL + refresh rotation  
- No long-lived API keys in agent cards  
- Audit log for SHIELDMCP commits (forensic, P8)  
- Fail closed if auth middleware missing in prod profile  

---

## Verdict

Spec is **directionally correct**. File map needs update. Implementation should wait for D-281/D-282 runway. Grok remains advisory.

*Deliverable for `ho_28b149118c70`.*
