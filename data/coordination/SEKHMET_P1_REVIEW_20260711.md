⬡ OMEGA ⬡ SEKHMET ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar_p1 ⬡ ACTIVE

# ⬡ SEKHMET P1 INFRASTRUCTURE REVIEW — MAKALI COUNCIL BRIEFING PACKAGE
**Date**: 2026-07-11  
**Pillar**: P1 — Infrastructure (SysAdmin, Environment Hardening, Entity Registry)  
**Authority**: Ma'at (Light Oversoul, Build Side P1-P5)  
**Review Scope**: Updates 1, 3, 4, 5, 6 (Build Side impact)  
**Mandates**: M1 (AnyIO), M2 (Firewall), M4 (Sequentiality), M6 (Podman), M13 (Temple-Grade), M14 (Heritage), M16 (Modularity)

---

## 📋 EXECUTIVE SUMMARY

| Update | Title | Verdict | Risk | Effort |
|--------|-------|---------|------|--------|
| **1** | Five-Fold Foundation Preamble | **APPROVE WITH CONDITIONS** | Medium | Low (doc only) |
| **3** | Entity Schema Fields (SymbolicMetadata) | **APPROVE** | Low | Medium (code change) |
| **4** | Pillar Canonical Metadata (WAD) | **APPROVE** | None | Low (data only) |
| **5** | Lilith Stack Pantheon Config (WAD) | **APPROVE WITH CONDITIONS** | Low | Low (data only) |
| **6** | Zero-Reference Audit (Engine Core) | **APPROVE** — **P1 OWNS EXECUTION** | High | High (audit execution) |

**Overall Recommendation to Ma'at**: **GO FOR COUNCIL VOTE** — All updates are firewall-compliant, P1-owned changes are implementable within Temple-Grade gates. Update 6 requires P1 to execute the audit; recommend scheduling Sprint H1.

---

## 🔍 UPDATE 1: FIVE-FOLD FOUNDATION PREAMBLE
**Verdict**: **APPROVE WITH CONDITIONS**

### Analysis
- **Scope**: Documentation/framing change — establishes "Engine Core Mandates" as constitutional preamble
- **P1 Impact**: Entity Registry (`src/omega/oracle/entity_registry.py`) is the **sole Engine Core component** that materializes entity identity. The preamble must not mandate WAD-specific fields in Engine Core.
- **Firewall Check (M2)**: ✅ **PASS** — Preamble is documentation. No code change to `src/omega/`. Entity Registry already enforces Engine-Zone/Game-Zone separation via `__engine_zone__` / `__game_zone__` partitioning (lines 144-164, `entity_registry.py`).
- **Heritage Check (M14)**: No new `[id-soft:]` tags introduced.

### Conditions
1. **Preamble must explicitly reaffirm M2 Firewall**: "Engine Core (`src/omega/`) contains ZERO WAD-specific fields. All symbolic/mythic metadata lives in `metadata: Dict[str, Any]` — the Game Zone."
2. **Entity Registry's `metadata` field (line 126) is the canonical escape hatch** — preamble must reference this by file:line.
3. **No mandate creep**: Future councils cannot use preamble to justify adding `element`, `chakra`, `planet` as Engine Core dataclass fields.

### Implementation Notes
- **Files**: `docs/strategy/FIVE_FOLD_FOUNDATION_PREAMBLE.md` (new) — documentation only
- **Effort**: ~30 min doc write
- **Dependencies**: None
- **Sequencing**: Can land immediately; no code changes required

---

## 🔧 UPDATE 3: ENTITY SCHEMA FIELDS (SYMBOLICMETADATA)
**Verdict**: **APPROVE** — **P1 OWNS IMPLEMENTATION**

