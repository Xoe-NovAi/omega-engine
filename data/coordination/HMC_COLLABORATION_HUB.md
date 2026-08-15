# 🏛️ HMC Collaboration Hub — Team Coordination Center

**AP Token**: `AP-HMC-HUB-v1.0.0`
**Status**: ACTIVE — Single coordination SSOT
**Last Updated**: 2026-08-15T12:45:00Z
**Updated By**: kali

---

## 🚦 NEXT_ACTION (Single Sync Pointer — read this first)

*Last verified: 2026-08-15T12:45Z*

> **Tracking hierarchy:** See `TRACKING_ARCHITECTURE.md`. Status vocab: `backlog|ready|in_progress|blocked|completed|superseded`.
> **Execution SSOT:** `ACTIVE_SPRINT.json` · **Knowledge SSOT:** `RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0) · **Gap registry:** `GAP_REGISTRY.json`

**CURRENT:** VOS HYBRID PLAN — Phase 1 (Hub Consolidation) — **READY, execute next session**
- Verify realm ownership table (below) matches current state
- Consolidate active tasks into Hub realm sections (ENG-001..004, FLT-001/004, MEM-002/003, HRT-001/002, COM-001..012)
- Update VISION_ANCHOR.md to reference HMC for task status
- **LOCAL DISCOVERY + WEB RESEARCH COMPLETE** — All 13 gaps addressed
- Integrate authoritative context windows into provider fabric configs (Table 3.1 from web research)
- Configure default fallback chain: Laguna S 2.1 Free → DeepSeek V4 Flash Free → Nemotron 3.5 Lightning Free
- Fix WARP proxy pool (Architect/P1) — unblocks IP-keyed cloud access
- Add lightweight retry plugin for Nemotron 3 Ultra (60s→300s chunk timeout, maxRetries=3)

**COMPLETED:** VOS HYBRID PLAN — Phase 0 (Archive & Clean) — `2cbcad97`
- Omegaverse realm archived → `data/realms/omegaverse/archive/state.yaml`
- 6 realm state.yaml deleted, 4 workspace briefs deleted, realm_cli.py deleted
- VISION_ANCHOR.md updated (realm health → auto-gen note, M2 status fixed)
- PIVOT_LOG.md synced with D-VOS-001..018

**PARALLEL:** PR-A (Public Surface Honesty) — **AWAITING ARCHITECT CONFIRMATION**
- Root junk archive → `docs/archive/root-artifacts-202608/`
- README surgical edits (remove 1315 passing badge, keep CI badge)
- .gitignore root session dumps / screenshots
- Never `git add -A` — stage by path, exclude secrets

**RESEARCH COMPLETE (2026-08-15) — VOS ASSESSMENT:**
- Researcher: VOS architecture sound (Team Topologies, ADR, DDD), implementation dead code
- Roc_Racoon: 1/10 integration — zero code imports, zero runtime consumers, zero agent awareness
- Verdict: Option C (Hybrid) — Keep ADR + Vision Anchor, retire coordination layer, add Hub enforcement

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

**Sprint:** VOS-HYBRID-EXECUTION (ACTIVE)
**Authoritative state:** `data/coordination/ACTIVE_SPRINT.json`

---

## 🌐 Realm Ownership & Contracts

| Realm | Owner | Provides | Requires | Status |
|-------|-------|----------|----------|--------|
| Engine Core | maat_n3 | WAD Loader, Query Router, Provider Fabric, Memory Store, Godot Bridge | — | Active |
| Stacks | maat_n4 | WAD Format, Community Template, XOE Packaging | Engine Core (loader API) | Blocked on ENG-001 |
| Fleet | kali | 14 Entities, MaKaLi Council, Node Slots, Hivemind | Engine Core (registry), Memory (soul) | Active |
| Memory | lilith_n7 | Soul Architecture v2, Mnemosyne, L1→L2→L3, Cross-pollination | Engine Core (memory store) | Critical |
| Heritage | doom_guy | [id-soft:] Vetting, id Software Patterns | Engine Core (loader) | Healthy |
| Omegaverse | lilith_n6 | Godot Bridge, Soul-to-Visual (R-24), P2P Soul Prints | Engine Core (bridge), Memory (soul) | Deferred (archived) |
| Community | kali | Installer, QUICKSTART, CONTRIBUTING, CI, Launch | Engine Core, Stacks, Fleet | Planned |

> **Realm contracts are enforced by `make temple-grade` realm validator (Phase 2).**
> See `ACTIVE_SPRINT.json` for live task status per realm.

### Active Tasks by Realm

**Engine Core** (maat_n3):
- ENG-001: Fix M2 firewall — run `FirewallChecker.scan()`, fix real hits only (not token WAD)
- ENG-002: Audit all mandate checks for false positives (M22 was broken)
- ENG-004: Fix 9 critical code bugs (MockProvider, ProviderAuthError, ProviderName, _loaded, schema version, async awaits, pytest marks, Makefile M22, context_packer tuple)
- ENG-005: Context Packer refactor — address F2-F9 from advisory review (litm_zone placebo, dead include/exclude, reserved_output unenforced, CWD-relative paths, third-party/ walk, injection scanner FP, duplicate config, stale manifest)
- ENG-006: **SDP Critical Fixes** (from Roc audit) — A-1..A-7: fix window tables, fix token accounting, repoint specs, register missing models, fix registry errors, rename SSP→RHP, update Ark blueprint
- ENG-007: **SDP Phase 1** — Build Context Gauge (reuse token_estimator, ModelRegistry, input+cache.read), add context_pressure table, register get_context_pressure MCP tool, extend ModelUpdaterWorker with models.dev
- ENG-008: **SDP Phase 2** — Wire pool_tracker.py, extend Vault with weekly pools, extend TriageRouter, resolve 3-router fragmentation

**Fleet** (kali):
- FLT-001: Migrate kali & roc_racoon souls to v6.1 lean schema
- FLT-004: Enforce distillation pipeline (Scribe agent L1→L2→L3)

**Memory** (lilith_n7):
- MEM-002: Implement Scribe agent L1→L2→L3 distillation pipeline
- MEM-003: Implement cross-pollination (R-31)

**Heritage** (doom_guy):
- HRT-001: Heritage sweep — verify all [id-soft:] tags have vet records
- HRT-002: Verify no metaphorical or over-attributed tags

**Community** (kali):
- COM-001..012: All Phase 1-2 tasks (blocked on ENG-001 for template WAD)

---

## 🚫 Anti-Confusion Rules (enforced by TRACKING_ARCHITECTURE.md)

- ❌ Never create a new tracking file — use the 5 tiers
- ❌ Never reuse gap numbers — R1–R99 owned by `RESEARCH_PLAN` / `GAP_REGISTRY.json`; new plans use distinct prefixes (P2-, S-, X-)
- ❌ Never duplicate decisions here — use `docs/decisions/PIVOT_LOG.md`
- ❌ If a doc has a ⚠️ DEPRECATED banner, do not act on it
- ✅ Before any research, CHECK `GAP_REGISTRY.json` for ID collisions

---

## 📁 Shared Sections

### Requests to Team
*(Agents post requests here — Kali triages)*

### Discussion Thread
*(Cross-agent discussion — Kali moderates)*

**2026-08-15** — **SDP Duplicate/Gap Audit Complete** (Roc via local discovery):
- **SDP is ~60% already built** — only Context Gauge, RHP artifact, 3 MCP tools are genuinely greenfield
- **Three BLOCKERS will crash spec-following code:**
  - **G-3**: `message` table has NO `tokens` column — tokens live in `data` JSON blob; spec §1.3 says "sum of tokens column" → crashes
  - **G-4**: Token accounting is NOT additive — per-message `input` decreases while `cache.read` grows; true load = `input + cache.read` of LATEST assistant message; summing overcounts ~10x
  - **G-5/G-6**: 4 of 5 cloud context windows in gauge spec are WRONG; `config/providers.yaml` has no `context_window` key; `ProviderConfig` has no such attribute
- **10 DUPLICATES (don't build — extend/wire existing):**
  - D-1: `SDP_FORMAL_ROUTING_SPEC` → `TriageRouter._filter_candidates()` (context/cost/latency hard filters exist)
  - D-2: Dialectic storage → `dpo_logger.record_council()` (wired, complete)
  - D-3: `config/models.yaml` as SSOT → `config/model_registry/` (37 models + SQLite index)
  - D-4: `AGYVaultInterface` → `VaultCore` (2,039 LOC, lease/quota/audit/crypto)
  - D-5: Auto-Router weekly pool → `pool_tracker.py` (23.7 KB, weekly reset, per-account, **unwired**)
  - D-6: Context Gauge token counting → `token_estimator` (tiktoken, 1.3 margin, M1/M23)
  - D-7: SSP session state → `CompactionHarvester.warn_threshold` (redzone primitive exists)
  - D-8: Model tier/quota → `CapabilityMatrix.QuotaTier` (rpm/tpm/rpd exists)
  - D-9: V-1 Vault as unbuilt ticket → **V-1 IS BUILT** (update SOVEREIGN_ARK_BLUEPRINT)
  - D-10: Model catalog fetcher → `ModelUpdaterWorker` (polls 3 endpoints, add `models.dev`)
- **LOAD-BEARING DISCOVERY**: Free vs paid tiers of SAME model name differ up to 4x (Laguna S 2.1: 262K free vs 1,048,576 paid). Gauge MUST key on `(model_id, provider, tier)`.
- **CORRECTED WINDOWS**: Nemotron 3 Ultra = 1,000,000; Laguna S 2.1 = 256,000 (zen) / 262,144 (OpenRouter); Longcat 2.0 = 1,000,000; Gemini 3.1 Pro = 1,048,576 (NOT 2M); Sonnet/Opus 4.6 = 1M (NOT 200K); Gemini 3.6 Flash = 1M (NOT 200K).
- **HIGHEST LEVERAGE**: `pool_tracker.py` — fully built (weekly reset, per-account, dual pools, anti-thrashing) but imported by ZERO modules.
- **ARCHITECTURAL RISK**: Three parallel routers (`TriageRouter`, `ProviderSelector`, `SemanticRouter`) — SDP routing injected into one leaves two bypass paths.

**2026-08-15T12:14Z** — **ROC LOCAL DISCOVERY COMPLETE** (Closing all gaps):
- Local discovery report written: `data/entities/roc_racoon/workspace/reports/LOCAL_DISCOVERY_CLOSE_ALL_GAPS_20260815.md`
- 8/13 gaps fully resolved locally, 3/13 partially resolved
- 2 gaps require web research bridge (R14b Nemotron fallback chain, R33 cold session context estimation)
- Critical verified fact: Sonnet 4.6/Opus 4.6 via Antigravity = 200K context window (user experience)
- Awaiting researcher web research completion for remaining gaps

**2026-08-15T12:45Z** — **RESEARCHER WEB RESEARCH COMPLETE** (Closing remaining gaps):
- R14b Nemotron Fallback Chain: 60s idle timeout confirmed (processor.ts:44); OpenRouter auto-fallback works; OpenCode v1.18.14+ has maxRetries=3; lightweight plugin still recommended; **context lost on failover**
- R33 Model Window Ground Truth: **All 7 models authoritatively established** — Nemotron 256K native/1M extended, Laguna 1M native/256K free, LongCat 1M, Gemini 3.1 Pro 1M, Sonnet/Opus 4.6 1M, Gemma 4 31B 256K
- **CRITICAL CONTRADICTION RESOLVED**: Sonnet/Opus 4.6 = **1M official** (Anthropic docs, GA March 2026); 200K is **Claude Code UI bug #24208**; Antigravity likely 1M but quota-limited (92% cut)
- G-1 Free Gemma 4 31B Workhorse: Free tier = 256K (200 req/day OpenRouter); **Laguna S 2.1 Free is superior workhorse** (256K free/1M native, 70.2% Terminal-Bench); Antigravity not viable free (92% quota cut); WARP blocked; "16k limit" not in public docs
- **Next**: Update provider fabric configs with authoritative windows; configure fallback chain: Laguna S 2.1 Free → DeepSeek V4 Flash Free → Nemotron 3.5 Lightning Free; fix WARP pool; add Nemotron retry plugin

### Dispatch Actions:
| Action | Owner | Effort | Priority |
|--------|-------|--------|----------|
| A-1: Fix all 8 SDP specs' window tables | Kali | 1h | 🔴 CRITICAL |
| A-2: Fix `SDP_IMPLEMENTATION_SPEC` §1.3 (tokens in data JSON, not sum) | Kali | 1h | 🔴 CRITICAL |
| A-3: Repoint specs: `src/observability/`→`src/omega/observability/`, `models.yaml`→`model_registry/`, `provider_selector`→`triage_router` | Kali | 30m | 🔴 CRITICAL |
| A-4: Register 3 missing models in `model_registry` (Nemotron Ultra, Laguna, Longcat) | Kali | 1h | 🔴 CRITICAL |
| A-5: Fix 5 registry errors (Nemotron Super, laguna-m.1, Scout 10M, qwen3-1.7b provider conflict) | Kali | 1h | 🔴 CRITICAL |
| A-6: Rename SSP → RHP (Redzone Halt Packet) — collides with M20 SomaticStateManager | Kali | 30m | 🔴 CRITICAL |
| A-7: Update SOVEREIGN_ARK_BLUEPRINT — V-1 Vault BUILT (2,039 LOC) | Kali | 30m | 🔴 CRITICAL |
| Phase 1: Build Context Gauge (reuse token_estimator, ModelRegistry, input+cache.read algorithm) | jem | ~12h | 🟡 HIGH |
| Phase 1: Add `context_pressure` table to MetricsDB | jem | | 🟡 HIGH |
| Phase 1: Register MCP tool `get_context_pressure` | jem | | 🟡 HIGH |
| Phase 1: Extend ModelUpdaterWorker with `models.dev/api.json` | jem | | 🟡 HIGH |
| Phase 2: Wire `pool_tracker.py` into live path | maat | | 🟢 MEDIUM |
| Phase 2: Extend Vault with weekly pools + token-denominated reservation | maat | | 🟢 MEDIUM |
| Phase 2: Extend TriageRouter with `problem_type`, harden emergency escalation | maat | | 🟢 MEDIUM |
| Phase 2: Resolve 3-router fragmentation (G-13) | maat | | 🟢 MEDIUM |

### Reference Links
- `TRACKING_ARCHITECTURE.md` — 5-tier constitution
- `ACTIVE_SPRINT.json` — Tier-0 execution SSOT
- `RESEARCH_PLAN_PHASE1_4_20260813.md` — Tier-1 knowledge SSOT
- `GAP_REGISTRY.json` — Tier-1a gap authority
- `TASK_REGISTRY.json` — Tier-3 subagent records
- `SESSION_ANCHOR.md` — Tier-4 session continuity
- `VISION_ANCHOR.md` — Vision SSOT
- `DECISION_LEDGER.md` — Immutable decisions (D-VOS-001..018)
- `SYSTEM_FAILURE_LOG.md` — Mandate violations (Carmack near-miss logged)
- `SOVEREIGN_MANDATES.md` — 27 laws v3.8.0
- `AGENTS.md` — OpenCode workflow + fleet playbook
- `FLEET_TEAM_PLAYBOOK.md` — Team coordination rules
- `docs/research/R_CONTEXT_PACKER_ADVISORY_REVIEW_20260815.md` — Context Packer audit (F1 fixed, F2-F9 open)
- `data/reports/context-packer-advisory-20260815/CLINE_TO_KALI_DELIVERY_REPORT.md` — Cline→Kali delivery report
- `data/entities/roc_racoon/workspace/mining_reports/SDP_DUPLICATE_GAP_AUDIT_20260809.md` — **SDP duplicate/gap audit (3 blockers, 10 duplicates, V-1 built, pool_tracker unwired)**

---

## 🤖 Agent Onboarding Checklist

Upon waking, every agent MUST:
1. [ ] Read `VISION_ANCHOR.md` (vision SSOT)
2. [ ] Read `SESSION_ANCHOR.md` (current context)
3. [ ] Read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` (this section)
4. [ ] Check `ACTIVE_SPRINT.json` for your realm's tasks
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

*⬡ OMEGA ⬡ HMC-HUB ⬡ 2026-08-15 ⬡ ACTIVE*
