# 🔱 Phase 1E: Exa Search API Free Tier + MCP Rotation Spec
**AP Token**: `AP-RESEARCHER-PHASE1E-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1e_exa ⬡ ACTIVE
**Date**: 2026-07-23
**Sources**: Exa docs (exa.ai/docs), rate limits page, MCP setup, pricing, changelog (2026-07-19)
**Architect Constraint**: D-432 — Zero paid accounts, all free tier. D-437 — Phase 1 free-tier only, no proxy layer.

---

## 🎯 Executive Summary (L1)

Exa provides **AI-native search** with 7 search types (`instant`, `fast`, `auto`, `deep-lite`, `deep`, `deep-reasoning`) and **structured output via `output_schema`**. Free tier: **3 QPS / 150 calls/day via MCP** (unauthenticated) OR **10 QPS `/search`, 100 QPS `/contents` with API key** ($10 credits on signup, then $7/1k search requests). **For 8-account fleet**: 8 API keys → 80 QPS `/search`, 800 QPS `/contents`, 1,200 calls/day. MCP free tier (3 QPS/150/day) is fallback only.

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**API Endpoints & Limits**:
| Endpoint | Authenticated (API Key) | Unauthenticated (MCP Free) |
|----------|------------------------|---------------------------|
| `/search` | 10 QPS | 3 QPS (MCP) |
| `/contents` | 100 QPS | N/A |
| `/answer` | 10 QPS | N/A |
| MCP `web_search_exa` | N/A | 3 QPS, 150/day |
| MCP `web_search_advanced_exa` | N/A | 3 QPS, 150/day |

**Search Types** (latency/quality tradeoff):
| Type | Latency | Use Case |
|------|---------|----------|
| `instant` | ~150ms | Real-time chat, voice |
| `fast` | ~450ms | Agentic workflows, low-latency |
| `auto` (default) | ~1s | Balanced |
| `deep-lite` | 4s | Lightweight synthesis |
| `deep` | 4-15s | Multi-step reasoning, structured output |
| `deep-reasoning` | 12-40s | Maximum reasoning depth |

**Structured Output**: `output_schema` (JSON Schema, max depth 2, max 10 properties) works on **ALL search types**. Returns `output.content` (structured) + `output.grounding` (field-level citations + confidence).

### 2. The Adversary (Critical Rigor)
**Constraints**:
- **MCP free tier is shared by IP** — 8 fleet instances on same IP = 3 QPS total, not 3 each
- **API key rate limits are per key** — 8 keys = 80 QPS `/search` (linear scale)
- **Deep search costs more**: $12-15/1k vs $7/1k for regular search
- **`output_schema` adds synthesis latency** on top of base search type
- **Contents endpoint**: `maxAgeHours: 0` forces live crawl (slower, costs more)
- **No free tier for `/contents` without API key** — MCP only exposes search

### 3. The Alchemist (Creative Synthesis)
**Fleet Strategy**:
- **8 API keys** (primary) → 80 QPS search, 800 QPS contents
- **MCP free tier** (fallback only) → 3 QPS shared, 150/day shared
- **Search type routing**: `instant`/`fast` for real-time; `deep`/`deep-reasoning` for research tasks with `output_schema`
- **Cost control**: Default `type: "auto"`, `maxAgeHours: 168` (weekly cache), `contents: { highlights: true, maxCharacters: 4000 }` — avoids live crawl costs

### 4. The Archivist (Historical Truth)
**2026 Updates** (Feb 2026 changelog):
- `instant` search: sub-150ms, new neural model
- `deep-reasoning`: 12-50s (was 12-40s)
- `output_schema` on ALL types (was deep-only)
- Pricing simplified: Search+contents $7/1k (10 results, text+highlights free)
- MCP free tier: 3 QPS, 150/day unauthenticated

---

## 📋 Actionable Config Specs (L3)

### 1. Exa VaultCore Schema (8 Keys)
```yaml
provider: "exa"
cred_type: "api_key"
encrypted_blob: "<age-encrypted exa_api_key>"
metadata:
  key_id: "exa_fleet_03"
  qps_search: 10
  qps_contents: 100
  daily_limit: 150  # Soft limit; hard limit = credits
  credits_remaining: 1000  # From $10 signup credit
  search_types_enabled: ["instant", "fast", "auto", "deep-lite", "deep", "deep-reasoning"]
  output_schema_enabled: true
  mcp_fallback: true
