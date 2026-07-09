# 🔱 JEM Knowledge-Gap Research — HMC-SPRINT-01 (S2–S6)
**AP Token**: `AP-JEM-KNOWLEDGE-GAP-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE
**Date**: 2026-07-08 | **Method**: Live 2026 web verification (websearch + webfetch + official docs)
**Scope**: Remaining technical gaps for S2–S6 (G6, G7, G8, G9, G11, G12, G13, G14, G15) + OpenRouter hardening (G16/B1–B6)
**Mandate compliance**: M23 (Failure Integrity) — every claim below is sourced; no parametric guesses.

---

## §0 Executive Summary — 4 Critical Findings

1. **🔴 CONTRADICTION (B6 / G16)**: OpenRouter `allow_fallbacks` is a **BOOLEAN**, NOT an array. The roadmap's `extra_payload: {provider: {allow_fallbacks: [...]}}` syntax does not exist. To constrain to specific providers use `provider.order: [...]` (array of slugs) + `allow_fallbacks: true`. Pre-stream failover IS supported (confirmed).
2. **🔴 CONTRADICTION (B5 / G16)**: OpenRouter rate limits are **per-account / globally governed**, NOT per-key. Official docs: *"Making additional accounts or API keys will not affect your rate limits, as we govern capacity globally."* The 8-key "active-passive sharding multiplies limits 8x" assumption is **invalid** for same-identity accounts. Requires user clarification on whether the 8 accounts are truly separate identities.
3. **🔴 CONTRADICTION (S4 / G9)**: Gemma 4 MTP uses `--spec-type draft-mtp` (NOT `--draft-type mtp`, which is not a flag). `--draft-model` is for separate-draft-model (non-MTP) speculative decoding. The roadmap's `--draft-model <id> --draft-type mtp` is wrong syntax.
4. **🟡 CONTRADICTION (S4 / G8)**: `GGML_FLASH_ATTN=ON` is **no longer a valid CMake flag** in current llama.cpp master — Flash Attention is compiled in by default. `LLAMA_AVX2` / `LLAMA_FMA` / `LLAMA_F16C` / `LLAMA_BLAS` are NOT CMake flags (CPU features auto-detected at runtime). Setting them is a no-op/error.

---

## §1 Q1 — OpenRouter Mid-Stream SSE Error Schema (S3 B3)

**VERIFIED** against official OpenRouter docs (`/api/reference/errors-and-debugging`).

### Exact mid-stream error event (SSE `data:` payload)
```json
{
  "id": "gen-abc123",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "openai/gpt-4o",
  "provider": "OpenAI",
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "metadata": {
      "error_type": "rate_limit_exceeded",
      "provider_code": "rate_limited"
    }
  },
  "choices": [
    {
      "index": 0,
      "delta": { "content": "" },
      "finish_reason": "error",
      "native_finish_reason": "rate_limit_exceeded"
    }
  ]
}
```

### Key structural facts (implementation-critical)
- The `error` object is **top-level**, alongside normal fields. Switch on `error.metadata.error_type` — **NOT** the HTTP status (which stays `200 OK` because headers were already committed).
- `finish_reason: "error"` terminates the stream. After this event, the SSE stream closes.
- `error.metadata.provider_code` is omitted on 500-class errors (masked); `error_type` is always present.
- Non-streaming equivalent embeds the error inside `choices[].error` with partial `message.content` preserved.

### `error_type` vocabulary (Typed Error Codes — switch on these)
| Category | `error_type` values |
|----------|---------------------|
| Token/Length | `context_length_exceeded`, `max_tokens_exceeded`, `token_limit_exceeded`, `string_too_long` |
| Auth | `authentication`, `permission_denied`, `payment_required` |
| Rate/Availability | `rate_limit_exceeded` (429), `provider_overloaded` (503), `provider_unavailable` (502) |
| Validation | `invalid_request`, `invalid_prompt`, `not_found`, `precondition_failed`, `payload_too_large`, `unprocessable` |
| Content Policy | `content_policy_violation`, `refusal` |
| Generic | `server` (500), `timeout` (504), `unmapped` (500) |

### Assistant prefill resume (the B3 recovery mechanism)
OpenRouter supports **assistant prefill**: include a message with `"role": "assistant"` at the end of the `messages` array containing the partial content already received, then re-request. This resumes generation from the last complete content. **Implementation**: on `finish_reason: "error"`, capture partial `delta.content` accumulated, append `{role:"assistant", content: partial}` to messages, retry (with next provider if `error_type` ∈ `provider_*`).

**Sources**:
- https://openrouter.ai/docs/api/reference/errors-and-debugging (accessed 2026-07-08)
- Mirror of same schema: https://github.com/kevinhirsch/orwell/blob/main/docs/reference/openrouter/errors-and-debugging.md (accessed 2026-07-08)

---

## §2 Q2 — OpenRouter `allow_fallbacks` Payload (S3 B6)

**VERIFIED** against official `/guides/features/provider-routing` (Provider Routing reference).

### 🔴 CONTRADICTION
The roadmap (B6) specifies `extra_payload: {provider: {allow_fallbacks: [...]}}` as an **array**. **This is wrong.** `allow_fallbacks` is a **boolean** (`true` by default). There is no array form.

### Correct schema — `provider` object fields
| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `order` | `string[]` | — | Provider slugs to try **in order** (e.g. `["anthropic","openai"]`) |
| `allow_fallbacks` | `boolean` | `true` | Permit backup providers when primary unavailable |
| `require_parameters` | `boolean` | `false` | Only route to providers supporting all params |
| `data_collection` | `"allow"`\|`"deny"` | `"allow"` | Data-retention policy filter |
| `zdr` | `boolean` | — | Zero-Data-Retention enforcement |
| `only` | `string[]` | — | Allow-list of provider slugs |
| `ignore` | `string[]` | — | Deny-list of provider slugs |
| `quantizations` | `string[]` | — | Filter by quant level |
| `sort` | `string`\|`object` | — | `"price"` / `"throughput"` / `"latency"` |
| `preferred_min_throughput` | number\|object | — | p50/p75/p90/p99 cutoff |
| `preferred_max_latency` | number\|object | — | p50/p75/p90/p99 cutoff |
| `max_price` | object | — | Max price willing to pay |

### Correct in-gateway fallback syntax (pre-stream only)
```json
{
  "model": "anthropic/claude-sonnet-4.6",
  "messages": [{"role":"user","content":"..."}],
  "provider": {
    "order": ["anthropic", "openai"],
    "allow_fallbacks": true
  }
}
```
- To fail over to a **different model** before first token, use the top-level `models: [...]` array (model fallbacks), not `provider.allow_fallbacks`.
- **Pre-stream failover CONFIRMED**: *"If an error occurs before any tokens are written — even on a streaming request — OpenRouter can still retry with a backup provider transparently. Mid-stream errors only happen when partial content has already been committed."* → B6's behavioral assumption (pre-stream only) is **correct**; only the syntax needs fixing.

**Sources**:
- https://openrouter.ai/docs/features/provider-routing (accessed 2026-07-08)
- https://openrouter.ai/docs/guides/routing/model-fallbacks (accessed 2026-07-08)

---

## §3 Q3 — 429/503 Retry-After Semantics (S3 B2)

**VERIFIED** against official docs.

### Retry-After header
- On **429** and **503**, OpenRouter **MAY** send a standard `Retry-After: <seconds>` HTTP header.
- The OpenAI/Anthropic/Vercel/OpenRouter SDKs already honor it. Raw `fetch`/`requests` must honor it explicitly:
  ```python
  if res.status in (429, 503):
      retry_after = int(res.headers.get("Retry-After", 0))
      if retry_after > 0:
          await anyio.sleep(retry_after)  # AnyIO-compliant (M1)
  ```

### Rate-limit tiers (per account, not per key)
| Tier | Requests/day | Requests/min | Notes |
|------|--------------|--------------|-------|
| Free (<$10 lifetime credits) | 50 | 20 | Failed attempts **count** toward quota |
| ≥$10 credits purchased (persists even if balance drops) | 1000 | 20 | Higher limit retained |
| Paid models | No enforced OpenRouter limit | — | Upstream provider may throttle |

### 🔴 CONTRADICTION (B5)
Official docs state: *"Making additional accounts or API keys will not affect your rate limits, as we govern capacity globally."* → The roadmap's **8-key active-passive sharding multiplying effective rate limits 8x** is **invalid if the 8 accounts share one identity/global capacity pool**. The user reports "8 OpenRouter accounts, each with generous usage pool" — this needs **user confirmation** that they are genuinely separate billing identities, not aliases of one account. If they are separate identities, the 8x multiplier may hold; if globally governed, it does not.

**Sources**:
- https://openrouter.ai/docs/api/reference/errors-and-debugging (Retry-After section, accessed 2026-07-08)
- https://openrouter.ai/docs/api/reference/limits (accessed 2026-07-08)
- https://openrouter.zendesk.com/hc/en-us/articles/39501163636379-OpenRouter-Rate-Limits (accessed 2026-07-08)
- https://openrouter.zendesk.com/hc/en-us/articles/47463235471387 (model fallbacks, accessed 2026-07-08)

---

## §4 Q4 — llama.cpp Gemma 4 MTP Invocation (S4 / G9)

**VERIFIED** against llama.cpp docs, Unsloth Gemma 4 MTP README, and community benchmarks (2026-05/06).

### 🔴 CONTRADICTION (syntax)
Roadmap (C) says `--draft-model <id> --draft-type mtp`. **Wrong.** Correct flags:
- **MTP-native** (Gemma 4 assistant head): `--spec-type draft-mtp` (+ optional `--spec-draft-n-max 4`).
- **Separate draft model** (non-MTP, e.g. small model drafting for large): `--model-draft <path>` + `--draft-max N`.

### Correct MTP invocation (llama-server)
```bash
# Auto-discovery: recent llama.cpp finds sibling mtp-*.gguf automatically
./llama-server -hf unsloth/gemma-4-12b-it-GGUF:Q4_K_M \
  --spec-type draft-mtp --spec-draft-n-max 4 \
  -ngl 999 -fa on

