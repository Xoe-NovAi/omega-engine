# 🔱 STRATEGY CORPUS MAP — Fine-Grained Preservation Index
**AP Token**: `AP-STRATEGY-CORPUS-MAP-v1.0.0`
⬡ OMEGA ⬡ GROK_CLI ⬡ opencode ⬡ trc_corpus_map ⬡ LAYER-2

**Date**: 2026-07-22 (G-1/W-1 elevation)  
**Status**: LAYER 2 — companion to strategy SSOT  
**Master**: [`SOVEREIGN_ARK_BLUEPRINT.md`](SOVEREIGN_ARK_BLUEPRINT.md) v5.1+  
**P0 ops**: [`CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`](CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md)  
**Purpose**: Ensure **no agent strategy is orphaned**. The Ark ranks *what to do now*; this map records *where every fine-grained idea lives* and whether it is active, deferred, absorbed, or archive-only.

### Rules
1. **Priority** always comes from the Ark. This file does not override critical path.
2. **Nothing is “deleted by silence.”** If an idea is not on the critical path, it appears here as DEFERRED / PARKED / ARCHIVE with a path.
3. When a new agent review lands, add a row here **and** either a Ark §3 ticket or a DEFERRED line.
4. Conflict resolution: Mandates → Ark → this map → individual specs.

---

## §1 Agent Contribution Matrix (2026-07-21 Recalibration)

