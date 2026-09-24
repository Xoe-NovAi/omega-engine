# GSCA Context: Local Multimodal LLM Benchmarking for UI Understanding

## Our Setup

**Hardware (Node 1 - ASUS ExpertBook P1503CVA):**
- CPU: Intel i7-13620H (6 P-cores + 4 E-cores, 10C/16T, no discrete GPU)
- RAM: 1×16GB DDR5-5200 single-channel @ 5200 MT/s (2nd slot empty)
- Storage: NVMe (fast, for model storage)
- OS: Ubuntu 26.04 LTS, Linux 7.0
- **CPU-only inference** — Ollama 0.33.3 with `AllowedCPUs=0-11` + `OLLAMA_NUM_THREADS=8` = 14.4 t/s on phi4-mini

**Models Under Test (all local, Ollama):**
| Model | Size | Quant | Type | Notes |
|-------|------|-------|------|-------|
| Qwen3-VL-4B-Instruct | 2.5 GB | Q4_K_M | Multimodal (VL) | + mmproj F16 (836 MB) |
| Qwen3-4B-Instruct | 2.5 GB | UD-Q4_K_XL | Dense instruct | Unsloth Dynamic |
| Qwen3-4B-Thinking | 2.5 GB | Q4_K_M | Dense reasoning | Dual-mode thinking |
| Qwen3-1.7B (UD-Q4_K_XL) | 1.1 GB | UD-Q4_K_XL | Dense base | Best quality/size |
| Qwen3.5-9B-Harmonic | 5.6 GB | Q4_K_M | Hybrid (DeltaNet+MoE) | 262K context |
| Qwen3.5-4B-super-coder | ~2.6 GB | Q4_0 | Experimental merge | Distilled from Claude |
| Qwen3-Zero-Coder-0.8B | ~0.5 GB | Various | Experimental | NEO Imatrix, draft candidate |

**Goal:** Benchmark local multimodal LLMs on:
1. **UI-to-code generation** (Design2Code: screenshot → HTML/CSS/JS)
2. **Visual layout extraction** (component identification, spacing, hierarchy)
3. **GUI grounding** (element localization, form field identification)
4. **Visual reasoning** (chart analysis, diagram understanding)

**Constraints:**
- CPU-only (no GPU), 16GB RAM single-channel
- Ollama with expert offloading (`--cpu-moe` for MoE models)
- Presence penalty 1.5 to prevent looping on low-bit quants
- Temperature sweep: 0.1, 0.5, 0.7
- Context sweep: 4096, 8192

---

## Questions for GSCA

### 1. Dataset Access & Sampling Strategy
- **Design2Code** (484 pages): Is there a curated subset (e.g., 50 diverse pages) for quick screening vs full eval?
- **WebSight**: How to sample for diversity (e-commerce, dashboards, forms, landing pages) without downloading full dataset?
- **DesignBench**: Does it include modern frameworks (Tailwind, React components) or vanilla HTML/CSS?
- **UI2App**: Are the multi-screen flows annotated with expected navigation logic?

### 2. Evaluation Frameworks for Local Models
- **Design2Code metrics**: What's the standard evaluation pipeline? (HTML structure similarity, CSS property match, visual diff via Playwright?)
- **GUI Grounding (ScreenSpot/ShowUI)**: How to adapt for *generation* eval vs *pointing* eval? We want code output, not click coordinates.
- **WebMMU**: 4,000 pages is heavy for local eval. Is there a validated 100-page subset?

### 3. Prompt Engineering for Local Models
- **Design2Code prompt template**: What's the SOTA prompt for Qwen3-VL? (e.g., "Generate clean, semantic HTML5 + CSS3 matching this design exactly. Use Tailwind CSS. No external dependencies.")
- **Thinking mode for VL**: Should we enable thinking for visual reasoning tasks? Temperature interaction?
- **Few-shot examples**: How many in-context examples fit in 4096/8192 context with image tokens?

### 4. Automated Evaluation Pipeline
- **Visual diff**: Playwright + pixelmatch for rendered output vs reference?
- **Structural similarity**: AST-based HTML comparison (ignoring whitespace/class ordering)?
- **CSS property extraction**: Compare computed styles via headless browser?
- **Component-level scoring**: Header/nav/hero/form/footer — weighted scoring?

### 5. Resource-Constrained Optimization
- **Image token budget**: Qwen3-VL uses ~16 tokens/patch at 448×448. What resolution balances detail vs context for UI screenshots?
- **Batch inference**: Can we pipeline multiple images through Ollama efficiently?
- **Quantization impact**: Q4_K_M vs Q8_0 for visual tasks — any quality cliff?

### 6. Comparative Baselines
- **Proprietary baselines**: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro scores on Design2Code/WebSight?
- **Open-weight baselines**: LLaVA-NeXT, InternVL2, Phi-3-Vision — published scores?
- **Human eval protocol**: Inter-annotator agreement for "code quality" scoring?

---

## What We Can Provide
- Local inference logs (tokens/sec, latency, RAM)
- Model outputs for any prompt/image you specify
- Hardware-specific performance data (CPU-only, single-channel DDR5)
- Quantization comparison (Q4_K_M vs Q5_K_M vs UD-Q4_K_XL)