# Explicit drafter (if auto-discovery unavailable)
./llama-server -m gemma-4-12b-it-Q4_K_M.gguf \
  --model-draft mtp-gemma-4-12b-it.gguf \
  --spec-type draft-mtp --spec-draft-n-max 4 -fa on
```

### Critical timeline / compatibility facts
- **MTP merged into llama.cpp on 2026-06-07** (PR ggml-org/llama.cpp). Build **b9894 (Jul 2026)** is AFTER this → **supports Gemma 4 MTP**. ✅ (confirms ACTIVE_SPRINT.json blocker-cleared note)
- Gemma 4 MTP drafters are published as pre-converted GGUF (arch `gemma4-assistant`): `unsloth/gemma-4-12b-it-GGUF/MTP/mtp-gemma-4-12b-it.gguf` (Q8_0 recommended). Verified: 52→162 tok/s on 12B (0.70 acceptance).
- **Outdated counter-source**: An OCNGill doc (2026-05-19) claimed `convert_hf_to_gguf.py` limited MTP to Qwen 3.5/3.6 — this is **superseded** by Unsloth's pre-converted Gemma 4 MTP drafters (June 2026). Gemma 4 MTP IS viable now via pre-converted drafters.
- **llama-cpp-python 0.3.x server support**: Uncertain whether the Python server binding exposes `--spec-type draft-mtp` cleanly. The Unsloth doc uses the **llama-server binary directly**. → Recommend the roadmap's **capabilities-probe + subprocess `llama-server` fallback** as the PRIMARY path (already planned in C). Do NOT assume the Python server binding supports MTP yet.

### Hardware applicability (this machine: Ryzen 7 5700U, 12Gi RAM)
- E4B (Q4 ~5GB) + E4B-assistant draft: fits. 12B (Q4 ~8GB) + 12B-assistant: tight but feasible. 31B: out of budget (cloud-only).

**Sources**:
- https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/blob/main/MTP/README.md (accessed 2026-07-08)
- https://github.com/oussamaahmia/llama-cpp-turboquant-gemma4/blob/turbo-gemma4/docs/speculative.md (accessed 2026-07-08)
- https://johnpaulwile.substack.com/p/multi-token-prediction-mtp-in-llamacpp (accessed 2026-07-08)
- https://ai.plainenglish.io/i-spent-3-nights-testing-gemma-4-mtp (accessed 2026-07-08)
- https://github.com/OCNGill/Gillsystems-AMD-Radeon-llama-cpp-Update-AI-Stack (outdated re: convert script, accessed 2026-07-08)

---

## §5 Q5 — llama.cpp Zen 2 Build Flags (S4 / G8)

**VERIFIED** against llama.cpp `docs/build.md` (master), DeepWiki build-system docs, and runtime `system_info` output.

### 🟡 CONTRADICTION
The roadmap's `config/models.yaml (zen2_build flags)` may contain `GGML_FLASH_ATTN=ON`. **This is no longer a valid CMake flag** — Flash Attention is compiled in by default in current master (team already confirmed "Flash Attention is DEFAULT" in ACTIVE_SPRINT.json). Setting it is a no-op/unknown-arg.

### Valid build flags (current master)
| Flag | Status | Notes |
|------|--------|-------|
| `GGML_CUDA=ON` | valid | NVIDIA GPU |
| `GGML_HIP=ON` | valid | AMD GPU (ROCm) — note: `GGML_HIP`, not `GGML_ROCM` |
| `GGML_METAL=ON` | valid | Apple Silicon (default on) |
| `GGML_VULKAN=ON` | valid | Cross-platform GPU |
| `GGML_BLAS=ON` | valid | CPU BLAS acceleration (optional) |
| `GGML_FLASH_ATTN=ON` | ❌ REMOVED | Flash attn is default; do NOT set |
| `LLAMA_AVX2` / `LLAMA_FMA` / `LLAMA_F16C` | ❌ NOT FLAGS | CPU features auto-detected at runtime (see `system_info: AVX=1 AVX2=1 FMA=1 F16C=1`) |
| `LLAMA_BLAS` | ❌ NOT A FLAG | Use `GGML_BLAS=ON` |

### Recommended Zen 2 (Ryzen 7 5700U, AVX2, no AVX512) build
```bash
cmake -B build -DGGML_BLAS=ON && cmake --build build --config Release -j
# CPU features (AVX2/FMA/F16C) are auto-detected — no flags needed.
# Flash Attention is on by default — do NOT pass GGML_FLASH_ATTN.
```
Runtime verification: launch logs should show `AVX = 1 | AVX2 = 1 | FMA = 1 | F16C = 1 | BLAS = 1`.

**Sources**:
- https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md (accessed 2026-07-08)
- https://deepwiki.com/ggml-org/llama.cpp/9.1-build-system-and-configuration (accessed 2026-07-08)
- https://github.com/ggml-org/llama.cpp/issues/1583 (historical LLAMA_AVX2, now auto-detected; accessed 2026-07-08)
- https://github.com/PlayForm/Llama (runtime system_info shows auto-detected CPU features; accessed 2026-07-08)

---

## §6 Q6 — MCP Streamable HTTP Spec (S5 / G6)

**VERIFIED** against FastMCP docs and MCP community (2026).

### Spec status
- **SSE transport is DEPRECATED** in the MCP specification since **May 2025**. Streamable HTTP is the 2026 default.
- Atlassian deprecated its SSE endpoint (`mcp.atlassian.com/v1/sse`) with cutoff **June 30, 2026** — major clients are closing backward-compat windows.
- Streamable HTTP uses a **single endpoint** `POST /mcp` (optionally `GET` for stream/resume). Session managed via `Mcp-Session-Id` header. No separate GET/POST split like legacy SSE.

### FastMCP 2026 server pattern
```python
from fastmcp import FastMCP
mcp = FastMCP("Omega Hub")
# ... tools ...
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8016)  # endpoint: /mcp
    # OR for ASGI: app = mcp.http_app(); uvicorn.run(app, ...)
