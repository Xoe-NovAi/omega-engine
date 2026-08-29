# 🔱 Omega Engine — Consolidated Decisions & Deep Understanding
**AP Token**: `AP-ENGINE-DECISIONS-CONSOLIDATED-20260817`
**Author**: roc_racoon (Legacy Miner / Deep Researcher)
**Date**: 2026-08-17
**Status**: SINGLE SOURCE OF TRUTH for all final decisions & rationale

---
§1 The North Star (One Paragraph)

**Omega Engine** is the universal, community-owned runtime for sovereign AI — a local-first, cognitive sovereign engine. It provides a pure runtime core (`src/omega/`) with a WAD architecture (Engine → IWADs → PWADs) so users never fork core code — they add layers. The engine delivers: local inference as the floor (native-gguf → lmster → Ollama), local verification as the ceiling (Skeptical Verification, Tainted Data Isolation, Unified Vector Abstractions), and cognitive sovereignty via L1→L2→L3 distillation in `soul.yaml`. The promise: **One install. Your computer. Your data. No cloud required.** The Engine Core is portable, modular, and platform-agnostic; WADs are cosmology-specific. Every agent maintains sovereign memory (`soul.yaml`) with L1→L2→L3 distillation so intelligence persists across sessions. The fleet coordinates via file-based Hivemind with zero external dependencies. Temple-Grade quality gates (T1-T11) enforce production readiness. This is not a chatbot wrapper — it is the infrastructure for **Cognitive Sovereignty**.
---

## §2 Final Decisions Registry (Every D-Series Decision)

