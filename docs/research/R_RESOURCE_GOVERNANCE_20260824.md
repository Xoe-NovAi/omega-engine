# R_RESOURCE_GOVERNANCE_20260824

**AP Token**: AP-RESEARCHER-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ x-preview-f-free ⬡ opencode ⬡ trc_resource_governance ⬡ ACTIVE

**Date**: 2026-08-24 · **Task**: kg-resource-platform-research-20260824 (gaps G1–G5)
**Trigger**: Two full-suite OOMs + Iris container permanently unhealthy (2026-08-24 incident record)
**Protocol**: FP-04 T0 discipline — every claim tagged VERIFIED-MEASURED / VERIFIED-CITED / THEORY.
Research only; no code edits. Companion doc: `R_OPENCODE_PLATFORM_INTERNALS_20260824.md`.

---

## Executive Summary (L1)

The suite's ~683MB/worker collection toll is **not diffuse — it is four files**. Full-suite
single-process collection measures **665MB RSS**; excluding just 4 root-level test files drops it
to **225MB**. The dominant offender (`test_youtube_research_v2.py`, 484MB alone) transitively
imports **torch + transformers + sklearn** through a module-level `try: import` guard in
`src/omega_youtube_research/faithfulness.py` — a pattern that guards against dependency *absence*
but pays full cost whenever the deps are *present* (they are). cgroup v2 enforcement via
`systemd-run --user --scope` **works on this host**, but `MemoryMax` alone swap-thrashes instead of
failing; `MemoryMax` + `MemorySwapMax=0` yields deterministic SIGKILL. llama.cpp's own docs and
merged PRs confirm physical-core thread counts for inference; compilation is the inverse case.

## Detailed Findings (L2)

### G1 — Collection weight attribution — VERIFIED-MEASURED

Method: `/usr/bin/time -f %M` around `pytest --collect-only -n0 -q -p no:randomly -p no:tldr`
(xdist off to isolate single-process import weight; `pytest-tldr` must be disabled or it swallows
collect output — measurement gotcha worth keeping).

| Scope | Peak RSS | Tests |
|---|---|---|
| Full `tests/` | **665MB** | 1910 |
| Root files only (subdirs ignored) | 622MB | 1467 |
| Each subdir individually | 78–80MB (baseline) | — |
| `tests/contract/` | 181MB (+103) | 143 |
| Full minus top-4 offenders | **225MB** | — |

Per-file top offenders (peak RSS at solo collection):

| File | Peak RSS | Δ over ~78MB baseline |
|---|---|---|
| `tests/test_youtube_research_v2.py` | **484MB** | ~406MB |
| `tests/test_qdrant_payload_index.py` | 156MB | ~78MB |
| `tests/test_sovereign_ingestion.py` | 145MB | ~67MB |
| `tests/test_e2e_sovereign_sieve.py` | 141MB | ~63MB |

Import-chain forensics (`python -X importtime`):

- `test_youtube_research_v2.py` → `src.omega_youtube_research.faithfulness` → **torch,
  transformers, sklearn.isotonic** — 4.32s cumulative import time, dominated by
  `transformers` (1.24s) and `torch._dynamo`. The heavy imports sit inside module-level
  `try/except ImportError` blocks (`faithfulness.py:36-48`) — graceful-degradation guards that
  never trigger because torch/transformers ARE installed.
- `omega.ingestion.pipeline` → `omega.ingestion.scraper` → **crawl4ai** (~0.85s import).
- `omega.memory.vector_adapters` → qdrant_client chain (~0.25s).

**Collection-weight reduction strategy** (est. savings from the measured 440MB delta):

1. **Lazy NLI imports** in `faithfulness.py`: move `torch`/`transformers`/`sklearn` imports into
   `NLIEntailmentScorer.__init__` (the class already raises RuntimeError when unavailable — the
   guard semantics survive relocation). Est. saving: ~400MB collection floor.
2. **Lazy crawl4ai** in `ingestion/scraper.py` (import inside fetch methods). Est.: tens of MB +
   0.85s startup per worker.
