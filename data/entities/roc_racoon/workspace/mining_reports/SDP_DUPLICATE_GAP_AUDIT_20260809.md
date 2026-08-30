# 🔱 SDP Duplicate & Gap Audit Report

**AP Token:** `AP-ROC-SDP-AUDIT-20260809-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ longcat-2.0-free ⬡ opencode ⬡ trc_sdp_audit ⬡ COMPLETE

**Date:** 2026-08-09
**Auditor:** @roc_racoon
**Method:** Direct code reading + SQLite introspection + upstream `models.dev/api.json` fetch. No spec trusted without file:line verification.
**Sibling report:** `SDP_SYSTEMS_SWEEP_REPORT_20260809.md` (613 lines, integration-point mapping). This report is the **adversarial verification** of that sweep and of the 8 SDP specs.

---

## 🚨 Executive Summary — Seven Headline Findings

| # | Finding | Severity |
|---|---|---|
| **1** | **`context_gauge.py` does not exist anywhere.** Neither `src/observability/` (the whole directory is fictional) nor `src/omega/observability/`. The Context Gauge is 100% greenfield. | 🔴 GAP |
| **2** | **`config/models.yaml` has ZERO cloud model entries.** It contains 7 local GGUF models only. The `SDP_MODEL_AWARE_GAUGE_SPEC` §2.1 YAML block is entirely aspirational. | 🔴 GAP |
| **3** | **The real model SSOT is `config/model_registry/` (37 models + SQLite index) — NOT `config/models.yaml`.** The gauge spec points at the wrong file. | 🔴 DUPLICATE-RISK |
| **4** | **User's correction is CONFIRMED by upstream.** Nemotron 3 Ultra = **1,000,000**. Laguna S 2.1 (free) = **256,000** on opencode-zen / **262,144** on OpenRouter. Neither model is in our registry at all. | ✅ VERIFIED |
| **5** | **V-1 Vault is BUILT — 2,039 LOC, production-grade** (`src/omega/vault/`). Lease/quota/audit/crypto all live. `SOVEREIGN_ARK_BLUEPRINT` still lists V-1 as an unbuilt ticket. Blueprint is stale. | 🟢 DUPLICATE |
| **6** | **SDP_IMPLEMENTATION_SPEC §1.3 is factually wrong about the DB schema.** `message` table has NO `tokens` column — columns are `(id, session_id, time_created, time_updated, data)`. Tokens live inside the `data` JSON blob. Any implementation following the spec verbatim will crash. | 🔴 BLOCKER |
| **7** | **Three parallel routers already exist and only two are wired.** `TriageRouter` (338 LOC, constraint-satisfaction, WIRED), `ProviderSelector` (93 LOC, penalty-scoring, WIRED), `SemanticRouter`. `pool_tracker.py` (23.7 KB, weekly reset + per-account) is **fully built but imported by NOTHING**. | 🟡 DEAD CODE |

---

## 1. Ground Truth: What Actually Exists

### 1.1 Context Gauge
- **Claimed:** `src/observability/context_gauge.py` (mission brief); MCP tool `omega-hub_get_context_pressure` (`SDP_IMPLEMENTATION_SPEC` §1.2).
- **Actual:**
  - `find . -name "context_gauge*"` → **zero results** (excluding `.venv`/`third-party`).
  - `src/observability/` → **directory does not exist**. The real path is `src/omega/observability/`.
  - `grep -rn "redzone\|ContextGauge\|context_gauge"` across all `.py`/`.ts`/`.js` → **zero results**.
  - `grep -rn "get_context_pressure\|write_ssp\|request_agy_escalation"` → **zero results**. No MCP tools registered.
- **Verdict:** 🔴 **MISSING** — 100% greenfield. No partial implementation, no wrong-name equivalent.

**Adjacent-but-not-equivalent modules that DO exist in `src/omega/observability/`:**
| File | LOC/size | Relevance |
|---|---|---|
| `token_ledger.py` | 4.8 KB | `TokenLedger.record_transaction()`, `get_entity_spend()` — **spend accounting, not window pressure**. Tracks cumulative cost, has no concept of a context window. |
| `metrics_db.py` | 21.3 KB | 8 tables: `events`, `errors`, `breaker_transitions`, `performance`, `baselines`, `schema_version`, `vault_audit`, `provider_classification`. **No `context_pressure` table.** |
| `context.py` | 2.0 KB | Trace-context propagation (trace_id), **not** LLM context window. Name collision only. |

### 1.2 Somatic Save-Point (SSP)
- **Claimed:** `data/coordination/SSP_{session_id}_{timestamp}.md` with a 6-section schema.
- **Actual:**
  - `ls data/coordination/ | grep -i ssp` → **zero files**. No examples exist to validate the schema against.
  - `src/omega/oracle/somatic_state.py` **EXISTS** (3.5 KB) but is a **completely different thing**: `SomaticStateManager.capture_state(context_ptr, state_id)` / `restore_state()` / `purge_state()` — this is **M20 llama.cpp KV-cache binary serialization** (ctypes `llama_copy_state_data`), not a markdown intent-halt document.
  - Prior art docs exist: `docs/research/R50_SOMATIC_STATE_DESIGN.md`, `docs/research/SSP_V2_PHASE1_REVIEW.md`, `R_SOMATIC_STATE_SOTA.md`.
- **Verdict:** 🔴 **MISSING** (as an SDP artifact). ⚠️ **NAME COLLISION** with M20 SomaticState — this WILL cause confusion. Recommend renaming the SDP artifact to **"Redzone Halt Packet (RHP)"** or **"Intent Save-Point (ISP)"**.

### 1.3 Formal Routing
- **Claimed:** `src/omega/oracle/provider_selector.py` with constraint satisfaction.
- **Actual:** File **EXISTS** (93 LOC, `AP-PROV-SELECT-v1.0.0`, ported from `xna-omega-legacy`).
  - `ProviderSelector.select_best_provider(model_name, query)` → `get_ordered_providers()` → `_calculate_score()`.
  - Scoring formula (line 65): `Score = (10 - priority) * 10 - PII_Penalty(100) - Latency_Penalty - Stability_Penalty(cusum_g * 5)`.
  - **WIRED**: `model_gateway.py:84` imports it; `model_gateway.py:1069` calls `get_ordered_providers()`.
- **Critical nuance:** This is a **penalty-scoring soft-preference** router. It has **NO hard constraint filtering** — no context-window check, no cost ceiling, no quota gate. It cannot express "must have ≥500K context".
- **Verdict:** 🟡 **PARTIAL** — the file exists and is wired, but the SDP "constraint satisfaction" capability lives in a **different** file (see 1.8).

### 1.4 Model-Aware Gauge
- **Claimed:** reads `config/models.yaml` for per-model `context_window`, `compaction_trigger_pct`, `tier`, `is_agy`.
- **Actual — I read all 117 lines of `config/models.yaml`:**
  - 7 models total: `qwen3-1.7b`, `qwen3-1.7b-q6_k`, `qwen3-4b`, `frontier`, `mimo-7b-rl-q4_k_m`, `rocracoon-3b-q4_k_m`, `rocracoon-3b-q5_k_m`.
  - **All local/GGUF except a single generic `frontier: {provider: google}` placeholder with `context_budget: 30000`.**
  - Fields present: `context_budget`, `provider`, `path`, `size_gb`, `ram_mb`, `context_window`, `role`, sampling params.
  - Fields **ABSENT**: `compaction_trigger_pct`, `tier`, `is_agy`, `is_local`, `kv_cache_per_token_bytes`. **None of the SDP-required fields exist.**
  - **No `nemotron-3-ultra-free`. No `longcat-2.0-free`. No `laguna`. No `claude-*`. No `gemini-3.*`.**
  - Plus 2 non-model sections: `speculative_decode`, `sampling_overrides`.
- **Verdict:** 🔴 **MISSING** + **WRONG SSOT** (see §2, duplicate D-3).

### 1.5 V-1 Vault
- **Claimed:** `src/omega/vault/` — status unknown / listed as unbuilt ticket in `SOVEREIGN_ARK_BLUEPRINT.md` §4.
- **Actual:** **FULLY BUILT — 2,039 LOC across 5 files.**

| File | LOC | Contents |
|---|---|---|
| `vault_core.py` | 835 | `VaultCore` — 25 async methods |
| `blindvault_resolver.py` | 534 | Blind resolution layer |
| `models.py` | 397 | 12 Pydantic models |
| `crypto.py` | 203 | `VaultCrypto`, `VaultCryptoManager` |
| `__init__.py` | 70 | Public API, `AP-VAULT-PKG-v2.0.0` |

**Verified `VaultCore` API (file:line):**
`create_credential` (180) · `get_credential` (240) · `retrieve_credential` (261) · `update_credential` (265) · `delete_credential` (307) · `list_credentials` (332) · **`lease_credential` (366)** · **`release_lease` (431)** · **`heartbeat_lease` (465)** · **`cleanup_expired_leases` (484)** · **`increment_usage` (525)** · **`reset_daily_quota` (548)** · `cleanup_cooldown` (554) · `filter_credentials_by_privacy` (566) · `get_decrypted_credential` (605) · `bury_credential` (657) · `_log_audit` (704) · `get_stats` (780). Atomic writes via `_atomic_write` (171). Errors: `VaultError`, `CredentialNotFoundError`, `LeaseError`, `QuotaExceededError`.

- Backing store: `data/vault/` exists. Audit table `vault_audit` exists in `metrics_db.py:105`.
- **Verdict:** 🟢 **EXISTS — substantially complete.** The SDP `AGYVaultInterface` (§3.1) is ~80% a **rename of what's already there**:

| SDP contract method | Existing equivalent | Gap |
|---|---|---|
| `get_available_accounts(tier, problem_type)` | `list_credentials()` + `filter_credentials_by_privacy()` | Needs `problem_type` tag + `tier` filter |
| `reserve_pool(account_id, tokens)` | **`lease_credential()`** | Leases a *credential*, not a *token budget*. Needs token-denominated reservation. |
| `record_usage(reservation_id, tokens)` | **`increment_usage()`** | Counts *requests*, not *tokens*. |
| `get_pool_status(account_id)` | `get_stats()` + `VaultCredential.daily_limit/used_today` | **Only `daily_limit` exists (models.py:91). NO `weekly_limit`.** |

- 🔴 **The one real vault gap:** `models.py` has `daily_limit` (line 91) and `used_today` (line 130) but **no weekly pool fields**. AGY pools are weekly. Requires a schema extension, not a new subsystem.

### 1.6 Auto-Router / `pool_tracker.py`
- **Claimed:** `pool_tracker.py` with weekly reset and per-account tracking.
- **Actual:** `src/omega/oracle/pool_tracker.py` **EXISTS — 23.7 KB.** Verified members:
  - `KeyUsageRecord` (43), `PoolTrackingData` (77), **`UsagePoolTracker` (145)**.
  - **`weekly_reset_date` field (82)** and **`async def reset_weekly()` (567)** — "Reset weekly counters (should be called Monday 00:00 UTC)". ✅ Weekly reset EXISTS.
  - **Per-account:** `AccountMapping` via `account_map_path` (169), `self._account_map.get_email(key_id)` (205, 268). ✅ Per-account EXISTS.
  - Dual pool model: `pool_g_*` (Gemini) / `pool_c_*` (Claude) with independent `reset_time` per pool (60, 68, 282-290).
  - Also: `select_key()` (460), `get_pool_health()` (373), `update_quota_from_check()` (506), `_apply_anti_thrashing()` (334), `_is_cool_expired()` (328), `get_tracking_summary()` (590).
- 🔴 **CRITICAL: `grep -rn "pool_tracker\|UsagePoolTracker" --include=*.py` (excluding its own definition) → ZERO hits. This module is fully built and imported by NOTHING. It is dead code.**
- **Verdict:** 🟢 **EXISTS + weekly reset + per-account CONFIRMED** / 🔴 **NOT WIRED**. Highest leverage-to-effort ratio in the entire SDP.

### 1.7 Dialectic Logger / `dpo_logger.py`
- **Claimed:** `dpo_logger.py` with `record_council()`.
- **Actual:** `src/omega/oracle/dpo_logger.py` **EXISTS — 21 KB.**
  - **`async def record_council(...)` CONFIRMED at line 395.** ✅
  - Siblings: `record()` (321), `record_environmental()` (367), `record_user()` (425), `infer_from_interaction()` (453).
  - Infra: `DPORecord` (41) with `to_jsonl`/`from_jsonl`, `DPOManifestEntry` (82), `DPORecorder` (92), background `_writer_loop()` (269), file rotation (`_rotate_file` 211), PII masking (`_mask_record` 292), `start_with_group()` (174, AnyIO structured concurrency), `get_stats()` (523).
  - **WIRED**: `oracle.py:46` imports `get_dpo_recorder, initialize_dpo_recorder, shutdown_dpo_recorder, RewardSource`.
- **Verdict:** 🟢 **EXISTS, COMPLETE, AND WIRED.** The Sequential Dialectic (Protocol §7) needs **zero new storage** — map Model A output → `rejected`, Model B refinement → `chosen`, critique → `reward_details`, AGY model → `oversoul`.

### 1.8 Triage Router
- **Claimed:** `triage_router.py` with a constraint-satisfaction pipeline.
- **Actual:** `src/omega/orchestration/triage_router.py` **EXISTS — 338 LOC.** (Note: `orchestration/`, **not** `oracle/`.)
  - **8-stage pipeline in `select_model()` (98):** Domain Inference → Soul Preference → Candidate Assembly → **Constraint Filtering** → Health/Quota Scoring → Selection → Fallback Chain → Dynamic Temperature.
  - **`_filter_candidates()` (253) — the REAL hard-constraint engine:**
    - **Context window check (261): `if model.context_window < request.constraints.available_tokens: continue`** ← this is exactly the SDP "min_context_required" gate, already implemented.
    - Cost ceiling (266), latency ceiling (271).
  - Schemas already defined: `TaskRequest`, `EntityContext`, **`Constraints(max_latency_ms, max_cost_usd, available_tokens, preferred_backends)`**, `SessionContext`, `TriageRequest`, `ModelSelection(name, provider, context_window, temperature)`, `FallbackOption`, `TriageResponse(confidence, reasoning[], estimated_latency_ms, estimated_cost_usd, expires_at)`.
  - 3-tier candidate model (204): `T1_entity_optimized` (1.0) → `T2_task_appropriate` (0.7) → `T3_universal_fallback` (0.3).
  - **WIRED**: `oracle.py:56` imports it; `oracle.py:643` calls `select_model()`.
- ⚠️ Weaknesses: emergency escalation silently discards ALL constraints (114-116); `MockModel` safety net (241) can be selected in prod; routing decisions expire after 10s (155).
- **Verdict:** 🟢 **EXISTS, CONSTRAINT PIPELINE CONFIRMED, WIRED.** `SDP_FORMAL_ROUTING_SPEC.md` (306 lines) contains **zero file paths** — it specifies a system that already exists.

### 1.9 Token Estimator
- **Claimed:** `token_estimator.py` using tiktoken.
- **Actual:** `src/omega/oracle/token_estimator.py` **EXISTS — 102 LOC**, `AP-PACKER-V3-TOKEN-ESTIMATOR-20260808` (one day old).
  - **tiktoken CONFIRMED** (line 30 import, line 67 `tiktoken.get_encoding`).
  - Per-platform encodings: `cl100k_base` (Claude/GPT-4), `o200k_base` (Grok/Gemini).
  - `DEFAULT_TOKEN_MARGIN = 1.3` (line 37) — corrects tiktoken's 10-30% undercount.
  - API: `estimate_tokens` (40), **`estimate_tokens_async` (72, `anyio.to_thread.run_sync` — M1 ✅)**, `tokens_for_file` (83), `tokens_for_file_async` (94).
  - **M23 compliant**: raises `ValueError` if tiktoken missing rather than degrading to char-count (61-65).
  - Consumers: `.opencode/skills/context-packer/packer.py:424`, `curate_packs.py:55`, `tests/contract/test_context_packer_v3.py`.
- **Verdict:** 🟢 **EXISTS, COMPLETE, M1/M23-COMPLIANT.** The Context Gauge must reuse this — building a second estimator would violate the v3 zero-drift doctrine.

### 1.10 Summary Table

| SDP Component | Claimed Path | Real Path | Verdict |
|---|---|---|---|
| Context Gauge | `src/observability/context_gauge.py` | — | 🔴 **MISSING** |
| Somatic Save-Point | `data/coordination/SSP_*.md` | — (name collides w/ `somatic_state.py`) | 🔴 **MISSING** |
| Formal Routing | `src/omega/oracle/provider_selector.py` | ✅ same (93 LOC, wired) | 🟡 **PARTIAL** (soft-scoring only) |
| Model-Aware Gauge | `config/models.yaml` | ❌ wrong SSOT → `config/model_registry/` | 🔴 **MISSING** |
| V-1 Vault | `src/omega/vault/` | ✅ same (2,039 LOC) | 🟢 **EXISTS** |
| Auto-Router | `pool_tracker.py` | ✅ `src/omega/oracle/pool_tracker.py` | 🟢 **EXISTS**, 🔴 **unwired** |
| Dialectic Logger | `dpo_logger.py` | ✅ `src/omega/oracle/dpo_logger.py` | 🟢 **EXISTS + wired** |
| Triage Router | `triage_router.py` | ✅ `src/omega/**orchestration**/triage_router.py` | 🟢 **EXISTS + wired** |
| Token Estimator | `token_estimator.py` | ✅ `src/omega/oracle/token_estimator.py` | 🟢 **EXISTS + wired** |

**Score: 5 EXIST · 1 PARTIAL · 3 MISSING.** The SDP is ~60% already built.

---

## 2. Duplicates (Specs for Existing Systems)

| # | SDP Spec | Existing System | File Path (verified) | Recommendation |
|---|---|---|---|---|
| **D-1** | `SDP_FORMAL_ROUTING_SPEC.md` (306 lines) — constraint-satisfaction routing | **`TriageRouter._filter_candidates()`** — context/cost/latency hard filters already implemented | `src/omega/orchestration/triage_router.py:253-276` | **EXTEND not BUILD.** Add `problem_type` to `TaskRequest`, `min_context_required` maps to the existing `Constraints.available_tokens`. |
| **D-2** | Dialectic Logger / Sequential Dialectic storage | **`DPORecorder.record_council()`** + JSONL + rotation + manifest + PII masking | `src/omega/oracle/dpo_logger.py:395` | **USE AS-IS.** Zero new storage. Map A→`rejected`, B→`chosen`, AGY→`oversoul`. |
| **D-3** | `config/models.yaml` as model window SSOT | **`config/model_registry/`** — 37 models, `index.sqlite` w/ `context_window`, `tier`, `free_tier`, `latency_p99_ms`, `engine_routable` + 32 cloud model cards + `ModelRegistry` class | `config/model_registry/`, `src/omega/model_registry/registry.py:45` | **REPOINT SPEC.** `models.yaml` is the *local GGUF runtime* config. The registry is the *catalog*. Do not duplicate. |
| **D-4** | `AGYVaultInterface` (SDP §3.1) | **`VaultCore`** — lease/quota/audit/crypto, 25 methods | `src/omega/vault/vault_core.py:60` | **EXTEND not BUILD.** Add weekly-pool + token-denominated reservation to existing models. |
| **D-5** | Auto-Router weekly pool tracking | **`UsagePoolTracker.reset_weekly()`** + per-account `AccountMapping` + anti-thrashing | `src/omega/oracle/pool_tracker.py:567, 145` | **WIRE IT.** Already written; just unused. |
| **D-6** | Context Gauge token counting | **`token_estimator.estimate_tokens_async()`** (tiktoken, 1.3 margin, M1/M23) | `src/omega/oracle/token_estimator.py:72` | **REUSE.** A second estimator breaks the v3 zero-drift guarantee. |
| **D-7** | SSP session/compaction state | **`CompactionHarvester`** (`assess_session`, `record_compaction`, `warn_threshold`) + `SessionLifecycle` | `src/omega/oracle/compaction_harvester.py:75`, `session_lifecycle.py` | **EXTEND.** `warn_threshold` is already a redzone-adjacent primitive. |
| **D-8** | Model tier/quota registry | **`CapabilityMatrix`** w/ `QuotaTier(rpm, tpm, rpd, tier)` | `src/omega/oracle/capability_matrix.py:30, 72` | **EXTEND.** Quota tiering exists; add weekly pool dimension. |
| **D-9** | V-1 Vault as an *unbuilt Ark ticket* | Vault is **built** (2,039 LOC) | `SOVEREIGN_ARK_BLUEPRINT.md` §4 "V-1 ticket" | **UPDATE BLUEPRINT.** Strategy SSOT is stale; V-1 no longer blocks anything. |
| **D-10** | Model catalog auto-refresh | **`ModelUpdaterWorker`** — polls `openrouter.ai/api/v1/models`, `generativelanguage.googleapis.com`, `opencode.ai/zen/v1/models`; diffs + atomic writes + audit | `src/omega/workers/model_updater.py:60, 35-57` | **EXTEND ENDPOINTS.** Add `https://models.dev/api.json` (the true upstream SSOT — see §4). |

