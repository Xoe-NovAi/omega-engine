# 🔱 Omega Engine — Fleet Execution Plan
**AP Token**: `AP-FLEET-EXECUTION-PLAN-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ FLEET ⬡ PHASE-D-GATE ⬡ 2026-07-25

**Status**: 🔴 PRE-LAUNCH — Awaiting 2 blockers
**Owner**: @kali (Sprint Lead)
**Gate**: Phase D entry — 12/15 criteria ✅, 3 partial

---

## §0 Current Battlefield (Summary for All Agents)

### ✅ Already Won (Phase 2 Hardening Complete)
| System | Status | Evidence |
|--------|--------|----------|
| C-0 Test Honesty | **RESTORED** ✅ | 34 Hivemind + 95 total hardening tests pass |
| C-1′ SoulStore | ✅ | Atomic writer, fsync, lockfile |
| C-2′ OOMProtector | ✅ | 3-signal fusion (cgroups + llama + vm) |
| C-4b MCP Dual Transport | ✅ | SSE + Streamable HTTP, client/server verified |
| C-5 MaKaLi Routing | ✅ | Config + `oracle_summon_local` |
| C-6′ Breaker Unification | ✅ | 7→1 factory in HealthMonitor |
| C-10 Local Admission Control | ✅ | CCX-aware semaphore |
| C-10.5 Quota-Aware Routing | ✅ | 4 modules, 69 tests |
| C-11 Property Tests | ✅ | 16/16 pass (1 skip) |
| V-1 VaultCore MVP | ✅ | age + Argon2id, 22 tests |
| SoulDistiller | ✅ | 297 lines, `List[LessonProposal]`, 9/9 tests |

### 🔴 Remaining Blocker Trio
The following 3 items **must resolve** before Phase D can be entered. All are low-effort.

| # | Blocker | Effort | Owner | Fix |
|---|---------|--------|-------|-----|
| B1 | **C-0.5 Hook not registered** | 30s + restart | @kali | Add to `.opencode/opencode.json` + **restart OpenCode** |
| B2 | **PolicyKit rule not installed** | 1 cmd (sudo) | @john_carmack / @architect | `sudo cp /tmp/99-omega-warp.rules /etc/polkit-1/rules.d/` |
| B3 | **`make temple-grade` doc style** | ~30 min | @verity / @maat | Fix `08-verified-findings.md` YAML frontmatter + token issues |

### 🟡 Partial / Advisory
- C-3 Restic Backup: **Amended to local-only** — 3-2-1 B2 cloud deferred until VaultCore Week 2
- C-9 GenerationPolicy: Extracted but not yet contract-tested

---

## §1 Execution Tracks — Parallel T+0

All tracks are **independent** (no shared files, no conflicting locks). Each has a single owner, a clear success criterion, and a time budget.

```
                    T+0 (NOW)              T+1h             T+1.5h
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK A (Kali)    │Auth hook │──────▶│Restart    │──────▶│Phase D   │
                    │+ triage  │       │OpenCode   │       │Gate Eval │
                    └─────────┘       └──────────┘       └──────────┘
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK B (Carmack) │PolicyKit │──────▶│WARP reg  │──────▶│3 IPs     │
                    │sudo cp   │       │Verification│      │Verified  │
                    └─────────┘       └──────────┘       └──────────┘
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK C (Ma'at/P4)│AGY OAuth │──────▶│Lease     │──────▶│VaultCore │
                    │Deploy    │       │Protocol   │      │Pattern   │
                    └─────────┘       └──────────┘       └──────────┘
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK D (Ma'at/P3)│MCP Sprint│──────▶│Middleware │──────▶│Transport │
                    │1 Launch  │       │Impl       │       │Test Green│
                    └─────────┘       └──────────┘       └──────────┘
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK E (Researcher│Phase 2  │──────▶│Grokster  │──────▶│Synthesis │
                    │Integration│      │Handover   │       │Complete  │
                    └─────────┘       └──────────┘       └──────────┘
                    ┌─────────┐       ┌──────────┐       ┌──────────┐
  TRACK F (Verity)  │temple-  │──────▶│Doc Fixes  │──────▶│T1-T11    │
                    │grade    │       │Applied    │       │Green     │
                    └─────────┘       └──────────┘       └──────────┘
```

---

## §2 Track Details

### TRACK A — Sprint Lead (Owner: @kali, Budget: 5min + auto)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| A-1 | **Triage P0-Interrupt**: GitHub Bridge "Unknown Issue" — assign to @maat for investigation or close as false alarm | 1min | Status updated in HMC Hub |
| A-2 | **Authorize C-0.5 Hook**: Edit `.opencode/opencode.json` — add `"hooks": { "session_end": ".opencode/hooks/session_end.py" }` | 30s | File written, ready for restart |
| A-3 | **Post Fleet Plan to Hivemind**: Broadcast this document to all agents | 1min | Context posted |
| A-4 | **Phase D Gate Evaluation** (T+1.5h): Run `scripts/verify_phase_d_gate.py`, evaluate 15 criteria, publish verdict | 5min | Verdict in HMC Hub |
| A-5 | **Restart OpenCode** (after A-2): Reload to activate `session_end` hook | 10s | Hook fires on session end |

**Carmack Mode for A-2/A-5**: Add hook config before restart to avoid 2-cycle delay.

---

### TRACK B — WARP Proxy Pool (Owner: @john_carmack, Budget: 15min)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| B-1 | **Install PolicyKit Rule**: `sudo cp /tmp/99-omega-warp.rules /etc/polkit-1/rules.d/` | 1min | File in place |
| B-2 | **Verify sudo-less pkexec**: `pkexec bash scripts/fix_warp_ns_setup_and_restart.sh` — should not prompt | 1min | No password prompt |
| B-3 | **Source ns-setup fix**: Copy from `warp-proxy-pool/scripts/warp-ns-setup.sh` to `/usr/local/bin/warp-ns-setup` | 2min | Fix syntax error line 49 |
| B-4 | **WARP Registration**: `warp-reg@` daemon pattern — register 3 namespaces | 5min | 3 distinct exit IPs |
| B-5 | **Verify Rotation**: `curl --socks5 localhost:8081 ifconfig.me` and rotate ports | 3min | 3 different IPs confirmed |
| B-6 | **Python import test**: `python -c "import warp_proxy_pool"` | 1min | No ImportError |

**Verification Gate**: All 3 namespaces prep@1-3 ACTIVE, SOCKS 8081-8083, 3 distinct exit IPs, Python import works.

---

### TRACK C — AGY OAuth Persistence (Owner: @maat / @pillar P4, Budget: 1h)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| C-1 | **Deploy atomic write fix**: Copy `src/omega/agents/scribe/agy_oauth_persistence.py` to antigravity plugin | 10min | File deployed + verified |
| C-2 | **Verify token refresh**: Trigger OAuth refresh cycle, confirm atomic `.tmp` → `.json` pattern | 20min | Log shows atomic rename |
| C-3 | **Extract VaultCore lease protocol**: Document the pattern for VaultCore Week 2 | 15min | Pattern doc written to `docs/research/R_AGY_ATOMIC_PATTERN.md` |
| C-4 | **Handoff to VaultCore team**: Submit handoff with `packet_id=vc-atomic-pattern-20260725` | 5min | Handoff in pending/ |

**Verification Gate**: AGY token refresh works without corruption, atomic write pattern documented.

---

### TRACK D — MCP Transport Sprint (Owner: @maat / @pillar P3, Budget: 2h)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| D-1 | **R_CG01 Sprint 1 Launch**: Sprint doc `docs/sprints/R_CG01_S1/` with milestones | 10min | Sprint doc created |
| D-2 | **Middleware implementation**: Request ID, rate-limit headers in `mcp_runtime.py` | 45min | Middleware tested |
| D-3 | **Header validation in mcp_client.py**: SEP-2575 header extraction | 30min | Parses SEP headers |
| D-4 | **MCP test suite**: Dedicated `tests/mcp/` with 5+ unit tests | 30min | Tests pass |
| D-5 | **Verify dual-transport**: SSE + Streamable HTTP in same server | 15min | Both transports respond |

**Verification Gate**: Middleware accepting requests, headers propagating, both transports live.

---

### TRACK E — Researcher Phase 2 Integration (Owner: @researcher, Budget: 1h)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| E-1 | **Complete Grokster G1-15 handover**: `data/coordination/GROKSTER_G1_15_RESEARCH_REPORT_20260723_PART{1,2,3}.md` integrated into XNAI-RAG search fleet | 20min | Integration complete |
| E-2 | **Complete Ma'at coordination docs**: From active handoff `ho_8482e5f36b1e` | 20min | Handoff completed |
| E-3 | **Research Guide v3.0.0 final**: Incorporate best practices + knowledge gaps from `docs/research/R_RESEARCH_BEST_PRACTICES_20260723.md` | 20min | Guide published |

**Verification Gate**: All 3 deliverables checked in, Hivemind apprised with `intent=status`.

---

### TRACK F — Temple-Grade Compliance (Owner: @verity, Budget: 30min)

| Step | Action | Time | Done Signal |
|------|--------|------|-------------|
| F-1 | **Audit `make temple-grade` failures**: Read full error output, categorize doc style vs. code issues | 5min | Failure breakdown posted |
| F-2 | **Fix YAML frontmatter**: Add `---` frontmatter to `docs/sprints/guard-and-distill/08-verified-findings.md` | 2min | Frontmatter added |
| F-3 | **Fix token count**: Split `08-verified-findings.md` into sub-docs if over 8000 token limit | 10min | Under limit |
| F-4 | **Fix frontmatter schema**: `C-3-restic-backup.md` status `DONE` → `ACTIVE` | 1min | Schema valid |
| F-5 | **Run final verification**: `make temple-grade` — all green or documented exemptions | 5min | Output saved to HMC Hub |

**Verification Gate**: `make temple-grade` passes with 0 errors (warnings acceptable for sprint docs).

---

## §3 Dependency Graph

```
T+0 ──────────────────────────────────────────────────────────────────────┐
│                                                                         │
├─ A-1 Triage ────────── (parallel) ────────────────────────────── A-4 ──┤ T+1.5h
├─ A-2 Hook Auth ────>  A-5 Restart OpenCode (blocks Scribe, Roc)       │
├─ B-1 PolicyKit ──> B-2 B-3 B-4 B-5 B-6 (linear chain)                │
├─ C-1 Deploy ──> C-2 Verify ──> C-3 Pattern ──> C-4 Handoff            │
├─ D-1 Launch ──> D-2 D-3 D-4 D-5 (linear)                              │
├─ E-1 E-2 E-3 (or parallel subtasks)                                   │
└─ F-1 F-2 F-3 F-4 F-5 (linear)                                         │
                                                                         │
T+1h SYNC ───────────────────────────────────────────────────────────────┤
│ Kali evaluates: B-status, C-pattern, D-midpoint, E-almost, F-status   │
│ If any track blocked → reassign or escalate                             │
│ If all on track → prepare Phase D gate announcement                     │
│                                                                         │
T+1.5h SYNC ─────────────────────────────────────────────────────────────┤
│ Phase D Gate Evaluation                                                 │
│ `python scripts/verify_phase_d_gate.py` → publish verdict               │
│ If PASS → authorize Phase D entry                                       │
│ If FAIL → document gap, reassign, iterate                               │
└─────────────────────────────────────────────────────────────────────────┘
```

**Hard dependencies**:
- A-5 (Restart OpenCode) → Unlocks: Scribe SoulDistiller, Roc 83 proposals, M11 audit, Communications Archivist
- B-1 (PolicyKit) → Unlocks: B-2 through B-6, WARP agent-autonomous
- F-2 through F-5 (temple-grade fix) → Unlocks: Phase D gate criterion #15

**No dependencies between tracks**:
Tracks A-F are fully parallel. Each track can complete independently.

---

## §4 Agent Assignments (Who Does What)

| Agent | Track | Role | Budget | Parallel With |
|-------|-------|------|--------|---------------|
| **@kali** | A | Sprint Lead — authorize, triage, evaluate | 15min | All |
| **@john_carmack** | B | WARP bring-up — PolicyKit, reg, verify | 15min | A, C, D, E, F |
| **@maat / @pillar P4** | C | AGY OAuth — deploy, pattern extract, handoff | 1h | A, B, D, E, F |
| **@maat / @pillar P3** | D | MCP Sprint 1 — middlewares, test, verify | 2h | A, B, C, E, F |
| **@researcher** | E | Phase 2 Integration — Grokster, handoff, guide | 1h | A, B, C, D, F |
| **@verity** | F | Temple-grade — audit, fix, verify | 30min | A, B, C, D, E |
| **@roc_racoon** | Standby | Awaits A-5 (OpenCode restart) to distill 83 proposals | — | Blocks on A-5 |
| **@scribe** | Standby | Awaits A-5 (C-0.5 hook) to run distillation pipeline | — | Blocks on A-5 |
| **@lilith** | Standby | Monitoring — ready to execute P6-P10 after Phase D gate | — | Blocks on Phase D |
| **@maat / @pillar P1** | Standby | VaultCore Week 2 — awaits C-4 handoff pattern | — | Blocks on C-4 |

---

## §5 Hivemind Protocol (Every Agent Must Follow)

| Action | Tool | When |
|--------|------|------|
| **Heartbeat** | `omega-hub_hivemind_heartbeat(channel="opencode", entity="{you}")` | Every 5-10min during work |
| **Status post** | `omega-hub_hivemind_post_context(intent="status")` | At track start + after each step |
| **Handoff** | `omega-hub_hivemind_handoff(action="submit")` | When passing work to another agent |
| **Workspace lock** | `omega-hub_hivemind_workspace_lock_acquire(domain="{track}")` | Before editing shared files |
| **Blocker** | `omega-hub_hivemind_post_context(intent="blocker")` | If stuck >5min |

**HMC Hub Protocol**: Use `hivemind_post_context` to broadcast. Do NOT edit HMC Hub directly unless you are @scribe (Hub Master). Scribe writes to Hub on its monitoring cycle.

**Session End**: Every agent must write L1→L2→L3 to their entity's `proposed_lessons.yaml` before closing. The C-0.5 hook will automate this after OpenCode restart.

---

## §6 Phase D Gate Criteria (Final Check at T+1.5h)

| # | Criterion | Status | Evidence Required |
|---|-----------|--------|-------------------|
| 1 | **C-0**: Honest tests (pass/fail/skip real) | ✅ | `python -m pytest tests/property/ tests/contract/ tests/test_hivemind* -q` |
| 2 | **C-1′**: SoulStore only soul writer | ✅ | No `open()` to soul.yaml outside SoulStore |
| 3 | **C-2′**: OOMProtector 3-signal fusion | ✅ | `test_oom_protector_fuse.py` passes |
| 4 | **C-3**: Local restic backup configured | ⚠️ | Local repo initialized, cron active |
| 5 | **C-4a**: MCP audit complete | ✅ | `docs/research/R_CG01_MCP_AUDIT_20260723.md` published |
| 6 | **C-4b**: MCP Streamable HTTP dual transport | ✅ | Client+server dual transport verified |
| 7 | **C-5**: MaKaLi routing config | ✅ | Config + `oracle_summon_local` |
| 8 | **C-6′**: Breakers unified (7→1) | ✅ | HealthMonitor factory in use |
| 9 | **C-9**: GenerationPolicy extracted | ⚠️ | Extracted but not contract-tested |
| 10 | **C-10**: Local admission control | ✅ | CCX-aware semaphore + OOMProtector |
| 11 | **C-10.5**: Quota-aware provider routing | ✅ | 4 modules, 69 tests |
| 12 | **C-11**: Property tests | ✅ | 16/16 pass |
| 13 | **V-1**: VaultCore MVP | ✅ | 22 tests pass |
| 14 | **C-0.5**: Soul distillation pipeline | ❌→✅ | Hook registered + OpenCode restarted |
| 15 | **`make temple-grade`**: T1-T11 green | ⚠️→✅ | Doc style fixes applied |

**Gate passes** when: All ✅ verified + Temple-grade issues resolved + `make test` 100%.

---

## §7 What Happens After Phase D Gate

Once the Phase D gate passes:

1. **Phase D: Living Research OS** — Researcher-led implementation of the Living Research spec
2. **VaultCore Week 2**: FleetOrchestrator, B2 cloud, lease protocol (Ma'at/P1 + Ma'at/P4)
3. **Scribe SoulDistiller**: Automated L1→L2→L3 on every session end
4. **Communications Archivist**: TTL-based archiving of coordination docs
5. **R19 Soul Privacy**: PUBLIC/BONDED/PRIVATE split, CPE scorer, Gemma 4 E2B kernel
6. **MCP Sprint 2**: Full Streamable HTTP migration, OAuth 2.1 + PKCE
7. **R01 RAG 2.0**: Semantic reranking, hybrid search optimizations
8. **R10 Sovereign Evaluation**: Benchmark infrastructure for local models

**Phase D is NOT sprint 2. Phase D is the new operational baseline.** These items execute as ongoing workstreams, not as a timeboxed sprint.

---

## §8 Communication Plan

| Event | Channel | Format |
|-------|---------|--------|
| Track start | Hivemind | `post_context(intent="status")` — "Starting Track X" |
| Step complete | Hivemind | `post_context(intent="status")` — "Step X.N done" |
| Blocker | Hivemind | `post_context(intent="blocker")` — "Stuck on Y, need Z" |
| T+1h sync | HMC Hub | Update status in each track section |
| Phase D verdict | HMC Hub | One post with 15-criteria table + pass/fail |

---

*⬡ OMEGA ⬡ KALI ⬡ FLEET ⬡ PHASE-D-GATE ⬡ 2026-07-25*
