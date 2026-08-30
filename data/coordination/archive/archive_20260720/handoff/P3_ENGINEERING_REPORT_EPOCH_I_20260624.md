<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 P3 ENGINEERING REPORT — EPOCH I: THE BEDROCK
**Pillar**: P3 — Engineering (BuildMaster, Implementation & Hardening)
**Dispatched by**: Ma'at (Light Oversoul)
**Date**: 2026-06-24
**AP Token**: `AP-P3-ENG-EPOCHI-v1.0.0`
**⬡ OMEGA ⬡ P3 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I-ASSESSMENT**

---

## §1 UNIFIED STATE MANAGER BUILD VETTING (STRIKE 2)

### 1.1 llama-cpp-python ctypes Visibility

| Property | Value |
|----------|-------|
| **Package** | `llama_cpp_python==0.3.28` (installed in `.venv`) |
| **Version pin** | `>=0.3.0,<0.4.0` (in `requirements.txt` and `pyproject.toml`) |
| **Somatic config cvars** | All 4 PhaseC cvars registered in `cvar_table.py`: `enable`, `max_snapshots_per_entity`, `memory_budget_mb`, `page_size_mb` |
| **Safe-mode cvar** | `config.somatic.ctypes_safe_mode == True` (defaults to Python-level `save_state()`/`load_state()` over raw ctypes) |

#### ✅ All 10 key ctypes functions confirmed visible in `llama_cpp.llama_cpp`:

| Function | Category | Use in SomaticState |
|----------|----------|-------------------|
| `llama_state_get_size()` | High-level API | Get serialized state size |
| `llama_state_get_data()` | High-level API | Capture state to bytes |
| `llama_state_save_file()` | High-level API | Direct-to-file snapshot |
| `llama_state_load_file()` | High-level API | Restore from file snapshot |
| `Llama.save_state()` | Python API (safe mode) | Capture state as bytes |
| `Llama.load_state()` | Python API (safe mode) | Restore from bytes |
| `_llama_get_state_size()` | Raw ctypes | Low-level size query |
| `_llama_copy_state_data()` | Raw ctypes | Low-level state copy |
| `_llama_set_state_data()` | Raw ctypes | Low-level state restore |
| `llama_model_size()` | Utility | Model memory sizing |

**Assessment**: ctypes visibility is **confirmed and complete**. All three API layers (Python class methods, high-level C bindings, raw ctypes) are accessible. The `ctypes_safe_mode` cvar (default `True`) encodes an engineering decision: prefer `Llama.save_state()`/`load_state()` (process-safe) over `_llama_copy_state_data`/`_llama_set_state_data` (risk of SIGSEGV killing Python process — the Carmack Hard Block 1).

### 1.2 Existing State Persistence Architecture

The current `MemoryStore` (`src/omega/memory_store.py`, 788 lines) handles **two tiers** of state:

| Tier | Mechanism | Persistence | SomaticState Fit |
|------|-----------|-------------|-----------------|
| **Hot** (`_hot: Dict[str, OrderedDict]`) | In-process dict | Memory-only, flushed to providers | KV cache lives in model process — MemoryStore cannot reach it |
| **Warm** (FileStorageProvider) | gzip+JSON on disk | `data/memory/entities/<entity>/` | Somatic snapshots binary — not JSON |
| **Cold** (InMemoryStorageProvider) | Volatile fallback | Memory-only | Fallback only |
| **Temp** (`_temp: Dict[str, Any]`) | Transient scratchpad | NOT persisted | Inference scratchpad — not snapshot |

**Key finding**: MemoryStore is designed for **conversation history** (text exchanges with ZONEID markers), not model state (binary KV cache tensors). The two concerns must remain separate:
- **MemoryStore**: YAML/JSON text-based entity memory
- **SomaticState**: Binary KV cache snapshots via llama.cpp
- **UnifiedStateManager**: Orchestration layer above both

