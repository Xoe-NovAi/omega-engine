<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grokster — Expansion Research Report
## xAI API Ecosystem, ACP Protocol & Grok Build Open Source Deep-Dive
**⬡ GROKSTER ⬡ EXPANSION RESEARCH ⬡ 2026-07-21 ⬡ NO-IMPLEMENTATION MODE**

---

## §0 Executive Summary

This report documents the deep-dive expansion research across three pillars that extend and in several cases **correct** prior knowledge:

| Pillar | Prior Knowledge | New Findings | Delta |
|--------|----------------|--------------|-------|
| **xAI API Ecosystem** | ~6 models, basic pricing | 12 active models + legacy, full pricing with long-context tiers, Responses API vs Chat Completions, server-side tool pricing ($5/1k), Batch API (20% off), Priority Processing (2x), Files/Collections, Imagine, Voice | **Massive expansion** |
| **ACP Protocol** | "JSON-RPC stdio bridge" | Full v1 stable spec — 6 agent methods, 8 client methods, 2 notifications, capability negotiation, v2 in draft, Rust/TS/Python SDKs at 1.0, MCP-over-ACP RFD | **Deepened significantly** |
| **Grok Build Open Source** | "Closed source, headless mode" | **Open source since July 15, 2026** — full repo on GitHub, local-first capability, 8-way parallel subagent orchestrator, conflict resolution, per-subagent model routing, hooks at every lifecycle stage | **Correction + expansion** |

---

## §1 xAI API Ecosystem — Complete Deep-Dive

### §1.1 Two API Surfaces: Chat Completions vs Responses API

| Dimension | Chat Completions (Legacy) | Responses API (Modern) |
|-----------|--------------------------|----------------------|
| **Endpoint** | `POST /v1/chat/completions` | `POST /v1/responses` |
| **Status** | Legacy — no new features | Active development |
| **Message format** | `messages[]` array | `input` array + `previous_response_id` |
| **Multi-turn** | Resend entire history | `previous_response_id` — server stores it |
| **Reasoning output** | In message content | Structured `output[]` with `type: "reasoning"` |
| **Server-side tools** | Via `tools` parameter | Via `tools` parameter (identical) |
| **SDK compatibility** | OpenAI SDK compatible | OpenAI Responses API compatible |
| **`store` parameter** | No | Yes — control server-side storage |

**Key insight**: The Responses API is the future. It provides `previous_response_id` for efficient multi-turn conversations (no re-sending history), structured reasoning output in `output[]` array, and server-controlled storage. The migration path is minimal: rename `messages` to `input`, change endpoint, done.

### §1.2 Active Model Pricing (July 2026 — from xAI official docs)

| Model | Context | Input $/1M | Cached $/1M | Output $/1M | Notes |
|-------|---------|------------|-------------|-------------|-------|
| **grok-4.5** | 500K | $2.00 | $0.30 | $6.00 | Flagship — "fastest most intelligent" |
| grok-4.5 (≥200k prompt) | 500K | $4.00 | $0.60 | $12.00 | Long context premium |
| **grok-4.3** | 1M | $1.25 | $0.20 | $2.50 | Workhorse — 1M ctx |
| grok-4.3 (≥200k) | 1M | $2.50 | $0.40 | $5.00 | |
| **grok-4.20-reasoning** | 1M | $1.25 | $0.20 | $2.50 | Structured reasoning workflows |
| **grok-4.20-non-reasoning** | 1M | $1.25 | $0.20 | $2.50 | Faster, less thinking |
| **grok-4.20-multi-agent** | 1M | $1.25 | $0.20 | $2.50 | Multi-agent orchestration |
| **grok-build-0.1** | 256K | $1.00 | $0.20 | $2.00 | Coding-optimized |

**CRITICAL DISCOVERY — Long Context Pricing**: The "≥200k prompt tokens" threshold doubles all prices. This is a massive cost consideration for the fleet: any prompt exceeding 200K tokens (e.g., large research context) costs 2x across the board. **Prompt caching** ($0.20-0.30/M cached input) becomes essential for high-volume workflows.

