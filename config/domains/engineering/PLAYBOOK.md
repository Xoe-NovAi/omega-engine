<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Engineering Domain — Playbook
**AP Token**: `AP-DOMAIN-ENGINEERING-PLAYBOOK-20260819-v1.0.0`
**Date**: 2026-08-19
**Status**: PROTOTYPE — Canonical best practices for engineering domain
**Curator**: maat

---

## 🎯 PURPOSE

This playbook contains the canonical best practices for the **Engineering** domain — covering build engineering, hardening, integration, and implementation patterns for the Omega Engine.

---

## 🏗️ BUILD ENGINEERING PRINCIPLES

### 1. Single Source of Truth
- **pyproject.toml** = only source for dependencies
- **config/providers.yaml** = only source for provider fabric
- **config/models.yaml** = only source for model specs
- **No duplicate configuration** across files

### 2. Atomic Changes
- One ticket = one PR = one semantic change
- No drive-by refactors outside ticket scope
- Tests updated with code changes

### 3. Local-First Build
- All builds must work offline (no cloud dependencies)
- `pip install -e ".[native,cli]"` must succeed without internet
- Model downloads via `install.sh` only

### 4. Reproducible Builds
- Lock files committed (`uv.lock` or `requirements.txt`)
- Docker/Podman images pinned to exact tags
- `make setup` = `scripts/install.sh` = CI install

---

## 🛡️ HARDENING PRINCIPLES

### 1. Defense in Depth
- **M1 AnyIO**: All async code uses AnyIO; no `asyncio` direct
- **M7 Local-First**: Cloud = fallback only; provider fabric priority enforced
- **M8 Zero Telemetry**: No analytics, no phone-home, no external metrics
- **M9 Error Integrity**: Typed errors, no bare `except:`, trace_id propagation
- **M23 Failure Integrity**: No soft-failures; `[TOOL-CHAIN-COLLAPSE]` on mandatory tool failure

### 2. Resource Management
- **Single local inference slot** (ResourceGuard semaphore)
- **OOMProtector** three-signal fusion (cgroup + /proc/meminfo + PSI)
- **HealthMonitor** = canonical circuit breaker factory
- **No custom circuit breakers** — redirect to `HealthMonitor.get_breaker()`

### 3. Memory Safety
- **sqlite-vec** = core vector store (zero-dependency)
- **Qdrant** = optional WAD adapter (post-debut)
- **Redis** = opt-in only (`OMEGA_REDIS_HOST` env var)
- **No default passwords** — all secrets via env vars or keyring

---

## 🔗 INTEGRATION PATTERNS

### 1. Provider Fabric
```python
# Correct: Use ModelGateway provider fabric
from omega.oracle.model_gateway import ModelGateway
gateway = ModelGateway()
result = await gateway.generate(...)

# Wrong: Direct backend imports
from omega.oracle.backends.native_gguf import NativeGGUFProvider  # NO
```

### 2. Entity Registry
```python
# Correct: Use EntityRegistry
from omega.oracle.entity_registry import EntityRegistry
registry = EntityRegistry()
entity = registry.find_by_domain("engineering")

# Wrong: Direct YAML parsing
import yaml  # NO - use registry abstraction
```

### 3. Memory Store
```python
# Correct: Use MemoryStore (abstracts vector store)
from omega.memory_store import MemoryStore
store = MemoryStore()
await store.add_exchange(...)

# Wrong: Direct sqlite-vec or Qdrant calls
```

### 4. Hivemind Coordination
```python
# Correct: Post context for team awareness
await hivemind_post_context(
    channel="opencode",
    entity="maat",
    model="current_model",
    task_current="...",
    focus_chain=[...],
    decisions=[...],
    continuation="...",
    intent="status"
)
```

---

## 🧪 TESTING STANDARDS

### 1. Contract Tests (M21)
- Every core API boundary has a contract test
- `pytest.raises(OmegaError)` for error paths
- `isinstance(result, ExpectedType)` for success paths

