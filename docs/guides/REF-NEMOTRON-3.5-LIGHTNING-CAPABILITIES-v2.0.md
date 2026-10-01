#  📚 NEMOTRON 3.5 LIGHTNING — MODEL CAPABILITIES & DEPLOYMENT REFERENCE
**Document ID:** `REF-NEMOTRON-3.5-LIGHTNING-CAPABILITIES-v2.0`  
**Status:** `ACTIVE`  
**Audience:** Higher-level models authoring execution guides for Nemotron 3.5 Lightning  
**Purpose:** Single source of truth for model characteristics, deployment, and authoring best practices  
**Retention:** Architecture-scoped (Valid until next major model generation or inference engine shift)  

---

## 1. MODEL SPECIFICATIONS (Grounded from NVIDIA Sources)

| Property | Value | Source |
|----------|-------|--------|
| **Model ID** | `nvidia/nemotron-3.5-lightning-30b-a3b` | NVIDIA NIM / HF Model Card |
| **Total Parameters** | 30B | NVIDIA Model Card |
| **Active Parameters/Token** | 3B | LatentMoE routing |
| **Architecture** | Hybrid LatentMixture-of-Experts (LatentMoE) | NVIDIA Technical Blog / NIM Docs |
| **Components** | Mamba-2 SSM + MoE layers + Select Attention | NVIDIA NIM Docs |
| **Context Window (Native)** | 262,144 tokens (256K) | NVIDIA NIM Docs |
| **Context Window (Extended)** | 1,048,576 tokens (1M) with `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` | NVIDIA NIM Docs |
| **Quantization (Production)** | NVFP4 (W4A16) with QAD | NVIDIA Quantization Docs |
| **Quantization (Ollama)** | Q8_0 (~35GB), MXFP8 (~34GB) | Ollama Library |
| **Quantization (llama.cpp)** | Q4_K_M, Q8_0 GGUF | HF ggml-org repo |
| **License** | NVIDIA Open Model License / OpenMDW-1.1 | Model Card |
| **Knowledge Cutoff** | Pre-training: Sep 2025; Post-training: May 2026 | HF Model Card |
| **Modality** | Text-only | NVIDIA NIM Docs |
| **Supported Languages** | English, Spanish, French, German, Italian, Japanese | HF Model Card |
| **Release Date** | August 11, 2026 (GA) | HF Model Card |

### 1.1 Architecture Deep-Dive (from NVIDIA Technical Blog, NIM Docs & Training Recipe)
```
LatentMoE = Interleaved [Mamba-2 Block → MoE Layer → Attention Layer] × N
- Mamba-2: Constant compute/memory per token (SSM state cache)
- MoE: Sparse expert routing — 128 routed experts (top-6) + 1 shared expert,
       via latent-space projection (LatentMoE projects activations into a
       lower-dimensional latent space, enabling more experts at constant cost)
- Attention: Select layers for global context integration
- Router: Latent projection + top-6 expert routing per token
- Total Layers: 52-layer hybrid backbone; Hidden dimension 2688
  (per NVIDIA training recipe: "Layers / Hidden | 52 / 2688")
```

### 1.2 Training Pipeline (from HF Model Card)
| Stage | Description | Data |
|-------|-------------|------|
| **1. Pre-training** | 20T+ tokens, NVFP4 recipe | Crawled + synthetic code, math, science, general |
| **2. Continued Pre-training (MTP)** | Multi-Token Prediction heads | Aligns MTP layers with base distribution |
| **3. Supervised Fine-Tuning** | Code, math, science, tool calling, instruction following, structured outputs, long-range retrieval | Synthetic + curated |
| **4. Reinforcement Learning (GRPO)** | Multi-environment: math, code, science, instruction following, multi-step tool use, multi-turn, structured output | NeMo RL + NeMo Gym (async architecture) |
| **5. Post-training Quantization (PTQ + QAD)** | NVFP4 via Model Optimizer | `cnn_nemotron_v2_mix` calibration (1000 samples, 32K seq) |

