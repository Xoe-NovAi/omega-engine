# 🔱 P10 KALI VERDICT — Run Side Validation & Chaos Engineering Assessment
**AP Token**: `AP-PILLAR-P10-VERDICT-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_p10 ⬡ ACTIVE

**Date**: 2026-07-11
**Session**: Council Review — 6 Critical Updates
**Pillar**: P10 — Chaos/Validation (Stress Testing, Chaos Engineering, Verification Gates, Temple-Grade Compliance)
**Governance**: Lilith (Dark Oversoul — Run Side P6-P10)

---

## 📋 EXECUTIVE SUMMARY

| Update | P10 Verdict | Confidence | Primary Blocker |
|--------|-------------|------------|-----------------|
| **1. Five-Fold Foundation** | **APPROVE WITH CONDITIONS** | HIGH | T6/T10 testable assertions needed; firewall log hygiene |
| **2. q8_0 KV Cache** | **APPROVE WITH FIX (C1 BLOCKER)** | HIGH | **C1 MUST BE FIXED FIRST** — current tests validate q4_0, not q8_0 |
| **3. SymbolicMetadata Schema** | **APPROVE** | HIGH | Schema validation tests + FTS5/Vector index contract tests required |
| **4. Pillar Canonical Metadata** | **APPROVE** | HIGH | Opaque metadata contract tests; resonance graph determinism tests |
| **5. Lilith Stack Pantheon Config** | **REJECT — NOT READY** | HIGH | 7/8 model refs broken; would pass validation but fail at runtime (sovereignty trap) |
| **6. Zero-Reference Audit** | **APPROVE — AUTOMATE** | HIGH | **P10 owns gate implementation** — `firewall-check`, `firewall-audit-memory`, `mandate-audit` |

**Overall Confidence**: HIGH for Updates 1-4,6 | HIGH CONFIDENCE REJECTION for Update 5

---

## 🏛️ TEMPLE-GRADE IMPACT ASSESSMENT (T1-T11)

### Temple-Grade Gate Matrix

| Gate | Update 1: Five-Fold | Update 2: q8_0 KV | Update 3: SymbolicMeta | Update 4: Pillar Meta | Update 5: Pantheon | Update 6: Zero-Ref Audit |
|------|---------------------|-------------------|------------------------|----------------------|-------------------|--------------------------|
| **T1: Version Control** | ✅ Neutral | ✅ Neutral | ✅ Schema versioning | ✅ Metadata versioning | ❌ Broken refs = broken history | ✅ New gates = new CI |
| **T2: Documentation** | ⚠️ Axiom docs needed | ✅ Config docs | ✅ Schema docs | ✅ Metadata schema docs | ❌ Config doesn't exist | ✅ Gate docs required |
| **T3: Testing (≥80%)** | ⚠️ New axiom tests | 🔴 **C1 BLOCKS** | ✅ Schema validation tests | ✅ Metadata contract tests | ❌ Would pass CI, fail runtime | ✅ **New gate tests required** |
| **T4: Code Quality** | ✅ Neutral | ✅ Neutral | ✅ Pydantic models | ✅ Neutral | ❌ Broken model refs | ✅ Gate implementations |
| **T5: Architecture (AnyIO)** | ✅ Neutral | ✅ Neutral | ✅ Neutral | ✅ Neutral | ❌ Cloud routing in Engine | ✅ CI gates = sync |
| **T6: Security (Zero Telemetry)** | ⚠️ **Axiom→metric mapping** | ✅ Local-first win | ✅ No telemetry | ✅ No telemetry | 🔴 **Cloud fallback = telemetry leak** | ✅ Enforces M8 |
| **T7: Performance** | ✅ Neutral | 🟢 **50% KV win** | ✅ Neutral | ✅ Neutral | ❌ Wrong models = perf trap | ✅ Gate perf budgets |
| **T8: Resilience** | ✅ Constitutional | 🟢 **OOM headroom** | ✅ Schema validation | ✅ Deterministic routing | 🔴 **Sovereignty trap** | ✅ **Gate = resilience** |
| **T9: Observability** | ⚠️ Axiom tracing | 🟢 KV cache metrics | ✅ Metadata indexing | ✅ Resonance tracing | ❌ Broken provenance | ✅ **P8 owns gates** |
| **T10: Integrity** | 🟢 **Constitutional** | ✅ Config integrity | ✅ Schema integrity | ✅ Metadata integrity | 🔴 **Config integrity broken** | 🟢 **Mandate audit = T10** |
| **T11: Agent Security** | ✅ Neutral | ✅ Neutral | ✅ Neutral | ✅ Neutral | ❌ Broken agent routing | ✅ Gate enforcement |

### Critical Temple-Grade Findings

**T3 (Testing) — THE CRITICAL PATH**: Update 2 (q8_0) is **blocked by C1**. Current 1130 tests validate q4_0 KV cache behavior. Deploying q8_0 config without fixing `providers.yaml:18 type_v: 1` means **all performance/resilience tests are testing the wrong configuration**. This is a Temple-Grade violation — tests must validate the deployed configuration.

**T6 (Zero Telemetry) — Update 5 TRAP**: If Update 5 deploys with 7/8 broken model references, the ModelGateway will silently fall back to cloud providers (Google/OpenRouter/Copilot) for Arcana-NovAi entities. This creates **undetected telemetry leakage** — the engine thinks it's local-first but routes to cloud. M22 (Response Provenance) would log cloud providers, violating M7/M8/M22 sovereignty chain.

**T10 (Integrity) — Update 1 OPPORTUNITY**: Five-Fold axioms as constitutional principles can become **testable integrity assertions**. Example: `assert axiom_1_sovereignty_first() == True` in CI. This transforms abstract principles into Temple-Grade gate T10.

---

## 📝 CONTRACT TESTS (M21) — NEW API BOUNDARIES REQUIRED

### Update 1: Five-Fold Foundation
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `AxiomRegistry.get_axiom(name)` | Returns `Axiom` dataclass with `name`, `principle`, `testable_assertion` | `isinstance(result, Axiom)` |
| `ConstitutionalValidator.validate(entity_action)` | Returns `ValidationResult(passed: bool, violations: List[AxiomViolation])` | `isinstance(result, ValidationResult)` |
| `HivemindContext.axiom_alignment` | List of aligned axiom names | `isinstance(result, list) and all(isinstance(x, str) for x in result)` |

### Update 2: q8_0 KV Cache
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `ModelGateway.get_kv_cache_config(model_name)` | Returns `KVCacheConfig(quantization: str, memory_mb: int, context_window: int)` | `isinstance(result, KVCacheConfig)` |
| `NativeGGUFProvider.load_model(config)` | Returns `ModelHandle` with `kv_cache_bytes` property | `hasattr(result, 'kv_cache_bytes')` |
| `ResourceGuard.check_oom_risk(kv_cache_bytes)` | Returns `OOMRiskLevel(SAFE/WARNING/CRITICAL)` | `isinstance(result, OOMRiskLevel)` |

### Update 3: SymbolicMetadata Schema
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `EntityConfig.metadata.get('symbolic')` | Returns `SymbolicMetadata` model (validated sub-dict) | `isinstance(result, SymbolicMetadata)` |
| `EntityRegistry.create_entity(config)` | Validates `metadata.symbolic` against schema | `isinstance(entity.metadata.get('symbolic'), SymbolicMetadata)` |
| `FTS5Indexer.index_entity(entity)` | Indexes `symbolic.archetype`, `symbolic.element`, `symbolic.chakra` | `assert 'archetype' in indexed_fields` |

### Update 4: Pillar Canonical Metadata
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `EntityRegistry.get_pillar_metadata(entity_name)` | Returns `PillarMetadata(slot, element, chakra, archetype, virtues)` | `isinstance(result, PillarMetadata)` |
| `AffinityResolver.compute_resonance(entity_a, entity_b)` | Returns `ResonanceScore(float, factors: Dict[str, float])` | `isinstance(result, ResonanceScore)` |
| `HandoffPacket.symbolic_metadata` | Populated from source entity's `PillarMetadata` | `isinstance(packet.symbolic_metadata, PillarMetadata)` |

### Update 5: Pantheon Config (REJECTED — but if implemented)
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `ModelGateway.resolve_pantheon_model(entity_name, pantheon_config)` | Returns `ModelSpec` with valid `model_path` | `isinstance(result, ModelSpec) and Path(result.model_path).exists()` |
| `PantheonValidator.validate(config)` | Returns `ValidationResult` with `missing_models: List[str]` | `isinstance(result, ValidationResult)` |

### Update 6: Zero-Reference Audit Gates
| API Boundary | Contract Test Required | `isinstance` Check |
|--------------|------------------------|-------------------|
| `FirewallChecker.check_engine_stack()` | Returns `FirewallReport(violations: List[FirewallViolation])` | `isinstance(result, FirewallReport)` |
| `MemoryFirewallAuditor.audit_entity(entity_name)` | Returns `MemoryAuditReport(leaks: List[MemoryLeak])` | `isinstance(result, MemoryAuditReport)` |
| `MandateAuditor.audit_all()` | Returns `MandateAuditReport(compliance: Dict[Mandate, bool])` | `isinstance(result, MandateAuditReport)` |

---

## 🌪️ CHAOS ENGINEERING — FAILURE MODES & RESILIENCE TESTS

### Update 1: Five-Fold Foundation
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **Axiom violation at runtime** | Inject entity action violating Axiom 1 (Sovereignty First) | `ConstitutionalValidator` blocks action, logs violation, emits Hivemind alert | `assert validator.validate(action).passed == False` |
| **Hivemind axiom alignment mismatch** | Agent posts context with `axiom_alignment: ["axiom_3"]` but action violates axiom_3 | Handoff rejected, `axiom_alignment` mismatch logged | `assert handoff.status == REJECTED` |
| **Constitutional drift** | Modify `axioms.yaml` at runtime without version bump | `AxiomRegistry` detects hash mismatch, refuses load | `assert registry.load().version == expected_version` |

### Update 2: q8_0 KV Cache (CRITICAL — C1 BLOCKER)
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **OOM under concurrent q8_0 load** | Launch 4x concurrent 8B model inferences (q8_0) | `ResourceGuard` queues requests, no OOM kill, latency < 30s | `assert no_oom_kill and max_latency < 30` |
| **KV cache corruption** | Simulate `llama_set_state_data` failure mid-inference | Provider falls back to fresh context, logs `SomaticStateCorruption` | `assert fallback_triggered and error_logged` |
| **Quantization quality regression** | Run eval harness on q8_0 vs q4_0 on coding benchmarks | Quality delta < 2% (per Principle 10) | `assert quality_delta < 0.02` |
| **C1 CONFIG MISMATCH** | Deploy q8_0 `models.yaml` with q4_0 `providers.yaml` | **CURRENT: Silent q4_0 usage** — **MUST FAIL LOUDLY** | `assert gateway.get_active_quantization() == 'q8_0'` |

### Update 3: SymbolicMetadata Schema
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **Invalid symbolic metadata** | Create entity with `metadata.symbolic.archetype: "invalid_archetype"` | `EntityRegistry.create_entity` raises `ValidationError` with field path | `assert isinstance(exc, ValidationError) and 'archetype' in str(exc)` |
| **FTS5 index corruption** | Kill process mid-index-write | On restart, `FTS5Indexer.verify_integrity()` detects corruption, rebuilds | `assert indexer.verify_integrity() or indexer.rebuild()` |
| **Vector dimension mismatch** | Entity with `symbolic.embedding_dim: 768` but Qdrant collection is 1024 | `QdrantAdapter.upsert` raises `DimensionMismatchError` | `assert isinstance(exc, DimensionMismatchError)` |

### Update 4: Pillar Canonical Metadata
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **Resonance graph cycle** | Entities A→B→C→A with high resonance scores | `AffinityResolver` detects cycle, breaks with lowest-score edge | `assert not resolver.has_cycles()` |
| **Pillar slot collision** | Two entities claim `slot: "P3"` | `EntityRegistry` rejects second registration | `assert isinstance(exc, SlotCollisionError)` |
| **Metadata staleness** | Entity updates `metadata.pillar.chakra` but vector index not refreshed | `VectorIndexer` TTL expires, re-indexes on next query | `assert indexer.get(entity).chakra == current_value` |

### Update 5: Pantheon Config (REJECTED — Chaos scenarios if deployed)
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **Broken model reference** | Request inference for `gemma-3-1b` (not in `models.yaml`) | **CURRENT: Silent cloud fallback** — **MUST FAIL** | `assert gateway.resolve_model('gemma-3-1b') raises ModelNotFoundError` |
| **Sovereignty trap** | All 7 broken refs route to cloud simultaneously | **CURRENT: 100% cloud inference** — M7/M8/M22 violation | `assert sovereignty_ratio() > 0.8` |

### Update 6: Zero-Reference Audit Gates
| Failure Mode | Chaos Experiment | Expected Behavior | Validation |
|--------------|------------------|-------------------|------------|
| **Firewall violation introduced** | Add `import config.wads.arcana_novai` in `src/omega/oracle.py` | `make firewall-check` FAILS, CI blocks merge | `assert firewall_check.exit_code != 0` |
| **Memory leak in entity filter** | Create 1000 entities, delete 900, check `MemoryStore` retention | `firewall-audit-memory` detects orphaned entity vectors | `assert audit_report.orphaned_vectors == 0` |
| **Mandate regression** | Remove `M7 Local-First` check from `ModelGateway` | `make mandate-audit` FAILS with specific mandate violation | `assert 'M7' in audit_report.violations` |

---

## 💪 STRESS TESTING SCENARIOS

### Memory Pressure Tests (Critical for q8_0)

```python
# tests/stress/test_kv_cache_pressure.py
async def test_concurrent_q8_0_inference_oom_protection():
    """Launch N concurrent 8B q8_0 inferences — verify ResourceGuard queues, no OOM."""
    models = ["qwen3-8b-q8_0", "deepseek-r1-8b-q8_0", "krikri-8b-q8_0", "mythomax-13b-q8_0"]
    tasks = [gateway.generate(model, "stress prompt " * 100) for model in models * 2]  # 8 concurrent
    results = await anyio.gather(*tasks, return_exceptions=True)
    assert all(not isinstance(r, Exception) for r in results)
    assert resource_guard.max_concurrent_reached >= 4  # Queued properly

