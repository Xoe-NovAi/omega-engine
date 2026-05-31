# 🔱 Gemma 4-31B Research Specialist — Strategic Brief

**AP Token**: `AP-GEMMA-RESEARCH-BRIEF-v1.0.0`
⬡ OMEGA ⬡ PROMETHEUS ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_research ⬡ BRIEF

**Date**: 2026-05-16
**Replaces**: This document supersedes `docs/operations/RESEARCH_QUEUE.md` as the active research tasking document
**Companion**: [R52_strategy_execution_plan.md](R52_strategy_execution_plan.md) — master strategy document with 4-track plan, risk register, timeline, and architectural decisions
**Audience**: Gemma 4-31B — dedicated OpenCode CLI research session

---

## §0 Letter to the Researcher

> Gemma 4-31B — you are the Omega Engine's most capable research agent. Your 256K context window lets you hold entire codebases in memory. Your role is to produce **actionable intelligence** — findings with version numbers, URLs, measured values, and code snippets — that the implementation agents (MiniMax M2.5, deepseek-v4-flash, Gemini CLI) can build from without ambiguity.
>
> The Omega Engine has completed Sprint A→D (Blocker Remediation). All 8 real bugs from the comprehensive audit are fixed. 123/123 tests pass. The Provider Fabric (Google, OpenRouter, lmster) is fully wired. The ContextBuilder wiring spec is complete (R-51) and ready for implementation.
>
> Your job is to **stay ahead of the implementers** — research the next layer so that when they finish wiring ContextBuilder, they have clear specs for Phase 1 tasks.
>
> Work in priority order. Every deliverable goes to `docs/research/`. Every update goes to `docs/research/INDEX.md`.

---

## §1 Project Context

### Where We Are

| Phase | Tasks Complete | Tasks Remaining | Next Action |
|-------|---------------|-----------------|-------------|
| Phase 0: MVE | 16/18 | 2 (lmster heartbeat, ContextBuilder wiring) | **ContextBuilder wiring has a complete spec (R-51)** |
| Phase 1: Inference & Soul | 0/13 | 13 | Needs research on native inference, soul architecture, lesson abstraction |
| Phase 2: Intake & Memory | 0/10 | 10 | Needs research on Qdrant integration, Mnemosyne memory |
| Phase 3: Orchestration | 0/9 | 9 | MCP ecosystem, resilience |
| Phase 4: Arcana-Nova Stack | 0/7 | 7 | Axiom generation, VR assets |
| Phase 5: Community | Open | Open | Future |

### Current Architecture State

```
Query → Oracle.talk() → Iris speculative decode (confidence check)
  ├── high confidence → Iris responds (functiongemma-270m)
  └── low confidence → escalate to domain-matched Pillar Keeper → ModelGateway
       → ContextBuilder (NOT WIRED — spec ready)
       → MemoryStore (NOT WIRED — spec ready)
       → SessionManager (NOT IMPLEMENTED — spec ready)
       → Provider Fabric (FULLY WIRED — Google/OpenRouter/lmster working)
```

### Key Files to Understand

| File | Purpose | Status |
|------|---------|--------|
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router | Working, needs memory wiring |
| `src/omega/oracle/context_builder.py` | Memory injection for prompts | Complete, NEVER called |
| `src/omega/memory_store.py` | Hot/Warm/Cold conversation storage | Complete, DATA_DIR path wrong |
| `src/omega/oracle/model_gateway.py` | Provider fabric inference chain | Working — Google/OpenRouter/lmster |
| `src/omega/oracle/providers.py` | Individual provider implementations | Working |
| `config/providers.yaml` | Provider chain configuration | Working |
| `config/entities.yaml` | Entity definitions (16 entities) | Working |
| `data/entities/arch/soul.yaml` | User soul file | Working |
| `docs/research/R51_context_builder_wiring_spec.md` | **ContextBuilder wiring spec** | Complete — 8h, 4 phases, 37 tests |

---

## §2 Immediate Research Queue (Priority Order)

> **⚠️ Updated Priority**: The master strategy at [R52_strategy_execution_plan.md](R52_strategy_execution_plan.md) defines a new execution order. Items R-52a, R-52b, and R-52c now take priority over the previous P0 items. Complete these first.

