<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Sonnet 4.6 Sprint Gate Audit — Omega Engine H1.5 Bridge Phase
**Auditor**: Claude Sonnet 4.6 (independent review, 2026-06-02T18:53 UTC)
**Prepares for**: Opus 4.6 Final Deep Audit
**Baseline**: 302/302 tests passing per OMEGA_ENGINE.md (2026-06-01)
**Verdict**: **🟡 AMBER — Proceed with targeted blitz patches before sprint launch**

---

## ⚙️ Audit Method

This audit reads code directly. Every finding has a `file:line` citation. Where OMEGA_ENGINE.md or handoff documents contradict what the code actually does, the **code is treated as ground truth** per the sprint prompt's own rule: *"if you find a conflict between these docs and the actual code, the actual code prevails."*

---

## 🟥 P0 — Critical Bugs (Must Fix Before Sprint Launch)

### P0-1: `summon()` never calls `bootstrap()` — WADs not loaded on direct summon

**File**: `src/omega/oracle/oracle.py:345-361`

`talk()` correctly gates on `await self.bootstrap()` at line 291. `summon()` does **not**:

```python
# oracle.py:291 — CORRECT
async def talk(self, query, transient=False):
    await self.bootstrap()   # ← WADs loaded here
    ...

# oracle.py:353 — MISSING bootstrap call
async def summon(self, entity_name, query, transient=False):
    async with self.observability.trace() as trace:   # ← no bootstrap
        ...
```

**Also affected**: `evolve_soul()` at line 868 — no `bootstrap()` call either.

**Impact**: Every test that calls `Oracle().summon(...)` directly runs without WAD loading. Hierarchy path is `None`, soul path is `None`, default entity may be wrong. The test suite masks this because `test_summon_direct` creates a fresh Oracle and the `EntityRegistry.__init__` sync load gives baseline entities — but WADs are never overlaid, and `self.config` stays `{}`.

**Fix**: Add `await self.bootstrap()` as the first line in `summon()` and `evolve_soul()`, matching `talk()`.

---

### P0-2: Four confirmed synchronous filesystem reads in `Oracle.__init__`

**Files**: Multiple — all triggered by `Oracle.__init__` before any async context exists.

| Sync I/O site | File | Line | What it reads |
|---|---|---|---|
| `EntityRegistry().__init__` | `oracle/entity_registry.py` | 84-97 | `omega.yaml` + `entities.yaml` |
| `ModelGateway().__init__` → `_load_models()` | `oracle/model_gateway.py` | 99, 215 | `models.yaml` |
| `ModelGateway().__init__` → `_load_kv_cache_config()` | `oracle/model_gateway.py` | 100, 223 | `models.yaml` (second read) |
| `ModelGateway().__init__` → `_load_provider_fabric()` | `oracle/model_gateway.py` | 109, 174 | `providers.yaml` |
| `ModelGateway.__init__` → `EntityRegistry()` | `oracle/model_gateway.py` | 112 | `omega.yaml` + `entities.yaml` (duplicate!) |
| `SovereignHierarchy().__init__` | `oracle/hierarchy.py` | 21-28 | `omega.yaml` |

`EntityRegistry` is loaded **twice**: once directly in `Oracle.__init__:101` and once inside `ModelGateway.__init__:112`. This is redundant and doubles the sync I/O cost.

**Current state of `bootstrap()`**: The method guards on `_wads_loaded` (not `_bootstrapped`) and loads WADs + config asynchronously. But all 5 sync reads above happen *before* bootstrap is ever called — during `__init__`.

**Note for sprint prompt alignment**: The sprint prompt C1 refers to `_bootstrapped` flag and `ensure_bootstrapped()`. The actual code uses `_wads_loaded` and `bootstrap()`. The rename should be intentional if done — or the sprint prompt should be corrected to match existing naming.

---

### P0-3: `_precheck_provider` culls all fallbacks when primary provider is OPEN

**File**: `src/omega/oracle/model_gateway.py:395-420`

