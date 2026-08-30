# 5-Tier Sovereign Search Protocol

Search orchestration moves to `src/omega/oracle/search_orchestrator.py`. The Hub's search tools expose this protocol as thin wrappers.

## Priority Order

| Tier | Backend | Cost | Role |
|------|---------|------|------|
| T0 | Local Cache (`.firecrawl/`, `data/kb/`) | Zero | Filesystem-first hit |
| T1 | Built-in `websearch`/`webfetch` | Zero | Built-in fallback |
| T2 | SearXNG (`:8017`) | Local | Private metasearch |
| T3 | Firecrawl API | Credits | Structured web extraction |
| T4 | Exa API | Credits | Neural semantic search |

## Protocol Rules

1. **Always check T0 cache** before Tier 2+ calls
2. **Log all failures** to Hivemind using `[SEARCH-ERROR]` format for observability
3. **Never call Tier 3/4 if Tier 0/1 returns results** — credits are precious
