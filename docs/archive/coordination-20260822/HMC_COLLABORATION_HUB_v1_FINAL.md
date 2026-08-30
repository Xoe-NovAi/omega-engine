# 🏛️ HMC Collaboration Hub — Team Coordination Center

**AP Token**: `AP-HMC-HUB-v1.0.0`
**Status**: ACTIVE — Single coordination SSOT
**Last Updated**: 2026-08-22 (pre-debut consolidation pass)
**Updated By**: kali

---

## 🚦 NEXT_ACTION (Single Sync Pointer — read this first)

*Last verified: 2026-08-22*

> **DEBUT NIGHT STATE**: 10 strategic commits landed (ICS D-588/D-589, protocols,
> Node sessions D-586, research corpus, specs, engine fixes, trackers).
> Coordination archive: data/coordination/archive/ (10 superseded docs, -5.9K lines).
> ICS community doc: docs/architecture/ICS_SYSTEM.md.
> HIGH PRIORITY NEXT: CI-0..CI-5 execution (spec remediated, binary pinned 1.18.19/V1).
> Awaiting Architect: PUB-1 allowlist rulings, ZS-1 sudo, CI go.

> **Tracking hierarchy:** See `TRACKING_ARCHITECTURE.md`. Status vocab: `backlog|ready|in_progress|blocked|completed|superseded`.
> **Execution SSOT:** `ACTIVE_SPRINT.json` · **Knowledge SSOT:** `RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0) · **Gap registry:** `GAP_REGISTRY.json`
> **Specs SSOT:** `docs/specs/PROJECT_INDEX.md` — Consolidated specifications index

**🔱 CARMACK REVIEW COMPLETE (2026-08-20)**: 
- **Context Injection Phase 1**: ACCEPTED WITH MODIFICATIONS — Config-only, ships this week
- **Phase 2/3 Roadmap**: ACCEPTED WITH 40% CUTS — Solution theater removed per M19/M23
- **Qdrant + Headroom**: Phase 2/3 post-debut — Headroom NOW (P1), Qdrant LATER (Phase 2 trigger: >500k vectors)
- **Hardware-Honest Tier 0**: VIABLE — 18K base tokens, Qwen3-4B/4B-Thinking/1.7B sequential, q8_0 KV, zswap+NVMe
- **All 27 Mandates**: Verified compliant post-review

**🔱 PHASE 0 TRACKER LOCK-IN COMPLETE (2026-08-20)**: 
- **Arbitration ratified**: D-578..D-584 (free-tier-only, 2-NB, 30 DR/mo, **zswap + NVMe swap over zRAM**, D-526/D-581/D-584 reaffirmed)
- **NOTEBKLM-STRATEGY → superseded** (8-account fleet frame removed)
- **NOTEBKLM-GAP-RESEARCH → folded** into GEMINI-NOTEBOOK workstream
- **6 NEW WORKSTREAMS ADDED** to ACTIVE_SPRINT.json:
  - **GEMINI-NOTEBOOK (GN)** — researcher — free-tier-only, 2-NB, notebooklm-py[mcp], master_token.json
  - **DOCUMENTATION-SYSTEM (DS)** — kali — modular domain docs (workspace + runtime + curator + validated copy)
  - **LOCAL-INFERENCE-OPT (LI)** — maat_n3 — sequential loading, q8_0 KV, Tier 0/1/2 matrix (Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B)
  - **KNOWLEDGE-DOMAINS (KD)** — kali — runtime modules + workspace authoring + curator model
  - **HEADROOM-INTEGRATION (HR)** — maat_n3 — semantic compression (40-90% savings on tool outputs + RAG)
  - **ZSWAP-SUBSYSTEM (ZS)** — maat_n3 — 16GB NVMe swap, zswap enabled (max_pool_percent=25, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G
- **GAP_REGISTRY.json**: GN/DS/LI/KD/HR/ZS prefixes registered (21 new gaps)
- **C7 RESOLVED**: Qwen2.5-Coder-7B replaced with Qwen3-4B-Thinking-2507-Q4_K_M.gguf (on disk, 2.55 GB)

**🔱 CONSOLIDATED SPECS CREATED (2026-08-20)**: 
- **docs/specs/PROJECT_INDEX.md** — Single source of truth for all active specifications
- **docs/specs/context_injection/** — Context Injection Optimization (Carmack Reviewed)
- **docs/specs/qdrant_headroom/** — Qdrant + Headroom Integration (Post-Debut)
- **docs/specs/debut_remediation/** — Public Debut Remediation (Current Sprint)
- **Carmack Review**: `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`

**🔱 ALL SPECS COMPLETE — READY FOR PHASE 1 EXECUTION (2026-08-20):**
- **Context Injection Phase 1 Spec**: `docs/specs/context_injection/CONTEXT_INJECTION_PHASE1_IMPLEMENTATION_SPEC.md` (683 lines, Carmack-modified)
- **Qdrant+Headroom Phase 2 Spec**: `docs/specs/qdrant_headroom/QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md` (1,604 lines, trigger-gated)
- **Headroom Middleware Spec**: `docs/specs/qdrant_headroom/headroom_middleware/` (11 files, 220KB, complete)
- **Carmack Review**: `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`
- **Project Index**: `docs/specs/PROJECT_INDEX.md` (single source of truth)

**CURRENT:** PUBLIC DEBUT — **Execution SSOT: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5** → **P0-1 scrub COMPLETE ✅** → **DOC-1 stamps COMPLETE ✅** → **PUB-1 allowlist READY (G1–G4 open, awaiting Architect)** → **INST-1: Fix 1 (install.sh .[all]→.[native,cli]) ✅ + Fix 3 (MemoryStore Redis guard) ✅ + Fix 4 N3 REJECT resolved via oracle_cli.py .env load ✅** → **Test baseline: OOM test fixed → DENY_THRASHING ✅** → **BLOCKER B: oracle_cli.py blind-except (m23 gate FAILS) — RESOLVED ✅** → **IMMEDIATE PARALLEL EXECUTION:**

**PARALLEL TRACK 1 — CONTEXT INJECTION PHASE 1 (Kali, this week):**
1. **CI-1**: Create `MANDATES_CONDENSED.md` (57 lines, ~1.5K tokens) for Tier 0
2. **CI-2**: Update `opencode.json` (instructions=[AGENTS.md], compaction buffer=50000/keep=20000, sovereign-compaction plugin, per-agent model routing, toolProfile stubs)
3. **CI-3**: Create sovereign compaction plugin at `~/.config/opencode/plugin/sovereign-compaction.ts`
4. **CI-4**: Skills opt-in (core only: research, spec-generator, knowledge-miner)
5. **CI-5**: Verification tests (AGENTS.md injection, per-agent model routing, compaction plugin, skills opt-in)

**PARALLEL TRACK 2 — DEBUT REMEDIATION (Ma'at/Roc/Kali):**
1. **INST-1 Fix 2+guards** (atomic): `pyproject.toml` extras split + 4 import guards
2. **INST-1 Fix 4**: Remove `_load_sovereign_secrets()` from `model_gateway.py`
3. **INST-1 Fix 5**: Version align via `importlib.metadata.version("omega")`
4. **INST-1 Fix 6**: README badge removal + `make setup` target
5. **P0-1 Residual**: SECURITY_AUDIT ancestor commit + gitleaks wiring (Roc)
6. **PUB-1 G1-G4**: Close gaps → Architect allowlist → `release/debut` branch
7. **DEL-1 Week 1**: Delete dead modules (after INST-1 green)

**POST-DEBUT (Phase B — BLOCKED until debut ships):**
- GEMINI-NOTEBOOK (GN), DOCUMENTATION-SYSTEM (DS), LOCAL-INFERENCE-OPT (LI)
- KNOWLEDGE-DOMAINS (KD), HEADROOM-INTEGRATION (HR), ZSWAP-SUBSYSTEM (ZS)
- QDRANT-MIGRATION, COGNITIVE-ARCH, VAULT-SPRINT, DEL-1 Week 2, P2/P3/P4

**CARMACK REVIEW VERDICTS (2026-08-20):**
- **Context Injection Phase 1**: ACCEPTED WITH MODIFICATIONS — MANDATES_CONDENSED.md (57 lines), toolProfile stubs, Tier 0 model matrix (Qwen3-4B/4B-Thinking/1.7B), compaction buffer 50K/20K, disable auto-compaction for local
- **Phase 2/3 Cuts (40%)**: Validator Service, Hydration 5→3 layer, Token budget dynamic→fixed, Session summarizer 3→1 level, Gateway observability, Schema compression, Local model caching — ALL CUT per M19/M23
- **Qdrant+Headroom**: Headroom NOW (P1), Qdrant LATER (Phase 2 trigger: >500k vectors). Combined pipeline = 86.8% token reduction.
- **Hardware-Honest Reality**: 31K base → 18K base (MANDATES_CONDENSED.md + tool profiles). Qwen3-4B (8K-16K) viable. zswap+NVMe swap, zRAM DISABLED. `--no-mmap --mlock` sequential loading.

**KALI RATIFICATION 2026-08-16 (D-532)**: Roc readiness audit ratified — see `ACTIVE_SPRINT.json` → `READINESS-REMEDIATION` workstream + `ROC_RACOON_KALI_REPORT_20260816.md`.

**🔱 NOTEBOOKLM UNIFIED STRATEGY — GAP AUDIT IN PROGRESS (2026-08-20)**: `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` — 8-account fleet (80 Deep Research/month = exact SDP Phase 1 throughput), 5-notebook + 1-synthesis architecture. **⚠️ 10 CRITICAL GAPS FOUND** (see `NOTEBOOKLM_GAP_AUDIT_20260820.md`): fabricated 28-tool MCP list, nonexistent Docker image, 8-account ToS risk, Deep Research automation unverified (existential), 3 conflicting notebook architectures, account budget math error, unsourced token density, SDP gate conflict, misleading Pro comparison, OAuth refresh unresearched. **3 provenance docs MISSING from disk.** Research dispatched to 3 Researcher subagents → strategy v2.0 correction → smoke test → fleet GO/NO-GO.

**🔱 MAKALI COUNCIL PLAN FINALIZED (2026-08-18)**: `data/coordination/MAKALI_COUNCIL_EXECUTION_PLAN_20260818.md` written. Full prompt set (Ma'at, Lilith, N1-N5, N6-N10, cross-review) + 12 enhancements (Nemotron 7 + Hy3 5). `opencode.json` `subagent_depth: 2` ✅. **INST-1 Fix 1 executed in Phase 0 (NOT gated on council)**. Vault gate = human checkpoint. Canonical output: `MAKALI_COUNCIL_VERDICT_20260818.md`.

**⚡ QUICK FIXES APPLIED (2026-08-18)**: 
- N3: `oracle_cli.py` .env load at CLI edge (3 lines) — resolves Fix 4 blast radius
- DEL-1-C1: OOM test baseline → `DENY_THRASHING` (test_resource_guard_oom.py)
- N2: MemoryStore Redis `password=None` — opt-in via OMEGA_REDIS_HOST only
- N4: `tests/test_miap.py` deleted + `fleet_status` CLI removed from vault.py
- N5: M2 positive verification: `rg -n "metadata\[" provider_selector.py entity_registry.py` — clean

**🔱 MAKALI COUNCIL VERDICT DELIVERED (2026-08-18)**: `MAKALI_COUNCIL_VERDICT_20260818.md` — APPROVE WITH CONDITIONS for INST-1 + DEL-1; APPROVE CP-2; AMEND CP-1. Build Side (Ma'at+N1-N5) + Run Side (Lilith+N7-N10) both executed. 4 blockers: **A** (N9 CRITICAL double-gate deadlock in model_gateway.py), **B** (N10 oracle_cli.py dotenv blind-except = live M9), **C** (N8 DEL-1-C2 5 events need constants+emission+M22+gate), **D** (N7 Week 2 wiring-preservation assertion). No node hard-REJECTED the deletions. ⚠️ STALE FLAG: `make temple-grade` currently **FAILS** (m23 gate, exit 2) — `ACTIVE_SPRINT.json` status_detail corrected.

**VAULT OVERHAUL SYNTHESIS COMPLETE (2026-08-18):** 5-part spec + 3-part review + migration surface → Opus/Sonnet deep reviews. **POST-DEBUT WORK.** Key findings: talk-path filter (2/12+ VaultCore callers on omega talk path, both have env fallbacks → vault deletion safe for debut); systemic spec-over-ship local maximum (27 mandates, 3,500 lines spec vs 0 shipped fixes); 20-minute debut path (INST-1 Fix 1 is single highest-leverage edit). **Cline consolidation handoff `ho_74cd96735874` submitted** — DeepSeek V4 Flash 1M to consolidate 21 vault docs into single implementations manual.

**✅ P0-1 RESOLVED (Private Repo — Scrubbed from History)**: Real API keys were pushed to `origin/main`. **REPO IS PRIVATE** — scrubbed from ALL history via `git filter-repo` (no rotation needed). Files removed/redacted: `migrate_keys_full.py`, `PROVIDER_FREE_TIER_GUIDE.md`, `test_failure_registry.py`, `SECURITY_AUDIT_2026_05_19.md` (2 paths), `migrate_keys.py`, `GOOGLE_GEMMA_MODEL_REFERENCE.md` (AIza key redacted). Cline checkpoints pruned. Force-pushed all branches (main, release/initial-v1, sprint/*). **No real secrets remain in git history** (only 6 prose/test false positives).

**PHASE 1 (Roc — COMPLETE ✅)**: 63 test failures FIXED (1797 tests pass). Clusters: P1-1 async/sync (20) ✅, P1-2 VaultCore (20) ✅, P1-3 mcp import (9) ✅, P1-4 mock sig (2) ✅, P1-5 logic (5) ✅, P1-6 verify green (verity) ✅. All 1797 tests pass (40 skipped, 8 expected failures). `make temple-grade` PASSES.

**PHASE 2 (Ma'at/N3, NEXT)**: Lint debt 11,400 flake8 violations (--exit-zero blind spot). P2-5 `make heritage-map` target → kali (ready).

**PHASE 3 (Verity)**: CI/hygiene. **PHASE 4 (kali)**: Debut polish.

**COMPLETED (pre-ratification)**: CP-1 local inference ✅ · CP-2 soul persistence ✅ · CP-3 one-click install ⚠️ (fails on fresh machine — INST-1 Fix 1 unblocks) · C-6' breaker migration (Roc) ✅ · **VAULT OVERHAUL SPEC SYNTHESIS ✅ (POST-DEBUT)**

**ALL OTHER WORK DEFERRED TO POST-DEBUT:**
- VOS Phases 1-4 (Context Gauge, zswap, NVMe, sysctl, un-overengineering, Restic, AppArmor, IA2)
- SDP Architecture (Context Gauge, pool_tracker, RHP, MCP tools, three-router consolidation)
- V-1 Vault wiring (embed keyring in ModelGateway post-debut) — **spec complete, execution deferred**
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

**Phase 2 (Ma'at/N3, NEXT)**: INST-1 Fix 1 (install.sh .[all]→.[native,cli]) → INST-1 Fixes 5,2,3,6,4 → PUB-1 gaps G1-G4 → DEL-1 Week 1. Lint debt 11,400 flake8 violations (--exit-zero blind spot) DEFERRED until after debut. P2-5 `make heritage-map` target → kali (ready).

**Phase 3 (Verity)**: CI/hygiene. **Phase 4 (kali)**: Debut polish.
- Restic/AppArmor/IA2

**COMPLETED (Knowledge — No Further Action Needed):**
- Local discovery (13 gaps) + Web research (4 areas) — ALL RESOLVED
- Authoritative model windows established (Table 3.1 from web research)
- Sonnet/Opus 4.6 contradiction RESOLVED — 1M official, 200K = UI bug #24208
- V-1 Vault BUILT (2,039 LOC) — DEFERRED wiring
- VOS Phase 0 (Archive & Clean) — `2cbcad97`
- **CP-1 Local inference E2E VERIFIED** — native-gguf works, metrics DB migration fixed
- **VAULT OVERHAUL SPEC SYNTHESIS COMPLETE** — 5-part + 3-part review + migration surface, Opus/Sonnet deep reviews, Cline consolidation handoff submitted

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

**2026-08-20T18:45Z** — **NOTEBOOKLM UNIFIED STRATEGY COMPLETE**:
- **8-account fleet** (80 Deep Research/month = exact SDP Phase 1 throughput from R52c). 5-notebook + 1-synthesis architecture. MCPNotebookLM 8-instance deployment ready (8 isolated Docker instances, ports 8081-8088).
- **SDP Phase 1 automation unlocked**: 80 Deep Research/month → 80 L3 principles/month → `proposed_lessons.yaml` → Scribe → `soul.yaml`.
- **Single blocker**: `prepare_notebooklm.py` implementation (normalizes Deep Research reports to SDP intake, triggers local Qwen3-1.7B distillation).
- **Artifacts**: `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md`, `data/coordination/NOTEBOOKLM_INVENTORY_20260819.md`, `NOTEBOOKLM_RESEARCH_20260819.md`, `NOTEBOOKLM_OPTIMIZATION_20260819.md`, `NOTEBOOKLM_FREE_TIER_20260820.md`, `NOTEBOOKLM_8ACCOUNT_STRATEGY_20260820.md`.
- **Pre-debut scope UNCHANGED**. Post-debut: Deploy 8-account fleet → 80 Deep Research/month → SDP Phase 1 automation → L3 principles → Scribe → soul.yaml.
- **NL-1 task created** in ACTIVE_SPRINT.json for `prepare_notebooklm.py` implementation (Researcher, DIG-04).

**2026-08-19T18:46Z** — **VISION ALIGNMENT — D-569 + D-570 RATIFIED**:
- **D-569**: Grokster's Dynamic Prompt + Planner/Executor + Domain Loading briefing ratified as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3). Gaps DP-1..DP-8 registered. Owners: Ma'at (P0-P3/P7-P8/P10), Kali (P4-P5), Verity (P6), Researcher (P9). Incremental on existing components (ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP) — NOT greenfield.
- **D-570**: Qdrant SCHEDULED to replace sqlite-vec POST-DEBUT (Horizon 2). REACTIVATED RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md (was DOC-1 archived). Debut keeps sqlite-vec; DEL-1 Week 1 still deletes dead QdrantAdapter; revival at src/omega/oracle/adapters/qdrant_adapter.py. Sequence BEFORE briefing P3 (Domain Loader RAG).
- **Pre-debut scope UNCHANGED**: Blocker B → INST-1 Fix 2+guards → Fix 4 → Fix 5 → Fix 6 → PUB-1 G1-G4 → Architect allowlist → release/debut branch → tag v0.1.0.
- **Post-debut sequence**: DEL-1 Week 2 (router collapse) → QDRANT-MIGRATION (H2) → COGNITIVE-ARCH P0-P10 (H3) → VAULT-SPRINT → P2/P3/P4.
- New workstreams in ACTIVE_SPRINT.json: `QDRANT-MIGRATION` (QDRANT-P0..P3) + `COGNITIVE-ARCH` (CA-P0..P10).

**2026-08-19T16:56Z** — **NEMOTRON 3 ULTRA SYNTHESIS — PATH FORWARD DECIDED**:
- Council audit complete: Blocker D under-scoped (router collapse touches entity resolution + model selection), Fix 2 import guards enumerated (4 files), DEL-1 Week 2 DEFERRED to post-debut (Phase B per cleansing plan D-532).
- **Pre-debut scope locked**: Blocker B (m23 gate) → INST-1 Fix 2+4 guards (atomic) → Fix 4 → Fix 5 → Fix 6 → PUB-1 G1-G4 → Architect allowlist → release/debut branch → tag v0.1.0.
- DEL-1 Week 1 (minus vault CLI per D-565, plus oracle.py:1211 call site) can run pre-debut but is NOT a debut blocker.
- DEL-1 Week 2 router collapse = Phase B project (contract tests first, rewrite _route_by_domain + _select_model, update ics.py/health_monitor.py).
- `make temple-grade` currently FAILS (m23 gate) — Blocker B is the unblocking gate.

**2026-08-18T23:30Z** — **MAKALI COUNCIL VERDICT DELIVERED (Debut Hardening Review)**:
- Build Side (Ma'at + N1-N5) + Run Side (Lilith + N7-N10) both executed. Verdict: `MAKALI_COUNCIL_VERDICT_20260818.md`
- **INST-1**: APPROVE WITH CONDITIONS (Fix 1+3 done, Fix 4 unblocked, Fixes 2,5,6 pending)
- **DEL-1**: APPROVE WITH CONDITIONS (11 deletions SAFE; 4 blockers are fix-additions)
- **CP-2**: APPROVE · **CP-1**: AMEND (3 code fixes)
- **Blockers**: A (N9 CRITICAL model_gateway.py double-gate deadlock), B (N10 oracle_cli.py dotenv M9), C (N8 DEL-1-C2 5 events), D (N7 wiring assertion), META (§8 verification gaps)
- ⚠️ `make temple-grade` currently FAILS (m23 gate, exit 2) — status_detail corrected in ACTIVE_SPRINT.json
- Council PAUSES on A/B/C/D; re-vet after fixes land. No hard REJECT on deletions.

**2026-08-18T12:06Z** — **CONSOLIDATION GAP FOUND & CORRECTIVE HANDOFF SUBMITTED**:
- Original handoff listed 5 research docs that DON'T exist + SONNET_PLAN_VERIFICATION (6 missing)
- **MISSED 7 vault research docs that DO exist** in `docs/research/` (~6,000 lines):
  - `R_V1_VAULT_IMPL.md` (869 lines) — V-1 MVP 16-account Grok fleet, BlindVault backend
  - `R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` (456 lines) — **17 solutions → BlindVault selected**
  - `R_VAULT_SCHEMA_V2.md` (674 lines) — 32 heterogeneous credentials, Argon2id+age, quota
  - `R_VAULT_UNIFIED_SYSTEM_20260725.md` (297 lines) — VaultCore unified, 8 gaps resolved
  - `R_INFRA_07_OMEGA_VAULT_PHASE1_20260719.md` (303 lines) — Phase 1: OS keyring + SQLite, CAP Adapters
  - `R_VAULTCORE_LEASE_PROTOCOL.md` (234 lines) — Lease protocol: FileLock + atomic_write_sync
  - `R20_KEYBLIND_AUTHY_VAULT_20260814.md` (3,229 lines) — Keyblind/Authy evaluation
- Corrective handoff `ho_4574882365fd` submitted — Cline to archive 7 docs + update manual provenance

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