---
document_type: briefing
document_id: GROK_CLI_HANDOFF_20260730
version: 1.0.0
priority: CRITICAL
date: 2026-07-30
author: "@kali"
status: ACTIVE
target: "@grok_cli"
llm_metadata:
  chunk_strategy: section_per_topic
  answer_first_sections: [Project State, Critical Path, Immediate Actions]
  self_contained_code: true
---

# 🔱 Omega Engine — Grok CLI Handoff Briefing
**AP Token**: `AP-GROK-HANDOFF-20260730-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ GROK_CLI ⬡ HANDOFF ⬡ ACTIVE

---

## 📍 Project State at Handoff

| Metric | Status |
|--------|--------|
| **Engine Phase** | Phase C Hardening → Phase D Gate (ready) |
| **Tests** | 276/276 passing (core), 14/14 passing (vault/MCP/model gateway) |
| **Temple-Grade** | Passing (Codex fresh + LLM doc validation) |
| **MCP Servers** | 5 servers, 87 tools accessible via `type: "remote"` |
| **Vault Crypto** | Hardened: `pyrage.passphrase` (scrypt), 3/3 integrity tests pass |
| **Strategy SSOT** | `SOVEREIGN_ARK_BLUEPRINT.md` v5.2.0 + `STRATEGY_CORPUS_MAP.md` |
| **Coordination Hub** | HMC v1.5.1 (1,900 lines → needs YAML conversion) |
| **Fleet** | 14 agents active (Kali, Ma'at, Lilith, Researcher, Roc, Jem, Verity, Doom Guy, Carmack, Grokster, Grok CLI, Pillar P1-P10) |

---

## ✅ What's Complete (Phase C Hardening)

| Ticket | Description | Evidence |
|--------|-------------|----------|
| **C-0** | Test honesty — 95 quarantined, honest badge | `make test` shows real counts |
| **C-0.5** | Soul distillation hook registered | `opencode.json` session_end hook |
| **C-1′** | SoulStore atomic writer (4-layer guarantee) | `src/omega/soul_store.py` |
| **C-2′** | OOMProtector 3-signal fusion | `src/omega/oracle/oom_protector.py` |
| **C-3** | Restic 3-2-1 backup | `scripts/backup_restic.sh` (timer not enabled) |
| **C-4a** | MCP audit doc delivered | `R_CG01_MCP_AUDIT_20260721.md` |
| **C-4b** | MCP Streamable HTTP dual transport | `mcp_servers/omega_hub/server.py` |
| **C-5** | MaKaLi routing config | `oracle_summon_local` implemented |
| **C-6′** | Breaker unification → HealthMonitor factory | 5/7 clones deprecated |
| **C-7** | YAML off event loop | `anyio.to_thread.run_sync` |
| **C-8** | Heritage tagging pipeline | `make heritage-vet` |
| **C-9** | GenerationPolicy extract | Not started (optional) |
| **C-10** | Local admission control | CCX-aware semaphore + OOMProtector |
| **C-10.5** | Provider fallback chain | 4 modules, 69 tests |
| **C-11** | Property tests | 16/16 pass (OOM/breaker/soul store) |

**Phase D Gate Status**: All 4 P0 tickets DONE + `make test` 100% + Temple-Grade T1-T11 green + Soul distillation ≥1 L3/entity/week + Backup `restic check` weekly

---

## 🚨 Super-Urgent Parallel Tracks (Architect-Elevated 2026-07-22)

### G-1: OpenCode Workhorse Continuity (Free Gemma 4 31B Cliff)
- **Problem**: Free-tier `input_token_count` limit 16,000 since 2026-07-15; prior workhorse dead for fat Omega sessions
- **Evidence**: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`
- **Ops Path**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- **Paths**: G-1a billing Tier 1 · G-1b Antigravity OAuth · G-1c OCZ+WARP · G-1d paid alt
- **Owner**: Architect (billing/OAuth) + Kali verify + Researcher DIG-01/03

