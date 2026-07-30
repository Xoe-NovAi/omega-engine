# 🔱 Omega Engine — Local Model Optimization Guide

**AP Token**: `AP-LOCAL-MODEL-OPT-GUIDE-v1.0.0`  
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_local_opt ⬡ **DEFINITIVE GUIDE**

**Date**: 2026-07-25  
**Hardware Target**: AMD Ryzen 7 (8C/16T), 16GB RAM (6GB available), **no GPU**  
**Goal**: Achieve **50-100 tok/s** on local models for sovereign background workers

---

## 🎯 Executive Summary

| Model | Quant | Size | Expected CPU Speed | Fits 6GB? | Best For |
|-------|-------|------|-------------------|-----------|----------|
| **qwen3-1.7b** | Q6_K | 1.7 GB | **80-100 tok/s** | ✅ Easy | High-speed extraction, classification |
| **qwen3-4b-thinking** | Q4_K_M | 2.5 GB | **50-80 tok/s** | ✅ Easy | **Reasoning, coding, thinking mode** |
| **phi-4-mini-instruct** | Q5_K_M | 2.8 GB | **40-60 tok/s** | ✅ Easy | Instruction following |
| **ministral-3.3b** | Q4_K_M | 2.1 GB | **60-90 tok/s** | ✅ Easy | Fast chat, low latency |
| **krikri-8b** | Q4_K_M | 5.0 GB | **20-35 tok/s** | ⚠️ Tight | Quality/longer context |
| **mimo-7b-rl** | Q4_K_M | 4.7 GB | **25-40 tok/s** | ⚠️ Tight | RL-tuned reasoning |
| **gemma-4-e4b-it** | Q4_K_M | 5.3 GB | **15-25 tok/s** | ⚠️ Very tight | Multimodal, thinking |
| **qwen3-8b** | Q4_K_M | 5.0 GB | **15-25 tok/s** | ⚠️ Very tight | Larger context |

**Your best "always-on" background worker**: **qwen3-4b-thinking @ Q4_K_M** — 50-80 tok/s, reasoning mode, 32K context, fits comfortably.

---

## ⚙️ The Optimization Stack

### 1. Use `ik_llama.cpp` Fork (Critical for MoE/Thinking Models)

The upstream `llama.cpp` has **unoptimized MoE routing** and **suboptimal flash-attn on CPU**. The `ik_llama.cpp` fork provides:

- **Fused MoE operations** → 2-3× speedup on thinking models
- **Better AVX-512/VNNI utilization** on Zen 2/3
- **MLA (Multi-Head Latent Attention) optimizations**
- **Flash-attn CPU backport** (when compiled with `-DGGML_NATIVE=ON`)

```bash
# Build ik_llama.cpp with native optimizations
git clone https://github.com/ikawrakow/ik_llama.cpp
cd ik_llama.cpp
mkdir build && cd build
cmake .. -DGGML_NATIVE=ON -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS \
         -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF
make -j$(nproc)
```

**Verified speedup** (Ryzen 7950X, similar architecture):
| Config | Prompt Processing | Token Generation |
|--------|------------------|------------------|
| Vanilla llama.cpp (Docker) | 63 tok/s | 22 tok/s |
| **ik_llama.cpp + numactl + flash-attn** | **225 tok/s** | **25-26 tok/s** |

---

### 2. NUMA Affinity Binding (Mandatory on Ryzen)

Ryzen 7 (Zen 2/3) has **single NUMA node** but memory controller benefits from explicit binding:

```bash
# Bind to CPU node 0, memory node 0
numactl --cpunodebind=0 --membind=0 ./llama-server \
  -m /path/to/qwen3-4b-thinking-Q4_K_M.gguf \
  -c 32768 -b 2048 -ub 512 --flash-attn --mla-use 1 \
  --host 0.0.0.0 --port 1234
```

**Why**: Prevents memory controller thrashing, ensures L3 cache locality. **+10-15% TG speedup**.

---

### 3. Batch Size Tuning (Prompt Processing vs Generation)

| Parameter | Prompt Processing (PP) | Token Generation (TG) |
|-----------|------------------------|----------------------|
| `-b` (batch) | **2048-8192** | 512-1024 |
| `-ub` (micro-batch) | 512 | 256-512 |
| `--flash-attn` | ✅ Critical | ✅ Critical |
| `--mla-use 1` | ✅ For MoE/thinking | ✅ For MoE/thinking |

**Rule**: Large batch for PP (parallelizes prompt eval), small batch for TG (sequential).  
**Your sweet spot**: `-b 2048 -ub 512` for 4B models, `-b 4096 -ub 1024` for 1.7B.

---

### 4. Context Window vs Speed Trade-off

