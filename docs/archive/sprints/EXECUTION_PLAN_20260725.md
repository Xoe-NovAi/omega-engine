> **SUPERSEDED**: This document is preserved for historical context. For current sprint control, see `data/coordination/ACTIVE_SPRINT.json` and `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md`.

# 🔱 Omega Engine — Fleet Execution Plan
**AP Token**: `AP-FLEET-EXECUTION-PLAN-v1.2.0`  
⬡ OMEGA ⬡ KALI ⬡ FLEET ⬡ PHASE-D-GATE ⬡ 2026-07-25

> ## ⚠️ SUPERSEDED FOR SPRINT CONTROL (2026-07-30)
> **Status**: 📦 **SUPERSEDED** — historical trail only. Do **not** treat this file as the active sprint.
> **Successor (near-term sprint)**: `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` + `data/coordination/ACTIVE_SPRINT.json` (`UNOVERENGINEER-01`)
> **Ops truth**: `docs/briefings/CLINE_CLI_HANDOFF_TO_GROK_20260730.md` · **Gate verdict**: `data/coordination/PHASE_D_GATE_VERDICT_20260730.md`
> **Session**: `data/coordination/SESSION_ANCHOR.md`
> Body below preserved for archaeology; metrics may be stale vs live probes.

**Status**: 📦 **SUPERSEDED** (was 🟡 HARDENED v1.2 on 2026-07-25)  
**Owner**: @kali (Sprint Lead) · Final review: @cline 2026-07-25  
**Gate**: Phase D entry — Integrity Gate (B1-B5) → Process Reform (P-1..P-7) → Phase D  
**Agent card (read first)**: `docs/sprints/current/AGENT_SPRINT_CARD.md`  
**Process reform plan**: `docs/strategy/PROCESS_IMPROVEMENT_PLAN_20260725.md`  
**Gap research**: `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md`  
**LAST_VERIFIED**: 2026-07-25T23:00Z (stale — see SESSION_ANCHOR 2026-07-30)

---

## §0 Reality Snapshot (Ground Truth — Not Narrative)

### 0.1 What agents must believe right now

| Area | Research | Execution | Probe / evidence |
|------|----------|-----------|------------------|
| C-0..C-2′, C-5, C-6′, C-10, C-10.5, C-11 | CLOSED | Mostly CLOSED | ⚠️ C-6' has 5+ live clones (probe: grep "class.*Breaker" | wc -l = 6) |
| V-1 VaultCore MVP | CLOSED | **EXEC-PARTIAL** | Tree present; **large uncommitted unification**; age binary MISSING |
| MCP pin `>=1.27,<2` | CLOSED | **EXEC-PARTIAL** | pyproject pinned; venv 1.28.1; requirements 1.27.1 |
| MCP Sprint 1 middleware | CLOSED | Hub: COMPLETE | Hub 8016 🅳 Firecrawl 8015 🅳 |
| AGY OAuth persistence | CLOSED design | Hub: COMPLETE | Re-auth on restart still P0 risk |
| C-0.5 SoulDistiller code | CLOSED | ✅ **COMPLETE** | Plugin API: `.opencode/plugins/soul_distiller.js` + `session_end.py`; gate 10/11 |
| W-1 WARP pool | CLOSED research | **EXEC-FAIL** | No listeners on 8081-8083 (probe: ss -lntp = ∅) |
| C-3 restic scripts | CLOSED | **EXEC-PARTIAL** | Scripts exist; systemd timer not enabled |
| Phase D gate script | — | FIXED fail-closed v1.1 | Was inverted |
| KG-1..6 contribution research | CLOSED | N/A | Do not re-survey |
| Process Reform (P-1..P-7) | NEW | Not started | See PROCESS_IMPROVEMENT_PLAN_20260725.md |
| DB consolidation (P-2) | NEW | Not started | 9 SQLite DBs; 2 duplicate omega_memory.db (118M+22M) |
| Soul Hardening RFC | OPEN design | Not started | RFC only; no gate criterion yet |

### 0.2 Remaining true P0 blockers (integrity)

| # | Blocker | Owner | Effort | Done signal |
|---|---------|-------|--------|-------------|
| **B1** | C-0.5 hook **registered via Plugin API** | @kali | 2 min + restart | `.opencode/plugins/soul_distiller.js` exists + `session.compacted` fires |
| **B2** | Dirty VaultCore / secret-scanner tree | @maat/P3 | 1–2 h | Commit slice **or** explicit freeze + lock |
| **B3** | W-1 not live (SOCKS down) | Carmack/P1 + Architect | 15–45 min | `ss` shows 8081–8083 + 3 exit IPs |
| **B4** | Honest Phase D gate run | @verity / @kali | 10–30 min | `verify_phase_d_gate.py` exit 0 or FAIL list |
| **B5** | AGY re-auth on restart (if still broken) | @maat/P4 | 1 h | Cold restart keeps tokens |

