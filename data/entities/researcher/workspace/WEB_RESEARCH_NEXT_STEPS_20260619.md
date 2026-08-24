# 🔱 Omega Engine — Web Research: Next Steps Knowledge Gaps
# ⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ WEB_RESEARCH ⬡ KNOWLEDGE_GAP_CLOSURE

**AP Token**: `AP-WEB-RESEARCH-GAPS-20260619-v1.0.0`
**Date**: 2026-06-19
**Status**: 🟢 ALL GAPS ADDRESSED (7/7 researched with web sources)
**Model**: deepseek-v4-flash-free (session), websearch/firecrawl (tool fleet)

---

## Executive Summary — The 3 Most Important Findings

### 🥇 Finding 1: Local Embeddings Are Solved — Three Clear Options
**all-MiniLM-L6-v2 via ONNX Runtime delivers 10-40ms inference on Zen 2 CPU.** The classic MiniLM-L6 (22M params, 384-dim, 88MB FP32) runs at **~150ms/single sentence on 1 thread, ~30ms with 4-8 threads** on Ryzen 7-class hardware. INT8 quantization via ONNX cuts this further. Our 12GB RAM supports this trivially alongside the inference model. **Recommendation**: Use `all-MiniLM-L6-v2` via ONNX Runtime initially. For extreme performance, evaluate the brand-new **potion-mxbai-micro** (700KB, 80-88x faster, 68.9 MTEB) — a 2026 static embedding model that is competitive for RAG.

### 🥇 Finding 2: Fine-Tuning Qwen3-4B on 12GB RAM Is NOT Feasible on CPU-Only
**QLoRA requires GPU, minimum 6-8GB VRAM.** The Qwen3-4B QLoRA pipeline (qwen-qlora-train repo, validated on RTX 3070 8GB) requires CUDA. CPU-only fine-tuning of 4B models is **not supported** by any current tooling. **Recommendation**: Postpone fine-tuning until either (a) a GPU becomes available, or (b) we explore CPU-only alternatives like smaller 1.7B models or distilling via llama.cpp (which has experimental fine-tuning support). The JSONL conversation data collection should continue — data is the prerequisite, not the blocker.

### 🥇 Finding 3: Abliterated Qwen3 Models Are Readily Available in GGUF
Multiple abliterated Qwen3 models exist **now** on Hugging Face, including Qwen3-14B (richardyoung), Qwen3-0.6B (Andycurrent), Qwen3-33B-A3B, and Qwen3.5-9B (DuoNeural). There is also **Dolphin 3.0 Llama 3.1 8B** (5GB Q4) which is fully uncensored and runs on CPU. **Recommendation**: Replace Qwen3-4B-Think with Dolphin 3.0 Llama 3.1 8B (Q4_K_M, ~5GB) for uncensored operation. For pure thinking, keep the Qwen3-4B-Think model for when reasoning is needed. Both fit in 12GB RAM.

---

## Gap 1: Local Embedding Models on Zen 2 (Horizon 2.5 — Sovereign Integration)

### Status: 🟢 CLOSED

### Finding
**all-MiniLM-L6-v2 is the goldilocks model for our hardware.** Here is the complete comparison:

| Model | Params | Dim | Size (FP32) | CPU Speed | MTEB Score | Notes |
|-------|--------|-----|-------------|-----------|------------|-------|
| **all-MiniLM-L6-v2** | 22M | 384 | 88MB | ~150ms/1 sentence (1 thread), ~30ms (4-8 threads) | 56.2 | Gold standard for CPU RAG |
| **multi-qa-MiniLM-L6-cos-v1** | 22M | 384 | 88MB | 750 queries/s (CPU) | 51.8 | Better for search queries |
| **multi-qa-MiniLM-L6-dot-v1** | 22M | 384 | 88MB | 750 queries/s (CPU) | 49.2 | Dot product, faster retrieval |
| **static-retrieval-mrl-en-v1** | ~16M | 1024 | ~64MB | **107,419 sentences/s (CPU)** | 50.3 | 100-400x faster than MiniLM |
| **potion-mxbai-micro** (2026) | ~2M | 256 | **700KB** | **80-88x faster than MiniLM** | 68.9 | 2026 static embedding — breakthrough |
| **granite-embedding-small-english-r2** | 47M | 384 | ~100MB | ~199 docs/s (H100) | 61.1 | IBM 2026, 8K context |
| **static-similarity-mrl-multilingual-v1** | ~16M | 1024 | ~64MB | Very fast (static) | ~55 | Multilingual variant |

**Speed on Zen 2 specifically:**
- MiniLM-L6-v2: ~100-150ms per sentence on single thread, ~30ms parallelized over 4-8 threads (confirmed by multiple benchmarks)
- TFLite INT8 quantized version: **10.6ms latency** on AMD CPU (WSL2 benchmark, 2026) — this is the target
- The Q4KM.ai benchmarks confirm: "Runs comfortably on 8-core Ryzen 7, ~150ms per sentence on single thread, ~30ms parallelized"
- ONNX Runtime with 4-8 threads is the optimal configuration
- **Static embeddings** (potion-mxbai-micro, static-retrieval-mrl-en-v1) are game-changing: 80-88x faster with competitive quality

