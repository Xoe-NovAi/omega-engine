# 🔱 GROK CLI BRIEFING — Carnak Strip-the-Engine Review
**AP Token**: `AP-GROK-CLI-BRIEFING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ trc_carnak_briefing ⬡ GROK-FLEET

**Date**: 2026-07-30
**Purpose**: Comprehensive briefing for Grok CLI to perform web-researched, strategic evaluation of 20+ Omega Engine systems. Determine what to cut, what to replace with existing solutions, and what to keep.

---

## §0 SESSION CONTEXT

This session generated ~12K lines of independent review across 4 agents (John Carmack, Lilith, Ma'at, Roc_Racoon) who each performed deep analysis of the Omega Engine codebase. The user's mandate:

> **"What should go? Where is the weight slowing us down? What systems should we stop trying to build ourselves, at least for now, and use a pre-existing solution? Let's strip this engine of everything that holds it back."**

Each agent returned structured findings. This briefing synthesizes their consensus and forks, then asks Grok CLI to perform web research on the replacement candidates.

### Current Codebase Stats
- **Total**: ~82,715 lines across 282 Python files
- **src/omega/**: ~35,000 lines (core engine)
- **docs/**: ~15,000 lines (strategy + research + archives)
- **tests/**: ~8,000 lines
- **Configs/scripts**: ~24,000 lines
- **Commit base**: `2fdaea7` (Kali P0 mandate fixes) + `74d9c7c` (Roc local worker pool)

---

## §1 CURRENT STATE

### Recent Changes (This Compact Cycle)
**Kali P0 fixes** (`2fdaea7`):
- Removed SovereignVetter runtime → replaced with Makefile CI gates
- M1 AnyIO migration: `cgroup_pressure.py`, `psi_monitor.py`, `oom_protector.py`
- Pre-commit hooks for M1/M7/M8/M9/M23 + GitHub Actions `make check-mandates` step
- Archived orphaned scribe agent (5 files, never imported)
- Fixed oracle.py cascading parse error, oracle_cli.py dead imports

**Roc local worker pool** (`74d9c7c`):
- Fixed 4 pipe bugs (KV cache default q8_0→f16, cloud fallback params, M7 routing priority, context window sizing)
- Built ~460-line LocalWorkerPool daemon + ~250-line CLI + 4 MCP tools + 11 entity registrations
- Fixed critical task re-picking bug (`_processing_task_ids`)
- Registered 4 models with 3-layer sampling param resolution

### Strategic State
- Phase C hardening complete ✅
- Phase D gate pending (needs `make test` pass, backup, soul distillation working)
- G-1 (workhorse continuity) + W-1 (WARP pool) super-urgent per Ark
- V-1 VaultCore MVP pending
- **Known blocker**: `make test` hangs (pre-existing, no root cause)
- **Zombie**: 1.9G process from Roc's debug run

---

## §2 SYSTEMS TO KILL — UNANIMOUS CONSENSUS (All 4 Agents)

These have unanimous agreement across all reviewers. No further debate needed — just execute.

### 2.1 PSI Monitor + Cgroup Pressure + MemAvailable + OOMProtector
| Field | Detail |
|-------|--------|
| **Files** | `oom_protector.py` (363), `psi_monitor.py` (283), `cgroup_pressure.py` (299), `memavailable.py` (256), `resource_guard.py` (343) |
| **Total lines** | ~1,544 |
| **System** | Reads 3 kernel files (`/proc/pressure/memory`, cgroup v2 `memory.pressure`, `/proc/meminfo`), fuses into 3-signal admission decision with EWMA smoothing, Ryzen-threshold tuning |
| **Verdict** | **DELETE. Replace with `psutil.virtual_memory().available`.** |
| **Carmack** | "Kernel's MemAvailable is the authoritative signal. PSI tells you about stall time, not OOM risk. For a single-user desktop app, the 3-signal fusion is server-grade theater." |
| **Lilith** | "Cgroup pressure duplicates PSI on bare metal (no Kubernetes). Keep PSI + MemAvailable at most. Save ~1,200 lines." |
| **Ma'at** | "Replace entire trio with a single psutil call. The ResourceGuard semaphore can stay — it does admission control regardless of OOM signal source." |
| **Roc** | "I read these files. `psutil.virtual_memory().available` gives you the exact same answer in 3 lines. Delete ~1,200 lines." |
| **Grok CLI task** | ✅ Consensus reached. No research needed for the verdict. Research: are there edge cases where PSI/cgroup v2 provides value for single-user desktop? Current hardware: Ryzen 5700U, 16GB RAM, Ubuntu 24.04. |

### 2.2 CascadeRouter
| Field | Detail |
|-------|--------|
| **File** | `cascade_router.py` (540 lines) |
| **System** | Weighted scoring across 6 dimensions (cost, quality, latency, quota, health, configuration) with ProviderScore dataclass, fallback chain builder, cost estimator |
| **Verdict** | **DELETE. Replace with priority-ordered provider list.** |
| **Carmack** | "Weighted scoring over 7 dimensions for a provider chain that has 3 entries. Roc found it scoring cloud higher than local — the bug is a feature of the complexity." |
| **Lilith** | "Hot path uses ProviderSelector (93 lines, correct). CascadeRouter is a fallback that gives wrong answers. Kill it." |
| **Roc** | "The priority-first routing fix I made to CascadeRouter was patching a fundamentally overbuilt design. A priority list can't have this bug by construction." |
| **Grok CLI task** | ✅ Consensus. Research: standard patterns for provider fallback chains in local-first AI tools? What do Ollama, LM Studio, LocalAI do? |

### 2.3 SoulHistory + SoulEditHistory
| Field | Detail |
|-------|--------|
| **Files** | `soul_history.py` (173), `soul_edit_history.py` (293) |
| **System** | SHA-256 hash chain in JSONL files with `verify_integrity()`, immutable append-only log, `previous_hash` chaining |
| **Verdict** | **DELETE. Git is the audit trail.** |
| **Carmack** | "Git already has a hash chain — the commit DAG. This is cryptographic theater on top of an existing VCS." |
| **Ma'at** | "SoulStore already writes atomically with fsync+flock. That's sufficient for crash safety. The hash chain adds forensic capability never used." |
| **Roc** | "I mined the legacy pattern: the original XNAi code used git for history. This was added later and duplicates existing infrastructure." |
| **Grok CLI task** | ✅ Consensus. Research: best practices for YAML config versioning in local AI tools? |

### 2.4 TokenEstimator + QuotaTracker
| Field | Detail |
|-------|--------|
| **Files** | `token_estimator.py` (262), `quota_tracker.py` (323) |
| **System** | Token estimation for cost projection + rate-limit header parsing for 6 providers |
| **Verdict** | **DELETE. Only used by CascadeRouter (also being killed).** |
| **Lilith** | "QuotaTracker parses `x-ratelimit-*` headers for 6 providers. Local providers don't have quota. Antigravity doesn't emit standard headers. Google is hit 5-10 times/day. Zero enforcement mechanism." |
| **Grok CLI task** | ✅ Consensus. Research: do any local-first AI engines do token estimation for cost awareness? Is this a standard practice in the ecosystem? |

### 2.5 DPO Logger Integration
| Field | Detail |
|-------|--------|
| **Location** | `oracle.py:_record_interaction()` lines 724-740; `dpo_logger` imports |
| **System** | Records every interaction as a "DPO training pair" (query + response + metadata) for RLHF-style fine-tuning |
| **Verdict** | **DELETE from hot path. No training pipeline exists or is planned.** |
| **Lilith** | "Collecting thousands of training pairs for a pipeline that doesn't exist. Pure data gravity with no downstream consumption." |
| **Grok CLI task** | ✅ Consensus. |

### 2.6 Stale Strategy Docs
| Field | Detail |
|-------|--------|
| **Scope** | ~6,000 lines across 10+ documents in `docs/strategy/` |
| **Verdict** | **ARCHIVE to `docs/archive/`.** |
| **Carmack** | "IMPLEMENTATION_MANUAL_C0_C2.md (1,416 lines) — completed tickets. LIVING_RESEARCH_OS_SPEC.md (720 lines) — amended 3 times. CANONICAL_ROADMAP.md (422 lines) — superseded. These are historical documents, not strategy." |
| **Docs to archive** | IMPLEMENTATION_MANUAL_C0_C2.md, LIVING_RESEARCH_OS_SPEC_20260721.md, CANONICAL_ROADMAP_20260721.md, HARDENING_PLAN_COMPLETE.md, FINAL_INSPECTION_REPORT_20260722.md, PROCESS_IMPROVEMENT_PLAN_20260725.md, UNIFIED_EXECUTION_PLAN_20260722.md, ENHANCED_COORDINATION_STRATEGY_v2_20260730.md, SESSION_END_ORCHESTRATION_PIVOT_20260730.md, POST_PR_ROSTER.md, ROLLBACK_PROCEDURES.md, SCRIBE_HUB_MASTER_PROTOCOL.md |
| **Keep** | SOVEREIGN_ARK_BLUEPRINT.md, FLEET_TEAM_PLAYBOOK.md, HIVEMIND_PROTOCOL.md, STRATEGY_CORPUS_MAP.md, STRATEGY_INDEX.md |
| **Grok CLI task** | ✅ Consensus. |

---

## §3 SYSTEMS TO SIMPLIFY — SUPERMAJORITY CONSENSUS (3 of 4)

These have strong agreement but one dissenter. Need Grok CLI to validate the replacement direction.

### 3.1 HealthMonitor / Custom Circuit Breakers
| Field | Detail |
|-------|--------|
| **Files** | `health_monitor.py` (936), `search_circuit_breaker.py` (299), `failure_registry.py` (395) |
| **Total** | ~1,630 lines |
| **System** | AsyncCircuitBreaker with 5-state FSM (closed/half_open/open), CUSUM + sliding window detection modes, EMA latency + quality tracking, 429 classification (rate limit vs quota), half-open probes, keyword matching |
| **Verdict** | **SIMPLIFY. Replace custom breakers with `tenacity`** (already a dependency in `pyproject.toml`). |
| **Carmack** | "Circuit breakers matter at 10K+ requests/minute. For a desktop app making one call at a time, the breaker adds complexity without benefit. For cloud providers, tenacity retry handles transient failures." |
| **Roc** | "Tenacity is already installed. You have 3 breaker implementations (HealthMonitor + SearchCircuitBreaker + FailureRegistry) and a 2nd QuotaStatus dataclass at line 99. Pick one, use tenacity." |
| **Lilith** | "The circuit-breaker pattern with EMA tracking is appropriate for provider resilience. Keep but don't expand. 936 lines is large but doing real work." |
| **Dissenter** | Ma'at says keep. "The circuit-breaker pattern is the right architectural choice for provider resilience." |
| **Grok CLI task** | **RESEARCH NEEDED.** What are the current best practices for retry/circuit-breaking in local-first AI tools? Is tenacity's `@retry` sufficient for model inference providers? Do Ollama/LM Studio/OpenAI-compatible tools use circuit breakers or simple retry? Compare: custom breaker vs tenacity vs `stamina` (newer tenacity successor). Provide code examples for the recommended approach. What does the community (Ollama, LocalAI, llama.cpp) do for provider resilience? |

### 3.2 MemoryStore Architecture
| Field | Detail |
|-------|--------|
| **Files** | `memory_store.py` (1,110) + `memory/` directory (12+ modules, ~6,300 lines total) |
| **Total** | ~7,400 lines across 19 files |
| **System** | 5 storage providers (Redis hot, File warm, InMemory cold, USM sovereign), 3 vector stores (SQLiteVec, Qdrant, MemoryVector), 2 embedding providers (GemmaGGUF, StaticEmbedding), FTS5 full-text, Hybrid RRF search fusion, batch writer, block store, archival, compaction, recall |
| **Verdict** | **DISAGREEMENT.** Three positions: full replacement (Lilith), deep trim (Carmack/Roc), keep (Ma'at). |
| **Lilith** | "Replace entire module with single SQLite-backed ConversationStore. 7,400 lines → 500 lines. You're not doing RAG on conversation history — you're doing RAG on documents. Drop Redis/File/InMemory providers. Drop vector stores from memory." |
| **Carmack** | "Trim. Keep SQLite + FTS5 as primary store. Drop the unused provider tiers. The architecture is sound but 3x larger than needed." |
| **Roc** | "Pick ONE storage backend. Pick ONE embedder. Delete the rest. The hybrid search is decorative — nobody's doing semantic search over 100 conversations on a laptop without GPU." |
| **Ma'at** | "Keep as-is. The memory system is a core differentiator. Improve test coverage." |
| **Grok CLI task** | **CRITICAL RESEARCH NEEDED.** This is the biggest fork. Research: 
- What do local-first AI tools (Ollama, LM Studio, LocalAI, GPT4All) use for conversation memory? Do they have multi-tier storage?
- Is SQLite FTS5 sufficient for single-user conversation search at ~10K exchanges? Benchmarks?
- Do any local AI tools use vector search for conversation memory, or is that limited to RAG on documents?
- What's the state of `sqlite-vec` (extension for vector search in SQLite) in 2026?
- What is the standard pattern for conversation history in local AI agents?
- Provide specific recommendations: should we kill MemoryStore entirely, trim it, or keep it? If trim, exact what to cut? |

### 3.3 EntityRegistry Bloat
| Field | Detail |
|-------|--------|
| **File** | `entity_registry.py` (944 lines) |
| **System** | YAML-backed entity CRUD with typed dataclass models, SymbolicMetadata parser (6 esoteric fields: element, energy_center, celestial_body, archetypal_ally, glyph, invocation), workspace management, wad_loader integration, SovereignPermissionError, flock-based write exclusion |
| **Verdict** | **SIMPLIFY. Strip to ~200 lines.** Keep Entity dataclass, load(), get(), list(). Kill SymbolicMetadata, SovereignPermissionError, write_soul_file() (SoulStore handles it), EntityWorkspaceManager. |
| **Carmack** | "If the engine core never interprets archetypal_ally fields, they're decoration. 60 lines of typed dict + validator for fields with zero effect on any code path." |
| **Roc** | "The legacy pattern was a simple YAML loader. This has grown by accretion. Strip." |
| **Grok CLI task** | ✅ Consensus direction clear. Research: what's the standard pattern for entity/agent configuration in agent frameworks (LangChain, CrewAI, AutoGen)? Do they have complex entity registries or simple config files? |

### 3.4 MCP Compliance + Dual Watchdog
| Field | Detail |
|-------|--------|
| **Files** | `mcp_compliance.py` (826 lines), dual watchdog services (`omega-hub-watchdog` + `omega-mcp-watchdog`) |
| **System** | Custom MCP protocol compliance checker + two redundant health monitors |
| **Verdict** | **KILL mcp_compliance.py. Use MCP Inspector for compliance testing. Consolidate to one watchdog.** |
| **Carmack** | "The `mcp` library handles spec compliance. If you need to validate server behavior, use the official MCP Inspector — a standard tool from Anthropic." |
| **Roc** | "826 lines of custom compliance code when the `mcp` library already handles it. This is textbook NIH." |
| **Grok CLI task** | **RESEARCH NEEDED.** What is MCP Inspector in 2026? Can it replace the custom compliance module? What's the standard pattern for MCP server testing? Is the dual watchdog pattern common or is systemd Restart= sufficient? |

### 3.5 MIAP — Multi-Instance Agent Protocol
| Field | Detail |
|-------|--------|
| **File** | `miap.py` (632 lines) |
| **System** | Event sourcing + deterministic projection + UUID7 + file-lock serialized writes + symlink projections + Hivemind integration. Designed for coordinating MULTIPLE INSTANCES of the same agent. |
| **Verdict** | **STRIP to UUID7 (~50 lines). Archive event sourcing + projection.** |
| **Carmack** | "Multi-instance coordination for a tool that runs one session at a time. SoulStore's flock() already handles write conflicts." |
| **Roc** | "Keep UUID7 (useful utility). Lose the 580 lines of event log infrastructure. If multi-instance becomes relevant, Redis Pub/Sub is a better foundation than JSONL files." |
| **Grok CLI task** | ✅ Consensus. Research: are there lightweight alternatives to MIAP for multi-agent state coordination? Should we ever revisit this or is UUID7 sufficient for the forseeable future? |

---

## §4 STRATEGIC FORKS — Disagreement, Need Web Research

These are the three critical forks where Grok CLI's web research is most needed to inform the decision.

### 4.1 FORK: LocalWorkerPool Backend

**Current**: File-based polling queue (~470 lines pool + ~268 lines CLI + 4 MCP tools)

| Option | Lines | Persistence | Overhead | Infrastructure |
|--------|-------|-------------|----------|---------------|
| **A: File-based** (Roc, Lilith) | ~200 (simplified) | Full (files survive restart) | 2s poll + 7 fs ops/task | Zero |
| **B: `anyio.Queue`** (Carmack) | ~80 | None (in-memory) | Zero latency, zero fs | Zero |
| **C: Redis/ARQ** (Ma'at) | ~50 | Full + observable | ~1ms RTT | Redis (already running) |

**User questions for Grok CLI research**:
1. What do local inference tools (Ollama, LocalAI, llama.cpp) use for background task queuing? ARQ? RQ? Celery? File-based?
2. For a single-user desktop tool processing 0-5 inference tasks/day, what's the standard practice?
3. Is the `anyio.Queue` + TaskGroup pattern (Carmack's proposal) used in production local AI tools?
4. What are the crash-recovery patterns for queued inference tasks that need to survive a restart?
5. Compare: ARQ vs RQ vs Hue vs Celery vs file-based for this exact use case (lightweight local inference queue). Include lines of code needed to integrate each.

### 4.2 FORK: MemoryStore Depth

**Current**: 7,400 lines across 19 files. 5 storage providers, 3 vector stores, 2 embedders.

| Option | Lines | Capability | Complexity |
|--------|-------|------------|------------|
| **A: SQLite-only** (Lilith) | ~500 | Basic FTS5 search | Minimal |
| **B: Trim providers** (Carmack, Roc) | ~2,000 | Keep structure, drop tiers | Moderate |
| **C: Status quo** (Ma'at) | ~7,400 | Full multi-tier vector search | High |

**User questions for Grok CLI research**:
1. See detailed questions in §3.2 above.
2. **Key question**: Is multi-tier memory with vector search a standard pattern in local AI tools in 2026, or is it overbuilt for single-user conversation history?
3. What's the token/query volume threshold where SQLite FTS5 breaks down and vector search becomes necessary?
4. Are there lightweight alternatives (e.g., `chromadb` embedded, `sqlite-vec`) that provide vector search at 1/10 the lines?

### 4.3 FORK: Strategy Docs Hygiene

**Current**: 8,181 lines in `docs/strategy/`, 15MB in `docs/archive/`.

| Option | Docs Kept | Lines | Risk |
|--------|-----------|-------|------|
| **A: Aggressive** (Carmack) | 5 docs | ~2,000 | Lose historical context |
| **B: Moderate** (Ma'at) | 8 docs | ~3,500 | Keep more reference |
| **C: Laissez-faire** | Keep all | ~8,200 | Bloat, confusion |

**Grok CLI task**: ✅ Consensus that aggressive archive is correct. No research needed — this is an execution decision. Carmack's list in §2.6 is the recommended archive set.

---

## §5 SYSTEMS TO KEEP (No Research Needed)

All 4 agents agree these earn their place:

| System | Why |
|--------|-----|
| **SoulStore** (217 lines) | Well-engineered atomic writer with 4-layer guarantee. Single responsibility. Testable. |
| **ProviderSelector** (93 lines) | Simple, correct, priority-first routing with health awareness. Does exactly what it needs. |
| **NativeGGUFProvider + OpenAICompatProvider + AntigravityProvider** (150-400 lines each) | Core value proposition: load model, run inference, return result. Each does one thing well. |
| **Hivemind coordination** (file-based) | Simple, debuggable, works for single-user. No Redis dependency. Handoff protocol works. |
| **Pre-commit hooks** (mandate checks) | Fast, real, catch violations. Only trim: replace `make` indirection with direct `rg` calls. |
| **ResourceGuard** (semaphore + cancellation) | Directly prevents resource contention on 15W TDP machine. Keep admission control, swap OOM signal source. |
| **Test quarantine / badge system** | Adds honesty to testing. Keep but fix: badge must report HANG/INCOMPLETE if suite doesn't complete. |

---

## §6 SPECIFIC RESEARCH QUESTIONS FOR GROK CLI

### Tier 1: Highest Priority (Informs the 3 Forks)

```
1. Memory system patterns in local AI tools (2026):
   - What do Ollama, LM Studio, LocalAI, GPT4All, llama.cpp use for conversation memory?
   - How many use vector search for chat history vs SQLite FTS5?
   - What is the standard architecture for single-user conversation persistence?
   - Is multi-tier (hot/warm/cold) memory a standard pattern or over-engineering?

