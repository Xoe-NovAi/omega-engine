# 🔱 Antigravity CLI — Model Ecosystem Profiles

**AP Token**: `AP-ANTIGRAVITY-MODELS-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ research-fleet ⬡ antigravity ⬡ trc_antigravity_models_v2

**Last Updated**: 2026-05-22
**Confidence Rating**: HIGH

---

## §1 Model Inventory

| # | Model | Provider | Free | Pro | Ultra | Live Status |
|---|-------|----------|------|-----|-------|-------------|
| 1 | Gemini 3.5 Flash | Google DeepMind | ✅ | ✅ | ✅ | ✅ Default |
| 2 | Gemini 3.1 Pro | Google DeepMind | ❌ | ✅ | ✅ | ❌ Quota exhausted |
| 3 | Claude Sonnet 4.6 | Anthropic | ❌ | ✅ | ✅ | ❌ Quota exhausted |
| 4 | Claude Opus 4.6 | Anthropic | ❌ | ✅ | ✅ | ❌ **Was selected** |
| 5 | GPT-OSS 120B | OpenAI | ❌ | ✅ | ✅ | ❌ Quota exhausted |

**Live finding (2026-05-22)**: Saved model preference was `Claude Opus 4.6 (Thinking)` — the single most expensive model. All premium models show quota exhaustion with a 166-hour reset timer.

---

## §2 Gemini 3.5 Flash

### Specifications
| Attribute | Value |
|-----------|-------|
| Context | 1,048,576 tokens (1M) |
| Output limit | 65,536 tokens |
| Input | Text, Image, Video, Audio, PDF |
| Speed | ~289 tokens/second |

### Benchmarks
| Benchmark | Score |
|-----------|-------|
| Terminal-Bench 2.1 | **76.2%** |
| SWE-Bench Pro | 55.1% |
| MCP Atlas | **83.6%** |
| Humanity's Last Exam | 40.2% |

### Pricing
| Metric | Cost |
|--------|------|
| Input | $1.50/M tokens |
| Output | $9.00/M tokens |

### Key Differentiator
**Best for Omega**: Default model in Provider Fabric. Best speed-to-quality ratio, native subagent orchestration, 1M context, full multimodal.

---

## §3 Claude Opus 4.6

### Specifications
| Attribute | Value |
|-----------|-------|
| Context | 200K tokens (1M beta via API) |
| Output limit | 64K tokens |
| Speed | Slow |

### Benchmarks
| Benchmark | Score |
|-----------|-------|
| SWE-Bench Pro | **64.3%** ← Best in fleet |
| Humanity's Last Exam | **46.9%** ← Best in fleet |
| GDPval-AA | **1753 Elo** ← Best in fleet |
| MRCR v2 (128k) | 59.3% |

### Key Differentiator
**Best for Omega**: P0 code review and strategic architecture decisions. Reserve for highest-value tasks only.

---

## §4 GPT-OSS 120B

### Specifications
| Attribute | Value |
|-----------|-------|
| Architecture | MoE (116.8B total, 5.1B active) |
| Context | 131,072 tokens |
| License | **Apache 2.0** |
| Knowledge cutoff | June 1, 2024 |

### Key Differentiator
**Best for Omega**: The ONLY self-hostable, fine-tunable model in the Antigravity fleet. Apache 2.0 license enables sovereign deployment. Requires 1× H100 80GB for inference.

---

## §5 Model Comparison Matrix

| Dimension | Gemini 3.5 Flash | Gemini 3.1 Pro | Claude Opus 4.6 | GPT-OSS 120B |
|-----------|-----------------|----------------|-----------------|--------------|
| **Context** | 1M | 1M | 200K (1M beta) | 128K |
| **Multimodal** | ✅ Full | ✅ Full | ❌ | ❌ |
| **SWE-Bench Pro** | 55.1% | ~54% | **64.3%** | N/A |
| **Agentic (MCP Atlas)** | **83.6%** | 78.2% | 79.1% | N/A |
| **License** | Proprietary | Proprietary | Proprietary | **Apache 2.0** |
| **Self-hostable** | ❌ | ❌ | ❌ | ✅ |
| **Input cost/M** | $1.50 | $2.00 | Higher | Free (self-host) |