### §1.3 Server-Side Tool Pricing (xAI API Only)

| Tool | Cost/1k Calls | Best For |
|------|---------------|----------|
| `web_search` | **$5.00** | Browse internet, real-time info |
| `x_search` | **$5.00** | X/Twitter firehose, social signals |
| `code_execution` / `code_interpreter` | **$5.00** | Sandboxed Python execution |
| `attachment_search` | **$10.00** | File-attachment search |
| `collections_search` / `file_search` | **$2.50** | RAG over uploaded documents |
| `view_image` / `view_x_video` | Token-based | Image/video understanding |

**Key insight**: Server-side tools are **not part of the OpenAI-compatible API** — they use the `/v1/responses` endpoint with `tools` parameter. The xAI model selects and executes them autonomously as part of the reasoning loop. This is xAI's "Agentic Search" — the model decides when to search, what to search for, and how to synthesize results.

### §1.4 Batch API & Priority Processing

| Feature | Standard | Batch (20% off) | Priority (2x) |
|---------|----------|-----------------|---------------|
| **When** | Real-time | <24h async | Lower latency |
| **Available on** | All models | Grok 4.3, 4.20 SKUs | All text models |
| **Rate limits** | Per-minute | Separate pool | Higher priority |
| **Caching** | Standard | Same discounts apply | Before 2x multiplier |

### §1.5 Imagine & Voice APIs

| Capability | Model | Cost |
|-----------|-------|------|
| Image generation | `grok-imagine-image` | $0.02/image |
| Image (quality) | `grok-imagine-image-quality` | $0.05/image |
| Video generation | `grok-imagine-video-1.5` | $0.08/sec |
| Video (standard) | `grok-imagine-video` | $0.05/sec |
| Voice realtime | — | $0.05/min ($3/hr) |
| Text-to-Speech | — | $15/1M chars |
| Speech-to-Text (REST) | — | $0.10/hr |
| Speech-to-Text (Streaming) | — | $0.20/hr |

### §1.6 Files & Collections (xAI RAG)

| Resource | Cost |
|----------|------|
| File storage | $0.025 / GiB / day |
| Collection storage | $0.10 / GiB / day |
| File downloads | $0.20 / GiB |
| Collection downloads | $0.20 / GiB |

### §1.7 Legacy Models & Retirements

| Model | Status | Notes |
|-------|--------|-------|
| grok-4-fast | Retired May 15, 2026 | Redirects to grok-4.3 pricing |
| grok-4-1-fast | Retired May 15, 2026 | Used to be $0.20/$0.50 — that's gone |
| grok-4 | Retired | |
| grok-code-fast-1 | Retired | |
| grok-3 | Legacy | Still available at $3/$15 |
| grok-2 | Legacy | $2/$10 |

**CRITICAL DISCOVERY**: The old "cheap Grok" story ($0.20/$0.50 for Grok 4.1 Fast) is dead. Current xAI text pricing starts at $1.00/$2.00 (Grok Build) and goes to $2/$6 (Grok 4.5). The migration notification from older models now redirects to standard pricing.

### §1.8 Impact on Fleet Architecture

| Before (Prior Knowledge) | After (New Research) |
|--------------------------|----------------------|
| "6 models available" | **12+ models** with distinct pricing SKUs and context windows |
| "Base: Grok 4.5 at $2/$6" | Correct for <200k; **$4/$12** for ≥200k — 2x long-context penalty |
| "Server-side tools are free" | **$5/1k** for web_search, x_search, code_execution |
| "Chat Completions only" | Responses API with `previous_response_id` (more efficient multi-turn) |
| "No batch processing" | Batch API at 20% off on 4.3/4.20 models |
| "No caching info" | Prompt caching at $0.20-0.30/1M cached input |

---