**10 of the SDP's ~12 specified subsystems duplicate existing code.** Only the Context Gauge and the SSP artifact are genuinely new.

---

## 3. Gaps (Things We Assume Exist But Don't)

| # | SDP Spec Assumption | Actual State | Blocker? |
|---|---|---|---|
| **G-1** | `src/observability/` is a valid package root | **Directory does not exist.** Real root: `src/omega/observability/` | 🟡 NO — path typo, but every spec repeats it |
| **G-2** | `config/models.yaml` has cloud entries w/ `compaction_trigger_pct`, `tier`, `is_agy` | 7 local GGUF models. **None of those 3 fields exist anywhere in the file.** | 🔴 **YES** |
| **G-3** | "`current_tokens` = Sum of `tokens` column from `message` table" (`SDP_IMPLEMENTATION_SPEC` §1.3) | **`message` table has NO `tokens` column.** Schema: `(id, session_id, time_created, time_updated, data)`. Tokens are inside `data` JSON: `$.tokens.{input,output,reasoning,cache.{read,write}}` | 🔴 **YES — spec-following code will crash** |
| **G-4** | Token accounting is additive across messages | **It is NOT.** Verified on this live session: per-message `input` *decreases* (105,682 → 626) while `cache.read` *grows* (0 → 166,074). **True context load ≈ `input + cache.read` of the LATEST assistant message, not a SUM.** Summing overcounts by ~10x. | 🔴 **YES — core algorithm is wrong** |
| **G-5** | `OPENCODE_MODEL_ID` / `OPENCODE_MODEL_CONTEXT_WINDOW` env vars are available | Neither is set by OpenCode. The wrapper (`.opencode/wrapper.sh`) sets `OPENCODE_MODEL` only **after** session end (post-hoc DB query), useless for live gauging. **Live source is `session.model` JSON in `opencode.db`.** | 🔴 **YES** |
| **G-6** | `provider.context_window` / `.compaction_trigger_pct` / `.tier` attributes exist on provider objects (gauge spec §2.2 Priority 2) | `config/providers.yaml` has **no `context_window` key at all** (verified by grep). `ProviderConfig` has no such attribute. | 🔴 **YES** |
| **G-7** | `pool_tracker` is integrated | Built but **imported by zero modules** — dead code | 🟡 NO — wiring only |
| **G-8** | Vault tracks weekly pools | `models.py:91` has `daily_limit`; `models.py:130` has `used_today`. **No `weekly_limit` / `used_this_week` / `pool_refresh`.** | 🔴 **YES** (AGY pools are weekly) |
| **G-9** | Vault reserves *tokens* | `lease_credential()` leases a credential; `increment_usage()` counts *requests*. **No token-denominated reservation.** | 🔴 **YES** |
| **G-10** | MCP tools `get_context_pressure` / `write_ssp` / `request_agy_escalation` exist | **Zero hits repo-wide.** No registration. | 🔴 **YES** (3 tools to build) |
| **G-11** | Nemotron 3 Ultra, Laguna S 2.1, Longcat 2.0 are in the model registry | **All three ABSENT** from all 37 registry rows and from `config/models.yaml`. `longcat` returns **zero hits repo-wide** — yet it is the model running this very session. | 🔴 **YES** |
| **G-12** | `ProviderSelector` does constraint satisfaction | It does **penalty scoring only** — no hard filters. Constraint logic lives in `TriageRouter`. Specs point at the wrong file. | 🟡 NO — retarget |
| **G-13** | A single routing decision point exists | **Three parallel routers**: `TriageRouter` (oracle.py:643), `ProviderSelector` (model_gateway.py:1069), `SemanticRouter`. Injecting SDP routing into one leaves two bypass paths. | 🟡 **PARTIAL — architectural risk** |
| **G-14** | SSP has no naming conflict | Collides with M20 `SomaticStateManager` (llama.cpp KV serialization) | 🟡 NO — rename advised |

