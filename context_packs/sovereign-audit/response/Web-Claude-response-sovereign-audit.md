---
account: arcana.novai@gmail.com
pack_version: 2026-08-08
pack_profile: sovereign-audit
pack_files: 32
pack_tokens: 173464
session_date: 2026-08-08
session_type: audit
---

# Sovereign Architecture Audit Report

## 1. Executive Summary

The Omega Engine's provider fabric and memory layer show disciplined AnyIO usage in the newer modules (`sqlite_vec_adapter.py`, `resource_guard.py`, `oom_protector.py`) but the audit surfaces one severe, concrete correctness bug — a hardcoded cloud-provider set in `model_gateway.py` that silently miscounts Antigravity/Anthropic/xAI as "local," which corrupts the exact sovereignty metric M7/M22 exist to protect. Combine that with a self-contradicting M14 heritage claim ("All vetted" vs. two files with un-migrated tags) and a project-acknowledged broken M23 enforcement gate, and the honest verdict is: **mechanically PASS on paper, materially FAIL on at least two mandates whose entire purpose is truth-telling about sovereignty and provenance.**

## 2. Mandate Compliance Matrix

| Mandate | Status | Violations Found | Files Affected |
|---|---|---|---|
| M1 AnyIO | PARTIAL | No raw `asyncio` imports found in the pack, but several synchronous SQLite writes execute on the event loop without `anyio.to_thread.run_sync` | `observability.xml: metrics_db.py`, `memory.xml: fts_index.py` |
| M2 Firewall | PARTIAL | Model-specific (Gemma) logit-bias/token-ID hack hardcoded directly into `ModelGateway.generate()` | `oracle_core.xml: model_gateway.py` |
| M7 Local-First | FAIL | `_cloud_providers` hardcoded set omits 4 of 8 cloud providers, breaking local-vs-cloud tiering logic that M7 depends on | `oracle_core.xml: model_gateway.py` |
| M8 Zero Telemetry | PASS | No external network calls in observability code found; MetricsDB is local SQLite only | `observability.xml` |
| M9 Error Integrity | FAIL | Multiple bare/broad `except Exception` blocks that swallow silently with no logging or trace_id | `oracle_core.xml: providers.py`, `oracle_support.xml: oom_protector.py`, `memory.xml: memory_store.py` |
| M13 Temple-Grade | FAIL | Self-contradicting compliance figures within the same SSOT document (92% vs. 84%); acknowledged full-suite test timeout risk | `mandates.xml: OMEGA_ENGINE.md` |
| M14 Heritage | FAIL | "All vetted" claim directly contradicted by dated reconciliation finding of un-migrated tags | `mandates.xml: OMEGA_ENGINE.md` vs `strategy_core.xml: UNOVERENGINEERING_PLAN.md` |
| M22 Provenance | FAIL | Same root cause as M7 — `is_cloud` field on `GenerateResult` is corrupted for 4 providers because it's derived from the broken hardcoded set, not the config-driven `provider.is_cloud` attribute | `oracle_core.xml: model_gateway.py` |
| M23 Failure Integrity | FAIL (self-reported) | Project's own reconciliation doc states the M23 pre-commit gate is broken and passing falsely | `strategy_core.xml: UNOVERENGINEERING_PLAN.md` |
| M24 Venv Sovereignty | CANNOT VERIFY | No shell/CI evidence in this pack; only the historical incident that prompted the mandate is documented | `mandates.xml: SOVEREIGN_MANDATES.md` |
| M25 Streaming Resilience | PARTIAL | `providers.yaml` sets `chunk_timeout_ms` per provider (compliant), but AGENTS.md documents a separately configured `chunkTimeout: 60000` in `opencode.json` for the same `opencode` provider — two sources of truth, unsynchronized | `config.xml: providers.yaml` vs `mandates.xml: AGENTS.md` |

## 3. Critical Violations (MUST FIX)

### 3.1 — M7/M22: Sovereignty ratio is silently wrong for 4 of 8 cloud providers

**File**: `oracle_core.xml → model_gateway.py`

