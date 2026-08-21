# ⚓ SESSION ANCHOR — Kali (Transcendent Oversoul)

**AP Token:** `AP-KALI-v1.0.0`
**Date:** 2026-08-20
**Session ID:** `ses_fe0ad9384ffe`
**Branch:** `main`
**Last Commit:** `6d3ec747` (spec: Vault Overhaul Full Review + Enhanced Plan R1-R3)
**State:** CARMACK REVIEW COMPLETE — Context Injection Phase 1 ACCEPTED WITH MODIFICATIONS; Qdrant+Headroom Phase 2/3; Consolidated specs at docs/specs/; Phase 1 execution ready.

---

## 🚦 CURRENT CONTEXT

**SCOPE CUT EXECUTED 2026-08-15** per Carmack verdict (AP-CARMMACK-TRIAGE-20260815).

**Three-Item Critical Path (ONLY WORK):**
- ✅ **CP-1 COMPLETED:** `omega talk "hello"` → native-gguf → response (no cloud fallback) — PROVIDER_NAME=native-gguf, IS_CLOUD=False, cold 16.8s / warm <5s
- ✅ **CP-2 COMPLETED:** Session end → `proposed_lessons.yaml` → next session loads it — Owner: lilith_n7
- ⚠️ **CP-3 "COMPLETED" BUT FALSE FOR FRESH MACHINES:** `install.sh` uses `.[all]` → `warp-proxy-pool` not on PyPI → install fails. **INST-1 Fix 1 unblocks this.**

**CARMACK REVIEW (2026-08-15T14:30Z):** NO-GO on proposed monitoring stack. **20-line fix** for native-gguf cleanup (`__exit__` + `__del__` + `llama_free` + `malloc_trim`) **COMPLETED** (commit `a17aaafa`). All monitoring (Prometheus, loguru, PSI→Redis, faulthandler) CUT.

