## §4 Priority Stack (Do This Order)

```
🚨 SUPER-URGENT (Architect-elevated 2026-07-22) — PARALLEL TO PHASE C
├── **G-1** Gemma/OpenCode workhorse continuity after free-tier cliff
│     Forensic: docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md
│     Ops path: docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md
└── **W-1** WARP proxy pool bring-up (OCZ multi-IP unlock; D-304 Track 1)
      Blocker: truncated /usr/local/bin/warp-ns-setup — fix from warp-proxy-pool/scripts/

PHASE C — COMPLETED ✅ (Keep below for historical trace; items no longer pending)
├── C-0  Test honesty ✅ (95/95 Phase 2 hardening, false count ban)
├── C-0.5 Soul Distillation Pipeline ✅ (Hook registered in opencode.json + script exists; needs OpenCode restart)
├── C-2′ One RAM truth ✅ (OOMProtector 3-signal fusion)
├── C-1′ SoulStore ✅ (Atomic writer, 4-layer guarantee)
├── C-3  Restic 3-2-1 Backup 🟡 (Amended: local repo acceptable; timer not enabled — only remaining required Phase D gate failure)
├── C-4a MCP audit ✅ (R_CG01 delivered, 16-hour/4-sprint plan)
├── C-4b MCP Streamable HTTP ✅ (Dual transport live; client SEP-2575 compliant)
├── C-5  MaKaLi routing config ✅ (oracle_summon_local)
├── C-6′ Breaker unification ✅ (Canonical HealthMonitor factory; 5/7 clones deprecated; 2 clones unmigrated — P-5 ticket open)
├── C-10 Local admission control ✅ (CCX-aware semaphore + OOMProtector)
├── C-10.5 Provider Fallback Chain ✅ (4 modules, 69 tests)
├── C-9  GenerationPolicy extract ❌ (Not started — optional Phase D criterion)
└── C-11 Property tests ✅ (16/16 pass; 1 skip; OOM/breaker/soul store coverage)

IMPORTANT (Next)
├── C-7 / C-8
├── E-0 Identity Phase 0 (after C-1′)
├── D-1 Content persistence + TTL (+ D-T tests)
├── D-2 Job board YAML bridge (P0/P1 only)
├── **NL-1** NotebookLM Ingestion Pipeline — implement `prepare_notebooklm.py` per R52c spec
└── **V-1** Omega-Vault MVP — explicit ticket (GAP-08; unblocks fleet later)
```

### G-1 ticket (Architect elevation 2026-07-22 — workhorse)

| Field | Value |
|-------|--------|
| **ID** | **G-1** |
| **Name** | OpenCode workhorse continuity after free Gemma 4 31B cliff |
| **Why** | Free-tier `input_token_count` limit **16000** for `gemma-4-31b` since **2026-07-15**; prior workhorse (May–Jul) dead for fat Omega sessions |
| **Evidence** | `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` |
| **Ops** | `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` |
| **Owner** | Architect (billing/OAuth) + Kali verify + Researcher DIG-01/03 |
| **Paths** | G-1a billing Tier 1 · G-1b Antigravity OAuth · G-1c OCZ+WARP · G-1d paid alt |
| **Not** | Context caps to fit free 16k · WARP as Gemma free-tier fix |

### W-1 ticket (Architect elevation 2026-07-22 — WARP)

| Field | Value |
|-------|--------|
| **ID** | **W-1** |
| **Name** | WARP multi-namespace proxy pool operational |
| **Why** | Unlock IP-rotated OpenCode Zen / IP-keyed cloud; D-304 Track 1 |
| **Blocker** | `/usr/local/bin/warp-ns-setup` truncated (syntax error line 49); prep units failed since ≥Jul 18 |
| **Fix source** | `/home/arcana-novai/Documents/Xoe-NovAi/warp-proxy-pool/scripts/warp-ns-setup.sh` |
| **Owner** | Architect (sudo) + P1/sysadmin |
| **Accept** | prep@1–3 active · node@1–3 active · SOCKS 8081–8083 · 3 distinct exit IPs · `import warp_proxy_pool` |
| **Not** | Google free-tier project quota rotation |

### V-1 ticket (Kali amendment 2 — explicit home)

| Field | Value |
|-------|--------|
| **ID** | **V-1** |
| **Name** | Omega-Vault MVP — credential / session automation |
| **Why** | GAP-08 credential void; fleet pool blocked until this exists |
| **Owner** | Researcher + Grokster (design) → Ma'at/P3 (impl) |
| **Depends** | Prefer after C-0; may design in parallel with C-1′…C-10 |
| **Blocks** | Grok CLI multi-account fabric pool (D-360′) |
| **Not** | Full 8-account pool — vault MVP first, then single ACP smoke |

