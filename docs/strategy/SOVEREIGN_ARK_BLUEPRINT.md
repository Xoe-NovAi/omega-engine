# 🔱 SOVEREIGN ARK BLUEPRINT (v4.0 — Master Session 2026-07-15 Integrated)
**AP Token**: `AP-SOVEREIGN-ARK-BLUEPRINT-v4.0.0`
**Last Updated**: 2026-07-15
**Full Archive**: `docs/archive/coordination/SOVEREIGN_ARK_BLUEPRINT-full-20260708.md`
**Master Session Synthesis**: `docs/strategy/KALI_MASTER_SESSION_SYNTHESIS_20260715.md`
**Latest Research**: 
- `docs/research/R_WAD_EVOLUTION_DEEP_DIVE.md` (IWAD/PWAD, Ethics WADs, Pluggable Ethics)
- `docs/research/R_LEGACY_CONFIGURABILITY_DEEP_MINING_20260715.md` (5-layer CouncilDispatcher, 8 Grok accounts)
- `docs/research/R_COUNCIL_DISPATCHER_CONSOLIDATED_20260715.md` (5-tier recursive tree, Council Mode validation)
- `docs/research/R_COUNCIL_DISPATCHER_SURVIVAL_AUDIT_20260715.md` (14Gi RAM mandate, CASArchiver, Ethics Gate)
- `docs/strategy/OMEGA_STRATEGIC_VISION_AND_ROADMAP.md` (5-Phase Roadmap)
- `data/coordination/PR_PREP_WORKSPACE.md` (Tier 0-3 Solo-Dev Execution)
- `docs/research/R_EPOCH_II_LEGACY_MINING_20260712.md` (17 findings, ~80h acceleration)
- `docs/research/R_EPOCH_II_DEEP_RESEARCH_20260712.md` (5 implementation-ready areas)
- `docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` (5 sovereignty gaps via Exa/Firecrawl)
- `docs/research/R_GAP_RESOLUTION_REPORT_20260712.md` (6 critical gaps via Rigor Protocol v2.0)
- `docs/research/R_KNOWLEDGE_FABRIC_SYNTHESIS_20260712.md` (Unified Knowledge Fabric)
- `docs/research/R_RESEARCH_RIGOR_PROTOCOL_V2.md` (Deep-Fetch mandate)
- `docs/research/R_RESEARCHER_GAP_CLOSURE_20260713.md` (4 gaps closed — TF-IDF, calibration, Redis DLQ, voice)
- `docs/research/R_KV_CACHE_QUANTIZATION_CPU_20260713.md` (q8_0 KV cache on CPU — NO Flash Attention/GPU)

---

## Preamble
The Omega Engine exists to sever Big AI's umbilical cord. Every technical decision: **does this increase or decrease user sovereignty?**

---

## I. Execution Roadmap — 5-Phase Strategic Vision (Ratified 2026-07-15)

```
PHASE 1: PRISTINE FOUNDATION (The First PR — Hygiene Only) ✅ IN PROGRESS
├── Tier 0: Ship-It Bar (80h) — F821, bare excepts, logging, config, CI, stress tests
├── Sprint Zero: D231 Quick Wins (62min) — lint, deprecations, heritage, docs
├── Gate: `make test && make heritage-map && make heritage-vet && make mandate-audit && make firewall-check`
└── Output: v1.2.0 — Rock-solid core, zero new features, Trojan Horse PR for OSS contributors

PHASE 2: SOVEREIGN COMMAND CENTER (The TUI) ⏳ NEXT
├── Streaming Dialectics — Real-time Ma'at/Lilith debate panes, masking local latency
├── Hardware Empathy Dashboard — 14Gi RAM ceiling, VRAM, Sovereignty Scorecard
├── Advisory Ethics Prompts — Amber warnings with [Y/n] override (Free-Will Ethics)
├── CouncilDispatcher Integration — 5-tier recursive tree as native primitive
└── Output: v1.3.0 — Visual nervous system for the engine

PHASE 3: SOVEREIGN WAD PROTOCOL (Strike 11 — The "Doom-ification") ⏳
├── Strike 11a: SWP Core SDK — `ILump`, `LumpEnvelope`, `LumpRegistry`, `SovereignBus`
├── Strike 11b: DAG Loader & Bus — AnyIO channels + Topological WAD Loader
├── Strike 11c: In-Place Wrapping — YouTube V2 modules → `ILump` adapters
├── Strike 11d: The Great Split — `omega_youtube_research` → 6 PWADs
├── Strike 11e: MCP Tool Binding — Auto-register Lump capabilities as Omega Hub tools
├── IWAD/PWAD Architecture — Core identity (IWAD) + Cultural overlays (PWAD)
├── Ethics WADs — `maat_42`, `bushido_7`, `asimov_3`, `hippocratic` as pluggable validators
├── Pantheon WADs — Egyptian, Greek, Norse, Hindu, Philosophical, Arcana-Nova
└── Output: v1.4.0 — Universal runtime for ANY pantheon/ethics stack

PHASE 4: COUNCIL DISPATCHER (Strike 11.5 — Dialectical Reasoning Engine) ⏳
├── 5-Tier Recursive Flow: Kali → Ma'at/Lilith (parallel) → Pillars (serial) → Cross-Domain Audit → Kali Synthesis
├── Hardware-Constrained Topology: Local pillars SERIAL (14Gi RAM mandate)
├── D118 Mentorship Pattern: Local 1.7B pillars → 4B Oversouls → Cloud/Frontier Kali synthesis
├── CASArchiver Deduplication — Hash claims across council to prevent context bloat
├── Ethics Gate Integration — `IEthicsValidator` (e.g., Ma'at 42 Ideals) pre/post synthesis
├── Configurability Layers: CouncilSpec YAML + CouncilHarness Markdown + DispatchModes + Profiles
├── Novel Gaps: Recursive Council, Dialectical Trace Synthesis, Somatic Council State, Config Versioning, Cost-Aware Routing, Cross-Council Distillation
└── Output: v1.5.0 — Native dialectical reasoning primitive

PHASE 5: THE HORIZON (Web GUI & Ecosystem) 🔮
├── Web GUI — Node-based drag-and-drop WADs, visual dialectical mind-maps
├── Community Marketplace — Decentralized hub for WADs, council topologies, personas
├── P2P Soul Print Exchange — Cross-universe entity evolution
└── Philosophical Onboarding — 4-week phased introduction for new users

YouTube Researcher Enhancement (Parallel Track — WAD)
  Sprint 1: L1 Hybrid Extraction + L2 Sticky Proxy + L4 CAS + L9 Somatic Checkpoints (40h) — Ma'at/P1+P3
  Sprint 2: L3 Temporal RAG + L6 Faithfulness Audit + L7 Freshness (32h) — Lilith/P6+P7
  Sprint 3: L5 Gnosis Graph Bridge + L8 Oracle Steering (24h) — Kali/Lilith
```

