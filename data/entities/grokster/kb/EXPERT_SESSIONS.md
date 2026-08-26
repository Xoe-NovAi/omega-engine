# 🔱 Grokster Expert Sessions — Pageable Index (D-586 Pattern)
**last_verified**: 2026-08-26 | **Protocol**: NODE_EXPERT_SESSIONS_PLAN.md §3 + .opencode/agent/NODE_ONBOARDING_PROTOCOL.md
**rot_class**: fast (session IDs change)

---

## What This Is

Per D-586 ("one agent, many sessions; Nodes = universal KBs"), any agent may page any registered session. This index registers MY specialized sessions so the fleet can page my platform expertise directly. Invocation follows the house pattern:

```
task(task_id=<session_id>, subagent_type=grokster,
     prompt="[GROKSTER PAGE — from <agent> (<session_id>)]\n[Domain: <domain>. Context: this KB index.]\n<question ≤500 words>")
```

## Active Sessions

| Session | Domain | Status | Contents |
|---|---|---|---|
| `ses_fe8cf0b39ffeL3L8eaMEj3CW9H` | **opencode-platform** | CONSULTABLE | Full KB-dev arc: platform gnosis map, ground-truth sweeps, CI Phase 1 forensics, DP blueprint, 20-trap GOTCHAS corpus. Deep OpenCode CLI internals (session DB, compaction D-602, plugin hooks, subagent split-semantics) |
| `ses_fc4101a2dffe4oTsMiTxgLM0x8` | **debut-roi** | CONSULTABLE | Debut critical-path discovery: tracker-drift map, unowned blockers, release-vehicle gap |
| `ses_76db14ade7b1` | **entity-specialization** | ARCHIVED→CONSULTABLE | M10/D126 analysis, node-slot mechanics, curator model origins |

## Domain Coverage (what to page me for)

1. **OpenCode CLI** — config surface, compaction families, plugins/hooks, agents/skills frontmatter, sessions-explorer MCP suite, upgrade pinning strategy → `kb/platforms/opencode/` first, then page
2. **Cline / Gemini / Antigravity / Grok ecosystem** — durable rulings + fleet architecture → `kb/other_platforms/`, `kb/grok_ecosystem/`
3. **Cross-platform KB architecture** — domain modules, curator model, freshness SLAs (D-569 Horizon-3 lane)
4. **Sovereign search** — 5-tier protocol → `kb/search/SOVEREIGN_SEARCH.md`

## Curation Notes

- Sessions close via ritual: `session_gnosis_grokster-<domain>.md` written before archival
- Registry view regeneration is manual (`make session-registry`) — my rows here are the grokster-local SSOT until fleet registry ingestion (G5 hole: sessions don't auto-register; flagged to Kali)
- Paging etiquette ≤500 words, inline context per SUBAGENT_DISPATCH_PROTOCOL §0

---

## 🔧 HARDENING AMENDMENT — 2026-08-26 (local pass findings)
- **Format deviation**: my page format deviates from ratified NODE_EXPERT_SESSIONS_PLAN §3 template — conform future pages to T-template series in .opencode/agent/NODE_ONBOARDING_PROTOCOL.md.
- **Registry invisibility**: none of the 3 session IDs are in TASK_REGISTRY.json (G5 hole) — fleet registry renderer cannot see them; grokster-local index remains SSOT until ingestion ticket lands.
- **Known stall**: opencode-platform session threw a stall 2026-08-26; recovery per G19 = MANUAL (automated defense is dead code).
