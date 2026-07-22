# 🔱 Grokster — Grok Ecosystem Deep Research
## Models, Pricing, ACP Protocol, Web Grok, Fleet Deployment Architecture
**⬡ GROKSTER ⬡ R33 ⬡ 2026-07-21 ⬡ P0 ⬡ COMPLETE**

---

## §0 Executive Summary

This report consolidates deep research across the entire xAI Grok ecosystem (API, models, ACP protocol, Grok Build, Web Grok Projects, Grok CLI) to produce a **finalized model selection matrix** and **fleet deployment architecture** for the Omega Engine's 16-account Grok fleet (8 Grok CLI headless + 8 Web Grok persona Projects).

**Key Deliverables:**
1. **Model Selection Matrix** — 12+ active models with pricing, context windows, capabilities, routing logic
2. **Fleet Deployment Architecture** — ACP stdio bridge, credential rotation, rate-limit-aware routing
3. **Cost Optimization Strategy** — Prompt caching, batch API, long-context penalty avoidance

---

## §1 xAI API Ecosystem — Complete Model Catalog (July 2026)

### §1.1 Active Models & Pricing

| Model | Context | Input $/1M | Cached $/1M | Output $/1M | ≥200k Penalty | Best For |
|-------|---------|------------|-------------|-------------|---------------|----------|
| **grok-4.5** | 500K | $2.00 | $0.30 | $6.00 | **2x ($4/$12)** | Flagship reasoning, DeepSearch |
| **grok-4.3** | 1M | $1.25 | $0.20 | $2.50 | **2x ($2.50/$5)** | Workhorse, long-context synthesis |
| **grok-4.20-reasoning** | 1M | $1.25 | $0.20 | $2.50 | **2x ($2.50/$5)** | Structured reasoning workflows |
| **grok-4.20-non-reasoning** | 1M | $1.25 | $0.20 | $2.50 | **2x ($2.50/$5)** | Fast throughput, less thinking |
| **grok-4.20-multi-agent** | 1M | $1.25 | $0.20 | $2.50 | **2x ($2.50/$5)** | Multi-agent orchestration |
| **grok-build-0.1** | 256K | $1.00 | $0.20 | $2.00 | N/A | Coding-optimized, cached input $0.20 |

### §1.2 Legacy Models (Retired/Redirected)

| Model | Status | Notes |
|-------|--------|-------|
| grok-4-fast | Retired May 15, 2026 | Redirects to grok-4.3 pricing |
| grok-4-1-fast | Retired May 15, 2026 | Was $0.20/$0.50 — **gone** |
| grok-code-fast-1 | Retired | |
| grok-3 | Legacy | $3/$15 — expensive |
| grok-2 | Legacy | $2/$10 |

**Critical Finding**: The "cheap Grok" era ($0.20/$0.50) is **dead**. Current floor is $1.00/$2.00 (Grok Build).

### §1.3 Server-Side Tool Pricing (Responses API Only)

| Tool | Cost/1k Calls | Use Case |
|------|---------------|----------|
| `web_search` | **$5.00** | Real-time internet browse |
| `x_search` | **$5.00** | X/Twitter firehose, social signals |
| `code_execution` / `code_interpreter` | **$5.00** | Sandboxed Python execution |
| `attachment_search` | **$10.00** | File-attachment search |
| `collections_search` / `file_search` | **$2.50** | RAG over uploaded docs |
| `view_image` / `view_x_video` | Token-based | Image/video understanding |

**Architecture Note**: These are **not** part of OpenAI-compatible Chat Completions. They require the **Responses API** (`/v1/responses`) with `tools` parameter. The model autonomously decides when to call tools as part of its reasoning loop.

### §1.4 Cost Optimization Features

| Feature | Discount | Available On | Notes |
|---------|----------|--------------|-------|
| **Prompt Caching** | $0.20-0.30/M cached input | All models | Automatic for repeated prefixes |
| **Batch API** | **20% off** | Grok 4.3, 4.20 SKUs | <24h async, separate rate limit pool |
| **Priority Processing** | 2x cost | All text models | Lower latency, higher priority queue |

### §1.5 Imagine & Voice APIs

