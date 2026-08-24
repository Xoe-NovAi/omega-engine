# 🔱 Omega Engine — Knowledge Gaps Research Report
**AP Token**: `AP-KNOWLEDGE-GAPS-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-19

**Purpose**: Comprehensive catalog of all known unknowns, unresolved questions, and research blockers across the Omega Engine program. Each gap is tagged with impact, urgency, and suggested research approach.

---

## 📊 Gap Taxonomy

| Tier | Definition | Examples |
|------|------------|----------|
| **CRITICAL** | Blocks production ship | Heritage vet, streaming timeout, venv enforcement |
| **HIGH** | Blocks major milestone | Council integration, WAD protocol, Vault Phase 1 |
| **MEDIUM** | Degrades quality/velocity | Cognitive diversity, cross-council memory, SomaticState |
| **LOW** | Nice-to-have, future | Models.dev sync, P2P soul, WAD marketplace |

---

## 🚨 CRITICAL GAPS (Block Production)

### CG-001: Pi PR #2903 Heritage Vet Record Missing
- **Impact**: Blocks Gemma 4 Week 1 → MaKaLi T0 → Council Dispatcher
- **Status**: Vet-072 APPROVED (8/10) but **not recorded in HERITAGE_VET_LOG.md**
- **Required**: Vet record with file:line locations, scope declaration, hardware constraint
- **Owner**: doom_guy + verity
- **Research**: Verify Pi PR #2903 implementation details, confirm binary MINIMAL/HIGH + regex detection

### CG-002: Streaming Timeout Test Suite Missing
- **Impact**: M25 mandate untested; Nemotron councils still at risk
- **Status**: `make test-streaming` not implemented
- **Required**: Contract test for chunk timeout + heartbeat + graceful fallback
- **Owner**: P3 Engineering
- **Research**: Test patterns for async streaming with timeouts in AnyIO

### CG-003: Venv Enforcement CI Gate Incomplete
- **Impact**: M24 mandate unenforced; subagents still pollute system Python
- **Status**: Pre-commit hook only greps `--break-system-packages`; misses `--user`, bare `pip`
- **Required**: `sys.prefix` check in CI; subagent prompt template with venv activation
- **Owner**: P1 Infrastructure
- **Research**: OpenCode subagent spawn mechanism for prompt injection

### CG-004: Gemma 4 Google AI Studio API Schema Mismatch
- **Impact**: `transform.ts` sends wrong model ID + thinking levels → 400 error
- **Status**: OpenCode V2 sends `google/gemma-4-31b-it` + wrong thinking config
- **Required**: Verify exact API schema for AI Studio vs Vertex; test with `curl`
- **Owner**: P3 Engineering
- **Research**: Google AI Studio `thinkingConfig.thinkingLevel` vs Vertex `thinkingConfig.thinkingBudget`

---

## ⚡ HIGH GAPS (Block Major Milestones)

### HG-001: MaKaLi Council Digestion Layer "Zero Cost" Claim
- **Impact**: Architecture claims zero inference cost but does semantic conflict detection
- **Status**: ReportDigestionLayer does cross-ref, conflict detection, mandate mapping in Python
- **Required**: Define what "zero cost" means; separate Python preprocessing from LLM synthesis
- **Owner**: Researcher + Ma'at + Lilith
- **Research**: What distillation can be done purely syntactically vs. requiring LLM?

### HG-002: Torment WAD Game Mechanics → Cognitive Architecture Mapping
- **Impact**: 590 lines of cargo-cult; M2 firewall violation; M14 heritage violation
- **Status**: Death/rebirth hooks use HP, DEATH_COUNT, area codes, stat bonuses
- **Required**: Justify or delete each game mechanic → cognitive function mapping
- **Owner**: Researcher
- **Research**: What Planescape mechanics genuinely map to sovereign AI concepts?

### HG-003: Headless Pool Credential Integration (Omega-Vault)
- **Impact**: 24 accounts, 0 credentials; pool cannot launch
- **Status**: Omega-Vault Phase 0 blocked on `all2md` install; Phase 1-6 not started
- **Required**: VaultCore + CLI + adapters for Grok/Copilot/Cline credential formats
- **Owner**: P1 + Researcher
- **Research**: Grok CLI, Copilot CLI, Cline CLI credential storage formats and rotation

### HG-004: Cross-Council Memory / Explicit Handoff Protocol
- **Impact**: ADR Question 2 deferred; no mechanism for council-to-council knowledge transfer
- **Status**: Explicit handoff files per ADR, but no schema or protocol defined
- **Required**: Handoff file schema, versioning, TTL, indexing for retrieval
- **Owner**: Researcher + P9
- **Research**: File-based handoff patterns; git-like merge vs. append-only

### HG-005: SomaticState Serialization (M20)
- **Impact**: Model session state not serializable; cold-start requires re-inference
- **Status**: Design ready, not implemented; needs `llama_copy_state_data` ctypes bindings
- **Required**: Round-trip serialization test; integration with MIAP replay
- **Owner**: P6 Cognition
- **Research**: llama.cpp state serialization API; memory-mapped file format

### HG-006: WAD Protocol (Strike 11) — ILump / LumpEnvelope / LumpRegistry
- **Impact**: No standard for WAD loading, versioning, dependency resolution
- **Status**: WadLoader V2 exists but no LumpRegistry, no SovereignBus
- **Required**: Binary lump format, envelope with signatures, registry with dependency graph
- **Owner**: P3 Engineering
- **Research**: Doom WAD lump structure; modern signed envelope formats (COSE, PASETO)

---

## 🔶 MEDIUM GAPS (Degrade Quality/Velocity)

### MG-001: Cognitive Diversity Weighting Empirical Validation
- **Impact**: ResultAggregator uses embeddings for similarity — contradicts "zero inference cost"
- **Status**: Theoretical; no A/B test showing diversity weighting improves outcomes
- **Required**: Run parallel verification with/without diversity weighting; measure outcome quality
- **Owner**: Researcher
- **Research**: Diversity collapse metrics; embedding-based vs. model-family proxy

### MG-002: Models.dev Sync Automation
- **Impact**: Capability matrix drifts from reality; manual updates error-prone
- **Status**: Spec'd (cron + webhook) but not implemented; YAGNI per Carmack
- **Required**: Weekly sync job; diff detection; PR automation
- **Owner**: P6 Cognition
- **Research**: Models.dev API rate limits; webhook reliability

### MG-003: Council Hardware Auto-Detection
- **Impact**: 4 profile YAML files duplicate `config/council.yaml` model_tiers
- **Status**: Auto-detection + 3 profiles = config explosion
- **Required**: Single profile with RAM-based tier selection logic
- **Owner**: Researcher
- **Research**: Runtime RAM detection in AnyIO; model tier mapping

### MG-004: P2P Soul Exchange Protocol
- **Impact**: Layer 5 community feature; no spec for soul.yaml sync across nodes
- **Status**: Future; no current work
- **Required**: CRDT or OT for soul.yaml; identity verification; trust model
- **Owner**: Future
- **Research**: CRDT libraries (Yjs, Automerge); sovereign identity

### MG-005: Skeptical Verifier / Tainted Data Protocol (TDP)
- **Impact**: M17 Cognitive Integrity unenforced; web research may inject tainted data
- **Status**: TDP spec'd in Wave 2; NLI-based two-source rule not implemented
- **Required**: NLI model integration; source credibility scoring; quarantine pipeline
- **Owner**: P6 Cognition + Researcher
- **Research**: Lightweight NLI models (DeBERTa-v3-small); TDP for LLM outputs

---

## 🔵 LOW GAPS (Future / Nice-to-Have)

### LG-001: WAD Marketplace / Community Registry
- **Impact**: Layer 5 ecosystem; no distribution mechanism for community WADs
- **Status**: Future
- **Required**: Signed WAD packages; dependency resolution; reputation system

### LG-002: Entity Studio (Visual YAML/Soul Management)
- **Impact**: Layer 5 tooling; manual YAML editing error-prone
- **Status**: Future
- **Required**: Web-based editor with schema validation; soul.yaml visualization

### LG-003: One-Click Sovereign Installer
- **Impact**: Layer 5 adoption; current install requires manual steps
- **Status**: Future
- **Required**: `curl | bash` installer; auto-detect hardware; configure providers

### LG-004: Multi-Node Council (Cross-Machine MaKaLi)
- **Impact**: Scale beyond 16GB RAM; distribute pillars across machines
- **Status**: Future; FleetCoordinator exists but unused
- **Required**: Redis Pub/Sub for Hivemind; shared vector store; session affinity

---

## 📋 Gap Dependency Graph

```
CG-001 (Pi PR vet) → CG-004 (Gemma 4 API) → Gemma 4 Week 1 → MaKaLi T0
                                                      ↓