3. **Slim conftest**: `tests/conftest.py:87-93` imports MemoryStore, ContextBuilder, world_state,
   USM, observability, provider/resource registries at module level — every one of the 141 test
   files pays this. Most are re-imported/reset per-fixture anyway. Moderate saving; do after 1–2.
4. Post-fix expectation: collection floor ≈ 225MB → memory-aware worker budget could safely drop
   `per_worker_mb` from 750 toward ~300, roughly doubling parallelism headroom on this box.

Note: `conftest.py`'s `pytest_xdist_auto_num_workers` already encodes the 750MB figure as
*measured* — this research confirms the number and identifies its cause and cure.

### G2 — cgroup v2 enforcement on rootless user sessions — VERIFIED-MEASURED

Host: Ubuntu 25.10, systemd user manager with cgroup delegation (unified hierarchy, `0::` path).

Experiments:

1. `systemd-run --user --scope -p MemoryMax=100M -- python3` allocating+touching 300MB:
   process **survived**. Verified from inside the scope:
   `cat /sys/fs/cgroup/$(sed -n 's/^0:://p' /proc/self/cgroup)/memory.max` → `104857600`.
   The limit IS applied; the 8GB swap absorbed overflow (memcg swaps anon pages before OOM-kill).
2. Same command + `-p MemorySwapMax=0`: **exit 137 (SIGKILL)** — deterministic hard ceiling.
3. Arbitrary cap verified: `-p MemoryMax=6G` → `memory.max = 6442450944`.

**Canonical Makefile integration pattern**:

```make
# Hard-capped test run (deterministic OOM inside the scope, host untouched)
MEM_CAP ?= 8G
SWAP_CAP ?= 200M
test-capped:
	systemd-run --user --scope -p MemoryMax=$(MEM_CAP) -p MemorySwapMax=$(SWAP_CAP) -- \
		.venv/bin/pytest tests/ $(PYTEST_ARGS)
```

Caveat (VERIFIED-MEASURED): without `MemorySwapMax`, breach = silent swap-thrash, which is
*worse* than an OOM kill for CI determinism. Always pair the two properties. A killed scope
returns exit 137 — treat as "cap too low," not flaky failure.

### G3 — SMT/NUMA decision table for THIS box — topology VERIFIED-MEASURED, rules VERIFIED-CITED

Live topology (from `/sys/devices/system/cpu/cpu*/topology/thread_siblings_list` + lscpu):
AMD Ryzen 7 5700U · 8 cores / 16 threads · interleaved sibling pairs **0-1, 2-3, 4-5, … 14-15**
· single NUMA node (0: cpus 0-15) · Zen 2 mobile (no E/P-core split — uniform cores, unlike the
hybrid cases in the citations).

Decision table:

| Workload | Bound by | Threads/pinning rule for this box |
|---|---|---|
| LLM inference (llama.cpp decode) | Memory bandwidth | **8 threads = physical cores only**; pin to one sibling of each pair (e.g., even CPUs 0,2,4,…,14). SMT siblings add contention, not bandwidth. |
| LLM prompt processing (batch) | Compute (GEMM) | Physical cores still best default; SMT can help slightly on some gens — benchmark `-t 8` vs `-t 16` before deviating. |
| C++ compilation (cmake/ninja/make) | Compute | **SMT helps** — use all 16 logical CPUs; cap via env vars (see G4) only to protect co-running inference. |
| pytest-xdist workers | Mixed, mostly Python-bound | Workers ≈ physical-core count (8) or fewer under memory pressure; collection floor (G1) is the binding constraint, not CPU. |
| Speculative decode (Iris-class live inference) | Latency-sensitive bandwidth | Physical cores; avoid sharing siblings with batch/compile jobs. |

Citations:
- llama.cpp official docs, *token_generation_performance_tips.md*: "explicitly set this parameter
  to the number of the physical CPU cores… If your token generation is extremely slow, try
  setting this number to 1." (VERIFIED-CITED)