**Phase II (Process Reform) tickets begin after B1-B5 are resolved:**
| # | Ticket | Owner | Effort | Done signal |
|---|--------|-------|--------|-------------|
| **P-1** | Probe-backed OMEGA_ENGINE claims | @verity | 4 h | Every \u00a72 row has LAST_PROBE + command |
| **P-2** | DB consolidation to 3 databases | @maat/P3 | 4 h | `find data -name '*.db'` returns \u22643 |
| **P-3** | Vector consolidation (7\u21923 collections) | @maat/P3 | 2 h | 3 vec0 tables, not 7 |
| **P-4** | Unified soul distiller (kill dual) | @kali / @scribe | 2 h | 1 distiller interface, not 2 |
| **P-5** | Kill C-6' breaker clones | @maat/P3 | 3 h | `grep -r class.*Breaker src/omega/` = 1 |
| **P-6** | Split god modules >1000 lines | @maat/P3 | 6 h | oracle.py < 1000, model_gateway.py < 1000 |
| **P-7** | MCP version single source | @maat/P3 | 30 min | pyproject.toml only; requirements.txt generated |

PolicyKit / temple-grade doc style remain **important** but secondary to B1–B4 for agent thrash reduction.

### 0.3 Explicit freezes (team-wide this window)

| Freeze | Until |
|--------|--------|
| Parallel writes to `src/omega/vault/` | Vault lander commits or releases lock |
| New free-tier providers | D-351 fabric systematized (Ark) |
| Phase D feature build (Living Research OS) | Fail-closed gate + B1 + B2 |
| SoulHealthScorer / CI soul gates implementation | Soul Hardening RFC consensus |
| Claiming “Grok CLI 8-account fabric capacity” | V-1 landed + single ACP smoke (GAP-S-01) |

---

## §0.5 Agent Support Packet (NEW in v1.1)

### Truth hierarchy

1. Machine probes (AGENT_SPRINT_CARD §3)  
2. This plan’s `LAST_VERIFIED` + §0  
3. `git status` / HEAD  
4. HMC Sprint Status  
5. SESSION_ANCHOR / anchored-summary  
6. Historical “all gaps closed” research prose  

### Labels every status cell must use

| Label | Meaning |
|-------|---------|
| RESEARCH-CLOSED | Do not re-websearch |
| EXEC-PARTIAL | Exists; probe not green |
| EXEC-CLOSED | Probe green + committed (or Architect-locked dirty) |
| RFC-OPEN | Debate only |

### Coordination minimum

| Action | When |
|--------|------|
| Hivemind awareness + handoffs | Session start |
| Workspace lock | Before frozen paths |
| Status post | Track start + each P0 flip |
| SESSION_ANCHOR update | After any B1–B4 flip |
| No direct hub edit | Prefer Hivemind; @scribe is Hub Master |

### Hardware

Max **1** concurrent local inference (5700U Zen2, 8MB L3, ~8GB free). MaKaLi: cloud for parallel voices.

### Workhorse (D-432: zero paid Google)

Local → Groq free → OpenRouter `:free` → NIM free → Antigravity OAuth. **Not** “enable Gemini billing” without Architect override.

---

## §1 Execution Tracks — Status Board (v1.1)

Original T+0 parallel design retained for history. **Current status** (hub + probes):

| Track | Owner | Plan intent | Current status | Next action |
|-------|-------|-------------|----------------|-------------|
| **A** Sprint Lead | @kali | Hook + gate | **PARTIAL** — hook file only | Register hook + restart; run gate script |
| **B** WARP | @john_carmack | PolicyKit + 3 IPs | **PARTIAL/FAIL live** | Bring SOCKS up; probe IPs |
| **C** AGY + lease pattern | @maat/P4 | Deploy + handoff | Hub: COMPLETE | Verify cold restart; keep pattern doc |
| **D** MCP Sprint 1 | @maat/P3 | Middleware + tests | Hub: COMPLETE | Align mcp pin story; no re-design |
| **E** Researcher integration | @researcher | Phase 2 + guide | Hub: DISPATCHED/advanced | Close any open handoffs only |
| **F** Temple-grade | @verity | Doc style + T1–T11 | DISPATCHED | Run fail-closed gate; fix real fails |
| **G** (NEW) Dirty-tree land | @maat/P3 | — | **ACTIVE RISK** | Vault commit slice + freeze |
| **H** (NEW) Agent SSOT hygiene | @kali / @grok_cli | — | **THIS HARDENING** | Keep card/plan/anchor ≤12h fresh |

