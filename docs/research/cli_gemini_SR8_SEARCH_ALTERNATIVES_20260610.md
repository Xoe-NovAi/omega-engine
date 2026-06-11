# 🔱 Research Report: Exa Alternatives & Firecrawl Strategy (SR-8)
# ⬡ OMEGA ⬡ CLI_GEMINI ⬡ gemini-2.0-flash ⬡ docs/research ⬡ SR-8 ⬡ PHASE-III

## 1. Exa Replacement Evaluation (SR-8)

Given the current 401 (Unauthorized) status of Exa, the council requires a resilient alternative.

### 1.1 Comparison Matrix

| Provider | Strength | Cost (Free Tier) | MCP Support | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **Tavily** | Clean, agent-optimized context | 2,500 queries/mo | ✅ Official Remote/Local | **Primary Replacement** |
| **Jina Reader**| URL-to-Markdown (RAG-perfect) | 10M tokens (one-time) | ✅ Official Remote | **Secondary (RAG Focus)** |
| **Serper** | Raw Google SERP (High volume) | 2,500 queries/mo | ✅ Community Local | **Tertiary (Budget)** |

### 1.2 Implementation Recommendation (SR-8)
*   **Action**: Enable **Tavily** as the primary neural search fallback. It mirrors Exa's "search + extract" flow but with better free-tier availability.
*   **Action**: Enable **Jina Reader** for tasks requiring high-fidelity Markdown conversion (e.g., library ingestion).

## 2. Firecrawl Self-Hosting vs Cloud

### 2.1 Analysis
*   **Cloud (Current)**: Zero maintenance but credit-gated (1,000/mo). Currently at 402 (Exhausted).
*   **Self-Hosted (OSS)**: Unlimited scraping but high maintenance (Redis, Playwright, Proxy rotation).
*   **Stealth Gap**: Self-hosted OSS lacks the "Fire-engine" bypass logic found in the cloud, meaning frequent 403s on protected sites (Amazon, Cloudflare) without a premium proxy pool.

### 2.2 Strategic Recommendation
*   **Short-Term**: Stick with Cloud and implement **Tier 0 (Local Cache)** and **Tier 1 (Built-in websearch)** more aggressively to preserve credits.
*   **Long-Term**: Prepare a `deploy/infra/firecrawl-oss.yaml` Docker stack. Use it specifically for **unprotected/internal sites** where credits are wasted.
*   **Hybrid Move**: Use Firecrawl Cloud only for "Hard Targets" (Cloudflare/JS-heavy) and native `websearch`/`webfetch` for "Soft Targets."

## 3. The ics_render Bug (Definitive Fix)

*   **Diagnosis**: The bug "Object of type coroutine is not JSON serializable" in `server.py` is caused by name shadowing.
*   **Proposed Fix**:
    ```python
    # Change import in mcp_servers/omega_hub/server.py
    from omega.ics import render as ics_render_logic
    
    # Ensure the tool calls the logic and returns the STRING result
    @mcp.tool()
    async def ics_render(...):
        # ... logic ...
        header = ics_render_logic(...) # Synchronous call
        return header # Returns the string, not a coroutine
    ```
*   **Status**: Lilith claims fixed in D127, but if errors persist, the shadowing might still exist in a different scope or within the `m9_safe` decorator's return handling.

---
*Authored by: Gemini CLI — Heavy Research Specialist*