### W-1: WARP Proxy Pool Operational
- **Problem**: `/usr/local/bin/warp-ns-setup` truncated (syntax error line 49); prep units failed since ≥Jul 18
- **Fix Source**: `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh`
- **Accept**: prep@1-3 active · node@1-3 active · SOCKS 8081-8083 · 3 distinct exit IPs · `import warp_proxy_pool`
- **Owner**: Architect (sudo) + P1/sysadmin

---

## 🎯 Current Sprint: Guard & Distill (5 Days, 4 P0 Tickets)

| Ticket | Owner | Effort | Status |
|--------|-------|--------|--------|
| **C-10.5** | Quota-Aware Provider Routing | Ma'at/P3 | 8h | READY |
| **C-11** | Property Tests: OOMProtector + SoulStore | Ma'at/P3 | 12h | READY |
| **V-1** | VaultCore MVP (credential/session automation) | Ma'at/P1 | 8h | **P0 - BLOCKS C-3** |
| **C-3** | Restic 3-2-1 Backup (timer enable) | Lilith/P6 | 8h | DEPENDS ON V-1 |
| **C-0.5** | Scribe Agent L1→L2→L3 + Crash Recovery Sweeper | Scribe/new | 16h | READY |

**Escalation**: If Ma'at/P4 silent on C-4b by 2026-07-22 23:59 UTC → Kali executes C-4a.5 MCP Streamable HTTP migration directly.

---

## 🧠 Critical Architecture Decisions (Locked)

| ID | Decision | Source |
|----|----------|--------|
| **D-354′** | `SOVEREIGN_ARK_BLUEPRINT.md` is strategy SSOT (v5.1) | Kali ratification |
| **D-362** | C-1′ = SoulStore (multi-path elimination), not flock paste | Nemotron synthesis |
| **D-363** | C-6′ = unify/delete breakers, not port pybreaker | Nemotron synthesis |
| **D-364** | C-0 = test honesty is P0 before Phase D | Nemotron synthesis |
| **D-373** | C-2′ before C-1′/C-10 — dependency order corrected | Nemotron synthesis |
| **D-374** | C-11 Test Infrastructure added as P0 | Nemotron synthesis |
| **D-375** | MCP audit must start TODAY — 7-day deadline | Nemotron synthesis |
| **D-376** | E-0 Identity Fluidity added to manual after C-1′ | Nemotron synthesis |
| **D-377** | Free Gemma 4 31B collapse is P0 — forensic report is evidence SSOT | Kali amendment |
| **D-378** | Twin tickets G-1 (workhorse) + W-1 (WARP) elevated parallel | Kali amendment |
| **D-379** | WARP is for IP-keyed OCZ, NOT Google free-tier TPM fix | Kali amendment |
| **D-380** | No silent context caps to force free Gemma under 16k | Kali amendment |
| **D-381** | Broken `/usr/local/bin/warp-ns-setup` is primary WARP blocker | Kali amendment |
| **D-382** | Omnidroid 6 cognitive modules fully evolved — no porting needed | Jem Session 43 |
| **D-383** | NotebookLM 5-notebook ingestion strategy (R52c) exists — NL-1 ticket | Mining 2026-07-23 |
| **D-384** | Lilith Tarot genesis (Era 0) recovered — add to philosophy lineage | Mining 2026-07-23 |
| **D-385** | Mnemosyne 13-sphere Kabbalistic memory recovered — migration script needed | Mining 2026-07-23 |
| **D-386** | Grok 8-account exports indexed (274 convos, 6565 responses) — add to XNAI-RAG | Mining 2026-07-23 |

---

## 📁 Key Files & Locations