```python
async def _precheck_provider(self, provider, model_name: str) -> bool:
    if self._health_monitor:
        if not self._health_monitor.is_available(model_name):
            return False   # ← model_name → primary provider lookup
```

`HealthMonitor.is_available(model_name)` at `health_monitor.py:266-272` resolves `model_name` → its mapped primary provider → checks *that* provider's breaker. In the loop over all 7 providers in `generate()`, every provider is checked against the *same* model's primary provider. When provider 0 (native-gguf) is OPEN, `is_available("qwen3-1.7b")` returns `False` — and every subsequent provider (lmster, ollama, google, cline…) is also culled because they all use the same model name lookup.

**The fallback chain is dead when any primary provider trips.**

**Fix**: Check the candidate provider's own breaker directly:
```python
if self._health_monitor:
    breaker = self._health_monitor._breakers.get(provider.name)
    if breaker and not breaker.is_available:
        return False
```

---

### P0-4: `RemoteProvider.generate()` returns `None` on retry exhaustion — circuit breaker never trips

**File**: `src/omega/oracle/backends/remote_provider.py:207-208`

```python
# After all retries exhausted:
logger.error(f"Provider {self.name} exhausted all retries. Last error: {last_error}")
return None   # ← silent None, no exception raised
```

When `ModelGateway.generate()` calls `await breaker.call(provider.generate, ...)`, the breaker's `_is_circuit_breaking_error()` is only triggered when `func()` **raises**. Since `RemoteProvider.generate()` catches and swallows all exceptions internally, `breaker.call()` receives a successful `None` return — breaker records a success, resets failure count. **The circuit breaker for all RemoteProvider subclasses (opencode-zen, cline, copilot) will never open.**

`LocallmsterProvider`, `OllamaProvider`, `GoogleAIProvider` in `providers.py` are different — they raise typed `ProviderError` subclasses on failure. Only `RemoteProvider` (used by OpenAI-compat backends) has this bug.

**Fix**: After retry exhaustion, raise `ProviderUnavailableError` instead of returning `None`.

---

## 🟠 P1 — Significant Issues (Fix Before or During Sprint)

### P1-1: Dead code — OpenRouter retry policy and `_call_provider_with_resilience`

**File**: `src/omega/oracle/model_gateway.py:57-75, 512-530`

OpenRouter was removed per Decision 90. However the file still defines:
- `OpenRouterTransientError` class (line 57)
- `OpenRouterFatalError` class (line 61)
- `openrouter_retry_policy` decorator (line 69-75, using `tenacity`)
- `_call_provider_with_resilience()` method (line 512) decorated with `@openrouter_retry_policy`

None of these are called anywhere in the active code path. `tenacity` is imported at lines 31-37 purely to support this dead code.

**Impact**: Dead code adds cognitive overhead; `tenacity` remains a live dependency that could conflict. This is also a Mandate 9 risk — if `_call_provider_with_resilience` is ever mistakenly called, the swallowed errors inside it won't propagate correctly.

---

### P1-2: Mandate 9 — three remaining `except Exception:` without logging

**Confirmed by grep across `src/omega/`**:

| File | Line | Context | Severity |
|---|---|---|---|
| `oracle/health_monitor.py` | 140 | `except Exception: pass` — circuit state transition silently swallowed | HIGH |
| `oracle/health_monitor.py` | 165 | `except Exception: pass` — same silent swallow in `_on_failure` | HIGH |
| `oracle/model_gateway.py` | 370 | `except Exception:` with `logger.debug(..., exc_info=True)` | ACCEPTABLE (per HANDOFF_OPTION_B line 14: "Leave it") |
| `workers/background_researcher/searxng_client.py` | 92 | `except Exception:` — needs review | MEDIUM |

`health_monitor.py:140,165` — these are the observability emit blocks inside `_on_success` / `_on_failure`. They say `except Exception: pass` (the comment says "Circuit works silently if observability unavailable"). Strictly these violate Mandate 9 but were likely intentional. A `logger.debug()` would satisfy the mandate without changing behavior.

