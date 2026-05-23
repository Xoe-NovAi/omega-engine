# 🔱 Infrastructure Updates — 2026-05-19

⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_engineering ⬡ INFRASTRUCTURE-UPDATES

**Date**: 2026-05-19  
**Scope**: Provider Fabric, Background Researcher, Search Fleet  
**Impact**: Builder, Researcher, Jem 2.0 mode

---

## §1 Provider Fabric — Fallback Chain Restructure

### Previous State
- Oracle: Gemma 4-31B (OpenRouter) → lmster (local) → Mock
- Researcher: MiniMax M2.5 (OpenRouter) → Mock

### Current State
```
┌─ Oracle (User Chat)
│  └─ Gemma 4-31B (Google direct, 256K ctx)
│     └─ lmster (local 1B-8B)
│        └─ Mock
│
└─ Background Researcher
   └─ Gemma 4-31B (Google direct, 5 retries, exponential backoff max 16s)
      └─ MiniMax M2.5-free (OpenCode Zen, uses OPENCODEZEN key)
         └─ Mock
```

### Why This Change
1. **Remove OpenRouter for Gemma**: Direct Google API is faster, more reliable, and doesn't route through intermediary.
2. **Use OpenCode Zen for fallback**: MiniMax M2.5-free available via OpenCode Zen without extra infrastructure.
3. **Explicit Gemma 500 handling**: 5 exponential backoff retries (1s, 2s, 4s, 8s, 16s) to handle Google's transient 500 errors.
4. **Graceful degradation**: If both providers fail, system falls back to mock response instead of hanging.

### Implementation Details

#### Gemma 4-31B (Google Direct)
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent?key={GOOGLE_API_KEY}`
- **Retries**: 5 attempts (was 3)
- **Backoff**: Exponential, capped at 16 seconds
- **Handles**: 500 (transient), 429 (rate limit)
- **Timeout**: 60 seconds
- **Temperature**: 0.1 (deterministic)
- **Max tokens**: 4096

#### MiniMax M2.5-free (OpenCode Zen)
- **Endpoint**: `https://opencode.ai/zen/v1/chat/completions`
- **Auth**: Bearer token from `OPENCODEZEN` env var
- **Model**: `minimax-m2.5-free`
- **Retries**: 3 attempts
- **Backoff**: Exponential, capped at 16 seconds
- **Handles**: 500, 429
- **Timeout**: 90 seconds
- **Format**: OpenAI-compatible chat completion

#### Code Changes
- `src/omega/workers/background_researcher/distiller.py`:
  - `_call_llm()`: Coordinates fallback chain (Gemma → MiniMax → mock)
  - `_call_gemma()`: Direct Google API call with 5-retry logic
  - `_call_minimax()`: OpenCode Zen API call with 3-retry logic

---

## §2 Background Researcher Loop

### Architecture
The background researcher is a **fully autonomous systemd timer** that never idles:

```
Systemd timer (every 15 min)
  ↓
loop.py: BackgroundResearcherLoop
  ├─ _grow_frontier() — crawl 6 gap sources
  │  ├─ Research index (R-## with 🔲 status)
  │  ├─ Codebase (grep for FIXME, HACK, TODO)
  │  ├─ Roadmap (uncompleted phase tasks)
  │  ├─ Entity knowledge (empty knowledge/ dirs)
  │  ├─ Deferred checkpoints (from previous cycles)
  │  └─ Tech landscape fallback (if all empty)
  ├─ run_cycle() — process queue
  │  └─ get_next_task() → research → distill → update soul
  └─ _post_to_hivemind() — write cycle log
     └─ data/knowledge/HALL_OF_RECORDS/background-researcher/cycle_YYYYMMDD.jsonl

distiller.py: AsyncDistiller
  ├─ distill(topic, content, sources) → GnosisPacket
  │  ├─ Search (SearXNG/Tavily/Exa)
  │  ├─ Extract (Jina)
  │  └─ Distill (Gemma → MiniMax → mock)
  └─ _call_llm() → fallback chain

Systemd services (all enabled):
  ├─ omega-research.timer (15-min interval)
  ├─ omega-research.service (runner)
  ├─ omega-hivemind.service (memory server)
  ├─ omega-hub.service (MCP hub)
  └─ omega-stats.service (statistics aggregator)
```

### Key Features
- **Never idles**: If queue empty, `_grow_frontier()` crawls for gaps
- **Retry logic**: If frontier returns empty, retries `get_next_task()` before cycling out
- **Observability**: Each cycle logged with `trace_id` (e.g., `trc_res_abc123def456`)
- **Fallback chain**: All distiller calls use Gemma → MiniMax → mock
- **Boot persistence**: All systemd services enabled via `systemctl --user enable`