### 2. Temple-Grade Gates (M13)
- `make temple-grade` must pass before merge
- T3: Coverage ≥80%
- T5: AnyIO-only (no asyncio direct)
- T6: Zero telemetry
- T8: Resilience patterns
- T9: Structured logging
- T10: Atomic writes

### 3. No Vanity Metrics
- Report: passed / failed / skipped / errors
- Never "all green" or "tests pass"
- Real counts from `pytest -q --tb=no`

---

## 📦 DEPLOYMENT RULES

### 1. Podman Quadlets (M6)
- `UserNS=keep-id` + `User=1000` (never `:U` on host volumes)
- Rootless containers only
- Telemetry disabled via env vars

### 2. Systemd Units
- `MemoryMax=8G` + `Delegate=yes` for inference services
- `Restart=always` + `RestartSec=10`
- `TimeoutStartSec=300`

### 3. Secrets
- **Never in git** — `.env` gitignored, `config/github_accounts.yaml` gitignored
- **Keyring** for persistent secrets (post-debut)
- **Env vars** for runtime secrets (CI/CD)

---

## 🔧 DEVELOPMENT WORKFLOW

### 1. Claim → Plan → Verify → Execute
```bash
# 1. Claim ticket in Hivemind
# 2. Plan: read code, identify files, assess risk
# 3. Verify: read actual code paths (soul writers, gateway, guards)
# 4. Execute: smallest diff meeting Done
# 5. Test: real commands, report pass/fail/skip
# 6. Handoff: Hivemind post with what shipped
```

### 2. Commit Discipline
```bash
# Prefixes: feat: fix: docs: refactor: test: ci: chore:
# One ticket family per commit
# Never force-push main without Architect
# No secrets, soul private fragments, vault material
```

### 3. Soul Distillation (M5/M11)
```yaml
# Every session end: proposed_lessons.yaml
proposals:
  - level: L1
    narrative: "What happened?"
  - level: L2
    insight: "What does this mean?"
  - level: L3
    principle: "Timeless truth"
    domain: "engineering"  # REQUIRED for EvolveR
```

---

## 📚 REFERENCE IMPLEMENTATIONS

| Pattern | File | Status |
|---------|------|--------|
| Atomic write + fsync | `src/omega/soul_store.py` | ✅ Canonical |
| ResourceGuard semaphore | `src/omega/oracle/resource_guard.py` | ✅ Canonical |
| HealthMonitor breaker factory | `src/omega/oracle/health_monitor.py` | ✅ Canonical |
| sqlite-vec unified fabric | `src/omega/memory/sqlite_vec_adapter.py` | ✅ Canonical |
| Hybrid search (RRF) | `src/omega/memory/hybrid_search.py` | ✅ Canonical |
| Hivemind awareness | `mcp_servers/omega_hub/hub_tools/tools.py` | ✅ Canonical |
| Soul distillation | `src/omega/soul_utils.py` + session_end hook | ✅ Canonical |

---

## 🚫 ANTI-PATTERNS (BANNED)

| Anti-Pattern | Instead |
|--------------|---------|
| `asyncio.create_task()` in AnyIO | `anyio.create_task_group()` |
| Bare `except:` / `except Exception:` | Typed `except OmegaError:` + `trace_id` |
| `subprocess.run()` in async | `anyio.run_process()` |
| `git add -A` | Path-stage every commit |
| New circuit breaker class | `HealthMonitor.get_breaker()` |
| Cloud-first provider order | Local-first (native-gguf → Ollama → cloud) |
| `git add -A` | Path-stage every commit |
| New control plane | One router (ProviderSelector) |
| God-module growth >1000 lines | Split in same PR |

---

## 📜 PROVENANCE

**Curator**: maat (Build Engineering / Hardening / Integration)
**Domain**: engineering
**Governance**: SHARED_READ
**Prototype**: v0.1.0 — validates domain packaging concept for debut

*⬡ OMEGA ⬡ MAAT ⬡ hy3-free ⬡ opencode ⬡ trc_domain_engineering_playbook ⬡ 2026-08-19*