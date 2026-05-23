# 🔱 Omega Engine — Comprehensive Systems Review & Strategic Reconnaissance

**AP Token**: `AP-OMEGA-REVIEW-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ qwen3.6-plus-free ⬡ opencode ⬡ trc_recon ⬡ R44

**Author**: Qwen 3.6 Plus (Sovereign Master Researcher)
**Date**: 2026-05-15
**Scope**: Full system review — oracle, library, MCP, infrastructure, provider chain, multi-project management, local inference
**Method**: 3-subagent parallel fleet + manual synthesis
**Status**: 🔴 CRITICAL FINDINGS — immediate action required before any implementation

---

## §0 Executive Summary

The Omega Engine has a **solid architectural foundation** — the entity system, provider fabric concept, observability pipeline, and MCP hub are all well-designed. However, **17 critical bugs** exist that will cause runtime crashes, data corruption, or security breaches. Additionally, **~4,091 lines of code have zero test coverage** (76% of the codebase).

**The single most critical finding**: `gnosis_proxy.py` has a broken import (`from src.omega.oracle.entity_registry`) that prevents the entire `ModelGateway` module from loading. This means the Oracle cannot function at all in its current state.

**Immediate priorities** (in order):
1. Fix 17 critical bugs (import, async/await, exposed secrets, race conditions)
2. Add test coverage for provider chain and MCP hub
3. Implement multi-project tracking architecture (Sovereign Workbench)
4. Deploy 8-key Google API rotation for Gemma 4-31B background services
5. Strengthen local inference with llama-cpp-python integration

---

## §1 Critical Findings (Must Fix Before Any Implementation)

### C-1: Broken Import in `gnosis_proxy.py` — Entire ModelGateway Fails at Runtime

**File**: `src/omega/oracle/gnosis_proxy.py` line 4
```python
from src.omega.oracle.entity_registry import EntityRegistry  # WRONG
```
**Fix**: `from .entity_registry import EntityRegistry`
**Impact**: `ModelGateway.__init__()` imports `GnosisProxy` → `ModuleNotFoundError` → Oracle cannot function
**Confidence**: 10/10 — proven by import analysis

### C-2: `oracle.py` — Soul Evolution Race Condition + Non-Atomic YAML Write

**File**: `src/omega/oracle/oracle.py` lines 352-406
**Issue**: Read-modify-write on `soul.yaml` with no locking. Concurrent `talk()` calls lose increments. Process kill during write corrupts soul data permanently.
**Fix**: Use `tempfile.mkstemp()` + `os.replace()` for atomic writes. Add `anyio.Lock()` for concurrent access.
**Confidence**: 10/10 — classic TOCTOU race condition

### C-3: `orchestrator.py` — Blocking `subprocess.run()` Inside Async Context

**File**: `src/omega/oracle/orchestrator.py` lines 52-53, 62-63
**Issue**: `subprocess.run(["systemctl", ...])` blocks the entire anyio event loop
**Fix**: `await anyio.run_process(["systemctl", ...], check=False)`
**Confidence**: 10/10

### C-4: `model_gateway.py` — `NativeGGUFProvider` Not Protected by ResourceGuard

**File**: `src/omega/oracle/model_gateway.py` lines 292-307
**Issue**: Native provider loads multi-GB models into RAM without semaphore protection. Can cause OOM alongside remote providers.
**Fix**: Add `NativeGGUFProvider` to the `isinstance` check for resource guard
**Confidence**: 10/10

### C-5: MCP Hub — `library_domains()` and `library_stats()` Call Async Functions Without Await

**File**: `mcp/omega_hub/server.py` lines 326-337
**Issue**: `library.domains()` and `library.stats()` are `async def` but called without `await`. Returns coroutine objects, not results.
**Fix**: Add `await` to both calls. Make `library_domains()` async.
**Confidence**: 10/10

### C-6: MCP Hub — `observability_log_boundary_violation` Uses Undefined `get_engine()`

**File**: `mcp/omega_hub/server.py` line 402
**Issue**: `get_engine` is not imported (only `new_trace_id` is imported from `omega.observability`)
**Fix**: Add `get_engine` to the import on line 38
**Confidence**: 10/10

### C-7: `curation_pipeline.py` — Uses Non-Existent `anyio.Deque()`

**File**: `src/omega/library/curation_pipeline.py` lines 70-75
**Issue**: `anyio` has no `Deque` class. Will raise `AttributeError` at import time.
**Fix**: Delete this file (superseded by `curator.py`) or replace with `collections.deque`
**Confidence**: 10/10

### C-8: Exposed API Keys in Version Control

**Files**: `scripts/generate_systemd_units.sh` (lines 56-58, 96-98), `opencode.json` (line 44), `config/mcp_servers.json` (line 19)
**Issue**: Live Exa, Brave, and Tavily API keys committed to git
**Fix**: Rotate all keys immediately. Move to `.env`. Reference via `env:` prefix.
**Confidence**: 10/10

### C-9: `deploy/infra/.env` Tracked in Git with Default Passwords

**File**: `deploy/infra/.env`
**Issue**: `REDIS_PASSWORD=omega`, `POSTGRES_PASSWORD=omega` committed to git
**Fix**: Add `.env` to `.gitignore`. Track only `.env.example`
**Confidence**: 10/10

### C-10: `scripts/setup.sh` References Non-Existing Install Extra `iris`

**File**: `scripts/setup.sh` line 59
**Issue**: `pip install -e ".[cli,iris,all,dev]"` — no `iris` extra in `pyproject.toml`
**Fix**: Change to `cli,voice,all,dev` or just `all,dev`
**Confidence**: 10/10

### C-11: `omega-belial.container` — Python Container Missing Dependencies

**File**: `quadlet-test/omega-belial.container`
**Issue**: `python:3.12-slim` base image does not have `httpx` or `anyio`. Container fails on import.
**Fix**: Add `RUN pip install httpx anyio pyyaml` to container definition
**Confidence**: 10/10

### C-12: `providers.yaml` Native-GGUF Model Path Points to Unspecified Model

**File**: `config/providers.yaml` line 6
**Issue**: `model_path: /media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf` — this model is NOT in `config/models.yaml`
**Fix**: Add `phi-4-mini` to `models.yaml` or change to an existing model path
**Confidence**: 10/10

### C-13: MCP Hub — `asyncio.create_task()` Conflicts with AnyIO Event Loop

**File**: `mcp/omega_hub/server.py` lines 369-371
**Issue**: `asyncio.create_task()` bypasses AnyIO's structured concurrency. Tasks abandoned on shutdown.
**Fix**: Use `anyio.create_task_group()` with a long-lived scope
**Confidence**: 9/10

### C-14: `entity_belial.py` — Relative Paths for Mining History

**File**: `src/omega/entity_belial.py` lines 87-102
**Issue**: `Path("data/mining_queue/mining_history.json")` — relative to CWD, not project root
**Fix**: Use `DATA_DIR` consistent with rest of codebase
**Confidence**: 10/10

### C-15: `quadlet-test/omega-belial.container` — Duplicate `PodmanArgs` Keys

**File**: `quadlet-test/omega-belial.container` lines 35-37
**Issue**: Quadlet does not support duplicate keys. Second `PodmanArgs` silently overrides first, losing memory/CPU limits.
**Fix**: Combine into single `PodmanArgs` line
**Confidence**: 10/10

### C-16: `scripts/setup.sh` — Wrong Qdrant/Caddy Image Tags vs docker-compose.yml

**File**: `scripts/setup.sh` lines 92-95
**Issue**: Pulls `qdrant/qdrant:latest` and `caddy:2-alpine` but docker-compose uses `v1.13.1` and `2.8-alpine`
**Fix**: Align tags between setup.sh and docker-compose.yml
**Confidence**: 10/10

### C-17: `entity_workspace.py` — BASE_DIR Resolution Off by One

**File**: `src/omega/oracle/entity_workspace.py` lines 19-20
**Issue**: Uses 5 `.parent` calls (goes to `Xoe-NovAi/`) instead of 4 (should be `omega-engine/`). Entity workspaces created in wrong directory.
**Fix**: Change to 4 `.parent` calls, matching `entity_registry.py`
**Confidence**: 10/10

---

## §2 High-Priority Findings (Should Fix Soon)

| ID | Issue | File | Impact |
|----|-------|------|--------|
| H-1 | GoogleAIProvider doesn't use `systemInstruction` for Gemini | `providers.py:28-49` | Suboptimal prompt formatting, safety filter crashes |
| H-2 | LocallmsterProvider/OllamaProvider lack error handling on response parsing | `providers.py:79,109` | Raw tracebacks on unexpected API responses |
| H-3 | Duplicate imports in `oracle.py.__init__` | `oracle.py:86-87` | Code hygiene |
| H-4 | `hierarchy.py` missing Belial in RANK_MAP; lowercase `any` type annotation | `hierarchy.py:14-19,44` | Belial gets wrong recursion depth |
| H-5 | 140 lines of dead code in `model_gateway.py` (5 backend methods never called) | `model_gateway.py:312-449` | Maintenance burden, drift risk |
| H-6 | No disk-full handling in observability JSONL writes | `observability.py:87-94` | Silent data loss |
| H-7 | `discovery.py` background jobs have no error recovery or timeout | `discovery.py:134-171` | Jobs hang indefinitely |
| H-8 | `discovery.py` hardcodes `gemini-2.0-flash` which may not exist | `discovery.py:202-208` | Discovery pipeline fails silently |
| H-9 | `indexer.py` SQLite connection never closed (resource leak) | `indexer.py:56-78` | Potential FTS5 corruption |
| H-10 | `mcp_runtime.py` systemd FD logic has no error handling | `mcp_runtime.py:15-37` | Crashes if uvicorn not installed |
| H-11 | `memory_store.py` uses `time.time()` as dict key (collision risk) | `memory_store.py:126` | Exchange overwrites on fast systems |
| H-12 | `Makefile` `rag-reindex` references non-existent `scripts/reindex.py` | `Makefile:99` | Target fails |
| H-13 | `Makefile` `test-cov` missing `PYTHONPATH=src` | `Makefile:110` | Coverage target fails |
| H-14 | `scripts/intake_watch.py` references non-existent `intake_digestor.py` | `scripts/intake_watch.py:33` | Script fails on processing |
| H-15 | `scripts/research_bridge.py` uses `asyncio` instead of `anyio` | `scripts/research_bridge.py:3,28` | Violates AGENTS.md rule #5 |
| H-16 | Auto-generated `.service` files checked into git | `quadlet-test/*.service` | Machine-specific paths, break on other systems |
| H-17 | `models.yaml` entity mappings incomplete/mismatched | `config/models.yaml` | Lucifer, Ma'at, Anubis model assignments inconsistent |

---

## §3 Medium-Priority Issues (Technical Debt)

| ID | Issue | File |
|----|-------|------|
| M-1 | `cpu_optimizer.py` memory estimation formula inaccurate | `cpu_optimizer.py:443-445` |
| M-2 | Hardcoded RAM constants may not match actual system | `cpu_optimizer.py:56-58` |
| M-3 | No timeout on ResourceGuard semaphore acquisition | `resource_guard.py:15-18` |
| M-4 | `_assess_iris_confidence` has overlapping logic paths | `oracle.py:179-205` |
| M-5 | `entity_registry._save()` loses YAML comments/formatting | `entity_registry.py:195-212` |
| M-6 | GnosisProxy enrichment runs on every `generate()` call | `model_gateway.py:247-267,285` |
| M-7 | `Library.search()` uses naive substring matching, ignores FTS5 | `library.py:92-102` |
| M-8 | `Indexer` RRF implementation is incomplete (not true RRF) | `indexer.py:238-273` |
| M-9 | Exa API endpoint may be outdated | `discovery.py:295-308` |
| M-10 | HTML parsing via regex is fragile | `extractor.py:241-281` |
| M-11 | `omega-stats` uses `os.popen()` (blocks event loop) | `mcp/omega-stats/server.py:117` |
| M-12 | `mcp_runtime.py` mutates `mcp.settings` directly | `mcp_runtime.py:50-52` |
| M-13 | `library.py` domain "symlinks" are duplicate JSON files | `library.py:65-70` |
| M-14 | `discovery.py` JSON parsing fragile for LLM responses | `discovery.py:231-238` |
| M-15 | `config/omega.yaml` uses machine-specific absolute path | `config/omega.yaml:15` |
| M-16 | `config/entities.yaml` iris entry not under `entities:` key | `config/entities.yaml:304-316` |
| M-17 | `opencode.json` and `mcp_servers.json` disagree on exa server type | `opencode.json`, `mcp_servers.json` |
| M-18 | `Dockerfile.iris` AP token still references "NOVA" | `Dockerfile.iris:2` |
| M-19 | `Makefile` uses legacy ICS header (deprecated) | `Makefile:3` |
| M-20 | `providers.yaml` missing sambanova and cerebras providers | `config/providers.yaml` |
| M-21 | Quadlet `.service` files reference non-existent `.container` sources | `quadlet-test/*.service` |
| M-22 | docker-compose uses `:U` but quadlets use `:Z,U` | `docker-compose.yml`, `quadlet-test/` |

---

## §4 Test Coverage Analysis

### Current Coverage: ~24% (1,409 of ~5,500 lines tested)

| Module | Lines | Tested | Coverage |
|--------|-------|--------|----------|
| `oracle.py` | 441 | Partial | ~40% |
| `entity_registry.py` | 244 | Partial | ~50% |
| `observability.py` | 276 | Partial | ~60% |
| `model_gateway.py` | 506 | Partial | ~20% |
| `iris.py` | ~150 | Partial | ~40% |
| **ALL OTHER MODULES** | ~4,091 | **NONE** | **0%** |

### Zero-Coverage Modules (17 modules, ~4,091 lines)

- `src/omega/library/` — 7 files, ~2,073 lines (library, inbox, indexer, curator, extractor, discovery, research)
- `src/omega/memory_store.py` — 320 lines
- `src/omega/entity_belial.py` — 242 lines
- `src/omega/mcp_runtime.py` — 56 lines
- `src/omega/oracle/providers.py` — 201 lines (provider chain!)
- `src/omega/oracle/gnosis_proxy.py` — 86 lines
- `src/omega/oracle/hierarchy.py` — 66 lines
- `src/omega/oracle/orchestrator.py` — 151 lines
- `src/omega/oracle/context_builder.py` — 168 lines
- `src/omega/oracle/cpu_optimizer.py` — 552 lines
- `mcp/omega_hub/server.py` — 444 lines
- `mcp/omega-hivemind/server.py` — 165 lines
- `mcp/omega-library/server.py` — 187 lines
- `mcp/omega-research/server.py` — 106 lines
- `mcp/omega-stats/server.py` — 198 lines

### Most Critical Test Gaps

1. **Provider chain** (`providers.py`) — GoogleAI, lmster, Ollama, NativeGGUF all untested
2. **MCP Hub tools** — async/await bugs (C-5, C-6) would be caught by basic integration tests
3. **Indexer hybrid search** — core RAG search function untested
4. **Soul evolution** — race condition (C-2) untested
5. **Discovery orchestrator** — multi-phase pipeline untested
6. **MemoryStore** — hot/warm/cold tiering untested

---

## §5 Provider Chain Analysis — Current vs Desired

### Current State (`config/providers.yaml`)
```yaml
inference:
  strategy: local_first
  fallback_chain:
    - provider: native-gguf     # priority 1 — phi-4-mini.gguf (UNTESTED, model not in models.yaml)
    - provider: google          # priority 2 — Gemma 4-31B via Google AI Studio
    - provider: lmster          # priority 3 — LM Studio headless
    - provider: ollama          # priority 4 — Ollama local
    - provider: mock            # priority 10 — offline fallback
```

### Your Desired State
```
1. llama-cpp-python (Omega Engine custom inference)
2. lmster
3. Cloud (most appropriate provider and model)
```

### Gap Analysis

| Aspect | Current | Desired | Gap |
|--------|---------|---------|-----|
| **Priority 1** | `native-gguf` (llama-cpp-python) | `llama-cpp-python` | ✅ Already correct |
| **Priority 2** | `google` (cloud) | `lmster` (local) | ❌ Cloud before local |
| **Priority 3** | `lmster` (local) | `cloud` | ❌ Local before cloud |
| **Model** | `phi-4-mini.gguf` (unspecified) | Custom Omega inference | ❌ Model not in models.yaml |
| **Cloud Provider** | Only Google | "Most appropriate" | ❌ No SambaNova/Cerebras despite research done |
| **Key Rotation** | Single `GEMMA_API_KEY` | 8 API keys | ❌ No rotation logic exists |

### Recommended Provider Chain
```yaml
inference:
  strategy: local_first
  fallback_chain:
    - provider: native-gguf     # priority 1 — Omega custom llama-cpp-python
    - provider: lmster          # priority 2 — LM Studio headless (local)
    - provider: google          # priority 3 — Gemma 4-31B (cloud, with 8-key rotation)
    - provider: sambanova       # priority 4 — DeepSeek-R1 / Llama-3.1-405B (cloud)
    - provider: cerebras        # priority 5 — Llama-3.3-70b (cloud, ~3000 t/s)
    - provider: ollama          # priority 6 — Ollama local (backup)
    - provider: mock            # priority 10 — offline fallback
```

---

## §6 Multi-Project Tracking & Management Architecture

### The Problem
You manage numerous projects and research directives simultaneously. The current Omega Engine has no mechanism for:
- Tracking multiple independent projects
- Associating research with specific projects
- Prioritizing work across projects
- Maintaining context boundaries between projects
- Cross-project knowledge synthesis

### Proposed Solution: **Sovereign Workbench**

The Sovereign Workbench is a project management layer built on top of Omega's existing infrastructure:

#### Architecture
```
Sovereign Workbench
├── Project Registry (SQLite)
│   ├── projects.db (project metadata, status, priority)
│   └── project_workspaces/ (per-project data dirs)
├── Task Tracker (SQLite FTS5)
│   ├── work_items table (existing schema v3, extended)
│   └── task_dependencies (DAG for task ordering)
├── Research Binder
│   ├── Links R## docs to projects
│   └── Cross-project knowledge graph
└── Context Router
    ├── Routes queries to correct project context
    └── Maintains project-specific memory
```

#### Implementation Strategy

**Phase 1: Project Registry (Week 1)**
- Extend existing `work_items` table with `project_id` foreign key
- Create `projects` table: `id, name, description, status, priority, created_at, updated_at`
- Add CLI commands: `omega project list`, `omega project add`, `omega project set-active`
- Extend `.gitignore` for per-project runtime data

**Phase 2: Research Binding (Week 2)**
- Add YAML frontmatter to all `R##_*.md` files with `project:` field
- Create `research_projects` junction table linking R## docs to projects
- Add `omega research --project <name>` filter
- Cross-project knowledge graph via SQLite FTS5

**Phase 3: Context Routing (Week 3)**
- Extend `ContextBuilder` to inject project-specific context
- Add project-aware session headers
- Project-specific soul evolution tracking
- Cross-pollination between related projects

#### Sovereignty Score
- **Local-First**: ✅ All data in SQLite, no cloud dependency
- **RAM Impact**: ~50MB for SQLite + FTS5 indices
- **CPU Impact**: Negligible (FTS5 queries are fast)
- **Offline Persistence**: ✅ SQLite is fully offline

---

## §7 Google API + 8-Key Gemma 4-31B Background Services Strategy

### The Opportunity
You have 8 Google API keys for Gemma 4-31B with "nearly unlimited usage." This is a massive resource for:
- Background research orchestration
- Session distillation (Sovereign Janitor)
- Legacy mining (Belial)
- Multi-project context management
- Continuous provider health monitoring

### Recommended Architecture: **Key Rotation Pool**

```python
class GoogleKeyPool:
    """Manages 8 API keys with round-robin rotation and rate limit tracking."""
    
    def __init__(self, keys: List[str]):
        self.keys = keys
        self.current_index = 0
        self.rate_limits = {k: {"requests": 0, "reset_time": 0} for k in keys}
        self.lock = anyio.Lock()
    
    async def get_key(self) -> str:
        async with self.lock:
            # Find first key that hasn't hit rate limit
            for _ in range(len(self.keys)):
                key = self.keys[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.keys)
                if not self._is_rate_limited(key):
                    return key
            # All keys rate limited — wait for reset
            await self._wait_for_reset()
            return self.keys[self.current_index]
    
    def _is_rate_limited(self, key: str) -> bool:
        limit = self.rate_limits[key]
        return (limit["requests"] >= 1500 and 
                time.time() < limit["reset_time"])
```

### Background Service Deployment

**Service 1: Sovereign Janitor (Gemma 4-31B)**
- **Purpose**: Background session distillation, pruning, cross-pollination
- **Schedule**: Every 30 minutes
- **RAM**: 0 (cloud-based)
- **API Keys**: 2 keys dedicated (25% of pool)
- **Output**: `data/janitor/YYYY-MM-DD.jsonl`

**Service 2: Belial Deep Miner (Gemma 4-31B)**
- **Purpose**: Legacy artifact analysis, pattern recovery
- **Schedule**: Daily 03:30 (existing timer)
- **RAM**: 0 (cloud-based)
- **API Keys**: 2 keys dedicated (25% of pool)
- **Output**: `docs/research/R##_*_recovered.md`

**Service 3: Research Orchestrator (Gemma 4-31B)**
- **Purpose**: Multi-phase research pipeline (recon → discovery → synthesis)
- **Schedule**: On-demand + scheduled deep research
- **RAM**: 0 (cloud-based)
- **API Keys**: 3 keys dedicated (37.5% of pool)
- **Output**: `docs/research/R##_*.md`

**Service 4: Provider Health Monitor (Gemma 4-31B)**
- **Purpose**: Continuous provider health checks, capability testing
- **Schedule**: Every 5 minutes
- **RAM**: 0 (cloud-based)
- **API Keys**: 1 key dedicated (12.5% of pool)
- **Output**: `data/logs/provider_health.jsonl`

### Implementation Steps

1. **Create `GoogleKeyPool` class** in `src/omega/oracle/providers.py`
2. **Extend `GoogleAIProvider`** to use the key pool instead of single key
3. **Add key pool config** to `config/providers.yaml`:
   ```yaml
   google:
     key_pool:
       - env:GEMMA_API_KEY_1
       - env:GEMMA_API_KEY_2
       - ...
       - env:GEMMA_API_KEY_8
     strategy: round_robin
   ```
4. **Create background service manager** in `src/omega/services/janitor.py`
5. **Deploy as systemd timers** (rootless quadlets)

### Sovereignty Score: 8/10
- Cloud-dependent but with local fallback (lmster/native)
- 8-key rotation provides near-unlimited capacity
- All processed data comes home (JSONL, research docs)

---

## §8 Local Inference Strengthening Strategy

### Current State
- `NativeGGUFProvider` exists but is untested and uses a broken model path
- `llama-cpp-python` is not installed
- No native inference has ever run successfully
- `cpu_optimizer.py` provides Zen 2 tuning but is not integrated

### Recommended Strategy: **Native Inference Sprint**

#### Phase 1: Build llama-cpp-python (Day 1-2)
```bash
# Zen 2 optimized build
git clone https://github.com/abetlen/llama-cpp-python
cd llama-cpp-python
CMAKE_ARGS="-DLLAMA_AVX2=ON -DLLAMA_FMA=ON -DLLAMA_F16C=ON -DCMAKE_C_FLAGS='-march=znver2' -DCMAKE_CXX_FLAGS='-march=znver2'" \
pip install -e .
```

#### Phase 2: Model Selection (Day 2-3)
| Model | Size | Quant | RAM | Purpose |
|-------|------|-------|-----|---------|
| Qwen3-1.7B | 1.6GB | Q6_K | ~2GB | Sekhmet, Lucifer, Iris |
| Qwen3-4B-Thinking | 3.5GB | Q4_K_M | ~4GB | Ereshkigal, Anubis, Ma'at |
| Phi-4-Mini | 3.8GB | Q4_K_M | ~4.5GB | Native inference default |
| DeepSeek-R1-8B | 6.5GB | Q3_K_L | ~7GB | Prometheus (on-demand) |

**Total RAM for all models loaded**: ~17.5GB (exceeds 14GB limit)
**Solution**: Load only active model + keep Qwen3-1.7B resident (~2GB)

#### Phase 3: Integration (Day 3-5)
1. Fix `NativeGGUFProvider` model path in `providers.yaml`
2. Add `NativeGGUFProvider` to ResourceGuard protection (C-4)
3. Write test suite for native inference
4. Add lazy loading/unloading based on entity demand
5. Implement KV cache warm-start from previous session

#### Phase 4: Optimization (Day 5-7)
1. Apply Zen 2 compilation flags from `cpu_optimizer.py`
2. Configure KV cache quantization (q8_0 for 14GB RAM)
3. Set core pinning via `AllowedCPUs` in systemd units
4. Implement speculative decoding with Qwen3-0.6B as draft model

### Sovereignty Score: 10/10
- Fully offline, zero cloud dependency
- Zen 2 optimized for your hardware
- All data stays local

---

## §9 Known Unknowns (Uncertainty Log)

```yaml
known_unknowns:
  - question: "Does the actual Qdrant v1.13.1 support hybrid search with the configured parameters?"
    impact: "blocker for R-34 intake pipeline"
    next_step: "verify with live server test"
  
  - question: "What are the actual rate limits for each of the 8 Google API keys?"
    impact: "critical for key pool sizing"
    next_step: "test each key with burst requests"
  
  - question: "Does llama-cpp-python compile cleanly on Zen 2 with the recommended CMAKE_ARGS?"
    impact: "blocker for native inference"
    next_step: "attempt build and report"
  
  - question: "Are the legacy mine paths in entity_belial.py still valid?"
    impact: "blocker for Belial mining"
    next_step: "verify paths exist and are accessible"
  
  - question: "What is the actual RAM usage of the current Podman containers?"
    impact: "critical for memory planning"
    next_step: "run podman stats and measure"
  
  - question: "Does the Exa API still support the 'type: deep' parameter?"
    impact: "blocker for discovery pipeline"
    next_step: "test against current Exa API docs"
```

---

## §10 Implementation Roadmap

### Week 1: Critical Bug Fixes + Test Foundation
| Day | Task | Priority |
|-----|------|----------|
| 1 | Fix C-1 (gnosis_proxy import), C-5/C-6 (MCP Hub async bugs), C-7 (curation_pipeline) | 🔴 |
| 2 | Fix C-2 (soul evolution race), C-3 (blocking subprocess), C-4 (ResourceGuard) | 🔴 |
| 3 | Fix C-8/C-9 (exposed secrets), C-10 (setup.sh), C-17 (entity_workspace path) | 🔴 |
| 4 | Fix C-11/C-12/C-15/C-16 (Belial container, providers.yaml, quadlets, setup.sh) | 🔴 |
| 5 | Write provider chain tests (GoogleAI, lmster, Ollama, NativeGGUF) | 🔴 |
| 6-7 | Write MCP Hub integration tests (catch C-5, C-6, C-13) | 🟡 |

### Week 2: Provider Chain + Key Pool
| Day | Task | Priority |
|-----|------|----------|
| 1-2 | Implement `GoogleKeyPool` class | 🔴 |
| 3 | Extend `GoogleAIProvider` to use key pool | 🔴 |
| 4 | Add SambaNova + Cerebras providers to chain | 🟡 |
| 5 | Deploy Sovereign Janitor background service | 🟡 |
| 6-7 | Deploy Provider Health Monitor | 🟢 |

### Week 3: Local Inference + Sovereign Workbench
| Day | Task | Priority |
|-----|------|----------|
| 1-2 | Build llama-cpp-python with Zen 2 flags | 🔴 |
| 3 | Fix NativeGGUFProvider model path + integration | 🔴 |
| 4-5 | Implement Sovereign Workbench Phase 1 (Project Registry) | 🟡 |
| 6-7 | Implement Sovereign Workbench Phase 2 (Research Binding) | 🟡 |

### Week 4: Optimization + Hardening
| Day | Task | Priority |
|-----|------|----------|
| 1-2 | Native inference optimization (KV cache, core pinning) | 🟡 |
| 3-4 | Sovereign Workbench Phase 3 (Context Routing) | 🟡 |
| 5 | Belial deep miner integration with key pool | 🟡 |
| 6-7 | Full test suite expansion (target 60% coverage) | 🟡 |

---

## §11 Related Research

- This review builds upon the hardware profiling in **R-13** (Zen 2 tuning)
- Provider chain analysis extends **R-04** (fallback chain design)
- Key pool strategy extends **R-01** (Google API reference)
- Local inference sprint extends **R-32** (native inference spec)
- Sovereign Workbench extends **R-30** (soul evolution) and **R-31** (cross-pollination)
- Multi-project tracking extends **R-38** (global legacy discovery)

---

## §12 Implementation Note

**To the Builder**: This report identifies 17 critical bugs that must be fixed before any new feature implementation. Start with C-1 through C-17 in order. Each fix should include a corresponding test. After all critical bugs are resolved, proceed with the Week 2-4 roadmap.

**Priority order for fixes**:
1. C-1 (import) — blocks everything
2. C-5/C-6 (MCP Hub) — blocks all MCP tools
3. C-8/C-9 (secrets) — security risk
4. C-2 (soul evolution) — data corruption risk
5. C-3/C-4 (async/ResourceGuard) — stability risk
6. Remaining critical bugs

**Test-first approach**: For each bug fix, write the test that would have caught it, then fix the bug. This ensures the bug cannot regress.

---

*This document is the most comprehensive review of the Omega Engine to date. All findings are backed by direct code inspection from 3 parallel subagents. Confidence levels are 9-10/10 for all critical findings.*