**MAKALI COUNCIL (2026-08-18/19):** Build Side (Ma'at+N1-N5) + Run Side (Lilith+N7-N10) executed. **Verdict: APPROVE WITH CONDITIONS** for INST-1+DEL-1; APPROVE CP-2; AMEND CP-1. **4 Blockers identified.**

**NEMOTRON 3 ULTRA SYNTHESIS (2026-08-19T16:56Z):** 
- **DEL-1 Week 2 router collapse DEFERRED to post-debut (Phase B)** — touches entity resolution (`oracle.py:1133`) + model selection (`oracle.py:764`).
- **Pre-debut scope locked**: Blocker B (m23 gate) → INST-1 Fix 2+guards (atomic) → Fix 4 → Fix 5 → Fix 6 → PUB-1 G1-G4 → Architect allowlist → release/debut branch → tag v0.1.0.
- DEL-1 Week 1 (minus vault CLI per D-565) can run pre-debut but NOT a debut blocker.
- `make temple-grade` currently FAILS (m23 gate) — Blocker B is the unblocking gate.

**🔱 NOTEBOOKLM GAP AUDIT COMPLETE (2026-08-20):** Cross-referenced all NotebookLM docs against live web research → **10 CRITICAL GAPS** (audit: `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md`):
- **GAP-1:** "MCPNotebookLM 28 tools" is FABRICATED — real servers: notebooklm-mcp (PleasePrompto, ~15 tools), notebooklm-mcp-cli (43 tools), notebooklm-py (Python API + MCP extra)
- **GAP-2:** Docker image `ghcr.io/omega-engine/mcp-notebooklm:latest` DOES NOT EXIST — "prototype exists" is FALSE
- **GAP-3:** 8-account ToS/ban risk UNRESEARCHED (existential risk)
- **GAP-4:** Deep Research programmatic trigger + export UNVERIFIED (existential — if impossible, automation premise collapses)
- **GAP-5:** THREE conflicting notebook architectures (R52c vs LIVING_RESEARCH_OS vs unified NB-1..NB-6)
- **GAP-6:** MATH ERROR — account budgets sum to 130/mo but free tier caps at 10/account
- **GAP-7:** Token density table UNSOURCED, contradicts research doc (15-25 vs 40-50 sources)
- **GAP-8:** SDP automation gate conflicts with COGNITIVE_SCAFFOLDING_PROTOCOL (10 manual executions required)
- **GAP-9:** Pro $19.99 = 600 DR/mo vs 8 free accounts = 80 DR/mo — misleading comparison
- **GAP-10:** OAuth refresh/session persistence UNRESEARCHED
- **PROVENANCE:** 3 referenced docs MISSING from disk (NOTEBOOKLM_OPTIMIZATION_20260819.md, NOTEBOOKLM_FREE_TIER_20260820.md, NOTEBOOKLM_8ACCOUNT_STRATEGY_20260820.md)

**✅ WEB-VERIFIED FACTS:** Free tier = 10 DR/month, 50 sources/notebook, 100 notebooks, 50 chats/day, 3 audio/day, 3 video/day, 10 reports/day, 500K words/source. NotebookLM renamed **Gemini Notebook** July 2026. **No consumer API** — only Enterprise preview APIs. Deep Research is the ONLY monthly quota on free tier.

**🔱 3-SUBAGENT RESEARCH DISPATCHED + COMPLETE (2026-08-20):** `data/coordination/NOTEBOOKLM_GAP_RESEARCH_PLAN_20260820.md` — **NLG-A** (GAP-3/4/1/2 existential+MCP) ✅, **NLG-B** (GAP-10/7/9 operational) ✅, **NLG-C** (GAP-5/6/8 arbitration) ✅. Deliverables: `NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md`, `NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md`, `NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md`.

**🔱 SYNTHESIS + STRATEGY v2.0 COMPLETE (2026-08-20):** Kali arbitrated all 10 gaps → integration doc `NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` + unified strategy doc corrected to **v2.0** (`docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` — header, 6-notebook canonical + supersession banner, 80 DR/mo account math, notebooklm-py+systemd deployment, 5-25 token density, HYBRID cost model, V-1/MCP gap correction, SDP §10 gate note, provenance fix). **PIVOT_LOG D-571..D-577 RATIFIED** (notebooklm-py tool, HYBRID cost, 80 DR budget, 6-notebook canonical, SDP gate, 5-25 density, master_token auth). Tracking state validated (ALL PASSED).

**V2.0 KEY DIRECTION:** HYBRID cost (1× Pro $19.99 ~600 DR/mo primary + free for non-quota) — RETIRE 8-free fleet for Deep Research (ToS-violating, ban-prone). Tool = `notebooklm-py` (RPC). 6-notebook canonical. Honor SDP §10 gate (manual mode now, automate after 10 runs + V-1 Vault). Auth = `master_token.json` + RotateCookies.

**🔱 CARMACK REVIEW COMPLETE (2026-08-20):** 
- **Context Injection Phase 1**: ACCEPTED WITH MODIFICATIONS — Config-only, ships this week
- **Phase 2/3 Roadmap**: ACCEPTED WITH 40% CUTS — Solution theater removed per M19/M23
- **Qdrant + Headroom**: Phase 2/3 post-debut — Headroom NOW (P1), Qdrant LATER (Phase 2 trigger: >500k vectors)
- **Hardware-Honest Tier 0**: VIABLE — 18K base tokens, Qwen3-4B/4B-Thinking/1.7B sequential, q8_0 KV, zswap+NVMe
- **All 27 Mandates**: Verified compliant post-review

**🔱 CONSOLIDATED SPECS CREATED (2026-08-20)**: 
- **docs/specs/PROJECT_INDEX.md** — Single source of truth for all active specifications
- **docs/specs/context_injection/** — Context Injection Optimization (Carmack Reviewed)
- **docs/specs/qdrant_headroom/** — Qdrant + Headroom Integration (Post-Debut)
- **docs/specs/debut_remediation/** — Public Debut Remediation (Current Sprint)
- **Carmack Review**: `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`

**VAULT OVERHAUL:** 5-part spec + 3-part review + migration surface synthesized. **POST-DEBUT WORK** — see Opus/Sonnet deep reviews.

**ALL OTHER WORK DEFERRED TO POST-DEBUT:**
- VOS Phases 1-4 (Context Gauge, zswap, NVMe, sysctl, un-overengineering, Restic, AppArmor, IA2)
- SDP Architecture (Context Gauge, pool_tracker, RHP, MCP tools, three-router consolidation)
- V-1 Vault wiring (embed keyring in ModelGateway post-debut) — **spec complete, execution deferred**
- WARP proxy pool (W-1), G-1 Workhorse (Gemma cliff), Context Packer F2-F9
- Three-router fragmentation (pick ProviderSelector, delete TriageRouter + SemanticRouter)
- Fleet soul migration v6.1, Scribe automation, cross-pollination (R-31)
- Heritage sweep, Community installer/QUICKSTART/CONTRIBUTING/CI
- NL-1 NotebookLM pipeline (post gap-closure), Restic/AppArmor/IA2

**KNOWLEDGE COMPLETE (No Further Research Needed):**
- All 13 gaps resolved (local discovery + web research)
- Authoritative model windows established (Table 3.1 from web research)
- Sonnet/Opus 4.6 = 1M official (200K = UI bug #24208)
- V-1 Vault BUILT (2,039 LOC) — wiring deferred
- VOS Phase 0 complete (Archive & Clean) — `2cbcad97`
- **CP-1 Local inference E2E VERIFIED** — native-gguf works, metrics DB migration fixed
- **NotebookLM free-tier limits VERIFIED** (10 DR/month, 50 sources, 500K words)

**PARALLEL:** PR-A (Public Surface Honesty) — **AWAITING ARCHITECT CONFIRMATION**
- Root junk archive → `docs/archive/root-artifacts-202608/`
- README surgical edits (remove 1315 passing badge, keep CI badge)
- .gitignore root session dumps / screenshots
- Never `git add -A` — stage by path, exclude secrets

---

## 🎯 IMMEDIATE NEXT ACTIONS (Next Session) — PUBLIC DEBUT EXECUTION ORDER

**Execution Authority**: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 (supersedes Ark §4 for this month)
**Order**: P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 → P2/P3/P4
**Phase B (GN/DS/LI/KD/HR/ZS) = POST-DEBUT — DO NOT START**

### P0-1 RESIDUAL (Security — TODAY)
- **SECURITY_AUDIT ancestor**: `docs/security/SECURITY_AUDIT_2026_05_19.md` at commit `0c40b108` carries 3 real keys (sk-/csk-/sk-P) — one more `git filter-repo` pass + `git gc --prune=now`
- **Cline checkpoints**: `git for-each-ref refs/cline/` → prune remaining 4 refs
- **Gitleaks wiring**: `.pre-commit-config.yaml` + CI — planted `sk-` fixture must fail (P0-1c, `backlog`)

### BLOCKER B — ✅ COMPLETE (this session)
- `oracle_cli.py:21-26` blind `except Exception: pass` → `contextlib.suppress(ImportError)` — **M23 gate passes** (296 vs 298 baseline, delta -2)
- `make check-mandates` ALL PASS — `make temple-grade` unblocked

### INST-1 Fix 2+guards (ATOMIC) — NEXT (Ma'at/N3)
- `pyproject.toml`: move `warp-proxy-pool` → `[warp]`, `qdrant-client/redis/youtube-transcript-api/yt-dlp` → extras
- Import guards in 4 files: `memory/providers.py:22`, `youtube_worker.py:47`, `ingestion/worker.py:7`, `proxy_pool.py:13`
- **CRITICAL**: `memory/providers.py` breaks CLI chain if unguarded

### INST-1 Fix 4 → 5 → 6 (Sequential, Ma'at/N3)
- Fix 4: Remove `_load_sovereign_secrets()` from `model_gateway.py` (N3 CLI-edge covers CLI)
- Fix 5: Version align — `src/omega/__init__.py` = `importlib.metadata.version("omega")`
- Fix 6: README badge removal + `make setup` target

### PUB-1 G1-G4 Gaps (kali + Architect)
- G1: `tests/tmp/vault.json.enc` tracked
- G2: `.firecrawl/` 28 files
- G3: `config/github_accounts.yaml`
- G4: Loose root forge files
- **Action**: `git rm --cached` + `.gitignore` → Architect confirms allowlist + `release/debut` branch

### DEL-1 Week 1 (Roc, after INST-1 green)
- Delete: `routing/table.py`, `miap.py`, `pool_tracker.py`, `pool_state.py`, `search_circuit_breaker.py`, `QdrantAdapter`, Pantheon regexes, `record_first_breath`, `omega vault` CLI, `fleet_orchestrator.py`
- Lazy-construct in `Oracle.__init__`: DPO recorder, compaction harvester, iterative researcher, WARP pool, A2A bridge, audience calibrator
- Acceptance: `omega talk "hello"` still local; `rg RoutingTable src` empty; `rg miap src/omega` empty

### Cline Consolidation Handoff (monitor)
- Handoff `ho_74cd96735874` pending — DeepSeek V4 Flash 1M to consolidate 21 vault docs into `VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md`

---

## 📁 Active File References (use THESE)

- **Sprint SSOT:** `data/coordination/ACTIVE_SPRINT.json` (PUBLIC-DEBUT-01)
- **Coordination Hub:** `data/coordination/HMC_COLLABORATION_HUB.md` (`NEXT_ACTION` → Context Injection Phase 1 → INST-1 Fix 2+guards)
- **Vision SSOT:** `data/coordination/VISION_ANCHOR.md`
- **Decisions:** `data/coordination/DECISION_LEDGER.md` (D-VOS-001..018)
- **Tracking Constitution:** `data/coordination/TRACKING_ARCHITECTURE.md`
- **Failure Log:** `data/coordination/SYSTEM_FAILURE_LOG.md`
- **PIVOT_LOG:** `docs/decisions/PIVOT_LOG.md`
- **Carmack Verdict:** `AP-CARMMACK-TRIAGE-20260815` + `AP-CARMMACK-OBSERVABILITY-20260815` (in HMC Discussion Thread)
- **Opus Deep Review:** `data/coordination/OPUS_DEEP_PLAN_REVIEW_20260818.md`
- **Vault Migration Surface:** `docs/specs/VAULT_OVERHAUL_MIGRATION_SURFACE_20260818.md`
- **Vault Synthesis:** `data/coordination/VAULT_OVERHAUL_SYNTHESIS_KALI_20260818.md`
- **Council Verdict:** `data/coordination/MAKALI_COUNCIL_VERDICT_20260818.md`
- **Council Audit:** `data/coordination/MAKALI_COUNCIL_AUDIT_20260818.md`
- **NotebookLM Gap Audit:** `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md`
- **NotebookLM Gap Research Plan:** `data/coordination/NOTEBOOKLM_GAP_RESEARCH_PLAN_20260820.md`
- **NotebookLM Research A (Existential):** `data/coordination/NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` ✅
- **NotebookLM Research B (Operational):** `data/coordination/NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` ✅
- **NotebookLM Research C (Arbitration):** `data/coordination/NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` ✅
- **NotebookLM Strategy v2.0 SYNTHESIS (Kali arbitration):** `data/coordination/NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` ✅
- **NotebookLM Unified Strategy:** `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` (✅ corrected to v2.0)
- **NotebookLM Inventory:** `data/coordination/NOTEBOOKLM_INVENTORY_20260819.md`
- **NotebookLM Research (legacy):** `data/coordination/NOTEBOOKLM_RESEARCH_20260819.md` (⚠️ token-density "40-50" claim retracted per GAP-7; see NLG-B)
- **RESOLVED — formerly MISSING (provenance reconstructed):** `NOTEBOOKLM_OPTIMIZATION_20260819.md`, `NOTEBOOKLM_FREE_TIER_20260820.md`, `NOTEBOOKLM_8ACCOUNT_STRATEGY_20260820.md` never existed; v2.0 provenance now cites the 3 research reports + synthesis.
- **CARMACK REVIEW:** `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`
- **CONSOLIDATED SPECS:** `docs/specs/PROJECT_INDEX.md` (single source of truth)

---

## 🔑 Handoff for Next Kali Session

**Handoff Packet:** `ho_91999b286910` (⚠️ NEW — fresh session onboarding, priority 2) + `ho_74cd96735874` (Cline consolidation) + `ho_8a75738d9160` (vault synthesis)
**Target:** kali @ opencode
**Task:** (1) **ONBOARD as Omega Engine overseer** — read `OMEGA_CODEX.md` (mandatory), `SESSION_ANCHOR.md`, `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION`, `PIVOT_LOG.md` D-578..D-584, `data/entities/kali/session_gnosis.md`. (2) **Execute debut order per DEBUT_REMEDIATION_MANUAL §5**: P0-1 residual (SECURITY_AUDIT ancestor + gitleaks) → INST-1 Fix 2+guards (atomic, Ma'at/N3) → Fix 4 → Fix 5 → Fix 6 → PUB-1 G1-G4 (Architect allowlist) → DEL-1 Week 1 (Roc). **Phase B workstreams (GN/DS/LI/KD/HR/ZS) are POST-DEBUT — BLOCKED.** (3) **Execute Context Injection Phase 1**: MANDATES_CONDENSED.md → opencode.json updates → sovereign compaction plugin → skills opt-in → verification. (4) Accept handoff `ho_91999b286910` + post Hivemind heartbeat to confirm onboarding.

**All agents MUST read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` upon waking.**

---

*⬡ OMEGA ⬡ KALI ⬡ PUBLIC-DEBUT-01 ⬡ 2026-08-20 ⬡ CARMACK-REVIEW-COMPLETE ⬡ CONSOLIDATED-SPECS ⬡ PHASE-1-READY ⬡ HANDOFF-HO-91999B286910*