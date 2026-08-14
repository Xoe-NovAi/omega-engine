# 🔱 COPILOT CLI BRIEFING — Carnak Strip-the-Engine Review
**AP Token**: `AP-COPilot-CLI-BRIEFING-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ big-pickle ⬡ opencode ⬡ trc_carnak_briefing ⬡ COPILOT-FLEET

**Date**: 2026-07-30
**Purpose**: Comprehensive briefing for Copilot CLI to perform code review and strategic evaluation of the Omega Engine after the "Temple Cleansing" decisions. Validate the implementation plan and identify any risks or gaps.

---

## §0 SESSION CONTEXT

This session produced a definitive architectural verdict from four independent agents (John Carmack, Lilith, Ma'at, Roc_Racoon) plus two LLM architects (Gemini 3.1 Pro, Sonnet 4.6). The mandate:

> **"I want this first release to be nothing but the systems and methods we will still be using in 5 years in one form or another, not something that will plague us for the next 5 years."**

The consensus: **The Omega Engine is suffering from severe NIH syndrome and microservice-scale over-engineering applied to a single-user desktop application.**

---

## §1 THE VERDICT: What Gets Cut (Definitive)

### 1.1 Systems to DELETE Entirely (Unanimous + Architect Consensus)

| System | Files | Lines | Replacement |
|--------|-------|-------|-------------|
| **OOM/PSI/Cgroup Kernel Polling** | `cgroup_pressure.py`, `psi_monitor.py`, `memavailable.py` | ~840 | `psutil.virtual_memory().available` (3 lines) |
| **CascadeRouter + TokenEstimator + QuotaTracker** | `cascade_router.py`, `token_estimator.py`, `quota_tracker.py` | ~1,125 | Hardcoded priority list: `["native-gguf", "lmster", "antigravity", "google"]` |
| **SoulHistory / SoulEditHistory** | `soul_history.py`, `soul_edit_history.py` | ~470 | Git (existing VCS) |
| **MCP Compliance Module** | `mcp_compliance.py` | 826 | Official MCP Inspector |
| **Quadlet Test Directory** | `quadlet-test/` | 6 files | Archive/Delete |
| **Custom Circuit Breakers** | `health_monitor.py`, `search_circuit_breaker.py`, `failure_registry.py` | ~1,630 | `tenacity` (already in deps) |
| **DPO Logger Hot Path** | `dpo_logger.py` integration in `oracle.py` | ~50 | Remove — no training pipeline exists |

### 1.2 Systems to REPLACE (Architect Consensus)

| System | Current | Replacement | Why |
|--------|---------|-------------|-----|
| **Memory/Conversation Store** | 7,400 lines, 19 files, 5 providers, 3 vector stores | Single SQLite + FTS5 | Vector search is for Document RAG, not chat history |
| **LocalWorkerPool** | 730 lines file-based polling | `anyio.Queue` + TaskGroup | Zero I/O, zero latency, no crash-recovery needed for local chat |
| **Entity Registry** | 944 lines, SymbolicMetadata, custom CRUD | Pydantic model + `yaml.safe_load()` | Standard pattern in LangChain/CrewAI/PydanticAI |
| **Provider Routing** | Weighted scoring | Priority list | First available wins — no scoring bug possible |

---

## §2 THE 5-YEAR CORE LOOP (What Survives)

The initial PR must do exactly one loop flawlessly:

```
Receive Prompt → Pick Best Available Model (Local > Cloud) → Generate → Save to SQLite → Distill to YAML
```

**Systems that earn their place (Keep As-Is):**

| System | Why |
|--------|-----|
| **SoulStore** (217 lines) | Well-engineered atomic writer with 4-layer guarantee. Single responsibility. |
| **ProviderSelector** (93 lines) | Simple, correct, priority-first routing with health awareness. |
| **NativeGGUFProvider / OpenAICompatProvider / AntigravityProvider** | Core value: load model, run inference, return result. |
| **Hivemind Coordination** (file-based) | Simple, debuggable, works for single-user. No Redis dependency. |
| **Pre-commit Mandate Hooks** | Fast, real, catch violations. (Trim: replace `make` indirection with direct `rg`). |
| **ResourceGuard** (semaphore + cancellation) | Prevents resource contention on 15W TDP. Keep admission control, swap OOM signal to psutil. |
| **Test Quarantine System** | Adds honesty. Fix: badge must report HANG/INCOMPLETE if suite doesn't complete. |

---

## §3 IMPLEMENTATION GUIDE (The "Temple Cleansing")

### Phase 1: The Great Pruning (Burn the Scaffolding)
```bash
# 1. Eradicate OOM/Kernel Polling Theater
rm src/omega/oracle/cgroup_pressure.py
rm src/omega/oracle/psi_monitor.py
rm src/omega/oracle/memavailable.py

# 2. Eradicate Routing Bloat
rm src/omega/oracle/cascade_router.py
rm src/omega/oracle/token_estimator.py
rm src/omega/oracle/quota_tracker.py

