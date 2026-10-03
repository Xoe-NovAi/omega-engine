# 5-Tier Sovereign Search Protocol (SSP-V2)

Search orchestration lives in `src/omega/oracle/sovereign_search_service.py` with intent routing driven by `src/omega/oracle/search_router.py`. The Hub exposes this protocol via `omega-hub_library_web_search` and `omega-hub_sovereign_search`.

## Priority Order

| Tier | Backend | Endpoint | Cost | Role |
|------|---------|----------|------|------|
| T0 | Local Cache | `.firecrawl/`, MemoryStore | Zero | Filesystem-first hit |
| T1 | SearXNG | `http://127.0.0.1:8017` | Zero | Sovereign private metasearch |
| T2 | Exa API | `https://api.exa.ai` | Key | Neural semantic search |
| T3 | Firecrawl API | `http://127.0.0.1:8015` | Credits | Structured web extraction |

## Development Invariants (Zero Local Model Stalls)

1. **No Local Model Invocations During Development**: Local inference (NativeGGUF, Ollama, lmster) is strictly bypassed during engine development. Do not wait on local models for search verification or NLI tasks.
2. **Verification Opt-in**: `verification.enabled: false` in `config/search.yaml`. Claims and search results return directly without blocking on `SkepticalVerifier` model generation.
3. **SearXNG Engine Isolation**: In `data/searxng/config/settings.yml`, `duckduckgo` and `google` are disabled to avoid CAPTCHA blocks. Multi-engine fallbacks (`bing`, `brave`, `startpage`, `marginalia`, `qwant`, `wikipedia`, `github`, `arxiv`) ensure reliable results.
4. **Defensive Result Parsing**: `SearXNGProvider` and `searxng-mcp` safely parse `results`, `infoboxes`, `answers`, `corrections`, and `suggestions` regardless of whether they arrive as dictionaries or string primitives.

## Protocol Rules

1. **Always check T0 cache** before Tier 1+ calls
2. **Log all failures** to Hivemind using `[SEARCH-ERROR]` format for observability
3. **Never call Tier 2/3 if Tier 0/1 returns results** — credits and latency are preserved
