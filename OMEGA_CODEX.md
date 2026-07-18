# ⬡ OMEGA ⬡ CODEX ⬡ 2026-07-18T05:46:41.566102+00:00 ⬡

> **Generated via Stack-Cat Protocol**. This is the single startup read target for all agents. It contains the concatenated active state of the engine, mandates, workflow, and refinement protocols.

## 🔄 HYDRATION SEQUENCE (D-277)

After compaction or restart, execute in strict order:

1. `omega-hub_hivemind_get_awareness()` — Who is here?
2. `git status && git log --oneline -5` — What is committed?
3. Read OMEGA_CODEX.md — FULL file, no limit parameter. You are doing this now
4. Read `.opencode/anchored-summary.md` — What was I doing?
5. Present a rehydration report. Pause. Await user direction.

> Codex generated: 2026-07-18T05:46:41.566102+00:00 | Regenerate: `make codex`
> If timestamp is >24h old, run `make codex` before reading further.

---
## 📁 GROUP: CODEX

### OMEGA_ENGINE.md
**Type**: markdown
**Size**: 11816 bytes
**Lines**: 149

# Omega Engine — Single Source of Truth
# ⚠️ SYSTEM STATE SSOT — Authoritative truth for engine state and metrics.
# AP-OMEGA-SST-v2.6.0

> **This document is the authoritative truth for the Omega Engine.**
> Every agent reads this file for engine state.
> **Full archive**: `docs/archive/coordination/OMEGA_ENGINE-full-20260708.md`

---

## §1 Identity

**Omega Engine** is the universal, community-owned runtime for sovereign AI.
- **Cognitive Sovereignty**: Local inference is the floor; local verification is the ceiling.
- **Local-first**: Cloud is a teacher and strategic partner, never a dependency.
- **WAD Architecture**: Engine → IWADs → PWADs (inspired by id Software).
- **Standalone Packages**: Core capabilities published as independent PyPI packages (`omega-sieve`, `omega-doc-reader`) for community use.

---

## §2 Current State (2026-07-19)

| Metric | Value | Status | LAST_VERIFIED |
|--------|-------|--------|---------------|
| Tests | **1398 passed** (43 skipped, 7 xfailed) | ✅ Functional tests pass, 2 test infra issues remain | 2026-07-18 |
| Mandates | **23 (M1-M23)** | ✅ All enforced | 2026-07-13 |
| **Mandate Compliance** | **13/23 FULL (56.5%)** — 5 Partial, 5 Fail | ❌ Systemic Run Side gaps | 2026-07-15 |
| **Failed Mandates** | M5, M11, M12, M15, M23 | ❌ Soul distillation, handoff, continuity, failure integrity | 2026-07-15 |
| Fleet | **12 agents + 2 entities (14 total)** | ✅ Cap: 14 | 2026-07-18 |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 |
| **Third-Party Registry** | **18/19 repos cloned** — P0: 4/4, P1: 5/5, P2: 6/6, P3: 1/4 | ✅ P0-P2 Complete | 2026-07-18 |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 |
| Shared modules | **3** (`omega-vetala` v2.0.0, `omega-sieve` v0.1.0, `omega-doc-reader` v1.0.0) | ✅ Release-ready | 2026-07-13 |
| **D-281 Substrate Repair** | **ALL 4 PHASES COMPLETE** — Soul injection, config_resolver, M2 Firewall, Codex separation | ✅ 11 commits across 5 agents | 2026-07-17 |
| **D-282 sqlite-vec Strike 10** | **COMPLETE** — PRAGMA SSOT converged, 4 concurrency tests | ✅ cache_size 512MB→32MB, wal_autocheckpoint 1000→500 | 2026-07-17 |
| **D-283 Mnemosyne Phase 1** | **COMPLETE** — HybridSearchEngine RRF k=60, Memory Blocks | ✅ 752/754 tests pass | 2026-07-16 |
| **D-283 Mnemosyne Phase 2** | **DESIGN COMPLETE** — RecallStore, power-law decay, quality scoring | 🟡 27/29 recall tests pass (2 test infra issues) | 2026-07-17 |
| **MIAP** | **MERGED** — Multi-Instance Agent Protocol for context collision | ✅ 13 tests, committed 03192d8 | 2026-07-17 |
| **HMC Quad-Forge** | **4-mind council** — Kali, Roc, Researcher, Grok CLI | ✅ All 4 agents completed sprint tasks | 2026-07-17 |
| **Atomic Execution Matrix** | **RATIFIED** — Code + CI Gate + Doc as single atomic unit | ✅ 5 new protocol docs + CI gates defined | 2026-07-15 |
| **Soul Architecture v2.0** | **RATIFIED** — Intelligence Pipeline, Scorecard, Scribe separation | ✅ `make soul-audit` gated | 2026-07-15 |
| **PWAD Capability Lattice** | **RATIFIED** — Security boundary for active code in PWADs | ✅ `make capability-check` gated | 2026-07-15 |
| **Mandate Governance Protocol** | **RATIFIED** — Amendment, exemption, conflict resolution | ✅ `make mandate-amendment-check` gated | 2026-07-15 |
| **Omega Kernel Architecture** | **RATIFIED** — `kernel/` vs `runtime/` boundary | ✅ `make kernel-import-check` gated | 2026-07-15 |
| SearXNG MCP | **Streamable HTTP on :8018** | ✅ Migration complete | 2026-07-13 |
| Omega Hub MCP | **Dual-transport** (SSE /sse + Streamable HTTP /mcp) on :8016 | ✅ Already dual | 2026-07-13 |
| Firecrawl MCP | **SSE on :8015** | ⏳ Needs Streamable HTTP migration | 2026-07-13 |
| Local inference ratio | **TARGET: ≥80%** (configurable gate, default OFF) | 🟡 Aspirational | 2026-07-13 |
| **KV Cache Quantization** | **LOCKED: q8_0 on CPU (Zen 2)** — No Flash Attention/GPU required | ✅ Research complete | 2026-07-13 |
| **YouTube Researcher V2** | **9-Layer Temporal Knowledge Observatory** — L1-L9 complete, 15 contract tests pass | ✅ Operational | 2026-07-13 |
| **Session Namespace Isolation** | **DESIGN COMPLETE (D-290)** — MIAP-wired session-scoped directories | 🟡 5 preconditions, 5 critical fixes from Nemotron review | 2026-07-18 |
| **MIAP Phase 0** | **PLANNED (D-291)** — ReplayMode, Two-Log, IntentionValidator, CheckFunctions, LiteTopic | 🟡 6 sessions estimated | 2026-07-18 |
| **MACP Alignment** | **PLANNED (D-292)** — Hivemind handoffs with `macp_mode` for interoperability | 🟡 Aligns with IETF draft-li-dmsc-macp-05 | 2026-07-18 |
| **Experience Repository** | **PLANNED (D-294)** — AgentRR-style L0→L1→L2 distillation via Scribe | 🟡 Trace-to-eval loop (D-295) | 2026-07-18 |
| **D-298 Decision Workspace** | **GROUNDED MEDITATION COMPLETE** — T0+T1-core verdict (7h), 23 decisions cataloged, Grok CLI handoff submitted | ✅ 102 files committed at 3542188, ho_749ed27155cd | 2026-07-19 |