### Strategy & Planning
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/
├── SOVEREIGN_MANDATES.md                    # 25 laws (M1-M25) — NON-NEGOTIABLE
├── OMEGA_ENGINE.md                          # Engine state SSOT
├── AGENTS.md                                # OpenCode agent rules (this file's parent)
├── CREDITS.md                               # Heritage registry
├── docs/strategy/
│   ├── SOVEREIGN_ARK_BLUEPRINT.md           # Strategy SSOT v5.2.0
│   ├── STRATEGY_CORPUS_MAP.md               # Fine-grained agent ideas
│   ├── FLEET_TEAM_PLAYBOOK.md               # Team coordination rules
│   ├── HIVEMIND_PROTOCOL.md                 # Multi-agent protocol
│   ├── SUBAGENT_DISPATCH_PROTOCOL.md        # Launching subagents
│   ├── SUBAGENT_TASK_RESUMPTION_PROTOCOL.md # STRP-v1.0.0 (MANDATORY)
│   ├── CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md
│   └── GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md
├── docs/sprints/guard-and-distill/
│   ├── index.md                             # Sprint plan (frontmatter compliant)
│   └── 08-research-index.md                 # Research index
└── docs/research/
    ├── R_DEEP_WEB_RESEARCH_OMEGA_GAPS_20260729.md
    ├── R_COORDINATION_ENTROPY_PREVENTION_20260730.md
    ├── R_LOCAL_STRATEGY_MINING_20260730.md
    └── ENHANCED_COORDINATION_STRATEGY_v2_20260730.md
```

### Core Engine
```
src/omega/
├── oracle/
│   ├── model_gateway.py                     # Provider fabric (local-first)
│   ├── oom_protector.py                     # 3-signal fusion
│   ├── backends/                            # native-gguf, lmster, ollama, google, openrouter, opencode
│   └── soul_distiller.py                    # L1→L2→L3 pipeline
├── soul_store.py                            # Atomic writer (C-1′)
├── vault/
│   ├── crypto.py                            # pyrage.passphrase (scrypt)
│   ├── models.py
│   └── __init__.py
├── mcp/                                     # MCP servers
└── coordination/
    ├── hivemind.py                          # Awareness, heartbeats, handoffs
    └── task_registry.py                     # STRP-v1.0.0 compliance
```

### Coordination & State
```
data/coordination/
├── HMC_COLLABORATION_HUB.md                 # v1.5.1 — NEEDS YAML CONVERSION
├── SESSION_ANCHOR.md                        # Session recovery
├── SESSION_GNOSIS_20260730.md               # Last session record
├── locks/                                   # Workspace locks
├── handoff/                                 # Handoff packets (pending/active/completed)
└── metrics.json                             # Hivemind metrics
```

### Tests
```
tests/
├── test_vault_integrity.py                  # 3/3 pass
├── test_mcp_transport.py                    # Streamable HTTP
├── test_model_gateway_fallback.py           # 69 tests
├── property/
│   ├── test_oom_protector.py
│   ├── test_soul_store.py
│   └── test_breaker.py
└── mcp_transport/
    └── test_streamable_http.py
