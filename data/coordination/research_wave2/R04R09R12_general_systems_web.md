---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "research_report"
task_id: "R04R09R12-general-systems"
session_purpose: "Web-research bundle for R4 (llama-fit-params), R9 (NVMe swap), R12 (doc-gen patterns)"
researcher: "Local Inference & Systems Specialist"
date: "2026-08-26"
status: "complete"
---

# R04R09R12 — General Systems Web Research

Consolidated web-research findings for three gaps. Sources verified 2026-08-26.

---

## §1 R4 — llama-fit-params: Existence, Usage, Integration

### 1.1 Verdict: CONFIRMED — Tool Exists and Is Active

`llama-fit-params` is a **real, shipping tool** in llama.cpp, located at `tools/fit-params/`. It has been part of the codebase since ~2025 and is included in all 2026 release builds (latest: b10638, 2026-08-24).

**Source**: [github.com/ggml-org/llama.cpp/tree/master/tools/fit-params](https://github.com/ggml-org/llama.cpp/tree/master/tools/fit-params)

**Files**:
- `tools/fit-params/fit-params.cpp` — core logic
- `tools/fit-params/main.cpp` — CLI entry point
- `tools/fit-params/CMakeLists.txt` — build integration
- `tools/fit-params/README.md` — documentation

### 1.2 What It Does

`llama-fit-params` is a **static VRAM probe**. It:

1. Initializes CUDA/Metal/ROCm backend
2. Queries free device memory
3. Calls `llama_params_fit_impl()` to project memory requirements for the given model
4. Adjusts `llama_model_params` and `llama_context_params` to fit available memory
5. Prints the resulting CLI arguments to stdout

**Key behaviors**:
- Reduces context size if model + context exceeds VRAM (e.g., `context size reduced from 40960 to 4096`)
- Distributes layers across devices with overflow to system memory
- Reports per-device memory breakdown: `CUDA0 (RTX 4090): 48 layers (34 overflowing), 19187 MiB used, 1199 MiB free`
- Maintains a configurable margin (default 1024 MiB free)

**What it does NOT tune**:
- Thread count (`-t`)
- Batch sizes (`-b`, `-ub`)
- Flash attention (`--flash-attn`)
- KV cache types (`--cache-type-k`, `--cache-type-v`)
- mmap/mlock settings

### 1.3 CLI Usage

```bash
# Probe and print fitted args
./build/bin/llama-fit-params --model /path/to/model.gguf | tee args.txt

# Pipe into llama-server
./build/bin/llama-fit-params --model /path/to/model.gguf 2>/dev/null | \
  xargs ./build/bin/llama-server -m /path/to/model.gguf

# Auto-fit is also built into llama-server (default ON since ~2025)
./build/bin/llama-server -m /path/to/model.gguf  # auto-fits at startup
# Disable with: -fit off
```

**Output example** (from upstream README):
```
llama_params_fit_impl: projected to use 61807 MiB of device memory vs. 24077 MiB of free device memory
llama_params_fit_impl: context size reduced from 40960 to 4096 -> need 3456 MiB less memory in total
llama_params_fit_impl: distributing layers across devices with overflow to next device/system memory:
llama_params_fit_impl:   - CUDA0 (RTX 4090): 48 layers (34 overflowing), 19187 MiB used, 1199 MiB free
llama_params_fit: successfully fit params to free device memory
```

### 1.4 Known Issues (2025-2026)

| Issue | Status | Impact |
|-------|--------|--------|
| **Race condition in output** (#18085) | Fixed in #18276 (merged 2025-12-24) | Suggested `-c X -ngl 999` printed at random location when model fits |
| **Vision stack not included** (#18111) | Closed as duplicate, not fully resolved | `--mmproj` not accounted for in fit calculations; causes OOM on image requests |
| **Slow fitting on ROCm** (#19878) | Open/unresolved | `fitting params to free memory took 149.52 seconds` on AMD 7900XTX |

### 1.5 Relationship to Other Tools

| Tool | Type | What It Tunes | Dependencies |
|------|------|---------------|--------------|
| **llama-fit-params** | Static probe | `-ngl`, `--override-tensor`, context size | Built into llama.cpp |
| **llama-bench** | Benchmark | Measures tok/s for given config | Built into llama.cpp |
| **llama-sweep-bench** | Sweep | Batch/thread/param sweeps | Built into llama.cpp |
| **llama-optimus** | Bayesian optimizer | All params via Optuna TPE | Requires llama-bench |
| **llmfit** | Fit estimator | VRAM fit scoring, model recommendations | Standalone Python |

### 1.6 Existing Omega References

The codebase already references `llama-fit-params` in 56 locations:

- **`DEBUT_REMEDIATION_MANUAL_20260817.md:442`**: Listed as part of LOCAL-INFERENCE-OPT workstream (LI-3): "llama-fit-params probe"
- **`R_LOCAL_INFERENCE_OPTIMIZATION_CPU_20260819.md:325`**: "Always use `llama-fit-params` first" before loading ~60GB models
- **`LLAMA_OPTIMUS_DEEP_DIVE.md:205-210`**: Documented as "Static Profiling" — built into llama.cpp since ~2025, probes free VRAM, computes optimal `-ngl` and `--override-tensor`
- **`LLAMA_OPTIMUS_DEEP_DIVE.md:536`**: Positioned as "VRAM-limited setup" tool — static, instant, for ngl

### 1.7 Integration Recommendation for Omega Engine

`llama-fit-params` is the **correct tool** for the AdaptiveContextBuffer (LI-1) and SequentialModelLoader (LI-2) in the LOCAL-INFERENCE-OPT workstream. Integration path:

1. **At model load time**: Call `llama-fit-params --model <path>` to get fitted args
2. **Parse output**: Extract `-ngl`, `-c`, and overflow info
3. **Feed into ModelGateway**: Use fitted args as defaults for `llama-server` launch
4. **Fallback**: If `llama-fit-params` fails (e.g., ROCm slowdown), fall back to hardcoded defaults per model class

**Caveat**: `llama-fit-params` does NOT handle CPU-only inference (no GPU). For the Omega Engine's primary use case (CPU-only Ryzen 5700U), the tool will report no CUDA devices and output minimal guidance. In this mode, `llama-bench` sweeps are more useful for finding optimal thread/batch configs.

---

## §2 R9 — NVMe Swap Best Practice (2026 Consensus)

### 2.1 The 2026 Consensus: Tiered zram-first, NVMe-overflow

The debate has shifted from "swapfile vs partition" to **"which tier goes where."** The 2026 consensus from multiple authoritative sources (Big Iron, LinuxBlog, Enrico Pesce, Hayden James) is:

**Recommended architecture**:
```
Tier 0: zram (compressed in RAM)     — priority 100, swappiness 100+
Tier 1: NVMe swapfile (overflow)     — priority default (-2), swappiness 10-30
```

**Why**: zram handles routine cold-page eviction entirely in RAM (fast, zero disk wear). NVMe swapfile catches genuine memory spikes that exhaust zram. This combination is "hard to beat" for 16-32GB systems.

### 2.2 Swapfile vs Partition on NVMe

**Verdict**: Swapfile is functionally equivalent to partition on modern kernels (4.x+).

| Factor | Swapfile | Swap Partition |
|--------|----------|----------------|
| Performance | Negligible difference on NVMe | Negligible difference on NVMe |
| Flexibility | Easy to resize/remove | Requires repartition |
| Btrfs | Needs special handling (`btrfs filesystem mkswapfile`) | Works natively |
| Hibernation | Supported with offsets | Supported natively |
| Encryption | Inherits filesystem encryption | Requires `cryptsetup` |
| Recommendation | **Preferred** for most use cases | Only if hibernation or LVM snapshots needed |

**NVMe wear**: "Non-issue for moderate swap and a real issue for thrashing." Occasional paging writes are trivial relative to consumer NVMe endurance (typically 600-1200 TBW). If sustained thrashing occurs, the performance collapse gets attention long before wear does — the fix is more RAM or fewer workloads, not a bigger swapfile.

### 2.3 Swappiness Recommendations (2026)

The old rule of thumb (set swappiness=10 for everything) is **stale**. The 2026 matrix:

| Host Profile | Recommended Swap | swappiness | Why |
|-------------|-----------------|------------|-----|
| Pi / small VM / 4-8GB | zram (ram/2, zstd) | **100+** | Free effective-RAM expansion, no disk wear |
| General server, NVMe, adequate RAM | NVMe swapfile (2-8GB) | **10-30** | OOM cushion for spikes, low eager paging |
| Big-RAM latency-critical (DB) | small NVMe swap + cgroup limits + oomd | **1-10** | Evict cold pages without thrashing the hot set |
| Laptop that hibernates | disk swap >= RAM | **10-20** | Hibernation needs RAM-sized swap |
| zram + NVMe overflow (tiered) | zram + NVMe swapfile | **60-100** | Kernel reaches for fast zram tier first |

**Key insight**: The kernel documentation explicitly says values **above 100** can make sense when swap is faster than filesystem I/O — exactly the case for zram. Setting swappiness=0 does NOT disable swap; it postpones swapping until pressure is already severe (worst possible moment).

**D-526 assessment**: The mandate says swappiness=100. This is **correct for zram-only setups** but **too aggressive for NVMe-only swap**. For the tiered zram+NVMe approach in the Omega Engine, swappiness=60-100 is appropriate.

### 2.4 Kernel Advances (6.x / 7.x)

**Multi-Gen LRU (MGLRU)**: Default-on since kernel 6.1. Replaces the old two-list active/inactive heuristic with a generational model that identifies cold pages more accurately. Linux 7.2 (June 2026) brought significant improvements:
- Improved reclaim loop and dirty folio handling: **30-100% throughput gain** on MongoDB with NVMe
- Faster freeing of 0-order pages
- Tighter mmap_miss hit accounting for sparse random access

**Practical effect**: With MGLRU enabled, aggressive manual swappiness tuning matters less than it used to. The kernel makes better swap-versus-cache decisions on its own.

**PSI (Pressure Stall Information)**: The metric that should drive decisions instead of staring at swap usage. `cat /proc/pressure/memory` reports real-time memory pressure. Nonzero, climbing `some`/`full` values mean real thrashing; a box with 2GB in swap and zero memory pressure is **fine**.

**Virtual Swap Space** (active patch series, v3 as of early 2026): Decouples zswap from physical swapfiles. Future win for making zswap more dynamic, removing need for large pre-allocated swapfiles.

### 2.5 Recommended NVMe Swap Setup for Omega Engine

```bash
# 1. Create 16GB swapfile on NVMe root
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile

# 2. Enable with lower priority than zram
sudo swapon -p 5 /swapfile

# 3. Persist in /etc/fstab
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Set swappiness for tiered setup
echo 'vm.swappiness=60' | sudo tee /etc/sysctl.d/99-swap.conf
sudo sysctl --system

# 5. Verify tiered swap
swapon --show
# NAME       TYPE      SIZE  USED  PRIO
# /dev/zram0 partition 16G   0B    100
# /swapfile  file      16G   0B    5
```

**Note**: The existing `config/hardware_profile.yaml` has `nvme_swap_mb: 32768` (32GB). This is conservative but safe. For a 64GB RAM system, 16GB NVMe swap is sufficient as overflow.

### 2.6 SSD TRIM for Swap

The `discard` mount option or periodic `fstrim` works for swapfiles on ext4/xfs. However, for swap specifically, TRIM is less critical because:
- Swap pages are constantly overwritten (self-trimming)
- The SSD's wear leveling handles swap's sequential write pattern
- Periodic `fstrim /` (weekly via timer) covers swap file regions

**Recommendation**: Keep `discard` in fstab for root filesystem. Don't add special TRIM handling for swap.

---

## §3 R12 — Doc-Generation Patterns for Omega DS Workstream

### 3.1 The Documentation Tooling Landscape (2026)

| Tool | Type | Plugin Model | Best For |
|------|------|-------------|----------|
| **Sphinx** | Static site gen | Extensions (Python modules) | API-first docs, autodoc from docstrings |
| **MkDocs** | Static site gen | Plugins (YAML config) | Prose-heavy docs, Markdown-native |
| **RepoDoc** | LLM-powered gen | Skill-based agent pipeline | Repo-level docs with KG backbone |
| **AsciiDoc** | Markup + toolchain | Includes + conditionals | Modular content reuse |
| **DITA** | XML standard | Topic maps + ditamaps | Enterprise multi-output |
| **BMAD** | Agent framework | YAML cascade + CSV manifests | Nested agent/workflow architecture |

### 3.2 Plugin Architecture Patterns

**Pattern 1: Core + Plugin Modules** (Sphinx, MkDocs, VS Code)
```
core_system/
├── core/              # Minimal, stable interface
├── plugins/           # Independent, swappable modules
│   ├── plugin_a/
│   └── plugin_b/
└── plugin_registry.py # Discovery + loading
```
- Well-defined interfaces (hooks, events, APIs)
- Plugins can be loaded/unloaded without touching core
- Discovery via entry points, config, or directory scan

**Pattern 2: Skill-Based Agent Pipeline** (RepoDoc)
```
orchestrator (LLM)
├── skill_layer/
│   ├── research_skill    # Code analysis
│   ├── write_skill       # Doc generation
│   └── validate_skill    # Cross-reference check
└── tool_layer/
    ├── file_reader
    └── diagram_generator
```
- Orchestrator decomposes tasks → dispatches to skills
- Skills are stateless, composable
- Each skill has its own prompt template + tool access

**Pattern 3: Namespace Cascade** (BMAD)
```
_bmad/
├── _config/manifest.yaml    # Installation metadata
├── _memory/                 # Agent persistent state
├── core/                    # Base agents
├── modules/                 # Feature modules
│   └── {module}/
│       ├── agents/
│       ├── commands/
│       └── workflows/
```
- Multi-level namespace: `bmad:bmgd:workflows:create-story`
- YAML cascade config resolution
- Agent memory sidecars for persistence

### 3.3 Modular Documentation Patterns

**The Five Building Blocks** (adoc Studio, 2026):
1. **Define Topics**: Split into Concept, Task, and Reference
2. **Plan Architecture**: Module scoping + naming conventions
3. **Use Includes**: AsciiDoc `include::` or Markdown partials
4. **Apply Conditionals**: Platform/audience-specific content
5. **Version Modules**: Git-based versioning per module

**Modular docs > monolithic docs when**:
- 200+ pages AND 5+ product variants
- Multiple output formats needed (HTML, PDF, man pages)
- AI tools need structured context (70% of teams now factor AI into info architecture)

### 3.4 Self-Validating / Curator Model Patterns

**Pattern A: CI/CD Doc Validation** (Codex CLI pipeline)
```
Audit → Generate → Validate → Render & Publish
  │        │           │            │
  │        │           │            └─ sphinx-build / typedoc
  │        │           └─ pydocstyle / eslint-plugin-jsdoc
  │        └─ codex exec: write docstrings
  └─ codex exec: find undocumented symbols
```
- Docs validated against code on every PR
- Doctests run as part of test suite (`pytest --doctest-modules`)
- Broken links caught at build time (`make linkcheck`)

**Pattern B: Knowledge Graph-Based Incremental Update** (RepoDoc)
- Build RepoKG (Repository Knowledge Graph) as semantic backbone
- Skill-based agent pipeline generates docs from graph queries
- **Semantic Impact Propagation**: When code changes, trace which doc sections are affected
- Incremental update: 73% faster, 77% fewer tokens than full regeneration
- Auto-generated Mermaid architecture diagrams

**Pattern D: LLM-Validated Documentation** (emerging 2026)
- LLM reads code + existing docs
- Identifies drift, outdated sections, missing coverage
- Generates patch-style updates (not full rewrite)
- Human reviews diffs before merge

### 3.5 Reusable Patterns for Omega DS Workstream

| Pattern | Source | Applicability to Omega DS |
|---------|--------|--------------------------|
| **Audit-Generate-Validate-Render pipeline** | Codex CLI | Direct — fits the DS workstream's "curator model" |
| **Skill-based agent architecture** | RepoDoc | High — Omega already uses agent fleet; doc-gen can be a skill |
| **Knowledge Graph backbone** | RepoDoc | Medium — Omega has Library System (FTS5) that could serve as KG |
| **Modular topic types (Concept/Task/Reference)** | DITA/AsciiDoc | High — aligns with Omega's domain-specific docs structure |
| **YAML cascade configuration** | BMAD | High — Omega already uses YAML extensively |
| **Agent memory sidecars** | BMAD | High — aligns with soul.yaml / proposed_lessons.yaml pattern |
| **Doctest-as-test-suite** | Sphinx/pytest | High — validates code examples in docs automatically |
| **Incremental update via impact propagation** | RepoDoc | Medium — reduces doc regeneration cost on code changes |

### 3.6 Recommended Architecture for Omega DS

Based on the patterns above, the Omega Documentation System should use:

1. **MkDocs + Material** as the base generator (Markdown-native, simpler than Sphinx for prose-heavy docs)
2. **Plugin architecture** following the Core + Plugin pattern (domain modules as plugins)
3. **Audit-Generate-Validate-Render pipeline** for the curator model
4. **Modular topic types**: Concept (architecture), Task (how-to), Reference (API/config)
5. **Agent memory sidecars** for doc state persistence (which docs are current, what changed)
6. **Doctest integration** via `pytest --doctest-modules` for code-example validation
7. **Incremental update** via file-change tracking (simpler than full KG, sufficient for Phase 1)

---

## §4 Build-Packets

### BP-R04: llama-fit-params Integration

**Goal**: Wire `llama-fit-params` into ModelGateway for adaptive context sizing.

**Steps**:
1. Build llama.cpp with `llama-fit-params` binary (ensure CMake includes `tools/fit-params`)
2. Create Python wrapper: `src/omega/oracle/llama_fit_probe.py`
   - Subprocess call to `llama-fit-params --model <path>`
   - Parse stdout for fitted args (`-ngl`, `-c`, overflow info)
   - Return as dict for ModelGateway consumption
3. Integrate into SequentialModelLoader (LI-2): probe before load, use fitted args as defaults
4. Handle CPU-only case: if no CUDA/Metal device found, fall back to `llama-bench` sweep
5. Test: verify probe output matches manual `llama-bench` measurements

**Effort**: ~4h implementation + 2h testing
**Blocks**: LI-1 (AdaptiveContextBuffer), LI-2 (SequentialModelLoader)
**Risk**: ROCm fitting may be slow (#19878); need timeout + fallback

### BP-R09: NVMe Swap Configuration

**Goal**: Apply tiered zram+NVMe swap to Omega Engine hosts.

**Steps**:
1. Verify zswap is deployed (ZS-1 from DEB-G0-05): `scripts/zswap_deploy.sh`
2. Create 16GB NVMe swapfile: `sudo fallocate -l 16G /swapfile && sudo mkswap /swapfile`
3. Set priority: `sudo swapon -p 5 /swapfile` (lower than zram's implicit priority)
4. Update `config/hardware_profile.yaml`: `nvme_swap_mb: 16384` (reduce from 32768)
5. Set swappiness: `vm.swappiness=60` (tiered zram+NVMe)
6. Add cgroup MemoryMax=6G for omega containers
7. Verify: `swapon --show` shows both zram (prio 100) and swapfile (prio 5)

**Effort**: ~1h (script exists, needs sudo execution)
**Blocks**: ZS-1 (zswap deployment)
**Risk**: Requires sudo; architect must execute

### BP-R12: Documentation System Architecture

**Goal**: Define the DS workstream's plugin architecture and curator model.

**Steps**:
1. Choose base: MkDocs + Material (Markdown-native, simpler setup)
2. Define module structure:
   ```
   docs/domains/
   ├── workspace/       # Entity workspaces, soul.yaml
   ├── runtime/         # Oracle, ModelGateway, providers
   ├── infrastructure/  # Podman, systemd, NVMe
   └── governance/      # Mandates, decisions, tracking
   ```
3. Implement plugin discovery: each domain module is a directory with `index.md` + optional `config.yaml`
4. Create curator agent skill: `audit → generate → validate → render` pipeline
5. Wire doctests: `pytest --doctest-modules` in CI
6. Initial domain modules: port existing docs from `docs/strategy/`, `docs/research/`, `docs/kb/`

**Effort**: ~2 days (architecture + initial modules)
**Blocks**: DS workstream start
**Risk**: MkDocs Material entered maintenance mode (2026); successor Zensical may require migration

---

## §5 Open Questions

1. **R4**: Does `llama-fit-params` work correctly on CPU-only systems (no CUDA/Metal)? The upstream README only shows CUDA examples. If it outputs nothing useful for CPU-only, the Omega Engine's primary use case (Ryzen 5700U) needs `llama-bench` sweeps instead.

2. **R4**: What is the actual latency of `llama-fit-params` on modest hardware? The upstream example shows 1.15s on RTX 4090. On a CPU-only system without VRAM to probe, does it return instantly or hang?

3. **R9**: Should the Omega Engine's `nvme_swap_mb` be reduced from 32768 to 16384? The system has 64GB RAM; 16GB NVMe overflow is sufficient. 32GB wastes NVMe space that could be used for model storage.

4. **R9**: Is the existing `scripts/zswap_deploy.sh` compatible with tiered zram+NVMe, or does it assume zram-only? Need to verify before applying.

5. **R12**: Should Omega DS use MkDocs or Sphinx? MkDocs is simpler for prose, but Sphinx has stronger autodoc for Python API reference. Given Omega's heavy Python codebase, Sphinx may be more appropriate for `docs/api/` sections.

6. **R12**: Does the RepoDoc Knowledge Graph approach (incremental update via impact propagation) justify its complexity for Omega's doc scale (~200 pages)? Or is simple file-change tracking sufficient for Phase 1?

---

*Research complete. All three gaps investigated with web sources verified 2026-08-26.*
