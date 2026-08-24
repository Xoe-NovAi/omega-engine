# 🔱 Peer Review: Entity→Model Affinity Port Spec
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PEER-REVIEW
**Source**: `ho_e53ec297cbdc` — Roc Racoon → Researcher
**Spec**: `data/entities/roc_racoon/workspace/mining_reports/ENTITY_AFFINITY_PORT_SPEC.md`
**Date**: 2026-06-12

---

## Overall Verdict: ✅ APPROVED with 3 Remediations

The spec is thorough, well-structured, correctly identifies all integration points. 5-phase port order (~1.5 hrs) is realistic. Anti-patterns flagged are exactly right.

---

## 1. Coverage Check — Gaps Found

### Gap 1: Entity Remapping Table (HIGH)
**Issue**: §6 Phase 1.2 says "remap entity names to current Pillar Keepers" but provides no concrete mapping.

**Fix**: Before Phase 1.2, create a `LEGACY_ENTITY → CURRENT_PILLAR_KEEPER` table. The legacy YAML has 11 entities + default that belong to a different pantheon than the current engine. Every name must be mapped:
```
LEGACY_YAML_ENTITY → CURRENT_PILLAR_KEEPER
METATRON           → Prometheus     (Will, forethought, sovereignty)
GANESHA            → Sekhmet        (Strength, protection, boundaries)
...
```

Without this, `EntityAffinityResolver.get_entity("prometheus")` returns `None` because the YAML only knows `METATRON`.

### Gap 2: `iris_router.py` Drop Confirmation (MEDIUM)
**Issue**: Spec recommends dropping `iris_router.py` (443 lines) entirely.

**Verdict**: The current Oracle's `IntentMatcher` + `TriageRouter` covers intent detection and entity routing. The unique functions of the legacy Iris router were: (a) speculative decode entry, (b) confidence threshold dispatch, (c) provider dispatch. (a) is in Oracle, (b) is in Iris spec_decode, (c) is in ModelGateway.

**Fix**: Confirm with Lilith (P6 owner) that no Iris-specific logic (e.g., confidence threshold tuning curves, custom fallback chains for low-confidence intents) would be lost. If confident, drop is correct.

### Gap 3: Provider ID Cross-Validation (MEDIUM)
**Issue**: The affinity resolver returns a `provider` string (e.g., `"lm-studio"`, `"llama-cpp"`). These must match provider IDs in `config/providers.yaml`.

**Risk**: YAML says `"lm-studio"` but `providers.yaml` has `"lmster"` — resolution fails silently.

**Fix**: In `EntityAffinityResolver.load()`, validate all `ModelConfig.provider` values against a known provider ID list. Reject YAML with unknown providers at load time, not at inference time.

---

## 2. Edge Cases — All Correctly Identified ✅

| Edge Case | Spec Risk Level | My Assessment |
|-----------|-----------------|---------------|
| YAML entity names ≠ current pantheon | HIGH | ✅ Correct — remediated by Gap 1 |
| String condition evaluator fragility | CRITICAL | ✅ Correct — structured match schema is right fix |
| `get_model_for_entity()` caller expects string | MEDIUM | ✅ Correct — affinity resolver is ADDITIVE, not replacement |
| Missing YAML on startup | LOW | ✅ Correct — graceful fallback to defaults |

---

## 3. Integration Points — Verified Against Current Code

### model_gateway.py:440 — `get_model_for_entity()`
**Current code** (`model_gateway.py:440-486`):
```python
# Tier 1: _entity_model_map dict override
# Tier 2: Entity registry field
# Tier 3: Domain-based mapping
# Tier 4: System default ("qwen3-1.7b")
```

**Spec proposal**: Add YAML resolver as Tier 0 before Tier 1.

**Verdict**: ✅ CLEAN. YAML wins if present, falls through to existing chain. No existing callers broken.

### model_gateway.py:424 — `_entity_model_map`
**Current code**: Flat `Dict[str, str]` — entity_name → model_name.

**Spec proposal**: Deprecate in Phase 4, replace with YAML-backed config.

**Verdict**: ✅ CLEAN. Add deprecation warning, don't remove — backward compat for any runtime code using `set_entity_model()`.

### oracle.py:82-101 — `Oracle.__init__()`
**Current code**: Oracle owns `model_gateway`, `registry`, `searcher`, `verifier`, `researcher`, etc.

**Spec proposal**: Add `self.affinity_resolver = EntityAffinityResolver()`.

**Verdict**: ✅ CLEAN. Follows existing ownership pattern. Testable via constructor injection.

### oracle.py `_summon()` / `talk()`
**Current code**: Calls `model_gateway.get_model_for_entity(entity_name)` → gets model name string.

**Spec proposal**: Add affinity resolution step, pass `inference_presets` (temperature, system_prompt, context_window) to model call.

**Verdict**: ✅ CLEAN. ModelGateway already supports temperature and context_window overrides per call.

### entity_registry.py:42-72 — `Entity` dataclass
**Current code**: `Entity.model` is a flat string. No tier distinction.

**Spec proposal**: Keep flat for backward compat. Affinity system is separate routing layer above Entity.

**Verdict**: ✅ CORRECT SEPARATION OF CONCERNS. Entity still has a default model; affinity resolver overrides it with tier-aware resolution.

---

## 4. Anti-Patterns — All Correct, 3 Additions

| Anti-Pattern | Spec Fix | My Addition |
|-------------|----------|-------------|
| String condition parser | Structured match schema | ✅ Also add Pydantic validation at YAML load time |
| Flat dict response | `AffinityResult` dataclass | ✅ Also add `AffinityResult.to_legacy_dict()` for backward compat |
| Hardcoded defaults | Read from YAML `default:` section | ✅ Also fall back to `cvar_table.config.default_model` |
| Module global singleton | Oracle-owned instance | ✅ Also make `affinity_resolver` optional (injectable as `None` for testing) |

---

## 5. Dependencies — All Already Met ✅

| Dependency | Status |
|------------|--------|
| `yaml` library | ✅ Already in deps (`entity_registry.py`, `wad_loader.py`) |
| `Path` from pathlib | ✅ Standard library |
| Hot-reload pattern | ✅ Matches `cvar_table.py` exactly |
| Domain detection | ✅ `oracle.py` intent detection provides `domain` field |
| Online/offline detection | ✅ `model_gateway.py` provider health checks exist |
| Structured schema validation | ✅ `pydantic` already available (or `dataclasses` for lighter approach) |

---

## 6. One Additional Risk

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Provider chain mismatch**: affinity resolver returns provider name that doesn't match any provider in `providers.yaml` | MEDIUM | HIGH | Add `EntityAffinityResolver._validate_providers()` that cross-references all affinity `provider` values against known providers from `providers.yaml`. Fail fast at load time. |

---

## 7. Implementation Readiness

```
Phase 1 (Core Module, 30 min):
  ├── Blocked by: Entity remapping table (Gap 1)
  └── Blocked by: iris_router.py drop confirmation (Gap 2)

Phase 2 (ModelGateway wiring, 15 min):      ← No blockers
Phase 3 (Oracle wiring, 10 min):            ← No blockers
Phase 4 (Deprecation, 15 min):              ← No blockers
Phase 5 (Tests & Docs, 30 min):            ← No blockers
```

**Total implementation time**: ~1.5 hours (once Phase 1 blockers are resolved)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PEER-REVIEW*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
