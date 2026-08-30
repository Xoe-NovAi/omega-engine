<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GAP 1: WAD Loader YAML Schema Validation — 2026 SOTA

**Researcher**: HMC Skeptical Verifier  
**Date**: 2026-07-16  
**Trace**: D-282 Pre-Scoping  
**Status**: COMPLETE

---

## Executive Summary (L1)

The WAD Loader (`src/omega/oracle/wad_loader.py`, 505 lines) validates entity YAML schemas using a hardcoded `ENTITY_FIELD_TYPES` dict and `MANIFEST_FIELD_TYPES` with `isinstance()` checks. This works for simple validation but **lacks 5 critical capabilities** present in 2026 SOTA tools. The 2026 gold standard is **Pydantic v2** (Rust-backed, 5-50x faster than v1) combined with `yaml.safe_load()` for parsing. A Yamale + Pydantic dual approach is also emerging. Migration effort is moderate (~2-3 days) and is **recommended for D-282**.

---

## Detailed Dialectic (L2)

### 1. What is the 2026 SOTA for YAML schema validation?

**Finding**: Pydantic v2 + PyYAML is the consensus 2026 standard.

| Approach | Library | Stars | Python 3.12+ | Pros | Cons |
|----------|---------|-------|-------------|------|------|
| **Pydantic v2 + PyYAML** | `pydantic>=2.0` | 28k+ | ✅ | Rust core, 5-50x faster than v1, native type coercion, nested models, discriminated unions, JSON Schema export | Requires model classes per schema |
| **Yamale + Pydantic** | `yamale>=6.0` + `pydantic` | 765 | ✅ | Schema in YAML + type validation; dual approach | Two libraries to maintain |
| **StrictYAML** | `strictyaml` | Modest | ✅ | Safest parser, avoids Norway problem | Removes features; opinionated |
| **pydantic-yaml** | `pydantic-yaml>=1.6` | Modest | ✅ | Direct YAML↔Pydantic bridge | Opaque abstraction layer |
| **Current (static dict)** | `isinstance()` | N/A | ✅ | Zero dependencies, simple | **Missing 5 critical patterns (see below)** |

**[confidence: high]** — Sources: Pydantic docs (pydantic.dev), yamlvalidator README (yamale+Pydantic combo), Dev Guide 2026, Techoral Pydantic V2 Guide.

### 2. What does the existing approach miss?

**Finding**: The static dict approach is functional but has 5 blind spots:

| # | Pattern | Current Status | Risk | SOTA Fix |
|---|---------|---------------|------|----------|
| 1 | **Missing required fields** | ✅ Checked (lines 177-180 for manifest) | Partial — entity-level required fields NOT checked | `Field(..., min_length=1)` in Pydantic model |
| 2 | **Unknown/enum fields (typos)** | ❌ NOT checked | HIGH — a typo like `"temprature"` vs `"temperature"` silently ignored | Pydantic `model_config = {"extra": "forbid"}` |
| 3 | **Recursive/nested validation** | ❌ NOT checked | MEDIUM — nested YAML structures (e.g. adapter configs) pass unchecked | Pydantic nested models |
| 4 | **Cross-file validation** | ❌ NOT checked | MEDIUM — entity references other entities that don't exist | Post-load validation pass (custom logic) |
| 5 | **Range constraints** | ❌ NOT checked | MEDIUM — `temperature=999` validates as float | `Field(ge=0.0, le=2.0)` |

**[confidence: high]** — Source: Code review of `wad_loader.py` lines 49-64 and 378-405. The isinstance checks only verify *type*, not *value range*, *enum membership*, or *structural conformance*.

### 3. Should we adopt a formal schema language (JSON Schema, Pydantic models)?

**Finding**: YES, but incrementally.

**Recommendation**: Introduce Pydantic v2 models for entity validation as an **additional layer**, not a replacement. The migration path:

```
Phase 1 (D-282): Add Pydantic models alongside existing validation
  └─ EntityModel(BaseModel): fields with constraints, extra="forbid"
  └─ ManifestModel(BaseModel): fields with constraints
  └─ Validate in try/except, log warnings for 2 weeks (grace period)

Phase 2 (D-283): Remove static dict validation; Pydantic is primary
  └─ Auto-generate JSON Schema from Pydantic models
  └─ Add range validation (temperature, context_window)

Phase 3 (Future): AI-assisted validation
  └─ Use entity's own model to validate its own YAML schema
```