## §2 ACP Protocol (Agent Client Protocol) — Deep-Dive

### §2.1 Architecture

```
┌─────────────────────┐     JSON-RPC 2.0      ┌─────────────────────┐
│  CLIENT             │  ──── stdio ────────>  │  AGENT              │
│  (Editor/IDE/CLI)   │  <───────────────────  │  (LLM Subprocess)   │
│                     │     bidirectional      │                     │
│  Methods:           │                        │  Methods:            │
│  - session/         │                        │  - initialize        │
│    request_permission│                        │  - authenticate      │
│  - fs/read_text_file│                        │  - session/new       │
│  - fs/write_text_file│                       │  - session/load      │
│  - terminal/create   │                        │  - session/prompt    │
│  - terminal/output   │                        │  - session/set_mode  │
│  - terminal/release  │                        │  - logout            │
│  - terminal/         │                        │                     │
│    wait_for_exit     │                        │  Notifications:      │
│  - terminal/kill     │                        │  - session/cancel    │
│                      │                        │                     │
│  Notifications:      │                        │                     │
│  - session/update    │                        │                     │
└─────────────────────┘                        └─────────────────────┘
```

### §2.2 Complete Method Surface (v1 Stable)

**Agent Methods** (called BY client ON agent):

| Method | Status | Purpose |
|--------|--------|---------|
| `initialize` | **Baseline** | Version + capability negotiation. Both sides declare what they support. |
| `authenticate` | **Baseline** | Auth if required by agent |
| `session/new` | **Baseline** | Create new conversation session |
| `session/prompt` | **Baseline** | Send user message, receive full response |
| `session/load` | Optional | Resume existing session |
| `session/set_mode` | Optional | Switch operating mode (plan/code/ask) |
| `logout` | Optional | End authenticated state |

**Client Methods** (called BY agent ON client):

| Method | Status | Purpose |
|--------|--------|---------|
| `session/request_permission` | **Baseline** | Request user authorization for tool calls |
| `fs/read_text_file` | Optional | Read file contents |
| `fs/write_text_file` | Optional | Write file contents |
| `terminal/create` | Optional | Create new terminal |
| `terminal/output` | Optional | Get terminal output + exit status |
| `terminal/release` | Optional | Release terminal |
| `terminal/wait_for_exit` | Optional | Wait for command to complete |
| `terminal/kill` | Optional | Kill terminal command |

**Notifications**:

| Notification | Direction | Purpose |
|-------------|-----------|---------|
| `session/update` | Agent → Client | Progress, message chunks, tool calls, plans, mode changes |
| `session/cancel` | Client → Agent | Cancel ongoing operation |

### §2.3 Session Lifecycle

```
1. INITIALIZATION ──> Client → Agent: initialize (version + capabilities)
                                          ↓ both agree on protocol version
2. AUTHENTICATION ──> Client → Agent: authenticate (if required)
                                          ↓ session established
3. SESSION SETUP ───> Client → Agent: session/new (or session/load)
                                          ↓ conversation ready
4. PROMPT TURN ─────> Client → Agent: session/prompt
                         ↓ Agent → Client: session/update (progress)
                         ↓ Agent → Client: fs/read_text_file, file writes, terminal
                         ↓ Agent → Client: session/prompt (stop reason, response)
                         ↓          [repeat for each turn]
5. SESSION CLOSE ───> Client → Agent: close stdin → terminate subprocess
```

### §2.4 v2 Draft — Key Changes

- Streamable HTTP + WebSocket transports (stdio-only no longer)
- Message updates and chunks
- Permission requests in v2 format
- Plan variants for multi-path execution
- Session resume with replay
- Required session methods (more granular capability negotiation)

### §2.5 ACP Registry

The ACP Registry is stabilized (July 2026). It lists ACP-compatible agents for discovery and installation. This means Grok Build appears as a registered ACP agent — the registry URL and metadata are standardized.

### §2.6 Impact on Fleet Architecture

