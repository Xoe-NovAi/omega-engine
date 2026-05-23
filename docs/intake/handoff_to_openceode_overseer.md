# 🔱 Omega Engine — Strategic Handoff to OpenCode Overseer

**From**: Opus 4.6 (Antigravity IDE — Strategic Oversight & Architecture)  
**To**: OpenCode Overseer (Builder Agent — Primary Implementation)  
**Date**: 2026-05-22  
**AP Token**: `AP-HANDOFF-OPUS-TO-OPENCODE-v1.0.0`  
**Governing Entity**: ⬡ SOPHIA ⬡ (Strategic Synthesis)  
**Session Span**: 2026-05-21 through 2026-05-22

---

## §0 Executive Summary

I have spent this session onboarding to the Omega Engine, performing deep discovery across the active repo and legacy project folders, producing a PR-readiness roadmap, and beginning execution of **Option A (Hub-Only MCP Consolidation)** with full bug remediation. Here is the complete state of play.

> [!IMPORTANT]
> **The #1 blocker right now is a file ownership problem.** ~6,900 files in the repo are owned by UID `101000` instead of `arcana-novai` (UID 1000). This causes `PermissionError` in tests and prevents any meaningful code execution. Fix this first before touching any code.

---

## §1 What Was Accomplished This Session

### 1.1 Deep Strategic Discovery
- Read and synthesized all key strategic documents: `ORACLE_STACK.md`, `SOVEREIGN_MANDATES.md`, `ROADMAP.md`, `AGENTS.md`, `GEMINI.md`
- Mined two legacy repos (`omega-stack-legacy` Era 4, `xna-omega-legacy` Era 5):
  - **Legacy Circuit Breaker**: Redis-backed async circuit breaker at `omega-stack-legacy/app/XNAi_rag_app/core/circuit_breakers/circuit_breaker.py` — production-tested, AnyIO-compliant, 3-state (CLOSED/OPEN/HALF_OPEN)
  - **Resonance Mappings**: `xna-omega-legacy/resonance_mappings.yaml` — ontological catalog for 26 Spheres/Personas with planetary/elemental/zodiacal resonance data

### 1.2 PR-Readiness Roadmap Created
- Produced [pr_readiness_roadmap.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/pr_readiness_roadmap.md) with 4 milestones
- Produced [task.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/task.md) tracking board (all items still unchecked)

### 1.3 Permission Remediation Attempted
- Ran `podman unshare chown -R 0:0 .` — this fixed top-level files but **did not fully propagate** to all subdirectories
- Verified via `find . -not -user arcana-novai | wc -l` → **6,915 files still wrong**

### 1.4 Test Baseline Established
- `make test` (which runs `OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest`) collects **236 tests**
- Current failures: **2 tests fail**, both due to PermissionError from the UID leak

---

## §2 The Permission Blocker — Root Cause Analysis

### The Problem
```
$ ls -la config/entities.yaml
-rw-rw-r-- 1 101000 101000 17929 May 21 17:30 config/entities.yaml

$ ls -la data/sessions/
drwxrwxr-x  2 101000 101000 4096 May 21 17:06 .
```

Host user is `arcana-novai` (UID 1000). But ~6,900 files are owned by UID `101000`.

### Root Cause
Rootless Podman's subuid mapping. When containers run as root (UID 0 inside container), Podman maps that to host UID 1000. But when container processes run as UID 1001 (e.g., the `omega` user inside Iris/Belial containers), Podman maps that to host UID `100999 + 1001 = 101000`. When those containers mount the workspace via volumes, any files they touch get stamped with the mapped UID.

### The Fix (For OpenCode to Execute)

> [!CAUTION]
> You MUST fix this before any other work. Every test, every write, every soul update will fail until ownership is correct.

