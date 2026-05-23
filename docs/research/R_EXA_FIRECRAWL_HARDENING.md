# 🔱 Omega Engine — Exa & Firecrawl Integration Hardening
**AP Token**: `AP-EXA-FC-HARDEN-v1.0.0`
**Date**: 2026-05-19
**Status**: ACTIVE

## §1 Executive Summary
This document formalizes the hardening of the Omega Engine's web search and extraction layer. We identified a critical instability in the remote MCP bridge for Exa and a need for token-efficient extraction patterns for AI agents.

## §2 Exa Integration Analysis
### 2.1 The Remote MCP Failure
- **Symptom**: Calls to `exa_web_search_exa` via the remote MCP server (`mcp.exa.ai`) returned `401 Unauthorized`.
- **Root Cause**: The remote MCP server was not correctly forwarding the `x-api-key` header from the OpenCode runtime to the Exa API.
- **Verification**: Direct `curl` requests to `https://api.exa.ai/search` using the same key and header succeeded perfectly.

### 2.2 Parameter Optimization
To reduce token cost and increase relevance, the following changes were applied to `src/omega/workers/background_researcher/search_fleet.py`:
- **Search**: Changed `type: "high"` $\rightarrow$ `type: "auto"` and added `highlights: True`.
- **Fetch**: Added `highlights: True` to the `/contents` endpoint request.
- **Benefit**: Highlights provide 10x token efficiency compared to full text while preserving the most relevant excerpts.

## §3 Firecrawl Integration
- **Verification**: `firecrawl-cli` installed and authenticated.
- **Implementation**: The engine uses a direct HTTP POST to `https://api.firecrawl.dev/v1/scrape` in `search_fleet.py`, ensuring reliability by bypassing the MCP layer for core background research.

## §4 Agent Guardrails
To prevent agents from attempting unsupported methods or hitting 401s:
1. **Mandate**: Agents must use the `sovereign-search` skill.
2. **Abstraction**: The skill wraps the `search_all` logic, which handles the provider fallback chain and correct parameter injection.
3. **Forbidden**: Direct calls to `exa_web_search_exa` are now flagged as unstable in agent instructions.

## §5 Implementation Note
Implementation agent should ensure that any new search tools follow the `Sovereign Search Wrapper` pattern:
`User Query` $\rightarrow$ `Sovereign Search Skill` $\rightarrow$ `search_fleet.py` $\rightarrow$ `Direct API Call` $\rightarrow$ `Cleaned Results`.