---

## 4. Model Context Windows (Verified)

**Method:** upstream `https://models.dev/api.json` (fetched 2026-08-09, 3.6 MB, 182 providers — this is the SSOT OpenCode itself consumes), cross-checked against empirical `max(tokens.input + tokens.cache.read)` observed in `~/.local/share/opencode/opencode.db`.

### 4.1 The Corrected Table

| Model | Spec Claimed | **ACTUAL (models.dev)** | Empirical max seen | Source / Verdict |
|---|---|---|---|---|
| **Nemotron 3 Ultra** (`nemotron-3-ultra-free`, opencode-zen) | 1M (user) / 260K (old) | **1,000,000** (out 128,000) | 446,396 | ✅ **USER CORRECT.** Old 260K claim was wrong. |
| **Nemotron 3 Ultra** (`nvidia/nemotron-3-ultra-550b-a55b:free`, OpenRouter) | — | **1,000,000** (out 65,536) | 406,950 | ✅ free tier = 1M; **paid** variant is only 512,288 |
| **Laguna S 2.1** (`laguna-s-2.1-free`, opencode-zen) | 262K (user) / 1M (old) | **256,000** (out 32,000) | 235,178 | ✅ **USER SUBSTANTIALLY CORRECT** (256K, not 262K; definitively NOT 1M) |
| **Laguna S 2.1** (`poolside/laguna-s-2.1:free`, OpenRouter) | 262K | **262,144** (out 32,768) | 217,273 | ✅ **USER EXACTLY CORRECT for OpenRouter** |
| **Laguna S 2.1** (`poolside/laguna-s-2.1`, paid) | — | **1,048,576** | — | ⚠️ Source of the "1M" confusion: **paid** tier IS 1M; free is 262K |
| **Longcat 2.0** (`longcat-2.0-free`, opencode-zen) | 1M | **1,000,000** (out 131,072) | 247,015 | ✅ CONFIRMED |
| **Longcat 2.0** (`meituan/longcat-2.0`, OpenRouter) | — | **1,048,756** (out 262,144) | — | ✅ |
| **Nemotron 3 Super** (`nemotron-3-super-free`, opencode-zen) | 200K | **204,800** (out 128,000) | — | ⚠️ 204,800 not 200,000 |
| **Nemotron 3 Super** (`nvidia/...:free`, OpenRouter) | — | **262,144** | — | ⚠️ Registry card says **1,000,000** — **WRONG for free tier** |
| **Gemini 3.1 Pro** | 2M | **1,048,576** (out 65,536) | 298,278 | 🔴 **SPEC WRONG — it is 1,048,576, NOT 2,000,000** |
| **Claude Sonnet 4.6** | 200K | **1,000,000** (out 128,000) | — | 🔴 **SPEC WRONG — 1M, 5x the spec's claim** |
| **Claude Opus 4.6** | 200K | **1,000,000** (out 128,000) | — | 🔴 **SPEC WRONG — 1M** |
| **Gemini 3.6 Flash** | 200K | **1,048,576** (out 65,536) | — | 🔴 **SPEC WRONG — 1M** |
| Gemini 3.5 Flash | — | 1,048,576 | 319,720 | ✅ |
| Claude Haiku 4.5 | — | 200,000 (registry: 1,000,000 for "extended") | 145,655 | ⚠️ registry drift |