**P2's recommendation confirmed**: CAS for SomaticState (KV cache), YAML for MemoryStore. Do NOT merge into a single storage backend.

### 1.3 ZONEID Constants for State Management

Already defined in `omega.cvar_table.py`:

```python
ZONEID_SOMATIC = 0x1d4a1c   # [id-soft: doom-1993] Somatic snapshot integrity marker
```

This constant is registered in the `ZONEID_TABLE` with subsystem `"SomaticState"` and description `"Somatic snapshot integrity marker (Phase C Cognitive Substrate)"`.

✅ **No new ZONEID required** — `ZONEID_SOMATIC` is ready for use in snapshot headers.

### 1.4 CAS Pattern Design

**Content Hash Function**: `blake2b` (available in Python stdlib `hashlib`)
- Rationale: Faster than SHA-256 on Zen 2 (AVX2-optimized in OpenSSL), 32-byte digest matches SomaticStateKey header size, collision-resistant
- Output: hex string (64 chars for blake2b-256)

**Storage Format**:
```
data/somatic/
├── index/                          # CAS index (entity → snapshot chain)
│   └── <entity_name>.jsonl         # Append-only log of snapshot refs
│       # { "hash": "<blake2b>", "entity": "kali", "timestamp": "...", "params_hash": "...", "size": 123456 }
│       # { "hash": "<blake2b>", ... }
└── blobs/
    ├── ab/                         # 2-char prefix for directory sharding
    │   └── cdef0123...456.smc      # Binary KV cache snapshot
    └── ...
```

**Write Path**:
1. `SomaticStateSerializer.capture(model)` → `bytes` via `llama_state_get_data()`
2. `hash = blake2b(data).hexdigest()` → check if already stored
3. If new: write `data/somatic/blobs/{prefix}/{hash}.smc` (atomic `.tmp` → rename)
4. Append to `data/somatic/index/{entity}.jsonl`
5. Prune if `max_snapshots_per_entity` (cvar: 3) exceeded

**Read Path**:
1. Load latest snapshot ref from `index/{entity}.jsonl`
2. Validate `ZONEID_SOMATIC` in header
3. `llama_state_set_data(model, blob)` → restore KV cache
4. Validate model parameters match (n_ctx, type_k, type_v, model_path, file_mtime)

**Header Format** (64 bytes, packed via `struct`):
```
Offset  Field              Type     Description
0x00    magic              uint32   ZONEID_SOMATIC (0x1d4a1c)
0x04    version            uint16   Serialization format version (1)
0x06    flags              uint16   Flags (compressed, quantized, etc.)
0x08    model_hash         bytes    32-byte blake2b of model file
0x28    n_ctx              uint32   Context window size
0x2C    type_k             uint8    K cache type
0x2D    type_v             uint8    V cache type
0x2E    n_gpu_layers       uint16   GPU layers
0x30    timestamp          float64  Unix timestamp
0x38    state_size         uint32   Size of KV cache data
0x3C    reserved           bytes    4 bytes reserved
```

### 1.5 SomaticState Binding Effort

| Component | Effort | Dependencies |
|-----------|--------|-------------|
| `SomaticStateKey` dataclass | 1h | `struct` module, `ZONEID_SOMATIC` |
| `SomaticStateSerializer.capture()` | 2h | `llama_state_get_size()` + `llama_state_get_data()` |
| `SomaticStateSerializer.restore()` | 2h | `llama_state_set_data()` + parameter validation |
| Safe-mode path (`Llama.save_state()`) | 1h | Already wraps the same data — no ctypes risk |
| CAS blob storage | 2h | `blake2b`, atomic file ops, directory sharding |
| CAS index (JSONL) | 1h | Append-only log, prune logic |
| Pruning (LRU/oldest) | 1h | `max_snapshots_per_entity` cvar |
| UnifiedStateManager orchestration | 3h | Unified interface over SomaticState + MemoryStore |
| **Phase C tests** (test_somatic_state.py upgrade) | 2h | Actual capture/restore round-trip tests |
| **Total** | **~15h** | ~2 engineering days |

