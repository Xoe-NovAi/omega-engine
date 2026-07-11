⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_p3_review ⬡ ACTIVE

# 🔱 PROMETHEUS P3 ENGINEERING REVIEW
## MaKaLi Council Briefing Package — Build Side (P1-P5) Assessment
**Date**: 2026-07-11
**Slot**: P3 — Engineering (BuildMaster, Implementation, Hardening, Model Configs)
**Authority**: Ma'at (Light Oversoul, Build Side Governor)
**Scope**: Updates 2, 3, 5 — Direct P3 Engineering Impact

---

## EXECUTIVE SUMMARY

| Update | Verdict | Risk | Effort | Firewall (M2) |
|--------|---------|------|--------|---------------|
| **2: q8_0 KV Cache Universal** | **APPROVE WITH CONDITIONS** | LOW | 2-4h | ✅ COMPLIANT |
| **3: SymbolicMetadata Schema** | **APPROVE WITH CONDITIONS** | MEDIUM | 4-8h | ✅ COMPLIANT |
| **5: Lilith Pantheon Config** | **DEFER** | MEDIUM | 2-3h | ⚠️ WAD CONTENT (P3 validates only) |

**Overall Recommendation to Ma'at**: **CONDITIONAL GO** — Updates 2 & 3 are engineering-hardening wins with clear local-first ROI. Update 5 is WAD content; P3 validates model resolution only. No Engine-Stack Firewall violations.

---

## UPDATE 2: q8_0 KV CACHE UNIVERSAL
**Classification**: ENGINE CORE OPTIMIZATION (M7 Local-First, M13 Temple-Grade)

### Briefing Summary
Universal `llama.cpp` KV cache quantization (`q8_0` key + value) for ALL models in `config/models.yaml`. LM Studio mining (P0) identified this as #1 missed optimization: ~50% KV memory reduction, negligible quality loss. Affects ALL models via native-gguf backend. Requires `config/models.yaml` `loading_strategy` entries update.

### Current State Analysis

**config/models.yaml** (lines 114-123):
```yaml
kv_cache:
  default_key_type: q8_0
  default_value_type: q8_0
  models:
    qwen3-0.6b-q6_k:
      key_type: f16
      value_type: f16
    qwen3-4b-thinking-q4_k_m:
      key_type: q8_0
      value_type: q8_0
```

**model_gateway.py** (lines 336-341, 424-436):
```python
kv_map = {"f16": 1, "q8_0": 8, "q4_0": 2}
for yaml_key, prov_key in [("kv_cache_key_type", "type_k"), ("kv_cache_value_type", "type_v")]:
    if yaml_key in merged:
        merged[prov_key] = kv_map.get(merged.pop(yaml_key), 8)
```

**providers.yaml** (lines 17-18):
```yaml
type_k: 8
type_v: 1  # <-- MISMATCH: key=q8_0 (8), value=f16 (1)
```

### Findings

| Aspect | Status | Notes |
|--------|--------|-------|
| **Default config** | ✅ CORRECT | `default_key_type: q8_0`, `default_value_type: q8_0` |
| **Per-model overrides** | ⚠️ INCOMPLETE | Only 2 of 18 models have explicit KV config |
| **Provider default** | ❌ MISMATCH | `providers.yaml` has `type_v: 1` (f16) — overrides models.yaml default |
| **Model loading path** | ✅ WORKING | `_merge_native_gguf_config()` correctly maps YAML→llama.cpp enums |

### Firewall Compliance (M2)
**COMPLIANT** — This is pure Engine Core optimization. No WAD content touched. `config/models.yaml` is Engine config (not WAD).

### Implementation Plan

1. **Fix providers.yaml mismatch** (Priority: CRITICAL)
   - Change `type_v: 1` → `type_v: 8` to align with models.yaml default
   - This ensures native-gguf provider uses q8_0 for BOTH key and value by default

