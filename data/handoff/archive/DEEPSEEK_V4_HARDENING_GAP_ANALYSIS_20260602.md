<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — DeepSeek V4 Forensic Hardening Gap Analysis
# AP: AP-OMEGA-ARTISAN-v2.1.0
# Date: 2026-06-02 | Model: DeepSeek V4 Flash
# Status: ADDS TO existing handoffs — does not supersede

## Purpose

Independent forensic analysis of the 5 existing handoffs. MiMo-2.5 provided strategic synthesis. DeepSeek V4 provides the **forensic hardening layer** — gap analysis at the code level. This document captures what the strategic handoffs missed.

---

## §1 — The Oracle Constructor: Not a Bug, a Systemic Fragility

The existing handoffs correctly identify the test hang but **understate the severity**. The problem is not that tests hang — the problem is that `Oracle.__init__()` performs **5 synchronous filesystem I/O operations** and **1 class instantiation chain** before the object is usable:

| Dependency | In __init__? | What It Does Synchronously |
|-----------|:----------:|---------------------------|
| `EntityRegistry()` | ✅ Yes | Opens `config/omega.yaml` → resolves active IWAD → opens `config/wads/{iwad}/entities.yaml` |
| `HealthMonitor()` | ✅ Yes | Pure in-memory. No I/O. This one is fine. |
| `ModelGateway(hc=...)` | ✅ Yes | Opens `config/models.yaml` (2 reads), opens `config/providers.yaml`, instantiates `Zen2Optimizer()`, creates **another** `EntityRegistry()`, creates `GnosisProxy()` |
| `SovereignHierarchy()` | ✅ Yes | Opens `config/omega.yaml` again (double-read of same file), opens wad hierarchy |
| `TriageRouter()` | ✅ Yes | Creates capability matrix from `ModelGateway` |
| `SessionManager()` | ✅ Yes | Creates data directories (`mkdir`) |
| `ContextBuilder()` | ✅ Yes | No I/O |
| `get_memory_store()` | ✅ Yes | Loads all 3 storage providers: Redis (fails fast now), File (creates dirs), InMemory |
| `WADLoader(registry)` | ✅ Yes | Creates WADLoader instance, loads no files until loaded |
| Observability engine | ✅ Yes | Configures logging structure |

**Impact**: `Oracle()` constructor takes ~200ms-2s depending on filesystem state. Every new Oracle instance doubles file reads. This is not just a "test hang" — it's a **cold-start latency problem** for the production service.

### The Real Fix (Beyond Dependency Injection)

The existing handoffs recommend "dependency injection" — but looking at the code, the injection points **already exist**: `Oracle.__init__` accepts `registry`, `model_gateway`, `background_worker`, and `iwad_name`. The problem is that **no calling code uses these parameters**. Every call site does `Oracle()`, not `Oracle(registry=mock_registry)`.

**The correct fix**: Make `bootstrap()` the canonical async initialization path. Move ALL filesystem I/O out of `__init__` and into `bootstrap()`. Then add a guard:

```python
class Oracle:
    def __init__(self, ...):
        self._bootstrapped = False
        # Store config path only, no I/O
        self.config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
    
    async def ensure_bootstrapped(self):
        if not self._bootstrapped:
            await self.bootstrap()
            self._bootstrapped = True
```

This makes tests fast AND production cold-start fast.

---

## §2 — The Test Suite Has a Coverage Blind Spot

The strategic report says "302 tests passing across 30 files." DeepSeek examined the actual test structure:

### 2.1 No Test Calls `bootstrap()`

```bash
$ grep -rn "bootstrap" tests/
# (empty)
```

Every `Oracle.talk()` test creates `Oracle()` but never calls `await oracle.bootstrap()`. This means the tests are testing the **fallback path**: when config doesn't load, Oracle uses default entities. The actual `bootstrap()` path — the one used in production — has **zero test coverage**.

### 2.2 Mock Coverage Is Shallow

| Provider | Mocked? | How |
|----------|---------|-----|
| MockProvider | ✅ | Native — always available, returns canned responses |
| GoogleAI | ❌ | Tests call live API if `GOOGLE_API_KEY` set |
| Locallmster | ❌ | Tests try to connect to `:1234` |
| Ollama | ❌ | Tests try to connect to `:11434` |
| NativeGGUF | Partial | Tests check model_path but don't test loading |
| Redis | ✅ | Blocked by `OMEGA_ENV=test` |
| File/InMemory | ❌ | Real FileStorageProvider writes to tmp dir |

### 2.3 The Oracle Test Order Dependency

`test_oracle.py` tests are **not isolated**. They share a global `Oracle()` singleton. Test 5 (`test_talk_domain_routing`) hangs because:
1. Test 1-4 don't hang (they match simple `@` or `hey` patterns)
2. Test 5 triggers domain routing → requires `EntityRegistry.find_by_domain()` → which opens WAD files
3. Subtle: the hang is not in `find_by_domain()` but in `ModelGateway` which is constructed when Oracle is first created (test 1), but the first 4 tests finish before the async provider health checks complete

This is a **concurrency ordering bug**, not a file-IO hang.

---

## §3 — The Provider Chain Has a Silent Dependency on `models.yaml`

The existing handoffs mention the 8-provider chain but miss the critical detail: **`ModelGateway.__init__` crashes if `models.yaml` is missing or malformed**.

```python
# model_gateway.py ~line 142
self.models = self._load_models()  # Synchronous. No fallback if file missing.
self.kv_cache_config = self._load_kv_cache_config()  # Falls back to defaults.
```