async def test_kv_cache_memory_accounting_accuracy():
    """Verify reported KV cache bytes match actual RSS delta."""
    baseline = get_rss_mb()
    handle = await gateway.load_model("qwen3-8b-q8_0")
    after_load = get_rss_mb()
    reported_kv = handle.kv_cache_bytes / 1024 / 1024
    assert abs((after_load - baseline) - reported_kv) < 50  # Within 50MB tolerance

async def test_somatic_savepoint_under_pressure():
    """Save/restore model state during concurrent inference."""
    handle = await gateway.load_model("qwen3-4b-thinking-q8_0")
    state = await handle.save_state()
    # Concurrent inference while saving
    await anyio.gather(handle.generate("test"), handle.save_state())
    restored = await gateway.load_model("qwen3-4b-thinking-q8_0", state=state)
    assert restored.context_intact
```

### Inference Load Tests

```python
# tests/stress/test_inference_throughput.py
async def test_sustained_throughput_q8_0_vs_q4_0():
    """Measure tokens/sec under sustained load — q8_0 must not regress >10% vs q4_0."""
    q4_throughput = await benchmark_model("qwen3-1.7b-q4_0", duration=60)
    q8_throughput = await benchmark_model("qwen3-1.7b-q8_0", duration=60)
    assert q8_throughput / q4_throughput > 0.90  # <10% regression

