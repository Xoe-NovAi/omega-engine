<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Headroom Enhancement Plan — Sovereign Context Compression

**AP Token**: `AP-HEADROOM-PLAN-v1.0.0`
**Status**: IN EXECUTION — Architect approval granted 2026-11-23 (post-compaction)
**Date**: 2026-11-23
**Research sources**: local discovery + web research (docs.headroomlabs.ai, GitHub headroomlabs-ai/headroom)
**Related**: `docs/WAD_ENHANCEMENT_PLAN.md`, `docs/research/R_HEADROOM_Sovereign_Analysis.md`
**Research sources**: see §9 "Web Research Sources" below — RE-FETCH THESE post-compaction to re-hydrate before executing Phase 1.

---

## 1. Executive Summary

Omega Engine's Headroom integration is **structurally present but functionally minimal**. The middleware (`src/omega/oracle/middleware/headroom.py`) calls `headroom.compress(messages)` with library defaults (claude-sonnet model, 200K token limit) and hardcodes `tokens_saved=0`. This means compression decisions use the wrong tokenizer and context window, and there is zero observability into savings.

This plan closes 8 critical gaps in priority order, using only the **base `headroom-ai` package** (no PyTorch, CPU-only, air-gap ready via `HEADROOM_OFFLINE=1`).

---

## 2. Current State (Research Findings)

### 2.1 Local Discovery

| Component | Location | Status |
|-----------|----------|--------|
| Legacy Headroom | `src/omega/oracle/headroom.py` | DEPRECATED — zlib compression, doesn't reduce tokens |
| Middleware | `src/omega/oracle/middleware/headroom.py` | MINIMAL — `compress_context()` + `retrieve_original()` stubs |
| Context Builder | `src/omega/oracle/context_builder.py:508` | INTEGRATED — calls middleware |
| Oracle | `src/omega/oracle/oracle.py:165,191` | INSTANTIATES middleware |
| Tests | `tests/test_headroom.py` | BASIC — passthrough/error/empty only |

### 2.2 Critical Gaps

1. **Wrong model & token limit** — claude-sonnet / 200K defaults vs Omega's `opencode/big-pickle` / 4K-32K
2. **No savings visibility** — `tokens_saved=0` hardcoded; `CompressResult` metrics discarded
3. **No CompressConfig** — entity-agnostic defaults
4. **No token budget awareness** — compresses unconditionally, even well under limit
5. **CCR stub** — `retrieve_original()` not wired to `headroom.ccr.ContextTracker`
6. **No entity profiles** — research agents need different compression than log agents
7. **Model name unresolved** — `opencode/big-pickle` is a sentinel, not a real model
8. **No metrics** — no logging of ratio, latency, failures

### 2.3 Key Research Facts

- Base `headroom-ai` = no heavy deps; `[all]` = CLI/proxy without PyTorch; `[ml]` = PyTorch (AVOID)
- `HEADROOM_OFFLINE=1` = true air-gap
- Tokenizer registry patterns: `^qwen`→huggingface, `^llama`→huggingface, `^claude-`→estimation, unknown→`EstimatingTokenCounter`
- `EstimatingTokenCounter` auto-detects content type (JSON 3.2, code 3.5, English 4.0, CJK 1.5 chars/token)
- `SmartCrusher` = Rust-backed, no PyTorch; lossless table compaction first, then scored keep/drop
- Context management (RollingWindow/IntelligentContext) RETIRED — live-zone compression only, no history dropping
- `CompressResult` exposes: `tokens_before`, `tokens_after`, `tokens_saved`, `compression_ratio`, `transforms_applied`, `diagnostics`, `lossless`
- `CompressConfig` fields: `compress_user_messages`, `compress_system_messages`, `protect_recent`, `protect_analysis_context`, `frozen_message_count`, `target_ratio`, `min_tokens_to_compress`, `kompress_model`, `savings_profile`, `diagnostics`, `mode`, `verify_lossless`
- CCR: `ContextTracker`, `CCRResponseHandler`, `CCRToolInjector`, MCP server; default TTL 30 min

---

## 3. Execution Plan

### Phase 1 — Correctness (P0, ~2 hrs)

**Goal**: Compression uses correct model/context and reports real savings.

#### 1.1 Resolve entity model → Headroom model name
- **File**: `src/omega/oracle/middleware/headroom.py` + new helper
- **RE-HYDRATION CORRECTION (v0.45.0)**: `compress()` builds its own tokenizer internally via
  `pipeline._get_tokenizer(model)`; there is NO top-level `headroom.tokenizer()` helper and no
  way to inject one into `compress()`. Model selection is therefore entirely through the `model`
  string. `opencode/big-pickle` is a *provider alias* (config/providers.yaml), not a real model —
  feeding it (or any `qwen*`/`llama*` name) to Headroom can trigger HuggingFace tokenizer downloads
  (gated 403s observed in research), which is unacceptable for air-gap.