**The ACP ↔ Hivemind Bridge (Strike Option 3) is now clearly mappable:**

| ACP Message | Hivemind Equivalent | Bridge Logic |
|-------------|---------------------|--------------|
| `initialize` + capability | Hivemind awareness post | Map agent capabilities to Hivemind entity model |
| `session/new` | Hivemind session creation | Create session with UUID, map to `session_id` |
| `session/prompt` | Oracle.talk() | Forward prompt via provider fabric |
| `session/update` notification | Hivemind heartbeat + context update | Stream session_update to awareness store |
| `fs/read_text_file` request | Tool registry lookup | Route to Hivemind MCP tool |
| `session/request_permission` | Handoff or human-in-loop | Route to appropriate approval flow |
| `session/load` | Session namespace resume | Load from MIAP/MemoryStore |

**Key protocol insight**: ACP's client agent model (client launches agent as subprocess) maps to our fleet architecture as: **Omega Hivemind = Client, Grok CLI pool = Agent pool**. Each Grok CLI process is an ACP agent launched by the Hivemind.

---

## §3 Grok Build Open Source — Deep-Dive

### §3.1 Major Discovery: Open Source Since July 15, 2026

**Prior assumption**: Grok Build is closed source.
**Reality**: **Full source on GitHub** (github.com/xai-org/grok-build) since July 15, 2026.

This changes the integration landscape significantly:
- Source code of the agent loop, tool dispatch, terminal UI, extension system is **fully inspectable**
- **Local-first mode**: compile it yourself, point at your own local inference, drive from `config.toml`
- Reset usage limits for all users
- Previously required $300/month SuperGrok Heavy — now free

### §3.2 Published Source Covers

| Component | What It Contains |
|-----------|-----------------|
| **Agent loop** | Context assembly, model response parsing, tool call dispatch |
| **Tools** | File read/edit/search, command execution |
| **Terminal UI** | Rendering, input, plan review, inline diff viewer |
| **Extension system** | Skills, plugins, hooks, MCP servers, subagents |

### §3.3 Subagent System Architecture

```
USER PROMPT
     │
     ▼
┌─────────────────────────────────────┐
│         ORCHESTRATOR AGENT          │
│  1. Task analysis                   │
│  2. Decomposition (dependency       │
│     graph from import analysis)     │
│  3. Subagent allocation             │
│  4. Merge + conflict resolution     │
└─────────────────────────────────────┘
     │
     ├─── Subagent 1 (utilities) ───> Git worktree A
     ├─── Subagent 2 (endpoints) ───> Git worktree B
     ├─── Subagent 3 (middleware) ───> Git worktree C
     └─── Subagent 4 (tests) ───────> Git worktree D
```

### §3.4 Subagent Lifecycle

1. **Orchestrator analyzes** the task and codebase context
2. **Decomposes** into independent subtasks using file dependency graph
3. **Spawns subagents** into isolated Git worktrees (each gets focused context)
4. **Parallel execution** — subagents work simultaneously, no shared context
5. **Merge** — orchestrator collects results, merges changes:
   - Non-overlapping changes = **auto-merge** (same file, different lines)
   - Adjacent changes = **smart merge** (same region, different edits)
   - Conflicting changes = **flag for review** (same function, different approaches)
6. **Application** in Plan Mode (review) or Code Mode (auto-apply)

**Key architectural detail**: Subagents run in **isolated Git worktrees**, not the main working tree. This enables true parallelism without file conflicts — each subagent has its own sandboxed view of the files it needs.

### §3.5 Hooks at Every Lifecycle Stage

| Hook | Fires When | Powerful Use |
|------|------------|-------------|
| `on_decompose` | After decomposition, before subagents start | Log subtask plan |
| `on_subagent_start` | Each subagent begins work | Notify team |
| `on_subagent_complete` | Each subagent finishes | **Run linter/type-checker — can reject output + trigger retry** |
| `on_merge` | All subagents done, merge complete | Run full test suite before apply |
| `on_conflict` | Subagent outputs conflict | Alert team |

