# 🔱 Phase 1F: Firecrawl Credit System & Rate Limits Spec
**AP Token**: `AP-RESEARCHER-PHASE1F-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1f_firecrawl ⬡ ACTIVE
**Date**: 2026-07-23
**Sources**: Firecrawl docs (docs.firecrawl.dev), pricing page, rate limits, billing, API reference
**Architect Constraint**: D-432 — Zero paid accounts, all free tier. D-437 — Phase 1 free-tier only, no proxy layer.

---

## 🎯 Executive Summary (L1)

Firecrawl operates on a **credit-based system** with monthly subscription tiers. **Free tier**: 1,000 credits/month, 2 concurrent browsers, low rate limits (10 RPM `/scrape`, 10 RPM `/map`, 1 RPM `/crawl`, 5 RPM `/search`, 10 RPM `/agent`). Credits consumed per page + modifiers (JSON extraction +4, Enhanced Mode +4, PDF +1/page). **402 Payment Required** when credits exhausted. **Smart Upgrade** (since Jun 2026) auto-upgrades tier instead of failing. For 8-account fleet: 8 × 1,000 = 8,000 credits/month free. Keyless usage (MCP/CLI/SDK) capped per IP/day.

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**Credit Economy**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    FIRECRAWL CREDIT MODEL                         │
├─────────────────────────────────────────────────────────────────┤
│  BASE COSTS (per page/call)                                       │
│  ├── Scrape: 1 credit                                            │
│  ├── Crawl: 1 credit/page (default limit 10,000!)                │
│  ├── Map: 1 credit/call                                          │
│  ├── Search: 2 credits / 10 results (rounded up)                 │
│  ├── Interact: 2 credits / browser minute                        │
│  └── Agent: 5 free runs/day, then dynamic                        │
├─────────────────────────────────────────────────────────────────┤
│  MODIFIERS (stack additively)                                     │
│  ├── JSON format (LLM extraction): +4 credits/page               │
│  ├── Enhanced Mode (anti-bot): +4 credits/page                   │
│  ├── PDF parsing: +1 credit/PDF page                             │
│  ├── Zero Data Retention (ZDR): +1 credit/page                   │
│  ├── Audio extraction: +4 credits/page (1 base + 4)              │
│  └── Video extraction: +4 credits/page                           │
├─────────────────────────────────────────────────────────────────┤
│  EXAMPLE: Scrape + JSON + Enhanced = 1 + 4 + 4 = 9 credits/page  │
│  Crawl 100 pages with JSON = 100 × (1+4) = 500 credits           │
└─────────────────────────────────────────────────────────────────┘
```

**Rate Limits (Free Tier)**:
| Endpoint | RPM | Notes |
|----------|-----|-------|
| `/scrape` | 10 | Per team (all keys share) |
| `/map` | 10 | |
| `/crawl` | 1 | 1 concurrent crawl |
| `/search` | 5 | |
| `/agent` | 10 | |
| `/crawl/status` | 1,500 | High for polling |
| `/agent/status` | 500 | |

**Concurrency**: 2 browsers (Free) → 15 (Hobby) → 50 (Standard) → 250 (Growth) → 750 (Scale)

### 2. The Adversary (Critical Rigor)
**Traps**:
- **Crawl pre-flight credit check**: Default `limit: 10000` requires 10,000 credits upfront → 402 on free tier. **Fix**: Always pass explicit `limit: 100` or similar.
- **Credits charged on HTTP errors**: 403/404 still cost 1 credit (browser rendered). Check `metadata.statusCode` before retry.
- **Modifiers stack**: JSON + Enhanced = 9 credits/page. Easy to burn 1,000 credits on 111 pages.
- **Keyless limits**: Per IP per day — requests AND credits. Shared office IP = shared cap.
- **Smart Upgrade auto-charges**: "Payments go toward upgrades" — may surprise if not monitored.
- **Team-scoped rate limits**: All 8 keys share 10 RPM `/scrape`. No per-key isolation.

### 3. The Alchemist (Creative Synthesis)
**Cross-pollination**: Firecrawl credits map to VaultCore `used_today` / `daily_limit`. **Crawl pre-flight** = VaultCore lease acquisition (check `used_today + estimated_cost <= daily_limit`). **Modifiers** = metadata on credential lease (`scrape_options: {formats: ["json"], enhanced: true}` → cost multiplier 9x). **Exa + Firecrawl pipeline**: Exa finds URLs (cheap, 10 QPS) → Firecrawl scrapes details (expensive, 10 RPM). **Agent as research primitive**: 5 free runs/day/account = 40 free deep research runs/fleet/day.