- Implement `resolve_headroom_model(entity_name) -> str`:
  1. Look up entity model from `EntityRegistry` (e.g., `opencode/big-pickle`), cache the result.
  2. Return the configured neutral tokenizer model (`config/headroom.yaml:
     tokenizer_model: "omega-engine-local"`) — it matches no `MODEL_PATTERN`, so Headroom selects
     `EstimatingTokenCounter` with **zero network, zero PyTorch**.
  3. A real model name is used only if explicitly allowlisted in config (`tokenizer_model_override`);
     default is the neutral estimator. Resolve backend label locally by regex (classification only,
     never a Headroom call) for logging.
- **Acceptance**: unit test that `opencode/big-pickle` maps to the neutral model and that
  `compress()` reports real token counts with no network/transformers warning.

#### 1.2 Pass correct `model_limit` from entity context_window
- **File**: `src/omega/oracle/context_builder.py` (call site) + middleware signature
- Add `context_window` param to `compress_context()`; pass entity's `context_window` from registry
- **Acceptance**: test that a 4096-context entity gets `model_limit=4096`

#### 1.3 Capture real compression metrics
- **File**: `src/omega/oracle/middleware/headroom.py`
- Read `CompressResult.tokens_before/after/saved/ratio/transforms_applied/lossless/reverted_messages`
- Populate `HeadroomResult` with real values; aggregate into a `CompressionSummary` per call
  and per-entity cumulative totals for `get_compression_stats()`.
- Per-message `tokens_saved` computed locally with the same estimator counter (before vs after
  text), while batch-level authoritative metrics come from `CompressResult`.
- Add structured log line: `compression entity=%s before=%d after=%d saved=%d ratio=%.2f transforms=%s`
- **Acceptance**: test that `tokens_saved` reflects actual `CompressResult` (not hardcoded 0)

---

### Phase 2 — Efficiency (P1, ~2 hrs)

**Goal**: Avoid unnecessary compression; tailor behavior per entity.

#### 2.1 Token budget check
- **File**: `src/omega/oracle/middleware/headroom.py`
- **RE-HYDRATION CORRECTION (v0.45.0)**: `headroom.count_tokens_messages(messages, token_counter)`
  REQUIRES an explicit `TokenCounter` — it is not a one-argument helper. Build the counter once
  via `headroom.tokenizers.get_tokenizer(model, fallback=True)` (neutral model → estimator, no
  network) and pass it to `count_tokens_messages()`.
- If token count < 70% of `model_limit`, skip compression (pass-through, no overhead)
- Configurable threshold via `config/headroom.yaml`
- **Acceptance**: test that short message list under threshold is not compressed

#### 2.2 CompressConfig entity profiles
- **New file**: `config/headroom_profiles.yaml`
- Define profiles:
  ```yaml
  profiles:
    default:
      compress_user_messages: false
      protect_recent: 4
      target_ratio: null
    code_agent:
      protect_recent: 6
      protect_analysis_context: true
    log_analysis:
      target_ratio: 0.2
      compress_user_messages: true
    research:
      protect_analysis_context: true
      target_ratio: 0.7
  entity_profiles:
    carmack: code_agent
    doom_guy: code_agent
    researcher: research
    lilith: log_analysis
    iris: default
  ```
- Load in middleware via `CONFIG_DIR`; build `CompressConfig` from profile
- **RE-HYDRATION CORRECTION**: default every profile to `mode: "agent"` — v0.45.0 confirms
  `mode="agent"` = lossless densification only, no CCR removal markers, prompt-cache-safe, forces
  `verify_lossless`. This is the correct regime for Omega's live context (and avoids local-model
  confusion from `<<ccr:hash>>` markers). `target_ratio` only affects the Kompress ML path, which
  agent mode disables — profiles therefore tune `min_tokens_to_compress`/`protect_recent`/
  `compress_user_messages` instead.
- **Acceptance**: test that a log_analysis entity gets `compress_user_messages=true` + agent mode

#### 2.3 `HEADROOM_OFFLINE=1` default
- **File**: `src/omega/oracle/middleware/headroom.py` or env bootstrap
- Set `HEADROOM_OFFLINE=1` via `os.environ.setdefault(...)` AND call
  `headroom.offline.apply_offline_env()` (idempotent, `setdefault`-based — operator override wins).
