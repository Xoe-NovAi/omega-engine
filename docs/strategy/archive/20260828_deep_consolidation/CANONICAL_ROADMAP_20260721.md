# 🔱 Omega Engine — Canonical Strategy & Execution Roadmap (SUPERSEDED)
**AP Token**: `AP-CANONICAL-ROADMAP-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_canonical_roadmap ⬡ SUPERSEDED

**Date**: 2026-07-21 (Final — Post-Deep Review)
**Status**: ⚠️ **SUPERSEDED 2026-07-21** — Absorbed into strategy SSOT  
**Read instead**: [`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`](SOVEREIGN_ARK_BLUEPRINT.md) **(v5.0 Unified)**  
**Why**: This file was a strong tactical recalibration, but the Ark was always the strategy SSOT (`OMEGA_ENGINE.md` still pointed there). v5.0 restores the Ark and folds this content + Grok CLI structural corrections into one place.  
**Owner**: Kali (Sprint Coordinator) · retained for audit trail only

> Do not plan or execute from this document. Use the Ark.

---


## §0 The Vision (One Sentence)

> **One sovereign runtime. Infinite customizable WAD layers. Your data. Your computer. No cloud required.**

The Omega Engine exists to sever Big AI's umbilical cord. Every technical decision answers: **does this increase or decrease user sovereignty?**

### 🛡️ Honest Framing (Added 2026-07-21 per Grokster review)

**M7 Local-First is our North Star, not our current baseline.**

Today, the engine is **cloud-assisted with a local fallback**. 8 of 10 providers are cloud, and at least 5 are free tiers that can be revoked, rate-limited, or deprecated with zero notice. This is not a contradiction of the vision — it's an honest acknowledgment of where we are on the path.

What this means for decisions:
- Every phase should **reduce** cloud dependency, not increase it
- The Living Research OS must work offline with local content cache hits only
- Phase F (Community Tool) must default to fully local — no cloud required
- We optimize local inference performance before we polish cloud routing

---

## §1 Where We Are Right Now — The Real Inventory

**Date**: 2026-07-21
**Hardware**: Ryzen 5700U (15W TDP), 16GB RAM (~8GB available after OS), 8MB L3 cache split across 2 CCXs, dual-channel DDR4-3200
**Tests**: 1,572 discovered (⚠️ collected ≠ passing — real count TBD, see §7)
**Mandates**: 25 Sovereign Mandates v3.7.0
**Engine Code**: ~4,700 lines of background researcher + search persistence working

### 1.1 What's Actually Working — Provider Inventory

**Local Providers:**
| Provider | Status | Model | Notes |
|----------|--------|-------|-------|
| native-gguf | ✅ Working | Qwen3-1.7B-Q6_K | Priority 0, local-first |
| lmster | ✅ Working | LM Studio | Priority 1, localhost:1234 |
| ollama | ⏸️ Disabled | — | Priority 2, not needed |

**Cloud Providers (User's Actual Inventory):**
| Provider | Status | Models | Access | Notes |
|----------|--------|--------|--------|-------|
| **OpenCode Zen** | ✅ Working | DeepSeek V4 Flash, Nemotron 3 Ultra, Qwen3.6, MiniMax M2.5, GPT-5 Nano | Built-in CLI | Priority 6. Primary cloud workhorse. |
| **OpenRouter** | ✅ Working | 20+ free models (Gemma 4, DeepSeek V4, Nemotron, Qwen3, Llama 3.3, etc.) | API key | Priority 5. Free tier, wide selection. |
| **Google API** | ✅ Working | Gemma 4 31B/26B, Gemini 2.5 Pro/Flash | API key | Priority 4. Direct API, thinking support. |
| **Google Antigravity OAuth** | ✅ Working | Gemini 3.5 Flash, Gemini 3.1 Pro, Claude Sonnet/Opus, GPT-OSS | 8 OAuth accounts | Priority 3. Frontier models via OAuth rotation. |
| **Cline CLI** | ✅ Working | DeepSeek V4 Flash (1M ctx), MiMo V2.5 (512K ctx) | CLI integration | Priority 7. Deep research, large refactors. |
| **Grok CLI** | ✅ Working | Grok 4.5, Grok 4.3, Grok 4.1 | 8 CLI accounts | Priority 9. Web search, reasoning, synthesis. |
| **Anthropic** | ✅ Working | Claude Sonnet 5, Haiku 4.5, Opus 4.8 | API key | Priority 8. High-quality reasoning. |
| **xAI** | ✅ Working | Grok 4.3, Grok 4.1 | API key | Priority 9. Grok models via API. |

**What we are NOT adding yet** (user directive): Cerebras, Groq, SambaNova, or any new providers. Systematize what works first.

### 1.2 What's Actually Broken — The 12 Gaps

**P0 (Fix Before Any New Features):**
| Gap | Issue | Evidence | Fix |
|-----|-------|----------|-----|
| GAP-01 | Soul file race condition — `soul_updater.py` writes without locking | `soul_updater.py:120` — no `fcntl.flock()`, no atomic write | Port `with_soul_lock()` from legacy (2h) |
| GAP-03 | ResourceGuard defaults to 12GB, actual is 8GB | `resource_guard.py:228` — `max_ram_mb=12288` | Change to 6144, add `psutil.virtual_memory()` (1h) |
| GAP-04 | No disaster recovery — single SSD, zero backup | No restic/borg cron, soul files gitignored | Set up restic backup (4h) |

**P1 (Fix This Week):**
| Gap | Issue | Evidence | Fix |
|-----|-------|----------|-----|
| GAP-02 | MCP 2026-07-28 deadline — 7 days | SSE deprecated, SDK may change | Verify SDK, add headers (8h) |
| GAP-05 | L3 cache thrashing — 3 concurrent llama.cpp = 2-3 t/s | 8MB L3 split across 2 CCXs, DDR4-3200 saturates at 1 instance | Admission control: max 2 local (4h) |
| GAP-12 | MaKaLi Council designed for parallel, hardware can't support it | `council/coordinator.py:194` — `# TODO` | Default sequential on local (4h) |