### 4. The Archivist (Historical Truth)
**Jun 1 2026**: Smart Upgrade replaces Auto-Recharge. **Legacy Extract plans** (Starter/Explorer/Pro) separate from main plans. **MCP server** (`npx -y firecrawl-mcp`) enables keyless usage but hits IP caps. **ZDR** (Zero Data Retention) enterprise only.

---

## 📋 Actionable Config Specs (L3)

### 1. VaultCore Credential Schema
```yaml
provider: "firecrawl"
cred_type: "api_key"
encrypted_blob: "<age-encrypted: FC_API_KEY>"
metadata:
  plan: "free"  # free|hobby|standard|growth|scale
  monthly_credits: 1000
  concurrency: 2
  rate_limits:
    scrape: 10
    map: 10
    crawl: 1
    search: 5
    agent: 10
  modifiers_cost:
    base_scrape: 1
    json_format: 4
    enhanced_mode: 4
    pdf_parsing: 1
    zdr: 1
```

### 2. Lease Cost Estimation (Pre-flight)
```python
async def estimate_firecrawl_cost(operation: str, options: dict) -> int:
    """Return estimated credits for operation. Used in lease acquisition."""
    base = {
        "scrape": 1,
        "crawl": 1,  # per page
        "map": 1,
        "search": 2,  # per 10 results
        "interact": 2,  # per minute
        "agent": 0,  # dynamic
    }[operation]
    
    modifiers = 0
    if options.get("formats"):
        for fmt in options["formats"]:
            if isinstance(fmt, dict) and fmt.get("type") == "json":
                modifiers += 4
            elif fmt in ("json", "question", "highlights"):
                modifiers += 4
    if options.get("enhanced_mode") or options.get("proxy") == "enhanced":
        modifiers += 4
    if options.get("pdf_parsing"):
        modifiers += 1
    if options.get("zero_data_retention"):
        modifiers += 1
    
    # For crawl: multiply by limit (default 10000!)
    if operation == "crawl":
        limit = options.get("limit", 100)  # SAFE DEFAULT
        return (base + modifiers) * limit
    
    # For search: per 10 results
    if operation == "search":
        num_results = options.get("num_results", 10)
        return ((base + modifiers) * math.ceil(num_results / 10))
    
    return base + modifiers
```

### 3. Lease Acquisition with Cost Check
```python
async def lease_firecrawl_key(vault, operation: str, options: dict) -> str:
    estimated = await estimate_firecrawl_cost(operation, options)
    
    for attempt in range(8):  # 8 keys
        key_id = await vault.lease_credential(
            provider="firecrawl",
            required_credits=estimated,
            metadata={"operation": operation, "options": options}
        )
        if key_id:
            return key_id
        
        # All keys cooling down or exhausted
        await anyio.sleep(2 ** attempt)
    
    raise FirecrawlExhaustedError(f"No keys available for {operation} (est. {estimated} credits)")
```

### 4. Response Handling & Credit Tracking
```python
async def firecrawl_request(key_id: str, endpoint: str, payload: dict) -> FirecrawlResponse:
    key = await vault.get_key(key_id)
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"https://api.firecrawl.dev/v1{endpoint}",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload
        )
    
    if resp.status_code == 402:
        # Insufficient credits — mark key exhausted for today
        await vault.mark_exhausted(key_id, reason="credits_exhausted")
        raise FirecrawlCreditsExhausted(key_id)
    
    if resp.status_code == 429:
        await vault.mark_cooldown(key_id, seconds=60)
        raise FirecrawlRateLimited(key_id)
    
    resp.raise_for_status()
    data = resp.json()
    
    # Track actual credits used
    credits_used = data.get("creditsUsed", 0)
    if credits_used:
        await vault.increment_usage(key_id, credits_used)
    
    # Check for HTTP errors that still cost credits
    if data.get("metadata", {}).get("statusCode", 200) >= 400:
        logger.warning(f"Firecrawl HTTP {data['metadata']['statusCode']} but credits charged: {credits_used}")
    
    return FirecrawlResponse(**data)
```