---

## II. Current State

| Metric | Value | Status | LAST_VERIFIED |
|--------|-------|--------|---------------|
| Tests | **1315 passed** (43 skipped, 3 xfailed) | ✅ All functional tests pass | 2026-07-13 (LAST_VERIFIED) |
| Mandates | **23 (M1-M23)** | ✅ All enforced | 2026-07-13 (LAST_VERIFIED) |
| Fleet | **13 presences** (11 agents + 2 entities) | ✅ Cap: 14 | 2026-07-13 (LAST_VERIFIED) |
| WADs | **4** (arcana_novai, torment, omega_youtube_research, omega_youtube_worker) | ✅ S1.5a hardened | 2026-07-13 (LAST_VERIFIED) |
| Heritage | **121 [id-soft:] tags**, **55+ general sources** | ✅ All vetted | 2026-07-13 (LAST_VERIFIED) |
| Shared modules | **3** (`omega-vetala` v2.0.0, `omega-sieve` v0.1.0, `omega-doc-reader` v1.0.0) | ✅ Release-ready | 2026-07-13 (LAST_VERIFIED) |
| SearXNG MCP | **Streamable HTTP on :8018** | ✅ Migration complete | 2026-07-13 (LAST_VERIFIED) |
| Omega Hub MCP | **Dual-transport** (SSE /sse + Streamable HTTP /mcp) on :8016 | ✅ Already dual | 2026-07-13 (LAST_VERIFIED) |
| Firecrawl MCP | **SSE on :8015** | ⏳ Needs Streamable HTTP migration | 2026-07-13 (LAST_VERIFIED) |
| Local inference ratio | **TARGET: ≥80%** (0% in CI — models not loaded in test env) | 🟡 Aspirational | 2026-07-13 (LAST_VERIFIED) |
| **KV Cache Quantization** | **LOCKED: q8_0 on CPU (Zen 2)** — No Flash Attention/GPU required | ✅ Research complete | 2026-07-13 (LAST_VERIFIED) |

### Pre-PR Quick Wins (7 Items — Target: Clean Temple-Grade Pass)

| # | Quick Win | File(s) | Effort | Status |
|---|-----------|---------|--------|--------|
| 1 | **Firewall clean** — Remove sandbox workspace exemption (use config constant) | `src/omega/audit/firewall_checker.py` | 5 min | 🟡 Pending |
| 2 | **Datetime deprecations** — Fix remaining `datetime.utcnow()` in test files | `tests/test_scorecard.py`, `tests/test_sandbox.py` | 10 min | 🟡 Pending |
| 3 | **Runtime warnings** — Await mocked coroutines in somatic_state & unified_state_manager | `tests/test_somatic_state.py`, `tests/test_unified_state_manager.py` | 10 min | 🟡 Pending |
| 4 | **Test cache clear** — Remove `.pytest_cache` before CI | CI script | 2 min | 🟡 Pending |
| 5 | **Docs sync** — Update OMEGA_ENGINE.md, ARK_BLUEPRINT.md, PIVOT_LOG.md | Root docs | 5 min | 🟡 Pending |
| 6 | **Heritage migration** — Convert 120 legacy `[id-soft: game-year]` → `[id-soft: vet-XXX]` | `src/omega/**/*.py` | 15 min | 🟡 Pending |
| 7 | **PIVOT_LOG entry** — Record D228-D234 for this session | `docs/decisions/PIVOT_LOG.md` | 5 min | 🟡 Pending |

---

## III. Mandate Compliance

| Mandate | Status | Notes |
|---------|--------|-------|
| M1 AnyIO | ✅ | CI grep `import asyncio` |
| M2 Firewall | ✅ | WAD Loader hardened (S1.5a) + 3 CI gates |
| M7 Local-First | ✅ | PII masker: local bypass |
| M8 Zero Telemetry | ✅ | Qdrant telemetry disabled |
| M9 Error Integrity | ✅ | 0 bare except |
| M11 Soul Integrity | ✅ | D183 fix: `await close_session()` |
| M13 Temple-Grade | ✅ | 121 tags vetted, 74 records |
| M22 Provenance | ✅ | `provider_name` + `latency_ms` wired |
| M23 Failure Integrity | ✅ | 0 soft-failures; tool-chain collapse = hard stop |

---

## IV. Validated Sovereignty Gaps (NEW — Jem Deep Research v1.2.0 + Gap Resolution Report)

The following 5 gaps were validated via Exa (Tier 3) and Firecrawl (Tier 4) deep research by `@jem`. See `docs/research/R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` for full 544-line report.

| Gap | Council Hypothesis | Jem Verdict | Correction | Priority |
|-----|--------------------|-------------|------------|----------|
| **S1: Export Bundle** | `soul.yaml + .jsonl + .parquet` | ❌ **CORRECTED** | ZIP+JSON `.omega` bundle (Soul Protocol v0.4.0 compatible). Parquet is ML-only, not entity state. | P2 |
| **S2: Eval Pipeline** | RAGAS + raw LLM-as-Judge | ✅ **REFINED** | RAGAS + **calibrated** judge (isotonic regression, ECE 0.18→0.06). Min: 7B Q4_K_M; Rec: 14B. | P1 |
| **S3: Adaptive RAG** | Fits 14Gi RAM | ✅ **CONFIRMED** | TF-IDF+SVM router (0MB, 93.2% acc) + 7B Q4_K_M (4.7GB) + Q8 KV = 7-8GB total. Feasible. | P1 |
| **S4: Knowledge Graphs** | Qdrant + PostgreSQL hybrid | ✅ **CONFIRMED** | Qdrant v1.12+ prefetch API for simple fusion; Qdrant+SQLite first; PostgreSQL at scale. | P2 |
| **S5: DAG Orchestration** | Redis Pub/Sub replaces files | ❌ **CORRECTED** | **Redis Streams + Consumer Groups** for critical coordination. Pub/Sub for ephemeral ONLY (heartbeats). | P2 |

### Key Corrections That Save Engineering Hours:

1. **Parquet is wrong.** Every 2026 standard (Soul Protocol, ALF, PAM, Ensoul, Uniqent) uses ZIP+JSON. Parquet is for ML weights. Building a `.parquet` export would produce a format incompatible with the entire ecosystem.