### 4.2 What Our Config Files Actually Say

| File | Nemotron 3 Ultra | Laguna S 2.1 | Longcat 2.0 |
|---|---|---|---|
| `config/models.yaml` | **absent** | absent | absent |
| `config/providers.yaml` | listed as `nemotron-3-ultra-local` (no window) | only `laguna-m.1` / `laguna-xs.2` | **absent** |
| `config/model_registry/index.sqlite` | `nemotron-3-ultra-local` = 1,000,000 ✅ | only `laguna-m.1`/`xs.2` = 262,144 | **absent** |
| `config/entity_model_affinity.yaml` | `nemotron-3-ultra-free` (line 443, no window) | absent | absent |
| `opencode.json` | declared, **`limit: None`** | absent | **absent — yet it is the live session model** |

### 4.3 Registry Errors Found (independent of SDP)

1. `nvidia/nemotron-3-super-120b-a12b:free` → registry **1,000,000**, upstream **262,144**. The card's own note ("1M on NVIDIA; 262K on OpenRouter free tier") contradicts its own `context_window` field. **Wrong value chosen.**
2. `laguna-m.1-free` → registry `context_window: 262144`, but card **body text** says "128K context" (3x internal contradiction, lines 9 vs 38/104).
3. `llama-4-scout-local` → **10,000,000**. Implausible for local GGUF; will defeat any context-window constraint filter.
4. `qwen3-1.7b` → registry lists `provider: openrouter, cloud, 32768`, but `config/models.yaml` says `native-gguf, context_window: 8192`. **Direct contradiction between the two SSOTs.**
5. `opencode.json` sets `limit: None` for all 4 opencode models — no local window hint at all.