### 1.3 Performance Profile (from NVIDIA Dynamo Recipes & HF Benchmarks)

| Metric | Value | Conditions |
|--------|-------|------------|
| **Throughput (NVFP4, MTP=3, c=32-64)** | ~156 tok/s aggregate | HP ZGX Nano (GB10), Mooncake trace |
| **Throughput Gain (NVFP4 vs BF16)** | 2.46-2.80× faster | MTP=3 across concurrency range |
| **Acceptance Rate (MTP k=3)** | 82-84% | c=1 to c=64 |
| **TTFT p50 Target** | <5 seconds | Dynamo recipe pass criteria |
| **Tok/s/user Target** | ≥50 | Dynamo recipe pass criteria |
| **VRAM (NVFP4)** | ~22 GB | Single H100 / RTX 4090 feasible |
| **VRAM (BF16)** | ~60 GB | Single H100 80GB (leaves little room for draft) |
| **Resident Memory (BF16, ZGX Nano)** | 58.93 GiB | HP Z Runtime measurements |

---

## 2. DEPLOYMENT CONFIGURATIONS (All Three Backends)

### 2.1 vLLM (Primary — Best Agent Workload Support)

#### 2.1.1 Recommended: NVFP4 + DSpark (Interactive, c≤128)
```bash
# Inside vllm/vllm-openai:v0.27.1 container
vllm serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --served-model-name nemotron-3.5-lightning \
  --max-num-seqs 128 \
  --max-model-len 1048576 \
  --enable-prefix-caching \
  --async-scheduling \
  --speculative_config.method dspark \
  --speculative_config.model nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark \
  --trust-remote-code \
  --reasoning-parser nemotron_v3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

#### 2.1.2 Alternative: NVFP4 + DFlash (Interactive, c≤128)
```bash
# Replace DSpark block with:
--speculative_config.method dflash \
--speculative_config.model nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash \
--speculative_config.num_speculative_tokens 3 \
--speculative_config.attention_backend FLASHINFER
```

#### 2.1.3 Alternative: NVFP4 + MTP (Built-in, No Separate Draft)
```bash
# Replace DSpark block with:
--speculative_config.method mtp \
--speculative_config.num_speculative_tokens 3
# Note: NVFP4 checkpoint has num_lookahead_tokens=3 architecturally fixed
```

#### 2.1.4 High-Throughput: NVFP4 No Speculative (c=256, 1M context)
```bash
vllm serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --served-model-name nemotron-3.5-lightning \
  --max-num-seqs 256 \
  --max-model-len 1048576 \
  --enable-prefix-caching \
  --trust-remote-code \
  --reasoning-parser nemotron_v3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

#### 2.1.5 BF16 Baseline (No Speculative, 256K Context)
```bash
vllm serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 \
  --served-model-name nemotron-3.5-lightning \
  --max-num-seqs 128 \
  --max-model-len 262144 \
  --enable-prefix-caching \
  --trust-remote-code \
  --reasoning-parser nemotron_v3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

#### 2.1.6 Key vLLM Flags Explained

| Flag | Purpose | Critical Notes |
|------|---------|----------------|
| `--reasoning-parser nemotron_v3` | Separates `<thinking>` from final answer | **Mandatory** for reasoning tasks; vLLM-specific name |
| `--enable-auto-tool-choice` | Allows `tool_choice: "auto"` | Required for tool calling |
| `--tool-call-parser qwen3_coder` | Parses Qwen3-Coder tool format | vLLM-specific name |
| `--trust-remote-code` | Loads custom model code | **Mandatory** for this architecture |
| `--generation-config vllm` | Overrides model's sampling defaults | Add via `NIM_PASSTHROUGH_ARGS` or CLI |
| `--mamba-cache-mode align` | Aligns Mamba/Attention KV cache | Hybrid arch correctness |
| `--moe-backend humming` | NVIDIA MoE kernels for NVFP4 | Quantized MoE performance |
| `--mamba-backend flashinfer` | Fused kernels for recurrent layers | Required for Mamba-2 |
| `--mamba-ssm-cache-dtype float16` | FP16 Mamba state cache | Speedup from FP32 |
| `--speculative_config.num_speculative_tokens` | Draft depth | Must ≥ draft checkpoint's block size (DSpark: 3) |
| `--max-model-len 1048576` | 1M context | Requires `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` for >256K |
| `--enable-prefix-caching` | KV cache reuse | Critical for agent workloads with shared prefixes |

### 2.2 SGLang (Alternative — Fast, Flexible)

#### 2.2.1 NVFP4 + DSpark (1x H100)
```bash
docker pull lmsysorg/sglang:dev-nemotron3-5-lightning