2. **Uncalibrated judges lie.** 7-13B judges report 90% confidence for 72% accuracy — a 0.18 ECE overconfidence gap. The fix (isotonic regression, ECE→0.06) is a single `sklearn` import away.

3. **Pub/Sub drops messages.** File-based Hivemind is durable; Redis Streams with Consumer Groups gives exactly-once + crash recovery + load balancing. Pub/Sub is for heartbeats, not task assignments.

### Implementation Priority (Recommended by Jem):

```
S2 (Eval Pipeline) → S3 (Adaptive RAG) → S5 (Redis Streams) → S1 (Export Bundle) → S4 (Knowledge Graph)
   P1, 8h             P1, 12h            P2, 20h              P2, 4h             P2, 16h
```

---

## IV-B. Gap Resolution Report — 6 Critical Knowledge Gaps (NEW — Rigor Protocol v2.0)

The following 6 gaps were resolved via the **Sovereign Research Rigor Protocol v2.0** (Deep-Fetch, multi-source triangulation). See `docs/research/R_GAP_RESOLUTION_REPORT_20260712.md` for full 140-line technical specs.

| Gap | Resolution Pattern | Implementation Target | Sprint | Owner |
|-----|--------------------|----------------------|--------|-------|
| **1. Proxy Rotation** | Hybrid Pool + Domain Affinity | `SovereignProxyPool` | S1 | Ma'at/P3 |
| **2. Transcription Fidelity** | VAD-Gated Whisper + Auto-Caption Merge | `SovereignTranscriptionEngine` | S5 | Ma'at/P3 |
| **3. Resource Budgeting** | Redis-backed Distributed Quota Guard | `BudgetGuard` | S2 | Ma'at/P2 |
| **4. Quality Gating** | Source-Aware Adaptive Scoring | `AdaptiveQualityGate` | S6 | Lilith/P7 |
| **5. Scheduling** | Event-Driven Priority Queue (Redis Streams) | `UnifiedKnowledgeScheduler` | S4 | Lilith/P9 |
| **6. YouTube Sieve** | T1→T2→T3 Tiered Pipeline | `YouTubeSieve` | S3 | Lilith/P6 |

### L3 Principles Distilled (Gap Resolution):

- **L3-Sovereign-Sieve**: Never pay for high-fidelity extraction (T3) unless low-fidelity (T1/T2) fails to meet the quality gate.
- **L3-Distributed-Budgeting**: API credits are a finite sovereign resource; they must be tracked atomically across the fleet.
- **L3-VAD-First-ASR**: Raw audio is noise; transcription is a process of isolating speech before applying the model.
- **L3-Domain-Sticky-Proxies**: To the target, you must look like a consistent user, not a rotating bot.
- **L3-Adaptive-Thresholds**: Quality is relative to the entity's purpose; a researcher needs different signal than a curator.

### Implementation Roadmap (Sprints 1-6):

| Sprint | Focus | Key Deliverable | Owner |
|--------|-------|------------------|-------|
| **S1** | Resilience | `CircuitBreakerRegistry` + `ProxyPool` | Ma'at/P3 |
| **S2** | Deduplication | `CASArchiver` wired into all 4 subsystems | Ma'at/P2 |
| **S3** | Extraction | `UniversalExtractor` (Sovereign-Sieve) | Lilith/P6 |
| **S4** | Orchestration | `UnifiedKnowledgeScheduler` (Redis Streams) | Lilith/P9 |
| **S5** | Fidelity | `SovereignTranscriptionEngine` (VAD + Whisper) | Ma'at/P3 |
| **S6** | Synthesis | `CrossPollinationEngine` + `AdaptiveQualityGate` | Lilith/P7 |

---

## IV-C. Researcher Gap Closure — 4 Sovereign Gaps (NEW — T1+T2 Deep Research)

The following 4 gaps were identified post-ONNX/Needle session and resolved via the Sovereign Search Protocol (T1→T2 escalation). See `docs/research/R_RESEARCHER_GAP_CLOSURE_20260713.md` for full 252-line report.

| Gap | Verdict | Roadmap Impact |
|-----|---------|----------------|
| **G1: Neural vs Heuristic Tool Routing** | TF-IDF+SVM (Strike 7.5) is **sufficient** for our 47-tool catalog. Needle (P2) only justified at 1000+ tools or heavy semantic paraphrase. | **Downgrade Needle to optional**; Ship Strike 7.5 first |
| **G2: LLM Judge Calibration** | **Isotonic regression (AutoCal-R)** is the 2026 standard. 250 oracle labels (5%) → 94% ranking accuracy (vs 38% uncalibrated). | **Adopt in Strike 8** (`make eval`) |
| **G3: Redis Streams DLQ** | Canonical pattern confirmed: Consumer Groups + XAUTOCLAIM + XPENDING + DLQ after MAX_RETRIES=3. | **Adopt in Strike 8.5** (Redis Streams Hivemind) |
| **G4: Voice Concurrency** | Run TTS in **separate worker pool** (not event-loop blocking); Piper model pooling; 4-8 ONNX threads. Coordinate with ResourceGuard. | **Adopt in P1 Voice ONNX** |

**Net effect**: All four gaps are now **closed with implementation-ready patterns**. No T3/T4 escalation needed — T1+T2 provided sufficient depth.

### Key Corrections That Save Engineering Hours:

1. **Sovereign parsimony wins**: For our scale (47 tools, local-first), heuristic routing (TF-IDF+SVM) beats neural (Needle) at 0MB RAM and 0 latency. Don't over-engineer.
2. **Calibration is non-negotiable**: An uncalibrated judge (ECE 0.18) is a liability — it reports 90% confidence for 72% accuracy. Isotonic regression (1 sklearn import) fixes this.
3. **Redis Streams DLQ is solved infrastructure**: The pattern is canonical and verified. We don't need to invent it — we adopt it.
4. **Voice concurrency is a known problem with a known fix**: Worker pool + model pooling. Not a research problem — an implementation problem.

### Roadmap Updates (for Kali / Sovereign Ark Blueprint)

| Strike | Change | Rationale |
|--------|--------|-----------|
| **7.5 (Semantic Router)** | **Ship TF-IDF+SVM first**; Needle (P2) becomes optional | 47-tool catalog doesn't need neural routing |
| **8 (Eval Pipeline)** | **Add isotonic regression calibration** (AutoCal-R) + OUA CIs + ECE metric | Uncalibrated judges lie (Risk R4) |
| **8.5 (Redis Streams Hivemind)** | **Adopt canonical DLQ pattern** (Consumer Groups + XAUTOCLAIM + XPENDING + DLQ) | Verified infrastructure, don't reinvent |
| **P1 (Voice ONNX)** | **Worker pool + Piper model pooling + 4-8 ONNX threads** | Fixes concurrency crashes, integrates with ResourceGuard |