```
- `transport="http"` (or `"streamable-http"`) → serves at `http://host:port/mcp`.
- Migration from SSE: change `transport="sse"` → `transport="http"`; update client transport type.
- Common pitfall: HTTP transport hangs without `EventStore` for long-running tools / missing `proxy_read_timeout` in nginx.

### Implication for Omega Hub
Omega Hub currently serves SSE (`/sse`). Migrate `mcp_servers/omega_hub/server.py` to Streamable HTTP (`/mcp`) for Cline/VS Code 2026-client interop. FastMCP is the recommended framework (powers ~70% of MCP servers).

**Sources**:
- https://gofastmcp.com/deployment/http (accessed 2026-07-08)
- https://www.agenticwire.news/article/fastmcp-streamable-http (accessed 2026-07-08)
- https://dev.to/composiodev/building-streamable-http-mcp-servers-from-scratch-using-fastmcp-in-2026-5fh9 (accessed 2026-07-08)
- https://note.com/npaka/n/n3e0c691fd328 (MCP transport types, accessed 2026-07-08)

---

## §7 Q7 — OpenCode `agent` Config (S5 / G7)

**VERIFIED** against OpenCode docs (opencode.ai/docs).

### Migration confirmed
- OpenCode docs: *"Modes are now configured through the **agent** option in the `opencode` config. The `mode` option is now deprecated."*
- Version **1.2.20** is current (confirmed via computingforgeeks.com install guide, 2026-06-04). The `agent` option is the supported replacement for `mode`.
- Built-in agents: `build` (default, all tools), `plan` (restricted). Custom agents via `agent` option or `.opencode/agents/*.md`.