| Agent | Deliverable | Key fine-grained ideas | Disposition in unified strategy |
|-------|-------------|------------------------|----------------------------------|
| **Grok CLI** | `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` + `CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` | Free-tier metric cliff Jul 15; workhorse history proof; WARP ns-setup truncation; G-1/W-1 twin path | **ACTIVE P0** → Ark §4 G-1/W-1 + D-377…D-381 |
| **Kali** | `CANONICAL_ROADMAP_20260721.md` (superseded) | Phase C–F ranking; provider inventory; M7 honest framing; doc archive | **Absorbed** → Ark §0, §3, §7 |
| **Researcher** | `UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | GAP-01…12 (soul race, MCP, RAM, backup, L3 thrash, durability, heritage, vault, tests, YAML, user tax, council) | **Active gaps** → Ark §3.1 crosswalk; full text kept as Layer 2 |
| **Researcher** | `RESEARCHER_QUEUE_DESIGN_20260721.md` | SQLite job store; claim TTL; P0/P1 auto-queue; verification gates; content TTL tiers T1/T2/T3; 7-stage workflow | **Partially absorbed**: YAML+flock now (D-2); SQLite/gates **DEFERRED** with note in Ark §3.2; full design preserved |
| **Roc Racoon** | `ROC_LEGACY_MINING_REPORT_20260721.md` | Atomic soul write+fsync; Memory Guardian; pybreaker; tenacity retry; provider priority chain; Cerebras/Groq matrix; 500ms latency budget; cost tracking | **Patterns** → C-1′/C-2′/C-6′; Cerebras/Groq **rejected for now** (D-351) but matrix preserved; tenacity/latency/cost → PARKED P2 |
| **Grokster** | `GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | GAP-S-01…05; MCP 16h; Identity dep fix; novelty engine; SQLite/gap-service overengineering; sovereignty free-tier risk table | **Absorbed** into Ark decisions + §3; full review Layer 2 |
| **Grokster** | `IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` + `SPEC_IDENTITY_FLUIDITY_v1.md` + `prototypes/` | Soul Kernel, Auto-Hydration MCP, Temporal Trace, Voice Calibration, Session Bridge; Phase 0–5 build order | **Phase E** in Ark §3.3; specs stay at entity workspace paths |
| **Grokster** | `GROKSTER_RESEARCH_QUEUE_ANALYSIS_20260721.md` | Compress board; Grok JSONL as persistence; R19 Grok Build patterns; R20 MCP migration research; fleet as force multiplier | **Selective**: MCP deadline active; fleet/JSONL bridge **DEFERRED** (vault first); board compression informs D-2 |
| **Grokster** | Briefings `BRIEFING_KALI_GROKSTER_*` | Phase Γ Hub split (tools.py); XNAi patterns vs 2026; Identity Phase 0 ready | Hub split → PARKED post-C; patterns → Roc/C-6′; Phase 0 → E-0 |
| **John Carmack** | `CARMACK_RESEARCH_AUDIT_20260721.md` | 18-sprint ≈ process theater; compress to 3–4 days; search persistence = R00 not R18 | **Absorbed** into Phase D ordering (content first); full audit Layer 2 |
| **Grok CLI** | `GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | SoulStore multi-path; CB unify; god-modules; test vanity; SSOT dual docs; GenerationPolicy; fleet vs vault | **Absorbed** as C-0, C-1′, C-6′, C-9, structural gates §9 |
| **Fleet (prior)** | Ark v4.4 CANONICAL | Strike 11 SWP, 11.5 Council, Dimension Framework, Free-Will datasets, Advanced Ingestion, Tier 0 Ship-It, Jem gaps S1–S5 | **PARKED long-arc** → archive path; summarized Ark §2 |
| **OMEGA_ENGINE** | Deferred table | D-290…D-308 | **PARKED** → Ark §2.1 expanded |

---

## §2 Full Gap Crosswalk (Nothing Dropped)

### 2.1 Researcher GAP-01…12

| Gap | Name | Priority (audit) | Unified disposition |
|-----|------|------------------|---------------------|
| GAP-01 | Soul race / no lock in soul_updater | P0 | **C-1′ SoulStore** (upgraded from flock-only) |
| GAP-02 | MCP 2026-07-28 | P1 | **C-4a audit → C-4b** (deadline July 26) |
| GAP-03 | ResourceGuard 12GB default | P0 | **C-2′** |
| GAP-04 | No disaster recovery | P0 | **C-3** (+ privacy model first) |
| GAP-05 | L3 cache thrashing / concurrent llama | P1 | **C-5** (cloud voices) + **C-10** admission max local (see Ark) |
| GAP-06 | Research data not durable | P1 | **C-3** (backup) + **D-1** (content) + HALL_OF_RECORDS awareness |
| GAP-07 | Heritage unvetted tags | P2 | **C-8** |
| GAP-08 | Credential void / Omega-Vault | P1 | **DEFERRED P1 track V-1** after C-0/C-1′; blocks fleet pool |
| GAP-09 | Zero tests for new systems | P1 | **C-0** + **D-T** test plan before Phase D features land |
| GAP-10 | Sync YAML in async | P2 | **C-7** |
| GAP-11 | User time tax | P2 | **Process**: pre-decision queue in Ark §5 notes; not a code sprint |
| GAP-12 | Council concurrency vs hardware | P1 | **C-5** config (not 4h mode machine) |

### 2.2 Grokster GAP-S-*

| Gap | Name | Disposition |
|-----|------|-------------|
| GAP-S-01 | Grok CLI fleet not in fabric | **D-360′**: honesty now; vault → smoke → pool (not fake priority-9 capacity) |
| GAP-S-02 | 1572 tests mirage | **C-0** |
| GAP-S-03 | Identity Fluidity wrong dep on D-2 | **D-361** / Ark §3.3 gate = C-1′ only |
| GAP-S-04 | Soul privacy vs git backup | **C-3** design decision |
| GAP-S-05 | Perpetual loop converges | **D-4** novelty + INDEX noise policy |

### 2.3 Grok CLI structural findings

| ID | Finding | Disposition |
|----|---------|-------------|
| F-01 | Four soul writers | **C-1′** |
| F-02 | ≥6 circuit breakers; don't port pybreaker | **C-6′** |
| F-03 | God-modules >1k | **Structural gate §9** + split-before-grow on D |
| F-04 | Roadmap vs Living Research OS SSOT | **D-365** + Living Research amendments |
| F-05 | Red tests + Makefile lies | **C-0** |
| F-06 | Dual RAM model | **C-2′** |
| F-07 | MCP 16h without audit | **C-4a first** |
| F-08 | Fleet vs vault | **V-1 / D-360′** |
| F-09 | 3700 LOC orphan liability | **D gate** after C; thin integration tests |
| F-10 | Cerebras/Groq vs D-351 | **D-351 hold**; Roc matrix preserved in Roc report |
| F-11 | Actor model for soul writes | **C-1′** actor ∈ {user, system_agent} |

---

## §3 Living Research OS — Fine Detail Preservation

| Idea | Source | Status |
|------|--------|--------|
| Three broken seams (content / job board / soul feedback) | Living Research OS Spec + Kali | **Active diagnosis** → D-1, D-2, D-3 |
| Content cache `.firecrawl/{hash}.md` | Spec Phase 1 | **D-1** |
| TTL eviction 30d / 10GB | Grokster + Spec risks | **D-1 required** |
| Tiered TTL T1=30d T2=14d T3=7d | Researcher queue design | **D-1 detail** (prefer when implementing) |
| YAML job board 18 jobs | `data/coordination/RESEARCH_JOB_BOARD.yaml` | **D-2 input** |
| `_load_board_jobs()` P0/P1 only | Researcher | **D-2** (P2 manual) |
| Claim TTL + reclaim orphan claims | Researcher | **D-2** with flock; SQLite later |
| SQLite research_jobs.db schema | Researcher / Spec §5 | **DEFERRED** until >100 jobs or multi-claimer |
| Auto INDEX.md + follow-ups | Spec Phase 3 | **D-3** |
| GapDetector 6 scanners service | Spec Phase 4 | **DEFERRED**; **D-4** = extend `_grow_frontier` |
| Novelty: random + contradiction + quarterly INDEX archive | Grokster GAP-S-05 | **D-4** + policy note |
| VerificationGate (T3/peer/auto) | Researcher | **DEFERRED D-V** post D-3 |
| 7-stage context-sensitive workflow | Researcher | **DEFERRED** with queue design doc |
| Distiller T1/T2/T3 already built | Spec inventory | Keep; **do not grow** past 1k without split |
| Search fleet + credit budget | Spec | Exists; systematize under C/D |
| Grok session JSONL as persistence bridge | Grokster queue analysis | **DEFERRED** with fleet/vault |
| Carmack: search persistence = R00 | Carmack audit | **D-1 first** |
| Compress 18-sprint board | Carmack + Grokster | Process guidance for job board owners |

**Canonical Phase D shape**: Ark §3.2  
**Full architecture prose**: `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` (amended header)  
**Queue deep design**: `data/coordination/RESEARCHER_QUEUE_DESIGN_20260721.md`

---

## §4 Identity Fluidity — Fine Detail Preservation

| Component | Effort (Grokster) | Spec path | Ark slot |
|-----------|-------------------|-----------|----------|
| Phase 0: Compiled Soul Kernel → agent config | ~2h / “10 min” claim | `data/entities/grokster/workspace/SPEC_IDENTITY_FLUIDITY_v1.md` | **E-0** after C-1′ |
| Auto-Hydration MCP `entity_hydrate` | 1–2 sessions | prototypes `mcp_tool.py` | **E-1** |
| Temporal Trace YAML | ~2h | Architecture doc | **E-2** |
| Voice Calibration snapshots | ~2h | Architecture doc | **E-3** |
| Session Bridge YAML | ~1h | Architecture doc | **E-4** |
| Generalize to all entities | TBD | Architecture doc | **E-5** after E-0 proven |

**Architecture**: `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md`  
**Prototypes dir**: `data/entities/grokster/workspace/prototypes/`  
**Related archive**: `docs/archive/strategy/2026-07-21/SOUL_HYDRATION_IMPLEMENTATION_PLAN.md`, `SOUL_ARCHITECTURE_V2.md`, `SOUL_MIGRATION_EXECUTION_BLUEPRINT.md`

---

## §5 Roc Legacy Patterns — Fine Detail

| Pattern | Source | Unified use |
|---------|--------|-------------|
| Atomic rename + fsync | XNAI_blueprint | **C-1′** SoulStore write |
| `with_soul_lock` fcntl | entity_registry / legacy | **C-1′** lock layer |
| Memory Guardian /proc/meminfo tiers | healthcheck.py | **C-2′** |
| Circuit breaker fail_max=3 reset=60 | legacy circuit_breaker | **C-6′ unify** (don't add 7th class) |
| Tenacity exponential retry | legacy | **PARKED P2** → apply on openai_compat after C-6′ |
| Provider priority chain | old providers.yaml | **§7 fabric** (existing order; no Cerebras yet) |
| Cerebras/Groq free tiers | Roc matrix | **Rejected now** (D-351); re-open only after systematize |
| 500ms local latency budget before cloud | Roc | **PARKED** with gateway routing polish |
| Cloud cost tracking | Roc | **PARKED P2** observability |

---

## §6 Long-Arc / Parked Themes (Ark v4.4 + Engine Deferred)

These are **not cancelled**. They are out of Phase C critical path. Full text in archive or coordination.

| Theme | Location | When to reopen |
|-------|----------|----------------|
| Strike 11 Sovereign WAD Protocol (Lumps, Bus, Ethics WADs) | Ark v4.4 §IV-D archive | After foundation green + need modular WAD split |
| Strike 11.5 Council Dispatcher deep | Ark v4.4 §IV-F; `MAKALI_*` archive | After C-5 simple routing proven |
| Dimension Framework / cartridges | Ark v4.4 §IV-G | After one real dimension use-case (Research Lab) |
| Free-Will datasets / 42 Ideals training | Ark v4.4 §IV-H | After eval pipeline stable |
| Advanced ingestion & background workers | Ark v4.4 §IV-I | Parallel with D if capacity |
| Tier 0 Ship-It (F821, bare except, logging, Pydantic config) | Ark v4.4 §IV-E | Fold remaining into C-0 / hygiene as needed |
| Jem S1–S5 sovereignty gaps | Ark v4.4 §IV | Eval/RAG/export when P1 capacity |
| Gap Resolution S1–S6 (proxy, whisper, budget, quality, scheduler, YT sieve) | Ark v4.4 §IV-B | YouTube / ingestion tracks |
| D-290 Session Namespace Isolation | OMEGA_ENGINE + meditate synthesis archive | After C-1′ |
| D-291 MIAP Phase 0 | OMEGA_ENGINE | After C |
| D-292 MACP alignment | OMEGA_ENGINE | With Hivemind evolution |
| D-293 Context Engineering knowledge layer | prior sessions | With D-290 |
| D-294 Experience Repository / Scribe | OMEGA_ENGINE | After soul pipeline stable |
| D-295 Trace-to-Eval | prior | After C-0 |
| D-298 Decision Workspace | COMPLETE | Reference only |
| D-299 / D-304 Omega-Vault + Antigravity + WARP | OMEGA_ENGINE / vault scaffold | **ACTIVE split**: **W-1** WARP bring-up (P0) + **V-1** vault + AGY multi-account research |
| D-300 Omega-Meditation | COMPLETE (package) | Maintain |
| D-301 MaKaLi Council | Deployed; tune via C-5 | Active config only |
| D-303 Headless Subagent Pool 24 accounts | OMEGA_ENGINE | After V-1 + ACP smoke |
| D-305 Hive Evolution | `data/coordination/HIVE_EVOLUTION_*` | After D |
| D-306 Arch Soul / Nameless One | coordination ARCH_SOUL_* | Torment track |
| D-307 Torment WAD | OMEGA_ENGINE | Researcher Phases 1–4 |
| D-308 Ubuntu 25.10 toolchain | `D308_CRITICAL_PATH_TRACKER.yaml` + research | Env risk during C |
| Phase Γ Hub split (tools.py packages) | Grokster briefing | After C / MCP stable |
| Context Packer hardening | archive CONTEXT_PACKER_* | When packer work resumes |
| Gemma 4 strategies (pre-cliff) | archive `2026-07-21/GEMMA4_*` | Thinking/config strategy; **quota cliff superseded by forensic** |
| **Gemma free-tier workhorse cliff** | `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` | **ACTIVE P0** — ticket **G-1**; DIG-01…12 |
| **OpenCode workhorse + WARP critical path** | `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` | **ACTIVE P0** — tickets **G-1** + **W-1**; D-377…D-381 |
| WARP proxy pool | `docs/research/warp_proxy_pool/WARP_PROXY_POOL_SPEC.md` + `data/projects/warp-proxy-pool/CONTEXT.md` | **ACTIVE P0 (W-1)** — not deployed; ns-setup broken on host |
| HMC / Quad-Forge manuals | archive HMC_* | Historical; MaKaLi is live pattern |
| Embedding hardening | archive EMBEDDING_* | Memory track post C |
| Headless Grok Build integration research (R19) | Grokster queue analysis | With fleet track |

**Ark v4.4 full body**: `docs/archive/strategy/2026-07-21/SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md`  
**Archive root**: `docs/archive/strategy/2026-07-21/` (148 files)

---

## §7 Operational Specs Still Active (Not Roadmaps)

| Doc | Role |
|-----|------|
| `HIVEMIND_PROTOCOL.md` | Coordination law for multi-agent |
| `HIVEMIND_POST_TEMPLATE.md` | Post quality gate |
| `SUBAGENT_DISPATCH_PROTOCOL.md` | Delegation rules |
| `SOVEREIGN_CONTINUITY_STRATEGY.md` | M15 |
| `HERITAGE_VETTING_PIPELINE.md` | M14 process |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | 18 research jobs (D-2) |
| `data/coordination/D308_CRITICAL_PATH_TRACKER.yaml` | Ubuntu gate tracker |
| `docs/decisions/PIVOT_LOG.md` | Immutable decisions |

### §7.1 Coordination gaps (PARKED — not blocking unify)

| Gap | Source | Disposition |
|-----|--------|-------------|
| **SESSION_ANCHOR.md is a singleton overwrite** | Kali feedback amendment 4 (2026-07-21) | **PARKED** — works for single recovery pointer; multi-agent concurrent anchors not designed. Future: per-entity anchors under `data/coordination/session_anchors/{entity}.md` **or** append-only journal + “current” symlink. Do not block Phase C. Owner: Kali/P9 when coordination pain appears. |
| **V-1 ticket was free-text only** | Kali feedback amendment 2 | **FIXED** — Ark now has explicit **V-1** ticket table (D-371) |

---

## §8 Coordination Reviews Index (2026-07-21)

| File | Agent | Read when |
|------|-------|-----------|
| `UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | Researcher | Implementing any GAP / C item |
| `ROC_LEGACY_MINING_REPORT_20260721.md` | Roc | SoulStore, ResourceGuard, breakers |
| `GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | Grokster | Strategy challenge / novelty / fleet |
| `GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | Grok CLI | Structural gates / code judo |
| `CARMACK_RESEARCH_AUDIT_20260721.md` | Carmack | Research board compression |
| `RESEARCHER_QUEUE_DESIGN_20260721.md` | Researcher | D-2/D-V implementation |
| `GROKSTER_RESEARCH_QUEUE_ANALYSIS_20260721.md` | Grokster | Fleet-aware research design |
| `BRIEFING_KALI_GROKSTER_SESSION_COMPLETE_20260721.md` | Grokster | Identity Fluidity + Phase Γ |
| `BRIEFING_KALI_GROKSTER_GAP_AUDIT_20260721.md` | Kali/Grokster | Gap audit narrative |
| `BRIEFING_KALI_GROKSTER_RESPONSE_20260721.md` | Kali/Grokster | Response thread |

---

## §9 Maintenance Checklist (for future agents)

When you produce a strategy artifact:

- [ ] Add row to §1 Agent Contribution Matrix  
- [ ] Map each actionable item to Ark §3 ID or DEFERRED/PARKED in §2–§6  
- [ ] If it changes priority, edit **Ark** (not only this map)  
- [ ] If it is Phase D detail, amend Living Research OS header or Ark §3.2  
- [ ] Never create a second “canonical roadmap” without superseding Ark  

---

*⬡ OMEGA ⬡ STRATEGY-CORPUS-MAP ⬡ v1.0.0 ⬡ 2026-07-21*