- llama.cpp PR #934 (merged direction): physical-core default, "Perf (ms per token) is 1.5-2x
  better" vs logical cores. (VERIFIED-CITED)
- llama.cpp issue #19110 → PR #25463: `--threads -1` resolves to physical cores via
  `cpu_get_num_math()`; hardware_concurrency double-counts SMT and can make perf *negative*
  (9 t/s → 2.5 t/s case). (VERIFIED-CITED)
- llama.cpp discussion #572: `numactl -C <P-cores>` gave 2.4–3x on hybrid CPUs — relevant
  pattern if a future box has E/P cores; not needed on uniform Zen 2. (VERIFIED-CITED)

For this box the practical llama.cpp invocation shape: `-t 8` (or taskset to even-numbered
CPUs), never `-t 16`.

### G4 — Bounded source builds — VERIFIED-CITED (env-var semantics), make cap VERIFIED-MEASURED

Mechanism of the redline: llama-cpp-python builds via scikit-build-core → Ninja generator, and
"Ninja … automatically tries to run in parallel with the number of cores on your machine"
(scikit-build-core FAQ) — i.e., all 16 threads, each compile job multi-hundred-MB, colliding
with any live inference workload.

Controlling variables (all documented upstream):

- **`CMAKE_BUILD_PARALLEL_LEVEL=N`** — official CMake env var: caps `cmake --build` concurrency
  ("as if … invoked with the --parallel N option"). scikit-build-core FAQ gives the exact recipe:
  `CMAKE_BUILD_PARALLEL_LEVEL=8 pip install .`
- **`MAKEFLAGS=-jN`** — caps make-driven steps regardless of invocation. Trivially
  VERIFIED-MEASURED on this host (`MAKEFLAGS=-j2 make` honored).
- **`MAX_JOBS=N`** — torch-ecosystem convention, NOT read by cmake/ninja directly;
  scikit-build-core documents forwarding it: `[tool.scikit-build.env]
  CMAKE_BUILD_PARALLEL_LEVEL = { env = "MAX_JOBS" }`. Treat as belt-and-braces for mixed-dependency installs.

**setup.sh wrapper pattern** (proposed; not applied — research-only):

```bash
# Never let a source build redline all 16 threads while inference/desktop runs.
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-4}"
export MAKEFLAGS="${MAKEFLAGS:--j4}"
export MAX_JOBS="${MAX_JOBS:-4}"
.venv/bin/pip install "$@"
```

Honesty note: a full capped `pip install llama-cpp-python` was NOT executed here (host lacks
cmake entirely — itself a finding: any current source build would fail at configure, not
parallelism). Env-var semantics are cited from CMake 4.x and scikit-build-core official docs;
the wrapper pattern is THEORY-pending-first-real-build until then.

### G5 — pytest-cov overhead — config VERIFIED-MEASURED, delta VERIFIED-MEASURED

- Default runs do **NOT** pay coverage: `addopts` (pyproject.toml:135) contains no `--cov`;
  only `make test-cov` adds it. The suite's default path is cov-free.
- Measured delta on `tests/memory` (32 tests, single-process): 0.28s → 1.93s test time (~7x on
  this micro-subset; wall 1.2s → 3.2s including tracer startup). Coverage is expensive when
  paid but is opt-in — no action needed beyond awareness that `test-cov` runs are the slow ones.

## Sovereign Synthesis (L3)

> Memory failures blamed on "too many workers" were actually **four import statements away**.
> Enforcement without swap-control is theater: a limit that thrashes silently is indistinguishable
> from no limit until the box freezes. And the same physical-core rule that governs llama.cpp
> threads governs worker counts: parallelism past the memory-bandwidth/core boundary is not speed,
> it is queueing.

Priority order: (1) lazy-import faithfulness.py [~400MB], (2) MemorySwapMax pairing in any cap
recipe, (3) llama.cpp `-t 8` physical-core pinning, (4) lazy crawl4ai, (5) conftest slimming.

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ R_RESOURCE_GOVERNANCE ⬡ 2026-08-24*
<!-- PROVENANCE-CORRECTED 2026-08-25T03:09:58Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

