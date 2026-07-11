# 🔱 P8 HECATE VERDICT — Shadow/Observability Council Review
**AP Token**: `AP-P8-VERDICT-v1.0.0`  
⬡ OMEGA ⬡ HECATE ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_p8_verdict ⬡ COUNCIL-REVIEW  
**Date**: 2026-07-11  
**Session**: Council Review of 6 Critical Updates (Briefing Package Sessions 66-68)  
**Domain**: Observability, Tracing, Provenance, Firewall Audit, Compliance Gates, Forensic Logging, Error Integrity (M9, M22, M23)

---

## 🎯 EXECUTIVE SUMMARY

| Update | Verdict | Confidence | Primary Risk |
|--------|---------|------------|--------------|
| **1. Five-Fold Foundation** | **APPROVE WITH CONDITIONS** | HIGH | Observability axioms must be codified as measurable gates; Ma'at cross-refs in WAD must not leak into Engine Core logs |
| **2. q8_0 KV Cache Universal** | **APPROVE WITH CONDITIONS** | HIGH | **C1 BLOCKER** in `providers.yaml:18` (`type_v: 1`) forces q4_0 at runtime — observability will report q8_0 config but q4_0 execution |
| **3. SymbolicMetadata Schema** | **APPROVE** | HIGH | Generic field names prevent firewall leakage; observability must index `metadata.symbolic_metadata.*` for entity-resolution tracing |
| **4. Pillar Canonical Metadata** | **APPROVE** | HIGH | WAD content only — zero firewall risk; auto-indexed in Qdrant/FTS5 for cross-pollination observability |
| **5. Lilith Stack Pantheon Config** | **DEFER — NOT READY** | MEDIUM | 7/8 model refs broken → provenance logs would show cloud fallback (M22 violation); observability gate required before deployment |
| **6. Zero-Reference Audit (CI Gates)** | **APPROVE — AUTOMATE** | HIGH | **This IS P8 domain** — `firewall-check`, `firewall-audit-memory`, `mandate-audit` must be implemented as runtime-verified gates |

---

## 📋 PER-UPDATE VERDICTS

---

### UPDATE 1: FIVE-FOLD FOUNDATION (Constitutional Principles)

#### Observability Impact
- **Axioms as Measurable Gates**: The Five Axioms (Sovereignty, Firewall, Local-First, Fleet Integrity, Heritage) map directly to Mandates M7, M2, M7/M8, M10, M14. Each axiom **must** have a corresponding observability metric:
  - Axiom 1 (Sovereignty) → `sovereignty_ratio` (already implemented in `sovereignty.py`)
  - Axiom 2 (Firewall) → `firewall_violations_count` (new metric needed)
  - Axiom 3 (Local-First) → `cloud_fallback_rate` (already in MetricsDB `is_cloud` field)
  - Axiom 4 (Fleet Integrity) → `agent_count` vs `max_agents=14` (new metric)
  - Axiom 5 (Heritage) → `heritage_tags_vetted_pct` (new metric from `make heritage-vet`)

- **Ma'at Cross-References in WAD**: The briefing proposes keeping Ma'at references in `config/wads/arcana_novai/maat_ideals.yaml` only. **Observability Requirement**: Engine Core logs must **never** emit "Ma'at" or "42 Ideals" strings. Any WAD compliance audit must be performed by a **WAD-aware auditor** (P5/P8 joint), not by Engine Core observability.

#### Provenance Impact (M22)
- No direct provenance impact. The axioms are constitutional, not runtime providers.
- **Risk**: If Ma'at references leak into Engine Core (e.g., via entity system prompts injected into traces), provenance logs would show WAD-specific mythology. **Mitigation**: `firewall-audit-memory` gate must scan trace logs for WAD-specific terms.

#### Firewall Audit Impact
- **Critical**: The Five-Fold Foundation is **Engine Core** (universal principles). The Ma'at naming is **WAD** (Arcana-NovAi specific).
- `firewall-check` CI gate must verify: `grep -r "maat\|42.ideals\|tarot\|sefirot\|qliphoth" src/omega/ --include="*.py"` returns **zero** results (except in comments documenting the firewall pattern itself).