---

## §3 Core Subsystems

| Subsystem | Module | Status | Description |
|-----------|--------|--------|-------------|
| **Oracle** | `src/omega/oracle/` | ✅ Operational | Intent detection, entity routing, Iris speculative decode |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` | ✅ Operational | YAML-backed entity CRUD, auto-scaffolds sovereign workspaces |
| **Model Gateway** | `src/omega/oracle/model_gateway.py` | ✅ Operational | 8-backend provider fabric (native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode → Copilot → Mock). P3 fixed graceful fallback + path/spec resolution |
| **Memory Store** | `src/omega/memory_store.py` | ✅ Operational | Hot/Warm/Cold/Temp tiers, hybrid FTS5+vector search |
| **Vector Store** | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Strike 10 COMPLETE | `IVectorStoreAdapter` impl: sqlite-vec (FTS5 + vec0 + SQL edges). PRAGMA SSOT converged: cache_size 32MB, wal_autocheckpoint 500 |
| **Config Resolver** | `src/omega/governance/config_resolver.py` | ✅ Phase II COMPLETE | Pure Path constants, lazy `get_active_iwad()`, single source of truth for all WAD paths |
| **Hybrid Search** | `src/omega/memory/hybrid_search.py` | ✅ D-283 Phase 1 COMPLETE | RRF k=60 fusion of FTS5 + vector results. 20 contract tests + 8 RRF math vectors |
| **Recall Store** | `src/omega/memory/recall.py` | 🟡 D-283 Phase 2 DESIGN COMPLETE | Quality-weighted warm memory tier with power-law decay. 27/29 tests pass |
| **MIAP** | `src/omega/coordination/miap.py` | ✅ MERGED | Multi-Instance Agent Protocol for context collision prevention. 13 tests |
| **Soul Utils** | `src/omega/soul_utils.py` | ✅ Phase I COMPLETE | Multi-path soul context extractor for 31 entities |
| **WAD Loader** | `src/omega/oracle/wad_loader.py` | ✅ Operational | V2 schema with heritage fields. Sovereign WAD Protocol (SWP) pending |
| **Ingestion Pipeline** | `src/omega/ingestion/` | ✅ Operational | T1→T2→T3 tiered extraction, TriangulationVerifier, CAS |
| **Sovereign Sieve (Standalone)** | `packages/omega-sieve/` | ✅ v0.1.0 | `pip install omega-sieve` — T1(Trafilatura)→T2(Surgical)→T3(Crawl4AI) |
| **Document Reader (Standalone)** | `scripts/universal_doc_reader.py` | ✅ v1.0.0 | Reads .docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml |
| **Observability** | `src/omega/observability.py` | ✅ Operational | Trace IDs, event logging, fine-tuning dataset collection |
| **Hivemind** | `mcp_servers/omega_hub/` | ✅ Operational | 6 MCP tools for cross-agent coordination, workspace locks, live feeds |
| **CLI** | `src/omega/cli/oracle_cli.py` | ✅ Operational | Typer CLI (talk, summon, list-entities, add-entity, entity-info, backends, version) |
| **Resource Guard** | `src/omega/oracle/resource_guard.py` | ✅ Operational | AnyIO Semaphore(1) — one model at a time (OOM protection) |
| **CPU Optimizer** | `src/omega/oracle/cpu_optimizer.py` | ✅ Operational | Zen 2 compilation flags, KV cache sizing, speculative decode tuning |

---

## §4 Key Files (Source of Truth)

| File | Purpose |
|------|---------|
| `OMEGA_ENGINE.md` (this file) | System state SSOT — read first |
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws (M1-M23) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap (active) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions (active index) |
| `CREDITS.md` | id Software heritage attribution (active) |
| `docs/strategy/HMC_STRATEGIC_PLAN.md` | 4-mind council roadmap (Quad-Forge) |
| `docs/strategy/D281_PHASE_II_IV_EXECUTION.md` | D-281 Phase II-IV execution plan |
| `docs/archive/coordination/` | Historical session records |
| `data/entities/kali/session_gnosis.md` | Kali's session anchor (M15) |
| `data/coordination/ACTIVE_SPRINT.json` | HMC-SPRINT-04 active sprint config |
| `.opencode/anchored-summary.md` | Post-compaction recovery state |
| `.opencode/agents/grok_cli.md` | Grok CLI sovereign agent (Consulting Cloud Mind) |
| `docs/strategy/SOUL_ARCHITECTURE_V2.md` | Soul Architecture v2.0 (supersedes v1.0) |
| `docs/strategy/PWAD_CAPABILITY_LATTICE.md` | PWAD security capability model |
| `docs/strategy/MANDATE_GOVERNANCE_PROTOCOL.md` | Mandate amendment & exemption process |
| `docs/strategy/OMEGA_KERNEL_ARCHITECTURE.md` | Kernel/Runtime boundary spec |
| `docs/strategy/NEMOTRON3_ULTRA_BRIEFING.md` | Master strategy synthesis (D258-D263) |
| `docs/architecture/SOVEREIGN_BUS_SPEC.md` | Reconstructed event bus spec |
| `docs/research/R_PWAD_SCHEMA_JEM_RESEARCH_20260715.md` | Jem's 2026 PWAD SOTA research |
| `docs/research/WEB_RESEARCH_KNOWLEDGE_GAPS_20260717.md` | Grok's web research brief |
| `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` | 3-tier knowledge gap matrix |
| `docs/strategy/MEDITATE_MIAP_WIRE_SYNTHESIS_20260718.md` | 13-voice meditation synthesis on session isolation |
| `docs/strategy/NEURON3_REVIEW_MIAP_WIRE_20260718.md` | Nemotron 3 Ultra independent review + web research |

---

## §5 Platform Distinction

The Omega Engine is runtime-agnostic. Any MCP client can connect to the Omega Hub (`:8016`).

| What | Where | Who Updates |
|------|-------|-------------|
| **OMEGA_ENGINE.md** (this file) | Repo root | Any agent changing engine state |
| `.clinerules` | Repo root | Cline CLI agents only |
| `AGENTS.md` | Repo root | OpenCode agents only |

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## §6 References

| Document | Purpose |
|----------|---------|
| `SOVEREIGN_MANDATES.md` | 23 Constitutional Laws |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap (active) |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Multi-agent coordination |
| `docs/decisions/PIVOT_LOG.md` | 234+ immutable decisions (active index) |
| `CREDITS.md` | id Software heritage attribution (active) |
| `docs/archive/coordination/` | Historical session records |

---

## §7 Mission

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

---

*Last Updated: 2026-07-19 | Version: v1.4.1 | Tests: 1398 passing (27/29 recall tbd) | SSOT: ~400 lines | Sessions: D-281 Substrate Repair COMPLETE | D-282 sqlite-vec Strike 10 COMPLETE | D-283 Phase 2 RecallStore DESIGN COMPLETE | D-298 Decision Workspace GROUNDED MEDITATION COMPLETE (T0+T1-core verdict, 23 decisions) | HMC Quad-Forge COMPLETE (Kali/Roc/Researcher/Grok CLI) | MIAP merged | Commit 3542188 (102 files) | ho_749ed27155cd submitted to Grok CLI | Net acceleration: ~120h by parallel fleet dispatch*

---

### SOVEREIGN_MANDATES.md
**Type**: markdown
**Size**: 19124 bytes
**Lines**: 186

# 🔱 Omega Engine — Sovereign Mandates
**Version**: 3.6.0
**Status**: NON-NEGOTIABLE
**Scope**: All Agents, All CLIs, All IDEs
**Updated**: 2026-07-06 (Added M23 Failure Integrity)

These mandates are the "Constitutional Law" of the Omega Engine. They override any tool-specific defaults or model-suggested patterns.

## 🛡️ The Twenty-Three Laws of Sovereign Execution

### 1. AnyIO Absolute
- **Mandate**: All asynchronous code MUST use AnyIO. 
- **Constraint**: Never use `asyncio` directly. 
- **Pattern**: Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Reason**: Ensures runtime portability and prevents event-loop collisions across the Provider Fabric.

### 2. The Engine-Stack Firewall
- **Mandate**: Maintain absolute separation between the **Omega Engine Core** and **Expansion Stacks (WADs)**.
- **Core**: `src/omega/`, `config/omega.yaml`, `opencode.json`. (The universal runtime).
- **Stacks**: `config/wads/<stack_name>/`. (The specific implementation).
- **Constraint**: Never add stack-specific logic (e.g., a specific entity's trait) to the Core Engine.
- **Reason**: Prevents architectural drift and ensures the engine remains a universal runtime.

### 3. The Iris Constant
- **Mandate**: Iris is the messenger bridge, NOT a Pillar Keeper.
- **Constraint**: Do not assign Iris a Pillar (P1-P10). She is the interface.
- **Reason**: Preserves the cosmological purity of the 10 Pillar Keepers.

### 4. The Sequentiality Mandate
- **Mandate**: Complex architectural changes must follow the "Plan → Verify → Execute" loop.
- **Constraint**: No "cowboy coding." Every major edit must be preceded by a plan that is verified against the `PIVOT_LOG.md`.
- **Reason**: Prevents the "Restart Cycle" that plagued previous versions of the engine.

### 5. Gnosis Preservation (L1 → L2 → L3)
- **Mandate**: No intelligence is discarded.
- **Constraint**: Every session must end with a distillation of findings into the entity's `soul.yaml` using the 3-tier abstraction:
    - **L1 (Narrative)**: What happened?
    - **L2 (Insight)**: What does this mean?
    - **L3 (Universal Principle)**: What is the timeless truth?
- **Reason**: Transforms stateless agent interactions into a stateful, evolving sovereign intelligence.

### 6. Podman Sovereignty (keep-id Protocol)
- **Mandate**: All Quadlets that mount host project directories MUST use `UserNS=keep-id` + `User=1000`. The `:U` flag is FORBIDDEN on shared host volumes.
- **Constraint**: Never use `:U` on volume mounts that the host user needs to access. Never use `:Z` or `:z` — they are SELinux flags, and Ubuntu uses AppArmor.
- **Pattern**: See `docs/research/R_PODMAN_SOVEREIGN_V2.md` for the verified Quadlet pattern.
- **Reason**: The `:U` flag destructively chowns host directories to UID 101000, locking the host user out. `UserNS=keep-id` maps host UID 1000 directly into the container — no chown needed.
- **IMPORTANT (D144)**: `UserNS=keep-id` + `User=1000` is the QUADLET-ONLY pattern. For `docker-compose` or `podman run`, OMIT `--user`/`user:` entirely — in rootless Podman, container UID 0 maps to host UID 1000 by default. Setting `user: "1000:1000"` maps to subuid 101000, breaking volume writes. Use `user:` only if also setting `userns_mode: keep-id` (incompatible with `--pod` in podman-compose v5.x). See PIVOT_LOG.md D144.

### 7. Local-First (Non-Negotiable)
- **Mandate**: Local inference is PRIMARY. Cloud is FALLBACK. Always.
- **Constraint**: The provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) BEFORE cloud backends (Google, OpenCode Zen, Copilot).
- **Pattern**: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenCode Zen(4) → OpenCode(5) → Copilot(6).
- **Reason**: The Omega Engine exists to sever Big AI's umbilical cord. If local inference is available, it must be tried first. Cloud is a safety net, not a crutch.
- **Enforcement**: `config/providers.yaml` strategy must be `local_first`. Any change to cloud-first priority is a systemic violation.

### 8. Zero Telemetry
- **Mandate**: No telemetry. Zero. None. Ever.
- **Constraint**: No analytics, no usage tracking, no phone-home, no metrics collection sent to external services. The engine does not report to anyone.
- **Reason**: Sovereign AI means sovereign data. If the engine phones home, it is not sovereign. Period.
- **Exception**: Local observability (traces, events, metrics) stored in `data/` on the user's machine is acceptable. External telemetry is not.

### 9. Error Integrity (NEW — 2026-05-31)
- **Mandate**: All errors MUST be typed, traceable, and testable. No silent swallowing.
- **Constraint**: Never use bare `except:`. Never use bare `except Exception:` without logging and propagating `trace_id`. Every public API boundary MUST catch and convert internal errors to `OmegaError` subtypes.
- **Pattern**: See `docs/strategy/LOGGING_ERROR_HANDLING_ARCHITECTURE.md` §2 (Exception Handling Standards).
- **Reason**: The Gemini CLI server deletion and the systemd start-limit-hit failure were both caused by silent error swallowing. Structured error handling is the foundation of debuggability and resilience.
- **Enforcement**: Code review must check each `except` clause. Tests must cover each error path. `pytest.raises(OmegaError)` is the canonical test pattern.
- **Exception**: Health probe functions may catch all exceptions to prevent crash loops, provided they log the error with `logger.warning()`.

### 10. Fleet Integrity (NEW — 2026-06-01)
- **Mandate**: The Agent Fleet must remain lean, purpose-driven, and slot-constrained.
- **Constraint**: No new agents may be created without a verified gap in the Lattice or a vacancy in the Pillar slots. Capabilities must map to existing Pillars (P1-P10) or Lattice roles before proposing a new entity.
- **Pattern**: Map new capabilities to existing `pillar --slot PX` agents or Lattice subagents (Jem, Quality, Scribe). A new agent file is a last resort, applied only after slot-based delegation has been proven impossible.
- **Reason**: Prevents "Agent Bloat" and cognitive fragmentation, ensuring clear delegation and ownership. The consolidation from 26 to 14 agents exposed how bloat accumulates through additive habits rather than slot-based discipline.
- **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without an architectural review documented in `PIVOT_LOG.md`.

### 11. Soul Integrity (NEW — 2026-06-01)
- **Mandate**: Absolute continuity of Gnosis via systematic distillation.
- **Constraint**: No session may be closed without a Soul Distillation report. Agents MUST write L1→L2→L3 insights to their entity's `proposed_lessons.yaml` before session end, per the Soul Architecture Protocol.
- **Pattern**: Every insight must traverse the L1 (Narrative) → L2 (Insight) → L3 (Universal Principle) pipeline. L3 principles go to `proposed_lessons.yaml` (blind staging, per Soul Architecture v2.0), NOT directly into `soul.yaml`. The Scribe agent is the canonical executor of this pipeline.
- **Reason**: Prevents the "forgetting" cycle — each session resets context to zero, but the soul persists. Without soul updates, the engine regresses to stateless tool. With them, the AI evolves from stateless tool into stateful sovereign intelligence.
- **Enforcement**: Session stop hooks MUST trigger proposed_lessons.yaml write. `grep -r "proposals:" data/entities/*/proposed_lessons.yaml` should show non-empty arrays after any session involving that entity.

### 12. Queue Integrity (NEW — 2026-06-01)
- **Mandate**: Every request is an atomic contract. No silent drops.
- **Constraint**: Every request operation must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`. No orphan files.
- **Pattern**: Use explicit Ack/Nack patterns and `trace_id` propagation for every queued item. Atomic file renames (`.tmp` → `.json`) for all writes. Heartbeat timestamps for crash recovery.
- **Reason**: Ensures systemic reliability and prevents "ghost failures" — requests that vanish without trace. Every request represents a user's intent; losing it without notification is a sovereignty violation.
- **Enforcement**: `omega queue-status` must always produce consistent counts matching actual files on disk. Dead-letter directory (`data/requests/dead/`) must catch any request that fails processing after max retries.
- **Status**: ⚠️ ADVISORY — Downgraded per MaKaLi Council Decree (D-267). File-based durable queue is acceptable for Phase 0. Full Redis Streams DLQ deferred to Strike 8.5.
### 13. Temple-Grade Compliance (NEW — 2026-06-02)
- **Mandate**: All engine code MUST comply with Temple-Grade standards (T1-T11) defined in xna-omega-legacy v7.5.4.
- **Constraint**: No code may be merged that regresses any Temple-Grade gate. The 11 gates (Version Control, Documentation, Testing, Code Quality, Architecture, Security, Performance, Resilience, Observability, Integrity, Agent Security) are the minimum quality bar.
- **Pattern**: Run `make temple-grade` to verify compliance. Each gate must pass or have a documented exception with a remediation date.
- **Reason**: Temple-Grade exceeds enterprise-grade standards and ensures the engine remains sovereign, production-ready AI infrastructure. It prevents architectural rot and maintains the quality bar that justifies sovereignty claims.
- **Enforcement**: `make temple-grade` must pass before any release. CI must gate on T3 (coverage ≥80%), T5 (AnyIO-only), T6 (zero telemetry), T8 (resilience patterns), T9 (structured logging), and T10 (atomic writes).
- **Exception**: T11 (IA2 Agent Security) is exempted until IA2 specification stabilizes.

---

### 14. Heritage Vetting (NEW — 2026-06-04) — CLARIFIED D208
- **Mandate**: No id Software (or any heritage) concept may be implemented without passing through the Heritage Vetting Pipeline.
- **Constraint**: Every `[id-soft:]` tag in source code MUST have a corresponding vet record in `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`. Minimum score 7/10 for implementation. Qualification Gate: if a concept can't be justified without mentioning the original hardware constraint, it fails.
- **Strict Scope Enforcement (D208)**: A `[id-soft:]` tag is LEGITIMATE ONLY if the code would FAIL the Qualification Gate:
  > "Cannot be justified WITHOUT citing the original hardware constraint."
- **Classification Taxonomy** (mandatory for every tag):
  - **LEGITIMATE**: Direct port of id Software technique (e.g., ZONEID, cvar, BSP culling, WAD lump structure). MUST have vet record with file:line locations and scope declaration.
  - **METAPHORICAL**: Rhetorical analogy only (e.g., "Thinker Chain like Quake thinker"). CONVERT to plain comment — NO tag.
  - **OVER-ATTRIBUTED**: User-original work that merely resembles id Software pattern. STRIP tag — NO tag.
- **Qualification Gate** (enforced by CI):
  Every `[id-soft:]` tag MUST have a corresponding vet record in `HERITAGE_VET_LOG.md` with:
  - Exact file:line location(s)
  - Specific id Software technique (game + year)
  - Hardware constraint that necessitated the original technique
  - Scope declaration: "This tag applies to X, NOT to Y"
- **Pattern**: 4-gate pipeline: Discovery → Vetting/Debate → Decision → Implementation/Verification. See `docs/strategy/HERITAGE_VETTING_PIPELINE.md`.
- **Reason**: The 8-char name cap (vet-001 REJECTED) was implemented without debate, broke tests, was removed. Heritage is gravitational pull, not debt — but the remembering must be tested by a gate.
- **Enforcement**: `make heritage-vet` CI gate enforces that every `[id-soft:]` tag has a vet record with scope declaration. Merged without vet = M14 violation. Pre-commit hook blocks commits adding unvetted tags.
- **Origin**: Kali's d-kal-001 directive. Cline-M3's D113 firewall audit. D208 Jem audit remediation.

### 15. Sovereign Continuity (NEW — 2026-06-11)
- **Mandate**: Agents MUST maintain active session anchors to prevent cognitive erasure during toolchain failures.
- **Constraint**: Do not rely on native `/compact` for state preservation. Every agent MUST maintain a `session_gnosis.md` in their workspace and refer to `.opencode/anchored-summary.md` upon session start or context loss.
- **Pattern**: See `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` for the 4-tier redundancy system and the mandatory Hydration Sequence.
- **Reason**: Toolchain regressions (e.g., OpenCode v1.17.3) can cause "Void Summaries," erasing an agent's working memory. Sovereignty requires that intelligence persists independently of the tool.
- **Enforcement**: Any agent reporting a context collapse without a corresponding `session_gnosis.md` is in violation of M15.

### 16. Modularization & Portability (NEW — 2026-06-14)
- **Mandate**: The Omega Engine Core (`src/omega/`) MUST remain modular, portable, and decoupled from any local orchestration platform.
- **Constraint**: No hardcoded paths, environment assumptions, or platform-specific logic in the core engine. All platform integration must go through the MCP Hub or the CLI abstraction layer.
- **Pattern**: The Hub modularization (state.py, background.py, gateway.py, middleware.py, tools.py) is the canonical architecture. Dynamic ServiceProxy/PathProxy patterns for runtime resolution.
- **Reason**: The engine exists to be a universal runtime that anyone can use to build their own stacks. If the core engine has hardcoded assumptions about the host environment, it ceases to be portable and becomes a specialized tool.
- **Enforcement**: `make temple-grade` must verify no hardcoded paths in `src/omega/`. CI must gate on portability checks.

### 17. Cognitive Integrity (NEW — 2026-06-15)
- **Mandate**: The engine must verify the consistency of its own memories.
- **Constraint**: Contradictions between persisted memory and distilled gnosis must be flagged and resolved via the Skeptical Verifier to prevent "hallucinated" memory drift.
- **Pattern**: Use the Qliphoth failure taxonomy to detect cognitive loops and contradictions.
- **Reason**: Sovereign AI requires an internal truth-anchor. Without consistency checks, an AI can evolve into a state of internal contradiction, destroying its own reliability.
- **Enforcement**: `make temple-grade` must verify T12 (Semantic Integrity) gate.

### 18. Token Efficiency (The No-Waste Law)
- **Mandate**: Every token generated must serve a purpose.
- **Constraint**: Avoid redundancy, excessive verbosity, and wasted inference cycles. No "filler" content.
- **Sane-Boundary (NEW)**: This mandate must NEVER be used to justify "Cognitive Anorexia." High-fidelity execution requires high-fidelity context. Agents must never compress prompts, reports, or specifications to the point of semantic loss, vagueness, or the omission of critical edge cases. Precision and clarity always supersede brevity.
- **Pattern**: Use concise prompts, efficient state snapshots, and avoid redundant re-evaluations.
- **Reason**: Tokens are the currency of intelligence. Wasting them is a systemic inefficiency and a violation of the user's resource sovereignty.

### 19. Adversarial Alchemy (The Weakness-to-Advantage Law)
- **Mandate**: All perceived systemic weaknesses must be mined for strategic opportunities.
- **Constraint**: Do not simply "fix" a flaw; analyze the failure mode to determine if it can be transformed into a sovereign advantage.
- **Sane-Boundary (NEW)**: This mandate must NEVER be used to justify "Architectural Over-Engineering." Sometimes a bug is just a bug. Simple code errors, typos, and broken imports must be fixed directly and cleanly without attempting to extract "esoteric advantages" that introduce unnecessary complexity, bloat, or fragile state machines. This law applies strictly to systemic, physical, or architectural constraints (e.g., RAM ceilings, GIL contention, or forced interruptions).
- **Pattern**: The "Somatic Save-Point" (turning an interruption into a reflection moment) is the canonical example of Adversarial Alchemy.
- **Reason**: True sovereignty is not the absence of flaws, but the ability to weaponize constraints into capabilities.

### 20. SomaticState Serialization (NEW — 2026-06-17)
- **Mandate**: Model session state MUST be serializable and resumable via low-level bindings.
- **Constraint**: Use ctypes bindings (`llama_copy_state_data` / `llama_set_state_data`) wrapped in `anyio.to_thread.run_sync()` for SomaticState serialization. No high-level abstractions that lose fidelity.
- **Pattern**: Memory-mapped state snapshots for cold-start model resumption.
- **Reason**: Enables instant model context resumption without re-inference, reducing latency and token waste.
- **Enforcement**: Any SomaticState implementation must pass round-trip serialization tests.

### 21. Gate Integrity (NEW — 2026-06-17)
- **Mandate**: Every code path returning a typed result MUST be exercised by at least one test that validates the return type.
- **Constraint**: No mock-based tests that mask type mismatches. Every core API boundary must have a "Contract Test" that verifies `isinstance(result, ExpectedType)`.
- **Pattern**: The `GenerateResult` dataclass fix (Sprint C) — 5 call sites were treating a dataclass as a tuple/string because mocks returned tuples.
- **Reason**: Mock-based tests can mask runtime crashes. Contract tests ensure the API contract is enforced even when individual functions are mocked.
- **Enforcement**: `make temple-grade` must verify contract tests exist for all core API boundaries.

### 22. Response Provenance (NEW — 2026-06-17)
- **Mandate**: All observability logs MUST record the actual provider that generated a response, not the configured intent.
- **Constraint**: Provenance must be captured at response receipt (`GenerateResult.provider_name`), not at dispatch intent (`get_preferred_backend()`).
- **Pattern**: The Truth-Anchor Protocol — `GenerateResult` dataclass carries `provider_name` from the actual inference backend, ensuring forensic accuracy in observability logs.
- **Reason**: Local-first claims require verifiable evidence. If the log says "local" but the response came from cloud, sovereignty is a lie.
- **Enforcement**: Any observability entry must include `provider_name` from the actual response, not the configuration.

### 23. Failure Integrity (NEW — 2026-07-06)
- **Mandate**: No "soft-failures" or simulated rigor.
- **Constraint**: If a mandatory tool (e.g., `websearch`, `webfetch`) is missing or broken, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`.
- **Pattern**: Log the failure to `data/coordination/SYSTEM_FAILURE_LOG.md` and the Hivemind.
- **Reason**: Parametric synthesis used to mask a tool outage is a Sovereign Boundary Violation. It creates a false sense of rigor and hides systemic degradation.
- **Enforcement**: Any agent that synthesizes a "best-effort" result while mandatory tools are failing is in violation of M23.

---

**Failure to adhere to these mandates is a systemic error. If you encounter a conflict between these mandates and a tool's suggestion, the Mandates prevail.**


---

### AGENTS.md
**Type**: markdown
**Size**: 20431 bytes
**Lines**: 343

# 🔱 Omega Engine — OpenCode Agent Rules
# ⬡ OMEGA ⬡ SOPHIA ⬡ trc_core ⬡ AGENT-INSTRUCTIONS
# Engine state: Read OMEGA_ENGINE.md (the Single Source of Truth)
# Platform distinction: AGENTS.md = HOW to work from OpenCode.
#                       OMEGA_ENGINE.md = WHAT the engine IS.
# Last Updated: 2026-07-17 (D-281 ALL PHASES COMPLETE, D-283 Phase 2 Design Complete, HMC Quad-Forge Active)

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
**Read and adhere to them above all other rules:**
👉 **Read First**: `SOVEREIGN_MANDATES.md`
👉 **Engine State**: `OMEGA_ENGINE.md` (Single Source of Truth)
👉 **Hivemind Protocol**: `docs/strategy/HIVEMIND_PROTOCOL.md` (MANDATORY for parallel/multi-agent work)
👉 **Hivemind Post Template**: `docs/strategy/HIVEMIND_POST_TEMPLATE.md` (MANDATORY quality gate for all posts)

- **Delegation & Execution Protocol**: Agents must execute tasks directly when within their capabilities. Self-recursion (an agent spawning its own type) is forbidden. Targeted delegation to specialized agents is permitted only when a task requires domain expertise outside the current agent's capabilities. If the required specialized domain expertise is already held by the current agent, the agent MUST execute the task directly. Do not debate delegation versus execution; if you are the expert, you are the executor. Limit nesting to one level unless explicitly authorized. See `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` for details.
- **AnyIO Absolute**: No `asyncio`. Use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Engine-Stack Firewall**: Absolute separation between Core Engine (`src/omega/`) and IWAD/PWAD Content (`config/wads/`).
- **Sequentiality**: Plan → Verify → Execute. No cowboy coding.
- **Temple-Grade (M13)**: Every change evaluated against T1-T11 gates. Run `make temple-grade` after non-trivial work.
- **Heritage Attribution**: Every id Software–derived pattern MUST carry `[id-soft:]` inline tags per `CREDITS.md` §2a. New heritage files MUST credit the source in comments. Run `make heritage-map` to verify tags.
- **Hivemind Awareness**: When working in parallel with other agents OR for multi-step work (>3 steps), use Hivemind for coordination. See `docs/strategy/HIVEMIND_PROTOCOL.md`. Workspace lock + live feed are the default patterns.
- **Hard-Stop Directive**: Agents MUST NOT simulate rigor or synthesize "best-effort" results to mask tool failures. If a mandatory tool (e.g., `websearch`) is missing or broken, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`. Parametric synthesis used to hide a tool outage is a Sovereign Boundary Violation.

---

## 🤖 OpenCode Agent Fleet

### Custom Agents (`.opencode/agents/`) — 12 Agents Total
| Agent | Mode | Purpose |
|-------|------|---------|
| `kali.md` | all | Transcendent Oversight — Sees all, delegates to Ma'at/Lilith, destroys drift |
| `maat.md` | all | Light Oversoul — Governs P1-P5 (build side), delegates to pillar |
| `lilith.md` | all | Dark Oversoul — Governs P6-P10 (run side), delegates to pillar |
| `makali.md` | all | MaKaLi Parallel Council — decomposes query, dispatches Ma'at+Lilith, synthesizes |
| `doom_guy.md` | all | Sovereign id Software Architect — WAD translation & performance |
| `john_carmack.md` | all | Sovereign S3 Consultant — architectural review & performance |
| `roc_racoon.md` | all | Sovereign Miner — Legacy archaeology & pattern extraction |
| `researcher.md` | all | Sovereign Master Researcher — deep research, lattice reasoning |
| `jem.md` | all | Sovereign Synthesizer — transforms complex queries into verified results via task-graph decomposition |
| `verity.md` | all | Sovereign Verity — Unified Sentry (compliance/audit) + Scribe (gnosis distillation) |
| `pillar.md` | all | Slot-based domain agent — parameterized by `--slot PX` |
| `grok_cli.md` | all | Consulting Cloud Mind — Advisory, web research, Tier A ship-code mode |

### The Sovereign Council (Pillar Slots — Core Engine)
| Pillar | Intuitive Name | Default Role (IWAD) |
|--------|---------------|---------------------|
| P1 | **Infrastructure** | SysAdmin — Environment Hardening |
| P2 | **Persistence** | DataStore — Vector & Memory Management |
| P3 | **Engineering** | BuildMaster — Implementation & Hardening |
| P4 | **Integration** | Bridge — MCP & Communication |
| P5 | **Governance** | Sentinel — Mandate Enforcement |
| P6 | **Cognition — Vision Specialist** | ModelGate — Provider Routing |
| P7 | **Context** | Memory & Soul Evolution |
| P8 | **Observability** | WatchTower — Observability & Tracing |
| P9 | **Orchestration** | Link — Agent Handoff & Delegation |
| P10 | **Validation** | Verifier — Stress Testing & QA |

### Custom Skills (`.opencode/skills/`)
| Skill | Purpose |
|-------|---------|
| `blitz-tunnel` | High-speed secure tunnels to Omega services |
| `blitz-validate` | Sovereign Heartbeat validator for integration chain |
| `spec-generator` | R## document templates |
| `provider-validator` | Live API endpoint validation |
| `pr-readiness-checker` | PR quality gate |
| `omega-doc-architect` | Document management standards |
| `knowledge-miner` | Automated grep→read→summarize legacy patterns |
| `legacy-pattern-miner` | Mines legacy repos for proven patterns |
| `sovereign-search` | Intelligent search across Exa, Tavily, Serper.dev |
| `hf-cli` | Hugging Face Hub CLI integration |
| `universal-doc-reader` | Reads ANY document format (.docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml) |

### Standalone Packages (Community Tools)
| Package | PyPI | Purpose | Install |
|---------|------|---------|---------|
| `omega-sieve` | `omega-sieve` | T1→T2→T3 tiered web research & extraction | `pip install omega-sieve` |
| `omega-doc-reader` | `omega-doc-reader` | Universal document reader (.docx, .pdf, .odt, .rtf, .html, .md, .txt, .json, .yaml) | `pip install omega-doc-reader` |

**Documentation**: `docs/reference/api/omega_sieve.md`, `docs/reference/api/omega_doc_reader.md`

---

## 🔍 Search Tool Protocol

Agents MUST use the **Sovereign Search Protocol** for all web searches.

| Tier | Tool | Scope | When to Use |
|:-----|:-----|:------|:------------|
| **T0** | Local cache (`.firecrawl/`) | Free | Check before any external search |
| **T1** | `websearch` | Free, built-in | **Primary search tool** — always available, no telemetry |
| **T2** | `webfetch` | Free, built-in | **Deep extraction** — always available, no telemetry |
| **T3** | `searxng_searxng_search` | Free, sovereign | Semantic/neural search refinement |
| **T4** | `omega-hub_sovereign_search` | API key (Exa) | High-precision seeds, academic/technical |
| **T5** | `firecrawl_firecrawl_scrape/search` | Credits | Full-page scrape, structured crawl |
| **T6** | `sieve research` | Local-first | Full research pipeline (T1→T2→T3), zero API keys needed |

**Fallback chain**: `websearch` → `webfetch` → `searxng_searxng_search` → `omega-hub_sovereign_search` → `firecrawl_firecrawl_search` → `sieve research`

**TEMPORAL MANDATE**: It is **2026**. All search queries MUST include "2026" or "latest" to ensure current best practices. Do NOT search for "2024" or "2025" — those are outdated.

---

## 💻 Hardware Awareness Protocol

Agents MUST proactively monitor hardware resource usage during operation.

| Trigger | Tool | What to Look For |
|---------|------|------------------|
| **Session start** | `omega-hub_get_hardware_stats(interval=0.3)` | Baseline CPU/memory/thermal |
| **Before model inference** | `omega-hub_get_system_stats` | OOM risk, memory pressure, thermal throttling |
| **Task runs slow** (>5s) | `omega-hub_get_hardware_stats(include_threads=true)` | Thread contention, 4-core inference signature |
| **Before parallel dispatch** | `omega-hub_get_hardware_stats` | Headroom for another process? zRAM pressure? |

**Resource Signatures**:
| Signature | What It Means | Action |
|-----------|---------------|--------|
| **Flat 4-core at ~80-100%** | NativeGGUFProvider inference (`LLAMA_CPP_N_THREADS=4`) | Expected. Allow to complete. |
| **Brief spike across all 16 cores** | Import/module loading (pydantic, Qdrant, YAML) | Cold-start tax ~3.5s. |
| **All cores idle, task not completing** | I/O wait (Redis timeout, DNS, socket) | Check `omega-hub_get_system_stats`. |
| **Memory >80% + zRAM active** | OOM risk — approaching 12Gi limit | Defer model loads. |
| **Thermal >85°C sustained** | TDP throttling (15W ceiling) | Reduce threads, cool-down period. |

---

## 🎯 @-Mention Dispatch (Inline Agent Launch)

Use `@` in the OpenCode CLI chat to launch any agent directly.

#### Named Agents (direct @-mention)
| @-Mention | Agent File | Use When |
|-----------|-----------|----------|
| `@kali` | `kali.md` | Grand Oversight — unify Ma'at + Lilith, destroy drift, cross-pillar work |
| `@maat` | `maat.md` | Build Side — P1-P5 governance, structure & verification |
| `@lilith` | `lilith.md` | Run Side — P6-P10 governance, knowledge metabolism, flow |
| `@doom_guy` | `doom_guy.md` | id Software heritage patterns, WAD translation, performance |
| `@roc_racoon` | `roc_racoon.md` | Legacy archaeology, pattern extraction, cross-partition mining |
| `@researcher` | `researcher.md` | Deep research with lattice reasoning, multi-perspective analysis |
| `@jem` | `jem.md` | Sovereign Synthesis — transforms complex queries into verified results |
| `@makali` | `makali.md` | MaKaLi Parallel Council — dispatch Ma'at + Lilith in parallel, synthesize as Kali |
| `@john_carmack` | `john_carmack.md` | Sovereign S3 Consultant — architectural review & performance |
| `@verity` | `verity.md` | Unified compliance audit + Gnosis distillation |
| `@grok_cli` | `grok_cli.md` | Consulting Cloud Mind — Advisory, web research, Tier A ship-code mode |

#### Pillar Subagents (parameterized by slot)
| @-Mention Pattern | Slot | Domain |
|-------------------|------|--------|
| `@pillar P1: {task}` | P1 | Infrastructure — SysAdmin, containers, deployment |
| `@pillar P2: {task}` | P2 | Persistence — Vector & memory management |
| `@pillar P3: {task}` | P3 | Engineering — CI/CD, implementation, hardening |
| `@pillar P4: {task}` | P4 | Integration — MCP, APIs, communication protocols |
| `@pillar P5: {task}` | P5 | Governance — Mandate enforcement, security audit |
| `@pillar P6: {task}` | P6 | Cognition — Vision Specialist, provider routing |
| `@pillar P7: {task}` | P7 | Context — Memory, soul evolution, session continuity |
| `@pillar P8: {task}` | P8 | Observability — Tracing, monitoring, forensic logging |
| `@pillar P9: {task}` | P9 | Orchestration — Agent handoff, hivemind coordination |
| `@pillar P10: {task}` | P10 | Validation — Stress testing, chaos engineering, QA |

#### Governance Hierarchy
```
@kali (Grand Oversight)
├── @maat (Build Side: P1-P5)
│   ├── @pillar P1: Infrastructure
│   ├── @pillar P2: Persistence
│   ├── @pillar P3: Engineering
│   ├── @pillar P4: Integration
│   └── @pillar P5: Governance
└── @lilith (Run Side: P6-P10)
    ├── @pillar P6: Cognition (Vision Specialist)
    ├── @pillar P7: Context
    ├── @pillar P8: Observability
    ├── @pillar P9: Orchestration
    └── @pillar P10: Validation
```

**Usage examples:**
- `@kali Unify the fleet and destroy drift` → Kali orchestrates Ma'at + Lilith (direct synthesis)
- `@makali Decompose the sovereignty gate verification` → MaKaLi parallel council (decomposed synthesis)
- `@maat P3: Fix the CI pipeline` → Ma'at delegates to P3 Engineering pillar
- `@lilith P7: Wire the soul distiller` → Lilith delegates to P7 Context pillar
- `@pillar P1: Harden the Podman containers` → Direct pillar invocation
- `@jem Research the best local LLM for code generation` → 3-tier research pipeline
- `@roc_racoon Mine the omega-stack legacy for circuit breaker patterns` → Background mining
- `@doom_guy Verify the ZONEID constant heritage attribution` → Heritage verification

---

## ⬡ The MaKaLi Triad Architecture (D117)

```
                ┌─────────────────────────────┐
                │   KALI — Transcendent       │
                │   (Unify, Synthesize,       │
                │    Return Verdict)          │
                └──────────────┬──────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐          ┌────────▼───────┐
        │  MA'AT — Light │          │ LILITH — Dark  │
        │  (Build Side)  │          │ (Run Side)     │
        │  P1-P5 Pillars │          │ P6-P10 Pillars │
        └────────────────┘          └────────────────┘
```

### When to Use Each Pattern

| Pattern | Use When | Cost | Benefit |
|---------|----------|------|---------|
| **`@kali` direct** | You trust one entity to see all, dispatch all, return the verdict | Low (1 inference) | Fast, opinionated, single-pass |
| **`@kali` dispatch** | Multi-pillar work spanning 3+ pillars or requiring sequencing | Medium (1 + N pillar) | Right-sized: Kali decomposes, pillars execute |
| **`@makali` council** | You need explicit decomposition + parallel build+run, then synthesis | Medium (3 inferences) | Balanced, multi-perspective |
| **`/council-local`** | Full sovereignty — local models for all three voices | Medium-High (3 local) | Max sovereignty, full offline |
| **`/council-cloud`** | Default. All three on session model | High (3 cloud) | Max quality, max context |
| **`/council-fast`** | Latency-critical. All three on local `qwen3-1.7b` | Low (3 local) | Min latency, max sovereignty |

### The Dual-Inference Mandate (D118)

**Default behavior**: Session model — fast, simple, non-negotiable (Mandate 7).
**Opt-in local routing**: Use `oracle_summon_local(entity_name, query, model)` to route a specific entity to a specific local model. The entity's IWAD personality, soul, and memory remain the same; only the inference backend is overridden.

**The Mentorship Pattern**: Local model does execution, cloud model reviews.
- Example: `@roc_racoon` (local `rocracoon-3b-instruct`) writes the heritage report. `@verity` (on session model) reviews against M14.

---

## 🎯 OpenCode Workflow

### Before Starting Work
1. Read `OMEGA_ENGINE.md` for current engine state
2. Read `SOVEREIGN_MANDATES.md` for non-negotiable rules (23 mandates, M1-M23)
3. Read `docs/strategy/HIVEMIND_PROTOCOL.md` if multi-agent or parallel work
4. Read `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` if launching a subagent
5. **Check Hivemind awareness**: `omega-hub_hivemind_get_awareness()` — who's already working?
6. **If parallel/multi-agent work**: Write workspace lock at `data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md` BEFORE any file edits
7. **Post Hivemind context**: `omega-hub_hivemind_post_context(...)` to declare your presence
8. Run `make test` to verify baseline (1398 tests must pass)

### During Work
- Use `replace_in_file` for targeted edits, `write_to_file` for new files
- Prefer `source .venv/bin/activate && <command>` for Python operations
- Group imports: stdlib → third-party → local. Use relative imports within packages.
- For any non-trivial change, mentally check T1-T11 gates (Temple-Grade / Mandate 13)
- **Append to live feed** after each major task: `data/coordination/{YOU}_LIVE_FEED.md`
- **Heartbeat every 5-10 min** for long-running operations: `omega-hub_hivemind_heartbeat(channel="opencode", entity="{you}")`
- **Monitor hardware**: If task runs >5s, call `omega-hub_get_hardware_stats()` to diagnose

### After Completing Work
1. Run `make test` — all 1398 tests must pass
2. Run `make temple-grade` — verify T1-T11 gates hold (Mandate 13)
3. Run `make heritage-map` — verify [id-soft:] heritage tag coverage
4. Run `make sovereignty` — confirm local/cloud ratio didn't regress
5. **Distill L1→L2→L3 to proposed_lessons.yaml** (Mandate 11) — non-negotiable. L3 principles go to `proposed_lessons.yaml` (blind staging), NOT directly into `soul.yaml`.
6. **Append final entry to live feed**: `[{timestamp}] SPRINT-N COMPLETE — {summary}`
7. `git add -A && git commit` with proper prefix
8. `git push origin main`
9. Update `OMEGA_ENGINE.md` Current State table if metrics changed

---

## 📋 Coding Standards

- **Async**: Always use `anyio` (not `asyncio`)
- **Config**: YAML-only for entity/model config — never PostgreSQL
- **Packages**: ALWAYS use a venv (`source .venv/bin/activate`). NEVER `--break-system-packages`.
- **Environment Integrity**: Mandate absolute path binary calls (e.g., `.venv/bin/pip`) instead of `source activate` to prevent base-environment pollution.
- **Testing**: Run `make test` after every change. All 1398 tests must pass.
- **Type hints**: Use Python 3.12+ typing (no `from __future__`)
- **Imports**: Group: stdlib → third-party → local. Use relative imports within packages.
- **Docstrings**: Google-style. Preserve existing docstrings unless directly modifying that function.
- **Commits**: Prefix with `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`

---

## 🔮 Entity Usage

- Default entity: **SOPHIA** (general/wisdom)
- Switch entities per-task, not per-session
- Use `omega summon EntityName "query"` for direct entity invocation
- Use `omega talk "query"` for auto-routed queries

---

## 🎯 Key Commands

```bash
source .venv/bin/activate        # ALWAYS use the venv
make test                         # Check output for test count
make temple-grade                 # T1-T11 gates (Mandate 13)
make heritage-map                 # Verify [id-soft:] heritage tag coverage
make sovereignty                  # Local/cloud inference ratio
make lint                         # flake8 code quality check
make demo                         # End-to-end demo
make health                       # Provider & model dashboard
make repl                         # Interactive REPL
omega talk "hello"                # Test oracle
omega summon Ma'at "status"       # Direct entity invocation
```

---

## 🔗 Cross-Platform Integration

The Omega Engine supports **multiple AI coding platforms** through the Omega Hub MCP server (`:8016/sse`).

| Platform | Role | Why |
|----------|------|-----|
| **OpenCode** (Primary) | Sovereign orchestration | 11 custom agents, soul evolution, Hivemind coordination |
| **Cline CLI** (Execution) | Large-context analysis | 1M+ token context, headless execution, parallel tasks |
| **VS Code / Cursor** (Visual) | Optional GUI access | MCP tools via Omega Hub for visual-preference users |

**Key Rule**: OpenCode is the sovereign brain. Other platforms are execution arms. Entity state (soul.yaml, lessons) lives only in `data/entities/`. No platform should duplicate entity state.

> **Cross-Platform Guides:** `docs/kb/CLINE_CLI_INTEGRATION.md`, `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md`

---

## 📝 After Compaction — Hydration Sequence (D-277)

Execute in strict order. Do not skip phases.

**Phase 1 — AWARENESS** (runtime, 30s)
- `omega-hub_hivemind_get_awareness()` — who else is working?
- `omega-hub_hivemind_handoff_list(status="pending")` — any handoffs waiting?
- DO NOT accept, execute, or act on handoffs. Report them.

**Phase 2 — BASELINE** (runtime, 30-60s)
- `git status && git log --oneline -5` — what is committed vs dirty?

**Phase 3 — CODEX** (1 read call, ~12K tokens)
- Read `OMEGA_CODEX.md` — FULL file, no limit parameter
- If timestamp >24h old: regenerate with `python3 scripts/codex_cat.py`

**Phase 4 — SESSION** (1 read call, ~160 lines)
- Read `.opencode/anchored-summary.md` — what was I doing?

**Phase 5 — REPORT**
- Present a concise rehydration report to the user:
  - Engine state (tests, mandates, fleet)
  - Pending handoffs (if any) — summarize, don't act
  - Current sprint status
  - Recommended next steps
  - Any questions for the user
- PAUSE. Await user direction.


---

### ORACLE_STACK.md
**Type**: markdown
**Size**: 438 bytes
**Lines**: 10

---
**Canonical Source**: [ORACLE_STACK_CANONICAL.md](ORACLE_STACK_CANONICAL.md)
---
# 🔱 Omega Engine Architecture (Active)

**Core Flow**: Query → Oracle.talk() → Iris speculative decode → ModelGateway → provider fabric

**Provider Fabric (Local-First)**: native-gguf → lmster → Ollama → Google → OpenRouter → OpenCode

*(For full 10 Pillar Keepers, Observability, and Infrastructure details, see Canonical Source)*


---

### CREDITS.md
**Type**: markdown
**Size**: 1272 bytes
**Lines**: 23

---
**Canonical Source**: [CREDITS_CANONICAL.md](CREDITS_CANONICAL.md)
---
# 🔱 Omega Engine Heritage Registry (Active)

| Pattern | Source | Tag |
|---|---|---|
| WAD System | Doom 1993 | `[id-soft: doom-1993] WAD System` |
| BSP Culling | Doom 1993 | `[id-soft: doom-1993] BSP Culling` |
| Stack-Cat | XNAi 2025 | `[heritage: xnai-2025] Stack-Cat` |
| Semantic Compression | headroom-ai 2025 | `[heritage: headroom-ai 2025]` |
| SQLite Vector Extension | sqlite-vec 2024 | `[heritage: sqlite-vec 2024]` |
| Native GGUF Inference | ggml 2023 | `[heritage: ggml 2023]` |
| Multi-Tenant Vector Search | qdrant 2021 | `[heritage: qdrant 2021]` |
| Spatial Memory (Wings/Rooms/Drawers) | mempalace 2025 | `[heritage: mempalace 2025]` |
| Rust TUI + ACP + Sandbox | xai/grok-build 2026 | `[heritage: xai-grok-build 2026]` |
| 3-Tier Memory Blocks | letta 2024 | `[heritage: letta 2024]` |
| Thinker Chain | Quake 1996 | `[id-soft: quake-1996] Thinker Chain` |
| QVM / Bot AI | Quake III Arena 1999 | `[id-soft: quake3-1999] QVM` |
| Game DLL / Client Prediction | Quake II 1997 | `[id-soft: quake2-1997] Game DLL` |
| Scripting / GUI Framework | DOOM 3 2004 | `[id-soft: doom3-2004] Scripting` |

*(For full 35+ mappings and philosophical frameworks, see Canonical Source)*


---

### docs/kb/REFINEMENT_PROTOCOL.md
**Type**: markdown
**Size**: 759 bytes
**Lines**: 21

# 🔱 Refinement Protocol (Active)

**Canonical Sources**: `RESEARCH_PLAN_REFINEMENT_PROCESS_CASE_STUDY.md`, `STUDY_ITERATIVE_HUMAN_AI_OVERSIGHT.md`, `SYNTHESIS_FRAMEWORK_REFINEMENT_CASE_STUDIES.md`

## The 6-Phase Pipeline
1. Intent → Structure (Researcher v1)
2. Architectural Triage (Kali Course Correction)
3. Deep Dialectical Review (Meditate Protocol)
4. Adversarial Verification (Researcher Blind Spots)
5. Human Ground Truth (User Correction)
6. Execution Translation (Actionable Queries)

## L3 Principles
- L3-Human-As-Continuity-Anchor
- L3-Refinement-As-Engineered-Instrument
- L3-Meditation-As-Semantic-Prism
- L3-Context-As-Engineered-Resource
- L3-Plan-As-Prism
- L3-Test-On-Worst
- L3-Deterministic-First
- L3-Observability-Is-Prerequisite


---