2. **Add per-model KV config to ALL 18 models** (Priority: HIGH)
   - Apply `kv_cache_key_type: q8_0`, `kv_cache_value_type: q8_0` to every model entry
   - Exception: `qwen3-0.6b-q6_k` can stay f16 if quality regression observed (document rationale)

3. **Validate memory savings** (Priority: MEDIUM)
   - Add benchmark test: `make bench-kvcache` measuring KV memory before/after
   - Target: ≥40% reduction for 8K context, ≥50% for 16K+

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Quality regression on small models (0.6B) | LOW | MEDIUM | Keep f16 override for qwen3-0.6b-q6_k with comment |
| Provider config drift | MEDIUM | HIGH | Fix providers.yaml now; add CI check |
| llama.cpp version incompatibility | VERY LOW | LOW | q8_0 stable since llama.cpp b4000+ |

### Effort Estimate
- **Code changes**: 30 min (providers.yaml + models.yaml bulk edit)
- **Testing**: 1-2h (benchmarks + smoke test all 18 models)
- **CI gate**: Add `make heritage-map` style check for KV config completeness

---

## UPDATE 3: ENTITY SCHEMA FIELDS (SYMBOLICMETADATA)
**Classification**: ENGINE CORE CHANGE (M16 Modularity, M21 Gate Integrity)

### Briefing Summary
Generic framework fields for symbolic metadata in `src/omega/oracle/entity_registry.py`. P3 owns `config/models.yaml` and model loading pipeline — verify no model loading regression.

### Current State Analysis

**entity_registry.py** (lines 121-126, 159-164):
```python
# Generic Metadata (WAD-defined, engine-agnostic)
metadata: Dict[str, Any] = field(default_factory=dict)

__game_zone__ = {
    "personality": self.personality,
    "temperature": self.temperature,
    "context_window": self.context_window,
    **self.metadata,  # <-- Symbolic metadata merged here
}
```

**Entity loading** (lines 309-317, 339-353):
```python
core_fields = {"name", "domains", "capabilities", "model", "personality", 
               "temperature", "context_window", "slots", "role", 
               "container", "port", "wad_source", "priority", "metadata"}
wad_metadata = {k: v for k, v in raw.items() if k not in core_fields}
```

**Model resolution** (model_gateway.py lines 595-662):
```python
def get_model_for_entity(self, entity_name, affinity_context=None):
    # Tier 0: YAML Affinity Resolver (entity_model_affinity.yaml)
    # Tier 1: Runtime override
    # Tier 2: Entity registry field (entity.model)
    # Tier 3: Domain-based
    # Tier 4: System default
```

### Findings

| Aspect | Status | Notes |
|--------|--------|-------|
| **Metadata field exists** | ✅ | `metadata: Dict[str, Any]` in Entity dataclass |
| **Engine-zone isolation** | ✅ | `__engine_zone__` / `__game_zone__` partition enforced |
| **Model loading path** | ✅ UNCHANGED | `entity.model` field still read at Tier 2 |
| **Affinity resolver** | ✅ UNCHANGED | Reads entity name, not metadata |
| **Backward compat** | ✅ | `__getattr__` proxies to metadata dict |

### Firewall Compliance (M2)
**COMPLIANT** — Pure Engine Core schema evolution. WAD content (entities.yaml) consumes the new field; Engine does not interpret symbolic keys.

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model loading regression | VERY LOW | HIGH | Tier 2 resolution unchanged; existing tests cover |
| Metadata bloat in entities.yaml | MEDIUM | LOW | 1MB integrity guard in `_save()` catches this |
| Recursive metadata nesting | LOW | MEDIUM | `core_fields` includes "metadata" — prevents absorption |

### Implementation Notes
- **No code changes required in P3 domain** — model loading pipeline unaffected
- **Validation only**: Run `make test` focusing on `tests/test_entity_registry*.py` and `tests/test_model_gateway.py`
- **Gate Integrity (M21)**: Add contract test verifying `entity.model` resolution path unchanged