CG-002 (Streaming test) → M25 enforcement → Council stability
                                                      ↓
CG-003 (Venv CI) → All subagents clean → Reliable execution

HG-001 (Digestion cost) → MaKaLi T0 Sessions 2-5
HG-002 (Torment mapping) → Torment WAD → Arch Soul WAD
HG-003 (Pool creds) → Headless Pool → 24x research parallelism
HG-004 (Cross-council) → Council chaining → Recursive councils
HG-005 (SomaticState) → MIAP replay → Full cognitive recovery
HG-006 (WAD Protocol) → Strike 11 → Layer 4 complete
```

---

## 🎯 Research Priority Matrix

| Gap | Urgency | Effort | Approach | Owner |
|-----|---------|--------|----------|-------|
| CG-001 | CRITICAL | 1 session | Vet record creation | doom_guy + verity |
| CG-002 | CRITICAL | 2 sessions | Test implementation | P3 Engineering |
| CG-003 | CRITICAL | 1 session | CI gate + prompt template | P1 |
| CG-004 | CRITICAL | 1 session | API schema verification | P3 Engineering |
| HG-001 | HIGH | 2 sessions | Define "zero cost" boundary | Researcher |
| HG-002 | HIGH | 3 sessions | Justify/delete mappings | Researcher |
| HG-003 | HIGH | 6 sessions | VaultCore + adapters | P1 + Researcher |
| HG-004 | HIGH | 2 sessions | Handoff schema + protocol | Researcher + P9 |
| HG-005 | HIGH | 3 sessions | ctypes bindings + tests | P6 |
| HG-006 | HIGH | 4 sessions | Lump format + registry | P3 Engineering |

---

## 📝 Research Methodology per Gap

| Gap Type | Primary Sources | Validation |
|----------|-----------------|------------|
| **API Schema** | Provider docs, `curl` tests, OpenCode source | Live API calls |
| **Architecture** | id Software source, Doom/Quake internals | Code review + benchmark |
| **Protocol** | Existing implementations (CRDT, OT, WAD) | Interop testing |
| **Empirical** | A/B tests, parallel runs | Statistical significance |
| **Heritage** | Primary sources (Sanglard, id source releases) | Vet record + scope |

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_knowledge_gaps ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