**Note**: `oracle.py:912` bare except is **legitimate** — it's cleanup-before-reraise for temp file removal. Not a violation.

---

### P1-3: `PIVOT_LOG.md` ends at Decision 90 — D91 and D92 are missing

**File**: `docs/decisions/PIVOT_LOG.md:1452`

The file ends with Decision 90 (Temple-Grade Mandate 13 Restoration). The last line reads: *"PIVOT_LOG.md — Immutable. Every decision recorded. 89 decisions tracked."* (line 1423) — but Decision 90 was then added. The sprint task C3 says to add Decision 92 (Tool-Usage Discipline). However, Decision 91 is also absent — the OpenRouter removal and provider fabric reconciliation has no PIVOT_LOG entry, violating **Mandate 5 (Gnosis Preservation)**.

**Required entries**:
- **D91**: OpenRouter removal & provider fabric reconciliation (7→8 providers, fabric reordered, `openrouter_retry_policy` left as dead code)
- **D92**: Tool-Usage Discipline (model context limits, local-first routing discipline)

---

## 🟡 P2 — Stale/Contradictory Handoff Claims (Correct Before Handing to Opus)

### P2-1: OMEGA_ENGINE.md claims Doom Guy circuit breaker work is DONE — it's not fully correct

**File**: `OMEGA_ENGINE.md:152-153`

```
ModelGateway.generate() | WIRED — circuit breaker + BSP culling + per-provider timeouts | 2026-06-01 (Doom Guy)
Circuit Breaker | Consolidated — single AsyncCircuitBreaker in health_monitor.py | 2026-06-01 (Doom Guy)
```

These entries are **partially accurate** — the code structure is correct, `circuit_breaker.py` is deleted, `generate()` has the integration scaffolding. But P0-3 and P0-4 above are confirmed bugs in the integration. The SST should be corrected to reflect that integration is scaffolded but contains functional bugs requiring sprint D-tasks.

---

### P2-2: Sprint prompt says circuit_breaker.py needs deletion — it's already deleted

**File**: Sprint prompt `PROMPT_OPENCODE_DOOM_GUY_SPRINT_INIT_20260602.md:Task D2`

`circuit_breaker.py` does not exist: `ls src/omega/oracle/circuit_breaker.py → No such file or directory`. No import references remain in Python source files. The task D2 deletion portion is already done.

**Action**: D2 should be marked as partially complete. The remaining D2 work (removing legacy `consecutive_failures` metrics from `remote_provider.py` per Doom Guy handoff §Task 5) is still valid.

---

### P2-3: Sprint prompt says CI/CD needs to be created (Task C4) — two workflows already exist

**Files**: `.github/workflows/ci.yml` (May 14), `.github/workflows/test.yml` (May 25)

`ci.yml`: Basic flake8 lint + pytest + doc lint. Does NOT enforce `make temple-grade`.
`test.yml`: More complete — matrix Python 3.12/3.13, import verification, lint (non-blocking). Also does NOT enforce temple-grade gates.

**Task C4 should be reframed**: Not "create CI" but "harden existing CI with temple-grade gates T4 (code quality blocking) and T5 (AnyIO-only check)". The T11 gate is correctly exempted.

---

### P2-4: `observability.py` bugs cited in HANDOFF_OPTION_B are ALREADY FIXED

**File**: `HANDOFF_OPTION_B_OPENCODE.md` (Opus 4.6 findings, the currently open file)

Per direct code inspection:
- `_collect_system_info()` structural bug (dead code / no return): **FIXED** — `observability.py:270` now correctly returns `info`
- `asyncio` direct import in `_detect_anyio_backend()`: **FIXED** — now uses `sniffio` at line 280-281
- `deque` slicing bug in `recent_events()`: **FIXED** — uses indexed access at lines 586-587