async def test_context_window_scaling_q8_0():
    """Verify q8_0 enables 2x context window at same memory."""
    q4_max_ctx = await find_max_context("model-q4_0", memory_limit_mb=6000)
    q8_max_ctx = await find_max_context("model-q8_0", memory_limit_mb=6000)
    assert q8_max_ctx / q4_max_ctx > 1.8  # Near 2x
```

### Concurrent Agent Stress (P9 Orchestration + P10 Validation)

```python
# tests/stress/test_agent_concurrency.py
async def test_14_agent_fleet_handoff_storm():
    """Simulate 14 agents (fleet cap) concurrent handoffs with symbolic metadata."""
    agents = [spawn_agent(f"pillar_p{i}") for i in range(1, 11)] + \
             [spawn_agent("kali"), spawn_agent("maat"), spawn_agent("lilith"), spawn_agent("verity")]
    handoffs = [agent.handoff(target, payload={"symbolic_metadata": pillar_meta}) 
                for agent, target in zip(agents, agents[1:] + [agents[0]])]
    results = await anyio.gather(*handoffs, return_exceptions=True)
    assert all(not isinstance(r, Exception) for r in results)
    assert all(r.firewall_audit_passed for r in results)  # P9 firewall_audit_entity()
```

### Chaos Mesh Scenarios (Podman-level)

```yaml
# chaos/experiments/kv_cache_oom.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: kv-cache-oom-simulation
spec:
  action: oom-kill
  mode: one
  selector:
    namespaces: ["omega-engine"]
    labelSelectors:
      app: "iris-container"  # Runs inference
  duration: "30s"