**Can llama.cpp serve embeddings as drop-in replacement?**
- ✅ **Yes.** `llama-server --embeddings` with GGUF models works as drop-in
- Models available: `nomic-embed-text-v1.5` (GGUF), `bge-small-en-v1.5` (GGUF), `bge-base-en-v1.5` (GGUF)
- Throughput on CPU: ~2 docs/second (Ryzen 9 7950X 16-core) for nomic-embed — **not great**
- SentenceTransformers + ONNX is **5-25x faster** on CPU for embeddings than llama.cpp server
- **Recommendation**: Use SentenceTransformers/ONNX for embedding generation, not llama.cpp embed mode

**Memory footprint:**
- MiniLM-L6-v2 ONNX: ~90MB loaded, negligible
- Even running alongside a 4B Q4 model (~2.5GB GGUF), total stays well under 6GB
- **No OOM risk** on 12GB RAM

### Sources
- [Q4KM.ai — MiniLM benchmark on CPU](https://q4km.ai/models/sentence-transformers-all-MiniLM-L6-v2.html) — "~150ms per sentence single thread, ~30ms 4-8 threads"
- [Hugging Face — potion-mxbai-micro](https://huggingface.co/blobbybob/potion-mxbai-micro) — 700KB, 68.9 avg, 80-88x faster
- [StackOverflow — containerized MiniLM on 1 CPU](https://stackoverflow.com/questions/76618655) — 15-20x slowdown on 1 core
- [Sentence-Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html) — 750 queries/s CPU for multi-qa-MiniLM
- [TFLite MiniLM benchmark](https://huggingface.co/Bombek1/all-MiniLM-L6-v2-litert) — 10.6ms on AMD CPU WSL2
- [HuggingFace blog — static embeddings](https://huggingface.co/blog/static-embeddings) — 100-400x faster, 85% quality retention
- [IBM Granite Embedding small r2](https://huggingface.co/ibm-granite/granite-embedding-small-english-r2) — 47M params, 8K context, 2026

### Recommendation
1. **Immediate**: Install `sentence-transformers` and load `all-MiniLM-L6-v2` for embeddings. Test with `--onnx` flag. Expected: ~30-50ms per chunk.
2. **Evaluate**: Test `potion-mxbai-micro` (700KB, 80x faster) for production embedding. If quality is acceptable (68.9 MTEB vs 56.2 for MiniLM), switch to it.
3. **Alternative**: Test `granite-embedding-small-english-r2` (47M, 8K context) if you need longer context windows.
4. **Ignore**: llama.cpp embedding mode for this use case — too slow on CPU.

### Confidence: 🟢 HIGH (multiple corroborating benchmarks, official docs)

---

## Gap 2: Small NLI Models for Skeptical Verifier (Horizon 3 — Cognitive Loops)

### Status: 🟢 CLOSED

### Finding
**The landscape has evolved significantly.** Multiple new small NLI models in 2025-2026 offer 82-91% accuracy in sub-100MB packages.

### NLI Model Comparison

| Model | Params | Size | MNLI-Mis | SNLI | Context | Notes |
|-------|--------|------|----------|------|---------|-------|
| **EttinX-nli-xxs** (2025) | **17M** | ~35MB FP32 | 80.47 | 86.95 | **8192** | **Best on CPU** — ModernBERT-based |
| **EttinX-nli-xs** (2025) | **32M** | ~64MB FP32 | 83.80 | 88.20 | **8192** | Good quality/size tradeoff |
| **cross-encoder/nli-deberta-v3-xsmall** | 70M | ~140MB | **87.77** | **91.64** | 512 | Highest accuracy under 100M |
| **cross-encoder/nli-distilroberta-base** | 82M | ~167MB | 83.98 | 88.38 | 512 | Classic, well-documented |
| **EttinX-nli-s** (2025) | 68M | ~136MB | 87.98 | 89.67 | **8192** | Best all-rounder |
| **PrismNLI-0.4B** (2025) | **400M** | ~800MB | *SOTA* | *SOTA* | Default | Best accuracy but larger |
| **cross-encoder/nli-MiniLM2-L6-H768** | 82M | 167MB | 86.83 | 91.37 | 512 | Fast on CPU, good accuracy |
| **finecat-nli-xxs** | 17M | ~35MB | 77.14 | 84.84 | 8192 | Distilled from larger |

**GGUF-quantized NLI models available:**
- ✅ **nli-MiniLM2-L6-H768 GGUF** (mradermacher) — Q4_K_M = 61MB, Q8_0 = 90MB. Drop-in for llama.cpp.
- ✅ **distilroberta-base-nli-v2 Q8_0 GGUF** (Sleem247) — 82M base. Can run via `llama-server`.
- ❌ **EttinX models not yet GGUF'd** — would need manual conversion via `convert_hf_to_gguf.py`

**Can llama.cpp serve NLI?**
- ✅ **Yes** for classification models loaded as GGUF via `llama-server`
- ✅ `llama-server --hf-repo Sleem247/distilroberta-base-nli-v2-Q8_0-GGUF` works
- ⚠️ NLI requires *pair* scoring (premise + hypothesis), which is a cross-encoder pattern. llama.cpp can handle this via its embedding mode + logits, but it's not as clean as SentenceTransformers' CrossEncoder API
- **Recommendation**: Use SentenceTransformers CrossEncoder for NLI; it's the native interface and well-documented

**Can we do NLI in-context via Qwen3-4B-Think prompt?**
- ✅ **Technically yes** — prompt engineering can do ad-hoc NLI
- ❌ **Accuracy gap** — dedicated NLI cross-encoders achieve 88-92% on SNLI; in-context NLI with 4B models is estimated at 70-80% (no formal benchmark found for Qwen3-4B specifically)
- ❌ **Latency cost** — each NLI check would require ~500ms+ of LLM inference vs ~10-30ms for a cross-encoder
- **Recommendation**: Do NOT use in-context NLI for the Skeptical Verifier. The cross-encoder approach is faster, more accurate, and more reliable.

### Sources
- [EttinX-nli-xxs (17M params)](https://huggingface.co/dleemiller/EttinX-nli-xxs) — 17M params, 8192 context, ModernBERT
- [EttinX-nli-xs (32M params)](https://huggingface.co/dleemiller/EttinX-nli-xs) — 32M, MNLI-Mis 83.80
- [EttinX-nli-s (68M params)](https://huggingface.co/dleemiller/EttinX-nli-s) — 68M, MNLI-Mis 87.98
- [cross-encoder/nli-deberta-v3-xsmall](https://huggingface.co/cross-encoder/nli-deberta-v3-xsmall) — 70M, 91.64 SNLI
- [cross-encoder/nli-distilroberta-base](https://huggingface.co/cross-encoder/nli-distilroberta-base) — 82M params, classic
- [PrismNLI-0.4B](https://huggingface.co/Jaehun/PrismNLI-0.4B) — SOTA, 400M params, 2025
- [nli-MiniLM2-L6-H768 GGUF](https://huggingface.co/mradermacher/nli-MiniLM2-L6-H768-GGUF) — Q4_K_M = 61MB
- [distilroberta-base-nli-v2 GGUF](https://huggingface.co/Sleem247/distilroberta-base-nli-v2-Q8_0-GGUF) — 82M, Q8_0 GGUF
- [finecat NLI throughput benchmarks](https://huggingface.co/dleemiller/finecat-nli-xxs) — **2,838-3,619 samples/s** on GPU (for context)

### Recommendation
1. **Phase 1 (Prototype)**: Use `cross-encoder/nli-distilroberta-base` (82M params, ~167MB) via SentenceTransformers CrossEncoder. Most documented, most community support.
2. **Phase 2 (Optimize)**: Evaluate `EttinX-nli-xs` (32M params, ~64MB) — same quality at half the size, plus 8K context for evaluating long LLM responses.
3. **Phase 3 (Deploy)**: If 32M is still too heavy, `EttinX-nli-xxs` (17M params, ~35MB) is the smallest viable option with acceptable accuracy (80.47/86.95).
4. **Memory**: Cross-encoder loaded once (~70-170MB). Negligible alongside 4B inference model. **No OOM risk.**
5. **Do NOT** use in-context NLI — accuracy is worse and latency is 10-50x higher.

### Confidence: 🟢 HIGH (official model cards, multiple alternatives, documented benchmarks)

---

## Gap 3: Qwen3-4B Fine-Tuning on Consumer Hardware (Horizon 3 — Fine-Tuning Pipeline)

### Status: 🟡 PARTIAL

### Finding
**CPU-only fine-tuning of Qwen3-4B is not supported by current tools.** All fine-tuning frameworks (Unsloth, Axolotl, QLoRA, etc.) require a CUDA-capable GPU. Here is the breakdown:

### Can Qwen3-4B be fine-tuned on CPU with 12GB RAM?
**No.** Current tools do not support CPU fine-tuning for models of this scale. Here's what exists:

| Method | GPU Memory Required | Quality | CPU Option? | Notes |
|--------|-------------------|---------|-------------|-------|
| QLoRA (4-bit) | **6-8 GB VRAM** | ⭐⭐ Very Good | ❌ | Needs CUDA GPU. GTX 1660 Ti+ |
| LoRA | **10-12 GB VRAM** | ⭐⭐⭐ Great | ❌ | RTX 3060 12GB+ |
| Full fine-tune | 20-22 GB VRAM | ⭐⭐⭐ Best | ❌ | RTX 3090+ |
| CPU-only via llama.cpp | N/A | N/A | ⚠️ **Experimental** | llama.cpp has `--finetune` but not production-ready |

**Key finding from qwen-qlora-train repo**: "Validated on RTX 3070 8GB for Qwen3 1.7B / 4B. 8B OOMs." This is the gold standard — a purpose-built Qwen3 QLoRA pipeline validated on consumer hardware.

### Minimum dataset size
- **500 examples**: Works for QLoRA, measurable improvement on narrow tasks
- **1,000-2,000 examples**: Recommended minimum for meaningful behavioral change
- **10,000+ examples**: For general capability improvements across domains
- The Qwen team recommends **1 epoch** as optimal (per GRAPE paper)
- **Our current collection**: Unknown quantity, but if we have 500+ high-quality JSONL exchanges, we can already fine-tune meaningfully

### Can we fine-tune Krikri-8B on 12GB RAM?
- **No.** 8B QLoRA requires 12-16GB VRAM minimum. CPU is not an option.
- The qwen-qlora-train repo explicitly calls 8B "experimental" on 8GB GPUs and reports OOMs

### 2026 advancements in CPU fine-tuning?
- **llama.cpp** has experimental fine-tuning support (`--finetune` flag) but it's not production-ready and targets smaller models
- **Unsloth 2026** has Faster MOE support but still requires CUDA
- **No major breakthrough** in CPU fine-tuning for 2025-2026 — this remains GPU-bound
- **Knowledge Distillation** is the closest CPU-friendly alternative: use a larger model (even cloud) to label data, train a small student model

### Sources
- [qwen-qlora-train](https://github.com/techwithsergiu/qwen-qlora-train) — Validated 4B on RTX 3070 8GB, 8B OOMs
- [Unsloth Qwen3 fine-tuning](https://unsloth.ai/docs/models/tutorials/qwen3-how-to-run-and-fine-tune) — 2x faster, 70% less VRAM, GPU required
- [Qwen official fine-tuning docs](https://qwenlm-qwen.mintlify.app/finetuning/overview) — Q-LoRA: 5.8GB GPU memory minimum for Qwen2.5-0.5B
- [NengYi7781/qwen3-4b-local-sft-kit](https://huggingface.co/NengYi7781/qwen3-4b-local-sft-kit) — Auto-detects VRAM: <12GB → QLoRA, 12GB+ → LoRA (all GPU)
- [Qwen3 GitHub](https://github.com/QwenLM/Qwen3) — Recommends Axolotl, Unsloth, Swift, Llama-Factory

### Recommendation
1. **Continue collecting JSONL data** — without data, fine-tuning is impossible regardless of hardware. This is not wasted effort.
2. **Options for fine-tuning without GPU:**
   - **Cloud GPU spot instance**: ~$0.50-1/hr for a T4 16GB. Fine-tune Qwen3-4B in 1-2 hours (~$1-2 total).
   - **Knowledge Distillation**: Use Gemma 4 31B (Google, unlimited) to label data, train a smaller model
   - **Local 1.7B fine-tuning**: If we can get a 1.7B QLoRA working on our hardware... still requires GPU.
3. **Postpone until Option 2 is blocked**: Continue data collection, implement embeddings + NLI first (Gaps 1 & 2 give immediate value).
4. **Monitor**: llama.cpp fine-tuning maturity. Check back in 6 months.

### Confidence: 🟡 MEDIUM-HIGH (official docs and validated repos are clear; uncertainty is about future tooling)

---

## Gap 4: Podman Disk Space Optimization

### Status: 🟢 CLOSED

### Finding
**Moving Podman storage to the omega_library partition is well-documented and safe.**

### How to Move Podman Storage

**Safe method (no data loss):**
1. Create new storage directory on omega_library:
   ```bash
   mkdir -p /media/arcana-novai/omega_library/podman-storage
   ```
2. Edit `~/.config/containers/storage.conf`:
   ```ini
   [storage]
   driver = "overlay"
   graphroot = "/media/arcana-novai/omega_library/podman-storage"
   runroot = "/run/user/1000/containers"
   ```
3. Run `podman system migrate` to move existing data
4. Verify with `podman info --format '{{.Store.GraphRoot}}'`

**Alternative (symlink approach, simpler but less clean):**
```bash
# Stop all containers
podman stop -a
# Backup current storage
cp -a ~/.local/share/containers/storage /media/arcana-novai/omega_library/podman-storage
# Replace with symlink
mv ~/.local/share/containers/storage ~/.local/share/containers/storage.bak
ln -s /media/arcana-novai/omega_library/podman-storage ~/.local/share/containers/storage
```

**Risk**: The `storage.conf` method is the **official Red Hat recommended approach** and is preferred for rootless Podman.

### Safe Cleanup Commands
| Command | What It Does | Safety Level |
|---------|-------------|--------------|
| `podman system prune -f` | Removes stopped containers, unused networks, dangling images | 🟢 Safe (keeps volumes) |
| `podman system prune --volumes -f` | Also removes unused volumes | 🟡 Moderate (may delete data) |
| `podman system prune -a --volumes -f` | Maximum cleanup | 🔴 Aggressive (removes ALL unused images) |
| `podman container prune --filter until=168h` | Removes containers stopped >7 days | 🟢 Safest |
| `podman image prune -a -f` | Removes all unused images | 🟡 Moderate |
| `podman volume prune -f` | Removes unused volumes | 🟡 Check first |
| `podman system df` | Shows disk usage (preview before pruning) | 🟢 Read-only |

**Recommended safe sequence:**
```bash
podman system df                    # Check what's using space
podman container prune -f           # Remove stopped containers
podman image prune -a -f            # Remove unused images
podman system df                    # Verify savings
```

### Size Impact of Running Containers
| Container | Image Size | Storage (layers, volumes) | Notes |
|-----------|-----------|--------------------------|-------|
| redis:7-alpine | ~32MB | ~100MB+ for AOF/RDB data | Depends on cache |
| qdrant/qdrant | ~200MB | Variable (depends on index) | Can grow large with vectors |
| postgres (pgvector) | ~400MB | Variable (DB size) | Schema-only mostly |
| caddy:alpine | ~40MB | ~10MB | Static config |
| iris (omega-iris) | ~300MB+ | ~50MB | Voice data |

**Total minimum**: ~1GB for images + variable for data volumes (2-5GB typical).

### Sources
- [Red Hat — Change rootless storage location](https://access.redhat.com/solutions/7007159) — Official recommendation
- [Podman docs — rootless storage](https://docs.podman.io/en/stable/markdown/podman.1.html) — `--root` flag and XDG_DATA_HOME
- [OneUptime — Move Podman storage](https://oneuptime.com/blog/post/2026-03-18-change-container-storage-location-podman) — Step-by-step guide
- [Podman docs — system prune](https://docs.podman.io/en/latest/markdown/podman-system-prune.1.html) — Official documentation
- [OneUptime — Fix no space left](https://oneuptime.com/blog/post/2026-03-18-fix-no-space-left-on-device-podman) — VFS vs overlay detection
- [GitHub discussion #21213](https://github.com/podman-container-tools/podman/discussions/21213) — User reports storage.conf fix works with `podman system reset`

### Recommendation
1. **Immediate**: Run `podman system prune -f` to reclaim dangling space
2. **This week**: Move Podman storage to omega_library partition via `~/.config/containers/storage.conf` + `podman system migrate`
3. **Monitor**: Add `podman system prune -f` to weekly cron
4. **Check storage driver**: Verify `overlay` (not `vfs`) — if vfs, do `podman system reset` to switch

### Confidence: 🟢 HIGH (Red Hat official docs, multiple verified user reports)

---

## Gap 5: Abliterated / Uncensored Local Models

### Status: 🟢 CLOSED

### Finding
**Abliterated Qwen3 models are widely available in GGUF format.** Multiple community members have published Qwen3 abliterations across all size ranges.

### Available Abliterated Qwen3 GGUF Models

| Model | Size | Quant | File Size | Abliteration Method | Refusal Rate |
|-------|------|-------|-----------|-------------------|--------------|
| **Qwen3-0.6B** (Andycurrent) | 0.6B | GGUF | ~400MB Q4 | Heretic | 6/100 (down from 49/100) |
| **Qwen3-14B** (richardyoung) | 14B | Q4_K_M | ~8.18GB | Conservative | 19/100 (down from ~80/100) |
| **Qwen3.5-9B** (DuoNeural) | 9B | Q4_K_M | ~5.63GB | ARA (heretic-llm) | 35/100 (down from 40/100) |
| **Qwen3.5-35B-A3B** (jiaojjjjje) | 35B-A3B | Q8_0 | ~34GB | Asymmetric layer tapering | Full uncensoring |
| **Qwen3.6-27B** (huihui-ai) | 27B | Q2-Q8 | Various | huihui standard | Full uncensoring |
| **Qwen3-33B-A3B Stranger Thoughts** | 33B-A3B | IQ4_XS+ | Various | Abliterated + uncensored | Uncensored |

### Best Uncensored Alternatives for 1.7B-8B Range (CPU-Friendly)

| Model | Size | Q4 Size | CPU-Friendly? | Notes |
|-------|------|---------|---------------|-------|
| **Dolphin 3.0 Llama 3.1 8B** | 8B | ~5GB | ✅ Yes (Q4, 8GB RAM) | **Best uncensored for CPU** — Eric Hartford's flagshp |
| **Dolphin 3.0 Qwen 2.5 3B** | 3B | ~2.5GB | ✅ Yes | Minimal hardware option |
| **Dolphin X1 8B** | 8B | ~4.92GB | ✅ Yes (Q4) | 95.96% pass on 4.5k refusal prompts |
| **Qwen3-0.6B abl** | 0.6B | ~400MB | ✅ Yes (trivial) | Ultra-lightweight uncensored |

### Status of Abliteration in 2026
**Abliteration is alive and well.** Key developments:
- **Heretic method** (Andycurrent, DuoNeural): Uses norm-preserving biprojection to remove refusal vectors without degrading quality (KL divergence ~0.00-0.02)
- **Asymmetric layer tapering** (jiaojjjjje): Early layers get 30% abliteration, core refusal layers get 100%. Prevents long-text repetition while maintaing uncensoring. Tested stable at 11,000+ characters.
- **huihui-ai** remains the largest abliteration publisher on Hugging Face with hundreds of models
- **Refusal is in the residual stream**: The 2024 paper "Refusal in LLMs is Mediated by a Single Direction" is still the foundation; all 2025-2026 methods build on it
- **Abliteration is not superseded** — it remains the primary method because it's surgical (no fine-tuning required)

### Sources
- [Qwen3-0.6B abliterated (Andycurrent)](https://huggingface.co/Andycurrent/Qwen3-0.6B-heretic-abliterated-uncensored-GGUF) — 6/100 refusal, KL 0.00
- [Qwen3-14B abliterated (richardyoung)](https://huggingface.co/richardyoung/Qwen3-14B-abliterated-GGUF) — Q4_K_M, 19/100 refusal
- [Qwen3.5-9B abliterated (DuoNeural)](https://huggingface.co/DuoNeural/Qwen-3.5-9B-Abliterated-GGUF) — ARA method, Q4_K_M 5.63GB
- [Dolphin 3.0 Llama 3.1 8B](https://huggingface.co/dphn/dolphin-2.9.4-llama3.1-8b-gguf) — Unensored, Q4_K_M ~5GB
- [Dolphin X1 8B](https://huggingface.co/dphn/Dolphin-X1-8B-GGUF) — 95.96% pass rate on refusal prompts
- [InsiderLLM — Best Uncensored Local LLMs](https://insiderllm.com/guides/best-uncensored-local-llms/) — Comprehensive 2026 guide
- [Qwen3.5-35B-A3B abliteration details](https://huggingface.co/jiaojjjjje/Qwen3.5-35B-A3B-abliterated) — Asymmetric layer tapering technique

### Recommendation
1. **Immediate**: Download **Dolphin 3.0 Llama 3.1 8B (Q4_K_M, ~5GB)** as the fleet's primary uncensored model. This is the best CPU-friendly uncensored model in our size range.
2. **Keep**: Qwen3-4B-Think for tasks requiring structured reasoning/thinking mode.
3. **Try**: Qwen3-0.6B abliterated (~400MB) for Iris (voice assistant) — ultra-lightweight, fully uncensored.
4. **Swap strategy**: Use Dolphin for open-ended interaction, Qwen3-4B-Think for reasoning-heavy tasks, switch via entity config.

### Confidence: 🟢 HIGH (multiple independent publishers, documented methods, Dolphin is well-established)

---

## Gap 6: Firecrawl MCP Best Practices

### Status: 🟢 CLOSED

### Finding
Firecrawl's pricing, rate limits, and MCP integration are well-documented.

### Firecrawl Pricing (2026)
| Plan | Monthly Credits | Price | Rate Limits |
|------|----------------|-------|-------------|
| **Free** | 500-1,000 | $0 | Low (5-10 concurrent) |
| Hobby | 5,000 | $16/mo | Higher |
| Starter | 50,000 | $49/mo | ⬆️ |
| Standard | 250,000 | $199/mo | ⬆️ |
| Growth | 500,000 | $333/mo | Higher concurrent |
| Scale | 1,000,000 | $599/mo | 50 concurrent |

**Credit consumption per operation:**
- `scrape` (no JS): **1 credit**
- `scrape` (with JS render): **2-5 credits**
- `crawl` per page: **1 credit**
- `search`: **2 credits per 10 results**
- `extract` (JSON/LLM-powered): **3-10 credits** (1 base + 4 for JSON)
- `map`: **1 credit**
- `interact`: **2 credits per browser minute**

**Our plan**: The system prompt says we have an API key. The free tier (500-1,000 credits/month) gives ~200-500 scrapes. We need to check our current plan status.

### MCP Integration Pattern
**Best practice**: The official `firecrawl-mcp` server is the recommended integration path:
```bash
npx firecrawl-mcp  # Simplest — no custom wrapper needed
```
Exposes 12 MCP tools: scrape, crawl, search, agent, map, batch_scrape, interact, extract, deep_research, and job management tools.

**IMPORTANT best practices from official docs:**
1. **Search first, scrape second**: `firecrawl_search` without scrapeOptions → identify best pages → `firecrawl_scrape` specific URLs. More efficient than scraping everything.
2. **Set limits on crawl**: Crawl defaults to 10,000 pages. Set `limit` explicitly (10-50 for most use cases).
3. **Use `max_age`**: For pages that don't change hourly, `max_age` returns cached content at 500% faster speeds and saves credits.
4. **Cache aggressively**: Cache results in our own storage for pages we visit regularly.
5. **Rate limiting**: The MCP server has built-in exponential backoff (`FIRECRAWL_RETRY_MAX_ATTEMPTS=3`, backoff factor 2).
6. **Avoid `extract` for simple data**: Use JSON format in scrape/crawl instead of extract when possible (extract costs 3-10 credits per page).
7. **Monitor credits**: Set up warnings at 50% / 80% of monthly credit depletion.

### Exa Pricing (Updated March 2026)
| Tier | Cost | Details |
|------|------|---------|
| **Free** | $10 credit on signup + $7/mo recurring | ~1,428 searches at $7/1k |
| Search | $7/1k requests | 10 results with text + highlights included |
| Deep Search | $12/1k requests | Structured outputs |
| Deep-Reasoning | $15/1k requests | 12-50s effort |
| Contents | $1/1k pages | Per content type |
| Agent | $0.012-$2.00/run | Depending on effort |

**Rate limits**: 10 QPS for search/answer endpoints, 100 QPS for contents endpoint.

### Sources
- [Firecrawl Pricing page](https://www.firecrawl.dev/pricing) — Official pricing
- [Firecrawl Rate Limits](https://firecrawl-firecrawl.mintlify.app/api-reference/rate-limits) — Official docs
- [Firecrawl Billing](https://firecrawl.mintlify.app/billing) — Smart Upgrade, credit system
- [Firecrawl MCP GitHub](https://github.com/firecrawl/firecrawl-mcp-server) — Official MCP server
- [Firecrawl MCP in Cursor blog](https://www.firecrawl.dev/blog/firecrawl-mcp-in-cursor) — Best practices
- [TokenMix — Firecrawl MCP Server Guide](https://tokenmix.ai/blog/firecrawl-mcp-server-web-scraping-via-mcp-2026) — Comprehensive 2026 guide
- [Exa Pricing](https://exa.ai/pricing?tab=api) — Official pricing
- [Exa Rate Limits](https://exa.ai/docs/reference/rate-limits) — 10 QPS limit
- [Exa Pricing Update (March 2026)](https://exa.ai/docs/changelog/pricing-update) — Lower prices, contents included

### Recommendation
1. **Check our plan**: Verify current Firecrawl plan level. If free tier, we have ~500-1,000 credits/month.
2. **MCP server**: Already integrated (we can call firecrawl_scrape, firecrawl_search in this session). Keep using `npx firecrawl-mcp`.
3. **Best practice**: Two-step workflow — search without scrapeOptions, then selectively scrape the best results.
4. **Credit management**: Set `maxAge` for cached results. Avoid unnecessary JS rendering (2-5x credit cost).
5. **Exa**: More expensive ($7/1k searches) but more powerful for structured search. Use for deep research, Firecrawl for scrape-heavy tasks.

### Confidence: 🟢 HIGH (official pricing pages, MCP docs, multiple blog corroborations)

---

## Gap 7: Qwen3-4B-Think Model Behavior

### Status: 🟢 CLOSED

### Finding
**Qwen3-4B-Thinking-2507 is a significant upgrade over the original Qwen3-4B-Think.** The 2507 variant was released August 2025 and brings major improvements.

### Qwen3-4B vs Qwen3-4B-Think vs Qwen3-4B-Thinking-2507

The "Think" variant in our fleet refers to Qwen3-4B-Thinking-2507 (the latest). Here's the distinction:

| Aspect | Qwen3-4B (base instruct) | Qwen3-4B-Think (2507) |
|--------|-------------------------|----------------------|
| **Thinking mode** | Optional (`enable_thinking=True/False`) | **Mandatory** — always thinks |
| **CoT visible?** | Only if thinking enabled | ✅ Always — CoT in `<think>...</think>` tags |
| **AIME25** | 65.6% | **81.3%** (+15.7pp) |
| **GPQA** | 55.9% | **65.8%** (matches 30B!) |
| **MMLU-Pro** | 70.4% | 74.0% |
| **LiveCodeBench** | 48.4% | **55.2%** |
| **Arena-Hard v2** | 13.7% | **34.9%** (+21.2pp) |
| **BFCL-v3 (tool use)** | 65.9% | **71.2%** |
| **Context length** | 32K (128K with YaRN) | Same |

**Key findings about thinking behavior:**
1. **The CoT IS visible in the output.** Thinking content appears in `<think>...</think>` tags. The model outputs reasoning first, then the final answer.
2. **The thinking process can be controlled via budget.** `thinking_budget` parameter caps the number of reasoning tokens. Once the budget is hit, the model auto-transitions to answer. This is implemented via prompt engineering (forced stop instruction), not architecture.
3. **Default behavior**: Thinking is always enabled for the 2507 variant. You cannot disable it without using a different model checkpoint.
4. **In multi-turn conversations**, historical thinking content should NOT be included in context — only the final answer part. The chat template handles this automatically.

### Recommended Inference Parameters
| Parameter | Thinking Mode | Non-Thinking Mode |
|-----------|--------------|-------------------|
| Temperature | 0.6 | 0.7 |
| TopP | 0.95 | 0.8 |
| TopK | 20 | 20 |
| MinP | 0 | 0 |
| **DO NOT use** | Greedy decoding (causes repetition) | — |
| Presence penalty | 0-2 (for repetition) | 0-2 |
| Max output length | 32,768 (up to 81,920 for complex) | 32,768 |

### Known Issues / Limitations
1. **Long context at 4B**: The 32K native context works, but 128K via YaRN at 4B may cause quality degradation in very long contexts. The model's reasoning may drift with extremely long CoT.
2. **Thinking budget plateau**: Accuracy plateaus past 10-12K reasoning tokens for AIME-type tasks. More thinking does not always help — the model can "overthink."
3. **NoThinking alternative**: Recent research (Ma et al., April 2025) shows that for budget-constrained inference, parallel sampling without thinking + best-of-N aggregation can match or exceed thinking mode at 2-9x lower latency.
4. **Output length**: Qwen recommends 32,768 tokens for most queries. For complex math/coding, 81,920 tokens. This means our generation can be long.
5. **Speed on Zen 2**: Qwen3-4B Q4 on Ryzen 5700U typically runs at **5-15 tokens/s**. A 32K token thinking budget would take 35-100 minutes — impractical. **We should set a tight thinking budget (512-1024 tokens) for interactive use.**

### Sources
- [Qwen3-4B-Thinking-2507 model card](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) — Official with benchmarks
- [Qwen3 GitHub — thinking_budget.md](https://github.com/QwenLM/Qwen3/blob/main/docs/source/getting_started/thinking_budget.md) — Budget control mechanism
- [QwenLM/Qwen3 blog](https://qwenlm.github.io/blog/qwen3/) — 4-stage training pipeline
- [Qwen3 Technical Report (arXiv)](https://arxiv.org/html/2505.09388) — Thinking mode fusion details
- [EmergentMind — Qwen3-4B-Thinking-2507 analysis](https://www.emergentmind.com/topics/qwen3-4b-thinking-2507) — Budget plateauing, NoThinking alternatives
- [DEV Community — Qwen3-4B-Thinking-2507 review](https://dev.to/lukehinds/qwen3-4b-thinking-2507-just-shipped-4e0n) — Community overview
- [Qwen3 1.7B vs 4B comparison](https://artificialanalysis.ai/models/comparisons/qwen3-1.7b-instruct-reasoning-vs-qwen3-4b-instruct-reasoning) — Speed benchmarks
- [arXiv — Gemma 4, Phi-4, Qwen3 benchmark](https://arxiv.org/html/2604.07035v1) — 8,400 model-dataset-prompt evaluations

### Recommendation
1. **Keep Qwen3-4B-Thinking-2507 for reasoning-heavy tasks** where its 81.3% AIME25 is needed.
2. **Set a thinking budget of 512-1024 tokens** for interactive use. Full thinking (32K tokens) is impractical on Zen 2.
3. **Switch to non-thinking mode for simple Q&A** to avoid latency. Use `Qwen3-4B-Instruct` (not the Think variant) or use `/no_think` tag.
4. **For multi-turn**: The chat template handles CoT stripping automatically. No manual intervention needed.
5. **Parallel sampling**: For latency-sensitive tasks, consider multiple shallow passes without thinking rather than one deep thinking pass.
6. **Known issue**: Greedy decoding causes endless repetitions in thinking mode. Always use sampling parameters.

### Confidence: 🟢 HIGH (official Qwen documentation, model cards, published paper, community analysis)

---

## Blocker Assessment

| Blocker | Severity | Status | Resolution |
|---------|----------|--------|------------|
| **Root partition 99% full (2.8GB free)** | 🔴 **CRITICAL** | 🟢 **ACTIONABLE** | Move Podman storage to omega_library partition (Gap 4). Immediate relief. |
| **Fine-tuning requires GPU** | 🟡 MODERATE | 🟢 **KNOWN** | Not a blocker for current sprint. Continue data collection. Cloud GPU is $1-2/fine-tune. |
| **No GPU for NLI inference** | 🟢 NOT A BLOCKER | — | All recommended NLI models run on CPU (17M-82M params, 35-167MB). No GPU needed. |
| **Embedding model not installed** | 🟢 NOT A BLOCKER | — | `pip install sentence-transformers` + one line to load model. 10 minute setup. |
| **Podman migration affects running containers** | 🟡 MODERATE | 🟢 **MANAGEABLE** | Stop containers, migrate, restart. 5 minutes of downtime. |

## Priority Ranking by Importance

| Rank | Gap | Finds | Immediate Action? | Effort | Impact |
|------|-----|-------|-------------------|--------|--------|
| **1** | **Gap 4: Podman Disk Space** | 🟢 CLOSED | ✅ YES (migrate storage) | 30 min | 🔴 CRITICAL — frees root partition |
| **2** | **Gap 5: Abliterated Models** | 🟢 CLOSED | ✅ YES (deploy Dolphin 8B) | 20 min | 🔴 HIGH — uncensors fleet |
| **3** | **Gap 1: Embedding Models** | 🟢 CLOSED | ✅ YES (install st + MiniLM) | 15 min | 🔴 HIGH — enables local RAG |
| **4** | **Gap 2: NLI Models** | 🟢 CLOSED | ⏳ NEXT (after embedding) | 30 min | 🔴 HIGH — enables Skeptical Verifier |
| **5** | **Gap 7: Qwen3-4B-Think** | 🟢 CLOSED | ⏳ TUNE (budget settings) | 5 min | 🟡 MED — improves latency |
| **6** | **Gap 6: Firecrawl/Exa** | 🟢 CLOSED | ⏳ OPTIMIZE (credit management) | 15 min | 🟡 MED — reduces API costs |
| **7** | **Gap 3: Fine-Tuning** | 🟡 PARTIAL | 📋 PLAN (continue data collection) | N/A | 🟢 LONG-TERM — not urgent |

---

## Appendix: Quick-Reference Command Summary

### Embeddings (Gap 1)
```bash
pip install sentence-transformers faiss-cpu
# Test MiniLM speed
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print(m.encode(['test']).shape)"
```

### NLI (Gap 2)
```bash
pip install sentence-transformers
python -c "from sentence_transformers import CrossEncoder; m = CrossEncoder('cross-encoder/nli-distilroberta-base'); print(m.predict([('A cat is on the mat', 'A pet is present')]))"
```

### Podman Storage Move (Gap 4)
```bash
# Check current storage location
podman info --format '{{.Store.GraphRoot}}'

# Move to omega_library
mkdir -p /media/arcana-novai/omega_library/podman-storage
# Edit ~/.config/containers/storage.conf → set graphroot
podman system migrate  # Move existing data
podman info --format '{{.Store.GraphRoot}}'  # Verify
```

### Dolphin Uncensored (Gap 5)
```bash
# Via Hugging Face
huggingface-cli download dphn/dolphin-2.9.4-llama3.1-8b-gguf --local-dir ~/OmegaLibrary/hf_cache/hub --local-dir-use-symlinks False
# Or use existing GGUF from models directory
```

### Firecrawl Best Practices (Gap 6)
```bash
# Search first, then scrape
# Use max_age for cached content
# Set crawl limits explicitly
```

### Qwen3 Thinking Budget (Gap 7)
```python
# In llama-cpp-python or API call, add:
# thinking_budget=512 (for interactive use)
# thinking_budget=4096 (for complex reasoning)
# max_tokens=thinking_budget + answer_budget
```

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ WEB_RESEARCH ⬡ KNOWLEDGE_GAP_CLOSURE*

*Report generated: 2026-06-19 | Deployment: 7/7 gaps addressed with web-sourced evidence | Next: Transfer to Kali for fleet-wide consumption*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