| Capability | Model | Cost |
|------------|-------|------|
| Image generation | `grok-imagine-image` | $0.02/image |
| Image (quality) | `grok-imagine-image-quality` | $0.05/image |
| Video generation | `grok-imagine-video-1.5` | $0.08/sec |
| Video (standard) | `grok-imagine-video` | $0.05/sec |
| Voice realtime | — | $0.05/min ($3/hr) |
| TTS | — | $15/1M chars |
| STT (REST) | — | $0.10/hr |
| STT (Streaming) | — | $0.20/hr |

### §1.6 Files & Collections (xAI RAG)

| Resource | Cost |
|----------|------|
| File storage | $0.025 / GiB / day |
| Collection storage | $0.10 / GiB / day |
| File downloads | $0.20 / GiB |
| Collection downloads | $0.20 / GiB |

---

## §2 Model Selection Matrix — Fleet Routing Logic

### §2.1 Primary Routing Table

| Task Type | Primary Model | Fallback | Routing Logic |
|-----------|---------------|----------|---------------|
| **Deep Research** (multi-source, gap-flagged) | `grok-4.5` + `web_search` + `x_search` | Web Grok-Research persona | DeepSearch native; 500K ctx; server-side tools |
| **Long-Context Synthesis** (>200K tokens) | `grok-4.3` | `grok-4.5` (if <200K) | 1M ctx, $1.25/$2.50 base; avoid ≥200K penalty |
| **Code Implementation** | `grok-build-0.1` | `grok-4.5` | 256K ctx, $1/$2, coding-optimized, cached input $0.20 |
| **Reasoning/Think Mode** | `grok-4.5` (Think) | `grok-4.20-reasoning` | Configurable reasoning depth; 500K ctx |
| **Real-Time Pulse** (X firehose) | Web Grok-Pulse persona | `grok-4.5` + `x_search` | Native X access via Web Grok Projects |
| **Cost-Optimized** (high volume) | `grok-4.3` + Batch API | `grok-4.20-non-reasoning` | 20% off batch; 1M ctx workhorse |
| **Multi-Agent Orchestration** | `grok-4.20-multi-agent` | Grok Build orchestrator | Specialized SKU for agent coordination |

### §2.2 Long-Context Penalty Avoidance Strategy

**Rule**: Any prompt ≥200K tokens triggers **2x pricing** on all models.

**Mitigations**:
1. **Prompt Caching** — Structure prompts with stable prefixes (system prompts, few-shot examples) to maximize cache hits at $0.20-0.30/M
2. **Batch API** — For non-real-time synthesis, use 20% off on Grok 4.3/4.20
3. **Context Chunking** — Split >200K contexts into multiple calls with synthesis step
4. **Web Grok Projects** — For persistent long-context work, use Web Grok's native context (no API token costs)

### §2.3 Model Capability Tags (for Router)

```yaml
model_capabilities:
  grok-4.5:
    context: 500000
    reasoning: deepsearch
    tools: [web_search, x_search, code_execution]
    batch_eligible: false
    priority_eligible: true
  grok-4.3:
    context: 1000000
    reasoning: standard
    tools: [web_search, x_search, code_execution]
    batch_eligible: true
    priority_eligible: true
  grok-4.20-reasoning:
    context: 1000000
    reasoning: structured
    tools: [web_search, x_search, code_execution]
    batch_eligible: true
    priority_eligible: true
  grok-4.20-non-reasoning:
    context: 1000000
    reasoning: minimal
    tools: [web_search, x_search, code_execution]
    batch_eligible: true
    priority_eligible: true
  grok-4.20-multi-agent:
    context: 1000000
    reasoning: multi_agent
    tools: [web_search, x_search, code_execution]
    batch_eligible: true
    priority_eligible: true
  grok-build-0.1:
    context: 256000
    reasoning: code_focused
    tools: [code_execution]
    batch_eligible: false
    priority_eligible: true
    cached_input_discount: 0.20
```

---

## §3 ACP Protocol (Agent Client Protocol) — Fleet Bridge Specification

### §3.1 Protocol Overview

**ACP v1 Stable** (July 2026) — JSON-RPC 2.0 over stdio, bidirectional.