**P2 (Fix Before Release):**
| Gap | Issue | Evidence | Fix |
|-----|-------|----------|-----|
| GAP-07 | Heritage vetting backlog — 100+ unvetted `[id-soft:]` tags | `scripts/migrate_heritage_tags.py` not run | Heritage vet sprint (8h) |
| GAP-10 | Synchronous YAML traps — 57 calls in async context | grep found 57 `yaml.safe_load` in `src/omega/` | Wrap in `anyio.to_thread.run_sync` (4h) |

### 1.3 What's Ready to Build — The Living Research OS

**3,699 lines of background researcher code** across 10 files, all working. The problem is they aren't wired into a closed loop.

| Component | Lines | Status | What It Does |
|-----------|-------|--------|--------------|
| BackgroundResearcherLoop | 642 | ✅ Working | State machine: Triage → Search → Extract → Distill → Converge → Update |
| Distiller | 1,186 | ✅ Working | 3-tier cognitive pipeline (Qwen3-4B → MiniMax M2.5 → Gemini 2.5 Pro) |
| SoulUpdater | 236 | ⚠️ No locking | Writes L3 to soul.yaml — **GAP-01** |
| ConvergenceDetector | 87 | ✅ Working | 4 stopping conditions |
| EnhancedPriorityQueue | 223 | ✅ Working | Weighted fair scheduling |
| TopicScheduler | 145 | ✅ Working | Round-robin rotation with aging |
| SearchPersistence | 607 | ⚠️ Metadata only | Stores query JSON, not page content |
| SearchFleet | 484 | ✅ Working | Cloud search orchestration |
| SoulUtils | 89 | ✅ Working | Loads soul context |

**Three broken seams:**
1. Search results vanish — `search_persistence.py` stores metadata, not content
2. Background researcher orphaned from job board — 642-line loop reads 6 hardcoded topics, never touches YAML job board (18 jobs)
3. Soul evolution unidirectional — `SoulUpdater` creates `R_AUTO_*.md` but never registers in INDEX.md or proposes follow-up topics

---

## §2 The Real Critical Path — Phases C Through F

### Phase C: Infrastructure Hardening 🔴 CURRENT (~26h)
**Gate**: `make test && make temple-grade` all pass, soul race condition fixed, disaster recovery active