### NL-1 ticket (NotebookLM Ingestion Pipeline — 2026-07-23 Mining)

| Field | Value |
|-------|--------|
| **ID** | **NL-1** |
| **Name** | NotebookLM Ingestion Pipeline — `prepare_notebooklm.py` |
| **Why** | R52c spec exists (5-notebook architecture, weekly sync, strategic pivot triggers); current docs not ingested into NotebookLM for LLM-assisted research |
| **Evidence** | `docs/research/archive/R52c_notebooklm_ingestion_strategy.md` |
| **Owner** | Researcher (impl) + Roc (validation) |
| **Depends** | D-1 Content Cache (provides `.firecrawl/` content source) |
| **Effort** | ~4h (script + 5 notebook creation + validation) |
| **Not** | Full NotebookLM automation — manual upload still required |

EXPLICITLY NOT DOING NOW (preserved in Corpus Map — not cancelled)
├── New free-tier providers (Cerebras/Groq/…)
├── SQLite job store / GapDetector service / VerificationGate
├── Grok CLI 8-account fabric pool (before V-1 + smoke)
├── "Port pybreaker into ModelGateway"
├── flock-only fix of soul_updater alone
├── Strike 11 / Dimension / Free-Will / Phase Γ Hub split
└── Phase D before C-0 + C-1′
```

---

## §5 Immediate Next Steps

**🚨 Super-urgent (same day, parallel)**: `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`
- **G-1** workhorse continuity · **W-1** WARP pool · forensic DIG tickets
- Evidence: `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md`

**Current Sprint**: `data/coordination/ACTIVE_SPRINT.json` (LLM-native format)
- Full plan: `docs/sprints/current/llms-full.txt` (16K tokens for agent consumption)
- Research index: `docs/archive/sprints/2026-07-25-guard-and-distill/08-research-index.md`

```
SUPER-URGENT (parallel, Architect):
├── G-1 Workhorse continuity (billing / Antigravity / OCZ)
└── W-1 WARP pool bring-up (sudo fix ns-setup → reg → bridges)

SPRINT: Guard & Distill (5 days, 4 P0 tickets)
├── C-10.5 Quota-Aware Provider Routing (maat/P3) — 8h
├── C-11 Property Tests: OOMProtector + SoulStore (maat/P3) — 12h
├── V-1 VaultCore MVP (maat/P1) — 8h (MOVED TO P0 - Blocks C-3)
├── C-3 Restic 3-2-1 Backup for Sovereign Data (lilith/P6) — 8h (Depends on V-1)
├── C-0.5 Scribe Agent L1→L2→L3 Distillation + Crash Recovery Sweeper (scribe/new) — 16h
└── P1 Gates: C-9, D-1, M21, C-4a.5 (escalation)

COMPLETED (Phase C Hardening):
├── C-0 Test Honesty ✅ (99 quarantined, honest badge)
├── C-2′ OOMProtector 3-signal fusion ✅
├── C-1′ SoulStore atomic writer ✅
├── C-6′ Breaker unification ✅ (HealthMonitor factory + 5/7 deprecated; 2 unmigrated → P-5)
├── C-5 MaKaLi routing config ✅
├── C-10 Admission control ✅
├── C-4a MCP audit doc ✅
└── 429 classification + Discovery fix ✅
```

**Escalation Trigger**: If Ma'at/P4 silent on C-4b by 2026-07-22 23:59 UTC → Kali executes C-4a.5 MCP Streamable HTTP migration directly.

**Gate to Phase D**: All 4 P0 tickets DONE + `make test` 100% pass + `make temple-grade` T1-T11 green + Soul distillation ≥1 L3 axiom/entity/week + Backup `restic check --read-data-subset 5%` weekly.

**NotebookLM Pipeline (Post Phase D Gate)**: NL-1 ticket ready — implement `prepare_notebooklm.py` per R52c spec once D-1 content cache provides `.firecrawl/` source.

---

## §6 Mandate Hotspots (Execution View)

| Mandate | Status | Action |
|---------|--------|--------|
| **M1** AnyIO | Partial | C-7 YAML off event loop |
| **M7** Local-First | Partial (North Star) | C-5 routing; no new cloud deps |
| **M11** Soul Integrity | **FAIL** | C-1′ SoulStore |
| **M13** Temple-Grade | At risk | C-0 green suite |
| **M14** Heritage | Partial | C-8 |
| **M22** Provenance | Partial | provider_name through fabric |
| **M23** Failure Integrity | Hold | MCP contingency; no soft-fail theater |

---

## §7 Provider Fabric (What We Actually Have)

```
LOCAL
├── native-gguf (Qwen3-1.7B)  priority 0
└── lmster                    priority 1