The OMEGA_ENGINE.md (lines 277-279) confirms these fixes. HANDOFF_OPTION_B_OPENCODE.md is a historical document; its Opus findings have been executed.

---

## ✅ Verified Clean — No Action Needed

| Component | Status | Evidence |
|---|---|---|
| `circuit_breaker.py` | Deleted | `ls` → Not found; no imports in src/ |
| `asyncio` in observability | Fixed | `sniffio` at observability.py:280 |
| `_collect_system_info()` | Fixed | Returns `info` at observability.py:270 |
| `deque` slicing | Fixed | Indexed access at observability.py:586-587 |
| Mandate 1 (AnyIO) | Clean | Zero `import asyncio` in all of `src/omega/` |
| Mandate 8 (Telemetry) | Clean | No analytics/posthog/datadog imports found |
| `AsyncCircuitBreaker.call()` trace_id | Done | `_on_success`/`_on_failure` accept `trace_id` at health_monitor.py:116,123,143 |
| Bare except in oracle.py:912 | Legitimate | Cleanup-before-reraise pattern — not a M9 violation |
| `remote_provider.py` `is_available()` | Async | Correctly declared `async def is_available()` at line 128 |

---

## 📋 Corrected Sprint Task Execution Plan

### OpenCode Dev Sprint 0 (ordered by dependency)

```
C3 → C1 → C2 → C4
```

**C3 — PIVOT_LOG Recovery** *(5 min, LOW risk)*
Add Decision 91 (OpenRouter removal + provider fabric reconciliation) then Decision 92 (Tool-Usage Discipline) to `docs/decisions/PIVOT_LOG.md`. Update footer count to 92.

**C1 — Oracle Bootstrap Guard** *(45 min, MEDIUM risk)*

The actual fix is broader than the sprint prompt describes. Two parts:

*Part A*: Add `await self.bootstrap()` to `summon()` (line 353) and `evolve_soul()` (line 868). This is a **2-line fix** and closes P0-1 immediately.

*Part B*: For the async init pattern, the naming in the sprint prompt (`_bootstrapped`, `ensure_bootstrapped()`) conflicts with existing code (`_wads_loaded`, `bootstrap()`). **Recommended**: keep existing naming, just ensure all public async entry points call `bootstrap()`. Do not rename unless Opus 4.6 decides otherwise.

*Part C*: The `ModelGateway.__init__:112` duplicate `EntityRegistry()` instantiation should be removed or made to reuse the Oracle's registry.

**C2 — Makefile target** *(10 min, LOW risk)*

```makefile
test-oracle-bootstrap: ## 🧪 Test Oracle bootstrap path (WAD loading, config, hierarchy)
	OMEGA_ENV=test $(PYTHON) -m pytest tests/test_oracle.py -k "bootstrap or summon or talk" -v
```

**C4 — CI Hardening** *(30 min, LOW risk)*

Both workflow files exist. Harden `test.yml` to add:
1. `make lint` (flake8, blocking) — satisfies T4
2. AnyIO-only check: `grep -r "import asyncio" src/omega/ && exit 1 || exit 0` — satisfies T5

---

### Doom Guy Tier 2 (after Sprint 0 is green)

**D2 — Partial cleanup only** *(15 min)*
- `circuit_breaker.py` is already deleted — skip deletion
- Remove `consecutive_failures` tracking from `remote_provider.py` (lines 43-44, 186-196) — delegate to HealthMonitor

**D3 — Verify trace_id propagation** *(5 min — already done)*
- `AsyncCircuitBreaker._on_success()` and `_on_failure()` already accept and propagate `trace_id`
- Just verify with grep and move on

**D1 — Fix `_precheck_provider` bug** *(30 min, P0-3)*
- Replace model-name breaker lookup with provider-name lookup (see P0-3 fix above)

**D4 — Fix `RemoteProvider` silent return** *(45 min, P0-4)*
- `remote_provider.py:207-208` must raise `ProviderUnavailableError` after retry exhaustion
- This activates the circuit breaker for all cloud providers