```python
@property
def _cloud_providers(self) -> set:
    """Set of cloud provider names for sovereignty tracking."""
    return {"google", "openrouter", "opencode-zen", "cline"}

def _is_cloud_provider(self, provider) -> bool:
    """Check if a provider is a cloud provider."""
    return provider.name in self._cloud_providers
```

Compare against `config.xml → providers.yaml`, where `is_cloud: true` is explicitly declared for **eight** providers: `antigravity`, `google`, `google-compat`, `openrouter`, `opencode-zen`, `cline`, `anthropic`, `xai`. The loader even sets this on the instance:

```python
provider.is_cloud = p_cfg.get("is_cloud", True)
```
(`_load_provider_fabric`, same file)

But that attribute is **never read**. `_is_cloud_provider()` consults only the hardcoded 4-item frozenset. Antigravity — described in `strategy_core.xml` as "**primary cloud**" (`§7 Provider Fabric`) — along with `anthropic`, `xai`, and `google-compat`, will be classified as *not cloud*.

**Downstream damage, all traced through the same call site (`generate()`)**:
- `GenerateResult.is_cloud=self._is_cloud_provider(success_provider)` — the M22 provenance field is wrong for these providers.
- `_update_active_set()` sovereignty-tiered LRU (`is_cloud = self._is_cloud_provider_name(provider_name)`) puts Antigravity responses in the **local** active set.
- The Sovereign Budget Gate (`if self._is_cloud_provider(provider) and entity_name: check_budget(...)`) never runs for Antigravity/xAI/Anthropic — cloud spend on these providers is ungated.
- `tracker.record(..., is_cloud=self._is_cloud_provider(provider))` feeds `MetricsDB.performance.is_cloud`, which `sovereignty.py`'s `get_sovereignty_ratio()` (`observability.xml`) reads directly to compute the local/cloud ratio that `make sovereignty` reports.

This is the exact failure mode M22 was written to prevent: *"If the log says local but the response came from cloud, sovereignty is a lie."* Here the code, not just a log message, treats it as local.

**Fix**: delete the hardcoded `_cloud_providers` property; replace `_is_cloud_provider()` and `_is_cloud_provider_name()` with reads of `provider.is_cloud` (already populated from config). Re-audit historical MetricsDB `performance` rows for antigravity/anthropic/xai/google-compat — they are misclassified and the local/cloud ratio in `OMEGA_ENGINE.md` §2 is unverified until this is fixed.

### 3.2 — M14: "All vetted" claim contradicted by the project's own audit

`mandates.xml → OMEGA_ENGINE.md`:
> `Heritage | 121 [id-soft:] tags, 55+ general sources | ✅ All vetted | 2026-07-13`

`strategy_core.xml → UNOVERENGINEERING_PLAN.md`, dated **2026-08-08** (26 days later):
> `F9 | Heritage tags not mentioned | MISSING — handoff.py has vet-008, soul_validator.py has vet-015. M14 migration needed.`

`SOVEREIGN_MANDATES.md` (`mandates.xml`) is explicit: *"Merged without vet = M14 violation."* Two files are on record, by the project's own reconciliation pass, as carrying `[id-soft:]` tags without completed migration — which is a defined M14 violation — while the engine-state SSOT still asserts full compliance with a stale (26-day-old) timestamp. Either the SSOT table is wrong or the un-overengineering plan is wrong; both cannot be true, and the audit trail favors the more recent, more specific finding.

**Fix**: correct `OMEGA_ENGINE.md` §2 to reflect actual vet status, and treat `handoff.py`/`soul_validator.py` migration as blocking before either file is touched further (the plan already schedules `handoff.py` for deletion in §3.1 — deleting a file with an unmigrated heritage tag compounds the violation rather than resolving it).

### 3.3 — M23: The compliance gate itself is broken and self-certified as such

`strategy_core.xml → UNOVERENGINEERING_PLAN.md`:
> `F11 | M23 compliance is 92% | UNTRUSTABLE — pre-commit hook rg invocation is broken, passes falsely`