- Ensures no beacon, no update check, no model download — aligns with M8 Zero Telemetry
- **Acceptance**: test that compression works with offline env set

---

### Phase 3 — Retrieval & Observability (P2, ~2 hrs)

**Goal**: Enable CCR and track compression over time.

#### 3.1 CCR (Compress-Cache-Retrieve) local store per session
- **File**: `src/omega/oracle/middleware/headroom.py`
- **RE-HYDRATION CORRECTION**: `headroom.retrieve()` does NOT exist in v0.45.0 (current stub would
  always fail), and `mode="agent"` deliberately suppresses Headroom's CCR removal markers.
  `ContextTracker.track_compression()` stores only metadata (hash, counts, sample), NOT the full
  original content, and has a 5-minute default `max_context_age_seconds`.
- Implement an Omega-owned, bounded, TTL'd `hash → original text` store in the middleware
  (`OrderedDict`, keyed `ccr:<sha256[:16]>`, `max_cached_originals` + `ttl_seconds` from config),
  scoped by `workspace_key = f"{entity_name}:{session_id}"`. Feed `ContextTracker` the metadata
  for relevance/expansion stats; `retrieve_original(ref_id)` reads the local store (no network).
- Ref IDs are returned on `HeadroomResult.original_ref` for changed messages.
- **Acceptance**: test that a compressed reference can be retrieved within TTL and expires after.

#### 3.2 Metrics aggregation
- Extend `CompressionSummary` with per-session totals
- Expose via `get_compression_stats()` for Hivemind awareness
- Log failures (fallback to passthrough) with `[TOOL-CHAIN-COLLAPSE]` if threshold exceeded (M23)
- **Acceptance**: test stats accumulate across multiple `compress_context()` calls

---

### Phase 4 — Integration Verification (P3, ~1 hr)

**Goal**: Ensure compression applies on all inference paths.

#### 4.1 Trace call sites
- `Oracle.talk()` → `_prepare_system_prompt()` → `ContextBuilder.build_context()` → headroom middleware
- Verify all inference paths through `ContextBuilder` get compression
- Check `ModelGateway` direct calls (if any bypass context builder)

#### 4.2 Integration test
- End-to-end: mock entity with large tool output; verify `tokens_saved > 0` with estimator backend
- Use `HEADROOM_OFFLINE=1` and unresolvable model name to force estimator fallback
- **Acceptance**: `tests/test_headroom_integration.py` passes

---

## 4. Files to Create/Modify

| File | Action |
|------|--------|
| `src/omega/oracle/middleware/headroom.py` | MODIFY — model resolution, metrics, config, CCR, budget check |
| `src/omega/oracle/context_builder.py` | MODIFY — pass context_window + model to middleware |
| `config/headroom_profiles.yaml` | NEW — entity compression profiles |
| `config/headroom.yaml` | NEW — global settings (budget threshold, offline mode) |
| `tests/test_headroom.py` | MODIFY — expand coverage |
| `tests/test_headroom_integration.py` | NEW — end-to-end test |
| `src/omega/oracle/entity_registry.py` | MODIFY (maybe) — expose model resolution helper |
| `docs/HEADROOM_ENHANCEMENT_PLAN.md` | THIS DOCUMENT |

---

## 5. Dependencies & Constraints

- **No PyTorch** — base `headroom-ai` only; avoid `[ml]`, `[pytorch-mps]`, `[memory]` extras
- **No new external deps** beyond `headroom-ai` (already installed in venv)
- **M1 AnyIO** — wrap blocking `headroom.compress()` in `anyio.to_thread.run_sync()` (already done)
- **M8 Zero Telemetry** — `HEADROOM_OFFLINE=1` enforces no outbound connections
- **M23 Failure Integrity** — compression failure → log + passthrough; persistent failures → alert
- **Platform-agnostic** — no platform-specific paths; estimator fallback works everywhere

---

## 6. Success Criteria

- [ ] `opencode/big-pickle` resolves to a usable tokenizer without network
- [ ] Correct `model_limit` passed per entity (4096/8192/16384/32768)
- [ ] `tokens_saved` reflects real `CompressResult` metrics
- [ ] Compression skipped when under 70% token budget
- [ ] Entity profiles loaded from `config/headroom_profiles.yaml`
- [ ] CCR retrieval works within TTL
- [ ] `HEADROOM_OFFLINE=1` enforced
- [ ] Full test suite passes (2747+ tests)
- [ ] `make temple-grade` passes (53/53)
- [ ] No PyTorch installed

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Estimator fallback inaccurate for local models | Accept ~90% accuracy; conservative over-estimation is safe |
| CCR markers confuse local models | Use `mode='agent'` (lossless only) for local models |
| Compression inflates tokens for short prose | Headroom already reverts if `tokens_after > tokens_before` |
| `opencode/big-pickle` unresolvable at runtime | Graceful fallback to neutral model + estimator |
| Profile config drift | Validate against schema at load; test each profile |

