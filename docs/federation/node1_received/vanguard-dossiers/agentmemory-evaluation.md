# agentmemory Evaluation — REJECTED

**Date:** 2026-09-11
**Source:** rohitg00/agentmemory (Apache-2.0, ~27.9k★)

## Verdict: REJECTED for Node 1 (ASUS)

### What It Is
- TypeScript/Node.js memory engine + MCP server + auto-capture hooks
- Built on **iii-engine** (Rust, Elastic License 2.0)
- Auto-capture memory for coding agents (supports OpenCode)
- BM25 + Vector + Graph with RRF retrieval
- Consolidation + decay + auto-forget lifecycle

### Comparison vs MemPalace (Our Current)

| Dimension | AgentMemory | MemPalace (Ours) | Winner |
|-----------|-------------|------------------|--------|
| **Retrieval (LongMemEval-S)** | 95.2% R@5 | 96.6% raw / 98.4% hybrid+rerank | **MemPalace** |
| **Capture Granularity** | 22 OpenCode hooks | 3 hook events + sweep | AgentMemory |
| **Memory Lifecycle** | 4-tier + decay + auto-forget | Flat + AAAK compression | AgentMemory |
| **Retrieval Quality** | BM25+Vector+Graph RRF | Vector + FTS5 + KG + AAAK | **MemPalace** |
| **Architecture** | Node + iii-engine (Rust, ELv2) | Python + Chroma/SQLite | MemPalace (simpler) |
| **Resource Footprint** | iii-engine + Node + HNSW | sqlite_exact: 557 MB | MemPalace |
| **Ports** | 3111/3112/3113/49134 | Stdio MCP only | MemPalace |
| **Provenance** | Full (channel, capturedAt) | Full (source file, session) | Tie |
| **Multi-agent** | Leases, signals, mesh sync | Wings + diaries + logstream | AgentMemory |
| **Viewer** | Real-time (port 3113) | None built-in | AgentMemory |
| **License** | Apache-2.0 | MIT | MemPalace |

### Why We Don't Need It

1. **Core metric: MemPalace wins on retrieval** (96.6% vs 95.2% R@5)
2. **Already integrated:** 62 drawers, 8 rooms, MCP verified, mining hygiene proven
3. **AgentMemory's strengths are YAGNI:** viewer, multi-agent coordination, 4-tier lifecycle
4. **License conflict:** ELv2 (iii-engine) vs MIT (MemPalace) — cannot mix
5. **Architecture mismatch:** iii-engine = orchestration bus; MemPalace = memory palace

### If We Needed AgentMemory's Unique Features
We would **adapt** (not adopt): use AgentMemory's OpenCode hook capture as supplementary ingest pipeline into MemPalace, keep MemPalace as retrieval backbone.

### Verdict
**REJECTED** — doesn't beat MemPalace on retrieval; duplicates memory layer without retrieval gain.

**Dossier:** `docs/ROADMAP.md` P2.5 status = REJECTED