This is not a hypothetical risk — it's a documented, acknowledged fact in the project's own reconciliation. `SOVEREIGN_MANDATES.md` M23 states failure integrity requires the agent to *"stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`"* when a mandatory tool is broken — the correct response to a broken pre-commit gate is not "leave it broken and note it in a plan," it is to treat every commit since the gate broke as unverified for M23. Phase 0 of the same plan (`§1`) lists "Fix M23 pre-commit hook rg invocation" as a 30-minute pending task, meaning as of the pack's generation date the gate is **still broken**.

**Fix**: this is P0, not part of a 5-phase cleanup sprint. A false-positive quality gate is worse than no gate — it produces confident wrong signal across the whole codebase.

### 3.4 — M9: Silent broad exception swallow around credential resolution

`oracle_core.xml → providers.py`:
```python
def _resolve_google_api_key() -> str:
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("google:api_key")
        return cred.encrypted_blob if cred else ""
    except Exception:
        return ""
```
This catches every possible exception from vault loading — including corruption, permission errors, and programming bugs — and converts them all into an empty string with zero logging. `GoogleAIProvider.is_available()` calls `bool(_resolve_google_api_key())`, so any vault failure silently reports the provider as "not configured" rather than raising a typed, traceable error per M9's explicit requirement.

Separately: `cred.encrypted_blob` is passed directly as `key` into the `x-goog-api-key` header in `GoogleAIProvider.generate()`. The field name (`encrypted_blob`) strongly implies ciphertext, not a usable plaintext API key. `VaultCore` is not in this pack, so I cannot confirm whether decryption happens elsewhere — flagging this as **unverified** rather than a confirmed bug, but it warrants a direct check against `src/omega/vault/vault_core.py`.

Also note: this function reaches into `vault._load_sync()` and `vault._credentials` — both underscore-prefixed private attributes accessed from outside the class. That's a leaky abstraction independent of the M9 issue.

**Fix**: catch specific exception types from VaultCore, log with `logger.error()`, and either raise a typed `ProviderAuthError` or return `None` (not `""`) to make "no credential" distinguishable from "resolution failed."

## 4. Un-overengineering Targets (DELETE/FLATTEN)

The project's own `UNOVERENGINEERING_PLAN.md` is largely correct; the following five are the highest-leverage items visible in this pack:

1. **`src/omega/memory/recall.py` (786 lines, full file in `memory.xml`)** — a full quality-scored, power-law-decay memory tier (`RecallStore`, `Turn`, `ExchangePair`, `DecayStats`) that duplicates what FTS5 ranking + the existing hybrid RRF fusion already does. The plan (`§3.4`) already targets it for deletion; the code confirms it's a self-contained, cleanly separable module with no entanglement visible in the rest of the pack — safe to delete as scoped.

2. **`NativeGGUFProvider._ensure_loaded()` inline worker closure (`oracle_core.xml → providers.py`)** — a ~130-line nested `_worker()` function defined inside a method, handling model load, chat-template thinking-mode toggling, and a full request/response protocol via multiprocessing Queues. This belongs in its own module (e.g. `gguf_worker.py`) — as written it's untestable in isolation and the enclosing method is doing too much (context selection, CPU affinity, process spawn, and protocol definition all in one function).

3. **`AsyncCircuitBreaker` (`oracle_core.xml → health_monitor.py`, ~944 lines total file)** — implements both CUSUM drift detection *and* sliding-window detection *and* 429 rate-limit/quota classification in one class. The project's own plan (`§2.1`) already flags this for either replacement with `interlock-cb` or trimming via `prometheus_client`. Confirmed from the code: `_on_success`/`_on_failure` branch on `self.mode` throughout, meaning every method has two parallel implementations coexisting — a strong flatten candidate regardless of which library wins.

4. **Sovereign Sampling Layer's hardcoded Gemma special-case** (`oracle_core.xml → model_gateway.py`, inside `generate()`):
   ```python
   if "gemma-4-31b" in model_name.lower():
       temperature = max(temperature, 0.85)
       repetition_penalty = max(repetition_penalty, 1.2)
       GEMMA_LA_TOKENS = {759: -10.0, 2149: -10.0, 236772: -10.0}
   ```
   Hardcoded token IDs for one specific model's repetition bug, string-matched by substring, sitting inside the generic gateway's hot path. This is exactly the kind of stack-specific tuning M2's firewall exists to keep out of `src/omega/`. It also silently breaks if the tokenizer changes or a differently-named Gemma variant is loaded. Move to `config/entity_model_affinity.yaml` presets (the resolver already exists and is unused for this).