```

### 2. Search Request Builder (ModelGateway Integration)
```python
class ExaSearchRouter:
    """Routes search requests to optimal Exa fleet key + search type."""
    
    SEARCH_TYPE_POLICY = {
        "realtime": "instant",      # Chat, voice, autocomplete
        "agentic": "fast",          # Tool use, quick grounding
        "default": "auto",          # General purpose
        "research": "deep",         # Multi-step, structured output
        "deep_research": "deep-reasoning",  # Maximum reasoning
    }
    
    def __init__(self, vault):
        self.vault = vault
        self.key_usage = defaultdict(lambda: {"search": 0, "contents": 0, "reset_at": midnight_pacific()})
    
    async def search(self, query: str, intent: str = "default", 
                     output_schema: dict = None, **kwargs) -> ExaResponse:
        # 1. Select search type
        search_type = self.SEARCH_TYPE_POLICY.get(intent, "auto")
        
        # 2. Lease least-used key
        key_id = await self._lease_key("search")
        
        # 3. Build request
        request = {
            "query": query,
            "type": search_type,
            "numResults": kwargs.get("num_results", 10),
            "contents": {
                "highlights": {"maxCharacters": 4000},
                "maxAgeHours": 168,  # Weekly cache
            },
        }
        if output_schema:
            request["outputSchema"] = output_schema
            request["systemPrompt"] = kwargs.get("system_prompt", 
                "Prefer official sources. Avoid duplicates. Cite all claims.")
        
        # 4. Execute with rotation on 429
        return await self._execute_with_rotation(key_id, "/search", request)
    
    async def _execute_with_rotation(self, key_id: str, endpoint: str, request: dict):
        for attempt in range(3):  # Max 3 key rotations
            key = await self.vault.get_secret(f"exa/{key_id}")
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://api.exa.ai{endpoint}",
                    headers={"x-api-key": key, "Content-Type": "application/json"},
                    json=request,
                    timeout=60.0 if "deep" in request.get("type", "") else 10.0
                )
            
            if resp.status_code == 429:
                # Rate limited — rotate key
                await self.vault.mark_rate_limited(f"exa/{key_id}")
                key_id = await self._lease_key("search")
                continue
            
            resp.raise_for_status()
            return ExaResponse(**resp.json())
        
        raise ExaExhaustedError("All 8 Exa keys rate limited")
```

### 3. Structured Output Schema Patterns
```python
# Company research
COMPANY_SCHEMA = {
    "type": "object",
    "required": ["companies"],
    "properties": {
        "companies": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["company_name", "ceo_name", "headquarters", "employee_count"],
                "properties": {
                    "company_name": {"type": "string"},
                    "ceo_name": {"type": "string"},
                    "headquarters": {"type": "string"},
                    "employee_count": {"type": "number"},
                    "founded_year": {"type": "number"},
                    "description": {"type": "string"}
                }
            }
        }
    }
}

# Technical specification extraction
TECH_SPEC_SCHEMA = {
    "type": "object",
    "required": ["specs"],
    "properties": {
        "specs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["parameter", "value", "unit", "source_url"],
                "properties": {
                    "parameter": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": "string"},
                    "source_url": {"type": "string", "format": "uri"}
                }
            }
        }
    }
}