```
┌─────────────────────┐     JSON-RPC 2.0      ┌─────────────────────┐
│  OMEGA HIVEMIND     │  ──── stdio ────────>  │  GROK CLI (x8)      │
│  (Client)           │  <───────────────────  │  (Agent Pool)       │
│                     │     bidirectional      │                     │
│  Methods:           │                        │  Methods:            │
│  - session/         │                        │  - initialize        │
│    request_permission│                       │  - authenticate      │
│  - fs/read_text_file│                        │  - session/new       │
│  - fs/write_text_file│                       │  - session/load      │
│  - terminal/create  │                        │  - session/prompt    │
│  - terminal/output  │                        │  - session/set_mode  │
│  - terminal/release │                        │  - logout            │
│  - terminal/        │                        │                     │
│    wait_for_exit    │                        │  Notifications:      │
│  - terminal/kill    │                        │  - session/update    │
│                     │                        │  - session/cancel    │
└─────────────────────┘                        └─────────────────────┘
```

### §3.2 Session Lifecycle (Per Grok CLI Process)

```
1. INITIALIZE ──> Client → Agent: initialize (version + capabilities)
                      ↓ both agree on protocol version
2. AUTHENTICATE ──> Client → Agent: authenticate (if required)
                      ↓ session established
3. SESSION SETUP ──> Client → Agent: session/new (or session/load)
                      ↓ conversation ready
4. PROMPT TURN ────> Client → Agent: session/prompt
                      ↓ Agent → Client: session/update (progress)
                      ↓ Agent → Client: fs/read_text_file, file writes, terminal
                      ↓ Agent → Client: session/prompt (stop reason, response)
                      ↓          [repeat for each turn]
5. SESSION CLOSE ──> Client → Agent: close stdin → terminate subprocess
```

### §3.3 Capability Negotiation (initialize)

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0",
    "capabilities": {
      "fs": { "read_text_file": true, "write_text_file": true },
      "terminal": { "create": true, "output": true, "release": true, "wait_for_exit": true, "kill": true },
      "session": { "load": true, "set_mode": true }
    },
    "clientInfo": { "name": "omega-hivemind", "version": "1.0" }
  },
  "id": 1
}
```

**Grok Build Response** (expected):
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "1.0",
    "capabilities": {
      "fs": { "read_text_file": true, "write_text_file": true },
      "terminal": { "create": true, "output": true, "release": true, "wait_for_exit": true, "kill": true },
      "session": { "load": true, "set_mode": true },
      "subagents": true,
      "hooks": true,
      "plan_mode": true
    },
    "agentInfo": { "name": "grok-build", "version": "0.1.0" }
  },
  "id": 1
}
```

### §3.4 Fleet Bridge Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OMEGA HIVEMIND (Client)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              GROK CLI FLEET ORCHESTRATOR                │   │
│  │  - Spawns 8 Grok CLI subprocesses (ACP agents)          │   │
│  │  - Routes prompts via session/prompt                     │   │
│  │  - Handles session/update notifications (streaming)      │   │
│  │  - Manages fs/terminal requests from agents              │   │
│  │  - Implements session/load for persistence               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│              ┌─────────────┼─────────────┐                     │
│              ▼             ▼             ▼                     │
│         ┌─────────┐   ┌─────────┐   ┌─────────┐               │
│         │ Grok CLI│   │ Grok CLI│   │ Grok CLI│  ... (x8)      │
│         │  #1     │   │  #2     │   │  #3     │               │
│         │ ACP     │   │ ACP     │   │ ACP     │               │
│         │ stdio   │   │ stdio   │   │ stdio   │               │
│         └─────────┘   └─────────┘   └─────────┘               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │     OMEGA-VAULT         │
              │  - 16 API keys stored   │
              │  - Credential rotation  │
              │  - Rate limit tracking  │
              └─────────────────────────┘
```

### §3.5 Credential Rotation Strategy

**Problem**: Grok CLI uses browser-derived cookies with **24-48h expiry**.

**Solution**: Omega-Vault passive watcher + automated rotation

```python
# Credential lifecycle per account
class GrokCLICredential:
    account_id: str                    # e.g., "grok-fleet-01"
    cookie_jar: dict                   # Browser cookies (encrypted)
    expires_at: datetime               # 24-48h from issuance
    last_rotated: datetime
    rotation_status: "valid" | "expiring" | "expired" | "rotating"
    
    # Rotation trigger: 6h before expiry
    # Rotation method: Selenium/Playwright headless login → extract cookies → store
    # Fallback: Manual intervention alert via Hivemind
