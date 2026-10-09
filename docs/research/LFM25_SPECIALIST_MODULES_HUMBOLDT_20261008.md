# LFM2.5 Sub-1B as Specialist Local Cognitive Modules — Research Brief

**Author**: researcher_humboldt · **Date**: 2026-10-08 · **Status**: research brief (not a roadmap commitment)
**Node**: Node 1 (ASUS ExpertBook, i7-13620H, 16GB DDR5 single-channel, CPU-only, ZRAM, Ollama + OWUI)

Labels used: `[Provider claim]` = Liquid/Unsloth marketing, `[Community]` = third-party write-up, `[Local measurement]` = measured on this chassis, `[Interpretation]` = our synthesis.

---

## 0. Executive summary

- LFM2.5-230M and LFM2.5-350M are **open-weight, hybrid conv+attention decoders**, 32K-context, tool-calling, designed for on-device agentic tasks: **data extraction, tool use, instruction following, routing**. They are explicitly **not** positioned for knowledge-intensive work, programming, advanced math, or creative writing. `[Provider claim]`
- **Fine-tuning from base/safetensors is the correct path**. Never fine-tune from GGUF (no gradient path, quantization already applied); QAD-Q4_0 source weights exist for fine-tuning but carry a documented distribution caveat. `[Provider claim]`
- **On Node 1 (CPU-only), Unsloth is disqualified for training** (its training requires NVIDIA/AMD/Intel GPU or Apple MLX). The safe path is **torch-CPU + transformers + PEFT/LoRA + TRL SFTTrainer**, then merge → `convert_hf_to_gguf` → `llama-quantize` → Ollama Modelfile.
- Realistic specialist roles: **schema-constrained extraction, classification/routing, well-curation triage, failure classification, privacy filtering**. Weak fit: long multi-turn "voice," memory recall, reasoning, code.
- A **230M/350M generative model may be the wrong tool for some candidate roles** — Liquid's **LFM2.5-Encoder-230M/350M** (masked-MLM, 8K context, CPU-oriented) is the better base for `failure-classifier`, `privacy-sentinel`, `tool-router` if those are classification-shaped. `[Provider claim]` + `[Interpretation]`
- First experiment should be **measurement, not training**: a prompt+few-shot+retrieval baseline of the two local Q6_K GGUFs through Ollama, scored on JSON validity, schema conformance, and extraction F1. Training starts only if the baseline misses an explicit gate.

---

## 1. LFM2.5 architecture / family status

`[Provider claim]` LFM2.5 is Liquid AI's on-device hybrid family (blog, 2026-01-05 family launch; 230M on 2026-06-25):

| Variant | Layers | Pretrain tokens | Context | Notes |
|---|---|---|---|---|
| LFM2.5-230M | 14 (8 conv + 6 GQA) | 19T | 32,768 | Distilled from 350M, then DPO + multi-domain RL |
| LFM2.5-350M | 16 (10 conv + 6 GQA) | 28T | 32,768 | Same token budget as the 1.2B |
| LFM2.5-1.2B-Instruct | 16 (10+6) | 28T | 32,768 | The "holds a thread" size |
| LFM2.5-2.6B | — | — | 32K (Ollama metadata reports up to 128K locally) | Dense flagship edge model |
| LFM2.5-8B-A1B | MoE | — | — | |
| LFM2.5-VL 450M/1.6B | VLM | — | — | |
| LFM2.5-Encoder 230M/350M | bidirectional | same backbone | 8,192 | MLM; classification/routing/token tasks |
| LFM2.5-Retrievers | bidirectional | — | — | multilingual retrieval |

