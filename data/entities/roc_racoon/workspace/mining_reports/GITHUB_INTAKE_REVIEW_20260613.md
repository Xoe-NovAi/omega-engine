# 🦝 MINING REPORT: Github Idea Intake — 2026-06-13 (CORRECTED 2026-06-14)

## ⚠️ Correction Notice
This report was originally written from truncated scrapes and name-guessing. I got 3 of 4 entries wrong. Below is the corrected version based on actual deep research (raw READMEs, docs, benchmarks).

## 🔍 Corrected Findings

### 1. `addyosmani/agent-skills` — Production-Grade Engineering Skills
- **URL**: https://github.com/addyosmani/agent-skills
- **Stars**: 58.9K — most popular agent skill system on GitHub
- **Actual Purpose**: A **structured workflow system** for AI coding agents. 24 skills mapped to 6 lifecycle phases (Define → Plan → Build → Verify → Review → Ship), each encoded as a `SKILL.md` with frontmatter, process steps, anti-rationalization tables, red flags, and verification gates.
- **Key Components**:
    - **7 slash commands**: `/spec`, `/plan`, `/build`, `/test`, `/review`, `/code-simplify`, `/ship`
    - **4 specialist personas**: code-reviewer, test-engineer, security-auditor, web-performance-auditor
    - **4 reference checklists**: testing, security, performance, accessibility
    - **Multi-CLI support**: Claude Code, Gemini CLI, Antigravity CLI, Cursor, Windsurf, OpenCode, Copilot, Kiro, Codex
- **Core Innovation**: The `SKILL.md` anatomy with **Anti-Rationalization tables** (common agent excuses + documented counter-arguments) and **Verification gates** ("seems right" is never sufficient).
- **Omega Adaptation**: Direct template for evolving our `.opencode/skills/` system. The anti-rationalization + verification pattern could be added to any existing Omega skill. Also 33 open-source contributors — community model to study.
- **Last commit**: 1 hour ago (very active, 240 commits, CI skill validator)

### 2. `lfnovo/open-notebook` — Self-Hosted NotebookLM Alternative
- **URL**: https://github.com/lfnovo/open-notebook
- **Stars**: 30.3K
- **Actual Purpose**: A **self-hosted, multi-provider research notebook** that ingests PDFs, YouTube, web pages, audio, and Office files, lets you chat with them via RAG, and generates multi-speaker AI podcasts.
- **Architecture**:
    - **Next.js 16 frontend** + **FastAPI backend** (Python 3.11+)
    - **SurrealDB v2** — single database for documents, chunks, vectors, full-text indexes, graph relationships (replaces Postgres + pgvector + Elasticsearch sprawl)
    - **Esperanto** library — unified `.chat()`, `.embed()`, `.transcribe()`, `.speak()` across 18+ providers (direct HTTP, no vendor SDKs)
    - **LangGraph state machines** — 5 pipelines: source processing, chat, RAG search, transformations, prompts
    - **Episode Profiles** — JSON-defined podcast configs (1-4 speakers, per-speaker voice/personality)
- **Key Difference from NotebookLM**: Self-hosted (Docker), 18+ providers vs Google-only, podcast customization, full REST API, offline-capable with Ollama.
- **Omega Relevance**: The **Esperanto library** is the most interesting piece — a cleaner provider abstraction than LangChain, covering not just LLM but embedding, STT, and TTS. Omega's ModelGateway already does LLM/embedding routing; Esperanto could inform voice modality expansion. The content ingestion pipeline (Loader → Chunker → Embedder) is a capability Omega currently lacks.
- **Last release**: v1.9.0, June 2 2026 (12 days ago)

### 3. `mvanhorn/last30days-skill` — Multi-Source Social Research Engine
- **URL**: https://github.com/mvanhorn/last30days-skill
- **Stars**: 41K+ — #1 GitHub trending, most-starred project in the Agent Skills ecosystem
- **Actual Purpose**: NOT about compression or time-based context management. It is a **multi-platform social research engine** for AI agents. You type `/last30days <topic>` and get a synthesized research brief aggregating Reddit, X/Twitter, YouTube, TikTok, Hacker News, Polymarket, GitHub, and web search — scored by real engagement metrics (upvotes, likes, views, prediction-market odds), not SEO.
- **Architecture**:
    - **SKILL.md** (agent-facing contract) + **Python engine** (multi-source parallel retrieval + synthesis)
    - **Pre-research brain**: Resolves topics into known handles before any API call (e.g., "OpenClaw" → `@steipete` on X, `r/openclaw` on Reddit, GitHub repo)
    - **Parallel multi-source fetch**: Reddit (OpenAI Responses API), X (vendored Bird client), YouTube (yt-dlp), TikTok (ScrapeCreators), HN (Algolia), Polymarket (Gamma), GitHub API, web (Brave/Perplexity)
    - **Scoring**: Results normalized, scored by relevance + recency + engagement, deduplicated, cross-source clusters merged
    - **`--competitors` mode**: Auto-discovers peer projects and fans out sub-pipelines