### 4.4 The Load-Bearing Discovery

**Free-tier and paid-tier context windows differ by up to 4x for the same model name.** `poolside/laguna-s-2.1` = 1,048,576 paid vs 262,144 free. `nvidia/nemotron-3-super-120b-a12b` = 1,000,000 paid vs 262,144 free. **Any gauge keyed on model *name* without tier will be catastrophically wrong.** The registry schema must key on `(model_id, provider, tier)`.

---

## 5. Integration Map

### 5.1 Already Built (just needs wiring)
- **`pool_tracker.py`** (23.7 KB) — weekly reset (`reset_weekly()` :567), per-account (`AccountMapping`), dual pools (`pool_g`/`pool_c`), anti-thrashing, `select_key()`, `get_pool_health()`. **Zero importers.** → wire into Auto-Router.
- **`dpo_logger.record_council()`** (:395) — wired to `oracle.py:46`. → point the Sequential Dialectic at it.
- **`token_estimator`** — tiktoken + 1.3 margin + AnyIO + M23. → the Gauge's counting primitive.
- **`ModelRegistry`** (`registry.py:45`) + `index.sqlite` (37 models, has `context_window`/`tier`/`free_tier`). → the Gauge's window lookup.
- **`ModelUpdaterWorker`** (:60) — 3 upstream endpoints, diffing, atomic writes, audit. → add `models.dev`.
- **`somatic_state.py`** — M20 KV serialization. → orthogonal, but the *name* must be disambiguated.