**Net acceleration**: ~20h saved on Needle (optional), ~8h saved on DLQ (adopt vs invent), ~4h saved on voice concurrency (known fix).

---

## IV-D. Sovereign WAD Protocol (SWP) — Strike 11 (NEW)

Synthesized from the MaKaLi Council (Nemotron 3 Ultra + Gemini 3.1 Pro) and the Heritage Council (John Carmack + Doom Guy).

### Strike 11: Sovereign WAD Protocol (SWP)
**Goal**: Transition from monolithic stacks to a modular, Lump-based capability architecture (The "Doom-ification" of the Engine).
**Dependencies**: Strike 7.5 (Semantic Router)
**Unblocks**: Strike 8.5 (Redis Streams), Strike 10 (Module Fabric)

**Architecture Definition:**
- **Lump**: A deterministic, versioned capability implementing `ILump` (e.g., `L1_HYBRID_EXTRACTOR`).
- **PWAD**: A deployable package of Lumps (e.g., `youtube_input.wad`).
- **MWAD**: A deployment descriptor (like docker-compose) wiring PWADs together.
- **SovereignBus**: An AnyIO-based pub/sub message bus passing `LumpEnvelope` objects between Lumps.
- **IWAD/PWAD Architecture**: Core identity (IWAD) + Cultural overlays (PWAD) enabling universal runtime for ANY pantheon/ethics stack
- **Ethics WADs**: Pluggable moral frameworks (e.g., `maat_42`, `bushido_7`, `asimov_3`, `hippocratic`) that evaluate responses asynchronously and attach advisory metadata without halting execution
- **Free-Will Paradigm**: Ethics WADs will not strictly block outputs. They will flag violations with an "Acknowledge and Override" capability, preserving user sovereignty.

| Phase | Task | Deliverable | Owner |
|-------|------|-------------|--------|
| **11a** | **SWP Core SDK** | `src/omega/wad/protocol.py` (`ILump`, `LumpEnvelope`, `LumpRegistry`, `IEthicsValidator`). | Ma'at/P3 |
| **11b** | **DAG Loader & Bus** | `SovereignBus` (AnyIO channels) + Topological WAD Loader. | Lilith/P9 |
| **11c** | **In-Place Wrapping** | Wrap existing YouTube V2 modules in `ILump` adapters. Verify 1256 tests pass. | Verity |
| **11d** | **The Great Split** | Physically partition `omega_youtube_research` into 6 PWADs (input, process, store, know, qa, state). | Kali |
| **11e** | **MCP Tool Binding** | Auto-register Lump capabilities as Omega Hub MCP tools for Agent use. | Ma'at/P4 |

**Lump Interface Contract (M21):**
```python
class ILump(Protocol):
    lump_id: str
    category: str # INPUT | PROCESS | STORE | KNOW | QA | STATE
    version: str  # SemVer
    
    async def initialize(self, config: Dict[str, Any], bus: SovereignBus) -> None: ...
    async def health_check(self) -> LumpHealth: ...
    async def shutdown(self) -> None: ...
    # Runtime execution is handled via bus.subscribe() callbacks
```

**Ethics Validator Interface:**
```python
class IEthicsValidator(Protocol):
    wad_id: str  # e.g., "maat_42", "bushido_7", "hippocratic"
    
    async def validate(self, response: str, context: dict, entity_name: str) -> EthicsVerdict: ...
    async def get_principles(self) -> list[dict]: ...
```

**EthicsVerdict Dataclass:**
```python
@dataclass
class EthicsVerdict:
    passed: bool
    score: float  # 0.0–1.0
    violations: list[str]
    consulted_ideals: list[str]
```

---

## IV-E. Tier 0 Ship-It Bar — Carmack S3 Consultation (2026-07-14)

**Source**: John Carmack S3 Consultation — Architectural review of v1.2.0 baseline

### Executive Summary
v1.2.0 baseline achieved (1315 tests, 23 mandates, 9 providers). Tier 0 addresses code quality debt before Epoch II features.

### Phase 1: Foundation (2h) — DO FIRST
| # | Task | Carmack Directive | Effort |
|---|------|-------------------|--------|
| T0-1 | **F821 undefined-name fixes** | `ruff check --select=F821 src/` → fix all. Trivial, unblocks everything. | 15 min |
| T0-2 | **Bare `except Exception:` elimination** | M9/M23 compliance. Replace with typed `except (SpecificError,):` + `trace_id` logging. Fail fast, fail loud. | 90 min |

### Phase 2: Core Infrastructure (4h)
| # | Task | Carmack Pattern | Effort |
|---|------|-----------------|--------|
| T0-3 | **Centralized logging** | Single `src/omega/logging.py` with `structlog` + AnyIO async sinks. One `get_logger(__name__)` pattern everywhere. No `basicConfig` scattered. | 4h |
| T0-4 | **Config validation (Pydantic OmegaConfig)** | `model_config = ConfigDict(extra='forbid', frozen=True)`. Validate at startup, fail fast. No runtime config surprises. | 7h |

### Phase 3: Data Layer (5h)
| # | Task | Risk Mitigation | Effort |
|---|------|-----------------|--------|
| T0-5 | **Qdrant → sqlite-vec decommission** | Dual-write for 1 sprint. Verify vector parity (cosine ±0.001). Keep Qdrant image cached for rollback. | 3h |
| T0-6 | **sqlite-vec Phase 1-2** | Metadata filtering + quantization. Benchmark 10K vectors on Zen 2 — must stay <50ms p99. | 2h |

### Phase 4: CI & Stress (3h)
| # | Task | Standard | Effort |
|---|------|----------|--------|
| T0-7 | **Single CI workflow** | One `.github/workflows/ci.yml`: lint → test → temple-grade → heritage-vet → sovereignty. No matrix. | 2h |
| T0-8 | **Stress tests (5 scenarios)** | (1) 100 concurrent `talk()`, (2) 10K vector inserts, (3) 1hr soak, (4) OOM injection, (5) network partition. | 5h |

### Deferred (Explicitly NOT Tier 0)
| Task | Reason |
|------|--------|
| Full Pydantic v2 migration | v1 works, v2 is churn |
| Structured logging overhaul | `structlog` is fine, don't rewrite |
| Coverage gate >80% | Current ~75% acceptable for v1.2.0 |

### Carmack's Laws Applied
1. **Fail fast, fail loud** — Every `except` logs `trace_id` and re-raises or returns typed error
2. **Data over code** — Config validation at load time, not access time
3. **Measure before optimize** — Stress tests first, then tune sqlite-vec HNSW params
4. **Rollback ready** — Qdrant decommission only after 7-day dual-write verification