| D-ID | Decision | Rationale | Evidence | Supersedes | Status |
|------|----------|-----------|----------|------------|--------|
| D-275 | Institutionalize Wave 3 refinement meta-process | Process continuity across agent handoffs | PIVOT_LOG.md | — | Active |
| D-276 | Implement ContextProtocol pipeline (15K budget) | Standardized context injection | PIVOT_LOG.md | — | Active |
| D-277 | Soul Hydration Pipeline — fix schema mismatch, add soul_utils.py, hydration sequence, soul-verify gate | Fix soul.yaml load/save corruption | PIVOT_LOG.md | — | ✅ COMPLETE (Phase I) |
| D-279 | Hydration System Portability & M2 Firewall Remediation — 4 M2 violations, mechanism-content separation | Engine/Stack firewall enforcement | PIVOT_LOG.md | — | ✅ COMPLETE (Phase III+IV) |
| D-280 | Sovereign Continuity Feature — SSE-based compaction detection, epoch-scoped receipts, CheckpointManager | Prevent Void Summaries | PIVOT_LOG.md | — | Deferred |
| D-281 | Substrate Repair Execution — 4-phase plan (Soul Injection, Path Infra, M2 Firewall, Codex Sep) | Fix foundational substrate | PIVOT_LOG.md | — | ✅ COMPLETE — 11 commits, 5 agents |
| D-282 | sqlite-vec PRAGMA SSOT convergence — cache_size 512MB→32MB, wal_autocheckpoint 1000→500, 4 concurrency tests | 5700U hardware reality | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-283 | Mnemosyne Phase 2 — RecallStore (power-law decay, quality scoring, promote-to-core bridge) | Warm memory tier | PIVOT_LOG.md | — | 🟡 DESIGN COMPLETE — 2 test infra fixes pending |
| D-284 | MCP Streamable HTTP + PKCE auth — SSE→Streamable HTTP migration, self-hosted IdP | MCP 2026-07-28 GA | PIVOT_LOG.md | — | Deferred |
| D-285 | Nomenclature Correction — Slots (engine) vs Pillar Keepers (ANAi) vs Lenses (Meditate) vs Roles (Lattice) | M2 firewall compliance | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-286 | Meditate Base+Overlay Architecture — 13 universal base lenses + PWAD-specific overlays | M2 compliance: engine ≠ WAD | PIVOT_LOG.md | — | ✅ DESIGN COMPLETE |
| D-287 | M2 Firewall Migration Phases A-E — 201 violations across 5 modules, ROLE constants + WAD YAML pattern | Systematic M2 remediation | PIVOT_LOG.md | — | 🟡 PHASE A ACTIVE |
| D-288 | Scribe as Lattice Role — Documentation/gnosis distillation as cross-cutting capability (not Slot Entity) | Cross-cutting concerns belong in Lattice | PIVOT_LOG.md | — | ✅ DESIGN COMPLETE |
| D-289 | Cline CLI Integration — DeepSeek V4 Flash (1M) + MiMo V2.5 (512K) as HMC Tier 5 | Cloud synthesis tier, local-first preserved | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-290 | Session Namespace Isolation — MIAP-wired session-scoped directories under `sessions/<uuid>/` | Multi-instance collision prevention | PIVOT_LOG.md | — | 🟡 DESIGN COMPLETE |
| D-291 | MIAP Phase 0 — Core + Safety: ReplayMode enum, Two-Log Model, IntentionValidator, CheckFunctions, LiteTopic | Production-scale operational details | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-292 | MACP Alignment — Hivemind handoffs extended with `macp_mode` for interoperability | Open standard coordination | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-293 | Context Engineering Knowledge Layer — Governed knowledge mount in `sessions/` structure | Enterprise multi-agent layers | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-294 | Experience Repository — AgentRR-Style L0→L1→L2 Distillation Pipeline via Scribe | Compound interest of agent intelligence | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-295 | Trace-to-Eval Loop — Automatic conversion of production failures to regression tests | Highest-value test cases | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-296 | SomaticState + MIAP Integration — Full cognitive state recovery with somatic snapshots | Model interchangeability | PIVOT_LOG.md | — | 🟡 DEFERRED — requires llama.cpp API stability |
| D-297 | MEDITATE Architecture Inversion — Substrate-First Critical Path (10 phases) | Hardware constraint = architecture | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-298 | Substrate-First Serial Mining — Ken Walger Operation (serial 10-phase, 60% infra exists) | 14GiB RAM = serial physics | PIVOT_LOG.md | — | 🟢 RATIFIED |
| D-299 | Omega-Vault Credential Operator — OS keyring + SQLite event log + CAP adapters (6-phase) | Credential void blocks fleet | PIVOT_LOG.md | — | 🟡 IN PROGRESS |
| D-300 | Autonomous Meditation Pipeline — Complete product delivery + Nemotron streaming fix | Productized meditation + fix 30s chunk gaps | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-301 | MaKaLi Parallel Council Architecture — Parallel independence + oversoul distillation + optimized synthesis | Triad governance model | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-302 | Canonical Project Registry (CPR) — One-turn hydration for all projects via `data/projects/*/CONTEXT.md` | Context recovery in one read | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-303 | Headless Subagent Pool — 24-account compute resource (8 Grok + 8 Copilot + 8 Cline) | Massive idle compute resource | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-304 | Antigravity Multi-Account Integration — Omega-Vault provider + WARP Pool IP rotation for OCZ | 8 accounts + IP rotation synergy | PIVOT_LOG.md | — | 🟡 PLANNED |
| D-350 | Phase C as Current Execution Phase | Post-Foundation Stabilization | PIVOT_LOG.md | — | ✅ ACTIVE |
| D-351 | No New Providers Until Fabric Systematized | Prevent provider sprawl | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-352 | MaKaLi Routing — Kali Local, Voices Cloud | Config in providers.yaml | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-353 | 147 Stale Strategy Docs Archived | Reduce fragmentation | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-354 | Cloud Provider Order: Antigravity → Google → OpenCode Zen → OpenRouter | Single breaker per provider | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-355 | STRATEGY_CORPUS_MAP.md as Mandatory Layer 2 | Fine-grained preservation | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-356 | GAP-05 → C-10 Admission Control | Semaphore(1) + OOMProtector | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-357 | V-1 Is an Explicit Ticket | Blocks Grok CLI fleet pool | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-358 | C-2' Before C-1'/C-10 | Dependency order corrected | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-359 | MCP Audit Must Start TODAY — 7-day deadline | July 28 GA deadline | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-360 | C-11 Test Infrastructure Added as P0 | Fixtures, chaos tests, benchmarks | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-361 | Identity Phase 0 depends on C-1′, not Phase D | SoulStore prerequisite | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-362 | C-1′ = SoulStore (multi-path elimination), not flock paste | Atomic writer, 4-layer guarantee | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ COMPLETE |
| D-363 | C-6′ = unify/delete breakers, not port pybreaker | HealthMonitor factory canonical | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ COMPLETE |
| D-364 | C-0 = test honesty is P0 before Phase D | No vanity pass counts | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ COMPLETE |
| D-365 | Living Research OS spec amended by §3.2; cannot claim dual CANONICAL | Single SSOT | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-366 | STRATEGY_CORPUS_MAP.md is mandatory Layer 2 for fine-grained preservation | Companion to Ark | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-367 | GAP-05 → C-10 admission control (not only C-5 cloud voices) | Local admission first | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-368 | Identity Fluidity E-0…E-5 paths preserved under `data/entities/grokster/workspace/` | Entity workspace preservation | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ PRESERVED |
| D-369 | Researcher queue extras (VerificationGate, SQLite, 7-stage) deferred but mapped — not discarded | Corpus Map preservation | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ DEFERRED |
| D-370 | Kali ratifies Strategy Unify APPROVE with amendments | `KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md` | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-371 | V-1 is an explicit ticket (not free-text only) | GAP-08 credential void | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-372 | Living Research OS body SUPERSEDED by banner + Ark §3.2 where conflict | Kali amendment 1 | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-373 | C-2′ before C-1′/C-10 — dependency order corrected | Nemotron synthesis | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-374 | C-11 Test Infrastructure added as P0 ticket | Nemotron synthesis | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-375 | MCP audit must start TODAY — 7-day deadline | Nemotron synthesis | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ COMPLETE |
| D-376 | E-0 Identity Fluidity added to manual after C-1′ | Nemotron synthesis | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-377 | Free Gemma 4 31B workhorse collapse is P0 — forensic report is evidence SSOT | 16k input token limit Jul 15 | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-378 | Twin tickets G-1 (workhorse) + W-1 (WARP) elevated parallel to Guard & Distill | Architect elevation | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-379 | WARP is for IP-keyed OCZ (etc.), NOT Google free-tier input TPM fix | Distinct rate-limit keys | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-380 | No silent context caps to force free Gemma under 16k | Honesty over theater | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-381 | Broken `/usr/local/bin/warp-ns-setup` is primary WARP blocker; source = `warp-proxy-pool/scripts/warp-ns-setup.sh` | Syntax error line 49 | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ RATIFIED |
| D-382 | Omnidroid 6 cognitive modules fully evolved into current architecture — Jem Session 43 confirmed; no porting needed | Mining verification | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ VERIFIED |
| D-383 | NotebookLM 5-notebook ingestion strategy (R52c) exists — implement `prepare_notebooklm.py` as NL-1 ticket post Phase D | R52c spec complete | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ PARKED |
| D-384 | Lilith Tarot genesis (Era 0) recovered — 5 cards, full pantheon, rituals; add to philosophy lineage | Mining recovery | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ PRESERVED |
| D-385 | Mnemosyne 13-sphere Kabbalistic memory recovered — precursor to soul.yaml; migration script needed | Mining recovery | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ PRESERVED |
| D-386 | Grok 8-account exports indexed (274 convos, 6565 responses) — add to XNAI-RAG search fleet | Mining recovery | SOVEREIGN_ARK_BLUEPRINT.md | — | ✅ PRESERVED |
| D-510 | Node (N1-N10) Architecture Replaces Pillar (P1-P10) — eradicate P-prefix across engine core, default IWAD, agent system, canonical docs | P-prefix collision with Priority, Percentiles, ANAi WAD | PIVOT_LOG.md | — | ✅ COMPLETE (116 files) |
| D-511 | Vetala + Omega-Sieve Dead-Code Removal — delete 47 files, 11,390 deletions, purge Vetala references | Dead code flag declared obsolete | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-512 | sqlite-vec M14 Heritage Tag Correction — `[id-soft: sqlite-vec-2024]` → `[heritage: sqlite-vec 2024]` | Not id Software technique | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-513 | PyPI Fiction Removal — remove false "3 on PyPI" claims; 0 packages published | Truth in advertising | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-514 | ark_optimizer Service Fix + make Targets — remove User=1000, fix RE_IDSOFT_EMPTY false positive | systemd user session fix | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-515 | Complete omega_pantheon → omega_nodes Rename (D-510 follow-up) — fix docstring and test references | KeyError on missing YAML key | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-516 | Rotating Test-Run Log Implementation — `data/logs/test-run.log` with 4-generation retention | Historical test record | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-517 | GAP-0 Fix: ObservabilityEngine Async Refactor — all MetricsDB-facing methods async + `_sync` wrappers | Data loss + TypeError in async contexts | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-518 | GAP-3 Fix: M23 Pre-commit Gate Repair — replace broken `rg` pipeline with AST-based Ruff ratchet (S110/S112/BLE001/E722) | Gate was structurally incapable of failing | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-519 | Context Packer Enhancement — Forensic Linking + Agent Guidance — pack_id UUID, account/project/version metadata, PROJECT_OVERVIEW.md | Traceability + agent guidance | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-520 | GAP-1 Foundation: ProviderRegistry SSOT — `src/omega/oracle/provider_registry.py` reads `is_cloud` from `config/providers.yaml` | 5 divergent classifiers causing 73.6% misclassification | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-521 | Sovereign Distillation Pipeline (SDP) — tripartite: Scaffold (cheap) → Synthesize (AGY) → Execute (local); 80% Redzone escalation | Replace single workhorse search | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-522 | SDP Ground Truth: Model Context Windows — Nemotron 3 Ultra=1M, Laguna S 2.1=262K, Claude Sonnet 4.6=200K, Gemini 3.1 Pro=1M; free vs paid differ 4× | Gauge keyed on model+tier | PIVOT_LOG.md | — | ✅ VERIFIED |
| D-523 | SDP Systems Audit: No Duplicates — SDP ~60% built; V-1 Vault, Pool Tracker, Dialectic Logger, Triage Router, Token Estimator exist | Extend existing, don't rebuild | PIVOT_LOG.md | — | ✅ VERIFIED |
| D-524 | SDP Quick Win Items — QW-1 through QW-10 for Phase 1 Context Gauge (~24 hrs) | Model windows, token counting, CI guard, pool_tracker, cloud config | PIVOT_LOG.md | — | ✅ APPROVED |
| D-526 | zswap > zRAM for Desktop with NVMe — 25% pool, lzo_rle, zsmalloc; never run both simultaneously | Chris Down + Fedora + kernel docs | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-527 | Never Run zswap + zRAM Simultaneously — they fight; migration: swapoff → rmmod zram → enable zswap → NVMe swap | Hardware reality | PIVOT_LOG.md | — | ✅ LOCKED |
| D-528 | pyresilience > tenacity for Circuit Breaker — 10.4x faster happy path, 14.4x async, 43% less memory, all 7 patterns | Spike 1h, fallback tenacity | PIVOT_LOG.md | — | ✅ APPROVED |
| D-529 | Simplify OOMProtector to 2-Signal — remove cgroup pressure; keep PSI + MemAvailable only | "Server-grade theater for desktop" (Carmack) | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-530 | Context Gauge Uses tokens.total — never tokens_input (overcounts ~87x); json_extract(data, '$.tokens.total') | Token accounting not additive | PIVOT_LOG.md | — | ✅ LOCKED |
| D-531 | Multi-Write Subagent Method Mandatory — phase-based execution with mandatory disk writes after each phase | 0% → 100% success rate | PIVOT_LOG.md | — | ✅ MANDATED |
| D-532 | Mandate Compliance Measured Mechanically, Not Hand-Written — `make check-mandate-compliance` parses SOVEREIGN_MANDATES.md for denominator=27 | 3-way SSOT contradiction (25/26/27) from hand-written % | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-533 | This month's execution SSOT is DEBUT_REMEDIATION_MANUAL_20260817.md, not Ark §4 | Grok CLI remediation review | DEBUT_REMEDIATION_MANUAL.md | Ark §4 | ✅ RATIFIED |
| D-534 | Publication (PUB-1) and runtime deletion (DEL-1) are separate cuts | Code-judo thesis | DEBUT_REMEDIATION_MANUAL.md | — | ✅ RATIFIED |
| D-535 | Vault is not wired for debut. Invert V-1 from "build/wire" to "hide or delete" | Sidecar unused, CLI-broken | DEBUT_REMEDIATION_MANUAL.md | V-1 | ✅ RATIFIED |
| D-536 | One router: ProviderSelector + providers.yaml. Delete Triage + Semantic + RoutingTable | 5 historical answers in path | DEBUT_REMEDIATION_MANUAL.md | — | ✅ RATIFIED |
| D-537 | UO Phase 1 library swaps and UO §2.6 three-vault adoption rejected for debut | DEL-1 supersedes | DEBUT_REMEDIATION_MANUAL.md | UNOVERENGINEERING_PLAN.md | ✅ RATIFIED |
| D-538 | SDP / Cognitive Sovereignty §7 / Qdrant / JIT Graph RAG / Instruction Router are PARKED | DOC-1 override | DEBUT_REMEDIATION_MANUAL.md | SOVEREIGN_ARK_BLUEPRINT.md | ✅ PARKED |
| D-539 | CP-3 not publicly true until INST-1 passes on machine without warp-proxy-pool | Install honesty gate | DEBUT_REMEDIATION_MANUAL.md | — | ✅ RATIFIED |
| D-540 | Corpus Map "nothing deleted by silence" inverted for this campaign | PARKED = do not implement | DEBUT_REMEDIATION_MANUAL.md | STRATEGY_CORPUS_MAP.md | ✅ RATIFIED |
| D-VOS-001 | VOS v1.0 Instantiation — 7 sovereign realms with state.yaml, VISION_ANCHOR.md, DECISION_LEDGER.md, realm_cli.py | Vision persistence | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-002 | Session-End Hook Preserves Proposals — session_end.py no longer overwrites agent proposals with `[]` | Soul integrity | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-003 | Soul Validator — VALID_SOUL_VERSIONS expanded to {6.1,7.0,7.1,7.2} | Version compatibility | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-004 | Soul Validator — LIVE_FEED→HUB — replaced LIVE_FEED references with HMC_COLLABORATION_HUB.md | Coordination consolidation | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-005 | Mandate Header Correction — SOVEREIGN_MANDATES.md "Twenty-Five" → "Twenty-Seven" | v3.8.0 accuracy | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-006 | M22 SSOT Check Fix — fixed false positive on `is_cloud` in providers.yaml | Provider classification | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-007 | Context Packer Tuple Fix — test_context_packer.py tuple unpack fix | Test stability | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-008 | 96 Test Failures Triage — Class A (code bugs ~20), B (test drift ~50), C (integration ~26) | Failure categorization | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-009 | Public Debut PR — 3-Phase Plan — Phase 1 (root junk), Phase 2 (README), Phase 3 (.gitignore) | Publication strategy | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-VOS-010 | 7 Sovereign Realms — Domain decomposition for vision persistence | VOS architecture | PIVOT_LOG.md | — | ✅ COMPLETE |
| D-VOS-011 | PKEXEC Privilege Directive — N1/Architect privileged ops use pkexec, not sudo | Security hygiene | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-VOS-012 | Audit-First Approach — Verify all claims before execution | M23 Failure Integrity | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-VOS-013 | Ratify 3-PR Path — PR-A (public-surface-honesty), PR-B (real M2), PR-C (dead-code quarantine) | Structured debut | PIVOT_LOG.md | — | ✅ RATIFIED |
| D-VOS-014 | Reject Carmack Nuclear Plan — 6 fatal errors (M2 misdiagnosis, wrong paths, vault liveness, strategy-doc purge, VOS age, git add -A secrets) | Independent verification | PIVOT_LOG.md | — | ✅ LOGGED |
| D-VOS-015 | Amend ENG-001 — "146 WAD term leaks" → "M2 = stack-specific leaks, run FirewallChecker.scan()" | Accurate diagnosis | PIVOT_LOG.md | — | ✅ AMENDED |
| D-VOS-016 | TRACKING_ARCHITECTURE.md Keep-List — Added to PR-C keep-list (M27 constitution) | Constitution preservation | PIVOT_LOG.md | — | ✅ AMENDED |
| D-VOS-017 | Log Carmack Mandate Violations — SYSTEM_FAILURE_LOG.md created with M4/M23/M14/M26/M27/M8/false-M2 | Violation tracking | PIVOT_LOG.md | — | ✅ LOGGED |
| D-VOS-018 | VOS Hybrid Plan (Option C) Approved — Keep DECISION_LEDGER + VISION_ANCHOR, retire 7 state.yaml + 7 briefs + realm_cli.py, add Hub enforcement | VOS simplification | PIVOT_LOG.md | — | ✅ APPROVED |