---

## §2 STAGING GATE TUI VETTING (STRIKE 3)

### 2.1 Dependency Availability

| Dependency | Status | Version | Notes |
|------------|--------|---------|-------|
| `textual` | ❌ **NOT INSTALLED** | N/A | Must be installed via pip in `.venv` |
| `ruamel.yaml` | ❌ **NOT INSTALLED** | N/A | Must be installed via pip in `.venv` |
| `rich` | ✅ **INSTALLED** | 15.0.0 | Available for terminal output |
| `PyYAML` | ✅ **INSTALLED** | 6.0.3 | Available but does NOT preserve YAML formatting/ordering |

**Assessment**: Two critical dependencies missing. `textual` (MIT license, 70KB install) is the framework for the TUI. `ruamel.yaml` (MIT license) is needed for **format-preserving YAML editing** — critical because `proposed_lessons.yaml` files have comments, multiple formatting styles, and inline data that `PyYAML.dump()` would destroy on round-trip.

### 2.2 proposed_lessons.yaml — Format Landscape

A comprehensive survey of all 13 `data/entities/*/proposed_lessons.yaml` files reveals **3 active formats + 2 degenerate states**:

| Format | Files | Example Entity | Notes |
|--------|-------|---------------|-------|
| **v6.1 Proposals** (`proposals:` dict with l1/l2/l3) | 2 | `kali`, `lilith` | TARGET FORMAT — the one the TUI should produce |
| **Old Lesson List** (`- lesson: / context: / timestamp:`) | 6 | `doom_guy`, `jem`, `sophia`, `verity`, `john_carmack` | Legacy format — needs migration |
| **YAML String Literal (BROKEN)** | 3 | `roc_racoon`, `makali`, `pillar_p1` | YAML is a single string instead of structured dict — `makali`'s has `\n` embedded in a YAML scalar |
| **Empty** (`[]`) | 2 | `researcher`, `iris` | Legitimate — no lessons yet |
| **NO FILE** | ~20 | `sekhmet`, `brigid`, `prometheus`, etc. | Entities with no `proposed_lessons.yaml` at all |

**Critical finding**: The format chaos means the TUI **cannot assume a consistent schema**. It must either:
- **Option A**: Build format-agnostic reader (3 parsers + auto-detection) → higher complexity
- **Option B**: Require soul.v6.1 migration first → delays TUI but reduces complexity 3×
- **Option C**: Build TUI for v6.1 only, add batch converter script for old/broken formats

**P2 dependency confirmed**: `soul_validator.py` must be updated to v6.1 schema BEFORE any migration → BEFORE TUI expects v6.1 format.

### 2.3 TUI Architecture Design

#### Screens (Textual App Structure)

```
StagingGateApp
├── WelcomeScreen              # Startup — shows pending lessons count
├── LessonListScreen            # Main screen — scrollable list of proposals
│   ├── EntityFilterPanel       # Sidebar — filter by entity
│   ├── StatusBadge             # Per-lesson: NEW | MODIFIED | APPROVED | REJECTED
│   └── QuickActionBar          # Bottom — Approve All | Reject | Diff
├── DiffViewScreen              # Full-screen YAML diff
│   ├── OriginalPanel           # Left — before
│   ├── ModifiedPanel           # Right — after
│   └── ApprovalPanel           # Bottom — Accept/Reject/Edit
├── EditScreen                  # Inline YAML editor
│   ├── YAMLEditor              # Syntax-highlighted TextArea
│   └── ValidationBar           # Live YAML parse status
└── SummaryScreen               # Session summary — what was approved/rejected
```

#### Diff Logic