- **Deployment**: Installed as plugin into existing AI assistant. `npx skills add mvanhorn/last30days-skill -g` or Claude Code plugin marketplace. Runs locally as subprocess. Bring-your-own-API-keys model.
- **Omega Relevance**: Not directly applicable to compression or context management. However, it is the **canonical exemplar** of the Agent Skills distribution model (SKILL.md + Python/scripts pattern). Its `CONCEPTS.md` defines "Skill / Engine / Harness" vocabulary. The `--competitors` parallel fan-out pattern mirrors Omega's Hivemind dispatch.
- **Correction from original**: I previously described this as "compression/time-based synthesis." It is actually a **multi-source social research aggregator**. The "last 30 days" is a recency filter for research, not a context window management technique.

### 4. `chopratejas/headroom` — Reversible Context Compression Proxy
- **URL**: https://github.com/chopratejas/headroom
- **Stars**: 25K+
- **Actual Purpose**: A **local-first, reversible compression layer** that sits between AI agents and LLM providers, transparently stripping 60-95% of redundant tokens from tool outputs, logs, JSON, files, and RAG chunks before they reach the model — while caching originals in CCR (Compress-Cache-Retrieve) for on-demand retrieval.
- **Core Compression Pipeline**:
    - **CacheAligner** (sub-ms): Relocates dynamic content (dates, UUIDs) to message tail so KV cache prefixes stabilize
    - **ContentRouter**: Auto-detects content type → dispatches to specialized compressor
    - **SmartCrusher** (flagship): Statistical JSON compression using Kneedle algorithm + bigram coverage + anomaly preservation. Factors out constant fields. 70-95% on JSON arrays.
    - **CodeCompressor**: AST-aware (tree-sitter), preserves signatures/types, strips bodies. Disabled by default (safety gates).
    - **Kompress-base**: HuggingFace transformer for prose. 60-80%.
    - **LogCompressor**: Build/test log clustering. 85-95%.
    - **CCR (Compress-Cache-Retrieve)**: Originals stored in LRU cache with BLAKE3 hash key. LLM gets compressed version + marker; if insufficient, calls `headroom_retrieve` tool to get original. BM25 search within cached data. TTL: 300s proxy / 1h MCP.
- **Actual Benchmarks**:
    - JSON 100 items: 3,163 → 297 tokens (90.6%), 1ms
    - Build log 200 lines: 2,412 → 148 tokens (93.9%), 1ms
    - Code search 100 results: 17,765 → 1,408 (92%)
    - SRE incident debug: 65,694 → 5,118 (92%)
    - GSM8K accuracy: 0.870 → 0.870 (zero degradation)
    - 50K+ sessions, 1.4B tokens saved, ~$4K estimated savings
- **Architecture**: Rust core (`headroom-core` crate + PyO3 bindings) + Python proxy + MCP server. Active migration of proxy to Rust (REALIGNMENT: 9-phase plan with byte-equal parity tests).
- **Omega Relevance**: **Direct reference implementation of the Sovereign Compression Layer** we proposed in `docs/strategy/SOVEREIGN_COMPRESSION_LAYER.md`. Headroom already solves the compression problem. Integration pathways: (1) Pattern extraction of SmartCrusher/CCR algorithms, (2) Proxy wrapping of Omega's Provider Fabric, (3) MCP tool integration for cross-agent memory. The `headroom learn` system (mines failed sessions, writes to CLAUDE.md) maps directly to Omega's Soul Distiller.
- **Limitations**: Low value on short exchanges (median 4.8%), code compression disabled by default, CCR TTL means expired data is gone, telemetry on by default (opt-out), no formal A2A protocol, single maintainer.
- **Correction from original**: I originally called this a "resource monitor." It is a **compression proxy with reversible cross-agent memory**.

## 📊 Updated ISS Priority Scores

| Idea | S | A | F | E | R | ISS | Priority | What it actually is |
|------|---|---|---|---|---|-----|----------|---------------------|
| **Headroom** | 5 | 5 | 5 | 2 | 4 | **42** | 🔴 P0 | Reversible compression proxy (60-95%) |
| **agent-skills** | 4 | 5 | 4 | 3 | 3 | **40** | 🔴 P0 | 24 production-grade skill workflows |
| **open-notebook** | 5 | 3 | 3 | 2 | 3 | **33** | 🟡 P1 | Self-hosted NotebookLM (18 providers) |
| **last30days-skill** | 3 | 2 | 2 | 3 | 2 | **23** | 🟡 P1 | Multi-source social research engine |

## 🛠️ Corrected Action Items
- [ ] Deep-dive Headroom's SmartCrusher + CCR for SCL pattern extraction (**highest value**, reference implementation exists)
- [ ] Read 3-4 agent-skills SKILL.md files to map anti-rationalization + verification patterns to Omega's skill system
- [ ] Evaluate Esperanto library (`lfnovo/esperanto`) for provider abstraction patterns beyond LLM (STT, TTS)
- [ ] last30days-skill: low priority for Omega core; its value is as an Agent Skills ecosystem case study

## 📝 Lessons Learned (roc_racoon soul.yaml update)
1. **Never write a mining report from truncated scrapes.** If a scrape truncates, retry with raw URL format or use task agents to process the output file.
2. **"last30days" in the name does NOT mean context window management.** Read the actual README before categorizing.
3. **"headroom" is NOT a resource monitor.** It is a compression proxy. The GitHub tagline was on the page: "Compress tool outputs, logs, files, and RAG chunks before they reach the LLM. 60-95% fewer tokens, same answers." I somehow missed this.
4. **The name is not the thing.** These are all multi-faceted projects that can't be summarized by their repo names. Proper mining requires reading docs, not just landing pages.