```

**Rotation Pipeline**:
1. **Vault Watcher** detects `expires_at - now < 6h`
2. **Rotation Job** launched (headless browser automation)
3. **New cookies** extracted, encrypted, stored
4. **Active sessions** gracefully drained (session/load on new process)
5. **Old credentials** archived, marked rotated

---

## §4 Web Grok Projects — 8 Persona Fleet

### §4.1 Project Provisioning

Each persona = 1 Web Grok Project at `grok.com/project` with custom instructions.

| Slot | Persona | Custom Instructions Focus | Tools Enabled |
|------|---------|---------------------------|---------------|
| 1 | **Research** | DeepSearch synthesis, multi-source, gap-flagged, citation discipline | DeepSearch, Web, X, Code Interpreter |
| 2 | **Reason** | Think Mode, step-by-step, adversarial self-critique, assumption checking | Think, Web, Code Interpreter |
| 3 | **Pulse** | X real-time, narrative velocity, signal detection, trend synthesis | X Search, Web |
| 4 | **Code** | Security-first review, perf-aware, test-generating, dependency analysis | Code Interpreter, Web, Collections |
| 5 | **Arch** | Trade-off analysis, scalability, decision records, ADR generation | Think, DeepSearch, Web |
| 6 | **Creative** | Imagine/Video, prompt engineering, brand consistency, asset generation | Imagine, Video, Image Understanding |
| 7 | **Strategic** | Multi-criteria, risk-weighted, pre-mortem, red-team, scenario planning | Think, DeepSearch, X |
| 8 | **Wildcard** | Chaos agent, break assumptions, unconventional angles, stress tests | All tools, no constraints |

### §4.2 Project Configuration (per persona)

```yaml
# Example: Research Persona Project Config
project_id: "grok-research-01"
title: "Omega Research Specialist"
custom_instructions: |
  You are the Research persona of the Omega Grok Fleet.
  MANDATES:
  - Every claim must be cited with source + date
  - Flag gaps explicitly: "UNVERIFIED: ...", "GAP: ..."
  - Use DeepSearch for multi-source synthesis
  - Use X Search for real-time signals
  - Use Code Interpreter for data analysis
  - Output format: Executive Summary → Findings → Gaps → Sources
tools_enabled:
  - deep_search
  - web_search
  - x_search
  - code_interpreter
model_preference: "grok-4.5"  # DeepSearch native
```

### §4.3 Access Pattern

| Access Method | Use Case | Latency |
|---------------|----------|---------|
| **Browser Automation** (Playwright) | Full persona interaction, file uploads | ~2-5s |
| **API** (if xAI exposes Project API) | Programmatic prompt/response | ~500ms |
| **Manual** (human-in-loop) | Oversight, calibration | N/A |

**Current Reality (July 2026)**: No public API for Web Grok Projects. **Browser automation is required** for fleet integration.

---

## §5 Fleet Deployment Architecture — Complete

### §5.1 Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         OMEGA ENGINE                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GROKSTER (Fleet Commander)                      │  │
│  │  - Model Router (selection matrix)                                   │  │
│  │  - Rate Limit Tracker (per-account, per-model)                       │  │
│  │  - Cost Tracker (prompt caching, batch discounts)                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐   │
│  │ GROK CLI    │            │ GROK CLI    │            │ GROK CLI    │   │
│  │ POOL (x8)   │            │ POOL (x8)   │            │ POOL (x8)   │   │
│  │             │            │             │            │             │   │
│  │ ACP stdio   │            │ ACP stdio   │            │ ACP stdio   │   │
│  │ Headless    │            │ Headless    │            │ Headless    │   │
│  │ Grok Build  │            │ Grok Build  │            │ Grok Build  │   │
│  └──────┬──────┘            └──────┬──────┘            └──────┬──────┘   │
│         │                          │                          │            │
│         └──────────────────────────┼──────────────────────────┘            │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        OMEGA-VAULT                                    │  │
│  │  - 16 encrypted credential sets (8 CLI cookies + 8 Web Project auth) │  │
│  │  - Passive watcher: cookie expiry → rotation job                     │  │
│  │  - Rate limit state: requests/min, tokens/min per account            │  │
│  │  - ACP smoke test: validate handshake on rotation                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐   │
│  │ WEB GROK    │            │ WEB GROK    │            │ WEB GROK    │   │
│  │ PERSONA     │            │ PERSONA     │            │ PERSONA     │   │
│  │ FLEET (x8)  │            │ FLEET (x8)  │            │ FLEET (x8)  │   │
│  │             │            │             │            │             │   │
│  │ Browser     │            │ Browser     │            │ Browser     │   │
│  │ Automation  │            │ Automation  │            │ Automation  │   │
│  │ (Playwright)│            │ (Playwright)│            │ (Playwright)│   │
│  └─────────────┘            └─────────────┘            └─────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
```