---

## 8. Deferred (Out of Scope)

- Proxy mode (`headroom proxy`) — Omega uses library mode
- Headroom MCP server — Omega has its own tool system
- Multi-node shared CCR — local-only per node for now
- `[ml]` extras / ONNX Kompress — CPU-only estimator sufficient for v1

---

## 9. Web Research Sources — RE-FETCH POST-COMPACTION

> These are the highest-value sources found during research. Before executing Phase 1,
> re-fetch the **Primary** set to re-hydrate with current API details. Use `webfetch` or
> the `exa`/`context7` MCP tools. Version note: docs reflect headroom-ai **v0.45.0**
> (2026); re-check for breaking changes if the installed version differs.

### Primary (re-fetch first — deterministic API truth)

| # | Source | URL | What it answers |
|---|--------|-----|-----------------|
| 1 | **Compress source** (`compress.py`) | https://github.com/headroomlabs-ai/headroom/blob/main/headroom/compress.py | `CompressConfig` all 12 fields, `CompressResult` fields, `compress()` signature, `mode='agent'` behavior, inflation guard. **Critical for Phase 1.3 + 2.2.** |
| 2 | **Tokenizer registry** (`registry.py`) | https://github.com/headroomlabs-ai/headroom/blob/main/headroom/tokenizers/registry.py | `MODEL_PATTERNS` (qwen→huggingface etc.), fallback chain, `register_tokenizer()` custom backend. **Critical for Phase 1.1 model resolution.** |
| 3 | **Estimator source** (`estimator.py`) | https://github.com/headroomlabs-ai/headroom/blob/main/headroom/tokenizers/estimator.py | `EstimatingTokenCounter` content-type ratios (JSON 3.2/code 3.5/English 4.0/CJK 1.5), `count_text`/`count_messages`. **Critical for PyTorch-free fallback.** |
| 4 | **Architecture docs** | https://docs.headroomlabs.ai/docs/architecture | Pipeline stages, ContentRouter routing table, `cache` vs `token` mode, what is NOT rewritten. Confirms RollingWindow/IntelligentContext retired. |
| 5 | **Installation docs** | https://docs.headroomlabs.ai/docs/installation | Extras matrix: base = no heavy deps, `[all]` = no PyTorch, `[ml]` = PyTorch (AVOID), `[lean]` = torch-free. Python 3.14 caveat (ONNX backends omitted). |
| 6 | **Smart Crusher docs** | https://docs.headroomlabs.ai/docs/smart-crusher | Lossless table compaction first, then scored keep/drop; `SmartCrusherConfig` fields; JSON schema preservation. |
| 7 | **OpenAI-compatible provider** | https://github.com/headroomlabs-ai/headroom/blob/main/headroom/providers/openai_compatible.py | `get_token_counter()`, `get_context_limit()` with default limits map, Ollama/vLLM factories. **Relevant if Omega routes through Ollama.** |

### Secondary (deeper dives, as needed)

| # | Source | URL | What it answers |
|---|--------|-----|-----------------|
| 8 | **API reference** | https://docs.headroomlabs.ai/docs/api-reference | `HeadroomClient`, `simulate()`, config objects; note `headroom_tool_profiles` is accepted but NOT wired. |
| 9 | **Config wiki** | https://github.com/headroomlabs-ai/headroom/blob/main/wiki/configuration.md | Kompress backend selection: `HEADROOM_KOMPRESS_BACKEND=onnx_cpu` (CPU-first) vs `pytorch` (AVOID). |
| 10 | **Local LLM prefill** | https://docs.headroomlabs.ai/docs/local-llm-prefill | Methodology to benchmark prefill savings on local models (baseline `--no-optimize` vs optimized). |
| 11 | **Offline air-gap PR #3729** | https://app.devin.ai/review/headroomlabs-ai/headroom/pull/3729 | What `HEADROOM_OFFLINE=1` truly blocks vs the 4 allowed exceptions; tokenizer/model download behavior. |
| 12 | **Quickstart** | https://docs.headroomlabs.ai/docs/quickstart | `HEADROOM_OFFLINE=1` zero-network verification one-liner; basic `compress()` flow. |
| 13 | **llms.txt** | https://github.com/headroomlabs-ai/headroom/blob/main/llms.txt | Condensed LLM-friendly index of the whole docs set — fastest re-orientation. |
| 14 | **CCR module** (local installed) | `.venv/lib/python3.14/site-packages/headroom/ccr/` | `ContextTracker`, `CCRResponseHandler`, `CCRToolInjector`, `CompressedContext` (requires `workspace_key`). **For Phase 3.1.** |