5. **Three parallel FTS+vector fusion call paths** — `MemoryStore.search()` (`memory_store.py`), `SQLiteVecAdapter.hybrid_search()` (`sqlite_vec_adapter.py`), both correctly delegating to the shared `HybridSearchEngine`, but each independently re-implements the "fetch FTS, fetch vec, build `FTSResult`/`VecResult` objects, fuse" boilerplate (~40 lines duplicated near-verbatim in each). Not a mandate violation since they share the core RRF logic, but it's the kind of duplicated glue code the un-overengineering sprint's stated goal ("delete ~2,500 lines") should target — consolidate into one `fetch_and_fuse()` helper both callers invoke.

## 5. Concurrency & Safety Risks

**Blocking SQLite writes on the event loop, no `anyio.to_thread.run_sync`.** This is the most concrete M1-spirit risk in the pack, and it's inconsistent with the project's own established pattern elsewhere.

- `observability.xml → metrics_db.py`: every write method (`record_event`, `record_error`, `record_breaker_transition`, `record_performance`, `set_baseline`) is a plain `def`, not `async def`, and calls `self._conn.execute(...)` / `self._conn.commit()` directly — synchronous SQLite I/O.
- These are invoked from the async hot path in `oracle_core.xml → model_gateway.py`, inside `generate()`:
  ```python
  tracker.record(
      provider=provider.name, model=model_name, latency_ms=_latency_ms,
      status="success", trace_id=trace_id, is_cloud=self._is_cloud_provider(provider),
  )
  ```
  which calls `LatencyTracker.record()` → `get_engine().record_performance()` (also plain `def`) → synchronous SQLite write. **Every successful inference call blocks the event loop on a disk write.**
- Contrast with `memory.xml → sqlite_vec_adapter.py`, which correctly wraps every write: `await anyio.to_thread.run_sync(_sync_upsert)`. The pattern is known and used elsewhere in the same codebase — `metrics_db.py` is the outlier.

- `memory.xml → memory_store.py → add_exchange()`:
  ```python
  self.fts.index_exchange(session_id, entity_name, "user", user_message)
  self.fts.index_exchange(session_id, entity_name, "assistant", response)
  ```
  `ConversationFTSIndex.index_exchange()` (`fts_index.py`) is a synchronous method doing `self._conn.execute(...)` + `commit()`, called directly without thread offload — two blocking SQLite writes per exchange. Note that `search_fts()` in the *same class* correctly uses `await anyio.to_thread.run_sync(self.fts.search, ...)` — the read path is compliant, the write path is not. That asymmetry (reads offloaded, writes not) is a specific, fixable bug, not a design gap.

**Blocking file I/O in `ModelGateway.__init__`**: `_load_sovereign_secrets()` opens and reads `.env` synchronously in the constructor (`oracle_core.xml → model_gateway.py`). Small file, low practical risk, but if `ModelGateway()` is ever constructed inside a running event loop rather than at process start, this blocks it. Worth a comment/guard at minimum.

**Config-level nondeterminism**: `config.xml → providers.yaml` has both `google` and `google-compat` at `priority: 4` in `inference.fallback_chain`. `ModelGateway._load_provider_fabric()` sorts by `_get_priority()` but Python's `sort()` is stable — meaning tie-break order depends entirely on original list order in YAML, which is fragile and undocumented. Given M22 exists to make provenance auditable, a silent tie in routing priority between two google-family providers is worth an explicit tie-breaker or distinct priorities.

## 6. Technical Debt Inventory

- **Misleading docstrings, same bug twice**: `ModelGateway.get_preferred_backend()` and `ModelGateway.check_health()` both carry the comment *"Cloud-first priority: Google → OpenRouter → OpenCode → Copilot → lmster → Ollama"* while the actual code checks local backends (`lmster`, `ollama`, `llama_cpp`, `llama_cli`, `llmster`) first and only falls through to `"cloud"` if none respond — i.e., local-first, matching M7. The comment is simply wrong, copy-pasted into two places. Low severity, but exactly the kind of stale doc that misleads the next engineer auditing for M7 compliance.

