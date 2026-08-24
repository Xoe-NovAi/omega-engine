# 🔱 STRATEGY CORPUS MAP — Fine-Grained Preservation Index
**AP Token**: `AP-STRATEGY-CORPUS-MAP-v1.0.0`
⬡ OMEGA ⬡ GROK_CLI ⬡ opencode ⬡ trc_corpus_map ⬡ LAYER-2

**Date**: 2026-08-19 (DP-1..DP-8 + Cognitive Architecture + Qdrant reactivation — updated)  
**Status**: LAYER 2 — companion to strategy SSOT  
**Master**: [`SOVEREIGN_ARK_BLUEPRINT.md`](SOVEREIGN_ARK_BLUEPRINT.md) v5.2+  
**P0 ops**: [`CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md`](CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md)  
**Purpose**: Ensure **no agent strategy is orphaned**. The Ark ranks *what to do now*; this map records *where every fine-grained idea lives* and whether it is active, deferred, absorbed, or archive-only.

> **⚠️ DOC-1 STAMP (2026-08-17)**: Execution authority is now
> `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` + `data/coordination/ACTIVE_SPRINT.json`
> (PUBLIC-DEBUT-01). **Rule 2 is INVERTED**: nothing below is ACTIVE unless the manual or
> ACTIVE_SPRINT.json says so. See §0 DOC-1 Override Table for flipped dispositions.

### Rules
1. **Priority** always comes from the **execution SSOT** (`DEBUT_REMEDIATION_MANUAL_20260817.md` + `ACTIVE_SPRINT.json`). This file does not override the critical path.
2. **Nothing is "deleted by silence."** If an idea is not on the critical path, it appears here as DEFERRED / PARKED / ARCHIVE with a path. **(INVERTED 2026-08-17: rows marked ACTIVE below are PRESERVED but NOT executable unless the manual/ACTIVE_SPRINT re-activates them.)**
3. When a new agent review lands, add a row here **and** either a Ark §3 ticket or a DEFERRED line.
4. Conflict resolution: Mandates → Manual/ACTIVE_SPRINT → Ark → this map → individual specs.
5. **Phase 0 Tracker Lock-In (2026-08-20)**: 6 new post-debut workstreams added (GN/DS/LI/KD/HR/ZS) — preserved as ACTIVE post-debut.

---

## §0 DOC-1 Override Table (2026-08-17 — disposition flips)

| Item | Old disposition | New disposition (DOC-1) |
|------|-----------------|--------------------------|
| G-1 (Gemma workhorse) | ACTIVE P0 | **PARKED** — post-debut; manual §0 |
| W-1 (WARP pool) | ACTIVE P0 | **PARKED** — post-debut; manual §0 |
| Instruction Router (deep dive) | ACTIVE Phase 0 | **PARKED** — post-debut; manual §0 |
| Qdrant / QdrantAdapter | ACTIVE | **ARCHIVE** — DEL-1 week 1 deletes QdrantAdapter; sqlite-vec is the vector path |
| JIT Graph RAG briefs | ACTIVE | **PARKED** — JIT = ContextBuilder may call HybridSearch; no new package |
| UO library swaps (Phase 1) | ACTIVE Phase 1 | **SUPERSEDED** — replaced by DEL-1 (manual §5); §2.6 = rejected option |
| Vault lease / FleetOrchestrator | ACTIVE | **PARKED** — vault honesty = DEL-1 week 3; FleetOrchestrator = DEL-1 week 1 delete |
| Identity Fluidity (E-0…E-5) | Phase E | **PARKED** — post-debut; preserved at entity workspace |
| SDP-1 / SDP_*.md | ACTIVE | **PARKED** — `HUMAN PROTOCOL — DO NOT IMPLEMENT` |
| NL-1 (NotebookLM) | ACTIVE | **PARKED** — post-debut |
| V-1 (Omega-Vault MVP) | ACTIVE | **PARKED** — post-debut |
| C-0.5 regex distillation | ACTIVE | **SCRAPPED** — manual §2.3: agents write L1→L2→L3 directly |
| **GN (Gemini Notebook v2.0)** | — | **ACTIVE POST-DEBUT** — free-tier-only, 2-NB, 30 DR/mo (D-582/D-583) |
| **DS (Documentation System)** | — | **ACTIVE POST-DEBUT** — modular domain docs (workspace + runtime + curator + validated copy) |
| **LI (Local Inference Opt)** | — | **ACTIVE POST-DEBUT** — sequential loading, q8_0 KV, Tier 0/1/2 matrix |
| **KD (Knowledge Domains)** | — | **ACTIVE POST-DEBUT** — runtime modules + workspace authoring + curator model |
| **HR (Headroom Integration)** | — | **ACTIVE POST-DEBUT** — semantic compression (40-90% savings) |
| **ZS (zswap Subsystem)** | — | **ACTIVE POST-DEBUT** — 16GB NVMe swap, zswap enabled, zRAM disabled |