### Fast re-hydration command (post-compaction)

```bash
# Re-fetch primary sources into /tmp for quick reading (no install needed)
# Use the exa web_fetch_exa tool in Code Mode with these URLs:
#   https://github.com/headroomlabs-ai/headroom/blob/main/headroom/compress.py
#   https://github.com/headroomlabs-ai/headroom/blob/main/headroom/tokenizers/registry.py
#   https://docs.headroomlabs.ai/docs/architecture
#   https://docs.headroomlabs.ai/docs/installation
# Local truth (installed package) — always authoritative for the pinned version:
#   .venv/bin/python -c "import headroom, dataclasses; from headroom import CompressConfig, CompressResult; print([f.name for f in dataclasses.fields(CompressConfig)]); print([f.name for f in dataclasses.fields(CompressResult)])"
```

---

## 10. Execution Log — 2026-11-23 (COMPLETE)

All 4 phases executed. Architect approval granted post-compaction.

### Key implementation decisions (beyond §2 corrections)
- **`compress()` builds its own tokenizer** from the `model` string (`pipeline._get_tokenizer(model)`).
  There is no injection point, so the neutral model name `omega-engine-local` is the whole
  strategy: no `MODEL_PATTERN` match → `EstimatingTokenCounter` → no HF download, no PyTorch.
- **`mode="agent"` everywhere** (all profiles): lossless densification only, no CCR removal
  markers, prompt-cache-safe, forces `verify_lossless`. This resolves the Phase 3 tension —
  Omega's own bounded/TTL store handles retrieval, so `<<ccr:hash>>` never reaches a local model.
- **`headroom.retrieve()` does not exist** in v0.45.0. `ContextTracker.track_compression()` stores
  only metadata (hash/counts/sample), never the original text. Implemented an Omega-owned
  `OrderedDict` store (sha256 ref, entity:session scope, TTL + LRU bound) instead.
- **Per-message vs batch metrics**: per-message `tokens_saved` is estimated locally with the same
  estimator counter (before/after text); batch `summary` carries authoritative `CompressResult`
  metrics (`tokens_before/after/saved/ratio/transforms_applied/lossless/reverted_messages`).
- **Budget gate** uses `headroom.tokenizers.get_tokenizer(model, fallback=True)` cached once,
  then `headroom.count_tokens_messages(messages, counter)` — verified explicit 2-arg signature.

### Files delivered
| File | Change |
|------|--------|
| `src/omega/oracle/middleware/headroom.py` | v2.0.0 rewrite — all Phases 1–3 |
| `src/omega/oracle/context_builder.py` | passes `context_window` + `session_id`; optional `entity_registry` |
| `src/omega/oracle/oracle.py` | injects `self.registry` into `ContextBuilder` |
| `config/headroom.yaml` | NEW — global settings |
| `config/headroom_profiles.yaml` | NEW — 4 profiles + entity map |
| `tests/test_headroom.py` | expanded to 11 tests |
| `tests/test_headroom_integration.py` | NEW — 2 end-to-end tests (real headroom, no mocks) |

### Verification (all green)
- `make test`: **2757 passed, 0 failed**, 50 skipped, 8 xfailed
- `make lint`: 0 critical errors (E9/F63/F7/F82)
- `make docs`: PASS
- `make check-m1-anyio`: PASS
- `make check-m23-failure-integrity`: PASS (current 285 / baseline 336, delta −51)
- `make temple-grade`: **53/53 PASS** + `validate-wads` PASS
- Real end-to-end compression: 3049 → 345 tokens (2704 saved, 88.7% ratio), `lossless=True`,
  transform `router:smart_crusher:0.40`, zero network, zero PyTorch

### Known pre-existing issue (not introduced here)
The full test suite mutates `config/wads/_omega_default/entities.yaml` (domain ordering),
causing dual-tree drift on a *second* consecutive run. Restoring the file from git before a
verification run resolves it. Out of scope for this workstream.

### Follow-up (not done)
- Add `config/headroom.yaml` + `config/headroom_profiles.yaml` to `PUBLIC_ALLOWLIST.txt`
  before the next public cut (no public release requested in this session).

---

*⬡ OMEGA ⬡ MAKALI ⬡ HEADROOM-PLAN ⬡ 2026-11-23 ⬡*