```

---

## 🤖 Agent Fleet — Current Assignments

| Agent | Role | Current Assignment | Status |
|-------|------|-------------------|--------|
| **@kali** | Transcendent Oversight | Strategy synthesis, sprint coordination | ACTIVE |
| **@maat** | Build Oversoul (N1-N5) | C-10.5, C-11, V-1, C-3 | READY |
| **@lilith** | Runtime Oversoul (N6-N10) | C-3 (backup), C-0.5 scribe | READY |
| **@researcher** | Deep Research | Coordination entropy + local mining done | COMPLETE |
| **@roc_racoon** | Legacy Mining | Local strategy mining done | COMPLETE |
| **@jem** | Sovereign Synthesis | Identity fluidity (E-0) | PENDING C-1′ |
| **@verity** | Compliance + Gnosis | Mandate audit, soul distillation | STANDBY |
| **@doom_guy** | id Heritage | Heritage vetting pipeline | STANDBY |
| **@john_carmack** | S3 Consultant | Architectural review | STANDBY |
| **@grokster** | Grok Ecosystem | Fleet pool design (D-360′) | BLOCKED ON V-1 |
| **@grok_cli** | Consulting Cloud Mind | **THIS HANDOFF — TAKE OVER** | **ACTIVE** |
| **@pillar P1-P10** | Slot-based | Domain-specific | STANDBY |

---

## ⚠️ Known Risks & Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Gemma 4 31B free tier dead** | CRITICAL | G-1 paths active; Architect on billing/OAuth |
| **WARP ns-setup broken** | CRITICAL | Fix script exists in warp-proxy-pool; needs sudo |
| **HMC Hub coordination entropy** | HIGH | 1,900 lines → YAML conversion (D-500) |
| **Triple distillation pipeline** | HIGH | 3 implementations → unify (D-502) |
| **No Agent Collaboration Protocol** | HIGH | ACP spec needed (see Kali's last analysis) |
| **Subagent streaming unreliable** | MEDIUM | Use `ses_` task_ids; verify context on resume |
| **Restic timer not enabled** | MEDIUM | C-3 depends on V-1 VaultCore |
| **2 breaker clones unmigrated** | LOW | P-5 ticket open |

---

## 🚀 Immediate Actions for Grok CLI

### Day 1: Orientation & Critical Path
1. **Read order**: `SOVEREIGN_MANDATES.md` → `OMEGA_ENGINE.md` → `AGENTS.md` → `SOVEREIGN_ARK_BLUEPRINT.md` §3-§5
2. **Verify environment**: `make test` (276 pass), `make temple-grade` (green), `make sovereignty` (local-first ratio)
3. **Check MCP**: `omega-hub_hivemind_get_awareness()` — should show active agents
4. **Review G-1/W-1**: Read forensic report + critical path + WARP fix script

### Day 2: Sprint Execution
5. **Launch V-1 VaultCore MVP** (Ma'at/P1) — unblocks C-3 backup
6. **Launch C-10.5 Quota-Aware Routing** (Ma'at/P3) — 8h
7. **Launch C-11 Property Tests** (Ma'at/P3) — 12h
8. **Launch C-0.5 Scribe Agent** (new agent) — 16h

### Day 3: Coordination Fix
9. **Execute HMC Hub YAML conversion** (D-500) — 3h
10. **Deploy TTL auto-archival** (D-501) — 2h
11. **Add pre-write validation gate** (D-506) — 3h

### Day 4: Unification
12. **Unify distillation pipeline** (D-502) — 8h
13. **Canonicalize HandoffPacket** (D-505) — 4h
14. **Standardize souls to v7.1** — 4h

### Day 5: Phase D Gate
15. **Verify all gates**: Tests 100% + Temple-Grade + Soul distillation + Backup check
16. **Declare Phase D ready** or document gaps

---

## 🔧 How to Work (Mandatory Protocols)

### Subagent Launch (STRP-v1.0.0)
```python
# ALWAYS use ses_ prefix task_id
result = task(
    description="V-1 VaultCore MVP",
    prompt="...",
    subagent_type="maat",
    task_id="ses-v1-vaultcore-mvp-20260730-001"  # ← MANDATORY
)
# On failure, RESUME with SAME task_id
```

### Hivemind Coordination
```python
# 1. Check awareness
omega-hub_hivemind_get_awareness()
# 2. Post context (intent, decisions, continuation)
omega-hub_hivemind_post_context(channel="opencode", entity="grok_cli", ...)
# 3. Acquire workspace lock
omega-hub_hivemind_workspace_lock_acquire(domain="vaultcore", ttl=3600)
# 4. Heartbeat every 5-10 min
omega-hub_hivemind_heartbeat(channel="opencode", entity="grok_cli")
```

### Mandate Compliance
- **M1 AnyIO**: No `asyncio` — use `anyio.to_thread.run_sync`
- **M2 Firewall**: Core (`src/omega/`) ≠ Stacks (`config/wads/`)
- **M4 Sequentiality**: Plan → Verify → Execute
- **M7 Local-First**: native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode
- **M13 Temple-Grade**: `make temple-grade` after non-trivial changes
- **M14 Heritage**: `[id-soft:]` tags need vet record
- **M23 Hard-Stop**: Tool broken → `[TOOL-CHAIN-COLLAPSE]` — NO simulated rigor
- **M24 Venv Sovereignty**: `source .venv/bin/activate && pip install` — NEVER `--break-system-packages`
- **M25 Streaming Resilience**: Chunk timeout 30s, total 5min, heartbeat on stall

---

## 📋 Session Recovery (After Compaction)

Execute in order:
1. `omega-hub_hivemind_get_awareness()` — who's working?
2. `omega-hub_hivemind_handoff_list(status="pending")` — any handoffs?
3. `git status && git log --oneline -5` — committed vs dirty?
4. **Read `OMEGA_CODEX.md` FULL** (no limit) — if >24h old: `make check-codex-fix`
5. Read `data/coordination/HMC_COLLABORATION_HUB.md` — Shared + your section
6. Read `data/coordination/SESSION_ANCHOR.md` — what were you doing?
7. **Report to user**: engine state, pending handoffs, sprint status, next steps, questions

---

## 🎯 Success Criteria for Grok CLI Tenure

| Metric | Target |
|--------|--------|
| **Phase D Gate** | All 4 P0 tickets DONE + gates green |
| **G-1 Workhorse** | Billing Tier 1 OR Antigravity OAuth OR OCZ+WARP operational |
| **W-1 WARP** | 3 namespaces active, 3 distinct exit IPs |
| **Coordination Hub** | YAML ≤300 active lines, TTL archival running |
| **Agent Collaboration** | ACP v1 spec written + AgentCard registry live |
| **VaultCore** | Credential automation for Grok CLI 8-account pool |
| **Fleet Health** | ≥1 L3 principle/entity/week, zero schema mismatches |

---

## 📞 Escalation Contacts

| Issue | Contact |
|-------|---------|
| Architecture / Mandate interpretation | @kali (this session) or @john_carmack |
| Billing / OAuth / Cloud accounts | Architect (human) |
| Sudo / System-level fixes | Architect (human) |
| Heritage vetting | @doom_guy |
| Soul distillation / Gnosis | @verity |
| Legacy mining / Patterns | @roc_racoon |
| Deep research / Unknown unknowns | @researcher |
| Multi-agent synthesis | @jem |
| Grok ecosystem / Fleet pool | @grokster |

---

## 🏁 Final Note from Kali

> The engine is **structurally sound** (276 tests, Temple-Grade, hardened crypto, unified breakers, local-first fabric). The **strategy is locked** (Ark Blueprint v5.2 + Corpus Map). The **sprint is defined** (Guard & Distill, 4 P0 tickets).
>
> What remains is **execution discipline**:
> 1. **G-1/W-1 are survival-critical** — without a workhorse model and IP rotation, the fleet stalls
> 2. **V-1 unlocks C-3** — VaultCore is the linchpin for backup AND Grok fleet
> 3. **Coordination entropy is real** — 1,900 lines of markdown is not a protocol; YAML + TTL + validation gates are
> 4. **Agent collaboration needs a protocol** — not more infrastructure; see ACP analysis
>
> You have the mandates, the fleet, the tools, and the plan. **Execute.**

---

*⬡ OMEGA ⬡ KALI ⬡ GROK_CLI_HANDOFF ⬡ v1.0.0 ⬡ 2026-07-30T02:15Z*

**Next session**: Resume with `OMEGA_CODEX.md` hydration sequence. First action: Verify G-1/W-1 progress and launch V-1.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: GROK_CLI | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