---

## §3 Architecture Decisions (The "Why" Behind the Code)

### 3.1 Engine vs Stack Separation (M2) — Final Ruling

**Decision**: Absolute separation. Engine Core = `src/omega/`, `config/omega.yaml`, `opencode.json`. Stacks = `config/wads/<stack_name>/`. Never add stack-specific logic to Core.

**Rationale**: 14 months of architectural drift proved commingling destroys portability. The Feb 2026 "Foundation vs Arcana" document explicitly separated them but was never implemented cleanly. The current omega-engine repo is the FIRST clean implementation.

**Evidence**: R44_ENGINE_STACK_SEPARATION.md §2-§3; SOVEREIGN_MANDATES.md M2; OMEGA_ENGINE.md §1.

**Invariant**: Engine defines Slots (N1-N10). WADs fill Slots. Engine never references WAD entities.

### 3.2 Local-First Provider Fabric (M7) — Priority Chain Final

**Decision**: `native-gguf(0)` → `lmster(1)` → `Ollama(2)` → `Google(3)` → `OpenCode Zen(4)` → `OpenCode(5)` → `Copilot(6)`. Unknown providers classified **cloud** (pessimistic). No new providers until fabric systematized (D-351).

**Rationale**: Sovereignty means local inference is primary, cloud is safety net. The 8-key Gemma rotation (Cerebras/Groq free tiers) are cloud fallbacks, not local replacements.