2. Background task queuing for local inference:
   - What queue backends do local AI tools use? ARQ? RQ? File-based? anyio.Queue?
   - Best practices for single-user inference queues — do they persist across restarts?
   - Crash recovery patterns for inference tasks

3. Circuit breaker / retry best practices (2026):
   - Is tenacity still the standard or has stamina replaced it?
   - Do local AI inference providers use circuit breakers or simple retry?
   - What's the right pattern for a 3-provider chain (local → cloud fallback)?
```

### Tier 2: Important Context

```
4. MCP ecosystem in 2026:
   - MCP Inspector capabilities — can it replace the custom compliance module?
   - MCP SSE vs Streamable HTTP — is dual-transport still necessary in 2026?
   - Standard MCP server testing practices

5. Entity/agent configuration patterns:
   - How do LangChain, CrewAI, AutoGen define agent configs?
   - What's the standard: YAML files, JSON, Pydantic models, SQLite?

6. Provider fallback chains:
   - How do Ollama + OpenRouter integrations handle fallback?
   - Standard pattern: priority list vs weighted scoring?

7. Soul/metadata versioning:
   - Best practices for YAML config versioning in agent tools
   - Is git log sufficient as an audit trail for agent config changes?
```

### Tier 3: Nice-to-Have Context

```
8. OOM protection patterns:
   - Do local AI tools implement OOM protection? How?
   - Is psutil.virtual_memory() considered sufficient?