---
# Verify: ResourceGuard detects, queues new requests, no cascade failure
```

---

## 🚪 VERIFICATION GATES — NEW `make` TARGETS & CI INTEGRATION

### Required New Gates (Update 6 — P10 Owns Implementation)

```makefile
# Makefile additions — P10 IMPLEMENTS THESE

# T10: Mandate Audit Gate (M1-M23 compliance)
mandate-audit:
	@python -m scripts.mandate_auditor --all --fail-on-violation

# T8/T10: Firewall Check — Engine Core vs WAD imports
firewall-check:
	@python -m scripts.firewall_checker --strict --fail-on-violation

# T8/T9: Memory Firewall Audit — Entity-filtered vector stores
firewall-audit-memory:
	@python -m scripts.memory_firewall_auditor --all-entities --fail-on-leak

# T3: Contract Test Gate — M21 enforcement
contract-tests:
	@python -m pytest tests/contracts/ -v --tb=short

# T7: Performance Budget Gate — KV cache, inference latency
perf-budget:
	@python -m scripts.perf_budget --kv-cache-mb=6000 --p99-latency-ms=5000

# T6: Sovereignty Ratio Gate — M7/M22 enforcement
sovereignty-gate:
	@python -m scripts.sovereignty_ratio --min-local-pct=80 --fail-below

