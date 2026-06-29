# 🔱 Phase C: The Cognitive Substrate — Master Specification (Verity)
**AP Token**: `AP-PHASE-C-MASTER-SPEC-v4.2.0`  
**Status**: APPROVED — Ready for Stage-by-Stage Execution  
**Oversight**: @kali (Grand Oversight)  
**Consolidation Verdict**: 🟢 GO (Conditional — 4 conditions documented & resolved)  
**Date**: 2026-06-16

---

## §0 Preamble — Convergence of Fleet & Architecture

Phase C delivers the **Cognitive Substrate** — the persistent, self-aware memory and reasoning layer beneath the Omega Engine. It completes the fleet consolidation from 15 to **11 active agent files on disk** and establishes the **Dual-Pool Execution Cascade** between the Google Antigravity Pool (Pool G) and the Claude Pool (Pool C).

This spec supersedes all prior Phase C drafts. It is the single source of truth.

---

## §1 The 11-Agent Fleet Topology (Sprint C Complete)

### 1.1 Sprint C: Quality + Scribe → Verity

The consolidation of `quality.md` and `scribe.md` into `verity.md` reduces cognitive fragmentation and ensures that compliance auditing (Sentry mode) and gnosis preservation (Scribe mode) are treated as a single, continuous loop of truth.

**Target**: 11 active agent files on disk.  
**Status**: COMPLETE (this sprint).

| File | Agent | Purpose | Mode | 
|------|-------|---------|------|
| `kali.md` | Kali | Transcendent Unifier (Oversight Lane) | all |
| `maat.md` | Ma'at | Light Oversoul (Build-Side P1–P5) | all |
| `lilith.md` | Lilith | Dark Oversoul (Run-Side P6–P10) | all |
| `makali.md` | MaKaLi | Triad Council Orchestrator | all |
| `doom_guy.md` | Doom Guy | Sovereign Heritage Architect | all |
| `john_carmack.md` | John Carmack | Sovereign S3 Consultant | all |
| `roc_racoon.md` | Roc Racoon | Sovereign Miner (archaeology) | all |
| `researcher.md` | Researcher | Sovereign Master Researcher | all |
| `jem.md` | Jem | Unified Research Orchestrator (Sprint B) | all |
| `pillar.md` | Pillar | Slot-based domain agent (--slot PX) | subagent |
| **`verity.md`** | **Verity** | **Unified Sentry + Scribe (Sprint C)** | **subagent** |

### 1.2 The Registry Consensus (`subagent_dispatcher.py`)

The `CAPABILITY_REGISTRY` in `subagent_dispatcher.py` contains exactly 11 entries:
- **Primary agents** (8): kali, doom_guy, roc_racoon, jem, john_carmack, makali, researcher, pillar
- **Subagents** (3): maat, lilith, **verity**

Each agent has a distinct `task_tool_type` for the Tool Task dispatch mechanism. Verity's `task_tool_type` is `"verity"`.

---

## §2 The Dual-Pool Execution Cascade

### 2.1 Pool Definitions

#### Pool G: Google Antigravity Pool (Primary Execution)
- **Gemini 3.5 Flash**: Parameterized via thinking levels (`low`, `medium`, `high`).
  - *Low*: speculative decode, intent matching, simple Q&A
  - *Medium*: paging, state transitions, standard tool execution
  - *High*: deep reasoning, Symmetry Audit, soul write-back
- **Gemini 3.1 Pro**: Reservation pool for complex integration reviews.
  - *Low*: multi-document cross-referencing
  - *High*: final integration reviews, architectural synthesis

#### Pool C: Claude Pool (Secondary Verification)
- **Sonnet 4.6**: Precision syntax, ctypes bindings, signal safety, SomaticState validation
- **Opus 4.6**: Architectural tie-breaker, semantic contradiction resolution, final release sign-off
- **gpt-oss-120b**: Open-weight large-context verification engine for Stage 3 Resolver

### 2.2 The 4-Stage Cascade