sglang serve --model-path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --host 127.0.0.1 --port 8000 \
  --served-model-name nemotron-3.5-lightning \
  --context-length 1048576 \
  --speculative-draft-model-path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark \
  --speculative-num-steps 3 \
  --mem-fraction-static 0.85 \
  --decode-cuda-graph-max-bs 16 \
  --reasoning-parser nemotron_3 \
  --tool-call-parser qwen3_coder
```

#### 2.2.2 Key SGLang Differences
| Aspect | vLLM | SGLang |
|--------|------|--------|
| Reasoning parser name | `nemotron_v3` | `nemotron_3` |
| Speculative config | CLI flags | `--speculative-draft-model-path` + `--speculative-num-steps` |
| Memory fraction | `--gpu-memory-utilization` | `--mem-fraction-static` |
| BF16 memory | ~60GB H100 | Same; `--mem-fraction-static 0.78` |

### 2.3 TensorRT-LLM (Highest Performance, MTP Only)

#### 2.3.1 NVFP4 + MTP (1x H100)
```bash
# Create extra-llm-api-config.yml first:
cat > ./extra-llm-api-config.yml << EOF
kv_cache_config:
  dtype: fp8
  enable_block_reuse: false
  free_gpu_memory_fraction: 0.8
  mamba_ssm_cache_dtype: float16
  mamba_ssm_stochastic_rounding: true
  mamba_ssm_philox_rounds: 5
  mamba_state_config:
    periodic_snapshot_interval: 8192

moe_config:
  backend: MARLIN
EOF

# Then serve:
docker pull nvcr.io/nvidia/tensorrt-llm/release:1.3.0rc24

trtllm-serve nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --host 127.0.0.1 --port 8000 \
  --max_batch_size 8 \
  --max_num_tokens 8192 \
  --max_seq_len 1048576 \
  --trust_remote_code \
  --served_model_name nemotron-3.5-lightning \
  --reasoning_parser nemotron-v3 \
  --tool_parser qwen3_coder \
  --extra_llm_api_options extra-llm-api-config.yml
```

#### 2.3.2 Add MTP Speculative (Modify YAML)
```yaml
# Add to extra-llm-api-config.yml:
speculative_decoding_config:
  mtp:
    enabled: true
    num_speculative_tokens: 3
```

#### 2.3.3 Key TensorRT-LLM Differences
| Aspect | vLLM/SGLang | TensorRT-LLM |
|--------|-------------|--------------|
| Reasoning parser | `nemotron_v3` / `nemotron_3` | `nemotron-v3` |
| Tool parser | `qwen3_coder` | `qwen3_coder` |
| Speculative decoding | DSpark, DFlash, MTP | **MTP only** |
| Config format | CLI flags | YAML (`extra-llm-api-options`) |
| KV cache | PagedAttention | FP8 block config |
| Mamba state | `float16` + stochastic rounding | Same |

### 2.4 Ollama (Local Development)
```bash
# Q8_0 (higher quality, ~35GB, 256K context on 48GB+ VRAM)
ollama pull nemotron-3.5-lightning:30b-a3b-q8_0

# MXFP8 (faster, ~34GB)
ollama pull nemotron-3.5-lightning:30b-a3b-mxfp8

ollama run nemotron-3.5-lightning:30b-a3b-q8_0

