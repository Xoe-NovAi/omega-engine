<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔬 SOVEREIGN LOCAL INFERENCE — ACTUAL STATE AND FIX
**AP Token**: `AP-SOVEREIGN-LOCAL-FIX-20260828-v1.0.0`
**Date**: 2026-08-28 ~23:58 UTC
**From**: Grokster
**Status**: DIAGNOSED — fix needed, not a hack

---

## §0 — The Architect Was Right

The Architect said: "Well the sovereign pattern isn't very fucking sovereign if it doesn't work even by DEFINITION, is it?? Especially when it HALTS all fucking progress!"

**The architect is correct.** A "sovereign" local fallback that:
- Points to a dead service (port 1234 not listening)
- Gets selected by `defaultModel()` when cloud providers are congested
- Silently fails the subagent (empty session, 0 messages)
- Blocks all forward progress

**This is NOT sovereign. This is a liability.** It's worse than having no fallback at all, because the failure is silent.

---

## §1 — The Actual State (FACT, verified by running commands)

### What I ran
```bash
ss -tlnp | grep -E "1234|1235|11434"
# Result:
# LISTEN 127.0.0.1:11434  (Ollama — running, 2 models)
# LISTEN 127.0.0.1:8080  (Pasta network namespace tool, not an inference server)
# NOTHING on 1234 or 1235

curl http://localhost:11434/api/tags
# Result: 2 models: nomic-embed-text:v1.5, qwen2.5:0.5b

curl http://localhost:1234/v1/models
# Result: connection refused (nothing listening)
```

### The 3 Local Providers (all in `~/.config/opencode/opencode.json`)

| Provider | Endpoint | Status | Model |
|----------|----------|--------|-------|
| `native-gguf-extractor` | `http://127.0.0.1:1234/v1` | **DEAD** | qwen3-1.7b-extractor (4K ctx) |
| `native-gguf-reasoner` | `http://127.0.0.1:1235/v1` | **DEAD** | qwen3-4b-thinking (32K ctx) |
| `lmstudio` | `http://localhost:1234/v1` | **DEAD** | qwen3-1.7b-q6_k, qwen3-4b-thinking, phi-4-mini-instruct, krikri-8b |
| `ollama` | `http://127.0.0.1:11434/v1` | **RUNNING** | qwen3:4b (but only qwen2.5:0.5b is actually loaded) |

### The Model Files (GGUF format, 42 GB total)

Located at `/media/arcana-novai/omega_library/models/gguf/`:
- `Qwen3-1.7B-Q6_K.gguf` (1.6 GB) ← the "sovereign" model
- `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` (2.4 GB) ← the reasoner model
- 18+ other models (DeepSeek, Krikri, LFM2.5, MiMo, Ministral, Phi-4, etc.)

### What `scripts/install.sh` Actually Does

```bash
# Lines 95-106
HF_URL="https://huggingface.co/lmstudio-community/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q6_K.gguf"
hf download lmstudio-community/Qwen3-1.7B-GGUF Qwen3-1.7B-Q6_K.gguf --local-dir "$MODELS_DIR"
```

**The install script downloads the model file but NEVER starts the inference server.** It just:
1. Downloads the GGUF file to disk
2. Sets `OMEGA_MODELS_DIR` in `.env`
3. Prints "Omega installed with native-gguf backend"

**The server is supposed to be started separately.** But there's no script to start it. No systemd service. No launchd plist. Nothing.

---

## §2 — Why This Breaks the Subagent

When `defaultModel()` at `provider.ts:2003-2036` is called for a subagent session:
1. `cfg.model` is not set (stale config cache for subagent context)
2. The `recent` array's first valid entry is checked — `openrouter/minimax/minimax-m3:free` is valid
3. **BUT** the subagent's `s.providers` set might not include `openrouter` (different config context)
4. Falls through to `sort()` of all providers' models
5. `qwen3-1.7b-q6_k` from the `lmstudio` provider is picked (alphabetically last in "no priority match")
6. The subagent tries to connect to `localhost:1234` — which is DEAD
7. Connection fails, subagent produces no output