**Evidence**: SOVEREIGN_MANDATES.md M7; ORACLE_STACK_CANONICAL.md §6; SOVEREIGN_ARK_BLUEPRINT.md §7; DEBUT_REMEDIATION_MANUAL.md §7.

**Config**: `config/providers.yaml` strategy = `local_first`. `ProviderRegistry.is_cloud()` implements pessimistic classification.

### 3.3 AnyIO Absolute (M1) — No asyncio Exceptions

**Decision**: All async code uses AnyIO. Never `asyncio` directly. Blocking I/O wrapped in `anyio.to_thread.run_sync`.

**Rationale**: Runtime portability, prevents event-loop collisions across Provider Fabric. MCP Hub C-5/C-6/C-13 bugs were asyncio/AnyIO conflicts.

**Evidence**: SOVEREIGN_MANDATES.md M1; R44_comprehensive_systems_review.md C-3, C-5, C-6, C-13; ORACLE_STACK_CANONICAL.md §12.

**Enforcement**: `make temple-grade` T5 gate. Pre-commit checks.

### 3.4 Soul Integrity (M11) — L1→L2→L3 Pipeline Final

**Decision**: Agents write L1→L2→L3 directly to `proposed_lessons.yaml` (blind staging). **Regex distillation pipeline SCRAPPED** (D-538, DOC-1). Scribe agent is canonical executor. Session stop hooks MUST trigger write.

**Rationale**: Carmack verdict: regex distillation was "fortune-cookie generation." Manual §2.3: agents write their own lessons. That works.

**Evidence**: SOVEREIGN_MANDATES.md M11; OMEGA_ENGINE.md §2 (C-0.5 scrapped); DEBUT_REMEDIATION_MANUAL.md §2.3; PIVOT_LOG.md D-521.

**Status**: ✅ WORKING — agents write 5 lessons/session; `session_end.py` preserves + timestamps; `get_soul_prompt()` hydrates from `approved_lessons.yaml`.

### 3.5 Circuit Breaker Unification (C-6') — HealthMonitor Factory

**Decision**: `HealthMonitor.get_breaker()` is the SINGLE canonical factory. Sliding-window rate-based failure detection + CUSUM drift detection. 5-state FSM. Deprecated 6 clone implementations with migration path.

**Rationale**: Factory-Before-Third Rule — extract canonical factory after second implementation, not third. 17 `class.*Breaker` hits reduced to 1.

**Evidence**: PIVOT_LOG.md D-376b; SOVEREIGN_ARK_BLUEPRINT.md §6; UNOVERENGINEERING_PLAN.md §2.1 (corrected); DEBUT_REMEDIATION_MANUAL.md §5 DEL-1.

**Status**: ✅ COMPLETE — 5/7 clones deprecated; 2 unmigrated → P-5 ticket open.

### 3.6 OOMProtector 3-Signal Fusion (C-2') — RAM + cgroup + systemd

**Decision**: Three-signal fusion: PSI (memory pressure) + MemAvailable (kernel) + cgroup (container limits). 5-tier decision logic. **Simplified to 2-signal per D-529** (remove cgroup pressure — duplicates PSI on bare metal).

**Rationale**: ResourceGuard default was wrong (12GB vs 8GB real UMA). Carmack: "server-grade theater for single-user desktop." Lilith: "cgroup pressure duplicates PSI on bare metal." Saves ~1,200 lines.

**Evidence**: PIVOT_LOG.md D-529; SOVEREIGN_ARK_BLUEPRINT.md §6; OMEGA_ENGINE.md §3 (OOMProtector); DEBUT_REMEDIATION_MANUAL.md §2.3.

**Status**: ✅ COMPLETE — C-2' done; D-529 ratified simplification.

### 3.7 Vault Honesty (DEL-1 Week 3) — Path A Only

**Decision**: **Path A (debut)**: delete `src/omega/vault/` from product surface; keep `crypto.py` in forge if wanted later. **Path B (minimal)**: `crypto.py` + ≤50-line store; Gateway reads env/keyring only. **Keyblind/Authy/Agent Vault REJECTED for debut** (UNOVERENGINEERING_PLAN.md §2.6 = rejected option).

**Rationale**: VaultCore is a sidecar — CLI calls missing `store_credential`, Gateway dumps `.env` into `os.environ`. Not wired. 2,039 LOC custom code → 3 community tools is post-debut.

**Evidence**: DEBUT_REMEDIATION_MANUAL.md §5 DEL-1 Week 3; UNOVERENGINEERING_PLAN.md §2.6 (DOC-1 stamp); SOVEREIGN_ARK_BLUEPRINT.md V-1 ticket.

**Status**: 🟡 BACKLOG — Architect decides A vs B at Week 3.

### 3.8 Router Collapse (DEL-1 Week 2) — Single Router Contract