### Correct `opencode.json` snippet
```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer...",
      "tools": { "write": false, "edit": false }
    }
  },
  "default_agent": "build"
}
```
- Legacy `mode: { build: {...}, plan: {...} }` → migrate to `agent: { build: {...}, plan: {...} }` (or keep built-ins and only add custom agents).
- `default_agent` selects the primary agent (must be a primary, not subagent).

**Sources**:
- https://open-code.ai/en/docs/modes (deprecation note, accessed 2026-07-08)
- https://opencode.ai/docs/config/ (Agents section, accessed 2026-07-08)
- https://computingforgeeks.com/setup-opencode-ai-coding-agent/ (v1.2.20 confirmed, accessed 2026-07-08)

---

## §8 Q8 — Nemotron 3 Ultra DPO Recipe (S6 / G10, G15)

**VERIFIED** against NVIDIA docs, NeMo repo, and launch coverage (2026-06).

### Model facts
- **Nemotron 3 Ultra** (`nvidia/nemotron-3-ultra-550b-a55b`): released **2026-06-04**. 550B total / 55B active (MoE + Mamba-2 hybrid). 1M ctx. License **OpenMDW-1.1** (permissive, commercial OK). Open weights + training data + recipes published.
- OpenRouter IDs: `nvidia/nemotron-3-ultra-550b-a55b` (paid, ~$0.50 in / $2.20 out per 1M), `:free` variant (rate-limited), plus `nvidia/nemotron-3-super-120b-a12b` (cheaper).