```
NOW ────────────────────────────────────────────────────────────
│ B1 Hook register + OpenCode restart  (@kali)
│ B2 Vault dirty-tree land/freeze      (@maat/P3)
│ B3 W-1 SOCKS live probes             (Carmack/P1)
│ B4 Fail-closed gate run              (@verity)
│ RFC Soul Hardening replies           (fleet, async)
│ G-1 model defaults only (D-432)      (no paid Google)
└── Phase D ONLY if B1 + B2 + B4 green and gate honest
```

---

## §2 Track Details (Reference + Deltas)

### TRACK A — Sprint Lead (Owner: @kali)

| Step | Action | Status |
|------|--------|--------|
| A-1 | Triage P0-Interrupt GitHub unknown issue | Hub: triaged → @maat |
| A-2 | Add `"hooks": { "session_end": ".opencode/hooks/session_end.py" }` to `.opencode/opencode.json` | ❌ **STILL MISSING** |
| A-3 | Broadcast plan / card | Do on every status flip |
| A-4 | Phase D gate evaluation via **fail-closed** script | Use fixed script |
| A-5 | Restart OpenCode after A-2 | Blocks Scribe/Roc until done |

### TRACK B — WARP (Owner: @john_carmack)

Keep B-1..B-6 from v1.0. **Do not mark complete** until:

```bash
ss -lntp | rg '808[123]'
curl --socks5 127.0.0.1:8081 https://ifconfig.me
# repeat 8082, 8083 — three distinct IPs
```

### TRACK C — AGY OAuth (Owner: @maat / P4)

Hub claims complete. Remaining: **cold restart re-auth** verification. Lease protocol docs stay authoritative for Vault Week 2.

### TRACK D — MCP Sprint 1 (Owner: @maat / P3)

Hub claims complete. Remaining hygiene:

- Document single pin story (`mcp>=1.27,<2`; installed may be 1.28.x)  
- Do **not** migrate to mcp v2 until stable + deliberate ticket  
- Spec date pressure (2026-07-28) is **protocol** awareness; dual-transport v1 path remains valid

### TRACK E — Researcher (Owner: @researcher)

No new gap campaigns unless SG-* residual list grows. Prefer **applying** KG-1..6 and research guides.

### TRACK F — Temple-Grade (Owner: @verity)

Use fixed gate script. Prefer real test exit codes over grepping PASS strings.

### TRACK G — Vault Dirty Tree (NEW, Owner: @maat / P3)

| Step | Action |
|------|--------|
| G-1 | Workspace lock `vault` domain |
| G-2 | Land coherent slice: vault_core + blindvault_resolver + models + tests + scanners + pre-commit |
| G-3 | Or freeze with written “do not touch” in HMC via Hivemind |
| G-4 | Update AGENT_SPRINT_CARD freeze table |

### TRACK H — SSOT Hygiene (NEW)

| Step | Action | Cadence |
|------|--------|---------|
| H-1 | Update AGENT_SPRINT_CARD `LAST_VERIFIED` | Every P0 flip |
| H-2 | Update SESSION_ANCHOR | Every P0 flip |
| H-3 | Reject “all gaps closed” language without EXEC column | Always |

---

## §3 Dependency Graph (Hardened)

```
B1 Hook register ──► A-5 Restart ──► Scribe/Roc distillation unblocked
B2 Vault land/freeze ──► safe parallel work on providers/search
B3 W-1 live ──► G-1c multi-IP plans allowed (else FORBIDDEN claim)
B4 Honest gate ──► Phase D entry decision
Soul RFC ──X──► no implementation dependency this week
```

**Hard rule**: Tracks that only exist in prose without probes do not unlock Phase D.

---

## §4 Agent Assignments (Who Does What Now)

| Agent | Now | Not now |
|-------|-----|---------|
| **@kali** | B1 hook, gate call, freeze enforcement | Solo vault rewrite |
| **@maat / P3** | Track G vault land; mcp pin hygiene | Re-open V-1 crypto research |
| **@maat / P4** | AGY cold-restart verify | New OAuth designs |
| **@john_carmack / P1** | B3 W-1 live | Claiming pool without probes |
| **@verity** | B4 gate + mandate honesty | Rubber-stamp Phase D |
| **@researcher** | Only residual SG research if asked | 46-gap re-survey |
| **@roc_racoon** | Standby for distillation after B1; RFC answers | Implementing soul_health.py pre-consensus |
| **@scribe** | Ready after B1; hub mastery | Writing soul.yaml directly |
| **@lilith** | Standby Phase D run-side | Starting D-* early |
| **@grok_cli** | Adversarial SSOT / this hardening | Wiring Grok fleet without vault+ACP smoke |
| **@jem / @doom_guy / @grokster** | RFC replies; support reviews | Competing roadmaps |