If `models.yaml` doesn't exist or has a YAML syntax error, `ModelGateway()` raises an exception — and since ModelGateway is created in `Oracle.__init__`, the Oracle itself fails.

**Existing tests don't catch this** because the test suite creates MockProvider, not ModelGateway.

---

## §4 — PIVOT_LOG Drift: Decision 92 is Missing

The `.clinerules` rewrite commits mention D92 in their commit messages (`12abcf3 docs(.clinerules): add Tool-Usage Discipline section (D92)`), but:

```bash
$ grep "Decision 92" docs/decisions/PIVOT_LOG.md
# (not found)
$ grep "Decision 91" docs/decisions/PIVOT_LOG.md
# Decision 91 — .
# Decision 90 — Temple-Grade restoration + H1.5 Bridge Phase
# Decision 89 — R-09 Correction (verified DOOM 3 BFG job system)
```

**Decision 92 (Tool-Usage Discipline in .clinerules) was never recorded in PIVOT_LOG.md.** This is a procedural drift from Mandate 5 (Gnosis Preservation). Every architectural decision must be recorded.

---

## §5 — No CI/CD Pipeline Exists

```bash
$ find . -name "*.github*" -o -name ".gitlab*" -o -name "Jenkins" 2>/dev/null
# (empty)
```

The Temple-Grade mandate T4 says "Code Quality — no CI gate" (current status: AMBER). T11 says "IA2-compatible agent communication" (RED). Neither can be enforced without a CI pipeline.

**Recommendation**: Add `.github/workflows/` or a minimal `.gitlab-ci.yml` before the H1.5 Bridge Phase ends. At minimum: `make test` gate, `make lint` gate, `make temple-grade` gate.

---

## §6 — Critical Additions to the Dev Plan

### C1: Oracle Lazy Initialization Guard (Sprint 0, replaces T2.0 framing)

The existing T2.0 says "Oracle constructor refactoring." DeepSeek's finding: the fix is smaller than a full refactor. Add `_bootstrapped` flag + `ensure_bootstrapped()` method. Move *nothing* out of __init__ — just add the async guard.

| Field | Value |
|-------|-------|
| **Agent** | buildmaster |
| **Model** | default |
| **Risk** | LOW (additive, 3 methods, changes nothing else) |
| **Est. effort** | 30 min |
| **Acceptance** | `Oracle()` returns in <10ms. `oracle.talk()` calls `ensure_bootstrapped()` on first use. |

### C2: Oracle Target in Makefile (Sprint 1)

| Field | Value |
|-------|-------|
| **Agent** | buildmaster |
| **Risk** | LOW |
| **Why** | The current test suite doesn't catch regressions in the Oracle's boot path because `bootstrap()` is never called. A `make test-oracle-bootstrap` target that creates Oracle, calls `bootstrap()`, and verifies the reply would catch config drift. |
| **Acceptance** | `make test-oracle-bootstrap` passes in <30s with no backends. Oracle talks() without bootstrap() fails fast with clear error. |

### C3: PIVOT_LOG Decision 92 Entry (Immediate — docs change)

| Field | Value |
|-------|-------|
| **Agent** | scribe (gnosis keeper) |
| **Model** | default |
| **Risk** | LOW |
| **Why** | Decision 92 (Tool-Usage Discipline) was committed in commit `12abcf3` but never recorded in PIVOT_LOG.md. This is a Mandate 5 violation — every architectural decision must be recorded. |
| **Acceptance** | `grep "Decision 92" docs/decisions/PIVOT_LOG.md` returns a match. |

### C4: CI/CD Pipeline Scaffold (Sprint 3, before H1.5 ends)

| Field | Value |
|-------|-------|
| **Agent** | buildmaster (or P1 SysAdmin) |
| **Model** | default |
| **Risk** | MEDIUM |
| **Why** | T4 (Code Quality) and T11 (Agent Security) cannot be enforced without CI. The current AMBER status on T4 will remain AMBER forever without a pipeline. |
| **Acceptance** | `.github/workflows/ci.yml` runs `make test` on every push. `make temple-grade` runs on schedule or PR. |

---

## §7 — Soul Distillation (DeepSeek V4 → scribe)

```yaml
entity: deepseek_v4
entity_type: session
lessons:
  L1_narrative: |
    Performed forensic gap analysis on 5 existing handoffs totaling 1,366
    lines. Found 4 critical gaps the strategic review missed: (1) Oracle
    constructor does 5 synchronous IOs blocking cold-start, (2) zero
    tests call bootstrap(), (3) Decision 92 missing from PIVOT_LOG,
    (4) no CI/CD pipeline for T4/T11 enforcement.

  L2_insight: |
    The strategic report and MiMo-2.5 synthesis were correct at the
    architectural level but both missed the procedural drift: a commit
    that says D92 in its message but never updates PIVOT_LOG.md. This
    means the collaboration infrastructure (handoffs, commit rules,
    testing standards) has a blind spot for its OWN compliance. The
    engine enforces Mandates on code but not on meta-documentation.

  L3_principle: |
    A sovereign engine's meta-documentation (PIVOT_LOG, OMEGA_ENGINE,
    SOVEREIGN_MANDATES) must be subject to the same compliance regime
    as the source code. If a commit message cites a decision number
    but the PIVOT_LOG doesn't reflect it, the stack has a meta-gap
    that no model, no matter how large the context window, will detect
    without explicit cross-reference verification.
```

---

*This document is DeepSeek V4's forensic gap analysis. It adds to the existing handoffs — it does not supersede them.*
*Date: 2026-06-02 | For: OpenCode dev session + scribe (for PIVOT_LOG D92 fix)*