**D5 — Dead code removal** *(15 min)*
- Remove `OpenRouterTransientError`, `OpenRouterFatalError`, `openrouter_retry_policy`, `_call_provider_with_resilience` from `model_gateway.py`
- Drop `tenacity` import if no other usage (verify with grep)

---

## 🔑 Key Findings Summary for Opus 4.6

| # | Finding | Severity | File:Line | State |
|---|---|---|---|---|
| 1 | `summon()` missing `bootstrap()` call | P0 | `oracle.py:353` | 🔴 Bug |
| 2 | `evolve_soul()` missing `bootstrap()` call | P0 | `oracle.py:868` | 🔴 Bug |
| 3 | 6 sync I/O calls in `Oracle.__init__` | P0 | Multiple (see P0-2) | 🔴 Bug |
| 4 | `_precheck_provider` culls all providers via wrong breaker lookup | P0 | `model_gateway.py:404` | 🔴 Bug |
| 5 | `RemoteProvider.generate()` returns `None` → breaker never trips | P0 | `remote_provider.py:208` | 🔴 Bug |
| 6 | `OpenRouter*` dead code + tenacity dep | P1 | `model_gateway.py:57-75,512` | 🟠 Cleanup |
| 7 | `health_monitor.py:140,165` bare except without logging | P1 | `health_monitor.py:140,165` | 🟠 M9 |
| 8 | PIVOT_LOG missing D91 and D92 | P1 | `PIVOT_LOG.md:1452` | 🟠 M5 |
| 9 | CI workflows exist but lack temple-grade gates | P2 | `.github/workflows/*.yml` | 🟡 Harden |
| 10 | D2 deletion portion already done | P2 | Verified by `ls` | ✅ Stale claim |
| 11 | Observability bugs (Opus HANDOFF_OPTION_B findings) already fixed | P2 | `observability.py:270,280,586` | ✅ Stale claim |
| 12 | OMEGA_ENGINE.md Doom Guy claim partially inaccurate | P2 | `OMEGA_ENGINE.md:152-153` | 🟡 Update SST |
| 13 | `_bootstrapped`/`ensure_bootstrapped` naming mismatch vs actual code | P2 | Sprint prompt vs `oracle.py:162,172` | 🟡 Align |

---

## 📐 Mandate Compliance Scorecard

| Mandate | Status | Evidence |
|---|---|---|
| M1 — AnyIO Absolute | ✅ GREEN | Zero `import asyncio` in src/omega/ |
| M2 — Engine-Stack Firewall | ✅ GREEN | No WAD content in src/ |
| M3 — Iris Constant | ✅ GREEN | Iris is messenger, not Pillar |
| M4 — Sequentiality | ✅ GREEN | Plan exists, verified before sprint |
| M5 — Gnosis Preservation | 🟠 AMBER | D91+D92 missing from PIVOT_LOG |
| M6 — Podman Sovereignty | ✅ GREEN | `keep-id` confirmed in Quadlets |
| M7 — Local-First | ✅ GREEN | native-gguf(0)→lmster(1)→ollama(2) verified |
| M8 — Zero Telemetry | ✅ GREEN | No external telemetry found |
| M9 — Error Integrity | 🟠 AMBER | `health_monitor.py:140,165` bare except without log; `remote_provider.py:208` silent None |
| M10 — Fleet Integrity | ✅ GREEN | 14 agent files confirmed |
| M11 — Soul Integrity | ✅ GREEN | Atomic soul writes verified |
| M12 — Queue Integrity | ✅ GREEN | Request queue uses atomic claims |
| M13 — Temple-Grade | 🟡 AMBER | CI exists but doesn't enforce gates T4/T5 |

---

*Audit complete. Hand to Opus 4.6 with this document as primary context.*
*Opus should focus on: (1) validate P0-4 fix approach for RemoteProvider, (2) decide on bootstrap naming (keep vs rename), (3) rule on tenacity/OpenRouter dead code approach.*