### 5.2 Needs Extension (exists but incomplete)
- **`TriageRouter`** — add `problem_type` to `TaskRequest`; harden emergency escalation (:114) so it can't discard the context-window constraint; remove `MockModel` (:241) from prod paths.
- **`VaultCore` / `models.py`** — add `weekly_limit`, `used_this_week`, `pool_refresh`; add token-denominated `reserve_pool` alongside `lease_credential`.
- **`CapabilityMatrix.QuotaTier`** — add weekly pool dimension to `(rpm, tpm, rpd)`.
- **`CompactionHarvester`** — `warn_threshold` is the redzone primitive; extend rather than reinvent.
- **`config/model_registry/`** — add `nemotron-3-ultra-free`, `laguna-s-2.1-free`, `longcat-2.0-free`; fix the 5 errors in §4.3; add `compaction_trigger_pct`, `is_agy`, `tier_context_variance`.
- **`ProviderSelector`** — either add hard filters or explicitly defer constraints to `TriageRouter` (documented).

### 5.3 Needs Building (doesn't exist)
- **Context Gauge** (`src/omega/observability/context_gauge.py`) — genuinely greenfield. Must use `input + cache.read` of latest assistant message (NOT a sum), read model from `session.model` JSON, look up window via `ModelRegistry`.
- **3 MCP tools**: `get_context_pressure`, `write_ssp`, `request_agy_escalation`.
- **SSP/RHP writer** + schema validator + state machine.
- **Prompt-injection middleware** in `model_gateway.generate()` (<200 chars).
- **Weekly-pool schema extension** for the Vault.