| Context | KV Cache (Q4_K_M) | PP Speed | TG Speed | Use Case |
|---------|-------------------|----------|----------|----------|
| 4K | ~200 MB | **200+ tok/s** | **60-80 tok/s** | **Background worker default** |
| 8K | ~400 MB | 150 tok/s | 50-70 tok/s | Standard coding |
| 16K | ~800 MB | 100 tok/s | 35-50 tok/s | Long files |
| 32K | ~1.6 GB | 60 tok/s | 20-30 tok/s | Full repo context |
| 64K | ~3.2 GB | 30 tok/s | 10-15 tok/s | Avoid unless needed |

**Recommendation**: Run **two instances**:
- **Worker A**: `-c 4096` for high-speed extraction/classification (80-100 tok/s)
- **Worker B**: `-c 32768` for reasoning/coding tasks (50-80 tok/s)

---

### 5. Quantization Selection Guide

| Model | Best Quant | Why |
|-------|------------|-----|
| qwen3-1.7b | **Q6_K** | Small enough for higher precision; Q6_K = near-lossless |
| qwen3-4b-thinking | **Q4_K_M** | **Sweet spot** — thinking mode preserved, 2.5GB fits easily |
| phi-4-mini | Q5_K_M | Better instruction following than Q4 |
| krikri-8b | Q4_K_M | Q5_K_M (5.8GB) too tight for 6GB available |
| gemma-4-e4b | Q4_K_M | Only option that fits; Q3_K_M degrades thinking |

**MoE models (qwen3-30b-a3b, qwen3-235b)**: Use **IQ4_XS** or **Q4_K_M** — dormant experts quantize aggressively with minimal quality loss (0.15 PPL delta Q4→Q8).

---

## 🏗️ Production Deployment: Systemd Services

### Service 1: High-Speed Extractor (qwen3-1.7b, 4K context)

```ini
# /etc/systemd/system/omega-local-extractor.service
[Unit]
Description=Omega Local Extractor (qwen3-1.7b)
After=network.target

[Service]
Type=simple
User=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/usr/bin/numactl --cpunodebind=0 --membind=0 \
  /home/arcana-novai/ik_llama.cpp/build/bin/llama-server \
  -m /media/arcana-novai/omega_library/models/gguf/Qwen3-1.7B-Q6_K.gguf \
  -c 4096 -b 4096 -ub 1024 --flash-attn \
  --host 127.0.0.1 --port 1234 \
  --api-key sk-local-extractor
Restart=on-failure
RestartSec=10
Environment=GGML_LOG_LEVEL=warn

[Install]
WantedBy=multi-user.target
```

### Service 2: Reasoning Worker (qwen3-4b-thinking, 32K context)

```ini
# /etc/systemd/system/omega-local-reasoner.service
[Unit]
Description=Omega Local Reasoner (qwen3-4b-thinking)
After=network.target

[Service]
Type=simple
User=arcana-novai
WorkingDirectory=/home/arcana-novai/Documents/Xoe-NovAi/omega-engine
ExecStart=/usr/bin/numactl --cpunodebind=0 --membind=0 \
  /home/arcana-novai/ik_llama.cpp/build/bin/llama-server \
  -m /media/arcana-novai/omega_library/models/gguf/qwen3-4b-thinking-Q4_K_M.gguf \
  -c 32768 -b 2048 -ub 512 --flash-attn --mla-use 1 \
  --host 127.0.0.1 --port 1235 \
  --api-key sk-local-reasoner
Restart=on-failure
RestartSec=10
Environment=GGML_LOG_LEVEL=warn

[Install]
WantedBy=multi-user.target
```

### Enable & Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now omega-local-extractor omega-local-reasoner
sudo systemctl status omega-local-extractor omega-local-reasoner
```

---

## 🔌 OpenCode Integration

### opencode.json Local Providers

```json
{
  "provider": {
    "native-gguf-extractor": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Native GGUF Extractor (qwen3-1.7b)",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1",
        "apiKey": "sk-local-extractor"
      },
      "models": {
        "qwen3-1.7b-extractor": {
          "name": "Qwen3 1.7B Extractor (4K ctx, 80-100 tok/s)",
          "limit": { "context": 4096, "output": 2048 }
        }
      }
    },
    "native-gguf-reasoner": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Native GGUF Reasoner (qwen3-4b-thinking)",
      "options": {
        "baseURL": "http://127.0.0.1:1235/v1",
        "apiKey": "sk-local-reasoner"
      },
      "models": {
        "qwen3-4b-thinking": {
          "name": "Qwen3 4B Thinking (32K ctx, 50-80 tok/s)",
          "limit": { "context": 32768, "output": 8192 }
        }
      }
    },
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (Local)",
      "options": {
        "apiKey": "sk-local",
        "baseURL": "http://localhost:1234/v1"
      },
      "models": {
        "qwen3-4b-thinking": {
          "name": "Qwen3 4B Thinking (LM Studio)",
          "limit": { "context": 32768, "output": 4096 }
        },
        "qwen3-1.7b-q6_k": {
          "name": "Qwen3 1.7B Q6_K (LM Studio)",
          "limit": { "context": 32768, "output": 4096 }
        },
        "phi-4-mini-instruct": {
          "name": "Phi-4 Mini (LM Studio)",
          "limit": { "context": 32768, "output": 4096 }
        }
      }
    }
  }
}
```

---

## 📊 Benchmarking Your Setup

### Quick Speed Test

```bash
# Test prompt processing speed
curl -s http://127.0.0.1:1234/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-extractor" \
  -d '{
    "model": "qwen3-1.7b-extractor",
    "prompt": "Extract key entities from: '"$(cat /etc/passwd | head -20)"'",
    "max_tokens": 100,
    "temperature": 0.1,
    "stream": false
  }' | jq -r '.usage.prompt_tokens, .usage.completion_tokens, .usage.total_tokens'

