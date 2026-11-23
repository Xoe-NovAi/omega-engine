<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Headroom Enhancement Plan — Sovereign Context Compression

**AP Token**: `AP-HEADROOM-PLAN-v1.0.0`
**Status**: PLANNED — awaiting Architect approval to execute
**Date**: 2026-11-23
**Research sources**: local discovery + web research (docs.headroomlabs.ai, GitHub headroomlabs-ai/headroom)
**Related**: `docs/WAD_ENHANCEMENT_PLAN.md`, `docs/research/R_HEADROOM_Sovereign_Analysis.md`

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
- Implement `resolve_headroom_model(entity_name) -> (model, backend)`:
  1. Look up entity model from `EntityRegistry` (e.g., `opencode/big-pickle`)
  2. Resolve sentinel → actual model via `ProviderSelector` / `config/models.yaml`
  3. Map to Headroom tokenizer pattern (qwen3-1.7b → huggingface, etc.)
  4. Cache resolution result
- **Fallback**: if unresolvable, use `EstimatingTokenCounter` with a neutral model name (`"omega-engine-local"`)
- **Acceptance**: unit test that `opencode/big-pickle` resolves to a usable tokenizer backend without network

#### 1.2 Pass correct `model_limit` from entity context_window
- **File**: `src/omega/oracle/context_builder.py` (call site) + middleware signature
- Add `context_window` param to `compress_context()`; pass entity's `context_window` from registry
- **Acceptance**: test that a 4096-context entity gets `model_limit=4096`

#### 1.3 Capture real compression metrics
- **File**: `src/omega/oracle/middleware/headroom.py`
- Read `CompressResult.tokens_before/after/saved/ratio/transforms_applied`
- Populate `HeadroomResult` with real values; aggregate into a `CompressionSummary`
- Add structured log line: `compression entity=%s before=%d after=%d saved=%d ratio=%.2f transforms=%s`
- **Acceptance**: test that `tokens_saved` reflects actual `CompressResult` (not hardcoded 0)

---

### Phase 2 — Efficiency (P1, ~2 hrs)

**Goal**: Avoid unnecessary compression; tailor behavior per entity.

#### 2.1 Token budget check
- **File**: `src/omega/oracle/middleware/headroom.py`
- Before compressing, call `headroom.count_tokens_messages()` (or use `result` from a simulate pass)
- If token count < 70% of `model_limit`, skip compression (pass-through)
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
- Load in middleware; build `CompressConfig` from profile
- **Acceptance**: test that a log_analysis entity gets `target_ratio=0.2`

#### 2.3 `HEADROOM_OFFLINE=1` default
- **File**: `src/omega/oracle/middleware/headroom.py` or env bootstrap
- Set `HEADROOM_OFFLINE=1` in Omega's env config to enforce air-gap
- Ensures no beacon, no update check, no model download — aligns with M8 Zero Telemetry
- **Acceptance**: test that compression works with offline env set

---

### Phase 3 — Retrieval & Observability (P2, ~2 hrs)

**Goal**: Enable CCR and track compression over time.

#### 3.1 CCR ContextTracker per session
- **File**: `src/omega/oracle/middleware/headroom.py`
- Instantiate `headroom.ccr.ContextTracker` keyed by `workspace_key` (session_id + entity)
- Wire `retrieve_original(ref_id)` to tracker's cached originals
- Replace error-only stub with actual retrieval
- **Acceptance**: test that a compressed reference can be retrieved within TTL

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

*⬡ OMEGA ⬡ MAKALI ⬡ HEADROOM-PLAN ⬡ 2026-11-23 ⬡*