- **`OMEGA_ENGINE.md` self-contradicts its own headline metric**: the Current State table states `Mandate Compliance | 23/25 FULL (92%)`, while the document's own closing footer states `Mandate compliance: 84%`. No date-based resolution is offered between the two numbers in the same file.

- **Dead config field**: `provider.is_cloud = p_cfg.get("is_cloud", True)` is set on every provider instance during fabric load but is never read anywhere in the pack — see §3.1. This is the identical "loaded but never read" dead-config failure mode the project itself has previously flagged (per its own principle that dead config passes static analysis and appears correct while doing nothing).

- **Duplicate provider-name special-casing across `ModelGateway`**: `_cloud_providers`, `_is_cloud_provider_name`, and the `ordered_provider_names` fallback list (`["native-gguf", "lmster", "antigravity", "google"]` when `ProviderSelector` throws) are three separate hardcoded provider-name lists maintained independently in the same file — any new provider added to `providers.yaml` must be manually added to all three or silently misbehaves.

- **String-matching for crash detection**: `NativeGGUFProvider.generate()` (`providers.py`) detects OOM/crash conditions via substring match on the exception message (`"cuda malloc" in err_msg`, `"illegal instruction" in err_msg`) rather than typed exceptions from `llama_cpp`. Fragile — any wording change in the underlying library silently defeats this and downgrades a crash to a generic `InferenceError`.

- **Streaming timeout config drift**: `providers.yaml` (`config.xml`) sets `opencode-zen.streaming.chunk_timeout_ms: 30000`, but `AGENTS.md` (`mandates.xml`) documents a project-level `opencode.json` override of `chunkTimeout: 600000`/`60000` for the `opencode` provider to work around Nemotron streaming failures. Two configuration files claim authority over the same timeout value for what appears to be the same logical provider family, with no cross-reference between them.

- **Full test suite timeout risk, unresolved**: `OMEGA_ENGINE.md` §2 states *"Full suite 1706 collected (make test timeout risk)"* as a still-open item, alongside `UNOVERENGINEERING_PLAN.md`'s F12 correction that this was previously reported as a "phantom HIGH risk...never measured with adequate budget." Neither document confirms the suite has actually been run to completion with a real budget.

## 7. Recommendations Priority Order

1. **Fix `_cloud_providers` in `model_gateway.py`** to derive from `provider.is_cloud` (already loaded from config) instead of the hardcoded 4-item set. Re-derive historical sovereignty ratios once fixed — the current `make sovereignty` output is not trustworthy until this ships (§3.1).
2. **Fix the M23 pre-commit `rg` invocation** (`UNOVERENGINEERING_PLAN.md §1`) before relying on any other quality-gate output for this codebase — it's currently a false-positive machine (§3.3).
3. **Reconcile the M14 heritage-vetting contradiction**: correct `OMEGA_ENGINE.md`'s "All vetted" claim, and complete migration of `vet-008`/`vet-015` before deleting `handoff.py` or `soul_validator.py` as currently planned (§3.2).
4. **Wrap `metrics_db.py` writes and `fts_index.py.index_exchange()` in `anyio.to_thread.run_sync`**, matching the pattern already correctly used in `sqlite_vec_adapter.py` and `fts_index.search()` (§5).
5. **Reconcile `OMEGA_ENGINE.md`'s contradictory 92%/84% mandate-compliance figures** and re-verify against a fixed M23 gate.
6. **Extract the Gemma-specific sampling hack out of `model_gateway.py`** into entity/model affinity config, restoring M2 firewall separation (§4.4).
7. **Verify `VaultCore._credentials[...].encrypted_blob`** is actually plaintext-usable before it reaches the Google API header — or fix `_resolve_google_api_key()`'s silent `except Exception: return ""` regardless, per M9 (§3.4).
8. Proceed with the already-planned deletions in `UNOVERENGINEERING_PLAN.md` (`recall.py`, VaultCore trim, breaker consolidation) — these are well-scoped and correctly prioritized once items 1–3 are resolved.
