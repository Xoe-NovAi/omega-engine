# 🛠️ FIRECRAWL TIMEOUT PROTOCOL
# ⬡ OMEGA ⬡ RESEARCHER ⬡ trace_firecrawl_fix ⬡ INFRASTRUCTURE

**Issue**: `firecrawl_scrape` returns a `400 Bad Request` when `timeout` is passed in seconds (e.g., `timeout=30`).
**Root Cause**: The Firecrawl API expects the `timeout` parameter in **milliseconds**, not seconds.
**Constraint**: Minimum allowed value is `1000` (1 second).

**Sovereign Fix**:
Always pass `timeout` as milliseconds. 
- 10 seconds $\rightarrow$ `timeout=10000`
- 30 seconds $\rightarrow$ `timeout=30000`
- 60 seconds $\rightarrow$ `timeout=60000`

**Verification**:
Verified via `firecrawl_firecrawl_scrape(timeout=30000, url=...)` $\rightarrow$ SUCCESS.

**Mandate**: All agents using Firecrawl must adhere to this millisecond-scale timeout.