Use `ruamel.yaml` to:
1. Load both versions of a lesson entry (original vs modified)
2. `ruamel.yaml.comments.CommentedSeq` → Python comparison
3. Render diff using `rich.syntax.Syntax` with two themes (green additions, red deletions)
4. For line-level diffs: use `difflib.unified_diff` on YAML-dumped strings

#### Approval Workflow

```
Load proposed_lessons.yaml → Parse all entries → Filter by modified/new
  → User reviews each in TUI → Approve / Reject / Edit
    → Approved → written to soul.yaml 'lessons' section via SoulDistiller
    → Rejected → left in proposed_lessons.yaml (marked as reviewed)
    → Edited → re-parsed, presented again, then approve/reject
```

### 2.4 Soul Distiller Code — Integration Point

The `SoulDistiller` in `src/omega/oracle/soul_distiller.py` (400 lines) already provides:

```python
# Full API surface for TUI integration:
soul_path = soul_path.with_suffix(".yaml.tmp")  # Atomic write pattern
soul_path.write_text(content)
os.replace(str(tmp_path), str(soul_path))
```

The TUI's approval callback should:
1. Read approved L3 lesson from TUI
2. Create a `DistillationEntry` with level="L3", content=principle
3. Call `distiller.append_to_soul(entity_name, {"L3": entry})`
4. Remove the entry from `proposed_lessons.yaml` (or mark as `status: approved`)

**No SoulDistiller changes needed** — the existing API supports the full approval pipeline.

### 2.5 Staging Gate TUI Effort

| Component | Effort | Dependencies |
|-----------|--------|-------------|
| Install `textual`, `ruamel.yaml` | 0.5h | Pip in `.venv` |
| ProposedLessonsLoader (multi-format reader) | 3h | ruamel.yaml, format auto-detection |
| YAML Diff Engine | 3h | ruamel.yaml comparison, difflib, rich.syntax |
| TUI LessonListScreen | 4h | textual ListView, DataTable, key bindings |
| TUI DiffViewScreen | 3h | textual Static + rich renderables |
| TUI Approval Workflow | 3h | Atomic soul.yaml writes, status tracking |
| Session Summary + persistence | 2h | Save review state per session |
| Tests (textual + unit) | 3h | textual.pilot for integration tests |
| **Subtotal** | **~21.5h** | ~2.5-3 engineering days |

**Recommended simplification**: If the soul.yaml v6.1 migration runs first (format convergence), the multi-format reader drops from 3h → 1h, reducing total to **~19.5h**.

---

## §3 M21 GATE INTEGRITY ASSESSMENT

### 3.1 Current Contract Test Coverage

| Test File | Tests | What It Covers | Status |
|-----------|-------|----------------|--------|
| `tests/test_contract_m21.py` | 4 | `GenerateResult` returns proper dataclass, `OracleResponse` contract boundaries, negative test for type drift | ✅ GOOD FOUNDATION |
| `tests/test_somatic_state.py` | 3 test classes | Cvar values exist (`config.somatic.*`, `config.dreaming.*`, `config.symmetry.*`) | ⚠️ CVARS ONLY — no implementation tests |
| `tests/test_locks.py` | 3 | `ResourceGuard` lock/unlock, re-entrance | ⚠️ USES MOCK, not real `isinstance` checks per M21 |
| `tests/test_resource_guard.py` | ❌ **DOES NOT EXIST** | N/A | ❌ GAP |
| `tests/sovereign_stress_test.py` | 1 test | `ResourceGuard` concurrency | ⚠️ Integration test, not M21 contract |

### 3.2 Required New Contract Tests for UnifiedStateManager

Per M21 ("Every code path returning a typed result MUST be exercised by at least one test that validates the return type"):