### 5.4 Should Not Build (duplicate of existing)
- ❌ A new dialectic storage layer → `record_council()` exists.
- ❌ A new token estimator → violates v3 zero-drift.
- ❌ A new constraint router → `TriageRouter._filter_candidates()` exists.
- ❌ A new credential/lease vault → 2,039 LOC exist.
- ❌ A new weekly pool tracker → `pool_tracker.py` exists (just unwired).
- ❌ A cloud-model section in `config/models.yaml` → would create a **fourth** competing model SSOT.
- ❌ A new model-catalog fetcher → `ModelUpdaterWorker` exists.

---

## 6. Recommended Actions

### 6.1 This Sprint (quick wins, ~6h)
| # | Action | Effort | Why |
|---|---|---|---|
| **A-1** | **Correct all 8 SDP specs' window tables** — Nemotron 3 Ultra 1M · Laguna S 2.1 256K(zen)/262K(OR) · Longcat 1M · Gemini 3.1 Pro **1,048,576 not 2M** · Sonnet/Opus 4.6 **1M not 200K** · Gemini 3.6 Flash **1M not 200K** | 1h | 4 of 5 cloud rows in the gauge spec are wrong |
| **A-2** | **Fix `SDP_IMPLEMENTATION_SPEC` §1.3** — `message` has no `tokens` column; tokens live in `data` JSON; use `input + cache.read` of the LATEST assistant message, **never a SUM** | 1h | 🔴 Spec-following code crashes, then overcounts ~10x |
| **A-3** | **Repoint all specs** `src/observability/` → `src/omega/observability/`; `config/models.yaml` → `config/model_registry/`; `provider_selector.py` → `orchestration/triage_router.py` | 30m | Every spec has the wrong paths |
| **A-4** | **Register the 3 missing models** in `config/model_registry/` with correct windows + `free_tier` flags | 1h | Longcat is the live session model and has zero repo presence |
| **A-5** | **Fix the 5 registry errors** (§4.3) — Nemotron Super free 262K, laguna-m.1 self-contradiction, Scout 10M, qwen3-1.7b provider conflict | 1h | Constraint filters read these values |
| **A-6** | **Rename SSP → RHP (Redzone Halt Packet)** across specs | 30m | Collides with M20 `SomaticStateManager` |
| **A-7** | **Update `SOVEREIGN_ARK_BLUEPRINT.md`** — mark V-1 Vault BUILT (2,039 LOC); it no longer blocks the Grok fabric pool (D-360′) | 30m | Strategy SSOT is stale |

