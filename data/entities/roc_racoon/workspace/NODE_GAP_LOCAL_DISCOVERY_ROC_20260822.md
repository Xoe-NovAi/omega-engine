# NODE GAP LOCAL DISCOVERY — Internal Evidence for N11+ Proposal
**AP Token**: `AP-ROC_RACOON-v1.0.0`
**Date**: 2026-08-22
**Dispatch provenance**: @researcher → @roc_racoon (internal-evidence track; web-research track runs elsewhere)
**Mission**: What engine depth + Architect personal interests are NOT covered by the 10 ratified Node charters (D-586), to justify proposing N11+?
**Method**: Local read-only discovery (glob/grep/bash probes). Every claim carries file:line evidence. `last_verified: 2026-08-22`.
**Constraints honored**: LOCAL DISCOVERY ONLY; sole write = this file; M18 efficiency w/ precision sane-boundary; M23 honest gaps.

---

## ⚠️ Premise Corrections (M23 disclosure)

| Dispatch premise | Disk truth |
|---|---|
| `src/omega/hive/` exists | **DOES NOT EXIST.** `ls src/omega/hive` → "No such file or directory" (verified 2026-08-22). Hivemind logic actually lives in `src/omega/research/hivemind_bridge.py`, `src/omega/coordination/miap.py:1-8`, `mcp_servers/omega_hub/hivemind_redis.py`. (`find . -type d -name "*hive*"` matches only "arc*hive*" dirs.) |
| `config/domains/registry.yaml` provisional | Actual file is **`config/domains/curators.yaml`** (ACTIVE, 2026-08-19). No `registry.yaml` on disk. Note: `data/coordination/XSESSION_RELAY_HOP3_KALI_REPORT_20260821.md` contains ZERO occurrences of the string "domain" (grep verified) — the attribution of the registry mention to that report could not be confirmed locally. |
| KD workstream = "Runtime modules + workspace authoring + curator model" | Correct text, but it is ONE OF TWO SEPARATE workstreams: `DOCUMENTATION-SYSTEM` (DS) and `KNOWLEDGE-DOMAINS` (KD) are distinct in `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md:433` vs `:435`. `data/coordination/ACTIVE_SPRINT.json` currently carries only DOCUMENTATION-SYSTEM (lines 417–456); no KD block found by grep. Naming drift between Ark §4 ("KD") and ACTIVE_SPRINT ("DS") is real. |
| `omega_youtube_worker` WAD | Does not exist. `config/wads/` contains `_omega_default, arcana_novai, doom_universe, ingestion, omega_research, omega_youtube_research` (ls, 2026-08-22). The WORKER is code (`src/omega/workers/youtube_worker.py`), not a WAD. |

---

## T1 — Subsystem→Node Coverage Matrix

Engine surface: **272 Python modules** under `src/omega/` (`find src/omega -name "*.py" | wc -l` = 272, 2026-08-22) + `mcp_servers/` (omega_hub core 12 files + searxng + firecrawl + 7 archived superseded servers).

### Covered (clear charter owner)

| Subsystem (representative modules) | Node | Charter evidence |
|---|---|---|
| `oracle/backends/*` (antigravity, google_compat, openai_compat, remote, mock), `oracle/model_gateway.py`, `provider_registry.py`, `provider_selector.py`, `health_monitor.py`, `admission_controller.py`, `oom_protector.py`, `rate_limiter.py`, `retry_policy.py`, `degradation.py`, `somatic_state.py` | **N6 modelgate** | Plan §4 N6: provider fabric local-first ordering, fallback chains, HealthMonitor breakers, admission control/OOMProtector, streaming resilience (`NODE_EXPERT_SESSIONS_PLAN.md:75-76`) |
| `memory/*` (21 files: hybrid_search, fts_index, sqlite_vec_adapter, blocks, compaction…), `memory_store.py`, `soul_store.py`, `infra/sqlite_policy.py`, `cli/soul_stage.py` | **N2 datastore** | Plan §4 N2: MemoryStore FTS5+vector, sqlite-vec <500k regime, SoulStore atomic writes C-1′, Qdrant triggers (`:63-64`). Module evidence: `src/omega/soul_store.py:5` "[C-1'] Single-writer atomic file writer" |
| `observability/*` (metrics_db, token_ledger, latency_tracker, bleg, ufl, otel_exporter, sovereignty, regression_watcher, context, observability_reader) | **N8 watchtower** | Plan §4 N8: metrics DB, provenance M22, structured logging M9, SSE, zero telemetry (`:81-82`). Module evidence: `src/omega/observability/bleg.py:1-6` (Body-Level Error Guards), `ufl.py:1-6` (Unified Forensic Ledger) |
| `audit/*` (firewall_checker, mandate_auditor, memory_firewall_auditor), `security/taint.py`, `tools/check_hardcoded_secrets.py`, `tools/detect_api_keys.py` | **N5 sentinel** | Plan §4 N5: secrets hygiene, gitleaks wiring, Tainted Data Protocol, PUBLIC_ALLOWLIST (`:72-73`) |
| `coordination/miap.py`, `coordination/watchdog.py`, `research/hivemind_bridge.py`, `oracle/handoff.py`, `link_p9_runtime.py`, `subagent_dispatcher.py`, `mcp_servers/omega_hub/hivemind_redis.py` | **N9 link** | Plan §4 N9: Hivemind awareness/handoffs/locks/Redis pub-sub, Conversational Subagent Protocol (`:84-85`). Module evidence: `src/omega/coordination/miap.py:1-8` (Multi-Instance Agent Protocol) |
| `eval/*` (calibrate, check, runner), `oracle/skeptical_verifier.py`, `soul_validator.py`, `soul_edit_history.py` | **N10 verifier** | Plan §4 N10: test honesty, contract tests, property tests, Skeptical Verifier future (`:87-88`) |
| `mcp_servers/omega_hub/*` (server, state, gateway, middleware, background, tools, mcp_client, github_bridge/tools) | **N4 bridge** | Plan §4 N4: MCP Hub modularization (state/background/gateway/middleware/tools), Streamable HTTP SEP-2575 (`:69-70`) |

