# Prompt Compression / Context Distillation Techniques
## SOTA Research — 2025-2026 Frontier

**AP Token**: `AP-PROMPT-COMPRESSION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_prompt_compression ⬡ ACTIVE
**Date**: 2026-08-19

---

## Executive Summary

This document surveys the 2025-2026 state of the art in **prompt compression** and **context distillation** — techniques that reduce token count while preserving downstream task quality. The frontier has four canonical approaches: **LLMLingua** (token-level perplexity filtering), **RECOMP** (RAG-specific context compression), **AutoCompressors** (learned soft-prompt compression), and **Selective Context** (sentence-level relevance filtering). A fifth orthogonal strategy, **Context Distillation**, trains models to internalize prompt knowledge. Critical finding: **Compression ratios of 2-100× with 60-99% quality retention** depending on technique and workload.

---

## 1. Four Canonical Compression Techniques (AI Prompts Hub, 2026-06-08)
> **Source**: [Prompt Compression in 2026: LLMLingua, RECOMP, AutoCompressors, Selective Context Compared](https://aipromptshub.co/blog/prompt-compression-techniques-llmlingua-recomp)

| Technique | Compression Ratio | Quality Retention | Best Workload |
|-----------|-------------------|-------------------|---------------|
| **LLMLingua** (token-level) | 2–20× | 90–99% at 4× | Verbose prompts, long RAG context |
| **RECOMP** (RAG-specific) | 5–25× on retrieved context | 80–98% | RAG with long retrieval |
| **AutoCompressors** (learned) | 30–100× | 60–85% at 30× | High-volume static workloads |
| **Selective Context** (sentence-level) | 3–10× | 92–99% at 3–5× | Quality-critical workflows |
| Naive truncation (baseline) | Any | Highly variable, often catastrophic | Not recommended |

**Key insight**: "Long prompts cost 20-50× more per query than necessary. Compression techniques cut input tokens 60-80% while preserving most output quality."

---

## 2. LLMLingua Family (Microsoft Research, 2023-2024)

### 2.1 LLMLingua (Jiang et al., 2023)
> **Sources**: 
> - [LLMLingua Project](https://www.microsoft.com/en-us/research/project/llmlingua/)
> - [arXiv:2310.05736](https://arxiv.org/abs/2310.05736)
> - [LLMLingua Website](https://llmlingua.com/llmlingua.html)

**Mechanism**: Coarse-to-fine prompt compression using perplexity-based token importance scoring. Uses a small LM (e.g., GPT-2, LLaMA-7B) to compute token-level perplexity, removes low-importance tokens.

**Achievement**: **20× compression ratio** with minimal performance loss.

**GitHub**: https://github.com/microsoft/LLMLingua

### 2.2 LongLLMLingua (Jiang et al., 2024)
> **Sources**: 
> - [LongLLMLingua Website](https://llmlingua.com/longllmlingua.html)
> - [ACL 2024 Paper](https://aclanthology.org/2024.acl-long.91/)

**Enhancements for long context**:
1. **Question-aware coarse-to-fine compression**
2. **Document reordering mechanism** (addresses "lost in the middle")
3. **Dynamic compression ratios** per document
4. **Subsequence recovery strategy** (preserves key info)

**Results**:
- NaturalQuestions: **21.4% performance boost** with **4× fewer tokens** (GPT-3.5-Turbo)
- LooGLE: **94.0% cost reduction**
- 10K token prompts at 2×–6× compression: **1.4×–2.6× latency acceleration**

> "LongLLMLingua not only enhances performance but also significantly reduces costs and latency."

### 2.3 LLMLingua-2 (Data Distillation)
> **Source**: [Microsoft Research LLMLingua-2](https://www.microsoft.com/en-us/research/project/llmlingua/)

**Innovation**: Small BERT-level encoder trained via data distillation from GPT-4 for token classification. **Task-agnostic compression** — no need for target LLM at compression time.

**Advantages**:
- 3×–6× faster than LLMLingua
- Better out-of-domain handling
- No target LLM calls during compression

---

## 3. RECOMP — RAG-Specific Compression (Princeton NLP, 2023)
> **Sources**: 
> - [arXiv:2310.04408](https://arxiv.org/abs/2310.04408)
> - [RECOMP GitHub](https://github.com/carriex/recomp)

**Mechanism**: Compresses retrieved context specifically for RAG. Two variants:
- **Extractive**: Selects relevant sentences from retrieved docs
- **Abstractive**: Generates summary of retrieved context

**Performance**: 5–25× compression of retrieved context at 80–98% quality retention.

**Best for**: RAG-heavy workflows where retrieval context dominates prompt length.

---

## 4. AutoCompressors — Learned Soft-Prompt Compression (Chevalier et al., 2023)
> **Sources**: 
> - [arXiv:2305.14788](https://arxiv.org/abs/2305.14788)
> - [GitHub: mrxmoex/llm-prompt-compression-techniques](https://github.com/mrxmoex/llm-prompt-compression-techniques/blob/main/articles/autocompressor.md)

**Mechanism**: Adapts LLMs to compress lengthy contexts into concise **summary vectors (soft prompts)**. Not human-readable text — learned continuous embeddings.

**Process**:
1. Recursive processing: Handles ultra-long contexts by breaking into segments (up to 30,720 tokens)
2. Iterative compression: Compresses sub-prompts through multiple iterations
3. Soft prompt generation: Uses summary vectors as soft prompts for downstream tasks
4. Unsupervised learning: Works without labeled training data

**Performance**: 30–100× compression. 50 tokens of summary embeddings encode 5,000+ tokens of source text. **Quality retention: 60–85% at 30× compression**.

**Trade-off**: Requires custom fine-tuning of LLM to learn compression. Higher upfront cost; lower per-query cost at scale. **Best for high-volume static workloads**.

---

## 5. Selective Context — Sentence-Level Filtering (Li et al., 2023)
> **Sources**: 
> - [arXiv:2310.06201](https://arxiv.org/abs/2310.06201)
> - [Selective Context GitHub](https://github.com/liyucheng09/Selective_Context)

**Mechanic**: Scoring model evaluates each sentence for relevance to task. Low-relevance sentences dropped. Higher granularity than token-level, more targeted than abstractive summarization.

**Performance**: 3–10× compression typical. **92–99% retention at 3–5× compression**. More predictable quality preservation than aggressive techniques.

**Installation**:
```bash
pip install selective-context
python -m spacy download en_core_web_sm