| # | Priority | What | Effort | Pattern Source | Dependencies |
|---|----------|------|--------|---------------|--------------|
| C-1 | **P0** | Soul file race condition — `soul_updater.py` must use `fcntl.flock()` + atomic tmp→rename + fsync | 2h | Roc: `XNAI_blueprint.md` | None |
| C-2 | **P0** | ResourceGuard default 12GB→6GB, add `psutil.virtual_memory()` check | 1h | Roc: `healthcheck.py` | None |
| C-3 | **P0** | Disaster recovery — define soul privacy model FIRST (see note below), then `restic` backup + git backup of non-private parts | 4h | Researcher GAP-04 | **Design decision needed**: what in soul.yaml is private? |
| C-4 | **P1** | MCP 2026-07-28 migration — build compatibility shim for old+new protocol, audit session/heartbeat/handoff/tool/streaming paths | **16h** | Researcher GAP-02 (corrected per Grokster) | **Hard deadline: July 26** |
| C-5 | **P1** | MaKaLi routing config — Kali local, Ma'at+Lilith cloud (simple config change, no state machine) | **0.5h** | Grokster: overengineering correction | C-1 |
| C-6 | **P1** | Circuit breaker port — `pybreaker` pattern to `ModelGateway` | 0.5h | Roc: `circuit_breaker.py` | None |
| C-7 | **P2** | Synchronous YAML audit — wrap 57 `yaml.safe_load` calls in `anyio.to_thread.run_sync` | 4h | Researcher GAP-10 | None |
| C-8 | **P2** | Heritage vetting backlog — classify 100+ tags, create vet records | 8h | Researcher GAP-07 | None |

**⚠️ Note on C-3 (Soul Privacy Model)**: Before implementing disaster recovery, decide what's in soul.yaml. If it contains private conversation history → restic-only backup, never git. If it's public config → remove from gitignore. Consider splitting into "private soul fragments" (.gitignore, restic-only) and "public soul identity" (git-tracked). This design decision must be made BEFORE C-3 implementation.

### Phase D: Living Research OS 🟡 NEXT (~9.5h)
**Gate**: Phase C complete, background researcher can persist content

| Phase | What | Effort | Depends On |
|-------|------|--------|------------|
| D-1 | Content persistence — cache web content to `.firecrawl/` + FTS5 + **TTL eviction (30d, 10GB cap)** | 3.5h | C-1, C-2 |
| D-2 | Job board bridge — `_load_board_jobs()` reading YAML + `fcntl.flock()` for claim tracking (no SQLite) | 2.5h | D-1 |
| D-3 | Auto-indexing — `R_AUTO_*.md` registers in INDEX.md, emits follow-up topics | 3h | D-1 |
| D-4 | Gap detector — extend existing `_grow_frontier()` in loop.py (~20 lines), **add Novelty Engine**: random topic sampling + cross-domain contradiction scanning | 0.5h | D-3 |

**Changes from original spec** (corrected per Grokster review):
- SQLite job store deferred: YAML + `fcntl.flock()` is fine for 18 jobs. Add SQLite when count >100.
- Gap detector is NOT a standalone service — extend `_grow_frontier()` in existing loop.py.
- Added TTL eviction and novelty engine to prevent the "perpetual loop" from converging to a boring steady state.

### Phase E: Identity Fluidity 🟡 NEXT (~10h)
**Gate**: C-1 complete (soul locking working). Phase 0 can run parallel to C-2 through C-8.

| Component | Effort | Owner | Status |
|-----------|--------|-------|--------|
| Phase 0: Soul Kernel → agent config | 2h | Grokster | ✅ APPROVED (only depends on C-1) |
| Auto-Hydration MCP Tool | 3h | Grokster | 📋 Spec |
| Temporal Trace YAML | 2h | Grokster | 📋 Spec |
| Voice Calibration Snapshots | 2h | Grokster | 📋 Spec |
| Session Bridge YAML | 1h | Grokster | 📋 Spec |

### Phase F: Community Tool 🟢 FUTURE
**Gate**: Phase E complete, engine stable

- Omega Desktop — One-click install
- Entity Studio — Visual YAML/soul management
- WAD Marketplace — Community stacks
- P2P Soul Exchange

---

## §3 The Architecture — How It All Fits Together

