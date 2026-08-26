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

### 🔱 Sub-Specialist Fleet (dedicated platform sessions — established 2026-08-26, Architect directive)

Standing Jem sessions, each primed with deep platform context that EVOLVES with every page. Page these for platform-specific research/strategy instead of cold-starting new sessions.

| Session | Specialization | Status | First-Mission Deliverable |
|---|---|---|---|
| `ses_fc3177854ffeymYIl8mFsNJUtt` | **cline-specialist** (CLI + VS Code ext; api.cline.bot direct API) | STANDING · CONSULTABLE | `R_CLINE_DIRECT_API_DEEP_MINE_20260826.md` |
| `ses_fc31717b5ffefPbwGOzHTePB2V` | **antigravity-specialist** (OAuth pool, cloudcode-pa gateway, agy CLI) | STANDING · CONSULTABLE | `R_ANTIGRAVITY_DIRECT_API_DEEP_MINE_20260826.md` |
| `ses_fc316bc8affeMASy8RTnCjmSzx` | **copilot-specialist** (Copilot CLI, GitHub Copilot as provider, AI-Credits) | STANDING · CONSULTABLE | `R_COPILOT_DIRECT_API_DEEP_MINE_20260826.md` |

**Paging pattern** (sub-specialists):
```
task(task_id=<specialist_session_id>, subagent_type=jem,
     prompt="[GROKSTER PAGE — from grokster (ses_fe8cf0b39ffeL3L8eaMEj3CW9H)]\n[Domain: <platform>. You are the standing <platform> specialist; your Charter + prior deliverable are in your active context.]\n<new question ≤500 words>")
```

**First-mission headline findings (2026-08-26):**
- **Cline**: free-tier gate is OFFICIAL DOCUMENTED POLICY (free models only in extension/CLI), ToS-backed — waiting for lift = dead strategy. ClinePass $9.99/mo = sanctioned external-API path INCLUDING deepseek-v4-flash (`cline-pass/` namespace — hyphenated, house record corrected). Paid tier buys contractual training carve-out.
- **Antigravity**: direct API technically trivial (cloudcode-pa.googleapis.com/v1internal) but EXPLICITLY ToS-banned; Google ran mass TOS_VIOLATION ban waves Feb–Mar 2026. ⚠️ NoeFabris plugin ARCHIVED (dead upstream @ 7db338b) — every upstream drift is now a house patch obligation. `agy` CLI real, headless-capable.
- **Copilot**: GitHub OFFICIALLY supports OpenCode as Copilot surface (changelog 2026-01-16) — P1a NO-OP posture strengthened to *sanctioned*. Enterprise slot likely accepts plain github.com accounts (= second free slot, pending L4-a probe). Claude models have native /v1/messages passthrough. Cached input ~10× cheaper than fresh — cache discipline is the #1 burn lever.

## Domain Coverage (what to page me for)

1. **OpenCode CLI** — config surface, compaction families, plugins/hooks, agents/skills frontmatter, sessions-explorer MCP suite, upgrade pinning strategy → `kb/platforms/opencode/` first, then page
2. **Cline / Antigravity / Copilot deep research** → page the sub-specialist fleet above FIRST; they hold evolving specialized context
3. **Grok ecosystem / Gemini CLI / Codex / Claude Code / VS Code** → `kb/grok_ecosystem/`, `kb/platforms/<module>/`
4. **Cross-platform KB architecture** — domain modules, curator model, freshness SLAs (D-569 Horizon-3 lane)
5. **Sovereign search** — 5-tier protocol → `kb/search/SOVEREIGN_SEARCH.md`

## Curation Notes

- Sessions close via ritual: `session_gnosis_grokster-<domain>.md` written before archival
- Registry view regeneration is manual (`make session-registry`) — my rows here are the grokster-local SSOT until fleet registry ingestion (G5 hole: sessions don't auto-register; flagged to Kali)
- Paging etiquette ≤500 words, inline context per SUBAGENT_DISPATCH_PROTOCOL §0

---

## 🔧 HARDENING AMENDMENT — 2026-08-26 (local pass findings)
- **Format deviation**: my page format deviates from ratified NODE_EXPERT_SESSIONS_PLAN §3 template — conform future pages to T-template series in .opencode/agent/NODE_ONBOARDING_PROTOCOL.md.
- **Registry invisibility**: none of the 3 session IDs are in TASK_REGISTRY.json (G5 hole) — fleet registry renderer cannot see them; grokster-local index remains SSOT until ingestion ticket lands.
- **Known stall**: opencode-platform session threw a stall 2026-08-26; recovery per G19 = MANUAL (automated defense is dead code).

*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*