### Effort Estimate
- **Validation**: 30 min (targeted test run)
- **Documentation**: 15 min (update `docs/reference/api/entity_registry.md` if needed)

---

## UPDATE 5: LILITH STACK PANTHEON CONFIG
**Classification**: WAD CONTENT (M2 Engine-Stack Firewall — P3 validates resolution only)

### Briefing Summary
WAD content `config/wads/arcana_novai/pantheon.yaml` mapping models to P1-P5 pillars. P3 owns model loading — verify `pantheon.yaml` model references resolve to actual models in `config/models.yaml`.

### Current State Analysis

**File Status**: `config/wads/arcana_novai/pantheon.yaml` **DOES NOT EXIST** (glob search negative)

**Existing Pillar Mapping** (entities.yaml lines 58-59, 129-130, 199-200, 272-273, 343-344):
```yaml
# P1: Flesh (Sekhmet)
pillars: ['P1: Flesh']
model: qwen3-1.7b-q6_k

# P2: Dream (Brigid)  
pillars: ['P2: Dream']
model: phi-2-omnimatrix-i1-q4_k_m

# P3: Will (Prometheus)
pillars: ['P3: Will']
model: deepseek-r1-qwen3-8b-q3_k_l

# P4: Heart (Saraswati)
pillars: ['P4: Heart']
model: krikri-8b-q5_k_m  # <-- NOT IN models.yaml!

# P5: Throat (Inanna)
pillars: ['P5: Throat']
model: krikri-8b-q5_k_m  # <-- NOT IN models.yaml!
```

**models.yaml Model Registry** (lines 20-113):
| Model Key | Exists? | Path Valid? |
|-----------|---------|-------------|
| qwen3-1.7b-q6_k | ✅ | ✅ |
| phi-2-omnimatrix-i1-q4_k_m | ✅ | ✅ |
| deepseek-r1-qwen3-8b-q3_k_l | ✅ | ✅ |
| krikri-8b-q5_k_m | ❌ | N/A |
| krikri-8b-q4_k_m | ✅ | ✅ |

### Findings

| Issue | Severity | Impact |
|-------|----------|--------|
| **pantheon.yaml missing** | BLOCKER | Cannot validate what doesn't exist |
| **Saraswati/Inanna model mismatch** | HIGH | `krikri-8b-q5_k_m` not in models.yaml — will fail at load time |
| **Model key inconsistency** | MEDIUM | entities.yaml uses `krikri-8b-q5_k_m`; models.yaml has `krikri-8b-q4_k_m` |

### Firewall Compliance (M2)
**COMPLIANT WITH CAVEAT** — This is WAD content (arcana_novai). P3's role: **validate model resolution**, not author WAD content. The Engine-Stack Firewall holds: P3 does not dictate pantheon.yaml structure.

### Resolution Path (P3 Scope)
1. **Verify model keys** in entities.yaml resolve to models.yaml entries
2. **Fix Saraswati/Inanna**: Change `krikri-8b-q5_k_m` → `krikri-8b-q4_k_m` in entities.yaml
3. **When pantheon.yaml created**: Validate all `model:` refs exist in models.yaml

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Runtime model load failure | HIGH (current state) | CRITICAL | Fix entities.yaml model keys NOW |
| pantheon.yaml drift from entities.yaml | MEDIUM | MEDIUM | Add CI validation: `make validate-pantheon` |

### Effort Estimate
- **Fix entities.yaml**: 15 min (2 model key corrections)
- **Validate resolution**: 15 min (test `ModelGateway.get_model_path()` for all 10 pillars)
- **pantheon.yaml creation**: OUT OF SCOPE (WAD authoring — Lilith/P6-P10 domain)

---

## P3 ENGINEERING IMPACT SUMMARY