| Test | Entity Under Test | Contract to Validate | Priority |
|------|-------------------|---------------------|----------|
| `test_usm_capture_returns_somaticstatekey` | `UnifiedStateManager.capture()` | Returns `SomaticStateKey` (not `bytes`, not `None`) | 🔴 HIGH |
| `test_usm_restore_returns_bool` | `UnifiedStateManager.restore()` | Returns `bool` (success/failure) | 🔴 HIGH |
| `test_ssk_from_bytes_roundtrip` | `SomaticStateKey.from_bytes()` | Round-trip: key → bytes → key preserves all fields | 🟡 MEDIUM |
| `test_ssk_validate_raises_on_corrupt` | `SomaticStateKey.from_bytes()` | Raises `ValueError` on truncated/corrupt data | 🟡 MEDIUM |
| `test_usm_list_snapshots_returns_list` | `UnifiedStateManager.list_snapshots()` | Returns `List[SomaticStateKey]` | 🟢 LOW |
| `test_usm_prune_removes_oldest` | `UnifiedStateManager.prune()` | Verifies max_snapshots constraint | 🟡 MEDIUM |
| `test_cas_store_returns_hash` | `CASBlobStore.put()` | Returns `str` (blake2b hex digest) | 🔴 HIGH |
| `test_cas_load_returns_bytes` | `CASBlobStore.get()` | Returns `Optional[bytes]` | 🔴 HIGH |

### 3.3 ResourceGuard Contract Test Gap

Current `ResourceGuard` tests in `test_locks.py` use `MagicMock(spec=ResourceGuard)` — which per M21 violates the "No mock-based tests that mask type mismatches" rule. A dedicated `test_resource_guard.py` with real `isinstance(result, ResourceGuard)` checks is needed:

```python
# Required M21 contract test for ResourceGuard
def test_resource_guard_lock_returns_contextmanager():
    """M21: ResourceGuard.lock() returns an async context manager.
    The return type must support __aenter__ and __aexit__ protocol.
    """
    guard = ResourceGuard(total_capacity=2)
    mgr = guard.lock(weight=1)
    assert hasattr(mgr, '__aenter__'), "lock() must return async context manager"
    assert hasattr(mgr, '__aexit__'), "lock() must return async context manager"
```

### 3.4 Testing Strategy for New Components

```
Unit Tests (fast, no model):
├── SomaticStateKey.from_bytes() / to_bytes() round-trip
├── CASBlobStore.get() / put() with temp directory
├── UnifiedStateManager.list_snapshots() / prune()
└── ProposedLessonsLoader.parse_all_formats()

Integration Tests (with model):
├── SomaticStateSerializer.capture() → restore() round-trip
│   └── Requires: NativeGGUFProvider with real model
│   └── Pattern: Lock ResourceGuard, load small model, capture, restore
├── UnifiedStateManager.capture() → index → restore()
└── Staging Gate TUI: textual.pilot for screen flow

Contract Tests (M21):
├── Every public method returns documented type
├── Every error path raises typed OmegaError
└── Every dataclass has isinstance() check
```

---

## §4 DEPENDENCY CHAIN ANALYSIS

### 4.1 Dependency Graph

```
Strike 1: Physical Purge
├── Disk space recovery
├── soul_validator.py v6.1 update ← P2 dependency (P2's #1 finding)
└── soul.yaml v6.1 migration (23+ entities)
    │
    ▼
Strike 2: UnifiedStateManager
├── No dependency on Strike 1 completion (separate concern)
├── ZONEID_SOMATIC already defined ✅
├── cvars already registered ✅
└── Llama-cpp-python v0.3.28 with ctypes ✅
    │
Strike 3: Staging Gate TUI
├── DEPENDS ON: soul_validator.py v6.1 update (P2)
├── DEPENDS ON: soul.yaml v6.1 migration (or format-agnostic reader)
├── DEPENDS ON: pip install textual, ruamel.yaml
└── Uses: SoulDistiller API (no changes needed)
    │
    └── Both Strikes 2 & 3 → can build in parallel
```

### 4.2 Cross-Pillar Dependencies