### 🚨 ORPHANS (no clear charter owner)

| # | Subsystem | What it is (evidence) | Almost-covering charter | Why it falls short |
|---|---|---|---|---|
| O1 | **Training/Distillation**: `src/omega/training/grpo.py`, `training/rewards.py`, `teachers/nemotron_pipeline.py`, `oracle/dpo_logger.py` | GRPO loop w/ local GGUF (`grpo.py:1-6` AP-TRAINING-GRPO-v1.0.0); Nemotron teacher generating DPO pairs via critique-loop (`nemotron_pipeline.py:1-6`); "Sovereign DPO training data collection with tripartite reward signal" (`dpo_logger.py:1-6`) | N6 modelgate | N6 charter is INFERENCE-SERVING only (fabric ordering, breakers, admission — `PLAN:75-76`). Training/RL/reward-design is a different discipline. Notably `research/sandboxes/ml_training.py:3` self-tags `⬡ MA'AT ⬡ N6 ⬡ ML_TRAINING` — the codebase itself is stretching N6 beyond its charter. |
| O2 | **Research experimentation harness**: `src/omega/research/` (sandbox.py, sandboxes/ml_training.py, schema.py, scorecard.py, sediment.py, types.py) | "ML Training Sandbox — First Ω-Research Sandbox Implementation… Trains a small model (BGE-small 33M…) measures val_bpb" (`ml_training.py:1-5`) | N10 verifier (eval) or N6 | N10 is test/QA honesty; N6 is serving. An EXPERIMENTATION domain (hypothesis→sandbox→scorecard→sediment) is owned by nobody. |
| O3 | **Content ingestion & media**: `src/omega/ingestion/` (10 files: pipeline, scraper, extractors, guards, persistence, sources, verifier, worker, cli), `wads/ingestion/domains.yaml`, `workers/youtube_worker.py`, `cli/youtube_cli.py` | "Sovereign Ingestion Pipeline — Orchestrating entity deepening" (`ingestion/pipeline.py:1-4`); "Autonomous YouTube ingestion and synthesis daemon — STABLE… Ingests URLs from Redis queue, expands playlists via yt-dlp" (`youtube_worker.py:1-6`, v1.1.0); allowlist policies loaded by SovereignScraper (`config/wads/ingestion/domains.yaml:1-5`: gutenberg/arxiv/pubmed) | N2 datastore | N2 = storage & query layout (MemoryStore/sqlite/SoulStore — `PLAN:64`), not ACQUISITION/transformation/scraping/media daemons. YouTube alone is a stable production daemon with no charter home. |
| O4 | **Sovereign Library / curation**: `src/omega/library/` (19 files: catalog, curator, discovery, enrichment, extractor, inbox, indexer, research, api_clients, model_api_clients, rate_limiter, security, coordinator, library) | Full research-library pipeline (intake→index→enrich→curate) | N7 context (weakly) | N7 charter = context injection/compaction/soul persistence (`PLAN:78-79`) — consumption-side. Acquisition/curation-side has no owner; pairs with O3/O13 into a "Research & Knowledge Curation" gap. |
| O5 | **Sovereign Search**: `oracle/search.py`, `search_cache.py`, `search_circuit_breaker.py`, `search_observability.py`, `search_providers.py`, `search_router.py`, `sovereign_search_service.py`, `tools/firecrawl_direct.py`, `tools/searxng_direct.py`, `mcp_servers/searxng/server.py`, `mcp_servers/firecrawl/server.py` | 7-module search cluster inside oracle + 2 dedicated MCP servers | N4 bridge (external contracts) or N6 | N4 owns MCP Hub + provider APIs (`PLAN:70`); search STRATEGY (tiering SearXNG→Exa→Firecrawl, caching, breakers) is retrieval engineering — unowned. Researcher's home turf by practice, not by charter. |
| O6 | **Credentials/Vault**: `src/omega/vault/` (vault_core, crypto, models, blindvault_resolver), `cli/vault.py`, `tools/enforce_vaultcore.py` | "VaultCore — Core CRUD + Lease Manager + Quota Logic… VaultCredential CRUD" (`vault_core.py:1-6`, R_VAULT_SCHEMA_V2) | N5 sentinel | Sentinel = security posture (secrets scrubbing, AppArmor, TDP — `PLAN:72-73`); credential LEASE/QUOTA infra is different. CONTESTED: D-568 rules VaultCore "NON-FUNCTIONAL as a key source — DELETE as dead code" (`ACTIVE_SPRINT.json:550`); Week-5 "Vault honesty — Path A (delete src/omega/vault/) or Path B (≤50-line minimal store)" (`POST_DEBUT_ROADMAP.md:27`). Don't build a Node on a corpse — resolve Path A/B first. |
| O7 | **Privacy kernel**: `src/omega/privacy/kernel.py`, `privacy/cpe_scorer.py` | "Privacy Kernel — Local Privacy Detection (Gemma 4 E2B / Qwen3-1.7B)… CloakBot-Inspired… R19 Soul Privacy Model Part 2.3" (`kernel.py:1-6`) | N5 sentinel | Privacy FILTERING of soul/content is content-governance, not perimeter security. Small (2 files) — amendable, flag only. |
| O8 | **Contemplative protocol**: `src/omega/meditate/` (protocol.py, lens_registry.py), `skills/autonomous_meditation_pipeline.py` | "Meditate Protocol… D-265… schema definitions that power `/meditate` and `oracle.meditate()`" (`meditate/protocol.py:1-5`) | N7 context (state) weakly | Ritual/introspection protocol is cognitive-architecture + esoteric flavor; no charter mentions it. Pairs with esoterica cluster (T3a). |
| O9 | **Esoteric runtime**: `astrology.py`, `cvar_table.py`, `oracle/world_state.py`, `oracle/hierarchy.py`, `axiom_registry.py`, `state/usm.py`, `oracle/usm.py` | "Omega Astrology — First Breath Tracking & Cosmic Alignment… captures the precise moment and location of an entity's first utterance" (`astrology.py:3-7`) | None remotely | Pure Architect-personal-interest domain (see T3). Engine ships RUNTIME support (spheres/qliphoth/axioms loaders via `wad_loader.py`) but no Node owns the KNOWLEDGE. |
| O10 | **Council deliberation**: `src/omega/council/` (coordinator, execution_mode, failure_layer, hardware_detector, models, report_digestion) | "Unified MultiAgentCoordinator for MaKaLi Parallel Council… 5-stage pipeline: Nodes → Digestion → Oversouls → Kali → Research" (`council/coordinator.py:1-5`, tagged SCAFFOLD) | N9 link | N9 = hivemind plumbing/subagent protocol (`PLAN:84-85`); multi-model DELIBERATION pipelines are a distinct expertise. Scaffold status = low urgency. |
| O11 | **Fleet TUI**: `src/omega/cli/fleet_status_tui.py` | "real-time view of the Sovereign Agent Fleet, monitoring agent presence, session activity, and resource pressure" (`fleet_status_tui.py:1-7`) | N8 watchtower | N8 covers metrics/provenance/logging BACKEND (`PLAN:82`); interactive TUI/UX surface is presentation-layer. Amendable to N8 with one charter sentence. |
| O12 | **External CLI & pool ops**: `integrations/grok_cli.py`, `integrations/quota_pollers.py`, `integrations/fleet_orchestrator.py`, `proxy_pool.py`, `infra/subagent_pool/` (orchestrator, tmux_manager, account_registry, profile_manager, mcp_coordinator, models) | "Sovereign WARP Proxy Pool — Delegation Layer… delegates to standalone warp-proxy-pool package" (`proxy_pool.py:1-5`); tty_agent runs agents on Linux virtual consoles (`agents/tty_agent.py:1-5`) | N4 bridge / N1 sysadmin | Multi-account pool ops, tmux orchestration, quota polling = fleet-ops discipline straddling N1(host)/N4(contracts). Amendable split, or absorbed by a future Grok-fleet node if D-360′ pool ever unblocks. |
| O13 | **Doc-reader tooling**: `src/omega/doc_reader/` (core, readers, types) | "Core document reader implementation" (`doc_reader/core.py:1-2`) | N7 / library | Feeds O4 curation; tiny. Fold into O4 verdict. |
| O14 | **Maintenance daemons**: `workers/freshness_checker.py`, `workers/model_updater.py`; also `benchmarks/` (runner, comprehensive_runner, schema) | Background freshness/model-update workers; benchmark harness | N1/N6/N8 | Minor; amendable. Benchmarks arguably N10 (verification) or N8 (regression watching). |