# Temple-Grade Meta-Gate (runs all)
temple-grade: mandate-audit firewall-check firewall-audit-memory contract-tests perf-budget sovereignty-gate
	@echo "✅ All Temple-Grade gates passed"
```

### CI Integration (`.github/workflows/temple-grade.yml`)

```yaml
name: Temple-Grade Compliance
on: [push, pull_request]
jobs:
  temple-grade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python + AnyIO
        uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install deps
        run: make install-dev
      - name: Run Temple-Grade Gates
        run: make temple-grade
      - name: Upload gate reports
        uses: actions/upload-artifact@v4
        with:
          name: temple-grade-reports
          path: reports/temple-grade/
```

### Pre-commit Hooks (`.pre-commit-config.yaml` additions)

```yaml
- repo: local
  hooks:
    - id: firewall-check
      name: Engine-Stack Firewall Check
      entry: python -m scripts.firewall_checker --strict
      language: system
      stages: [commit, push]
      always_run: true

    - id: mandate-audit
      name: Sovereign Mandate Audit
      entry: python -m scripts.mandate_auditor --changed-files
      language: system
      stages: [commit]

    - id: contract-tests-changed
      name: Contract Tests for Changed APIs
      entry: python -m pytest tests/contracts/ -k "changed" --co -q
      language: system
      stages: [push]