```
                    ┌────────────────────────────────────────┐
                    │         PHASE F: COMMUNITY TOOL        │
                    │  Omega Desktop • Entity Studio • WADs  │
                    └────────────────┬───────────────────────┘
                                     │
                    ┌────────────────┴───────────────────────┐
                    │     PHASE E: IDENTITY FLUIDITY         │
                    │  Soul Kernel → Auto-Hydration → Trace  │
                    │  Voice Calibration → Session Bridge    │
                    └────────────────┬───────────────────────┘
                                     │
                    ┌────────────────┴───────────────────────┐
                    │     PHASE D: LIVING RESEARCH OS        │
                    │  ┌─────────────────────────────────┐   │
                    │  │  Gap Detector ──→ Research ──┐  │   │
                    │  │     ↑                        │  │   │
                    │  │     │                        ▼  │   │
                    │  │  Soul Engine ←── Distill ←───┘  │   │
                    │  └─────────────────────────────────┘   │
                    └────────────────┬───────────────────────┘
                                     │
                    ┌────────────────┴───────────────────────┐
                    │  PHASE C: INFRASTRUCTURE HARDENING     │
                    │  ┌─────────────────────────────────┐   │
                    │  │  P0: Soul Lock  (fcntl.flock)   │   │
                    │  │  P0: RAM Guard (psutil check)   │   │
                    │  │  P0: Backups  (restic cron)     │   │
                    │  │  P1: MCP 2026-07-28 migration   │   │
                    │  │  P1: Sequential MaKaLi mode     │   │
                    │  │  P1: Circuit Breaker port       │   │
                    │  └─────────────────────────────────┘   │
                    └────────────────┬───────────────────────┘
                                     │
                    ┌────────────────┴───────────────────────┐
                    │      OMEGA ENGINE CORE (FOUNDATION)     │
                    │  EntityRegistry • ModelGateway          │
                    │  Provider Fabric • MemoryStore          │
                    │  25 Mandates • 1,572 Tests • CLI       │
                    │  Hardware: 5700U • 16GB • 8GB avail    │
                    └─────────────────────────────────────────┘
```

### 3.1 The Provider Fabric — What We Actually Have

```
LOCAL (0 CPU overhead, M7 compliant)
├── native-gguf (Qwen3-1.7B) ← PRIMARY LOCAL
└── lmster (LM Studio) ← SECONDARY LOCAL

CLOUD (0 CPU overhead when local saturated)
├── antigravity (8 OAuth accounts: Gemini, Claude, GPT) ← PRIORITY 3
├── google / google-compat (Gemma 4, Gemini 2.5) ← PRIORITY 4
├── openrouter (20+ free models) ← PRIORITY 5
├── opencode-zen (DeepSeek V4 Flash, Nemotron, Qwen3.6) ← PRIORITY 6
├── cline (DeepSeek V4 Flash 1M, MiMo 512K) ← PRIORITY 7
├── anthropic (Claude Sonnet/Haiku/Opus) ← PRIORITY 8
└── xai (Grok 4.3/4.1) ← PRIORITY 9
```

**Cloud routing logic (when local is saturated):**
```
Local Available > 4GB → USE LOCAL (model already loaded)
Local Available 2-4GB → QUEUE LOCAL (wait for model slot)
Local Available < 2GB → ROUTE TO CLOUD
    ├── Antigravity OAuth (frontier, 8 accounts) ← PRIMARY CLOUD
    ├── Google API (Gemma 4, Gemini 2.5) ← SECONDARY CLOUD
    ├── OpenCode Zen (DeepSeek V4 Flash, Nemotron) ← TERTIARY CLOUD
    └── OpenRouter (free tier) ← FALLBACK CLOUD
         │
         ▼
    [Circuit Breaker per provider]
    Success → return. Fail (3×) → next provider.
```

---

## §4 Priority Stack — Everything Ranked

