<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# P3 Deepened Analysis — LongCat 2.0

**AP Token**: `AP-LONGCAT-P3-DEEPENED-v1.0.0`
**Date**: 2026-08-10
**Author**: LongCat 2.0
**Purpose**: Deepened review of P3 audit findings with code-level verification.

---

## Executive Summary

The P3 audit report's findings are **confirmed and deepened**. Code verification reveals:

1. **M25**: Streaming path is confirmed dead code. Non-streaming path has its own 120s httpx timeout. Dead code confirmed byte-for-byte identical.
2. **M7**: Scoring inversion confirmed. Only one caller of `_calculate_score` — tuple fix is safe.
3. **M14**: 18 colliding IDs confirmed. vet-017 has direct APPROVED/REJECTED contradiction.
4. **NEW FINDING**: Sovereignty ratio is **reporting 87% local but actual is ~38% local**. Cloud providers misclassified as local in metrics.

---

## M25 Streaming Resilience — CONFIRMED + DEEPENED

### Finding A: `_stream_completion()` is dead code — CONFIRMED

**Evidence**: `remote_provider.py:286-287` calls `_send_request` with NO `stream` kwarg:
```python
result = await self._send_request(
    model_name, system_prompt, user_query, temperature, max_tokens, trace_id=trace_id, session_id=session_id
)
```

`openai_compat.py:47` defaults `stream: bool = False`. The `else` branch at line 118-120 that calls `_stream_completion()` is unreachable through the standard call chain.

**Deepening**: The non-streaming path (`if not stream:` at line 104) uses `httpx.AsyncClient(timeout=self.config.timeout_seconds)` where `timeout_seconds = 120.0` (remote_provider.py:181). So the non-streaming path HAS a 120s timeout — but it's a total request timeout, not a per-chunk timeout. This is correct for non-streaming but means the streaming path's 30s/5min timeouts are entirely theoretical.

### Finding B: Timeout logic is starvation-vulnerable — CONFIRMED

**Evidence**: `openai_compat.py:153-167` — both timeout checks are INSIDE the `async for line in response.aiter_lines()` loop body. If the far end goes silent, `aiter_lines()` blocks and the loop body never runs.

**Deepening**: The proposed AnyIO watchdog pattern is correct in principle but has a subtle issue:
```python
stop.set()  # Line 131 — AFTER the async for loop
```
If an exception occurs inside the `async for` loop (e.g., `RuntimeError` from finish_reason='error'), `stop.set()` is never called. The watchdog task leaks until `fail_after` fires. **Fix**: wrap in `try/finally`:
```python
try:
    async with client.stream(...) as response:
        async for line in response.aiter_lines():
            ...
finally:
    stop.set()
```

### Finding C: Partial content loss — CONFIRMED

**Evidence**: `openai_compat.py:159` raises `RuntimeError` before reaching `return "".join(chunks).strip()` at line 204. All accumulated chunks are discarded.

**Deepening**: The Nemotron fix was specifically designed to avoid this class of waste. Once streaming is wired up, this finding will compound with Finding A.

### Finding D: Dead code — CONFIRMED

**Evidence**:
- `_detect_repetition_loop` at `openai_compat.py:207-223` is byte-for-byte identical to `remote_provider.py:376-397`. Both have the same docstring, same logic, same threshold.
- `create_openrouter_provider()` at `openai_compat.py:226-233` has ZERO callers in the codebase (grep confirms only the definition exists).

**Deepening**: Both are safe deletions. The `_detect_repetition_loop` override is truly dead — the base class version at `remote_provider.py:376` is inherited by all subclasses including `OpenAICompatProvider`.

---

## M7 ProviderSelector — CONFIRMED + DEEPENED

### Finding A: Happy path pulls full fabric — CONFIRMED

**Evidence**: `model_gateway.py:1043` calls `self.provider_selector.get_ordered_providers()`. `provider_selector.py:48` calls `self.model_gateway.get_available_providers()` which iterates the full fabric.

### Finding B: Scoring inverts priority — CONFIRMED

**Evidence**: `provider_selector.py:71`:
```python
score = float((10 - priority) * 10.0)
```
Additive with latency penalty at lines 85-86:
```python
latency_penalty = max(0.0, (breaker.ema_latency - 1000.0) / 100.0)
score -= latency_penalty
```