from selective_context import SelectiveContext
sc = SelectiveContext()
compressed = sc.compress(prompt, context, ratio=0.3)  # 30% of original
```

**Best for**: Workflows needing predictable quality — high-stakes individual queries where 99% retention matters more than maximum compression.

---

## 6. Context Distillation — Orthogonal Strategy (Neel Mishra, 2026)
> **Source**: [Prompt Compression: LLMLingua, Context Distillation](https://neelmishra.github.io/blog/mlops/prompt-engineering/prompt-compression.html)

**Concept**: Instead of pruning tokens at inference time, train a model (or soft prompts) to **internalize** knowledge that would otherwise live in the prompt.

### 6.1 Knowledge Distillation Variant
```python
def distill_context(teacher_name: str, student_name: str, system_prompt: str, train_queries: list):
    # Step 1: Generate teacher outputs WITH full system prompt
    teacher_tok = AutoTokenizer.from_pretrained(teacher_name)
    teacher = AutoModelForCausalLM.from_pretrained(teacher_name)
    student_tok = AutoTokenizer.from_pretrained(student_name)
    student = AutoModelForCausalLM.from_pretrained(student_name)
    
    distill_pairs = []
    for query in train_queries:
        prompted_input = system_prompt + "\n\n" + query
        ids = teacher_tok.encode(prompted_input, return_tensors="pt")
        out = teacher.generate(ids, max_new_tokens=256)
        answer = teacher_tok.decode(out[0], skip_special_tokens=True)
        distill_pairs.append({"input": query, "output": answer})
    
    # Step 2: Fine-tune student on (query → answer) WITHOUT system prompt
    # Student internalizes the context during training
    # ... standard Trainer loop with distill_pairs as dataset
    return student
```

### 6.2 Soft-Prompt Distillation
Train a small set of continuous embedding vectors (soft prompts) that, when prepended to input, reproduce effect of full context. **Reduces thousands of discrete tokens to 10–50 continuous vectors**.

### 6.3 Trade-off Summary

| Aspect | Token-Level Compression | Context Distillation |
|--------|------------------------|---------------------|
| **When applied** | Inference time | Training time |
| **Training required** | No | Yes (fine-tuning pipeline) |
| **Model access needed** | Black-box OK | Need model weights |
| **Compression ratio** | Tunable per call | 100% token removal |
| **Quality loss** | Slight per request | Locked in at training |
| **Adaptability** | Dynamic | Static (retrain if context changes) |

> "Context distillation is the most aggressive compression — 100% token removal — but it's static. If the context changes (new documents, updated policies), you must retrain. Use it for stable, high-volume prompts where the context rarely changes."

---

## 7. Summarization-Based Approaches (Neel Mishra, 2026)
> **Source**: [Prompt Compression: LLMLingua, Context Distillation](https://neelmishra.github.io/blog/mlops/prompt-engineering/prompt-compression.html)

**Divide-and-conquer summarization** (Fei et al., 2024):
1. Split long text into chunks
2. Summarize each chunk independently
3. Combine summaries
4. Optionally iterate

**Trade-off**: Human-readable, but loses fine-grained detail. Good for narrative context, bad for precise factual retrieval.

---

## 8. Production Decision Tree (AI Prompts Hub, 2026)
> **Source**: [Prompt Compression in 2026](https://aipromptshub.co/blog/prompt-compression-techniques-llmlingua-recomp)

```
Step 1: Measure current average prompt token count
        → Tokenize 1000 representative production prompts
        → Calculate median + 95th percentile
        → If both well under 8K tokens: compression not worth engineering cost