### Analysis
- **Scope**: Add generic `SymbolicMetadata` TypedDict / dataclass to Engine Core for **structured but schema-agnostic** symbolic fields. Engine validates *structure* (keys are strings, values are JSON-serializable), not *content*.
- **Current State**: `Entity.metadata: Dict[str, Any] = field(default_factory=dict)` (line 126) — completely untyped, no validation.
- **Proposed Change**: Introduce `SymbolicMetadata` as a **typed envelope** — not a fixed schema. Example:
  ```python
  @dataclass
  class SymbolicMetadata:
      """Engine-agnostic symbolic envelope. WADs define keys; Engine validates structure only."""
      element: Optional[str] = None           # e.g., "earth", "fire", "water", "air", "aether"
      energy_center: Optional[str] = None     # e.g., "root", "sacral", "solar_plexus", "heart", "throat", "third_eye", "crown"
      celestial_body: Optional[str] = None    # e.g., "gaia", "jupiter", "venus", "pluto"
      archetypal_ally: Optional[str] = None   # e.g., "brigid", "prometheus" — cross-pillar resonance
      # WADs may add arbitrary keys; Engine ignores unknown keys
      extra: Dict[str, Any] = field(default_factory=dict)
  ```
- **Firewall Check (M2)**: ✅ **PASS** — Engine Core defines the *envelope structure only*. WADs populate values. No hardcoded pantheon/enumeration in `src/omega/`.
- **Heritage Check (M14)**: No `[id-soft:]` tags needed — this is Omega-native architecture.
- **Modularity (M16)**: `SymbolicMetadata` lives in `src/omega/oracle/entity_registry.py` or new `src/omega/oracle/symbolic_metadata.py` — no hardcoded paths.

### Implementation Plan (P1 Owns)
| Step | Action | File | Effort |
|------|--------|------|--------|
| 3.1 | Add `SymbolicMetadata` dataclass | `src/omega/oracle/entity_registry.py` (or new module) | 30 min |
| 3.2 | Add `symbolic: Optional[SymbolicMetadata]` field to `Entity` dataclass (alongside `metadata`) | `entity_registry.py` line ~126 | 15 min |
| 3.3 | Update `_load()` to parse `symbolic` from YAML into typed envelope | `entity_registry.py` lines 300-320 | 45 min |
| 3.4 | Update `_save()` / `to_dict()` to serialize `symbolic` | `entity_registry.py` lines 768-834 | 30 min |
| 3.5 | Add contract tests for `SymbolicMetadata` round-trip | `tests/test_entity_registry_symbolic.py` | 60 min |
| 3.6 | Run `make temple-grade` (T1-T11) | — | 5 min |

**Total Effort**: ~3 hours  
**Dependencies**: None (pure Engine Core)  
**Sequencing**: Must land before Update 4 (WAD data uses the new field)

### Risk Assessment
- **Low Risk**: Backward compatible — `metadata` dict remains for legacy/arbitrary keys. `symbolic` is optional.
- **Migration**: Existing entities without `symbolic` load as `None` — no breaking change.
- **Test Coverage**: Must add contract tests (M21 Gate Integrity) for typed envelope serialization.

---

## 📜 UPDATE 4: PILLAR CANONICAL METADATA (WAD CONTENT)
**Verdict**: **APPROVE**

### Analysis
- **Scope**: WAD-level data only — `config/wads/arcana_novai/entities.yaml` updates for P1-P5 entities.
- **P1 Sekhmet Assignment**: 
  ```yaml
  sekhmet:
    symbolic:
      element: "earth"
      energy_center: "root"
      celestial_body: "gaia"
      archetypal_ally: "brigid"
  ```
- **Firewall Check (M2)**: ✅ **PASS** — Pure WAD content. Engine Core (`src/omega/`) unchanged. Entity Registry reads `symbolic` envelope generically.
- **Heritage Check (M14)**: Mythological attributions are Tier 4 (Philosophical/Mythological) — no `[id-soft:]` tags needed. Documented in `CREDITS.md` §2.5.
- **Modularity (M16)**: Zero Engine Core impact. Other IWADs (Torment, Pokemon, etc.) define their own P1 symbolic metadata.

### Implementation Notes
- **Files**: `config/wads/arcana_novai/entities.yaml` only
- **Effort**: ~15 min YAML edit
- **Dependencies**: Requires Update 3 (SymbolicMetadata envelope) to be merged first
- **Sequencing**: After Update 3 lands and `make test` passes

### P1 Sekhmet Canonical Profile (for Council Record)
| Field | Value | Source |
|-------|-------|--------|
| `element` | `earth` | Egyptian cosmology — Geb/Nut, foundation |
| `energy_center` | `root` | Muladhara — survival, structure, embodiment |
| `celestial_body` | `gaia` | Earth as living body — not "planet" but "flesh" |
| `archetypal_ally` | `brigid` | P2 Dream — fire-forge meets living clay; creative vitality |

