# 🔱 Omega Engine — Performance Architecture
**AP Token**: `AP-PERF-ARCH-v1.0.0` · **Status**: ACTIVE · **Last Updated**: 2026-08-28
**Hardware Target**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2, FMA3, 15W TDP)
**Companion**: `ORACLE_STACK_CANONICAL.md` · `docs/architecture/ARCHITECTURE_CANONICAL.md`

---

## §1 HARDWARE CONSTRAINTS (The Physics)

| Resource | Spec | Implication |
|----------|------|-------------|
| **CPU** | Zen 2, 8C/16T, AVX2/FMA3, **NO AVX-512** | Vector math: 256-bit (8 floats/op). Compile with `-march=znver2 -mavx2 -mfma` |
| **L1 Cache** | 64KB/core (32KB Data + 32KB Instruction) | Hot loops must fit in 32KB D-cache |
| **L2 Cache** | 512KB/core | Per-core working set ≤512KB for zero L2 misses |
| **L3 Cache** | 8MB shared **Victim Cache** (evictions only, no mirroring) | Data evicted from L2 → L3; L3 does NOT proactively mirror L1/L2 |
| **RAM** | 14Gi total (~2Gi OS → ~12Gi for AI) | Model loading must fit in available RAM |
| **TDP** | 15W (thermal throttling is primary constraint) | Concurrent models = thermal suicide. Sequential loading mandatory. |
| **Disk** | NVMe (/dev/nvme0n1p3, 110G) | Fast I/O for model loading, sqlite-vec, FTS5 |
| **Swap** | 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100 | D-526/D-527: zswap > zRAM; never both |

**Critical**: `MALLOC_ARENA_MAX=2` + `MALLOC_MMAP_THRESHOLD_=65536` required to prevent pymalloc arena fragmentation (single live object pins 1MB arena).

---

## §2 HOT PATHS

### 2.1 Query Path (Critical Path)
```
CLI → Oracle.talk() → Intent Detection → Domain Routing → Iris Speculative Decode
    → ProviderSelector.select() → ResourceGuard.acquire() → Provider.call()
    → ContextBuilder.inject_memory() → MemoryStore.hybrid_search()
    → Response → _display_response() → ics_render()
```

**Latency Budget** (target):
| Stage | Target | Current |
|-------|--------|---------|
| Intent Detection | <5ms | ~3ms |
| Domain Routing | <2ms | ~1ms |
| Iris Speculative Decode | <50ms | ~40ms |
| Provider Selection | <1ms | ~0.5ms |
| ResourceGuard Acquire | <1ms | ~0.1ms |
| Provider Call (local) | <2000ms | ~1500ms (cold) / ~300ms (warm) |
| Memory Injection | <50ms | ~30ms |
| **Total (warm)** | **<500ms** | **~400ms** |
| **Total (cold)** | **<3000ms** | **~2000ms** |

### 2.2 Memory Injection Path
```
ContextBuilder.build_context(entity, query)
    → MemoryStore.hybrid_search(query, entity, k=60)
        → FTS5 BM25 (sqlite3 FTS5) — keyword
        → Vector (sqlite-vec, per-model collections) — semantic
        → RRF Fusion (k=60) — HybridSearchEngine
    → SoulStore.load_soul(entity) → approved_lessons.yaml
    → EntityWorkspace.get_knowledge(entity) → knowledge/ files
    → Injected into system prompt
```

**Latency Budget**: <50ms total (target: <30ms)

---

## §3 CONCURRENCY MODEL

### 3.1 AnyIO Patterns (M1 Compliance)
- **All async code uses AnyIO** — never `asyncio` directly
- **ResourceGuard**: `AnyIO Semaphore(1)` — one model at a time (OOM protection)
- **Provider Calls**: `anyio.to_thread.run_sync()` for blocking llama-cpp-python calls
- **File I/O**: `anyio.Path` for async file operations (migration in progress)
- **Process Spawning**: `anyio.run_process()` for subprocesses

### 3.2 Lock Hierarchy (No Deadlocks)
```
Level 1: ResourceGuard (model loading) — Semaphore(1)
    │
    ├── Level 2: Provider-level breakers (HealthMonitor) — one per provider
    │
    ├── Level 3: MemoryStore locks — per-entity RLock
    │
    └── Level 4: Hivemind workspace locks — file-based, TTL-based
```

