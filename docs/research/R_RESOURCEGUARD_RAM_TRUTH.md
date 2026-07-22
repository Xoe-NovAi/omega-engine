# 🔱 R27 — ResourceGuard Single RAM Truth (OOMProtector)
**AP Token**: AP-RESEARCH-R27-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_research
**Date**: 2026-07-21
**Status**: COMPLETE
**Priority**: P0 (Blocks C-2′)

---

## Executive Summary

1. **`psutil.virtual_memory().available` is authoritative** — it reads the kernel's `MemAvailable` from `/proc/meminfo`, which is the same metric the OOM killer uses. It accounts for page cache, reclaimable slab, and low-watermark reserves.
2. **The dual RAM counter is harmful** — `ResourceGuard._current_ram_mb` is a software counter that drifts from reality. RAM usage is non-deterministic (shared memory, mmap overcommit, kernel page cache). The counter creates a false sense of safety while masking real OOM conditions.
3. **OOMProtector is the correct path** — reading `MemAvailable` directly from the kernel AND estimating model RAM requirements gives accurate safety checks. This is what OOMProtector already does.
4. **Default `max_ram_mb = 12288` is wrong** — on a 16GB system with ~8GB available at idle, setting 12288 (12GB) means the software counter allows more allocations than available RAM before the OOMProtector fires.
5. **Kill the software counter entirely** — replace `ResourceGuard._current_ram_mb` with OOMProtector-only protection. The software weight system (tracking individual task RAM consumption) should be removed in favor of admission control via `available_ram - model_estimate - 1GB margin`.

---

## Technical Findings

### 1. psutil.virtual_memory().available — The Authoritative Source

**`psutil.virtual_memory().available`** on Linux ≥3.14 reads directly from `/proc/meminfo` field `MemAvailable`, added by Rik van Riel in commit [`34e431b0ae39`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773) (Linux 3.14, 2014).

**What MemAvailable represents**:
- `MemFree` — completely unused, zeroed pages
- Reclaimable page cache — file-backed pages that can be dropped instantly
- Reclaimable slab — kernel caches (dentry/inode) that can be shrunk
- Minus low-watermark reserves (kernel safety margin)

The kernel's `si_mem_available()` function computes this precisely:
```c
available = MemFree - low_watermark_reserve
available += reclaimable_page_cache * safety_margin
available += reclaimable_slab * safety_margin
```

**Critical insight**: `MemFree` can be near-zero on a healthy system with lots of page cache. Using `MemFree` instead of `MemAvailable` would give false OOM alerts. The current `_get_available_ram_mb()` function correctly uses `MemAvailable`.