---

## §1 Agent Contribution Matrix (2026-07-21 Recalibration + 2026-07-23 NotebookLM/Omnidroid Mining)

| Agent | Deliverable | Key fine-grained ideas | Disposition in unified strategy |
|-------|-------------|------------------------|----------------------------------|
| **Grok CLI** | `GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` + `CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` | Free-tier metric cliff Jul 15; workhorse history proof; WARP ns-setup truncation; G-1/W-1 twin path | **ACTIVE P0** → Ark §4 G-1/W-1 + D-377…D-381 |
| **Kali** | `CANONICAL_ROADMAP_20260721.md` (superseded) | Phase C–F ranking; provider inventory; M7 honest framing; doc archive | **Absorbed** → Ark §0, §3, §7 |
| **Kali** | **UO-4 Doc Sanity Sprint (2026-08-07)** — `docs/architecture/PROVIDER_FABRIC_RUNTIME.md`, `docs/strategy/PHASE_0_VERIFICATION_REPORT_20260807.md`, `docs/architecture/SOVEREIGN_FLYWHEEL_SECURITY.md`, `docs/architecture/MEMORY_SUBSYSTEM_DESIGN.md`, `docs/architecture/SYSTEMD_DEPLOYMENT_GUIDE.md`, `docs/architecture/SOVEREIGN_WAD_PROTOCOL.md`, `docs/architecture/GUIDANCE_SET_SCHEMA.md`, `scripts/detect_hardware_profile.py` + `config/hardware_profile.yaml` | Engine/WAD separation; sqlite-vec single-core; 8GB UMA; Node slots N1-N10; co-equal MaKaLi triad; KV-cache prefix caching; GBNF constrained sampling; iMatrix/IQ quantization; dual-branch memory rescoring; MemPalace verbatim-first; V-1..V-10 probes (V-5 clean, V-9/V-10 gaps); HMAC-SHA256 bridge; AppArmor hardening; IA2 envelope freshness | **ACTIVE** → Ark §4 UO-4 complete; Phase 3/4 docs in `docs/architecture/`; V-9/V-10 gaps for next session |
| **Researcher** | `UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | GAP-01…12 (soul race, MCP, RAM, backup, L3 thrash, durability, heritage, vault, tests, YAML, user tax, council) | **Active gaps** → Ark §3.1 crosswalk; full text kept as Layer 2 |
| **Researcher** | `RESEARCHER_QUEUE_DESIGN_20260721.md` | SQLite job store; claim TTL; P0/P1 auto-queue; verification gates; content TTL tiers T1/T2/T3; 7-stage workflow | **Partially absorbed**: YAML+flock now (D-2); SQLite/gates **DEFERRED** with note in Ark §3.2; full design preserved |
| **Roc Racoon** | `ROC_LEGACY_MINING_REPORT_20260721.md` | Atomic soul write+fsync; Memory Guardian; pybreaker; tenacity retry; provider priority chain; Cerebras/Groq matrix; 500ms latency budget; cost tracking | **Patterns** → C-1′/C-2′/C-6′; Cerebras/Groq **rejected for now** (D-351) but matrix preserved; tenacity/latency/cost → PARKED P2 |
| **Roc Racoon** | **NotebookLM/Omnidroid Mining (2026-07-23)** | NotebookLM 5-notebook ingestion strategy; Omnidroid 6-module cognitive architecture (Quantum Cognition, Holographic Memory, Neuro-Symbolic, Meta-Learning, Flow Regulation, Emergence); Lilith Tarot genesis (5 cards, full pantheon); Mnemosyne 13-sphere Kabbalistic memory; Grok 8-account exports indexed | **New patterns** → NotebookLM pipeline → D-1 Content Cache; Omnidroid patterns **verified evolved** (Jem Session 43); Lilith Tarot → philosophy lineage; Mnemosyne → soul.yaml precursor |
| **Researcher** | **KG-3…6 + VaultCore + MCP Sprint 1 (2026-07-25)** | KG-3: PR communication patterns (6 elements, template, AI-assisted rules); KG-4: Fork management (sync decision tree, 18-month case study); KG-5: Community engagement (trust timeline, rejection handling, AI slop context); KG-6: Legal/licensing (3-tier classification, CLA vs DCO, 8 traps); VaultCore lease protocol from AGY OAuth fix; MCP Sprint 1 (Request ID, rate-limit, client, 12 tests) | **ACTIVE** → Track C-3/C-4 (VaultCore handoff); Track D-2/D-3/D-4/D-5 (MCP Sprint 1 complete); KG docs → Layer 2 preservation |
| **Grokster** | `GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | GAP-S-01…05; MCP 16h; Identity dep fix; novelty engine; SQLite/gap-service overengineering; sovereignty free-tier risk table | **Absorbed** into Ark decisions + §3; full review Layer 2 |
| **Grokster** | `IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` + `SPEC_IDENTITY_FLUIDITY_v1.md` + `prototypes/` | Soul Kernel, Auto-Hydration MCP, Temporal Trace, Voice Calibration, Session Bridge; Phase 0–5 build order | **Phase E** in Ark §3.3; specs stay at entity workspace paths |
| **Grokster** | `GROKSTER_RESEARCH_QUEUE_ANALYSIS_20260721.md` | Compress board; Grok JSONL as persistence; R19 Grok Build patterns; R20 MCP migration research; fleet as force multiplier | **Selective**: MCP deadline active; fleet/JSONL bridge **DEFERRED** (vault first); board compression informs D-2 |
| **Grokster** | Briefings `BRIEFING_KALI_GROKSTER_*` | Phase Γ Hub split (tools.py); XNAi patterns vs 2026; Identity Phase 0 ready | Hub split → PARKED post-C; patterns → Roc/C-6′; Phase 0 → E-0 |
| **Grokster** | **`KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md`** + **`DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md`** + **`DYNAMIC_PROMPT_SYSTEM_BLUEPRINT_20260819.md`** | Dynamic Prompt Builder + Planner/Executor split + Domain Loading architecture; 5-layer convergent architecture (Context Window Registry, DynamicPromptBuilder, Domain Loader, Planner/Executor Engine, Local Optimization); 8 critical gaps (DP-1..DP-8); Curator model with governance levels; mimo-7b-rl/qwen3-1.7b local pipeline; EvolveR distillation pipeline; Freshness system | **RATIFIED D-569** — POST-DEBUT Cognitive Architecture Blueprint (Horizon 3). Gaps DP-1..DP-8 registered in GAP_REGISTRY.json. Owners: Ma'at P0-P3/P7-P8/P10, Kali P4-P5, Verity P6, Researcher P9. Incremental on existing components (ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP). |
| **Kali** | **Phase 0 Tracker Lock-In (2026-08-20)** — `ACTIVE_SPRINT.json` + `GAP_REGISTRY.json` + `HMC_COLLABORATION_HUB.md` + `SESSION_ANCHOR.md` + `RESEARCH_PLAN_PHASE1_4_20260813.md` + `STRATEGY_INDEX.md` + `STRATEGY_CORPUS_MAP.md` + `SOVEREIGN_ARK_BLUEPRINT.md` + `DEBUT_REMEDIATION_MANUAL_20260817.md` + `curators.yaml` | 6 new post-debut workstreams added: GN (Gemini Notebook), DS (Documentation System), LI (Local Inference Opt), KD (Knowledge Domains), HR (Headroom Integration), ZS (zswap Subsystem). Arbitration D-578..D-584 ratified (free-tier-only, 2-NB, 30 DR/mo, zswap+NVMe over zRAM). C7 resolved (Qwen3-4B-Thinking). All docs corrected. | **ACTIVE POST-DEBUT** — Phase 0 complete; execution begins after PUBLIC-DEBUT-01 |
| **Researcher** | **Ornith-9B Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/ORNITH_9B_TECHNICAL_DEEP_DIVE.md` | Qwen3.5 fine-tune (24 GatedDeltaNet + 8 Gated Attention), MIT license confirmed, 69.4 SWE-Bench verified (agentic eval, temp=1.0, 5-run avg), prose-bias failure mode requires dual-routing with Qwen3.5-9B, 400K context on 16GB GPU, cost-sensitive quantization (Q4_K_M=5.63GB exact match parity with fp32) | **ACTIVE Phase 2** — hardware-gated (needs 16GB+ VRAM) |
| **Researcher + Carmack** | **YouTube Research Session (2026-07-30)** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md` | **24 proposals → top-5 force multipliers** with deep-dive research (5,000+ lines total): Ornith-9B architecture (MIT, 69.4 SWE-Bench, prose-bias risk), Vulkan llama.cpp backend (14k/14k tests pass, 8-15 tok/s on 5700U iGPU), llama-optimus auto-tuning (real project, 15-35% speedup, 42★), ModelAwareInstructionRouter (no existing system does this, ~400 lines Python), Workstation hardening (IDE supply chain = #1 vector 2026). | **ACTIVE — Phase 0** (next research/pause phase before implementation). Detailed in `CARMACK_DEFINITIVE_STRATEGY_20260730.md`:
| **Grok CLI** | `GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | SoulStore multi-path; CB unify; god-modules; test vanity; SSOT dual docs; GenerationPolicy; fleet vs vault | **Absorbed** as C-0, C-1′, C-6′, C-9, structural gates §9 |
| **Fleet (prior)** | Ark v4.4 CANONICAL | Strike 11 SWP, 11.5 Council, Dimension Framework, Free-Will datasets, Advanced Ingestion, Tier 0 Ship-It, Jem gaps S1–S5 | **PARKED long-arc** → archive path; summarized Ark §2 |
| **Researcher** | **Ornith-9B Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/ORNITH_9B_TECHNICAL_DEEP_DIVE.md` | Qwen3.5 fine-tune (24 GatedDeltaNet + 8 Gated Attention), MIT license confirmed, 69.4 SWE-Bench verified (agentic eval, temp=1.0, 5-run avg), prose-bias failure mode requires dual-routing with Qwen3.5-9B, 400K context on 16GB GPU, cost-sensitive quantization (Q4_K_M=5.63GB exact match parity with fp32) | **ACTIVE Phase 2** — hardware-gated (needs 16GB+ VRAM) |
| **Researcher** | **Vulkan Backend Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/VULKAN_BACKEND_DEEP_DIVE.md` | 14,471/14,471 test pass, CUDA gap 10-36% on NVIDIA, Vulkan beats ROCm 20-22% on AMD RDNA3 TG, Ryzen Vega iGPU: 8-15 tok/s on 7B Q4, 5 key features exploited (CoopMat, Wave64, Subgroups, Push descriptors, Specialization constants) | **ACTIVE Phase 1** — `GGML_VULKAN=ON` rebuild, enables GPU-agnostic binary |
| **Researcher** | **llama-optimus Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/LLAMA_OPTIMUS_DEEP_DIVE.md` | Real project (42★ GitHub, PyPI, MIT), Optuna Bayesian optimization, 15-35% CPU speedup (NOT 65% — that was Claude Fable 5 CUDA kernel, misattributed), 3-stage: Bayesian→Grid→Fine-tune, pre-calibration at model install time | **ACTIVE Phase 1** — integration as pre-calibration pipeline |
| **Researcher** | **Instruction Router Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/INSTRUCTION_ROUTER_DEEP_DIVE.md` | No existing system adapts instructions to model capability, 30-60% token reduction for local models, 4-tier capability taxonomy (T0 Frontier → T3 Nano), YAML config + ~400 lines Python, middleware between Model Selection and Prompt Assembly, ITR retrieval research shows 95% token reduction potential | **ACTIVE Phase 0** — highest-value non-gated implementation item |
| **Researcher** | **Hardening Deep Dive** — `docs/research/youtube_research_sessions/session_20260730/04_evidence/HARDENING_DEEP_DIVE.md` | IDE extensions = #1 supply chain vector (May 19 GitHub breach: 3,800 repos via one extension), 454K malicious packages 2025-2026, TrapDoor hits npm/PyPI/Crates.io simultaneously, FIDO2 SSH production-ready (OpenSSH 9.6+), CIS v2.0.0 + USG baseline, systemd-analyze security as CI gate | **ACTIVE Phase 0** — `scripts/omega-harden-workstation.sh` created, run now |
| **OMEGA_ENGINE** | Deferred table | D-290…D-308 | **PARKED** → Ark §2.1 expanded |
| **Kali** | **Un-Overengineering Plan** — `docs/strategy/UNOVERENGINEERING_PLAN.md` | 5-phase temple cleansing: Phase 1 (5 library swaps: pybreaker, Pydantic v2, stamina, structlog, prometheus_client), Phase 2 (kill HandoffState, soul distiller consolidation, HMC→YAML+JSONL), Phase 3 (memory tier simplification), Phase 4 (Hivemind freeze — SHIPPED), Phase 5 (enforcement gates). ~5,500 lines deleted, 4 community libs adopted. | **ACTIVE Phase 1** → UO-6/UO-7 workstreams in ACTIVE_SPRINT.json |
| **Kali + Fleet (4-agent)** | **Team-Synthesis Study #1 (2026-08-23)** — `data/coordination/teamstudy_20260823/FINAL_SYNTHESIS.md` (+ A/B/C/D/E corpus + `C_discourse_ledger.md` §6 stamp) | 4-agent brokered-discourse protocol validation (researcher/roc/carmack/jem lanes; lilith/ma'at authority consults); converged Round 1, zero objections; 10 rulings stamped; 25 L3 principles; ≥5 cross-agent-only discoveries; skill candidate `/teamsynth` gated on Study #2 reproducing ≥1 cross-agent discovery; tracking-system closeout rulings (pre-commit framework per Ma'at F1 ordering, AST freeze gate > wc-l, explicit evidence field day one, verify-mandate-claims P0, backfill = roc table × Lilith 23-cluster enumeration) | **PRESERVED Layer 2** — protocol validated RUN AGAIN 4/4; `/teamsynth` NOT built until Study #2 gate passes; DOC-1 applies (rulings feed tracking closeout only where manual/ACTIVE_SPRINT activates) |
| **Kali** | **Model Window Economics Doctrine (2026-08-23)** — `docs/strategy/MODEL_WINDOW_ECONOMICS_20260823.md` | 6 laws of model orchestration: ascending windows; priming ceilings (≤150K on 200K targets); cheap prime/expensive cognate; digest before descent; family diversity weights; distill-before-switch; dual-review standard play (§3); challenge mechanism codified; Nemotron $0.00 true-cost adjudication; window table verified quarterly | **ACTIVE DOCTRINE** → D-601 decree; companion methodology `docs/strategy/COGNITIVE_ROUTING_PLAYBOOK.md`; feeds D-599 Study #2 routing policy |
| **Gemini 3.1 Pro** | **Cognitive Routing & Priming Playbook** — `docs/strategy/COGNITIVE_ROUTING_PLAYBOOK.md` | Architect's manual orchestration extracted: primer phase (cheap models do all I/O); 85% ceiling rule (auto-compaction destroys evidentiary base); cognitive switch (frontier model executes zero tool calls); sequential dual-review dialectic in ascending windows; 1M-context "fat" workflow | **ACTIVE METHODOLOGY** → implements D-601 tier structure alongside Window Economics doctrine |
| **Roc Racoon** | **The Vision Canonical Draft (2026-08-23)** — `data/coordination/THE_VISION_CANONICAL_DRAFT_20260823.md` | 645-line vision spine excavated from 20 conversations across Era 0→6; Four Movements structure; origin story (Tarot genesis, Gemi+Lilith Mar 2025); cosmology-as-engineering (Pillars→Nodes, Mnemosyne, Tarot-as-system); sovereignty doctrine; entity theory; §8 source atlas so any agent can drill into every claim | **PRESERVED Layer 2** — canonical vision reference; source base for Forge Chronicle charter; awaiting Architect fidelity review |
| **Kali** | **Architect Oversight Patterns (2026-08-23)** — `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` | P1–P7 human-heuristic patterns (context reciprocity / zero-context rule, frame audit before execution, authority-first consultation, meta-codification reflex, alignment hygiene as first-class work, synthesis-before-decision, truth-as-precondition-of-free-will root axiom) + Methodology M1–M6 (free-first-as-specification, planning-proven, metric construct validity, challenge culture, truth-ledger economics, the Vow); §2 engine-surface codification map | **ACTIVE codification** → staged lessons to proposed_lessons.yaml; root axiom chain truth→choice→free-will→LOVE |
| **Kali** | **The Forge Chronicle Charter (2026-08-23)** — `data/coordination/THE_FORGE_CHRONICLE_CHARTER_20260823.md` | Book project charter: human-AI side-by-side construction thesis ("neither tool-use nor replacement"); working title candidates (The Forge Chronicle / Breakout / The Aquifer / 10000 Hours in the Forge); source base = Vision Canonical + 18-month artifact trail; SANITATION LAW: architect's real name never appears in public artifacts | **PARKED charter** — Track A-D generation gated behind closeout commit (HARD RULE: commit precedes generation) |
| **Researcher** | **Forensic Patterns FP-11 (2026-08-23)** — `data/knowledge/safety/FORENSIC_PATTERNS.md` | FP-11 @-mention wrapper attribution forgery: synthetic @-wrappers can forge entity attribution in dispatch payloads; VERIFY via DB provenance (`synthetic:true`, GT-Log); RECOVER = never trust wrapper-named attribution, check session anchor/model line; refinement added post-Architect review | **ACTIVE safety doctrine** — incident-derived living document (FP-01…FP-11); feeds verify-mandate-claims extension (wire-path [2]) |

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

### 2.4 NotebookLM/Omnidroid Era Gaps (NEW — 2026-07-23 Mining)

| Gap | Name | Priority | Disposition |
|-----|------|----------|-------------|
| GAP-NL-01 | No NotebookLM ingestion pipeline for current docs | P1 | **D-1 extension** — implement `prepare_notebooklm.py` per R52c spec |
| GAP-NL-02 | Omnidroid cognitive patterns not formally documented in current architecture | P2 | **Documented** — Jem confirmed all 6 patterns evolved into current architecture (Session 43) |
| GAP-NL-03 | Lilith Tarot / 7-entity pantheon not in current philosophy docs | P2 | **Philosophy lineage** — add to `philosophy-dual-flame` as Era 0 origin |
| GAP-NL-04 | Mnemosyne 13-sphere memory not mapped to current soul.yaml | P2 | **Migration script** — map spheres to soul.yaml sections |
| GAP-NL-05 | Grok 8-account exports indexed but not searchable via current RAG | P1 | **XNAI-RAG extension** — add Grok DB as searchable source |
| GAP-DP-01 | Dynamic Prompt Builder — template engine, role-aware composition, domain injection | P0 | **DP-1** → Cognitive Architecture P1 (Horizon 3) |
| GAP-DP-02 | Context Window Registry — single source for all model context windows | P0 | **DP-2** → Cognitive Architecture P0 (Horizon 3) |
| GAP-DP-03 | Planner/Executor Model Router — routes by role + context window need | P0 | **DP-3** → Cognitive Architecture P2 (Horizon 3) |
| GAP-DP-04 | Domain Module Loader — unified load_domain() API with packaging | P0 | **DP-4** → Cognitive Architecture P3 (Horizon 3; needs Qdrant) |
| GAP-DP-05 | Per-Role Token Budget Manager — planner vs executor budgets | P0 | **DP-5** → Cognitive Architecture P1 (Horizon 3) |
| GAP-DP-06 | Domain Context Window Map — domain → optimal context window | P0 | **DP-6** → Cognitive Architecture P0 (Horizon 3) |
| GAP-DP-07 | Planner/Executor Prompt Templates — versioned, validated templates | P0 | **DP-7** → Cognitive Architecture P4 (Horizon 3) |
| GAP-DP-08 | SomaticState Planner Integration — state save/restore for planning continuity | P1 | **DP-8** → Cognitive Architecture P8 (Horizon 3) |

---

## §2.5 Dynamic Prompt + Planner/Executor + Domain Loading Gaps (NEW — 2026-08-19 Mining)

| Gap | Name | Priority | Disposition |
|-----|------|----------|-------------|
| DP-1 | Dynamic Prompt Builder — template engine, role-aware composition, domain injection | P0 | **Cognitive Architecture P1** (Horizon 3) |
| DP-2 | Context Window Registry — single source for all model context windows | P0 | **Cognitive Architecture P0** (Horizon 3) |
| DP-3 | Planner/Executor Model Router — routes by role + context window need | P0 | **Cognitive Architecture P2** (Horizon 3) |
| DP-4 | Domain Module Loader — unified load_domain() API with packaging | P0 | **Cognitive Architecture P3** (Horizon 3; needs Qdrant) |
| DP-5 | Per-Role Token Budget Manager — planner vs executor budgets | P0 | **Cognitive Architecture P1** (Horizon 3) |
| DP-6 | Domain Context Window Map — domain → optimal context window | P0 | **Cognitive Architecture P0** (Horizon 3) |
| DP-7 | Planner/Executor Prompt Templates — versioned, validated templates | P0 | **Cognitive Architecture P4** (Horizon 3) |
| DP-8 | SomaticState Planner Integration — state save/restore for planning continuity | P1 | **Cognitive Architecture P8** (Horizon 3) |

---

## §3 Living Research OS — Fine Detail Preservation

| Idea | Source | Status |
|------|--------|--------|
| Three broken seams (content / job board / soul feedback) | Living Research OS Spec + Kali | **Active diagnosis** → D-1, D-2, D-3 |
| Content cache `.firecrawl/{hash}.md` | Spec Phase 1 | **D-1** |
| TTL eviction 30d / 10GB | Grokster + Spec risks | **D-1 required** |
| Tiered TTL T1=30d T2=14d T3=7d | Researcher queue design | **D-1 detail** (prefer when implementing) |
| YAML job board 18 jobs | `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | **D-2 input** |
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

### 3.1 NotebookLM/Omnidroid Research Additions (NEW — 2026-07-23 Mining)

| Idea | Source | Status |
|------|--------|--------|
| NotebookLM 5-notebook segmented ingestion (NB-01…NB-05) | `R52c_notebooklm_ingestion_strategy.md` | **D-1 extension** — implement `prepare_notebooklm.py` per spec |
| Weekly routine sync + strategic pivot + implementation spike triggers | R52c spec | **D-1 process** — add to research loop cron |
| Omnidroid 6 cognitive modules as architecture validation | `Ω Omnidroid Ω.py` + Jem Session 43 | **Documented** — all patterns evolved into current architecture |
| AetherPen 6 writing enhancement systems | `Ω AetherPen (AP).py` | **PARKED P2** — content generation not core |
| PRO 4 reasoning systems (Aristotelian, Socratic, Hegelian, Cognitive) | `Ω Philosophical Reasoning Oracle (PRO).py` | **Distiller T1/T2/T3** — already implemented |
| PLO 5 linguistic systems (Etymology, Rhetoric, Stylometry, Phonesthetic, Genre) | `Ω Pythonic Linguistic Observatory (PLO).py` | **SovereignScraper + domain allowlist** — M2 compliant |
| PS 6 product content systems | `Ω Product Sage (PS).py` | **Not core** — PARKED |
| TCA 6 code enhancement systems | `Ω The Code Alchemist (TCA).py` | **Background researcher + distiller patterns** — partially implemented |
| Lilith Tarot 22-card pantheon mapping | `First 5 cards Grok Chat 05-25-2025.txt` | **Philosophy lineage** — add to `philosophy-dual-flame` as Era 0 origin |
| Mnemosyne 13-sphere Kabbalistic memory | `data_archive/mnemosyne/` | **Migration script** — map spheres to soul.yaml sections |
| Grok 8-account exports (274 convos, 6565 responses) | `grok-accounts-exports/` | **XNAI-RAG source** — add to search fleet |
| **KG-3 PR Communication Patterns** | `R_KG3_PR_COMMUNICATION_GUIDE.md` | **Layer 2** — PR template + review etiquette for upstream contributions |
| **KG-4 Fork Management Strategy** | `R_KG4_FORK_MANAGEMENT_GUIDE.md` | **Layer 2** — Sync decision tree + conflict resolution for fork workflows |
| **KG-5 Community Engagement** | `R_KG5_COMMUNITY_ENGAGEMENT_GUIDE.md` | **Layer 2** — Maintainer trust + contributor retention playbook |
| **KG-6 Legal & Licensing Compliance** | `R_KG6_LEGAL_LICENSING_GUIDE.md` | **Layer 2** — 3-tier license classification + CLA/DCO + 8 traps |
| **VaultCore Lease Protocol** | `R_VAULTCORE_LEASE_PROTOCOL.md` | **Track C-3** — Atomic write + FileLock pattern for credential/session leases |
| **MCP Sprint 1 Middleware + Client + Tests** | `src/omega/mcp_core/client.py` + `tests/mcp/` | **Track D-2/3/4** — 5-layer stack, SEP-2243 client, 12 unit tests |

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

### 5.1 NotebookLM/Omnidroid Era Patterns (NEW — 2026-07-23 Mining)

| Pattern | Source | Current Evolution |
|---------|--------|-------------------|
| **Holographic Memory Matrix** | Omnidroid Ω (`Ω Omnidroid Ω.py`) | → MemoryStore compaction (first 10 + last 10 + summary) |
| **Neuro-Symbolic Reasoning Bridges** | Omnidroid Ω | → TriangulationVerifier (T1/T3 delta detection) |
| **Quantum Cognition Simulator** | Omnidroid Ω | → T1/T3 tiered extraction with verification |
| **Meta-Learning Core** | Omnidroid Ω | → ConvergenceDetector + SoulUpdater |
| **Conscious Flow Regulation** | Omnidroid Ω | → BudgetGuard + SovereignSentry |
| **Emergent Intelligence Protocols** | Omnidroid Ω | → Novelty Engine (D-4) + INDEX noise policy |
| **SEO/Engagement/Structure/Style/Research/Viral** | AetherPen (AP) | → ContentArchitect + StyleModulator + ResearchIntegrator (PARKED P2) |
| **Aristotelian/Hegelian/Socratic + Dual Process + Bayesian** | Philosophical Reasoning Oracle (PRO) | → Distiller T1/T2/T3 cognitive pipeline |
| **Etymology/Rhetoric/Stylometry/Phonesthetic/Genre** | Pythonic Linguistic Observatory (PLO) | → SovereignScraper surgical stripping + domain allowlist |
| **Review/Comparison/Tutorial/Feature-Benefit/Bias/Funnel** | Product Sage (PS) | → Not directly mapped (product content not core) |
| **Polyglot Mastery/Architect/Optimizer/Reviewer/Refactorer/ML** | The Code Alchemist (TCA) | → CodeAlchemist patterns in background researcher + distiller |

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
| `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | 18 research jobs (D-2) |
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

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