Step 2: Identify the prompt component that's growing
        → Retrieved context (RAG)? System prompt accumulation? Long examples? History?

Step 3: Match technique to component
        → RAG context dominates          → RECOMP
        → Verbose system prompts         → LLMLingua (token-level)
        → High-volume static workloads   → AutoCompressors (with fine-tuning)
        → Quality-critical workflows     → Selective Context

Step 4: Benchmark compression-vs-quality on 100 representative tasks
        → Compress at 2×, 5×, 10× ratios
        → Score downstream output quality vs. uncompressed baseline

Step 5: ROI Calculation
        → Monthly input spend < $500: probably not worth it
        → Monthly input spend > $2K: high ROI from compression
```

---

## 9. Characterizing Compression Methods (arXiv:2407.08892, 2024)
> **Source**: [Characterizing Prompt Compression Methods for Long Context Inference](https://arxiv.org/html/2407.08892)

**Taxonomy of methods**:

| Category | Methods | Key Characteristic |
|----------|---------|-------------------|
| **Token Deletion** | Selective-Context, LLMLingua, LongLLMLingua | Direct token removal based on importance scoring |
| **Semantic Compression** | AutoCompressors, GIST, Soft Prompts | Learned continuous representations |
| **Summarization** | Divide-and-conquer, Recursive | Human-readable summaries |

**Key finding from characterization**: 
- Token deletion methods (LLMLingua family) work well for moderate compression (2–20×)
- Semantic compression (AutoCompressors) enables extreme compression (30–100×) but with quality trade-offs
- **EHPC (Evaluator Heads Prompt Compression)** — new 2025 method: **49.6% performance, 0.88 latency, training-free** — outperforms LongLLMLingua (48.0%, 67.44 latency)

---

## 10. EHPC: Evaluator Heads Prompt Compression (2025)
> **Source**: [arXiv:2501.12959](https://arxiv.org/pdf/2501.12959)

**Innovation**: Training-free prompt compression using evaluator heads attached to transformer layers. Avoids repeated LLM calls for chunking.

**Results** (Table 4/5 from paper):
| Method | Performance | Latency | Training-free |
|--------|-------------|---------|---------------|
| LongLLMLingua | 48.0 | 67.44 | ✓ |
| LLMLingua | 34.6 | 7.51 | ✓ |
| LLMLingua-2 | 39.1 | 1.27 | ✗ |
| **EHPC (ours)** | **49.6** | **0.88** | **✓** |

**Significance**: Best of both worlds — high quality retention AND low latency AND training-free. **Watch for open-source release**.

---

## 11. Token-Efficient Prompt Formats

### 11.1 Structured vs. Natural Language (Multiple Sources)
> **Sources**: 
> - [AI Prompts Hub](https://aipromptshub.co/blog/prompt-compression-techniques-llmlingua-recomp)
> - [CoreConcept (2026-07-21)](https://corecocept.com/blog/context-engineering)

**Structured formats (JSON, YAML, XML) compress better**:
- Explicit field boundaries → easier token importance scoring
- Less linguistic redundancy
- Deterministic parsing

**Natural language advantages**:
- Better model understanding (training distribution match)
- Human readable/debuggable
- More robust to compression artifacts

**Recommendation**: Use structured for machine-to-machine (planner→executor contracts), natural language for human-facing prompts.

### 11.2 Code Compression Techniques (LocalAIMaster, 2026)
> **Source**: [AI Context Windows](https://localaimaster.com/models/context-windows-coding-explained)

Pre-process code before context injection:
- Remove comments: **20–30% token savings**
- Strip whitespace: **10–15% savings**
- Remove unused imports: **5–10% savings**
- Minify config files: **40% savings**

---

## 12. Recommendations for Omega Engine

### 12.1 Compression Pipeline Architecture
```python
class PromptCompressor:
    def __init__(self):
        self.techniques = {
            "rag_context": RECOMPCompressor(),           # RAG retrieval
            "system_prompt": LLMLingua2Compressor(),     # Verbose system prompts
            "high_volume": AutoCompressor(),             # Stable high-volume prompts
            "quality_critical": SelectiveContext(),      # Planner/executor contracts
        }
    
    def compress(self, prompt: Prompt, role: str, budget: int) -> CompressedPrompt:
        # Identify dominant component
        component = self.analyze_prompt(prompt)
        
        # Select technique
        technique = self.techniques.get(component, LLMLingua2Compressor())
        
        # Compress with budget awareness
        return technique.compress(prompt, target_tokens=budget)