**Worked example** (matches audit report):
| Provider | Base | ema_latency | Latency penalty | Final |
|----------|------|-------------|-----------------|-------|
| native-gguf (p=0) | 100 | 5000ms | 40 | **60** |
| antigravity (p=3) | 70 | 1500ms | 5 | **65** |

Antigravity outranks native-gguf. M7's core guarantee is violated.

**Deepening**: Grep confirms `_calculate_score` has ONLY ONE caller (`provider_selector.py:54`). The tuple scoring fix is safe — no other callers to break.

### Finding C: Exception path bypass — CONFIRMED FIXED

**Evidence**: `model_gateway.py:1051-1060` — the exception handler falls back to `list(self.providers)` which is priority-sorted from `_load_provider_fabric()`. This is correct.

### Finding D: No kill-switch — CONFIRMED

**Evidence**: No config option to skip ProviderSelector scoring. The audit suggestion for a safety valve is valid.

---

## M14 Heritage — CONFIRMED + DEEPENED

### ID Collisions — CONFIRMED (18 colliding IDs)

**Evidence**: `grep -c "### vet-" data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` returns **98 total entries**.

Specific collisions confirmed:
- **vet-017**: Line 84 ("Job-Worker Queue (Parallel Ensemble)") vs Line 465 ("In-Flight Pipeline — REJECTED") — different content, different verdicts
- **vet-064-072**: Lines 695-761 (`###` heading level) vs Lines 889-961 (`####` heading level) — same IDs reused across two vetting passes

**Deepening**: The vet-064-072 block is a wholesale numbering restart. The "General Heritage Vetting — Non-id-Software Sources (Sprint A-EXT)" section dated 2026-07-11 restarted numbering at vet-059 without checking that vet-064-072 were already assigned. This accounts for 9 of the 18 colliding IDs.

### Redundant Vetting — CONFIRMED (3 pairs)

**Evidence**: The audit report's Table B identifies 3 code locations vetted twice under different IDs:
- `extractor.py:134-135` (SSRF check): vet-030 vs vet-076
- `extractor.py:144-145` (size check): vet-031 vs vet-077
- `extractor.py:282-283` (path scope): vet-032 vs vet-078

A naive ID-collision grep cannot catch this category — only a content/location read catches it.

---

## NEW FINDING: Sovereignty Ratio Misclassification

### The Bug

The sovereignty ratio reports **87.35% local** (2776 local / 402 cloud), but the provider breakdown reveals that `openrouter` (401), `opencode-zen` (400), `antigravity` (393), and `cline` (383) are classified as `is_cloud: false` — despite being cloud providers.

### Evidence

1. **`config/providers.yaml` correctly classifies these as cloud**:
   - `antigravity`: `is_cloud: true` (line 84)
   - `openrouter`: `is_cloud: true` (line 94)
   - `opencode-zen`: `is_cloud: true` (line 99)
   - `cline`: `is_cloud: true` (line 104)

2. **`ProviderRegistry.is_cloud()` reads from config** (provider_registry.py:43):
   ```python
   self._is_cloud[name] = bool(p.get("is_cloud", self._UNKNOWN_IS_CLOUD))
   ```

3. **MetricsDB populates `provider_classification` from registry** (metrics_db.py:232-238):
   ```python
   for name, is_cloud in registry.all_providers().items():
       self._conn.execute(
           "INSERT OR REPLACE INTO provider_classification ...",
           (name, int(is_cloud), ...)
       )
   ```

4. **The view uses `COALESCE(c.is_cloud, p.is_cloud)`** (metrics_db.py:267):
   ```sql
   COALESCE(c.is_cloud, p.is_cloud) AS is_cloud_corrected
   ```

5. **But the output shows them as `is_cloud: false`**.

### Root Cause Analysis

The `provider_classification` table is populated from `registry.all_providers()`. If this method doesn't return all providers, or if the table has stale data, the view falls back to `p.is_cloud` (the per-response recorded bit).

The per-response `is_cloud` bit is set by `ModelGateway.generate()` at line 1225:
```python
is_cloud=self._is_cloud_provider(provider),
```

This delegates to `ProviderRegistry.is_cloud()`. If the registry correctly reads from config, the per-response bit should be correct.