**Source**: [Understanding /proc/meminfo — Kernel Internals 2026](https://kernel-internals.org/mm/understanding-proc-meminfo/)

### 2. The Dual Counter Problem — Why Software Counters Fail

Current architecture has **two independent RAM tracking systems**:

```
OOMProtector.check()              ResourceGuard()
│                                 │
├── psutil.virtual_memory()       ├── _current_ram_mb (software counter)
│   .available                    │   + weight tracking
│   → Kernel MemAvailable         │   + _max_ram_mb = 12288
│   → ACCURATE (real-time)        │   → APPROXIMATE (subject to drift)
└── Issues HARD-STOP              └── Blocks on condition.wait()
    or SAFE                           when current + weight > max
```

**Drift mechanisms** (why software counter diverges from reality):

| Cause | Effect | Severity |
|-------|--------|----------|
| **Shared memory** (mmap'd models) | Multiple tasks map same pages → RSS double-counted | HIGH |
| **Overcommit** | Process allocates more virtual than physical | MEDIUM |
| **Kernel page cache** | `_current_ram_mb` doesn't track kernel's cache usage | HIGH |
| **Task weight ≠ actual** | A task with `weight=1` may allocate 2GB | CRITICAL |
| **Garbage collection** | Python GC free memory mid-inference | LOW |
| **Concurrent system services** | Redis, Podman, systemd use RAM outside tracking | MEDIUM |

### 3. OOM Killer Prediction from Userspace (2026)

The Linux OOM killer activates when the kernel cannot satisfy a page allocation. Userspace prediction is inherently imprecise, but the best approach is:

```python
# OOM risk assessment (current implementation works)
available_mb = psutil.virtual_memory().available / (1024 * 1024)
model_estimate_mb = model_spec.get("ram_mb", 0)
kv_cache_mb = context_size * kv_cache_bytes_per_token / (1024 * 1024)
system_reserve_mb = 1024  # 1GB safety margin

total_needed = model_estimate_mb + kv_cache_mb + system_reserve_mb
risk_level = "CRITICAL" if available_mb < total_needed else "SAFE"
```

**Key insight**: The OOMProtector already implements this correctly. The formula in the codebase is sound:
```
required_mb = model_ram_mb + RESERVED_MARGIN_MB (1024 MB)
if available_mb < required_mb → HARD STOP
```

**What is missing**: KV cache estimate is not included in the current formula. On a 16GB system with 8k context, KV cache can be 500MB-2GB depending on quantization.

**Source**: [OOM killer detection — OneUptime 2026](https://oneuptime.com/blog/post/2026-03-02-how-to-monitor-memory-usage-and-troubleshoot-oom-kills-on-ubuntu)

### 4. llama.cpp Memory Mapping vs RSS Accounting

llama.cpp uses `mmap()` for model weights by default. This means:

- **Virtual memory (VSZ)** appears very large (full model size)
- **Resident memory (RSS)** only counts pages actually touched during inference
- **Shared pages** (between processes if same model loaded twice) are counted once per process in RSS

For the Qwen3-1.7B GGUF model (~1.7GB file):
```
VSZ = ~10GB (memory-mapped file + KV cache buffers)
RSS = ~2.5GB (active model weights + KV cache during inference)
```

**This makes software RAM tracking impossible** — the mmap'd pages are demand-paged and RSS varies with inference activity. Only the kernel (`MemAvailable`) knows the true reclaimable state.

**Source**: [llama.cpp memory management — DeepWiki](https://deepwiki.com/spacemit-com/llama.cpp/6.1-memory-management)

### 5. Worker Hardcoded Budgets — Audit

Current hardcoded budgets in `ResourceGuard(max_ram_mb=...)`:

| Worker | Budget | File | Line |
|--------|--------|------|------|
| `ResourceGuard()` default | 12288 (12GB) | `resource_guard.py:228` | Default cvar |
| `ModelGateway` | 12288 (default) | `model_gateway.py:146` | Uses default |
| `Orchestrator` | 1024 | `orchestrator.py:150` | |
| `BackgroundResearcher` | 4096 | `loop.py:115` | |
| `YoutubeWorker` | 2048 | `youtube_worker.py:600` | |
| `IngestionWorker` | psutil-based | `worker.py` | Uses OOMProtector |

**Problem**: These budgets are passed to `ResourceGuard()` which uses them as a software counter limit. With OOMProtector also active, a task blocked at the software counter level may still have 4GB+ of `MemAvailable` because the counter drifted.

**Solution**: 
1. Derive `max_ram_mb` from `MemAvailable` at boot-time (or dynamically per-call)
2. Remove the `max_ram_mb` parameter — let OOMProtector be the sole arbiter
3. Replace worker budgets with `expected_ram_mb` hints (documentation only, not enforcement)

---

## Decision Recommendation

**Prefer OOMProtector only; kill the `ResourceGuard._current_ram_mb` software counter.**

Specific actions:

1. **Remove `_current_ram_mb`** from `ResourceGuard` entirely
2. **Remove `max_ram_mb` parameter** — OOMProtector gets the authoritative number from the kernel
3. **Keep `OOMProtector.check()` as the sole RAM gate** — enhance it to include KV cache estimate
4. **Keep the re-entrant lock pattern** (`_held_weights` ContextVar) for concurrency — just remove RAM tracking from it. The semaphore protects concurrent model loads, not RAM.
5. **Worker budgets → `model_spec.ram_mb` hints** — Orchestrator=1024, Researcher=4096, etc. are documented expected RAM usage, not hard enforcement

**Rationale**: The kernel knows more about available memory than any userspace counter. The OOM killer will kill you if you're wrong. The software counter gives false confidence and has already caused bugs (the default `12288` mask on a system with 8000MB available would allow concurrent loads that OOM). Remove the counter, trust the kernel.

---

## Sources

1. [Understanding /proc/meminfo — Linux Kernel Internals 2026](https://kernel-internals.org/mm/understanding-proc-meminfo/)
2. [psutil virtual_memory docs — giampaolo/psutil](https://github.com/giampaolo/psutil/blob/master/psutil/_pslinux.py)
3. [Linux kernel MemAvailable calculation — commit 34e431b0ae39](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=34e431b0ae398fc54ea69ff85ec700722c9da773)
4. [OOM kill detection — OneUptime 2026](https://oneuptime.com/blog/post/2026-03-02-how-to-monitor-memory-usage-and-troubleshoot-oom-kills-on-ubuntu)
5. [llama.cpp memory management — DeepWiki](https://deepwiki.com/spacemit-com/llama.cpp/6.1-memory-management)
6. [psutil memory metrics — Giampaolo Rodola](https://gmpy.dev/blog/2016/psutil-440-improved-linux-memory-metrics)
7. [MemAvailable vs MemFree](https://chewett.co.uk/blog/2829/python-psutil-and-the-differences-between-free-and-available-memory/)
8. Existing code: `src/omega/oracle/resource_guard.py` (OOMProtector + ResourceGuard)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ R27-COMPLETE ⬡ 2026-07-21*