# News summarization
NEWS_SUMMARY_SCHEMA = {
    "type": "object",
    "required": ["articles"],
    "properties": {
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "summary", "source", "published_date", "url"],
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "source": {"type": "string"},
                    "published_date": {"type": "string", "format": "date"},
                    "url": {"type": "string", "format": "uri"},
                    "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]}
                }
            }
        }
    }
}
```

### 4. Contents Retrieval (Post-Search)
```python
async def get_contents(self, urls: list[str], **kwargs) -> ExaContentsResponse:
    key_id = await self._lease_key("contents")
    request = {
        "ids": urls,
        "contents": {
            "text": {"maxCharacters": kwargs.get("max_chars", 10000)},
            "highlights": {"maxCharacters": 4000},
            "summary": {"query": kwargs.get("summary_query")} if kwargs.get("summary_query") else False,
            "maxAgeHours": 168,
        }
    }
    # ... execute with rotation
```

### 5. MCP Fallback Config
```json
// .opencode/mcp/exa-free.json
{
  "mcpServers": {
    "exa": {
      "url": "https://mcp.exa.ai/mcp",
      "headers": {}
    }
  }
}
```
**Warning**: Keyless MCP hits IP-based daily caps. Only for emergency when all 8 keys exhausted.

---

## 🛡️ Mandate Alignment Checklist

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO** | ✅ | HTTPX async in AnyIO task group |
| **M7 Local-First** | ✅ | Keys in VaultCore; Exa = cloud only |
| **M8 Zero Telemetry** | ✅ | No Exa telemetry in our code |
| **M14 Heritage** | N/A | No id Software patterns |
| **M23 Failure Integrity** | ✅ | 429 → rotation; timeout per search type |
| **M25 Streaming Resilience** | ✅ | Exa supports `stream: true` SSE; lease TTL covers |

---

## 🚀 Dev Strategy Revisal Recommendations

### Immediate (P0-2 — This Week)
1. **Create 8 Exa accounts** (free tier, $10 credits each = 8,000 fleet credits)
2. **VaultCore schema**: `cred_type: exa_api_key` with cost metadata
3. **ModelGateway tool**: `exa_search`, `exa_contents`, `exa_deep_research`

### Short-term (P1-1 — VaultCore Schema)
1. **Per-key credit tracking**: `used_today` reset at midnight Pacific
2. **Search type cost awareness**: `deep` = 2x cost, `deep-reasoning` = 2.5x
3. **Output schema cost**: Adds synthesis tokens — track in `used_today`

### Medium-term (P2 — Orchestration)
1. **Exa → Firecrawl pipeline**: Exa search (10 QPS, cheap) → Firecrawl scrape (10 RPM, expensive)
2. **Deep research agent**: `exa_deep_research` tool with `output_schema` + multi-step
3. **Citation verifier**: Use `output.grounding` confidence scores to filter low-confidence claims

---

## 📦 Deliverables for Phase 3 Synthesis

| Artifact | Location | Purpose |
|----------|----------|---------|
| Exa VaultCore Schema | `docs/research/R_VAULT_SCHEMA_V2.md` (extended) | 8 keys + cost metadata |
| Exa Router Class | `src/omega/model_gateway/exa_router.py` | Lease + search type + rotate |
| Structured Schema Library | `config/exa_output_schemas.yaml` | Reusable JSON schemas |
| Deep Research Tool | `src/omega/tools/exa_deep_research.py` | Multi-step with structured output |
| MCP Fallback Config | `.opencode/mcp/exa-free.json` | Emergency keyless access |

---

## 🔗 Cross-References

| Provider | Phase 1 Report | Key Integration Point |
|----------|----------------|----------------------|
| **Firecrawl** | `PHASE1F_FIRECRAWL_CREDITS_...` | Exa finds URLs → Firecrawl scrapes |
| **OpenRouter** | `PHASE1D_OPENROUTER_...` | Exa as tool via OpenRouter? No — direct |
| **Google API** | `PHASE1A_GOOGLE_API_...` | Exa can search Google results |
| **Antigravity** | `PHASE1B_ANTIGRAVITY_...` | No direct link |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1E-COMPLETE ⬡ 2026-07-23*