# Context control:
/set parameter num_ctx 262144  # May CPU-offload if VRAM insufficient
```

### 2.5 llama.cpp (CPU/Edge)
```bash
llama-server -hf ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF:Q4_K_M \
  --temp 1.0 --top-p 0.95 \
  -np 1 -c 40960 --port 8000 \
  -ngl 99 -fa on --jinja --no-webui --fit off
# Validated context: ~40K; raise -c as VRAM allows
```

---

## 3. QUANTIZATION DEEP-DIVE (from NVIDIA Quantization Docs)

### 3.1 NVFP4 PTQ + QAD Pipeline
```bash
# From NVIDIA Model Optimizer examples/megatron_bridge/
# Step 1: PTQ (Post-Training Quantization)
python quantize.py \
  --hf_model_name_or_path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 \
  --trust_remote_code \
  --tp_size 1 --ep_size 1 --pp_size 1 \
  --recipe models/Nemotron-3.5-Lightning-30B-A3B/lightning_w4a16_nvfp4_4o6 \
  --calib_batch_size 1 \
  --calib_num_samples 1000 \
  --seq_length 32768 \
  --export_megatron_path /path/to/lightning-nvfp4-ptq

# Step 2: QAD (Quantization-Aware Distillation)
# Data blend (public Nemotron post-training):
export DATA_BLEND="20 /path/to/Nemotron-Pretraining-SFT-v1 \
  17 /path/to/Nemotron-SFT-Math-v3 \
  15 /path/to/competitive_programming_python_00_messages \
  ..."

python -u distill.py \
  --teacher_hf_path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 \
  --student_hf_path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 \
  --student_megatron_path /path/to/lightning-nvfp4-ptq \
  --trust_remote_code \
  --tp_size 1 --ep_size 16 --pp_size 1 --cp_size 4 \
  --data_paths ${DATA_BLEND} \
  --data_path_to_cache /path/to/blend_idx_cache \
  --seq_length 32768 --mbs 1 --gbs 64 \
  --lr 2e-5 --min_lr 5e-6 --lr_warmup_iters 30 \
  --eval_interval 50 --eval_iters 8 --log_interval 10 \
  --train_iters 200 \
  --checkpoint_keep_last 2 \
  --output_dir /path/to/lightning-nvfp4-qad

# Step 3: Export to HF
python -u export_quantized_megatron_to_hf.py \
  --hf_model_name_or_path nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 \
  --megatron_path /path/to/lightning-nvfp4-qad/checkpoints \
  --trust_remote_code \
  --pp_size 1 \
  --export_unified_hf_path /path/to/lightning-nvfp4-hf