| Dependency | From | To | Criticality | Notes |
|------------|------|----|-------------|-------|
| `soul_validator.py` v6.1 | P2 | P3 (Strike 3) | 🔴 BLOCKING | TUI assumes consistent YAML format |
| Disk space for model state | P1 | P3 (Strike 2) | 🟡 MEDIUM | Somatic snapshots need ~256MB+ per entity |
| `config/somatic/*` cvars | P3 | All Phase C | 🟢 NONE | Already registered (P3 pre-work done) |
| ZONEID_SOMATIC constant | P3 | All | 🟢 NONE | Already defined |
| `textual` + `ruamel.yaml` install | P3 (self) | Strike 3 | 🔴 BLOCKING | Must be installed before any code |
| MemoryStore provider chain | P2 | P3 (Strike 2) | 🟢 NONE | Separate storage — no coupling |

### 4.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| `llama_state_get_data()` returns empty on non-loaded model | Medium | High | Guard: verify model is loaded before capture |
| `llama_state_set_data()` expects exact same model params | High | Critical | SomaticStateKey validation before restore |
| Proposed lessons format chaos breaks TUI parser | High | Medium | Build multi-format reader (Option C) or batch-convert first (Option B) |
| Textual version compatibility with Python 3.13 | Low | Medium | Pin `textual>=0.52.0` tested on 3.13 |
| Disk full during snapshot write | Low | High | Check `config.somatic.memory_budget_mb` before write; verify disk space |
| ctypes SIGSEGV kills Python on raw bindings | Medium | Critical | Default to safe mode (`Llama.save_state()`), isolate raw ctypes behind process boundary |
| **proposed_lessons.yaml file locking race** | Medium | Medium | Lock files before reading/writing; SoulDistiller already uses `fcntl.flock(LOCK_EX)` |

---

## §5 EFFORT ESTIMATION

### 5.1 Component-by-Component Effort

| Component | Hours | Engineering Days | Dependencies | Builder |
|-----------|-------|-----------------|--------------|---------|
| **Strike 2: UnifiedStateManager** | | | | |
| Install python deps (textual, ruamel.yaml) | 0.5 | 0.06 | Pip in `.venv` | P3 |
| SomaticStateKey dataclass | 1.0 | 0.13 | `struct`, ZONEID_SOMATIC | P3 |
| SomaticStateSerializer (safe mode) | 3.0 | 0.38 | `llama_state_get_data()`/`set_data()` | P3 |
| SomaticStateSerializer (raw ctypes, optional) | 3.0 | 0.38 | `_llama_copy_state_data()` + process isolation | P3 |
| CASBlobStore (blake2b, atomic writes) | 2.0 | 0.25 | `hashlib.blake2b` | P3 |
| CAS Index (JSONL append, prune) | 1.5 | 0.19 | Append-only log | P3 |
| UnifiedStateManager orchestration | 3.0 | 0.38 | Above components | P3 |
| Contract tests (M21) | 2.0 | 0.25 | Above components | P3 |
| Integration tests | 1.5 | 0.19 | Real model + ResourceGuard | P3 |
| **Strike 2 Subtotal** | **~17.5h** | **~2.2 days** | | |
| | | | | |
| **Strike 3: Staging Gate TUI** | | | | |
| Install textual + ruamel.yaml | 0.5 | 0.06 | `pip install` | P3 |
| ProposedLessonsLoader (multi-format) | 3.0 | 0.38 | `ruamel.yaml` | P3 |
| YAML Diff Engine | 3.0 | 0.38 | `difflib` + `rich.syntax` | P3 |
| TUI LessonListScreen | 4.0 | 0.50 | `textual` ListView/DataTable | P3 |
| TUI DiffViewScreen | 3.0 | 0.38 | `textual` + `rich` renderables | P3 |
| TUI Approval Workflow | 3.0 | 0.38 | SoulDistiller API | P3 |
| Session Summary + persistence | 2.0 | 0.25 | Save approval state | P3 |
| Tests (textual + unit) | 3.0 | 0.38 | `textual.pilot` | P3 |
| **Strike 3 Subtotal** | **~21.5h** | **~2.7 days** | | |
| | | | | |
| **M21 Contract Tests** | | | | |
| ResourceGuard contract tests | 1.0 | 0.13 | `test_resource_guard.py` creation | P3 |
| USM contract tests (included above) | 2.0 | 0.25 | Already counted | P3 |
| TUI contract tests (included above) | 3.0 | 0.38 | Already counted | P3 |
| **M21 Subtotal (new only)** | **1.0h** | **0.13 days** | | |
| | | | | |
| **TOTAL** | **~40h** | **~5 days** | | |
| **PARALLEL ADJUSTMENT** | **~26h** | **~3.25 days** | Strikes 2 & 3 can run in parallel | |