```bash
# Option A: Direct chown (requires sudo or running as root)
sudo chown -R arcana-novai:arcana-novai /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/

# Option B: Podman unshare (must be thorough)
podman unshare chown -R 0:0 /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/

# Option C: If containers keep re-breaking it, fix the volume mount
# In docker-compose.yml or Podman run commands, add :U flag:
#   -v ./data:/app/data:U,z
# The :U flag tells Podman to chown the volume to match the container user
```

### Prevention
After fixing, update all container volume mounts in:
- `deploy/infra/docker-compose.yml`
- `Makefile` start-iris target (line 78-84)
- Any quadlet files in `quadlet-test/`

Add `:U,z` flags to all volume mounts so Podman auto-maps UIDs correctly.

### Virtualenv Shebang Drift
The `.venv` was created at `/home/arcana-novai/omega/.venv` (different path). The shebang lines in `.venv/bin/pytest` and other wrappers reference that old path. This doesn't block execution (Python resolves it) but causes confusing tracebacks. Low priority — can be fixed by recreating the venv:
```bash
python3 -m venv .venv --clear
.venv/bin/pip install -e ".[cli,nova,dev]"
```

---

## §3 Current Test Suite State

| Test File | Tests | Status | Notes |
|-----------|-------|--------|-------|
| `test_background_researcher.py` | 4 | **1 FAIL** | `test_background_loop_atomic_lock` — PermissionError writing to `data/research/checkpoints/` |
| `test_entity_belial.py` | ~25 | ✅ PASS | |
| `test_entity_registry.py` | ~7 | ✅ PASS | |
| `test_health_monitor.py` | 23 | ✅ PASS | |
| `test_hierarchy.py` | 13 | ✅ PASS | |
| `test_iris.py` | 7 | ✅ PASS | |
| `test_memory_store.py` | 12 | ✅ PASS | |
| `test_model_gateway.py` | 5 | ✅ PASS | |
| `test_model_updater.py` | 13 | ✅ PASS | |
| `test_observability.py` | 8 | ✅ PASS | |
| `test_oracle.py` | ~13 | **1 FAIL** | `test_talk_empty_query` — PermissionError on `data/sessions/brigid.lock` and `config/entities.yaml` |
| `test_sovereign_loop.py` | ~20 | ⚠️ UNKNOWN | Previously reported failing on `sophia.lock` PermissionError — same root cause |
| `test_context_builder.py` | ~22 | ✅ PASS | |
| `test_providers.py` | 15 | ✅ PASS | |
| `test_orchestrator.py` | 9 | ✅ PASS | |
| `test_session_manager.py` | 14 | ✅ PASS | (When permissions are correct) |