```

### 3.2 Quantization Recipe: `four_over_six` (Production)
| Component | Quantization | Calibration |
|-----------|--------------|-------------|
| MoE / Shared / lm_head weights | W4A16 dynamic NVFP4 | max |
| Mamba in_proj / out_proj | W4A16 NVFP4 | max |
| KV cache | FP8 | — |
| Attention projections | BF16 (kept) | — |
| lm_head | W4A16 (faithful lm_head) | — |
| Router | FP32 (kept) | — |

**Result**: 66 GB BF16 → 22 GB NVFP4 (3× compression), accuracy recovered via QAD

### 3.3 Key QAD Insights
- **Sequence length critical**: 522K seq length needed for long-context benchmarks (post-training SFT used ~522K)
- **Training tokens**: ~419M tokens over 200 iterations (8 nodes × 4 GPUs, DP=8, CP=4)
- **Calibration data**: `cnn_nemotron_v2_mix` (CNN DailyMail + Nemotron-Post-Training v2), 1000 samples, 32K tokens

---

## 4. KNOWN ISSUES & WORKAROUNDS (from NVIDIA NIM Docs + Cookbooks)

| Issue | Impact | Workaround |
|-------|--------|------------|
| **Reasoning + output share `max_tokens`** | Long reasoning truncates answer | Increase `max_tokens` 2-3× expected output; disable thinking for structured output |
| **Model provides `generation_config.json` defaults** | Unexpected sampling (temp, top_p) | Add `--generation-config vllm` (vLLM) / omit in TRT-LLM |
| **Backend validates empty `messages`** | Cryptic errors on malformed requests | Always send non-empty `messages[]` array |
| **No vision capability** | Cannot process images | Text-only workflows only |
| **Extended context >256K unvalidated** | Quality degradation risk | Test per workload; prefer chunking over extension |
| **DSpark block size fixed** | `--speculative_config.num_speculative_tokens` must ≥ 3 | vLLM refuses to start below draft's `dspark_block_size` |
| **BF16 + speculator OOM** | 60GB weights + draft > 80GB H100 | Use NVFP4 for speculative; benchmark before assuming speculator wins |
| **Thinking tokens count against budget** | Budget exhaustion on complex tasks | Budget explicitly; use `chat_template_kwargs.enable_thinking: false` for JSON |
| **Parser names backend-specific** | Wrong parser = no parsing | vLLM: `nemotron_v3`, SGLang: `nemotron_3`, TRT-LLM: `nemotron-v3` |

---

## 5. AUTHORING BEST PRACTICES FOR EXECUTION GUIDES

### 5.1 Prompt Design Principles (Model-Agnostic)

**DO:**
- Separate **task specification** from **model-specific prompting**
- Use `enable_thinking: false` for structured output (JSON, docs, code)
- Provide explicit output format templates with examples
- Chunk large tasks: "Process files 1-5, then 6-10"
- Specify verification steps: "Run linter after each fix"
- Include context: surrounding code, imports, project conventions

**DON'T:**
- Include model architecture docs in execution guides
- Assume the model knows your codebase conventions
- Omit error handling requirements
- Mix "what to do" with "how the model works"
- Use filesystem globs for index operations (use `git ls-files | xargs`)

### 5.2 Context Window Management Strategies

| Strategy | Token Budget | When to Use |
|----------|--------------|-------------|
| **Single-file + context** | <50K | Files <50K tokens; include imports/surrounding code |
| **Related file batches (5-10)** | 50-150K | Cohesive modules (e.g., all audit files) |
| **Chunked with 20% overlap** | 150-256K | Large refactors; maintain continuity |
| **Reset between unrelated tasks** | N/A | Prevents context pollution; start fresh session |

### 5.3 Output Format Templates (Standardized)

**For Code Fixes:**
```markdown
## File: path/to/file.py
### Before:
```python
[exact lines with line numbers if possible]
```
### After:
```python
[fixed lines]
```
### Justification:
[Why this fix is correct per project standards]
```

**For Audits:**
```markdown
## File: path/to/file.py
### Finding: [Bare except at line 42]
### Classification: [M9 violation / False positive / Already compliant]
### Fix Required: [Yes/No + specific fix if yes]
```

**For Documentation:**
```markdown
# Title
## Context
[Why this doc exists; link to driving decision/issue]
## Content
[Structured sections with headers]
## References
[Links to related artifacts, decisions, specs]
```

**For Scripts:**
```markdown
## Script: scripts/script_name.py
### Purpose
[One-line description]
### Usage
```bash
python scripts/script_name.py [args]
```
### Exit Codes
- 0: Success
- 1: [Specific failure mode]
- 2: [Another failure mode]
### Validation
```bash
python -m py_compile scripts/script_name.py
./scripts/script_name.py --help
```
```

---

## 6. QUALITY ASSURANCE CHECKLISTS

### 6.1 Code Generation Validation
- [ ] `python -m py_compile` passes
- [ ] Imports resolve in target environment (`.venv`)
- [ ] Linters clean (ruff, pylint per project config)
- [ ] Existing tests pass (if applicable)
- [ ] Logging follows project patterns: `logger.warning("ctx: %s", e, exc_info=True)`
- [ ] No bare `except Exception:` (M9 compliance)
- [ ] Type hints where project requires

### 6.2 Documentation Validation
- [ ] Technically accurate (cross-reference with code)
- [ ] Audience-appropriate tone
- [ ] All placeholders resolved
- [ ] Links valid (relative paths preferred)
- [ ] Follows Omega Document Management System (if applicable)

### 6.3 Script Validation
- [ ] Shebang + executable bit (`chmod +x`)
- [ ] Exit codes: 0 success, non-zero failure with message
- [ ] `--help` / `-h` works
- [ ] Dry-run mode if destructive
- [ ] Input validation with clear errors

---

## 7. MODEL SWITCHING PROTOCOL

### 7.1 When to Use Nemotron 3.5 Lightning
- High-volume code pattern tasks (audits, fixes across many files)
- Tool-calling agentic workflows
- Structured output generation (JSON, YAML, markdown)
- Long-context single-session tasks (<256K native, up to 1M extended)
- Cost/latency sensitive execution
- Local inference on single GPU (H100, RTX 4090, GB10)

### 7.2 When to Escalate to Larger Model (Nemotron 3 Ultra, Sonnet, etc.)
- Architectural decisions requiring cross-domain synthesis
- Novel problem solving without established patterns
- Complex reasoning requiring >3B active params consistently
- Multi-modal requirements (vision, audio)
- **Escalation trigger (per Antigravity dialectic 2026-09-21):** **Two consecutive failed validation loops on the same file/task** — i.e., "attempt fix → validation fails → attempt re-fix → validation fails". At the second failure, mark the task `BLOCKED-ESCALATE` and hand off to a frontier model.

### 7.3 Handoff Requirements (M15 Continuity)
```
Handoff Packet Must Include:
- Current task state + progress (% complete, blockers)
- Relevant codebase context (files, patterns, conventions)
- Continuity artifacts (session_gnosis.md, projection.md, proposed_lessons.yaml)
- Explicit "next action" for receiving model
- Model-specific config if different (deployment flags, parser names)
- Validation results so far (linter output, test results)
```

---

## 8. PERFORMANCE TUNING KNOBS

| Knob | Range | Trade-off | Recommended Starting Point |
|------|-------|-----------|---------------------------|
| `--max-num-seqs` | 128-512 | Concurrency vs VRAM | 128 (interactive), 256 (batch) |
| `--max-model-len` | 32K-1M | Context vs KV cache | 262144 (native), 1048576 (extended) |
| `--max-num-batched-tokens` | 8K-32K | Throughput vs latency | 32768 (vLLM default) |
| `temperature` | 0.0-0.3 (code) | Determinism vs creativity | 0.1 for audits, 0.3 for docs |
| `top_p` | 0.95 (default) | Nucleus sampling | 0.95 |
| Speculative tokens | 2-5 | Speed vs quality | 3 (validated for DSpark/DFlash/MTP) |
| `--mem-fraction-static` (SGLang) | 0.7-0.9 | Model vs KV cache | 0.85 (NVFP4), 0.78 (BF16) |
| `--max_batch_size` (TRT-LLM) | 1-32 | Concurrency vs latency | 8 (NVFP4), 32 (BF16) |

---

## 9. TROUBLESHOOTING QUICK REFERENCE

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `<thinking>` tags in final output | Reasoning parser missing | Add `--reasoning-parser nemotron_v3` (vLLM) / `nemotron_3` (SGLang) / `nemotron-v3` (TRT-LLM) |
| Tool calls not parsed / malformed | Tool parser mismatch | Verify `--tool-call-parser qwen3_coder` (vLLM/SGLang) / `--tool_parser qwen3_coder` (TRT-LLM) |
| OOM on startup | VRAM insufficient | Reduce `--max-num-seqs`, `--max-model-len`, `--mem-fraction-static` |
| Slow first request (high TTFT) | Cold model load | Keep server warm; pre-load; use `--enable-prefix-caching` |
| Truncated JSON output | Thinking ate token budget | `enable_thinking: false` + raise `max_tokens` |
| Hallucinated imports / wrong APIs | Insufficient context | Provide more surrounding code, imports, project patterns |
| Garbled output with speculative | Draft tokens < block size | Ensure `--speculative_config.num_speculative_tokens` ≥ draft's block size (3 for DSpark) |
| `generation_config` ignored | Model defaults override | Add `--generation-config vllm` |
| Mamba cache misalignment | Hybrid arch cache mismatch | Add `--mamba-cache-mode align` |
| Low acceptance rate (<80%) | Speculative depth too high | Reduce draft tokens; try MTP instead of DSpark/DFlash |

---

## 10. BENCHMARK METHODOLOGY (for Validation)

### 10.1 Dynamo Recipe Benchmarks (Production Standard)
```bash
# Mooncake-format agentic trace: 64K input, 400 output, 90% KV reuse
aiperf profile \
  -m nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4 \
  --custom-dataset-type mooncake_trace \
  --num-requests 3541 \
  --endpoint-type chat \
  --streaming \
  --use-server-token-count \
  --extra-inputs ignore_eos:true \
  --request-timeout-seconds 1200 \
  --url http://<frontend>:8000 \
  --concurrency <target>