**Decision**: Keep `ProviderSelector` + `config/providers.yaml` local-first list. Delete `TriageRouter` AND `SemanticRouter` in SAME change as `Oracle._select_model` / `Oracle._route_by_domain`. Entity pick: `EntityRegistry.find_by_domain` (keyword) enough for debut. Optional one embed call later — not stacked.

**Rationale**: Query passes RAGRouter → Iris → SemanticRouter → TriageRouter → ProviderSelector → Gateway fallback → optional RoutingTable = 5 historical answers. One contract test: single `RouteDecision` (entity, model, provider, reason). Fails if second router module imported on talk path.

**Evidence**: DEBUT_REMEDIATION_MANUAL.md §3.2, §5 DEL-1 Week 2; SOVEREIGN_ARK_BLUEPRINT.md §3.2; OMEGA_ENGINE.md §3.

**Acceptance**: `rg TriageRouter src/omega` and `rg SemanticRouter src/omega` empty; two concurrent `omega talk` calls: one local slot, user-visible busy or explicit cloud warning (`cost_warning`), never silent cloud leak.

### 3.9 Memory Tier — SQLiteVec + FTS5 + RRF (Qdrant Deleted)

**Decision**: `sqlite-vec` is the **SINGLE Core store**. 7 per-model vec0 collections + FTS5 BM25 + RRF fusion (k=60) via `HybridSearchEngine`. **Qdrant is optional WAD adapter only** — implements `IVectorStoreAdapter` for stacks opting into external vector infra. No new core dependency on Qdrant/FAISS/PostgreSQL.

**Rationale**: 8GB UMA carve-out (not 12GB). Qdrant 6G container contradicts sqlite-vec SSOT; OOM on 8G. `QdrantAdapter` class in `vector_adapters.py` marked DEPRECATED heritage reference.

**Evidence**: OMEGA_ENGINE.md §3 (Vector Store Decision UO-4); ROC_JIT_RAG_LOCAL_DISCOVERY.md §1; DEBUT_REMEDIATION_MANUAL.md §5 DEL-1 Week 1 (delete QdrantAdapter); STRATEGY_CORPUS_MAP.md §0 (Qdrant = ARCHIVE).

**Status**: ✅ WORKING — `SQLiteVecAdapter` + `ConversationFTSIndex` + `HybridSearchEngine.fetch_and_fuse()` all operational.

### 3.10 MCP Architecture — Streamable HTTP, OAuth 2.1, No Redis

**Decision**: MCP Hub dual transport live (SSE + Streamable HTTP); client SEP-2575 compliant. OAuth 2.1 + PKCE for auth. **Redis removed from core** — migrated to SQLite + Honker (wafris.org precedent, Honker 2957 stars). `hivemind_redis.py` is LIVE (imported by hub_tools, watchdog, bridge) — migrate before delete.

**Rationale**: MCP 2026-07-28 GA deadline. SDK v2.0.0 stable. Hub still on `mcp.server.fastmcp` (SDK v1). Redis in budget_guard, youtube_worker, memory providers — deeper than Hivemind.

**Evidence**: SOVEREIGN_ARK_BLUEPRINT.md §6 (C-4b ✅); UNOVERENGINEERING_PLAN.md §4.1; RESEARCH_PLAN_PHASE1_4.md R28; DEBUT_REMEDIATION_MANUAL.md (MCP audit C-4a ✅).

**Status**: 🟡 C-4b Streamable HTTP ✅; Redis migration = post-debut (UO-7 Phase 3).

---

## §4 The Debut Path (Manual §5, Carmack-Compressed)

**Phase A (Weeks 1-2): PR/Debut Completion** — Sequential, measurable gates only.

| Week | Ticket | Owner | Acceptance Gate |
|------|--------|-------|-----------------|
| 1 | P0-1: Key rotation + history scrub | Architect → Roc | `git log -S 'csk-' --all` clean; 137 checkpoints pruned; 2 commits pushed |
| 1 | PUB-1: Publication allowlist | Kali + Architect | `release/debut` branch from allowlist; CI green; no forge leaks |
| 1-2 | INST-1: Install honesty | Ma'at/N3 | Fresh venv, no warp/Redis: `pip install -e ".[native,cli]"` → `omega talk "hello"` native, exit 0 |
| 2 | P0-1c: gitleaks pre-commit + CI | Ma'at + Verity | Planted `sk-` fixture fails CI |

**Phase B (Weeks 3-6): Post-Debut Cleansing** — DEL-1 → P2 → P3 → P4

| Week | Focus | Key Actions | Owner |
|------|-------|-------------|-------|
| 3 | DEL-1 Week 1: Pure deletion | `routing/table.py`, `miap.py`, `pool_tracker.py`, `pool_state.py`, `search_circuit_breaker.py`, `QdrantAdapter`, `FleetOrchestrator`, Pantheon regexes, `record_first_breath`, vault CLI default | Roc + Ma'at |
| 4 | DEL-1 Week 2: Router collapse | `TriageRouter` + `SemanticRouter` → single router; tests rewritten with code | Ma'at |
| 5 | DEL-1 Week 3: Vault honesty | Path A (delete `src/omega/vault/`) OR Path B (minimal store) — Architect decides | Ma'at + Architect |
| 6 | P2: Lint debt | 11,400 violations → 0; no `--exit-zero` for E9/F63/F7/F82 | Verity |
| 7 | P3: CI/hygiene | Real suite, no vanity counts; gitleaks enforced; `make temple-grade` all green | Verity |
| 8 | P4: Polish | README, CONTRIBUTING, tag v0.1.0, `pip install -e .` works | Kali + Verity |

**Measurable Gates Only** (from Manual §8):
- `rg -n "sk-[a-zA-Z0-9]{16,}\|csk-\|AIza\|ghp_\|xai-" --glob '!docs/archive/**' --glob '!**/DEBUT_REMEDIATION_MANUAL*'` → 0 matches
- `rg -n "warp-proxy-pool\|qdrant-client\|^    \"redis" pyproject.toml` → 0 matches
- `rg -n "TriageRouter\|SemanticRouter\|RoutingTable\|RAGRouter" src/omega` → 0 matches
- `OMEGA_ENV= source .venv/bin/activate && omega talk "hello"` → native, IS_CLOUD=False, exit 0
- `pytest -q --tb=no` → report passed/failed/skipped/errors (never "green")

---

## §5 Post-Debut Unoverengineering (UO-1→UO-4)