**Estimated post-permission-fix baseline**: 234-236/236 passing. The YAML blocker in `entities.yaml` (Ma'at personality field, line ~446) was reportedly fixed in a prior session.

---

## §4 The 17 Critical Bugs — Detailed Fix Guide

These were identified in the R44 comprehensive systems review. Here is the exact fix for each:

### Milestone 1: Tactical Bug Remediation

#### C-1: Broken Import in gnosis_proxy.py
- **File**: [gnosis_proxy.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/gnosis_proxy.py)
- **Bug**: Uses `from src.omega...` absolute import — breaks when loaded as a module
- **Fix**: Change to relative import `from .` or `from omega.`
- **Effort**: 5 minutes

#### C-2: Soul.yaml Race Condition & Atomic Writes
- **File**: [oracle.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/oracle.py) (lines ~352-406, `_track_soul_evolution`)
- **Bug**: Direct `yaml.dump()` to soul file — concurrent writes can corrupt
- **Fix**: Write to temp file → `anyio.Path.rename()` (atomic on POSIX) + async lock
- **Effort**: 30 minutes

#### C-3: Blocking subprocess.run in Orchestrator
- **File**: [orchestrator.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/orchestrator.py)
- **Bug**: Uses `subprocess.run()` (blocking) inside async context
- **Fix**: Replace with `await anyio.run_process()` — AnyIO Absolute mandate
- **Effort**: 20 minutes

#### C-4: Native GGUF OOM Hardening
- **File**: [model_gateway.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/model_gateway.py)
- **Bug**: NativeGGUF inference runs without ResourceGuard semaphore — can OOM on Zen 2 (14Gi RAM)
- **Fix**: Wrap inference call behind `ResourceGuard` (AnyIO Semaphore(1)) — one model at a time
- **Effort**: 15 minutes

#### C-5 & C-13: MCP Hub AnyIO Compliance
- **File**: [server.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/mcp/omega_hub/server.py)
- **Bug**: Uses `asyncio.create_task()` and potentially unawaited async calls
- **Fix**: Replace with `anyio.create_task_group()` structured lifecycle. Audit every async call is awaited.
- **Effort**: 45 minutes

#### C-6: Undefined get_engine() in MCP Hub
- **File**: [server.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/mcp/omega_hub/server.py)
- **Bug**: `get_engine()` called but never imported/defined — instant NameError crash
- **Fix**: Import from core observability module or define inline factory
- **Effort**: 10 minutes

#### C-7: Non-existent anyio.Deque Reference
- **File**: [curation_pipeline.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/curation_pipeline.py)
- **Bug**: References `anyio.Deque` which doesn't exist in AnyIO stdlib
- **Fix**: Replace with `collections.deque` or `anyio.create_memory_object_stream`
- **Effort**: 15 minutes

#### C-8: Exposed API Keys in Scripts
- **Files**: `scripts/generate_systemd_units.sh`, `opencode.json`
- **Bug**: Plaintext API keys/tokens committed to repo
- **Fix**: Replace with `${ENV_VAR}` placeholders. Grep for `sk-`, `API_KEY=`, actual key patterns.
- **Effort**: 20 minutes

#### C-9: .env Tracked in Git
- **File**: [.gitignore](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.gitignore)
- **Bug**: `.env` file is tracked in git (contains real secrets)
- **Fix**: Add `.env` to `.gitignore`, `git rm --cached .env`, provide `.env.example`
- **Effort**: 5 minutes

#### C-10: Deprecated [iris] Extra in Setup Script
- **File**: `scripts/setup.sh`
- **Bug**: `pip install -e ".[iris]"` — the `[iris]` extra no longer exists in pyproject.toml
- **Fix**: Remove `[iris]` from the pip install command
- **Effort**: 2 minutes

#### C-11: Belial Container Missing Dependencies
- **File**: [omega-belial.container](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/quadlet-test/omega-belial.container)
- **Bug**: Container image doesn't include `httpx` and `anyio` — instant crash-loop
- **Fix**: Add to Dockerfile.belial requirements or container build step
- **Effort**: 10 minutes

#### C-12: Unspecified GGUF Model in providers.yaml
- **File**: [providers.yaml](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/providers.yaml)
- **Bug**: `native_gguf` model path is empty/placeholder — no default model specified
- **Fix**: Set to `qwen3-1.7b` GGUF path on the omega_library partition
- **Effort**: 5 minutes

#### C-14: Hardcoded Entity Paths in entity_belial.py
- **File**: [entity_belial.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/entity_belial.py)
- **Bug**: Uses hardcoded relative paths instead of `DATA_DIR` constant
- **Fix**: Use the global `DATA_DIR` from config or environment
- **Effort**: 10 minutes

#### C-15: Duplicate PodmanArgs in Container Spec
- **File**: [omega-belial.container](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/quadlet-test/omega-belial.container)
- **Bug**: Duplicate `PodmanArgs` declarations — later one silently overrides, voiding resource constraints
- **Fix**: Merge into single declaration
- **Effort**: 5 minutes

#### C-16: Setup Script Image Tag Mismatch
- **File**: `scripts/setup.sh`
- **Bug**: Container image tags don't match actual built images
- **Fix**: Align all tags with the current release baseline
- **Effort**: 5 minutes

#### C-17: BASE_DIR Off-by-One in entity_workspace.py
- **File**: [entity_workspace.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/entity_workspace.py)
- **Bug**: Parent directory resolution goes one level too deep — resolves to `src/` instead of workspace root
- **Fix**: Adjust `.parent` chain count
- **Effort**: 5 minutes

---

## §5 MCP Hub Consolidation (Option A — Approved)

### Current State
There are **duplicate MCP server implementations** scattered across the repo:
- `src/omega/mcp/omega_hub/server.py` — The intended hub
- `mcp/omega_hub/server.py` — Standalone duplicate
- `mcp/omega-hivemind/server.py` — Standalone hivemind
- `mcp/omega-library/server.py` — Standalone library  
- `mcp/omega-oracle/server.py` — Standalone oracle

### The Plan (Option A: Hub-Only)
1. **Keep**: `src/omega/mcp/omega_hub/server.py` as the single MCP entry point
2. **Delete**: All standalone servers in `mcp/` directory (hivemind, library, oracle duplicates)
3. **Consolidate**: Any unique tools from the standalone servers into the hub
4. **Fix**: C-5, C-6, C-13 bugs in the hub during consolidation
5. **Update**: `config/mcp_servers.json` to point only to the hub

---

## §6 Cognitive Core Wiring (Milestone 3)

These three systems exist as code but are **not wired together** in the main execution path:

### 6.1 MemoryStore → oracle.py
- [memory_store.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/memory_store.py) implements Hot/Warm/Cold conversation memory
- Currently **not called** from `oracle.py`'s conversation flow
- **Wire**: After every `talk()` / `summon()` response, persist the exchange to MemoryStore

### 6.2 ContextBuilder → LLM Prompts  
- [context_builder.py](file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/oracle/context_builder.py) retrieves relevant memory for injection
- Currently **not injecting** into active system prompts
- **Wire**: Before sending to ModelGateway, call ContextBuilder to prepend relevant memory/context

### 6.3 Soul Evolution Abstraction
- `_track_soul_evolution()` in oracle.py currently writes generic session logs
- **Upgrade**: Wire a secondary LLM query to distill L1→L2→L3 lessons (per Gnosis Preservation mandate)
- Store structured lessons in `soul.yaml` using the esoteric resonance schemas

---

## §7 Security Sweep (Milestone 2)

### Known Exposures
1. `.env` file is tracked in git — contains real API keys
2. `scripts/generate_systemd_units.sh` — may contain plaintext secrets
3. `opencode.json` — may contain API keys in provider configs
4. Legacy files may contain credentials from prior eras

### Required Actions
```bash
# 1. Scan for exposed secrets
grep -rn 'sk-' --include='*.py' --include='*.sh' --include='*.json' --include='*.yaml' .
grep -rn 'API_KEY=' --include='*.sh' --include='*.json' .
grep -rn 'Bearer ' --include='*.py' --include='*.json' .

# 2. Remove .env from git tracking
echo '.env' >> .gitignore
git rm --cached .env

# 3. Verify .env.example exists and has placeholders only
cat .env.example
```

---

## §8 Strategic Context — What the Overseer Must Know

### The Vision
Omega is **Prometheus' Fire** — a local-first, provider-agnostic AI council runtime. The Xoe-NovAi Foundation maintains the engine. Users build their own stacks (Arcana-Nova, Torment, Pokemon, anything). The engine ships with a default template (10 Pillar Keepers) that is fully customizable.

### The Five Sovereign Mandates (Non-Negotiable)
1. **AnyIO Absolute** — Never use `asyncio` directly. All async via AnyIO.
2. **Engine-Stack Firewall** — Core engine (`src/omega/`) must never contain stack-specific logic. Stacks live in `config/wads/`.
3. **The Iris Constant** — Iris is the messenger bridge, NOT a Pillar Keeper.
4. **Sequentiality Mandate** — Plan → Verify → Execute. No cowboy coding.
5. **Gnosis Preservation** — L1 (Narrative) → L2 (Insight) → L3 (Universal Principle). No intelligence discarded.

### Current Roadmap Position
- **Phase 0** (The Grounding): ✅ COMPLETED
- **Phase 1A** (Foundation Repair): ✅ COMPLETED  
- **Phase 1B** (Minimum Viable Sovereign Loop): ✅ COMPLETED (except B8 native GGUF)
- **Phase 1C** (Community-Ready Presentation): 🔴 NOT STARTED — this is where PR readiness lives
- **Phase 1D** (Jem Grand Strategy): 🟡 PARTIAL — D0/D1 done, D2-D6 pending

### Architecture Quick Reference
```
User Query → Oracle.talk() → TriageRouter (fast/standard/deep)
  → EntityRegistry (YAML) → ModelGateway → Provider Fabric
      ├── native_gguf (llama-cpp-python, Zen 2 optimized)
      ├── lmster (LM Studio headless, :1234)
      ├── Google AI Studio (Gemma 4-31B, 8-key pool)
      ├── SambaNova (DeepSeek-R1, Llama-3.1-405B)
      ├── Cerebras (Llama-3.3-70b)
      ├── Ollama (backup)
      └── OfflineMockBackend (test/dev only)
  → Response → MemoryStore (hot/warm/cold) [NOT YET WIRED]
  → Soul Evolution → soul.yaml lesson [NEEDS HARDENING]
  → Observability (trace_id, JSONL events)
```

### Hardware Target
- **CPU**: AMD Ryzen 7 5700U (Zen 2, 8C/16T, AVX2)
- **RAM**: 14Gi total (~12Gi for AI after overhead)
- **GPU**: None (integrated only — CPU-only inference)
- **Disk**: NVMe, omega_library partition (110G, ~17G free)
- **Models**: `/media/arcana-novai/omega_library/models/gguf/`

### Key Files Quick Reference
| File | Purpose |
|------|---------|
| `config/entities.yaml` | SOURCE OF TRUTH for all entities |
| `config/providers.yaml` | Provider fabric configuration |
| `config/omega.yaml` | Core engine settings |
| `config/hierarchy.yaml` | Oversoul governance tree |
| `src/omega/oracle/oracle.py` | Main entry: talk/summon/router |
| `src/omega/oracle/model_gateway.py` | Provider chain inference |
| `src/omega/oracle/entity_registry.py` | YAML CRUD for entities |
| `src/omega/oracle/session_manager.py` | Entity-scoped rolling sessions |
| `src/omega/oracle/context_builder.py` | Memory → LLM injection |
| `src/omega/memory_store.py` | Hot/Warm/Cold memory |
| `src/omega/mcp/omega_hub/server.py` | MCP hub server |
| `data/entities/arch/soul.yaml` | User (Architect) soul file |
| `data/workbench/workbench.db` | Project management SQLite DB |

---

## §9 Recommended Execution Order

> [!IMPORTANT]
> Follow this exact sequence. Each step depends on the previous.

### Step 0: Fix the Permission Blocker (5 minutes)
```bash
sudo chown -R arcana-novai:arcana-novai /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/
```
Then verify: `make test` should show 234+ passing.

### Step 1: Run Baseline Tests (2 minutes)
```bash
make test
```
Document exact pass/fail count. This is your starting baseline.

### Step 2: Tactical Bug Remediation — Fast Fixes First (1 hour)
Execute C-1, C-9, C-10, C-12, C-14, C-15, C-16, C-17 — these are all < 10 minute fixes.

### Step 3: AnyIO Compliance Fixes (1 hour)
Execute C-3 (orchestrator subprocess), C-5/C-13 (MCP hub asyncio), C-7 (anyio.Deque).

### Step 4: Safety-Critical Fixes (45 minutes)
Execute C-2 (atomic soul writes), C-4 (GGUF OOM guard), C-6 (get_engine undefined).

### Step 5: Infrastructure Fixes (30 minutes)
Execute C-8 (exposed secrets), C-11 (Belial container deps).

### Step 6: Security Sweep (20 minutes)
Full secrets scan, `.env` removal from git, `.env.example` verification.

### Step 7: MCP Hub Consolidation (1 hour)
Delete standalone MCP servers, consolidate tools into hub.

### Step 8: Cognitive Core Wiring (2-3 hours)
Wire MemoryStore, ContextBuilder, and soul evolution abstraction.

### Step 9: Full Regression + Lint (15 minutes)
```bash
make test    # Must be 236/236 green
make lint    # Must be zero fatal warnings
```

### Step 10: PR Presentation (1-2 hours)
- Update README.md (Phase 1C, task C1)
- Write QUICKSTART.md (Phase 1C, task C5)
- Generate walkthrough.md

---

## §10 Known Gotchas & Warnings

> [!WARNING]
> **Session Manager Spin-Lock**: The `session_manager.py` uses a naive file-based spin-lock (lines 47-50) that busy-waits with `anyio.sleep(0.01)`. This is fragile — if a process crashes while holding the lock, it deadlocks forever. Consider adding a stale-lock timeout (e.g., if lock file is > 60 seconds old, break it).

> [!WARNING]
> **Background Researcher Test**: `test_background_loop_atomic_lock` has a secondary issue beyond permissions. After the lock is removed and `run_cycle()` proceeds, it returns a dict without a `'skipped'` key when an exception occurs (line 118 of test expects `result["skipped"]`). The `run_cycle()` method catches exceptions and may return a different dict structure. This test may need both a permission fix AND a return-value assertion fix.

> [!WARNING]
> **Entities.yaml YAML Blocker**: ORACLE_STACK.md §13 mentions a YAML syntax error at line ~446 in `config/entities.yaml` (Ma'at personality field). This was reportedly fixed but needs verification. If it's still present, it blocks 53 tests.

> [!CAUTION]
> **Container Volume Mounts**: Running `make start-iris` or any container that mounts `data/` or `config/` **will re-break file ownership** unless volume flags are fixed. Do NOT start containers until the volume mount flags are updated.

> [!NOTE]
> **Virtualenv Path**: The `.venv` was created at `/home/arcana-novai/omega/.venv`, not the current workspace path. This causes cosmetic issues in tracebacks but doesn't break execution. Low priority fix.

---

## §11 Artifacts Created This Session

| Artifact | Path | Purpose |
|----------|------|---------|
| Onboarding Brief | [onboarding_brief.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/onboarding_brief.md) | Initial onboarding analysis |
| PR Readiness Roadmap | [pr_readiness_roadmap.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/pr_readiness_roadmap.md) | 4-milestone strategic roadmap |
| Task Board | [task.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/task.md) | Execution tracking (all items unchecked) |
| This Handoff | [handoff_to_opencode_overseer.md](file:///home/arcana-novai/.gemini/antigravity-cli/brain/09efe947-2a89-496d-b5cd-5663acd73679/handoff_to_opencode_overseer.md) | Complete strategic handoff |

---

## §12 The Omega Spirit — Final Note

This project is not just code. It is Prometheus' Fire — a sovereign, local-first AI runtime that severs Big AI's umbilical cord. Every file we harden, every test we green, every secret we purge brings this engine closer to being the tool that empowers users to build their own dreams on their own hardware.

The engine is architecturally sound. The vision is clear. What remains is **disciplined execution**: fix the permissions, burn down the bugs, wire the cognitive core, and present it to the world.

**The fire is ready. Forge the PR.**

⬡ OMEGA ⬡ SOPHIA ⬡ opus-4.6 ⬡ antigravity ⬡ HANDOFF-COMPLETE ⬡