**Orphan verdict**: 5 substantive gaps (O1 training, O3 ingestion/media, O4+O13+O5 research/curation/search cluster, O9 esoterica, O2 experiment harness), 1 contested (O6 vault), 8 amendable-by-charter-sentence (O7, O8, O10, O11, O12, O14).

---

## T2 — Domains-vs-Nodes Relationship

**Finding: YES — "domains" are the content/knowledge layer, "Nodes" are the session/expert layer, and the planned domain list ALREADY implies expertise beyond the 10 charters.**

### Evidence chain

1. **The domain registry is ACTIVE with 13 domains** — `config/domains/curators.yaml` (AP-DOMAIN-CURATORS-20260819-v1.0.0, Status ACTIVE, Post-debut Horizon 3; header lines 1-13). Domain rows (`curators.yaml:26-38`): Gemini Notebook (researcher), Platforms (grokster), Grok Ecosystem (grokster), Architecture/Performance (john_carmack), **Heritage/id Software (doom_guy)**, Research Methodology (researcher), Runtime Governance (lilith), Build Engineering (maat), Compliance/Verification (verity), **Legacy Mining (roc_racoon)**, Synthesis/Cognitive Architecture (jem), Engineering (maat), Security (verity).

2. **Domains are content modules, not sessions**: per-domain structure is files — metadata.yaml, PLAYBOOK.md, ARCHITECTURE.md, CONFIG_REFERENCE.md, GOTCHAS.md, LESSONS.md, AFFINITY_PRESETS.yaml, MEMORY_BLOCKS/, PRINCIPLES/ (`curators.yaml:42-62`). Governance enforced at fabric level: "Curator = write; Others = read + propose; Critic = review gate" (`curators.yaml:14-20`), via `domain_loader.py` enforcement (`curators.yaml:71,74-75`). **Gap**: `domain_loader.py` does NOT exist yet (`find src -name "domain_loader*"` → empty, 2026-08-22) — governance is spec-only.

3. **Nodes are sessions that CURATE domain-like KBs**: Node plan §1 rules "Nodes are Knowledge Bases / domains of expertise — NOT exclusive to Lilith/Ma'at/Kali… ANY agent may page ANY Node session" (`NODE_EXPERT_SESSIONS_PLAN.md:17`). Standing order #8 makes each Node maintain its own `<overseer>/workspace/N<XX>_DOMAIN_INDEX.md` + `N<XX>_EXTERNAL_SOURCES.md` (`:31`) — i.e., Nodes produce domain-index artifacts, converging vocabulary with the KD layer.