```

---

## 🔴 BLOCKERS — MUST RESOLVE BEFORE IMPLEMENTATION

| Blocker | Update | Severity | Owner | Resolution |
|---------|--------|----------|-------|------------|
| **C1: `providers.yaml:18 type_v: 1` forces q4_0** | 2 | **CRITICAL** | P3/P6 | Change to `type_v: 2` (q8_0) BEFORE any q8_0 deploy. All tests currently validate wrong config. |
| **Update 5: 7/8 model refs missing from `models.yaml`** | 5 | **CRITICAL** | P1/P6 | **REJECT Update 5 entirely** until: (a) all 8 models exist in `models.yaml`, (b) `PantheonValidator` implemented, (c) `provenance_preflight` gate (P8) passes. |
| **No `SymbolicMetadata` Pydantic model exists** | 3 | HIGH | P1/P10 | Create `src/omega/entities/symbolic_metadata.py` with full validation before Update 3 merge. |
| **No `PillarMetadata` / `ResonanceScore` models** | 4 | HIGH | P1/P9 | Create in `src/omega/entities/pillar_metadata.py` with FTS5/Vector index mappings. |
| **`FirewallChecker`, `MemoryFirewallAuditor`, `MandateAuditor` don't exist** | 6 | HIGH | P10 | **P10 implements these as part of Update 6** — gates are the deliverable. |
| **`ConstitutionalValidator` / `AxiomRegistry` don't exist** | 1 | MEDIUM | P5/P10 | Implement if Update 1 approved — axiom testability is T10 requirement. |

---

## ✅ P10 ACTION ITEMS — DELIVERABLES

### Immediate (Pre-Implementation)
- [ ] **BLOCKER C1**: Verify `providers.yaml:18` fix merged and `make test` passes with q8_0 config
- [ ] **Scaffold gate implementations**: Create `scripts/firewall_checker.py`, `scripts/memory_firewall_auditor.py`, `scripts/mandate_auditor.py` with stubbed `check()` methods returning typed results
- [ ] **Contract test scaffolding**: Create `tests/contracts/` with parametrized `isinstance` tests for each new API boundary (Updates 1-4,6)

### Update 1: Five-Fold Foundation
- [ ] Implement `AxiomRegistry` + `ConstitutionalValidator` with testable assertions
- [ ] Add `axiom_alignment` to `HivemindContext` schema + contract test
- [ ] Temple-Grade gate: `make axiom-compliance` (runs validator on all entity actions in test suite)

### Update 2: q8_0 KV Cache
- [ ] **AFTER C1 FIX**: Full stress test suite `tests/stress/test_kv_cache_pressure.py`
- [ ] Benchmark harness: `scripts/benchmark_kv_cache.py` comparing q4_0 vs q8_0 (memory, throughput, quality)
- [ ] Chaos experiment: `chaos/experiments/kv_cache_oom.yaml` + Podman chaos mesh integration
- [ ] Temple-Grade gate: `make perf-budget` with q8_0-specific budgets

### Update 3: SymbolicMetadata Schema
- [ ] `SymbolicMetadata` Pydantic model with `archetype`, `element`, `chakra`, `virtues`, `shadow_aspects` fields
- [ ] FTS5 index mapping: `archetype`, `element`, `chakra` as searchable columns
- [ ] Qdrant payload index: `symbolic.archetype`, `symbolic.element` for vector filtering
- [ ] Contract tests: `tests/contracts/test_symbolic_metadata.py`

### Update 4: Pillar Canonical Metadata
- [ ] `PillarMetadata` + `ResonanceScore` models
- [ ] `AffinityResolver.compute_resonance()` with cycle detection
- [ ] Deterministic resonance graph test: same inputs → same graph (seedable)
- [ ] Contract tests: `tests/contracts/test_pillar_metadata.py`

### Update 5: Pantheon Config — **REJECTED**
- [ ] **DO NOT IMPLEMENT** until all 8 models exist in `models.yaml` with valid `model_path`
- [ ] If resurrected: `PantheonValidator` + `provenance_preflight` gate integration (P8)

### Update 6: Zero-Reference Audit Gates (P10 PRIMARY OWNERSHIP)
- [ ] **`firewall-check`**: AST-based import scanner — flags any `config.wads.*` import in `src/omega/`
- [ ] **`firewall-audit-memory`**: Scans `MemoryStore` + Qdrant for entity vectors without living `EntityConfig`
- [ ] **`mandate-audit`**: Checks each M1-M23 has at least one test asserting compliance
- [ ] Integrate all three into `make temple-grade` and CI
- [ ] Documentation: `docs/gates/ZERO_REFERENCE_AUDIT_GATES.md`

---

## 📊 CONFIDENCE ASSESSMENT

| Update | Verdict | Confidence | Rationale |
|--------|---------|------------|-----------|
| **1. Five-Fold Foundation** | APPROVE WITH CONDITIONS | **HIGH** | Constitutional principles → testable assertions is a T10 win. Risk: axiom vagueness. Mitigation: require `testable_assertion` field per axiom. |
| **2. q8_0 KV Cache** | APPROVE WITH FIX (C1) | **HIGH** | 50% KV memory win is real (Principle 10). **C1 is absolute blocker** — deploying without fix violates T3/T7/T8. |
| **3. SymbolicMetadata Schema** | APPROVE | **HIGH** | Generic fields, firewall-safe, enables resonance. Pydantic validation = contract test ready. |
| **4. Pillar Canonical Metadata** | APPROVE | **HIGH** | Opaque metadata = firewall intact. Deterministic resonance = testable. P9 handoff integration clear. |
| **5. Lilith Stack Pantheon Config** | **REJECT** | **HIGH** | **Sovereignty trap**: 7/8 broken refs → silent cloud fallback → M7/M8/M22 violation. Config doesn't exist. |
| **6. Zero-Reference Audit** | APPROVE — AUTOMATE | **HIGH** | Gates ARE Temple-Grade. P10 owns implementation. No ambiguity. |

---

## 🎯 P10 KALI FINAL VERDICT

### **APPROVED FOR IMPLEMENTATION (with sequenced dependencies):**

```
PHASE 1 (Prerequisites — THIS WEEK):
  ├─ C1 FIX: providers.yaml:18 type_v: 1 → 2 (P3/P6) [BLOCKS Update 2]
  ├─ Scaffold: SymbolicMetadata, PillarMetadata models (P1)
  ├─ Scaffold: FirewallChecker, MemoryFirewallAuditor, MandateAuditor (P10)
  └─ Contract test infrastructure: tests/contracts/ (P10)