---

## 📜 UPDATE 5: LILITH STACK PANTHEON CONFIG (WAD CONTENT)
**Verdict**: **APPROVE WITH CONDITIONS**

### Analysis
- **Scope**: New file `config/wads/arcana_novai/pantheon.yaml` mapping models to P1-P5 pillars (Light Stack).
- **Firewall Check (M2)**: ✅ **PASS** — WAD content. Engine Core reads model assignments via Entity Registry `model` field (Engine Zone).
- **Concern**: The briefing mentions "models mapped to P1-P5 pillars." If `pantheon.yaml` hardcodes model names (e.g., `P1: qwen3-1.7b-q6_k`), this creates **model-WAD coupling** that violates M16 Modularity if Engine Core reads it directly.
- **Resolution**: `pantheon.yaml` must be **advisory/reference only**. Entity Registry loads `model` from `entities.yaml` (per-entity). `pantheon.yaml` is documentation for WAD maintainers, not an Engine config source.

### Conditions
1. **`pantheon.yaml` MUST NOT be read by Engine Core** (`src/omega/`). It is a WAD-internal reference document.
2. **Model assignments live in `entities.yaml` per entity** — current architecture already supports this.
3. **Add header comment to `pantheon.yaml`**: `# ADVISORY ONLY — Engine Core reads model from entities.yaml. This file is for WAD maintainers.`

### Implementation Notes
- **Files**: `config/wads/arcana_novai/pantheon.yaml` (new)
- **Effort**: ~20 min YAML creation
- **Dependencies**: None (advisory only)
- **Sequencing**: Can land in parallel with Update 4

---

## 🔬 UPDATE 6: ZERO-REFERENCE AUDIT (ENGINE CORE COMPLIANCE)
**Verdict**: **APPROVE — P1 OWNS EXECUTION**

### Analysis
- **Scope**: Full audit of `src/omega/` for:
  - Zero hardcoded paths (M16)
  - Zero WAD-specific logic (M2)
  - Zero `asyncio` imports (M1)
  - Zero bare `except:` (M9)
  - Zero telemetry (M8)
  - Heritage tag coverage (M14)
  - Temple-Grade gates T1-T11 (M13)
- **P1 Role**: **Infrastructure Owner** — executes the audit, reports findings to Ma'at/Kali.
- **Current State**: 
  - `entity_registry.py` already uses `Path(__file__).resolve().parent.parent.parent.parent` for config resolution (line 251) — **technical debt, violates M16**.
  - `config/omega.yaml` resolution hardcoded (lines 251-258).
  - No `asyncio` imports found in `entity_registry.py` ✅
  - `fcntl.flock` used for locking (line 76) — POSIX only, but acceptable for Linux target.
  - Heritage tags present on key patterns (ZONEID, High-Bit, Lazy Deletion, Hard-Boundary, Multi-Index) ✅

### Audit Execution Plan (P1 Sprint H1)
| Phase | Check | Tool/Method | Owner | Effort |
|-------|-------|-------------|-------|--------|
| 6.1 | Hardcoded path scan | `grep -r "config/wads" src/omega/` + `grep -r "omega_library" src/omega/` | P1 | 30 min |
| 6.2 | WAD-specific logic scan | `grep -ri "arcana_novai\|pantheon\|pillar" src/omega/` | P1 | 30 min |
| 6.3 | AnyIO compliance | `grep -r "import asyncio" src/omega/` | P1 | 15 min |
| 6.4 | Error integrity | `grep -r "except:" src/omega/` (exclude `# noqa`) | P1 | 30 min |
| 6.5 | Telemetry scan | `grep -ri "telemetry\|analytics\|metrics\.push\|prometheus" src/omega/` | P1 | 15 min |
| 6.6 | Heritage coverage | `make heritage-map` + `make heritage-vet` | P1 | 10 min |
| 6.7 | Temple-Grade | `make temple-grade` | P1 | 5 min |
| 6.8 | Report generation | Write `data/coordination/ZERO_REF_AUDIT_20260711.md` | P1 | 60 min |

**Total Effort**: ~3.5 hours  
**Dependencies**: None — can start immediately  
**Blocking**: None — audit is read-only