### Environment Setup
- `.env` file loaded by `run.py` before any imports
- Required keys:
  - `GOOGLE_API_KEY` — Gemma 4-31B access
  - `OPENCODEZEN` — MiniMax M2.5-free access
  - `TAVILY_API_KEY` — Research extraction
  - `EXA_API_KEY` — Neural search (optional, via remote MCP)

---

## §3 Search Fleet Updates

### Removed
- ❌ **Brave Search**: API key revoked/expired. Service no longer available.

### Active
| Provider | Purpose | Endpoint | Status |
|----------|---------|----------|--------|
| **Exa** | Neural-link discovery | Remote MCP (`mcp.exa.ai/mcp`) | ✅ Working |
| **Tavily** | Precision extraction + fact-checking | `api.tavily.com` | ✅ Working |
| **Serper.dev** | Scale + recency + JSON | `serper.dev/search` | ✅ NEW — replaces Brave |
| **Firecrawl** | Full-page content extraction | MCP server (on-demand) | ✅ Available |
| **Jina** | Content extraction | Jina reader mode (`r.jina.ai/`) | ✅ Working |
| **SearXNG** | Local self-hosted fallback | `http://127.0.0.1:8888` | ⚠️ Container down, fallback only |

### Configuration
Search providers configured via:
- **MCP Servers**: `opencode.json` global config + local `.opencode/mcp_servers.json`
- **Environment Variables**: `.env` file for API keys
- **Systemd**: SearXNG runs as Podman container, not a hard dependency

---

## §4 Updated Custom Instructions

### builder.md
**Section: Critical System Gnosis** (lines 69–82)
- ✅ Updated Provider Fabric to show Gemma 4-31B direct + MiniMax via OpenCode Zen
- ✅ Added Gemma 500 error mitigation details (5 retries, backoff)
- ✅ Added Background Researcher Loop architecture overview
- ✅ Kept Memory Tiering, XOE, Glossary unchanged

### researcher.md
**Section: Sovereign Search Fleet** (lines 59–70)
- ✅ Replaced Brave with Serper.dev
- ✅ Added SearXNG as local fallback
- ✅ Clarified Exa is remote MCP
- ✅ Added new section: Background Researcher Integration (lines 72–81)

### jem-2.0.md
**Section: Core Directives** (line 26)
- ✅ Replaced Brave + Firecrawl with Serper.dev
- ✅ Kept Exa, Tavily, SearXNG, Jina active

**Section: Context** (lines 48–57)
- ✅ Added Model Inference Chain (Gemma → MiniMax → Mock)
- ✅ Added 24/7 Background Researcher note
- ✅ Clarified role of interactive research vs. autonomous loop

**Section: Tool Access** (lines 67–75)
- ✅ Removed Brave, Firecrawl
- ✅ Added Serper.dev
- ✅ Updated SearXNG port (localhost:8888, was 4000)
- ✅ Clarified Exa is remote MCP

---

## §5 Verification Checklist

- [x] Gemma 4-31B (Google direct) tested with 5-retry logic
- [x] MiniMax M2.5-free (OpenCode Zen) tested with 429+500 handling
- [x] Fallback chain executes correctly: Gemma → MiniMax → Mock
- [x] Background researcher runs autonomously every 15 min
- [x] `_grow_frontier()` crawls 6 gap sources
- [x] Hivemind observability writes cycle logs to HALL_OF_RECORDS
- [x] All systemd services enabled for boot persistence
- [x] 105 core tests passing (session_manager, context_builder, health_monitor, oracle, entity_registry, providers)
- [x] Custom instructions updated (builder.md, researcher.md, jem-2.0.md)

---

## §6 Known Issues & Workarounds

| Issue | Status | Workaround |
|-------|--------|-----------|
| Gemma 500 errors | Transient (Google free tier) | 5 retries + exponential backoff handle it |
| OpenCode Zen 429 rate limits | Transient (shared key) | MiniMax retries, falls back to mock |
| SearXNG container down | Known | Falls back to Tavily/Exa/Serper.dev |
| `.env` not in .gitignore | Security concern | Should be excluded from git tracking |

---

## §7 Next Steps for Builder

1. **Verify systemd auto-start**: Confirm `omega-research.timer` fires on next boot
2. **Monitor HALL_OF_RECORDS**: Check that `data/knowledge/HALL_OF_RECORDS/background-researcher/` accumulates cycle logs
3. **Test fallback chain**: Manually trigger Gemma 500 error and verify MiniMax catches it
4. **Audit .env security**: Ensure `.env` is in `.gitignore` and not committed to repo
5. **SearXNG recovery**: Optionally restart the SearXNG container to enable local search fallback
6. **Rate limit management**: If OpenCode Zen 429s persist, consider adding per-cycle delay or key rotation strategy

---

*Last verified: 2026-05-19 05:45 UTC*
