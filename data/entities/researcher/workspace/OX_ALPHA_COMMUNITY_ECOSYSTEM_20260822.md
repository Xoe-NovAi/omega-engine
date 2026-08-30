<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# Ox Alpha Community Ecosystem & Vision Capabilities Research
**AP Token**: `AP-RESEARCHER-OXALPHA-VISION-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_oxalpha_vision ⬡ ACTIVE
**Date**: 2026-08-22
**Mission**: Deep research on Ox Alpha community ecosystem & vision capabilities for Omega Engine integration

---

## 🏛️ COUNCIL OF FOUR — DIALECTIC SYNTHESIS

### 🏛️ ARCHITECT (Systemic Logic)
**Integration Patterns Observed**: Ox Alpha integrates via OpenAI-compatible Chat Completions API across multiple agent harnesses (OpenCode Zen, Hermes Agent, Claude Code, Zed Editor). The 1M context window enables whole-repository coding workflows. Provider routing (OpenRouter stealth slot) allows zero-config fallback chains.

**Vision Pipeline Architecture**: CogViT vision encoder → NaFlex variable-resolution preprocessing → Multimodal Multi-Token Prediction (MMTP) → Joint RL across 30+ task types (STEM, grounding, video, GUI agents, coding agents) → Tool calling + structured output. Video tokenization uses FPS-invariant sampling (~147 tokens/sec) + per-frame resolution scaling.

**Omega Adoption Path**: Add `stealth/ox-alpha` as routed tier in Provider Fabric (priority 3-4, behind local-first). Implement vision preprocessing shim for CogViT-compatible frame extraction. Build fallback to GLM-5V-Turbo (Z.ai official) when preview ends.

---

### ⚔️ ADVERSARY (Critical Rigor)
**Vision Limitations**:
- **Hallucination risk**: Video understanding benchmarks (MVBench +5.6% from RL) still show gaps in temporal reasoning
- **Context pollution**: Video tokens consume shared 202K/1M context pool — long videos starve text reasoning
- **No independent benchmarks**: Ox Alpha has zero Artificial Analysis leaderboard entry; all numbers community-measured
- **Rate limit impact**: Video = massive token consumption (147 tokens/sec × 60 sec = ~8.8K tokens/minute). Free preview has soft RPM limits
- **Audio rejection**: Cannot process audio tracks — limits video use cases requiring narration analysis

**Community Tool Quality**:
- **Hermes Agent**: Production-grade, open-source, Nous Research backed
- **OpenCode Zen**: Primary harness, but Ox Alpha reliability degrades under peak load (stall-echo artifact)
- **Claude Code**: Major traffic (9.3B tokens) but Anthropic-owned — not community
- **Most "projects" are integrations, not standalone applications**: Ecosystem is harness-centric, not app-centric

**Security Risks**:
- Anonymous provider retains logs (OpenRouter stealth terms)
- Zero Data Retention claim only on OpenCode Zen route
- No enterprise agreement — unsuitable for PII/production secrets

---

### 🧪 ALCHEMIST (Creative Synthesis)
**Omega-Specific Vision Leverage**:
| Use Case | Description | Implementation Approach | Priority |
|----------|-------------|------------------------|----------|
| **Screenshot-to-Code** | Omega Engine UI dev: screenshot → React/Vue/Svelte component | Ox Alpha + OpenCode Zen harness; feed UI screenshots, get component code | 🔴 P0 |
| **Architecture Diagram → Mermaid** | Whiteboard photos / Confluence diagrams → Mermaid/PlantUML for docs | Vision prompt: "Convert this architecture diagram to Mermaid with clickable nodes" | 🔴 P0 |
| **Legacy Codebase Screenshots → Docs** | Photograph legacy terminal/code → auto-generate documentation | Batch process screenshots through Ox Alpha 1M context; aggregate into knowledge base | 🟡 P1 |
| **Video Tutorials → Knowledge Base** | Record Omega workflow demos → distill into HALL_OF_RECORDS entries | Video input → structured summary → L1/L2/L3 distillation pipeline | 🟡 P1 |
| **Visual Regression Testing** | WAD/stack UI screenshots → diff analysis → alert on drift | Scheduled captures → Ox Alpha "compare these two UI screenshots" → JSON diff | 🟡 P1 |
| **Entity Relationship Maps** | Diagram screenshots → YAML entity definitions + resonance mappings | Vision → structured extraction → soul.yaml patch generation | 🟢 P2 |
| **GUI Agent Automation** | Ox Alpha + OpenClaw/Claude Code for browser-based Omega admin tasks | Native GUI agent benchmarks (AndroidWorld, WebVoyager leader) | 🟢 P2 |

**Cross-Pollination**: GLM-5V-Turbo's "perceive → plan → execute" loop maps directly to Omega's Oracle → Iris → ModelGateway flow. Vision adds the "perceive" layer for visual environments.

---

### 📜 ARCHIVIST (Historical Truth)
**Zhipu/GLM Vision Lineage**:
- **GLM-4V** (2024): Image input only, bolted-on vision
- **GLM-5** (Feb 2026): Text-only, 1M context, MoE (744B/40B)
- **GLM-5V-Turbo** (Apr 2026): Native multimodal agent, CogViT encoder, 202K context, 30+ task RL
- **GLM-5.3** (Aug 14, 2026): Text-only, 1M context, improved coding
- **Ox Alpha** (Aug 20, 2026): Stealth release, 1M context + video, fingerprint = GLM-5.3 multimodal variant

**Prior Art Comparison**:
| Model | Context | Video | Design2Code | GUI Agent | Price (in/out) |
|-------|---------|-------|-------------|-----------|----------------|
| **GLM-5V-Turbo** | 202K | ✅ | 94.8 | AndroidWorld/WebVoyager leader | $1.20/$4.00 |
| **GPT-4o** | 128K | ✅ | ~77 | WebVoyager strong | $2.50/$10.00 |
| **Claude 3.5 Sonnet** | 200K | ✅ | 77.3 | Computer Use API | $3.00/$15.00 |
| **Gemini 1.5 Pro** | 2M | ✅ | ~75 | Strong video reasoning | $1.25/$5.00 |
| **Ox Alpha** | 1M | ✅ | ~94 (est) | Strong (est) | **FREE (preview)** |

**Chinese AI Ecosystem Priorities**: Vision-first agent workflows (design-to-code, GUI automation) over general chat. Z.ai's "multimodal coding foundation model" positioning reflects this.

---

## 📋 COMMUNITY PROJECTS CATALOG

| Project | Category | Repo/Link | Maturity | Key Tech | Omega Relevance |
|---------|----------|-----------|----------|----------|-----------------|
| **Hermes Agent** | Autonomous Coding Agent | `github.com/NousResearch/hermes-agent` / `github.com/evangit2/hermes-opencode` | Production (open-source, self-improving) | Provider-agnostic, skills system, multi-platform messaging, OpenCode integration | Primary reference for Ox Alpha agentic workflows; 9B tokens on Ox Alpha |
| **OpenCode / OpenCode Zen** | Coding Agent Harness | `github.com/opencode-ai/opencode` | Production (core Omega interface) | TUI/CLI, provider-agnostic, `x-preview-f-free` model ID for Ox Alpha | Native Omega interface; Ox Alpha = default free tier |
| **Claude Code** | Coding Agent (Anthropic) | `github.com/anthropics/claude-code` | Production (closed-source) | Native tool use, 9.3B tokens on Ox Alpha | Major traffic validator; routing pattern reference |
| **Zed Editor** | IDE with AI Integration | `github.com/zed-industries/zed` | Production | Native AI assistant, Ox Alpha integration | Editor-level integration pattern |
| **GLM-5 Official Repo** | Model Ecosystem / Skills | `github.com/zai-org/GLM-5` (7K⭐) | Official (Z.ai) | Skills for OpenClaw, AutoClaw, Claude Code; deployment cookbooks (SGLang, vLLM, KTransformers) | Official skills = integration blueprints |
| **GLM-5V-Turbo Skills** | Vision Agent Skills | `clawhub.ai/jaredforreal/glm-master-skill` | Official (Z.ai) | 5 vision skills: OCR, Image understanding, GUI agent, Web reading, Design-to-code | Direct vision integration patterns |
| **CogViT Implementation** | Vision Encoder (Open) | `github.com/kyegomez/cogvit` | Experimental (community port) | PyTorch implementation of GLM-5V-Turbo vision encoder | Local vision encoder research / distillation target |
| **Oh-My-Pi** | Agent Harness | Community | Active | Ox Alpha top-5 traffic source | Alternative harness pattern |
| **DeepSeek Harness** | Agent Harness | Community | Active | Ox Alpha top-5 traffic source | Alternative harness pattern |
| **Z Code** | Agent Harness | Community | Active | Ox Alpha top-5 traffic source | Alternative harness pattern |

**Maturity Assessment**: Ecosystem is **harness-centric** not app-centric. No standalone "Ox Alpha applications" exist yet — all usage flows through coding agent harnesses. This is a **feature**, not a bug: Ox Alpha is positioned as a **model layer** for agentic workflows.

---

## 🔬 VISION CAPABILITY TECHNICAL SPECIFICATION

| Aspect | Specification | Source |
|--------|---------------|--------|
| **Model Identity** | Ox Alpha = Stealth preview of GLM-5.3 multimodal variant (90% confidence via tokenizer + video encoder fingerprinting). GLM-5V-Turbo = Official Z.ai release (Apr 2026). | explainx.ai, kocpc.com.tw, BigGo, arxiv:2604.26752 |
| **Input Modalities** | Text, Image (JPEG, PNG, WebP), Video (MP4, WebM), File (PDF, etc.) | oxalpha.io, docs.z.ai, OpenRouter |
| **Output Modality** | Text only (reasoning + structured output) | All sources |
| **Context Window** | Ox Alpha: 1,048,576 tokens (1M) \| GLM-5V-Turbo: 202,752 tokens | oxalpha.io, OpenRouter, docs.z.ai |
| **Max Output** | 131,072 tokens (both) | All sources |
| **Vision Encoder** | **CogViT** — novel parameter-efficient ViT, 2-stage pretraining: (1) Distillation-based MIM (SigLIP2 + DINOv3 teachers, 35% masking, 224×224) → (2) Contrastive image-text (NaFlex variable resolution, 64K batch, 8B bilingual corpus) | arxiv:2604.26752 §2.1 |
| **Video Tokenization** | **FPS-invariant frame sampling** + **~147 tokens/second duration scaling** + **Per-frame resolution scaling** — 3 independent design choices matching exactly between Ox Alpha and GLM-5V-Turbo | explainx.ai, kocpc.com.tw, BigGo |
| **Video Token Cost** | ~147 tokens/second of video (duration scaling) + per-frame resolution overhead | Fingerprinting evidence |
| **Image Token Cost** | Variable via NaFlex (preserves aspect ratio); typical ~256-1024 tokens/image depending on resolution | CogViT NaFlex design |
| **API Format** | OpenAI-compatible Chat Completions (`/v1/chat/completions`), `image_url` / `video_url` in message content, `reasoning_effort: "max"` default | oxalpha.io, glm5.app, docs.z.ai |
| **Function Calling** | Full support, OpenAI-compatible tool schema | All sources |
| **Streaming** | Supported (SSE) | All sources |
| **Structured Output** | JSON mode supported | docs.z.ai, Puter.js |
| **Reasoning** | Mandatory (reasoning effort controls exposed on some routes) | oxalpha.io, explainx.ai |
| **Pricing (GLM-5V-Turbo)** | Input: $1.20/M \| Output: $4.00/M \| Cached: $0.24/M | docs.z.ai, OpenRouter, Puter.js ($0.79/$3.44) |
| **Pricing (Ox Alpha)** | **FREE** ($0/$0) during preview (ends ~Aug 27, 2026) | OpenRouter, oxalpha.io |
| **Rate Limits** | Soft RPM limits under peak load; "100T tokens/day capacity" claimed | PLATFORM_GROUND_TRUTH_LOG.md #87 |
| **Audio Support** | **Rejected** — no audio endpoints (matches GLM-5V family, rules out MiMo) | Fingerprinting evidence |
| **Tokenizer** | Matches GLM-5.3 exactly (+75 token constant offset = system wrapper) | dax @thdxr, Ben Davis, explainx.ai |
| **Knowledge Cutoff** | ~November 2025 | Fingerprinting evidence |
| **Architecture** | 744B total params, 40B active (MoE), INT8 quantization, MTP (Multi-Token Prediction) | wavespeed.ai, BigGo |
| **Training** | 30+ task joint RL: STEM, grounding, video, GUI agents, coding agents | arxiv:2604.26752, docs.z.ai |

---

## 📊 VISION BENCHMARKS

| Benchmark | GLM-5V-Turbo Score | Comparison | Notes |
|-----------|-------------------|------------|-------|
| **Design2Code** | **94.8** | Claude Opus 4.6: 77.3 | SOTA for UI→code generation |
| **AndroidWorld** | **Leader** | Beats Claude Opus 4.5 | GUI agent navigation |
| **WebVoyager** | **Leader** | Beats Claude Opus 4.5 | Web agent tasks |
| **BrowseComp** | **> Claude Opus 4.5** | Agentic browsing | |
| **MVBench** (video) | **+5.6% vs SFT** | Video understanding | RL improvement |
| **RefCOCO-avg** (grounding) | **+4.8% vs SFT** | 2D pointing/grounding | |
| **PointBench** | **+3.2% vs SFT** | Fine-grained pointing | |
| **DeepSWE** (Ox Alpha) | **80% Pass@1** (8/10) | GLM-5.3: 62%, Claude Fable 5: 65%, GPT-5.6-sol: 52% | Community-measured, small sample |
| **Artificial Analysis Intelligence Index** | **35.3** (87th pct) | Median: 17 | Reasoning version |
| **GPQA Diamond** | **80.9** (78th pct) | | |
| **Tau-2 Tool Use** | **98.5%** | Matches GLM-5-Turbo | Vision didn't degrade tool use |
| **IFBench** (instruction following) | 61.1% | GLM-5-Turbo: 73.2% | Text-only sibling better |

---

## 🎯 VISION USE CASES FOR OMEGA ENGINE

| Use Case | Description | Implementation Approach | Priority | Effort |
|----------|-------------|------------------------|----------|--------|
| **Screenshot-to-Code (Omega UI)** | Feed UI screenshots/mockups → generate React/Vue/Svelte components for Omega Engine stacks | Ox Alpha via OpenCode Zen harness; prompt: "Generate a React component matching this screenshot, using Omega Engine design tokens" | 🔴 P0 | 2-3 days |
| **Architecture Diagram → Mermaid/PlantUML** | Whiteboard photos, Confluence diagrams, ASCII art → executable Mermaid for docs | Vision prompt: "Convert to Mermaid with clickable nodes, preserve hierarchy, output .mmd" | 🔴 P0 | 1-2 days |
| **Legacy Codebase Screenshots → Documentation** | Photograph terminal sessions, legacy IDE screens → auto-generate markdown docs | Batch process via Ox Alpha 1M context; aggregate into `data/knowledge/` | 🟡 P1 | 3-5 days |
| **Video Tutorials → Knowledge Base** | Record Omega workflow demos (5-10 min) → distill into HALL_OF_RECORDS entries | Video input → structured summary → L1/L2/L3 distillation → `soul.yaml` lessons | 🟡 P1 | 3-5 days |
| **Visual Regression Testing (WAD UIs)** | Scheduled UI captures → diff analysis → alert on drift | Cron + Playwright screenshots → Ox Alpha "compare these two screenshots, output JSON diff" | 🟡 P1 | 2-3 days |
| **Entity Relationship Maps** | Diagram screenshots → YAML entity definitions + resonance mappings | Vision → structured extraction → `soul.yaml` patch + `resonance_mappings.yaml` update | 🟢 P2 | 3-4 days |
| **GUI Agent Automation** | Ox Alpha + OpenClaw/Claude Code for browser-based Omega admin (dashboard, deployments) | Native GUI agent benchmarks leader; integrate via Z.ai official skills | 🟢 P2 | 5-7 days |
| **Code-from-Screenshot (Rapid Prototyping)** | Hand-drawn wireframes / Figma exports → working Omega stack prototypes | Vision + code generation in single 1M context call | 🟢 P2 | 2-3 days |
| **Document Analysis (PDF/Images)** | Technical PDFs, scanned docs → structured knowledge extraction | File input + vision → RAG ingestion pipeline | 🟢 P2 | 2-3 days |

---

## ⚠️ CRITICAL CAVEATS & RISKS

1. **Identity Unconfirmed**: Ox Alpha = GLM-5.3 multimodal variant at ~90% confidence (fingerprinting), NOT official confirmation. Zhipu silent.
2. **Preview Window**: Free tier ends ~Aug 27, 2026 (1 week from Aug 20 launch). Plan for paid fallback (GLM-5V-Turbo $1.20/$4.00).
3. **Privacy**: Anonymous provider retains logs (OpenRouter stealth terms). OpenCode Zen claims zero retention. **Do not send PII/secrets**.
4. **Reliability**: Stall-echo artifact (provider-side stream truncation → partial output re-injected as user turn). Cognitive corruption risk. See `PLATFORM_GROUND_TRUTH_LOG.md` #10, #170-177.
5. **No Independent Benchmarks**: Ox Alpha absent from Artificial Analysis, LMSYS, etc. All numbers community-measured.
6. **Context ≠ Reasoning Depth**: 1M tokens capacity ≠ effective long-context reasoning. No RULER/Lost-in-Middle tests run.
7. **Single Provider Risk**: Only OpenRouter (stealth) + OpenCode Zen + Mercury Cloud. No multi-provider redundancy yet.

---

## 🔗 SOURCES & EVIDENCE CHAIN

| # | Source | Type | Key Claims |
|---|--------|------|------------|
| 1 | `explainx.ai/blog/openrouter-ox-alpha-stealth-model-august-2026` | Analysis | Specs, traffic stats, privacy caveats, routing patterns |
| 2 | `explainx.ai/blog/ox-alpha-what-we-know-mystery-ai-model-august-2026` | Forensics | Tokenizer (25 prompts) + video encoder (4 videos) fingerprinting = 90% GLM-5.3 |
| 3 | `orcarouter.ai/blog/ox-alpha-stealth-model-what-we-know` | Analysis | DeepSWE 80%, tokenizer/video encoder forensics, geopolitical framing |
| 4 | `kocpc.com.tw/archives/24693` | Chinese tech media | Triple verification (tokenizer, video encoder, audio refusal) |
| 5 | `finance.biggo.com/news/...` | Financial news | Ben Davis 99% certain, DeepSWE 80%, video encoder 147 tokens/sec |
| 6 | `arxiv.org/html/2604.26752v1` | Technical paper | CogViT, MMTP, 30+ task RL, VBVR benchmark, architecture |
| 7 | `docs.z.ai/guides/vlm/glm-5v-turbo` | Official docs | Capabilities, API, pricing, benchmarks, skills |
| 8 | `oxalpha.io` | Official landing | Specs, API docs, use cases, FAQ |
| 9 | `glm5.app/blog/ox-alpha-openrouter` | Community guide | Model ID, pricing, API setup, reasoning settings |
| 10 | `wavespeed.ai/blog/posts/glm-5v-turbo-developers-2026` | Developer guide | Design-to-code, pricing, API, benchmarks |
| 11 | `github.com/zai-org/GLM-5` | Official repo | Skills, deployment, cookbooks (7K⭐) |
| 12 | `PLATFORM_GROUND_TRUTH_LOG.md` | Omega internal | Ox Alpha reliability profile, stall-echo, thinking-level correlation |

---

## 📝 SESSION GNOSIS (L1→L2→L3)

**L1 Narrative**: Researched Ox Alpha (stealth model on OpenRouter, launched Aug 20, 2026) and its vision capabilities. Found strong forensic evidence (tokenizer + video encoder fingerprinting) that Ox Alpha is a hidden multimodal variant of Zhipu AI's GLM-5.3, matching GLM-5V-Turbo's video tokenization exactly (FPS-invariant sampling, 147 tokens/sec, per-frame resolution scaling). Community ecosystem is harness-centric: Hermes Agent, OpenCode Zen, Claude Code, Zed Editor drive billions of tokens. Vision benchmarks show SOTA Design2Code (94.8) and GUI agent leadership.

**L2 Insight**: Ox Alpha is a **time-boxed opportunity** — free 1M-context multimodal model for agentic coding workflows. The vision pipeline (CogViT + MMTP + 30-task RL) is purpose-built for "perceive → plan → execute" loops, aligning perfectly with Omega's Oracle → Iris → ModelGateway architecture. However, the stall-echo artifact (provider-side stream truncation re-injecting partial output as user turns) is a **cognitive integrity hazard** requiring agent-level inoculation.

**L3 Universal Principle**: **Free preview tiers from anonymous providers are tactical assets, not strategic dependencies.** The correct pattern: route high-volume/low-stakes workloads (agent loops, video analysis, spikes) through the preview while maintaining a verified fallback (GLM-5V-Turbo official API) behind a routing layer. Never architect production secrets or cognitive integrity around unverified infrastructure.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_oxalpha_vision ⬡ COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