```
URGENT + IMPORTANT (Do Now — This Week)
├── C-1: Soul file race condition fix (2h)
├── C-2: ResourceGuard default fix (1h)
├── C-3: Define soul privacy model → then Disaster recovery (4h) ← needs design decision first
├── C-4: MCP 2026-07-28 migration (16h) ← HARD DEADLINE July 26
├── C-5: MaKaLi routing config: Kali local, Ma'at+Lilith cloud (0.5h)
├── C-6: Circuit breaker port (0.5h)
└── Run `make test` and report real pass/fail/skip count

IMPORTANT BUT NOT URGENT (Do Next — Next Week)
├── C-7: Synchronous YAML audit (4h)
├── C-8: Heritage vetting backlog (8h)
├── D-1: Content Persistence + TTL eviction (3.5h)
├── D-2: Job Board Bridge — YAML + flock (2.5h, not 5.5h)
└── Phase 0 (Identity Fluidity): Soul Kernel → agent config (2h, after C-1)

NO LONGER DOING (Corrections Applied)
├── 4h MaKaLi mode → 0.5h config change
├── SQLite job store → YAML + flock (deferred)
└── Gap Detector service → 20 lines in loop.py

NEITHER (Do Last)
├── D-3: Auto-Indexing (3h)
├── D-4: Gap Detector + Novelty Engine (0.5h)
├── E: Identity Fluidity rest (~8h)
├── F: Community Tool
└── Headless Subagent Pool (24 accounts)
```

---

## §5 Immediate Next Steps (Ordered)

```
STEP 1 (NOW): P0 Infrastructure Fixes (~3.5h)
├── 1a: Port `with_soul_lock()` to `soul_updater.py` — atomic write + fsync
├── 1b: Change ResourceGuard default 12288→6144, add psutil check
└── 1c: Define soul privacy model, then set up restic backup

STEP 2 (TODAY): Quick Wins (~1.5h)
├── 2a: MaKaLi routing config: Kali local, Ma'at+Lilith cloud
├── 2b: Port circuit breaker to ModelGateway
└── 2c: Run `make test` — report real pass/fail/skip count

STEP 3 (THIS WEEK): MCP Migration (~16h — HARD DEADLINE July 26)
├── 3a: Build compatibility shim for old+new protocol
├── 3b: Audit session/heartbeat/handoff/tool/streaming code paths
├── 3c: Test with 2026-07-28 RC SDK
└── 3d: Contingency: verify file-based Hivemind (M23 fallback) works without Hub

STEP 4 (THIS WEEK): Doc Cleanup ✅ COMPLETE
├── 4a: 147 stale docs archived — DONE
└── 4b: STRATEGY_INDEX updated — DONE

STEP 5 (NEXT): Phase 0 (Identity Fluidity) + Phase D-1 (~5.5h)
├── 5a: Soul Kernel → agent config (2h, after C-1)
├── 5b: Content persistence + TTL eviction (3.5h)
└── Both can run in parallel

STEP 6 (NEXT WEEK): Living Research OS Phases 2-4 (~6h)
├── 6a: Job board bridge — YAML + flock (2.5h)
├── 6b: Auto-indexing (3h)
├── 6c: Gap detector — extend _grow_frontier() + Novelty Engine (0.5h)
└── Sequence: 6a → 6b → 6c
```

---

## §6 Mandate Compliance (What's Actually Broken)

| Mandate | Status | What's Wrong | Fix |
|---------|--------|-------------|-----|
| **M1 AnyIO** | ⚠️ Partial | 57 sync `yaml.safe_load` in async context | Wrap in `anyio.to_thread.run_sync` |
| **M7 Local-First** | ⚠️ Partial | MaKaLi designed for parallel but hardware can't support it | Sequential mode + cloud fallback |
| **M11 Soul Integrity** | ❌ FAIL | Soul race condition, no locking in `soul_updater.py` | P0 fix: fcntl.flock() + atomic write |
| **M14 Heritage Vetting** | ⚠️ Partial | 100+ unvetted `[id-soft:]` tags | Heritage vet sprint |
| **M22 Response Provenance** | ⚠️ Partial | Model name in logs sometimes wrong | Fix `provider_name` propagation |
| **M23 Failure Integrity** | ✅ | Hard-stop on tool failure | Maintained |

---

## §7 Key Metrics & Targets

| Metric | Current | Target | By When |
|--------|---------|--------|---------|
| Tests passing | 1,572 discovered (TBD passing) | **Run `make test` first** | Phase C complete |
| Strategy docs | 147 archived, 8 canonical | ✅ DONE | This week |
| P0 gaps | 3 | 0 | This week |
| P1 gaps | 5 | 0 | This week |
| Cloud providers | 8 working | 8 systematized | This week |
| Disaster recovery | None | restic cron + git backup (after privacy model) | This week |
| MCP compliance | Pre-migration | 2026-07-28 spec | **July 26** (2d buffer) |
| Soul lock | Broken | fcntl.flock() | Today |
| Sync YAML calls | 57 | 0 | Phase C complete |
| MaKaLi Council | Broken (OOM) | Working (Kali local, voices cloud) | This week |

