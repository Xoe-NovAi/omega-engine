# 🔱 RESEARCHER — Sovereign Language Module: Provenance, Cross-Engine Wiring, Naming & Community State-of-Art (2026)

**AP Token**: `AP-RESEARCHER-LANGUAGE-MODULE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ Jem-Analyst ⬡ opencode ⬡ trc_research ⬡ LANGUAGE-MODULE-STRATEGY

**Date**: 2026-07-10
**Subject**: `omega-moderation` → engine-wide language integrity module (renamed proposal inside)
**Method**: Sovereign Search Fleet (Tier 1 `websearch`/`webfetch` + Tier 2 Firecrawl-class deep extraction), triangulated against local source at `omega-moderation/` and `omega-engine/`. All searches scoped to 2026.

---

## 1. Executive Summary

The `omega-moderation` system is already a hardened, local-first content-integrity stack: dual-pass obfuscation detection (`obfuscation/detector.py`), an ML ensemble (Perspective + OpenAI + HuggingFace `unitary/unbiased-toxic-roberta` + `s-nlp/roberta_toxicity_classifier` + a structural `LocalFallback` with **no slur lists**), Merkle-MMR + Ed25519 audit (`governance/audit.py`), GDPR tombstone erasure (`governance/privacy.py`), ε-DP metrics (`observability/differential_privacy.py`), and a FastAPI surface (`api/app.py`).

The user's three strategic questions resolve as follows:

1. **Provenance-Aware Synthesis** should be implemented as a first-class `ProvenanceSpan` primitive that rides the existing `trace_id` backbone (`src/omega/observability/`) and is modeled on the **OpenLineage AgentRunFacet** (RFC #4407 / PR #4480) — the 2026 open standard for agentic AI lineage. Every token/chunk is tagged `user | model:<provider> | tool:<mcp> | memory:<entity>`. "Hallucination laundering" is blocked by a **provenance-chain cross-check** (claim → cited tool output) plus optional output watermarking (SynthID/C2PA pattern).
2. **Cross-engine wiring**: 7 Omega systems should consume the module — Oracle (pre-filter), ContextBuilder (memory sanitization), Iris/Nova (voice I/O), Hivemind (`omega_hub`), Soul Distiller, ModelGateway (output tagging), and MemoryStore (exchange provenance). Integration points and data contracts are in §3.
3. **Naming**: recommend **`omega-vetala`** — Sanskrit "spirit of discernment," on-theme with the Omega mythic pantheon (Kali lineage), semantically precise (discernment ≠ mere blocking), and collision-free. Runner-up: `omega-aegis`.
4. **Knowledge gaps** (2026): multimodal omni-guardrails (GuardReasoner-Omni, SingGuard), context-aware moderation (Mamba-3 / RWKV-7 hybrids), XAI for moderation (counterfactual generation + integrated gradients), federated/HE privacy (SEAL, TenSEAL, MP-SPDZ, SMHE), Constitutional AI at inference (Reflect), uncensored 4B–14B GGUF models, and certified adversarial robustness (CSS, DCRS, CluCERT).
5. **Community state-of-art**: NeMo Guardrails, Guardrails AI, LLM Guard, Presidio, Lakera, Rebuff, PyRIT, Garak — with a sovereignty-alignment verdict (local-first vs cloud-dependent) in §6.

> **Constraint note**: This document is research-only. No source in `omega-moderation/` or `omega-engine/` was modified (per mandate).

---

## 2. Provenance-Aware Synthesis — Engine-Wide Architecture

### 2.1 The Problem: "Model Hallucination Laundering"

When a model receives tool output (e.g., a web fetch, a DB row, an MCP result) and re-states it as if it were its own reasoning, the provenance of the claim is lost. A downstream moderator then cannot tell whether a toxic/incorrect claim originated from the **user**, the **model**, a **tool**, or **memory**. This is the laundering gap. The 2026 OpenLineage community explicitly identified this: agentic AI "does not fit the Job→Run→Dataset model" and needs a provenance chain answering *"which tool calls were made, with what inputs, producing what outputs?"* [#1].

### 2.2 Reference Standard: OpenLineage AgentRunFacet (2026)

OpenLineage is the open standard for data lineage; **Marquez** is its reference store [#2]. In 2026 two extensions target agentic AI directly:

- **RFC AgentRunFacet** (OpenLineage Discussion #4407) — models an agentic flow as a Job, tools as sub-jobs (via `parent_run`), with a `turns[]` array carrying `turnId`, `turnType` (REASONING|TOOL_CALL|RETRIEVAL), `inputContextHash`, `outputHash`, and `toolCalls[]{toolName, inputHash, outputHash, datasetRef}` [#1].
- **AgentAttributionRunFacet** (PR #4480) — adds `covenantInEffect` (a hash of the governance attestation in force at execution) so a lineage record is *also* a compliance artifact [#1].

**Sovereign adaptation**: We do **not** need a full OpenLineage/Marquez deployment (heavy, and Marquez is a network service — violates M7 local-first spirit for the core path). Instead we adopt the **facet shape** as a local, in-process `ProvenanceSpan` dataclass that serializes into the existing audit chain (`governance/audit.py`) and the `trace_id` log stream (`src/omega/observability/`).

### 2.3 The `ProvenanceSpan` Primitive

```python
@dataclass
class ProvenanceSpan:
    trace_id: str                 # from src/omega/observability new_trace_id()
    span_id: str
    origin: Literal["user", "model", "tool", "memory"]
    origin_ref: str               # e.g. "native-gguf:qwen3-8b" | "mcp:searxng" | "memory:SOPHIA"
    content_hash: str             # sha256 of the chunk (pre-normalization)
    normalized_hash: str          # sha256 after ObfuscationDetector.normalize()
    parent_span_id: str | None    # builds the chain
    timestamp: str