### 🔴 R-52a: OpenRouter Resilience Spec
**Urgency**: 🔴 Critical — Blocks stable cloud inference
**Blocking**: Provider Fabric reliability — ModelGateway needs retry, provider pinning, and key rotation before entities can reliably use cloud models
**Status**: 🔲 Not started
**Reference**: [R52_strategy_execution_plan.md §1](R52_strategy_execution_plan.md#-track-a--model-gateway-resilience-p0--immediate)

**Research Questions**:
1. What is the optimal retry strategy for OpenRouter 502/timeout errors? (Exponential backoff? Circuit breaker?)
2. How should `providers.yaml` be extended to support `provider.order`, `provider.sort`, and `models` fallback array?
3. What health monitoring pattern works for 8 API keys? (Health-based routing with Redis-backed state?)
4. How should `OpenAICompatProvider` pass OpenRouter routing parameters in the request body?
5. What provider slugs should be pinned for each free model? (`deepinfra/turbo` for DeepSeek? `together` for Llama?)

**Deliverable**: `docs/research/R52a_openrouter_resilience_spec.md`
- Exact code for retry wrapper (tenacity or custom AnyIO), health cache, key rotator
- `providers.yaml` schema extension with routing parameters
- Test plan: mock failure → verify fallback chain, mock rate limit → verify key rotation
- Implementation note for MiniMax M2.5

---

### 🔴 R-52b: Background Orchestrator Spec
**Urgency**: 🔴 Critical — Core to the "living world" vision
**Blocking**: Background worker architecture — entities need access to free cloud models as subagents
**Status**: 🔲 Not started
**Reference**: [R52_strategy_execution_plan.md §2](R52_strategy_execution_plan.md#-track-b--background-worker-orchestrator-p0--immediate)

**Research Questions**:
1. What is the optimal "Phone-a-Friend" architecture for Gemma 4-31B orchestrating OpenRouter free models?
2. Which free models are best for which tasks? (Deep reasoning → DeepSeek-V3? Code review → Llama-4-Maverick?)
3. How should `anyio.TaskGroup` manage concurrent calls across 8 API keys with `Semaphore(8)`?
4. What reviewer validation prompt ensures quality before disk write?
5. How should discoveries be recorded? (Library store? Research doc? Both?)

**Deliverable**: `docs/research/R52b_background_orchestrator_spec.md`
- Full `BackgroundWorker` class design with parallel execution, semaphore, key rotation
- Model capability matrix for free-tier OpenRouter models
- Reviewer prompt templates (coherence, security, alignment checks)
- Recording pipeline design (accepted → Library → research doc)
- Implementation note for MiniMax M2.5

---

### 🟡 R-52c: NotebookLM Ingestion Strategy
**Urgency**: 🟡 High — First-week priority
**Status**: 🔲 Not started
**Reference**: [R52_strategy_execution_plan.md §3-C1](R52_strategy_execution_plan.md#c1-notebooklm-ingestion-strategy)

**Research Questions**:
1. What file categorization schema keeps sources under 50MB and 50 per notebook?
2. How should the `prepare_notebooklm.py` script chunk files with header preservation?
3. What archive naming convention supports dated snapshots? (`omega-engine_{YYYY-MM-DD}_v{N}/`)
4. What is the ideal refresh schedule? (Weekly? Per PR?)

**Deliverable**: `docs/research/R52c_notebooklm_ingestion_strategy.md`
- File categorization plan
- `prepare_notebooklm.py` script structure
- Archive naming convention
- Refresh schedule recommendation

---

### 🟡 R-52d: Gemini Deep Research Automation
**Urgency**: 🟡 High — Pending strategy
**Status**: 🔲 Not started

**Research Questions**:
1. How to build a CLI wrapper that syncs the repo to a clean Drive account and triggers Deep Research?
2. What output pipeline captures Gemini reports and saves to `docs/research/`?
3. How to integrate with the user's existing clean-account + archive strategy?

**Deliverable**: `docs/research/R52d_gemini_automation.md`

---

### 🟡 R-52e: Claude GitHub PAT Integration
**Urgency**: 🟡 High — Pending strategy
**Status**: 🔲 Not started

**Research Questions**:
1. What fine-grained PAT scopes are minimal for repo access? (`contents:read`, `metadata:read`)
2. How should the connector/USL hybrid strategy be implemented across 8 accounts?
3. What is the per-account load distribution?

**Deliverable**: `docs/research/R52e_claude_github_integration.md`

---

### 🔴 R-19: Soul Abstraction Logic
**Urgency**: 🔴 Critical — Blocks Phase 1 soul architecture
**Blocking**: Implementation of lesson extraction from session logs
**Status**: 🔲 Not started

**Research Questions**:
1. What LLM-based techniques exist for extracting structured "lessons" from conversation logs?
2. How should lessons be structured in `soul.yaml`? Define schema: `relevance_tags`, `priority_weight`, `creation_timestamp`, `source_entity`, `confidence_score`, `domain`
3. What prompt patterns work best for lesson abstraction with the models we have (Gemma 4-31B, deepseek-v4-flash, qwen3-1.7b local)?
4. How should sessions be segmented for lesson extraction? (Every N exchanges? End of session? Timed intervals?)
5. What retrieval strategy should ContextBuilder use to inject relevant lessons into system prompts? (Semantic search? Keyword matching? Recency-weighted?)

**Deliverable**: `docs/research/R19_soul_abstraction_logic.md`
- Lesson schema specification (YAML format with all fields)
- Prompt templates for lesson extraction with each model tier
- Retrieval strategy for ContextBuilder lesson injection
- Example lesson extractions from real session logs

---

### 🔴 R-39: Legacy Library & Curation Deep Dive
**Urgency**: 🔴 Critical — Informs R-34 (Intake Pipeline)
**Blocking**: Design of the "Sentinel" intake pipeline
**Status**: 🔲 Not started

**Research Questions**:
1. Search `omega-stack-legacy/` and `xna-omega-legacy/` for all code related to: `crawler`, `curation`, `ingestion`, `library`, `extractor`, `sentinel`, `inbox`, `pipeline`
2. What extraction strategies were tried? (LLM-based? Regex? Hybrid?)
3. What caused each strategy to be abandoned?
4. What "High-Gnosis" filtering logic existed? How was content quality assessed?
5. What patterns should be RECLAIMED vs. LEFT BEHIND?

**Deliverable**: `docs/research/R39_legacy_library_deep_dive.md`
- Complete catalog of all intake/curation code found in legacy repos
- Assessment of each pattern: working/abandoned/experimental
- Top 3 reclaimable patterns with code snippets and file paths
- Failure analysis: why each abandoned strategy failed

---

### 🔴 R-40: Sovereign Lifecycle & Native Persistence
**Urgency**: 🔴 Critical — Required for Phase 1 robustness
**Blocking**: Systemd integration, KV-cache persistence, warm/cold hibernation
**Status**: 🔲 Not started

**Research Questions**:
1. Research `systemd` File Descriptor Store (`fdstore`, `memfd`) for preserving model KV-cache state across restarts
2. How does `uvicorn`/`starlette` behave with socket activation? What are the latency implications?
3. Define a three-tier hibernation strategy: **Warm** (keep in RAM), **Tepid** (keep KV-cache, unload model), **Cold** (save to disk, full reload)
4. What are the memory savings at each tier for a 1.7B vs 8B model?
5. What systemd unit configurations are needed for each tier?

**Deliverable**: `docs/research/R40_sovereign_lifecycle_persistence.md`
- systemd unit templates for each hibernation tier
- Memory measurements: RAM used by each model/quantization at each tier
- Latency measurements: restart time at each tier
- Implementation plan for Phase 1

---

### 🔴 R-41: Adaptive Orchestration Topologies (AdaptOrch)
**Urgency**: 🔴 Critical — Core to the Intelligence layer
**Blocking**: Multi-agent orchestration design
**Status**: 🔲 Not started

**Research Questions**:
1. How should "Coupling Density" (γ) be calculated from a natural language prompt? (Heuristic token-level? Semantic embedding similarity?)
2. Define "Debate Mode" formalization: when should two models compare answers? How to calculate Consistency Score (χ)?
3. What Redis Stream patterns work best for multi-agent state transparency?
4. What are the best practices for "Blackboard Architectures" in local-first AI systems?
5. How does this apply to the Omega Engine's entity council? (10 Pillar Keepers debating a single query)

**Deliverable**: `docs/research/R41_adapt_orch_topologies.md`
- Formal definitions of γ (Coupling Density) and χ (Consistency Score)
- Redis Stream channel design for inter-entity communication
- Debate Mode state machine
- Implementation plan for Phase 3

---

### 🔴 R-42: Hardware Steering (Ryzen 7 5700U / Zen 2)
**Urgency**: 🔴 Critical — Essential for Sprint 4 Optimization
**Blocking**: Core pinning, AVX2 optimization, iGPU offloading
**Status**: 🔲 Not started

**Research Questions**:
1. What is the optimal CCX-aware `AllowedCPUs` map for the 5700U's two CCX quads? (CCX0 = cores 0-3, CCX1 = cores 4-7?)
2. What Qdrant `m` and `ef_construct` parameters optimize for the 5700U's split L3 cache? (2x 4MB L3, one per CCX)
3. Can KV-cache be offloaded to the integrated Vega GPU via Vulkan? What are the latency/throughput tradeoffs?
4. What's the optimal thread count for llama.cpp on 8C/16T Zen 2? (Physical cores only? Hyperthreads beneficial?)
5. What `mlock()` and `numactl` configurations prevent NUMA-related memory latency?

**Deliverable**: `docs/research/R42_zen2_hardware_steering.md`
- `AllowedCPUs` map for each service (Iris, Redis, Qdrant, model inference)
- Qdrant HNSW tuning parameters for split L3 cache
- iGPU offloading feasibility report
- Phoenix (benchmark) script to validate recommendations
- Implementation plan for Sprint 4

---

### 🟡 R-20: Memory Tiering Strategy
**Urgency**: 🟡 High — Needed for Phase 2 memory architecture
**Status**: 🔲 Not started

**Research Questions**:
1. How should MemoryStore's three tiers (Hot/Warm/Cold) be tuned for the 14GB RAM constraint?
2. What triggers hot→warm→cold transitions? (Time-based? Capacity-based? Hybrid?)
3. What compression ratios are achievable at each tier? (Cold = gzip JSON, Warm = JSON, Hot = in-memory dict)
4. What's the optimal MAX_HISTORY for each tier given the 14GB ceiling?
5. How does MemoryStore's compaction logic handle multi-session conversations? (Is a session per-day or per-conversation?)

**Deliverable**: `docs/research/R20_memory_tiering_strategy.md`
- Memory budget per tier (Hot: X MB, Warm: Y MB, Cold: Z MB)
- Transition triggers and thresholds
- Compaction/archive scheduling strategy
- Integration with SessionManager (R-50 design)

---

### 🟡 R-23: Cold-Start Mitigation
**Urgency**: 🟡 High — User-facing first-impression issue
**Status**: 🔲 Not started

**Research Questions**:
1. What should a new user see on first invocation? (Greeting wizard? Default entity intro? Quick-start tutorial?)
2. How should first-time entity creation work? (Pre-seeded personality? Dynamic generation from entity name?)
3. What fallback responses should the Oracle give before any memory exists?
4. How to handle "soul from scratch" for new entities? (Warm-start from default knowledge? Cold-start with minimal prompt?)
5. What onboarding sequence minimizes user frustration on a 14GB system with no GPU?

**Deliverable**: `docs/research/R23_cold_start_mitigation.md`
- First-run UX flow (text-based, CLI-native)
- Default entity knowledge injection strategy
- Oracle response templates for pre-memory state
- Implementation plan for Phase 0/1 boundary

---

### 🟢 R-21: Agent Handoff Protocol
**Urgency**: 🟢 Strategic — Cross-CLI orchestration
**Status**: 🔲 Not started

**Research Questions**:
1. What format should a "State Packet" (JSON/YAML) use for transferring task progress between OpenCode, Cline, and Gemini CLI?
2. How to maintain entity persona and "working memory" during handoffs between CLI agents?
3. What Hivemind MCP mechanisms exist for state transfer? What needs to be built?
4. How should the Orchestrator (`orchestrator.py`) handle agent handoff failures? (Timeout? Retry? Escalate?)
5. What metadata should accompany a handoff? (Entity, completed subtasks, remaining work, context window state?)

**Deliverable**: `docs/research/R21_agent_handoff_protocol.md`
- State Packet schema (JSON format)
- Hivemind MCP channel design for handoff messaging
- Orchestrator handoff state machine
- Implementation plan for Phase 3

---

### 🟢 R-22: MCP Community Audit
**Urgency**: 🟢 Strategic — Ecosystem awareness
**Status**: 🔲 Not started

**Research Questions**:
1. What MCP servers exist in the community that are relevant to Omega? (Search, memory, file system, code analysis?)
2. What is the MCP protocol version landscape? (Are servers v1.0.0 compatible?)
3. Which community MCP servers are production-ready vs experimental?
4. How does Omega's current MCP ecosystem (Hivemind, Hub) compare to community standards?
5. What gaps exist that Omega needs to fill vs can adopt from community?

**Deliverable**: `docs/research/R22_mcp_community_audit.md`
- Catalog of 20+ relevant community MCP servers with version numbers
- Compatibility matrix with Omega's current MCP infrastructure
- Recommendations: adopt vs build vs ignore
- Security assessment of each community server

---

### 🟢 R-24: Soul-to-Visual Mapping (VR Foundation)
**Urgency**: 🟢 Strategic — Phase 4 AR/VR groundwork
**Status**: 🔲 Not started

**Research Questions**:
1. How should `soul.yaml` attributes (archetype, soul_power, lessons) map to Godot VR visual parameters? (Luminosity, geometry, sigil animation, color?)
2. What generative art techniques work for procedurally-generated entity avatars?
3. What's the minimum viable VR integration? (Godot 4? WebXR? Three.js?)
4. How should soul evolution be visualized? (Growing complexity? Brighter colors? More geometry?)
5. What performance constraints does the 5700U's integrated GPU impose on VR rendering?

**Deliverable**: `docs/research/R24_soul_to_visual_mapping.md`
- Attribute→Visual parameter mapping table
- MVP VR architecture decision (Godot vs WebXR vs Three.js)
- Performance budget for iGPU VR rendering
- Implementation plan for Phase 4

---

### 🟢 R-35: Agent Handoff & State Transfer Protocol
**Note**: Re-numbered from R-21 — this is the formalized spec once handoff research is done
**Urgency**: 🟢 Strategic — Phase 3
**Status**: 🔲 Not started (depends on R-21)

---

### 🟢 R-36: Soul-to-Visual Mapping (VR Foundation)
**Note**: Re-numbered from R-24 — formalized spec
**Urgency**: 🟢 Strategic — Phase 4
**Status**: 🔲 Not started (depends on R-24)

---

### 🟢 R-37: Axiom & Ideal Generation Framework
**Urgency**: 🟢 Strategic — Arcana-Nova Stack foundation
**Status**: 🔲 Not started

**Research Questions**:
1. What prompt-engineering system can generate 156 consistent Axioms (12 × 13 entities) with correct constellation resonance mapping?
2. How to ensure Light and Dark interpretations are symmetrical under the "Ma'at Balance" check?
3. What validation logic ensures axiom quality? (LLM-as-judge? Human review? Statistical checks?)
4. How should axioms be stored? (YAML? SQLite? JSON?)
5. What's the minimum viable set of axioms before the Arcana-Nova Stack is usable?

**Deliverable**: `docs/research/R37_axiom_ideal_framework.md`
- Generation prompt templates for axioms and ideals
- Ma'at Balance validation schema
- Storage schema for axioms (YAML)
- MVP: Which axioms to generate first for maximum coverage

---

### 🔴 R-43: ElevenLabs Sovereign Console (Hackathon Blitz)
**Urgency**: 🔴 Critical — Voice interface for Iris
**Blocking**: Real-time conversational voice demo
**Status**: 🔲 Not started

**Research Questions**:
1. What's the maximum acceptable round-trip time (RTT) for real-time conversational feel? (<500ms? <1s?)
2. How should a local "Filler Generator" maintain voice activity during sub-agent processing? (Piper TTS? espeak? Pre-recorded phrases?)
3. How does ElevenLabs interruption signaling work with streaming audio? What happens when the user interrupts a long response?
4. What's the latency budget breakdown for: STT (Whisper) → Agent reasoning → TTS (ElevenLabs/Piper)?
5. What fallback voice stack works offline? (Piper TTS → espeak → MaryTTS?)

**Deliverable**: `docs/research/R43_elevenlabs_sovereign_console.md`
- Latency budget spreadsheet (each component's target latency)
- Filler Generator architecture (local, no network dependency)
- Interruption state machine
- Fallback voice stack specification
- Implementation plan for Iris voice enhancement

---

## §3 Ongoing Monitoring Tasks (Weekly)

### M1: Provider Model Landscape Refresh
Run `scripts/check_free_models.sh --report` weekly and compare against `docs/research/model_db/.last_state.json`

**Research Questions**:
1. Have any new free models appeared on OpenRouter, Google AI Studio, or OpenCode Zen?
2. Have any models been deprecated or moved to paid-only?
3. Have context windows changed?
4. Are there new providers worth integrating?

**Deliverable**: Update `docs/research/model_db/CURRENT_MODELS.md` with any changes

### M2: OpenCode Release Monitoring
Track OpenCode CLI releases (currently v1.15.0) for new features relevant to Omega.

**Research Questions**:
1. What new features are in each OpenCode release?
2. How do new features impact Omega's agent/skill ecosystem?
3. Are there breaking changes to MCP server integration?
4. What performance improvements might affect session latency?

**Deliverable**: Update `docs/research/R15_opencode_v1.15.0_subagent_capabilities.md` as needed

---

## §4 Strategic Research Plan — Phased Approach (Updated)

> **Alignment**: This phased plan now parallels the [R52_strategy_execution_plan.md](R52_strategy_execution_plan.md), which defines a 3-week execution timeline with risk register, dependency graph, and implementation sprints.

### Phase A: Provider & Ecosystem Foundation (Week 1)
Focus: Model Gateway resilience, background orchestration, external AI ecosystem

| Priority | Items | Rationale |
|----------|-------|-----------|
| P0 | **R-52a** (OpenRouter Resilience) | Blocks stable cloud inference — retry, provider pinning, key rotation |
| P0 | **R-52b** (Background Orchestrator) | Core to "living world" vision — phone-a-friend subagent model |
| P1 | **R-52c** (NotebookLM Strategy) | Enables external knowledge ingestion — manual OK, sync desired |
| P1 | **R-52d** (Gemini Automation) | Deep Research integration — pending strategy item |
| P1 | **R-52e** (Claude GitHub PAT) | 8-account hybrid connector strategy — temp public acceptable |

### Phase B: Soul & Memory Architecture (Week 2)
Focus: ContextBuilder wiring, soul abstraction, memory tiering

| Priority | Items | Rationale |
|----------|-------|-----------|
| P0 | R-19 (Soul Abstraction) | ContextBuilder needs lesson schema for soul injection |
| P1 | R-20 (Memory Tiering) | 14GB RAM constraint demands careful memory management |
| P1 | R-39 (Legacy Library) | Intake pipeline design depends on understanding what was tried before |
| P1 | R-40 (Lifecycle/Persistence) | Systemd integration needed for Phase 1 reliability |

### Phase C: Hardware & Performance (Week 2-3)
Focus: Making the engine efficient on the 5700U

| Priority | Items | Rationale |
|----------|-------|-----------|
| P0 | R-42 (Hardware Steering) | Optimal performance requires tuned CCX pinning and AVX2 optimization |
| P2 | R-23 (Cold-Start) | Better first-user experience, lower urgency |

### Phase D: Strategic Architecture (Week 3-4)
Focus: Phase 3-5 architectural groundwork

| Priority | Items | Rationale |
|----------|-------|-----------|
| P1 | R-41 (AdaptOrch) | Multi-agent orchestration design |
| P2 | R-43 (ElevenLabs) | Voice interface for Iris |
| P2 | R-22 (MCP Audit) | Ecosystem awareness |
| P3 | R-21 (Agent Handoff) | Cross-CLI orchestration |
| P3 | R-37 (Axiom Framework) | Stack foundation |
| P3 | R-24/R-36 (VR Mapping) | Phase 4 groundwork |

### Phase E: Ongoing Monitoring
- **Weekly**: Refresh provider model landscape (M1)
- **Bi-weekly**: Check OpenCode release notes (M2)
- **As needed**: Cross-reference research with implementation team

---

## §5 Specific Questions for Gemma 4-31B

These are the highest-leverage questions. Answering these will enable the implementation team to move faster.

### About Soul Abstraction (R-19)
1. For a 500-line session log between a user and Sekhmet, what prompt would you use to extract the key lesson? Show me the exact prompt template.
2. What fields should a lesson schema have beyond `lesson`, `domain`, and `confidence`? Should lessons include counter-examples?
3. How should ContextBuilder weigh lessons? (Similiarity to current query? Recency? Entity affinity? All three combined?)
4. What happens when two lessons contradict each other? How should the system resolve this?

### About the Intake Pipeline (R-39)
1. What proven crawling/extraction patterns exist in the legacy repos? (Show file paths and code snippets.)
2. Why were earlier ingestion pipelines abandoned? (Memory limits? Quality issues? Maintenance burden?)
3. What "High-Gnosis" filtering heuristics are worth reclaiming?

### About Hardware Optimization (R-42)
1. What `numactl` and `mlock()` configuration would you recommend for the Ryzen 7 5700U with 14GB RAM?
2. What Qdrant HNSW parameters (`m`, `ef_construct`, `ef_search`) optimize for a 4MB L3 cache?
3. Can the integrated Vega GPU accelerate any part of the pipeline? (KV-cache? Embedding? Reranking?)

### About Cross-Cutting Concerns
1. Which of the research items above are actually BLOCKING vs. STRATEGIC? (Help me re-prioritize based on what the implementers actually need next.)
2. Are there any research items I've missed that you think are critical?
3. What's the one thing you'd research first that would provide the most value to the implementation sprint?

---

## §6 Deliverable Format

Every completed research item must produce:

1. **A markdown document** at `docs/research/R##_<slug>.md` with:
   - The standard Omega session header
   - AP Token and date
   - Specific findings with version numbers, URLs, code snippets
   - Uncertainty log (what remains unknown)
   - Implementation note (addressed to the Builder)
   - All URLs consulted

2. **An entry** in `docs/research/INDEX.md`:
   ```
   | R-XX | Title | 🔴/🟡/🟢 | ✅ | [R-XX_...](R-XX_....md) | 2026-05-16 |
   ```

3. **A completion post** in `docs/team/COMMUNICATION_HUB.md` under `## 📡 Research Completions`

4. **An implementation note** at the bottom of the research doc with a direct address to the implementation agent (MiniMax M2.5 or deepseek-v4-flash) containing:
   - The exact change to make
   - Which files to modify
   - What not to break (existing tests)
   - How to verify the fix

---

## §7 Tool Access

You have the following tools available for research:

| Tool | Purpose |
|------|---------|
| `sovereign-search` skill | Intelligent search across Exa, Brave, Tavily |
| `knowledge-miner` skill | Grep→read→summarize for codebase pattern extraction |
| `websearch` | Real-time web search |
| `webfetch` | Full-page content extraction |
| `glob`/`grep` | Filesystem pattern/content search |
| `scripts/check_free_models.sh` | Live API queries to OpenRouter, Google, OpenCode Zen |

Use `scripts/check_free_models.sh --report` for provider landscape queries.
Use `sovereign-search` for deep web research (multi-provider fallback).
Use `knowledge-miner` for legacy repo pattern extraction.

---

## §8 Quick Reference

| What | Where |
|------|-------|
| Research Index | `docs/research/INDEX.md` |
| Research Queue | `docs/research/GEMMA_4_31B_RESEARCH_BRIEF.md` (This file) |
| Master Strategy | `docs/research/R52_strategy_execution_plan.md` |
| ROADMAP.md | `docs/ROADMAP.md` |
| Decision Log | `docs/decisions/PIVOT_LOG.md` |
| Oracle Stack Context | `ORACLE_STACK.md` |
| Agent Rules | `AGENTS.md` |
| Architecture Framework | `docs/architecture/framework.md` |
| Core Engine | `src/omega/oracle/oracle.py` |
| ContextBuilder | `src/omega/oracle/context_builder.py` |
| MemoryStore | `src/omega/memory_store.py` |
| Model Gateway | `src/omega/oracle/model_gateway.py` |
| Provider Config | `config/providers.yaml` |
| Entity Config | `config/entities.yaml` |
| Test Suite | `tests/` (123 tests) |
| Provider Validator | `.opencode/skills/provider-validator/SKILL.md` |
| Legacy Omega Stack | `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/` |
| Legacy XNA Omega | `/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/` |

---

*Research is not knowledge until it is documented. Documentation is not wisdom until it is applied.*

⬡ OMEGA ⬡ PROMETHEUS ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_research ⬡ BRIEF-END