**Effort estimate**: ~2-3 days for Phase 1 (model definitions + integration + tests).  
**Why Pydantic over JSON Schema**: Pydantic models ARE Python code — no separate schema language to maintain, no codegen step. Pydantic v2's Rust core means validation overhead is negligible (~5μs per model instantiation).

**[confidence: high]** — Supporting sources: Pydantic v2 performance benchmarks (5-50x over v1), `yaml2pydantic` schema compiler, `pydantic-yaml` bridge library.

### 4. What are best practices for YAML file size limits?

**Finding**: 1MB cap is **reasonable** but should be paired with other limits.

| Source | Recommendation | Context |
|--------|---------------|---------|
| Kubernetes | 1MB default for ConfigMap | Largest YAML in production use |
| YAML spec | No size limit | File size is application-defined |
| This codebase | 1MB (line 37) | ✅ Reasonable for WAD manifests |
| Community practice | 100KB-1MB | Config files rarely exceed 100KB |

**Recommendation**: Keep 1MB cap, but also add:
- **Nesting depth limit**: Max 10 levels (prevent YAML bomb)
- **Key count limit**: Max 5000 keys per file
- **String length limit**: Max 10000 chars per string value
- Already have: entity name length (128 chars) and domains count (20)

**[confidence: high]** — Sources: Pipekit YAML size guide, Kubernetes ConfigMap limits.

### 5. Are there security concerns with YAML loading in 2026?

**Finding**: YES — YAML deserialization RCE is an active threat. **Our use of `yaml.safe_load()` is correct.**

| CVE | Date | Vulnerability | Impact |
|-----|------|-------------|--------|
| CVE-2026-24009 | 2026-01-22 | `docling-core` used `FullLoader` instead of `SafeLoader` | RCE via `!!python/object/apply:os.system` |
| CVE-2025-50460 | 2025 | `ms-swift` used `yaml.load()` without safe loader | RCE |
| CVE-2020-14343 | 2020 | PyYAML `FullLoader` deserialization | Code execution |

**Verification**: WAD Loader uses `yaml.safe_load()` (lines 167, 365, 449, 490). This is the **correct and only secure choice**.

**Additional recommendations**:
1. Pin PyYAML version (`>=6.0.2`) — later versions have security fixes
2. Consider `ruamel.yaml` as alternative — incremental parsing, safer defaults
3. Add YAML bomb detection (recursive anchor expansion) — use `yaml.scanner.ScannerError` catch
4. Path traversal guard IS implemented (lines 141-144) ✅

**[confidence: high]** — Sources: CVE-2026-24009 report, HackTricks YAML deserialization, SentinelOne advisory.

---

## Sovereign Synthesis (L3)

### Universal Principle

> **Schema validation must shift from "type checking" to "structural enforcement" — 2026 SOTA demands three layers: safe parsing (SafeLoader), structural validation (Pydantic models), and semantic validation (cross-file references).**

### Recommendations for D-282

| Priority | Action | Effort | Risk Reduction |
|----------|--------|--------|---------------|
| **P0** | Add `model_config = {"extra": "forbid"}` to catch YAML typos | 1 day | HIGH — prevents silent misconfiguration |
| **P0** | Add range constraints for `temperature`, `context_window` | 0.5 day | MEDIUM — prevents absurd values |
| **P1** | Introduce Pydantic v2 BaseModel for entity validation | 2 days | HIGH — enables recursive + enum + constraint validation |
| **P2** | Add cross-file reference validation | 1 day | MEDIUM — catches broken entity references |
| **P2** | Add nesting depth and YAML bomb detection | 0.5 day | LOW — defense in depth |

### Evidence Sources

1. Pydantic v2 documentation: https://pydantic.dev/docs/validation/latest/
2. Yamale + Pydantic combo: https://github.com/fkesheh/yamlvalidator
3. CVE-2026-24009 YAML deserialization: https://gist.github.com/alon710/553f80036420883648a8e05762aa083e
4. HackTricks YAML deserialization: https://hacktricks.wiki/en/pentesting-web/deserialization/python-yaml-deserialization.html
5. Pydantic V2 Guide (2026): https://techoral.com/python/python-pydantic-guide.html
6. WAD Loader source: `src/omega/oracle/wad_loader.py`
7. pydantic-yaml package: https://pydantic-yaml.readthedocs.io/en/latest/