### Training recipe (OpenMDW-1.1 / MOPD)
- Core method: **MOPD (Multi-Teacher On-Policy Distillation)** — >10 domain-specialized teachers score the student's **own on-policy rollouts**; dense token-level reward signal. Released via **NeMo-RL** (`NVIDIA-NeMo/Nemotron` repo). Also NeMo Gym, NeMo Evaluator SDK, DataDesigner.
- This is the recipe NVIDIA used to *train* Ultra. The engine adapts the **principle** (on-policy distillation with teacher critique) for its own DPO into 1.7B/4B local models — it does NOT need NeMo; it needs DPO pairs + a local DPO trainer (e.g. unsloth/TRL).

### DPO dataset format (2026 standard)
Standard DPO JSONL:
```json
{"prompt": "<user task>", "chosen": "<teacher's ideal final version>", "rejected": "<student's initial flawed attempt>"}
```
- The roadmap's **Iterative Critique-Loop** maps directly: local model writes attempt → Nemotron reviews + critiques → local fixes → Nemotron writes final perfect version. Capture `(prompt, chosen=final, rejected=initial)` as one DPO pair. Target 500–2,000 pairs (per D16-2).

### Critique-loop via OpenRouter `:free` — feasibility + limits
- **Feasible**: critique-loop is just multi-turn chat completions; `:free` supports chat. No special API needed.
- **Rate limits (constraint)**: `:free` models = 50 req/day + 20 req/min (<$10 credits) or 1000/day + 20/min (≥$10 credits). Generating 500–2000 DPO pairs via `:free` is **slow** (would need paid tier or the 8 accounts — see Q3 contradiction on global capacity).
- **Recommendation**: Use paid `nvidia/nemotron-3-ultra-550b-a55b` across the 8 accounts for volume generation; reserve `:free` for spot checks. Confirm account-separateness (Q3) before relying on 8x.