```

Each engine stage emits spans:

| Stage | Origin tag | Emitted at |
|-------|-----------|-----------|
| User query | `user` | `oracle.py` `talk()` entry |
| Memory injection | `memory:<entity>` | `context_builder.py` `build_context()` |
| Tool/MCP call | `tool:<mcp_name>` | `omega_hub` / `orchestrator.py` |
| Model inference | `model:<provider>:<model>` | `model_gateway.py` |
| Final response | `model:<provider>` (root span) | `oracle.py` response assembly |

The chain is anchored to the **Merkle-MMR audit log** (`governance/audit.py` `record_event`) so provenance is tamper-evident and Ed25519-signed — satisfying EU AI Act Article 12 automatic logging [#1][#3].

### 2.4 Anti-Laundering Cross-Check

When a `model` span asserts a factual claim that references a `tool` or `memory` span, run a lightweight **claim-grounding check** (local, no LLM required for v1):

1. Extract candidate claims from the model span (noun-phrase / entity spans).
2. For each, fuzzy-match against the cited `tool`/`memory` span text (token-overlap + embedding cosine via the existing Qdrant adapter).
3. If a high-confidence claim has **zero grounding** in its cited source, flag `unverified_attribution` and route to the moderation action tier (same escalation path as `evasion_attempt` in `engine.py`).

This mirrors the 2026 "Beyond Red-Teaming" work that relocates guardrail verification to pre-activation representation space and treats harm as a *region*, not a point [#4]. It is structural, not lexical — consistent with the module's no-slur-list philosophy.

### 2.5 Output Watermarking (Optional, C2PA/SynthID Pattern)

For responses that leave the sovereign boundary (published, exported), attach a **C2PA-style Content Credential** (cryptographically signed manifest of the `ProvenanceSpan` chain) and/or an invisible **SynthID**-style token watermark. In 2026 SynthID watermarks 10B+ Google assets and survives re-encoding/screenshots; C2PA 2.3 (Dec 2025) is the open metadata standard; the two are **complementary** (pixels vs metadata) [#5][#6][#7]. For a local-first engine we implement the **C2PA manifest** ourselves (open standard, royalty-free) and treat SynthID as an optional cloud-side verify hook (not a hard dependency — preserves M7).

> **Sovereign note**: Watermarking local model output is optional and must never block local inference. It is an *export* feature, not a runtime gate.

### 2.6 Data Lineage Tooling (for the audit/observability layer)

If the engine later needs a queryable lineage graph, **Marquez** (self-hosted, Docker Compose) is the sovereign-aligned choice; OpenLineage events can be emitted from `audit.py` without adopting Marquez's network service for the hot path [#2][#8].

---

## 3. Cross-Engine Wiring Map

Data contract convention: the module exposes `VetalaClient.moderate(text, *, user_id, content_type, trace_id) -> ModerationResult` (the existing `ModerationEngine.moderate` signature in `engine.py`) plus a new `VetalaClient.check_provenance(spans) -> GroundingResult`.

| # | System | Integration Point (file → function) | What it does | Data Contract |
|---|--------|--------------------------------------|--------------|---------------|
| 1 | **Oracle** | `src/omega/oracle/oracle.py` → `talk()` / `_summon()` entry, **before** entity routing | Pre-filter user query; block/quarantine obfuscated or toxic input at the gate; emit `user` provenance span | `moderate(query, user_id=..., trace_id=...)` → if `action >= QUARANTINE`, short-circuit routing; else attach `ProvenanceSpan(origin="user")` |
| 2 | **ContextBuilder** | `src/omega/oracle/context_builder.py` → `build_context()` / `_compact_and_format_exchanges()` | Sanitize injected memory so a poisoned/obfuscated memory block cannot ride into the prompt; tag each memory exchange | Run `moderate()` on each exchange's `user`/`assistant` text; drop or redact flagged spans; emit `memory:<entity>` spans |
| 3 | **ModelGateway** | `src/omega/oracle/model_gateway.py` → response assembly | Tag model output with `model:<provider>:<model>` provenance; post-filter response before return | Wrap inference result; emit `ProvenanceSpan(origin="model", origin_ref=provider)`; run `moderate()` on final text; attach `action` to `OracleResponse` |
| 4 | **MemoryStore** | `src/omega/memory_store.py` → `add_exchange()` | Persist the provenance span chain alongside the exchange so future retrieval carries origin tags | Store `spans: list[ProvenanceSpan]` as a column/JSON; enables §2.4 grounding on recall |
| 5 | **Iris / Nova** | `src/omega/iris/matcher.py` + `nova/` FastAPI | Moderate spoken input (STT transcript) and spoken output (TTS text) for the voice assistant | Same `moderate()` contract on transcript text; low-latency path (local detectors only, skip cloud Perspective/OpenAI) |
| 6 | **Hivemind** (`omega_hub`) | `mcp_servers/omega_hub/` → `hivemind_post_context()` / `hivemind_handoff()` | Moderate inter-agent messages and handoff packets to prevent cross-agent toxicity propagation | `moderate(message, user_id="agent:"+entity)`; flag `evasion_attempt` in agent messages; quarantine handoff if toxic |
| 7 | **Soul Distiller** | `src/omega/oracle/soul_distiller.py` → distillation pipeline | Ensure distilled L1→L2→L3 lessons are non-toxic and non-obfuscated before they enter `soul.yaml` | Run `moderate()` on candidate lesson text; reject lessons failing policy; emit `memory:<entity>` span for the lesson source |

**Wiring principle**: The module is a **sidecar**, not a monolith. Each integration point calls `VetalaClient` (a thin wrapper around `ModerationEngine`) and respects the existing `ActionTier` escalation (`ALLOW < WARN < QUARANTINE < BAN`, `engine.py:_max_tier`). No engine file is rewritten to embed moderation logic inline — preserving the Engine-Stack Firewall (Mandate M2).

---

## 4. Naming Proposal

The module is now: obfuscation + ML ensemble + Merkle audit + GDPR erasure + DP metrics + (planned) provenance. "omega-moderation" is too narrow.

| Candidate | Etymology | Fit |
|-----------|-----------|-----|
| `omega-aegis` | Greek — Zeus's shield; protection | Strong "sovereign shield" connotation; generic; collides with many "aegis" security products |
| `omega-gatekeeper` | Generic sentinel | Clear but unimaginative; overused in AI safety |
| `omega-sovereign-shield` | Descriptive | Verbose; reads like a marketing phrase, not a package name |
| `omega-lingua-guard` | Latin *lingua* "tongue" + guard | Good for language focus, but implies text-only (excludes multimodal roadmap) |
| **`omega-vetala`** | Sanskrit **Vetala** (वेताल) — a spirit of *discernment* in Hindu/Buddhist folklore; poses riddles that test wisdom and separate truth from illusion | **Best fit**: (1) *discernment* is precisely what the module does — it distinguishes obfuscated/toxic/harmful from clean, not merely "blocks"; (2) on-theme with the Omega mythic pantheon (Kali is Sanskrit; Vetala is a Kali-adjacent spirit); (3) unique — zero collision with NeMo/Llama Guard/LLM Guard; (4) short, importable, package-name-safe |

**Recommendation: `omega-vetala`.**

Rationale (etymological): In the *Vetala Panchavimshati* and Tibetan *Vetala* lore, the Vetala possesses a corpse and speaks only to test the king's discernment — rewarding correct judgment, exposing flawed reasoning. The module's job is exactly this: it is the spirit that rides the sovereign's speech, testing every token for obfuscation, toxicity, and unverified attribution, and refusing to let illusion (laundered hallucination, zero-width attacks) pass as truth. The name also ages well into the multimodal roadmap (a "spirit of discernment" is modality-agnostic), unlike `lingua-guard`.

Runner-up if a Greco-sovereign brand is preferred: `omega-aegis`.

---

## 5. Knowledge Gap Filling (2026 Best Practices)

### 5.1 Multimodal Moderation (local-first)
- **GuardReasoner-Omni** (2026, arxiv 2602.03328): first omni-modal guardrail reasoning across text/image/video/audio via explicit CoT; 3B/7B sizes; trains on 181k corpus (Aegis2, BeaverTails, VLGuard, SPA-VL, MuTox…). 7B reaches 86.39% avg (all) prompt F1 [#9].
- **SingGuard** (2026, arxiv 2606.22873): policy-*adaptive* multimodal guardrail; runtime policy as input; fast/hybrid/slow inference regimes; 56,340-example benchmark, 80+ risk types; SOTA F1 across 6 families [#10].
- **LLaVAShield** (CVPR 2026, arxiv 2509.25896): safeguards multimodal multi-turn VLM dialogues; MMRT dataset [#11].
- **Hi-Guard** (arxiv 2508.03296): hierarchical pipeline (binary filter → fine-grained) + policy-aligned GRPO [#12].
- **Local stack**: CLIP (embeddings), Whisper/Large-v3 (audio), LLaVA / Qwen2.5-VL (visual reasoning) — all runnable on consumer GPU/CPU; pair with Presidio for image PII [#13][#14].
- **Sovereign path**: adopt a small local guardrail model (GuardReasoner-Omni-3B or SingGuard-3B) as a new `detectors/` entry; keep cloud Vision APIs out of the default path (M7).

### 5.2 Context-Aware Moderation (conversation-state transformers)
- Pure Transformers quadratic-scale at 128k+ context; **hybrid SSM+attention** dominates 2026 production [#15].
- **Mamba-3** (arxiv 2603.15569, 2026): selective SSM with complex-valued state + MIMO; 1.8pt gain over Gated DeltaNet at 1.5B; half the state size of Mamba-2 [#16].
- **RWKV-7 (Goose/G1)**: purely recurrent, constant memory, CPU-friendly, but recency-biased (42% recall at early context vs 81% recent) [#15][#17].
- **Jamba 1.5** (AI21): Transformer+Mamba MoE hybrid, 256k context, production-deployed [#15].
- **Sovereign path**: for long conversation-state moderation (multi-turn toxicity, evasion drift), a small **Mamba/RWKV hybrid** local classifier beats a Transformer on memory-constrained hardware. But for the core path, the existing dual-pass + ensemble is sufficient; reserve SSM models for the *conversation-state* detector (tracking evasion across turns).

### 5.3 Explainable AI for Moderation
- **CF-Detox** (arxiv 2405.09948): bridges counterfactual generation + XAI for toxicity mitigation; uses Integrated Gradients / KernelSHAP / self-attention to target toxic tokens, then counterfactual rephrase; preserves meaning [#18].
- **Prompt-Counterfactual Explanations (PCE)** (arxiv 2601.03156, 2026): adapts counterfactuals to generative systems — *what in the prompt caused the toxic output?* Enables proactive prompt auditing + red-teaming [#19].
- **Integrated Gradients** (Sundararajan et al. 2017) remain the standard gradient method for token attribution in moderation classifiers [#18][#20].
- **Sovereign path**: add a `detectors/xai_explainer.py` that, on a `QUARANTINE`, returns the top-3 toxic-salient tokens (Integrated Gradients over the local HF classifier) — turning every block into an auditable, explainable decision (supports EU AI Act Article 14 human-oversight explainability).

### 5.4 Federated Learning & Privacy (HE / SMPC)
- **Microsoft SEAL** (MIT, v4.3.3, 2026): BFV/BGV (integers) + CKKS (real numbers, approximate) homomorphic encryption [#21].
- **TenSEAL** (OpenMined): CKKS/BGV over SEAL, Pythonic, for ML on encrypted data [#22].
- **MP-SPDZ** (Keller, CCS 2020): versatile SMPC framework; ~100× less communication than MHE for statistical tests [#23].
- **HEAD-FL** (iacr 2026/1376): adaptive DP + verifiable homomorphic aggregation; FedAvg-based, tight RDP accounting [#24].
- **SMHE** (arxiv 2506.20101): fixes CDKS multi-key HE leakage for PPFL; <2× overhead vs CDKS [#25].
- **Sovereign path**: relevant **only** if the engine ever trains across user devices (it does not today — local-first, single-user). Document as a *future* capability for a community WAD marketplace (D178 horizon). Do **not** add HE to the single-node path (over-engineering — violates M19 sane-boundary). The existing `differential_privacy.py` (ε-DP via diffprivlib) already covers local metric privacy.

### 5.5 Constitutional AI (self-critique loops)
- **Anthropic Constitutional AI** (2022→2026): self-critique + RLAIF; Claude's "Soul Doc" constitution published Jan 2026 (22k words) [#26][#27].
- **Reflect** (arxiv 2601.18730, 2026): *inference-time* constitutional alignment — no training; constitution-conditioned generation → self-evaluation (Likert per principle) → critique → revision; plug-and-play; generates DPO data as by-product [#28].
- **C3AI** (arxiv 2502.15861): crafting/evaluating constitutions; positively-framed, behavior-based principles align better with human preferences [#29].
- **Sovereign path**: the module's `PolicyEngine` (`governance/policy.py`) is the natural home for a **user-authored constitution** (a YAML of principles). Adopt the Reflect loop as an optional `detectors/constitutional.py` post-filter: generate → self-evaluate against the user's constitution → revise. This is local-first and aligns with the Omega "user-owned values" thesis.

### 5.6 Uncensored Local Models 4B–14B (GGUF notes)
The module must run on the user's hardware. Recommended uncensored/abliterated GGUF models (2026, community HF):

| Model | Params | GGUF Q4_K_M | Notes |
|-------|--------|-------------|-------|
| Qwen3-8B-Uncensor | 8B | ~5.0 GB | `mradermacher/Qwen3-8B-Uncensor-v2-i1-GGUF`; IQ4_XS ~4.7 GB [#30] |
| Qwen3.5-9B-Uncensored | 9B | ~6.3 GB | `suldanpashir/Qwen3.5-9B-Uncensored`; 131k ctx, Apache 2.0 [#31] |
| Qwen3-4B-Revised | 4B | ~2.7 GB | `Smoffyy/Qwen3.5-4B-Instruct-Revised-GGUF`; entry-point local [#32] |
| Qwen3-14B-abliterated | 14B | ~8–9 GB | `richardyoung/Qwen3-14B-abliterated-GGUF`; uncensored [#33] |
| Nemomix-v4.0-12B | 12B | ~7.5 GB | `bartowski/Nemomix-v4.0-12B-GGUF`; strong general [#34] |

Quant guidance (2026 community): prefer **K-quants** (`Q4_K_M`, `Q5_K_M`) for quality; use **I-quants** (`IQ3_XS`, `IQ4_XS`) below Q4 on cuBLAS/rocBLAS; fit whole model in VRAM+1–2 GB headroom [#34]. The moderation *classifiers* (unbiased-toxic-roberta, roberta_toxicity_classifier) are ~500MB–1.5GB and run on CPU easily — keep them local; the **guardrail** model (GuardReasoner-Omni-3B) is the only new GPU cost.

> **Sovereign note**: "uncensored" models are for the *user's* sovereign right to run any model. The **Vetala module** remains the safety layer — uncensored base model + local guardrail = user control *with* integrity. This is the Omega thesis exactly.

### 5.7 Adversarial Robustness (certified defenses)
- **Certified Semantic Smoothing (CSS)** (arxiv 2602.01587): token-level stratified randomized ablation + Noise-Augmented Alignment Tuning; reduces GCG ASR 84.2%→1.2% at 94.1% benign utility; provides deterministic $l_0$ certificate [#35].
- **DCRS** (Discrete-Continuous Randomized Smoothing, OpenReview 2026): combines token-subset sampling + embedding Gaussian smoothing for finer-grained jailbreak certificates [#36].
- **CluCERT** (AAAI 2026): clustering-guided denoising smoothing; tighter bounds, lower cost [#37].
- **Feature-space Smoothing (FS)** (arxiv 2601.16200): certified robustness for MLLM feature encoders (CLIP) via Gaussian Smoothness Booster [#38].
- **Beyond Red-Teaming** (OpenReview 2605.10901): exact, O(d) certificates for guardrail classifiers by verifying the worst-case point in a convex harmful region in pre-activation space [#4].
- **Sovereign path**: certified smoothing is expensive (many forward passes). Adopt **only** as an optional, sampled (risk-routed) defense for high-stakes turns — not the per-request wall. The dual-pass obfuscation detector (`engine.py`) already catches the cheap evasion; reserve certified smoothing for the adversarial-red-team cadence (§6, PyRIT/Garak).

---

## 6. Community State-of-Art (2026)

| Tool / Framework | Type | Local / Cloud | Sovereign-aligned? | Notes |
|------------------|------|---------------|--------------------|-------|
| **NVIDIA NeMo Guardrails** | OSS (Apache 2.0) | Local (self-host) | ✅ Yes | Colang DSL; 5 rail types (input/dialog/retrieval/execution/output); reaches tool-execution layer [#39][#40] |
| **Guardrails AI** | OSS (Apache 2.0) | Local | ✅ Yes | Structured-output validation; 60+ hub validators; Pydantic-style; v0.10.0 Apr 2026 [#40][#41] |
| **LLM Guard** (Protect AI) | OSS (MIT) | Local | ✅ Yes | Scanner library: injection/PII/toxicity/code; strong PII; acquired by Palo Alto 2025 [#39][#42] |
| **Microsoft Presidio** | OSS (MIT) | Local | ✅ Yes | PII detect + anonymize (text/image/structured); best as a PII layer inside a larger stack [#39][#42] |
| **Llama Guard 3 / 4** | Open weights (Meta) | Local (model) | ⚠️ Partial | 1B/8B/12B classifier; Llama 3 Community License (commercial restrictions); slow (~0.459s), adversarially fragile [#40][#43] |
| **Rebuff** | OSS (MIT) | Local + managed API | ⚠️ Partial | Prompt-injection specialist; canary-token mechanism; managed API sends data to Rebuff servers (self-host avoids this) [#39][#42] |
| **Lakera Guard** | Commercial API | **Cloud** | ❌ No (M7 violation) | Prompt-injection/PII; acquired by Check Point 2025; routes prompts through 3rd party [#39][#42] |
| **Cleanlab** | Hosted API | **Cloud** | ❌ No | Real-time hallucination/policy validation [#42] |
| **Azure Prompt Shields / AWS Bedrock Guardrails** | Cloud-native | **Cloud** | ❌ No | Vendor-locked; zero-friction if already on Azure/AWS [#42] |
| **PyRIT** (Microsoft) | OSS (MIT) | Local | ✅ Yes | Red-team framework; 53+ datasets, 70+ converters, 6 attack strategies; v0.14.0 2026; CI-gate wrapper pattern [#44][#45] |
| **Garak** (NVIDIA) | OSS | Local | ✅ Yes | LLM vuln scanner; ~140 probes across OWASP LLM categories; structured pass/fail [#46] |
| **promptfoo** | OSS | Local (CI) | ✅ Yes | CI-oriented LLM eval; YAML tests; fail build on regression [#46] |
| **r/LocalLLaMA, TheBloke, Unsloth, llama.cpp Discord** | Community | n/a | ✅ Yes (knowledge) | Uncensored GGUF distribution, quant recipes, abliteration guides [#30][#31][#33][#34] |

**Verdict**: The sovereign-aligned stack is **NeMo Guardrails + Guardrails AI + LLM Guard + Presidio + PyRIT + Garak + promptfoo** — all self-hostable, MIT/Apache. The `omega-vetala` module should borrow the *layered* 2026 pattern: cheap broad scanner (local detectors) on every request → constitutional/structured validation → sampled multimodal classifier → continuous red-team (PyRIT/Garak in CI). Avoid Lakera/Cleanlab/cloud-native guardrails (M7).

---

## 7. Implementation Roadmap (Phased)

**Phase 0 — Rename & Package (low risk)**
- Rename `omega-moderation` → `omega-vetala` (package + import rewrites). Update `api/app.py`, `pyproject.toml`.
- Add `VetalaClient` thin wrapper exposing `moderate()` + `check_provenance()`.

**Phase 1 — Oracle + ContextBuilder wiring (high value, local-only)**
- Wire `oracle.py talk()` → pre-filter (integration #1).
- Wire `context_builder.py build_context()` → memory sanitization (#2).
- No new models; uses existing detectors.

**Phase 2 — ProvenanceSpan primitive (engine-wide)**
- Add `ProvenanceSpan` dataclass; emit spans in Oracle/ContextBuilder/ModelGateway/MemoryStore (#3, #4).
- Anchor spans into `audit.py` MMR chain (reuse `record_event`).
- Implement §2.4 anti-laundering cross-check (structural, local).

**Phase 3 — Voice + Hivemind + Soul Distiller (#5, #6, #7)**
- Iris/Nova STT/TTS moderation (local detectors only).
- Hivemind message moderation.
- Soul Distiller non-toxicity gate.

**Phase 4 — Capability expansion (optional, risk-gated)**
- Local multimodal guardrail (GuardReasoner-Omni-3B / SingGuard-3B) as `detectors/multimodal.py`.
- Constitutional `detectors/constitutional.py` (Reflect loop) reading user `constitution.yaml`.
- XAI explainer (`detectors/xai_explainer.py`, Integrated Gradients).
- C2PA manifest on export (optional).
- PyRIT/Garak red-team CI cadence (borrow the wrapper pattern from [#45]).

**Phase 5 — Advanced (future, D178 horizon)**
- Certified smoothing (CSS/DCRS) as sampled high-stakes defense.
- Federated/HE only if community WAD marketplace ships.

---

## 8. APPENDIX A — Source Citations (Official)

| # | Citation | Type |
|---|----------|------|
| 1 | OpenLineage, "AgentRunFacet RFC #4407" & "AgentAttributionRunFacet PR #4480", github.com/OpenLineage/OpenLineage, 2026. https://github.com/OpenLineage/OpenLineage/discussions/4407 | Official standard / RFC |
| 2 | OpenLineage, "Getting Started / Marquez", openlineage.io, 2026. https://openlineage.io/getting-started/ | Official standard |
| 3 | EU AI Act, Articles 12, 14, 19, 50 (high-risk logging; Aug 2026 deadlines). https://artificialintelligenceact.eu/ | Regulation |
| 4 | "Beyond Red-Teaming: Formal Guarantees of LLM Guardrail Classifiers", OpenReview 2605.10901, 2026. https://openreview.net/forum?id=… (pith.science/paper/2605.10901) | Paper (official venue) |
| 5 | Google DeepMind, "SynthID", deepmind.google/models/synthid/, 2026. https://deepmind.google/models/synthid/ | Vendor (official) |
| 6 | SynthID-Image, arxiv 2510.09263, 2026. https://arxiv.org/html/2510.09263v1 | Paper |
| 7 | C2PA, "Content Credentials Explainer (Spec 2.4)", spec.c2pa.org, 2026. https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html | Standard (official) |
| 8 | OpenAI, "Advancing content provenance", openai.com/index/advancing-content-provenance/, 2026. https://openai.com/index/advancing-content-provenance/ | Vendor (official) |
| 9 | GuardReasoner-Omni, arxiv 2602.03328, 2026. https://arxiv.org/html/2602.03328v2 | Paper |
| 10 | SingGuard, arxiv 2606.22873, 2026. https://arxiv.org/html/2606.22873v2 | Paper |
| 11 | LLaVAShield, arxiv 2509.25896 (CVPR 2026). https://arxiv.org/html/2509.25896v2 | Paper |
| 12 | Hi-Guard, arxiv 2508.03296, 2025. https://arxiv.org/html/2508.03296 | Paper |
| 13 | PromptQuorum, "Local Multimodal Pipeline 2026", promptquorum.com, 2026. | Vendor doc |
| 14 | Cliptics, "Pro Multimodal Workspace", cliptics.com, 2026. | Vendor doc |
| 15 | Presenc AI, "Hybrid Attention Models 2026: Mamba, Jamba, RWKV", 2026. https://presenc.ai/research/hybrid-attention-models-mamba-jamba-rwkv-2026 | Research org |
| 16 | Mamba-3, arxiv 2603.15569, 2026. https://arxiv.org/abs/2603.15569 | Paper |
| 17 | TildAlice, "Mamba vs RWKV 32K Benchmark", 2026. https://tildalice.io/mamba-vs-rwkv-long-context-benchmark-32k-tokens/ | Blog (technical) |
| 18 | CF-Detox, arxiv 2405.09948. https://arxiv.org/html/2405.09948v3 | Paper |
| 19 | Prompt-Counterfactual Explanations, arxiv 2601.03156, 2026. https://arxiv.org/html/2601.03156 | Paper |
| 20 | Sundararajan et al., "Axiomatic Attribution for DNNs (Integrated Gradients)", 2017. | Paper |
| 21 | Microsoft SEAL, github.com/microsoft/SEAL (MIT, v4.3.3, 2026). https://github.com/microsoft/SEAL | OSS (official) |
| 22 | TenSEAL, OpenMined, openmined.github.io/TenSEAL/ | OSS (official) |
| 23 | Keller, "MP-SPDZ", ACM CCS 2020. | Paper |
| 24 | HEAD-FL, iacr eprint 2026/1376. https://eprint.iacr.org/2026/1376 | Paper |
| 25 | SMHE, arxiv 2506.20101. https://arxiv.org/html/2506.20101v1 | Paper |
| 26 | Anthropic, "Constitutional AI", anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback, 2022. https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback | Vendor (official) |
| 27 | Anthropic, "Claude's Constitution", anthropic.com/constitution, 2026. | Vendor (official) |
| 28 | Reflect, arxiv 2601.18730, 2026. https://doi.org/10.48550/arxiv.2601.18730 | Paper |
| 29 | C3AI, arxiv 2502.15861, 2025. https://arxiv.org/html/2502.15861 | Paper |
| 30 | mradermacher/Qwen3-8B-Uncensor-v2-i1-GGUF, HuggingFace, 2026. https://huggingface.co/mradermacher/Qwen3-8B-Uncensor-v2-i1-GGUF | Model repo |
| 31 | suldanpashir/Qwen3.5-9B-Uncensored, HuggingFace, 2026. https://huggingface.co/suldanpashir/Qwen3.5-9B-Uncensored | Model repo |
| 32 | Smoffyy/Qwen3.5-4B-Instruct-Revised-GGUF, HuggingFace, 2026. https://huggingface.co/Smoffyy/Qwen3.5-4B-Instruct-Revised-GGUF | Model repo |
| 33 | richardyoung/Qwen3-14B-abliterated-GGUF, HuggingFace, 2026. https://huggingface.co/richardyoung/Qwen3-14B-abliterated-GGUF | Model repo |
| 34 | bartowski/Nemomix-v4.0-12B-GGUF, HuggingFace, 2026. https://huggingface.co/bartowski/Nemomix-v4.0-12B-GGUF | Model repo |
| 35 | Certified Semantic Smoothing (CSS), arxiv 2602.01587. https://arxiv.org/html/2602.01587v1 | Paper |
| 36 | DCRS, OpenReview 2026. https://openreview.net/forum?id=vrZwS5FQHa | Paper |
| 37 | CluCERT, AAAI 2026. https://doi.org/10.1609/aaai.v40i44.41137 | Paper |
| 38 | Feature-space Smoothing, arxiv 2601.16200. https://arxiv.org/html/2601.16200v2 | Paper |
| 39 | LLM Armor, "Open Source LLM Guardrails Comparison 2026", llmarmor.dev, 2026. | Technical blog |
| 40 | Alatirok, "LLM Guardrails Compared 2026", 2026. https://alatirok.com/llm-guardrails-compared-2026/ | Technical blog |
| 41 | Guardrails AI, github.com/guardrails-ai/guardrails (Apache 2.0). | OSS (official) |
| 42 | Infrabase, "LLM Guardrails Compared 2026", infrabase.ai, 2026. https://infrabase.ai/blog/llm-guardrails-compared | Technical blog |
| 43 | Morph, "LLM Guardrails 2026", morphllm.com, 2026. https://www.morphllm.com/llm-guardrails | Technical blog |
| 44 | Microsoft PyRIT, github.com/microsoft/pyrit (MIT), v0.14.0, 2026. https://github.com/microsoft/pyrit | OSS (official) |
| 45 | Microsoft Tech Community, "Red Teaming with PyRIT", 2026. https://techcommunity.microsoft.com/blog/appsonazureblog/securing-your-ai-agents-before-they-ship-red-teaming-with-microsoft-pyrit/4515514 | Vendor (official) |
| 46 | RingSafe, "AI Red Teaming: garak, PyRIT, OWASP LLM Top 10", 2026. https://ringsafe.in/ai-red-teaming-production-garak-pyrit-owasp-llm/ | Technical blog |
| 47 | NVIDIA NeMo Guardrails, github.com/NVIDIA/NeMo-Guardrails (Apache 2.0). | OSS (official) |
| 48 | NVIDIA Garak, github.com/NVIDIA/garak. | OSS (official) |
| 49 | OWASP, "LLM Top 10 (2025)", owasp.org. https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Standard |

---

## 9. APPENDIX B — Source Citations (Unofficial / Community)

| # | Citation | Type |
|---|----------|------|
| U1 | jsonhouse.com, "SynthID and C2PA Explained 2026", 2026. https://www.jsonhouse.com/posts/synthid-c2pa-explained-2026/ | Blog (community) |
| U2 | Presenc AI, "AI Content Watermarking Adoption 2026", 2026. https://presenc.ai/research/ai-content-watermarking-adoption-2026 | Research-org blog |
| U3 | CallSphere, "Lakera vs PromptArmor vs NeMo Guardrails 2026", 2026. https://callsphere.ai/blog/td30-fw-lakera-vs-promptarmor-vs-nemo-guardrails-2026-pick | Blog (community) |
| U4 | BeyondScale, "AI Red Teaming Tools Comparison 2026", 2026. https://beyondscale.tech/blog/ai-red-teaming-tools-comparison-2026 | Blog (community) |
| U5 | VibeReference, "AI Guardrails & LLM App Security", 2026. https://www.vibereference.com/ai-development/ai-guardrails-llm-application-security | Blog (community) |
| U6 | TildAlice, "Mamba-2 vs Griffin vs RWKV-6 SSM Benchmark", 2026. https://tildalice.io/mamba-2-griffin-rwkv-6-ssm-benchmark/ | Blog (community) |
| U7 | CallSphere, "Transformer Alternatives: Mamba, RWKV (2026)", 2026. https://callsphere.ai/blog/transformer-alternatives-mamba-rwkv-state-space-models-2026 | Blog (community) |
| U8 | iunera.com, "Top 10 Qwen Uncensored Models 2026", 2026. https://www.iunera.com/kraken/projects/top-10-qwen-uncensored-models-in-2026-which-one-should-you-actually-run-locally/ | Blog (community) |
| U9 | Data Engineer Academy, "OpenLineage and Marquez", 2026. https://dataengineeracademy.com/blog/openlineage-and-marquez-data-lineage-for-modern-pipelines/ | Blog (community) |
| U10 | Iceberg Lakehouse, "OpenLineage as the Spine of Data Observability", 2026. https://iceberglakehouse.com/posts/2026-05-24-openlineage-observability/ | Blog (community) |
| U11 | AI Security & Safety Directory, "Constitutional AI Guide 2026", 2026. https://aisecurityandsafety.org/en/guides/constitutional-ai-guide/ | Community guide |
| U12 | LessWrong, "Constitutional AI Alignment", 2026. https://www.lesswrong.com/posts/ejquSai53KymS5hHe/constitutional-ai-alignment | Forum (community) |
| U13 | r/LocalLLaMA, TheBloke, Unsloth, llama.cpp Discord — uncensored GGUF distribution & quant recipes, 2026. | Community (forum/Discord) |
| U14 | OpenLineage GitHub Discussion #4409 "Agent-level data attribution" (community-contributed extension to #4407). https://github.com/OpenLineage/OpenLineage/issues/4409 | Repo discussion (community) |

---

## 10. Cross-Links to Local Files

All paths relative to `omega-engine/` root.

| Topic | Local file | Relevance |
|-------|-----------|-----------|
| Dual-pass moderation, `ActionTier` escalation | `omega-moderation/src/omega_moderation/engine.py` | Wiring contract source; `moderate()` signature; `_max_tier` |
| Merkle-MMR + Ed25519 audit | `omega-moderation/src/omega_moderation/governance/audit.py` | ProvenanceSpan anchoring target; `record_event` / `verification_proof` |
| Zero-width / homoglyph / leetspeak | `omega-moderation/src/omega_moderation/obfuscation/detector.py` | Structural (no slur lists) obfuscation; `normalize()`, `detect_tag_attack()` |
| GDPR erasure | `omega-moderation/src/omega_moderation/governance/privacy.py` | PII redaction before storage (FIX 3) |
| ε-DP metrics | `omega-moderation/src/omega_moderation/observability/differential_privacy.py` | Local metric privacy (no HE needed for single-node) |
| FastAPI surface | `omega-moderation/src/omega_moderation/api/app.py` | `/moderate`, `/metrics`, `/api/v1/audit/verify/{index}` |
| Oracle routing (pre-filter point) | `src/omega/oracle/oracle.py` | `talk()` / `_summon()` entry; imports `TDPGate`, `PIIMasker`, `trace_id` |
| Memory injection (sanitize point) | `src/omega/oracle/context_builder.py` | `build_context()` / `_compact_and_format_exchanges()` |
| trace_id backbone | `src/omega/observability/` (`new_trace_id`, `ObservabilityEngine`) | ProvenanceSpan `trace_id` source (note: `observability.py` is a package, not a single file) |
| PII masking | `src/omega/oracle/pii_masker.py` | Complements `privacy.py` |
| Tainted-data gate | `src/omega/oracle/security.py` (`TDPGate`) | Cloud-critique quarantine; aligns with provenance trust |
| Soul distillation (non-toxic gate) | `src/omega/oracle/soul_distiller.py` | Integration #7 |
| Hivemind coordination | `mcp_servers/omega_hub/` | Integration #6 (inter-agent message moderation) |
| Model gateway (output tagging) | `src/omega/oracle/model_gateway.py` | Integration #3 |
| Memory store (exchange provenance) | `src/omega/memory_store.py` | Integration #4 |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ Jem-Analyst ⬡ trc_research ⬡ LANGUAGE-MODULE-STRATEGY — delivered 2026-07-10. No source modified. All claims cited in Appendices A/B.*