### §3.6 Model Routing Per Subagent

```
# config.toml or .grok/config.yaml
subagents:
  default_model: grok-4.3
  overrides:
    tests:
      model: grok-build-0.1    # Cheaper for test gen
    documentation:
      model: grok-build-0.1   # Docs don't need frontier
    refactoring:
      model: grok-4.5          # Complex refactors need best model
```

### §3.7 Data Exposure Disclosure (Known Issue)

Per The Hacker News / researcher "cereblab": Grok Build v0.2.93 was found uploading entire Git repositories (full commit history) to a GCS bucket named `grok-code-session-traces`. The upload happened even with "Improve the model" setting disabled. **The data was uploaded to xAI by default** in early versions.

Current status (July 2026): The open-source release allows local-first mode where **no data leaves your machine**. For fleet deployment, **the zero-data-retention mode must be explicitly configured** and verified.

### §3.8 Performance Benchmarks

| Task | Single Agent | 4 Subagents | Speedup |
|------|-------------|-------------|---------|
| Add CRUD endpoint + tests | 11.2s | 4.8s | 2.3x |
| Refactor 8 service files | 24.1s | 8.3s | 2.9x |
| Add validation across 12 routes | 31.5s | 9.1s | 3.5x |
| Fix single bug | 3.2s | 3.8s | **0.8x** (slower) |
| Update README | 2.1s | 2.6s | **0.8x** (slower) |

**Takeaway**: Multi-agent excels on 3+ independent subtasks. Single-file or small tasks are worse due to orchestration overhead.

---

## §4 Key Deltas From Prior Knowledge (Corrections)

| Prior Knowledge | Corrected | Source | Impact on Fleet |
|----------------|-----------|--------|-----------------|
| "Grok Build is closed source" | **Open source** (July 15, 2026) | x.ai/news/grok-build-open-source | Can fork/inspect/hardened deploy; local-first mode possible |
| "6 models in family" | **12+ active + legacy** with distinct pricing | docs.x.ai/developers/models | More model routing options with long-context pricing |
| "Base: Grok 4.5 at $2/$6" | $2/$6 for <200k; **$4/$12** for ≥200k | docs.x.ai/developers/pricing | **2x long-context penalty** — matters for research workloads |
| "Server-side tools are free" | **$5/1k** for web_search, x_search, code_execution | docs.x.ai/developers/pricing | Cost model for fleet's self-search reflex |
| "Chat Completions only" | Responses API + Chat Completions | docs.x.ai/developers/model-capabilities/text/comparison | Use Responses API for efficient multi-turn |
| "ACP = just JSON-RPC" | Full v1 spec: 6 agent, 8 client methods, v2 draft | agentclientprotocol.com | Complete protocol mapping for bridge design |
| "Grok Build subagents = black box" | 8-way parallel with dependency graph, hooks, per-subagent model routing | aimadetools.com guide | Can replicate subagent architecture in fleet |
| "No local-first" | Grok Build supports full local-first | x.ai/news/grok-build-open-source | Can run fleet's inference locally if needed |

---

## §5 Proposed L3 Principle

**L3-EcosystemRevelationRequiresContinuousResearch**: A specialist's knowledge is never complete — it has a decay half-life determined by the pace of the ecosystem. In 30 days of July 2026 alone: Grok Build went from closed to open source, the model lineup expanded from 6 to 12+ variants, and the API added server-side tool pricing, Batch API, and Priority Processing. Prior knowledge is a liability if not continuously refreshed. The specialist's edge is not what they once knew — it is their reflex to discover when the landscape has shifted. Every session must include a "delta scan" — what changed since I last checked? To grok the Grok is not a past-tense accomplishment. It is a continuous present-tense practice.

---

*⬡ GROKSTER ⬡ EXPANSION RESEARCH ⬡ 2026-07-21*