# 3. Eradicate Cryptographic Theater & Compliance Bloat
rm src/omega/oracle/soul_history.py
rm src/omega/oracle/soul_edit_history.py
rm src/omega/mcp_compliance.py
rm -rf quadlet-test/
```

**Code Changes Required:**
- In `resource_guard.py` / `oom_protector.py`: Replace admission logic with `psutil.virtual_memory().available`
- In `model_gateway.py`: Ensure `ProviderSelector` iterates hardcoded priority list only

### Phase 2: The 5-Year Foundation (Wire the Core)

**1. Resilience Layer — Replace Custom Breakers with Tenacity**
```python
# In provider classes (e.g., OpenAICompatProvider)
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
)
async def generate(self, ...):
    # Standard generation logic
```

**2. Memory Layer — Single SQLite + FTS5**
```sql
-- Schema
CREATE TABLE exchanges (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    entity TEXT,
    role TEXT,
    content TEXT,
    timestamp DATETIME
);
CREATE VIRTUAL TABLE exchanges_fts USING fts5(content, content=exchanges, content_rowid=rowid);
```

**3. Background Worker — anyio.Queue**
```python
import anyio

class LocalWorker:
    def __init__(self):
        self.queue = anyio.Queue(50)
        
    async def start(self):
        async with anyio.create_task_group() as tg:
            while True:
                task = await self.queue.get()
                tg.start_soon(self.execute, task)
```

### Phase 3: Unblocking the PR (CI & Governance)

1. **Merge CI**: Delete `ci.yml`, merge mandate checks into `test.yml`
2. **Trim Makefile**: Delete `generate-badge`, `load-quarantine`, `doc-llm-validate`, `doc-token-check`, `doc-chunk-sprint`, `sprint-plan-llm*`, `check-codex-stale`, `check-codex-force`
3. **Fix `make test`**: `pytest -v --timeout=30` (will pass once async polling loops are deleted)
4. **Entity Consolidation**: Move non-operational entities to `data/entities/archive/`

---

## §4 DEFINITION OF DONE FOR THIS PR

1. ✅ `make test` completes in under 30 seconds with **zero hangs**
2. ✅ Codebase is **~20,000 lines lighter**
3. ✅ Submit prompt → engine routes locally via priority list → generates → saves to SQLite
4. ✅ **No background polling loops** running while engine is idle
5. ✅ `make temple-grade` passes
6. ✅ `make check-mandates` passes

---

## §5 SPECIFIC REVIEW REQUESTS FOR COPILOT CLI

Please review the following and provide feedback:

### 5.1 Code Review Targets (Post-Pruning)
- `src/omega/oracle/resource_guard.py` — Verify psutil replacement is correct
- `src/omega/oracle/model_gateway.py` — Verify ProviderSelector uses priority list only
- `src/omega/oracle/providers.py` — Verify tenacity decorators on generate methods
- `src/omega/memory/conversation_store.py` (new) — Verify SQLite + FTS5 implementation
- `src/omega/worker/local_worker.py` (new) — Verify anyio.Queue implementation

### 5.2 Architecture Questions
1. **Is the priority list `["native-gguf", "lmster", "antigravity", "google"]` correct for M7 Local-First compliance?**
2. **Does the SQLite schema support the soul distillation pipeline (L1→L2→L3)?**
3. **Are there any hidden dependencies on the deleted modules (imports in other files)?**
4. **Does the anyio.Queue worker properly handle graceful shutdown on SIGTERM?**

### 5.3 Risk Assessment
1. **What breaks if we delete `cgroup_pressure.py` / `psi_monitor.py` imports elsewhere?**
2. **Does the test suite actually pass after these deletions? (The hang was likely caused the hang)**
3. **Is `tenacity` retry sufficient for provider failures, or do we need a minimal circuit breaker for cloud quota exhaustion?**
4. **Does the file-based Hivemind coordination still work without the custom queue?**

### 5.4 Strategic Validation
1. **Does this architecture support the Phase D gate requirements?**
2. **Can the V-1 VaultCore be built on top of this simplified foundation?**
3. **Does the Identity Fluidity (E-0) work with Pydantic entity configs?**

---

## §6 SOURCE CONTEXT — Agent Reviews

| Agent | task_id | Focus |
|-------|---------|-------|
| **John Carmack** | `ses_carmack_strip_20260730` | First-principles architecture, scope cutting |
| **Lilith** | `ses_lilith_strip_20260730` | Run-side: cognition, context, observability |
| **Ma'at** | `ses_maat_strip_20260730` | Build-side: infra, persistence, CI/CD |
| **Roc_Racoon** | `ses_roc_strip_20260730` | Implementation pragmatism, legacy patterns |
| **Gemini 3.1 Pro** | Session synthesis | Strategic verdict + implementation guide |
| **Sonnet 4.6** | Session synthesis | 5-year foundation insight + cleansing guide |

---

*⬡ OMEGA ⬡ KALI ⬡ COPILOT-CLI ⬡ CARNAK-BRIEFING ⬡ 2026-07-30*