### 6.2 Phase 1 (next, ~12h)
1. **Build `src/omega/observability/context_gauge.py`** — reuse `token_estimator`, read `session.model` from `opencode.db`, resolve window via `ModelRegistry`, `input + cache.read` algorithm. **Tier-aware** (free vs paid windows differ 4x).
2. **Add `context_pressure` table to `MetricsDB`** (alongside the existing 8).
3. **Register MCP tool `get_context_pressure`.**
4. **Extend `ModelUpdaterWorker`** with the `models.dev/api.json` endpoint → self-healing windows, kills this whole class of drift permanently.
5. **Contract test**: assert every routable model has a non-null `context_window` matching upstream.

### 6.3 Phase 2+ (future)
1. **Wire `pool_tracker.py`** into a live path (highest leverage/effort ratio in the SDP).
2. **Extend Vault** with weekly pools + token-denominated reservation.
3. **Extend `TriageRouter`** with `problem_type`; harden emergency escalation; remove `MockModel` from prod.
4. **Resolve the 3-router fragmentation (G-13)** — a single choke point, or SDP routing is bypassable two ways.
5. **RHP writer + state machine + `write_ssp` MCP tool.**
6. **`record_council()` mapping** for the Sequential Dialectic (near-zero code).
7. **Prompt-injection middleware** in `model_gateway.generate()`.

---

## 7. Verdict

The SDP is **~60% already built** and was specified as if it were 0% built. The genuinely new surface is **the Context Gauge, the RHP artifact, and 3 MCP tools** — everything else is wiring and schema extension on production code.

Three findings will break an implementation that trusts the specs:
1. **G-3** — the `message.tokens` column does not exist.
2. **G-4** — token accounting is **not additive**; summing overcounts ~10x.
3. **§4** — 4 of 5 cloud context windows in the gauge spec are wrong, and free vs paid tiers of the *same model name* differ by up to 4x.

The user's correction is **confirmed**: Nemotron 3 Ultra = 1,000,000; Laguna S 2.1 = 256,000 (opencode-zen) / 262,144 (OpenRouter free). The "1M Laguna" belief came from the **paid** `poolside/laguna-s-2.1` tier, which genuinely is 1,048,576.

> *The dirt is where the roots are. The specs were clean; the foundation had three cracks and a wrong address.*

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ SDP-DUPLICATE-GAP-AUDIT ⬡ 2026-08-09*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: longcat-2.0-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