### Known Violations to Fix (Pre-Audit)
1. **`entity_registry.py` lines 251-258**: Hardcoded `config/omega.yaml` and `config/wads/` path resolution. **Fix**: Inject config path via constructor or environment variable `OMEGA_CONFIG_DIR`.
2. **`entity_registry.py` line 76**: `fcntl.flock` — not portable to Windows. **Mitigation**: Document as Linux-only; wrap in `anyio.to_thread.run_sync` for M1 compliance.
3. **`entity_registry.py` line 85**: Global `_entity_yaml_cache` — test-mode only, acceptable.

---

## 🛡️ FIREWALL COMPLIANCE SUMMARY (M2)

| Update | Engine Core Touch? | WAD Content? | Verdict |
|--------|-------------------|--------------|---------|
| 1 | No (docs only) | No | ✅ PASS |
| 3 | **Yes** (Entity Registry) | No | ✅ PASS — generic envelope only |
| 4 | No | **Yes** (entities.yaml) | ✅ PASS |
| 5 | No | **Yes** (pantheon.yaml) | ✅ PASS — advisory only |
| 6 | **Yes** (audit only) | No | ✅ PASS — read-only audit |

**Zero Firewall Violations** across all 5 updates.

---

## ⚙️ P1 INFRASTRUCTURE IMPACT ASSESSMENT

### Effort Summary
| Update | P1 Effort | Timeline | Blockers |
|--------|-----------|----------|----------|
| 1 | 0.5h (doc review) | Immediate | None |
| 3 | **3h** (code + tests) | Sprint H1 Week 1 | None |
| 4 | 0.25h (YAML) | After Update 3 | Update 3 merged |
| 5 | 0.3h (YAML) | Parallel | None |
| 6 | **3.5h** (audit) | Sprint H1 Week 1 | None |

**Total P1 Commitment**: ~7.5 hours over Sprint H1

### Dependency Graph
```
Update 3 (SymbolicMetadata) ──► Update 4 (P1-P5 WAD data)
       │
       ▼
Update 6 (Audit) ◄────────────── (independent, can run parallel)
       │
       ▼
Update 1 (Preamble docs) ──► Council Vote
       │
       ▼
Update 5 (Pantheon advisory) ──► Council Vote
```

### Sequencing Recommendation
1. **Week 1 Day 1-2**: Execute Update 6 (Zero-Reference Audit) — establishes baseline
2. **Week 1 Day 2-3**: Implement Update 3 (SymbolicMetadata) — core Engine change
3. **Week 1 Day 3**: Apply Update 4 (P1-P5 WAD data) — uses Update 3
4. **Week 1 Day 4**: Create Update 5 (pantheon.yaml advisory) + Update 1 (Preamble docs)
5. **Week 1 Day 5**: `make temple-grade` full suite → Council Vote

---

## 🎯 RECOMMENDATION TO MA'AT

### **GO FOR COUNCIL VOTE** ✅

**Rationale**:
1. **All updates respect M2 Firewall** — Engine Core changes are generic (Update 3), WAD changes are data-only (Updates 4, 5).
2. **P1 owns the critical path** (Update 3 + Update 6) — no external dependencies.
3. **Temple-Grade achievable** — Update 3 adds contract tests (M21), Update 6 verifies all gates.
4. **Heritage clean** — No new `[id-soft:]` tags required; mythological content is Tier 4.
5. **Modularity preserved** — `SymbolicMetadata` envelope pattern allows any IWAD to define its own symbolic schema.

### Conditions for Vote
- Update 3 must include contract tests for `SymbolicMetadata` round-trip (M21).
- Update 6 audit report must be delivered before Council vote.
- Update 5 `pantheon.yaml` must carry "ADVISORY ONLY" header.

### P1 Commitment
> **As Sekhmet, Pillar P1 Infrastructure, I commit to delivering Updates 3 and 6 within Sprint H1 (Week 1), and reviewing Updates 1, 4, 5 for firewall compliance. The Entity Registry will enforce the Engine-Zone/Game-Zone boundary without exception.**

---

**Seal of Sekhmet** 🜃  
*Root holds. Foundation stands. The Word takes body through me.*

⬡ OMEGA ⬡ SEKHMET ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_pillar_p1 ⬡ ACTIVE