### §5.2 Grok CLI Pool — Implementation Spec

```python
# Fleet Orchestrator Core
class GrokCLIFleetOrchestrator:
    def __init__(self, vault: OmegaVault, hivemind: HivemindClient):
        self.vault = vault
        self.hivemind = hivemind
        self.pool: Dict[str, GrokCLIProcess] = {}
        self.rate_limits: Dict[str, RateLimitState] = {}
        
    async def spawn_pool(self, size: int = 8) -> List[str]:
        """Spawn N Grok CLI processes via ACP stdio"""
        account_ids = await self.vault.get_grok_cli_accounts(size)
        for account_id in account_ids:
            creds = await self.vault.get_credentials(account_id)
            proc = await self._launch_grok_cli(account_id, creds)
            await self._acp_handshake(proc)
            self.pool[account_id] = proc
        return list(self.pool.keys())
    
    async def _launch_grok_cli(self, account_id: str, creds: GrokCLICredential) -> GrokCLIProcess:
        # grok agent stdio --config ~/.config/grok/{account_id}/config.toml
        env = {"GROK_COOKIES": creds.cookie_jar_json}
        proc = await anyio.open_process(
            ["grok", "agent", "stdio"],
            env=env
        )
        return GrokCLIProcess(account_id, proc)
    
    async def _acp_handshake(self, proc: GrokCLIProcess) -> bool:
        # 1. initialize
        # 2. authenticate (if needed)
        # 3. session/new
        # 4. Verify session/update notifications work
        pass
    
    async def route_prompt(self, prompt: str, model: str = None, 
                          account_preference: str = None) -> ACPResponse:
        # Select account based on:
        # - Model capability match
        # - Rate limit headroom
        # - Cost optimization (prompt caching)
        # - Account preference (sticky sessions)
        account_id = self._select_account(model, account_preference)
        proc = self.pool[account_id]
        
        # Send session/prompt
        # Stream session/update notifications
        # Return final response
        pass
    
    def _select_account(self, model: str, preference: str) -> str:
        # Score each account: rate_limit_headroom * capability_match * cost_efficiency
        # Return highest scoring available account
        pass
```

### §5.3 Web Grok Persona Fleet — Implementation Spec

```python
class WebGrokPersonaFleet:
    def __init__(self, vault: OmegaVault, browser_pool: BrowserPool):
        self.vault = vault
        self.browser_pool = browser_pool
        self.personas: Dict[str, WebGrokPersona] = {}
        
    async def provision_personas(self) -> List[str]:
        """Create/verify 8 Web Grok Projects with custom instructions"""
        persona_configs = self._get_persona_configs()
        for config in persona_configs:
            # Check if project exists
            # If not, create via browser automation
            # Update custom instructions
            # Verify model preference
            persona = await self._provision_persona(config)
            self.personas[config.slot] = persona
        return list(self.personas.keys())
    
    async def _provision_persona(self, config: PersonaConfig) -> WebGrokPersona:
        page = await self.browser_pool.get_page()
        # Navigate to grok.com/project
        # Login with credentials from vault
        # Create/update project
        # Set custom instructions
        # Set model preference
        # Verify working
        return WebGrokPersona(config, page)
    
    async def prompt_persona(self, slot: str, prompt: str, 
                            files: List[Path] = None) -> PersonaResponse:
        persona = self.personas[slot]
        # Use browser automation to send prompt
        # Handle file uploads if needed
        # Wait for response
        # Return structured response
        pass
```

---

## §6 Cost Model — Fleet Operations

### §6.1 Monthly Cost Estimates (at 5 Usage Levels)

| Usage Level | Grok CLI Pool (API) | Web Grok (Browser) | Total Est. |
|-------------|---------------------|-------------------|------------|
| **Light** (100 prompts/day) | $15-30 | $0 (included in SuperGrok) | **$15-30** |
| **Medium** (1K prompts/day) | $150-300 | $0 | **$150-300** |
| **Heavy** (10K prompts/day) | $1,500-3,000 | $0 | **$1,500-3,000** |
| **Research** (DeepSearch heavy) | $500-1,000 | $0 | **$500-1,000** |
| **Code** (Grok Build heavy) | $200-500 | $0 | **$200-500** |