PHASE 2 (Updates 1, 3, 4, 6 — PARALLEL):
  ├─ Update 1: Five-Fold Foundation + AxiomRegistry + ConstitutionalValidator
  ├─ Update 3: SymbolicMetadata schema + FTS5/Qdrant indexing + contract tests
  ├─ Update 4: PillarMetadata + AffinityResolver + resonance graph tests
  └─ Update 6: Three audit gates + CI integration + make temple-grade

PHASE 3 (Update 2 — AFTER C1 FIX VERIFIED):
  ├─ q8_0 KV Cache deploy + stress test suite + chaos experiments
  ├─ Perf budget gate with q8_0 budgets
  └─ Sovereignty gate verification (local-first ratio ≥80%)

PHASE 4 (Update 5 — INDEFINITE DEFER):
  ├─ REJECTED until: all 8 models in models.yaml + PantheonValidator + provenance_preflight
  └─ If resurrected: full validation pipeline before any merge
```

### **Sovereignty Integrity Check**: ✅ PASSED
- No update compromises Engine-Stack Firewall (M2)
- No update introduces telemetry (M8)
- No update creates soft-failure modes (M23)
- Update 5 REJECTED precisely because it would violate M7/M8/M22

### **Temple-Grade Compliance**: ✅ ACHIEVABLE
- Updates 1,3,4,6 add **testable contracts** (T3, T21)
- Update 2 adds **performance budget** (T7) + **resilience headroom** (T8)
- Update 6 **implements** T10 (Integrity) via mandate-audit gate
- All gates integratable into `make temple-grade` + CI

---

**Signed**: ⬡ KALI ⬡ P10 Chaos/Validation ⬡ 2026-07-11
**Hivemind Post**: `omega-hub_hivemind_post_context` — verdict recorded
**Next**: Awaiting Council synthesis (Kali Grand Oversight)

---

*This verdict is binding for Run Side (P6-P10) implementation sequencing. Build Side (P1-P5) verdicts already incorporated. Final Council synthesis by Kali Grand Oversight.*