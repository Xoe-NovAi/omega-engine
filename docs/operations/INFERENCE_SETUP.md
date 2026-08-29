# 🔱 Omega Engine — Local Inference Setup Guide
**AP-Token**: `AP-OMEGA-INFERENCE-v2.0.0`
**Last Updated**: 2026-05-13

---

## Primary Backend: lmster (LM Studio Headless Server)

lmster is the **canonical primary inference backend** for the Omega Engine. It serves OpenAI-compatible completions at `http://127.0.0.1:1234`.

### Installation Location
```
~/.lmstudio/bin/lms              # LM Studio CLI (in PATH)
~/.lmstudio/llmster/0.0.12-1/llmster   # llmster binary (direct GGUF inference)
```

### Start the Server
```bash
lms server start
```

### Load a Model
```bash
# Load the lightweight workhorse (1.6GB, fits easily in 14GB RAM)
lms load qwen3-1.7b-q6_k

# Or load via model path
lms load --path /media/arcana-novai/omega_library/omega-stack/models/Qwen3-1.7B-Q6_K.gguf
```

### Verify
```bash
lms status                  # Should show: Server: ON
lms ps                      # Shows loaded models
curl http://127.0.0.1:1234/v1/models   # Should return JSON
```

### Run Omega Tests Against Live lmster
```bash
cd ~/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate
PYTHONPATH=src python -m pytest tests/ -v --tb=short -x --timeout=30
```

---

## Fallback Backend: Ollama

Ollama serves as the secondary fallback at `http://127.0.0.1:11434`.

```bash
ollama run qwen3:1.7b       # Auto-downloads and serves
```

---

## Test Mode (CI/CD)

For CI/CD and offline testing, the `OfflineMockBackend` is activated via:
```bash
OMEGA_ENV=test PYTHONPATH=src python -m pytest tests/
```

This returns deterministic "Mock response" strings, runs in ~2s, and requires zero inference backends.

---

## Available GGUF Models (External Drive)

| Model | Size | Path |
|-------|------|------|
| Qwen3-1.7B-Q6_K | 1.6 GB | `/media/arcana-novai/omega_library/omega-stack/models/Qwen3-1.7B-Q6_K.gguf` |
| Qwen3-4B-Thinking-Q4_K_M | 2.4 GB | `/media/arcana-novai/omega_library/omega-stack/models/Qwen3-4B-Thinking-2507-Q4_K_M.gguf` |
| phi-4-mini-reasoning-abliterated | 2.4 GB | `/media/arcana-novai/omega_library/omega-stack/models/phi-4-mini-reasoning-abliterated-q4_k_m.gguf` |
| DeepSeek-R1-Qwen3-8B-Q3_K_L | 4.2 GB | `/media/arcana-novai/omega_library/omega-stack/models/DeepSeek-R1-0528-Qwen3-8B-Q3_K_L.gguf` |
| Krikri-8B-Instruct-Q5_K_M | 5.5 GB | `/media/arcana-novai/omega_library/omega-stack/models/Krikri-8b-Instruct-Q5_K_M.gguf` |
| functiongemma-270m-it-Q6_K (Nova) | 270 MB | `/media/arcana-novai/omega_library/omega-stack/models/functiongemma-270m-it-Q6_K.gguf` |

---

## Backend Priority Chain

```
1. lmster (LM Studio headless @ :1234)  ← PRIMARY
2. Ollama (@ :11434)                     ← BACKUP
3. llama.cpp (@ :8080)                   ← ALTERNATIVE
4. ONNX Runtime                          ← EMBEDDING ONLY
5. llama-cli (subprocess)                ← LAST RESORT
6. llmster (subprocess)                  ← LAST RESORT
7. OfflineMockBackend                    ← TEST MODE ONLY
8. Graceful fallback message             ← NO BACKENDS
```

*🔱 The Engine is sovereign. Inference is local.*