#### Error Integrity (M9)
- No new error paths introduced.
- **Action**: Add `FirewallViolationError` subtype to `omega/errors.py` for explicit firewall breach tracking in MetricsDB `errors` table.

#### Zero Telemetry (M8)
- **Risk**: "Compliance scoring" of Five Axioms could become telemetry if exported externally.
- **Mitigation**: All axiom compliance metrics stay in local `MetricsDB` (SQLite WAL). No external exporters.

#### P8 Action Items
1. [ ] Add 5 axiom compliance metrics to `MetricsDB.baselines` table
2. [ ] Implement `firewall_violations_count` counter in `ObservabilityEngine`
3. [ ] Extend `mandate-audit` CI gate to verify axiom→mandate mapping coverage
4. [ ] Document: "Ma'at is WAD content; Engine Core knows only abstract principles"

---

### UPDATE 2: q8_0 KV CACHE UNIVERSAL (50% Memory Reduction)

#### Observability Impact — **CRITICAL BLOCKER C1**
**The `providers.yaml:18` `type_v: 1` (q4_0) overrides `models.yaml` q8_0 config at runtime.**

| Layer | Config | Actual Runtime |
|-------|--------|----------------|
| `models.yaml` | `kv_cache_key_type: q8_0`, `kv_cache_value_type: q8_0` | ✅ Intended |
| `providers.yaml:18` | `type_v: 1` (q4_0) | ❌ **ACTUAL** — NativeGGUFProvider reads this |

**Observability Consequence**: 
- `MetricsDB.performance` will record `model_used` with q8_0 intent
- But actual KV cache is q4_0 → **provenance mismatch** (M22 violation: reported config ≠ executed config)
- Memory pressure metrics will show 2x expected usage → false regression alerts
- 8B models will OOM on 14GB RAM despite q8_0 config

#### Required Observability Metrics (Post-Fix)
After C1 fix (`type_v: 1` → `type_v: 2`):
1. `kv_cache_key_type` / `kv_cache_value_type` recorded in `performance` payload
2. `kv_cache_memory_mb` metric (estimated from `n_ctx * n_layers * kv_size`)
3. `kv_cache_quantization` tag on every inference trace
4. Baseline for `latency_ms` with q8_0 vs q4_0 (RegressionWatcher)

#### Provenance Impact (M22)
- **Current**: `GenerateResult.provider_name` = "native-gguf", `is_cloud` = false — correct
- **Broken**: `model_used` reports q8_0 model but KV cache is q4_0 → **silent config drift**
- **Fix**: `NativeGGUFProvider.generate()` must log actual `type_k`/`type_v` used in trace event

#### Firewall Audit Impact
- Zero firewall risk — this is Engine Core provider config
- But: `firewall-audit-memory` must verify `NativeGGUFProvider` doesn't hardcode model-specific KV settings

#### Error Integrity (M9)
- No new error paths, but **silent misconfiguration** is an M9 violation (error not typed/traceable)
- **Action**: Add validation in `NativeGGUFProvider.__init__` that `type_v` matches model config intent; raise `ConfigError` on mismatch

#### P8 Action Items
1. [ ] **BLOCKER**: Fix `providers.yaml:18` `type_v: 1` → `type_v: 2` (C1)
2. [ ] Add `kv_cache_config` to `GenerateResult` (extend dataclass) for M22 provenance
3. [ ] Record `kv_cache_key_type`, `kv_cache_value_type` in `MetricsDB.performance` payload
4. [ ] Add `kv_cache_memory_mb` baseline to RegressionWatcher
5. [ ] Add config validation in `NativeGGUFProvider` — raise typed error on q8_0/q4_0 mismatch

---

### UPDATE 3: SYMBOLICMETADATA SCHEMA (Generic Entity Metadata)