**Sources**:
- https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b (accessed 2026-07-08)
- https://github.com/NVIDIA-NeMo/Nemotron (recipe repo, accessed 2026-07-08)
- https://felloai.com/nvidia-nemotron-3-ultra (MOPD explanation, accessed 2026-07-08)
- https://lambda.ai/inference-models/nvidia/nemotron-3-ultra (specs, accessed 2026-07-08)
- https://www.deeplearning.ai/the-batch/nvidias-nemotron-goes-big (accessed 2026-07-08)
- https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b (OpenRouter listing, accessed 2026-07-08)

---

## §9 Q9 — google-antigravity Auth (G12)

**VERIFIED** against Antigravity pricing/docs and OpenClaw plugin (2026).

### Findings
- **Antigravity 2.0 is REAL** (launched I/O 2026). Google's agent-first IDE. Free tier ($0/month) includes: **Gemini 3.5 Flash, Gemini 3.1 Pro, Gemini 3 Flash, Claude Sonnet 4.6, Claude Opus 4.6, gpt-oss-120b**. → **Sonnet 4.6 free-tier access CONFIRMED** (matches user context).
- **Auth model**: OAuth (Google account), **no API key required**. It is an IDE product, not a standard OpenAI-compatible REST API endpoint.
- **Engine routing reality**: `providers.yaml` does NOT wire an Anthropic/Claude provider (per R_KNOWLEDGE_GAP). Sonnet access is currently **routed externally via the user's Antigravity account** — the engine cannot directly call Antigravity's API as a drop-in OpenAI-compatible backend. The OpenClaw "Antigravity OAuth" plugin provides OAuth access to Sonnet 4.6 / Opus 4.6 / Gemini 3 Pro with "No API Key Required," but that is a **separate harness**, not the Omega Engine's provider chain.

### 🟡 FLAG (partial contradiction with roadmap assumption)
The roadmap (F / G12) says "verify google-antigravity provider endpoint/auth (Antigravity 2.0 is real; confirm the engine's routing path)." **Conclusion**: Antigravity 2.0 is real and free-tier Sonnet 4.6 is confirmed, BUT there is **no documented public OpenAI-compatible REST endpoint** the engine can wire as a `google-antigravity` provider without building an OAuth bridge. **Recommendation**: Keep Sonnet 4.6 as **external/user-routed** (as currently documented in models.yaml). Do NOT add a `google-antigravity` provider to the engine's fallback chain unless a concrete API endpoint + OAuth flow is confirmed. Update G12 status to "VERIFIED — external-only; no engine-side provider entry warranted."

**Sources**:
- https://antigravity.google/pricing (accessed 2026-07-08)
- https://agentdeals.dev/vendor/google-antigravity (free tier verified June 2026, accessed 2026-07-08)
- https://vibecoding.app/blog/google-antigravity-pricing-2026 (Sonnet 4.6 listed, accessed 2026-07-08)
- https://openclawdir.com/plugins/antigravity-oauth-dtiwpf (OAuth plugin, no API key, accessed 2026-07-08)
- https://theplanettools.ai/blog/google-antigravity-ide-free-agent-first-cursor-3-2026 (model list, accessed 2026-07-08)