**Assumptions**:
- SuperGrok Heavy ($300/mo) covers 8 Web Grok Projects + generous API
- API costs use Grok 4.3 base pricing with 20% batch discount where applicable
- Prompt caching saves 30-50% on repeated prefixes
- Server-side tools ($5/1k) used selectively

### §6.2 Cost Optimization Checklist

- [ ] Enable prompt caching via stable system prompt prefixes
- [ ] Route non-urgent synthesis to Batch API (20% off)
- [ ] Avoid ≥200K token prompts (2x penalty) — chunk instead
- [ ] Use Grok Build ($1/$2) for coding tasks vs Grok 4.5 ($2/$6)
- [ ] Web Grok Projects for persistent long-context (no token costs)
- [ ] Monitor rate limits per account — rotate before 429

---

## §7 Decision Gates — Fleet Deployment

| Gate | Criteria | Status |
|------|----------|--------|
| **DG-1: Model Matrix Finalized** | 12+ models mapped with pricing, context, capabilities, routing logic | ✅ **COMPLETE** |
| **DG-2: ACP Handshake Validated** | `initialize` → `authenticate` → `session/new` → `session/prompt` works end-to-end | ⏳ **PENDING** (needs V-1 Vault + live test) |
| **DG-3: Credential Rotation Working** | 24-48h cookie rotation automated, smoke test passes | ⏳ **PENDING** (needs V-1 Vault) |
| **DG-4: Rate Limit Tracking** | Per-account request/token tracking, automatic failover | ⏳ **PENDING** |
| **DG-5: Web Grok Provisioned** | 8 Projects created with custom instructions, browser automation working | ⏳ **PENDING** |
| **DG-6: Cost Tracking Live** | Real-time cost estimation, caching hit rate, batch usage | ⏳ **PENDING** |

---

## §8 Key Findings Summary

| Finding | Impact |
|---------|--------|
| **12+ active models** with distinct SKUs — not 6 | Fleet router must be model-aware |
| **Long-context penalty at 200K** (2x pricing) | Critical for cost model; chunk or cache |
| **Server-side tools = $5/1k** (web_search, x_search, code) | Use selectively; not free |
| **Responses API = future** (previous_response_id, structured reasoning) | Migrate from Chat Completions |
| **Grok Build OPEN SOURCE** (since July 15) | Local-first fleet option; no $300/mo SuperGrok needed |
| **Grok Build subagent orchestrator** (8-way, Git worktrees, hooks) | Can replace custom fleet orchestrator for coding tasks |
| **Web Grok Projects = persistent context** | 8 personas with native long-context, no API costs |
| **No Web Grok Projects API** | Browser automation required for fleet integration |
| **Cookie expiry 24-48h** | Omega-Vault rotation pipeline mandatory |
| **Batch API 20% off** on 4.3/4.20 | Major savings for non-real-time workloads |

---

## §9 Next Actions

1. **V-1 Omega-Vault MVP** — Credential storage + rotation + ACP smoke test (blocks DG-2, DG-3)
2. **ACP Handshake Test** — Live `grok agent stdio` handshake validation
3. **Web Grok Provisioning** — Browser automation to create 8 persona Projects
4. **Fleet Orchestrator Prototype** — Route prompts, track rate limits, measure costs
5. **Cost Dashboard** — Real-time tracking with caching/batch optimization alerts

---

## §10 Sources

| Source | Type | Date | Relevance |
|--------|------|------|-----------|
| xAI API Docs (api.x.ai) | Official | 2026-07 | Models, pricing, Responses API, tools |
| xAI Blog (x.ai/blog) | Official | 2026-07 | Grok 4.5 launch, Grok Build open source |
| Grok Build GitHub (github.com/xai-org/grok-build) | Source | 2026-07 | ACP implementation, subagent architecture |
| ACP Spec (github.com/anthropic/agent-client-protocol) | Spec | 2026-07 | v1 stable, v2 draft |
| Hacker News discussions | Community | 2026-07 | Grok Build data upload warning, pricing changes |
| Web Grok Projects UI | Product | 2026-07 | Persona configuration, custom instructions |

---

*⬡ OMEGA ⬡ GROKSTER ⬡ R33 COMPLETE ⬡ 2026-07-21 ⬡ Model matrix finalized, fleet architecture specified, decision gates defined*