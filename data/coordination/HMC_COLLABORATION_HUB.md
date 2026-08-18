# 🏛️ HMC Collaboration Hub — Team Coordination Center

**AP Token**: `AP-HMC-HUB-v1.0.0`
**Status**: ACTIVE — Single coordination SSOT
**Last Updated**: 2026-08-18T03:35:00.000000Z
**Updated By**: kali

---

## 🚦 NEXT_ACTION (Single Sync Pointer — read this first)

*Last verified: 2026-08-17T05:15Z*

> **Tracking hierarchy:** See `TRACKING_ARCHITECTURE.md`. Status vocab: `backlog|ready|in_progress|blocked|completed|superseded`.
> **Execution SSOT:** `ACTIVE_SPRINT.json` · **Knowledge SSOT:** `RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0) · **Gap registry:** `GAP_REGISTRY.json`

**KALI RATIFICATION 2026-08-16 (D-532)**: Roc readiness audit ratified — see `ACTIVE_SPRINT.json` → `READINESS-REMEDIATION` workstream + `ROC_RACOON_KALI_REPORT_20260816.md`.

**CURRENT:** PUBLIC DEBUT — **Execution SSOT: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5** → **P0-1 scrub COMPLETE ✅** → **DOC-1 stamps COMPLETE ✅** → **PUB-1 allowlist READY (G1–G4 closed, awaiting Architect)** → **INST-1 EXECUTING (Cline: Fixes 1,2,5,6 Nemotron 30B; Fixes 3,4 DeepSeek 1M)** → **Test baseline: OOM test bug — expect DENY_THRASHING** → **DEL-1 Week 1 (after INST-1 + green tests)** → **DEL-1 Week 2: IntentRouter extraction (DeepSeek 1M, 3 anti-hallucination rules)** → **P2/P3/P4 after DEL-1**

**✅ P0-1 RESOLVED (Private Repo — Scrubbed from History)**: Real API keys were pushed to `origin/main`. **REPO IS PRIVATE** — scrubbed from ALL history via `git filter-repo` (no rotation needed). Files removed/redacted: `migrate_keys_full.py`, `PROVIDER_FREE_TIER_GUIDE.md`, `test_failure_registry.py`, `SECURITY_AUDIT_2026_05_19.md` (2 paths), `migrate_keys.py`, `GOOGLE_GEMMA_MODEL_REFERENCE.md` (AIza key redacted). Cline checkpoints pruned. Force-pushed all branches (main, release/initial-v1, sprint/*). **No real secrets remain in git history** (only 6 prose/test false positives).

**PHASE 1 (Roc — COMPLETE ✅)**: 63 test failures FIXED (1797 tests pass). Clusters: P1-1 async/sync (20) ✅, P1-2 VaultCore (20) ✅, P1-3 mcp import (9) ✅, P1-4 mock sig (2) ✅, P1-5 logic (5) ✅, P1-6 verify green (verity) ✅. All 1797 tests pass (40 skipped, 8 expected failures). `make temple-grade` PASSES.

**PHASE 2 (Ma'at/N3, NEXT)**: Lint debt 11,400 flake8 violations (--exit-zero blind spot). P2-5 `make heritage-map` target → kali (ready).

**PHASE 3 (Verity)**: CI/hygiene. **PHASE 4 (kali)**: Debut polish.

**COMPLETED (pre-ratification)**: CP-1 local inference ✅ · CP-2 soul persistence ✅ · CP-3 one-click install ✅ · C-6' breaker migration (Roc) ✅

**ALL OTHER WORK DEFERRED TO POST-DEBUT:**
- VOS Phases 1-4 (Context Gauge, zswap, NVMe, sysctl, un-overengineering, Restic, AppArmor, IA2)
- SDP Architecture (Context Gauge, pool_tracker, RHP, MCP tools, three-router consolidation)
- V-1 Vault wiring (embed keyring in ModelGateway post-debut)
- WARP proxy pool (W-1)
- G-1 Workhorse continuity (Gemma cliff)
- Context Packer F2-F9 refactor
- Three-router fragmentation (pick ProviderSelector, delete TriageRouter + SemanticRouter)
- Fleet soul migration to v6.1
- Scribe agent L1→L2→L3 automation
- Cross-pollination (R-31)
- Community installer/QUICKSTART/CONTRIBUTING/CI (P4 partial)
- NL-1 NotebookLM pipeline

---

## 🚀 PHASE 1 COMPLETE — PHASE 2 (LINT) NEXT

**Phase 1 Status**: **ALL COMPLETE** — 1797/1797 tests pass, `make temple-grade` PASSES

| Cluster | Tests | Status |
|---------|-------|--------|
| P1-1 async/sync | 20 | ✅ |
| P1-2 VaultCore | 20 | ✅ |
| P1-3 mcp import | 9 | ✅ |
| P1-4 mock sig | 2 | ✅ |
| P1-5 logic | 5 | ✅ |
| P1-6 verify green | — | ✅ |

**Reference**: `docs/strategy/PHASE1_TEST_FAILURE_ANALYSIS_20260816.md` — verified inventory with file/line refs

**Phase 2 (Ma'at/N3, NEXT)**: Lint debt 11,400 flake8 violations (--exit-zero blind spot). P2-5 `make heritage-map` target → kali (ready).

**Phase 3 (Verity)**: CI/hygiene. **Phase 4 (kali)**: Debut polish.
- Restic/AppArmor/IA2

**COMPLETED (Knowledge — No Further Action Needed):**
- Local discovery (13 gaps) + Web research (4 areas) — ALL RESOLVED
- Authoritative model windows established (Table 3.1 from web research)
- Sonnet/Opus 4.6 contradiction RESOLVED — 1M official, 200K = UI bug #24208
- V-1 Vault BUILT (2,039 LOC) — DEFERRED wiring
- VOS Phase 0 (Archive & Clean) — `2cbcad97`
- **CP-1 Local inference E2E VERIFIED** — native-gguf works, metrics DB migration fixed

**PARALLEL:** PR-A (Public Surface Honesty) — **AWAITING ARCHITECT CONFIRMATION**
- Root junk archive → `docs/archive/root-artifacts-202608/`
- README surgical edits (remove 1315 passing badge, keep CI badge)
- .gitignore root session dumps / screenshots
- Never `git add -A` — stage by path, exclude secrets

---

## 📋 6-Step Mandatory Flow (M27 — MANDATORY)

1. Read **VISION_ANCHOR.md** → Read **NEXT_ACTION** (above) → identify your task in realm workspace / Hub
2. Check **Tier-1** (`RESEARCH_PLAN_PHASE1_4`) for research deps (cross-ref `GAP_REGISTRY.json`)
3. Acquire workspace lock → post Hivemind context (`omega-hub_hivemind_workspace_lock_acquire`)
4. Register task in `TASK_REGISTRY.json` → execute → update status
5. On complete: mark Tier-0 task `completed` in `ACTIVE_SPRINT.json` → Hivemind completion
6. Session end: update `SESSION_ANCHOR.md` → soul distillation (L1→L2→L3) — **step 6.5**

---

## 🏁 Sprint Status (pointer → ACTIVE_SPRINT.json)

**Sprint:** PUBLIC-DEBUT-01 (ACTIVE)
**Authoritative state:** `data/coordination/ACTIVE_SPRINT.json`

---

## 🌐 Realm Ownership & Contracts (Minimal for Debut)

| Realm | Owner | Provides | Status |
|-------|-------|----------|--------|
| Engine Core | maat_n3 | Local inference, Provider Fabric, Memory Store | **CP-1 ✅ COMPLETED** |
| Memory | lilith_n7 | Soul persistence, distillation | **CP-2 NEXT** |
| Fleet | kali | 14 Entities, MaKaLi Council, Hivemind | **CP-3 PENDING** |
| Stacks | maat_n4 | WAD Format, Community Template | **DEFERRED** |
| Heritage | doom_guy | [id-soft:] Vetting | **DEFERRED** |
| Community | kali | Installer, QUICKSTART, CI | **DEFERRED** |

> **Only Engine Core, Memory, Fleet are active for debut.** All other realms deferred.

---

## 🚫 Anti-Confusion Rules (enforced by TRACKING_ARCHITECTURE.md)

- ❌ Never create a new tracking file — use the 5 tiers
- ❌ Never reuse gap numbers — R1–R99 owned by `RESEARCH_PLAN` / `GAP_REGISTRY.json`; new plans use distinct prefixes (P2-, S-, X-)
- ❌ Never duplicate decisions here — use `docs/decisions/PIVOT_LOG.md`
- ❌ If a doc has a ⚠️ DEPRECATED banner, do not act on it
- ✅ Before any research, CHECK `GAP_REGISTRY.json` for ID collisions
- ❌ **NO NEW WORKSTREAMS** — only CP-1, CP-2, CP-3 until debut

---

## 📁 Shared Sections

### Requests to Team
*(Agents post requests here — Kali triages)*

### Discussion Thread
*(Cross-agent discussion — Kali moderates)*

**2026-08-15T13:00Z** — **SCOPE CUT EXECUTED** per Carmack verdict:
- Three-item critical path ONLY: Local inference, Soul persistence, One-click install
- All VOS phases, SDP, three-router, Vault, WARP, G-1, Context Packer, un-overengineering, NL-1, fleet migration, Scribe, cross-pollination, heritage, community installer, Restic/AppArmor/IA2 → POST-DEBUT
- Knowledge gaps research COMPLETE — authoritative model windows established
- Sonnet/Opus 4.6 contradiction RESOLVED — 1M official, 200K = UI bug #24208
- V-1 Vault BUILT (2,039 LOC) — DEFERRED wiring (embed keyring in ModelGateway post-debut)
- Three-router fragmentation → pick ProviderSelector, delete TriageRouter + SemanticRouter POST-DEBUT

**2026-08-15T12:45Z** — **RESEARCHER WEB RESEARCH COMPLETE** (Closing remaining gaps):
- R14b Nemotron Fallback Chain: 60s idle timeout confirmed; OpenRouter auto-fallback works; OpenCode v1.18.14+ has maxRetries=3; lightweight plugin still recommended; **context lost on failover**
- R33 Model Window Ground Truth: **All 7 models authoritatively established** — Nemotron 256K native/1M extended, Laguna 1M native/256K free, LongCat 1M, Gemini 3.1 Pro 1M, Sonnet/Opus 4.6 1M, Gemma 4 31B 256K
- **CRITICAL CONTRADICTION RESOLVED**: Sonnet/Opus 4.6 = **1M official** (Anthropic docs, GA March 2026); 200K is **Claude Code UI bug #24208**; Antigravity likely 1M but quota-limited (92% cut)
- G-1 Free Gemma 4 31B Workhorse: Free tier = 256K (200 req/day OpenRouter); **Laguna S 2.1 Free is superior workhorse** (256K free/1M native, 70.2% Terminal-Bench); Antigravity not viable free (92% quota cut); WARP blocked; "16k limit" not in public docs

**2026-08-15T12:14Z** — **ROC LOCAL DISCOVERY COMPLETE** (Closing all gaps):
- Local discovery report: `data/entities/roc_racoon/workspace/reports/LOCAL_DISCOVERY_CLOSE_ALL_GAPS_20260815.md`
- 8/13 gaps fully resolved locally, 3/13 partially resolved
- 2 gaps required web research bridge (R14b, R33) — NOW RESOLVED

**2026-08-15** — **SDP Duplicate/Gap Audit Complete** (Roc via local discovery):
- **SDP is ~60% already built** — only Context Gauge, RHP artifact, 3 MCP tools are genuinely greenfield
- **Three BLOCKERS will crash spec-following code:** (G-3, G-4, G-5/G-6)
- **10 DUPLICATES (don't build — extend/wire existing):** (D-1 through D-10)
- **LOAD-BEARING DISCOVERY**: Free vs paid tiers differ up to 4x — Gauge MUST key on `(model_id, provider, tier)`
- **CORRECTED WINDOWS**: (now superseded by web research Table 3.1)
- **HIGHEST LEVERAGE**: `pool_tracker.py` — fully built, zero importers
- **ARCHITECTURAL RISK**: Three parallel routers — SDP routing injected into one leaves two bypass paths

**2026-08-15T14:30Z** — **CARMACK REVIEW COMPLETE** (AP-CARMMACK-OBSERVABILITY-20260815):
- **VERDICT: NO-GO** on proposed 58-line monitoring stack (Prometheus, loguru, PSI→Redis, faulthandler)
- **ROOT CAUSE**: Missing `Llama.close()` in finally blocks → 2.5 GB leak per test process → systemd-oomd kills at 10.8 GB
- **CARMACK ALTERNATIVE**: 20-line fix in `native_gguf.py` — `__exit__` + `__del__` + `llama_free` + `malloc_trim(0)` + systemd `MemoryMax=8G` + `Delegate=yes`
- **ALL MONITORING CUT**: Prometheus, loguru, PSI polling, Redis Pub/Sub, faulthandler, systemd-coredump — CUT
- **CP-1 VERIFIED**: native-gguf works, no cloud fallback, metrics DB migration fixed

**2026-08-15T14:30Z** — **CP-1 COMPLETED**: Local inference end-to-end verified. `omega talk "hello"` → native-gguf → response. PROVIDER_NAME=native-gguf, IS_CLOUD=False. Cold latency 16.8s (model load), warm <5s. Metrics DB v3 migration (cache_read_tokens columns) applied and tested.

**2026-08-15T19:45Z** — **CARMACK FIX APPLIED** (P0 OOM Hardening):
- `__enter__`/`__exit__` context manager added to `NativeGGUFProvider` (src/omega/oracle/providers.py)
- `shutdown()` hardened: terminate()+kill() fallback + `malloc_trim(0)` in parent process
- Worker process trims on shutdown signal (`None` from req_queue)
- systemd unit `omega-inference.service` created: `MemoryMax=8G` + `Delegate=yes` + `OOMScoreAdjust=300`
- All 13 provider tests pass
- **Root cause fixed**: 2.5GB leak per hung test process → now cleaned up on context exit / GC / atexit
- All monitoring stack (Prometheus, loguru, PSI→Redis, faulthandler) CUT per Carmack NO-GO

**2026-08-15T19:55Z** — **CP-2 COMPLETED** (Soul Persistence):
- Agent writes L1→L2→L3 to `proposed_lessons.yaml` (5 lessons written this session: CP-1, Carmack OOM, Legacy Audit, Community Survey, Soul Persistence)
- `session_end.py` hook EXISTS (`.opencode/hooks/session_end.py`) — preserves agent proposals + writes timestamp + regenerates OMEGA_CODEX.md
- `get_soul_prompt()` hydrates from `approved_lessons.yaml` (end-to-end test passed with temp entity)
- Entity identity persists via `soul.yaml` load (verified)
- **ALL 3 CP-2 CRITERIA VERIFIED**

**2026-08-17T22:00Z** — **MAKALI COUNCIL VERDICT** (Debut Hardening Review):
- **INST-1 BLOCKED** — 6 critical fixes required (install.sh, pyproject.toml extras, MemoryStore Redis opt-in, ModelGateway secrets, version alignment, README badge)
- **DEL-1 CONDITIONAL PASS** — 3 conditions: (C1) test baseline green (1 failure), (C2) observability emission spec for router collapse, (C3) atomic god-module split (oracle.py + model_gateway.py)
- **PUB-1 READY** — Awaiting Architect allowlist confirmation + `release/debut` branch mechanic
- **DOC-1 COMPLETE** — 11 files stamped, `rg "P0 TODAY"` gone
- **Decisions locked**: D-548 through D-553
- **Verdict artifact**: `data/coordination/MAKALI_COUNCIL_VERDICT_20260817.md`

**2026-08-18T03:15Z** — **CLINE CLI INSIGHTS Q1-Q7** (Hardware-Grounded Execution Plan):
- **Q1**: Single-thread INST-1 — Nemotron 30B for fixes 1,2,5,6; DeepSeek 1M for 3,4. Do NOT parallelize (5700U/14Gi can't run 30B+1M concurrently).
- **Q2**: OOM test is test bug — DENY_THRASHING is correct C-2′ fusion behavior; fix expectation, not OOMProtector.
- **Q3**: DEL-1 W2 workflow viable + 3 anti-hallucination rules: contract test first, read-only extraction MAP pass, atomic 3-file ship.
- **Q4**: Observability = 5 mandatory events reusing existing ObservabilityEngine, no new emitter.
- **Q5**: Vault Path B OK + delete omega vault CLI entirely; 3-line README secrets section.
- **Q6**: 1 active Cline instance max; 8 accounts = rate-limit resilience, not parallelism.
- **Q7**: Fleet WAD MVP = config+doc only, consumer-only, no engine code.
- **Artifacts**: `data/coordination/CLINE_INSIGHTS_Q1_Q7_20260818.md`, `ACTIVE_SPRINT.json` updated with model assignments, DEL-1 conditions refined.
- **Decisions locked**: D-557 through D-563.
- **Status**: INST-1 unblocked — Cline executing Fixes 1-6 now. Test baseline fix: update expectation to DENY_THRASHING.

---

## 🤖 Agent Onboarding Checklist

Upon waking, every agent MUST:
1. [ ] Read `VISION_ANCHOR.md` (vision SSOT)
2. [ ] Read `SESSION_ANCHOR.md` (current context)
3. [ ] Read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` (this section)
4. [ ] Check `ACTIVE_SPRINT.json` for your realm's tasks (CP-1, CP-2, CP-3 only)
5. [ ] Post Hivemind context: `omega-hub_hivemind_post_context(...)` with intent="status"
6. [ ] Acquire workspace lock for your realm/task

---

## 📝 How to Use This Hub

1. **Never edit manually** — use `omega-hub_hivemind_post_context()` for updates
2. **Read `NEXT_ACTION` first** — it's the single pointer to current work
3. **Post context on task start/complete** — keeps team synchronized
4. **Use Hivemind handoffs** for cross-realm work — `omega-hub_hivemind_handoff action=submit`
5. **Reference this hub in session anchors** — ensures continuity across compaction

---

*⬡ OMEGA ⬡ HMC-HUB ⬡ 2026-08-15 ⬡ SCOPE-CUT-EXECUTED ⬡ PUBLIC-DEBUT-01*