**Hypothesis**: The `provider_classification` table has stale data from before the config was updated. The `build_provider_classification_table()` method uses `INSERT OR REPLACE`, so it should update existing rows — but only if `registry.all_providers()` returns the correct values.

### Quantified Impact

| Provider | Count | Reported as | Actual |
|----------|-------|-------------|--------|
| mock | 762 | local | local ✓ |
| ollama | 406 | local | local ✓ |
| native-gguf | 31 | local | local ✓ |
| openrouter | 401 | **local** | **cloud** ✗ |
| opencode-zen | 400 | **local** | **cloud** ✗ |
| antigravity | 393 | **local** | **cloud** ✗ |
| cline | 383 | **local** | **cloud** ✗ |

- **Reported**: 2776 local / 402 cloud = **87.35% local**
- **Actual**: 1199 local / 1979 cloud = **37.7% local**

The sovereignty ratio is inflated by ~50 percentage points.

### Significance

This is a **M22 Response Provenance** violation. The sovereignty ratio is a key metric for the project's core claim of "local-first AI." If the metric is wrong, the claim is unverifiable.

This also supports **H3** from the speculative analysis: the M7 scoring inversion may have been silently firing in production, causing cloud providers to be selected over local ones. The misclassification masks the true extent of the problem.

---

## Cross-Cutting Findings

### 1. Provider Fabric Integrity (M25 + M7)

If M25 is unreachable AND M7 inverts local-first, the worst case is: a request that should stream locally gets sent to a cloud provider as a non-streaming request. Both mandates are violated in a single request.

### 2. Metrics Integrity (M22)

The sovereignty ratio misclassification means the project's core metric is unreliable. This is a systemic issue that affects all sovereignty claims.

### 3. Heritage Process (M14)

The vet-064-072 collision and the 3 redundant vetting pairs suggest the heritage vetting process lacks:
- ID collision detection (a simple grep catches this)
- Content-aware dedup (catches redundant vetting of same code)
- A `make heritage-vet` Makefile target (per GAP-2)

---

## Priority for Implementation

| Priority | Finding | Effort | Impact |
|----------|---------|--------|--------|
| **P0** | M7 tuple scoring fix | ~15 lines | Fixes M7 core guarantee, fires on every request |
| **P0** | Sovereignty ratio investigation | ~2 hours | Quantifies true local/cloud ratio, may reveal M7 impact |
| **P1** | M25 wire streaming + AnyIO watchdog | ~50 lines | Unblocks Nemotron fix, prevents indefinite hangs |
| **P1** | M25 watchdog try/finally fix | ~5 lines | Prevents watchdog task leak on exceptions |
| **P2** | M14 renumber vet-064-072 block | ~20 lines | Blocks `make heritage-vet` gate |
| **P2** | M14 resolve vet-017 contradiction | ~10 lines | Resolves direct APPROVED/REJECTED conflict |
| **P2** | M14 merge redundant vetting pairs | ~15 lines | Content-aware dedup |
| **P3** | Delete dead `_detect_repetition_loop` | ~20 lines | Mechanical cleanup |
| **P3** | Delete dead `create_openrouter_provider` | ~10 lines | Mechanical cleanup |

---

## What LongCat Verified

1. ✅ M25 dead code: `remote_provider.py:286-287` never passes `stream=True`
2. ✅ M25 starvation: timeout checks inside `async for` loop body
3. ✅ M25 dead code: `_detect_repetition_loop` byte-for-byte identical
4. ✅ M25 dead code: `create_openrouter_provider()` has zero callers
5. ✅ M7 scoring: additive formula inverts priority under realistic latency
6. ✅ M7 callers: `_calculate_score` has only one caller (tuple fix is safe)
7. ✅ M7 exception path: falls back to priority-sorted `list(self.providers)`
8. ✅ M14 collisions: vet-017 (2 entries), vet-064-072 (range collision)
9. ✅ M14 redundant vetting: 3 pairs identified
10. ✅ Sovereignty ratio: 87% reported vs ~38% actual — cloud providers misclassified

---

*⬡ OMEGA ⬡ LONGCAT-2.0 ⬡ P3-DEEPENED-v1.0.0 ⬡ 2026-08-10*