### Dependencies & Sequencing
```
Update 2 (KV Cache) ──► Independent, can ship immediately
       │
       ▼
Update 3 (SymbolicMetadata) ──► Independent, validation only
       │
       ▼
Update 5 (Pantheon) ──► BLOCKED on entities.yaml fix + pantheon.yaml creation
```

### Test Coverage Requirements (M21 Gate Integrity)
| Test | Update 2 | Update 3 | Update 5 |
|------|----------|----------|----------|
| `test_model_gateway.py` | ✅ REQUIRED | ✅ REGRESSION | ✅ REGRESSION |
| `test_entity_registry.py` | N/A | ✅ REQUIRED | ✅ REGRESSION |
| `test_providers.py` | ✅ REQUIRED (KV flags) | N/A | N/A |
| New: `test_kv_cache_quantization.py` | ✅ ADD | N/A | N/A |
| New: `test_pantheon_model_resolution.py` | N/A | N/A | ✅ ADD |

### Temple-Grade Gates (M13) Impact
| Gate | Update 2 | Update 3 | Update 5 |
|------|----------|----------|----------|
| T1 Version Control | ✅ | ✅ | ✅ |
| T3 Coverage ≥80% | ✅ (add KV test) | ✅ | ✅ |
| T5 AnyIO Only | ✅ | ✅ | ✅ |
| T6 Zero Telemetry | ✅ | ✅ | ✅ |
| T8 Resilience | ✅ | ✅ | ✅ |
| T9 Structured Logging | ✅ | ✅ | ✅ |
| T10 Atomic Writes | ✅ | ✅ | ✅ |
| T12 Semantic Integrity | ✅ | ✅ | ✅ |

---

## RECOMMENDATION TO MA'AT

### VERDICT: **CONDITIONAL GO FOR COUNCIL VOTE**

**Approve Updates 2 & 3** with conditions:
1. Update 2: Fix `providers.yaml` type_v mismatch BEFORE merge
2. Update 3: Run targeted regression suite (entity_registry + model_gateway)
3. Update 5: **DEFER** — Blocked on:
   - entities.yaml model key corrections (P3 can fix in 15 min)
   - pantheon.yaml creation (WAD content — Lilith/P6-P10 ownership)

**No Engine-Stack Firewall violations**. All changes respect M2 boundary.

**Local-First (M7) Impact**: Update 2 delivers ~50% KV memory reduction — direct sovereignty win for 12Gi RAM ceiling.

**Sequentiality (M4) Compliance**: Plan → Verify (this review) → Execute (sequential PRs).

---

## APPENDIX: FILES TO MODIFY

### Update 2 — KV Cache Universal
| File | Change | Lines |
|------|--------|-------|
| `config/providers.yaml` | `type_v: 1` → `type_v: 8` | 18 |
| `config/models.yaml` | Add `kv_cache_key_type: q8_0`, `kv_cache_value_type: q8_0` to all 18 model entries | 20-113 |
| `tests/test_kv_cache_quantization.py` | NEW: Benchmark + contract test | New file |

### Update 3 — SymbolicMetadata (Validation Only)
| File | Action |
|------|--------|
| `tests/test_entity_registry.py` | Run full suite; verify metadata proxy works |
| `tests/test_model_gateway.py` | Run full suite; verify model resolution unchanged |

### Update 5 — Pantheon (Deferred)
| File | Change | Owner |
|------|--------|-------|
| `config/wads/arcana_novai/entities.yaml` | Fix Saraswati/Inanna `model: krikri-8b-q5_k_m` → `krikri-8b-q4_k_m` | P3 (15 min) |
| `config/wads/arcana_novai/pantheon.yaml` | Create WAD content mapping P1-P5 | Lilith/P6-P10 |
| `tests/test_pantheon_model_resolution.py` | NEW: Validate all pantheon model refs resolve | P3 (after pantheon.yaml exists) |

---

**End of Review**  
⬡ OMEGA ⬡ PROMETHEUS ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_pillar_p3_review ⬡ COMPLETE