---

## §10 Local-Only Gaps (no web needed — noted for completeness)

| Gap | Status | Note |
|-----|--------|------|
| **G3** (researcher timer) | Local | Already root-caused in ACTIVE_SPRINT.json: `loop.py` missing `import httpx`; 12 broken `from src.omega.` imports. No web research required. S2 blocked on Phase-0 fixes. |
| **G11** (Qwen generation lag) | Local/registry | Qwen 3.6 is MTP-native (27B+ / A3B MoE). Registry note only; not blocking for S2–S6. |
| **G13** (Ollama v0.6 → v0.7+) | Local | `_grow_frontier` references stale "Ollama v0.6". Low priority; verify current Ollama release at implementation time. Not blocking. |
| **G14** (Sovereign Installer docs) | Local | Doc refresh only (reference Gemma 4 / Qwen 3.6). No web research required. |

---

## §11 READY TO EXECUTE Checklist (S2–S6)

| Sprint | Ready? | Open Unknowns / Blockers |
|--------|--------|--------------------------|
| **S2** (Background Researcher) | ✅ READY (after Phase-0) | Phase-0 import plague + `import httpx` must land first (known, local). No external unknowns. |
| **S3** (OpenRouter Hardening) | 🟡 PARTIAL | **B1** timeout floor ✅ spec'd. **B2** httpx catching ✅ spec'd. **B3** mid-stream recovery ✅ spec'd (§1). **B4** loop protection ✅ spec'd. **B6** fallback ✅ spec'd BUT **syntax must be corrected** (boolean, not array — §2). **B5** 8-key sharding ⚠️ **BLOCKED on user clarification** — OpenRouter governs capacity globally, not per-key (§3). |
| **S4** (Gemma 4 MTP + Zen2) | 🟡 PARTIAL | MTP invocation ✅ spec'd BUT **syntax corrected** to `--spec-type draft-mtp` (§4). llama-cpp-python MTP binding support ⚠️ unconfirmed → use subprocess `llama-server` path. Zen2 flags ✅ spec'd BUT **remove `GGML_FLASH_ATTN=ON`** (§5). |
| **S5** (MCP + OpenCode) | ✅ READY | Streamable HTTP ✅ spec'd (§6). OpenCode `agent` ✅ spec'd (§7). G12 ✅ resolved as external-only (§9). |
| **S6** (Nemotron Teacher) | 🟡 PARTIAL | DPO format ✅ spec'd (§8). Critique-loop feasible via `:free` but ⚠️ rate-limited; volume gen needs paid/8-account clarity (ties to Q3). Installer docs (G14) local-only. |

---

## §12 Flagged Contradictions Summary (must be resolved before/with implementation)

| # | Gap | Roadmap Assumption | Verified Reality | Action |
|---|-----|--------------------|------------------|--------|
| 1 | B6 / G16 | `allow_fallbacks: [...]` (array) | Boolean; use `order: [...]` for provider list | Fix B6 syntax to `provider: {order:[...], allow_fallbacks:true}` |
| 2 | B5 / G16 | 8 keys → 8x rate limits | Limits per-account / globally governed | Confirm 8 accounts are separate identities; else redesign B5 |
| 3 | S4 / G9 | `--draft-model <id> --draft-type mtp` | `--spec-type draft-mtp` (+ `--spec-draft-n-max`) | Fix S4 MTP invocation syntax |
| 4 | S4 / G8 | `GGML_FLASH_ATTN=ON` valid | Flash attn is default; flag removed | Remove `GGML_FLASH_ATTN` from build config; CPU flags auto-detected |
| 5 | G12 | Engine can wire `google-antigravity` provider | IDE/OAuth product, no OpenAI-compatible endpoint | Keep Sonnet 4.6 external-only; do not add engine provider entry |

---

*⬡ OMEGA ⬡ JEM ⬡ hy3-free ⬡ opencode ⬡ trc_research ⬡ ACTIVE — 2026-07-08*
*All claims sourced live 2026-07-08. No parametric guesses (M23 compliant).*