---

## §5 Hivemind Protocol (Unchanged Discipline)

| Action | Tool | When |
|--------|------|------|
| Heartbeat | `hivemind_heartbeat` | Every 5–10 min active work |
| Status | `hivemind_post_context(intent="status")` | Start + P0 flips |
| Blocker | `intent="blocker"` | Stuck >5 min |
| Lock | workspace lock acquire | Frozen paths |
| Handoff | handoff submit/accept/complete | Cross-agent work |

Session end: L1→L2→L3 → `proposed_lessons.yaml` (manual until B1 live).

---

## §6 Phase D Gate Criteria (Honest)

| # | Criterion | v1.0 claim | Honest rule |
|---|-----------|------------|-------------|
| 1 | C-0 honest tests | ✅ | `make test` real pass/fail/skip posted |
| 2 | C-1′ SoulStore writer | ✅ | No raw soul writers outside SoulStore |
| 3 | C-2′ OOMProtector | ✅ | Contract/property tests green |
| 4 | C-3 restic | ⚠️ | Script **and** timer/repo probe (not “script exists”) |
| 5–8 | MCP audit, dual transport, MaKaLi, breakers | ✅ | Re-verify if dirty tree touches them |
| 9 | GenerationPolicy | ⚠️ | Optional warn until contract tests |
| 10–12 | Admission, quota routing, property tests | ✅ | Re-run targeted pytest |
| 13 | V-1 VaultCore | ✅ narrative | **EXEC-CLOSED only if tests green + landed or Architect accepts dirty** |
| 14 | C-0.5 distillation | ❌ | Hook registered **and** fired once |
| 15 | temple-grade | ⚠️ | Real T1–T11, not inverted greps |

**Gate script**: `scripts/verify_phase_d_gate.py` (v1.1 fail-closed). Exit 0 required for automated claim; any FAIL must be listed in HMC.

---

## §7 Execution Phases (Ordered by Criticality x Impact)

### Phase I: INTEGRITY GATE (B1-B5)
Clear the 5 P0 blockers from \u00a70.2. **These are the only things that matter right now.**

### Phase II: PROCESS REFORM (P-1..P-7)
Fix the 10 systemic process failures identified in PROCESS_IMPROVEMENT_PLAN_20260725.md:
- P-1: Probe-backed OMEGA_ENGINE claims
- P-2: DB consolidation (9 DBs \u2192 3)
- P-3: Vector consolidation (7 collections \u2192 3, remove FAISS)
- P-4: Unified soul distiller
- P-5: Kill C-6' breaker clones (adopt pybreaker)
- P-6: Split god modules >1000 lines
- P-7: MCP version single source

### Phase III: PHASE D \u2014 LIVING RESEARCH OS (D-1..D-5)
Only after Integrity Gate + Process Reform are green:
- D-1: Content persistence + TTL cache
- D-2: SQLite job store
- D-3: Initial index builder
- D-4: Vault Week 2 (ACP smoke, Grok fleet)
- D-5: MCP Sprint 2 (Streamable HTTP)

### Phase IV: OBSERVABILITY (O-1..O-3)
- O-1: Prometheus client + /metrics endpoint
- O-2: Alert routing
- O-3: Dashboard / web UI

### Phase V: PHASE E \u2014 IDENTITY FLUIDITY (E-0..E-2)
- E-0: Soul kernel \u2192 agent config
- E-1: Temporal trace
- E-2: Voice calibration

### Phase VI: PHASE F \u2014 COMMUNITY TOOL (Ongoing)
Default fully local. No cloud dependency for basic operation.

---

## §8 Communication Plan

| Event | Channel | Format |
|-------|---------|--------|
| P0 flip | Hivemind + SESSION_ANCHOR | status + probe output |
| False capacity claim | Blocker post | “probe failed: …” |
| Phase D verdict | HMC via Scribe/Kali | criteria table + script log |
| RFC replies | Agent Discussion Threads | `> **@you**: [RE: Soul Hardening RFC]` |

---

## §9 Changelog

| Version | Date | Change |
|---------|------|--------|
| v1.0.0 | 2026-07-25 | Initial 6-track pre-launch plan |
| v1.1.0 | 2026-07-25 | Reality snapshot; agent support packet; residual SG gaps; Tracks G/H; fail-closed gate; kill “all blind spots closed” for execution |

---

*⬡ OMEGA ⬡ KALI ⬡ FLEET ⬡ PHASE-D-GATE ⬡ EXEC-PLAN-v1.1 ⬡ 2026-07-25*