# Pass Criteria:
# - tok/s/user >= 50
# - TTFT p50 < 5 seconds
```

### 10.2 HP ZGX Nano Reference (MTP Benchmark)
| Concurrency | k=1 (tok/s) | k=2 (tok/s) | k=3 (tok/s) |
|-------------|-------------|-------------|-------------|
| 1 | ~45 | ~65 | ~75 |
| 4 | ~95 | ~120 | ~135 |
| 8 | ~115 | ~140 | ~150 |
| 16 | ~125 | ~148 | ~155 |
| 32 | ~130 | ~152 | ~156 |
| 64 | ~130 | ~152 | ~156 |

**Acceptance Rates at k=3**: 82-84% across all concurrency levels

---

## 11. VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-21 | Initial consolidation from NVIDIA NIM docs, Dynamo recipes, HF model card, cookbooks, quantization docs, MTP benchmark whitepaper |

---

## 12. RELATED DOCUMENTS (Temple-Grade Separation)

| Document | Purpose | Audience | Location |
|----------|---------|----------|----------|
| **This Document** | Model capabilities, deployment, authoring patterns | Higher-level model authoring guides | `docs/guides/REF-NEMOTRON-3.5-LIGHTNING-CAPABILITIES-v2.0.md` |
| **P1 Task Specification** | Model-agnostic task definitions, acceptance criteria | All models + humans | `docs/specs/P1_TASK_SPECIFICATION.md` |
| **P1 Execution Guide (Nemotron)** | Task + model-specific prompts for Nemotron 3.5 Lightning | Nemotron 3.5 Lightning (executing) | `docs/guides/GUIDE-NEMOTRON-3.5-LIGHTNING-P1-EXECUTION-v1.0.md` |
| **Quick Reference Card** | Minimal flags, prompts, checks for executing model | Nemotron 3.5 Lightning (executing) | `docs/guides/REF-NEMOTRON-3.5-LIGHTNING-P1-QUICK-v1.0.md` |
| **Omega Engine Sovereign Mandates** | Governance constraints (M1, M2, M7, M11, M13, M23, M24, M27, M28) | All agents | `SOVEREIGN_MANDATES.md` |

---

*⬡ OMEGA ⬡ NEMOTRON-3.5-LIGHTNING ⬡ CAPABILITIES-REF ⬡ v2.0 ⬡ 2026-09-21 ⬡ TEMPLE-GRADE ⬡ INDEFINITE-RETENTION ⬡ GROUNDED-IN-NVIDIA-SOURCES*

---

This reference document contains **only** the model knowledge needed to author effective execution guides. It contains **zero** task-specific instructions. When writing an execution guide for Nemotron 3.5 Lightning, you (the higher-level model) consult this document for deployment flags, prompt patterns, context limits, and validation criteria — then write a separate, clean execution guide that contains only what the executing model needs to know.