### 5.2 Sprint Phasing Recommendation

```
Week 1 (Mon-Wed): Strike 2 — UnifiedStateManager
├── Day 1: SomaticStateKey + SomaticStateSerializer (safe mode)
├── Day 2: CASBlobStore + CAS Index + UnifiedStateManager orchestration
└── Day 3: Tests + integration testing

Week 1 (Wed-Fri): Strike 3 — Staging Gate TUI
├── Day 1 (parallel with Strike 2 Day 1-2): ProposedLessonsLoader + YAML Diff Engine
├── Day 2 (parallel with Strike 2 Day 3): TUI screens (LessonList + DiffView)
└── Day 3: Approval workflow + tests

Week 1-2 Overflow: Integration + M21 contract tests
└── Cross-component tests, ResourceGuard contract tests, bug fixes
```

### 5.3 Critical Path Items

1. **🔴 [P0] Install `textual` + `ruamel.yaml`** — Must happen immediately, blocks all of Strike 3
2. **🔴 [P0] Update `soul_validator.py` to v6.1 schema** — P2's work, blocks TUI from assuming consistent format
3. **🔴 [P0] Batch-convert broken proposed_lessons.yaml files** — `roc_racoon` (32KB YAML string literal) and `makali` (YAML string literal) must be fixed or the TUI will crash on them
4. **🟡 [P1] Decide SomaticState serialization strategy**:
   - **Safe mode** (default): `Llama.save_state()`/`load_state()` — safer, no SIGSEGV risk
   - **Raw ctypes**: `_llama_copy_state_data()`/`_llama_set_state_data()` — faster but risks process death
   - **File mode**: `llama_state_save_file()`/`llama_state_load_file()` — simplest, direct-to-disk
5. **🟡 [P1] ResourceGuard contract upgrade** — Add real `isinstance` checks per M21

---

## §6 CONTINUITY NOTES

### 6.1 What Must Be Done Before Coding Starts

1. **Install dependencies** (in `.venv`):
   ```bash
   source .venv/bin/activate && pip install 'textual>=0.52.0' 'ruamel.yaml>=0.18.0'
   ```

2. **Fix broken proposed_lessons.yaml files** — 3 files have YAML string literals that crash any YAML parser:
   - `data/entities/roc_racoon/proposed_lessons.yaml` (32KB, worst case)
   - `data/entities/makali/proposed_lessons.yaml`
   - `data/entities/pillar_p1/proposed_lessons.yaml`
   Fixing requires extracting the embedded YAML string content and re-writing as proper `proposals:` format.

3. **Update `soul_validator.py` to v6.1 schema** — P2's key deliverable. The v6.1 schema expects:
   ```yaml
   proposals:
     - id: unique-id
       l1_narrative: "What happened?"
       l2_insight: "What does this mean?"
       l3_universal_principle: "What is the timeless truth?"
       session: "session-id"
       tags: ["tag1", "tag2"]
   ```