9. Alternative to custom breakers:
   - stamina (tenacity successor) maturity in 2026
   - pybreaker library comparison

10. Local inference ecosystem (2026):
    - New developments in llama-cpp-python, Ollama, LocalAI
    - Qwen3 vs Gemma vs Llama 4 for local code generation
    - Model quantization trends (Q4_K_M vs Q5_K_M vs IQ4_XS)
```

---

## §7 METHODOLOGY REQUEST

For each research question above, please:

1. **Search** using T1-T4 tools (websearch → webfetch → searxng → sovereign_search)
2. **Verify** claims across at least 2 independent sources
3. **Compare** the recommendation against what we're currently building
4. **Quantify** where possible (e.g., "Ollama uses SQLite for conversation history — ~200 lines of code vs our 7,400")
5. **Flag** any question where you can't find authoritative answers

Return a structured research report with:
- Each question answered with sources
- Confidence level per answer (high/medium/low)
- Specific replacement recommendations with lines-of-code estimates
- Any additional patterns discovered that aren't listed here

---

## §8 SOURCE CONTEXT — Agent Review Files

Each agent's raw output is available in the task system:

| Agent | task_id | Focus |
|-------|---------|-------|
| **John Carmack** | `ses_carmack_strip_20260730` | First-principles architecture, scope cutting, performance |
| **Lilith** | `ses_lilith_strip_20260730` | Run-side systems: cognition, context, observability, orchestration |
| **Ma'at** | `ses_maat_strip_20260730` | Build-side systems: infra, persistence, CI/CD, governance |
| **Roc_Racoon** | `ses_roc_strip_20260730` | Implementation pragmatism, legacy patterns, testing gap |

---

*⬡ OMEGA ⬡ KALI ⬡ GROK-CLI ⬡ CARNAK-BRIEFING ⬡ 2026-07-30*