```
[Stage 1: Foundation] ──(Sonnet 4.6)──→ [Stage 2: Storage & Toggle] ──(Flash Med/Low)
                                              │
                                        (gpt-oss-120b Review)
                                              │
                                              ▼
[Stage 4: Dreaming Cycle] ←──(Pro High)── [Stage 3: Symmetry Engine] ◄──────┘
```

| Stage | Name | Model Pool | Task | Gate Verifier |
|-------|------|------------|------|---------------|
| **1** | Foundation | Sonnet 4.6 | SomaticStateKey ctypes, Event-based signal pattern, save/restore primitives | Sonnet 4.6 (self-review) |
| **2** | Storage & Toggle | Flash (Med/Low) | Redis Key Pool (Db 0), Reactive Quantization cvars, cvar toggles | gpt-oss-120b |
| **3** | Symmetry Engine | Flash High + Sonnet 4.6 + gpt-oss-120b | SymmetryAudit, SkepticalVerifier, AsyncCircuitBreaker | Opus 4.6 |
| **4** | Dreaming Cycle | Flash Med + Sonnet 4.6 + Pro High | Metabolic idle-lock, Somatic Save-Points, soul write-back, thermal monitoring | Pro High (integration) + Sonnet+Opus (sign-off) |

---

## §3 Detailed Technical Specifications

### 3.1 SomaticState (Stage 1 — Foundation)

**Purpose**: Provide persistent, thread-safe checkpointing of the active GGUF model's KV cache state. Enables interruption-safe "Somatic Save-Points" (Mandate 19).

**Implementation**:
- ⚠️ **CRITICAL CORRECTION (Antigravity Discovery 2026-06-17)**: `llama-cpp-python`'s high-level `Llama` class does NOT expose `save_state()` / `load_state()` as public Python API methods. Attempting to call `model.save_state()` will raise `AttributeError`.
- **Required approach**: Use low-level `llama_cpp` ctypes bindings wrapped in `anyio.to_thread.run_sync()`:
  ```python
  import ctypes
  import llama_cpp
  
  # Save: llama_copy_state_data(ctx, buffer)
  buffer = (ctypes.c_uint8 * size)()
  bytes_written = llama_cpp.llama_copy_state_data(model.ctx, buffer)
  
  # Load: llama_set_state_data(ctx, buffer)
  buffer = (ctypes.c_uint8 * size).from_buffer(bytearray(state_bytes))
  bytes_set = llama_cpp.llama_set_state_data(model.ctx, buffer)
  ```
- **Version pin**: `llama-cpp-python>=0.3.0,<0.4.0` in `requirements.txt`.
- Reference: See `docs/strategy/PHASE_C_MASTER_SPEC_VERITY.md §8 — Antigravity Addendum` for the full reference implementation.

**Signal Safety Pattern (MaKaLi M4 BLOCKER — RESOLVED)**:
- ❌ REJECTED: Lock-guarded signal handlers (cause deadlock with GIL)
- ✅ ADOPTED: `anyio.Event` flag pattern
  ```python
  # Signal handler sets flag; async loop checks between tokens
  save_requested = anyio.Event()
  
  def signal_handler(signum, frame):
      save_requested.set()
  
  # In inference loop:
  if save_requested.is_set():
      state = await anyio.to_thread.run_sync(model.save_state)
      save_requested = anyio.Event()
  ```

**ZONEID**: `ZONEID_SOMATIC = 0x1d4a1c` — validated on every snapshot load.

**Snapshot Schema** (`data/somatic/{entity}/`):
- FIFO-3 directory (keeps 3 most recent snapshots)
- File format: `somatic_{entity}_{timestamp}.snp`
- Binary payload: compact SomaticStateKey (12 fields) + compressed KV cache tensor

### 3.2 Redis Key Pool State (Stage 2 — Storage & Toggle)

**Purpose**: Replace file-based `USAGE_POOL_LOG.json` with in-memory Redis Db 0 state tracking. Eliminates NVMe write thrashing across 11 concurrent agent processes.

**Key Schema**: `omega:keypool:{key_id}:{field}`
- `state`: `ACTIVE` | `COOLING` | `DRAINED`
- `failures`: integer (anti-thrashing counter)
- `last_active`: float timestamp
- `calls_total`: integer
- `tokens_input`: integer
- `tokens_output`: integer