### 5. Crawl Safety Wrapper (Prevent 10k Credit Burn)
```python
async def safe_crawl(key_id: str, url: str, max_pages: int = 100, **options) -> CrawlResponse:
    """Crawl with explicit limit to prevent pre-flight 402."""
    if max_pages > 1000:
        raise ValueError("max_pages > 1000 requires explicit approval")
    
    payload = {
        "url": url,
        "limit": max_pages,
        "scrapeOptions": options.get("scrapeOptions", {}),
    }
    
    # Estimate cost before lease
    estimated = await estimate_firecrawl_cost("crawl", {"limit": max_pages, **options})
    key_id = await lease_firecrawl_key(vault, "crawl", {"limit": max_pages, **options})
    
    return await firecrawl_request(key_id, "/crawl", payload)
```

### 6. Agent Research Primitive (5 Free Runs/Day)
```python
async def firecrawl_deep_research(query: str, max_depth: int = 3) -> AgentResponse:
    """Use 5 free agent runs/day/account. 40 runs/fleet/day free."""
    key_id = await lease_firecrawl_key(vault, "agent", {"query": query})
    
    payload = {
        "query": query,
        "maxDepth": max_depth,
        "timeLimit": 120,  # seconds
    }
    
    resp = await firecrawl_request(key_id, "/agent", payload)
    
    # Poll status
    run_id = resp.data["id"]
    while True:
        status_resp = await firecrawl_request(key_id, f"/agent/status/{run_id}", {})
        if status_resp.data["status"] == "completed":
            return AgentResponse(**status_resp.data)
        elif status_resp.data["status"] == "failed":
            raise FirecrawlAgentFailed(status_resp.data["error"])
        await anyio.sleep(5)
```

### 7. MCP Fallback Config
```json
// .opencode/mcp/firecrawl-free.json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {}
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
| **M7 Local-First** | ✅ | Keys in VaultCore; Firecrawl = cloud only |
| **M8 Zero Telemetry** | ✅ | No Firecrawl telemetry in our code |
| **M14 Heritage** | N/A | No id Software patterns |
| **M23 Failure Integrity** | ✅ | 402/429 → rotation; pre-flight cost check |
| **M25 Streaming Resilience** | N/A | Firecrawl async job polling, not streaming |

---

## 🚀 Dev Strategy Revisal Recommendations

### Immediate (P0-2 — This Week)
1. **Create 8 Firecrawl accounts** (free tier, 1,000 credits each = 8,000 fleet)
2. **VaultCore schema**: `cred_type: firecrawl_api_key` with cost metadata
3. **ModelGateway tool**: `firecrawl_scrape`, `firecrawl_crawl`, `firecrawl_search`, `firecrawl_agent`

### Short-term (P1-1 — VaultCore Schema)
1. **Per-key credit tracking**: `used_today` reset at billing cycle (monthly)
2. **Cost estimation in lease**: Prevent 402 by checking `used_today + estimated <= 1000`
3. **Crawl limit enforcement**: Default `limit: 100`, max `1000` without approval

### Medium-term (P2 — Orchestration)
1. **Exa → Firecrawl pipeline**: Exa search (10 QPS, cheap) → Firecrawl scrape (10 RPM, expensive)
2. **Agent quota manager**: Track 5 free runs/day/account across fleet (40 total)
3. **Smart Upgrade monitor**: Alert if any account auto-upgrades (unexpected charge)

---

## 📦 Deliverables for Phase 3 Synthesis

| Artifact | Location | Purpose |
|----------|----------|---------|
| Firecrawl VaultCore Schema | `docs/research/R_VAULT_SCHEMA_V2.md` (extended) | 8 keys + cost metadata |
| Firecrawl Router Class | `src/omega/model_gateway/firecrawl_router.py` | Lease + cost check + rotate |
| Cost Estimation Module | `src/omega/vaultcore/firecrawl_cost.py` | Pre-flight credit estimation |
| Safe Crawl Wrapper | `src/omega/tools/firecrawl_crawl.py` | Explicit limit enforcement |
| MCP Fallback Config | `.opencode/mcp/firecrawl-free.json` | Emergency keyless access |

---

## 🔗 Cross-References

| Provider | Phase 1 Report | Key Integration Point |
|----------|----------------|----------------------|
| **Exa** | `PHASE1E_EXA_SEARCH_API_...` | Exa finds URLs → Firecrawl scrapes |
| **OpenRouter** | `PHASE1D_OPENROUTER_...` | Firecrawl as tool via OpenRouter? No — direct |
| **Google API** | `PHASE1A_GOOGLE_API_...` | Firecrawl can scrape Google results |
| **Antigravity** | `PHASE1B_ANTIGRAVITY_...` | No direct link |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1F-COMPLETE ⬡ 2026-07-23*