Facts of note:
- **Hybrid backbone**: double-gated short convolutions interleaved with grouped-query attention; small KV cache, fast decode on CPU. Vocab 65,536 (~1/4 of Gemma 3), which is why the 1.2B packs small. `[Provider claim]` — https://www.liquid.ai/blog/introducing-lfm2-5, https://www.liquid.ai/blog/lfm2-5-230m, https://docs.vllm.ai/projects/recipes/en/latest/LiquidAI/LFM2.5.html
- **Positioning**: "foundation for developers to fine-tune and deploy in agentic workflows"; strong on instruction following and function calling for its size, ordinary-or-worse world knowledge. IFEval 71.7 (230M) / 77.0 (350M) / 86.2 (1.2B); Q4_K_M footprints ~153MB / ~229MB / ~731MB. `[Provider claim]` — https://www.ertas.ai/blog/lfm2-5-230m-vs-350m-vs-1-2b-on-device, https://www.explainx.ai/blog/liquid-ai-lfm2-5-230m-edge-agent-model-2026
- **Tool-call wire format**: native Pythonic calls wrapped in `<|tool_call_start|>…<|tool_call_end|>`; JSON-by-system-prompt is a supported alternative. Training data must match the shipped format. `[Community + Provider claim]` — ertas blog, https://huggingface.co/LiquidAI/LFM2.5-350M
- **Local evidence on this chassis**: LFM2.5-2.6B-heretic Q4_K_M ≈ **20.3–21.2 t/s at 6 threads**, TTFT ~65 ms, thermally limited (90–96 °C), concurrent embedding load costs ~15%, zRAM confounds early data, thread count 6 is optimal for LFM. `[Local measurement]` — `docs/research/BENCHMARK_STUDY_20260926.md`, `docs/BENCHMARKS.md` (2026-10-07 entry). Ollama reports `lfm2` architecture, `tools`+`thinking` capabilities on the installed 2.6B.