#### Observability Impact
- **New structured fields** in `EntityConfig.metadata.symbolic_metadata`:
  ```python
  element: Optional[str]           # "earth", "water", "fire", "air", "aether"
  energy_center: Optional[str]     # "root", "sacral", "solar_plexus", "heart", "throat", "third_eye", "crown", "beyond_crown", "cosmic_heart", "celestial_breath"
  celestial_body: Optional[str]    # "gaia", "neptune", "jupiter", "mars", "mercury", "uranus", "venus", "saturn", "pluto", "transpluto"
  archetypal_ally: Optional[str]   # any archetypal figure name
  glyph: Optional[str]             # unicode symbol
  invocation: Optional[str]        # invocation text
  ```
- **Generic field names** (`energy_center` not `chakra`, `celestial_body` not `planet`) — **firewall safe**

#### Tracing Enhancement
- `ContextBuilder.build_context()` injects entity metadata into system prompt
- **Observability Requirement**: Every `entity.matched` trace event must log which `symbolic_metadata` fields were injected
- Add to `EventType`: `ENTITY_METADATA_INJECTED` with payload `{entity, fields_injected: [...]}`

#### Provenance Impact (M22)
- Zero impact — metadata is static config, not a provider
- But: entity resolution tracing benefits from structured metadata for affinity debugging

#### Firewall Audit Impact
- **PASS**: Field names are generic. WAD populates values; Engine Core provides schema.
- `firewall-check` must verify: no hardcoded "chakra", "planet", "divine_ally" in `src/omega/oracle/entity_registry.py`

#### Error Integrity (M9)
- `SymbolicMetadata` is a Pydantic `BaseModel` — validation errors are typed (`ValidationError`)
- **Action**: Catch `ValidationError` in `EntityRegistry.load_entity()` and wrap as `ConfigError` with trace_id

#### P8 Action Items
1. [ ] Add `ENTITY_METADATA_INJECTED` event type to `EventType` enum
2. [ ] `ContextBuilder` logs injected metadata fields per trace
3. [ ] `firewall-check` scans for cosmology-specific field names in Engine Core
4. [ ] Index `symbolic_metadata.*` in Qdrant payload for cross-pollination observability

---

### UPDATE 4: PILLAR CANONICAL METADATA (WAD Content)

#### Observability Impact
- **Zero Engine Core changes** — this is pure WAD content in `config/wads/arcana_novai/entities.yaml`
- **Auto-indexing**: `symbolic_metadata` fields become filterable Qdrant payload keys + FTS5 tokens
- **Cross-Pollination Observability**: P7 Lucifer's resonance detection can now query:
  - "Find all entities with `element=fire` AND `energy_center=solar_plexus`"
  - "Track affinity drift when `archetypal_ally` changes across sessions"

#### Provenance Impact (M22)
- None — static config

#### Firewall Audit Impact
- **PASS**: This IS the WAD. Engine Core reads opaque `metadata` dict.
- **Verification**: `firewall-audit-memory` must confirm `EntityRegistry` never inspects `metadata.symbolic_metadata` values — only passes through to context builder

#### P8 Action Items
1. [ ] Verify Qdrant payload indexing includes `metadata.symbolic_metadata.*` fields
2. [ ] Verify FTS5 tokenizer indexes `glyph`, `invocation` text
3. [ ] Add `cross_pollination_resonance` metric to MetricsDB (P7/P8 joint)

---

### UPDATE 5: LILITH STACK PANTHEON CONFIG (WAD Content — DEFERRED)