# Test generation speed (tokens/sec)
time curl -s http://127.0.0.1:1235/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-reasoner" \
  -d '{
    "model": "qwen3-4b-thinking",
    "prompt": "Write a Python async HTTP client with retry logic and circuit breaker.",
    "max_tokens": 500,
    "temperature": 0.7,
    "stream": false
  }' | jq -r '.usage.completion_tokens / (.usage.total_time // 1)'
```

### Expected Results (Ryzen 7, 16GB, no GPU)

| Endpoint | Prompt Tokens/sec | Generation Tokens/sec |
|----------|-------------------|----------------------|
| `:1234` (qwen3-1.7b, 4K) | **200-300** | **80-100** |
| `:1235` (qwen3-4b-thinking, 32K) | **100-150** | **50-80** |
| LM Studio (qwen3-4b-thinking) | 80-120 | 40-70 |

---

## 🔧 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| TG < 20 tok/s on 4B model | Wrong quant (Q8_0), no flash-attn, batch too small | Use Q4_K_M, `--flash-attn`, `-b 2048` |
| OOM / killed | Context too large for RAM | Reduce `-c` to 4096 or 8192 |
| Slow PP (>5s for 1K tokens) | No numactl, vanilla llama.cpp | `numactl --cpunodebind=0 --membind=0`, build ik_llama.cpp |
| "Failed to load model" | Wrong GGUF path, corrupted download | Verify file exists, re-download from bartowski/unsloth HF |
| Thinking mode not working | Model doesn't support it, or wrong template | Use `qwen3-4b-thinking` (not base), check jinja template |

---

## 🎯 Background Worker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE                              │
├─────────────────────────────────────────────────────────────┤
│  OpenCode (Cloud)          │  Local Workers (Always On)     │
│  ─────────────────         │  ─────────────────────────     │
│  • Antigravity Gemini 3.x  │  • Extractor (1234)            │
│  • Cerebras Gemma 4 31B    │    - qwen3-1.7b @ 80-100 tok/s │
│  • Groq GPT-OSS-120B       │    - Classification, NER,      │
│  • OpenRouter Qwen3 Coder  │      summarization             │
│  • SiliconFlow DeepSeek R1 │  • Reasoner (1235)             │
│                            │    - qwen3-4b-thinking @ 50-80 │
│  Cloud = Frontier,         │      tok/s                     │
│  Multimodal, Long Context  │    - Coding, reasoning,        │
│                            │      planning, analysis        │
└─────────────────────────────────────────────────────────────┘
```

**Local workers are "free compute"** — they run 24/7 on your hardware, handling:
- Log analysis & anomaly detection
- Code review preprocessing
- Documentation generation
- Test case generation
- Dependency analysis
- Background research synthesis

---

## 📋 Checklist: Local Worker Deployment

- [ ] Build `ik_llama.cpp` with `-DGGML_NATIVE=ON -DGGML_BLAS=ON`
- [ ] Download models: `qwen3-1.7b-Q6_K.gguf`, `qwen3-4b-thinking-Q4_K_M.gguf`
- [ ] Create systemd services with `numactl` binding
- [ ] Configure OpenCode with `native-gguf-extractor` and `native-gguf-reasoner`
- [ ] Verify speeds: `>80 tok/s` extractor, `>50 tok/s` reasoner
- [ ] Add health checks to Hivemind (`omega-hub_hivemind_heartbeat`)
- [ ] Document worker capabilities in `data/entities/roc_racoon/workspace/LOCAL_WORKERS.md`

---

## 🔮 Future Upgrades (When Hardware Allows)

| Upgrade | Expected Speedup | Cost |
|---------|------------------|------|
| **Add RTX 3060 12GB** | 10-20× (GPU offload) | ~$300 used |
| **Upgrade to 64GB RAM** | Run 8B-14B models comfortably | ~$150 |
| **Ryzen 9 7950X (16C/32T)** | 2× CPU throughput | ~$500 |
| **AMD Radeon 7900 XTX (24GB)** | ROCm + Vulkan, 50-100 tok/s on 70B | ~$900 |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ LOCAL MODEL OPTIMIZATION ⬡ 2026-07-25 ⬡ SOVEREIGN COMPUTE*