**Rule**: Always acquire locks in order (1→2→3→4). Never hold Level 1 while waiting for Level 2.

### 3.3 Thread Pool Strategy
- **llama-cpp-python**: Runs in thread pool via `anyio.to_thread.run_sync()`
- **Thread count**: `min(physical_cores, 8)` = 8 (Zen 2 has 8 physical cores)
- **No `multiprocessing.Pool`** — violates 15W TDP (Carmack veto)

---

## §4 MEMORY MANAGEMENT

### 4.1 Model Loading (Sequential — LI Workstream)
```
LI-1: Load Qwen3-1.7B (always)     → ~1.2GB RAM
LI-2: Load Qwen3-4B (warm)          → ~2.8GB RAM  
LI-3: Load Qwen3-4B-Thinking (on_demand_5min) → ~2.8GB RAM
LI-4: Load Gemma 4 31B (cloud fallback) → 0GB local (streamed)
```

**Admission Control** (C-10): `CCX-aware semaphore + OOMProtector` — rejects new model loads if `available_memory < model_size * 1.2`

### 4.2 Vector Store (sqlite-vec)
- **7 per-model vec0 collections** (one per active model)
- **Page size**: 4096 bytes (sqlite default)
- **WAL mode**: Enabled for concurrent readers
- **Cache**: `-1` (sqlite default, ~2MB per connection)

### 4.3 FTS5 (BM25)
- **Tokenizer**: `porter` (stemming) + `unicode61` (unicode)
- **BM25 parameters**: `k1=1.2`, `b=0.75` (sqlite defaults)
- **Index size**: ~50MB for 100K documents

### 4.4 Hybrid Search (RRF Fusion)
```python
# src/omega/memory/hybrid_search.py
class HybridSearchEngine:
    def search(self, query: str, k: int = 60) -> List[Result]:
        fts_results = self.fts.search(query, k=k*2)      # BM25
        vec_results = self.vec.search(query, k=k*2)      # Cosine similarity
        return rrf_fuse(fts_results, vec_results, k=k)   # RRF k=60
```

**RRF Formula**: `score = 1 / (rank + k)` where `k=60`

---

## §5 CACHING STRATEGY

### 5.1 What's Cached

| Cache | TTL | Invalidation | Size |
|-------|-----|--------------|------|
| Provider health | 30s | On failure/success | ~1KB |
| Model metadata | 5min | On config change | ~10KB |
| EntityRegistry | 1min | On entity CRUD | ~50KB |
| FTS5 index | N/A | On document write | ~50MB |
| Vector index | N/A | On embedding write | ~200MB |
| Soul (approved_lessons) | 1min | On promotion | ~5KB/entity |

### 5.2 Cache Invalidation
- **Provider health**: Event-driven (on call success/failure)
- **Model metadata**: File watcher on `config/providers.yaml` + `config/models.yaml`
- **EntityRegistry**: Event-driven (on entity CRUD via `EntityRegistry` methods)
- **FTS5/Vector**: Automatic (sqlite-vec + FTS5 triggers)
- **Soul**: Event-driven (on `promote_soul_lessons.py` completion)

### 5.3 No-Cache Zones (Explicit)
- Vault decryption (never cached — `_inject_vault_to_env()` runs at CLI edge)
- Provider selection (always reads `config/providers.yaml` fresh)
- ResourceGuard state (real-time semaphore)

---

## §6 PERFORMANCE GATES

### 6.1 Mandatory Gates (CI)
```bash
# Benchmark gate
make bench-run MODEL=qwen3-1.7b ROLE=roc_racoon SAMPLES=10
# Must pass: TTFT < 200ms, TPS > 15, RAM < 4GB

# Memory gate
make bench-run MODEL=qwen3-4b ROLE=maat SAMPLES=5
# Must pass: RAM < 6GB, no OOM

# Stress gate
make bench-stress DURATION=60
# Must pass: No thermal throttling, no OOM, <5% error rate
```

### 6.2 Benchmark Targets (Current)

| Model | Role | TTFT (ms) | TPS | Peak RAM | Quality |
|-------|------|-----------|-----|----------|---------|
| qwen3-1.7b | roc_racoon | ~150 | ~25 | ~1.5GB | 0.82 |
| qwen3-4b | maat | ~300 | ~18 | ~3.2GB | 0.88 |
| qwen3-4b-thinking | prometheus | ~500 | ~12 | ~3.5GB | 0.91 |