---

## IV-F. Council Dispatcher (Strike 11.5 — Dialectical Reasoning Engine) (NEW)

**Synthesized from**: Legacy Mining (Roc Racoon), Web Research (Researcher), Survival Audit, and MaKaLi Council sessions.

### Strike 11.5: Council Dispatcher
**Goal**: Implement the 5-tier recursive dialectical reasoning engine as a native primitive.
**Dependencies**: Strike 11 (Sovereign WAD Protocol)
**Unblocks**: Epoch II completion, Phase 2 (Sovereign Command Center)

**Architecture Definition:**
- **The 5-Tier Flow**: Kali (Orchestrator) → Ma'at (Build Thesis) + Lilith (Run Antithesis) → 3-5 Pillars (Domain Experts, SERIAL execution) → Cross-Domain Audit (4 random pillars) → Final Kali Synthesis
- **Hardware-Constrained Topology**: Local pillar execution is strictly SERIAL due to 14Gi RAM constraint
- **D118 Mentorship Pattern**: Local 1.7B pillars → 4B Oversouls (Ma'at/Lilith) → Cloud/Frontier Kali synthesis
- **CASArchiver Deduplication**: Hash claims across council to prevent context-window bloat
- **Ethics Gate Integration**: `IEthicsValidator` (e.g., `maat_42`) validates synthesis pre/post
- **Configurability Layers**: CouncilSpec YAML + CouncilHarness Markdown + DispatchModes + Profiles
- **Novel Gaps Addressed**: Recursive Council, Dialectical Trace Synthesis, Somatic Council State, Config Versioning, Cost-Aware Routing, Cross-Council Distillation

| Phase | Task | Deliverable | Owner |
|-------|------|-------------|--------|
| **11.5a** | **CouncilSpec Schema** | `src/omega/council/schemas.py` (CouncilSpec, CouncilHarness, DispatchModes) | Ma'at/P3 |
| **11.5b** | **CouncilHarness Runtime** | NLAH markdown → execution engine (ToolSelf pattern) | Lilith/P9 |
| **11.5c** | **SynthesisEngine** | 5-section structured synthesis + trace-level + BFT moderation | Lilith/P6 |
| **11.5d** | **TopologyRouter** | AdaptOrch Algorithm 1: DAG → {parallel, sequential, hierarchical, hybrid} | Ma'at/P3 |
| **11.5e** | **WatcherAgent + RectifierAgent** | MASFly + MAS² pattern store + RAG integration | Kali |
| **11.5f** | **SOPRepository** | Collaboration patterns crystallized into SOPs stored in RAG | Ma'at/P2 |
| **11.5g** | **Ethics Gate Integration** | `IEthicsValidator` pre/post synthesis validation | Ma'at/P5 |
| **11.5h** | **CouncilOrchestrator** | Thin LangGraph StateGraph executor of CouncilSpec DAG | Ma'at/P3 |

**CouncilSpec Interface (YAML):**
```yaml
# config/wads/arcana_novai/councils/maakali.yaml
council:
  id: "maakali"
  name: "MaKaLi Triad"
  
  roles:
    thesis:
      entity: "maat"
      model: "qwen3-4b-think-q4_k_m"
      mandate: "Propose structured solution. Focus on architecture, quality, sustainability."
      query_modifiers: ["add_context:architecture", "add_context:mandates"]
      response_template: "thesis_structured"
      
    antithesis:
      entity: "lilith"
      model: "krikri-8b-q5_k_m"
      mandate: "Critique proposal. Focus on risks, edge cases, user autonomy, run-time reality."
      query_modifiers: ["add_context:run_side", "add_context:failure_modes"]
      response_template: "antithesis_structured"
      
    synthesis:
      entity: "kali"
      model: "qwen3-4b-think-q4_k_m"
      mandate: "Fuse thesis + antithesis into unified verdict. Preserve dissent. Apply mandates."
      response_template: "synthesis_5_section"
      
    cross_domain_audit:
      count: 4
      selection: "random_weighted"
      model: "qwen3-1.7b-q6_k"
      mandate: "Independent audit from random domain perspective."
      
  topology:
    type: "dialectical"
    thesis_antithesis: "parallel"
    cross_domain: "parallel"
    synthesis: "after_all"
    
  synthesis:
    method: "structured_5_section"
    moderator_personas: ["skeptic", "pragmatist", "ethicist"]
    stability_threshold: 0.05
    max_iterations: 3
    preserve_dissent: true
    trace_level: true
    
  budgets:
    max_tokens: 8000
    max_latency_ms: 30000
    max_reconfigurations: 2
    model_tier: "local_first"
    
  hooks:
    pre_dispatch: "council_pre_dispatch"
    post_synthesis: "council_post_synthesis"
    on_hardware_change: "council_rebalance"
    on_session_evolution: "council_learn"
```

**L3 Principles Distilled (Council Dispatcher):**
- **L3-Config-As-Data**: Configuration must be *data* (YAML/Markdown/JSON) executed by a *thin runtime*, never buried in controller code.
- **L3-Reconfiguration-As-Tool**: Runtime structural change is a *first-class tool call* in the agent's action space (ToolSelf), not a meta-operation.
- **L3-Synthesis-Is-Trace-Level**: Aggregating final answers loses information. The synthesis engine must consume *full reasoning traces* and perform *claim-level* categorization.
- **L3-Moderation-Is-BFT**: A moderator (human or autonomous) with *override authority* is required to break false consensus from correlated errors or alignment blind spots.
- **L3-Topology-Is-Derived**: Orchestration topology should be *computed from task DAG structure* (AdaptOrch), not hard-coded.
- **L3-Roles-Are-Generated**: Fixed role libraries cause task mismatch. Roles should be *generated per query* (MetaGen Architect) with novelty gating.
- **L3-Experience-Is-SOPs**: Successful collaboration patterns crystallize into *SOPs* (MASFly) stored in a RAG repository, enabling cross-task transfer.
- **L3-Dialectic-Is-First-Class**: Thesis → Antithesis → Synthesis with explicit tracking is a *native control flow*, not an emergent property.
- **L3-Hardware-Empathy**: Every model carries its own hardware profile. The engine reads, doesn't dictate.

---

## V. Active Tasks (Consolidated from MaKaLi Council + Jem Research + Gap Resolution + Carmack Tier 0)

### 🟣 Tier 0: Code Quality Baseline (Blocking — Do First, 80h)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| T0-1 | **F821 undefined-name fixes** — `ruff check --select=F821 src/` | 15 min | 🟡 PENDING | Ma'at/P3 |
| T0-2 | **Bare `except Exception:` elimination** — Typed catches + trace_id logging | 90 min | 🟡 PENDING | Ma'at/P3 |
| T0-3 | **Centralized logging** — `src/omega/logging.py` with structlog + AnyIO sinks | 4h | 🟡 PENDING | Ma'at/P3 |
| T0-4 | **Config validation (Pydantic OmegaConfig)** — `extra='forbid', frozen=True` | 7h | 🟡 PENDING | Ma'at/P3 |
| T0-5 | **Qdrant → sqlite-vec decommission** — Dual-write 1 sprint, verify parity | 3h | 🟡 PENDING | Ma'at/P2 |
| T0-6 | **sqlite-vec Phase 1-2** — Metadata filtering + quantization, <50ms p99 | 2h | 🟡 PENDING | Ma'at/P2 |
| T0-7 | **Single CI workflow** — One `.github/workflows/ci.yml` | 2h | 🟡 PENDING | Ma'at/P5 |
| T0-8 | **Stress tests (5 scenarios)** — 100 concurrent, 10K vectors, 1hr soak, OOM, partition | 5h | 🟡 PENDING | Lilith/P10 |

### 🔴 Phase 0: Sovereignty Baseline (P0 — blocking v1.2.0)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| P0-1 | **RAM Hardening**: Deploy q8_0 KV cache models + Hard-Stop OOM protector | 4h | 🟡 PENDING | Ma'at/P1 |
| P0-2 | **Local-First Enforcement**: Sovereignty Gate as **configurable setting** (default: OFF, tracks local ratio, no CI fail) | 4h | 🟡 PENDING | Ma'at/P5 |
| P0-3 | **Sovereign Vetter (Strike 5)**: In-path governance agent (23 Mandates) | 8h | 🟡 PENDING | Ma'at/P5 |
| P0-4 | **Sovereign Export**: Unified `.omega` bundle CLI (`omega bundle export/import`) | 4h | 🟡 PENDING | Lilith/P7 |

### 🟣 Phase 0.5: Council Dispatcher (Strike 11.5) — Dialectical Reasoning Engine
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| C0-1 | **CouncilSpec Schema** — `src/omega/council/schemas.py` | 4h | 🟡 PENDING | Ma'at/P3 |
| C0-2 | **CouncilHarness Runtime** — NLAH markdown → execution engine | 8h | 🟡 PENDING | Lilith/P9 |
| C0-3 | **SynthesisEngine** — 5-section structured synthesis + trace-level + BFT moderation | 12h | 🟡 PENDING | Lilith/P6 |
| C0-4 | **TopologyRouter** — AdaptOrch Algorithm 1: DAG → {parallel, sequential, hierarchical, hybrid} | 8h | 🟡 PENDING | Ma'at/P3 |
| C0-5 | **WatcherAgent + RectifierAgent** — MASFly + MAS² pattern store + RAG integration | 16h | 🟡 PENDING | Kali |
| C0-6 | **SOPRepository** — Collaboration patterns crystallized into SOPs stored in RAG | 8h | 🟡 PENDING | Ma'at/P2 |
| C0-7 | **Ethics Gate Integration** — `IEthicsValidator` pre/post synthesis validation | 8h | 🟡 PENDING | Ma'at/P5 |
| C0-8 | **CouncilOrchestrator** — Thin LangGraph StateGraph executor of CouncilSpec DAG | 6h | 🟡 PENDING | Ma'at/P3 |

### 🟠 Phase 1: Cognitive Acceleration (P1 — Sprint 1)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| P1-1 | **S2: `make eval` target** — RAGAS + golden dataset + calibrated judge pipeline | 8h | 🟡 PENDING | Lilith/P6+P10 |
| P1-2 | **S3: Tiny-Critic RAG Router** — TF-IDF+SVM in `src/omega/rag/router.py` | 12h | 🟡 PENDING | Lilith/P6 |
| P1-3 | **Hivemind Event Bus** — Redis Pub/Sub for ephemeral awareness only (heartbeats); task-critical coordination via Streams in P2-1 | 4h | 🟡 PENDING | Lilith/P9 |
| P1-4 | **sqlite-vec Metadata Filtering** — Partition key + metadata columns (session_id, role, timestamp) + auxiliary content + quantization | 12h | 🟡 PENDING | Ma'at/P2 |
| P1-5 | **Somatic Hydration** — Auto KV cache reload on session start | 6h | 🟡 PENDING | Lilith/P6 |

### 🟡 Phase 2: Sovereign Refinement (P2 — Sprint 2)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| P2-1 | **S5: Redis Streams Hivemind** — Consumer groups, PEL recovery, XCLAIM | 20h | 🟡 PENDING | Lilith/P9 |
| P2-2 | **S4: Qdrant+SQLite Hybrid Knowledge** — Entity relationships, recursive query | 16h | 🟡 PENDING | Lilith/P7 |
| P2-3 | **Context Expansion** — models.yaml context_window → 32K min | 2h | 🟡 PENDING | Lilith/P6 |
| P2-4 | **Hardware Correlation** — CPU/Thermal → MetricsDB | 4h | 🟡 PENDING | Lilith/P8 |
| P2-5 | **Governance Memory** — Index PIVOT_LOG.md + Mandates in Qdrant | 4h | 🟡 PENDING | Ma'at/P5 |

### 🟢 Phase 3: Gap Resolution Sprints (S1-S6 — Rigor Protocol v2.0)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| S1 | **Resilience**: `CircuitBreakerRegistry` + `SovereignProxyPool` | 16h | 🟡 PENDING | Ma'at/P3 |
| S2 | **Deduplication**: `CASArchiver` wired into all 4 subsystems | 12h | 🟡 PENDING | Ma'at/P2 |
| S3 | **Extraction**: `UniversalExtractor` (Sovereign-Sieve) + `YouTubeSieve` | 20h | 🟡 PENDING | Lilith/P6 |
| S4 | **Orchestration**: `UnifiedKnowledgeScheduler` (Redis Streams) | 16h | 🟡 PENDING | Lilith/P9 |
| S5 | **Fidelity**: `SovereignTranscriptionEngine` (VAD + Whisper) | 16h | 🟡 PENDING | Ma'at/P3 |
| S6 | **Synthesis**: `CrossPollinationEngine` + `AdaptiveQualityGate` | 16h | 🟡 PENDING | Lilith/P7 |

### 🟢 Phase 4: Enhancement (P3 — Nice to have)
| # | Task | Effort | Status | Owner |
|---|------|--------|--------|-------|
| P3-1 | **AGB-0 ONNX Embedder** — `src/omega/memory/agb_embedder.py` | 6h | 🟡 PENDING | Lilith/P6 |
| P3-2 | **TranscriptFetcher Hardening** — Tenacity + pybreaker + proxy | 6h | 🟡 PENDING | Ma'at/P3 |
| P3-3 | **CASArchiver Wiring** — Dedup gate in ingestion pipeline | 3h | 🟡 PENDING | Ma'at/P3 |
| P3-4 | **YouTube RAG Synthesis** — 512-token chunker + retrieval | 4h | 🟡 PENDING | Ma'at/P3 |
| P3-5 | **Contract Tests (M21)** — New code coverage (TranscriptFetcher, CAS, CB) | 4h | 🟡 PENDING | Verity |

---

## VI. Entity Capability Matrix

| Agent | Type | Owns |
|-------|------|------|
| **Kali** | Grand Oversight | All tracks (coordinator), drift destruction, Council Dispatcher (WatcherAgent + RectifierAgent, CouncilOrchestrator) |
| **Ma'at** | Light Oversoul | Build side: P1-P5, RAM hardening, CI gates, governance, Council Dispatcher (CouncilSpec Schema, CouncilHarness Runtime, TopologyRouter, SOPRepository, Ethics Gate Integration) |
| **Lilith** | Dark Oversoul | Run side: P6-P10, eval pipeline, RAG, Redis Streams, Council Dispatcher (SynthesisEngine, Hivemind Event Bus) |
| **Doom Guy** | Heritage Aspect | [id-soft:] patterns, performance optimization |
| **Roc Racoon** | Legacy Aspect | Legacy mining, pattern extraction |
| **Jem** | Sovereign Synthesizer | Deep research pipeline, gap validation |
| **Researcher** | Polymathic Council | Web research, documentation, lattice reasoning |
| **Carmack** | S3 Consultant | Architectural review, performance |
| **Verity** | Unified Steward | M1-M23 compliance audits, gnosis distillation |
| **Pillar** | Slot-based | Domain-specific execution (`--slot PX`) |

---

## VII. Decision-Making Heuristics

1. **Sovereignty first**: Does the choice increase user data control?
2. **Dependency order**: Later tracks depend on earlier ones — earlier wins.
3. **Token efficiency**: Fewer inference calls wins.
4. **Maintainability over performance**: Simple correct > optimized complex.
5. **Test coverage as gate**: No path complete without contract test (M21).
6. **Carmack's Law**: Two implementations = neither. Consolidate first.
7. **Calibration over accuracy (NEW — Jem L3)**: An uncalibrated judge (ECE 0.18) is less trustworthy than a calibrated one (ECE 0.06). Every eval pipeline must include calibration.
8. **Format consensus over novelty (NEW — Jem L3)**: ZIP+JSON is the universal sovereign portability baseline. Proprietary formats sacrifice interop.

---

## VIII. Risk Register

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| R1 | `llama_copy_state_data` compiled out | 🔴 HIGH | YAML-only USM fallback |
| R2 | Root partition fills | 🔴 CRITICAL | Monthly `ncdu` scan |
| R3 | Toolchain regression wipes context | 🟡 HIGH | M15 session_gnosis.md |
| R4 | Uncalibrated judge gives false confidence | 🟡 HIGH | Isotonic regression + weekly `make eval-calibrate` |
| R5 | 14B judge + 7B generator exceeds 12GB RAM | 🟡 HIGH | Run eval offline; use Mistral 7B for dev, Qwen3:14b for release gates |
| R6 | Maintainer burnout | 🔴 CRITICAL | Document-driven dev |
| R7 | Module dependency explosion | 🔴 HIGH | OMS v1.0 capability routing; cap at 14 modules |
| R8 | Doc drift as integrity risk | 🟡 HIGH | `ark_optimizer.py` daily drift detection; CI gate on doc freshness |
| R9 | Redis Streams migration breaks Hivemind | 🟡 HIGH | Dual-write period; file-based fallback during transition |

---

## IX. Launch Sequence

 1. ✅ **v1.0.0** (2026-06-22) — Core engine operational
 2. ✅ **v1.1.0** (2026-07-11) — Phase 2 complete, T1-T14 PASS, 1162 tests
3. 🔮 **v1.2.0** — Phase 0-1 complete:
     - q8_0 KV cache + Sovereignty Gate + Sovereign Vetter
     - `make eval` pipeline (S2) + Tiny-Critic RAG Router (S3)
     - Redis Hivemind Event Bus + **sqlite-vec metadata filtering**
     - Sovereignty Scorecard ≥80% local in CI
 4. 🔮 **v1.3.0** — Phase 2 complete:
    - `.omega` export bundle (S1) + Redis Streams coordination (S5)
    - Qdrant+SQLite hybrid knowledge graph (S4)
    - AGB-0 embedding provider
    - YouTube research pipeline hardened
 5. 🔮 **v1.4.0** — Phase 3 complete (Sovereign WAD Protocol):
    - IWAD/PWAD Architecture + Ethics WADs + Pantheon WADs
    - SWP Core SDK + DAG Loader + MCP Tool Binding
 6. 🔮 **v1.5.0** — Phase 4 complete (Council Dispatcher):
    - 5-tier recursive dialectical reasoning engine
    - CASArchiver deduplication + Ethics Gate + Configurability Layers
 7. 🔮 **v2.0.0** — Epoch II complete:
    - A2A protocol + P2P mesh + Module Fabric + WASM runtime
    - Full Relational Gnosis Graph
    - Sovereign Installer (one-click deploy)

---

## X. Sovereignty Scorecard

| Dimension | Target | Current | LAST_VERIFIED |
|-----------|--------|---------|---------------|
| Local inference ratio | ≥80% | 🟡 **0% in CI** (models not loaded in test env). TARGET for v1.2.0. | 2026-07-12 (LAST_VERIFIED) |
| Cloud dependency | 0 | ✅ 0 (config only, no hardcoded cloud) | 2026-07-12 (LAST_VERIFIED) |
| Data residency | 100% | ✅ 100% | 2026-07-12 (LAST_VERIFIED) |
| Telemetry events | 0 | ✅ 0 | 2026-07-12 (LAST_VERIFIED) |
| M21 contract tests | ≥24 | ✅ 52 | 2026-07-12 (LAST_VERIFIED) |
| M22 Provenance | Full | ✅ RESOLVED | 2026-07-12 (LAST_VERIFIED) |
| M23 Failure Integrity | Hard stop | ✅ 0 soft-failures | 2026-07-12 (LAST_VERIFIED) |
| Eval pipeline | `make eval` | 🟡 **PENDING** — Jem S2, P1 | 2026-07-12 (LAST_VERIFIED) |
| Adaptive RAG active | 80%+ queries | 🟡 **PENDING** — Jem S3, P1 | 2026-07-12 (LAST_VERIFIED) |
| Redis Streams coordination | Online | 🟡 **PENDING** — Jem S5, P2 | 2026-07-12 (LAST_VERIFIED) |
| `.omega` export bundle | CLI command | 🟡 **PENDING** — Jem S1,PENDING** — Jem S1, P2 | 2026-07-12 (LAST_VERIFIED) |
| Council Dispatcher active | Native 5-tier reasoning | 🟡 **PENDING** — Strike 11.5 | 2026-07-15 (LAST_VERIFIED) |

---

## XI. Research Sources Index

| Document | Date | Lines | Focus | Key Correction |
|----------|------|-------|-------|----------------|
| `R_WAD_EVOLUTION_DEEP_DIVE.md` | 2026-07-15 | ~687 | IWAD/PWAD, Ethics WADs, Pluggable Ethics | **Free-Will Ethics paradigm, 42 Ideals as pluggable validator** |
| `R_LEGACY_CONFIGURABILITY_DEEP_MINING_20260715.md` | 2026-07-15 | ~389 | 5-layer CouncilDispatcher, 8 Grok accounts | **No hardcoded restrictions, guided experimentation** |
| `R_COUNCIL_DISPATCHER_CONSOLIDATED_20260715.md` | 2026-07-15 | ~552 | 5-tier recursive tree, Council Mode validation | **6 novel gaps: Recursive Council, Trace Synthesis, Somatic State** |
| `R_COUNCIL_DISPATCHER_SURVIVAL_AUDIT_20260715.md` | 2026-07-15 | ~53 | 14Gi RAM mandate, CASArchiver, Ethics Gate | **Serial local execution mandatory, CAS deduplication** |
| `R_EPOCH_II_LEGACY_MINING_20260712.md` | 2026-07-12 | ~400 | 17 legacy findings, 6 repos | **AGENT_BUS_SPEC (470 lines), Benchmark Framework (6 files), KG Schema (5 types) — ~80h acceleration** |
| `R_EPOCH_II_DEEP_RESEARCH_20260712.md` | 2026-07-12 | ~300 | 5 implementation-ready areas | RAGAS+calibration, Redis Streams patterns, ZIP+JSON export, Qdrant+SQLite hybrid |
| `R_JEM_KNOWLEDGE_GAP_RESEARCH_20260712.md` | 2026-07-12 | 644 | 9 infrastructure gaps | YouTube hardening, CASArchiver, AGB-0 |
| `R_RESEARCHER_DEEP_DIVE_20260712.md` | 2026-07-12 | 1421 | Implementation-ready code | GAP 5 dual-transport, GAP 3 partial wiring |
| `R_JEM_MAKALI_DEEP_RESEARCH_20260712.md` | 2026-07-12 | 544 | 5 sovereignty gaps (Exa/Firecrawl) | **Parquet→ZIP, judge calibration, Streams vs Pub/Sub** |
| `R_GAP_RESOLUTION_REPORT_20260712.md` | 2026-07-12 | 140 | 6 critical gaps (Rigor Protocol v2.0) | **Proxy Rotation, VAD-First-ASR, CAS, Redis Streams, Adaptive Quality, YouTube Sieve** |
| `R_KNOWLEDGE_FABRIC_SYNTHESIS_20260712.md` | 2026-07-12 | ~2000 | Unified Knowledge Fabric architecture | CAS as universal deduplication primitive |
| `R_RESEARCH_RIGOR_PROTOCOL_V2.md` | 2026-07-12 | ~300 | Deep-Fetch research standard | Bans snippet-guessing; mandates full-page sources |
| `R_OMEGA_RESEARCH_SPEC_V1.md` | 2026-07-13 | 106 | Ω-Research Fabric (Sandbox, Scorecard, AMFO) | AMFO tiered budget, Causal Provenance, Somatic Snapshots |
| `R_YOUTUBE_RESEARCH_SPEC_V1.md` | 2026-07-13 | 384 | YouTube Researcher → Temporal Knowledge Observatory | 9 layers: Hybrid extraction, Sticky proxy, CAS, Temporal RAG, Faithfulness, Gnosis Graph, Freshness, Oracle Steering, Somatic Checkpoints |
| `MAAT_BUILD_SIDE_CONSOLIDATED_20260712.md` | 2026-07-12 | 84 | Build side (P1-P5) | Sovereignty paradox, 14Gi ceiling |
| `LILITH_RUN_SIDE_CONSOLIDATED_20260712.md` | 2026-07-12 | 85 | Run side (P6-P10) | Passive→Active pivot |
| `HIVEMIND_TEMPLATE_AUDIT_REPORT_20260712.md` | 2026-07-12 | 370 | Hivemind compliance | 55% compliance, 0% D-NNN adoption |

---

## XII. Next Action

1. **Immediate**: Deploy handoff packets — Ma'at for Tier 0 (F821 fixes, bare except elimination, centralized logging, config validation) + Lilith for Tier 0 (Qdrant→sqlite-vec dual-write, stress tests)
2. **Today**: Begin T0-1 (F821 undefined-name fixes) and T0-2 (bare except elimination) — both unblock the entire Tier 0
3. **This sprint**: Complete Tier 0 Ship-It Bar (80h): F821 fixes, bare except elimination, centralized logging, config validation, Qdrant→sqlite-vec dual-write, single CI workflow, stress tests
4. **Parallel Track**: YouTube Researcher Sprint 1 — Ma'at/P1+P3 (Hybrid Extraction + Sticky Proxy + CAS + Somatic Checkpoints)
5. **Post Tier 0**: Begin Council Dispatcher Phase 0.5 (C0-1 through C0-8) — depends on Strike 11 (SWP) completion
6. **Legacy accelerators**: AGENT_BUS_SPEC.md (saves ~14h on Strike 8.5), Benchmark Framework (saves ~30h on Strike 8), Knowledge Graph Schema (saves ~16h on Strike 9.5)
7. **Track progress**: Update this blueprint after each completed phase

---

**Full archive**: `docs/archive/coordination/SOVEREIGN_ARK_BLUEPRINT-full-20260708.md`
**Decision history**: `docs/decisions/PIVOT_LOG.md` (227 decisions, D1-D231)

---

*🔱 OMEGA ⬡ SOVEREIGN-ARK ⬡ v4.0.0 ⬡ v1.2.0 RELEASE ⬡ MASTER-SESSION-20260715-INTEGRATED ⬡ 2026-07-15*