CLOUD (systematize; do not expand)
├── antigravity (OAuth pool)  priority 3  ← primary cloud
├── google / google-compat    priority 4
├── openrouter                priority 5
├── opencode-zen              priority 6
├── cline                     priority 7
├── anthropic                 priority 8
└── xai (API)                 priority 9

NOT IN FABRIC (do not list as "working capacity")
└── Grok CLI 8-account fleet  — external advisory OK; pool after vault + ACP smoke
```

Routing when local saturated: Antigravity → Google → OCZ → OpenRouter · single breaker per provider (C-6′).

---

## §8 Decision Log (Unified 2026-07-21 + 2026-07-23 Mining)

| ID | Decision |
|----|----------|
| **D-354′** | **SOVEREIGN_ARK_BLUEPRINT.md is strategy SSOT again** (v5.1). CANONICAL_ROADMAP absorbed. |
| D-350 | Phase C is current execution phase |
| D-351 | No new providers until fabric systematized |
| D-352 | MaKaLi: Kali local, voices cloud (config) |
| D-353 | 147 stale strategy docs archived |
| D-355 | Cloud order: Antigravity → Google → OCZ → OpenRouter |
| D-357 | SQLite job store deferred |
| D-358 | Gap detector = extend loop, not service |
| D-359 | M7 = North Star, not baseline |
| D-360′ | Grok fleet: honesty in docs now; vault → smoke → pool (not 4h fantasy) |
| D-361 | Identity Phase 0 depends on C-1′, not Phase D |
| **D-362** | C-1′ = SoulStore (multi-path elimination), not flock paste |
| **D-363** | C-6′ = unify/delete breakers, not port pybreaker |
| **D-364** | C-0 = test honesty is P0 before Phase D |
| **D-365** | Living Research OS spec amended by §3.2; cannot claim dual CANONICAL |
| **D-366** | **STRATEGY_CORPUS_MAP.md** is mandatory Layer 2 for fine-grained preservation |
| **D-367** | GAP-05 → **C-10** admission control (not only C-5 cloud voices) |
| **D-368** | Identity Fluidity E-0…E-5 paths preserved under `data/entities/grokster/workspace/` |
| **D-369** | Researcher queue extras (VerificationGate, SQLite, 7-stage) deferred but mapped — not discarded |
| **D-370** | **Kali ratifies** Strategy Unify APPROVE with amendments (`KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md`) |
| **D-371** | **V-1** is an explicit ticket (not free-text only) |
| **D-372** | Living Research OS body SUPERSEDED by banner + Ark §3.2 where conflict (Kali amendment 1) |
| **D-373** | **C-2′ before C-1′/C-10** — dependency order corrected (Nemotron synthesis) |
| **D-374** | **C-11 Test Infrastructure** added as P0 ticket (Nemotron synthesis) |
| **D-375** | **MCP audit must start TODAY** — 7-day deadline (Nemotron synthesis) |
| **D-376** | **E-0 Identity Fluidity** added to manual after C-1′ (Nemotron synthesis) |
| **D-377** | Free Gemma 4 31B workhorse collapse is **P0** — forensic report is evidence SSOT |
| **D-378** | Twin tickets **G-1** (workhorse) + **W-1** (WARP) elevated parallel to Guard & Distill |
| **D-379** | WARP is for **IP-keyed** OCZ (etc.), **not** Google free-tier input TPM fix |
| **D-380** | No silent context caps to force free Gemma under 16k |
| **D-381** | Broken `/usr/local/bin/warp-ns-setup` is primary WARP blocker; source = `warp-proxy-pool/scripts/warp-ns-setup.sh` |
| **D-382** | **Omnidroid 6 cognitive modules fully evolved into current architecture** — Jem Session 43 confirmed; no porting needed |
| **D-383** | **NotebookLM 5-notebook ingestion strategy (R52c) exists** — implement `prepare_notebooklm.py` as NL-1 ticket post Phase D |
| **D-384** | **Lilith Tarot genesis (Era 0)** recovered — 5 cards, full pantheon, rituals; add to philosophy lineage |
| **D-385** | **Mnemosyne 13-sphere Kabbalistic memory** recovered — precursor to soul.yaml; migration script needed |
| **D-386** | **Grok 8-account exports indexed** (274 convos, 6565 responses) — add to XNAI-RAG search fleet |

---

## §9 Structural Debt Gates (from Grok CLI Review)

Do not approve Phase D if any of these are still true:

1. More than one production soul-write path  
2. Red tests unacknowledged / vanity pass counts in Makefile or OMEGA_ENGINE  
3. New code pushed into god-modules already >1000 lines without a split  
4. New circuit-breaker class added instead of reusing HealthMonitor/gateway  
5. Strategy docs claiming different critical paths without supersession banners  

Full review: `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md`

---

## §10 How Agents Use This Document

1. Read **this file** for strategy & what to build next  
2. Read `OMEGA_ENGINE.md` for live metrics  
3. Read `SOVEREIGN_MANDATES.md` + `AGENTS.md` for law & workflow  
4. Open **`STRATEGY_CORPUS_MAP.md`** when you need *why / who said / deferred detail*  
5. Open **`FLEET_TEAM_PLAYBOOK.md`** before multi-agent work or Phase C execution  
6. Open Layer 2 phase specs only when executing that phase  
7. After compaction: hydration sequence in `AGENTS.md` / `OMEGA_CODEX.md`  
8. **Do not** resurrect archived roadmaps as competing masters  
9. **Do not** drop an agent idea without a Corpus Map row  

---

## §11 Agent Sources (2026-07-21) — Quick Pointers

| Agent | Primary artifact | Role in unification |
|-------|------------------|---------------------|
| Kali | CANONICAL_ROADMAP (superseded) · SESSION history | Ranking C–F, inventory |
| Researcher | UNKNOWN_UNKNOWNS · QUEUE_DESIGN | GAP-01…12 · D-2 design depth |
| Roc | ROC_LEGACY_MINING | Port patterns · cloud matrix (held) |
| Grokster | ADVERSARIAL_REVIEW · Identity Fluidity workspace · queue analysis | Strategy challenge · Phase E · fleet |
| Carmack | CARMACK_RESEARCH_AUDIT | Compress research theater · D-1 first |
| Carmack+Researcher | CARMACK_DEFINITIVE_STRATEGY_20260730 | YouTube Research Session — 24 proposals → top 5 force multipliers (Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus). Deep-dive evidence base: 5,000+ lines across 6 documents. Phase 0 strategy: research complete, awaiting implementation go/no-go. Definitive doc in `docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md`. |
| Grok CLI | GROK_CLI_CODEBASE_STRATEGY_REVIEW | SoulStore · CB unify · structural gates |
| Nemotron 3 Ultra | THIS REVIEW | Dependency order · test infra · MCP deadline · E-0 integration |

Full matrix: **`STRATEGY_CORPUS_MAP.md` §1**

---

## §12 References

| Path | Role |
|------|------|
| `OMEGA_ENGINE.md` | Engine state SSOT |
| `SOVEREIGN_MANDATES.md` | Law |
| `AGENTS.md` | OpenCode how-to |
| `docs/strategy/STRATEGY_INDEX.md` | Doc hierarchy index |
| **`docs/strategy/STRATEGY_CORPUS_MAP.md`** | **Fine-grained preservation (mandatory companion)** |
| **`docs/strategy/FLEET_TEAM_PLAYBOOK.md`** | **Fleet teamwork & coordination playbook** |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D detail (amended) |
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Superseded tactical draft (trail) |
| `docs/archive/strategy/2026-07-21/SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` | Ark v4.4 full body |
| `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` | Phase E architecture |
| `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | 12 gaps |
| `data/coordination/ROC_LEGACY_MINING_REPORT_20260721.md` | Legacy patterns |
| `data/coordination/GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | Adversarial strategy |
| `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | Structural review |
| `data/coordination/RESEARCHER_QUEUE_DESIGN_20260721.md` | Queue / SQLite / gates deep design |
| `data/coordination/CARMACK_RESEARCH_AUDIT_20260721.md` | Research board compression |
`docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md` | **Top-5 force multipliers strategy (2026-07-30)** — Ornith-9B, Vulkan, Instruction Router, Hardening, llama-optimus deep dives |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | 18 jobs (D-2 input) |
| `docs/decisions/PIVOT_LOG.md` | Decision history |

---

*⬡ OMEGA ⬡ SOVEREIGN-ARK ⬡ v5.2.0 ⬡ UNIFIED-SSOT+CORPUS+NEMOTRON ⬡ 2026-07-21*