### 6.3 Regression Detection
- `scripts/benchmark_dashboard.py` — tracks trends over time
- `scripts/benchmark_hybrid.py` — compares local vs cloud
- Alert on: TTFT regression >20%, TPS regression >15%, RAM increase >10%

---

## §7 OPTIMIZATIONS APPLIED

### 7.1 CPU (Zen 2)
- **Compile flags**: `-march=znver2 -mavx2 -mfma -O3 -pipe`
- **llama-cpp-python**: Built with `LLAMA_CUBLAS=OFF LLAMA_CLBLAST=OFF LLAMA_METAL=OFF LLAMA_OPENBLAS=ON`
- **Thread pinning**: `taskset -c 0-7` for model inference threads

### 7.2 Memory
- **KV Cache**: Sized to context window (4K→16K) not model max
- **Quantization**: Q6_K for 1.7B/4B models (best quality/size tradeoff)
- **Mmap**: `llama_cpp_python` uses mmap for model loading (zero-copy)

### 7.3 I/O
- **NVMe**: Model loading from `/media/arcana-novai/omega_library/models/gguf/`
- **sqlite-vec**: WAL mode, `PRAGMA synchronous=NORMAL`
- **FTS5**: `PRAGMA journal_mode=WAL`

---

## §8 REGRESSION PREVENTION

### 8.1 God-Module Split (Q-2 Post-Debut)
| Module | Lines | Split Plan |
|--------|-------|------------|
| `observability/__init__.py` | 1660 | → trace/BLEG/sovereignty |
| `model_gateway.py` | 1582 | → router/selector/fabric |
| `oracle.py` | 1459 | → intent/routing/speculative |
| `providers.py` | 1303 | → base/backends/registry |

### 8.2 Silent Swallow Burndown (Q-3)
- Current: 60 `except…: pass` sites
- Target: 0 (ratchet ≤10/PR)
- Each: typed narrow `except` + `logger.debug` or `OmegaError` wrap

### 8.3 Pyflakes Burndown (Q-1)
- 42 redefinitions (shadowing risk) → fix first
- 62 unused imports → remove
- 43 unused locals → remove
- 1 `import re` inside loop → hoist

---

## §9 MONITORING & ALERTING

### 9.1 Hardware Monitor (`src/omega/monitoring/__init__.py`)
```python
class HardwareMonitor:
    def collect_all() -> dict:
        return {
            "cpu": {"avg_percent": ..., "per_core_percent": {...}, "thermal_throttling": ...},
            "memory": {"used_mb": ..., "available_mb": ..., "oom_risk": {...}},
            "temperatures": {"celsius": [...]},
            "threads": {"total_python_threads": ...},
            "disk_io": {...}
        }
```

### 9.2 Key Metrics
| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU avg | >70% | >90% | Throttle admissions |
| Memory % | >75% | >90% | Reject new model loads |
| OOM Risk | MODERATE | HIGH/CRITICAL | Emergency shed |
| Thermal | Throttling active | Sustained | Halt inference |
| Swap % | >10% | >25% | Investigate leak |

### 9.3 CLI Access
```bash
omega hardware-stats              # One-shot summary
omega hardware-stats --watch 2    # Poll every 2s
omega hardware-stats --oom        # Quick OOM risk check
omega hardware-stats --json       # Structured output
```

---

## §10 PERFORMANCE RULES (Carmack's Laws Applied)

1. **Measure before optimizing** — The 3-month Quake Pentium blitz: measure → analyze → implement → verify
2. **Right Approximation** — Trade precision for performance; good enough delivered on time beats perfect delivered late
3. **Precompute over Compute** (Axiom 04) — Trade abundant RAM for scarce CPU cycles
4. **Single Canonical Path** (Axiom 02) — Redundancy is cognitive and computational tax
5. **BSP Culling** — Precompute the hard parts; trade memory for compute
6. **Carmack's Reverse** — Question fundamental assumptions; sometimes invert the standard approach
7. **15W TDP is Law** — Concurrent models = thermal suicide; sequential loading mandatory
8. **L3 is Victim Cache** — Don't assume inclusive L3; design for eviction-only behavior

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_audit ⬡ PERFORMANCE-ARCHITECTURE-v1.0.0*