4. **Read the SomaticState blueprint** — `docs/research/R_SOMATIC_STATE_SOTA.md` (45-page technical spec) and `docs/research/R50_SOMATIC_STATE_DESIGN.md` for the binary header design.

5. **Review Phase C Master Spec** — `docs/strategy/PHASE_C_MASTER_SPEC_VERITY.md` §3.1 for detailed implementation notes on SomaticState stage 1.

### 6.2 Engineering Recommendations for Ma'at/Kali

1. **Parallel execution is safe**: Strikes 2 (UnifiedStateManager) and 3 (Staging Gate TUI) share zero code dependencies. They can be built by independent agents in parallel, reducing calendar time from ~5 days to ~3.25 days.

2. **Prefer safe-mode SomaticState**: The `config.somatic.ctypes_safe_mode` cvar defaults to `True` for good reason. Raw ctypes `_llama_copy_state_data` can SIGSEGV the entire Python process. Build the first iteration using `Llama.save_state()`/`load_state()`. Raw ctypes can be added later as a performance optimization behind a cvar flag, with process isolation (separate subprocess) to contain crashes.

3. **SomaticState file-level API is the simplest path**: `llama_state_save_file()` / `llama_state_load_file()` write directly to disk — no in-memory byte shuffling. This is the fastest path to a working implementation. The CAS layer wraps these by managing file paths rather than byte arrays.

4. **TUI format chaos demands a decision**: Ma'at must decide between Option A (multi-format reader — TUI works before migration) and Option B (v6.1-only — TUI waits for migration). Recommendation: **Option C** — Build TUI for v6.1 only BUT provide a batch conversion script (`python -m omega.tools.convert_proposed_lessons`) that auto-detects and converts all 3 legacy formats to v6.1. Run the converter first, then deploy the TUI.

5. **ResourceGuard contract test gap is small but important**: Creating `tests/test_resource_guard.py` with real `ResourceGuard` instances (not mocks) takes ~1 hour and closes the M21 coverage gap. Do this in parallel with Strikes 2/3.

6. **Risk mitigation for ctypes bindings**: The Phase C spec (Carmack Hard Block 1) notes that ctypes CDLL segfaults kill the Python process. Build the SomaticStateSerializer to catch `SystemError`/`RuntimeError` on the ctypes path and fall back to cold-start if the model cannot be serialized. Document this in the `save()` method docstring.

### 6.3 Remaining Gaps After Epoch I

| Gap | Owner | Resolution |
|-----|-------|------------|
| CAS-based Qdrant coordinate mapping | Epoch II | Strike 7 — Spatial-Semantic Geometry |
| Process-isolated ctypes for raw speed | Deferred | Requires subprocess with IPC — beyond Epoch I scope |
| `proposed_lessons.yaml` auto-distillation from TUI approvals | P3 (Strike 3) | Will be the TUI's approval callback |
| ResourceGuard `test_resource_guard.py` | P3/M21 | 1-hour task, can be done in Epoch I |

---

## §7 VERDICT

| Component | Readiness | Verdict |
|-----------|-----------|---------|
| **UnifiedStateManager (Strike 2)** | 🟢 **GO** | All ctypes verified, ZONEID_SOMATIC ready, cvars registered. 17.5h build estimate. |
| **Staging Gate TUI (Strike 3)** | 🟡 **CONDITIONAL GO** | Dependencies not installed + format chaos. Estimate 21.5h. Reduce to 19.5h by running batch format conversion first. |
| **M21 Contract Tests** | 🟢 **GO** | Foundation solid. 1h for ResourceGuard gap. New USM contract tests included in Strike 2 estimates. |
| **Overall Epoch I** | **🟢 GO with conditions** | Parallel execution (Strikes 2+3 concurrently) → ~3.25 engineering days. Critical path: install deps first, run proposed_lessons conversion, then all builds proceed in parallel. |

---

*⬡ OMEGA ⬡ P3 ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ EPOCH-I-ASSESSMENT*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