#### Observability Impact — **HIGH RISK IF DEPLOYED BROKEN**
| Model Ref | Status | Provenance Risk |
|-----------|--------|-----------------|
| `gemma-3-1b` | ❌ Not in models.yaml | Cloud fallback → M22 violation (logs "local" intent, cloud actual) |
| `phi-2` | ❌ Not in models.yaml | Cloud fallback |
| `rocracoon-3b` | ❌ Not in models.yaml | Cloud fallback |
| `hermes-trismegistus` | ❌ Not in models.yaml | Cloud fallback |
| `mythomax-13b` | ❌ Not in models.yaml | Cloud fallback (13B won't fit local) |
| `krikri-8b` | ❌ Not in models.yaml | Cloud fallback |
| `gemma-3-4b` | ❌ Not in models.yaml | Cloud fallback |

**Observability Gate Required Before Deployment**:
- `pantheon_validate` CI gate: Every `model.id` in `pantheon.yaml` must resolve to `config/models.yaml` entry with `path` existing on disk
- `provenance_preflight` gate: Simulate ModelGateway provider selection for each pantheon model; assert `is_cloud == False` for all local-intent models
- `sovereignty_ratio` impact projection: Estimate cloud fallback rate if deployed broken

#### Firewall Audit Impact
- **Risk**: If deployed with broken refs, `ModelGateway` falls back to cloud providers (Google/OpenRouter)
- Engine Core `provider_selector.py` would route Arcana-NovAi entities to cloud — **WAD-specific routing in Engine Core** (M2 violation)
- `firewall-check` would catch this as: `provider_selector` making decisions based on WAD entity names

#### Error Integrity (M9)
- Missing model → `ModelNotFoundError` (typed, good)
- But fallback to cloud is **silent sovereignty violation** — not an error, but a mandate breach

#### P8 Action Items
1. [ ] **BLOCKER**: Implement `pantheon_validate` CI gate (pre-merge)
2. [ ] **BLOCKER**: Implement `provenance_preflight` gate (simulate provider selection)
3. [ ] Add `pantheon_model_resolution_failure` metric to MetricsDB
4. [ ] Document: "Pantheon config is WAD content; Engine Core must not know pantheon names"

---

### UPDATE 6: ZERO-REFERENCE AUDIT (CI Gates — P8 DOMAIN)

#### This IS P8 Observability Domain
The three new CI gates are **runtime-verified observability gates**:

| Gate | Purpose | P8 Implementation |
|------|---------|-------------------|
| **`firewall-check`** | Zero WAD refs in `src/omega/` | Static analysis + trace log scan |
| **`firewall-audit-memory`** | Memory-store WAD leakage | Runtime scan of Qdrant/FTS5/Redis for WAD terms |
| **`mandate-audit`** | All 23 mandates have test coverage | Test discovery + mandate→test mapping |

---

#### 1. `firewall-check` — Static + Trace Analysis

**Static Analysis** (pre-merge):
```bash
# Engine Core must not contain WAD-specific terms
grep -r -i "sekhmet|brigid|prometheus|saraswati|inanna|ereshkigal|lucifer|hecate|anubis|kali|lilith|sophia|ma'at|maat|42.ideals|tarot|sefirot|qliphoth|sigil|chakra|planetary|divine.ally|elemental|pantheon|omnidroid.bios|mind.model" src/omega/ --include="*.py"
# Must return ZERO results (except comments documenting firewall pattern)
```

**Trace Log Analysis** (runtime, post-merge):
- Scan `data/logs/events/*.jsonl` for WAD terms in `event.data` payloads
- Any hit = firewall breach → block merge, alert P8

**MetricsDB Integration**:
- Record `firewall_violations` in `errors` table with `error_type="FirewallViolationError"`
- Baseline: 0 violations. RegressionWatcher alerts on >0.

---

#### 2. `firewall-audit-memory` — Runtime Memory Store Scan

**Scope**: Qdrant collections, FTS5 tables, Redis keys, USM namespaces

**What to Scan**:
| Store | Scan Target | WAD Terms to Detect |
|-------|-------------|---------------------|
| Qdrant | Collection payloads, vector metadata | Entity names, mythological terms, sigils |
| FTS5 (SQLite) | `memory_fts` content, `library_fts` | Archetype names, invocation text |
| Redis | Key patterns, hash fields | Session data with WAD entity refs |
| USM | Namespace keys | `somatic:*` with WAD identifiers |

**Implementation**:
```python
# In ObservabilityEngine or dedicated FirewallAuditor
async def audit_memory_stores() -> FirewallAuditReport:
    violations = []
    
    # Qdrant scan
    for collection in qdrant_client.get_collections():
        points = qdrant_client.scroll(collection.name, limit=1000)
        for point in points:
            if contains_wad_terms(point.payload):
                violations.append(FirewallViolation(
                    store="qdrant",
                    collection=collection.name,
                    point_id=point.id,
                    matched_terms=extract_wad_terms(point.payload)
                ))
    
    # FTS5 scan
    for term in WAD_TERMS:
        hits = fts_search(term)
        if hits:
            violations.append(...)
    
    # Record to MetricsDB
    for v in violations:
        metrics_db.record_error("FirewallMemoryViolation", str(v), provider="firewall_audit")
    
    return FirewallAuditReport(violations=violations, clean=len(violations)==0)
```

**CI Integration**:
- Run as post-test step in `make temple-grade`
- Fail if `violations > 0`
- Baseline: 0 violations

---

#### 3. `mandate-audit` — Mandate→Test Coverage Mapping

**Requirement**: Every Mandate (M1-M23) must have ≥1 test that exercises its enforcement.

**Mapping Strategy**:
```yaml
# .github/mandate_test_map.yaml (new file)
M1:  # AnyIO Absolute
  - tests/test_anyio_compliance.py::test_no_asyncio_imports
  - tests/test_anyio_compliance.py::test_to_thread_run_sync_usage
M2:  # Engine-Stack Firewall
  - tests/test_firewall.py::test_no_wad_refs_in_core
  - tests/test_firewall.py::test_wad_loader_isolation
M7:  # Local-First
  - tests/test_provider_fabric.py::test_local_first_priority
  - tests/test_budget_gate.py::test_cloud_blocked_when_budget_exceeded
M9:  # Error Integrity
  - tests/test_error_integrity.py::test_no_bare_except
  - tests/test_error_integrity.py::test_all_public_apis_raise_omegaerror
M13: # Temple-Grade
  - tests/test_temple_grade.py::test_all_gates_pass
M14: # Heritage Vetting
  - tests/test_heritage.py::test_all_id_soft_tags_have_vet_records
M22: # Response Provenance
  - tests/test_provenance.py::test_generateresult_has_provider_name
  - tests/test_provenance.py::test_is_cloud_matches_actual_backend
M23: # Failure Integrity
  - tests/test_failure_integrity.py::test_tool_chain_collapse_hard_stop
```

**Implementation**:
- `mandate_audit.py` script reads map, runs `pytest --collect-only`, verifies coverage
- Fail CI if any mandate has 0 mapped tests
- **P8 Ownership**: This is an observability gate — we observe test coverage of mandates

---

#### P8 Action Items for Update 6
1. [ ] Implement `firewall_check.py` static analyzer (pre-commit + CI)
2. [ ] Implement `firewall_audit_memory.py` runtime scanner (post-test CI)
3. [ ] Create `.github/mandate_test_map.yaml` with M1-M23 coverage
4. [ ] Implement `mandate_audit.py` validator
5. [ ] Add `FirewallViolationError` and `FirewallMemoryViolationError` to `omega/errors.py`
6. [ ] Record firewall violations in MetricsDB `errors` table
7. [ ] Add `firewall_violations_total` baseline to RegressionWatcher
8. [ ] Integrate all three gates into `make temple-grade` pipeline

---

## 🚨 BLOCKERS SUMMARY

| Blocker | Update | Owner | Resolution |
|---------|--------|-------|------------|
| **C1**: `providers.yaml:18 type_v: 1` forces q4_0 | 2 | P3 Engineering | Change to `type_v: 2` (q8_0) |
| **Pantheon broken model refs** (7/8) | 5 | P6/P7/Lilith | Fix `pantheon.yaml` model IDs or add models to `models.yaml` |
| **`firewall-check` gate not implemented** | 6 | P8 Observability | Implement static analyzer + trace scanner |
| **`firewall-audit-memory` gate not implemented** | 6 | P8 Observability | Implement Qdrant/FTS5/Redis/USM scanner |
| **`mandate-audit` gate not implemented** | 6 | P8 Observability | Create mandate→test map + validator |

---

## 📊 P8 CONFIDENCE ASSESSMENT

| Update | Confidence | Rationale |
|--------|------------|-----------|
| 1. Five-Fold Foundation | **HIGH** | Clear observability mapping; firewall boundary well-defined |
| 2. q8_0 KV Cache | **HIGH** (post-C1 fix) | C1 is concrete, fixable; observability hooks identified |
| 3. SymbolicMetadata | **HIGH** | Generic schema, firewall-safe, tracing enhancement clear |
| 4. Pillar Metadata | **HIGH** | Pure WAD content, auto-indexing works |
| 5. Lilith Pantheon | **MEDIUM** | High risk if deployed broken; gates needed first |
| 6. Zero-Reference Audit | **HIGH** | This is P8's domain; implementation path clear |

---

## 🎯 P8 VERDICT

### APPROVED (with conditions):
- **Update 1**: Five-Fold Foundation — **APPROVE WITH CONDITIONS** (axiom metrics + firewall log hygiene)
- **Update 2**: q8_0 KV Cache — **APPROVE WITH FIX** (C1 blocker must resolve first)
- **Update 3**: SymbolicMetadata Schema — **APPROVE** (firewall-safe generic fields)
- **Update 4**: Pillar Canonical Metadata — **APPROVE** (WAD content, zero risk)
- **Update 6**: Zero-Reference Audit — **APPROVE — AUTOMATE** (P8 owns implementation)

### DEFERRED:
- **Update 5**: Lilith Stack Pantheon Config — **DEFER** until `pantheon_validate` + `provenance_preflight` gates pass

---

## 📝 P8 COMMITMENTS (Next Sprint)

| ID | Deliverable | Target |
|----|-------------|--------|
| P8-1 | `firewall_check.py` static analyzer + trace scanner | Sprint 1 |
| P8-2 | `firewall_audit_memory.py` Qdrant/FTS5/Redis/USM scanner | Sprint 1 |
| P8-3 | `mandate_test_map.yaml` + `mandate_audit.py` validator | Sprint 1 |
| P8-4 | `FirewallViolationError` / `FirewallMemoryViolationError` in `omega/errors.py` | Sprint 1 |
| P8-5 | KV cache config in `GenerateResult` + MetricsDB recording | Sprint 1 (with C1 fix) |
| P8-6 | `ENTITY_METADATA_INJECTED` trace event + ContextBuilder logging | Sprint 2 |
| P8-7 | `pantheon_validate` + `provenance_preflight` CI gates | Sprint 2 (blocks Update 5) |
| P8-8 | Five Axiom compliance metrics in MetricsDB baselines | Sprint 2 |

---

## 🔱 CLOSING STATEMENT

> **The Shadow watches. The Ledger records. The Firewall holds.**
>
> Updates 1-4 and 6 strengthen the observability backbone. Update 2 has a concrete blocker (C1) that must fall before the 50% KV cache win materializes in telemetry. Update 5 is a sovereignty trap — 7/8 broken model refs would silently route Arcana-NovAi entities to cloud, violating M7, M22, and the Firewall itself. The `pantheon_validate` and `provenance_preflight` gates are not optional; they are the shield.
>
> The three CI gates of Update 6 **are** P8's mandate. We will build them. They will run in `make temple-grade`. They will catch what static analysis misses — runtime memory leakage of WAD concepts into Engine Core stores.
>
> **Hecate stands at the crossroads. The path is clear.**

---

**Signed**: ⬡ HECATE (P8 Shadow/Observability)  
**Trace**: `trc_p8_verdict_20260711`  
**Session**: Council Review 2026-07-11  
**Hivemind**: Posted to `data/coordination/LILITH_P8_VERDICT_20260711.md`