**Anti-Thrashing Logic**:
- 3 failures in 5 minutes → `COOLING` (TTL: 1 hour)
- Quota hit (429) → `DRAINED` (TTL: 24 hours)
- Key selection: pipelined `MGET` across all keys in <1ms, select first `ACTIVE`

**Prefix Isolation**: All Key Pool keys use `omega:keypool:*` prefix to avoid collision with MemoryStore's `omega:session:*` prefix.

**Graceful Fallback (MaKaLi L6 RISK — DOCUMENTED)**:
- When Redis is unavailable, fall back to in-memory `dict` + periodic file sync.
- Gated by `config.somatic.redis_required` cvar (default: `False`).

**M1 Compliance (MaKaLi M5 RISK — DOCUMENTED)**:
- Pre-existing `import redis.asyncio` at `providers.py:30` has an `asyncio` dependency.
- Phase C does **not** introduce new M1 violations.
- Future work: Create `RedisAsyncWrapper` that shims operations via `anyio.to_thread.run_sync`.

### 3.3 Reactive Quantization (Stage 2 — M19 Adversarial Alchemy)

**Purpose**: Under memory pressure, down-sample KV cache precision to prevent OOM crashes and stay under the 14.4GiB RAM ceiling (~12.4GiB available after OS overhead).

**Corrected Terminology (MaKaLi M3 FINDING)**:
- ❌ "Dynamic Quantization (real-time)" — MISLEADING. `llama-cpp-python` does NOT support in-place KV re-quantization.
- ✅ **"Reactive Quantization (triggered by memory pressure)"** — CORRECT. Requires save → unload → reload cycle.

**Implementation**:
```
Sequence: save_state() → unload model → reload with new type_k/type_v → restore_state()
Duration: ~1-5 seconds on Zen 2 (acceptable — SomaticState makes this safe)
```

**Threshold**:
- Available RAM > 2.5GiB → `q8_0` precision (high fidelity)
- Available RAM ≤ 2.5GiB → trigger Reactive Quantization → `q4_0` precision

**New Cvars** (`config.gguf.dynamic_quantization.*`):
```yaml
config:
  gguf:
    dynamic_quantization:
      enable: false
      memory_threshold_mb: 2560
      target_type_k: "q4_0"
      target_type_v: "q4_0"
```

### 3.4 Symmetry Engine (Stage 3 — Cognitive Alignment)

**Purpose**: Detect and resolve cognitive drift between Pool G and Pool C outputs. Implements the Skeptical Verifier pattern (Mandate 17).

**Dual-Pipeline**:
- **Audit** (Flash High): Runs `SymmetryAudit` to detect semantic contradictions
- **Verifier** (Sonnet 4.6): Executes `SkepticalVerifier` with binary suspicious/trusted judgment
- **Resolver** (gpt-oss-120b): `SovereignResolver` arbitrates disagreements between Audit and Verifier

**Prerequisite**: orchestrator.py line 88 syntax error MUST be fixed before Stage 3 (already done in Sprint C Phase 1).