```

### 12.2 Planner→Executor Compression Protocol
```python
def compress_plan_for_executor(plan: Plan, executor_budget: int) -> str:
    """
    Planner produces full plan (fits 64K context).
    Compress to fit executor budget (8K-16K).
    """
    # 1. Keep only current step + dependencies (Critical)
    current_step = plan.get_current_step()
    deps = plan.get_completed_dependencies(current_step)
    
    # 2. Summarize completed steps (High Value → compress)
    history_summary = summarize_steps(plan.completed_steps, budget=executor_budget * 0.3)
    
    # 3. Include only relevant knowledge for current step (Critical)
    relevant_kb = knowledge_base.retrieve(current_step.query, budget=executor_budget * 0.4)
    
    # 4. Structured format for token efficiency
    compressed = f"""
    ROLE: {current_step.executor_role}
    TASK: {current_step.description}
    INPUTS: {json.dumps(current_step.inputs)}
    SUCCESS_CRITERIA: {current_step.success_criteria}
    ALLOWED_TOOLS: {current_step.allowed_tools}
    HISTORY: {history_summary}
    KNOWLEDGE: {relevant_kb}
    """
    
    # 5. Final compression if still over budget
    if count_tokens(compressed) > executor_budget:
        compressed = selective_context.compress(compressed, ratio=executor_budget/count_tokens(compressed))
    
    return compressed
```

### 12.3 Context Distillation for Stable Domains
For Omega's **stable knowledge domains** (Tarot, Kabbalah, Software Engineering patterns):
- Distill domain system prompts into soft prompts (10–50 vectors)
- Fine-tune small critic/executor models on domain-specific behavior
- Eliminates need to inject domain prompt at every call

### 12.4 Integration with FTS5-First Search (C-MEM-004)
- Compress retrieved documents before context injection
- FTS5 BM25 ranks → retrieve top-k → compress each → pack into budget
- Hybrid scoring: `-rank + vec_score * 10` applied pre-compression

---

## 13. Sources & Verification Status

| # | Source | Type | Verified | Notes |
|---|--------|------|----------|-------|
| 1 | AI Prompts Hub (2026-06-08) | Comparison blog | ✅ Direct fetch | 4 techniques table, decision tree, ROI calc |
| 2 | Microsoft Research (2023-2024) | Research project | ✅ Direct fetch | LLMLingua, LongLLMLingua, LLMLingua-2 |
| 3 | Princeton NLP (2023) | arXiv paper | ✅ Direct fetch | RECOMP, extractive + abstractive |
| 4 | Chevalier et al. (2023) | arXiv paper | ✅ Direct fetch | AutoCompressors, soft prompts, recursive |
| 5 | Li et al. (2023) | arXiv paper | ✅ Direct fetch | Selective Context, sentence-level |
| 6 | Neel Mishra (2026) | Engineering blog | ✅ Direct fetch | Context distillation code example |
| 7 | arXiv:2407.08892 (2024) | Survey paper | ✅ Direct fetch | Taxonomy, characterization |
| 8 | arXiv:2501.12959 (2025) | Paper | ✅ Direct fetch | EHPC — training-free, best latency |
| 9 | LocalAIMaster (2026-06-21) | Technical guide | ✅ Direct fetch | Code compression techniques |
| 10 | CoreConcept (2026-07-21) | Engineering blog | ✅ Direct fetch | Structured vs natural language |
| 11 | Selective Context GitHub | Implementation | ✅ Direct fetch | Working pip package |

---

## 14. Unverified Claims (Flagged)

- **EHPC "49.6% performance, 0.88 latency, training-free"** — single paper, no independent replication, no open-source release found
- **AutoCompressors "30-100× compression, 60-85% quality"** — paper claims, no production deployment evidence
- **LLMLingua-2 "3-6× faster, better out-of-domain"** — Microsoft Research claim, no third-party benchmarks
- **LongLLMLingua "21.4% performance boost"** — paper claim on NaturalQuestions, specific to GPT-3.5-Turbo
- **Context distillation "100% token removal"** — theoretical; soft prompts still consume some capacity

---

*End of R_PROMPT_COMPRESSION_CONTEXT_DISTILLATION_20260819.md*