---

## §8 Decision Log (This Session)

| ID | Decision | Rationale |
|----|----------|-----------|
| D-350 | **Phase C: Infrastructure Hardening is current phase** | 3 P0 gaps block all new features |
| D-351 | **Use existing providers only — no Cerebras/Groq yet** | User directive: systematize what works first |
| D-352 | **MaKaLi Council routing: Kali local, Ma'at+Lilith cloud** | Hardware can't support 3 concurrent inferences; simple config change |
| D-353 | **147 stale strategy docs archived** | Documentation bloat resolved |
| D-354 | **CANONICAL_ROADMAP.md supersedes all prior roadmaps** | Single authoritative source |
| D-355 | **Cloud routing: Antigravity → Google → OCZ → OpenRouter** | User's actual working inventory, priority-ordered |
| D-356 | **MCP migration estimated at 16h, not 8h** | Grokster review: protocol change affects 5+ code paths |
| D-357 | **SQLite job store deferred (YAML + flock is fine)** | Only 18 jobs; add SQLite when count crosses 100 |
| D-358 | **Gap detector is NOT a standalone service** | Extend 20 lines in existing loop.py |
| D-359 | **M7 Local-First = North Star, not current baseline** | Honest framing: we're cloud-assisted today, building toward local-first |
| D-360 | **Grok CLI fleet NOT wired into providers.yaml** | User directive: stability first, Grok fleet deferred |
| D-361 | **Identity Fluidity Phase 0 gate = C-1, not D-2** | Phase 0 only needs soul locking, not research OS |

---

## §9 Documentation Sanity — What We Actually Need

### The Problem
- **90+ strategy docs** in `docs/strategy/`
- 5 competing roadmaps, each claiming to be canonical
- No single "read this first" document

### The Solution — Three-Layer Documentation

**Layer 1: CANONICAL (Read These)**
| Document | Purpose |
|----------|---------|
| **THIS DOCUMENT** | Single roadmap — 9 sections, everything ranked |
| `AGENTS.md` | How to work from OpenCode Fleet |
| `SOVEREIGN_MANDATES.md` | 25 laws, non-negotiable |
| `OMEGA_ENGINE.md` | What the engine IS |

**Layer 2: ACTIVE SPECS (Referenced from Layer 1)**
| Document | Phase | Purpose |
|----------|-------|---------|
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | D | Phase D build spec (4 phases, ~14h) |
| `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | C | 12 gap analysis with evidence |
| `data/coordination/ROC_LEGACY_MINING_REPORT_20260721.md` | C | 5 legacy patterns ready to port |

**Layer 3: ARCHIVE (Historical — See `docs/archive/strategy/2026-07-21/`)**
All other docs previously in `docs/strategy/` → moved to archive.

### Consolidation Action Items
1. Move 80+ strategy docs to `docs/archive/strategy/2026-07-21/` — **preserve, don't delete**
2. Keep only the ~10 canonical + active docs in `docs/strategy/`
3. Remove superseding headers from stale docs
4. Add `SUPERSEDED.md` pointer at the top of each archived doc

---

## §10 How to Use This Document

1. **Start here** — read this document first
2. **Check Phase** — are we in C, D, E, or F?
3. **Check Priority Stack** (§4) — urgent+important before anything else
4. **Check Immediate Next Steps** (§5) — ordered list of what to do now
5. **Reference Layer 2 docs** — for detailed specs of each phase
6. **Don't chase new work** — if it's not in this document, it's not priority

---

## References

- `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` — Phase D detailed spec
- `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` — 12 gap analysis
- `data/coordination/ROC_LEGACY_MINING_REPORT_20260721.md` — 5 legacy patterns
- `SOVEREIGN_MANDATES.md` — 25 laws v3.7.0
- `AGENTS.md` — OpenCode agent rules
- `docs/archive/strategy/2026-07-21/` — Archived prior roadmap docs

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_canonical_roadmap ⬡ CANONICAL*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