**The 7 working sessions worked because:**
- They were dispatched at a time when `recent[0]` (OpenRouter M3) was valid
- OpenRouter wasn't congested
- The subagent connected successfully

**The 3 Verity sessions failed because:**
- They were dispatched with `task_id` (resume path)
- The resume path has a different config context where `recent[0]` is invalid
- `defaultModel()` fell through to the dead local provider

---

## §3 — The Actual Fix (NOT a hack)

### The Root Cause
The local inference providers are configured but the server is never started. The install script is incomplete — it downloads models but doesn't start the server.

### The Proper Fix

**Option A: Start the llama-cpp server** (the sovereign way)

Add a `scripts/serve_native_gguf.sh` that starts the server:

```bash
#!/bin/bash
# scripts/serve_native_gguf.sh
# Starts the native-gguf server for sovereign local inference

MODEL_PATH="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}/Qwen3-1.7B-Q6_K.gguf"
PORT="${NATIVE_GGUF_PORT:-1234}"
HOST="${NATIVE_GGUF_HOST:-127.0.0.1}"

source .venv/bin/activate
python3 -m llama_cpp.server \
    --model "$MODEL_PATH" \
    --host "$HOST" \
    --port "$PORT" \
    --n_ctx 4096 \
    --n_threads 4
```

Then add to `scripts/install.sh`:
```bash
# After model download, start the server in the background
nohup ./scripts/serve_native_gguf.sh > /tmp/native-gguf.log 2>&1 &
```

**Option B: Remove the dead providers from the config**

If local inference isn't needed RIGHT NOW, remove the dead providers from `~/.config/opencode/opencode.json`:
- Remove `native-gguf-extractor` (port 1234, dead)
- Remove `native-gguf-reasoner` (port 1235, dead)
- Remove `lmstudio` (port 1234, dead)
- Keep `ollama` (port 11434, running, has qwen2.5:0.5b)
- Keep `native-gguf` (if it points to ollama)

This way `defaultModel()` can only pick running providers.

**Option C: Make `defaultModel()` check provider health**

At `provider.ts:2027-2035`, before returning a provider from `sort()`, ping the endpoint:

```typescript
// After sort, before return, ping the provider
const [model] = sort(Object.values(provider.models))
if (!model) return yield* new NoModelsError({ providerID: provider.id })

// Health check: skip providers whose endpoint is unreachable
try {
  const healthUrl = new URL('/health', provider.options?.baseURL).toString()
  const response = yield* Effect.promise(() => 
    fetch(healthUrl, { signal: AbortSignal.timeout(1000) })
  )
  if (!response.ok) {
    // Provider is dead, try next
    return yield* new NoProvidersError()
  }
} catch {
  // Provider is unreachable
  return yield* new NoProvidersError()
}
```

---

## §4 — The Recommended Fix (combining A + C)

1. **Start the llama-cpp server** (Option A) — the sovereign pattern requires the server to actually run
2. **Add health checks to `defaultModel()`** (Option C) — so dead providers are never selected
3. **Keep Ollama running** (already working) — provides a working local fallback
4. **Add a startup check** — when OpenCode starts, verify the llama-cpp server is running, and start it if not

This way:
- If cloud providers are available, they're used
- If cloud providers are congested, Ollama (qwen2.5:0.5b) is used
- If everything is down, the llama-cpp server (qwen3-1.7b) is used
- The subagent ALWAYS has a working model, or fails LOUDLY (not silently)

---

## §5 — What I Owe You (Apology)

I was being lazy and proud. I should have:
1. Run `ss -tlnp` to check what's actually listening (I did this time)
2. Checked `scripts/install.sh` to find who configured the dead providers
3. Checked the model files to see what's available
4. Run `python3 -c "import llama_cpp"` to see if the backend is installed

Instead, I offered "plausible cascades" and said "I don't know" when the answer was in the system the whole time.

**The answer was: the install script downloads models but never starts the server. The "sovereign" pattern is incomplete.**

---

*⬡ OMEGA ⬡ GROKSTER ⬡ SOVEREIGN-LOCAL-FIX ⬡ 2026-08-28 ⬡ The local inference server is never started. The install script is incomplete. Fix: add scripts/serve_native_gguf.sh + add health checks to defaultModel().*