**Intended use cases (provider's own framing)**: data extraction, tool-use agents, on-device assistants tight on RAM/latency, skill-selection layers (e.g. the Unitree G1 skill-router demo). `[Provider claim]`

## 2. Fine-tuning feasibility of 230M/350M on CPU-only Node 1

`[Interpretation]` grounded in sources:

- **LoRA (r=8–16) on the 350M, short context (512–2048), batch 1–4, fp32 or oneDNN-bf16**, fits in 16GB RAM with ZRAM headroom. LoRA trains ~1–2% of params; optimizer states shrink to the adapter. Estimate: minutes-to-hours for a few thousand examples on a 10C/16T CPU. (No published CPU-training wall-clock for this machine — **must be measured in the pilot**.)
- **Full fine-tune of 230M/350M in fp32+Adam** is plausible at 16GB (params+grads+Adam ≈ 4–8 GB) but leaves little headroom and gives no quality benefit for format-shaped tasks over LoRA. `[Interpretation]`
- **QLoRA 4-bit** is a GPU path (bitsandbytes/Unsloth) — not a useful CPU accelerator here.
- **RAM budget check**: currently 14GB total, 8GB available — Ollama resident models plus a training process must not overlap. Gate: `MAX_LOADED_MODELS=1` hygiene, run training with Ollama models evicted (`OLLAMA_NUM_THREADS`/`keep_alive` discipline). `[Interpretation]`
- **CPU feature check**: i7-13620H has AVX2 (no AVX-512). torch CPU fp32 will work; bf16 may or may not help — verify in pilot, do not assume. `[Interpretation]`
- The ROADMAP dream-log line *"turn well-export into a fine-tune … once RAM headroom (32GB) exists"* predates this analysis: for ≤350M LoRA at 16GB it is **likely no longer blocked on a 32GB machine** — flag to operator to revisit. `[Interpretation]`

## 3. Framework choice — what is safest on Node 1

| Framework | CPU-only training? | Verdict for Node 1 |
|---|---|---|
| **Unsloth** | ❌ (training needs NVIDIA/AMD/Intel GPU or Apple MLX; CPU only for chat/data-recipes) | Disqualified for training; fine for GPU elsewhere |
| **TRL SFTTrainer + PEFT LoRA + transformers + torch-CPU (+ accelerate, datasets)** | ✅ works on CPU | **Safest default** — Liquid's own docs present this path; `trl>=0.9`, `transformers>=4.55`, `torch>=2.6` |
| **LEAP Finetune** (Liquid's TRL wrapper) | Same as TRL; wraps dataset validation, config, evals | Optional convenience; evaluate after TRL baseline works |
| **DPO** | ✅ but memory ×2 (policy+ref) | Defer; SFT first |
| **GRPO / RL** | ⚠️ rollout-bound; on CPU the rollout phase would dominate and KV caches pile up | Not recommended on Node 1; if ever, on a GPU |
| **llama.cpp** | ❌ no practical CPU LoRA *training* path (train examples exist but are experimental) | Use for **conversion + serving only** |
| **GGUF conversion path** | n/a | merge LoRA → `convert_hf_to_gguf.py` → `llama-quantize` (Q4_K_M/Q6_K) → Ollama `Modelfile` (`FROM <gguf>`, `PARAMETER num_thread 6`) |

Recommended pilot venv: `~/WanderGround/.venv-lfm` (mirrors the existing `.venv` convention) with `torch` (CPU wheel), `transformers>=4.55`, `peft`, `trl`, `accelerate`, `datasets`, `hf-xet`. Do **not** install into the mempalace venv. `[Interpretation/convention]`

## 4. QAD checkpoints — appropriate for fine-tuning?

`[Provider claim]` Liquid released QAD (Quantization-Aware Distillation) Q4_0 GGUFs for 230M/350M/1.2B/2.6B in Aug 2026: BF16-teacher → quantized-student distillation, ~97% of BF16 average accuracy, matching Q5_K_M at 230M/350M, 4–33% higher decode throughput.

Caveats for our use:
1. **QAD Q4_0 GGUFs themselves are deployment artifacts — do not fine-tune from GGUF.**
2. **QAD source weights (FP32 safetensors) ship in the `qad/` subfolder** of each `-GGUF` repo, loadable via `AutoModelForCausalLM.from_pretrained(repo_id, subfolder="qad")`, and Liquid states they are "intended for fine-tuning and experimentation" — **but** "published QAD results apply to the Q4_0 GGUF; direct FP32/BF16 inference and other quantization formats may behave differently."
3. **Safest choice**: fine-tune from the standard post-trained BF16/safetensors checkpoint (`LiquidAI/LFM2.5-230M`, `LiquidAI/LFM2.5-350M`) or the `-Base` variants for a cleaner substrate, then quantize to our serving format. Use QAD-Q4_0 GGUFs as the **serving target** when quality≈Q5_K_M is acceptable and speed matters. `[Interpretation]`

Our local 230M/350M files are `LFM2.5-230M-Q6_K.gguf` and `LFM2.5-350M.i1-Q6_K.gguf` (higher-bit PTQ baselines — fine for inference baselines, not for training).

## 5. Realistic vs unrealistic tasks for 230M/350M

`[Provider claim]` + `[Community/ertas-Ertas]` + `[Interpretation]`

**Realistic (with facts supplied in the prompt, short outputs):**
- Schema-constrained extraction → JSONL (mempalace-extractor shape). 230M was literally evaluated on data-extraction / tool-use agentic benchmarks.
- Classification/routing/labeling over short windows: failure class, well `kind`/`domain`/`tags`, keep/supersede/merge triage — especially via **Encoder** variants.
- Intent routing for a fixed tool menu (omega-hub dispatcher) with a tight allowlist.
- Short template-bound summarization/ticketing text; well-entry normalization.
- Privacy filtering (PII detection demo exists on the encoder side).

**Unrealistic / do not ship:**
- Open-ended reasoning, math, programming, creative writing (provider says so; IFBench ≈ 81% of 1.2B at 230M, MMLU-Pro ≈ 46% of 1.2B).
- Long multi-turn conversational memory — Ertas's fine-tuned 350M **lost the thread of casual multi-turn chat** while holding its character voice, though automated metrics passed. Entity voice over multi-turn is a trap at 350M.
- Authoritative "memory recall" — that is MemPalace/retrieval's job; the model formats, it does not remember.
- Autonomous tool loops without a bounded executor — needs the P6.1 `MAX_ROUNDS`/timeout guardrails.

## 6. Integration into Omega Engine without contaminating core logic

`[Interpretation]` anchored in existing rules:

1. **Adapter rule (Well `fc3c8c43`)**: specialists live in **Omega Engine core** (`omega-engine-alpha/scripts/`, services, MCP tools). OpenCode remains the disposable CLI; agents call the specialists via CLI/REST/MCP — never as OpenCode plugins, never as Omega core plugins.
2. **Transport rule**: MemPalace is a local one-way projection; omega-hub/Hivemind is the only write path for coordination. A fine-tuned model drafting well-seeds still enters the world through `make well-add`/`wander` → Well, never through a MemPalace write dressed as a handoff.
3. **Each specialist = one versioned artifact**: `docs/models/<name>.md` OMER card (candidate→active→retired) + Ollama Modelfile + training config hash + dataset hash + eval report. No undocumented local GGUFs (see the orphan `LFM2-1.2B-Extract-Q5_K_M.gguf` — no repo reference, treat as unknown-origin artifact).
4. **Privacy tier**: privacy-sentinel and any PII-touching extractor run local-only, egress=none, no remote teacher calls on unsanitized text. Free Zen models collect prompt data — teacher labeling must use paid zero-retention models or fully local teachers.
5. **Failure isolation**: every specialist call has a schema-validated fallback (deterministic regex/JSON-schema extraction or "ask the human"). Small models fail open unless the harness fails closed.
6. **Registry pattern precedent**: `json-extractor`, `summarizer`, `linux-admin` Ollama models already exist as custom Modelfiles — specialists follow that pattern, extended with trained weights when the baseline fails.

## 7. Dataset design + evaluation gates — mempalace-extractor / well-curator pilot

**Sources** (all local, provenance-bearing):
- MemPalace drawers + sesstion transcripts (`ochist export`-style), WanderGround captures.
- `make well-export` JSONL bundle (Markdown + JSONL) as the well-curator corpus.

**Labeling**: teacher = LFM2.5-2.6B or LFM2.5-1.2B locally, or a paid-ZDR frontier model for gold; every label carries `model_id`, `prompt_hash`, `ts`, and a human-audit sample (≥10%).

**Format** (match shipped wire format):
- extractor: JSONL `{wing, room, content, source_file, provenance}` per item.
- curator: JSONL `{kind, domain, tags[], action: keep|supersede|merge|drop, superseded_by?}` with the Well's forward-supersession rule enforced at scoring time.

**Splits**: by session, not by row (prevents transcript leakage); ≥100-item held-out gold set, never seen in training.

**Evaluation gates (proposed, adjust at experiment):**
| Gate | Extractor | Curator |
|---|---|---|
| JSON validity | ≥95% | ≥95% |
| Schema conformance | ≥95% | ≥95% |
| Content quality (P/R vs gold) | F1 ≥ 0.70 | accuracy ≥ 0.80 on kinds/action |
| Supersession direction correctness | n/a | 100% on adversarial set |
| vs prompt-only baseline | ≥ +10 pts or training is rejected | same |
| Latency p95 @512 tok, t=6 | ≤ 2 s (estimate — measure) | same |
| Forgetting probe (20 generic extractions) | no collapse vs base | no collapse vs base |
| Contamination | no PII in training set (sentinel-scanned) | same |

**Training config (first pass)**: LoRA r=16, alpha=32, dropout 0.05, target `[q,k,v,o,gate,up,down]_proj`, lr 1e-4 cosine, 1–3 epochs, seq len 1024–2048, batch 1–4 w/ grad accum, fp32 (bf16 only if AVX2-oneDNN shows speedup), early stop on val loss.

## 8. Risks

- **Hallucination / JSON failure** at 230–350M — mitigation: schema validation + constrained decoding (GBNF via llama.cpp/Ollama format), teacher-audit.
- **Overfitting** tiny datasets → memorized templates, brittle on paraphrase — mitigation: held-out gold, small epochs, LoRA.
- **Privacy leakage**: training corpus contains the operator's life (the Well is personal); free-tier labeling leaks it to a provider; fine-tune retains it — mitigation: ZDR teachers, local-only serving, never commit the dataset to git.
- **License**: LFM Open License v1.0 — Apache-like, free commercial use under $10M annual revenue, no copyleft, attribution + NOTICE retention required, derivative use stays under the license. Fine for Omega (local/research); record it in each OMER card.
- **Quantization mismatch**: BF16→Q4_K_M/Q6_K serving drift; QAD-Q4_0 reduces it at 230M/350M. Evaluate the *served* artifact, not the training artifact.
- **CPU latency & RAM**: training will be slow (hours-class at most-for-LoRA) and must not fight a resident Ollama model; inference is fast (2.6B ≈ 21 t/s; smaller sizes should be faster — measure).
- **Context window expectations**: marketing 32K; local Ollama metadata has shown 128K on the 2.6B artifact; a 230M does not usefully exploit either — keep effective windows ≤2–4K at inference for these roles.
- **Thermals/power**: Node 1 thermally limits at ~90–96 °C under LFM load; long training runs need the same care as benches (idle-isolated E-core hygiene, zRAM on for production but off for measurements).
- **Undocumented artifact trap**: `LFM2-1.2B-Extract-Q5_K_M.gguf` has no repo provenance — do not build on it until its origin is recorded.

## 9. Roadmap entries (proposed)

- **New phase P7 — "Local specialist small-model modules" (status: `backlog`)** — one ordered home for 230M/350M specialist R&D, separate from P5 (memory substrate) and P6 (native MCP) so its gates and budgets don't blur into either. Rationale: every candidate role crosses both.
  - **P7.1** — LFM2.5-230M/350M extraction pilot: baseline eval → optional TRL/LoRA SFT → OMER card. (This brief's first experiment.)
  - **P7.2** — Well-curator pilot (curation JSONL + supersession-direction gate).
  - **P7.3** — Encoder-route classification (`failure-classifier`, `privacy-sentinel`, `tool-router`) with LFM2.5-Encoder, CPU-trained, vs generative LoRA baseline.
  - **P7.4** — Specialist registry + Ollama Modelfile factory (extend the `json-extractor`/`summarizer` pattern), feeding MCP/omega-hub dispatch.
- **Dream-log update candidate**: ROADMAP's *"Fine-tune seed … once RAM headroom (32GB) exists"* is likely stale for ≤350M LoRA — operator ruling requested.
- **Any adoption**: keep `LFM2.5-Encoder` vs generative LoRA as a measured A/B in P7.3, not a theological choice.

## 10. Concrete first experiment (with success/failure criteria)

**E0 — baseline measurement (no training; ~1–2 h)**
- Input: 100 held-out transcript windows; gold JSONL produced by teacher + human audit.
- Run: `LFM2.5-230M-Q6_K` and `LFM2.5-350M.i1-Q6_K` via Ollama, strict system prompt, 2 few-shot exemplars, `format: json`, temp 0.1, `num_thread 6`, 512–1024 ctx.
- Measure: JSON validity %, schema conformance %, P/R/F1 vs gold, p50/p95 latency.
- **Decision gates**:
  - If 350M hits validity ≥95%, conformance ≥95%, F1 ≥0.70 → **prompt+retrieval is the answer; do not fine-tune**; record OMER card `research_status: active` as prompt-only module.
  - If validity/conformance <80% → proceed to E1.
  - If 230M fails and 350M marginally passes → default specialist size is 350M.

**E1 — minimal training (only if E0 fails; LoRA SFT; 350M first)**
- venv `~/WanderGround/.venv-lfm`; TRL SFTTrainer, config per §7; ≤2k examples; ≤3 epochs.
- Deliverable: merged safetensors → Q4_K_M and QAD-Q4_0 GGUFs → Ollama `lfm25-extractor` Modelfile.
- **Success gates**: E0's harness rerun on the served artifact: validity ≥95%, conformance ≥95%, F1 ≥ (baseline + 10 pts), ≤2 s p95, no forgetting-probe collapse.
- **Failure criteria (record honestly in OMER card)**: any gate unmet after one retry with lr/epoch adjustment → reject generative route, promote LFM2.5-**Encoder** classification or a 1.2B base; file rejection with eval numbers.
- **Parking rule**: training never runs with a resident Ollama model; `MAX_LOADED_MODELS=1` discipline; ZRAM on for production, off only for *measurement* runs.

---

*Prepared 2026-10-08. Facts labeled; estimates marked. Nothing above is a benchmark claim for this chassis except the [Local measurement] rows, which cite `docs/research/BENCHMARK_STUDY_20260926.md` and `docs/BENCHMARKS.md`.*