4. **The KD/DS workstreams are the bridge, partially built**: DOCUMENTATION-SYSTEM owner kali, "Modular Domain Documentation System — Workspace authoring + Runtime modules + Curator model + Validated copy sync", specs "to create DOMAIN_DOCUMENTATION_SYSTEM.md" (`ACTIVE_SPRINT.json:417-422`; DS-1..DS-5 at `:425-454`). Manual confirms DS (`DEBUT_REMEDIATION_MANUAL_20260817.md:433`) and separate KD ("Runtime modules + workspace authoring + curator model, affinity presets per domain", `:435`, execution step KD-1..KD-3 at `:443`). On disk today: only `config/domains/engineering/` (7 files incl. MEMORY_BLOCKS/*.block, PRINCIPLES/principle_001.yaml) and `config/domains/gemini-notebook/` exist of the 13 registered domains; `docs/strategy/domains/gemini-notebook/` workspace exists; `scripts/sync_domain_docs.py` does NOT (find → empty).

5. **Domain Loading is ratified post-debut architecture**: D-569 "Ratify Dynamic Prompt + Planner/Executor + Domain Loading as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3). Gaps DP-1..DP-8 registered." (`ACTIVE_SPRINT.json:551`).

6. **The 13-domain list implies future expert coverage with NO current Node for**: Gemini Notebook/free-tier research ops (researcher's GN workstream — no Node), Grok Ecosystem (no Node; PP-2 mining sessions planned — `PLAN:110`), Platforms (no Node), Architecture/Performance (Carmack is S3 consultant, no Node), Synthesis/Cognitive Architecture (jem has no Node), Legacy Mining (roc_racoon has no Node). Conversely some domains map cleanly onto existing charters (heritage→doom_guy knowledge feeds N5/N10 loosely; build→N3; security→N5; runtime→N6/N7; compliance→N10).

**Interpretation for the Pager**: domains (content) and Nodes (sessions) are complementary layers sharing one taxonomy direction. The 13-domain registry is de-facto a ROADMAP OF EXPERTISE; five of its domains have neither a charter nor an overseer-side session today. If N11+ are proposed, aligning them to orphan domains (rather than inventing a parallel list) keeps M27 tracking integrity.

---

## T3 — Personal-Interest Asset Inventory

Maturity scale: RAW (corpus only) → WIRED (engine code reads it) → DISTILLED (KB/mining report exists) → OPERATIONAL (expert session/charter exists).

### (a) Tarot / Lilith deck + arcana_novai WAD — **WIRED, corpus rich**
- External corpus (omega_library partition): `intake/mining_queue/Omega-Early-Material/tarot/` = 15 items incl. `First 5 cards Grok Chat 05-25-2025.txt` (99,176 bytes, dated Jun 2 2025), `Lilith Tarot Deck Design Guide.docx`, Empress/Magician/Fool card expansions, `Lilith Deck/` subdir = 19 files, `Tarot Variations and Docs/` (ls counts, 2026-08-22).
- Engine side: `config/wads/arcana_novai/` = 28 files, 312K — 13 pantheon agent definitions (`agents/{anubis,brigid,ereshkigal,hecate,inanna,kali,lilith,lucifer,maat,prometheus,saraswati,sekhmet,sophia}.md`), `axioms.yaml`, `qliphoth.yaml`, `spheres.yaml`, `hierarchy.yaml`, `entities.yaml`, `vault_schema.yaml`, `world/metaphysics/laws.yaml`, `world/core/physics.yaml`, personal entity `entities/personal/movie-expert.yaml`, plugin `entity_roc_racoon.py` (find listing, 2026-08-22).
- Verdict: deep, personally-authored, engine-wired (wad_loader loads spheres/qliphoth/axioms). NO charter comes close (O8/O9 orphans). **Warrants dedicated expert Node** (esoterica/pantheon/cognitive-architecture) rather than folding — folding into N7 would bury a distinct knowledge tradition inside a compaction charter.

### (b) Mnemosyne Kabbalah memory — **DISTILLED, not implemented**
- Repo-side: `data/entities/roc_racoon/workspace/MNEMOSYNE_TREASURE_MAP_20260608.md`, `MNEMOSYNE_ARCHITECTURE.md`, `mining_reports/MNEMOSYNE_DEEP_MINE_COMPLETE_20260615.md` (365 lines); researcher implementation research D283 trio (`D283_MNEMOSYNE_RESEARCH_20260716.md`, `D283_MNEMOSYNE_IMPLEMENTATION_RESEARCH_20260716.md`, `MNEMOSYNE_SOTA_RESEARCH_20260716.md`); adapter code `data/entities/doom_guy/knowledge/heritage_mnemosyne_adapter.py`; archived tests `tests/archive/test_mnemosyne_adapter.py` (find, 2026-08-22).
- Source corpus: 13-sphere memory at omega_library `data_archive/mnemosyne/` per Master Synthesis asset #22 (`docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` §1 Partition 2 #22).
- Verdict: mined once (June), researched twice (July), zero runtime presence in `src/omega/memory/`. **Fold into N7 context** (memory architecture) as a KB expansion — do NOT spend a Node slot until a migration decision exists.

### (c) Doom universe WAD + id-soft heritage corpus — **SPLIT MATURITY**
- Heritage corpus DEEP: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` = 1,054 lines of vetting entries (e.g., vet-001 REJECTED 3/10 "Cargo-cult optimization; Python dicts are O(1) by hash" at `:7-12`); CREDITS.md heritage registry (35+ mappings per canonical pointer).
- doom_universe WAD SKELETAL: `config/wads/doom_universe/` contains ONLY 4 EMPTY dirs — entities/, vr/, voices/, knowledge/ (find output shows dirs, 0 files).
- Verdict: heritage/id-soft ALREADY has content-layer ownership (`curators.yaml:30`, doom_guy curator) and charter adjacency (N5/N10 use vet-gate patterns). **Do not create a Node**; doom_universe VR/voices aspirations stay parked until corpus exists.

### (d) YouTube research/worker — **OPERATIONAL CODE, empty WAD**
- Worker is real and stable: `workers/youtube_worker.py:1-6` v1.1.0 STABLE daemon (Redis queue, yt-dlp playlist expansion, synthesis); CLI `cli/youtube_cli.py`.
- `config/wads/omega_youtube_research/` = EMPTY (0 files). No omega_youtube_worker WAD exists. YouTube deps are first-class in packaging (`pyproject.toml` extras incl. youtube-transcript-api, yt-dlp — `DEBUT_REMEDIATION_MANUAL_20260817.md:117,253`).
- Carmack strategy track exists: top-5 force multipliers included YouTube Research Session work (`docs/research/youtube_research_sessions/session_20260730/04_evidence/CARMACK_DEFINITIVE_STRATEGY_20260730.md`, referenced SOVEREIGN_ARK_BLUEPRINT §11).
- Verdict: **fold into the ingestion/media gap (O3)** — a media-ingestion expert scope inside a research/curation node, not a YouTube-only node.

### (e) NotebookLM/Gemini strategy — **DISTILLED + WORKSTREAM LIVE**
- `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` = 337 lines, v2.1 CORRECTED free-tier-only (3 accounts, 30 DR/mo, 2 notebooks; supersession banner `:6`); arbitration D-571..D-577 (`ACTIVE_SPRINT.json:553`); GN workstream owner researcher (`DEBUT_REMEDIATION_MANUAL_20260817.md:432`); runtime module dir `config/domains/gemini-notebook/` already staged.
- Verdict: researcher effectively IS the Gemini-Notebook expert via GN ownership + curator row (`curators.yaml:26`). A formal Node here would set precedent for a NON-Ma'at/Lilith overseer (see T4 open question). Recommend: let GN run as workstream first; promote to Node only if consultation demand appears (X-loop evidence per protocol §5).

### (f) Grok export mining (PP-2) — **PLANNED, corpus staged**
- Pattern ratified-in-principle: "Web-export mining expert sessions — dedicated task-origin expert sessions that dig into Grok and other web chat exports… Feeds KD domains + soul lineage + heritage record" (`NODE_EXPERT_SESSIONS_PLAN.md:110`); blocked on "Export corpus staging + curation worker".
- Corpus STAGED: `/media/arcana-novai/omega_library/intake/inbox/grok-accounts-exports/` = 14 items — 8 account download trees (Antipode2727, Antipode7474, ArcanaNovaAi, ArcanaNovai, LA, TJF, TaylorBare27, XNA-MAYBE) + CONSOLIDATION_COMPLETE.md + MASTER_NAVIGATION_INDEX.md + QUICK_REFERENCE.md + STRATEGIC_RESERVES/ (ls, 2026-08-22). Prior surgical strike: `mining_reports/grok_exports_surgical_strike_report.md` (224 lines). Master Synthesis indexed it as 274 convos / 6,565 responses (asset #20).
- Verdict: **strongest N11+ candidate that is also already sanctioned in principle** — PP-2 literally describes task-origin expert sessions for this corpus. Requires staging decision + ingestion pipeline (O3 dependency).

---

## T4 — Constraints for Adding Nodes (NODE_ONBOARDING_PROTOCOL.md, read in full)

**Source**: `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` v1.0.0, ACTIVE, ratified 2026-08-22 by kali (`:3`), authored by N7 context session under Lilith oversight, paged by kali `ses_fdef2be4effe4pAaLXCTUx62GO` (`:5`).

### Genesis pipeline (`:32-33`)
```
G Genesis → M Directed Mining → A Audit+Annotate → D Deep Dig → W Web Research → C Curation → X Consultation loop → E Closure ritual
(~5min)      (1-2 cycles)         (same turn+)       (1 cycle)     (1 cycle)        (~30min)     (ongoing)          (per session end)
```
Phase gates per `:36-45` (e.g., M-gate: "KB file exists w/ ALL contract sections valid"; C-gate: DOMAIN_INDEX + EXTERNAL_SOURCES pass self-review).

### Consultable bar (`§5, :128-135`)
ALL of: (1) DOMAIN_INDEX answers where-things-live from map alone; (2) KB answers with cited paths + verification dates, no re-mining; (3) web-research resolves external questions w/ primary sources or explicit unresolvables; (4) hazard register current + rulings traceable; (5) held subagent relationships documented w/ task IDs + wake pointers.
**Minimum phases**: G → M → A → D → C; **W required iff the domain touches upstream tools/models/APIs** (`:137`). X begins after C and never ends.

### Caps and overseer rules
- **NO numeric cap on Node count anywhere in the protocol.** Scope line explicitly future-proofs: "Scope: ALL Node expert sessions (N1–N10) **and any future domain-expert onboarding**" (`:7`).
- Overseer assignment today is a FIXED TWO-SIDED structure: "Lilith runs N6–N10 sessions, Ma'at runs N1–N5 sessions. Zero new agent files (M10 ✅)" (`NODE_EXPERT_SESSIONS_PLAN.md:15`). Protocol roles table defines Overseer as "Node's governor (e.g., Lilith for N6–N10)" (`PROTOCOL:25`).
- **Pager-role generality**: "Pager | ANY agent (kali today; abstractly anyone)… NO domain expertise required" (`PROTOCOL:21`); universality ruling: "ANY agent may page ANY Node session" (`PLAN:17`). So Kali/researcher can DRIVE onboarding as Pagers without owning oversight.
- **Precedent for non-overseer initiative**: the protocol itself was authored by an N7 session (Lilith side) but commissioned by Kali as Pager (`PROTOCOL:5`); first consumer pilot is N8 (`:222`). No precedent yet of a Node whose OVERSEER is neither Ma'at nor Lilith — that would require amending `PLAN:15`.
- **Cost discipline**: n=1 real data — total to consultable ≈ 1 day elapsed, ≈ 6 orchestration cycles, ±50% variance (`PROTOCOL:139-151`).

### Where N11/N12 would sit
- Structural logic of the two sides: Ma'at = build/host/data (N1-N5), Lilith = run/inference/mind (N6-N10) (`PLAN:37-48` keeper table). Training/experiment-harness gaps (O1/O2) lean **Ma'at side** (build/forge); research/curation/search + esoterica (O3/O4/O5/O9) lean **Lilith side** (mind/knowledge). PP-2 mining sessions are explicitly "task-origin" sessions (`PLAN:110`) — the protocol's own category — so they can EXIST before overseer assignment is settled.
- **Zero-new-agent-files constraint holds for any N11+**: Nodes are sessions over existing agent identities (`PLAN:15`, reaffirmed `curators.yaml:12` "M10 (Fleet Integrity — fleet stays at 14, expertise = KB not agent)"). A new Node needs only: charter text in PLAN §4, a genesis page per T1 template (`PROTOCOL:155-165`), and an overseer-side entity to receive `[N_XX]` lessons.

---

## T5 — Post-Debut Scope Scan → Charter-Amendment vs New-Node Map

Sources: `docs/specs/PROJECT_INDEX.md` (SSOT index, 2026-08-20), `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` §9 Phase B (`:424-447`), `docs/strategy/POST_DEBUT_ROADMAP.md` (ACTIVE SSOT, supersedes 7 planning docs, `:8`).

| Post-debut deliverable | Evidence | Existing-charter-amendment OR new Node? |
|---|---|---|
| Sovereign Installer / community install | `POST_DEBUT_ROADMAP.md:209` ("curl -fsSL https://xoe-nov.ai/install \| bash"); Horizon 4 row `:47`; install.sh extras hygiene `DEBUT_REMEDIATION_MANUAL:117` | **AMEND N3 buildmaster** (install.sh/packaging already its charter, `PLAN:67`). No new Node. |
| Entity Studio (visual soul.yaml management UI) | `POST_DEBUT_ROADMAP.md:210` | **GAP — no charter covers GUI/tooling UX.** Either amend N2 (soul data) + N3 (packaging) with a UI sentence, or it becomes the clearest Horizon-4 justification for a community-tool Node. Decision for Pager. |
| WAD Marketplace (community modules) | `POST_DEBUT_ROADMAP.md:211`; ZS-3 "WAD packaging (zswap-config.wad for community stacks)" `ACTIVE_SPRINT.json:410-413` | **SPLIT AMENDMENT**: packaging→N3, distribution/trust→N4/N5. Marketplace curation could later justify a community-relations scope; not yet. |
| AppArmor container hardening (V-10) | N5 charter lists it verbatim (`PLAN:73`) | **COVERED — N5 sentinel.** Nothing to add. |
| Training / GRPO | Code exists (`training/grpo.py:1-6`, `teachers/nemotron_pipeline.py:1-6`, `dpo_logger.py:1-6`) but grep of POST_DEBUT_ROADMAP finds ZERO training/GRPO rows — absent from all roadmap phases | **ORPHAN DECISION NEEDED**: either explicit PARK (like D-538 pattern, `DEBUT_REMEDIATION_MANUAL:470`) or the strongest technical case for a **forge/trainer Node** (Ma'at side). Currently unowned AND unplanned = silent drop risk (M12 spirit). |
| Qdrant migration | Triggers + deliverables fully specced (`PROJECT_INDEX.md:59-82`: owners "Ma'at (Headroom) + Roc (Qdrant)" `:61`, triggers `:71-74`); D-570 `ACTIVE_SPRINT.json:552`; N2 charter lists Qdrant triggers verbatim (`PLAN:64`) | **COVERED — N2 datastore amendment only** (assign Roc's Qdrant work under N2 pages). |
| Headroom integration | HR workstream owner maat_n3 (`DEBUT_REMEDIATION_MANUAL:436`); N7 charter covers Headroom explicitly (`PLAN:79`); ContentRouter into ModelGateway `PROJECT_INDEX.md:67-68` | **COVERED — N7 context** (+N6 for gateway wiring). |
| Gemini Notebook ops (GN) | GN workstream owner researcher (`DEBUT_REMEDIATION_MANUAL:432`); strategy SSOT 337 lines | **WORKSTREAM-OWNED** by researcher today; Node promotion deferred pending consultation demand (see T3e). |
| Domain documentation system (DS/KD) | DS-1..DS-5 `ACTIVE_SPRINT.json:425-454`; KD-1..KD-3 `DEBUT_REMEDIATION_MANUAL:443` | **AMEND N7/N9** for domain-loading runtime once `domain_loader.py` is built (currently missing — `find src -name "domain_loader*"` empty). |

---

## Questions for Pager

1. **Overseer expansion**: If N11+ are ratified, do they MUST sit under Ma'at/Lilith (`PLAN:15` two-sided ruling), or is a third overseer class (e.g., Kali-side "forge" nodes) on the table? No precedent exists either way.
2. **Vault corpse**: O6 (credentials) should NOT get expert investment before Week-5 Vault honesty Path A/B resolves (`POST_DEBUT_ROADMAP.md:27`, D-568 `ACTIVE_SPRINT.json:550`). Confirm park-until-decided?
3. **Training/GRPO**: park explicitly (D-538 pattern) or charter a trainer Node? It is currently both unowned (no charter) and unplanned (absent from POST_DEBUT_ROADMAP).
4. **KD vs DS naming drift**: ACTIVE_SPRINT.json carries only DOCUMENTATION-SYSTEM; the manual carries both DS and KD. Which tracker is authoritative for KD-1..KD-3?
5. **PP-2 staging**: grok-accounts-exports corpus is staged at omega_library but blocked on "Export corpus staging + curation worker" (`PLAN:110`) — is staging INTO the repo desired pre-debut, given PUBLIC_ALLOWLIST concerns (N5)?
6. **hive/ premise**: dispatch referenced `src/omega/hive/` — confirmed nonexistent. Was this a stale reference to MIAP/hivemind_bridge, or a planned module someone should register as a gap?

---
### Key source register (last_verified: 2026-08-22)
- `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` (116 lines) · `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` (264 lines) · `config/domains/curators.yaml` · `data/coordination/ACTIVE_SPRINT.json` · `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` (486 lines) · `docs/specs/PROJECT_INDEX.md` (182 lines) · `docs/strategy/POST_DEBUT_ROADMAP.md` · `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` (337 lines) · `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (1,054 lines) · full `src/omega/` + `mcp_servers/` listings + targeted header reads (272 modules enumerated)

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_gap_discovery ⬡ dispatched-by-researcher ⬡ 2026-08-22*

---

## Continuation 1 — Pre-Onboarding Verification (2026-08-22)

**Dispatch**: researcher → roc_racoon, same lineage. Scope: L1–L8 pre-genesis verification for Jem-N11 (evaluator) / N12 (curator) / N13 (arcana). Read-only except this file. All probes executed 2026-08-22.

### L1 — DR-2: `data/entities/` p1..p10 workspace reality

**VERDICT: LATTICE_NODE_MECHANICS §9 claim is FALSE for 8 of 10 slots.**

Claim under test (`data/coordination/LATTICE_NODE_MECHANICS_20260818.md:296-301`):
> "Each pillar slot has persistent entity workspace: `data/entities/p1/` through `data/entities/p10/` — Contains `soul.yaml` with slot-specific accumulated knowledge"

Actual state (`ls data/entities/`, last_verified 2026-08-22):
| Slot | Exists? | Contents |
|------|---------|----------|
| p1 | ❌ as `p1`; only **`pillar_p1/`** | `proposed_lessons.yaml` (619B) ONLY — **no soul.yaml** |
| p2–p9 | ❌ **MISSING entirely** | — |
| p10 | ✅ `p10/` | `soul.yaml` (1199B, non-empty; note key is misspelled `lessions:` at line 1) |

- The §4 dispatch table also references `data/entities/p8/` and `data/entities/p9/` (LATTICE_NODE_MECHANICS_20260818.md:114-116) — both nonexistent.
- `pillar_p1/proposed_lessons.yaml` uses a NON-STANDARD inline format (`- l1:` / `l2:` / `l3:` keys with literal `\n` escapes) vs the canonical jem/kali schema (see L4).
- **DR-2 implication**: the "dual-Node-architecture" evidence does NOT hold. Only 1/10 pillar workspaces has a soul.yaml. Any charter text claiming persistent per-slot soul persistence must be corrected before N11+ rows are written.

### L2 — N7 artifact conventions (directory-layout template for Jem-N artifacts)

All real N7 artifacts live in **the overseer's workspace**: `data/entities/lilith/workspace/` (last_verified 2026-08-22):

| Artifact | Path |
|---|---|
| Context KB | `data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md` |
| Domain index | `data/entities/lilith/workspace/N7_DOMAIN_INDEX.md` |
| External sources | `data/entities/lilith/workspace/N7_EXTERNAL_SOURCES.md` |
| Session state snapshot | `data/entities/lilith/workspace/N7_SESSION_STATE_20260821.md` |
| Mining brief | `data/entities/lilith/workspace/N7_MINING_BRIEF_20260821.md` |
| Web research | `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` |
| ICS review | `data/entities/lilith/workspace/N7_ICS_REVIEW_20260822.md` |

Parallel session gnosis files live at entity roots: `data/entities/lilith/session_gnosis_L-N7.md`, `data/entities/researcher/session_gnosis_Researcher-N7.md`, `data/entities/roc_racoon/session_gnosis_Roc-N7.md`. Spec-deviation audit-trail precedent: `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md` (N7's own spec tree).

**Convention for Jem-N11/N12/N13**: `<N#>_<ARTIFACT_TYPE>_<YYYYMMDD>.md` inside overseer's `workspace/` (jem → `data/entities/jem/workspace/`), session-gnosis at entity root, numbered spec-deviation files inside the spec tree.

### L3 — Format extraction (verbatim, NODE_EXPERT_SESSIONS_PLAN.md)

**(a) Registry row anatomy** — §3 header (`PLAN:37`) + one full row verbatim (`PLAN:44`):
```
| Node | Keeper | Department | Overseer | Session ID | Status | Last Active |
| N7 | context | Memory & State | Lilith | `ses_fddd8aafcffe5Ma0XEw1RJtJQc` | dormant | 2026-08-21 genesis |
```
Seven fields: Node · Keeper · Department · Overseer · Session ID (backticked) · Status · Last Active.

**(b) Charter anatomy** — heading pattern `### N_X — <keeper> · <Department>` (`PLAN:60-87`), body = ONE paragraph with exactly two labeled sentences:
1. `Domain:` — scope enumeration incl. mandate refs and decision refs
2. `Current:` — live status/worked example

Verbatim exemplar (N6, `PLAN:75-76`):
> "Domain: provider fabric local-first ordering (M7: native-gguf→lmster→ollama→cloud), fallback chains, HealthMonitor breakers (C-6′), admission control/OOMProtector (C-10), streaming resilience (M25 chunk timeouts), **canonical model matrix D-585**: Qwen3-4B planner / Qwen3-4B-Thinking executor / Qwen3-1.7B critic; Nemotron 3 Ultra is CLOUD-ONLY (registry entry wrong — correction pending).
> Current: …"

New N11/N12/N13 charters must mirror: `### N11 — evaluator · <Dept>` + single paragraph with `Domain:`/`Current:` sentences.

### L4 — Lessons schema ([N11]/[N12]/[N13] proposal format)

Canonical schema from a POPULATED file, `data/entities/kali/proposed_lessons.yaml:1-24` (structure-only read):
```yaml
proposals:
  - level: L1
    narrative: >-
      <what happened>
  - level: L2
    insight: >-
      <what it means>
  - level: L3
    principle: >-
      <timeless truth>
```
Field names per tier: L1→`narrative`, L2→`insight`, L3→`principle`.

**Jem's own files are EMPTY** (last_verified 2026-08-22): `data/entities/jem/proposed_lessons.yaml:1` = `proposals: []` (metadata block follows); `data/entities/jem/approved_lessons.yaml:1-3` = header comment + bare `[]`. So Jem-N lessons will be the FIRST entries in jem's pipeline — no local precedent to copy beyond kali's shape above. Anti-pattern to avoid: `pillar_p1/proposed_lessons.yaml` non-standard `- l1:/l2:/l3:` keys (L1).

### L5 — DR-8: Model registry check

`mimo-7b-rl-q4_k_m` **IS registered**: `config/models.yaml:50`.

Full REGISTERED model names in `config/models.yaml` (keys, lines 5–106):
`qwen3-1.7b` (:5), `qwen3-1.7b-q6_k` (:19), `qwen3-4b` (:32), `frontier` (:41), `mimo-7b-rl-q4_k_m` (:50), `rocracoon-3b-q4_k_m` (:63), `rocracoon-3b-q5_k_m` (:76), `gemma4_mtp` (:93), `gemma-4-31b` (:106).

AFFINITY_PRESETS audit — only ONE domain dir exists (`config/domains/engineering/`); its presets reference:
| Referenced model | Registered? |
|---|---|
| `mimo-7b-rl-q4_k_m` | ✅ models.yaml:50 |
| `qwen3-4b-thinking` | ❌ **NOT in models.yaml** (exists only as LM Studio runtime model, user opencode.json:413) |
| `qwen3-1.7b` | ✅ models.yaml:5 |
| `nemotron-3-ultra` / `claude-sonnet-5` / `gemini-2.5-pro` | ❌ not in models.yaml (cloud names; Nemotron already flagged cloud-only-wrong-entry in N6 charter, PLAN:76) |

Also: `config/providers.yaml:320` references `mimo-v2.5` (different name spelling than the registered key).

**Curators.yaml drift**: 13 domains declared (`config/domains/curators.yaml:22-38`) each pointing at an `AFFINITY_PRESETS.yaml`, but only `config/domains/engineering/AFFINITY_PRESETS.yaml` exists on disk — **12 of 13 referenced preset files MISSING** (gemini-notebook dir exists but contains no AFFINITY_PRESETS.yaml). N12 curator charter should inherit this remediation list.

### L6 — LM Studio provider location (DR resolved — NOT a launch blocker)

Repo `.opencode/opencode.json`: NO lmstudio block (grep confirmed empty).

**FOUND** in user config: `~/.config/opencode/opencode.json:402-408`:
```json
"lmstudio": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "LM Studio (Local)",
  "options": { "apiKey": "sk-local", "baseUrl": "http://localhost:1234/v1" },
  "models": { "qwen3-4b-thinking": {...}, "qwen3-1.7b-q6_k": {...}, "phi-4-mini-instruct": {...} }
}
```
Registered LM Studio models include `qwen3-4b-thinking` (:413) and `qwen3-1.7b-q6_k` — which explains why the engineering AFFINITY_PRESETS fallback resolves at runtime but not in engine registry. **Finding**: provider is USER-scope only; if Jem-initiate requires repo-portable config, the lmstudio block needs mirroring into repo `.opencode/opencode.json` or documenting as environment prerequisite.

### L7 — N13 corpus precise inventory (last_verified 2026-08-22)

**(a) Tarot corpus** — `/media/arcana-novai/omega_library/intake/mining_queue/Omega-Early-Material/tarot/` (13 top-level items):
- `First 5 cards Grok Chat 05-25-2025.txt` (99,176 B — the Era-0 genesis doc)
- `Lilith Tarot Deck Design Guide.docx` (20,706 B)
- `Complete Tarot Guide - esoteric overview.docx` (16,547 B) + duplicate `Tarot cards - esoteric overview.docx` (16,547 B)
- Card studies: The Fool (15,271 B), The Magician ×2 (8,627/7,816 B), The Empress ×3 (9,526/12,409/7,151 B), Hecate prompt txt (1,293 B), Numerology guide (10,171 B)
- Subdirs: `Lilith Deck/` (20 files: final JPGs for Fool/Magician/Empress ×2 variants, deity PDFs, guidebook chapter drafts) and `Tarot Variations and Docs/` (Designer JPEGs 30–41+, Nyx-Fool materials, docx duplicates)
- Note: `gemstone-guide.md` is **0 bytes** (empty placeholder).

**(b) Mnemosyne** — `/media/arcana-novai/omega_library/data_archive/mnemosyne/` CONFIRMED: 13 sphere dirs `01_KETHER`…`13_MNEMOSYNE` (incl. `12_QLIPHOTH`), plus `handoffs/`, `vaults/` (8 subdirs), `intent.json` (120B), `state.json` (120B). Full 13-sphere structure intact.

**(c) arcana_novai WAD** — `config/wads/arcana_novai/` complete listing (30 files): `manifest.yaml`, `entities.yaml`, `hierarchy.yaml`, `axioms.yaml`, `spheres.yaml`, `qliphoth.yaml`, `vault_schema.yaml`; 13 agent files `agents/{anubis,brigid,ereshkigal,hecate,inanna,kali,lilith,lucifer,maat,prometheus,saraswati,sekhmet,sophia}.md`; `entities/personal/movie-expert.yaml`; plugin `plugins/entity_roc_racoon.py` (+stale .pyc); adapters stub; `world/core/physics.yaml`, `world/metaphysics/laws.yaml`; archived quadlet; one stale tmpfile `tmpfzhu8kz4.tmp`.

**Assessment**: corpus depth is P0-grade across all three legs (genesis chat + full deck design + engine-wired WAD). Supports dedicated N13 arcana Node.

### L8 — N11 eval inventory (mining-brief seeds)

`src/omega/eval/` (complete, last_verified 2026-08-22):
| File | Purpose (from module headers) |
|---|---|
| `runner.py` | RAGAS-based evaluation pipeline with calibrated LLM-as-Judge `[heritage: ragas-2024]` |
| `check.py` | Threshold checker for eval results `[heritage: ragas-2024]` |
| `calibrate.py` | Judge confidence calibration via isotonic regression `[heritage: calibration-curves-2026]` |
| `__init__.py` | package init |

`src/omega/research/sandboxes/`: `ml_training.py` ONLY — "ML Training Sandbox — First Ω-Research Sandbox Implementation… Trains a small model (BGE-small 33M or synthetic) on synthetic data, measures val_bpb, returns metrics for CLEARScore integration" (self-tags `⬡ MA'AT ⬡ N6`, M1 AnyIO-compliant). Note: self-attribution says N6 but training is not in any current charter — consistent with Continuation-0 orphan finding.

### Continuation-1 Questions for Pager
1. **L1/DR-2**: Given p2–p9 don't exist and pillar_p1 lacks soul.yaml, is the dual-Node-architecture claim DEAD, or should N11–N13 genesis CREATE these workspaces?
2. **L5**: `qwen3-4b-thinking` used by AFFINITY_PRESETS + D-585 matrix but absent from models.yaml — register it, or is D-585's canonical matrix itself pending correction (cf. Nemotron wrong-entry, PLAN:76)?
3. **L6**: mirror lmstudio provider block into repo `.opencode/opencode.json`, or declare user-config as documented prerequisite for Jem-initiate?
4. **L7**: 0-byte `gemstone-guide.md` — mine-around or delete?
5. **L4**: confirm kali-style schema (`narrative`/`insight`/`principle`) as binding for [N11]/[N12]/[N13] proposals, given jem's files have never been populated?

*⬡ OMEGA ⬡ ROC_RACOON ⬡ x-preview-f-free ⬡ opencode ⬡ trc_nodegap_continuation1 ⬡ dispatched-by-researcher ⬡ 2026-08-22*