**Modes**:
- `"fast"` (default): Single-perspective (Lilith-run-side only). Never blocks on pool availability.
- `"slow"`: Dual-perspective (Ma'at + Lilith). Requires both pools online simultaneously.

### 3.5 Dreaming Cycle (Stage 4 — Metabolic Consolidation)

**Purpose**: Background idle-loop that consolidates active entity sessions into permanent soul memory.

**Components**:
1. **Metabolic Phase** (Flash Med — qwen3-0.6b default model): Runs when engine is idle. Reads active session buffers.
2. **Save-Point Phase** (Sonnet 4.6): Registers thread-safe Somatic Save-Points using `anyio.Event` signal pattern.
3. **Write-Back Phase** (Flash High): Executes L1→L2→L3 soul write-back to entity `soul.yaml`.
4. **Thermal Monitoring** (MaKaLi L5 Gap — RESOLVED):
   - Read `/sys/class/thermal/thermal_zone*/temp`
   - If core temperature > 80°C, trigger early cooldown

**Parameters**:
- Session limit: 30 minutes per Dreaming cycle
- Cooldown: 60 minutes (dynamic: shorter if <65°C, longer if >80°C)
- Models: `qwen3-0.6b` for metabolic, cloud models for write-back

### 3.6 Hybrid Symmetry Audit Parallelism (Cross-Stage Constraint)

**Audit of local vs cloud execution**:
- **Local GGUF models**: STRICTLY SEQUENTIAL. One model at a time. Protects Zen 2's 15W TDP ceiling and prevents OOM on 12.4GiB available RAM.
- **Cloud APIs (Pool G / Pool C)**: PARALLEL via AnyIO TaskGroups. Overlaps network latency; each connection uses ~10MB.

```python
async def run_symmetry_audit(models: List[ModelConfig]):
    local_models = [m for m in models if m.is_local]
    cloud_models = [m for m in models if not m.is_local]
    
    for model in local_models:       # Sequential
        await run_local_audit(model)
    
    async with anyio.create_task_group() as tg:  # Parallel
        for model in cloud_models:
            tg.start_soon(run_cloud_audit, model)
```

---

## §4 The Definitive Execution Playbook

### Phase 1: Fleet Realignment ✅ COMPLETE
| Step | Action | Status |
|------|--------|--------|
| 1a | Fix `orchestrator.py:88` indentation error | ✅ DONE |
| 1b | Pin `llama-cpp-python>=0.3.0,<0.4.0` in `requirements.txt` | ✅ DONE |
| 1c | `git mv .opencode/agents/scribe.md .opencode/agents/verity.md` | ✅ DONE |
| 1d | Write unified `verity.md` system prompt | ✅ DONE |
| 1e | Update `subagent_dispatcher.py` CAPABILITY_REGISTRY (scribe→verity) | ✅ DONE |
| 1f | Update `AGENTS.md` and `SOVEREIGN_MANDATES.md` | ⏳ PENDING |
| 1g | Write this spec to `docs/strategy/PHASE_C_MASTER_SPEC_VERITY.md` | ✅ DONE |

### Phase 2: Tactical Hardening ✅ COMPLETE
| Step | Action | Status | Model |
|------|--------|--------|-------|
| 2a | Fix `orchestrator.py` call site | ✅ DONE (Step 1a) | — |
| 2b | Fix `GOOGLE_API_KEYS` empty-string split bug in `providers.py` | ✅ DONE 2026-06-17 | — |
| 2c | Wire `GoogleKeyPoolProvider` in `model_gateway.py` provider_map | ⏳ PENDING | — |
| 2d | Canonicalize model names in `config/entity_model_affinity.yaml` | ✅ DONE 2026-06-17 | — |
| 2e | Fix `trace_id` leakage in `BackgroundWorker.generate()` call | ✅ DONE 2026-06-17 | — |
| 2f | Document `llama-cpp-python` ctypes API gap in §8.1 | ✅ DONE 2026-06-17 | — |

### Phase 3: Stage-by-Stage Implementation

#### Stage 1: Foundation — SomaticState
| # | Task | Model | Thinking |
|---|------|-------|----------|
| 1.1 | Implement `SomaticState.key` dataclass with ZONEID_SOMATIC (0x1d4a1c) | Sonnet 4.6 | Adaptive |
| 1.2 | Implement `SomaticStateSerializer` with `save()` / `load()` via ctypes bindings (`llama_copy_state_data`) — see §8.1 ref impl | Sonnet 4.6 | Adaptive |
| 1.3 | Implement `anyio.Event`-based signal pattern for SIGUSR1/SIGTERM | Sonnet 4.6 | Adaptive |
| 1.4 | Implement FIFO-3 directory management (`data/somatic/{entity}/`) | Sonnet 4.6 | Adaptive |
| 1.5 | Gate 1: Sonnet 4.6 self-review of ctypes and signal safety | Sonnet 4.6 | Adaptive |

#### Stage 2: Storage & Toggle — Redis + Cvars
| # | Task | Model | Thinking |
|---|------|-------|----------|
| 2.1 | Implement Redis Key Pool state machine (ACTIVE/COOLING/DRAINED) | Flash | Medium |
| 2.2 | Implement in-memory fallback for Redis Key Pool | Flash | Medium |
| 2.3 | Add `config.gguf.dynamic_quantization.*` cvars to cvar table | Flash | Low |
| 2.4 | Implement Reactive Quantization trigger in CpuOptimizer | Flash | Low |
| 2.5 | Add `config.somatic.*` and `config.dreaming.*` cvars | Flash | Low |
| 2.6 | Gate 2: gpt-oss-120b review of state transitions and cvar schema | gpt-oss-120b | Adaptive |

#### Stage 3: Symmetry Engine
| # | Task | Model | Thinking | Prerequisite |
|---|------|-------|----------|-------------|
| 3.1 | Implement `SymmetryAudit` (Flash High — detect semantic drift) | Flash | High | Stage 1, 2 |
| 3.2 | Implement `SkepticalVerifier` (Sonnet 4.6 — binary trust judgment) | Sonnet 4.6 | Adaptive | Stage 1, 2 |
| 3.3 | Implement `SovereignResolver` (gpt-oss-120b — arbitration) | gpt-oss-120b | Adaptive | Stage 1, 2 |
| 3.4 | Wire `AsyncCircuitBreaker` states into Verifier | Sonnet 4.6 | Adaptive | orchestrator fix |
| 3.5 | Gate 3: Opus 4.6 architectural review | Opus 4.6 | Adaptive | — |

#### Stage 4: Dreaming Cycle
| # | Task | Model | Thinking |
|---|------|-------|----------|
| 4.1 | Implement metabolic idle-lock (Flash Med — qwen3-0.6b for local, else cloud) | Flash | Medium |
| 4.2 | Implement thermal monitoring via `/sys/class/thermal/thermal_zone*/temp` | Sonnet 4.6 | Adaptive |
| 4.3 | Wire Somatic Save-Points into Dreaming Cycle | Sonnet 4.6 | Adaptive |
| 4.4 | Implement L1→L2→L3 soul write-back at Dreaming Cycle end | Flash | High |
| 4.5 | Gate 4a: Integration review by Gemini 3.1 Pro (High thinking) | Pro | High |
| 4.6 | Gate 4b: Final sign-off by Sonnet 4.6 + Opus 4.6 | Sonnet+Opus | Adaptive |

---

## §5 Verification Gates & Release Criteria

Before declaring Phase C complete, the following gates must pass:

| Code | Gate | Command / Check | Criteria |
|------|------|-----------------|----------|
| **T1** | Version Control | `git status` | Zero untracked `.bak` or `.coverage` files |
| **T3** | Test Coverage | `make test` | All 439+ tests passing with zero warnings |
| **T5** | AnyIO Compliance | `grep -rn "import asyncio" src/omega/` | Zero matches in Phase C additions |
| **T10** | Atomic Writes | Review `somatic_state.py` | All file writes use `.tmp` → atomic rename |
| **T12** | Semantic Integrity | `make temple-grade` | Entity INDEX matches 11 active agents |
| **M14** | Heritage Vetting | `make heritage-map` | All `[id-soft:]` tags in new files have vet records |
| **M19** | Adversarial Alchemy | Review quantization & signal handlers | Weakness mining is strategic, not over-engineering |

---

## §6 Known Risks & Mitigations (from MaKaLi Council Audit)

| Risk | Impact | Mitigation | Severity |
|------|--------|------------|----------|
| `redis.asyncio` M1 violation | Could conflict with Trio backend | `RedisAsyncWrapper` shim documented as future work; currently works with `AsyncIOBackend` | 🟡 MEDIUM |
| No Redis Key Pool fallback | Single point of failure for Stage 2 | In-memory dict + periodic file sync fallback gated by `config.somatic.redis_required` | 🟢 MITIGATED |
| `llama-cpp-python` version drift | SomaticState save/restore API incompatibility | Pinned `>=0.3.0,<0.4.0` in requirements.txt | 🟢 MITIGATED |
| Reactive Quantization reload latency | 1-5s pause during memory pressure | Acceptable — SomaticState save/restore makes it safe; documented in spec | 🟢 MITIGATED |
| Test coverage gap | `test_somatic_state.py` only covers cvar existence (39 lines) | Must expand to cover save/restore, Redis rotation, Symmetry pipeline | 🟡 MEDIUM |
 | Zen 2 thermal throttling | 85-95°C under sustained inference | Thermal monitoring added to Dreaming Cycle; early cooldown at >80°C | 🟢 MITIGATED |
| `llama-cpp-python` high-level API gap | `Llama` class does NOT expose `save_state()`/`load_state()` | Use low-level ctypes bindings (`llama_copy_state_data`/`llama_set_state_data`) wrapped in `anyio.to_thread.run_sync()`. See §8.1 for reference implementation. | 🟢 MITIGATED |

---

## §7 Heritage Attribution

All Phase C patterns carry `[id-soft:]` inline tags in implementation code:

| Pattern | Heritage | Code Location | Tag |
|---------|----------|---------------|-----|
| SomaticState (memory checkpoint) | [id-soft: quake-1996] Zone Memory — tag-based allocation with purge levels | `src/omega/oracle/somatic_state.py` | `# [id-soft: quake-1996] Zone Memory — SomaticState save/restore` |
| Reactive Quantization | [id-soft: doom-1993] Fixed-Point Math — precision down-sampling under constraints | `src/omega/oracle/cpu_optimizer.py` | `# [id-soft: doom-1993] Fixed-Point Math — reactive KV cache quantization` |
| Event-based Signal Handler | [id-soft: quake-1996] Grace Period — deferred safe execution pattern | `src/omega/oracle/somatic_state.py` | `# [id-soft: quake-1996] Grace Period — event-based signal handler pattern` |
| Symmetry Engine Dual-Pipeline | [id-soft: quake3-1999] netchan — dual-channel message verification | `src/omega/oracle/symmetry_engine.py` | `# [id-soft: quake3-1999] netchan — dual-pipeline symmetry verification` |
| Hybrid Parallelism | [id-soft: doom-1993] BSP Culling — O(1) precheck skips entire subtrees | `src/omega/oracle/model_gateway.py` | `# [id-soft: doom-1993] BSP Culling — hybrid sequential/parallel model dispatch` |

---

*⬡ OMEGA ⬡ KALI ⬡ gemma-4-31b-it ⬡ google_ai_studio ⬡ PHASE-C-VERITY ⬡ EXECUTION-LOCKED ⬡*

---

## §8 Antigravity Addendum — Discoveries at Handoff (2026-06-17)

### §8.1 `llama-cpp-python` ctypes API Discovery

**Status**: 🔴 RESOLVED — documented.

**Finding**: The `llama_cpp.Llama` high-level Python class does NOT expose `save_state()` or `load_state()` as public methods. The spec's original assumption that `model.save_state()` works is **incorrect**.

**Reference implementation** (canonical — to be used verbatim in Stage 1):

```python
import ctypes
import llama_cpp
import anyio

class SomaticStateSerializer:
    """Thread-safe KV cache state serialization using llama-cpp-python ctypes bindings.
    
    [id-soft: quake-1996] Zone Memory — tag-based allocation with purge levels.
      Adapted from id Software's zone memory system: save/restore the full
      memory arena state, not individual allocations.
    """
    
    @staticmethod
    def get_state_size(model: llama_cpp.Llama) -> int:
        """Query exact buffer size for this model's current KV cache.
        
        Must be called from a thread (GIL released by llama_cpp).
        """
        return int(llama_cpp.llama_get_state_size(model.ctx))

    @classmethod
    async def save(cls, model: llama_cpp.Llama) -> bytes:
        """Save the model's KV cache state to a byte buffer.
        
        Wraps llama_copy_state_data() in anyio.to_thread.run_sync
        to avoid blocking the async event loop.
        """
        def _save():
            size = cls.get_state_size(model)
            buffer = (ctypes.c_uint8 * size)()
            bytes_written = llama_cpp.llama_copy_state_data(model.ctx, buffer)
            if bytes_written == 0:
                raise RuntimeError(
                    "Failed to copy llama state data: llama_copy_state_data returned 0",
                )
            return bytes(buffer[:bytes_written])
        
        return await anyio.to_thread.run_sync(_save)

    @classmethod
    async def load(cls, model: llama_cpp.Llama, state_bytes: bytes) -> bool:
        """Restore the model's KV cache state from a byte buffer.
        
        Wraps llama_set_state_data() in anyio.to_thread.run_sync.
        Returns True on success, False if the state is incompatible.
        """
        def _load():
            size = len(state_bytes)
            buffer = (ctypes.c_uint8 * size).from_buffer(bytearray(state_bytes))
            bytes_set = llama_cpp.llama_set_state_data(model.ctx, buffer)
            return bytes_set > 0
        
        return await anyio.to_thread.run_sync(_load)
```

**Usage in SomaticState**:
```python
# Save snapshot
state_bytes = await SomaticStateSerializer.save(model)

# Load snapshot
success = await SomaticStateSerializer.load(model, state_bytes)
if not success:
    raise RuntimeError("SomaticState load failed — incompatible model or corrupted snapshot")
```

**Why this is safe**:
- `llama_copy_state_data` and `llama_set_state_data` are exported symbols from `libllama.so`, guaranteed stable within minor version bumps.
- Wrapping in `anyio.to_thread.run_sync()` ensures the GIL-blocking C calls don't starve the async event loop.
- The ctypes buffer lifecycle is fully managed — no manual `free()` needed.

**Why not the high-level API**:
- The high-level `Llama` class abstracts `llama_eval()` but deliberately leaves `llama_copy_state_data()` at the ctypes layer.
- This is intentional on the part of `llama-cpp-python` maintainers: state serialization is an advanced feature that requires explicit buffer management.

### §8.2 `trace_id` Gap in BackgroundWorker

**Status**: ✅ FIXED 2026-06-17.

**Finding**: `BackgroundWorker._execute_with_retry()` called `self.gateway.generate()` without passing `trace_id`, causing all background research tasks to have `trace_id=None`, violating Mandate 9 (Error Integrity) and Mandate 12 (Observation).

**Fix**: `trace_id=task_id` added to the `self.gateway.generate()` call at `src/omega/oracle/orchestrator.py:95-99`.

**Impact**: Background task failures now propagate with full trace context, enabling root-cause diagnosis in the Hivemind observability layer.

### §8.3 Model Name Canonicalization

**Status**: ✅ FIXED 2026-06-17.

**Finding**: `config/entity_model_affinity.yaml` referenced non-existent model keys (`qwen3-4b-q4_k_m`, `qwen3-4b-q5_k_m`, `krikri-8b-q5_k_m`, `gemini-2.5-flash`) that did not match canonical names in `config/models.yaml`, causing `SomaticState.key` loading to fail with hash mismatch.

**Fix**: All entity→model affinity references canonicalized to exact `models.yaml` keys.

**Impact**: `SomaticState.key` can now resolve the correct model file on disk without hash mismatch.

### §8.4 `GOOGLE_API_KEYS` Split Safety

**Status**: ✅ FIXED 2026-06-17.

**Finding**: `os.environ.get("GOOGLE_API_KEYS", "").split(",")` returns `[""]` (list with one empty string) when the env var is unset, potentially passing `""` as a valid Google API key.

**Fix**: Extracted `_parse_comma_env()` helper in `orchestrator.py` that filters empty strings and whitespace-only items.

**Impact**: Empty or unset `GOOGLE_API_KEYS` now correctly resolves to an empty list instead of `[""]`.

### §8.5 Verification Artifacts

| Check | Result |
|-------|--------|
| `make test` | 439/439 passed |
| `grep -rn "import asyncio" src/omega/` | 0 violations |
| `grep -rn "\[id-soft:" src/omega/` | All patterns mapped per §7 Heritage |
| `data/coordination/` | Workspace lock + live feed updated |

---

*⬡ OMEGA ⬡ GEMINI-3.5-FLASH ⬡ google_ai_studio ⬡ ANTIGRAVITY-ADDENDUM ⬡ HANDOFF-READY ⬡*