**Phase UO-1: Library Swaps** (interlock-cb, Pydantic v2, stamina, structlog, prometheus_client)
- **interlock-cb v2.1.3** over pybreaker (sync+async, sliding-window, slow-call detection, httpx2 transport)
- **Pydantic v2**: `yaml.safe_load()` + `model_validate()` — NOT `model_validate_yaml()` (doesn't exist)
- **stamina** vs tenacity vs interlock-cb retry pipeline — spike one provider, measure glue-code deletion
- **structlog v26.1.0** — replace dead `setup_json_logging()` (M9 blocker)
- **prometheus_client** textfile collector at `:8016/metrics` (local-only, M8 compliant)

**Phase UO-2: Coordination Consolidation**
- Kill `HandoffState` → consolidate to `HandoffPacket` (migrate vet-008 heritage tag)
- Soul distiller consolidation — scribe deleted, `miap.py` (631 lines) verify dead code → delete
- HMC Hub → `hub_state.yaml` + `hub_log.jsonl`; pre-commit gate: max 100 lines/week; TTL archival 7 days

**Phase UO-3: Memory Tier Simplification**
- SQLiteVec + FTS5 + RRF (3 tiers: file-based, sqlite-vec+FTS5, raw archive)
- Kill Recall tier (`recall.py` 786 lines) — duplicates FTS5 ranking
- Kill Warm tier (Redis) — ~8GB RAM too small; M7: RAM goes to inference
- Kill Archival tier (gzip) — files ARE the archive
- Install Honker, migrate Redis use cases (memory_store, budget_guard, youtube_worker, providers, hivemind_redis) → Honker/SQLite
- **Sequence**: providers → workers → hivemind → budget_guard LAST (needs SQLite fallback first)

**Phase UO-4: Enforcement Gates**
- `make check-instruction-hierarchy` — no doc overrides higher-priority doc
- `make check-mandate-compliance` — mechanical %, not narrative (denominator=27)
- `make check-no-schema-drift` — no >1 handoff schema
- Pre-commit hook: HMC ≤100 lines/week
- `make check-freshness` — LAST_VERIFIED ≤7 days → CI warning
- `make check-distiller-count` — only 1 canonical distiller
- **Hard constraints**: dep count ceiling, import time budget, cold start <Xms, RSS ceiling, Temple-Grade all green

---

## §6 Heritage & Patterns (What We Kept From Where)

### [id-soft:] Tags with Vet Records → CREDITS_CANONICAL.md Mapping

| Pattern | Source | Tag | Vet Status |
|---------|--------|-----|------------|
| WAD System | Doom 1993 | `[id-soft: doom-1993] WAD System` | ✅ PROMOTED |
| BSP Culling | Doom 1993 | `[id-soft: doom-1993] BSP Culling` | ✅ PROMOTED |
| Zone Memory Allocator | Quake 1996 | `[id-soft: quake-1996] Zone Memory` | ✅ PROMOTED |
| cvar Table | Quake 1996/1999 | `[id-soft: quake-1996] cvar` | ✅ PROMOTED |
| Thinker Chain | Quake 1996 | `[id-soft: quake-1996] Thinker Chain` | ✅ PROMOTED |
| QVM / Bot AI | Quake III 1999 | `[id-soft: quake3-1999] QVM` | ✅ PROMOTED |
| Game DLL / Client Prediction | Quake II 1997 | `[id-soft: quake2-1997] Game DLL` | ✅ PROMOTED |
| Scripting / GUI Framework | DOOM 3 2004 | `[id-soft: doom3-2004] Scripting` | ✅ PROMOTED |
| ZONEID Pattern | Doom 1993 | `[id-soft: doom-1993] ZONEID` | ✅ PROMOTED |
| Lazy Deletion + Grace Period | Doom 1993 + Quake 1996 | `[id-soft: doom-1993] Lazy Deletion` | ✅ PROMOTED |
| Hard-Boundary Struct | Quake 1999 | `[id-soft: quake3-1999] Hard-Boundary` | ✅ PROMOTED |
| High-Bit Leaf Trick | Doom 1993 | `[id-soft: doom-1993] High-Bit Trick` | ✅ PROMOTED |
| Fixed-Size Active Set | Doom 1993 | `[id-soft: doom-1993] Active Set` | ✅ PROMOTED |
| Network Channel (netchan) | Quake 1999 | `[id-soft: quake3-1999] netchan` | ✅ PROMOTED |
| Unified Memory (idHeap) | DOOM 3 2004 | `[id-soft: doom3-2004] idHeap` | ✅ MAPPED |
| Precomputed Lookup Table | Doom 1993 | `[id-soft: doom-1993] Precomputed Lookup` | ✅ PROMOTED |
| Job-Worker Queue | DOOM 3 BFG 2012 | `[id-soft: doom3bfg-2012] Job-Worker` | ✅ APPROVED |
| Knowledge Leak Detection | DOOM 3 2004 | `[id-soft: doom3-2004] Leak Detection` | ✅ APPROVED |

**Total**: 21 legitimate mappings (5 REJECTED archived in HERITAGE_VET_LOG.md — vet-001 8-char name cap rejected).

### Legacy Patterns Ported

| Pattern | Source | Current Location | Status |
|---------|--------|------------------|--------|
| Atomic rename + fsync | XNAI_blueprint.md | `SoulStore` write (C-1') | ✅ PORTED |
| `with_soul_lock` fcntl | entity_registry / legacy | `SoulStore` lock layer (C-1') | ✅ PORTED |
| Memory Guardian /proc/meminfo tiers | healthcheck.py | `OOMProtector` 3-signal (C-2') | ✅ PORTED |
| Circuit breaker fail_max=3 reset=60 | legacy circuit_breaker.py | `HealthMonitor.get_breaker()` (C-6') | ✅ UNIFIED |
| Tenacity exponential retry | legacy stack | **PARKED P2** — apply on openai_compat after C-6' | 🟡 PARKED |
| Provider priority chain | old providers.yaml | §7 fabric (existing order; no Cerebras yet) | ✅ PORTED |

### Patterns Rejected

| Pattern | Reason | Disposition |
|---------|--------|-------------|
| Cerebras/Groq free tiers | D-351: no new providers until fabric systematized | REJECTED for now; matrix preserved in Roc report |
| pybreaker | Sync-only, M1 violation; interlock-cb recommended | REJECTED |
| Tenacity manual retry | Interlock-cb v2 has built-in retry pipeline | REJECTED (use interlock-cb) |
| QdrantAdapter | Contradicts sqlite-vec SSOT; OOM on 8G UMA | ARCHIVE — DEL-1 Week 1 deletes |
| Soul distillation regex pipeline | Carmack: "fortune-cookie generation" | SCRAPPED (D-538) |
| MIAP / Hive Evolution | D-495: Hivemind shipped; un-overengineering | CANCELLED |

---

## §7 Research Force Multipliers (Carmack Session 2026-07-30)

**Source**: `CARMACK_DEFINITIVE_STRATEGY_20260730.md` — 24 proposals → top 5 force multipliers with deep-dive evidence (5,000+ lines across 6 documents).

| # | Force Multiplier | Key Finding | Phase | Hardware Gate |
|---|------------------|-------------|-------|---------------|
| 1 | **Ornith-1.0-9B** | Qwen3.5 fine-tune (24 GatedDeltaNet + 8 Gated Attention), MIT license, 69.4 SWE-Bench, 400K context on 16GB GPU. **FAIL: prose-bias kills tool-calling** → mandatory dual routing with Qwen3.5-9B. | Phase 2 | 16GB+ VRAM (Q4_K_M=5.63GB + KV cache) |
| 2 | **Vulkan llama.cpp Backend** | 14,471/14,471 tests pass. Ryzen 5700U iGPU: **8-15 tok/s on 7B Q4** (usable). AMD RDNA3: Vulkan beats ROCm 20-22% TG. CUDA gap: 10-36% on NVIDIA. | Phase 1 | Any GPU (Vulkan = GPU-agnostic binary) |
| 3 | **llama-optimus Auto-Tuning** | Real project (42★ GitHub, PyPI, MIT). Optuna Bayesian optimization. **15-35% CPU speedup** (NOT 65% — that was Claude Fable 5 CUDA kernel, misattributed). Pre-calibration at model install time. | Phase 1 | None (CPU-only works) |
| 4 | **ModelAwareInstructionRouter** | **No existing system adapts instructions to model capability.** 30-60% token reduction for local models. ~400 lines Python. YAML config per capability tier (T0 Frontier → T3 Nano). Middleware between Model Selection and Prompt Assembly. | Phase 0 | None (pure Python) |
| 5 | **Workstation Hardening** | IDE extensions = #1 supply chain vector 2026 (May 19 GitHub breach: 3,800 repos via one extension). 454K malicious packages 2025-2026. FIDO2 SSH production-ready (OpenSSH 9.6+). `scripts/omega-harden-workstation.sh` created. | Phase 0 | None |

**Dependency Graph**:
```
PHASE 0 (This Week — ~4 days)
├── P0.1 Prompt Cache Fix (CLAUDE_CODE_ATTRIBUTION_HEADER=0) — 1 min ✅ DONE
├── P0.2 Hardening Script — 1 hr ✅ DONE (script exists, run it)
└── P0.3 Instruction Router — 3.5 days 🔲 DO

HARD GATE: GPU Budget Approved

PHASE 1 (Next Sprint — 1 week)
├── P1.1 Acquire Discrete GPU (RTX 3090 24GB ~$700 used = best value)
├── P1.2 Rebuild llama.cpp with Vulkan (GGML_VULKAN=ON)
└── P1.3 Calibrate with llama-optimus (4 hrs)

HARD GATE: Model Inference ≥40 tok/s

PHASE 2 (Sprint after GPU — 3 days)
├── P2.1 Deploy Ornith-9B (dual routing with Qwen3.5-9B mandatory)
├── P2.2 Deploy Qwen3.5-9B
└── P2.3 Register in ModelGateway

PHASE 3 (Ongoing)
├── P3.1 TTFT-Optimized Routing (12 hrs)
├── P3.2 llama-optimus in CI (4 hrs)
└── P3.3 Network Kill Switch + VPN (8 hrs)
```

**Status**: Phase 0 = research complete, awaiting implementation go/no-go. Phase 1 = hardware-gated (GPU acquisition). Phase 2 = depends on Phase 1. Phase 3 = parallel with Phase 2.

---

## §8 Open Questions & Risks (Honest)

| # | Question | Risk Level | Trigger for Resolution | Owner |
|---|----------|------------|------------------------|-------|
| 1 | **GPU Budget Approval** — RTX 3090 24GB ~$700 used required for Ornith-9B | HIGH | Architect decision; fund from cloud savings (Ornith local replaces Gemma 31B cloud) | Architect |
| 2 | **Vault Path A vs B** — Delete `src/omega/vault/` entirely (Path A) or minimal store (Path B)? | MEDIUM | DEL-1 Week 3; Architect decides | Architect |
| 3 | **Redis Migration Completeness** — `hivemind_redis.py` LIVE (hub_tools, watchdog, bridge); budget_guard, youtube_worker, providers also use Redis | HIGH | UO-7 Phase 3; migrate providers → workers → hivemind → budget_guard LAST | Ma'at |
| 4 | **MCP v2 Migration Scope** — Hub still SDK v1 FastMCP; SDK v2.0.0 stable Jul 28 | MEDIUM | Post-debut; prefer external FastMCP (SearXNG precedent) | Ma'at |
| 5 | **C-3 Restic Backup Operational** — Timer enabled but oneshot FAILED (missing `OMEGA_VAULT_PASSPHRASE` / `.env.backup`) | MEDIUM | Architect secrets required; ≥1 successful snapshot | Architect |
| 6 | **V-10 AppArmor Container Hardening** — Containers unconfined; no `podman` AppArmor profile applied | HIGH | Post-debut; GAP in SOVEREIGN_ARK_BLUEPRINT.md §8 | Ma'at |
| 7 | **V-9 IA2 Envelope Freshness/Signature** — `_meta` envelope in `mcp_core/compliance.py` lacks freshness/signature check | MEDIUM | Post-debut; GAP in SOVEREIGN_ARK_BLUEPRINT.md §8 | Ma'at |
| 8 | **D-308 Ubuntu 25.10 Toolchain** — Kernel/AppArmor/Podman notes residual; OS deployment target = Ubuntu 24.04 LTS or 26.04 LTS (25.10 EOL) | LOW | Env risk during C; monitor | Ma'at |
| 9 | **G-1 Workhorse Continuity** — Free Gemma 4 31B dead (16k input limit); billing Tier 1 / Antigravity OAuth / OCZ+WARP / paid alt paths | HIGH | PARKED per DOC-1; post-debut | Architect |
| 10 | **W-1 WARP Pool** — `/usr/local/bin/warp-ns-setup` truncated; 1/3 SOCKS active; bridges flaky | MEDIUM | PARKED per DOC-1; sudo fix ns-setup → reg → bridges | Architect |
| 11 | **Instruction Router Integration Risk** — Wrong tier assignment = architectural failure | MEDIUM | Pattern-based mapping + T2 default fallback; validation gates in CARMACK_DEFINITIVE_STRATEGY.md | Ma'at |
| 12 | **TTFT Routing Loops** — Model A → B → A oscillation | MEDIUM | TTL on negative routing decisions; Phase 3 | Ma'at |
| 13 | **SoulStore Multi-Path Elimination Completeness** — 4 writers → 1; verify no hidden paths | LOW | C-1' COMPLETE; Verity audit | Verity |
| 14 | **Heritage Vet Coverage** — 121 `[id-soft:]` tags; all vetted per M14? | LOW | `make heritage-vet` CI gate | doom_guy |
| 15 | **Test Suite Timing** — Full suite 1706 collected; timeout risk phantom per GLM52 F12 | LOW | `time make test` with 600s budget; measured | Verity |

---

## §9 Deep Engine Map (Mental Model)

### Oracle (`src/omega/oracle/oracle.py`)
- **Responsibility**: Intent detection, entity routing, Iris speculative decode, dispatch to ModelGateway
- **Key Files**: `oracle.py`, `entity_registry.py`, `entity_workspace.py`, `context_builder.py`, `session_lifecycle.py`, `subagent_dispatcher.py`
- **Invariants**: 
  - Single `RouteDecision` contract (entity, model, provider, reason)
  - No stacked routers (RAGRouter, SemanticRouter, TriageRouter deleted DEL-1)
  - `talk()` → speculative decode → escalation → `_route_by_domain()` → `_summon()`
  - Soul evolution via `_track_soul_evolution()` → `SoulStore` atomic write
- **Dependencies**: ModelGateway, MemoryStore, EntityRegistry, HealthMonitor, ResourceGuard, OOMProtector, AdmissionController

### ModelGateway (`src/omega/oracle/model_gateway.py`)
- **Responsibility**: 8-backend provider fabric, fallback chain, resource protection, streaming resilience
- **Key Files**: `model_gateway.py`, `providers.py`, `backends/*`, `health_monitor.py`, `resource_guard.py`, `admission_controller.py`, `oom_protector.py`
- **Invariants**:
  - Local-first priority chain enforced (native-gguf → lmster → Ollama → cloud)
  - `HealthMonitor.get_breaker()` = single canonical breaker factory
  - `ResourceGuard` Semaphore(1) + `OOMProtector` 3-signal = one admission controller
  - Streaming: chunk timeout 30s (heartbeat, continue), total timeout 5min (graceful fallback)
  - `GenerateResult` dataclass carries `provider_name` from actual backend (M22 provenance)
- **Dependencies**: ProviderRegistry (SSOT for `is_cloud`), config/providers.yaml, native-gguf/llama-cpp-python

### MemoryStore (`src/omega/memory_store.py`)
- **Responsibility**: Hot/Warm/Cold tiering, hybrid FTS5+vector search, conversation persistence, ACP event stream
- **Key Files**: `memory_store.py`, `sqlite_vec_adapter.py`, `vector_adapters.py`, `hybrid_search.py`, `fts_index.py`, `recall.py` (DEPRECATED)
- **Invariants**:
  - `sqlite-vec` = SINGLE core store (7 per-model vec0 collections + FTS5 BM25 + RRF k=60)
  - `IVectorStoreAdapter` ABC with 3 impls: SQLiteVecAdapter (core), MemoryVectorAdapter (fallback), QdrantAdapter (DEPRECATED heritage)
  - `HybridSearchEngine.fetch_and_fuse()` = concurrent FTS + Vector → RRF fusion
  - Entity isolation via `entity_name` partition key in vec0 + WHERE clause in FTS5
  - ACP event stream: JSONL `updates.jsonl` + `rewind_points.jsonl` per session
- **Dependencies**: sqlite-vec, sqlite3 (FTS5), config/jit_rag.yaml (PARKED)

### ProviderFabric (`src/omega/oracle/providers.py` + `backends/`)
- **Responsibility**: Provider implementations, fallback chain, key rotation, classification
- **Key Files**: `providers.py`, `provider_registry.py`, `backends/native_gguf.py`, `backends/openai_compat.py`, `backends/google.py`, `backends/lmster.py`, `backends/ollama.py`
- **Invariants**:
  - `ProviderRegistry` reads `is_cloud` from `config/providers.yaml` (SSOT, D-520)
  - Unknown providers = cloud (pessimistic)
  - GoogleKeyPool: 8-key round-robin with rate-limit tracking (PARKED)
  - NativeGGUFProvider behind ResourceGuard (C-4 fixed)
  - Streaming config in providers.yaml per cloud provider (M25)
- **Dependencies**: config/providers.yaml, config/models.yaml, llama-cpp-python, httpx2

### Hivemind (`mcp_servers/omega_hub/`)
- **Responsibility**: Cross-agent coordination, workspace locks, live feeds, awareness, handoffs
- **Key Files**: `hub_tools/tools.py` (3649 lines — GOD MODULE FREEZE), `state.py`, `background.py`, `gateway.py`, `middleware.py`, `hivemind_redis.py`
- **Invariants**:
  - Feature-freeze; bug fixes only (SOVEREIGN_ARK_BLUEPRINT.md §4)
  - 6 MCP tools: post_context, get_awareness, heartbeat, get_live_feed, get_workspace_lock, acknowledge
  - Handoff lifecycle: pending → active → completed → stale (4-state)
  - `hivemind_redis.py` LIVE — migrate to Honker/SQLite before Redis removal
  - Dual transport: SSE + Streamable HTTP (C-4b ✅)
- **Dependencies**: Redis (currently), Honker (target), MCP SDK v2.0.0

### MCP (`mcp_servers/omega_hub/` + `src/omega/mcp_core/`)
- **Responsibility**: MCP server for tools, research, stats; client for external MCP servers
- **Key Files**: `hub_tools/tools.py`, `mcp_core/client.py`, `mcp_core/compliance.py` (IA2 envelope)
- **Invariants**:
  - Streamable HTTP + OAuth 2.1 + PKCE (C-4b)
  - Client SEP-2575 compliant
  - IA2 envelope in `_meta` lacks freshness/signature check (V-9 GAP)
  - Firecrawl MCP on :8015 (SSE)
- **Dependencies**: MCP SDK v2.0.0, Honker (for Redis replacement)

### Soul (`src/omega/soul_store.py` + `src/omega/oracle/entity_workspace.py`)
- **Responsibility**: soul.yaml persistence, L1→L2→L3 distillation, cross-pollination, hydration
- **Key Files**: `soul_store.py`, `entity_workspace.py`, `soul_utils.py`, `proposed_lessons.yaml`, `approved_lessons.yaml`
- **Invariants**:
  - Atomic writer: tempfile → write → fsync → os.replace → fsync parent → flock → .bak rotation (4-layer guarantee)
  - Agents write L1→L2→L3 directly to `proposed_lessons.yaml` (blind staging, M11)
  - Scribe agent = canonical distillation executor
  - `get_soul_prompt()` hydrates from `approved_lessons.yaml` filtered by `session_id` (D-290)
  - Session end hook preserves proposals + timestamps (D-VOS-002)
- **Dependencies**: fcntl.flock (cross-process safe), anyio.Lock (async), yaml

### CLI (`src/omega/cli/oracle_cli.py`)
- **Responsibility**: Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version)
- **Key Files**: `oracle_cli.py`, `install.sh`, `Makefile`
- **Invariants**:
  - `install.sh` uses `pip install -e ".[native,cli]"` — NOT `.[all]` (INST-1)
  - `make setup` parity or delete from README
  - Version alignment: `src/omega/__init__.py` == `pyproject.toml`
  - `omega talk "hello"` → native-gguf, IS_CLOUD=False, exit 0 (CP-1/CP-3)
- **Dependencies**: Oracle, ModelGateway, EntityRegistry, config/omega.yaml

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_consolidated_decisions ⬡ 2026-08-17*
